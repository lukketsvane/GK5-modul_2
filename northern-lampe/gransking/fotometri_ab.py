# -*- coding: utf-8 -*-
"""Gransking 2 · linse: fotometri for (a) bru og (b) krok, og den felles lysmodellen. 2026-11-13.

Eigen kode frå grunnformlane. Ingen kall til felles.py eller motorane i kontrollrekninga (berre i del K, til samanlikning).
  dE = L·cosθe·cosθr·dA/r²  (kvadratur, med eigne okkludarar: skjerm, leppe, boks)
  Lamberts polygonformel     (eksakt for eit plant, fritt rektangel)
  eigen Monte Carlo i røyrhulrommet (LED på bakvegg / i aksen, diffus / spegel)
  eigen spegling i skjermen med skjermtilt
  eigen linjekjelde for (c) prisme (fjernfelt som motoren, og nærfelt med plata sin breidd)

Køyr:  PYTHONIOENCODING=utf-8 python fotometri_ab.py   -> fotometri_ab.json + tabellar på stdout
"""
import json
import math
import os
import sys
import time

import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
rng = np.random.default_rng(13112026)
UT = {}
T0 = time.time()

# ---------------- scene: tal skrivne av frå felles.py l. 17–26 (ikkje importert) ----------------
SX0, SX1, SY, SZ0, SZ1 = -0.275, 0.275, 0.45, 0.10, 0.42
WY = 0.75
TX0, TX1, TY0, TY1 = -0.30, 0.30, 0.05, 0.40
WX0, WX1, WZ0, WZ1 = -0.70, 0.70, 0.05, 1.20
DX0, DX1, DY0, DY1 = -0.70, 0.70, 0.0, 0.75
R, BETA = 0.022, math.radians(25.0)
RHO_ROYR, E_TASK, DIM = 0.85, 500.0, 0.25
RHO_VEGG, RHO_SKJ_DIFF, RHO_SKJ_SPEG = 0.75, 0.04, 0.04      # vegg som lysstudie.py; skjerm som oppgåva
UP, MOT_BRUKAR = np.array([0, 0, 1.0]), np.array([0, -1.0, 0])
KONSEPT = json.load(open(os.path.join(ROOT, 'konsept.json'), encoding='utf-8'))
AUGE = {'nominell': (0, -0.30, 0.45), 'x -15': (-0.15, -0.30, 0.45), 'x +15': (0.15, -0.30, 0.45),
        'lener 15 fram': (0, -0.15, 0.45), '5 lågare': (0, -0.30, 0.40), '5 høgare': (0, -0.30, 0.50),
        'fram 15 + lågare 5': (0, -0.15, 0.40), 'fram 15 + høgare 5': (0, -0.15, 0.50)}


def e_dir(psi):
    p = math.radians(psi)
    return np.array([0.0, -math.sin(p), -math.cos(p)])


def v_dir(psi):
    p = math.radians(psi)
    return np.array([0.0, math.cos(p), -math.sin(p)])          # x̂ × e


# ---------------- kjelder: kordeflata i røyret ----------------
def slot(yp, hp, psi, xr):
    e, v = e_dir(psi), v_dir(psi)
    return [dict(c=np.array([(a + b) / 2, yp, hp]) + R * math.cos(BETA) * e, u=np.array([1.0, 0, 0]), hu=(b - a) / 2,
                 v=v, hv=R * math.sin(BETA), n=e) for a, b in xr]


KONF = {'a': dict(yp=0.18, hp=0.62, xr=[(-0.315, 0.315)], Lcav=0.63, opn=[(-0.315, 0.315)]),
        'b': dict(yp=0.25, hp=0.62, xr=[(-0.30, -0.02), (0.02, 0.30)], Lcav=0.6016, opn=[(-0.30, -0.02), (0.02, 0.30)])}
PSI_ARB, PSI_STEM = -20, -95


def areal(rs):
    return sum(4 * r['hu'] * r['hv'] for r in rs)


def eta_formel(A_ap, Lcav, direkte):
    f = A_ap / (2 * math.pi * R * Lcav + 2 * math.pi * R ** 2)
    return direkte + (1 - direkte) * RHO_ROYR * f / (1 - RHO_ROYR * (1 - f)), f


# η slik motoren reknar det (form01/motor.py l. 62–67): A_ap frå opning(B, 0) utan navfrådrag, Lcav = k·L
WAP = 2 * R * math.sin(BETA)
ETA = {'a': eta_formel(0.630 * WAP, 1.12 * 0.536, math.sin(BETA))[0], 'b': eta_formel(0.600 * WAP, 0.64 * 0.94, math.sin(BETA))[0]}


def punkt(rs, du=0.005, dv=0.003):
    P, N, dA = [], [], []
    for r in rs:
        nu, nv = max(1, round(2 * r['hu'] / du)), max(1, round(2 * r['hv'] / dv))
        su = ((np.arange(nu) + .5) / nu * 2 - 1) * r['hu']
        sv = ((np.arange(nv) + .5) / nv * 2 - 1) * r['hv']
        U, V = np.meshgrid(su, sv, indexing='ij')
        p = r['c'] + U.ravel()[:, None] * r['u'] + V.ravel()[:, None] * r['v']
        P.append(p); N.append(np.tile(r['n'], (len(p), 1))); dA.append(np.full(len(p), 4 * r['hu'] * r['hv'] / (nu * nv)))
    return np.vstack(P), np.vstack(N), np.concatenate(dA)


# ---------------- Lamberts polygonformel ----------------
def E_lam(rs, Q, nq):
    """lx per cd/m². Eksakt for plane rektangel heilt over horisonten til mottakaren. Ingen okkludarar."""
    E = np.zeros(len(Q))
    for r in rs:
        V = np.array([r['c'] + a * r['hu'] * r['u'] + b * r['hv'] * r['v'] for a, b in ((1, 1), (-1, 1), (-1, -1), (1, -1))])
        D = V[None] - Q[:, None]                                         # (m,4,3)
        foran = (Q - r['c']) @ r['n'] > 0
        over = ((D @ nq) > 0).all(1)
        assert over[foran].all(), 'kjelda kryssar horisonten til mottakaren'
        Dn = D / np.linalg.norm(D, axis=2, keepdims=True)
        tot = np.zeros(len(Q))
        for i in range(4):
            a, b = Dn[:, i], Dn[:, (i + 1) % 4]
            c = np.cross(a, b)
            nc = np.linalg.norm(c, axis=1)
            tot += np.arctan2(nc, (a * b).sum(1)) * (c @ nq) / nc
        E += np.where(foran, 0.5 * np.abs(tot), 0.0)
    return E


# ---------------- okkludarar ----------------
def okk_rekt(c0, e1, h1, e2, h2):
    c0, e1, e2 = (np.asarray(x, float) for x in (c0, e1, e2))
    m = np.cross(e1, e2)

    def f(P, Q):
        a = (P - c0) @ m
        b = (Q - c0) @ m
        kr = a[:, None] * b[None, :] < 0
        with np.errstate(divide='ignore', invalid='ignore'):
            s = np.where(kr, a[:, None] / (a[:, None] - b[None, :]), 0.0)
        X = P[:, None, :] + s[..., None] * (Q[None] - P[:, None])
        return kr & (np.abs((X - c0) @ e1) < h1) & (np.abs((X - c0) @ e2) < h2)
    return f


