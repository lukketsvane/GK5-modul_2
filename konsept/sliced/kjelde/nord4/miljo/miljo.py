import argparse
import json
import math
import os
import random
import sys
import time

import bpy
import bmesh
from mathutils import Matrix, Vector, geometry

MM = 0.001
SKOT = ["miljo-dag", "miljo-kveld", "miljo-arbeid", "modus"]
KONTROLL = {}
CPU = {}
BILETE = {}
EV = {}


def argument():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    p = argparse.ArgumentParser(prog="miljo.py")
    p.add_argument("mappe")
    p.add_argument("--arbeid")
    p.add_argument("--ut")
    p.add_argument("--namn")
    p.add_argument("--skot", default=",".join(SKOT))
    p.add_argument("--rask", action="store_true")
    p.add_argument("--prover", type=int)
    p.add_argument("--breidd", type=int)
    p.add_argument("--kraft", type=float, default=1.0)
    p.add_argument("--blend", action="store_true")
    return p.parse_args(a)


def finn_ut(m):
    m = os.path.abspath(m)
    for d in (m, os.path.join(m, "ut")):
        if os.path.exists(os.path.join(d, "scene.json")) or os.path.exists(os.path.join(d, "delar.json")):
            return d
    raise SystemExit(f"finn korkje scene.json eller delar.json i {m} eller {m}/ut")


def les_design(m):
    d = finn_ut(m)
    sc = {}
    if os.path.exists(os.path.join(d, "scene.json")):
        sc = json.load(open(os.path.join(d, "scene.json")))
    delar = sc.get("deler") or sc.get("delar")
    if not delar:
        dj = json.load(open(os.path.join(d, "delar.json")))
        delar = dj["delar"]
        sc.setdefault("tjukn", dj.get("tjukn"))
    sc["delar"] = delar
    sc.setdefault("material", "bjork")
    sc["mappe"] = d
    return sc


def arbeid_mappe(m, gitt):
    if gitt:
        return gitt
    m = os.path.abspath(m).rstrip("/")
    if os.path.basename(m) == "ut":
        m = os.path.dirname(m)
    b = os.path.basename(m)
    if b.endswith("s"):
        s = os.path.join(os.path.dirname(m), b[:-1] + "a")
        if os.path.isdir(s):
            return s
    return None


def lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


class Stoff:
    def __init__(self, namn):
        self.m = bpy.data.materials.new(namn)
        self.t = self.m.node_tree
        self.t.nodes.clear()
        self.ut = self.t.nodes.new("ShaderNodeOutputMaterial")

    def n(self, kind, **kw):
        x = self.t.nodes.new(kind)
        for k, v in kw.items():
            if k in x.inputs:
                x.inputs[k].default_value = v
            else:
                setattr(x, k, v)
        return x

    def l(self, a, b):
        self.t.links.new(a, b)

    def principled(self, **kw):
        p = self.n("ShaderNodeBsdfPrincipled")
        for k, v in kw.items():
            p.inputs[k].default_value = v
        return p

    def ferdig(self, s):
        self.l(s.outputs[0] if hasattr(s, "outputs") else s, self.ut.inputs["Surface"])
        return self.m

    def koord(self, skala=1.0, slump=True):
        tc = self.n("ShaderNodeTexCoord")
        mp = self.n("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (skala, skala, skala)
        self.l(tc.outputs["Object"], mp.inputs["Vector"])
        if slump:
            oi = self.n("ShaderNodeObjectInfo")
            mul = self.n("ShaderNodeVectorMath", operation="MULTIPLY")
            mul.inputs[1].default_value = (517.3, 331.7, 91.1)
            cmb = self.n("ShaderNodeCombineXYZ")
            self.l(oi.outputs["Random"], cmb.inputs[0])
            self.l(oi.outputs["Random"], cmb.inputs[1])
            self.l(oi.outputs["Random"], cmb.inputs[2])
            self.l(cmb.outputs[0], mul.inputs[0])
            self.l(mul.outputs[0], mp.inputs["Location"])
        return mp.outputs[0]

    def bump(self, h, styrke, avstand=1.0):
        b = self.n("ShaderNodeBump", Strength=styrke, Distance=avstand)
        self.l(h, b.inputs["Height"])
        return b.outputs[0]

    def rampe(self, fac, a, b, p0=0.0, p1=1.0):
        r = self.n("ShaderNodeValToRGB")
        e = r.color_ramp.elements
        e[0].position, e[0].color = p0, (*a, 1)
        e[1].position, e[1].color = p1, (*b, 1)
        self.l(fac, r.inputs[0])
        return r.outputs[0]


def mat_tre(namn, lys, mork, ru, aarer, mm=True):
    s = Stoff(namn)
    k = s.koord(1.0 if mm else 1000.0)
    sep = s.n("ShaderNodeSeparateXYZ")
    s.l(k, sep.inputs[0])
    strekk = s.n("ShaderNodeCombineXYZ")
    mx = s.n("ShaderNodeMath", operation="MULTIPLY")
    mx.inputs[1].default_value = 0.04
    s.l(sep.outputs[0], mx.inputs[0])
    s.l(mx.outputs[0], strekk.inputs[0])
    s.l(sep.outputs[1], strekk.inputs[1])
    s.l(sep.outputs[2], strekk.inputs[2])
    fiber = s.n("ShaderNodeTexNoise", Scale=0.9, Detail=6.0, Roughness=0.6)
    s.l(strekk.outputs[0], fiber.inputs["Vector"])
    w = s.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction="Y", Scale=0.045, Distortion=6.0, Detail=3.0)
    w.inputs["Detail Scale"].default_value = 0.6
    s.l(k, w.inputs["Vector"])
    blend = s.n("ShaderNodeMix", data_type="FLOAT")
    blend.inputs["Factor"].default_value = 0.45
    s.l(w.outputs["Fac"], blend.inputs[2])
    s.l(fiber.outputs["Fac"], blend.inputs[3])
    fac = s.n("ShaderNodeMath", operation="POWER")
    fac.inputs[1].default_value = 1.6
    s.l(blend.outputs[0], fac.inputs[0])
    lerp = s.n("ShaderNodeMix", data_type="FLOAT")
    lerp.inputs["Factor"].default_value = aarer
    lerp.inputs[2].default_value = 0.35
    s.l(fac.outputs[0], lerp.inputs[3])
    farge = s.rampe(lerp.outputs[0], lys, mork, 0.15, 0.95)
    p = s.principled(Roughness=ru)
    p.inputs["Specular IOR Level"].default_value = 0.4
    s.l(farge, p.inputs["Base Color"])
    s.l(s.bump(fiber.outputs["Fac"], 0.08, 0.2 if mm else 0.0002), p.inputs["Normal"])
    return s.ferdig(p)


def mat_brent_kant(namn):
    s = Stoff(namn)
    k = s.koord()
    sep = s.n("ShaderNodeSeparateXYZ")
    s.l(k, sep.inputs[0])
    w = s.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction="Z", Scale=0.22, Distortion=1.5)
    s.l(k, w.inputs["Vector"])
    nz = s.n("ShaderNodeTexNoise", Scale=1.2, Detail=4.0)
    s.l(k, nz.inputs["Vector"])
    mix = s.n("ShaderNodeMix", data_type="FLOAT")
    mix.inputs["Factor"].default_value = 0.5
    s.l(w.outputs["Fac"], mix.inputs[2])
    s.l(nz.outputs["Fac"], mix.inputs[3])
    farge = s.rampe(mix.outputs[0], lin("#1d130c"), lin("#4a3220"), 0.2, 0.9)
    p = s.principled(Roughness=0.82)
    s.l(farge, p.inputs["Base Color"])
    s.l(s.bump(nz.outputs["Fac"], 0.25, 0.15), p.inputs["Normal"])
    return s.ferdig(p)


def mat_matt(namn, farge, ru=0.6, appelsin=True, mm=True):
    s = Stoff(namn)
    p = s.principled(**{"Base Color": (*farge, 1), "Roughness": ru})
    p.inputs["Specular IOR Level"].default_value = 0.45
    if appelsin:
        k = s.koord(1.0 if mm else 1000.0, False)
        nz = s.n("ShaderNodeTexNoise", Scale=1.6, Detail=2.0)
        s.l(k, nz.inputs["Vector"])
        s.l(s.bump(nz.outputs["Fac"], 0.05, 0.1 if mm else 0.0001), p.inputs["Normal"])
    return s.ferdig(p)


def mat_spegl(namn):
    s = Stoff(namn)
    p = s.principled(**{"Base Color": (0.93, 0.93, 0.94, 1), "Metallic": 1.0, "Roughness": 0.035})
    p.inputs["Coat Weight"].default_value = 0.6
    p.inputs["Coat Roughness"].default_value = 0.02
    p.inputs["Coat Tint"].default_value = (0.9, 0.97, 0.94, 1)
    return s.ferdig(p)


def mat_akrylkant(namn):
    s = Stoff(namn)
    p = s.principled(**{"Base Color": (*lin("#c3d5cb"), 1), "Roughness": 0.22})
    p.inputs["Transmission Weight"].default_value = 0.35
    return s.ferdig(p)


def mat_opal(namn, farge=(0.93, 0.91, 0.87), gjennom=0.6, ru=0.35):
    s = Stoff(namn)
    tr = s.n("ShaderNodeBsdfTranslucent")
    tr.inputs["Color"].default_value = (*farge, 1)
    p = s.principled(**{"Base Color": (*farge, 1), "Roughness": ru})
    mix = s.n("ShaderNodeMixShader")
    mix.inputs[0].default_value = gjennom
    s.l(p.outputs[0], mix.inputs[1])
    s.l(tr.outputs[0], mix.inputs[2])
    lp = s.n("ShaderNodeLightPath")
    tp = s.n("ShaderNodeBsdfTransparent")
    tp.inputs["Color"].default_value = (*(x * gjennom for x in farge), 1)
    skugge = s.n("ShaderNodeMixShader")
    s.l(lp.outputs["Is Shadow Ray"], skugge.inputs[0])
    s.l(mix.outputs[0], skugge.inputs[1])
    s.l(tp.outputs[0], skugge.inputs[2])
    return s.ferdig(skugge.outputs[0])


