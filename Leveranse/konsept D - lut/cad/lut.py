# -*- coding: utf-8 -*-
"""
lut.py  ·  konsept D «Lut»: parametrisk CAD-samanstilling, kontroll og eksport

  py -3 cad/lut.py           byggjer delane, kontrollerer og eksporterer alt
  py -3 cad/lut.py --rask    berre bygg og kontroll (ingen filer ut)

Grunnlag: referanse/maaling.json. Opprisset (vinklar, høgder, radiar, hovud og knott) er målt i skissa med
0,5 mm per pikselpunkt. Djupna (fot, blad) syner ikkje i skissa og er vald; vala står under «valde».

Koordinatar: X langs lampa frå venstre ende av foten, Y djupn (+Y bak, -Y mot den som ser skissa), Z opp frå
bordet. Alle mål i mm. Delane ligg i monteringsposisjon; printretninga blir sett når printplatene blir skrivne.
"""
from __future__ import annotations

import csv
import json
import math
import sys
import time
import zipfile
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
# ---- målt i skissa (0,5 mm per pikselpunkt; sjå referanse/maaling.json)
FOT_L = 195.0                 # lengda til foten (målt 195,35)
FOT_Z = 32.0                  # toppen av foten over bordet (målt 31,75)
BAK_DXDZ = 0.5625             # bakkanten: X aukar 0,5625 per mm opp, 29,36 grader frå loddrett
INN_X0, INN_DXDZ = 122.3, 0.15266   # innerkanten: X = INN_X0 + INN_DXDZ * Z, 8,68 grader frå loddrett
HOV_X = 204.5                 # aksen til hovudet (målt 204,65)
HOV_R = 40.0                  # hovudet er Ø 80
HOV_Z0, HOV_Z1 = 194.0, 274.0  # botn og topp av hovudet (målt 194,25 og 273,55): høgd = diameter
TOPP_R = 40.0                 # avrundinga mellom bakkant og topp, same radius som hovudet (målt 39,8)
INNHJ_R = 5.0                 # innerhjørnet der innerkanten møter hovudet
KNOTT_D, KNOTT_TOPP = 20.0, 50.0    # knotten (målt Ø 20,0, topp 50,25)

# ---- valde (djupna syner ikkje i skissa)
FOT_B = 80.0                  # djupna til foten = hovuddiameteren
BLAD_T = 40.0                 # tjukkleiken til bladet = radien til hovudet
FOT_RV = (FOT_B - BLAD_T) / 2   # hjørneradius i venstre ende (20): den rette enden er nett så brei som bladet
FOT_RH = 40.0                 # halvsirkel i høgre ende, same radius som hovudet
BAK_X0 = 2.0                  # bakkanten startar der den runda toppkanten på foten sluttar
KNOTT_X = FOT_L - FOT_RH      # 155: knotten står i senter av den runde enden (målt 153,3)

# ---- kantradiar
R_BLAD = 1.5
R_HOV_TOPP, R_HOV_BOTN = 2.0, 1.0
R_FOT_TOPP, R_FOT_BOTN = 2.0, 1.0
R_KNOTT_TOPP, R_KNOTT_BOTN = 1.5, 0.5

# ---- konstruksjon
VEGG = 2.4                    # vegg i fot, hovud (6 strengar à 0,4 mm)
FOT_TAK = 3.0                 # topplata i foten (panel for potensiometeret)
FOT_BOTN = 2.0                # gummiføtene: skalet står 2 mm over bordet
PLATE_T = 4.0                 # botnplata: 4 mm S235, laserskoren
FALS, PLATE_KLARING = 1.2, 0.5    # 0,5 mm luft rundt stålplata: PLA krympar om lag 0,5 mm over 192 mm
PLATE_HOL_R, PLATE_SENK_D = 1.9, 7.0   # hol Ø 3,8 i botnplata, senka 90° til Ø 7,0 nedanfrå (ISO 10642 M3, dk ≤ 6,72)
SKUGGE_KNOTT = 0.8            # luft mellom knotten og foten
RING_R0, RING_Z0 = 28.0, 217.0     # magnetringen i hovudet: indre radius, underflate (= toppen av lyskoppen)
KOPP_Z0 = 195.0               # nedre kant av lyskoppen: 1 mm inne i hovudet
KOPP_RY, KOPP_RI = 37.2, 35.6  # lyskoppen: ytre og indre radius (0,4 mm luft til hovudet)
MAGNET_R, MAGNET_VINKLAR = 32.0, (0.0, 120.0, 240.0)
SPREIAR_R, SPREIAR_T = 35.5, 1.0   # spreiaren: Ø 71 × 1 mm opal PC eller LCD-diffusorark
LED_R, LED_T = 25.0, 1.6           # LED-kort Ø 50 (nominelt), loddepunkta på LED-sida ved kanten
KJOL_R, KJOL_T = 25.0, 1.5         # kjøleplate Ø 50 × 1,5 aluminium, same storleik som LED-kortet
KABEL_SPOR_R, KABEL_SPOR_VINKEL = 26.6, 60.0   # kabelspalta i lyskoppen: utanfor kjøleplata, innanfor magnetringen
LUG_R, LUG_VINKLAR = 7.8, (0.0, 90.0, 180.0, 270.0)   # låsetappen på potensiometeret (nominelt; mål på delen)

BLAD_SKRUAR = ((20.0, 0.0), (104.0, -11.0), (104.0, 11.0))   # M4 frå innsida av foten opp i bladet
KABEL_FOT = (62.0, 0.0)
PLATE_SKRUAR = ((40.0, -31.0), (40.0, 31.0), (135.0, -31.0), (135.0, 31.0))
FOTER = ((10.0, -27.0), (10.0, 27.0), (172.0, -26.0), (172.0, 26.0))
FOT_R_GUMMI, FOT_H_GUMMI = 5.0, 2.0
USB_X, USB_Z = 115.0, 14.0
USB_SPALTE = 3.0              # luft bak USB-C-kontakten til ribba: kontakten må kunne gå 2,4 mm attende for å komme forbi veggen
HOV_SKRUAR_Z = (235.0, 265.0)
HOV_KABEL_Z = 252.0

# ======================================================================== hjelparar


def norm(v):
    l = math.hypot(*v)
    return tuple(c / l for c in v)


def xz(p, y=0.0):
    return V(p[0], y, p[1])


def linje(a, b):
    return Edge.makeLine(xz(a), xz(b))


def boge(a, m, b):
    return Edge.makeThreePointArc(xz(a), xz(m), xz(b))


def flate(kantar):
    return Face.makeFromWires(Wire.assembleEdges(kantar))


def polyflate_xz(pts):
    return flate([linje(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))])


def prisme(f, v):
    return cq.Shape.cast(BRepPrimAPI_MakePrism(f.wrapped, gp_Vec(*v)).Shape())


def dreie(f, x0, y0=0.0):
    return cq.Shape.cast(BRepPrimAPI_MakeRevol(f.wrapped, gp_Ax1(gp_Pnt(x0, y0, 0), gp_Dir(0, 0, 1)), 2 * math.pi).Shape())


