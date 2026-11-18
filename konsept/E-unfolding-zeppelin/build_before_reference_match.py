import itertools
import json
import math
from functools import lru_cache
from pathlib import Path

import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape


V = cq.Vector
L = 45.0
ALPHA = math.asin(14.0 / L)
YA = -math.sqrt(L * L - 14.0 * 14.0)
FRONT = YA + 9.0
POSES = {"closed": 0.0, "middle": 0.5, "open": 1.0}
PALETTE = {
    "pearl": (0.865, 0.849, 0.791, 1.0),
    "stone": (0.665, 0.665, 0.630, 1.0),
    "bronze": (0.515, 0.408, 0.319, 1.0),
    "nickel": (0.609, 0.624, 0.618, 1.0),
    "dark": (0.279, 0.285, 0.279, 1.0),
    "opal": (1.0, 0.921, 0.758, 0.83),
    "light": (1.0, 0.849, 0.578, 1.0),
    "silicone": (0.826, 0.817, 0.769, 0.92),
}


def T(x=0.0, y=0.0, z=0.0):
    return cq.Location(V(x, y, z))


def R(axis, degrees):
    return cq.Location(V(0, 0, 0), V(*axis), float(degrees))


def rz(a):
    return R((0, 0, 1), a)


def rx(a):
    return R((1, 0, 0), a)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(p, axis, length, radius):
    return cq.Solid.makeCylinder(radius, length, V(*p), V(*axis))


def cx(x0, x1, y, z, r):
    return cyl((x0, y, z), (1, 0, 0), x1 - x0, r)


def cz(x, y, z0, z1, r):
    return cyl((x, y, z0), (0, 0, 1), z1 - z0, r)


def bore_between(p, q, r):
    a, b = V(*p), V(*q)
    d = b - a
    return cq.Solid.makeCylinder(r, d.Length, a, d.normalized())


def ring_x(x0, x1, y, z, ro, ri):
    return cx(x0, x1, y, z, ro).cut(cx(x0 - 1, x1 + 1, y, z, ri))


def plate_xz(points, y0, y1):
    return cq.Workplane("XZ", origin=(0, y1, 0)).polyline(points).close().extrude(y1 - y0).val()


def plate_xy(points, z0, z1):
    return cq.Workplane("XY", origin=(0, 0, z0)).polyline(points).close().extrude(z1 - z0).val()


def capsule_x(x0, x1, yz0, yz1, r):
    y0, z0 = yz0
    y1, z1 = yz1
    dy, dz = y1 - y0, z1 - z0
    plane = cq.Workplane("YZ", origin=(x0, (y0 + y1) / 2, (z0 + z1) / 2))
    return plane.slot2D(math.hypot(dy, dz) + 2 * r, 2 * r, math.degrees(math.atan2(dz, dy))).extrude(x1 - x0).val()


def single(shape, name):
    ss = shape.Solids()
    if len(ss) != 1:
        raise RuntimeError(f"{name}: expected one solid, found {len(ss)}")
    return ss[0]


def line(p, q):
    return cq.Edge.makeLine(V(*p), V(*q))


def stations(n, end_factor):
    limit = math.acos(end_factor)
    for i in range(n):
        a = limit * (2.0 * i / (n - 1) - 1.0)
        yield math.sin(a) / math.sin(limit), math.cos(a)


def hood_volume(length_radius, width_radius, height, below):
    sections = []
    for s, f in stations(15, 0.062):
        x, w, h = length_radius * s, width_radius * f, height * f
        arc = cq.Edge.makeEllipse(w, h, V(x, 0, 0), V(1, 0, 0), V(0, 1, 0), 0.0, 180.0)
        edges = [arc]
        if below:
            edges += [line((x, -w, 0), (x, -w, -below)), line((x, -w, -below), (x, w, -below)), line((x, w, -below), (x, w, 0))]
        else:
            edges.append(line((x, -w, 0), (x, w, 0)))
        sections.append(cq.Wire.assembleEdges(edges))
    return cq.Solid.makeLoft(sections, False)


def leaf_blank():
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


