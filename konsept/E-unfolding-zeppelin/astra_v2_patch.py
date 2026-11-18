import ast
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = ("build.py", "render_blender.py")


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sub(text, old, new, count=1):
    n = text.count(old)
    require(n == count, f"Expected {count} occurrences, found {n}: {old!r}")
    return text.replace(old, new)


LEAF = '''def leaf_blank():
    sections = []
    for s, f in stations(21, 0.041):
        x, w = 165.0 * s, 62.5 * f
        span = max(0.0, 1.0 - s * s)
        land = -0.38 * w
        aft = [(-w, 160.0 - 3.0 * span), (-0.95 * w, 160.0), (-0.87 * w, 160.0)]
        face = [(land + (w - land) * i / 4, 160.0 - 50.0 * span * k)
                for i, k in enumerate((0.0, 0.0, 0.0, 0.56, 1.0))]
        runs = [aft, [aft[-1], face[0]], face]

        def edge(run, dz):
            points = [V(x, y, z + dz) for y, z in run]
            return cq.Edge.makeLine(*points) if len(points) == 2 else cq.Edge.makeBezier(points)

        edges = [edge(run, 0.0) for run in runs]
        for run, dz in ((face, -1.5),):
            y, z = run[-1]
            edges.append(line((x, y, z), (x, y, z + dz)))
        edges.extend(edge(run[::-1], -1.5) for run in reversed(runs))
        y, z = aft[0]
        edges.append(line((x, y, z - 1.5), (x, y, z)))
        sections.append(cq.Wire.assembleEdges(edges))
    return cq.Solid.makeLoft(sections, False)'''


CHECKS = '''def v2_checks(parts, bb, failures):
    def check(ok, message):
        if not ok:
            failures.append("v2: " + message)

    def close(a, b):
        return max(abs(u - v) for u, v in zip(a, b)) < 0.015

    hood, leaf = (parts[k][0] for k in ("formed_hood", "opal_leaf"))
    check(close((bb["formed_hood"][0], bb["formed_hood"][3]), (-220, 220)), "hood endpoints")
    ratio = dims(bb["plinth"])[0] / dims(bb["formed_hood"])[0]
    check(0.72 <= ratio <= 0.78, "base/hood physical width")
    check(close(bb["raked_post"], (151, -9, 16, 171, 9, 171)), "upright post stock")
    check(close(bb["opal_leaf"], (-165, -62.5, 108.5, 165, 62.5, 160)), "formed leaf extents")
    crowns = [bounds(hood.intersect(box(x - 0.1, x + 0.1, -90, 90, -1, 42)))[5] for x in (-180, 180)]
    check(crowns[0] > crowns[1] + 5, "fuller image-right crown section")
    for x in (-127, -64, 0, 64, 127):
        for z in (154, 157.8):
            check(distance(line((x, -26.4, z), (-205, 780, 300)), leaf) < 1e-5, "rail sightline")
    for i in range(9):
        t = i / 8
        items, _ = layout(t)
        _, cy, trim = motion(t)

        def point(key, v=(0, 0, 0)):
            return tuple(r[3] + sum(a*b for a, b in zip(r[:3], v)) for r in mat(items[key][1]))

        check(close(point("hood"), (0, cy, trim)), "roof translation")
        check(close(point("hood", (10, 13, 17)), (10, cy + 13, trim + 17)), "roof orientation")
        for s, side in ((-1, "L_"), (1, "R_")):
            for arm, ab, cd, z, dz in (("AC", "A", "C", 138, -48), ("BD", "B", "D", 160, -26)):
                a, c = point(side + arm), point(side + arm, (0, 45, 0))
                check(close(a, (s*174, YA, z)) and close(c, (s*174, cy, trim + dz)), "link registration")
                for p, label in ((a, ab), (c, cd)):
                    check(close(point(side + label + "_sleeve"), p), "journal axis")
                    check(close(point(side + label + "_pin", (3, 0, 0)), p), "shoulder axis")
    check(close((motion(1)[2] - motion(0)[2], motion(1)[1] - motion(0)[1]), (28, 0)), "endpoint travel")
    return {"base_to_hood_width": ratio, "crown_sections_z_mm_at_minus_plus_180": crowns,
            "rail_occlusion": "Ten sampled rays from the forward channel wall to the studio camera."}


'''


