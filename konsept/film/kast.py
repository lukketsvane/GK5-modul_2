# -*- coding: utf-8 -*-
"""
kast.py  ·  lys utan linse: diode, maske og film kastar eit mønster ut i rommet

Kvart foton går frå ei lita diode, gjennom opningane i éi eller fleire masker, gjennom filmen (film.py, strålespora
per bølgjelengd) og ut i rommet. Skuggekanten (halvskuggen frå storleiken på dioden), smørja frå filmen og fargekanten
kjem ut av geometrien. Resultatet blir strøk for lysmotoren (same rom og same tal() som A, B og C) og lux-kart på
vegg og bord.

    from kast import Kast, maske, rekt
    k = Kast(pos, mot, W=1.25, K=2200, film=Film(...), riller=(1, 0, 0), side='prisme',
             a=0.05, s=0.002, masker=[maske(avstand=0.045, opningar=[rekt(-0.01, 0.01, -0.015, 0.015)])])
    lys = k.lys()            # liste med strøk til tal(), luminans() og par()
    k.kart_vegg, k.kart_bord # lux (rgb) utan skuggar frå rommet

Rekneskap: W er watten til dioden, 100 lm/W ved dioden (LMW_KJELDE i motoren). Alt som blir stoppa av maske, ramme
og film, er tapt. `k.rekneskap` viser kvar lyset blir av.
"""
import math, os, sys
import numpy as np
from numba import njit, prange
from scipy.ndimage import gaussian_filter

HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
sys.path.insert(0, os.path.join(HER, '..', 'lysskisse'))
import lysskisse as ls
from film import Film, prisme, _mikro

# ------------------------------------------------------------------ farge per bølgjelengd

LAM = np.arange(400, 701, 2).astype(float)

def _cmf(lam):
    def g(l, mu, s1, s2):
        s = np.where(l < mu, s1, s2)
        return np.exp(-0.5 * ((l - mu) / s) ** 2)
    x = 1.056 * g(lam, 599.8, 37.9, 31.0) + 0.362 * g(lam, 442.0, 16.0, 26.7) - 0.065 * g(lam, 501.1, 20.4, 26.2)
    y = 0.821 * g(lam, 568.8, 46.9, 40.5) + 0.286 * g(lam, 530.9, 16.3, 31.1)
    z = 1.217 * g(lam, 437.0, 11.8, 36.0) + 0.681 * g(lam, 459.0, 26.0, 13.8)
    return np.stack([x, y, z], 1)

XYZ_RGB = np.array([[3.2406, -1.5372, -0.4986], [-0.9689, 1.8758, 0.0415], [0.0557, -0.2040, 1.0570]])

def fotonfarge(K):
    """Vekt (rgb, i motoren sine einingar) for eit foton med bølgjelengd LAM[i]. Snittet over LAM har 1 i luminans,
    og summen har same farge som motoren gjev ei kjelde på K kelvin. ANTAKING: spekteret er ein svart lekam ved K."""
    l = LAM * 1e-9
    S = 1.0 / (l ** 5 * (np.exp(1.4388e-2 / (l * K)) - 1.0)); S /= S.max()
    rgb = (_cmf(LAM) @ XYZ_RGB.T) * S[:, None]
    C = rgb.sum(0)
    maal = ls.farge(K)                                  # luminans 1
    v = rgb * (maal / (C / (C @ ls.LUM)))
    return v / (v @ ls.LUM).mean()

# ------------------------------------------------------------------ masker

def rekt(u0, u1, v0, v1):
    """Rektangulær opning i maskeplanet (meter frå aksen)."""
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]

def maske(avstand, opningar, etter=False, normal=None, opp=None, senter=None):
    """Ei maske: eit plan med opningar (konvekse firkantar i maskeplanet).
    avstand: frå dioden langs aksen (meter). etter=True: maska står etter filmen. normal: maskeplanet si retning
    (standard: aksen). senter: eige senter i rommet (standard: på aksen)."""
    return dict(avstand=avstand, opningar=[list(q) for q in opningar], etter=etter, normal=normal, opp=opp, senter=senter)

