# -*- coding: utf-8 -*-
"""Motprov nr. 1 av P4 (luminans mot auga i arbeid, (c) prisme).

1) Motoren: dekomponer L_mot(FINAL, α 0, EYES) i lova-delen (G i augeretninga) og STRO-delen.
2) Eigen strålesporar, ikkje henta frå prisme.py: plata som lukka polygon i snittet (s fram, z ned frå LED-aksen),
   flat overside z = d, botn z = d + tp, 200 riller à 0,8 mm under botnen, τ(s) frå motor.optikk() lagt der strålen
   går ut av botnen, stigevegg loddrett eller med slipp β = ½(maks(θ·sgn τ, 0) + |φ_i|). Brute force over alle
   segment, Snell + Fresnel på vektorform i 3D, Monte Carlo R/T. Renneopning |s| < 8 mm ved z 5 mm, LED-stripe |s| <= w/2.
3) Bakover frå auga: punkt i planet rett under rillene, gauss σ 4° på profilvinkelen der (motorpremissen), stratifisert.
4) Framover frå LED (uavhengig av bakover): illuminans i eit 6 × 6 cm vindauge ved midtauga, mot bakover-integralet.
Køyr: PYTHONIOENCODING=utf-8 python stadfest_P4_1.py   (om lag 1-2 min)
"""
import os, sys, math, json, time
import numpy as np
from numba import njit

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
UT = {}

# ---------- 1) motoren ----------
I, dd, r, S = mo.I_mot(B, 0.0, fe.EYES)
m = np.array([0.0, 0.0, -1.0])
c = ((fe.EYES - np.array([0, ys, zs])) @ m) / np.linalg.norm(fe.EYES - np.array([0, ys, zs]), axis=-1)
A = L * bp
Lb = (I * ~fe.screen_block(S, fe.EYES)).sum(0) / (A * np.clip(c, 0.05, None))
stro = mo.STRO * O['eta'] / (math.pi * A)
Lm = mo.L_mot(B, 0.0, fe.EYES)
PHI_M = 432.737
UT['motor'] = dict(Lb_per_lm=Lb.tolist(), stro_per_lm=stro, L_mot_per_lm=Lm.tolist(), L_cdm2=(Lm * PHI_M).tolist(),
                   stro_cdm2=stro * PHI_M, siktvinkel_deg=np.degrees(np.arccos(c)).tolist())
print('motor:', UT['motor'], flush=True)

# ---------- 2) profil ----------
phi_i = np.arcsin(np.sin(O['ph']) / n)
S_BOT = d * np.tan(O['ph']) + tp * np.tan(phi_i)


def profil(slipp=False, p=0.0008):
    K = int(round(bp / p)); p = bp / K
    e = -bp / 2 + np.arange(K + 1) * p
    mm = (e[:-1] + e[1:]) / 2
    tau = np.interp(mm, S_BOT, O['tau']); th = np.interp(mm, S_BOT, O['th']); pi_ = np.interp(mm, S_BOT, phi_i)
    beta = 0.5 * (np.maximum(th * np.sign(tau), 0) + np.abs(pi_)) if slipp else np.zeros(K)
    P = [(e[0], ZB)]
    for k in range(K):
        t_, b_ = abs(tau[k]), beta[k]
        h = p * math.tan(t_) / (1 + math.tan(t_) * math.tan(b_))
        if tau[k] > 0:
            P += [(e[k] + h * math.tan(b_), ZB + h), (e[k + 1], ZB)]
        else:
            P += [(e[k + 1] - h * math.tan(b_), ZB + h), (e[k + 1], ZB)]
    # fjern (e, ZB)-punkt mellom to stigeveggar som møtest (τ<0 så τ>0): ingen flate der
    Q = [P[0]]
    for i in range(1, len(P) - 1):
        a_, b2, c_ = P[i - 1], P[i], P[i + 1]
        if abs(b2[1] - ZB) < 1e-12 and a_[1] > ZB and c_[1] > ZB and abs(a_[0] - b2[0]) < 1e-9 and abs(c_[0] - b2[0]) < 1e-9:
            continue
        Q.append(b2)
    Q.append(P[-1])
    # lukk: høgre endeflate opp, overside, venstre endeflate ned
    Q += [(bp / 2, d), (-bp / 2, d), (-bp / 2, ZB)]
    Q = np.array(Q)
    SA, SB = Q[:-1], Q[1:]
    ok = np.linalg.norm(SB - SA, axis=1) > 1e-12
    return dict(SA=np.ascontiguousarray(SA[ok]), SB=np.ascontiguousarray(SB[ok]), hmax=float(Q[:, 1].max() - ZB), tau=tau, beta=beta)


