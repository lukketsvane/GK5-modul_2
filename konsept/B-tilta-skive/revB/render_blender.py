import bpy, math
from mathutils import Vector
from pathlib import Path

DIR=Path(__file__).resolve().parent
OUT=DIR/'renders'
OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials):
    bpy.data.materials.remove(m)

S=0.001
tilt=math.radians(34)
cs,sn=math.cos(tilt),math.sin(tilt)
def hw(x,y,z):
    return ((34+cs*x+sn*z)*S,y*S,(175-sn*x+cs*z)*S)
def obj(name,verts,faces,mat,smooth=True):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    o=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    if smooth:
        for p in mesh.polygons:p.use_smooth=True
    return o

def pbr(name,color,roughness=.51,metallic=.45):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metallic
    bs.inputs['Roughness'].default_value=roughness
    return m

def glow(name,rgb,strength):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    nt=m.node_tree;nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial')
    em=nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value=(*rgb,1)
    em.inputs['Strength'].default_value=strength
    nt.links.new(em.outputs[0],out.inputs['Surface'])
    return m

topmat=pbr('Graphite | soft mineral powdercoat',(0.195,0.182,0.169),.71,.30)
shellmat=pbr('Graphite | deep satin metal',(0.125,0.110,0.101),.52,.50)
base=pbr('Pedestal | warm charcoal',(0.115,0.106,0.099),.66,.33)
lipmat=pbr('Interior | dark optical baffle',(0.026,0.025,0.025),.67,.25)
workmat=pbr('Work optic | tinted diffused PC',(0.125,0.113,0.099),.8,.05)
amber=glow('2200 K | window',(1.0,.49,.195),12)
rear=glow('2200 K | rear leak',(1.0,.39,.15),9)
floor_mat=pbr('Stage | graphite',(0.018,0.016,0.015),.80,.03)

N=192
def head_rings(name,rings,mat,cap_top=False,cap_bottom=False):
    v=[];f=[]
    for z,a,b in rings:
        for j in range(N):
            phi=2*math.pi*j/N
            v.append(hw(a*math.cos(phi),b*math.sin(phi),z))
    for i in range(len(rings)-1):
        for j in range(N):
            k=i*N+j;h=i*N+(j+1)%N
            f.append((k,h,h+N,k+N))
    if cap_bottom:
        v.append(hw(0,0,rings[0][0]))
        i0=len(v)-1
        for j in range(N):f.append((i0,(j+1)%N,j))
    if cap_top:
        v.append(hw(0,0,rings[-1][0]))
        i0=len(v)-1; k=(len(rings)-1)*N
        for j in range(N):f.append((i0,k+j,k+(j+1)%N))
    return obj(name,v,f,mat)

rings=[(-40,92,85),(-39,101,93),(-36,112,103),(-31,124,113),
       (-24,136,125),(-15,147,136),(-4,156,144),(4,161,148),(9.3,164,151)]
head_rings('Bowl | continuously tapered aluminum',rings,shellmat,True,False)
head_rings('Surface | uninterrupted shallow crown',
           [(9.1,166.0,152.0),(10.5,169,154),(11.7,170,155.3),
            (13.0,168.5,154),(14.2,160,147),(15.0,135,124),
            (15.7,101,93),(16.1,65,60),(16.3,15,13)],
           topmat,False,True)
head_rings('Shadow gap behind crown',[(8.5,161.5,148.8),(9.8,162.1,148.9)],lipmat)

def cross_section(z):
    for (z1,a1,b1),(z2,a2,b2) in zip(rings,rings[1:]):
        if z1<=z<=z2:
            t=(z-z1)/(z2-z1)
            return a1+(a2-a1)*t,b1+(b2-b1)*t
    return rings[0][1:]
def window(name,begin,end,midz,thickness,offset,mat,count=100):
    verts=[]
    for row in (0,1):
        for i in range(count+1):
            t=i/count
            phi=math.radians(begin+(end-begin)*t)
            width=thickness*(max(0,math.sin(math.pi*t))**.55)
            z=midz+(row-.5)*max(.24,width)
            ra,rb=cross_section(z)
            x=(ra+offset)*math.cos(phi)
            y=(rb+offset)*math.sin(phi)
            verts.append(hw(x,y,z))
    faces=[(i,i+1,i+count+2,i+count+1) for i in range(count)]
    return obj(name,verts,faces,mat)
window('Deep dark cutout | front',-145,-36,-25.5,11.5,1.20,lipmat)
window('ONE amber aperture | front',-138,-43,-25.5,7.0,1.55,amber)

def halo_ribbon(name,begin,end,z,r1,r2,mat,count=140):
    verts=[];faces=[]
    for row,r in enumerate((r1,r2)):
        for i in range(count+1):
            t=math.radians(begin+(end-begin)*i/count)
            verts.append(hw(r*math.cos(t),r*.92*math.sin(t),z))
    for i in range(count):faces.append((i,i+1,i+count+2,i+count+1))
    return obj(name,verts,faces,mat)
