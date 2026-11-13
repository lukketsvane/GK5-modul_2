# -*- coding: utf-8 -*-
"""Motbevisar 1 for F1: skjermlys i (a)/(b). Brukar sjølve målereiskapen (felles.py + motorane), ikkje granskarskripta.
1) arbeidstilstanden frå fe.sok, E på skjermflata med fe.illum (grov og fin opning)
2) ψ-sveip 1°: minst skjermlys med vis/refl False (3 auge i felles) og U0 >= 0,4; òg 8 auge
3) plassering (yp, hp) utvida: finst det ein stad der vrivinkelen held skjermlyset <= 100 lx?
4) kontrastaritmetikk
"""
import os, sys, math, time, json
import numpy as np
ROOT = r'C:\Users\Iver\Documents\northern-lampe'
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form01')); sys.path.insert(0, os.path.join(ROOT, 'form02'))
import felles as fe
import val as V2
M1 = V2.M1
T0 = time.time()
UP, MOT = np.array([0, 0, 1.0]), np.array([0, -1.0, 0])
xs, zs = np.meshgrid(fe.SCR['x0'] + (np.arange(55) + .5) / 55 * 0.55, fe.SCR['z0'] + (np.arange(32) + .5) / 32 * 0.32)
SKJ = np.c_[xs.ravel(), np.full(xs.size, fe.SCR['y'] - 1e-4), zs.ravel()]
SKJg = SKJ[::7]
AUGE8 = np.array([(0, -0.30, 0.45), (-0.15, -0.30, 0.45), (0.15, -0.30, 0.45), (0, -0.15, 0.45), (0, -0.30, 0.40), (0, -0.30, 0.50), (0, -0.15, 0.40), (0, -0.15, 0.50)])


def vis8(P, N):
    front = ((AUGE8[None] - P[:, None]) * N[:, None]).sum(-1) > 0
    return bool((front & ~fe.screen_block(P, AUGE8)).any())


Ba, ta, Sa = V2.tal_bru(15.0)
print(f"(a) tal_bru(15): yp {Ba['yp']} hp {Ba['hp']} a {Ba['a']}  ({time.time()-T0:.0f} s)")
Bb = dict(V2.B_KROK)
KONF = {'a': (Ba, lambda B, s, n=None, nt=3: M1.opning(B, s, nt, n), M1.eta(Ba)),
        'b': (Bb, lambda B, s, n=None, nt=3: V2.opning_krok(B, s, nt, n), V2.eta_krok(Bb))}
