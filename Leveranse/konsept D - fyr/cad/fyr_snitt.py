# -*- coding: utf-8 -*-
"""FYR · fargelagde snitt for kontroll (matplotlib). Kvar del har sin farge.

    py -3 cad/fyr_snitt.py <utmappe> [theta] [prototype]

Lagar:
  snitt_XZ*.png    loddrette snitt gjennom aksen i planet y = 0 (vindauget til høgre, +X)
  snitt_z*.png     vassrette snitt
"""
from __future__ import annotations

import sys
from pathlib import Path

import cadquery as cq
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402

HER = Path(__file__).resolve().parent
sys.path.insert(0, str(HER))
import fyr_geometri as g  # noqa: E402

FARGAR = {
    "01_fot": "#6b1a1f", "03_chassis": "#2b2b2e", "04_mantel": "#8c2229", "05_hylse": "#c9a043",
    "05b_hylsefot": "#555555", "05c_stoppskruar": "#2060c0", "06_lysstav": "#aeb4ba", "06b_led_side": "#ffb000",
    "06c_led_topp": "#ffb000", "06d_kontakt": "#406040", "07_lysrist": "#cfc9b8", "08_lok": "#e8e2c8",
    "10_glidering": "#000000", "11_oring": "#111111", "12_brytarar": "#3030c0",
}


def snitt(shape: cq.Shape, origo, normal):
    plan = cq.Face.makePlane(None, None, basePnt=cq.Vector(*origo), dir=cq.Vector(*normal))
    try:
        r = shape.intersect(plan)
        return [f for f in r.Faces()]
    except Exception:  # noqa: BLE001
        return []


def trekantar(faces, mapping):
    polys = []
    for f in faces:
        try:
            verts, tris = f.tessellate(0.02, 0.1)
        except Exception:  # noqa: BLE001
            continue
        pts = [mapping(v) for v in verts]
        for t in tris:
            polys.append([pts[t[0]], pts[t[1]], pts[t[2]]])
    return polys


def shape_of(wp):
    vals = wp.vals()
    return vals[0] if len(vals) == 1 else cq.Compound.makeCompound(vals)


def main():
    ut = Path(sys.argv[1])
    ut.mkdir(parents=True, exist_ok=True)
    theta = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    p = g.FyrParams.prototype() if (len(sys.argv) > 3 and sys.argv[3] == "prototype") else g.FyrParams()
    d = {k: shape_of(v) for k, v in g.bygg_alle(p, theta).items()}

    def loddrett(fil, xlim, ylim, w, h, phi=0.0, tittel=""):
        """Snitt i planet gjennom aksen på asimut phi (forskyvd 0,37 mm for å unngå skøytar)."""
        import math as _m
        c, s_ = _m.cos(_m.radians(phi)), _m.sin(_m.radians(phi))
        n = (-s_, c, 0.0)
        o = (-s_ * 0.37, c * 0.37, 0.0)
        fig, ax = plt.subplots(figsize=(w, h), dpi=150)
        for namn, s in d.items():
            fs = snitt(s, o, n)
            polys = trekantar(fs, lambda v: (v.x * c + v.y * s_, v.z))
            if polys:
                ax.add_collection(PolyCollection(polys, facecolors=FARGAR.get(namn, "#999"), edgecolors="none"))
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal")
        ax.grid(True, lw=0.3, alpha=0.5)
        ax.set_xlabel(f"radius langs asimut {phi:.3f}° [mm]")
        ax.set_ylabel("z [mm]")
        ax.set_title(f"FYR {p.variant}  snitt asimut {phi:.3f}°  hylse θ = {theta:.2f}°  {tittel}")
        fig.tight_layout()
        fig.savefig(ut / fil)
        plt.close(fig)

    loddrett("snitt_XZ.png", (-52, 52), (-2, 302), 7, 18)
    loddrett("snitt_XZ_botn.png", (-52, 52), (0, 95), 12, 11)
    loddrett("snitt_XZ_topp.png", (-52, 52), (245, 302), 12, 7)
    loddrett("snitt_XZ_lager.png", (24, 48), (64, 96), 9, 11)
    loddrett("snitt_spalte.png", (-52, 52), (-2, 302), 7, 18, phi=5.625, tittel="gjennom spalte")
    loddrett("snitt_spalte_rist.png", (-4, 48), (140, 200), 12, 11, phi=5.625, tittel="gjennom spalte")
    loddrett("snitt_spalte_topp.png", (-4, 48), (225, 300), 12, 14, phi=5.625, tittel="gjennom spalte")
    for (a_sw, _t) in p.sw:
        loddrett(f"snitt_brytar_{int(a_sw):03d}.png", (20, 48), (56, 92), 9, 11, phi=a_sw, tittel="gjennom brytar")

    for z in (5.0, 6.2, 12.0, 30.0, 73.0, 77.0, 79.0, 86.0, 150.0, 268.0, 279.0, 285.0):
        fig, ax = plt.subplots(figsize=(9, 9), dpi=140)
        for namn, s in d.items():
            fs = snitt(s, (0, 0, z), (0, 0, 1))
            polys = trekantar(fs, lambda v: (v.x, v.y))
            if polys:
                ax.add_collection(PolyCollection(polys, facecolors=FARGAR.get(namn, "#999"), edgecolors="none"))
        ax.set_xlim(-52, 52)
        ax.set_ylim(-52, 52)
        ax.set_aspect("equal")
        ax.grid(True, lw=0.3, alpha=0.5)
        ax.set_title(f"FYR {p.variant}  snitt z = {z:.1f}  hylse θ = {theta:.2f}°")
        fig.tight_layout()
        fig.savefig(ut / f"snitt_z{z:05.1f}.png")
        plt.close(fig)
    print("ok", ut)


if __name__ == "__main__":
    main()
