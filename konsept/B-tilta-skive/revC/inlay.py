import bpy,math
from mathutils import Vector
from pathlib import Path

root=Path(__file__).resolve().parent
scene=bpy.context.scene
cam=scene.camera
W=1536
H=1024
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()

def ray(x,y):
    u=x/W;v=1-y/H
    direction=(cam.rotation_euler.to_matrix()@Vector(((u-.5)*cam.data.sensor_width/cam.data.lens,(v-.5)*cam.data.sensor_width/cam.data.lens*(H/W),-1))).normalized()
    hit,p,n,idx,o,mat=scene.ray_cast(deps,cam.location,direction)
    return hit,p,n,o

def optical_surface(name,cx,cy,rx,ry,offset,mat):
    n=160;radials=(0,.18,.35,.52,.70,.86,.95,1)
    vv=[];faces=[];fails=[]
    for r in radials:
        for i in range(n):
            t=2*math.pi*i/n
            x=cx+rx*r*math.cos(t)
            y=cy+ry*r*math.sin(t)
            hit,p,no,o=ray(x,y)
            if not hit or 'Deep smooth underbody' not in o.name:
                fails.append((round(x),round(y),o.name if hit else 'MISS'))
                # ray along a slightly lower row, all emitters remain attached to dark bowl.
                for delta in (5,10,15,22):
                    hit,p,no,o=ray(x,y+delta)
                    if hit and 'Deep smooth underbody' in o.name:
                        break
                if not hit or 'Deep smooth underbody' not in o.name:
                    # show result is invalid rather than inventing an unsupported lens placement.
                    raise RuntimeError('Cannot fit port on bowl: '+str((x,y)))
            vv.append(p+no*offset)
    for r in range(len(radials)-1):
        for i in range(n):
            a=r*n+i;b=r*n+(i+1)%n
            faces.append((a,b,b+n,a+n))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vv,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    for p in mesh.polygons:p.use_smooth=True
    print('OPTIC',name,'POINTS_OUTSIDE',len(fails),'FIRST',fails[:12],flush=True)
    return o

black=bpy.data.materials.get('Light trap | almost black') or bpy.data.materials.new('Light trap | almost black')
black.use_nodes=True
black.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.004,.003,.003,1)
optic=bpy.data.materials.get('Real inset diffused warm-white optic') or bpy.data.materials.new('Real inset diffused warm-white optic')
optic.use_nodes=True
nt=optic.node_tree
nt.nodes.clear()
e=nt.nodes.new('ShaderNodeEmission')
e.inputs['Color'].default_value=(1,.70,.48,1)
e.inputs['Strength'].default_value=6
output=nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(e.outputs[0],output.inputs['Surface'])

# Reference light aperture 704..1070 px by 631..668 px. Keep inset inside actual front-bowl surface.
optical_surface('Dark optical recess | attached to bowl',900,649,156,10,0.00045,black)
optical_surface('Inlaid almond-shaped luminous aperture',900,649,151,7.5,0.00065,optic)

# Left-hand indirect golden halo between top flange and backing shell.
# Lift the diffuser wedge out from behind the opaque body only on the rear-left arc.
def arc(name,a0,a1,rad,z0,z1,mat,n=120):
    v=[];f=[]
    t0=math.radians(33);co,si=math.cos(t0),math.sin(t0)
    for row,z in enumerate((z0,z1)):
        for i in range(n+1):
            t=i/n;phi=math.radians(a0+(a1-a0)*t)
            delta=6+7*math.sin(math.pi*t)
            x=(rad+delta)*math.cos(phi)
            y=(rad*.93+delta)*math.sin(phi)
            # head is raised +24mm from revA dimensions.
            v.append(Vector((.026+(co*x+si*z)*.001, y*.001,.206+(-si*x+co*z)*.001)))
    for i in range(n):f.append((i,i+1,i+n+2,i+n+1))
    m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.update()
    o=bpy.data.objects.new(name,m)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    for p in m.polygons:p.use_smooth=True

halo=bpy.data.materials['Rear halo optical insert']
halo.node_tree.nodes.get('Emission').inputs['Strength'].default_value=4.8
arc('New offset rear-left amber diffuser',145,242,166,-7,-26,halo)

scene.cycles.samples=18
scene.render.resolution_x=1024
scene.render.resolution_y=682
scene.render.filepath=str(root/'renders'/'04_inset_lens_render.png')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'B_RevC_port.blend'))
bpy.ops.render.render(write_still=True)
print('RENDERED',scene.render.filepath,flush=True)
