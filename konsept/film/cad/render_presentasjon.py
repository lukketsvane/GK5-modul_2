# -*- coding: utf-8 -*-
"""
render_presentasjon.py  ·  rendringane til presentasjonen av revisjon B

Geometrien er delane frå northern.py (ut-b/samla/*.stl), og måla kjem frå ut-b/geometri.json. Hellinga blir sett ved å
dreie dei rørlege delane om røyret, slik bjelken gjer. Gløden i ruta er ei visualisering, ikkje ei lysrekning.

  blender.exe -b -P render_presentasjon.py -- studio helling detalj sprengt kveld dag [--prove]

  studio   lampa i mørkt studio, tre kvart framanfrå
  helling  profilen ved 0°, 35° og 70°
  detalj   messingpunktet i enden av bjelken
  sprengt  delane trekte frå kvarandre, med ankerpunkt til nummera i sprengt.json
  kveld    pulten om kvelden, mørkegrøn
  dag      fire fargar i dagslys frå sida
"""
import bpy, os, sys, math, json
from mathutils import Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view

HER = os.path.dirname(os.path.abspath(__file__))
UT = os.path.join(HER, 'ut-b'); RUT = os.path.join(UT, 'render')
G = json.load(open(os.path.join(UT, 'geometri.json'), encoding='utf-8'))
PROVE = '--prove' in sys.argv
VIS = [a for a in sys.argv[sys.argv.index('--') + 1:] if not a.startswith('--')] if '--' in sys.argv else []
AKSE = Vector((0.0, G['YT'] / 1000.0, G['AKSE_H'] / 1000.0))
FARGAR = [('graabeige', (0.33, 0.30, 0.26)), ('morkegron', (0.022, 0.048, 0.033)), ('svart', (0.012, 0.012, 0.013)), ('kirsebaer', (0.19, 0.016, 0.022))]
FARGE = dict(FARGAR)
ROERLEG = ('05', '06', '07', '08', '09', '10', '11', '13', 'E')

def skaansam():
    try:
        import ctypes
        k = ctypes.windll.kernel32; k.SetPriorityClass(k.GetCurrentProcess(), 0x40)
    except Exception:
        pass

def mat(namn, farge, metall=0.0, ruheit=0.5, trans=0.0, ior=1.5, glod=None, styrke=0.0):
    m = bpy.data.materials.new(namn); m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*farge, 1.0); p.inputs['Metallic'].default_value = metall
    p.inputs['Roughness'].default_value = ruheit; p.inputs['Transmission Weight'].default_value = trans
    p.inputs['IOR'].default_value = ior
    if glod is not None:
        p.inputs['Emission Color'].default_value = (*glod, 1.0); p.inputs['Emission Strength'].default_value = styrke
    return m

def film_materiale(glod, reine=False):
    """Prismearket: fine striper på tvers av bjelken, og meir glød mot den frie kanten."""
    m = bpy.data.materials.new('film'); m.use_nodes = True; nt = m.node_tree
    p = nt.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (0.88, 0.86, 0.82, 1.0); p.inputs['Roughness'].default_value = 0.25
    p.inputs['Transmission Weight'].default_value = 0.25
    tc = nt.nodes.new('ShaderNodeTexCoord')
    # reine striper: mønsteret varierer berre langs bjelken, slik rillene i arket går. Elles teiknar støyen skrå band i mørke
    ma = nt.nodes.new('ShaderNodeMapping'); ma.inputs['Scale'].default_value = (55.0, 0.02, 0.02) if reine else (55.0, 1.2, 1.2)
    nt.links.new(tc.outputs['Object'], ma.inputs['Vector'])
    no = nt.nodes.new('ShaderNodeTexNoise'); no.inputs['Scale'].default_value = 3.0; no.inputs['Detail'].default_value = 5.0
    nt.links.new(ma.outputs['Vector'], no.inputs['Vector'])
    cr = nt.nodes.new('ShaderNodeValToRGB')
    cr.color_ramp.elements[0].position = 0.35; cr.color_ramp.elements[0].color = (1.0, 0.86, 0.66, 1.0)
    cr.color_ramp.elements[1].position = 0.75; cr.color_ramp.elements[1].color = (1.0, 0.64, 0.26, 1.0)
    nt.links.new(no.outputs['Fac'], cr.inputs['Fac'])
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sep.inputs[0])
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.26; mr.inputs['From Max'].default_value = 0.15
    mr.inputs['To Min'].default_value = 0.3 * glod; mr.inputs['To Max'].default_value = 2.0 * glod
    nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
    m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'
    nt.links.new(no.outputs['Fac'], m2.inputs[0]); nt.links.new(mr.outputs['Result'], m2.inputs[1])
    nt.links.new(cr.outputs['Color'], p.inputs['Emission Color']); nt.links.new(m2.outputs[0], p.inputs['Emission Strength'])
    return m

