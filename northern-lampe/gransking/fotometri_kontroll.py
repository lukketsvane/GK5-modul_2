# -*- coding: utf-8 -*-
"""Gransking 3 · fotometri (a)/(b) og felles lysmodell: det fotometri_ab.py ikkje dekte. 2026-11-13.

Ny, eigen kode frå grunnformlane. Ingen import av felles.py, motorane eller fotometri_ab.py.
  A  Monte Carlo i røyrhulrommet (ny kode): ψ-sveip med fysisk utstråling (LED i aksen / LED på bakveggen)
     og ein lambertsk kordeflate trekt med same estimator (kontroll av estimatoren mot polygonformelen).
  B  spegling i skjermen med tilt, ved framover-strålegang frå auga (anna metode enn spegla auge i fotometri_ab)
  C  skjermlys og spegling i stemning (ψ −95, 25 %)
  D  leppe (svart, stiv del av røyret) langs opninga, fint utval, både lambertsk og MC
Køyr:  PYTHONIOENCODING=utf-8 python fotometri_kontroll.py   -> fotometri_kontroll.json
"""
import json, math, os, time
import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
T0 = time.time()
UT = {}

# ---- scene (tal skrivne av frå felles.py) ----
SX0, SX1, SY, SZ0, SZ1 = -0.275, 0.275, 0.45, 0.10, 0.42
WY = 0.75
TX0, TX1, TY0, TY1 = -0.30, 0.30, 0.05, 0.40
WX0, WX1, WZ0, WZ1 = -0.70, 0.70, 0.05, 1.20
DX0, DX1, DY0, DY1 = -0.70, 0.70, 0.0, 0.75
R, BETA, RHO = 0.022, math.radians(25.0), 0.85
A_T, A_W, A_D = (TX1 - TX0) * (TY1 - TY0), (WX1 - WX0) * (WZ1 - WZ0), (DX1 - DX0) * (DY1 - DY0)
AUGE = {'nominell': (0, -0.30, 0.45), 'x -15': (-0.15, -0.30, 0.45), 'x +15': (0.15, -0.30, 0.45),
        'fram 15': (0, -0.15, 0.45), '5 lågare': (0, -0.30, 0.40), '5 høgare': (0, -0.30, 0.50),
        'fram 15 + lågare 5': (0, -0.15, 0.40), 'fram 15 + høgare 5': (0, -0.15, 0.50)}
KONF = {'a': dict(yp=0.18, hp=0.62, opn=[(-0.315, 0.315)], Lcav=0.63, Phi_json=1255.2431, eta_motor=0.674110),
        'b': dict(yp=0.25, hp=0.62, opn=[(-0.30, -0.02), (0.02, 0.30)], Lcav=0.6016, Phi_json=1311.2998, eta_motor=0.666918)}
HV = R * math.sin(BETA)
RC = R * math.cos(BETA)
X1 = np.array([1.0, 0, 0])


def e_(psi):
    p = math.radians(psi)
    return np.array([0.0, -math.sin(p), -math.cos(p)])


def v_(psi):
    p = math.radians(psi)
    return np.array([0.0, math.cos(p), -math.sin(p)])


def hdr(s):
    print('\n' + '=' * 100 + '\n' + s + '\n' + '=' * 100, flush=True)


# =====================================================================================================
# A · Monte Carlo i hulrommet. Lokalt: x langs aksen, a mot opningsmidten (e), b = x̂ × a (v).
# =====================================================================================================
def cosvekt(nrm, rng):
    n = len(nrm)
    u1, u2 = rng.random(n), rng.random(n)
    s, ph = np.sqrt(u1), 2 * math.pi * u2
    ref = np.where(np.abs(nrm[:, :1]) < 0.9, np.array([[1.0, 0, 0]]), np.array([[0, 1.0, 0]]))
    t1 = np.cross(nrm, ref); t1 /= np.linalg.norm(t1, axis=1, keepdims=True)
    t2 = np.cross(nrm, t1)
    return (s * np.cos(ph))[:, None] * t1 + (s * np.sin(ph))[:, None] * t2 + np.sqrt(1 - u1)[:, None] * nrm


def i_opn(x, opn):
    m = np.zeros(len(x), bool)
    for a0, a1 in opn:
        m |= (x > a0) & (x < a1)
    return m


