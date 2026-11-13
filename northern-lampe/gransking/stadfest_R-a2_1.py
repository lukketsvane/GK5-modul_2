# -*- coding: utf-8 -*-
"""Motbevis R-a2 (leppe 5-10 / 30 mm) · eigen kode, ingen import av prosjektfiler.
  L  arbeid, lambertsk korde: synleg del av korda i snittet (leppene er parallelle med aksen, og alle
     mottakarar ligg innanfor opninga i x), deretter EKSAKT polygonformel på synlege rektangel.
  S  stemning: punktkvadratur 3D med leppe (x-lengd som opninga + 1 cm, og uendeleg), skjermen som hinder.
  M  Monte Carlo i røyret (LED på bakveggen), eigen kode, leppe som svart plate.
Køyr: PYTHONIOENCODING=utf-8 python stadfest_R-a2_1.py [L|S|M]
"""
import sys, math, time
import numpy as np

T0 = time.time()
R, BETA = 0.022, math.radians(25.0)
HV, RC = R * math.sin(BETA), R * math.cos(BETA)
SX0, SX1, SY, SZ0, SZ1 = -0.275, 0.275, 0.45, 0.10, 0.42
WY = 0.75
X1 = np.array([1.0, 0, 0])
KONF = {'a': dict(O=(0, 0.18, 0.62), opn=[(-0.315, 0.315)], eta=0.674110, Lcav=0.63),
        'b': dict(O=(0, 0.25, 0.62), opn=[(-0.30, -0.02), (0.02, 0.30)], eta=0.666918, Lcav=0.64 * 0.94)}
AUGE8 = np.array([(0, -0.30, 0.45), (-0.15, -0.30, 0.45), (0.15, -0.30, 0.45), (0, -0.15, 0.45), (0, -0.30, 0.40), (0, -0.30, 0.50),
                  (0, -0.15, 0.40), (0, -0.15, 0.50)], float)
AUGE10 = np.vstack([AUGE8, [(0, -0.60, 1.60), (0, 0.0, 1.60)]])
PSI_ARB = -20.0


def ev(psi):
    p = math.radians(psi)
    return np.array([0.0, -math.sin(p), -math.cos(p)]), np.array([0.0, math.cos(p), -math.sin(p)])


def leppedir(psi):
    """Stiv med røyret: −z når ψ = ψ_arb."""
    ea, va = ev(PSI_ARB)
    e, v = ev(psi)
    return (-ea[2]) * e + (-va[2]) * v


# ---------------------------------------------------------------- L · eksakt polygonformel på synleg del
def kryss2(p, q, a, b):
    """2D: krysser segment p->q (p (n,2), q (2,)) segmentet a->b? Strengt indre."""
    d1 = q - p; d2 = b - a
    den = d1[:, 0] * d2[1] - d1[:, 1] * d2[0]
    w = a - p
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (w[:, 0] * d2[1] - w[:, 1] * d2[0]) / den
        u = (w[:, 0] * d1[:, 1] - w[:, 1] * d1[:, 0]) / den
    return (np.abs(den) > 1e-15) & (t > 1e-9) & (t < 1 - 1e-9) & (u > 1e-9) & (u < 1 - 1e-9)


VS = ((np.arange(1200) + 0.5) / 1200 * 2 - 1) * HV          # punkt langs korda (v)


def synleg_intervall(O, psi, q, hb, hv):
    """Liste av synlege v-intervall av korda sett frå q (snittet y–z). Tom liste: ikkje synleg."""
    e, v = ev(psi)
    c0 = np.asarray(O, float) + RC * e
    if (q - c0) @ e <= 0:
        return []
    yz = lambda P: np.asarray(P)[..., 1:]
    P2 = yz(c0[None] + VS[:, None] * v[None])
    q2 = yz(q)
    dl = leppedir(psi)
    ok = np.ones(len(VS), bool)
    for sg, h in ((-1, hb), (1, hv)):
        if h > 0:
            E0 = c0 + sg * HV * v
            ok &= ~kryss2(P2, q2, yz(E0), yz(E0 + h * dl))
    if not ok.any():
        return []
    # løp av samanhengande synlege punkt
    d = np.diff(np.r_[0, ok.astype(int), 0])
    st, sl = np.where(d == 1)[0], np.where(d == -1)[0]
    dv = VS[1] - VS[0]
    return [(VS[i] - dv / 2, VS[j - 1] + dv / 2) for i, j in zip(st, sl)]


