# -*- coding: utf-8 -*-
"""
film.py  ·  optisk ark frå bakbelysninga i ein monitor, rekna som det det er: ein riflete profil i plast

Arket er ein tynn film med ein periodisk profil på den eine sida (riller langs y) og flat bakside.
Kvart foton blir spora gjennom éin periode av profilen med Snell, totalrefleksjon og Fresnel-tap,
i 3D (skeive strålar), med brytingsindeks som følgjer bølgjelengda. Ingen tabell er gjetta:
splitting, smørje og fargekant kjem ut av geometrien.

Filmkoordinatar: x på tvers av rillene, y langs rillene, z ut av den rifla sida.
  side='prisme': lyset kjem inn mot den rifla sida (går mot -z).  side='flat': inn gjennom den flate sida (går mot +z).

    from film import Film, prisme, linse
    f = Film(prisme(90), n_d=1.59, abbe=30)
    T, R, lober = f.lober(theta_x=0, side='prisme')          # [(vinkel i grader, del av lyset), ...]
    D_ut, ut = f.spor(D_inn, lam=550, side='prisme')         # D_inn (N,3) i filmkoordinatar; ut = +1 gjennom, -1 attende, 0 tapt
    D_ut, ut = f.gjennom(D_verd, normal, riller, lam=550)    # same i romkoordinatar: sida blir lesen av retninga

Profilen er ein parameter: prisme(toppvinkel, avrunding, land), linse(radius), eller eigne punkt.
ANTAKING: éin brytingsindeks for heile filmen, upolarisert lys, ingen absorpsjon. Ekstra spreiing (matt bakside,
ujamne prisme) er ein gaussisk dreiing om rilleaksen (spreiing) og på tvers (spreiing_langs), pluss ein diffus del (haze).

  python film.py            sjølvkontroll: energi, analytisk splittvinkel, tabell
"""
import math, os, sys
import numpy as np
from numba import njit, prange

# ------------------------------------------------------------------ profilar (éin periode, breidd 1)

def prisme(toppvinkel=90.0, avrunding=0.0, land=0.0, n_bue=12):
    """Symmetrisk prisme. toppvinkel i grader. avrunding: radius på toppen (del av perioden).
    land: flat dal mellom prisma (del av perioden). Gjev punkt (x, h) frå x = 0 til 1, h er høgd over berelaget."""
    a = math.radians(toppvinkel) / 2.0
    w = 1.0 - land
    H = (w / 2.0) / math.tan(a)
    pts = [(0.0, 0.0)]
    if land > 0: pts.append((land / 2.0, 0.0))
    xm = 0.5
    if avrunding <= 0:
        pts.append((xm, H))
    else:
        r = avrunding
        # sirkelboge som tangerer begge flankane: sentrum under toppen
        d = r / math.sin(a)                      # avstand frå toppunktet ned til sentrum
        zc = H - d
        fi = math.pi / 2 - a                     # halv bogevinkel
        for i in range(n_bue + 1):
            t = -fi + 2 * fi * i / n_bue
            pts.append((xm + r * math.sin(t), zc + r * math.cos(t)))
    if land > 0: pts.append((1.0 - land / 2.0, 0.0))
    pts.append((1.0, 0.0))
    return np.array(pts, float)

def linse(radius=0.6, n_bue=48):
    """Sylinderlinser (lentikulært ark): sirkelboge med radius (del av perioden, minst 0,5) over heile perioden."""
    r = max(radius, 0.5)
    zc = -math.sqrt(r * r - 0.25)
    x = np.linspace(0, 1, n_bue + 1)
    return np.stack([x, zc + np.sqrt(np.maximum(r * r - (x - 0.5) ** 2, 0.0))], 1)

def boelgje(amplitude=0.15, n=64):
    """Mjuk sinusprofil (1D-diffusor)."""
    x = np.linspace(0, 1, n + 1)
    return np.stack([x, amplitude * (1 - np.cos(2 * np.pi * x))], 1)

# ------------------------------------------------------------------ mikrosporing (numba)

