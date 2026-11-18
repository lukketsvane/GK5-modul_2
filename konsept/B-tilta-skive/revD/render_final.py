import bpy, math
from pathlib import Path
from mathutils import Vector

R=Path(__file__).resolve().parent
s=bpy.context.scene
floor=bpy.data.materials['Black tabletop'].node_tree
sub=next(n for n in floor.nodes if n.type=='VECT_MATH' and n.operation=='SUBTRACT')
scale=next(n for n in floor.nodes if n.type=='VECT_MATH' and n.operation=='MULTIPLY')
rotate=floor.nodes.new('ShaderNodeVectorRotate')
rotate.rotation_type='AXIS_ANGLE'
rotate.inputs['Axis'].default_value=(0,0,1)
rotate.inputs['Angle'].default_value=-math.pi/4
floor.links.new(sub.outputs['Vector'],rotate.inputs['Vector'])
floor.links.new(rotate.outputs['Vector'],scale.inputs[0])
scale.inputs[1].default_value=(1/.14,1/.06,0)
em=floor.nodes.get('Emission')
em.inputs['Color'].default_value=(1,.43,.20,1)
em.inputs['Strength'].default_value=1.53

halo=bpy.data.materials['Warm reflected light, not a flat orange surface'].node_tree.nodes.get('Emission')
halo.inputs['Color'].default_value=(1,.46,.18,1)
halo.inputs['Strength'].default_value=11.5

s.cycles.samples=64
s.cycles.use_denoising=True
s.render.resolution_x=1536
s.render.resolution_y=1024
s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
s.render.filepath=str(R/'renders'/'B_REFERENCE_MATCH_REV_D.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Concept_B_RevD.blend'))
bpy.ops.render.render(write_still=True)
print('HERO_RENDERED',s.render.filepath,flush=True)

cam=s.camera
cam.location=(.55,-1.10,.35)
cam.rotation_euler=(Vector((.015,0,.144))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=78
s.cycles.samples=44
s.render.resolution_x=1280
s.render.resolution_y=853
s.render.filepath=str(R/'renders'/'B_ALTERNATE_3_4_REV_D.png')
bpy.ops.render.render(write_still=True)
print('SECOND_RENDERED',s.render.filepath,flush=True)
