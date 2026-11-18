import bpy
for o in bpy.data.objects:
    if o.type=='MESH':
        print('MESH',o.name,'verts',len(o.data.vertices),'mods',[(m.type,m.name) for m in o.modifiers], 'bbox', [[round(float(v),3) for v in b] for b in (o.bound_box[0],o.bound_box[6])])
    elif o.type=='LIGHT': print('LIGHT',o.name,round(o.data.energy,3),tuple(round(x,3) for x in o.location))
    elif o.type=='CAMERA': print('CAMERA',o.name,tuple(round(x,3) for x in o.location),'lens',o.data.lens)
print('SCENE',bpy.context.scene.view_settings.exposure)
