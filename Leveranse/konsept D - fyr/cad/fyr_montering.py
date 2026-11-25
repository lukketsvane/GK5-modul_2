# -*- coding: utf-8 -*-
"""FYR · monterings- og servicerettleiing (IKEA-stil) rett frå CAD-modellen.

Køyr frå mappa «konsept D - fyr» (eller kvar som helst, stiane er faste):
    py -3 cad/fyr_montering.py              # alle sider
    py -3 cad/fyr_montering.py --utan-cache # rekn alle projeksjonar på nytt

Skriv til montering/:
    FYR_montering.pdf      A4 ståande, vektor (cairosvg) og samla med pypdf
    side-NN-<namn>.png     kvar side i 150 dpi
    scener.json            per steg: synlege delar, transformasjonar, innføringsvektor/rotasjon, kamera

Alle figurar er HLR-strekteikningar (OCP HLRBRep, skjulte kantar fjerna) av delane i fyr_geometri.py.
Beslag og verktøy (innsatsar, skruar, kabel, loddebolt, nøklar) er modellerte her etter standardmål.
Projeksjonane blir mellomlagra i %TEMP%/fyr_montering_cache, nøkla på kjeldeteksten til geometrien,
beslagsmodellane her og scenen, så ei ny køyring etter ei geometriendring berre reknar om det som er endra.
"""
from __future__ import annotations

import hashlib
import html
import inspect
import io
import json
import math
import os
import pickle
import re
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepLib import BRepLib
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.gp import gp_Ax2, gp_Ax3, gp_Dir, gp_Pnt, gp_Pnt2d, gp_Trsf, gp_Vec
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS

HER = Path(__file__).resolve().parent
ROT = HER.parent
UT = ROT / "montering"
sys.path.insert(0, str(HER))
import fyr_geometri as g  # noqa: E402

REVISJON = g.REVISJON
DATO = g.DATO
SIDER = UT / "sider"
CACHE = Path(tempfile.gettempdir()) / "fyr_montering_cache"
DEG = math.pi / 180.0
A4W, A4H = 210.0, 297.0

# kamera: retning MOT betraktaren. Sett framme til venstre, litt ovanfrå: spaltene (+X) til venstre for midten.
ISO = (1.35, 1.0, 0.85)
BAK = (-1.35, -1.0, 0.85)
# strekvekter (mm på arket): ny del tjukk, kontekst tynn
W_NY_O, W_NY_S, W_KT_O, W_KT_S, W_FIN = 0.62, 0.34, 0.34, 0.17, 0.17


def vinkel_skjerm(N):
    return math.degrees(math.atan2(N[1], N[0]))


V_ISO = vinkel_skjerm(ISO)


def fmt(x, d=2):
    """Tal med desimalkomma, utan unødvendige nullar."""
    s = f"{x:.{d}f}".rstrip("0").rstrip(".")
    return s.replace(".", ",").replace("-", "−")


def polar3(r, a, z):
    return (r * math.cos(a * DEG), r * math.sin(a * DEG), z)


def norm(v):
    L = math.sqrt(sum(c * c for c in v))
    return tuple(c / L for c in v)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def mul(a, k):
    return tuple(x * k for x in a)


def shape_of(wp):
    if isinstance(wp, cq.Shape):
        return wp
    vals = wp.vals()
    return vals[0] if len(vals) == 1 else cq.Compound.makeCompound(vals)


# =============================================================================== beslag og verktøy
def plasser(s: cq.Shape, tupp, zdir, xdir) -> cq.Shape:
    """Flytt ei form bygd langs +Z (tupp i origo) slik at +Z peikar langs zdir og +X langs xdir."""
    zd = norm(zdir)
    xd = norm(xdir)
    xd = norm(cross(cross(zd, xd), zd))  # gjer vinkelrett
    t = gp_Trsf()
    t.SetTransformation(gp_Ax3(gp_Pnt(*tupp), gp_Dir(*zd), gp_Dir(*xd)), gp_Ax3())
    return s.moved(cq.Location(t))


def hw_innsats(p, a):
    """Innpressmutter M3 x 5,7 (ytre Ø = hol + 0,6), to riller."""
    x, y, _ = polar3(p.skrue_r, a, 0)
    z0 = p.z_fot_1
    L = p.innsats_l
    D = p.innsats_hol_d + 0.6
    s = g.ring(D / 2, 1.5, z0, z0 + L)
    for zz in (1.5, 3.4):
        s = s.cut(g.ring(D / 2 + 1, D / 2 - 0.3, z0 + zz, z0 + zz + 0.7))
    return shape_of(s.translate((x, y, 0)))


def knappskrue(L, k=1.65, dk=5.7, s_hex=2.0, d=3.0):
    """ISO 7380 M3 (eller M2 med d = 2) i eige system: lageflata i z = 0, hovudet ned (z < 0), skaftet opp."""
    prof = (cq.Workplane("XZ").moveTo(0, 0).lineTo(dk / 2, 0).lineTo(dk / 2, -0.3 * k / 1.65 - 0.15)
            .threePointArc((dk / 2 * 0.62, -k * 0.86), (0, -k)).close().revolve(360, (0, 0, 0), (0, 1, 0)))
    hx = cq.Workplane("XY").workplane(offset=-k - 0.1).polygon(6, s_hex / math.cos(30 * DEG)).extrude(k * 0.7)
    skaft = g.syl(d / 2, -0.01, L)
    return shape_of(prof.cut(hx).union(skaft))


def panskrue(L, d=2.0, dk=4.0, k=1.6):
    """ISO 7045 (linsehovud, krysspor) i eige system: lageflata i z = 0, hovudet ned (z < 0), skaftet opp."""
    prof = (cq.Workplane("XZ").moveTo(0, 0).lineTo(dk / 2, 0).lineTo(dk / 2, -k * 0.45)
            .threePointArc((dk / 2 * 0.62, -k * 0.9), (0, -k)).close().revolve(360, (0, 0, 0), (0, 1, 0)))
    for vri in (0, 90):
        spor = cq.Solid.makeBox(dk * 0.62, 0.55, 1.0, cq.Vector(-dk * 0.31, -0.275, -k - 0.2))
        prof = prof.cut(spor.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), vri))
    return shape_of(prof.union(g.syl(d / 2, -0.01, L)))


def m2_mutter(skive=True):
    """ISO 4032 M2-mutter (NV 4, h 1,6), med ISO 7089-skive (Ø5 x 0,3) under: frå z = 0 og opp."""
    hx = cq.Workplane("XY").polygon(6, 4.0 / math.cos(30 * DEG)).extrude(1.6).faces(">Z").workplane().hole(2.0)
    if not skive:
        return shape_of(hx)
    return shape_of(g.ring(2.5, 1.1, 0.0, 0.3).union(hx.translate((0, 0, 0.3))))


def hw_m2_sett(L, skive=True):
    """Skrue, (skive) og mutter på line langs skaftet, for ikonet J."""
    m = m2_mutter(skive).translate(cq.Vector(0, 0, L + 2.5))
    return cq.Compound.makeCompound([panskrue(L), m])


def hw_brytarfeste(p, i, j, kva, L=10.0):
    """Feste J for brytar i, hol j: M2 x 10 utanfrå gjennom brytaren og braketten, skive og mutter innanfor.
    Lokal brytarramme som sw_lokal i geometrien: x radielt ut, y tangentielt, kroppen x ±2,9, braketten x −4,7..−2,95."""
    a = p.sw[i][0] * DEG
    ca, sa = math.cos(a), math.sin(a)
    y_h = (-6.85, -0.35)[j]
    w = lambda x: (p.sw_r * ca + x * ca - y_h * sa, p.sw_r * sa + x * sa + y_h * ca, p.sw_hol_z)
    inn = (-ca, -sa, 0.0)
    if kva == "skrue":
        return plasser(panskrue(L), w(2.9), inn, (0, 0, 1))
    return plasser(m2_mutter(), w(-4.7), inn, (0, 0, 1))


def hw_skrujarn(tupp, akse, xdir=(1, 0, 0), L=118.0):
    """Skrujarn PH0 (krysspor for ISO 7045 M2): spissen i tupp, skaftet langs akse."""
    s = (cq.Workplane("XZ").polyline([(0, 0), (0.9, 0), (1.5, 3.0), (1.5, 52), (3.2, 54), (6.5, 58), (7.2, 64),
                                      (7.2, L - 8), (5.5, L), (0, L)]).close().revolve(360, (0, 0, 0), (0, 1, 0)))
    for zz in (70.0, 80.0, 90.0, 100.0):
        s = s.cut(g.ring(9, 6.6, zz, zz + 3.0))
    return plasser(shape_of(s), tupp, akse, xdir)


def hw_multimeter(probar=True):
    """Multimeter liggjande flatt (display, vreidar, tre kontaktar), med to målepinnar ved sida."""
    kropp = cq.Workplane("XY").rect(40, 72).extrude(14).edges("|Z").fillet(4.0)
    kropp = kropp.cut(cq.Workplane("XY").workplane(offset=13).center(0, 18).rect(30, 17).extrude(2))
    kropp = kropp.union(cq.Workplane("XY").workplane(offset=14).center(0, -6).circle(9.5).extrude(2.0))
    kropp = kropp.union(cq.Workplane("XY").workplane(offset=16).center(0, -6).rect(3.0, 15.0).extrude(2.0))
    for xx in (-11.0, 0.0, 11.0):
        kropp = kropp.cut(cq.Workplane("XY").workplane(offset=11).center(xx, -27).circle(2.2).extrude(4))
    delar = [shape_of(kropp)]
    if probar:
        for xx in (29.0, 37.0):
            h = cq.Solid.makeCylinder(2.6, 46.0, cq.Vector(xx, 30, 2.6), cq.Vector(0, -1, 0))
            spiss = cq.Solid.makeCone(0.9, 0.2, 16.0, cq.Vector(xx, -16, 2.6), cq.Vector(0, -1, 0))
            delar += [h, spiss]
    return cq.Compound.makeCompound(delar)


def hw_snorbit():
    """Éin bit silikonsnor Ø2 x 10 (11b), liggjande langs X, for ikonet."""
    return cq.Solid.makeCylinder(1.0, 10.0, cq.Vector(-5, 0, 0), cq.Vector(1, 0, 0))


def hw_fastnokkel(tupp, xdir, aapning=8.0, L=82.0, t=3.2):
    """Fastnøkkel (open ende) med kjeften rundt tupp, skaftet langs xdir, flat i XY-planet."""
    hr = aapning * 0.95 + 1.6
    hovud = cq.Workplane("XY").circle(hr).extrude(t)
    skaft = cq.Workplane("XY").center(L / 2 + hr * 0.4, 0).rect(L, aapning * 0.85).extrude(t)
    ende = cq.Workplane("XY").center(L + hr * 0.4, 0).circle(aapning * 0.62).extrude(t)
    s = hovud.union(skaft).union(ende)
    s = s.cut(cq.Workplane("XY").center(-hr, 0).rect(2 * hr, aapning).extrude(t))      # kjeften
    s = s.cut(cq.Workplane("XY").circle(aapning / 2).extrude(t))
    s = shape_of(s).translate(cq.Vector(0, 0, -t / 2))
    return plasser(s, tupp, (0, 0, 1), xdir)


def hw_jack_del(p, kva):
    """TRS-kontakten (13) delt i kropp med bøssing (opp nedanfrå) og M6-mutteren (oppå navet)."""
    j = shape_of(g.jack(p))
    zd1 = p.dekk_z + p.dekk_t
    kutt = cq.Solid.makeBox(60, 60, 30, cq.Vector(-30, -30, zd1))
    return j.cut(kutt) if kva == "kropp" else j.intersect(kutt)


def hw_skrue_a(p, a, L=16.0):
    x, y, _ = polar3(p.skrue_r, a, 0)
    zc = p.z_fot_0 + 2.2  # botnen av forsenkinga
    return knappskrue(L).translate(cq.Vector(x, y, zc))


def hw_loddebolt(tupp, akse, xdir=(1, 0, 0)):
    s = (cq.Workplane("XZ").polyline([(0, 0), (0.7, 0), (2.4, 9), (2.4, 42), (4.5, 44), (4.5, 50), (8.5, 54),
                                      (9.0, 120), (7.0, 128), (0, 128)]).close().revolve(360, (0, 0, 0), (0, 1, 0)))
    for zz in (70, 84, 98):
        s = s.cut(g.ring(10, 8.4, zz, zz + 2.5))
    return plasser(shape_of(s), tupp, akse, xdir)


def hw_nokkel(d, tupp, akse, armdir, kort=13.0, lang=48.0):
    """L-forma sekskantnøkkel: kort arm langs +Z frå tuppen, lang arm langs +X."""
    e = d / math.cos(30 * DEG)
    kortarm = cq.Workplane("XY").polygon(6, e).extrude(kort)
    langarm = cq.Workplane("YZ").workplane(offset=-d / 2).center(0, kort - d / 2).polygon(6, e).extrude(lang)
    return plasser(shape_of(kortarm.union(langarm)), tupp, akse, armdir)


KABEL_R = 2.0      # kabelen Ø4 (holet bak er Ø4,2)
LEIAR_R = 0.75     # dei to leiarane etter kappa, teikna som éin bunt


def kabel_info(p):
    """Strekkavlastinga slik geometrien har ho: stolpane P1, P2, P3 i lomma i foten og holet i chassisflensen."""
    return {"stolpar_P1_P2_P3": [list(q) for q in p.stolpe_pos], "stolpe_d": 3.0, "stolpe_topp_z": p.stolpe_topp,
            "hol_flens": [p.kabel_ut_x, 0.0, 3.5],
            "inn": "radielt hol bak (asimut 180), z = kabel_z", "kabel_z": p.kabel_z, "lomme_r": p.fot_lomme_r,
            "lomme_golv_z": p.fot_lomme_z, "bane": "under P1, over P2, under P3 (S); kappa sluttar etter P3"}


def kabelbane(p, ut=38.0):
    """Midtlina til kabelkappa: inn langs -X bak, S rundt stolpane (under P1, over P2, under P3 sett ovanfrå med +Y opp)."""
    R = p.fot_d / 2
    kz = p.kabel_z
    (ax, ay), (bx, by), (cx, cy) = p.stolpe_pos
    off = 1.5 + KABEL_R + 0.05
    return [(-R - ut, 0, kz), (-R + 1.0, 0, kz), (-p.fot_lomme_r + 1.0, 0, kz),
            (ax, ay - off, kz), (bx, by + off, kz), (cx, cy - off, kz), (cx + 2.6, cy - off + 0.5, kz)]


def leiarbane(p, loft=0.0):
    """Leiarane frå enden av kappa, opp gjennom holet i chassisflensen, rundt armen bak og fram til JST-pluggen på kortet."""
    (cx, cy), = p.stolpe_pos[2:]
    off = 1.5 + KABEL_R + 0.05
    hx = p.kabel_ut_x
    zd0, zd1 = p.dekk_z + loft, p.dekk_z + p.dekk_t + loft
    return [(cx + 2.6, cy - off + 0.5, p.kabel_z), (hx, 0.0, p.kabel_z + 2.5), (hx, 0.0, p.z_fot_1 + loft + 6.0),
            (hx, 0.0, zd0 - 7.0), (hx, 11.5, zd0 - 2.0), (hx, 11.5, zd1 + 3.4), (hx - 1.2, 6.0, zd1 + 3.4)]


def roeyr_delar(bane, r):
    delar = []
    for a, b in zip(bane[:-1], bane[1:]):
        v = tuple(bb - aa for aa, bb in zip(a, b))
        L = math.sqrt(sum(c * c for c in v))
        if L < 1e-6:
            continue
        delar.append(cq.Solid.makeCylinder(r, L, cq.Vector(*a), cq.Vector(*v)))
    for q in bane[1:-1]:
        delar.append(cq.Solid.makeSphere(r, cq.Vector(*q), angleDegrees1=-90, angleDegrees2=90))
    return delar


def roeyr(pts, r, glatt=True):
    """Røyr av sylindrar og kuler langs ein samplad spline: analytiske flater gjer HLR rask
    (ein B-spline-sveip tok over 10 s eller hekk seg i HLR). Fusen er skjør i krappe bøyar: prøv fleire
    samplingsavstandar og bruk den første gyldige; elles ein compound utan fuse."""
    banar = [pts]
    if glatt:
        t0 = norm(tuple(b - a for a, b in zip(pts[0], pts[1])))
        t1 = norm(tuple(b - a for a, b in zip(pts[-2], pts[-1])))
        try:
            e = cq.Edge.makeSpline([cq.Vector(*q) for q in pts], tangents=[cq.Vector(*t0), cq.Vector(*t1)])
            banar = []
            for steg in (4.0, 3.5, 4.5, 3.0, 5.0, 2.5):
                n = max(8, int(e.Length() / steg))
                banar.append([pts[0]] + [tuple(e.positionAt(i / n)) for i in range(1, n)] + [pts[-1]])
        except Exception:  # noqa: BLE001
            banar = [pts]
    for bane in banar:
        d = roeyr_delar(bane, r)
        try:
            s = d[0].fuse(*d[1:]).clean()
            if s.isValid() and len(s.Solids()) == 1:
                return s
        except Exception:  # noqa: BLE001
            pass
    return cq.Compound.makeCompound(roeyr_delar(banar[0], r))


def hw_kabel(p, loft=0.0, ut=38.0):
    """Kabel F: kappe Ø4 gjennom strekkavlastinga, leiarbunt opp til kortet, JST-plugg."""
    kappe = roeyr(kabelbane(p, ut), KABEL_R)
    lb = leiarbane(p, loft)
    leiar = roeyr(lb, LEIAR_R)
    ex, ey, ez = lb[-1]
    plugg = cq.Solid.makeBox(3.4, 5.0, 3.0, cq.Vector(ex - 3.4 + 0.3, ey - 2.5, ez - 1.5))
    return cq.Compound.makeCompound([kappe, leiar, plugg])


LEIAR28_R = 0.35                          # AWG 28 med isolasjon, Ø0,7
# Leiarane i lysmodulen (E12): (funksjon, farge, stripe). Kvar stripe har pluss og GND, så den svarte
# leiaren er kappa i to bitar, éin frå kvar stripe; båe blir lodda til hylsa på pluggen.
MLEIARAR = (("TOPP+", "raud", "06c"), ("SIDE+", "blå", "06b"), ("GND", "svart", "06b"), ("GND", "svart", "06c"))
LODD_XY = ((1.1, 0.0), (-1.3, 1.5), (-1.1, -2.0), (-1.2, -0.95))     # loddeøyra: tupp, ring, hylse, hylse


def leiar_loddepunkt(p, j, ep=0.0):
    """Loddeøyret for leiar j (sjå MLEIARAR) på toppen av pluggkroppen, plugga senka ep."""
    lx, ly = LODD_XY[j]
    return (lx, ly, p.mastfot_z0 + p.trs_kropp_l - ep)


def mleiar_bane(p, j):
    """Leiar j i lysmodulen i montert stilling, som liste av (lekam, punkt). Lekamen seier kva punktet følgjer når
    figuren er eksplodert: B 06b, S staven 06, C 06c, R rista 07, M mastfoten. Loddeøyret (plugga) kjem i hw_mleiar.
    06b: frå loddeflata nedst på stripa, under stripa inn framfor staven, gjennom gjennomgangen framfor staven i golvet,
    under golvet rundt kanten på staven og inn i kanalen bak han. 06c: frå toppstripa over bereringen, ned gjennom
    holet på r 17 (90° / 270°), ned bakrommet bak klypa, gjennom gjennomgangen bak klypa og inn i same kanal.
    Kanalen bak staven i mastfoten fører alle fire ned i lomma."""
    kl = 0.2
    zt = p.topp_berar_z + 1.5 + p.stripe_t + LEIAR28_R        # oppå toppstripa
    zr = p.topp_berar_z + 1.5 + LEIAR28_R                     # oppå bereringen
    zg0, zg1 = p.rist_z0, p.rist_z0 + p.golv_t
    kx0 = -p.stav_t / 2 - 1.6
    xb = kx0 - (p.leidning_b + 0.4) / 2                       # midt i gjennomgangen bak klypa
    xf = p.stav_t / 2 + kl + p.leidning_b / 2                 # midt i gjennomgangen framfor staven
    xk = -p.stav_t / 2 - 0.05 - p.mastfot_kanal / 2           # kanalen bak staven i mastfoten
    xs = p.stav_t / 2 + p.stripe_t + LEIAR28_R                # framfor loddeflata nedst på 06b
    yk = (0.65, 1.9, -1.9, -0.65)[j]
    if MLEIARAR[j][2] == "06c":
        s = 1.0 if j == 0 else -1.0
        xg, yg = (xb + 0.3, 4.2) if j == 0 else (xb - 0.4, 6.3)
        b = [("C", (5.6, s * 21.6, zt)), ("C", (3.0, s * 19.2, zr + 0.3)), ("R", (0.0, s * 17.0, zr)),
             ("R", (0.0, s * 17.0, zr - 3.5)), ("R", (-3.2, s * 12.5, zr - 20.0))]
        b += ([("R", (-3.3, 9.5, 180.0)), ("R", (-3.4, 6.5, 120.0))] if j == 0 else
              [("R", (-4.0, -2.0, 160.0)), ("R", (-3.9, 6.3, 100.0))])
        b += [("R", (xg, yg, zg1 + 7.0)), ("R", (xg, yg, zg1 + 1.0)), ("R", (xg, yg, zg0 - 1.5))]
        # under golvet: TOPP+ går innanfor GND frå 06c, som kryssar bakanfor og lågare
        b += ([("S", (xg + 0.9, yg - 2.0, zg0 - 6.0)), ("S", (xk, yk, zg0 - 9.5))] if j == 0 else
              [("S", (-3.0, 3.0, zg0 - 5.0)), ("S", (-2.4, yk, zg0 - 7.5)), ("S", (xk, yk, zg0 - 11.0))])
    else:
        s = 1.0 if j == 1 else -1.0
        ye = p.stav_b / 2 + 0.7
        b = [("B", (xs, s * 2.0, p.stripe_z0 + 1.6)), ("B", (xs, s * 2.0, p.stripe_z0 - 0.6)),
             ("S", (xf, s * 2.0, p.stripe_z0 - 2.0)), ("S", (xf, s * 2.0, zg1 + 1.0)), ("S", (xf, s * 2.0, zg0 - 1.5)),
             ("S", (1.3, s * ye, zg0 - 4.5)), ("S", (-1.3, s * ye, zg0 - 6.5)), ("S", (xk, yk, zg0 - 9.0))]
    # ned kanalen og under enden av staven inn i lomma
    b += [("M", (xk, yk, p.mastfot_z1 + 0.4)), ("M", (xk, yk, p.stav_z0 + 0.8)), ("M", (xk, yk, p.stav_z0 - 0.5))]
    return b


