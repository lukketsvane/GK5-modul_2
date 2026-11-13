# -*- coding: utf-8 -*-
"""Etterprøving av dei tre beste i familien PROJEKTOR: dele-vindauge, golv-dele, zoom.

  python etterproving.py

Endrar ikkje familie.py eller motoren. Køyrer tal() og overgang() på nytt, prøver andre augehøgder,
sprut 5 % i staden for 2 %, og reknar på nytt to ledd i verknadsgraden som familie.py hoppar over:
(1) maska i trakta skuggar bort lyset utanfor opninga, (2) kjelda over fresnelplata må få lyset inn i maska.
"""
import sys, os, math
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
sys.path.insert(0, os.path.join(HER, '..', '..', 'lysskisse'))
import lysskisse
from lysskisse import *
import familie as F

try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass

G = dict(F.G4)
NAMN = ['dele-vindauge', 'golv-dele', 'zoom']
FUNN = {   # tal frå funn.md / tal.md / g4-overgang (agenten sine)
    'dele-vindauge': dict(W350=1.78, felt=981, jamnheit=0.24, auge=358, vegg=106, ansikt=49, s_auge=265, s_vegg=91, likskap=0.35),
    'golv-dele':     dict(W350=4.58, felt=382, jamnheit=0.58, auge=169, vegg=43, ansikt=26, s_auge=62, s_vegg=37, likskap=0.37),
    'zoom':          dict(W350=1.83, felt=956, jamnheit=0.36, auge=324, vegg=18, ansikt=42, s_auge=167, s_vegg=5, likskap=0.94),
}
OVERGANG = {'dele-vindauge': (0.93, 0.06), 'golv-dele': (0.53, 0.07), 'zoom': (0.87, 0.01)}

def L(d): return max(d['L_lampe'], d['L_flate'])

def tal_par(g):
    s = tal(*g(0.0)); a = tal(*g(1.0))
    return s, a

print('== 1 Tala på nytt (avvik mot funn.md) ==')
RAD = {}
for n in NAMN:
    s, a = tal_par(G[n])
    r = dict(W350=a['W'] * 350 / a['E_felt'], felt=a['E_felt'], jamnheit=a['U'], auge=L(a), vegg=a['E_vegg'], ansikt=a['E_ansikt'],
             s_auge=L(s), s_vegg=s['E_vegg'], likskap=likskap(s['_fordeling'], a['_fordeling']))
    RAD[n] = (s, a, r)
    print(n, ' W %.2f  lm %.0f  skjerm/felt %.2f  L_spegl %.0f / %.0f' % (a['W'], a['lm'], a['E_skjerm'] / a['E_felt'], a['L_spegl'], s['L_spegl']))
    for k, v in r.items():
        f = FUNN[n][k]; av = (v - f) / f if f else 0.0
        print('   %-9s %8.2f   funn %8.2f   avvik %+5.1f %%%s' % (k, v, f, av * 100, '  FEIL' if abs(av) > 0.05 else ''))
    _, m = overgang(G[n], n=5)
    sk = [F.lm_skjerm(G[n](float(t))[0]) for t in m['t']]
    print('   overgang: topp %.2f (funn %.2f)  sprang %.2f (funn %.2f)  jamn %.2f' % (m['topp'], OVERGANG[n][0], m['sprang'], OVERGANG[n][1], m['jamn_auke']))
    print('   auge', [round(x) for x in m['auge']], ' felt', [round(x) for x in m['felt']], ' vegg', [round(x) for x in m['vegg']], ' lm skjerm', [round(x, 1) for x in sk])

print('\n== 2 Andre augehøgder (F1: 25 til 60 cm, F5: 1500 / 500 cd/m²) ==')
z0 = float(lysskisse.AUGE[2])
for dh in (0.25, 0.60):
    lysskisse.AUGE[2] = ZB + dh
    for n in NAMN:
        ut = []
        for t in (0.0, 0.5, 1.0):
            d = tal(*G[n](t)); ut.append('t=%.1f lampe %5.0f flate %4.0f spegl %5.0f' % (t, d['L_lampe'], d['L_flate'], d['L_spegl']))
        print('auge %.2f m  %-14s %s' % (dh, n, ' | '.join(ut)))
lysskisse.AUGE[2] = z0

print('\n== 3 Sprut 5 % i staden for 2 % (ANTAKING i motoren) ==')
s0 = F.SPRUT; F.SPRUT = 0.05
for n in NAMN:
    s, a = tal_par(G[n])
    print('%-14s arbeid: auge %5.0f felt %4.0f vegg %4.0f | stemning: auge %4.0f vegg %4.0f' % (n, L(a), a['E_felt'], a['E_vegg'], L(s), s['E_vegg']))
F.SPRUT = s0