@njit(cache=False)
def spor(s, z, x, dx, ds, dz, SA, SB, w, Lh, nn, zc, cw):
    """Bakover: 1 om strålen endar på LED-stripa. Kode 2 = for mange sprett."""
    med = 0; last = -1
    for b in range(80):
        tb = 1e30; g = -1
        for k in range(SA.shape[0]):
            if k == last:
                continue
            ax = SA[k, 0]; az = SA[k, 1]; ex = SB[k, 0] - ax; ez = SB[k, 1] - az
            den = ds * ez - dz * ex
            if abs(den) < 1e-300:
                continue
            wx = ax - s; wz = az - z
            t = (wx * ez - wz * ex) / den
            u = (wx * dz - wz * ds) / den
            if t > 1e-12 and u >= 0.0 and u <= 1.0 and t < tb:
                tb = t; g = k
        if g < 0:
            if med == 1:
                return -1
            if dz < 0.0:
                t5 = (zc - z) / dz
                if abs(s + t5 * ds) < cw:
                    t0 = -z / dz
                    if abs(s + t0 * ds) <= w / 2 and abs(x + t0 * dx) <= Lh:
                        return 1
            return 0
        s += tb * ds; z += tb * dz; x += tb * dx
        ex = SB[g, 0] - SA[g, 0]; ez = SB[g, 1] - SA[g, 1]; ll = math.sqrt(ex * ex + ez * ez)
        Ns = -ez / ll; Nz = ex / ll
        ci = -(ds * Ns + dz * Nz)
        if ci < 0.0:
            Ns = -Ns; Nz = -Nz; ci = -ci
        n1 = 1.0 if med == 0 else nn
        n2 = nn if med == 0 else 1.0
        rr = n1 / n2
        k2 = 1.0 - rr * rr * (1.0 - ci * ci)
        if k2 < 0.0:
            R = 1.0
        else:
            ct = math.sqrt(k2)
            rs = ((n1 * ci - n2 * ct) / (n1 * ci + n2 * ct)) ** 2
            rp = ((n1 * ct - n2 * ci) / (n1 * ct + n2 * ci)) ** 2
            R = 0.5 * (rs + rp)
        if np.random.random() < R:
            ds = ds + 2.0 * ci * Ns; dz = dz + 2.0 * ci * Nz
        else:
            ct = math.sqrt(k2)
            dx = rr * dx; ds = rr * ds + (rr * ci - ct) * Ns; dz = rr * dz + (rr * ci - ct) * Nz
            med = 1 - med
        q = math.sqrt(dx * dx + ds * ds + dz * dz); dx /= q; ds /= q; dz /= q
        last = g
    return 2


@njit(cache=False)
def bunt(P, Dv, X, SA, SB, w, Lh, nn, zc, cw, seed, RES):
    np.random.seed(seed)
    for i in range(P.shape[0]):
        RES[i] = spor(P[i, 0], P[i, 1], X[i], Dv[i, 0], Dv[i, 1], Dv[i, 2], SA, SB, w, Lh, nn, zc, cw)


