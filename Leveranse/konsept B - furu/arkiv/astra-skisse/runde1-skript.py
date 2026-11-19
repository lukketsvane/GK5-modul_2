import bpy
import bmesh
import math
import os
import sys
from bisect import bisect_right
from mathutils import Vector
from mathutils.bvhtree import BVHTree

PI = math.pi
TAU = 2.0 * PI
MM = 0.001
ZPIN = 155.0
CLOSED, OPENED = 35.0, 3.0
ALPHA = math.radians(CLOSED)
CA, SA, K = math.cos(ALPHA), math.sin(ALPHA), math.tan(ALPHA)
RAIL, EAR = 83.0, 75.5
JOINT = 30.0
CUTS = (-299.0, -213.0, -111.0, JOINT, 149.0, 231.0, 299.0)
EYES = (-271.0, -192.0, -90.0, 48.5, 170.0, 252.0)


def set_if(block, key, value):
    try:
        setattr(block, key, value)
        return True
    except (AttributeError, TypeError, ValueError, RuntimeError):
        return False


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def mix(a, b, t):
    return a + (b - a) * t


def bow(y):
    return -0.0077 * y * y


scene = bpy.context.scene
for lib in (bpy.data.objects, bpy.data.collections, bpy.data.meshes,
            bpy.data.curves, bpy.data.materials, bpy.data.lights,
            bpy.data.cameras, bpy.data.worlds):
    for item in list(lib):
        lib.remove(item, do_unlink=True)


def collection(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c


rig = collection("00 | Adjustment")
scales = collection("01 | Formed shells")
frame = collection("02 | Chassis")
fittings = collection("03 | Pivot fittings")
optics = collection("04 | Optics")
studio = collection("05 | Studio")

scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'MILLIMETERS'

ctrl = bpy.data.objects.new("LAMP_CTRL", None)
rig.objects.link(ctrl)
ctrl.empty_display_type = 'PLAIN_AXES'
ctrl.empty_display_size = 0.024
ctrl["open"] = 0.0
ctrl.id_properties_ui("open").update(
    min=0.0, max=1.0, soft_min=0.0, soft_max=1.0, default=0.0,
    description="Common aperture: 0 = nested, 1 = upright")
ctrl["construction"] = "Six individually pierced wraps; fixed twin rails; coaxial light cartridges."


def linear(v):
    v /= 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def socket(node, *names):
    for name in names:
        try:
            return node.inputs[name]
        except (KeyError, TypeError):
            pass
    return None


def value(node, names, v):
    s = socket(node, *names)
    if s is not None:
        try:
            s.default_value = v
        except (TypeError, ValueError, RuntimeError):
            pass


def material(name, rgb, rough, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1.0)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    value(p, ("Base Color",), (*rgb, 1.0))
    value(p, ("Roughness",), rough)
    value(p, ("Metallic",), metallic)
    return m, p


coat, pc = material("01 / Pebble • microtexture polyester",
                    tuple(linear(i) for i in (185, 182, 175)), 0.51)
nt = coat.node_tree
tex = nt.nodes.new("ShaderNodeTexCoord")
grain = nt.nodes.new("ShaderNodeTexNoise")
grain.inputs["Scale"].default_value = 13200.0
grain.inputs["Detail"].default_value = 2.0
nt.links.new(tex.outputs["Object"], grain.inputs["Vector"])
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.115
bump.inputs["Distance"].default_value = 0.000024
nt.links.new(grain.outputs["Fac"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], pc.inputs["Normal"])

steel, ps = material("02 / 316L • longitudinal satin", (0.69, 0.71, 0.73), 0.28, 1.0)
value(ps, ("Anisotropic IOR Level", "Anisotropic"), 0.57)
nt = steel.node_tree
uv = nt.nodes.new("ShaderNodeUVMap")
uv.uv_map = "Brush"
stretch = nt.nodes.new("ShaderNodeVectorMath")
stretch.operation = 'MULTIPLY'
stretch.inputs[1].default_value = (7.0, 510.0, 1.0)
nt.links.new(uv.outputs[0], stretch.inputs[0])
grain = nt.nodes.new("ShaderNodeTexNoise")
grain.inputs["Scale"].default_value = 1.0
grain.inputs["Detail"].default_value = 1.5
nt.links.new(stretch.outputs[0], grain.inputs["Vector"])
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (0.230, 0.230, 0.230, 1)
ramp.color_ramp.elements[1].color = (0.335, 0.335, 0.335, 1)
nt.links.new(grain.outputs["Fac"], ramp.inputs[0])
nt.links.new(ramp.outputs[0], ps.inputs["Roughness"])
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.07
bump.inputs["Distance"].default_value = 0.000009
nt.links.new(grain.outputs["Fac"], bump.inputs["Height"])
nt.links.new(bump.outputs[0], ps.inputs["Normal"])
try:
    tangent = nt.nodes.new("ShaderNodeTangent")
    tangent.direction_type = 'UV_MAP'
    tangent.uv_map = "Brush"
    nt.links.new(tangent.outputs[0], ps.inputs["Tangent"])
except (TypeError, KeyError, AttributeError, RuntimeError):
    pass

opal, pe = material("03 / Warm opal • 2700 K", (0.93, 0.89, 0.79), 0.34)
bb = opal.node_tree.nodes.new("ShaderNodeBlackbody")
bb.inputs[0].default_value = 2700.0
em = socket(pe, "Emission Color", "Emission")
if em is not None:
    opal.node_tree.links.new(bb.outputs[0], em)
value(pe, ("Emission Strength",), 12.0)
value(pe, ("Transmission Weight", "Transmission"), 0.09)

black, pf = material("04 / Black cyclorama", (0.00028, 0.00028, 0.00028), 0.97)
value(pf, ("Specular IOR Level", "Specular"), 0.008)


def mesh_object(name, points, faces, mat, coll, uv_func=None, shading=True):
    me = bpy.data.meshes.new(name + " | tool surface")
    me.from_pydata([(x * MM, y * MM, z * MM) for x, y, z in points], [], faces)
    bm = bmesh.new()
    bm.from_mesh(me)
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context='VERTS')
    if bm.faces:
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(me)
    bm.free()
    me.update()
    for p in me.polygons:
        p.use_smooth = shading
    if uv_func:
        layer = me.uv_layers.new(name="Brush")
        params = [uv_func(v.co) for v in me.vertices]
        for p in me.polygons:
            ids = list(p.loop_indices)
            coords = [params[me.loops[i].vertex_index] for i in ids]
            seam = max(v for u, v in coords) - min(v for u, v in coords) > 0.5
            for i, (u, v) in zip(ids, coords):
                layer.data[i].uv = (u, v + (1.0 if seam and v < 0.5 else 0.0))
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    me.materials.append(mat)
    return ob


