# -*- coding: utf-8 -*-
"""Familie PROJEKTOR: maske, linse og spegel. Ei maske blir avbilda som ei form av lys.

  python familie.py --g1        generasjon 1: kvar i rommet verkar linsa på 285 mm (berre tal)
  python familie.py --g2        generasjon 2: kva optikk gjev eit felt på bordet frå ein kompakt kropp (berre tal)
  python familie.py --g3        generasjon 3: forma på lyset og overgangen (berre tal)
  python familie.py --brett     siste generasjon: tal.md, tal.csv og brett med px=200
  python familie.py --par       par-NAMN.png for dei tre beste
  python familie.py --rekn      reknestykka åleine (tynn linse, verknadsgrad, trakt, føreseiingar)

Bygd på ../_mal.py. Motoren (lysskisse.py) reknar ikkje linser. Difor står strålegangen her:
tynn linse (1/f = 1/u + 1/v), uskarpskive ved defokus, verknadsgrad ledd for ledd og kroppsmål.
Eit lysgrep er g(t) -> (lys, kropp), t = 0 er stemning og t = 1 er arbeid.
Alt merkt ANTAKING er ikkje målt.
"""
import sys, os, math
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HER, '..', '..', 'lysskisse'))
from lysskisse import *

# ------------------------------------------------------------------ faste tal

F_LINSE = 0.285        # projeksjonslinsa, brennvidd (research/13: 27 til 29 cm)
D_LINSE = 0.070        # ANTAKING: fri opning 70 mm
PLATE = 0.285          # fresnelspegelen, sidekant
F_PLATE = 0.1871       # fresnelspegelen, brennvidd
LMW_LED = 115.0        # lm/W frå naken LED etter drivar (reflektoren.md: 115 til 170 x 0,9). ANTAKING
RHO_F = 0.85           # fresnelspegelen (same tal som motoren brukar)
SIGMA_F = 2.5          # spreiing frå fresnelplata, grader (motoren)
TAU_L = 0.92           # linse utan antirefleks, to flater. ANTAKING
TAU_K = 0.85           # kondensor eller feltlinse (sterk fresnellinse) i ei produktlampe. ANTAKING
RHO_S = 0.90           # frontflatespegel. ANTAKING
HALE = 0.90            # del av ein samla stråle som ligg innanfor den omskrivne sirkelen til maska. ANTAKING
ETA_KASSE = 0.60       # lyskasse med diffusorark bak ei maske (lysande maske). ANTAKING
G_LYKT = PI * (PI * 0.0125 ** 2) * math.sin(math.radians(20)) ** 2   # étendue, lykt Ø 25 mm og ±20°. ANTAKING
G_TIR = PI * (PI * 0.005 ** 2) * math.sin(math.radians(25)) ** 2     # étendue, LED med samlelinse Ø 10 mm og ±25°. ANTAKING
K_C = 0.156            # logistisk kantskala per diameter på uskarpskiva (10 til 90 % av kanten er 0,687 c)
SPRUT = 0.02           # motoren si antaking om diffus lekkasje frå opninga
KOMPAKT = (0.16, 0.275)   # konvolutten til bordlykta: Ø 16 x 27,5 cm (formromkartet K2). Fotavtrykk F9 er 200 cm²

FOT = (0.47, 0.48)
HODE = b(0.47, 0.40, 0.36)            # lyshovudet til ei kompakt lampe: framfor skjermplanet, til høgre for skjermen
VEGGSOL = b(0.0, YV, 0.42)            # midt bak skjermen
FELTHJORNE = [b(-0.3, 0.05, 0), b(0.3, 0.05, 0), b(0.3, 0.45, 0), b(-0.3, 0.45, 0)]

# ------------------------------------------------------------------ tynn linse

def fokus(f, u):
    """Biletavstand v' frå 1/f = 1/u + 1/v. Negativ v' er virtuelt bilete: inga skarp flate finst.
    f = None er inga linse (skuggemaske): då er u avstanden frå kjelde til maske."""
    if f is None: return -u
    if abs(u - f) < 1e-9: return float('inf')
    return f * u / (u - f)

def u_for(f, v):
    """Maskeavstanden som gjev skarpt bilete i avstand v. None når v <= f: linsa kan ikkje avbilde så nær."""
    return f * v / (v - f) if v > f + 1e-9 else None

def uskarp(p, f, u, r):
    """Diameter på uskarpskiva i avstand r: c = p * |1 - r / v'|.
    p er den lysfylte delen av opninga (med inga linse: storleiken på kjelda)."""
    inv = (0.0 if f is None else 1.0 / f) - 1.0 / u
    return p * np.abs(1 - np.asarray(r, float) * inv)

def u_mjuk(f, p, r, kant):
    """Maskeavstand innanfor fokus som gjev kantbreidd «kant» (10 til 90 %) i avstand r."""
    c = kant / 0.687
    return 1.0 / (1.0 / f + (c / p - 1) / r) if c > p else f

def minste_kast(f):
    """Minste avstand frå maske til skarpt bilete: 4 f (u = v = 2 f)."""
    return 4 * f

# ------------------------------------------------------------------ verknadsgrad

def lambert_sirkel(D, s):
    """Del av lyset frå ein flat LED som går gjennom ei sirkelopning D i avstand s: sin² av halvvinkelen."""
    return (D / 2) ** 2 / ((D / 2) ** 2 + s ** 2)

def lambert_rekt(a, c, s):
    """Del av lyset frå ein flat LED som treffer eit rektangel a x c i avstand s, midt framfor."""
    x, y = a / (2 * s), c / (2 * s)
    return 2 / PI * (x / math.sqrt(1 + x * x) * math.atan(y / math.sqrt(1 + x * x))
                     + y / math.sqrt(1 + y * y) * math.atan(x / math.sqrt(1 + y * y)))

def pupill(D, u):
    """Del av kjeldebiletet frå fresnelplata som fell innanfor linseopninga (gaussisk flekk, sigma 2,5°)."""
    s = u * math.tan(math.radians(SIGMA_F))
    return 1 - math.exp(-(D / 2) ** 2 / (2 * s * s))

def kit_kjelde(u, dia, D=D_LINSE):
    """Fresnelplata som kondensor (slik overheadprojektoren gjer det): kjelda står s over plata, og plata avbildar
    ho i s' (1/s + 1/s' = 1/F). Best er s' = u. Kjelda kan stå 0,25 til 0,60 m over plata. Gjev (s, fotavtrykk i
    linseplanet, del av lyset som går gjennom opninga). Under F = 187 mm finst ikkje noko reelt kjeldebilete nær linsa."""
    s = u * F_PLATE / (u - F_PLATE) if u > F_PLATE * 1.05 else 0.60
    s = min(max(s, 0.25), 0.60)
    sb = 1.0 / (1.0 / F_PLATE - 1.0 / s)
    fot = dia * abs(1 - u / sb)
    return s, fot, min(1.0, (D / max(fot, 1e-6)) ** 2) * pupill(D, u)

