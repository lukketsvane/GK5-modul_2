import bpy, sys, json, math, bmesh
from mathutils import Vector, Matrix

a = json.loads(open(sys.argv[sys.argv.index('--') + 1], encoding='utf8').read())
for ob in list(bpy.data.objects): bpy.data.objects.remove(ob)
bpy.ops.import_scene.gltf(filepath=a['glb'])
obs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
for o in bpy.context.scene.objects: o.select_set(o in obs)
bpy.context.view_layer.objects.active = obs[0]
if len(obs) > 1: bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active
for o in list(bpy.context.scene.objects):
    if o is not ob: bpy.data.objects.remove(o)
ob.parent = None
bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
me = ob.data
R = Matrix.Rotation(math.radians(a.get('dreiZ', 0)), 4, 'Z')
if a.get('dreiX'): R = Matrix.Rotation(math.radians(a['dreiX']), 4, 'X') @ R
me.transform(R)
xs = [v.co for v in me.vertices]
mn = Vector((min(v.x for v in xs), min(v.y for v in xs), min(v.z for v in xs)))
mx = Vector((max(v.x for v in xs), max(v.y for v in xs), max(v.z for v in xs)))
s = mx - mn
k = a['storst'] / max(s) if 'storst' in a else a['hogd'] / s.z
me.transform(Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
me.transform(Matrix.Scale(k, 4))
me.update()


def tett():
    if not a.get('voxel'): return
    m = ob.modifiers.new('r', 'REMESH'); m.mode = 'VOXEL'; m.voxel_size = a['voxel']
    bpy.context.view_layer.objects.active = ob; bpy.ops.object.modifier_apply(modifier=m.name)
    n = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    if n > a.get('tris', 30000):
        d = ob.modifiers.new('d', 'DECIMATE'); d.ratio = a.get('tris', 30000) / n
        bpy.ops.object.modifier_apply(modifier=d.name)


def kutt(lag):
    bpy.ops.object.select_all(action='DESELECT')
    lag.select_set(False)
    m = ob.modifiers.new('b', 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = lag; m.solver = 'EXACT'
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(lag)


H = s.z * k
if a.get('kappTopp'):
    z = a['kappTopp']
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z + 1000)); c = bpy.context.active_object; c.scale = (4000, 4000, 2000); bpy.ops.object.transform_apply(scale=True)
    kutt(c)
if a.get('kappBotn'):
    z = a['kappBotn']
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z - 1000)); c = bpy.context.active_object; c.scale = (4000, 4000, 2000); bpy.ops.object.transform_apply(scale=True)
    kutt(c)
if a.get('radius'):
    bpy.ops.mesh.primitive_cylinder_add(radius=a['radius'], depth=4000, location=(0, 0, 0), vertices=192)
    c = bpy.context.active_object
    bpy.ops.object.select_all(action='DESELECT')
    m = ob.modifiers.new('rr', 'BOOLEAN'); m.operation = 'INTERSECT'; m.object = c; m.solver = 'EXACT'
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(c)
for h in a.get('hol', []):
    if h['slag'] == 'kule':
        bpy.ops.mesh.primitive_uv_sphere_add(radius=h['r'], location=h['senter'], segments=48, ring_count=24)
    elif h['slag'] == 'boks':
        bpy.ops.mesh.primitive_cube_add(size=1, location=h['senter']); c = bpy.context.active_object; c.scale = h['storleik']; bpy.ops.object.transform_apply(scale=True)
    else:
        bpy.ops.mesh.primitive_cylinder_add(radius=h['r'], depth=h['lengd'], location=h['senter'], vertices=48)
        d = Vector(h.get('retning', (0, 0, 1))).normalized()
        bpy.context.active_object.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        bpy.ops.object.transform_apply(rotation=True)
    kutt(bpy.context.active_object)
tett()
xs = [v.co for v in ob.data.vertices]
mn = Vector((min(v.x for v in xs), min(v.y for v in xs), min(v.z for v in xs)))
mx = Vector((max(v.x for v in xs), max(v.y for v in xs), max(v.z for v in xs)))
ob.data.transform(Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
bm = bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.triangulate(bm, faces=bm.faces[:])
bm.to_mesh(ob.data); bm.free()
bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True)
bpy.ops.wm.stl_export(filepath=a['ut'], export_selected_objects=True, apply_modifiers=True, global_scale=1.0, ascii_format=False)
print('PREP', a['ut'], 'mm', [round(v, 1) for v in (mx - mn)], 'tri', len(ob.data.polygons), 'k', round(k, 2))

