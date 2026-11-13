# -*- coding: utf-8 -*-
"""Motbevis F2 (skjerming berre for tre auge). Eigen siktline gjennom slissa, med og utan godstjukn 1,2 mm (form01/logg.md l. 8).
Φ og skjermlys frå felles.py + motorane (ikkje frå fotometri_ab.py).
Køyr: PYTHONIOENCODING=utf-8 python stadfest_F2_1.py
"""
import os, sys, math, json
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HER)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form01')); sys.path.insert(0, os.path.join(ROOT, 'form02'))
import felles as fe
import motor as M1
import val as V2

RO, BETA = 0.022, math.radians(25.0)
KONF = {'a': dict(B=dict(M1.FINAL, yp=0.18, hp=0.62, a=0.15), xr=[(-0.315, 0.315)], op=M1.opning, eta=M1.eta),
        'b': dict(B=dict(V2.B_KROK), xr=[(-0.30, -0.02), (0.02, 0.30)], op=V2.opning_krok, eta=V2.eta_krok)}


def ev(psi):
    p = math.radians(psi)
    return np.array([0.0, -math.sin(p), -math.cos(p)]), np.array([0.0, math.cos(p), -math.sin(p)])


def vindauge(k, psi, E, t=0.0, kutt='radial', dx=0.005, dv=0.0002):
    """Romvinkel (projisert, sr) av den delen av kavitetet auga E ser gjennom slissa. t = godstjukn."""
    B = KONF[k]['B']; e, v = ev(psi); O = np.array([0.0, B['yp'], B['hp']])
    ao, ho = RO * math.sin(BETA), RO * math.cos(BETA)
    ri = RO - t
    if kutt == 'radial':
        ai, hi = ri * math.sin(BETA), ri * math.cos(BETA)
    else:                                   # fresa slisse med parallelle veggar
        ai, hi = ao, math.sqrt(ri ** 2 - ao ** 2)
    xs = np.concatenate([np.arange(a + dx / 2, b, dx) for a, b in KONF[k]['xr']])
    vs = np.arange(-ao + dv / 2, ao, dv)
    X, Vv = np.meshgrid(xs, vs, indexing='ij'); X, Vv = X.ravel(), Vv.ravel()
    P = O + X[:, None] * np.array([1.0, 0, 0]) + ho * e + Vv[:, None] * v
    D = P - E
    de = D @ e
    d = np.linalg.norm(D, axis=1)
    ok = de < 0                                            # auga framfor ytre korde
    if t > 0:
        s = (hi - ho) / np.where(ok, de, -1)
        Q = P + s[:, None] * D
        ok &= np.abs((Q - O) @ v) < ai
    cs = -de / d
    return float((np.where(ok, cs, 0) * dx * dv / d ** 2).sum())


def lysdata(k, psi):
    c = KONF[k]; B = c['B']
    P, N, dA = c['op'](B, math.radians(psi))
    r = fe.lys(P, N, dA, c['eta'](B))
    gx, gz = np.meshgrid(np.linspace(-0.27, 0.27, 23), np.linspace(0.105, 0.415, 14))
    S = np.c_[gx.ravel(), np.full(gx.size, fe.SCR['y'] - 1e-4), gz.ravel()]
    Es = fe.illum(P, N, dA, S, np.array([0, -1.0, 0])) * r['k'] * r['Phi']
    return dict(Phi=r['Phi'], U0=r['U0'], L=r['k'] * r['Phi'], E_skjerm=float(Es.mean()), vis3=r['vis'])


AUGE = {'nominell': (0, -0.30, 0.45), '5 lågare': (0, -0.30, 0.40), 'lener 15 fram': (0, -0.15, 0.45), 'fram 15 + lågare 5': (0, -0.15, 0.40),
        'hjørne x0,15 fram lågare': (0.15, -0.15, 0.40)}
VOL = np.array([(x, y, z) for x in (-0.15, -0.075, 0, 0.075, 0.15) for y in (-0.30, -0.225, -0.15) for z in (0.40, 0.425, 0.45, 0.475, 0.50)])
UT = {}
for k in 'ab':
    ld = lysdata(k, -20)
    print(f"\n({k}) ψ −20 (felles): Φ {ld['Phi']:.0f} lm  L {ld['L']:.0f} cd/m²  skjerm {ld['E_skjerm']:.0f} lx  synleg for 3 auge: {ld['vis3']}")
    UT[k] = dict(psi20=ld, auge={})
    for nm, E in AUGE.items():
        E = np.array(E, float)
        w0, w1, w2 = vindauge(k, -20, E, 0.0), vindauge(k, -20, E, 0.0012, 'radial'), vindauge(k, -20, E, 0.0012, 'fres')
        UT[k]['auge'][nm] = dict(E0=ld['L'] * w0, E_radial=ld['L'] * w1, E_fres=ld['L'] * w2)
        print(f"    {nm:26s} E ved auga: utan gods {ld['L']*w0:6.1f} lx | 1,2 mm radial {ld['L']*w1:6.1f} lx | 1,2 mm fresa {ld['L']*w2:6.1f} lx")
    # margin langs z (ned) og y (fram) frå nominelt auge, 1 mm steg
    for lab, t, ku in (('utan gods', 0.0, 'radial'), ('1,2 mm radial', 0.0012, 'radial'), ('1,2 mm fresa', 0.0012, 'fres')):
        dz = next(m for m in np.arange(0, 0.30, 0.001) if vindauge(k, -20, np.array([0, -0.30, 0.45 - m]), t, ku, 0.01, 0.0004) > 0)
        dy = next(m for m in np.arange(0, 0.40, 0.002) if vindauge(k, -20, np.array([0, -0.30 + m, 0.45]), t, ku, 0.01, 0.0004) > 0)
        # skjermvinkel EN 12464-1: vinkel under horisontalen på brukarsida der kavitetet vert synleg (fjernt auge, x 0)
        th = next(a for a in np.arange(0, 60, 0.1)
                  if vindauge(k, -20, np.array([0, KONF[k]['B']['yp'], KONF[k]['B']['hp']]) + 50 * np.array([0, -math.cos(math.radians(a)), -math.sin(math.radians(a))]), t, ku, 0.02, 0.0004) > 0)
        UT[k][f'margin {lab}'] = dict(ned_cm=dz * 100, fram_cm=dy * 100, skjermvinkel_deg=float(th))
        print(f"    margin {lab:14s}: {dz*100:4.1f} cm ned eller {dy*100:4.1f} cm fram.  Skjermvinkel mot brukaren (frå horisontalen) {th:.1f}°")
    # minste |ψ| der heile augevolumet er skjerma
    for lab, t, ku in (('utan gods', 0.0, 'radial'), ('1,2 mm radial', 0.0012, 'radial'), ('1,2 mm fresa', 0.0012, 'fres')):
        psi = next(p for p in range(-15, -50, -1) if all(vindauge(k, p, E, t, ku, 0.01, 0.0004) == 0 for E in VOL))
        q = lysdata(k, psi)
        UT[k][f'volum {lab}'] = dict(psi=psi, **q, dPhi_pst=100 * (q['Phi'] / ld['Phi'] - 1))
        print(f"    augevolum skjerma ({lab:14s}): ψ {psi}  Φ {q['Phi']:.0f} lm ({100*(q['Phi']/ld['Phi']-1):+.1f} %)  U0 {q['U0']:.2f}  skjerm {q['E_skjerm']:.0f} lx")
