import json
import math
import os
import sys
import traceback
from array import array
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


MM = 0.001
SHAFT_DATUM_DEG = 38.0
CLOSED_FRAME = 1
OPEN_FRAME = 25
CAMERA_TARGET = (0.0, 0.0, 0.091)
LIGHT_TARGET = (0.0, 0.0, 0.101)


def set_if_available(owner, key, value):
    if owner is None or not hasattr(owner, key):
        return False
    try:
        setattr(owner, key, value)
    except (AttributeError, TypeError, ValueError, RuntimeError):
        return False
    return True


def finite_number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return float(value)


def make_collection(scene, name):
    collection = bpy.data.collections.new(name)
    scene.collection.children.link(collection)
    return collection


def configure_render(scene):
    try:
        scene.render.engine = "BLENDER_EEVEE"
    except (TypeError, ValueError):
        scene.render.engine = "BLENDER_EEVEE_NEXT"

    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"

    render = scene.render
    render.resolution_x = 1536
    render.resolution_y = 864
    render.resolution_percentage = 100
    render.pixel_aspect_x = 1.0
    render.pixel_aspect_y = 1.0
    render.use_border = False
    render.film_transparent = False
    render.use_file_extension = True
    render.image_settings.file_format = "PNG"
    render.image_settings.color_mode = "RGB"
    render.image_settings.color_depth = "8"
    render.image_settings.compression = 25

    scene.display_settings.display_device = "sRGB"
    if not set_if_available(scene.view_settings, "view_transform", "AgX"):
        scene.view_settings.view_transform = "Standard"
    set_if_available(scene.view_settings, "look", "None")
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0

    eevee = getattr(scene, "eevee", None)
    if not set_if_available(eevee, "taa_render_samples", 32):
        set_if_available(eevee, "render_samples", 32)
    for key, value in (
        ("use_shadows", True),
        ("shadow_ray_count", 4),
        ("shadow_step_count", 16),
        ("use_raytracing", True),
        ("use_fast_gi", True),
        ("fast_gi_method", "AMBIENT_OCCLUSION"),
        ("fast_gi_resolution", "2"),
        ("fast_gi_ray_count", 8),
        ("fast_gi_step_count", 16),
        ("fast_gi_quality", 1.0),
        ("fast_gi_distance", 0.035),
        ("fast_gi_thickness_near", 0.002),
        ("use_gtao", True),
        ("gtao_distance", 0.035),
        ("gtao_quality", 1.0),
    ):
        set_if_available(eevee, key, value)

    tracing = getattr(eevee, "ray_tracing_options", None)
    set_if_available(tracing, "resolution_scale", "2")
    set_if_available(tracing, "screen_trace_quality", 1.0)
    set_if_available(tracing, "screen_trace_thickness", 0.003)
    set_if_available(tracing, "trace_max_roughness", 0.5)

    world = bpy.data.worlds.new("Studio black")
    scene.world = world
    world.color = (0.0, 0.0, 0.0)
    set_if_available(world, "use_nodes", True)
    tree = world.node_tree
    tree.nodes.clear()
    bg = tree.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1.0)
    bg.inputs["Strength"].default_value = 0.0
    output = tree.nodes.new("ShaderNodeOutputWorld")
    output.location.x = 240
    tree.links.new(bg.outputs["Background"], output.inputs["Surface"])


def make_material(name, rgb, metallic, roughness, emission=None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1.0)
    set_if_available(mat, "use_nodes", True)
    tree = mat.node_tree
    tree.nodes.clear()
    surface = tree.nodes.new("ShaderNodeBsdfPrincipled")
    surface.inputs["Base Color"].default_value = (*rgb, 1.0)
    surface.inputs["Metallic"].default_value = metallic
    surface.inputs["Roughness"].default_value = roughness
    if emission is not None:
        color, strength = emission
        surface.inputs["Emission Color"].default_value = (*color, 1.0)
        surface.inputs["Emission Strength"].default_value = strength
    output = tree.nodes.new("ShaderNodeOutputMaterial")
    output.location.x = 320
    tree.links.new(surface.outputs["BSDF"], output.inputs["Surface"])
    return mat


