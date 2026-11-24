# -*- coding: utf-8 -*-
"""
render_lut.py  ·  rendringar av Lut rett frå CAD-nettet (render/nett/*.stl, laga av cad/lut.py)

  blender.exe -b -P render/render_lut.py -- oppriss tre_kvart [--prove] [--prover=256]

visingar: oppriss (same utsnitt som skissa), tre_kvart, venstre, bak, sprengt, ovanfra
Svart rom, éitt stort mjukt lys oppe til høgre, eit svakt kantlys, og lyskoppen lyser sjølv (2900 K).
"""
import bmesh
import bpy
import json
import math
import os
import sys
from mathutils import Vector

HER = os.path.dirname(os.path.abspath(__file__))
ROT = os.path.dirname(HER)
NETT = os.path.join(HER, 'nett')
DELAR = json.load(open(os.path.join(ROT, 'kontroll', 'lut_delar.json'), encoding='utf-8'))
ARG = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
PROVE = '--prove' in ARG
PROVER = int(next((a.split('=')[1] for a in ARG if a.startswith('--prover=')), 64 if PROVE else 384))
VIS = [a for a in ARG if not a.startswith('--')] or ['oppriss', 'tre_kvart']
MM = 0.001
SENTER = Vector((122.25 * MM, 0.0, 137.0 * MM))

LAKK = (0.125, 0.125, 0.12)           # matt mellomgrå som i skissa, lineære verdiar
MOTTAKARAR = None                     # lyslenking: studiolysa lyser berre på lampa, golvet får berre lyset frå lyskoppen


def nullstill(b, h):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    try:
        p = bpy.context.preferences.addons['cycles'].preferences
        p.compute_device_type = 'CUDA'
        p.get_devices()
        for d in p.devices:
            d.use = d.type != 'CPU'
        s.cycles.device = 'GPU'
    except Exception as e:                                        # noqa: BLE001
        print('SKJERMKORT IKKJE I BRUK', e, flush=True)
        s.cycles.device = 'CPU'
    s.cycles.samples = PROVER
    s.cycles.use_adaptive_sampling = True
    s.cycles.adaptive_threshold = 0.01
    s.cycles.use_denoising = True
    s.cycles.max_bounces = 10
    s.cycles.sample_clamp_indirect = 6.0
    s.render.resolution_x, s.render.resolution_y = b, h
    s.render.resolution_percentage = 50 if PROVE else 100
    s.render.film_transparent = False
    s.view_settings.view_transform = 'AgX'
    s.view_settings.exposure = 0.0
    v = bpy.data.worlds.new('rom')
    s.world = v
    if v.node_tree is None:
        v.use_nodes = True
    bg = v.node_tree.nodes.get('Background')
    bg.inputs[0].default_value = (0, 0, 0, 1)
    bg.inputs[1].default_value = 0.0
    return s


def nytt_materiale(namn):
    m = bpy.data.materials.new(namn)
    if m.node_tree is None:
        m.use_nodes = True
    return m, m.node_tree


def lakk(namn, farge, ruheit=0.55, kant=0.0003):
    m, nt = nytt_materiale(namn)
    b = nt.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*farge, 1)
    b.inputs['Roughness'].default_value = ruheit
    if kant:
        bev = nt.nodes.new('ShaderNodeBevel')
        bev.inputs['Radius'].default_value = kant
        bev.samples = 6
        nt.links.new(bev.outputs['Normal'], b.inputs['Normal'])
    return m


def lysande(namn, styrke, kelvin=2900):
    m, nt = nytt_materiale(namn)
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    ut = nt.nodes.new('ShaderNodeOutputMaterial')
    em = nt.nodes.new('ShaderNodeEmission')
    bb = nt.nodes.new('ShaderNodeBlackbody')
    bb.inputs['Temperature'].default_value = kelvin
    em.inputs['Strength'].default_value = styrke
    nt.links.new(bb.outputs[0], em.inputs['Color'])
    nt.links.new(em.outputs[0], ut.inputs['Surface'])
    return m


def importer(pid, mat):
    fil = DELAR[pid]['fil']
    bpy.ops.wm.stl_import(filepath=os.path.join(NETT, fil + '.stl'), global_scale=MM)
    o = bpy.context.selected_objects[0]
    o.name = pid
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bm.to_mesh(o.data)
    bm.free()
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(32))
    o.data.materials.append(mat)
    return o


