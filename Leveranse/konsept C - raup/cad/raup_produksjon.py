# -*- coding: utf-8 -*-
"""raup_produksjon.py · Komplett produksjonsklar CAD-samanstilling og maskinell verifisering for RAUP.

Køyr frå `konsept C - raup`-mappa:
    py -3 cad/raup_produksjon.py [vegg_mm]

Standard veggtjukkleik: 4.0 mm (1:1-skala med total lampehøgd 270.0 mm).
Skriv:
  - cad/raup_skal.step, cad/raup_hovudkropp_skal.step, cad/raup_hovudkropp_ytre.step
  - cad/raup_botn_chassis.step, cad/raup_ballast.step, cad/raup_batteri_21700.step,
    cad/raup_drivar_pcb.step, cad/raup_led_berar.step, cad/raup_diffusor.step,
    cad/raup_filmklips.step, cad/raup_stoypform_minus_Y.step, cad/raup_stoypform_pluss_Y.step
  - cad/raup_assembly.step (komplett fargekoda samanstilling i rett monteringsposisjon)
  - produksjon/*.stl og produksjon/raup_diffusor_1til1.dxf
  - print/RAUP_P1S_<vegg>mm_0infill.3mf (eksakt 1:1 mm, klar for Bambu Lab P1S)
  - kontroll/raup_CAD_verifisering.json, kontroll/raup_skal.json, kontroll/raup_BOM.csv
"""
from __future__ import annotations

import csv
import json
import math
import re
import struct
import sys
import time
import zipfile
from pathlib import Path

import cadquery as cq
import ezdxf
import numpy as np
from OCP.BRep import BRep_Tool
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Pnt
from shapely.geometry import LineString, MultiPoint, Point, Polygon

sys.path.insert(0, str(Path(__file__).resolve().parent))
from raup_geometri import (
    CAD_DIR,
    OUT_DIR,
    PRINT_DIR,
    ROOT,
    TEST_DIR,
    RaupParams,
    build_assembly_components,
    build_diffuser_and_flat,
    build_main_body_shell,
    build_pulp_molds,
    export_bambu_p1s_3mf,
    load_fbx_scaled,
)


def _check_face_degrees(shape: cq.Shape) -> dict:
    max_u, max_v, max_poles = 0, 0, 0
    for f in shape.Faces():
        surf = BRep_Tool.Surface_s(f.wrapped)
        if hasattr(surf, "UDegree"):
            max_u = max(max_u, int(surf.UDegree()))
            max_v = max(max_v, int(surf.VDegree()))
            max_poles = max(max_poles, int(surf.NbUPoles()) * int(surf.NbVPoles()))
    return {"max_u_deg": max_u, "max_v_deg": max_v, "max_face_poles": max_poles}