def mat_alu(namn, farge=(0.86, 0.87, 0.88), ru=0.3, aniso=0.75):
    s = Stoff(namn)
    p = s.principled(**{"Base Color": (*farge, 1), "Metallic": 1.0, "Roughness": ru})
    p.inputs["Anisotropic"].default_value = aniso
    tg = s.n("ShaderNodeTangent", direction_type="RADIAL", axis="Z")
    s.l(tg.outputs[0], p.inputs["Tangent"])
    k = s.koord(1.0, False)
    sep = s.n("ShaderNodeSeparateXYZ")
    s.l(k, sep.inputs[0])
    nz = s.n("ShaderNodeTexNoise", Scale=4.0, Detail=8.0)
    cmb = s.n("ShaderNodeCombineXYZ")
    for i in range(3):
        mul = s.n("ShaderNodeMath", operation="MULTIPLY")
        mul.inputs[1].default_value = 0.02 if i < 2 else 1.0
        s.l(sep.outputs[i], mul.inputs[0])
        s.l(mul.outputs[0], cmb.inputs[i])
    s.l(cmb.outputs[0], nz.inputs["Vector"])
    s.l(s.bump(nz.outputs["Fac"], 0.04, 0.05), p.inputs["Normal"])
    return s.ferdig(p)


def mat_tekstil(namn, farge=(0.016, 0.016, 0.018)):
    s = Stoff(namn)
    uv = s.n("ShaderNodeUVMap")
    w = s.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction="DIAGONAL", Scale=1.4)
    s.l(uv.outputs[0], w.inputs["Vector"])
    p = s.principled(**{"Base Color": (*farge, 1), "Roughness": 0.8})
    p.inputs["Sheen Weight"].default_value = 0.3
    p.inputs["Sheen Roughness"].default_value = 0.35
    p.inputs["Sheen Tint"].default_value = (0.5, 0.5, 0.52, 1)
    s.l(s.bump(w.outputs["Fac"], 0.5, 0.4), p.inputs["Normal"])
    return s.ferdig(p)


def blackbody(t):
    t = t / 100
    r = 255 if t <= 66 else 329.698727446 * (t - 60) ** -0.1332047592
    g = 99.4708025861 * math.log(t) - 161.1195681661 if t <= 66 else 288.1221695283 * (t - 60) ** -0.0755148492
    b = 255 if t >= 66 else (0 if t <= 19 else 138.5177312231 * math.log(t - 10) - 305.0447927307)
    c = [min(max(x, 0), 255) / 255 for x in (r, g, b)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def mat_lys(namn, styrke, kelvin=2700, berre_syn=False):
    s = Stoff(namn)
    bb = s.n("ShaderNodeBlackbody", Temperature=kelvin)
    e = s.n("ShaderNodeEmission", Strength=styrke)
    s.l(bb.outputs[0], e.inputs["Color"])
    if not berre_syn:
        tr = s.n("ShaderNodeBsdfTranslucent")
        tr.inputs["Color"].default_value = (0.9, 0.88, 0.84, 1)
        add = s.n("ShaderNodeAddShader")
        s.l(e.outputs[0], add.inputs[0])
        s.l(tr.outputs[0], add.inputs[1])
        m = s.ferdig(add.outputs[0])
    else:
        m = s.ferdig(e.outputs[0])
    m.cycles.emission_sampling = "FRONT"
    return m


class Stoffbok:
    def __init__(self):
        self.c = {}

    def __call__(self, nkl, lag):
        if nkl not in self.c:
            self.c[nkl] = lag()
        return self.c[nkl]


def ringar_reine(r):
    p = [tuple(map(float, q[:2])) for q in r]
    if len(p) > 2 and abs(p[0][0] - p[-1][0]) < 1e-6 and abs(p[0][1] - p[-1][1]) < 1e-6:
        p = p[:-1]
    ut = []
    for q in p:
        if not ut or abs(q[0] - ut[-1][0]) > 1e-6 or abs(q[1] - ut[-1][1]) > 1e-6:
            ut.append(q)
    if len(ut) > 2 and abs(ut[0][0] - ut[-1][0]) < 1e-6 and abs(ut[0][1] - ut[-1][1]) < 1e-6:
        ut.pop()
    return ut


def areal(r):
    return 0.5 * sum(r[i][0] * r[(i + 1) % len(r)][1] - r[(i + 1) % len(r)][0] * r[i][1] for i in range(len(r)))


def plate_mesh(namn, omriss, hol, t, k=0.0):
    ytre = ringar_reine(omriss)
    if areal(ytre) < 0:
        ytre.reverse()
    ringar = [ytre]
    for h in hol or []:
        h = ringar_reine(h)
        if len(h) < 3:
            continue
        if areal(h) > 0:
            h.reverse()
        ringar.append(h)
    alle = [q for r in ringar for q in r]
    n = len(alle)
    tris = geometry.tessellate_polygon([[Vector((u, v, 0)) for u, v in r] for r in ringar])
    verts = [(u, v, 0.0) for u, v in alle] + [(u, v, t) for u, v in alle]
    faces, mi = [], []
    for a, b, c in tris:
        pa, pb, pc = alle[a], alle[b], alle[c]
        z = (pb[0] - pa[0]) * (pc[1] - pa[1]) - (pb[1] - pa[1]) * (pc[0] - pa[0])
        if z < 0:
            b, c = c, b
        faces.append((a, c, b))
        mi.append(0)
        faces.append((a + n, b + n, c + n))
        mi.append(1)
    o = 0
    for r in ringar:
        m = len(r)
        for i in range(m):
            a, b = o + i, o + (i + 1) % m
            faces.append((a, b, b + n, a + n))
            mi.append(2)
        o += m
    me = bpy.data.meshes.new(namn)
    me.from_pydata(verts, [], faces)
    me.polygons.foreach_set("material_index", mi)
    me["flate"] = sum(abs((alle[b][0] - alle[a][0]) * (alle[c][1] - alle[a][1]) - (alle[b][1] - alle[a][1]) * (alle[c][0] - alle[a][0])) / 2 for a, b, c in tris)
    if k:
        bm = bmesh.new()
        bm.from_mesh(me)
        us = [v.co.x for v in bm.verts]
        u0, u1 = min(us), max(us)
        steg = max(2.0, min(6.0, 0.05 / abs(k)))
        u = math.floor(u0 / steg) * steg + steg
        while u < u1:
            g = bm.verts[:] + bm.edges[:] + bm.faces[:]
            bmesh.ops.bisect_plane(bm, geom=g, plane_co=(u, 0, 0), plane_no=(1, 0, 0))
            u += steg
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        h = t / 2
        for v in bm.verts:
            uu, vv, ww = v.co
            a = k * uu
            off = ww - h
            v.co = (math.sin(a) / k - off * math.sin(a), vv, h + (1 - math.cos(a)) / k + off * math.cos(a))
        bm.to_mesh(me)
        bm.free()
    me.validate()
    me.update()
    return me


def dreie(namn, profil, n=48, vinkel=35):
    verts, faces, ringar = [], [], []
    for r, z in profil:
        if r < 1e-7:
            ringar.append([len(verts)])
            verts.append((0.0, 0.0, z))
        else:
            ringar.append(list(range(len(verts), len(verts) + n)))
            verts += [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), z) for i in range(n)]
    for A, B in zip(ringar, ringar[1:]):
        if len(A) == 1 and len(B) == 1:
            continue
        if len(A) == 1:
            faces += [(A[0], B[(i + 1) % n], B[i]) for i in range(n)]
        elif len(B) == 1:
            faces += [(A[i], A[(i + 1) % n], B[0]) for i in range(n)]
        else:
            faces += [(A[i], A[(i + 1) % n], B[(i + 1) % n], B[i]) for i in range(n)]
    me = bpy.data.meshes.new(namn)
    me.from_pydata(verts, [], faces)
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(vinkel))
    me.update()
    return me


def sylinder_profil(d, L, fas=0.8):
    R = d / 2
    b = max(0.05, min(fas, R * 0.15, L * 0.15))
    return [(0, -L / 2), (R - b, -L / 2), (R - b * 0.3, -L / 2 + b * 0.3), (R, -L / 2 + b), (R, L / 2 - b), (R - b * 0.3, L / 2 - b * 0.3), (R - b, L / 2), (0, L / 2)]


def retta(senter, retning):
    r = Vector(retning or (0, 0, 1)).normalized()
    q = Vector((0, 0, 1)).rotation_difference(r)
    return Matrix.Translation(Vector(senter)) @ q.to_matrix().to_4x4()


def catmull(p, n_per_mm=0.25):
    p = [Vector(x) for x in p]
    if len(p) == 2:
        L = (p[1] - p[0]).length
        m = max(2, int(L * n_per_mm))
        return [p[0].lerp(p[1], i / m) for i in range(m + 1)]
    q = [p[0] + (p[0] - p[1])] + p + [p[-1] + (p[-1] - p[-2])]
    ut = []
    for i in range(1, len(q) - 2):
        P0, P1, P2, P3 = q[i - 1], q[i], q[i + 1], q[i + 2]
        t0 = 0.0
        t1 = t0 + max((P1 - P0).length ** 0.5, 1e-4)
        t2 = t1 + max((P2 - P1).length ** 0.5, 1e-4)
        t3 = t2 + max((P3 - P2).length ** 0.5, 1e-4)
        m = max(2, int((P2 - P1).length * n_per_mm))
        for j in range(m):
            t = t1 + (t2 - t1) * j / m
            A1 = P0 * ((t1 - t) / (t1 - t0)) + P1 * ((t - t0) / (t1 - t0))
            A2 = P1 * ((t2 - t) / (t2 - t1)) + P2 * ((t - t1) / (t2 - t1))
            A3 = P2 * ((t3 - t) / (t3 - t2)) + P3 * ((t - t2) / (t3 - t2))
            B1 = A1 * ((t2 - t) / (t2 - t0)) + A2 * ((t - t0) / (t2 - t0))
            B2 = A2 * ((t3 - t) / (t3 - t1)) + A3 * ((t - t1) / (t3 - t1))
            ut.append(B1 * ((t2 - t) / (t2 - t1)) + B2 * ((t - t1) / (t2 - t1)))
    ut.append(p[-1])
    return ut


