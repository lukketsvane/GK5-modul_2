# -*- coding: utf-8 -*-
"""mini_sprengt.py: sprengbilete av printdelane til Sveip mini med micro:bit V2 (mini_sprengt.png).

Kroppen står i midten. Lysplata kjem ned i skjermen ovanfrå, messingskruen inn framanfrå, og under
står chassiset, kortet og lysrista med lysleiarane, slik dei blir sette saman og skuva opp i stamma.
  python mini_sprengt.py [--prove]
"""
import math
import sys
import tempfile
from pathlib import Path

import cadquery as cq

import d15_lysrist as L15
import mini_print as MP
from mini_passform import kortdelar, til_lampa

HER = Path(__file__).resolve().parent
NED = -78.0                     # kor langt under lampa chassiset og kortet står

# del: (lekam, materiale, forskyving (x, y, z) i mm)
def delar():
    kort = kortdelar(MP.YK)
    led = cq.Workplane("XY")
    for u, v in L15.LED:
        led = led.union(cq.Workplane("XY").box(0.8, 1.6, 0.4).translate((u, v, 0.2)))
    hovud, skaft = MP.messingskrue()
    return {
        "kropp": (MP.kropp(), "kropp", (0, 0, 0)),
        "lysplate": (MP.lysplate(), "kvit", (0, 0, 42)),
        "skruehovud": (hovud, "messing", (0, -30, 0)),
        "skrueskaft": (skaft, "messing", (0, -30, 0)),
        "chassis": (MP.chassis(), "svart", (0, 16, NED)),
        "kretskort": (kort["kretskort"], "kort", (0, 0, NED)),
        "knapp A": (kort["knapp A"], "knapp", (0, 0, NED)),
        "knapp B": (kort["knapp B"], "knapp", (0, 0, NED)),
        "led": (til_lampa(led, MP.YK), "led", (0, 0, NED)),
        "lysrist": (kort["lysrist D15"], "svart", (0, -16, NED)),
        "lysleiarar": (MP.lysleiarar(), "leiar", (0, -16, NED)),
        "fjor": (MP.fjor(), "stal", (0, -8, NED)),
    }


def render(prove=False):
    import bpy
    from mathutils import Vector

    tmp = Path(tempfile.mkdtemp(prefix="sveip_mini_"))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 32 if prove else 160
    sc.cycles.use_denoising = True
    sc.render.resolution_x = sc.render.resolution_y = 1400
    sc.render.resolution_percentage = 45 if prove else 100
    sc.view_settings.view_transform = "AgX"
    sc.world = bpy.data.worlds.new("v")
    sc.world.use_nodes = True
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.55, 0.55, 1)
    sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.35

    def mat(nm, farge, rough=0.55, metal=0.0, lys=0.0, trans=0.0):
        m = bpy.data.materials.new(nm)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*farge, 1)
        b.inputs["Roughness"].default_value = rough
        b.inputs["Metallic"].default_value = metal
        if trans:
            b.inputs["Transmission Weight"].default_value = trans
        if lys:
            b.inputs["Emission Color"].default_value = (*farge, 1)
            b.inputs["Emission Strength"].default_value = lys
        return m

    mats = {
        "kropp": mat("kropp", (0.62, 0.61, 0.59), 0.62),
        "kvit": mat("kvit", (0.85, 0.84, 0.82), 0.6),
        "svart": mat("svart", (0.018, 0.018, 0.02), 0.5),
        "kort": mat("kort", (0.03, 0.035, 0.03), 0.35),
        "knapp": mat("knapp", (0.01, 0.01, 0.01), 0.4),
        "led": mat("led", (1.0, 0.02, 0.01), 0.4, lys=6.0),
        "leiar": mat("leiar", (0.95, 0.93, 0.88), 0.25, trans=0.6),
        "messing": mat("messing", (0.78, 0.56, 0.26), 0.28, 1.0),
        "stal": mat("stal", (0.7, 0.7, 0.72), 0.3, 1.0),
    }
    for nm, (form, m, (dx, dy, dz)) in delar().items():
        sti = tmp / f"{nm}.stl"
        cq.exporters.export(form.translate((dx, dy, dz)), str(sti), tolerance=0.02, angularTolerance=0.1)
        bpy.ops.wm.stl_import(filepath=str(sti), global_scale=0.001)
        o = bpy.context.selected_objects[0]
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30))
        except Exception:
            pass
        o.data.materials.append(mats[m])

    mal = Vector((0.040, 0.0, 0.010))
    cam = bpy.data.cameras.new("kam")
    cam.lens = 85
    co = bpy.data.objects.new("kam", cam)
    sc.collection.objects.link(co)
    retn = Vector((-0.42, -1.90, 0.62)).normalized()
    co.location = mal + retn * 0.58
    co.rotation_euler = (mal - co.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co
    for nm, pos, energi, storleik in (("nokkel", (-0.35, -0.45, 0.55), 14, 0.5), ("fyll", (0.5, -0.3, 0.1), 4, 0.6),
                                      ("bak", (0.1, 0.5, 0.4), 9, 0.4)):
        l = bpy.data.lights.new(nm, "AREA")
        l.energy, l.size = energi, storleik
        o = bpy.data.objects.new(nm, l)
        sc.collection.objects.link(o)
        o.location = Vector(pos)
        o.rotation_euler = (mal - o.location).to_track_quat("-Z", "Y").to_euler()
    ut = HER / f"mini_sprengt{'_prove' if prove else ''}.png"
    sc.render.filepath = str(ut)
    bpy.ops.render.render(write_still=True)
    print("SKREIV", ut)


if __name__ == "__main__":
    render(prove="--prove" in sys.argv)
