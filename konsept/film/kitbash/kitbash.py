# -*- coding: utf-8 -*-
"""
kitbash.py  ·  lamper sette saman av delane i byggjesettet (modell/byggjesett/) og trykte overgangsdelar

Delane frå settet blir lesne, ikkje endra: STL-filene og måla ligg i modell/byggjesett/. Dei trykte delane blir teikna
her (CadQuery) og skrivne til stl/. Kvar lampe blir ei scene i same format som settet sine, og blir rendra med settet sitt
eige Blender-oppsett (render_kitbash.py), ortografisk, med 4 pikslar per mm, så alt står i same målestokk som delbanken.

  python kitbash.py          skriv stl/ og scener.json
  python kitbash.py ark      set rendrane saman til kitbash.png

Origo er midt i foten på bordflata. x mot høgre, y bort frå brukaren, z opp. Måla på delane frå settet er anslag frå foto.
"""
import os, sys, math, json
import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
SETT = os.path.abspath(os.path.join(HER, '..', '..', '..', 'modell', 'byggjesett'))
sys.path.insert(0, SETT)
sys.path.insert(0, os.path.join(HER, '..', 'cad'))
STL = os.path.join(HER, 'stl')

def Rx(g): c, s = math.cos(math.radians(g)), math.sin(math.radians(g)); return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1.0]])
def Ry(g): c, s = math.cos(math.radians(g)), math.sin(math.radians(g)); return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1.0]])
def Rz(g): c, s = math.cos(math.radians(g)), math.sin(math.radians(g)); return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1.0]])
def T(x, y, z): m = np.eye(4); m[:3, 3] = (x, y, z); return m
def pkt(M, p): return (M @ np.array([p[0], p[1], p[2], 1.0]))[:3]

# ------------------------------------------------------------------ stativet: trykt fot, hengselet P02 og armen P01
FOT_D, FOT_H = 158.0, 16.0
AKSE = np.array([20.0, 0.0, FOT_H + 2.0 + 62.0])            # hengselaksen: festeplata rekk 62 mm ned frå aksen
M_ARM = T(*AKSE) @ Rz(-90) @ Ry(-90)                         # armen opp, tappen mot venstre (-x)
M_HENGSEL = T(*AKSE) @ Rz(90) @ Ry(-90)                      # hengselet snudd, så festeplata står bak armen
TAPP_INN = pkt(M_ARM, (304.5, -20.0, 0.0))                   # der tappen går ut av kappa
TAPP_UT = pkt(M_ARM, (304.5, -35.0, 0.0))
LEDD_H = TAPP_INN[2]                                         # høgda på dreieaksen i toppen av armen

def _stl_av(pid, under):
    for f in os.listdir(os.path.join(SETT, 'stl')):
        if f.startswith(pid + '_') and f.endswith('_' + under + '.stl'):
            return os.path.join(SETT, 'stl', f)
    raise KeyError((pid, under))

def fraa_settet(pid, M, berre=None, utan=(), del_=None):
    import delar as D
    ut = []
    for under, mesh, mat in D.del_(pid)[0]:
        if (berre and under not in berre) or under in utan: continue
        ut.append(dict(fil=_stl_av(pid, under), mat=mat, M=np.asarray(M).tolist(), del_=del_ or pid, under=under, _mesh=(mesh, np.asarray(M))))
    return ut

_TRYKT = {}
def trykt(namn, form, mat='trykt'):
    """Ein del teikna her, alt på plass. Blir skriven til stl/ éin gong."""
    import cadquery as cq
    from cadquery import exporters
    import trimesh
    os.makedirs(STL, exist_ok=True)
    fil = os.path.join(STL, namn + '.stl')
    if namn not in _TRYKT:
        exporters.export(form, fil, tolerance=0.03, angularTolerance=0.12); _TRYKT[namn] = trimesh.load(fil)
    return dict(fil=fil, mat=mat, M=np.eye(4).tolist(), del_='ny', under=namn, _mesh=(_TRYKT[namn], np.eye(4)))