def mc_hulrom(n, Lcav, opn, led, rng, bit=400_000, led_halv=13.0):
    """Returnerer utgangsstrålar (P, D lokalt, float64) og η, direkte del."""
    Ps, Ds, nd, nut = [], [], 0, 0
    for i0 in range(0, n, bit):
        m = min(bit, n - i0)
        x = (rng.random(m) - 0.5) * Lcav
        if led == 'akse':
            p = np.c_[x, np.zeros(m), np.zeros(m)]
            nrm = np.tile([0.0, 1.0, 0.0], (m, 1))
        else:
            ph = math.pi + math.radians(led_halv) * (2 * rng.random(m) - 1)
            p = np.c_[x, R * (1 - 1e-7) * np.cos(ph), R * (1 - 1e-7) * np.sin(ph)]
            nrm = np.c_[np.zeros(m), -np.cos(ph), -np.sin(ph)]
        d = cosvekt(nrm, rng)
        live = np.arange(m)
        first = True
        while len(live):
            pp, dd = p[live], d[live]
            A = dd[:, 1] ** 2 + dd[:, 2] ** 2
            B = pp[:, 1] * dd[:, 1] + pp[:, 2] * dd[:, 2]
            C = pp[:, 1] ** 2 + pp[:, 2] ** 2 - R ** 2
            with np.errstate(divide='ignore', invalid='ignore'):
                tc = np.where(A > 1e-14, (-B + np.sqrt(np.maximum(B * B - A * C, 0))) / A, np.inf)
                te = np.where(dd[:, 0] > 0, (Lcav / 2 - pp[:, 0]) / dd[:, 0], np.where(dd[:, 0] < 0, (-Lcav / 2 - pp[:, 0]) / dd[:, 0], np.inf))
            cap = te < tc
            t = np.minimum(tc, te)
            q = pp + t[:, None] * dd
            ut = (~cap) & (np.abs(np.arctan2(q[:, 2], q[:, 1])) < BETA) & i_opn(q[:, 0], opn)
            Ps.append(q[ut]); Ds.append(dd[ut]); nut += ut.sum()
            if first:
                nd += ut.sum(); first = False
            keep = (~ut) & (rng.random(len(live)) < RHO)
            j, qj, cj = live[keep], q[keep], cap[keep]
            nr = np.where(cj[:, None], np.c_[-np.sign(qj[:, 0]), np.zeros(len(j)), np.zeros(len(j))],
                          -np.c_[np.zeros(len(j)), qj[:, 1], qj[:, 2]] / R)
            d[j] = cosvekt(nr, rng)
            p[j] = qj + 1e-9 * nr
            live = j
    return np.vstack(Ps), np.vstack(Ds), nut / n, nd / n


def lambert_opning(n, opn, eta, rng):
    """Same estimator, men kjelda er den lambertske kordeflata i felles.py (η trekt inn som vekt)."""
    L = np.array([b - a for a, b in opn]); w = L / L.sum()
    k = rng.choice(len(opn), n, p=w)
    a0 = np.array([a for a, _ in opn])[k]
    x = a0 + rng.random(n) * L[k]
    b = (2 * rng.random(n) - 1) * HV
    P = np.c_[x, np.full(n, RC), b]
    D = cosvekt(np.tile([0.0, 1.0, 0.0], (n, 1)), rng)
    return P, D, eta


def til_global(P, D, yp, hp, psi):
    e, v = e_(psi), v_(psi)
    O = np.array([0.0, yp, hp])
    G = O + P[:, :1] * X1 + P[:, 1:2] * e + P[:, 2:3] * v
    H = D[:, :1] * X1 + D[:, 1:2] * e + D[:, 2:3] * v
    return G, H


def leppe_blokk(G, H, lepper):
    """lepper: liste av (kantpunkt E0, retning dl, lengd h, x-halvbreidd). Stråle G + sH, s > 0."""
    blokk = np.zeros(len(G), bool)
    for E0, dl, h, xh in lepper:
        m = np.cross(X1, dl)
        dn = H @ m
        with np.errstate(divide='ignore', invalid='ignore'):
            s = ((E0 - G) @ m) / dn
        Q = G + s[:, None] * H
        al = (Q - E0) @ dl
        blokk |= (s > 1e-7) & (al > 0) & (al < h) & (np.abs(Q[:, 0]) < xh)
    return blokk


