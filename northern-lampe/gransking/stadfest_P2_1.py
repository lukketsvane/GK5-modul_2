"""Motprov av P2 (skeive strålar i prismeplata til (c)).

Uavhengig av prisme.py: berre to flater (flat overside, fasett τ(s) frå motoren), ingen stigeveggar,
så verknaden av skeive strålar vert isolert. Snell og Fresnel på vektorform i 3D.
Tre modellar for same plate:
  M2  motoren sin premiss: projisert θ ut = θ_lov(φ) for alle ξ  (I = G(θ)·cos ξ)
  M3  eksakt 3D: θ ut avheng av ξ (effektiv indeks sqrt(n²-sin²ξ)/cos ξ)
  M3m G(θ) frå 3D-sporing marginalisert over alle ξ og brukt separabelt (slik fjern_tal() i prisme.py gjer)
Nærfelt: Monte Carlo frå line langs x, strålar ut frå plata der dei går ut, celler ±1,5 cm (som naer_tal()).
Fjernfelt: punktkjelder på LED-aksen (som motoren), I(θ, ξ) frå tabell.
"""
import os, sys, math, json, time
import numpy as np

ROOT = r'C:\Users\Iver\Documents\northern-lampe'
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form04'))
import felles as fe
import motor as mo

t0 = time.time()
B = mo.FINAL
O = mo.optikk(B)
n = mo.N_PMMA
d, tp, bp, L, ys, zs = B['d'], B['tp'], B['bp'], B['L'], B['ys'], B['zs']
phm = O['phm']
S_TAB, TAU_TAB, PH_TAB, TH_TAB = O['s'], O['tau'], O['ph'], O['th']
UT = {}


def refr(k, N, n1, n2):
    ci = (k * N).sum(-1)
    e = n1 / n2
    rad = 1 - e ** 2 * (1 - ci ** 2)
    tir = rad < 0
    ct = np.sqrt(np.clip(rad, 0, None))
    kt = e * k + (ct - e * ci)[..., None] * N               # N langs utbreiinga (k·N > 0)
    rs = ((n1 * ci - n2 * ct) / (n1 * ci + n2 * ct)) ** 2
    rp = ((n1 * ct - n2 * ci) / (n1 * ct + n2 * ci)) ** 2
    T = np.where(tir, 0.0, 1 - 0.5 * (rs + rp))
    return kt, T, tir


def trace(k0):
    """k0 (m,3) i ramma (x, s fram mot brukaren, w ned). Returnerer k ut, T, tir, s på oversida, k inne."""
    Nt = np.zeros_like(k0); Nt[:, 2] = 1.0
    k1, T1, _ = refr(k0, Nt, 1.0, n)
    s = d * k0[:, 1] / k0[:, 2]
    tau = np.interp(s, S_TAB, TAU_TAB)
    N2 = np.c_[np.zeros_like(tau), np.sin(tau), np.cos(tau)]
    k2, T2, tir = refr(k1, N2, n, 1.0)
    return k2, T1 * T2, tir, s, k1


def retn(phi, dx):
    c = math.sqrt(1 - dx ** 2)
    return np.array([[dx, c * math.sin(phi), c * math.cos(phi)]])


# ---- 0: designlova attgjeven i snittet ----
k = np.c_[np.zeros_like(PH_TAB), np.sin(PH_TAB), np.cos(PH_TAB)]
k2, T, tir, s, _ = trace(k)
th0 = np.arctan2(k2[:, 1], k2[:, 2])
UT['lov_avvik_maks_deg'] = float(np.degrees(np.abs(th0 - TH_TAB)).max())

# ---- 1: einskildstrålar som i funnet ----
tab = {}
for phd in (40.0, 55.0, 58.0):
    th_lov = float(np.degrees(np.interp(math.radians(phd), PH_TAB, TH_TAB)))
    rad = dict(lov=round(th_lov, 2))
    for dx in (0.0, 0.3, 0.5, 0.7):
        k2, T, tir, _, _ = trace(retn(math.radians(phd), dx))
        rad[f'dx{dx}'] = 'TIR' if tir[0] else round(float(np.degrees(np.arctan2(k2[0, 1], k2[0, 2]))), 2)
    tab[f'phi{phd:g}'] = rad
UT['einskildstraalar_theta_ut_deg'] = tab

# del av lambertsk fluks med |dx| > 0,5: heile halvkula og det som når plata
rng = np.random.default_rng(7)
m = 2_000_000
r = np.sqrt(rng.random(m)); a = 2 * np.pi * rng.random(m)
kx, ks = r * np.cos(a), r * np.sin(a); kw = np.sqrt(1 - r ** 2)
paa = np.abs(d * ks / kw) <= bp / 2
UT['del_dx_over_0_5_halvkula'] = float((np.abs(kx) > 0.5).mean())
UT['del_dx_over_0_5_av_det_som_naar_plata'] = float((np.abs(kx[paa]) > 0.5).mean())

