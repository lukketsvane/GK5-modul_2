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
    p.inputs['Transmission Weight'].default_value = 0.55
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
    mu = nt.nodes.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = 2.2
    nt.links.new(no.outputs['Fac'], mu.inputs[0])
    nt.links.new(cr.outputs['Color'], p.inputs['Emission Color']); nt.links.new(mu.outputs[0], p.inputs['Emission Strength'])
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
s.cycles.samples = 24 if PROVE else 160
s.cycles.use_denoising = True
s.render.resolution_x, s.render.resolution_y = (640, 427) if PROVE else (1536, 1024)
s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'

raud = mat('raudbrun', (0.20, 0.028, 0.03), 0.0, 0.42, coat=0.25)
alu = mat('aluminium', (0.80, 0.80, 0.79), 1.0, 0.36)
messing = mat('messing', (0.83, 0.62, 0.30), 1.0, 0.28)
staal = mat('staal', (0.62, 0.62, 0.63), 1.0, 0.3)
svart = mat('svart', (0.015, 0.015, 0.017), 0.0, 0.5)
kork = mat('kork', (0.45, 0.33, 0.22), 0.0, 0.8)
akryl = mat('akryl', (1.0, 0.97, 0.92), 0.0, 0.03, trans=1.0, ior=1.49, glod=(1.0, 0.70, 0.36), styrke=0.6)
led = mat('led', (1.0, 0.9, 0.7), 0.0, 0.5, glod=(1.0, 0.72, 0.38), styrke=30.0)
film = film_materiale()
M = {'01': raud, '02': svart, '03': staal, '04': alu, '05': svart, '06': raud, '07': raud, '08': raud, '09': akryl, '10': film,
     '11': alu, '12': led, '13': messing, '14': kork, 'A': staal, 'B': staal, 'C': staal, 'D': staal, 'E': staal}
for i, m in M.items():
    f = os.path.join(UT, 'samla', i + '.stl')
    if os.path.exists(f): importer(f, m)

bord = mat('bord', (0.10, 0.055, 0.03), 0.0, 0.38, coat=0.15)
vegg = mat('vegg', (0.50, 0.45, 0.40), 0.0, 0.9)
flate('bord', 4.0, (0, 0, 0), bord)
flate('vegg', 4.0, (0, 0.55, 1.0), vegg, (math.radians(90), 0, 0))

# lyset: ei svak, stor flate framme til venstre for forma, og gløden under ruta ned på bordet
lys('fyll', (-0.9, -1.1, 0.9), (0, 0, 0.15), 1.2, 9.0, (1.0, 0.93, 0.85))
lys('kant', (0.7, -0.5, 0.6), (0.05, 0, 0.2), 0.5, 4.0, (1.0, 0.95, 0.9))
lys('under', (-0.08, -0.07, 0.17), (-0.08, -0.10, 0.0), 0.22, 3.2, (1.0, 0.66, 0.34))
verd = bpy.data.worlds.new('verd'); s.world = verd; verd.use_nodes = True
verd.node_tree.nodes['Background'].inputs['Color'].default_value = (0.02, 0.017, 0.014, 1.0)

kam = bpy.data.cameras.new('kam'); kam.lens = 52
ko = bpy.data.objects.new('kam', kam); bpy.context.collection.objects.link(ko)
ko.location = (-0.50, -0.78, 0.25); peik(ko, (-0.03, 0.0, 0.135)); s.camera = ko
kam.dof.use_dof = False

os.makedirs(os.path.join(UT, 'render'), exist_ok=True)
s.render.filepath = os.path.join(UT, 'render', 'ruta-pa-fot-prove.png' if PROVE else 'ruta-pa-fot.png')
bpy.ops.render.render(write_still=True)
print('render ferdig', s.render.filepath)
