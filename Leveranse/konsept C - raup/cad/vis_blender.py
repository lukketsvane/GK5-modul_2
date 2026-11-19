# -*- coding: utf-8 -*-
"""vis_blender.py · Nøytrale kontrollrendringar av den FAKTISKE CAD-modellen i Cycles.

    "C:/Program Files/Blender Foundation/Blender 5.3/blender.exe" -b -P cad/vis_blender.py -- [--prove]

Skriv:
  - render/cad_skal_botn.png  (ope-botn skal sett skrått nedanfrå — direkte samanlikning med Bambu Studio)
  - render/cad_skal_snitt.png (snitt gjennom hovudskalet som syner jamn 4 mm vegg og glatt kuppel)
  - render/cad_modell.png     (komplett samanstilling frå front 3/4)
  - render/cad_bak.png        (komplett samanstilling bakfrå med innsprang, botnchassis og diffusorfot)
"""
import math
import os
import sys
import bpy
from mathutils import Vector

try:
    import ctypes
    k = ctypes.windll.kernel32
    h = k.GetCurrentProcess()
    k.SetPriorityClass(h, 0x40)
    k.SetProcessAffinityMask(h, 0xFC)
except Exception:
    pass

ARG = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PROVE = "--prove" in ARG
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(R, "produksjon")
UT = os.path.join(R, "render")


def nullstill(bg=(0.04, 0.04, 0.045)):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.render.threads_mode = "FIXED"
    s.render.threads = 6
    s.cycles.samples = 24 if PROVE else 64
    s.cycles.use_denoising = True
    s.render.resolution_x, s.render.resolution_y = (800, 800) if PROVE else (1200, 1200)
    s.render.film_transparent = False
    s.view_settings.view_transform = "AgX"
    w = bpy.data.worlds.new("w")
    s.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (*bg, 1.0)
    return s


def mat(namn, farge, ruheit=0.55, metal=0.0, trans=0.0, emisjon=0.0):
    m = bpy.data.materials.new(namn)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*farge, 1.0)
    p.inputs["Roughness"].default_value = ruheit
    p.inputs["Metallic"].default_value = metal
    p.inputs["Transmission Weight"].default_value = trans
    if emisjon:
        p.inputs["Emission Color"].default_value = (1.0, 0.78, 0.50, 1.0)
        p.inputs["Emission Strength"].default_value = emisjon
    return m


def last(fil, m, dz_mm=0.0):
    fp = os.path.join(P, fil)
    if not os.path.exists(fp):
        return None
    bpy.ops.wm.stl_import(filepath=fp)
    o = bpy.context.selected_objects[0]
    o.scale = (0.001, 0.001, 0.001)
    o.location = (0.0, 0.0, dz_mm * 0.001)
    o.data.materials.append(m)
    bpy.ops.object.shade_auto_smooth(angle=math.radians(32))
    return o


def lys_og_kamera(s, mal, avstand, azimut, elev, linse=55, underlys=False):
    lys = [
        ("nokkel", (-0.50, -0.55, 0.55), 140, 0.55),
        ("kant", (0.55, 0.45, 0.45), 95, 0.45),
        ("fyll", (0.55, -0.55, 0.15), 35, 0.85),
    ]
    if underlys:
        lys.append(("botn", (0.0, -0.25, -0.55), 110, 0.55))
    for namn, pos, e, storleik in lys:
        d = bpy.data.lights.new(namn, "AREA")
        d.energy = e
        d.size = storleik
        o = bpy.data.objects.new(namn, d)
        o.location = pos
        o.rotation_euler = (Vector(mal) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
        s.collection.objects.link(o)
    kd = bpy.data.cameras.new("kam")
    kd.lens = linse
    k = bpy.data.objects.new("kam", kd)
    s.collection.objects.link(k)
    s.camera = k
    a, e = math.radians(azimut), math.radians(elev)
    k.location = Vector(mal) + avstand * Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    k.rotation_euler = (Vector(mal) - k.location).to_track_quat("-Z", "Y").to_euler()


def golv(s):
    bpy.ops.mesh.primitive_plane_add(size=4)
    g = bpy.context.active_object
    g.data.materials.append(mat("golv", (0.08, 0.08, 0.085), 0.75))


def render(s, namn):
    suffix = "-prove" if PROVE else ""
    s.render.filepath = os.path.join(UT, namn + suffix + ".png")
    bpy.ops.render.render(write_still=True)
    print("skreiv", s.render.filepath, flush=True)


# 1. Hovudskalet sett skrått nedanfrå (samanlikningsvinkel med Bambu Studio-skjermbiletet!)
s = nullstill(bg=(0.14, 0.14, 0.15))
o_skal = last("raup_skal_P1S.stl", mat("pla_lys", (0.76, 0.75, 0.73), 0.42))
lys_og_kamera(s, (0.0, 0.005, 0.09), 0.56, 15, -42, linse=50, underlys=True)
render(s, "cad_skal_botn")

# 2. Snitt gjennom hovudskalet (syner jamn 4 mm vegg over kuppel, skulder, innsprang og botn)
s = nullstill(bg=(0.05, 0.05, 0.06))
golv(s)
snitt_m = mat("snitt", (0.72, 0.28, 0.16), 0.5)
o = last("raup_skal_P1S.stl", mat("skal", (0.82, 0.79, 0.74), 0.65))
bpy.context.view_layer.objects.active = o
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
cy = 0.052  # skjer gjennom bakre buk og det 51 mm innspranget!
bpy.ops.mesh.bisect(plane_co=(0, cy, 0), plane_no=(0, -1, 0), use_fill=True, clear_inner=False, clear_outer=True)
bpy.ops.object.mode_set(mode="OBJECT")
o.data.materials.append(snitt_m)
for poly in o.data.polygons:
    if abs(poly.normal.y) > 0.99 and abs((o.matrix_world @ poly.center).y - cy) < 2e-4:
        poly.material_index = 1
lys_og_kamera(s, (0.01, cy, 0.10), 0.62, -12, 14, linse=55)
render(s, "cad_skal_snitt")

# 3. Komplett samanstilling front 3/4 (hovudskal på botnchassis + diffusor + LED + klips)
def last_samanstilling():
    last("raup_skal_P1S.stl", mat("papir", (0.84, 0.80, 0.74), 0.78), dz_mm=3.5)
    last("raup_botn_chassis.stl", mat("chassis", (0.20, 0.20, 0.22), 0.40, metal=0.7))
    last("raup_led_berar.stl", mat("led_alu", (0.85, 0.83, 0.80), 0.35, metal=0.8, emisjon=1.2))
    last("raup_diffusor.stl", mat("film", (0.96, 0.94, 0.90), 0.25, trans=0.72))
    last("raup_filmklips.stl", mat("klips", (0.25, 0.25, 0.28), 0.45))

s = nullstill(bg=(0.04, 0.04, 0.045))
golv(s)
last_samanstilling()
lys_og_kamera(s, (0.01, -0.01, 0.13), 0.72, -32, 16, linse=60)
render(s, "cad_modell")

# 4. Komplett samanstilling bak-høgre 3/4 (syner reint innsprang, botnchassis og diffusorfot)
s = nullstill(bg=(0.04, 0.04, 0.045))
golv(s)
last_samanstilling()
lys_og_kamera(s, (0.01, 0.01, 0.13), 0.72, 138, 14, linse=60)
render(s, "cad_bak")