def vindauge(breidd, hogd, kol=2, rad=3, sprosse=0.1, senter=(0.0, 0.0)):
    """Opningar for eit sprossevindauge. breidd, hogd: ytre mål i maskeplanet. sprosse: breidd på sprossene (del av ruta)."""
    cu, cv = senter
    bu = breidd / kol; bv = hogd / rad
    su = bu * sprosse / 2; sv = bv * sprosse / 2
    ut = []
    for i in range(kol):
        for j in range(rad):
            u0 = cu - breidd / 2 + i * bu; v0 = cv - hogd / 2 + j * bv
            ut.append(rekt(u0 + su, u0 + bu - su, v0 + sv, v0 + bv - sv))
    return ut

# ------------------------------------------------------------------ kjernen (numba)

@njit(cache=True)
def _i_firkant(q, a, b):
    pos = 0; neg = 0
    for i in range(4):
        j = (i + 1) % 4
        c = (q[j, 0] - q[i, 0]) * (b - q[i, 1]) - (q[j, 1] - q[i, 1]) * (a - q[i, 0])
        if c > 0: pos += 1
        elif c < 0: neg += 1
    return pos == 0 or neg == 0

@njit(cache=True)
def _plate(p, d, c, n, u, v, quad, nq):
    """Går strålen gjennom ei opning? Gjev (ja, t)."""
    den = d[0] * n[0] + d[1] * n[1] + d[2] * n[2]
    if abs(den) < 1e-12: return False, 0.0
    t = ((c[0] - p[0]) * n[0] + (c[1] - p[1]) * n[1] + (c[2] - p[2]) * n[2]) / den
    if t <= 0: return False, 0.0
    x0 = p[0] + t * d[0] - c[0]; x1 = p[1] + t * d[1] - c[1]; x2 = p[2] + t * d[2] - c[2]
    a = x0 * u[0] + x1 * u[1] + x2 * u[2]; b = x0 * v[0] + x1 * v[1] + x2 * v[2]
    for k in range(nq):
        if _i_firkant(quad[k], a, b): return True, t
    return False, t