def trakt(inn, ut, L, u, D, rho=0.85, n=30000, seed=3):
    """Pyramidetrakt falda av spegelark (utfaldbar: fire plane trapes). Flat LED i den tronge enden,
    maska er den vide enden, feltlinse i maska og projeksjonslinse i avstand u. Monte Carlo.
    Gjev (del av LED-lyset som går gjennom linseopninga, del som kjem ut av trakta, snitt sprett)."""
    rng = np.random.default_rng(seed)
    w0, h0 = inn; w1, h1 = ut
    P = np.stack([(rng.random(n) - .5) * w0, (rng.random(n) - .5) * h0, np.zeros(n)], 1)
    r1 = rng.random(n); ph = 2 * PI * rng.random(n); st = np.sqrt(r1)
    V = np.stack([st * np.cos(ph), st * np.sin(ph), np.sqrt(1 - r1)], 1)
    ax, ay = (w1 - w0) / (2 * L), (h1 - h0) / (2 * L)
    vegger = [((-1, 0, ax), (1, 0, -ax), w0 / 2), ((1, 0, ax), (-1, 0, -ax), w0 / 2),
              ((0, -1, ay), (0, 1, -ay), h0 / 2), ((0, 1, ay), (0, -1, -ay), h0 / 2)]
    vekt = np.ones(n); spr = np.zeros(n); ferdig = np.zeros(n, bool); tapt = np.zeros(n, bool)
    for _ in range(60):
        akt = ~(ferdig | tapt)
        if not akt.any(): break
        with np.errstate(all='ignore'):
            tz = np.where(V[:, 2] > 1e-9, (L - P[:, 2]) / V[:, 2], np.inf)
            t0 = np.where(V[:, 2] < -1e-9, -P[:, 2] / V[:, 2], np.inf)
            best = np.minimum(tz, t0); kva = np.where(tz <= t0, -1, -2)
            for i, (nn, pl, c0) in enumerate(vegger):
                nn = np.array(nn, float); nn /= np.linalg.norm(nn); pl = np.array(pl, float)
                den = V @ pl; tt = (c0 - P @ pl) / den
                ok = (den > 1e-12) & (tt > 1e-9) & (tt < best)
                best = np.where(ok, tt, best); kva = np.where(ok, i, kva)
        P = np.where(akt[:, None], P + best[:, None] * V, P)
        ferdig |= akt & (kva == -1); tapt |= akt & (kva == -2)
        for i, (nn, pl, c0) in enumerate(vegger):
            m = akt & (kva == i)
            if m.any():
                nn = np.array(nn, float); nn /= np.linalg.norm(nn)
                V[m] = V[m] - 2 * (V[m] @ nn)[:, None] * nn
                vekt[m] *= rho; spr[m] += 1
    ut_del = float(vekt[ferdig].sum() / n)
    best_gjennom = 0.0
    for F in np.linspace(0.4, 1.6, 13) * (1.0 / (1.0 / L + 1.0 / u)):       # feltlinsa: finn beste brennvidd
        sx = V[ferdig, 0] / V[ferdig, 2] - P[ferdig, 0] / F
        sy = V[ferdig, 1] / V[ferdig, 2] - P[ferdig, 1] / F
        inne = np.hypot(P[ferdig, 0] + sx * u, P[ferdig, 1] + sy * u) <= D / 2
        best_gjennom = max(best_gjennom, float((vekt[ferdig] * inne).sum() / n))
    return best_gjennom, ut_del, float(spr[ferdig].mean()) if ferdig.any() else 0.0

# ------------------------------------------------------------------ masker (avstandsfelt i meter, positivt inni)

def sol(r, x0=0.0, y0=0.0): return lambda x, y: r - np.hypot(x - x0, y - y0)
def rekt(w, h, x0=0.0, y0=0.0): return lambda x, y: np.minimum(w / 2 - np.abs(x - x0), h / 2 - np.abs(y - y0))
def snitt(*fs): return lambda x, y: np.minimum.reduce([f(x, y) for f in fs])
def over(y0): return lambda x, y: y - y0                       # halvplan: alt over y0 (bladet til horisonten)
def vindauge(w, h, sprosse):
    """Rektangel med sprossekross: fire ruter."""
    return lambda x, y: np.minimum(rekt(w, h)(x, y), np.minimum(np.abs(x) - sprosse / 2, np.abs(y) - sprosse / 2))
def dreidd(form, grader, spegla=False):
    c, s = math.cos(math.radians(grader)), math.sin(math.radians(grader))
    return lambda x, y: form((-1 if spegla else 1) * (c * x + s * y), -s * x + c * y)

def mangekant(pts):
    """Konveks mangekant."""
    pts = np.asarray(pts, float)
    if 0.5 * np.sum(pts[:, 0] * np.roll(pts[:, 1], -1) - np.roll(pts[:, 0], -1) * pts[:, 1]) < 0: pts = pts[::-1]
    def f(x, y):
        sd = np.full(np.shape(x), np.inf)
        for i in range(len(pts)):
            a = pts[i]; e = pts[(i + 1) % len(pts)] - a; L = math.hypot(*e)
            sd = np.minimum(sd, ((x - a[0]) * -e[1] + (y - a[1]) * e[0]) / L)
        return sd
    return f

def tilbake(pos, mot, punkt, u, opp=None):
    """Punkt i rommet -> maskekoordinatar (meter i maskeplanet) for ei linse i pos som siktar mot «mot»."""
    n = nrm(np.asarray(mot, float) - pos); eu, ev = ortho(n, opp)
    return [(u * ((P - pos) @ eu) / ((P - pos) @ n), u * ((P - pos) @ ev) / ((P - pos) @ n)) for P in punkt]

# ------------------------------------------------------------------ biletet i rommet (maskefunksjon til straale)

def treff(pos, d):
    """Avstand langs kvar stråle til næraste romflate (bord, vegg, tak). 3 m der strålen ikkje treffer noko."""
    t = np.full(len(d), np.inf)
    with np.errstate(all='ignore'):
        tb = (ZB - pos[2]) / d[:, 2]; x = pos[0] + tb * d[:, 0]; y = pos[1] + tb * d[:, 1]
        t = np.where((d[:, 2] < -1e-6) & (tb > 0) & (np.abs(x) <= 0.7) & (y >= 0) & (y <= YV), np.minimum(t, tb), t)
        tv = (YV - pos[1]) / d[:, 1]; z = pos[2] + tv * d[:, 2]
        t = np.where((d[:, 1] > 1e-6) & (tv > 0) & (z >= 0) & (z <= 2.5), np.minimum(t, tv), t)
        tt = (2.5 - pos[2]) / d[:, 2]; y = pos[1] + tt * d[:, 1]
        t = np.where((d[:, 2] > 1e-6) & (tt > 0) & (y <= YV), np.minimum(t, tt), t)
    return np.where(np.isfinite(t), t, 3.0)

def _sd(pos, d, n, eu, ev, form, koord, u):
    """Avstand til maskekanten, målt i meter på tvers av strålen ved flata, og aksial avstand r."""
    c = d @ n; cc = np.maximum(c, 1e-6)
    t = treff(pos, d); r = t * cc
    if koord == 'maske':
        return form(u * (d @ eu) / cc, u * (d @ ev) / cc) * r / u, r, c
    with np.errstate(all='ignore'):
        if koord == 'bord':
            tp = (ZB - pos[2]) / d[:, 2]; P = pos + tp[:, None] * d; sd = form(P[:, 0], P[:, 1]); ci = np.abs(d[:, 2])
        elif koord == 'vegg':
            tp = (YV - pos[1]) / d[:, 1]; P = pos + tp[:, None] * d; sd = form(P[:, 0], P[:, 2] - ZB); ci = np.abs(d[:, 1])
        else:
            tp = (2.5 - pos[2]) / d[:, 2]; P = pos + tp[:, None] * d; sd = form(P[:, 0], P[:, 1]); ci = np.abs(d[:, 2])
    sd = np.where(np.isfinite(sd) & (tp > 0), sd * np.sqrt(np.clip(ci, 0.04, 1)), -1.0)
    return sd, np.where(tp > 0, tp * cc, r), c

