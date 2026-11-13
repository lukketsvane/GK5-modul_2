# -*- coding: utf-8 -*-
"""Familien FALD: arket får faldar, slik at ulike flater peikar mot ulike adresser.

  python familie.py            siste generasjon: tal.md, tal.csv, ekstra.md, brett og par i denne mappa
  python familie.py --gen 1    søk i generasjon 1 (berre tal, i mappa gen1/). Like eins 2 og 3
  python familie.py --radius   serien skarp mot mjuk fald (radius.md)

Bygd på konsept/reflektor/_mal.py. Geometrien kjem frå faldmotor.py (kreppar inn, falda ark ut).
Eit lysgrep er g(t) -> (lys, kropp). t = 0 er stemning, t = 1 er arbeid.
"""
import sys, os, math, csv
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
from faldmotor import *

S, M = SATIN, MATT
KP = b(FOT[0], FOT[1], 0.05)
MAAL = dict(felt=350.0, vegg=100.0, ansikt=50.0)

def lin(a, c, t): return a + (c - a) * t

# ------------------------------------------------------------------ lampa

def lampe(t, kreppar=None, rot='felt', flater=(S,), storleik=(0.25, 0.25), hogd=0.41, pos=(0.47, 0.40),
          rull=0.0, spreiing=10, flat=None, sikte=(0.0, 0.0), anker=(0.0, 0.0), klipp=None, flik=False,
          n=22, eigaform=None, dim=1.0):
    """Kjelde i foten lyser opp på eit falda ark på ei stong.
    kreppar: liste, eller funksjon (t, c, n_rot) -> liste. rot: adressa til rotpanelet (namn, punkt eller funksjon av t).
    flater: overflate per panel (rot først). sikte: punktet på det flate arket som kjelda siktar på.
    anker: punkt i rotpanelet. flik=True klipper bort hjørna mellom flikar."""
    W, K = watt(t)
    c = b(pos[0], pos[1], hogd)
    m = rot(t) if callable(rot) else rot
    m = ADR[m] if isinstance(m, str) else np.asarray(m, float)
    n_rot = nrm(nrm(KP - c) + nrm(m - c))
    for _ in range(2):                                   # rotpanelet speglar frå ankeret, ikkje frå arksenteret
        ex, ey, ez = ramme(n_rot, rull); pa = c + anker[0] * ex + anker[1] * ey
        n_rot = nrm(nrm(KP - pa) + nrm(m - pa))
    ex, ey, ez = ramme(n_rot, rull)
    kr = kreppar(t, c, n_rot) if callable(kreppar) else (list(kreppar) if kreppar else [])
    sk = sikte(t) if callable(sikte) else sikte
    mot = c + sk[0] * ex + sk[1] * ey
    sp = spreiing(t) if callable(spreiing) else spreiing
    k = straale(KP, mot, W * LMW_KJELDE * dim, K, spreiing=sp, flat=flat, kutt=2 * (max(flat) if flat else sp),
                opning=0.02, bronn=40)
    kl = klipp
    if flik:
        hk = hjorneklipp(kr, anker)
        kl = hk if klipp is None else (lambda u, v: hk(u, v) & klipp(u, v))
    fl = flater(t) if callable(flater) else flater
    a = faldark(k, c, n_rot, storleik, kr, fl, klipp=kl, rull=rull, n=n, eigaform=eigaform, anker=anker)
    kropp = [syl(b(FOT[0], FOT[1], 0), b(FOT[0], FOT[1], 0.05), 0.06),
             syl(b(FOT[0], 0.535, 0.05), b(FOT[0], 0.535, hogd + 0.02), 0.004)]
    return [k, a], kropp

def vipp(t):
    return VEGGM * (1 - t) + FELT * t

def K1(maal, avstand, hol, skala=lambda t: t, R=SKARP, anker=(0.0, 0.0)):
    """Éin krepp som siktar panelet utanfor mot «maal» ved t = 1. Vinkelen følgjer skala(t)."""
    def f(t, c, n_rot):
        k = sikt(c, n_rot, KP, ADR[maal] if isinstance(maal, str) else maal, avstand, hol, R=R, anker=anker)
        k['vinkel'] *= skala(t); return [k]
    return f