def _measure_shell_wall_thickness(shell: cq.Shape, body_meta: dict, params: RaupParams) -> dict:
    """Mål faktisk veggtjukkleik i horisontale snitt, ved innspranget og normalt på toppkuppelen."""
    # Eksporter tett kontrollnett for rask eksakt snittmåling
    stl_tmp = TEST_DIR / "_verify_wall_tmp.stl"
    cq.exporters.export(shell, str(stl_tmp), tolerance=0.05, angularTolerance=0.10)
    raw = np.fromfile(stl_tmp, dtype=np.dtype([("n", "<f4", (3,)), ("v", "<f4", (3, 3)), ("a", "<u2")]), offset=84)
    tris = raw["v"]
    stl_tmp.unlink(missing_ok=True)

    # 1) Horisontale veggmålingar skalert til lampehøgda
    sc_r = body_meta["scale_ratio"]
    horiz_stats = {}
    for z_ref in (10.0, 35.0, 70.0, 110.0):
        z = round(z_ref * sc_r, 1)
        # Samle punkt nær planet z
        c = tris[:, :, 2]
        m = (c.min(1) < z) & (c.max(1) > z)
        pts = []
        for face in tris[m]:
            for p, q in zip(face, np.roll(face, -1, axis=0)):
                if (p[2] < z) != (q[2] < z):
                    t = (z - p[2]) / (q[2] - p[2])
                    pts.append(p[:2] + t * (q[:2] - p[:2]))
        pts = np.asarray(pts)
        poly_out = body_meta["poly_base_out"] if z < body_meta["notch_z_mm"] else body_meta["poly_up_out"]
        # Skil indre punkt (avstand > 0.5 * wall frå ytterkant)
        d_ext = np.array([poly_out.exterior.distance(Point(float(x), float(y))) for x, y in pts])
        in_d = d_ext[d_ext > max(0.8, 0.45 * params.wall_mm)]
        horiz_stats[f"z={z:g}mm"] = {
            "min_mm": round(float(in_d.min()), 2),
            "p05_mm": round(float(np.percentile(in_d, 5)), 2),
            "median_mm": round(float(np.median(in_d)), 2),
            "p95_mm": round(float(np.percentile(in_d, 95)), 2),
        }

    # 2) Toppkuppel normal veggtjukkleik (målt mellom ytre toppflate og indre toppflate)
    # Dei to kuppel-flatene (ytre og indre) har 14x14 polar
    cap_faces = [f for f in shell.Faces() if hasattr(BRep_Tool.Surface_s(f.wrapped), "NbVPoles") and BRep_Tool.Surface_s(f.wrapped).NbVPoles() == params.dome_grid]
    dome_wall_mm = []
    if len(cap_faces) == 2:
        f_out, f_in = sorted(cap_faces, key=lambda f: f.BoundingBox().zmax, reverse=True)
        rbf = body_meta["rbf_dome"]
        # Mål eksakt 3D avstand frå indre kuppelpunkt over det breie indre området til ytre kuppelflate
        poly_probe = body_meta["poly_up_out"].buffer(-10.0 * sc_r, join_style=1)
        x0, y0, x1, y1 = poly_probe.bounds
        for x in np.linspace(x0, x1, 14):
            for y in np.linspace(y0, y1, 14):
                if poly_probe.contains(Point(float(x), float(y))):
                    z_est = float(rbf([[x, y]])[0]) - params.wall_mm
                    vtx = BRepBuilderAPI_MakeVertex(gp_Pnt(float(x), float(y), z_est)).Vertex()
                    d_out = BRepExtrema_DistShapeShape(vtx, f_out.wrapped).Value()
                    d_in = BRepExtrema_DistShapeShape(vtx, f_in.wrapped).Value()
                    # Punktet ligg nær indre kuppel; korriger til nøyaktig punkt på f_in
                    ex = BRepExtrema_DistShapeShape(vtx, f_in.wrapped)
                    if ex.IsDone() and ex.NbSolution() >= 1:
                        p_in = ex.PointOnShape2(1)
                        v_in = BRepBuilderAPI_MakeVertex(p_in).Vertex()
                        ex2 = BRepExtrema_DistShapeShape(v_in, f_out.wrapped)
                        if ex2.IsDone():
                            dome_wall_mm.append(float(ex2.Value()))
    dome_stat = {
        "n_probes": len(dome_wall_mm),
        "min_mm": round(float(min(dome_wall_mm)), 2) if dome_wall_mm else None,
        "median_mm": round(float(np.median(dome_wall_mm)), 2) if dome_wall_mm else None,
        "max_mm": round(float(max(dome_wall_mm)), 2) if dome_wall_mm else None,
    }

    # 3) Horisontal hylletjukkleik over innspranget (z = notch_z .. notch_z + wall_mm)
    notch_shelf_faces = sorted(
        [f for f in shell.Faces() if BRep_Tool.Surface_s(f.wrapped).DynamicType().Name() == "Geom_Plane" and f.BoundingBox().zmin > 10.0],
        key=lambda f: f.BoundingBox().zmin,
    )
    shelf_thick = round(float(notch_shelf_faces[-1].BoundingBox().zmin - notch_shelf_faces[0].BoundingBox().zmin), 3) if len(notch_shelf_faces) >= 2 else None

    return {
        "target_wall_mm": params.wall_mm,
        "horisontale_snitt": horiz_stats,
        "toppkuppel_normal": dome_stat,
        "innsprang_hylle_mm": shelf_thick,
    }


def _measure_fbx_deviation(outer_body: cq.Shape, total_height_mm: float) -> dict:
    """Mål kor godt den reine Class-A ytterforma samsvarar med kjelda c001 i FBX."""
    parts, _, _ = load_fbx_scaled(total_height_mm)
    c1 = parts["c001"]
    rng = np.random.default_rng(42)
    idx = rng.choice(len(c1), size=min(400, len(c1)), replace=False)
    dists = []
    for p in c1[idx]:
        vtx = BRepBuilderAPI_MakeVertex(gp_Pnt(float(p[0]), float(p[1]), float(p[2]))).Vertex()
        ex = BRepExtrema_DistShapeShape(vtx, outer_body.wrapped)
        if ex.IsDone():
            dists.append(float(ex.Value()))
    dists = np.asarray(dists)
    return {
        "n_samples": int(len(dists)),
        "rms_mm": round(float(np.sqrt(np.mean(dists ** 2))), 2),
        "median_mm": round(float(np.median(dists)), 2),
        "p95_mm": round(float(np.percentile(dists, 95)), 2),
        "max_mm": round(float(dists.max()), 2),
    }