def sylinder(r, z0, z1, x, y):
    return Solid.makeCylinder(r, z1 - z0, V(x, y, z0), V(0, 0, 1))


def sylinder_x(r, x0, x1, y, z):
    return Solid.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


def boks(x0, x1, y0, y1, z0, z1):
    return Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def kantar_ved_z(s, z, tol=1e-4):
    return [e for e in s.Edges() if abs(e.BoundingBox().zmin - z) < tol and abs(e.BoundingBox().zmax - z) < tol]


def polar(r, vinkel, x0=HOV_X):
    a = math.radians(vinkel)
    return x0 + r * math.cos(a), r * math.sin(a)


# ======================================================================== geometri


def blad_geometri():
    """Punkta i opprisset til bladet. Profilen går mot klokka: rot, innerkant, innerhjørne, underside, (snitt i
    hovudaksen), topp, toppavrunding, bakkant."""
    zr = FOT_Z
    A = (BAK_X0, zr)
    B = (INN_X0 + INN_DXDZ * zr, zr)
    Pc = (INN_X0 + INN_DXDZ * HOV_Z0, HOV_Z0)                 # skjeringa innerkant × underside
    u1 = norm((INN_DXDZ, 1.0))
    t1 = INNHJ_R * math.tan((math.pi / 2 - math.atan(INN_DXDZ)) / 2)
    T4 = (Pc[0] - t1 * u1[0], Pc[1] - t1 * u1[1])
    T3 = (Pc[0] + t1, Pc[1])
    C3 = (T4[0] + INNHJ_R * u1[1], T4[1] - INNHJ_R * u1[0])
    k = norm((Pc[0] - C3[0], Pc[1] - C3[1]))
    M3 = (C3[0] + INNHJ_R * k[0], C3[1] + INNHJ_R * k[1])
    Q = (BAK_X0 + BAK_DXDZ * (HOV_Z1 - zr), HOV_Z1)          # skjeringa bakkant × topp
    ub = norm((-BAK_DXDZ, -1.0))
    t2 = TOPP_R * math.tan(math.acos(-ub[0]) / 2)
    T2 = (Q[0] + t2, Q[1])
    T1 = (Q[0] + t2 * ub[0], Q[1] + t2 * ub[1])
    C2 = (T2[0], T2[1] - TOPP_R)
    k = norm((Q[0] - C2[0], Q[1] - C2[1]))
    M2 = (C2[0] + TOPP_R * k[0], C2[1] + TOPP_R * k[1])
    return dict(A=A, B=B, Pc=Pc, T1=T1, T2=T2, T3=T3, T4=T4, M2=M2, M3=M3, C2=C2, C3=C3, Q=Q)


def kanal():
    """Kabelkanalen gjennom bladet: diamantprofil (8 mm diagonal) så taket ber seg sjølv når bladet ligg flatt i
    printaren. Frå rota rett opp langs bladet, ein boge med R15, og vassrett inn mot hovudet."""
    S0, K, E, R = (62.0, 31.0), (140.0, HOV_KABEL_Z), (158.0, HOV_KABEL_Z), 15.0
    d1 = norm((K[0] - S0[0], K[1] - S0[1]))
    S = (S0[0] - 4 * d1[0], S0[1] - 4 * d1[1])
    t = R * math.tan(math.acos(d1[0]) / 2)
    Ta = (K[0] - t * d1[0], K[1] - t * d1[1])
    Tb = (K[0] + t, K[1])
    C = (Ta[0] + R * d1[1], Ta[1] - R * d1[0])
    k = norm((K[0] - C[0], K[1] - C[1]))
    M = (C[0] + R * k[0], C[1] + R * k[1])
    sti = Wire.assembleEdges([linje(S, Ta), boge(Ta, M, Tb), linje(Tb, E)])
    n = (d1[1], -d1[0])
    h = 4.0
    pts = [V(S[0], h, S[1]), V(S[0] + h * n[0], 0, S[1] + h * n[1]), V(S[0], -h, S[1]), V(S[0] - h * n[0], 0, S[1] - h * n[1])]
    profil = Wire.makePolygon(pts, close=True)
    return Solid.sweep(profil, [], sti, True, False), dict(S=S, Ta=Ta, Tb=Tb, C=C, E=E)   # binormal-modus gjev ugyldig solid


def blad():
    g = blad_geometri()
    kantar = [linje(g['A'], g['B']), linje(g['B'], g['T4']), boge(g['T4'], g['M3'], g['T3']),
              linje(g['T3'], (HOV_X, HOV_Z0)), linje((HOV_X, HOV_Z0), (HOV_X, HOV_Z1)),
              linje((HOV_X, HOV_Z1), g['T2']), boge(g['T2'], g['M2'], g['T1']), linje(g['T1'], g['A'])]
    s = prisme(flate(kantar), (0, BLAD_T, 0)).translate(V(0, -BLAD_T / 2, 0))
    val = []
    for e in s.Edges():
        bb = e.BoundingBox()
        if abs(bb.ymax - bb.ymin) < 1e-6 and abs(abs(bb.ymin) - BLAD_T / 2) < 1e-6:
            if bb.xmin > HOV_X - 1e-3:
                continue                                     # snittet i hovudaksen blir skore bort
            val.append(e)
        elif abs(bb.ymax - bb.ymin - BLAD_T) < 1e-6 and abs(bb.zmin - FOT_Z) < 1e-4 and abs(bb.zmax - FOT_Z) < 1e-4:
            val.append(e)                                    # dei to tverrkantane ved rota
    s = s.fillet(R_BLAD, val)
    s = s.cut(Solid.makeCylinder(HOV_R, 120.0, V(HOV_X, 0, HOV_Z0 - 20.0)))   # enden blir hol som hovudet
    xi = HOV_X - HOV_R
    s = s.fuse(sylinder_x(4.0, xi - 4.5, xi + VEGG, 0, HOV_KABEL_Z))           # styretapp gjennom veggen i hovudet
    s = s.fuse(Solid.makeCone(4.0, 3.5, 0.5, V(xi + VEGG - 0.01, 0, HOV_KABEL_Z), V(1, 0, 0)))   # fas 0,5 × 45° på tuppen
    kn, _ = kanal()
    s = s.cut(kn)
    s = s.cut(sylinder_x(2.75, xi - 10.5, xi + VEGG + 1.5, 0, HOV_KABEL_Z))
    for x, y in BLAD_SKRUAR:                                 # innpressmutter M4: Ø 5,6 × 9
        s = s.cut(sylinder(2.8, FOT_Z - 1.0, FOT_Z + 9.0, x, y))
    for zc in HOV_SKRUAR_Z:                                  # innpressmutter M3: Ø 4,0 × 7
        s = s.cut(sylinder_x(2.0, xi - 7.0, xi + 2.0, 0, zc))
    return s.clean()


