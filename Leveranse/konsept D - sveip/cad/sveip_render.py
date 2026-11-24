# -*- coding: utf-8 -*-
"""Rendring av Sveip i Blender 5.1 (Cycles). Køyr:
  blender.exe -b -P sveip_render.py -- samanlikn   (same kamera og bakgrunn som skissa)
  blender.exe -b -P sveip_render.py -- svart       (objektet åleine på svart, eitt lys)
  blender.exe -b -P sveip_render.py -- sprengt     (innmatsmodulen løfta ut av kroppen)
  blender.exe -b -P sveip_render.py -- lys         (stemningslys og arbeidslys på)
Legg til --prove for 1/3 oppløysing.
"""
import ctypes
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROT = Path(__file__).resolve().parent.parent
ARG = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MODUS = ARG[0] if ARG else "samanlikn"
PROVE = "--prove" in ARG


def skaansam():
    try:
        k = ctypes.windll.kernel32
        h = k.GetCurrentProcess()
        k.SetPriorityClass(h, 0x40)
        k.SetProcessAffinityMask(h, 0xFC)
    except Exception:
        pass


def tom_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    try:
        pref = bpy.context.preferences.addons["cycles"].preferences
        pref.compute_device_type = "CUDA"
        pref.get_devices()
        for d in pref.devices:
            d.use = d.type != "CPU"
        s.cycles.device = "GPU"
    except Exception:
        s.cycles.device = "CPU"
    s.render.threads_mode = "FIXED"
    s.render.threads = 4
    s.cycles.use_denoising = True
    s.cycles.adaptive_threshold = 0.015
    return s


def mat(namn, farge, rough=0.55, metal=0.0, emit=None, trans=0.0, sss=False):
    m = bpy.data.materials.new(namn)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*farge, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if trans:
        b.inputs["Transmission Weight"].default_value = trans
    if emit:
        b.inputs["Emission Color"].default_value = (*emit[0], 1.0)
        b.inputs["Emission Strength"].default_value = emit[1]
    # avrunda kantar i skyggjaren (0,4 mm)
    try:
        bev = nt.nodes.new("ShaderNodeBevel")
        bev.inputs["Radius"].default_value = 0.0004
        nt.links.new(bev.outputs["Normal"], b.inputs["Normal"])
    except Exception:
        pass
    return m


def lin(c):
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


def importer(geo, lys_paa=False, flytt_modul=0.0):
    objs = []
    kropp = mat("kropp", lin((0.80, 0.80, 0.79)), rough=0.62)
    alu = mat("alu", lin((0.78, 0.79, 0.80)), rough=0.35, metal=1.0)
    messing = mat("messing", lin((0.86, 0.68, 0.38)), rough=0.28, metal=1.0)
    svart = mat("svart", lin((0.05, 0.05, 0.05)), rough=0.5)
    kvit = mat("kvit", lin((0.93, 0.93, 0.92)), rough=0.5)
    pcb = mat("pcb", lin((0.08, 0.22, 0.12)), rough=0.4)
    staal = mat("staal", lin((0.6, 0.6, 0.62)), rough=0.3, metal=1.0)
    opal = mat("opal", lin((0.96, 0.96, 0.95)), rough=0.45,
               emit=(((1.0, 0.80, 0.58), 6.0) if lys_paa else None))
    opal_ned = mat("opal_ned", lin((0.96, 0.96, 0.95)), rough=0.45,
                   emit=(((1.0, 0.86, 0.68), 22.0) if lys_paa else None))
    led = mat("led", lin((0.95, 0.88, 0.55)), rough=0.3)
    celle = mat("celle", lin((0.20, 0.35, 0.65)), rough=0.4)
    m_for = {"D01": kropp, "D02": kropp, "D10": kropp, "D03": alu, "D04": pcb, "D05": pcb,
             "D09": pcb, "D11": pcb, "D14": pcb, "D04L": led, "D05L": led, "D06": kvit,
             "D07": opal_ned, "D08": opal, "D12F": messing, "D12B": messing, "D13F": svart,
             "D13B": svart, "K01": celle, "K02": svart, "K08": svart, "E01": svart,
             "D09K": svart, "D11J": kvit, "K18": kvit, "K05": kvit, "K20": messing}
    for d in geo["delar"]:
        sti = ROT / d["stl"]
        bpy.ops.wm.stl_import(filepath=str(sti), global_scale=0.001)
        o = bpy.context.selected_objects[0]
        o.name = d["id"]
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(28))
        except Exception:
            pass
        o.data.materials.append(m_for.get(d["id"], staal))
        if d["modul"] and flytt_modul:
            o.location.z += flytt_modul
        objs.append(o)
    return objs


def kamera(s, pos, maal, brennvidd=135, orto=None):
    c = bpy.data.cameras.new("kam")
    if orto:
        c.type = "ORTHO"
        c.ortho_scale = orto
    else:
        c.lens = brennvidd
    o = bpy.data.objects.new("kam", c)
    s.collection.objects.link(o)
    o.location = Vector(pos)
    retn = Vector(maal) - Vector(pos)
    o.rotation_euler = retn.to_track_quat("-Z", "Y").to_euler()
    s.camera = o
    return o


