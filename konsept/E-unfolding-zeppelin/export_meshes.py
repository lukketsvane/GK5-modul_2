import hashlib
import json
import math
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import build
import cadquery as cq
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.TopLoc import TopLoc_Location
from OCP.gp import gp_Pnt, gp_Vec

MESH = ROOT / "mesh"
INDEX = MESH / "index.json"
LINEAR_MM = 0.22
ANGULAR_RAD = 0.09
XYZ = struct.Struct("<3f")
FACET = struct.Struct("<12fH")
NORMALS = struct.Struct("<9f")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def cad_corner_table(solid):
    table = {}
    for face in solid.Faces():
        location = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face.wrapped, location)
        if tri is None or not tri.NbTriangles():
            raise ValueError("Missing CAD face triangulation")
        transform = location.Transformation()
        surface = BRepAdaptor_Surface(face.wrapped)
        point, du, dv = gp_Pnt(), gp_Vec(), gp_Vec()
        has_uv = tri.HasUVNodes()
        nodes = [None]
        for i in range(1, tri.NbNodes() + 1):
            p = tri.Node(i).Transformed(transform)
            xyz = XYZ.unpack(XYZ.pack(p.X(), p.Y(), p.Z()))
            normal = None
            if has_uv:
                uv = tri.UVNode(i)
                surface.D1(uv.X(), uv.Y(), point, du, dv)
                v = du.Crossed(dv)
                length = v.Magnitude()
                if math.isfinite(length) and length > 1.0e-20:
                    normal = (v.X() / length, v.Y() / length, v.Z() / length)
            nodes.append((xyz, normal))
        for i in range(1, tri.NbTriangles() + 1):
            corners = [nodes[j] for j in tri.Triangle(i).Get()]
            table[tuple(sorted(p for p, n in corners))] = dict(corners)
    return table


def verify_and_write_normals(solid, stl, normals):
    data = stl.read_bytes()
    if len(data) < 84:
        raise ValueError(f"Missing STL header: {stl}")
    count = struct.unpack_from("<I", data, 80)[0]
    if count < 4 or len(data) != 84 + count * FACET.size:
        raise ValueError(f"Invalid binary STL length: {stl}")
    table = cad_corner_table(solid)
    volume6 = 0.0
    live = 0
    with normals.open("wb") as stream:
        for facet in FACET.iter_unpack(memoryview(data)[84:]):
            if not all(math.isfinite(v) for v in facet[:12]):
                raise ValueError(f"Nonfinite STL data: {stl}")
            a, b, c = facet[3:6], facet[6:9], facet[9:12]
            ux, uy, uz = (b[i] - a[i] for i in range(3))
            vx, vy, vz = (c[i] - a[i] for i in range(3))
            cross = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
            length = math.hypot(*cross)
            if length == 0.0:
                stream.write(bytes(NORMALS.size))
                continue
            live += 1
            volume6 += sum(x * y for x, y in zip(a, cross))
            flat = tuple(x / length for x in cross)
            corners = table.get(tuple(sorted((a, b, c))))
            if corners is None:
                raise ValueError(f"STL facet does not match CAD triangulation: {stl}")
            values = []
            for p in (a, b, c):
                n = corners[p] or flat
                sign = -1.0 if sum(x * y for x, y in zip(n, flat)) < 0.0 else 1.0
                values.extend(sign * x for x in n)
            stream.write(NORMALS.pack(*values))
    if live < 4 or not math.isfinite(volume6) or volume6 <= 0.0:
        raise ValueError(f"STL has no positive enclosed volume: {stl}")
    if normals.stat().st_size != count * NORMALS.size:
        raise IOError(f"Incomplete corner normals: {normals}")
    return count


def export_part(key, solid, stl, normals):
    if not solid.isValid() or len(solid.Solids()) != 1 or not solid.Volume() > 0.0:
        raise ValueError(f"Invalid catalogue solid: {key}")
    tmp = stl.with_suffix(".tmp.stl")
    ntmp = normals.with_suffix(".tmp.cnorm")
    try:
        tmp.unlink(missing_ok=True)
        ok = solid.exportStl(
            str(tmp),
            tolerance=LINEAR_MM,
            angularTolerance=ANGULAR_RAD,
            ascii=False,
            relative=False,
            parallel=False,
        )
        if ok is False:
            raise IOError(f"CadQuery STL export failed: {key}")
        count = verify_and_write_normals(solid, tmp, ntmp)
        record = {
            "bytes": tmp.stat().st_size,
            "facets": count,
            "stl_sha256": digest(tmp),
            "normals_sha256": digest(ntmp),
        }
        tmp.replace(stl)
        ntmp.replace(normals)
        return record
    finally:
        tmp.unlink(missing_ok=True)
        ntmp.unlink(missing_ok=True)


def main():
    MESH.mkdir(exist_ok=True)
    signature = hashlib.sha256(
        Path(build.__file__).read_bytes()
        + Path(__file__).read_bytes()
        + str(cq.__version__).encode()
    ).hexdigest()
    try:
        previous = json.loads(INDEX.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        previous = {}
    cache = previous.get("parts", {}) if previous.get("signature") == signature else {}
    records = {}
    exported = 0
    for key, (solid, pigment, category, material) in build.catalogue().items():
        stl = MESH / f"{key}.stl"
        normals = MESH / f"{key}.cnorm"
        old = cache.get(key)
        if (
            old
            and stl.is_file()
            and normals.is_file()
            and stl.stat().st_size == old["bytes"]
            and normals.stat().st_size == NORMALS.size * old["facets"]
            and digest(stl) == old["stl_sha256"]
            and digest(normals) == old["normals_sha256"]
        ):
            records[key] = old
        else:
            records[key] = export_part(key, solid, stl, normals)
            exported += 1
    if not records:
        raise ValueError("Empty CAD catalogue")
    index = {"signature": signature, "units": "mm", "rgba": build.PALETTE, "parts": records}
    tmp = INDEX.with_suffix(".tmp")
    tmp.write_text(json.dumps(index, separators=(",", ":"), allow_nan=False), encoding="utf-8")
    tmp.replace(INDEX)
    sizes = {f"mesh/{key}.stl": record["bytes"] for key, record in records.items()}
    print(json.dumps({"exported": exported, "cached": len(records) - exported, "mesh_bytes": sizes}, separators=(",", ":")))


if __name__ == "__main__":
    main()
