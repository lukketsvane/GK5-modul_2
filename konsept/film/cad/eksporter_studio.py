# -*- coding: utf-8 -*-
"""
eksporter_studio.py  ·  Ruta som GLB til studiosida (ruta/index.html)

Same delar som eksporter_3d.py, pluss dei som ligg inni (ballast, flatstong, stripe, stoppskrue og bremseskrue),
og to animasjonar som sida styrer med éin glidar:

  Vipp   gruppa «Blad» dreier om røyret frå 0° til 80°, jamt. Tida i sekund er hellinga delt på 24
  Opne   delane blir trekte frå kvarandre langs retningane dei blir sette saman i, jamt over 2,5 sekund

Utan animasjon står lampa samla med 35° helling.

  blender.exe -b -P eksporter_studio.py     skriv ut-b/3d/ruta-studio.glb og ruta-studio.kontroll.json
"""
import bpy, os, sys, math, json
from mathutils import Vector

HER = os.path.dirname(os.path.abspath(__file__))
UT = os.path.join(HER, 'ut-b'); NETT = os.path.join(UT, 'samla'); TRED = os.path.join(UT, '3d')
G = json.load(open(os.path.join(UT, 'geometri.json'), encoding='utf-8'))
AKSE = Vector((0.0, G['YT'] / 1000.0, G['AKSE_H'] / 1000.0))
t = math.radians(G['VINKEL'])
OPP = Vector((0.0, -math.sin(t), math.cos(t)))               # ut av oversida på ruta ved 35°
X, Z = Vector((1, 0, 0)), Vector((0, 0, 1))
LAKK = (0.40, 0.350, 0.285); LYS = (1.0, 0.71, 0.43)
FAST = {'01': 'Fot', '02': 'Botnlok', '03': 'Ballast', '04': 'Royr', '12': 'Stoppskrue', 'leidning': 'Leidning'}
BLAD = {'05': 'Bjelke', '06': 'Bjelkelok', '07': 'Lysleiar', '08': 'Prismeark', '09': 'Flatstong', '10': 'Stripe', '11': 'Messingpunkt', '13': 'Bremseskrue', 'E': 'Skruar'}
OPNE = {'Prismeark': 0.085 * OPP, 'Stripe': -0.035 * OPP, 'Flatstong': -0.055 * OPP, 'Bjelkelok': -0.085 * OPP, 'Bremseskrue': -0.100 * OPP, 'Skruar': -0.125 * OPP,
        'Messingpunkt': -0.055 * X, 'Stoppskrue': -0.030 * Z, 'Fot': -0.060 * Z, 'Leidning': -0.060 * Z, 'Ballast': -0.115 * Z, 'Botnlok': -0.170 * Z}
FORENKLA = {'Leidning': 0.22, 'Royr': 0.45}
FPS = 24
VIPP = (1, 81)                 # bilete 1 er 0°, bilete 81 er 80°
OPNING = (101, 161)            # bilete 101 er samla, bilete 161 er heilt opna
KVILE = 1 + int(G['VINKEL'])   # biletet der fila blir skriven: 35° og samla

def mat(namn, farge, metall=0.0, ruheit=0.5, alfa=1.0, glod=None, styrke=0.0):
    m = bpy.data.materials.new(namn); m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*farge, 1.0); p.inputs['Metallic'].default_value = metall; p.inputs['Roughness'].default_value = ruheit
    p.inputs['Alpha'].default_value = alfa
    if glod is not None:
        p.inputs['Emission Color'].default_value = (*glod, 1.0); p.inputs['Emission Strength'].default_value = styrke
    if alfa < 1.0:
        for k, v in (('blend_method', 'BLEND'), ('surface_render_method', 'BLENDED')):
            try: setattr(m, k, v)
            except Exception: pass
    return m

def importer(fil, namn, m):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.stl_import(filepath=fil, global_scale=0.001)
    ob = bpy.context.selected_objects[0]; ob.name = namn; ob.data.name = namn
    ob.data.materials.clear(); ob.data.materials.append(m)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if namn in FORENKLA:
        mo = ob.modifiers.new('forenkla', 'DECIMATE'); mo.ratio = FORENKLA[namn]; bpy.ops.object.modifier_apply(modifier=mo.name)
    try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
    except Exception: pass
    return ob

def tom(namn, pos, forelder=None):
    e = bpy.data.objects.new(namn, None); bpy.context.collection.objects.link(e); e.location = pos
    if forelder is not None: e.parent = forelder
    return e

def spor(ob, namn, eigenskap, noklar):
    """Nøklar på éin eigenskap, lagde ned som eit NLA-spor. Spor med same namn blir éin animasjon i GLB-fila.
    Éin nøkkel per bilete, rekna rett fram mellom endepunkta. Då går rørsla jamt same kva kurve Blender legg mellom
    nøklane. Med berre to nøklar vart kurva mjuk i endane, og 35° på glidaren var 32,5° i modellen."""
    ob.animation_data_create()
    (b0, v0), (b1, v1) = noklar[0], noklar[-1]
    for bilete in range(int(b0), int(b1) + 1):
        k = (bilete - b0) / float(b1 - b0)
        setattr(ob, eigenskap, tuple(a + (b - a) * k for a, b in zip(v0, v1))); ob.keyframe_insert(eigenskap, frame=bilete)
    akt = ob.animation_data.action; akt.name = namn + '_' + ob.name
    sp = ob.animation_data.nla_tracks.new(); sp.name = namn
    st = sp.strips.new(namn, int(noklar[0][0]), akt); st.name = namn
    ob.animation_data.action = None
    setattr(ob, eigenskap, noklar[0][1])

