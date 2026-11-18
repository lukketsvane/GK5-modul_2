import hashlib
import json
import math
import os
import struct
import traceback
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parent
MESH = ROOT / "mesh"
OUT = ROOT / "render_blender"
FAST = os.environ.get("E_FAST_RENDER", "").strip() == "1"
MM = 0.001
FACET = struct.Struct("<12fH")
NORMALS = struct.Struct("<9f")
TARGET = (0.0, 0.0, 0.110)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def verified_bytes(path, size, checksum):
    data = path.read_bytes()
    if len(data) != size or hashlib.sha256(data).hexdigest() != checksum:
        raise ValueError(f"Mesh cache mismatch; rerun the mesh exporter: {path}")
    return data


def load_mesh(key, record):
    count = record["facets"]
    data = verified_bytes(MESH / f"{key}.stl", record["bytes"], record["stl_sha256"])
    sidecar = verified_bytes(MESH / f"{key}.cnorm", count * NORMALS.size, record["normals_sha256"])
    if count < 4 or len(data) != 84 + FACET.size * count or struct.unpack_from("<I", data, 80)[0] != count:
        raise ValueError(f"Invalid binary STL: {key}")
    vertices, faces, corner_normals = [], [], []
    by_position = {}
    for facet, ns in zip(FACET.iter_unpack(memoryview(data)[84:]), NORMALS.iter_unpack(sidecar), strict=True):
        if ns[:3] == (0.0, 0.0, 0.0):
            continue
        face = []
        for start in (3, 6, 9):
            p = facet[start:start + 3]
            i = by_position.get(p)
            if i is None:
                i = by_position[p] = len(vertices)
                vertices.append((p[0] * MM, p[1] * MM, p[2] * MM))
            face.append(i)
        faces.append(face)
        corner_normals.extend((ns[:3], ns[3:6], ns[6:]))
    mesh = bpy.data.meshes.new(key)
    mesh.from_pydata(vertices, [], faces, shade_flat=False)
    mesh.update()
    if not faces or mesh.validate(verbose=False) or len(mesh.loops) != len(corner_normals):
        raise ValueError(f"Invalid Blender mesh: {key}")
    mesh.polygons.foreach_set("use_smooth", [True] * len(faces))
    mesh.set_sharp_from_angle(angle=math.radians(35.0))
    mesh.normals_split_custom_set(corner_normals)
    mesh.update()
    return mesh


def world_matrix(raw):
    if len(raw) in (12, 16) and not isinstance(raw[0], (list, tuple)):
        rows = [raw[i:i + 4] for i in range(0, len(raw), 4)]
    else:
        rows = raw
    if len(rows) == 4:
        if len(rows[3]) != 4 or any(abs(float(a) - b) > 1.0e-9 for a, b in zip(rows[3], (0, 0, 0, 1))):
            raise ValueError(f"Not an affine matrix: {raw}")
        rows = rows[:3]
    if len(rows) != 3 or any(len(row) != 4 for row in rows):
        raise ValueError(f"Expected a row-major 3x4 transform: {raw}")
    rows = [[float(v) for v in row] for row in rows]
    if not all(math.isfinite(v) for row in rows for v in row):
        raise ValueError("Nonfinite world transform")
    for row in rows:
        row[3] *= MM
    return Matrix(rows + [[0.0, 0.0, 0.0, 1.0]])


def linear(rgb):
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb[:3])


def material(name, rgb, metallic, roughness):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1.0)
    mat.use_nodes = True
    bs = mat.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (*rgb, 1.0)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = roughness
    return mat, bs


def warm_emission(mat, shader, strength):
    source = mat.node_tree.nodes.new("ShaderNodeBlackbody")
    source.inputs["Temperature"].default_value = 3000.0
    mat.node_tree.links.new(source.outputs["Color"], shader.inputs["Emission Color"])
    shader.inputs["Emission Strength"].default_value = strength