def peik(o, maal):
    o.rotation_euler = (Vector(maal) - o.location).to_track_quat('-Z', 'Y').to_euler()


def lys(namn, pos, maal, storleik, effekt, form='RECTANGLE', farge=(1.0, 0.98, 0.95)):
    l = bpy.data.lights.new(namn, 'AREA')
    l.shape = form
    l.size = storleik
    if form == 'RECTANGLE':
        l.size_y = storleik * 0.5
    l.energy = effekt
    l.color = farge
    o = bpy.data.objects.new(namn, l)
    bpy.context.scene.collection.objects.link(o)
    o.location = Vector(pos)
    peik(o, maal)
    if MOTTAKARAR is not None:
        o.light_linking.receiver_collection = MOTTAKARAR
    return o


def kamera(pos, maal, lens, orto=None, skift=(0.0, 0.0)):
    c = bpy.data.cameras.new('kamera')
    if orto:
        c.type = 'ORTHO'
        c.ortho_scale = orto
    c.lens = lens
    c.sensor_width = 36.0
    c.shift_x, c.shift_y = skift
    o = bpy.data.objects.new('kamera', c)
    bpy.context.scene.collection.objects.link(o)
    o.location = Vector(pos)
    peik(o, maal)
    bpy.context.scene.camera = o
    return o


def golv(farge=(0.0015, 0.0015, 0.0015)):
    bpy.ops.mesh.primitive_plane_add(size=6.0, location=(0, 0, 0))
    o = bpy.context.active_object
    o.name = 'golv'
    o.data.materials.append(lakk('golv', farge, 0.65, 0.0))
    return o


def scene(med_innmat=False, utan=()):
    m_lakk = lakk('lakk', LAKK)
    m_stal = lakk('stal', (0.035, 0.035, 0.037), 0.45)
    m_kvit = lakk('petg', (0.80, 0.80, 0.78), 0.35)
    m_gummi = lakk('gummi', (0.012, 0.012, 0.012), 0.8)
    m_lys = lysande('spreiar', 38.0)
    m_alu = lakk('alu', (0.55, 0.56, 0.58), 0.3)
    m_messing = lakk('messing', (0.55, 0.38, 0.14), 0.35)
    m_kort = lakk('kort', (0.02, 0.12, 0.05), 0.5)
    m_metall = lakk('metall', (0.45, 0.45, 0.46), 0.3)
    global MOTTAKARAR
    MOTTAKARAR = bpy.data.collections.new('lampe_mottakarar')
    obj = {}
    synleg = {'D01': m_lakk, 'D02': m_lakk, 'D03': m_lakk, 'D05': m_lakk, 'D04': m_stal, 'D06': m_kvit, 'D07': m_lys}
    for pid, mat in synleg.items():
        if pid not in utan:
            obj[pid] = importer(pid, mat)
    for pid in DELAR:
        if pid.startswith('M07') and pid not in utan:
            obj[pid] = importer(pid, m_gummi)
    if med_innmat:
        inn = {'D08': m_alu, 'E01': m_messing, 'E02': m_metall, 'E02b': m_metall, 'E03': m_kort, 'E04': m_metall}
        for pid, mat in inn.items():
            if pid not in utan:
                obj[pid] = importer(pid, mat)
        for pid in DELAR:
            if pid.startswith(('M03', 'M04', 'M05', 'M06')) and pid not in utan:
                obj[pid] = importer(pid, m_metall)
    for o in obj.values():
        MOTTAKARAR.objects.link(o)
    return obj


def studio(skala=1.0):
    lys('hovudlys', (0.55, -0.85, 0.75), (0.12, 0.0, 0.14), 1.1 * skala, 38.0 * skala ** 2)
    lys('kantlys', (-0.55, 0.65, 0.45), (0.12, 0.0, 0.14), 0.8 * skala, 12.0 * skala ** 2)
    lys('fyll', (-0.6, -0.9, 0.2), (0.12, 0.0, 0.12), 1.2 * skala, 3.5 * skala ** 2)


def render(namn):
    s = bpy.context.scene
    s.render.filepath = os.path.join(HER, f'{namn}{"_prove" if PROVE else ""}.png')
    bpy.ops.render.render(write_still=True)
    print('SKREIV', s.render.filepath, flush=True)