def treff(G, H):
    """Første treff: skjerm (framsida), bord, vegg. Returnerer dict med koordinatar."""
    with np.errstate(divide='ignore', invalid='ignore'):
        ts = np.where(H[:, 1] > 1e-12, (SY - G[:, 1]) / H[:, 1], np.inf)
        xs, zs = G[:, 0] + ts * H[:, 0], G[:, 2] + ts * H[:, 2]
        ts = np.where((ts > 0) & (xs > SX0) & (xs < SX1) & (zs > SZ0) & (zs < SZ1), ts, np.inf)
        td = np.where(H[:, 2] < -1e-12, -G[:, 2] / H[:, 2], np.inf)
        xd, yd = G[:, 0] + td * H[:, 0], G[:, 1] + td * H[:, 1]
        td = np.where((xd > DX0) & (xd < DX1) & (yd > DY0) & (yd < DY1), td, np.inf)
        tw = np.where(H[:, 1] > 1e-12, (WY - G[:, 1]) / H[:, 1], np.inf)
        xw, zw = G[:, 0] + tw * H[:, 0], G[:, 2] + tw * H[:, 2]
        tw = np.where(zw > 0, tw, np.inf)
    T = np.stack([ts, td, tw]); f = T.argmin(0); fin = np.isfinite(T.min(0))
    return dict(skjerm=np.c_[xs, zs][(f == 0) & fin], bord=np.c_[xd, yd][(f == 1) & fin], vegg=np.c_[xw, zw][(f == 2) & fin])


GX7, GY5 = np.linspace(TX0, TX1, 7), np.linspace(TY0, TY1, 5)


def arbeidstal(G, H, w):
    """w: LED-lm per stråle per LED-lm. Gjev Ē (lx/LED-lm), U0 på 5×3 EN-celler og på 7×5 punkt (3×3 cm), skjerm (lx/LED-lm)."""
    s = treff(G, H)
    b = s['bord']
    inn = (b[:, 0] > TX0) & (b[:, 0] < TX1) & (b[:, 1] > TY0) & (b[:, 1] < TY1)
    Em = inn.sum() * w / A_T
    Hn, _, _ = np.histogram2d(b[inn, 0], b[inn, 1], bins=[5, 3], range=[[TX0, TX1], [TY0, TY1]])
    Hp, _, _ = np.histogram2d(b[:, 0], b[:, 1], bins=[np.sort(np.r_[GX7 - 0.02, GX7 + 0.02]), np.sort(np.r_[GY5 - 0.02, GY5 + 0.02])])
    Ep = Hp[::2, ::2] * w / 16e-4                      # annankvar bin er cella (4 × 4 cm) rundt punktet
    Es = len(s['skjerm']) * w / ((SX1 - SX0) * (SZ1 - SZ0))
    Hs, _, _ = np.histogram2d(s['skjerm'][:, 0], s['skjerm'][:, 1], bins=[11, 8], range=[[SX0, SX1], [SZ0, SZ1]])
    return dict(Em=Em, U0_EN=Hn.min() / max(Hn.mean(), 1e-12), U0_7x5=Ep.min() / max(Em, 1e-12), Es=Es,
                Es_maks=Hs.max() * w / ((SX1 - SX0) * (SZ1 - SZ0) / 88), n_min_celle=int(Hp[::2, ::2].min()))


def stemningstal(G, H, w):
    s = treff(G, H)
    wv = s['vegg']
    i_f = (wv[:, 0] > WX0) & (wv[:, 0] < WX1) & (wv[:, 1] > WZ0) & (wv[:, 1] < WZ1)
    Ev = i_f.sum() * w / A_W
    Ed = len(s['bord']) * w / A_D
    Hw, _, _ = np.histogram2d(wv[i_f, 0], wv[i_f, 1], bins=[14, 12], range=[[WX0, WX1], [WZ0, WZ1]])
    return dict(Ev=Ev, Ed=Ed, R=Ev / (Ev + Ed), Es=len(s['skjerm']) * w / ((SX1 - SX0) * (SZ1 - SZ0)), maks_snitt=Hw.max() / Hw.mean())