@njit(cache=True)
def _grense(d0, d1, d2, nx, nz, n1, n2, u):
    """Bryt eller spegl i ei flate med normal (nx, 0, nz). u er eit slumptal. Gjev (retning, kryssa)."""
    c = d0 * nx + d2 * nz
    if c > 0:
        nx = -nx; nz = -nz; c = -c
    ci = -c
    eta = n1 / n2
    s2 = eta * eta * (1.0 - ci * ci)
    if s2 >= 1.0:
        return d0 + 2 * ci * nx, d1, d2 + 2 * ci * nz, False
    ct = math.sqrt(1.0 - s2)
    rs = (n1 * ci - n2 * ct) / (n1 * ci + n2 * ct)
    rp = (n1 * ct - n2 * ci) / (n1 * ct + n2 * ci)
    R = 0.5 * (rs * rs + rp * rp)
    if u < R:
        return d0 + 2 * ci * nx, d1, d2 + 2 * ci * nz, False
    k = eta * ci - ct
    return eta * d0 + k * nx, eta * d1, eta * d2 + k * nz, True

@njit(cache=True)
def _mikro(px, pz, tj, n, d0, d1, d2, x0, maxb):
    """Eitt foton gjennom filmen. Profil (px, pz) over éin periode med breidd 1, berelag 0 <= z <= tj.
    Startar i x0: nedanfrå (d2 > 0, gjennom flatsida) eller ovanfrå (d2 < 0, mot profilen).
    Gjev (d0, d1, d2, status): +1 ut på profilsida, -1 ut på flatsida, 0 tapt."""
    m = len(px) - 1
    hmax = 0.0
    for i in range(m + 1):
        if pz[i] > hmax: hmax = pz[i]
    ztopp = tj + hmax
    inne = False
    x = x0
    z = -1e-7 if d2 > 0 else ztopp + 1e-7
    eps = 1e-9
    for _ in range(maxb):
        tb = 1e30; kind = 0; bnx = 0.0; bnz = 0.0
        # flatsida z = 0
        if d2 != 0.0:
            t = -z / d2
            if t > eps:
                tb = t; kind = 1; bnx = 0.0; bnz = -1.0
        # profilen: finn t-intervallet der strålen er i høgdeområdet til profilen
        ta = eps; tc = 1e30
        if d2 != 0.0:
            t1 = (tj - 1e-9 - z) / d2; t2 = (ztopp + 1e-9 - z) / d2
            if t1 > t2:
                tt = t1; t1 = t2; t2 = tt
            if t1 > ta: ta = t1
            tc = t2
        elif z < tj - 1e-9 or z > ztopp + 1e-9:
            tc = -1.0
        if tc > ta:
            if tc > 1e6: tc = 1e6
            xa = x + ta * d0; xb = x + tc * d0
            if d0 >= 0:
                k0 = int(math.floor(xa)); k1 = int(math.floor(xb)); steg = 1
            else:
                k0 = int(math.floor(xa)); k1 = int(math.floor(xb)); steg = -1
            nk = abs(k1 - k0) + 1
            if nk > 400: nk = 400
            k = k0
            for _c in range(nk):
                funne = False
                for i in range(m):
                    ax = px[i] + k; az = tj + pz[i]
                    ex = px[i + 1] - px[i]; ez = pz[i + 1] - pz[i]
                    den = d0 * ez - d2 * ex
                    if abs(den) < 1e-14: continue
                    t = ((ax - x) * ez - (az - z) * ex) / den
                    if t <= eps or t >= tb: continue
                    uu = ((ax - x) * d2 - (az - z) * d0) / den
                    if uu < -1e-12 or uu > 1.0 + 1e-12: continue
                    l = math.sqrt(ex * ex + ez * ez)
                    tb = t; kind = 2; bnx = -ez / l; bnz = ex / l; funne = True
                if funne: break
                k += steg
        if kind == 0:
            if inne: return d0, d1, d2, 0
            if d2 > 0: return d0, d1, d2, 1
            if d2 < 0: return d0, d1, d2, -1
            return d0, d1, d2, 0
        x += tb * d0; z += tb * d2
        n1 = n if inne else 1.0
        n2 = 1.0 if inne else n
        d0, d1, d2, kryssa = _grense(d0, d1, d2, bnx, bnz, n1, n2, np.random.random())
        if kryssa: inne = not inne
    return d0, d1, d2, 0

