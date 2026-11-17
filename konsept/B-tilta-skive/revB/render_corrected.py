import bpy
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent
s=bpy.context.scene
o=bpy.data.objects['Warm 2200K bounce to tabletop']
o.location=(.08,-.10,.045)
o.rotation_euler=(Vector((.07,-.025,-.002))-o.location).to_track_quat('-Z','Y').to_euler()
o.data.energy=1.6
s.cycles.samples=52
s.render.resolution_x=1536
s.render.resolution_y=1024
s.render.filepath=str(p/'renders'/'B_REV_B_HERO_CYCLES.png')
bpy.ops.wm.save_as_mainfile(filepath=str(p/'Concept_B_RevB.blend'))
bpy.ops.render.render(write_still=True)
print('FINAL HERO CHECKED',s.render.filepath,flush=True)
cam=s.camera
cam.location=(.48,-.98,.30)
cam.rotation_euler=(Vector((.025,0,.14))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=78
s.cycles.samples=36
s.render.resolution_x=1280
s.render.resolution_y=853
s.render.filepath=str(p/'renders'/'B_REV_B_PROFILE_CYCLES.png')
bpy.ops.render.render(write_still=True)
print('FINAL PROFILE CHECKED',s.render.filepath,flush=True)
