# -*- coding: utf-8 -*-
"""Familien KLIPP: omriss og opningar. Bygd på konsept/reflektor/_mal.py.

  python familie.py            tal.md, tal.csv, klipp-tal.md og bretta (px 200) for siste generasjon
  python familie.py --tal      berre tala (px 0)
  python familie.py --par      par-NAMN.png for dei tre beste

Motoren i denne fila: parametrar inn (oppstilling, klipp, flikar, lag, rørsle), geometri ut.
Produksjonsvilkåra bur her: arket er flatt eller sylindrisk bøygd (strekk 0), kvart lag er eitt
samanhengande stykke (delar = 1), og minste bru er minst 4 mm.
Eit lysgrep er g(t) -> (lys, kropp). t = 0 er stemning, t = 1 er arbeid.
"""
import sys, os
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HER, '..', '..', 'lysskisse'))
from lysskisse import *
from scipy import ndimage

R0 = 0.125                 # arket er ei skive på Ø 25 cm om ikkje anna er sagt
N_FLIS = 24                # fliser tvers over arket (om lag 1 cm)
DELT = 3                   # kjelda er ei opning på Ø 4 cm: tre punkt i staden for eitt (sjå funn.md, feil i motoren)

# ------------------------------------------------------------------ oppstillingar
# kp: kjelda (i foten). c: senteret i arket. Lyset som går gjennom klippet, held fram langs kp -> c.
OPPST = {
    'fot':  dict(kp=b(0.47, 0.48, 0.05), c=b(0.47, 0.40, 0.41)),   # malen: kjelda rett under, klippet går til taket
    'fram': dict(kp=b(0.47, 0.15, 0.05), c=b(0.47, 0.40, 0.33)),   # kjelda 25 cm framfor arket, klippet går til veggen
    'hog':  dict(kp=b(0.47, 0.10, 0.05), c=b(0.47, 0.40, 0.41)),   # same, høgare ark og lengre fot
    'skra': dict(kp=b(0.66, 0.22, 0.05), c=b(0.44, 0.40, 0.38)),   # kjelda til høgre framme, klippet går mot veggen over skjermen
}

def ramme(c, n, rull=0.0):
    """Same akser som ark() brukar: (ex, ey, ez)."""
    ez = nrm(n); ex0, ey0 = ortho(ez)
    cr, sr = math.cos(math.radians(rull)), math.sin(math.radians(rull))
    ex = cr * ex0 + sr * ey0
    return ex, np.cross(ez, ex), ez

def kjelde(kp, mot, W, K, spreiing=10, delt=DELT):
    """Kjelda i foten: opning Ø 4 cm i ein brønn. Delt i punkt, så halvskuggen bak klippet blir med."""
    if delt == 1:
        return [straale(kp, mot, W * LMW_KJELDE, K, spreiing=spreiing, kutt=2 * spreiing, opning=0.02, bronn=40)]
    u, v = ortho(nrm(mot - kp)); ut = []
    for a in np.arange(delt) * 2 * PI / delt + 0.3:
        o = 0.013 * (math.cos(a) * u + math.sin(a) * v)
        ut.append(straale(kp + o, mot + o, W * LMW_KJELDE / delt, K, spreiing=spreiing, kutt=2 * spreiing,
                          opning=0.02 / math.sqrt(delt), bronn=40))
    return ut

def _bokfor(ks, arka):
    """Motoren skriv over lm_ut når fleire ark deler kjelde. Her blir spillet rekna samla."""
    rest = max(sum(k.lm for k in ks) - sum(a.lm_inn for a in arka), 0.0)
    for k in ks: k.lm_ut = rest / len(ks)