# ------------------------------------------------------------------ visingar

def oppriss():
    """Same utsnitt som skissa: rett frå framsida, kameraet i høgd mellom foten og hovudet, lang linse."""
    nullstill(952, 1267)
    scene()
    golv()
    studio()
    kamera((0.1225, -1.40, 0.150), (0.1225, 0.0, 0.150), 83.0, skift=(0.028, -0.006))
    render('01_oppriss')


def tre_kvart():
    nullstill(2256, 1600)
    scene()
    golv()
    studio()
    a, e, d = math.radians(-38), math.radians(17), 1.55
    pos = SENTER + Vector((math.sin(-a) * math.cos(e) * d, -math.cos(a) * math.cos(e) * d, math.sin(e) * d))
    kamera(pos, SENTER + Vector((0.004, 0, -0.004)), 98.0)
    render('02_tre_kvart')


def venstre():
    nullstill(2256, 1600)
    scene()
    golv()
    studio()
    a, e, d = math.radians(32), math.radians(14), 1.55
    pos = SENTER + Vector((math.sin(-a) * math.cos(e) * d, -math.cos(a) * math.cos(e) * d, math.sin(e) * d))
    kamera(pos, SENTER, 98.0)
    render('03_venstre')


def bak():
    nullstill(2256, 1600)
    scene()
    golv()
    studio()
    lys('baklys', (0.4, 1.0, 0.6), (0.12, 0.0, 0.1), 1.0, 25.0)
    a, e, d = math.radians(-150), math.radians(16), 1.55
    pos = SENTER + Vector((math.sin(-a) * math.cos(e) * d, -math.cos(a) * math.cos(e) * d, math.sin(e) * d))
    kamera(pos, SENTER, 98.0)
    render('04_bak')


def sprengt():
    """Delane trekte frå kvarandre langs monteringsaksane. Ståande format."""
    nullstill(1600, 2256)
    obj = scene(med_innmat=True)
    golv()
    studio(1.3)
    flytt = {}
    hov = Vector((95, 0, 0)) * MM
    kopp = hov + Vector((0, 0, -62)) * MM
    for pid in ('D02', 'M06-1', 'M06-2', 'M06-3'):
        flytt[pid] = hov
    for pid in ('D06', 'M06-4', 'M06-5', 'M06-6'):
        flytt[pid] = kopp
    flytt['D08'] = kopp + Vector((0, 0, -34)) * MM            # kjøleplate og LED går opp i koppen nedanfrå
    flytt['E01'] = kopp + Vector((0, 0, -54)) * MM
    flytt['D07'] = kopp + Vector((0, 0, -92)) * MM
    for pid in ('M04-1', 'M04-2'):
        flytt[pid] = hov + Vector((40, 0, 0)) * MM
    flytt['D05'] = Vector((0, 0, 70)) * MM
    flytt['E02b'] = Vector((0, 0, 45)) * MM
    fot = Vector((0, 0, -95)) * MM
    for pid in ('D03', 'E02', 'E03', 'E04'):
        flytt[pid] = fot
    for pid in ('M03-1', 'M03-2', 'M03-3'):
        flytt[pid] = fot + Vector((0, 0, -45)) * MM
    plate = fot + Vector((0, 0, -95)) * MM
    flytt['D04'] = plate
    for pid in DELAR:
        if pid.startswith('M05'):
            flytt[pid] = plate + Vector((0, 0, -30)) * MM
        if pid.startswith('M07'):
            flytt[pid] = plate + Vector((0, 0, -18)) * MM
    for pid, v in flytt.items():
        if pid in obj:
            obj[pid].location = obj[pid].location + v
    bpy.data.objects['golv'].location.z = -0.26
    maal = Vector((0.165, 0.0, -0.005))
    a, e, d = math.radians(-30), math.radians(14), 1.62
    pos = maal + Vector((math.sin(-a) * math.cos(e) * d, -math.cos(a) * math.cos(e) * d, math.sin(e) * d))
    kamera(pos, maal, 85.0)
    render('05_sprengt')


def ovanfra():
    nullstill(1600, 1600)
    scene()
    golv()
    studio()
    kamera((0.1225, -0.0001, 1.5), (0.1225, 0.0, 0.0), 50.0, orto=0.32)
    render('06_ovanfra')


for v in VIS:
    globals()[v]()