def bilete(mot, form, u, f, p, koord='maske', c0=0.0, tvang=None, opp=None, jamn=0.0, r0=1.0, kmin=0.004, vekt=None):
    """Maskefunksjon til straale(): maska «form» avbilda av ei linse (f, lysfylt opning p) med maska i avstand u.
    koord='maske': form er gjeven i maskeplanet. 'bord', 'vegg', 'tak': form er gjeven på flata (maska er klipt
    som tilbakeprojeksjonen, altså trapeskorrigert). Kanten er logistisk med skala K_C * uskarpskiva.
    c0: ekstra uskarpleik per meter (aberrasjon). tvang: fast uskarpskive i meter (ønske, ikkje fysikk).
    jamn: gradert maske, vekt (r / r0)^jamn, høgst 1 (gråfilter som dempar dei nære strålane)."""
    mot = np.asarray(mot, float)
    def fn(pos, d):
        n = nrm(mot - pos); eu, ev = ortho(n, opp)
        sd, r, c = _sd(pos, d, n, eu, ev, form, koord, u)
        blur = (uskarp(p, f, u, r) + c0 * r) if tvang is None else tvang
        w = sig(sd / np.maximum(K_C * blur, kmin))
        if jamn: w = w * np.minimum(r / r0, 1.0) ** jamn          # r0 er lengste stråle i maska
        if vekt is not None:                                       # gradert maske, fast i maskeplanet (G4)
            cc = np.maximum(d @ n, 1e-6); w = w * vekt(u * (d @ eu) / cc, u * (d @ ev) / cc)
        return np.where(c > 0.05, w, 0.0)
    return fn

def maskemaal(pos, mot, form, koord, u, opp=None, jamn=0.0, r0=1.0, N=141, vekt=None):
    """Opninga i maskeplanet: areal, omskriven diameter, fyllgrad av den omskrivne sirkelen, filtertap."""
    pos = np.asarray(pos, float); n = nrm(np.asarray(mot, float) - pos); eu, ev = ortho(n, opp)
    R0 = 1.5 * u; g = (np.arange(N) + 0.5) / N * 2 * R0 - R0
    X, Y = np.meshgrid(g, g); x = X.ravel(); y = Y.ravel()
    d = n[None] + (x / u)[:, None] * eu + (y / u)[:, None] * ev
    d /= np.linalg.norm(d, axis=1)[:, None]
    sd, r, c = _sd(pos, d, n, eu, ev, form, koord, u)
    inne = sd > 0
    if not inne.any(): return dict(A=0.0, dia=0.0, fyll=0.0, filter=1.0, rmax=1.0, skugge=0.0)
    cx, cy = x[inne].mean(), y[inne].mean()
    R = float(np.hypot(x[inne] - cx, y[inne] - cy).max()) + R0 / N
    A = float(inne.sum()) * (2 * R0 / N) ** 2
    rmax = float(r[inne].max())
    fl = float(((r[inne] / rmax) ** jamn).mean()) if jamn else 1.0
    if vekt is not None: fl *= float(vekt(x[inne], y[inne]).mean())
    return dict(A=A, dia=2 * R, fyll=min(A / (PI * R * R), 1.0), filter=fl, rmax=rmax,
                skugge=float(((1 + (x[inne] ** 2 + y[inne] ** 2) / u ** 2) ** -2).sum() * (2 * R0 / N) ** 2 / (PI * u * u)))

# ------------------------------------------------------------------ optikkane

def optikk(namn, type, f, D, p=None, **kw):
    o = dict(namn=namn, type=type, f=f, D=D, p=(D if p is None else p)); o.update(kw); return o

KIT = optikk('linsa 285 + fresnelplata', 'kit', F_LINSE, D_LINSE, p=0.045)          # samla kjelde, plata som kondensor
KIT_NAKEN = optikk('linsa 285 + plata, naken LED', 'kit-naken', F_LINSE, D_LINSE, p=0.045)
KIT_UTAN = optikk('linsa 285 utan kondensor', 'utan', F_LINSE, D_LINSE, p=D_LINSE)
C0_KORT = 0.03         # ANTAKING: enkel linse over eit felt på ±34° er 3 cm uskarp per meter
KORT = optikk('produktlinse 60 mm', 'kort', 0.060, 0.030, c0=C0_KORT)
KORT_LITEN = optikk('produktlinse 60 mm, Ø 12', 'kort', 0.060, 0.012, c0=C0_KORT)
KORT41 = optikk('produktlinse 41 mm', 'kort', 0.041, 0.020, c0=C0_KORT)
KULE = optikk('glaskule Ø 70', 'kule', 0.052, 0.070, p=0.025, c0=0.05)             # S12. ANTAKING: 5 cm uskarpt per meter
SKUGGE3 = optikk('skuggemaske, LED 3 mm', 'skugge', None, 0.003)
SKUGGE12 = optikk('skuggemaske, kjelde 12 mm', 'skugge', None, 0.012)
_TRAKT = {}
def trakt_optikk(u=0.0667, ut=(0.066, 0.048), L=0.06):
    key = (round(u, 4), ut, L)
    if key not in _TRAKT:
        gj, ute, spr = trakt((0.005, 0.005 * ut[1] / ut[0]), ut, L, u, 0.030)
        _TRAKT[key] = optikk('produktlinse 60 mm + trakt', 'trakt', 0.060, 0.030, eta_trakt=gj, L=L, c0=C0_KORT)
    return _TRAKT[key]

def lumen_per_watt(o, mm, u, spegel=0, blad=1.0):
    """Lumen ut per watt inn, ledd for ledd. mm er maskemåla. blad: open del av maska når eit blad eller ein iris stengjer.
    Gjev (lm/W, tekst)."""
    t = o['type']; D = o['D']
    Gs = mm['A'] * PI * lambert_sirkel(D, u)                        # étendue som systemet tek imot
    if t == 'kit':
        ledd = [('hale', HALE), ('maske', mm['fyll']), ('plate', RHO_F), ('pupill', kit_kjelde(u, mm['dia'], D)[2]), ('linse', TAU_L),
                ('étendue', min(1.0, Gs / G_LYKT))]; basis = LMW_KJELDE
    elif t == 'kit-naken':
        ledd = [('plata fangar', lambert_rekt(PLATE, PLATE, 0.40)), ('maske', min(mm['A'] / PLATE ** 2, 1.0)), ('plate', RHO_F),
                ('pupill', kit_kjelde(u, mm['dia'], D)[2]), ('linse', TAU_L)]; basis = LMW_LED
    elif t == 'utan':
        ledd = [('linsa fangar', lambert_sirkel(D, u)), ('linse', TAU_L)]; basis = LMW_LED
    elif t in ('kort', 'kule'):
        ledd = [('hale', HALE), ('maske', mm['fyll']), ('kondensor', TAU_K), ('linse', TAU_L),
                ('étendue', min(1.0, Gs / G_TIR))]; basis = LMW_KJELDE
    elif t == 'trakt':
        ledd = [('trakt og opning', o['eta_trakt']), ('feltlinse', TAU_K), ('linse', TAU_L)]
        basis = LMW_LED
    elif t == 'skugge':
        ledd = [('maska slepper', mm['skugge'])]; basis = LMW_LED
    if blad < 0.999: ledd.append(('blad', blad))
    if mm['filter'] < 1: ledd.append(('gråfilter', mm['filter']))
    if spegel: ledd.append(('spegel', RHO_S ** spegel))
    e = float(np.prod([v for _, v in ledd]))
    return basis * e, ' x '.join('%s %.2f' % kv for kv in ledd)

