import bpy,math
from mathutils import Vector
from pathlib import Path
p=Path(__file__).resolve().parent
s=bpy.context.scene;c=s.camera
for name in ['Independent 2700K work lens | warm lozenge','Inset cavity | shadow black rim']:
    o=bpy.data.objects.get(name)
    if o:bpy.data.objects.remove(o,do_unlink=True)
for name in ['Upper uninterrupted dish | 342 x 322 mm','Deep smooth underbody | conical bowl',
             'Rear left indirect halo | short screened arc','Rear halo metallic shade']:
    o=bpy.data.objects[name]
    o.location.z+=.024
j=bpy.data.objects['J pedestal | shorter seamless casting']
for v in j.data.vertices:
    if v.co.x>0:v.co.x*=.67
    if 0.007<v.co.z<.078:v.co.z=.007+(v.co.z-.007)*.82
j.data.update()
b=bpy.data.materials['Black tabletop'].node_tree.nodes.get('Principled BSDF')
b.inputs['Base Color'].default_value=(.00025,.00020,.00017,1)
bpy.data.objects['Overhead broad graybox'].data.energy=25
bpy.data.objects['Physically motivated warm spot on desk'].data.energy=3.0
bpy.context.view_layer.update()
from mathutils import Vector
def hit_at(x,y):
    U=x/1536; V=1-y/1024
    z=Vector(((U-.5)*c.data.sensor_width/c.data.lens,(V-.5)*c.data.sensor_width/c.data.lens*(1024/1536),-1))
    d=(c.rotation_euler.to_matrix()@z).normalized()
    return s.ray_cast(bpy.context.evaluated_depsgraph_get(),c.location,d)
for y in (622,642,662,682):
    for x in (715,775,840,885,935,990,1040,1080):
        hit,loc,n,idx,ob,m=hit_at(x,y)
        print('SCREEN',x,y,ob.name.split(' | ')[0] if hit else 'BACKGROUND',flush=True)
s.cycles.samples=10
s.render.resolution_x=1024;s.render.resolution_y=682
s.render.filepath=str(p/'renders'/'02_raise_head_no_lens.png')
bpy.ops.wm.save_as_mainfile(filepath=str(p/'B_RevC_raised.blend'))
bpy.ops.render.render(write_still=True)
print('SAVED',s.render.filepath)
