# -*- coding: utf-8 -*-
"""
render_northern.py  ·  revisjon B i fire av Northern sine fargar, i dagslys frå sida

Biletstilen følgjer det granskinga fann i miljøbileta til Northern: naturleg sidelys frå vindauge, roleg og jordnær
bakgrunn, få rekvisittar, og lampa tend i dagslys. Geometrien er delane frå northern.py (ut-b/samla/*.stl).
Gløden i ruta er ei visualisering, ikkje ei lysrekning.

  blender.exe -b -P render_northern.py -- [--prove]
"""
import bpy, os, sys, math
HER = os.path.dirname(os.path.abspath(__file__))
PROVE = '--prove' in sys.argv
UT = os.path.join(HER, 'ut-b')

FARGAR = [('graabeige', 'grå-beige', (0.33, 0.30, 0.26)), ('morkegron', 'mørkegrøn', (0.022, 0.048, 0.033)),
          ('svart', 'svart', (0.012, 0.012, 0.013)), ('kirsebaer', 'kirsebærraud', (0.19, 0.016, 0.022))]

def skaansam():
    try:
        import ctypes
        k = ctypes.windll.kernel32; k.SetPriorityClass(k.GetCurrentProcess(), 0x40)
    except Exception:
        pass

def mat(namn, farge, metall=0.0, ruheit=0.5, trans=0.0, ior=1.5, coat=0.0, glod=None, styrke=0.0):
    m = bpy.data.materials.new(namn); m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*farge, 1.0); p.inputs['Metallic'].default_value = metall
    p.inputs['Roughness'].default_value = ruheit; p.inputs['Transmission Weight'].default_value = trans
    p.inputs['IOR'].default_value = ior; p.inputs['Coat Weight'].default_value = coat
    if glod is not None:
        p.inputs['Emission Color'].default_value = (*glod, 1.0); p.inputs['Emission Strength'].default_value = styrke
    return m

def film_materiale():
    m = bpy.data.materials.new('film'); m.use_nodes = True; nt = m.node_tree
    p = nt.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (0.88, 0.86, 0.82, 1.0); p.inputs['Roughness'].default_value = 0.25
    p.inputs['Transmission Weight'].default_value = 0.25
    tc = nt.nodes.new('ShaderNodeTexCoord')
    ma = nt.nodes.new('ShaderNodeMapping'); ma.inputs['Scale'].default_value = (55.0, 1.2, 1.2)
    nt.links.new(tc.outputs['Object'], ma.inputs['Vector'])
    no = nt.nodes.new('ShaderNodeTexNoise'); no.inputs['Scale'].default_value = 3.0; no.inputs['Detail'].default_value = 5.0
    nt.links.new(ma.outputs['Vector'], no.inputs['Vector'])
    cr = nt.nodes.new('ShaderNodeValToRGB')
    cr.color_ramp.elements[0].position = 0.35; cr.color_ramp.elements[0].color = (1.0, 0.86, 0.66, 1.0)
    cr.color_ramp.elements[1].position = 0.75; cr.color_ramp.elements[1].color = (1.0, 0.64, 0.26, 1.0)
    nt.links.new(no.outputs['Fac'], cr.inputs['Fac'])
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sep.inputs[0])
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.26; mr.inputs['From Max'].default_value = 0.15
    mr.inputs['To Min'].default_value = 0.3; mr.inputs['To Max'].default_value = 2.0
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
    from mathutils import Vector
    ob.rotation_euler = (Vector(maal) - ob.location).to_track_quat('-Z', 'Y').to_euler()

def lys(namn, pos, maal, storleik, styrke, farge=(1, 1, 1)):
    ld = bpy.data.lights.new(namn, 'AREA'); ld.size = storleik; ld.energy = styrke; ld.color = farge
    ob = bpy.data.objects.new(namn, ld); bpy.context.collection.objects.link(ob); ob.location = pos; peik(ob, maal); return ob