def cap_screw(stem_r, length, head_r, head_h, hex_af):
    body = cz(0, 0, -head_h, 0, head_r).fuse(cz(0, 0, 0, length, stem_r))
    tool = cq.Workplane("XY", origin=(0, 0, -head_h - 0.1)).polygon(6, hex_af / math.cos(math.pi / 6)).extrude(head_h * 0.60 + 0.1).val()
    return body.cut(tool).clean()


def shoulder_screw():
    thread = cx(-5.6, 0, 0, 0, 2.46)
    journal = cx(0, 6.0, 0, 0, 2.99)
    head = cx(6.0, 10, 0, 0, 4.95)
    tool = cq.Workplane("YZ", origin=(7.65, 0, 0)).polygon(6, 4 / math.cos(math.pi / 6)).extrude(3).val()
    return thread.fuse(journal, head).cut(tool).clean()


@lru_cache(maxsize=1)
def catalogue():
    out = {}

    def add(key, shape, palette, category, material):
        out[key] = (single(shape, key), palette, category, material)

    footprint = [(-210, -57.5), (210, -57.5), (210, 57.5), (185, 57.5), (185, -33), (-185, -33), (-185, 57.5), (-210, 57.5)]
    base = cq.Workplane("XY").polyline(footprint).close().extrude(16).edges("|Z").fillet(3.8).val()
    for hand in (-1, 1):
        for off in (-5.6, 5.6):
            x, y = hand * 196, YA + off
            base = base.cut(cz(x, y, -1, 17, 2.16), cz(x, y, -1, 3.1, 3.75))
    base = base.cut(cx(194, 211, YA, 8, 2.5), cz(196, YA, 7, 17, 2.5))
    add("plinth", base.clean(), "stone", "foundation", "powder-coated aluminium")

    post = plate_xz([(185.5, 16), (206, 16), (228, 127), (228, 171), (210, 171), (210, 129)], -9, 9)
    for z in (138, 160):
        post = post.cut(cx(221.5, 229, 0, z, 2.50))
    for y in (-5.6, 5.6):
        post = post.cut(cz(196, y, 15, 24.4, 1.99))
    post = post.cut(bore_between((195.80, 0, 15), (217.6, 0, 123.5), 2.45), cyl((217.5, -10, 123), (0, 1, 0), 20, 2.4))
    add("raked_post", post, "stone", "foundation", "machined aluminium; cross-drilled low-voltage chase")

    bridge = plate_xy([(153, -8), (166, -8), (211, FRONT + 4), (211, FRONT), (225, FRONT), (225, FRONT + 5), (180, 8), (153, 8)], 124.55, 127.5)
    bridge = bridge.cut(box(150, 166.05, -9, 9, 123, 126), cz(159, 0, 123, 128, 1.61), cz(175, 0, 123, 128, 1.49))
    add("tray_bridge_R", bridge, "nickel", "static_light", "3 mm aluminium, welded tab at post")
    add("tray_bridge_L", bridge.mirror("YZ"), "nickel", "static_light", "3 mm aluminium, welded tab at post")

    dish = leaf_blank()
    for x in (-175, 175):
        dish = dish.cut(cz(x, 0, 115, 126, 2.60))
    add("opal_leaf", dish, "opal", "diffuser", "formed milky PC, nominal 1.5 mm")
    button = cz(175, 0, 118.8, 124.55, 4.4).cut(dish, cz(175, 0, 118, 126, 1.59))
    add("leaf_isolator", button, "silicone", "static_light", "compliant spool grommet, contoured to PC")

    rail = box(-166, 166, -7.3, 7.3, 122.45, 126)
    rail = rail.cut(box(-167, 167, -5.55, 5.55, 121.5, 124.1))
    for x in (-159, 159):
        rail = rail.cut(cz(x, 0, 123, 127, 1.49))
    add("thermal_channel", rail, "nickel", "static_light", "fixed aluminium heat spreader")
    add("cob_strip", box(-152, 152, -5, 5, 122.85, 124.1), "light", "static_light", "downward-facing COB on thermally bonded MCPCB")

    outer = hood_volume(220, 77.5, 36, 0)
    cavity = hood_volume(218.5, 76, 34.5, 2.5)
    add("formed_hood", outer.cut(cavity).clean(), "pearl", "hood", "vacuum-formed opaque PETG, nominal 1.5 mm")
    saddle_stock = cq.Workplane("XY", origin=(124, 0, 4)).rect(13, 37).extrude(34).edges("|Z").fillet(2.3).val()
    saddle = saddle_stock.intersect(cavity).cut(cx(115, 133, 0, 10, 9.08))
    add("roof_saddle", saddle, "stone", "hood_structure", "printed PA saddle, bonded roof and tube lands")

    tube = ring_x(-160, 160, 0, 10, 9, 7.5)
    for x in (-155, 155):
        tube = tube.cut(cz(x, 0, -1, 4, 1.62), cz(x, 0, -2, 1.6, 2.95))
    add("carrier_18", tube, "nickel", "hood_structure", "18 x 1.5 aluminium round tube, nonrotating")
    cheek = capsule_x(222, 228, (0, -12), (0, 10), 7.45)
    horn = plate_xz([(160, 2.8), (163, 2.8), (179, -7), (226, -7), (226, -1), (179, -1), (163, 14), (160, 14)], -5.25, 5.25)
    shoe = cheek.fuse(horn, cx(160, 163, 0, 10, 8.9), cx(149, 160, 0, 10, 7.45))
    shoe = shoe.cut(cz(155, 0, 1.4, 10, 1.49))
    for z in (-12, 10):
        shoe = shoe.cut(cx(221.7, 229, 0, z, 2.50))
    add("gooseneck_cheek", shoe.clean(), "bronze", "hood_structure", "metal end plug, under-trim return and CD cheek")

    basic_arm = capsule_x(-2.5, 2.5, (0, 0), (45, 0), 7.3)
    journals = [cx(-3.5, 3.5, y, 0, 4.0) for y in (0, 45)]
    link = basic_arm.cut(*journals)
    add("follower_BD", link, "bronze", "mechanism", "5 mm stainless plate, bronze finish")
    tail = capsule_x(-2.5, 2.5, (-26, -25), (0, 0), 8.3)
    crank = basic_arm.fuse(tail).clean().cut(*journals, box(-3.5, 3.5, -30.56, -21.44, -29.56, -20.44))
    add("driving_AC", crank, "bronze", "mechanism", "ternary stainless crank, square drive at offset E")
    sync = box(-233.45, 233.45, -4.5, 4.5, -4.5, 4.5).cut(box(-235, 235, -3.25, 3.25, -3.25, 3.25))
    add("sync_cross_tube", sync, "dark", "mechanism", "9 mm square steel torque tube, indexed and welded into both AC tails")
    add("shoulder_M6", shoulder_screw(), "nickel", "pivot_hardware", "6 mm shoulder, simplified M5 threaded tip")
    add("journal_bush", ring_x(-2.5, 2.5, 0, 0, 4, 3.025), "bronze", "pivot_hardware", "sintered bronze sleeve")
    add("thrust_shim", ring_x(0, 0.5, 0, 0, 5.0, 3.055), "nickel", "pivot_hardware", "0.5 mm stainless thrust/retainer washer")
    for key, args in [("M4x20", (1.96, 20, 3.49, 2.85, 2.5)), ("M3x8", (1.46, 8, 2.74, 2.15, 2.0)), ("M3x6", (1.46, 6, 2.74, 2.15, 2.0))]:
        add(key, cap_screw(*args), "nickel", "fastener", "socket fastener; thread shown by smooth envelope")
    return out