def stativ():
    import cadquery as cq
    fot = cq.Workplane('XY').circle(FOT_D / 2).extrude(FOT_H).faces('>Z').edges().fillet(2.0)
    # sokkel bak hengselet: festeplata blir skrudd mot framsida av han
    sokkel = cq.Workplane('XY').box(70, 20, AKSE[2] + 24 - FOT_H, centered=(True, False, False)).translate((AKSE[0], AKSE[1] + 27.5, FOT_H))
    sokkel = sokkel.edges('|Z').fillet(4.0)
    return [trykt('stativ_fot', fot.union(sokkel))] + fraa_settet('P02', M_HENGSEL) + fraa_settet('P01', M_ARM)

# ------------------------------------------------------------------ K1: ruta på armen

def k1():
    import cadquery as cq
    import lampe as L
    D = {d[0]: d for d in L.delar(35.0)}
    dx = TAPP_UT[0] - 3.0 - L.X_BJ1; dy = TAPP_INN[1] - L.YB; dz = LEDD_H - L.AKSE_H
    fl = lambda f: f.translate((dx, dy, dz))
    kopling = cq.Workplane('YZ', origin=(TAPP_UT[0] - 3.0, 0, 0)).center(TAPP_INN[1], LEDD_H).circle(16).extrude(TAPP_INN[0] - TAPP_UT[0] + 3.0)
    ut = stativ()
    ut += [trykt('k1_bjelke', fl(D['07'][2])), trykt('k1_lok', fl(D['08'][2])), trykt('k1_kopling', kopling),
           trykt('k1_lysleiar', fl(D['09'][2]), 'glas'), trykt('k1_ark', fl(D['10'][2]), 'film'),
           trykt('k1_skruar', fl(D['E'][2]), 'stål')]
    return ut

# ------------------------------------------------------------------ K2: vindauget med glaslinsa

def k2():
    import cadquery as cq
    opp = 8.0                                   # røyret peikar mot veggen, 8° opp
    d = np.array([0.0, math.cos(math.radians(opp)), math.sin(math.radians(opp))])
    c = np.array([TAPP_UT[0] - 34.0, TAPP_INN[1], LEDD_H])              # midt i røyret, til venstre for kappa
    L_ROYR, D_Y, D_I = 120.0, 60.0, 50.0
    # røyret blir teikna langs z og lagt på plass: z -> d
    M = T(*c) @ Rx(-(90.0 - opp))
    def plass(f): return f.rotate((0, 0, 0), (1, 0, 0), -(90.0 - opp)).translate(tuple(c))
    royr = cq.Workplane('XY').circle(D_Y / 2).circle(D_I / 2).extrude(L_ROYR).translate((0, 0, -L_ROYR / 2))
    leppe = cq.Workplane('XY').circle(D_Y / 2).circle(19.0).extrude(3.0).translate((0, 0, L_ROYR / 2 - 3.0))        # held linsa
    bak = cq.Workplane('XY').circle(D_Y / 2).extrude(4.0).translate((0, 0, -L_ROYR / 2 - 4.0))
    ribber = None
    for i in range(5):
        r = cq.Workplane('XY').circle(D_Y / 2 + 3).circle(D_Y / 2 - 0.1).extrude(2.0).translate((0, 0, -L_ROYR / 2 + 4 + i * 7.0))
        ribber = r if ribber is None else ribber.union(r)
    spor = cq.Workplane('XY').box(54, 2.0, 40, centered=(True, True, False)).translate((0, 0, L_ROYR / 2 - 14 - 46 - 1)).rotate((0, 0, 0), (1, 0, 0), 0)
    hus = royr.union(leppe).union(bak).union(ribber)
    feste = cq.Workplane('YZ', origin=(TAPP_UT[0] - 4.0, 0, 0)).center(TAPP_INN[1], LEDD_H).circle(16).extrude(TAPP_INN[0] - TAPP_UT[0] + 4.0)
    # maska: ei tynn plate i eit spor 46 mm bak linsa, med ein flik ein kan ta i
    maske = cq.Workplane('XY').box(46, 66, 1.0, centered=(True, False, True)).translate((0, -43, L_ROYR / 2 - 14 - 46))
    ut = stativ() + [trykt('k2_hus', plass(hus)), trykt('k2_feste', feste), trykt('k2_maske', plass(maske), 'plast_svart')]
    # glaslinsa P06: flat side mot maska, kvelven ut mot veggen
    ut += fraa_settet('P06', M @ T(0, 0, L_ROYR / 2 - 14.0 - 3.0))
    return ut

