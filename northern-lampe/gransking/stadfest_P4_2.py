# -*- coding: utf-8 -*-
"""Motprov nr. 2 av P4: luminans mot auga i arbeid, (c) prisme, alpha 0.

Uavhengig av prisme.py og stadfest_P4_1.py:
- Deterministisk sporing med forgreining (R og T vert begge følgde med vekt, ingen Monte Carlo), 3D-retning,
  flater utan x-del i normalen. Stabel i numba.
- Profil bygd på nytt frå motor.optikk(FINAL): tann k frå e_k til e_k+1, tau i midten (kart: s ved botnen).
- Mattering på to måtar: (A) som granskaren og motoren: gauss sigma på profilvinkelen ved plata (augesida),
  på eit jamt vinkelgitter med gaussvekter; (B) fysisk på oversida: gauss på vinkelen der strålen går ut av
  oversida mot LED, integrert analytisk (erf) over intervallet som treffer stripa gjennom renna.
Køyr: PYTHONIOENCODING=utf-8 python stadfest_P4_2.py
"""
import os, sys, math, json, time
import numpy as np
from numba import njit
from scipy.special import erf

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

# ---- 1) motoren: kva er 10,6? ----
I, dd, r, S = mo.I_mot(B, 0.0, fe.EYES)
A = L * bp
cvec = ((fe.EYES - np.array([0, ys, zs])) @ np.array([0, 0, -1.0])) / np.linalg.norm(fe.EYES - np.array([0, ys, zs]), axis=-1)
Lb = (I * ~fe.screen_block(S, fe.EYES)).sum(0) / (A * np.clip(cvec, 0.05, None))
stro = mo.STRO * O['eta'] / (math.pi * A)
PHI_M = 432.737
gam = np.degrees(np.arctan2(fe.EYES[:, 1] - ys, -(fe.EYES[:, 2] - zs)))
UT['motor'] = dict(Lb_cdm2=(Lb * PHI_M).tolist(), stro_cdm2=stro * PHI_M, L_mot_cdm2=(mo.L_mot(B, 0.0, fe.EYES) * PHI_M).tolist(),
                   auge_vinkel_fra_loddrett_deg=(-gam).tolist(), vifte_deg=[math.degrees(O['th1']), math.degrees(O['th2'])])
print('motor', UT['motor'], flush=True)

# ---- 2) profil ----
phi_i = np.arcsin(np.sin(O['ph']) / n)
S_BOT = d * np.tan(O['ph']) + tp * np.tan(phi_i)


def profil(slipp=False, p=0.0008):
    K = int(round(bp / p)); p = bp / K
    e = -bp / 2 + np.arange(K + 1) * p
    m = (e[:-1] + e[1:]) / 2
    tau = np.interp(m, S_BOT, O['tau']); th = np.interp(m, S_BOT, O['th']); pi_ = np.interp(m, S_BOT, phi_i)
    beta = 0.5 * (np.maximum(th * np.sign(tau), 0) + np.abs(pi_)) if slipp else np.zeros(K)
    V = [(e[0], ZB)]
    for k in range(K):
        ta, be = abs(tau[k]), beta[k]
        h = p * math.tan(ta) / (1 + math.tan(ta) * math.tan(be))
        if tau[k] > 0:
            V += [(e[k] + h * math.tan(be), ZB + h), (e[k + 1], ZB)]
        else:
            V += [(e[k + 1] - h * math.tan(be), ZB + h), (e[k + 1], ZB)]
    V += [(bp / 2, d), (-bp / 2, d), (-bp / 2, ZB)]          # endeflate, overside, endeflate (lukka)
    V = np.array(V)
    SA, SB = V[:-1], V[1:]
    ok = np.linalg.norm(SB - SA, axis=1) > 1e-13
    return dict(SA=np.ascontiguousarray(SA[ok]), SB=np.ascontiguousarray(SB[ok]), hmax=float(V[:, 1].max() - ZB),
                tau=tau, beta=beta, K=K)


