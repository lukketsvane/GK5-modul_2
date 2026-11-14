# -*- coding: utf-8 -*-
"""
render_ekte.py  ·  rendringane av Ruta, revisjon B, til presentasjonen. Ingen genererte bilete.

Geometrien er delane frå northern.py med fin netting (ut-b/fin/*.stl, frå eksporter_fin.py). Biletet blir rekna i
Cycles på skjermkortet. Det som skil dette frå render_presentasjon.py:

  kantar     alle skarpe kantar får ein radius på 0,3 mm i skyggjaren, slik lakkerte og dreidde delar har
  lakk       matt pulverlakk med fin appelsinhud
  messing    dreidd flate: glansen følgjer sirklar om midten av skiva
  ruta       plata er klar akryl som lyser frå undersida og frå den frie kanten, arket lyser frå oversida, mest ved
             bjelken. Det er rutene sitt eige lys som lyser opp golvet. Styrkane er sette for biletet, ikkje rekna
  studio     éi lang smal lysflate over og litt bak lampa, eit svakt kantlys, svart rom. Lysa treff berre lampa
  kamera     same utsnitt som førelegga (lang linse eller utan perspektiv), blendar og skarpleik som eit kamera
  linse      lysspreiinga i linsa er lagt på etterpå som ei folding av det lineære biletet (tre gaussklokker)

  blender.exe -b -P render_ekte.py -- helt messing ... [--prove]
  visingar: framside helt front profil vifte messing fargar kant boge kveld
"""
import bpy, os, sys, math, json
import numpy as np
from mathutils import Matrix, Vector

HER = os.path.dirname(os.path.abspath(__file__))
UT = os.path.join(HER, 'ut-b'); FIN = os.path.join(UT, 'fin'); RUT = os.path.join(UT, 'ekte')
G = json.load(open(os.path.join(UT, 'geometri.json'), encoding='utf-8'))
PROVE = '--prove' in sys.argv
VIS = [a for a in sys.argv[sys.argv.index('--') + 1:] if not a.startswith('--')] if '--' in sys.argv else []
AKSE = Vector((0.0, G['YT'] / 1000.0, G['AKSE_H'] / 1000.0))
_t = math.radians(G['VINKEL'])
UT_I_RUTA = (0.0, -math.cos(_t), -math.sin(_t))            # frå bjelken ut i ruta, slik delane ligg i fila
UNDERSIDE = (0.0, math.sin(_t), -math.cos(_t))             # ut av undersida på ruta
FARGE = {'graabeige': (0.40, 0.350, 0.285), 'morkegron': (0.020, 0.050, 0.033), 'svart': (0.011, 0.011, 0.012), 'kirsebaer': (0.20, 0.014, 0.020)}
ROERLEG = ('05', '06', '07', '08', '09', '10', '11', '13', 'E')
STOR = (2256, 1600)
UTE = 0.0285                            # så langt frå røyret kjem ruta ut av bjelken
RILLE = float(next((a.split('=')[1] for a in sys.argv if a.startswith('--rille=')), 0.0005))                         # rillene i arket i nærbileta: 0,5 mm. Eit verkeleg prismeark har om lag 0,05 mm, og det syner ikkje i biletet

# ------------------------------------------------------------------ oppsett

def oppsett(prover=256, eksponering=0.0):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    try:
        p = bpy.context.preferences.addons['cycles'].preferences
        p.compute_device_type = 'CUDA'; p.get_devices()
        for d in p.devices: d.use = (d.type != 'CPU')
        s.cycles.device = 'GPU'
    except Exception as e:
        print('SKJERMKORT IKKJE I BRUK', e, flush=True); s.cycles.device = 'CPU'
    s.render.threads_mode = 'FIXED'; s.render.threads = 4
    w, h = STOR
    if PROVE: w, h, prover = w // 3, h // 3, 72
    if '--grov' in sys.argv: prover = 48
    for a in sys.argv:                                   # --utsnitt=x0,y0,x1,y1 som brøkar: rendrar berre eit utsnitt, til feilsøking
        if a.startswith('--utsnitt='):
            x0, y0, x1, y1 = [float(v) for v in a.split('=')[1].split(',')]
            s.render.use_border = True; s.render.use_crop_to_border = True
            s.render.border_min_x, s.render.border_max_x, s.render.border_min_y, s.render.border_max_y = x0, x1, 1.0 - y1, 1.0 - y0
    s.render.resolution_x, s.render.resolution_y = w, h
    s.cycles.samples = prover; s.cycles.use_adaptive_sampling = True; s.cycles.adaptive_threshold = 0.012; s.cycles.adaptive_min_samples = 48
    s.cycles.use_denoising = '--raa' not in sys.argv
    try: s.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception: pass
    s.cycles.max_bounces = 14; s.cycles.transmission_bounces = 14; s.cycles.glossy_bounces = 8; s.cycles.diffuse_bounces = 4
    s.cycles.sample_clamp_indirect = 8.0
    s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'; s.view_settings.exposure = eksponering
    v = bpy.data.worlds.new('verd'); s.world = v; v.use_nodes = True
    v.node_tree.nodes['Background'].inputs['Color'].default_value = (0, 0, 0, 1)
    return s