def stroek(pos, mot, Wd, K, form, o, koord='maske', u=None, kant=None, spegel=0, bronn=None, opp=None,
           jamn=0.0, tvang=None, lm_fast=None, blad=1.0, A_full=None, vekt=None):
    """Eitt projisert strøk. u = None gjev skarpt bilete i målavstanden (eller u = f når målet ligg innanfor f).
    kant: ønskt kantbreidd i meter (10 til 90 %), løyst ved å skyve maska innanfor fokus.
    Wd er watten som går til dette strøket. Motoren får sann watt (kjelde) og lumen ut (etter optikken)."""
    pos = np.asarray(pos, float); mot = np.asarray(mot, float)
    f, D, p = o['f'], o['D'], o['p']; r = float(np.linalg.norm(mot - pos)); merk = ''
    if u is None:
        u = u_for(f, r) if f is not None else 0.10
        if u is None: u = f; merk = 'målet ligg innanfor f: uendeleg fokus'
        if kant is not None and f is not None: u = min(u, u_mjuk(f, p, r, kant))
    vf = fokus(f, u)
    mm = maskemaal(pos, mot, form, koord, u, opp, jamn, r, vekt=vekt)
    if A_full: blad = min(mm['A'] / A_full, 1.0)
    if o['type'] in ('kit', 'kit-naken'):
        s_k, fot_k, _ = kit_kjelde(u, mm['dia'], D); p = min(D, math.hypot(fot_k, 0.045))
    lmw, tekst = lumen_per_watt(o, mm, u, spegel, blad)
    lm = Wd * lmw if lm_fast is None else lm_fast
    l = straale(pos, mot, max(lm, 1e-6), K, maske=bilete(mot, form, u, f, p, koord, o.get('c0', 0.0), tvang, opp, jamn, mm['rmax'], vekt=vekt),
                opning=max(D / 2, 0.004), sprut=SPRUT, bronn=bronn, opp=opp)
    l.lm_ut = lm; l.lm = Wd * LMW_KJELDE; l.mater = True          # motoren reknar W = lm / LMW_KJELDE og lumen ut = lm_ut
    c = float(uskarp(p, f, u, r)) + o.get('c0', 0.0) * r if tvang is None else tvang
    ekstra = {'kit': 0.0, 'kit-naken': 0.0, 'utan': 0.0, 'kort': 0.045, 'kule': 0.08, 'trakt': o.get('L', 0.06) + 0.01, 'skugge': 0.02}[o['type']]
    lengd = u + ekstra
    breidd = max(mm['dia'], D) + 0.012
    if o['type'] in ('kit', 'kit-naken'):
        lengd = max(u, s_k); breidd = max(breidd, PLATE); merk += ' kjelda %.2f m over plata' % s_k
        if mm['dia'] > PLATE * 1.2: merk += ', maska er større enn plata'
    if vf < 0 and f is not None and tvang is not None and tvang < 0.02: merk += ' KAN IKKJE LAGAST: virtuelt bilete, ingen skarp kant'
    l.info = dict(optikk=o['namn'], f=f, u=u, vf=vf, r=r, skala=r / u, maske=mm['dia'], A=mm['A'], fyll=mm['fyll'], c=c,
                  kant=0.687 * c, lmw=lmw, ledd=tekst, lm=lm, lengd=lengd, breidd=breidd,
                  kompakt=(breidd <= KOMPAKT[0] and lengd <= KOMPAKT[1]), merk=merk.strip(), spegel=spegel)
    return l

def lm_skjerm(lys):
    """Lumen som landar på framsida av dataskjermen (motoren tel det ikkje). Projektoren kan sveipe over skjermen."""
    s = 0.0
    for l in lys:
        if isinstance(l, Ark): continue
        p = l.pts[0]
        if p[1] >= 0.45: continue
        with np.errstate(all='ignore'):
            t = (0.45 - p[1]) / FIB[:, 1]; x = p[0] + t * FIB[:, 0]; z = p[2] + t * FIB[:, 2]
        m = (FIB[:, 1] > 1e-6) & (np.abs(x) < 0.27) & (z > ZB + 0.11) & (z < ZB + 0.42)
        s += float(l.I(FIB[m]).sum()) * 4 * PI / len(FIB)
    return s

# ------------------------------------------------------------------ kroppar (svarte lekamar)

def lekam(pos, n, info, fot=FOT, stamme=True):
    r = min(info['breidd'] / 2, 0.16); L = min(info['lengd'], 0.45)
    k = [Syl(pos - L * n, pos - 0.004 * n, r)]
    if stamme:
        k += [syl(b(fot[0], fot[1], 0), b(fot[0], fot[1], 0.04), 0.05),
              syl(b(fot[0], fot[1], 0.04), pos - 0.5 * L * n - np.array([0, 0, r]), 0.006)]
    return k

def vipp(t, fra=VEGGSOL, til=FELT):
    return np.asarray(fra, float) * (1 - t) + np.asarray(til, float) * t

def lerp(a, c, t): return a + (c - a) * t

# ------------------------------------------------------------------ generasjon 1: kvar verkar linsa på 285 mm?
# Same grep på alle: sol som maske, irisen opnar seg frå stemning til arbeid. Det som varierer, er staden og kastet.

def g1(pos, mot, rm_s, rm_a, o=KIT, u=None, spegel=0, fot=FOT, tvang=None, stamme=True):
    def g(t):
        W, K = watt(t); p = np.asarray(pos, float)
        l = stroek(p, mot, W, K, sol(lerp(rm_s, rm_a, t)), o, u=u, spegel=spegel, tvang=tvang)
        return [l], lekam(p, nrm(np.asarray(mot, float) - p), l.info, fot, stamme)
    return g