@njit(parallel=True, cache=True)
def _spor_mange(px, pz, tj, nn, D, maxb, s_x, s_y, haze):
    N = len(D)
    U = np.empty((N, 3)); st = np.empty(N, np.int8)
    for i in prange(N):
        d0, d1, d2 = D[i, 0], D[i, 1], D[i, 2]
        inn = 1 if d2 > 0 else -1
        d0, d1, d2, s = _mikro(px, pz, tj, nn[i], d0, d1, d2, np.random.random(), maxb)
        if s != 0:
            gj = (s == inn)
            if gj and haze > 0 and np.random.random() < haze:
                # diffus del: lambertsk ut på utgangssida
                r = math.sqrt(np.random.random()); ph = 2 * math.pi * np.random.random()
                d0 = r * math.cos(ph); d1 = r * math.sin(ph); d2 = s * math.sqrt(max(1 - r * r, 0.0))
            else:
                if s_x > 0:      # dreiing om rilleaksen (y): smørje på tvers av rillene
                    a = np.random.normal() * s_x
                    c, sn = math.cos(a), math.sin(a)
                    e0 = c * d0 + sn * d2; e2 = -sn * d0 + c * d2
                    if e2 * d2 > 0: d0 = e0; d2 = e2
                if s_y > 0:      # dreiing om x: smørje langs rillene
                    a = np.random.normal() * s_y
                    c, sn = math.cos(a), math.sin(a)
                    e1 = c * d1 + sn * d2; e2 = -sn * d1 + c * d2
                    if e2 * d2 > 0: d1 = e1; d2 = e2
            st[i] = 1 if gj else -1
        else:
            st[i] = 0
        U[i, 0] = d0; U[i, 1] = d1; U[i, 2] = d2
    return U, st

# ------------------------------------------------------------------ filmen

LAM_F, LAM_D, LAM_C = 486.1, 587.6, 656.3