def gyldige(op, ynske):
    k = set(op.get_rna_type().properties.keys())
    return {a: b for a, b in ynske.items() if a in k}

bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene; s.render.fps = FPS; s.frame_start = 1; s.frame_end = OPNING[1]
try: bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
except Exception as e: print('JAMN RØRSLE IKKJE SETT', e)
lakk = mat('Lakk', LAKK, 0.0, 0.5); staal = mat('Staal', (0.50, 0.50, 0.52), 1.0, 0.4)
M = {'01': lakk, '04': lakk, '05': lakk, '06': lakk, '02': mat('Pute', (0.012, 0.012, 0.013), 0.0, 0.8), '03': staal, '12': staal, '13': staal,
     '07': mat('Akryl', (1.0, 0.98, 0.95), 0.0, 0.06, alfa=0.32, glod=LYS, styrke=0.5), '08': mat('Ark', (0.92, 0.74, 0.52), 0.0, 0.35, glod=LYS, styrke=0.9),
     '09': mat('Alu', (0.72, 0.72, 0.74), 1.0, 0.35), '10': mat('Stripe', (1.0, 0.9, 0.7), 0.0, 0.5, glod=LYS, styrke=2.5),
     '11': mat('Messing', (0.78, 0.52, 0.20), 1.0, 0.30), 'E': mat('Skrue', (0.02, 0.02, 0.02), 0.6, 0.5), 'leidning': mat('Leidning', LAKK, 0.0, 0.9)}
rot = tom('Ruta', (0, 0, 0)); fast = tom('Fast', (0, 0, 0), rot); blad = tom('Blad', AKSE, rot)
O = {}
for i, namn in list(FAST.items()) + list(BLAD.items()):
    f = os.path.join(NETT, i + '.stl')
    if not os.path.exists(f): continue
    ob = importer(f, namn, M[i]); O[namn] = ob
    bpy.context.view_layer.update()
    forelder = blad if i in BLAD else fast
    ob.parent = forelder; ob.matrix_parent_inverse = forelder.matrix_world.inverted()
blad.rotation_mode = 'XYZ'
spor(blad, 'Vipp', 'rotation_euler', [(VIPP[0], (math.radians(0.0 - G['VINKEL']), 0.0, 0.0)), (VIPP[1], (math.radians(80.0 - G['VINKEL']), 0.0, 0.0))])
blad.rotation_euler = (0.0, 0.0, 0.0)                         # utan animasjon står ruta ved 35°, slik delane ligg i fila
for namn, v in OPNE.items():
    if namn in O: spor(O[namn], 'Opne', 'location', [(OPNING[0], (0.0, 0.0, 0.0)), (OPNING[1], tuple(v))])
s.frame_set(KVILE); bpy.context.view_layer.update()
os.makedirs(TRED, exist_ok=True)
ut = os.path.join(TRED, 'ruta-studio.glb')
val = dict(filepath=ut, export_format='GLB', export_animations=True, export_yup=True, export_apply=False, export_materials='EXPORT', export_normals=True,
           export_texcoords=False, export_cameras=False, export_lights=False, export_extras=False, export_animation_mode='NLA_TRACKS', export_nla_strips=True,
           export_force_sampling=True, export_frame_range=False, export_bake_animation=False, export_optimize_animation_size=True,
           export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6, export_draco_position_quantization=14, export_draco_normal_quantization=10,      # lita fil, rask lasting
           export_current_frame=False)
bpy.ops.export_scene.gltf(**gyldige(bpy.ops.export_scene.gltf, val))
# kontroll: les fila og sjå kva animasjonar ho har
import struct
d = open(ut, 'rb').read(); n = struct.unpack('<I', d[12:16])[0]; J = json.loads(d[20:20 + n].decode('utf-8'))
anim = {}
for a in J.get('animations', []):
    tid = 0.0
    for sa in a['samplers']: tid = max(tid, J['accessors'][sa['input']]['max'][0])
    anim[a.get('name', '?')] = dict(kanalar=len(a['channels']), sekund=round(tid, 3))
blad_node = next((x for x in J['nodes'] if x.get('name') == 'Blad'), {})
def les(i):
    a = J['accessors'][i]; bv = J['bufferViews'][a['bufferView']]; o = 20 + n + 8 + bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    k = {'SCALAR': 1, 'VEC3': 3, 'VEC4': 4}[a['type']]
    return [struct.unpack_from('<%df' % k, d, o + j * 4 * k) for j in range(a['count'])]
avvik = None                    # største avstand i gradar mellom hellinga i fila og den jamne rørsla (bilete 1 er 0°, eitt bilete er éin grad)
for a in J.get('animations', []):
    if a.get('name') != 'Vipp': continue
    for ch in a['channels']:
        if ch['target']['path'] != 'rotation': continue
        sa = a['samplers'][ch['sampler']]
        avvik = max(abs(2 * math.degrees(math.atan2(q[0], q[3])) + G['VINKEL'] - (tt * FPS - VIPP[0])) for (tt,), q in zip(les(sa['input']), les(sa['output'])))
rap = dict(fil=os.path.basename(ut), kB=round(len(d) / 1e3), nodar=len(J['nodes']), nett=len(J['meshes']), material=sorted(m['name'] for m in J['materials']),
           animasjonar=anim, vipp_storste_avvik_gradar=None if avvik is None else round(avvik, 4), blad_i_kvile=blad_node.get('rotation'),
           trekantar=sum(len(o.data.polygons) for o in O.values()))
json.dump(rap, open(os.path.join(TRED, 'ruta-studio.kontroll.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('STUDIO', json.dumps(rap, ensure_ascii=False), flush=True)