def hovud():
    s = sylinder(HOV_R, HOV_Z0, HOV_Z1, HOV_X, 0)
    s = s.fillet(R_HOV_TOPP, kantar_ved_z(s, HOV_Z1))
    s = s.fillet(R_HOV_BOTN, kantar_ved_z(s, HOV_Z0))
    ri = HOV_R - VEGG
    s = s.cut(sylinder(ri, HOV_Z0 - 1.0, HOV_Z1 - VEGG, HOV_X, 0))
    rr = lambda r, z: (HOV_X + r, z)
    ring = dreie(polyflate_xz([rr(RING_R0, RING_Z0), rr(ri + 0.5, RING_Z0),
                               rr(ri + 0.5, RING_Z0 + 3.0 + ri + 0.5 - RING_R0), rr(RING_R0, RING_Z0 + 3.0)]), HOV_X)
    s = s.fuse(ring)
    xi = HOV_X - HOV_R
    for zc in HOV_SKRUAR_Z:                                  # flate anlegg for skruhovudet, fasa 45° oppover
        topp = zc + 9.0
        if topp > HOV_Z1 - VEGG - 1.0:
            pts = [(xi + 1.0, zc - 5.0), (xi + 5.0, zc - 5.0), (xi + 5.0, HOV_Z1 - VEGG + 0.3), (xi + 1.0, HOV_Z1 - VEGG + 0.3)]
        else:
            pts = [(xi + 1.0, zc - 5.0), (xi + 5.0, zc - 5.0), (xi + 5.0, zc + 5.0), (xi + 1.0, topp)]
        s = s.fuse(prisme(polyflate_xz(pts).translate(V(0, -5.0, 0)), (0, 10.0, 0)))
    for a in MAGNET_VINKLAR:
        x, y = polar(MAGNET_R, a)
        s = s.cut(sylinder(3.1, RING_Z0 - 0.1, RING_Z0 + 3.1, x, y))
    for zc in HOV_SKRUAR_Z:
        s = s.cut(sylinder_x(1.7, xi - 2.0, xi + 8.0, 0, zc))
    s = s.cut(sylinder_x(4.45, xi - 2.0, xi + 8.0, 0, HOV_KABEL_Z))     # Ø 8,9 for styretappen Ø 8: begge printa liggjande
    return s.clean()


def d_kantar(z=0.0):
    r1, b, xc = FOT_RV, FOT_B / 2, FOT_L - FOT_RH
    c = math.cos(math.pi / 4)
    P = lambda x, y: V(x, y, z)
    e = [Edge.makeLine(P(0, b - r1), P(0, -(b - r1))),
         Edge.makeThreePointArc(P(0, -(b - r1)), P(r1 - r1 * c, -(b - r1) - r1 * c), P(r1, -b)),
         Edge.makeLine(P(r1, -b), P(xc, -b)),
         Edge.makeThreePointArc(P(xc, -b), P(FOT_L, 0), P(xc, b)),
         Edge.makeLine(P(xc, b), P(r1, b)),
         Edge.makeThreePointArc(P(r1, b), P(r1 - r1 * c, (b - r1) + r1 * c), P(0, b - r1))]
    return Wire.assembleEdges(e)


def d_flate(innsett=0.0, z=0.0):
    w = d_kantar(z)
    if not innsett:
        return Face.makeFromWires(w)
    kand = [Face.makeFromWires(ww) for d in (-innsett, innsett) for ww in w.offset2D(d, 'arc')]
    return min(kand, key=lambda f: f.Area())


def spor_y(x, z, lengd, hogd, y0, y1):
    r = hogd / 2
    s = boks(x - lengd / 2 + r, x + lengd / 2 - r, y0, y1, z - r, z + r)
    for dx in (-(lengd / 2 - r), lengd / 2 - r):
        s = s.fuse(Solid.makeCylinder(r, y1 - y0, V(x + dx, y0, z), V(0, 1, 0)))
    return s


def fot():
    s = prisme(d_flate(0, FOT_BOTN), (0, 0, FOT_Z - FOT_BOTN))
    s = s.fillet(R_FOT_TOPP, kantar_ved_z(s, FOT_Z))
    s = s.fillet(R_FOT_BOTN, kantar_ved_z(s, FOT_BOTN))
    zt, zp = FOT_Z - FOT_TAK, FOT_BOTN + PLATE_T
    s = s.cut(prisme(d_flate(VEGG, FOT_BOTN - 1.0), (0, 0, zt - (FOT_BOTN - 1.0))))
    s = s.cut(prisme(d_flate(VEGG - FALS, FOT_BOTN - 1.0), (0, 0, PLATE_T + 1.0)))
    for x, y in PLATE_SKRUAR:
        s = s.fuse(sylinder(4.0, zp, zt + 0.5, x, y))
    for x, y in BLAD_SKRUAR:
        s = s.fuse(sylinder(6.5, zt - 5.0, zt + 0.5, x, y))
    s = s.fuse(usb_bakstotte())
    for x, y in PLATE_SKRUAR:                                # innpressmutter M3 × 5,7: hol Ø 4,0 × 7
        s = s.cut(sylinder(2.0, zp - 0.5, zp + 7.0, x, y))
    for x, y in BLAD_SKRUAR:
        s = s.cut(sylinder(2.25, zt - 6.0, FOT_Z + 1.0, x, y))
    s = s.cut(sylinder(5.5, zt - 1.0, FOT_Z + 1.0, *KABEL_FOT))
    s = s.cut(sylinder(3.65, zt - 1.0, FOT_Z + 1.0, KNOTT_X, 0))
    for a in LUG_VINKLAR:                                    # lomme for låsetappen, 2 mm inn i topplata nedanfrå
        lomme = boks(KNOTT_X + LUG_R - 1.5, KNOTT_X + LUG_R + 1.5, -0.9, 0.9, zt - 0.5, zt + 2.0)
        s = s.cut(lomme.rotate(V(KNOTT_X, 0, 0), V(KNOTT_X, 0, 1), a))
    yv = FOT_B / 2
    s = s.cut(spor_y(USB_X, USB_Z, 9.4, 3.8, yv - VEGG - 1.0, yv + 1.0))
    s = s.cut(boks(USB_X - 6.0, USB_X + 6.0, yv - VEGG - 1.0, yv - VEGG + 1.0, USB_Z - 3.0, USB_Z + 3.0))
    return s.clean()


def usb_bakstotte():
    """Ribbe bak USB-C-kontakten, hengt frå topplata. Kontakten blir løfta inn bak ribba og skyvd ut i lomma, og spalta på 3,0 mm mellom
    kontakten og ribba blir fylt med epoksy, så innstikkskrafta går gjennom epoksyen inn i ribba. Spor midt i ribba for
    leidningane. Ved 20 N er bøyespenninga om lag 10 MPa."""
    yb = FOT_B / 2 - VEGG + 1.0 - 8.8                      # baksida av kontakten (29,8)
    zt = FOT_Z - FOT_TAK
    r = boks(USB_X - 7.0, USB_X + 7.0, yb - USB_SPALTE - 4.5, yb - USB_SPALTE, 9.0, zt + 0.5)
    return r.cut(boks(USB_X - 2.5, USB_X + 2.5, yb - USB_SPALTE - 6.0, yb - 1.0, 8.0, 17.0))