TAKPOS = b(0.47, 0.48, 0.38)
GOLVPOS = b(0.75, -0.55, 0.95)
G1 = [
    ('bak-skjerm',  g1(HODE, VEGGSOL, 0.076, 0.14)),                                  # 0,56 m: innanfor 4 f, uendeleg fokus
    ('tak',         g1(TAKPOS, b(0.47, 0.48, 1.78), 0.05, 0.14, stamme=False)),       # søyle, sol i taket
    ('vegg-hog',    g1(HODE, b(0.10, YV, 1.25), 0.06, 0.14)),                         # høgt på veggen over skjermen
    ('vegg-skraa',  g1(b(0.62, 0.50, 0.25), b(-0.40, YV, 0.50), 0.03, 0.06, spegel=1, fot=(0.62, 0.55))),   # stryk langs veggen
    ('framkant',    g1(b(0.58, 0.06, 0.25), b(0.0, YV, 0.62), 0.07, 0.14, spegel=1, fot=(0.60, 0.10))),     # frå framkanten av bordet
    ('ohp-bord',    g1(HODE, FELT, 0.05, 0.14, u=F_LINSE, spegel=1)),                 # uendeleg fokus ned på bordet
    ('bord-skarp',  g1(HODE, FELT, 0.05, 0.14)),                                      # skarpt på 0,61 m: u = 0,535 m
    ('golv',        g1(GOLVPOS, FELT, 0.03, 0.085, fot=(0.75, -0.55), stamme=False)), # golvlampe 1,45 m unna
    ('tak-naken',   g1(TAKPOS, b(0.47, 0.48, 1.78), 0.05, 0.14, o=KIT_NAKEN, stamme=False)),
    ('tak-utan',    g1(TAKPOS, b(0.47, 0.48, 1.78), 0.05, 0.14, o=KIT_UTAN, stamme=False)),
    ('onske-kort',  g1(HODE, VEGGSOL, 0.04, 0.07, u=0.14, tvang=0.004)),              # skarp sol frå ein kropp på 14 cm: finst ikkje
]

# ------------------------------------------------------------------ generasjon 2: kva optikk gjev eit felt på bordet?
# Same stad (HODE), same maske (feltet, trapeskorrigert), same overgang (vipp frå veggen til feltet). Optikken varierer.

def feltmaske(u, pos=HODE): return mangekant(tilbake(pos, FELT, FELTHJORNE, u))

def g2(o, u=None, kant=None, spegel=0, jamn=0.0, bronn=45):
    def g(t):
        W, K = watt(t); mot = vipp(t)
        uu = u
        if uu is None:
            uu = u_for(o['f'], 0.61) if o['f'] is not None else 0.10
            if uu is None: uu = o['f']
            if kant is not None: uu = min(uu, u_mjuk(o['f'], o['p'], 0.61, kant))
        l = stroek(HODE, mot, W, K, feltmaske(uu), o, u=uu, spegel=spegel, bronn=bronn, jamn=jamn)
        return [l], lekam(HODE, nrm(mot - HODE), l.info)
    return g

def g_fresnelprofil(t, c=b(0.47, 0.40, 0.55), kp=b(0.47, 0.44, 0.31), n_flis=22):
    """Fresnelspegelen som avbildande optikk: ei lysande maske 0,25 m framfor plata blir avbilda 0,74 m unna (m = 3).
    Rekna i motoren sin eigen arkmodell. Maska er ei lyskasse med diffusorark (lambertsk)."""
    W, K = watt(t); mot = vipp(t)
    nk = nrm(c - kp); eu, ev = ortho(nk)
    lm = W * LMW_LED * ETA_KASSE
    ks = [flate(kp + eu * 0.05 * i + ev * 0.0333 * j, nk, (0.10, 0.0667), lm / 4, K) for i in (-1, 1) for j in (-1, 1)]
    a = fresnelspegel(ks, c, nrm(nrm(kp - c) + nrm(mot - c)), n=n_flis)
    for k in ks: k.lm = W * LMW_KJELDE / 4                     # sann watt i motoren sitt rekneskap
    kropp = [syl(b(FOT[0], FOT[1], 0), b(FOT[0], FOT[1], 0.04), 0.06), syl(b(FOT[0], FOT[1], 0.04), b(FOT[0], FOT[1], 0.60), 0.008),
             Syl(kp - 0.06 * nk, kp - 0.004 * nk, 0.12)]
    return ks + [a], kropp

def g_ideal(t):
    """Referansen frå første brett: «profil», idealisert maske utan tap i optikken."""
    return g_profil('a' if t >= 0.5 else 's')

G2 = [
    ('ideal',          g_ideal),
    ('linse285',       g2(KIT, u=F_LINSE, spegel=1, bronn=None)),
    ('linse285-lupe',  g2(KIT, u=0.15, bronn=None)),
    ('skugge-3',       g2(SKUGGE3, u=0.10)),
    ('skugge-12',      g2(SKUGGE12, u=0.10)),
    ('kort60',         g2(KORT)),
    ('kort60-liten',   g2(KORT_LITEN)),
    ('kort41',         g2(KORT41)),
    ('kort60-mjuk',    g2(KORT, kant=0.06)),
    ('kort60-jamn',    g2(KORT, kant=0.06, jamn=2.0)),
    ('trakt60',        lambda t: g2(trakt_optikk(), kant=0.06)(t)),
    ('kule52',         g2(KULE)),
    ('fresnelprofil',  g_fresnelprofil),
]

# ------------------------------------------------------------------ generasjon 3: forma på lyset og overgangen
# Optikken er vald (kort linse med trakt som kondensor, mjuk kant ved defokus). No varierer maska (sol, horisont,
# vindauge, felt) og organet som gjer overgangen (vipp, iris, blad, delt spegel, fokus, kjeldeskyv). Settet sin eigen
# optikk står attmed som kropp (ohp, tak-sol, golv, plateprofil), saman med referansen og ønsket som ikkje kan lagast.

KANT = 0.06                                    # mjuk lyskant: 6 cm frå 10 til 90 %
def PROD(): return trakt_optikk()
def U_P(): return u_mjuk(0.060, 0.030, 0.61, KANT)     # maska om lag 16 mm innanfor fokus
HORISONT_MIDT = b(-0.15, YV, 0.48)
def horisontmaske(u):
    """Liggjande band på veggen bak skjermen, 0,85 m langt og 0,24 m høgt, sett frå hovudet."""
    hj = [b(-0.60, YV, 0.36), b(0.25, YV, 0.36), b(0.25, YV, 0.60), b(-0.60, YV, 0.60)]
    return mangekant(tilbake(HODE, HORISONT_MIDT, hj, u))

def beste_rull(form, u, mot=FELT, pos=HODE, spegla=True):
    """Spegelen kan rulle biletet fritt. Vel rullen som legg mest av maska på arbeidsfeltet."""
    n = nrm(mot - pos); eu, ev = ortho(n); best = (-1, 0)
    N = 61; g = (np.arange(N) + 0.5) / N * 3 * u - 1.5 * u; X, Y = np.meshgrid(g, g); x = X.ravel(); y = Y.ravel()
    d = n[None] + (x / u)[:, None] * eu + (y / u)[:, None] * ev
    tp = (ZB - pos[2]) / d[:, 2]; P = pos + tp[:, None] * d
    ifelt = (tp > 0) & (np.abs(P[:, 0]) < 0.3) & (P[:, 1] > 0.05) & (P[:, 1] < 0.45)
    for ang in range(0, 180, 10):
        inne = dreidd(form, ang, spegla)(x, y) > 0
        if inne.any():
            q = float((inne & ifelt).sum()) / float(ifelt.sum()) * float((inne & ifelt).sum()) / float(inne.sum())
            if q > best[0]: best = (q, ang)
    return best[1]

