import bpy
import math
import os
from mathutils import Vector

ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(ROOT,"blender_revB")
os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials):
    bpy.data.materials.remove(m)

def material(name,color,metal=0,rough=.4,emission=None,strength=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Metallic"].default_value=metal
    bs.inputs["Roughness"].default_value=rough
    if emission:
        bs.inputs["Emission Color"].default_value=(*emission,1)
        bs.inputs["Emission Strength"].default_value=strength
    return m
metal=material("01 | powder-coated warm graphite aluminum",(.20,.184,.174),.34,.65)
top_mat=material("02 | fine satin matte graphite canopy",(.245,.236,.228),.11,.82)
inner=material("03 | dark recessed graphite bowl",(.105,.095,.09),.42,.42)
glass=material("05 | warm 2200K opal diffusing PC",(.84,.56,.31),.02,.58,(1.0,.48,.16),4.5)
halo_mat=material("06 | concealed amber halo diffuser",(.73,.42,.17),.08,.5,(1,.34,.06),3.0)
black=material("08 | internal shadow gasket",(.024,.024,.023),.15,.68)
floor_mat=material("09 | dark satin charcoal stage",(.009,.009,.009),.08,.55)

def obj_from_mesh(name,verts,faces,mat):
    mesh=bpy.data.meshes.new(name+"_mesh")
    mesh.from_pydata([(x*.001,y*.001,z*.001) for x,y,z in verts],[],faces)
    mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    for p in ob.data.polygons:p.use_smooth=True
    return ob

def base_j():
    points=[(-100,0),(70,0)]
    for j in range(1,9):
        th=-math.pi/2 + j/8*(math.pi/2)
        points.append((70+7*math.cos(th),7+7*math.sin(th)))
    points.append((77,26))
    for j in range(1,9):
        th=j/8*math.pi/2
        points.append((68+9*math.cos(th),26+9*math.sin(th)))
    points.append((-10,35))
    for j in range(1,18):
        t=j/17
        u=1-t
        x=u*u*u*(-10)+3*u*u*t*(-34)+3*u*t*t*(-53)+t*t*t*(-54)
        z=u*u*u*35+3*u*u*t*35+3*u*t*t*48+t*t*t*73
        points.append((x,z))
    points.append((-54,197))
    for j in range(1,33):
        th=j/32*math.pi
        points.append((-77+23*math.cos(th),197+23*math.sin(th)))
    points.extend([(-100,1)])
    n=len(points);verts=[]
    for y in (-33,33):
        verts += [(x,y,z) for x,z in points]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    ob=obj_from_mesh("10 | continuous J pedestal and low foot",verts,faces,metal)
    mod=ob.modifiers.new("small cast edge radii","BEVEL")
    mod.width=.0023;mod.segments=4
    mod.affect="EDGES"
    ob.modifiers.new("weighted normals","WEIGHTED_NORMAL")
    return ob
stand=base_j()

def rings_mesh(name,rings,mat,n=192):
    verts=[]
    for sx,sy,z in rings:
        for i in range(n):
            t=2*math.pi*i/n
            verts.append((sx*math.cos(t),sy*math.sin(t),z))
    faces=[]
    for ri in range(len(rings)-1):
        for i in range(n):
            i1=(i+1)%n
            faces.append((ri*n+i,ri*n+i1,(ri+1)*n+i1,(ri+1)*n+i))
    faces.append(tuple(reversed(range(n))))
    faces.append(tuple((len(rings)-1)*n+i for i in range(n)))
    ob=obj_from_mesh(name,verts,faces,mat)
    return ob

def orient_head(ob):
    ob.rotation_euler[1]=math.radians(33)
    ob.location=(.026,0,.188)
    return ob

canopy=[(1.5,1.5,15.3)]
for i in range(1,17):
    t=i/16
    canopy.append((160*t,154*t,15.3+2.3*(1-t*t)))
canopy += [(161.0,155.0,14.2),(161.9,155.7,12.7),
           (162.0,155.8,11.4),(160.6,154.4,9.8),
           (156,150.2,8.2)]
top=orient_head(rings_mesh("20 | single sculpted shield with fine rolled lip",canopy,top_mat))
be=top.modifiers.new("subtle stamped edge radius","BEVEL");be.width=.0007;be.segments=2

dish=[(156,150,8.4),(159.4,153.2,5.8),(159,152.9,1),
      (155.6,149.4,-5),(149.5,143.0,-12),
      (138,132,-19),(125,120,-24),(109,105,-28),
      (87,84,-29.0),(65,63,-27),(35,33,-23),(1.5,1.5,-21)]
bowl=orient_head(rings_mesh("21 | continuously tapered deep underbowl",dish,inner))

def annular_strip(name,r_out,r_in,z_start,z_end,startdeg,enddeg,mat):
    n=100;verts=[]
    for z,r,ang in [(z_start,r_in,0),(z_start,r_out,0),(z_end,r_out,0),(z_end,r_in,0)]:
        for i in range(n+1):
            t=math.radians(startdeg+(enddeg-startdeg)*i/n)
            verts.append((r*math.cos(t),r*.960*math.sin(t),z))
    faces=[]
    for j in range(3):
        for i in range(n):
            faces.append((j*(n+1)+i,j*(n+1)+i+1,(j+1)*(n+1)+i+1,(j+1)*(n+1)+i))
    ob=obj_from_mesh(name,verts,faces,mat)
    return orient_head(ob)

rear=annular_strip("22 | narrow concealed left-rear halo",159.0,156.3,-5.8,6.0,109,230,halo_mat)
rim=annular_strip("23 | dark opal light aperture cover line",161.5,159.1,-3.2,1.2,234,341,black)

def side_eye(name,length,width,center_x,center_z,outward,mat):
    a=length*.5-width*.5
    r=width*.5
    coords=[]
    for j in range(25):
        th=-math.pi/2+math.pi*j/24
        coords.append((a+r*math.cos(th),r*math.sin(th)))
    for j in range(25):
        th=math.pi/2+math.pi*j/24
        coords.append((-a+r*math.cos(th),r*math.sin(th)))
    verts=[]
    for u,v in coords:
        x=center_x+u
        z=center_z+v
        front=-134*math.sqrt(max(.08,1-(x/144)**2))
        verts.append((x,front-outward,z))
    verts.append((center_x,-134*math.sqrt(max(.08,1-(center_x/144)**2))-outward,center_z))
    idx=len(verts)-1
    ob=obj_from_mesh(name,verts,[(j,(j+1)%len(coords),idx) for j in range(len(coords))],mat)
    return orient_head(ob)

side_eye("26 | recessed black optic surround",126,14,74,-18.5,3.1,black)
side_eye("27 | forward-facing warm opal aperture",118,8.5,74,-18.5,4.3,glass)

def floor_plane():
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.002))
    p=bpy.context.object
    p.name="90 | dark tabletop receiving real warm light"
    p.scale=(.1,.1,1)
    p.data.materials.append(floor_mat)
    return p
