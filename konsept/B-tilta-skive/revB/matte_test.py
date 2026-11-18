import bpy
from pathlib import Path
p=Path(__file__).resolve().parent;s=bpy.context.scene
m=bpy.data.materials['Graphite | soft mineral powdercoat'].node_tree.nodes.get('Principled BSDF')
m.inputs['Metallic'].default_value=0
m.inputs['Roughness'].default_value=0.98
s.cycles.samples=10;s.render.resolution_x=768;s.render.resolution_y=512
s.render.filepath=str(p/'renders'/'06_matte_test.png')
bpy.ops.render.render(write_still=True)
print('DONE',s.render.filepath)