def bevel(ob, width, seg=3, angle=30.0):
    b = ob.modifiers.new("Tool radius", 'BEVEL')
    b.width = width * MM
    b.segments = seg
    b.limit_method = 'ANGLE'
    b.angle_limit = math.radians(angle)
    set_if(b, "harden_normals", True)
    return b


def lathe(name, profile, pos, axis, mat, coll, n=96, yscale=1.0):
    pts, faces, rings = [], [], []
    for row in profile:
        z, r = row[:2]
        hexagon = len(row) == 3 and row[2]
        loop = []
        for j in range(n if r > 1e-8 else 1):
            a = TAU * j / n
            rr = r
            if hexagon:
                rr *= math.cos(PI / 6) / math.cos((a % (PI / 3)) - PI / 6)
            loop.append(len(pts))
            pts.append((rr * math.cos(a), yscale * rr * math.sin(a), z))
        rings.append(loop)
    for a, b in zip(rings, rings[1:]):
        for j in range(n):
            k = (j + 1) % n
            if len(a) == 1:
                faces.append((a[0], b[k], b[j]))
            elif len(b) == 1:
                faces.append((a[j], a[k], b[0]))
            else:
                faces.append((a[j], a[k], b[k], b[j]))
    lo = min(p[0] for p in profile) * MM
    dz = max(0.001, max(p[0] for p in profile) * MM - lo)

    def coords(v):
        return ((v.z - lo + 0.15 * math.hypot(v.x, v.y)) / dz,
                (math.atan2(v.y, v.x) / TAU) % 1.0)

    ob = mesh_object(name, pts, faces, mat, coll, coords if mat == steel else None)
    ob.location = Vector(pos) * MM
    if tuple(axis) != (0, 0, 1):
        ob.rotation_euler = Vector(axis).to_track_quat('Z', 'Y').to_euler()
    return ob