def motion(t):
    t = float(t)
    if not 0 <= t <= 1:
        raise ValueError("pose parameter must be in [0, 1]")
    a = (2 * t - 1) * ALPHA
    return a, YA + L * math.cos(a), 150 + L * math.sin(a)


def layout(t):
    a, cy, trim = motion(t)
    swing = rx(math.degrees(a))
    lift = T(0, cy, trim)
    items = {}
    contacts = set()

    def put(name, part, loc, frame):
        items[name] = (part, loc, frame)
        return name

    def mate(name, *others):
        for other in others:
            contacts.add(tuple(sorted((name, other))))

    put("base", "plinth", T(), "ground")
    put("leaf", "opal_leaf", T(), "ground")
    put("rail", "thermal_channel", T(), "ground")
    put("pcb", "cob_strip", T(), "ground")
    mate("rail", "pcb")
    put("hood", "formed_hood", lift, "roof")
    put("carrier", "carrier_18", lift, "roof")
    put("coupler", "sync_cross_tube", T(0, YA, 138) * swing * T(0, -26, -25), "lower")
    for s, h in ((-1, "L"), (1, "R")):
        flip = rz(180) if s < 0 else T()

        def end(n, part, loc, frame="ground"):
            return put(h + "_" + n, part, loc, frame)

        post = end("post", "raked_post", T(0, YA, 0) * flip)
        bridge = end("bridge", "tray_bridge_" + h, T())
        mate(post, "base", bridge)
        mate(bridge, "rail")
        for idx, dy in enumerate((-5.6, 5.6)):
            screw = end("plinth_screw_" + str(idx), "M4x20", T(s * 196, YA + dy, 3.1))
            mate(screw, "base", post)
        grom = end("isolator", "leaf_isolator", flip)
        mate(grom, "leaf", bridge)
        bolt = end("leaf_screw", "M3x8", T(s * 175, 0, 118.8))
        mate(bolt, grom, bridge)
        bolt = end("rail_screw", "M3x6", T(s * 159, 0, 127.5) * rx(180))
        mate(bolt, "rail", bridge)
        saddle = end("saddle", "roof_saddle", lift * flip, "roof")
        shoe = end("cheek", "gooseneck_cheek", lift * flip, "roof")
        mate(saddle, "hood", "carrier")
        mate(shoe, "carrier")
        bolt = end("endcap_screw", "M3x6", lift * T(s * 155, 0, 1.6), "roof")
        mate(bolt, shoe, "carrier")
        low = end("AC", "driving_AC", T(s * 231, YA, 138) * swing, "lower")
        high = end("BD", "follower_BD", T(s * 231, YA, 160) * swing, "upper")
        mate(low, "coupler")
        for k, y, z, support, arm, frame in [
            ("A", YA, 138, post, low, "ground"),
            ("B", YA, 160, post, high, "ground"),
            ("C", cy, trim - 12, shoe, low, "roof"),
            ("D", cy, trim + 10, shoe, high, "roof"),
        ]:
            pin = end(k + "_pin", "shoulder_M6", T(s * 228, y, z) * flip, frame)
            bush = end(k + "_sleeve", "journal_bush", T(s * 231, y, z) * flip, frame)
            inner = end(k + "_thrust", "thrust_shim", T(s * 228, y, z) * flip, frame)
            outer = end(k + "_retainer", "thrust_shim", T(s * 233.5, y, z) * flip, frame)
            mate(pin, support, inner, outer, bush)
            mate(inner, support, bush, arm)
            mate(outer, arm, bush)
            mate(bush, arm)
    return items, contacts


