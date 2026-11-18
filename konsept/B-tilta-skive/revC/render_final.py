import bpy
from pathlib import Path
R=Path(__file__).resolve().parent
s=bpy.context.scene
top=bpy.data.materials['Matte warm graphite | anodized aluminum'].node_tree.nodes.get('Principled BSDF')
top.inputs['Base Color'].default_value=(.041,.040,.040,1)
halo=bpy.data.materials['Rear halo optical insert'].node_tree.nodes.get('Emission')
halo.inputs['Color'].default_value=(1,.52,.27,1)
halo.inputs['Strength'].default_value=.72
s.render.engine='CYCLES'
s.cycles.samples=64
s.cycles.use_denoising=True
s.render.resolution_x=1536
s.render.resolution_y=1024
s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
s.render.filepath=str(R/'renders'/'B_REFERENCE_MATCH_CYCLES.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'B_Reference_Match.blend'))
bpy.ops.render.render(write_still=True)
print('FINAL_RENDER',s.render.filepath,flush=True)
