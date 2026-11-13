# -*- coding: utf-8 -*-
"""kit.py  ·  delane i byggjesettet, trykte delar og kjøpte delar som éi samling

Ei lampe er ei liste med plasserte delar (`Del`). Alt er i millimeter med Z opp. Lampa sitt system:
origo midt i foten på bordflata (z = 0 er bordet), x mot høgre, y bort frå brukaren (mot veggen).

  sett('P01', M)          ein del frå byggjesettet, lesen frå modell/byggjesett/delar.py (måla blir ikkje kopierte hit)
  film(breidd, hogd, M)   eit stykke klipt av prismearket P08
  trykt(namn, mesh, M)    ein del du teiknar sjølv (trimesh eller CadQuery), materiale «print»
  kjopt(namn, mesh, ...)  ein kjøpt del med oppgjeven masse: LED, ballast, kjøleplate, skruar

Plassering er ei stiv transformering: plass(pos, rot), eller T() @ Rz() @ Ry() @ Rx(), om() for eit ledd, og
T(*pos) @ retta(n) for det som skal peike ein stad (speglnormal() gjev retninga ein spegel må ha).
Usikkerheita i måla ligg i usikker() og klaring(). Køyr `python kit.py` for å sjå grensesnittmåla.

TRYGGLEIK: P04 (basen med straumforsyninga, nettspenning) kan ikkje hentast herifrå. P09 (halogenpæra) heller ikkje:
ein LED erstattar ho. Fresnelspegelen og linsene må aldri stå i sol. Trykt PLA mjuknar ved 55 til 60 °C.
"""
import os, sys, json, math, copy, importlib.util
sys.dont_write_bytecode = True                       # ikkje skriv .pyc i mappene vi berre les frå
if os.path.dirname(os.path.abspath(__file__)) not in sys.path: sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import miljo                                         # høgst fire trådar og låg prioritet, før numpy
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box as _sboks
from shapely import affinity as _aff

# Det `from kit import *` gjev. HER, ROT og SETT er ikkje med, så dei ikkje skriv over dine eigne.
__all__ = ['T', 'Rx', 'Ry', 'Rz', 'om', 'plass', 'retta', 'speglnormal', 'pkt', 'retn', 'usikker', 'klaring', 'GRENSESNITT', 'FILM_TRYGG', 'Del', 'sett', 'film',
           'trykt', 'kjopt', 'ekstruder', 'boks', 'sylinder', 'royr', 'hylse', 'plate', 'vinkel', 'skal', 'kopp', 'dreielekam', 'minus',
           'pluss', 'snitt', 'flytta', 'fraa_cq', 'led_skive', 'led_stripe', 'alle_under', 'grenser', 'finn', 'sprengd', 'med_staalarm', 'filnamn', 'DIMS', 'MAAL',
           'PRINTER', 'MJUKNAR', 'FORBODNE']

HER = os.path.dirname(os.path.abspath(__file__))
ROT = os.path.normpath(os.path.join(HER, '..', '..', '..'))
SETT = os.path.join(ROT, 'modell', 'byggjesett')


def _last(namn, fil):
    """Last ein modul frå ei fil utan å endre sys.path for andre."""
    if namn in sys.modules:
        return sys.modules[namn]
    spec = importlib.util.spec_from_file_location(namn, fil)
    m = importlib.util.module_from_spec(spec)
    sys.modules[namn] = m
    spec.loader.exec_module(m)
    return m


D = _last('byggjesett_delar', os.path.join(SETT, 'delar.py'))      # delane og DIMS, urørte
DIMS = D.DIMS
MAAL = json.load(open(os.path.join(SETT, 'maal.json'), encoding='utf-8'))

FORBODNE = {'P04': 'P04 er straumforsyninga (230 V nettspenning). Ho skal aldri brukast, heller ikkje som form i ei lampe.',
            'P09': 'P09 er den gamle halogenpæra (400 W). Ho er ikkje i bruk: ein LED erstattar ho.'}
PRINTER = (256.0, 256.0, 256.0)                      # Bambu Lab P1S, byggjevolum i mm
MJUKNAR = {'PLA': 57.0, 'PETG': 78.0}                # °C der plasten mjuknar (PLA 55 til 60: kjent frå kjelde; PETG om lag 75 til 80)

