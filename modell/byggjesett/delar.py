# -*- coding: utf-8 -*-
"""delar.py · byggjesettet frå overheadprojektoren (truleg 3M 2000) som parametriske 3D-delar

Måla er anten dokumenterte (delelista, typeskilt) eller anslått frå fotoa Iver tok 13.11.2026. Tre målarar mælte
fotoa kvar for seg med ulik målestokk. Den eine fekk fresnelvindauget til 198 mm mot 285 mm i delelista, så han vart
utelaten. Verdiane er snittet av dei to andre, og usikkerheita er minst halve skilnaden mellom dei.
Alle mål i mm, Z opp. Kvar del er ei liste med underdelar (namn, mesh, materiale), så rendrar kan gje kvar sitt materiale.

  python delar.py      skriv stl/, byggjesett.glb (delane utlagde), projektoren.glb (samla) og scener.json

TRYGGLEIK: straumforsyninga i basen (kort, kondensatorar, IEC-inntak) går på NETTSPENNING. Ho skal aldri koplast
til straum att og aldri brukast i ein skissemodell. Fresnelspegelen og glaslinsene må aldri liggje i sol:
dei samlar sollyset og kan tenne papir.
"""
import os, json, math
import numpy as np
import trimesh
from shapely.geometry import Polygon, box as sboks

HER = os.path.dirname(os.path.abspath(__file__))
D, F, T, A = 'deleliste', 'anslått frå foto', 'typeskilt', 'antaking'

# mål: (verdi i mm, ± mm, kjelde)
DIMS = {
    'P01': dict(namn='arm', profil_lengd=(240, 12, F), profil_breidd=(43, 6, F), profil_tjukk=(26, 3, F), vegg=(1.5, 0.5, A),
                kappe_lengd=(98, 10, F), kappe_breidd=(40, 5, F), kappe_hogd=(51, 8, F),
                tapp_d=(6, 1.5, F), tapp_lengd=(15, 3, F), laas_lengd=(12, 4, F)),
    'P02': dict(namn='hengsel', lengd=(84, 12, F), breidd=(66, 12, F), hogd=(55, 15, F), fjoer_lengd=(35, 8, F), fjoer_d=(5.5, 2, F)),
    'P03': dict(namn='hovud', lengd=(140, 15, F), breidd=(78, 10, F), hogd=(80, 20, F), fas=(18, 5, F),
                vifte=(60, 1, T + ' Sunon GM1206PTV3-A'), lager_d=(70, 10, F)),
    'P04': dict(namn='base', lengd=(285, 12, F), breidd=(99, 12, F), hogd=(28, 10, F)),
    'P05': dict(namn='fresnelspegel', vindauge=(285, 0, D), brennvidd=(187.1, 0, D), ramme_ytre=(295, 4, F),
                skraa=(37, 5, F), tjukk=(3.5, 2, F)),
    'P06': dict(namn='glaslinse', d=(41, 4, F), hogd=(14, 6, F)),
    'P07': dict(namn='projeksjonslinse', fatning_d=(77, 5, F), fatning_hogd=(28, 10, F), linse_d=(40, 4, F),
                spak_lengd=(17, 5, F), brennvidd=(280, 10, 'research/13, utrekna')),
    'P08': dict(namn='prismeark', breidd=(306, 40, F), hogd=(535, 70, F), tjukk=(0.2, 0.15, A),
                flik_breidd=(10, 3, F), flik_hogd=(1.6, 1, F), flik_tal=(2, 0, F)),
    'P09': dict(namn='fsx_paere', d=(20, 0, D), lengd=(77, 0, D)),
}
NETTSPENNING = ('P04', 'kort', 'kondensator', 'trafo', 'iec', 'brytar')


def v(pid, k):
    return float(DIMS[pid][k][0])


# ---------------------------------------------------------------- hjelparar
def _rr(b, h, r=0.0):
    p = sboks(-b / 2, -h / 2, b / 2, h / 2)
    return p.buffer(-r).buffer(r, resolution=8) if r > 0 else p


def _ekstr(poly, h, z0=0.0):
    m = trimesh.creation.extrude_polygon(poly, h)
    m.apply_translation((0, 0, z0))
    return m