# ---- 2: nærfelt Monte Carlo ----
TX = np.linspace(-0.30, 0.30, 7); TY = np.linspace(0.05, 0.40, 5)
H = 0.015
# 2D Fresnel som motoren (vinklar i snittet)
phi_i2 = np.arcsin(np.sin(PH_TAB) / n)
T2D = mo.fresnel_T(np.abs(PH_TAB), np.abs(phi_i2), 1.0, n) * mo.fresnel_T(np.abs(phi_i2 - TAU_TAB), np.abs(TH_TAB - TAU_TAB), n, 1.0)


def naer(modell, sig_deg, N=6_000_000, seed=11, kinn=True, chunk=1_000_000):
    rng = np.random.default_rng(seed)
    E = np.zeros((len(TY), len(TX)))
    tot = 0.0
    for i0 in range(0, N, chunk):
        mm = min(chunk, N - i0)
        x0 = (rng.random(mm) - 0.5) * L
        r = np.sqrt(rng.random(mm)); a = 2 * np.pi * rng.random(mm)
        kx, ks = r * np.cos(a), r * np.sin(a); kw = np.sqrt(1 - r ** 2)
        ok = (np.abs(d * ks / kw) <= bp / 2) & (kw > 1e-6)
        kx, ks, kw, x0 = kx[ok], ks[ok], kw[ok], x0[ok]
        k0 = np.c_[kx, ks, kw]
        k2, T, tir, s, k1 = trace(k0)
        xh = x0 + d * kx / kw
        xe = xh + tp * k1[:, 0] / k1[:, 2]
        se = s + tp * k1[:, 1] / k1[:, 2]
        phi = np.arctan2(ks, kw)
        if modell == 'M2':                       # motoren: θ = θ_lov(φ), ξ uendra, 2D Fresnel
            th = np.interp(phi, PH_TAB, TH_TAB)
            T = np.interp(phi, PH_TAB, T2D)
            c = np.sqrt(1 - kx ** 2)
            k2 = np.c_[kx, c * np.sin(th), c * np.cos(th)]
            tir = np.zeros(len(th), bool)
        w = np.where(tir, 0.0, T)
        if kinn:
            w = np.where(np.abs(xe) > L / 2, 0.0, w)
        if sig_deg > 0:
            g = rng.normal(0, math.radians(sig_deg), len(w)); cg, sg = np.cos(g), np.sin(g)
            ds, dz = k2[:, 1], k2[:, 2]
            k2 = np.c_[k2[:, 0], ds * cg + dz * sg, -ds * sg + dz * cg]
        down = k2[:, 2] > 1e-6
        t = np.where(down, (zs - (d + tp)) / np.where(down, k2[:, 2], 1), np.inf)
        xq = xe + t * k2[:, 0]
        yq = ys - (se + t * k2[:, 1])
        ia = np.rint((xq - TX[0]) / (TX[1] - TX[0])); ib = np.rint((yq - TY[0]) / (TY[1] - TY[0]))
        okc = down & (ia >= 0) & (ia < len(TX)) & (ib >= 0) & (ib < len(TY))
        ia, ib = ia[okc].astype(int), ib[okc].astype(int)
        inn = (np.abs(xq[okc] - TX[ia]) < H) & (np.abs(yq[okc] - TY[ib]) < H)
        E += np.bincount(ib[inn] * len(TX) + ia[inn], weights=w[okc][inn], minlength=E.size).reshape(E.shape)
        tot += mm
    E = E / tot / (2 * H) ** 2                                # lx per LED-lm
    imin = np.unravel_index(np.argmin(E), E.shape)
    return dict(U0=round(float(E.min() / E.mean()), 3), Phi_lm=round(float(fe.E_TASK / E.mean() / mo.RISS), 1),
                min_ved=(float(TX[imin[1]]), float(TY[imin[0]])), rad_snitt=np.round(E.mean(1) / E.mean(), 2).tolist(),
                E_rel=np.round(E / E.mean(), 2).tolist())


NAER = {}
for mdl in ('M2', 'M3'):
    for sg in (4.0, 6.0):
        NAER[f'{mdl}_sigma{sg:g}'] = naer(mdl, sg)
NAER['M3_sigma4_utan_kinn'] = naer('M3', 4.0, kinn=False)
NAER['M3_sigma4_frø2'] = naer('M3', 4.0, seed=23)
UT['naer'] = NAER

