# -*- coding: utf-8 -*-
"""Motbevis F3 (spegling med skjermtilt). Eigen metode: eksakt projeksjon av opningsrektangelet frå spegla auge
gjennom eit tilta skjermplan (shapely), pluss felles.reflected() generalisert til tilt på punkta frå motoren.
Køyr: PYTHONIOENCODING=utf-8 python stadfest_F3_1.py
"""
import os, sys, math, json
import numpy as np
from shapely.geometry import Polygon, box
HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form01')); sys.path.insert(0, os.path.join(ROOT, 'form02'))
import felles as fe
import motor as M1
import val as V2

SCR = fe.SCR
H_S = SCR['z1'] - SCR['z0']
AUGE = {'nom': (0, -0.30, 0.45), 'x-15': (-0.15, -0.30, 0.45), 'x+15': (0.15, -0.30, 0.45),
        'lag5': (0, -0.30, 0.40), 'hog5': (0, -0.30, 0.50), 'fram15': (0, -0.15, 0.45), 'fram15lag5': (0, -0.15, 0.40)}


def plan(tilt):
    t = math.radians(tilt)
    o = np.array([0.0, SCR['y'], SCR['z0']])
    u = np.array([0.0, math.sin(t), math.cos(t)])        # opp langs skjermen, toppen bakover
    m = np.array([0.0, -math.cos(t), math.sin(t)])       # normal mot brukaren
    return o, u, m


def speg_poly(c, e, v, xs, E, tilt):
    """Eksakt: projiser kvart opningsrektangel frå spegla auge E' til skjermplanet, snitt med skjermrektangelet.
    Returnerer del av skjermflata (0..1) og om nokon del er spegla."""
    o, u, m = plan(tilt)
    E = np.asarray(E, float)
    Em = E - 2 * ((E - o) @ m) * m
    if (Em - c) @ e <= 0:                                # opninga vender bort frå spegelauget
        return 0.0
    hv = fe_HV
    scr = box(SCR['x0'], 0.0, SCR['x1'], H_S)
    areal = 0.0
    for a0, a1 in xs:
        hj = [c + a0 * np.array([1.0, 0, 0]) - hv * v, c + a1 * np.array([1.0, 0, 0]) - hv * v,
              c + a1 * np.array([1.0, 0, 0]) + hv * v, c + a0 * np.array([1.0, 0, 0]) + hv * v]
        q = []
        for P in hj:
            if (P - o) @ m <= 0:                         # hjørnet bak skjermplanet
                return float('nan')
            s = ((o - Em) @ m) / ((P - Em) @ m)
            Q = Em + s * (P - Em)
            q.append(((Q - o)[0], (Q - o) @ u))
        areal += Polygon(q).intersection(scr).area
    return areal / scr.area


def refl_tilt_pts(P, N, E, tilt):
    """felles.reflected() med tilta plan, punktvis på motorpunkta."""
    o, u, m = plan(tilt)
    E = np.asarray(E, float)
    Em = E - 2 * ((E - o) @ m) * m
    fr = (P - o) @ m > 0
    s = ((o - Em) @ m) / ((P - Em) @ m)
    Q = Em + s[:, None] * (P - Em)
    lx, lh = Q[:, 0], (Q - o) @ u
    ok = fr & (s > 0) & (s < 1) & (lx > SCR['x0']) & (lx < SCR['x1']) & (lh > 0) & (lh < H_S) & (((Q - P) * N).sum(1) > 0)
    return bool(ok.any())


def synleg(c, e, E):
    E = np.asarray(E, float)
    d = E - c
    return float(math.degrees(math.asin(d @ e / np.linalg.norm(d))))


R, BETA = 0.022, math.radians(25.0)
fe_HV, RC = R * math.sin(BETA), R * math.cos(BETA)
UT = {}

# ---- konfigurasjonar frå motorane sjølve ----
Ba = dict(M1.FINAL, yp=0.18, hp=0.62, a=0.20)
Bb = dict(V2.B_KROK)
Sa = fe.sok(Ba, M1.PSIS, M1.opning, M1.eta(Ba))
Sb = fe.sok(Bb, M1.PSIS, V2.opning_krok, V2.eta_krok(Bb))
KONF = {}
for k, B, S, opn, xs in (('a', Ba, Sa, M1.opning, None), ('b', Bb, Sb, V2.opning_krok, None)):
    pw, pm = math.degrees(S['work']['s']), math.degrees(S['mood']['s'])
    P, N, dA = opn(B, S['work']['s'])
    L = S['work']['k'] * S['work']['Phi']
    xmax = np.abs(P[:, 0]).max()
    KONF[k] = dict(B=B, psi_arb=pw, psi_stem=pm, L_arb=L, Phi=S['work']['Phi'], vis=S['work']['vis'], refl=S['work']['refl'], opn=opn)
    print(f"({k}) ψ_arb {pw:+.0f}  ψ_stem {pm:+.0f}  Φ {S['work']['Phi']:.0f} lm  L_arb {L:.0f} cd/m²  vis {S['work']['vis']} refl {S['work']['refl']}  "
          f"0,04·L = {0.04*L:.0f} cd/m²  ({0.04*L/200:.2f} × 200)")