def synleg(yp, hp, psi):
    c = np.array([0.0, yp, hp]) + RC * e_(psi)
    return {nm: bool((np.asarray(E, float) - c) @ e_(psi) > 0) for nm, E in AUGE.items()}


def skjerm_vinkel(yp, hp, psi, E=AUGE['nominell']):
    """Vinkel (grader) mellom siktlina til opningsmidten og opningsplanet; negativ = skjerma."""
    c = np.array([0.0, yp, hp]) + RC * e_(psi)
    d = np.asarray(E, float) - c
    return math.degrees(math.asin(d @ e_(psi) / np.linalg.norm(d)))


hdr('A · Monte Carlo i røyret og ψ-sveip (Φ skalert til 500 lx på arbeidsflata)')
NMC = int(os.environ.get('NMC', 1_500_000))
NLAM = int(os.environ.get('NLAM', 1_000_000))
rng = np.random.default_rng(20261113)
DA = {}
EXIT = {}
for k in 'ab':
    c = KONF[k]
    for mod in ('lambert', 'akse', 'bakvegg'):
        t1 = time.time()
        if mod == 'lambert':
            P, D, eta = lambert_opning(NLAM, c['opn'], c['eta_motor'], rng)
            w, dirk = eta / NLAM, None
        else:
            P, D, eta, dirk = mc_hulrom(NMC, c['Lcav'], c['opn'], mod, rng)
            w = 1.0 / NMC
        EXIT[(k, mod)] = (P, D, w)
        rows = []
        for psi in list(range(-50, -30, 5)) + list(range(-30, 6)):
            G, H = til_global(P, D, c['yp'], c['hp'], psi)
            r = arbeidstal(G, H, w)
            vis = synleg(c['yp'], c['hp'], psi)
            rows.append(dict(psi=psi, Phi=500 / r['Em'], U0_7x5=r['U0_7x5'], U0_EN=r['U0_EN'], E_skjerm=r['Es'] * 500 / r['Em'],
                             E_skjerm_maks=r['Es_maks'] * 500 / r['Em'], n_min=r['n_min_celle'],
                             vis_nom=vis['nominell'], vis_nokon=any(vis.values()), vinkel=skjerm_vinkel(c['yp'], c['hp'], psi)))
        G, H = til_global(P, D, c['yp'], c['hp'], -95)
        st = stemningstal(G, H, w)
        ref = next(r for r in rows if r['psi'] == -20)
        ok_nom = [r for r in rows if not r['vis_nom'] and r['U0_7x5'] >= 0.40]
        ok_rob = [r for r in rows if not r['vis_nokon'] and r['U0_7x5'] >= 0.40]
        ok_15 = [r for r in rows if r['vinkel'] <= -15 and r['U0_7x5'] >= 0.40]
        best = lambda L, key: (min(L, key=lambda r: r[key]) if L else None)
        DA[f'{k}_{mod}'] = dict(eta=eta, direkte=dirk, n_ut=len(P), ref=ref, stemning=st,
                                minst_Phi_nom=best(ok_nom, 'Phi'), minst_skjerm_nom=best(ok_nom, 'E_skjerm'),
                                minst_Phi_robust=best(ok_rob, 'Phi'), minst_Phi_15grader=best(ok_15, 'Phi'), rader=rows)
        print(f"({k}) {mod:8s} η {eta:.3f}" + (f" (direkte {dirk:.3f})" if dirk is not None else '') + f"  {len(P)/1e6:.2f} M ut  ({time.time()-t1:.0f} s)")
        print(f"    ψ −20: Φ {ref['Phi']:6.0f} lm  U0 7×5 {ref['U0_7x5']:.2f}  EN 5×3 {ref['U0_EN']:.2f}  skjerm {ref['E_skjerm']:4.0f} lx (maks {ref['E_skjerm_maks']:4.0f})  min-celle {ref['n_min']} strålar")
        for lab, rr in (('beste Φ, skjerma nominelt', DA[f'{k}_{mod}']['minst_Phi_nom']), ('minst skjermlys, skjerma nominelt', DA[f'{k}_{mod}']['minst_skjerm_nom']),
                        ('beste Φ, skjerma for alle 8 auge', DA[f'{k}_{mod}']['minst_Phi_robust']), ('beste Φ, skjermvinkel ≥ 15°', DA[f'{k}_{mod}']['minst_Phi_15grader'])):
            if rr is None:
                print(f"    {lab:34s}: inga ψ i [−50, 5] held U0 ≥ 0,40")
            else:
                print(f"    {lab:34s}: ψ {rr['psi']:+3d}  Φ {rr['Phi']:6.0f} lm  U0 {rr['U0_7x5']:.2f}/{rr['U0_EN']:.2f}  skjerm {rr['E_skjerm']:4.0f} lx  vinkel {rr['vinkel']:+.1f}°")
        print(f"    stemning ψ −95: Ē_vegg {st['Ev']:.4f} lx/LED-lm  R {st['R']:.3f}  skjerm {st['Es']:.3f} lx/LED-lm  maks/snitt (10 cm) {st['maks_snitt']:.2f}", flush=True)