def build_pose(t):
    parts = catalogue()
    items, _ = layout(t)
    result = []
    for name, (part, loc, _) in items.items():
        shape, pigment, category, _ = parts[part]
        result.append((name, shape.moved(loc), cq.Color(*PALETTE[pigment]), category))
    return result


def mat(loc):
    m = loc.wrapped.Transformation()
    return tuple(tuple(m.Value(i, j) for j in (1, 2, 3, 4)) for i in (1, 2, 3))


def compact_matrix(loc):
    return [round(n, 9) + 0.0 for row in mat(loc) for n in row]


def bounds(shape):
    b = shape.BoundingBox()
    return (b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax)


def mapped_bounds(bb, loc):
    rows = mat(loc)
    low, high = [], []
    for row in rows:
        a = b = row[3]
        for i in range(3):
            p, q = row[i] * bb[i], row[i] * bb[i + 3]
            a += min(p, q)
            b += max(p, q)
        low.append(a)
        high.append(b)
    return tuple(low + high)


def enclosing(all_bounds):
    return tuple((min if i < 3 else max)(b[i] for b in all_bounds) for i in range(6))


def separated(a, b):
    return any(a[k + 3] < b[k] - 1.0e-5 or b[k + 3] < a[k] - 1.0e-5 for k in range(3))


