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


def kropp_dxf(sti: Path, p=P0, flik=10.0):
    """Flatmønster for D01. s = 0 og s = L er saumen i nasen; påløps- og avløpsflikar
    (flik x flik mm) ved toppkanten og underkanten av skjermen blir skorne av etter sveising."""
    f = kropp_flat(p)
    L, sa, sb, ha, hb = f["L"], f["sa"], f["sb"], f["ha"], f["hb"]
    S, zs, r, zh, rh = p.S, p.z_skjerm, p.r_inn, p.z_hakk, p.r_hakk
    (fa0, fa1), (fb0, fb1) = f["flens"]
    zf = f["z_fl2"]
    avl, avl_h = p.fl_avl, p.fl_avl_h
    b90 = _bulge(90)
    P = [(0.0, zs - flik, 0), (0.0, S + flik, 0), (flik, S + flik, 0), (flik, S, 0),
         (L - flik, S, 0), (L - flik, S + flik, 0), (L, S + flik, 0), (L, zs - flik, 0),
         (L - flik, zs - flik, 0), (L - flik, zs, 0),
         (sb + r, zs, b90), (sb, zs - r, 0), (sb, zf, 0), (fb0, zf, 0), (fb0, avl_h, 0),
         (fb0 - avl, avl_h, 0), (fb0 - avl, 0.0, 0),
         (hb, 0.0, 0), (hb, zh - rh, b90), (hb - rh, zh, 0), (ha + rh, zh, b90), (ha, zh - rh, 0),
         (ha, 0.0, 0), (fa1 + avl, 0.0, 0), (fa1 + avl, avl_h, 0), (fa1, avl_h, 0), (fa1, zf, 0),
         (sa, zf, 0), (sa, zs - r, b90), (sa - r, zs, 0), (flik, zs, 0), (flik, zs - flik, 0)]
    doc = _ny()
    msp = doc.modelspace()
    msp.add_lwpolyline([(x, z, 0, 0, bb) for x, z, bb in P], format="xyseb", close=True,
                       dxfattribs={"layer": "SKJER"})
    sf, sbk = f["s_framme"], f["s_bak"]
    for s_ in (sf(p.pkt_x), sbk(p.pkt_x)):
        msp.add_circle((s_, p.pkt_z), p.pkt_hol / 2, dxfattribs={"layer": "SKJER"})
    d_inn = (p.R - p.fl_yc) - (p.fl_ri + p.t)
    zhol = f["z_fl1"] - d_inn
    bx, by = 3.4, 5.0
    for x in p.fot_x:
        for s_ in (sf(x), sbk(x)):     # spor langs z (y i 3D)
            rr = bx / 2
            msp.add_lwpolyline([(s_ - rr, zhol - by / 2 + rr, 0, 0, 0), (s_ - rr, zhol + by / 2 - rr, 0, 0, -1),
                                (s_ + rr, zhol + by / 2 - rr, 0, 0, 0), (s_ + rr, zhol - by / 2 + rr, 0, 0, -1)],
                               format="xyseb", close=True, dxfattribs={"layer": "SKJER"})
    zb = f["z_v"] - f["BA"] / 2
    for a, b in f["flens"]:
        msp.add_line((a, zb), (b, zb), dxfattribs={"layer": "BOY"})
    for i, (a, b) in enumerate(f["s_boge"]):
        for s_ in (a, b):
            if s_ in (0.0, L):
                continue
            msp.add_line((s_, 0.0 if i == 1 else zs), (s_, S), dxfattribs={"layer": "VALS"})
    msp.add_text(f"SVEIP D01 KROPP  EN AW-5754 H22  t={p.t}  1:1 mm  L={L:.2f}  K bogar 0,5 / flens {p.K_flens}",
                 height=4, dxfattribs={"layer": "TEKST"}).set_placement((5, S + flik + 6))
    msp.add_text("SAUM i nasen: s=0 / s=L, laser-buttsveis med flikar, skjer flikane av og slip. "
                 "BOY: 90 gr ri=%.1f innover.  VALS: 180 gr Ri=%.1f" % (p.fl_ri, p.R - p.t),
                 height=3, dxfattribs={"layer": "TEKST"}).set_placement((5, S + flik + 12))
    msp.add_line((0, S + flik + 20), (100, S + flik + 20), dxfattribs={"layer": "TEKST"})
    doc.saveas(sti)
    return dict(L=L, H=S - zf, blank_mm=(round(L, 2), round(S + flik - zf, 2)), saum="nasen (s = 0 og s = L)",
                hakk_s=(round(ha, 2), round(hb, 2)), stamme_s=(round(sa, 2), round(sb, 2)),
                flens_s=[(round(a, 2), round(b, 2)) for a, b in f["flens"]],
                valsesoner_s=[(round(a, 2), round(b, 2)) for a, b in f["s_boge"]],
                hol_s_z=dict(punkt=[(round(sf(p.pkt_x), 2), p.pkt_z), (round(sbk(p.pkt_x), 2), p.pkt_z)],
                             spor=[(round(s_, 2), round(zhol, 2)) for x in p.fot_x for s_ in (sf(x), sbk(x))]))