def gradert(grad, u, pos=HODE, mot=FELT, spegla=False):
    """Gradert maske (gråfilter i maskeplanet) som jamnar ut nær og fjern del av feltet. Vekta er fast i maskeplanet:
    (r / r_fjern)^grad, rekna for siktet mot feltet, der r er aksial avstand til bordet og r_fjern er det fjernaste hjørnet.
    spegla: maska sett utan spegel (x -> -x), når bordstrålen går via frontflatespegelen."""
    pos = np.asarray(pos, float); n = nrm(np.asarray(mot, float) - pos); eu, ev = ortho(n)
    rref = max(float((P - pos) @ n) for P in FELTHJORNE)
    def v(x, y):
        x = -np.asarray(x, float) if spegla else np.asarray(x, float); y = np.asarray(y, float)
        d = n[None] + (x.ravel() / u)[:, None] * eu + (y.ravel() / u)[:, None] * ev
        d /= np.linalg.norm(d, axis=1)[:, None]
        r = treff(pos, d) * (d @ n)
        return (np.clip(r / rref, 0, 1) ** grad).reshape(np.shape(x))
    return v

def p_vipp(formf, mot0=VEGGSOL, o=None, jamn=0.0, grad=0.0):
    """Hovudet vippar: same maske, frå veggen bak skjermen til feltet."""
    def g(t):
        W, K = watt(t); oo = o or PROD(); u = U_P() if oo['type'] == 'trakt' else u_for(oo['f'], 0.61)
        mot = vipp(t, mot0)
        l = stroek(HODE, mot, W, K, formf(u), oo, u=u, bronn=45, jamn=jamn, vekt=(gradert(grad, u) if grad else None))
        return [l], lekam(HODE, nrm(mot - HODE), l.info)
    return g

def p_blad(kva):
    """Fast sikte mot feltet. Maska endrar seg: iris (sol som veks) eller blad (horisont som stig over feltet)."""
    def g(t):
        W, K = watt(t); u = U_P(); full = feltmaske(u)
        A_full = maskemaal(HODE, FELT, full, 'maske', u)['A']
        if kva == 'iris':
            form = snitt(full, sol(lerp(0.012, 0.050, t)))
            l = stroek(HODE, FELT, W, K, form, PROD(), u=u, bronn=45, A_full=A_full)
        else:
            y0 = lerp(0.33, 0.05, t)                         # bladet: lys berre bak lina y0 på bordet
            l = stroek(HODE, FELT, W, K, lambda x, y: np.minimum(rekt(0.6, 0.4, 0, 0.25)(x, y), y - y0), PROD(),
                       koord='bord', u=u, bronn=45, A_full=A_full)
        return [l], lekam(HODE, nrm(FELT - HODE), l.info)
    return g

def p_dele(formf, mot0=VEGGSOL, q1=0.75, rull=None, jamn=0.0, grad=0.0):
    """Linsa siktar mot veggen. Frontflatespegelen blir skoven inn i strålen og legg delen q på bordet.
    Begge bileta er heile, fordi kvart maskepunkt fyller heile opninga. q = 0 i stemning, q1 i arbeid."""
    def g(t):
        W, K = watt(t); u = U_P(); form = formf(u); q = q1 * t
        ang = beste_rull(form, u) if rull is None else rull
        vb = gradert(grad, u) if grad else None                    # same fysiske filter i begge strålane
        vv = gradert(grad, u, spegla=True) if grad else None
        lv = stroek(HODE, mot0, W * (1 - q), K, form, PROD(), u=u, bronn=45, vekt=vv)
        lys = [lv]
        if q > 1e-6:
            lys.append(stroek(HODE, FELT, W * q, K, dreidd(form, ang, True), PROD(), u=u, spegel=1, bronn=45, jamn=jamn, vekt=vb))
        return lys, lekam(HODE, nrm(mot0 - HODE), lv.info)
    return g

def p_zoom(t):
    """Fast sikte mot feltet, fast sol i maska. Maska blir skoven mot linsa: skarp lysmynt blir stort, mjukt felt."""
    W, K = watt(t); u = lerp(u_for(0.060, 0.61), 0.042, t)
    l = stroek(HODE, FELT, W, K, sol(0.020), PROD(), u=u, bronn=45)
    return [l], lekam(HODE, nrm(FELT - HODE), l.info)

def p_skugge(t):
    """Inga linse. Fast maske, kjelda (5 mm) blir skoven frå 25 til 10 cm bak maska: lite, skarpt felt blir stort."""
    W, K = watt(t); n = nrm(FELT - HODE); a = lerp(0.25, 0.10, t)
    o = optikk('skuggemaske, kjelde 5 mm', 'skugge', None, 0.005)
    l = stroek(HODE - (a - 0.10) * n, FELT, W, K, feltmaske(0.10), o, u=a, bronn=45)
    return [l], lekam(HODE, n, dict(breidd=l.info['breidd'], lengd=0.27))

def k_ohp(t):
    """Overheadprojektoren slik han står, utan pære: maska ligg på plata, hovudet 345 mm over, spegelen vippar biletet."""
    W, K = watt(t); mot = vipp(t)
    l = stroek(HODE, mot, W, K, sol(0.14), KIT, u=0.345, spegel=1)
    kropp = [Syl(b(0.47, 0.42, 0.0), b(0.47, 0.42, 0.012), 0.16), syl(b(0.62, 0.47, 0), b(0.62, 0.47, 0.36), 0.012),
             Syl(HODE - 0.09 * nrm(mot - HODE), HODE - 0.004 * nrm(mot - HODE), 0.05)]
    return [l], kropp

def k_golv(t):
    """Linsa 285 der ho høver: 1,45 m unna, på ei hylle eller ei golvstong bak høgre skulder. Skarpt felt."""
    W, K = watt(t); mot = vipp(t, b(0.0, YV, 0.75)); u = u_for(F_LINSE, 1.45)
    hj = tilbake(GOLVPOS, FELT, FELTHJORNE, u)
    l = stroek(GOLVPOS, mot, W, K, mangekant(hj), KIT, u=u)
    return [l], [Syl(GOLVPOS - 0.36 * nrm(mot - GOLVPOS), GOLVPOS - 0.004 * nrm(mot - GOLVPOS), 0.15)]

def k_plateprofil(t, rull=0.0, d_kjelde=0.12, n_flis=26):
    """Fresnelspegelen som projektor: maska ligg på plata (plata er klipt til 190 x 125 mm), kjelda står 12 cm
    framfor, innanfor brennvidda, så biletet spreier seg til feltet. Rekna i motoren sin arkmodell."""
    W, K = watt(t); c = b(0.47, 0.40, 0.55); mot = vipp(t)
    kp = c + d_kjelde * nrm(b(0.47, 0.47, 0.30) - c)
    k = straale(kp, c, W * LMW_KJELDE, K, spreiing=18, kutt=40, opning=0.012, bronn=45)
    nn = nrm(nrm(kp - c) + nrm(mot - c))
    a = fresnelspegel(k, c, nn, storleik=(0.19, 0.125), n=n_flis, rull=rull)
    kropp = [syl(b(FOT[0], FOT[1], 0), b(FOT[0], FOT[1], 0.04), 0.06), syl(b(FOT[0], FOT[1] + 0.03, 0.04), b(FOT[0], FOT[1] + 0.03, 0.62), 0.008),
             Skive(c - 0.012 * nn, nn, 0.18), Syl(kp - 0.05 * nrm(c - kp), kp - 0.004 * nrm(c - kp), 0.02)]
    return [k, a], kropp