def dress(mesh, key, spec, palette):
    pigment = spec["color"]
    swatch = palette[pigment]
    color = linear(swatch)
    if spec["category"] == "foundation" and pigment == "stone":
        color = tuple(0.46 * a + 0.54 * b for a, b in zip(color, linear(palette["pearl"])))
    metal, rough = {
        "pearl": (0.0, 0.49),
        "stone": (0.025, 0.53),
        "nickel": (0.83, 0.38),
        "bronze": (0.62, 0.46),
        "dark": (0.52, 0.49),
        "opal": (0.0, 0.34),
        "silicone": (0.0, 0.57),
        "light": (0.0, 0.44),
    }[pigment]
    mat, bs = material(f"{key} | {pigment}", color, metal, rough)
    mesh.materials.append(mat)
    mat["CAD material"] = spec["material"]
    if pigment == "pearl":
        bs.inputs["Coat Weight"].default_value = 0.09
        bs.inputs["Coat Roughness"].default_value = 0.37
    elif pigment == "opal":
        bs.inputs["IOR"].default_value = 1.58
        bs.inputs["Transmission Weight"].default_value = 1.0 - swatch[3]
        bs.inputs["Subsurface Weight"].default_value = 0.24
        bs.inputs["Subsurface Scale"].default_value = 0.00065
        warm_emission(mat, bs, 2.2)
    elif pigment == "silicone":
        bs.inputs["Transmission Weight"].default_value = 1.0 - swatch[3]
    elif key == "cob_strip":
        emitting = mat.copy()
        emitting.name = "COB | downward emitting face"
        shader = emitting.node_tree.nodes["Principled BSDF"]
        warm_emission(emitting, shader, 9.0)
        mesh.materials.append(emitting)
        for face in mesh.polygons:
            if face.normal.z < -0.99:
                face.material_index = 1


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def new_object(collection, name, data):
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    return obj


STUDIO = (
    ((-0.42, 0.47, 0.72), 8.0, (1.0, 0.94, 0.86), 0.72, 0.50),
    ((0.51, 0.31, 0.43), 3.1, (0.89, 0.94, 1.0), 0.49, 0.41),
    ((0.03, -0.46, 0.60), 5.1, (1.0, 0.97, 0.91), 0.72, 0.21),
)
BLACK = (
    ((-0.15, 0.39, 0.62), 3.2, (1.0, 0.95, 0.89), 0.62, 0.44),
    ((0.48, -0.22, 0.37), 2.5, (0.85, 0.92, 1.0), 0.16, 0.46),
    ((-0.47, -0.18, 0.40), 2.8, (1.0, 0.87, 0.72), 0.19, 0.48),
)


def set_lighting(black, boxes, background, floor, floors):
    background.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1.0) if black else (0.66, 0.62, 0.57, 1.0)
    background.inputs["Strength"].default_value = 0.0 if black else 0.34
    floor.data.materials[0] = floors[int(black)]
    for obj, (xyz, watts, color, width, height) in zip(boxes, BLACK if black else STUDIO):
        obj.location = xyz
        aim(obj, TARGET)
        light = obj.data
        light.shape = "RECTANGLE"
        light.size = width
        light.size_y = height
        light.color = color
        light.energy = watts


def render_png(scene, name):
    path = OUT / name
    tmp = OUT / (path.stem + ".partial.png")
    tmp.unlink(missing_ok=True)
    try:
        scene.render.filepath = str(tmp)
        bpy.context.view_layer.update()
        result = bpy.ops.render.render(write_still=True)
        if "FINISHED" not in result or not tmp.is_file():
            raise IOError(f"Render did not finish: {name}")
        with tmp.open("rb") as stream:
            header = stream.read(24)
        if (
            len(header) != 24
            or header[:8] != b"\x89PNG\r\n\x1a\n"
            or header[12:16] != b"IHDR"
            or struct.unpack(">II", header[16:24]) != (scene.render.resolution_x, scene.render.resolution_y)
        ):
            raise IOError(f"Invalid rendered PNG: {name}")
        tmp.replace(path)
        scene.render.filepath = str(path)
    finally:
        tmp.unlink(missing_ok=True)
    return path.relative_to(ROOT).as_posix()