def bezier2(a, b, c, d, n):
    ans = []
    for i in range(1, n + 1):
        t, u = i / n, 1.0 - i / n
        ans.append(tuple(u**3 * a[j] + 3*u*u*t*b[j] + 3*u*t*t*c[j] + t**3*d[j]
                         for j in range(2)))
    return ans


base_profile = [(0.0, 0.0), (0.0, 93.7)]
for i in range(15):
    a = mix(-PI / 2, 0, i / 14)
    base_profile.append((2.55 + 2.55 * math.sin(a), 94.95 + 2.55 * math.cos(a)))
for i in range(15):
    a = PI * i / 28
    base_profile.append((8.15 + 2.85 * math.sin(a), 94.65 + 2.85 * math.cos(a)))
base_profile += [(11.0, 93.5), (11.0, 0.0)]
base = lathe("Base", base_profile, (0, 0, 0), (0, 0, 1), coat, frame, 192, 130 / 195)

p = [(10.90, 0), (10.90, 40.6), (10.92, 42.5)]
for b, c, d, n in [
    ((11.15, 40.4), (14.4, 35.5), (18.7, 33.6), 20),
    ((24.3, 31.1), (34.0, 28.5), (45.0, 28.5), 28),
    ((63.0, 28.5), (81.0, 33.9), (88.3, 38.4), 32),
    ((90.4, 39.7), (91.7, 40.5), (92.3, 40.5), 12),
    ((92.74, 40.5), (93.0, 40.2), (93.0, 39.8), 8)
]:
    p += bezier2(p[-1], b, c, d, n)
p += [(93.0, 38.9), (93.0, 0)]
stem = lathe("Stem", p, (0, 0, 0), (0, 0, 1), coat, frame, 144)

kn = Vector((0.202, -math.sqrt(1.0 - 0.202**2), 0))
kp = [( -0.65, 0), (-0.65, 4.1), (0.27, 4.1), (0.31, 4.56),
      (0.45, 4.86), (0.69, 5.0), (2.30, 5.0), (2.61, 4.94),
      (2.86, 4.73), (3.0, 4.32), (3.0, 3.95), (3.0, 0)]
knob = lathe("Dimmer_Knob", kp, (28.5*kn.x, 28.5*kn.y, 45), kn, coat, frame, 96)


def pchip(samples):
    xs, ys = zip(*samples)
    hs = [b - a for a, b in zip(xs, xs[1:])]
    ds = [(b - a) / h for a, b, h in zip(ys, ys[1:], hs)]

    def endpoint(h0, h1, s0, s1):
        m = ((2*h0 + h1)*s0 - h0*s1) / (h0 + h1)
        if m*s0 <= 0:
            return 0.0
        if s0*s1 < 0 and abs(m) > 3*abs(s0):
            return 3*s0
        return m

    ms = [endpoint(hs[0], hs[1], ds[0], ds[1])]
    for i in range(1, len(xs) - 1):
        a, b = ds[i-1:i+1]
        u, v = 2*hs[i] + hs[i-1], hs[i] + 2*hs[i-1]
        ms.append(0.0 if a*b <= 0 else (u+v)/(u/a + v/b))
    ms.append(endpoint(hs[-1], hs[-2], ds[-1], ds[-2]))
    coef = []
    for i, h in enumerate(hs):
        d = ys[i+1] - ys[i]
        m, n = ms[i]*h, ms[i+1]*h
        coef.append((ys[i], m, 3*d - 2*m - n, m+n - 2*d))

    def ev(x):
        i = min(len(hs)-1, max(0, bisect_right(xs, x)-1))
        t = (x - xs[i]) / hs[i]
        a, b, c, d = coef[i]
        return a + t*(b + t*(c + t*d))
    return ev


top = pchip([(-300, 0), (-270, 33), (-226, 65), (-167, 80), (-98, 95),
             (21, 105), (120, 83), (194, 63), (258, 37), (300, 0)])
bottom = pchip([(-300, 0), (-251, -36), (-137, -53), (-28, -58), (70, -51),
                (194, -36), (268, -11), (300, 0)])


def envelope(x):
    x = min(300.0, max(-300.0, x * 300.0 / 299.0))
    return top(x) * (104 / 105), bottom(x) * (57 / 58)


def side_y(x):
    a, b = envelope(x)
    return 0.9 * math.sqrt(max(0.0, -a*b))


