# -*- coding: utf-8 -*-
"""
kran.py  ·  konsept D «Kran»: parametrisk CAD-samanstilling, kontroll og eksport

  py -3 cad/kran.py           byggjer delane, kontrollerer og eksporterer alt
  py -3 cad/kran.py --rask    berre bygg og kontroll (ingen filer ut)

Grunnlag: referanse/maaling.json, kameratilpassinga av referansefotoet (referanse/kamera.py). Fotoet er teke
skrått (stativplanet dreidd om lag 27 grader mot kameraet), så alle mål er rekna tilbake gjennom kameraet.
Skala: leddaksen 330 mm over bordet (vald; fotoet har ingen målestokk).

Koordinatar: X langs armen i stativplanet frå nedre venstre hjørne av stativet, Y vinkelrett på plata (+Y bak,
-Y framover, mot den som ser fotoet), Z opp frå bordet. Alle mål i mm. Delane ligg i monteringsposisjon med armen
vassrett; printretninga blir sett når printplatene blir skrivne.
"""
from __future__ import annotations

import csv
import json
import math
import sys
import time
from itertools import combinations
from pathlib import Path

import cadquery as cq
from cadquery import Edge, Face, Solid, Vector as V, Wire
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeRevol
from OCP.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Vec

HER = Path(__file__).resolve().parent
ROT = HER.parent
RASK = '--rask' in sys.argv

# ======================================================================== parametrar
# ---- målt i fotoet gjennom kameraet (referanse/maaling.json), avrunda
FOT_L = 180.0                   # botnkanten på stativplata, frå nedre venstre til nedre høgre hjørne (målt 179,8)
LEDD_X, LEDD_Z = 154.0, 330.0   # leddaksen (målt X 154,2; Z er skalaen)
HYP_DXDZ = 133.65 / 344.73      # venstre kant (hypotenusen) gjennom origo: 21,2 grader frå loddrett
HOG_DXDZ = -15.12 / 313.08      # høgre kant gjennom (FOT_L, 0): lener 2,8 grader innover mot toppen
SPALTE_1, SPALTE_2 = (48.3, 50.3), (141.9, 313.0)   # sentera i endane av spalta
SPALTE_B = 13.8                 # breidda på spalta (målt 13,8)
ARM_TOPP, ARM_BOTN = 337.1, 316.7   # overkant og underkant av armen (målt med framsida på Y -7,25)
ARM_TUPP = 631.3                # enden av framsida på armen (målt X)
ARM_D = 43.85                   # djupna til armen (målt; det minst sikre målet, 34-60 mm over alle brennvidder)
ARM_X0 = 180.7                  # der den vassrette profilen byrjar (målt; øyret dekkjer resten inn til leddet)
LED_X0 = 274.0                  # der lyslista byrjar (målt; ho går til enden)
KNOTT_D = 15.0                  # knotten på leddet (målt 36 x 42 px = Ø 15)

# ---- valde: stativet er tre laserskorne lag S235 1,5 mm, limte saman (kanal for leidningen i midtlaget)
LAG_T = 1.5                     # kvart lag
PLATE_T = 3 * LAG_T             # heile plata, 4,5 mm
FILT_T = 1.0                    # filt under flensane
BOY_RI = 1.5                    # innvendig bøyeradius i flensane (= platetjukkleiken)
FLENS_L = 22.0                  # framflensen: 22 mm fram frå plata (den tynne stripa i fotoet)
FLENS_LB = 26.0                 # bakflensen: 26 mm bak, skjult; armen ligg mest bak plata og dreg tyngdepunktet bakover
MIDT_Z0 = FILT_T + BOY_RI + LAG_T   # midtlaget sluttar der bøyane byrjar (4,0)
KANAL_B = 3.4                   # leidningskanalen i midtlaget (fire PTFE-leidningar side om side, til saman 2,9)
KANAL_INN = 7.0                 # senterlina i kanalen ligg så langt innanfor høgre kanten (minst 5 mm stål)
KAMMER_R = 8.5                  # vridekammeret i midtlaget rundt akselen (Ø 17)
LAGER_R = 5.1                   # Ø 10,2 i fram- og baklaget: akselen går her, gjengetoppane slipte til Ø 9,9
VINDAUGE = (104.0, 124.0, 6.0, 16.0)   # i baklaget, for leidningane ut i lomma: x0, x1, z0, z1
BOGE_R, BOGE_B = 12.0, 3.4      # bogesporet for stoppinnen i framlaget
BOGE_FRA, BOGE_TIL = 81.5, 188.5    # senterlina i sporet, grader frå +X mot klokka sett framanfrå: stopp ved -30 og +75
STOPP_VINKEL = 112.5            # stoppinnen med armen vassrett
ARM_MIN, ARM_MAX = -30.0, 75.0  # rørsleområdet til armen (grader frå vassrett)

# ---- armen: bøygd C-profil i Al 5754 1,0 mm frå same laserordre; framflensen held fram som øyret rundt leddet
ARM_T = 1.0                     # platetjukkleik
ARM_DJUP = 44.0                 # målt 43,85
LEPPE = 5.0                     # innbøygde lepper i botnen som ber spreiaren
ARM_X1 = 627.5                  # enden av den bøygde profilen; endelokket går til 631,5 (målt 631,3)
DOBLAR_T = 3.0                  # forsterkingsplata bak øyret (Al 5754 3,0)
TUNGE_L = 26.0                  # tunga på forsterkingsplata inn i profilen
SPREIAR_T = 1.5                 # opal PC

# ---- leddet, sett frå stativplata og framover (-Y) og bakover (+Y)
PA6_T, PA6_R, PA6_RI = 1.0, 10.0, 5.25
D_FLAT = 9.0                    # mål over flata på akselen (M10 x 1)
AKSEL_R, AKSEL_BOR = 5.0, 3.5
MUTTER_NV, MUTTER_T = 13.0, 3.0
TALLERK_RY, TALLERK_RI, TALLERK_T, TALLERK_H = 10.0, 5.1, 0.5, 0.99   # DIN 2093 C 20 x 10,2 x 0,5, samantrykt
TALLERK_N = 4
KNOTT_R, KNOTT_H = 8.5, 6.0     # Ø 17 x 6: dekkjer mutteren (fotoet Ø 15)
HETTE_R, HETTE_H = 12.0, 12.0


def _avstand_til_linje(p, a, d):
    """Avstand frå punktet p til linja gjennom a med retning d (2D, d treng ikkje vere eining)."""
    dl = math.hypot(*d)
    return abs(d[0] * (p[1] - a[1]) - d[1] * (p[0] - a[0])) / dl


HOVUD_R = _avstand_til_linje((LEDD_X, LEDD_Z), (0.0, 0.0), (HYP_DXDZ, 1.0))   # 24,5: hovudet tangerer hypotenusen


# ======================================================================== hjelparar

def boks(x0, x1, y0, y1, z0, z1):
    return Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def sylinder_y(r, y0, y1, x, z):
    """Sylinder langs Y (vinkelrett på stativplata)."""
    return Solid.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))


def prisme_y(f, y0, y1):
    """Flate i XZ-planet (Y = 0) løfta til ein prisme frå y0 til y1."""
    s = cq.Shape.cast(BRepPrimAPI_MakePrism(f.wrapped, gp_Vec(0, y1 - y0, 0)).Shape())
    return s.translate(V(0, y0, 0))


def xz(p):
    return V(p[0], 0.0, p[1])


def polygon_xz(pts):
    return Face.makeFromWires(Wire.makePolygon([xz(p) for p in pts], close=True))


def sirkel_xz(c, r):
    return Face.makeFromWires(Wire.makeCircle(r, xz(c), V(0, 1, 0)))


def stadion_xz(a, b, r):
    """Avlang spalte med runde endar frå a til b (senter i endane), halv breidd r."""
    ax = (b[0] - a[0], b[1] - a[1])
    L = math.hypot(*ax)
    u = (ax[0] / L, ax[1] / L)
    n = (-u[1], u[0])
    pts = [(a[0] + n[0] * r, a[1] + n[1] * r), (b[0] + n[0] * r, b[1] + n[1] * r),
           (b[0] - n[0] * r, b[1] - n[1] * r), (a[0] - n[0] * r, a[1] - n[1] * r)]
    f = polygon_xz(pts)
    return f.fuse(sirkel_xz(a, r)).fuse(sirkel_xz(b, r)).clean()


def hogre_kant_x(z):
    return FOT_L + HOG_DXDZ * z


def hyp_x(z):
    return HYP_DXDZ * z


def _hovud_pkt(a):
    return (LEDD_X + HOVUD_R * math.cos(a), LEDD_Z + HOVUD_R * math.sin(a))


def _hovud_boge(a0, a1):
    """Boge på hovudsirkelen frå vinkel a0 til a1 (radianar), gjennom midtvinkelen."""
    return Edge.makeThreePointArc(xz(_hovud_pkt(a0)), xz(_hovud_pkt((a0 + a1) / 2)), xz(_hovud_pkt(a1)))


def _vinkel(p):
    return math.atan2(p[1] - LEDD_Z, p[0] - LEDD_X)