# ------------------------------------------------------------------ K3: fresnelspegelen på armen

def k3():
    import cadquery as cq
    hell = 25.0
    t = math.radians(hell)
    s = np.array([0.0, -math.cos(t), -math.sin(t)]); n = np.array([0.0, -math.sin(t), math.cos(t)])     # ut i plata, og oversida
    xh = TAPP_UT[0] - 3.0                                   # høgre ende av bjelken
    Lb = 310.0
    akse = np.array([xh - Lb / 2, TAPP_INN[1], LEDD_H])
    bjelke = cq.Workplane('YZ', origin=(xh - Lb, 0, 0)).center(TAPP_INN[1], LEDD_H).circle(16).extrude(Lb)
    kopling = cq.Workplane('YZ', origin=(xh, 0, 0)).center(TAPP_INN[1], LEDD_H).circle(16).extrude(TAPP_INN[0] - xh)
    # plata: P05 ligg i xy med rillene opp. Her skal spegelsida ned mot bordet, og plata skal gå ut frå bjelken langs s
    senter = akse + s * (147.5 + 12.0)
    R = np.eye(4); R[:3, 0] = (1, 0, 0); R[:3, 1] = -s; R[:3, 2] = -n      # lokal y -> -s, lokal z (spegelsida) -> ned
    M5 = T(*senter) @ R
    # dioden: ein kopp 120 mm under midten av plata, festa med ein strut frå bjelken
    kp = senter - n * 120.0
    kopp = cq.Workplane('XY').circle(17).circle(13).extrude(26).translate((0, 0, -26))
    botn = cq.Workplane('XY').circle(17).extrude(3).translate((0, 0, -29))
    kopp = kopp.union(botn)
    vz = math.degrees(math.atan2(n[1], n[2]))               # koppen opnar seg langs n
    kopp = kopp.rotate((0, 0, 0), (1, 0, 0), -vz).translate(tuple(kp))
    a0 = akse + np.array([-Lb / 2 + 10.0, 0, 0]); a1 = kp + np.array([-17.0, 0, 0]) - n * 14.0
    v = a1 - a0; l = float(np.linalg.norm(v))
    strut = cq.Workplane('XY').circle(4.5).extrude(l)
    ax = np.cross([0, 0, 1], v / l); vk = math.degrees(math.acos(float(v[2] / l)))
    strut = strut.rotate((0, 0, 0), tuple(ax), vk).translate(tuple(a0))
    tverr = cq.Workplane('YZ', origin=(a1[0], 0, 0)).center(a1[1], a1[2]).circle(4.5).extrude(kp[0] - a1[0])
    led = cq.Workplane('XY').circle(11).extrude(1.5).translate((0, 0, -25)).rotate((0, 0, 0), (1, 0, 0), -vz).translate(tuple(kp))
    ut = stativ() + [trykt('k3_bjelke', bjelke), trykt('k3_kopling', kopling), trykt('k3_kopp', kopp.union(strut).union(tverr)),
                     trykt('k3_led', led, 'led')]
    ut += fraa_settet('P05', M5)
    return ut

# ------------------------------------------------------------------ K4: projektoren ombygd (brett, hengsel, arm og hovud frå settet)

