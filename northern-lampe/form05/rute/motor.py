# -*- coding: utf-8 -*-
"""
motor.py  ·  form05/rute «Lysrute»: lampa ER vindauget

Ei rute som sjølv lyser: LED-ar i kanten, ei lysleiarplate i PMMA (ANTAKING, finst ikkje i byggjesettet),
ein diffusor og éin eller to prismefilmar. Filmen er strålespora per bølgjelengd med film.py frå konsept/film.
Rommet, watten og tala er dei same som for A, B og C (konsept/tre/tre.py og konsept/lysskisse/lysskisse.py).

Ein kropp er ein spesifikasjon med fire identitetsparametrar og éin gest (sjå KROPPAR nedst i fila):
  stotte   'telt' (rund fot, bøygd arm, sylinder) · 'klemme' (klemme på bordkanten, stolpe, arm)
           · 'stolpe' (stolpe på liten fot) · 'fot' (fot under skjermen, stolpe bak skjermen)
  ruter    liste med ruter. Kvar rute har breidd w, djupn h, hengsel (x, y, h over bordet), fraa 'kant' (heng frå
           hengslet) eller 'midt' (dreier om midtlina), og vinkel (stemning, arbeid) i grader:
           0 liggjande og lyser ned, 90 ståande og lyser mot brukaren, 180 liggjande og lyser opp,
           -90 heng ned og lyser mot veggen. Skrå er alt imellom. To ruter med kvar sin vinkel er «delt i to».
  rille    'vassrett' (rillene langs x, kanten med LED-ane) · 'loddrett' (langs y, vekk frå kanten) · 'kryss' · 'ingen'
  kjelde   'kant' (kantlys i lysleiarplate) · 'bak' (dioderekkje bak arket, i kvit boks med diffusor)
  bak      del av lyset som går ut baksida (0 med kvit reflektor bak)
Gesten er at vinkelen går frå stemning til arbeid medan watten går frå 1,25 til 5 W (som A, B og C).

Køyr med låg prioritet, éin prosess om gongen (under 6 min kvar):
  python -B motor.py kalib          filmen mot 00-vindauge-utan-linse.md, og luminanstabellane (.cache/tab_*.npz)
  python -B motor.py tretest        tre.rekn('A') mot konsept/tre/tal.md
  python -B motor.py skann          endepunkta (stemning, arbeid) for variantar av T og K
  python -B motor.py rekn T|K       heile overgangen med tre.rekn, og augevolum, spegling og veggsnitt på 2 cm
  python -B motor.py striper        stripene og regnbogebandet i stemning
  python -B motor.py ut             ies_*.ies og scene.json
  python -B studie.py               lysstudie.png
Alle tal blir skrivne til tal.json fortløpande, og ei linje per køyring til logg.md.
"""
import os, sys, math, json, time, copy
HER = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('NUMBA_CACHE_DIR', os.path.join(os.path.dirname(HER), '.numba'))
sys.dont_write_bytecode = True


def _skaansam():
    """Låg prioritet, som _skaansam i modell/byggjesett/rendre_blender.py."""
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetPriorityClass(k.GetCurrentProcess(), 0x40)          # IDLE_PRIORITY_CLASS
        k.SetProcessAffinityMask(k.GetCurrentProcess(), 0xFC)
    except Exception:
        pass
_skaansam()

import numpy as np
from scipy.ndimage import map_coordinates, gaussian_filter

ROT = os.path.normpath(os.path.join(HER, '..', '..', '..'))
for d in (('konsept', 'film'), ('konsept', 'tre'), ('konsept', 'lysskisse')):
    p = os.path.join(ROT, *d)
    if p not in sys.path: sys.path.insert(0, p)
from film import Film, prisme, analytisk_splitt
import lysskisse as ls
from lysskisse import b, ZB, YV, AUGE, nrm

CACHE = os.path.join(HER, '.cache'); os.makedirs(CACHE, exist_ok=True)
TALFIL = os.path.join(HER, 'tal.json')
LOGG = os.path.join(HER, 'logg.md')
ARKET = os.path.join(ROT, 'konsept', 'vindauge', 'film', 'arket.md')

# ------------------------------------------------------------------ lagring fortløpande

def _j(o):
    if isinstance(o, np.ndarray): return o.tolist()
    if isinstance(o, (np.floating, np.integer)): return o.item()
    if isinstance(o, np.bool_): return bool(o)
    return str(o)