def _flate(kantar):
    return Face.makeFromWires(Wire.assembleEdges(kantar))


def stativ_hjorne():
    """Tangentpunktet på hypotenusen og punktet der hovudsirkelen skjer høgre kanten (under leddaksen)."""
    d = (HYP_DXDZ, 1.0)
    dl = math.hypot(*d)
    u = (d[0] / dl, d[1] / dl)
    t = LEDD_X * u[0] + LEDD_Z * u[1]
    tang = (t * u[0], t * u[1])
    a = HOG_DXDZ ** 2 + 1
    b = 2 * HOG_DXDZ * (FOT_L - LEDD_X) - 2 * LEDD_Z
    c = (FOT_L - LEDD_X) ** 2 + LEDD_Z ** 2 - HOVUD_R ** 2
    z = (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)
    return tang, (hogre_kant_x(z), z)


def oyre_flate(kva='oyre'):
    """Øyret sett framanfrå som éin kontur: bogen rundt leddaksen på venstre sida (same radius som stativhovudet),
    overkanten rett frå toppen av bogen ned til overkanten av armen (27 grader, som i fotoet) og underkanten som
    tangerer bogen. kva: 'oyre' sluttar ved ARM_X0, 'flagg' held fram som framflensen til ARM_X1, 'doblar' har tunga
    inn i profilen."""
    topp = (LEDD_X, LEDD_Z + HOVUD_R)
    tb = tangent_frå_punkt((ARM_X0, ARM_BOTN), (LEDD_X, LEDD_Z), HOVUD_R, +1)
    if kva == 'flagg':
        pts = [topp, (ARM_X0, ARM_TOPP), (ARM_X1, ARM_TOPP), (ARM_X1, ARM_BOTN), (ARM_X0, ARM_BOTN), tb]
    elif kva == 'doblar':
        zt, zb = ARM_TOPP - ARM_T - 0.3, ARM_BOTN + ARM_T + 0.3
        pts = [topp, (ARM_X0, ARM_TOPP), (ARM_X0, zt), (ARM_X0 + TUNGE_L, zt), (ARM_X0 + TUNGE_L, zb), (ARM_X0, zb),
               (ARM_X0, ARM_BOTN), tb]
    else:
        pts = [topp, (ARM_X0, ARM_TOPP), (ARM_X0, ARM_BOTN), tb]
    k = [Edge.makeLine(xz(a), xz(b)) for a, b in zip(pts, pts[1:])]
    a_tb = _vinkel(tb)
    k.append(_hovud_boge(a_tb, math.pi / 2 - 2 * math.pi))      # med klokka rundt venstre sida, opp til toppen
    return _flate(k)


def stativ_omriss():
    """Omrisset av stativplata i XZ-planet: trekanten frå fotoet med eit rundt hovud om leddaksen. Hovudet
    tangerer hypotenusen, så venstre kanten går mjukt over i bogen; på høgre sida stikk hovudet ut forbi den
    nesten loddrette kanten, gøymt bak øyret på armen. Spalta er skoren ut. Éin samanhengande kontur."""
    tang, pr = stativ_hjorne()
    a0, a1 = _vinkel(tang), _vinkel(pr)
    k = [Edge.makeLine(xz((0.0, 0.0)), xz(tang)), _hovud_boge(a0, a1), Edge.makeLine(xz(pr), xz((FOT_L, 0.0))),
         Edge.makeLine(xz((FOT_L, 0.0)), xz((0.0, 0.0)))]
    return _flate(k).cut(stadion_xz(SPALTE_1, SPALTE_2, SPALTE_B / 2)).clean()


def tangent_frå_punkt(p, c, r, side):
    """Tangentpunktet på sirkelen (c, r) frå punktet p; side +1 eller -1 vel kva for tangent."""
    dx, dy = c[0] - p[0], c[1] - p[1]
    d = math.hypot(dx, dy)
    a = math.atan2(dy, dx)
    b = math.asin(r / d)
    t = a + side * b
    L = math.sqrt(d * d - r * r)
    return (p[0] + L * math.cos(t), p[1] + L * math.sin(t))


def oyre_omriss(x1=None):
    tb = tangent_frå_punkt((ARM_X0, ARM_BOTN), (LEDD_X, LEDD_Z), HOVUD_R, +1)
    return oyre_flate('oyre'), (LEDD_X, LEDD_Z + HOVUD_R), tb


# ======================================================================== avleidde mål (Y)
Y_PL0, Y_PL1 = -PLATE_T / 2, PLATE_T / 2                      # stativplata -2,25 ... +2,25
Y_FRAM = (Y_PL0, Y_PL0 + LAG_T)
Y_MIDT = (-LAG_T / 2, LAG_T / 2)
Y_BAK = (Y_PL1 - LAG_T, Y_PL1)
Y_PA6F = (Y_PL0 - PA6_T, Y_PL0)                                # framfor plata
Y_DOBLAR = (Y_PA6F[0] - DOBLAR_T, Y_PA6F[0])
Y_ARMF = (Y_DOBLAR[0] - ARM_T, Y_DOBLAR[0])                    # framflensen og øyret, framflata på -7,25
Y_MUTF = (Y_ARMF[0] - MUTTER_T, Y_ARMF[0])
Y_KNOTT = (Y_ARMF[0] - 0.5 - KNOTT_H, Y_ARMF[0] - 0.5)
Y_PA6B = (Y_PL1, Y_PL1 + PA6_T)                                # bak plata
Y_LAAS = (Y_PA6B[1], Y_PA6B[1] + 1.0)
Y_TALL = (Y_LAAS[1], Y_LAAS[1] + TALLERK_N * TALLERK_H)
Y_MUTB = (Y_TALL[1], Y_TALL[1] + MUTTER_T)
Y_HETTE = (Y_LAAS[0] + 0.5, Y_LAAS[0] + 0.5 + HETTE_H)
Y_AKSEL = (Y_MUTF[0] - 0.75, Y_MUTB[1] + 0.75)
ARM_Y0, ARM_Y1 = Y_ARMF[0], Y_ARMF[0] + ARM_DJUP              # armen -7,25 ... 36,75
BOY_ZC = FILT_T + LAG_T + BOY_RI                               # senteret i bøyane (4,0)
FLENS_X0, FLENS_X1 = HYP_DXDZ * BOY_ZC, FOT_L + HOG_DXDZ * BOY_ZC


# ======================================================================== stativet

def over_z(f, z0):
    """Den delen av flata som ligg over z0."""
    return f.intersect(polygon_xz([(-50.0, z0), (500.0, z0), (500.0, 600.0), (-50.0, 600.0)])).clean()


def boge_spor(c, r, b, a0, a1):
    """Bogeforma spor (sentrum c, midtradius r, breidd b) frå vinkel a0 til a1 i grader, runde endar."""
    ri, ry = r - b / 2, r + b / 2
    p = lambda rr, a: xz((c[0] + rr * math.cos(math.radians(a)), c[1] + rr * math.sin(math.radians(a))))
    am = (a0 + a1) / 2
    e = [Edge.makeThreePointArc(p(ry, a0), p(ry, am), p(ry, a1)),
         Edge.makeThreePointArc(p(ry, a1), p(r + b / 2 * 0.0, a1) + V(0, 0, 0) if False else
                                xz((c[0] + r * math.cos(math.radians(a1)) + b / 2 * math.cos(math.radians(a1 + 90)),
                                    c[1] + r * math.sin(math.radians(a1)) + b / 2 * math.sin(math.radians(a1 + 90)))),
                                p(ri, a1)),
         Edge.makeThreePointArc(p(ri, a1), p(ri, am), p(ri, a0)),
         Edge.makeThreePointArc(p(ri, a0),
                                xz((c[0] + r * math.cos(math.radians(a0)) + b / 2 * math.cos(math.radians(a0 - 90)),
                                    c[1] + r * math.sin(math.radians(a0)) + b / 2 * math.sin(math.radians(a0 - 90)))),
                                p(ry, a0))]
    return Face.makeFromWires(Wire.assembleEdges(e))


def kanal_xz():
    """Leidningskanalen i midtlaget: frå vindauget vassrett bort til høgre kanten, opp 7 mm innanfor kanten og inn i
    vridekammeret rundt akselen."""
    zv = (VINDAUGE[2] + VINDAUGE[3]) / 2
    p0 = ((VINDAUGE[0] + VINDAUGE[1]) / 2, zv)
    p1 = (hogre_kant_x(zv) - KANAL_INN, zv)
    z2 = LEDD_Z - 12.0
    p2 = (hogre_kant_x(z2) - KANAL_INN, z2)
    f = stadion_xz(p0, p1, KANAL_B / 2).fuse(stadion_xz(p1, p2, KANAL_B / 2)).fuse(
        stadion_xz(p2, (LEDD_X, LEDD_Z), KANAL_B / 2)).fuse(sirkel_xz((LEDD_X, LEDD_Z), KAMMER_R))
    return f.clean(), (p0, p1, p2)