def okk_boks(lo, hi):
    lo, hi = np.asarray(lo, float), np.asarray(hi, float)

    def f(P, Q):
        D = Q[None] - P[:, None]
        t0 = np.zeros(D.shape[:2]); t1 = np.ones(D.shape[:2])
        for k in range(3):
            p = P[:, None, k]
            with np.errstate(divide='ignore', invalid='ignore'):
                ta, tb = (lo[k] - p) / D[..., k], (hi[k] - p) / D[..., k]
            par = np.abs(D[..., k]) < 1e-15
            inne = (p > lo[k]) & (p < hi[k])
            mn = np.where(par, np.where(inne, -np.inf, np.inf), np.minimum(ta, tb))
            mx = np.where(par, np.where(inne, np.inf, -np.inf), np.maximum(ta, tb))
            t0, t1 = np.maximum(t0, mn), np.minimum(t1, mx)
        return t0 < t1
    return f


SKJERM = okk_rekt(((SX0 + SX1) / 2, SY, (SZ0 + SZ1) / 2), (1, 0, 0), (SX1 - SX0) / 2, (0, 0, 1), (SZ1 - SZ0) / 2)


def E_kv(P, N, dA, Q, nq, okk=(SKJERM,), bit=300):
    out = np.zeros(len(Q))
    for i in range(0, len(Q), bit):
        q = Q[i:i + bit]
        d = q[None] - P[:, None]
        r2 = np.einsum('ijk,ijk->ij', d, d)
        r = np.sqrt(r2)
        ce = np.einsum('ijk,ik->ij', d, N) / r
        cr = -(d @ nq) / r
        w = np.where((ce > 0) & (cr > 0), ce * cr / r2, 0.0)
        for o in okk:
            w[o(P, q)] = 0.0
        out[i:i + bit] = (w * dA[:, None]).sum(0)
    return out


# ---------------- gitter ----------------
def kant(x0, x1, nx, y0, y1, ny):
    X, Y = np.meshgrid(np.linspace(x0, x1, nx), np.linspace(y0, y1, ny))
    return X.ravel(), Y.ravel()


def celle(x0, x1, nx, y0, y1, ny):
    X, Y = np.meshgrid(x0 + (np.arange(nx) + .5) / nx * (x1 - x0), y0 + (np.arange(ny) + .5) / ny * (y1 - y0))
    return X.ravel(), Y.ravel()


bord = lambda g: np.c_[g[0], g[1], np.zeros(len(g[0]))]
vegg = lambda g: np.c_[g[0], np.full(len(g[0]), WY - 1e-3), g[1]]
skjermflate = lambda g: np.c_[g[0], np.full(len(g[0]), SY - 1e-4), g[1]]
TASK_M = bord(kant(TX0, TX1, 7, TY0, TY1, 5))
TASK_EN = bord(celle(TX0, TX1, 5, TY0, TY1, 3))          # EN 12464-1: p = 0,2·5^log10(0,6) = 0,14 m -> 5 × 3 celler
TASK_F = bord(celle(TX0, TX1, 120, TY0, TY1, 70))        # 5 mm
WALL_M = vegg(kant(WX0, WX1, 8, WZ0, WZ1, 6))
WALL_F = vegg(celle(WX0, WX1, 70, WZ0, WZ1, 58))         # 2 cm
DESK_M = bord(kant(-0.68, 0.68, 8, 0.02, 0.73, 5))
DESK_F = bord(celle(DX0, DX1, 70, DY0, DY1, 38))
SKJ_F = skjermflate(celle(SX0, SX1, 55, SZ0, SZ1, 32))   # 1 cm
A_WF, A_DF, A_TF = (WX1 - WX0) * (WZ1 - WZ0), (DX1 - DX0) * (DY1 - DY0), (TX1 - TX0) * (TY1 - TY0)


def pst(x, ref):
    return 100 * (x / ref - 1)


def hdr(s):
    print('\n' + '=' * 110 + '\n' + s + '\n' + '=' * 110, flush=True)


# =====================================================================================
hdr('DEL 1 · (a) og (b): Φ, U0, veggdel, veggluminans. Eigen kode, finare gitter')
D1 = {}
for k in 'ab':
    c = KONF[k]
    srcW, srcM = slot(c['yp'], c['hp'], PSI_ARB, c['xr']), slot(c['yp'], c['hp'], PSI_STEM, c['xr'])
    A, eta = areal(srcW), ETA[k]
    Phi = lambda Em: E_TASK * math.pi * A / (eta * Em)
    Em_M, Em_EN, Em_F = (E_lam(srcW, g, UP) for g in (TASK_M, TASK_EN, TASK_F))
    # kvadratur som andre metode på motorgitteret
    P, N, dA = punkt(srcW)
    Em_Mq = E_kv(P, N, dA, TASK_M, UP)
    Ef2 = Em_F.reshape(70, 120)
    r = dict(A_cm2=A * 1e4, eta=eta,
             Phi_7x5=Phi(Em_M.mean()), U0_7x5=Em_M.min() / Em_M.mean(), Phi_7x5_kvad=Phi(Em_Mq.mean()),
             Phi_EN5x3=Phi(Em_EN.mean()), U0_EN5x3=Em_EN.min() / Em_EN.mean(),
             Phi_fin=Phi(Em_F.mean()), U0_fin_celle=Em_F.min() / Em_F.mean(),
             Phi_json=KONSEPT[k]['Phi_lm'], U0_json=KONSEPT[k]['U0'])
    # hjørneverdi eksakt (kanten av sona) / arealsnitt
    Eh = E_lam(srcW, bord((np.array([TX0, TX1, TX0, TX1]), np.array([TY0, TY0, TY1, TY1]))), UP)
    r['U0_hjorne_areal'] = Eh.min() / Em_F.mean()
    r['L_ap_500'] = E_TASK / Em_M.mean()
    r['L_ap_500_fin'] = E_TASK / Em_F.mean()
    r['avvik_Phi_pst'] = pst(r['Phi_7x5'], r['Phi_json']); r['avvik_U0_pst'] = pst(r['U0_7x5'], r['U0_json'])
    # stemning, Φ frå motorgitteret (slik konsept.json) og frå det fine gitteret
    P, N, dA = punkt(srcM)
    Ew_M, Ed_M = E_kv(P, N, dA, WALL_M, MOT_BRUKAR), E_kv(P, N, dA, DESK_M, UP)
    Ew_F, Ed_F = E_kv(P, N, dA, WALL_F, MOT_BRUKAR), E_kv(P, N, dA, DESK_F, UP)
    for lab, PhiW in (('motor', r['Phi_7x5']), ('fin', r['Phi_fin'])):
        Lst = eta * PhiW * DIM / (math.pi * A)
        ew_m, ed_m, ew_f, ed_f = Ew_M.mean() * Lst, Ed_M.mean() * Lst, Ew_F * Lst, Ed_F.mean() * Lst
        r[f'stem_{lab}'] = dict(Phi_LED_stem=PhiW * DIM, L_opning=Lst,
                                Ev_8x6=ew_m, R_8x6=ew_m / (ew_m + ed_m), Ev_fin=ew_f.mean(), Ed_fin=ed_f, R_fin=ew_f.mean() / (ew_f.mean() + ed_f),
                                Lv_snitt=RHO_VEGG * ew_f.mean() / math.pi, Lv_maks=RHO_VEGG * ew_f.max() / math.pi,
                                Ev_maks=ew_f.max(), maks_snitt=ew_f.max() / ew_f.mean(),
                                del_felt_over_halv_maks=float((ew_f > 0.5 * ew_f.max()).mean()),
                                del_felt_under_5lx=float((ew_f < 5).mean()),
                                lm_paa_veggfelt=ew_f.mean() * A_WF, del_av_LED=ew_f.mean() * A_WF / (PhiW * DIM))
    r['Ev_json'], r['R_json'] = KONSEPT[k]['Ev_stem'], KONSEPT[k]['R_stem']
    r['avvik_Ev_pst'] = pst(r['stem_motor']['Ev_8x6'], r['Ev_json'])
    D1[k] = r
    s0, s1 = r['stem_motor'], r['stem_fin']
    print(f"({k}) A {A*1e4:.1f} cm²  η {eta:.4f}   (konsept.json: Φ {r['Phi_json']:.1f}, U0 {r['U0_json']:.4f}, Ē_vegg {r['Ev_json']:.2f}, R {r['R_json']:.4f})")
    print(f"    Φ for 500 lx: 7×5 kant {r['Phi_7x5']:.1f} ({r['avvik_Phi_pst']:+.2f} %)  [kvadratur {r['Phi_7x5_kvad']:.1f}]   EN 5×3 celle {r['Phi_EN5x3']:.1f}   5 mm areal {r['Phi_fin']:.1f} ({pst(r['Phi_fin'], r['Phi_json']):+.1f} %)")
    print(f"    U0: 7×5 {r['U0_7x5']:.4f}  EN 5×3 {r['U0_EN5x3']:.3f}  5 mm celle {r['U0_fin_celle']:.3f}  hjørne/arealsnitt {r['U0_hjorne_areal']:.3f}   L i opninga {r['L_ap_500']:.0f} cd/m² ({r['L_ap_500_fin']:.0f} fint)")
    print(f"    stemning (Φ motor): Ē_vegg 8×6 {s0['Ev_8x6']:.2f} lx ({r['avvik_Ev_pst']:+.2f} %) R {s0['R_8x6']:.4f} | 2 cm: Ē {s0['Ev_fin']:.1f} lx R {s0['R_fin']:.3f}  L_vegg snitt {s0['Lv_snitt']:.1f} maks {s0['Lv_maks']:.1f} cd/m² (ρ {RHO_VEGG})  maks/snitt {s0['maks_snitt']:.2f}  {100*s0['del_felt_over_halv_maks']:.0f} % av feltet > ½ maks")
    print(f"    stemning (Φ fin):   Ē_vegg 8×6 {s1['Ev_8x6']:.2f} lx | 2 cm: Ē {s1['Ev_fin']:.1f} lx  L_vegg snitt {s1['Lv_snitt']:.1f} cd/m²   {s1['lm_paa_veggfelt']:.0f} lm på veggfeltet = {100*s1['del_av_LED']:.0f} % av LED-lm i stemning")
