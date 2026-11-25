# -*- coding: utf-8 -*-
"""FYR · Cycles-rendering av CAD-en (Blender 5.1, hovudlaust).

    py -3 cad/fyr_render_eksport.py <stl_mappe> [theta]      # først: STL per del og scene.json (theta 0 = open, 90 = av)
    blender.exe -b -P cad/fyr_render.py -- <stl_mappe> <ut.png> <scene> [--prove]

Scener:
  helt     lampa lyser, 3/4 ovanfrå som skissa, strålar på bordet, mørkt studio (eksport med theta 0)
  av       lampa slokt, produktlys (eksport med theta 90: spaltene er stengde, messingen syner i dei)
  krage    nærbilete av messingkragen og toppen
  ovanfra  rett ovanfrå: loket og krona
Lyskjeldene i lampa er flatelys på plassen til LED-stripene (rett fysisk veg gjennom rista og spaltene).
"""
import ctypes
import json
import math
import os
import sys

import bpy
from mathutils import Vector

try:
    k = ctypes.windll.kernel32
    h = k.GetCurrentProcess()
    k.SetPriorityClass(h, 0x40)
    k.SetProcessAffinityMask(h, 0xFC)
except Exception:
    pass

ARGS = sys.argv[sys.argv.index("--") + 1:]
STL, OUT, SCENE = ARGS[0], ARGS[1], ARGS[2]
if SCENE not in ("helt", "av", "krage", "ovanfra"):
    raise SystemExit(f"ukjend scene {SCENE!r} (stiar med mellomrom må setjast i hermeteikn): {ARGS}")
PROVE = "--prove" in ARGS
INFO = json.load(open(os.path.join(STL, "scene.json"), encoding="utf-8"))
MM = 0.001

bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
s.render.engine = "CYCLES"
try:
    pr = bpy.context.preferences.addons["cycles"].preferences
    pr.compute_device_type = "CUDA"
    pr.get_devices()
    for d in pr.devices:
        d.use = d.type != "CPU"
    s.cycles.device = "GPU"
except Exception:
    s.cycles.device = "CPU"
s.render.threads_mode = "FIXED"
s.render.threads = 4
RX, RY = (2256, 1600) if SCENE != "ovanfra" else (1600, 1600)
if PROVE:
    RX, RY = RX // 3, RY // 3
s.render.resolution_x, s.render.resolution_y = RX, RY
s.cycles.samples = 96 if PROVE else 640
s.cycles.use_adaptive_sampling = True
s.cycles.adaptive_threshold = 0.01
s.cycles.use_denoising = True
s.cycles.denoiser = "OPENIMAGEDENOISE"
s.cycles.sample_clamp_indirect = 6.0
s.cycles.max_bounces = 12
s.cycles.diffuse_bounces = 5
s.cycles.glossy_bounces = 6
s.cycles.transmission_bounces = 10
s.view_settings.view_transform = "AgX"
s.view_settings.look = "AgX - Medium High Contrast"
s.view_settings.exposure = 0.0
w = bpy.data.worlds.new("verd")
s.world = w
w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0, 0, 0, 1)
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0


# ------------------------------------------------------------------ material
def ny(n):
    m = bpy.data.materials.new(n)
    m.use_nodes = True
    return m, m.node_tree, m.node_tree.nodes["Principled BSDF"]


def kant(nt, r):
    b = nt.nodes.new("ShaderNodeBevel")
    b.samples = 6
    b.inputs["Radius"].default_value = r
    return b.outputs["Normal"]


def lakk(farge, ru=0.55):
    """Fin strukturlakk (pulverlakk RAL 3005-ish)."""
    m, nt, p = ny("lakk")
    p.inputs["Base Color"].default_value = (*farge, 1)
    p.inputs["Roughness"].default_value = ru
    p.inputs["Specular IOR Level"].default_value = 0.35
    tc = nt.nodes.new("ShaderNodeTexCoord")
    st = nt.nodes.new("ShaderNodeTexNoise")
    st.inputs["Scale"].default_value = 2200.0
    st.inputs["Detail"].default_value = 3.0
    nt.links.new(tc.outputs["Object"], st.inputs["Vector"])
    bu = nt.nodes.new("ShaderNodeBump")
    bu.inputs["Strength"].default_value = 0.28
    bu.inputs["Distance"].default_value = 0.00004
    nt.links.new(st.outputs[0], bu.inputs["Height"])
    nt.links.new(kant(nt, 0.0004), bu.inputs["Normal"])
    nt.links.new(bu.outputs["Normal"], p.inputs["Normal"])
    return m


