# -*- coding: utf-8 -*-
"""Motprov av PR6: felles.py brukar eigne premissar, ikkje kravspesifikasjonen (GK5-modul_2/grunnlag/04).
Rekna opp att med motoren sjølv (felles.lys/visible, form01 opning, form02 krok, form04 tal_mek), ikkje premiss.py.
1  Φ og W for (a) og (b) ved 350 lx på 0,6 × 0,4 (to plasseringar) over alle ψ, og ved 500 lx på TASK (attgjeving).
2  Synlegheit av opninga i arbeidsstillinga for augehøgd 0,20–0,65 (felles.visible med EYES bytt).
3  Finst det ein ψ som er skjerma frå 25–60 cm og held U0 >= 0,4? Kva kostar han?
4  Massen til (c) frå tal_mek, og med tynnaste fot (3 mm).
Køyr: PYTHONIOENCODING=utf-8 python stadfest_PR6_1.py   (under 1 min)
"""
import os, sys, math, json, importlib.util
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form01')); sys.path.insert(0, os.path.join(ROOT, 'form02'))
import felles as fe
import motor as M1
import val as V2
spec = importlib.util.spec_from_file_location('motor4', os.path.join(ROOT, 'form04', 'motor.py'))
M4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(M4)

OUT = {}
EYES0 = fe.EYES.copy()


def grid(y0, y1):
    tx, ty = np.meshgrid(np.linspace(-0.30, 0.30, 7), np.linspace(y0, y1, 6))
    return np.c_[tx.ravel(), ty.ravel(), np.zeros(tx.size)]


TASKS = {'0,6x0,35 (felles)': fe.TASK, '0,6x0,4 y0,05-0,45': grid(0.05, 0.45), '0,6x0,4 y0,00-0,40': grid(0.00, 0.40)}


def eyes_at(z):
    E = EYES0.copy(); E[:, 2] = z
    return E


def vis_at(P, N, z):
    fe.EYES = eyes_at(z)
    try:
        return fe.visible(P, N)
    finally:
        fe.EYES = EYES0


def skjerma_frå_alle(P, N, zs=np.arange(0.25, 0.6001, 0.01)):
    return not any(vis_at(P, N, z) for z in zs)


def konsept(key, B, opning, eta):
    rows = []
    for s in M1.PSIS:
        P, N, dA = opning(B, s)
        A = dA.sum(); k = eta / (math.pi * A)
        r = dict(psi=round(math.degrees(s)), vis45=fe.visible(P, N), refl=fe.reflected(P, N))
        for nm, T in TASKS.items():
            Et = fe.illum(P, N, dA, T, np.array([0, 0, 1.0])) * k
            Em = Et.mean()
            r[nm] = dict(U0=float(Et.min() / max(Em, 1e-12)), Phi500=float(500 / max(Em, 1e-12)), Phi350=float(350 / max(Em, 1e-12)))
        r['Lap500'] = float(k * r['0,6x0,35 (felles)']['Phi500'])
        r['skjerma_25_60'] = skjerma_frå_alle(P, N)
        rows.append(r)
    S = fe.sok(B, M1.PSIS, opning, eta)
    psi_w = round(math.degrees(S['work']['s']))
    w = [r for r in rows if r['psi'] == psi_w][0]
    P, N, dA = opning(B, S['work']['s'])
    zs = np.round(np.arange(0.20, 0.6501, 0.001), 3)
    v = [vis_at(P, N, z) for z in zs]
    z_vis = [float(z) for z, q in zip(zs, v) if q]
    res = dict(psi_arb=psi_w, Phi_arb_felles=float(S['work']['Phi']), W_arb_felles=float(S['work']['Phi'] / fe.LM_W),
               arb_ved_350=dict((nm, dict(Phi=w[nm]['Phi350'], W=w[nm]['Phi350'] / fe.LM_W, U0=w[nm]['U0'])) for nm in TASKS),
               synleg_auge_z=(min(z_vis), max(z_vis)) if z_vis else None, Lap_arb_500=w['Lap500'])
    # minste Φ ved 350 lx over alle ψ (U0 >= 0,4), utan og med skjerming frå 25–60 cm
    for nm in TASKS:
        ok = [r for r in rows if r[nm]['U0'] >= fe.U0_MIN]
        ok_sk = [r for r in ok if r['skjerma_25_60'] and not r['refl']]
        best = min(ok, key=lambda r: r[nm]['Phi350']) if ok else None
        best_sk = min(ok_sk, key=lambda r: r[nm]['Phi350']) if ok_sk else None
        res[f'min350_{nm}'] = dict(psi=best['psi'], W=best[nm]['Phi350'] / fe.LM_W, U0=best[nm]['U0'], skjerma=best['skjerma_25_60']) if best else None
        res[f'min350_skjerma25_60_{nm}'] = (dict(psi=best_sk['psi'], W=best_sk[nm]['Phi350'] / fe.LM_W, U0=best_sk[nm]['U0'])
                                            if best_sk else None)
    res['psi_skjerma_25_60'] = [r['psi'] for r in rows if r['skjerma_25_60']]
    OUT[key] = res
    return res


Ba = dict(M1.FINAL, yp=0.18, hp=0.62, a=0.20)
konsept('a', Ba, M1.opning, M1.eta(Ba))
Bb = dict(V2.B_KROK)
konsept('b', Bb, V2.opning_krok, V2.eta_krok(Bb))

# (c) masse
Bc = dict(M4.FINAL)
mk = M4.tal_mek(Bc)
m_tot = mk['st_a']['masse_kg']
t_f = mk['t_fot']
m_fot = M4.RHO_ALU * M4.FOT_XY[0] * M4.FOT_XY[1] * t_f + 0.15
m_utan_fot = m_tot - m_fot
m3 = m_utan_fot + M4.RHO_ALU * M4.FOT_XY[0] * M4.FOT_XY[1] * 0.003 + 0.15
OUT['c'] = dict(masse_kg=m_tot, t_fot_mm=t_f * 1000, m_fot=m_fot, m_utan_fot=m_utan_fot, masse_fot3mm=m3,
                m_plate=mk['m_plate'])
# (a) masse frå konsept.json (1,2457) mot F8 1,2
kj = json.load(open(os.path.join(ROOT, 'konsept.json'), encoding='utf-8'))
OUT['konsept_json'] = {k: dict(P_W=kj[k]['P_W'], masse_kg=kj[k]['masse_kg']) for k in 'abc'}

for k in ('a', 'b'):
    r = OUT[k]
    print(k, 'psi_arb', r['psi_arb'], 'W felles', round(r['W_arb_felles'], 2), 'synleg z', r['synleg_auge_z'], 'Lap', round(r['Lap_arb_500']))
    for nm, q in r['arb_ved_350'].items():
        print('   arb 350', nm, {a: round(b, 2) for a, b in q.items()})
    for nm in TASKS:
        print('   min350', nm, r[f'min350_{nm}'], '| skjerma', r[f'min350_skjerma25_60_{nm}'])
    print('   psi skjerma 25-60:', r['psi_skjerma_25_60'])
print('c', {a: round(b, 3) for a, b in OUT['c'].items()})
print(OUT['konsept_json'])
