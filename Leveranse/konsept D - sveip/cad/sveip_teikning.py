# -*- coding: utf-8 -*-
"""Tekniske teikningar av Sveip frå CAD-en: skjulte liner fjerna (OCP HLR).

Køyr frå cad/: python sveip_teikning.py
Skriv teikning/sveip_teikningar.pdf og teikning/side-NN.png (A3 liggjande).
Projeksjon ISO E (første vinkel). Mål i mm.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from lagprio import lag_prioritet  # noqa: E402

lag_prioritet()

import cadquery as cq  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from OCP.BRepAdaptor import BRepAdaptor_Curve  # noqa: E402
from OCP.BRepLib import BRepLib  # noqa: E402
from OCP.GCPnts import GCPnts_QuasiUniformDeflection  # noqa: E402
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt  # noqa: E402
from OCP.HLRAlgo import HLRAlgo_Projector  # noqa: E402
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape  # noqa: E402
from OCP.TopAbs import TopAbs_EDGE  # noqa: E402
from OCP.TopExp import TopExp_Explorer  # noqa: E402
from OCP.TopoDS import TopoDS  # noqa: E402

import sveip_samanstilling as SA  # noqa: E402
from sveip_geometri import P0  # noqa: E402
from sveip_kropp import kropp_flat  # noqa: E402

ROT = Path(__file__).resolve().parent.parent
UT = ROT / "teikning"
UT.mkdir(exist_ok=True)
REPO = ROT.parent.parent
FONT = None
for kand in [REPO / "grunnlag/leveransar/01_fase1_sider/fonts/EBGaramond12-Regular.otf",
             REPO / "leveransar/01_fase1_sider/fonts/EBGaramond12-Regular.otf"]:
    if kand.exists():
        font_manager.fontManager.addfont(str(kand))
        FONT = font_manager.FontProperties(fname=str(kand)).get_name()
        break
plt.rcParams["font.family"] = FONT or "DejaVu Serif"
plt.rcParams["font.size"] = 8
A3 = (420.0, 297.0)
TJUKK, MIDDELS, TYNN = 0.50, 0.30, 0.18          # strekvekt i mm
MM = 72 / 25.4                                   # punkt per mm


# ------------------------------------------------------------------ HLR
def hlr(former, N, X):
    algo = HLRBRep_Algo()
    for s in former:
        algo.Add(s.wrapped)
    algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*N), gp_Dir(*X))))
    algo.Update()
    algo.Hide()
    h = HLRBRep_HLRToShape(algo)
    ut = []
    for comp, vekt in ((h.VCompound(), MIDDELS), (h.OutLineVCompound(), TJUKK),
                       (h.Rg1LineVCompound(), TYNN)):
        if comp is None or comp.IsNull():
            continue
        BRepLib.BuildCurves3d_s(comp)
        ex = TopExp_Explorer(comp, TopAbs_EDGE)
        while ex.More():
            e = TopoDS.Edge_s(ex.Current())
            try:
                c = BRepAdaptor_Curve(e)
                d = GCPnts_QuasiUniformDeflection(c, 0.03)
                if d.IsDone() and d.NbPoints() > 1:
                    pts = [(d.Value(i).X(), d.Value(i).Y()) for i in range(1, d.NbPoints() + 1)]
                    ut.append((pts, vekt))
            except Exception:
                pass
            ex.Next()
    return ut


def teikn(ax, liner, x0, y0, skala, farge="k"):
    for pts, vekt in liner:
        ax.plot([x0 + p[0] * skala for p in pts], [y0 + p[1] * skala for p in pts],
                color=farge, lw=vekt * MM, solid_capstyle="round", solid_joinstyle="round")


def proj(p, N, X):
    """Projiser eit 3D-punkt inn i visingsplanet (u, v)."""
    import numpy as np
    n = np.array(N, float); n /= np.linalg.norm(n)
    x = np.array(X, float); x /= np.linalg.norm(x)
    y = np.cross(n, x)
    v = np.array(p, float)
    return float(v @ x), float(v @ y)


# ------------------------------------------------------------------ mål og tekst
def tekst(ax, x, y, s, storleik=8, **kw):
    ax.text(x, y, s, fontsize=storleik, **kw)


def k(v, d=1):
    """Tal med desimalkomma."""
    return f"{v:.{d}f}".replace(".", ",")


def maal_h(ax, xa, xb, y, yref_a, yref_b, s, opp=True):
    """Vassrett mål mellom xa og xb, linja i y, hjelpeliner frå yref."""
    for x, yr in ((xa, yref_a), (xb, yref_b)):
        ax.plot([x, x], [yr + (1 if y > yr else -1), y + (1.5 if y > yr else -1.5)],
                color="k", lw=TYNN * MM)
    ax.annotate("", (xa, y), (xb, y), arrowprops=dict(arrowstyle="<|-|>", lw=TYNN * MM, color="k",
                                                      shrinkA=0, shrinkB=0, mutation_scale=6))
    tekst(ax, (xa + xb) / 2, y + (1.0 if opp else -3.6), s, ha="center", va="bottom")


def maal_v(ax, ya, yb, x, xref_a, xref_b, s, venstre=True):
    for yy, xr in ((ya, xref_a), (yb, xref_b)):
        ax.plot([xr + (1 if x > xr else -1), x + (1.5 if x > xr else -1.5)], [yy, yy],
                color="k", lw=TYNN * MM)
    ax.annotate("", (x, ya), (x, yb), arrowprops=dict(arrowstyle="<|-|>", lw=TYNN * MM, color="k",
                                                      shrinkA=0, shrinkB=0, mutation_scale=6))
    tekst(ax, x + (-1.2 if venstre else 1.2), (ya + yb) / 2, s, ha="right" if venstre else "left",
          va="center", rotation=90)


def peikar(ax, xp, yp, xt, yt, s):
    ax.annotate(s, (xp, yp), (xt, yt), fontsize=8, va="center",
                arrowprops=dict(arrowstyle="-", lw=TYNN * MM, color="k", shrinkA=0, shrinkB=0))
    ax.plot([xp], [yp], marker="o", ms=1.6, color="k")


def ark(tittel, nr, skala_tekst, merknad=""):
    fig = plt.figure(figsize=(A3[0] / 25.4, A3[1] / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, A3[0]); ax.set_ylim(0, A3[1]); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(plt.Rectangle((10, 10), A3[0] - 20, A3[1] - 20, fill=False, lw=TJUKK * MM))
    # tittelfelt nedst til høgre
    x0, y0, b, h = A3[0] - 10 - 150, 10, 150, 24
    ax.add_patch(plt.Rectangle((x0, y0), b, h, fill=False, lw=MIDDELS * MM))
    ax.plot([x0, x0 + b], [y0 + 12, y0 + 12], color="k", lw=TYNN * MM)
    ax.plot([x0 + 100, x0 + 100], [y0, y0 + h], color="k", lw=TYNN * MM)
    tekst(ax, x0 + 3, y0 + 16, f"Sveip · {tittel}", 11)
    tekst(ax, x0 + 3, y0 + 4, "Konsept D for Northern · rev. A · 24.11.2026 · mål i mm", 7.5)
    tekst(ax, x0 + 103, y0 + 16, f"Ark {nr}", 9)
    tekst(ax, x0 + 103, y0 + 4, f"{skala_tekst} · ISO E", 7.5)
    if merknad:
        tekst(ax, 14, 14, merknad, 7, va="bottom")
    return fig, ax


# ------------------------------------------------------------------ ark
def former(ids=None, flytt=None):
    ut = []
    for d in SA.DELAR:
        if ids and d[0] not in ids:
            continue
        w = d[2]()
        v = w.vals()
        s = v[0] if len(v) == 1 else cq.Compound.makeCompound(v)
        if flytt and d[0] in flytt:
            s = s.translate(cq.Vector(*flytt[d[0]]))
        ut.append(s)
    return ut


FRAMME = ((0, -1, 0), (1, 0, 0))
TOPP = ((0, 0, 1), (1, 0, 0))
SIDE_V = ((-1, 0, 0), (0, -1, 0))
ISO = ((-1.0, -1.35, 0.85), (1.35, -1.0, 0.0))


def ark_ga(pdf):
    fig, ax = ark("Generalarrangement", 1, "Skala 1:2",
                  "Kropp EN AW-5754 H22 1,2 mm, valsa og pulverlakkert (matt, lys grå, fargeprøve krevst). "
                  "Masse 1111 g. Veltevinkel 15,5° mot utkraginga. Toleransar ISO 2768-m der ikkje anna står.")
    s = 0.5
    ytre = former({"D01", "D12F", "D12B", "D13F", "D13B", "K08"})
    # framvising
    fx, fy = 40.0, 120.0
    teikn(ax, hlr(ytre, *FRAMME), fx, fy, s)
    S, z0 = P0.S, 0.0
    X = lambda x: fx + x * s
    Z = lambda z: fy + z * s
    maal_h(ax, X(0), X(S), Z(S) + 10, Z(S), Z(S), "300")
    maal_v(ax, Z(0), Z(S), X(0) - 10, X(0), X(0), "300")
    maal_v(ax, Z(0), Z(P0.z_skjerm), X(S) + 10, X(P0.x_stamme), X(S), "167,5", venstre=False)
    maal_h(ax, X(0), X(P0.x_stamme), Z(0) - 12, Z(0), Z(0), "178", opp=False)
    maal_h(ax, X(0), X(P0.x_hakk), Z(P0.z_hakk) + 6, Z(P0.z_hakk), Z(P0.z_hakk), "45,5")
    maal_v(ax, Z(0), Z(P0.z_hakk), X(P0.x_hakk) + 6, X(P0.x_hakk), X(P0.x_hakk), "61", venstre=False)
    peikar(ax, X(P0.x_stamme + 3.5), Z(P0.z_skjerm - 3.5), X(P0.x_stamme + 30), Z(P0.z_skjerm - 30), "R12 (inner)")
    peikar(ax, X(P0.x_hakk - 2), Z(P0.z_hakk - 2), X(P0.x_hakk + 25), Z(P0.z_hakk - 40), "R7")
    peikar(ax, X(P0.pkt_x), Z(P0.pkt_z), X(P0.pkt_x + 70), Z(P0.pkt_z - 20),
           "Ø10 messing, flukt (berøring)")
    maal_h(ax, X(0), X(P0.pkt_x), Z(P0.pkt_z), Z(P0.pkt_z), Z(P0.pkt_z), "165")
    maal_v(ax, Z(0), Z(P0.pkt_z), X(P0.pkt_x) - 6, X(P0.pkt_x), X(P0.pkt_x), "140")
    tekst(ax, X(S / 2), Z(-44), "Framfrå", 9, ha="center")
    # vising ovanfrå (under framvisinga i ISO E)
    tx, ty = fx, 62.0
    alle = former({d[0] for d in SA.DELAR if d[6] != "ekstern"})
    teikn(ax, hlr(alle, *TOPP), tx, ty, s)
    Y = lambda y: ty + y * s
    maal_v(ax, Y(-P0.R), Y(P0.R), tx - 10, tx, tx, "105")
    peikar(ax, X(S - P0.R + P0.R * 0.7), Y(P0.R * 0.7), X(S + 18), Y(P0.R + 8), "R52,5 (ytre)")
    tekst(ax, X(S / 2), ty - 34, "Ovanfrå (med innmat)", 9, ha="center")
    # vising frå venstre: til høgre for framvisinga (ISO E)
    sx, sy = 225.0, fy
    teikn(ax, hlr(ytre, *SIDE_V), sx + P0.R * s, sy, s)
    maal_h(ax, sx, sx + P0.D * s, sy + P0.S * s + 10, sy + P0.S * s, sy + P0.S * s, "105")
    tekst(ax, sx + P0.R * s, sy - 24, "Frå venstre", 9, ha="center")
    tekst(ax, sx + P0.D * s + 4, sy - 2, "føter 3 mm", 7, va="top")
    # iso
    ix, iy = 330.0, 175.0
    teikn(ax, hlr(ytre + former({"E01"}), *ISO), ix, iy, 0.3)
    tekst(ax, ix + 10, iy - 52, "Isometri, 1:3,3", 9, ha="center")
    pdf.savefig(fig); fig.savefig(UT / "side-01.png", dpi=150); plt.close(fig)


def ark_snitt(pdf):
    fig, ax = ark("Snitt A–A (y = 0)", 2, "Skala 1:2",
                  "Innmaten er éin modul: chassis D02 med lysbrett D03 og alt elektrisk, senka ned gjennom "
                  "toppen og skrudd med 4 x M3 nedanfrå gjennom botnflensane.")
    alle = [d for d in SA.DELAR if d[6] != "ekstern"]
    snitt_boks = cq.Solid.makeBox(1000, 500, 1000, cq.Vector(-500, -500.0, -500))
    s_ = []
    for d in alle:
        w = d[2]()
        v = w.vals()
        f = v[0] if len(v) == 1 else cq.Compound.makeCompound(v)
        try:
            f = f.cut(snitt_boks)
        except Exception:
            continue
        if f.Volume() > 1e-3:
            s_.append((d[0], f))
    s = 0.5
    fx, fy = 50.0, 80.0
    teikn(ax, hlr([f for _, f in s_], *FRAMME), fx, fy, s)
    X = lambda x: fx + x * s
    Z = lambda z: fy + z * s
    merk = [("D01", 2, 250, "D01 kropp 1,2 mm"), ("D08", 150, 205, "D08 diffusor opp, PMMA opal 1,5"),
            ("D04", 100, 188.5, "D04 LED opp 2700 K, 16 stk"), ("D03", 60, 187, "D03 lysbrett 1,5 mm"),
            ("D05", 230, 185, "D05 LED ned 3000 K, 24 stk"), ("D06", 290, 175, "D06 ramme"),
            ("D07", 240, 170.5, "D07 diffusor ned, PMMA opal 2"), ("D02", 175, 100, "D02 chassis 1,5 mm (rygg)"),
            ("D09", 120, 23.8, "D09 hovudkort"), ("K01", 120, 13, "K01 celle 18650"),
            ("D10", 120, 0.6, "D10 luke, 2 myntskruar"), ("D11", 23, 66, "D11 USB-C, munning i taket"),
            ("D14", 170.7, 150, "D14 berøringskort med fjør")]
    for i, (pid, x, z, s_txt) in enumerate(merk):
        xt = X(320) if x > 140 else X(-60)
        yt = Z(300 - i * 23)
        peikar(ax, X(x), Z(z), xt, yt, s_txt)
    tekst(ax, X(150), Z(-25), "Snitt A–A sett framfrå", 9, ha="center")
    pdf.savefig(fig); fig.savefig(UT / "side-02.png", dpi=150); plt.close(fig)


def ark_sprengt(pdf):
    fig, ax = ark("Sprengd vising og stykkliste", 3, "Skala 1:3",
                  "Montering: modulen ned gjennom toppen (1), 4 skruar nedanfrå (2), berøringspunkta smett inn (3), "
                  "føter (4), celle og luke (5).")
    flytt = {}
    for d in SA.DELAR:
        i = d[0]
        if i in ("D01", "E01"):
            continue
        dz = 0.0
        if i in ("D03", "D04", "D04L", "D05", "D05L", "D06", "D07", "D08", "K05", "K11", "K12", "K18", "K21", "K10"):
            dz = 330.0
        elif i in ("D10", "K14"):
            dz = -90.0
        elif i in ("K09", "K08"):
            dz = -45.0
        else:
            dz = 210.0
        if i in ("D08", "K05"):
            dz += 60.0
        if i in ("D07", "D06", "K12"):
            dz -= 20.0
        dy = {"D12F": -60.0, "D13F": -45.0, "D12B": 60.0, "D13B": 45.0}.get(i, 0.0)
        if i in ("D12F", "D13F", "D12B", "D13B"):
            dz = 0.0
        flytt[i] = (0.0, dy, dz)
    ids = [d[0] for d in SA.DELAR if d[6] != "ekstern"]
    alle = former(set(ids), flytt)
    s = 0.25
    liner = hlr(alle, *ISO)
    us = [p[0] for pts, _ in liner for p in pts]
    vs = [p[1] for pts, _ in liner for p in pts]
    ix = 135.0 - s * (min(us) + max(us)) / 2
    iy = 152.0 - s * (min(vs) + max(vs)) / 2
    teikn(ax, liner, ix, iy, s)
    # delnummer med peikeline
    merk = {"D01": (40, 60), "D02": (-75, 30), "D03": (-70, 0), "D04": (-60, 15), "D05": (75, -10),
            "D06": (75, 5), "D07": (70, -25), "D08": (-60, 20), "D09": (-70, -20), "D10": (-60, -10),
            "D11": (-55, -5), "D12F": (-55, 0), "D13F": (-50, -12), "D14": (55, 15), "K01": (-65, -35),
            "K08": (45, -6), "K09": (60, -38), "K14": (-45, -28)}
    for pid, (dx, dy) in merk.items():
        f = [f_ for d, f_ in zip([d for d in SA.DELAR if d[0] in set(ids)], alle) if d[0] == pid]
        if not f:
            continue
        c = cq.Shape.centerOfMass(f[0]) if f[0].Volume() > 0 else f[0].Center()
        u, v = proj((c.x, c.y, c.z), *ISO)
        xp, yp = ix + u * s, iy + v * s
        peikar(ax, xp, yp, xp + dx, yp + dy, pid)
    # stykkliste til høgre
    rad = [d for d in SA.DELAR if d[6] != "ekstern"]
    x0, y0 = 262.0, 280.0
    tekst(ax, x0, y0, "Nr.   Del                                          Tal   Materiale / delenummer", 7)
    for k, d in enumerate(rad):
        y = y0 - 5.6 * (k + 1)
        tekst(ax, x0, y, d[0], 6.5)
        tekst(ax, x0 + 10, y, d[1][:30], 6.5)
        tekst(ax, x0 + 58, y, str(d[7]), 6.5)
        tekst(ax, x0 + 66, y, d[3][:44], 6.5)
    pdf.savefig(fig); fig.savefig(UT / "side-03.png", dpi=150); plt.close(fig)


def ark_flat(pdf):
    import ezdxf
    from ezdxf import path as epath
    fig, ax = ark("Flatmønster D01 kropp", 4, "Skala 1:2",
                  "Laserskjering 1,2 mm EN AW-5754 H22. K = 0,5 i bogane (R/t > 40). Saum i s = 0 / s = L: "
                  "laser-buttsveis, slipast plan før lakk. Bøy flensane (90°, ri 2) før bogane.")
    doc = ezdxf.readfile(ROT / "produksjon/dxf/sveip_D01_kropp_flat.dxf")
    s = 0.5
    ox, oy = 30.0, 80.0
    for e in doc.modelspace():
        lag = e.dxf.layer
        if lag == "TEKST":
            continue
        farge = {"SKJER": "k", "BOY": "#c00", "VALS": "#06c"}.get(lag, "k")
        lw = (MIDDELS if lag == "SKJER" else TYNN) * MM
        stil = "-" if lag == "SKJER" else (0, (6, 3))
        if e.dxftype() in ("LWPOLYLINE", "LINE", "CIRCLE"):
            pts = [(v.x, v.y) for v in epath.make_path(e).flattening(0.05)]
            ax.plot([ox + p[0] * s for p in pts], [oy + p[1] * s for p in pts], color=farge, lw=lw, ls=stil)
    f = kropp_flat()
    L, S = f["L"], P0.S
    X = lambda u: ox + u * s
    Z = lambda z: oy + z * s
    maal_h(ax, X(0), X(L), Z(S) + 10, Z(S), Z(S), k(L) + " (utbretta lengd)")
    maal_v(ax, Z(f["z_fl2"]), Z(S), X(0) - 8, X(f["sa"]), X(0), k(S - f['z_fl2']))
    for (a, b), namn in zip(f["s_boge"], ("valsesone høgre boge", "valsesone venstre boge")):
        maal_h(ax, X(a), X(b), Z(S) + 3.5, Z(S), Z(S), k(b - a) + "  " + namn)
    maal_h(ax, X(f["ha"]), X(f["hb"]), Z(P0.z_hakk) + 4, Z(P0.z_hakk), Z(P0.z_hakk), k(f['hb'] - f['ha']) + " hakk")
    maal_h(ax, X(f["sa"]), X(f["sb"]), Z(f["z_fl2"]) - 9, Z(f["z_fl2"]), Z(f["z_fl2"]), k(f['sb'] - f['sa']) + " stamme", opp=False)
    tekst(ax, X(5), Z(S) - 8, "baksida, saum", 7)
    tekst(ax, X(L / 2), Z(S / 2 + 40), "innsida opp", 8, ha="center", color="#555")
    tekst(ax, ox, oy - 30, "Raud stipla: bøyeline flens (90° innover).  Blå stipla: start og slutt for 180°-bogane (Ri 51,3).", 7)
    pdf.savefig(fig); fig.savefig(UT / "side-04.png", dpi=150); plt.close(fig)


def main():
    with PdfPages(UT / "sveip_teikningar.pdf") as pdf:
        for f in (ark_ga, ark_snitt, ark_sprengt, ark_flat):
            f(pdf)
            print("ferdig", f.__name__)


if __name__ == "__main__":
    main()