def messing():
    """Børsta messing, rundtgåande børsting (tangent rundt z-aksen)."""
    m, nt, p = ny("messing")
    p.inputs["Base Color"].default_value = (0.80, 0.56, 0.24, 1)
    p.inputs["Metallic"].default_value = 1.0
    p.inputs["Roughness"].default_value = 0.30
    p.inputs["Anisotropic"].default_value = 0.85
    ta = nt.nodes.new("ShaderNodeTangent")
    ta.direction_type = "RADIAL"
    ta.axis = "Z"
    tt = nt.nodes.new("ShaderNodeVectorMath")
    tt.operation = "ADD"
    tt.inputs[1].default_value = (0.0, 0.0, 0.003)
    nt.links.new(ta.outputs["Tangent"], tt.inputs[0])
    nt.links.new(tt.outputs["Vector"], p.inputs["Tangent"])
    # fine børsteriper
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    noi = nt.nodes.new("ShaderNodeTexNoise")
    noi.inputs["Scale"].default_value = 9000.0
    nt.links.new(sep.outputs["Z"], noi.inputs["Vector"])
    bu = nt.nodes.new("ShaderNodeBump")
    bu.inputs["Strength"].default_value = 0.08
    bu.inputs["Distance"].default_value = 0.00002
    nt.links.new(noi.outputs[0], bu.inputs["Height"])
    nt.links.new(kant(nt, 0.0002), bu.inputs["Normal"])
    nt.links.new(bu.outputs["Normal"], p.inputs["Normal"])
    return m


def plast(farge, ru=0.5, sss=0.0):
    m, nt, p = ny("plast")
    p.inputs["Base Color"].default_value = (*farge, 1)
    p.inputs["Roughness"].default_value = ru
    if sss:
        p.inputs["Subsurface Weight"].default_value = sss
        p.inputs["Subsurface Radius"].default_value = (2.0, 1.6, 1.2)
        p.inputs["Subsurface Scale"].default_value = 0.0015
    return m


def opal():
    m, nt, p = ny("opal")
    p.inputs["Base Color"].default_value = (0.95, 0.93, 0.90, 1)
    p.inputs["Roughness"].default_value = 0.45
    p.inputs["Transmission Weight"].default_value = 0.0
    p.inputs["Subsurface Weight"].default_value = 1.0
    p.inputs["Subsurface Radius"].default_value = (6.0, 5.0, 4.0)
    p.inputs["Subsurface Scale"].default_value = 0.004
    p.inputs["IOR"].default_value = 1.49
    return m


def metall(farge, ru=0.35):
    m, nt, p = ny("metall")
    p.inputs["Base Color"].default_value = (*farge, 1)
    p.inputs["Metallic"].default_value = 1.0
    p.inputs["Roughness"].default_value = ru
    return m


def led_mat(styrke):
    m, nt, p = ny("led")
    p.inputs["Base Color"].default_value = (1.0, 0.85, 0.6, 1)
    p.inputs["Emission Color"].default_value = (1.0, 0.70, 0.40, 1)
    p.inputs["Emission Strength"].default_value = styrke
    return m


LYS_PA = SCENE != "av"
OKSEBLOD = (0.105, 0.016, 0.020)
MAT = {
    "01_fot": lakk(OKSEBLOD),
    "04_mantel": lakk(OKSEBLOD),
    "05_hylse": messing(),
    "05b_hylsefot": plast((0.02, 0.02, 0.02), 0.6),
    "05c_stoppskruar": metall((0.3, 0.3, 0.32)),
    "03_chassis": plast((0.02, 0.02, 0.022), 0.6),
    "06_lysstav": metall((0.8, 0.8, 0.82), 0.4),
    "06b_led_side": led_mat(8.0 if LYS_PA else 0.0),
    "06c_led_topp": led_mat(8.0 if LYS_PA else 0.0),
    "06d_kontakt": plast((0.05, 0.05, 0.05)),
    "07_lysrist": plast((0.92, 0.90, 0.86), 0.55, sss=0.25),
    "08_lok": opal(),
    "10_glidering": plast((0.01, 0.01, 0.01), 0.7),
    "11_oring": plast((0.01, 0.01, 0.01), 0.8),
    "12_brytarar": plast((0.05, 0.05, 0.3)),
}

lampe = bpy.data.collections.new("lampe")
s.collection.children.link(lampe)
for namn, m in MAT.items():
    fil = os.path.join(STL, namn + ".stl")
    if not os.path.exists(fil):
        continue
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.stl_import(filepath=fil, global_scale=MM)
    ob = bpy.context.selected_objects[0]
    ob.name = namn
    ob.data.materials.clear()
    ob.data.materials.append(m)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    try:
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(25))
    except Exception:
        pass
    for c in ob.users_collection:
        c.objects.unlink(ob)
    lampe.objects.link(ob)


# ------------------------------------------------------------------ lys
def peik(ob, maal):
    ob.rotation_euler = (Vector(maal) - ob.location).to_track_quat("-Z", "Y").to_euler()


def flatelys(n, pos, retning, bx, by, W, farge=(1.0, 0.74, 0.46)):
    ld = bpy.data.lights.new(n, "AREA")
    ld.shape = "RECTANGLE"
    ld.size = bx
    ld.size_y = by
    ld.energy = W
    ld.color = farge
    ob = bpy.data.objects.new(n, ld)
    s.collection.objects.link(ob)
    ob.location = pos
    peik(ob, (pos[0] + retning[0], pos[1] + retning[1], pos[2] + retning[2]))
    return ob


