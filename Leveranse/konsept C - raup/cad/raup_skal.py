# -*- coding: utf-8 -*-
"""raup_skal.py · Bygg berre hovudskalet til RAUP (Class-A ope-botn B-rep) for STEP, STL og Bambu Lab P1S 3MF.

    py -3 cad/raup_skal.py [vegg_mm] [total_lampehogd_mm]

Standard: 4.0 mm jamn veggtjukkleik, 270.0 mm total lampehøgd (1:1 mm-skala).
Skriv cad/raup_skal.step, produksjon/raup_skal_P1S.stl, print/RAUP_P1S_<vegg>mm_0infill.3mf og kontroll/raup_skal.json.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import cadquery as cq
from OCP.BRepCheck import BRepCheck_Analyzer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from raup_geometri import (
    CAD_DIR,
    OUT_DIR,
    PRINT_DIR,
    TEST_DIR,
    RaupParams,
    build_clean_textured_shell_mesh,
    build_main_body_shell,
    export_bambu_p1s_3mf,
)
from raup_produksjon import _measure_fbx_deviation, _measure_shell_wall_thickness, _verify_3mf_scale_and_manifold


def main():
    t0 = time.time()
    wall_mm = float(sys.argv[1]) if len(sys.argv) > 1 else 2.5
    total_h = float(sys.argv[2]) if len(sys.argv) > 2 else 200.0
    params = RaupParams(total_height_mm=total_h, wall_mm=wall_mm)

    for d in (CAD_DIR, OUT_DIR, PRINT_DIR, TEST_DIR):
        d.mkdir(parents=True, exist_ok=True)

    shell, outer_body, meta = build_main_body_shell(params)
    bb = shell.BoundingBox()

    step_path = CAD_DIR / "raup_skal.step"
    stl_path = OUT_DIR / "raup_skal_P1S.stl"
    out_3mf = PRINT_DIR / f"RAUP_P1S_H{total_h:g}_{wall_mm:g}mm_fuzzy.3mf"

    cq.exporters.export(shell, str(step_path))
    reimp = cq.importers.importStep(str(step_path)).val()
    re_ok = bool(reimp.isValid() and BRepCheck_Analyzer(reimp.wrapped).IsValid())
    build_clean_textured_shell_mesh(shell, meta, params, max_edge_mm=1.10, tex_amp_mm=0.095, out_stl=stl_path)
    info_3mf = export_bambu_p1s_3mf(
        shell,
        out_3mf,
        wall_mm=wall_mm,
        total_height_mm=total_h,
        lin_deflection=0.05,
        ang_deflection=0.10,
        layer_height_mm=0.16,
        fuzzy_skin="external",
        fuzzy_thickness_mm=0.08,
        fuzzy_point_dist_mm=params.fuzzy_skin_point_dist_mm,
        stl_source=stl_path,
    )
    v3mf = _verify_3mf_scale_and_manifold(out_3mf, (bb.xlen, bb.ylen, bb.zlen))

    report = {
        "filer": ["cad/raup_skal.step", "produksjon/raup_skal_P1S.stl", v3mf["fil"]],
        "metode": "Class-A NURBS (grad <= 3) periodisk B-rep med eksakt 3D normal-offset kuppel og ope botn",
        "skala": f"Eksakt 1:1 mm (total lampehøgd {total_h:.1f} mm)",
        "veggtjukkleik_mm": wall_mm,
        "botn": "open (z = 0.000 mm)",
        "gyldig_BRep": bool(shell.isValid() and BRepCheck_Analyzer(shell.wrapped).IsValid()),
        "STEP_attlest_gyldig": re_ok,
        "eitt_solid": len(shell.Solids()) == 1,
        "flater": len(shell.Faces()),
        "mal_mm": [round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2)],
        "passar_P1S_256": v3mf["fits_P1S_256"],
        "volum_cm3": round(shell.Volume() / 1e3, 1),
        "masse_papirmasse_g": round(shell.Volume() / 1e3 * 0.65),
        "masse_PLA_g": round(shell.Volume() / 1e3 * 1.24),
        "veggkontroll": _measure_shell_wall_thickness(shell, meta, params),
        "fbx_avvik_ytterform": _measure_fbx_deviation(outer_body, total_h),
        "bambu_3mf_verifisering": v3mf,
        "wall_loops_anbefalt": info_3mf["wall_loops"],
        "tid_s": round(time.time() - t0, 2),
    }
    (TEST_DIR / "raup_skal.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