@njit(cache=False)
def spor(s0, z0, x0, dx0, ds0, dz0, SA, SB, nn, w, Lh, zc, cw, dtop, sig, modus):
    """Sum av vekt som endar på LED-stripa. modus 0: skarp. modus 1: gauss sig på vinkelen ut av oversida (erf)."""
    M = 256
    st = np.empty((M, 9))
    sp = 0
    st[0, 0] = s0; st[0, 1] = z0; st[0, 2] = x0; st[0, 3] = dx0; st[0, 4] = ds0; st[0, 5] = dz0
    st[0, 6] = 0; st[0, 7] = 1.0; st[0, 8] = -1
    sp = 1
    tot = 0.0
    nfeil = 0
    while sp > 0:
        sp -= 1
        s = st[sp, 0]; z = st[sp, 1]; x = st[sp, 2]; dx = st[sp, 3]; ds = st[sp, 4]; dz = st[sp, 5]
        med = int(st[sp, 6]); wt = st[sp, 7]; last = int(st[sp, 8])
        for b in range(200):
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
                    nfeil += 1
                    break
                if dz < 0.0:
                    hor = math.sqrt(ds * ds + dz * dz)
                    if modus == 0:
                        t5 = (zc - z) / dz
                        if abs(s + t5 * ds) < cw:
                            t0 = -z / dz
                            if abs(s + t0 * ds) <= w / 2 and abs(x + t0 * dx) <= Lh:
                                tot += wt
                    else:
                        # vinkel i s-z-planet frå loddrett opp: tan(psi) = ds / (-dz)
                        psi = math.atan2(ds, -dz)
                        # treff: |s + (z - zc) tan psi'| < cw  og |s + z tan psi'| <= w/2  (z er høgda over LED, her z)
                        a1 = (-cw - s) / (z - zc); b1 = (cw - s) / (z - zc)
                        a2 = (-w / 2 - s) / z; b2 = (w / 2 - s) / z
                        lo = max(a1, a2); hi = min(b1, b2)
                        if hi > lo:
                            pl = math.atan(lo); ph = math.atan(hi)
                            q = 0.5 * (math.erf((ph - psi) / (math.sqrt(2.0) * sig)) - math.erf((pl - psi) / (math.sqrt(2.0) * sig)))
                            # x-krav ved midtvinkelen
                            t0 = -z / dz
                            if abs(x + t0 * dx) <= Lh:
                                tot += wt * q
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
            # transmisjon på stabelen, refleksjon vidare her
            if R < 1.0 and wt * (1 - R) > 1e-6 and sp < M:
                ct = math.sqrt(k2)
                tx = rr * dx; ts = rr * ds + (rr * ci - ct) * Ns; tz = rr * dz + (rr * ci - ct) * Nz
                q = math.sqrt(tx * tx + ts * ts + tz * tz)
                st[sp, 0] = s; st[sp, 1] = z; st[sp, 2] = x; st[sp, 3] = tx / q; st[sp, 4] = ts / q; st[sp, 5] = tz / q
                st[sp, 6] = 1 - med; st[sp, 7] = wt * (1 - R); st[sp, 8] = g
                sp += 1
            wt = wt * R
            if wt < 1e-6:
                break
            ds = ds + 2.0 * ci * Ns; dz = dz + 2.0 * ci * Nz
            q = math.sqrt(dx * dx + ds * ds + dz * dz); dx /= q; ds /= q; dz /= q
            last = g
    return tot, nfeil


@njit(cache=False)
def bunt(P, D, X, SA, SB, nn, w, Lh, zc, cw, dtop, sig, modus, RES):
    nf = 0
    for i in range(P.shape[0]):
        a, f = spor(P[i, 0], P[i, 1], X[i], D[i, 0], D[i, 1], D[i, 2], SA, SB, nn, w, Lh, zc, cw, dtop, sig, modus)
        RES[i] = a; nf += f
    return nf