def roer(namn, punkt, d, n=14):
    p = catmull(punkt)
    r = d / 2
    verts, faces, uvs = [], [], []
    tang = []
    for i in range(len(p)):
        a = p[min(i + 1, len(p) - 1)] - p[max(i - 1, 0)]
        tang.append(a.normalized() if a.length > 1e-9 else Vector((0, 0, 1)))
    ref = Vector((0, 0, 1)) if abs(tang[0].z) < 0.9 else Vector((1, 0, 0))
    nrm = tang[0].cross(ref).normalized()
    lengd = 0.0
    for i, c in enumerate(p):
        if i:
            lengd += (c - p[i - 1]).length
            ax = tang[i - 1].cross(tang[i])
            if ax.length > 1e-9:
                ang = tang[i - 1].angle(tang[i])
                nrm = Matrix.Rotation(ang, 3, ax.normalized()) @ nrm
        bi = tang[i].cross(nrm).normalized()
        nrm = bi.cross(tang[i]).normalized()
        for j in range(n):
            a = 2 * math.pi * j / n
            verts.append(c + (nrm * math.cos(a) + bi * math.sin(a)) * r)
            uvs.append((lengd / d, j / n))
    m = len(p)
    for i in range(m - 1):
        for j in range(n):
            faces.append((i * n + j, i * n + (j + 1) % n, (i + 1) * n + (j + 1) % n, (i + 1) * n + j))
    s0 = len(verts)
    verts.append(p[0])
    s1 = len(verts)
    verts.append(p[-1])
    uvs += [(0, 0), (0, 0)]
    for j in range(n):
        faces.append((s0, (j + 1) % n, j))
        faces.append((s1, (m - 1) * n + j, (m - 1) * n + (j + 1) % n))
    me = bpy.data.meshes.new(namn)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    uvl = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        for li in poly.loop_indices:
            uvl.data[li].uv = uvs[me.loops[li].vertex_index]
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(60))
    me.update()
    return me


def paere_mesh(namn, d, L):
    r = d / 2
    bR = min(13.5, r * 0.5)
    bL = min(26, L * 0.25)
    hals = L - r - bL
    a1 = math.radians(118)
    pkt = [(max(r * math.sin(a1 * i / 26), 0.0), -r * math.cos(a1 * i / 26)) for i in range(27)]
    p0 = pkt[-1]
    stig = -math.tan(a1)
    dy = hals - p0[1]
    for i in range(1, 15):
        s = i / 14
        h00 = 2 * s ** 3 - 3 * s ** 2 + 1
        h10 = s ** 3 - 2 * s ** 2 + s
        h01 = -2 * s ** 3 + 3 * s ** 2
        x = h00 * p0[0] + h10 * (dy / stig) * -1 * 0.9 + h01 * bR
        pkt.append((max(x, bR), p0[1] + dy * s))
    glas = dreie(namn + "-glas", pkt, 48, 80)
    sokkel = dreie(namn + "-sokkel", sylinder_profil(2 * bR, bL, 0.6), 32)
    return glas, sokkel, Matrix.Translation((0, 0, hals + bL / 2)), r


class Lampe:
    def __init__(self, sc, namn, sb, kraft=1.0):
        self.sc, self.namn, self.sb = sc, namn, sb
        self.obj, self.lys, self.leidningar = [], [], []
        self.pkt = []
        self.kraft = kraft
        self.paerer = 0
        self.plater, self.hol, self.flateavvik = 0, 0, 0.0
        self.bygg()
        KONTROLL.setdefault("plater", {"plater": self.plater, "hol": self.hol, "flateavvik_pst": round(self.flateavvik * 100, 4), "utstyr": len(sc.get("utstyr") or [])})

    def legg(self, me, mats, M, struktur=True):
        o = bpy.data.objects.new(me.name, me)
        bpy.context.scene.collection.objects.link(o)
        for m in mats:
            me.materials.append(m)
        o.matrix_world = M
        self.obj.append((o, M))
        if struktur:
            ws = [M @ v.co for v in me.vertices]
            stride = max(1, len(ws) // 400)
            self.pkt += ws[::stride]
            for i in range(3):
                self.pkt += [min(ws, key=lambda w: w[i]), max(ws, key=lambda w: w[i])]
        return o

    def plate_stoff(self, d):
        sc = self.sc
        namn = d.get("material") or sc.get("material") or "bjork"
        farge = d.get("farge")
        sb = self.sb
        kant_tre = sb("brent", lambda: mat_brent_kant("brent-kant"))
        if namn == "spegl":
            matt = sb(("matt", farge or "#8a8d8f"), lambda: mat_matt("spegl-bak", lin(farge or "#8a8d8f"), 0.55))
            sp = sb("spegl", lambda: mat_spegl("spegl"))
            side = d.get("speglSide")
            bot = sp if side in (-1, None, 0) else matt
            top = sp if side in (1, None, 0) else matt
            return [bot, top, sb("akrylkant", lambda: mat_akrylkant("akrylkant"))]
        if namn in ("akryl-opal", "opal", "akryl"):
            f = lin(farge) if farge else (0.93, 0.91, 0.87)
            o = sb(("opal", farge), lambda: mat_opal("opal", f, 0.62))
            k = sb(("opalkant", farge), lambda: mat_opal("opal-kant", f, 0.8, 0.2))
            return [o, o, k]
        if namn == "pp":
            o = sb("pp", lambda: mat_opal("pp", (0.92, 0.93, 0.93), 0.72, 0.45))
            return [o, o, o]
        if farge:
            f = sb(("maling", farge), lambda: mat_matt("maling-" + farge, lin(farge), 0.62))
            return [f, f, kant_tre]
        if namn == "mdf":
            f = sb("mdf", lambda: mat_matt("mdf", lin("#b89472"), 0.8))
            return [f, f, sb("mdfkant", lambda: mat_matt("mdf-kant", lin("#2a1f17"), 0.9))]
        if namn == "papp":
            f = sb("papp", lambda: mat_matt("papp", lin("#b9966b"), 0.95))
            return [f, f, sb("pappkant", lambda: mat_matt("papp-kant", lin("#6b4f35"), 0.95))]
        if namn == "poppel":
            f = sb("poppel", lambda: mat_tre("poppel", lin("#efe3c8"), lin("#d9c7a2"), 0.62, 0.35))
            return [f, f, kant_tre]
        f = sb("bjork", lambda: mat_tre("bjork", lin("#e8d3ad"), lin("#c4a272"), 0.58, 0.6))
        return [f, f, kant_tre]

    def utstyr_stoff(self, u):
        sb = self.sb
        f = u.get("farge")
        slag = u.get("slag")
        st = u.get("stoff")
        c = lin(f) if f else None
        if st in ("alu", "aluminium") or (u.get("metall") and c and not (c[0] > c[2] * 1.35)):
            return sb(("alu", f), lambda: mat_alu("alu", (0.86, 0.87, 0.88) if not c else tuple(max(x, 0.6) for x in c), u.get("ru", 0.3) * 0.9))
        if st in ("messing", "brass") or (u.get("metall") and c):
            return sb(("messing", f), lambda: mat_alu("messing", (0.78, 0.55, 0.24), min(u.get("ru", 0.32), 0.38), 0.4))
        if st in ("tekstil",) or (slag == "leidning" and (c is None or lum(c) < 0.05)):
            return sb("tekstil", lambda: mat_tekstil("tekstil"))
        if slag == "sokkel" and not f:
            return sb("sokkel", lambda: mat_matt("sokkel", lin("#1e1e20"), 0.45))
        if slag == "sylinder" and not f:
            return sb(("alu", None), lambda: mat_alu("alu", (0.86, 0.87, 0.88), 0.3))
        farge = c or lin("#8d8a85")
        return sb(("pulver", f, u.get("ru")), lambda: mat_matt("pulver", farge, min(0.75, max(0.35, u.get("ru", 0.5) * 0.7))))

    def bygg(self):
        sc = self.sc
        t0 = sc.get("tjukn") or 3
        for i, d in enumerate(sc["delar"]):
            namn = f"{self.namn}-{d.get('adr') or d.get('namn') or i}"
            t = d.get("tjukn") or t0
            by = d.get("boygd") or {}
            if by.get("nett"):
                n = by["nett"]
                verts = [tuple(n[j:j + 3]) for j in range(0, len(n), 3)]
                me = bpy.data.meshes.new(namn)
                me.from_pydata(verts, [], [(j, j + 1, j + 2) for j in range(0, len(verts), 3)])
                mats = self.plate_stoff(d)
                self.legg(me, [mats[1]], Matrix.Identity(4))
                continue
            k = by.get("krumming") or d.get("krumming") or 0
            me = plate_mesh(namn, d["omriss"], d.get("hol"), t, k)
            self.plater += 1
            if d.get("areal"):
                self.flateavvik = max(self.flateavvik, abs(me["flate"] - d["areal"]) / d["areal"])
            self.hol += len(d.get("hol") or [])
            a = d.get("matrise") or [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
            M = Matrix([a[0:4], a[4:8], a[8:12], a[12:16]]).transposed()
            if M.to_3x3().determinant() < 0:
                me.flip_normals()
            self.legg(me, self.plate_stoff(d), M)
        utstyr = sc.get("utstyr") or []
        paerer = [u for u in utstyr if u.get("slag") == "paere"]
        for j, u in enumerate(utstyr):
            slag = u.get("slag")
            namn = f"{self.namn}-{slag}{j}"
            if slag == "paere":
                d = u.get("diameter") or 60
                L = u.get("lengd") or 105
                glas, sokkel, Ms, r = paere_mesh(namn, d, L)
                M = retta(u["senter"], u.get("retning"))
                P = 9.0 * self.kraft * u.get("styrke", 1.0)
                area = sum(p.area for p in glas.polygons) * MM * MM
                styrke = P / max(area, 1e-6)
                self.legg(glas, [mat_lys(namn + "-lys", styrke)], M)
                self.legg(sokkel, [self.sb("paeresokkel", lambda: mat_alu("paeresokkel", (0.8, 0.79, 0.76), 0.35, 0.2))], M @ Ms)
                self.lys.append(("paere", Vector(u["senter"]), P))
            elif slag in ("sokkel", "sylinder"):
                d = u.get("diameter") or 40
                L = u.get("lengd") or 55
                me = dreie(namn, sylinder_profil(d, L), 64)
                self.legg(me, [self.utstyr_stoff(u)], retta(u["senter"], u.get("retning")))
            elif slag == "leidning":
                self.leidningar.append(u)
            elif slag == "boks":
                s = u.get("storleik") or [20, 20, 20]
                bm = bmesh.new()
                bmesh.ops.create_cube(bm, size=1.0)
                for v in bm.verts:
                    v.co = Vector((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2]))
                me = bpy.data.meshes.new(namn)
                bm.to_mesh(me)
                bm.free()
                if u.get("matrise"):
                    a = u["matrise"]
                    M = Matrix([a[0:4], a[4:8], a[8:12], a[12:16]]).transposed()
                else:
                    M = Matrix.Translation(Vector(u["senter"]))
                self.legg(me, [self.utstyr_stoff(u)], M)
            elif slag == "kule":
                d = u.get("diameter") or 20
                prof = [(d / 2 * math.sin(math.pi * i / 24), -d / 2 * math.cos(math.pi * i / 24)) for i in range(25)]
                self.legg(dreie(namn, prof, 48, 80), [self.utstyr_stoff(u)], Matrix.Translation(Vector(u["senter"])))
        lys = sc.get("lys")
        if isinstance(lys, dict):
            lys = [lys]
        for q in lys or []:
            self.lys.append(("punkt", Vector(q["punkt"]), 4.0 * self.kraft * q.get("styrke", 1.0), q.get("radius", 8)))
        self.paerer = len(paerer)
        self.boks_rekn()

    def er_kabel(self, u):
        f = u.get("farge")
        return f is None or lum(lin(f)) < 0.05

    def boks_rekn(self):
        xs = [p.x for p in self.pkt]
        ys = [p.y for p in self.pkt]
        zs = [p.z for p in self.pkt]
        for u in self.leidningar:
            if not self.er_kabel(u):
                r = (u.get("diameter") or 6) / 2
                for q in u["punkt"]:
                    xs += [q[0] - r, q[0] + r]
                    ys += [q[1] - r, q[1] + r]
                    zs += [q[2] - r, q[2] + r]
        self.b0 = Vector((min(xs), min(ys), min(zs)))
        self.b1 = Vector((max(xs), max(ys), max(zs)))

    def plasser(self, pos, rot_z=0.0):
        self.T = Matrix.Translation(pos) @ Matrix.Rotation(rot_z, 4, "Z") @ Matrix.Scale(MM, 4)
        for o, M in self.obj:
            o.matrix_world = self.T @ M

    def verd(self, p):
        return self.T @ Vector(p)

    def verdspunkt(self):
        return [self.T @ p for p in self.pkt]

    def leidning_bygg(self, flate=None):
        for j, u in enumerate(self.leidningar):
            d = u.get("diameter") or 6
            pk = [self.verd(q) for q in u["punkt"]]
            if self.er_kabel(u) and flate is not None:
                z_flate, y_bak, x_lo, x_hi = flate
                r = d / 2 * MM
                ny = []
                for p in pk:
                    q = p.copy()
                    if q.z - r < z_flate + 0.004:
                        q.z = z_flate + r
                    q.y = min(q.y, y_bak - r - 0.002)
                    ny.append(q)
                last = ny[-1]
                if last.z - r < z_flate + 0.01:
                    ny.append(Vector((last.x, y_bak + 0.004, z_flate + r * 0.4)))
                    ny.append(Vector((last.x, y_bak + 0.011, z_flate - 0.05)))
                    ny.append(Vector((last.x, y_bak + 0.011, z_flate - 0.6)))
                pk = ny
            me = roer(f"{self.namn}-leidning{j}", [tuple(p) for p in pk], d * MM, 14 if self.er_kabel(u) else 20)
            o = bpy.data.objects.new(me.name, me)
            bpy.context.scene.collection.objects.link(o)
            me.materials.append(self.utstyr_stoff(u))

    def lyskjelder(self, kraft):
        for o, M in self.obj:
            for m in o.data.materials:
                if m and m.name.endswith("-lys"):
                    e = m.node_tree.nodes.get("Emission")
                    if e is not None:
                        if "styrke0" not in m:
                            m["styrke0"] = e.inputs["Strength"].default_value
                        e.inputs["Strength"].default_value = m["styrke0"] * kraft
        for i, l in enumerate(self.lys):
            if l[0] != "punkt":
                continue
            ld = bpy.data.lights.get(f"{self.namn}-lys{i}") or bpy.data.lights.new(f"{self.namn}-lys{i}", "POINT")
            ld.energy = l[2] * kraft
            ld.shadow_soft_size = l[3] * MM
            ld.use_temperature = True
            ld.temperature = 2700
            ob = bpy.data.objects.get(f"{self.namn}-lys{i}") or bpy.data.objects.new(f"{self.namn}-lys{i}", ld)
            if ob.name not in bpy.context.scene.collection.objects:
                bpy.context.scene.collection.objects.link(ob)
            ob.location = self.verd(l[1])
            ob.visible_camera = False


def boks(namn, x0, x1, y0, y1, z0, z1, mat, fas=0.0015):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector(((x0 + x1) / 2 + v.co.x * (x1 - x0), (y0 + y1) / 2 + v.co.y * (y1 - y0), (z0 + z1) / 2 + v.co.z * (z1 - z0)))
    if fas > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=fas, segments=2, affect="EDGES", profile=0.5)
    me = bpy.data.meshes.new(namn)
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(40))
    o = bpy.data.objects.new(namn, me)
    bpy.context.scene.collection.objects.link(o)
    me.materials.append(mat)
    return o


