# -*- coding: utf-8 -*-
"""
segl_render.py  ·  ekte rendringar av CAD-en i Cycles (Blender 5.1, hovudlaust)

  blender.exe -b -P segl_render.py -- <nettingmappe> <utmappe> [skisse|sprengt|dag] [--prove]

skisse   same kamera som skissa (passa: 79,7 mm, sjå kontroll/segl_mot_skisse.json), lys på, mørkt rom
sprengt  delane trekte frå kvarandre langs monteringsvegen, nøytralt studiolys
dag      same kamera, lys av, mjukt dagslys frå venstre

Netting: STL frå segl_cad.py (mm). Materiale: fin struktur pulverlakk i terrakotta, aluminium, LED-stripa sjølvlysande 2700 K.
"""
import bpy, os, sys, math
from mathutils import Vector, Matrix

arg = sys.argv[sys.argv.index('--') + 1:]
NETT, UT = arg[0], arg[1]
VIS = [a for a in arg[2:] if not a.startswith('--')] or ['skisse']
PROVE = '--prove' in arg
os.makedirs(UT, exist_ok=True)

TERRA = (0.36, 0.072, 0.036)      # lineær RGB, lesen ut av skissa (sRGB ca 0,66 0,28 0,19)
KAM = dict(f_mm=3400.0 * 36.0 / 1536.0, C=(-379.4, -1093.13, 212.16), theta=25.48, phi=3.48)


def nullstill():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    try:
        p = bpy.context.preferences.addons['cycles'].preferences
        p.compute_device_type = 'CUDA'; p.get_devices()
        for d in p.devices:
            d.use = d.type != 'CPU'
        s.cycles.device = 'GPU'
    except Exception as e:
        print('GPU ikkje tilgjengeleg:', e)
    s.cycles.samples = 64 if PROVE else 384
    s.cycles.use_denoising = True
    s.render.resolution_x, s.render.resolution_y = 1536, 1024
    s.render.film_transparent = False
    s.view_settings.view_transform = 'AgX'
    s.view_settings.look = 'AgX - Medium High Contrast' if 'AgX - Medium High Contrast' in [l for l in ()] else 'None'
    s.unit_settings.system = 'METRIC'
    return s


def mat_lakk(namn, farge, ruheit=0.62):
    m = bpy.data.materials.new(namn)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree; b = nt.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*farge, 1)
    b.inputs['Roughness'].default_value = ruheit
    # fin struktur: liten støy i normalen
    tex = nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value = 2500.0; tex.inputs['Detail'].default_value = 4.0
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.08; bump.inputs['Distance'].default_value = 0.00005
    nt.links.new(tex.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    # avrunda kantar i skyggjaren (lakkerte kantar er aldri knivskarpe)
    try:
        bev = nt.nodes.new('ShaderNodeBevel'); bev.inputs['Radius'].default_value = 0.0003
        nt.links.new(bev.outputs['Normal'], bump.inputs['Normal'])
    except Exception:
        pass
    return m


def mat_alu():
    m = bpy.data.materials.new('alu')
    try:
        m.use_nodes = True
    except Exception:
        pass
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (0.75, 0.75, 0.76, 1); b.inputs['Metallic'].default_value = 1.0; b.inputs['Roughness'].default_value = 0.35
    return m


def mat_led(styrke):
    m = bpy.data.materials.new('led')
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree; nt.nodes.clear()
    em = nt.nodes.new('ShaderNodeEmission'); bb = nt.nodes.new('ShaderNodeBlackbody'); bb.inputs['Temperature'].default_value = 2700
    nt.links.new(bb.outputs['Color'], em.inputs['Color']); em.inputs['Strength'].default_value = styrke
    out = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    return m


def hent(namn, mat):
    bpy.ops.wm.stl_import(filepath=os.path.join(NETT, namn + '.stl'))
    o = bpy.context.selected_objects[0]
    o.name = namn
    o.scale = (0.001, 0.001, 0.001)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.clear(); o.data.materials.append(mat)
    try:
        bpy.ops.object.shade_auto_smooth(angle=math.radians(30))
    except Exception:
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30))
        except Exception:
            pass
    return o


def kamera_skisse(s):
    th, ph = math.radians(KAM['theta']), math.radians(KAM['phi'])
    fwd = Vector((math.sin(th) * math.cos(ph), math.cos(th) * math.cos(ph), -math.sin(ph)))
    C = Vector(KAM['C']) * 0.001
    cam = bpy.data.cameras.new('kam'); cam.lens = KAM['f_mm']; cam.sensor_width = 36.0; cam.sensor_fit = 'HORIZONTAL'
    o = bpy.data.objects.new('kam', cam); s.collection.objects.link(o)
    o.location = C
    o.rotation_euler = fwd.to_track_quat('-Z', 'Y').to_euler()
    s.camera = o
    return o