def profilL(Pr, eye, xt, w, sig_deg=4.0, matt='auge', ds_=0.0001, gstep=0.25, s0=-bp / 2, s1=bp / 2):
    """L/L_LED langs s (x = xt) frå auga. matt: 'ingen', 'auge' (gauss ved plata, augesida), 'overside' (gauss ved utgang oppover)."""
    el = np.array([eye[0], ys - eye[1], zs - eye[2]])
    zq = ZB + Pr['hmax'] + 0.0005
    sc = np.arange(s0 + ds_ / 2, s1, ds_)
    if matt == 'auge':
        gg = np.radians(np.arange(-3 * sig_deg, 3 * sig_deg + 1e-9, gstep))
        wg = np.exp(-0.5 * (gg / math.radians(sig_deg)) ** 2); wg /= wg.sum()
    else:
        gg = np.zeros(1); wg = np.ones(1)
    ss = np.repeat(sc, len(gg)); G = np.tile(gg, len(sc))
    D = np.c_[np.full(len(ss), xt - el[0]), ss - el[1], np.full(len(ss), zq - el[2])]
    D /= np.linalg.norm(D, axis=1, keepdims=True)
    cg, sg = np.cos(G), np.sin(G)
    D[:, 1], D[:, 2] = D[:, 1] * cg + D[:, 2] * sg, -D[:, 1] * sg + D[:, 2] * cg
    P = np.ascontiguousarray(np.c_[ss, np.full(len(ss), zq)])
    RES = np.zeros(len(ss))
    nf = bunt(P, np.ascontiguousarray(D), np.full(len(ss), xt), Pr['SA'], Pr['SB'], n, w, L / 2, ZC, CW, d,
              math.radians(sig_deg), 1 if matt == 'overside' else 0, RES)
    prof = (RES.reshape(len(sc), len(gg)) * wg[None]).sum(1)
    return sc, prof, nf