def skaansam():
    try:
        import ctypes
        k = ctypes.windll.kernel32; h = k.GetCurrentProcess()
        k.SetPriorityClass(h, 0x40); k.SetProcessAffinityMask(h, 0xFC)     # lågaste prioritet og kjerne 0 og 1 frie: skjermkortet gjer arbeidet, og lyden skal ikkje hakke
    except Exception:
        pass

# ------------------------------------------------------------------ skyggjarar

def ny(namn):
    m = bpy.data.materials.new(namn); m.use_nodes = True
    return m, m.node_tree, m.node_tree.nodes['Principled BSDF']

def node(nt, slag, **eig):
    n = nt.nodes.new(slag)
    for k, v in eig.items(): setattr(n, k, v)
    return n

def tal(nt, op, a, b=None, c=None):
    """Éin reknenode. a, b, c er anten tal eller utgangar."""
    n = node(nt, 'ShaderNodeMath', operation=op)
    for i, x in enumerate((a, b, c)):
        if x is None: continue
        if isinstance(x, (int, float)): n.inputs[i].default_value = x
        else: nt.links.new(x, n.inputs[i])
    return n.outputs[0]

def prikk(nt, vektor, retning):
    n = node(nt, 'ShaderNodeVectorMath', operation='DOT_PRODUCT')
    nt.links.new(vektor, n.inputs[0]); n.inputs[1].default_value = retning
    return n.outputs['Value']

def kant(nt, radius=0.0003):
    b = node(nt, 'ShaderNodeBevel', samples=6); b.inputs['Radius'].default_value = radius
    return b.outputs['Normal']

def ut_i_ruta(nt, tc):
    """Avstanden frå røyret ut i ruta i meter, og 1 der ruta er utanfor bjelken (0 inni, så ikkje lys lek ut gjennom fugene)."""
    pos = node(nt, 'ShaderNodeVectorMath', operation='SUBTRACT'); nt.links.new(tc.outputs['Object'], pos.inputs[0]); pos.inputs[1].default_value = tuple(AKSE)
    u = prikk(nt, pos.outputs['Vector'], UT_I_RUTA)
    return u, tal(nt, 'GREATER_THAN', u, UTE)

def lakk(farge):
    """Matt pulverlakk: fin appelsinhud og avrunda kantar."""
    m, nt, p = ny('lakk')
    p.inputs['Base Color'].default_value = (*farge, 1.0); p.inputs['Roughness'].default_value = 0.46
    tc = node(nt, 'ShaderNodeTexCoord')
    st = node(nt, 'ShaderNodeTexNoise'); st.inputs['Scale'].default_value = 2600.0; st.inputs['Detail'].default_value = 2.0
    nt.links.new(tc.outputs['Object'], st.inputs['Vector'])
    bu = node(nt, 'ShaderNodeBump'); bu.inputs['Strength'].default_value = 0.22; bu.inputs['Distance'].default_value = 0.00004
    nt.links.new(st.outputs[0], bu.inputs['Height']); nt.links.new(kant(nt, 0.00035), bu.inputs['Normal'])
    nt.links.new(bu.outputs['Normal'], p.inputs['Normal'])
    nt.links.new(tal(nt, 'MULTIPLY_ADD', st.outputs[0], 0.10, 0.41), p.inputs['Roughness'])
    return m