UT['del1'] = D1

# =====================================================================================
hdr('DEL 2 · Lys på skjermflata, luminans og kontrast')
D2 = {}
LW, CR0 = 200.0, 1000.0                                       # kvit 200 cd/m², ekte kontrast 1000:1 (IPS) -> svart 0,2
LB = LW / CR0


def kontrast(Lr):
    return dict(Lr=Lr, CR=(LW + Lr) / (LB + Lr), weber_tekst=(LW - LB) / (LW + Lr), svart_x=(LB + Lr) / LB,
                gra20_mot_kvit=(LW + Lr) / (0.2 * LW + Lr))


for k in 'ab':
    c = KONF[k]
    srcW = slot(c['yp'], c['hp'], PSI_ARB, c['xr'])
    A, eta = areal(srcW), ETA[k]
    Es_lam = E_lam(srcW, SKJ_F, MOT_BRUKAR)                  # per cd/m², eksakt (ingenting mellom kjelde og skjerm)
    P, N, dA = punkt(srcW)
    Es_kv = E_kv(P, N, dA, SKJ_F, MOT_BRUKAR, okk=())
    out = {}
    for lab, PhiW in (('json', KONSEPT[k]['Phi_lm']), ('fin', D1[k]['Phi_fin'])):
        L = eta * PhiW / (math.pi * A)
        Es = Es_lam * L
        Lr = RHO_SKJ_DIFF * Es.mean() / math.pi
        out[lab] = dict(Phi=PhiW, E_snitt=Es.mean(), E_maks=Es.max(), E_min=Es.min(), Lr_matt=Lr,
                        Lr_matt_maks=RHO_SKJ_DIFF * Es.max() / math.pi, kontrast_matt=kontrast(Lr),
                        Lr_blank_diffus=0.005 * Es.mean() / math.pi, kontrast_blank=kontrast(0.005 * Es.mean() / math.pi),
                        L_spegelbilete_blank=RHO_SKJ_SPEG * L)
    out['avvik_lam_kvad_pst'] = pst(Es_kv.mean(), Es_lam.mean())
    D2[k] = out
    o = out['json']
    print(f"({k}) Φ {o['Phi']:.0f} lm: E på skjermen snitt {o['E_snitt']:.0f} lx (maks {o['E_maks']:.0f}, min {o['E_min']:.0f})  [Lambert mot kvadratur {out['avvik_lam_kvad_pst']:+.2f} %;  med Φ fin: {out['fin']['E_snitt']:.0f} lx]")
    kk = o['kontrast_matt']
    print(f"    matt (ρ {RHO_SKJ_DIFF} diffus): L_refl {o['Lr_matt']:.1f} cd/m² (maks {o['Lr_matt_maks']:.1f})  ->  CR {CR0:.0f}:1 -> {kk['CR']:.0f}:1,  svart {kk['svart_x']:.0f}× lysare,"
          f"  kvit/20 %-grå {LW/(0.2*LW):.1f} -> {kk['gra20_mot_kvit']:.2f},  Weber svart tekst {(LW-LB)/LW:.3f} -> {kk['weber_tekst']:.3f}")
    kb = o['kontrast_blank']
    print(f"    blank (0,5 % diffus): L_refl {o['Lr_blank_diffus']:.2f} cd/m²  CR -> {kb['CR']:.0f}:1.   Om opninga vert spegla: spegelbilete {o['L_spegelbilete_blank']:.0f} cd/m² (ρ_s 0,04 · L)")
# (c) frå skjerm.json (motoren) til samanlikning; eigen sjekk i del 4
sk_c = json.load(open(os.path.join(ROOT, 'form04', 'skjerm.json'), encoding='utf-8'))
D2['c_motor'] = dict(E_snitt=sk_c['E_skjerm_snitt'], kontrast_matt=kontrast(RHO_SKJ_DIFF * sk_c['E_skjerm_snitt'] / math.pi))
print(f"(c) motoren: {sk_c['E_skjerm_snitt']:.1f} lx -> L_refl {RHO_SKJ_DIFF*sk_c['E_skjerm_snitt']/math.pi:.2f} cd/m², CR {D2['c_motor']['kontrast_matt']['CR']:.0f}:1")
UT['del2'] = D2


