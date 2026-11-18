import bpy
from mathutils import Vector
s=bpy.context.scene
c=s.camera
g=bpy.data.objects['Seamless black studio table']
s.view_layers.update()
M=c.rotation_euler.to_matrix()
dg=bpy.context.evaluated_depsgraph_get()
for y in [850,880,900,915,940,965]:
 for x in [600,700,800,900,1000,1100]:
  q=Vector(((x/1536-.5)*c.data.sensor_width/c.data.lens,(.5-y/1024)*c.data.sensor_width/c.data.lens*1024/1536,-1))
  d=(M@q).normalized()
  hit,p,n,i,obj,mi=s.ray_cast(dg,c.location,d)
  print('PX',x,y,'OBJ',obj.name[:12] if hit else '-', 'XY',tuple(round(float(t),3) for t in p[:2]) if hit else None)
