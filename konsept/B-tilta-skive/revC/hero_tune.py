import bpy,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parent
s=bpy.context.scene;c=s.camera
c.rotation_euler=(Vector((.010,0,.1605))-c.location).to_track_quat('-Z','Y').to_euler()
right=(c.rotation_euler.to_matrix()@Vector((1,0,0))).normalized()
for name in ('Wide opal work-light inset','Black bevelled surround'):
    o=bpy.data.objects[name]
    center=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
    for v in o.data.vertices:
        rel=v.co-center
        v.co=center+rel+right*(.075*rel.dot(right))
    o.data.update()
old=bpy.data.objects.get('Fine concealed rear-left halo')
if old:bpy.data.objects.remove(old,do_unlink=True)

mat=bpy.data.materials['Rear halo optical insert']
emit=mat.node_tree.nodes.get('Emission')
emit.inputs['Color'].default_value=(1,.34,.13,1)
emit.inputs['Strength'].default_value=1.05
n=190
verts=[];faces=[]
cs=math.cos(math.radians(33));sn=math.sin(math.radians(33))
for row in (0,1):
    for i in range(n+1):
        t=i/n
        ph=math.radians(139+140*t)
        taper=math.sin(math.pi*t)**.85
        z=-11-24*taper*row
        radial=166+(1.1+2.8*taper)*row
        x=radial*math.cos(ph)
        y=(radial*.93)*math.sin(ph)
        verts.append((.026+(cs*x+sn*z)*.001,y*.001,.220+(-sn*x+cs*z)*.001))
for i in range(n):
    faces.append((i,i+1,i+n+2,i+n+1))
mesh=bpy.data.meshes.new('Curved tapered rear halo');mesh.from_pydata(verts,[],faces);mesh.update()
halo=bpy.data.objects.new('Tapered rear-left hidden amber halo',mesh)
bpy.context.collection.objects.link(halo)
halo.data.materials.append(mat)
for face in mesh.polygons:face.use_smooth=True
bpy.data.objects['Local rear halo bounce'].data.energy=4
spot=bpy.data.objects['Physically motivated warm spot on desk']
spot.location=(.18,-.07,.097)
spot.rotation_euler=(Vector((.16,-.10,-.001))-spot.location).to_track_quat('-Z','Y').to_euler()
spot.data.size=.10
spot.data.energy=1.85
s.cycles.samples=20
s.render.resolution_x=1024;s.render.resolution_y=682
s.render.filepath=str(R/'renders'/'06_hero_preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'B_RevC_hero.blend'))
bpy.ops.render.render(write_still=True)
print('DONE',s.render.filepath,flush=True)