# =====================================================================================
def sikt(src, eye, du=0.005, dv=0.002):
    P, N, dA = punkt(src, du, dv)
    E = np.asarray(eye, float)
    d = E[None] - P
    dist = np.linalg.norm(d, axis=1)
    cs = (d * N).sum(1) / dist
    fri = (cs > 0) & ~SKJERM(P, E[None])[:, 0]
    om = float((np.where(fri, cs, 0) * dA / dist ** 2).sum())
    return float((fri * dA).sum() / dA.sum()), om, float(np.degrees(np.arcsin(cs)).max())


def margin(src):
    """Kor mykje auga kan flytte seg før det ser opninga: lågare (cm) og fram (cm) frå nominelt auge."""
    r = src[0]
    n, c = r['n'], r['c']
    # planet n·(E − c) = 0 gjennom kordesenter; kanten med størst n·(hjørne) avgjer ikkje (planet er eitt plan)
    zk = c[2] + n[1] / (-n[2]) * (-0.30 - c[1])
    yk = c[1] + (0.45 - c[2]) * (-n[2]) / n[1] if abs(n[1]) > 1e-9 else np.inf
    return dict(lagare_cm=(0.45 - zk) * 100, fram_cm=(yk + 0.30) * 100)


def spegling(src, eye, tilt, du=0.005, dv=0.002):
    """Del av opningsflata auga ser spegla i skjermen. Skjermen roterer om underkanten, toppen bakover (tilt > 0)."""
    P, N, dA = punkt(src, du, dv)
    t = math.radians(tilt)
    o = np.array([0.0, SY, SZ0])
    u = np.array([0.0, math.sin(t), math.cos(t)])
    m = np.array([0.0, -math.cos(t), math.sin(t)])
    E = np.asarray(eye, float)
    Em = E - 2 * ((E - o) @ m) * m
    d = P - Em
    with np.errstate(divide='ignore', invalid='ignore'):
        s = ((o - Em) @ m) / (d @ m)
    X = Em + s[:, None] * d
    h = (X - o) @ u
    ok = ((P - o) @ m > 0) & (s > 0) & (s < 1) & (np.abs(X[:, 0]) < SX1) & (h > 0) & (h < SZ1 - SZ0) & (((X - P) * N).sum(1) > 0)
    # vinkelavstand frå spegelbiletet til næraste skjermpunkt (grader), sett frå auga
    Pm = P - 2 * ((P - o) @ m)[:, None] * m[None]
    dirP = (Pm - E) / np.linalg.norm(Pm - E, axis=1, keepdims=True)
    hs = np.linspace(0, SZ1 - SZ0, 33); xs = np.linspace(SX0, SX1, 23)
    S = (o + hs[:, None, None] * u + xs[None, :, None] * np.array([1.0, 0, 0])).reshape(-1, 3)
    dirS = (S - E) / np.linalg.norm(S - E, axis=1, keepdims=True)
    gap = float(np.degrees(np.arccos(np.clip((dirP[::7] @ dirS.T).max(), -1, 1))))
    return float((ok * dA).sum() / dA.sum()), gap


def krit_tilt(src, eye):
    for tt in np.arange(0, 45.01, 0.25):
        if spegling(src, eye, tt, 0.01, 0.003)[0] > 0:
            return float(tt)
    return None


hdr('DEL 3 · Synlegheit og spegling i arbeidsstilling (ψ −20°), eigne siktliner og eigen spegel med skjermtilt')
D3 = {}
for k in 'ab':
    c = KONF[k]
    srcW = slot(c['yp'], c['hp'], PSI_ARB, c['xr'])
    L = D1[k]['L_ap_500']
    D3[k] = dict(margin=margin(srcW), auge={})
    g = D3[k]['margin']
    print(f"({k}) L i opninga {L:.0f} cd/m².  Opningsplanet går {g['lagare_cm']:.1f} cm under nominelt auge; auga ser opninga etter {g['fram_cm']:.1f} cm framlening")
    for nm, eye in AUGE.items():
        fr, om, vmax = sikt(srcW, eye)
        kt = krit_tilt(srcW, eye)
        sp0, gap0 = spegling(srcW, eye, 0.0)
        _, gap10 = spegling(srcW, eye, 10.0)
        E_auge = L * om
        D3[k]['auge'][nm] = dict(synleg_del=fr, omega_sr=om, E_ved_auga_lx=E_auge, vinkel_maks=vmax, krit_tilt=kt, spegla_tilt0=sp0, gap_tilt0=gap0, gap_tilt10=gap10)
        print(f"    {nm:20s} synleg {100*fr:5.1f} %  ω {om*1e3:6.2f} msr  E_auge {E_auge:6.0f} lx   spegling: første ved tilt {kt}°, avstand frå spegelbilete til skjermen {gap0:4.1f}° (tilt 0) / {gap10:4.1f}° (tilt 10)")
UT['del3'] = D3

# =====================================================================================
hdr('DEL 2b · Søk over vrivinkelen ψ: Φ, U0, skjermlys, skjerming (Φ skalert til 500 lx)')
D2b = {}
for k in 'ab':
    c = KONF[k]
    rows = []
    for psi in range(-60, 11, 1):
        src = slot(c['yp'], c['hp'], psi, c['xr'])
        A, eta = areal(src), ETA[k]
        try:
            Em = E_lam(src, TASK_M, UP); Een = E_lam(src, TASK_EN, UP); Ef = E_lam(src, TASK_F[::7], UP)
        except AssertionError:
            continue
        Phi = E_TASK * math.pi * A / (eta * Em.mean())
        Es = E_lam(src, SKJ_F[::3], MOT_BRUKAR) * eta * Phi / (math.pi * A)
        mg = margin(src)
        vis = {nm: bool(sikt(src, e, 0.01, 0.004)[0] > 0) for nm, e in AUGE.items()}
        rows.append(dict(psi=psi, Phi=Phi, U0=Em.min() / Em.mean(), U0_EN=Een.min() / Een.mean(), Phi_fin=E_TASK * math.pi * A / (eta * Ef.mean()),
                         E_skjerm=float(Es.mean()), E_skjerm_maks=float(Es.max()), lagare_cm=mg['lagare_cm'], fram_cm=mg['fram_cm'],
                         synleg_nom=vis['nominell'], synleg_nokon=any(vis.values()), krit_tilt=krit_tilt(src, AUGE['nominell'])))
    D2b[k] = rows
    ref = next(r for r in rows if r['psi'] == PSI_ARB)
    ok_nom = [r for r in rows if not r['synleg_nom'] and r['U0'] >= 0.4]
    ok_rob = [r for r in rows if not r['synleg_nokon'] and r['U0'] >= 0.4]
    bn, br = min(ok_nom, key=lambda r: r['E_skjerm']), min(ok_rob, key=lambda r: r['E_skjerm'])
    print(f"({k}) ψ −20 (vald): Φ {ref['Phi']:.0f} lm, U0 {ref['U0']:.2f}, skjerm {ref['E_skjerm']:.0f} lx, margin {ref['lagare_cm']:.1f} cm lågare / {ref['fram_cm']:.1f} cm fram, spegling frå tilt {ref['krit_tilt']}°")
    print(f"    minst skjermlys, skjerma for nominelt auge: ψ {bn['psi']:+d}  {bn['E_skjerm']:.0f} lx, Φ {bn['Phi']:.0f} lm, U0 {bn['U0']:.2f}")
    print(f"    minst skjermlys, skjerma for alle 8 auge:  ψ {br['psi']:+d}  {br['E_skjerm']:.0f} lx, Φ {br['Phi']:.0f} lm ({pst(br['Phi'], ref['Phi']):+.1f} %), U0 {br['U0']:.2f}, spegling frå tilt {br['krit_tilt']}°")
    for r in rows:
        if r['psi'] % 5 == 0 and -50 <= r['psi'] <= 10:
            print(f"      ψ {r['psi']:+4d}: Φ {r['Phi']:6.0f} ({pst(r['Phi'], ref['Phi']):+5.1f} %)  U0 {r['U0']:.2f}/{r['U0_EN']:.2f}  skjerm {r['E_skjerm']:5.0f} lx (maks {r['E_skjerm_maks']:5.0f})"
                  f"  margin {r['lagare_cm']:+6.1f} cm lågare {r['fram_cm']:+6.1f} cm fram  synleg nom/nokon {int(r['synleg_nom'])}/{int(r['synleg_nokon'])}  spegling frå tilt {r['krit_tilt']}°")