def lampe(t, klipp=None, opp='fram', kp=None, c=None, mot=None, sikt=(0.0, 0.0), storleik=2 * R0, form=None,
          side=SATIN, bakside=MORK, rull=0.0, spreiing=10, flikar=(), n=N_FLIS, delt=DELT, W=None, fresnel=None,
          lag2=None, tone=None, lag=None, ekstra=None):
    """Kjelde i foten lyser på eit klipt ark. Det som er klipt bort, slepper lyset vidare.
    klipp(u, v) -> True der arket finst. sikt: kvar på arket (u, v) strålen siktar.
    flikar: liste av dict(u, v, b, l, mal=punkt eller vinkel=grader og akse=grader, side, rund). Flika er klipt på tre sider
            og bøygd ut mot kjelda. Ho er eit eige lite ark, og holet etter ho slepper lys gjennom.
    lag2: dict(klipp=..., side=...) er eit anna materiale i same plan (til dømes matt maske oppå fresnelplata).
    lag: dei fysiske arka (liste av klipp) når klippet er sett saman av fleire lag. Til produksjonsanalysen.
    ekstra(ks, arka, ramme) -> (lys, kropp) legg til strøk og lekamar, til dømes ei linse bak holet."""
    W0, K = watt(t); W = W0 if W is None else W
    o = OPPST[opp]; kp = o['kp'] if kp is None else kp; c = o['c'] if c is None else c
    mot = FELT if mot is None else mot
    nn = nrm(nrm(kp - c) + nrm(mot - c))
    ex, ey, ez = ramme(c, nn, rull)
    fx, fy, _ = ramme(c, nn, 0.0)                         # sikt er gjeve i den udreia ramma: strålen står fast når skiva blir dreia
    sp = c + sikt[0] * fx + sikt[1] * fy
    ks = kjelde(kp, sp, W, K, spreiing, delt)
    hol = []; fl = []
    for f in flikar:
        H = c + f['u'] * ex + f['v'] * ey
        if 'mal' in f:
            nt = nrm(nrm(kp - H) + nrm(np.asarray(f['mal'], float) - H))
            m = nt - (nt @ ez) * ez; alfa = math.atan2(np.linalg.norm(m), nt @ ez); m = nrm(m)
        else:
            alfa = math.radians(f['vinkel']); ak = math.radians(f.get('akse', 0.0))
            a0 = math.cos(ak) * ex + math.sin(ak) * ey; m = -np.cross(ez, a0)
        a = np.cross(ez, m); e0 = -m                       # hengsla går langs a, flika ligg flat langs e0
        e = math.cos(alfa) * e0 + math.sin(alfa) * ez; nf = math.cos(alfa) * ez + math.sin(alfa) * m
        bb, ll = f['b'], f['l']
        hol.append((f['u'], f['v'], (a @ ex, a @ ey), (e0 @ ex, e0 @ ey), bb, ll, f.get('rund', True)))
        vsign = float(np.cross(nf, a) @ e)
        if f.get('rund', True):
            kf = (lambda sg, bb, ll: (lambda u, v: (sg * v < ll / 2 - bb / 2) | (u * u + (sg * v - (ll / 2 - bb / 2)) ** 2 <= (bb / 2) ** 2)))(vsign, bb, ll)
        else: kf = None
        fl.append(ark(ks, H + ll / 2 * e, nf, (bb, ll), klipp=kf, n=max(6, int(round(bb / 0.008))), opp=np.cross(nf, a),
                      framside=f.get('side', side), bakside=bakside))
        fl[-1].alfa = math.degrees(alfa)
    def kl(u, v):
        hald = np.ones(np.shape(u), bool) if klipp is None else np.asarray(klipp(u, v), bool)
        for (u0, v0, a2, e2, bb, ll, rund) in hol:
            s = (u - u0) * a2[0] + (v - v0) * a2[1]; q = (u - u0) * e2[0] + (v - v0) * e2[1]
            inne = (np.abs(s) <= bb / 2) & (q >= 0) & (q <= ll)
            if rund: inne &= (q <= ll - bb / 2) | (s * s + (q - (ll - bb / 2)) ** 2 <= (bb / 2) ** 2)
            hald &= ~inne
        return hald
    arka = []
    if fresnel is None:
        arka.append(ark(ks, c, nn, storleik, form=form, klipp=kl, n=n, rull=rull, framside=side, bakside=bakside, tone=tone))
    else:
        arka.append(ark(ks, c, nn, storleik, klipp=kl, n=max(n, 30), rull=rull, fresnel=fresnel['f'],
                        framside=dict(rd=0.03, rs=0.85, sigma=fresnel.get('spreiing', 2.5)), bakside=bakside))
    if lag2 is not None:
        arka.append(ark(ks, c, nn, lag2.get('storleik', storleik), klipp=lag2['klipp'], n=n, rull=lag2.get('rull', rull),
                        framside=lag2.get('side', MATT), bakside=lag2.get('bakside', bakside)))
    arka[0].lag = [kl] if lag is None else list(lag)       # til analyse(): dei fysiske arka
    arka[0].storleik = storleik; arka[0].avstand = float(np.hypot(*(c - kp)[:2]))
    arka += fl
    _bokfor(ks, arka)
    # svart kropp: fot under kjelda og ei stong langs sida av strålen opp til arkkanten
    hs = c + (np.max(storleik) / 2) * (ex if ex[0] > 0 else -ex)
    fot = b(kp[0], kp[1], 0)
    kropp = [syl(fot, np.array([kp[0], kp[1], kp[2] - 0.004]), 0.05),
             syl(np.array([kp[0] + 0.045, kp[1], kp[2] - 0.01]), hs, 0.004)]
    lys = ks + arka
    if ekstra is not None:
        l2, k2 = ekstra(ks, arka, (c, ex, ey, ez)); lys += l2; kropp += k2
    return lys, kropp