def dims(bb):
    return [round(bb[i + 3] - bb[i], 4) for i in range(3)]


def distance(a, b):
    alg = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    if not alg.IsDone():
        alg.Perform()
    if not alg.IsDone() or alg.NbSolution() < 1:
        raise RuntimeError("OCP minimum distance did not converge")
    return float(alg.Value())


def validate():
    parts = catalogue()
    bb = {}
    results = {}
    failures = []
    for key, (shape, _, _, _) in parts.items():
        b = bb[key] = bounds(shape)
        vol = shape.Volume()
        valid = bool(shape.isValid() and len(shape.Solids()) == 1 and vol > 1e-5)
        results[key] = {"valid_solid": valid, "volume_mm3": round(vol, 3), "size_mm": dims(b)}
        if not valid:
            failures.append("invalid part: " + key)
    samples = []
    same_frame_done = set()
    contact_errors = set()
    calls = 0
    all_envelopes = []
    masks = None
    for i in range(9):
        t = i / 8
        items, masks = layout(t)
        cache = {}

        def solid(name):
            if name not in cache:
                part, loc, _ = items[name]
                cache[name] = parts[part][0].moved(loc)
            return cache[name]

        boxes = {k: mapped_bounds(bb[p], loc) for k, (p, loc, _) in items.items()}
        near_tests = 0
        for k, j in itertools.combinations(sorted(items), 2):
            pair = (k, j)
            if pair == ("hood", "leaf") or pair in masks or pair in same_frame_done:
                continue
            if items[k][2] == items[j][2]:
                same_frame_done.add(pair)
            if separated(boxes[k], boxes[j]):
                continue
            d = distance(solid(k), solid(j))
            calls += 1
            near_tests += 1
            if d < 1e-5:
                contact_errors.add(f"{k}:{j}@{t:.3f}")
        hd = distance(solid("hood"), solid("leaf"))
        calls += 1
        gap = boxes["hood"][2] - boxes["leaf"][5]
        a, y, trim = motion(t)
        if hd < 1e-5 or gap < trim - 124 - 0.015:
            failures.append(f"diffuser clearance failed at {t}")
        env = enclosing(list(boxes.values()))
        all_envelopes.append(env)
        samples.append({"t": t, "theta_deg": round(math.degrees(a), 6), "hood_y_z": [round(y, 5), round(trim, 5)], "vertical_clearance_lower_bound_mm": round(gap, 5), "hood_to_leaf_occ_mm": round(hd, 5), "enclosing_aabb_mm": [round(x, 4) for x in env], "other_narrow_phase_tests": near_tests})
    failures.extend(sorted(contact_errors))
    targets = {}
    for key, nominal in (("plinth", (420, 115, 16)), ("opal_leaf", (400, 125, 11.5)), ("formed_hood", (440, 155, 36))):
        measured = dims(bb[key])
        ok = all(abs(x - y) < 0.2 for x, y in zip(measured, nominal))
        targets[key] = {"target_mm": nominal, "measured_mm": measured, "within_0.2mm": ok}
        if not ok:
            failures.append("target dimension: " + key)
    envelope = dims(enclosing(all_envelopes))
    env_ok = all(x <= y + 0.1 for x, y in zip(envelope, (482, 160, 200)))
    targets["sampled_swept_box"] = {"conservative_size_mm": envelope, "design_box_mm": [482, 160, 200], "within_box": env_ok}
    return {"ok": not failures, "units": "mm", "parts": results, "samples": samples, "target_checks": targets, "translation_closed_to_open_mm": [0, 0, 28], "maximum_intermediate_side_step_mm": round(YA + L, 6), "nominal_slot_closed_middle_open_mm": [12, 26, 40], "occ_distance_calls": calls, "named_mating_pairs_excluded": sorted(masks), "method": "Nine discrete configurations. Conservative transformed part AABBs, OCC solid distance for unresolved nonmating pairs and for hood/leaf at every sample. Rigid co-moving pairs need only one test. Envelope uses enclosing boxes, not oriented silhouettes.", "limitations": "Ideal unloaded geometry only; no continuous sweep, tolerance, guarding, life, electrical or thermal validation. External actuation required; no holding brake modeled.", "failures": failures}


