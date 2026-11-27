# -*- coding: utf-8 -*-
"""skal_render.py: rendrar eit skal frå print/<namn>.stl som printa PLA, med same kamera og lys
som overflatestudiane i ../../overflate (sveip_hud.render). Lampa blir skalert opp til storleiken
til rev. B (300 mm), så biletutsnittet blir det same.

Køyr frå skal/:
    python3 skal_render.py <namn> [--naer] [--prove] [--farge mork]
Skriv bilete/<namn>.png (eller <namn>_naer.png). Matrisa lyser som i V12 (skjermen 6, stamma 3).
"""
import math
import sys
from pathlib import Path

import numpy as np

HER = Path(__file__).resolve().parent
sys.path.insert(0, str(HER.parent))

import mini_print as MP                          # noqa: E402
from mini_passform import D, K, S                 # noqa: E402

FARGAR = {"lys": (0.79, 0.78, 0.76), "mork": (0.19, 0.19, 0.20), "kvit": (0.93, 0.92, 0.89)}


def les_stl(sti):
    data = np.fromfile(sti, dtype=np.uint8)
    n = int(np.frombuffer(data[80:84].tobytes(), dtype="<u4")[0])
    rec = np.frombuffer(data[84:84 + 50 * n].tobytes(), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("x", "<u2")])
    v = rec["v"].reshape(-1, 3).astype(np.float64)
    nokkel, inv = np.unique(np.round(v, 5), axis=0, return_inverse=True)
    return nokkel, inv.reshape(-1, 3)


