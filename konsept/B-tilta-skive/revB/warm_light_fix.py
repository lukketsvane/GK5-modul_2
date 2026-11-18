import bpy
from mathutils import Vector
from pathlib import Path
p=Path(__file__).resolve().parent
scene=bpy.context.scene
o=bpy.data.objects['Warm 2200K bounce to tabletop']
o.location=(.08,-.10,.045)
o.rotation_euler=(Vector((.07,-.025,-.002))-o.location).to_track_quat('-Z','Y').to_euler()
o.data.energy=1.6
scene.cycles.samples=12
scene.render.resolution_x=768;scene.render.resolution_y=512
scene.render.filepath=str(p/'renders'/'08_light_fixed_test.png')
bpy.ops.render.render(write_still=True)
print('OK')