def messing():
    """Dreidd messing: glansen ligg i sirklar om midten (objektet må ha origo i midten av skiva)."""
    m, nt, p = ny('messing')
    p.inputs['Base Color'].default_value = (0.78, 0.52, 0.20, 1.0); p.inputs['Metallic'].default_value = 1.0
    p.inputs['Roughness'].default_value = 0.26; p.inputs['Anisotropic'].default_value = 0.82
    ta = node(nt, 'ShaderNodeTangent', direction_type='RADIAL', axis='X')
    tt = node(nt, 'ShaderNodeVectorMath', operation='ADD'); nt.links.new(ta.outputs['Tangent'], tt.inputs[0]); tt.inputs[1].default_value = (0.0, 0.004, 0.003)
    nt.links.new(tt.outputs['Vector'], p.inputs['Tangent'])      # litt til, så retninga aldri har lengd null i midten av skiva
    nt.links.new(kant(nt, 0.00025), p.inputs['Normal'])
    return m

def staal():
    m, nt, p = ny('staal')
    p.inputs['Base Color'].default_value = (0.55, 0.55, 0.56, 1.0); p.inputs['Metallic'].default_value = 1.0; p.inputs['Roughness'].default_value = 0.35
    return m

def matt(namn, farge, ruheit=0.7):
    m, nt, p = ny(namn)
    p.inputs['Base Color'].default_value = (*farge, 1.0); p.inputs['Roughness'].default_value = ruheit
    return m

LYS = (1.0, 0.71, 0.43)                 # lysfargen til ruta slik kameraet ser 2700 K

def akryl(styrke=1.0):
    """Plata: klar akryl. Lyset kjem ut av undersida, av den frie kanten og litt av sidekantane."""
    m, nt, p = ny('akryl')
    p.inputs['Base Color'].default_value = (1.0, 0.985, 0.96, 1.0); p.inputs['Roughness'].default_value = 0.03
    p.inputs['Transmission Weight'].default_value = 1.0; p.inputs['IOR'].default_value = 1.49
    tc = node(nt, 'ShaderNodeTexCoord'); nrm = tc.outputs['Normal']
    under = tal(nt, 'GREATER_THAN', prikk(nt, nrm, UNDERSIDE), 0.9)
    fri = tal(nt, 'GREATER_THAN', prikk(nt, nrm, UT_I_RUTA), 0.45)
    side = tal(nt, 'GREATER_THAN', tal(nt, 'ABSOLUTE', prikk(nt, nrm, (1.0, 0.0, 0.0))), 0.9)
    s = tal(nt, 'ADD', tal(nt, 'ADD', tal(nt, 'MULTIPLY', under, 1.5 * styrke), tal(nt, 'MULTIPLY', fri, 9.0 * styrke)), tal(nt, 'MULTIPLY', side, 5.0 * styrke))
    u, ute = ut_i_ruta(nt, tc)
    ge = node(nt, 'ShaderNodeNewGeometry')                                     # flatene lyser berre utover: ovanfrå ser ein ikkje undersida lyse gjennom plata
    framside = tal(nt, 'SUBTRACT', 1.0, ge.outputs['Backfacing'])
    p.inputs['Emission Color'].default_value = (*LYS, 1.0); nt.links.new(tal(nt, 'MULTIPLY', tal(nt, 'MULTIPLY', s, ute), framside), p.inputs['Emission Strength'])
    return m