def plan(namn, verts, faces, mat):
    me = bpy.data.meshes.new(namn)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(namn, me)
    bpy.context.scene.collection.objects.link(o)
    me.materials.append(mat)
    return o


def mat_valnott():
    s = Stoff("valnott")
    k = s.koord(1.0)
    sep = s.n("ShaderNodeSeparateXYZ")
    s.l(k, sep.inputs[0])
    yz = s.n("ShaderNodeMath", operation="ADD")
    s.l(sep.outputs[1], yz.inputs[0])
    s.l(sep.outputs[2], yz.inputs[1])
    def strekk(f):
        c = s.n("ShaderNodeCombineXYZ")
        m = s.n("ShaderNodeMath", operation="MULTIPLY")
        m.inputs[1].default_value = f
        s.l(sep.outputs[0], m.inputs[0])
        s.l(m.outputs[0], c.inputs[0])
        s.l(yz.outputs[0], c.inputs[1])
        return c.outputs[0]
    fin = s.n("ShaderNodeTexNoise", Scale=220.0, Detail=2.0, Roughness=0.5)
    s.l(strekk(0.04), fin.inputs["Vector"])
    grov = s.n("ShaderNodeTexNoise", Scale=30.0, Detail=2.0, Roughness=0.5)
    s.l(strekk(0.06), grov.inputs["Vector"])
    w = s.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction="Y", Scale=5.0, Distortion=14.0, Detail=1.5)
    w.inputs["Detail Scale"].default_value = 0.7
    s.l(strekk(0.18), w.inputs["Vector"])
    a = s.n("ShaderNodeMix", data_type="FLOAT")
    a.inputs["Factor"].default_value = 0.25
    s.l(fin.outputs["Fac"], a.inputs[2])
    s.l(grov.outputs["Fac"], a.inputs[3])
    b = s.n("ShaderNodeMix", data_type="FLOAT")
    b.inputs["Factor"].default_value = 0.2
    s.l(a.outputs[0], b.inputs[2])
    s.l(w.outputs["Fac"], b.inputs[3])
    farge = s.rampe(b.outputs[0], lin("#2c1d14"), lin("#5f4333"), 0.3, 0.7)
    p = s.principled(Roughness=0.4)
    p.inputs["Coat Weight"].default_value = 0.3
    p.inputs["Coat Roughness"].default_value = 0.3
    s.l(farge, p.inputs["Base Color"])
    s.l(s.bump(fin.outputs["Fac"], 0.04, 0.0003), p.inputs["Normal"])
    return s.ferdig(p)


def mat_kalk():
    s = Stoff("kalkpuss")
    k = s.koord(1.0, False)
    stor = s.n("ShaderNodeTexNoise", Scale=1.4, Detail=3.0, Roughness=0.55)
    s.l(k, stor.inputs["Vector"])
    mid = s.n("ShaderNodeTexNoise", Scale=9.0, Detail=3.0, Roughness=0.6)
    s.l(k, mid.inputs["Vector"])
    fin = s.n("ShaderNodeTexNoise", Scale=140.0, Detail=2.0, Roughness=0.7)
    s.l(k, fin.inputs["Vector"])
    mix = s.n("ShaderNodeMix", data_type="FLOAT")
    mix.inputs["Factor"].default_value = 0.4
    s.l(stor.outputs["Fac"], mix.inputs[2])
    s.l(mid.outputs["Fac"], mix.inputs[3])
    farge = s.rampe(mix.outputs[0], lin("#a89c8c"), lin("#c2b8a9"), 0.3, 0.72)
    p = s.principled(Roughness=0.92)
    p.inputs["Specular IOR Level"].default_value = 0.3
    s.l(farge, p.inputs["Base Color"])
    h = s.n("ShaderNodeMix", data_type="FLOAT")
    h.inputs["Factor"].default_value = 0.55
    s.l(mid.outputs["Fac"], h.inputs[2])
    s.l(fin.outputs["Fac"], h.inputs[3])
    s.l(s.bump(h.outputs[0], 0.28, 0.0015), p.inputs["Normal"])
    return s.ferdig(p)


def mat_lin():
    s = Stoff("lin")
    tc = s.n("ShaderNodeTexCoord")
    lw = s.n("ShaderNodeLayerWeight", Blend=0.35)
    fac = s.n("ShaderNodeMapRange")
    fac.inputs["To Min"].default_value = 0.42
    fac.inputs["To Max"].default_value = 1.0
    s.l(lw.outputs["Facing"], fac.inputs["Value"])
    nz = s.n("ShaderNodeTexNoise", Scale=60.0, Detail=2.0)
    s.l(tc.outputs["Object"], nz.inputs["Vector"])
    tp = s.n("ShaderNodeBsdfTransparent")
    tl = s.n("ShaderNodeBsdfTranslucent")
    tl.inputs["Color"].default_value = (0.85, 0.8, 0.7, 1)
    df = s.n("ShaderNodeBsdfDiffuse")
    df.inputs["Color"].default_value = (0.78, 0.73, 0.64, 1)
    stoff = s.n("ShaderNodeMixShader")
    stoff.inputs[0].default_value = 0.55
    s.l(df.outputs[0], stoff.inputs[1])
    s.l(tl.outputs[0], stoff.inputs[2])
    mix = s.n("ShaderNodeMixShader")
    s.l(fac.outputs[0], mix.inputs[0])
    s.l(tp.outputs[0], mix.inputs[1])
    s.l(stoff.outputs[0], mix.inputs[2])
    return s.ferdig(mix.outputs[0])


