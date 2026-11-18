import bpy,math
from mathutils import Vector
from pathlib import Path
DIR=Path(__file__).resolve().parent
scene=bpy.context.scene
for k in ['ONE amber aperture | front','Deep dark cutout | front','Recessed crescent 135 mm | direct lens']:
    o=bpy.data.objects.get(k)
    if o:bpy.data.objects.remove(o,do_unlink=True)

a=bpy.data.materials['2200 K | window']
a.node_tree.nodes.get('Emission').inputs['Strength'].default_value=6.0
for name,power in {'Huge left softbox | 250 W':9,'Broad white overhead':12,'Faint edge rim | camera right':4,'Warm 2200K bounce to tabletop':1.9,'Rear halo warm spill':1.1}.items():
    bpy.data.objects[name].data.energy=power
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.11
floor=bpy.data.materials['Stage | graphite'].node_tree.nodes.get('Principled BSDF')
floor.inputs['Base Color'].default_value=(.007,.006,.006,1)
bpy.data.objects['Near-black tabletop'].scale=(.011,.011,1)

tilt=math.radians(34)
cs,sn=math.cos(tilt),math.sin(tilt)
def hw(x,y,z):
    return ((34+cs*x+sn*z)*.001,y*.001,(175-sn*x+cs*z)*.001)
rings=[(-40,92,85),(-39,101,93),(-36,112,103),(-31,124,113),(-24,136,125),(-15,147,136),(-4,156,144)]
def axes(z):
    for (z0,a0,b0),(z1,a1,b1) in zip(rings,rings[1:]):
        if z0<=z<=z1:
            f=(z-z0)/(z1-z0)
            return (a0+(a1-a0)*f,b0+(b1-b0)*f)
    return 124,113
def slit(name,begin,end,zmid,height,off,material):
    count=128;verts=[];faces=[]
    for row in (0,1):
        for i in range(count+1):
            t=i/count
            theta=math.radians(begin+(end-begin)*t)
            thickness=height*(max(0,math.sin(math.pi*t))**.53)
            z=zmid+(row-.5)*max(.1,thickness)
            ax,by=axes(z)
            verts.append(hw((ax+off)*math.cos(theta),(by+off)*math.sin(theta),z))
    for i in range(count):faces.append((i,i+1,i+count+2,i+count+1))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    for p in mesh.polygons:p.use_smooth=True

slit('Front aperture | deep black recess',-105,-11,-31,15,1.35,bpy.data.materials['Interior | dark optical baffle'])
slit('Front aperture | warm opal, shorter',-101,-15,-31,9.5,1.95,a)

cam=scene.camera
cam.location=(.56,-1.1,.34)
cam.rotation_euler=(Vector((-.025,0,.14))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=76
scene.view_settings.exposure=-.60
scene.cycles.samples=24
scene.render.resolution_x=1152
scene.render.resolution_y=768
scene.render.filepath=str(DIR/'renders'/'04_refined_preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(DIR/'Concept_B_RevB.blend'))
bpy.ops.render.render(write_still=True)
print('RENDERED',scene.render.filepath,flush=True)
