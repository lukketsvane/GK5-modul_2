# -*- coding: utf-8 -*-
"""Motbevisar 1 for funn P1 (stigeveggane i prismeplata, konsept c).

Uavhengig av gransking/prisme.py: eigen, enklare strålesporar i numpy (ingen numba, ingen import av prisme.py,
felles.py eller motor.py). Designlova er skriven opp att frå optikk() i form04/motor.py.
Kvar stråle: lambertsk frå lina (2D eller 3D, breidd w), renneklipp, Snell+Fresnel på oversida, gjennom plata,
inn i tanna under, så lokal sporing mot fasett og stigevegg i eiga og nabocellene (Fresnel med MC-val).
Variant 'usynleg': stigeveggane er tekne bort (strålen går rett gjennom), for å skilje stigeveggverknaden
frå 3D-verknaden (skeive strålar) i 3D.
"""
import math, json, os, sys
import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
n = 1.49
BP, D, TP, YS, ZS, Y1, Y2 = 0.16, 0.05, 0.003, 0.22, 0.70, 0.02, 0.43
CW, ZC = 0.008, 0.005
ZB = D + TP
TH1, TH2 = math.atan((YS - Y2) / ZS), math.atan((YS - Y1) / ZS)
P = 0.0008


def lov(npts=6001):
    phm = math.atan(BP / 2 / D)
    ph = np.linspace(-phm, phm, npts)
    Fs = (np.sin(ph) + math.sin(phm)) / (2 * math.sin(phm))
    th = np.arctan(math.tan(TH1) + Fs * (math.tan(TH2) - math.tan(TH1)))
    pi_ = np.arcsin(np.sin(ph) / n)
    tau = np.arctan2(n * np.sin(pi_) - np.sin(th), n * np.cos(pi_) - np.cos(th))
    sb = D * np.tan(ph) + TP * np.tan(pi_)
    return sb, tau, th, pi_


def celler(slipp=False):
    sb, tau_l, th_l, pi_l = lov()
    K = int(round(BP / P)); e = -BP / 2 + np.arange(K + 1) * P; m = (e[:-1] + e[1:]) / 2
    tau = np.interp(m, sb, tau_l); th = np.interp(m, sb, th_l); pi_ = np.interp(m, sb, pi_l)
    beta = 0.5 * (np.maximum(th * np.sign(tau), 0) + np.abs(pi_)) if slipp else np.zeros(K)
    mt = np.tan(np.abs(tau)); h = P * mt / (1 + mt * np.tan(beta))
    # segment: riser R0->R1, fasett F0->F1 (punkt i (s, z))
    pos = tau > 0
    R0 = np.where(pos[:, None], np.c_[e[:-1], np.full(K, ZB)], np.c_[e[1:] - h * np.tan(beta), ZB + h])
    R1 = np.where(pos[:, None], np.c_[e[:-1] + h * np.tan(beta), ZB + h], np.c_[e[1:], np.full(K, ZB)])
    F0 = np.where(pos[:, None], np.c_[e[:-1] + h * np.tan(beta), ZB + h], np.c_[e[:-1], np.full(K, ZB)])
    F1 = np.where(pos[:, None], np.c_[e[1:], np.full(K, ZB)], np.c_[e[1:] - h * np.tan(beta), ZB + h])
    return dict(K=K, e=e, tau=tau, h=h, beta=beta, R0=R0, R1=R1, F0=F0, F1=F1)


def fresnel_brot(d, N, n1, n2, rng):
    """d (m,3) innfall, N (m,3) normal mot innfallssida. MC: refleksjon eller brot. Returnerer ny d og 'brote'."""
    ci = -(d * N).sum(1)
    r = n1 / n2
    k = 1 - r * r * (1 - ci * ci)
    tir = k < 0
    ct = np.sqrt(np.clip(k, 0, None))
    rs = ((n1 * ci - n2 * ct) / (n1 * ci + n2 * ct)) ** 2
    rp = ((n1 * ct - n2 * ci) / (n1 * ct + n2 * ci)) ** 2
    R = np.where(tir, 1.0, 0.5 * (rs + rp))
    refl = rng.random(len(d)) < R
    dr = d + 2 * ci[:, None] * N
    dt = r * d + (r * ci - ct)[:, None] * N
    out = np.where(refl[:, None], dr, dt)
    out /= np.linalg.norm(out, axis=1, keepdims=True)
    return out, ~refl


