# -*- coding: utf-8 -*-
"""mini_plate.py: teiknar print/Sveip_mini_alle_delar.png, plata i Sveip_mini_alle_delar.3mf sett ovanfrå.
  python mini_plate.py      (køyr mini_print.py først)
"""
import re
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle

HER = Path(__file__).resolve().parent
FIL = HER / "print" / "Sveip_mini_alle_delar.3mf"
LYS, GRAA = "#e6e3dc", "#8d8b86"
VIS = {"lampefarge": "#c9c7c1", "svart": "#3a3a3a"}


def les(fil):
    m = zipfile.ZipFile(fil).read("3D/3dmodel.model").decode()
    fargar = re.findall(r'<base name="([^"]+)"', m)
    for o in re.finditer(r'<object id="\d+" name="([^"]+)"[^>]*pindex="(\d+)"[^>]*>(.*?)</object>', m, re.S):
        v = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', o.group(3)), dtype=float)
        t = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', o.group(3)), dtype=int)
        yield o.group(1), fargar[int(o.group(2))], v, t


fig, ax = plt.subplots(figsize=(7.2, 7.2), dpi=200, facecolor="black")
ax.set_facecolor("black")
ax.add_patch(Rectangle((0, 0), 256, 256, fill=False, ec=GRAA, lw=0.8))
ax.add_patch(Rectangle((0, 0), 18, 28, fc="#2a1a1a", ec="#7a3a30", lw=0.6))
ax.text(9, 31, "sperresone", color="#a05a50", fontsize=5.5, ha="center", va="bottom")
for namn, farge, v, t in les(FIL):
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    opp = np.cross(b - a, c - a)[:, 2] > 0          # flater som vender opp
    poly = np.stack([a[opp, :2], b[opp, :2], c[opp, :2]], axis=1)
    lys = 0.55 + 0.45 * (np.stack([a[opp, 2], b[opp, 2], c[opp, 2]], 1).mean(1) / max(v[:, 2].max(), 1))
    base = np.array(matplotlib.colors.to_rgb(VIS[farge]))
    ax.add_collection(PolyCollection(poly, facecolors=np.clip(base[None, :] * lys[:, None], 0, 1), edgecolors="none"))
    x0, y0, x1, y1 = v[:, 0].min(), v[:, 1].min(), v[:, 0].max(), v[:, 1].max()
    ax.text((x0 + x1) / 2, y0 - 3, f"{namn.replace('_', ' ')}  ·  {farge}", color=LYS, fontsize=6.5, ha="center", va="top")
ax.set_xlim(-8, 264); ax.set_ylim(-14, 264); ax.set_aspect("equal"); ax.axis("off")
ax.text(0, 262, "Sveip mini · alle delar på éi plate (P1S, 256 × 256 mm)", color=LYS, fontsize=9, ha="left", va="bottom")
ax.text(256, -12, "framme", color=GRAA, fontsize=6, ha="right", va="bottom")
ut = HER / "print" / "Sveip_mini_alle_delar.png"
fig.savefig(ut, facecolor="black", bbox_inches="tight")
print("SKREIV", ut)