def botnplate():
    s = prisme(d_flate(VEGG - FALS + PLATE_KLARING, FOT_BOTN), (0, 0, PLATE_T))
    rs = PLATE_SENK_D / 2
    for x, y in PLATE_SKRUAR:
        s = s.cut(sylinder(PLATE_HOL_R, FOT_BOTN - 1.0, FOT_BOTN + PLATE_T + 1.0, x, y))
        s = s.cut(Solid.makeCone(rs + 0.01, PLATE_HOL_R, rs - PLATE_HOL_R + 0.01, V(x, y, FOT_BOTN - 0.01), V(0, 0, 1)))
    return s.clean()


def knott():
    z0 = FOT_Z + SKUGGE_KNOTT
    s = sylinder(KNOTT_D / 2, z0, KNOTT_TOPP, KNOTT_X, 0)
    s = s.fillet(R_KNOTT_TOPP, kantar_ved_z(s, KNOTT_TOPP))
    s = s.fillet(R_KNOTT_BOTN, kantar_ved_z(s, z0))
    s = s.cut(sylinder(6.75, z0 - 1.0, 36.4, KNOTT_X, 0))      # over mutter M7 og skive; taket stoppar mot halsen
    s = s.cut(sylinder(2.95, 36.3, 45.0, KNOTT_X, 0))          # pressast på riflet aksel Ø 6
    return s.clean()


def lyskopp():
    rr = lambda r, z: (HOV_X + r, z)
    pts = [rr(3.0, RING_Z0), rr(KOPP_RY, RING_Z0), rr(KOPP_RY, KOPP_Z0), rr(34.8, KOPP_Z0), rr(34.8, KOPP_Z0 + 0.2),
           rr(KOPP_RI, KOPP_Z0 + 1.0), rr(KOPP_RI, RING_Z0 - 2.0), rr(3.0, RING_Z0 - 2.0)]
    s = dreie(polyflate_xz(pts), HOV_X)
    for a in MAGNET_VINKLAR:
        x, y = polar(MAGNET_R, a)
        s = s.fuse(sylinder(4.5, RING_Z0 - 4.0, RING_Z0 - 1.8, x, y))
        s = s.cut(sylinder(3.1, RING_Z0 - 3.1, RING_Z0 + 0.1, x, y))
    for sgn in (1, -1):                                      # to hakk for fingernegl
        y0, y1 = sorted((sgn * 34.0, sgn * 38.0))
        s = s.cut(boks(HOV_X - 1.5, HOV_X + 1.5, y0, y1, KOPP_Z0 - 1.0, KOPP_Z0 + 1.5))
    spor = boks(HOV_X + KABEL_SPOR_R - 1.1, HOV_X + KABEL_SPOR_R + 1.1, -1.5, 1.5, RING_Z0 - 2.2, RING_Z0 + 0.1)
    s = s.cut(spor.rotate(V(HOV_X, 0, 0), V(HOV_X, 0, 1), KABEL_SPOR_VINKEL))   # kabelen går forbi kanten av LED-kortet
    return s.clean()


def skive(r, z0, t, ri=0.0, x=HOV_X, y=0.0):
    s = sylinder(r, z0, z0 + t, x, y)
    return s.cut(sylinder(ri, z0 - 1, z0 + t + 1, x, y)) if ri else s


def sekskant(af, z0, z1, x, y, hol=0.0):
    r = af / math.sqrt(3)
    pts = [V(x + r * math.cos(math.radians(30 + 60 * i)), y + r * math.sin(math.radians(30 + 60 * i)), z0) for i in range(6)]
    s = prisme(Face.makeFromWires(Wire.makePolygon(pts, close=True)), (0, 0, z1 - z0))
    return s.cut(sylinder(hol, z0 - 1, z1 + 1, x, y)) if hol else s


# ---- kjøpte delar (nominelle mål til kollisjons- og plasskontroll; mål sjølv før bestilling)

def potmeter():
    """WH148-type 16 mm potensiometer med brytar, M7×0,75 hals, riflet aksel Ø 6 kappa til 15 mm, på dimmarkortet."""
    x, zt = KNOTT_X, FOT_Z - FOT_TAK
    s = sylinder(8.5, 12.0, zt, x, 0)                        # hus med brytar, 17 mm djupt
    s = s.fuse(sylinder(3.5, zt, 36.0, x, 0))                # hals M7, 7 mm
    s = s.fuse(sylinder(2.95, 36.0, 44.0, x, 0))             # aksel (modellert som hol i knotten)
    return s


def mutter_m7():
    return skive(5.0, FOT_Z, 0.5, 3.6, KNOTT_X).fuse(sekskant(10.0, FOT_Z + 0.5, FOT_Z + 2.5, KNOTT_X, 0, 3.55))


def dimmarkort():
    """PWM-dimmar 5–24 V: kort 34 × 21 × 1,6 med komponentar ved sida av potensiometeret (nominelt)."""
    s = boks(KNOTT_X - 12.0, KNOTT_X + 22.0, -10.5, 10.5, 10.4, 12.0)
    return s.fuse(boks(KNOTT_X + 9.0, KNOTT_X + 21.0, -8.0, 8.0, 12.0, 19.0))


def usb_c():
    yv = FOT_B / 2 - VEGG + 1.0
    s = boks(USB_X - 5.5, USB_X + 5.5, yv - 8.8, yv, USB_Z - 2.5, USB_Z + 2.5)
    return s.fuse(spor_y(USB_X, USB_Z, 8.9, 3.2, yv, FOT_B / 2 - 0.1))     # munnen er ein stadion som kontakten


def skrue(d, l, hovud_d, hovud_h, start, retning):
    """Skrue med hovudet ved start, skaftet langs retning."""
    sx, sy, sz = start
    dx, dy, dz = retning
    h = Solid.makeCylinder(hovud_d / 2, hovud_h, V(sx - dx * hovud_h, sy - dy * hovud_h, sz - dz * hovud_h), V(dx, dy, dz))
    return h.fuse(Solid.makeCylinder(d / 2 - 0.05, l, V(sx, sy, sz), V(dx, dy, dz)))


def skruar():
    ut = {}
    zt = FOT_Z - FOT_TAK - 5.0
    for i, (x, y) in enumerate(BLAD_SKRUAR):
        ut[f'M03-{i + 1}'] = skrue(4.0, 16.0, 7.0, 4.0, (x, y, zt), (0, 0, 1))
    xi = HOV_X - HOV_R + 5.0
    for i, zc in enumerate(HOV_SKRUAR_Z):
        ut[f'M04-{i + 1}'] = skrue(3.0, 10.0, 5.5, 3.0, (xi, 0, zc), (-1, 0, 0))
    for i, (x, y) in enumerate(PLATE_SKRUAR):                # ISO 10642 M3 × 8 senkskrue: hovudet ligg i plan med plata
        hovud = Solid.makeCone(3.36, 1.5, 1.86, V(x, y, FOT_BOTN), V(0, 0, 1))
        ut[f'M05-{i + 1}'] = hovud.fuse(Solid.makeCylinder(1.45, 8.0, V(x, y, FOT_BOTN), V(0, 0, 1)))
    return ut