def bøy_og_flens(retning):
    """Bøyen (Ri 1,5) og flensen nedst på eit ytre lag. retning -1 = fram (-Y), +1 = bak (+Y)."""
    yp = Y_PL0 if retning < 0 else Y_PL1
    yc = yp + retning * BOY_RI
    ri, ry = BOY_RI, BOY_RI + LAG_T
    # kvartring i YZ-planet ved X = FLENS_X0
    a_v = 0.0 if retning < 0 else 180.0                          # vinkelen der den loddrette delen byrjar
    a_f = -90.0
    pt = lambda r, a: V(FLENS_X0, yc + r * math.cos(math.radians(a)), BOY_ZC + r * math.sin(math.radians(a)))
    am = (a_v + (a_f if retning < 0 else 270.0)) / 2
    a_f2 = a_f if retning < 0 else 270.0
    e = [Edge.makeThreePointArc(pt(ry, a_v), pt(ry, am), pt(ry, a_f2)), Edge.makeLine(pt(ry, a_f2), pt(ri, a_f2)),
         Edge.makeThreePointArc(pt(ri, a_f2), pt(ri, am), pt(ri, a_v)), Edge.makeLine(pt(ri, a_v), pt(ry, a_v))]
    ring = Face.makeFromWires(Wire.assembleEdges(e))
    boy = cq.Shape.cast(BRepPrimAPI_MakePrism(ring.wrapped, gp_Vec(FLENS_X1 - FLENS_X0, 0, 0)).Shape())
    y_ende = yp + retning * (FLENS_L if retning < 0 else FLENS_LB)
    y0, y1 = sorted((yc, y_ende))
    flens = boks(FLENS_X0, FLENS_X1, y0, y1, FILT_T, FILT_T + LAG_T)
    kantar = [e for e in flens.Edges() if abs(e.BoundingBox().ymin - y_ende) < 1e-3 and abs(e.BoundingBox().ymax - y_ende) < 1e-3
              and e.BoundingBox().zlen > 1.0]
    flens = flens.fillet(6.0, kantar)
    return boy.fuse(flens)


def stativ_lag(kva):
    """Eitt av dei tre laga i stativet: 'fram' (D01), 'midt' (D02) eller 'bak' (D03)."""
    f = over_z(stativ_omriss(), BOY_ZC)
    c = (LEDD_X, LEDD_Z)
    if kva == 'fram':
        f = f.cut(sirkel_xz(c, LAGER_R)).cut(boge_spor(c, BOGE_R, BOGE_B, BOGE_FRA, BOGE_TIL)).clean()
        s = prisme_y(f, *Y_FRAM).fuse(bøy_og_flens(-1))
    elif kva == 'midt':
        s = prisme_y(f.cut(kanal_xz()[0]).clean(), *Y_MIDT)
    else:
        v = VINDAUGE
        f = f.cut(sirkel_xz(c, LAGER_R)).cut(polygon_xz([(v[0], v[2]), (v[1], v[2]), (v[1], v[3]), (v[0], v[3])])).clean()
        s = prisme_y(f, *Y_BAK).fuse(bøy_og_flens(+1))
    return s.clean()


# ======================================================================== armen og leddet

def sylinder_y_hol(r, ri, y0, y1, x=None, z=None):
    x = LEDD_X if x is None else x
    z = LEDD_Z if z is None else z
    s = sylinder_y(r, y0, y1, x, z)
    return s.cut(sylinder_y(ri, y0 - 1, y1 + 1, x, z)) if ri else s


def d_hol_xz(r=LAGER_R, flat=D_FLAT - AKSEL_R + 0.1):
    """D-hol om leddaksen: sirkel med ei flat side øvst (akselen er fila flat på oversida)."""
    c = (LEDD_X, LEDD_Z)
    return sirkel_xz(c, r).intersect(polygon_xz([(c[0] - 20, c[1] - 20), (c[0] + 20, c[1] - 20),
                                                  (c[0] + 20, c[1] + flat), (c[0] - 20, c[1] + flat)])).clean()


