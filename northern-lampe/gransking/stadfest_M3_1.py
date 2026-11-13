# -*- coding: utf-8 -*-
"""stadfest_M3_1.py · motbevisar 1 for M3: (a) bru veltar av fingerdytt på grepet?
Brukar motoren sin eigen geometri (M1.geometri, M1.bow) og val.py-plasseringa (yp 0,18, hp 0,62, a 0,15),
utan sok(): røyret er rett (g 0), så massar og føter er uavhengige av psi."""
import os, sys, math
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form01'))
import felles as fe
import motor as M1
g = fe.G
B = dict(M1.FINAL, yp=0.18, hp=0.62, a=0.15)
_, C, *_ = M1.bow(B, 0.0, 61)
V, F, emit, legs = M1.geometri(B, 0.0)
Larc = M1.arc_len(B)
m_bow = M1.RHO_ALU * math.pi * 2 * B['R'] * B['t_bow'] * Larc * (1 - B['k'] * B['beta'] / 180)
Aleg = math.pi / 4 * (B['D_leg'] ** 2 - (B['D_leg'] - 2 * B['t_leg']) ** 2)
parts = [(m_bow, C.mean(0)), (0.10, C[len(C) // 2]), (0.06, np.array([B['L'] / 2 + 0.04, B['yp'], B['hp']])),
         (0.03, np.array([-B['L'] / 2, B['yp'], B['hp']]))]
for ap, ft in legs:
    parts.append((M1.RHO_ALU * Aleg * np.linalg.norm(ap - ft), (ap + ft) / 2))
m = sum(p for p, _ in parts); com = sum(p * c for p, c in parts) / m
feet = np.array([[f[0], f[1]] for _, f in legs])
yf, yb = feet[:, 1].min(), feet[:, 1].max()
d = com[1] - yf
Mr = m * g * d
print(f'masse {m:.4f} kg, tp y {com[1]:.3f} z {com[2]:.3f}, føter y {yf:.3f}-{yb:.3f}, x ±{feet[:,0].max():.3f}; M_rett {Mr:.3f} N·m')
st = fe.stabilitet(parts, [feet], B['hp'], M1.T_DET / 0.026)
print(f'fe.stabilitet: F_tipp {st["F_tipp_N"]:.3f} N i z {B["hp"]}, tipp {st["tipp_deg"]:.2f}°, grep_ratio {st["F_tipp_N"]*B["hp"]/M1.T_DET:.1f}')
r = 0.026; zt = B['hp'] + r
Ff = M1.T_DET / r
print(f'finger øvst (z {zt:.3f}): lyftar ved {Mr/zt:.3f} N, fingerkraft {Ff:.3f} N -> λ {Mr/zt/Ff:.3f}; 10 N -> λ {Mr/zt/10:.3f}')
# ubalanse om røyraksen 0,025 N·m (mekanikk_kontroll): vri med/mot tyngda
for T in (M1.T_DET - 0.025, M1.T_DET, M1.T_DET + 0.025):
    print(f'   vri krev {T:.3f} N·m: finger {T/r:.2f} N, λ {Mr/zt/(T/r):.2f}')
# null-masse-rettingar
for T, rr in ((0.08, 0.032), (0.05, 0.026), (0.04, 0.026), (0.04, 0.032), (0.05, 0.035)):
    z = B['hp'] + rr
    print(f'   T {T:.2f}, grep r {rr*1e3:.0f} mm: finger {T/rr:.2f} N, λ {Mr/z/(T/rr):.2f}')
# tunge r 40 mm framme på grepet, fingeren trykkjer ned / opp (vertikal kraft i y = yp - 0,04)
for rl in (0.026, 0.040):
    Ft = M1.T_DET / rl; yP = B['yp'] - rl
    # ned: aukar rettande moment om framkant om yP > yf; opp: minkar om bakkant/framkant
    lam_opp = min(m * g * (com[1] - yf) / (Ft * (yP - yf)) if yP > yf else math.inf,
                  m * g * (yb - com[1]) / (Ft * (yb - yP)))
    print(f'   tunge r {rl*1e3:.0f}: {Ft:.2f} N, ned stabiliserer, opp λ {lam_opp:.2f}')
# glid mot tipp
print(f'glid før tipp om μ < {Mr/zt/(m*g):.3f}')
zc = com[2]
print(f'energi til velt {m*g*(math.hypot(d, zc)-zc):.3f} J, tippvinkel {math.degrees(math.atan2(d, zc)):.1f}°')