def ark(styrke=1.0, liner=False):
    """Prismearket: lyser frå oversida, mest der det møter bjelken. Glansen følgjer rillene, som går frå bjelken mot kanten.
    liner=True legg rillene inn som fin relieff (0,1 mm), til nærbileta."""
    m, nt, p = ny('ark')
    p.inputs['Base Color'].default_value = (0.92, 0.90, 0.86, 1.0); p.inputs['Roughness'].default_value = 0.22
    p.inputs['Transmission Weight'].default_value = 0.92; p.inputs['IOR'].default_value = 1.5      # klart ark: det er gløden som syner, ikkje ei kvit flate
    p.inputs['Anisotropic'].default_value = 0.6
    vt = node(nt, 'ShaderNodeVectorTransform', vector_type='VECTOR', convert_from='OBJECT', convert_to='WORLD')
    vt.inputs['Vector'].default_value = tuple(Vector(UT_I_RUTA) + 0.04 * Vector(UNDERSIDE) + Vector((0.04, 0.0, 0.0)))     # aldri parallell med ein flatenormal
    nt.links.new(vt.outputs['Vector'], p.inputs['Tangent'])
    tc = node(nt, 'ShaderNodeTexCoord')
    u, ute = ut_i_ruta(nt, tc)
    lengd = tal(nt, 'SUBTRACT', u, UTE)
    nar = tal(nt, 'EXPONENT', tal(nt, 'MINIMUM', tal(nt, 'MULTIPLY', lengd, -1.0 / 0.008), 0.0))             # heitast ved bjelken, der stripa sit
    fall = tal(nt, 'SUBTRACT', 1.0, tal(nt, 'MULTIPLY', tal(nt, 'MINIMUM', tal(nt, 'MAXIMUM', lengd, 0.0), 0.175), 0.25 / 0.175))   # litt svakare utover
    s = tal(nt, 'MULTIPLY', tal(nt, 'MULTIPLY', tal(nt, 'MULTIPLY_ADD', nar, 4.0, 1.0), fall), 0.30 * styrke)
    if liner:
        bo = node(nt, 'ShaderNodeTexWave', wave_type='BANDS', bands_direction='X', wave_profile='SAW')
        bo.inputs['Scale'].default_value = 2.0 * math.pi / (20.0 * RILLE)
        nt.links.new(tc.outputs['Object'], bo.inputs['Vector'])
        bu = node(nt, 'ShaderNodeBump'); bu.inputs['Strength'].default_value = 1.0; bu.inputs['Distance'].default_value = 0.00012
        nt.links.new(bo.outputs[1], bu.inputs['Height']); nt.links.new(bu.outputs['Normal'], p.inputs['Normal'])
        s = tal(nt, 'MULTIPLY', s, tal(nt, 'MULTIPLY_ADD', bo.outputs[1], 0.60, 0.55))
    p.inputs['Emission Color'].default_value = (*LYS, 1.0); nt.links.new(tal(nt, 'MULTIPLY', s, ute), p.inputs['Emission Strength'])
    return m

def golv_materiale(farge=(0.010, 0.010, 0.011), ruheit=0.30):
    m, nt, p = ny('golv')
    p.inputs['Base Color'].default_value = (*farge, 1.0); p.inputs['Roughness'].default_value = ruheit
    return m

# ------------------------------------------------------------------ scena

def importer(fil, m, glatt=30):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.stl_import(filepath=fil, global_scale=0.001)
    ob = bpy.context.selected_objects[0]
    ob.data.materials.clear(); ob.data.materials.append(m)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)      # måla i meter inn i sjølve nettet, så skyggjarane kan rekne med objektkoordinatar
    try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(glatt))
    except Exception: pass
    return ob

def lampe(farge='graabeige', styrke=1.0, liner=False):
    """Les inn delane. Returnerer {id: objekt}. Alle ligg òg i samlinga 'lampe', som studiolysa er lenkte til."""
    la = lakk(FARGE[farge]); st = staal(); sk = matt('svart skrue', (0.015, 0.015, 0.016), 0.5)
    M = {'01': la, '02': matt('pute', (0.012, 0.012, 0.013)), '03': st, '04': la, '05': la, '06': la, '07': akryl(styrke), '08': ark(styrke, liner),
         '09': st, '10': matt('stripe', (0.9, 0.85, 0.7)), '11': messing(), '12': sk, '13': sk, 'E': sk, 'leidning': matt('leidning', FARGE[farge], 0.8)}
    sam = bpy.data.collections.new('lampe'); bpy.context.scene.collection.children.link(sam)
    # studiolysa treff alt utanom ruta: ei blank rute speglar lysflata over seg og mistar gløden. Fotografen skjermar lyset frå glaset
    lyst = bpy.data.collections.new('studiolyst'); bpy.context.scene.collection.children.link(lyst)
    O = {}
    for i, m in M.items():
        f = os.path.join(FIN, i + '.stl')
        if not os.path.exists(f): continue
        ob = importer(f, m); ob.name = 'del_' + i; O[i] = ob
        sam.objects.link(ob)
        if i not in ('07', '08'): lyst.objects.link(ob)
    if '11' in O:                                                    # glansen i messingen skal gå om midten av skiva
        bpy.ops.object.select_all(action='DESELECT'); O['11'].select_set(True); bpy.context.view_layer.objects.active = O['11']
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    if '08' in O:                                                    # arket ligg mot plata i CAD-en. Like flater gjev trekantmønster, så det blir løfta 0,1 mm
        O['08'].matrix_world = Matrix.Translation(Vector((0.0, -math.sin(_t), math.cos(_t))) * 0.00012) @ O['08'].matrix_world
    bpy.context.view_layer.update()
    return O

