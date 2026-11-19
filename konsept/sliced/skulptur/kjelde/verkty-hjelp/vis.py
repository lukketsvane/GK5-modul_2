import bpy, sys, os, math
from mathutils import Vector
argv = sys.argv[sys.argv.index('--') + 1:]
SRC, OUT = argv[0], argv[1]
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading
sh.light = 'STUDIO'; sh.studio_light = 'paint.sl'; sh.color_type = 'SINGLE'; sh.single_color = (0.85, 0.80, 0.72)
sh.show_cavity = True; sh.show_shadows = True
sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = 600
sc.view_settings.view_transform = 'Standard'
cd = bpy.data.cameras.new('c'); cd.type = 'ORTHO'
cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
info = []
for i in range(1, 13):
    for ob in list(bpy.data.objects):
        if ob.type != 'CAMERA': bpy.data.objects.remove(ob)
    bpy.ops.import_scene.gltf(filepath=f'{SRC}/skulptur-{i:02d}.glb')
    obs = [o for o in sc.objects if o.type == 'MESH']
    pts = [o.matrix_world @ Vector(c) for o in obs for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    c = (mn + mx) / 2; s = mx - mn
    tri = sum(len(o.data.polygons) for o in obs)
    info.append(f'skulptur-{i:02d}: {s.x:.3f} x {s.y:.3f} x {s.z:.3f} · {tri} flater')
    D = Vector((0.9, -1.4, 0.6)).normalized()
    cam.location = c + D * 50 * max(s)
    cam.rotation_euler = (-D).to_track_quat('-Z', 'Y').to_euler()
    cd.ortho_scale = max(s) * 1.45; cd.clip_end = 1000 * max(s)
    sc.render.filepath = f'{OUT}/s{i:02d}.png'
    bpy.ops.render.render(write_still=True)
open(f'{OUT}/info.txt', 'w').write('\n'.join(info))
print('\n'.join(info))