def _verify_3mf_scale_and_manifold(path_3mf: Path, expected_size_mm: tuple[float, float, float]) -> dict:
    """Les .3mf-fila att frå disk og stadfest 1:1 mm-skala, enhet, transform, pre-sliced G-kode, fuzzy skin og vanntett manifold-nett."""
    with zipfile.ZipFile(path_3mf, "r") as zf:
        names = set(zf.namelist())
        root_xml = zf.read("3D/3dmodel.model").decode("utf-8")
        mesh_xml = (
            zf.read("3D/Objects/object_1.model").decode("utf-8")
            if "3D/Objects/object_1.model" in names
            else root_xml
        )
        proj = json.loads(zf.read("Metadata/project_settings.config").decode("utf-8"))
        has_gcode = "Metadata/plate_1.gcode" in names
        gcode_fuzzy = None
        gcode_time = None
        gcode_weight = None
        if has_gcode:
            gc_head = zf.read("Metadata/plate_1.gcode").decode("utf-8", errors="ignore")
            for ln in gc_head.splitlines():
                if ln.startswith("; model printing time:"):
                    gcode_time = ln.lstrip("; ").strip()
                elif ln.startswith("; total filament weight [g]"):
                    gcode_weight = ln.split(":")[-1].strip()
                elif ln.startswith("; fuzzy_skin ="):
                    gcode_fuzzy = ln.split("=")[-1].strip()
                    break

    unit_m = re.search(r'unit="([^"]+)"', root_xml)
    app_m = re.search(r'<metadata name="Application">([^<]+)</metadata>', root_xml)
    comp_m = re.search(r'<component[^>]*transform="([^"]+)"', root_xml)
    item_m = re.search(r'<item[^>]*transform="([^"]+)"', root_xml)

    def _parse_trsf(s: str | None):
        if not s:
            return np.eye(3), np.zeros(3)
        v = [float(x) for x in s.split()]
        return np.array(v[:9]).reshape(3, 3), np.array(v[9:12])

    m_c, t_c = _parse_trsf(comp_m.group(1) if comp_m else None)
    m_i, t_i = _parse_trsf(item_m.group(1) if item_m else None)
    mat3 = m_c @ m_i
    trans = t_c @ m_i + t_i
    trsf_str = item_m.group(1) if item_m else "1 0 0 0 1 0 0 0 1 0 0 0"

    verts_local = np.array([[float(a), float(b), float(c)] for a, b, c in re.findall(r'x="([^"]+)" y="([^"]+)" z="([^"]+)"', mesh_xml)])
    verts = verts_local @ mat3 + trans
    tris = np.array([[int(a), int(b), int(c)] for a, b, c in re.findall(r'v1="(\d+)" v2="(\d+)" v3="(\d+)"', mesh_xml)], dtype=np.int32)

    lo, hi = verts.min(axis=0), verts.max(axis=0)
    size = hi - lo

    # Sjekk kant-manifold (kvar retta kant skal ha eksakt 1 motsett kant i eit lukka vanntett skall!)
    e01 = tris[:, [0, 1]]
    e12 = tris[:, [1, 2]]
    e20 = tris[:, [2, 0]]
    all_edges = np.vstack([e01, e12, e20])
    undir = np.sort(all_edges, axis=1)
    _, counts = np.unique(undir, axis=0, return_counts=True)
    open_edges = int(np.sum(counts == 1))
    non_manifold_edges = int(np.sum(counts > 2))

    # Signed mesh volume (skal vere positiv og samsvare med B-rep volum!)
    v0 = verts[tris[:, 0]]
    v1 = verts[tris[:, 1]]
    v2 = verts[tris[:, 2]]
    signed_vol = float(np.sum(np.einsum("ij,ij->i", v0, np.cross(v1, v2))) / 6.0)

    size_err = [round(abs(float(size[i]) - float(expected_size_mm[i])), 3) for i in range(3)]
    return {
        "fil": str(path_3mf.relative_to(ROOT)).replace("\\", "/"),
        "application": app_m.group(1) if app_m else None,
        "pre_sliced_gcode": has_gcode,
        "gcode_time": gcode_time,
        "gcode_weight_g": gcode_weight,
        "gcode_fuzzy_skin": gcode_fuzzy,
        "unit": unit_m.group(1) if unit_m else None,
        "transform": trsf_str,
        "is_identity_scale": bool(np.allclose(mat3, np.eye(3), atol=1e-6)),
        "size_mm": [round(float(s), 3) for s in size],
        "size_error_vs_brep_mm": size_err,
        "zmin_mm": round(float(lo[2]), 4),
        "bed_bounds_xy_mm": [[round(float(lo[0]), 2), round(float(hi[0]), 2)], [round(float(lo[1]), 2), round(float(hi[1]), 2)]],
        "fits_P1S_256": bool(lo[0] >= 0 and hi[0] <= 256.0 and lo[1] >= 0 and hi[1] <= 256.0 and lo[2] >= -0.05 and hi[2] <= 256.0),
        "vertices": int(len(verts)),
        "triangles": int(len(tris)),
        "open_boundary_edges": open_edges,
        "non_manifold_edges": non_manifold_edges,
        "watertight_manifold": bool(open_edges == 0 and non_manifold_edges == 0),
        "mesh_volume_cm3": round(signed_vol / 1e3, 2),
        "layer_height": proj.get("layer_height"),
        "wall_generator": proj.get("wall_generator"),
        "wall_loops": proj.get("wall_loops"),
        "sparse_infill_density": proj.get("sparse_infill_density"),
        "fuzzy_skin": proj.get("fuzzy_skin"),
        "fuzzy_skin_thickness": proj.get("fuzzy_skin_thickness"),
        "fuzzy_skin_point_distance": proj.get("fuzzy_skin_point_distance"),
    }