def hell(O, vinkel):
    R = Matrix.Translation(AKSE) @ Matrix.Rotation(math.radians(vinkel - G['VINKEL']), 4, 'X') @ Matrix.Translation(-AKSE)
    for i in ROERLEG:
        if i in O: O[i].matrix_world = R @ O[i].matrix_world
    bpy.context.view_layer.update()

def midt(ob):
    return sum((ob.matrix_world @ Vector(c) for c in ob.bound_box), Vector()) / 8.0

def peik(ob, maal):
    ob.rotation_euler = (Vector(maal) - ob.location).to_track_quat('-Z', 'Y').to_euler()

def flate(namn, pos, maal, bx, by, styrke, farge=(1, 1, 1), spreiing=120.0, berre_lampa=True):
    """Ei rektangulær lysflate. Ho lyser berre på dei lakkerte delane og messingen, ikkje på golvet og ikkje på ruta."""
    ld = bpy.data.lights.new(namn, 'AREA'); ld.shape = 'RECTANGLE'; ld.size = bx; ld.size_y = by; ld.energy = styrke; ld.color = farge
    try: ld.spread = math.radians(spreiing)
    except Exception: pass
    ob = bpy.data.objects.new(namn, ld); bpy.context.collection.objects.link(ob); ob.location = pos; peik(ob, maal)
    if berre_lampa:
        try: ob.light_linking.receiver_collection = bpy.data.collections['studiolyst']
        except Exception as e: print('LYSLENKING VERKAR IKKJE', e, flush=True)
    return ob

def golv(farge=(0.010, 0.010, 0.011), ruheit=0.30):
    bpy.ops.mesh.primitive_plane_add(size=12.0, location=(0, 0, 0))
    ob = bpy.context.object; ob.name = 'golv'; ob.data.materials.append(golv_materiale(farge, ruheit)); return ob

def studio(nokkel=3.2, kantlys=3.0, fyll=0.8, x=0.0):
    """Éi lang smal lysflate over og litt bak lampa, eit kjølig kantlys bakfrå, og eit svakt fyll frå kamerasida."""
    flate('nokkel', (x, 0.16, 0.70), (x, 0.0, 0.25), 1.5, 0.16, nokkel, (1.0, 0.975, 0.95), 100.0)
    flate('kantlys', (-0.9, 1.1, 0.55), (0.0, 0.0, 0.2), 0.7, 0.7, kantlys, (0.86, 0.92, 1.0))
    flate('fyll', (0.3, -2.2, 0.6), (0.0, 0.0, 0.15), 2.0, 2.0, fyll, (1.0, 0.97, 0.94))

def kamera(pos, maal, lens, fstop=None, fokus=None):
    s = bpy.context.scene
    kam = bpy.data.cameras.new('kam'); kam.lens = lens
    ko = bpy.data.objects.new('kam', kam); bpy.context.collection.objects.link(ko)
    ko.location = pos; peik(ko, maal); s.camera = ko
    if fstop and '--utan-dof' not in sys.argv:
        kam.dof.use_dof = True; kam.dof.aperture_fstop = fstop
        kam.dof.focus_distance = (Vector(fokus if fokus is not None else maal) - Vector(pos)).length
    bpy.context.view_layer.update()
    return ko

def kamera_orto(pos, maal, breidd):
    s = bpy.context.scene
    kam = bpy.data.cameras.new('kam'); kam.type = 'ORTHO'; kam.ortho_scale = breidd
    ko = bpy.data.objects.new('kam', kam); bpy.context.collection.objects.link(ko)
    ko.location = pos; peik(ko, maal); s.camera = ko
    bpy.context.view_layer.update()
    return ko

# ------------------------------------------------------------------ linsa og fila