UT['A_mc'] = DA

# =====================================================================================================
# B · spegling med tilt, framover-strålegang frå auga gjennom skjermpunkt
# =====================================================================================================
hdr('B · Spegling i skjermen: framover-strålegang frå auga, skjermen tilta om underkanten (toppen bakover)')
_hs = np.arange(0.001, SZ1 - SZ0, 0.002); _xs = np.arange(SX0 + 0.001, SX1, 0.002)
HSG, XSG = np.meshgrid(_hs, _xs, indexing='ij'); HSG, XSG = HSG.ravel(), XSG.ravel()


def spegel_treff(yp, hp, psi, opn, E, tilt):
    t = math.radians(tilt)
    o = np.array([0.0, SY, SZ0]); u = np.array([0.0, math.sin(t), math.cos(t)]); m = np.array([0.0, -math.cos(t), math.sin(t)])
    S = o + XSG[:, None] * X1 + HSG[:, None] * u
    E = np.asarray(E, float)
    d = S - E; d /= np.linalg.norm(d, axis=1, keepdims=True)
    r = d - 2 * (d @ m)[:, None] * m
    e, v = e_(psi), v_(psi)
    c = np.array([0.0, yp, hp]) + RC * e
    rn = r @ e
    with np.errstate(divide='ignore', invalid='ignore'):
        s = ((c - S) @ e) / rn
    Q = S + s[:, None] * r
    ok = (s > 0) & (rn < 0) & (np.abs((Q - c) @ v) < HV) & i_opn(Q[:, 0], opn)
    return ok


def krit(yp, hp, psi, opn, E, lo=0.0, hi=35.0, steg=0.25):
    for tt in np.arange(lo, hi + 1e-9, steg):
        ok = spegel_treff(yp, hp, psi, opn, E, tt)
        if ok.any():
            return float(tt), float(ok.mean())
    return None, 0.0


DB = {}
for k in 'ab':
    c = KONF[k]
    DB[k] = {}
    for tilstand, psi in (('arbeid', -20), ('stemning', -95)):
        DB[k][tilstand] = {}
        for nm, E in AUGE.items():
            kt, _ = krit(c['yp'], c['hp'], psi, c['opn'], E)
            # del av skjermflata som syner opninga ved 20° tilt
            f20 = float(spegel_treff(c['yp'], c['hp'], psi, c['opn'], E, 20.0).mean())
            DB[k][tilstand][nm] = dict(krit_tilt=kt, del_flate_tilt20=f20)
        print(f"({k}) {tilstand:8s} ψ {psi:+d}: første spegling ved tilt " +
              ', '.join(f"{nm} {DB[k][tilstand][nm]['krit_tilt']}" for nm in AUGE) +
              f"   | del av skjermflata med spegelbilete ved 20°, nominelt: {100*DB[k][tilstand]['nominell']['del_flate_tilt20']:.2f} %")
UT['B_spegel'] = DB


