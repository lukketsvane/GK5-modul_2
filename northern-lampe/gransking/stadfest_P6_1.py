# -*- coding: utf-8 -*-
"""Motbevisar P6: eigen, uavhengig nærfeltsrekning av Φ for 500 lx i (c). Ingen import av prisme.py.
Strålar: lambertsk line (eller stripe), renne-klipp, flat overside (Snell+Fresnel), 3 mm PMMA, fasett τ(s_botn) frå designlova.
Variantar:
  V0  motoren sjølv (E_punkt, α 0)
  V2a fjernfelt, separabel modell som motoren (profilvinkel θ(φp), ξ uendra, vekt T1·T2·RISS) frå LED-aksen
  V2b same strålar, men ut frå staden på plata (nærfelt)
  V3a eksakt 3D-Snell gjennom fasetten, ut frå LED-aksen (fjern), ingen stigevegg, ingen RISS
  V3b eksakt 3D-Snell, nærfelt, ingen stigevegg
  V4b V3b + stigeveggar (loddrette): stråle som treffer stigevegg innanfrå eller ved utgang vert fjerna (øvre grense Φ)
"""
import math, os, sys, time
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HER)
T0 = time.time()
n = 1.49
L, BP, D, TP, YS, ZS, Y1, Y2 = 0.60, 0.16, 0.05, 0.003, 0.22, 0.70, 0.02, 0.43
SIG = math.radians(4.0); RISS = 0.95
CW, ZC = 0.008, 0.005
ZB = D + TP
TX, TY = np.linspace(-0.30, 0.30, 7), np.linspace(0.05, 0.40, 5)
K = 200; p = BP / K

# designlov
phm = math.atan(BP / 2 / D)
ph = np.linspace(-phm, phm, 8001)
th1, th2 = math.atan((YS - Y2) / ZS), math.atan((YS - Y1) / ZS)
F = (np.sin(ph) + math.sin(phm)) / (2 * math.sin(phm))
th = np.arctan(math.tan(th1) + F * (math.tan(th2) - math.tan(th1)))
pi_ = np.arcsin(np.sin(ph) / n)
tau = np.arctan2(n * np.sin(pi_) - np.sin(th), n * np.cos(pi_) - np.cos(th))
s_bot = D * np.tan(ph) + TP * np.tan(pi_)


def fres(ci, ct, n1, n2):
    rs = ((n1 * ci - n2 * ct) / (n1 * ci + n2 * ct)) ** 2
    rp = ((n1 * ct - n2 * ci) / (n1 * ct + n2 * ci)) ** 2
    return 1 - 0.5 * (rs + rp)


ti2 = pi_ - tau
Wdes = fres(np.cos(ph), np.cos(pi_), 1, n) * fres(np.cos(np.abs(ti2)), np.cos(np.abs(th - tau)), n, 1) * RISS
e = -BP / 2 + np.arange(K + 1) * p; m = (e[:-1] + e[1:]) / 2
tk = np.interp(m, s_bot, tau); hk = p * np.tan(np.abs(tk))


def celle(xl, yl, w, h=0.015):
    ix = np.rint((xl - TX[0]) / (TX[1] - TX[0])).astype(int); iy = np.rint((yl - TY[0]) / (TY[1] - TY[0])).astype(int)
    ok = (ix >= 0) & (ix < 7) & (iy >= 0) & (iy < 5)
    ok[ok] &= (np.abs(xl[ok] - TX[ix[ok]]) < h) & (np.abs(yl[ok] - TY[iy[ok]]) < h)
    E = np.bincount(iy[ok] * 7 + ix[ok], weights=w[ok], minlength=35)
    return E / (2 * h) ** 2


