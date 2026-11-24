# -*- coding: utf-8 -*-
"""Flatmønster (DXF 1:1, mm) for platedelane i Sveip.

Lag: SKJER (7, kvit/svart) = laserskjering, BOY (1, raud) = bøyeliner for kantpresse,
VALS (5, blå) = start/slutt for 180-graders bogar (R51 innvendig), TEKST (3) = merking.
K-faktor 0,5 for bogane (R/t > 40), 0,44 for 90-gradars bøyar med r = t.
"""
from __future__ import annotations

import math
from pathlib import Path

import ezdxf

from sveip_geometri import P0
from sveip_kropp import (BK_Y, HK_HOL, LUKE_OPNING, LUKE_SKRUAR, MODUL_HOL, USB_YS,
                         chassis_senterline, kropp_flat)


def _ny():
    d = ezdxf.new("R2010")
    d.units = ezdxf.units.MM
    for namn, farge in (("SKJER", 7), ("BOY", 1), ("VALS", 5), ("TEKST", 3)):
        d.layers.add(namn, color=farge)
    return d


def _bulge(vinkel_grad):
    return math.tan(math.radians(vinkel_grad) / 4.0)


def kropp_dxf(sti: Path, p=P0):
    f = kropp_flat(p)
    L, sa, sb, ha, hb = f["L"], f["sa"], f["sb"], f["ha"], f["hb"]
    S, zs, r, zh, rh = p.S, p.z_skjerm, p.r_inn, p.z_hakk, p.r_hakk
    (fa0, fa1), (fb0, fb1) = f["flens"]
    zf = f["z_fl2"]
    avl, avl_h = p.fl_avl, p.fl_avl_h
    # omrisset, rundt med klokka frå (0, S): punkt (s, z, bulge til neste)
    P = []
    P += [(0.0, S, 0), (L, S, 0), (L, zs, 0)]
    # under skjermen frå høgre: bakre stamme byrjar i sb (R12 inn mot stamma)
    P += [(sb + r, zs, _bulge(90)), (sb, zs - r, 0)]
    # bakre stamme ned til flensen (sb = x_stamme bak); flensen går til fb0
    P += [(sb, zf, 0), (fb0, zf, 0)]
    # avlastingsspor framfor bakre flens (mot bogen)
    P += [(fb0, avl_h, 0), (fb0 - avl, avl_h, 0), (fb0 - avl, 0.0, 0)]
    # botnkant bort til hakket (bak), hakket med R7 i hjørna
    P += [(hb, 0.0, 0), (hb, zh - rh, _bulge(90)), (hb - rh, zh, 0),
          (ha + rh, zh, _bulge(90)), (ha, zh - rh, 0), (ha, 0.0, 0)]
    # botnkant til avlastingsspor framfor framre flens
    P += [(fa1 + avl, 0.0, 0), (fa1 + avl, avl_h, 0), (fa1, avl_h, 0), (fa1, zf, 0)]
    P += [(sa, zf, 0), (sa, zs - r, _bulge(90)), (sa - r, zs, 0), (0.0, zs, 0)]
    doc = _ny()
    msp = doc.modelspace()
    pts = [(x, z, 0, 0, b) for x, z, b in P]
    msp.add_lwpolyline(pts, format="xyseb", close=True, dxfattribs={"layer": "SKJER"})
    # hol: berøringspunkt (framme og bak), flenshol
    sf, sbk = f["s_framme"], f["s_bak"]
    msp.add_circle((sf(p.pkt_x), p.pkt_z), p.pkt_hol / 2, dxfattribs={"layer": "SKJER"})
    msp.add_circle((sbk(p.pkt_x), p.pkt_z), p.pkt_hol / 2, dxfattribs={"layer": "SKJER"})
    # flenshol: avstand frå flat flensstart (z_fl1) = fl_yc - (R - fl_b) ... målt frå ytterflata
    d_inn = (p.R - p.fl_yc) - (p.fl_ri + p.t)           # frå flat start til holsenter
    zhol = f["z_fl1"] - d_inn
    for x in p.skrue_x:
        for s_ in (sf(x), sbk(x)):
            msp.add_circle((s_, zhol), 1.7, dxfattribs={"layer": "SKJER"})
    for x in p.fot_x:
        for s_ in (sf(x), sbk(x)):
            msp.add_circle((s_, zhol), 2.1, dxfattribs={"layer": "SKJER"})
    # bøyeliner for flensane (midt i bøyesona), valsesoner for bogane
    zb = f["z_v"] - f["BA"] / 2
    for a, b in f["flens"]:
        msp.add_line((a, zb), (b, zb), dxfattribs={"layer": "BOY"})
    for i, (a, b) in enumerate(f["s_boge"]):
        for s_ in (a, b):
            msp.add_line((s_, zs if i == 0 else 0.0), (s_, S), dxfattribs={"layer": "VALS"})
    msp.add_text(f"SVEIP D01 KROPP  EN AW-5754 H22  t={p.t}  1:1 mm  L={L:.2f}  K=0,5",
                 height=4, dxfattribs={"layer": "TEKST"}).set_placement((5, S + 6))
    msp.add_text("SAUM: s=0 / s=L (laser butt, slipast)  BOY: 90 gr ri=%.1f innover  VALS: 180 gr Ri=%.1f"
                 % (p.fl_ri, p.R - p.t), height=3, dxfattribs={"layer": "TEKST"}).set_placement((5, S + 12))
    # 100 mm kontrollmål
    msp.add_line((0, S + 20), (100, S + 20), dxfattribs={"layer": "TEKST"})
    doc.saveas(sti)
    return dict(L=L, H=S - zf, blank_mm=(round(L, 2), round(S - zf, 2)), s_saum=0.0,
                hakk_s=(round(ha, 2), round(hb, 2)), stamme_s=(round(sa, 2), round(sb, 2)),
                flens_s=[(round(a, 2), round(b, 2)) for a, b in f["flens"]],
                valsesoner_s=[(round(a, 2), round(b, 2)) for a, b in f["s_boge"]])


