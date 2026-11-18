import bpy
from pathlib import Path

R=Path(__file__).resolve().parent
s=bpy.context.scene
top=bpy.data.materials['Matte warm graphite | anodized aluminum'].node_tree.nodes.get('Principled BSDF')
top.inputs['Base Color'].default_value=(.0375,.0368,.037,1)
rear=bpy.data.materials['Warm reflected light, not a flat orange surface'].node_tree.nodes.get('Emission')
rear.inputs['Color'].default_value=(1,.55,.26,1)
rear.inputs['Strength'].default_value=10
lens=bpy.data.materials['Warm opal diffuser with centre glow'].node_tree.nodes.get('Color Ramp')
lens.color_ramp.elements[0].color=(1,.69,.48,1)
lens.color_ramp.elements[1].color=(.88,.56,.37,1)

floor=bpy.data.materials['Black tabletop'].node_tree
for n in floor.nodes:
    if n.type=='VECT_MATH' and n.operation=='MULTIPLY':
        n.inputs[1].default_value=(10,17.24,0)
r=floor.nodes.get('Color Ramp')
for el in r.color_ramp.elements:
    if abs(el.position-.39)<.04:
        el.color=(.54,.54,.54,1)
    if abs(el.position-.70)<.04:
        el.color=(.035,.035,.035,1)
em=floor.nodes.get('Emission')
em.inputs['Color'].default_value=(1,.35,.13,1)
em.inputs['Strength'].default_value=1.8
s.cycles.samples=24
s.render.resolution_x=1024
s.render.resolution_y=682
s.render.filepath=str(R/'renders'/'03_color_preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Concept_B_RevD.blend'))
bpy.ops.render.render(write_still=True)
print('RENDERED',s.render.filepath,flush=True)
