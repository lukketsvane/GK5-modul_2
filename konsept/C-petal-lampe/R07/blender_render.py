import bpy,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent
out=root/'renders'
out.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=45
scene.cycles.use_denoising=True
scene.render.resolution_x=1169
scene.render.resolution_y=1279
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'

scene.view_settings.exposure=0
scene.camera=None

def mat(name,color,rough=0.86,emission=0,grain=False):
 m=bpy.data.materials.new(name)
 m.use_nodes=True
 node=m.node_tree.nodes.get('Principled BSDF')
 node.inputs['Base Color'].default_value=(*color,1)
 node.inputs['Roughness'].default_value=rough
 node.inputs['Metallic'].default_value=0
 node.inputs['Emission Color'].default_value=(*color,1)
 node.inputs['Emission Strength'].default_value=emission
 if grain:
  noise=m.node_tree.nodes.new('ShaderNodeTexNoise')
  noise.inputs['Scale'].default_value=700
  noise.inputs['Detail'].default_value=2
  bump=m.node_tree.nodes.new('ShaderNodeBump')
  bump.inputs['Strength'].default_value=.10
  bump.inputs['Distance'].default_value=.00012
  m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
  m.node_tree.links.new(bump.outputs['Normal'],node.inputs['Normal'])
 return m
stone=mat('Warm stone matte PETG',(.195,.155,.12),grain=True)
opal=mat('Opal internal light',(.99,.72,.44),rough=.80,emission=3.2)
floor_mat=mat('Warm diffuse studio',(.75,.65,.59),rough=1.0)
cable_mat=mat('Warm grey cable',(.22,.195,.175),rough=.94)

def load(part, material):
 bpy.ops.wm.stl_import(filepath=str(root/'stl'/(part+'.stl')),global_scale=.001)
 ob=bpy.context.object
 ob.name=part
 ob.data.materials.clear()
 ob.data.materials.append(material)
 for face in ob.data.polygons:face.use_smooth=True
 return ob
for name in ('RIB_FRONT_L','RIB_FRONT_R','RIB_SHOULDER_L','RIB_SHOULDER_R','RIB_OUTER_L','RIB_OUTER_R','RIB_REAR_L','RIB_REAR_R'):
 load(name,stone)
load('BASE',stone)
load('DIFFUSER',opal)
bpy.ops.mesh.primitive_plane_add(size=5,location=(0,0,-.002))
bpy.context.object.name='Matte studio ground'
bpy.context.object.data.materials.append(floor_mat)

curve=bpy.data.curves.new('Power cable nominal','CURVE')
curve.dimensions='3D'
curve.bevel_depth=.0013
curve.resolution_u=16
curve.bevel_resolution=4
sp=curve.splines.new('BEZIER')
sp.bezier_points.add(3)
coords=[(-.023,-.018,.003),(-.065,-.01,.003),(-.110,-.014,.003),(-.220,-.020,.003)]
for pt,xyz in zip(sp.bezier_points,coords):
 pt.co=xyz
 pt.handle_left_type='AUTO'
 pt.handle_right_type='AUTO'
cobj=bpy.data.objects.new('Power cable visual aid',curve)
scene.collection.objects.link(cobj)
cobj.data.materials.append(cable_mat)

def area(name,coords,power,size,col):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=col
 ob=bpy.data.objects.new(name,d);scene.collection.objects.link(ob);ob.location=coords
 ob.rotation_euler=(Vector((0,0,.10))-ob.location).to_track_quat('-Z','Y').to_euler()
area('Broad front left',(-.34,-.44,.48),8.0,.55,(1,.95,.90))
area('Broad right',(.35,-.06,.40),2.0,.50,(.95,.96,1))
area('Soft top',(.15,.25,.55),4.0,.56,(1,.99,.96))
for z in (.08,.16):
 d=bpy.data.lights.new('Internal warm fill','POINT')
 d.energy=1.6
 d.color=(1,.78,.53)
 d.shadow_soft_size=.035
 ob=bpy.data.objects.new('Internal warm fill',d);scene.collection.objects.link(ob);ob.location=(0,0,z)
w=bpy.data.worlds.new('Warm white studio')
w.use_nodes=True
w.node_tree.nodes.get('Background').inputs['Color'].default_value=(.70,.63,.57,1)
w.node_tree.nodes.get('Background').inputs['Strength'].default_value=.28
cam_bg=w.node_tree.nodes.new('ShaderNodeBackground')
cam_bg.inputs['Color'].default_value=(.83,.70,.63,1)
cam_bg.inputs['Strength'].default_value=1.1
light_path=w.node_tree.nodes.new('ShaderNodeLightPath')
mix=w.node_tree.nodes.new('ShaderNodeMixShader')
output=w.node_tree.nodes.get('World Output')
w.node_tree.links.new(light_path.outputs['Is Camera Ray'],mix.inputs[0])
w.node_tree.links.new(w.node_tree.nodes.get('Background').outputs[0],mix.inputs[1])
w.node_tree.links.new(cam_bg.outputs[0],mix.inputs[2])
w.node_tree.links.new(mix.outputs[0],output.inputs['Surface'])
scene.world=w

camdata=bpy.data.cameras.new('Orthographic matching')
cam=bpy.data.objects.new('Camera',camdata);scene.collection.objects.link(cam)
camdata.type='ORTHO'
camdata.ortho_scale=.282
scene.camera=cam
def shoot(name,coords,target):
 cam.location=coords
 cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(out/(name+'.png'))
 bpy.ops.render.render(write_still=True)
 print('RENDERED '+name,flush=True)
shoot('01_actual_CAD_reference_camera',(.002,-1.0,.14),(.002,0,.1124))
shoot('02_actual_CAD_threequarter',(.42,-.92,.30),(0,0,.11))
bpy.ops.wm.save_as_mainfile(filepath=str(out/'R07_CAD_SCENE.blend'))
