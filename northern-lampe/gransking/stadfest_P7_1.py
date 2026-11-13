# -*- coding: utf-8 -*-
"""Motbevis P7 (prisme): stemningstal på 8x6-gitteret og kollisjon med armen.
Del A: motoren sjølv (form04/motor.py FINAL): rader, kollisjon mot armboksen frå geometri(), to akseval.
Del B: eigen, enkel 3D-sporar (ideelle fasettar frå designlova, ingen stigeveggar), 2D- og 3D-modus,
       gitter 8x6 (celler +-2,5 cm) mot arealsnitt, same Phi frå same sporing (eta kansellerer).
Køyr: PYTHONIOENCODING=utf-8 python stadfest_P7_1.py  (om lag 1 min)
"""
import os, sys, math, json
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HER)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form04'))
import felles as fe
import motor as M

B = dict(M.FINAL)
ut = {}
# ---------------- Del A ----------------
S = M.sok(B)
rows = S['rows']
deg = lambda r: round(math.degrees(r['s']))
ut['motor_mood'] = dict(alfa=deg(S['mood']), Ev=S['mood']['Ev_stem'], R=S['mood']['R_stem'], Phi=S['work']['Phi'])
# fint veggfelt, same lysmodell
Wx, Wz = np.meshgrid(np.linspace(-0.69, 0.69, 35), np.linspace(0.06, 1.19, 29))
WF = np.c_[Wx.ravel(), np.full(Wx.size, fe.WALL_Y - 1e-3), Wz.ravel()]
a105 = math.radians(-105)
Ewf = M.E_punkt(B, a105, WF, np.array([0, -1.0, 0])).mean()
ut['motor_areal_Ev'] = float(Ewf * S['work']['Phi'] * fe.DIM_STEM)
# rad-profil i motoren: E på veggen langs z ved x = 0 og x = 0,6
zz = np.linspace(0.40, 1.25, 18)
for xv in (0.0, 0.5, 0.7):
    Q = np.c_[np.full(zz.size, xv), np.full(zz.size, fe.WALL_Y - 1e-3), zz]
    ut[f'motor_profil_x{xv}'] = [round(float(v), 1) for v in M.E_punkt(B, a105, Q, np.array([0, -1.0, 0])) * S['work']['Phi'] * fe.DIM_STEM]

# armboks frå geometri(): flensar x = +-0,05, y ys-0,012 .. COL_Y+COL_F, z za .. za+COL_F
za = B['zs'] + 0.03
ARM = (B['ys'] - 0.012, M.COL_Y + M.COL_F, za, za + M.COL_F)


def plate_pts(a, pivot_ned=0.0, ns=41):
    """Plateomriss (overside d og underside d+tp, +-bp/2) i y-z. pivot_ned: aksen ligg så langt under LED-lina (i hovudramma)."""
    ned = np.array([-math.sin(a), -math.cos(a)]); fram = np.array([-math.cos(a), math.sin(a)])
    piv = np.array([B['ys'], B['zs'] - pivot_ned])       # fast akse i verda (ved alfa 0 ligg han rett under LED)
    pts = []
    for w in (B['d'], B['d'] + B['tp']):
        for v in np.linspace(-B['bp'] / 2, B['bp'] / 2, ns):
            pts.append(piv + v * fram + (w - pivot_ned) * ned)
    return np.array(pts)


def i_arm(p):
    return (p[:, 0] > ARM[0]) & (p[:, 0] < ARM[1]) & (p[:, 1] > ARM[2])


kol = {}
for nm, pn in (('LED-akse', 0.0), ('tyngdepunkt', M.akse_under_led(B))):
    first = None; zmax = {}
    for r in rows:
        a = r['s']; p = plate_pts(a, pn)
        hit = bool(i_arm(p).any())
        zmax[deg(r)] = round(float(p[:, 1].max()), 3)
        if hit and a < 0 and (first is None or a > first):
            first = a
    p55 = plate_pts(math.radians(-55), pn); p105 = plate_pts(math.radians(-105), pn)
    j = np.argmax(p55[:, 1]); k = np.argmax(p105[:, 1])
    kol[nm] = dict(pivot_under_led_mm=round(pn * 1000, 1), forste_kollisjon_bakover=round(math.degrees(first)) if first is not None else None,
                   topp_m55=[round(float(v), 3) for v in p55[j]], topp_m105=[round(float(v), 3) for v in p105[k]],
                   radius_cm=round(100 * math.hypot(B['bp'] / 2, B['d'] + B['tp'] - pn), 1),
                   m105_i_arm=bool(i_arm(p105).any()))