@njit(parallel=True, cache=True)
def _kjerne(N, T, led_p, led_n, led_u, led_v, led_r, sin2max, sig_led,
            pl_c, pl_n, pl_u, pl_v, pl_q, pl_nq, pl_etter,
            f_c, f_x, f_y, f_z, f_w, f_h, px, pz, tj, ntab, s_x, s_y, haze,
            vtab, H, e1, e2, e3, nlat, nlon, YV, ZB, vgr, vnx, vnz, bgr, bnx, bny, maxb):
    tab = np.zeros((T, 3, nlat, nlon), np.float32)
    tabh = np.zeros((T, nlat, nlon), np.float32)
    vegg = np.zeros((T, 3, vnz, vnx), np.float32)
    bord = np.zeros((T, 3, bny, bnx), np.float32)
    stat = np.zeros((T, 6))
    P = len(pl_c); nl = len(ntab)
    per = N // T
    for th in prange(T):
        p = np.empty(3); d = np.empty(3); q = np.empty(3)
        for _ in range(per):
            # dioden: punkt på skiva, retning i kjegla
            r = led_r * math.sqrt(np.random.random()); ph = 2 * math.pi * np.random.random()
            cu = r * math.cos(ph); cv = r * math.sin(ph)
            for i in range(3): p[i] = led_p[i] + cu * led_u[i] + cv * led_v[i]
            if sig_led <= 0:                      # lambertsk, cosinusvekta innanfor kjegla
                s2 = np.random.random() * sin2max
                st = math.sqrt(s2); ct = math.sqrt(1 - s2); ph = 2 * math.pi * np.random.random()
                a = st * math.cos(ph); b = st * math.sin(ph)
            else:                                 # lykt: gaussisk stråle
                ta = math.tan(np.random.normal() * sig_led); tb = math.tan(np.random.normal() * sig_led)
                l = math.sqrt(1 + ta * ta + tb * tb); a = ta / l; b = tb / l; ct = 1 / l
            for i in range(3): d[i] = a * led_u[i] + b * led_v[i] + ct * led_n[i]
            il = np.random.randint(nl)
            stat[th, 0] += 1
            ok = True
            for k in range(P):
                if pl_etter[k]: continue
                ja, t = _plate(p, d, pl_c[k], pl_n[k], pl_u[k], pl_v[k], pl_q[k], pl_nq[k])
                if not ja:
                    ok = False; break
            if not ok: continue
            stat[th, 1] += 1
            # filmen
            den = d[0] * f_z[0] + d[1] * f_z[1] + d[2] * f_z[2]
            if abs(den) < 1e-9: continue
            t = ((f_c[0] - p[0]) * f_z[0] + (f_c[1] - p[1]) * f_z[1] + (f_c[2] - p[2]) * f_z[2]) / den
            if t <= 0: continue
            for i in range(3): q[i] = p[i] + t * d[i]
            xa = (q[0] - f_c[0]) * f_x[0] + (q[1] - f_c[1]) * f_x[1] + (q[2] - f_c[2]) * f_x[2]
            ya = (q[0] - f_c[0]) * f_y[0] + (q[1] - f_c[1]) * f_y[1] + (q[2] - f_c[2]) * f_y[2]
            if abs(xa) > f_w / 2 or abs(ya) > f_h / 2: continue
            stat[th, 2] += 1
            diffus = False
            if tj >= 0:
                d0 = d[0] * f_x[0] + d[1] * f_x[1] + d[2] * f_x[2]
                d1 = d[0] * f_y[0] + d[1] * f_y[1] + d[2] * f_y[2]
                d2 = den
                inn = 1 if d2 > 0 else -1
                d0, d1, d2, s = _mikro(px, pz, tj, ntab[il], d0, d1, d2, np.random.random(), maxb)
                if s != inn: continue
                if haze > 0 and np.random.random() < haze:
                    r = math.sqrt(np.random.random()); ph = 2 * math.pi * np.random.random()
                    d0 = r * math.cos(ph); d1 = r * math.sin(ph); d2 = s * math.sqrt(max(1 - r * r, 0.0)); diffus = True
                else:
                    if s_x > 0:
                        an = np.random.normal() * s_x; c = math.cos(an); sn = math.sin(an)
                        g0 = c * d0 + sn * d2; g2 = -sn * d0 + c * d2
                        if g2 * d2 > 0: d0 = g0; d2 = g2
                    if s_y > 0:
                        an = np.random.normal() * s_y; c = math.cos(an); sn = math.sin(an)
                        g1 = c * d1 + sn * d2; g2 = -sn * d1 + c * d2
                        if g2 * d2 > 0: d1 = g1; d2 = g2
                for i in range(3): d[i] = d0 * f_x[i] + d1 * f_y[i] + d2 * f_z[i]
            stat[th, 3] += 1
            ok = True
            for k in range(P):
                if not pl_etter[k]: continue
                ja, t = _plate(q, d, pl_c[k], pl_n[k], pl_u[k], pl_v[k], pl_q[k], pl_nq[k])
                if not ja:
                    ok = False; break
            if not ok: continue
            stat[th, 4] += 1
            # landing: vegg, bord eller langt ute
            tl = 2.0; kva = 0
            if d[1] > 1e-9:
                tv = (YV - q[1]) / d[1]
                if tv > 0 and tv < tl: tl = tv; kva = 1
            if d[2] < -1e-9:
                tb2 = (ZB - q[2]) / d[2]
                if tb2 > 0 and tb2 < tl: tl = tb2; kva = 2
            X0 = q[0] + tl * d[0]; X1 = q[1] + tl * d[1]; X2 = q[2] + tl * d[2]
            if kva == 1:
                ix = int((X0 - vgr[0]) / vgr[2]); iz = int((X2 - vgr[1]) / vgr[2])
                if ix >= 0 and ix < vnx and iz >= 0 and iz < vnz:
                    for c3 in range(3): vegg[th, c3, iz, ix] += vtab[il, c3]
            elif kva == 2:
                ix = int((X0 - bgr[0]) / bgr[2]); iy = int((X1 - bgr[1]) / bgr[2])
                if ix >= 0 and ix < bnx and iy >= 0 and iy < bny:
                    for c3 in range(3): bord[th, c3, iy, ix] += vtab[il, c3]
            h0 = X0 - H[0]; h1 = X1 - H[1]; h2 = X2 - H[2]
            l = math.sqrt(h0 * h0 + h1 * h1 + h2 * h2)
            h0 /= l; h1 /= l; h2 /= l
            sl = h0 * e3[0] + h1 * e3[1] + h2 * e3[2]
            lat = math.asin(max(-1.0, min(1.0, sl)))
            lon = math.atan2(h0 * e2[0] + h1 * e2[1] + h2 * e2[2], h0 * e1[0] + h1 * e1[1] + h2 * e1[2])
            ia = int((lat + math.pi / 2) / math.pi * nlat); io = int((lon + math.pi) / (2 * math.pi) * nlon)
            if ia >= nlat: ia = nlat - 1
            if io >= nlon: io = nlon - 1
            for c3 in range(3): tab[th, c3, ia, io] += vtab[il, c3]
            if diffus:
                tabh[th, ia, io] += vtab[il, 0] * 0.2126 + vtab[il, 1] * 0.7152 + vtab[il, 2] * 0.0722
                stat[th, 5] += 1
    return tab, tabh, vegg, bord, stat

