import codecs
import importlib
import json
import math
import os
import stat
import sys
import tempfile
from pathlib import Path


def once(text, old, new):
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"Expected one source anchor, found {count}: {old.splitlines()[0]!r}")
    return text.replace(old, new, 1)


def patch_build(text):
    text = once(text, '''def leaf_blank():
    sections = []
    for s, f in stations(15, 0.041):
        x, w = 200 * s, 62.5 * f
        sag = 10 * f * f
        a = (x, -w, 124)
        b = (x, w, 124)
        c = (x, w, 122.5)
        d = (x, -w, 122.5)
        upper = cq.Edge.makeBezier([V(*a), V(x, 0, 124 - 2 * sag), V(*b)])
        lower = cq.Edge.makeBezier([V(*c), V(x, 0, 122.5 - 2 * sag), V(*d)])
        sections.append(cq.Wire.assembleEdges([upper, line(b, c), lower, line(d, a)]))
    return cq.Solid.makeLoft(sections, False)
''', '''def leaf_blank():
    sections = []
    for s, f in stations(21, 0.041):
        x, w = 200.0 * s, 62.5 * f
        span = max(0.0, 1.0 - s * s)
        lip_drop = 40.0 * span
        tilt = lip_drop * span * span / 3.0
        hollow = 8.0 * span
        poles = [
            (x, -w, 124.0),
            (x, -w / 3.0, 124.0 - hollow - tilt),
            (x, w / 3.0, 124.0 - hollow - 2.0 * tilt),
            (x, w, 124.0 - lip_drop),
        ]
        underside = [(px, py, pz - 1.5) for px, py, pz in poles]
        upper = cq.Edge.makeBezier([V(*p) for p in poles])
        lower = cq.Edge.makeBezier([V(*p) for p in reversed(underside)])
        sections.append(cq.Wire.assembleEdges([
            upper, line(poles[-1], underside[-1]), lower, line(underside[0], poles[0])
        ]))
    return cq.Solid.makeLoft(sections, False)
''')
    text = once(text,
        '    footprint = [(-210, -57.5), (210, -57.5), (210, 57.5), (185, 57.5), (185, -33), (-185, -33), (-185, 57.5), (-210, 57.5)]',
        '    footprint = [(-210, -57.5), (-185, -57.5), (-185, 32.5), (185, 32.5), (185, -57.5), (210, -57.5), (210, 57.5), (-210, 57.5)]')
    anchor = '    add("leaf_isolator", button, "silicone", "static_light", "compliant spool grommet, contoured to PC")'
    text = once(text, anchor, anchor + '\n    add("leaf_isolator_L", button.mirror("XZ"), *out["leaf_isolator"][1:])')
    text = once(text,
        '        grom = end("isolator", "leaf_isolator", flip)',
        '        grom = end("isolator", "leaf_isolator" if s > 0 else "leaf_isolator_L", flip)')
    text = once(text,
        '    for key in ("roof_saddle", "leaf_isolator", "gooseneck_cheek"):',
        '    for key in ("roof_saddle", "leaf_isolator", "leaf_isolator_L", "gooseneck_cheek"):')
    text = once(text, '("opal_leaf", (400, 125, 11.5))', '("opal_leaf", (400, 125, 41.5))')
    text = once(text, '"pearl": (0.865, 0.849, 0.791, 1.0)', '"pearl": (0.923, 0.902, 0.847, 1.0)')
    text = once(text, '"bronze": (0.515, 0.408, 0.319, 1.0)', '"bronze": (0.748, 0.709, 0.646, 1.0)')
    text = once(text, '"opal": (1.0, 0.921, 0.758, 0.83)', '"opal": (0.988, 0.976, 0.950, 0.92)')
    text = once(text, 'add("shoulder_M6", shoulder_screw(), "nickel",', 'add("shoulder_M6", shoulder_screw(), "bronze",')
    return text


def patch_render(text):
    text = once(text, 'TARGET = (0.0, 0.0, 0.105)', 'TARGET = (0.0, 0.0, 0.110)')
    text = once(text, '(0.0, 0.85, 0.12) if side else (0.55, 0.70, 0.33)', '(0.0, 0.85, 0.12) if side else (0.16, 0.75, 0.37)')
    text = once(text, 'camera.data.ortho_scale = 0.55 if side else 0.515', 'camera.data.ortho_scale = 0.55 if side else 0.535')
    text = once(text, '(1000, 720) if FAST else (1600, 1100)', '(960, 640) if FAST else (1536, 1024)')
    text = once(text, '"Stage | warm porcelain", linear((0.923, 0.905, 0.878)), 0.0, 0.76',
                      '"Stage | matte taupe", linear((0.482, 0.454, 0.417)), 0.0, 0.85')
    text = once(text, 'if black else (0.94, 0.91, 0.86, 1.0)', 'if black else (0.66, 0.62, 0.57, 1.0)')
    text = once(text, '0.0 if black else 0.50', '0.0 if black else 0.34')
    text = once(text, '"bronze": (0.76, 0.42)', '"bronze": (0.62, 0.46)')
    text = once(text, 'def dress(mesh, key, spec, palette):', '''def warm_emission(mat, shader, strength):
    source = mat.node_tree.nodes.new("ShaderNodeBlackbody")
    source.inputs["Temperature"].default_value = 3000.0
    mat.node_tree.links.new(source.outputs["Color"], shader.inputs["Emission Color"])
    shader.inputs["Emission Strength"].default_value = strength


def dress(mesh, key, spec, palette):''')
    text = once(text, '    warm = linear(palette["light"])\n', '')
    text = once(text, '''        bs.inputs["Emission Color"].default_value = (*warm, 1.0)
        bs.inputs["Emission Strength"].default_value = 0.95''', '        warm_emission(mat, bs, 2.2)')
    text = once(text, '''        shader.inputs["Emission Color"].default_value = (*warm, 1.0)
        shader.inputs["Emission Strength"].default_value = 9.0''', '        warm_emission(emitting, shader, 9.0)')
    return text


