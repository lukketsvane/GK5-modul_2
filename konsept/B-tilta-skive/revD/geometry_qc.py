import bpy, bmesh, math
from pathlib import Path

R=Path(__file__).resolve().parent
s=bpy.context.scene
crown=bpy.data.objects['Upper uninterrupted dish | 342 x 322 mm'].data
bm=bmesh.new()
bm.from_mesh(crown)
bm.faces.ensure_lookup_table()
for f in bm.faces:
    if f.index>=2560:
        f.normal_flip()
bm.to_mesh(crown)
bm.free()
crown.update()
print('CROWN_NORMAL_DOT',crown.polygons[2559].normal.dot(crown.polygons[2560].normal),flush=True)

g=bpy.data.objects['Rear cavity | graded physical reflector']
n=191
nr=18
a=g.data.attributes['heat']
for row in range(nr):
    rr=row/(nr-1)
    for i in range(n):
        t=i/(n-1)
        a.data[row*n+i].value=.80*(max(0,math.sin(math.pi*t))**.68)*((1-rr)**1.35)

floor=bpy.data.materials['Black tabletop'].node_tree
for node in floor.nodes:
    if node.type=='VECT_MATH' and node.operation=='SUBTRACT':
        node.inputs[1].default_value=(.065,-.009,0)
    elif node.type=='VECT_MATH' and node.operation=='MULTIPLY':
        node.inputs[1].default_value=(1/.092,1/.060,0)
ramp=floor.nodes.get('Color Ramp')
for el in ramp.color_ramp.elements:
    if abs(el.position-.39)<.03:el.color=(.50,.50,.50,1)
    if abs(el.position-.70)<.03:el.color=(.015,.015,.015,1)
em=floor.nodes.get('Emission')
em.inputs['Color'].default_value=(1,.395,.152,1)
em.inputs['Strength'].default_value=1.57

lens=bpy.data.materials['Warm opal diffuser with centre glow'].node_tree.nodes.get('Color Ramp')
lens.color_ramp.elements[0].color=(1,.65,.41,1)
lens.color_ramp.elements[1].color=(.88,.54,.32,1)

s.render.resolution_x=1024
s.render.resolution_y=682
s.cycles.samples=24
s.render.filepath=str(R/'renders'/'04_geometry_corrected_preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Concept_B_RevD.blend'))
bpy.ops.render.render(write_still=True)
print('CHECK_RENDER',s.render.filepath,flush=True)