def importer(fil, m, glatt=32):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.stl_import(filepath=fil, global_scale=0.001)
    ob = bpy.context.selected_objects[0]
    ob.data.materials.clear(); ob.data.materials.append(m)
    bpy.context.view_layer.objects.active = ob
    try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(glatt))
    except Exception: pass
    return ob

def boks(namn, storleik, pos, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=pos, rotation=rot)
    ob = bpy.context.object; ob.name = namn; ob.scale = storleik; ob.data.materials.append(m); return ob

def peik(ob, maal):
    ob.rotation_euler = (Vector(maal) - ob.location).to_track_quat('-Z', 'Y').to_euler()

def lys(namn, pos, maal, storleik, styrke, farge=(1, 1, 1), synleg=True):
    ld = bpy.data.lights.new(namn, 'AREA'); ld.size = storleik; ld.energy = styrke; ld.color = farge
    ob = bpy.data.objects.new(namn, ld); bpy.context.collection.objects.link(ob); ob.location = pos; peik(ob, maal)
    if not synleg:
        ob.visible_camera = False; ob.visible_transmission = False; ob.visible_glossy = False
    return ob

def grunn(storleik, prover, eksponering=-0.35, verd=0.0):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.render.threads_mode = 'FIXED'; s.render.threads = 4
    if PROVE: storleik, prover = (storleik[0] // 3, storleik[1] // 3), 14
    s.cycles.samples = prover; s.cycles.use_denoising = True
    s.render.resolution_x, s.render.resolution_y = storleik
    s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'; s.view_settings.exposure = eksponering
    w = bpy.data.worlds.new('verd'); s.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (verd, verd, verd * 1.1, 1.0)
    return s

def lampe(farge, glod=1.0, under=1.6, stripe=None, reine=False):
    """Les inn delane. Returnerer {id: objekt}. Lyset under ruta følgjer med dei rørlege delane."""
    kropp = mat('kropp', farge, 0.0, 0.58)
    messing = mat('messing', (0.80, 0.60, 0.30), 1.0, 0.30)
    staal = mat('staal', (0.6, 0.6, 0.6), 1.0, 0.35)
    svart = mat('svart', (0.012, 0.012, 0.013), 0.0, 0.7)
    akryl = mat('akryl', (1.0, 0.97, 0.92), 0.0, 0.03, trans=1.0, ior=1.49, glod=(1.0, 0.70, 0.36), styrke=0.25 * glod)
    # stripa inni bjelken: i mørke teiknar ho ein skrå lysflekk gjennom plata, så kveldsbiletet dempar ho
    led = mat('led', (1.0, 0.9, 0.7), 0.0, 0.5, glod=(1.0, 0.72, 0.38), styrke=30.0 * glod if stripe is None else stripe)
    M = {'01': kropp, '02': svart, '03': staal, '04': kropp, '05': kropp, '06': kropp, '07': akryl, '08': film_materiale(glod, reine), '09': staal,
         '10': led, '11': messing, '12': staal, '13': staal, 'E': staal, 'leidning': kropp}
    O = {}
    for i, m in M.items():
        f = os.path.join(UT, 'samla', i + '.stl')
        if os.path.exists(f): O[i] = importer(f, m); O[i].name = 'del_' + i
    if '08' in O:                                   # arket ligg mot plata i CAD-en. Like flater gjev trekantmønster i rendringa, så arket blir løfta 0,1 mm
        t = math.radians(G['VINKEL']); O['08'].matrix_world = Matrix.Translation(Vector((0.0, -math.sin(t), math.cos(t))) * 0.00012) @ O['08'].matrix_world
    if under > 0:
        O['under'] = lys('under', (-0.02, -0.11, 0.15), (-0.02, -0.20, 0.0), 0.20, under, (1.0, 0.64, 0.32), synleg=False)
    bpy.context.view_layer.update()
    return O

def hell(O, vinkel):
    """Dreier dei rørlege delane om røyret frå hellinga i fila til den nye."""
    R = Matrix.Translation(AKSE) @ Matrix.Rotation(math.radians(vinkel - G['VINKEL']), 4, 'X') @ Matrix.Translation(-AKSE)
    for i in ROERLEG + ('under',):
        if i in O: O[i].matrix_world = R @ O[i].matrix_world
    bpy.context.view_layer.update()

def flytt(ob, v):
    ob.matrix_world = Matrix.Translation(Vector(v)) @ ob.matrix_world

def midt(ob):
    return sum((ob.matrix_world @ Vector(c) for c in ob.bound_box), Vector()) / 8.0

def kamera(pos, maal, lens, fstop=None, fokus=None):
    s = bpy.context.scene
    kam = bpy.data.cameras.new('kam'); kam.lens = lens
    ko = bpy.data.objects.new('kam', kam); bpy.context.collection.objects.link(ko)
    ko.location = pos; peik(ko, maal); s.camera = ko
    if fstop:
        kam.dof.use_dof = True; kam.dof.aperture_fstop = fstop
        kam.dof.focus_distance = (Vector(fokus if fokus is not None else maal) - Vector(pos)).length
    bpy.context.view_layer.update()
    return ko

def rendre(namn):
    s = bpy.context.scene
    s.render.filepath = os.path.join(RUT, namn + ('-prove' if PROVE else '') + '.png')
    bpy.ops.render.render(write_still=True)
    print('RENDRA', s.render.filepath, flush=True)

def rom_dag(vindauge=62.0, fyll=7.0, vindaugsfarge=(0.93, 0.96, 1.0)):
    """Pulten: eik, oker vegg, éi bok, lys frå eit vindauge til venstre."""
    boks('bord', (6.0, 6.0, 0.04), (0, 0, -0.02), mat('eik', (0.36, 0.25, 0.15), 0.0, 0.5))
    boks('vegg', (6.0, 0.04, 4.0), (0, 0.75, 1.0), mat('vegg', (0.42, 0.34, 0.23), 0.0, 0.95))
    lin = mat('lin', (0.20, 0.23, 0.26), 0.0, 0.9); ark = mat('ark', (0.82, 0.80, 0.74), 0.0, 0.8)
    boks('bok', (0.150, 0.210, 0.016), (0.20, -0.06, 0.009), lin, (0, 0, math.radians(-12)))
    boks('blokk', (0.142, 0.202, 0.012), (0.1995, -0.0595, 0.009), ark, (0, 0, math.radians(-12)))
    lys('vindauge', (-1.6, -0.5, 0.9), (0.0, 0.0, 0.15), 1.6, vindauge, vindaugsfarge)
    lys('fyll', (0.9, -1.2, 0.8), (0, 0, 0.15), 1.5, fyll, (1.0, 0.95, 0.9))

def rom_studio(golv=True, nokkel=20.0, kant=24.0, fyll=3.0, kort=None, kortstyrke=7.0, kortmaal=(-0.2, 0.02, 0.26)):
    """Mørkt studio: eitt stort mjukt lys ovanfrå venstre, eit kantlys bakfrå venstre, og eit mørkt golv som tek imot gløden.
    Kortet er ei lysflate som messingpunktet speglar."""
    if golv: boks('golv', (9.0, 9.0, 0.04), (0, 0, -0.02), mat('golv', (0.016, 0.016, 0.017), 0.0, 0.45))
    lys('nokkel', (-1.3, -1.3, 1.5), (0, 0, 0.13), 1.8, nokkel, (1.0, 0.97, 0.94))
    lys('kant', (-0.75, 1.30, 0.45), (-0.1, 0, 0.22), 1.1, kant, (0.90, 0.94, 1.0))
    lys('fyll', (0.9, -1.5, 0.3), (0, 0, 0.13), 1.6, fyll, (1.0, 0.96, 0.92))
    if kort is not None: lys('kort', kort, kortmaal, 1.2, kortstyrke, (1.0, 0.97, 0.93))

# ------------------------------------------------------------------ visingane

def vis_studio():
    grunn((1800, 1200), 64, 0.0)
    lampe(FARGE['graabeige'], glod=0.9, under=2.4); rom_studio(nokkel=16.0)
    kamera((-0.52, -0.80, 0.27), (-0.01, 0.0, 0.132), 60, fstop=8.0, fokus=(-0.05, -0.05, 0.2))
    rendre('studio')

def vis_helling():
    for v in (0, 35, 70):
        grunn((1500, 1200), 48, 0.0)
        O = lampe(FARGE['graabeige'], glod=1.2, under=2.6)
        rom_studio(nokkel=14.0, kant=18.0, fyll=2.0, kort=(-2.7, 0.15, 0.32), kortstyrke=10.0)
        hell(O, float(v))
        kamera((-2.3, -0.30, 0.30), (0.0, -0.05, 0.128), 135)
        rendre('helling-%02d' % v)

def vis_detalj():
    grunn((1500, 1000), 64, 0.0)
    O = lampe(FARGE['graabeige'], glod=0.9, under=2.0)
    p = midt(O['11'])
    rom_studio(nokkel=22.0, kant=14.0, fyll=5.0, kort=p + Vector((-1.0, 0.62, -0.19)), kortstyrke=9.0, kortmaal=p)
    kamera(p + Vector((-0.26, -0.16, 0.05)), p + Vector((0.035, -0.020, -0.012)), 85, fstop=9.0, fokus=p)
    rendre('detalj-messing')

def bbpunkt(ob, f):
    """Eit punkt i objektet si romboks, gjeve som brøkar langs x, y og z."""
    P = [ob.matrix_world @ v.co for v in ob.data.vertices]          # hjørna i romet, ikkje den dreidde boksen
    lo = Vector((min(p.x for p in P), min(p.y for p in P), min(p.z for p in P)))
    hi = Vector((max(p.x for p in P), max(p.y for p in P), max(p.z for p in P)))
    return Vector((lo.x + f[0] * (hi.x - lo.x), lo.y + f[1] * (hi.y - lo.y), lo.z + f[2] * (hi.z - lo.z)))

def vis_sprengt():
    """Delane trekte frå kvarandre langs aksane, med ruta vassrett: x langs bjelken, y ut i ruta, z opp.
    Arket er løfta, plata dregen fram og det som sit under bjelken senka, slik at ingenting skjuler noko anna."""
    grunn((1500, 1300), 48, 0.0, verd=0.0)
    O = lampe(FARGE['graabeige'], glod=0.12, under=0.0)
    hell(O, 0.0)
    rom_studio(golv=False, nokkel=34.0, kant=26.0, fyll=12.0)
    x, y, z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
    F = {'11': -0.055 * x, '08': 0.190 * z, '07': -0.190 * y, '10': -0.030 * z, '09': -0.055 * z,
         '06': -0.090 * z, '13': -0.132 * z, 'E': -0.125 * z,
         '04': 0.190 * x, '12': 0.190 * x - 0.034 * z,
         '01': 0.190 * x - 0.055 * z, 'leidning': 0.190 * x - 0.055 * z, '03': 0.190 * x - 0.125 * z, '02': 0.190 * x - 0.195 * z}
    for i, v in F.items():
        if i in O: flytt(O[i], v)
    bpy.context.view_layer.update()
    ko = kamera((0.771, -1.154, 1.195), (-0.02, -0.024, 0.118), 70)
    s = bpy.context.scene
    BR = {'05': (0.80, 0.5, 1.0), '08': (0.95, 0.5, 1.0), '07': (0.04, 0.5, 0.5), '10': (0.0, 0.5, 0.5), '09': (0.0, 0.5, 0.5),
          '06': (0.01, 0.5, 0.5), 'E': (1.0, 0.5, 0.5), '01': (0.25, 0.2, 1.0), '03': (0.3, 0.2, 1.0), '02': (0.3, 0.2, 1.0)}
    anker = {}
    for i, ob in O.items():
        if i in ('under', 'leidning'): continue
        p = bbpunkt(ob, BR[i]) if i in BR else midt(ob)
        if i == '04': p = Vector((0.070, G['YT'] / 1000.0, G['AKSE_H'] / 1000.0 + 0.006)) + F['04']
        c = world_to_camera_view(s, ko, p); anker[i] = [round(c.x, 4), round(1.0 - c.y, 4)]
    json.dump(anker, open(os.path.join(RUT, 'sprengt.json'), 'w'), indent=1)
    rendre('sprengt')

def vis_kveld():
    grunn((1500, 1000), 64, 1.0)
    lampe(FARGE['morkegron'], glod=1.0, under=1.5, stripe=1.5, reine=True); rom_dag(vindauge=0.9, fyll=0.25, vindaugsfarge=(0.55, 0.65, 1.0))
    kamera((-0.52, -0.80, 0.26), (-0.01, 0.0, 0.130), 60)
    rendre('kveld')

def vis_dag():
    for i, (kode, farge) in enumerate(FARGAR):
        grunn((1800, 1200) if i == 0 else (1200, 800), 64 if i == 0 else 48, -0.35, verd=0.10)
        lampe(farge); rom_dag()
        kamera((-0.52, -0.80, 0.26), (-0.01, 0.0, 0.130), 60)
        rendre('rev-b-' + kode)

skaansam()
os.makedirs(RUT, exist_ok=True)
for v in VIS:
    globals()['vis_' + v]()