def patch_build(text):
    def r(a, b, n=1):
        nonlocal text
        text = sub(text, a, b, n)

    defs = [n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == "leaf_blank"]
    require(len(defs) == 1, "Missing or ambiguous leaf_blank")
    original = ast.get_source_segment(text, defs[0])
    require("200.0 * s, 62.5 * f" in original and "lip_drop = 40.0 * span" in original, "Unknown leaf revision")
    r(original, LEAF)
    r("for s, f in stations(15, 0.062):\n        x, w, h = length_radius * s, width_radius * f, height * f",
      "for s, f in stations(21, 0.035):\n        x = length_radius * (s - 0.21 * (1 - s*s))\n        fullness = f ** (1.0 + 0.25*s)\n        w, h = width_radius * fullness, height * fullness")
    r("[(-210, -57.5), (-185, -57.5), (-185, 32.5), (185, 32.5), (185, -57.5), (210, -57.5), (210, 57.5), (-210, 57.5)]",
      "[(-171.5, -57.5), (-146.5, -57.5), (-146.5, 32.5), (146.5, 32.5), (146.5, -57.5), (171.5, -57.5), (171.5, 57.5), (-171.5, 57.5)]")
    r("hand * 196", "hand * 161")
    r("cx(194, 211, YA, 8, 2.5), cz(196, YA, 7, 17, 2.5)", "cx(158, 173, YA, 8, 2.5), cz(159, YA, 7, 17, 2.5)")
    r("plate_xz([(185.5, 16), (206, 16), (228, 127), (228, 171), (210, 171), (210, 129)], -9, 9)",
      'cq.Workplane("XY", origin=(161, 0, 16)).rect(20, 18).extrude(155).edges("|Z").fillet(3.2).edges(">Z").fillet(2.3).val()')
    r("cx(221.5, 229, 0, z", "cx(164.5, 172, 0, z")
    r("cz(196, y, 15", "cz(161, y, 15")
    r("bore_between((195.80, 0, 15), (217.6, 0, 123.5), 2.45), cyl((217.5, -10, 123), (0, 1, 0), 20, 2.4)",
      "cz(159, 0, 15, 148.5, 2.45), cyl((159, 0, 147), (0, 1, 0), 10, 2.4)")
    r("[(153, -8), (166, -8), (211, FRONT + 4), (211, FRONT), (225, FRONT), (225, FRONT + 5), (180, 8), (153, 8)], 124.55, 127.5",
      "[(116, -34), (151, FRONT + 1), (155, FRONT), (170, FRONT), (170, FRONT + 5), (146, -17), (138, -17), (127, -25), (116, -25)], 151, 154")
    r("box(150, 166.05, -9, 9, 123, 126), cz(159, 0, 123, 128, 1.61), cz(175, 0, 123, 128, 1.49)",
      "cz(122, -30, 150, 155, 1.61), cz(143, -22, 150, 155, 1.49)")
    r("(-175, 175)", "(-143, 143)")
    r("cz(x, 0, 115, 126, 2.60)", "cz(x, -22, 153, 162, 2.60)")
    r("cz(175, 0, 118.8, 124.55, 4.4).cut(dish, cz(175, 0, 118, 126, 1.59))",
      "cz(143, -22, 154, 160.8, 4.4).cut(dish, cz(143, -22, 153, 162, 1.59))")
    r("box(-166, 166, -7.3, 7.3, 122.45, 126)", "box(-127, 127, -33.6, -26.4, 154, 157.8)")
    r("box(-167, 167, -5.55, 5.55, 121.5, 124.1)", "box(-128, 128, -32.7, -27.3, 155.7, 159)")
    r("(-159, 159)", "(-122, 122)")
    r("cz(x, 0, 123, 127, 1.49)", "cz(x, -30, 153, 159, 1.49)")
    r("box(-152, 152, -5, 5, 122.85, 124.1)", "box(-117, 117, -32.5, -27.5, 155.7, 156.9)")
    r("downward-facing COB", "upward-facing COB")
    r("220, 77.5, 36, 0", "220, 77.5, 40, 0")
    r("218.5, 76, 34.5, 2.5", "218.5, 76, 38.5, 2.5")
    r("    tube = ring_x(-160, 160", '''    left_saddle = saddle_stock.mirror("YZ").intersect(cavity).cut(cx(-133, -115, 0, 10, 9.08))
    add("roof_saddle_L", left_saddle, *out["roof_saddle"][1:])
    tube = ring_x(-144, 144''')
    r("(-155, 155)", "(-139, 139)")
    r("capsule_x(222, 228, (0, -12), (0, 10), 7.45)", "capsule_x(166, 171, (0, -48), (0, -26), 6.45)")
    r("[(160, 2.8), (163, 2.8), (179, -7), (226, -7), (226, -1), (179, -1), (163, 14), (160, 14)], -5.25, 5.25",
      "[(144, 4), (164, 4), (166, 2), (166, -32), (171, -32), (171, 6), (167, 12), (144, 12)], -4.5, 4.5")
    r("cx(160, 163, 0, 10, 8.9), cx(149, 160, 0, 10, 7.45)", "cx(144, 147, 0, 10, 8.9), cx(133, 144, 0, 10, 7.45)")
    r("cz(155, 0, 1.4", "cz(139, 0, 1.4")
    r("for z in (-12, 10):", "for z in (-48, -26):")
    r("cx(221.7, 229, 0, z", "cx(165, 172, 0, z")
    r("(45, 0), 7.3)", "(45, 0), 6.4)")
    r("-233.45, 233.45", "-176.45, 176.45")
    r("-235, 235", "-177, 177")
    r('sync, "dark"', 'sync, "stone"')
    r("cx(6.0, 10, 0, 0, 4.95)", "cx(6.0, 8.8, 0, 0, 4.7)")
    r("origin=(7.65, 0, 0)", "origin=(7.0, 0, 0)")
    r("150 + L * math.sin(a)", "186 + L * math.sin(a)")
    r("s * 196", "s * 161")
    r("T(s * 175, 0, 118.8)", "T(s * 143, -22, 160.8) * rx(180)")
    r("T(s * 159, 0, 127.5) * rx(180)", "T(s * 122, -30, 151)")
    r('"saddle", "roof_saddle", lift * flip', '"saddle", "roof_saddle" if s > 0 else "roof_saddle_L", lift')
    r("s * 155", "s * 139")
    r("s * 231", "s * 174", 3)
    r("s * 228", "s * 171", 2)
    r("s * 233.5", "s * 176.5")
    r("cy, trim - 12", "cy, trim - 48")
    r("cy, trim + 10", "cy, trim - 26")
    r("gap < trim - 124", "gap < trim - 160")
    r("(420, 115, 16)", "(343, 115, 16)")
    r("(400, 125, 41.5)", "(330, 125, 51.5)")
    r("(440, 155, 36)", "(440, 155, 40)")
    r("(482, 160, 200)", "(440, 160, 240)")
    r("[482, 160, 200]", "[440, 160, 240]")
    r('pair == ("hood", "leaf") or pair in masks or', 'pair == ("hood", "leaf") or')
    r("            d = distance(solid(k), solid(j))", '''            if pair in masks:
                common = solid(k).intersect(solid(j))
                if sum(s.Volume() for s in common.Solids()) > 0.001:
                    contact_errors.add(f"mating material overlap {k}:{j}@{t:.3f}")
                continue
            d = distance(solid(k), solid(j))''')
    r("def validate():", CHECKS + "def validate():")
    r("    env_ok = ", '''    targets["v2_geometry"] = v2_checks(parts, bb, failures)
    if envelope[2] > 240.1 or max(b[5] for b in all_envelopes) > 300:
        failures.append("sampled height limit")
    env_ok = ''')
    r("Rigid co-moving pairs need only one test.", "Named mates allow contact but not common solid volume above 0.001 mm3. Rigid co-moving pairs need only one test.")
    r('"fixed_A_B_x": [-231, 231]', '"fixed_A_B_x": [-174, 174],\n            "moving_C_D_z_from_trim": [-48, -26]')
    r("Static COB channel screwed to both bridges above the opal PC.", "Static upward COB channel on the bridges beneath the returned rear PC land.")
    r('("roof_saddle", "leaf_isolator",', '("roof_saddle", "roof_saddle_L", "leaf_isolator",')
    return text