G3 = [
    ('vipp-sol',       p_vipp(lambda u: sol(0.25 * u / 0.56))),
    ('vipp-vindauge',  p_vipp(feltmaske)),
    ('vipp-horisont',  p_vipp(horisontmaske, HORISONT_MIDT)),
    ('iris',           p_blad('iris')),
    ('soloppgang',     p_blad('blad')),
    ('dele-sol',       p_dele(lambda u: sol(0.25 * u / 0.56), rull=0)),
    ('dele-vindauge',  p_dele(lambda u: dreidd(feltmaske(u), 0, True), rull=0)),
    ('dele-horisont',  p_dele(horisontmaske, HORISONT_MIDT)),
    ('zoom',           p_zoom),
    ('skugge',         p_skugge),
    ('kule',           p_vipp(lambda u: sol(0.25 * u / 0.56), o=KULE)),
    ('ohp',            k_ohp),
    ('tak-sol',        g1(TAKPOS, b(0.47, 0.48, 1.78), 0.05, 0.14, stamme=False)),
    ('golv',           k_golv),
    ('plateprofil',    k_plateprofil),
    ('ideal',          g_ideal),
    ('onske-kort',     g1(HODE, VEGGSOL, 0.04, 0.07, u=0.14, tvang=0.004)),
]

# ------------------------------------------------------------------ generasjon 4: avgjerdssettet (fint, berre for valet)
# Fire opne spørsmål frå G3 avgjer kva som er dei tre beste:
#   (a) kva kostar jamnheit når kanten er mjuk? Overfylling (maska 5 cm større enn feltet) og gradert maske.
#   (b) kor mykje vegg i arbeid når spegelen deler strålen (q = 0,55 mot 0,75)?
#   (c) kan linsa 285 bli éin av dei tre når ho står der ho verkar (1,45 m unna), med mjuk kant og delt spegel?
#   (d) overgangen: sveipar vippen lyset over dataskjermen (lm på skjermen langs overgangen)?
# Settet held fram med kroppane frå G3 som står i konkurransen, referansen, ein som veltar og ein som ikkje kan lagast.

def feltmaske_m(u, marg=0.0, pos=HODE):
    """Feltmaska, trapeskorrigert, med marg (meter) rundt feltet: overfylling for jamnheit under mjuk kant."""
    hj = [b(-0.3 - marg, 0.05 - marg, 0), b(0.3 + marg, 0.05 - marg, 0), b(0.3 + marg, 0.45 + marg, 0), b(-0.3 - marg, 0.45 + marg, 0)]
    return mangekant(tilbake(pos, FELT, hj, u))

LANGPOS = GOLVPOS                     # linsa 285 der ho verkar: 1,45 m frå feltet, bak høgre skulder (hylle eller golvstong)
LANGVEGG = b(0.0, YV, 0.62)           # vindauget på veggen over skjermkanten, sett frå LANGPOS

def k_lang(kant=None, q1=None, mot0=LANGVEGG, marg=0.0):
    """Linsa 285 med fresnelplata som kondensor, 1,45 m unna. kant: mjuk kant ved defokus (maska innanfor fokus).
    q1 = None: hovudet vippar frå veggen til feltet. q1 = tal: frontflatespegelen deler strålen, delen q1 går til bordet."""
    def g(t):
        W, K = watt(t); pos = LANGPOS; r = float(np.linalg.norm(FELT - pos)); u = u_for(F_LINSE, r)
        if kant is not None: u = min(u, u_mjuk(F_LINSE, 0.045, r, kant))
        form = feltmaske_m(u, marg, pos)
        if q1 is None:
            mot = vipp(t, mot0); lys = [stroek(pos, mot, W, K, form, KIT, u=u)]; n = nrm(mot - pos)
        else:
            q = q1 * t; n = nrm(mot0 - pos)
            lys = [stroek(pos, mot0, W * (1 - q), K, dreidd(form, 0, True), KIT, u=u)]
            if q > 1e-6: lys.append(stroek(pos, FELT, W * q, K, form, KIT, u=u, spegel=1))
        return lys, [Syl(pos - 0.36 * n, pos - 0.004 * n, 0.15)]
    return g

FYLL = 0.05; JAMN = 1.5
G4 = [
    ('dele-vindauge',  p_dele(lambda u: dreidd(feltmaske(u), 0, True), rull=0)),                          # G3, q1 0,75
    ('dele-fyll',      p_dele(lambda u: dreidd(feltmaske_m(u, FYLL), 0, True), rull=0, grad=JAMN)),        # (a)
    ('dele-q55',       p_dele(lambda u: dreidd(feltmaske(u), 0, True), rull=0, q1=0.55)),                 # (b)
    ('dele-sol',       p_dele(lambda u: sol(0.25 * u / 0.56), rull=0)),                                    # G3
    ('vipp-vindauge',  p_vipp(feltmaske)),                                                                 # G3, (d)
    ('vipp-fyll',      p_vipp(lambda u: feltmaske_m(u, FYLL), grad=JAMN)),                                 # (a), (d)
    ('zoom',           p_zoom),                                                                            # G3
    ('soloppgang',     p_blad('blad')),                                                                    # G3
    ('golv',           k_golv),                                                                            # G3: skarp, vippar
    ('golv-mjuk',      k_lang(kant=KANT)),                                                                 # (c)
    ('golv-dele',      k_lang(kant=KANT, q1=0.75)),                                                        # (c)
    ('tak-sol',        g1(TAKPOS, b(0.47, 0.48, 1.78), 0.05, 0.14, stamme=False)),                         # G1/G3: linsa som rein stemning
    ('ideal',          g_ideal),                                                                           # referansen
    ('linse285-bord',  g2(KIT, u=F_LINSE, spegel=1, bronn=None)),                                          # VELTAR: linsa 285 i bordlampa
    ('onske-kort',     g1(HODE, VEGGSOL, 0.04, 0.07, u=0.14, tvang=0.004)),                                # KAN IKKJE LAGAST
]
TOPP3 = ['dele-vindauge', 'golv-dele', 'zoom']     # valt etter G4, sjå funn.md

def fin():
    """Fint søk for avgjerda: kva kostar jamnheit? Høgd på hovudet, gradert maske og overfylling."""
    print('h, m   jamn  kant   felt lx  jamnheit  nytte  W350  lm/W')
    for h in (0.36, 0.45, 0.55):
        pos = b(0.47, 0.40, h); r = float(np.linalg.norm(FELT - pos))
        for jamn in (0.0, 1.5, 3.0):
            for marg in (0.0, 0.04):
                W, K = watt(1.0); u = u_mjuk(0.060, 0.030, r, KANT)
                l = stroek(pos, FELT, W, K, rekt(0.6 + 2 * marg, 0.4 + 2 * marg, 0, 0.25), PROD(), koord='bord', u=u, bronn=45, jamn=jamn)
                d = tal([l], [])
                print('%.2f   %.1f   +%.0f cm   %5.0f    %.2f     %3.0f %%  %.2f  %.1f' % (h, jamn, marg * 100, d['E_felt'], d['U'], d['nytte'] * 100,
                                                                                    d['W'] * 350 / d['E_felt'], l.info['lmw']))

