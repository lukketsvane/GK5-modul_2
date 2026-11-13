# -*- coding: utf-8 -*-
"""Gransking, premiss-linsa: uavhengig strålesporing av (c) prisme og kontroll av lys på skjermen for (a).
Eigen kode frå grunnformlane (lambertsk utsending, Snell på vektorform, Fresnel, fluks per celle).
Ingen kall til felles.py eller form04/motor.py. Tal frå dei er skrivne av som konstantar.
Køyr: PYTHONIOENCODING=utf-8 python premiss_prisme.py
Modellstega (eitt grep om gongen):
  M0  kopi av premissen i motor.py: kjelda er eit punkt på LED-lina (fjernfelt), 2D-Snell i snittet, ingen endetap
  M1  M0 + eksakt 3D-Snell (skeive strålar, ξ ≠ 0)
  M2  M1 + strålen går ut frå staden han faktisk treffer plata (16 cm brei, 5 cm under lina)
  M3  M2 + strålar som går ut over endane av plata (|x| > 0,30) vert stoppa av kinna
"""
import math, json, os
import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(17)

# ---- scene (tal skrivne av frå felles.py l.17-27) ----
SX0, SX1, SY, SZ0, SZ1 = -0.275, 0.275, 0.45, 0.10, 0.42
WALL = 0.75
EYE = np.array([0.0, -0.30, 0.45])
TX = np.linspace(-0.30, 0.30, 7); TY = np.linspace(0.05, 0.40, 5)
WX = np.linspace(-0.70, 0.70, 8); WZ = np.linspace(0.05, 1.20, 6)
DX = np.linspace(-0.68, 0.68, 8); DY = np.linspace(0.02, 0.73, 5)
# ---- (c) prisme, tal skrivne av frå form04/motor.py FINAL ----
n = 1.49
L, BP, D, TP, YS, ZS, Y1, Y2 = 0.60, 0.16, 0.05, 0.003, 0.22, 0.70, 0.02, 0.43
RISS, SIG = 0.95, math.radians(4.0)


def fresnel(ci, ct, n1, n2):
    rs = ((n1 * ci - n2 * ct) / (n1 * ci + n2 * ct)) ** 2
    rp = ((n1 * ct - n2 * ci) / (n1 * ct + n2 * ci)) ** 2
    return 1 - 0.5 * (rs + rp)


# ---- rilleprofilen, rekna frå designregelen (jamn E: kumulativ fluks lineær i tan θ) ----
phm = math.atan(BP / 2 / D)
ph = np.linspace(-phm, phm, 4001)
F = (np.sin(ph) + math.sin(phm)) / (2 * math.sin(phm))
th1, th2 = math.atan((YS - Y2) / ZS), math.atan((YS - Y1) / ZS)
th = np.arctan(math.tan(th1) + F * (math.tan(th2) - math.tan(th1)))
pi_ = np.arcsin(np.sin(ph) / n)
tau = np.arctan2(n * np.sin(pi_) - np.sin(th), n * np.cos(pi_) - np.cos(th))
s_bot = D * np.tan(ph) + TP * np.tan(pi_)          # der strålen i snittet treff undersida (positiv mot brukaren)