def luminans(Pr, eye, xt, w=0.005, sig_deg=4.0, ns=320, per=600, seed=1, s0=-bp / 2, s1=bp / 2):
    """Treffbrøk (del av L_LED) som funksjon av sikta s, x = xt, α 0. Stratifisert gauss på profilvinkelen."""
    rng = np.random.default_rng(seed)
    el = np.array([eye[0], ys - eye[1], zs - eye[2]])         # α 0: s = ys - y, z = zs - z
    zq = ZB + Pr['hmax'] + 0.0005
    sb = np.linspace(s0, s1, ns + 1)
    st = rng.uniform(np.repeat(sb[:-1], per), np.repeat(sb[1:], per))
    Dl = np.c_[np.full(len(st), xt - el[0]), st - el[1], np.full(len(st), zq - el[2])]
    Dl /= np.linalg.norm(Dl, axis=1, keepdims=True)
    if sig_deg > 0:
        from scipy.stats import norm
        q = (np.tile(np.arange(per), ns) + rng.random(len(st))) / per
        g = math.radians(sig_deg) * norm.ppf(q)
        cg, sg = np.cos(g), np.sin(g)
        Dl[:, 1], Dl[:, 2] = Dl[:, 1] * cg + Dl[:, 2] * sg, -Dl[:, 1] * sg + Dl[:, 2] * cg
    P = np.ascontiguousarray(np.c_[st, np.full(len(st), zq)])
    RES = np.zeros(len(st), np.int64)
    bunt(P, np.ascontiguousarray(Dl), np.full(len(st), xt), Pr['SA'], Pr['SB'], w, L / 2, n, ZC, CW, seed, RES)
    feil = float((RES < 0).mean() + (RES == 2).mean())
    prof = (RES == 1).reshape(ns, per).mean(1)
    sc = (sb[:-1] + sb[1:]) / 2
    h = sc[1] - sc[0]
    m1 = np.convolve(prof, np.ones(2) / 2, mode='same')
    m10 = np.convolve(prof, np.ones(20) / 20, mode='same')
    return dict(sc=sc, prof=prof, topp_1mm=float(m1.max()), s_topp_cm=float(sc[np.argmax(m1)] * 100), topp_1cm=float(m10[10:-10].max()),
                snitt=float(prof.mean()), feil=feil, vinkel_deg=float(np.degrees(math.atan2(el[1] - 0.05, el[2] - zq))))


PH = dict(loddrett=459.35, slipp=431.59)          # Φ for 500 lx frå prisme.json (3D, 5 mm), til samanlikning
W = 0.005
LL = 1 / (math.pi * W * L)
PROF = {k: profil(k == 'slipp') for k in ('loddrett', 'slipp')}
for k, Pr in PROF.items():
    print(k, 'segment', len(Pr['SA']), 'hmax mm', round(Pr['hmax'] * 1000, 3), 'β maks', round(math.degrees(Pr['beta'].max()), 1), flush=True)

SYN = [(fe.EYES[0], 0.0), (fe.EYES[1], -0.15), (fe.EYES[2], 0.15), (fe.EYES[0], 0.25)]
UT['bakover'] = {}
LAGRA = {}
KUN_KRYSS = 'kryss' in sys.argv
for pn, Pr in ({} if KUN_KRYSS else PROF).items():
    for sgd in (0.0, 4.0):
        rad = []
        for vi, (eye, xt) in enumerate(SYN):
            t1 = time.time()
            rr = luminans(Pr, eye, xt, sig_deg=sgd, seed=11 + vi)
            LAGRA[(pn, sgd, vi)] = rr
            out = {k: v for k, v in rr.items() if k not in ('sc', 'prof')}
            for k in ('topp_1mm', 'topp_1cm', 'snitt'):
                out[k + '_cdm2'] = rr[k] * LL * PH[pn]
                out[k + '_cdm2_motorPhi'] = rr[k] * LL * PHI_M
            out['syn'] = vi
            rad.append(out)
            print(pn, f'σ {sgd:.0f}', vi, {k: round(v, 4) if isinstance(v, float) else v for k, v in out.items()}, f'{time.time()-t1:.1f}s', flush=True)
        UT['bakover'][f'{pn}_sigma{sgd:.0f}'] = rad