# =====================================================================================================
# C · Skjermlys i stemning, polygonformelen (eigen kode)
# =====================================================================================================
def E_poly(yp, hp, psi, opn, Q, nq):
    """Lamberts polygonformel, lx per cd/m² frå kordeflata. Q (m,3), nq mottakarnormal."""
    e, v = e_(psi), v_(psi)
    c0 = np.array([0.0, yp, hp]) + RC * e
    out = np.zeros(len(Q))
    for a0, a1 in opn:
        V = np.array([c0 + a0 * X1 - HV * v, c0 + a1 * X1 - HV * v, c0 + a1 * X1 + HV * v, c0 + a0 * X1 + HV * v])
        Dv = V[None] - Q[:, None]
        Dv /= np.linalg.norm(Dv, axis=2, keepdims=True)
        s = np.zeros(len(Q))
        for i in range(4):
            a, b = Dv[:, i], Dv[:, (i + 1) % 4]
            cr = np.cross(a, b); ncr = np.linalg.norm(cr, axis=1)
            s += np.arctan2(ncr, (a * b).sum(1)) * (cr @ nq) / ncr
        foran = (Q - c0) @ e > 0
        out += np.where(foran, 0.5 * np.abs(s), 0.0)
    return out


hdr('C · Skjermlys i arbeid og stemning, polygonformelen')
xs_, zs_ = np.meshgrid(SX0 + (np.arange(55) + .5) / 55 * (SX1 - SX0), SZ0 + (np.arange(32) + .5) / 32 * (SZ1 - SZ0))
SKJ = np.c_[xs_.ravel(), np.full(xs_.size, SY - 1e-4), zs_.ravel()]
tx_, ty_ = np.meshgrid(GX7, GY5)
TASK = np.c_[tx_.ravel(), ty_.ravel(), np.zeros(tx_.size)]
DC = {}
for k in 'ab':
    c = KONF[k]
    A = sum(b - a for a, b in c['opn']) * 2 * HV
    Lw = c['eta_motor'] * c['Phi_json'] / (math.pi * A)
    Et = E_poly(c['yp'], c['hp'], -20, c['opn'], TASK, np.array([0, 0, 1.0])) * Lw
    Ew = E_poly(c['yp'], c['hp'], -20, c['opn'], SKJ, np.array([0, -1.0, 0])) * Lw
    Em = E_poly(c['yp'], c['hp'], -95, c['opn'], SKJ, np.array([0, -1.0, 0])) * Lw * 0.25
    DC[k] = dict(L_opning_arbeid=Lw, Et_snitt=Et.mean(), U0=Et.min() / Et.mean(), E_skjerm_arbeid=Ew.mean(), E_skjerm_arbeid_maks=Ew.max(),
                 E_skjerm_stemning=Em.mean(), E_skjerm_stemning_maks=Em.max(), L_opning_stemning=0.25 * Lw)
    print(f"({k}) L {Lw:.0f} cd/m²  oppgåve {Et.mean():.1f} lx U0 {Et.min()/Et.mean():.4f}  skjerm arbeid {Ew.mean():.1f} lx (maks {Ew.max():.0f})  skjerm stemning (25 %) {Em.mean():.1f} lx (maks {Em.max():.0f}), L_opning {0.25*Lw:.0f} cd/m²")
UT['C_skjerm'] = DC

# =====================================================================================================
# D · Leppe langs opninga (stiv del av røyret, loddrett i arbeid), fint utval, lambertsk og MC
# =====================================================================================================
hdr('D · Leppe: brukarside (skjerming) og veggside (skjermlys). Φ for 500 lx, U0, skjermlys, synleg for 8 auge')


def kjelde_punkt(yp, hp, psi, opn, du=0.01, nv=60):
    e, v = e_(psi), v_(psi)
    c0 = np.array([0.0, yp, hp]) + RC * e
    P, dA = [], []
    sv = ((np.arange(nv) + .5) / nv * 2 - 1) * HV
    for a0, a1 in opn:
        nu = max(1, round((a1 - a0) / du))
        su = a0 + (np.arange(nu) + .5) / nu * (a1 - a0)
        U, V = np.meshgrid(su, sv, indexing='ij')
        P.append(c0 + U.ravel()[:, None] * X1 + V.ravel()[:, None] * v)
        dA.append(np.full(U.size, (a1 - a0) / nu * 2 * HV / nv))
    return np.vstack(P), np.concatenate(dA), e


