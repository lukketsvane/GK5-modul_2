# -*- coding: utf-8 -*-
"""vis_blender.py · syner Raup-modellen: hovudkroppen og filmen, og (om fila finst) skalet i snitt.

    blender.exe -b -P cad/vis_blender.py -- [--prove]

Skriv render/cad_*.png. Svart bakgrunn som rendrane av byggjesettet, Cycles på CPU med fire trådar og lågaste prioritet.
"""
import bpy, sys, os, math
from mathutils import Vector

try:
    import ctypes
    k = ctypes.windll.kernel32; h = k.GetCurrentProcess()
    k.SetPriorityClass(h, 0x40); k.SetProcessAffinityMask(h, 0xFC)
except Exception:
    pass

ARG = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
PROVE = '--prove' in ARG
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(R, 'produksjon'); UT = os.path.join(R, 'render')


def nullstill():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'
    s.render.threads_mode = 'FIXED'; s.render.threads = 4
    s.cycles.samples = 24 if PROVE else 96
    s.cycles.use_denoising = True
    s.render.resolution_x, s.render.resolution_y = (800, 800) if PROVE else (1600, 1600)
    s.render.film_transparent = False
    s.view_settings.view_transform = 'AgX'
    w = bpy.data.worlds.new('w'); s.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (0.004, 0.004, 0.004, 1)
    return s


def mat(namn, farge, ruheit=0.6, trans=0.0, emisjon=0.0, alpha=1.0):
    m = bpy.data.materials.new(namn); m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*farge, 1)
    p.inputs['Roughness'].default_value = ruheit
    p.inputs['Transmission Weight'].default_value = trans
    if emisjon:
        p.inputs['Emission Color'].default_value = (1.0, 0.78, 0.52, 1)
        p.inputs['Emission Strength'].default_value = emisjon
    return m


def last(fil, m):
    bpy.ops.wm.stl_import(filepath=os.path.join(P, fil))
    o = bpy.context.selected_objects[0]
    o.scale = (0.001, 0.001, 0.001)          # mm -> m
    o.data.materials.append(m)
    bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
    return o


def lys_og_kamera(s, mal, avstand, azimut, elev, linse=60):
    for namn, pos, e, storleik in [('nokkel', (-0.45, -0.55, 0.55), 160, 0.5), ('kant', (0.5, 0.4, 0.45), 90, 0.4),
                                   ('fyll', (0.6, -0.6, 0.15), 25, 0.8)]:
        d = bpy.data.lights.new(namn, 'AREA'); d.energy = e; d.size = storleik
        o = bpy.data.objects.new(namn, d); o.location = pos
        o.rotation_euler = (Vector(mal) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
        s.collection.objects.link(o)
    kd = bpy.data.cameras.new('kam'); kd.lens = linse
    k = bpy.data.objects.new('kam', kd); s.collection.objects.link(k); s.camera = k
    a, e = math.radians(azimut), math.radians(elev)
    k.location = Vector(mal) + avstand * Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    k.rotation_euler = (Vector(mal) - k.location).to_track_quat('-Z', 'Y').to_euler()


def golv(s):
    bpy.ops.mesh.primitive_plane_add(size=4)
    g = bpy.context.active_object
    g.data.materials.append(mat('golv', (0.02, 0.02, 0.02), 0.8))


def render(s, namn):
    s.render.filepath = os.path.join(UT, namn + ('-prove' if PROVE else '') + '.png')
    bpy.ops.render.render(write_still=True)
    print('skreiv', s.render.filepath, flush=True)


# 1. Modellen slik CAD-en står: kroppen og filmen
s = nullstill(); golv(s)
last('raup_hovudkropp_ytre.stl', mat('kropp', (0.80, 0.76, 0.70), 0.75))
last('raup_diffusor.stl', mat('film', (0.95, 0.93, 0.90), 0.25, trans=0.85))
lys_og_kamera(s, (0.0, -0.03, 0.12), 0.95, -35, 18)
render(s, 'cad_modell')

# 2. Skalet i snitt, om det finst
if os.path.exists(os.path.join(P, 'raup_skal_P1S.stl')):
    s = nullstill(); golv(s)
    SNITT = mat('snitt', (0.62, 0.26, 0.16), 0.6)       # snittflata i rust, så veggen les
    o = last('raup_skal_P1S.stl', mat('skal', (0.80, 0.76, 0.70), 0.75))
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    # snitt gjennom midten (y = senter), fjern halvparten mot kameraet, fyll snittet
    cy = sum((o.matrix_world @ v.co).y for v in o.data.vertices) / len(o.data.vertices)
    bpy.ops.mesh.bisect(plane_co=(0, cy, 0), plane_no=(0, -1, 0), use_fill=True, clear_inner=False, clear_outer=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    o.data.materials.append(SNITT)
    for poly in o.data.polygons:                 # snittflatene får rust-farge
        if abs(poly.normal.y) > 0.999 and abs((o.matrix_world @ poly.center).y - cy) < 1e-4:
            poly.material_index = 1
    lys_og_kamera(s, (0.0, cy, 0.10), 0.95, -20, 15)
    render(s, 'cad_skal_snitt')
