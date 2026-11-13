# -*- coding: utf-8 -*-
"""Gransking · linse: fotometri. Uavhengig kontroll av lystala i konsept.json for (a) bru, (b) krok, (c) flak.

Eigen kode frå grunnformelen dE = L·cosθ_e·cosθ_r·dA/r². Ingen kall til felles.illum/lys/sok i kontrollrekninga.
Geometrien er bygd opp att frå parametrane (røyrakse, R, β, ψ; brettsenter, L, b, α), ikkje henta frå opning().
Tre uavhengige metodar:
  1. Lamberts polygonformel (eksakt for eit fritt, plant rektangel med jamn luminans)  -> oppgåvesona
  2. Eigen kvadratur med fin kjeldeinndeling og eigen skjermskugge                      -> vegg, bord, skjerm
  3. Monte Carlo strålekast frå kjelda (cosinusvekta)                                    -> energirekneskap
Til slutt (del K) ei kryssprøve mot motorane: der vert felles.py importert, berre for å samanlikne.

Køyr:  PYTHONIOENCODING=utf-8 python fotometri.py      -> skriv fotometri.json og tabellar til stdout
"""
import json
import math
import os
import sys

import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
rng = np.random.default_rng(20261113)
UT = {}

# ---------------- scene (skriven av frå felles.py l. 17–26, ikkje importert) ----------------
DX0, DX1, DY0, DY1 = -0.70, 0.70, 0.0, 0.75          # bord
WALL_Y = 0.75
SX0, SX1, SY, SZ0, SZ1 = -0.275, 0.275, 0.45, 0.10, 0.42   # skjerm
EYE0 = np.array([0.0, -0.30, 0.45])
TX0, TX1, TY0, TY1 = -0.30, 0.30, 0.05, 0.40          # oppgåvesone
WX0, WX1, WZ0, WZ1 = -0.70, 0.70, 0.05, 1.20          # veggfelt i stemningsmålet
RHO, E_TASK, DIM = 0.85, 500.0, 0.25
R_TUBE, BETA = 0.022, 25.0
UP, FRAM = np.array([0, 0, 1.0]), np.array([0, -1.0, 0])     # normal bord, normal vegg (inn i rommet)

KONSEPT = json.load(open(os.path.join(ROOT, 'konsept.json'), encoding='utf-8'))


# ---------------- kjelder: plane rektangel ----------------
def tube_ap(yp, hp, psi_deg, x0, x1):
    """Kordeflata i røyret: senter R·cosβ frå aksen i retning e(ψ), breidd 2R·sinβ, frå x0 til x1."""
    psi, be = math.radians(psi_deg), math.radians(BETA)
    e = np.array([0.0, -math.sin(psi), -math.cos(psi)])
    u = np.array([1.0, 0.0, 0.0])
    return dict(c=np.array([(x0 + x1) / 2, yp, hp]) + R_TUBE * math.cos(be) * e, u=u, hu=(x1 - x0) / 2,
                v=np.cross(u, e), hv=R_TUBE * math.sin(be), n=e)


def tray(yp, zp, alpha_deg, L=0.60, b=0.25):
    a = math.radians(alpha_deg)
    f = np.array([0.0, -math.cos(a), math.sin(a)])
    return dict(c=np.array([0.0, yp, zp]), u=np.array([1.0, 0.0, 0.0]), hu=L / 2, v=f, hv=b / 2,
                n=np.array([0.0, -math.sin(a), -math.cos(a)]))


def areal(rects):
    return sum(4 * r['hu'] * r['hv'] for r in rects)


def punkt(rects, du, dv):
    P, N, dA = [], [], []
    for r in rects:
        nu, nv = max(1, round(2 * r['hu'] / du)), max(1, round(2 * r['hv'] / dv))
        su = ((np.arange(nu) + .5) / nu * 2 - 1) * r['hu']
        sv = ((np.arange(nv) + .5) / nv * 2 - 1) * r['hv']
        U, V = np.meshgrid(su, sv, indexing='ij')
        p = r['c'] + U.ravel()[:, None] * r['u'] + V.ravel()[:, None] * r['v']
        P.append(p); N.append(np.tile(r['n'], (len(p), 1))); dA.append(np.full(len(p), 4 * r['hu'] * r['hv'] / (nu * nv)))
    return np.vstack(P), np.vstack(N), np.concatenate(dA)


# ---------------- eigen skjermskugge: strekning P->Q mot rektangelet y = SY ----------------
def skugge(P, Q):
    a = P[:, None, 1] - SY
    b = Q[None, :, 1] - SY
    kryss = a * b < 0                                       # endepunkta ligg på kvar si side av skjermplanet
    with np.errstate(divide='ignore', invalid='ignore'):
        s = np.where(kryss, a / (a - b), 0.0)
    X = P[:, None, 0] + s * (Q[None, :, 0] - P[:, None, 0])
    Z = P[:, None, 2] + s * (Q[None, :, 2] - P[:, None, 2])
    return kryss & (X > SX0) & (X < SX1) & (Z > SZ0) & (Z < SZ1)


# ---------------- metode 2: kvadratur ----------------
def E_kvad(P, N, dA, Q, nq, skjerm=True, bit=400):
    """lx per cd/m² på mottakarar Q med normal nq."""
    out = np.zeros(len(Q))
    for i in range(0, len(Q), bit):
        q = Q[i:i + bit]
        d = q[None] - P[:, None]
        r2 = np.einsum('ijk,ijk->ij', d, d)
        r = np.sqrt(r2)
        ce = np.einsum('ijk,ik->ij', d, N) / r
        cr = -(d @ nq) / r
        w = np.where((ce > 0) & (cr > 0), ce * cr / r2, 0.0)
        if skjerm:
            w[skugge(P, q)] = 0.0
        out[i:i + bit] = (w * dA[:, None]).sum(0)
    return out


