"""D03-retur med halv rygg: 6 mm bak pressflata i staden for 12 mm.

Klossen ber lite (handpressing av ein kort returvegg), så ryggen kan halverast.
Pressflata (offset -3,15 mm frå veggsenteret) er uendra. Kjeldegeometrien ligg i
Codex-mappa Raup-svart/Underkutt og Fotprove.
"""
import hashlib
import json
import sys
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh
from shapely.geometry import LineString

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\Iver\Documents\Codex\2026-11-20\lag-ti-nye-design-for-northern-3\Raup-svart")
sys.path.insert(0, str(SRC / "Underkutt"))
import fasade  # noqa: E402
from bygg import fiberskal  # noqa: E402
from formingskloss import check_contact  # noqa: E402

FACE, BACK = -3.15, -9.15  # var -3.15 / -15.15


def profile(z, stations):
    paths = []
    for offset in (FACE, BACK):
        curve = np.asarray([fasade.projected(u, z, offset) for u in stations])
        t = curve[[0, -1]] - curve[[1, -2]]
        ends = curve[[0, -1]] + 4 * t / np.linalg.norm(t, axis=1)[:, None]
        pts = np.vstack((ends[0], curve, ends[-1]))
        paths.append(cq.Edge.makeSpline([cq.Vector(x, y, z) for x, y in pts]))
    a, b = paths
    return cq.Wire.assembleEdges([a, cq.Edge.makeLine(a.endPoint(), b.endPoint()),
                                  b, cq.Edge.makeLine(b.startPoint(), a.startPoint())])


def main():
    scene = cq.Assembly.load(str(SRC / "Fotprove/Raup-tupp.step"))
    wall = {p.name: p.obj.moved(p.loc) for p in scene.children}["P02-Retur"]
    pts = wall.tessellate(.04, .10)[0]
    st = [p.x * fasade.U[0] + p.y * fasade.U[1] for p in pts]
    us = np.linspace(min(st), max(st), 140)
    b = wall.BoundingBox()
    die = fiberskal.indexed_loft([profile(z, us) for z in [b.zmin, 7, b.zmax, b.zmax + 3]], True)
    gaps = check_contact(LineString([fasade.projected(u, 7, -1.5) for u in us]), 1, wall, die)
    overlap = sum(abs(s.Volume()) for s in die.intersect(wall).Solids())
    assert overlap < .1 and die.isValid() and len(die.Solids()) == 1
    box = die.BoundingBox()
    die = die.translate((-box.xmin, -box.ymin, -box.zmin))
    path = ROOT / "former" / "D03-retur.stl"
    die.exportStl(str(path), tolerance=.025, angularTolerance=.08)
    mesh = trimesh.load_mesh(path)
    assert mesh.is_volume and len(mesh.split()) == 1
    rec = {"stl": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
           "rygg_mm": round(FACE - BACK, 2), "xyz_mm": np.round(mesh.extents, 2).tolist(),
           "volum_cm3": round(mesh.volume / 1000, 2), "kontaktprover": gaps, "overlapp_mm3": overlap}
    (ROOT / "former" / "D03-kontroll.json").write_text(json.dumps(rec, indent=2), encoding="utf8")
    print(json.dumps(rec))


if __name__ == "__main__":
    main()