def trace(N, model, alfa=0.0):
    """Returnerer (P0 startpunkt (N,3), V retning (N,3), w vekt i LED-lm per stråle). alfa: vipp om LED-aksen (motor.py-konvensjon)."""
    x0 = (rng.random(N) - 0.5) * L
    u1, u2 = rng.random(N), rng.random(N)
    st, ct = np.sqrt(u1), np.sqrt(1 - u1)
    fi = 2 * math.pi * u2
    # lokal ramme: f = fram (mot brukaren, -y), q = ned (-z). Retning (x, f, q)
    dx, df, dq = st * np.cos(fi), st * np.sin(fi), ct
    pa = np.arctan2(df, dq)                               # profilvinkel inn
    keep = np.abs(pa) < phm                               # renna klipper resten (som i motor.py)
    w = np.full(N, 1.0 / N)
    if model == 'M0':
        xi = np.arcsin(np.clip(dx, -1, 1))
        T1 = fresnel(np.cos(np.abs(pa)), np.cos(np.arcsin(np.sin(np.abs(pa)) / n)), 1.0, n)
        pin = np.arcsin(np.sin(pa) / n)
        ta = np.interp(pa, ph, tau)
        thx = np.interp(pa, ph, th)
        T2 = fresnel(np.cos(np.abs(pin - ta)), np.cos(np.abs(thx - ta)), n, 1.0)
        thx = thx + rng.normal(0, SIG, N)
        ox, of, oq = np.sin(xi), np.cos(xi) * np.sin(thx), np.cos(xi) * np.cos(thx)
        w = w * T1 * T2 * RISS * keep
        Px, Pf, Pq = x0, np.zeros(N), np.zeros(N)
    else:
        # topp: flat, normal opp (lokal -q). Snell på vektorform.
        r = 1 / n
        ci = dq                                            # cos mot normalen (ned)
        k = 1 - r * r * (1 - ci * ci)
        tx, tf, tq = r * dx, r * df, r * dq + (np.sqrt(k) - r * ci)
        T1 = fresnel(ci, np.sqrt(k), 1.0, n)
        # treffpunkt topp og botn
        xt = x0 + D * dx / dq; ft = D * df / dq
        xb = xt + TP * tx / tq; fb = ft + TP * tf / tq
        ta = np.interp(fb, s_bot, tau)                     # rilla der strålen faktisk treff
        mx, mf, mq = np.zeros(N), np.sin(ta), np.cos(ta)  # normal ut av PMMA (nedover)
        ci2 = tx * mx + tf * mf + tq * mq
        r2 = n
        k2 = 1 - r2 * r2 * (1 - ci2 * ci2)
        tir = k2 < 0
        k2 = np.clip(k2, 0, None)
        ox = r2 * tx + (np.sqrt(k2) - r2 * ci2) * mx
        of = r2 * tf + (np.sqrt(k2) - r2 * ci2) * mf
        oq = r2 * tq + (np.sqrt(k2) - r2 * ci2) * mq
        T2 = fresnel(np.clip(ci2, 1e-9, 1), np.sqrt(k2), n, 1.0)
        # mattering: same 4° gauss i profilvinkelen som motor.py
        g = rng.normal(0, SIG, N)
        cg, sg = np.cos(g), np.sin(g)
        of, oq = of * cg + oq * sg, -of * sg + oq * cg
        w = w * T1 * T2 * RISS * keep * (~tir)
        if model == 'M1':
            Px, Pf, Pq = x0, np.zeros(N), np.zeros(N)
        else:
            Px, Pf, Pq = xb, fb, np.full(N, D + TP)
            if model == 'M3':
                w = w * (np.abs(xt) <= L / 2)
    # til global ramme, med vipp alfa om LED-aksen: ned(a) = (0, -sin a, -cos a), fram(a) = (0, -cos a, sin a)
    fy, fz = -math.cos(alfa), math.sin(alfa)
    qy, qz = -math.sin(alfa), -math.cos(alfa)
    P0 = np.c_[Px, YS + Pf * fy + Pq * qy, ZS + Pf * fz + Pq * qz]
    V = np.c_[ox, of * fy + oq * qy, of * fz + oq * qz]
    V /= np.linalg.norm(V, axis=1, keepdims=True)
    return P0, V, w


def hits(P0, V, w):
    """Første treff: skjerm (framside eller bakside), bord z=0, vegg y=0,75. Returnerer dict med punkt og vekt."""
    big = 1e9
    with np.errstate(divide='ignore', invalid='ignore'):
        td = np.where(V[:, 2] < 0, -P0[:, 2] / V[:, 2], big)
        tw = np.where(V[:, 1] > 0, (WALL - P0[:, 1]) / V[:, 1], big)
        tsc = np.where(np.abs(V[:, 1]) > 1e-12, (SY - P0[:, 1]) / V[:, 1], big)
    tsc = np.where(tsc > 0, tsc, big)
    Ps = P0 + tsc[:, None] * V
    on_s = (tsc < big) & (Ps[:, 0] > SX0) & (Ps[:, 0] < SX1) & (Ps[:, 2] > SZ0) & (Ps[:, 2] < SZ1)
    tsc = np.where(on_s, tsc, big)
    t = np.minimum(np.minimum(td, tw), tsc)
    Q = P0 + t[:, None] * V
    kind = np.where(t == tsc, 1, np.where(t == td, 2, np.where(t == tw, 3, 0)))
    front = V[:, 1] > 0                                    # skjermframsida vender mot brukaren (-y); strålen må gå mot +y
    return Q, kind, front, w


def cellE(Q, w, cx, cy, hx, hy, i0, i1):
    E = np.zeros((len(cy), len(cx)))
    for a, y in enumerate(cy):
        for b, x in enumerate(cx):
            m = (np.abs(Q[:, i0] - x) < hx) & (np.abs(Q[:, i1] - y) < hy)
            E[a, b] = w[m].sum() / (4 * hx * hy)
    return E