def gardin(namn, x, y0, y1, z0, z1, mat, seed=3):
    rnd = random.Random(seed)
    ny = 160
    nz = 24
    fasar = [(rnd.uniform(0.12, 0.22), rnd.uniform(0, 6.28), rnd.uniform(0.016, 0.026)) for _ in range(3)] + [(rnd.uniform(0.4, 0.7), rnd.uniform(0, 6.28), 0.02)]
    verts, faces = [], []
    for j in range(nz + 1):
        z = z0 + (z1 - z0) * j / nz
        for i in range(ny + 1):
            y = y0 + (y1 - y0) * i / ny
            dx = sum(a * math.sin(2 * math.pi * y / l + f + 0.15 * z) for l, f, a in fasar)
            verts.append((x + dx, y, z))
    for j in range(nz):
        for i in range(ny):
            a = j * (ny + 1) + i
            faces.append((a, a + 1, a + ny + 2, a + ny + 1))
    o = plan(namn, verts, faces, mat)
    o.data.shade_smooth()
    return o


def lys_obj(namn, kind, loc, retn=None, **kw):
    ld = bpy.data.lights.new(namn, kind)
    for k, v in kw.items():
        setattr(ld, k, v)
    o = bpy.data.objects.new(namn, ld)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    if retn is not None:
        o.rotation_euler = Vector(retn).to_track_quat("-Z", "Y").to_euler()
    return o


def verd(farge, styrke):
    w = bpy.data.worlds.new("verd")
    bpy.context.scene.world = w
    bg = w.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (*farge, 1)
    bg.inputs[1].default_value = styrke
    return bg


class Kamera:
    def __init__(self, linse=50.0, sensor=36.0, aspekt=1.5):
        self.linse, self.sensor, self.aspekt = linse, sensor, aspekt

    def sett(self, C, T):
        self.C, self.T = Vector(C), Vector(T)
        f = (self.T - self.C).normalized()
        r = f.cross(Vector((0, 0, 1))).normalized()
        u = r.cross(f)
        self.f, self.r, self.u = f, r, u

    def ndc(self, p):
        d = p - self.C
        z = d.dot(self.f)
        k = self.linse / (self.sensor / 2)
        return d.dot(self.r) / z * k, d.dot(self.u) / z * k * self.aspekt

    def ramme(self, pkt):
        q = [self.ndc(p) for p in pkt]
        return min(a for a, b in q), max(a for a, b in q), min(b for a, b in q), max(b for a, b in q)

    def pass_inn(self, pkt, retning, maal, bredd_frac, hogd_frac, botn=None, midt_x=0.0, midt_y=0.0):
        D = 2.0
        for _ in range(12):
            self.sett(maal - retning * D, maal)
            x0, x1, y0, y1 = self.ramme(pkt)
            s = max((x1 - x0) / (2 * bredd_frac), (y1 - y0) / (2 * hogd_frac))
            D *= s
        self.sett(maal - retning * D, maal)
        x0, x1, y0, y1 = self.ramme(pkt)
        self.shift_x = ((x0 + x1) / 2 - midt_x) / 2
        if botn is not None:
            self.shift_y = (y0 - botn) / (2 * self.aspekt)
        else:
            self.shift_y = ((y0 + y1) / 2 - midt_y) / (2 * self.aspekt)
        self.D = D
        return D

    def ramme_shift(self, pkt):
        x0, x1, y0, y1 = self.ramme(pkt)
        return x0 - 2 * self.shift_x, x1 - 2 * self.shift_x, y0 - 2 * self.shift_y * self.aspekt, y1 - 2 * self.shift_y * self.aspekt

    def frustum_x_min(self, y_plan):
        k = self.sensor / 2 / self.linse
        best = 1e9
        for sy in (-1, 1):
            nx = -1 + 2 * self.shift_x
            ny = sy + 2 * self.shift_y * self.aspekt
            d = self.f + self.r * (nx * k) + self.u * (ny * k / self.aspekt)
            if abs(d.y) < 1e-6:
                continue
            t = (y_plan - self.C.y) / d.y
            if t > 0:
                best = min(best, (self.C + d * t).x)
        return best

    def frustum_x_max(self, y_plan):
        k = self.sensor / 2 / self.linse
        best = -1e9
        for sy in (-1, 1):
            nx = 1 + 2 * self.shift_x
            ny = sy + 2 * self.shift_y * self.aspekt
            d = self.f + self.r * (nx * k) + self.u * (ny * k / self.aspekt)
            t = (y_plan - self.C.y) / d.y
            if t > 0:
                best = max(best, (self.C + d * t).x)
        return best

    def lag(self, fstop=5.6, fokus=None):
        cd = bpy.data.cameras.new("kamera")
        cd.lens = self.linse
        cd.sensor_width = self.sensor
        cd.sensor_fit = "HORIZONTAL"
        cd.shift_x = self.shift_x
        cd.shift_y = self.shift_y
        cd.clip_start = 0.02
        cd.clip_end = 60
        cd.dof.use_dof = True
        cd.dof.focus_distance = fokus or (self.T - self.C).length
        cd.dof.aperture_fstop = fstop
        o = bpy.data.objects.new("kamera", cd)
        bpy.context.scene.collection.objects.link(o)
        R = Matrix((self.r, self.u, -self.f)).transposed().to_4x4()
        o.matrix_world = Matrix.Translation(self.C) @ R
        bpy.context.scene.camera = o
        return o


def tom_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for b in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.worlds):
        for x in list(b):
            b.remove(x)