def hw_mleiar(p, j, off=None, n=None, heng=0.0):
    """Leiar j (AWG 28) langs mleiar_bane. off: forskyving per lekam ("B", "S", "C", "R", "M", "P" = plugga), eksplodert.
    n: berre dei n første punkta, og den frie enden heng då heng mm rett ned; n = None: heile vegen til loddeøyret."""
    off = off or {}
    o = lambda k: tuple(off.get(k, (0.0, 0.0, 0.0)))
    b = mleiar_bane(p, j)
    pts = [add(q, o(k)) for k, q in (b if n is None else b[:n])]
    if n is not None:
        if heng > 0:
            pts.append(add(pts[-1], (0.0, 0.0, -heng)))
        return roeyr(pts, LEIAR28_R, glatt=False)
    lx, ly, zb = add(leiar_loddepunkt(p, j), o("P"))
    if zb + 0.75 < pts[-1][2] - 6.0:     # plugga senka: leiaren går skrått ut av lomma
        pts.append(((pts[-1][0] + lx) / 2, (pts[-1][1] + ly) / 2, min(pts[-1][2] - 4.8, zb + 8.0)))
    pts += [(lx, ly, zb + 0.75), (lx, ly, zb)]
    return roeyr(pts, LEIAR28_R, glatt=False)


# Koplinga av dei fire toppstripene 06c (4 x 25 mm på kvadratet r 22, sentra ved 45°, 135°, 225°, 315°): alle med +
# ytst, i parallell. Bøylane går over skøytane mellom stripene (skøytane ligg ved 0°, 90°, 180°, 270°); raud TOPP+
# kjem opp gjennom holet ved 90° og blir lodda på +-bøylen der, svart GND gjennom holet ved 270° til −-bøylen der.
TOPP_BOYLAR = {"+": (0.0, 90.0, 180.0), "GND": (0.0, 180.0, 270.0), "TOPP+_ved": 90.0, "GND_ved": 270.0}


def maal_golvhol(p, s):
    """Leidningsgjennomgangane i golvet på rista 07, målte på B-rep midt i golvet (punktprøve og halvering), så
    figurane og teksten i steg M følgjer geometrien: {"framfor": (x0, x1, y0, y1), "bak": (x0, x1, y0, y1)}.
    Gjennomgangen framfor staven går i eitt med stavsporet, så x0 der er veggen i sporet (stav_t/2 + 0,2)."""
    from OCP.BRepClass3d import BRepClass3d_SolidClassifier
    from OCP.TopAbs import TopAbs_IN, TopAbs_ON
    from OCP.gp import gp_Pnt
    sol = max(s.Solids(), key=lambda q: q.Volume())
    kls = BRepClass3d_SolidClassifier(sol.wrapped)
    z = p.rist_z0 + p.golv_t / 2

    def fylt(x, y):
        kls.Perform(gp_Pnt(x, y, z), 1e-7)
        return kls.State() in (TopAbs_IN, TopAbs_ON)

    def kant(q, d, maks=15.0, steg=0.1):
        """Frå det tomme punktet q langs d til første materiale."""
        t = 0.0
        while t < maks:
            t1 = t + steg
            if fylt(q[0] + d[0] * t1, q[1] + d[1] * t1):
                a, b = t, t1
                for _ in range(24):
                    m = (a + b) / 2
                    if fylt(q[0] + d[0] * m, q[1] + d[1] * m):
                        b = m
                    else:
                        a = m
                return (a + b) / 2
            t = t1
        return float("nan")

    x0f = p.stav_t / 2 + 0.2
    qf = (x0f + 0.3, 0.0)
    x1f = qf[0] + kant(qf, (1.0, 0.0))
    xm = (x0f + x1f) / 2
    yf0, yf1 = -kant((xm, 0.0), (0.0, -1.0)), kant((xm, 0.0), (0.0, 1.0))
    kx0 = -p.stav_t / 2 - 1.6
    qb = (kx0 - (p.leidning_b + 0.4) / 2, 5.25)
    xb0, xb1 = qb[0] - kant(qb, (-1.0, 0.0)), qb[0] + kant(qb, (1.0, 0.0))
    qb2 = ((xb0 + xb1) / 2, qb[1])
    yb0, yb1 = qb2[1] - kant(qb2, (0.0, -1.0)), qb2[1] + kant(qb2, (0.0, 1.0))
    r = lambda v: round(v, 3)
    return {"framfor": (r(x0f), r(x1f), r(yf0), r(yf1)), "bak": (r(xb0), r(xb1), r(yb0), r(yb1))}


def hw_usb():
    """USB-A-plugg med kort kabel, eige system (kabelen langs +X frå plugga)."""
    metall = cq.Workplane("YZ").rect(12.0, 4.5).extrude(-12.0)
    kropp = cq.Workplane("YZ").rect(15.0, 7.5).extrude(18.0)
    hals = cq.Workplane("YZ").workplane(offset=18.0).circle(3.2).workplane(offset=8.0).circle(2.2).loft()
    kabel = cq.Workplane("YZ").workplane(offset=26.0).circle(2.0).extrude(40.0)
    return shape_of(metall.union(kropp).union(hals).union(kabel))


def hw_oring(p):
    """O-ringen (11) som glatt torus med same mål og plass som i modellen (modellen har 24-kantprofil)."""
    rm = p.oring_id / 2.0 + p.oring_strekk_r + p.oring_snor / 2.0
    zc = p.z_fot_0 + p.oring_spor_djup - p.oring_snor / 2.0
    return cq.Solid.makeTorus(rm, p.oring_snor / 2.0, cq.Vector(0, 0, zc), cq.Vector(0, 0, 1))


def hw_brytar_enkel(p):
    """Éin mikrobrytar (del av 12) for ikonet."""
    b = shape_of(g.brytarar(p))
    s = sorted(b.Solids(), key=lambda q: abs(((math.degrees(math.atan2(q.Center().y, q.Center().x)) - p.sw[0][0]) + 180) % 360 - 180))
    return s[0]


# =============================================================================== kjelder (former i montert stilling)
DELNAMN = {k.split("_")[0]: k for k in g.DELAR}  # "01" -> "01_fot"


class Kjelder:
    def __init__(self, p):
        self.p = p
        self._c = {}
        self._info = None

    @property
    def info(self):
        if self._info is None:
            self._info = kabel_info(self.p)
        return self._info

    def del_(self, did):
        k = ("del", did)
        if k not in self._c:
            self._c[k] = shape_of(g.DELAR[DELNAMN[did]][0](self.p))
        return self._c[k]

    def stykke(self, did, i, vinklar):
        """Lekamane i ein del med fleire like (05c, 12) som høyrer til stykke i (næraste asimut)."""
        k = ("stykke", did, i)
        if k not in self._c:
            s = self.del_(did).Solids()
            mål = vinklar[i]
            avst = lambda q: abs(((math.degrees(math.atan2(q.Center().y, q.Center().x)) - mål) + 180) % 360 - 180)
            sel = [q for q in s if avst(q) < 25.0] or [min(s, key=avst)]
            self._c[k] = sel[0] if len(sel) == 1 else cq.Compound.makeCompound(sel)
        return self._c[k]

    def form(self, kjelde, args):
        p = self.p
        k = (kjelde, json.dumps(args))
        if k in self._c:
            return self._c[k]
        if kjelde in DELNAMN:
            s = self.del_(kjelde)
        elif kjelde == "C":
            s = self.stykke("05c", args[0], list(p.stopp_vinklar))
        elif kjelde == "E":
            s = self.stykke("12", args[0], [a for a, _t in p.sw])
        elif kjelde == "G":
            s = self.stykke("11b", args[0], list(p.snor_vinklar))
        elif kjelde == "snorbit":
            s = hw_snorbit()
        elif kjelde == "M2sett":
            s = hw_m2_sett(*args)
        elif kjelde == "J":
            s = hw_brytarfeste(p, *args)
        elif kjelde == "skrujarn":
            s = hw_skrujarn(*args)
        elif kjelde == "multimeter":
            s = hw_multimeter(*args)
        elif kjelde == "fast8":
            s = hw_fastnokkel(*args)
        elif kjelde in ("jack_kropp", "jack_mutter"):
            s = hw_jack_del(p, kjelde.split("_")[1])
        elif kjelde == "B":
            s = hw_innsats(p, args[0])
        elif kjelde == "A":
            s = hw_skrue_a(p, args[0])
        elif kjelde == "F":
            s = hw_kabel(p, *args)
        elif kjelde == "lodd":
            s = hw_loddebolt(*args)
        elif kjelde == "nokkel":
            s = hw_nokkel(*args)
        elif kjelde == "usb":
            s = hw_usb()
        elif kjelde == "Dt":
            s = hw_oring(p)
        elif kjelde == "proto_mantel":
            lo, hi = g.mantel_prototype_delar(g.FyrParams.prototype())
            s = shape_of(lo if args[0] == 0 else hi)
        elif kjelde == "proto_hylse":
            s = shape_of(g.hylse(g.FyrParams.prototype()))
        elif kjelde == "proto_glide":
            s = shape_of(g.glidering(g.FyrParams.prototype()))
        elif kjelde == "MF":
            s = shape_of(g.mastfot(p))
        elif kjelde == "TRS":
            s = shape_of(g.trs_plugg(p))
        elif kjelde == "mleiar":
            s = hw_mleiar(p, *args)
        else:
            raise KeyError(kjelde)
        self._c[k] = s
        return s


# =============================================================================== scener og HLR
@dataclass
class It:
    key: str
    kjelde: str
    args: tuple = ()
    t: tuple = (0.0, 0.0, 0.0)
    rz: float = 0.0
    ny: bool = False


@dataclass
class Scene:
    namn: str
    items: list
    N: tuple = ISO
    X: tuple | None = None
    G: str = ""            # "" eller "snu" (180° om X: delen ligg opp ned)
    kutt: dict | None = None
    region: dict | None = None
    defl: float = 0.06

    def spec(self):
        return {"items": [[i.key, i.kjelde, list(i.args), list(i.t), i.rz] for i in self.items], "N": list(self.N),
                "X": list(self.X) if self.X else None, "G": self.G, "kutt": self.kutt, "region": self.region, "defl": self.defl}


def projektor(N, X=None):
    n = norm(N)
    x = norm(X) if X else norm(cross((0, 0, 1), n))
    return HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*n), gp_Dir(*x)))


def G_pkt(G, q):
    return (q[0], -q[1], -q[2]) if G == "snu" else tuple(q)


def proj_pkt(sc: Scene, q):
    pr = projektor(sc.N, sc.X)
    r = gp_Pnt2d()
    pr.Project(gp_Pnt(*G_pkt(sc.G, q)), r)
    return (r.X(), r.Y())


def kantar(comp, defl):
    ut = []
    if comp is None or comp.IsNull():
        return ut
    BRepLib.BuildCurves3d_s(comp)
    e = TopExp_Explorer(comp, TopAbs_EDGE)
    while e.More():
        c = BRepAdaptor_Curve(TopoDS.Edge_s(e.Current()))
        d = GCPnts_QuasiUniformDeflection(c, defl)
        if d.IsDone() and d.NbPoints() > 1:
            ut.append([(round(d.Value(i).X(), 3), round(d.Value(i).Y(), 3)) for i in range(1, d.NbPoints() + 1)])
        e.Next()
    return ut


def kjelde_hash():
    h = hashlib.sha1()
    h.update((HER / "fyr_geometri.py").read_bytes())
    for f in (hw_innsats, knappskrue, hw_skrue_a, hw_loddebolt, hw_nokkel, kabel_info, kabelbane, leiarbane, roeyr_delar, roeyr, hw_kabel,
              hw_usb, hw_brytar_enkel, hw_oring, panskrue, m2_mutter, hw_m2_sett, hw_brytarfeste, hw_skrujarn,
              hw_multimeter, hw_snorbit, hw_fastnokkel, hw_jack_del, leiar_loddepunkt, mleiar_bane, hw_mleiar, plasser, Kjelder.form,
              Kjelder.stykke, kantar, HLR._rekn):
        h.update(inspect.getsource(f).encode("utf-8"))
    return h.hexdigest()[:16]


class HLR:
    def __init__(self, p, bruk_cache=True):
        self.p = p
        self.kj = Kjelder(p)
        self.hash = kjelde_hash()
        self.bruk = bruk_cache
        self.tal = {"cache": 0, "rekna": 0}
        self.utdaterte = []
        CACHE.mkdir(parents=True, exist_ok=True)

    def info(self):
        f = CACHE / f"info_{self.hash}.pkl"
        if self.bruk and f.exists():
            return pickle.loads(f.read_bytes())
        i = self.kj.info
        f.write_bytes(pickle.dumps(i))
        return i

    def __call__(self, sc: Scene):
        key = hashlib.sha1((self.hash + json.dumps(sc.spec(), sort_keys=True)).encode()).hexdigest()[:20]
        f = CACHE / f"hlr_{sc.namn}_{key}.pkl"
        if self.bruk and f.exists():
            self.tal["cache"] += 1
            return pickle.loads(f.read_bytes())
        try:
            return self._rekn(sc, f)
        except Exception as e:  # noqa: BLE001  geometrien kan vere midt i ei endring
            gamle = sorted(CACHE.glob(f"hlr_{sc.namn}_*.pkl"), key=lambda q: q.stat().st_mtime)
            if not gamle:
                raise
            print(f"  ÅTVARING: {sc.namn} kunne ikkje reknast ({type(e).__name__}: {e}); brukar eldre projeksjon", flush=True)
            self.utdaterte.append(sc.namn)
            return pickle.loads(gamle[-1].read_bytes())

    def _rekn(self, sc, f):
        t0 = time.time()
        former = []
        for it in sc.items:
            s = self.kj.form(it.kjelde, list(it.args))
            if it.rz:
                s = s.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), it.rz)
            if any(it.t):
                s = s.translate(cq.Vector(*it.t))
            if sc.region:
                c, h = sc.region["c"], sc.region["h"]
                boks = cq.Solid.makeBox(2 * h, 2 * h, 2 * h, cq.Vector(c[0] - h, c[1] - h, c[2] - h))
                try:
                    s = s.intersect(boks)
                except Exception:  # noqa: BLE001
                    continue
                if not s.Solids():
                    continue
            kutt = sc.kutt if isinstance(sc.kutt, list) else ([sc.kutt] if sc.kutt else [])
            for k in kutt:
                if k.get("delar") and it.key not in k["delar"]:
                    continue
                if k["type"] == "snitt":
                    b = cq.Solid.makeBox(1000, 500, 1000, cq.Vector(-500, -500, -500)).rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), k["az"])
                elif k["type"] == "over":
                    b = cq.Solid.makeBox(1000, 1000, 500, cq.Vector(-500, -500, k["z"]))
                elif k["type"] == "utanfor_r":
                    b = cq.Solid.makeCylinder(500, 1000, cq.Vector(0, 0, -500)).cut(cq.Solid.makeCylinder(k["r"], 1000, cq.Vector(0, 0, -500)))
                else:
                    raise KeyError(k)
                try:
                    s = s.cut(b)
                except Exception:  # noqa: BLE001
                    pass
            if kutt and not s.Solids():
                continue
            # tangentkontinuerlege kantar (kuler mot sylindrar, rundingar) skal ikkje teiknast som skarpe
            BRepLib.EncodeRegularity_s(s.wrapped, 0.01)
            if sc.G == "snu":
                s = s.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180)
            former.append((it.key, s))
        pr = projektor(sc.N, sc.X)
        algo = HLRBRep_Algo()
        for _k, s in former:
            algo.Add(s.wrapped)
        algo.Projector(pr)
        algo.Update()
        algo.Hide()
        h = HLRBRep_HLRToShape(algo)
        res = {}
        for k, s in former:
            res[k] = {"o": kantar(h.OutLineVCompound(s.wrapped), sc.defl), "s": kantar(h.VCompound(s.wrapped), sc.defl)}
        f.write_bytes(pickle.dumps(res))
        self.tal["rekna"] += 1
        print(f"  HLR {sc.namn:22s} {time.time() - t0:5.1f} s", flush=True)
        return res


def bbox(res, keys=None):
    xs, ys = [], []
    for k, d in res.items():
        if keys and k not in keys:
            continue
        for pl in d["o"] + d["s"]:
            for (u, v) in pl:
                xs.append(u)
                ys.append(v)
    if not xs:
        return (0, 0, 1, 1)
    return (min(xs), min(ys), max(xs), max(ys))


# =============================================================================== SVG-side
FONT = "Arial, Helvetica, sans-serif"