def sekskant_y(nv, y0, y1, x=None, z=None):
    x = LEDD_X if x is None else x
    z = LEDD_Z if z is None else z
    r = nv / math.sqrt(3)
    pts = [(x + r * math.cos(math.radians(30 + 60 * i)), z + r * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
    return prisme_y(polygon_xz(pts), y0, y1)


def stopp_pkt(vinkel=0.0):
    a = math.radians(STOPP_VINKEL + vinkel)
    return LEDD_X + BOGE_R * math.cos(a), LEDD_Z + BOGE_R * math.sin(a)


def spor_xz_y(x, z, lengd, hogd, y0, y1):
    """Avlang opning (stadion) langs Y gjennom ein vegg."""
    r = hogd / 2
    return prisme_y(stadion_xz((x - lengd / 2 + r, z), (x + lengd / 2 - r, z), r), y0, y1)


def arm_plate():
    """D04: armen og øyret i éi bøygd plate (Al 5754 1,0). Framflensen held fram forbi profilen som øyret rundt
    leddet, så framsida av armen og øyret er éi flate, slik fotoet syner. Profilen er ein C med lepper nedst."""
    s = prisme_y(oyre_flate('flagg').cut(d_hol_xz()).clean(), ARM_Y0, ARM_Y0 + ARM_T)
    s = s.fuse(boks(ARM_X0, ARM_X1, ARM_Y0, ARM_Y1, ARM_TOPP - ARM_T, ARM_TOPP))              # ryggen øvst
    s = s.fuse(boks(ARM_X0, ARM_X1, ARM_Y1 - ARM_T, ARM_Y1, ARM_BOTN, ARM_TOPP))              # bakflensen
    s = s.fuse(boks(ARM_X0, ARM_X1, ARM_Y0, ARM_Y0 + LEPPE, ARM_BOTN, ARM_BOTN + ARM_T))      # leppene
    s = s.fuse(boks(ARM_X0, ARM_X1, ARM_Y1 - LEPPE, ARM_Y1, ARM_BOTN, ARM_BOTN + ARM_T))
    return s.clean()


def doblar():
    """D05: forsterkingsplate bak øyret (Al 5754 3,0), limt til øyret. D-hol, hol for stoppinnen og spor for
    LED-leidningane frå akselen ut gjennom enden av tunga. Tunga går inn i profilen og gjev limflate."""
    return prisme_y(doblar_flate(), *Y_DOBLAR).clean()


def aksel():
    """M01: holt gjengerøyr M10 x 1 (lampedel), kappa til 23 mm, fila flat på oversida til 9,0 og med to tverrspor
    for leidningane: eitt i midtlaget (vridekammeret) og eitt ved forsterkingsplata."""
    s = sylinder_y_hol(AKSEL_R, AKSEL_BOR, *Y_AKSEL)
    s = s.cut(boks(LEDD_X - 10, LEDD_X + 10, Y_AKSEL[0] - 1, Y_AKSEL[1] + 1, LEDD_Z + D_FLAT - AKSEL_R, LEDD_Z + 10))
    # det midtre sporet peikar 60 grader ned mot kanalen inn i kammeret, det fremre 10 grader ned langs sporet i
    # forsterkingsplata (rotasjon om +Y: positiv vinkel dreier +X nedover)
    for yc, vri in ((0.0, 60.0), (sum(Y_DOBLAR) / 2, 10.0)):
        spor = boks(LEDD_X, LEDD_X + 6, yc - 1.0, yc + 1.0, LEDD_Z - 1.0, LEDD_Z + 1.0)
        s = s.cut(spor.rotate(V(LEDD_X, 0, LEDD_Z), V(LEDD_X, 1, LEDD_Z), vri))
    return s.clean()


def mutter(y0, y1):
    return sekskant_y(MUTTER_NV, y0, y1).cut(sylinder_y(AKSEL_R + 0.02, y0 - 1, y1 + 1, LEDD_X, LEDD_Z))


def knott():
    """D07: knotten på leddet, printa i PETG og limt på frammutteren. Han er berøringsflata: koparfolie Ø 11 limt på
    innsida av frontveggen (1,0 mm), inne i holrommet Ø 12. Dreier med armen."""
    y0, y1 = Y_KNOTT
    s = sylinder_y(KNOTT_R, y0, y1, LEDD_X, LEDD_Z)
    kant = [e for e in s.Edges() if abs(e.BoundingBox().ymin - y0) < 1e-4 and abs(e.BoundingBox().ymax - y0) < 1e-4]
    s = s.fillet(0.6, kant)
    s = s.cut(sekskant_y(MUTTER_NV + 0.2, y1 - 2.6, y1 + 1))
    s = s.cut(sylinder_y(6.0, y0 + 1.0, y1 - 2.6 + 0.01, LEDD_X, LEDD_Z))
    return s.clean()


def hette():
    """D08: hetta bak leddet, printa i PETG og limt på bakmutteren. Dekkjer fjørpakka og dreier med armen."""
    y0, y1 = Y_HETTE[0], Y_HETTE[0] + 10.0
    s = sylinder_y(HETTE_R, y0, y1, LEDD_X, LEDD_Z)
    kant = [e for e in s.Edges() if abs(e.BoundingBox().ymin - y1) < 1e-4 and abs(e.BoundingBox().ymax - y1) < 1e-4]
    s = s.fillet(1.5, kant)
    s = s.cut(sylinder_y(TALLERK_RY + 0.5, y0 - 1, Y_MUTB[0], LEDD_X, LEDD_Z))
    s = s.cut(sekskant_y(MUTTER_NV + 0.2, Y_MUTB[0] - 0.01, Y_MUTB[1] + 0.1))
    s = s.cut(sylinder_y(AKSEL_R + 0.3, Y_MUTB[1], Y_AKSEL[1] + 0.4, LEDD_X, LEDD_Z))
    return s.clean()


def lomme_y():
    """Grensene til lomma bak foten: x0, x1, y0, y1, z0, z1."""
    return 94.0, 154.0, Y_PL1, Y_PL1 + 20.0, FILT_T + LAG_T, FILT_T + LAG_T + 24.0


LOMME_W = 1.6


def lomme():
    """D11: lomma bak stativet for USB-C, kontrollar og MOSFET (PETG), limt på bakflensen og baksida av plata,
    innanfor omrisset sett framanfrå. Open oppe (lok D14), opning mot vindauget i baklaget og for USB-C bakover.
    Fas langs botnkanten mot plata, så ho går klar av bøyen."""
    x0, x1, y0, y1, z0, z1 = lomme_y()
    w = LOMME_W
    s = boks(x0, x1, y0, y1, z0, z1).cut(boks(x0 + w, x1 - w, y0 + w, y1 - w, z0 + w, z1 + 1))
    v = VINDAUGE
    s = s.cut(boks(v[0], v[1], y0 - 1, y0 + w + 1, v[2], v[3]))                       # mot vindauget
    s = s.cut(spor_xz_y(134.0, 11.0, 9.4, 3.8, y1 - w - 1, y1 + 1))                    # USB-C bakover
    a = 3.2
    kile = boks(x0 - 1, x1 + 1, -a / 2, a / 2, -a / 2, a / 2).rotate(V(0, 0, 0), V(1, 0, 0), 45).translate(V(0, y0, z0))
    return s.cut(kile).clean()


def lomme_lok():
    """D14: lok på lomma (PETG), med kant ned i opninga. Klikkar på."""
    x0, x1, y0, y1, z0, z1 = lomme_y()
    w, k = LOMME_W, 0.15
    s = boks(x0, x1, y0, y1, z1, z1 + 1.6)
    return s.fuse(boks(x0 + w + k, x1 - w - k, y0 + w + k, y1 - w - k, z1 - 2.5, z1).cut(
        boks(x0 + 2 * w + k, x1 - 2 * w - k, y0 + 2 * w + k, y1 - 2 * w - k, z1 - 3, z1 + 0.01))).clean()


def spreiar():
    """D12: opal PC 1,5 mm, ligg på leppene i botnen av armen. Lyset byrjar der det byrjar i fotoet."""
    return boks(LED_X0, ARM_X1 - 4.0, ARM_Y0 + ARM_T + 0.25, ARM_Y1 - ARM_T - 0.25,
                ARM_BOTN + ARM_T, ARM_BOTN + ARM_T + SPREIAR_T)


def endelokk():
    """D09: endelokket på tuppen (PETG), med avrunda kant som i fotoet og ein plugg inn i profilen som held enden av
    spreiaren. Limt."""
    yi0, yi1 = ARM_Y0 + ARM_T + 0.15, ARM_Y1 - ARM_T - 0.15
    s = boks(ARM_X1, ARM_X1 + 4.0, ARM_Y0, ARM_Y1, ARM_BOTN, ARM_TOPP)
    kant = [e for e in s.Edges() if abs(e.BoundingBox().xmin - (ARM_X1 + 4.0)) < 1e-4
            and abs(e.BoundingBox().xmax - (ARM_X1 + 4.0)) < 1e-4]
    s = s.fillet(2.5, kant)
    s = s.fuse(boks(ARM_X1 - 8.0, ARM_X1, yi0, yi1, ARM_BOTN + ARM_T + SPREIAR_T + 0.1, ARM_TOPP - ARM_T - 0.15))
    s = s.fuse(boks(ARM_X1 - 4.0, ARM_X1, yi0, yi1, ARM_BOTN + ARM_T + 0.05, ARM_TOPP - ARM_T - 0.15))
    s = s.fuse(boks(ARM_X1 - 4.0, ARM_X1, ARM_Y0 + LEPPE + 0.15, ARM_Y1 - LEPPE - 0.15, ARM_BOTN + 0.1,
                    ARM_BOTN + ARM_T + 0.05))
    return s.clean()


def endeplugg():
    """D10: pluggen inne i armen frå øyret til der lyset byrjar (PETG). Ein U-profil: botnen fyller opninga mellom
    leppene, så armen er lukka under fram til lyset, og endeveggen ved øyret lukkar enden av profilen sett bakfrå.
    Open oppe og mot lyset. Framveggen står bak forsterkingsplata og tunga hennar; spalta mellom framflensen og
    framveggen (3,4 mm) er kanalen for dei to LED-leidningane frå akselen til lyslista. Printa på endeveggen utan
    støtte. Lakka som armen. Limt."""
    yf, yi1 = Y_DOBLAR[1] + 0.4, ARM_Y1 - ARM_T - 0.15
    zi0, zi1 = ARM_BOTN + ARM_T + 0.05, ARM_TOPP - ARM_T - 0.15
    x0, x1 = ARM_X0 + 0.0, LED_X0 - 0.2
    s = boks(x0, x1, yf, yi1, zi0, zi1).fuse(
        boks(x0, x1, ARM_Y0 + LEPPE + 0.15, ARM_Y1 - LEPPE - 0.15, ARM_BOTN + 0.1, zi0 + 0.01))
    w = 1.2
    s = s.cut(boks(x0 + w, x1 + 1, yf + w, yi1 - w, ARM_BOTN + 0.1 + w, zi1 + 1))      # open oppe og mot lyset
    return s.clean()


def led():
    """E01: COB-stripe 5 V, 8 mm, 2700 K, CRI >= 90, limt under ryggen inne i armen."""
    yc = (ARM_Y0 + ARM_Y1) / 2
    z1 = ARM_TOPP - ARM_T - 0.25
    return boks(LED_X0 + 2.0, ARM_X1 - 9.0, yc - 4.0, yc + 4.0, z1 - 1.6, z1)


def kjopte_lomme():
    """Kontrollar, MOSFET og USB-C-kort inne i lomma (nominelle mål)."""
    x0, x1, y0, y1, z0, z1 = lomme_y()
    usb = boks(127.5, 140.5, y1 - 1.6 - 5.2, y1 - 1.6 - 0.1, z0 + 1.7, z0 + 16.7)
    xiao = boks(97.0, 118.0, y1 - LOMME_W - 0.5 - 3.5, y1 - LOMME_W - 0.5, z0 + 1.7, z0 + 1.7 + 17.5)   # på høgkant mot bakveggen
    mos = boks(120.0, 126.0, y0 + 2.2, y0 + 12.2, z0 + 1.7, z0 + 1.7 + 10.0)
    return {'E02': xiao, 'E03': mos, 'E04': usb}


def filt():
    ut = {}
    for i, retn in enumerate((-1, 1)):
        y_a, y_b = sorted((retn * (PLATE_T / 2 + BOY_RI + LAG_T + 0.5), retn * (PLATE_T / 2 + (FLENS_L if retn < 0 else FLENS_LB) - 1.0)))
        ut[f'D13-{i + 1}'] = boks(FLENS_X0 + 1.0, FLENS_X1 - 1.0, y_a, y_b, 0.0, FILT_T)
    return ut


def leddbeslag():
    """Aksel, mutrar, PA6-skiver, låseskive, tallerkenfjører og stoppinne."""
    ut = {'M01': aksel(), 'M02-1': mutter(*Y_MUTF), 'M02-2': mutter(*Y_MUTB),
          'M03-1': sylinder_y_hol(PA6_R, PA6_RI, *Y_PA6F), 'M03-2': sylinder_y_hol(PA6_R, PA6_RI, *Y_PA6B)}
    ut['D06'] = prisme_y(sirkel_xz((LEDD_X, LEDD_Z), 10.0).cut(d_hol_xz()).clean(), *Y_LAAS)
    for i in range(TALLERK_N):
        y0 = Y_TALL[0] + i * TALLERK_H
        ut[f'M04-{i + 1}'] = sylinder_y_hol(TALLERK_RY, TALLERK_RI, y0, y0 + TALLERK_H)
    px, pz = stopp_pkt()
    ut['M05'] = sylinder_y(1.5, Y_DOBLAR[0], Y_DOBLAR[0] + 5.0, px, pz)
    return ut


# ======================================================================== delliste

LAKK = (0.73, 0.71, 0.53)               # silkematt salviegrøn som i fotoet (startpunkt RAL 6021, prøv mot fotoet)
METALL = (0.62, 0.62, 0.64)
KVIT = (0.93, 0.92, 0.88)
OPAL = (0.98, 0.97, 0.93)
SVART = (0.10, 0.10, 0.11)
KORT = (0.08, 0.33, 0.16)
FILT = (0.22, 0.22, 0.23)


def _beslag(pid):
    return leddbeslag()[pid]


DELAR = [
    # id, namn, materiale, tettleik g/cm³, fyllgrad, farge, byggjar, roterer med armen, kjelde
    ('D01', 'Framlag', 'S235 1,5 mm, laserskoren, éin bøy 90° fram (Ri 1,5), lakka', 7.85, 1.0, LAKK,
     lambda: stativ_lag('fram'), False, 'laser og bøy'),
    ('D02', 'Midtlag', 'S235 1,5 mm, laserskoren, leidningskanal og vridekammer', 7.85, 1.0, LAKK,
     lambda: stativ_lag('midt'), False, 'laser'),
    ('D03', 'Baklag', 'S235 1,5 mm, laserskoren, éin bøy 90° bak (Ri 1,5), vindauge, lakka', 7.85, 1.0, LAKK,
     lambda: stativ_lag('bak'), False, 'laser og bøy'),
    ('D04', 'Arm med øyre', 'Al 5754-H22 1,0 mm, laserskoren, fire bøyar 90° (Ri 1,0), lakka', 2.70, 1.0, LAKK,
     arm_plate, True, 'laser og bøy'),
    ('D05', 'Forsterkingsplate', 'Al 5754 3,0 mm, laserskoren, limt bak øyret med epoksy', 2.70, 1.0, METALL,
     doblar, True, 'laser'),
    ('D06', 'Låseskive', 'Rustfritt 1,0 mm, laserskoren, D-hol', 7.90, 1.0, METALL, lambda: _beslag('D06'), True, 'laser'),
    ('D07', 'Knott', 'PETG, print, berøringsflate (koparfolie Ø 11 inni), lakka', 1.27, 0.85, LAKK, knott, True, 'print'),
    ('D08', 'Hette', 'PETG, print, limt på bakmutteren, lakka', 1.27, 0.7, LAKK, hette, True, 'print'),
    ('D09', 'Endelokk', 'PETG, print, limt i tuppen, lakka', 1.27, 0.6, LAKK, endelokk, True, 'print'),
    ('D10', 'Endeplugg', 'PETG, print, skyvd inn i armen frå rota og limt, lakka', 1.27, 1.0, LAKK, endeplugg, True, 'print'),
    ('D11', 'Lomme', 'PETG, print, limt på bakflensen', 1.27, 1.0, SVART, lomme, False, 'print'),
    ('D12', 'Spreiar', 'Opal PC 1,5 mm, skoren etter DXF-mal', 1.20, 1.0, OPAL, spreiar, True, 'skjer'),
    ('D14', 'Lok på lomma', 'PETG, print, klikkar på', 1.27, 1.0, SVART, lomme_lok, False, 'print'),
]
KJOPT = [
    # id, namn, spesifikasjon, masse g, farge, byggjar, roterer med armen
    ('E01', 'COB-stripe', '5 V, 8 mm, 2700 K, CRI >= 90, om lag 8 W/m, sjølvklebande; kappa til 340 mm på kappemerket',
     6.0, (0.95, 0.85, 0.55), led, True),
    ('E02', 'Kontrollar', 'Seeed XIAO SAMD21 (QTouch), forsynt på 5 V-pinnen', 3.0, SVART,
     lambda: kjopte_lomme()['E02'], False),
    ('E03', 'MOSFET-kort', 'AO3400A (logisk nivå) på SOT-23-adapter, 100 Ω i gate, 100 kΩ frå gate til GND', 1.0, KORT,
     lambda: kjopte_lomme()['E03'], False),
    ('E04', 'USB-C-kort', '6-pinnars utbrytar med CC1 og CC2 ute, 5,1 kΩ frå kvar CC til GND', 2.0, SVART,
     lambda: kjopte_lomme()['E04'], False),
]
BESLAG = [
    # id, namn, spesifikasjon, tettleik, farge, roterer
    ('M01', 'Aksel', 'Holt gjengerøyr M10 x 1 i messing (lampedel), kappa til 23 mm, fila flat til 9,0, to tverrspor', 8.5, METALL, True),
    ('M02-1', 'Mutter', 'Tynn lampemutter M10 x 1, 3 mm, NV 13, framme', 7.85, METALL, True),
    ('M02-2', 'Mutter', 'Tynn lampemutter M10 x 1, 3 mm, NV 13, bak', 7.85, METALL, True),
    ('M03-1', 'PA6-skive', 'Nylonskive 10,5 x 20 x 1, framfor plata', 1.14, KVIT, False),
    ('M03-2', 'PA6-skive', 'Nylonskive 10,5 x 20 x 1, bak plata', 1.14, KVIT, False),
    ('M04-1', 'Tallerkenfjør', 'DIN 2093 C 20 x 10,2 x 0,5, fire i serie ()()', 7.85, METALL, True),
    ('M04-2', 'Tallerkenfjør', 'DIN 2093 C 20 x 10,2 x 0,5', 7.85, METALL, True),
    ('M04-3', 'Tallerkenfjør', 'DIN 2093 C 20 x 10,2 x 0,5', 7.85, METALL, True),
    ('M04-4', 'Tallerkenfjør', 'DIN 2093 C 20 x 10,2 x 0,5', 7.85, METALL, True),
    ('M05', 'Stoppinne', 'ISO 2338 Ø 3 m6 x 5, pressa i forsterkingsplata', 7.85, METALL, True),
]


def bygg():
    t0 = time.time()
    delar = {}
    for pid, namn, mat, rho, fyll, farge, fn, arm, kjelde in DELAR:
        f = fn()
        delar[pid] = dict(id=pid, namn=namn, materiale=mat, rho=rho, fyll=fyll, farge=farge, form=f, kjopt=False,
                          arm=arm, kjelde=kjelde, masse=f.Volume() * rho * 1e-3 * fyll)
        print(f'  {pid} {namn:<18} {time.time() - t0:6.1f} s', flush=True)
    for pid, namn, spes, m, farge, fn, arm in KJOPT:
        delar[pid] = dict(id=pid, namn=namn, materiale=spes, farge=farge, form=fn(), kjopt=True, arm=arm, kjelde='kjøp',
                          masse=m)
    bs = leddbeslag()
    for pid, namn, spes, rho, farge, arm in BESLAG:
        f = bs[pid]
        delar[pid] = dict(id=pid, namn=namn, materiale=spes, farge=farge, form=f, kjopt=True, arm=arm, kjelde='kjøp',
                          masse=f.Volume() * rho * 1e-3)
    for pid, f in filt().items():
        delar[pid] = dict(id=pid, namn='Filt', materiale='Sjølvklebande møbelfilt 1 mm, skoren etter mal', farge=FILT,
                          form=f, kjopt=True, arm=False, kjelde='kjøp', masse=f.Volume() * 0.3e-3)
    return delar


def vri(form, vinkel):
    """Vri ei form om leddaksen; positiv vinkel løftar armen (mot klokka sett framanfrå)."""
    return form.rotate(V(LEDD_X, 0, LEDD_Z), V(LEDD_X, 1, LEDD_Z), -vinkel) if vinkel else form


def former(delar, vinkel=0.0):
    return {pid: (vri(d['form'], vinkel) if d['arm'] else d['form']) for pid, d in delar.items()}


# ======================================================================== kontroll

def _boks_overlapp(a, b, m=0.0):
    return not (a.xmax < b.xmin - m or b.xmax < a.xmin - m or a.ymax < b.ymin - m or b.ymax < a.ymin - m
                or a.zmax < b.zmin - m or b.zmax < a.zmin - m)


def tallerkenfjor_kraft(s, t=TALLERK_T, h0=0.65, D=2 * TALLERK_RY, d=10.2, E=206000.0, nu=0.3):
    """Almen-László: kraft (N) i éi tallerkenfjør ved samantrykk s (mm)."""
    dl = D / d
    K1 = (1 / math.pi) * ((dl - 1) / dl) ** 2 / ((dl + 1) / (dl - 1) - 2 / math.log(dl))
    return 4 * E / (1 - nu ** 2) * t ** 4 / (K1 * D ** 2) * (s / t) * ((h0 / t - s / t) * (h0 / t - s / (2 * t)) + 1)


def tyngdepunkt(delar, vinkel):
    M, c = 0.0, V(0, 0, 0)
    for pid, d in delar.items():
        f = vri(d['form'], vinkel) if d['arm'] else d['form']
        c = c + f.Center() * d['masse']
        M += d['masse']
    return M, c * (1.0 / M)


def kontroll(delar):
    ut = {'dato': time.strftime('%Y-%m-%d %H:%M'), 'delar': {}, 'kollisjonar': [], 'rorsle': {}, 'velting': {}}
    for pid, d in delar.items():
        s = d['form']
        bb = s.BoundingBox()
        ut['delar'][pid] = dict(namn=d['namn'], gyldig=bool(s.isValid()), volum_mm3=round(s.Volume(), 1),
                                masse_g=round(d['masse'], 1), roterer=d['arm'],
                                boks_mm=[round(v, 2) for v in (bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)])
    ids = list(delar)
    for a, b in combinations(ids, 2):
        fa, fb = delar[a]['form'], delar[b]['form']
        if not _boks_overlapp(fa.BoundingBox(), fb.BoundingBox()):
            continue
        v = fa.intersect(fb).Volume()
        if v > 0.01:
            ut['kollisjonar'].append(dict(a=a, b=b, volum_mm3=round(v, 3)))
    # armen gjennom heile rørsleområdet, steg på 1 grad, og 6 grader forbi kvar ende for å sjå at stoppen tek
    arm = [p for p, d in delar.items() if d['arm']]
    fast = [p for p, d in delar.items() if not d['arm']]
    verste, verste_v, treff = 0.0, None, {}
    for v in range(int(ARM_MIN) - 6, int(ARM_MAX) + 7):
        for a in arm:
            fa = vri(delar[a]['form'], v)
            ba = fa.BoundingBox()
            for b in fast:
                if not _boks_overlapp(ba, delar[b]['form'].BoundingBox()):
                    continue
                o = fa.intersect(delar[b]['form']).Volume()
                if o > 0.01:
                    treff.setdefault(v, []).append(f'{a}/{b}')
                    if ARM_MIN <= v <= ARM_MAX and o > verste:
                        verste, verste_v = o, v
    inne = {v: t for v, t in treff.items() if ARM_MIN <= v <= ARM_MAX}
    ned = max([v for v in treff if v < ARM_MIN] or [None], key=lambda x: -999 if x is None else x)
    opp = min([v for v in treff if v > ARM_MAX] or [None], key=lambda x: 999 if x is None else x)
    ut['rorsle'] = dict(omraade_grad=[ARM_MIN, ARM_MAX], steg_grad=1.0, storste_overlapp_mm3=round(verste, 3),
                        ved_vinkel=verste_v, treff_innanfor=inne,
                        forste_treff_under=dict(vinkel=ned, delar=treff.get(ned)) if ned is not None else None,
                        forste_treff_over=dict(vinkel=opp, delar=treff.get(opp)) if opp is not None else None,
                        metode='diskret, armen vridd om leddaksen')
    # velting: støttekanten er filten under flensane
    sx0, sx1 = FLENS_X0 + 1.0, FLENS_X1 - 1.0
    syf, syb = PLATE_T / 2 + FLENS_L - 1.0, PLATE_T / 2 + FLENS_LB - 1.0
    for v in (ARM_MIN, 0.0, ARM_MAX):
        M, c = tyngdepunkt(delar, v)
        vin = dict(mot_armen=math.degrees(math.atan2(sx1 - c.x, c.z)), frå_armen=math.degrees(math.atan2(c.x - sx0, c.z)),
                   framover=math.degrees(math.atan2(c.y + syf, c.z)), bakover=math.degrees(math.atan2(syb - c.y, c.z)))
        ut['velting'][f'arm_{v:+.0f}'] = dict(masse_g=round(M, 1), tyngdepunkt_mm=[round(c.x, 1), round(c.y, 1), round(c.z, 1)],
                                              vinkel_grad={k: round(x, 1) for k, x in vin.items()})
    ut['velting']['minste_grad'] = round(min(min(x['vinkel_grad'].values()) for x in ut['velting'].values()), 1)
    ut['velting']['krav_EN60598_grad'] = 6.0
    ut['velting']['stottekant_mm'] = dict(x=[round(sx0, 2), round(sx1, 2)], y=[-syf, syb])
    # leddet: moment frå armen, friksjon, fjørkraft og handkrafter
    g = 9.81
    m_arm = sum(delar[p]['masse'] for p in arm)
    mx = sum(delar[p]['masse'] * (delar[p]['form'].Center().x - LEDD_X) for p in arm)
    M_g = m_arm * 1e-3 * g * mx / m_arm * 1e-3
    tupp = ARM_X1 + 4.0 - LEDD_X
    T_f = M_g + 0.28                                          # midt mellom vektprøva: held 40 g, glid med 80 g i tuppen
    r_eff = 2 / 3 * (PA6_R ** 3 - PA6_RI ** 3) / (PA6_R ** 2 - PA6_RI ** 2)
    mu = 0.25
    F = T_f / (2 * mu * r_eff * 1e-3)
    s = 0.0
    while tallerkenfjor_kraft(s) < F and s < 0.65:
        s += 0.001
    Mtot, c0 = tyngdepunkt(delar, 0.0)
    F_tipp = Mtot * 1e-3 * g * (sx1 - c0.x) / (ARM_X1 + 4.0 - sx1)
    ut['ledd'] = dict(arm_masse_g=round(m_arm, 1), arm_tyngdepunkt_frå_aksen_mm=round(mx / m_arm, 1),
                      moment_frå_armen_Nm=round(M_g, 3), friksjonsmoment_mål_Nm=round(T_f, 3),
                      vektprove_g=[40, 80], mu_PA6_stål=mu, r_eff_mm=round(r_eff, 2), fjorkraft_N=round(F, 1),
                      samantrykk_per_fjor_mm=round(s, 3), samantrykk_mot_h0=round(s / 0.65, 2),
                      mutter_etter_anlegg_grad=round(TALLERK_N * s / 1.0 * 360, 0),
                      handkraft_tupp_ned_N=round((T_f - M_g) / (tupp * 1e-3), 2),
                      handkraft_tupp_opp_N=round((T_f + M_g) / (tupp * 1e-3), 2),
                      kraft_ned_på_tuppen_som_vippar_lampa_N=round(F_tipp, 2),
                      kraft_opp_på_tuppen_som_vippar_lampa_N=round(Mtot * 1e-3 * g * (c0.x - sx0) / (ARM_X1 + 4.0 - sx0), 2),
                      merknad='Vektprøva avgjer: armen vassrett skal halde 40 g i tuppen og gli med 80 g. Juster bakmutteren.')
    # elektro
    led_l = delar['E01']['form'].BoundingBox().xlen
    P = 8.0 * led_l * 1e-3
    ut['elektro'] = dict(led_lengd_mm=round(led_l, 1), led_effekt_W=round(P, 2), straum_A=round(P / 5.0, 2),
                         spenningsfall_V=round(P / 5.0 * 2 * 0.75 * 0.213, 3))
    return ut


# ======================================================================== flatmønster (DXF for laser og bøying)

K_STAL, K_AL = 0.44, 0.40               # K-faktor for Ri = t; leverandøren justerer etter eigne bøyetabellar


def bogetillegg(ri, t, k):
    return math.pi / 2 * (ri + k * t)


def flate_til_poly(f, defl=0.01):
    """CadQuery-flate i XZ-planet til ein shapely-polygon i (X, Z)."""
    from OCP.BRepAdaptor import BRepAdaptor_CompCurve
    from OCP.GCPnts import GCPnts_QuasiUniformDeflection
    from shapely.geometry import Polygon

    def pkt(w):
        c = BRepAdaptor_CompCurve(w.wrapped)
        d = GCPnts_QuasiUniformDeflection(c, defl)
        return [(d.Value(i).X(), d.Value(i).Z()) for i in range(1, d.NbPoints() + 1)]

    polys = []
    for face in f.Faces():
        polys.append(Polygon(pkt(face.outerWire()), [pkt(w) for w in face.innerWires()]))
    from shapely.ops import unary_union
    return unary_union(polys).buffer(0)


def doblar_flate(dxf=False):
    f = oyre_flate('doblar').cut(d_hol_xz())
    f = f.cut(sirkel_xz(stopp_pkt(), 1.45 if dxf else 1.5))
    # sporet for LED-leidningane går ut gjennom enden av tunga, så leidningane kjem fritt ut i kanalen framfor
    # endepluggen (D10)
    f = f.cut(stadion_xz((LEDD_X + 3.5, LEDD_Z - 1.0), (ARM_X0 + TUNGE_L + 2.0, LEDD_Z - 4.0), 1.1))
    return f.clean()


def flatmonster():
    """Flatmønster for alle laserdelane som shapely-polygonar i (X, W), med bøyeliner. W er Z i planet til den
    loddrette delen; bøygde flensar er bretta ut nedanfor (stativet) eller ut frå framflensen (armen)."""
    from shapely.geometry import box
    from shapely.ops import unary_union
    ut = {}
    ba = bogetillegg(BOY_RI, LAG_T, K_STAL)
    c = (LEDD_X, LEDD_Z)
    for pid, kva, fl in (('D01', 'fram', FLENS_L), ('D03', 'bak', FLENS_LB)):
        f = over_z(stativ_omriss(), BOY_ZC).cut(sirkel_xz(c, LAGER_R))
        if kva == 'fram':
            f = f.cut(boge_spor(c, BOGE_R, BOGE_B, BOGE_FRA, BOGE_TIL))
        else:
            v = VINDAUGE
            f = f.cut(polygon_xz([(v[0], v[2]), (v[1], v[2]), (v[1], v[3]), (v[0], v[3])]))
        p = flate_til_poly(f.clean())
        rett = fl - BOY_RI                                        # rett del av flensen etter bøyen
        w1 = BOY_ZC - ba
        w0 = w1 - rett
        flens = box(FLENS_X0, w0, FLENS_X1, w1 + 0.01)
        flens = flens.buffer(-6.0, join_style=1).buffer(6.0, join_style=1).union(box(FLENS_X0, w0 + 6.5, FLENS_X1, w1 + 0.01))
        poly = unary_union([p, box(FLENS_X0, w1, FLENS_X1, BOY_ZC + 0.01), flens]).buffer(0)
        ut[pid] = dict(poly=poly, boy=[((FLENS_X0, BOY_ZC - ba / 2), (FLENS_X1, BOY_ZC - ba / 2),
                                         f'BØY 90° {"FRAM" if kva == "fram" else "BAK"}, Ri 1,5')],
                       t=LAG_T, materiale='S235', tal=1)
    ut['D02'] = dict(poly=flate_til_poly(over_z(stativ_omriss(), BOY_ZC).cut(kanal_xz()[0]).clean()), boy=[], t=LAG_T,
                     materiale='S235', tal=1)
    # armen: framflensen med øyret ligg i planet; ryggen, bakflensen og bakleppa er bretta ut oppover, frameppa nedover
    ba = bogetillegg(1.0, ARM_T, K_AL)
    o = 1.0 + ARM_T                                               # utvendig tilbaketrekk per bøy (Ri + t)
    h = ARM_TOPP - ARM_BOTN
    w_topp, w_botn = ARM_TOPP - o, ARM_BOTN + o
    p = flate_til_poly(oyre_flate('flagg').cut(d_hol_xz()).clean())
    p = p.difference(box(ARM_X0, w_topp, ARM_X1 + 1, ARM_TOPP + 1)).difference(box(ARM_X0, ARM_BOTN - 1, ARM_X1 + 1, w_botn))
    deler, boy, w = [p], [], w_topp
    for i, (namn, lengd) in enumerate((('rygg', ARM_DJUP - 2 * o), ('bakflens', h - 2 * o), ('bakleppe', LEPPE - o))):
        deler.append(box(ARM_X0, w, ARM_X1, w + ba))
        boy.append(((ARM_X0, w + ba / 2), (ARM_X1, w + ba / 2), f'BØY {i + 1}: 90°, Ri 1,0'))
        w += ba
        deler.append(box(ARM_X0, w, ARM_X1, w + lengd))
        w += lengd
    deler.append(box(ARM_X0, w_botn - ba, ARM_X1, w_botn))
    boy.append(((ARM_X0, w_botn - ba / 2), (ARM_X1, w_botn - ba / 2), 'BØY 4: 90°, Ri 1,0, same veg som 1-3'))
    deler.append(box(ARM_X0, w_botn - ba - (LEPPE - o), ARM_X1, w_botn - ba))
    poly = unary_union(deler).buffer(0)
    # avlastingsspor (1 mm) der bøyane sluttar mot øyret
    poly = poly.difference(box(ARM_X0 - 1.0, w_topp - 1.0, ARM_X0, w_topp + ba + 1.0)).difference(
        box(ARM_X0 - 1.0, w_botn - ba - 1.0, ARM_X0, w_botn + 1.0))
    ut['D04'] = dict(poly=poly.buffer(0), boy=boy, t=ARM_T, materiale='Al 5754-H22', tal=1)
    ut['D05'] = dict(poly=flate_til_poly(doblar_flate(dxf=True)), boy=[], t=DOBLAR_T, materiale='Al 5754', tal=1)
    ut['D06'] = dict(poly=flate_til_poly(sirkel_xz((LEDD_X, LEDD_Z), 10.0).cut(d_hol_xz()).clean()), boy=[], t=1.0,
                     materiale='Rustfritt 1.4301', tal=1)
    return ut


def skriv_dxf():
    import ezdxf
    mappe = ROT / 'produksjon'
    mappe.mkdir(exist_ok=True)
    info = {}

    def ny():
        doc = ezdxf.new('R2010')
        doc.units = 4                                             # mm
        for namn, farge in (('SKJER', 7), ('BOY', 1), ('MERKNAD', 3)):
            doc.layers.add(namn, color=farge)
        return doc

    def poly_inn(msp, poly, lag='SKJER'):
        geom = [poly] if poly.geom_type == 'Polygon' else list(poly.geoms)
        for g in geom:
            for ring in [g.exterior, *g.interiors]:
                msp.add_lwpolyline(list(ring.coords), close=True, dxfattribs={'layer': lag})

    for pid, d in flatmonster().items():
        doc = ny()
        msp = doc.modelspace()
        poly_inn(msp, d['poly'])
        for a, b, tekst in d['boy']:
            msp.add_line(a, b, dxfattribs={'layer': 'BOY'})
            msp.add_text(tekst, dxfattribs={'height': 2.5, 'layer': 'BOY'}).set_placement((b[0] + 3, b[1] - 1.2))
        bb = d['poly'].bounds
        msp.add_text(f'{pid} Kran · {d["materiale"]} {str(d["t"]).replace(".", ",")} mm · {d["tal"]} stk',
                     dxfattribs={'height': 3.5, 'layer': 'MERKNAD'}).set_placement((bb[0], bb[1] - 10))
        if pid == 'D05':
            msp.add_text('Hol for stoppinnen Ø 2,9: røm til Ø 3 H7 (presspasning for ISO 2338 Ø 3 m6)',
                         dxfattribs={'height': 2.5, 'layer': 'MERKNAD'}).set_placement((bb[0], bb[1] - 16))
        if pid in ('D01', 'D03', 'D04'):
            msp.add_text('Bøyetillegg rekna med K = ' + (str(K_AL) if pid == 'D04' else str(K_STAL)).replace('.', ',') +
                         '. Leverandøren justerer etter eigne tabellar; mål på ferdig del står i LES_MEG.',
                         dxfattribs={'height': 2.5, 'layer': 'MERKNAD'}).set_placement((bb[0], bb[1] - 16))
        sti = mappe / f'{pid}_flat_{d["materiale"].split()[0].replace(".", "")}_{str(d["t"]).replace(".", "_")}mm_1til1.dxf'
        doc.saveas(str(sti))
        info[pid] = dict(fil=sti.name, areal_mm2=round(d['poly'].area, 1), boks_mm=[round(v, 2) for v in bb],
                         bøyar=len(d['boy']), materiale=d['materiale'], t_mm=d['t'])
    # malar for spreiaren og filten
    for pid, (b, h), tekst in (('D12', (ARM_X1 - 4.0 - LED_X0, ARM_DJUP - 2 * ARM_T - 0.5), 'D12 spreiar · opal PC 1,5 mm'),
                               ('D13', (FLENS_X1 - FLENS_X0 - 2.0, FLENS_LB - BOY_RI - LAG_T - 1.5), 'D13 filt 1 mm · 2 stk: '
                                f'{FLENS_L - BOY_RI - LAG_T - 1.5:.1f} og {FLENS_LB - BOY_RI - LAG_T - 1.5:.1f} mm breie'.replace('.', ','))):
        doc = ny()
        msp = doc.modelspace()
        msp.add_lwpolyline([(0, 0), (b, 0), (b, h), (0, h)], close=True, dxfattribs={'layer': 'SKJER'})
        msp.add_text(tekst, dxfattribs={'height': 3.5, 'layer': 'MERKNAD'}).set_placement((0, -8))
        doc.saveas(str(mappe / f'{pid}_mal_1til1.dxf'))
    return info


# ======================================================================== eksport

def filnamn(pid, namn):
    t = namn.lower()
    for a, b in (('ø', 'o'), ('å', 'aa'), ('æ', 'ae'), ('×', 'x'), (' ', '_'), (',', '')):
        t = t.replace(a, b)
    return f"{pid}_{''.join(c for c in t if c.isascii() and (c.isalnum() or c in '_-'))}"


def skriv_step(delar):
    (ROT / 'cad').mkdir(exist_ok=True)
    assy = cq.Assembly(name='Kran')
    for pid, d in delar.items():
        if not d['kjopt']:
            cq.exporters.export(cq.Workplane().add(d['form']), str(ROT / 'cad' / f"{filnamn(pid, d['namn'])}.step"))
        assy.add(d['form'], name=filnamn(pid, d['namn']), color=cq.Color(*d['farge']))
    assy.save(str(ROT / 'cad' / 'kran_samanstilling.step'))


def skriv_stl(delar, mappe, alle=False):
    """Éin STL per del i monteringsposisjon. Utan «alle» berre første eksemplar av like beslag. Kvar fil blir lesen
    inn att og sjekka for tett nett."""
    import trimesh
    mappe.mkdir(parents=True, exist_ok=True)
    tett = {}
    for pid, d in delar.items():
        if not alle and (pid.startswith(('M02', 'M03', 'M04', 'D13')) and pid[-1] != '1'):
            continue
        sti = mappe / f"{filnamn(pid, d['namn'])}.stl"
        reparert = 0
        for tol, ang in ((0.01, 0.08), (0.005, 0.05)):
            d['form'].exportStl(str(sti), tolerance=tol, angularTolerance=ang, relative=False)
            m = trimesh.load(str(sti), force='mesh')
            if m.is_watertight:
                break
        if not m.is_watertight:
            opne = len(trimesh.grouping.group_rows(m.edges_sorted, require_count=1))
            m.update_faces(m.nondegenerate_faces())
            m.remove_unreferenced_vertices()
            m.merge_vertices()
            if not m.is_watertight:
                m.fill_holes()
            if m.is_watertight:
                m.export(str(sti))
                reparert = opne
        tett[pid] = dict(tett=bool(m.is_watertight), toleranse_mm=tol, trekantar=int(len(m.faces)), tetta_opne_kantar=reparert)
    return tett


PRINTRETNING = {
    # rotasjon til printplata; omsett etter rotasjonen så delen står på z = 0
    'D07': ('x', 90.0),       # knotten: framsida ned (konsentrisk topp- og botnmønster)
    'D08': ('x', -90.0),      # hetta: baksida ned
    'D09': ('y', 90.0),       # endelokket: endeflata ned
    'D10': ('y', -90.0),      # endepluggen: på endeveggen, open opp
    'D11': ('x', 0.0),        # lomma: open side opp
    'D14': ('x', 180.0),      # loket: toppflata ned
}


def i_printretning(form, akse, grad):
    f = form.rotate(V(0, 0, 0), V(1, 0, 0) if akse == 'x' else V(0, 1, 0), grad) if grad else form
    bb = f.BoundingBox()
    return f.translate(V(-bb.xmin, -bb.ymin, -bb.zmin))


def skriv_3mf(sti, plate, tittel):
    """Plate: liste av (namn, form i printretning, (x, y) for hjørnet nede til venstre på plata)."""
    import zipfile
    obj, items = [], []
    for i, (namn, form, (px, py)) in enumerate(plate, start=1):
        verts, tris = form.tessellate(0.01, 0.08)
        vx = ''.join(f'<vertex x="{p.x:.4f}" y="{p.y:.4f}" z="{p.z:.4f}"/>' for p in verts)
        tx = ''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in tris)
        obj.append(f'<object id="{i}" type="model" name="{namn}"><mesh><vertices>{vx}</vertices>'
                   f'<triangles>{tx}</triangles></mesh></object>')
        items.append(f'<item objectid="{i}" transform="1 0 0 0 1 0 0 0 1 {px:.3f} {py:.3f} 0"/>')
    modell = ('<?xml version="1.0" encoding="UTF-8"?>\n'
              '<model unit="millimeter" xml:lang="nn-NO" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
              f'<metadata name="Title">{tittel}</metadata><metadata name="Designer">GK5 konsept D Kran</metadata>'
              f'<resources>{"".join(obj)}</resources><build>{"".join(items)}</build></model>')
    with zipfile.ZipFile(sti, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model', modell)


def leddprove():
    """Passprøve for leddet før laserordren: dei tre laga i stativhovudet, forsterkingsplata, øyret og låseskiva,
    printa flate i rett tjukkleik. Set dei saman med den verkelege akselen, skivene, fjørene, mutrane og dei fire
    leidningane, og rør armen 100 gonger mellom stoppane: leidningane skal ikkje setje seg fast i vridekammeret."""
    utsnitt = boks(LEDD_X - 42, LEDD_X + 42, -50, 50, LEDD_Z - 48, LEDD_Z + 30)
    ut = {}
    for pid, kva in (('P01', 'fram'), ('P02', 'midt'), ('P03', 'bak')):
        ut[pid] = stativ_lag(kva).intersect(utsnitt).clean()
    ut['P04'] = doblar()
    ut['P05'] = arm_plate().intersect(boks(0, ARM_X0 + 20, ARM_Y0 - 1, ARM_Y0 + ARM_T + 0.001, 0, 600)).clean()
    ut['P06'] = leddbeslag()['D06']
    return ut


def printplater(delar):
    mappe = ROT / 'print'
    mappe.mkdir(exist_ok=True)
    info = {}

    def legg_ut(former, start=(12.0, 32.0), luft=10.0, breidd=232.0):     # P1S sperrar 0-18 x 0-28 mm framme til venstre
        plate, x, y, rad_h = [], start[0], start[1], 0.0
        for namn, f in former:
            bb = f.BoundingBox()
            if x + bb.xlen > breidd + start[0]:
                x, y, rad_h = start[0], y + rad_h + luft, 0.0
            plate.append((namn, f, (x, y)))
            x += bb.xlen + luft
            rad_h = max(rad_h, bb.ylen)
        assert y + rad_h <= 250, ('plata er full', y + rad_h)
        return plate

    smaa = []
    for pid in ('D10', 'D11', 'D09', 'D14', 'D08', 'D07'):
        akse, grad = PRINTRETNING[pid]
        f = i_printretning(delar[pid]['form'], akse, grad)
        bb = f.BoundingBox()
        info[pid] = dict(storleik_mm=[round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)],
                         passar_P1S=bool(max(bb.xlen, bb.ylen, bb.zlen) <= 250))
        smaa.append((f'{pid} {delar[pid]["namn"]}', f))
    skriv_3mf(mappe / 'KRAN_P1S_plate1_smaadelar_PETG.3mf', legg_ut(smaa), 'Kran plate 1, smådelar i PETG')
    prove = []
    for pid, f in leddprove().items():
        prove.append((pid, i_printretning(f, 'x', 90.0)))
    skriv_3mf(mappe / 'KRAN_P1S_plate0_leddprove_PETG.3mf', legg_ut(prove), 'Kran plate 0, leddprøve')
    return info


def skriv_stykkliste(delar, k):
    rader = [('ID', 'Namn', 'Tal', 'Materiale / spesifikasjon', 'Masse g', 'Kjelde')]
    for pid, d in delar.items():
        if pid.startswith(('M02-2', 'M03-2', 'M04-2', 'M04-3', 'M04-4', 'D13-2')):
            continue
        tal = {'M02-1': 2, 'M03-1': 2, 'M04-1': TALLERK_N, 'D13-1': 2}.get(pid, 1)
        rader.append((pid.split('-')[0], d['namn'], tal, d['materiale'], round(d['masse'] * tal, 1), d['kjelde']))
    rader += [
        ('E05', 'Leidningar', 4, 'PTFE-isolert, mangetråda, 750 mm kvar: AWG28 raud (LED +) og blå (LED -), AWG30 kvit (berøring) og svart (jord)',
         4.0, 'kjøp'),
        ('M06', 'Epoksy', 1, '2-komponent, 25 ml: laminering av stativet, forsterkingsplata, lomma, endedelane', 12.0, 'kjøp'),
        ('M07', 'Koparteip og -folie', 1, 'koparteip med leiande lim (jord på stativet), koparfolie Ø 11 (knotten)', 1.0, 'kjøp'),
        ('M08', 'Lakk', 1, 'primer og silkematt sprøytelakk, startpunkt RAL 6021, prøvd mot fotoet', 0.0, 'kjøp'),
        ('M09', 'Forbruk', 1, 'gjengelås middels (Loctite 243), krympestrømpe, loddetinn, sparkel', 0.0, 'kjøp'),
        ('R01', 'Reserve for dimminga', 1, 'potensiometer WH148 B10K med brytar og PWM-kort (som Lut E02/E03), i lomma', 0.0,
         'kjøp om berøringa ikkje blir stabil'),
    ]
    with open(ROT / 'kontroll' / 'kran_stykkliste.csv', 'w', newline='', encoding='utf-8-sig') as f:
        csv.writer(f, delimiter=';').writerows(rader)


def main():
    t0 = time.time()
    print('Byggjer delane', flush=True)
    delar = bygg()
    print(f'Kontrollerer ({time.time() - t0:.0f} s)', flush=True)
    k = kontroll(delar)
    k['parametrar'] = {n: v for n, v in globals().items() if n.isupper() and isinstance(v, (int, float, tuple))}
    if not RASK:
        print(f'Eksporterer ({time.time() - t0:.0f} s)', flush=True)
        (ROT / 'kontroll').mkdir(exist_ok=True)
        skriv_step(delar)
        k['stl_tett'] = skriv_stl(delar, ROT / 'produksjon')
        skriv_stl(delar, ROT / 'render' / 'nett', alle=True)
        k['laser'] = skriv_dxf()
        k['print'] = printplater(delar)
        skriv_stykkliste(delar, k)
        json.dump({pid: dict(namn=d['namn'], farge=d['farge'], kjopt=d['kjopt'], arm=d['arm'], fil=filnamn(pid, d['namn']),
                             senter=[round(c, 3) for c in d['form'].Center().toTuple()]) for pid, d in delar.items()},
                  open(ROT / 'kontroll' / 'kran_delar.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        json.dump(k, open(ROT / 'kontroll' / 'kran_kontroll.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ugyldige = [p for p, d in k['delar'].items() if not d['gyldig']]
    print(json.dumps(dict(masse_g=k['velting']['arm_+0']['masse_g'], velting_minst=k['velting']['minste_grad'],
                          kollisjonar=k['kollisjonar'], ugyldige=ugyldige, rorsle=k['rorsle']['storste_overlapp_mm3'],
                          ledd=k['ledd'], laser=k.get('laser'), print=k.get('print'),
                          utette=[p for p, v in k.get('stl_tett', {}).items() if not v['tett']]), ensure_ascii=False, indent=1))
    print(f'Ferdig på {time.time() - t0:.0f} s')


if __name__ == '__main__':
    main()