def magnetar():
    ut = {}
    for i, a in enumerate(MAGNET_VINKLAR):
        x, y = polar(MAGNET_R, a)
        ut[f'M06-{i + 1}'] = sylinder(3.0, RING_Z0 + 0.05, RING_Z0 + 3.05, x, y)
        ut[f'M06-{i + 4}'] = sylinder(3.0, RING_Z0 - 3.05, RING_Z0 - 0.05, x, y)
    return ut


def gummifoter():
    return {f'M07-{i + 1}': sylinder(FOT_R_GUMMI, 0.0, FOT_H_GUMMI, x, y) for i, (x, y) in enumerate(FOTER)}


def passprove_blad():
    """Plate 0a, printa med innstillingane for bladet (plate 1): prøvene for bladet, liggjande som bladet.
    Kloss med innpresshola frå rota og enden (M4 Ø 5,6 × 9 og M3 Ø 4,0 × 7), hola liggjande med opning i sideflata.
    Kloss med styretappen (Ø 8, fas 0,5, røyr med Ø 5,5-hol som i bladet), liggjande 20 mm over plata."""
    kloss = boks(0, 30, 0, 14, 0, 14)
    kloss = kloss.cut(Solid.makeCylinder(2.8, 9.0, V(8, -0.1, 7), V(0, 1, 0)))
    kloss = kloss.cut(Solid.makeCylinder(2.0, 7.0, V(22, -0.1, 7), V(0, 1, 0)))
    tapp = boks(40, 52, 0, 22, 0, 28)
    tapp = tapp.fuse(sylinder_x(4.0, 51.9, 52 + VEGG, 11, 20))
    tapp = tapp.fuse(Solid.makeCone(4.0, 3.5, 0.5, V(52 + VEGG - 0.01, 11, 20), V(1, 0, 0)))
    tapp = tapp.cut(sylinder_x(2.75, 44.0, 52 + VEGG + 1.0, 11, 20))
    return kloss.fuse(tapp)


def passprove_hovud_fot():
    """Plate 0b, printa med innstillingane for plate 2 (hovud, fot og knott): kvar prøve ligg som i delen.
    Vegg på 2,4 mm med holet til styretappen (Ø 8,9 liggjande, 22 mm over plata, som i hovudet opp-ned).
    Magnetlomme Ø 6,2 × 3,1 opna oppover frå eit fast golv, som i ringen i hovudet.
    Tårn Ø 8 med M3-hol Ø 4,0 × 7 ovanfrå, som tårna i foten.
    Panel på 3 mm rett på plata med hol for potensiometeret (Ø 7,3) og fire lommer for låsetappen, 2 mm djupe ovanfrå,
    som topplata i foten opp-ned. Knottstubb med same innside og stopp som knotten. Ring med veggen i hovudet;
    lyskoppen (plate 3, 37 min) er sjølv prøva for passinga mot ringen og for magnetane i PETG."""
    vegg = boks(0, 2.4, 0, 22, 0, 32).fuse(boks(-4, 6.4, 0, 22, 0, 3))
    vegg = vegg.cut(sylinder_x(4.45, -2, 5, 11, 22))
    magnet = boks(14, 28, 0, 14, 0, 6).cut(sylinder(3.1, 6 - 3.1, 6.5, 21, 7))
    taarn = sylinder(4.0, 0, 23.5, 36, 7).cut(sylinder(2.0, 23.5 - 7.0, 24.0, 36, 7))
    panel = boks(46, 70, 0, 24, 0, FOT_TAK).cut(sylinder(3.65, -0.5, FOT_TAK + 0.5, 58, 12))
    for a in LUG_VINKLAR:
        lomme = boks(58 + LUG_R - 1.5, 58 + LUG_R + 1.5, 12 - 0.9, 12 + 0.9, FOT_TAK - 2.0, FOT_TAK + 0.5)
        panel = panel.cut(lomme.rotate(V(58, 12, 0), V(58, 12, 1), a))
    zr = 14.0                                                  # knottstubb, opp-ned som knotten
    djup_r, djup_b = 36.4 - (FOT_Z + SKUGGE_KNOTT), 45.0 - 36.3
    stubb = sylinder(KNOTT_D / 2, 0, zr, 85, 12)
    stubb = stubb.cut(sylinder(6.75, zr - djup_r, zr + 0.5, 85, 12)).cut(sylinder(2.95, zr - djup_r - djup_b, zr - djup_r + 0.1, 85, 12))
    ring_h = sylinder(HOV_R, 0, 8.0, 45, 75).cut(sylinder(HOV_R - VEGG, -1, 9.0, 45, 75))
    return vegg.fuse(magnet).fuse(taarn).fuse(panel).fuse(stubb).fuse(ring_h)


# ======================================================================== delliste

PLA_GRAA = (0.55, 0.55, 0.54)
DELAR = [
    # id, namn, materiale, tettleik g/cm³, farge, byggjar, fylling ('massiv' | 'skal' | 'infill')
    ('D01', 'Blad', 'PLA matt grå, print liggjande', 1.24, PLA_GRAA, blad, 'infill'),
    ('D02', 'Hovud', 'PLA matt grå, print opp-ned', 1.24, PLA_GRAA, hovud, 'massiv'),
    ('D03', 'Fot', 'PLA matt grå, print opp-ned', 1.24, PLA_GRAA, fot, 'massiv'),
    ('D04', 'Botnplate', 'Stål S235 4 mm, laserskoren frå DXF, 4 hol senka 90° Ø 7 nedanfrå (alt.: PLA, plate 4, utan ballast)',
     7.85, (0.22, 0.22, 0.23), botnplate, 'massiv'),
    ('D05', 'Knott', 'PLA matt grå, print opp-ned', 1.24, PLA_GRAA, knott, 'massiv'),
    ('D06', 'Lyskopp', 'PETG kvit, print opp-ned', 1.27, (0.92, 0.92, 0.90), lyskopp, 'massiv'),
    ('D07', 'Spreiar', 'Opal PC 1 mm eller LCD-diffusorark, Ø 71', 1.20, (0.98, 0.97, 0.93),
     lambda: skive(SPREIAR_R, KOPP_Z0 + 1.0, SPREIAR_T), 'massiv'),
    ('D08', 'Kjøleplate', 'Aluminium 1,5 mm, Ø 50 med Ø 6-hol i senter, skoren frå DXF', 2.70, (0.75, 0.76, 0.78),
     lambda: skive(KJOL_R, RING_Z0 - 2.0 - KJOL_T, KJOL_T, 3.0), 'massiv'),
]
KJOPT = [
    # id, namn, spesifikasjon, masse g (anslått), farge, byggjar
    ('E01', 'LED-modul', 'Rund aluminiums-LED Ø 50, 5 V, ≤ 1,5 W med hovudet i PLA (≤ 2 W med hovudet i PETG, plate 5), '
     '2700 K, CRI ≥ 90, loddepunkt + og − på LED-sida ved kanten',
     6.0, (0.95, 0.85, 0.55), lambda: skive(LED_R, RING_Z0 - 2.0 - KJOL_T - LED_T, LED_T)),
    ('E02', 'Potensiometer med brytar', 'WH148 16 mm med brytar, B10K eller det dimmaren krev, M7 × 0,75-hals 7 mm '
     '(6,6–7,4: knotten stoppar mot enden av halsen), riflet aksel Ø 6 kappa til 15 mm frå monteringsflata '
     '(8 mm over halsen), låsetapp', 9.0, (0.30, 0.30, 0.32), potmeter),
    ('E02b', 'Mutter og skive M7', 'følgjer potensiometeret', 1.5, (0.70, 0.70, 0.70), mutter_m7),
    ('E03', 'PWM-dimmarkort', 'verkar frå 4,5 V (prøv ved 4,75 V), PWM ≥ 3 kHz, ≥ 1 A, potensiometeret lodda på kortet '
     '(nominelt 34 × 21 mm)', 6.0, (0.10, 0.35, 0.15), dimmarkort),
    ('E04', 'USB-C-kontakt', 'USB-C hokontakt for panel, 2 pinnar, med innebygde 5,1 kΩ på CC1 og CC2 kvar for seg',
     2.0, (0.15, 0.15, 0.15), usb_c),
]