def chassis_dxf(sti: Path, p=P0, K=0.44):
    """Utbretting av chassiset: fem felt, fire 90-gradarsbøyar langs, og to sideflensar på ryggen."""
    from sveip_kropp import RYGG_FLENS, chassis_b
    pts = chassis_senterline(p)
    tc, ri = p.tc, p.rc_i
    rc = ri + tc / 2
    BA = math.pi / 2 * (ri + K * tc)
    seg = []
    for i in range(len(pts) - 1):
        L = math.dist(pts[i], pts[i + 1])
        if i > 0:
            L -= rc
        if i < len(pts) - 2:
            L -= rc
        seg.append(L)
    b = chassis_b(p)
    R_env = p.R - p.t - p.klaring
    starts, u = [], 0.0
    for i, L in enumerate(seg):
        starts.append(u)
        u += L + (BA if i < len(seg) - 1 else 0.0)
    total = u
    x_tan = pts[1][0] - rc

    def tak_u(x):
        return seg[0] - (x_tan - x)

    def botn_u(x):
        return starts[2] + (x - (pts[2][0] + rc))

    def rygg_u(z):
        return starts[3] + (z - (pts[3][1] + rc))

    def flens_u(x):
        return starts[4] + ((pts[4][0] - rc) - x)

    # sideflensane: frå z_a til z_b, utbretta breidd = BA + flat del
    z_a = pts[2][1] + tc / 2 + ri + 3.0
    z_b = pts[4][1] - tc / 2 - ri - 3.0
    ua, ub = rygg_u(z_a), rygg_u(z_b)
    web = b - (ri + tc)                       # bøyetangent på ryggen (|y|)
    ytter = web + BA + (RYGG_FLENS - (ri + tc))
    venstre = []
    n = 40
    for k in range(n + 1):
        y = -b + 2 * b * k / n
        xl = min(p.R - math.sqrt(max(R_env ** 2 - y ** 2, 0.0)), p.x_hakk)   # som i 3D: full breidd frå hakkanten
        venstre.append((max(tak_u(xl), 0.0), y))
    sl = 0.5                                 # avlastingsslisse ved enden av sideflensane
    poly = [(venstre[0][0], -b)] + venstre[1:-1] + [(venstre[-1][0], b),
            (ua - sl, b), (ua - sl, ytter), (ub + sl, ytter), (ub + sl, b),
            (total, b), (total, -b),
            (ub + sl, -b), (ub + sl, -ytter), (ua - sl, -ytter), (ua - sl, -b)]
    doc = _ny()
    msp = doc.modelspace()
    msp.add_lwpolyline(poly, close=True, dxfattribs={"layer": "SKJER"})
    for sy in (-1, 1):                         # avlastingsslissar inn til bøyelina
        for uu in (ua - sl, ub):
            msp.add_lwpolyline([(uu, sy * (web - 0.5)), (uu + sl, sy * (web - 0.5)),
                                (uu + sl, sy * b), (uu, sy * b)], close=True, dxfattribs={"layer": "SKJER"})
        msp.add_line((ua, sy * (web + BA / 2)), (ub, sy * (web + BA / 2)), dxfattribs={"layer": "BOY"})
    for i in range(len(seg) - 1):
        ubb = starts[i] + seg[i] + BA / 2
        msp.add_line((ubb, -b), (ubb, b), dxfattribs={"layer": "BOY"})

    def hol(uu, y, d, lag="SKJER"):
        msp.add_circle((uu, y), d / 2, dxfattribs={"layer": lag})

    b05 = _bulge(90)
    u0 = tak_u(p.usb_x)
    msp.add_lwpolyline([(u0 - 1.45, -4.8, 0, 0, 0), (u0 + 1.45, -4.8, 0, 0, b05), (u0 + 1.95, -4.3, 0, 0, 0),
                        (u0 + 1.95, 4.3, 0, 0, b05), (u0 + 1.45, 4.8, 0, 0, 0), (u0 - 1.45, 4.8, 0, 0, b05),
                        (u0 - 1.95, 4.3, 0, 0, 0), (u0 - 1.95, -4.3, 0, 0, b05)],
                       format="xyseb", close=True, dxfattribs={"layer": "SKJER"})
    for y in (-USB_YS, USB_YS):
        hol(u0, y, 4.22, "PEM")
    for sy in (-1, 1):
        for x in p.fot_x:
            hol(botn_u(x), sy * p.fl_yc, 4.22, "PEM")
    for x, y in HK_HOL:
        hol(botn_u(x), y, 3.4)
    for x, y in LUKE_SKRUAR:
        hol(botn_u(x), y, 4.22, "PEM")
    for y in BK_Y:
        hol(rygg_u(p.pkt_z), y, 4.22, "PEM")
    for x, y in MODUL_HOL:
        hol(flens_u(x), y, 4.22, "PEM")
    x0, x1, lb = LUKE_OPNING
    ua_, ub_ = botn_u(x0), botn_u(x1)
    rr = 3.0
    msp.add_lwpolyline([(ua_ + rr, -lb / 2, 0, 0, 0), (ub_ - rr, -lb / 2, 0, 0, b05), (ub_, -lb / 2 + rr, 0, 0, 0),
                        (ub_, lb / 2 - rr, 0, 0, b05), (ub_ - rr, lb / 2, 0, 0, 0), (ua_ + rr, lb / 2, 0, 0, b05),
                        (ua_, lb / 2 - rr, 0, 0, 0), (ua_, -lb / 2 + rr, 0, 0, b05)],
                       format="xyseb", close=True, dxfattribs={"layer": "SKJER"})
    msp.add_text(f"SVEIP D02 CHASSIS  EN AW-5754 H22  t={tc}  6 x 90 gr ri={ri}  K={K}  PEM: CLS-M3-2 / SO-M3-3 "
                 "(lag PEM, pressast før bøying, hovud på innsida)", height=3,
                 dxfattribs={"layer": "TEKST"}).set_placement((0, ytter + 6))
    doc.layers.add("PEM", color=6)
    doc.saveas(sti)
    return dict(utbretta_mm=(round(total, 2), round(2 * ytter, 2)), felt_mm=[round(s_, 2) for s_ in seg],
                BA=round(BA, 3), sideflens_u=(round(ua, 2), round(ub, 2)))