def render_oppsett(b, h, prover, rask):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    c = sc.cycles
    c.device = "CPU"
    c.samples = prover
    c.use_adaptive_sampling = True
    c.adaptive_threshold = 0.06 if rask else 0.04
    c.adaptive_min_samples = min(16, prover // 2)
    c.use_denoising = True
    c.denoiser = "OPENIMAGEDENOISE"
    c.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    c.denoising_prefilter = "ACCURATE"
    c.denoising_quality = "HIGH"
    c.use_light_tree = False
    c.max_bounces = 10
    c.diffuse_bounces = 3
    c.glossy_bounces = 5
    c.transmission_bounces = 8
    c.transparent_max_bounces = 24
    c.sample_clamp_direct = 0
    c.sample_clamp_indirect = 6.0
    c.blur_glossy = 0.6
    c.caustics_reflective = True
    c.caustics_refractive = False
    c.use_guiding = False
    sc.render.threads_mode = "FIXED"
    sc.render.threads = 4
    sc.render.resolution_x = b
    sc.render.resolution_y = h
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "8"
    sc.render.film_transparent = False
    vs = sc.view_settings
    vs.view_transform = "AgX"
    for look in ("AgX - Medium High Contrast", "Medium High Contrast"):
        try:
            vs.look = look
            break
        except Exception:
            pass


def maal_lys(berre_lampe):
    import numpy as np
    sc = bpy.context.scene
    r, c = sc.render, sc.cycles
    gml = (r.resolution_x, r.resolution_y, c.samples, r.filepath, r.image_settings.file_format, r.image_settings.color_depth)
    r.resolution_y = max(60, round(220 * r.resolution_y / r.resolution_x))
    r.resolution_x = 220
    c.samples = 24
    tmp = os.path.join(os.path.dirname(gml[3]) or ".", ".eksponering.exr")
    r.filepath = tmp
    r.image_settings.file_format = "OPEN_EXR"
    r.image_settings.color_depth = "32"
    glas = [o for o in bpy.data.objects if o.type == "MESH" and any(m and m.name.endswith("-lys") for m in o.data.materials)]
    for o in glas:
        o.visible_camera = False
    av = []
    if berre_lampe:
        av = [(o.data, "energy", o.data.energy) for o in bpy.data.objects if o.type == "LIGHT" and o.name in ("sol", "himmel", "skjermbak")]
        bg = sc.world.node_tree.nodes.get("Background") if sc.world else None
        if bg is not None:
            av.append((bg.inputs[1], "default_value", bg.inputs[1].default_value))
        for d, k, _ in av:
            setattr(d, k, 0.0)
    bpy.ops.render.render(write_still=True)
    for d, k, v in av:
        setattr(d, k, v)
    for o in glas:
        o.visible_camera = True
    img = bpy.data.images.load(tmp)
    px = np.array(img.pixels[:], dtype=np.float32).reshape(-1, 4)
    bpy.data.images.remove(img)
    os.remove(tmp)
    r.resolution_x, r.resolution_y, c.samples, r.filepath = gml[:4]
    r.image_settings.file_format, r.image_settings.color_depth = gml[4], gml[5]
    return px[:, 0] * 0.2126 + px[:, 1] * 0.7152 + px[:, 2] * 0.0722


def eksponer(maal):
    import numpy as np
    full = maal_lys(False)
    if maal == "dag":
        ev = min(math.log2(0.2 / max(float(np.median(full)), 1e-6)), math.log2(5.0 / max(float(np.quantile(full, 0.99)), 1e-6)))
    elif maal == "studio":
        ev = min(math.log2(0.07 / max(float(np.median(full)), 1e-6)), math.log2(4.0 / max(float(np.quantile(full, 0.99)), 1e-6)))
    else:
        lampe = maal_lys(True)
        omgjevnad = np.maximum(full - lampe, 0)
        m = max(float(np.median(omgjevnad)), 1e-6)
        ev = min(max(math.log2(1.2 / max(float(np.quantile(lampe, 0.95)), 1e-6)), math.log2(0.012 / m)), math.log2(0.035 / m))
    return max(-8.0, min(8.0, ev))


def kantsjekk(sti):
    import numpy as np
    img = bpy.data.images.load(sti)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(img)
    L = px[..., :3].mean(axis=2)
    e = max(2, w // 100)
    ut = {}
    for namn, kant, inne in (("venstre", L[:, :e], L[:, e:6 * e]), ("hogre", L[:, -e:], L[:, -6 * e:-e]), ("topp", L[-e:, :], L[-6 * e:-e, :]), ("botn", L[:e, :], L[e:6 * e, :])):
        ut[namn] = round(float(kant.mean() / max(inne.mean(), 1e-4)), 2)
    return {"kant_mot_innsida": ut, "svart_kant": [k for k, v in ut.items() if v < 0.6], "klipt_pst": round(float((L > 0.995).mean() * 100), 2)}


def render(sti, maal):
    sc = bpy.context.scene
    sc.render.filepath = sti
    t, c = time.time(), time.process_time()
    sc.view_settings.exposure = eksponer(maal)
    EV[os.path.basename(sti)] = round(sc.view_settings.exposure, 2)
    bpy.ops.render.render(write_still=True)
    CPU[os.path.basename(sti)] = round(time.process_time() - c, 1)
    BILETE[os.path.basename(sti)] = kantsjekk(sti)
    return time.time() - t


class Rom:
    def __init__(self, lamper, min_djupn=0.48, ekstra=0.2):
        self.H = 0.80
        self.sb = lamper[0].sb
        b0 = Vector((min(l.b0.x for l in lamper), min(l.b0.y for l in lamper), min(l.b0.z for l in lamper))) * MM
        b1 = Vector((max(l.b1.x for l in lamper), max(l.b1.y for l in lamper), max(l.b1.z for l in lamper))) * MM
        self.lampdjupn = b1.y - b0.y
        self.D = max(min_djupn, self.lampdjupn + ekstra)
        self.yf = -self.D / 2
        self.yb = self.D / 2
        self.Yw = self.yb + 0.02


def sjekk_plass(lampe, rom, props=()):
    pkt = lampe.verdspunkt()
    z0 = min(p.z for p in pkt)
    fot = [p for p in pkt if p.z < z0 + 0.012]
    k = {"kontakt_mm": round((z0 - rom.H) * 1000, 3),
         "vegg_mm": round((rom.Yw - max(p.y for p in pkt)) * 1000, 1),
         "fot_inne_mm": round(min(min(p.y for p in fot) - rom.yf, rom.yb - max(p.y for p in fot), min(p.x for p in fot) - rom.xl, rom.xr - max(p.x for p in fot)) * 1000, 1),
         "under_topp": sum(1 for p in pkt if p.z < rom.H - 1e-5 and rom.xl < p.x < rom.xr and rom.yf < p.y < rom.yb)}
    if props:
        lx0, lx1 = min(p.x for p in pkt), max(p.x for p in pkt)
        ly0, ly1 = min(p.y for p in pkt), max(p.y for p in pkt)
        k["props_i_lampa"] = [n for n, x0, x1, y0, y1, zt in props if x0 < lx1 and x1 > lx0 and y0 < ly1 and y1 > ly0 and any(x0 < p.x < x1 and y0 < p.y < y1 and p.z < zt for p in pkt)]
    return k


def bygg_mobel(rom, xl, xr):
    rom.xl, rom.xr = xl, xr
    H = rom.H
    v = rom.sb("valnott", mat_valnott)
    skugge = rom.sb("skugge", lambda: mat_matt("skugge", (0.02, 0.015, 0.012), 0.8, False))
    yf, yb = rom.yf, rom.yb
    boks("topp", xl, xr, yf, yb, H - 0.045, H, v, 0.002)
    boks("fuge", xl + 0.01, xr - 0.01, yf + 0.018, yb - 0.01, H - 0.059, H - 0.045, skugge, 0.0)
    xm = (xl + xr) / 2
    zt = H - 0.059
    zb = zt - 0.23
    boks("skuff-v", xl + 0.01, xm - 0.0015, yf, yf + 0.02, zb, zt, v, 0.0015)
    boks("skuff-h", xm + 0.0015, xr - 0.01, yf, yf + 0.02, zb, zt, v, 0.0015)
    boks("dor-v", xl + 0.01, xm - 0.0015, yf, yf + 0.02, 0.1, zb - 0.003, v, 0.0015)
    boks("dor-h", xm + 0.0015, xr - 0.01, yf, yf + 0.02, 0.1, zb - 0.003, v, 0.0015)
    boks("korpus", xl, xr, yf + 0.02, yb, 0.08, H - 0.059, v, 0.0)
    boks("sokkel", xl + 0.04, xr - 0.04, yf + 0.05, yb - 0.03, 0.0, 0.08, skugge, 0.0)


def bygg_rom(rom, kam, dag=True):
    Yw = rom.Yw
    x_venstre = kam.frustum_x_min(Yw)
    x_hogre = kam.frustum_x_max(Yw)
    XL = min(x_venstre - 0.45, kam.C.x - 0.6, -0.8)
    xr = x_hogre + 0.8
    rom.XL = XL
    kalk = rom.sb("kalk", mat_kalk)
    plan("vegg", [(XL - 0.2, Yw, 0), (xr + 3, Yw, 0), (xr + 3, Yw, 3.0), (XL - 0.2, Yw, 3.0)], [(0, 3, 2, 1)], kalk)
    golv = rom.sb("golv", lambda: mat_matt("golv", lin("#6b5440"), 0.55, False))
    plan("golv", [(XL - 0.2, Yw - 6, 0), (xr + 3, Yw - 6, 0), (xr + 3, Yw, 0), (XL - 0.2, Yw, 0)], [(0, 1, 2, 3)], golv)
    vind_y1 = Yw - rom.D - 0.3
    vind_y0 = vind_y1 - 1.35
    sill, topp = 0.92, 2.35
    t = 0.14
    xw0, xw1 = XL - t, XL
    boks("sidevegg-bak", xw0, xw1, vind_y1, Yw, 0, 2.8, kalk, 0)
    boks("sidevegg-fram", xw0, xw1, Yw - 12, vind_y0, 0, 2.8, kalk, 0)
    tak = plan("tak", [(XL - 0.2, Yw - 12, 2.8), (XL - 0.2, Yw, 2.8), (xr + 3, Yw, 2.8), (xr + 3, Yw - 12, 2.8)], [(0, 1, 2, 3)], rom.sb("takmaling", lambda: mat_matt("takmaling", (0.75, 0.74, 0.71), 0.9, False)))
    for k in ("visible_camera", "visible_diffuse", "visible_glossy", "visible_transmission"):
        setattr(tak, k, False)
    boks("sidevegg-under", xw0, xw1, vind_y0, vind_y1, 0, sill, kalk, 0)
    boks("sidevegg-over", xw0, xw1, vind_y0, vind_y1, topp, 2.8, kalk, 0)
    karm = rom.sb("karm", lambda: mat_matt("karm", lin("#e9e6df"), 0.5, False))
    ym = (vind_y0 + vind_y1) / 2
    boks("post", xw0 + 0.03, xw0 + 0.09, ym - 0.03, ym + 0.03, sill, topp, karm, 0.002)
    boks("losholt", xw0 + 0.03, xw0 + 0.09, vind_y0, vind_y1, 1.92, 1.98, karm, 0.002)
    g = gardin("gardin", XL + 0.13, vind_y0 - 0.25, vind_y1 + 0.2, 0.03, 2.6, rom.sb("lin", mat_lin))
    for k in ("visible_diffuse", "visible_glossy", "visible_transmission"):
        setattr(g, k, False)
    rom.vindauge = (XL, vind_y0, vind_y1, sill, topp)
    bygg_mobel(rom, XL + 0.25, xr)
    return XL, xr


def dagslys(rom, maal, dag):
    XL, y0, y1, sill, topp = rom.vindauge
    sentrum = Vector((XL - 0.5, (y0 + y1) / 2 + 0.25, (sill + topp) / 2 + 0.25))
    retn = (maal - sentrum).normalized()
    sol = lys_obj("sol", "SUN", sentrum, retn, energy=3.0 if dag else 0.0, angle=math.radians(1.3))
    sol.data.use_temperature = True
    sol.data.temperature = 5200
    himmel = lys_obj("himmel", "AREA", (XL + 0.2, (y0 + y1) / 2, (sill + topp) / 2), (1, 0, 0), shape="RECTANGLE",
                     size=y1 - y0, size_y=topp - sill, energy=260 if dag else 26)
    himmel.data.use_temperature = True
    himmel.data.temperature = 6500 if dag else 14000
    if not dag:
        himmel.data.color = (0.55, 0.7, 1.0)
    return sol, himmel


def maal_dag(rom, lampe):
    return Vector((lampe.T.translation.x - 0.05, rom.Yw, rom.H + 0.32))


def lamp_pos_sentrert(lampe, rom, bak=False):
    b0, b1 = lampe.b0 * MM, lampe.b1 * MM
    cx = (b0.x + b1.x) / 2
    cy = (b0.y + b1.y) / 2
    y = -cy
    if bak:
        y = rom.Yw - 0.07 - b1.y
    else:
        y = min(y, rom.Yw - 0.05 - b1.y)
    y = max(y, rom.yf + 0.03 - b0.y)
    return Vector((-cx, y, rom.H - b0.z))


def skot_miljo(sc, kveld_og_dag, args, ut, namn, b, h, prover, tider):
    tom_scene()
    sb = Stoffbok()
    lampe = Lampe(sc, "lampe", sb, args.kraft)
    rom = Rom([lampe])
    lampe.plasser(lamp_pos_sentrert(lampe, rom))
    pkt = lampe.verdspunkt()
    kam = Kamera(50.0, 36.0, b / h)
    lh = (lampe.b1.z - lampe.b0.z) * MM
    lb = max((lampe.b1.x - lampe.b0.x), (lampe.b1.y - lampe.b0.y)) * MM
    T = Vector((lampe.T.translation.x + (lampe.b0.x + lampe.b1.x) / 2 * MM, lampe.T.translation.y + (lampe.b0.y + lampe.b1.y) / 2 * MM, rom.H + lh * 0.45))
    az, el = math.radians(16), math.radians(7)
    retn = Vector((-math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), -math.sin(el)))
    kam.pass_inn(pkt, retn, T, 0.62, 0.56, botn=-0.44)
    bygg_rom(rom, kam)
    lampe.leidning_bygg((rom.H, rom.yb, None, None))
    kam.lag(5.6)
    render_oppsett(b, h, prover, args.rask)
    maal = maal_dag(rom, lampe)
    sol, himmel = dagslys(rom, maal, True)
    rammer = {}
    for skot in kveld_og_dag:
        dag = skot == "miljo-dag"
        sol.data.energy = 3.0 if dag else 0.0
        himmel.data.energy = 50 if dag else 45
        himmel.data.temperature = 6500 if dag else 14000
        himmel.data.color = (1, 1, 1) if dag else (0.5, 0.66, 1.0)
        verd((0.62, 0.57, 0.52) if dag else (0.16, 0.22, 0.38), 0.08 if dag else 0.02)
        lampe.lyskjelder(0.04 if dag else 1.0)
        sti = os.path.join(ut, f"{namn}-{skot}.png")
        s = render(sti, "dag" if dag else "kveld")
        tider[skot] = round(s, 1)
        rammer[skot] = [round(x, 3) for x in kam.ramme_shift(pkt)]
        KONTROLL[skot] = sjekk_plass(lampe, rom)
        print(f"  {skot:13s} {s:6.1f} s  {sti}  ramme {rammer[skot]}", flush=True)
        if args.blend:
            bpy.ops.wm.save_as_mainfile(filepath=sti[:-4] + ".blend")
    return rammer


def mat_keramikk():
    s = Stoff("keramikk")
    k = s.koord(1.0)
    nz = s.n("ShaderNodeTexNoise", Scale=350.0, Detail=1.0)
    s.l(k, nz.inputs["Vector"])
    prikk = s.rampe(nz.outputs["Fac"], (0.82, 0.8, 0.75), (0.25, 0.2, 0.17), 0.7, 0.74)
    p = s.principled(Roughness=0.12)
    p.inputs["Coat Weight"].default_value = 0.3
    s.l(prikk, p.inputs["Base Color"])
    return s.ferdig(p)


def mat_skjerm():
    s = Stoff("skjerm")
    tc = s.n("ShaderNodeTexCoord")
    sep = s.n("ShaderNodeSeparateXYZ")
    s.l(tc.outputs["Generated"], sep.inputs[0])
    def band(kanal, midt, halv):
        c = s.n("ShaderNodeMath", operation="COMPARE")
        c.inputs[1].default_value = midt
        c.inputs[2].default_value = halv
        s.l(sep.outputs[kanal], c.inputs[0])
        return c.outputs[0]
    panel = s.n("ShaderNodeMath", operation="MULTIPLY")
    s.l(band(0, 0.5, 0.2), panel.inputs[0])
    s.l(band(2, 0.47, 0.36), panel.inputs[1])
    w = s.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction="Z", Scale=30.0)
    s.l(tc.outputs["Generated"], w.inputs["Vector"])
    zv = s.n("ShaderNodeCombineXYZ")
    s.l(sep.outputs[2], zv.inputs[2])
    nz = s.n("ShaderNodeTexWhiteNoise", noise_dimensions="1D")
    zq = s.n("ShaderNodeMath", operation="FLOOR")
    zm = s.n("ShaderNodeMath", operation="MULTIPLY")
    zm.inputs[1].default_value = 30.0 / math.pi
    s.l(sep.outputs[2], zm.inputs[0])
    s.l(zm.outputs[0], zq.inputs[0])
    s.l(zq.outputs[0], nz.inputs["W"])
    xr = s.n("ShaderNodeMapRange")
    xr.inputs["From Min"].default_value = 0.3
    xr.inputs["From Max"].default_value = 0.7
    s.l(sep.outputs[0], xr.inputs["Value"])
    lengd = s.n("ShaderNodeMath", operation="LESS_THAN")
    s.l(xr.outputs[0], lengd.inputs[0])
    s.l(nz.outputs["Value"], lengd.inputs[1])
    linje = s.n("ShaderNodeMath", operation="GREATER_THAN")
    linje.inputs[1].default_value = 0.75
    s.l(w.outputs["Fac"], linje.inputs[0])
    tekst = s.n("ShaderNodeMath", operation="MULTIPLY")
    s.l(linje.outputs[0], tekst.inputs[0])
    s.l(lengd.outputs[0], tekst.inputs[1])
    tp = s.n("ShaderNodeMath", operation="MULTIPLY")
    s.l(tekst.outputs[0], tp.inputs[0])
    s.l(panel.outputs[0], tp.inputs[1])
    sum_ = s.n("ShaderNodeMath", operation="MULTIPLY_ADD")
    s.l(panel.outputs[0], sum_.inputs[0])
    sum_.inputs[1].default_value = 0.6
    s.l(tp.outputs[0], sum_.inputs[2])
    farge = s.rampe(sum_.outputs[0], (0.008, 0.009, 0.012), (0.075, 0.075, 0.072), 0.0, 1.6)
    e = s.n("ShaderNodeEmission", Strength=0.8)
    s.l(farge, e.inputs["Color"])
    g = s.principled(**{"Base Color": (0.01, 0.01, 0.012, 1), "Roughness": 0.25})
    add = s.n("ShaderNodeAddShader")
    s.l(e.outputs[0], add.inputs[0])
    s.l(g.outputs[0], add.inputs[1])
    return s.ferdig(add.outputs[0])