ut['kollisjon'] = kol
ut['motor_kollisjon_flagg_m105'] = bool(M.kollisjon(B, a105, False))
# kva vel motoren om armen er med (LED-akse)? same sok-reglar
ok_rows = [r for r in rows if not r['kolli'] and r['stem_ok'] and not i_arm(plate_pts(r['s'])).any()]
Mo2 = max(ok_rows, key=lambda r: (r['R_stem'] >= fe.R_STEM_MIN, r['Ev_stem']))
ut['mood_med_arm'] = dict(alfa=deg(Mo2), Ev=Mo2['Ev_stem'], R=Mo2['R_stem'])
ut['rader'] = {deg(r): dict(Ev=round(r['Ev_stem'], 1), R=round(r['R_stem'], 3), arm=bool(i_arm(plate_pts(r['s'])).any()))
               for r in rows if -110 <= deg(r) <= -30}

# ---------------- Del B: eigen 3D-sporar ----------------
O = M.optikk(B)
n = M.N_PMMA
ph = O['ph']; tau = O['tau']
phi_i = np.arcsin(np.sin(ph) / n)
s_bot_tab = B['d'] * np.tan(ph) + B['tp'] * np.tan(phi_i)


def snell(I, Nn, n1, n2):
    c = -(I * Nn).sum(1)
    Nn = np.where(c[:, None] < 0, -Nn, Nn); c = np.abs(c)
    r = n1 / n2
    k = 1 - r * r * (1 - c * c)
    ok = k >= 0
    T = r * I + (r * c - np.sqrt(np.clip(k, 0, None)))[:, None] * Nn
    ct = np.sqrt(np.clip(k, 0, None))
    rs = ((n1 * c - n2 * ct) / (n1 * c + n2 * ct)) ** 2; rp = ((n1 * ct - n2 * c) / (n1 * ct + n2 * c)) ** 2
    return T, ok, 1 - 0.5 * (rs + rp)


def spor(N, tre_d, rng):
    """Lambertsk linjekjelde langs x, normal ned (+z i hovudramma: x, s, z_ned). Returnerer startpunkt og retning ut av plata."""
    r1, r2 = rng.random(N), rng.random(N)
    st = np.sqrt(r1); u = np.c_[st * np.cos(2 * np.pi * r2), st * np.sin(2 * np.pi * r2), np.sqrt(1 - r1)]
    x0 = (rng.random(N) - 0.5) * B['L']
    if not tre_d:                       # 2D: same profilvinkel, ingen x-del (som motoren sin snittmodell)
        p = np.arctan2(u[:, 1], u[:, 2])
        u = np.c_[np.zeros(N), np.sin(p), np.cos(p)]
    s_top = B['d'] * u[:, 1] / u[:, 2]; x_top = x0 + B['d'] * u[:, 0] / u[:, 2]
    keep = np.abs(s_top) <= B['bp'] / 2
    t1, ok1, T1 = snell(u, np.tile([0, 0, 1.0], (N, 1)), 1.0, n)
    s_b = s_top + B['tp'] * t1[:, 1] / t1[:, 2]; x_b = x_top + B['tp'] * t1[:, 0] / t1[:, 2]
    keep &= np.abs(s_b) <= B['bp'] / 2
    ta = np.interp(s_b, s_bot_tab, tau)
    Nf = np.c_[np.zeros(N), np.sin(ta), np.cos(ta)]
    t2, ok2, T2 = snell(t1, Nf, n, 1.0)
    keep &= ok1 & ok2 & (np.abs(x_b) <= B['L'] / 2) & (t2[:, 2] > 0)
    w = T1 * T2 * keep
    P = np.c_[x_b, s_b, np.full(N, B['d'] + B['tp'])]
    return P[keep], t2[keep], w[keep]


def til_verda(P, V, a, rng, matt=True):
    if matt:
        g = rng.normal(0, math.radians(M.SIGMA), len(V)); cg, sg = np.cos(g), np.sin(g)
        ds, dz = V[:, 1] * cg + V[:, 2] * sg, -V[:, 1] * sg + V[:, 2] * cg
        V = np.c_[V[:, 0], ds, dz]
    fr = np.array([-math.cos(a), math.sin(a)]); ne = np.array([-math.sin(a), -math.cos(a)])
    Pw = np.c_[P[:, 0], B['ys'] + P[:, 1] * fr[0] + P[:, 2] * ne[0], B['zs'] + P[:, 1] * fr[1] + P[:, 2] * ne[1]]
    Vw = np.c_[V[:, 0], V[:, 1] * fr[0] + V[:, 2] * ne[0], V[:, 1] * fr[1] + V[:, 2] * ne[1]]
    return Pw, Vw