def bygg():
    t0 = time.time()
    delar = {}
    for pid, namn, mat, rho, farge, fn, fyll in DELAR:
        delar[pid] = dict(id=pid, namn=namn, materiale=mat, rho=rho, farge=farge, form=fn(), fyll=fyll, kjopt=False)
        print(f'  {pid} {namn:<12} {time.time() - t0:6.1f} s', flush=True)
    for pid, namn, spes, masse, farge, fn in KJOPT:
        delar[pid] = dict(id=pid, namn=namn, materiale=spes, masse=masse, farge=farge, form=fn(), kjopt=True)
    for samling, masse, farge, namn in ((skruar(), None, (0.12, 0.12, 0.13), 'Skrue'),
                                        (magnetar(), 0.65, (0.78, 0.78, 0.80), 'Magnet Ø 6 × 3 N42'),
                                        (gummifoter(), 0.2, (0.05, 0.05, 0.05), 'Gummifot Ø 10 × 2')):
        for pid, form in samling.items():
            m = masse if masse is not None else round(form.Volume() * 7.9e-3, 2)
            delar[pid] = dict(id=pid, namn=namn, materiale='', masse=m, farge=farge, form=form, kjopt=True)
    return delar


# ======================================================================== kontroll


def masse(d):
    if d['kjopt']:
        return d['masse']
    s, rho = d['form'], d['rho'] * 1e-3
    if d['fyll'] == 'infill':                                # 5 vegger (2,1 mm) + 20 % gyroid inni, som plate 1
        skal = min(s.Volume(), s.Area() * 2.1)
        return rho * (skal + 0.20 * (s.Volume() - skal))
    return rho * s.Volume()


def kontroll(delar):
    ut = {'dato': time.strftime('%Y-%m-%d %H:%M'), 'delar': {}, 'kollisjonar': [], 'innføring': {}}
    for pid, d in delar.items():
        s = d['form']
        bb = s.BoundingBox()
        ut['delar'][pid] = dict(namn=d['namn'], gyldig=bool(s.isValid()), volum_mm3=round(s.Volume(), 1),
                                masse_g=round(masse(d), 1),
                                boks_mm=[round(bb.xmin, 2), round(bb.ymin, 2), round(bb.zmin, 2),
                                         round(bb.xmax, 2), round(bb.ymax, 2), round(bb.zmax, 2)])
    # kollisjonar: alle par, filtrert på boks
    ids = list(delar)
    for a, b in combinations(ids, 2):
        ba, bb_ = delar[a]['form'].BoundingBox(), delar[b]['form'].BoundingBox()
        if ba.xmax < bb_.xmin or bb_.xmax < ba.xmin or ba.ymax < bb_.ymin or bb_.ymax < ba.ymin or ba.zmax < bb_.zmin or bb_.zmax < ba.zmin:
            continue
        v = delar[a]['form'].intersect(delar[b]['form']).Volume()
        if v > 0.01:
            ut['kollisjonar'].append(dict(a=a, b=b, volum_mm3=round(v, 3)))
    # tyngdepunkt og velting, med botnplata i stål og i PLA
    xs = [x for x, _ in FOTER]
    stod = dict(venstre=min(xs) - FOT_R_GUMMI, hogre=max(xs) + FOT_R_GUMMI,
                framme=-min(abs(y) for _, y in FOTER) - FOT_R_GUMMI, bak=min(abs(y) for _, y in FOTER) + FOT_R_GUMMI)

    def vipp(bytt):
        mass = {pid: bytt.get(pid, masse(d)) for pid, d in delar.items()}
        M = sum(mass.values())
        c = V(0, 0, 0)
        for pid, d in delar.items():
            c = c + d['form'].Center() * mass[pid]
        c = c * (1.0 / M)
        vinklar = dict(mot_hovudet=math.degrees(math.atan2(stod['hogre'] - c.x, c.z)),
                       mot_bladet=math.degrees(math.atan2(c.x - stod['venstre'], c.z)),
                       framover=math.degrees(math.atan2(c.y - stod['framme'], c.z)),
                       bakover=math.degrees(math.atan2(stod['bak'] - c.y, c.z)))
        return M, c, vinklar

    M, c, vinklar = vipp({})
    ut['masse_g'] = round(M, 1)
    ut['tyngdepunkt_mm'] = [round(c.x, 1), round(c.y, 1), round(c.z, 1)]
    ut['velting'] = dict(stottekant_mm=stod, vinkel_grad={k: round(v, 1) for k, v in vinklar.items()},
                         minste_grad=round(min(vinklar.values()), 1), krav_EN60598_grad=6.0,
                         merknad='Statisk vippevinkel om ytterkanten av gummiføtene. Kabelen er ikkje med.')
    Mp, cp, vp = vipp({'D04': delar['D04']['form'].Volume() * 1.24e-3})
    ut['velting_pla_botnplate'] = dict(masse_g=round(Mp, 1), tyngdepunkt_mm=[round(cp.x, 1), round(cp.y, 1), round(cp.z, 1)],
                                       vinkel_grad={k: round(v, 1) for k, v in vp.items()}, minste_grad=round(min(vp.values()), 1))
    # innføring, prøvd i steg på 1 mm
    def sveip(namn, flytt, tre, steg, folgjer=()):
        verste = 0.0
        for i in range(1, steg + 1):
            f = delar[flytt]['form'].translate(V(*[k * i for k in tre]))
            for andre in delar:
                if andre == flytt or andre.startswith(folgjer):
                    continue                                 # delar som følgjer med eller er tekne ut først
                bf, bo = f.BoundingBox(), delar[andre]['form'].BoundingBox()
                if bf.xmax < bo.xmin or bo.xmax < bf.xmin or bf.ymax < bo.ymin or bo.ymax < bf.ymin or bf.zmax < bo.zmin or bo.zmax < bf.zmin:
                    continue
                verste = max(verste, f.intersect(delar[andre]['form']).Volume())
        ut['innføring'][namn] = dict(retning=tre, steg_mm=1.0, tal_steg=steg, storste_overlapp_mm3=round(verste, 3),
                                     metode='diskret')
    sveip('lyskopp', 'D06', (0, 0, -1.0), 25, ('M06', 'D07', 'D08', 'E01'))
    sveip('hovud_paa_bladet', 'D02', (1.0, 0, 0), 6, ('M06', 'M04', 'D06', 'D07', 'D08', 'E01'))
    sveip('knott', 'D05', (0, 0, 1.0), 12)
    sveip('botnplate', 'D04', (0, 0, -1.0), 8, ('M05', 'M07'))
    verste = 0.0                                             # USB-C: 2,4 mm attende, opp frå undersida, så ut i lomma
    for dz in range(-20, 1):
        verste = max(verste, delar['E04']['form'].translate(V(0, -2.4, dz)).intersect(delar['D03']['form']).Volume())
    for i in range(13):
        verste = max(verste, delar['E04']['form'].translate(V(0, -2.4 + 0.2 * i, 0)).intersect(delar['D03']['form']).Volume())
    ut['innføring']['usb_c'] = dict(veg='2,4 mm attende, 20 mm opp, så 2,4 mm ut i lomma', steg_mm=[1.0, 0.2],
                                    storste_overlapp_mm3=round(verste, 3), metode='diskret')
    return ut