def scene(farge, storleik, prover, fil):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.render.threads_mode = 'FIXED'; s.render.threads = 4
    s.cycles.samples = prover; s.cycles.use_denoising = True
    s.render.resolution_x, s.render.resolution_y = storleik
    s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'; s.view_settings.exposure = -0.35
    kropp = mat('kropp', farge, 0.0, 0.58)                                     # matt pulverlakk, éin farge over heile lekamen
    messing = mat('messing', (0.80, 0.60, 0.30), 1.0, 0.32)
    staal = mat('staal', (0.6, 0.6, 0.6), 1.0, 0.35)
    svart = mat('svart', (0.012, 0.012, 0.013), 0.0, 0.7)
    akryl = mat('akryl', (1.0, 0.97, 0.92), 0.0, 0.03, trans=1.0, ior=1.49, glod=(1.0, 0.70, 0.36), styrke=0.25)
    led = mat('led', (1.0, 0.9, 0.7), 0.0, 0.5, glod=(1.0, 0.72, 0.38), styrke=30.0)
    M = {'01': kropp, '02': svart, '03': staal, '04': kropp, '05': kropp, '06': kropp, '07': akryl, '08': film_materiale(), '09': staal,
         '10': led, '11': messing, 'E': staal, 'leidning': kropp}
    for i, m in M.items():
        f = os.path.join(UT, 'samla', i + '.stl')
        if os.path.exists(f): importer(f, m)
    eik = mat('eik', (0.36, 0.25, 0.15), 0.0, 0.5)
    vegg = mat('vegg', (0.42, 0.34, 0.23), 0.0, 0.95)
    boks('bord', (6.0, 6.0, 0.04), (0, 0, -0.02), eik)
    boks('vegg', (6.0, 0.04, 4.0), (0, 0.75, 1.0), vegg)
    lin = mat('lin', (0.20, 0.23, 0.26), 0.0, 0.9); ark = mat('ark', (0.82, 0.80, 0.74), 0.0, 0.8)
    boks('bok', (0.150, 0.210, 0.016), (0.20, -0.06, 0.009), lin, (0, 0, math.radians(-12)))        # éi bok, slik miljøbileta har
    boks('blokk', (0.142, 0.202, 0.012), (0.1995, -0.0595, 0.009), ark, (0, 0, math.radians(-12)))
    # dagslys frå eit vindauge til venstre, og gløden under ruta
    lys('vindauge', (-1.6, -0.5, 0.9), (0.0, 0.0, 0.15), 1.6, 62.0, (0.93, 0.96, 1.0))
    lys('fyll', (0.9, -1.2, 0.8), (0, 0, 0.15), 1.5, 7.0, (1.0, 0.95, 0.9))
    u = lys('under', (-0.02, -0.11, 0.15), (-0.02, -0.20, 0.0), 0.20, 1.6, (1.0, 0.64, 0.32))
    u.visible_camera = False; u.visible_transmission = False; u.visible_glossy = False
    verd = bpy.data.worlds.new('verd'); s.world = verd; verd.use_nodes = True
    verd.node_tree.nodes['Background'].inputs['Color'].default_value = (0.10, 0.10, 0.11, 1.0)
    kam = bpy.data.cameras.new('kam'); kam.lens = 60
    ko = bpy.data.objects.new('kam', kam); bpy.context.collection.objects.link(ko)
    ko.location = (-0.52, -0.80, 0.26); peik(ko, (-0.01, 0.0, 0.130)); s.camera = ko
    s.render.filepath = fil
    bpy.ops.render.render(write_still=True)
    print('RENDRA', fil, flush=True)

skaansam()
os.makedirs(os.path.join(UT, 'render'), exist_ok=True)
for i, (kode, namn, farge) in enumerate(FARGAR):
    stor = (600, 400) if PROVE else ((1440, 960) if i == 0 else (720, 480))
    scene(farge, stor, 20 if PROVE else (72 if i == 0 else 56), os.path.join(UT, 'render', 'rev-b-%s%s.png' % (kode, '-prove' if PROVE else '')))