def tal(sc, prof):
    h = sc[1] - sc[0]
    k1 = max(1, int(round(0.001 / h))); k10 = int(round(0.01 / h))
    m1 = np.convolve(prof, np.ones(k1) / k1, mode='valid'); m10 = np.convolve(prof, np.ones(k10) / k10, mode='valid')
    return dict(topp_1mm=float(m1.max()), s_topp_cm=float(sc[np.argmax(m1) + k1 // 2] * 100), topp_1cm=float(m10.max()),
                snitt=float(prof.mean()))


PROF = {'loddrett': profil(False), 'slipp': profil(True)}
for k, Pr in PROF.items():
    print(k, 'segment', len(Pr['SA']), 'hmax mm', round(Pr['hmax'] * 1e3, 3), flush=True)

# ---- kontroll: flat plate, loddrett opp frå s 0 -> T to flater med fleire sprett (teori 0,9257) ----
FL = np.array([(-bp / 2, ZB), (bp / 2, ZB), (bp / 2, d), (-bp / 2, d), (-bp / 2, ZB)])
tf, _ = spor(0.0, ZB + 0.001, 0.0, 0.0, 0.0, -1.0, np.ascontiguousarray(FL[:-1]), np.ascontiguousarray(FL[1:]), n, 0.005, L / 2, ZC, CW, d, 0.07, 0)
R0 = ((n - 1) / (n + 1)) ** 2
UT['kontroll_flat'] = dict(T_spora=tf, T_teori=(1 - R0) ** 2 / (1 - R0 ** 2))
# kontroll: designstråle framover-lova attgjeven bakover: frå s_bot ved φ 45°, ut-vinkel θ(φ) -> skal treffe LED-lina
j = np.argmin(abs(O['ph'] - math.radians(45)))
Pr = PROF['loddrett']
sb_ = S_BOT[j]; th_ = O['th'][j]
zq_ = ZB + Pr['hmax'] + 0.0005
# start under rilla, gå bakover langs designstrålen (opp, mot -s når θ>0)
s_st = sb_ + (zq_ - ZB) * math.tan(th_) * 0.999
UT['kontroll_design'] = []
for off in (-0.3, -0.2, -0.1, 0.0, 0.1):     # mm forskyving langs s, for å treffe midt på fasetten
    tt, _ = spor(s_st + off * 1e-3, zq_, 0.0, 0.0, -math.sin(th_), -math.cos(th_), Pr['SA'], Pr['SB'], n, 0.0012, L / 2, ZC, CW, d, 0.07, 0)
    UT['kontroll_design'].append(round(tt, 4))
print('kontroll', UT['kontroll_flat'], 'designstråle φ45 (stripe 1,2 mm):', UT['kontroll_design'], f'{time.time()-t0:.1f}s', flush=True)
if 'test' in sys.argv:
    sys.exit()

# Phi for 500 lx: granskaren sin (prisme.json, nærfelt) og motoren sin
PH = {('loddrett', 0.005): 459.351, ('loddrett', 0.010): 482.377, ('slipp', 0.005): 431.586, ('slipp', 0.010): 454.545}
eye = fe.EYES[0]
UT['linje_x0'] = {}
_ = profilL(PROF['loddrett'], eye, 0.0, 0.005, matt='ingen', ds_=0.004)          # kompiler
for pn in ('loddrett', 'slipp'):
    for w in (0.005, 0.010):
        LL = 1 / (math.pi * w * L)
        for matt, kw in (('ingen', dict(ds_=0.00002)), ('auge', dict(ds_=0.0001, gstep=0.25)), ('overside', dict(ds_=0.00002))):
            t1 = time.time()
            sc, prof, nf = profilL(PROF[pn], eye, 0.0, w, matt=matt, **kw)
            q = tal(sc, prof)
            out = dict(q, **{k + '_cdm2': q[k] * LL * PH[(pn, w)] for k in ('topp_1mm', 'topp_1cm', 'snitt')},
                       **{k + '_cdm2_motorPhi': q[k] * LL * PHI_M for k in ('topp_1mm', 'topp_1cm', 'snitt')}, feil=int(nf))
            UT['linje_x0'][f'{pn}_w{int(w*1000)}_{matt}'] = out
            print(pn, w, matt, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in out.items()}, f'{time.time()-t1:.1f}s', flush=True)
            if pn == 'loddrett' and w == 0.005 and matt == 'auge':
                # kvar på plata: snitt per cm
                bins = np.arange(-8, 8.01, 1)
                hcm = np.histogram(sc * 100, bins=bins, weights=prof)[0] / np.histogram(sc * 100, bins=bins)[0]
                UT['per_cm_loddrett_w5_auge_cdm2'] = (hcm * LL * PH[(pn, w)]).round(1).tolist()
                print('per cm (s -8..8):', UT['per_cm_loddrett_w5_auge_cdm2'], flush=True)

# ---- heile plata (alle x) frå midtauga, 4° på augesida, 5 mm: same definisjon som L_mot (snitt over flata) ----
UT['heile_plata'] = {}
for pn in ('loddrett', 'slipp'):
    w = 0.005; LL = 1 / (math.pi * w * L)
    XG = np.linspace(-0.27, 0.27, 7)
    sn = []; t1m = []
    for xt in XG:
        sc, prof, nf = profilL(PROF[pn], eye, xt, w, matt='auge', ds_=0.0002, gstep=0.5)
        q = tal(sc, prof); sn.append(q['snitt']); t1m.append(q['topp_1mm'])
    UT['heile_plata'][pn] = dict(x=XG.tolist(), snitt_per_x_cdm2=(np.array(sn) * LL * PH[(pn, w)]).round(1).tolist(),
                                 snitt_cdm2=float(np.mean(sn) * LL * PH[(pn, w)]), topp_1mm_per_x_cdm2=(np.array(t1m) * LL * PH[(pn, w)]).round(0).tolist())
    print('heile plata', pn, UT['heile_plata'][pn], flush=True)

UT['tid_s'] = time.time() - t0
print(json.dumps(UT, ensure_ascii=False))
print(f'ferdig {time.time()-t0:.0f} s')
