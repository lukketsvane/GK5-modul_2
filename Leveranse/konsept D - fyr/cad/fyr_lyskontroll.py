# -*- coding: utf-8 -*-
"""FYR · lyskontroll på dei faktiske CAD-nettene (Blender BVH-strålekasting, hovudlaust).

    blender.exe -b -P cad/fyr_lyskontroll.py -- <stl_mappe> <ut.json> [n_strålar]

STL-ane kjem frå fyr_render_eksport.py (serie, hylsa på 0° = alle seks spaltene opne). Heile lampa blir
rekna som svart (første treff tel), slik protokollen frå lysanalysen krev:

 1 Avskjering: strålar frå heile flata til sidestripa ut i framre halvrom. Krav: ingen stråle som slepp ut
   av lampa går ut over -34° (34° under horisontalen dekkjer spegling i ein skjerm som hallar 20° bakover).
 2 Toppemitter: strålar frå dei fire toppbitane. Krav: ingen slepp ut utan å treffe loket (dvs. ingen
   veg forbi loket ut gjennom kronespaltene eller spalta mot mantelen).
 3 Augo: frå augehøgd 250/350/470/600 mm over bordet, 400/700 mm unna, asimut 0/±30°, kastar vi strålar
   mot heile spalte- og kronefeltet. Krav: ingen stråle treffer ein LED (sidestripe eller toppemitter).
"""
import json
import math
import os
import random
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ARGS = sys.argv[sys.argv.index("--") + 1:]
STL, UT = ARGS[0], ARGS[1]
N = int(ARGS[2]) if len(ARGS) > 2 else 1_000_000
random.seed(20261124)
INFO = json.load(open(os.path.join(STL, "scene.json"), encoding="utf-8"))

bpy.ops.wm.read_factory_settings(use_empty=True)
verts, polys, eigar = [], [], []
namn_liste = []
for fil in sorted(os.listdir(STL)):
    if not fil.endswith(".stl"):
        continue
    namn = fil[:-4]
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.stl_import(filepath=os.path.join(STL, fil), global_scale=1.0)
    ob = bpy.context.selected_objects[0]
    mw = ob.matrix_world
    base = len(verts)
    verts.extend([mw @ v.co for v in ob.data.vertices])
    idx = len(namn_liste)
    namn_liste.append(namn)
    for pl in ob.data.polygons:
        polys.append([base + i for i in pl.vertices])
        eigar.append(idx)
bvh = BVHTree.FromPolygons(verts, polys, all_triangles=True, epsilon=0.0)
print("BVH", len(verts), "hjørne", len(polys), "flater", namn_liste)
LED = {i for i, n in enumerate(namn_liste) if n.startswith("06b") or n.startswith("06c")}
LOK = {i for i, n in enumerate(namn_liste) if n.startswith("08")}


def kast(o, d, maks=600.0):
    loc, nrm, fi, dist = bvh.ray_cast(o, d, maks)
    if loc is None:
        return None, None
    return eigar[fi], loc


def retning(el, az):
    ce = math.cos(el)
    return Vector((ce * math.cos(az), ce * math.sin(az), math.sin(el)))


# ------------------------------------------------------------------ 1 avskjering
st = INFO["stripe"]
x0 = st["x"] + 0.02
ut_1 = {"n": 0, "slapp_ut": 0, "maks_elevasjon_slapp_ut": -90.0, "hist": {}}
for i in range(N):
    o = Vector((x0, random.uniform(-st["b"] / 2 + 0.05, st["b"] / 2 - 0.05), random.uniform(st["z0"] + 0.05, st["z1"] - 0.05)))
    # uniform over framre halvrom (x > 0)
    while True:
        d = Vector((random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1)))
        if d.length > 1e-9:
            d.normalize()
            if d.x > 1e-4:
                break
    hit, loc = kast(o, d)
    ut_1["n"] += 1
    if hit is None:
        ut_1["slapp_ut"] += 1
        el = math.degrees(math.asin(max(-1.0, min(1.0, d.z))))
        ut_1["maks_elevasjon_slapp_ut"] = max(ut_1["maks_elevasjon_slapp_ut"], el)
        b = str(int(math.floor(el / 5.0) * 5))
        ut_1["hist"][b] = ut_1["hist"].get(b, 0) + 1
