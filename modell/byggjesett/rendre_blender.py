# -*- coding: utf-8 -*-
"""rendre_blender.py · studiorendrar av byggjesettet med Cycles (Blender 5.1, hovudlaust)

Les scener.json (skrive av delar.py: STL-filer, materiale, plassering og kamera per scene) og rendrar kvar scene
til render/<scene>.png. Glas, blankt metall og fresnelringar er ekte i Cycles; fargespalting i prismearket er ikkje med.

  blender.exe -b -P rendre_blender.py -- [scene ...] [--prove]

--prove gjev små, raske bilete. Prosessen går på lågaste prioritet med fire trådar på kjerne 2 til 7 (CPU, ikkje GPU),
så lyden ikkje hakkar.
"""
import bpy, json, os, sys, math
from mathutils import Matrix, Vector


def _skaansam():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.GetCurrentProcess()
        k.SetPriorityClass(h, 0x40)              # IDLE_PRIORITY_CLASS
        k.SetProcessAffinityMask(h, 0xFC)
    except Exception:
        pass


_skaansam()
HER = os.path.dirname(os.path.abspath(__file__))
UT = os.path.join(HER, 'render')
ARG = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
PROVE = '--prove' in ARG
SCENER = json.load(open(os.path.join(HER, 'scener.json'), encoding='utf-8'))
VALDE = [a for a in ARG if not a.startswith('--')] or list(SCENER)


# ---------------------------------------------------------------- materiale
def _principled(namn, farge, metall=0.0, ruheit=0.5, trans=0.0, ior=1.5, coat=0.0):
    m = bpy.data.materials.new(namn); m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*farge, 1.0)
    p.inputs['Metallic'].default_value = metall
    p.inputs['Roughness'].default_value = ruheit
    p.inputs['Transmission Weight'].default_value = trans
    p.inputs['IOR'].default_value = ior
    p.inputs['Coat Weight'].default_value = coat
    return m, p


def _bump(m, p, hogd, styrke, avstand):
    nt = m.node_tree
    b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = styrke; b.inputs['Distance'].default_value = avstand
    nt.links.new(hogd, b.inputs['Height']); nt.links.new(b.outputs['Normal'], p.inputs['Normal'])


def _ringar(m, p, steg):
    """Konsentriske riller rundt origo i objektet (fresnelplata ligg med midten i origo)."""
    nt = m.node_tree
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sep.inputs[0])
    xy = nt.nodes.new('ShaderNodeCombineXYZ'); nt.links.new(sep.outputs['X'], xy.inputs['X']); nt.links.new(sep.outputs['Y'], xy.inputs['Y'])
    r = nt.nodes.new('ShaderNodeVectorMath'); r.operation = 'LENGTH'; nt.links.new(xy.outputs[0], r.inputs[0])
    k = nt.nodes.new('ShaderNodeMath'); k.operation = 'MULTIPLY'; k.inputs[1].default_value = 2 * math.pi / steg
    nt.links.new(r.outputs['Value'], k.inputs[0])
    s = nt.nodes.new('ShaderNodeMath'); s.operation = 'SINE'; nt.links.new(k.outputs[0], s.inputs[0])
    _bump(m, p, s.outputs[0], 0.5, 0.0003)


def _liner(m, p, steg):
    """Lineære prisme i arket, langs objektets x-akse."""
    nt = m.node_tree
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sep.inputs[0])
    k = nt.nodes.new('ShaderNodeMath'); k.operation = 'MULTIPLY'; k.inputs[1].default_value = 2 * math.pi / steg
    nt.links.new(sep.outputs['Y'], k.inputs[0])
    s = nt.nodes.new('ShaderNodeMath'); s.operation = 'SINE'; nt.links.new(k.outputs[0], s.inputs[0])
    _bump(m, p, s.outputs[0], 0.25, 0.0001)


def materiale():
    M = {}
    M['aluminium'], _ = _principled('aluminium', (0.80, 0.81, 0.82), 1.0, 0.30)
    M['stål_svart'], _ = _principled('stål_svart', (0.018, 0.018, 0.02), 0.0, 0.38, coat=0.3)
    M['stål'], _ = _principled('stål', (0.72, 0.72, 0.73), 1.0, 0.22)
    M['plast_grå'], _ = _principled('plast_grå', (0.34, 0.35, 0.36), 0.0, 0.48)
    M['plast_svart'], _ = _principled('plast_svart', (0.012, 0.012, 0.014), 0.0, 0.42)
    M['kopar'], _ = _principled('kopar', (0.95, 0.60, 0.46), 1.0, 0.28)
    M['kretskort'], _ = _principled('kretskort', (0.03, 0.17, 0.06), 0.0, 0.45, coat=0.4)
    M['gummi_svart'], _ = _principled('gummi_svart', (0.02, 0.02, 0.022), 0.0, 0.7)
    M['keramikk'], _ = _principled('keramikk', (0.86, 0.84, 0.80), 0.0, 0.45)
    m, p = _principled('fresnel', (0.92, 0.93, 0.95), 1.0, 0.12); _ringar(m, p, 0.0018); M['fresnel'] = m
    M['glas'], _ = _principled('glas', (0.96, 1.0, 0.98), 0.0, 0.0, trans=1.0, ior=1.52)
    m, p = _principled('film', (0.96, 0.98, 1.0), 0.0, 0.32, trans=1.0, ior=1.58); _liner(m, p, 0.0006); M['film'] = m
    M['golv'], _ = _principled('golv', (0.014, 0.014, 0.016), 0.0, 0.6)
    return M