def legg_mesh(namn, me, mat, M):
    o = bpy.data.objects.new(namn, me)
    bpy.context.scene.collection.objects.link(o)
    me.materials.append(mat)
    o.matrix_world = M
    return o


def kopp(sb, pos):
    prof = [(0, 0), (0.026, 0), (0.0285, 0.002), (0.03, 0.006), (0.04, 0.05), (0.043, 0.088), (0.0435, 0.09), (0.0415, 0.0905),
            (0.0395, 0.087), (0.037, 0.05), (0.027, 0.01), (0, 0.009)]
    me = dreie("kopp", prof, 64, 50)
    keram = sb("keramikk", mat_keramikk)
    legg_mesh("kopp", me, keram, Matrix.Translation(pos))
    hank = [(0.038 + 0.022 * math.sin(math.pi * i / 16), 0, 0.072 - 0.044 * i / 16 + 0.006 * math.sin(math.pi * i / 16)) for i in range(17)]
    hme = roer("hank", hank, 0.008, 12)
    legg_mesh("hank", hme, keram, Matrix.Translation(pos) @ Matrix.Rotation(math.radians(-35), 4, "Z"))
    kaffi = dreie("kaffi", [(0, 0.068), (0.0405, 0.068)], 48)
    legg_mesh("kaffi", kaffi, sb("kaffi", lambda: mat_matt("kaffi", (0.03, 0.012, 0.005), 0.05, False)), Matrix.Translation(pos))


def notatbok(sb, pos, rot):
    R = Matrix.Translation(pos) @ Matrix.Rotation(rot, 4, "Z")
    dekke = sb("dekke", lambda: mat_matt("dekke", lin("#4f5546"), 0.85, True, False))
    ark = sb("ark", lambda: mat_matt("ark", lin("#ece4d2"), 0.9, False))
    w, d = 0.148, 0.21
    for nm, z0, z1, ww, dd, m in (("bok-botn", 0, 0.0015, w, d, dekke), ("bok-ark", 0.0015, 0.0125, w - 0.006, d - 0.006, ark), ("bok-topp", 0.0125, 0.014, w, d, dekke)):
        o = boks(nm, -ww / 2, ww / 2, -dd / 2, dd / 2, z0, z1, m, 0.0006)
        o.matrix_world = R @ o.matrix_world
    o = boks("rygg", -w / 2 - 0.0005, -w / 2 + 0.003, -d / 2, d / 2, 0, 0.014, dekke, 0.001)
    o.matrix_world = R @ o.matrix_world
    blyant = dreie("blyant", [(0, -0.087), (0.0012, -0.087), (0.0036, -0.07), (0.0036, 0.087), (0, 0.087)], 6, 20)
    P = R @ Matrix.Translation((0.02, 0.0, 0.0175)) @ Matrix.Rotation(math.radians(80), 4, "Y") @ Matrix.Rotation(math.radians(8), 4, "X")
    legg_mesh("blyant", blyant, sb("blyantlakk", lambda: mat_matt("blyantlakk", lin("#1d2a24"), 0.3, False)), P)


def skjerm(sb, x, y, H, side):
    R = Matrix.Translation((x, y, H)) @ Matrix.Rotation(math.radians(-14 * side), 4, "Z")
    alu = sb(("alu", "skjerm"), lambda: mat_alu("alu-skjerm", (0.55, 0.56, 0.58), 0.35, 0.3))
    fot = dreie("skjermfot", sylinder_profil(200, 7, 1.5), 64)
    legg_mesh("skjermfot", fot, alu, R @ Matrix.Translation((0, 0.02, 0.0035)) @ Matrix.Scale(MM, 4))
    boks("skjermstolpe", -0.016, 0.016, 0.035, 0.047, 0.0, 0.29, alu, 0.002).matrix_world = R @ Matrix.Identity(4)
    W, Hs = 0.545, 0.322
    zc = 0.11 + Hs / 2
    tilt = Matrix.Translation((0, 0.03, zc)) @ Matrix.Rotation(math.radians(-6), 4, "X")
    o = boks("skjermrygg", -W / 2, W / 2, 0.0, 0.007, -Hs / 2, Hs / 2, sb("svart", lambda: mat_matt("svart", (0.012, 0.012, 0.013), 0.4, False)), 0.0015)
    o.matrix_world = R @ tilt @ o.matrix_world
    s = plan("skjermflate", [(-W / 2 + 0.005, -0.0005, -Hs / 2 + 0.012), (W / 2 - 0.005, -0.0005, -Hs / 2 + 0.012), (W / 2 - 0.005, -0.0005, Hs / 2 - 0.005), (-W / 2 + 0.005, -0.0005, Hs / 2 - 0.005)], [(0, 1, 2, 3)], sb("skjerm", mat_skjerm))
    s.matrix_world = R @ tilt
    bak = lys_obj("skjermbak", "AREA", R @ tilt @ Vector((0, 0.03, 0.02)), None, shape="RECTANGLE", size=0.42, size_y=0.18, energy=2.2)
    bak.matrix_world = R @ tilt @ Matrix.Translation((0, 0.03, 0.03)) @ Matrix.Rotation(math.radians(90), 4, "X")
    bak.data.use_temperature = True
    bak.data.temperature = 3000
    bak.visible_camera = False
    return (x - W / 2, x + W / 2)