class Film:
    """Eit optisk ark. profil: punkt (x, h) over éin periode (sjå prisme(), linse(), boelgje()).
    n_d, abbe: brytingsindeks ved 587,6 nm og Abbe-tal (Cauchy: n = A + B / lam²).
    tjukn: berelaget i periodar. spreiing / spreiing_langs: ekstra gaussisk spreiing (sigma, grader) på tvers av og langs rillene.
    haze: diffus del av det som kjem gjennom. T_ekstra: ekstra tap (absorpsjon, smuss)."""
    def __init__(s, profil=None, n_d=1.59, abbe=30.0, tjukn=2.0, spreiing=0.0, spreiing_langs=0.0, haze=0.0,
                 T_ekstra=1.0, namn='prismefilm'):
        s.profil = np.asarray(prisme(90.0) if profil is None else profil, float)
        s.px = np.ascontiguousarray(s.profil[:, 0]); s.pz = np.ascontiguousarray(s.profil[:, 1])
        s.n_d, s.abbe, s.tjukn = float(n_d), float(abbe), float(tjukn)
        s.B = (s.n_d - 1.0) / s.abbe / (1 / LAM_F ** 2 - 1 / LAM_C ** 2)
        s.A = s.n_d - s.B / LAM_D ** 2
        s.spreiing, s.spreiing_langs, s.haze, s.T_ekstra, s.namn = spreiing, spreiing_langs, haze, T_ekstra, namn

    def n(s, lam):
        return s.A + s.B / np.asarray(lam, float) ** 2

    def spor(s, D, lam=550.0, side=None, maxb=64):
        """Spor retningar D (N,3) i filmkoordinatar. side: 'prisme' eller 'flat' snur z-forteiknet til D om det trengst.
        Gjev (D_ut, ut): ut = +1 gjennom filmen, -1 kasta attende, 0 tapt (meir enn maxb sprett)."""
        D = np.atleast_2d(np.asarray(D, float)).copy()
        D /= np.linalg.norm(D, axis=1)[:, None]
        if side == 'prisme': D[:, 2] = -np.abs(D[:, 2])
        elif side == 'flat': D[:, 2] = np.abs(D[:, 2])
        nn = np.broadcast_to(s.n(lam), (len(D),)).astype(float).copy()
        return _spor_mange(s.px, s.pz, s.tjukn, nn, D, maxb, math.radians(s.spreiing), math.radians(s.spreiing_langs), s.haze)

    def gjennom(s, D, normal, riller, lam=550.0):
        """Same i romkoordinatar. normal: ut av den rifla sida. riller: retninga rillene går. Gjev (D_ut, ut)."""
        fz = np.asarray(normal, float); fz = fz / np.linalg.norm(fz)
        fy = np.asarray(riller, float); fy = fy - (fy @ fz) * fz; fy /= np.linalg.norm(fy)
        fx = np.cross(fy, fz)
        M = np.stack([fx, fy, fz])
        U, st = s.spor(np.atleast_2d(D) @ M.T, lam)
        return U @ M, st

    def fordeling(s, theta_x=0.0, theta_y=0.0, lam=550.0, side='prisme', n=200000, bin_grader=0.5):
        """Fordelinga av utgåande vinkel på tvers av rillene. Gjev (T, R, sentrum, del per bin av innfallande lys)."""
        z = -1.0 if side == 'prisme' else 1.0
        d = np.array([math.tan(math.radians(theta_x)), math.tan(math.radians(theta_y)), z])
        U, st = s.spor(np.tile(d, (n, 1)), lam)
        gj = st == 1
        fi = np.degrees(np.arctan2(U[gj, 0], np.abs(U[gj, 2])))
        kant = np.arange(-90, 90 + bin_grader, bin_grader)
        h, _ = np.histogram(fi, kant)
        return gj.mean() * s.T_ekstra, (st == -1).mean(), 0.5 * (kant[1:] + kant[:-1]), h / n * s.T_ekstra

    def lober(s, theta_x=0.0, theta_y=0.0, lam=550.0, side='prisme', n=200000, terskel=0.01):
        """Lobene i det gjennomsleppte lyset. Gjev (T, R, [(vinkel, del av innfallande lys), ...]) sortert etter del."""
        T, R, c, h = s.fordeling(theta_x, theta_y, lam, side, n)
        glatt = np.convolve(h, np.ones(5) / 5, 'same')
        ut = []; i = 0
        gr = max(glatt.max() * 0.05, 1e-6)
        while i < len(h):
            if glatt[i] > gr:
                j = i
                while j < len(h) and glatt[j] > gr: j += 1
                w = h[i:j]
                if w.sum() >= terskel:
                    ut.append((float((c[i:j] * w).sum() / w.sum()), float(w.sum())))
                i = j
            else:
                i += 1
        return T, R, sorted(ut, key=lambda e: -e[1])

    def tabell(s, side='prisme', vinklar=(0, 10, 20, 30, 40, 50, 60), lam=550.0, theta_y=0.0, n=100000):
        rader = []
        for a in vinklar:
            T, R, L = s.lober(a, theta_y, lam, side, n)
            rader.append((a, T, R, L))
        return rader

def analytisk_splitt(n=1.59, toppvinkel=90.0):
    """Lys rett inn mot prismesida: vinkelen kvar av dei to lobene går ut med, i grader."""
    a = math.radians(toppvinkel) / 2.0          # flanken står a frå loddlina; innfallsvinkelen på flanken er 90° - a
    i = math.pi / 2 - a
    r = math.asin(math.sin(i) / n)
    inne = i - r                                # vinkel frå filmnormalen inne i plasten
    return math.degrees(math.asin(n * math.sin(inne)))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    f = Film(prisme(90.0), n_d=1.59, abbe=30.0)
    print('n(450) %.4f  n(550) %.4f  n(650) %.4f' % (f.n(450), f.n(550), f.n(650)))
    print('analytisk splitt ved n(550): %.2f°' % analytisk_splitt(float(f.n(550))))
    for side in ('prisme', 'flat'):
        print('\nside inn:', side)
        print('  vinkel   T      R      tapt   lober (vinkel°, del)')
        for a, T, R, L in f.tabell(side):
            print('  %5.0f  %.3f  %.3f  %.4f  %s' % (a, T, R, 1 - T - R, '  '.join('%+.1f: %.2f' % e for e in L[:5])))
    print('\nfargebrot, prismeside inn, rett på:')
    for lam in (450, 500, 550, 600, 650):
        T, R, L = f.lober(0, 0, lam, 'prisme')
        print('  %d nm  n %.4f  lobe %+.2f° (analytisk %.2f°)' % (lam, f.n(lam), abs(L[0][0]), analytisk_splitt(float(f.n(lam)))))