def lagre(nokkel, verdi):
    d = json.load(open(TALFIL, encoding='utf-8')) if os.path.exists(TALFIL) else {}
    d[nokkel] = verdi
    json.dump(d, open(TALFIL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=_j)

def les(nokkel, standard=None):
    return json.load(open(TALFIL, encoding='utf-8')).get(nokkel, standard) if os.path.exists(TALFIL) else standard

def logg(tekst):
    with open(LOGG, 'a', encoding='utf-8') as f:
        f.write('- ' + time.strftime('%H.%M') + ' ' + tekst + '\n')

def r2(x, n=2):
    return round(float(x), n)

# ------------------------------------------------------------------ filmen

def filmprofil():
    """Profilen frå konsept/vindauge/film/arket.md om dommen ligg der, elles det ideelle 90°-prismet (ANTAKING)."""
    if os.path.exists(ARKET) and not os.environ.get('RUTE_IDEELL'):
        raise SystemExit('arket.md finst no: les profilen derifrå og set han inn i filmprofil() før du reknar vidare.')
    return Film(prisme(90.0), n_d=1.59, abbe=30.0), 'ideelt 90°-prisme, n_d 1,59, Abbe 30 (ANTAKING: arket.md fanst ikkje)'

FILM, FILMTEKST = filmprofil()
PITCH_UM = 50.0      # ANTAKING: vanleg pitch for prismefilm i skjermar (24 til 50 µm). Rekninga er skalafri.

# ------------------------------------------------------------------ lysmotoren: tal som ikkje er målte

ETA_KOPL = 0.85      # ANTAKING: del av LED-lyset som kjem inn i plata gjennom kanten
ETA_LEIAR = 0.85     # ANTAKING: absorpsjon i PMMA og tap i endekanten på 200 mm veg
RC = 0.90            # kalibrert mot konsept/film/rute.py (rho 0,90): del av lyset filmane kastar attende som kjem ut att av huset
T_SPREIAR = 0.90     # som rute.py: matt spreiar utan film slepper ut 90 %

KJELDE = {'kant': dict(namn='kantlys i lysleiarplate (PMMA 4 mm)', eta_inn=ETA_KOPL * ETA_LEIAR, djupn=0.006),
          'bak': dict(namn='dioderekkje bak arket, kvitt hus og spreiar (som rute.py)', eta_inn=1.0, djupn=0.025)}
RILLE = {'ingen': [], 'vassrett': ['x'], 'loddrett': ['y'], 'kryss': ['x', 'y'], 'kryss-v': ['y', 'x']}
# kryss: det øvste arket har loddrette riller (mot auget). kryss-v: det øvste har vassrette. tab_kryss.npz er rekna som kryss-v.

LAMS = np.array([430., 470., 510., 550., 590., 630., 670.])
NB = 81                          # retningstabell i retningscosinus (u, v) over [-1, 1]
DU = 2.0 / NB

def _cmf(lam):
    """CIE 1931 (analytisk tilnærming, same som konsept/film/kast.py)."""
    def g(l, mu, s1, s2):
        s = np.where(l < mu, s1, s2)
        return np.exp(-0.5 * ((l - mu) / s) ** 2)
    x = 1.056 * g(lam, 599.8, 37.9, 31.0) + 0.362 * g(lam, 442.0, 16.0, 26.7) - 0.065 * g(lam, 501.1, 20.4, 26.2)
    y = 0.821 * g(lam, 568.8, 46.9, 40.5) + 0.286 * g(lam, 530.9, 16.3, 31.1)
    z = 1.217 * g(lam, 437.0, 11.8, 36.0) + 0.681 * g(lam, 459.0, 26.0, 13.8)
    return np.stack([x, y, z], 1)
XYZ_RGB = np.array([[3.2406, -1.5372, -0.4986], [-0.9689, 1.8758, 0.0415], [0.0557, -0.2040, 1.0570]])

def planck(lam, K):
    l = np.asarray(lam, float) * 1e-9
    return 1.0 / (l ** 5 * (np.exp(1.4388e-2 / (l * K)) - 1.0))

def vekter(K=2700):
    """Fotometrisk vekt per bølgjelengd: V(λ) gonger spekteret (svart lekam ved K, ANTAKING)."""
    w = _cmf(LAMS)[:, 1] * planck(LAMS, K)
    return w / w.sum()

def lambert(N, rng):
    u1 = rng.random(N); u2 = rng.random(N)
    s = np.sqrt(u1); f = 2 * math.pi * u2
    return np.stack([s * np.cos(f), s * np.sin(f), np.sqrt(1 - u1)], 1)

def _M(rille):
    """Filmaksane i rutekoordinatar (x langs kanten med LED-ane, y vekk frå kanten, z ut). Prismesida vender ut (+z)."""
    fz = np.array([0, 0, 1.0])
    fy = np.array([1.0, 0, 0]) if rille == 'x' else np.array([0, 1.0, 0])
    return np.stack([np.cross(fy, fz), fy, fz])

def stabel(film, rillar, Rc=RC, lam=550.0, N=150_000, frø=1, maxsteg=80):
    """Monte Carlo gjennom kavitet og filmar. Lyset kjem lambertsk ut av diffusoren (ANTAKING). Det filmane kastar attende,
    går ned i kaviteten, blir kvitt att med Rc og prøver på nytt. Gjev (Ltab, rekneskap): Ltab er luminansen per
    retningscelle, normert til éin lumen inn i filmstabelen første gong, slik at integralet av Ltab du dv er verknadsgraden."""
    rng = np.random.default_rng(frø)
    Ms = [_M(r) for r in rillar]; m = len(Ms)
    kant = np.linspace(-1, 1, NB + 1)
    H = np.zeros((NB, NB)); ut = 0.0; tapt = 0.0; kav = 0.0
    D = lambert(N, rng); w = np.ones(N); i = np.zeros(N, int)
    for steg in range(maxsteg):
        e = i >= m
        if e.any():
            H += np.histogram2d(D[e, 0], D[e, 1], bins=[kant, kant], weights=w[e])[0]
            ut += w[e].sum()
            D, w, i = D[~e], w[~e], i[~e]
        if not len(w): break
        k = i == -1
        if k.any():
            kav += (w[k] * (1 - Rc)).sum(); w[k] *= Rc
            D[k] = lambert(int(k.sum()), rng); i[k] = 0
        for j in range(m):
            s = np.flatnonzero(i == j)
            if not len(s): continue
            Do, st = film.spor(D[s] @ Ms[j].T, lam)
            Dp = Do @ Ms[j]
            tapt += w[s[st == 0]].sum(); w[s[st == 0]] = 0.0
            D[s] = Dp
            i[s] = np.where(Dp[:, 2] > 0, j + 1, j - 1)
        hald = w > 1e-4
        tapt += w[~hald].sum()
        D, w, i = D[hald], w[hald], i[hald]
        if not len(w): break
    tapt += w.sum()
    L = H / (N * DU * DU)
    return L, dict(ut=ut / N, kavitet=kav / N, tapt=tapt / N)

def oppslag(tab, u, v):
    iu = (np.asarray(u) + 1) / DU - 0.5; iv = (np.asarray(v) + 1) / DU - 0.5
    return map_coordinates(tab, [np.ravel(iu), np.ravel(iv)], order=1, mode='nearest').reshape(np.shape(u))

def last_motor(kjelde, rille):
    """Luminanstabellen for kjelde og rilleretning. 'loddrett' er 'vassrett' snudd 90° (tabellen transponert)."""
    base = {'loddrett': 'vassrett', 'kryss-v': 'kryss'}.get(rille, rille)
    f = os.path.join(CACHE, 'tab_%s.npz' % base)
    if not os.path.exists(f): raise SystemExit('køyr kalib først')
    z = np.load(f)
    tab_l = z['tab'].transpose(0, 2, 1) if rille in ('loddrett', 'kryss') else z['tab']
    fs = T_SPREIAR if rille == 'ingen' else 1.0
    w = vekter(2700)
    return dict(kjelde=kjelde, rille=rille, namn='%s, %s' % (KJELDE[kjelde]['namn'], {'ingen': 'diffusor utan prismefilm',
                'vassrett': 'éin prismefilm, rillene vassrette', 'loddrett': 'éin prismefilm, rillene loddrette',
                'kryss': 'to prismefilmar i kryss, det øvste loddrett', 'kryss-v': 'to prismefilmar i kryss, det øvste vassrett'}[rille]),
                eta_inn=KJELDE[kjelde]['eta_inn'], tab_l=tab_l * fs, eta_l=z['eta'] * fs,
                tab=(w[:, None, None] * tab_l).sum(0) * fs, eta_stabel=float((w * z['eta']).sum()) * fs)

# ------------------------------------------------------------------ ruta som strøk i lysskisse

class Rute:
    """Ei lysande rute: o er hjørnet, ex langs kanten med LED-ane, ey vekk frå kanten, ez = ex × ey er framsida.
    Framsida har luminansen frå motoren. Baksida lyser lambertsk med delen bak (0 med kvit reflektor bak)."""
    def __init__(s, o, ex, ey, w, h, motor, W, K, bak=0.0, namn='rute', nu=8, nv=4):
        s.ex, s.ey = nrm(np.asarray(ex, float)), nrm(np.asarray(ey, float)); s.ez = nrm(np.cross(s.ex, s.ey))
        s.o = np.asarray(o, float); s.w, s.h = w, h; s.A = w * h
        s.c = s.o + s.ex * w / 2 + s.ey * h / 2
        s.W, s.K, s.motor, s.bak, s.namn = W, K, motor, bak, namn
        s.lm_led = W * ls.LMW_KJELDE
        s.phi_inn = s.lm_led * motor['eta_inn']
        s.phi_ut = s.phi_inn * motor['eta_stabel']
        s.kf = (1 - bak) * s.phi_inn / s.A                    # framsida: L = kf · Ltab(u, v)
        s.Lb = bak * s.phi_ut / (math.pi * s.A)
        s.nu, s.nv = nu, nv
    def L(s, d):
        d = np.atleast_2d(d)
        c = d @ s.ez
        Lf = s.kf * oppslag(s.motor['tab'], d @ s.ex, d @ s.ey)
        return np.where(c > 0, Lf, s.Lb)
    def I(s, d):
        d = np.atleast_2d(d)
        c = d @ s.ez
        Lf = s.kf * oppslag(s.motor['tab'], d @ s.ex, d @ s.ey)
        return s.A * np.where(c > 0, Lf * c, s.Lb * (-c))
    def punkt(s, nu=None, nv=None):
        nu = nu or s.nu; nv = nv or s.nv
        return [s.o + s.ex * s.w * (i + 0.5) / nu + s.ey * s.h * (j + 0.5) / nv for i in range(nu) for j in range(nv)]
    def lys(s):
        prim = ls.Rekt(s.o, s.ex * s.w, s.ey * s.h)
        l = ls.Lys(s.lm_led, s.K, prim, s.punkt(), s.I, s.L, s.namn)
        l.mater = True; l.lm_ut = s.phi_ut; l.rute = s
        return [l]

def L_ruter(ruter, d_fraa):
    """Høgaste luminans frå ruter mot punkt: d_fraa(r) gjev (punkt på ruta, retning mot auget)."""
    return max(float(r.L(d_fraa(r)).max()) for r in ruter)

# ------------------------------------------------------------------ kroppane: rute, støtte, gest

ALU = (0.55, 0.55, 0.56); BURG = (0.30, 0.06, 0.07); GRA = (0.40, 0.38, 0.36); SVARTK = (0.05, 0.05, 0.05)

def rute_pose(r, phi):
    """Hengslet går langs x. phi = 0: ruta ligg og peikar mot brukaren, framsida ned. 90: står, framsida mot brukaren."""
    f = math.radians(phi)
    ex = np.array([1.0, 0, 0]); ey = np.array([0.0, -math.cos(f), math.sin(f)])
    H = b(*r['hengsel'])
    off = (r.get('r', 0.020) + 0.002) if r['fraa'] == 'kant' else -r['h'] / 2
    return H + off * ey - ex * r['w'] / 2, ex, ey

def stotte(spec):
    """Kroppen som ber rutene, som prim til lysskisse (skuggar). Mål i meter."""
    R = spec['ruter']
    xr = max(r['hengsel'][0] + r['w'] / 2 for r in R); xl = min(r['hengsel'][0] - r['w'] / 2 for r in R)
    hx, yc, H = R[0]['hengsel']
    s = spec['stotte']; p = []
    farge = BURG if s == 'telt' else GRA
    if any(r['fraa'] == 'kant' for r in R):          # huset for LED-ane langs hengslet
        p.append(ls.Syl(b(xl - 0.015, yc, H), b(xr + 0.015, yc, H), R[0].get('r', 0.020), rho=farge))
    if s == 'telt':                                     # foten står utanfor feltet (x over 0,30 + radius)
        xa = xr + 0.05; xf = max(xa, 0.44)
        p += [ls.Syl(b(xr + 0.015, yc, H), b(xa + 0.012, yc, H), 0.028, rho=ALU),
              ls.Syl(b(xf, yc, 0.018), b(xa, yc, H - 0.03), 0.010, rho=ALU),
              ls.Syl(b(xf, yc, 0.0), b(xf, yc, 0.018), 0.12, rho=BURG)]
    elif s == 'klemme':
        xs = 0.66
        p += [ls.Syl(b(xr + 0.005, yc, H), b(xs, yc, H), 0.010, rho=GRA),
              ls.Syl(b(xs, yc, 0.0), b(xs, yc, H + 0.015), 0.012, rho=GRA),
              ls.Syl(b(xs, yc, 0.0), b(xs, yc, 0.01), 0.03, rho=GRA)]
    elif s == 'stolpe':
        xs = xr + 0.06
        p += [ls.Syl(b(xr + 0.005, yc, H), b(xs, yc, H), 0.010, rho=GRA),
              ls.Syl(b(xs, yc, 0.0), b(xs, yc, H + 0.015), 0.012, rho=GRA),
              ls.Syl(b(xs, yc, 0.0), b(xs, yc, 0.012), 0.08, rho=GRA)]
    elif s == 'fot':
        p += [ls.Syl(b(0.0, 0.52, 0.0), b(0.0, 0.52, 0.008), 0.10, rho=GRA),
              ls.Syl(b(0.0, 0.58, 0.0), b(0.0, 0.58, H), 0.012, rho=GRA),
              ls.Syl(b(0.0, 0.58, H), b(0.0, yc + 0.02, H), 0.010, rho=GRA)]
    return p

def watt_k(t):
    """Same watt som A, B og C (1,25 W til 5 W), men 2200 K i stemning og 2700 K i arbeid (oppgåva)."""
    return 1.25 * 4.0 ** float(t), 2200.0 + 500.0 * float(t)

def bygg(spec, t, W=None, K=None):
    """Ruter (Rute) og kropp (prim) for kroppen spec ved steg t (0 stemning, 1 arbeid)."""
    W0, K0 = watt_k(t)
    W = W0 if W is None else W; K = K0 if K is None else K
    M = last_motor(spec['kjelde'], spec['rille'])
    A = sum(r['w'] * r['h'] for r in spec['ruter'])
    ruter, kropp = [], stotte(spec)
    q = spec.get('bakstripe', 0.0)
    if q > 0:                                           # stripe dioder på hengslet, vend mot veggen bak skjermen (som rute.py)
        R0 = spec['ruter'][0]; sn = nrm(np.array([0.0, 1.0, -0.3])); xr = max(r['hengsel'][0] + r['w'] / 2 for r in spec['ruter'])
        xl = min(r['hengsel'][0] - r['w'] / 2 for r in spec['ruter'])
        fl = ls.flate(b(*R0['hengsel']) + sn * (R0.get('r', 0.012) + 0.004), sn, (xr - xl, 0.02), q * W * ls.LMW_KJELDE * 0.9, K, opp=(0, 0, 1))
        fl.lm_ut = fl.lm; fl.lm = q * W * ls.LMW_KJELDE; fl.mater = True
        stripe = [fl]; W = W * (1 - q)
    else:
        stripe = []
    for r in spec['ruter']:
        phi = r['vinkel'][0] + (r['vinkel'][1] - r['vinkel'][0]) * float(t)
        o, ex, ey = rute_pose(r, phi)
        ru = Rute(o, ex, ey, r['w'], r['h'], M, W * r['w'] * r['h'] / A, K, spec.get('bak', 0.0), spec['namn'])
        ruter.append(ru)
        if spec['kjelde'] == 'bak':                     # boksen bak arket
            d = KJELDE['bak']['djupn']
            kropp.append(ls.Rekt(o - d * ru.ez, ex * r['w'], ey * r['h'], rho=SVARTK))
    bygg.stripe = stripe
    return ruter, kropp

def grep(spec):
    def g(t):
        ruter, kr = bygg(spec, t)
        g.siste = ruter
        return sum([r.lys() for r in ruter], []) + bygg.stripe, kr
    return g

def variant(spec, **endr):
    """Kopi av spec med endringar. vinkel=(s, a) og w, h gjeld alle rutene."""
    s = copy.deepcopy(spec)
    for k, v in endr.items():
        if k in ('vinkel', 'w', 'h', 'fraa'):
            for r in s['ruter']: r[k] = v
        else:
            s[k] = v
    return s

# ------------------------------------------------------------------ tal (same rader som tre.rekn)

def rad(s, a):
    f = 350.0 / max(a['E_felt'], 1e-9)
    La = lambda d: max(d['L_lampe'], d['L_flate'])
    return dict(W350=a['W'] * f, jamnheit=a['U'], felt_a=a['E_felt'], bak350=a['E_bak'] * f, vegg350=a['E_vegg'] * f,
                skjerm350=a['E_skjerm'] * f, ansikt350=a['E_ansikt'] * f,
                auge25=max(a['L_auge25'], a['L_flate']) * f, auge47=La(a) * f, auge60=max(a['L_auge60'], a['L_flate']) * f,
                s_W=s['W'], s_felt=s['E_felt'], s_vegg=s['E_vegg'], s_bak=s['E_bak'], s_skjerm=s['E_skjerm'],
                s_auge25=max(s['L_auge25'], s['L_flate']), s_auge47=La(s), s_auge60=max(s['L_auge60'], s['L_flate']),
                s_ansikt=s['E_ansikt'], likskap=ls.likskap(s['_fordeling'], a['_fordeling']), lm_ut_a=a['lm'] * f, lm_ut_s=s['lm'])

def kort(r):
    return ('W350 %.2f U %.2f auge %4.0f/%4.0f/%4.0f bak %3.0f skjerm %3.0f | st: auge %3.0f/%3.0f/%3.0f bak %3.0f felt %3.0f skjerm %3.1f | lik %.2f'
            % (r['W350'], r['jamnheit'], r['auge25'], r['auge47'], r['auge60'], r['bak350'], r['skjerm350'],
               r['s_auge25'], r['s_auge47'], r['s_auge60'], r['s_bak'], r['s_felt'], r['s_skjerm'], r['likskap']))

def bak_fin(lys, kropp, celle=0.02):
    """Veggen bak skjermen som arealsnitt med celler på 2 cm: tal() sitt snitt (10 cm-celler), der det direkte lyset
    er bytt ut med eit fint gitter. Det indirekte lyset er glatt og blir ståande."""
    T = ls.tal(lys, kropp)
    okkl = ls.STATISK + list(kropp) + [l.prim for l in lys]
    R = ls.rom(); kv = R.kart[1]; Pv = R.P[kv.sl]; Nv = R.N[kv.sl]
    mb = (np.abs(Pv[:, 0]) < 0.35) & (Pv[:, 2] > ZB + 0.05) & (Pv[:, 2] < ZB + 0.65)
    Edc = float((ls.E_direkte(Pv[mb], Nv[mb], lys, okkl) @ ls.LUM).mean())
    xs = np.arange(-0.35 + celle / 2, 0.35, celle); zs = ZB + np.arange(0.05 + celle / 2, 0.65, celle)
    P = np.array([[x, YV - 1e-4, z] for x in xs for z in zs]); N = np.tile([0.0, -1.0, 0.0], (len(P), 1))
    Edf = float((ls.E_direkte(P, N, lys, okkl) @ ls.LUM).mean())
    return dict(bak_tal=T['E_bak'], bak_fin=T['E_bak'] - Edc + Edf, felt=T['E_felt'], skjerm=T['E_skjerm'])

AUGEVOLUM = [b(x, y, z) for x in (-0.15, 0.0, 0.15) for y in (-0.15, -0.075, 0.0) for z in (0.25, 0.37, 0.42, 0.47, 0.52, 0.60)]

def augevolum(ruter):
    """Høgaste luminans frå rutene mot auget i volumet ±15 cm sidevegs, 15 cm fram, 25 til 60 cm over bordet.
    Ingen skugge frå kroppen (konservativt). Gjev (maks, punktet)."""
    best = (0.0, None)
    for r in ruter:
        S = np.array(r.punkt(24, 10))
        for E in AUGEVOLUM:
            d = E - S; d /= np.linalg.norm(d, axis=1)[:, None]
            L = float(r.L(d).max())
            if L > best[0]: best = (L, E)
    return best

def spegling(ruter, tiltar=(0, 5, 10, 15, 20)):
    """Luminansen av rutene slik auget ser dei spegla i skjermen, tilta 0 til 20° bakover om underkanten.
    Gjev luminansen før refleksjon per tilt (gang med ρ: 0,04 blank, 0,01 matt)."""
    ut = {}
    auge = [b(x, y, z) for x in (-0.15, 0.0, 0.15) for y in (-0.15, 0.0) for z in (0.37, 0.47, 0.57)]
    for tau in tiltar:
        t = math.radians(tau)
        P0 = b(-0.27, 0.45, 0.11); ex = np.array([1.0, 0, 0]); td = np.array([0.0, math.sin(t), math.cos(t)])
        n = np.array([0.0, -math.cos(t), math.sin(t)])
        best = 0.0
        for r in ruter:
            S = np.array(r.punkt(24, 10))
            for E in auge:
                if (E - P0) @ n <= 0: continue
                Em = E - 2 * ((E - P0) @ n) * n
                Sv = S[(S - P0) @ n > 0]
                if not len(Sv): continue
                dv = Em - Sv
                tt = ((P0 - Sv) @ n) / (dv @ n)
                X = Sv + tt[:, None] * dv
                a = (X - P0) @ ex; bb = (X - P0) @ td
                ok = (tt > 0) & (tt < 1) & (a >= 0) & (a <= 0.54) & (bb >= 0) & (bb <= 0.31)
                if not ok.any(): continue
                d = X[ok] - Sv[ok]; d /= np.linalg.norm(d, axis=1)[:, None]
                best = max(best, float(r.L(d).max()))
        ut[tau] = best
    return ut

# ------------------------------------------------------------------ kommandoane

def k_kalib():
    t0 = time.time()
    f = FILM
    sjekk = {}
    T, R, L = f.lober(0, 0, 550, 'prisme'); sjekk['prisme_0'] = dict(T=r2(T), lober=[(r2(a, 1), r2(d)) for a, d in L[:2]])
    T, R, L = f.lober(0, 0, 550, 'flat'); sjekk['flat_0'] = dict(T=r2(T), R=r2(R))
    T, R, L = f.lober(30, 0, 550, 'flat'); sjekk['flat_30'] = dict(T=r2(T), lober=[(r2(a, 1), r2(d)) for a, d in L[:1]])
    sjekk['farge_450_650'] = [r2(abs(f.lober(0, 0, l, 'prisme')[2][0][0]), 2) for l in (450, 650)]
    sjekk['analytisk_550'] = r2(analytisk_splitt(float(f.n(550))), 2)
    sjekk['maal_frå_00-vindauge'] = 'prisme rett på: ±30,8°, 0,47 kvar, T 0,93; flat rett på: T 0; flat 30°: −0,8°, 0,63; 450/650 nm: 31,75°/30,25°'
    print(json.dumps(sjekk, ensure_ascii=False), flush=True)
    for base in ('ingen', 'vassrett', 'kryss'):
        tabs, etas = [], []
        for lam in LAMS:
            L, rk = stabel(f, RILLE['kryss-v' if base == 'kryss' else base], RC, lam)
            tabs.append(gaussian_filter(L, 0.6)); etas.append(rk['ut'])
        np.savez_compressed(os.path.join(CACHE, 'tab_%s.npz' % base), tab=np.array(tabs), eta=np.array(etas))
    res = {}
    th = np.arange(0, 90, 1.0); vv = np.sin(np.radians(th))
    def halv(p):
        k = np.flatnonzero(p < 0.5); return float(th[k[0]]) if len(k) else 90.0
    for kj in ('kant', 'bak'):
        for ri in ('ingen', 'vassrett', 'kryss'):
            M = last_motor(kj, ri); tab = M['tab']; c = NB // 2; L0 = tab[c, c]
            prof = oppslag(tab, np.zeros_like(vv), vv) / L0; prof_x = oppslag(tab, vv, np.zeros_like(vv)) / L0
            res['%s-%s' % (kj, ri)] = dict(namn=M['namn'], eta_stabel=r2(M['eta_stabel'], 3), eta_total=r2(M['eta_inn'] * M['eta_stabel'], 3),
                                           lm_per_W=r2(100 * M['eta_inn'] * M['eta_stabel'], 1), gain_rett_fram=r2(L0 * math.pi),
                                           halvvinkel_paa_tvers=halv(prof), halvvinkel_langs=halv(prof_x),
                                           profil_paa_tvers_10gr=[r2(x, 3) for x in prof[::10]], profil_langs_10gr=[r2(x, 3) for x in prof_x[::10]])
    lagre('film_sjekk', sjekk); lagre('motor', res)
    logg('kalib (%.0f s) skreiv tab_ingen, tab_vassrett og tab_kryss' % (time.time() - t0))

def k_tretest():
    import tre
    t0 = time.time()
    r = tre.rekn('A')
    venta = dict(W350=2.99, jamnheit=0.62, auge25=1013, auge47=103, bak350=109, skjerm350=115, s_auge25=424, s_bak=131, likskap=0.60)
    avvik = {k: (r2(r[k]), v) for k, v in venta.items()}
    print(avvik, flush=True)
    lagre('tretest_A', dict(rekna_og_talmd=avvik, sekund=r2(time.time() - t0, 0)))
    logg('tretest: tre.rekn(\'A\') gav ' + ', '.join('%s %s (tal.md %s)' % (k, a, v) for k, (a, v) in avvik.items()) + ' på %.0f s' % (time.time() - t0))

def ende(spec):
    return ende_g(grep(spec))

def skannliste():
    """Runde 1 (15.44) hadde foten til Telt inne i feltet (jamnheit 0,01). Runde 2 under har foten utanfor."""
    T, K = KROPPAR['T'], KROPPAR['K']
    return [('T2 kryss 110>0', variant(T, rille='kryss', vinkel=(110, 0))),
            ('T2 kryss 125>0', variant(T, rille='kryss', vinkel=(125, 0))),
            ('T2 kryss 125>0 stripe0.2', variant(T, rille='kryss', vinkel=(125, 0), bakstripe=0.2)),
            ('T2 kryss 125>0 bak0.3', variant(T, rille='kryss', vinkel=(125, 0), bak=0.3)),
            ('K kryss -135>0 stripe0.2', variant(K, rille='kryss', vinkel=(-135, 0), bakstripe=0.2)),
            ('K kryss 180>0 stripe0.2', variant(K, rille='kryss', vinkel=(180, 0), bakstripe=0.2))]

def k_skann():
    t0 = time.time()
    ut = les('skann', {})
    for namn, spec in skannliste():
        if namn in ut: continue
        r = ende(spec)
        ut[namn] = {k: r2(v, 2) for k, v in r.items()}
        print('%-22s %s' % (namn, kort(r)), flush=True)
        lagre('skann', ut)
        logg('skann %s: %s' % (namn, kort(r)))
        if time.time() - t0 > 300: print('stoppar før 6 min, køyr skann att for resten'); break

def k_rekn(kv):
    import tre
    t0 = time.time()
    spec = KROPPAR[kv]
    g = grep(spec)
    tre.KONSEPT[kv] = dict(namn=spec['namn'], g=g)
    r = tre.rekn(kv)
    lagre('rekn_' + kv, {k: (r2(x, 3) if not isinstance(x, (list, str)) else x) for k, x in r.items()})
    print(kv, kort(r), flush=True)
    ekstra = {}
    for t, m in ((0.0, 'stemning'), (1.0, 'arbeid')):
        lys, kr = g(t); ruter = g.siste
        bf = bak_fin(lys, kr)
        f = 350.0 / bf['felt'] if m == 'arbeid' else 1.0
        La, Ea = augevolum(ruter)
        sp = spegling(ruter)
        M = ruter[0].motor
        ekstra[m] = dict(W=r2(sum(x.W for x in ruter) * f, 2), lm_led=r2(sum(x.lm_led for x in ruter) * f, 0), lm_ut=r2(sum(x.phi_ut for x in ruter) * f, 0),
                         L_rute_rett_fram=r2(ruter[0].kf * M['tab'][NB // 2, NB // 2] * f, 0),
                         bak_tal=r2(bf['bak_tal'] * f, 1), bak_fin_2cm=r2(bf['bak_fin'] * f, 1), skjerm=r2(bf['skjerm'] * f, 1),
                         augevolum_maks=r2(La * f, 0), augevolum_punkt_over_bordet=[r2(x, 3) for x in (Ea - b(0, 0, 0))] if Ea is not None else None,
                         spegling_L=dict((str(k), r2(x * f, 0)) for k, x in sp.items()),
                         spegling_blank_004=r2(max(sp.values()) * f * 0.04, 1), spegling_matt_001=r2(max(sp.values()) * f * 0.01, 2))
        print(m, ekstra[m], flush=True)
    lagre('ekstra_' + kv, ekstra)
    logg('rekn %s (%.0f s): %s. Stemning: augevolum %s cd/m², spegling blank %s. Arbeid: %s W, augevolum %s cd/m², bak 2 cm %s lx (tal() %s), spegling blank %s cd/m².' % (
        kv, time.time() - t0, kort(r), ekstra['stemning']['augevolum_maks'], ekstra['stemning']['spegling_blank_004'],
        ekstra['arbeid']['W'], ekstra['arbeid']['augevolum_maks'], ekstra['arbeid']['bak_fin_2cm'], ekstra['arbeid']['bak_tal'], ekstra['arbeid']['spegling_blank_004']))

def k_rutesjekk():
    """Kalibrering mot konsept/film/rute.py (anna økt, pusha 13.11): (a) fordelinga ut av ruta i cd per 1000 lm,
    (b) lampa «over» (klemme som teikna, rute-tal.json) rekna med Rute-klassen her."""
    t0 = time.time()
    import rute as RU
    ut = {}
    for nk, kw in (('vassrett', dict(innside='flat')), ('kryss', dict(innside='flat', lag2='kryss'))):
        F = RU.utfordeling(**kw)
        M = last_motor('bak', nk); v = np.radians(np.arange(0, 90, 10))
        tv = 1000 * oppslag(M['tab'], np.zeros_like(v), np.sin(v)) * np.cos(v)        # på tvers av rillene (v-aksen for rille x)
        lg = 1000 * oppslag(M['tab'], np.sin(v), np.zeros_like(v)) * np.cos(v)
        ut[nk] = dict(verknad=(r2(F['verknad']), r2(M['eta_stabel'])),
                      tvers_rute=[round(1000 * x) for x in RU.profil(F, 'tvers')], tvers_motor=[round(x) for x in tv],
                      langs_rute=[round(1000 * x) for x in RU.profil(F, 'langs')], langs_motor=[round(x) for x in lg])
        print(nk, ut[nk], flush=True)
    M = last_motor('bak', 'vassrett')
    def g(t):
        W, K = ls.watt(t)
        ex = np.array([-1.0, 0, 0]); ey = np.array([0.0, 1.0, 0]); w, h = 0.32, 0.16
        c = b(0.66, 0.40, 0.33) + np.array([-0.16, 0, 0])
        r = Rute(c - ex * w / 2 - ey * h / 2, ex, ey, w, h, M, W, K, 0.0, 'over')
        kr = [ls.Rekt(c + np.array([0, 0, 0.012]) - ex * w / 2 - ey * h / 2, ex * w, ey * h),
              ls.syl(b(0.66, 0.32, 0.33), b(0.66, 0.48, 0.33), 0.012), ls.syl(b(0.69, 0.40, 0.0), b(0.66, 0.40, 0.33), 0.008),
              ls.skive(b(0.69, 0.40, 0.004), (0, 0, 1), 0.10)]
        return r.lys(), kr
    r = ende_g(g)
    fasit = json.load(open(os.path.join(ROT, 'konsept', 'film', 'rute-tal.json'), encoding='utf-8'))['over']
    sam = {k: (r2(r[k], 2), r2(fasit[k], 2)) for k in ('W350', 'jamnheit', 'bak350', 'skjerm350', 'auge25', 'auge47', 's_auge25', 's_auge47', 's_bak', 's_felt')}
    print('over (motor, rute.py):', sam, flush=True)
    lagre('rutesjekk', dict(fordeling_cd_per_1000lm=ut, over_motor_mot_rute=sam, sekund=r2(time.time() - t0, 0)))
    logg('rutesjekk (%.0f s): fordelinga og lampa «over» mot rute.py: %s' % (time.time() - t0, ', '.join('%s %s/%s' % (k, a, b_) for k, (a, b_) in sam.items())))

def ende_g(g):
    s = ls.tal(*g(0.0)); a = ls.tal(*g(1.0))
    return rad(s, a)

# ------------------------------------------------------------------ stripene

def stripekart(w, h, pitch, sigma=None, nx=241, ny=101, y0=0.004):
    """Luminansen i plata (relativ, snitt 1) frå LED-ar i kanten y = 0 med avstand pitch. sigma = None er naken LED
    (lambertsk inn i kanten, ±42° i PMMA, I ∝ cos ψ). Elles ei gaussisk vifte med sigma grader i planet (LED med
    smal innkopling). 2D-modell: fluksen per lengd fell som 1/r, uttaket er jamt (ANTAKING). Speglar i sidekantane."""
    xs = np.linspace(0, w, nx); ys = np.linspace(y0, h, ny)
    X, Y = np.meshgrid(xs, ys, indexing='ij')
    n_led = int(round(w / pitch)); xl = (np.arange(n_led) + 0.5) * (w / n_led)
    xl = np.concatenate([xl, -xl, 2 * w - xl])
    L = np.zeros_like(X)
    for x0 in xl:
        dx = X - x0; r = np.hypot(dx, Y); psi = np.arctan2(dx, Y)
        if sigma is None:
            I = np.where(np.abs(psi) < math.asin(1 / 1.49), np.cos(psi), 0.0)
        else:
            I = np.exp(-0.5 * (np.degrees(psi) / sigma) ** 2)
        L += I / r
    return xs, ys, L / L.mean()

def kontrast(xs, ys, L, y):
    j = int(np.argmin(np.abs(ys - y))); m = (xs > 0.25 * xs[-1]) & (xs < 0.75 * xs[-1])
    p = L[m, j]; return float((p.max() - p.min()) / (p.max() + p.min())), float(p.max() / p.mean())

STRIPER = dict(pitch=0.040, sigma=6.0)      # stemningsrekkja: 12 LED à 0,1 W, vifte 6° (ANTAKING), sjå k_striper

def k_striper(kv='T'):
    t0 = time.time()
    spec = KROPPAR[kv]; R0 = spec['ruter'][0]
    w, h = R0['w'], R0['h']
    variantar = {'arbeid: 60 LED, 8 mm, nakne': (0.008, None), 'stemning: 12 LED, 40 mm, nakne': (0.040, None),
                 'stemning: 12 LED, 40 mm, vifte 6°': (0.040, 6.0), 'stemning: 20 LED, 24 mm, vifte 6°': (0.024, 6.0),
                 'stemning: 12 LED, 40 mm, vifte 3°': (0.040, 3.0)}
    ut = {}
    for namn, (p, s) in variantar.items():
        xs, ys, L = stripekart(w, h, p, s)
        ut[namn] = {('%d mm' % round(y * 1000)): [r2(c, 2), r2(m, 2)] for y in (0.01, 0.03, 0.06, 0.10, 0.15, 0.19)
                    for c, m in [kontrast(xs, ys, L, y)]}
        print(namn, ut[namn], flush=True)
    ruter, kr = bygg(spec, 0.0); r = ruter[0]; M = r.motor; K = r.K
    band = {}
    rgbw = np.clip((_cmf(LAMS) @ XYZ_RGB.T), 0, None) * planck(LAMS, K)[:, None]
    for navn, E in (('auge 47 cm', AUGE), ('auge 25 cm', b(0, -0.15, 0.25)), ('auge 60 cm', b(0, -0.15, 0.60)), ('auge 47 cm, 15 cm fram', b(0, 0.0, 0.47))):
        yy = np.linspace(0.002, h - 0.002, 200)
        P = r.o[None] + r.ex * w / 2 + yy[:, None] * r.ey
        d = E - P; d /= np.linalg.norm(d, axis=1)[:, None]
        u, vv = d @ r.ex, d @ r.ey
        Ll = np.array([oppslag(M['tab_l'][i], u, vv) for i in range(len(LAMS))]) * r.kf     # (lam, y)
        Lm = (vekter(K)[:, None] * Ll).sum(0)
        rgb = Ll.T @ rgbw
        kr_ = rgb / np.maximum(rgb.sum(1, keepdims=True), 1e-12) / (rgbw.sum(0) / rgbw.sum())
        farga = (np.abs(kr_ - 1).max(1) > 0.15) & (Lm > 0.05 * Lm.max())
        th = np.degrees(np.arccos(np.clip(d @ r.ez, -1, 1)))
        band[navn] = dict(L_maks=r2(Lm.max(), 0), L_min=r2(Lm.min(), 0), vinkel_frå_normal=[r2(th.min(), 1), r2(th.max(), 1)],
                          farga_mm_frå_hengslet=[r2(yy[k] * 1000, 0) for k in np.flatnonzero(farga)[[0, -1]]] if farga.any() else [],
                          farga_breidd_mm=r2(farga.sum() * (yy[1] - yy[0]) * 1000, 0))
        print(navn, band[navn], flush=True)
    xs, ys, Ls = stripekart(w, h, STRIPER['pitch'], STRIPER['sigma'])
    S = np.array(r.punkt(24, 10)); d = AUGE - S; d /= np.linalg.norm(d, axis=1)[:, None]
    Lsnitt = float(r.L(d).mean())
    auge = dict(L_snitt=r2(Lsnitt, 0), L_stripe_topp=r2(Lsnitt * float(Ls[:, ys > 0.01].max()), 0),
                L_stripe_topp_frå_30mm=r2(Lsnitt * float(Ls[:, ys > 0.03].max()), 0))
    print('auget i stemning', auge, flush=True)
    np.save(os.path.join(CACHE, 'stripe_stemning.npy'), Ls.astype(np.float32))
    lagre('striper', dict(kontrast_og_topp_per_avstand=ut, regnbogeband=band, auget_stemning=auge,
                          merk='kontrast = (maks − min)/(maks + min) på tvers av stripene i midtre halvdel; topp = maks/snitt'))
    logg('striper (%.0f s): sjå tal.json["striper"]. Auget 47 cm i stemning: snitt %s cd/m², stripetopp %s (frå 30 mm %s).' % (
        time.time() - t0, auge['L_snitt'], auge['L_stripe_topp'], auge['L_stripe_topp_frå_30mm']))

# ------------------------------------------------------------------ IES og scene

def skriv_ies(ruter, fil, tittel):
    """LM-63-2002, type C, i romkoordinatar: γ = 0 er rett ned (−z), C = 0 er +x (til høgre), C = 90 er +y (mot veggen).
    Absolutt fotometri (lumen −1): candela for tilstanden slik han er rekna."""
    V = np.arange(0, 180.01, 2.5); Hh = np.arange(0, 360, 5.0)
    G, C = np.meshgrid(np.radians(V), np.radians(Hh), indexing='ij')
    d = np.stack([np.sin(G) * np.cos(C), np.sin(G) * np.sin(C), -np.cos(G)], -1).reshape(-1, 3)
    I = sum(r.I(d) for r in ruter).reshape(len(V), len(Hh))
    r0 = ruter[0]; lm = sum(r.phi_ut for r in ruter); lmled = sum(r.lm_led for r in ruter); W = sum(r.W for r in ruter)
    with open(fil, 'w', encoding='ascii', newline='\r\n') as f:
        f.write('IESNA:LM-63-2002\n[TEST] Rekna i northern-lampe/form05/rute/motor.py, ikkje maalt\n')
        f.write('[MANUFAC] Northern-lampe, skuleprosjekt\n[LUMCAT] %s\n[LUMINAIRE] %s\n' % (os.path.basename(fil), tittel))
        f.write('[LAMP] LED %.0f K, %.0f lm ut av ruta (%.0f lm ved LED-ane)\n[OTHER] gamma 0 = -z (ned), C 0 = +x, C 90 = +y; romkoordinatar\n' % (r0.K, lm, lmled))
        f.write('TILT=NONE\n')
        f.write('1 -1 1 %d %d 1 2 %.3f %.3f 0.006\n' % (len(V), len(Hh), r0.w, r0.h))
        f.write('1 1 %.2f\n' % W)
        def rader(x):
            s = ['%.1f' % v for v in x]
            return '\n'.join(' '.join(s[i:i + 10]) for i in range(0, len(s), 10)) + '\n'
        f.write(rader(V)); f.write(rader(Hh))
        for j in range(len(Hh)): f.write(rader(I[:, j]))
    return float(lm)

KAMERA = dict(T=dict(pos=[-0.45, -0.85, ZB + 0.30], mot=[0.02, 0.38, ZB + 0.42], fov_grader=38, merk='anslått frå det genererte biletet «Telt»'),
              K=dict(pos=[-0.60, -0.55, ZB + 0.32], mot=[0.30, 0.24, ZB + 0.38], fov_grader=45, merk='anslått frå det genererte biletet «Klemme»'))

def k_ut():
    sc = dict(merk='Romkoordinatar i meter som lysskisse.py: x til høgre, y mot veggen (veggen y = 0,70), z opp, bordplata z = 0,72. '
                    'Lyset i IES-filene er i romkoordinatar (γ 0 = ned, C 0 = +x, C 90 = +y): set punktlyset i rutesenteret utan rotasjon. '
                    'IES-filene er rekna frå luminanstabellen til motoren, ikkje målte. Arbeid er ved watten for 350 lx på feltet, stemning ved 1,25 W.',
              rom=dict(bord=dict(z=ZB, x=[-0.7, 0.7], y=[0.0, 0.7], rho=[0.50, 0.40, 0.30]), vegg_y=YV,
                       skjerm=dict(senter=[0.0, 0.45, ZB + 0.265], storleik=[0.54, 0.31], luminans_cd_m2=40, tilt_sjekka_grader=[0, 20])),
              augepunkt=dict(auge=[r2(x, 3) for x in AUGE], volum='±0,15 m sidevegs, 0,15 m fram, 0,25 til 0,60 m over bordet'),
              materiale=dict(prismefilm=dict(profil=FILMTEKST, pitch_um=PITCH_UM, pitch_merk='ANTAKING, ikkje målt',
                                              n_d=FILM.n_d, abbe=FILM.abbe, cauchy='n(λ) = A + B/λ², λ i nm', cauchy_A=r2(FILM.A, 5), cauchy_B_nm2=r2(FILM.B, 1),
                                              n=dict((str(int(l)), r2(FILM.n(l), 4)) for l in (450, 550, 650)),
                                              orientering='prismesida ut frå plata; rilleretninga står per kropp'),
                             lysleiarplate=dict(merk='ANTAKING: finst ikkje i byggjesettet', materiale='PMMA, klar', tjukn_mm=4, n_d=1.49,
                                                uttak='kvite prikkar eller V-riller på baksida, tettare mot enden'),
                             diffusor='volumdiffusor, om lag 60 % gjennom første gong (ANTAKING)',
                             reflektor='kvit PET bak plata, ρ 0,95 (ANTAKING)',
                             burgunder=list(BURG), aluminium_borsta=dict(farge=list(ALU), ruheit=0.35), gra=list(GRA)),
              kamera=dict(KAMERA, rom=dict(pos=[r2(x, 3) for x in ls.KAM.C], merk='kameraet til A, B og C i lysskisse.py')),
              kroppar={}, emitterar=[])
    for kv in ('T', 'K'):
        spec = KROPPAR[kv]; ek = les('ekstra_' + kv, {})
        sc['kroppar'][kv] = dict(spec, gest=spec.get('gest', ''), motor=last_motor(spec['kjelde'], spec['rille'])['namn'])
        for t, m in ((0.0, 'stemning'), (1.0, 'arbeid')):
            W = les('rekn_' + kv, {}).get('W350') if m == 'arbeid' else None        # heile watten, stripa med
            ruter, kr = bygg(spec, t, W=W)
            fil = 'ies_%s_%s.ies' % (spec['namn'].lower(), m)
            lm = skriv_ies(ruter, os.path.join(HER, fil), '%s, %s, %.0f K' % (spec['namn'], m, ruter[0].K))
            for r in ruter:
                sc['emitterar'].append(dict(kropp=kv, tilstand=m, ies=fil, W=r2(r.W, 2), lm_led=r2(r.lm_led, 0), lm_ut=r2(r.phi_ut, 0),
                                            CCT=r.K, senter=[r2(x, 4) for x in r.c], normal_framside=[r2(x, 4) for x in r.ez],
                                            ex=[r2(x, 4) for x in r.ex], ey=[r2(x, 4) for x in r.ey], storleik=[r.w, r.h],
                                            L_rett_fram_cd_m2=r2(r.kf * r.motor['tab'][NB // 2, NB // 2], 0),
                                            merk='mesh-plate med emisjon for det auget ser; punktlys med IES i senteret for rommet'))
    json.dump(sc, open(os.path.join(HER, 'scene.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=_j)
    logg('ut: ies_*.ies og scene.json skrivne')

# ------------------------------------------------------------------ kroppane (sjå toppen av fila)

KROPPAR = {
    'T': dict(namn='Telt', stotte='telt', kjelde='kant', rille='kryss', bak=0.0, bakstripe=0.25,
              ruter=[dict(w=0.48, h=0.20, hengsel=(0.0, 0.40, 0.50), fraa='kant', r=0.020, vinkel=(125, 0))],
              gest='drei ruta om sylinderen: lent bakover som eit vindauge i stemning (125°), liggjande over feltet i arbeid (0°)'),
    'K': dict(namn='Klemme', stotte='klemme', kjelde='kant', rille='kryss', bak=0.0,
              ruter=[dict(w=0.52, h=0.20, hengsel=(0.0, 0.24, 0.50), fraa='midt', vinkel=(-135, 0))],
              gest='snu hovudet om armen: mot veggen og taket i stemning (−135°), rett ned i arbeid (0°)'),
}

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit()
    if a[0] == 'rekn': k_rekn(a[1])
    elif a[0] == 'striper': k_striper(*a[1:])
    else: {'kalib': k_kalib, 'tretest': k_tretest, 'skann': k_skann, 'ut': k_ut, 'rutesjekk': k_rutesjekk}[a[0]]()