floor_plane()

def area(name,loc,watts,color,size,target,size_y=None):
    l=bpy.data.lights.new(name,"AREA")
    l.energy=watts;l.color=color;l.shape='DISK';l.size=size
    ob=bpy.data.objects.new(name,l);bpy.context.collection.objects.link(ob)
    ob.location=loc
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    return ob

area("91 | giant upper-left softbox",(-.64,-.42,.90),4.0,(.90,.91,1),1.3,(-.02,0,.12))
area("92 | broad pale edge reflection",(.34,.25,.52),1.5,(.88,.91,1),.60,(0,0,.15))
area("93 | low warm underside bounce",(.14,-.35,.18),.85,(1.0,.69,.36),.35,(0,0,.03))
area("94 | narrow amber local fill",(-.11,.06,.20),.35,(1.0,.53,.22),.23,(0,0,.12))
area("95 | warm tabletop pool",(.05,-.08,.095),.8,(1.0,.54,.24),.18,(.03,-.05,0))

world=bpy.context.scene.world
if world is None:world=bpy.data.worlds.new("black studio");bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.004,.0035,.003,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35

def aim(ob,target):
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()

bpy.ops.object.camera_add()
camera=bpy.context.object
camera.name="100 | restrained 70mm studio camera"
camera.location=(.50,-1.00,.345)
aim(camera,(-.006,0,.162))
camera.data.type='PERSP'
camera.data.lens=74
camera.data.sensor_width=36
bpy.context.scene.camera=camera

scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=36
scene.cycles.use_denoising=True
scene.render.resolution_x=1536
scene.render.resolution_y=1024
scene.render.resolution_percentage=82
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=0.15
scene.render.filepath=os.path.join(OUT,"01_B_revB_hero.png")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,"B_tilta_skive_revB.blend"))
bpy.ops.render.render(write_still=True)

camera.location=(.15,-1.10,.29)
aim(camera,(-.008,0,.16))
scene.render.filepath=os.path.join(OUT,"02_B_revB_front.png")
bpy.ops.render.render(write_still=True)
print("DONE Blender form RevB",OUT)