def proj_romvinkel(q, nq, V):
    """Lamberts polygonformel: projisert romvinkel (E/L) frå polygon V (k,3) sett frå q med normal nq."""
    a = V - q
    a /= np.linalg.norm(a, axis=1, keepdims=True)
    s = 0.0
    for i in range(len(a)):
        u, w = a[i], a[(i + 1) % len(a)]
        cr = np.cross(u, w)
        n = np.linalg.norm(cr)
        if n < 1e-15:
            continue
        s += math.atan2(n, u @ w) * (cr @ nq) / n
    return 0.5 * abs(s)


def E_eksakt(O, psi, opn, Q, nq, hb, hv):
    e, v = ev(psi)
    c0 = np.asarray(O, float) + RC * e
    out = np.zeros(len(Q))
    for i, q in enumerate(Q):
        for v0, v1 in synleg_intervall(O, psi, q, hb, hv):
            for a0, a1 in opn:
                V = np.array([c0 + a0 * X1 + v0 * v, c0 + a1 * X1 + v0 * v, c0 + a1 * X1 + v1 * v, c0 + a0 * X1 + v1 * v])
                out[i] += proj_romvinkel(q, nq, V)
    return out


def del_L():
    tx, ty = np.meshgrid(np.linspace(-0.30, 0.30, 7), np.linspace(0.05, 0.40, 5))
    TASK = np.c_[tx.ravel(), ty.ravel(), np.zeros(tx.size)]
    sx, sz = np.meshgrid(SX0 + (np.arange(22) + .5) / 22 * (SX1 - SX0), SZ0 + (np.arange(13) + .5) / 13 * (SZ1 - SZ0))
    SKJ = np.c_[sx.ravel(), np.full(sx.size, SY - 1e-4), sz.ravel()]
    up, inn = np.array([0, 0, 1.0]), np.array([0, -1.0, 0])
    for k in 'ab':
        c = KONF[k]
        A = sum(b - a for a, b in c['opn']) * 2 * HV
        ref = None
        for psi in (-20, -15, -10, -5):
            for hb, hv in ((0, 0), (0.005, 0), (0.010, 0), (0, 0.030), (0.005, 0.030), (0.010, 0.030)):
                if psi != -20 and not (hb == 0.010 and hv == 0.030):
                    continue
                Et = E_eksakt(c['O'], psi, c['opn'], TASK, up, hb, hv)
                Es = E_eksakt(c['O'], psi, c['opn'], SKJ, inn, hb, hv)
                Phi = 500 * math.pi * A / (c['eta'] * Et.mean())
                L500 = 500 / Et.mean()
                nsyn = sum(1 for E in AUGE8 if synleg_intervall(c['O'], psi, E, hb, hv))
                if ref is None:
                    ref = Phi
                print(f"L ({k}) ψ {psi:+d} leppe {hb*1e3:2.0f}/{hv*1e3:2.0f} mm: Φ {Phi:6.0f} lm ({100*(Phi/ref-1):+5.1f} %)  U0 {Et.min()/Et.mean():.3f}"
                      f"  skjerm {Es.mean()*L500:5.1f} lx (maks {Es.max()*L500:4.0f})  synleg for {nsyn}/8 auge", flush=True)


# ---------------------------------------------------------------- S · stemning, punktkvadratur 3D
def kjelde(O, psi, opn, du=0.0075, nv=24):
    e, v = ev(psi)
    c0 = np.asarray(O, float) + RC * e
    sv = ((np.arange(nv) + .5) / nv * 2 - 1) * HV
    P, dA = [], []
    for a0, a1 in opn:
        nu = max(1, round((a1 - a0) / du))
        su = a0 + (np.arange(nu) + .5) / nu * (a1 - a0)
        U, W = np.meshgrid(su, sv, indexing='ij')
        P.append(c0 + U.ravel()[:, None] * X1 + W.ravel()[:, None] * v)
        dA.append(np.full(U.size, (a1 - a0) / nu * 2 * HV / nv))
    return np.vstack(P), np.concatenate(dA), e, v, c0


