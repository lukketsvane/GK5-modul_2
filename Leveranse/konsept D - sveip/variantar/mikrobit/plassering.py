# -*- coding: utf-8 -*-
"""plassering.py: teiknar plassering.png, som viser korleis micro:bit V2 sit bak framveggen på stamma.
Øvst: stamma sett framanfrå. Nedst: snitt A-A gjennom matrisa og messingknappen, sett ovanfrå.
Måla på kortet er frå den offisielle monteringsteikninga for V2 (Avnet, DWG 1.48, rev. 1).
  python plassering.py
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

HER = Path(__file__).resolve().parent
sys.path.insert(0, str(HER.parent / "overflate"))
from sveip_hud import MB_FELT, MB_HOL_R, MB_PX, MB_X, MB_Z, PKT_X, PKT_Z, R_, R_INN, R_KNAPP, X_STAMME, Z_SKJERM

# micro:bit V2, mål i mm relativt til midtre LED (x mot høgre og z opp, sett framanfrå)
KORT = (-25.80, -20.00, 51.60, 42.00)          # venstre, nedre, breidd, høgd; hjørneradius 3
RINGAR = [(-21.59, "0"), (-11.43, "1"), (0.0, "2"), (11.43, "3V"), (21.59, "GND")]
RING_Z, RING_D = -13.14, 4.0
KNAPP_AB = [(-19.94, 0.96), (19.94, 0.96)]     # senter; 6,0 x 6,5, 4,55 høg
T_PCB, H_KNAPP, H_LED, H_BAK = 1.6, 4.55, 0.4, 5.5
VEGG = 1.2                                     # aluminium
LUFT = 0.55                                    # mellom knapp A/B og veggen
T_RIST = 4.8                                   # lysrista D15, frå kortet og fram mot veggen
DRAGAR = [163.93, 149.46, 134.19, 117.77, 99.82, 80.03, 58.20]

LYS, GRAA, DIM, RAUD, MESSING = "#e6e3dc", "#8d8b86", "#55534f", "#ff3b24", "#c9a24a"
ALU = "#b9b7b1"

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


# ------------------------------------------------------------------ framanfrå
a = akse([0.04, 0.37, 0.92, 0.56], (30, 214), (-6, 106))
a.plot([30, X_STAMME, X_STAMME], [0, 0, 106], color=LYS, lw=1.0)                  # underkanten og kanten mot utskjeringa
for x in DRAGAR:                                                                 # dragarane i huda
    if abs(x - MB_X) < 1:
        a.plot([x, x], [0, MB_Z - 16.5], color=DIM, lw=0.6); a.plot([x, x], [MB_Z + 16.5, 106], color=DIM, lw=0.6)
    elif abs(x - PKT_X) < 2:
        a.plot([x, x], [0, PKT_Z - 13], color=DIM, lw=0.6); a.plot([x, x], [PKT_Z + 13, 106], color=DIM, lw=0.6)
    else:
        a.plot([x, x], [0, 106], color=DIM, lw=0.6)
x0, z0, b, h = KORT
a.add_patch(FancyBboxPatch((MB_X + x0 + 3, MB_Z + z0 + 3), b - 6, h - 6, boxstyle="round,pad=3", fill=False,
                           ec=GRAA, lw=0.8, ls=(0, (4, 2.5))))
for dx, namn in RINGAR:
    a.add_patch(Circle((MB_X + dx, MB_Z + RING_Z), RING_D / 2, fill=False, ec=GRAA, lw=0.7, ls=(0, (2, 1.5))))
    a.text(MB_X + dx, MB_Z + z0 - 1.6, namn, color=GRAA, fontsize=5.5, ha="center", va="top")
for dx, dz in KNAPP_AB:
    a.add_patch(Rectangle((MB_X + dx - 3.0, MB_Z + dz - 3.25), 6.0, 6.5, fill=False, ec=GRAA, lw=0.7, ls=(0, (2, 1.5))))
f = MB_FELT + 2 * MB_PX                                                           # halv feltbreidd
a.add_patch(FancyBboxPatch((MB_X - f + MB_FELT, MB_Z - f + MB_FELT), 2 * (f - MB_FELT), 2 * (f - MB_FELT),
                           boxstyle=f"round,pad={MB_FELT}", fc="black", ec=LYS, lw=0.8))
bilete = ["66666", "66666", "33300", "33300", "33300"]
for rad in range(5):
    for kol in range(5):
        n = int(bilete[rad][kol])
        a.add_patch(Circle((MB_X + (kol - 2) * MB_PX, MB_Z + (2 - rad) * MB_PX), MB_HOL_R,
                           fc={6: RAUD, 3: "#9c2416", 0: "#2a1210"}[n], ec="none"))
a.add_patch(Circle((PKT_X, PKT_Z), R_KNAPP + 2.2, fc="black", ec=LYS, lw=0.6))
a.add_patch(Circle((PKT_X, PKT_Z), R_KNAPP, fc=MESSING, ec="none"))
for xa, xb in ((34, MB_X + x0 - 1), (MB_X + x0 + b + 1, PKT_X - R_KNAPP - 3), (PKT_X + R_KNAPP + 3, 200)):
    a.plot([xa, xb], [MB_Z, MB_Z], color=GRAA, lw=0.5, ls=(0, (8, 2, 1.5, 2)))    # betjeningslina, snitt A-A
a.text(34, MB_Z + 1.2, "A", color=LYS, fontsize=8, ha="left", va="bottom")
a.text(200, MB_Z + 1.2, "A", color=LYS, fontsize=8, ha="right", va="bottom")
maal(a, (MB_X, 99), (PKT_X, 99), f"{PKT_X - MB_X:.1f}".replace(".", ","))
a.plot([MB_X, MB_X], [MB_Z + 23.5, 101], color=GRAA, lw=0.4); a.plot([PKT_X, PKT_X], [PKT_Z + 10, 101], color=GRAA, lw=0.4)
maal(a, (PKT_X, 12), (X_STAMME, 12), f"{X_STAMME - PKT_X:.0f}")
a.plot([PKT_X, PKT_X], [PKT_Z - 10, 10], color=GRAA, lw=0.4)
maal(a, (206, 0), (206, MB_Z), f"{MB_Z:.0f}", forskyv=(1.5, 0), ha="left", va="center")
a.plot([X_STAMME, 208], [0, 0], color=GRAA, lw=0.4); a.plot([200, 208], [MB_Z, MB_Z], color=GRAA, lw=0.4)
maal(a, (MB_X - 8, MB_Z + 14.5), (MB_X + 8, MB_Z + 14.5), "4 × 4,0", forskyv=(0, 0.6))
peik(a, (MB_X - 11.5, MB_Z + 8), (32, 96), "forsenka felt 23 × 23, 0,12 djupt")
peik(a, (MB_X - 9, MB_Z + 4), (32, 84), "25 hol Ø 2,0 med klar, matta propp")
peik(a, (MB_X + x0, MB_Z - 6), (32, 56), "micro:bit V2 bak veggen,\n51,6 × 42 (stipla)")
peik(a, (MB_X - 21.59 - 1.5, MB_Z + RING_Z - 1.5), (32, 38), "ringane: M3 i nylon,\nleidning med ringsko")
peik(a, (PKT_X + 4.5, PKT_Z - 4.5), (184, 40), "messingknapp\nØ 12,6")
a.text(30, 105, "STAMMA FRAMANFRÅ", color=GRAA, fontsize=6.5, ha="left", va="top")

# ------------------------------------------------------------------ snitt A-A, sett ovanfrå
YV = -R_                                    # utsida av veggen
YI = YV + VEGG                              # innsida
YK = YI + LUFT + H_KNAPP                    # framsida av kretskortet
s = akse([0.04, 0.045, 0.92, 0.30], (88, 178), (YV - 4.5, YV + 22))
HOL_K = 12.3                                # holet til knappen (hylsa er Ø 12,1)
s.add_patch(Rectangle((88, YV), PKT_X - HOL_K / 2 - 88, VEGG, fc=ALU, ec="none"))             # veggen
s.add_patch(Rectangle((PKT_X + HOL_K / 2, YV), X_STAMME - PKT_X - HOL_K / 2, VEGG, fc=ALU, ec="none"))
for kol in range(5):
    x = MB_X + (kol - 2) * MB_PX
    lyser = bilete[2][kol] != "0"
    s.add_patch(Rectangle((x - MB_HOL_R, YV), 2 * MB_HOL_R, VEGG, fc="#ff9a8c" if lyser else "#6b6966", ec="none"))
s.add_patch(Rectangle((MB_X + x0, YK), b, T_PCB, fc="#3d4a3f", ec="none"))                    # kretskortet
s.add_patch(Rectangle((MB_X - 11.5, YK - T_RIST), 23, T_RIST, fc="#1c1c1c", ec=GRAA, lw=0.5))  # lysrista
for kol in range(5):
    x = MB_X + (kol - 2) * MB_PX
    lyser = bilete[2][kol] != "0"
    s.add_patch(Rectangle((x - 1.2, YK - T_RIST), 2.4, T_RIST, fc="#5a1410" if lyser else "black", ec="none"))
    s.add_patch(Rectangle((x - 0.4, YK - H_LED), 0.8, H_LED, fc=RAUD if lyser else "#7a2a22", ec="none"))
for dx, _ in KNAPP_AB:
    s.add_patch(Rectangle((MB_X + dx - 3.0, YK - 3.4), 6.0, 3.4, fc="#6f6d68", ec="none"))
    s.add_patch(Rectangle((MB_X + dx - 1.6, YK - H_KNAPP), 3.2, H_KNAPP - 3.4, fc="#2b2b2b", ec="none"))
s.add_patch(Rectangle((MB_X - 4.0, YK + T_PCB), 8.0, 3.0, fc="#4c4a47", ec="none"))           # høgtalaren
s.add_patch(Rectangle((MB_X + x0, YK + T_PCB), b, H_BAK, fill=False, ec=GRAA, lw=0.5, ls=(0, (2, 1.5))))
# messingknappen i POM-hylsa (rev. B), skjematisk
s.add_patch(Rectangle((PKT_X - 6.05, YV), 12.1, 6.0, fc="#d8d5cd", ec="none"))                # hylsa
s.add_patch(Rectangle((PKT_X - 4.6, YV), 9.2, 7.0, fc=MESSING, ec="none"))                    # skaftet
s.add_patch(Rectangle((PKT_X - 6.4, YV - 0.4), 12.8, 0.4, fc=MESSING, ec="none"))             # kragen
s.add_patch(Rectangle((PKT_X - R_KNAPP + 1.2, YV - 1.0), 2 * R_KNAPP - 2.4, 0.6, fc=MESSING, ec="none"))
s.plot([PKT_X, PKT_X, MB_X + 9, MB_X + 9], [YV + 7.0, YV + 11.5, YV + 11.5, YK + T_PCB], color=MESSING, lw=0.8)
s.plot([150, 150], [YV - 2.4, YV], color=GRAA, lw=0.5); s.plot([150, 150], [YI, YI + 2.0], color=GRAA, lw=0.5)
s.text(151, YV - 2.0, "plate 1,2", color=LYS, fontsize=6.5, ha="left", va="center")
maal(s, (MB_X + 27.5, YI), (MB_X + 27.5, YK), f"{YK - YI:.1f}".replace(".", ","), forskyv=(1.2, 0), ha="left", va="center")
maal(s, (MB_X + 27.5, YK + T_PCB), (MB_X + 27.5, YK + T_PCB + H_BAK), "5,5", forskyv=(1.2, 0), ha="left", va="center")
peik(s, (MB_X + 4, YV + 0.6), (MB_X + 9, YV - 3.2), "klar, matta propp i flukt med plata")
peik(s, (MB_X - 10.5, YK - 2.6), (89, YV + 9.5), "lysrist D15\n(svart, 25 kanalar)")
peik(s, (MB_X - 19.94, YK - 4.0), (89, YV + 4.2), "knapp A,\n0,55 frå veggen")
peik(s, (MB_X - 15, YK + 0.8), (89, YV + 15.5), "kretskort 1,6")
peik(s, (MB_X + 1.5, YK + T_PCB + 1.5), (MB_X - 4, YV + 18.6), "høgtalar 3,0 (JST 5,5 i hjørnet)")
peik(s, (PKT_X - 12, YV + 11.5), (152, YV + 16.5), "berøring: messing, fjør\nog leidning til ring 2")
s.text(88, YV + 21.6, "SNITT A–A, SETT OVANFRÅ (FORSTØRRA)", color=GRAA, fontsize=6.5, ha="left", va="top")
s.text(177.5, YV - 3.6, "framsida", color=GRAA, fontsize=6.0, ha="right", va="center")

fig.text(0.04, 0.965, "Sveip · micro:bit V2 bak framveggen", color=LYS, fontsize=11, ha="left", va="center")
fig.text(0.96, 0.965, "mål i mm", color=GRAA, fontsize=6.5, ha="right", va="center")
fig.savefig(HER / "plassering.png", facecolor="black")
print("SKREIV", HER / "plassering.png")