def patch_render(text):
    for a, b in (
        ("3000.0", "5100.0"), ("warm_emission(mat, bs, 2.2)", "warm_emission(mat, bs, 1.55)"),
        ("COB | downward emitting face", "COB | upward emitting face"), ("face.normal.z < -0.99", "face.normal.z > 0.99"),
        ("0.66, 0.62, 0.57", "0.49, 0.46, 0.42"), ("0.482, 0.454, 0.417", "0.444, 0.417, 0.385"),
        ("0.0, 0.0, 0.110", "0.0, 0.0, 0.119"), ("Product orthographic", "Product perspective"),
        ('camera.data.type = "ORTHO"', 'camera.data.type = "PERSP"'), ("camera.data.lens = 65.0", "camera.data.lens = 55.0"),
        ("(0.16, 0.75, 0.37)", "(-0.205, 0.780, 0.300)"),
        ("        camera.data.ortho_scale = 0.55 if side else 0.535", '        camera.data.type = "ORTHO" if side else "PERSP"\n        camera.data.ortho_scale = 0.55'),
        ('    palette = bom.get', '''    if bom.get("kinematics", {}).get("fixed_A_B_x") != [-174, 174] or "roof_saddle_L" not in index["parts"]:
        raise ValueError("Stale v1 CAD or mesh cache: run build.py and export_meshes.py first")
    palette = bom.get'''),
    ):
        text = sub(text, a, b)
    return text