def _uskarp(a, sigma):
    """Gaussisk utjamning med FFT, kant for kant spegla."""
    h, w = a.shape[:2]; r = int(3 * sigma) + 1
    b = np.pad(a, ((r, r), (r, r), (0, 0)), mode='reflect')
    fy = np.fft.fftfreq(b.shape[0])[:, None]; fx = np.fft.rfftfreq(b.shape[1])[None, :]
    k = np.exp(-2.0 * (math.pi * sigma) ** 2 * (fx * fx + fy * fy))
    ut = np.empty_like(b)
    for c in range(b.shape[2]):
        ut[:, :, c] = np.fft.irfft2(np.fft.rfft2(b[:, :, c]) * k, s=b.shape[:2])
    return ut[r:r + h, r:r + w]

def rendre(namn, glans=(0.040, 0.016, 0.008)):
    """Rendrar til lineær EXR, legg på lysspreiinga i linsa, og lagrar PNG med same fargehandsaming som scena."""
    s = bpy.context.scene
    os.makedirs(RUT, exist_ok=True)
    namn = namn + ('-prove' if PROVE else '')
    exr = os.path.join(RUT, namn + '.exr'); png = os.path.join(RUT, namn + '.png')
    s.render.image_settings.file_format = 'OPEN_EXR'; s.render.image_settings.color_depth = '32'
    s.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(exr)
    w, h = im.size; a = np.empty(w * h * 4, dtype=np.float32); im.pixels.foreach_get(a); a = a.reshape(h, w, 4)
    ugyldige = int((~np.isfinite(a[:, :, :3])).sum()); print('PIKSLAR %s: ugyldige %d, høgst %.2f, snitt %.4f' % (namn, ugyldige, float(np.nanmax(a[:, :, :3])), float(np.nanmean(a[:, :, :3]))), flush=True)
    rgb = np.clip(np.nan_to_num(a[:, :, :3], nan=0.0, posinf=40.0, neginf=0.0), 0.0, 40.0); f = w / 2256.0
    ut = (1.0 - sum(glans)) * rgb
    for vekt, sigma in zip(glans, (5.0, 22.0, 90.0)):
        ut = ut + vekt * _uskarp(rgb, sigma * f)
    a[:, :, :3] = ut; a[:, :, 3] = 1.0
    im.pixels.foreach_set(a.ravel()); im.update()
    s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_depth = '8'; s.render.image_settings.color_mode = 'RGB'
    im.save_render(png, scene=s)
    bpy.data.images.remove(im)
    try: os.remove(exr)
    except Exception: pass
    print('RENDRA', png, flush=True)

# ------------------------------------------------------------------ visingane (same utsnitt som førelegga)

def vis_helt():
    oppsett(); lampe(); golv(); studio()
    kamera((-1.287, -2.018, 0.469), (-0.099, 0.04, 0.135), 120, fstop=11.0, fokus=(-0.05, -0.05, 0.2)); rendre('r-helt')

def vis_front():
    oppsett(); lampe(); golv(); studio()
    kamera_orto((-0.02, -3.0, 0.30), (-0.02, 0.0, 0.143), 0.62); rendre('r-front')

def _profil(vinkel=None):
    oppsett(); O = lampe(); golv(); studio(kantlys=2.0)
    flate('kort', (-2.7, 0.15, 0.32), (-0.2, 0.02, 0.26), 1.2, 1.2, 3.5, (1.0, 0.97, 0.93))        # lysflata messingen speglar
    if vinkel is not None: hell(O, float(vinkel))
    return O

def vis_profil():
    _profil(); kamera_orto((-3.0, -0.03, 0.160), (0.0, -0.03, 0.148), 0.56); rendre('r-profil')

def vis_framside():
    _profil(0); kamera_orto((-3.0, -0.085, 0.26), (0.0, -0.085, 0.26), 0.36); rendre('r-framside')

def vis_vifte():
    for v in (0, 40, 80):
        _profil(v); kamera_orto((-3.0, -0.03, 0.160), (0.0, -0.03, 0.148), 0.56); rendre('r-vifte-%02d' % v)