def chassis_dxf(sti: Path, p=P0, K=0.44):
    """Utbretting av chassiset: fem flate felt og fire 90-graders bøyar."""
    pts = chassis_senterline(p)
    tc, ri = p.tc, p.rc_i
    rc = ri + tc / 2
    BA = math.pi / 2 * (ri + K * tc)
    # lengder på flate felt (senterline mellom tangentpunkt)
    seg = []
    for i in range(len(pts) - 1):
        L = math.dist(pts[i], pts[i + 1])
        if i > 0:
            L -= rc
        if i < len(pts) - 2:
            L -= rc
        seg.append(L)
    b = p.D / 2 - p.t - 2.5
    R_env = p.R - p.t - p.klaring
    # felt 0 (taket) må kortast til konvolutten: venstre ende følgjer sirkelen
    doc = _ny()
    msp = doc.modelspace()
    u = 0.0
    starts = []
    for i, L in enumerate(seg):
        starts.append(u)
        u += L + (BA if i < len(seg) - 1 else 0.0)
    total = u
    # omriss: rektangel u = 0..total, y = -b..b, men taket (felt 0) sin frie ende er boga
    # taket: u = 0 svarar til x = pts[0][0] (= 0), tangentpunktet til x = pts[1][0] - rc
    x_tan = pts[1][0] - rc
    n = 40
    venstre = []
    for k in range(n + 1):
        y = -b + 2 * b * k / n
        xl = p.R - math.sqrt(max(R_env ** 2 - y ** 2, 0.0))
        venstre.append((max(x_tan - xl, 0.0), y))
    # u for taket = seg0 - (x_tan - x)  ->  fri ende når x = xl
    omriss = [(seg[0] - uu, y) for uu, y in venstre]
    omriss = [(max(uu, 0.0), y) for uu, y in omriss]
    poly = [(omriss[0][0], -b)] + omriss[1:-1] + [(omriss[-1][0], b), (total, b), (total, -b)]
    msp.add_lwpolyline(poly, close=True, dxfattribs={"layer": "SKJER"})
    for i in range(len(seg) - 1):
        ub = starts[i] + seg[i] + BA / 2
        msp.add_line((ub, -b), (ub, b), dxfattribs={"layer": "BOY"})

    def u_av(felt, d):  # d = avstand frå starten av feltet (frå førre bøy)
        return starts[felt] + d

    # tak (felt 0): x minkar med u; d frå fri ende... bruk avstand frå bøyen
    def tak_u(x):
        return seg[0] - (x_tan - x)

    def botn_u(x):   # felt 2: x frå (vegg + rc) mot ryggen
        return starts[2] + (x - (pts[2][0] + rc))

    def rygg_u(z):   # felt 3: z frå botn + rc
        return starts[3] + (z - (pts[3][1] + rc))

    def flens_u(x):  # felt 4: x minkar frå ryggen
        return starts[4] + ((pts[4][0] - rc) - x)

    hol = []
    hol.append(("USB 3,9 x 9,6", tak_u(p.usb_x), 0.0, "slot"))
    for y in (-USB_YS, USB_YS):
        hol.append(("SO-M3", tak_u(p.usb_x), y, 4.22))
    for sy in (-1, 1):
        for x in p.skrue_x:
            hol.append(("CLS-M3", botn_u(x), sy * p.fl_yc, 4.22))
        for x in p.fot_x:
            hol.append(("fot", botn_u(x), sy * p.fl_yc, 7.0))
    for x, y in HK_HOL:
        hol.append(("M3", botn_u(x), y, 3.4))
    for x, y in LUKE_SKRUAR:
        hol.append(("CLS-M3", botn_u(x), y, 4.22))
    for y in BK_Y:
        hol.append(("SO-M3", rygg_u(p.pkt_z), y, 4.22))
    for x, y in MODUL_HOL:
        hol.append(("CLS-M3", flens_u(x), y, 4.22))
    for namn, uu, y, d in hol:
        if d == "slot":
            msp.add_lwpolyline([(uu - 1.95, y - 4.8), (uu + 1.95, y - 4.8), (uu + 1.95, y + 4.8),
                                (uu - 1.95, y + 4.8)], close=True, dxfattribs={"layer": "SKJER"})
        else:
            msp.add_circle((uu, y), d / 2, dxfattribs={"layer": "SKJER"})
    x0, x1, lb = LUKE_OPNING
    msp.add_lwpolyline([(botn_u(x0), -lb / 2), (botn_u(x1), -lb / 2), (botn_u(x1), lb / 2),
                        (botn_u(x0), lb / 2)], close=True, dxfattribs={"layer": "SKJER"})
    msp.add_text(f"SVEIP D02 CHASSIS  EN AW-5754 H22  t={tc}  4 x 90 gr ri={ri}  K={K}",
                 height=3, dxfattribs={"layer": "TEKST"}).set_placement((0, b + 6))
    doc.saveas(sti)
    return dict(utbretta_mm=(round(total, 2), round(2 * b, 2)), felt_mm=[round(s_, 2) for s_ in seg],
                BA=round(BA, 3), hol=len(hol) + 1)


def enkel_dxf(sti: Path, form, tekst):
    """DXF frå ei flat form: skjer omrisset av undersida (z = zmin)."""
    import cadquery as cq
    s = form.val()
    bb = s.BoundingBox()
    snitt = cq.Workplane("XY").add(s).section(bb.zmin + 0.5 * min(bb.zlen, 1.0))
    doc = _ny()
    msp = doc.modelspace()
    for e in snitt.edges().vals():
        pts = [e.positionAt(i / 48.0) for i in range(49)]
        msp.add_lwpolyline([(v.x, v.y) for v in pts], dxfattribs={"layer": "SKJER"})
    msp.add_text(tekst, height=3, dxfattribs={"layer": "TEKST"}).set_placement((bb.xmin, bb.ymax + 5))
    doc.saveas(sti)
    return dict(maal_mm=(round(bb.xlen, 2), round(bb.ylen, 2)))