# ======================================================================== eksport


def filnamn(pid, namn):
    t = namn.lower()
    for a, b in (('ø', 'o'), ('å', 'aa'), ('æ', 'ae'), ('×', 'x'), (' ', '_'), (',', '')):
        t = t.replace(a, b)
    return f"{pid}_{''.join(c for c in t if c.isascii() and (c.isalnum() or c in '_-'))}"


def skriv_step(delar):
    (ROT / 'cad').mkdir(exist_ok=True)
    assy = cq.Assembly(name='Lut')
    for pid, d in delar.items():
        if not d['kjopt']:
            cq.exporters.export(cq.Workplane().add(d['form']), str(ROT / 'cad' / f"{filnamn(pid, d['namn'])}.step"))
        assy.add(d['form'], name=filnamn(pid, d['namn']), color=cq.Color(*d['farge']))
    assy.save(str(ROT / 'cad' / 'lut_samanstilling.step'))


def skriv_stl(delar, mappe, alle=False):
    """Éin STL per del i monteringsposisjon. Utan «alle» berre første eksemplar av like skruar, magnetar og føter.
    Kvar fil blir lesen inn att og sjekka for tett nett; er ho ikkje tett, blir ho skriven på nytt med finare netting."""
    import trimesh
    mappe.mkdir(parents=True, exist_ok=True)
    tett = {}
    for pid, d in delar.items():
        if not alle and pid.startswith('M0') and pid[-1] != '1':
            continue
        sti = mappe / f"{filnamn(pid, d['namn'])}.stl"
        reparert = 0
        for tol, ang in ((0.01, 0.08), (0.005, 0.05)):
            d['form'].exportStl(str(sti), tolerance=tol, angularTolerance=ang, relative=False)
            m = trimesh.load(str(sti), force='mesh')
            if m.is_watertight:
                break
        if not m.is_watertight:                              # trekantar med null areal der tre avrundingar møtest i eit hjørne
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
    # rotasjonar til printplata; omsetjast etter rotasjonen så delen står på z = 0
    'D01': ('x', 90.0),       # liggjande: framsida (Y = -20) ned mot plata
    'D02': ('x', 180.0),      # opp-ned: toppen ned
    'D03': ('x', 180.0),      # opp-ned: toppen ned
    'D05': ('x', 180.0),
    'D06': ('x', 180.0),      # toppplata ned
    'D04p': ('x', 0.0),
}


def i_printretning(form, pid):
    akse, grad = PRINTRETNING[pid]
    f = form.rotate(V(0, 0, 0), V(1, 0, 0) if akse == 'x' else V(0, 1, 0), grad)
    bb = f.BoundingBox()
    return f.translate(V(-bb.xmin, -bb.ymin, -bb.zmin))


def skriv_3mf(sti, plate, tittel):
    """Plate: liste av (namn, form i printretning, (x, y) for hjørnet nede til venstre på plata)."""
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
              f'<metadata name="Title">{tittel}</metadata><metadata name="Designer">GK5 konsept D Lut</metadata>'
              f'<resources>{"".join(obj)}</resources><build>{"".join(items)}</build></model>')
    with zipfile.ZipFile(sti, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model', modell)


def printplater(delar):
    mappe = ROT / 'print'
    mappe.mkdir(exist_ok=True)
    pr = {pid: i_printretning(delar[pid]['form'], pid) for pid in ('D01', 'D02', 'D03', 'D05', 'D06')}
    pr['D04p'] = i_printretning(delar['D04']['form'], 'D04p')
    info = {}
    for pid, f in pr.items():
        bb = f.BoundingBox()
        info[pid] = dict(storleik_mm=[round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)],
                         passar_P1S=bool(bb.xlen <= 250 and bb.ylen <= 250 and bb.zlen <= 250))
    b1, b2 = pr['D01'].BoundingBox(), pr['D03'].BoundingBox()
    plater = {
        'LUT_P1S_plate1_blad_PLA.3mf': [('D01 Blad', pr['D01'], ((256 - b1.xlen) / 2, (256 - b1.ylen) / 2))],
        'LUT_P1S_plate2_fot_hovud_knott_PLA.3mf': [
            ('D03 Fot', pr['D03'], ((256 - b2.xlen) / 2, 18.0)),
            ('D02 Hovud', pr['D02'], (40.0, 18.0 + b2.ylen + 20.0)),
            ('D05 Knott', pr['D05'], (150.0, 18.0 + b2.ylen + 50.0))],
        'LUT_P1S_plate3_lyskopp_PETG_kvit.3mf': [('D06 Lyskopp', pr['D06'], (88.0, 88.0))],
        'LUT_P1S_plate4_botnplate_PLA_alternativ.3mf': [('D04 Botnplate (PLA)', pr['D04p'], ((256 - b2.xlen) / 2, 88.0))],
    }
    for namn, pp, tittel in (('LUT_P1S_plate0a_passprove_blad_PLA.3mf', passprove_blad(), 'P00a Passprøve blad'),
                             ('LUT_P1S_plate0b_passprove_hovud_fot_PLA.3mf', passprove_hovud_fot(), 'P00b Passprøve hovud og fot')):
        bp = pp.BoundingBox()
        pp = pp.translate(V(-bp.xmin, -bp.ymin, -bp.zmin))
        plater[namn] = [(tittel, pp, ((256 - bp.xlen) / 2, (256 - bp.ylen) / 2))]
    plater['LUT_P1S_plate5_hovud_PETG_alternativ.3mf'] = [('D02 Hovud (PETG)', pr['D02'], (88.0, 88.0))]
    for namn, innhald in plater.items():
        skriv_3mf(mappe / namn, innhald, namn[:-4])
    return info