def areal(s, namn, pos, maal, storleik, energi, farge=(1, 1, 1)):
    l = bpy.data.lights.new(namn, "AREA")
    l.size = storleik
    l.energy = energi
    l.color = farge
    o = bpy.data.objects.new(namn, l)
    s.collection.objects.link(o)
    o.location = Vector(pos)
    o.rotation_euler = (Vector(maal) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    return o


def golv(s, farge, rough=0.9, z=-0.003):
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, z))
    g = bpy.context.active_object
    g.data.materials.append(mat("golv", farge, rough=rough))
    return g


def verd(s, farge, styrke=1.0):
    w = bpy.data.worlds.new("verd")
    s.world = w
    try:
        w.use_nodes = True
    except Exception:
        pass
    bg = w.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (*farge, 1.0)
    bg.inputs["Strength"].default_value = styrke


def main():
    skaansam()
    s = tom_scene()
    geo = json.loads((ROT / "render" / "geometri.json").read_text(encoding="utf-8"))
    geo["delar"] = [d for d in geo["delar"] if d["id"] != "E01" or MODUS in ("samanlikn", "svart")]
    px = (1000, 1000)
    if MODUS == "samanlikn":
        importer(geo)
        s.view_settings.view_transform = "Standard"
        s.render.film_transparent = True
        verd(s, (1.0, 1.0, 1.0), 0.35)
        g = golv(s, (0.8, 0.8, 0.8), rough=1.0)
        g.is_shadow_catcher = True
        # kamera som i skissa: om lag 2 m frå framflata, 43 cm over bordet, 135 mm
        kamera(s, (0.150, -2.011, 0.430), (0.150, 0.0, 0.147), 135)
        areal(s, "nokkel", (-0.9, -1.6, 1.4), (0.15, 0, 0.15), 1.6, 22)
        areal(s, "fyll", (1.6, -1.2, 0.6), (0.15, 0, 0.15), 2.0, 5)
        s.cycles.samples = 96 if PROVE else 256
    elif MODUS in ("svart", "lys"):
        importer(geo, lys_paa=(MODUS == "lys"))
        s.view_settings.view_transform = "AgX"
        try:
            s.view_settings.look = "AgX - Medium High Contrast"
        except Exception:
            pass
        verd(s, (0, 0, 0), 0.0)
        golv(s, (0.02, 0.02, 0.02), rough=0.35)
        kamera(s, (-0.62, -1.45, 0.62), (0.150, 0.0, 0.140), 105)
        if MODUS == "svart":
            areal(s, "nokkel", (-0.5, -0.9, 1.3), (0.15, 0, 0.15), 1.2, 520)
            areal(s, "kant", (1.2, 0.9, 0.7), (0.15, 0, 0.18), 0.8, 160, (0.85, 0.9, 1.0))
        else:
            areal(s, "svak", (-0.5, -0.9, 1.3), (0.15, 0, 0.15), 1.2, 25)
        px = (1600, 1200)
        s.cycles.samples = 96 if PROVE else 384
    elif MODUS == "sprengt":
        importer(geo, flytt_modul=0.33)
        s.view_settings.view_transform = "Standard"
        s.render.film_transparent = True
        verd(s, (1.0, 1.0, 1.0), 0.35)
        g = golv(s, (0.8, 0.8, 0.8), rough=1.0)
        g.is_shadow_catcher = True
        kamera(s, (-1.30, -2.40, 1.50), (0.150, 0.0, 0.32), 85)
        areal(s, "nokkel", (-0.9, -1.6, 1.8), (0.15, 0, 0.3), 1.8, 30)
        areal(s, "fyll", (1.6, -1.2, 0.9), (0.15, 0, 0.3), 2.0, 6)
        px = (1200, 1500)
        s.cycles.samples = 96 if PROVE else 256
    s.render.resolution_x, s.render.resolution_y = px
    s.render.resolution_percentage = 34 if PROVE else 100
    ut = ROT / "render" / f"sveip_{MODUS}{'_prove' if PROVE else ''}.png"
    s.render.filepath = str(ut)
    s.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    if s.render.film_transparent:
        # legg på den lysgrå bakgrunnen frå skissa (239, 239, 239)
        img = bpy.data.images.load(str(ut))
        w, h = img.size
        px_ = list(img.pixels)
        bgc = 239 / 255.0
        for i in range(0, len(px_), 4):
            a_ = px_[i + 3]
            for c in range(3):
                px_[i + c] = px_[i + c] * a_ + bgc * (1 - a_)
            px_[i + 3] = 1.0
        img.pixels = px_
        img.filepath_raw = str(ut)
        img.file_format = "PNG"
        img.save()
    print("SKREIV", ut)


main()
