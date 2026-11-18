import bpy, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent
out=root/'renders'
out.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=32
sc.cycles.use_denoising=True
sc.render.resolution_x=1450
sc.render.resolution_y=1600
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
sc.view_settings.view_transform='AgX'
def material(name,color,rough=.83,metal=0,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*color,1)
 p.inputs['Roughness'].default_value=rough
 p.inputs['Metallic'].default_value=metal
 p.inputs['Emission Color'].default_value=(*color,1)
 p.inputs['Emission Strength'].default_value=emission
 return m
stone=material('Ceramic / PETG prototype',(.59,.53,.45))
opal=material('Opal PC light diffuser',(.96,.77,.53),.73,emission=1.1)
metal=material('Steel and aluminum',(.35,.37,.39),.38,.7)
led=material('LED surface placeholders',(.99,.75,.51),.45,emission=10)
bgmat=material('Warm studio surface',(.80,.77,.71))
dark=material('Black studio surface',(.014,.014,.015))
parts={}
def imp(prefix,mat,key=None):
 f=next((root/'stl').glob(prefix+'*.stl'))
 bpy.ops.wm.stl_import(filepath=str(f),global_scale=.001)
 ob=bpy.context.object
 ob.name=key or prefix
 ob.data.materials.clear()
 ob.data.materials.append(mat)
 for poly in ob.data.polygons:poly.use_smooth=True
 parts.setdefault(prefix,[]).append(ob)
 return ob
for prefix,mat in [('C02_BASE',stone),('C03_BOTTOM',stone),('C04_BALLAST',metal),('C05_DIFFUSER',opal),('C06_CAP',opal),('C08_LED_CORE',metal)]:
 imp(prefix,mat)
for k in range(8):
 ob=imp('C01_RIB',stone,'Curved petal %02d'%(k+1))
 ob.rotation_euler.z=math.radians(22.5+45*k)
for k in range(4):
 ob=imp('C09_LED',led,'LED face %02d'%(k+1))
 ob.rotation_euler.z=math.radians(k*90)
def light(name,pos,power,size,color=(1,1,1)):
 data=bpy.data.lights.new(name,'AREA')
 data.energy=power;data.shape='DISK';data.size=size;data.color=color
 obj=bpy.data.objects.new(name,data);sc.collection.objects.link(obj)
 obj.location=pos
 obj.rotation_euler=(Vector((0,0,.11))-obj.location).to_track_quat('-Z','Y').to_euler()
light('Key left',(-.3,-.25,.38),75,.32,(1,.94,.86))
light('Fill right',(.27,.12,.42),65,.4,(.90,.94,1))
light('Top diffuse',(.05,.1,.52),70,.54,(1,.99,.94))
world=bpy.data.worlds.new('Studio')
sc.world=world;world.use_nodes=True
back=world.node_tree.nodes.get('Background')
back.inputs['Color'].default_value=(.70,.68,.64,1)
back.inputs['Strength'].default_value=.44
bpy.ops.mesh.primitive_plane_add(size=5,location=(0,0,-.001))
floor=bpy.context.object
floor.data.materials.append(bgmat)
camera_data=bpy.data.cameras.new('Lens')
camera=bpy.data.objects.new('Camera',camera_data)
sc.collection.objects.link(camera);sc.camera=camera
camera_data.type='ORTHO'
def shoot(name,position,target=(0,0,.112),scale=.265,night=False,power=1.1):
 camera.location=position
 camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
 camera_data.ortho_scale=scale
 floor.data.materials.clear()
 floor.data.materials.append(dark if night else bgmat)
 back.inputs['Strength'].default_value=.12 if night else .44
 opal.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=power
 sc.render.filepath=str(out/(name+'.png'))
 bpy.ops.render.render(write_still=True)
 print('RENDER_DONE',name,flush=True)
shoot('01_front_actual_CAD',(0,-.49,.22))
shoot('02_threequarter_actual_CAD',(.26,-.40,.255))
shoot('03_side_actual_CAD',(.43,-.12,.22))
shoot('04_back_actual_CAD',(0,.47,.235))
shoot('05_top_actual_CAD',(.07,-.12,.5),(0,0,.166),.24)
shoot('06_ambient_mode_black',(0,-.49,.23),night=True,power=.35)
shoot('07_bright_mode_black',(.25,-.42,.255),night=True,power=1.8)
shoot('08_top_joint_detail',(.06,-.11,.32),(0,0,.207),.105)
shoot('09_base_joint_detail',(.06,-.14,.095),(0,0,.027),.10)
for i,o in enumerate(parts['C01_RIB']):
 a=math.radians(22.5+i*45)
 o.location.x+=.035*math.cos(a)
 o.location.y+=.035*math.sin(a)
 o.location.z+=.01
for o in parts['C03_BOTTOM']+parts['C04_BALLAST']:
 o.location.z-=.025
for o in parts['C06_CAP']:
 o.location.z+=.017
shoot('10_exploded_actual_CAD',(.26,-.43,.29),(0,0,.115),.325)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'CONCEPT_C_REAL_CAD_SCENE.blend'))
print('COMPLETE_RENDER_BATCH',len(list(out.glob('*.png'))),flush=True)