# heile plata (alle x) frå midtauga og sideauga, σ 4°: same definisjon som L_mot (snitt over flata)
UT['heile_plata'] = {}
XG = np.linspace(-0.29, 0.29, 9)
for pn, Pr in ({} if KUN_KRYSS else PROF).items():
    for ei, eye in enumerate(fe.EYES):
        sn = []; tp1 = []
        for j, xt in enumerate(XG):
            rr = luminans(Pr, eye, xt, sig_deg=4.0, ns=160, per=300, seed=100 + 10 * ei + j)
            sn.append(rr['snitt']); tp1.append(rr['topp_1mm'])
        UT['heile_plata'][f'{pn}_auge{ei}'] = dict(x=XG.tolist(), snitt_per_x_cdm2=(np.array(sn) * LL * PH[pn]).round(1).tolist(),
                                                  snitt_cdm2=float(np.mean(sn) * LL * PH[pn]), topp_1mm_maks_cdm2=float(max(tp1) * LL * PH[pn]))
        print('heile plata', pn, ei, UT['heile_plata'][f'{pn}_auge{ei}'], flush=True)


# ---------- 4) framover: E ved midtauga frå LED, mot bakover-integralet ----------
@njit(cache=False)
def fram(N, w, SA, SB, nn, zc, cw, seed, OUT):
    """LED -> plate. OUT: s, z, x, dx, ds, dz, kode (0 ut i luft nedover, anna = ikkje med)."""
    np.random.seed(seed)
    for i in range(N):
        s0 = (np.random.random() - 0.5) * w
        u1 = np.random.random(); u2 = np.random.random()
        st = math.sqrt(u1); dz = math.sqrt(1.0 - u1)
        dx = st * math.cos(2 * math.pi * u2); ds = st * math.sin(2 * math.pi * u2)
        OUT[i, 6] = 9
        if dz < 1e-9:
            continue
        t5 = zc / dz; s = s0 + t5 * ds
        if abs(s) >= cw:
            continue
        z = zc; x = t5 * dx
        med = 0; last = -1; ok = False
        for b in range(80):
            tb = 1e30; g = -1
            for k in range(SA.shape[0]):
                if k == last:
                    continue
                ax = SA[k, 0]; az = SA[k, 1]; ex = SB[k, 0] - ax; ez = SB[k, 1] - az
                den = ds * ez - dz * ex
                if abs(den) < 1e-300:
                    continue
                wx = ax - s; wz = az - z
                t = (wx * ez - wz * ex) / den
                u = (wx * dz - wz * ds) / den
                if t > 1e-12 and u >= 0.0 and u <= 1.0 and t < tb:
                    tb = t; g = k
            if g < 0:
                ok = med == 0
                break
            s += tb * ds; z += tb * dz; x += tb * dx
            ex = SB[g, 0] - SA[g, 0]; ez = SB[g, 1] - SA[g, 1]; ll = math.sqrt(ex * ex + ez * ez)
            Ns = -ez / ll; Nz = ex / ll
            ci = -(ds * Ns + dz * Nz)
            if ci < 0.0:
                Ns = -Ns; Nz = -Nz; ci = -ci
            n1 = 1.0 if med == 0 else nn
            n2 = nn if med == 0 else 1.0
            rr = n1 / n2
            k2 = 1.0 - rr * rr * (1.0 - ci * ci)
            if k2 < 0.0:
                R = 1.0
            else:
                ct = math.sqrt(k2)
                rs = ((n1 * ci - n2 * ct) / (n1 * ci + n2 * ct)) ** 2
                rp = ((n1 * ct - n2 * ci) / (n1 * ct + n2 * ci)) ** 2
                R = 0.5 * (rs + rp)
            if np.random.random() < R:
                ds = ds + 2.0 * ci * Ns; dz = dz + 2.0 * ci * Nz
            else:
                ct = math.sqrt(k2)
                dx = rr * dx; ds = rr * ds + (rr * ci - ct) * Ns; dz = rr * dz + (rr * ci - ct) * Nz
                med = 1 - med
            q = math.sqrt(dx * dx + ds * ds + dz * dz); dx /= q; ds /= q; dz /= q
            last = g
        if ok and dz > 0.0:
            OUT[i, 0] = s; OUT[i, 1] = z; OUT[i, 2] = x; OUT[i, 3] = dx; OUT[i, 4] = ds; OUT[i, 5] = dz; OUT[i, 6] = 0