# ------------------------------------------------------------------ kastet

VEGGRUTE = (-1.0, ls.ZB - 0.10, 0.004)        # x0, z0, rutestorleik: kartet dekkjer x -1..1, 10 cm under bordet til 1,5 m over
VEGG_N = (500, 400)
BORDRUTE = (-0.7, 0.0, 0.004)
BORD_N = (350, 175)

class Kast:
    """Diode + masker + film. pos: dioden. mot: punkt aksen peikar mot. a: avstand frå dioden til filmen (meter).
    s: diameteren på den lysande flata (meter). led: 'lambert' eller sigma i grader for ei lykt med eigen optikk.
    film: Film eller None (open ramme). riller: retninga rillene går i rommet. side: sida som vender mot dioden.
    film_normal: retninga den rifla sida peikar (standard: langs aksen, bestemt av side). film_storleik: (på tvers, langs rillene).
    masker: liste frå maske(). N: tal foton. opplaus: grader per rute i retningstabellen."""
    def __init__(s, pos, mot, W, K, film=None, riller=(1, 0, 0), side='prisme', a=0.05, diode=0.002, led='lambert',
                 film_normal=None, film_storleik=(0.04, 0.04), masker=(), N=4_000_000, opplaus=0.5, traadar=6,
                 glatt=0.6, namn='kast', frø=1):
        s.pos = np.asarray(pos, float); s.n = ls.nrm(np.asarray(mot, float) - s.pos)
        s.W, s.K, s.film, s.a, s.diode, s.led, s.namn = W, K, film, a, diode, led, namn
        s.lm_inn = W * ls.LMW_KJELDE
        s.H = s.pos + a * s.n                                  # filmsenteret
        g = np.asarray(riller, float); g = ls.nrm(g - (g @ s.n) * s.n) if film_normal is None else ls.nrm(g)
        if film_normal is None:
            fz = -s.n if side == 'prisme' else s.n             # rifla side mot dioden, eller bort frå han
        else:
            fz = ls.nrm(film_normal); g = ls.nrm(g - (g @ fz) * fz)
        s.fz, s.fy = fz, g; s.fx = np.cross(s.fy, s.fz)
        s.fw, s.fh = film_storleik
        # diodeplanet
        u, v = ls.ortho(s.n)
        # prøvekjegla: dekkjer filmramma sett frå dioden, med margin
        hj = [s.H + sx * s.fx * s.fw / 2 + sy * s.fy * s.fh / 2 for sx in (-1, 1) for sy in (-1, 1)]
        cmin = min(float(ls.nrm(h - s.pos) @ s.n) for h in hj)
        vmax = min(math.acos(max(cmin, 0.05)) + math.atan(diode / max(a, 1e-3)) + math.radians(2), math.radians(89))
        sin2 = math.sin(vmax) ** 2
        sig = 0.0 if led == 'lambert' else math.radians(float(led))
        s.del_i_kjegla = sin2 if led == 'lambert' else 1.0
        # masker
        P = len(masker); Q = max([len(m['opningar']) for m in masker] + [1])
        pl_c = np.zeros((max(P, 1), 3)); pl_n = np.zeros((max(P, 1), 3)); pl_u = np.zeros((max(P, 1), 3)); pl_v = np.zeros((max(P, 1), 3))
        pl_q = np.zeros((max(P, 1), Q, 4, 2)); pl_nq = np.zeros(max(P, 1), np.int64); pl_e = np.zeros(max(P, 1), np.bool_)
        s.masker = []
        for i, m in enumerate(masker):
            nm = s.n if m['normal'] is None else ls.nrm(m['normal'])
            c = s.pos + m['avstand'] * s.n if m['senter'] is None else np.asarray(m['senter'], float)
            mu, mv = ls.ortho(nm, m['opp'])
            pl_c[i], pl_n[i], pl_u[i], pl_v[i] = c, nm, mu, mv
            for k, q in enumerate(m['opningar']): pl_q[i, k] = np.asarray(q, float)
            pl_nq[i] = len(m['opningar']); pl_e[i] = m['etter']
            s.masker.append(dict(c=c, n=nm, u=mu, v=mv, opningar=m['opningar'], etter=m['etter']))
        if P == 0: pl_nq[0] = 0; pl_e[0] = False
        Pn = P
        # film
        if film is None:
            px = np.array([0.0, 1.0]); pz = np.array([0.0, 0.0]); tj = -1.0; ntab = np.ones(len(LAM)); sx = sy = hz = 0.0; Tx = 1.0
        else:
            px, pz, tj = film.px, film.pz, film.tjukn; ntab = film.n(LAM).astype(float)
            sx, sy, hz, Tx = math.radians(film.spreiing), math.radians(film.spreiing_langs), film.haze, film.T_ekstra
        # retningstabell: aksen på ekvator, polen langs rillene
        e3 = s.fy; e1 = ls.nrm(s.n - (s.n @ e3) * e3); e2 = np.cross(e3, e1)
        s.e1, s.e2, s.e3 = e1, e2, e3
        nlat = int(round(180 / opplaus)); nlon = 2 * nlat
        np.random.seed(frø)
        T = traadar
        tab, tabh, vegg, bord, stat = _kjerne(int(N), T, s.pos, s.n, u, v, diode / 2, sin2, sig,
                                              pl_c[:max(Pn, 1)] if Pn else pl_c[:0], pl_n[:Pn] if Pn else pl_n[:0],
                                              pl_u[:Pn] if Pn else pl_u[:0], pl_v[:Pn] if Pn else pl_v[:0],
                                              pl_q[:Pn] if Pn else pl_q[:0], pl_nq[:Pn] if Pn else pl_nq[:0],
                                              pl_e[:Pn] if Pn else pl_e[:0],
                                              s.H, s.fx, s.fy, s.fz, s.fw, s.fh, px, pz, tj, ntab, sx, sy, hz,
                                              fotonfarge(K), s.H, e1, e2, e3, nlat, nlon, ls.YV, ls.ZB,
                                              np.array(VEGGRUTE), VEGG_N[0], VEGG_N[1], np.array(BORDRUTE), BORD_N[0], BORD_N[1], 64)
        Nf = (int(N) // T) * T
        w = s.lm_inn * s.del_i_kjegla * Tx / Nf                 # lumen per foton
        tab = tab.sum(0).astype(float) * w; tabh = tabh.sum(0).astype(float) * w
        st = stat.sum(0)
        s.rekneskap = dict(lm_diode=s.lm_inn, i_kjegla=s.del_i_kjegla, gjennom_maske=st[1] / st[0], treff_film=st[2] / st[0],
                           gjennom_film=st[3] / max(st[2], 1), ut=st[4] / st[0], diffus=st[5] / max(st[4], 1),
                           lm_ut=float((tab * ls.LUM[:, None, None]).sum()))
        s.lm_ut = s.rekneskap['lm_ut']; s.verknad = s.lm_ut / s.lm_inn
        lat = (np.arange(nlat) + 0.5) / nlat * math.pi - math.pi / 2
        dO = np.cos(lat) * (math.pi / nlat) * (2 * math.pi / nlon)
        if glatt > 0:
            tab = gaussian_filter(tab, sigma=(0, glatt, glatt), mode=('nearest', 'nearest', 'wrap'))
            tabh = gaussian_filter(tabh, sigma=(glatt, glatt), mode=('nearest', 'wrap'))
        s.I = np.maximum(tab / dO[None, :, None], 0.0)          # cd per kanal (motoren sine rgb-einingar)
        s.Ih = np.maximum(tabh / dO[:, None], 0.0)              # cd, berre den diffuse delen
        s.nlat, s.nlon = nlat, nlon
        s.kart_vegg = np.moveaxis(vegg.sum(0).astype(float) * w / VEGGRUTE[2] ** 2, 0, -1)     # lux rgb, [z, x]
        s.kart_bord = np.moveaxis(bord.sum(0).astype(float) * w / BORDRUTE[2] ** 2, 0, -1)     # lux rgb, [y, x]
        # synleg lysande flate: biletet av dioden i filmen, smurt av filmen (ANTAKING: sjå API.md)
        smorje = 2.355 * (math.radians(film.spreiing) if film is not None else 0.0) * a
        s.A_bilete = max(diode * (diode + smorje), 1e-7)
        s.A_film = s.fw * s.fh

    # --- oppslag
    def _ij(s, d):
        la = np.arcsin(np.clip(d @ s.e3, -1, 1)); lo = np.arctan2(d @ s.e2, d @ s.e1)
        fa = (la + math.pi / 2) / math.pi * s.nlat - 0.5; fo = (lo + math.pi) / (2 * math.pi) * s.nlon - 0.5
        return fa, fo

    def _opp(s, tab, d):
        fa, fo = s._ij(d)
        a0 = np.clip(np.floor(fa).astype(int), 0, s.nlat - 2); o0 = np.floor(fo).astype(int)
        ta = np.clip(fa - a0, 0, 1); to = fo - o0
        o1 = (o0 + 1) % s.nlon; o0 = o0 % s.nlon
        return ((1 - ta) * (1 - to) * tab[a0, o0] + (1 - ta) * to * tab[a0, o1] + ta * (1 - to) * tab[a0 + 1, o0] + ta * to * tab[a0 + 1, o1])

    def cd(s, d):
        """Lysstyrke (cd, luminans) i retningane d (N,3) frå filmsenteret."""
        return sum(ls.LUM[c] * s._opp(s.I[c], d) for c in range(3))

    def lys(s):
        """Strøka til lysmotoren: eitt berande strøk (flata auget ser, watt) og tre fargekanalar."""
        ut = []
        prim = ls.Rekt(s.H - s.fx * s.fw / 2 - s.fy * s.fh / 2, s.fx * s.fw, s.fy * s.fh); prim.spoke = True
        def L(d):
            c = np.maximum(np.abs(d @ s.fz), 0.08)
            ih = s._opp(s.Ih, d)
            return np.maximum(s.cd(d) - ih, 0.0) / (s.A_bilete * c) + ih / (s.A_film * c)
        b = ls.Lys(s.lm_inn, s.K, prim, [s.H], lambda d: np.zeros(len(d)), L, s.namn)
        b.mater = True; b.lm_ut = 0.0; b.kast = s
        ut.append(b)
        for c in range(3):
            e = np.zeros(3); e[c] = 1.0
            pr = ls.Skive(s.H - 0.002 * s.n, s.n, 0.0005); pr.spoke = True
            l = ls.Lys(0.0, s.K, pr, [s.H], (lambda d, c=c: s._opp(s.I[c], d)), lambda d: np.zeros(len(d)), s.namn + '-' + 'rgb'[c])
            l.rgb = e; l.lm_ut = float(ls.LUM[c] * (s.I[c] * (np.cos((np.arange(s.nlat) + 0.5) / s.nlat * math.pi - math.pi / 2)
                                                             * (math.pi / s.nlat) * (2 * math.pi / s.nlon))[:, None]).sum())
            ut.append(l)
        return ut

def kartbilete(kart, lux_kvit=150.0, gamma=2.2):
    """Lux-kart (rgb) til bilete på svart. lux_kvit: lux som gjev 63 % av kvitt (same framkalling som motoren)."""
    img = 1 - np.exp(-np.maximum(kart, 0) / lux_kvit)
    return (np.clip(img, 0, 1) ** (1 / gamma) * 255 + 0.5).astype(np.uint8)[::-1]
