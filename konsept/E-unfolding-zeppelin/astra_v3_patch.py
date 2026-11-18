import json
import os
import py_compile
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CAMERA = '    camera = new_object(scene.collection, "Studio | camera", bpy.data.cameras.new("Product perspective"))'
RESOLUTION = '    scene.render.resolution_x, scene.render.resolution_y = (960, 640) if FAST else (1536, 1024)'
BAR = '''    bar = bpy.data.lights.new("COB | 3200 K strip flux", "AREA")
    bar.shape = "RECTANGLE"
    bar.size, bar.size_y = 234.0 * MM, 5.0 * MM
    bar.color = (1.0, 0.516, 0.193)
    bar.energy = 3.0
    source = new_object(scene.collection, bar.name, bar)
    source.location = (0.0, -30.0 * MM, (156.9 + 0.05) * MM)
    source.rotation_euler = (math.pi, 0.0, 0.0)
'''

BUILD = (
    ("FRONT = YA + 9.0\nPOSES =", "FRONT = YA + 9.0\nHOOD_CROWN = 69.0\nPOSES ="),
    ("x = length_radius * (s - 0.21 * (1 - s*s))", "x = length_radius * (s - 0.21 * (1 - s*s))"),
    ("outer = hood_volume(220, 77.5, 40, 0)", "outer = hood_volume(220, 77.5, HOOD_CROWN, 0)"),
    ("cavity = hood_volume(218.5, 76, 38.5, 2.5)", "cavity = hood_volume(218.5, 76, HOOD_CROWN - 1.5, 2.5)"),
    ("origin=(124, 0, 4)).rect(13, 37).extrude(34)", "origin=(124, 0, 4)).rect(13, 37).extrude(HOOD_CROWN)"),
    ("    crowns = [bounds(hood.intersect(", '''    for key in ("roof_saddle", "roof_saddle_L"):
        check(distance(parts[key][0], hood) < 1e-5, key + " roof contact")
    crowns = [bounds(hood.intersect('''),
    ("box(x - 0.1, x + 0.1, -90, 90, -1, 42)", "box(x - 0.1, x + 0.1, -90, 90, -1, HOOD_CROWN + 1)"),
    ('("formed_hood", (440, 155, 40))', '("formed_hood", (440, 155, HOOD_CROWN))'),
    ("if envelope[2] > 240.1 or", "if envelope[2] > 270.1 or"),
    ("zip(envelope, (440, 160, 240))", "zip(envelope, (440, 160, 270))"),
    ('"design_box_mm": [440, 160, 240]', '"design_box_mm": [440, 160, 270]'),
)

RENDER = (
    ('source.inputs["Temperature"].default_value = 5100.0', 'source.inputs["Temperature"].default_value = 3200.0'),
    ('1.0 - swatch[3]\n        bs.inputs["Subsurface Weight"]', '0.42\n        bs.inputs["Subsurface Weight"]'),
    ("        warm_emission(mat, bs, 1.55)", '''        tree = mat.node_tree
        scatter = tree.nodes.new("ShaderNodeBsdfTranslucent")
        scatter.inputs["Color"].default_value = (*color, 1.0)
        mix = tree.nodes.new("ShaderNodeMixShader")
        mix.inputs[0].default_value = 0.45
        tree.links.new(bs.outputs["BSDF"], mix.inputs[1])
        tree.links.new(scatter.outputs["BSDF"], mix.inputs[2])
        tree.links.new(mix.outputs[0], tree.nodes["Material Output"].inputs["Surface"])'''),
    ("warm_emission(emitting, shader, 9.0)", "warm_emission(emitting, shader, 75.0)"),
    ('background.inputs["Strength"].default_value = 0.0 if black else 0.34',
     'background.inputs["Strength"].default_value = 0.0 if black else 0.46'),
    ('"Stage | matte taupe", linear((0.444, 0.417, 0.385))',
     '"Stage | matte taupe", tuple(1.35 * v for v in linear((0.444, 0.417, 0.385)))'),
    (CAMERA, BAR + CAMERA),
    (RESOLUTION, RESOLUTION),
)