def treff(Pw, Vw):
    with np.errstate(divide='ignore', invalid='ignore'):
        td = np.where(Vw[:, 2] < 0, -Pw[:, 2] / Vw[:, 2], np.inf)
        tw = np.where(Vw[:, 1] > 0, (fe.WALL_Y - Pw[:, 1]) / Vw[:, 1], np.inf)
        ts = np.where(np.abs(Vw[:, 1]) > 1e-12, (fe.SCR['y'] - Pw[:, 1]) / Vw[:, 1], np.inf)
    ts = np.where(ts > 1e-9, ts, np.inf)
    Ps = Pw + np.where(np.isfinite(ts), ts, 0)[:, None] * Vw
    on = (Ps[:, 0] > fe.SCR['x0']) & (Ps[:, 0] < fe.SCR['x1']) & (Ps[:, 2] > fe.SCR['z0']) & (Ps[:, 2] < fe.SCR['z1'])
    ts = np.where(on, ts, np.inf)
    t = np.minimum.reduce([td, tw, ts])
    Q = Pw + np.where(np.isfinite(t), t, 0)[:, None] * Vw
    kind = np.select([t == ts, t == td, t == tw], [1, 2, 3], 0); kind[~np.isfinite(t)] = 0
    return Q, kind


def celle(Qa, Qb, w, ga, gb, h):
    ia = np.rint((Qa - ga[0]) / (ga[1] - ga[0])).astype(int); ib = np.rint((Qb - gb[0]) / (gb[1] - gb[0])).astype(int)
    ok = (ia >= 0) & (ia < len(ga)) & (ib >= 0) & (ib < len(gb))
    ok[ok] &= (np.abs(Qa[ok] - ga[ia[ok]]) < h) & (np.abs(Qb[ok] - gb[ib[ok]]) < h)
    E = np.bincount(ib[ok] * len(ga) + ia[ok], weights=w[ok], minlength=len(ga) * len(gb))
    return E.reshape(len(gb), len(ga)) / (2 * h) ** 2


TX, TY = np.linspace(-0.30, 0.30, 7), np.linspace(0.05, 0.40, 5)
WX, WZ = np.linspace(-0.70, 0.70, 8), np.linspace(0.05, 1.20, 6)
DX, DY = np.linspace(-0.68, 0.68, 8), np.linspace(0.02, 0.73, 5)
N = 2_000_000
for modus in ('2D', '3D'):
    rng = np.random.default_rng(7)
    P, V, w = spor(N, modus == '3D', rng)
    w = w / N
    # arbeid
    Pw, Vw = til_verda(P, V, 0.0, rng); Q, kd = treff(Pw, Vw)
    d = kd == 2
    Et = celle(Q[d, 0], Q[d, 1], w[d], TX, TY, 0.015)
    Phi = fe.E_TASK / Et.mean()
    # stemning
    Pw, Vw = til_verda(P, V, a105, rng); Q, kd = treff(Pw, Vw)
    wv = kd == 3; dd = kd == 2
    Ew = celle(Q[wv, 0], Q[wv, 2], w[wv], WX, WZ, 0.025)
    Ed = celle(Q[dd, 0], Q[dd, 1], w[dd], DX, DY, 0.025)
    felt = wv & (np.abs(Q[:, 0]) <= 0.70) & (Q[:, 2] >= 0.05) & (Q[:, 2] <= 1.20)
    Ew_a = w[felt].sum() / (1.4 * 1.15)
    # søyle (boks frå geometri) i vegen? del av fluksen som kryssar søyleboksen før veggen
    yb0, yb1 = M.COL_Y, M.COL_Y + M.COL_F
    with np.errstate(divide='ignore', invalid='ignore'):
        tc = (yb0 - Pw[:, 1]) / Vw[:, 1]
    Pc = Pw + np.where(np.isfinite(tc) & (tc > 0), tc, 0)[:, None] * Vw
    sy = (Vw[:, 1] > 0) & (np.abs(Pc[:, 0]) < M.COL_W / 2) & (Pc[:, 2] < za + M.COL_F) & (Pc[:, 2] > 0.004)
    # bandet: midtre z for treff på veggen, rekna i x-bolkar
    band = {}
    for x0_, x1_ in ((0, 0.1), (0.25, 0.35), (0.45, 0.55), (0.6, 0.7)):
        m = wv & (np.abs(Q[:, 0]) >= x0_) & (np.abs(Q[:, 0]) < x1_)
        if m.sum() > 100:
            zs_ = Q[m, 2]; ww = w[m]
            o = np.argsort(zs_); cw = np.cumsum(ww[o]) / ww.sum()
            band[f'|x| {x0_}-{x1_}'] = [round(float(np.interp(q, cw, zs_[o])), 3) for q in (0.1, 0.5, 0.9)]
    ut[f'spor_{modus}'] = dict(Phi=float(Phi), U0=float(Et.min() / Et.mean()), Ev_gitter=float(Ew.mean() * Phi * fe.DIM_STEM),
                              Ev_areal=float(Ew_a * Phi * fe.DIM_STEM), R_gitter=float(Ew.mean() / (Ew.mean() + Ed.mean())),
                              del_soyle=float(w[sy].sum() / w.sum()), del_ut_av_LED=float(w.sum()),
                              rad_snitt_lx=[round(float(v), 1) for v in Ew.mean(1) * Phi * fe.DIM_STEM],
                              band_z_10_50_90=band)

print(json.dumps(ut, indent=1, ensure_ascii=False, default=float))
