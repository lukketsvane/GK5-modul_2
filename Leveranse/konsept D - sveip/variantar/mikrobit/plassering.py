# -*- coding: utf-8 -*-
"""plassering.py: teiknar plassering.png for Sveip mini.
Øvst: heile lampa framanfrå, med kortet stipla bak veggen. Nedst: snitt B-B gjennom matrisa og
messingpunktet, sett ovanfrå. Måla på lampa og kortet kjem frå mini_passform.py.
  python plassering.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle
from shapely.geometry import LineString, box

from d15_lysrist import BLOKK_V, FOT_V, T_FOT
from mini_passform import AVST, D, K, MB, R, S, T, X_ST, YK, Z_SK, avstand, delar, vegg

HER = Path(__file__).resolve().parent
R_INN = 12.0 * K
MX, MZ = MB
LOGO, R_MESSING = 14.0, 3.0
FELT = (MX - 11.5, MZ - 11.5, MX + LOGO + 6.5, MZ + 11.5)        # forsenka felt 32 x 23, radius 3,5
KORT = (MX - 20.0, MZ - 25.8, MX + 22.0, MZ + 25.8)              # kretskortet rotert 90° med klokka
RINGAR_Z = [MZ - u for u in (-21.59, -11.43, 0.0, 11.43, 21.59)]  # ring 0 øvst, GND nedst
BILETE = ["66666", "66666", "33300", "33300", "33300"]

LYS, GRAA, DIM, RAUD, MESSING, ALU = "#e6e3dc", "#8d8b86", "#55534f", "#ff3b24", "#c9a24a", "#b9b7b1"
LED = {6: RAUD, 3: "#9c2416", 0: "#2a1210"}
STIPLA = (0, (3, 2))

fig = plt.figure(figsize=(7.97, 7.97), dpi=200, facecolor="black")


def akse(rect, xlim, ylim):
    ax = fig.add_axes(rect, facecolor="black")
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal"); ax.axis("off")
    return ax


def maal(ax, p0, p1, tekst, forskyv=(0, 0), ha="center", va="bottom"):
    ax.annotate("", p0, p1, arrowprops=dict(arrowstyle="<->", color=GRAA, lw=0.6, shrinkA=0, shrinkB=0))
    ax.text((p0[0] + p1[0]) / 2 + forskyv[0], (p0[1] + p1[1]) / 2 + forskyv[1], tekst, color=LYS,
            fontsize=6.5, ha=ha, va=va)


def peik(ax, punkt, tekstpunkt, tekst, ha="left"):
    ax.annotate(tekst, punkt, tekstpunkt, color=LYS, fontsize=6.5, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=GRAA, lw=0.5, shrinkA=2, shrinkB=1))


def rund(ax, x0, z0, x1, z1, r, **kw):
    ax.add_patch(FancyBboxPatch((x0 + r, z0 + r), x1 - x0 - 2 * r, z1 - z0 - 2 * r, boxstyle=f"round,pad={r}", **kw))


def tal(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


# ------------------------------------------------------------------ heile lampa framanfrå
a = akse([0.035, 0.435, 0.60, 0.50], (-17, S + 15), (-10, S + 7))
v = np.radians(np.linspace(180, 90, 16))
hjorne = np.c_[X_ST + R_INN + R_INN * np.cos(v), Z_SK - R_INN + R_INN * np.sin(v)]
omriss = np.vstack([[0, 0], [X_ST, 0], hjorne, [S, Z_SK], [S, S], [0, S]])
a.add_patch(Polygon(omriss, closed=True, fc="#141414", ec=LYS, lw=1.0))
a.plot([0, X_ST], [Z_SK, Z_SK], color=DIM, lw=0.6)                                   # ringsaumen
rund(a, *KORT, 3.0, fill=False, ec=GRAA, lw=0.8, ls=STIPLA)                          # kretskortet
for z in RINGAR_Z:
    a.add_patch(Circle((MX - 13.14, z), 2.0, fill=False, ec=GRAA, lw=0.6, ls=STIPLA))
for dz in (19.94, -19.94):                                                           # knapp A over, B under
    a.add_patch(Rectangle((MX + 0.96 - 3.25, MZ + dz - 3.0), 6.5, 6.0, fill=False, ec=GRAA, lw=0.6, ls=STIPLA))
a.add_patch(Rectangle((MX + 12.96, MZ + 14.87), 8.6, 7.9, fill=False, ec=GRAA, lw=0.6, ls=STIPLA))   # JST
a.add_patch(Rectangle((MX + 17.14, MZ - 4.0), 6.26, 8.0, fill=False, ec=GRAA, lw=0.6, ls=STIPLA))    # USB
rund(a, *FELT, 3.5, fc="black", ec=LYS, lw=0.8)
for rad in range(5):
    for kol in range(5):
        a.add_patch(Circle((MX + (kol - 2) * 4.0, MZ + (2 - rad) * 4.0), 1.0, fc=LED[int(BILETE[rad][kol])], ec="none"))
a.add_patch(Circle((MX + LOGO, MZ), R_MESSING + 2.2, fill=False, ec=GRAA, lw=0.5))
a.add_patch(Circle((MX + LOGO, MZ), R_MESSING, fc=MESSING, ec="none"))
for xa, xb in ((-8, FELT[0] - 1), (FELT[2] + 1, X_ST + 13)):
    a.plot([xa, xb], [MZ, MZ], color=GRAA, lw=0.5, ls=(0, (8, 2, 1.5, 2)))           # snittet B-B
a.text(-8, MZ + 1.0, "B", color=LYS, fontsize=8, ha="left", va="bottom")
a.text(X_ST + 13, MZ + 1.0, "B", color=LYS, fontsize=8, ha="right", va="bottom")
a.annotate("", (X_ST + 9, MZ - 6), (KORT[2] + 1.2, MZ - 6), arrowprops=dict(arrowstyle="->", color=GRAA, lw=0.6))
a.text(X_ST + 10, MZ - 6, "USB", color=LYS, fontsize=6.5, ha="left", va="center")
maal(a, (0, -6.5), (S, -6.5), tal(S, 0), va="top", forskyv=(0, -0.8))
maal(a, (0, -2.5), (X_ST, -2.5), tal(X_ST), va="top", forskyv=(0, -0.6))
maal(a, (S + 6, 0), (S + 6, S), tal(S, 0), forskyv=(1.5, 0), ha="left", va="center")
maal(a, (-5, 0), (-5, Z_SK), tal(Z_SK), forskyv=(-1.5, -14), ha="right", va="center")
maal(a, (X_ST + 4, KORT[1]), (X_ST + 4, KORT[3]), "51,6", forskyv=(1.2, 12), ha="left", va="center")
for z in (KORT[1], KORT[3]):
    a.plot([KORT[2] + 1, X_ST + 5], [z, z], color=GRAA, lw=0.4)
for x in (0, S):
    a.plot([x, x], [-7.5, -1], color=GRAA, lw=0.4)
a.plot([X_ST, X_ST], [-3.5, -1], color=GRAA, lw=0.4)
a.plot([-6, -1], [Z_SK, Z_SK], color=GRAA, lw=0.4); a.plot([-6, -1], [0, 0], color=GRAA, lw=0.4)
a.plot([S + 1, S + 7], [0, 0], color=GRAA, lw=0.4); a.plot([S + 1, S + 7], [S, S], color=GRAA, lw=0.4)
peik(a, (FELT[0] + 6, FELT[3]), (4, Z_SK + 24), "forsenka felt 32 × 23\nmed 25 hol Ø 2,0 og messingpunkt Ø 6")
peik(a, (KORT[0] + 3, KORT[3] - 1.5), (4, Z_SK + 12), "micro:bit V2 bak veggen (stipla)")
a.plot([0, 10], [-9.5, -9.5], color=LYS, lw=1.2)
a.text(11.5, -9.5, "10 mm", color=GRAA, fontsize=6.0, ha="left", va="center")
a.text(-17, S + 6.5, "HEILE LAMPA FRAMANFRÅ", color=GRAA, fontsize=6.5, ha="left", va="top")

# ------------------------------------------------------------------ tala
kb = delar["kretskort"].val().BoundingBox()
til_nasen = tal(avstand(delar["kretskort"], vegg))
y = 0.885
for i, (tekst, farge, storleik) in enumerate([
        (f"{tal(S, 0)} × {tal(S, 0)} × {tal(D)} mm", LYS, 13),
        (f"rev. B i skala {tal(K, 2)}, plate {tal(T)} mm", GRAA, 7.5),
        ("", GRAA, 5),
        ("micro:bit V2, rotert 90°", LYS, 8.5),
        (f"42,0 brei i ei stamme på {tal(X_ST)}", GRAA, 7.5),
        ("USB mot den opne enden av stamma", GRAA, 7.5),
        ("touch-logoen bak messingpunktet", GRAA, 7.5),
        ("", GRAA, 5),
        ("Kontrollert i CAD (mm)", LYS, 8.5),
        (f"kortet til krumminga i nasen   {til_nasen}", GRAA, 7.5),
        (f"knapp A og B til veggen   {tal(avstand(delar['knapp A'], vegg), 2)}", GRAA, 7.5),
        (f"lysrista til veggen   {tal(avstand(delar['lysrist D15'], vegg))}", GRAA, 7.5),
        (f"kortet til enden av stamma   {tal(X_ST - kb.xmax)}", GRAA, 7.5),
        (f"kortet over underkanten   {tal(kb.zmin)}", GRAA, 7.5),
        (f"kortet opp bak skjermsaumen   {tal(kb.zmax - Z_SK)}", GRAA, 7.5),
        (f"fri djupn bak kortet   {tal(D / 2 - T - (YK + 1.6 + 5.5), 0)}", GRAA, 7.5)]):
    fig.text(0.665, y, tekst, color=farge, fontsize=storleik, ha="left", va="top")
    y -= 0.012 + storleik * 0.0026

# ------------------------------------------------------------------ snitt B-B, sett ovanfrå
s = akse([0.035, 0.03, 0.93, 0.375], (-8, S + 8), (-R - 7.7, R + 3.7))
ytre = LineString([(R, 0), (S - R, 0)]).buffer(R, resolution=64)
indre = LineString([(R, 0), (S - R, 0)]).buffer(R - T, resolution=64)
vegg = ytre.difference(indre).intersection(box(-1, -R - 1, X_ST, R + 1))
s.add_patch(Polygon(np.array(ytre.exterior.coords), closed=True, fill=False, ec=DIM, lw=0.6, ls=STIPLA))
for g in getattr(vegg, "geoms", [vegg]):
    s.add_patch(Polygon(np.array(g.exterior.coords), closed=True, fc=ALU, ec="none"))
YV, YI = -R, -R + T
s.add_patch(Rectangle((X_ST - 1.0, YI), 1.0, 2 * (R - T), fc="#3a3a3a", ec="none"))               # endeplata
s.add_patch(Rectangle((X_ST - 1.1, YK + 1.6 - 0.4), 1.2, 3.2, fc="black", ec="none"))             # opning for USB
for kol in range(5):
    x = MX + (kol - 2) * 4.0
    n = int(BILETE[2][kol])
    s.add_patch(Rectangle((x - 1.0, YV), 2.0, T, fc="#ff9a8c" if n else "#6b6966", ec="none"))     # proppane
    s.add_patch(Rectangle((x - 1.2, YK - 4.8), 2.4, 4.8, fc="#5a1410" if n else "black", ec="none", zorder=3))
    s.add_patch(Rectangle((x - 0.8, YK - 0.4), 1.6, 0.4, fc=RAUD if n else "#7a2a22", ec="none", zorder=4))
s.add_patch(Rectangle((MX + BLOKK_V[0], YK - 4.8), BLOKK_V[1] - BLOKK_V[0], 4.8, fc="#1c1c1c", ec=GRAA, lw=0.5,
                      zorder=2))                                                                   # lysrista
s.add_patch(Rectangle((MX + FOT_V[0], YK - T_FOT), FOT_V[1] - FOT_V[0], T_FOT, fc="#1c1c1c", ec=GRAA, lw=0.5,
                      zorder=2))                                                                   # foten
s.add_patch(Rectangle((KORT[0], YK), 42.0, 1.6, fc="#3d4a3f", ec="none", zorder=2))               # kretskortet
s.add_patch(Rectangle((MX - 2.25, YK + 1.6), 8.0, 3.0, fc="#4c4a47", ec="none"))                  # høgtalaren
s.add_patch(Rectangle((MX + 17.14, YK + 1.6), 6.26, 2.4, fc="#a9a7a2", ec="none"))                # USB
xm = MX + LOGO                                                                                    # messingpunktet
s.add_patch(Rectangle((xm - 3.5, YV), 7.0, T + 3.6, fc="#d8d5cd", ec="none", zorder=3))           # hylsa
s.add_patch(Rectangle((xm - 2.0, YV), 4.0, T + 2.6, fc=MESSING, ec="none", zorder=4))             # skaftet
s.add_patch(Rectangle((xm - 3.0, YV - 0.5), 6.0, 0.5, fc=MESSING, ec="none", zorder=4))           # kragen
s.add_patch(Rectangle((xm - 0.5, YV + T + 2.6), 1.0, YK - (YV + T + 2.6), fc=MESSING, ec="none", zorder=4))  # fjørpinnen
s.add_patch(Rectangle((14.0, YK + 6.0), 25.0, 14.0, fill=False, ec=GRAA, lw=0.6, ls=STIPLA))      # 2 x AAA
s.text(26.5, YK + 13.0, "2 × AAA\n(framlegg)", color=GRAA, fontsize=6.0, ha="center", va="center")
maal(s, (X_ST - 4.0, YI), (X_ST - 4.0, YK), tal(AVST), forskyv=(-0.8, 0), ha="right", va="center")
maal(s, (S + 4, -R), (S + 4, R), tal(D), forskyv=(-1.0, 0), ha="right", va="center")
YM, YT = -R - 3.0, -R - 6.4                 # høgda på mållinene og på tekstrada under snittet
maal(s, (0, YM), (KORT[0], YM), tal(KORT[0]), forskyv=(0, 0.3))
maal(s, (KORT[2], YM), (X_ST, YM), tal(X_ST - KORT[2]), forskyv=(0, 0.3))
for x in (0, KORT[0], KORT[2], X_ST):
    s.plot([x, x], [YM - 0.7, -R - 0.6 if x in (0, X_ST) else YK - 0.3], color=GRAA, lw=0.4)
peik(s, (MX - 15, YK - T_FOT + 0.1), (-7, YT), f"lysrist D15, {tal(T_FOT)} ved ringane")
peik(s, (MX + 2, YV + 0.5), (MX + 1, YT), "klar, matta propp", ha="right")
peik(s, (xm, YV - 0.5), (xm + 4, YT), "messingpunkt Ø 6 i isolerande hylse, fjørpinne mot logoen")
peik(s, (KORT[0] + 0.6, YK + 0.9), (-8, R + 1.0), f"kretskort, {til_nasen} frå krumminga i nasen")
peik(s, (MX + 20.5, YK + 2.8), (X_ST + 5, R - 14.5), "micro-USB ut gjennom endeplata")
peik(s, (MX + 3, YK + 3.2), (X_ST + 5, R - 9.0), "høgtalar 3,0 (JST 5,5 over snittet)")
s.text(X_ST + 5, R - 3.5, "skjermen over snittet (stipla)", color=GRAA, fontsize=6.5, ha="left", va="center")
s.text(-8, R + 3.5, "SNITT B–B, SETT OVANFRÅ (FORSTØRRA)", color=GRAA, fontsize=6.5, ha="left", va="top")
s.text(S + 7.5, YT, "framsida", color=GRAA, fontsize=6.0, ha="right", va="center")

fig.text(0.035, 0.968, "Sveip mini · den minste lampa som rommar ein micro:bit V2", color=LYS, fontsize=11,
         ha="left", va="center")
fig.text(0.965, 0.968, "mål i mm", color=GRAA, fontsize=6.5, ha="right", va="center")
fig.savefig(HER / "plassering.png", facecolor="black")
print("SKREIV", HER / "plassering.png")