# ------------------------------------------------------------------ stive transformeringar (mm, grader)

def T(x=0.0, y=0.0, z=0.0):
    m = np.eye(4); m[:3, 3] = (x, y, z); return m

def _rot(akse, g):
    return trimesh.transformations.rotation_matrix(math.radians(g), akse)

def Rx(g): return _rot((1, 0, 0), g)
def Ry(g): return _rot((0, 1, 0), g)
def Rz(g): return _rot((0, 0, 1), g)

def om(akse, grader, punkt=(0, 0, 0)):
    """Dreiing om ein akse gjennom eit punkt (eit ledd). Bruk: M_ny = om(akse, vinkel, punkt) @ M."""
    return trimesh.transformations.rotation_matrix(math.radians(grader), akse, punkt)

def plass(pos=(0, 0, 0), rot=(0, 0, 0)):
    """Stiv transformering: først dreiing om x, så y, så z (grader), så flytting til pos (mm).
    rot kan òg vere ei ferdig 3x3- eller 4x4-matrise."""
    if np.ndim(rot) == 2:
        R = np.eye(4); R[:3, :3] = np.asarray(rot, float)[:3, :3]
    else:
        R = Rz(rot[2]) @ Ry(rot[1]) @ Rx(rot[0])
    return T(*pos) @ R

def retta(z_til, x_til=None):
    """Dreiing (4x4) som tek +z i delen til retninga z_til, og +x så nær x_til som råd. Til det som skal peike ein stad:
    spegelsida på fresnelplata (+z), lysflata på ein LED (+z), prismesida på filmen (+z). Bruk: T(*pos) @ retta(n)."""
    w = np.asarray(z_til, float); w = w / np.linalg.norm(w)
    x0 = np.array((1.0, 0.0, 0.0) if x_til is None else x_til, float)
    u = x0 - (x0 @ w) * w
    if np.linalg.norm(u) < 1e-6:
        u = np.array([0.0, 1.0, 0.0]) - w[1] * w
    u = u / np.linalg.norm(u)
    M = np.eye(4); M[:3, 0], M[:3, 1], M[:3, 2] = u, np.cross(w, u), w
    return M

def speglnormal(c, kjelde, maal):
    """Normalen ein spegel i punktet c må ha for å sende lyset frå `kjelde` mot `maal` (tre punkt i same system)."""
    c = np.asarray(c, float)
    a = np.asarray(kjelde, float) - c; b = np.asarray(maal, float) - c
    n = a / np.linalg.norm(a) + b / np.linalg.norm(b)
    return n / np.linalg.norm(n)

def pkt(M, p):
    """Punktet p (mm) gjennom transformeringa M."""
    return (np.asarray(M, float) @ np.array([p[0], p[1], p[2], 1.0]))[:3]

def retn(M, v):
    """Retninga v gjennom transformeringa M (berre dreiinga)."""
    return np.asarray(M, float)[:3, :3] @ np.asarray(v, float)

# ------------------------------------------------------------------ usikkerheit i måla (maal.json)

GRENSESNITT = {     # måla som avgjer om eit spor, ei klemme eller ein kopp passar
    'P01': dict(profil_breidd='breisida av armprofilen', profil_tjukk='smalsida av armprofilen', profil_lengd='lengda på profilen',
                vegg='godstjukn i profilen', kappe_breidd='kappa på tvers', kappe_hogd='kappa i høgda', tapp_d='tappen hovudet dreidde på',
                tapp_lengd='kor langt tappen stikk ut'),
    'P02': dict(lengd='hengsel, lengd', breidd='hengsel, breidd', hogd='hengsel, høgd'),
    'P03': dict(lengd='hovudet, lengd', breidd='hovudet, breidd', hogd='hovudet, høgd', lager_d='lagerskiva'),
    'P05': dict(ramme_ytre='ytterkant av ramma rundt spegelen', tjukk='tjukn på plate og ramme', vindauge='spegelflata'),
    'P06': dict(d='diameter på glaslinsa', hogd='høgd på glaslinsa'),
    'P07': dict(fatning_d='flensen på fatninga', fatning_hogd='høgd på fatninga', linse_d='glaset'),
    'P08': dict(breidd='arket, kortside', hogd='arket, langside', tjukk='tjukn på arket'),
}
FILM_TRYGG = (250.0, 440.0)     # minste storleik arket kan ha (ANTAKING frå fotoa: mellom 250 x 440 og 306 x 535)