def lepper_for(yp, hp, psi, psi_arb, hb, hv_, opn):
    """Lepper som heng loddrett ned frå kantane når røyret står i ψ_arb; i ψ er dei rotert med røyret."""
    xh = max(abs(a) for o in opn for a in o) + 0.01
    O = np.array([0.0, yp, hp])
    out = []
    dpsi = math.radians(psi - psi_arb)
    # retninga −z i arbeidsstilling, uttrykt i (e, v) ved ψ_arb, og så ført over til ψ
    ea, va = e_(psi_arb), v_(psi_arb)
    dl_loc = np.array([-ea[2], -va[2]])                          # (−ẑ·e, −ẑ·v)
    e, v = e_(psi), v_(psi)
    dl = dl_loc[0] * e + dl_loc[1] * v
    for sg, h in ((-1, hb), (1, hv_)):                           # −v: brukarside, +v: veggside (i arbeid)
        if h > 0:
            out.append((O + RC * e + sg * HV * v, dl, h, xh))
    return out


def E_kv(P, N, dA, Q, nq, lepper, bit=150):
    out = np.zeros(len(Q))
    for i in range(0, len(Q), bit):
        q = Q[i:i + bit]
        d = q[None] - P[:, None]
        r2 = (d * d).sum(-1); r = np.sqrt(r2)
        ce = (d * N[:, None, :]).sum(-1) / r
        cr = -(d @ nq) / r
        w = np.where((ce > 0) & (cr > 0), ce * cr / r2, 0.0)
        for E0, dl, h, xh in lepper:
            m = np.cross(X1, dl)
            a = (P - E0) @ m
            b = (q - E0) @ m
            kr = a[:, None] * b[None, :] < 0
            with np.errstate(divide='ignore', invalid='ignore'):
                s = np.where(kr, a[:, None] / (a[:, None] - b[None, :]), 0.0)
            X = P[:, None, :] + s[..., None] * d
            al = (X - E0) @ dl
            w[kr & (al > 0) & (al < h) & (np.abs(X[..., 0]) < xh)] = 0.0
        out[i:i + bit] = (w * dA[:, None]).sum(0)
    return out


def synleg_lepper(P, N, lepper):
    res = {}
    for nm, E in AUGE.items():
        E = np.asarray(E, float)
        fr = ((E - P) * N).sum(1) > 0
        if lepper and fr.any():
            Pf = P[fr]
            bl = np.zeros(len(Pf), bool)
            for E0, dl, h, xh in lepper:
                m = np.cross(X1, dl)
                a = (Pf - E0) @ m; b = (E - E0) @ m
                kr = a * b < 0
                with np.errstate(divide='ignore', invalid='ignore'):
                    s = a / (a - b)
                X = Pf + s[:, None] * (E - Pf)
                al = (X - E0) @ dl
                bl |= kr & (al > 0) & (al < h) & (np.abs(X[:, 0]) < xh)
            fr_frac = float((~bl).mean() * fr.mean())
        else:
            fr_frac = float(fr.mean())
        res[nm] = fr_frac
    return res