def _messing(farge):
    oppsett(); O = lampe(farge, liner=True); p = midt(O['11'])
    studio(nokkel=3.0, kantlys=2.5, fyll=1.0, x=p.x + 0.2)
    flate('kort', p + Vector((-0.77, 0.91, -0.17)), p, 1.0, 1.0, 0.75, (1.0, 0.97, 0.93))
    kamera(p + Vector((-0.22, -0.26, 0.05)), p + Vector((0.022, -0.012, -0.006)), 105, fstop=11.0, fokus=p + Vector((0.0, -0.012, 0.0)))

def vis_messing():
    _messing('graabeige'); rendre('r-messing')

def vis_fargar():
    for f in ('morkegron', 'svart', 'kirsebaer'):
        _messing(f); rendre('r-messing-' + f)

def vis_boge():
    oppsett(); lampe(liner=True)
    m = Vector((G['T2'][0] / 1000.0 + 0.012, G['YT'] / 1000.0, G['AKSE_H'] / 1000.0 - 0.012))
    studio(nokkel=3.0, kantlys=2.5, fyll=1.2, x=m.x - 0.2)
    kamera(m + Vector((0.15, -0.30, 0.09)), m, 105, fstop=11.0, fokus=m + Vector((-0.012, -0.012, 0.012))); rendre('r-boge')

def vis_kant():
    """Hjørnet og den frie kanten, med ruta vassrett: då er bakgrunnen golvet langt under, ikkje foten."""
    oppsett(); O = lampe(liner=True); golv(); studio(nokkel=1.2, kantlys=1.2, fyll=0.4); hell(O, 0.0)
    d = (G['EKS'] + G['U_KANT'] + G['RUTE_D']) / 1000.0
    k = Vector((G['XR0'] / 1000.0, G['YT'] / 1000.0 - d, G['AKSE_H'] / 1000.0))
    kamera(k + Vector((-0.085, -0.215, 0.135)), k + Vector((0.052, 0.018, 0.004)), 105, fstop=16.0, fokus=k + Vector((0.035, 0.012, 0.0))); rendre('r-kant')

def vis_kveld():
    """Lampa i bruk: einaste lyskjelde, på ei mørk matt plate med eit kvitt ark under ruta."""
    oppsett(eksponering=0.6); lampe(styrke=1.0); golv((0.045, 0.040, 0.036), 0.55)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.045, -0.105, 0.0004))
    a4 = bpy.context.object; a4.scale = (0.297, 0.210, 0.0008); a4.rotation_euler = (0, 0, math.radians(-7)); a4.data.materials.append(matt('papir', (0.80, 0.79, 0.76), 0.85))
    flate('fyll', (0.3, -2.2, 0.6), (0.0, 0.0, 0.15), 2.0, 2.0, 0.35, (0.75, 0.82, 1.0))
    kamera((-1.287, -2.018, 0.469), (-0.099, 0.04, 0.135), 120, fstop=11.0, fokus=(-0.05, -0.05, 0.2)); rendre('r-kveld')

def vis_sprengt():
    """Delane trekte frå kvarandre, svevande i svart utan golv, med ruta ved 35°. Same avstandar som i studiosida (eksporter_studio.py)."""
    oppsett(); O = lampe(liner=False, styrke=0.8); studio(nokkel=3.4, kantlys=3.4, fyll=2.4)
    flate('nedanfraa', (-0.5, -1.6, -0.35), (0.0, 0.0, -0.05), 1.6, 1.0, 5.0, (1.0, 0.97, 0.94))          # så ballasten og botnloket syner
    opp = Vector((0.0, -math.sin(_t), math.cos(_t))); x = Vector((1, 0, 0)); z = Vector((0, 0, 1))
    F = {'08': 0.085 * opp, '10': -0.035 * opp, '09': -0.055 * opp, '06': -0.085 * opp, '13': -0.100 * opp, 'E': -0.125 * opp, '11': -0.055 * x,
         '12': -0.030 * z, '01': -0.060 * z, 'leidning': -0.060 * z, '03': -0.115 * z, '02': -0.170 * z}
    for i, v in F.items():
        if i in O: O[i].matrix_world = Matrix.Translation(v) @ O[i].matrix_world
    bpy.context.view_layer.update()
    kamera((-1.40, -2.19, 0.33), (-0.105, 0.035, 0.105), 100, fstop=16.0, fokus=(-0.05, -0.05, 0.2)); rendre('r-sprengt')

skaansam()
for v in VIS:
    globals()['vis_' + v]()
