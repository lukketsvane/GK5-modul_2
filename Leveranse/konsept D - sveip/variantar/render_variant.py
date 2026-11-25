# -*- coding: utf-8 -*-
"""Felles rendring for Sveip-variantane (Blender som Python-modul, `pip install bpy`).

Same kamera, lys og bakgrunn for alle variantar, så bileta kan samanliknast.
Køyr frå variantar/<id>/cad/:
  python ../../render_variant.py front trekvart svart lys topp naer [--kvalitet prove|variant|full]

Les   <variant>/render/geometri.json og STL-ane han peikar på (skrivne av sveip_produksjon.py)
      <variant>/render/materialar.json (valfri): {"D01": "kropp", "H01": {"type": "hud", "farge": [..], "trans": 0.5}, ...}
Skriv <variant>/render/<id>_<vising>.png

Visingar:
  front     rett framfrå på lys grå, som produktfotoet
  trekvart  tre kvart framfrå på lys grå, streiflys som syner flata
  svart     tre kvart på svart, eitt lys
  lys       begge lysa på i mørke
  topp      ovanfrå og ned i den opne toppen
  naer      nærbilete av nasen: toppkant, saum, underkant av skjermen
  plate     éin lampe i matt sølv på heilt svart (#000), utan golv: grunnlag for overflatestudiar
Materialnamn: kropp, kropp_inn, alu, alu_borsta, messing, svart, kvit, pcb, staal, opal, opal_ned, led, celle, hud
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ARG = [a for a in sys.argv[1:] if a != "--"]
KVAL = "variant"
if "--kvalitet" in ARG:
    i = ARG.index("--kvalitet")
    KVAL = ARG[i + 1]
    del ARG[i:i + 2]
ROT = Path.cwd().parent if Path.cwd().name == "cad" else Path.cwd()
if "--rot" in ARG:
    i = ARG.index("--rot")
    ROT = Path(ARG[i + 1]).resolve()
    del ARG[i:i + 2]
VISINGAR = ARG or ["front", "trekvart", "svart", "lys", "topp", "naer"]
PROSENT, PROVER = {"prove": (34, 48), "variant": (75, 128), "full": (100, 320)}[KVAL]
BG = 239 / 255.0


def lin(c):
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


def tom_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.render.threads_mode = "FIXED"
    s.render.threads = 4
    s.cycles.use_denoising = True
    s.cycles.adaptive_threshold = 0.02
    return s


def mat(namn, farge, rough=0.55, metal=0.0, emit=None, trans=0.0, aniso=0.0):
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
    if aniso:
        b.inputs["Anisotropic"].default_value = aniso
    if trans:
        b.inputs["Transmission Weight"].default_value = trans
    if emit:
        b.inputs["Emission Color"].default_value = (*emit[0], 1.0)
        b.inputs["Emission Strength"].default_value = emit[1]
    try:  # avrunda kantar i skyggjaren (0,3 mm)
        bev = nt.nodes.new("ShaderNodeBevel")
        bev.inputs["Radius"].default_value = 0.0003
        nt.links.new(bev.outputs["Normal"], b.inputs["Normal"])
    except Exception:
        pass
    return m


def mat_hud(namn, farge, trans=0.5, rough=0.8):
    """Tynn, gjennomskinleg hud (duk, papir, film): diffus + translusent."""
    m = bpy.data.materials.new(namn)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    ut = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    tr = nt.nodes.new("ShaderNodeBsdfTranslucent")
    dif.inputs["Color"].default_value = (*farge, 1.0)
    dif.inputs["Roughness"].default_value = rough
    tr.inputs["Color"].default_value = (*farge, 1.0)
    mix.inputs[0].default_value = trans
    nt.links.new(dif.outputs[0], mix.inputs[1])
    nt.links.new(tr.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], ut.inputs["Surface"])
    return m


def bibliotek(lys_paa):
    return {
        "kropp": mat("kropp", lin((0.80, 0.80, 0.79)), rough=0.62),
        "kropp_inn": mat("kropp_inn", lin((0.93, 0.93, 0.92)), rough=0.7),
        "alu": mat("alu", lin((0.78, 0.79, 0.80)), rough=0.35, metal=1.0),
        "alu_borsta": mat("alu_borsta", lin((0.80, 0.81, 0.82)), rough=0.42, metal=1.0, aniso=0.6),
        "solv": mat("solv", lin((0.86, 0.86, 0.87)), rough=0.5, metal=1.0),
        "messing": mat("messing", lin((0.86, 0.68, 0.38)), rough=0.28, metal=1.0),
        "svart": mat("svart", lin((0.05, 0.05, 0.05)), rough=0.5),
        "kvit": mat("kvit", lin((0.93, 0.93, 0.92)), rough=0.5),
        "pcb": mat("pcb", lin((0.08, 0.22, 0.12)), rough=0.4),
        "staal": mat("staal", lin((0.6, 0.6, 0.62)), rough=0.3, metal=1.0),
        "opal": mat("opal", lin((0.96, 0.96, 0.95)), rough=0.45,
                    emit=(((1.0, 0.80, 0.58), 6.0) if lys_paa else None)),
        "opal_ned": mat("opal_ned", lin((0.96, 0.96, 0.95)), rough=0.45,
                        emit=(((1.0, 0.86, 0.68), 22.0) if lys_paa else None)),
        "led": mat("led", lin((0.95, 0.88, 0.55)), rough=0.3),
        "celle": mat("celle", lin((0.20, 0.35, 0.65)), rough=0.4),
        "hud": mat_hud("hud", lin((0.93, 0.91, 0.86)), trans=0.5),
    }


STANDARD = {"D01": "kropp", "D02": "kropp", "D10": "kropp", "D03": "alu", "D04": "pcb", "D05": "pcb",
            "D09": "pcb", "D11": "pcb", "D14": "pcb", "D04L": "led", "D05L": "led", "D06": "kvit",
            "D07": "opal_ned", "D07P": "opal_ned", "D08": "opal", "D12F": "messing", "D12B": "messing",
            "D13F": "svart", "D13B": "svart", "K01": "celle", "K02": "svart", "K08": "kropp", "E01": "svart",
            "D09K": "svart", "D11J": "kvit", "K18": "kvit", "K05": "kvit", "K20": "messing"}

LAMPE = None


def importer(geo, lys_paa=False, med_leidning=True, overstyr=None):
    global LAMPE
    LAMPE = bpy.data.collections.new("lampe")
    bpy.context.scene.collection.children.link(LAMPE)
    bib = bibliotek(lys_paa)
    val = dict(STANDARD)
    f = ROT / "render" / "materialar.json"
    if f.exists():
        val.update(json.loads(f.read_text(encoding="utf-8")))
    if overstyr:
        val.update(overstyr)
    for d in geo["delar"]:
        if d["id"] == "E01" and not med_leidning:
            continue
        bpy.ops.wm.stl_import(filepath=str(ROT / d["stl"]), global_scale=0.001)
        o = bpy.context.selected_objects[0]
        o.name = d["id"]
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(28))
        except Exception:
            pass
        v = val.get(d["id"], "staal")
        if isinstance(v, dict):
            if v.get("type") == "hud":
                m = mat_hud(d["id"], lin(tuple(v.get("farge", (0.93, 0.91, 0.86)))), v.get("trans", 0.5),
                            v.get("rough", 0.8))
            else:
                em = v.get("emit") if lys_paa else None
                m = mat(d["id"], lin(tuple(v.get("farge", (0.8, 0.8, 0.79)))), v.get("rough", 0.6),
                        v.get("metal", 0.0), emit=((tuple(em[0]), em[1]) if em else None),
                        trans=v.get("trans", 0.0), aniso=v.get("aniso", 0.0))
        else:
            m = bib[v]
        o.data.materials.append(m)
        for c in list(o.users_collection):
            c.objects.unlink(o)
        LAMPE.objects.link(o)


def kamera(s, pos, maal, brennvidd=135):
    c = bpy.data.cameras.new("kam")
    c.lens = brennvidd
    o = bpy.data.objects.new("kam", c)
    s.collection.objects.link(o)
    o.location = Vector(pos)
    o.rotation_euler = (Vector(maal) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    s.camera = o


def areal(s, namn, pos, maal, storleik, energi, farge=(1, 1, 1), berre_lampa=False):
    l = bpy.data.lights.new(namn, "AREA")
    l.size = storleik
    l.energy = energi
    l.color = farge
    o = bpy.data.objects.new(namn, l)
    s.collection.objects.link(o)
    o.location = Vector(pos)
    o.rotation_euler = (Vector(maal) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    if berre_lampa and LAMPE is not None:
        try:
            o.light_linking.receiver_collection = LAMPE
        except Exception:
            pass


def golv(s, farge, rough=0.9, z=0.0, skuggefangar=False):
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, z))
    g = bpy.context.active_object
    g.data.materials.append(mat("golv", farge, rough=rough))
    g.is_shadow_catcher = skuggefangar


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


def lys_studio(s, z_bord):
    s.view_settings.view_transform = "Standard"
    s.render.film_transparent = True
    verd(s, (1.0, 1.0, 1.0), 0.35)
    golv(s, (0.8, 0.8, 0.8), rough=1.0, z=z_bord, skuggefangar=True)


def lys_svart(s, z_bord):
    s.view_settings.view_transform = "AgX"
    try:
        s.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    s.render.film_transparent = False
    verd(s, (0, 0, 0), 0.0)
    golv(s, (0.02, 0.02, 0.02), rough=0.35, z=z_bord)


def graa_bakgrunn(ut, bg=BG):
    img = bpy.data.images.load(str(ut))
    px = list(img.pixels)
    for i in range(0, len(px), 4):
        a = px[i + 3]
        for c in range(3):
            px[i + c] = px[i + c] * a + bg * (1 - a)
        px[i + 3] = 1.0
    img.pixels = px
    img.filepath_raw = str(ut)
    img.file_format = "PNG"
    img.save()


def render(vising):
    s = tom_scene()
    geo = json.loads((ROT / "render" / "geometri.json").read_text(encoding="utf-8"))
    z_bord = -geo.get("fot_h", 3.0) / 1000.0
    M = (0.150, 0.0, 0.147)   # midten av lampa
    px = (1200, 1200)
    svart_bg = False
    if vising == "front":
        importer(geo)
        lys_studio(s, z_bord)
        kamera(s, (0.150, -2.011, 0.430), M, 135)
        areal(s, "nokkel", (-0.9, -1.6, 1.4), (0.15, 0, 0.15), 1.6, 22)
        areal(s, "fyll", (1.6, -1.2, 0.6), (0.15, 0, 0.15), 2.0, 5)
    elif vising == "trekvart":
        importer(geo)
        lys_studio(s, z_bord)
        kamera(s, (1.05, -1.60, 0.66), (0.150, 0.0, 0.140), 132)
        # streiflys frå venstre langs framsida og rundt nasen: syner fasettar, vulstar og saumar
        areal(s, "nokkel", (-1.5, -0.55, 0.9), (0.15, 0, 0.16), 1.0, 17)
        areal(s, "topp", (0.4, -0.3, 1.8), (0.15, 0, 0.15), 1.6, 7)
        areal(s, "fyll", (1.8, -1.6, 0.5), (0.15, 0, 0.15), 2.2, 2.5)
        px = (1400, 1120)
    elif vising == "svart":
        importer(geo)
        lys_svart(s, z_bord)
        kamera(s, (-0.62, -1.45, 0.62), (0.150, 0.0, 0.140), 105)
        areal(s, "nokkel", (-0.5, -0.9, 1.3), (0.15, 0, 0.15), 1.2, 42, berre_lampa=True)
        areal(s, "kant", (1.2, 0.9, 0.7), (0.15, 0, 0.18), 0.8, 14, (0.85, 0.9, 1.0), berre_lampa=True)
        areal(s, "spegel", (-0.95, -2.2, 0.75), (0.15, 0, 0.14), 1.4, 6, berre_lampa=True)
        px = (1400, 1050)
    elif vising == "lys":
        importer(geo, lys_paa=True, med_leidning=False)
        lys_svart(s, z_bord)
        kamera(s, (-0.62, -1.45, 0.62), (0.150, 0.0, 0.140), 105)
        areal(s, "svak", (-0.5, -0.9, 1.3), (0.15, 0, 0.15), 1.2, 2.5, berre_lampa=True)
        px = (1400, 1050)
    elif vising == "topp":
        importer(geo)
        lys_studio(s, z_bord)
        kamera(s, (0.02, -0.66, 1.06), (0.150, 0.0, 0.215), 85)
        areal(s, "nokkel", (-0.8, -1.0, 1.6), (0.15, 0, 0.25), 1.6, 26)
        areal(s, "fyll", (1.4, -0.6, 1.2), (0.15, 0, 0.25), 2.0, 8)
        px = (1400, 1050)
    elif vising == "naer":
        importer(geo)
        lys_studio(s, z_bord)
        kamera(s, (0.98, -0.86, 0.47), (0.235, -0.020, 0.215), 100)
        areal(s, "nokkel", (-0.6, -0.9, 0.7), (0.26, 0, 0.23), 0.8, 8)
        areal(s, "topp", (0.5, -0.2, 1.3), (0.26, 0, 0.23), 1.2, 4)
        areal(s, "fyll", (1.5, -1.0, 0.4), (0.26, 0, 0.23), 1.8, 1.5)
        px = (1400, 1050)
    elif vising == "plate":
        # éin lampe på heilt svart (#000), ingen golv: grunnlag for overflatestudiar
        importer(geo, overstyr={"D01": "solv", "D02": "solv", "D10": "solv", "K08": "svart"})
        s.view_settings.view_transform = "Standard"
        s.render.film_transparent = True
        verd(s, (0, 0, 0), 0.0)
        kamera(s, (-0.27, -1.90, 0.64), (0.150, 0.0, 0.142), 150)
        areal(s, "nokkel", (-1.1, -1.5, 1.5), M, 1.6, 55)
        areal(s, "fyll", (1.5, -1.4, 0.5), M, 2.0, 9)
        areal(s, "kant", (0.9, 1.0, 1.1), M, 1.0, 30)
        px = (1536, 1536)
        svart_bg = True
    else:
        sys.exit("ukjend vising: " + vising)
    s.cycles.samples = PROVER
    s.render.resolution_x, s.render.resolution_y = px
    s.render.resolution_percentage = PROSENT
    ut = ROT / "render" / f"{ROT.name}_{vising}{'_prove' if KVAL == 'prove' else ''}.png"
    s.render.filepath = str(ut)
    s.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    if s.render.film_transparent:
        graa_bakgrunn(ut, 0.0 if svart_bg else BG)
    print("SKREIV", ut)


for v in VISINGAR:
    render(v)