def kor(model, alfa, N=2_000_000, chunks=4):
    """Køyrer chunks og gjev (Q, kind, front, w, P0, V) per chunk; w er skalert med 1/chunks."""
    for _ in range(chunks):
        P0, V, w = trace(N, model, alfa)
        Q, kind, front, w = hits(P0, V, w)
        yield Q, kind, front, w / chunks, P0, V


def arbeid(model):
    Et = 0; Erect = 0; sc_w = 0; Esc = 0; ut = 0; fk = 0; dsum = 0
    sxg, szg = np.linspace(-0.25, 0.25, 6), np.linspace(0.12, 0.40, 8)
    for Q, kind, front, w, P0, V in kor(model, 0.0):
        d = kind == 2
        Et = Et + cellE(Q[d], w[d], TX, TY, 0.025, 0.025, 0, 1)
        rect = d & (np.abs(Q[:, 0]) <= 0.30) & (Q[:, 1] >= 0.05) & (Q[:, 1] <= 0.40)
        Erect += w[rect].sum() / (0.60 * 0.35)
        sc = (kind == 1) & front
        sc_w += w[sc].sum()
        Esc = Esc + cellE(Q[sc], w[sc], sxg, szg, 0.05, 0.02, 0, 2)
        ut += w.sum(); fk += w[d & (Q[:, 1] < 0.0)].sum(); dsum += w[d].sum()
    Phi = 500 / Et.mean()
    Es = sc_w / ((SX1 - SX0) * (SZ1 - SZ0)) * Phi
    return dict(model=model, eta=float(ut), Phi=float(Phi), U0=float(Et.min() / Et.mean()), Phi_rekt=float(500 / Erect),
                E_skjerm_snitt=float(Es), E_skjerm_maks_celle=float(Esc.max() * Phi),
                del_paa_skjerm=float(sc_w / ut), del_paa_oppgava=float(Erect * 0.21 / ut),
                del_forbi_framkant=float(fk / ut), del_bord=float(dsum / ut))


def stemning(model, Phi_arb, alfa=math.radians(-105)):
    Ew = 0; Ed = 0; ut = 0; vw = 0; vd = 0
    for Q, kind, front, w, P0, V in kor(model, alfa):
        wv = kind == 3; d = kind == 2
        Ew = Ew + cellE(Q[wv], w[wv], WX, WZ, 0.025, 0.025, 0, 2)
        Ed = Ed + cellE(Q[d], w[d], DX, DY, 0.025, 0.025, 0, 1)
        ut += w.sum(); vw += w[wv].sum(); vd += w[d].sum()
    Ew, Ed = Ew.mean(), Ed.mean()
    return dict(R_stem=float(Ew / (Ew + Ed)) if Ew + Ed > 0 else None, Ev_stem=float(Ew * Phi_arb * 0.25),
                del_vegg_av_ut=float(vw / ut), del_bord_av_ut=float(vd / ut))


