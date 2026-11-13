# -*- coding: utf-8 -*-
"""Stadfesting F4 (motbevisar 1): sjølvstendig Monte Carlo i røyrhulrommet, eigen kode.
Skil seg frå fotometri_kontroll.py: lambertsk trekk via n + einingskule, eigen skjering, eigen mottakar
(både flatesnitt og felles-metrikken = snitt av 7×5 punkt med små celler), og felles.lys() køyrd direkte som referanse.
Køyr: PYTHONIOENCODING=utf-8 python stadfest_F4_1.py
"""
import math, os, sys, time, json
import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
T0 = time.time()
R, BETA, RHO = 0.022, math.radians(25.0), 0.85
TX0, TX1, TY0, TY1 = -0.30, 0.30, 0.05, 0.40
SY, SX0, SX1, SZ0, SZ1 = 0.45, -0.275, 0.275, 0.10, 0.42
PX, PY = np.linspace(TX0, TX1, 7), np.linspace(TY0, TY1, 5)
KONF = {'a': dict(yp=0.18, hp=0.62, Lc=0.63, opn=[(-0.315, 0.315)], eta=None),
        'b': dict(yp=0.25, hp=0.62, Lc=0.6016, opn=[(-0.30, -0.02), (0.02, 0.30)], eta=None)}


def lamb(n, rng):
    """Lambertsk retning om normalane n: normaliser n + uniform punkt på einingskula."""
    u = rng.normal(size=n.shape)
    u /= np.linalg.norm(u, axis=1, keepdims=True)
    d = n + u
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    return d


def inn_opn(x, opn):
    m = np.zeros(x.shape, bool)
    for a0, a1 in opn:
        m |= (x >= a0) & (x <= a1)
    return m


def hulrom(N, Lc, opn, kjelde, rng, halv=13.0, chunk=250_000):
    """Lokalt (x, a, b): a mot opningsmidten. Returnerer utgangspunkt, -retning, η, direkte del."""
    Pout, Dout, ut, dir_ = [], [], 0, 0
    for s0 in range(0, N, chunk):
        m = min(chunk, N - s0)
        x = rng.uniform(-Lc / 2, Lc / 2, m)
        if kjelde == 'akse':
            p = np.c_[x, np.zeros(m), np.zeros(m)]
            n = np.tile([0.0, 1.0, 0.0], (m, 1))
        else:
            th = math.pi + math.radians(halv) * rng.uniform(-1, 1, m)
            p = np.c_[x, 0.999999 * R * np.cos(th), 0.999999 * R * np.sin(th)]
            n = np.c_[np.zeros(m), -np.cos(th), -np.sin(th)]
        d = lamb(n, rng)
        alive = np.ones(m, bool)
        gen = 0
        while alive.any():
            idx = np.nonzero(alive)[0]
            pp, dd = p[idx], d[idx]
            qa = dd[:, 1] ** 2 + dd[:, 2] ** 2
            qb = 2 * (pp[:, 1] * dd[:, 1] + pp[:, 2] * dd[:, 2])
            qc = pp[:, 1] ** 2 + pp[:, 2] ** 2 - R * R
            disc = np.sqrt(np.maximum(qb * qb - 4 * qa * qc, 0))
            with np.errstate(divide='ignore', invalid='ignore'):
                tw = np.where(qa > 1e-15, (-qb + disc) / (2 * qa), np.inf)
                tx = np.where(dd[:, 0] > 1e-15, (Lc / 2 - pp[:, 0]) / dd[:, 0],
                              np.where(dd[:, 0] < -1e-15, (-Lc / 2 - pp[:, 0]) / dd[:, 0], np.inf))
            ende = tx < tw
            t = np.where(ende, tx, tw)
            q = pp + t[:, None] * dd
            ang = np.arctan2(q[:, 2], q[:, 1])
            go = (~ende) & (np.abs(ang) < BETA) & inn_opn(q[:, 0], opn)
            Pout.append(q[go]); Dout.append(dd[go]); ut += go.sum()
            if gen == 0:
                dir_ += go.sum()
            gen += 1
            # refleksjon eller absorpsjon
            lev = (~go) & (rng.random(len(idx)) < RHO)
            alive[idx[~lev]] = False
            j = idx[lev]
            qj, ej = q[lev], ende[lev]
            nr = np.where(ej[:, None], np.c_[-np.sign(qj[:, 0]), np.zeros(len(j)), np.zeros(len(j))],
                          np.c_[np.zeros(len(j)), -qj[:, 1] / R, -qj[:, 2] / R])
            p[j] = qj + 1e-10 * nr
            d[j] = lamb(nr, rng)
    return np.vstack(Pout), np.vstack(Dout), ut / N, dir_ / N


def korde(N, opn, eta, rng):
    L = np.array([b - a for a, b in opn])
    k = rng.choice(len(opn), N, p=L / L.sum())
    x = np.array([a for a, _ in opn])[k] + rng.random(N) * L[k]
    b = rng.uniform(-1, 1, N) * R * math.sin(BETA)
    P = np.c_[x, np.full(N, R * math.cos(BETA)), b]
    D = lamb(np.tile([0.0, 1.0, 0.0], (N, 1)), rng)
    return P, D, eta