def pin_x(t):
    l, r = -299.0, 299.0
    for _ in range(36):
        x = (l+r)*0.5
        if x - bow(side_y(x)) < t:
            l = x
        else:
            r = x
    return 0.5*(l+r)


PINS = [pin_x(t) for t in EYES]


# In the closed tooling coordinates t = x - tan(35°) h - bow(y).
# Unleaning increases adjacent t-separation by pitch * (cos(tilt)/cos(35°) - 1).
# The 1.1 mm laps have a 13.4 mm radial return; the fork has its own relieved seam.
def shell(i):
    px, tp = PINS[i], EYES[i]
    left = CUTS[i] + (6.7 if i == 3 else (-0.55 if i else 0.0))

    def right(a):
        if i == 2:
            return JOINT - 6.7 - 23.0*smooth((-math.cos(a)-0.38)/0.50)
        return CUTS[i+1] + (0.55 if i < 5 else 0.0)

    def surf(t, a):
        if t <= -299.0 or t >= 299.0:
            return (t, 0.0, 0.0)
        end = right(a)
        f = max(0.0, min(1.0, (t-left)/(end-left)))
        depth = ((3.4 if i == 2 else 13.4) *
                 (0.06*smooth(1.5*f) + 0.94*smooth((t-end+30)/24))
                 if i < 5 else 0.48 * math.sin(PI*f)**2)
        sn = math.sin(a)
        lo, hi = -299.0, 299.0
        for _ in range(27):
            x = (lo+hi)*0.5
            u, d = envelope(x)
            c, rad = (u+d)*0.5, (u-d)*0.5
            ang = a + math.asin(max(-0.999, min(0.999, c/max(rad, 1e-12))))*sn
            rr = rad - min(depth, 0.85*rad)
            h, y = c + rr*math.cos(ang), 0.9*rr*math.sin(ang)
            if x < t + K*h + bow(y):
                lo = x
            else:
                hi = x
        return (x, y, h)

    ta, tb = tp-8.8, tp+22.0

    def angle_at(t, h):
        lo, hi = 0.0, PI
        for _ in range(22):
            a = (lo+hi)*0.5
            if surf(t, a)[2] > h:
                lo = a
            else:
                hi = a
        return (lo+hi)*0.5

    test_t = [mix(ta, tb, j/4) for j in range(5)]
    wu = max(0.12, min(angle_at(t, 9.6) for t in test_t)-0.014)
    wd = min(PI-0.12, max(angle_at(t, -9.6) for t in test_t)+0.014)
    tu, td = angle_at(tb, 5.8), angle_at(tb, -5.8)
    half, marks = [0.0], []
    for end, fixed in ((wu, 0), (tu, 0), (td, 16), (wd, 0), (PI, 0)):
        start = half[-1]
        n = fixed or max(2, math.ceil((end-start)*176/TAU))
        half += [mix(start, end, j/n) for j in range(1, n+1)]
        marks.append(len(half)-1)
    angles = half + [TAU-a for a in reversed(half[1:-1])]
    n = len(angles)
    w0, e0, e1, w1 = marks[:4]
    windows = ((w0, w1), (n-w1, n-w0))

    stations = [(0, left)]

    def leg(a, b, spacing=2.65):
        m = max(1, math.ceil((b-a)/spacing))
        stations.extend((0, mix(a, b, j/m)) for j in range(1, m+1))

    if i == 0:
        stations.append((0, left+4.9))
    leg(stations[-1][1], ta)
    ia = len(stations)-1
    leg(ta, tb)
    ib = len(stations)-1
    if i == 5:
        leg(tb, 294.1)
        stations.append((0, 299.0))
    else:
        m = max(2, math.ceil((right(0)-tb)/2.65))
        stations.extend((1, j/m) for j in range(1, m+1))

    pts, faces, rows = [], [], []

    def add(v):
        pts.append(tuple(v))
        return len(pts)-1

    for mode, val in stations:
        if not mode and abs(val) == 299.0:
            rows.append([add((val, 0, 0))]*n)
        else:
            rows.append([add(surf(mix(tb, right(a), val) if mode else val, a))
                         for a in angles])
    for j in range(len(rows)-1):
        a, b = rows[j:j+2]
        for k in range(n):
            if ia <= j < ib and any(lo <= k < hi for lo, hi in windows):
                continue
            q = (k+1) % n
            f = tuple(dict.fromkeys((a[k], b[k], b[q], a[q])))
            if len(f) >= 3:
                faces.append(f)

    # Lanced, double-bent tongues share their root edges with the wrap itself.
    for sg, ids in ((1, range(e0, e1+1)), (-1, range(n-e1, n-e0+1))):
        root = sorted((rows[ib][j] for j in ids), key=lambda j: pts[j][2])
        paths = []
        for j, idx in enumerate(root):
            x0, y0, h0 = pts[idx]
            y0 *= sg
            dx, dy = x0-(px+6.5), EAR-y0
            r = min(4.1, 0.43*dx, 0.46*dy)
            pre = (dx-2*r)*0.5
            path = [(pre, 0.0)]
            for k in range(1, 11):
                a = PI*k/20
                path.append((pre+r*math.sin(a), r*(1-math.cos(a))))
            path.append((pre+r, dy-r))
            for k in range(1, 11):
                a = PI*k/20
                path.append((pre+r+r*(1-math.cos(a)), dy-r+r*math.sin(a)))
            path.append((dx, dy))
            h1 = mix(-5.55, 5.55, j/(len(root)-1))
            paths.append([idx] + [
                add((x0-u, sg*(y0+v), mix(h0, h1, smooth(k/len(path)))))
                for k, (u, v) in enumerate(path, 1)])
        for a, b in zip(paths, paths[1:]):
            faces.extend((a[k], a[k+1], b[k+1], b[k]) for k in range(len(a)-1))
        perimeter = [p[-1] for p in paths]
        for k in range(1, 7):
            perimeter.append(add((px+6.5*(1-k/6), sg*EAR, 5.55)))
        for k in range(1, 33):
            a = PI/2 + PI*k/32
            perimeter.append(add((px+5.55*math.cos(a), sg*EAR, 5.55*math.sin(a))))
        for k in range(1, 6):
            perimeter.append(add((px+6.5*k/6, sg*EAR, -5.55)))
        bore = []
        for j in perimeter:
            x, y, h = pts[j]
            f = 2.58/math.hypot(x-px, h)
            bore.append(add((px+(x-px)*f, y, h*f)))
        for j in range(len(bore)):
            k = (j+1) % len(bore)
            faces.append((perimeter[j], perimeter[k], bore[k], bore[j]))

    local = [(CA*(x-px)-SA*h, y, SA*(x-px)+CA*h) for x, y, h in pts]
    ob = mesh_object("Shell_" + str(i+1), local, faces, coat, scales)
    ob.location = (px*MM, 0, ZPIN*MM)
    ob.rotation_euler.y = ALPHA
    wall = ob.modifiers.new("Formed sheet / 2 mm", 'SOLIDIFY')
    wall.thickness = 2.0*MM
    wall.offset = 0.0
    wall.use_even_offset = False
    wall.use_rim = True
    bevel(ob, 0.32, 3, 34)
    drv = ob.driver_add("rotation_euler", 1).driver
    drv.type = 'SCRIPTED'
    var = drv.variables.new()
    var.name = "aperture"
    var.type = 'SINGLE_PROP'
    var.targets[0].id = ctrl
    var.targets[0].data_path = '["open"]'
    drv.expression = "%.16g - %.16g * aperture" % (ALPHA, ALPHA-math.radians(OPENED))
    return ob