def kjor(N, w_led=0.0, seed=1, chunk=500000):
    rng = np.random.default_rng(seed)
    acc = {k: np.zeros(35) for k in ('V2a', 'V2b', 'V3a', 'V3b', 'V4b')}
    sona = {k: 0.0 for k in acc}
    for c0 in range(0, N, chunk):
        M = min(chunk, N - c0)
        x0 = (rng.random(M) - .5) * L; s0 = (rng.random(M) - .5) * w_led
        u1, u2 = rng.random(M), rng.random(M)
        st = np.sqrt(u1); dz = np.sqrt(1 - u1); dx = st * np.cos(2 * np.pi * u2); ds = st * np.sin(2 * np.pi * u2)
        ok = (dz > 1e-9) & (np.abs(s0 + ZC * ds / np.maximum(dz, 1e-12)) < CW)
        x0, s0, dx, ds, dz = x0[ok], s0[ok], dx[ok], ds[ok], dz[ok]
        s1 = s0 + D * ds / dz; x1 = x0 + D * dx / dz
        ok = np.abs(s1) <= BP / 2
        x0, s0, dx, ds, dz, s1, x1 = x0[ok], s0[ok], dx[ok], ds[ok], dz[ok], s1[ok], x1[ok]
        g = rng.normal(0, SIG, len(dz))
        # ---- separabel (motoren) ----
        php = np.arctan2(ds, dz); xi = np.arcsin(np.clip(dx, -1, 1))
        thp = np.interp(php, ph, th) + g
        wd = np.interp(php, ph, Wdes) / N
        ox, os_, oz = np.sin(xi), np.cos(xi) * np.sin(thp), np.cos(xi) * np.cos(thp)
        # fjern: frå LED-aksen (x0, 0, 0)
        tt = ZS / oz
        xl, yl = x0 + tt * ox, YS - tt * os_
        acc['V2a'] += celle(xl, yl, wd)
        sona['V2a'] += wd[(np.abs(xl) <= .3) & (yl >= .05) & (yl <= .40)].sum()
        # nær: ut frå plata
        r = 1 / n; ct = np.sqrt(1 - r * r * (1 - dz * dz))
        ix_, is_, iz_ = r * dx, r * ds, ct
        s2 = s1 + TP * is_ / iz_; x2 = x1 + TP * ix_ / iz_
        kinn = np.abs(x2) > L / 2
        tt = (ZS - ZB) / oz
        xl, yl = x2 + tt * ox, YS - s2 - tt * os_
        wb = np.where(kinn, 0, wd)
        acc['V2b'] += celle(xl, yl, wb)
        sona['V2b'] += wb[(np.abs(xl) <= .3) & (yl >= .05) & (yl <= .40)].sum()
        # ---- eksakt 3D ----
        T1 = fres(dz, ct, 1, n)
        tf = np.interp(s2, s_bot, tau)
        Ns, Nz = np.sin(tf), np.cos(tf)
        ci = is_ * Ns + iz_ * Nz
        kk = 1 - n * n * (1 - ci * ci)
        tir = kk < 0
        ct2 = np.sqrt(np.where(tir, 0, kk))
        tx = n * ix_; ts = n * is_ - (n * ci - ct2) * Ns; tz = n * iz_ - (n * ci - ct2) * Nz
        T2 = np.where(tir, 0, fres(np.clip(ci, 1e-9, 1), np.where(tir, 1, ct2), n, 1))
        w3 = T1 * T2 / N
        cg, sg = np.cos(g), np.sin(g)
        tsm, tzm = ts * cg + tz * sg, -ts * sg + tz * cg
        dn = tzm > 1e-6
        tt = np.where(dn, ZS / np.maximum(tzm, 1e-6), 0)
        xl, yl = x0 + tt * tx, YS - tt * tsm
        w3a = np.where(dn, w3, 0)
        acc['V3a'] += celle(xl, yl, w3a)
        sona['V3a'] += w3a[(np.abs(xl) <= .3) & (yl >= .05) & (yl <= .40)].sum()
        tt = np.where(dn, (ZS - ZB) / np.maximum(tzm, 1e-6), 0)
        xl, yl = x2 + tt * tx, YS - s2 - tt * tsm
        w3b = np.where(dn & ~kinn, w3, 0)
        acc['V3b'] += celle(xl, yl, w3b)
        sona['V3b'] += w3b[(np.abs(xl) <= .3) & (yl >= .05) & (yl <= .40)].sum()
        # ---- stigeveggar: rille k, fasett frå τ_k i midten av rilla ----
        k = np.clip(np.floor((s2 + BP / 2) / p).astype(int), 0, K - 1)
        tq, h = tk[k], hk[k]
        ek, ek1 = e[k], e[k + 1]
        pos = tq > 0
        # treffpunkt på fasetten (innanfrå)
        den_p = iz_ + h * is_ / p; den_n = iz_ - h * is_ / p
        t_p = h * (ek1 - s2) / p / np.where(np.abs(den_p) > 1e-12, den_p, 1e-12)
        t_n = h * (s2 - ek) / p / np.where(np.abs(den_n) > 1e-12, den_n, 1e-12)
        tin = np.where(pos, t_p, t_n)
        sf = s2 + tin * is_; zf = ZB + tin * iz_; xf = x2 + tin * ix_
        inn_ris = np.where(pos, sf < ek - 1e-12, sf > ek1 + 1e-12)
        Ns, Nz = np.sin(tq), np.cos(tq)
        ci = is_ * Ns + iz_ * Nz
        kk = 1 - n * n * (1 - ci * ci); tir = kk < 0
        ct2 = np.sqrt(np.where(tir, 0, kk))
        tx = n * ix_; ts = n * is_ - (n * ci - ct2) * Ns; tz = n * iz_ - (n * ci - ct2) * Nz
        T2 = np.where(tir, 0, fres(np.clip(ci, 1e-9, 1), np.where(tir, 1, ct2), n, 1))
        # neste stigevegg i den retninga strålen går
        kn = np.clip(k + 1, 0, K - 1); kp = np.clip(k - 1, 0, K - 1)
        hn = np.where((tk[kn] > 0) & (k + 1 < K), hk[kn], 0.0)
        hp = np.where((tk[kp] < 0) & (k - 1 >= 0), hk[kp], 0.0)
        with np.errstate(divide='ignore', invalid='ignore'):
            z_at_r = zf + (ek1 - sf) * tz / ts
            z_at_l = zf + (sf - ek) * tz / (-ts)
        ut_ris = np.where(pos & (ts > 0), z_at_r < ZB + hn, False) | np.where(~pos & (ts < 0), z_at_l < ZB + hp, False)
        w4 = T1 * T2 / N * ~(inn_ris | ut_ris | tir)
        tsm, tzm = ts * cg + tz * sg, -ts * sg + tz * cg
        dn = tzm > 1e-6
        tt = np.where(dn, (ZS - zf) / np.maximum(tzm, 1e-6), 0)
        xl, yl = xf + tt * tx, YS - sf - tt * tsm
        w4b = np.where(dn & (np.abs(xf) <= L / 2), w4, 0)
        acc['V4b'] += celle(xl, yl, w4b)
        sona['V4b'] += w4b[(np.abs(xl) <= .3) & (yl >= .05) & (yl <= .40)].sum()
        if c0 == 0:
            ned = (tz > 0) & ~tir
            print(f'  stigevegg: inn {inn_ris.mean():.3f}, ut {(ut_ris & ~inn_ris).mean():.3f} av strålar på plata, tir {tir.mean():.4f}')
    out = {}
    for k_, E in acc.items():
        out[k_] = dict(Phi=500 / E.mean(), U0=E.min() / E.mean(), sona=sona[k_], rad=np.round(E.reshape(5, 7).mean(1) / E.mean(), 2))
    return out


if __name__ == '__main__':
    sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form04'))
    import felles as fe
    import motor as mo
    B = mo.FINAL
    Et = mo.E_punkt(B, 0.0, fe.TASK, np.array([0, 0, 1.0]))
    Ef = Et.reshape(5, 7) if len(Et) == 35 else Et
    print(f'V0 motor: Phi {500 / Et.mean():.1f}  U0 {Et.min() / Et.mean():.3f}  eta {mo.eta(B):.4f}  rad {np.round(Ef.mean(1) / Et.mean(), 2) if Ef.ndim == 2 else ""}')
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000000
    for w_led in (0.0, 0.005):
        R = kjor(N, w_led)
        print(f'w {w_led * 1000:.0f} mm, N {N}:')
        for k_, v in R.items():
            print(f'  {k_}: Phi {v["Phi"]:.1f}  U0 {v["U0"]:.3f}  sona {v["sona"]:.3f}  rad(y) {v["rad"]}')
    print(f'tid {time.time() - T0:.0f} s')
