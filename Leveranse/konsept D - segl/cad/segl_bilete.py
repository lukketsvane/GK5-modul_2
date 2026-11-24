# -*- coding: utf-8 -*-
"""segl_bilete.py · biletet av dei utbretta emna (produksjon/segl_utbretta.png): svart strek på kvitt, bøyelinjer stipla,
sveisepunkt som kryss. Køyr etter segl_utbretta.py."""
import os, sys
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
HER = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HER)
import segl_utbretta as U

if __name__ == '__main__':
    fig, ax = plt.subplots(figsize=(16, 9), dpi=150)
    ox = 0
    for namn, fn in (('D01 framsegl', U.utbrett_d01), ('D02 høgsegl', U.utbrett_d02), ('E01 lysberar', U.utbrett_e01), ('E02 botnplate', U.utbrett_botn)):
        form, boy, merke, _ = fn()
        b = form.bounds; dx = ox - b[0]; dy = -b[1]
        for g in (form.geoms if hasattr(form, 'geoms') else [form]):
            for ring in [g.exterior] + list(g.interiors):
                xy = np.array(ring.coords); ax.plot(xy[:, 0] + dx, xy[:, 1] + dy, color='black', lw=0.9)
        for nr, kva, vinkel, retn, ls in boy:
            xy = np.array(ls.coords); ax.plot(xy[:, 0] + dx, xy[:, 1] + dy, color='black', lw=0.6, ls=(0, (6, 4)))
        for p in merke:
            ax.plot([p[0] + dx - 2, p[0] + dx + 2], [p[1] + dy] * 2, color='black', lw=0.6)
            ax.plot([p[0] + dx] * 2, [p[1] + dy - 2, p[1] + dy + 2], color='black', lw=0.6)
        ax.text(ox, -14, namn, fontsize=10, family='Arial')
        ox += (b[2] - b[0]) + 40
    ax.set_aspect('equal'); ax.axis('off')
    fig.savefig(os.path.join(os.path.dirname(HER), 'produksjon', 'segl_utbretta.png'), dpi=150, facecolor='white', bbox_inches='tight', pad_inches=0.3)
