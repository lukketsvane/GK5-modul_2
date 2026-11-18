import bpy, math, json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parent
(RENDER:=ROOT/'renders').mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name,color,rough=.72,metal=.26,texture=False):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=metal
    if texture:
        noise=m.node_tree.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=220
        noise.inputs['Roughness'].default_value=.85
        bump=m.node_tree.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.12
        bump.inputs['Distance'].default_value=.000065
        m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
        m.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return m

def emat(name,color,strength):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    nt=m.node_tree
    nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial')
    e=nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value=(*color,1)
    e.inputs['Strength'].default_value=strength
    nt.links.new(e.outputs[0],out.inputs['Surface'])
    return m

TOP=material('Matte warm graphite | anodized aluminum',(0.105,.098,.092),.79,.30,True)
BOWL=material('Deep bowl | dark charcoal metal',(.059,.052,.046),.72,.40,True)
STEM=material('One-piece J | graphite',(.075,.068,.064),.82,.24,True)
BLK=material('Light trap | almost black',(.010,.009,.008),.88,.10)
LENS=emat('Real inset diffused warm-white optic',(1,.64,.34),8)
HALO=emat('Rear halo optical insert',(1,.42,.16),3.5)
FLOOR=material('Black tabletop',(.006,.005,.005),.83,.04)

pitch=math.radians(33.0)
cs,sn=math.cos(pitch),math.sin(pitch)
headcenter=Vector((.026,0,.182))
def hpt(x,y,z):
    return headcenter + Vector((cs*x+sn*z,y,-sn*x+cs*z))*.001

def mesh_obj(name,verts,faces,mat,smooth=True):
    m=bpy.data.meshes.new(name)
    m.from_pydata(verts,[],faces)
    m.update()
    o=bpy.data.objects.new(name,m)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    if smooth:
        for p in m.polygons:p.use_smooth=True
    return o

N=256
def lathe(name,rings,mat,closed_top=False,closed_bottom=False):
    verts=[];faces=[]
    for z,ax,by in rings:
        for i in range(N):
            phi=2*math.pi*i/N
            verts.append(hpt(ax*math.cos(phi),by*math.sin(phi),z))
    for k in range(len(rings)-1):
        for i in range(N):
            a=k*N+i;b=k*N+(i+1)%N
            faces.append((a,b,b+N,a+N))
    if closed_bottom:
        verts.append(hpt(0,0,rings[0][0]))
        a=len(verts)-1
        for i in range(N):faces.append((a,i,(i+1)%N))
    if closed_top:
        verts.append(hpt(0,0,rings[-1][0]))
        a=len(verts)-1;offset=(len(rings)-1)*N
        for i in range(N):faces.append((a,offset+(i+1)%N,offset+i))
    return mesh_obj(name,verts,faces,mat)

# A solid ultrathin crown, with only ~2.4 mm of organic camber and no centre emblem.
rings=[(-.0,170,161),(.40,166,158),(1.20,160,152),(1.75,152,144),
       (2.20,140,133),(2.65,124,117),(3.0,103,97),(3.2,80,76),
       (3.38,54,52),(3.50,25,24),(3.57,0.08,0.08)]
crown=lathe('Upper uninterrupted dish | 342 x 322 mm',rings,TOP,True,False)
thin=crown.modifiers.new('Real pressed aluminum thickness','SOLIDIFY')
thin.thickness=.0017;thin.offset=-1
# Solid underbody with a tapered cowl, rather than the former flat pancake.
profile=[(-65,83,80),(-64,96,90),(-59,108,101),(-49,122,114),
         (-37,135,126),(-26,147,137),(-17,157,147),
         (-9,164,154),(-4,168,159)]
bowl=lathe('Deep smooth underbody | conical bowl',profile,BOWL,False,True)
solid=bowl.modifiers.new('Shell wall approx 2mm','SOLIDIFY')
solid.thickness=.0022
solid.offset=-1

# Rounded continuous J casting.
def bezier(a,b,c,d,count):
    pts=[]
    for i in range(1,count+1):
        t=i/count;u=1-t
        pts.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*d[0],
                    u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*d[1]))
    return pts

outline=[(-124,7),(-124,201)]
# round-headed upright similar to photo: domed 50mm across
for i in range(1,41):
    a=math.pi-math.pi*i/40
    outline.append((-99+25*math.cos(a),201+25*math.sin(a)))
