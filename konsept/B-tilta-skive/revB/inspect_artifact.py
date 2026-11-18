import bpy,math
from mathutils import Vector
s=bpy.context.scene;c=s.camera
w=864;h=576
for x in (575,585,595,605,615):
    for y in (325,340,355,370):
        u=x/w;v=1-y/h
        a=(u-.5)*c.data.sensor_width/c.data.lens
        b=(v-.5)*c.data.sensor_width/c.data.lens*h/w
        direction=c.matrix_world.to_3x3()@Vector((a,b,-1))
        hit,point,norm,index,obj,mat=s.ray_cast(bpy.context.evaluated_depsgraph_get(),c.location,direction)
        print(x,y,obj.name if hit else 'NOTHING',tuple(round(a,3) for a in point) if hit else '',flush=True)
