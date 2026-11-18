import bpy
from mathutils import Vector
from pathlib import Path
DIR=Path(__file__).resolve().parent
scene=bpy.context.scene
scene.cycles.samples=72
scene.render.resolution_x=1536
scene.render.resolution_y=1024
scene.view_settings.exposure=-.84
scene.view_settings.look='AgX - Medium High Contrast'
warm=bpy.data.objects['Warm 2200K bounce to tabletop']
warm.location=(.13,-.055,.105)
warm.rotation_euler=(Vector((.11,-.025,0))-warm.location).to_track_quat('-Z','Y').to_euler()
warm.data.energy=1.7
cam=scene.camera
cam.location=(.61,-1.16,.37)
cam.rotation_euler=(Vector((.03,0,.14))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=74
scene.render.filepath=str(DIR/'renders'/'B_REV_B_HERO_CYCLES.png')
bpy.ops.wm.save_as_mainfile(filepath=str(DIR/'Concept_B_RevB.blend'))
bpy.ops.render.render(write_still=True)
print('FINAL_HERO',scene.render.filepath,flush=True)
cam.location=(.48,-.98,.30)
cam.rotation_euler=(Vector((.025,0,.14))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=78
scene.render.filepath=str(DIR/'renders'/'B_REV_B_PROFILE_CYCLES.png')
bpy.ops.render.render(write_still=True)
print('FINAL_PROFILE',scene.render.filepath,flush=True)
