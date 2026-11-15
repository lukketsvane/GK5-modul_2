import bpy
import math
from pathlib import Path
from mathutils import Vector

CAD = Path(__file__).resolve().parent
PARTS = CAD / 'ut-c' / 'samla'
OUT = CAD.parents[2] / 'ruta' / 'northern' / 'ruta-c.glb'
MOVING = {'05h','05v','06h','06v','07','08','10','11','13','E','G'}

def material(name, rgb, metal=0, rough=.5, alpha=1, emission=None):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    p.inputs['Alpha'].default_value=alpha
    if emission:
        p.inputs['Emission Color'].default_value=(*emission[0],1)
        p.inputs['Emission Strength'].default_value=emission[1]
    if alpha<1:
        m.surface_render_method='BLENDED'
    return m

bpy.ops.wm.read_factory_settings(use_empty=True)
coat=material('BodyFinish',(.025,.025,.027),rough=.62)
chrome=material('ChromeCopper',(.67,.70,.73),metal=.93,rough=.21)
steel=material('Steel',(.28,.30,.32),metal=.7,rough=.46)
gold=material('GoldPaint',(.52,.34,.12),metal=.64,rough=.32)
pmma=material('ClearLightGuide',(.81,.88,.93),rough=.19,alpha=.38,emission=((1,.78,.51),.28))
film=material('RecycledPrismFilm',(.79,.70,.57),rough=.33,emission=((1,.75,.47),.38))
led=material('LEDStrip',(.95,.85,.68),rough=.37,emission=((1,.72,.42),2.2))
cable=material('PowerCord',(.018,.018,.019),rough=.72)
mats={'03':steel,'04':chrome,'07':pmma,'08':film,'09':chrome,'10':led,'11':gold,'E':steel,'F':steel,'G':steel,'leidning':cable}

def empty(name,location,parent=None):
    o=bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(o)
    o.location=location
    if parent: o.parent=parent
    return o

root=empty('RUTA_C',(0,0,0))
fixed=empty('Fast',(0,0,0),root)
pivot=empty('Blad',(0,.022,.260),root)
objs=[]
for f in sorted(PARTS.glob('*.stl')):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.stl_import(filepath=str(f),global_scale=.001)
    ob=bpy.context.object
    ob.name=f.stem
    ob.data.materials.clear()
    ob.data.materials.append(mats.get(f.stem,coat))
    bpy.context.view_layer.objects.active=ob
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
    except AttributeError: pass
    parent=pivot if f.stem in MOVING else fixed
    bpy.context.view_layer.update()
    ob.parent=parent
    ob.matrix_parent_inverse=parent.matrix_world.inverted()
    objs.append(ob)

bpy.context.view_layer.update()
assert len(objs)==20,len(objs)
assert len(pivot.children)==len(MOVING),(len(pivot.children),len(MOVING))
OUT.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(OUT),export_format='GLB',export_yup=True,export_apply=False,export_materials='EXPORT',export_normals=True,export_texcoords=False,export_cameras=False,export_lights=False,export_animations=False,export_extras=True)
assert OUT.is_file() and OUT.stat().st_size>100000
print('C_MODEL_EXPORT_OK',str(OUT),'BYTES',OUT.stat().st_size,'PARTS',len(objs),'MOVING',len(pivot.children),flush=True)
