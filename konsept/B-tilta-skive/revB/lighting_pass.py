import bpy,math
from mathutils import Vector
from pathlib import Path

DIR=Path(__file__).resolve().parent
scene=bpy.context.scene
changes={'Huge left softbox | 250 W':20,'Broad white overhead':23,'Faint edge rim | camera right':7,
'Warm 2200K bounce to tabletop':2.6,'Rear halo warm spill':2.1}
for name,power in changes.items():
    bpy.data.objects[name].data.energy=power
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.13

top=bpy.data.materials['Graphite | soft mineral powdercoat'].node_tree.nodes.get('Principled BSDF')
top.inputs['Base Color'].default_value=(.17,.159,.150,1)
top.inputs['Roughness'].default_value=.76
bowl=bpy.data.materials['Graphite | deep satin metal'].node_tree.nodes.get('Principled BSDF')
bowl.inputs['Base Color'].default_value=(.085,.076,.068,1)
bowl.inputs['Roughness'].default_value=.61
foot=bpy.data.materials['Pedestal | warm charcoal'].node_tree.nodes.get('Principled BSDF')
foot.inputs['Base Color'].default_value=(.093,.087,.080,1)

tilt=math.radians(34)
cx,cy,cz=.034,0,.175
def hw(x,y,z):
    return (cx+(math.cos(tilt)*x+math.sin(tilt)*z)*.001,y*.001,
            cz+(-math.sin(tilt)*x+math.cos(tilt)*z)*.001)

# Conceal the radial mesh pole with a truly closed same-material disk.
bpy.ops.mesh.primitive_circle_add(vertices=128,radius=.020,fill_type='NGON',location=hw(0,0,16.34))
cover=bpy.context.object
cover.name='Continuous canopy | pole closure'
cover.rotation_euler.y=tilt
cover.data.materials.append(bpy.data.materials['Graphite | soft mineral powdercoat'])

# Second, shorter and warmer front optic set below the top, following the front-right bowl.
N=90
a1=134.5;b1=124.3
verts=[]
for row in (0,1):
    for i in range(N+1):
        t=i/N
        theta=math.radians(-112+94*t)
        w=10*max(.02,math.sin(math.pi*t)**.55)
        z=-26+(row-.5)*w
        a=a1+(z+25)*.55
        b=b1+(z+25)*.43
        verts.append(hw((a+1.8)*math.cos(theta),(b+1.8)*math.sin(theta),z))
faces=[(i,i+1,i+N+2,i+N+1) for i in range(N)]
mesh=bpy.data.meshes.new('Supplemental optical strip')
mesh.from_pydata(verts,[],faces);mesh.update()
ob=bpy.data.objects.new('Recessed crescent 135 mm | direct lens',mesh)
bpy.context.collection.objects.link(ob)
ob.data.materials.append(bpy.data.materials['2200 K | window'])
for p in mesh.polygons:p.use_smooth=True

cam=scene.camera
cam.location=(.58,-1.1,.35)
focus=Vector((.013,0,.145))
cam.rotation_euler=(focus-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=77
scene.render.resolution_x=1152
scene.render.resolution_y=768
scene.cycles.samples=20
scene.view_settings.exposure=0
scene.render.filepath=str(DIR/'renders'/'03_lighting_preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(DIR/'Concept_B_RevB.blend'))
bpy.ops.render.render(write_still=True)
print('RENDERED',scene.render.filepath,flush=True)