def make_cad_mesh(key, record):
    v = record["v"]
    f = record["f"]
    if not v or len(v) % 3 or not f or len(f) % 3:
        raise ValueError(f"Model {key!r}: expected XYZ triples and indexed triangles")

    coords = array("f", (x * MM for x in v))
    if not all(map(math.isfinite, coords)):
        raise ValueError(f"Model {key!r}: non-finite mesh coordinate")
    indices = array("i", f)
    vertex_count = len(coords) // 3
    triangle_count = len(indices) // 3
    if min(indices) < 0 or max(indices) >= vertex_count:
        raise ValueError(f"Model {key!r}: triangle index out of range")

    mesh = bpy.data.meshes.new(key)
    mesh.vertices.add(vertex_count)
    mesh.loops.add(len(indices))
    mesh.polygons.add(triangle_count)
    mesh.vertices.foreach_set("co", coords)
    mesh.polygons.foreach_set("loop_start", array("i", range(0, len(indices), 3)))
    mesh.loops.foreach_set("vertex_index", indices)
    mesh.update(calc_edges=True)

    if hasattr(mesh, "set_sharp_from_angle"):
        mesh.shade_smooth()
        mesh.set_sharp_from_angle(angle=math.radians(30.0))
    else:
        for polygon in mesh.polygons:
            polygon.use_smooth = False
    mesh.update()
    mesh.use_fake_user = True
    return mesh


def import_cad(data, collection, materials):
    models = data["models"]
    parts = data["parts"]
    if not isinstance(models, dict) or not models or not isinstance(parts, list) or not parts:
        raise ValueError("Expected a nonempty models mapping and a nonempty parts list")

    meshes = {}
    for key in list(models):
        meshes[key] = make_cad_mesh(key, models.pop(key))

    objects = []
    moving = []
    for index, part in enumerate(parts):
        key = part["g"]
        mesh = meshes[key]
        mat = materials[part["color"]]
        motion = part["motion"]
        if motion not in {"fixed", "leaf", "gear", "rack"}:
            raise ValueError(f"Part {index}: unknown motion {motion!r}")
        if len(part["p"]) != 3:
            raise ValueError(f"Part {index}: expected three position coordinates")
        pos = tuple(finite_number(x, f"parts[{index}].p") * MM for x in part["p"])

        if len(mesh.materials) == 0:
            mesh.materials.append(mat)
        obj = bpy.data.objects.new(part["name"], mesh)
        collection.objects.link(obj)
        obj.material_slots[0].link = "OBJECT"
        obj.material_slots[0].material = mat
        obj.color = mat.diffuse_color
        obj.location = pos
        obj.rotation_mode = "XYZ"
        obj["cad_model"] = key
        obj["motion"] = motion
        objects.append(obj)
        if motion != "fixed":
            moving.append((obj, motion, pos[0]))

    return meshes, objects, moving


def set_up_poses(scene, moving, kinematics):
    closed = finite_number(kinematics["closed_deg"], "closed_deg")
    opened = finite_number(kinematics["open_deg"], "open_deg")
    radius = finite_number(kinematics["rack_pitch_radius_mm"], "rack_pitch_radius_mm") * MM

    scene.frame_start = CLOSED_FRAME
    scene.frame_end = OPEN_FRAME
    for frame, label, theta in ((CLOSED_FRAME, "Closed", closed), (OPEN_FRAME, "Open", opened)):
        scene.timeline_markers.new(label, frame=frame)
        scene.frame_set(frame)
        leaf_angle = math.radians(theta)
        gear_angle = math.radians(theta - SHAFT_DATUM_DEG)
        for obj, motion, base_x in moving:
            if motion == "rack":
                obj.location.x = base_x + radius * gear_angle
                obj.keyframe_insert(data_path="location", index=0, frame=frame)
            else:
                obj.rotation_euler.y = leaf_angle if motion == "leaf" else gear_angle
                obj.keyframe_insert(data_path="rotation_euler", index=1, frame=frame)
    scene.frame_set(CLOSED_FRAME)


def make_camera(collection, name, position):
    lens = bpy.data.cameras.new(name)
    lens.type = "ORTHO"
    lens.ortho_scale = 0.470
    lens.clip_start = 0.005
    lens.clip_end = 10.0
    lens.display_size = 0.045
    camera = bpy.data.objects.new(name, lens)
    collection.objects.link(camera)
    camera.location = position
    camera.rotation_euler = (Vector(CAMERA_TARGET) - camera.location).to_track_quat("-Z", "Y").to_euler()
    return camera


def fit_pose_pair(scene, cameras, objects):
    aspect = scene.render.resolution_x / scene.render.resolution_y
    for frame in (CLOSED_FRAME, OPEN_FRAME):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        for camera in cameras:
            view = camera.matrix_world.inverted()
            span = camera.data.ortho_scale
            for obj in objects:
                local_to_view = view @ obj.matrix_world
                for corner in obj.bound_box:
                    q = local_to_view @ Vector(corner)
                    span = max(span, 2.0 * abs(q.x) / 0.84, 2.0 * abs(q.y) * aspect / 0.84)
            camera.data.ortho_scale = span
    scene.frame_set(CLOSED_FRAME)