def write_json(path, value):
    path.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False), encoding="utf-8")


def export_all(root):
    for folder in ("parts", "assemblies", "stl"):
        (root / folder).mkdir(exist_ok=True)
    parts = catalogue()
    report = validate()
    write_json(root / "validation.json", report)
    if not report["ok"]:
        raise RuntimeError("; ".join(report["failures"]))
    if not report["target_checks"]["sampled_swept_box"]["within_box"]:
        print("Warning: conservative sampled part boxes extend outside the nominal styling envelope.")
    bom = {
        "units": "mm",
        "origin": "tabletop at base centre; x longitudinal, +y forward, +z up",
        "transform_format": "row-major world-from-part 3x4 affine matrix, implicit final row 0 0 0 1",
        "rgba": PALETTE,
        "parts": {},
        "instances": {},
        "poses": {},
        "kinematics": {
            "fixed_A_B_x": [-231, 231],
            "fixed_A_B_y": YA,
            "A_B_heights": [138, 160],
            "AC_BD_length": 45,
            "CD_height": 22,
            "angle_law": "theta=(2*t-1)*asin(14/45); AC and BD rotate about +x from +y",
            "synchronization": "E is offset from A by (0,-26,-25) at theta=0. A keyed square torque tube between the two rotating E bosses makes the two lower cranks a single swinging bail. It clears the back of the posts. Upper 18 mm carrier is a separate nonrotating structure.",
            "assembly": "Bond saddle crowns to PETG and saddle bores to carrier in fixture. Slide cheek spigots into carrier and fit radial endcap screws. Index and weld both square crank sockets with axes aligned. Fit bushed pivots and shim stacks. Fixed end bridges are welded to the forward faces of the posts.",
            "light": "Static COB channel screwed to both bridges above the opal PC. Contoured isolators retain the diffuser independently. Base side entry and post chase provided for SELV supply; harness, connector and external driver not modeled.",
        },
    }
    for key, (shape, col, cat, material) in parts.items():
        path = root / "parts" / (key + ".step")
        cq.exporters.export(shape, str(path))
        bom["parts"][key] = {"file": "parts/" + path.name, "color": col, "category": cat, "material": material}
    for key in ("roof_saddle", "leaf_isolator", "gooseneck_cheek"):
        cq.exporters.export(parts[key][0], str(root / "stl" / (key + ".stl")), tolerance=0.075, angularTolerance=0.18)
    for label, t in POSES.items():
        asm = cq.Assembly(name="Northern_E_" + label)
        items, _ = layout(t)
        transforms = {}
        for name, (key, loc, frame) in items.items():
            shape, pigment, _, _ = parts[key]
            asm.add(shape, name=name, loc=loc, color=cq.Color(*PALETTE[pigment]))
            transforms[name] = compact_matrix(loc)
            bom["instances"][name] = {"part": key, "motion_group": frame}
        a, y, z = motion(t)
        bom["poses"][label] = {"t": t, "angle_deg": math.degrees(a), "hood_y": y, "trim_z": z, "transforms": transforms}
        asm.save(str(root / "assemblies" / (label + ".step")))
    write_json(root / "components.json", bom)
    return {"ok": True, "unique_parts": len(parts), "instances": len(bom["instances"]), "assemblies": list(POSES), "samples_checked": len(report["samples"]), "validation": "validation.json"}


if __name__ == "__main__":
    try:
        print(json.dumps(export_all(Path(__file__).resolve().parent), separators=(",", ":")))
    except Exception as error:
        print(json.dumps({"ok": False, "error": str(error)}, separators=(",", ":")))
        raise