def bord_og_vegg(s, bordfarge=(0.10, 0.07, 0.05), veggfarge=(0.05, 0.055, 0.06)):
    bpy.ops.mesh.primitive_plane_add(size=4.0, location=(0.12, 0.3, 0.0))
    bord = bpy.context.object; bord.name = 'bord'
    mb = bpy.data.materials.new('bord')
    try:
        mb.use_nodes = True
    except Exception:
        pass
    pb = mb.node_tree.nodes.get('Principled BSDF'); pb.inputs['Base Color'].default_value = (*bordfarge, 1); pb.inputs['Roughness'].default_value = 0.45
    bord.data.materials.append(mb)
    bpy.ops.mesh.primitive_plane_add(size=4.0, location=(0.12, 0.42, 1.0), rotation=(math.radians(90), 0, 0))
    vegg = bpy.context.object; vegg.name = 'vegg'
    mv = bpy.data.materials.new('vegg')
    try:
        mv.use_nodes = True
    except Exception:
        pass
    pv = mv.node_tree.nodes.get('Principled BSDF'); pv.inputs['Base Color'].default_value = (*veggfarge, 1); pv.inputs['Roughness'].default_value = 0.9
    vegg.data.materials.append(mv)


def verd(s, styrke=0.0, farge=(0, 0, 0)):
    w = bpy.data.worlds.new('w'); s.world = w
    try:
        w.use_nodes = True
        bg = w.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value = (*farge, 1); bg.inputs['Strength'].default_value = styrke
    except Exception:
        w.color = farge


def flatelys(s, namn, pos, mot, storleik, watt, farge=(1, 1, 1)):
    l = bpy.data.lights.new(namn, 'AREA'); l.size = storleik; l.energy = watt; l.color = farge
    o = bpy.data.objects.new(namn, l); s.collection.objects.link(o)
    o.location = Vector(pos)
    o.rotation_euler = (Vector(mot) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    return o


def lampe(s, led_styrke, utskyv=None):
    lakk = mat_lakk('terrakotta', TERRA)
    obj = {}
    for k in ('D01', 'D02', 'E02', 'E03'):
        obj[k] = hent(k, lakk)
    obj['E01'] = hent('E01', lakk)         # beraren pulverlakkert i same farge (H4: éin farge)
    obj['E01-LED'] = hent('E01-LED', mat_led(led_styrke))
    for k in ('H02', 'H04'):
        obj[k] = hent(k, mat_alu())
    obj['H06'] = hent('H06', mat_lakk('leidning', (0.02, 0.02, 0.02), 0.5))
    if utskyv:
        for k, v in utskyv.items():
            if k in obj:
                obj[k].location = Vector(v) * 0.001
    return obj


def render(s, namn):
    s.render.filepath = os.path.join(UT, namn + '.png')
    bpy.ops.render.render(write_still=True)
    print('skrive', s.render.filepath)


for vis in VIS:
    s = nullstill()
    if vis == 'skisse':
        verd(s, 0.02, (0.6, 0.65, 0.75))
        lampe(s, led_styrke=260.0)
        bord_og_vegg(s, bordfarge=(0.16, 0.10, 0.06), veggfarge=(0.10, 0.11, 0.13))
        kamera_skisse(s)
        flatelys(s, 'vindauge', (-0.9, -0.6, 0.9), (0.12, 0.05, 0.1), 0.8, 22.0, (0.85, 0.9, 1.0))
        render(s, '01_segl_skissevising')
    elif vis == 'dag':
        verd(s, 0.25, (0.7, 0.75, 0.85))
        lampe(s, led_styrke=0.0)
        bord_og_vegg(s, bordfarge=(0.30, 0.20, 0.12), veggfarge=(0.45, 0.50, 0.58))
        kamera_skisse(s)
        flatelys(s, 'vindauge', (-0.9, -0.6, 0.9), (0.12, 0.05, 0.1), 1.2, 180.0, (0.9, 0.95, 1.0))
        render(s, '02_segl_dagslys')
    elif vis == 'sprengt':
        verd(s, 0.0)
        ut = {'E02': (-60, 0, 0), 'E03': (-60, 0, 45), 'E01': (0, 0, 70), 'E01-LED': (0, 0, 70), 'H04': (0, 0, 110),
              'D02': (0, 120, 0), 'H02': (0, 55, 0)}
        lampe(s, led_styrke=8.0, utskyv=ut)
        cam = bpy.data.cameras.new('kam'); cam.lens = 70.0
        o = bpy.data.objects.new('kam', cam); s.collection.objects.link(o)
        o.location = Vector((-0.55, -0.95, 0.55)); tgt = Vector((0.08, 0.06, 0.12))
        o.rotation_euler = (tgt - o.location).to_track_quat('-Z', 'Y').to_euler(); s.camera = o
        flatelys(s, 'nøkkel', (-0.6, -0.7, 0.9), (0.1, 0.05, 0.1), 1.0, 45.0)
        flatelys(s, 'kant', (0.6, 0.6, 0.5), (0.1, 0.05, 0.1), 0.6, 18.0)
        render(s, '03_segl_sprengt')
