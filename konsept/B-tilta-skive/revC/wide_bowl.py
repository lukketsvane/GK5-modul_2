import bpy,math
from mathutils import Vector
from pathlib import Path
r=Path(__file__).resolve().parent
s=bpy.context.scene;c=s.camera
bowl=bpy.data.objects['Deep smooth underbody | conical bowl']
theta=math.radians(33);co,si=math.cos(theta),math.sin(theta)
for v in bowl.data.vertices:
    wx=v.co.x-.026
    wz=v.co.z-.182
    x=co*wx-si*wz
    z=si*wx+co*wz
    y=v.co.y
    t=min(1,max(0,(-z-.004)/.061))
    factor=1+.48*t**1.35
    x*=factor
    y*=factor
    v.co.x=.026+co*x+si*z
    v.co.y=y
    v.co.z=.182-si*x+co*z
bowl.data.update()
bpy.context.view_layer.update()
def ray(x,y):
    u=x/1536;v=1-y/1024
    direction=(c.rotation_euler.to_matrix()@Vector(((u-.5)*c.data.sensor_width/c.data.lens,(v-.5)*c.data.sensor_width/c.data.lens*(1024/1536),-1))).normalized()
    ok,loc,normal,idx,o,m=s.ray_cast(bpy.context.evaluated_depsgraph_get(),c.location,direction)
    return o.name.split(' | ')[0] if ok else 'EMPTY'
for yy in (622,642,662,680):
    print('HITS',yy,[(xx,ray(xx,yy)) for xx in (704,750,800,850,900,950,1000,1050,1070)],flush=True)
s.render.resolution_x=1024;s.render.resolution_y=682;s.cycles.samples=12
s.render.filepath=str(r/'renders'/'03_wide_bowl_test.png')
bpy.ops.wm.save_as_mainfile(filepath=str(r/'B_RevC_wide.blend'))
bpy.ops.render.render(write_still=True)
print('RENDERED',s.render.filepath)