class Side:
    def __init__(self, namn, tittel=""):
        self.namn = namn
        self.tittel = tittel
        self.el = []
        self.defs = []
        self.nclip = 0
        self.scener = []   # for scener.json

    # ---- primitiv
    def linje(self, pts, w=W_FIN, dash=None, farge="#000"):
        if len(pts) < 2:
            return
        d = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.el.append(f'<polyline points="{d}" fill="none" stroke="{farge}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{da}/>')

    def tekst(self, x, y, s, size=3.5, vekt="normal", anker="start", farge="#000"):
        self.el.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{FONT}" font-size="{size}" font-weight="{vekt}" '
                       f'text-anchor="{anker}" fill="{farge}">{html.escape(s)}</text>')

    def sirkel(self, x, y, r, w=W_KT_O, fill="none", dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.el.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{fill}" stroke="#000" stroke-width="{w}"{da}/>')

    def rekt(self, x0, y0, x1, y1, w=W_KT_S, fill="none", rx=0):
        self.el.append(f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{x1 - x0:.2f}" height="{y1 - y0:.2f}" rx="{rx}" fill="{fill}" stroke="#000" stroke-width="{w}"/>')

    def poly(self, pts, w=W_KT_O, fill="#fff"):
        d = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        self.el.append(f'<polygon points="{d}" fill="{fill}" stroke="#000" stroke-width="{w}" stroke-linejoin="miter"/>')

    # ---- strekteikning
    def teikning(self, res, f2, ny=(), skala_vekt=1.0, clip=None):
        g_open = ""
        if clip:
            self.nclip += 1
            cid = f"c{self.nclip}"
            self.defs.append(f'<clipPath id="{cid}"><circle cx="{clip[0]:.2f}" cy="{clip[1]:.2f}" r="{clip[2]:.2f}"/></clipPath>')
            self.el.append(f'<g clip-path="url(#{cid})">')
            g_open = "</g>"
        for k, d in res.items():
            er_ny = k in ny or any(k.startswith(n + "#") for n in ny)
            wo, ws = (W_NY_O, W_NY_S) if er_ny else (W_KT_O, W_KT_S)
            # kabelen er bygd av sylinderstykke; skøytane mellom stykka skal ikkje synast, berre omrisset
            for pl in ([] if k == "F" else d["s"]):
                self.linje([f2(q) for q in pl], ws * skala_vekt)
            for pl in d["o"]:
                self.linje([f2(q) for q in pl], wo * skala_vekt)
        if g_open:
            self.el.append(g_open)

    # ---- symbol
    def ballong(self, anker, pos, tekst, r=3.7, beslag=False):
        ax, ay = anker
        bx, by = pos
        L = math.hypot(bx - ax, by - ay)
        if L > r:
            ex, ey = bx - (bx - ax) * r / L, by - (by - ay) * r / L
            self.linje([(ax, ay), (ex, ey)], W_FIN)
        self.el.append(f'<circle cx="{ax:.2f}" cy="{ay:.2f}" r="0.55" fill="#000"/>')
        if beslag:
            self.rekt(bx - r, by - r, bx + r, by + r, W_KT_O, "#fff")
        else:
            self.sirkel(bx, by, r, W_KT_O, "#fff")
        sz = 3.3 if len(tekst) <= 2 else 2.6
        self.tekst(bx, by + sz * 0.36, tekst, sz, "bold", "middle")

    def hol_pil(self, pts, w=2.4, hw=6.4, hl=5.2):
        from shapely.geometry import LineString, Polygon
        pts = [tuple(q) for q in pts]
        # fjern dublettar
        rein = [pts[0]]
        for q in pts[1:]:
            if math.hypot(q[0] - rein[-1][0], q[1] - rein[-1][1]) > 0.05:
                rein.append(q)
        pts = rein
        if len(pts) < 2:
            return
        tip = pts[-1]
        # gå bakover hl langs lina for basen til pilhovudet
        rest = hl
        i = len(pts) - 1
        base = pts[0]
        while i > 0:
            a, b = pts[i - 1], pts[i]
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            if L >= rest:
                base = (b[0] + (a[0] - b[0]) * rest / L, b[1] + (a[1] - b[1]) * rest / L)
                break
            rest -= L
            i -= 1
        skaft = pts[:i] + [base]
        dx, dy = tip[0] - base[0], tip[1] - base[1]
        L = math.hypot(dx, dy) or 1
        nx, ny_ = -dy / L, dx / L
        hode = Polygon([(base[0] + nx * hw / 2, base[1] + ny_ * hw / 2), tip, (base[0] - nx * hw / 2, base[1] - ny_ * hw / 2)])
        if len(skaft) >= 2:
            form = LineString(skaft).buffer(w / 2, cap_style=2, join_style=2, mitre_limit=4).union(hode)
        else:
            form = hode
        if form.geom_type != "Polygon":
            form = max(form.geoms, key=lambda q: q.area)
        self.poly(list(form.exterior.coords), W_KT_O, "#fff")

    def strek(self, a, b):
        self.linje([a, b], W_FIN, dash="1.6 1.1")

    def snu_ikon(self, x, y, tekst="snu"):
        """Lita teikning av ei vending: boge med pil og ein flat blokk som blir snudd."""
        self.rekt(x, y + 6, x + 10, y + 9, W_KT_O)
        self.rekt(x + 15, y + 6, x + 25, y + 9, W_KT_O, "#000")
        bue = [(x + 5 + 7.5 - 7.5 * math.cos(t * DEG), y + 4 - 4.5 * math.sin(t * DEG)) for t in range(10, 171, 8)]
        self.hol_pil(bue, w=1.2, hw=3.2, hl=2.6)
        self.tekst(x + 12.5, y + 14, tekst, 3.0, "normal", "middle")

    def auge_ikon(self, x, y, tekst):
        self.el.append(f'<path d="M{x:.2f},{y:.2f} Q{x + 6:.2f},{y - 4.5:.2f} {x + 12:.2f},{y:.2f} Q{x + 6:.2f},{y + 4.5:.2f} {x:.2f},{y:.2f} Z" '
                       f'fill="none" stroke="#000" stroke-width="{W_KT_O}"/>')
        self.sirkel(x + 6, y, 1.6, W_KT_O, "#000")
        self.tekst(x + 15, y + 1.2, tekst, 3.0)

    def svg(self, sidenr, totalt, kart=None):
        hode = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{A4W}mm" height="{A4H}mm" viewBox="0 0 {A4W} {A4H}">'
                f'<defs>{"".join(self.defs)}</defs><rect x="0" y="0" width="{A4W}" height="{A4H}" fill="#fff"/>')
        fot = (f'<text x="{A4W - 12}" y="{A4H - 9}" font-family="{FONT}" font-size="2.6" text-anchor="end">'
               f'FYR · montering og service · {REVISJON} · {DATO} · {sidenr}/{totalt}</text>')
        return hode + sidetal("".join(self.el), kart or {}) + fot + "</svg>"


def sideref(namn):
    """Plasshaldar for sidenummeret til sida namn; blir fylt inn når alle sidene er bygde (sidetal)."""
    return "{{side:" + namn + "}}"


def sidetal(tekst, kart):
    return re.sub(r"\{\{side:([\w-]+)\}\}", lambda m: str(kart.get(m.group(1), "?")), tekst)


# ---- figurplassering
def fit_skala(res, ramme, keys=None):
    u0, v0, u1, v1 = bbox(res, keys)
    x0, y0, x1, y1 = ramme
    return min((x1 - x0) / max(u1 - u0, 1e-6), (y1 - y0) / max(v1 - v0, 1e-6))


def figur(res, ramme, skala, juster="midt"):
    """Gjev f2(uv)->side, plassert midt i ramma med gitt skala."""
    u0, v0, u1, v1 = bbox(res)
    x0, y0, x1, y1 = ramme
    bw, bh = (u1 - u0) * skala, (v1 - v0) * skala
    ox = x0 + ((x1 - x0) - bw) / 2
    oy = y0 + ((y1 - y0) - bh) / 2 if juster == "midt" else (y1 - bh if juster == "botn" else y0)
    return lambda q: (ox + (q[0] - u0) * skala, oy + (v1 - q[1]) * skala)


# =============================================================================== monteringa
class Rettleiing:
    def __init__(self, p, hlr: HLR):
        self.p = p
        self.hlr = hlr
        self.sider: list[Side] = []
        self.manifest = []
        self.info = hlr.info()

    # ------------------------------------------------------------------ hjelparar
    def scene(self, namn, items, **kw):
        return Scene(namn, items, **kw)

    def f3(self, sc, f2):
        return lambda q: f2(proj_pkt(sc, q))

    @staticmethod
    def ank(res, f2, key, mot=(-1, 0), h=0.5, band=0.05):
        """Festepunkt for ein leiar: synleg punkt på delen (key, eller key#n) lengst i retning mot,
        innanfor eit band rundt relativ høgd h (0 = topp, 1 = botn av delen på arket)."""
        pts = []
        for k, d in res.items():
            if k == key or k.startswith(key + "#"):
                for pl in d["o"] + d["s"]:
                    pts += [f2(q) for q in pl]
        if not pts:
            return None
        ys = [q[1] for q in pts]
        y0, y1 = min(ys), max(ys)
        yc = y0 + (y1 - y0) * h
        for b in (band, band * 3, 1.0):
            sel = [q for q in pts if abs(q[1] - yc) <= max(1.0, (y1 - y0) * b)]
            if sel:
                break
        return max(sel, key=lambda q: q[0] * mot[0] + q[1] * mot[1])

    def merk(self, s, res, f2, key, tekst=None, mot=(-1, 0), h=0.5, off=None, beslag=False):
        a = self.ank(res, f2, key, mot, h)
        if a is None:
            return
        off = off or (mot[0] * 16, mot[1] * 16)
        s.ballong(a, (a[0] + off[0], a[1] + off[1]), tekst or key, beslag=beslag)

    def ny_side(self, namn, tittel=""):
        s = Side(namn, tittel)
        self.sider.append(s)
        return s

    def steghovud(self, s, nr, tittel):
        s.tekst(13, 30, str(nr), 17, "bold")
        s.tekst(13 + 11 * len(str(nr)) + 2, 29.5, tittel, 4.2)

    def beslagboks(self, s, innhald, x1=198, y0=10, h=30, bw=25):
        """innhald: liste av (type, merke, scene|None, tal). Boksen står øvst til høgre."""
        n = len(innhald)
        x0 = x1 - n * bw
        s.rekt(x0, y0, x1, y0 + h, W_KT_O, "#fff", rx=2)
        for i, (typ, merke, sc, tal) in enumerate(innhald):
            cx = x0 + i * bw
            if i:
                s.linje([(cx, y0 + 2), (cx, y0 + h - 2)], W_FIN)
            if sc is not None:
                res = self.hlr(sc)
                ramme = (cx + 3, y0 + 3, cx + bw - 3, y0 + h - 10)
                k = fit_skala(res, ramme)
                s.teikning(res, figur(res, ramme, k), ny=set(res), skala_vekt=0.7)
            if typ == "del":
                s.sirkel(cx + 6, y0 + h - 5, 3.3, W_KT_O, "#fff")
                s.tekst(cx + 6, y0 + h - 3.8, merke, 3.0 if len(merke) <= 2 else 2.3, "bold", "middle")
            elif typ == "beslag":
                s.rekt(cx + 2.8, y0 + h - 8.3, cx + 9.2, y0 + h - 1.9, W_KT_O, "#fff")
                s.tekst(cx + 6, y0 + h - 3.8, merke, 3.2, "bold", "middle")
            elif typ == "modul":       # ferdig samla eining: delnummera på line
                s.tekst(cx + 3, y0 + h - 3.8, merke, 3.0, "bold", "start")
            else:
                s.tekst(cx + bw / 2, y0 + h - 3.6, merke, 2.5, "normal", "middle")
            if tal:
                s.tekst(cx + bw - 3, y0 + h - 3.6, f"×{tal}", 3.4, "bold", "end")

    def detalj(self, s, sc, senter, r_modell, pos, r_side, main=None, pilar=(), ny=(), merke_r=None, tekst=None):
        """Forstørringsboble. main = (f3_hovud, punkt3d) for markering og leiar på hovudfiguren."""
        res = self.hlr(sc)
        k = r_side / r_modell
        cu, cv = proj_pkt(sc, senter)
        f2 = lambda q: (pos[0] + (q[0] - cu) * k, pos[1] - (q[1] - cv) * k)
        s.sirkel(pos[0], pos[1], r_side, 0.0001, "#fff")
        s.teikning(res, f2, ny=ny, clip=(pos[0], pos[1], r_side))
        f3 = lambda q: f2(proj_pkt(sc, q))
        for pl in pilar:
            if pl[0] == "pil":
                s.hol_pil([f3(q) for q in pl[1]], w=1.8, hw=4.8, hl=3.8)
            elif pl[0] == "pil2":
                s.hol_pil(pl[1], w=1.8, hw=4.8, hl=3.8)
        s.sirkel(pos[0], pos[1], r_side, 0.5)
        if main:
            f3m, q, rm = main
            mx, my = f3m(q)
            rm = rm or 5.0
            s.sirkel(mx, my, rm, W_KT_O)
            dx, dy = pos[0] - mx, pos[1] - my
            L = math.hypot(dx, dy)
            if L > rm + r_side:
                s.linje([(mx + dx * rm / L, my + dy * rm / L), (pos[0] - dx * r_side / L, pos[1] - dy * r_side / L)], W_KT_S)
        if tekst:
            s.tekst(pos[0], pos[1] + r_side + 5, tekst, 3.2, "normal", "middle")
        return f3

    def logg(self, side, nr, tittel, sc, skala, pilar_3d=(), merknad=""):
        self.manifest.append({
            "side": len(self.sider), "steg": nr, "tittel": tittel, "scene": sc.namn,
            "kamera": {"retning_mot_betraktar": list(norm(sc.N)), "x_akse": list(sc.X) if sc.X else None,
                       "snudd_180_om_x": sc.G == "snu", "skala_mm_per_mm": round(skala, 4)},
            "delar": [{"id": it.key, "kjelde": it.kjelde, "ny_i_steget": it.ny, "rot_z_grader": it.rz,
                       "eksplodert_forskyving_mm": [round(c, 2) for c in it.t]} for it in sc.items],
            "rorsle": list(pilar_3d), "merknad": merknad})

    # ------------------------------------------------------------------ standardsett
    @property
    def mastfot(self):
        """Ny modell: 06d er mastfoten på lysmodulen (TRS-plugg ned i chassiset), ikkje ein kontakt i chassiset."""
        return hasattr(self.p, "mastfot_z0")

    @property
    def MOD(self):
        return ("06", "06b", "06c", "07") + (("06d",) if self.mastfot else ())

    def synlegaste(self, vinklar):
        return max(range(len(vinklar)), key=lambda i: math.cos((vinklar[i] - V_ISO) * DEG))

    def elektronikk(self, t=(0.0, 0.0, 0.0), kort=True):
        """Det som sit i chassiset etter steg 2 til 4: brytarar med feste J, jack og kort."""
        p = self.p
        it = [It(f"E#{i}", "E", (i,), t=t) for i in range(len(p.sw))] + [It("13", "13", t=t)] + self.brytarfeste(t=t)
        if kort:
            it.append(It("14", "14", t=t))
        return it

    def brytarfeste(self, t=(0.0, 0.0, 0.0), brytarar=None, ut=0.0, inn=0.0, ny=False):
        """Festa J (skrue + skive/mutter) for brytarane. ut/inn: eksplodert radielt (skrue ut, mutter inn)."""
        p = self.p
        it = []
        for i in (range(len(p.sw)) if brytarar is None else brytarar):
            r = polar3(1.0, p.sw[i][0], 0.0)
            for j in range(2):
                it.append(It(f"J#{i}{j}s", "J", (i, j, "skrue"), t=add(t, mul(r, ut)), ny=ny))
                it.append(It(f"J#{i}{j}m", "J", (i, j, "mutter"), t=add(t, mul(r, -inn)), ny=ny))
        return it

    def basis(self, kabel=True, skruar=False, oring=True, snor=False, nyttig=()):
        p = self.p
        it = [It("01", "01"), It("03", "03")] + self.elektronikk()
        if not self.mastfot:
            it += [It("06d", "06d")]
        if kabel:
            it.append(It("F", "F", (0.0,)))
        if oring:
            it.append(It("D", "Dt"))
        if snor:
            it += [It(f"G#{i}", "G", (i,)) for i in range(len(p.snor_vinklar))]
        if skruar:
            it += [It(f"A#{i}", "A", (a,)) for i, a in enumerate(p.skrue_vinklar)]
        for x in it:
            if x.key in nyttig:
                x.ny = True
        return it

    def hylse_sett(self, dz=0.0, rz=0.0, ny=False, skruar=True):
        p = self.p
        it = [It("05b", "05b", t=(0, 0, dz), rz=rz, ny=ny), It("05", "05", t=(0, 0, dz), rz=rz, ny=ny)]
        if skruar:
            it += [It(f"C#{i}", "C", (i,), t=(0, 0, dz), rz=rz) for i in range(len(p.stopp_vinklar))]
        return it

    def modul(self, dz=0.0, ny=False):
        return [It(k, k, t=(0, 0, dz), ny=ny) for k in self.MOD]

    # ------------------------------------------------------------------ hardware-ikon
    def ikon(self, kva):
        p = self.p
        if kva == "A":
            return Scene("ikon_A", [It("A", "A", (0.0,))], G="snu", defl=0.02)
        if kva == "B":
            return Scene("ikon_B", [It("B", "B", (0.0,))], defl=0.02)
        if kva == "C":
            return Scene("ikon_C", [It("C", "C", (0,))], N=(0.3, -1.0, 0.6), defl=0.02)
        if kva == "D":
            return Scene("ikon_D", [It("D", "Dt")], defl=0.1)
        if kva == "E":
            return Scene("ikon_E", [It("E", "E", (0,))], defl=0.02)
        if kva == "F":
            return Scene("ikon_F", [It("Fusb", "usb")], N=(0.6, -1.0, 0.7), defl=0.05)
        if kva == "lodd":
            return Scene("ikon_lodd", [It("L", "lodd", ((0, 0, 0), (1, 0, 0.35)))], N=(0.2, -1.0, 0.4), defl=0.08)
        if kva in ("n15", "n20", "n25"):
            d = {"n15": 1.5, "n20": 2.0, "n25": 2.5}[kva]
            return Scene("ikon_" + kva, [It("N", "nokkel", (d, (0, 0, 0), (0, 0, 1), (1, 0, 0)))], N=(0.4, -1.0, 0.5), defl=0.03)
        if kva == "G":
            return Scene("ikon_G", [It("G", "snorbit")], N=(0.3, -1.0, 0.7), defl=0.02)
        if kva == "J":
            return Scene("ikon_J", [It("J", "M2sett", (10.0, True))], G="snu", defl=0.01)
        if kva == "ph0":
            return Scene("ikon_ph0",[It("S", "skrujarn", ((0, 0, 0), (1, 0, 0.35), (0, 0, 1)))], N=(0.2, -1.0, 0.4), defl=0.05)
        if kva == "multimeter":
            return Scene("ikon_multimeter", [It("M", "multimeter", (True,))], N=(0.35, -0.6, 1.0), defl=0.05)
        if kva == "modul":
            return Scene("ikon_modul", [It(k, k) for k in self.MOD], N=(0.6, -1.0, 0.45), X=(0, 0, 1), defl=0.08)
        if kva == "f8":
            return Scene("ikon_f8", [It("W", "fast8", ((0, 0, 0), (1, 0, 0)))], N=(0.25, -0.35, 1.0), defl=0.03)
        if kva == "13":
            return Scene("ikon_13", [It("13", "13")], N=(1.0, -0.8, 0.45), defl=0.02)
        if kva == "14":
            return Scene("ikon_14", [It("14", "14")], N=(0.8, -1.0, 1.1), defl=0.05)
        if kva in DELNAMN:
            return Scene("ikon_" + kva, [It(kva, kva)], defl=0.08)
        raise KeyError(kva)

    @property
    def c_beskriving(self):
        p = self.p
        if hasattr(p, "stopp_hovud_d"):
            return f"ISO 7380 M3×{fmt(getattr(p, 'stopp_l', 5.0))}", "n20", "2 mm"
        return "ISO 7435 M3×6", "n15", "1,5 mm"

    # ================================================================== sidene
    # stegnummera på eitt stad: feilsøking og service viser hit
    STEG = {"innsatsar": 1, "jack": 2, "brytarar": 3, "kort": 4, "kabel": 5, "skruar": 6, "oring": 7, "glidering": 8,
            "fotring": 9, "hylse": 10, "stopp": 11, "juster": 12, "modul": 13, "prov": 14, "snor": 15, "mantel": 16, "lok": 17}

    def bygg(self):
        p = self.p
        t0 = time.time()
        self.s_framside()
        self.s_delar()
        self.s_beslag()
        self.s_oversikt()
        self.s1_innsatsar()
        self.s_jack()
        self.s2_brytarar()
        self.s_kort()
        self.s3_kabel()
        self.s4_skruar()
        self.s5_oring()
        self.s6_glidering()
        self.s7_fotring()
        self.s8_hylse_ned()
        self.s9_stoppskruar()
        self.s_juster()
        self.s10_modul()
        self.s11_prov()
        self.s_snor()
        self.s12_mantel()
        self.s13_lok()
        self.s_sluttkontroll()
        self.s_service_modul()
        self.s_service_kabel()
        self.s_feilsoking()
        self.s_lysmodul()
        self.s_prototype()
        print(f"sider bygde {time.time() - t0:.1f} s  (HLR: {self.hlr.tal})", flush=True)

    # ------------------------------------------------------------------ framside
    def heil(self, med_mantel=True, med_lok=True):
        it = self.basis(snor=med_mantel)
        it += self.hylse_sett()
        it += self.modul()
        if med_mantel:
            it += [It("04", "04"), It("10", "10")]
        if med_lok:
            it.append(It("08", "08"))
        return it

    def s_framside(self):
        s = self.ny_side("framside")
        sc = Scene("framside", self.heil(), defl=0.05)
        res = self.hlr(sc)
        ramme = (30, 62, 180, 272)
        k = fit_skala(res, ramme)
        s.teikning(res, figur(res, ramme, k), ny=set(res))
        s.tekst(14, 34, "FYR", 22, "bold")
        s.tekst(14, 44, "Montering og service", 6)
        s.tekst(14, 51, f"Revisjon {REVISJON} · {DATO} · seriegeometri · teikna frå CAD", 3.2)
        self.logg(s, None, "framside", sc, k)

    # ------------------------------------------------------------------ delar
    def s_delar(self):
        p = self.p
        s = self.ny_side("delar")
        s.tekst(13, 26, "Delar", 7, "bold")
        delar = [("01", 1), ("03", 1), ("04", 1), ("10", 1), ("05", 1), ("05b", 1), ("06", 1), ("07", 1), ("08", 1), ("06d", 1),
                 ("13", 1), ("14", 1)]
        merknad = {"06": "med LED 06b + 06c", "07": "limt til staven (2K-epoksy)",
                   "08": f"opal Ø{fmt(2 * p.r_lok)} (prototype Ø{fmt(2 * g.FyrParams.prototype().r_lok)})",
                   "06d": "mastfot med 3,5 mm TRS-plugg" if self.mastfot else "X1, 3-pol",
                   "13": "3,5 mm TRS-kontakt, M6-mutter", "14": "kort: R1, R3, F1, JST PH"}
        kol, rad = 3, 4
        x0, y0, cw, ch = 13, 34, 61.3, 60
        for i, (did, n) in enumerate(delar):
            cx = x0 + (i % kol) * cw
            cy = y0 + (i // kol) * ch
            items = [It(did, did)]
            if did == "06":
                items = [It("06", "06"), It("06b", "06b"), It("06c", "06c")]
            sc = Scene("del_" + did, items, defl=0.08)
            res = self.hlr(sc)
            ramme = (cx + 12, cy + 4, cx + cw - 4, cy + ch - 6)
            k = fit_skala(res, ramme)
            s.teikning(res, figur(res, ramme, k), ny=set(res), skala_vekt=0.85)
            s.sirkel(cx + 6, cy + 7, 3.7, W_KT_O, "#fff")
            s.tekst(cx + 6, cy + 8.2, did, 3.3 if len(did) <= 2 else 2.6, "bold", "middle")
            s.tekst(cx + 6, cy + 15, f"×{n}", 3.6, "bold", "middle")
            if did in merknad:
                s.tekst(cx + 4, cy + ch - 3, merknad[did], 2.6)
        s.tekst(13, 278, "Lysmodulen (06 + 07" + (" + 06d" if self.mastfot else "") + ") kjem ferdig samla og limt (2K-epoksy), "
                "og blir bytt som éi eining.", 3.0)
        s.tekst(13, 283, f"Førmonteringa av modulen står på side {sideref('lysmodul')}.", 3.0)

    def s_beslag(self):
        p = self.p
        s = self.ny_side("beslag")
        s.tekst(13, 26, "Beslag og verktøy", 7, "bold")
        cdesc, cnok, cnok_t = self.c_beskriving
        rader = [("A", 3, ["ISO 7380 M3×16"], "A"), ("B", 3, [f"innpressmutter M3×{fmt(p.innsats_l)}"], "B"),
                 ("C", 3, [cdesc, f"gjengeformande, skjer gjengene i Ø{fmt(p.stopp_kjerne_d)}"], "C"),
                 ("D", 1, [f"O-ring {fmt(p.oring_id)}×{fmt(p.oring_snor)} silikon (11)"], "D"),
                 ("E", 3, ["mikrobrytar (12): 2 × D2F-01L3 gull", "(SW1, SW3) og 1 × D2F-L3 sølv (SW2)"], "E"),
                 ("F", 1, [f"USB-kabel 5 V, Ø{fmt(2 * KABEL_R)}, med JST PH-plugg"], "F"),
                 ("G", 3, [f"silikonsnor Ø{fmt(p.snor_d)} × {fmt(p.snor_l)} (11b)"], "G"),
                 ("J", 6, ["ISO 7045 M2 × 10 + skive + M2-mutter (PH0)", "brytarfeste, 2 per brytar"], "J")]
        # posisjonen i innkjøpslista (kontroll/fyr_innkjopsliste.csv) for kvar beslagsbokstav. Lysmodulen har ingen
        # beslag: han er limt (H11) og kjem ferdig samla; limet og leiarane står under Forbruk nedst.
        pos = {"A": "H2", "B": "H1", "C": "H3", "D": "H5", "E": "E2 + E3", "F": "E9 + E10", "G": "H10", "J": "H4"}
        y = 32
        dy = 20
        for (b, n, txt, ik) in rader:
            s.linje([(13, y), (197, y)], W_FIN)
            s.rekt(15, y + 5, 25, y + 15, W_KT_O, "#fff")
            s.tekst(20, y + 12.3, b, 5.5, "bold", "middle")
            res = self.hlr(self.ikon(ik))
            ramme = (34, y + 3, 104, y + dy - 3)
            s.teikning(res, figur(res, ramme, fit_skala(res, ramme)), ny=set(res), skala_vekt=0.85)
            s.tekst(112, y + 12, f"×{n}", 5.5, "bold")
            s.tekst(112, y + 17, f"pos. {pos[b]}", 2.4)
            yt = y + 11.6 - 2.2 * (len(txt) - 1)
            for j, t in enumerate(txt):
                s.tekst(128, yt + 4.4 * j, t, 3.4)
            y += dy
        s.linje([(13, y), (197, y)], W_FIN)
        y += 4
        s.tekst(13, y + 4, "Verktøy", 4.5, "bold")
        y += 7
        verk = [("lodd", "loddebolt"), ("n20", "sekskant 2 mm"), ("f8", "fastnøkkel 8 mm"), ("ph0", "skrujarn PH0"),
                ("multimeter", "multimeter (pip)")]
        if cnok != "n20":
            verk.append((cnok, f"sekskant {cnok_t}"))
        bw = 184 / len(verk)
        for i, (ik, txt) in enumerate(verk):
            x = 13 + i * bw
            res = self.hlr(self.ikon(ik))
            ramme = (x + 3, y, x + bw - 3, y + 24)
            s.teikning(res, figur(res, ramme, fit_skala(res, ramme)), ny=set(res), skala_vekt=0.85)
            s.tekst(x + bw / 2, y + 30, txt, 3.2, "normal", "middle")
        y += 36
        # inga lim i hovudmonteringa; lim og forbruk berre i førmonteringa av lysmodulen og i prototypen
        s.rekt(15, y, 31, y + 10, W_KT_O)
        s.tekst(23, y + 6.6, "lim", 3.4, "bold", "middle")
        s.linje([(13, y + 12), (33, y - 2)], 0.6)
        s.tekst(38, y + 4.2, "Ikkje lim i monteringa, steg 1 til 17.", 3.4)
        s.tekst(38, y + 9.4, f"Lim berre i førmonteringa av lysmodulen (side {sideref('lysmodul')}) og i prototypen "
                f"(side {sideref('prototype')}).", 3.0)
        y += 19
        s.tekst(13, y, "Forbruk", 3.4, "bold")
        forbruk = [("Lysmodul", "2K-epoksy: pluggen og staven i mastfoten, kil under golvet i rista", "pos. H11"),
                   ("", "leiarar AWG 28: raud TOPP+, blå SIDE+, 2 × svart GND, bøylar på 06c", "pos. E12"),
                   ("", "loddetinn", ""),
                   ("Prototype", "epoksy til falsen i mantelen", "pos. H8"),
                   ("", "CA (sekundlim) til gliderringen 10", "pos. H12")]
        for j, (gruppe, t, ps) in enumerate(forbruk):
            yy = y + 5.2 * j + (2.0 if j >= 3 else 0.0)
            if gruppe:
                s.tekst(38, yy, gruppe, 3.0, "bold")
            s.tekst(60, yy, t, 3.0)
            s.tekst(197, yy, ps, 2.6, "normal", "end")

    # ------------------------------------------------------------------ eksplodert oversikt
    def s_oversikt(self):
        p = self.p
        s = self.ny_side("oversikt")
        s.tekst(13, 26, "Oversikt", 7, "bold")
        Xs = norm(cross((0, 0, 1), norm(ISO)))
        hx = lambda k, dz: (Xs[0] * k, Xs[1] * k, dz)
        it = [It("01", "01"), It("D", "Dt", t=(0, 0, -24)), It("F", "F", (40.0,))]
        it += [It(f"G#{i}", "G", (i,), t=(0, 0, 12)) for i in range(len(p.snor_vinklar))]
        it += [It("03", "03", t=(0, 0, 40))] + self.elektronikk(t=(0, 0, 40)) + ([] if self.mastfot else [It("06d", "06d", t=(0, 0, 40))])
        it += [It("05b", "05b", t=(0, 0, 80)), It("05", "05", t=(0, 0, 112))]
        it += [It(f"C#{i}", "C", (i,), t=add((0, 0, 112), polar3(26, a, 0))) for i, a in enumerate(p.stopp_vinklar)]
        mod = hx(125, 60)
        it += [It(k, k, t=mod) for k in self.MOD] + [It("08", "08", t=add(mod, (0, 0, 40)))]
        man = hx(-118, 0)
        it += [It("04", "04", t=man), It("10", "10", t=add(man, (0, 0, 42)))]
        sc = Scene("oversikt", it, defl=0.06)
        res = self.hlr(sc)
        ramme = (34, 38, 176, 280)
        k = fit_skala(res, ramme)
        f2 = figur(res, ramme, k)
        f3 = self.f3(sc, f2)
        s.teikning(res, f2, ny=set(res))
        for (lab, mot, h, off, bs) in (("01", (-1, 0), 0.5, None, False), ("D", (-1, 0), 0.5, (-12, 6), True),
                                       ("03", (-1, 0), 0.75, None, False), ("05b", (-1, 0), 0.5, (-14, 0), False),
                                       ("05", (-1, 0), 0.5, None, False), ("07", (1, 0), 0.6, (14, 0), False),
                                       ("06", (1, 0), 0.92, (16, 4), False), ("08", (1, 0), 0.5, None, False),
                                       ("04", (-1, 0), 0.5, None, False), ("10", (-1, 0), 0.5, None, False),
                                       ("C", (1, 0), 0.5, (8, -10), True), ("E", (1, 0), 0.5, (14, 2), True),
                                       ("F", (1, 0), 0.3, (16, -6), True), ("06d", (1, 0), 0.5, (14, 6), False),
                                       ("G", (1, 0), 0.5, (16, 2), True)):
            self.merk(s, res, f2, lab, mot=mot, h=h, off=off, beslag=bs)
        self.logg(s, None, "oversikt", sc, k)

    # ------------------------------------------------------------------ steg 1-5: chassis og fot
    def gruppe_skala(self, scener, ramme):
        return min(fit_skala(self.hlr(sc), ramme) for sc in scener)

    def scener_A(self):
        p = self.p
        E1 = 24.0
        sc1 = Scene("s01_innsatsar", [It("03", "03")] + [It(f"B#{i}", "B", (a,), t=(0, 0, -E1), ny=True) for i, a in enumerate(p.skrue_vinklar)]
                    + [It("L", "lodd", (polar3(p.skrue_r, p.skrue_vinklar[0], p.z_fot_1 - E1), (0, 0, -1), (1, 0, 0)))], G="snu")
        sw_ut, sw_ned = 30.0, 12.0
        it2 = [It("03", "03"), It("13", "13")] + [It(f"E#{i}", "E", (i,), t=add(polar3(sw_ut, a, 0), (0, 0, -sw_ned)), ny=True)
                                                  for i, (a, _t) in enumerate(p.sw)]
        if not self.mastfot:
            it2 += [It("06d", "06d", t=polar3(82, 175, 0), ny=True)]
        sc2 = Scene("s03_brytarar", it2)
        itk = [It("03", "03")] + self.elektronikk(kort=False) + [It("14", "14", t=self.KORT_UT, ny=True)]
        sck = Scene("s04_kort", itk, N=BAK)
        E3 = 46.0
        sc3 = Scene("s05_kabel", [It("01", "01"), It("03", "03", t=(0, 0, E3))] + self.elektronikk(t=(0, 0, E3))
                    + [It("F", "F", (E3,), ny=True)] + ([] if self.mastfot else [It("06d", "06d", t=(0, 0, E3))]), N=BAK)
        EA = 26.0
        it4 = self.basis(oring=False) + [It(f"A#{i}", "A", (a,), t=(0, 0, -EA), ny=True) for i, a in enumerate(p.skrue_vinklar)]
        a0 = p.skrue_vinklar[0]
        it4.append(It("N", "nokkel", (2.0, polar3(p.skrue_r, a0, p.z_fot_0 + 2.2 - 1.65 + 0.9 - EA), (0, 0, -1), (1, 0, 0))))
        sc4 = Scene("s06_skruar", it4, G="snu")
        it5 = self.basis(skruar=True, oring=False) + [It("D", "Dt", t=(0, 0, -22), ny=True)]
        sc5 = Scene("s07_oring", it5, G="snu")
        return {"innsatsar": sc1, "brytarar": sc2, "kort": sck, "kabel": sc3, "skruar": sc4, "oring": sc5}

    RAMME = (14, 44, 196, 272)
    KORT_UT = (-30.0, -62.0, 16.0)      # kortet kjem inn gjennom opninga mellom søylene bak til venstre (sett bakfrå)
    N_JACK = (math.cos(14 * DEG), math.sin(14 * DEG), 0.30)   # mellom søylene framme, under toppdekket

    def s1_innsatsar(self):
        p = self.p
        scs = self.scener_A()
        self._skala_A = self.gruppe_skala(list(scs.values()), self.RAMME)
        sc = scs["innsatsar"]
        s = self.ny_side("s01-innsatsar")
        self.steghovud(s, self.STEG["innsatsar"], "Innpressmutrar")
        res = self.hlr(sc)
        k = self._skala_A
        f2 = figur(res, self.RAMME, k)
        f3 = self.f3(sc, f2)
        s.teikning(res, f2, ny={"B", "L"})
        E1 = 24.0
        for i, a in enumerate(p.skrue_vinklar):
            top = f3(polar3(p.skrue_r, a, p.z_fot_1 - E1))
            bot = f3(polar3(p.skrue_r, a, p.z_fot_1))
            s.strek(top, bot)
        a0 = p.skrue_vinklar[2]
        s.hol_pil([f3(polar3(p.skrue_r + 13, a0, p.z_fot_1 - E1 + 2)), f3(polar3(p.skrue_r + 13, a0, p.z_fot_1 - 2))])
        self.merk(s, res, f2, "B", mot=(-1, 0), h=0.5, off=(-14, -6), beslag=True)
        self.merk(s, res, f2, "03", mot=(-1, 0), h=0.7)
        s.snu_ikon(16, 50)
        self.beslagboks(s, [("beslag", "B", self.ikon("B"), 3), ("verktoy", "loddebolt", self.ikon("lodd"), None)])
        self.logg(s, self.STEG["innsatsar"], "innpressmutrar B i chassisflensen nedanfrå", sc, k,
                  [{"type": "innføring", "delar": ["B#0", "B#1", "B#2"], "vektor_modell": [0, 0, 1], "lengd_mm": E1}],
                  "Chassiset ligg opp ned. Loddebolten pressar mutrane ned i hola til dei er i flukt.")

    def s_jack(self):
        p = self.p
        s = self.ny_side("s02-jack")
        self.steghovud(s, self.STEG["jack"], "Jack i navet")
        zd0, zd1 = p.dekk_z, p.dekk_z + p.dekk_t
        EJ, EM = 9.0, 7.0
        sc = Scene("s02_jack", [It("03", "03"), It("13k", "jack_kropp", t=(0, 0, -EJ), ny=True),
                                It("13m", "jack_mutter", t=(0, 0, EM), ny=True)], N=self.N_JACK)
        res = self.hlr(sc)
        ramme = (14, 44, 196, 272)
        k = fit_skala(res, ramme)
        f2 = figur(res, ramme, k)
        f3 = self.f3(sc, f2)
        s.teikning(res, f2, ny={"13k", "13m"})
        # kroppen opp nedanfrå gjennom holet, mutteren ned ovanfrå
        s.strek(f3((0, 0, zd0 - EJ)), f3((0, 0, zd0)))
        s.strek(f3((0, 0, zd1 + EM)), f3((0, 0, zd1 + 2)))
        ax = -9.5
        s.hol_pil([f3((0, ax, zd0 - EJ - 9)), f3((0, ax, zd0 - 1.5))], w=2.0, hw=5.2, hl=4.2)
        s.hol_pil([f3((0, ax, zd1 + EM + 9)), f3((0, ax, zd1 + 3.5))], w=2.0, hw=5.2, hl=4.2)
        self.merk(s, res, f2, "13k", tekst="13", mot=(-1, 0), h=0.6, off=(-26, 10))
        s.snu_ikon(16, 46)        # chassiset låg opp ned i steg 1: snu det rett veg
        # detalj: fastnøkkelen på mutteren, frå sida mellom søylene
        zm = zd1 + 0.95
        c = (0.0, 0.0, zm)
        dsc = Scene("d02_nokkel", [It("03", "03"), It("13", "13"),
                                   It("W", "fast8", ((0.0, 0.0, zm), (math.cos(-25 * DEG), math.sin(-25 * DEG), 0.0)), ny=True)],
                    N=self.N_JACK, region={"c": c, "h": 22}, defl=0.01)
        f3d = self.detalj(s, dsc, c, 17.0, (160, 236), 30, ny={"W"}, tekst="8 mm, frå sida")
        bue = [f3d(polar3(13.5, 70 - t, zm + 1.6)) for t in range(0, 71, 5)]
        s.hol_pil(bue, w=1.6, hw=4.2, hl=3.4)
        self.beslagboks(s, [("del", "13", self.ikon("13"), 1), ("verktoy", "8 mm", self.ikon("f8"), None)])
        self.logg(s, self.STEG["jack"], "TRS-kontakten 13 opp nedanfrå gjennom holet Ø6,2 i navet, M6-mutteren oppå, trekk til med 8 mm fastnøkkel frå sida",
                  sc, k, [{"type": "innføring", "delar": ["13k"], "vektor_modell": [0, 0, 1], "lengd_mm": EJ},
                          {"type": "innføring+skru", "delar": ["13m"], "vektor_modell": [0, 0, -1], "lengd_mm": EM}],
                  "Snu-ikonet: chassiset låg opp ned i steg 1 og blir snudd rett veg att. "
                  "Mutteren blir nådd mellom søylene framme, under toppdekket. Mastfoten kviler seinare på mutteren.")

    def s2_brytarar(self):
        p = self.p
        sc = self.scener_A()["brytarar"]
        s = self.ny_side("s03-brytarar")
        self.steghovud(s, self.STEG["brytarar"], "Brytarar")
        res = self.hlr(sc)
        k = self._skala_A
        ramme = (14, 44, 196, 205)
        f2 = figur(res, ramme, k)
        f3 = self.f3(sc, f2)
        s.teikning(res, f2, ny={"E", "06d"})
        sw_ut, sw_ned = 30.0, 12.0
        zt0 = p.z_toppdekk_0
        r0 = p.sw_r - 0.5
        iv = self.synlegaste([a for a, _t in p.sw])
        for i, (a, _t) in enumerate(p.sw):
            pa = polar3(r0 + sw_ut, a, zt0 - 3.2 - sw_ned)
            pb = polar3(r0, a, zt0 - 3.2 - sw_ned)
            pc = polar3(r0, a, zt0 - 3.2)
            s.strek(f3(pa), f3(pb))
            s.strek(f3(pb), f3(pc))
        a = p.sw[iv][0]
        s.hol_pil([f3(polar3(r0 + sw_ut - 2, a + 16, zt0 - 3.2 - sw_ned)), f3(polar3(r0 + 2, a + 16, zt0 - 3.2 - sw_ned)),
                   f3(polar3(r0 + 2, a + 16, zt0 - 4.0))])
        namn = [q.split()[0] for q in p.sw_namn]
        for i in range(len(p.sw)):
            q = self.ank(res, f2, f"E#{i}", mot=(-1, 0), h=0.5)
            if q is None:
                continue
            mot = -1 if q[0] < 105 else 1
            self.merk(s, res, f2, f"E#{i}", tekst=namn[i], mot=(mot, 0), h=0.4, off=(mot * 13, -9), beslag=True)
        if not self.mastfot:
            self.merk(s, res, f2, "06d", mot=(1, 0), h=0.5, off=(12, 8))
            s.hol_pil([f3(polar3(78, 175, p.dekk_z + 9)), f3(polar3(48, 175, p.dekk_z + 9))])
        # detalj: armen opp gjennom toppdekket (snitt gjennom den synlegaste brytaren)
        c = polar3(p.sw_r, a, zt0 + 1)
        dsc = Scene("d03_brytar", [It("03", "03"), It(f"E#{iv}", "E", (iv,), ny=True)], N=(math.sin(a * DEG), -math.cos(a * DEG), 0.0),
                    kutt={"type": "snitt", "az": a}, region={"c": c, "h": 16}, defl=0.01)
        self.detalj(s, dsc, c, 9.0, (165, 168), 26, main=(f3, polar3(p.sw_r, a, zt0 + 2), 5), ny={f"E#{iv}"}, tekst="armen opp i slissa")
        # detalj: festet J, plansnitt gjennom skrueaksen sett ovanfrå (radielt ut mot høgre)
        JU, JI = 7.0, 5.0
        ar = a * DEG
        rr, tt = (math.cos(ar), math.sin(ar), 0.0), (-math.sin(ar), math.cos(ar), 0.0)
        lok = lambda x, y: add(add(mul(rr, p.sw_r + x), mul(tt, y)), (0.0, 0.0, p.sw_hol_z))
        cj = lok(0.0, -3.6)
        dsc = Scene("d03_feste", [It("03", "03"), It(f"E#{iv}", "E", (iv,))] + self.brytarfeste(brytarar=[iv], ut=JU, inn=JI, ny=True),
                    N=(0.0, 0.0, 1.0), X=rr, kutt={"type": "over", "z": p.sw_hol_z + 0.02}, region={"c": cj, "h": 14}, defl=0.005)
        f3j = self.detalj(s, dsc, cj, 12.5, (165, 238), 22, ny={"J"})
        for y_h in (-6.85, -0.35):
            s.strek(f3j(lok(2.9 + JU, y_h)), f3j(lok(-6.6 - JI, y_h)))
        s.tekst(165, 265, "J utanfrå, mutter innanfor", 3.2, "normal", "middle")
        s.tekst(165, 270, f"lett til: blir justert i steg {self.STEG['juster']}", 3.2, "normal", "middle")
        # kart ovanfrå: kvar brytar står
        self.brytarkart(s, 60, 246, 22)
        boks = [("beslag", "E", self.ikon("E"), 3), ("beslag", "J", self.ikon("J"), 6), ("verktoy", "PH0", self.ikon("ph0"), None)]
        if not self.mastfot:
            boks.append(("del", "06d", self.ikon("06d"), 1))
        self.beslagboks(s, boks)
        self.logg(s, self.STEG["brytarar"], "tre mikrobrytarar E under toppdekket, kvar med 2 x J (M2 x 10 utanfrå, skive og mutter innanfor); "
                  "SW1 og SW3 gull (D2F-01L3), SW2 sølv (D2F-L3)", sc, k,
                  [{"type": "innføring", "delar": [f"E#{i}" for i in range(3)], "bane_modell": ["radielt inn", "opp"], "lengd_mm": [sw_ut, sw_ned]},
                   {"type": "innføring+skru", "delar": ["J"], "vektor_modell": "radielt inn (skrue), radielt ut (mutter)", "detalj": "d03_feste"}],
                  "Armane går opp gjennom slissene i toppdekket. Asimut (SW1, SW2, SW3): "
                  + ", ".join(f"{fmt(a_)}°" for a_, _t in p.sw)
                  + f". J blir berre skrudd lett til: braketten har loddrette spor (± {fmt(p.sw_just)} mm), brytarane blir justerte i steg {self.STEG['juster']}.")

    def brytarkart(self, s, cx, cy, R):
        """Chassiset sett ovanfrå, framme (spaltene, asimut 0) ned: kvar brytar står og kva type."""
        p = self.p
        s.sirkel(cx, cy, R, W_NY_O)
        s.sirkel(cx, cy, R * 0.55, W_KT_S)
        pt = lambda a, r: (cx + r * math.sin(a * DEG), cy + r * math.cos(a * DEG))
        typar = ["gull", "sølv", "gull"]
        for i, ((a, _t), nm) in enumerate(zip(p.sw, p.sw_namn)):
            x, y = pt(a, R * 0.84)
            s.rekt(x - 2.2, y - 2.2, x + 2.2, y + 2.2, W_KT_O, "#000")
            lx, ly = pt(a, R + 9)
            anker = "end" if lx < cx - 3 else ("start" if lx > cx + 3 else "middle")
            s.tekst(lx, ly, nm.split()[0], 3.2, "bold", anker)
            s.tekst(lx, ly + 4.2, f"{nm.split()[1]} {typar[i]}", 2.7, "normal", anker)
        s.hol_pil([pt(0, R + 2), pt(0, R + 13)], w=1.4, hw=3.8, hl=3.0)
        s.tekst(cx, cy + R + 18, "framme", 3.0, "normal", "middle")
        s.tekst(cx, cy + 1, "ovanfrå", 2.6, "normal", "middle")

    def s_kort(self):
        p = self.p
        sc = self.scener_A()["kort"]
        s = self.ny_side("s04-kort")
        self.steghovud(s, self.STEG["kort"], "Kort og kopling")
        res = self.hlr(sc)
        k = self._skala_A
        ramme = (14, 40, 196, 196)
        f2 = figur(res, ramme, k)
        f3 = self.f3(sc, f2)
        s.teikning(res, f2, ny={"14"})
        zd1 = p.dekk_z + p.dekk_t
        mal = (-25.5, 0.0, zd1 + 1)
        s.strek(f3(add(mal, self.KORT_UT)), f3(mal))
        a, b = add(mal, mul(self.KORT_UT, 0.85)), add(mal, mul(self.KORT_UT, 0.25))
        s.hol_pil([f3(add(a, (0, 0, 9))), f3(add(b, (0, 0, 9)))])
        self.merk(s, res, f2, "14", mot=(-1, 0), h=0.5, off=(-16, 6))
        s.auge_ikon(16, 52, "sett bakfrå")
        self.koplingsskjema(s, 14, 204, 182, 74)
        self.beslagboks(s, [("del", "14", self.ikon("14"), 1), ("verktoy", "loddebolt", self.ikon("lodd"), None)])
        self.logg(s, self.STEG["kort"], "kortet 14 på armen bak på elektronikkdekket, lodd brytarane og jacken etter skjemaet", sc, k,
                  [{"type": "innføring", "delar": ["14"], "vektor_modell": [-c for c in self.KORT_UT]}],
                  "Kamera sett bakfrå. Tre parallelle greiner frå +5 V etter F1: SW1-R1-TOPP, SW3-R3-TOPP, SW2-SIDE. Inga hovudbrytar.")

    def koplingsskjema(self, s, x0, y0, w, h):
        """Tre parallelle greiner frå +5 V etter F1 (PTC): SW1 -> R1 -> TOPP, SW3 -> R3 -> TOPP, SW2 -> SIDE. Inga hovudbrytar."""
        p = self.p
        s.rekt(x0, y0, x0 + w, y0 + h, W_FIN, rx=2)
        y1, y3, y2 = y0 + 15, y0 + 31, y0 + 47      # greinene SW1, SW3, SW2
        yb = y0 + h - 9

        def sw(x, y, lab, sub):
            s.linje([(x - 6, y), (x - 2.5, y)], W_KT_O)
            s.sirkel(x - 2.5, y, 0.6, W_KT_O)
            s.sirkel(x + 2.5, y, 0.6, W_KT_O)
            s.linje([(x - 2.0, y - 0.4), (x + 2.6, y - 3.2)], W_KT_O)
            s.linje([(x + 2.5, y), (x + 6, y)], W_KT_O)
            s.tekst(x, y - 5, lab, 2.8, "bold", "middle")
            s.tekst(x, y + 4.6, sub, 2.3, "normal", "middle")

        def mot(x, y, lab):
            s.rekt(x, y - 1.8, x + 12, y + 1.8, W_KT_O, "#fff")
            s.tekst(x + 6, y - 3.2, lab, 2.5, "normal", "middle")

        def prikk(x, y):
            s.el.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="0.85" fill="#000"/>')

        # USB
        s.rekt(x0 + 5, y1 - 5, x0 + 19, yb + 3, W_KT_O)
        s.tekst(x0 + 12, y1 - 7, "USB", 2.8, "bold", "middle")
        s.tekst(x0 + 12, y1 + 1, "5 V", 2.8, "normal", "middle")
        s.tekst(x0 + 12, yb + 1, "0 V", 2.8, "normal", "middle")
        # F1
        s.linje([(x0 + 19, y1), (x0 + 25, y1)], W_KT_O)
        s.rekt(x0 + 25, y1 - 2, x0 + 36, y1 + 2, W_KT_O, "#fff")
        s.linje([(x0 + 26, y1 + 2), (x0 + 35, y1 - 2)], W_FIN)
        s.tekst(x0 + 30.5, y1 - 3.6, "F1", 2.8, "bold", "middle")
        s.tekst(x0 + 30.5, y1 + 6.2, "PTC 0,5 A", 2.3, "normal", "middle")
        xn = x0 + 46
        s.linje([(x0 + 36, y1), (xn, y1)], W_KT_O)
        s.linje([(xn, y1), (xn, y2)], W_KT_O)
        for y in (y1, y3, y2):
            prikk(xn, y)
        tersk = {i: p.sw[i][1] - getattr(p, "kam_rampe", 0.0) / 2 for i in range(3)}
        lukka = lambda i: f"lukka 0–{fmt(round(tersk[i]))}°"
        xs, xr, xj = x0 + 60, x0 + 76, x0 + 104
        # grein 1 og 3: SW -> R -> TOPP
        for (y, i, rlab) in ((y1, 0, "R1 91 Ω"), (y3, 2, "R3 33 Ω")):
            s.linje([(xn, y), (xs - 6, y)], W_KT_O)
            sw(xs, y, ["SW1 gull", "SW2 sølv", "SW3 gull"][i], lukka(i))
            s.linje([(xs + 6, y), (xr, y)], W_KT_O)
            mot(xr, y, rlab)
            s.linje([(xr + 12, y), (xj, y)], W_KT_O)
        s.linje([(xj, y1), (xj, y3)], W_KT_O)
        prikk(xj, y1)
        s.linje([(xj, y1), (x0 + 128, y1)], W_KT_O)
        # grein 2: SW2 -> SIDE
        s.linje([(xn, y2), (xs - 6, y2)], W_KT_O)
        sw(xs, y2, "SW2 sølv", lukka(1))
        s.linje([(xs + 6, y2), (x0 + 128, y2)], W_KT_O)
        # 0 V
        s.linje([(x0 + 19, yb), (x0 + 128, yb)], W_KT_O)
        # X1 = jacken 13
        s.rekt(x0 + 128, y1 - 4, x0 + 140, yb + 4, W_KT_O)
        s.tekst(x0 + 134, y1 - 6, "13", 2.8, "bold", "middle")
        for yy, lab in zip((y1, y2, yb), ("tupp  TOPP+", "ring  SIDE+", "hylse  GND")):
            s.sirkel(x0 + 134, yy, 1.1, W_KT_O, "#fff")
            s.linje([(x0 + 140, yy), (x0 + 148, yy)], W_KT_O)
            s.tekst(x0 + 150, yy + 1, lab, 2.6)
        s.tekst(x0 + 150, y1 - 7, "06d plugg" if self.mastfot else "06", 2.6, "bold")
        s.tekst(x0 + 134, yb + 7.5, "jack 3,5 mm", 2.3, "normal", "middle")

    def s3_kabel(self):
        p = self.p
        sc = self.scener_A()["kabel"]
        s = self.ny_side("s05-kabel")
        self.steghovud(s, self.STEG["kabel"], "Kabel")
        res = self.hlr(sc)
        k = self._skala_A
        f2 = figur(res, self.RAMME, k)
        f3 = self.f3(sc, f2)
        s.teikning(res, f2, ny={"F"})
        R = p.fot_d / 2
        E3 = 46.0
        s.hol_pil([f3((-R - 34, 9, p.kabel_z + 8)), f3((-R - 6, 9, p.kabel_z + 8))])
        s.hol_pil([f3((p.kabel_ut_x - 10, -14, p.z_fot_1 + 6)), f3((p.kabel_ut_x - 10, -14, p.z_fot_1 + E3 - 6))])
        s.hol_pil([f3(polar3(p.chassis_r + 8, 230, p.z_fot_1 + E3 + 34)), f3(polar3(p.chassis_r + 8, 230, p.z_fot_1 + E3 + 8))])
        self.merk(s, res, f2, "F", mot=(-1, 0), h=0.9, off=(-4, 14), beslag=True)
        s.auge_ikon(16, 52, "sett bakfrå")
        # detalj ovanfrå: S-en rundt dei tre stolpane i lomma (chassiset er teke vekk)
        c = (-20.0, 0.0, p.kabel_z)
        dsc = Scene("d05_stolpar", [It("01", "01"), It("F", "F", (0.0,), ny=True)], N=(0.12, 0.05, 1), X=(0, -1, 0),
                    kutt={"type": "over", "z": p.z_fot_1 - 0.3}, region={"c": c, "h": 17}, defl=0.01)
        f3d = self.detalj(s, dsc, c, 13.0, (160, 228), 32, main=(f3, (-20.0, 0, p.z_fot_1), 7), ny={"F"})
        # stolpane P1, P2, P3: namnet på den sida av stolpen kabelen ikkje går
        for j, (sx, sy) in enumerate(p.stolpe_pos):
            q = f3d((sx, sy + math.copysign(3.4, sy), p.stolpe_topp))
            s.tekst(q[0], q[1] + 1.0, f"P{j + 1}", 2.8, "bold", "middle")
        s.tekst(160, 266, "ovanfrå: under P1, over P2, under P3", 3.2, "normal", "middle")
        s.tekst(160, 271, "kappa sluttar etter P3", 3.2, "normal", "middle")
        self.beslagboks(s, [("beslag", "F", self.ikon("F"), 1)])
        self.logg(s, self.STEG["kabel"], "kabel F inn bak i foten, S rundt stolpane P1, P2, P3 i lomma, leiarane opp gjennom flensen til kortet; set chassiset ned", sc, k,
                  [{"type": "innføring", "delar": ["F"], "vektor_modell": [1, 0, 0]}, {"type": "innføring", "delar": ["F"], "vektor_modell": [0, 0, 1]},
                   {"type": "innføring", "delar": ["03"], "vektor_modell": [0, 0, -1], "lengd_mm": E3}],
                  "Kamera sett bakfrå. Kabelen går under P1, over P2 og under P3 (S, glipe 4,2), kappa sluttar etter P3, leiarane går opp "
                  f"gjennom holet Ø7 på ({fmt(p.kabel_ut_x)}, 0) og rundt armen bak til JST-pluggen på kortet. Bogetappen under flensen "
                  "(210..510°) sentrerer chassiset og står ikkje over kabelen.")

    def s4_skruar(self):
        p = self.p
        sc = self.scener_A()["skruar"]
        s = self.ny_side("s06-skruar")
        self.steghovud(s, self.STEG["skruar"], "Skru fast chassiset")
        res = self.hlr(sc)
        k = self._skala_A
        f2 = figur(res, self.RAMME, k)
        f3 = self.f3(sc, f2)
        s.teikning(res, f2, ny={"A", "N"})
        EA = 26.0
        zc = p.z_fot_0 + 2.2
        for i, a in enumerate(p.skrue_vinklar):
            s.strek(f3(polar3(p.skrue_r, a, zc - EA)), f3(polar3(p.skrue_r, a, zc)))
        a1 = p.skrue_vinklar[2]
        s.hol_pil([f3(polar3(p.skrue_r + 13, a1, zc - EA + 6)), f3(polar3(p.skrue_r + 13, a1, zc - 2))])
        self.merk(s, res, f2, "A", mot=(-1, 0), h=0.5, off=(-14, -6), beslag=True)
        s.snu_ikon(16, 50)
        self.beslagboks(s, [("beslag", "A", self.ikon("A"), 3), ("verktoy", "2 mm", self.ikon("n20"), None)])
        self.logg(s, self.STEG["skruar"], "snu, skru foten til chassiset med 3 x A", sc, k,
                  [{"type": "innføring+skru", "delar": ["A#0", "A#1", "A#2"], "vektor_modell": [0, 0, 1], "lengd_mm": EA}])

    def s5_oring(self):
        p = self.p
        sc = self.scener_A()["oring"]
        s = self.ny_side("s07-oring")
        self.steghovud(s, self.STEG["oring"], "O-ring")
        res = self.hlr(sc)
        k = self._skala_A
        f2 = figur(res, self.RAMME, k)
        f3 = self.f3(sc, f2)
        s.teikning(res, f2, ny={"D"})
        rm = p.oring_id / 2 + p.oring_snor / 2
        s.hol_pil([f3(polar3(p.fot_d / 2 + 10, V_ISO + 180 + 50, -22 + 6)), f3(polar3(p.fot_d / 2 + 10, V_ISO + 180 + 50, p.z_fot_0 - 3))])
        self.merk(s, res, f2, "D", mot=(-1, 0), h=0.5, off=(-14, -8), beslag=True)
        # inkje snu-ikon: lampa ligg alt opp ned etter steg 6 (same stilling)
        # detalj: snitt, ringen står 1 mm ut
        a = 90.0
        c = polar3(rm, a, p.z_fot_0 + 1)
        dsc = Scene("d07_oring", [It("01", "01"), It("D", "Dt", ny=True)], N=(math.sin(a * DEG), -math.cos(a * DEG), 0.0),
                    kutt={"type": "snitt", "az": a}, region={"c": c, "h": 12}, defl=0.01)
        self.detalj(s, dsc, c, 6.5, (162, 236), 26, ny={"D"}, tekst=f"{fmt(p.fot_loft)} mm luft")
        self.beslagboks(s, [("beslag", "D", self.ikon("D"), 1)])
        self.logg(s, self.STEG["oring"], "O-ringen D i sporet under foten", sc, k, [{"type": "innføring", "delar": ["D"], "vektor_modell": [0, 0, 1], "lengd_mm": 22}],
                  "Lampa ligg framleis opp ned frå steg 6, difor inkje snu-ikon.")

    # ------------------------------------------------------------------ steg 6-9: mantel og hylse
    def s6_glidering(self):
        p = self.p
        E = 44.0
        sc = Scene("s08_glidering", [It("04", "04"), It("10", "10", t=(0, 0, E), ny=True)])
        s = self.ny_side("s08-glidering")
        self.steghovud(s, self.STEG["glidering"], "Glidering i mantelen")
        res = self.hlr(sc)
        ramme = (40, 44, 170, 272)
        k = fit_skala(res, ramme)
        f2 = figur(res, ramme, k)
        f3 = self.f3(sc, f2)
        s.teikning(res, f2, ny={"10"})
        s.hol_pil([f3(polar3(p.r_mo + 9, V_ISO, p.z_glide_1 + E - 4)), f3(polar3(p.r_mo + 9, V_ISO, p.z_mantel_1 + 3))])
        self.merk(s, res, f2, "10", mot=(1, 0), h=0.5, off=(14, -4))
        self.merk(s, res, f2, "04", mot=(1, 0), h=0.6, off=(14, 0))
        a = 90.0
        c = polar3(p.r_mi, a, p.z_glide_1 - 2)
        dsc = Scene("d08_glide", [It("04", "04"), It("10", "10", ny=True)], N=(math.sin(a * DEG), -math.cos(a * DEG), 0.0),
                    kutt={"type": "snitt", "az": a}, region={"c": c, "h": 12}, defl=0.01)
        self.detalj(s, dsc, c, 6.0, (170, 200), 24, main=(f3, polar3(p.r_mo, V_ISO + 30, p.z_mantel_1 - 3), 5), ny={"10"},
                    tekst=f"{fmt(p.glide_under_kant)} mm under kanten")
        s.tekst(170, 238, f"prototype: lim med CA, sjå side {sideref('prototype')}", 3.0, "normal", "middle")
        self.beslagboks(s, [("del", "10", self.ikon("10"), 1)])
        self.logg(s, self.STEG["glidering"], "press gliderringen 10 inn øvst i mantelen", sc, k, [{"type": "innføring", "delar": ["10"], "vektor_modell": [0, 0, -1], "lengd_mm": E}],
                  f"Prototypen: gliderringen blir limt med CA i toppen av mantelen (side {sideref('prototype')}).")

    def scener_B(self):
        p = self.p
        base = self.basis(skruar=False)
        sc7 = Scene("s09_fotring", [It("05", "05"), It("05b", "05b", t=(0, 0, -34), ny=True)])
        sc8 = Scene("s10_hylse", base + self.hylse_sett(dz=70, ny=True, skruar=False))
        EC = 24.0
        cs = [It(f"C#{i}", "C", (i,), t=polar3(EC, a, 0), ny=True) for i, a in enumerate(p.stopp_vinklar)]
        a0 = p.stopp_vinklar[0]
        rs = getattr(p, "r_stopp_sete", p.r_ho - 1.0) + getattr(p, "stopp_hovud_h", 0.0)
        cn, _n, _t = self.c_beskriving
        dkey = 2.0 if hasattr(p, "stopp_hovud_d") else 1.5
        key = It("N", "nokkel", (dkey, polar3(rs + EC + 0.3 - 1.0, a0, p.stopp_z), polar3(1, a0, 0), (0, 0, 1)))
        sc9 = Scene("s11_stoppskruar", base + self.hylse_sett(skruar=False) + cs + [key])
        return sc7, sc8, sc9

    def s7_fotring(self):
        p = self.p
        sc7, sc8, sc9 = self.scener_B()
        ramme = self.RAMME
        self._skala_B = self.gruppe_skala([sc8, sc9], ramme)
        s = self.ny_side("s09-fotring")
        self.steghovud(s, self.STEG["fotring"], "Fotring i hylsa")
        res = self.hlr(sc7)
        k = fit_skala(res, (40, 44, 170, 272))
        f2 = figur(res, (40, 44, 170, 272), k)
        f3 = self.f3(sc7, f2)
        s.teikning(res, f2, ny={"05b"})
        s.hol_pil([f3(polar3(p.r_ho + 10, V_ISO, p.toppdekk_z1 - 30)), f3(polar3(p.r_ho + 10, V_ISO, p.toppdekk_z1 + 4))])
        a0 = p.stopp_vinklar[0]
        s.strek(f3(polar3(p.r_ho, a0, p.stopp_z)), f3(polar3(p.r_hi, a0, p.stopp_z - 34)))
        self.merk(s, res, f2, "05b", mot=(1, 0), h=0.5, off=(16, -4))
        self.merk(s, res, f2, "05", mot=(1, 0), h=0.4, off=(16, 0))
        # detalj: hola skal liggje over kvarandre
        c = polar3(p.r_ho, a0, p.stopp_z)
        N = add(polar3(1, a0, 0), (0, 0, 0.25))
        dsc = Scene("d09_hol", [It("05", "05"), It("05b", "05b", ny=True)], N=N, region={"c": c, "h": 12}, defl=0.01)
        self.detalj(s, dsc, c, 6.0, (42, 236), 26, main=(f3, polar3(p.r_ho, a0, p.stopp_z), 5), ny={"05b"}, tekst="hol mot hol ×3")
        self.beslagboks(s, [("del", "05b", self.ikon("05b"), 1)])
        self.logg(s, self.STEG["fotring"], "fotringen 05b inn nedanfrå i hylserøyret 05, hola for C rett over kvarandre", sc7, k,
                  [{"type": "innføring", "delar": ["05b"], "vektor_modell": [0, 0, 1], "lengd_mm": 34}],
                  "Seriegeometri. I prototypen er 05 og 05b prenta i eitt, steget fell bort.")

    def s8_hylse_ned(self):
        p = self.p
        sc7, sc8, sc9 = self.scener_B()
        s = self.ny_side("s10-hylse")
        self.steghovud(s, self.STEG["hylse"], "Hylsa på tappen")
        res = self.hlr(sc8)
        k = self._skala_B
        f2 = figur(res, self.RAMME, k)
        f3 = self.f3(sc8, f2)
        s.teikning(res, f2, ny={"05", "05b"})
        s.hol_pil([f3(polar3(p.r_ho + 12, V_ISO + 100, p.toppdekk_z1 + 62)), f3(polar3(p.r_ho + 12, V_ISO + 100, p.toppdekk_z1 + 6))])
        # porten mot framsida (spaltene): pil på bordet frå senter mot +X
        s.hol_pil([f3((p.fot_d / 2 + 6, 0, p.z_fot_0)), f3((p.fot_d / 2 + 26, 0, p.z_fot_0))], w=1.8, hw=4.8, hl=3.8)
        qq = f3((p.fot_d / 2 + 30, 0, p.z_fot_0))
        s.tekst(qq[0] - 2, qq[1] + 6, "framme", 3.0, "normal", "middle")
        s.snu_ikon(16, 46)        # foten med chassiset låg opp ned i steg 6 og 7
        # detalj: klikk (plan, kutt over tappen)
        a = p.tunge_vinklar[0]
        c = polar3(p.tapp_ro, a - 2, p.klikk_z0 + 2.6)
        dsc = Scene("d10_klikk", [It("03", "03"), It("05b", "05b", ny=True)], N=(0, 0, 1), X=(-math.sin(a * DEG), math.cos(a * DEG), 0),
                    kutt={"type": "over", "z": p.klikk_z0 + 2.6}, region={"c": c, "h": 9}, defl=0.005)
        self.detalj(s, dsc, c, 4.0, (165, 236), 26, main=(f3, polar3(p.tapp_ro, a, p.toppdekk_z1 + 3), 5), ny={"05b"}, tekst="klikk")
        self.beslagboks(s, [("del", "05", self.ikon("05"), 1)])
        self.logg(s, self.STEG["hylse"], "hylsa (05 med 05b) ned på tappen, porten mot spaltene (framme, +X)", sc8, k,
                  [{"type": "innføring", "delar": ["05", "05b"], "vektor_modell": [0, 0, -1], "lengd_mm": 70}],
                  "Snu-ikonet: foten med chassiset låg opp ned i steg 6 og 7 og blir snudd rett veg att.")

    def s9_stoppskruar(self):
        p = self.p
        sc7, sc8, sc9 = self.scener_B()
        s = self.ny_side("s11-stoppskruar")
        self.steghovud(s, self.STEG["stopp"], "Stoppskruar")
        res = self.hlr(sc9)
        k = self._skala_B
        f2 = figur(res, self.RAMME, k)
        f3 = self.f3(sc9, f2)
        s.teikning(res, f2, ny={"C", "N"})
        EC = 24.0
        rs = getattr(p, "r_stopp_sete", p.r_ho - 1.0)
        for i, a in enumerate(p.stopp_vinklar):
            s.strek(f3(polar3(rs + EC, a, p.stopp_z)), f3(polar3(rs, a, p.stopp_z)))
        a0 = p.stopp_vinklar[0]
        s.hol_pil([f3(polar3(rs + EC + 2, a0 - 14, p.stopp_z + 8)), f3(polar3(rs + 3, a0 - 14, p.stopp_z + 8))])
        self.merk(s, res, f2, "C", mot=(-1, 0), h=0.5, off=(-12, 10), beslag=True)
        # først: kragen på 0° (klikk 1), porten framme: då står hola i røyret over enden av sporet i tappen
        self.vri_ikon(s, 20, 50, "Vri kragen til klikk 1 (0°), porten framme, før skruane.", mot_klokka=True)
        s.hol_pil([f3((p.fot_d / 2 + 6, 0, p.z_fot_0)), f3((p.fot_d / 2 + 26, 0, p.z_fot_0))], w=1.8, hw=4.8, hl=3.8)
        qq = f3((p.fot_d / 2 + 30, 0, p.z_fot_0))
        s.tekst(qq[0] - 2, qq[1] + 6, "framme", 3.0, "normal", "middle")
        # detalj: snitt gjennom skruen
        c = polar3(p.tapp_ro + 1.5, a0, p.stopp_z)
        dsc = Scene("d11_skrue", [It("03", "03"), It("05", "05"), It("05b", "05b"), It("C#0", "C", (0,), ny=True)],
                    N=(math.sin(a0 * DEG), -math.cos(a0 * DEG), 0.0), kutt={"type": "snitt", "az": a0}, region={"c": c, "h": 14}, defl=0.006)
        self.detalj(s, dsc, c, 7.0, (164, 236), 27, main=(f3, polar3(p.r_ho, a0, p.stopp_z), 5), ny={"C#0"}, tekst="spissen i sporet")
        cdesc, cnok, cnok_t = self.c_beskriving
        s.tekst(164, 236 + 27 + 10, f"skruen skjer gjengene sjølv i Ø{fmt(p.stopp_kjerne_d)}", 3.0, "normal", "middle")
        self.beslagboks(s, [("beslag", "C", self.ikon("C"), 3), ("verktoy", cnok_t, self.ikon(cnok), None)])
        self.logg(s, self.STEG["stopp"], f"3 x C ({cdesc}) gjennom hylsa og fotringen, spissen i sporet i tappen", sc9, k,
                  [{"type": "innføring+skru", "delar": ["C#0", "C#1", "C#2"], "vektor_modell": "radielt inn", "lengd_mm": EC}],
                  f"Kragen står på 0° (klikk 1, porten framme) før skruane blir sette i: då står hola over enden av sporet. "
                  f"Gjengeformande M3: skruen skjer gjengene sjølv i kjerneholet Ø{fmt(p.stopp_kjerne_d)} i hylsefoten. "
                  "Skruane er endestopp (0° og 90°) og held hylsa nede.")

    def s_juster(self):
        """Juster brytarane mot fotringen: kragen på 0° (alle tre på flata), kvar brytar opp til han lukkar
        (kontinuitet), 0,6 mm til (armen på OP − 0,6), trekk til J. Spora i braketten gjev ± sw_just."""
        p = self.p
        s = self.ny_side("s12-juster")
        self.steghovud(s, self.STEG["juster"], "Juster brytarane")
        iv = self.synlegaste([a for a, _t in p.sw])
        a = p.sw[iv][0]
        ar = a * DEG
        rr, tt = (math.cos(ar), math.sin(ar), 0.0), (-math.sin(ar), math.cos(ar), 0.0)
        lok = lambda x, y, z: add(add(mul(rr, p.sw_r + x), mul(tt, y)), (0.0, 0.0, z))
        jarn = It("S", "skrujarn", (lok(2.9 + 1.6, -0.35, p.sw_hol_z), rr, (0.0, 0.0, 1.0)), ny=True)
        sc = Scene("s12_juster", self.basis(skruar=False) + self.hylse_sett() + [jarn])
        res = self.hlr(sc)
        k = min(self._skala_B, fit_skala(res, self.RAMME))
        f2 = figur(res, self.RAMME, k)
        f3 = self.f3(sc, f2)
        s.teikning(res, f2, ny={"S"})
        for i, (nr, t) in enumerate((("1", "Kragen på klikk 1 (0°)."),
                                     ("2", "Løys J. Skyv brytaren opp til multimeteret piper,"),
                                     ("", f"så {fmt(0.6)} mm til. Trekk til J."),
                                     ("3", "Same med dei to andre brytarane."))):
            s.tekst(13, 46 + 5.2 * i, nr, 3.2, "bold")
            s.tekst(19, 46 + 5.2 * i, t, 3.2)
        # multimeteret til venstre, leidningar til terminalane under brytaren
        msc = Scene("s12_multimeter", [It("M", "multimeter", (False,))], N=(0.35, -0.6, 1.0), defl=0.05)
        mres = self.hlr(msc)
        mramme = (16, 120, 50, 176)
        mk = fit_skala(mres, mramme)
        mf2 = figur(mres, mramme, mk)
        mf3 = self.f3(msc, mf2)
        s.teikning(mres, mf2, ny=set(mres))
        z_t = p.sw_hol_z - 1.5 - 1.0
        for (xj, yt) in ((-11.0, -8.5), (0.0, -1.0)):
            q0 = mf3((xj, -27.0, 14.0))
            q1 = f3(lok(0.0, yt, z_t))
            mid = ((q0[0] + q1[0]) / 2 + 6, max(q0[1], q1[1]) + 10)
            bez = [((1 - u) ** 2 * q0[0] + 2 * u * (1 - u) * mid[0] + u * u * q1[0],
                    (1 - u) ** 2 * q0[1] + 2 * u * (1 - u) * mid[1] + u * u * q1[1]) for u in [i / 24 for i in range(25)]]
            s.linje(bez, W_KT_O)
            s.el.append(f'<circle cx="{q1[0]:.2f}" cy="{q1[1]:.2f}" r="0.7" fill="#000"/>')
        qd = mf3((20.0, 18.0, 14.0))
        for j in range(3):     # pip
            rb = 2.2 + 1.8 * j
            s.linje([(qd[0] + 2 + rb * math.cos(t * DEG), qd[1] - 4 + rb * math.sin(t * DEG)) for t in range(-40, 41, 8)], W_KT_O)
        # detalj: snitt gjennom brytaren, armen mot undersida av fotringen
        c = polar3(p.sw_r, a, p.toppdekk_z1 - 2.0)
        dsc = Scene("d12_juster", [It("03", "03"), It("05b", "05b"), It(f"E#{iv}", "E", (iv,), ny=True)],
                    N=(math.sin(ar), -math.cos(ar), 0.0), kutt={"type": "snitt", "az": a}, region={"c": c, "h": 12}, defl=0.006)
        f3d = self.detalj(s, dsc, c, 8.0, (164, 232), 28, main=(f3, polar3(p.sw_r, a, p.toppdekk_z1 - 4), 5), ny={f"E#{iv}"})
        s.hol_pil([f3d(polar3(p.sw_r + 4.6, a, p.sw_hol_z)), f3d(polar3(p.sw_r + 4.6, a, p.sw_hol_z + 5.0))], w=1.6, hw=4.2, hl=3.2)
        s.tekst(164, 232 + 28 + 6, "armen mot fotringen:", 3.2, "normal", "middle")
        s.tekst(164, 232 + 28 + 11, f"opp til pip, så {fmt(0.6)} mm til", 3.2, "normal", "middle")
        self.beslagboks(s, [("verktoy", "PH0", self.ikon("ph0"), None), ("verktoy", "multimeter", self.ikon("multimeter"), None)])
        self.logg(s, self.STEG["juster"], "juster brytarane: kragen på 0°, kvar brytar opp til han lukkar (kontinuitet), 0,6 mm til, trekk til J", sc, k,
                  [{"type": "justering", "delar": [f"E#{i}" for i in range(len(p.sw))], "vektor_modell": [0, 0, 1],
                    "skildring": "opp til kontakt (pip), så 0,6 mm til: armen står på OP − 0,6 på flata og OP + 1,2 i utsparinga"}],
                  f"Kragen på 0°: alle tre brytarane står på flata under fotringen. Spora i braketten gjev ± {fmt(p.sw_just)} mm, "
                  f"kamdjupna er {fmt(p.kam_djup)} mm. Utan justeringa held ikkje tersklane i tilstandstabellen (steg {self.STEG['prov']}).")

    # ------------------------------------------------------------------ steg 10-13
    def scener_C(self):
        p = self.p
        base = self.basis()
        hyl = self.hylse_sett()
        EM = 150.0
        sc10 = Scene("s13_modul", base + hyl + self.modul(dz=EM, ny=True))
        sc11 = Scene("s14_prov", base + hyl + self.modul())
        EMa = 120.0
        # mantelen blir halden vridd +baj_vri (mot klokka) i høve til ferdig stilling: då står inngangen i L-sporet over knastane
        sc12 = Scene("s16_mantel", self.basis(snor=True) + hyl + self.modul()
                     + [It("04", "04", t=(0, 0, EMa), rz=p.baj_vri, ny=True), It("10", "10", t=(0, 0, EMa), rz=p.baj_vri, ny=True)])
        sc13 = Scene("s17_lok", self.heil(med_lok=False) + [It("08", "08", t=(0, 0, 46), ny=True)])
        ES = 24.0
        sc_snor = Scene("s15_snor", base + hyl + self.modul()
                        + [It(f"G#{i}", "G", (i,), t=(0, 0, ES), ny=True) for i in range(len(p.snor_vinklar))])
        return {"modul": sc10, "prov": sc11, "mantel": sc12, "lok": sc13, "snor": sc_snor}

    def s10_modul(self):
        p = self.p
        scs = self.scener_C()
        self._skala_C = self.gruppe_skala([scs["modul"], scs["mantel"]], self.RAMME)
        sc = scs["modul"]
        s = self.ny_side("s13-modul")
        self.steghovud(s, self.STEG["modul"], "Lysmodul")
        res = self.hlr(sc)
        k = self._skala_C
        f2 = figur(res, self.RAMME, k)
        f3 = self.f3(sc, f2)
        s.teikning(res, f2, ny=set(self.MOD))
        EM = 150.0
        s.hol_pil([f3(polar3(p.r_ho + 14, V_ISO + 90, p.z_hylse_1 + 80)), f3(polar3(p.r_ho + 14, V_ISO + 90, p.z_hylse_1 + 6))])
        self.merk(s, res, f2, "07", mot=(1, 0), h=0.35, off=(18, 0))
        self.merk(s, res, f2, "06", mot=(1, 0), h=0.9, off=(22, 6))
        if self.mastfot:
            self.merk(s, res, f2, "06d", mot=(-1, 0), h=0.5, off=(-16, 4))
        # framme-merke
        s.hol_pil([f3((p.fot_d / 2 + 6, 0, p.z_fot_0)), f3((p.fot_d / 2 + 26, 0, p.z_fot_0))], w=1.8, hw=4.8, hl=3.8)
        qq = f3((p.fot_d / 2 + 30, 0, p.z_fot_0))
        s.tekst(qq[0] - 2, qq[1] + 6, "framme", 3.0, "normal", "middle")
        # detalj: plan ovanfrå, kutta over toppdekket: staven i sokkelen og nøkkeltappen i holet framme (framme ned)
        nr = getattr(p, "nokkel_r", 18.0)
        c = (nr * 0.5, 0.0, p.toppdekk_z1)
        dsc = Scene("d13_tapp", [It("03", "03")] + ([] if self.mastfot else [It("06d", "06d")]) + self.modul(ny=True),
                    N=(0.0, 0.0, 1.0), X=(0.0, 1.0, 0.0),
                    kutt={"type": "over", "z": p.toppdekk_z1 + 1.5}, region={"c": c, "h": 24}, defl=0.01)
        self.detalj(s, dsc, c, 16.0, (166, 230), 28, main=(f3, (nr * 0.5, 0, p.toppdekk_z1), 7), ny=set(self.MOD))
        s.hol_pil([(166, 261), (166, 270)], w=1.6, hw=4.2, hl=3.2)
        s.tekst(176, 268, "framme", 3.0)
        s.tekst(166, 198, "ovanfrå: tappen framme", 3.2, "normal", "middle")
        # éin boks for heile modulen: han kjem ferdig samla og limt (06 + 06b + 06c + 07 + 06d, 2K-epoksy H11)
        self.beslagboks(s, [("modul", " + ".join(k for k in ("06", "07", "06d") if k in self.MOD), self.ikon("modul"), 1)], bw=44)
        s.tekst(198, 46, f"kjem ferdig samla, sjå side {sideref('lysmodul')}", 3.0, "normal", "end")
        self.logg(s, self.STEG["modul"], "lysmodulen (" + " + ".join(k for k in ("06", "07", "06d") if k in self.MOD) + ", ferdig samla) ned ovanfrå gjennom kragen, lamellane mot spaltene, trykk til pluggen sit", sc, k,
                  [{"type": "innføring", "delar": list(self.MOD), "vektor_modell": [0, 0, -1], "lengd_mm": EM}],
                  f"Modulen kjem ferdig samla (førmontering: side {sideref('lysmodul')}). Mastfoten ({fmt(p.mastfot_b)} × {fmt(p.mastfot_l)}) "
                  f"går ned gjennom gjennomgangen {fmt(p.mastfot_b + 0.6)} × {fmt(p.mastfot_l + 0.6)} i toppdekket, nøkkeltappen i holet framme "
                  f"før pluggen når kontakten; mastfoten kviler på mutteren til 13 (z {fmt(p.mastfot_z0)}). "
                  "Modulen må stå i sokkelen for funksjonsprøva. Mantelen går utanpå hylsa og rører ikkje modulen.")

    def tilstandar(self):
        p = self.p
        n = int(round(p.vandring / p.deling))
        halv_spalte = math.degrees(p.spalte_b / 2 / p.r_mo)
        rampe = getattr(p, "kam_rampe", 0.0)
        ut = []
        for k in range(n + 1):
            th = k * p.deling
            sw = []
            for (_a, t) in p.sw:
                if th >= t:
                    sw.append(False)
                elif th <= t - rampe:
                    sw.append(True)
                else:
                    sw.append(None)
            opne = sum(1 for a in p.vindauge_vinklar if abs(a + th) <= p.port_halv - halv_spalte)
            ut.append({"theta": th, "SW1": sw[0], "SW2": sw[1], "SW3": sw[2], "opne_spalter": opne})
        return ut

    @staticmethod
    def lys_tekst(d):
        """SW1 (via R1 91 Ω) og SW3 (via R3 33 Ω) ligg parallelt mot TOPP: SW3 lukka = full glød, berre SW1 = svak glød.
        SW2 ber SIDE (sidelys). Inga hovudbrytar."""
        if None in (d["SW1"], d["SW2"], d["SW3"]):
            return "?"
        glod = "full glød" if d["SW3"] else ("svak glød" if d["SW1"] else "")
        lab = " + ".join(x for x in (glod, "sidelys" if d["SW2"] else "") if x)
        return lab or "av"

    def skive(self, s, cx, cy, R):
        """Kragen sett ovanfrå, framme (spaltene) ned. Nummera viser kvar porten i hylsa står i dei ni klikka.
        Spaltene i mantelen er ikkje teikna: dei las som ekstra klikkstillingar."""
        st = self.tilstandar()
        s.sirkel(cx, cy, R, W_NY_O)
        s.sirkel(cx, cy, R * 0.70, W_KT_S)
        for i, d in enumerate(st):
            phi = -d["theta"]
            sx, sy = math.sin(phi * DEG), math.cos(phi * DEG)
            s.linje([(cx + sx * R * 0.70, cy + sy * R * 0.70), (cx + sx * R * 1.10, cy + sy * R * 1.10)], W_KT_O)
            bx, by = cx + sx * (R + 8.5), cy + sy * (R + 8.5)
            s.sirkel(bx, by, 2.6, W_KT_S, "#fff")
            s.tekst(bx, by + 1.0, str(i + 1), 2.7, "bold", "middle")
        bue = [(cx + R * 0.48 * math.sin(-t * DEG), cy + R * 0.48 * math.cos(-t * DEG)) for t in range(6, 86, 4)]
        s.hol_pil(bue, w=1.6, hw=4.2, hl=3.4)
        s.tekst(cx + 3, cy - 2, "ovanfrå", 2.6, "normal", "middle")
        s.tekst(cx, cy + R + 16, "framme", 3.0, "normal", "middle")

    def tabell(self, s, x, y, med_sw):
        st = self.tilstandar()
        kol = [x, x + 8, x + 24] + ([x + 59, x + 71, x + 83] if med_sw else []) + [x + (95 if med_sw else 58)]
        hode = ["", "θ", "lys"] + (["SW1", "SW2", "SW3"] if med_sw else []) + ["spalter*"]
        for j, (xx, t) in enumerate(zip(kol, hode)):
            s.tekst(xx + (3 if 3 <= j <= 5 and med_sw else 0), y, t, 3.0, "bold", "middle" if 3 <= j <= 5 and med_sw else "start")
        y += 1.6
        s.linje([(x - 1, y), (kol[-1] + 16, y)], W_FIN)
        for i, d in enumerate(st):
            y += 5.2
            s.tekst(kol[0] + 1.5, y, str(i + 1), 3.0, "bold", "middle")
            s.tekst(kol[1], y, f"{fmt(d['theta'])}°", 3.0)
            s.tekst(kol[2], y, self.lys_tekst(d), 3.0)
            if med_sw:
                for j, key in enumerate(("SW1", "SW2", "SW3")):
                    v = d[key]
                    s.tekst(kol[3 + j] + 3, y, "lukka" if v else ("open" if v is False else "?"), 2.8, "normal", "middle")
            s.tekst(kol[-1] + 5, y, str(d["opne_spalter"]), 3.0, "normal", "middle")
        s.tekst(x, y + 6.5, "* opne spalter når mantelen er på", 2.6)
        return y + 6.5

    def s11_prov(self):
        p = self.p
        sc = self.scener_C()["prov"]
        s = self.ny_side("s14-prov")
        self.steghovud(s, self.STEG["prov"], "Prøv før du lukkar")
        res = self.hlr(sc)
        ramme = (14, 44, 96, 272)
        k = fit_skala(res, ramme)
        f2 = figur(res, ramme, k)
        f3 = self.f3(sc, f2)
        s.teikning(res, f2, ny=set())
        zr = p.z_hylse_1 - 8
        bue = [polar3(p.r_ho + 10, V_ISO + 40 - t, zr) for t in range(0, 81, 4)]
        s.hol_pil([f3(q) for q in bue])
        q9 = f3(polar3(p.r_ho + 10, V_ISO + 40, zr))
        s.tekst(q9[0] + 9, q9[1] + 2, "9 klikk", 3.4, "bold")
        # kabelenden: 5 V inn
        q = self.ank(res, f2, "F", mot=(1, -1), h=0.5) or f3((-p.fot_d / 2 - 38, 0, p.kabel_z))
        s.ballong(q, (q[0] + 14, q[1] + 10), "F", beslag=True)
        s.tekst(q[0] + 20, q[1] + 11.2, "5 V inn", 3.0)
        st = self.tilstandar()
        self.skive(s, 158, 96, 27)
        self.tabell(s, 92, 162, med_sw=True)
        self.logg(s, self.STEG["prov"], "open funksjonsprøve: kople til 5 V, drei hylsa gjennom dei ni klikka", sc, k,
                  [{"type": "rotasjon", "delar": ["05", "05b", "C"], "akse_modell": [0, 0, 1], "frå_grader": 0, "til_grader": -p.vandring,
                    "skildring": "med klokka sett ovanfrå frå open (0) til av (90)"}],
                  json.dumps(st, ensure_ascii=False))

    def s_snor(self):
        p = self.p
        sc = self.scener_C()["snor"]
        s = self.ny_side("s15-snor")
        self.steghovud(s, self.STEG["snor"], "Silikonsnor")
        res = self.hlr(sc)
        k = self._skala_C
        f2 = figur(res, (70, 44, 196, 272), k)
        f3 = self.f3(sc, f2)
        s.teikning(res, f2, ny={"G"})
        ES = 24.0
        r_s = (p.r_mi + p.r_mo) / 2.0
        for a in p.snor_vinklar:
            s.strek(f3(polar3(r_s, a, p.z_mantel_0 + ES)), f3(polar3(r_s, a, p.z_mantel_0)))
        q = self.ank(res, f2, "G", mot=(1, 0), h=0.5)
        if q:
            s.ballong(q, (q[0] + 16, q[1] - 8), "G", beslag=True)
        # detalj: lomma i golvet av mantelsporet, bit på veg ned
        a = p.snor_vinklar[0]
        c = polar3(r_s, a, p.z_mantel_0 + 1.5)
        Nd = norm(add(polar3(1, a + 25, 0), (0, 0, 1.6)))
        dsc = Scene("d15_snor", [It("01", "01"), It("03", "03"), It("G#0", "G", (0,), t=(0, 0, 7.0), ny=True)], N=Nd,
                    region={"c": c, "h": 12}, defl=0.006)
        f3d = self.detalj(s, dsc, c, 9.0, (44, 176), 32, main=(f3, polar3(r_s, a, p.z_mantel_0 + 2), 6), ny={"G#0"},
                          tekst="i lomma i golvet av sporet ×3")
        s.hol_pil([f3d(polar3(r_s + 4.5, a, p.z_mantel_0 + 9.0)), f3d(polar3(r_s + 4.5, a, p.z_mantel_0 + 2.0))], w=1.6, hw=4.2, hl=3.2)
        self.beslagboks(s, [("beslag", "G", self.ikon("G"), 3)])
        self.logg(s, self.STEG["snor"], "tre bitar silikonsnor G (11b) i lommene i golvet av mantelsporet i foten", sc, k,
                  [{"type": "innføring", "delar": [f"G#{i}" for i in range(3)], "vektor_modell": [0, 0, -1], "lengd_mm": ES}],
                  f"Lommene ligg på asimut {', '.join(fmt(a_) for a_ in p.snor_vinklar)}°. Snora gjev forspenninga i bajonetten (steg {self.STEG['mantel']}).")

    def s12_mantel(self):
        p = self.p
        sc = self.scener_C()["mantel"]
        s = self.ny_side("s16-mantel")
        self.steghovud(s, self.STEG["mantel"], "Mantel")
        res = self.hlr(sc)
        k = self._skala_C
        f2 = figur(res, self.RAMME, k)
        f3 = self.f3(sc, f2)
        s.teikning(res, f2, ny={"04", "10"})
        EMa = 120.0
        s.hol_pil([f3(polar3(p.r_mo + 12, V_ISO + 95, EMa + 150)), f3(polar3(p.r_mo + 12, V_ISO + 95, EMa + 40))])
        # vriinga: frå +baj_vri til 0, altså med klokka sett ovanfrå (minkande asimut)
        zr = EMa + p.z_mantel_0 + 14          # rundt nedre enden av mantelen, som er det som blir vridd
        bue = [polar3(p.r_mo + 7, V_ISO + 40 - t, zr) for t in range(0, 71, 3)]
        s.hol_pil([f3(q) for q in bue])
        q0 = f3(bue[0])
        s.tekst(q0[0] + 9, q0[1] + 1, f"{fmt(p.baj_vri)}°", 3.6, "bold", "start")
        self.merk(s, res, f2, "04", mot=(1, 0), h=0.3, off=(14, 0))
        # detaljar: bajonett før og etter. L-sporet ligg inne i sporet i foten, så ytterveggen til foten er kutta bort.
        th = p.baj_vinklar[0]
        Nb = norm(add(polar3(1, th, 0), (0, 0, 0.35)))
        zk = p.z_mantel_0 + p.baj_knast_z + p.baj_knast_h / 2
        c = polar3(p.r_mo, th, zk)
        rd = 12.0
        kutt = [{"type": "utanfor_r", "r": p.r_mo + 0.1, "delar": ["01"]}]
        for j, (rz, pos, txt) in enumerate(((p.baj_vri, (40, 172), "1  ned og trykk"), (0.0, (40, 234), f"2  vri {fmt(p.baj_vri)}°"))):
            dsc = Scene(f"d16_baj{j}", [It("01", "01"), It("04", "04", rz=rz, ny=True)], N=Nb,
                        region={"c": c, "h": 16}, kutt=kutt, defl=0.01)
            f3d = self.detalj(s, dsc, c, rd, pos, 24, main=(f3, polar3(p.r_mo, th, p.z_fot_1 - 2), 6) if j == 0 else None,
                              ny={"04"}, tekst=txt)
            if j == 0:
                s.hol_pil([f3d(polar3(p.r_mo + 1, th, zk + 9.0)), f3d(polar3(p.r_mo + 1, th, zk + 3.2))], w=1.6, hw=4.2, hl=3.2)
            else:
                zp = p.z_mantel_0 + p.baj_knast_z + p.baj_knast_h + 3.0
                pts = [f3d(polar3(p.r_mo + 1, th + 4.0 - (p.baj_vri + 2.0) * i / 11.0, zp)) for i in range(12)]
                s.hol_pil(pts, w=1.6, hw=4.2, hl=3.2)
        s.tekst(40, 270, "trykk ned, vri med klokka", 3.2, "normal", "middle")
        s.tekst(40, 275, "sett ovanfrå, til ho låser", 3.2, "normal", "middle")
        self.beslagboks(s, [("del", "04", self.ikon("04"), 1)])
        self.logg(s, self.STEG["mantel"], "mantelen ned over hylsa med L-spora over knastane, trykk ned mot snora og vri med klokka til ho låser", sc, k,
                  [{"type": "innføring", "delar": ["04", "10"], "vektor_modell": [0, 0, -1], "lengd_mm": EMa, "start_rot_z_grader": p.baj_vri},
                   {"type": "trykk", "delar": ["04", "10"], "vektor_modell": [0, 0, -1], "skildring": f"mot snorbitane G, forbi nabben {fmt(p.baj_nabb_h)} mm"},
                   {"type": "rotasjon", "delar": ["04", "10"], "akse_modell": [0, 0, 1], "frå_grader": p.baj_vri, "til_grader": 0.0,
                    "skildring": "med klokka sett ovanfrå (minkande asimut), slik L-sporet i modellen krev"}],
                  f"L-sporet har inngangen på knastvinkel - baj_vri i mantelen si ramme: mantelen går ned berre når ho står på +{fmt(p.baj_vri)}°. "
                  f"Demontering: trykk ned, vri {fmt(p.baj_vri)}° mot klokka, løft.")

    def s13_lok(self):
        p = self.p
        sc = self.scener_C()["lok"]
        s = self.ny_side("s17-lok")
        self.steghovud(s, self.STEG["lok"], "Lok")
        res = self.hlr(sc)
        k = self._skala_C
        f2 = figur(res, self.RAMME, k)
        f3 = self.f3(sc, f2)
        s.teikning(res, f2, ny={"08"})
        s.hol_pil([f3(polar3(p.r_ho + 12, V_ISO + 95, p.z_lok_1 + 60)), f3(polar3(p.r_ho + 12, V_ISO + 95, p.z_lok_1 + 4))])
        self.merk(s, res, f2, "08", mot=(1, 0), h=0.5, off=(16, -6))
        a = 0.0       # nabbane på skjørtet står på 0, 120 og 240; fingergrepa på 90 og 270
        c = polar3(p.r_lok, a, p.z_lok_1 - 0.5)
        dsc = Scene("d17_nabb", [It("07", "07"), It("08", "08", ny=True)], N=(math.sin(a * DEG), -math.cos(a * DEG), 0.0),
                    kutt={"type": "snitt", "az": a}, region={"c": c, "h": 9}, defl=0.004)
        self.detalj(s, dsc, c, 4.0, (165, 230), 26, main=(f3, polar3(p.r_lok, a, p.z_lok_1), 5), ny={"08"}, tekst="klikk under nabbane ×3")
        self.beslagboks(s, [("del", "08", self.ikon("08"), 1)])
        self.logg(s, self.STEG["lok"], "opalskiva 08 ned i setet, ho smett under tre små nabbar (0°, 120°, 240°)", sc, k,
                  [{"type": "innføring", "delar": ["08"], "vektor_modell": [0, 0, -1], "lengd_mm": 46}],
                  "Fingergrepa på 90° og 270° er for å løfte loket ut igjen (S1).")

    # ------------------------------------------------------------------ sluttkontroll og service
    def s_sluttkontroll(self):
        p = self.p
        s = self.ny_side("sluttkontroll")
        s.tekst(13, 30, "Sluttkontroll", 7, "bold")
        sc = Scene("framside", self.heil(), defl=0.05)
        res = self.hlr(sc)
        ramme = (14, 44, 100, 272)
        k = fit_skala(res, ramme)
        s.teikning(res, figur(res, ramme, k), ny=set(res))
        self.skive(s, 150, 80, 24)
        y = self.tabell(s, 106, 132, med_sw=False) + 14
        for t in (f"Står stødig på O-ringen, {fmt(p.fot_loft)} mm skuggefuge.", "Mantelen er låst: ho går ikkje rundt",
                  "  utan at du trykkjer ho ned.", "Hylsa går lett gjennom alle ni klikk og stoppar i båe endar.",
                  "Klikk 9 (90°): alt lys er av.", "Loket ligg i flukt under nabbane.",
                  "Kabelen sit fast bak: dra lett, ingenting rører seg."):
            if not t.startswith("  "):
                s.rekt(112, y - 3.6, 116, y + 0.4, W_KT_O)
            s.tekst(119, y, t.strip(), 3.0)
            y += 5 if t.endswith("rundt") else 9
        self.logg(s, None, "sluttkontroll", sc, k)

    def vri_ikon(self, s, x, y, tekst, mot_klokka=False):
        """Lite ovanfrå-ikon av kragen, framme ned. Med klokka: frå 0° til av (90°); mot klokka: tilbake til 0° (klikk 1)."""
        R = 4.2
        s.sirkel(x, y, R, W_KT_O)
        s.linje([(x, y + R * 0.3), (x, y + R * 1.25)], W_KT_O)
        bue = [(x + (R + 2.4) * math.sin(-t * DEG), y + (R + 2.4) * math.cos(-t * DEG)) for t in range(0, 91, 8)]
        s.hol_pil(bue[::-1] if mot_klokka else bue, w=1.0, hw=2.8, hl=2.2)
        s.tekst(x + R + 6, y + 1.2, tekst, 3.2)

    def vri_av_ikon(self, s, x, y, tekst):
        self.vri_ikon(s, x, y, tekst)

    def s_service_modul(self):
        p = self.p
        s = self.ny_side("service-modul")
        s.tekst(13, 30, "S1", 17, "bold")
        s.tekst(37, 29.5, "Byt lysmodul, utan verktøy", 4.2)
        self.vri_av_ikon(s, 20, 42, "Vri kragen til av (90°) først: modulen er straumlaus når pluggen kjem laus.")
        s.tekst(30.2, 48.6, "Modulen er limt og blir bytt som heil eining: ikkje ta han frå kvarandre.", 3.0)
        sc_a = Scene("sv1_lok", self.heil(med_lok=False) + [It("08", "08", t=(0, 0, 30), ny=True)])
        sc_b = Scene("sv1_modul", [x for x in self.heil(med_lok=False) if x.key not in self.MOD] + self.modul(dz=150, ny=True))
        rammer = ((14, 56, 104, 272), (106, 56, 196, 272))
        k = min(fit_skala(self.hlr(sc_a), rammer[0]), fit_skala(self.hlr(sc_b), rammer[1]))
        for (sc, ramme, nr) in ((sc_a, rammer[0], "1"), (sc_b, rammer[1], "2")):
            res = self.hlr(sc)
            f2 = figur(res, ramme, k, juster="botn")
            f3 = self.f3(sc, f2)
            s.teikning(res, f2, ny={"08"} if nr == "1" else set(self.MOD))
            s.sirkel(ramme[0] + 6, 62, 4.5, W_KT_O)
            s.tekst(ramme[0] + 6, 63.6, nr, 4.5, "bold", "middle")
            if nr == "1":
                s.hol_pil([f3(polar3(p.r_ho + 12, V_ISO + 95, p.z_lok_1 + 4)), f3(polar3(p.r_ho + 12, V_ISO + 95, p.z_lok_1 + 50))])
                a = 90.0
                c = polar3(p.r_lok, a, p.z_lok_1)
                dsc = Scene("dsv1_grep", [It("07", "07"), It("08", "08", ny=True), It("05", "05")], N=(math.sin(a * DEG), -math.cos(a * DEG), 0.0),
                            kutt={"type": "snitt", "az": a}, region={"c": c, "h": 9}, defl=0.004)
                self.detalj(s, dsc, c, 4.5, (38, 88), 18, main=(f3, polar3(p.r_lok, 90, p.z_lok_1), 4), ny={"08"}, tekst="fingergrep ×2")
            else:
                s.hol_pil([f3(polar3(p.r_ho + 12, V_ISO + 95, p.z_hylse_1 - 10)), f3(polar3(p.r_ho + 12, V_ISO + 95, p.z_hylse_1 + 100))])
        self.logg(s, "S1", "service: vri til av (90°), lyft loket ut i fingergrepet, dra modulen rett opp", sc_b, k,
                  [{"type": "rotasjon", "delar": ["05", "05b", "C"], "akse_modell": [0, 0, 1], "til_grader": -p.vandring,
                    "skildring": "til av (90°): alle tre brytarane opne, 0 W før pluggen i mastfoten blir kopla frå"},
                   {"type": "uttak", "delar": ["08"], "vektor_modell": [0, 0, 1]}, {"type": "uttak", "delar": list(self.MOD), "vektor_modell": [0, 0, 1]}],
                  "Lysmodulen er limt (2K-epoksy) og blir bytt som heil eining.")

    def s_service_kabel(self):
        p = self.p
        s = self.ny_side("service-kabel")
        s.tekst(13, 30, "S2", 17, "bold")
        s.tekst(37, 29.5, "Byt kabel", 4.2)
        self.vri_av_ikon(s, 20, 42, "Vri til av (90°), ta ut loket og lysmodulen (S1) og trekk ut USB-pluggen.")
        # lok og modul er ute (S1) før lampa blir snudd: dei sit laust og ville falle ut
        base = self.basis(skruar=True, snor=True)
        hyl = self.hylse_sett()
        LM = 90.0
        sc_a = Scene("sv2_mantel", base + hyl + [It("04", "04", t=(0, 0, LM), rz=p.baj_vri, ny=True),
                                                 It("10", "10", t=(0, 0, LM), rz=p.baj_vri, ny=True)])
        EA = 22.0
        sc_b = Scene("sv2_skruar", [x for x in self.basis(skruar=True) if not x.key.startswith("A#")] + hyl
                     + [It(f"A#{i}", "A", (a,), t=(0, 0, -EA), ny=True) for i, a in enumerate(p.skrue_vinklar)], G="snu")
        lyft = 60.0
        upper = [It(x.key, x.kjelde, x.args, t=(0, 0, lyft), ny=True)
                 for x in [It("03", "03")] + self.elektronikk() + ([] if self.mastfot else [It("06d", "06d")]) + hyl]
        sc_c = Scene("sv2_lyft", [It("01", "01"), It("D", "Dt"), It("F", "F", (lyft,), ny=True)] + upper)
        # tre høge figurar side om side
        rammer = [(14, 52, 74, 280), (76, 52, 136, 280), (138, 52, 196, 280)]
        for (sc, ramme, nr) in ((sc_a, rammer[0], "1"), (sc_b, rammer[1], "2"), (sc_c, rammer[2], "3")):
            res = self.hlr(sc)
            fr = (ramme[0] + 2, ramme[1] + (26 if nr == "2" else 12), ramme[2] - 2, ramme[3] - 13)
            k = fit_skala(res, fr)
            f2 = figur(res, fr, k, juster="botn")
            f3 = self.f3(sc, f2)
            s.teikning(res, f2, ny={x.key.split("#")[0] for x in sc.items if x.ny} | {x.key for x in sc.items if x.ny})
            s.sirkel(ramme[0] + 6, ramme[1] + 6, 4.5, W_KT_O)
            s.tekst(ramme[0] + 6, ramme[1] + 7.6, nr, 4.5, "bold", "middle")
            xm = (ramme[0] + ramme[2]) / 2
            if nr == "1":
                # demontering av mantelen (04): trykk ned, vri mot klokka sett ovanfrå (aukande asimut), løft.
                # Pilene sit på mantelen, som er teikna løfta LM over foten.
                zm0, zm1 = LM + p.z_mantel_0, LM + p.z_mantel_1
                s.hol_pil([f3(polar3(p.r_mo + 12, V_ISO - 95, zm1 - 20)), f3(polar3(p.r_mo + 12, V_ISO - 95, zm1 - 70))])
                bue = [polar3(p.r_mo + 7, V_ISO - 35 + t, zm0 + 18) for t in range(0, 61, 3)]
                s.hol_pil([f3(q) for q in bue])
                s.hol_pil([f3(polar3(p.r_mo + 12, V_ISO + 95, zm0 + 60)), f3(polar3(p.r_mo + 12, V_ISO + 95, zm0 + 150))])
                s.tekst(xm, ramme[3] - 6, f"trykk ned, vri {fmt(p.baj_vri)}°", 3.0, "normal", "middle")
                s.tekst(xm, ramme[3] - 1.5, "mot klokka, løft", 3.0, "normal", "middle")
            elif nr == "2":
                s.snu_ikon(ramme[0] + 14, ramme[1] + 2)
                a1 = p.skrue_vinklar[1]
                zc = p.z_fot_0 + 2.2
                s.hol_pil([f3(polar3(p.skrue_r + 10, a1 + 28, zc - 2)), f3(polar3(p.skrue_r + 10, a1 + 28, zc - EA + 4))])
                s.tekst(xm, ramme[3] - 6, "A ×3  ·  2 mm", 3.0, "bold", "middle")
            else:
                s.hol_pil([f3(polar3(p.r_ho + 12, V_ISO + 95, p.toppdekk_z1 + 6)), f3(polar3(p.r_ho + 12, V_ISO + 95, p.toppdekk_z1 + lyft + 10))])
                s.tekst(xm, ramme[3] - 6, "JST-pluggen ut, løys S-en,", 3.0, "normal", "middle")
                s.tekst(xm, ramme[3] - 1.5, "kabelen ut bak", 3.0, "normal", "middle")
        self.logg(s, "S2", "service: vri til av, lok og modul ut (S1), USB ut; mantelen av (trykk ned, vri mot klokka, løft), "
                  "snu og skru ut 3 x A, lyft chassiset med hylsa, JST ut", sc_c, 0,
                  [{"type": "uttak", "delar": ["08"] + list(self.MOD), "skildring": "som S1"},
                   {"type": "trykk", "delar": ["04"], "vektor_modell": [0, 0, -1]},
                   {"type": "rotasjon", "delar": ["04"], "frå_grader": 0, "til_grader": p.baj_vri, "skildring": "mot klokka sett ovanfrå"},
                   {"type": "uttak", "delar": ["04"], "vektor_modell": [0, 0, 1]},
                   {"type": "uttak", "delar": ["A#0", "A#1", "A#2"], "vektor_modell": [0, 0, -1]}, {"type": "uttak", "delar": ["03"], "vektor_modell": [0, 0, 1]}],
                  "Figur 1: mantelen er teikna løfta og vridd; pilene (ned, boge, opp) sit på mantelen.")

    def s_feilsoking(self):
        S = self.STEG
        s = self.ny_side("feilsoking")
        s.tekst(13, 30, "S3", 17, "bold")
        s.tekst(37, 29.5, "Feilsøking", 4.2)
        rader = [("Inkje lys", "Ikkje straum, F1 (PTC) har løyst ut, eller pluggen i mastfoten sit ikkje",
                  f"Prøv anna USB-lader, vent eit minutt. Trykk modulen ned (steg {S['modul']}). Sjå kortet (steg {S['kort']})."),
                 ("Berre glød, inkje sidelys", "SW2, ringen på jacken 13, eller SIDE-leidningen i lysmodulen",
                  f"Juster SW2 (steg {S['juster']}). Sjå ringen på 13 (steg {S['kort']}). Er feilen i modulen: byt han (S1)."),
                 ("Sidelys, men inkje glød", "Tuppen på jacken 13, R1 og R3, eller TOPP-leidningen i lysmodulen",
                  f"Sjå tuppen på jacken, R1 og R3 (steg {S['kort']}). Er feilen i modulen: byt han (S1)."),
                 ("Berre svak glød i stilling 1 til 7", "SW3 eller R3",
                  f"Juster SW3 (steg {S['juster']}). Sjå R3 (steg {S['kort']})."),
                 ("Klikka er slappe", "Fotringen 05b er sliten eller sit ikkje heilt nede",
                  f"Byt 05b (S2, steg {S['fotring']} til {S['juster']})."),
                 ("Kragen vaglar", "Stoppskruane C er lause", f"Mantelen av, stram C (steg {S['stopp']})."),
                 ("Mantelen er laus", "Bajonetten er ikkje låst, eller snorbitane G manglar",
                  f"Trykk ned og vri {fmt(self.p.baj_vri)}° med klokka (steg {S['mantel']}). Sjå G (steg {S['snor']})."),
                 ("Mantelen vil ikkje av", "Han er ikkje trykt ned forbi nabben",
                  f"Trykk ned, vri {fmt(self.p.baj_vri)}° mot klokka, løft.")]
        x = (13, 62, 128)
        y = 46
        for t, xx in zip(("Feil", "Årsak", "Tiltak"), x):
            s.tekst(xx, y, t, 3.8, "bold")
        y += 3
        s.linje([(13, y), (197, y)], W_KT_O)
        for (a, b, c) in rader:
            ya = self._wrap(s, x[0], y + 6, a, 46, 3.3, "bold")
            yb = self._wrap(s, x[1], y + 6, b, 62, 3.1)
            yc = self._wrap(s, x[2], y + 6, c, 68, 3.1)
            y = max(ya, yb, yc) + 3
            s.linje([(13, y), (197, y)], W_FIN)

    def _wrap(self, s, x, y, tekst, breidd_mm, size, vekt="normal"):
        maks = int(breidd_mm / (size * 0.5))
        ord_ = tekst.split()
        linje = ""
        lengd = lambda t: len(re.sub(r"\{\{side:[\w-]+\}\}", "00", t))     # plasshaldaren blir eit tosifra sidenummer
        for w in ord_:
            if lengd(linje) + lengd(w) + 1 > maks and linje:
                s.tekst(x, y, linje, size, vekt)
                y += size * 1.35
                linje = w
            else:
                linje = (linje + " " + w).strip()
        if linje:
            s.tekst(x, y, linje, size, vekt)
        return y

    def s_prototype(self):
        pp = g.FyrParams.prototype()
        s = self.ny_side("prototype")
        s.tekst(13, 30, "P", 17, "bold")
        s.tekst(27, 29.5, "Berre prototypen (P1S-prent)", 4.2)
        EH, EG = 40.0, 74.0      # øvre mantelhalvdel og gliderringen, eksplodert opp
        sc = Scene("proto_mantel", [It("04a", "proto_mantel", (0,)), It("04b", "proto_mantel", (1,), t=(0, 0, EH), ny=True),
                                    It("10", "proto_glide", t=(0, 0, EG), ny=True)])
        res = self.hlr(sc)
        ramme = (14, 44, 104, 266)
        k = fit_skala(res, ramme)
        f2 = figur(res, ramme, k)
        f3 = self.f3(sc, f2)
        s.teikning(res, f2, ny={"04b", "10"})
        s.hol_pil([f3(polar3(pp.r_mo + 12, V_ISO + 95, 140)), f3(polar3(pp.r_mo + 12, V_ISO + 95, 92))])
        s.hol_pil([f3(polar3(pp.r_mo + 12, V_ISO + 95, pp.z_glide_1 + EG + 18)), f3(polar3(pp.r_mo + 12, V_ISO + 95, pp.z_mantel_1 + EH + 4))])
        s.tekst(60, 274, "mantelen i to: lim falsen (epoksy)", 3.2, "normal", "middle")
        s.tekst(60, 279, "gliderringen 10: CA i toppen av mantelen", 3.2, "normal", "middle")

        def limmerke(q, tekst):
            s.rekt(q[0] - 22, q[1] - 4, q[0] - 10, q[1] + 4, W_KT_O, "#fff")
            s.tekst(q[0] - 16, q[1] + 1.2, tekst, 3.0, "bold", "middle")
            s.linje([(q[0] - 10, q[1]), (q[0] - 0.5, q[1])], W_FIN)
        # limsymbol ved skøyten (epoksy) og øvst i mantelen der gliderringen sit (CA)
        limmerke(self.ank(res, f2, "04a", mot=(-1, 0), h=0.02) or f3(polar3(pp.r_mo, V_ISO + 160, 86)), "lim")
        limmerke(self.ank(res, f2, "04b", mot=(-1, 0), h=0.01) or f3(polar3(pp.r_mo, V_ISO + 160, pp.z_mantel_1 + EH)), "CA")
        self.merk(s, res, f2, "10", mot=(-1, 0), h=0.4, off=(-7, -11))
        sc2 = Scene("proto_hylse", [It("05p", "proto_hylse", ny=True)])
        res2 = self.hlr(sc2)
        ramme2 = (112, 60, 196, 230)
        k2 = fit_skala(res2, ramme2)
        s.teikning(res2, figur(res2, ramme2, k2), ny={"05p"})
        s.tekst(154, 244, f"hylse 05 + 05b prenta i eitt,", 3.2, "normal", "middle")
        s.tekst(154, 249, f"vegg {fmt(pp.hylse_t)} mm: steg {self.STEG['fotring']} fell bort", 3.2, "normal", "middle")
        self.logg(s, "P", "prototype: mantelen i to delar med limt falsskøyt (epoksy), gliderringen 10 limt med CA i toppen av mantelen, "
                  "hylsa prenta i eitt", sc, k,
                  [{"type": "innføring+lim", "delar": ["04b"], "vektor_modell": [0, 0, -1], "lengd_mm": EH, "lim": "epoksy i falsen"},
                   {"type": "innføring+lim", "delar": ["10"], "vektor_modell": [0, 0, -1], "lengd_mm": EG - EH, "lim": "CA"}],
                  f"Prototypen: gliderringen blir limt med CA i tillegg til falsen i mantelen. Lysmodulen: sjå side {sideref('lysmodul')}.")

    # ------------------------------------------------------------------ førmontering av lysmodulen
    def plugg_skjema(self, s, x, y, L):
        """TRS-pluggen sett frå sida (tuppen til venstre): tupp, ring og hylse med leiarane som skal loddast til kvar."""
        h, hb = 3.6, 6.2
        sone = [("tupp", "TOPP+", 0.0, 0.22), ("ring", "SIDE+", 0.27, 0.47), ("hylse", "GND ×2", 0.52, 0.80)]
        s.poly([(x, y), (x + 0.07 * L, y - h / 2), (x + 0.22 * L, y - h / 2), (x + 0.22 * L, y + h / 2), (x + 0.07 * L, y + h / 2)], W_KT_O, "#fff")
        for a, b in ((0.22, 0.27), (0.47, 0.52)):        # isolasjonsringane
            s.rekt(x + a * L, y - h / 2, x + b * L, y + h / 2, W_KT_O, "#000")
        s.rekt(x + 0.27 * L, y - h / 2, x + 0.47 * L, y + h / 2, W_KT_O, "#fff")
        s.rekt(x + 0.52 * L, y - h / 2, x + 0.80 * L, y + h / 2, W_KT_O, "#fff")
        s.rekt(x + 0.80 * L, y - hb / 2, x + L, y + hb / 2, W_KT_O, "#fff")      # loddekroppen
        for j, (namn, leiar, a, b) in enumerate(sone):
            xm = x + (a + b) / 2 * L
            yt = y + h / 2 + 5.5 + 4.6 * j
            s.linje([(xm, y + h / 2), (xm, yt - 2.6)], W_FIN)
            s.el.append(f'<circle cx="{xm:.2f}" cy="{y + h / 2:.2f}" r="0.5" fill="#000"/>')
            s.tekst(xm, yt, f"{namn} = {leiar}", 2.8, "bold" if j == 0 else "normal", "middle")

    def golvmaal(self):
        """Leidningsgjennomgangane i golvet, målte på B-rep (maal_golvhol), mellomlagra på geometrihashen."""
        if getattr(self, "_golvmaal", None) is None:
            f = CACHE / f"golvmaal_v1_{self.hlr.hash}.json"
            if self.hlr.bruk and f.exists():
                self._golvmaal = {k: tuple(v) for k, v in json.loads(f.read_text(encoding="utf-8")).items()}
            else:
                self._golvmaal = maal_golvhol(self.p, self.hlr.kj.del_("07"))
                f.write_text(json.dumps(self._golvmaal), encoding="utf-8")
        return self._golvmaal

    def golvhol(self, s, f3, dz=0.0, kva=("framfor", "bak"), w=W_NY_O):
        """Omrisset av leidningsgjennomgangane på oversida av golvet i rista, teikna tjukt (dz: rista løfta)."""
        p = self.p
        z = p.rist_z0 + p.golv_t + dz
        hol = self.golvmaal()
        for k in kva:
            x0, x1, y0, y1 = hol[k]
            s.linje([f3((x0, y0, z)), f3((x1, y0, z)), f3((x1, y1, z)), f3((x0, y1, z)), f3((x0, y0, z))], w)

    def topp_kopling(self, s, cx, cy, k):
        """Detalj ovanfrå (framme til venstre): dei fire 06c på bereringen med + ytst, bøylane over skøytane og
        dei to leiarane som kjem opp gjennom hola på r 17 (TOPP_BOYLAR). Skjematisk, skala k."""
        p = self.p
        rm, hb, tl = p.topp_r, p.stripe_b / 2, p.topp_l / 2
        tp = tl - 1.8                                   # loddeflatene ved endane
        # ovanfrå med +X (framme) til venstre og +Y ned: (u, v) = (cx - x k, cy + y k) er sett ovanfrå, ikkje spegla
        P = lambda a, r, t: (cx - k * (r * math.cos(a * DEG) - t * math.sin(a * DEG)),
                             cy + k * (r * math.sin(a * DEG) + t * math.cos(a * DEG)))
        ytopp = cy - k * (rm + hb + 3.0)
        s.tekst(cx, ytopp - 9.5, "06c sett ovanfrå", 2.6, "bold", "middle")
        s.tekst(cx, ytopp - 6.3, "(framme til venstre)", 2.2, "normal", "middle")
        for a in (45.0, 135.0, 225.0, 315.0):
            s.linje([P(a, rm - hb, -tl), P(a, rm + hb, -tl), P(a, rm + hb, tl), P(a, rm - hb, tl), P(a, rm - hb, -tl)], W_KT_O)
            for t in (-tp, tp):
                for dr in (2.2, -2.2):
                    q = P(a, rm + dr, t)
                    s.el.append(f'<circle cx="{q[0]:.2f}" cy="{q[1]:.2f}" r="0.42" fill="#000"/>')
            q = P(a, rm + 2.2, 0.0)
            s.tekst(q[0], q[1] + 1.0, "+", 2.6, "bold", "middle")
        for pol, dr, rmid in (("+", 2.2, rm + hb + 1.6), ("GND", -2.2, rm - hb - 1.2)):
            for gv in TOPP_BOYLAR[pol]:
                a0, a1 = gv - 45.0, gv + 45.0
                q0, q1 = P(a0, rm + dr, tp), P(a1, rm + dr, -tp)
                qm = P(gv, rmid, 0.0)
                s.linje([q0, qm, q1], W_NY_O)
        # hola på r 17 og leiarane opp til bøylane
        for gv, rmid, namn, dv in ((TOPP_BOYLAR["TOPP+_ved"], rm + hb + 1.6, "raud TOPP+", 1.0),
                                   (TOPP_BOYLAR["GND_ved"], rm - hb - 1.2, "svart GND", -1.0)):
            qh = P(gv, 17.0, 0.0)
            s.sirkel(qh[0], qh[1], 0.6 * k + 0.25, W_FIN, "#fff")
            s.linje([qh, P(gv, rmid, 0.0)], 0.9)
            # leiar ut gjennom skøyten til namnet over / under ringen
            ql = P(gv, rm + hb + 5.0, 0.0)
            s.linje([qh if dv < 0 else P(gv, rmid, 0.0), ql], W_FIN)
            s.tekst(ql[0], ql[1] + (3.2 if dv > 0 else -1.2), namn, 2.4, "bold", "middle")
        ybotn = cy + k * (rm + hb + 5.0) + 3.2
        s.tekst(cx, ybotn + 4.6, "+ ytst på alle fire; bøylar AWG 28,", 2.3, "normal", "middle")
        s.tekst(cx, ybotn + 7.8, "ca. 15 mm, over skøytane", 2.3, "normal", "middle")

    def s_lysmodul(self):
        """M: førmontering av lysmodulen (06 + 06b + 06c + 07 + 06d, limt med 2K-epoksy H11), for fabrikken og
        prototypen. Kunden får modulen ferdig samla (steg 13) og byter han som eining (S1). Fire delbilete i den
        rekkjefølgja dei kan utførast:
          1 06b på staven og leiarane lodda til 06b; leiarane til 06c trekte opp nedanfrå (gjennomgangen bak klypa,
            bakrommet, hola i bereringen), så 06c på bereringen (+ ytst) og leiarar og bøylar lodda (detalj ovanfrå);
          2 rista tørr ned over staven til ho kviler på toppen av han (06b og leiarane gjennom gjennomgangen framfor
            staven), så ein kil epoksy mellom undersida av golvet og staven, bak og på sidene;
          3 leiarane under golvet rundt staven til kanalen bak staven i mastfoten, gjennom lomma og ut nedst, lodda
            til pluggen (tupp TOPP+, ring SIDE+, hylse GND);
          4 pluggkroppen opp i lomma og staven ned i stavsporet, båe med epoksy."""
        p = self.p
        pp = g.FyrParams.prototype()
        s = self.ny_side("lysmodul")
        s.tekst(13, 30, "M", 17, "bold")
        s.tekst(31, 29.5, "Lysmodul: førmontering", 4.2)
        s.tekst(31, 35.5, "for fabrikken og prototypen · modulen er éi limt eining", 3.0)
        self.beslagboks(s, [("verktoy", "loddebolt", self.ikon("lodd"), None), ("forbruk", "epoksy (H11)", None, None),
                            ("forbruk", "AWG 28 (E12)", None, None)])
        s.tekst(160.5, 27.5, "2K", 7, "bold", "middle")
        for j in range(3):                     # tre leiarar i boksen
            yy = 16.0 + 4.2 * j
            s.linje([(176.5 + 0.5 * t, yy + 1.1 * math.sin(0.32 * t + 1.4 * j)) for t in range(0, 38)], 0.45)
        P = [(14, 46, 104, 162), (106, 46, 196, 162), (14, 166, 104, 282), (106, 166, 196, 282)]
        s.linje([(105, 48), (105, 280)], W_FIN)
        s.linje([(16, 164), (194, 164)], W_FIN)
        for (x0, y0, _x1, _y1), nr in zip(P, "1234"):
            s.sirkel(x0 + 5, y0 + 5, 4.0, W_KT_O)
            s.tekst(x0 + 5, y0 + 6.5, nr, 4.2, "bold", "middle")

        def tekstar(panel, linjer):
            x0, _y0, _x1, y1 = panel
            for j, t in enumerate(linjer):
                s.tekst(x0 + 2, y1 - 4.8 * (len(linjer) - 1 - j) - 2, t, 3.0)

        def limmerke(q, xb, tekst="epoksy"):
            s.rekt(xb, q[1] - 3.6, xb + 15, q[1] + 3.6, W_KT_O, "#fff")
            s.tekst(xb + 7.5, q[1] + 1.1, tekst, 2.7, "bold", "middle")
            s.linje([(xb + 15, q[1]) if xb < q[0] else (xb, q[1]), q], W_FIN)
            s.el.append(f'<circle cx="{q[0]:.2f}" cy="{q[1]:.2f}" r="0.45" fill="#000"/>')

        L4 = [f"L#{j}" for j in range(4)]
        Lb, Lc = ("L#1", "L#2"), ("L#0", "L#3")

        # ---- 1: stripene på, og éin leiar lodda til kvar pol på kvar stripe
        Xs = norm(cross((0, 0, 1), norm(ISO)))
        rpos = (Xs[0] * 72.0, Xs[1] * 72.0, 0.0)
        ES1, EC1 = 30.0, 46.0
        ob = {"B": (ES1, 0.0, 0.0), "S": (ES1, 0.0, 0.0)}
        oc = {"C": add(rpos, (0.0, 0.0, EC1)), "R": rpos}
        it1 = [It("06", "06"), It("06b", "06b", t=(ES1, 0, 0), ny=True), It("07", "07", t=rpos),
               It("06c", "06c", t=add(rpos, (0, 0, EC1)), ny=True)]
        it1 += [It(f"L#{j}", "mleiar", (j, ob, 4, 18.0), ny=True) for j in (1, 2)]
        it1 += [It(f"L#{j}", "mleiar", (j, oc, 4, 5.0), ny=True) for j in (0, 3)]
        sc1 = Scene("m1_stripene", it1, defl=0.05)
        res = self.hlr(sc1)
        ramme = (P[0][0] + 42, P[0][1] + 6, P[0][2] - 9, P[0][3] - 32)
        k1 = fit_skala(res, ramme)
        f2 = figur(res, ramme, k1)
        f3 = self.f3(sc1, f2)
        s.teikning(res, f2, ny={"06b", "06c", "L"})
        for z in (p.stripe_z0, p.stripe_z1):
            s.strek(f3((ES1 + p.stav_t / 2, 0, z)), f3((p.stav_t / 2 + 0.2, 0, z)))
        zp = (p.stripe_z0 + p.stripe_z1) / 2
        s.hol_pil([f3((ES1 + 2, -10, zp)), f3((3, -10, zp))], w=1.6, hw=4.2, hl=3.4)
        s.hol_pil([f3(add(rpos, polar3(50, V_ISO + 95, p.topp_berar_z + EC1 + 14))), f3(add(rpos, polar3(50, V_ISO + 95, p.topp_berar_z + 30)))],
                  w=1.6, hw=4.2, hl=3.4)
        self.merk(s, res, f2, "06", mot=(-1, 0), h=0.85, off=(-10, 4))
        self.merk(s, res, f2, "06b", mot=(-1, 0), h=0.3, off=(-12, -1))
        self.merk(s, res, f2, "07", mot=(1, 0), h=0.55, off=(10, 0))
        self.merk(s, res, f2, "06c", mot=(1, 0), h=0.2, off=(9, -5))
        # leiarane på 06b: blå SIDE+ og svart GND, med loddebolten ved loddeflata
        qe = f3(add(mleiar_bane(p, 1)[3][1], (ES1, 0.0, -18.0)))
        s.linje([qe, (qe[0] + 27, qe[1] + 4.2)], W_FIN)
        s.el.append(f'<circle cx="{qe[0]:.2f}" cy="{qe[1]:.2f}" r="0.45" fill="#000"/>')
        s.tekst(qe[0] + 28, qe[1] + 4.6, "blå SIDE+", 2.6, "bold")
        s.tekst(qe[0] + 28, qe[1] + 8.0, "svart GND", 2.6, "bold")
        self.topp_kopling(s, 34.0, 79.0, 0.5)
        tekstar(P[0], [f"06b på framsida av staven, {fmt(p.stripe_z0 - p.stav_z0)} mm frå nedre enden;",
                       "lodd blå (SIDE+) og svart (GND) til 06b. Trekk raud",
                       "(TOPP+) og svart (GND) opp nedanfrå: gjennom golvet",
                       "bak klypa og ut gjennom hola i bereringen (trekketråd).",
                       "Lim 4 × 06c på bereringen med + ytst, og lodd",
                       "leiarane og bøylane som i detaljen ovanfrå."])
        self.logg(s, "M1", "sidestripa 06b på framsida av staven 06 (z 92..250), blå SIDE+ og svart GND (E12) lodda til 06b; "
                  "raud TOPP+ og svart GND (E12) trekte opp nedanfrå gjennom gjennomgangen bak klypa, bakrommet og hola på r 17 "
                  "(90° og 270°) med trekketråd; fire toppstriper 06c på bereringen i rista 07 med + ytst, og raud TOPP+, svart GND "
                  "og bøylane mellom 06c lodda etterpå", sc1, k1,
                  [{"type": "innføring", "delar": ["06b"], "vektor_modell": [-1, 0, 0], "lengd_mm": ES1},
                   {"type": "lodding", "delar": ["06b", "L#1", "L#2"]},
                   {"type": "gjennomføring", "delar": ["L#0", "L#3"], "retning": "nedanfrå og opp",
                    "gjennom": "gjennomgangen bak klypa i golvet, bakrommet og hola på r 17 i bereringen", "hjelpemiddel": "trekketråd"},
                   {"type": "innføring", "delar": ["06c"], "vektor_modell": [0, 0, -1], "lengd_mm": EC1},
                   {"type": "lodding", "delar": ["06c", "L#0", "L#3"], "bøylar": TOPP_BOYLAR}],
                  f"Staven: flatstål {fmt(p.stav_b)} × {fmt(p.stav_t)}, kappa {fmt(p.stav_z1 - p.stav_z0)}, ingen hol (H7). "
                  f"Stripa {fmt(p.stripe_z1 - p.stripe_z0)} mm (E1). Den svarte leiaren (GND) er kappa i to bitar, éin frå kvar stripe. "
                  f"Dei fire 06c ligg i parallell: + ytst på alle fire, raud TOPP+ på +-bøylen ved 90°, svart GND på −-bøylen ved "
                  f"270°; bøylar (AWG 28, ca. 15 mm) over skøytane: + ved 0°, 90° og 180°, − ved 0°, 180° og 270°.")

        # ---- 2: rista ned over staven med epoksy i klypa; leiarane gjennom golvet
        ER = 40.0
        o_r = {"C": (0.0, 0.0, ER), "R": (0.0, 0.0, ER)}
        it2 = [It("06", "06"), It("06b", "06b")] + [It(k, "mleiar", (int(k[2]), {}, 5, 16.0)) for k in Lb]
        it2 += [It("07", "07", t=(0, 0, ER), ny=True), It("06c", "06c", t=(0, 0, ER), ny=True)]
        it2 += [It(k, "mleiar", (int(k[2]), o_r, 10, 16.0), ny=True) for k in Lc]
        sc2 = Scene("m2_rista", it2, defl=0.05)
        res = self.hlr(sc2)
        ramme = (P[1][0] + 4, P[1][1] + 8, P[1][0] + 38, P[1][3] - 32)
        k2 = fit_skala(res, ramme)
        f2 = figur(res, ramme, k2)
        f3 = self.f3(sc2, f2)
        s.teikning(res, f2, ny={"07", "06c", "L#0", "L#3"})
        s.hol_pil([f3(polar3(48, V_ISO + 95, p.stav_z1 - 40 + ER)), f3(polar3(48, V_ISO + 95, p.stav_z1 - 40))], w=1.6, hw=4.2, hl=3.4)
        self.merk(s, res, f2, "07", mot=(-1, 0), h=0.45, off=(-6, 0))
        # epoksy etterpå: ein kil mellom undersida av golvet og staven, bak og på sidene (rista er tørr når ho
        # går ned: limfuga i golvet og klypa er 0,2 og ville skrapt av limet heile vegen ned)
        qe = f3((0.0, p.stav_b / 2, p.rist_z0 - 0.5))
        limmerke(qe, qe[0] + 9)
        # detalj: ovanfrå, snitt over golvet, rista nede: dei to gjennomgangane med leiarane
        cG = (-0.9, 0.0, p.rist_z0 + p.golv_t)
        dsc = Scene("dm2_golv", [It("06", "06"), It("07", "07")] + [It(k, "mleiar", (int(k[2]), {}, None, 0.0), ny=True) for k in L4],
                    N=(0.0, 0.0, 1.0), X=(0.0, 1.0, 0.0), kutt={"type": "over", "z": p.rist_z0 + p.golv_t + 1.5},
                    region={"c": cG, "h": 12.0}, defl=0.004)
        bc = (172.0, 84.0)
        f3d = self.detalj(s, dsc, cG, 10.5, bc, 21, main=(f3, (0.0, 0.0, p.rist_z0 + ER), 4.0), ny={"L"})
        self.golvhol(s, f3d, w=0.6)
        gm = self.golvmaal()
        hf, hb_ = gm["framfor"], gm["bak"]
        qf = f3d(((hf[0] + hf[1]) / 2, hf[2] + 0.8, p.rist_z0 + p.golv_t))
        qb = f3d(((hb_[0] + hb_[1]) / 2, hb_[3] - 0.7, p.rist_z0 + p.golv_t))
        s.ballong(qf, (bc[0] - 26, bc[1] + 15), "06b")
        s.ballong(qb, (bc[0] + 21, bc[1] - 23), "06c")
        s.tekst(bc[0], bc[1] + 26.5, "ovanfrå, snitt over golvet", 2.8, "normal", "middle")
        tekstar(P[1], ["Rista tørr ned over staven, stripa mot spaltene: 06b",
                       "og leiarane gjennom golvet framfor staven, leiarane",
                       "frå 06c ut under golvet bak klypa. Rista kviler på",
                       "staven. Legg så ein kil epoksy mellom undersida av",
                       "golvet og staven, bak og på sidene, ikkje framfor",
                       "staven (06b og leiarane). La herde."])
        self.logg(s, "M2", "rista 07 (med 06c) tørr ned over staven til ho kviler på toppen av staven; 06b og leiarane frå 06b "
                  "gjennom gjennomgangen framfor staven, leiarane frå 06c (alt trekte gjennom i M1) under golvet bak klypa; "
                  "deretter ein kil 2K-epoksy (H11) mellom undersida av golvet og staven, bak og på sidene", sc2, k2,
                  [{"type": "innføring", "delar": ["07", "06c", "L#0", "L#3"], "vektor_modell": [0, 0, -1], "lengd_mm": ER,
                    "merknad": "tørr: limfuga i golvet og klypa er 0,2 og ville skrapt av limet"},
                   {"type": "gjennomføring", "delar": ["06b", "L#1", "L#2"], "gjennom": "gjennomgangen framfor staven i golvet", "detalj": "dm2_golv"},
                   {"type": "gjennomføring", "delar": ["L#0", "L#3"], "gjennom": "gjennomgangen bak klypa i golvet", "detalj": "dm2_golv"},
                   {"type": "lim", "delar": ["07", "06"], "lim": "2K-epoksy (H11)",
                    "kvar": "kil mellom undersida av golvet og staven, baksida og sidene; ikkje framfor staven"}],
                  f"Gjennomgangane i golvet (z {fmt(p.rist_z0)}..{fmt(p.rist_z0 + p.golv_t)}), målte på B-rep: "
                  f"framfor staven x {fmt(hf[0])}..{fmt(hf[1])}, y {fmt(hf[2])}..{fmt(hf[3])}; "
                  f"bak klypa x {fmt(hb_[0])}..{fmt(hb_[1])}, y {fmt(hb_[2])}..{fmt(hb_[3])}. Rista kviler på toppen av staven "
                  f"(z {fmt(p.stav_z1)}); sporet i klypa hindrar vriing, kilen held rista når modulen blir løfta i skjørtet.")

        # ---- 3 og 4: snitt gjennom mastfoten (y < 0 er teke vekk), sett bakanfrå til venstre; rista skoren over golvet
        NB = (-0.5, -1.0, 0.35)
        lomme = p.trs_kropp_d + p.mastfot_lomme_klaring
        lomme_p = pp.trs_kropp_d + pp.mastfot_lomme_klaring

        def mf_scene(namn, es, ep, ny_mod, ny_plugg, ny_leiar):
            om = {k: (0.0, 0.0, es) for k in "BSCR"}
            om["P"] = (0.0, 0.0, -ep)
            it = [It(k, k, t=(0, 0, es), ny=ny_mod) for k in ("07", "06", "06b")]
            it += [It("MF", "MF"), It("TRS", "TRS", t=(0, 0, -ep), ny=ny_plugg)]
            it += [It(k, "mleiar", (int(k[2]), om, None, 0.0), ny=ny_leiar) for k in L4]
            kutt = [{"type": "over", "z": p.rist_z0 + p.golv_t + es + 6.0, "delar": ["07", "06", "06b"] + L4},
                    {"type": "utanfor_r", "r": 13.0, "delar": ["07"]},
                    {"type": "snitt", "az": 0.0, "delar": ["MF"]}]
            return Scene(namn, it, N=NB, kutt=kutt, defl=0.008)

        ES3, EP3 = 14.0, 16.0
        sc3 = mf_scene("m3_leiarar", ES3, EP3, False, False, True)
        ES4, EP4 = 12.0, 14.0
        sc4 = mf_scene("m4_lim", ES4, EP4, True, True, False)
        rammer = ((P[2][0] + 16, P[2][1] + 8, P[2][0] + 50, P[2][3] - 22), (P[3][0] + 30, P[3][1] + 8, P[3][0] + 64, P[3][3] - 22))
        k34 = min(fit_skala(self.hlr(sc3), rammer[0]), fit_skala(self.hlr(sc4), rammer[1]))

        # 3: leiarane under golvet rundt staven, ned kanalen bak staven og gjennom lomma; lodd til pluggen
        res = self.hlr(sc3)
        f2 = figur(res, rammer[0], k34)
        f3 = self.f3(sc3, f2)
        s.teikning(res, f2, ny={"L"})
        self.golvhol(s, f3, dz=ES3, kva=("bak",), w=0.5)
        self.merk(s, res, f2, "MF", tekst="06d", mot=(-1, 0), h=0.4, off=(-9, 0))
        self.merk(s, res, f2, "07", mot=(-1, 0), h=0.3, off=(-6, -8))
        self.merk(s, res, f2, "06", mot=(-1, 0), h=0.55, off=(-13, 0))
        xr = max(q[0] for q in (f3(leiar_loddepunkt(p, j, EP3)) for j in range(4))) + 10
        ank = sorted(((f3(add(leiar_loddepunkt(p, j, EP3), (0, 0, 1.0))), ("TOPP+", "SIDE+", "GND")[j]) for j in range(3)),
                     key=lambda t: t[0][1])
        ym = sum(q[1] for q, _ in ank) / 3
        for j, (q, namn) in enumerate(ank):
            yt = ym + (j - 1) * 4.6
            s.linje([q, (xr - 1, yt - 1.0)], W_FIN)
            s.el.append(f'<circle cx="{q[0]:.2f}" cy="{q[1]:.2f}" r="0.45" fill="#000"/>')
            s.tekst(xr, yt, namn + (" ×2" if namn == "GND" else ""), 2.8, "bold")
        xk = -p.stav_t / 2 - 0.05 - p.mastfot_kanal / 2
        qk = f3((xk, 0.0, (p.mastfot_z1 + p.stav_z0) / 2))
        s.linje([qk, (qk[0] + 18, qk[1] - 14)], W_FIN)
        s.el.append(f'<circle cx="{qk[0]:.2f}" cy="{qk[1]:.2f}" r="0.45" fill="#000"/>')
        s.tekst(qk[0] + 19, qk[1] - 14.6, "kanalen bak", 2.6)
        s.tekst(qk[0] + 19, qk[1] - 11.2, "staven", 2.6)
        self.plugg_skjema(s, P[2][0] + 54, P[2][1] + 16, 32)
        tekstar(P[2], ["Under golvet: leiarane rundt staven til kanalen bak",
                       "han i mastfoten, gjennom lomma og ut nedst. Lodd:",
                       "tupp = TOPP+ (raud), ring = SIDE+ (blå),",
                       "hylse = GND (båe svarte)."])
        self.logg(s, "M3", "leiarane under golvet rundt staven til kanalen bak staven i mastfoten, gjennom lomma og ut nedst; "
                  "lodda til pluggen: tupp = TOPP+ (raud), ring = SIDE+ (blå), hylse = GND (båe svarte)", sc3, k34,
                  [{"type": "gjennomføring", "delar": L4, "gjennom": "kanalen bak staven i mastfoten og lomma"},
                   {"type": "lodding", "delar": L4 + ["TRS"]}],
                  f"Snitt gjennom mastfoten i planet y = 0. Kanalen er {fmt(p.mastfot_kanal)} mm brei bak staven (−X) og går ned i lomma. "
                  f"Rista er teikna skoren over golvet og utanfor r 13.")

        # 4: pluggkroppen opp i lomma, modulen (staven) ned i sporet, båe med epoksy
        res = self.hlr(sc4)
        f2 = figur(res, rammer[1], k34)
        f3 = self.f3(sc4, f2)
        s.teikning(res, f2, ny={"07", "06", "06b", "TRS"})
        xa = p.mastfot_b / 2 + 4.0
        s.hol_pil([f3((xa, 0, p.mastfot_z0 - EP4 - 2)), f3((xa, 0, p.mastfot_z0 - 1.5))], w=1.6, hw=4.2, hl=3.4)
        s.hol_pil([f3((17.0, 0, p.stav_z0 + ES4 + 30)), f3((17.0, 0, p.stav_z0 + 14.0))], w=1.6, hw=4.2, hl=3.4)
        for q3 in ((-p.trs_kropp_d / 2 + 0.6, 0.0, p.mastfot_z0 + 6.0), (-p.stav_t / 2, 0.0, p.stav_z0 + ES4 + 3.0)):
            limmerke(f3(q3), rammer[1][0] - 22)
        self.merk(s, res, f2, "MF", tekst="06d", mot=(1, 0), h=0.5, off=(17, 4))
        tekstar(P[3], [f"Epoksy i lomma (Ø{fmt(lomme)}, prototype Ø{fmt(lomme_p)}): pluggen opp",
                       "til kroppen er i flukt med underkanten. Epoksy på",
                       "staven: ned i sporet til han kviler på golvet. Legg",
                       "slakken under golvet, bak staven. La herde."])
        self.logg(s, "M4", "pluggkroppen limt i lomma nedanfrå (epoksy), modulen ned med staven limt i sporet til han kviler på golvet", sc4, k34,
                  [{"type": "innføring+lim", "delar": ["TRS"], "vektor_modell": [0, 0, 1], "lengd_mm": EP4, "lim": "2K-epoksy (H11)"},
                   {"type": "innføring+lim", "delar": ["06", "06b", "07"], "vektor_modell": [0, 0, -1], "lengd_mm": ES4, "lim": "2K-epoksy (H11)"}],
                  f"Lomma Ø{fmt(lomme)} (prototype Ø{fmt(lomme_p)}) frå underkanten (z {fmt(p.mastfot_z0)}) opp til z {fmt(p.stav_z0)}; "
                  f"stavsporet {fmt(p.stav_t + 0.1)} × {fmt(p.stav_b + 0.1)} frå z {fmt(p.stav_z0)} til toppen. "
                  f"Staven kviler på golvet utanfor lomma (|y| > {fmt(lomme / 2)}). Modulen er no éi limt eining.")


# =============================================================================== utskrift
def skriv(rett: Rettleiing):
    import cairosvg
    from pypdf import PdfReader, PdfWriter

    SIDER.mkdir(parents=True, exist_ok=True)
    for f in list(UT.glob("side-*.png")) + list(SIDER.glob("side-*.png")):
        try:
            f.unlink()
        except OSError:
            pass
    n = len(rett.sider)
    kart = {s.namn: i for i, s in enumerate(rett.sider, 1)}
    w = PdfWriter()
    for i, s in enumerate(rett.sider, 1):
        svg = s.svg(i, n, kart).encode("utf-8")
        cairosvg.svg2png(bytestring=svg, write_to=str(SIDER / f"side-{i:02d}-{s.namn}.png"), dpi=150)
        buf = io.BytesIO()
        cairosvg.svg2pdf(bytestring=svg, write_to=buf)
        buf.seek(0)
        for pg in PdfReader(buf).pages:
            w.add_page(pg)
    w.add_metadata({"/Title": f"FYR montering og service {REVISJON} ({DATO})", "/Subject": "Monteringsrettleiing teikna frå CAD (HLR)"})
    with open(UT / "FYR_montering.pdf", "wb") as fh:
        w.write(fh)
    p = rett.p
    man = {"produkt": "FYR", "revisjon": REVISJON, "dato": DATO, "variant": p.variant,
           "sider": {s.namn: i for i, s in enumerate(rett.sider, 1)},
           "koordinatar": "mm, z = 0 bordplata, lampeaksen = z, asimut 0 = +X = vindauget (framme), positiv mot klokka sett ovanfrå",
           "kamera_standard": {"retning_mot_betraktar": list(norm(ISO)), "projeksjon": "parallell (HLRAlgo_Projector)"},
           "geometri_hash": rett.hlr.hash, "utdaterte_scener": rett.hlr.utdaterte, "strekkavlastning": rett.info, "brytarar": [{"namn": n, "asimut": a, "terskel_theta": t_} for n, (a, t_) in zip(rett.p.sw_namn, rett.p.sw)], "tilstandar": rett.tilstandar(),
           "steg": rett.manifest}
    (UT / "scener.json").write_text(sidetal(json.dumps(man, indent=1, ensure_ascii=False), kart), encoding="utf-8")


def main():
    t0 = time.time()
    bruk = "--utan-cache" not in sys.argv
    p = g.FyrParams()
    hlr = HLR(p, bruk)
    r = Rettleiing(p, hlr)
    r.bygg()
    skriv(r)
    print(f"ferdig: {len(r.sider)} sider, {time.time() - t0:.1f} s  -> {UT}", flush=True)
    if hlr.utdaterte:
        print("ÅTVARING: eldre projeksjonar brukte for:", ", ".join(hlr.utdaterte), flush=True)


if __name__ == "__main__":
    main()