halo_ribbon('Rear-left hidden rim warmth',118,234,9.75,162.0,166.2,rear)
halo_ribbon('Rear opaque inner shield',118,234,8.6,157.1,162.1,lipmat)

# The task optical opening is below the bowl and dimmed for the ambient hero.
def ellipse_disk(name,ax,by,z,mat):
    v=[hw(0,0,z)]
    for i in range(N):
        t=2*math.pi*i/N
        v.append(hw(ax*math.cos(t),by*math.sin(t),z))
    f=[(0,1+i,1+(i+1)%N) for i in range(N)]
    return obj(name,v,f,mat)
ellipse_disk('Flush serviceable work optic',78,57,-40.1,workmat)
ellipse_disk('Invisible LED baffle',64,45,-40.4,lipmat)

def bez(a,b,c,d,steps=8):
    result=[]
    for i in range(1,steps+1):
        t=i/steps;u=1-t
        result.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*d[0],
                       u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*d[1]))
    return result

profile=[(-123,1),(57,1)]
profile+=bez((57,1),(69,1),(76,5),(77,14))
profile.append((77,27))
profile+=bez((77,27),(77,35),(71,38),(62,39))
profile.append((-39,39))
profile+=bez((-39,39),(-62,39),(-73,50),(-73,80),12)
profile.append((-73,207))
profile+=bez((-73,207),(-73,222),(-83,231),(-96,231))
profile+=bez((-96,231),(-109,231),(-119,222),(-119,208))
profile.append((-119,19))
profile+=bez((-119,19),(-119,10),(-122,3),(-123,1))
# Extruded J form, rounded edge with production-like cast profiles.
V=[];F=[]; m=len(profile)
for y in (-29,29):
    for x,z in profile:V.append((x*S,y*S,z*S))
F.append(tuple(range(m-1,-1,-1)))
F.append(tuple(range(m,2*m)))
for i in range(m):
    j=(i+1)%m
    F.append((i,j,j+m,i+m))
stem=obj('One-piece J | foot and upright',V,F,base,False)
bev=stem.modifiers.new('Continuous soft casting radii','BEVEL')
bev.width=.0031; bev.segments=5;bev.affect='EDGES'
norm=stem.modifiers.new('Soft normals','WEIGHTED_NORMAL')
norm.keep_sharp=True; norm.weight=55

# Pivot is almost hidden behind the cap of the J, mechanically separate from the shade.
def cylinder(name,loc,r,depth,mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=depth,location=loc)
    o=bpy.context.object;o.name=name
    o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    return o
pivot=cylinder('Shadowed internal pivot cap',(-.096,-.031,.211),.018,.007,shellmat)
pivot.rotation_euler[0]=math.pi/2

# Studio tabletop and continuous black cyclorama.
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.002))
ground=bpy.context.object;ground.name='Near-black tabletop';ground.scale=(.0011,.0011,1)
ground.data.materials.append(floor_mat)

def aim(o,point):
    direction=Vector(point)-o.location
    o.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size,color,target):
    data=bpy.data.lights.new(name,'AREA')
    data.energy=power
    data.shape='DISK';data.size=size
    data.color=color
    o=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(o)
    o.location=loc;aim(o,target)
    return o
area('Huge left softbox | 250 W',(-.46,-.57,.66),240,.72,(1,.92,.87),(.0,0,.14))
area('Broad white overhead',( .36,.31,.77),310,.90,(.96,.94,1),(.01,0,.14))
area('Faint edge rim | camera right',(.47,-.11,.38),95,.44,(1,.9,.84),(.05,0,.16))
area('Warm 2200K bounce to tabletop',(.045,-.065,.105),9,.11,(1,.45,.19),(.07,-.05,0))
area('Rear halo warm spill',(-.185,.025,.246),7,.18,(1,.40,.15),(-.05,0,.165))

world=bpy.context.scene.world or bpy.data.worlds.new('black')
bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.006,.006,.006,1)
world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.22

data=bpy.data.cameras.new('65mm product lens')
cam=bpy.data.objects.new('65mm product lens',data)
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera=cam
data.type='PERSP';data.lens=72;data.sensor_width=36
cam.location=(.69,-1.12,.49)
aim(cam,(.012,0,.147))
data.dof.use_dof=False

scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=48
scene.cycles.use_denoising=True
scene.render.resolution_x=1536
scene.render.resolution_y=1024
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.render.filepath=str(OUT/'01_hero_blender.png')
bpy.ops.wm.save_as_mainfile(filepath=str(DIR/'Concept_B_RevB.blend'))
bpy.ops.render.render(write_still=True)
print('RENDERED',scene.render.filepath,flush=True)
cam.location=(.43,-.97,.34)
aim(cam,(.012,0,.145))
data.lens=85
scene.render.filepath=str(OUT/'02_lower_angle.png')
bpy.ops.render.render(write_still=True)
print('RENDERED',scene.render.filepath,flush=True)
