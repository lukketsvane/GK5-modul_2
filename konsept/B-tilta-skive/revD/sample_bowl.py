import bpy
from mathutils import Vector
s=bpy.context.scene
c=s.camera
dg=bpy.context.evaluated_depsgraph_get()
b=bpy.data.objects['Deep smooth underbody | conical bowl'].evaluated_get(dg)
C=c.rotation_euler.to_matrix()
def test(x,y):
    q=Vector(((x/1536-.5)*c.data.sensor_width/c.data.lens,(.5-y/1024)*c.data.sensor_width/c.data.lens*1024/1536,-1))
    direction=(C@q).normalized()
    R=b.matrix_world.inverted()
    yes,p,n,i=b.ray_cast(R@c.location,(R.to_3x3()@direction).normalized())
    return bool(yes)
for y in [620,630,640,645,650,655,660,665,670,675,680]:
 print('BOWL_ROW',y,[(x,test(x,y)) for x in [680,695,705,720,735,750,775,800,850,900,950,1000,1050,1070,1090]])