# ------------------------------------------------------------------ klippa (u, v i meter i arket)
# I oppstillinga «fram» peikar +v opp og fram mot brukaren, -v ned og bak mot veggen. +u peikar til høgre og fram.

def heil(u, v): return np.ones(np.shape(u), bool)
def ring(r, u0=0.0, v0=0.0): return lambda u, v: (u - u0) ** 2 + (v - v0) ** 2 > r * r
def maane(r, du=0.0, dv=0.0): return lambda u, v: (u - du) ** 2 + (v - dv) ** 2 > r * r       # bit av ei skive: halvmåne
def halv(v0=0.0, vinkel=0.0):
    c, s = math.cos(math.radians(vinkel)), math.sin(math.radians(vinkel))
    return lambda u, v: (-s * u + c * v) > v0
def blad(breidd, vinkel=0.0):
    """To sirkelbogar som møtest i spiss: lengd 2·R0, breidd som oppgjeve."""
    h = breidd / 2; Rb = (R0 * R0 + h * h) / (2 * h); d = Rb - h
    c, s = math.cos(math.radians(vinkel)), math.sin(math.radians(vinkel))
    def f(u, v):
        x = c * u + s * v; y = -s * u + c * v
        return (x * x + (y - d) ** 2 < Rb * Rb) & (x * x + (y + d) ** 2 < Rb * Rb)
    return f
def stripe(breidd, vinkel=0.0, v0=0.0):
    c, s = math.cos(math.radians(vinkel)), math.sin(math.radians(vinkel))
    return lambda u, v: np.abs(-s * u + c * v - v0) < breidd / 2
def sektor(opning, retning=-90.0):
    """Kakestykke klipt ut: opning i grader, midt i retninga (grader frå +u)."""
    return lambda u, v: np.abs((np.degrees(np.arctan2(v, u)) - retning + 180) % 360 - 180) > opning / 2
def hol(pitch, r, gradert=None):
    """Runde hol i trekantnett. gradert(u, v) -> faktor på radien gjev tettleik som varierer."""
    def f(u, v):
        j = np.round(v / (pitch * 0.866)); uu = u - 0.5 * pitch * (j % 2)
        i = np.round(uu / pitch)
        cu = i * pitch + 0.5 * pitch * (j % 2); cv = j * pitch * 0.866
        rr = r * (gradert(cu, cv) if gradert is not None else 1.0)
        return (u - cu) ** 2 + (v - cv) ** 2 > rr * rr
    return f
def slissar(periode, open_del, vinkel=0.0, fase=0.0, kant=0.012):
    """Parallelle slissar. Ein kant står att rundt, så arket heng saman."""
    c, s = math.cos(math.radians(vinkel)), math.sin(math.radians(vinkel))
    return lambda u, v: (((-s * u + c * v) / periode + fase) % 1.0 >= open_del) | (u * u + v * v > (R0 - kant) ** 2)
def bogar(periode, open_del, bruer=3, bru=0.02, r_min=0.03):
    """Konsentriske bogeslissar. bruer = 0 gjev lause ringar (øyar)."""
    def f(u, v):
        r = np.hypot(u, v); open_ = ((r / periode) % 1.0 < open_del) & (r > r_min) & (r < R0 - 0.01)
        if bruer:
            fi = np.arctan2(v, u); d = np.abs(((fi / (2 * PI / bruer)) + 0.5) % 1.0 - 0.5) * (2 * PI / bruer) * r
            open_ &= d > bru / 2
        return ~open_
    return f