def E_auge_fram(Pr, N, sig_deg=4.0, seed=7, he=0.03):
    OUT = np.zeros((N, 7))
    fram(N, W, Pr['SA'], Pr['SB'], n, ZC, CW, seed, OUT)
    o = OUT[OUT[:, 6] == 0]
    rng = np.random.default_rng(seed)
    x0 = (rng.random(len(o)) - 0.5) * L
    xe = x0 + o[:, 2]
    keep = np.abs(xe) <= L / 2                                   # kinn i endane
    ds, dz = o[:, 4], o[:, 5]
    g = rng.normal(0, math.radians(sig_deg), len(o)); cg, sg = np.cos(g), np.sin(g)
    ds, dz = ds * cg + dz * sg, -ds * sg + dz * cg
    # global ramme α 0: y = ys - s, Z = zs - z; retning (dx, -ds, -dz)
    Py = ys - o[:, 0]; Pz = zs - o[:, 1]
    Vx, Vy, Vz = o[:, 3], -ds, -dz
    ey = fe.EYES[0]
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (ey[1] - Py) / Vy
    hit = keep & (Vy < 0) & (t > 0)
    X = xe + t * Vx; Z = Pz + t * Vz
    hit &= (np.abs(X - ey[0]) < he) & (np.abs(Z - ey[2]) < he)
    ende = (np.abs(o[:, 0]) > bp / 2 - 1e-7) & (o[:, 1] < ZB + 1e-7)
    k = lambda m: float((hit & m).sum() / N / (2 * he) ** 2)
    return dict(alt=k(np.ones(len(o), bool)), underside=k(~ende), endeflate_pluss=k(ende & (o[:, 0] > 0)), endeflate_minus=k(ende & (o[:, 0] < 0)),
                s_hist_underside=np.histogram(o[hit & ~ende, 0] * 100, bins=np.arange(-8, 8.01, 1))[0].tolist())


def E_auge_bak(Pr, sig_deg=4.0, nx=13, he=0.03, s0=-bp / 2, s1=bp / 2):
    """∫ L cos(normal +y) dΩ over plata frå midtauga, med L frå bakoversporing (x-gitter × s)."""
    eye = fe.EYES[0]
    Et = 0.0
    xs = np.linspace(-L / 2, L / 2, nx + 1); xc = (xs[:-1] + xs[1:]) / 2; dxw = xs[1] - xs[0]
    for j, xt in enumerate(xc):
        rr = luminans(Pr, eye, xt, sig_deg=sig_deg, ns=int(round((s1 - s0) / 0.001)), per=300, seed=300 + j, s0=s0, s1=s1)
        sc = rr['sc']; ds_ = sc[1] - sc[0]
        # flatepunkt i global ramme (planet under rillene ≈ plateplanet), dA = dx·ds
        Py = ys - sc; Pz = zs - (ZB + Pr['hmax'] + 0.0005)
        v = np.c_[np.full(len(sc), xt - eye[0]), Py - eye[1], np.full(len(sc), Pz - eye[2])]
        rr2 = (v ** 2).sum(1); rn = np.sqrt(rr2)
        cos_e = v[:, 1] / rn                                    # mot normalen +y på augeflata
        cos_p = (Pz - eye[2]) / rn                              # plata vender ned
        Et += (rr['prof'] * LL * cos_e * cos_p / rr2 * dxw * ds_).sum()
    return float(Et)                                            # lx per LED-lm


UT['kryss'] = {}
for pn in ('loddrett',):
    Pr = PROF[pn]
    t1 = time.time()
    Ef = E_auge_fram(Pr, 4_000_000)
    Eb = E_auge_bak(Pr)
    Eb2 = E_auge_bak(Pr, s0=-0.10, s1=0.12)
    UT['kryss'][pn] = dict(E_fram_lx_per_lm=Ef, E_bak_plata_lx_per_lm=Eb, E_bak_utvida_lx_per_lm=Eb2,
                          forhold_underside=Ef['underside'] / Eb, forhold_alt=Ef['alt'] / Eb2)
    print('kryss framover/bakover', pn, UT['kryss'][pn], f'{time.time()-t1:.1f}s', flush=True)

