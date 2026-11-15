# -*- coding: utf-8 -*-
"""
eksporter_3d.py  ·  Ruta som 3D-fil: USDZ til AR på iPhone og iPad, GLB til nettlesaren

Geometrien er delane frå northern.py med middels netting (ut-b/samla). Fila er i meter, med foten på golvet i origo og
framsida mot sjåaren. Delane som ikkje syner utanfrå (ballast, flatstong, stripe, stoppskrue) er ikkje med.

Vippinga er ein animasjon på gruppa «Blad» (bjelke, lok, rute, ark, messingpunkt og skruar), som dreier om røyret:
35° → 0° → 80° → 35°, i sløyfe. AR Quick Look spelar han av seg sjølv, og nettlesaren kan styre han.

Materiala er enkle (UsdPreviewSurface og glTF PBR): matt lakk, messing, klar plate og lysande ark. Dei er ikkje dei
same som i rendringane, der kantar, appelsinhud og dreidd glans ligg i skyggjaren.

  blender.exe -b -P eksporter_3d.py [-- farge]
  skriv ut-b/3d/ruta.usdz, ruta.glb og kontroll.json
"""
import bpy, os, sys, math, json
from mathutils import Matrix, Vector

HER = os.path.dirname(os.path.abspath(__file__))
UT = os.path.join(HER, 'ut-b'); FIN = os.path.join(UT, 'samla'); TRED = os.path.join(UT, '3d')       # middels netting: fin nok med glatte normalar, lett nok til AR
G = json.load(open(os.path.join(UT, 'geometri.json'), encoding='utf-8'))
AKSE = Vector((0.0, G['YT'] / 1000.0, G['AKSE_H'] / 1000.0))
ARG = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
FARGAR = {'graabeige': (0.40, 0.350, 0.285), 'morkegron': (0.020, 0.050, 0.033), 'svart': (0.011, 0.011, 0.012), 'kirsebaer': (0.20, 0.014, 0.020)}
FARGE = ARG[0] if ARG and ARG[0] in FARGAR else 'graabeige'
NAMN = 'ruta' if FARGE == 'graabeige' else 'ruta-' + FARGE
LYS = (1.0, 0.71, 0.43)
FAST = {'01': 'Fot', '02': 'Botnlok', '04': 'Royr', 'leidning': 'Leidning'}
BLAD = {'05': 'Bjelke', '06': 'Bjelkelok', '07': 'Lysleiar', '08': 'Prismeark', '11': 'Messingpunkt', 'E': 'Skruar'}
FORENKLA = {'Leidning': 0.22, 'Royr': 0.45}
FPS = 24
NOKLAR = [(1, 35.0), (36, 35.0), (84, 0.0), (108, 0.0), (180, 80.0), (204, 80.0), (264, 35.0), (288, 35.0)]      # (bilete, helling)

def mat(namn, farge, metall=0.0, ruheit=0.5, alfa=1.0, glod=None, styrke=0.0, gjennom=0.0):
    m = bpy.data.materials.new(namn); m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*farge, 1.0); p.inputs['Metallic'].default_value = metall; p.inputs['Roughness'].default_value = ruheit
    p.inputs['Alpha'].default_value = alfa; p.inputs['Transmission Weight'].default_value = gjennom
    if glod is not None:
        p.inputs['Emission Color'].default_value = (*glod, 1.0); p.inputs['Emission Strength'].default_value = styrke
    if alfa < 1.0:
        for k, v in (('blend_method', 'BLEND'), ('surface_render_method', 'BLENDED')):
            try: setattr(m, k, v)
            except Exception: pass
    return m

def importer(fil, namn, m):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.stl_import(filepath=fil, global_scale=0.001)
    ob = bpy.context.selected_objects[0]; ob.name = namn; ob.data.name = namn
    ob.data.materials.clear(); ob.data.materials.append(m)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30))
    except Exception: pass
    return ob

def tom(namn, pos, forelder=None):
    e = bpy.data.objects.new(namn, None); bpy.context.collection.objects.link(e); e.location = pos
    if forelder is not None: e.parent = forelder
    return e

def under(ob, forelder):
    bpy.context.view_layer.update()
    ob.parent = forelder; ob.matrix_parent_inverse = forelder.matrix_world.inverted()

def gyldige(op, ynske):
    """Berre dei vala denne Blender-utgåva kjenner."""
    k = set(op.get_rna_type().properties.keys())
    return {a: b for a, b in ynske.items() if a in k}

def bygg():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene; s.render.fps = FPS; s.frame_start = NOKLAR[0][0]; s.frame_end = NOKLAR[-1][0]
    s.unit_settings.system = 'METRIC'; s.unit_settings.scale_length = 1.0
    lakk = mat('Lakk', FARGAR[FARGE], 0.0, 0.5)
    M = {'01': lakk, '04': lakk, '05': lakk, '06': lakk, '02': mat('Pute', (0.012, 0.012, 0.013), 0.0, 0.8),
         '07': mat('Akryl', (1.0, 0.98, 0.95), 0.0, 0.06, alfa=0.32, glod=LYS, styrke=0.5, gjennom=0.0),
         '08': mat('Ark', (0.92, 0.74, 0.52), 0.0, 0.35, glod=LYS, styrke=0.9),
         '11': mat('Messing', (0.78, 0.52, 0.20), 1.0, 0.30), 'E': mat('Skrue', (0.02, 0.02, 0.02), 0.6, 0.5),
         'leidning': mat('Leidning', FARGAR[FARGE], 0.0, 0.9)}
    rot = tom('Ruta', (0, 0, 0))
    fast = tom('Fast', (0, 0, 0), rot)
    blad = tom('Blad', AKSE, rot)
    tal = {}
    for i, namn in list(FAST.items()) + list(BLAD.items()):
        f = os.path.join(FIN, i + '.stl')
        if not os.path.exists(f): continue
        ob = importer(f, namn, M[i])
        if namn in FORENKLA:                              # leidningen og røyret er lange, jamne røyr: dei toler færre flater
            mo = ob.modifiers.new('forenkla', 'DECIMATE'); mo.ratio = FORENKLA[namn]
            bpy.context.view_layer.objects.active = ob; bpy.ops.object.modifier_apply(modifier=mo.name)
            try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
            except Exception: pass
        tal[namn] = len(ob.data.polygons)
        under(ob, blad if i in BLAD else fast)
    # vippinga: gruppa dreier om røyret. Kvilestillinga i fila er 35°
    blad.rotation_mode = 'XYZ'
    for bilete, v in NOKLAR:
        blad.rotation_euler = (math.radians(v - G['VINKEL']), 0.0, 0.0)
        blad.keyframe_insert('rotation_euler', frame=bilete)
    s.frame_set(NOKLAR[0][0])
    return s, tal