print('\n== 4 Maska i trakta: kor mykje av trakt-lyset slepp gjennom opninga? ==')
def trakt_m(maskf, inn, ut, Lt, u, D, rho=0.85, n=30000, seed=3):
    """Kopi av familie.trakt, men strålen må òg gå gjennom opninga i maska (maskf > 0) i utgangsplanet."""
    rng = np.random.default_rng(seed)
    w0, h0 = inn; w1, h1 = ut
    P = np.stack([(rng.random(n) - .5) * w0, (rng.random(n) - .5) * h0, np.zeros(n)], 1)
    r1 = rng.random(n); ph = 2 * PI * rng.random(n); st = np.sqrt(r1)
    V = np.stack([st * np.cos(ph), st * np.sin(ph), np.sqrt(1 - r1)], 1)
    ax, ay = (w1 - w0) / (2 * Lt), (h1 - h0) / (2 * Lt)
    vegger = [((-1, 0, ax), (1, 0, -ax), w0 / 2), ((1, 0, ax), (-1, 0, -ax), w0 / 2),
              ((0, -1, ay), (0, 1, -ay), h0 / 2), ((0, 1, ay), (0, -1, -ay), h0 / 2)]
    vekt = np.ones(n); ferdig = np.zeros(n, bool); tapt = np.zeros(n, bool)
    for _ in range(60):
        akt = ~(ferdig | tapt)
        if not akt.any(): break
        with np.errstate(all='ignore'):
            tz = np.where(V[:, 2] > 1e-9, (Lt - P[:, 2]) / V[:, 2], np.inf)
            t0 = np.where(V[:, 2] < -1e-9, -P[:, 2] / V[:, 2], np.inf)
            best = np.minimum(tz, t0); kva = np.where(tz <= t0, -1, -2)
            for i, (nn, pl, c0) in enumerate(vegger):
                pl = np.array(pl, float); den = V @ pl; tt = (c0 - P @ pl) / den
                ok = (den > 1e-12) & (tt > 1e-9) & (tt < best)
                best = np.where(ok, tt, best); kva = np.where(ok, i, kva)
        P = np.where(akt[:, None], P + best[:, None] * V, P)
        ferdig |= akt & (kva == -1); tapt |= akt & (kva == -2)
        for i, (nn, pl, c0) in enumerate(vegger):
            m = akt & (kva == i)
            if m.any():
                nn = np.array(nn, float); nn /= np.linalg.norm(nn)
                V[m] = V[m] - 2 * (V[m] @ nn)[:, None] * nn; vekt[m] *= rho
    f = ferdig; best_all = best_m = 0.0
    inne_m = maskf(P[f, 0], P[f, 1]) > 0
    for Fl in np.linspace(0.4, 1.6, 13) * (1.0 / (1.0 / Lt + 1.0 / u)):
        sx = V[f, 0] / V[f, 2] - P[f, 0] / Fl; sy = V[f, 1] / V[f, 2] - P[f, 1] / Fl
        inne = np.hypot(P[f, 0] + sx * u, P[f, 1] + sy * u) <= D / 2
        best_all = max(best_all, float((vekt[f] * inne).sum() / n))
        best_m = max(best_m, float((vekt[f] * inne * inne_m).sum() / n))
    return best_all, best_m

def maskeboks(form, u):
    N = 401; g = (np.arange(N) + 0.5) / N * 3 * u - 1.5 * u; X, Y = np.meshgrid(g, g)
    inne = form(X, Y) > 0
    return X[inne].min(), X[inne].max(), Y[inne].min(), Y[inne].max(), inne.sum() * (g[1] - g[0]) ** 2

u_d = F.U_P()
former = {'dele-vindauge': (F.dreidd(F.feltmaske(u_d), 0, True), u_d),
          'zoom (t=0, u=67)': (F.sol(0.020), F.u_for(0.060, 0.61)), 'zoom (t=1, u=42)': (F.sol(0.020), 0.042)}
for n, (form, u) in former.items():
    x0, x1, y0, y1, A = maskeboks(form, u)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    fs = lambda x, y, form=form, cx=cx, cy=cy: form(x + cx, y + cy)
    rot = lambda x, y, form=form, cx=cx, cy=cy: form(y + cx, x + cy)
    a66, m66 = trakt_m(fs, (0.005, 0.005 * 0.048 / 0.066), (0.066, 0.048), 0.06, u, 0.030)
    _, m66r = trakt_m(rot, (0.005, 0.005 * 0.048 / 0.066), (0.066, 0.048), 0.06, u, 0.030)
    bw, bh = x1 - x0, y1 - y0
    a_b, m_b = trakt_m(fs, (0.005, 0.005 * bh / bw), (bw, bh), 0.06, u, 0.030)
    print('%-18s maske %.0f x %.0f mm, areal %.0f mm² (trakt 66 x 48 = 3168 mm²)' % (n, bw * 1000, bh * 1000, A * 1e6))
    print('   trakt 66 x 48: gjennom linsa %.3f, gjennom maske og linse %.3f (rotert %.3f): del %.2f'
          % (a66, m66, m66r, max(m66, m66r) / a66))
    print('   trakt tilpassa maskeboksen %.0f x %.0f: gjennom linsa %.3f, gjennom maske og linse %.3f: mot familie.py %.2f'
          % (bw * 1000, bh * 1000, a_b, m_b, m_b / a66))

print('\n== 5 Kjelda over fresnelplata (golv-dele): kjem lyset inn i maska? ==')
lys, _ = G['golv-dele'](1.0)
inf = [l.info for l in lys if hasattr(l, 'info')][-1]
s_k, fot_k, _ = F.kit_kjelde(inf['u'], inf['maske'])
Rm = inf['maske'] / 2
for namn, ra, half in (('lykt Ø 25, ±20° (G_LYKT i familie.py)', 0.0125, 20), ('telefonlykt, emitter 1,5 mm, ±35°', 0.00075, 35)):
    geo = min(1.0, (Rm / (s_k * math.tan(math.radians(half)))) ** 2)
    G_src = PI * (PI * ra * ra) * math.sin(math.radians(half)) ** 2
    G_maske = inf['A'] * PI * (ra / s_k) ** 2
    print('%-38s kjelda %.2f m over plata, maske Ø %.0f mm: del av strålen i maskesirkelen %.3f, étendue-tak %.3f (familie.py set hale 0,90)'
          % (namn, s_k, inf['maske'] * 1000, geo, min(1.0, G_maske / G_src)))
D_trong = 2 * s_k * math.sqrt(F.G_LYKT / (PI * inf['A'])) if inf['A'] else 0
print('   minste opning på kjelda for at étendue-taket skal vere 1 (med G_LYKT): Ø %.0f mm' % (D_trong * 1000))
