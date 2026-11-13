# -*- coding: utf-8 -*-
# KOPI av modell/byggjesett/rendre_blender.py (13.11.2026). Endra berre: kvar scenene blir lesne frå (--scener),
# kvar bileta blir skrivne (--ut), materiala «print», «led» og «opal» for trykte og kjøpte delar, og «flat» på filmstykke.
# Materiale, lys, verd, kamera, prøvetal og utdata er dei same som i originalen.
"""rendre_blender.py · studiorendrar av kitbash-lampene med oppsettet til byggjesettet (Cycles, Blender 5.1, hovudlaust)

Les ei scenefil (skriven av rendre.py: STL-filer, materiale, plassering og kamera per scene) og rendrar kvar scene
til <ut>/<scene>.png. Scener med «delbank» blir rendra ortografisk med gjennomsiktig bakgrunn og fast tal pikslar per mm,
med storleiken i <ut>/<scene>.json.

  blender.exe -b -P rendre_blender.py -- --scener <mappe>/scener.json [--ut <mappe>/render] [scene ...] [--prove]

--prove gjev små, raske bilete. Prosessen går på lågaste prioritet med fire trådar på kjerne 2 til 7 (CPU, ikkje GPU),
så lyden ikkje hakkar. Køyr helst gjennom rendre.py.
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
ARG = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
PROVE = '--prove' in ARG


def _val(flagg, standard=None):
    return ARG[ARG.index(flagg) + 1] if flagg in ARG else standard


SCENEFIL = os.path.abspath(_val('--scener', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scener.json')))
HER = os.path.dirname(SCENEFIL)                                         # stiane i scenefila er relative til henne
UT = os.path.abspath(_val('--ut', os.path.join(HER, 'render')))
SCENER = json.load(open(SCENEFIL, encoding='utf-8'))
_hopp = {i + 1 for i, a in enumerate(ARG) if a in ('--scener', '--ut')}
VALDE = [a for i, a in enumerate(ARG) if not a.startswith('--') and i not in _hopp] or list(SCENER)


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
    # Prismefilmen: tynn, klar plast med ein blank, sølvaktig glans. Han er sett som ein miks av gjennomsiktig
    # (lyset går rett gjennom ein så tynn film) og ei blank flate. Prisma (om lag 0,05 mm) er for små til å synast.
    # Lyset bak arket i den første utgåva gjorde han heilt kvit, så scena «arket» har ikkje baklys lenger.
    m = bpy.data.materials.new('film'); m.use_nodes = True; nt = m.node_tree
    p = nt.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (0.02, 0.02, 0.022, 1.0); p.inputs['Roughness'].default_value = 0.06
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mix = nt.nodes.new('ShaderNodeMixShader')
    mix.inputs['Fac'].default_value = 0.3
    nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(p.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], nt.nodes['Material Output'].inputs['Surface'])
    M['film'] = m
    M['golv'], _ = _principled('golv', (0.014, 0.014, 0.016), 0.0, 0.6)
    # --- lagt til for kitbash: trykte og kjøpte delar
    # Trykte delar: matt, varm raudbrun, fargen Iver brukte på fot og bjelke i konsept/film/cad/render.py (0,20 0,028 0,03).
    M['print'], _ = _principled('print', (0.13, 0.024, 0.018), 0.0, 0.62)
    # Kjøpt LED-flate: lyser svakt varmt, så ho les som tend utan å lyse opp studioet
    m, p = _principled('led', (1.0, 0.86, 0.62), 0.0, 0.5)
    p.inputs['Emission Color'].default_value = (1.0, 0.74, 0.42, 1.0); p.inputs['Emission Strength'].default_value = 2.5
    M['led'] = m
    M['opal'], _ = _principled('opal', (0.86, 0.85, 0.82), 0.0, 0.35)       # kjøpt opal plate eller spreiar
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


def _kort(namn, pos, mal, storleik, styrke):
    """Lysande flate utanfor biletet (refleks). Synest i speglingar, der eit lys berre gjev ein liten flekk."""
    h = storleik / 2
    me = bpy.data.meshes.new(namn); me.from_pydata([(-h, -h, 0), (h, -h, 0), (h, h, 0), (-h, h, 0)], [], [(0, 1, 2, 3)]); me.update()
    m = bpy.data.materials.new(namn); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Strength'].default_value = styrke
    ut = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(e.outputs[0], ut.inputs['Surface'])
    me.materials.append(m)
    ob = bpy.data.objects.new(namn, me); bpy.context.collection.objects.link(ob)
    ob.location = pos; _peik(ob, mal); ob.visible_camera = False
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


def _film_rutenett(ob, boy=26.0):
    """Byt arket (eit ekstrudert rektangel med hjørnepunkt berre) med eit tett rutenett i same omriss, lagt på ein svak
    boge (boy grader over breidda), så filmen les som film. Flikane (1,6 mm) fell bort, dei synest ikkje i denne målestokken."""
    me = ob.data
    xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys) - 0.0016
    n = 64
    rho = (x1 - x0) / math.radians(boy); xc = (x0 + x1) / 2
    def punkt(i, y):
        a = (x0 + (x1 - x0) * i / n - xc) / rho
        return (xc + rho * math.sin(a), y, -rho * (1 - math.cos(a)))
    vx = [punkt(i, y) for y in (y0, y1) for i in range(n + 1)]
    fl = [(i, i + 1, n + 2 + i, n + 1 + i) for i in range(n)]
    ny = bpy.data.meshes.new('film'); ny.from_pydata(vx, [], fl); ny.update()
    for pg in ny.polygons:
        pg.use_smooth = True
    ny.materials.append(me.materials[0])
    ob.data = ny


def _verd(s):
    """Studioverd: mørk under, lys over. Blanke flater og glas får noko å spegle, også utan bakgrunn i biletet."""
    verd = bpy.data.worlds.new('verd'); s.world = verd; verd.use_nodes = True
    nt = verd.node_tree
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])                # i verda er dette retninga til strålen
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -1.0; mr.inputs['From Max'].default_value = 1.0
    nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
    cr = nt.nodes.new('ShaderNodeValToRGB'); nt.links.new(mr.outputs['Result'], cr.inputs['Fac'])
    e = cr.color_ramp.elements
    e[0].position, e[0].color = 0.0, (0.004, 0.004, 0.005, 1.0)
    e[1].position, e[1].color = 1.0, (0.30, 0.30, 0.31, 1.0)
    midt = e.new(0.5); midt.color = (0.05, 0.05, 0.055, 1.0)
    nt.links.new(cr.outputs['Color'], nt.nodes['Background'].inputs['Color'])


def rendre(namn, sc):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    bank = sc.get('delbank')                                            # delbanken: ortografisk, gjennomsiktig, fast målestokk
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
    if bank:
        s.render.film_transparent = True
        s.cycles.film_transparent_glass = True
        s.render.image_settings.color_mode = 'RGBA'
    _verd(s)
    M = materiale()
    objekt = [_importer(o['fil'], o['M'], M[o['mat']]) for o in sc['objekt']]
    lo, hi = Vector(sc['lo']) * 0.001, Vector(sc['hi']) * 0.001
    midt = (lo + hi) / 2; R = (hi - lo).length / 2
    y_bak = hi.y + 0.25 * R + 0.05
    if not bank:
        bg = _bakgrunn(lo.z, y_bak); bg.data.materials.append(M['golv'])
    k = sc['kamera']
    mal = Vector(k['mal']) * 0.001
    az, el = math.radians(k['azimut']), math.radians(k['elevasjon'])
    retn = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    cd = bpy.data.cameras.new('kamera'); cd.lens = k.get('lens', 70); cd.sensor_width = 36
    cam = bpy.data.objects.new('kamera', cd); bpy.context.collection.objects.link(cam); s.camera = cam
    meta = None
    if bank:
        # Ortografisk: biletet blir akkurat så stort som delen, med px_per_mm pikslar per mm, så alle delane har same målestokk.
        cd.type = 'ORTHO'
        for ob, o in zip(objekt, sc['objekt']):
            if o.get('del_') == 'P08' and not o.get('flat'):            # filmen er mjuk: ein svak bøy får han til å lese som film
                _film_rutenett(ob)                                      # (eit filmstykke som sit flatt i ei lampe, har «flat»)
        cam.rotation_euler = (-retn).to_track_quat('-Z', 'Y').to_euler()
        bpy.context.view_layer.update()
        R3 = cam.matrix_world.to_3x3()
        hogre, opp, fram = R3.col[0].normalized(), R3.col[1].normalized(), -R3.col[2].normalized()
        us, ws, fs = [], [], []
        dg = bpy.context.evaluated_depsgraph_get()
        for ob in objekt:
            oe = ob.evaluated_get(dg); me = oe.to_mesh(); mw = oe.matrix_world
            for vx in me.vertices:
                p = mw @ vx.co
                us.append(p.dot(hogre)); ws.append(p.dot(opp)); fs.append(p.dot(fram))
            oe.to_mesh_clear()
        ppmm = bank['px_per_mm'] / (3 if PROVE else 1)
        px_m = 0.001 / ppmm; marg = 12
        W = math.ceil((max(us) - min(us)) / px_m) + 2 * marg
        H = math.ceil((max(ws) - min(ws)) / px_m) + 2 * marg
        s.render.resolution_x, s.render.resolution_y = W, H
        cd.ortho_scale = max(W, H) * px_m
        cam.location = hogre * (max(us) + min(us)) / 2 + opp * (max(ws) + min(ws)) / 2 + fram * (min(fs) - 1.0)
        cd.clip_start = 0.01; cd.clip_end = (max(fs) - min(fs)) + 2.0
        meta = dict(scene=namn, px_per_mm=ppmm, w=W, h=H, marg=marg, azimut=k['azimut'], elevasjon=k['elevasjon'],
                    breidd_mm=round((max(us) - min(us)) * 1000, 1), hogd_mm=round((max(ws) - min(ws)) * 1000, 1))
    else:
        halv_v = math.atan((36.0 * H / W / 2) / cd.lens)            # halve vertikale synsvinkelen
        cam.location = mal + retn * (k.get('faktor', 1.0) * R / math.sin(halv_v)); _peik(cam, mal)
    d = max(R, 0.08)
    _lys('hovudlys', mal + Vector((-1.6, -1.8, 2.2)) * d * 2.2, mal, 1.4 * d * 2, 120 * (d / 0.3) ** 2)
    _lys('fyll', mal + Vector((2.2, -0.9, 0.9)) * d * 2.2, mal, 2.0 * d * 2, 28 * (d / 0.3) ** 2)
    kant = mal + Vector((0.4, 2.4, 1.8)) * d * 2.2
    if not bank:
        kant.y = min(kant.y, y_bak - 0.03)                              # framfor bakveggen, elles skuggar veggen lyset
    _lys('kant', kant, mal, 1.0 * d * 2, 85 * (d / 0.3) ** 2, (1.0, 0.93, 0.85))
    for o in sc['objekt']:
        if o.get('del_') == 'P08':
            # Refleks: ei stor lysflate der arket speglar kameraretninga, så filmen får ein blank glans som skiftar over bøyen
            n = (Matrix(o['M']).to_3x3() @ Vector((0, 0, 1))).normalized()
            dv = -retn
            if dv.dot(n) > 0:
                n = -n
            r = dv - 2 * dv.dot(n) * n
            _kort('refleks', mal + r * 1.2, mal, 1.2, 70.0)
    if sc.get('baklys'):                                                # lys gjennom arket bakfrå
        bak = Vector((mal.x, min(hi.y + 0.25, y_bak - 0.03), mal.z))
        _lys('baklys', bak, mal, 0.9 * d * 2, 30 * (d / 0.3) ** 2, (1.0, 0.95, 0.88))
    os.makedirs(UT, exist_ok=True)
    s.render.filepath = os.path.join(UT, namn + ('-prove' if PROVE else '') + '.png')
    bpy.ops.render.render(write_still=True)
    if meta:
        json.dump(meta, open(os.path.join(UT, namn + ('-prove' if PROVE else '') + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('RENDRA', s.render.filepath, flush=True)


if __name__ == '__main__':
    for namn in VALDE:
        rendre(namn, SCENER[namn])