def usikker(pid, maal):
    """Eitt mål frå maal.json: dict(verdi, pm, lo, hi, kjelde), alt i mm."""
    verdi, pm, kjelde = MAAL[pid][maal]
    return dict(verdi=float(verdi), pm=float(pm), lo=float(verdi) - float(pm), hi=float(verdi) + float(pm), kjelde=kjelde)


def klaring(pid, maal, luft=0.3):
    """Kor stort eit spor eller ei klemme må vere for å tole usikkerheita i eit mål.
    opning: sporet som tek delen òg om han er størst (verdi + pm + luft).
    slark: kor mykje delen sleng i det sporet om han er minst (2 pm + luft): det må ei klemskrue, ein kile eller
    ein mjuk innsats ta opp. luft er trykkjeklaringa (0,3 mm for PETG og PLA på P1S, ANTAKING)."""
    u = usikker(pid, maal)
    return dict(nominell=u['verdi'], pm=u['pm'], opning=u['hi'] + luft, slark=2 * u['pm'] + luft, kjelde=u['kjelde'],
                raad=('mål delen med skyvelære før du trykkjer' if u['pm'] > 1.0 else 'kan trykkjast etter målet'))

# ------------------------------------------------------------------ delen

class Del:
    """Ein plassert del. under: [(undernamn, mesh i delen sitt eige system, materiale)]. M: frå delen til lampa (mm)."""
    def __init__(s, namn, slag, under, M=None, pid=None, vekt_g=None, spreng=None, plast='PETG', print_R=None,
                 watt=None, lyser=False, anker=None, merknad='', flat_film=True, omgjevnad=False):
        s.namn = namn; s.slag = slag                      # slag: 'sett' | 'print' | 'kjopt'
        s.under = list(under); s.M = np.eye(4) if M is None else np.asarray(M, float).copy()
        s.pid = pid; s.vekt_g = vekt_g; s.spreng = spreng; s.plast = plast
        s.print_R = np.eye(4) if print_R is None else np.asarray(print_R, float)
        s.watt = watt; s.lyser = lyser; s.anker = dict(anker or {}); s.merknad = merknad; s.flat_film = flat_film
        s.omgjevnad = omgjevnad                           # ikkje ein del av lampa (skjermen, bordkanten): sjå kjopt()
        if abs(abs(np.linalg.det(s.M[:3, :3])) - 1.0) > 1e-6:
            raise ValueError('%s: M er ikkje stiv (delane kan ikkje skalerast)' % namn)

    def kopi(s, **kw):
        n = copy.copy(s); n.under = list(s.under); n.M = s.M.copy(); n.anker = dict(s.anker)
        for k, v in kw.items(): setattr(n, k, v)
        return n

    def flytt(s, M2):
        """Same del, flytta med M2 etter plasseringa han alt har (til dømes ei stilling i gesten)."""
        return s.kopi(M=np.asarray(M2, float) @ s.M)

    def punkt(s, namn):
        """Eit ankerpunkt på delen, i lampa sitt system (mm). Sjå del.anker for namna."""
        return pkt(s.M, s.anker[namn])

    def retning(s, v):
        """Ei retning i delen sitt eige system, i lampa sitt system."""
        return retn(s.M, v)

    def underdelar(s):
        """[(undernamn, mesh i lampa sitt system, materiale)]"""
        ut = []
        for u, m, mat in s.under:
            m2 = m.copy(); m2.apply_transform(s.M); ut.append((u, m2, mat))
        return ut

    def mesh(s, lokal=False):
        ms = [m.copy() for _, m, _ in s.under]
        m = trimesh.util.concatenate(ms) if len(ms) > 1 else ms[0]
        if not lokal: m.apply_transform(s.M)
        return m

    def grenser(s):
        return s.mesh().bounds

    def __repr__(s):
        return '<Del %s (%s%s) %s>' % (s.namn, s.slag, ' ' + s.pid if s.pid else '', '+'.join(u for u, _, _ in s.under))


