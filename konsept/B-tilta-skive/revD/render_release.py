import bpy, math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
s=bpy.context.scene
nt=bpy.data.materials['Black tabletop'].node_tree
geom=nt.nodes.get('Geometry')
ramp=nt.nodes.get('Color Ramp')
mix=nt.nodes.get('Mix Shader')
sep=nt.nodes.new('ShaderNodeSeparateXYZ')
nt.links.new(geom.outputs['Position'],sep.inputs['Vector'])
ycut=nt.nodes.new('ShaderNodeMapRange')
ycut.inputs['From Min'].default_value=.05
ycut.inputs['From Max'].default_value=.12
ycut.inputs['To Min'].default_value=1
ycut.inputs['To Max'].default_value=0
ycut.clamp=True
nt.links.new(sep.outputs['Y'],ycut.inputs['Value'])
mult=nt.nodes.new('ShaderNodeMath')
mult.operation='MULTIPLY'
nt.links.new(ramp.outputs['Color'],mult.inputs[0])
nt.links.new(ycut.outputs['Result'],mult.inputs[1])
nt.links.new(mult.outputs[0],mix.inputs[0])

s.cycles.samples=64
s.cycles.use_denoising=True
s.render.resolution_x=1536
s.render.resolution_y=1024
s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
s.render.filepath=str(R/'renders'/'B_REFERENCE_MATCH_REV_D.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Concept_B_RevD.blend'))
bpy.ops.render.render(write_still=True)
print('HERO_READY',s.render.filepath,flush=True)
cam=s.camera
cam.location=(.55,-1.10,.35)
cam.rotation_euler=(Vector((.015,0,.144))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=78
s.cycles.samples=42
s.render.resolution_x=1280
s.render.resolution_y=853
s.render.filepath=str(R/'renders'/'B_ALTERNATE_3_4_REV_D.png')
bpy.ops.render.render(write_still=True)
print('ALTERNATE_READY',s.render.filepath,flush=True)
