# -*- coding: utf-8 -*-
"""Motbevisar 2 for P1 (stigeveggane i prismeplata, konsept c).

Eigen strålesporar, uavhengig av prisme.py og stadfest_P1_1.py: plata er ein lukka polygon i snittet (s, z)
(flat overside, endekantar, sagtann under), kvar stråle testar ALLE segment kvar sprett (ingen gitteroppslag),
Snell på vektorform i 3D (normalane har ingen x-del), Fresnel med MC-val. Designlova skriven opp att frå optikk().
Kontrafaktisk «ideell stigevegg»: retninga ved FØRSTE utgang gjennom botnen (det designlova og motoren reknar med).
Skilnaden full spor minus første utgang er det stigeveggane gjer. U0/Φ: motoren sin eigen E_punkt med G bytt ut.
"""
import math, json, os, sys, time
import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
n = 1.49
BP, D, TP, YS, ZS, Y1, Y2 = 0.16, 0.05, 0.003, 0.22, 0.70, 0.02, 0.43
CW, ZC = 0.008, 0.005
ZB = D + TP
TH1, TH2 = math.atan((YS - Y2) / ZS), math.atan((YS - Y1) / ZS)
P = 0.0008
SIG = math.radians(4.0)


def lov(npts=6001):
    phm = math.atan(BP / 2 / D)
    ph = np.linspace(-phm, phm, npts)
    Fs = (np.sin(ph) + math.sin(phm)) / (2 * math.sin(phm))
    th = np.arctan(math.tan(TH1) + Fs * (math.tan(TH2) - math.tan(TH1)))
    pi_ = np.arcsin(np.sin(ph) / n)
    tau = np.arctan2(n * np.sin(pi_) - np.sin(th), n * np.cos(pi_) - np.cos(th))
    sb = D * np.tan(ph) + TP * np.tan(pi_)
    return sb, tau, th, pi_


def polygon(slipp=False):
    sb, tl, thl, pil = lov()
    K = int(round(BP / P)); e = -BP / 2 + np.arange(K + 1) * P; m = (e[:-1] + e[1:]) / 2
    tau = np.interp(m, sb, tl); th = np.interp(m, sb, thl); pi_ = np.interp(m, sb, pil)
    beta = 0.5 * (np.maximum(th * np.sign(tau), 0) + np.abs(pi_)) if slipp else np.zeros(K)
    pts = [(-BP / 2, D), (BP / 2, D), (BP / 2, ZB)]            # overside venstre->høgre, endekant høgre
    typ = [0, 1]
    # botn frå høgre mot venstre
    for k in range(K - 1, -1, -1):
        mt = math.tan(abs(tau[k])); h = P * mt / (1 + mt * math.tan(beta[k]))
        if tau[k] > 0:   # djup ende til venstre: frå (e[k+1],ZB) fasett ned til djupt punkt, så stigevegg opp til (e[k],ZB)
            pts.append((e[k] + h * math.tan(beta[k]), ZB + h)); typ.append(2)
            pts.append((e[k], ZB)); typ.append(3)
        else:            # djup ende til høgre: stigevegg ned frå (e[k+1],ZB), så fasett opp til (e[k],ZB)
            pts.append((e[k + 1] - h * math.tan(beta[k]), ZB + h)); typ.append(3)
            pts.append((e[k], ZB)); typ.append(2)
    pts.append((-BP / 2, D)); typ.append(1)
    # midten: to stigeveggar mot kvarandre i same s, slå saman (fjern felles botnpunkt)
    i = 0
    while i < len(typ) - 1:
        if typ[i] == 3 and typ[i + 1] == 3 and abs(pts[i + 1][1] - ZB) < 1e-12:
            del pts[i + 1]; del typ[i + 1]
        i += 1
    V = np.array(pts); T = np.array(typ)
    A, B = V[:-1], V[1:]
    ok = np.linalg.norm(B - A, axis=1) > 1e-12
    return A[ok], B[ok], T[ok], beta