UT['psi_sok'] = D2b

# --- leppe: ei svart skjermkant langs opninga, loddrett ned frå kanten på brukarsida eller veggsida ---
hdr('DEL 2c · Leppe langs opninga (svart, loddrett ned), ψ −20°')
D2c = {}
for k in 'ab':
    c = KONF[k]
    src = slot(c['yp'], c['hp'], PSI_ARB, c['xr'])
    A, eta = areal(src), ETA[k]
    P, N, dA = punkt(src, 0.005, 0.0012)
    r0 = src[0]
    xs0, xs1 = min(a for a, _ in c['xr']), max(b for _, b in c['xr'])
    rad = {}
    for side in ('vegg', 'brukar'):
        for h in (0, 3, 6, 10, 15, 20, 30):
            sg = 1 if side == 'vegg' else -1
            kantp = r0['c'] + sg * r0['hv'] * r0['v']
            kantp = np.array([0.0, kantp[1], kantp[2]])
            okk = [] if h == 0 else [okk_rekt(kantp + np.array([(xs0 + xs1) / 2, 0, -h / 2000]), (1, 0, 0), (xs1 - xs0) / 2 + 0.01, (0, 0, 1), h / 2000)]
            Et = E_kv(P, N, dA, TASK_M, UP, okk=okk)
            Ete = E_kv(P, N, dA, TASK_EN, UP, okk=okk)
            Phi = E_TASK * math.pi * A / (eta * Et.mean())
            Es = E_kv(P, N, dA, SKJ_F[::3], MOT_BRUKAR, okk=okk) * eta * Phi / (math.pi * A)
            vis = {}
            for nm, e in AUGE.items():
                e = np.asarray(e, float)
                blokk = okk[0](P, e[None])[:, 0] if okk else np.zeros(len(P), bool)
                vis[nm] = float(((((e[None] - P) * N).sum(1) > 0) & ~blokk).mean())
            rad[f'{side}_{h}'] = dict(Phi=Phi, U0=Et.min() / Et.mean(), U0_EN=Ete.min() / Ete.mean(), E_skjerm=float(Es.mean()), E_skjerm_maks=float(Es.max()),
                                     synleg={nm: v for nm, v in vis.items() if v > 0})
            q = rad[f'{side}_{h}']
            print(f"({k}) leppe {side:6s} {h:2d} mm: Φ {Phi:6.0f} lm  U0 {q['U0']:.2f}/{q['U0_EN']:.2f}  skjerm {q['E_skjerm']:4.0f} lx (maks {q['E_skjerm_maks']:4.0f})  synleg for: "
                  + (', '.join(f"{nm} {100*v:.0f} %" for nm, v in q['synleg'].items()) or 'ingen'))
    D2c[k] = rad
UT['leppe'] = D2c


# =====================================================================================
# MC i røyrhulrommet (eigen kode)
def lambert_retning(n_, nn):
    """cosinusvekta retningar om einingsnormalane nn (n,3)."""
    rr, ph = np.sqrt(rng.random(n_)), 2 * math.pi * rng.random(n_)
    a = np.where(np.abs(nn[:, 0:1]) < 0.9, np.array([[1.0, 0, 0]]), np.array([[0, 1.0, 0]]))
    t1 = np.cross(nn, a); t1 /= np.linalg.norm(t1, axis=1, keepdims=True)
    t2 = np.cross(nn, t1)
    return (rr * np.cos(ph))[:, None] * t1 + (rr * np.sin(ph))[:, None] * t2 + np.sqrt(1 - rr ** 2)[:, None] * nn


def mc_royr(n, Lcav, opn, led='bakvegg', vegg='diffus', rho=RHO_ROYR, led_halvvinkel=13.0, maks=200):
    """Lokale koordinatar: x langs aksen, a mot slissemidten, b = x̂ × a. Slisse |φ| < β der x er i opn. Endeskiver ved ±Lcav/2.
    Returnerer utgangsstrålar (posisjon, retning) og tal."""
    p = np.zeros((n, 3)); p[:, 0] = (rng.random(n) - .5) * Lcav
    if led == 'bakvegg':
        phi = math.pi + np.radians(led_halvvinkel) * (2 * rng.random(n) - 1)
        p[:, 1], p[:, 2] = R * np.cos(phi) * 0.9999, R * np.sin(phi) * 0.9999
        nn = -np.c_[np.zeros(n), np.cos(phi), np.sin(phi)]
    else:
        nn = np.tile([0, 1.0, 0], (n, 1))
    d = lambert_retning(n, nn)
    live = np.ones(n, bool); sprett = np.zeros(n, int)
    UTp, UTd, UTs = [], [], []
    for it in range(maks):
        i = np.flatnonzero(live)
        if not len(i):
            break
        pa, pb, da, db, px, dx = p[i, 1], p[i, 2], d[i, 1], d[i, 2], p[i, 0], d[i, 0]
        A_ = da ** 2 + db ** 2; B_ = pa * da + pb * db; C_ = pa ** 2 + pb ** 2 - R ** 2
        with np.errstate(divide='ignore', invalid='ignore'):
            tc = np.where(A_ > 1e-16, (-B_ + np.sqrt(np.maximum(B_ ** 2 - A_ * C_, 0))) / A_, np.inf)
            te = np.where(dx > 1e-15, (Lcav / 2 - px) / dx, np.where(dx < -1e-15, (-Lcav / 2 - px) / dx, np.inf))
        lokk = te < tc
        t = np.where(lokk, te, tc)
        q = p[i] + t[:, None] * d[i]
        fi = np.arctan2(q[:, 2], q[:, 1])
        i_opn = np.zeros(len(i), bool)
        for a0, a1 in opn:
            i_opn |= (q[:, 0] > a0) & (q[:, 0] < a1)
        ut = ~lokk & (np.abs(fi) < BETA) & i_opn
        UTp.append(q[ut]); UTd.append(d[i[ut]]); UTs.append(sprett[i[ut]])
        live[i[ut]] = False
        j, qj, lk = i[~ut], q[~ut], lokk[~ut]
        dod = rng.random(len(j)) > rho
        live[j[dod]] = False
        j, qj, lk = j[~dod], qj[~dod], lk[~dod]
        sprett[j] += 1
        nrm = np.where(lk[:, None], np.c_[-np.sign(qj[:, 0]), np.zeros(len(j)), np.zeros(len(j))],
                       -np.c_[np.zeros(len(j)), qj[:, 1], qj[:, 2]] / R)
        if vegg == 'diffus':
            d[j] = lambert_retning(len(j), nrm)
        else:
            dj = d[j]
            d[j] = dj - 2 * (dj * nrm).sum(1)[:, None] * nrm
        p[j] = qj + 1e-9 * nrm
    P = np.vstack(UTp); D = np.vstack(UTd); S = np.concatenate(UTs)
    return dict(P=P, D=D, eta=len(P) / n, direkte=float((S == 0).sum() / n), n=n, sprett_snitt=float(S.mean()))


