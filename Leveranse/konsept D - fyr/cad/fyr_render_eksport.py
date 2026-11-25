# -*- coding: utf-8 -*-
"""FYR · eksporterer fine STL-ar for rendering (serie-geometri), éin fil per del.

    py -3 cad/fyr_render_eksport.py <utmappe> [theta]

Filene får namnet <del>.stl i mm. Blender-skriptet fyr_render.py les dei.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cadquery as cq

HER = Path(__file__).resolve().parent
sys.path.insert(0, str(HER))
import fyr_geometri as g  # noqa: E402


def main():
    ut = Path(sys.argv[1])
    ut.mkdir(parents=True, exist_ok=True)
    theta = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    p = g.FyrParams()
    d = g.bygg_alle(p, theta)
    for namn, wp in d.items():
        vals = wp.vals()
        s = vals[0] if len(vals) == 1 else cq.Compound.makeCompound(vals)
        cq.exporters.export(s, str(ut / f"{namn}.stl"), tolerance=0.01, angularTolerance=0.04)
    info = {
        "theta": theta,
        "stripe": {"x": p.stav_t / 2 + p.stripe_t, "z0": p.stripe_z0, "z1": p.stripe_z1, "b": p.stripe_b},
        "topp": {"z": p.topp_berar_z + 1.5 + p.stripe_t, "l": p.topp_l, "b": p.stripe_b, "r": p.topp_r, "n": p.topp_n},
        "rist_avskjering_2D": p.rist_avskjering,
        "lok": {"z0": p.z_lok_0, "z1": p.z_lok_1, "r": p.r_lok},
        "hogd": p.z_hylse_1,
        "spalter": {"z0": p.z_spalte_0, "z1": p.z_spalte_1, "vinklar": p.vindauge_vinklar, "r": p.r_mo},
    }
    (ut / "scene.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print("ok", ut, len(d), "delar")


if __name__ == "__main__":
    main()