def _kjede(kantar, tol=1e-3):
    """Set saman kantar (punktlister) til lukka kjeder."""
    kantar = [list(k) for k in kantar]
    kjeder = []
    while kantar:
        k = kantar.pop(0)
        endra = True
        while endra and kantar:
            endra = False
            for i, e in enumerate(kantar):
                if math.dist(k[-1], e[0]) < tol:
                    k += e[1:]; kantar.pop(i); endra = True; break
                if math.dist(k[-1], e[-1]) < tol:
                    k += e[::-1][1:]; kantar.pop(i); endra = True; break
        kjeder.append(k)
    return kjeder


def enkel_dxf(sti: Path, form, tekst, pem_r=2.11):
    """DXF frå ei flat form: lukka konturar frå snittet midt i plata. Hol med radius pem_r
    blir lagde på laget PEM."""
    import cadquery as cq
    s = form.val()
    bb = s.BoundingBox()
    snitt = cq.Workplane("XY").add(s).section(bb.zmin + 0.5 * min(bb.zlen, 1.0))
    kantar = []
    sirklar = []
    for e in snitt.edges().vals():
        if e.geomType() == "CIRCLE" and e.IsClosed():
            c = e.Center()
            sirklar.append(((c.x, c.y), e.radius()))
            continue
        n = 48 if e.geomType() != "LINE" else 1
        kantar.append([(e.positionAt(i / n).x, e.positionAt(i / n).y) for i in range(n + 1)])
    doc = _ny()
    doc.layers.add("PEM", color=6)
    msp = doc.modelspace()
    for k in _kjede(kantar):
        msp.add_lwpolyline(k, close=True, dxfattribs={"layer": "SKJER"})
    for (x, y), r in sirklar:
        msp.add_circle((x, y), r, dxfattribs={"layer": "PEM" if abs(r - pem_r) < 0.02 else "SKJER"})
    msp.add_text(tekst, height=3, dxfattribs={"layer": "TEKST"}).set_placement((bb.xmin, bb.ymax + 5))
    doc.saveas(sti)
    return dict(maal_mm=(round(bb.xlen, 2), round(bb.ylen, 2)), konturar=len(_kjede(kantar)), sirklar=len(sirklar))