# opningsutstrekning (kontinuerleg, frå segmentkantane)
n = 33; tt = np.linspace(-1, 1, n); tm = (tt[:-1] + tt[1:]) / 2
ka = tt[1:][np.abs(tm) <= Ba['k']].max() * Ba['L'] / 2
kb = tt[1:][np.abs(tm) <= Bb['k']].max() * Bb['L'] / 2
XS = {'a': [(-ka, ka)], 'b': [(-kb, -0.02), (0.02, kb)]}
print('opning a', XS['a'], ' b', XS['b'])

# ---- skjerm vinkelrett på siktlina ----
for tilt in np.arange(10, 18, 0.1):
    o, u, m = plan(tilt)
    cs = o + 0.5 * H_S * u
    d = np.array(AUGE['nom']) - cs
    if math.degrees(math.acos(d @ m / np.linalg.norm(d))) < 0.05:
        break
print(f"skjerm vinkelrett på siktlina (nominelt auge til midten): tilt {tilt:.1f}°")
UT['tilt_vinkelrett'] = float(tilt)

TILTS = np.arange(0, 25.01, 0.25)
for k in 'ab':
    c_ = KONF[k]; B = c_['B']
    UT[k] = dict(psi_arb=c_['psi_arb'], psi_stem=c_['psi_stem'], L_arb=c_['L_arb'], Phi=c_['Phi'])
    for tilstand, psi in (('arbeid', c_['psi_arb']), ('stemning', c_['psi_stem'])):
        ps = math.radians(psi)
        e, v = M1.e_dir(ps), np.array([0.0, math.cos(ps), -math.sin(ps)])
        c = np.array([0.0, B['yp'], B['hp']]) + RC * e
        P, N, _ = c_['opn'](B, ps)
        rad = {}
        for nm, E in AUGE.items():
            kp = next((float(t) for t in TILTS if speg_poly(c, e, v, XS[k], E, t) > 0), None)
            kq = next((float(t) for t in TILTS if refl_tilt_pts(P, N, E, t)), None)
            a14 = speg_poly(c, e, v, XS[k], E, 14.0)
            a20 = speg_poly(c, e, v, XS[k], E, 20.0)
            rad[nm] = dict(krit_eksakt=kp, krit_punkt=kq, del14=a14, del20=a20, synleg_vinkel=synleg(c, e, E))
        # vinkel frå nedover-loddlina (γ) for den spegla strålen ved første tilt, nominelt auge
        kt = rad['nom']['krit_eksakt']
        gam = None
        if kt is not None:
            o, u, m = plan(kt)
            E = np.array(AUGE['nom'], float); Em = E - 2 * ((E - o) @ m) * m
            d = Em - c; d /= np.linalg.norm(d)
            gam = math.degrees(math.acos(-d[2]))
        UT[k][tilstand] = dict(psi=psi, auge=rad, gamma_nom=gam)
        print(f"({k}) {tilstand:8s} ψ {psi:+.0f}: " + '  '.join(f"{nm} {r['krit_eksakt']}/{r['krit_punkt']} (syn {r['synleg_vinkel']:+.1f}°)" for nm, r in rad.items()))
        print(f"      del av skjermen ved 14°: " + ' '.join(f"{nm} {100*r['del14']:.2f}%" for nm, r in rad.items()) +
              f"   ved 20° nom {100*rad['nom']['del20']:.2f} %   γ (frå nedover-lodd) ved første tilt, nom: {gam}")

# ---- felles.reflected() ved tilt 0 (kontroll) ----
for k in 'ab':
    B = KONF[k]['B']; ps = math.radians(KONF[k]['psi_arb'])
    P, N, _ = KONF[k]['opn'](B, ps)
    print(f"({k}) felles.reflected tilt 0: {fe.reflected(P, N)}   min tilt (felles-auge, punkt): "
          f"{min(UT[k]['arbeid']['auge'][n_]['krit_punkt'] or 99 for n_ in ('nom', 'x-15', 'x+15'))}")

print(json.dumps({k: UT[k]['arbeid']['gamma_nom'] for k in 'ab'}))
