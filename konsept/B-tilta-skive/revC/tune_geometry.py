import bpy,math
from mathutils import Vector
from pathlib import Path
r=Path(__file__).resolve().parent
s=bpy.context.scene;c=s.camera
upward=Vector((.010,0,.157))
c.rotation_euler=(upward-c.location).to_track_quat('-Z','Y').to_euler()
for name in ['Upper uninterrupted dish | 342 x 322 mm','Deep smooth underbody | conical bowl',
             'Rear left indirect halo | short screened arc','Rear halo metallic shade',
             'Hidden structural hinge bridge | visual envelope']:
    o=bpy.data.objects.get(name)
    if o:o.location.z+=.014

j=bpy.data.objects['J pedestal | shorter seamless casting']
for v in j.data.vertices:
    if v.co.x>0:v.co.x*=.88
j.data.update()

for name in ['Inlaid almond-shaped luminous aperture','Dark optical recess | attached to bowl',
             'New offset rear-left amber diffuser']:
    o=bpy.data.objects.get(name)
    if o:bpy.data.objects.remove(o,do_unlink=True)

m=bpy.data.materials['Matte warm graphite | anodized aluminum'].node_tree.nodes.get('Principled BSDF')
m.inputs['Base Color'].default_value=(.049,.048,.048,1)
b=bpy.data.materials['Black tabletop'].node_tree.nodes.get('Principled BSDF')
b.inputs['Base Color'].default_value=(.00011,.000095,.000085,1)
bpy.data.objects['Physically motivated warm spot on desk'].data.energy=2.8

# New rear-left low-glare diffuser, thin and warm rather than white exposed sheet.
def arc(name,a0,a1,radius,z0,z1):
    count=160;vv=[];ff=[]
    pitch=math.radians(33);co,si=math.cos(pitch),math.sin(pitch)
    for z in (z0,z1):
        for i in range(count+1):
            t=i/count;phi=math.radians(a0+(a1-a0)*t)
            outside=1+3*math.sin(math.pi*t)
            x=(radius+outside)*math.cos(phi)
            y=(radius*.93+outside)*math.sin(phi)
            vv.append((.026+(co*x+si*z)*.001,y*.001,.220+(-si*x+co*z)*.001))
    for i in range(count):ff.append((i,i+1,i+count+2,i+count+1))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vv,[],ff);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o)
    o.data.materials.append(bpy.data.materials['Rear halo optical insert'])
    for p in mesh.polygons:p.use_smooth=True
bpy.data.materials['Rear halo optical insert'].node_tree.nodes.get('Emission').inputs['Strength'].default_value=1.75
arc('Fine concealed rear-left halo',142,249,166,-14,-31)
bpy.data.objects['Local rear halo bounce'].data.energy=5

bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
bowl=bpy.data.objects['Deep smooth underbody | conical bowl'].evaluated_get(deps)
M=bowl.matrix_world.copy();I=M.inverted()

def sample_bowl(x,y):
    U=x/1536;V=1-y/1024
    vec=Vector(((U-.5)*c.data.sensor_width/c.data.lens,(V-.5)*c.data.sensor_width/c.data.lens*(1024/1536),-1))
    dr=(c.rotation_euler.to_matrix()@vec).normalized()
    org=I@c.location
    d=(I.to_3x3()@dr).normalized()
    hit,loc,n,i=bowl.ray_cast(org,d)
    if not hit:
        return None,None
    world=M@loc
    nworld=(I.transposed().to_3x3()@n).normalized()
    return world,nworld

def inlay(name,rx,ry,offset,mat):
    cx,cy=904,645
    n=160
    rs=(0,.20,.37,.55,.72,.87,.96,1)
    vv=[];ff=[];fails=0
    for R in rs:
        for i in range(n):
            t=2*math.pi*i/n
            x=cx+rx*R*math.cos(t)
            y=cy+ry*R*math.sin(t)
            point,norm=sample_bowl(x,y)
            if point is None:
                fails+=1
                raise RuntimeError('inlay outside bowl '+str((x,y)))
            vv.append(point+norm*offset)
    for k in range(len(rs)-1):
        for i in range(n):
            a=k*n+i;b=k*n+(i+1)%n
            ff.append((a,b,b+n,a+n))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vv,[],ff);mesh.update()
    o=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    for p in mesh.polygons:p.use_smooth=True
    print('INLAY',name,'FACES',len(mesh.polygons),'OUT_OF_BOWL',fails,flush=True)

inlay('Black bevelled surround',148,12,.0004,bpy.data.materials['Light trap | almost black'])
inlay('Wide opal work-light inset',144,9.6,.00065,bpy.data.materials['Real inset diffused warm-white optic'])

s.cycles.samples=20;s.render.resolution_x=1024;s.render.resolution_y=682
s.render.filepath=str(r/'renders'/'05_tuned_a.png')
bpy.ops.wm.save_as_mainfile(filepath=str(r/'B_RevC_tuned.blend'))
bpy.ops.render.render(write_still=True)
print('RENDERED',s.render.filepath,flush=True)
