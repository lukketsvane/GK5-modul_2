# -*- coding: utf-8 -*-
"""Motbevis PR3 (c prisme): når plata armen før stemningsstillinga −105°, og kva gjev nåelege vinklar?
1) armboksen lesen ut av geometri() sjølv (ikkje skriven av), 2) plata sveipt i 0,5°-steg om LED-aksen og om tyngdepunktet,
3) stemning med motoren sin eigen lysmodell (I_mot, same optikk) på 8x6 og fint veggfelt, med kjelda flytt når aksen er tyngdepunktet.
Køyr: PYTHONIOENCODING=utf-8 python stadfest_PR3_1.py
"""
import os, sys, math, json
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HER)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form04'))
import felles as fe
import motor as M

B = dict(M.FINAL)
ut = {}
S = M.sok(B)
W, Mo = S['work'], S['mood']
PhiW = W['Phi']
ut['motor'] = dict(alfa_arb=math.degrees(W['s']), alfa_stem=math.degrees(Mo['s']), Ev_stem=Mo['Ev_stem'], R=Mo['R_stem'], Phi=PhiW,
                   kollisjon_flagg_m105=bool(M.kollisjon(B, math.radians(-105), False)))

# 1) armen frå geometri(): alle hjørne over LED-aksen og bak han, utanom hovudet (hovudet vert rotert, armen ikkje)
V0, F0, em0 = M.geometri(B, 0.0)
V1, F1, em1 = M.geometri(B, math.radians(-40))
fast = np.all(np.isclose(V0, V1), axis=1)                      # punkt som ikkje flyttar seg med vippa = bering
Vf = V0[fast & (V0[:, 2] > B['zs'] - 0.02) & (V0[:, 1] < M.COL_Y)]
ut['bering_boks'] = dict(x=[float(Vf[:, 0].min()), float(Vf[:, 0].max())], y=[float(Vf[:, 1].min()), float(Vf[:, 1].max())],
                         z=[float(Vf[:, 2].min()), float(Vf[:, 2].max())])
za = B['zs'] + 0.03
ARM = (B['ys'] - 0.012, M.COL_Y + M.COL_F, za, za + M.COL_F)            # flensar + topp, x ±0,05
HENG = (B['ys'] - 0.012, B['ys'] + 0.012, B['zs'] - 0.012, za + M.COL_F)  # hengjeplatene x ±0,05


def plate(a, pn):
    ned = np.array([-math.sin(a), -math.cos(a)]); fram = np.array([-math.cos(a), math.sin(a)])
    piv = np.array([B['ys'], B['zs'] - pn])
    s = np.linspace(-B['bp'] / 2, B['bp'] / 2, 161)
    return np.vstack([piv + s[:, None] * fram + (w - pn) * ned for w in (B['d'], B['d'] + B['tp'])])


def inni(p, b):
    return (p[:, 0] > b[0]) & (p[:, 0] < b[1]) & (p[:, 1] > b[2]) & (p[:, 1] < b[3])


pn_cg = M.akse_under_led(B)
kol = {}
for nm, pn in (('LED', 0.0), ('tyngdepunkt', pn_cg)):
    forste = None
    for ad in np.arange(0, -130.01, -0.5):
        p = plate(math.radians(ad), pn)
        if inni(p, ARM).any() or inni(p, HENG).any():
            forste = float(ad); break
    p = plate(math.radians(-105), pn)
    kol[nm] = dict(pivot_mm=round(pn * 1000, 1), forste_treff=forste, m105_i_arm=bool(inni(p, ARM).any()),
                   m105_plate_z=[round(float(p[:, 1].min()), 3), round(float(p[:, 1].max()), 3)],
                   m105_y_ved_armhogd=[round(float(v), 3) for v in p[(p[:, 1] > za) & (p[:, 1] < za + M.COL_F), 0][[0, -1]]] if inni(p, ARM).any() else None)
ut['kollisjon'] = kol

# 3) stemning: same I_mot, kjelda flytt for tyngdepunktsaksen
Wx, Wz = np.meshgrid(np.linspace(-0.69, 0.69, 35), np.linspace(0.06, 1.19, 29))
WF = np.c_[Wx.ravel(), np.full(Wx.size, fe.WALL_Y - 1e-3), Wz.ravel()]
_src0 = M._src


def stem(ad, pn):
    a = math.radians(ad)
    off = np.array([0.0, pn * math.sin(a), -pn + pn * math.cos(a)])   # LED = piv − pn·ned
    M._src = lambda B_, nx=24: _src0(B_, nx) + off
    try:
        Ew = M.E_punkt(B, a, fe.WALLG, np.array([0, -1.0, 0])).mean()
        Ed = M.E_punkt(B, a, fe.DESKG, np.array([0, 0, 1.0])).mean()
        Ewf = M.E_punkt(B, a, WF, np.array([0, -1.0, 0])).mean()
    finally:
        M._src = _src0
    k = PhiW * fe.DIM_STEM
    return dict(Ev_8x6=round(float(Ew * k), 1), Ev_fin=round(float(Ewf * k), 1), R=round(float(Ew / (Ew + Ed)), 3))


ut['stemning_LED'] = {int(ad): stem(ad, 0.0) for ad in (-105, -60, -55, -50, -45, -40)}
ut['stemning_tyngdepunkt'] = {int(ad): stem(ad, pn_cg) for ad in (-105, -65, -62, -60, -55, -50)}
# beste nåelege (same reglar som sok: R >= 0,5 først, så Ev) på 8x6
for nm, pn in (('LED', 0.0), ('tyngdepunkt', pn_cg)):
    gr = kol[nm]['forste_treff']
    cand = [(ad, stem(ad, pn)) for ad in range(-5, int(math.ceil(gr)) - 1 + 1, -5) if ad > gr] + [(int(math.ceil(gr)) + 1, stem(math.ceil(gr) + 1, pn))]
    best = max(cand, key=lambda c: (c[1]['R'] >= fe.R_STEM_MIN, c[1]['Ev_8x6']))
    ut[f'beste_naaeleg_{nm}'] = dict(alfa=best[0], **best[1])
print(json.dumps(ut, indent=1, ensure_ascii=False))

# 4) kor mykje må armen opp for at sveipet 0 .. −105° går fritt (høgaste platepunkt i sveipet mot armunderkant za)
loft = {}
for nm, pn in (('LED', 0.0), ('tyngdepunkt', pn_cg)):
    zt = max(float(plate(math.radians(ad), pn)[:, 1].max()) for ad in np.arange(0, -105.01, -0.5))
    loft[nm] = dict(plate_zmax=round(zt, 3), armunderkant=za, loft_cm=round(100 * (zt - za), 1))
print(json.dumps(dict(loft=loft), ensure_ascii=False))
