# -*- coding: utf-8 -*-
"""Motprov nr. 2 av P3 (toppluminans i ansiktslyset til (c) prisme).

Deterministisk, ingen Monte Carlo (so ingen maks-over-støy-skeivskap):
- rillevinkel τ(s) frå form04/motor.py optikk(FINAL), fasett på botnen (s_botn = d tanφ + tp tanφ_i), flat overside.
- ideelle fasettar (ingen stigevegg): øvre grense for kvar fasett, ikkje snitt over riller.
- bakoversporing frå auget til punkt P på botnen, rotert g i profilplanet (motorens mattering: gauss σ på θ ut),
  Snell + Fresnel (upolarisert) på vektorform i 3D, renneopning |s| < 8 mm ved z 5 mm, LED-stripe |u| <= w/2.
- g på fast gitter 0,1° (±32°): treffbrøken for kvar (w, σ) er ei vekta sum, same strålar for alle variantar.
- L_LED = 1/(π w L) per LED-lumen (jamn lambertsk stripe). Φ150 frå motoren (79,30 lm) og sjølvkonsistent
  (E_v ved midtauga = Σ L cos_andlet cos_plate dA / r²).
Køyr: PYTHONIOENCODING=utf-8 python stadfest_P3_2.py   (om lag 1 min)
"""
import os, sys, math, json, time
import numpy as np

ROOT = r'C:\Users\Iver\Documents\northern-lampe'
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form04'))
import felles as fe
import motor as mo

t0 = time.time()
B = mo.FINAL
O = mo.optikk(B)
n = mo.N_PMMA
d, tp, bp, L, ys, zs = B['d'], B['tp'], B['bp'], B['L'], B['ys'], B['zs']
ZB = d + tp
CW, ZC = 0.008, 0.005
A_F = math.radians(70.0)          # tal.csv alfa_ansikt
PHI150_MOTOR = 79.3008            # tal.csv Phi_ansikt
L150_MOTOR = 658.626              # tal.csv L_ansikt (snitt)

phi_i = np.arcsin(np.sin(O['ph']) / n)
S_BOT = d * np.tan(O['ph']) + tp * np.tan(phi_i)
TAU = O['tau']

fram = np.array([0, -math.cos(A_F), math.sin(A_F)]); ned = np.array([0, -math.sin(A_F), -math.cos(A_F)])
Oax = np.array([0, ys, zs])


def lok(e):
    v = e - Oax
    return np.array([e[0], v @ fram, v @ ned])


def refr(k, N, n1, n2):
    c1 = -(k * N).sum(-1)
    r = n1 / n2
    kk = 1 - r * r * (1 - c1 * c1)
    ok = kk > 0
    ct = np.sqrt(np.clip(kk, 0, None))
    t = r * k + (r * c1 - ct)[..., None] * N
    rs = ((n1 * c1 - n2 * ct) / (n1 * c1 + n2 * ct)) ** 2
    rp = ((n1 * ct - n2 * c1) / (n1 * ct + n2 * c1)) ** 2
    return t, np.where(ok, 1 - 0.5 * (rs + rp), 0.0), ok


DS = 1e-4
SG = np.arange(-bp / 2 + DS / 2, bp / 2, DS)               # 0,1 mm
XG = np.arange(-0.29, 0.2901, 0.02)                        # 2 cm
GD = np.arange(-32.0, 32.001, 0.1)                         # mattering, grader
G = np.radians(GD)
WS = [0.005, 0.008, 0.010, 0.012, 0.016]
SIGS = [0.0, 4.0, 5.0, 6.0, 8.0]
GW = []
for sg in SIGS:
    if sg == 0:
        v = (np.abs(GD) < 0.05).astype(float)
    else:
        v = np.exp(-0.5 * (GD / sg) ** 2)
    GW.append(v / v.sum())
GW = np.array(GW).T                                        # (ng, nsig)

tau_s = np.interp(SG, S_BOT, TAU)
Nf = np.c_[np.zeros_like(tau_s), np.sin(tau_s), np.cos(tau_s)]
cg, sg_ = np.cos(G)[None, :], np.sin(G)[None, :]

# M[eye][w][sig] : (nx, ns) luminans per LED-lm i delar av L_LED (dvs. T·treffbrøk)
M = np.zeros((len(fe.EYES), len(WS), len(SIGS), len(XG), len(SG)))
EV = np.zeros((len(WS), len(SIGS)))                         # E_v ved midtauga per LED-lm
for ie, e in enumerate(fe.EYES):
    el = lok(e)
    for ix, x in enumerate(XG):
        P = np.c_[np.full_like(SG, x), SG, np.full_like(SG, ZB)]
        b = P - el; r = np.linalg.norm(b, axis=1); b /= r[:, None]
        bb = np.stack([np.broadcast_to(b[:, 0:1], (len(SG), len(G))), b[:, 1:2] * cg + b[:, 2:3] * sg_, -b[:, 1:2] * sg_ + b[:, 2:3] * cg], -1)
        t1, T1, ok1 = refr(bb, Nf[:, None, :], 1.0, n)
        lam = (d - ZB) / t1[..., 2]
        p1 = P[:, None, :] + lam[..., None] * t1
        ok = ok1 & (lam > 0) & (np.abs(p1[..., 1]) <= bp / 2)
        t2, T2, ok2 = refr(t1, np.array([0, 0, 1.0]), n, 1.0)
        ok &= ok2 & (t2[..., 2] < 0)
        lc = (ZC - d) / t2[..., 2]; sc = p1[..., 1] + lc * t2[..., 1]
        ok &= np.abs(sc) < CW
        l0 = (0 - d) / t2[..., 2]; u = p1[..., 1] + l0 * t2[..., 1]; xu = p1[..., 0] + l0 * t2[..., 0]
        ok &= np.abs(xu) <= L / 2
        TT = np.where(ok, T1 * T2, 0.0)
        for iw, w in enumerate(WS):
            Hm = np.where(np.abs(u) <= w / 2, TT, 0.0)
            M[ie, iw, :, ix, :] = (Hm @ GW).T
        if ie == 0:
            ce = np.clip(-b[:, 1] * math.cos(A_F) - b[:, 2] * math.sin(A_F), 0, None)
            dOm = ce * np.abs(b[:, 2]) / r ** 2 * DS * (XG[1] - XG[0])
            for iw, w in enumerate(WS):
                EV[iw] += (M[0, iw, :, ix, :] * dOm[None, :]).sum(1) / (math.pi * w * L)