def k4():
    import cadquery as cq
    import delar as D
    H4 = 28.0; zh = H4 + 27.5
    opp = Ry(-90)
    P = np.array([0.0, 6.0, zh])
    M1 = T(*P) @ opp
    pa = pkt(M1, (304.5, 20.0, 0.0))
    vipp = -140.0                                            # hovudet dreidd om si eiga lengdeakse: opninga ned og mot feltet til venstre
    MH = T(pa[0], pa[1] + 2.0, pa[2]) @ Rz(90) @ Rx(vipp)
    ut = fraa_settet('P04', np.eye(4), berre=('brett',)) + fraa_settet('P02', M1) + fraa_settet('P01', M1)
    ut += fraa_settet('P03', MH, berre=('hus', 'lager', 'lager_nav'))
    # trykt innsats: ramme over opninga (lokalt +z) som held ein bit av arket, og ein berar til LED-stripa inni
    ramme = cq.Workplane('XY').box(136, 74, 5, centered=(False, True, False)).translate((2, 0, 40)) \
        .cut(cq.Workplane('XY').box(120, 58, 7, centered=(False, True, False)).translate((10, 0, 39)))
    ark = cq.Workplane('XY').box(124, 62, 0.4, centered=(False, True, False)).translate((8, 0, 42))
    led = cq.Workplane('XY').box(110, 8, 2, centered=(False, True, False)).translate((15, 0, 8))
    def plass(f):
        return f.rotate((0, 0, 0), (1, 0, 0), vipp).rotate((0, 0, 0), (0, 0, 1), 90).translate((pa[0], pa[1] + 2.0, pa[2]))
    ut += [trykt('k4_ramme', plass(ramme)), trykt('k4_ark', plass(ark), 'film'), trykt('k4_led', plass(led), 'led')]
    return ut

LAMPER = {
    'k1': dict(fn=k1, namn='Ruta på armen', tekst=['FRÅ SETTET: P01 ARM · P02 HENGSEL · P08 ARK', 'TRYKT: FOT MED SOKKEL · BJELKE · LOK · KOPLING',
                                                      'ELLES: LYSLEIARPLATE · LED-STRIPE', 'ARMEN KAN LEGGJAST NED I HENGSELET']),
    'k2': dict(fn=k2, namn='Vindauget med glaslinsa', tekst=['FRÅ SETTET: P01 · P02 · P06', 'TRYKT: FOT · RØYR · MASKE',
                                                                'ELLES: ÉI DIODE', 'MASKA 46 MM BAK LINSA']),
    'k3': dict(fn=k3, namn='Spegelen på armen', tekst=['FRÅ SETTET: P01 · P02 · P05 FRESNELSPEGEL', 'TRYKT: FOT · BJELKE · KOPP MED STRUT',
                                                          'ELLES: ÉI DIODE I KOPPEN', 'ALDRI I SOL']),
    'k4': dict(fn=k4, namn='Projektoren ombygd', tekst=['FRÅ SETTET: P04 BRETT · P02 · P01 · P03 HOVUD', 'TRYKT: RAMME · BERAR TIL STRIPA',
                                                           'ELLES: LED-STRIPE · EIN BIT AV ARKET', 'STRAUMFORSYNINGA ER TEKEN UT']),
}

