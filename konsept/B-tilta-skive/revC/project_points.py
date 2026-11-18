import bpy,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene;c=s.camera
bpy.context.view_layer.update()
t=math.radians(33);co,si=math.cos(t),math.sin(t)
def pt(x,y,z):
    return Vector((.026+(co*x+si*z)*.001,y*.001,.182+(-si*x+co*z)*.001))
for x in [-50,0,40,80,120]:
    for y in [-120,-80,-40,0]:
        p=pt(x,y,-45)
        v=world_to_camera_view(s,c,p)
        print('PT',x,y,'PX',int(v.x*1536),'PY',int((1-v.y)*1024),flush=True)