def saman(*deler):
    return lambda t, c, n_rot: [k for d in deler for k in d(t, c, n_rot)]

def parallell(maal_a, av_a, hol_a, maal_b, av_b, hol_b, skala=lambda t: t, R=SKARP):
    """To parallelle kreppar. Den første siktar mot maal_a og gjev retninga.
    Den andre ligg på motsett side, og vinkelen blir stilt så midtstrålen går nærast maal_b."""
    def f(t, c, n_rot):
        ka = sikt(c, n_rot, KP, ADR[maal_a], av_a, hol_a, R=R)
        th = math.radians(ka['ret'] - 90.0); g = np.array([math.cos(th), math.sin(th)])
        s = 1.0 if hol_a else -1.0                        # flik a ligg på -s·g ... flik b på motsett side
        if not hol_a: g = g                               # g er projeksjonen av normalen til a
        pb = s * av_b * g
        kb = dict(p=(float(pb[0]), float(pb[1])), ret=ka['ret'], vinkel=0.0, R=R, mot=(float(pb[0] + s * g[0]), float(pb[1] + s * g[1])))
        uv = pb + s * 0.045 * g
        omr = (0, 85) if hol_b else (-85, 0)
        kb['vinkel'] = still(KP, c, n_rot, [ka, kb], 1, uv, ADR[maal_b], omrade=omr)
        ka['vinkel'] *= skala(t); kb['vinkel'] *= skala(t)
        return [ka, kb]
    return f

def vifte(apex, retningar, vinklar, skala=lambda t: t, R=SKARP):
    """Kreppar som strålar ut frå eitt punkt utanfor arket."""
    return lambda t, c, n_rot: [dict(p=apex, ret=r, vinkel=v * skala(t), R=R) for r, v in zip(retningar, vinklar)]