def prepare(path, transform):
    backup = path.with_name(path.stem + "_before_reference_match.py")
    current = path.read_bytes()
    original = backup.read_bytes() if backup.exists() else current
    source = original.decode("utf-8-sig")
    crlf = "\r\n" in source
    if crlf and "\n" in source.replace("\r\n", ""):
        raise ValueError(f"Mixed line endings in {path.name}")
    revised = transform(source.replace("\r\n", "\n"))
    data = (revised.replace("\n", "\r\n") if crlf else revised).encode("utf-8")
    if original.startswith(codecs.BOM_UTF8):
        data = codecs.BOM_UTF8 + data
    compile(data, str(path), "exec", dont_inherit=True)
    if current not in (original, data):
        raise RuntimeError(f"Refusing to discard edits in {path.name} relative to {backup.name}")
    return path, backup, current, original, data


def install(path, data):
    mode = stat.S_IMODE(path.stat().st_mode)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix="." + path.name + ".")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        os.chmod(name, mode)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def check_build(model):
    report = model.validate()
    if not report["ok"]:
        raise RuntimeError("Revised CAD validation: " + "; ".join(report["failures"]))
    parts = model.catalogue()
    leaf = parts["opal_leaf"][0]
    base = parts["plinth"][0]
    if not leaf.isInside(model.V(0, 62.0, 83.3)):
        raise AssertionError("Missing solid PC at the lowered forward lip")
    if not base.isInside(model.V(0, 45, 8)) or base.isInside(model.V(0, -45, 8)):
        raise AssertionError("Incorrect plinth opening direction")
    for hand in (-1, 1):
        for dy in (-5.6, 5.6):
            y = model.YA + dy
            if base.isInside(model.V(hand * 196, y, 10)) or not base.isInside(model.V(hand * 190, y, 10)):
                raise AssertionError("Missing post fixture bore or supporting rear arm")
    if not (model.L > 0 and 0 < model.ALPHA < math.pi / 2):
        raise AssertionError("Unexpected trim motion law")
    closed_trim = model.motion(0.0)[2]
    full_stroke_gap = closed_trim + model.bounds(parts["formed_hood"][0])[2] - model.bounds(leaf)[5]
    if full_stroke_gap < 11.98:
        raise AssertionError(f"Insufficient full-stroke hood/leaf vertical bound: {full_stroke_gap}")
    return {
        "sampled_assembly_poses": len(report["samples"]),
        "full_stroke_hood_leaf_vertical_bound_mm": round(full_stroke_gap, 3),
        "leaf_size_mm": report["target_checks"]["opal_leaf"]["measured_mm"],
    }


def main():
    root = Path.cwd().resolve()
    plans = [
        prepare(root / "build.py", patch_build),
        prepare(root / "render_blender.py", patch_render),
    ]
    for path, backup, current, original, data in plans:
        if not backup.exists():
            with backup.open("xb") as stream:
                stream.write(original)
    changed = []
    try:
        for path, backup, current, original, data in plans:
            if path.read_bytes() != current:
                raise RuntimeError(f"{path.name} changed during patch preparation")
            if current != data:
                install(path, data)
                changed.append((path, current))
        sys.path.insert(0, str(root))
        sys.dont_write_bytecode = True
        importlib.invalidate_caches()
        model = importlib.import_module("build")
        if Path(model.__file__).resolve() != root / "build.py":
            raise ImportError("Imported build is not the E project module")
        checks = check_build(model)
    except BaseException:
        for path, previous in reversed(changed):
            install(path, previous)
        raise
    print(json.dumps({
        "edited_files": [path.name for path, _ in changed],
        "expected": [
            "40 mm longitudinal front-lip drop on one formed PC solid; handed isolators on the original fixed mounts",
            "25 mm front joiner, rear support arms, original post bores and cable entry",
            "Unchanged hood solid and four-bar motion; matte ivory shell and pale satin hardware",
            "Front-dominant 65 mm orthographic setup, 3000 K emissive opal, taupe studio and retained black view",
        ],
        "cad_checks": checks,
        "next": "Regenerate CAD exports and the mesh cache before rendering. No render or production qualification performed.",
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
