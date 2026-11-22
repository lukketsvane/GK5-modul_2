import hashlib
import json
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[2] / "Kvervel-R3/forms"
THICKNESS = 6
GUIDES = [(-98, -29), (107, -17), (0, 100)]


def planar_face(shape, z):
    return max(
        (f for f in shape.Faces() if abs(f.BoundingBox().zmin - z) < 1e-5
         and f.BoundingBox().zlen < 1e-5),
        key=lambda f: f.Area(),
    )


def circle_data(face):
    circles = []
    for wire in face.innerWires():
        edges = wire.Edges()
        if len(edges) == 1 and edges[0].geomType() == "CIRCLE":
            point = edges[0].arcCenter()
            circles.append((point.x, point.y, edges[0].radius()))
    return sorted(circles)


def main():
    source = SOURCE / "R3-pressformer.step"
    assembly = cq.Assembly.load(str(source))
    parts = {p.name: p.obj.moved(p.loc) for p in assembly.children}
    old, die = parts["D01-stempel"], parts["D02-matrise"]
    old_bottom = planar_face(old, -8)
    die_stop = planar_face(die, 0)
    perimeter = die_stop.outerWire()
    old_top = old.intersect(cq.Solid.makeBox(260, 200, 180, (-125, -60, 0)))
    holes = [w.translate((0, 0, 8)) for w in old_bottom.innerWires()]
    sole = cq.Solid.extrudeLinear(perimeter, holes, (0, 0, -THICKNESS))
    new = old_top.fuse(sole).clean()
    assert new.isValid() and len(new.Solids()) == 1
    bottom = planar_face(new, -THICKNESS)
    holes_measured = np.array(circle_data(bottom))
    assert np.allclose(holes_measured, sorted((x, y, 3.45) for x, y in GUIDES))
    assert np.allclose(np.array(circle_data(die_stop))[:, :2], holes_measured[:, :2])
    overlap = planar_face(new, 0).intersect(die_stop).Area()
    assert abs(overlap - die_stop.Area()) < 0.01
    old_plate_vol = old_bottom.Area() * 8
    removed = old_plate_vol - sole.Volume(0.0001)
    assert abs((old.Volume(0.0001) - new.Volume(0.0001)) - removed) < 0.2
    assert abs(sole.Volume() / THICKNESS - bottom.Area()) < 0.01
    assert abs(new.BoundingBox().zmax - old.BoundingBox().zmax) < 1e-5
    new.exportStep(str(HERE / "D01-R2.step"))
    placed = new.translate((0, 0, THICKNESS))
    stl = HERE / "D01-R2.stl"
    placed.exportStl(str(stl), tolerance=0.06, angularTolerance=0.10)
    mesh = trimesh.load_mesh(stl)
    assert mesh.is_volume and mesh.body_count == 1 and abs(mesh.bounds[0, 2]) < 1e-4
    report = {
        "source_step_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "stl_sha256": hashlib.sha256(stl.read_bytes()).hexdigest(),
        "old_sole_mm": 8,
        "new_sole_mm": THICKNESS,
        "old_contact_with_bed_mm2": round(old_bottom.Area(), 1),
        "new_contact_with_bed_mm2": round(bottom.Area(), 1),
        "sole_area_reduction_percent": round(100 * (1 - bottom.Area() / old_bottom.Area()), 1),
        "sole_volume_reduction_percent": round(100 * removed / old_plate_vol, 1),
        "d02_stop_area_mm2": round(die_stop.Area(), 2),
        "d02_supported_stop_area_mm2": round(overlap, 2),
        "guide_x_y_r_mm": holes_measured.round(3).tolist(),
        "print_dimensions_mm": mesh.extents.round(3).tolist(),
        "stl_single_watertight_solid": True,
    }
    (HERE / "Kontroll.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
