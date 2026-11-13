# -*- coding: utf-8 -*-
"""
render.py  ·  lampa frå CAD-en i same vinkel som skissa (Blender 5.1, Cycles, hovudlaust)

  blender.exe -b -P render.py -- [--prove]

Geometrien er delane frå lampe.py (ut/samla/*.stl). Lyset i ruta er ei visualisering, ikkje ei lysrekning:
plata og den skrå kanten er gjevne ei varm glød. Tala for lyset står i notatet.
"""
import bpy, os, sys, math
HER = os.path.dirname(os.path.abspath(__file__))
PROVE = '--prove' in sys.argv
UT = os.path.join(HER, 'ut')

def skaansam():
    try:
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000040)   # lågaste prioritet
    except Exception:
        pass

def mat(namn, farge, metall=0.0, ruheit=0.5, trans=0.0, ior=1.5, coat=0.0, glod=None, styrke=0.0):
    m = bpy.data.materials.new(namn); m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*farge, 1.0)
    p.inputs['Metallic'].default_value = metall
    p.inputs['Roughness'].default_value = ruheit
    p.inputs['Transmission Weight'].default_value = trans
    p.inputs['IOR'].default_value = ior
    p.inputs['Coat Weight'].default_value = coat
    if glod is not None:
        p.inputs['Emission Color'].default_value = (*glod, 1.0); p.inputs['Emission Strength'].default_value = styrke
    return m

def film_materiale():
    """Arket: mjølkekvitt med varm glød som aukar mot den frie kanten, og striper langs rillene (på tvers av bjelken)."""
    m = bpy.data.materials.new('film'); m.use_nodes = True; nt = m.node_tree
    p = nt.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (0.86, 0.84, 0.80, 1.0); p.inputs['Roughness'].default_value = 0.25
    p.inputs['Transmission Weight'].default_value = 0.22
    tc = nt.nodes.new('ShaderNodeTexCoord')
    ma = nt.nodes.new('ShaderNodeMapping'); ma.inputs['Scale'].default_value = (55.0, 1.2, 1.2)      # stripene går på tvers av bjelken (x)
    nt.links.new(tc.outputs['Object'], ma.inputs['Vector'])
    no = nt.nodes.new('ShaderNodeTexNoise'); no.inputs['Scale'].default_value = 3.0; no.inputs['Detail'].default_value = 5.0
    nt.links.new(ma.outputs['Vector'], no.inputs['Vector'])
    gr = nt.nodes.new('ShaderNodeTexGradient')
    mg = nt.nodes.new('ShaderNodeMapping'); mg.inputs['Rotation'].default_value = (0, 0, math.radians(90)); mg.inputs['Scale'].default_value = (5.5, 5.5, 5.5)
    nt.links.new(tc.outputs['Generated'], mg.inputs['Vector']); nt.links.new(mg.outputs['Vector'], gr.inputs['Vector'])
    cr = nt.nodes.new('ShaderNodeValToRGB')
    cr.color_ramp.elements[0].position = 0.35; cr.color_ramp.elements[0].color = (1.0, 0.86, 0.66, 1.0)
    cr.color_ramp.elements[1].position = 0.75; cr.color_ramp.elements[1].color = (1.0, 0.62, 0.22, 1.0)
    nt.links.new(no.outputs['Fac'], cr.inputs['Fac'])
    mu = nt.nodes.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = 1.15
    nt.links.new(no.outputs['Fac'], mu.inputs[0])
    # sterkare mot den frie kanten: høgda z går frå 0,26 m ved bjelken til 0,15 m ved kanten
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sep.inputs[0])
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.26; mr.inputs['From Max'].default_value = 0.15
    mr.inputs['To Min'].default_value = 0.25; mr.inputs['To Max'].default_value = 2.0
    nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
    m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'
    nt.links.new(mu.outputs[0], m2.inputs[0]); nt.links.new(mr.outputs['Result'], m2.inputs[1])
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

def flate(namn, storleik, pos, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=storleik, location=pos, rotation=rot)
    ob = bpy.context.object; ob.name = namn; ob.data.materials.append(m); return ob

def peik(ob, maal):
    from mathutils import Vector
    r = (Vector(maal) - ob.location).to_track_quat('-Z', 'Y'); ob.rotation_euler = r.to_euler()