shells = [shell(i) for i in range(6)]


def tube(label, sg):
    pts, faces = [], []
    xs, cuts = [-304.8], []
    n = 96
    for p in PINS:
        first = len(xs)
        xs.extend(p + mix(-3.4, 3.4, j/14) for j in range(15))
        cuts.append((first, first+14, p))
    xs.append(304.8)

    def add(x, y, h):
        pts.append((x, y, h))
        return len(pts)-1

    grids = []
    for radius in (5.0, 3.78):
        grid = [[add(x, radius*math.cos(TAU*k/n), radius*math.sin(TAU*k/n))
                 for k in range(n)] for x in xs]
        grids.append(grid)
        for j in range(len(xs)-1):
            punch = any(lo <= j < hi for lo, hi, p in cuts)
            for k in range(n):
                if punch and min((k+0.5) % (n/2), n/2-(k+0.5) % (n/2)) < n/8:
                    continue
                h = (k+1) % n
                faces.append((grid[j][k], grid[j+1][k], grid[j+1][h], grid[j][h]))

    for lo, hi, p in cuts:
        for center, sign in ((0, 1), (n//2, -1)):
            a, b = center-n//8, center+n//8
            outline = ([(j, a) for j in range(lo, hi)] +
                       [(hi, k) for k in range(a, b)] +
                       [(j, b) for j in range(hi, lo, -1)] +
                       [(lo, k) for k in range(b, a, -1)])
            ends = []
            for grid, radius in zip(grids, (5.0, 3.78)):
                start = [grid[j][k % n] for j, k in outline]
                prev = start
                for step in range(1, 5):
                    ring = []
                    for idx, (j, k) in zip(start, outline):
                        x, y, h = pts[idx]
                        ang = math.atan2(5.0*math.sin(TAU*k/n), xs[j]-p)
                        xx = mix(x, p+2.12*math.cos(ang), step/4)
                        hh = mix(h, 2.12*math.sin(ang), step/4)
                        ring.append(add(xx, sign*math.sqrt(max(0, radius**2-hh**2)), hh))
                    for j in range(len(prev)):
                        k = (j+1) % len(prev)
                        faces.append((prev[j], prev[k], ring[k], ring[j]))
                    prev = ring
                ends.append(prev)
            a0, a1 = ends
            for j in range(len(a0)):
                k = (j+1) % len(a0)
                faces.append((a0[j], a1[j], a1[k], a0[k]))
    for j in (0, -1):
        a, b = grids[0][j], grids[1][j]
        for k in range(n):
            h = (k+1) % n
            faces.append((a[k], b[k], b[h], a[h]))

    ob = mesh_object("Tube_"+label, pts, faces, steel, frame,
                     lambda v: (v.x/0.6096+0.5, (math.atan2(v.z, v.y)/TAU) % 1))
    ob.location = (0, sg*RAIL*MM, ZPIN*MM)
    bevel(ob, 0.095, 3, 31)
    return ob


tubes = [tube("Front", -1), tube("Back", 1)]


def make_yoke():
    plane, cells = [], []
    r, b, nr = 7.65, 2.8, 10
    arm = RAIL-math.sqrt(r*r-b*b)

    def add(y, h):
        plane.append((y, h))
        return len(plane)-1

    grid = []
    for j in range(113):
        y = mix(-arm, arm, j/112)
        t = smooth((abs(y)-6.0)/(arm-12.0))
        low = mix(-62.22, -b, t)
        high = mix(-56.85, b, t)
        grid.append([add(y, mix(low, high, k/nr)) for k in range(nr+1)])
    for a, z in zip(grid, grid[1:]):
        cells.extend((a[j], a[j+1], z[j+1], z[j]) for j in range(nr))

    for sg, end in ((-1, grid[0]), (1, grid[-1])):
        ids = list(end)
        beta = math.asin(b/r)
        for k in range(1, 88):
            ang = mix(PI-beta, -PI+beta, k/88)
            ids.append(add(sg*(RAIL+r*math.cos(ang)), r*math.sin(ang)))
        ins = []
        for j in ids:
            y, h = plane[j]
            dy = y-sg*RAIL
            f = 5.075/math.hypot(dy, h)
            ins.append(add(sg*RAIL+dy*f, h*f))
        for j in range(len(ids)):
            k = (j+1) % len(ids)
            cells.append((ids[j], ids[k], ins[k], ins[j]))

    pts, faces, counts = [], [], {}
    for sg in (-1, 1):
        for y, h in plane:
            f = smooth((abs(y)-71.0)/7.0)
            x = JOINT + mix(K*h+bow(y), bow(78.0), f)
            w = mix(4.05, 5.9, f)
            pts.append((x + sg*w/2, y, ZPIN+h))
    n = len(plane)
    for cell in cells:
        faces += [cell, tuple(j+n for j in reversed(cell))]
        for a, b0 in zip(cell, cell[1:]+cell[:1]):
            key = tuple(sorted((a, b0)))
            counts[key] = counts.get(key, 0)+1
    for (a, b0), count in counts.items():
        if count == 1:
            faces.append((a, a+n, b0+n, b0))
    ob = mesh_object("Yoke", pts, faces, coat, frame)
    bevel(ob, 0.44, 3, 27)
    return ob


yoke = make_yoke()
caps, pins, leds = [], [], []


def area(name, loc, aim, power, color, size, size_y=None, coll=studio):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = power
    data.color = color
    data.shape = 'RECTANGLE' if size_y is not None else 'DISK'
    data.size = size
    if size_y is not None:
        data.size_y = size_y
    ob = bpy.data.objects.new(name, data)
    coll.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(aim)-Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


for sg, side in ((-1, "Front"), (1, "Back")):
    for direction, end in ((-1, "L"), (1, "R")):
        profile = [(-2.15, 0), (-2.15, 3.60), (-2.0, 3.71),
                   (0.04, 3.71), (0.04, 4.74), (0.15, 4.92), (0.33, 4.99)]
        for j in range(1, 26):
            a = PI*j/50
            profile.append((0.33+2.87*math.sin(a), 4.99*math.cos(a)))
        caps.append(lathe("Cap_"+side+"_"+end, profile,
                          (direction*304.8, sg*RAIL, ZPIN), (direction, 0, 0),
                          steel, fittings, 96))

    for i, px in enumerate(PINS):
        ys = side_y(px)
        a = RAIL+5.0
        prof = [(ys-2.90, 0), (ys-2.90, 2.95), (ys-2.70, 3.08),
                (ys-2.25, 3.08), (ys-1.45, 2.70), (ys-0.92, 1.81),
                (a-0.18, 1.81), (a+0.025, 2.02), (a+0.04, 4.13),
                (a+0.15, 4.45), (a+0.38, 4.60), (a+0.73, 4.61),
                (a+1.08, 4.48), (a+1.53, 4.03), (a+1.96, 3.31),
                (a+2.28, 2.48), (a+2.47, 1.59), (a+2.49, 1.37, True),
                (a+2.35, 1.21, True), (a+1.45, 1.21, True),
                (a+1.37, 1.08, True), (a+1.37, 0)]
        label = str(i+1)+"_"+side
        pins.append(lathe("Pin_"+label, prof, (px, 0, ZPIN), (0, sg, 0),
                          steel, fittings, 72))

        # The light cartridge is a surface of revolution on the pin axis.
        # Its clearance to its own moving wrap is invariant, not just sampled.
        tip = ys-8.15
        prof = [(tip, 0)]
        for k in range(1, 16):
            ang = mix(-PI/2, 0, k/15)
            prof.append((tip+2.5+2.5*math.sin(ang), 3.0*math.cos(ang)))
        prof += [(ys-3.14, 3.0), (ys-2.90, 2.89), (ys-2.90, 0)]
        leds.append(lathe("LED_"+label, prof, (px, 0, ZPIN), (0, sg, 0),
                          opal, optics, 72))
        loc = (px*MM, sg*(tip-0.7)*MM, ZPIN*MM)
        aim = ((px+min(21, 0.34*ys))*MM, -sg*0.005, (ZPIN-0.72*ys)*MM)
        source = area("LED_Photometry_"+label, loc, aim,
                      0.075+0.33*(ys/69)**2, (1.0, 0.484, 0.196), 0.0042, coll=optics)
        if set_if(source.data, "temperature", 2700.0) and set_if(source.data, "use_temperature", True):
            source.data.color = (1, 1, 1)

floor = mesh_object("Floor", [(-8000, -8000, 0), (8000, -8000, 0),
                              (8000, 8000, 0), (-8000, 8000, 0)],
                    [(0, 1, 2, 3)], black, studio, shading=False)

world = bpy.data.worlds.new("Studio / black")
scene.world = world
world.use_nodes = True
world.color = (0, 0, 0)
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0, 0, 0, 1)
    bg.inputs["Strength"].default_value = 0.0

area("Key", (-0.46, -0.69, 0.84), (-0.04, 0, 0.125), 18.5,
     (1.0, 0.964, 0.915), 0.68, 0.53)
area("Fill", (0.51, -0.42, 0.39), (0.045, 0, 0.15), 4.0,
     (0.92, 0.954, 1.0), 0.49, 0.36)
area("Rim", (0.09, 0.43, 0.65), (0, 0, 0.163), 16.5,
     (1.0, 0.968, 0.917), 0.72, 0.22)

cd = bpy.data.cameras.new("Camera")
cam = bpy.data.objects.new("Camera", cd)
studio.objects.link(cam)
cd.lens = 100.0
cd.sensor_width = 36.0
cd.sensor_fit = 'HORIZONTAL'
cd.clip_start, cd.clip_end = 0.01, 50.0
pitch = math.radians(9.0)
target_z = 0.134
distance = 0.616/(0.79*0.36) + RAIL*MM*math.cos(pitch) + (ZPIN*MM-target_z)*math.sin(pitch)
cam.location = (0.0, -distance*math.cos(pitch), target_z+distance*math.sin(pitch))
cam.rotation_euler = (Vector((0, 0, target_z))-cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam

scene.render.engine = 'CYCLES'
set_if(scene.cycles, "device", 'CPU')
set_if(scene.cycles, "samples", 96)
set_if(scene.cycles, "use_denoising", True)
set_if(scene.cycles, "denoiser", 'OPENIMAGEDENOISE')
set_if(scene.cycles, "denoising_use_gpu", False)
set_if(scene.cycles, "max_bounces", 10)
scene.render.resolution_x = 1536
scene.render.resolution_y = 864
scene.render.resolution_percentage = 100
scene.render.pixel_aspect_x = scene.render.pixel_aspect_y = 1.0
scene.render.film_transparent = False
set_if(scene.view_settings, "view_transform", 'AgX')
for look in ("AgX - Medium High Contrast", "Medium High Contrast"):
    if set_if(scene.view_settings, "look", look):
        break
scene.render.filepath = "//Lamp"
for screen in bpy.data.screens:
    for ar in screen.areas:
        if ar.type == 'VIEW_3D':
            ar.spaces.active.region_3d.view_perspective = 'CAMERA'
            ar.spaces.active.overlay.show_overlays = False


def aperture(v, fr):
    ctrl["open"] = float(v)
    ctrl.update_tag()
    bpy.context.view_layer.update()
    scene.frame_set(fr)
    bpy.context.view_layer.update()


def evaluated_tree(ob, dg):
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    try:
        mw = ev.matrix_world
        pts = [mw @ v.co for v in me.vertices]
        me.calc_loop_triangles()
        tree = BVHTree.FromPolygons(pts, [tuple(t.vertices) for t in me.loop_triangles],
                                    all_triangles=True, epsilon=0.0)
        bounds = tuple((min(p[k] for p in pts), max(p[k] for p in pts)) for k in range(3))
        return tree, bounds
    finally:
        ev.to_mesh_clear()


fixed = tubes + pins + caps + [yoke, stem, base, knob] + leds
fixed_trees, bounds = {}, {}
for step, opening in enumerate((0.0, 0.25, 0.5, 0.75, 1.0)):
    aperture(opening, step+1)
    dg = bpy.context.evaluated_depsgraph_get()
    if not step:
        for ob in fixed:
            fixed_trees[ob], bounds[ob] = evaluated_tree(ob, dg)
    moving = {}
    for ob in shells:
        moving[ob], box = evaluated_tree(ob, dg)
        if not step:
            bounds[ob] = box
    hits = []
    for j, ob in enumerate(shells):
        for other in shells[j+1:]:
            if moving[ob].overlap(moving[other]):
                hits.append(ob.name+"/"+other.name)
        for other in fixed:
            if moving[ob].overlap(fixed_trees[other]):
                hits.append(ob.name+"/"+other.name)
    print("SELFTEST open=%.2f %s" % (opening, "COLLISION "+" ".join(hits) if hits else "OK"),
          flush=True)

aperture(0.0, 1)


def extent(obs, axis):
    return (max(bounds[o][axis][1] for o in obs)-min(bounds[o][axis][0] for o in obs))/MM


print("DIMS closed overall L %.2f mm  H %.2f mm" %
      (extent(fixed+shells, 0), extent(fixed+shells, 2)))
print("DIMS closed shells L %.2f mm  H %.2f mm  Z %.2f .. %.2f mm" %
      (extent(shells, 0), extent(shells, 2), min(bounds[o][2][0] for o in shells)/MM,
       max(bounds[o][2][1] for o in shells)/MM))
print("DIMS base %.2f x %.2f x %.2f mm" % tuple(extent([base], k) for k in range(3)))
print("DIMS shell pin X (mm): " + ", ".join("%.2f" % x for x in PINS))
print("DIMS tilt closed %.2f deg / open %.2f deg; pin line Z %.2f mm" % (CLOSED, OPENED, ZPIN))

if "--" in sys.argv:
    args = sys.argv[sys.argv.index("--")+1:]
    if args and args[0]:
        path = os.path.abspath(os.path.expanduser(args[0]))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=path)