def _syl(r, h, z0=0.0, n=64):
    m = trimesh.creation.cylinder(radius=r, height=h, sections=n)
    m.apply_translation((0, 0, z0 + h / 2))
    return m


def _boks(lx, ly, lz, c=(0, 0, 0)):
    m = trimesh.creation.box((lx, ly, lz))
    m.apply_translation(c)
    return m


def _rot(m, akse, grader, punkt=(0, 0, 0)):
    m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(grader), akse, punkt))
    return m


def _flytt(m, d):
    m.apply_translation(d)
    return m


def _minus(a, *b):
    return trimesh.boolean.difference([a, *b], engine='manifold')


def _pluss(*ms):
    return trimesh.boolean.union(list(ms), engine='manifold')


UVW_TIL_YZX = np.array([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float)   # (u, v, w) -> (x=w, y=u, z=v)


def _langs_x(poly, lengd, x0):
    """Ekstruder eit tverrsnitt i (y, z) langs +x frå x0."""
    m = trimesh.creation.extrude_polygon(poly, lengd)
    m.apply_transform(UVW_TIL_YZX)
    m.apply_translation((x0, 0, 0))
    return m


# ---------------------------------------------------------------- delane
def arm():
    """P01. Origo i hengselaksen (langs y). Armen går langs +x, den breie sida av profilen står loddrett (z)."""
    L, b, t, w = v('P01', 'profil_lengd'), v('P01', 'profil_breidd'), v('P01', 'profil_tjukk'), v('P01', 'vegg')
    kl, kb, kh = v('P01', 'kappe_lengd'), v('P01', 'kappe_breidd'), v('P01', 'kappe_hogd')
    x0 = 12.0
    profil = _rr(t, b, 2.0).difference(_rr(t - 2 * w, b - 2 * w, 0.8))
    rør = _langs_x(profil, L, x0)
    xk = x0 + L - 20.0                                   # kappa er tredd 20 mm inn over profilen
    blokk = _langs_x(_rr(kb, kh, 4.0), kl - kh / 2, xk)
    knoke = _rot(_syl(kh / 2, kb, -kb / 2), (1, 0, 0), 90)
    knoke = _flytt(knoke, (xk + kl - kh / 2, 0, 0))
    kappe = _pluss(blokk, knoke)
    xa = xk + kl - kh / 2                                # aksen hovudet dreier om
    tapp = _flytt(_rot(_syl(v('P01', 'tapp_d') / 2, v('P01', 'tapp_lengd') + 2, -2), (1, 0, 0), 90), (xa, -kb / 2, 0))
    laas = _boks(v('P01', 'laas_lengd'), 6, 2.0, (xk + 25, 0, kh / 2 + 1.0))
    return [('profil', rør, 'aluminium'), ('kappe', kappe, 'plast_grå'), ('tapp', tapp, 'stål'), ('laas', laas, 'stål')], \
        dict(hovudakse=(xa, kb / 2, 0.0))


def hengsel():
    """P02. Origo i hengselaksen, same som armen. Festeplata går mot -x."""
    L, B, H = v('P02', 'lengd'), v('P02', 'breidd'), v('P02', 'hogd')
    t = v('P01', 'profil_tjukk'); s = 2.0
    zb = -H / 2
    plate = _boks(L, B, s, (-L / 2 + 22, 0, zb + s / 2))
    for y in (-B / 2 + 9, B / 2 - 9):                    # avlange skruehol i øyra
        hol = _boks(14, 5, s + 2, (-L + 32, y, zb + s / 2))
        plate = _minus(plate, hol)
    sider = [_boks(46, s, H - s, (-4, y, zb + s + (H - s) / 2)) for y in (-(t / 2 + 1 + s / 2), t / 2 + 1 + s / 2)]
    kanal = _pluss(*sider, _boks(46, t + 2 + 2 * s, s, (-4, 0, zb + s * 1.5)))
    bolt = _rot(_syl(3.0, B * 0.75, -B * 0.375), (1, 0, 0), 90)
    mutter = _flytt(_rot(_syl(5.5, 4.5, 0, n=6), (1, 0, 0), -90), (0, B * 0.375 - 1, 0))
    spak = _rot(_boks(52, t + 8, 1.8, (-14, 0, H / 2 + 2)), (0, 1, 0), -12, (-40, 0, H / 2))
    fjoer = []
    fl, fd = v('P02', 'fjoer_lengd'), v('P02', 'fjoer_d')
    n = 9
    for i in range(n):
        try:
            ring = trimesh.creation.torus(major_radius=fd / 2, minor_radius=0.55, major_sections=24, minor_sections=8)
        except Exception:
            ring = _syl(fd / 2, 1.1, -0.55, n=24)
        ring = _rot(ring, (0, 1, 0), 90)
        fjoer.append(_flytt(ring, (-L + 30 + i * fl / (n - 1), B / 2 - 5, zb + s + fd / 2 + 0.6)))
    fjoer = trimesh.util.concatenate(fjoer)
    return [('plate', plate, 'stål'), ('kanal', kanal, 'stål'), ('bolt', bolt, 'stål'), ('mutter', mutter, 'stål'),
            ('spak', spak, 'stål'), ('fjoer', fjoer, 'stål')], {}


def hovud():
    """P03. Origo midt på lagerskiva på endeflata mot armen. Huset går langs +x, den opne flata vender mot +z."""
    L, B, H, fas = v('P03', 'lengd'), v('P03', 'breidd'), v('P03', 'hogd'), v('P03', 'fas')
    plan = Polygon([(0, -B / 2), (L - fas, -B / 2), (L, -B / 2 + fas), (L, B / 2 - fas), (L - fas, B / 2), (0, B / 2)])
    ytre = _ekstr(plan, H, -H / 2)
    indre = _ekstr(plan.buffer(-1.2, join_style=2), H, -H / 2 + 1.2)
    hus = _minus(ytre, indre)
    vf = v('P03', 'vifte')
    ramme = _minus(_boks(vf, vf, 25, (L * 0.55, 0, -H / 2 + 1.2 + 12.5)), _flytt(_syl(vf / 2 - 2, 29, -H / 2 - 1), (L * 0.55, 0, 0)))
    nav = _flytt(_syl(15, 24, -12), (L * 0.55, 0, -H / 2 + 1.2 + 12.5))
    blad = []
    for i in range(7):
        bl = _boks(vf / 2 - 17, 11, 1.2, (15 + (vf / 2 - 17) / 2, 0, 0))
        bl = _rot(bl, (1, 0, 0), 28)
        bl = _rot(bl, (0, 0, 1), i * 360 / 7)
        blad.append(_flytt(bl, (L * 0.55, 0, -H / 2 + 1.2 + 12.5)))
    vifte = trimesh.util.concatenate([ramme, nav] + blad)
    merke = _flytt(_syl(11, 0.4, 12), (L * 0.55, 0, -H / 2 + 1.2 + 12.5))
    sokkel = _boks(32, 36, 38, (8 + 16, -B / 2 + 1.2 + 18 + 2, -H / 2 + 1.2 + 19))
    lager = _rot(_syl(v('P03', 'lager_d') / 2, 4.0, 0), (0, 1, 0), -90)
    nav2 = _rot(_syl(9, 7, 0), (0, 1, 0), -90)
    return [('hus', hus, 'stål_svart'), ('vifte', vifte, 'plast_svart'), ('vifte_merke', merke, 'kopar'),
            ('sokkel', sokkel, 'stål'), ('lager', lager, 'kopar'), ('lager_nav', nav2, 'stål')], {}


def base():
    """P04. Origo midt på botnen. NETTSPENNING: kortet, kondensatorane, trafoen og IEC-inntaket skal ikkje brukast."""
    L, B, H = v('P04', 'lengd'), v('P04', 'breidd'), v('P04', 'hogd')
    w = 2.5
    brett = _minus(_ekstr(_rr(L, B, 6), H), _ekstr(_rr(L - 2 * w, B - 2 * w, 4), H, w))
    kort = _boks(150, 60, 1.6, (-L / 2 + 30 + 75, B / 2 - w - 32, w + 8))
    trafo = _boks(30, 26, 24, (-L / 2 + 30 + 120, B / 2 - w - 30, w + 9.6 + 12))
    kond = trimesh.util.concatenate([_flytt(_syl(8, 24, w + 9.6), (-L / 2 + 30 + x, B / 2 - w - 22, 0)) for x in (40, 75)])
    kjol = _boks(150, 2, 30, (-L / 2 + 30 + 75, B / 2 - w - 64, w + 15))
    iec = _boks(27, 22, 24, (L / 2 - w - 20, -B / 2 + w + 18, w + 12))
    brytar = _boks(21, 15, 13, (L / 2 - w - 20, -B / 2 + w + 44, w + 6.5))
    return [('brett', brett, 'plast_grå'), ('kort', kort, 'kretskort'), ('trafo', trafo, 'plast_svart'),
            ('kondensator', kond, 'plast_svart'), ('kjoleplate', kjol, 'aluminium'), ('iec', iec, 'plast_svart'),
            ('brytar', brytar, 'plast_svart')], {}


def _aattekant(s, fas):
    h = s / 2
    return Polygon([(-h + fas, -h), (h - fas, -h), (h, -h + fas), (h, h - fas), (h - fas, h), (-h + fas, h), (-h, h - fas), (-h, -h + fas)])


def fresnel():
    """P05. Origo midt på plata, botnen i z = 0. Rillene (konsentriske) sit på oversida."""
    S, R, fas, t = v('P05', 'vindauge'), v('P05', 'ramme_ytre'), v('P05', 'skraa'), v('P05', 'tjukk')
    vind = _aattekant(S, fas)
    ramme = _ekstr(_rr(R, R).difference(vind), t)
    plate = _ekstr(_aattekant(S + 2, fas), t - 0.6, 0.0)
    return [('ramme', ramme, 'plast_svart'), ('plate', plate, 'fresnel')], {}


def glaslinse():
    """P06. Plankonveks linse, flat side ned, origo midt på den flate sida."""
    r, h, e = v('P06', 'd') / 2, v('P06', 'hogd'), 2.5
    s = h - e; Rc = (r * r + s * s) / (2 * s)
    rr = np.linspace(r, 0, 40)
    prof = [(0, 0), (r, 0), (r, e)] + [(x, e + math.sqrt(Rc * Rc - x * x) - (Rc - s)) for x in rr[1:]]
    m = trimesh.creation.revolve(np.array(prof), sections=96)
    return [('linse', m, 'glas')], {}


def projeksjonslinse():
    """P07. Origo midt under fatninga. Flensen øvst, glaset søkk i røyret, spaken radielt ut under flensen."""
    D_, H, dl, sp = v('P07', 'fatning_d'), v('P07', 'fatning_hogd'), v('P07', 'linse_d'), v('P07', 'spak_lengd')
    skjort = _syl(30, H - 4, 0)
    flens = _syl(D_ / 2, 4, H - 4)
    for i in range(6):
        a = 2 * math.pi * i / 6
        flens = _minus(flens, _flytt(_syl(1.5, 6, H - 5), (34 * math.cos(a), 34 * math.sin(a), 0)))
    røyr = _minus(_syl(23.5, 7, H), _syl(dl / 2 + 0.5, 9, H - 1))
    ring = _minus(_syl(dl / 2 + 0.5, 1.5, H + 3.5), _syl(dl / 2 - 2, 3, H + 3))
    fatning = _pluss(skjort, flens, røyr, ring)
    glas = trimesh.creation.revolve(np.array([(0, -2.2), (dl / 2, -0.4), (dl / 2, 0.4), (0, 2.2)]), sections=96)
    glas.apply_translation((0, 0, H + 1.5))
    lengd = D_ / 2 + sp
    stong = _rot(_syl(2.5, lengd - 28, 28), (0, 1, 0), 90)
    stong.apply_translation((0, 0, H - 9))
    hylse = _rot(_syl(4, 12, lengd - 12), (0, 1, 0), 90)
    hylse.apply_translation((0, 0, H - 9))
    return [('fatning', fatning, 'plast_svart'), ('glas', glas, 'glas'), ('spak', stong, 'stål'), ('hylse', hylse, 'gummi_svart')], {}


def prismeark():
    """P08. Berre geometri, ikkje optikk (optikken ligg i konsept/vindauge/). Arket ligg i xy-planet med langsida
    langs y og flikane på kortsida ved +y, med midten 10 % og 72 % av breidda frå venstre kant. Origo midt på nedre kortside."""
    B, H, t = v('P08', 'breidd'), v('P08', 'hogd'), max(v('P08', 'tjukk'), 0.2)
    fb, fh = v('P08', 'flik_breidd'), v('P08', 'flik_hogd')
    omriss = sboks(-B / 2, 0, B / 2, H)
    for fx in (0.10, 0.72):
        xc = -B / 2 + fx * B
        omriss = omriss.union(sboks(xc - fb / 2, H - 0.01, xc + fb / 2, H + fh))
    return [('ark', _ekstr(omriss, t), 'film')], {}


def fsx_paere():
    """P09. FSX-pære, 400 W, GY9.5, Ø 20 x 77 mm (delelista). Origo midt under sokkelen."""
    d, L = v('P09', 'd'), v('P09', 'lengd')
    r = d / 2
    prof = [(0, 22), (5, 22), (r, 28), (r, L - r)] + [(r * math.cos(a), L - r + r * math.sin(a)) for a in np.linspace(0, math.pi / 2, 12)[1:]]
    kolbe = trimesh.creation.revolve(np.array(prof), sections=64)
    sokkel = _boks(d, 12, 22, (0, 0, 11))
    pinnar = trimesh.util.concatenate([_flytt(_syl(1.0, 6, -6), (x, 0, 0)) for x in (-4.75, 4.75)])
    return [('kolbe', kolbe, 'glas'), ('sokkel', sokkel, 'keramikk'), ('pinnar', pinnar, 'stål')], {}


DELAR = {'P01': arm, 'P02': hengsel, 'P03': hovud, 'P04': base, 'P05': fresnel, 'P06': glaslinse,
         'P07': projeksjonslinse, 'P08': prismeark, 'P09': fsx_paere}


def del_(pid):
    """Underdelane til ein del: [(namn, mesh, materiale)], og ekstra punkt (dict)."""
    return DELAR[pid]()


# ---------------------------------------------------------------- scener
def _M(*steg):
    M = np.eye(4)
    for s in steg:
        M = s @ M
    return M


def _R(akse, grader):
    return trimesh.transformations.rotation_matrix(np.radians(grader), akse)


def _Tr(x, y, z):
    return trimesh.transformations.translation_matrix((x, y, z))


def scene_samla():
    """Projektoren slik delane kan ha sete: fresnelspegelen på bordet, basen langs kanten, armen loddrett frå hengselet
    og hovudet ut over plata, om lag 2f = 374 mm over spegelen. Rekonstruksjon frå delane, ikkje målt."""
    B4 = v('P04', 'breidd'); H4 = v('P04', 'hogd'); R5 = v('P05', 'ramme_ytre')
    yb = -R5 / 2 - B4 / 2 - 2
    zh = H4 + v('P02', 'hogd') / 2                         # hengselaksen over golvet
    opp = _R((0, 1, 0), -90)                               # armen frå +x til +z
    ut = [('P05', np.eye(4)), ('P04', _Tr(0, yb, 0)),
          ('P02', _M(_R((0, 1, 0), -90), _Tr(0, yb + 6, zh))),
          ('P01', _M(opp, _Tr(0, yb + 6, zh)))]
    _, ekstra = arm()
    xa, ya, za = ekstra['hovudakse']
    pa = opp @ np.array([xa, ya, za, 1.0])
    hovud_M = _M(_R((0, 0, 1), 90), _Tr(pa[0], yb + 6 + pa[1] + 2, zh + pa[2]))
    ut.append(('P03', hovud_M))
    ende = hovud_M @ np.array([v('P03', 'lengd') * 0.78, 0, -v('P03', 'hogd') / 2, 1.0])
    ut.append(('P07', _M(_R((1, 0, 0), 180), _Tr(ende[0], ende[1], ende[2] - 2))))
    return ut


def scene_utlagd():
    plass = {'P05': (0, 0), 'P04': (0, -260), 'P01': (-120, 260), 'P02': (-260, 260), 'P03': (240, 260),
             'P06': (260, 60), 'P07': (260, -60), 'P09': (260, -170), 'P08': (-560, -270)}
    ut = []
    for pid, (x, y) in plass.items():
        M = _Tr(x, y, 0)
        if pid == 'P01':
            M = _Tr(x, y, v('P01', 'kappe_hogd') / 2)
        if pid == 'P02':
            M = _Tr(x, y, v('P02', 'hogd') / 2)
        if pid == 'P03':
            M = _Tr(x, y, v('P03', 'hogd') / 2)
        if pid == 'P09':
            M = _M(_R((0, 1, 0), 90), _Tr(x - 38, y, 10))
        ut.append((pid, M))
    return ut


SCENER = {      # faktor: avstand i høve til det som akkurat får med heile kula rundt motivet (1,0)
    'projektoren-samla': dict(fn=scene_samla, kamera=dict(azimut=-38, elevasjon=22, lens=50, faktor=0.82), prover=48),
    'fresnelplata': dict(fn=lambda: [('P05', np.eye(4))], kamera=dict(azimut=-22, elevasjon=36, lens=60, faktor=0.78), prover=48),
    'linsene': dict(fn=lambda: [('P07', np.eye(4)), ('P06', _Tr(80, 18, 0)), ('P09', _M(_R((0, 1, 0), 90), _Tr(-110, 10, 10)))],
                    kamera=dict(azimut=-18, elevasjon=32, lens=90, faktor=0.85), prover=64),
    'arket': dict(fn=lambda: [('P08', _M(_R((1, 0, 0), 90 - 9), _Tr(0, 0, 0)))],
                  kamera=dict(azimut=-24, elevasjon=10, lens=50, faktor=0.80), prover=48, baklys=True),
}


def _scenedata(namn, sc, stl_av):
    objekt, alle = [], []
    for pid, M in sc['fn']():
        for under, mesh, mat in DELAR[pid]()[0]:
            fil = stl_av[(pid, under)]
            objekt.append(dict(fil=fil, mat=mat, M=M.tolist(), del_=pid, under=under))
            m = mesh.copy(); m.apply_transform(M); alle.append(m)
    lo, hi = trimesh.util.concatenate(alle).bounds
    midt = (lo + hi) / 2
    R = np.linalg.norm(hi - lo) / 2
    k = sc['kamera']
    return dict(objekt=objekt, lo=lo.tolist(), hi=hi.tolist(), prover=sc['prover'], storleik=[1600, 1000], baklys=sc.get('baklys', False),
                kamera=dict(mal=midt.tolist(), azimut=k['azimut'], elevasjon=k['elevasjon'], lens=k['lens'], faktor=k['faktor']))


FARGAR = {'aluminium': (200, 202, 205), 'plast_grå': (130, 132, 135), 'stål': (185, 185, 188), 'stål_svart': (25, 25, 28),
          'plast_svart': (20, 20, 22), 'kopar': (215, 140, 105), 'kretskort': (20, 90, 40), 'fresnel': (225, 228, 232),
          'glas': (210, 235, 225), 'film': (215, 225, 238), 'gummi_svart': (15, 15, 15), 'keramikk': (235, 232, 225)}


def _glb(par, fil):
    sc = trimesh.Scene()
    for pid, M in par:
        for under, mesh, mat in DELAR[pid]()[0]:
            m = mesh.copy(); m.apply_transform(M)
            m.visual.face_colors = (*FARGAR.get(mat, (180, 180, 180)), 255)
            sc.add_geometry(m, node_name=f'{pid}_{DIMS[pid]["namn"]}_{under}')
    sc.export(fil)


if __name__ == '__main__':
    os.makedirs(os.path.join(HER, 'stl'), exist_ok=True)
    stl_av, rapport = {}, []
    for pid, fn in DELAR.items():
        for under, mesh, mat in fn()[0]:
            fil = f'stl/{pid}_{DIMS[pid]["namn"]}_{under}.stl'
            mesh.export(os.path.join(HER, fil))
            stl_av[(pid, under)] = fil
            rapport.append(f'{fil:44s} {mat:12s} tett={mesh.is_watertight!s:5s} mål={np.round(mesh.extents, 1).tolist()}')
    print('\n'.join(rapport))
    _glb(scene_utlagd(), os.path.join(HER, 'byggjesett.glb'))
    _glb(scene_samla(), os.path.join(HER, 'projektoren.glb'))
    data = {namn: _scenedata(namn, sc, stl_av) for namn, sc in SCENER.items()}
    json.dump(data, open(os.path.join(HER, 'scener.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump({pid: {k: list(x) if isinstance(x, tuple) else x for k, x in d.items()} for pid, d in DIMS.items()},
              open(os.path.join(HER, 'maal.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('skrive byggjesett.glb, projektoren.glb, scener.json, maal.json')
