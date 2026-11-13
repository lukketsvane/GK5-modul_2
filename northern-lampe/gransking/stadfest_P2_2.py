"""Motbevisar 2 for P2 (skeive strålar i prismeplata, konsept c).

Isolerer skeiv-effekten: ideelle fasettar (berre flat overside + fasett, ingen stigeveggar, line utan breidd),
same τ(φ) som form04/motor.py optikk(). Samanliknar
  D: designlova separabel, G(θ)·cos ξ (skal gje motoren: U0 0,688, Φ 433)
  X: eksakt 3D-brytning (Bravais), full tabell I(θ, ξ)
  M: 3D, men kollapsa til marginal G(θ) og så separabel (metoden i prisme.py fjern_tal)
Fjernfelt med motoren sine 24 lineelement, og nærfelt (strålar frå verkeleg utgangspunkt, celler ±1,5 cm).
"""
import os, sys, math, json
import numpy as np
from scipy.interpolate import RegularGridInterpolator
HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form04'))
import felles as fe
import motor as M

B = M.FINAL
O = M.optikk(B)
n = M.N_PMMA
phm = O['phm']


def fr(ci, ct, n1, n2):
    rs = ((n1 * ci - n2 * ct) / (n1 * ci + n2 * ct)) ** 2
    rp = ((n1 * ct - n2 * ci) / (n1 * ct + n2 * ci)) ** 2
    return 1 - 0.5 * (rs + rp)


def tau_av(ph):
    return np.interp(ph, O['ph'], O['tau'])


def bryt3d(ph, xi):
    """Eksakt: retning i luft (sin ξ, cos ξ sin φ, cos ξ cos φ) -> flat overside -> fasett τ(φ). Gjev θ ut, T, ok."""
    ux, uy, uz = np.sin(xi), np.cos(xi) * np.sin(ph), np.cos(xi) * np.cos(ph)
    v = np.stack([ux / n, uy / n, np.sqrt(1 - (ux ** 2 + uy ** 2) / n ** 2)])
    T1 = fr(uz, v[2], 1.0, n)
    ta = tau_av(ph)
    N = np.stack([np.zeros_like(ta), np.sin(ta), np.cos(ta)])
    ci = (v * N).sum(0)
    s2 = n ** 2 * (1 - ci ** 2)
    ok = s2 < 1
    ct = np.sqrt(np.clip(1 - s2, 0, 1))
    t = n * v - (n * ci - ct) * N
    T2 = np.where(ok, fr(ci, ct, n, 1.0), 0.0)
    return np.arctan2(t[1], t[2]), np.arcsin(np.clip(t[0], -1, 1)), T1 * T2, ok, t


def bryt_design(ph, xi):
    """Separabel designlov: θ(φ) frå motoren, ξ uendra, Fresnel i snittet."""
    th = np.interp(ph, O['ph'], O['th'])
    phi_i = np.arcsin(np.sin(ph) / n); ta = tau_av(ph)
    T = fr(np.cos(ph), np.cos(phi_i), 1.0, n) * fr(np.cos(phi_i - ta), np.cos(th - ta), n, 1.0)
    return th, xi + 0 * ph, T, np.ones_like(ph, bool), None


# ---------- 1 · analytisk kontroll av tala i funnet ----------
def kontroll_phi(phd, dxs):
    ph = math.radians(phd)
    th_lov = math.degrees(np.interp(ph, O['ph'], O['th']))
    ut = {'lov': round(th_lov, 2)}
    for dx in dxs:
        th, xo, T, ok, t = bryt3d(np.array([ph]), np.array([math.asin(dx)]))
        ut[f'dx{dx}'] = round(math.degrees(th[0]), 2) if ok[0] else 'TIR'
    return ut


# ---------- 2 · tabell I(θ, ξ) per LED-lumen ----------
TG = np.radians(np.arange(-90, 90.001, 0.25))
XG = np.radians(np.arange(-89.5, 89.51, 1.0))
SIG = M.SIGMA


def tabell(fn, nph=12001):
    ph = np.linspace(-phm, phm, nph); dph = ph[1] - ph[0]
    e = np.concatenate([[TG[0] - 0.125 * math.pi / 180], (TG[1:] + TG[:-1]) / 2, [TG[-1] + 0.125 * math.pi / 180]])
    dth = np.diff(e)
    k = np.exp(-0.5 * (np.arange(-60, 61) * 0.25 / SIG) ** 2); k /= k.sum()
    I = np.zeros((len(XG), len(TG)))
    eta = 0.0
    dxi = XG[1] - XG[0]
    for j, xi in enumerate(XG):
        th, xo, T, ok, _ = fn(ph, np.full_like(ph, xi))
        w = np.cos(ph) * math.cos(xi) ** 2 / math.pi * T * ok * M.RISS * dph * dxi   # LED-lm
        H, _ = np.histogram(th, e, weights=w)
        eta += H.sum()
        H = np.convolve(H, k, mode='same')
        I[j] = H / (dth * math.cos(xi) * dxi)                                          # cd per LED-lm
    return I, eta


def marginal(I):
    """Kollaps til G(θ) og separabel (2/π)cos ξ, som prisme.py G_tab + E_fjern."""
    dxi = XG[1] - XG[0]
    G = (I * np.cos(XG)[:, None]).sum(0) * dxi            # lm per rad θ
    return (2 / np.pi) * np.cos(XG)[:, None] * G[None]