def scene(k):
    import trimesh
    ob = LAMPER[k]['fn']()
    alle = []
    for o in ob:
        m, M = o.pop('_mesh'); mm = m.copy(); mm.apply_transform(M); alle.append(mm)
        if o['del_'] == 'P08': o['del_'] = 'ark'
    lo, hi = trimesh.util.concatenate(alle).bounds
    return dict(objekt=ob, lo=lo.tolist(), hi=hi.tolist(), prover=40, storleik=[1600, 1000], baklys=False,
                kamera=dict(mal=((lo + hi) / 2).tolist(), azimut=-35, elevasjon=28, lens=50, faktor=1.0), delbank=dict(px_per_mm=4))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    if sys.argv[1:2] == ['ark']:
        from PIL import Image, ImageDraw, ImageFont
        sys.path.insert(0, os.path.join(HER, '..', '..', 'lysskisse'))
        os.environ.setdefault('LYSSKISSE_POLGE', '0')
        import lysskisse as ls
        W, H = 2254, 1594; S = 2.0
        ark = Image.new('RGB', (W, H), (0, 0, 0)); dr = ImageDraw.Draw(ark)
        mono = lambda px: ImageFont.truetype('consola.ttf', px)
        graa, kvit = (150, 150, 150), (236, 232, 224)
        dr.text((88, 46), 'GK5 · NORTHERN · BYGGJESETT', font=mono(19), fill=graa)
        t = 'KITBASH'; dr.text(((W - dr.textlength(t, font=mono(19))) / 2, 46), t, font=mono(19), fill=kvit)
        t = 'IVER R. FINNE · 13.11.2026'; dr.text((W - 88 - dr.textlength(t, font=mono(19)), 46), t, font=mono(19), fill=graa)
        dr.line([88, 88, W - 88, 88], fill=(70, 70, 70), width=2)
        dr.text((88, 118), 'Fire lamper av same byggjesett.', font=ls._font(86), fill=kvit)
        meta = {k: json.load(open(os.path.join(HER, 'render', k + '.json'), encoding='utf-8')) for k in LAMPER}
        ims = {k: Image.open(os.path.join(HER, 'render', k + '.png')).convert('RGBA') for k in LAMPER}
        mx = max(m['hogd_mm'] for m in meta.values()); bx = sum(m['breidd_mm'] for m in meta.values())
        sk = min((H - 250 - 330) / mx, (W - 176 - 3 * 50) / bx)                     # px på arket per mm
        x = 88; y_botn = 230 + (H - 100 - 230 - int(mx * sk) - 150) // 2 + int(mx * sk)
        for k, L_ in LAMPER.items():
            m = meta[k]; im = ims[k]
            f = sk / m['px_per_mm']
            im = im.resize((max(1, int(im.width * f)), max(1, int(im.height * f))), Image.LANCZOS)
            cw = int(m['breidd_mm'] * sk)
            ark.paste(im, (x - int(m['marg'] * f), y_botn - im.height + int(m['marg'] * f)), im)
            dr.text((x, y_botn + 26), L_['namn'].upper(), font=mono(21), fill=kvit)
            for i, tx in enumerate(L_['tekst']):
                dr.text((x, y_botn + 26 + 30 * (i + 1)), tx, font=mono(17), fill=kvit if i == 3 else graa)
            x += cw + 50
        lx = int(100 * sk); ys = 168
        dr.line([W - 88 - lx, ys, W - 88, ys], fill=kvit, width=2)
        for xx in (W - 88 - lx, W - 88): dr.line([xx, ys - 8, xx, ys + 8], fill=kvit, width=2)
        dr.text((W - 88 - lx, ys + 16), '100 MM', font=mono(17), fill=kvit)
        dr.line([88, H - 84, W - 88, H - 84], fill=(70, 70, 70), width=2)
        dr.text((88, H - 66), 'Raudt er trykt. Resten er delar frå settet, med måla frå foto. Rendra med same oppsett som delbanken, 4 pikslar per mm.', font=mono(17), fill=graa)
        t = 'Ingenting er bygd eller målt enno.'; dr.text((W - 88 - dr.textlength(t, font=mono(17)), H - 66), t, font=mono(17), fill=graa)
        ark.save(os.path.join(HER, 'kitbash.png')); print('kitbash.png', ark.size, 'målestokk %.2f px/mm' % sk)
    else:
        ut = {}
        for k in LAMPER:
            ut[k] = scene(k); lo, hi = ut[k]['lo'], ut[k]['hi']
            print('%s %-26s %2d objekt  %4.0f x %4.0f x %4.0f mm' % (k, LAMPER[k]['namn'], len(ut[k]['objekt']), hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]), flush=True)
        json.dump(ut, open(os.path.join(HER, 'scener.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('dreieaksen i toppen av armen står %.0f mm over bordet' % LEDD_H)