def spor(C, N=400_000, w=0.0, d3=True, usynleg=False, seed=1):
    rng = np.random.default_rng(seed)
    s0 = (rng.random(N) - 0.5) * w
    if d3:
        u1, u2 = rng.random(N), rng.random(N)
        st = np.sqrt(u1); d = np.c_[st * np.cos(2 * np.pi * u2), st * np.sin(2 * np.pi * u2), np.sqrt(1 - u1)]
    else:
        sp = 2 * rng.random(N) - 1; d = np.c_[np.zeros(N), sp, np.sqrt(1 - sp * sp)]
    ok = (d[:, 2] > 1e-9)
    s5 = s0 + ZC * d[:, 1] / np.maximum(d[:, 2], 1e-12)
    ok &= np.abs(s5) < CW                                  # renna
    st_ = s0 + D * d[:, 1] / np.maximum(d[:, 2], 1e-12)
    samla = ok.mean()
    forbi = ok & (np.abs(st_) > BP / 2)                    # forbi platekanten (går ned utan plate)
    th_f = np.arctan2(d[forbi, 1], d[forbi, 2])
    ok &= np.abs(st_) <= BP / 2                            # treffer plata
    idx = np.where(ok)[0]
    d = d[idx]; st_ = st_[idx]
    # overside
    Nz = np.tile([0, 0, -1.0], (len(d), 1))
    d, br = fresnel_brot(d, Nz, 1.0, n, rng)
    keep = br
    d = d[keep]; st_ = st_[keep]
    m = len(d)
    s = st_ + TP * d[:, 1] / d[:, 2]
    z = np.full(m, ZB - 1e-7)
    inne = np.ones(m, bool)
    cell = np.clip(np.floor((s + BP / 2) / P).astype(int), 0, C['K'] - 1)
    traff = np.zeros(m, bool)
    ferdig = np.zeros(m, bool); kode = np.zeros(m, int)     # 1 ut i luft, 2 attende i plata / anna, 3 for mange
    for steg in range(40):
        a = np.where(~ferdig)[0]
        if len(a) == 0:
            break
        sa, za, da, ca = s[a], z[a], d[a], cell[a]
        best = np.full(len(a), np.inf); bnorm = np.zeros((len(a), 2)); briser = np.zeros(len(a), bool); bcell = ca.copy()
        for off in (-2, -1, 0, 1, 2):
            cc = np.clip(ca + off, 0, C['K'] - 1)
            for typ, (A, B) in (('r', (C['R0'], C['R1'])), ('f', (C['F0'], C['F1']))):
                Ax, Az = A[cc, 0], A[cc, 1]; ex, ez = B[cc, 0] - Ax, B[cc, 1] - Az
                ln = np.hypot(ex, ez)
                den = da[:, 1] * ez - da[:, 2] * ex
                with np.errstate(divide='ignore', invalid='ignore'):
                    wx, wz = Ax - sa, Az - za
                    t = (wx * ez - wz * ex) / den
                    u = (wx * da[:, 2] - wz * da[:, 1]) / den
                hit = (ln > 1e-12) & (np.abs(den) > 1e-15) & (t > 1e-10) & (u >= 0) & (u <= 1) & (t < best)
                best = np.where(hit, t, best)
                nn = np.c_[-ez, ex] / np.maximum(ln, 1e-30)[:, None]
                bnorm = np.where(hit[:, None], nn, bnorm)
                briser = np.where(hit, typ == 'r', briser)
                bcell = np.where(hit, cc, bcell)
        # innanfrå og på veg opp mot z = ZB: inn i plata, til oversida (Fresnel/TIR), ned att til ZB (lysleiar)
        ia = inne[a]
        with np.errstate(divide='ignore', invalid='ignore'):
            tc = np.where(ia & (da[:, 2] < 0), (ZB - za) / da[:, 2], np.inf)
        opp = ia & (tc < best) & (tc > 0)
        if opp.any():
            ao = a[opp]; do = da[opp]
            so = sa[opp] + ((D - za[opp]) / do[:, 2]) * do[:, 1]
            kant = np.abs(so) > BP / 2
            Nt = np.tile([0, 0, 1.0], (len(ao), 1))
            dn, brote = fresnel_brot(do, Nt, n, 1.0, rng)
            gaar_ut = brote | kant
            kode[ao[gaar_ut]] = 2; ferdig[ao[gaar_ut]] = True
            bl = ~gaar_ut
            if bl.any():
                ab = ao[bl]; db = dn[bl]
                sn = so[bl] + (ZB - D) / db[:, 2] * db[:, 1]
                ute = np.abs(sn) > BP / 2
                kode[ab[ute]] = 2; ferdig[ab[ute]] = True
                ab = ab[~ute]; db = db[~ute]; sn = sn[~ute]
                s[ab] = sn; z[ab] = ZB - 1e-7; d[ab] = db
                cell[ab] = np.clip(np.floor((sn + BP / 2) / P).astype(int), 0, C['K'] - 1)
        ingen = ~np.isfinite(best) & ~opp
        luft_ut = ingen & ~ia
        kode[a[luft_ut]] = 1; ferdig[a[luft_ut]] = True
        feil = ingen & ia
        kode[a[feil]] = 2; ferdig[a[feil]] = True
        g = np.isfinite(best) & ~opp
        if not g.any():
            continue
        ag = a[g]; t = best[g]
        s[ag] = sa[g] + t * da[g, 1]; z[ag] = za[g] + t * da[g, 2]
        traff[ag] |= briser[g]
        cell[ag] = bcell[g]
        N3 = np.c_[np.zeros(g.sum()), bnorm[g]]
        dg = da[g]
        sg = np.sign((N3 * dg).sum(1)); N3 = -N3 * np.where(sg == 0, 1, sg)[:, None]   # mot innfallssida
        n1 = np.where(inne[ag], n, 1.0); n2 = np.where(inne[ag], 1.0, n)
        dn = np.empty_like(dg); brote = np.empty(len(ag), bool)
        for v1, v2 in ((n, 1.0), (1.0, n)):
            mm = n1 == v1
            if mm.any():
                dn[mm], brote[mm] = fresnel_brot(dg[mm], N3[mm], v1, v2, rng)
        d[ag] = dn
        vart_luft = brote & inne[ag]
        inne[ag] = np.where(brote, ~inne[ag], inne[ag])
        if usynleg:
            kode[ag[vart_luft]] = 1; ferdig[ag[vart_luft]] = True
    kode[~ferdig] = 3
    ut = kode == 1
    th = np.arctan2(d[:, 1], d[:, 2])
    ned = ut & (d[:, 2] > 0)
    iv = ned & (th >= TH1 - math.radians(0.5)) & (th <= TH2 + math.radians(0.5))
    W = 1.0 / N
    thd = np.degrees(th[ned])
    fv = (th_f >= TH1 - math.radians(0.5)) & (th_f <= TH2 + math.radians(0.5))
    return dict(samla=float(samla), forbi_kanten=float(len(th_f) * W), eta_ned=float(ned.sum() * W), i_vifta=float(iv.sum() * W), utanfor=float((ned & ~iv).sum() * W),
                ned_traff_stigevegg=float((ned & traff).sum() / max(ned.sum(), 1)),
                stigevegg_i_vifta=float((iv & traff).sum() * W), stigevegg_utanfor=float((ned & ~iv & traff).sum() * W),
                kvantil_2_5_97_5=[float(np.percentile(thd, 2.5)), float(np.percentile(thd, 97.5))],
                lobe_stigevegg_median_abs_deg=float(np.median(np.abs(np.degrees(th[ned & traff & ~iv])))) if (ned & traff & ~iv).any() else None,
                attende=float((kode == 2).sum() * W), uferdig=float((kode == 3).sum() * W))


