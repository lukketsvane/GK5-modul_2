# -*- coding: utf-8 -*-
"""Motbevisar 1 for PR1: optikk berre i (c)?
Brukar den VERKELEGE optikk()/E_punkt() i form04/motor.py (ikkje premiss.py sin G_vifte) og flyttar LED-aksen til
plassen til (a) (form02 tal.json: yp 0,18 hp 0,62) og (b) (B_KROK: yp 0,25 hp 0,62). Same 7×5-oppgåvesone, same skjermskugge.
Prøver kor robust Φa/Φc er for (1) mjukare kant (σ 4 → 8 → 12°: ei lita linse i Ø44 har kortare brennvidd),
(2) lågare η (hulrom × plate), (3) ei prismeplate rett i opninga til røyret (b 18,6 mm, 42 mm frå LED på bakveggen).
Køyr: PYTHONIOENCODING=utf-8 python stadfest_PR1_1.py   (under 30 s)
"""
import os, sys, math, json
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form04'))
import felles as fe
import motor as M4

UP, SCRN = np.array([0, 0, 1.0]), np.array([0, -1.0, 0])
S = fe.SCR
sx, sz = np.meshgrid((np.arange(22) + .5) / 22 * (S['x1'] - S['x0']) + S['x0'], (np.arange(16) + .5) / 16 * (S['z1'] - S['z0']) + S['z0'])
SCRQ = np.c_[sx.ravel(), np.full(sx.size, S['y'] - 1e-4), sz.ravel()]


def mal(B, sigma=4.0, eta=None, alfas=np.radians(np.arange(-10, 10.1, 1.0))):
    M4.SIGMA = sigma; M4._opt.clear()
    O = M4.optikk(B)
    best = None
    for a in alfas:
        Et = M4.E_punkt(B, a, fe.TASK, UP)
        if Et.min() / Et.mean() < fe.U0_MIN:
            continue
        Phi = fe.E_TASK / Et.mean()
        if best is None or Phi < best[1]:
            best = (a, Phi, Et.min() / Et.mean())
    a, Phi, U0 = best
    k = 1.0 if eta is None else eta / O['eta']
    Es = M4.E_punkt(B, a, SCRQ, SCRN) * Phi
    return dict(alfa=round(math.degrees(a), 1), eta=round(O['eta'] * k, 3), Phi=round(Phi / k, 1), U0=round(U0, 3),
                E_skjerm=round(float(Es.mean()), 1), E_skjerm_maks=round(float(Es.max()), 1))


F = M4.FINAL
POS = dict(a=dict(ys=0.18, zs=0.62), b=dict(ys=0.25, zs=0.62), c=dict(ys=F['ys'], zs=F['zs']))
ut = {}
for sig in (4.0, 8.0, 12.0):
    for k, p in POS.items():
        ut[f'{k}_vifte_sig{int(sig)}'] = mal(dict(F, **p), sig)
for k in ('a', 'b'):
    ut[f'{k}_vifte_sig4_eta_hulrom'] = mal(dict(F, **POS[k]), 4.0, eta=0.674 * 0.85)
    ut[f'{k}_vifte_sig12_eta_hulrom'] = mal(dict(F, **POS[k]), 12.0, eta=0.674 * 0.85)
# prismeplate rett i røyropninga: b = 2R sin25° = 18,6 mm, LED på bakveggen d = R(1+cos25°) = 41,9 mm. Berre direkte lys vert styrt.
R, be = 0.022, math.radians(25)
Bt = dict(F, **POS['a'], bp=2 * R * math.sin(be), d=R * (1 + math.cos(be)))
ut['a_plate_i_opninga_sig4'] = mal(Bt, 4.0)
M4.SIGMA = 4.0; M4._opt.clear()
ut['a_plate_i_opninga_sig4']['samla'] = round(M4.optikk(Bt)['samla'], 3)

for k, v in ut.items():
    print(f'{k:30s}', v)
Phic = ut['c_vifte_sig4']['Phi']
print('\nΦ / Φc(σ4):', {k: round(v['Phi'] / Phic, 3) for k, v in ut.items()})
print('konsept: Φa/Φc =', round(1255 / 433, 2), ' Φb/Φc =', round(1311 / 433, 2))
