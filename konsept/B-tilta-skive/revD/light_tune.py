import bpy
from pathlib import Path
from mathutils import Vector

R=Path(__file__).resolve().parent
s=bpy.context.scene
top=bpy.data.materials['Matte warm graphite | anodized aluminum'].node_tree.nodes.get('Principled BSDF')
top.inputs['Base Color'].default_value=(.040,.039,.039,1)

m=bpy.data.materials['Warm reflected light, not a flat orange surface']
e=m.node_tree.nodes.get('Emission')
e.inputs['Color'].default_value=(1,.62,.35,1)
e.inputs['Strength'].default_value=8

lens=bpy.data.materials['Warm opal diffuser with centre glow']
ramp=lens.node_tree.nodes.get('Color Ramp')
ramp.color_ramp.elements[0].color=(1,.78,.56,1)
ramp.color_ramp.elements[1].color=(.88,.59,.41,1)

f=bpy.data.materials['Black tabletop']
nt=f.node_tree
nt.nodes.clear()
tex=nt.nodes.new('ShaderNodeNewGeometry')
sub=nt.nodes.new('ShaderNodeVectorMath')
sub.operation='SUBTRACT'
sub.inputs[1].default_value=(.080,-.009,0)
nt.links.new(tex.outputs['Position'],sub.inputs[0])
scale=nt.nodes.new('ShaderNodeVectorMath')
scale.operation='MULTIPLY'
scale.inputs[1].default_value=(1/.11,1/.073,0)
nt.links.new(sub.outputs['Vector'],scale.inputs[0])
length=nt.nodes.new('ShaderNodeVectorMath')
length.operation='LENGTH'
nt.links.new(scale.outputs['Vector'],length.inputs[0])
maprange=nt.nodes.new('ShaderNodeMapRange')
maprange.inputs['From Min'].default_value=0
maprange.inputs['From Max'].default_value=2.3
maprange.inputs['To Min'].default_value=0
maprange.inputs['To Max'].default_value=1
nt.links.new(length.outputs['Value'],maprange.inputs['Value'])
r=nt.nodes.new('ShaderNodeValToRGB')
r.color_ramp.interpolation='EASE'
r.color_ramp.elements[0].position=0.0
r.color_ramp.elements[0].color=(1,1,1,1)
r.color_ramp.elements[1].position=1.0
r.color_ramp.elements[1].color=(0,0,0,1)
r.color_ramp.elements.new(.39).color=(.50,.50,.50,1)
r.color_ramp.elements.new(.70).color=(.09,.09,.09,1)
nt.links.new(maprange.outputs['Result'],r.inputs['Fac'])
base=nt.nodes.new('ShaderNodeBsdfPrincipled')
base.inputs['Base Color'].default_value=(.000006,.000005,.000005,1)
base.inputs['Metallic'].default_value=0
base.inputs['Roughness'].default_value=.99
try:base.inputs['IOR Level'].default_value=0.0
except KeyError:pass
em=nt.nodes.new('ShaderNodeEmission')
em.inputs['Color'].default_value=(1,.54,.295,1)
em.inputs['Strength'].default_value=1.7
mix=nt.nodes.new('ShaderNodeMixShader')
nt.links.new(r.outputs['Color'],mix.inputs[0])
nt.links.new(base.outputs[0],mix.inputs[1])
nt.links.new(em.outputs[0],mix.inputs[2])
out=nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(mix.outputs[0],out.inputs['Surface'])
s.cycles.samples=22
s.render.resolution_x=1024
s.render.resolution_y=682
s.render.filepath=str(R/'renders'/'02_glow_preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Concept_B_RevD.blend'))
bpy.ops.render.render(write_still=True)
print('RENDERED',s.render.filepath,flush=True)