def mal_pdf(dxf: Path, ut: Path, side=(420.0, 297.0), marg=12.0):
    """1:1-mal av eit flatmønster, flislagd over A3-sider med passmerke og 100 mm kontrollmål.
    Skriv ut i 100 % (ikkje «tilpass side»)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf import path as epath
    from matplotlib.backends.backend_pdf import PdfPages
    doc = ezdxf.readfile(dxf)
    liner = []
    for e in doc.modelspace():
        if e.dxftype() in ("LWPOLYLINE", "LINE", "CIRCLE") and e.dxf.layer != "TEKST":
            pts = [(v.x, v.y) for v in epath.make_path(e).flattening(0.05)]
            liner.append((pts, e.dxf.layer))
    xs = [p[0] for pts, _ in liner for p in pts]
    ys = [p[1] for pts, _ in liner for p in pts]
    x0, y0, x1, y1 = min(xs) - 5, min(ys) - 5, max(xs) + 5, max(ys) + 5
    bw, bh = side[0] - 2 * marg, side[1] - 2 * marg - 8
    nx = math.ceil((x1 - x0) / bw)
    ny = math.ceil((y1 - y0) / bh)
    with PdfPages(ut) as pdf:
        for j in range(ny):
            for i in range(nx):
                fig = plt.figure(figsize=(side[0] / 25.4, side[1] / 25.4))
                ax = fig.add_axes([0, 0, 1, 1])
                ax.set_xlim(0, side[0]); ax.set_ylim(0, side[1]); ax.axis("off")
                ox, oy = x0 + i * bw, y0 + j * bh
                for pts, lag in liner:
                    farge = {"SKJER": "k", "BOY": "#c00", "VALS": "#06c"}.get(lag, "k")
                    ax.plot([marg + p[0] - ox for p in pts], [marg + 8 + p[1] - oy for p in pts], color=farge,
                            lw=0.6 if lag == "SKJER" else 0.4, ls="-" if lag == "SKJER" else (0, (6, 3)))
                ax.add_patch(plt.Rectangle((marg, marg + 8), bw, bh, fill=False, lw=0.3, ls=(0, (2, 2)), color="#888"))
                for cx, cy in ((marg, marg + 8), (marg + bw, marg + 8), (marg, marg + 8 + bh), (marg + bw, marg + 8 + bh)):
                    ax.plot([cx - 4, cx + 4], [cy, cy], color="k", lw=0.4)
                    ax.plot([cx, cx], [cy - 4, cy + 4], color="k", lw=0.4)
                ax.plot([marg, marg + 100], [marg + 2, marg + 2], color="k", lw=0.8)
                ax.text(marg + 102, marg + 1, "100 mm: kontroller utskrifta (100 %, ikkje tilpass)", fontsize=6)
                ax.text(side[0] - marg, marg + 1, f"Sveip D01 · mal 1:1 · side {j * nx + i + 1} av {nx * ny} "
                        f"(kolonne {i + 1}, rad {j + 1}) · skjer langs stipla ramme og legg kant i kant",
                        fontsize=6, ha="right")
                pdf.savefig(fig)
                plt.close(fig)
    return nx * ny