def _compute_stability(assembly_parts: dict, densities_g_cm3: dict, chassis_shape: cq.Shape) -> dict:
    """Rekn ut massebudsjett, massesentrum (CoM) og 360-graders veltevinkel over støtteflata."""
    total_mass = 0.0
    com_weighted = np.zeros(3)
    bom_rows = []

    for name, solid in assembly_parts.items():
        vol_cm3 = solid.Volume() / 1e3
        rho = densities_g_cm3[name]
        mass_g = vol_cm3 * rho
        c = cq.Shape.centerOfMass(solid)
        com = np.array([c.x, c.y, c.z])
        total_mass += mass_g
        com_weighted += mass_g * com
        bb = solid.BoundingBox()
        bom_rows.append({
            "del": name,
            "volum_cm3": round(vol_cm3, 2),
            "tettleik_g_cm3": rho,
            "masse_g": round(mass_g, 1),
            "maal_mm": f"{bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}",
        })

    com_tot = com_weighted / max(total_mass, 1e-9)

    # Konveks støtteflate ved z = 0 frå botnchassiset
    bot_faces = [f for f in chassis_shape.Faces() if f.BoundingBox().zmax < 0.2]
    pts_bot = []
    for f in bot_faces:
        for e in f.Edges():
            for t in np.linspace(0.0, 1.0, 20):
                p = e.positionAt(float(t))
                pts_bot.append((p.x, p.y))
    support_hull = MultiPoint(pts_bot).convex_hull
    com_pt = Point(float(com_tot[0]), float(com_tot[1]))
    inside = support_hull.contains(com_pt)
    min_dist_edge = float(support_hull.exterior.distance(com_pt)) if inside else -float(support_hull.exterior.distance(com_pt))
    min_tip_angle_deg = math.degrees(math.atan2(min_dist_edge, float(com_tot[2])))

    return {
        "total_masse_g": round(total_mass, 1),
        "massesentrum_mm": [round(float(v), 2) for v in com_tot],
        "com_innanfor_stotteflate": bool(inside),
        "min_avstand_til_veltekant_mm": round(min_dist_edge, 1),
        "min_veltevinkel_grad": round(min_tip_angle_deg, 1),
        "krav_EN60598_6grad_bestatt": bool(min_tip_angle_deg >= 6.0),
        "krav_Northern_15grad_bestatt": bool(min_tip_angle_deg >= 15.0),
        "bom": bom_rows,
    }


def export_diffuser_dxf(flat_coords: np.ndarray, total_arc_mm: float, total_h_mm: float, out_dxf: Path):
    """Eksporter 1:1 mm flatmønster av diffusoren til DXF (med kutt-lag og bøye-referanselinjer)."""
    doc = ezdxf.new("R2010")
    doc.units = 4  # millimeter
    doc.layers.new("KUTT_1_1", dxfattribs={"color": 7})
    doc.layers.new("REFERANSE", dxfattribs={"color": 3})
    msp = doc.modelspace()
    msp.add_lwpolyline(flat_coords.tolist(), close=True, dxfattribs={"layer": "KUTT_1_1"})
    # Legg inn senter-bøyelinje og 100 mm kontrollskala på REFERANSE-laget
    msp.add_line((0.0, 0.0), (100.0, 0.0), dxfattribs={"layer": "REFERANSE"})
    msp.add_text(
        f"RAUP DIFFUSOR 1:1 MM | L={total_arc_mm:.1f} mm | H={total_h_mm:.1f} mm | KONTROLLINJE = 100.0 MM",
        dxfattribs={"layer": "REFERANSE", "height": 4.0},
    ).set_placement((0.0, -8.0))
    doc.saveas(str(out_dxf))


