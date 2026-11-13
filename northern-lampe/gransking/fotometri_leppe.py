# -*- coding: utf-8 -*-
"""Gransking 3b · kva leppene (retting R-a2 i fotometri.md) gjer med stemninga i (a) og (b). Eigen kode, lambertsk kordeflate
(same modell som felles.py, men eigen kvadratur og eigen leppeskugge). Leppene er stive delar av røyret: loddrette i arbeid,
rotert med røyret i stemning.
Køyr: PYTHONIOENCODING=utf-8 python fotometri_leppe.py  -> fotometri_leppe.json
"""
import json, math, os, time
import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
T0 = time.time()
SX0, SX1, SY, SZ0, SZ1 = -0.275, 0.275, 0.45, 0.10, 0.42
WY = 0.75
R, BETA, RHO_V = 0.022, math.radians(25.0), 0.75
HV, RC = R * math.sin(BETA), R * math.cos(BETA)
X1 = np.array([1.0, 0, 0])
AUGE = [(0, -0.30, 0.45), (-0.15, -0.30, 0.45), (0.15, -0.30, 0.45), (0, -0.15, 0.45), (0, -0.30, 0.40), (0, -0.30, 0.50),
        (0, -0.15, 0.40), (0, -0.15, 0.50), (0, -0.60, 1.60), (0, 0.0, 1.60)]         # + ståande bak stolen og ved bordkanten
KONF = {'a': dict(yp=0.18, hp=0.62, opn=[(-0.315, 0.315)], eta=0.674110),
        'b': dict(yp=0.25, hp=0.62, opn=[(-0.30, -0.02), (0.02, 0.30)], eta=0.666918)}


def e_(p):
    p = math.radians(p); return np.array([0.0, -math.sin(p), -math.cos(p)])


def v_(p):
    p = math.radians(p); return np.array([0.0, math.cos(p), -math.sin(p)])


def kjelde(yp, hp, psi, opn, du=0.01, nv=40):
    e, v = e_(psi), v_(psi)
    c0 = np.array([0.0, yp, hp]) + RC * e
    sv = ((np.arange(nv) + .5) / nv * 2 - 1) * HV
    P, dA = [], []
    for a0, a1 in opn:
        nu = max(1, round((a1 - a0) / du))
        su = a0 + (np.arange(nu) + .5) / nu * (a1 - a0)
        U, V = np.meshgrid(su, sv, indexing='ij')
        P.append(c0 + U.ravel()[:, None] * X1 + V.ravel()[:, None] * v); dA.append(np.full(U.size, (a1 - a0) / nu * 2 * HV / nv))
    return np.vstack(P), np.concatenate(dA), e


def lepper(yp, hp, psi, psi_arb, hb, hv, opn):
    xh = max(abs(a) for o in opn for a in o) + 0.01
    ea, va = e_(psi_arb), v_(psi_arb)
    e, v = e_(psi), v_(psi)
    dl = -ea[2] * e - va[2] * v
    O = np.array([0.0, yp, hp])
    return [(O + RC * e + sg * HV * v, dl, h, xh) for sg, h in ((-1, hb), (1, hv)) if h > 0]


def E_kv(P, e, dA, Q, nq, lp, bit=120):
    out = np.zeros(len(Q))
    for i in range(0, len(Q), bit):
        q = Q[i:i + bit]
        d = q[None] - P[:, None]
        r2 = (d * d).sum(-1); r = np.sqrt(r2)
        ce = (d @ e) / r
        cr = -(d @ nq) / r
        w = np.where((ce > 0) & (cr > 0), ce * cr / r2, 0.0)
        # skjermen som hinder (plan y = SY)
        with np.errstate(divide='ignore', invalid='ignore'):
            s = (SY - P[:, None, 1]) / d[..., 1]
        Xs, Zs = P[:, None, 0] + s * d[..., 0], P[:, None, 2] + s * d[..., 2]
        w[(s > 1e-6) & (s < 1 - 1e-6) & (Xs > SX0) & (Xs < SX1) & (Zs > SZ0) & (Zs < SZ1)] = 0.0
        for E0, dl, h, xh in lp:
            m = np.cross(X1, dl)
            a = (P - E0) @ m; b = (q - E0) @ m
            kr = a[:, None] * b[None, :] < 0
            with np.errstate(divide='ignore', invalid='ignore'):
                t = np.where(kr, a[:, None] / (a[:, None] - b[None, :]), 0.0)
            X = P[:, None, :] + t[..., None] * d
            al = (X - E0) @ dl
            w[kr & (al > 0) & (al < h) & (np.abs(X[..., 0]) < xh)] = 0.0
        out[i:i + bit] = (w * dA[:, None]).sum(0)
    return out


