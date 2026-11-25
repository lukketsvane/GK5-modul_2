# -*- coding: utf-8 -*-
"""
render_kran.py  ·  rendringar av Kran rett frå CAD-nettet (render/nett/*.stl, laga av cad/kran.py)

  blender.exe -b -P render/render_kran.py -- som_fotoet tre_kvart [--prove] [--prover=256]

visingar: som_fotoet (kameraet som er rekna ut frå fotoet), oppriss, tre_kvart, bak, ledd, sprengt, lys
Svart rom. Studiolysa lyser berre på lampa; golvet får berre lyset frå lyslista (spreiaren lyser sjølv, 2700 K).
Lakken er prøvd mot fotoet: varm salvie, silkematt.
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
DELAR = json.load(open(os.path.join(ROT, 'kontroll', 'kran_delar.json'), encoding='utf-8'))
MAAL = json.load(open(os.path.join(ROT, 'referanse', 'maaling.json'), encoding='utf-8'))
ARG = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
PROVE = '--prove' in ARG
PROVER = int(next((a.split('=')[1] for a in ARG if a.startswith('--prover=')), 48 if PROVE else 320))
VIS = [a for a in ARG if not a.startswith('--')] or ['som_fotoet', 'tre_kvart']
LYSFAKTOR = float(next((a.split('=')[1] for a in ARG if a.startswith('--lys=')), 0.38))
VISNING = next((a.split('=')[1] for a in ARG if a.startswith('--visning=')), 'AgX')   # mjuk overgang i høglys; lakken er mettare for å vege opp
LOOK = next((a.split('=')[1] for a in ARG if a.startswith('--look=')), 'None')
MM = 0.001
SENTER = Vector((0.315, 0.006, 0.175))

SALVIE = tuple(float(x) for x in next((a.split('=')[1] for a in ARG if a.startswith('--salvie=')), '0.345,0.305,0.125').split(','))
# lakken: lineære verdiar, prøvd mot fotoet gjennom AgX (stativflata blir 166/157/120 mot 165/157/120 i fotoet)
LED_STYRKE = 45.0
MOTTAKARAR = None


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
        s.cycles.device = 'GPU' if any(d.use for d in p.devices) else 'CPU'
    except Exception as e:                                        # noqa: BLE001
        print('SKJERMKORT IKKJE I BRUK', e, flush=True)
        s.cycles.device = 'CPU'
    s.cycles.samples = PROVER
    s.cycles.use_adaptive_sampling = True
    s.cycles.adaptive_threshold = 0.012
    s.cycles.use_denoising = True
    s.cycles.max_bounces = 8
    s.cycles.sample_clamp_indirect = 6.0
    s.render.resolution_x, s.render.resolution_y = b, h
    s.render.resolution_percentage = 50 if PROVE else 100
    s.render.film_transparent = False
    s.view_settings.view_transform = VISNING
    s.view_settings.look = LOOK if LOOK == 'None' else f'{VISNING} - {LOOK}'
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


def lakk(namn, farge, ruheit=0.5, kant=0.0003, metall=0.0):
    m, nt = nytt_materiale(namn)
    b = nt.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*farge, 1)
    b.inputs['Roughness'].default_value = ruheit
    b.inputs['Metallic'].default_value = metall
    if kant:
        bev = nt.nodes.new('ShaderNodeBevel')
        bev.inputs['Radius'].default_value = kant
        bev.samples = 6
        nt.links.new(bev.outputs['Normal'], b.inputs['Normal'])
    return m


def lysande(namn, styrke, kelvin=2700):
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


def lys(namn, pos, maal, storleik, effekt, form='RECTANGLE', farge=(1.0, 0.98, 0.95), glans=1.0):
    l = bpy.data.lights.new(namn, 'AREA')
    l.shape = form
    l.size = storleik
    if form == 'RECTANGLE':
        l.size_y = storleik * 0.5
    l.energy = effekt
    l.color = farge
    l.specular_factor = glans
    o = bpy.data.objects.new(namn, l)
    bpy.context.scene.collection.objects.link(o)
    o.location = Vector(pos)
    peik(o, maal)
    if MOTTAKARAR is not None:
        o.light_linking.receiver_collection = MOTTAKARAR
    return o


def kamera(pos, maal=None, lens=85.0, orto=None, skift=(0.0, 0.0), rot=None):
    c = bpy.data.cameras.new('kamera')
    if orto:
        c.type = 'ORTHO'
        c.ortho_scale = orto
    c.lens = lens
    c.sensor_width = 36.0
    c.sensor_fit = 'HORIZONTAL'
    c.shift_x, c.shift_y = skift
    c.clip_start, c.clip_end = 0.01, 20.0
    o = bpy.data.objects.new('kamera', c)
    bpy.context.scene.collection.objects.link(o)
    o.location = Vector(pos)
    if rot is not None:
        o.rotation_euler = rot
    else:
        peik(o, maal)
    bpy.context.scene.camera = o
    return o


def golv(farge=(0.0015, 0.0015, 0.0015), z=0.0):
    bpy.ops.mesh.primitive_plane_add(size=8.0, location=(0.3, 0, z))
    o = bpy.context.active_object
    o.name = 'golv'
    o.data.materials.append(lakk('golv', farge, 0.6, 0.0))
    return o


SYNLEGE = ('D01', 'D02', 'D03', 'D04', 'D05', 'D06', 'D07', 'D08', 'D09', 'D10', 'D11', 'D12', 'D14',
           'M01', 'M03-1', 'M03-2', 'D13-1', 'D13-2')


def scene(med_innmat=False, utan=(), led=LED_STYRKE):
    m_lakk = lakk('lakk', SALVIE, 0.42)
    m_stal = lakk('rustfritt', (0.62, 0.62, 0.63), 0.28, metall=1.0)
    m_messing = lakk('messing', (0.80, 0.58, 0.28), 0.3, metall=1.0)
    m_pa6 = lakk('pa6', (0.80, 0.78, 0.72), 0.55)
    m_mork = lakk('petg_mork', (0.018, 0.018, 0.02), 0.45)
    m_filt = lakk('filt', (0.025, 0.025, 0.025), 0.95, 0.0)
    m_lys = lysande('spreiar', led) if led else lakk('opal', (0.85, 0.84, 0.80), 0.4)
    m_led = lakk('led', (0.95, 0.80, 0.35), 0.4)
    m_kort = lakk('kort', (0.02, 0.10, 0.05), 0.5)
    m_svart = lakk('svart', (0.012, 0.012, 0.013), 0.5)
    global MOTTAKARAR
    MOTTAKARAR = bpy.data.collections.new('lampe_mottakarar')
    mat = {'D01': m_lakk, 'D02': m_lakk, 'D03': m_lakk, 'D04': m_lakk, 'D05': m_lakk, 'D06': m_stal, 'D07': m_lakk,
           'D08': m_lakk, 'D09': m_lakk, 'D10': m_lakk, 'D11': m_mork, 'D12': m_lys, 'D14': m_mork,
           'M01': m_messing, 'M03-1': m_pa6, 'M03-2': m_pa6, 'D13-1': m_filt, 'D13-2': m_filt}
    if med_innmat:
        mat.update({'E01': m_led, 'E02': m_svart, 'E03': m_kort, 'E04': m_svart, 'M05': m_stal})
        for pid in DELAR:
            if pid.startswith(('M02', 'M04')):
                mat[pid] = m_stal
    obj = {}
    for pid, m in mat.items():
        if pid not in utan and pid in DELAR:
            obj[pid] = importer(pid, m)
    for pid, o in obj.items():
        if pid != 'D12' or not led:
            MOTTAKARAR.objects.link(o)
    return obj


def studio(skala=1.0, maal=None, styrke=1.0):
    """Hovudlys framme til venstre og høgt (som i fotoet), kantlys bak til høgre, svakt fyll frå framsida."""
    m = Vector(maal) if maal is not None else SENTER
    k = 1.55 * skala
    styrke *= LYSFAKTOR
    lys('hovudlys', m + Vector((-0.55, -0.95, 0.80)) * k, m, 1.3 * k, 95.0 * k * k * styrke)
    lys('kantlys', m + Vector((0.75, 0.70, 0.45)) * k, m, 1.0 * k, 34.0 * k * k * styrke, glans=0.2)   # glansen ville gjort toppflata kvit
    lys('fyll', m + Vector((0.55, -1.0, 0.10)) * k, m, 1.6 * k, 9.0 * k * k * styrke)


def render(namn):
    s = bpy.context.scene
    s.render.filepath = os.path.join(HER, f'{namn}{"_prove" if PROVE else ""}.png')
    bpy.ops.render.render(write_still=True)
    print('SKREIV', s.render.filepath, flush=True)


def baan(a_grad, e_grad, d, maal):
    a, e = math.radians(a_grad), math.radians(e_grad)
    return Vector(maal) + Vector((math.sin(a) * math.cos(e) * d, -math.cos(a) * math.cos(e) * d, math.sin(e) * d))


# ------------------------------------------------------------------ visingar

def som_fotoet():
    """Kameraet rekna ut frå fotoet (referanse/kamera.py): vatrett, 87,5 mm linse på 36 mm, same utsnitt."""
    q = MAAL
    nullstill(2254, 1594)
    scene()
    golv()
    studio()
    c, s_ = math.cos(q['phi']), math.sin(q['phi'])
    pos = Vector((-q['uA'] * c + q['ZA'] * s_, -q['uA'] * s_ - q['ZA'] * c, q['H'])) * MM
    kamera(pos, lens=q['f'] * 36.0 / 2254, rot=(math.pi / 2, 0.0, q['phi']),
           skift=((1128.0 - 2254 / 2) / 2254, (q['cy'] - 1594 / 2) / 2254))
    render('01_som_fotoet')


def oppriss():
    """Rett framanfrå, ortografisk: silhuetten."""
    nullstill(2256, 1500)
    scene()
    golv()
    studio()
    kamera((SENTER.x, -3.0, 0.19), (SENTER.x, 0.0, 0.19), 50.0, orto=0.80)
    render('02_oppriss')


def tre_kvart():
    nullstill(2256, 1600)
    scene()
    golv()
    studio()
    m = SENTER + Vector((0.0, 0.0, -0.005))
    kamera(baan(-36, 14, 2.35, m), m, 85.0)
    render('03_tre_kvart')


def bak():
    nullstill(2256, 1600)
    scene()
    golv()
    studio()
    lys('baklys', SENTER + Vector((0.6, 1.6, 0.9)), SENTER, 1.4, 70.0 * LYSFAKTOR)
    m = SENTER + Vector((-0.02, 0.0, 0.0))
    kamera(baan(152, 16, 2.35, m), m, 85.0)
    render('04_bak')


def ledd():
    """Nærbilete av leddet: knotten, øyret, stativhovudet og spalta."""
    nullstill(1600, 1600)
    scene()
    golv()
    m = Vector((0.170, -0.004, 0.318))
    studio(0.45, m)
    kamera(baan(-24, 9, 0.62, m), m, 100.0)
    render('05_ledd')


def sprengt():
    """Delane trekte frå kvarandre langs monteringsaksane: leddpakka langs akselen (Y), innmaten i armen ned og
    endelokket ut. Lomma med innmaten og loket står til venstre for stativet (ho sit bak på foten), så ho ikkje
    blir gøymd bak platene."""
    nullstill(2256, 1600)
    obj = scene(med_innmat=True, led=0.0)
    golv(z=-0.06)
    flytt = {}
    arm = Vector((0, -95, 0))
    for pid in ('D04', 'D09', 'D10', 'D12', 'E01'):
        flytt[pid] = arm
    flytt['D05'] = arm + Vector((0, 22, 0))
    flytt['M05'] = arm + Vector((0, 44, 0))
    flytt['D09'] = arm + Vector((55, 0, 0))
    flytt['D10'] = arm + Vector((0, 0, -45))
    flytt['E01'] = arm + Vector((0, 0, -45))
    flytt['D12'] = arm + Vector((0, 0, -80))
    flytt['M02-1'] = Vector((0, -150, 0))
    flytt['D07'] = Vector((0, -185, 0))
    flytt['M01'] = Vector((0, -235, 0))
    flytt['M03-1'] = Vector((0, -42, 0))
    flytt['D01'] = Vector((0, -16, 0))
    flytt['D03'] = Vector((0, 16, 0))
    flytt['D13-1'] = Vector((0, -16, -30))
    flytt['D13-2'] = Vector((0, 16, -30))
    flytt['M03-2'] = Vector((0, 40, 0))
    flytt['D06'] = Vector((0, 58, 0))
    for i in range(1, 5):
        flytt[f'M04-{i}'] = Vector((0, 70 + 7 * i, 0))
    flytt['M02-2'] = Vector((0, 120, 0))
    flytt['D08'] = Vector((0, 150, 0))
    lomme = Vector((-175, 40, 0))
    flytt['D11'] = lomme
    for pid in ('E02', 'E03', 'E04'):
        flytt[pid] = lomme + Vector((0, 0, 42))
    flytt['D14'] = lomme + Vector((0, 0, 80))
    for pid, v in flytt.items():
        if pid in obj:
            obj[pid].location = obj[pid].location + v * MM
    m = Vector((0.27, -0.03, 0.175))
    studio(1.15, m)
    kamera(baan(-40, 22, 2.2, m), m, 85.0)
    render('06_sprengt')


def lys_paa():
    """Lampa i mørkret: berre lyslista og eit svakt kantlys."""
    nullstill(2256, 1600)
    scene(led=LED_STYRKE * 1.3)
    golv((0.004, 0.004, 0.004))
    lys('kantlys', SENTER + Vector((0.9, 0.9, 0.6)), SENTER, 1.2, 14.0, glans=0.3)
    lys('fyll', SENTER + Vector((-0.8, -1.4, 0.4)), SENTER, 1.8, 6.0)
    m = SENTER + Vector((0.0, 0.0, -0.02))
    kamera(baan(-30, 3, 2.3, m), m, 85.0)
    render('07_lys')


for v in VIS:
    globals()['lys_paa' if v == 'lys' else v]()