def spor(A, B, T, N, w, tre_d, seed, maxb=40, chunk=4000):
    rng = np.random.default_rng(seed)
    s0 = (rng.random(N) - 0.5) * w
    if tre_d:
        u1, u2 = rng.random(N), rng.random(N)
        st = np.sqrt(u1); dz = np.sqrt(1 - u1); dx = st * np.cos(2 * np.pi * u2); ds = st * np.sin(2 * np.pi * u2)
    else:
        sp = 2 * rng.random(N) - 1; ds = sp; dz = np.sqrt(1 - sp * sp); dx = np.zeros(N)
    s = s0 + ZC * ds / dz
    inn = np.abs(s) < CW                                       # renneklipp
    Dv = np.c_[dx, ds, dz][inn]; Pp = np.c_[s, np.full(N, ZC)][inn]
    M = len(Dv)
    med = np.zeros(M, bool); last = np.full(M, -1); ris = np.zeros(M, bool); aktiv = np.ones(M, bool)
    forste = np.full((M, 3), np.nan)                           # retning ved første utgang gjennom botnen
    ex, ez = (B - A)[:, 0], (B - A)[:, 1]; L_ = np.hypot(ex, ez)
    Ns, Nz = -ez / L_, ex / L_
    for _ in range(maxb):
        idx = np.nonzero(aktiv)[0]
        if len(idx) == 0:
            break
        tb = np.full(len(idx), np.inf); gb = np.full(len(idx), -1)
        for c0 in range(0, len(idx), chunk):
            ii = idx[c0:c0 + chunk]
            s_, z_ = Pp[ii, 0:1], Pp[ii, 1:2]; d_s, d_z = Dv[ii, 1:2], Dv[ii, 2:3]
            den = d_s * ez[None] - d_z * ex[None]
            with np.errstate(divide='ignore', invalid='ignore'):
                wx = A[None, :, 0] - s_; wz = A[None, :, 1] - z_
                t = (wx * ez[None] - wz * ex[None]) / den
                u = (wx * d_z - wz * d_s) / den
            okk = (np.abs(den) > 1e-300) & (t > 1e-11) & (u >= -1e-12) & (u <= 1 + 1e-12)
            okk &= np.arange(len(A))[None] != last[ii][:, None]
            t = np.where(okk, t, np.inf)
            g = np.argmin(t, axis=1); tm = t[np.arange(len(ii)), g]
            tb[c0:c0 + len(ii)] = tm; gb[c0:c0 + len(ii)] = np.where(np.isfinite(tm), g, -1)
        ferdig = gb < 0
        aktiv[idx[ferdig]] = False
        idx, tb, gb = idx[~ferdig], tb[~ferdig], gb[~ferdig]
        if len(idx) == 0:
            break
        Pp[idx, 0] += tb * Dv[idx, 1]; Pp[idx, 1] += tb * Dv[idx, 2]
        ris[idx] |= T[gb] == 3
        d = Dv[idx]; Nv = np.c_[np.zeros(len(idx)), Ns[gb], Nz[gb]]
        flip = (d * Nv).sum(1) > 0; Nv[flip] *= -1
        ci = -(d * Nv).sum(1)
        n1 = np.where(med[idx], n, 1.0); n2 = np.where(med[idx], 1.0, n); r = n1 / n2
        k = 1 - r * r * (1 - ci * ci); tir = k < 0; ct = np.sqrt(np.clip(k, 0, None))
        rs = ((n1 * ci - n2 * ct) / (n1 * ci + n2 * ct)) ** 2; rp = ((n1 * ct - n2 * ci) / (n1 * ct + n2 * ci)) ** 2
        R = np.where(tir, 1.0, 0.5 * (rs + rp))
        refl = rng.random(len(idx)) < R
        dn = np.where(refl[:, None], d + 2 * ci[:, None] * Nv, r[:, None] * d + (r * ci - ct)[:, None] * Nv)
        dn /= np.linalg.norm(dn, axis=1, keepdims=True)
        # første utgang gjennom botnen (fasett eller stigevegg), frå plata ut i luft
        ut_botn = (~refl) & med[idx] & ((T[gb] == 2) | (T[gb] == 3)) & np.isnan(forste[idx, 0])
        forste[idx[ut_botn]] = dn[ut_botn]
        Dv[idx] = dn
        med[idx] = np.where(refl, med[idx], ~med[idx])
        last[idx] = gb
    return dict(N=N, Dv=Dv, Pp=Pp, med=med, aktiv=aktiv, ris=ris, forste=forste)


def budsjett(R):
    N = R['N']; Dv = R['Dv']; ferdig = ~R['aktiv'] & ~R['med']
    th = np.arctan2(Dv[:, 1], Dv[:, 2]); ned = ferdig & (Dv[:, 2] > 0)
    lo, hi = TH1 - math.radians(.5), TH2 + math.radians(.5)
    iv = ned & (th >= lo) & (th <= hi)
    F = R['forste']; har = ~np.isnan(F[:, 0])
    thf = np.arctan2(F[:, 1], F[:, 2])
    ivf = har & (F[:, 2] > 0) & (thf >= lo) & (thf <= hi)
    ris = R['ris']
    q = lambda m: [round(float(v), 1) for v in np.percentile(np.degrees(th[m]), [2.5, 50, 97.5])] if m.any() else None
    # soner etter utgangsstad
    sb = np.linspace(-BP / 2, BP / 2, 9); soner = []
    for a, b in zip(sb[:-1], sb[1:]):
        mm = ned & (R['Pp'][:, 0] >= a) & (R['Pp'][:, 0] < b)
        soner.append(round(float((mm & ris).sum() / max(mm.sum(), 1)), 3))
    return dict(samla=len(Dv) / N, ned=ned.sum() / N, i_vifta=iv.sum() / N, utanfor=(ned & ~iv).sum() / N,
                i_vifta_forste_utgang=ivf.sum() / N,
                stigevegg_tap_av_vifta=1 - iv.sum() / max(ivf.sum(), 1),
                del_ned_traff_stigevegg=(ned & ris).sum() / max(ned.sum(), 1),
                stigevegg_i_vifta=(iv & ris).sum() / N, stigevegg_utanfor=(ned & ~iv & ris).sum() / N,
                utanfor_utan_veggtreff=(ned & ~iv & ~ris).sum() / N,
                theta_2_5_50_97_5_alle=q(ned), theta_2_5_50_97_5_veggtreff=q(ned & ris),
                veggtreff_per_sone_8=soner, uferdige=int(R['aktiv'].sum()))


