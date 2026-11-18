import bpy
from pathlib import Path
p=Path(__file__).resolve().parent
s=bpy.context.scene
for n in ('Front aperture | warm opal, shorter','Front aperture | deep black recess'):
    o=bpy.data.objects.get(n)
    if o:o.hide_render=True
s.cycles.samples=12
s.render.resolution_x=864
s.render.resolution_y=576
s.render.filepath=str(p/'renders'/'05_no_tip_test.png')
bpy.ops.render.render(write_still=True)
print('CHECK_RENDER',s.render.filepath,flush=True)