def verify():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("konsept_e_v2_local", ROOT / FILES[0])
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    parts = model.catalogue()
    report = model.validate()
    require(report["ok"], "; ".join(report["failures"]))
    require(len(report["samples"]) == 9 and report["occ_distance_calls"] >= 9, "Incomplete pose validation")
    for name, size in (("formed_hood", (440, 155, 40)), ("opal_leaf", (330, 125, 51.5)), ("plinth", (343, 115, 16))):
        measured = model.dims(model.bounds(parts[name][0]))
        require(max(abs(a-b) for a, b in zip(measured, size)) < 0.02, f"{name}: {measured}")
    return {"parts": len(parts), "samples": 9, "occ_distance_calls": report["occ_distance_calls"],
            "sampled_box": report["target_checks"]["sampled_swept_box"], "scope": report["limitations"]}


def read_regular(path):
    require(stat.S_ISREG(path.lstat().st_mode), f"Not a regular file: {path}")
    return path.read_bytes()


def publish(path, data, mode, exclusive=False):
    fd, tmp = tempfile.mkstemp(prefix=".astra-v2-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        os.chmod(tmp, mode)
        if exclusive:
            os.link(tmp, path)
        else:
            os.replace(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)


def main():
    git = ["git", "-C", str(ROOT)]
    require(subprocess.check_output(git + ["rev-parse", "--is-inside-work-tree"]).strip() == b"true", "Local Git worktree required")
    subprocess.run(git + ["ls-files", "--error-unmatch", "--", *FILES], stdout=subprocess.DEVNULL, check=True)
    paths = [ROOT / n for n in FILES]
    old, new, modes, backups, installed = {}, {}, {}, [], []
    for path, edit in zip(paths, (patch_build, patch_render)):
        raw = old[path] = read_regular(path)
        modes[path] = stat.S_IMODE(path.stat().st_mode)
        encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
        source = raw.decode(encoding)
        crlf = "\r\n" in source
        require(not crlf or "\n" not in source.replace("\r\n", ""), f"Mixed newlines: {path}")
        patched = edit(source.replace("\r\n", "\n"))
        new[path] = (patched.replace("\n", "\r\n") if crlf else patched).encode(encoding)
        compile(new[path], str(path), "exec", dont_inherit=True)
    for path in paths:
        backup = path.with_name(path.stem + "_before_v2.py")
        if not os.path.lexists(backup):
            publish(backup, old[path], modes[path], True)
        require(read_regular(backup) == old[path], f"Conflicting backup: {backup}")
        backups.append(backup.name)
    try:
        for path in paths:
            require(read_regular(path) == old[path], f"Concurrent edit: {path}")
            publish(path, new[path], modes[path])
            installed.append(path)
        run = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "--verify"],
                             cwd=ROOT, capture_output=True, text=True)
        require(run.returncode == 0, f"CAD check exited {run.returncode}: {(run.stdout + run.stderr)[-3000:]}")
        checked = json.loads(run.stdout.strip().splitlines()[-1])
        require(checked.get("ok") is True, "Missing successful CAD report")
        return dict(checked, backups=backups, regenerate_in_order=["build.py", "export_meshes.py", "blender -b -P render_blender.py"])
    except BaseException as error:
        problems = []
        for path in reversed(installed):
            try:
                require(read_regular(path) == new[path], f"Concurrent edit; refusing overwrite: {path}")
                publish(path, old[path], modes[path])
            except BaseException as rollback:
                problems.append(str(rollback))
        if problems:
            raise RuntimeError(f"{error}; rollback: {'; '.join(problems)}") from error
        raise


if __name__ == "__main__":
    try:
        require(sys.argv[1:] in ([], ["--verify"]), "Run astra_v2_patch.py without arguments")
        result = dict(ok=True, **verify()) if sys.argv[1:] else main()
        print(json.dumps(result, separators=(",", ":"), allow_nan=False), flush=True)
    except BaseException as exc:
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, separators=(",", ":")), flush=True)
        sys.exit(1)