# ---------------- metode 1: Lamberts polygonformel (eksakt, utan skugge) ----------------
def E_lambert(rects, Q, nq):
    E = np.zeros(len(Q))
    for r in rects:
        hj = [r['c'] + a * r['hu'] * r['u'] + b * r['hv'] * r['v'] for a, b in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
        assert all(((h[None] - Q) @ nq > 0).all() for h in hj), 'kjelda må liggje heilt over horisonten til mottakaren'
        Rv = [(h[None] - Q) / np.linalg.norm(h[None] - Q, axis=1, keepdims=True) for h in hj]
        tot = np.zeros(len(Q))
        for i in range(4):
            a, b = Rv[i], Rv[(i + 1) % 4]
            cr = np.cross(a, b)
            nrm = np.linalg.norm(cr, axis=1)
            tot += np.arctan2(nrm, (a * b).sum(1)) * (cr @ nq) / nrm
        E += np.where((Q - r['c']) @ r['n'] > 0, 0.5 * np.abs(tot), 0.0)
    return E


# ---------------- mottakargitter ----------------
def gitter_kant(x0, x1, nx, y0, y1, ny):
    """Som motoren: linspace med endepunkta (kant og hjørne tel fullt)."""
    X, Y = np.meshgrid(np.linspace(x0, x1, nx), np.linspace(y0, y1, ny))
    return X.ravel(), Y.ravel()


def gitter_celle(x0, x1, nx, y0, y1, ny):
    """Cellesentrert (arealrett snitt)."""
    X, Y = np.meshgrid(x0 + (np.arange(nx) + .5) / nx * (x1 - x0), y0 + (np.arange(ny) + .5) / ny * (y1 - y0))
    return X.ravel(), Y.ravel()


def bordpunkt(xy):
    return np.c_[xy[0], xy[1], np.zeros(len(xy[0]))]


def veggpunkt(xz):
    return np.c_[xz[0], np.full(len(xz[0]), WALL_Y - 1e-3), xz[1]]


TASK_M = bordpunkt(gitter_kant(TX0, TX1, 7, TY0, TY1, 5))                 # motorgitteret
TASK_F = bordpunkt(gitter_celle(TX0, TX1, 120, TY0, TY1, 70))             # 5 mm celler
HJORNE = bordpunkt((np.array([TX0, TX1, TX0, TX1]), np.array([TY0, TY0, TY1, TY1])))
WALL_M = veggpunkt(gitter_kant(WX0, WX1, 8, WZ0, WZ1, 6))
WALL_F = veggpunkt(gitter_celle(WX0, WX1, 70, WZ0, WZ1, 58))              # 2 cm celler
DESK_M = bordpunkt(gitter_kant(-0.68, 0.68, 8, 0.02, 0.73, 5))
DESK_F = bordpunkt(gitter_celle(DX0, DX1, 70, DY0, DY1, 38))


# ---------------- konsepta (parametrar frå form02/tal.json, form02/val.py l. 23, form03/motor.py l. 29) ----------------
# Motoren diskretiserer røyret i 32 segment. (a): 18 segment à 35 mm = 0,630 m (nominelt k·L = 0,600 m).
# (b): 30 segment à 20 mm minus 2 ved navet = 2 × 0,280 m.
def kjelde(k, modus, lengd='motor'):
    if k == 'a':
        h = 0.315 if lengd == 'motor' else 0.300
        return [tube_ap(0.18, 0.62, {'arbeid': -20, 'stemning': -95}[modus], -h, h)]
    if k == 'b':
        psi = {'arbeid': -20, 'stemning': -95}[modus]
        return [tube_ap(0.25, 0.62, psi, -0.30, -0.02), tube_ap(0.25, 0.62, psi, 0.02, 0.30)]
    return [tray(0.26, 0.64, {'arbeid': 0, 'stemning': -90, 'ansikt': 70}[modus])]


def eta_formel(A_ap, Lcav, direkte):
    f = A_ap / (2 * math.pi * R_TUBE * Lcav + 2 * math.pi * R_TUBE ** 2)
    return direkte + (1 - direkte) * RHO * f / (1 - RHO * (1 - f)), f


SB = math.sin(math.radians(BETA))
W_AP = 2 * R_TUBE * SB
ETA = {'a': eta_formel(0.630 * W_AP, 1.12 * 0.536, SB)[0],         # som motoren: A_ap frå 0,630 m, Lcav = k·L = 0,600 m
       'b': eta_formel(0.600 * W_AP, 0.64 * 0.94, SB)[0],          # som motoren: A_ap utan navfrådrag
       'c': 0.70}
FIN = {'a': (0.005, 0.003), 'b': (0.005, 0.003), 'c': (0.01, 0.01)}


def pst(x, ref):
    return 100 * (x / ref - 1)


# =====================================================================================
print('=' * 100)
print('DEL 1 · ARBEID: snitt, U0, Φ for 500 lx. Metode 1 (Lambert eksakt) og 2 (kvadratur) mot konsept.json')
print('=' * 100)
D1 = {}
for k in 'abc':
    src = kjelde(k, 'arbeid')
    A = areal(src)
    assert max((r['c'][1] + r['hv'] * abs(r['v'][1])) for r in src) < SY       # kjelda framfor skjermen -> ingen skugge på oppgåva
    E1 = E_lambert(src, TASK_M, UP)
    P, N, dA = punkt(src, *FIN[k])
    E2 = E_kvad(P, N, dA, TASK_M, UP)
    Ef = E_lambert(src, TASK_F, UP)
    Eh = E_lambert(src, HJORNE, UP)
    eta = ETA[k]
    Phi = lambda Em: E_TASK * math.pi * A / (eta * Em)
    r = dict(A_cm2=A * 1e4, eta=eta,
             Em_grid=E1.mean(), U0_grid=E1.min() / E1.mean(), Phi_grid=Phi(E1.mean()),
             Em_kvad=E2.mean(), Phi_kvad=Phi(E2.mean()), U0_kvad=E2.min() / E2.mean(),
             Em_areal=Ef.mean(), Emin_hjorne=Eh.min(), U0_areal=Eh.min() / Ef.mean(), Phi_areal=Phi(Ef.mean()),
             L_500=E_TASK / E1.mean(), L_500_areal=E_TASK / Ef.mean(),
             Phi_json=KONSEPT[k]['Phi_lm'], U0_json=KONSEPT[k]['U0'])
    r['avvik_Phi_pst'] = pst(r['Phi_grid'], r['Phi_json'])
    r['avvik_U0_pst'] = pst(r['U0_grid'], r['U0_json'])
    D1[k] = r
    print(f"({k}) A {A*1e4:7.1f} cm²  η {eta:.4f}")
    print(f"    motorgitter 7×5:  Lambert  Ē/L {E1.mean():.5f}  U0 {r['U0_grid']:.4f}  Φ {r['Phi_grid']:7.1f} lm   | kvadratur Φ {r['Phi_kvad']:7.1f}  U0 {r['U0_kvad']:.4f}")
    print(f"    konsept.json:     Φ {r['Phi_json']:7.1f} lm  U0 {r['U0_json']:.4f}   avvik Φ {r['avvik_Phi_pst']:+.2f} %  U0 {r['avvik_U0_pst']:+.2f} %")
    print(f"    arealrett (5 mm): Ē/L {Ef.mean():.5f}  Φ {r['Phi_areal']:7.1f} lm ({pst(r['Phi_areal'], r['Phi_json']):+.1f} %)  U0 = E_hjørne/Ē {r['U0_areal']:.4f}")
    print(f"    L i opninga ved 500 lx: {r['L_500']:8.0f} cd/m² (motorgitter)  {r['L_500_areal']:8.0f} (arealrett)")
# (a) med nominell opningslengd 0,600 m i staden for dei 0,630 m diskretiseringa gjev
src = kjelde('a', 'arbeid', 'nominell'); A = areal(src)
e_nom = eta_formel(0.600 * W_AP, 0.600, SB)[0]
E1 = E_lambert(src, TASK_M, UP)
D1['a_nominell_060'] = dict(A_cm2=A * 1e4, eta=e_nom, Phi=E_TASK * math.pi * A / (e_nom * E1.mean()), U0=E1.min() / E1.mean(), L_500=E_TASK / E1.mean())
print(f"(a) nominell opning 0,600 m (k·L): A {A*1e4:.1f} cm²  η {e_nom:.4f}  Φ {D1['a_nominell_060']['Phi']:.1f} lm  U0 {D1['a_nominell_060']['U0']:.4f}  L {D1['a_nominell_060']['L_500']:.0f} cd/m²")
UT['arbeid'] = D1

# =====================================================================================
print()
print('=' * 100)
print('DEL 1b · STEMNING (25 % av arbeidsfluksen): lux på veggen og veggdel')
print('=' * 100)
D1b = {}
for k in 'abc':
    src = kjelde(k, 'stemning'); A = areal(src); eta = ETA[k]
    P, N, dA = punkt(src, *FIN[k])
    PhiW = D1[k]['Phi_grid']
    Lst = eta * PhiW * DIM / (math.pi * A)                       # cd/m² i stemning
    Ew_m, Ed_m = E_kvad(P, N, dA, WALL_M, FRAM) * Lst, E_kvad(P, N, dA, DESK_M, UP) * Lst
    Ew_f, Ed_f = E_kvad(P, N, dA, WALL_F, FRAM) * Lst, E_kvad(P, N, dA, DESK_F, UP) * Lst
    Aw, Ad = (WX1 - WX0) * (WZ1 - WZ0), (DX1 - DX0) * (DY1 - DY0)
    ut = eta * PhiW * DIM
    r = dict(L_stem=Lst, Phi_ut=ut, Ev_grid=Ew_m.mean(), Ed_grid=Ed_m.mean(), R_grid=Ew_m.mean() / (Ew_m.mean() + Ed_m.mean()),
             Ev_areal=Ew_f.mean(), Ed_areal=Ed_f.mean(), R_areal=Ew_f.mean() / (Ew_f.mean() + Ed_f.mean()),
             Ev_maks=Ew_f.max(), Ev_min=Ew_f.min(), Ev_median=float(np.median(Ew_f)), del_under_10lx=float((Ew_f < 10).mean()),
             fluks_veggfelt=Ew_f.mean() * Aw, fluks_bord=Ed_f.mean() * Ad,
             Ev_json=KONSEPT[k]['Ev_stem'], R_json=KONSEPT[k]['R_stem'])
    r['fluksdel_veggfelt'] = r['fluks_veggfelt'] / ut
    r['fluksdel_bord'] = r['fluks_bord'] / ut
    r['avvik_Ev_pst'] = pst(r['Ev_grid'], r['Ev_json']); r['avvik_R_pst'] = pst(r['R_grid'], r['R_json'])
    D1b[k] = r
    print(f"({k}) L_stem {Lst:7.0f} cd/m²  ut av lampa {ut:6.1f} lm")
    print(f"    motorgitter:  Ē_vegg {r['Ev_grid']:6.2f} lx  veggdel {r['R_grid']:.4f}   | konsept.json {r['Ev_json']:6.2f} lx  {r['R_json']:.4f}   avvik {r['avvik_Ev_pst']:+.2f} % / {r['avvik_R_pst']:+.2f} %")
    print(f"    arealrett:    Ē_vegg {r['Ev_areal']:6.2f} lx ({pst(r['Ev_areal'], r['Ev_json']):+.1f} %)  veggdel {r['R_areal']:.4f}   maks {r['Ev_maks']:.0f}  median {r['Ev_median']:.0f}  min {r['Ev_min']:.1f} lx  ({100*r['del_under_10lx']:.0f} % av feltet under 10 lx)")
    print(f"    fluks: veggfelt {r['fluks_veggfelt']:6.1f} lm = {100*r['fluksdel_veggfelt']:.0f} % av utsendt   bord {r['fluks_bord']:5.1f} lm = {100*r['fluksdel_bord']:.0f} %")
UT['stemning'] = D1b


# =====================================================================================
def mc_fordeling(src, n=3_000_000):
    """Cosinusvekta strålar frå kjelda. Første treff: skjerm, bord, vegg (delt), rest. Returnerer fluksdelar (sum = 1)."""
    ar = np.array([4 * r['hu'] * r['hv'] for r in src])
    idx = rng.choice(len(src), n, p=ar / ar.sum())
    C = np.array([r['c'] for r in src])[idx]; U = np.array([r['u'] for r in src])[idx]; V = np.array([r['v'] for r in src])[idx]
    Nn = np.array([r['n'] for r in src])[idx]
    hu = np.array([r['hu'] for r in src])[idx]; hv = np.array([r['hv'] for r in src])[idx]
    p = C + ((2 * rng.random(n) - 1) * hu)[:, None] * U + ((2 * rng.random(n) - 1) * hv)[:, None] * V
    rr, ph = np.sqrt(rng.random(n)), 2 * math.pi * rng.random(n)
    d = (rr * np.cos(ph))[:, None] * U + (rr * np.sin(ph))[:, None] * V + np.sqrt(1 - rr ** 2)[:, None] * Nn
    inf = np.full(n, np.inf)
    with np.errstate(divide='ignore', invalid='ignore'):
        ts = np.where(np.abs(d[:, 1]) > 1e-12, (SY - p[:, 1]) / d[:, 1], inf)
        xs, zs = p[:, 0] + ts * d[:, 0], p[:, 2] + ts * d[:, 2]
        ts = np.where((ts > 1e-9) & (xs > SX0) & (xs < SX1) & (zs > SZ0) & (zs < SZ1), ts, inf)
        tb = np.where(d[:, 2] < -1e-12, -p[:, 2] / d[:, 2], inf)
        xb, yb = p[:, 0] + tb * d[:, 0], p[:, 1] + tb * d[:, 1]
        pa_bord = (xb > DX0) & (xb < DX1) & (yb > DY0) & (yb < DY1)
        tb_ok = np.where(pa_bord, tb, inf)
        tw = np.where(d[:, 1] > 1e-12, (WALL_Y - p[:, 1]) / d[:, 1], inf)
        xw, zw = p[:, 0] + tw * d[:, 0], p[:, 2] + tw * d[:, 2]
        tw = np.where(zw > 0, tw, inf)                       # under bordkanten finst ikkje veggen for oss
    T = np.stack([ts, tb_ok, tw])
    forst = T.argmin(0)
    ingen = ~np.isfinite(T.min(0))
    skjerm = (forst == 0) & ~ingen
    bord = (forst == 1) & ~ingen
    vegg = (forst == 2) & ~ingen
    oppg = bord & (xb > TX0) & (xb < TX1) & (yb > TY0) & (yb < TY1)
    felt = vegg & (xw > WX0) & (xw < WX1) & (zw > WZ0) & (zw < WZ1)
    over = vegg & (zw >= WZ1) & (zw < 1.65)                  # veggen over feltet, opp til tak 2,40 m over golv
    tak = vegg & (zw >= 1.65)
    side = vegg & ~felt & ~over & ~tak
    f = lambda m: float(m.mean())
    return dict(skjerm=f(skjerm), bord=f(bord), oppgave=f(oppg), veggfelt=f(felt), vegg_over=f(over), vegg_side=f(side),
                tak=f(tak), rom_golv_brukar=f(ingen), sum=f(skjerm) + f(bord) + f(felt) + f(over) + f(side) + f(tak) + f(ingen))


print()
print('=' * 100)
print('DEL 2 · ENERGIREKNESKAP. MC-strålekast (fluksdelar av utsendt = η·Φ) mot mottakarintegralet ∫E dA')
print('=' * 100)
D2 = {}
for k in 'abc':
    for modus in ('arbeid', 'stemning'):
        src = kjelde(k, modus); A = areal(src)
        m = mc_fordeling(src)
        P, N, dA = punkt(src, *FIN[k])
        ut_per_L = math.pi * A                                   # lm ut per cd/m²
        m['bord_integral'] = float(E_kvad(P, N, dA, DESK_F, UP).mean() * (DX1 - DX0) * (DY1 - DY0) / ut_per_L)
        m['veggfelt_integral'] = float(E_kvad(P, N, dA, WALL_F, FRAM).mean() * (WX1 - WX0) * (WZ1 - WZ0) / ut_per_L)
        m['oppgave_integral'] = float(E_lambert(src, TASK_F, UP).mean() * (TX1 - TX0) * (TY1 - TY0) / ut_per_L) if modus == 'arbeid' else None
        D2[f'{k}_{modus}'] = m
        print(f"({k}) {modus:8s}  bord {100*m['bord']:5.1f} % (integral {100*m['bord_integral']:5.1f})  av dette oppgåvesona {100*m['oppgave']:5.1f} %"
              f"  skjerm {100*m['skjerm']:5.1f} %  veggfelt {100*m['veggfelt']:5.1f} % (integral {100*m['veggfelt_integral']:5.1f})"
              f"  vegg over/side {100*(m['vegg_over']+m['vegg_side']):5.1f} %  tak {100*m['tak']:5.1f} %  rom/golv/brukar {100*m['rom_golv_brukar']:5.1f} %  sum {m['sum']:.4f}")
UT['energi'] = D2


# ---------------- η: hulromsformelen og eit MC-hulrom ----------------
def mc_hulrom(n=1_500_000, Lc=0.60, led='bakvegg', rho=RHO, maks=400):
    """Røyr R, lengd Lc, diffuse veggar og endeskiver (ρ), opning = bogen ±β langs heile lengda.
    LED-stripe lambertsk; 'bakvegg': på veggen rett overfor opninga; 'akse': på røyraksen (slik sin β føreset).
    Lokalt system: x langs røyret, a mot opninga, b på tvers. Returnerer η, direkte del og utgangsstrålane (pos, retning)."""
    be = math.radians(BETA)
    x = (rng.random(n) - .5) * Lc
    a = np.full(n, -R_TUBE if led == 'bakvegg' else 0.0); b = np.zeros(n)
    rr, ph = np.sqrt(rng.random(n)), 2 * math.pi * rng.random(n)
    dx, db, da = rr * np.cos(ph), rr * np.sin(ph), np.sqrt(1 - rr ** 2)
    live = np.ones(n, bool); ute = np.zeros(n, bool); sprett = np.zeros(n, int)
    for _ in range(maks):
        i = np.flatnonzero(live)
        if not len(i):
            break
        A_ = da[i] ** 2 + db[i] ** 2
        B_ = a[i] * da[i] + b[i] * db[i]
        C_ = a[i] ** 2 + b[i] ** 2 - R_TUBE ** 2
        with np.errstate(divide='ignore', invalid='ignore'):
            tc = np.where(A_ > 1e-14, (-B_ + np.sqrt(np.maximum(B_ ** 2 - A_ * C_, 0))) / A_, np.inf)
            te = np.where(dx[i] > 1e-12, (Lc / 2 - x[i]) / dx[i], np.where(dx[i] < -1e-12, (-Lc / 2 - x[i]) / dx[i], np.inf))
        lokk = te < tc
        t = np.minimum(tc, te)
        x[i] += t * dx[i]; a[i] += t * da[i]; b[i] += t * db[i]
        fi = np.arctan2(b[i], a[i])
        ut_no = ~lokk & (np.abs(fi) < be)
        ute[i[ut_no]] = True; live[i[ut_no]] = False
        j = i[~ut_no]; lk = lokk[~ut_no]
        dod = rng.random(len(j)) > rho
        live[j[dod]] = False
        j, lk = j[~dod], lk[~dod]
        sprett[j] += 1
        # diffus refleksjon om innovernormalen
        nx = np.where(lk, -np.sign(x[j]), 0.0)
        na = np.where(lk, 0.0, -a[j] / R_TUBE); nb = np.where(lk, 0.0, -b[j] / R_TUBE)
        # tangentbasis
        t1x, t1a, t1b = np.where(lk, 0.0, 1.0), np.where(lk, 1.0, 0.0), np.zeros(len(j))
        t2x = na * t1b - nb * t1a; t2a = nb * t1x - nx * t1b; t2b = nx * t1a - na * t1x
        rr, ph = np.sqrt(rng.random(len(j))), 2 * math.pi * rng.random(len(j))
        l1, l2, l3 = rr * np.cos(ph), rr * np.sin(ph), np.sqrt(1 - rr ** 2)
        dx[j] = l1 * t1x + l2 * t2x + l3 * nx; da[j] = l1 * t1a + l2 * t2a + l3 * na; db[j] = l1 * t1b + l2 * t2b + l3 * nb
        if led == 'akse' and _ == 0:
            pass
    eta = ute.mean()
    direkte = (ute & (sprett == 0)).mean()
    return dict(eta=float(eta), direkte=float(direkte), x=x[ute], a=a[ute], b=b[ute], dx=dx[ute], da=da[ute], db=db[ute])


print()
print('=' * 100)
print('DEL 2b · η for røyret')
print('=' * 100)
D2b = {}
eta_a, f_a = eta_formel(0.630 * W_AP, 0.6003, SB)
print(f"formelen i form01/motor.py l. 62–67, rekna for hand: f = {f_a:.4f}, fleirsprett ρf/(1-ρ(1-f)) = {RHO*f_a/(1-RHO*(1-f_a)):.4f}, direkte sin β = {SB:.4f}  ->  η = {eta_a:.4f}  (tal.json: 0,6741)")
D2b['formel'] = dict(f=f_a, direkte_sin_beta=SB, eta=eta_a)
SB2 = math.sin(math.radians(BETA / 2))
D2b['formel_bakvegg'] = dict(direkte=SB2, eta=eta_formel(0.630 * W_AP, 0.6003, SB2)[0])
print(f"LED på bakveggen (einaste staden røyret kan kjøle): opninga spenner ±β/2 = ±12,5° (periferivinkel) -> direkte sin(β/2) = {SB2:.4f} -> η = {D2b['formel_bakvegg']['eta']:.4f}")
for led in ('akse', 'bakvegg'):
    h = mc_hulrom(led=led)
    cosn = h['da']                                                  # cos til vinkelen mot opningsnormalen
    D2b[f'mc_{led}'] = dict(eta=h['eta'], direkte=h['direkte'], del_innan_25grader=float((cosn > math.cos(math.radians(25))).mean()),
                           del_innan_45grader=float((cosn > math.cos(math.radians(45))).mean()), lambert_25=math.sin(math.radians(25)) ** 2, lambert_45=0.5)
    print(f"MC-hulrom, LED på {led:8s}: η = {h['eta']:.4f}  direkte del = {h['direkte']:.4f}   fluks innan 25° frå normalen {100*D2b[f'mc_{led}']['del_innan_25grader']:.0f} % (lambert: 18 %)  innan 45°: {100*D2b[f'mc_{led}']['del_innan_45grader']:.0f} % (lambert: 50 %)")
    if led == 'bakvegg':
        H = h
# Oppgåvelux rett frå MC-hulrommet (LED på bakveggen), (a) i arbeid: ikkje-lambertsk fordeling
r0 = kjelde('a', 'arbeid', 'nominell')[0]
e, u, v = r0['n'], r0['u'], r0['v']
akse = np.array([0.0, 0.18, 0.62])
p = akse + H['x'][:, None] * u + H['a'][:, None] * e + H['b'][:, None] * v
d = H['dx'][:, None] * u + H['da'][:, None] * e + H['db'][:, None] * v
n_led = round(len(H['x']) / H['eta'])
ned = d[:, 2] < -1e-9
t = -p[ned, 2] / d[ned, 2]
xb, yb = p[ned, 0] + t * d[ned, 0], p[ned, 1] + t * d[ned, 1]
inn = (xb > TX0) & (xb < TX1) & (yb > TY0) & (yb < TY1)
Hh, _, _ = np.histogram2d(xb[inn], yb[inn], bins=[7, 5], range=[[TX0, TX1], [TY0, TY1]])
celle = (TX1 - TX0) / 7 * (TY1 - TY0) / 5
E_per_lm = Hh / n_led / celle
Phi_mc = E_TASK / E_per_lm.mean()
# same binning for lambertmodellen: cellesnitt i 7×5 celler
src = kjelde('a', 'arbeid', 'nominell')
Ec = E_lambert(src, TASK_F, UP).reshape(70, 120)                    # (ny, nx)
Ec = Ec.reshape(5, 14, 7, 120 // 7 if 120 % 7 == 0 else 1, -1).mean((1, 3, 4)) if 120 % 7 == 0 else None
Xc, Yc = gitter_celle(TX0, TX1, 7 * 20, TY0, TY1, 5 * 14)
Ecell = E_lambert(src, bordpunkt((Xc, Yc)), UP).reshape(5, 14, 7, 20).mean((1, 3))      # (5,7) cellesnitt
D2b['mc_oppgave_a'] = dict(eta_mc=H['eta'], Phi_500_mc=float(Phi_mc), U0_celle_mc=float(E_per_lm.min() / E_per_lm.mean()),
                           U0_celle_lambert=float(Ecell.min() / Ecell.mean()),
                           Phi_500_lambert_same_eta=float(E_TASK * math.pi * areal(src) / (H['eta'] * Ecell.mean())),
                           del_paa_oppgave_mc=float(inn.sum() / len(H['x'])),
                           del_paa_oppgave_lambert=float(Ecell.mean() * 0.21 / (math.pi * areal(src))))
m = D2b['mc_oppgave_a']
print(f"(a) arbeid, strålar rett frå MC-hulrommet (LED bakvegg, η {m['eta_mc']:.3f}): {100*m['del_paa_oppgave_mc']:.1f} % av utgangsfluksen treffer oppgåvesona "
      f"(lambert: {100*m['del_paa_oppgave_lambert']:.1f} %)  ->  Φ for 500 lx = {m['Phi_500_mc']:.0f} lm, U0 (cellesnitt 7×5) {m['U0_celle_mc']:.2f} (lambert {m['U0_celle_lambert']:.2f})")
print()
print('Φ og effekt om η er ein annan (Φ ∝ 1/η; luminansen i opninga er uendra, han er rein geometri):')
D2b['folsemd'] = {}
for k in 'abc':
    rad = {}
    for e_ in (0.5, ETA[k], 0.8) + ((D2b['formel_bakvegg']['eta'], D2b['mc_bakvegg']['eta']) if k != 'c' else ()):
        Phi = D1[k]['Phi_grid'] * ETA[k] / e_
        rad[f'{e_:.3f}'] = dict(Phi=Phi, W=Phi / 100, A_krav_cm2=Phi / 100 / 300 * 1e4, A_har_cm2=KONSEPT[k]['A_kjol_cm2'])
    D2b['folsemd'][k] = rad
    print(f"({k}) " + '   '.join(f"η {e_}: {q['Phi']:.0f} lm, {q['W']:.1f} W, kjølekrav {q['A_krav_cm2']:.0f}/{q['A_har_cm2']:.0f} cm²" for e_, q in rad.items()))
UT['eta'] = D2b

# =====================================================================================
print()
print('=' * 100)
print('DEL 3 · SYNLEGHEIT. Eigne siktliner frå auga til opningsflata')
print('=' * 100)
AUGE = {'nominell': (0, -0.30, 0.45), 'nominell x+15': (0.15, -0.30, 0.45), 'lener 15 cm fram': (0, -0.15, 0.45),
        '5 cm lågare': (0, -0.30, 0.40), '5 cm høgare': (0, -0.30, 0.50), 'fram 15 + lågare 5': (0, -0.15, 0.40),
        'fram 15 + høgare 5': (0, -0.15, 0.50)}


def sikt(src, eye, du=0.01, dv=0.002):
    """Del av opninga auga ser (framfor flata og ikkje bak skjermen) + vinkel mellom siktlina og opningsplanet (+ = framfor)."""
    P, N, dA = punkt(src, du, dv)
    E = np.asarray(eye, float)
    d = E[None] - P
    s = (d * N).sum(1)
    vin = np.degrees(np.arcsin(s / np.linalg.norm(d, axis=1)))
    fri = (s > 0) & ~skugge(P, E[None])[:, 0]
    omega = float((np.where(fri, s / np.linalg.norm(d, axis=1), 0) * dA / (d ** 2).sum(1)).sum())
    return float((fri * dA).sum() / dA.sum()), float(vin.min()), float(vin.max()), omega


D3 = {}
for k in 'ab':
    src = kjelde(k, 'arbeid')
    L = D1[k]['L_500']
    D3[k] = {}
    print(f"({k}) arbeid ψ −20°, L i opninga {L:.0f} cd/m²")
    for nm, eye in AUGE.items():
        fr, v0, v1, om = sikt(src, eye)
        D3[k][nm] = dict(synleg_del=fr, vinkel_min=v0, vinkel_maks=v1, omega_sr=om, L_synleg=L if fr > 0 else 0.0)
        print(f"    {nm:20s} auge {eye}:  synleg del {100*fr:5.1f} %   siktline mot opningsplanet {v0:+5.1f}…{v1:+5.1f}°   {'SYNLEG, ' + format(L, '.0f') + ' cd/m²' if fr > 0 else 'skjerma'}")
    r = src[0]
    # grenseplanet: n·(E − c) = 0  ->  z_krit(y) = c_z + n_y/(-n_z)·(y − c_y)
    zk = lambda y: r['c'][2] + r['n'][1] / (-r['n'][2]) * (y - r['c'][1])
    yk = r['c'][1] + (0.45 - r['c'][2]) * (-r['n'][2]) / r['n'][1]
    D3[k]['grense'] = dict(z_krit_ved_y_m030=zk(-0.30), margin_hogd_cm=(0.45 - zk(-0.30)) * 100, y_krit_ved_z_045=yk, margin_fram_cm=(yk + 0.30) * 100,
                           elev_royr_fraa_auge=math.degrees(math.atan2(r['c'][2] - 0.45, r['c'][1] + 0.30)), avskjering=20.0)
    g = D3[k]['grense']
    print(f"    grense: auga ser opninga når z_auge < {g['z_krit_ved_y_m030']:.3f} m (margin {g['margin_hogd_cm']:.1f} cm) eller y_auge > {g['y_krit_ved_z_045']:.3f} m (margin {g['margin_fram_cm']:.1f} cm fram)."
          f"  Røyret ligg {g['elev_royr_fraa_auge']:.1f}° over augehøgd, avskjeringa er 20°.")
# kva kostar meir skjerming? Φ(ψ) for (a) og (b)
print('    pris for meir skjerming (Φ ved 500 lx, U0, margin i høgd for nominelt auge):')
D3['psi_sveip'] = {}
for k in 'ab':
    for psi in (-15, -20, -25, -30, -35, -40):
        if k == 'a':
            src = [tube_ap(0.18, 0.62, psi, -0.315, 0.315)]
        else:
            src = [tube_ap(0.25, 0.62, psi, -0.30, -0.02), tube_ap(0.25, 0.62, psi, 0.02, 0.30)]
        E1 = E_lambert(src, TASK_M, UP)
        Phi = E_TASK * math.pi * areal(src) / (ETA[k] * E1.mean())
        r = src[0]
        zk = r['c'][2] + r['n'][1] / (-r['n'][2]) * (-0.30 - r['c'][1])
        yk = r['c'][1] + (0.45 - r['c'][2]) * (-r['n'][2]) / r['n'][1]
        D3['psi_sveip'][f'{k}_{psi}'] = dict(Phi=Phi, U0=E1.min() / E1.mean(), margin_hogd_cm=(0.45 - zk) * 100, margin_fram_cm=(yk + 0.30) * 100)
        print(f"      ({k}) ψ {psi:+4d}°: Φ {Phi:6.0f} lm ({pst(Phi, D1[k]['Phi_grid']):+5.1f} %)  U0 {E1.min()/E1.mean():.2f}   margin {(0.45-zk)*100:+5.1f} cm i høgd, {(yk+0.30)*100:+5.1f} cm fram")

# (c): synleg flate, med og utan leppe (returfald 20 mm på lyssida)
print('(c) arbeid α 0°: flata er synleg')
src = kjelde('c', 'arbeid'); r = src[0]
Lsn = D1['c']['L_500']
D3['c'] = dict(L_snitt=Lsn, L_topp_13=1.3 * Lsn, L_json=KONSEPT['c']['L_synleg'], L_snitt_areal=D1['c']['L_500_areal'], L_topp_areal=1.3 * D1['c']['L_500_areal'])
print(f"    L snitt = 500/(Ē/L) = {Lsn:.0f} cd/m²,  × toppfaktor 1,3 = {1.3*Lsn:.0f}   (konsept.json L_synleg {KONSEPT['c']['L_synleg']:.0f}; avvik {pst(1.3*Lsn, KONSEPT['c']['L_synleg']):+.2f} %)")
print(f"    kontroll via fluks: η·Φ/(π·A) = 0,70·{D1['c']['Phi_grid']:.0f}/(π·0,15) = {0.70*D1['c']['Phi_grid']/(math.pi*0.15):.0f} cd/m²")
print(f"    arealrett snitt på oppgåva gjev L snitt {D1['c']['L_500_areal']:.0f}, topp {1.3*D1['c']['L_500_areal']:.0f} cd/m²")
P, N, dA = punkt(src, 0.005, 0.005)
for nm, eye in AUGE.items():
    E = np.asarray(eye, float)
    d = E[None] - P
    dist = np.linalg.norm(d, axis=1)
    cs = (d * N).sum(1) / dist
    # framleppa: plan y = fremre kant, 20 mm ned frå flata
    yk_ = r['c'][1] - r['hv']
    tt = (yk_ - P[:, 1]) / d[:, 1]
    zl = P[:, 2] + tt * d[:, 2]
    bak_leppe = (tt > 0) & (tt < 1) & (zl > r['c'][2] - 0.020)
    fri = (cs > 0) & ~bak_leppe
    om = float((np.where(fri, cs, 0) * dA / dist ** 2).sum())
    om0 = float((np.where(cs > 0, cs, 0) * dA / dist ** 2).sum())
    elev = np.degrees(np.arctan2(P[:, 2] - E[2], P[:, 1] - E[1]))
    D3['c'][nm] = dict(synleg_del_med_leppe=float(fri.mean()), omega_sr=om, omega_utan_leppe=om0, elev_min=float(elev.min()), elev_maks=float(elev.max()),
                       vinkel_fra_normal=float(np.degrees(np.arccos(cs.mean()))))
    print(f"    {nm:20s}: synleg {100*fri.mean():4.0f} % av flata (leppa løyner resten)  ω = {om:.3f} sr  flata ligg {elev.min():.0f}–{elev.max():.0f}° over augehøgd, sett {np.degrees(np.arccos(cs.mean())):.0f}° frå normalen")


# UGR-overslag for (c) (CIE 117; Guth posisjonsindeks). Utanfor gyldigheita (ω > 0,1 sr), difor berre overslag.
def guth(beta_deg, alpha_deg=0.0):
    return math.exp((35.2 - 0.31889 * alpha_deg - 1.22 * math.exp(-2 * alpha_deg / 9)) * 1e-3 * beta_deg
                    + (21 + 0.26667 * alpha_deg - 0.002963 * alpha_deg ** 2) * 1e-5 * beta_deg ** 2)


om = D3['c']['nominell']['omega_sr']
elev_mid = math.degrees(math.atan2(0.64 - 0.45, 0.26 + 0.30))
D3['c']['ugr'] = {}
for sikt_nm, ned in (('blikk mot skjermsenter', math.degrees(math.atan2(0.45 - 0.26, 0.75))), ('blikk mot skjermtopp', math.degrees(math.atan2(0.45 - 0.42, 0.75)))):
    be_ = elev_mid + ned
    p_ = guth(be_)
    for Lb in (10, 20, 40):
        ugr = 8 * math.log10(0.25 / Lb * Lsn ** 2 * om / p_ ** 2)
        D3['c']['ugr'][f'{sikt_nm}, Lb {Lb}'] = dict(beta=be_, p=p_, UGR=ugr)
    print(f"    UGR-overslag, {sikt_nm} (flata {be_:.0f}° over blikket, p = {p_:.2f}): " + ', '.join(f"Lb {Lb}: {D3['c']['ugr'][f'{sikt_nm}, Lb {Lb}']['UGR']:.1f}" for Lb in (10, 20, 40)) + '   (grense kontorarbeid: 19)')
UT['synlegheit'] = D3

# =====================================================================================
print()
print('=' * 100)
print('DEL 4 · GITTERFØLSEMD')
print('=' * 100)
D4 = {'oppgave': {}, 'stemning': {}}
for k in 'abc':
    src = kjelde(k, 'arbeid'); A = areal(src)
    print(f"({k}) oppgåvesona 0,60 × 0,35 m")
    for nm, g in (('7×5 kant (motor)', gitter_kant(TX0, TX1, 7, TY0, TY1, 5)), ('13×9 kant', gitter_kant(TX0, TX1, 13, TY0, TY1, 9)),
                  ('25×15 kant', gitter_kant(TX0, TX1, 25, TY0, TY1, 15)), ('61×36 kant', gitter_kant(TX0, TX1, 61, TY0, TY1, 36)),
                  ('7×5 celle', gitter_celle(TX0, TX1, 7, TY0, TY1, 5)), ('5×3 celle (EN 12464-1 p ≤ 0,14 m)', gitter_celle(TX0, TX1, 5, TY0, TY1, 3)),
                  ('120×70 celle', gitter_celle(TX0, TX1, 120, TY0, TY1, 70))):
        E = E_lambert(src, bordpunkt(g), UP)
        Phi = E_TASK * math.pi * A / (ETA[k] * E.mean())
        D4['oppgave'][f'{k} {nm}'] = dict(Em_per_L=float(E.mean()), U0=float(E.min() / E.mean()), Phi=float(Phi))
        print(f"    {nm:36s} Ē/L {E.mean():.5f}  U0 {E.min()/E.mean():.3f}  Φ {Phi:7.1f} lm ({pst(Phi, D1[k]['Phi_grid']):+5.1f} %)")
    src = kjelde(k, 'stemning'); P, N, dA = punkt(src, *FIN[k])
    Lst = D1b[k]['L_stem']
    print(f"({k}) stemning: veggfelt og bord")
    for nm, gw, gd in (('8×6 / 8×5 kant (motor)', gitter_kant(WX0, WX1, 8, WZ0, WZ1, 6), gitter_kant(-0.68, 0.68, 8, 0.02, 0.73, 5)),
                       ('15×11 / 15×9 kant', gitter_kant(WX0, WX1, 15, WZ0, WZ1, 11), gitter_kant(-0.68, 0.68, 15, 0.02, 0.73, 9)),
                       ('29×24 / 29×16 kant', gitter_kant(WX0, WX1, 29, WZ0, WZ1, 24), gitter_kant(-0.68, 0.68, 29, 0.02, 0.73, 16)),
                       ('8×6 / 8×5 celle', gitter_celle(WX0, WX1, 8, WZ0, WZ1, 6), gitter_celle(DX0, DX1, 8, DY0, DY1, 5)),
                       ('70×58 / 70×38 celle', gitter_celle(WX0, WX1, 70, WZ0, WZ1, 58), gitter_celle(DX0, DX1, 70, DY0, DY1, 38))):
        Ew = E_kvad(P, N, dA, veggpunkt(gw), FRAM).mean() * Lst
        Ed = E_kvad(P, N, dA, bordpunkt(gd), UP).mean() * Lst
        D4['stemning'][f'{k} {nm}'] = dict(Ev=float(Ew), Ed=float(Ed), R=float(Ew / (Ew + Ed)))
        print(f"    {nm:28s} Ē_vegg {Ew:6.2f} lx ({pst(Ew, D1b[k]['Ev_grid']):+5.1f} %)  Ē_bord {Ed:5.2f} lx  veggdel {Ew/(Ew+Ed):.3f}")
    # veggfeltet er vilkårleg: same lampe, anna felt
    for nm, (x0, x1, z0, z1) in (('felt 1,4 × 2,4 m (heile veggen over bordet til tak 1,65)', (WX0, WX1, 0.0, 1.65)), ('felt 0,8 × 0,6 m rundt lampa', (-0.4, 0.4, 0.3, 0.9))):
        Ew = E_kvad(P, N, dA, veggpunkt(gitter_celle(x0, x1, 60, z0, z1, 60)), FRAM).mean() * Lst
        Ed = D1b[k]['Ed_areal']
        D4['stemning'][f'{k} {nm}'] = dict(Ev=float(Ew), R=float(Ew / (Ew + Ed)))
        print(f"    {nm:58s} Ē_vegg {Ew:6.2f} lx  veggdel {Ew/(Ew+Ed):.3f}")
UT['gitter'] = D4

# =====================================================================================
print()
print('=' * 100)
print('DEL 5 · NORMALAR, SKJERMSKUGGE, SPEGLING, LYS PÅ SKJERMEN')
print('=' * 100)
D5 = {}
# 5a forteikn: handrekning i eitt punkt, (a) arbeid, punktkjelde-tilnærming midt i opninga mot oppgåvesenter
r = kjelde('a', 'arbeid')[0]
q = np.array([0.0, 0.225, 0.0])
dv_ = q - r['c']; rr_ = np.linalg.norm(dv_)
ce, cr = dv_ @ r['n'] / rr_, -dv_ @ UP / rr_
E_pkt = ce * cr * areal([r]) / rr_ ** 2
E_eks = E_lambert([r], q[None], UP)[0]
D5['forteikn'] = dict(n=r['n'].tolist(), cos_e=ce, cos_r=cr, r=rr_, E_punkt_per_L=E_pkt, E_eksakt_per_L=E_eks)
print(f"5a (a) arbeid: n = {np.round(r['n'], 3)} (ned og mot veggen), cosθ_e {ce:.3f}, cosθ_r {cr:.3f}, r {rr_:.3f} m  ->  punktkjelde {E_pkt:.5f}, eksakt {E_eks:.5f} lx per cd/m²  (begge > 0: forteikna er rette)")
for k, modus in (('a', 'stemning'), ('c', 'stemning'), ('c', 'ansikt')):
    rr0 = kjelde(k, modus)[0]
    print(f"   ({k}) {modus}: n = {np.round(rr0['n'], 3)}")

# 5b skjermskugge: ein analytisk prøve. Punktkjelde 20 cm bak skjermen i skjermhøgd skal ikkje lyse på oppgåva.
Pb = np.array([[0.0, 0.65, 0.30]]); Nb = np.array([[0.0, -1.0, 0.0]]); dAb = np.array([1e-4])
Eb = E_kvad(Pb, Nb, dAb, TASK_M, UP)
Eb0 = E_kvad(Pb, Nb, dAb, TASK_M, UP, skjerm=False)
D5['skugge_prove'] = dict(skugga_punkt=int((Eb == 0).sum()), av=len(Eb), utan_skjerm_min=float(Eb0.min()))
print(f"5b punktkjelde bak skjermen (y 0,65, z 0,30): {int((Eb == 0).sum())} av {len(Eb)} oppgåvepunkt i skugge (utan skjerm: alle > 0)")
# stemning: kor mykje tek skjermen?
for k in 'abc':
    src = kjelde(k, 'stemning'); P, N, dA = punkt(src, *FIN[k]); Lst = D1b[k]['L_stem']
    med = E_kvad(P, N, dA, WALL_F, FRAM).mean() * Lst
    utan = E_kvad(P, N, dA, WALL_F, FRAM, skjerm=False).mean() * Lst
    D5[f'skugge_stemning_{k}'] = dict(Ev_med=float(med), Ev_utan=float(utan))
    print(f"   ({k}) stemning: Ē_vegg {med:.1f} lx med skjermskugge, {utan:.1f} utan ({pst(med, utan):+.1f} %)")


# 5c spegling: eigen spegel, med tilt. Skjermen roterer om underkanten, toppen bakover (τ > 0).
def spegling(src, eye, tilt_deg, du=0.01, dv=0.003):
    P, N, dA = punkt(src, du, dv)
    t = math.radians(tilt_deg)
    o = np.array([0.0, SY, SZ0])                                    # underkant
    opp = np.array([0.0, math.sin(t), math.cos(t)])                 # langs skjermen oppover
    nm = np.array([0.0, -math.cos(t), math.sin(t)])                 # skjermnormal mot brukaren
    E = np.asarray(eye, float)
    Em = E - 2 * ((E - o) @ nm) * nm                                # spegla auge
    d = P - Em
    den = d @ nm
    with np.errstate(divide='ignore', invalid='ignore'):
        s = ((o - Em) @ nm) / den
    Qp = Em + s[:, None] * d
    h = (Qp - o) @ opp
    framfor = ((P - o) @ nm) > 0
    ok = framfor & (s > 0) & (s < 1) & (Qp[:, 0] > SX0) & (Qp[:, 0] < SX1) & (h > 0) & (h < SZ1 - SZ0) & (((Qp - P) * N).sum(1) > 0)
    return float((ok * dA).sum() / dA.sum())


D5['spegling'] = {}
for k in 'abc':
    src = kjelde(k, 'arbeid')
    L = D1[k]['L_500'] * (1.3 if k == 'c' else 1)
    rad = {}
    for tilt in (0, 5, 10, 15, 20, 25):
        rad[tilt] = max(spegling(src, e, tilt) for e in ((0, -0.30, 0.45), (0.15, -0.30, 0.45), (-0.15, -0.30, 0.45)))
    forst = next((tt for tt in np.arange(0, 40.01, 0.5) if spegling(src, (0, -0.30, 0.45), tt) > 0), None)
    forst_h = next((tt for tt in np.arange(0, 40.01, 0.5) if spegling(src, (0, -0.30, 0.50), tt) > 0), None)
    forst_f = next((tt for tt in np.arange(0, 40.01, 0.5) if spegling(src, (0, -0.15, 0.45), tt) > 0), None)
    D5['spegling'][k] = dict(del_spegla_per_tilt=rad, forste_tilt=forst, forste_tilt_auge_5cm_hogare=forst_h, forste_tilt_15cm_fram=forst_f, L=L)
    print(f"5c ({k}) arbeid: spegla del av opninga ved tilt " + ', '.join(f"{tt}°: {100*v_:.0f} %" for tt, v_ in rad.items())
          + f"   første spegling ved tilt {forst}° (auge 5 cm høgare: {forst_h}°, 15 cm fram: {forst_f}°)  L = {L:.0f} cd/m²")

# 5d lys på sjølve skjermflata (ikkje i modellen)
SKJ = np.c_[gitter_celle(SX0, SX1, 28, SZ0, SZ1, 16)[0], np.full(28 * 16, SY - 1e-4), gitter_celle(SX0, SX1, 28, SZ0, SZ1, 16)[1]]
D5['lys_paa_skjerm'] = {}
for k in 'abc':
    for modus in ('arbeid', 'stemning'):
        src = kjelde(k, modus); P, N, dA = punkt(src, *FIN[k])
        L = D1[k]['L_500'] if modus == 'arbeid' else D1b[k]['L_stem']
        Es = E_kvad(P, N, dA, SKJ, FRAM, skjerm=False) * L
        D5['lys_paa_skjerm'][f'{k}_{modus}'] = dict(snitt=float(Es.mean()), maks=float(Es.max()), min=float(Es.min()), slor_cd_m2_rho5=float(0.05 * Es.mean() / math.pi))
        print(f"5d ({k}) {modus:8s}: E på skjermflata snitt {Es.mean():5.0f} lx (maks {Es.max():.0f}, min {Es.min():.0f})  ->  slør {0.05*Es.mean()/math.pi:.1f} cd/m² ved diffus ρ 0,05")
UT['del5'] = D5

# =====================================================================================
print()
print('=' * 100)
print('DEL K · KRYSSPRØVE MOT MOTORANE (her, og berre her, vert felles.py og motorane importerte)')
print('=' * 100)
DK = {}
try:
    import importlib.util
    sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form01'))
    import felles as fe
    import motor as M1
    spec = importlib.util.spec_from_file_location('motor3', os.path.join(ROOT, 'form03', 'motor.py'))
    M3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(M3)
    Ba = dict(M1.FINAL, yp=0.18, hp=0.62, a=0.15)
    Bb = dict(M1.BASE, namn='krok', g=0.0, phir=0.0, yp=0.25, hp=0.62, L=0.64, k=0.94)
    Bc = dict(M3.FINAL)

    def op_b(B, psi):
        P, N, dA = M1.opning(B, psi)
        m = np.abs(P[:, 0]) > 0.015
        return P[m], N[m], dA[m]
    for k, op, st in (('a', lambda s: M1.opning(Ba, s), (-20, -95)), ('b', lambda s: op_b(Bb, s), (-20, -95)), ('c', lambda s: M3.opning(Bc, s), (0, -90))):
        for modus, s in zip(('arbeid', 'stemning'), st):
            P, N, dA = op(math.radians(s))
            src = kjelde(k, modus)
            Pm, Nm, dAm = punkt(src, 0.01, 0.003)
            # geometri: areal, tyngdepunkt, normal, utstrekking
            dgeo = dict(dA=float(dA.sum() - areal(src)), senter=float(np.abs((P * dA[:, None]).sum(0) / dA.sum() - (Pm * dAm[:, None]).sum(0) / dAm.sum()).max()),
                        normal=float(np.abs(N - src[0]['n']).max()))
            # motoren sin illum på motoren sine punkt mot min Lambert på mi geometri
            Et = fe.illum(P, N, dA, fe.TASK, np.array([0, 0, 1.0]))
            Em = E_lambert(src, TASK_M, UP)
            Ew = fe.illum(P, N, dA, fe.WALLG, np.array([0, -1.0, 0]))
            Ewm = E_kvad(Pm, Nm, dAm, WALL_M, FRAM)
            DK[f'{k}_{modus}'] = dict(geo=dgeo, maks_avvik_oppgave_pst=float(np.abs(Et / np.maximum(Em, 1e-12) - 1).max() * 100) if modus == 'arbeid' else None,
                                      avvik_vegg_snitt_pst=float(pst(Ew.mean(), Ewm.mean())))
            print(f"({k}) {modus:8s}: Δareal {dgeo['dA']:+.2e} m², Δsenter {dgeo['senter']:.1e} m, Δnormal {dgeo['normal']:.1e}"
                  + (f"   illum mot Lambert, maks punktavvik oppgåve {DK[f'{k}_{modus}']['maks_avvik_oppgave_pst']:.2f} %" if modus == 'arbeid' else '')
                  + f"   veggsnitt {DK[f'{k}_{modus}']['avvik_vegg_snitt_pst']:+.2f} %")
    # screen_block mot skugge på tilfeldige strekningar
    Pr = np.c_[rng.uniform(-0.8, 0.8, 4000), rng.uniform(-0.4, 0.75, 4000), rng.uniform(0, 1.2, 4000)]
    Qr = np.c_[rng.uniform(-0.8, 0.8, 300), rng.uniform(-0.4, 0.75, 300), rng.uniform(0, 1.2, 300)]
    ulik = int((fe.screen_block(Pr, Qr) != skugge(Pr, Qr)).sum())
    DK['screen_block_ulike'] = ulik; DK['screen_block_prova'] = 4000 * 300; DK['screen_block_del_blokkert'] = float(skugge(Pr, Qr).mean())
    print(f"screen_block mot eigen skugge: {ulik} ulike av {4000*300} tilfeldige strekningar ({100*skugge(Pr, Qr).mean():.1f} % blokkerte)")
    # visible / reflected mot eigne
    for k, op, s in (('a', lambda s: M1.opning(Ba, s), -20), ('b', lambda s: op_b(Bb, s), -20), ('c', lambda s: M3.opning(Bc, s), 0)):
        P, N, dA = op(math.radians(s))
        src = kjelde(k, 'arbeid')
        mi_vis = any(sikt(src, e)[0] > 0 for e in fe.EYES)
        mi_refl = any(spegling(src, e, 0.0) > 0 for e in fe.EYES)
        DK[f'vis_refl_{k}'] = dict(motor_vis=bool(fe.visible(P, N)), min_vis=bool(mi_vis), motor_refl=bool(fe.reflected(P, N)), min_refl=bool(mi_refl))
        print(f"({k}) arbeid: visible motor/eigen {fe.visible(P, N)}/{mi_vis}   reflected motor/eigen {fe.reflected(P, N)}/{mi_refl}")
    # heile ψ/α-sveipet: er same tilstand vald, og held visible/reflected langs sveipet?
    avvik = 0
    for psi in range(-180, 180, 5):
        P, N, dA = M1.opning(Ba, math.radians(psi))
        src = [tube_ap(0.18, 0.62, psi, -0.315, 0.315)]
        a1 = bool(fe.visible(P, N)); a2 = any(sikt(src, e)[0] > 0 for e in fe.EYES)
        b1 = bool(fe.reflected(P, N)); b2 = any(spegling(src, e, 0.0) > 0 for e in fe.EYES)
        avvik += (a1 != a2) + (b1 != b2)
    DK['sveip_a_ulike_flagg'] = int(avvik)
    print(f"(a) heile ψ-sveipet (72 tilstandar): {avvik} ulike visible/reflected-flagg mellom motor og eigen kode")
    # (c): brettet mot armen i stemning (utanfor linsa, men det skuggar lysflata)
    za = Bc['zp'] + 0.02
    arm = dict(x=(-M3.COL_W / 2, M3.COL_W / 2), y=(Bc['yp'] - 0.012, M3.COL_Y + M3.COL_F), z=(za, za + M3.COL_F))
    r = kjelde('c', 'stemning')[0]
    zb = (r['c'][2] - r['hv'], r['c'][2] + r['hv'])
    kol = (arm['y'][0] < r['c'][1] < arm['y'][1]) and (zb[0] < arm['z'][0]) and (zb[1] > arm['z'][1])
    DK['c_brett_mot_arm'] = dict(arm=arm, brett_y=float(r['c'][1]), brett_z=zb, kolliderer=bool(kol), tapt_lysflate_cm2=float(M3.COL_W * (zb[1] - arm['z'][0]) * 1e4))
    print(f"(c) stemning: brettet står i planet y = {r['c'][1]:.2f}, z {zb[0]:.3f}–{zb[1]:.3f}; armen (U-profil) ligg i x ±{M3.COL_W/2:.2f}, y {arm['y'][0]:.3f}–{arm['y'][1]:.3f}, z {arm['z'][0]:.2f}–{arm['z'][1]:.2f}"
          f"  ->  {'BRETTET GÅR GJENNOM ARMEN' if kol else 'fritt'} (ei utsparing ville ta {DK['c_brett_mot_arm']['tapt_lysflate_cm2']:.0f} cm² av lysflata)")
except Exception as ex:                                             # kryssprøva skal ikkje velte kontrollrekninga
    DK['feil'] = repr(ex)
    print('kryssprøva feila:', repr(ex))
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
        return o.tolist()
    return o


json.dump(rein(UT), open(os.path.join(HER, 'fotometri.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('\nskrive: fotometri.json')