def lys(namn, pos, maal, storleik, styrke, farge=(1, 1, 1)):
    ld = bpy.data.lights.new(namn, 'AREA'); ld.size = storleik; ld.energy = styrke; ld.color = farge
    ob = bpy.data.objects.new(namn, ld); bpy.context.collection.objects.link(ob); ob.location = pos; peik(ob, maal); return ob

skaansam()
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'
s.render.threads_mode = 'FIXED'; s.render.threads = 4
s.cycles.samples = 20 if PROVE else 72
s.cycles.use_denoising = True
s.render.resolution_x, s.render.resolution_y = (600, 400) if PROVE else (1440, 960)
s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'

raud = mat('raudbrun', (0.20, 0.028, 0.03), 0.0, 0.42, coat=0.25)
alu = mat('aluminium', (0.80, 0.80, 0.79), 1.0, 0.36)
messing = mat('messing', (0.83, 0.62, 0.30), 1.0, 0.28)
staal = mat('staal', (0.62, 0.62, 0.63), 1.0, 0.3)
svart = mat('svart', (0.015, 0.015, 0.017), 0.0, 0.5)
kork = mat('kork', (0.45, 0.33, 0.22), 0.0, 0.8)
akryl = mat('akryl', (1.0, 0.97, 0.92), 0.0, 0.03, trans=1.0, ior=1.49, glod=(1.0, 0.70, 0.36), styrke=0.12)
led = mat('led', (1.0, 0.9, 0.7), 0.0, 0.5, glod=(1.0, 0.72, 0.38), styrke=30.0)
film = film_materiale()
M = {'01': raud, '02': svart, '03': staal, '04': alu, '05': svart, '06': raud, '07': raud, '08': raud, '09': akryl, '10': film,
     '11': alu, '12': led, '13': messing, '14': kork, 'A': staal, 'B': staal, 'C': staal, 'D': staal, 'E': staal}
for i, m in M.items():
    f = os.path.join(UT, 'samla', i + '.stl')
    if os.path.exists(f): importer(f, m)

bord = mat('bord', (0.10, 0.055, 0.03), 0.0, 0.38, coat=0.15)
vegg = mat('vegg', (0.50, 0.45, 0.40), 0.0, 0.9)
flate('bord', 20.0, (0, 0, 0), bord)
flate('vegg', 20.0, (0, 1.1, 1.0), vegg, (math.radians(90), 0, 0))

# lyset: ei svak, stor flate framme til venstre for forma, og gløden under ruta ned på bordet
lys('fyll', (-0.9, -1.1, 0.9), (0, 0, 0.15), 1.2, 2.6, (1.0, 0.93, 0.85))
lys('kant', (0.7, 0.5, 0.7), (0.05, 0, 0.2), 0.6, 3.0, (1.0, 0.95, 0.9))
u = lys('under', (-0.10, -0.13, 0.15), (-0.10, -0.22, 0.0), 0.20, 1.1, (1.0, 0.64, 0.32))
u.visible_camera = False; u.visible_transmission = False; u.visible_glossy = False
verd = bpy.data.worlds.new('verd'); s.world = verd; verd.use_nodes = True
verd.node_tree.nodes['Background'].inputs['Color'].default_value = (0.02, 0.017, 0.014, 1.0)

VISINGAR = [('skissa', (-0.50, -0.78, 0.25), (-0.03, 0.0, 0.135), 62),
            ('bakfra', (0.52, 0.66, 0.34), (0.02, 0.0, 0.14), 58),
            ('sida', (0.80, -0.32, 0.20), (0.02, -0.02, 0.14), 62)]
os.makedirs(os.path.join(UT, 'render'), exist_ok=True)
for namn, pos, maal, linse in VISINGAR:
    kam = bpy.data.cameras.new('kam-' + namn); kam.lens = linse
    ko = bpy.data.objects.new('kam-' + namn, kam); bpy.context.collection.objects.link(ko)
    ko.location = pos; peik(ko, maal); s.camera = ko
    s.render.filepath = os.path.join(UT, 'render', 'ruta-pa-fot-%s%s.png' % (namn, '-prove' if PROVE else ''))
    bpy.ops.render.render(write_still=True)
    print('render ferdig', s.render.filepath, flush=True)