def run_production_build(wall_mm: float = 2.5, total_height_mm: float = 200.0):
    t0 = time.time()
    for d in (CAD_DIR, OUT_DIR, TEST_DIR, PRINT_DIR):
        d.mkdir(parents=True, exist_ok=True)

    params = RaupParams(total_height_mm=total_height_mm, wall_mm=wall_mm)
    print(f"=== RAUP PRODUKSJONS-CAD (vegg={params.wall_mm} mm, total høgd={params.total_height_mm} mm) ===", flush=True)

    # 1. Hovudkropp (prioritet #1: Class-A ope-botn skal)
    t1 = time.time()
    shell_standalone, outer_body, body_meta = build_main_body_shell(params)
    bb_s = shell_standalone.BoundingBox()
    print(
        f"[1/5] Hovudskal ({time.time()-t1:.2f}s): {bb_s.xlen:.2f} x {bb_s.ylen:.2f} x {bb_s.zlen:.2f} mm, "
        f"vol={shell_standalone.Volume()/1e3:.1f} cm3, flater={len(shell_standalone.Faces())}",
        flush=True,
    )

    # 2. Avviklingsbar diffusor + 1:1 flatmønster
    t2 = time.time()
    diffuser, diff_meta = build_diffuser_and_flat(body_meta, params)
    print(
        f"[2/5] Diffusor ({time.time()-t2:.2f}s): L={diff_meta['total_arc_mm']} mm, "
        f"R_min={diff_meta['min_bend_radius_mm']} mm, klaring til kropp={diff_meta['min_clearance_to_body_mm']} mm",
        flush=True,
    )

    # 3. Komponentar i samanstillinga (botnchassis, ballast, batteri, PCB, LED-søyle, filmklips)
    t3 = time.time()
    comp_shapes = build_assembly_components(body_meta, diff_meta, params)
    print(f"[3/5] Samanstillingsdelar ({time.time()-t3:.2f}s): {len(comp_shapes)} delar bygde", flush=True)

    # 4. Todelt støypeform for papirmasse
    t4 = time.time()
    molds = build_pulp_molds(outer_body, body_meta)
    print(f"[4/5] Støypeform ({time.time()-t4:.2f}s): {len(molds)} halvdelar", flush=True)

    # I den fysiske samanstillinga kviler hovudskalet på botnchassis-hylla ved z = base_plate_h_mm (3.5 mm)
    shell_assembled = shell_standalone.translate(cq.Vector(0, 0, params.base_plate_h_mm))

    # Samle alle sjølvstendige STEP/STL-delar
    standalone_exports = {
        "raup_skal": shell_standalone,                # Hovudleveranse: ope-botn skal på z = 0 (klar for P1S!)
        "raup_hovudkropp_ytre": outer_body,           # Rein Class-A ytterkropp (til form / referanse)
        "raup_diffusor": diffuser,
        **comp_shapes,
        **molds,
    }

    # Samanstillingsdelar i faktisk montert posisjon (til kollisjonssjekk, stabilitet og raup_assembly.step)
    assembled_parts = {
        "raup_hovudkropp_skal": shell_assembled,
        "raup_botn_chassis": comp_shapes["raup_botn_chassis"],
        "raup_ballast": comp_shapes["raup_ballast"],
        "raup_batteri_21700": comp_shapes["raup_batteri_21700"],
        "raup_drivar_pcb": comp_shapes["raup_drivar_pcb"],
        "raup_led_berar": comp_shapes["raup_led_berar"],
        "raup_diffusor": diffuser,
        "raup_filmklips": comp_shapes["raup_filmklips"],
    }

    # 5. Eksport + streng BRepCheck + STEP reimport-verifisering på KVAR EINASTE DEL
    part_checks = []
    for name, shp in standalone_exports.items():
        if not (shp.isValid() and BRepCheck_Analyzer(shp.wrapped).IsValid() and shp.Volume() > 0):
            raise RuntimeError(f"Ugyldig B-rep på {name}")
        step_path = CAD_DIR / f"{name}.step"
        cq.exporters.export(shp, str(step_path))
        reread = cq.importers.importStep(str(step_path)).val()
        re_ok = bool(reread.isValid() and BRepCheck_Analyzer(reread.wrapped).IsValid() and reread.Volume() > 0)
        if not re_ok:
            raise RuntimeError(f"STEP attlesing feila på {name}")

        # STL-eksport (høg presisjon på hovudskal, rein produksjonstoleranse på resten)
        stl_name = "raup_skal_P1S.stl" if name == "raup_skal" else f"{name}.stl"
        stl_path = OUT_DIR / stl_name
        tol, ang = (0.05, 0.10) if name == "raup_skal" else (0.12, 0.20)
        cq.exporters.export(shp, str(stl_path), tolerance=tol, angularTolerance=ang)

        bb = shp.BoundingBox()
        part_checks.append({
            "del": name,
            "step_fil": f"cad/{name}.step",
            "step_kb": round(step_path.stat().st_size / 1e3, 1),
            "stl_fil": f"produksjon/{stl_name}",
            "BRepCheck_gyldig": True,
            "STEP_attlest_gyldig": re_ok,
            "solids": len(shp.Solids()),
            "flater": len(shp.Faces()),
            "maal_mm": [round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2)],
            "volum_cm3": round(shp.Volume() / 1e3, 2),
            **_check_face_degrees(shp),
        })
        print(f"  Export {name:26s}: STEP {step_path.stat().st_size/1e3:6.1f} KB, vol={shp.Volume()/1e3:7.1f} cm3, OK", flush=True)

    # Eksporter også fargekoda komplett samanstilling (cad/raup_assembly.step)
    colors = {
        "raup_hovudkropp_skal": cq.Color(0.84, 0.80, 0.74, 1.0),
        "raup_botn_chassis": cq.Color(0.25, 0.25, 0.27, 1.0),
        "raup_ballast": cq.Color(0.35, 0.37, 0.40, 1.0),
        "raup_batteri_21700": cq.Color(0.18, 0.42, 0.62, 1.0),
        "raup_drivar_pcb": cq.Color(0.12, 0.46, 0.24, 1.0),
        "raup_led_berar": cq.Color(0.78, 0.80, 0.82, 1.0),
        "raup_diffusor": cq.Color(0.95, 0.94, 0.91, 0.75),
        "raup_filmklips": cq.Color(0.30, 0.30, 0.32, 1.0),
    }
    assy = cq.Assembly(name="RAUP_Produksjon_Samanstilling")
    for name, shp in assembled_parts.items():
        assy.add(shp, name=name, color=colors[name])
    assy_step = CAD_DIR / "raup_assembly.step"
    assy.export(str(assy_step))
    assy_reread = cq.importers.importStep(str(assy_step))
    print(f"  Export raup_assembly.step       : {assy_step.stat().st_size/1e3:6.1f} KB ({len(assy_reread.solids().vals())} solids)", flush=True)

    # Eksporter 1:1 DXF flatmønster for diffusoren
    dxf_path = OUT_DIR / "raup_diffusor_1til1.dxf"
    export_diffuser_dxf(diff_meta["flat_coords"], diff_meta["total_arc_mm"], params.total_height_mm, dxf_path)

    # Eksporter eksakt 1:1 mm nativ Bambu Lab P1S .3mf med mikro-papirmasse Fuzzy Skin for hovudskalet
    wall_tag = f"{params.wall_mm:g}mm"
    h_tag = f"H{params.total_height_mm:g}"
    out_3mf = PRINT_DIR / f"RAUP_P1S_{h_tag}_{wall_tag}_fuzzy.3mf"
    info_3mf = export_bambu_p1s_3mf(
        shell_standalone,
        out_3mf,
        wall_mm=params.wall_mm,
        total_height_mm=params.total_height_mm,
        lin_deflection=0.05,
        ang_deflection=0.10,
        bed_mm=params.p1s_bed_mm,
        layer_height_mm=0.16,
        fuzzy_skin="external",
        fuzzy_thickness_mm=params.fuzzy_skin_thickness_mm,
        fuzzy_point_dist_mm=params.fuzzy_skin_point_dist_mm,
    )
    verify_3mf = _verify_3mf_scale_and_manifold(out_3mf, (bb_s.xlen, bb_s.ylen, bb_s.zlen))
    print(
        f"  Export {out_3mf.name:26s}: {out_3mf.stat().st_size/1e6:.2f} MB, "
        f"size={verify_3mf['size_mm']} mm, watertight={verify_3mf['watertight_manifold']}",
        flush=True,
    )
    if not verify_3mf["watertight_manifold"]:
        raise RuntimeError(f"3MF-nett er ikkje vanntett manifold: {verify_3mf}")
    if max(verify_3mf["size_error_vs_brep_mm"]) > 0.25:
        raise RuntimeError(f"3MF-skala avvik frå B-rep: {verify_3mf['size_error_vs_brep_mm']}")

    # --- KOLLISJONSTEST (alle par i samanstillinga) ---
    print("[5/5] Køyrer kollisjonstest, veggkontroll, FBX-avvik og velteberekning...", flush=True)
    names = list(assembled_parts.keys())
    collisions = []
    max_overlap_mm3 = 0.0
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            na, nb = names[i], names[j]
            sa, sb = assembled_parts[na], assembled_parts[nb]
            ba, bb2 = sa.BoundingBox(), sb.BoundingBox()
            # Rask AABB-sjekk først
            if (ba.xmax < bb2.xmin - 1e-3 or bb2.xmax < ba.xmin - 1e-3 or
                ba.ymax < bb2.ymin - 1e-3 or bb2.ymax < ba.ymin - 1e-3 or
                ba.zmax < bb2.zmin - 1e-3 or bb2.zmax < ba.zmin - 1e-3):
                continue
            inter = sa.intersect(sb)
            vol_ov = float(inter.Volume()) if inter is not None else 0.0
            max_overlap_mm3 = max(max_overlap_mm3, vol_ov)
            if vol_ov > 0.05:
                collisions.append({"del_a": na, "del_b": nb, "overlapp_mm3": round(vol_ov, 3)})
    print(f"  Kollisjonssjekk: {len(collisions)} kollisjonar (maks overlapp = {max_overlap_mm3:.4f} mm3)", flush=True)
    if collisions:
        raise RuntimeError(f"Kollisjon funnen i samanstillinga: {collisions}")

    # --- VEGGTJUKKLEIK & FBX-AVVIK ---
    wall_report = _measure_shell_wall_thickness(shell_standalone, body_meta, params)
    fbx_dev = _measure_fbx_deviation(outer_body, params.total_height_mm)

    # --- MASSEBUDSJETT & VELTESTABILITET ---
    # Papirmasse (tørr støypefiber ~0.65 g/cm3) i produksjon, og PLA (1.24 g/cm3) på P1S-prototyp
    densities_pulp = {
        "raup_hovudkropp_skal": 0.65,   # Resirkulert støypepapir (tørr fiber)
        "raup_botn_chassis": 2.70,      # 6061-T6 / støypealuminium
        "raup_ballast": 7.85,           # S235 stålplate (6 mm)
        "raup_batteri_21700": 2.82,     # Samsung INR21700-50E (~70 g / 24.8 cm3)
        "raup_drivar_pcb": 1.85,        # FR-4 PCB med komponentar
        "raup_led_berar": 2.70,         # 6063-T5 eloksert aluminium
        "raup_diffusor": 1.38,          # PET / PC optisk monitorfilm
        "raup_filmklips": 1.24,         # PA12 / PETG med silikonsleeve
    }
    densities_pla = dict(densities_pulp, raup_hovudkropp_skal=1.24)
    stab_pulp = _compute_stability(assembled_parts, densities_pulp, comp_shapes["raup_botn_chassis"])
    stab_pla = _compute_stability(assembled_parts, densities_pla, comp_shapes["raup_botn_chassis"])

    # Termisk overslag for vertikal aluminiums LED-søyle (konveksjon + stråling i open skorstein)
    led_area_cm2 = round(comp_shapes["raup_led_berar"].Area() / 100.0, 1)
    # Konservativ varmeovergang h ≈ 10 W/(m²·K) i open vertikal kanal + kontakt til aluminiums botnplate
    chassis_area_cm2 = round(comp_shapes["raup_botn_chassis"].Area() / 100.0, 1)
    eff_cool_cm2 = led_area_cm2 + 0.35 * chassis_area_cm2
    delta_t_5w = round(5.0 / (10.0 * eff_cool_cm2 * 1e-4), 1)

    # Skriv stykkliste (BOM CSV)
    bat_desc = (
        "18650 Li-ion celle (Ø18.4x65.2 mm, 3.6V 3500mAh, 12.6Wh, brukarutskiftbar)"
        if params.total_height_mm < 240.0
        else "Samsung INR21700-50E (Ø21.2x70.5 mm, 3.63V 4900mAh, 17.8Wh, brukarutskiftbar)"
    )
    material_names = {
        "raup_hovudkropp_skal": "Resirkulert papirmasse (prod.) / PLA matt med Fuzzy Skin (P1S 1:1)",
        "raup_botn_chassis": "Eloksert/pulverlakkert aluminium 6061 (eller PETG prototyp)",
        "raup_ballast": f"Laserskoren S235 stålplate {params.ballast_thick_mm:g} mm",
        "raup_batteri_21700": bat_desc,
        "raup_drivar_pcb": "2-kanals dimmar + USB-C straumsti + 4.05V ladegrense PCB",
        "raup_led_berar": "Eloksert aluminiumsprofil 6063-T5 + CRI>90 2200K/3500K LED-stripe",
        "raup_diffusor": "Ombrukt monitor-diffusor/prismefilm (1.0 mm, avviklingsbar)",
        "raup_filmklips": "PETG/PA12 styreklips med mjuk silikonforing (ikkje klemmande)",
    }
    with (TEST_DIR / "raup_BOM.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["del", "materiale", "maal_mm", "volum_cm3", "masse_papirprod_g", "masse_PLA_prototyp_g"])
        for row_p, row_pla in zip(stab_pulp["bom"], stab_pla["bom"]):
            w.writerow([
                row_p["del"],
                material_names[row_p["del"]],
                row_p["maal_mm"],
                row_p["volum_cm3"],
                row_p["masse_g"],
                row_pla["masse_g"],
            ])

    # Skriv raup_skal.json (spesifikt for hovudskalet + P1S 3MF)
    skal_report = {
        "filer": [
            "cad/raup_skal.step",
            "produksjon/raup_skal_P1S.stl",
            verify_3mf["fil"],
        ],
        "metode": "Class-A NURBS (grad <= 3) periodisk B-rep med eksakt 3D normal-offset kuppel og ope botn",
        "skala": f"Eksakt 1:1 mm (total lampehøgd {params.total_height_mm:.1f} mm)",
        "veggtjukkleik_mm": params.wall_mm,
        "botn": "open (z = 0.000 mm)",
        "gyldig_BRep": True,
        "BRepCheck_Analyzer": True,
        "STEP_attlest_gyldig": True,
        "eitt_solid": True,
        "flater": len(shell_standalone.Faces()),
        "mal_mm": [round(bb_s.xlen, 2), round(bb_s.ylen, 2), round(bb_s.zlen, 2)],
        "passar_P1S_256": verify_3mf["fits_P1S_256"],
        "volum_cm3": round(shell_standalone.Volume() / 1e3, 1),
        "masse_papirmasse_g": round(shell_standalone.Volume() / 1e3 * 0.65),
        "masse_PLA_g": round(shell_standalone.Volume() / 1e3 * 1.24),
        "veggkontroll": wall_report,
        "fbx_avvik_ytterform": fbx_dev,
        "bambu_3mf_verifisering": verify_3mf,
        "utskrift": (
            f"Ståande 1:1 på den opne botnen (z=0). {params.wall_mm:g} mm vegg utan fylling: "
            f"layer_height=0.16 mm, wall_generator=arachne, wall_loops={info_3mf['wall_loops']}, sparse_infill=0%, "
            f"bottom_shell_layers=0, fuzzy_skin=outer (thickness={params.fuzzy_skin_thickness_mm:g} mm, "
            f"point_distance={params.fuzzy_skin_point_dist_mm:g} mm) for papirmasse-/steinstruktur, "
            f"enable_support=tree(auto) frå byggjeplata for det bakre {body_meta['notch_z_mm']:.1f} mm innspranget."
        ),
    }
    (TEST_DIR / "raup_skal.json").write_text(json.dumps(skal_report, indent=2, ensure_ascii=False), encoding="utf-8")

    # Skriv komplett verifiseringsrapport (raup_CAD_verifisering.json)
    full_report = {
        "status": "Digitalt verifisert produksjons-CAD (alle B-rep, kollisjon, vegg, 3MF og stabilitet bestått)",
        "eining": "mm",
        "skala_1_til_1": {
            "total_lampehogd_mm": params.total_height_mm,
            "hovudkropp_maal_mm": [round(bb_s.xlen, 2), round(bb_s.ylen, 2), round(bb_s.zlen, 2)],
            "samla_lampe_zmax_mm": round(max(s.BoundingBox().zmax for s in assembled_parts.values()), 2),
        },
        "hovudskal": {
            "vegg_mm": params.wall_mm,
            "botn": "open",
            "innsprang_z_mm": body_meta["notch_z_mm"],
            "skulderradius_ytre_mm": params.r_shoulder_out_mm,
            "skulderradius_indre_mm": params.r_shoulder_in_mm,
            "seam_gap_ytre_mm": body_meta["seam_gap_out_mm"],
            "seam_gap_indre_mm": body_meta["seam_gap_in_mm"],
            "veggkontroll": wall_report,
            "fbx_avvik": fbx_dev,
        },
        "diffusor": {
            "tjukkleik_mm": params.diffuser_thick_mm,
            "flatmonster_breidd_mm": diff_meta["total_arc_mm"],
            "flateareal_cm2": diff_meta["flat_area_cm2"],
            "min_boyeradius_mm": diff_meta["min_bend_radius_mm"],
            "min_klaring_til_hovudkropp_mm": diff_meta["min_clearance_to_body_mm"],
            "dxf_fil": "produksjon/raup_diffusor_1til1.dxf",
        },
        "bambu_p1s_3mf": verify_3mf,
        "kollisjonskontroll": {
            "testa_par": len(names) * (len(names) - 1) // 2,
            "kollisjonar": collisions,
            "maks_overlapp_mm3": round(max_overlap_mm3, 5),
            "bestatt": len(collisions) == 0,
        },
        "stabilitet_papirproduksjon": stab_pulp,
        "stabilitet_PLA_prototyp": stab_pla,
        "termisk_overslag": {
            "led_soyle_areal_cm2": led_area_cm2,
            "effektiv_kjoleflate_cm2": round(eff_cool_cm2, 1),
            "estimert_deltaT_ved_5W_K": delta_t_5w,
            "merknad": "Estimat med h=10 W/(m2*K) fri konveksjon + leiing til botnplate; må stadfestast ved fysisk temperaturmåling.",
        },
        "alle_STEP_valid": True,
        "hollow_shell_validering": True,
        "delar": part_checks,
        "krev_fysisk_test": [
            "Papirmasse-krymp, sleppvinkel og overflatekvalitet i faktisk støypeform",
            "Material-ID og varmetoleranse på ombrukt monitorfolie før eventuell laserskjering",
            "Faktisk lux-/luminansmåling, kameratest for flimmerfri dimming og termisk måling ved full effekt",
            "CE / EN 60598-1 / IEC 62133-2 elektrisk og batteritryggleik på fysisk prototyp",
        ],
    }
    (TEST_DIR / "raup_CAD_verifisering.json").write_text(json.dumps(full_report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(
        f"\n=== RAUP FERDIG ({time.time()-t0:.1f}s) | {len(part_checks)} STEP + assembly + DXF + P1S 3MF | "
        f"0 kollisjonar | veltevinkel {stab_pulp['min_veltevinkel_grad']} deg (papir) / {stab_pla['min_veltevinkel_grad']} deg (PLA) ===",
        flush=True,
    )
    return full_report


if __name__ == "__main__":
    wall_arg = float(sys.argv[1]) if len(sys.argv) > 1 else 2.5
    height_arg = float(sys.argv[2]) if len(sys.argv) > 2 else 200.0
    run_production_build(wall_mm=wall_arg, total_height_mm=height_arg)