def blokk_leppe(P, Q, E0, dl, h, xh):
    """(nP, nQ) maske: segmentet P->Q kryssar leppeplata."""
    m = np.cross(X1, dl)
    a = (P - E0) @ m; b = (Q - E0) @ m
    kr = a[:, None] * b[None, :] < 0
    with np.errstate(divide='ignore', invalid='ignore'):
        t = a[:, None] / (a[:, None] - b[None, :])
    X = P[:, None, :] + t[..., None] * (Q[None] - P[:, None])
    al = (X - E0) @ dl
    return kr & (al > 0) & (al < h) & (np.abs(X[..., 0]) < xh)


def blokk_skjerm(P, Q):
    d = Q[None] - P[:, None]
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (SY - P[:, None, 1]) / d[..., 1]
    X, Z = P[:, None, 0] + t * d[..., 0], P[:, None, 2] + t * d[..., 2]
    return (t > 1e-6) & (t < 1 - 1e-6) & (X > SX0) & (X < SX1) & (Z > SZ0) & (Z < SZ1)


def E_kv(P, e, dA, Q, nq, lp, bit=200):
    out = np.zeros(len(Q))
    for i in range(0, len(Q), bit):
        q = Q[i:i + bit]
        d = q[None] - P[:, None]
        r2 = (d * d).sum(-1); r = np.sqrt(r2)
        w = np.clip((d @ e) / r, 0, None) * np.clip(-(d @ nq) / r, 0, None) / r2
        bl = blokk_skjerm(P, q)
        for E0, dl, h, xh in lp:
            bl |= blokk_leppe(P, q, E0, dl, h, xh)
        out[i:i + bit] = (np.where(bl, 0.0, w) * dA[:, None]).sum(0)
    return out


def cellar(x0, x1, nx, a0, a1, na):
    X, Y = np.meshgrid(x0 + (np.arange(nx) + .5) / nx * (x1 - x0), a0 + (np.arange(na) + .5) / na * (a1 - a0))
    return X.ravel(), Y.ravel()


def del_S():
    wx, wz = cellar(-0.70, 0.70, 35, 0.05, 1.20, 29)
    VEGG = np.c_[wx, np.full(wx.size, WY - 1e-3), wz]
    dx, dy = cellar(-0.70, 0.70, 28, 0.0, 0.75, 15)
    BORD = np.c_[dx, dy, np.zeros(dx.size)]
    E_maal = 10.0 * math.pi / 0.75
    for k in 'ab':
        c = KONF[k]
        xh0 = max(abs(a) for o in c['opn'] for a in o) + 0.01
        for hb, hv, xh in ((0, 0, 0), (0.005, 0.030, xh0), (0.010, 0.030, xh0), (0.010, 0.030, 9.0)):
            best, rad = None, []
            for psi in range(-160, -59, 5):
                P, dA, e, v, c0 = kjelde(c['O'], psi, c['opn'])
                dl = leppedir(psi)
                lp = [(c0 + sg * HV * v, dl, h, xh) for sg, h in ((-1, hb), (1, hv)) if h > 0]
                kL = c['eta'] / (math.pi * dA.sum())
                Ew = E_kv(P, e, dA, VEGG, np.array([0, -1.0, 0]), lp).mean() * kL
                Ed = E_kv(P, e, dA, BORD, np.array([0, 0, 1.0]), lp).mean() * kL
                # synleg: nokon kjeldepunkt framfor og utan leppe imellom, for 10 auge
                syn = 0
                for E in AUGE10:
                    fr = (E - P) @ e > 0
                    if not fr.any():
                        continue
                    b = np.zeros(fr.sum(), bool)
                    for E0, dl_, h, xh_ in lp:
                        b |= blokk_leppe(P[fr], E[None], E0, dl_, h, xh_)[:, 0]
                    syn += int((~b).any())
                Rr = Ew / (Ew + Ed)
                rad.append((psi, Ew, Rr, syn))
                if Rr >= 0.5 and syn == 0 and (best is None or Ew > best[1]):
                    best = (psi, Ew, Rr, syn)
            r95 = next(r for r in rad if r[0] == -95)
            lm = E_maal / best[1]
            print(f"S ({k}) leppe {hb*1e3:2.0f}/{hv*1e3:2.0f} mm xh {xh:.3f}: ψ −95 Ē_v {r95[1]:.4f} lx/LED-lm (synleg {r95[3]})   beste ψ {best[0]}: "
                  f"Ē_v {best[1]:.4f}  R {best[2]:.3f}  10 cd/m²: {lm:.0f} lm = {lm/100:.2f} W   vri {PSI_ARB-best[0]:.0f}°   ({time.time()-T0:.0f} s)", flush=True)
            print('      ψ: ' + '  '.join(f"{p}:{w:.3f}{'*' if s else ''}" for p, w, _, s in rad), flush=True)


