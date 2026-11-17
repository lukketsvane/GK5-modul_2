import bpy
import math
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
PARTS = ROOT / "ut-c" / "samla"
OUT = ROOT.parents[2] / "ruta" / "northern" / "images"
OUT.mkdir(parents=True, exist_ok=True)

PRESETS = [
    ("01-hero-light", "light", "black", (0.61, -0.82, 0.45), (-0.015, -0.035, 0.155), 0.68),
    ("02-hero-dark", "dark", "black", (-0.66, -0.75, 0.42), (-0.015, -0.035, 0.150), 0.68),
    ("03-front", "light", "black", (0.00, -0.90, 0.34), (-0.015, -0.025, 0.150), 0.67),
    ("04-profile", "light", "black", (0.90, -0.08, 0.36), (0.0, -0.01, 0.14), 0.67),
    ("05-back", "dark", "black", (0.55, 0.82, 0.43), (0.00, 0.00, 0.155), 0.68),
    ("06-elbow", "dark", "black", (0.40, -0.36, 0.36), (0.13, 0.012, 0.243), 0.22),
    ("07-endcap", "dark", "black", (-0.45, -0.33, 0.34), (-0.19, 0.014, 0.253), 0.22),
    ("08-lightguide", "dark", "black", (-0.14, -0.47, 0.31), (-0.065, -0.09, 0.18), 0.38),
    ("09-base-detail", "light", "black", (0.31, -0.49, 0.21), (0.03, 0.005, 0.045), 0.34),
    ("10-olive", "light", "olive", (0.61, -0.82, 0.45), (-0.015, -0.035, 0.155), 0.68),
    ("11-oxblood", "light", "oxblood", (0.61, -0.82, 0.45), (-0.015, -0.035, 0.155), 0.68),
    ("12-evening", "evening", "black", (0.61, -0.82, 0.43), (-0.015, -0.035, 0.135), 0.68),
    ("13-assembly", "light", "black", (0.73, -0.81, 0.50), (-0.02, -0.035, 0.15), 0.77),
    ("14-chrome-detail", "light", "black", (0.38, -0.43, 0.34), (0.138, 0.026, 0.145), 0.35),
    ("15-forest-hero", "light", "forest", (0.61, -0.82, 0.45), (-0.015, -0.035, 0.155), 0.68),
    ("16-forest-night", "dark", "forest", (-0.66, -0.75, 0.42), (-0.015, -0.035, 0.150), 0.68),
    ("17-forest-front", "light", "forest", (0.00, -0.90, 0.34), (-0.015, -0.025, 0.150), 0.67),
    ("18-forest-profile", "light", "forest", (0.90, -0.08, 0.36), (0.0, -0.01, 0.14), 0.67),
    ("19-forest-back", "dark", "forest", (0.55, 0.82, 0.43), (0.0, 0.0, 0.155), 0.68),
    ("20-forest-joint", "dark", "forest", (0.40, -0.36, 0.36), (0.13, 0.012, 0.243), 0.22),
    ("21-forest-lightguide", "dark", "forest", (-0.14, -0.47, 0.31), (-0.065, -0.09, 0.18), 0.38),
    ("22-forest-base", "light", "forest", (0.31, -0.49, 0.21), (0.03, 0.005, 0.045), 0.34),
    ("23-forest-evening", "evening", "forest", (0.61, -0.82, 0.43), (-0.015, -0.035, 0.135), 0.68),
    ("24-forest-assembly", "light", "forest", (0.73, -0.81, 0.50), (-0.02, -0.035, 0.15), 0.77),
]
COLORS = {
    "black": (0.007, 0.007, 0.009),
    "olive": (0.073, 0.11, 0.073),
    "oxblood": (0.13, 0.023, 0.029),
    "forest": (0.006, 0.015, 0.008),
}
MATERIALS = {}

def material(name, color, metallic=0, roughness=0.5, transmission=0, emission=None, textured=False):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Transmission Weight"].default_value = transmission
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission[0], 1)
        bsdf.inputs["Emission Strength"].default_value = emission[1]
    if textured:
        nt = mat.node_tree
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 430
        tex.inputs["Detail"].default_value = 2
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .10
        bump.inputs["Distance"].default_value = .000065
        nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat

def look(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat('-Z', 'Y').to_euler()

def area(name, pos, target, power, color, sx, sy):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = power
    data.color = color
    data.shape = 'RECTANGLE'
    data.size = sx
    data.size_y = sy
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = pos
    look(obj, target)
    return obj

def cube(name, location, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj=bpy.context.object
    obj.name=name
    obj.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj

def setup(mode, finish, key, quality):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    scene.cycles.samples = 64 if quality == "final" else 18
    scene.cycles.use_denoising=True
    scene.render.resolution_x = 1920 if quality == "final" else 950
    scene.render.resolution_y = 1200 if quality == "final" else 594
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.render.film_transparent=False
    scene.render.image_settings.color_mode='RGBA'
    scene.view_settings.view_transform='AgX'
    scene.view_settings.exposure=-0.7
    try:
        pref=bpy.context.preferences.addons['cycles'].preferences
        pref.compute_device_type='CUDA'
        pref.get_devices()
        for dev in pref.devices: dev.use=True
        scene.cycles.device='GPU'
    except Exception as e:
        scene.cycles.device='CPU'
        print("GPU unavailable",str(e))
    world=bpy.data.worlds.new('Studio')
    scene.world=world
    world.use_nodes=True
    bg=world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value=(.38,.36,.34,1) if mode == 'light' else (.035,.035,.032,1)
    bg.inputs['Strength'].default_value=.22 if mode == 'light' else .08
    finish_mat=material('Forest green lacquer' if finish == 'forest' else 'Matte SLS powdercoat '+finish,COLORS[finish],roughness=.17 if finish == 'forest' else .56,textured=finish != 'forest')
    if finish == 'forest':
        finish_mat.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value = 0.3
        finish_mat.node_tree.nodes['Principled BSDF'].inputs['Coat Roughness'].default_value = 0.1
    chrome=material('Chromed copper',(.60,.62,.65),metallic=.95,roughness=.17)
    steel=material('Hidden steel',(.18,.17,.16),metallic=.78,roughness=.40)
    gold=material('Gold lacquered end cap',(.48,.29,.09),metallic=.65,roughness=.32)
    acrylic=material('Clear PMMA lightguide',(.82,.88,.91),roughness=.24,transmission=.75,emission=((1,.80,.56),.06))
    prism=material('Recovered microprism film',(.69,.58,.43),roughness=.30,transmission=.14,emission=((1,.79,.55),.17))
    led=material('Warm LED',(.95,.83,.63),roughness=.22,emission=((1,.63,.30),1.8))
    cable=material('Cable',(.025,.025,.025),roughness=.7)
    matmap={
        '01':finish_mat,'02':finish_mat,'03':steel,'04':chrome,'05h':finish_mat,'05v':finish_mat,
        '06h':finish_mat,'06v':finish_mat,'07':acrylic,'08':prism,'09':chrome,'10':led,
        '11':gold,'12':finish_mat,'13':finish_mat,'14':finish_mat,
        'E':steel,'F':steel,'G':steel,'leidning':cable
    }
    parts={}
    for file in sorted(PARTS.glob('*.stl')):
        bpy.ops.wm.stl_import(filepath=str(file),global_scale=.001)
        obj=bpy.context.object
        obj.name=file.stem
        obj.data.materials.clear()
        obj.data.materials.append(matmap.get(file.stem,finish_mat))
        parts[file.stem]=obj
    if key.startswith(('13', '24')):
        shift={
            '02':(0,0,-.03),'03':(0,0,.038),'04':(.08,0,0),
            '05v':(-.065,0,.012),'05h':(.06,0,.012),
            '06v':(-.065,-.045,-.022),'06h':(.065,-.045,-.022),
            '07':(0,-.075,-.028),'08':(0,-.10,-.015),
            '09':(0,.04,.055),'10':(0,-.055,.02),
            '11':(-.037,0,0),'12':(.055,.02,.02),
            '13':(.04,.015,0),'14':(.018,0,.013)
        }
        for name,delta in shift.items():
            if name in parts:
                obj=parts[name]
                obj.location+=Vector(delta)
    dark=mode != "light"
    floor_mat = material('Studio dark floor' if dark else 'Offwhite studio floor',(.007,.007,.007) if dark else (.78,.765,.73),roughness=.73)
    cube('Floor', (0,0,-.018), (8,8,.025),floor_mat)
    if mode=='evening':
        floor_mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.095,.060,.043,1)
        paper=material('Paper',(.76,.70,.58),roughness=.9)
        cube('Reading sheet',(-.060,-.12,-.004),(.28,.17,.0015),paper)
    area('Large studio softbox',(-.35,-.56,.83),(-.02,0,.16),20 if not dark else 11,(1,.91,.82),.95,.68)
    area('Rear rim',(.28,.32,.69),(0,0,.16),18 if not dark else 9,(.94,.96,1),.8,.4)
    area('Long strip',(-.13,.12,.68),(0,0,.23),7,(1,1,1),.75,.13)
    area('Bounce front',(-.02,-.60,.33),(0,0,.16),5 if not dark else 2,(1,.86,.71),.65,.45)
    if key not in ('05-back', '09-base-detail', '13-assembly', '19-forest-back', '22-forest-base', '24-forest-assembly'):
        area('Lightguide illumination',(-.026,-.06,.20),(-.04,-.06,-.016),3.5 if not dark else 4.5,(1,.64,.35),.30,.185)
    return scene,parts

def frame(name, mode, finish, pos, target, scale, quality):
    scene,parts=setup(mode,finish,name,quality)
    data=bpy.data.cameras.new('Hasselblad 65mm study')
    cam=bpy.data.objects.new('Hasselblad 65mm study',data)
    bpy.context.collection.objects.link(cam)
    cam.location=pos
    look(cam,target)
    data.type='ORTHO'
    data.ortho_scale=scale
    scene.camera=cam
    scene.render.filepath=str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('RENDERED',name,scene.render.filepath,flush=True)

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
quality='final' if '--final' in args else 'preview'
selection=[x for x in args if not x.startswith('--')]
for p in PRESETS:
    if not selection or p[0][:2] in selection or p[0] in selection:
        frame(*p,quality)