ut_1["slapp_ut_del"] = ut_1["slapp_ut"] / ut_1["n"]
ut_1["krav"] = "ingen stråle ut over -34°"
ut_1["bestatt"] = ut_1["maks_elevasjon_slapp_ut"] <= -34.0
print("1 avskjering", ut_1)

# ------------------------------------------------------------------ 2 toppemitter
tp = INFO["topp"]
ut_2 = {"n": 0, "forbi_loket": 0, "treff_lok": 0}
n2 = N // 4
for i in range(n2):
    a = math.radians(45.0 + 90.0 * random.randrange(4))
    u = random.uniform(-tp["l"] / 2 + 0.1, tp["l"] / 2 - 0.1)
    v = random.uniform(-tp["b"] / 2 + 0.1, tp["b"] / 2 - 0.1)
    r = tp["r"] + v
    px, py = r * math.cos(a) - u * math.sin(a), r * math.sin(a) + u * math.cos(a)
    o = Vector((px, py, tp["z"] + 0.02))
    while True:
        d = Vector((random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1)))
        if d.length > 1e-9:
            d.normalize()
            if d.z > 1e-4:
                break
    hit, loc = kast(o, d)
    ut_2["n"] += 1
    if hit is None:
        ut_2["forbi_loket"] += 1
    elif hit in LOK:
        ut_2["treff_lok"] += 1
ut_2["krav"] = "ingen stråle ut utan å gå gjennom loket"
ut_2["bestatt"] = ut_2["forbi_loket"] == 0
print("2 toppemitter", ut_2)

# ------------------------------------------------------------------ 3 augo
sp = INFO["spalter"]
H = INFO["hogd"]
ut_3 = {"posisjonar": [], "led_treff_totalt": 0}
for h_ in (250.0, 350.0, 470.0, 600.0):
    for dist in (400.0, 700.0):
        for az in (-30.0, 0.0, 30.0):
            a = math.radians(az)
            auge = Vector((dist * math.cos(a), dist * math.sin(a), h_))
            n_led, n_tot, n_inn = 0, 0, 0
            for k in range(20000):
                # mål: spaltefeltet (asimut ±35°, z spalter) eller krona (heile omkrinsen, z 262..299)
                if k % 2 == 0:
                    ta = math.radians(random.uniform(-35.0, 35.0))
                    tz = random.uniform(sp["z0"], sp["z1"])
                    tr = 44.0
                else:
                    ta = math.radians(random.uniform(0.0, 360.0))
                    tz = random.uniform(262.0, H)
                    tr = 41.5
                mal = Vector((tr * math.cos(ta), tr * math.sin(ta), tz))
                d = (mal - auge)
                d.normalize()
                hit, loc = kast(auge, d, 2000.0)
                n_tot += 1
                if hit is None:
                    continue
                if math.hypot(loc.x, loc.y) < 40.5:
                    n_inn += 1          # strålen kom inn i lampa (gjennom ei opning)
                if hit in LED:
                    n_led += 1
            ut_3["posisjonar"].append({"h": h_, "d": dist, "asimut": az, "strålar": n_tot, "inn_i_lampa": n_inn, "led_treff": n_led})
            ut_3["led_treff_totalt"] += n_led
ut_3["krav"] = "ingen siktline frå sitjande augo treffer ein LED"
ut_3["bestatt"] = ut_3["led_treff_totalt"] == 0
print("3 augo", ut_3["led_treff_totalt"], "LED-treff")

res = {"skildring": "FYR lyskontroll på CAD-nett (BVH, første treff, heile lampa svart)", "theta": INFO["theta"],
       "avskjering_rekna_2D_grader": INFO.get("rist_avskjering_2D"), "1_avskjering": ut_1, "2_toppemitter": ut_2, "3_augo": ut_3,
       "alle_bestatt": bool(ut_1["bestatt"] and ut_2["bestatt"] and ut_3["bestatt"])}
json.dump(res, open(UT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("LYSKONTROLL", "BESTÅTT" if res["alle_bestatt"] else "IKKJE BESTÅTT", UT)