def skriv_dxf(delar):
    """DXF i 1:1: botnplata for laserskjering (kontur og hol, merknad om senking), spreiaren og kjøleplata som mal."""
    import ezdxf
    ut = ROT / 'produksjon'
    f = d_flate(VEGG - FALS + PLATE_KLARING, 0.0)
    w = cq.Workplane('XY').add(f)
    for x, y in PLATE_SKRUAR:
        w = w.add(Wire.makeCircle(PLATE_HOL_R, V(x, y, 0), V(0, 0, 1)))
    sti = ut / 'D04_botnplate_4mm_S235_1til1.dxf'
    cq.exporters.export(w, str(sti), exportType='DXF')
    doc = ezdxf.readfile(str(sti))
    doc.layers.add('MERKNAD')
    doc.modelspace().add_text(f'D04 Lut · S235 4 mm · 4 hol Ø {2 * PLATE_HOL_R:.1f} · senk 90° til Ø {PLATE_SENK_D:.1f} '
                              f'frå undersida (ISO 10642 M3)', dxfattribs={'height': 3.0, 'layer': 'MERKNAD'}).set_placement((0, -50))
    doc.saveas(str(sti))
    for namn, r, ri in (('D07_spreiar_1til1.dxf', SPREIAR_R, 0.0), ('D08_kjoleplate_1til1.dxf', KJOL_R, 3.0)):
        w = cq.Workplane('XY').add(Wire.makeCircle(r, V(0, 0, 0), V(0, 0, 1)))
        if ri:
            w = w.add(Wire.makeCircle(ri, V(0, 0, 0), V(0, 0, 1)))
        cq.exporters.export(w, str(ut / namn), exportType='DXF')


def skriv_stykkliste(delar, k):
    rader = [('ID', 'Namn', 'Tal', 'Materiale / spesifikasjon', 'Masse g', 'Kjelde')]
    kjelde = {'D04': 'laserskjering frå DXF (stål) eller print plate 4 (PLA)', 'D07': 'skjer ut etter DXF-mal',
              'D08': 'skjer ut etter DXF-mal'}
    for pid, namn, mat, *_ in DELAR:
        rader.append((pid, namn, 1, mat, k['delar'][pid]['masse_g'], kjelde.get(pid, 'print')))
    for pid, namn, spes, m, *_ in KJOPT:
        rader.append((pid, namn, 1, spes, m, 'kjøp'))
    rader += [
        ('E05', 'Kabel til LED', 1, '2 × 0,25 mm² silikon, 650 mm (blad 260, hovud med 80 mm serviceslakk 155, fot 165, '
         'avisolering og reserve 70); kapp til slutt', 6.0, 'kjøp'),
        ('E06', 'Leidning i foten', 2, '0,25 mm² silikon raud og svart, 120 mm kvar (USB-C til brytar til dimmar)', 2.0, 'kjøp'),
        ('M01', 'Innpressmutter M4', 3, 'messing M4 × 8,1 (lengd ≤ 8,1), for hol Ø 5,6 × 9 i rota av bladet', 1.0, 'kjøp'),
        ('M02', 'Innpressmutter M3', 6, 'messing M3 × 5,7, for hol Ø 4,0 × 7 (2 i enden av bladet, 4 i foten)', 0.5, 'kjøp'),
        ('M03', 'Skrue M4 × 16', 3, 'ISO 4762 sylinderhovud, frå innsida av foten opp i bladet; handstramt, om lag 1 N·m',
         3.0, 'kjøp'),
        ('M04', 'Skrue M3 × 10', 2, 'ISO 4762 sylinderhovud, frå innsida av hovudet inn i bladet', 1.2, 'kjøp'),
        ('M05', 'Skrue M3 × 8', 4, 'ISO 10642 senkskrue, botnplata (hovudet i plan med plata)', 0.9, 'kjøp'),
        ('M06', 'Magnet Ø 6 × 3', 6, 'NdFeB N42, limast med epoksy (3 i hovudet, 3 i lyskoppen, motsett pol)', 0.65, 'kjøp'),
        ('M07', 'Gummifot Ø 10 × 2', 4, 'sjølvklebande', 0.2, 'kjøp'),
        ('M08', 'Termisk teip', 2, 'dobbeltsidig, Ø 50 × 0,25 mm: éin mellom kjøleplata og taket i koppen, éin mellom '
         'LED-kortet og kjøleplata', 0.5, 'kjøp'),
        ('M09', 'Kaptonteip', 1, '60 × 40 mm, på oversida av botnplata under dimmarkortet', 0.3, 'kjøp'),
    ]
    with open(ROT / 'kontroll' / 'lut_stykkliste.csv', 'w', newline='', encoding='utf-8-sig') as f:
        csv.writer(f, delimiter=';').writerows(rader)


def main():
    t0 = time.time()
    print('Byggjer delane', flush=True)
    delar = bygg()
    print(f'Kontrollerer ({time.time() - t0:.0f} s)', flush=True)
    k = kontroll(delar)
    g = blad_geometri()
    _, kanal_pkt = kanal()
    k['geometri'] = {n: [round(v, 3) for v in p] for n, p in g.items()}
    k['kanal'] = {n: [round(v, 3) for v in p] for n, p in kanal_pkt.items()}
    k['parametrar'] = {n: v for n, v in globals().items() if n.isupper() and isinstance(v, (int, float, tuple))}
    if not RASK:
        print(f'Eksporterer ({time.time() - t0:.0f} s)', flush=True)
        skriv_step(delar)
        k['stl_tett'] = skriv_stl(delar, ROT / 'produksjon')
        skriv_stl(delar, ROT / 'render' / 'nett', alle=True)          # til Blender; ikkje i git
        k['passprove'] = {}
        for namn, pp in (('P00a_passprove_blad', passprove_blad()), ('P00b_passprove_hovud_fot', passprove_hovud_fot())):
            k['passprove'][namn] = dict(gyldig=bool(pp.isValid()), volum_mm3=round(pp.Volume(), 1))
            pp.exportStl(str(ROT / 'produksjon' / f'{namn}.stl'), tolerance=0.01, angularTolerance=0.08, relative=False)
        k['print'] = printplater(delar)
        skriv_dxf(delar)
        skriv_stykkliste(delar, k)
        json.dump({pid: dict(namn=d['namn'], farge=d['farge'], kjopt=d['kjopt'], fil=filnamn(pid, d['namn']),
                             senter=[round(c, 3) for c in d['form'].Center().toTuple()]) for pid, d in delar.items()},
                  open(ROT / 'kontroll' / 'lut_delar.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        (ROT / 'kontroll').mkdir(exist_ok=True)
        json.dump(k, open(ROT / 'kontroll' / 'lut_kontroll.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ugyldige = [p for p, d in k['delar'].items() if not d['gyldig']]
    print(json.dumps(dict(masse_g=k['masse_g'], tyngdepunkt=k['tyngdepunkt_mm'], velting=k['velting']['vinkel_grad'],
                          kollisjonar=k['kollisjonar'], ugyldige=ugyldige, innføring=k['innføring'],
                          print=k.get('print')), ensure_ascii=False, indent=1))
    print(f'Ferdig på {time.time() - t0:.0f} s')


if __name__ == '__main__':
    main()