def glob(P, D, yp, hp, psi):
    p = math.radians(psi)
    e = np.array([0.0, -math.sin(p), -math.cos(p)])
    v = np.array([0.0, math.cos(p), -math.sin(p)])
    G = np.array([0.0, yp, hp]) + P[:, :1] * np.array([1.0, 0, 0]) + P[:, 1:2] * e + P[:, 2:3] * v
    H = D[:, :1] * np.array([1.0, 0, 0]) + D[:, 1:2] * e + D[:, 2:3] * v
    return G, H


def mal(G, H, w, half=0.015):
    """w = LED-lm per stråle. Returnerer lx per LED-lm: flatesnitt, punktsnitt (felles-metrikk), punktmin, skjerm."""
    with np.errstate(divide='ignore', invalid='ignore'):
        ts = np.where(H[:, 1] > 1e-12, (SY - G[:, 1]) / H[:, 1], np.inf)
        xs, zs = G[:, 0] + ts * H[:, 0], G[:, 2] + ts * H[:, 2]
        skj = (ts > 0) & (xs > SX0) & (xs < SX1) & (zs > SZ0) & (zs < SZ1)
        td = np.where(H[:, 2] < -1e-12, -G[:, 2] / H[:, 2], np.inf)
    xd, yd = G[:, 0] + td * H[:, 0], G[:, 1] + td * H[:, 1]
    bord = np.isfinite(td) & ~(skj & (ts < td))
    xb, yb = xd[bord], yd[bord]
    inn = (xb > TX0) & (xb < TX1) & (yb > TY0) & (yb < TY1)
    E_flate = inn.sum() * w / ((TX1 - TX0) * (TY1 - TY0))
    Ep = np.array([[((np.abs(xb - px) < half) & (np.abs(yb - py) < half)).sum() for px in PX] for py in PY]) * w / (2 * half) ** 2
    Es = skj.sum() * w / ((SX1 - SX0) * (SZ1 - SZ0))
    return dict(E_flate=E_flate, E_pkt=Ep.mean(), U0_pkt=Ep.min() / Ep.mean(), Es=Es, nmin=int(Ep.min() / w * (2 * half) ** 2))


# ---------- referanse: felles.lys() direkte på motorane ----------
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form01')); sys.path.insert(0, os.path.join(ROOT, 'form02'))
import felles as fe
import motor as M1
import val as V2
Ba = dict(M1.FINAL, yp=0.18, hp=0.62)
Bb = dict(V2.B_KROK)
REF = {}
for k, B, opf in (('a', Ba, M1.opning), ('b', Bb, V2.opning_krok)):
    eta = M1.eta(B)
    KONF[k]['eta'] = eta
    P, N, dA = opf(B, math.radians(-20))
    r = fe.lys(P, N, dA, eta)
    REF[k] = dict(eta=eta, Phi=r['Phi'], U0=r['U0'], A=dA.sum(), xmin=float(P[:, 0].min()), xmax=float(P[:, 0].max()))
    print(f"felles.lys ({k}) ψ −20: η {eta:.4f}  Φ {r['Phi']:.1f} lm  U0 {r['U0']:.3f}  opning x {P[:,0].min():+.3f}..{P[:,0].max():+.3f}  A {dA.sum()*1e4:.1f} cm²", flush=True)

rng = np.random.default_rng(777)
NMC = int(os.environ.get('NMC', 1_000_000))
UT = {'ref_felles': REF}
for k in 'ab':
    c = KONF[k]
    for kj in ('korde', 'akse', 'bakvegg', 'bakvegg_smal'):
        t1 = time.time()
        if kj == 'korde':
            P, D, eta = korde(NMC, c['opn'], c['eta'], rng); dr = None
            w = eta / NMC
        else:
            P, D, eta, dr = hulrom(NMC, c['Lc'], c['opn'], 'akse' if kj == 'akse' else 'bakvegg', rng,
                                   halv=13.0 if kj == 'bakvegg' else 5.0)
            w = 1.0 / NMC
        res = {}
        for psi in (-25, -20, -15):
            G, H = glob(P, D, c['yp'], c['hp'], psi)
            m = mal(G, H, w)
            res[psi] = dict(Phi_flate=500 / m['E_flate'], Phi_pkt=500 / m['E_pkt'], U0_pkt=m['U0_pkt'],
                            skjerm_lx=m['Es'] * 500 / m['E_pkt'], nmin=m['nmin'])
        UT[f'{k}_{kj}'] = dict(eta=eta, direkte=dr, psi=res)
        r = res[-20]
        print(f"({k}) {kj:12s} η {eta:.3f}" + (f" dir {dr:.3f}" if dr is not None else '          ') +
              f" | ψ−20: Φ flate {r['Phi_flate']:6.0f}  Φ 7×5 {r['Phi_pkt']:6.0f}  U0 7×5 {r['U0_pkt']:.2f}  skjerm {r['skjerm_lx']:4.0f} lx  (min-celle {r['nmin']})"
              f" | ψ−25: Φ7×5 {res[-25]['Phi_pkt']:5.0f} U0 {res[-25]['U0_pkt']:.2f} | ψ−15: Φ7×5 {res[-15]['Phi_pkt']:5.0f} U0 {res[-15]['U0_pkt']:.2f}  ({time.time()-t1:.0f} s)", flush=True)


def rein(o):
    if isinstance(o, dict):
        return {str(a): rein(b) for a, b in o.items()}
    if isinstance(o, (np.floating, np.integer)):
        return float(o)
    return o


print(json.dumps(rein({k: {'eta': v['eta'], 'direkte': v['direkte']} for k, v in UT.items() if k != 'ref_felles'})))
print(f"ferdig {time.time()-T0:.0f} s")