def main():
    if not bpy.app.background:
        raise RuntimeError("Run this renderer in Blender background mode")
    bom = read_json(ROOT / "components.json")
    index = read_json(MESH / "index.json")
    if bom.get("units", "mm") != "mm" or index["units"] != "mm":
        raise ValueError("Expected CAD coordinates in millimeters")
    palette = bom.get("rgba", index["rgba"])
    OUT.mkdir(exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 20 if FAST else 80
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = (960, 640) if FAST else (1536, 1024)
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "16"
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.exposure = 0.0

    product = bpy.data.collections.new("E | CAD instances")
    scene.collection.children.link(product)
    meshes, objects = {}, {}
    for name, instance in bom["instances"].items():
        key = instance["part"]
        if key not in meshes:
            mesh = load_mesh(key, index["parts"][key])
            dress(mesh, key, bom["parts"][key], palette)
            meshes[key] = mesh
        obj = new_object(product, name, meshes[key])
        obj["part_key"] = key
        obj["motion_group"] = instance["motion_group"]
        objects[name] = obj
    if not objects:
        raise ValueError("No CAD instances")

    bpy.ops.mesh.primitive_plane_add(size=50.0, location=(0.0, 0.0, -0.00001))
    floor = bpy.context.object
    floor.name = "Stage | tabletop"
    ivory, _ = material("Stage | matte taupe", linear((0.482, 0.454, 0.417)), 0.0, 0.85)
    black_mat, bs = material("Stage | matte black", (0.0014, 0.0014, 0.0014), 0.0, 0.73)
    bs.inputs["Specular IOR Level"].default_value = 0.075
    floors = (ivory, black_mat)
    floor.data.materials.append(ivory)

    world = bpy.data.worlds.new("Studio environment")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes["Background"]
    boxes = []
    for i in range(3):
        name = f"Studio | softbox {i + 1}"
        boxes.append(new_object(scene.collection, name, bpy.data.lights.new(name, "AREA")))
    camera = new_object(scene.collection, "Studio | camera", bpy.data.cameras.new("Product orthographic"))
    camera.data.type = "ORTHO"
    camera.data.lens = 65.0
    camera.data.sensor_fit = "HORIZONTAL"
    camera.data.clip_start = 0.005
    camera.data.clip_end = 100.0
    scene.camera = camera

    jobs = [("open", "studio"), ("open", "black")]
    if not FAST:
        jobs = [("closed", "studio"), ("middle", "studio")] + jobs + [("open", "side")]
    rendered = []
    blend = OUT / "open.blend"
    for pose, style in jobs:
        transforms = bom["poses"][pose]["transforms"]
        if transforms.keys() != objects.keys():
            raise ValueError(f"Pose {pose} does not contain exactly the authored instance set")
        for name, obj in objects.items():
            obj.matrix_world = world_matrix(transforms[name])
        side = style == "side"
        camera.location = (0.0, 0.85, 0.12) if side else (0.16, 0.75, 0.37)
        camera.data.ortho_scale = 0.55 if side else 0.535
        aim(camera, TARGET)
        set_lighting(style == "black", boxes, background, floor, floors)
        rendered.append(render_png(scene, f"{pose}_{style}.png"))
        if (pose, style) == ("open", "studio"):
            result = bpy.ops.wm.save_as_mainfile(filepath=str(blend), check_existing=False)
            if "FINISHED" not in result or not blend.is_file() or blend.stat().st_size == 0:
                raise IOError(f"Scene save failed: {blend}")
    print(json.dumps({
        "ok": True,
        "fast": FAST,
        "instances": len(objects),
        "rendered": rendered,
        "blend": blend.relative_to(ROOT).as_posix(),
    }, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        traceback.print_exc()
        print(json.dumps({"ok": False, "error": str(error)}, separators=(",", ":")), flush=True)
        raise SystemExit(1)