def synleg(P, e, lp):
    n = 0
    for E in AUGE:
        E = np.asarray(E, float)
        fr = (E - P) @ e > 0
        if not fr.any():
            continue
        Pf = P[fr]; bl = np.zeros(len(Pf), bool)
        for E0, dl, h, xh in lp:
            m = np.cross(X1, dl)
            a = (Pf - E0) @ m; b = (E - E0) @ m
            with np.errstate(divide='ignore', invalid='ignore'):
                t = a / (a - b)
            X = Pf + t[:, None] * (E - Pf); al = (X - E0) @ dl
            bl |= (a * b < 0) & (al > 0) & (al < h) & (np.abs(X[:, 0]) < xh)
        n += int((~bl).any())
    return n


def celle(x0, x1, nx, a0, a1, na):
    X, Y = np.meshgrid(x0 + (np.arange(nx) + .5) / nx * (x1 - x0), a0 + (np.arange(na) + .5) / na * (a1 - a0))
    return X.ravel(), Y.ravel()


wx, wz = celle(-0.70, 0.70, 35, 0.05, 1.20, 29)          # 4 cm
VEGG = np.c_[wx, np.full(wx.size, WY - 1e-3), wz]
dx, dy = celle(-0.70, 0.70, 28, 0.0, 0.75, 15)            # 5 cm
BORD = np.c_[dx, dy, np.zeros(dx.size)]
sx, sz = celle(SX0, SX1, 22, SZ0, SZ1, 13)
SKJ = np.c_[sx, np.full(sx.size, SY - 1e-4), sz]
E_MAAL = 10.0 * math.pi / RHO_V                           # 10 cd/m² snitt på veggfeltet
UT = {}
for k, design in (('a', [(-20, 0, 0), (-20, 0.010, 0.030), (-20, 0.005, 0.020)]), ('b', [(-20, 0, 0), (-20, 0.010, 0.030), (-20, 0.005, 0.020)])):
    c = KONF[k]
    UT[k] = []
    for psi_arb, hb, hv in design:
        best = None
        for psi in range(-125, -64, 5):
            P, dA, e = kjelde(c['yp'], c['hp'], psi, c['opn'])
            lp = lepper(c['yp'], c['hp'], psi, psi_arb, hb, hv, c['opn'])
            A = dA.sum(); kL = c['eta'] / (math.pi * A)             # cd/m² per LED-lm
            Ew = E_kv(P, e, dA, VEGG, np.array([0, -1.0, 0]), lp) * kL
            Ed = E_kv(P, e, dA, BORD, np.array([0, 0, 1.0]), lp) * kL
            Es = E_kv(P, e, dA, SKJ, np.array([0, -1.0, 0]), lp) * kL
            r = dict(psi_arb=psi_arb, h_brukar_mm=hb * 1e3, h_vegg_mm=hv * 1e3, psi_stem=psi, Ev_per_lm=Ew.mean(), R=Ew.mean() / (Ew.mean() + Ed.mean()),
                     maks_snitt=Ew.max() / Ew.mean(), Es_per_lm=Es.mean(), synleg_for=synleg(P, e, lp))
            r['lm_for_10cd'] = E_MAAL / r['Ev_per_lm']; r['W_for_10cd'] = r['lm_for_10cd'] / 100
            r['E_skjerm_ved_10cd'] = r['Es_per_lm'] * r['lm_for_10cd']
            if r['R'] >= 0.5 and r['synleg_for'] == 0 and (best is None or r['Ev_per_lm'] > best['Ev_per_lm']):
                best = r
            if psi == -95:
                r95 = r
        UT[k].append(dict(beste=best, psi95=r95))
        for lab, r in (('ψ −95', r95), ('beste ψ', best)):
            print(f"({k}) arbeid ψ {psi_arb:+d}, leppe {hb*1e3:.0f}/{hv*1e3:.0f} mm, {lab} ({r['psi_stem']}): Ē_vegg {r['Ev_per_lm']:.4f} lx/LED-lm  R {r['R']:.3f}  maks/snitt {r['maks_snitt']:.2f}"
                  f"  10 cd/m²: {r['lm_for_10cd']:.0f} lm = {r['W_for_10cd']:.2f} W, skjerm {r['E_skjerm_ved_10cd']:.0f} lx   synleg for {r['synleg_for']} auge", flush=True)
json.dump(UT, open(os.path.join(HER, 'fotometri_leppe.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False, default=float)
print(f'skrive fotometri_leppe.json ({time.time()-T0:.0f} s)')