def G_frå(R, forste=False):
    """Profilfordeling ut (lm per LED-lm per radian), mattert som motoren (gauss 4° i θ)."""
    if forste:
        F = R['forste']; m = ~np.isnan(F[:, 0]); d = F[m]
    else:
        m = ~R['aktiv'] & ~R['med']; d = R['Dv'][m]
    th = np.arctan2(d[:, 1], d[:, 2])
    tg = np.radians(np.arange(-180, 180.01, 0.25))
    e = np.r_[tg - np.radians(0.125), tg[-1] + np.radians(0.125)]
    H, _ = np.histogram(th, e)
    G = H / R['N'] / np.radians(0.25)
    k = np.exp(-0.5 * (np.degrees(tg - tg[len(tg) // 2]) / 4.0) ** 2); k /= k.sum()
    G = np.convolve(G, k, mode='same')
    return tg, G


def motor_U0(tg, G):
    """Motorens eigen E_punkt (form04/motor.py) med G og η bytte ut. α = 0 (alfa_arb i tal.csv)."""
    sys.path.insert(0, os.path.join(os.path.dirname(HER), 'form04'))
    import motor as mo
    B = mo.FINAL
    O = dict(mo.optikk(B))
    eta = float(np.trapezoid(G, tg))
    O.update(tg=tg, G=G / eta, eta=eta)
    key = (B['bp'], B['d'], B['ys'], B['zs'], B['y1'], B['y2'])
    gammal = mo._opt[key]
    mo._opt[key] = O
    Et = mo.E_punkt(B, 0.0, mo.fe.TASK, np.array([0, 0, 1.0]))
    mo._opt[key] = gammal
    E0 = mo.E_punkt(B, 0.0, mo.fe.TASK, np.array([0, 0, 1.0]))
    return dict(U0=float(Et.min() / Et.mean()), Phi=float(mo.fe.E_TASK / Et.mean()), eta_G=eta,
                motor_U0=float(E0.min() / E0.mean()), motor_Phi=float(mo.fe.E_TASK / E0.mean()))


if __name__ == '__main__':
    T0 = time.time(); UT = {}
    for nm, sl, w, d3, N in (('2D_w0_loddrett', False, 0.0, False, 150_000), ('2D_w0_slipp', True, 0.0, False, 150_000),
                             ('3D_w5_loddrett', False, 0.005, True, 200_000), ('3D_w5_slipp', True, 0.005, True, 200_000)):
        A, B, T, beta = polygon(sl)
        R = spor(A, B, T, N, w, d3, seed=21)
        b = budsjett(R); b['beta_maks'] = float(np.degrees(beta.max())); b['segment'] = int(len(A))
        tg, G = G_frå(R); b['motor_E'] = motor_U0(tg, G)
        if not sl:
            tgf, Gf = G_frå(R, forste=True); b['motor_E_forste_utgang'] = motor_U0(tgf, Gf)
        UT[nm] = b
        print(nm, f'{time.time()-T0:.0f}s', json.dumps(b, ensure_ascii=False, default=float), flush=True)
    # lokal geometrisk kontroll, 2D, ytste tann (s -> +8 cm): lyst del av fasetten og del som treffer neste vegg
    sb, tl, thl, pil = lov()
    ta, pa, ha = tl[-1], pil[-1], thl[-1]
    lys = 1 - math.tan(ta) * math.tan(pa) / (1 + math.tan(ta) * math.tan(pa))
    hp = math.tan(ta)
    UT['ytste_tann'] = dict(tau=math.degrees(ta), pi=math.degrees(pa), theta=math.degrees(ha), h_over_p=hp,
                            lyst_ovste_del=lys, ovste_del_som_treff_vegg=1 / (1 + 1 / (math.tan(ta) * math.tan(ha))) if ha > 0 else 0)
    print('ytste tann', UT['ytste_tann'])
    print(f'ferdig {time.time()-T0:.0f}s')