UT = {}
for k, (B, op, eta) in KONF.items():
    S = fe.sok(B, M1.PSIS, op, eta)
    W = S['work']
    psiW = math.degrees(W['s'])
    P, N, dA = op(B, W['s'])
    L = W['k'] * W['Phi']
    Es = fe.illum(P, N, dA, SKJ, MOT) * L
    Pf, Nf, dAf = op(B, W['s'], 257, 15)
    rf = fe.lys(Pf, Nf, dAf, eta)
    Esf = fe.illum(Pf, Nf, dAf, SKJ, MOT) * rf['k'] * rf['Phi']
    UT[k] = dict(psi=psiW, Phi=W['Phi'], U0=W['U0'], vis=W['vis'], refl=W['refl'], E_skjerm=Es.mean(), E_maks=Es.max(), Phi_fin=rf['Phi'], E_skjerm_fin=Esf.mean(), E_maks_fin=Esf.max())
    print(f"({k}) arbeid ψ {psiW:+.0f}  Φ {W['Phi']:.1f} lm  U0 {W['U0']:.3f}  vis {W['vis']} refl {W['refl']}  skjerm {Es.mean():.1f} lx (maks {Es.max():.0f})"
          f"  | fin opning: Φ {rf['Phi']:.1f}  skjerm {Esf.mean():.1f} (maks {Esf.max():.0f})")
    # ψ-sveip 1°
    rows = []
    for psi in range(-60, 21):
        P, N, dA = op(B, math.radians(psi))
        r = fe.lys(P, N, dA, eta)
        E = fe.illum(P, N, dA, SKJg, MOT).mean() * r['k'] * r['Phi']
        rows.append(dict(psi=psi, Phi=r['Phi'], U0=r['U0'], vis=r['vis'], refl=r['refl'], vis8=vis8(P, N), E=E))
    ok3 = [r for r in rows if not r['vis'] and not r['refl'] and r['U0'] >= fe.U0_MIN]
    ok8 = [r for r in rows if not r['vis8'] and not r['refl'] and r['U0'] >= fe.U0_MIN]
    b3, b8 = min(ok3, key=lambda r: r['E']), min(ok8, key=lambda r: r['E'])
    under100 = [r['psi'] for r in rows if r['E'] <= 100]
    print(f"    sveip: minst skjermlys skjult (3 auge): ψ {b3['psi']:+d} {b3['E']:.0f} lx Φ {b3['Phi']:.0f}   skjult for 8: ψ {b8['psi']:+d} {b8['E']:.0f} lx Φ {b8['Phi']:.0f}"
          f"   ψ med E <= 100 lx: {under100[:3]}...{under100[-3:] if under100 else ''}  (synleg der: {[r['vis'] for r in rows if r['E']<=100][:3]})")
    print("    " + "  ".join(f"{r['psi']:+d}:{r['E']:.0f}/{'V' if r['vis'] else '-'}" for r in rows if r['psi'] % 5 == 0))
    UT[k]['sveip'] = dict(min3=b3, min8=b8, min_E_alle=min(r['E'] for r in rows))

# 3) plassering, (a)-røyret: kan yp/hp + ψ gje <= 100 lx med kjelda skjult? (ser bort frå SYN_MIN/kollisjon her)
print('\nplassering (a)-røyr, ψ −60..+20 i 2°: minst skjermlys med vis/refl False og U0 >= 0,4')
B0, op, _ = KONF['a']
best = []
for yp in (0.10, 0.18, 0.25, 0.32, 0.40):
    line = []
    for hp in (0.54, 0.62, 0.70, 0.80):
        B = dict(B0, yp=yp, hp=hp)
        eta = M1.eta(B)
        m = None
        for psi in range(-60, 21, 2):
            P, N, dA = op(B, math.radians(psi))
            r = fe.lys(P, N, dA, eta)
            if r['vis'] or r['refl'] or r['U0'] < fe.U0_MIN:
                continue
            E = fe.illum(P, N, dA, SKJg, MOT).mean() * r['k'] * r['Phi']
            if m is None or E < m[1]:
                m = (psi, E, r['Phi'])
        # SYN_MIN: røyret over skjermen minst 15° over augehøgd
        elev = math.degrees(math.atan2(hp - 0.022 - 0.45, yp + 0.30))
        line.append(f"hp {hp:.2f}: " + (f"ψ {m[0]:+d} {m[1]:4.0f} lx Φ {m[2]:4.0f}" if m else 'ingen') + f" elev {elev:4.1f}°")
        if m: best.append((m[1], yp, hp, m[0], m[2], elev))
    print(f"  yp {yp:.2f}  " + " | ".join(line), flush=True)
best.sort()
print('  lågaste:', [tuple(round(x, 2) for x in b) for b in best[:4]])
UT['plassering_best'] = best[:6]

# 4) kontrast
LW, LB = 200.0, 0.2
for k in 'ab':
    E = UT[k]['E_skjerm']
    for rho in (0.04, 0.01):
        Lr = rho * E / math.pi
        print(f"({k}) ρ {rho}: L_r {Lr:.2f} cd/m²  CR {(LW+Lr)/(LB+Lr):.1f}:1  svart ×{(LB+Lr)/LB:.1f}")
Lr = 0.04 * 8.78 / math.pi
print(f"(c) 8,78 lx ρ 0,04: CR {(LW+Lr)/(LB+Lr):.0f}:1")
print(f'({time.time()-T0:.0f} s)')