print(f'sporing ferdig {time.time() - t0:.0f} s')


def glid(a, k):
    return np.apply_along_axis(lambda v: np.convolve(v, np.ones(k) / k, mode='valid'), -1, a)


UT = dict(motor=dict(alfa_ansikt=70.0, Phi150=PHI150_MOTOR, L_snitt=L150_MOTOR), tilfelle={})
print('w mm  σ°   T·treff topp  Φ150 eigen | topp 1 mm / 1 cm / 2 cm [cd/m²] Φmotor | Φeigen | snitt plata (Φmotor)')
for iw, w in enumerate(WS):
    for isg, sg in enumerate(SIGS):
        A = M[:, iw, isg]                                   # (3, nx, ns)
        f1, f10, f20 = glid(A, 10).max(), glid(A, 100).max(), glid(A, 200).max()
        LL = 1 / (math.pi * w * L)
        Phi_e = 150 / EV[iw, isg]
        snitt = A.mean(axis=(1, 2)).max() * LL
        rec = dict(w_mm=w * 1000, sigma=sg, frac_topp_0_1mm=float(A.max()), frac_topp_1mm=float(f1), frac_topp_1cm=float(f10),
                   Phi150_eigen=float(Phi_e), L_LED_motor=LL * PHI150_MOTOR,
                   topp_1mm_motor=float(f1 * LL * PHI150_MOTOR), topp_1cm_motor=float(f10 * LL * PHI150_MOTOR), topp_2cm_motor=float(f20 * LL * PHI150_MOTOR),
                   topp_1mm_eigen=float(f1 * LL * Phi_e), topp_1cm_eigen=float(f10 * LL * Phi_e),
                   snitt_motor=float(snitt * PHI150_MOTOR), snitt_eigen=float(snitt * Phi_e))
        UT['tilfelle'][f'w{int(w*1000)}_s{int(sg)}'] = rec
        print(f'{w*1000:4.0f} {sg:4.0f}   {A.max():.3f}  {Phi_e:6.1f}  | {rec["topp_1mm_motor"]:6.0f} {rec["topp_1cm_motor"]:6.0f} {rec["topp_2cm_motor"]:6.0f}'
              f' | {rec["topp_1mm_eigen"]:6.0f} {rec["topp_1cm_eigen"]:6.0f} | {rec["snitt_motor"]:5.0f}')

# kvar ligg toppen (midtauga, x nær 0)
ix0 = int(np.argmin(np.abs(XG)))
for key, (iw, isg) in (('w5_s4', (0, 1)), ('w10_s4', (2, 1))):
    prof = M[0, iw, isg, ix0]
    j = int(np.argmax(glid(prof, 10)))
    lit = prof > 0.05 * prof.max()
    UT['tilfelle'][key].update(s_topp_cm=float(SG[j + 5] * 100), breidd_5pst_cm=float(lit.sum() * DS * 100),
                               breidd_halv_cm=float((prof > 0.5 * prof.max()).sum() * DS * 100))
    print(key, 's_topp', round(SG[j + 5] * 100, 2), 'cm, breidd >5 %', round(lit.sum() * DS * 100, 2), 'cm, >50 %',
          round((prof > 0.5 * prof.max()).sum() * DS * 100, 2), 'cm')

# kva w gjev topp 1 cm = 3000 ved σ 4 (Φ motor)
ws = np.array(WS) * 1000
t1c = np.array([UT['tilfelle'][f'w{int(w)}_s4']['topp_1cm_motor'] for w in ws])
t1m = np.array([UT['tilfelle'][f'w{int(w)}_s4']['topp_1mm_motor'] for w in ws])
UT['w_grense_s4'] = dict(topp_1cm=float(np.interp(-3000, -t1c, ws)), topp_1mm=float(np.interp(-3000, -t1m, ws)))
print('w der toppen er 3000 cd/m² ved σ 4°: 1 cm', round(UT['w_grense_s4']['topp_1cm'], 1), 'mm, 1 mm', round(UT['w_grense_s4']['topp_1mm'], 1), 'mm')
for w in (5, 10):
    sgs = np.array(SIGS[1:]); tt = np.array([UT['tilfelle'][f'w{w}_s{int(s)}']['topp_1mm_motor'] for s in sgs])
    UT[f'sigma_grense_w{w}_1mm'] = float(np.interp(-3000, -tt, sgs))
    print(f'σ der toppen 1 mm er 3000 for w {w} mm:', round(UT[f'sigma_grense_w{w}_1mm'], 2), '°')
UT['tid_s'] = time.time() - t0
print(f'{time.time() - t0:.0f} s')