def skot_arbeid(sc, args, ut, namn, b, h, prover, tider):
    tom_scene()
    sb = Stoffbok()
    lampe = Lampe(sc, "lampe", sb, args.kraft)
    rom = Rom([lampe], 0.6, 0.36)
    lampe.plasser(lamp_pos_sentrert(lampe, rom, bak=True))
    b0 = lampe.T @ lampe.b0
    b1 = lampe.T @ lampe.b1
    kabel_ende = None
    for u in lampe.leidningar:
        if lampe.er_kabel(u):
            kabel_ende = lampe.verd(u["punkt"][-1]).x
    side = -1 if (kabel_ende is not None and kabel_ende > (b0.x + b1.x) / 2) else 1
    H = rom.H
    halv = max(abs(b0.x), abs(b1.x))
    skx = side * (halv + 0.16 + 0.2725)
    skjerm(sb, skx, rom.Yw - 0.2, H, side)
    kx = -side * (halv * 0.55 + 0.1)
    ky = rom.yf + 0.12
    kopp(sb, Vector((kx, ky, H)))
    nbx = side * (halv * 0.3 + 0.04)
    nby = rom.yf + 0.04 + 0.105
    for _ in range(60):
        lo, hi = nbx - 0.12, nbx + 0.12
        fri_lampe = hi < b0.x - 0.01 or lo > b1.x + 0.01 or nby + 0.125 < b0.y - 0.01
        fri_kopp = abs(nbx - kx) > 0.18
        if fri_lampe and fri_kopp:
            break
        nbx += side * 0.02
    notatbok(sb, Vector((nbx, nby, H)), math.radians(-10 * side))
    pkt = lampe.verdspunkt()
    props = [Vector((kx + dx, ky + dy, H + z)) for dx in (-0.045, 0.045) for dy in (-0.045, 0.045) for z in (0, 0.09)]
    props += [Vector((nbx + dx, nby + dy, H)) for dx in (-0.11, 0.11) for dy in (-0.12, 0.12)]
    kam = Kamera(50.0, 36.0, b / h)
    alle = pkt + props
    lh = (lampe.b1.z - lampe.b0.z) * MM
    T = Vector(((b0.x + b1.x) / 2, (b0.y + b1.y) / 2 - 0.08, H + lh * 0.35))
    az, el = math.radians(-12 * side), math.radians(15)
    retn = Vector((-math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), -math.sin(el)))
    kam.pass_inn(alle, retn, T, 0.68, 0.64, botn=-0.8)
    bygg_rom(rom, kam)
    lampe.leidning_bygg((rom.H, rom.yb, None, None))
    kam.lag(5.6, (kam.T - kam.C).length)
    render_oppsett(b, h, prover, args.rask)
    sol, himmel = dagslys(rom, maal_dag(rom, lampe), False)
    himmel.data.energy = 60
    himmel.data.temperature = 12000
    himmel.data.color = (0.55, 0.7, 1.0)
    verd((0.16, 0.22, 0.38), 0.03)
    lampe.lyskjelder(1.0)
    sti = os.path.join(ut, f"{namn}-miljo-arbeid.png")
    KONTROLL["miljo-arbeid"] = sjekk_plass(lampe, rom, [("kopp", kx - 0.075, kx + 0.075, ky - 0.075, ky + 0.075, H + 0.092), ("notatbok", nbx - 0.13, nbx + 0.13, nby - 0.13, nby + 0.13, H + 0.022),
                                                        ("skjermfot", skx - 0.1, skx + 0.1, rom.Yw - 0.3, rom.Yw - 0.08, H + 0.3)])
    s = render(sti, "kveld")
    tider["miljo-arbeid"] = round(s, 1)
    r = [round(x, 3) for x in kam.ramme_shift(pkt)]
    print(f"  {'miljo-arbeid':13s} {s:6.1f} s  {sti}  ramme {r}", flush=True)
    if args.blend:
        bpy.ops.wm.save_as_mainfile(filepath=sti[:-4] + ".blend")
    return r


def mat_studio():
    s = Stoff("studio")
    k = s.koord(1.0, False)
    nz = s.n("ShaderNodeTexNoise", Scale=60.0, Detail=3.0)
    s.l(k, nz.inputs["Vector"])
    p = s.principled(**{"Base Color": (0.055, 0.056, 0.058, 1), "Roughness": 0.85})
    p.inputs["Specular IOR Level"].default_value = 0.3
    s.l(s.bump(nz.outputs["Fac"], 0.05, 0.0005), p.inputs["Normal"])
    return s.ferdig(p)


def sveip(mat, yb, R=0.9, B=8.0):
    prof = []
    for i in range(10):
        prof.append((yb - 5 + 5 * i / 10, 0.0))
    for i in range(25):
        a = math.pi / 2 * i / 24
        prof.append((yb + R * math.sin(a), R - R * math.cos(a)))
    for i in range(1, 8):
        prof.append((yb + R, R + 4 * i / 7))
    verts, faces = [], []
    for x in (-B / 2, B / 2):
        for y, z in prof:
            verts.append((x, y, z))
    n = len(prof)
    for i in range(n - 1):
        faces.append((i, i + 1, n + i + 1, n + i))
    o = plan("sveip", verts, faces, mat)
    o.data.shade_smooth()
    return o


def skot_modus(scener, args, ut, namn, b, h, prover, tider):
    tom_scene()
    sb = Stoffbok()
    lamper = [Lampe(s, f"lampe{i}", sb, args.kraft) for i, s in enumerate(scener)]
    breidd = [(l.b1.x - l.b0.x) * MM for l in lamper]
    hogd = max((l.b1.z - l.b0.z) * MM for l in lamper)
    gap = max(0.12, 0.3 * hogd)
    tot = sum(breidd) + gap * (len(lamper) - 1)
    x = -tot / 2
    for l, bw in zip(lamper, breidd):
        cx = (l.b0.x + l.b1.x) / 2 * MM
        cy = (l.b0.y + l.b1.y) / 2 * MM
        l.plasser(Vector((x + bw / 2 - cx, -cy, -l.b0.z * MM)))
        x += bw + gap
    pkt = [p for l in lamper for p in l.verdspunkt()]
    for l in lamper:
        l.leidning_bygg(None)
        l.lyskjelder(0.12)
    djup = max((l.b1.y - l.b0.y) * MM for l in lamper)
    sveip(sb("studio", mat_studio), djup / 2 + 0.35 + 0.4 * hogd, 1.0)
    kam = Kamera(55.0, 36.0, b / h)
    T = Vector((0, 0, hogd * 0.42))
    az, el = math.radians(-32), math.radians(32)
    retn = Vector((-math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), -math.sin(el)))
    kam.pass_inn(pkt, retn, T, 0.8, 0.7)
    kam.lag(8.0)
    render_oppsett(b, h, prover, args.rask)
    S = kam.D
    def mot(p):
        return (T - Vector(p)).normalized()
    k1 = Vector((-1.1, -0.9, 1.3)) * S * 0.8
    lys_obj("nokkel", "AREA", k1, mot(k1), shape="RECTANGLE", size=1.2 * S * 0.6, size_y=0.9 * S * 0.6, energy=60 * S * S)
    k2 = Vector((1.3, -0.5, 0.55)) * S * 0.8
    lys_obj("fyll", "AREA", k2, mot(k2), shape="RECTANGLE", size=1.0 * S * 0.6, size_y=0.8 * S * 0.6, energy=10 * S * S)
    k3 = Vector((0.4, 1.1, 1.4)) * S * 0.8
    lys_obj("kant", "AREA", k3, mot(k3), shape="RECTANGLE", size=0.6 * S * 0.6, size_y=0.6 * S * 0.6, energy=25 * S * S)
    verd((0.5, 0.5, 0.52), 0.03)
    sti = os.path.join(ut, f"{namn}-modus.png")
    s = render(sti, "studio")
    tider["modus"] = round(s, 1)
    r = [round(x, 3) for x in kam.ramme_shift(pkt)]
    print(f"  {'modus':13s} {s:6.1f} s  {sti}  ramme {r}  ({len(lamper)} stilling{'ar' if len(lamper) > 1 else ''})", flush=True)
    if args.blend:
        bpy.ops.wm.save_as_mainfile(filepath=sti[:-4] + ".blend")
    return r


def main():
    args = argument()
    t0 = time.time()
    sc = les_design(args.mappe)
    am = arbeid_mappe(args.mappe, args.arbeid)
    sca = les_design(am) if am else None
    namn = args.namn or sc.get("namn") or os.path.basename(os.path.dirname(sc["mappe"]))
    ut = os.path.abspath(args.ut or sc["mappe"])
    os.makedirs(ut, exist_ok=True)
    skot = [s.strip() for s in args.skot.split(",") if s.strip()]
    for s in skot:
        if s not in SKOT:
            raise SystemExit(f"ukjent skot: {s} (kjende: {', '.join(SKOT)})")
    if args.rask:
        prover = args.prover or 32
    else:
        prover = args.prover or 128
    print(f"{namn}: {len(sc['delar'])} delar · {len(sc.get('utstyr') or [])} utstyr · arbeid {am or '-'} · {prover} prøver", flush=True)
    tider, rammer = {}, {}
    def storleik(B, Hh):
        if args.breidd:
            return args.breidd, round(args.breidd * Hh / B)
        if args.rask:
            return 640, round(640 * Hh / B)
        return B, Hh
    dk = [s for s in skot if s in ("miljo-dag", "miljo-kveld")]
    if dk:
        b, h = storleik(1600, 1100)
        rammer.update({k: v for k, v in skot_miljo(sc, dk, args, ut, namn, b, h, prover, tider).items()})
    if "miljo-arbeid" in skot:
        b, h = storleik(1600, 1100)
        rammer["miljo-arbeid"] = skot_arbeid(sca or sc, args, ut, namn, b, h, prover, tider)
    if "modus" in skot:
        b, h = storleik(1440, 1000)
        rammer["modus"] = skot_modus([sc, sca] if sca else [sc], args, ut, namn, b, h, prover, tider)
    utanfor = [k for k, r in rammer.items() if min(r[0], r[2]) < -1 or max(r[1], r[3]) > 1]
    for k, v in KONTROLL.items():
        print(f"  {k:13s} " + " · ".join(f"{a} {b}" for a, b in v.items()), flush=True)
    print("  cpu-s " + " · ".join(f"{k} {v}" for k, v in CPU.items()), flush=True)
    for k, v in BILETE.items():
        print(f"  {k}: eksponering {EV.get(k)} EV · svart kant {', '.join(v['svart_kant']) or 'ingen'} · utbrent {v['klipt_pst']} %", flush=True)
    rapport = {"cpu_s": CPU, "ev": EV, "bilete": BILETE, "namn": namn, "mappe": sc["mappe"], "arbeid": am, "prover": prover, "tider": tider, "rammer": rammer, "utanfor": utanfor, "kontroll": KONTROLL, "s": round(time.time() - t0, 1)}
    json.dump(rapport, open(os.path.join(ut, f"{namn}-miljo.json"), "w"), indent=1)
    print(f"ferdig {rapport['s']} s · utanfor ramma: {', '.join(utanfor) or 'ingen'}", flush=True)
    return 0 if not utanfor else 3


if __name__ == "__main__":
    sys.exit(main())
