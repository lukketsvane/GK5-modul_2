# -*- coding: utf-8 -*-
"""lys_sjekk.py  ·  kva lampa gjer med lyset: ruta lyser opp gjennom arket og ned på bordet. Overslag med same motor som A, B og C.

ANTAKING: 60 % av lyset frå stripa kjem inn i plata. Av det går 30 % opp gjennom arket, 60 % ned og 10 % ned ved den skrå kanten.
Lampa står til høgre for skjermen, midt i foten 47 cm til høgre og 30 cm inn på bordet."""
import os, sys, math
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HER, '..'))
os.environ.setdefault('LYSSKISSE_POLGE', '0')
import lampe as L
from rute import rute, utfordeling, ls
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
b = ls.b
PLASS = np.array([0.47, 0.30])
INN, OPP, NED, KANT = 0.60, 0.30, 0.60, 0.10
F_OPP = utfordeling(innside='flat'); F_NED = utfordeling(film=None)

def lys(W, vinkel, K=2700):
    t = math.radians(vinkel)
    s = np.array([0.0, -math.cos(t), -math.sin(t)]); n = np.array([0.0, -math.sin(t), math.cos(t)])
    akse = np.array([0.0, L.YB / 1000, L.AKSE_H / 1000])
    xm = 0.5 * (L.X_RUTE0 + L.X_RUTE1) / 1000
    c = b(PLASS[0] + xm, PLASS[1], 0) + akse + s * (L.U_KANT + L.RUTE_D / 2) / 1000
    lm = W * 100 * INN
    st = (L.RUTE_B / 1000, L.RUTE_D / 1000)
    opp = rute(c + n * 0.002, n, s, st, lm * OPP / F_OPP['verknad'], K, F_OPP, 'opp')       # rillene langs s: på tvers av bjelken
    ned = rute(c - n * 0.002, -n, s, st, lm * NED / F_NED['verknad'], K, F_NED, 'ned')
    kc = b(PLASS[0] + xm, PLASS[1], 0) + akse + s * (L.U_KANT + L.RUTE_D) / 1000
    kant = ls.flate(kc - n * 0.003, -n, (L.RUTE_B / 1000, 0.004), lm * KANT, K, opp=(1, 0, 0))     # den skrå kanten speglar lyset ned gjennom undersida
    for l in (opp, ned): l.lm = 0.0
    kant.lm = W * 100; kant.mater = True; kant.lm_ut = lm * KANT
    return [opp, ned, kant], c

for W in (0.5, 2.0):
    for v in (20, 35, 60):
        ll, c = lys(W, v)
        d = ls.tal(ll, [])
        # bordet under og framfor ruta
        xs = np.linspace(c[0] - 0.2, c[0] + 0.2, 9); ys = np.linspace(c[1] - 0.25, c[1] + 0.15, 9)
        P = np.array([[x, y, ls.ZB + 0.001] for x in xs for y in ys]); N = np.tile([0, 0, 1.0], (len(P), 1))
        E = ls.E_direkte(P, N, ll, list(ls.STATISK)) @ ls.LUM
        print('%.1f W, helling %2d°: bordet under ruta snitt %4.0f lx, høgst %4.0f · feltet framfor skjermen %3.0f lx · ansikt %3.0f lx · '
              'mot auget 25/47/60 cm %5.0f/%5.0f/%5.0f cd/m² · skjermflata %3.0f lx'
              % (W, v, E.mean(), E.max(), d['E_felt'], d['E_ansikt'], d['L_auge25'], d['L_auge47'], d['L_auge60'], d['E_skjerm']), flush=True)