# ---------------------------------------------------------------- M · Monte Carlo, LED på bakveggen
def cosvekt(nrm, rng):
    n = len(nrm)
    u1, u2 = rng.random(n), rng.random(n)
    r, ph = np.sqrt(u1), 2 * math.pi * u2
    t1 = np.cross(nrm, np.where(np.abs(nrm[:, :1]) < 0.9, [[1.0, 0, 0]], [[0, 1.0, 0]]))
    t1 /= np.linalg.norm(t1, axis=1, keepdims=True)
    t2 = np.cross(nrm, t1)
    return (r * np.cos(ph))[:, None] * t1 + (r * np.sin(ph))[:, None] * t2 + np.sqrt(1 - u1)[:, None] * nrm


def mc(n, Lcav, opn, rng, rho=0.85, halv=13.0):
    """Lokal ramme (x, a, b): a mot opningsmidten. Returnerer utgangspunkt og -retning."""
    x = (rng.random(n) - 0.5) * Lcav
    ph = math.pi + math.radians(halv) * (2 * rng.random(n) - 1)
    p = np.c_[x, R * np.cos(ph), R * np.sin(ph)] * np.array([1, 1 - 1e-9, 1 - 1e-9])
    d = cosvekt(-np.c_[np.zeros(n), np.cos(ph), np.sin(ph)], rng)
    Pu, Du = [], []
    while len(p):
        A = d[:, 1] ** 2 + d[:, 2] ** 2
        B = p[:, 1] * d[:, 1] + p[:, 2] * d[:, 2]
        C = p[:, 1] ** 2 + p[:, 2] ** 2 - R * R
        with np.errstate(divide='ignore', invalid='ignore'):
            tc = np.where(A > 1e-15, (-B + np.sqrt(np.maximum(B * B - A * C, 0))) / A, np.inf)
            tx = np.where(d[:, 0] > 0, (Lcav / 2 - p[:, 0]) / d[:, 0], np.where(d[:, 0] < 0, (-Lcav / 2 - p[:, 0]) / d[:, 0], np.inf))
        lok = tx < tc
        t = np.minimum(tc, tx)
        q = p + t[:, None] * d
        iopn = np.zeros(len(q), bool)
        for a0, a1 in opn:
            iopn |= (q[:, 0] > a0) & (q[:, 0] < a1)
        ut = ~lok & (np.abs(np.arctan2(q[:, 2], q[:, 1])) < BETA) & iopn
        Pu.append(q[ut]); Du.append(d[ut])
        lev = ~ut & (rng.random(len(q)) < rho)
        q, lk = q[lev], lok[lev]
        nr = np.where(lk[:, None], np.c_[-np.sign(q[:, 0]), np.zeros(len(q)), np.zeros(len(q))],
                      -np.c_[np.zeros(len(q)), q[:, 1], q[:, 2]] / np.hypot(q[:, 1], q[:, 2])[:, None])
        d = cosvekt(nr, rng)
        p = q + 1e-9 * nr
    return np.vstack(Pu), np.vstack(Du)