outline.append((-74,96))
# interior concave rounded bend from inner upright to top of foot
for i in range(1,29):
    a=math.pi+math.pi/2*i/28
    outline.append((-33+41*math.cos(a),96+41*math.sin(a)))
outline.append((63,55))
outline+=bezier((63,55),(76,55),(80,52),(80,42),12)
outline.append((80,16))
outline+=bezier((80,16),(80,10),(75,7),(66,7),10)
outline.append((-124,7))
zfront=-34;zback=+34
verts=[Vector((x*.001,y*.001,z*.001)) for y in (zfront,zback) for x,z in outline[:-1]]
m=len(outline)-1
faces=[tuple(range(m-1,-1,-1)),tuple(range(m,2*m))]
for i in range(m):
    j=(i+1)%m
    faces.append((i,j,j+m,i+m))
jfoot=mesh_obj('Monolithic J pedestal | continuous casting',verts,faces,STEM,False)
bv=jfoot.modifiers.new('Radius on outside edges','BEVEL')
bv.width=.003;bv.segments=5
wn=jfoot.modifiers.new('Balanced face normals','WEIGHTED_NORMAL')
wn.keep_sharp=True

# A lightly visible sub-shade behind the far-left back lip for indirect halo.
# Short curved physical emitter, NOT a full glowing perimeter.
def arc_mesh(name,a0,a1,rxa,rya,za,zb,material):
    v=[];f=[];n=120
    for z in (za,zb):
        for i in range(n+1):
            a=math.radians(a0+(a1-a0)*i/n)
            v.append(hpt(rxa*math.cos(a),rya*math.sin(a),z))
    for i in range(n):f.append((i,i+1,i+n+2,i+n+1))
    return mesh_obj(name,v,f,material)
arc_mesh('Rear left indirect halo | short screened arc',135,247,166,155,-14,-10,HALO)
arc_mesh('Rear halo metallic shade',135,247,163,153,-21,-18,BOWL)

# Floor
bpy.ops.mesh.primitive_plane_add(size=4,location=(0,0,-.0018))
ground=bpy.context.object
ground.name='Seamless black studio table'
ground.data.materials.append(FLOOR)

def focus(obj,point):
    obj.rotation_euler=(Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size,color,target,shape='DISK'):
    ld=bpy.data.lights.new(name,'AREA')
    ld.energy=power;ld.color=color;ld.shape=shape
    ld.size=size
    o=bpy.data.objects.new(name,ld)
    bpy.context.collection.objects.link(o)
    o.location=loc
    focus(o,target)
    return o

area('Key softbox left',(-.53,-.42,.68),36,.72,(1,.96,.92),(.025,0,.17))
area('Overhead broad graybox',(.47,.19,.78),40,.94,(1,.97,.93),(.015,0,.18))
area('Small camera right fill',(.50,-.60,.27),12,.45,(1,.92,.83),(.05,-.05,.13))
area('Local rear halo bounce',(-.27,.07,.34),7,.23,(1,.42,.17),(-.075,.05,.15))
area('Physically motivated warm spot on desk',(.09,-.07,.085),2.1,.14,(1,.48,.19),(.095,-.09,0))
bpy.context.scene.world=bpy.data.worlds.new('Black void')
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.004,.004,.004,1)
world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.20

# High-end 70mm product camera.
camdata=bpy.data.cameras.new('70mm product camera')
cam=bpy.data.objects.new('70mm product camera',camdata)
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera=cam
camdata.type='PERSP'
camdata.lens=72
camdata.sensor_width=36
cam.location=(.63,-1.15,.405)
focus(cam,(.010,0,.145))

scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=20
scene.cycles.use_denoising=True
scene.render.resolution_x=1024
scene.render.resolution_y=682
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=-.65

for x in (0,40,75,100):
    for y in (-30,-70,-100,-140):
        p=hpt(x,y,-47)
        v=world_to_camera_view(scene,cam,p)
        print('SAMPLE',x,y,'SCREEN',(round(v.x,3),round(1-v.y,3)),'WORLD',tuple(round(t,3) for t in p),flush=True)

scene.render.filepath=str(RENDER/'00_unlensed.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'B_RevC.blend'))
bpy.ops.render.render(write_still=True)
print('RENDERED',scene.render.filepath,flush=True)