def usdz(s):
    from pxr import Usd, UsdGeom, UsdUtils, Sdf
    os.makedirs(TRED, exist_ok=True)
    usdc = os.path.join(TRED, NAMN + '.usdc'); ut = os.path.join(TRED, NAMN + '.usdz')
    val = dict(filepath=usdc, selected_objects_only=False, export_animation=True, export_materials=True, generate_preview_surface=True,
               generate_materialx_network=False, export_textures=False, export_normals=True, export_uvmaps=False, export_hair=False,
               convert_orientation=True, export_global_forward_selection='NEGATIVE_Z', export_global_up_selection='Y',
               root_prim_path='', evaluation_mode='RENDER', export_meshes=True, export_lights=False, export_cameras=False, convert_world_material=False,
               triangulate_meshes=True, use_instancing=False)
    bpy.ops.wm.usd_export(**gyldige(bpy.ops.wm.usd_export, val))
    st = Usd.Stage.Open(usdc)
    UsdGeom.SetStageMetersPerUnit(st, 1.0)
    rot = st.GetPrimAtPath('/Ruta')
    if rot: st.SetDefaultPrim(rot)
    st.SetStartTimeCode(NOKLAR[0][0]); st.SetEndTimeCode(NOKLAR[-1][0]); st.SetTimeCodesPerSecond(FPS); st.SetFramesPerSecond(FPS)
    st.GetRootLayer().Save()
    if os.path.exists(ut): os.remove(ut)
    ok = UsdUtils.CreateNewARKitUsdzPackage(Sdf.AssetPath(usdc), ut)
    # kontroll: ARKit-reglane til Pixar sin kontrollør, og kva som faktisk ligg i fila
    k = UsdUtils.ComplianceChecker(arkit=True, skipARKitRootLayerCheck=False)
    k.CheckCompliance(ut)
    st = Usd.Stage.Open(ut)
    bb = UsdGeom.BBoxCache(Usd.TimeCode(NOKLAR[0][0]), [UsdGeom.Tokens.default_]).ComputeWorldBound(st.GetDefaultPrim()).ComputeAlignedRange()
    nett = [p for p in st.Traverse() if p.IsA(UsdGeom.Mesh)]
    blad = st.GetPrimAtPath('/Ruta/Blad')
    prover = 0
    if blad:
        for op in UsdGeom.Xformable(blad).GetOrderedXformOps(): prover = max(prover, len(op.GetTimeSamples()))
    rap = dict(fil=os.path.basename(ut), pakka=bool(ok), kB=round(os.path.getsize(ut) / 1e3), feil=[str(x) for x in k.GetErrors()] + [str(x) for x in k.GetFailedChecks()],
               merknader=[str(x) for x in k.GetWarnings()], opp=str(UsdGeom.GetStageUpAxis(st)), meter_per_eining=UsdGeom.GetStageMetersPerUnit(st),
               storleik_m=[round(v, 4) for v in bb.GetSize()], laagaste_punkt_m=round(bb.GetMin()[1], 4), nett=len(nett),
               trekantar=sum(len(UsdGeom.Mesh(p).GetFaceVertexCountsAttr().Get() or []) for p in nett),
               material=sorted({p.GetName() for p in st.Traverse() if p.GetTypeName() == 'Material'}),
               animasjon=dict(fraa=st.GetStartTimeCode(), til=st.GetEndTimeCode(), bilete_per_sekund=st.GetTimeCodesPerSecond(), tidsprover_paa_blad=prover))
    try: os.remove(usdc)
    except Exception: pass
    return rap

def glb():
    ut = os.path.join(TRED, NAMN + '.glb')
    val = dict(filepath=ut, export_format='GLB', export_animations=True, export_yup=True, export_apply=False, export_materials='EXPORT',
               export_normals=True, export_texcoords=False, export_cameras=False, export_lights=False, export_extras=False,
               export_frame_range=True, export_force_sampling=True, export_nla_strips=False, export_animation_mode='SCENE', export_bake_animation=False,
               export_draco_mesh_compression_enable=False)
    bpy.ops.export_scene.gltf(**gyldige(bpy.ops.export_scene.gltf, val))
    return dict(fil=os.path.basename(ut), kB=round(os.path.getsize(ut) / 1e3))

s, tal = bygg()
rap = dict(farge=FARGE, flater_per_del=tal, usdz=usdz(s), glb=glb())
json.dump(rap, open(os.path.join(TRED, NAMN + '.kontroll.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('TRED', json.dumps(rap, ensure_ascii=False), flush=True)
