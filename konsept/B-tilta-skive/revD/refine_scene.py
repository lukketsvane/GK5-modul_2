import bpy, math
from pathlib import Path
from mathutils import Vector
from math import sin, cos, pi

R=Path(__file__).resolve().parent
(R/'renders').mkdir(exist_ok=True)
s=bpy.context.scene
cam=s.camera
top=bpy.data.materials['Matte warm graphite | anodized aluminum'].node_tree.nodes.get('Principled BSDF')
top.inputs['Base Color'].default_value=(.049,.047,.045,1)
top.inputs['Metallic'].default_value=0
top.inputs['Roughness'].default_value=.69
j=bpy.data.objects['J pedestal | shorter seamless casting']
for vertex in j.data.vertices:
    if vertex.co.x>0:
        vertex.co.x*=.83
j.data.update()

for name in ('Wide opal work-light inset','Black bevelled surround','Tapered rear-left hidden amber halo','Rear left indirect halo | short screened arc'):
    if name=='Tapered rear-left hidden amber halo':
        original=bpy.data.objects.get(name)
        if original:
            points=[v.co.copy() for v in original.data.vertices]
    x=bpy.data.objects.get(name)
    if x:bpy.data.objects.remove(x,do_unlink=True)

n=len(points)//2
verts=[];faces=[];Nrows=18
attributes=[]
for row in range(Nrows):
    r=row/(Nrows-1)
    for i in range(n):
        t=i/(n-1)
        v=points[i].lerp(points[i+n],r)
        shift=max(0,(t-.70)/.30)
        v.x-=.017*(shift**2)
        v.z-=.012*(shift**2)
        verts.append(v)
        intensity=.83*(max(0,sin(pi*t))**.68)*((1-r)**2.25)
        attributes.append(float(intensity))
for row in range(Nrows-1):
    for i in range(n-1):
        a=row*n+i
        faces.append((a,a+1,a+n+1,a+n))
mesh=bpy.data.meshes.new('Rear cavity | gradient surface')
mesh.from_pydata(verts,[],faces)
mesh.update()
a=mesh.attributes.new('heat',type='FLOAT',domain='POINT')
for i,h in enumerate(attributes):
    a.data[i].value=h
m=bpy.data.materials.new('Warm reflected light, not a flat orange surface')
m.use_nodes=True
tree=m.node_tree;tree.nodes.clear()
attr=tree.nodes.new('ShaderNodeAttribute')
attr.attribute_name='heat'
bs=tree.nodes.new('ShaderNodeBsdfPrincipled')
bs.inputs['Base Color'].default_value=(.055,.037,.023,1)
bs.inputs['Metallic'].default_value=.34
bs.inputs['Roughness'].default_value=.74
em=tree.nodes.new('ShaderNodeEmission')
em.inputs['Color'].default_value=(1,.68,.41,1)
em.inputs['Strength'].default_value=6.2
mix=tree.nodes.new('ShaderNodeMixShader')
out=tree.nodes.new('ShaderNodeOutputMaterial')
tree.links.new(attr.outputs['Fac'],mix.inputs[0])
tree.links.new(bs.outputs[0],mix.inputs[1])
tree.links.new(em.outputs[0],mix.inputs[2])
tree.links.new(mix.outputs[0],out.inputs['Surface'])
o=bpy.data.objects.new('Rear cavity | graded physical reflector',mesh)
bpy.context.collection.objects.link(o)
mesh.materials.append(m)
for face in mesh.polygons:face.use_smooth=True
rearLight=bpy.data.objects['Local rear halo bounce']
rearLight.data.energy=2.5

bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
bowl=bpy.data.objects['Deep smooth underbody | conical bowl'].evaluated_get(dg)
mi=bowl.matrix_world.inverted()
cam_rot=cam.rotation_euler.to_matrix()
def ray_bowl(x,y):
    u=x/1536;v=1-y/1024
    q=Vector(((u-.5)*cam.data.sensor_width/cam.data.lens,(v-.5)*cam.data.sensor_width/cam.data.lens*1024/1536,-1))
    direction=(cam_rot@q).normalized()
    hit,loc,n,idx=bowl.ray_cast(mi@cam.location,(mi.to_3x3()@direction).normalized())
    if not hit:
        raise RuntimeError('Lens cannot lie on physical bowl at screen pixel '+str((round(x,1),round(y,1))))
    return bowl.matrix_world@loc,(mi.transposed().to_3x3()@n).normalized()

lensRings=(0,.18,.34,.49,.65,.78,.88,.94,1)
N=192
def make_lens(name,rx,ry,raise_mm,mat):
    v=[];f=[]
    for k,rad in enumerate(lensRings):
        for i in range(N):
            phi=2*pi*i/N
            u=rad*cos(phi)
            w=rad*sin(phi)
            x=888+rx*u
            y=650+14.5*u+ry*w
            pos,norm=ray_bowl(x,y)
            v.append(pos+norm*raise_mm*.001)
    for k in range(len(lensRings)-1):
        for i in range(N):
            a=k*N+i;b=k*N+(i+1)%N
            f.append((a,b,b+N,a+N))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],f);mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    mesh.materials.append(mat)
    for p in mesh.polygons:p.use_smooth=True
    return ob

rim=bpy.data.materials.new('Chamfered dark rim')
rim.use_nodes=True
rb=rim.node_tree.nodes.get('Principled BSDF')
rb.inputs['Base Color'].default_value=(.007,.006,.005,1)
rb.inputs['Roughness'].default_value=.67
rb.inputs['Metallic'].default_value=.08
diff=bpy.data.materials.new('Warm opal diffuser with centre glow')
diff.use_nodes=True
nt=diff.node_tree;nt.nodes.clear()
attr=nt.nodes.new('ShaderNodeAttribute')
attr.attribute_name='radial'
ramp=nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=0
ramp.color_ramp.elements[0].color=(1,.86,.69,1)
ramp.color_ramp.elements[1].position=1
ramp.color_ramp.elements[1].color=(.83,.59,.41,1)
em=nt.nodes.new('ShaderNodeEmission')
em.inputs['Strength'].default_value=11
out=nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(attr.outputs['Fac'],ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'],em.inputs['Color'])
nt.links.new(em.outputs[0],out.inputs['Surface'])
make_lens('Lens recess cutout | dark surround',182,13.8,.58,rim)
l=make_lens('Real bowl-following opal almond 360x24px',180,12,.86,diff)
rad=l.data.attributes.new(name='radial',type='FLOAT',domain='POINT')
for k,t in enumerate(lensRings):
    for i in range(N):
        rad.data[k*N+i].value=t*t
bpy.context.view_layer.update()

floor=bpy.data.materials['Black tabletop']
fb=floor.node_tree.nodes.get('Principled BSDF')
fb.inputs['Base Color'].default_value=(.000012,.000010,.000009,1)
fb.inputs['Roughness'].default_value=.96
spot=bpy.data.objects['Physically motivated warm spot on desk']
spot.location=(.10,-.02,.13)
spot.rotation_euler=(Vector((.08,-.01,-.001))-spot.location).to_track_quat('-Z','Y').to_euler()
spot.data.shape='DISK'
spot.data.size=.10
spot.data.energy=34
s.cycles.samples=24
s.render.resolution_x=1024
s.render.resolution_y=682
s.render.resolution_percentage=100
s.render.filepath=str(R/'renders'/'01_material_fit_preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Concept_B_RevD.blend'))
bpy.ops.render.render(write_still=True)
print('PREVIEW_DONE',s.render.filepath,flush=True)