def spiral(omgangar, breidd, r_inn=0.03):
    """Éin spiralsliss frå r_inn til kanten. Arket heng saman og kan dragast ut til ei fjør."""
    def f(u, v):
        r = np.hypot(u, v); fi = np.arctan2(v, u)
        steg = (R0 - 0.012 - r_inn) / omgangar
        x = (r - r_inn - steg * (fi + PI) / (2 * PI)) / steg
        return ~((np.abs(x - np.round(x)) * steg < breidd / 2) & (r > r_inn) & (r < R0 - 0.012))
    return f
def frynser(tal_, djupn, open_del=0.5):
    """Slissar inn frå kanten, som ein kam rundt heile skiva."""
    return lambda u, v: ~((np.hypot(u, v) > R0 - djupn) & (((np.arctan2(v, u) / (2 * PI)) * tal_) % 1.0 < open_del))
def vifte(blad_, open_del, dreiing=0.0, r_inn=0.025):
    """Sektoropningar (som ei luftrist). dreiing i grader."""
    return lambda u, v: ~((((np.degrees(np.arctan2(v, u)) - dreiing) / 360.0 * blad_) % 1.0 < open_del) & (np.hypot(u, v) > r_inn))
def eller(*ks): return lambda u, v: np.logical_or.reduce([np.asarray(k(u, v), bool) for k in ks])
def og(*ks): return lambda u, v: np.logical_and.reduce([np.asarray(k(u, v), bool) for k in ks])
def flytt(k, du=0.0, dv=0.0): return lambda u, v: k(u - du, v - dv)
def drei(k, grader):
    c, s = math.cos(math.radians(grader)), math.sin(math.radians(grader))
    return lambda u, v: k(c * u + s * v, -s * u + c * v)

# ------------------------------------------------------------------ produksjon: kan arket klippast i eitt stykke?

def analyse(lag, storleik=2 * R0, tjukn=0.001, d=0.25, px=0.0005):
    """lag: liste av klipp, eitt per ark. Gjev open del, tal på delar, minste bru, hol, kantlengd og masse.
    delar > 1: lause øyar, kan ikkje klippast av eitt ark. rist: kantlengd delt på omkrinsen av ei heil skive."""
    w = float(np.max(storleik)); x = np.arange(-w / 2, w / 2, px) + px / 2
    U, V = np.meshgrid(x, x, indexing='ij'); ut = dict(open_del=0.0, delar=0, bru=99.0, hol=0, rist=0.0, masse=0.0)
    for k in lag:
        K = (U * U + V * V <= (w / 2) ** 2) if np.ndim(storleik) == 0 else np.ones(U.shape, bool)
        A0 = K.sum()
        if k is not None: K = K & np.asarray(k(U, V), bool)
        ut['open_del'] = max(ut['open_del'], 1 - K.sum() / A0)
        nd = ndimage.label(K)[1]; ut['delar'] = max(ut['delar'], nd)
        bru = 99.0
        for r in (1, 2, 3, 4, 6):                       # erosjon: når deler arket seg?
            kj = np.hypot(*np.mgrid[-r:r + 1, -r:r + 1]) <= r
            E = ndimage.binary_erosion(K, kj); ne = ndimage.label(E)[1]
            stor = np.sum(np.bincount(ndimage.label(E)[0].ravel())[1:] > 0.002 * A0)
            if stor > nd: bru = 2 * r * px * 1000; break
        ut['bru'] = min(ut['bru'], bru)
        Kp = np.pad(~K, 1, constant_values=True); lab, nl = ndimage.label(Kp)
        ut['hol'] += nl - 1
        kant = (np.abs(np.diff(K.astype(int), axis=0)).sum() + np.abs(np.diff(K.astype(int), axis=1)).sum()) * px * PI / 4
        kant += (K[0].sum() + K[-1].sum() + K[:, 0].sum() + K[:, -1].sum()) * px
        ut['rist'] = max(ut['rist'], kant / (PI * w))
        ut['masse'] += K.sum() * px * px * tjukn * 2700
    # velt: fot 0,85 kg med radius 6 cm, stong i aluminium Ø 8 mm, arket d meter vassrett frå fotsenteret
    stong = 0.136 * math.hypot(d, 0.3)
    ut['velt'] = 0.85 * 0.06 / max(ut['masse'] * max(d - 0.06, 0) + stong * max(d / 2 - 0.06, 0), 1e-6)
    return ut

# ------------------------------------------------------------------ køyring