def spor(h, yp, hp, psi):
    """Til globale koordinatar og første treff: skjerm (framside), bord, vegg. Returnerer treffpunkt per mål."""
    e, v = e_dir(psi), v_dir(psi)
    O = np.array([0.0, yp, hp])
    P = O + h['P'][:, 0:1] * np.array([1.0, 0, 0]) + h['P'][:, 1:2] * e + h['P'][:, 2:3] * v
    D = h['D'][:, 0:1] * np.array([1.0, 0, 0]) + h['D'][:, 1:2] * e + h['D'][:, 2:3] * v
    inf = np.inf
    with np.errstate(divide='ignore', invalid='ignore'):
        ts = np.where(D[:, 1] > 1e-12, (SY - P[:, 1]) / D[:, 1], inf)
        Xs, Zs = P[:, 0] + ts * D[:, 0], P[:, 2] + ts * D[:, 2]
        ts = np.where((ts > 0) & (Xs > SX0) & (Xs < SX1) & (Zs > SZ0) & (Zs < SZ1), ts, inf)
        td = np.where(D[:, 2] < -1e-12, -P[:, 2] / D[:, 2], inf)
        Xd, Yd = P[:, 0] + td * D[:, 0], P[:, 1] + td * D[:, 1]
        td = np.where((Xd > DX0) & (Xd < DX1) & (Yd > DY0) & (Yd < DY1), td, inf)
        tw = np.where(D[:, 1] > 1e-12, (WY - P[:, 1]) / D[:, 1], inf)
        Xw, Zw = P[:, 0] + tw * D[:, 0], P[:, 2] + tw * D[:, 2]
        tw = np.where(Zw > 0, tw, inf)
    T = np.stack([ts, td, tw]); f = T.argmin(0); ingen = ~np.isfinite(T.min(0))
    return dict(skjerm=np.c_[Xs, Zs][(f == 0) & ~ingen], bord=np.c_[Xd, Yd][(f == 1) & ~ingen], vegg=np.c_[Xw, Zw][(f == 2) & ~ingen])


def mc_tal(h, k, psi_a=PSI_ARB, psi_m=PSI_STEM):
    c = KONF[k]
    s = spor(h, c['yp'], c['hp'], psi_a)
    b = s['bord']
    per = 1.0 / h['n']                                                     # lm per LED-stråle per LED-lm
    inn = (b[:, 0] > TX0) & (b[:, 0] < TX1) & (b[:, 1] > TY0) & (b[:, 1] < TY1)
    Em = inn.sum() * per / A_TF                                            # lx per LED-lm, arealsnitt
    Hen, _, _ = np.histogram2d(b[inn, 0], b[inn, 1], bins=[5, 3], range=[[TX0, TX1], [TY0, TY1]])
    Een = Hen * per / (A_TF / 15)
    gx, gy = np.linspace(TX0, TX1, 7), np.linspace(TY0, TY1, 5)            # 3 × 3 cm celler rundt motorpunkta
    Ep = np.array([[((np.abs(b[:, 0] - x) < 0.015) & (np.abs(b[:, 1] - y) < 0.015)).sum() * per / 9e-4 for x in gx] for y in gy])
    Phi = E_TASK / Em
    sk = s['skjerm']
    Es = len(sk) * per / ((SX1 - SX0) * (SZ1 - SZ0)) * Phi
    m = spor(h, c['yp'], c['hp'], psi_m)
    w = m['vegg']
    i_felt = (w[:, 0] > WX0) & (w[:, 0] < WX1) & (w[:, 1] > WZ0) & (w[:, 1] < WZ1)
    d_ = m['bord']
    Ev_per = i_felt.sum() * per / A_WF
    Ed_per = len(d_) * per / A_DF
    return dict(eta=h['eta'], direkte=h['direkte'], Phi_500=Phi, U0_EN5x3=float(Een.min() / Een.mean()), U0_7x5_3cm=float(Ep.min() / Em),
                E_skjerm=Es, stem_Ev_per_LEDlm=Ev_per, stem_R=Ev_per / (Ev_per + Ed_per), stem_del_veggfelt=float(i_felt.sum() / h['n']),
                rader_y=[float(x) for x in Een.mean(0) / Een.mean()])


hdr('DEL 5 · Lysmodellen: lambertsk opning mot Monte Carlo i røyret (eigen kode, 4 M LED-strålar per variant)')
D5 = {}
NMC = int(os.environ.get("NMC", 4_000_000))
for k in 'ab':
    c = KONF[k]
    srcW = slot(c['yp'], c['hp'], PSI_ARB, c['xr'])
    A = areal(srcW)
    for led, vg in (('akse', 'diffus'), ('bakvegg', 'diffus'), ('bakvegg', 'spegel')):
        t1 = time.time()
        h = mc_royr(NMC, c['Lcav'], c['opn'], led, vg)
        r = mc_tal(h, k)
        D5[f'{k}_{led}_{vg}'] = r
        print(f"({k}) LED {led:7s} vegg {vg:6s}: η {r['eta']:.3f} (direkte {r['direkte']:.3f})  Φ 500 lx {r['Phi_500']:6.0f} lm  U0 EN 5×3 {r['U0_EN5x3']:.2f}  U0 7×5 (3 cm) {r['U0_7x5_3cm']:.2f}"
              f"  skjerm {r['E_skjerm']:4.0f} lx  stemning: {r['stem_Ev_per_LEDlm']:.3f} lx/LED-lm på veggfeltet, R {r['stem_R']:.3f}   rad-profil y {np.round(r['rader_y'], 2)}   ({time.time()-t1:.0f} s)", flush=True)
    # lambertsk modell, same mål (η frå motoren)
    eta = ETA[k]
    Een = E_lam(srcW, TASK_EN, UP)
    Lam = dict(eta=eta, Phi_500=D1[k]['Phi_fin'], U0_EN5x3=D1[k]['U0_EN5x3'], E_skjerm=D2[k]['fin']['E_snitt'])
    D5[f'{k}_lambert'] = Lam
    print(f"({k}) lambertsk opning (motoren): η {eta:.3f}  Φ 500 lx {Lam['Phi_500']:.0f} lm (arealsnitt)  U0 EN 5×3 {Lam['U0_EN5x3']:.2f}  skjerm {Lam['E_skjerm']:.0f} lx")
UT['mc'] = D5

