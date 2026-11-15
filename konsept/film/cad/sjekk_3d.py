# -*- coding: utf-8 -*-
"""
sjekk_3d.py  ·  les USDZ-fila inn att i ei tom scene og rendrar to bilete av ho (ved 35° og 80°)

Dette er kontrollen av at fila held geometri, material og animasjon når ho blir opna av noko anna enn det som skreiv ho.
  blender.exe -b -P sjekk_3d.py     skriv ut-b/3d/sjekk-35.png og sjekk-80.png
"""
import bpy, os, math
from mathutils import Vector
HER = os.path.dirname(os.path.abspath(__file__)); TRED = os.path.join(HER, 'ut-b', '3d')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.usd_import(filepath=os.path.join(TRED, 'ruta.usdz'))
s = bpy.context.scene
s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.render.threads_mode = 'FIXED'; s.render.threads = 2
s.cycles.samples = 24; s.cycles.use_denoising = True; s.render.resolution_x, s.render.resolution_y = 720, 510
v = bpy.data.worlds.new('v'); s.world = v; v.use_nodes = True; v.node_tree.nodes['Background'].inputs['Color'].default_value = (0.05, 0.05, 0.055, 1)
ld = bpy.data.lights.new('l', 'AREA'); ld.size = 2.0; ld.energy = 60.0
lo = bpy.data.objects.new('l', ld); s.collection.objects.link(lo); lo.location = (-1.0, -1.5, 1.6)
lo.rotation_euler = (Vector((0, 0, 0.15)) - lo.location).to_track_quat('-Z', 'Y').to_euler()
kam = bpy.data.cameras.new('k'); kam.lens = 70
ko = bpy.data.objects.new('k', kam); s.collection.objects.link(ko); ko.location = (-0.75, -1.25, 0.45)
ko.rotation_euler = (Vector((0.0, 0.0, 0.14)) - ko.location).to_track_quat('-Z', 'Y').to_euler(); s.camera = ko
print('SJEKK objekt', sorted(o.name for o in s.objects if o.type == 'MESH'), 'bilete', s.frame_start, s.frame_end, flush=True)
for bilete, namn in ((1, 'sjekk-35'), (180, 'sjekk-80')):
    s.frame_set(bilete); s.render.filepath = os.path.join(TRED, namn + '.png'); bpy.ops.render.render(write_still=True)
    b = [o for o in s.objects if o.name.startswith('Bjelke')]
    if b: print('SJEKK', namn, 'bjelken står ved', [round(x, 3) for x in b[0].matrix_world.translation], flush=True)