def skriv_klipptal(GREP, INFO, rader, mappe, overg=None):
    """Tilleggstal for familien: forholdet vegg/felt, veggen ved 350 lx, produksjon og lesbarheit."""
    L = ['| Nr. | Lysgrep | Vegg/felt | Vegg ved 350 lx | W for 350 lx | Open del | Delar | Minste bru, mm | Hol | Kant/omkrins | Ark, g | Velt | Topp | Sprang |',
         '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    ut = []
    for i, r in enumerate(rader):
        hovud = [l for l in dict(GREP)[r['namn']](1.0)[0] if isinstance(l, Ark)][0]
        a = analyse(hovud.lag, hovud.storleik, d=hovud.avstand)
        a.update(INFO.get(r['namn'], {}))
        o = (overg or {}).get(r['namn'])
        rad = dict(namn=r['namn'], forhold=r['vegg'] / max(r['felt'], 1e-9), vegg350=r['vegg'] * 350 / max(r['felt'], 1e-9), **a)
        ut.append(rad)
        L.append(f"| {i+1} | {r['namn']} | {rad['forhold']:.2f} | {rad['vegg350']:.0f} | {r['W350']:.2f} | {a['open_del']*100:.0f} % | {a['delar']} | "
                 f"{('over 12' if a['bru'] > 90 else '%.0f' % a['bru'])} | {a['hol']} | {a['rist']:.1f} | {a['masse']*1000:.0f} | {a['velt']:.1f} | "
                 f"{('%.2f' % o['topp']) if o else ''} | {('%.2f' % o['sprang']) if o else ''} |")
    L.append('')
    L.append('Lesenøkkel. Vegg/felt: F6 saman med F3 krev 0,29 til 0,43 (100 til 150 lx på veggen ved 350 lx på feltet). '
             'Open del: areal klipt bort av ei heil skive. Delar: over 1 er lause øyar, og arket kan ikkje klippast i eitt stykke. '
             'Minste bru: smalaste stad der arket heng saman. Hol: opningar som ikkje når kanten. Kant/omkrins: lengda av alle klippkantar delt på omkrinsen '
             'av ei heil skive (1,0 er ei heil skive, høge tal les som rist). Ark: masse i 1 mm aluminium. '
             'Velt: stabiliserande moment delt på veltande (fot 0,85 kg, radius 6 cm), under 1,5 er for lite. Topp og sprang: frå overgang(), sjå API.md.')
    open(os.path.join(mappe, 'klipp-tal.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    return ut

def kjor(GREP, INFO, mappe, px=0, overgangar=()):
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    rader = familie(GREP, mappe, px=px)
    og_ = {}
    for namn in overgangar:
        _, m = overgang(dict(GREP)[namn], n=5); og_[namn] = m
    kt = skriv_klipptal(GREP, INFO, rader, mappe, og_)
    for r, k in zip(rader, kt):
        print('%-12s felt %4.0f U %.2f W350 %5.2f vegg %4.0f v/f %.2f ansikt %3.0f auge %5.0f | stemn: auge %5.0f felt %4.0f vegg %4.0f | lik %.2f strekk %.2f%% | open %2.0f%% delar %d bru %s hol %d rist %.1f velt %.1f'
              % (r['namn'], r['felt'], r['jamnheit'], r['W350'], r['vegg'], k['forhold'], r['ansikt'], r['auge'], r['s_auge'], r['s_felt'], r['s_vegg'],
                 r['likskap'], r['strekk'] * 100, k['open_del'] * 100, k['delar'], ('>12' if k['bru'] > 90 else '%.0f' % k['bru']), k['hol'], k['rist'], k['velt']))
    for namn, m in og_.items():
        print('overgang %-10s topp %.2f sprang %.2f jamn auke %.2f  auge %s  felt %s  vegg %s'
              % (namn, m['topp'], m['sprang'], m['jamn_auke'], [round(x) for x in m['auge']], [round(x) for x in m['felt']], [round(x) for x in m['vegg']]))
    return rader, kt

# ------------------------------------------------------------------ siste generasjon (blir fylt inn etter generasjon 1 og 2)
GREP = []
INFO = {}
BESTE = []

if __name__ == '__main__':
    a = sys.argv[1:]
    if '--par' in a:
        for namn in BESTE:
            par(dict(GREP)[namn], os.path.join(HER, 'par-%s.png' % namn), px=240, ss=1, steg=(0, 0.5, 1))
    else:
        kjor(GREP, INFO, HER, px=(0 if '--tal' in a else 200), overgangar=BESTE)