# ---- 3: fjernfelt med tabell I(θ, ξ) ----
XI = np.radians(np.arange(-85, 85.01, 1.0))
PHG = np.linspace(-phm, phm, 8001)
TE = np.radians(np.arange(-90, 90.001, 0.25)); TC = (TE[:-1] + TE[1:]) / 2


def KERN(sig_deg):
    o = np.arange(-120, 121) * 0.25
    kk = np.exp(-0.5 * (o / sig_deg) ** 2)
    return kk / kk.sum()


def tabell(modell, sig_deg):
    I = np.zeros((len(XI), len(TC)))
    for j, xi in enumerate(XI):
        c = math.cos(xi)
        k0 = np.c_[np.full(len(PHG), math.sin(xi)), c * np.sin(PHG), c * np.cos(PHG)]
        if modell == 'M2':
            th = np.interp(PHG, PH_TAB, TH_TAB); T = np.interp(PHG, PH_TAB, T2D)
        else:
            k2, T, tir, _, _ = trace(k0)
            th = np.arctan2(k2[:, 1], k2[:, 2]); T = np.where(tir, 0, T)
        f = np.cos(PHG) * c ** 2 * T / np.pi                  # LED-lm per dφ dξ (lambertsk, heile halvkula = 1)
        h, _ = np.histogram(th, TE, weights=f * (PHG[1] - PHG[0]))
        dens = h / np.diff(TE)
        if sig_deg > 0:
            dens = np.convolve(dens, KERN(sig_deg), mode='same')
        I[j] = dens / max(c, 1e-9)                            # per romvinkel
    return I


def tabell_marginal(sig_deg):
    """3D-spora θ, marginalisert over ξ, brukt som G(θ)·cos ξ (metoden i prisme.py fjern_tal)."""
    I3 = tabell('M3', 0.0)
    flux_theta = (I3 * np.cos(XI)[:, None]).sum(0) * (XI[1] - XI[0])   # fluks per dθ
    if sig_deg > 0:
        flux_theta = np.convolve(flux_theta, KERN(sig_deg), mode='same')
    # separabel: I = G(θ)·(2/π)cos ξ, ∫∫ I cos ξ = ∫G
    return flux_theta[None, :] * (2 / np.pi) * np.cos(XI)[:, None]


def fjern(I):
    S = mo._src(B)
    Q = fe.TASK
    dv = Q[None] - S[:, None]
    rr = np.linalg.norm(dv, axis=-1)
    xi = np.arcsin(np.clip(dv[..., 0] / rr, -1, 1))
    th = np.arctan2(-dv[..., 1], -dv[..., 2])
    fi = (xi - XI[0]) / (XI[1] - XI[0]); fj = (th - TC[0]) / (TC[1] - TC[0])
    i0 = np.clip(np.floor(fi).astype(int), 0, len(XI) - 2); j0 = np.clip(np.floor(fj).astype(int), 0, len(TC) - 2)
    a_, b_ = fi - i0, fj - j0
    Iv = (I[i0, j0] * (1 - a_) * (1 - b_) + I[i0 + 1, j0] * a_ * (1 - b_) + I[i0, j0 + 1] * (1 - a_) * b_ + I[i0 + 1, j0 + 1] * a_ * b_) / len(S)
    ci = dv[..., 2] * -1 / rr
    Et = (Iv * ci / rr ** 2).sum(0)
    E = Et.reshape(5, 7)
    imin = np.argmin(Et)
    return dict(U0=round(float(Et.min() / Et.mean()), 3), Phi_lm=round(float(fe.E_TASK / Et.mean() / mo.RISS), 1),
                min_ved=(float(Q[imin, 0]), float(Q[imin, 1])), rad_snitt=np.round(E.mean(1) / E.mean(), 2).tolist())


FJ = {}
Et_m = mo.E_punkt(B, 0.0, fe.TASK, np.array([0, 0, 1.0]))
FJ['motoren_E_punkt'] = dict(U0=round(float(Et_m.min() / Et_m.mean()), 3), Phi_lm=round(float(fe.E_TASK / Et_m.mean()), 1),
                             rad_snitt=np.round(Et_m.reshape(5, 7).mean(1) / Et_m.mean(), 2).tolist())
for sg in (4.0, 6.0):
    FJ[f'M2_sigma{sg:g}'] = fjern(tabell('M2', sg))
    FJ[f'M3_sigma{sg:g}'] = fjern(tabell('M3', sg))
    FJ[f'M3m_sigma{sg:g}'] = fjern(tabell_marginal(sg))
UT['fjern'] = FJ
UT['tid_s'] = round(time.time() - t0, 1)
print(json.dumps(UT, ensure_ascii=False, indent=1))