def del_M(n=700_000):
    rng = np.random.default_rng(7)
    TX0, TX1, TY0, TY1 = -0.30, 0.30, 0.05, 0.40
    GX, GY = np.linspace(TX0, TX1, 7), np.linspace(TY0, TY1, 5)
    for k in 'ab':
        c = KONF[k]
        t1 = time.time()
        P, D = mc(n, c['Lcav'], c['opn'], rng)
        w = 1.0 / n
        print(f"M ({k}) η {len(P)/n:.3f}  ({time.time()-t1:.0f} s)", flush=True)
        ref = None
        for psi in (-20,):
            e, v = ev(psi)
            O = np.asarray(c['O'], float)
            G = O + P[:, :1] * X1 + P[:, 1:2] * e + P[:, 2:3] * v
            H = D[:, :1] * X1 + D[:, 1:2] * e + D[:, 2:3] * v
            c0 = O + RC * e
            dl = leppedir(psi)
            xh = max(abs(a) for o in c['opn'] for a in o) + 0.01
            for hb, hv in ((0, 0), (0.005, 0.030), (0.010, 0.030), (0, 0.030)):
                bl = np.zeros(len(G), bool)
                for sg, h in ((-1, hb), (1, hv)):
                    if h > 0:
                        E0 = c0 + sg * HV * v
                        m = np.cross(X1, dl)
                        with np.errstate(divide='ignore', invalid='ignore'):
                            s = ((E0 - G) @ m) / (H @ m)
                        Xq = G + s[:, None] * H
                        al = (Xq - E0) @ dl
                        bl |= (s > 1e-9) & (al > 0) & (al < h) & (np.abs(Xq[:, 0]) < xh)
                g, hh = G[~bl], H[~bl]
                with np.errstate(divide='ignore', invalid='ignore'):
                    ts = np.where(hh[:, 1] > 0, (SY - g[:, 1]) / hh[:, 1], np.inf)
                    xs, zs = g[:, 0] + ts * hh[:, 0], g[:, 2] + ts * hh[:, 2]
                    ts = np.where((xs > SX0) & (xs < SX1) & (zs > SZ0) & (zs < SZ1), ts, np.inf)
                    td = np.where(hh[:, 2] < 0, -g[:, 2] / hh[:, 2], np.inf)
                    xd, yd = g[:, 0] + td * hh[:, 0], g[:, 1] + td * hh[:, 1]
                    td = np.where((xd > -0.70) & (xd < 0.70) & (yd > 0) & (yd < 0.75), td, np.inf)
                    tw = np.where(hh[:, 1] > 0, (WY - g[:, 1]) / hh[:, 1], np.inf)
                bord = (td < ts) & (td < tw) & np.isfinite(td)
                skj = (ts < td) & (ts < tw) & np.isfinite(ts)
                bx, by = xd[bord], yd[bord]
                inn = (bx > TX0) & (bx < TX1) & (by > TY0) & (by < TY1)
                Em = inn.sum() * w / ((TX1 - TX0) * (TY1 - TY0))
                Phi = 500 / Em
                Hp, _, _ = np.histogram2d(bx, by, bins=[np.sort(np.r_[GX - 0.02, GX + 0.02]), np.sort(np.r_[GY - 0.02, GY + 0.02])])
                Ep = Hp[::2, ::2] * w / 16e-4
                Hn, _, _ = np.histogram2d(bx[inn], by[inn], bins=[5, 3], range=[[TX0, TX1], [TY0, TY1]])
                Es = skj.sum() * w / ((SX1 - SX0) * (SZ1 - SZ0)) * Phi
                if ref is None:
                    ref = Phi
                print(f"M ({k}) ψ {psi:+d} leppe {hb*1e3:2.0f}/{hv*1e3:2.0f}: Φ {Phi:6.0f} lm ({100*(Phi/ref-1):+5.1f} % mot MC utan leppe)"
                      f"  U0 7×5 {Ep.min()/Em:.3f} (×1,09 = {1.09*Ep.min()/Em:.2f})  EN 5×3 {Hn.min()/Hn.mean():.3f}  skjerm {Es:5.1f} lx"
                      f"  min-celle {int(Hp[::2, ::2].min())}", flush=True)


if __name__ == '__main__':
    m = sys.argv[1] if len(sys.argv) > 1 else 'L'
    {'L': del_L, 'S': del_S, 'M': del_M}[m]()
    print(f'ferdig ({time.time()-T0:.0f} s)')