def render(namn, naer=False, prove=False, farge="lys"):
    import bpy
    from mathutils import Vector

    v, t = les_stl(HER / "print" / f"{namn}.stl")
    skala = 1.0 / (1000.0 * K)                        # mm i mini til meter i rev. B-storleik

    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.render.threads_mode = "FIXED"
    sc.render.threads = 4
    sc.cycles.use_denoising = True
    sc.cycles.adaptive_threshold = 0.015
    sc.cycles.samples = 48 if prove else 192
    sc.cycles.max_bounces = 6
    sc.render.resolution_x = sc.render.resolution_y = 1200
    sc.render.resolution_percentage = 50 if prove else 100
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass

    def lin(c):
        return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)

    def materiale(nm, farge_, rough, metal=0.0, emisjon=None):
        mt = bpy.data.materials.new(nm)
        mt.use_nodes = True
        bs = mt.node_tree.nodes.get("Principled BSDF")
        bs.inputs["Base Color"].default_value = (*lin(farge_), 1.0)
        bs.inputs["Roughness"].default_value = rough
        bs.inputs["Metallic"].default_value = metal
        if emisjon:
            bs.inputs["Emission Color"].default_value = (*emisjon[0], 1.0)
            bs.inputs["Emission Strength"].default_value = emisjon[1]
        return mt

    me = bpy.data.meshes.new(namn)
    me.from_pydata((v * skala).tolist(), [], t.tolist())
    me.update()
    ob = bpy.data.objects.new(namn, me)
    sc.collection.objects.link(ob)
    ob.data.materials.append(materiale("pla", FARGAR[farge], 0.62))
    for p in me.polygons:
        p.use_smooth = False

    # messingskruen (linsehovud) og LED-ane bak hola
    yf = (-D / 2 + MP.FELT_DJUPN) * skala
    bpy.ops.mesh.primitive_uv_sphere_add(radius=2.8 * skala, location=(MP.LOGO[0] * skala, yf, MP.LOGO[1] * skala),
                                         segments=48, ring_count=24)
    kule = bpy.context.object
    kule.scale = (1.0, 2.4 / 2.8, 1.0)
    kule.data.materials.append(materiale("messing", (0.80, 0.62, 0.32), 0.28, 1.0))
    for p in kule.data.polygons:
        p.use_smooth = True
    nivaa = [6, 6, 3, 3, 3]                        # rad ovanfrå: skjermen 6, stamma 3 (kolonne 0–2)
    raud = lin((1.0, 0.10, 0.05))
    for (x, z) in MP.led_lampa():
        kol = round((x - MP.MX) / 4) + 2
        rad = round((MP.MZ - z) / 4) + 2
        n = nivaa[rad] if (rad < 2 or kol < 3) else 0
        if n == 0:
            continue
        bpy.ops.mesh.primitive_cylinder_add(radius=0.95 * skala, depth=0.3 * skala,
                                            location=(x * skala, (-D / 2 + MP.T - 0.2) * skala, z * skala),
                                            rotation=(math.pi / 2, 0, 0), vertices=24)
        bpy.context.object.data.materials.append(materiale(f"led{x:.0f}{z:.0f}", (1, 0.2, 0.1), 0.5,
                                                           emisjon=(raud, 1.5 * 2 ** (n - 6))))
    # innsida: mørk botn i stamma, så hola les som hol
    bpy.ops.mesh.primitive_cube_add(size=1, location=(25 * skala, 0, 20 * skala))
    blokk = bpy.context.object
    blokk.scale = (40 * skala, 22 * skala, 38 * skala)
    blokk.data.materials.append(materiale("inni", (0.02, 0.02, 0.02), 0.9))

    M = Vector((0.150, 0.0, 0.146))
    cam = bpy.data.cameras.new("kam")
    cam.lens = 165
    co = bpy.data.objects.new("kam", cam)
    sc.collection.objects.link(co)
    co.location = Vector((-0.27, -1.90, 0.64))
    co.rotation_euler = (M - co.location).to_track_quat("-Z", "Y").to_euler()
    if naer:      # skrått inn mot hjørnet under skjermen og nasen: der overflata møtest
        cam.lens = 120
        co.location = Vector((0.62, -1.15, 0.52))
        sikt = Vector((0.205, -0.04, 0.165))
        co.rotation_euler = (sikt - co.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co

    def flate(nm, pos, storleik, energi, farge_=(1, 1, 1), form=None, maal=None):
        l = bpy.data.lights.new(nm, "AREA")
        if form:
            l.shape = "RECTANGLE"
            l.size, l.size_y = form
        else:
            l.size = storleik
        l.energy = energi
        l.color = farge_
        o = bpy.data.objects.new(nm, l)
        sc.collection.objects.link(o)
        o.location = Vector(pos)
        o.rotation_euler = ((Vector(maal) if maal else M) - o.location).to_track_quat("-Z", "Y").to_euler()

    flate("nokkel", (-1.30, -1.30, 1.05), 1.9, 88)
    flate("stripe", (-1.9, -0.25, 0.30), 0, 30, form=(0.35, 1.6))
    flate("front", (-0.15, -2.5, -0.15), 0, 15, form=(1.6, 1.2))
    flate("nase", (1.75, 0.10, -0.10), 0, 30, form=(0.45, 1.5))
    flate("kant", (1.25, 0.95, 0.95), 0, 26, (0.90, 0.94, 1.0), form=(0.4, 1.4))
    flate("topp", (0.15, -0.2, 1.7), 1.2, 10)
    flate("inni", (0.150, 0.0, 0.222), 0, 0.22, (1.0, 0.80, 0.58), form=(0.24, 0.07), maal=(0.150, 0.0, 0.5))
    w = bpy.data.worlds.new("verd")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes.get("Background").inputs["Color"].default_value = (0, 0, 0, 1)
    w.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.0

    ut = HER / "bilete"
    ut.mkdir(exist_ok=True)
    fil = ut / f"{namn}{'_naer' if naer else ''}{'_' + farge if farge != 'lys' else ''}{'_prove' if prove else ''}.png"
    sc.render.filepath = str(fil)
    sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    return fil


if __name__ == "__main__":
    a = sys.argv[1:]
    farge = a[a.index("--farge") + 1] if "--farge" in a else "lys"
    print(render(a[0], naer="--naer" in a, prove="--prove" in a, farge=farge))