def _anker(pid, under, ekstra):
    """Namngjevne punkt i delen sitt eige system, leidde ut av meshen (måla står berre i delar.py)."""
    b = {u: m.bounds for u, m, _ in under}
    a = {'origo': (0.0, 0.0, 0.0)}
    if pid == 'P01':
        if 'profil' in b:
            lo, hi = b['profil']
            a.update(profil_start=(lo[0], 0, 0), profil_slutt=(hi[0], 0, 0), profil_midt=((lo[0] + hi[0]) / 2, 0, 0))
        a['hengselakse'] = (0, 0, 0)
        xa, ya, za = ekstra['hovudakse']
        a['hovudakse'] = (xa, 0.0, za)                          # aksen går langs y gjennom dette punktet
        if 'tapp' in b:
            a['tapp_rot'] = (xa, b['tapp'][1][1], za); a['tapp_ende'] = (xa, b['tapp'][0][1], za)
    elif pid == 'P02':
        a['akse'] = (0, 0, 0)
        if 'plate' in b: a['plate_under'] = ((b['plate'][0][0] + b['plate'][1][0]) / 2, 0, b['plate'][0][2])
    elif pid == 'P03':
        a['lager'] = (0, 0, 0)
        if 'hus' in b:
            lo, hi = b['hus']
            a.update(midt=((lo[0] + hi[0]) / 2, 0, 0), opning=((lo[0] + hi[0]) / 2, 0, hi[2]), botn=((lo[0] + hi[0]) / 2, 0, lo[2]))
    elif pid == 'P05':
        t = b['plate'][1][2] if 'plate' in b else max(m.bounds[1][2] for _, m, _ in under)      # rillene sit på oversida av plata
        a.update(midt=(0, 0, 0), spegelflate=(0, 0, t), brennpunkt=(0, 0, t + D.v('P05', 'brennvidd')))
    elif pid == 'P06':
        a.update(flatside=(0, 0, 0), topp=(0, 0, b['linse'][1][2]))
    elif pid == 'P07':
        a['under'] = (0, 0, 0)
        if 'glas' in b: a['linse'] = (0, 0, (b['glas'][0][2] + b['glas'][1][2]) / 2)
        if 'fatning' in b: a['topp'] = (0, 0, b['fatning'][1][2])
    elif pid == 'P08':
        lo, hi = b['ark']
        a.update(midt=(0, (lo[1] + hi[1]) / 2, 0), nedkant=(0, lo[1], 0))
    return a


def sett(pid, M=None, berre=None, utan=(), namn=None, vekt_g=None, spreng=None, materiale=None, merknad=''):
    """Ein del frå byggjesettet (P01, P02, P03, P05, P06, P07, P08), plassert med M.
    berre / utan: ta med eller ta bort underdelar (namna står i modell/byggjesett/stl/).
    materiale: byt materialmerke på underdelar, t.d. {'profil': 'stål'} om magneten sit på armen.
    vekt_g: vegen masse for heile delen. Utan han blir massen rekna frå anslått mål (usikker)."""
    if pid in FORBODNE:
        raise ValueError(FORBODNE[pid])
    under, ekstra = D.del_(pid)
    val = [(u, m, (materiale or {}).get(u, mat)) for u, m, mat in under
           if (berre is None or u in berre) and u not in utan]
    if not val:
        raise ValueError('%s: ingen underdelar att (finst: %s)' % (pid, ', '.join(u for u, _, _ in under)))
    return Del(namn or DIMS[pid]['namn'], 'sett', val, M, pid=pid, vekt_g=vekt_g, spreng=spreng,
               anker=_anker(pid, val, ekstra), merknad=merknad)