def ansikt(model, alfa=math.radians(70)):
    """Vertikal E ved midtauga og luminanskart av plata sett derfrå (snitt og topp)."""
    h = 0.03
    PP, WW = [], []
    for Q, kind, front, w, P0, V in kor(model, alfa, chunks=8):
        with np.errstate(divide='ignore', invalid='ignore'):
            te = np.where(V[:, 1] < 0, (EYE[1] - P0[:, 1]) / V[:, 1], -1)
        Pe = P0 + te[:, None] * V
        m = (te > 0) & (np.abs(Pe[:, 0] - EYE[0]) < h) & (np.abs(Pe[:, 2] - EYE[2]) < h) & (w > 0)
        PP.append(P0[m]); WW.append(w[m])
    P0 = np.vstack(PP); w = np.concatenate(WW); m = np.ones(len(w), bool)
    Ee = w[m].sum() / (2 * h) ** 2
    Phi150 = 150 / Ee
    if model in ('M0', 'M1'):
        return dict(E_auge_per_lm=float(Ee), Phi150=float(Phi150))
    # luminans: fluks frå plateflekk dA gjennom augeruta / (dA cos_p · Ω_ruta)
    # plateframe ved alfa: fram(a), ned(a)
    fy, fz = -math.cos(alfa), math.sin(alfa); qy, qz = -math.sin(alfa), -math.cos(alfa)
    rel = P0[m] - np.array([0, YS, ZS])
    s = rel[:, 1] * fy + rel[:, 2] * fz
    x = rel[:, 0]
    nrm = np.array([0, qy, qz])                       # lyssida si normal (ned i hovudramma)
    r = EYE - np.array([0, YS + (D + TP) * qy, ZS + (D + TP) * qz])
    rr = np.linalg.norm(r)
    cos_p = abs(r @ nrm) / rr
    cos_e = abs(r[1]) / rr
    Om = (2 * h) ** 2 * cos_e / rr ** 2
    sb = np.linspace(-BP / 2, BP / 2, 33); xb = np.linspace(-L / 2, L / 2, 7)
    H, _, _ = np.histogram2d(s, x, bins=[sb, xb], weights=w[m])
    dA = (sb[1] - sb[0]) * (xb[1] - xb[0])
    Lmap = H / (dA * cos_p * Om) * Phi150
    Lsnitt = w[m].sum() / (BP * L * cos_p * Om) * Phi150
    prof = H.sum(1) / ((sb[1] - sb[0]) * L * cos_p * Om) * Phi150
    lit = prof > 0.05 * prof.max()
    return dict(E_auge_per_lm=float(Ee), Phi150=float(Phi150), L_snitt=float(Lsnitt), L_topp_1cm=float(Lmap.max()),
                L_topp_band=float(prof.max()), breidd_lysande_cm=float(lit.sum() * (sb[1] - sb[0]) * 100))


# ---- (a): uavhengig lambertsk spalte, lys på skjermen ----
def spalte_a():
    R, be, eta, yp, hp, psi = 0.022, math.radians(25), 0.674110050973263, 0.18, 0.62, math.radians(-20)
    A = 117.14978215452189e-4
    Lx = A / (2 * R * math.sin(be))
    nn = np.array([0, -math.sin(psi), -math.cos(psi)]); tt = np.array([0, math.cos(psi), -math.sin(psi)])
    c = np.array([0, yp, hp]) + R * math.cos(be) * nn
    xs = (np.arange(400) + .5) / 400 * Lx - Lx / 2
    ws = (np.arange(5) + .5) / 5 * 2 - 1
    P = np.array([c + np.array([x, 0, 0]) + v * R * math.sin(be) * tt for x in xs for v in ws])
    dA = A / len(P)

    def E(Qs, qn, block):
        out = []
        for q in Qs:
            d = q - P; r2 = (d * d).sum(1); r = np.sqrt(r2)
            ce = d @ nn / r; cr = -(d @ qn) / r
            ok = (ce > 0) & (cr > 0)
            if block:
                s = (SY - P[:, 1]) / d[:, 1]
                X = P[:, 0] + s * d[:, 0]; Z = P[:, 2] + s * d[:, 2]
                ok &= ~((s > 0) & (s < 1) & (X > SX0) & (X < SX1) & (Z > SZ0) & (Z < SZ1))
            out.append((np.where(ok, ce * cr / r2, 0) * dA).sum())
        return np.array(out)
    Lk = eta / (math.pi * A)
    Tq = np.array([[x, y, 0] for y in TY for x in TX])
    Et = E(Tq, np.array([0, 0, 1.0]), True) * Lk
    Phi = 500 / Et.mean()
    gx = (np.arange(22) + .5) / 22 * (SX1 - SX0) + SX0; gz = (np.arange(16) + .5) / 16 * (SZ1 - SZ0) + SZ0
    Sq = np.array([[x, SY - 1e-4, z] for z in gz for x in gx])
    Es = E(Sq, np.array([0, -1.0, 0]), False) * Lk * Phi
    Eh = np.array([[x, y, 0] for y in TY for x in TX])
    return dict(Phi=float(Phi), U0=float(Et.min() / Et.mean()), E_skjerm_snitt=float(Es.mean()), E_skjerm_maks=float(Es.max()),
                E_skjerm_ved_400lm=float(Es.mean() / Phi * 400))


if __name__ == '__main__':
    res = {'(a)_spalte': spalte_a()}
    print('(a)', res['(a)_spalte'], flush=True)
    for mdl in ('M0', 'M1', 'M2', 'M3'):
        a = arbeid(mdl)
        a['stemning'] = stemning(mdl, a['Phi'])
        a['ansikt'] = ansikt(mdl)
        res[mdl] = a
        print(mdl, json.dumps(a, ensure_ascii=False), flush=True)
    json.dump(res, open(os.path.join(HER, 'premiss_prisme.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