# =====================================================================================
hdr('DEL 4 · Stemningsmålet. (a), (b) eigen kjelde; (c) eigen linjekjelde etter designlova i form04 (fjern- og nærfelt)')
# (c) prisme: tal henta frå form04 (FINAL, tal()) som data: ys 0,22, zs 0,70, L 0,60, bp 0,16, d 0,05, tp 0,003, η 0,7388, α arb 0, α stem −105°
C = dict(ys=0.22, zs=0.70, L=0.60, bp=0.16, d=0.05, tp=0.003, y1=0.02, y2=0.43, eta=0.7387707081611625, Phi=KONSEPT['c']['Phi_lm'], a_arb=0.0, a_stem=-105.0, sig=4.0)
C['th1'], C['th2'] = math.atan((C['ys'] - C['y2']) / C['zs']), math.atan((C['ys'] - C['y1']) / C['zs'])


def c_kjelde(a_deg, naer=True, ns=41, nx=48, ng=13):
    """Strålebuntar: (posisjon, sentervinkel th, vekt). th frå loddrett ned, + mot brukaren. Designlova: lambertsk inn, jamn E ut (tan θ lineær i kumulativ fluks)."""
    phm = math.atan(C['bp'] / 2 / C['d'])
    ph = ((np.arange(ns) + .5) / ns * 2 - 1) * phm
    w = np.cos(ph); w /= w.sum()
    Fs = (np.sin(ph) + math.sin(phm)) / (2 * math.sin(phm))
    th = np.arctan(math.tan(C['th1']) + Fs * (math.tan(C['th2']) - math.tan(C['th1'])))
    s = C['d'] * np.tan(ph)
    a = math.radians(a_deg)
    ned = np.array([0.0, -math.sin(a), -math.cos(a)]); fram = np.array([0.0, -math.cos(a), math.sin(a)])
    c0 = np.array([0.0, C['ys'], C['zs']])
    pos = c0 + ((C['d'] + C['tp']) * ned + s[:, None] * fram if naer else 0 * s[:, None])
    xs = (np.arange(nx) + .5) / nx * C['L'] - C['L'] / 2
    return dict(pos=pos, th=th + a, w=w, xs=xs)


def E_c(K, Q, qn, okk=(SKJERM,), bit=200):
    """lx per LED-lm. Intensitet per bunt: η·w·N(γ; th, σ)·(2/π)·cos ξ / nx."""
    sig = math.radians(C['sig'])
    out = np.zeros(len(Q))
    S = (K['pos'][:, None, :] + K['xs'][None, :, None] * np.array([1.0, 0, 0])).reshape(-1, 3)    # (ns·nx, 3)
    th = np.repeat(K['th'], len(K['xs'])); w = np.repeat(K['w'], len(K['xs'])) / len(K['xs'])
    for i in range(0, len(Q), bit):
        q = Q[i:i + bit]
        d = q[None] - S[:, None]
        r = np.linalg.norm(d, axis=-1)
        xi = np.arcsin(np.clip(d[..., 0] / r, -1, 1))
        g = np.arctan2(-d[..., 1], -d[..., 2])
        dg = (g - th[:, None] + np.pi) % (2 * np.pi) - np.pi
        I = C['eta'] * w[:, None] * np.exp(-0.5 * (dg / sig) ** 2) / (sig * math.sqrt(2 * math.pi)) * (2 / np.pi) * np.cos(xi)
        ci = -(d @ qn) / r
        val = np.where(ci > 0, I * ci / r ** 2, 0.0)
        for o in okk:
            val[o(S, q)] = 0.0
        out[i:i + bit] = val.sum(0)
    return out


# søyle og arm i (c) (form04/motor.py: COL_Y 0,512, COL_F 0,03, COL_W 0,10, arm underkant zs+0,03)
C_OKK = [okk_boks((-0.05, 0.512, 0.004), (0.05, 0.542, 0.76)), okk_boks((-0.05, C['ys'] - 0.012, 0.73), (0.05, 0.542, 0.76))]
D4 = {'c_arbeid': {}}
for naer in (False, True):
    K = c_kjelde(C['a_arb'], naer)
    Et, Een, Es = E_c(K, TASK_M, UP), E_c(K, TASK_EN, UP), E_c(K, SKJ_F[::2], MOT_BRUKAR, okk=())
    Ef = E_c(K, TASK_F[::5], UP)
    Phi = E_TASK / Et.mean()
    D4['c_arbeid']['naer' if naer else 'fjern'] = dict(Phi_7x5=Phi, U0_7x5=Et.min() / Et.mean(), U0_EN=Een.min() / Een.mean(), Phi_fin=E_TASK / Ef.mean(),
                                                         E_skjerm_ved_motorPhi=float(Es.mean() * C['Phi']), E_skjerm_maks_ved_motorPhi=float(Es.max() * C['Phi']),
                                                         E_skjerm_ved_egenPhi=float(Es.mean() * Phi))
    q = D4['c_arbeid']['naer' if naer else 'fjern']
    print(f"(c) arbeid, {'nærfelt (plata 16 cm, 5 cm under LED)' if naer else 'fjernfelt (som motoren)'}: Φ 500 lx {Phi:.0f} lm (fint {q['Phi_fin']:.0f})  U0 {q['U0_7x5']:.2f}/{q['U0_EN']:.2f}"
          f"  skjerm {q['E_skjerm_ved_motorPhi']:.1f} lx (maks {q['E_skjerm_maks_ved_motorPhi']:.0f}) ved Φ {C['Phi']:.0f}")

stem = {}
for k in 'ab':
    c = KONF[k]
    srcM = slot(c['yp'], c['hp'], PSI_STEM, c['xr'])
    A, eta = areal(srcM), ETA[k]
    P, N, dA = punkt(srcM)
    kL = eta / (math.pi * A)                                          # cd/m² per LED-lm
    stem[k] = dict(Ew_M=E_kv(P, N, dA, WALL_M, MOT_BRUKAR).mean() * kL, Ed_M=E_kv(P, N, dA, DESK_M, UP).mean() * kL,
                   Ew_F=E_kv(P, N, dA, WALL_F, MOT_BRUKAR) * kL, Ed_F=E_kv(P, N, dA, DESK_F, UP).mean() * kL, Phi_arb=KONSEPT[k]['Phi_lm'],
                   L_synleg_per_lm=0.0)
for lab, naer, okk in (('c_fjern', False, (SKJERM,)), ('c_naer', True, (SKJERM,)), ('c_naer_soyle', True, (SKJERM, *C_OKK))):
    K = c_kjelde(C['a_stem'], naer)
    stem[lab] = dict(Ew_M=E_c(K, WALL_M, MOT_BRUKAR, okk).mean(), Ed_M=E_c(K, DESK_M, UP, okk).mean(),
                     Ew_F=E_c(K, WALL_F, MOT_BRUKAR, okk), Ed_F=E_c(K, DESK_F, UP, okk).mean(), Phi_arb=C['Phi'])