if LYS_PA:
    st = INFO["stripe"]
    zc = (st["z0"] + st["z1"]) / 2 * MM
    # sidestripa: lysflate 0,1 mm framfor stripa, peikar mot +X
    # peik() legg lokal Y opp (global z): size = breidd (8 mm), size_y = lengd langs z
    flatelys("led_side", ((st["x"] + 0.15) * MM, 0, zc), (1, 0, 0), st["b"] * MM, (st["z1"] - st["z0"]) * MM, 7.0)
    tp = INFO["topp"]
    for i in range(tp.get("n", 1)):
        a = math.radians(45.0 + i * 360.0 / tp.get("n", 1))
        ld = bpy.data.lights.new(f"led_topp{i}", "AREA")
        ld.shape = "RECTANGLE"
        ld.size = tp["b"] * MM
        ld.size_y = tp["l"] * MM
        ld.energy = 1.4 / tp.get("n", 1)
        ld.color = (1.0, 0.74, 0.46)
        ob = bpy.data.objects.new(f"led_topp{i}", ld)
        s.collection.objects.link(ob)
        r_ = tp.get("r", 0.0)
        ob.location = (r_ * math.cos(a) * MM, r_ * math.sin(a) * MM, (tp["z"] + 0.15) * MM)
        ob.rotation_euler = (math.pi, 0.0, a)     # lyser opp, lang side tangentielt

# rom: golv og vegg, mørkt og varmt
bpy.ops.mesh.primitive_plane_add(size=6.0)
golv = bpy.context.object
gm, gnt, gp = ny("golv")
gp.inputs["Base Color"].default_value = (0.16, 0.13, 0.11, 1) if SCENE != "av" else (0.03, 0.028, 0.027, 1)
gp.inputs["Roughness"].default_value = 0.62
golv.data.materials.append(gm)
# vegg bak lampa, vinkelrett på kameraretninga (kameraet står på asimut +35°)
bpy.ops.mesh.primitive_plane_add(size=6.0, location=(-0.45 * math.cos(math.radians(35)), -0.45 * math.sin(math.radians(35)), 3.0),
                                 rotation=(math.radians(90), 0, math.radians(35 + 90)))
vegg = bpy.context.object
vm, vnt, vp = ny("vegg")
vp.inputs["Base Color"].default_value = (0.12, 0.095, 0.085, 1)
vp.inputs["Roughness"].default_value = 0.9
vegg.data.materials.append(vm)

H = INFO["hogd"] * MM
if SCENE == "av":
    flatelys("nokkel", (0.55, -0.75, 0.75), (-0.55, 0.75, -0.62), 0.9, 0.5, 60.0, (1.0, 0.97, 0.93))
    flatelys("kant", (-0.5, 0.6, 0.5), (0.5, -0.6, -0.4), 0.5, 0.8, 25.0, (0.9, 0.93, 1.0))
else:
    # svakt fyll så forma les seg, utan å drukne lyset frå lampa
    flatelys("fyll", (1.1, 0.9, 0.9), (-1.1, -0.9, -0.75), 1.2, 1.2, 9.0, (1.0, 0.90, 0.80))
    flatelys("kant", (-0.6, 0.7, 0.7), (0.6, -0.7, -0.5), 0.6, 0.9, 5.0, (1.0, 0.86, 0.72))

# ------------------------------------------------------------------ kamera
kam = bpy.data.cameras.new("kam")
ko = bpy.data.objects.new("kam", kam)
s.collection.objects.link(ko)
s.camera = ko
if SCENE in ("helt", "av"):
    kam.lens = 105
    # vindauget (+X) vender litt mot venstre i biletet, som i skissa
    az = math.radians(35.0)
    el = math.radians(24.0)
    dist = 2.05
    tgt = Vector((0.02, 0.07, H * 0.33))
    ko.location = tgt + Vector((dist * math.cos(el) * math.cos(az), dist * math.cos(el) * math.sin(az), dist * math.sin(el)))
    peik(ko, tgt)
    ko.location = ko.location + Vector((0.0, 0.0, 0.0))
elif SCENE == "krage":
    kam.lens = 135
    az = math.radians(30.0)
    el = math.radians(28.0)
    dist = 0.62
    tgt = Vector((0.0, 0.0, H * 0.86))
    ko.location = tgt + Vector((dist * math.cos(el) * math.cos(az), dist * math.cos(el) * math.sin(az), dist * math.sin(el)))
    peik(ko, tgt)
elif SCENE == "ovanfra":
    kam.type = "ORTHO"
    kam.ortho_scale = 0.13
    ko.location = (0.0, 0.0, H + 0.6)
    ko.rotation_euler = (0, 0, math.radians(90))
s.render.film_transparent = False
s.render.image_settings.file_format = "PNG"
s.render.image_settings.color_mode = "RGB"
s.render.image_settings.color_depth = "8"
s.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("RENDER OK", OUT)
