import bpy, math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
o=bpy.data.objects['Deep smooth underbody | conical bowl']
theta=math.radians(33)
co=math.cos(theta)
si=math.sin(theta)
inv=o.matrix_world.inverted()
changed=0
for v in o.data.vertices:
    w=o.matrix_world@v.co
    dx=w.x-.026
    dz=w.z-.206
    x=co*dx-si*dz
    z=si*dx+co*dz
    fx=max(0,min(1,(x+.010)/.060))
    fz=max(0,min(1,(-z-.038)/.027))
    weight=fx*fx*(3-2*fx)*fz*fz*(3-2*fz)
    if weight>0:
        xx=x*(1-.06*weight)
        zz=z+.014*weight
        w=Vector((.026+co*xx+si*zz,w.y,.206-si*xx+co*zz))
        v.co=inv@w
        changed+=1
o.data.update()
print('BOWL_VERTICES_RESHAPED',changed,'of',len(o.data.vertices),flush=True)
s=bpy.context.scene
s.cycles.samples=20
s.render.resolution_x=1024
s.render.resolution_y=682
s.render.filepath=str(R/'renders'/'05_chin_correction_preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Concept_B_RevD.blend'))
bpy.ops.render.render(write_still=True)
print('CHECK_RENDER',s.render.filepath,flush=True)
