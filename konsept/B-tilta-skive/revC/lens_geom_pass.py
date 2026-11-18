import bpy, math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from pathlib import Path

root=Path(__file__).resolve().parent
scene=bpy.context.scene
cam=scene.camera

# Rebuild the support to the reference's shorter thick rounded head and long soft inside arc.
old=bpy.data.objects.get('Monolithic J pedestal | continuous casting')
if old:bpy.data.objects.remove(old,do_unlink=True)
outer=[(-125,6),(-125,146)]
for i in range(1,41):
    a=math.pi-math.pi*i/40
    outer.append((-101+24*math.cos(a),146+24*math.sin(a)))
outer.append((-77,75))
for i in range(1,31):
    a=math.pi+(math.pi/2)*i/30
    outer.append((-41+36*math.cos(a),75+36*math.sin(a)))
outer.append((54,39))
def cubic(a,b,c,d,n):
    return [((1-t)**3*a[0]+3*(1-t)**2*t*b[0]+3*(1-t)*t*t*c[0]+t**3*d[0],
             (1-t)**3*a[1]+3*(1-t)**2*t*b[1]+3*(1-t)*t*t*c[1]+t**3*d[1]) for t in (i/n for i in range(1,n+1))]
outer+=cubic((54,39),(69,39),(72,34),(72,25),10)
outer.append((72,17))
outer+=cubic((72,17),(72,11),(67,6),(60,6),10)
m=len(outer)
v=[(x*.001,y*.001,z*.001) for y in (-37,37) for x,z in outer]
f=[tuple(range(m-1,-1,-1)),tuple(range(m,2*m))]
for k in range(m): f.append((k,(k+1)%m,(k+1)%m+m,k+m))
mesh=bpy.data.meshes.new('J_continuous')
mesh.from_pydata(v,[],f);mesh.update()
o=bpy.data.objects.new('J pedestal | shorter seamless casting',mesh)
bpy.context.collection.objects.link(o)
o.data.materials.append(bpy.data.materials['One-piece J | graphite'])
bev=o.modifiers.new('Soften outside corners','BEVEL')
bev.width=.0035
bev.segments=6
o.modifiers.new('Consistent face normals','WEIGHTED_NORMAL')

# Small internal head connection behind the shade, not a decorative ball.
bpy.ops.mesh.primitive_cube_add(size=1,location=(-.104,.014,.161))
br=bpy.context.object
br.name='Hidden structural hinge bridge | visual envelope'
br.dimensions=(.018,.024,.053)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
br.data.materials.append(bpy.data.materials['Deep bowl | dark charcoal metal'])
br.modifiers.new('Rounded bridge','BEVEL').width=.003

# Adjusted graphite, less metallic & more realistic.
for name,color in [
('Matte warm graphite | anodized aluminum',(.047,.044,.041)),
('Deep bowl | dark charcoal metal',(.031,.027,.025)),
('One-piece J | graphite',(.049,.043,.040))]:
    b=bpy.data.materials[name].node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value=(*color,1)
    b.inputs['Metallic'].default_value=.18
b=bpy.data.materials['Black tabletop'].node_tree.nodes.get('Principled BSDF')
b.inputs['Base Color'].default_value=(.0011,.00095,.00085,1)
b.inputs['Roughness'].default_value=.97
for name,power in [('Key softbox left',22),('Overhead broad graybox',19),('Small camera right fill',6),('Local rear halo bounce',5),('Physically motivated warm spot on desk',3)]:
    bpy.data.objects[name].data.energy=power
scene.view_settings.exposure=-.83

# The long horizontal front slot is a planar inset on the front-facing lower bowl,
# replacing the incorrect glowing perimeter seam.
right=(cam.rotation_euler.to_matrix()@Vector((1,0,0))).normalized()
up=(cam.rotation_euler.to_matrix()@Vector((0,1,0))).normalized()
toward=(cam.rotation_euler.to_matrix()@Vector((0,0,1))).normalized()
center=Vector((.110,-.075,.098))
def ellipse(name,halfwidth,halfheight,off,mat):
    vv=[];ff=[];n=128
    vv.append(center+toward*off)
    for i in range(n):
        t=2*math.pi*i/n
        vv.append(center+toward*off+right*(halfwidth*math.cos(t))+up*(halfheight*math.sin(t)))
    ff=[(0,1+i,1+(i+1)%n) for i in range(n)]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vv,[],ff);mesh.update()
    o=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    for f in o.data.polygons:f.use_smooth=True
    return o
black=bpy.data.materials.get('Light trap | almost black') or bpy.data.materials.new('Light trap | almost black')
black.diffuse_color=(.008,.007,.006,1)
optic=bpy.data.materials.get('Real inset diffused warm-white optic') or bpy.data.materials.new('Real inset diffused warm-white optic')
optic.use_nodes=True
nt=optic.node_tree
nt.nodes.clear()
e=nt.nodes.new('ShaderNodeEmission')
e.inputs['Color'].default_value=(1,.65,.39,1)
e.inputs['Strength'].default_value=7
output=nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(e.outputs[0],output.inputs['Surface'])
ellipse('Inset cavity | shadow black rim',.091,.013,.008,black)
ellipse('Independent 2700K work lens | warm lozenge',.086,.009,.010,optic)

# Tone the small original rear arc up with physically glowing gold and hidden light.
mat=bpy.data.materials['Rear halo optical insert']
mat.node_tree.nodes.get('Emission').inputs['Strength'].default_value=7
bpy.data.objects['Local rear halo bounce'].data.energy=8

bpy.context.view_layer.update()
v=world_to_camera_view(scene,cam,center)
print('LENS_CENTER_SCREEN',int(v.x*1536),int((1-v.y)*1024),flush=True)

scene.cycles.samples=16
scene.render.resolution_x=1024
scene.render.resolution_y=682
scene.render.filepath=str(root/'renders'/'01_new_J_lens_test.png')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'B_RevC_lens.blend'))
bpy.ops.render.render(write_still=True)
print('RENDERED',scene.render.filepath,flush=True)