UT['tid_s'] = time.time() - t0
print(json.dumps({k: v for k, v in UT.items() if k != 'bakover'}, ensure_ascii=False))
print(f'ferdig {time.time()-t0:.0f} s')


# ---------- diagnose (køyr med argumentet diag): kvar på plata kjem E frå, framover mot bakover ----------
if 'diag' in sys.argv:
    Pr = PROF['loddrett']
    eye = fe.EYES[0]
    # bakover: bidrag til E per 5 mm av sikta s (start-planet), summert over x
    nx = 13
    xs_ = np.linspace(-L / 2, L / 2, nx + 1); xc = (xs_[:-1] + xs_[1:]) / 2; dxw = xs_[1] - xs_[0]
    s0, s1 = -0.10, 0.12
    bins = np.arange(-0.10, 0.1201, 0.01)
    Eb = np.zeros(len(bins) - 1)
    for j, xt in enumerate(xc):
        rr = luminans(Pr, eye, xt, sig_deg=4.0, ns=220, per=300, seed=500 + j, s0=s0, s1=s1)
        sc = rr['sc']; ds_ = sc[1] - sc[0]
        Py = ys - sc; Pz = zs - (ZB + Pr['hmax'] + 0.0005)
        v = np.c_[np.full(len(sc), xt - eye[0]), Py - eye[1], np.full(len(sc), Pz - eye[2])]
        r2 = (v ** 2).sum(1); rn = np.sqrt(r2)
        dE = rr['prof'] * LL * (v[:, 1] / rn) * ((Pz - eye[2]) / rn) / r2 * dxw * ds_
        Eb += np.histogram(sc, bins=bins, weights=dE)[0]
    print('bakover E per 1 cm sikta s (start-planet):', {f'{a*100:+.0f}': round(float(e), 5) for a, e in zip(bins[:-1], Eb)}, 'sum', round(float(Eb.sum()), 5))
    # bakover med treffpunkt: same, men logg kvar strålen først treffer plata
    # framover: vindauge ±1 cm og ±3 cm, og s ved utgang projisert til start-planet langs strålen
    OUT = np.zeros((6_000_000, 7))
    fram(len(OUT), W, Pr['SA'], Pr['SB'], n, ZC, CW, 21, OUT)
    o = OUT[OUT[:, 6] == 0]
    rng = np.random.default_rng(21)
    xe = (rng.random(len(o)) - 0.5) * L + o[:, 2]
    keep = np.abs(xe) <= L / 2
    ds, dz = o[:, 4], o[:, 5]
    g = rng.normal(0, math.radians(4.0), len(o)); cg, sg = np.cos(g), np.sin(g)
    ds, dz = ds * cg + dz * sg, -ds * sg + dz * cg
    Py = ys - o[:, 0]; Pz = zs - o[:, 1]
    Vx, Vy, Vz = o[:, 3], -ds, -dz
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (eye[1] - Py) / Vy
    X = xe + t * Vx; Z = Pz + t * Vz
    zq = ZB + Pr['hmax'] + 0.0005
    s_proj = o[:, 0] + (zq - o[:, 1]) * ds / dz                 # utgangsstrålen forlengd ned til start-planet
    for he in (0.01, 0.03):
        hit = keep & (Vy < 0) & (t > 0) & (np.abs(X - eye[0]) < he) & (np.abs(Z - eye[2]) < he)
        Ef = hit.sum() / len(OUT) / (2 * he) ** 2
        h1 = np.histogram(s_proj[hit], bins=bins)[0] / len(OUT) / (2 * he) ** 2
        h2 = np.histogram(o[hit, 0], bins=bins)[0] / len(OUT) / (2 * he) ** 2
        print(f'framover ±{he*100:.0f} cm: E', round(float(Ef), 5), 'treff', int(hit.sum()))
        print('   per 1 cm, projisert til start-planet:', {f'{a*100:+.0f}': round(float(e), 5) for a, e in zip(bins[:-1], h1)})
        print('   per 1 cm, utgangsstad på plata:     ', {f'{a*100:+.0f}': round(float(e), 5) for a, e in zip(bins[:-1], h2)})