def film(breidd, hogd, M=None, namn='film', spreng=None, riller='breidd'):
    """Eit stykke klipt av prismearket P08: ligg i xy-planet med origo i midten, prismesida mot +z.
    riller: rillene går langs 'breidd' (x) eller 'hogd' (y) på stykket. På heile arket går dei langs kortsida.
    Seier frå om stykket ikkje får plass i det minste arket måla tillèt."""
    t = max(D.v('P08', 'tjukk'), 0.2)
    langs_riller, tvers = (breidd, hogd) if riller == 'breidd' else (hogd, breidd)
    kort, lang = usikker('P08', 'breidd'), usikker('P08', 'hogd')
    if langs_riller > kort['hi'] or tvers > lang['hi']:
        raise ValueError('filmstykket %.0f x %.0f er større enn arket kan vere (%.0f langs rillene, %.0f på tvers)'
                         % (breidd, hogd, kort['hi'], lang['hi']))
    merk = ''
    if langs_riller > FILM_TRYGG[0] or tvers > FILM_TRYGG[1]:
        merk = ('ANTAKING: stykket krev at arket er større enn %.0f x %.0f mm. Mål arket før du klipper.' % FILM_TRYGG)
        print('  merk film:', merk)
    m = trimesh.creation.box((breidd, hogd, t)); m.apply_translation((0, 0, t / 2))
    d = Del(namn, 'sett', [('ark', m, 'film')], M, pid='P08', spreng=spreng, merknad=merk,
            anker=dict(origo=(0, 0, 0), midt=(0, 0, 0), prismeside=(0, 0, t)))
    d.riller = (1.0, 0.0, 0.0) if riller == 'breidd' else (0.0, 1.0, 0.0)      # retninga rillene går, i stykket sitt system
    d.storleik = (float(breidd), float(hogd))
    return d


def trykt(namn, mesh, M=None, plast='PETG', print_R=None, spreng=None, vekt_g=None, merknad=''):
    """Ein trykt del. mesh: trimesh i delen sitt eige system (mm), eller ei CadQuery-form.
    print_R: dreiinga frå delen sitt system til slik han ligg på plata (standard: som teikna, z opp)."""
    if not isinstance(mesh, trimesh.Trimesh):
        mesh = fraa_cq(mesh)
    return Del(namn, 'print', [(namn, mesh, 'print')], M, plast=plast, print_R=print_R, spreng=spreng, vekt_g=vekt_g, merknad=merknad)


def kjopt(namn, mesh, materiale, masse_g, M=None, watt=None, lyser=False, spreng=None, merknad='', omgjevnad=False):
    """Ein kjøpt del med oppgjeven masse (g). watt: effekten til ein LED-del (høgste). lyser: flata gløder i rendringa
    og blir halden utanfor skuggekroppen i lysstudien. materiale: 'led', 'opal', 'aluminium', 'stål', 'gummi_svart' ...
    omgjevnad=True: noko lampa heng på eller står under, som ikkje er ein del av henne (skjermen, ein bordkant). Det er med
    i velt og kollisjon, men ikkje i massen til lampa (F8), i rendringane, i GLB-fila eller i skuggekroppen til lysstudien."""
    return Del(namn, 'kjopt', [(namn, mesh, materiale)], M, vekt_g=float(masse_g), watt=watt, lyser=lyser, spreng=spreng, merknad=merknad,
               omgjevnad=omgjevnad)

# ------------------------------------------------------------------ former til trykte og kjøpte delar (trimesh, mm)

def _rr(b, h, r=0.0):
    p = _sboks(-b / 2, -h / 2, b / 2, h / 2)
    return p.buffer(-r).buffer(r, resolution=8) if r > 0 else p

def ekstruder(polygon, h, z0=0.0):
    """Ekstruder eit shapely-polygon (xy) h mm opp frå z0."""
    m = trimesh.creation.extrude_polygon(polygon, h); m.apply_translation((0, 0, z0)); return m

def boks(lx, ly, lz, senter=(0, 0, 0), r=0.0):
    """Boks med midten i senter. r rundar dei loddrette kantane."""
    m = ekstruder(_rr(lx, ly, r), lz, -lz / 2) if r > 0 else trimesh.creation.box((lx, ly, lz))
    m.apply_translation(senter); return m

def sylinder(d, h, z0=0.0, n=96):
    m = trimesh.creation.cylinder(radius=d / 2, height=h, sections=n); m.apply_translation((0, 0, z0 + h / 2)); return m