def edited(raw, name, rules):
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    for before, after in rules:
        anchor = before.encode().replace(b"\n", newline)
        if raw.count(anchor) != 1:
            raise ValueError(f"{name}: expected one current-v2 anchor: {before!r}")
        raw = raw.replace(anchor, after.encode().replace(b"\n", newline), 1)
    return raw


def validate(stage):
    command = ('import json, sys; sys.path.insert(0, "."); import build; from pathlib import Path; '
               'Path("check.json").write_text(json.dumps(build.validate(), allow_nan=False), encoding="utf-8")')
    proc = subprocess.run([sys.executable, "-B", "-c", command], cwd=stage, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True, errors="replace")
    if proc.returncode:
        raise RuntimeError(f"build.validate exited {proc.returncode}: {proc.stdout[-3000:]}")
    report = json.loads((stage / "check.json").read_text(encoding="utf-8"))
    if not report["ok"] or report["failures"]:
        raise ValueError("build.validate: " + "; ".join(report["failures"]))
    parts, samples = report["parts"], report["samples"]
    if len(parts) != 23 or not all(p["valid_solid"] is True for p in parts.values()):
        raise ValueError("Expected 23 valid single-solid part types")
    if [s["t"] for s in samples] != [i / 8 for i in range(9)]:
        raise ValueError("Expected the nine sampled poses at t = 0/8 through 8/8")
    height = parts["formed_hood"]["size_mm"][2]
    if not (65.0 <= height <= 70.0 and abs(height - 69.0) < 0.2):
        raise ValueError(f"Measured hood height mismatch: {height} mm")
    top = max(s["enclosing_aabb_mm"][5] for s in samples)
    if not top <= 300.0:
        raise ValueError(f"Sampled assembly exceeds the physical ceiling: {top} mm")
    box = report["target_checks"]["sampled_swept_box"]
    return {"ok": True, "valid_part_types": len(parts), "sampled_poses": len(samples), "hood_height_mm": height,
            "occ_distance_calls": report["occ_distance_calls"], "sampled_swept_box": box, "max_sampled_z_mm": top,
            "depth_over_160_mm": round(max(0.0, box["conservative_size_mm"][1] - 160.0), 4),
            "blender_run": False, "next": "Run build.py and export_meshes.py before rendering in Blender."}


def main():
    specs = {"build.py": BUILD, "render_blender.py": RENDER}
    with tempfile.TemporaryDirectory(prefix=".astra-v3-", dir=ROOT) as folder:
        stage = Path(folder)
        for name, rules in specs.items():
            src, candidate, original = ROOT / name, stage / name, stage / (name + ".orig")
            shutil.copy2(src, original)
            backup = src.with_name(src.stem + "_before_v3.py")
            if not backup.exists():
                snapshot = stage / backup.name
                shutil.copy2(original, snapshot)
                try:
                    os.link(snapshot, backup)
                except FileExistsError:
                    pass
            candidate.write_bytes(edited(original.read_bytes(), name, rules))
            shutil.copymode(original, candidate)
            py_compile.compile(str(candidate), doraise=True)
        status = validate(stage)
        if any((ROOT / n).read_bytes() != (stage / (n + ".orig")).read_bytes() for n in specs):
            raise RuntimeError("Source changed during validation; nothing installed")
        try:
            for name in specs:
                os.replace(stage / name, ROOT / name)
        except BaseException:
            for name in reversed(tuple(specs)):
                if not (stage / name).exists():
                    os.replace(stage / (name + ".orig"), ROOT / name)
            raise
    return status


if __name__ == "__main__":
    try:
        result = main()
    except (Exception, KeyboardInterrupt) as exc:
        result = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    print(json.dumps(result, separators=(",", ":"), allow_nan=False), flush=True)
    raise SystemExit(0 if result["ok"] else 1)