def overgangstabell(greps, fil):
    L = ['| Lysgrep | topp | sprang | jamn auke | mot auget langs overgangen, cd/m² | felt, lx | vegg, lx | lm på skjermen (t = 0, 0,25, 0,5, 0,75, 1) |',
         '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for namn, g in greps:
        _, m = overgang(g, n=5)
        sk = [lm_skjerm(g(float(t))[0]) for t in m['t']]
        L.append('| %s | %.2f | %.2f | %.2f | %s | %s | %s | %s |' % (namn, m['topp'], m['sprang'], m['jamn_auke'],
                 ', '.join('%.0f' % x for x in m['auge']), ', '.join('%.0f' % x for x in m['felt']),
                 ', '.join('%.0f' % x for x in m['vegg']), ', '.join('%.0f' % x for x in sk)))
        print(L[-1])
    open(fil, 'w', encoding='utf-8').write('\n'.join(L) + '\n')

# ------------------------------------------------------------------ rapport og køyring

def strok_info(g):
    ut = {}
    for t in (0.0, 1.0):
        lys, _ = g(t)
        ut[t] = [l.info for l in lys if hasattr(l, 'info')]
    return ut

def rapport(greps, fil, tittel):
    L = ['# ' + tittel, '',
         'Strålegangen er rekna i `familie.py` (tynn linse), ikkje i motoren. u: maske til linse. v\': der biletet er skarpt (negativ: virtuelt). '
         'r: linse til flata. Skala: r / u. Kant: 10 til 90 % av lyskanten. lm/W: lumen ut per watt inn. Kompakt: maske og lengd innanfor Ø 16 x 27,5 cm.', '',
         '| Lysgrep | t | Optikk | u, mm | v\', m | r, m | Skala | Maske Ø, mm | Kant, mm | lm/W | Lengd, mm | Breidd, mm | Kompakt | Ledd | Merknad |',
         '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for namn, g in greps:
        inf = strok_info(g)
        for t in (0.0, 1.0):
            for i in inf[t]:
                vf = 'uendeleg' if not np.isfinite(i['vf']) else '%.2f' % i['vf']
                L.append('| %s | %d | %s | %.0f | %s | %.2f | %.1f | %.0f | %.0f | %.1f | %.0f | %.0f | %s | %s | %s |'
                         % (namn, t, i['optikk'], i['u'] * 1000, vf, i['r'], i['skala'], i['maske'] * 1000, i['kant'] * 1000,
                            i['lmw'], i['lengd'] * 1000, i['breidd'] * 1000, 'ja' if i['kompakt'] else 'nei', i['ledd'], i['merk']))
    open(fil, 'w', encoding='utf-8').write('\n'.join(L) + '\n')

def skriv_rad(r):
    print('%-16s felt %5.0f lx  jamnh %.2f  nytte %3.0f %%  W350 %6.2f  vegg %4.0f  ansikt %3.0f  auge %5.0f  | stemning: auge %4.0f  felt %4.0f  vegg %4.0f | likskap %.2f'
          % (r['namn'], r['felt'], r['jamnheit'], r['nytte'] * 100, r['W350'], r['vegg'], r['ansikt'], r['auge'], r['s_auge'], r['s_felt'], r['s_vegg'], r['likskap']))

def rekn():
    print('TYNN LINSE, f = 285 mm, opning 70 mm')
    print('  minste avstand frå maske til skarpt bilete: 4 f = %.2f m' % minste_kast(F_LINSE))
    for v in (0.30, 0.61, 1.0, 1.5, 2.0):
        u = u_for(F_LINSE, v)
        print('  kast %.2f m: ' % v + ('u = %.0f mm, m = %.2f, maske for 0,6 m felt: %.0f mm' % (u * 1000, v / u, 600 * u / v) if u else 'inga avbilding (v <= f)'))
    print('  uendeleg fokus (u = f): skala r / f. 0,6 m felt på 0,61 m krev maske %.0f mm, uskarpskive = lysfylt opning (45 til 70 mm)' % (600 * F_LINSE / 0.61))
    print('KOMPAKT LAMPE, kast 0,61 m, felt 0,6 m: f = v / (1 + m)')
    for mb in (0.04, 0.06, 0.10):
        print('  maske %.0f mm: m = %.0f, f = %.0f mm' % (mb * 1000, 0.6 / mb, 610 / (1 + 0.6 / mb)))
    print('  opning frå étendue: E = tau L A / v². 350 lx (595 lx på tvers ved 54°) med L = 2,5e6 cd/m² (COB): D = %.0f mm. Med 3e7 (éin brikke): D = %.1f mm'
          % (2000 * math.sqrt(595 * 0.61 ** 2 / 0.8 / 2.5e6 / PI), 2000 * math.sqrt(595 * 0.61 ** 2 / 0.8 / 3e7 / PI)))
    print('VERKNADSGRAD')
    print('  naken LED, inga kondensor, linsa 352 mm unna: sin² = %.4f' % lambert_sirkel(D_LINSE, 0.352))
    print('  naken LED 0,40 m over fresnelplata: plata fangar %.3f' % lambert_rekt(PLATE, PLATE, 0.40))
    print('  kjeldebiletet frå plata i linseopninga (u = 0,352): %.3f' % pupill(D_LINSE, 0.352))
    print('  fresnelplata som avbildande spegel: 4 f = %.2f m, opning f/%.2f, fangar %.2f av ei lambertsk maske 0,25 m unna'
          % (4 * F_PLATE, F_PLATE / PLATE, lambert_rekt(PLATE, PLATE, 0.25)))
    for ut in ((0.066, 0.048), (0.066, 0.015)):
        gj, ute, spr = trakt((0.005, 0.005 * ut[1] / ut[0]), ut, 0.06, 0.0667, 0.030)
        print('  trakt 5 mm -> %.0f x %.0f mm, lengd 60: ut av trakta %.2f, gjennom linsa Ø 30 %.2f, sprett %.1f' % (ut[0] * 1000, ut[1] * 1000, ute, gj, spr))

def kjor(greps, namn, tittel, px=0):
    mappe = HER if namn is None else os.path.join(HER, namn)
    os.makedirs(mappe, exist_ok=True)
    rapport(greps, os.path.join(mappe, 'straalegang.md'), tittel)
    rader = familie(greps, mappe, px=px)
    for r in rader: skriv_rad(r)
    return rader

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    a = sys.argv[1:]
    if '--rekn' in a: rekn()
    if '--g1' in a: kjor(G1, 'g1', 'Generasjon 1: kvar i rommet verkar linsa på 285 mm')
    if '--g2' in a: kjor(G2, 'g2', 'Generasjon 2: kva optikk gjev eit felt på bordet')
    if '--fin' in a: fin()
    if '--g3' in a:
        kjor(G3, 'g3', 'Generasjon 3: forma på lyset og overgangen')
        overgangstabell(G3, os.path.join(HER, 'g3', 'overgang.md'))
    if '--g4' in a:
        kjor(G4, 'g4', 'Generasjon 4: avgjerdssettet')
    if '--g4-overgang' in a:
        overgangstabell(G4, os.path.join(HER, 'g4', 'overgang.md'))
    if '--brett' in a:
        rapport(G4, os.path.join(HER, 'straalegang.md'), 'Siste generasjon (G4): strålegangen')
        for r in familie(G4, HER, px=200): skriv_rad(r)
    if '--par' in a:
        d = dict(G4)
        for namn in TOPP3: par(d[namn], os.path.join(HER, 'par-%s.png' % namn), px=240, ss=1, steg=(0, 0.5, 1))