def trekkspel(maal, tal_, breidd, skala=lambda t: t, R=SKARP, rot='felt'):
    """Parallelle kreppar med annakvar veg: to sett panel, eitt mot rota si adresse og eitt mot «maal».
    Kvart panel blir sikta for seg (kjelda står nær, så vinklane er ulike), slik rillene i ein fresnelspegel er det.
    maal kan vere ei liste med punkt. Då får kvart panel sitt eige punkt (fordelt sikt)."""
    punkt = [ADR[maal]] if isinstance(maal, str) else [np.asarray(p, float) for p in maal]
    def f(t, c, n_rot):
        k0 = sikt(c, n_rot, KP, punkt[0], breidd / 2, True, R=R)
        th = math.radians(k0['ret'] - 90.0); g = np.array([math.cos(th), math.sin(th)])
        ut = []; nr = 0
        for side in (-1.0, 1.0):
            for j in range(tal_ // 2):
                p = side * (breidd / 2 + j * breidd) * g
                ut.append(dict(p=(float(p[0]), float(p[1])), ret=k0['ret'], vinkel=0.0, R=R,
                               mot=(float(p[0] + side * g[0]), float(p[1] + side * g[1]))))
                uv = p + side * (breidd / 2) * g
                if j % 2 == 0: m = punkt[nr % len(punkt)]; nr += 1
                else: m = ADR[rot]
                ut[-1]['vinkel'] = still(KP, c, n_rot, ut, len(ut) - 1, uv, m, omrade=(-70, 70))
        for k in ut: k['vinkel'] *= skala(t)
        return ut
    return f

def kjede(maal, avstand, steg, hol, skala=lambda t: t, R=SKARP, anker=(0.0, 0.0)):
    """Vifte: fleire panel etter kvarandre utover frå rota, kvart sikta mot sitt eige punkt.
    Første krepp kjem frå sikt(). Dei neste får retning og vinkel ved søk (rein geometri),
    så kreppane blir ikkje parallelle. Kryssar dei inne i arket, syner det som rift."""
    punkt = [np.asarray(p, float) for p in maal]
    def f(t, c, n_rot):
        k0 = sikt(c, n_rot, KP, punkt[0], avstand, hol, R=R, anker=anker)
        th = math.radians(k0['ret'] - 90.0); g = np.array([math.cos(th), math.sin(th)])
        ut_ = (-1.0 if hol else 1.0) * g
        ut = [k0]
        for j, m in enumerate(punkt[1:], 1):
            p = np.array(k0['p']) + j * steg * ut_
            uv = p + 0.5 * steg * ut_
            best = (9.0, ut[-1]['ret'], 0.0)                 # høgst 9 grader frå førre krepp, så dei ikkje kryssar inne i arket
            for ret in np.arange(ut[-1]['ret'] - 9, ut[-1]['ret'] + 9.1, 3.0):
                for v in np.arange(-20, 20.1, 1.0):
                    kk = ut + [dict(p=(float(p[0]), float(p[1])), ret=float(ret), vinkel=float(v), R=R, mot=(float(p[0] + ut_[0]), float(p[1] + ut_[1])))]
                    r, p0 = treff(KP, c, n_rot, kk, uv, anker=anker)
                    av = 1 - r @ nrm(m - p0)
                    if av < best[0]: best = (av, float(ret), float(v))
            ut.append(dict(p=(float(p[0]), float(p[1])), ret=best[1], vinkel=best[2], R=R, mot=(float(p[0] + ut_[0]), float(p[1] + ut_[1]))))
        for k in ut: k['vinkel'] *= skala(t)
        return ut
    return f

def staaande(t):
    """Ei bok som står på bordet. Kjelda i foten lyser vassrett inn i boka. Veltar: ingenting når feltet."""
    W, K = watt(t)
    c = b(0.50, 0.40, 0.17); kp = b(0.36, 0.26, 0.05)
    k = straale(kp, c, W * LMW_KJELDE, K, spreiing=14, kutt=28, opning=0.02, bronn=40)
    n_rot = nrm(nrm(kp - c) + nrm(VEGGM - c))
    kr = [dict(p=(0.0, 0.0), ret=90.0, vinkel=lin(10, 70, t), mot=(-1.0, 0.0))]
    a = faldark(k, c, n_rot, (0.30, 0.30), kr, (S, M), anker=(0.05, 0.0))
    return [k, a], [syl(b(0.36, 0.26, 0), b(0.36, 0.26, 0.05), 0.05)]

# ------------------------------------------------------------------ generasjon 1: topologi
# Alle: ark 25 x 25 cm, 41 cm over bordet, SATIN, skarpe faldar. Overgangen er «boka»:
# arket er flatt i stemning, og faldane opnar seg med t. Rota siktar mot feltet om ikkje anna står.

def valm(t, c, n_rot):
    a = 30 * t
    return [dict(p=(0.05, 0), ret=90, vinkel=-a), dict(p=(-0.05, 0), ret=90, vinkel=-a),
            dict(p=(0, 0.05), ret=0, vinkel=-a), dict(p=(0, -0.05), ret=0, vinkel=-a)]

GEN1 = [
    ('flat-vipp',  lambda t: lampe(t, rot=vipp)),
    ('bok-hol',    lambda t: lampe(t, K1('vegg', 0.03, True))),
    ('tak',        lambda t: lampe(t, K1('vegg', 0.03, False))),
    ('bok-vegg',   lambda t: lampe(t, K1('felt', 0.02, False, anker=(0.0, 0.06)), rot='vegg', anker=(0.0, 0.06))),
    ('Z',          lambda t: lampe(t, parallell('vegg', 0.04, True, 'vegg', 0.04, False))),
    ('U-hol',      lambda t: lampe(t, parallell('vegg', 0.04, True, 'ansikt', 0.04, True))),
    ('kvelv',      lambda t: lampe(t, parallell('vegg', 0.04, False, 'ansikt', 0.04, False))),
    ('vifte',      lambda t: lampe(t, vifte((0.40, 0.0), (168, 180, 192), (15, 15, 15)), anker=(0.0, -0.06))),
    ('trekkspel',  lambda t: lampe(t, trekkspel('vegg', 6, 0.036), n=34)),
    ('flik',       lambda t: lampe(t, saman(K1('vegg', 0.05, False), K1('ansikt', 0.06, False)), flater=(S, S, M), flik=True)),
    ('skeiv',      lambda t: lampe(t, saman(K1('vegg', 0.035, False), K1('ansikt', 0.05, False)), flater=(S, S, M))),
    ('rund',       lambda t: lampe(t, K1('vegg', 0.03, False), storleik=0.28)),
    ('band',       lambda t: lampe(t, saman(K1('vegg', 0.06, False), K1('ansikt', 0.06, False)), storleik=(0.14, 0.40), flat=(6, 14), flater=(S, S, M))),
    ('matt-floy',  lambda t: lampe(t, K1('ansikt', 0.05, False), flater=(S, M))),
    ('staaande',   staaande),                                  # veltar: bryt F3
    ('valm',       lambda t: lampe(t, valm)),                  # kan ikkje lagast: fire faldar utan klipp i hjørna
]

# ------------------------------------------------------------------ generasjon 2: overgang, radius, overflate
# Settet stivna i generasjon 1 (éin fald mot veggen er nok, og boka frå flatt ark mot feltet er ein dimmar).
# Nytt grep: kva som rører seg. Boka opnar seg frå veggen, heile arket vippar, eller kjelda sveiper over faldane.

C0 = b(0.47, 0.40, 0.41)
N_FELT = nrm(nrm(KP - C0) + nrm(FELT - C0))
G_V = np.array([0.50, 0.866])                         # retninga i arket frå feltpanelet mot veggpanelet
ein = lambda t: 1.0
FAST_TAK = K1('vegg', 0.03, False, skala=ein)(1.0, C0, N_FELT)
FAST_TAK0 = K1('vegg', 0.005, False, skala=ein)(1.0, C0, N_FELT)
FAST_Z = parallell('vegg', 0.04, True, 'vegg', 0.04, False, skala=ein)(1.0, C0, N_FELT)
FAST_SPEL = trekkspel('vegg', 6, 0.036, skala=ein)(1.0, C0, N_FELT)

def kuppel(U, V):
    R = 0.30
    return U, V, -(R - np.sqrt(np.maximum(R * R - U * U - V * V, 1e-9)))

MIDT = b(0.0, 0.50, 0.20)                              # mellom felt og vegg: der bogen siktar med midten

GEN2 = [
    ('tak-bok',      lambda t: lampe(t, K1('vegg', 0.03, False))),
    ('bok-vegg',     lambda t: lampe(t, K1('felt', 0.07, False, anker=(0.04, 0.07)), rot='vegg', anker=(0.04, 0.07))),
    ('tak-vipp',     lambda t: lampe(t, FAST_TAK, rot=vipp)),
    ('tak-sveip',    lambda t: lampe(t, FAST_TAK0, spreiing=8, sikte=lambda t: tuple(G_V * lin(0.06, -0.02, t)))),
    ('Z-vegg',       lambda t: lampe(t, parallell('felt', 0.03, True, 'felt', 0.03, False), rot='vegg')),
    ('Z-sveip',      lambda t: lampe(t, FAST_Z, spreiing=8, sikte=lambda t: tuple(G_V * lin(0.085, 0.0, t)))),
    ('spel-vegg',    lambda t: lampe(t, trekkspel('felt', 6, 0.036, rot='vegg'), rot='vegg', n=34)),
    ('spel-vipp',    lambda t: lampe(t, FAST_SPEL, rot=vipp, n=34)),
    ('tak-mattvegg', lambda t: lampe(t, K1('vegg', 0.03, False), flater=(S, M))),
    ('tak-mjuk',     lambda t: lampe(t, K1('vegg', 0.03, False, R=0.04))),
    ('S-boge',       lambda t: lampe(t, parallell('vegg', 0.04, True, 'vegg', 0.04, False, R=0.03))),
    ('bolgje',       lambda t: lampe(t, trekkspel('vegg', 6, 0.036, R=0.03), n=34)),
    ('boge',         lambda t: lampe(t, rot=MIDT, rull=60.0, eigaform=boy(-2.5 * t))),
    ('matt-rot',     lambda t: lampe(t, K1('vegg', 0.03, False), flater=(M, S))),        # veltar: bryt B3
    ('kuppel',       lambda t: lampe(t, eigaform=kuppel)),                               # kan ikkje lagast: dobbeltkrum
]

# ------------------------------------------------------------------ generasjon 3: fordelt sikt, mjuk radius, rot mot veggen
# Watten for tre adresser stivna i generasjon 2. No er grepet jamnheit (panela siktar ulike stader),
# mjuk fald som standard (R = 25 mm), og boka som opnar seg frå veggen. Pluss optikken frå overheadprojektoren.

MJ = 0.025
FX = lambda x, y=0.25: b(x, y, 0.0)                    # punkt i feltet
_cache = {}
def fast(namn, lag):
    """Kreppar som berre endrar vinkel med t, blir rekna éin gong (ved t = 1) og skalerte."""
    def f(t, c, n_rot):
        if namn not in _cache: _cache[namn] = lag(1.0, c, n_rot)
        return [dict(k, vinkel=k['vinkel'] * t) for k in _cache[namn]]
    return f

FAST_TAK_MJ = K1('vegg', 0.03, False, skala=ein, R=MJ)(1.0, C0, N_FELT)
FAST_TAK0_MJ = K1('vegg', 0.005, False, skala=ein, R=MJ)(1.0, C0, N_FELT)
FAST_Z_MJ = parallell('vegg', 0.04, True, 'vegg', 0.04, False, skala=ein, R=MJ)(1.0, C0, N_FELT)

def fresnel_floy(t):
    """Fresnelspegelen frå overheadprojektoren (285 x 285 mm, med diffusorark oppå) mot feltet,
    og ein falda satinvenge på veggkanten mot veggen. Leddet på projektorstolpen vippar plata."""
    W, K = watt(t)
    m = vipp(t)
    n = nrm(nrm(KP - C0) + nrm(m - C0))
    ex, ey, ez = ramme(n, -30.0)
    k = straale(KP, C0 + 0.09 * ey, W * LMW_KJELDE, K, spreiing=13, kutt=26, opning=0.02, bronn=40)
    plate = fresnelspegel(k, C0, n, spreiing=10, opp=OPP, rull=-30.0)
    a = math.radians(27.0); d = 0.06
    cv = C0 + (0.1425 + d * math.cos(a)) * ey - d * math.sin(a) * ez
    nv = math.cos(a) * ez + math.sin(a) * ey
    venge = ark(k, cv, nv, (0.285, 2 * d), opp=np.cross(nv, ex), framside=SATIN, n=24)
    k.lm_ut = max(k.lm - plate.lm_inn - venge.lm_inn, 0.0)      # ark() skriv over lm_ut når to ark deler kjelde
    kropp = [syl(b(FOT[0], FOT[1], 0), b(FOT[0], FOT[1], 0.05), 0.06),
             syl(b(FOT[0], 0.535, 0.05), b(FOT[0], 0.535, 0.43), 0.004)]
    return [k, plate, venge], kropp

def kryss3(t, c, n_rot):
    """Tre flikar mot tre punkt i feltet, rett frå rota og utan klipp. Kreppane kryssar inne i arket."""
    ut = []
    for x, av, hol in ((-0.2, 0.02, True), (0.0, 0.05, True), (0.2, 0.03, False)):
        k = sikt(c, n_rot, KP, FX(x), av, hol, R=MJ); k['vinkel'] *= t; ut.append(k)
    ut[1]['ret'] += 35.0
    return ut

SPELMAAL = [FX(0, 0.12), FX(0, 0.38), FX(0, 0.21), FX(0, 0.30)]
BOK = dict(rot='vegg', anker=(0.04, 0.07))

GEN3 = [
    ('flat-vipp',   lambda t: lampe(t, rot=vipp)),                                                        # referanse frå malen
    ('bok',         lambda t: lampe(t, K1('felt', 0.07, False, R=MJ, anker=(0.04, 0.07)), **BOK)),
    ('Z-samla',     lambda t: lampe(t, parallell('felt', 0.03, True, 'felt', 0.03, False, R=MJ), rot='vegg')),
    ('Z-spreidd',   lambda t: lampe(t, saman(K1(FX(-0.15), 0.03, True, R=MJ), K1(FX(0.15), 0.03, False, R=MJ)), rot='vegg')),
    ('vifte',       lambda t: lampe(t, fast('vifte', kjede([FX(0.18), FX(0.0), FX(-0.18)], 0.07, 0.055, False, R=MJ, anker=(0.04, 0.07))), **BOK)),
    ('spel',        lambda t: lampe(t, fast('spel', trekkspel(SPELMAAL, 6, 0.036, rot='vegg')), rot='vegg', n=34)),
    ('bolgje',      lambda t: lampe(t, fast('bolgje', trekkspel(SPELMAAL, 6, 0.036, R=0.02, rot='vegg')), rot='vegg', n=34)),
    ('tak-vipp',    lambda t: lampe(t, FAST_TAK_MJ, rot=vipp)),
    ('Z-vipp',      lambda t: lampe(t, FAST_Z_MJ, rot=vipp)),
    ('tak-sveip',   lambda t: lampe(t, FAST_TAK0_MJ, spreiing=8, sikte=lambda t: tuple(G_V * lin(0.06, -0.02, t)))),
    ('rund-bok',    lambda t: lampe(t, K1('felt', 0.07, False, R=MJ, anker=(0.04, 0.07)), storleik=0.28, **BOK)),
    ('liten-bok',   lambda t: lampe(t, K1('felt', 0.05, False, R=MJ, anker=(0.03, 0.05)), rot='vegg', anker=(0.03, 0.05), storleik=(0.18, 0.18), hogd=0.33, spreiing=9)),
    ('fresnel-floy', fresnel_floy),
    ('blank-bok',   lambda t: lampe(t, K1('felt', 0.07, False, anker=(0.04, 0.07)), flater=(BLANK,), n=30, **BOK)),   # veltar: spegel
    ('kryss',       lambda t: lampe(t, kryss3, rot='vegg')),                                              # kan ikkje lagast: kreppar som kryssar
]

def radiusserie(mappe):
    """Skarp mot mjuk fald: same adresser, ulik radius. Berre arbeid (t = 1)."""
    L = ['| Kropp | Radius, mm | Del av lyset som treff ein bøy | Felt, lx | Vegg, lx | Ansikt, lx | Jamnheit | W for alle tre | Mot auget, cd/m² |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for namn, lag, RR in (('tak (éin fald)', lambda R: lampe(1.0, K1('vegg', 0.03, False, R=R)), (0.002, 0.010, 0.020, 0.040, 0.080)),
                          ('Z (to faldar)', lambda R: lampe(1.0, parallell('vegg', 0.04, True, 'vegg', 0.04, False, R=R)), (0.002, 0.020, 0.040)),
                          ('trekkspel (seks faldar)', lambda R: lampe(1.0, trekkspel('vegg', 6, 0.036, R=R), n=34), (0.002, 0.010, 0.020, 0.040))):
        for R in RR:
            lys, kropp = lag(R); d = tal(lys, kropp); a = lys[1]
            kk = max(350 / d['E_felt'], 100 / d['E_vegg'], 50 / d['E_ansikt'])
            L.append(f"| {namn} | {R*1000:.0f} | {a.boydel*100:.0f} % | {d['E_felt']:.0f} | {d['E_vegg']:.0f} | {d['E_ansikt']:.0f} | {d['U']:.2f} | {d['W']*kk:.2f} | {max(d['L_lampe'], d['L_flate']):.0f} |")
            print(L[-1])
    open(os.path.join(mappe, 'radius.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')

# ------------------------------------------------------------------ køyring

def kjor(GREP, mappe, px=0, overg=()):
    """familie() pluss det faldmotoren veit: watt for alle tre adressene, rift og sjølvskugge."""
    huske = {}
    def pakk(namn, g):
        def gg(t):
            lys, kropp = g(t); huske[(namn, float(t))] = lys; return lys, kropp
        return gg
    rader = familie([(nm, pakk(nm, g)) for nm, g in GREP], mappe, px=px)
    for r in rader:
        ar = [l for t in (0.0, 1.0) for l in huske[(r['namn'], t)] if isinstance(l, Ark)]
        r['rift'] = max(getattr(a, 'rift', 0.0) for a in ar)
        r['sk_inn'] = max(getattr(a, 'sk_inn', 0.0) for a in ar); r['sk_ut'] = max(getattr(a, 'sk_ut', 0.0) for a in ar)
        krav = dict(felt=MAAL['felt'] / max(r['felt'], 1e-9), vegg=MAAL['vegg'] / max(r['vegg'], 1e-9),
                    ansikt=MAAL['ansikt'] / max(r['ansikt'], 1e-9))
        r['bind'] = max(krav, key=krav.get); r['W3'] = r['W'] * krav[r['bind']]
        r['auge3'] = r['auge'] * r['W3'] / r['W']
        r['topp'] = r['sprang'] = float('nan')
        if r['namn'] in overg:
            _, mm = overgang(dict(GREP)[r['namn']], n=5)
            r['topp'] = mm['topp']; r['sprang'] = mm['sprang']
    L = ['| Nr. | Lysgrep | W for alle tre | Bind | Mot auget ved W3 | Felt, lx | Vegg, lx | Ansikt, lx | Stemning: auge | Stemning: vegg | Likskap | Topp | Sprang | Strekk | Rift | Skugge inn | Skugge ut |',
         '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for i, r in enumerate(rader):
        L.append(f"| {i+1} | {r['namn']} | {r['W3']:.2f} | {r['bind']} | {r['auge3']:.0f} | {r['felt']:.0f} | {r['vegg']:.0f} | {r['ansikt']:.0f} | "
                 f"{r['s_auge']:.0f} | {r['s_vegg']:.0f} | {r['likskap']:.2f} | {r['topp']:.2f} | {r['sprang']:.2f} | {r['strekk']*100:.2f} % | {r['rift']:.2f} | {r['sk_inn']*100:.0f} % | {r['sk_ut']*100:.0f} % |")
    L.append('')
    L.append('W for alle tre: watt som gjev 350 lx på feltet, 100 lx på veggen og 50 lx på ansiktet samstundes. Bind: kravet som avgjer. '
             'Taket er 7,5 W. Mot auget ved W3: cd/m² skalert til den watten. Topp og sprang: frå overgang() med fem steg. '
             'Rift: største hopp i mm mellom to punkt som ligg 1 mm frå kvarandre i det flate arket (0 er heilt ark). '
             'Skugge inn og ut: del av lyset som arket eigentleg skuggar for seg sjølv, og som lysmotoren ikkje trekkjer frå.')
    open(os.path.join(mappe, 'ekstra.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    return rader

def vis(rader):
    for r in rader:
        print('%-11s W3 %5.2f (%-6s) auge3 %5.0f | felt %4.0f U %.2f W350 %.2f vegg %3.0f ans %3.0f auge %5.0f | s: auge %5.0f felt %3.0f vegg %3.0f | lik %.2f topp %.2f spr %.2f | strekk %.3f rift %.2f sk %.2f/%.2f'
              % (r['namn'], r['W3'], r['bind'], r['auge3'], r['felt'], r['jamnheit'], r['W350'], r['vegg'], r['ansikt'], r['auge'],
                 r['s_auge'], r['s_felt'], r['s_vegg'], r['likskap'], r['topp'], r['sprang'], r['strekk'], r['rift'], r['sk_inn'], r['sk_ut']))

# Siste generasjon er generasjon 3. Dei tre beste (sjå funn.md) får par-bilete.
SISTE = GEN3
OVERG = ('bok', 'Z-samla', 'Z-spreidd', 'vifte', 'spel', 'bolgje', 'tak-vipp', 'Z-vipp', 'tak-sveip',
         'rund-bok', 'liten-bok', 'fresnel-floy')
TRE = ('Z-spreidd', 'rund-bok', 'tak-vipp')

def lag_par(px=240):
    for nm in TRE:
        par(dict(SISTE)[nm], os.path.join(HER, 'par-%s.png' % nm), px=px, ss=1, steg=(0, 0.5, 1))
        print('par', nm, 'ferdig')

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception: pass
    a = sys.argv[1:]
    if '--gen' in a:
        g = a[a.index('--gen') + 1]
        vis(kjor({'1': GEN1, '2': GEN2, '3': GEN3}[g], os.path.join(HER, 'gen' + g), px=0))
    elif '--radius' in a:
        radiusserie(HER)
    elif '--par' in a:
        lag_par()
    else:
        vis(kjor(SISTE, HER, px=200, overg=OVERG))          # tal.md, tal.csv, ekstra.md og bretta med px=200
        lag_par()