def ytste_tann():
    """Handrekning i snittet for den ytste tanna: kor stor del av fasetten får lys, kor stor del av utgangsstrålane treffer neste vegg."""
    sb, tau_l, th_l, pi_l = lov()
    out = {}
    for ph_deg in (30.0, 40.0, 50.0, 57.99):
        i = np.argmin(np.abs(np.degrees(np.arctan((sb - TP * np.tan(pi_l)) / D)) - ph_deg))
        tau, th, pi_ = tau_l[i], th_l[i], pi_l[i]
        hp = math.tan(tau)
        # inngang i toppen av tanna ved a (0..1), stråle med helling tan(pi): treff fasetten ved u = (hp + a/tan(pi)... )
        k_in = 1 / math.tan(pi_)
        u_lo = hp / (k_in + hp)                                  # a = 0
        k_ut = 1 / math.tan(th)
        u_vegg = 1 - hp / (hp + k_ut)                             # utgangsstrålar frå u > u_vegg treff neste vegg
        # treffdel blant innlyste punkt (jamn fordeling i a gjev jamn i u på [u_lo, 1])
        frac = max(0.0, 1 - max(u_vegg, u_lo)) / (1 - u_lo)
        # vidare: brot inn i neste tann gjennom loddrett vegg og ut gjennom fasetten (same τ)
        inn = math.asin(math.cos(th) / n)                         # mot vegg-normalen (vassrett)
        phi2 = math.pi / 2 - inn                                  # frå loddrett
        th_ut = tau + math.asin(n * math.sin(phi2 - tau))
        out[f'phi_{ph_deg:.0f}'] = dict(tau_deg=math.degrees(tau), h_over_p=hp, theta_deg=math.degrees(th), innlyst_ovste=1 - u_lo,
                                        utgang_i_vegg_ovste=1 - u_vegg, treffdel=frac, lobe_deg=math.degrees(th_ut))
    return out


if __name__ == '__main__':
    UT = {'ytste_tann_hand': ytste_tann()}
    print(json.dumps(UT['ytste_tann_hand'], ensure_ascii=False))
    for nm, kw, sl in (('2D_w0_loddrett', dict(w=0.0, d3=False), False), ('2D_w0_slipp', dict(w=0.0, d3=False), True),
                       ('2D_w0_usynleg', dict(w=0.0, d3=False, usynleg=True), False),
                       ('3D_w5_loddrett', dict(w=0.005, d3=True), False), ('3D_w5_slipp', dict(w=0.005, d3=True), True),
                       ('3D_w5_usynleg', dict(w=0.005, d3=True, usynleg=True), False)):
        r = spor(celler(sl), **kw)
        UT[nm] = r
        print(nm, json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}), flush=True)