def royr(d_ytre, d_indre, h, z0=0.0, n=96):
    """Rundt røyr frå z0 til z0 + h."""
    ring = Point(0, 0).buffer(d_ytre / 2, resolution=n // 4).difference(Point(0, 0).buffer(d_indre / 2, resolution=n // 4))
    return ekstruder(ring, h, z0)

def hylse(indre_b, indre_h, lengd, vegg=3.0, z0=0.0, r=1.0):
    """Firkanta hylse (til dømes rundt armprofilen): opning indre_b x indre_h i xy, lengd langs z."""
    ytre = _rr(indre_b + 2 * vegg, indre_h + 2 * vegg, r + vegg)
    return ekstruder(ytre.difference(_rr(indre_b, indre_h, r)), lengd, z0)

def plate(lx, ly, t, hol=(), spor=(), r=0.0, z0=0.0):
    """Plate i xy med midten i origo. hol: [(x, y, d)]. spor: [(x, y, lengd, breidd, vinkel i grader)], avlange spor
    med runde endar (til skruar som skal kunne justerast, eller til å ta opp usikre mål)."""
    p = _rr(lx, ly, r)
    for x, y, d in hol:
        p = p.difference(Point(x, y).buffer(d / 2, resolution=16))
    for x, y, lengd, breidd, vinkel in spor:
        s = _sboks(-(lengd - breidd) / 2, -breidd / 2, (lengd - breidd) / 2, breidd / 2).buffer(0)
        s = s.union(Point(-(lengd - breidd) / 2, 0).buffer(breidd / 2, resolution=12)).union(Point((lengd - breidd) / 2, 0).buffer(breidd / 2, resolution=12))
        p = p.difference(_aff.translate(_aff.rotate(s, vinkel, origin=(0, 0)), x, y))
    return ekstruder(p, t, z0)

def vinkel(l1, l2, breidd, t, hol1=(), hol2=()):
    """Vinkelbrakett: éin flens ligg i xy (l1 langs +x), den andre står i yz ved x = 0 (l2 langs +z). breidd langs y.
    hol1: [(x, y, d)] i den liggjande flensen. hol2: [(z, y, d)] i den ståande."""
    a = plate(l1, breidd, t, hol=[(x - l1 / 2, y, d) for x, y, d in hol1]); a.apply_translation((l1 / 2, 0, 0))
    b = plate(l2, breidd, t, hol=[(z - l2 / 2, y, d) for z, y, d in hol2])
    b.apply_transform(Ry(-90)); b.apply_translation((t, 0, l2 / 2))
    return pluss(a, b)

def skal(lx, ly, lz, vegg=2.0, open='+z', r=0.0):
    """Open kasse (skal) med ytre mål lx, ly, lz, midt i xy, botnen i z = 0. open: sida utan vegg, '+z' eller '-z'."""
    ytre = ekstruder(_rr(lx, ly, r), lz)
    z0 = vegg if open == '+z' else -1.0
    indre = ekstruder(_rr(lx - 2 * vegg, ly - 2 * vegg, max(r - vegg, 0.0)), lz - vegg + 1.0, z0)
    return minus(ytre, indre)

def kopp(d, h, vegg=2.0, n=96):
    """Rund kopp: ytre diameter d, høgd h, open oppe, botnen i z = 0."""
    return minus(sylinder(d, h, 0, n), sylinder(d - 2 * vegg, h, vegg, n))

def dreielekam(profil, n=96):
    """Dreielekam om z frå ein profil [(radius, z), ...] (lukka, mot klokka)."""
    return trimesh.creation.revolve(np.asarray(profil, float), sections=n)

def minus(a, *b):
    return trimesh.boolean.difference([a, *b], engine='manifold')

def pluss(*ms):
    return trimesh.boolean.union(list(ms), engine='manifold')

def snitt(a, b):
    return trimesh.boolean.intersection([a, b], engine='manifold')

def flytta(mesh, M):
    """Kopi av ein mesh gjennom M (til å byggje ein trykt del av fleire former)."""
    m = mesh.copy(); m.apply_transform(M); return m

def fraa_cq(form, toleranse=0.05, vinkeltoleranse=0.15):
    """CadQuery-form (Workplane eller Shape) til trimesh."""
    shp = form.val() if hasattr(form, 'val') else form
    v, f = shp.tessellate(toleranse, vinkeltoleranse)
    m = trimesh.Trimesh(np.array([(p.x, p.y, p.z) for p in v]), np.array(f), process=True)
    if not m.is_watertight:
        m.merge_vertices(); trimesh.repair.fix_normals(m)
    return m

# ------------------------------------------------------------------ kjøpte delar som ofte går att

def led_skive(d=40.0, t=1.6, watt=5.0, namn='led', M=None, spreng=None):
    """Rund LED-modul på aluminiumskjerne (kjøpt). Lysflata er +z-sida. Masse rekna frå aluminium 2,70 g/cm³."""
    m = sylinder(d, t, 0, 64)
    return kjopt(namn, m, 'led', math.pi * (d / 20) ** 2 * (t / 10) * 2.70, M, watt=watt, lyser=True, spreng=spreng,
                 merknad='kjøpt LED-modul, ANTAKING om storleik')

def led_stripe(lengd, breidd=10.0, t=2.0, watt_per_m=10.0, namn='stripe', M=None, spreng=None):
    """LED-stripe (kjøpt), langs x, lysflata er +z-sida. Massen er ANTAKING: 25 g per meter."""
    m = boks(lengd, breidd, t, (0, 0, t / 2))
    return kjopt(namn, m, 'led', 25.0 * lengd / 1000, M, watt=watt_per_m * lengd / 1000, lyser=True, spreng=spreng,
                 merknad='kjøpt LED-stripe, %.0f W/m (ANTAKING)' % watt_per_m)

# ------------------------------------------------------------------ samlinga

def alle_under(delar):
    """[(del, undernamn, mesh i lampa sitt system, materiale)] for heile samlinga."""
    return [(d, u, m, mat) for d in delar for u, m, mat in d.underdelar()]

def grenser(delar):
    b = np.array([d.grenser() for d in delar])
    return b[:, 0].min(0), b[:, 1].max(0)

def finn(delar, namn):
    for d in delar:
        if d.namn == namn: return d
    raise KeyError(namn)

def filnamn(tekst):
    """Eit namn som trygt kan stå i eit filnamn (ASCII, utan mellomrom)."""
    for a, b in (('å', 'a'), ('ø', 'o'), ('æ', 'ae'), ('Å', 'A'), ('Ø', 'O'), ('Æ', 'Ae')):
        tekst = tekst.replace(a, b)
    return ''.join(c if (c.isascii() and (c.isalnum() or c in '-_')) else '_' for c in tekst)

def med_staalarm(delar):
    """Same samling med armprofilen (P01, underdelen «profil») rekna som stål. delar.py merkjer profilen som aluminium,
    oppdragsteksten kallar armen ein stålprofil, og ingen har prøvd med magnet. Stål gjev om lag 250 g meir.
    Delar med vegen masse (vekt_g) blir ikkje rørte."""
    ut = []
    for d in delar:
        if d.pid == 'P01' and d.vekt_g is None and any(u == 'profil' and mat == 'aluminium' for u, _, mat in d.under):
            d = d.kopi(under=[(u, m, 'stål' if u == 'profil' else mat) for u, m, mat in d.under])
        ut.append(d)
    return ut

def sprengd(delar, faktor=0.6):
    """Samlinga dregen frå kvarandre. Ein del med .spreng = (dx, dy, dz) flyttar seg så mykje. Delar utan
    blir skuva ut frå midten av samlinga langs den aksen dei ligg lengst ute på (faktor gonger avstanden)."""
    delar = [d for d in delar if not d.omgjevnad]
    lo, hi = grenser(delar); midt = (lo + hi) / 2
    ut = []
    for d in delar:
        if d.spreng is not None:
            v = np.asarray(d.spreng, float)
        else:
            b = d.grenser(); c = (b[0] + b[1]) / 2 - midt
            k = int(np.argmax(np.abs(c) / np.maximum(hi - lo, 1e-9)))
            v = np.zeros(3); v[k] = faktor * c[k]
        ut.append(d.flytt(T(*v)))
    return ut


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    print('Grensesnittmål frå modell/byggjesett/maal.json (mm). opning = sporet som tek delen om han er størst (luft 0,3).')
    for pid, d in GRENSESNITT.items():
        for k, tekst in d.items():
            c = klaring(pid, k)
            print('  %s %-14s %7.1f ± %-5.1f opning %7.1f  slark %5.1f  %-34s %s' % (pid, k, c['nominell'], c['pm'], c['opning'], c['slark'], tekst, c['kjelde']))
    for pid in ('P01', 'P02', 'P03', 'P05', 'P06', 'P07', 'P08'):
        d = sett(pid)
        print(' ', d, 'anker:', {k: tuple(round(float(x), 1) for x in v) for k, v in d.anker.items()})