def E_fjern(I, Q, qn=np.array([0, 0, 1.0]), a=0.0):
    f = RegularGridInterpolator((XG, TG), I, bounds_error=False, fill_value=0.0)
    S = M._src(B)
    d = Q[None] - S[:, None]
    r = np.linalg.norm(d, axis=-1)
    xi = np.arcsin(np.clip(d[..., 0] / r, -1, 1))
    th = np.arctan2(-d[..., 1], -d[..., 2]) - a
    Iv = f(np.stack([xi.ravel(), th.ravel()], -1)).reshape(xi.shape) / len(S)
    ci = -(d @ qn) / r
    ok = (ci > 0) & ~fe.screen_block(S, Q)
    return np.where(ok, Iv * ci / r ** 2, 0).sum(0)


def tal(E):
    Em = E.mean()
    i = int(np.argmin(E))
    return dict(U0=round(float(E.min() / Em), 3), Phi=round(float(fe.E_TASK / Em), 1),
                min_ved=[round(float(v), 2) for v in fe.TASK[i, :2]],
                rad_rel=[round(float(v), 2) for v in (E.reshape(5, 7).mean(1) / Em)],
                kol_rel=[round(float(v), 2) for v in (E.reshape(5, 7).mean(0) / Em)])


# ---------- 3 · nærfelt, strålar frå utgangspunktet ----------
def naer(fn, N=6_000_000, seed=3, chunk=1_000_000):
    rng = np.random.default_rng(seed)
    tx, ty = np.linspace(-0.30, 0.30, 7), np.linspace(0.05, 0.40, 5)
    h = 0.015
    Ec = np.zeros(35); hx = np.zeros(35); wt = 0.0
    for c0 in range(0, N, chunk):
        m = min(chunk, N - c0)
        u1, u2 = rng.random(m), rng.random(m)                 # lambertsk i 3D
        st = np.sqrt(u1); dz = np.sqrt(1 - u1)
        dx, ds = st * np.cos(2 * np.pi * u2), st * np.sin(2 * np.pi * u2)
        ph = np.arctan2(ds, dz); xi = np.arcsin(dx)
        inn = np.abs(ph) < phm
        ph, xi = ph[inn], xi[inn]
        th, xo, T, ok, _ = fn(ph, xi)
        w = T * ok * M.RISS / N
        th = th + rng.normal(0, math.radians(SIG), len(th))
        x0 = (rng.random(len(ph)) - 0.5) * B['L']
        zb = B['d'] + B['tp']
        s_top = B['d'] * np.tan(ph)
        xe = x0 + B['d'] * np.tan(xi) / np.cos(ph)              # forskyving i x fram til plata (innsida neglisjert, < 3 mm)
        kinn = np.abs(xe) > B['L'] / 2
        Py = B['ys'] - s_top; Pz = B['zs'] - zb
        # retning ut: projisert θ, x-del sin ξ
        cx = np.cos(xo)
        Vx, Vy, Vz = np.sin(xo), -cx * np.sin(th), -cx * np.cos(th)
        t = -Pz / Vz
        Qx, Qy = xe + t * Vx, Py + t * Vy
        w = np.where(kinn, 0.0, w)
        ia = np.rint((Qx + 0.30) / 0.10).astype(int); ib = np.rint((Qy - 0.05) / 0.0875).astype(int)
        okc = (ia >= 0) & (ia < 7) & (ib >= 0) & (ib < 5)
        okc[okc] &= (np.abs(Qx[okc] - tx[ia[okc]]) < h) & (np.abs(Qy[okc] - ty[ib[okc]]) < h)
        idx = ib[okc] * 7 + ia[okc]
        Ec += np.bincount(idx, weights=w[okc], minlength=35)
        hx += np.bincount(idx, weights=(w * (np.abs(np.sin(xo)) > 0.5))[okc], minlength=35)
        wt += w.sum()
    E = Ec / (2 * h) ** 2
    d = tal(E)
    d['del_dx_over_0_5_i_cellene'] = round(float(hx.sum() / Ec.sum()), 3)
    d['eta'] = round(float(wt), 4)
    return d


if __name__ == '__main__':
    UT = {}
    UT['analytisk'] = {f'phi{p}': kontroll_phi(p, (0.0, 0.3, 0.5, 0.7)) for p in (20, 40, 55)}
    print('analytisk', UT['analytisk'], flush=True)
    # lambertsk del med |dx|>0,5 ved kjelda
    UT['lambert_dx_over_0_5'] = round(1 - (math.pi / 12 + math.sin(math.pi / 3) / 4) * 2 / (math.pi / 2), 3)
    # største |ξ| som når oppgåvesona frå lina
    S = M._src(B); d = fe.TASK[None] - S[:, None]
    UT['maks_sin_xi_til_sona'] = round(float(np.abs(d[..., 0] / np.linalg.norm(d, axis=-1)).max()), 3)

    ID, etaD = tabell(bryt_design)
    IX, etaX = tabell(bryt3d)
    IM = marginal(IX)
    Em = M.E_punkt(B, 0.0, fe.TASK, np.array([0, 0, 1.0]))
    UT['motor'] = tal(Em); UT['motor']['eta'] = round(M.eta(B), 4)
    UT['fjern_D_design'] = tal(E_fjern(ID, fe.TASK)); UT['fjern_D_design']['eta'] = round(etaD, 4)
    UT['fjern_X_3D_tabell'] = tal(E_fjern(IX, fe.TASK)); UT['fjern_X_3D_tabell']['eta'] = round(etaX, 4)
    UT['fjern_M_3D_marginal'] = tal(E_fjern(IM, fe.TASK))
    for k in ('motor', 'fjern_D_design', 'fjern_X_3D_tabell', 'fjern_M_3D_marginal'):
        print(k, UT[k], flush=True)
    UT['naer_D_design'] = naer(bryt_design); print('naer_D', UT['naer_D_design'], flush=True)
    UT['naer_X_3D'] = naer(bryt3d); print('naer_X', UT['naer_X_3D'], flush=True)
    print(json.dumps(UT, ensure_ascii=False))