def make_softbox(collection, name, position, width, height, watts, rgb):
    light = bpy.data.lights.new(name, type="AREA")
    light.shape = "RECTANGLE"
    light.size = width
    light.size_y = height
    set_if_available(light, "normalize", True)
    light.energy = watts
    light.color = rgb
    set_if_available(light, "use_shadow", True)
    set_if_available(light, "use_shadow_jitter", True)

    obj = bpy.data.objects.new(name, light)
    collection.objects.link(obj)
    obj.location = position
    normal = (obj.location - Vector(LIGHT_TARGET)).normalized()
    long_axis = (Vector((1.0, 0.0, 0.0)) - normal * normal.x).normalized()
    short_axis = normal.cross(long_axis).normalized()
    obj.rotation_euler = Matrix((long_axis, short_axis, normal)).transposed().to_euler()


def main():
    root = Path(__file__).resolve().parent
    with (root / "scene.json").open("r", encoding="utf-8") as stream:
        data = json.load(stream)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "C_zeppelin"
    configure_render(scene)
    cad = make_collection(scene, "CAD parts")
    studio = make_collection(scene, "Studio lights")
    views = make_collection(scene, "Cameras")

    materials = {
        "matte": make_material("Satin silver aluminum", (0.39, 0.40, 0.41), 0.83, 0.30),
        "frame": make_material("Graphite frame", (0.022, 0.023, 0.025), 0.86, 0.23),
        "metal": make_material("Dark machined metal", (0.30, 0.31, 0.33), 0.80, 0.24),
        "light": make_material("Warm ivory strip", (0.91, 0.84, 0.71), 0.0, 0.52,
                               emission=((1.0, 0.78, 0.55), 3.4)),
    }
    meshes, objects, moving = import_cad(data, cad, materials)
    set_up_poses(scene, moving, data["kinematics"])

    cameras = {
        "3q": make_camera(views, "Three-quarter", (0.26, -0.98, 0.20)),
        "front": make_camera(views, "Front", (0.018, -1.10, 0.20)),
    }
    scene.camera = cameras["3q"]
    pass

    make_softbox(studio, "Overhead silk", (-0.035, -0.13, 0.57),
                 0.90, 0.35, 8.0, (1.0, 1.0, 1.0))
    make_softbox(studio, "Cool left rim", (-0.21, 0.15, 0.37),
                 0.62, 0.055, 6.0, (0.76, 0.86, 1.0))
    make_softbox(studio, "Front fill", (0.10, -0.43, 0.22),
                 0.45, 0.28, 2.0, (1.0, 0.98, 0.95))
    make_softbox(studio, "Warm lower bounce", (0.025, -0.075, -0.17),
                 0.52, 0.25, 8.0, (1.0, 0.71, 0.46))

    make_softbox(studio, "Pedestal soft fill", (0.02, -0.39, 0.045),
                 0.35, 0.30, 4.0, (1.0, 0.96, 0.90))
    output_dir = root / "renders"
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for view in ("3q", "front"):
        scene.camera = cameras[view]
        for pose, frame in (("closed", CLOSED_FRAME), ("open", OPEN_FRAME)):
            scene.frame_set(frame)
            path = output_dir / f"{pose}_{view}.png"
            scene.render.filepath = str(path)
            result = bpy.ops.render.render(write_still=True, scene=scene.name)
            if "FINISHED" not in result or not path.is_file() or path.stat().st_size == 0:
                raise RuntimeError(f"Render failed: {path}")
            outputs.append(path)

    if os.environ.get("C_RENDER_MOTION") == "1":
        scene.camera = cameras["3q"]
        for frame in range(CLOSED_FRAME, OPEN_FRAME + 1):
            scene.frame_set(frame)
            scene.render.filepath = str(output_dir / f"blender_frame_{frame:04d}.png")
            result = bpy.ops.render.render(write_still=True, scene=scene.name)
            if "FINISHED" not in result:
                raise RuntimeError("Animation frame render failed")
    scene.camera = cameras["3q"]
    scene.frame_set(CLOSED_FRAME)
    scene.render.filepath = "//renders/closed_3q.png"
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                space = area.spaces.active
                space.region_3d.view_perspective = "CAMERA"
                space.shading.color_type = "MATERIAL"

    blend_path = root / "C_zeppelin.blend"
    result = bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False, relative_remap=False)
    if "FINISHED" not in result or not blend_path.is_file() or blend_path.stat().st_size == 0:
        raise RuntimeError(f"Blend save failed: {blend_path}")

    print(f"Rendered {len(outputs)} PNGs from {len(objects)} CAD instances and {len(meshes)} model meshes.")
    for path in outputs:
        print(path)
    print(f"Saved editable scene: {blend_path}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        traceback.print_exc()
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(1)