# ---------------------------------------------------------------- scene
def _peik(ob, mal):
    d = Vector(mal) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def _lys(namn, pos, mal, storleik, styrke, farge=(1.0, 1.0, 1.0)):
    ld = bpy.data.lights.new(namn, 'AREA'); ld.size = storleik; ld.energy = styrke; ld.color = farge
    ob = bpy.data.objects.new(namn, ld); bpy.context.collection.objects.link(ob)
    ob.location = pos; _peik(ob, mal)
    return ob


def _bakgrunn(z0, y_bak, breidd=6.0, radius=0.7, hogd=4.0, framme=6.0):
    """Hol bakgrunn: golv som går over i ein vegg med ein boge, utan horisont."""
    profil = [(-framme, z0), (y_bak, z0)]
    for i in range(1, 17):
        a = i / 16 * math.pi / 2
        profil.append((y_bak + radius * math.sin(a), z0 + radius * (1 - math.cos(a))))
    profil.append((y_bak + radius, z0 + hogd))
    v = [(x, y, z) for x in (-breidd, breidd) for (y, z) in profil]
    n = len(profil)
    f = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
    me = bpy.data.meshes.new('bakgrunn'); me.from_pydata(v, [], f); me.update()
    for pg in me.polygons:
        pg.use_smooth = True
    ob = bpy.data.objects.new('bakgrunn', me); bpy.context.collection.objects.link(ob)
    return ob


def _importer(fil, M, mat):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.stl_import(filepath=os.path.join(HER, fil), global_scale=1.0)
    ob = bpy.context.selected_objects[0]
    ob.data.transform(Matrix.Scale(0.001, 4)); ob.data.update()        # mm til m i sjølve meshen, så objektskalaen er 1
    m = Matrix(M); m.translation = m.translation * 0.001
    ob.matrix_world = m
    ob.data.materials.append(mat)
    bpy.context.view_layer.objects.active = ob
    try:
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(32))
    except Exception:
        pass
    return ob


def rendre(namn, sc):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    s.cycles.device = 'CPU'
    s.render.threads_mode = 'FIXED'; s.render.threads = 4
    s.cycles.samples = 24 if PROVE else sc.get('prover', 192)
    s.cycles.use_denoising = True
    s.cycles.max_bounces = 10; s.cycles.transmission_bounces = 10; s.cycles.glossy_bounces = 6
    W, H = sc.get('storleik', [1600, 1000])
    s.render.resolution_x, s.render.resolution_y = (W // 3, H // 3) if PROVE else (W, H)
    s.render.resolution_percentage = 100
    s.view_settings.view_transform = 'AgX'
    s.view_settings.exposure = -0.6
    s.render.image_settings.file_format = 'PNG'
    verd = bpy.data.worlds.new('verd'); s.world = verd; verd.use_nodes = True
    verd.node_tree.nodes['Background'].inputs['Color'].default_value = (0.004, 0.004, 0.005, 1.0)
    M = materiale()
    for o in sc['objekt']:
        _importer(o['fil'], o['M'], M[o['mat']])
    lo, hi = Vector(sc['lo']) * 0.001, Vector(sc['hi']) * 0.001
    midt = (lo + hi) / 2; R = (hi - lo).length / 2
    y_bak = hi.y + 0.25 * R + 0.05
    bg = _bakgrunn(lo.z, y_bak); bg.data.materials.append(M['golv'])
    k = sc['kamera']
    mal = Vector(k['mal']) * 0.001
    az, el = math.radians(k['azimut']), math.radians(k['elevasjon'])
    retn = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    cd = bpy.data.cameras.new('kamera'); cd.lens = k.get('lens', 70); cd.sensor_width = 36
    cam = bpy.data.objects.new('kamera', cd); bpy.context.collection.objects.link(cam)
    halv_v = math.atan((36.0 * H / W / 2) / cd.lens)                # halve vertikale synsvinkelen
    cam.location = mal + retn * (k.get('faktor', 1.0) * R / math.sin(halv_v)); _peik(cam, mal); s.camera = cam
    d = max(R, 0.08)
    _lys('hovudlys', mal + Vector((-1.6, -1.8, 2.2)) * d * 2.2, mal, 1.4 * d * 2, 120 * (d / 0.3) ** 2)
    _lys('fyll', mal + Vector((2.2, -0.9, 0.9)) * d * 2.2, mal, 2.0 * d * 2, 28 * (d / 0.3) ** 2)
    kant = mal + Vector((0.4, 2.4, 1.8)) * d * 2.2
    kant.y = min(kant.y, y_bak - 0.03)                                  # framfor bakveggen, elles skuggar veggen lyset
    _lys('kant', kant, mal, 1.0 * d * 2, 85 * (d / 0.3) ** 2, (1.0, 0.93, 0.85))
    if sc.get('baklys'):                                                # lys gjennom arket bakfrå
        bak = Vector((mal.x, min(hi.y + 0.25, y_bak - 0.03), mal.z))
        _lys('baklys', bak, mal, 0.9 * d * 2, 30 * (d / 0.3) ** 2, (1.0, 0.95, 0.88))
    os.makedirs(UT, exist_ok=True)
    s.render.filepath = os.path.join(UT, namn + ('-prove' if PROVE else '') + '.png')
    bpy.ops.render.render(write_still=True)
    print('RENDRA', s.render.filepath, flush=True)


for namn in VALDE:
    rendre(namn, SCENER[namn])