L_MAAL = 10.0                                                         # cd/m² snitt på veggfeltet
E_MAAL = L_MAAL * math.pi / RHO_VEGG
D4['stemning'] = {}
for lab, s in stem.items():
    Ew, Ewf, Ed, Edf = s['Ew_M'], s['Ew_F'], s['Ed_M'], s['Ed_F']
    r = dict(Ev_per_LEDlm_8x6=Ew, Ev_per_LEDlm_fin=Ewf.mean(), R_8x6=Ew / (Ew + Ed), R_fin=Ewf.mean() / (Ewf.mean() + Edf),
             Ev_25pst_8x6=Ew * s['Phi_arb'] * DIM, Lv_25pst=RHO_VEGG * Ewf.mean() * s['Phi_arb'] * DIM / math.pi,
             lm_LED_for_10cd=E_MAAL / Ewf.mean(), W_for_10cd=E_MAAL / Ewf.mean() / 100, del_av_arbeid_for_10cd=E_MAAL / Ewf.mean() / s['Phi_arb'],
             Ev_ved_100lm=Ewf.mean() * 100, Lv_ved_100lm=RHO_VEGG * Ewf.mean() * 100 / math.pi,
             maks_snitt=Ewf.max() / Ewf.mean(), Lv_maks_for_10cd=RHO_VEGG * Ewf.max() * E_MAAL / Ewf.mean() / math.pi,
             del_felt_over_5cd_for_10cd=float((RHO_VEGG * Ewf * E_MAAL / Ewf.mean() / math.pi > 5).mean()),
             utnytting_veggfelt=Ewf.mean() * A_WF)
    D4['stemning'][lab] = r
    print(f"{lab:13s} Ē_vegg {Ew:.4f} lx/LED-lm (8×6) {Ewf.mean():.4f} (2 cm)  R {r['R_8x6']:.3f}/{r['R_fin']:.3f}  |  25 %-regel: {r['Ev_25pst_8x6']:5.1f} lx, L̄ {r['Lv_25pst']:4.1f} cd/m²"
          f"  |  L̄ 10 cd/m² krev {r['lm_LED_for_10cd']:4.0f} LED-lm = {r['W_for_10cd']:.2f} W = {100*r['del_av_arbeid_for_10cd']:.0f} % av arbeid, maks {r['Lv_maks_for_10cd']:.0f} cd/m², {100*r['del_felt_over_5cd_for_10cd']:.0f} % av feltet > 5 cd/m²"
          f"  |  100 LED-lm: {r['Ev_ved_100lm']:.0f} lx  |  {100*r['utnytting_veggfelt']:.0f} % av LED-lm på feltet")
UT['del4'] = D4

# =====================================================================================
hdr('DEL K · Kryssprøve mot felles.py og motorane (berre her importert)')
DK = {}
try:
    sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form01'))
    import felles as fe
    import motor as M1
    import importlib.util
    spec = importlib.util.spec_from_file_location('motor4', os.path.join(ROOT, 'form04', 'motor.py'))
    M4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(M4)
    Ba = dict(M1.FINAL, yp=0.18, hp=0.62, a=0.15)
    Bb = dict(M1.BASE, namn='krok', g=0.0, phir=0.0, yp=0.25, hp=0.62, L=0.64, k=0.94)

    def op_b(B, psi):
        P, N, dA = M1.opning(B, psi)
        m = np.abs(P[:, 0]) > 0.015
        return P[m], N[m], dA[m]
    DK['eta_motor'] = dict(a=M1.eta(Ba), b=M1.eta(Bb), mine=ETA)
    for k, op in (('a', lambda s: M1.opning(Ba, s)), ('b', lambda s: op_b(Bb, s))):
        P, N, dA = op(math.radians(PSI_ARB))
        src = slot(KONF[k]['yp'], KONF[k]['hp'], PSI_ARB, KONF[k]['xr'])
        DK[k] = dict(areal_motor=float(dA.sum()), areal_min=areal(src),
                     oppg_maks_avvik_pst=float(np.abs(fe.illum(P, N, dA, fe.TASK, UP) / E_lam(src, TASK_M, UP) - 1).max() * 100),
                     skjerm_avvik_pst=float(pst(fe.illum(P, N, dA, SKJ_F[::3], MOT_BRUKAR).mean(), E_lam(src, SKJ_F[::3], MOT_BRUKAR).mean())))
        # visible/reflected mot eigne for alle 8 auge (felles brukar 3 faste auge og loddrett skjerm)
        vis_m = bool(fe.visible(P, N)); refl_m = bool(fe.reflected(P, N))
        vis_e = any(sikt(src, e)[0] > 0 for e in fe.EYES); refl_e = any(spegling(src, e, 0.0)[0] > 0 for e in fe.EYES)
        DK[k].update(visible_motor=vis_m, visible_min=vis_e, reflected_motor=refl_m, reflected_min=refl_e)
        print(f"({k}) areal motor {dA.sum()*1e4:.2f} / mi {areal(src)*1e4:.2f} cm²  η motor {DK['eta_motor'][k]:.4f} / mi {ETA[k]:.4f}  illum mot Lambert maks {DK[k]['oppg_maks_avvik_pst']:.3f} %"
              f"  skjerm {DK[k]['skjerm_avvik_pst']:+.2f} %  visible {vis_m}/{vis_e}  reflected {refl_m}/{refl_e}")
    # reflected() i heile ψ-sveipet mot eigen spegel (tilt 0, dei tre auga i felles)
    ul = 0
    for psi in range(-180, 180, 5):
        P, N, dA = M1.opning(Ba, math.radians(psi))
        src = slot(0.18, 0.62, psi, [(-0.315, 0.315)])
        ul += bool(fe.reflected(P, N)) != any(spegling(src, e, 0.0, 0.01, 0.003)[0] > 0 for e in fe.EYES)
    DK['reflected_sveip_ulike'] = int(ul)
    print(f"(a) reflected() mot eigen spegel over 72 ψ-tilstandar: {ul} ulike")
    # (c): motoren sin E_punkt mot mi fjernfelt-linjekjelde
    B4 = dict(M4.FINAL)
    K = c_kjelde(0.0, naer=False)
    e_m = M4.E_punkt(B4, 0.0, fe.TASK, UP); e_e = E_c(K, fe.TASK, UP)
    w_m = M4.E_punkt(B4, math.radians(-105), fe.WALLG, MOT_BRUKAR).mean(); w_e = E_c(c_kjelde(-105.0, naer=False), fe.WALLG, MOT_BRUKAR).mean()
    s_m = M4.E_punkt(B4, 0.0, SKJ_F[::2], MOT_BRUKAR).mean() * C['Phi']
    DK['c'] = dict(oppg_snitt_motor=float(e_m.mean()), oppg_snitt_min=float(e_e.mean()), U0_motor=float(e_m.min() / e_m.mean()), U0_min=float(e_e.min() / e_e.mean()),
                   vegg_stem_motor=float(w_m), vegg_stem_min=float(w_e), skjerm_motor=float(s_m))
    print(f"(c) fjernfelt: oppgåve Ē {e_m.mean():.4f} motor / {e_e.mean():.4f} mi ({pst(e_e.mean(), e_m.mean()):+.1f} %)  U0 {e_m.min()/e_m.mean():.3f}/{e_e.min()/e_e.mean():.3f}"
          f"  vegg i stemning {w_m:.4f}/{w_e:.4f} lx/lm ({pst(w_e, w_m):+.1f} %)  skjerm (motor, mitt gitter) {s_m:.1f} lx")
except Exception as ex:
    import traceback; traceback.print_exc()
    DK['feil'] = repr(ex)
UT['kryss'] = DK


def rein(o):
    if isinstance(o, dict):
        return {str(k): rein(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [rein(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return rein(o.tolist())
    return o


json.dump(rein(UT), open(os.path.join(HER, 'fotometri_ab.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f'\nskrive: fotometri_ab.json  ({time.time()-T0:.0f} s)')