xs3, ys3 = np.meshgrid(TX0 + (np.arange(5) + .5) / 5 * (TX1 - TX0), TY0 + (np.arange(3) + .5) / 3 * (TY1 - TY0))
TASK_EN = np.c_[xs3.ravel(), ys3.ravel(), np.zeros(xs3.size)]
SKJ_G = SKJ[::8]
DD = {}
for k in 'ab':
    c = KONF[k]
    A = sum(b - a for a, b in c['opn']) * 2 * HV
    DD[k] = []
    t1 = time.time()
    for psi in (-20, -15, -10, -5, 0):
        P, dA, e = kjelde_punkt(c['yp'], c['hp'], psi, c['opn'])
        N = np.tile(e, (len(P), 1))
        for hb in (0.0, 0.005, 0.010, 0.020):
            for hv_ in (0.0, 0.010, 0.020, 0.030):
                lp = lepper_for(c['yp'], c['hp'], psi, psi, hb, hv_, c['opn'])
                Et = E_kv(P, N, dA, TASK, np.array([0, 0, 1.0]), lp)
                Ee = E_kv(P, N, dA, TASK_EN, np.array([0, 0, 1.0]), lp)
                Es = E_kv(P, N, dA, SKJ_G, np.array([0, -1.0, 0]), lp)
                L500 = 500 / Et.mean()
                vis = synleg_lepper(P, N, lp)
                DD[k].append(dict(psi=psi, h_brukar_mm=hb * 1000, h_vegg_mm=hv_ * 1000, Phi=500 * math.pi * A / (c['eta_motor'] * Et.mean()),
                                  U0=Et.min() / Et.mean(), U0_EN=Ee.min() / Ee.mean(), E_skjerm=Es.mean() * L500, E_skjerm_maks=Es.max() * L500,
                                  synleg={nm: f for nm, f in vis.items() if f > 0}))
    print(f"({k}) {len(DD[k])} kombinasjonar ({time.time()-t1:.0f} s)")
    ref = next(r for r in DD[k] if r['psi'] == -20 and r['h_brukar_mm'] == 0 and r['h_vegg_mm'] == 0)
    ok = [r for r in DD[k] if not r['synleg'] and r['U0'] >= 0.40]
    print(f"    ref ψ −20 utan leppe: Φ {ref['Phi']:.0f}  U0 {ref['U0']:.3f}  skjerm {ref['E_skjerm']:.0f} lx   synleg for {list(ref['synleg'])}")
    for r in sorted(ok, key=lambda r: r['E_skjerm'])[:6]:
        print(f"    skjerma for alle 8, U0 ≥ 0,4: ψ {r['psi']:+3d} leppe brukar {r['h_brukar_mm']:2.0f} mm vegg {r['h_vegg_mm']:2.0f} mm:  Φ {r['Phi']:5.0f} ({100*(r['Phi']/ref['Phi']-1):+5.1f} %)  U0 {r['U0']:.2f}/{r['U0_EN']:.2f}  skjerm {r['E_skjerm']:4.0f} lx (maks {r['E_skjerm_maks']:4.0f})")
    okm = [r for r in ok if r['h_vegg_mm'] == 0]
    if okm:
        r = min(okm, key=lambda r: r['Phi'])
        print(f"    berre brukarleppe, minst Φ: ψ {r['psi']:+d} {r['h_brukar_mm']:.0f} mm  Φ {r['Phi']:.0f} ({100*(r['Phi']/ref['Phi']-1):+.1f} %)  skjerm {r['E_skjerm']:.0f} lx")
UT['D_leppe'] = DD

# leppe i MC (bakvegg-LED): same kombinasjonar for den beste i lambertsk modell + nokre faste
hdr('D2 · Leppe i Monte Carlo (LED på bakveggen): skjermlys og U0')
DD2 = {}
for k in 'ab':
    c = KONF[k]
    P, D, w = EXIT[(k, 'bakvegg')]
    DD2[k] = []
    for psi in (-20, -15, -10, -5, 0):
        G, H = til_global(P, D, c['yp'], c['hp'], psi)
        for hb in (0.0, 0.010, 0.020):
            for hv_ in (0.0, 0.010, 0.020, 0.030):
                lp = lepper_for(c['yp'], c['hp'], psi, psi, hb, hv_, c['opn'])
                bl = leppe_blokk(G, H, lp) if lp else np.zeros(len(G), bool)
                r = arbeidstal(G[~bl], H[~bl], w)
                DD2[k].append(dict(psi=psi, h_brukar_mm=hb * 1000, h_vegg_mm=hv_ * 1000, Phi=500 / r['Em'], U0_7x5=r['U0_7x5'], U0_EN=r['U0_EN'],
                                   E_skjerm=r['Es'] * 500 / r['Em']))
    for r in DD2[k]:
        if r['h_brukar_mm'] in (0, 20):
            print(f"({k}) ψ {r['psi']:+3d} brukar {r['h_brukar_mm']:2.0f} vegg {r['h_vegg_mm']:2.0f} mm: Φ {r['Phi']:5.0f}  U0 {r['U0_7x5']:.2f}/{r['U0_EN']:.2f}  skjerm {r['E_skjerm']:4.0f} lx")
UT['D2_leppe_mc'] = DD2


def rein(o):
    if isinstance(o, dict):
        return {str(k): rein(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [rein(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


json.dump(rein(UT), open(os.path.join(HER, 'fotometri_kontroll.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f'\nskrive fotometri_kontroll.json ({time.time()-T0:.0f} s)')
