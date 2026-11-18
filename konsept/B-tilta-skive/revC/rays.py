import bpy
from mathutils import Vector
s=bpy.context.scene;c=s.camera
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
for x,y in [(887,650),(870,635),(880,665),(704,632),(1068,665),(750,640),(940,650),(940,690),(875,700),(800,620),(530,480),(470,260)]:
 u=x/1536;v=1-y/1024
 vctr=Vector(((u-.5)*c.data.sensor_width/c.data.lens,(v-.5)*c.data.sensor_width/c.data.lens*(1024/1536),-1))
 vec=(c.rotation_euler.to_matrix()@vctr).normalized()
 hit,p,n,ix,obj,mat=s.ray_cast(dg,c.location,vec)
 print('PIX',x,y,'OBJ',obj.name if hit else '-','XYZ',[round(float(t),4) for t in p] if hit else '-',flush=True)
