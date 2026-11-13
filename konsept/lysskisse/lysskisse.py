# -*- coding: utf-8 -*-
"""
lysskisse.py  ·  lysskisse på svart

Skissa er rommet, ikkje lampa. Svart er null lys, kvart strøk er lumen,
og lampa er ein svart kropp som berre syner seg der ho skuggar eller lyser.

Motor: lysgrep (strøk + svart kropp) -> rom -> luminansbilete (cd/m²) + tal().

  python lysskisse.py               begge bretta, tal.md og tal.csv
  python lysskisse.py --px 200      rask prøve
  python lysskisse.py --sjekk       kontroll mot analytiske svar
  python lysskisse.py --eitt vend   eitt lysgrep, stemning og arbeid
  LYSSKISSE_POLGE=1 python ...      med pølge-mannekengen som ryggfigur (modell/polge.py)
  python lysskisse.py --tal         berre tala

Einingar: meter, lumen, lux, cd/m². x mot høgre, y mot veggen, z opp.
Modell: punktprøvde kjelder, lambertske flater, radiositet mellom bord,
vegg og tak. Rommet elles er svart (ingen sidevegger, ikkje golv).
"""
import sys, os, csv, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

_HER = os.path.dirname(os.path.abspath(__file__))
PI = math.pi
LUM = np.array([0.2126, 0.7152, 0.0722])
EPS = 1e-5

# ------------------------------------------------------------------ hjelp

def nrm(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)

def ortho(n, opp=None):
    n = nrm(n)
    if opp is None:
        opp = (0, 0, 1) if abs(n[2]) < 0.9 else (0, 1, 0)
    u = nrm(np.cross(opp, n))
    return u, np.cross(n, u)

def sig(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40, 40)))

def kelvin_rgb(T):
    t = T / 100.0
    r = 255.0 if t <= 66 else 329.698727446 * ((t - 60) ** -0.1332047592)
    g = (99.4708025861 * math.log(t) - 161.1195681661) if t <= 66 else 288.1221695283 * ((t - 60) ** -0.0755148492)
    b = 255.0 if t >= 66 else (0.0 if t <= 19 else 138.5177312231 * math.log(t - 10) - 305.0447927307)
    return (np.clip([r, g, b], 0, 255) / 255.0) ** 2.2

KVITBALANSE = 3900            # kameraet er låst her: 2200 K les som rav, 6500 K som blått
def farge(T):
    c = kelvin_rgb(T) / kelvin_rgb(KVITBALANSE)
    return c / (c @ LUM)      # 1 lumen = 1 i luminanskanalen

def fib(n=120000):
    i = np.arange(n) + 0.5
    z = 1 - 2 * i / n
    r = np.sqrt(1 - z * z)
    ph = i * PI * (3 - math.sqrt(5))
    return np.stack([r * np.cos(ph), r * np.sin(ph), z], 1)
FIB = fib()

# ------------------------------------------------------------------ geometri

class Prim:
    rho = np.array([0.045, 0.045, 0.045])   # svart kropp
    lys = None
    kart = None
    spoke = False               # spøkelse: syner i biletet, skuggar ikkje

class Rekt(Prim):
    def __init__(s, o, u, v, rho=None):
        s.o, s.u, s.v = (np.asarray(a, float) for a in (o, u, v))
        s.n = nrm(np.cross(s.u, s.v)); s.uu = s.u @ s.u; s.vv = s.v @ s.v
        s.senter = s.o + s.u / 2 + s.v / 2
        if rho is not None: s.rho = np.asarray(rho, float)
    def t(s, O, D):
        with np.errstate(all='ignore'):
            dn = D @ s.n
            t = ((s.o - O) @ s.n) / dn
            P = O + t[:, None] * D - s.o
            a = (P @ s.u) / s.uu; b = (P @ s.v) / s.vv
            ok = (np.abs(dn) > 1e-12) & (t > EPS) & (a >= 0) & (a <= 1) & (b >= 0) & (b <= 1)
        return np.where(ok, t, np.inf)
    def normal(s, P):
        return np.broadcast_to(s.n, P.shape).copy()

class Skive(Prim):
    def __init__(s, c, n, r, rho=None):
        s.c = np.asarray(c, float); s.n = nrm(n); s.r = r; s.senter = s.c
        if rho is not None: s.rho = np.asarray(rho, float)
    def t(s, O, D):
        with np.errstate(all='ignore'):
            dn = D @ s.n
            t = ((s.c - O) @ s.n) / dn
            P = O + t[:, None] * D - s.c
            ok = (np.abs(dn) > 1e-12) & (t > EPS) & ((P * P).sum(1) <= s.r ** 2)
        return np.where(ok, t, np.inf)
    def normal(s, P):
        return np.broadcast_to(s.n, P.shape).copy()

class Kule(Prim):
    def __init__(s, c, r, rho=None):
        s.c = np.asarray(c, float); s.R = np.ones(3) * np.asarray(r, float); s.senter = s.c
        if rho is not None: s.rho = np.asarray(rho, float)
    def t(s, O, D):
        with np.errstate(all='ignore'):
            o = (O - s.c) / s.R; d = D / s.R
            a = (d * d).sum(1); b = (o * d).sum(1); c = (o * o).sum(1) - 1
            disk = b * b - a * c
            sq = np.sqrt(np.maximum(disk, 0))
            t1 = (-b - sq) / a; t2 = (-b + sq) / a
            t = np.where(t1 > EPS, t1, np.where(t2 > EPS, t2, np.inf))
        return np.where(disk >= 0, t, np.inf)
    def normal(s, P):
        n = (P - s.c) / s.R ** 2
        return n / np.linalg.norm(n, axis=1)[:, None]

class Syl(Prim):
    def __init__(s, a, b, r, rho=None):
        s.a = np.asarray(a, float); b = np.asarray(b, float)
        s.h = np.linalg.norm(b - s.a); s.ax = (b - s.a) / s.h; s.r = r
        s.senter = (s.a + b) / 2
        if rho is not None: s.rho = np.asarray(rho, float)
    def t(s, O, D):
        with np.errstate(all='ignore'):
            oc = O - s.a; dp = D @ s.ax; op = oc @ s.ax
            dq = D - dp[:, None] * s.ax; oq = oc - op[:, None] * s.ax
            A = (dq * dq).sum(1); B = (oq * dq).sum(1); C = (oq * oq).sum(1) - s.r ** 2
            disk = B * B - A * C
            sq = np.sqrt(np.maximum(disk, 0))
            best = np.full(len(O), np.inf)
            for tt in ((-B - sq) / A, (-B + sq) / A):
                z = op + tt * dp
                ok = (disk >= 0) & (A > 1e-14) & (tt > EPS) & (z >= 0) & (z <= s.h) & (tt < best)
                best = np.where(ok, tt, best)
            for z0 in (0.0, s.h):
                tt = (z0 - op) / dp
                q = oq + tt[:, None] * dq
                ok = (np.abs(dp) > 1e-12) & (tt > EPS) & ((q * q).sum(1) <= s.r ** 2) & (tt < best)
                best = np.where(ok, tt, best)
        return best
    def normal(s, P):
        oc = P - s.a; z = oc @ s.ax
        q = oc - z[:, None] * s.ax
        n = q / np.maximum(np.linalg.norm(q, axis=1), 1e-9)[:, None]
        n = np.where((z < 1e-4)[:, None], -s.ax, n)
        return np.where((z > s.h - 1e-4)[:, None], s.ax, n)

# ------------------------------------------------------------------ lys (strøka)

class Lys:
    """Eitt strøk: lumen, fargetemperatur, ei synleg flate og ei fordeling."""
    def __init__(s, lm, K, prim, pts, I, L, namn=''):
        s.lm = lm; s.K = K; s.rgb = farge(K); s.prim = prim; prim.lys = s
        s.pts = [np.asarray(p, float) for p in pts]; s.w = 1.0 / len(pts)
        s.I = I      # cd i retning d (einingsvektor frå kjelda), heile strøket
        s.L = L      # cd/m² mot d, det auget ser
        s.namn = namn

def _prover_rekt(c, u, v, w, h):
    f = lambda x: 1 if x < 0.06 else (3 if x < 0.22 else 5)
    nu, nv = f(w), f(h)
    return [c + u * w * ((i + 0.5) / nu - 0.5) + v * h * ((j + 0.5) / nv - 0.5) for i in range(nu) for j in range(nv)]

def _prover_skive(c, u, v, r):
    if r <= 0.05: return [c]
    return [c] + [c + 0.65 * r * (math.cos(a) * u + math.sin(a) * v) for a in np.arange(6) * PI / 3]

def _flateprim(c, n, u, v, storleik):
    if np.ndim(storleik) == 0:
        r = storleik / 2.0
        return Skive(c, n, r), PI * r * r, _prover_skive(c, u, v, r)
    w, h = storleik
    return Rekt(c - u * w / 2 - v * h / 2, u * w, v * h), w * h, _prover_rekt(c, u, v, w, h)

def glod(pos, r, lm, K=2700):
    """Glødande kule: lyser likt i alle retningar."""
    pos = np.asarray(pos, float)
    I = lambda d: np.full(len(d), lm / (4 * PI))
    L = lambda d: np.full(len(d), lm / (4 * PI * PI * r * r))
    return Lys(lm, K, Kule(pos, r), [pos], I, L, 'glød')

def royr(a, b, r, lm, K=2700):
    """Glødande røyr: lambertsk sideflate."""
    a = np.asarray(a, float); b = np.asarray(b, float); h = np.linalg.norm(b - a); ax = (b - a) / h
    pts = [a + (b - a) * (i + 0.5) / 5 for i in range(5)]
    I = lambda d: lm * np.sqrt(np.maximum(1 - (d @ ax) ** 2, 0)) / PI ** 2
    L = lambda d: np.full(len(d), lm / (PI * 2 * PI * r * h))
    return Lys(lm, K, Syl(a, b, r), pts, I, L, 'røyr')

def flate(senter, normal, storleik, lm, K=2700, tosidig=False, opp=None):
    """Lysande matt flate. storleik: diameter, eller (breidd, høgd)."""
    c = np.asarray(senter, float); n = nrm(normal); u, v = ortho(n, opp)
    prim, A, pts = _flateprim(c, n, u, v, storleik)
    if tosidig:
        I = lambda d: lm * np.abs(d @ n) / (2 * PI)
        L = lambda d: np.full(len(d), lm / (2 * PI * A))
    else:
        I = lambda d: lm * np.maximum(d @ n, 0) / PI
        L = lambda d: np.where(d @ n > 0, lm / (PI * A), 0.0)
    return Lys(lm, K, prim, pts, I, L, 'flate')

def maske_bord(x0, x1, y0, y1, k=0.012):
    """Skarp maske avbilda på bordet (profilprinsippet)."""
    def f(pos, d):
        dz = np.minimum(d[:, 2], -1e-6); t = (ZB - pos[2]) / dz
        x = pos[0] + t * d[:, 0]; y = pos[1] + t * d[:, 1]
        return np.where(d[:, 2] < 0, sig((x - x0) / k) * sig((x1 - x) / k) * sig((y - y0) / k) * sig((y1 - y) / k), 0.0)
    return f

def maske_vegg(cx, cz, r, k=0.012):
    """Skarp sirkel avbilda på veggen."""
    def f(pos, d):
        dy = np.maximum(d[:, 1], 1e-6); t = (YV - pos[1]) / dy
        x = pos[0] + t * d[:, 0]; z = pos[2] + t * d[:, 2]
        return np.where(d[:, 1] > 0, sig((r - np.hypot(x - cx, z - cz)) / k), 0.0)
    return f

def straale(pos, mot, lm, K=2700, spreiing=20, flat=None, kutt=None, horisont=None,
            maske=None, opning=0.03, sprut=0.02, opp=None, bronn=None):
    """Retta strøk frå ei opning.
    spreiing: sigma i grader. flat=(vassrett, loddrett) gjev vifte.
    kutt: avskjerming, grader frå aksen. horisont: ingen lys over denne høgdevinkelen.
    opning: radius, eller (breidd, høgd). sprut: del av lyset som lek diffust frå opninga.
    bronn: opninga ligg nedsenka, og ingenting syner eller lek ut over denne vinkelen frå aksen."""
    pos = np.asarray(pos, float); n = nrm(np.asarray(mot, float) - pos); u, v = ortho(n, opp)
    su, sv = np.radians(flat if flat is not None else (spreiing, spreiing))
    def g(d):
        c = d @ n
        if maske is not None:
            w = maske(pos, d)
        else:
            cc = np.maximum(c, 1e-6)
            w = np.exp(-0.5 * ((np.arctan2(d @ u, cc) / su) ** 2 + (np.arctan2(d @ v, cc) / sv) ** 2))
        if kutt is not None:
            w = w * sig(kutt - np.degrees(np.arccos(np.clip(c, -1, 1))))
        if horisont is not None:
            w = w * sig(horisont - np.degrees(np.arcsin(np.clip(d[:, 2], -1, 1))))
        return np.where(c > 0, w, 0.0)
    G = 4 * PI * g(FIB).mean()
    if np.ndim(opning) == 0:
        prim, A, pts = Skive(pos, n, opning), PI * opning ** 2, _prover_skive(pos, u, v, opning)
    else:
        w, h = opning
        prim, A, pts = Rekt(pos - u * w / 2 - v * h / 2, u * w, v * h), w * h, _prover_rekt(pos, u, v, w, h)
    if bronn is None:
        vegg = lambda d: 1.0
    else:
        vegg = lambda d: sig(bronn - np.degrees(np.arccos(np.clip(d @ n, -1, 1))))
    I = lambda d: lm * ((1 - sprut) * g(d) / G + sprut * np.maximum(d @ n, 0) / PI) * vegg(d)
    L = lambda d: np.where(d @ n > 0, I(d) / (A * np.maximum(d @ n, 0.08)), 0.0)
    l = Lys(lm, K, prim, pts, I, L, 'stråle'); l.akse = n
    return l

# ------------------------------------------------------------------ rommet

ZB = 0.72          # bordhøgd
YV = 0.70          # veggen
def b(x, y, h):    # punkt i bordkoordinatar: h er høgd over bordplata
    return np.array([x, y, ZB + h])

AUGE = b(0.0, -0.15, 0.47)        # 47 cm over bordet, 60 cm frå skjermen
FELT = b(0.0, 0.25, 0.0)          # midt i arbeidsfeltet, 0,6 x 0,4 m
FELTAREAL = 0.24

BORD = Rekt((-0.7, 0, ZB), (1.4, 0, 0), (0, 0.7, 0), rho=(0.50, 0.40, 0.30))
VEGG = Rekt((-1.7, YV, 0), (3.4, 0, 0), (0, 0, 2.5), rho=(0.74, 0.72, 0.68))
TAK = Rekt((-1.7, -1.9, 2.5), (0, 2.6, 0), (3.4, 0, 0), rho=(0.80, 0.80, 0.80))
STATIV = Syl(b(0, 0.47, 0), b(0, 0.47, 0.2), 0.018)
# ryggfiguren: brukaren er ein mørk kropp som berre lyset teiknar
_HUD = (0.30, 0.26, 0.24); _TOY = (0.20, 0.20, 0.22)
PERSON = [Kule(b(0, -0.25, 0.49), (0.085, 0.095, 0.105), rho=_HUD),
          Syl(b(0, -0.27, 0.30), b(0, -0.27, 0.42), 0.045, rho=_HUD),
          Syl(b(-0.17, -0.29, 0.29), b(0.17, -0.29, 0.29), 0.065, rho=_TOY),
          Kule(b(-0.17, -0.29, 0.29), 0.065, rho=_TOY), Kule(b(0.17, -0.29, 0.29), 0.065, rho=_TOY),
          Kule(b(0, -0.29, -0.02), (0.20, 0.115, 0.34), rho=_TOY)]
SKJERM_CD = 40.0   # ANTAKING: dempa skjerm med mørkt tema, snitt 40 cd/m²
SKJERMLYS = flate(b(0, 0.45, 0.265), (0, -1, 0), (0.54, 0.31), PI * SKJERM_CD * 0.54 * 0.31, 6000)
SKJERM = SKJERMLYS.prim
# arket er oppgåva: ei kvit flate i feltet som viser arbeidslyset. Det skuggar ikkje.
ARK = Rekt((0.02, 0.11, ZB + 0.001), (0.30, 0, 0), (0, 0.21, 0), rho=(0.82, 0.82, 0.80)); ARK.spoke = True
STATISK = [BORD, VEGG, TAK, SKJERM, STATIV, ARK] + PERSON

class Flatekart:
    def __init__(s, rekt, nu, nv):
        s.r = rekt; s.nu = nu; s.nv = nv; rekt.kart = s
        a, bb = np.meshgrid((np.arange(nu) + 0.5) / nu, (np.arange(nv) + 0.5) / nv, indexing='ij')
        s.P = rekt.o + a.reshape(-1, 1) * rekt.u + bb.reshape(-1, 1) * rekt.v
        s.N = np.broadcast_to(rekt.n, s.P.shape).copy()
        s.A = np.full(len(s.P), math.sqrt(rekt.uu * rekt.vv) / (nu * nv))
        s.RHO = np.broadcast_to(rekt.rho, s.P.shape).copy()
    def oppslag(s, P, E):
        q = P - s.r.o
        a = np.clip((q @ s.r.u) / s.r.uu * s.nu - 0.5, 0, s.nu - 1)
        c = np.clip((q @ s.r.v) / s.r.vv * s.nv - 0.5, 0, s.nv - 1)
        i0 = np.minimum(a.astype(int), s.nu - 2); j0 = np.minimum(c.astype(int), s.nv - 2)
        fa = (a - i0)[:, None]; fb = (c - j0)[:, None]
        return (E[i0, j0] * (1 - fa) * (1 - fb) + E[i0 + 1, j0] * fa * (1 - fb)
                + E[i0, j0 + 1] * (1 - fa) * fb + E[i0 + 1, j0 + 1] * fa * fb)

class Rom:
    def __init__(s):
        s.kart = [Flatekart(BORD, 28, 14), Flatekart(VEGG, 34, 25), Flatekart(TAK, 13, 17)]
        n0 = 0
        for k in s.kart:
            k.sl = slice(n0, n0 + len(k.P)); n0 += len(k.P)
        s.P = np.concatenate([k.P for k in s.kart]); s.N = np.concatenate([k.N for k in s.kart])
        s.A = np.concatenate([k.A for k in s.kart]); s.RHO = np.concatenate([k.RHO for k in s.kart])
        s.F = s._formfaktor([BORD, SKJERM] + PERSON)
        Ed = E_direkte(s.P, s.N, [SKJERMLYS], STATISK)
        s.Ei_skjerm, s.B_skjerm = s.radiositet(Ed)
    def _formfaktor(s, okkl):
        n = len(s.P); F = np.zeros((n, n), np.float32)
        for i0 in range(0, n, 256):
            sl = slice(i0, min(i0 + 256, n))
            d = s.P[None, :, :] - s.P[sl, None, :]
            r2 = (d * d).sum(2); r = np.sqrt(np.maximum(r2, 1e-12))
            ci = (d * s.N[sl, None, :]).sum(2) / r
            cj = -(d * s.N[None, :, :]).sum(2) / r
            f = np.where((ci > 1e-6) & (cj > 1e-6), ci * cj * s.A[None, :] / (PI * r2 + s.A[None, :]), 0.0)
            ii, jj = np.nonzero(f > 0)
            O = s.P[i0 + ii]; D = s.P[jj] - O
            vis = np.ones(len(ii), bool)
            for p in okkl:
                t = p.t(O, D); vis &= ~((t > 1e-4) & (t < 1 - 1e-4))
            f[ii, jj] *= vis
            F[sl] = f
        return F
    def radiositet(s, Ed):
        B = s.RHO * Ed
        for _ in range(5):
            B = s.RHO * (Ed + s.F @ B)
        return s.F @ B, B

_ROM = None
def rom():
    global _ROM
    if _ROM is None: _ROM = Rom()
    return _ROM

# ------------------------------------------------------------------ lysrekning

def synleg(P, s, okkl, hopp=None):
    D = s - P
    v = np.ones(len(P), bool)
    for p in okkl:
        if p is hopp or p.spoke: continue
        t = p.t(P, D)
        v &= ~((t > 1e-4) & (t < 1 - 1e-4))
    return v

def E_direkte(P, N, lysliste, okkl):
    """Lux (rgb) i punkta P med normal N, rett frå strøka."""
    E = np.zeros((len(P), 3))
    for l in lysliste:
        if isinstance(l, Ark):
            E += l.E_mot(P, N, okkl)[:, None] * l.rgb
            continue
        for s in l.pts:
            d = P - s
            r2 = np.maximum((d * d).sum(1), 1e-6)
            dn = d / np.sqrt(r2)[:, None]
            cosi = -(dn * N).sum(1)
            I = l.I(dn) * l.w
            m = np.flatnonzero((cosi > 1e-4) & (I > 1e-9))
            if not len(m): continue
            vis = synleg(P[m], s, okkl, l.prim)
            e = np.zeros(len(P)); e[m] = I[m] * cosi[m] / r2[m] * vis
            E += e[:, None] * l.rgb
    return E

def samle(p, n, B, okkl=()):
    """Lux (rgb) i eitt punkt frå radiositeten til romflatene."""
    R = rom()
    d = R.P - p; r2 = (d * d).sum(1); r = np.sqrt(r2)
    ci = (d @ n) / r; cj = -(d * R.N).sum(1) / r
    f = np.where((ci > 0) & (cj > 0), ci * cj * R.A / (PI * r2 + R.A), 0.0)
    if len(okkl):
        m = np.flatnonzero(f > 0)
        f[m] *= _synleg_par(p, R.P[m], okkl)
    return f @ B

def _synleg_par(p, Q, okkl):
    O = np.broadcast_to(p, Q.shape).copy(); D = Q - O
    v = np.ones(len(Q), bool)
    for o in okkl:
        t = o.t(O, D); v &= ~((t > 1e-4) & (t < 1 - 1e-4))
    return v

AKSAR = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], float)
def omgjevnad(senter, N, B):
    """Indirekte lys på små kroppar: seks retningar rundt senteret, vekta med normalen."""
    Ea = np.array([samle(senter, a, B) for a in AKSAR])
    w = np.maximum(N @ AKSAR.T, 0) ** 2
    return w @ Ea

# ------------------------------------------------------------------ ark: reflektoren som form
#
# Eit ark blir bøygd, falda og klipt. Kjelda lyser på arket, arket lyser på rommet.
# Kvar flis sender ut  E·A·(rd·cos/π + rs·g(δ)),  g = normalisert gausslobe rundt
# speglingsretninga (same modell som i konsept/fro/reflektoren.md).

MATT = dict(rd=0.85, rs=0.0, sigma=10.0)       # kvitlakkert eller matt
SATIN = dict(rd=0.15, rs=0.65, sigma=10.0)     # ANTAKING frå reflektor-frøa, ikkje målt
BLANK = dict(rd=0.03, rs=0.85, sigma=2.5)      # spegel
MORK = dict(rd=0.045, rs=0.0, sigma=10.0)      # svart bakside
LMW_KJELDE = 100.0                             # lm/W ut av kjeldeoptikken når ein reflektor kjem etter

class Nett(Prim):
    """Trekantnett med rask avvising mot omslutta kule."""
    def __init__(s, V0, V1, V2, flis):
        s.V0 = V0; s.E1 = V1 - V0; s.E2 = V2 - V0; s.flis = flis
        alle = np.concatenate([V0, V1, V2])
        s.c = alle.mean(0); s.r = float(np.linalg.norm(alle - s.c, axis=1).max()) + 1e-4
        s.senter = s.c; s.ark = None
    def t_idx(s, O, D):
        n = len(O); t = np.full(n, np.inf); idx = np.full(n, -1)
        with np.errstate(all='ignore'):
            oc = O - s.c; a = (D * D).sum(1); bq = (oc * D).sum(1); c = (oc * oc).sum(1) - s.r ** 2
            m = np.flatnonzero(bq * bq - a * c >= 0)
            steg = max(1, 600000 // len(s.V0))
            for i0 in range(0, len(m), steg):
                mm = m[i0:i0 + steg]
                Dm = D[mm][:, None, :]
                Pv = np.cross(Dm, s.E2[None])
                det = (s.E1[None] * Pv).sum(2); inv = 1.0 / det
                Tv = O[mm][:, None, :] - s.V0[None]
                u = (Tv * Pv).sum(2) * inv
                Q = np.cross(Tv, s.E1[None])
                v = (Dm * Q).sum(2) * inv
                tt = (s.E2[None] * Q).sum(2) * inv
                ok = (np.abs(det) > 1e-14) & (u >= 0) & (v >= 0) & (u + v <= 1) & (tt > EPS)
                tt = np.where(ok, tt, np.inf)
                k = tt.argmin(1); tk = tt[np.arange(len(mm)), k]
                t[mm] = tk; idx[mm] = np.where(np.isfinite(tk), k, -1)
        return t, idx
    def t(s, O, D):
        return s.t_idx(O, D)[0]

class Ark:
    """Reflektoren som lyskjelde. Bruk funksjonen ark() for å lage han."""
    def __init__(s, Pf, Nf, Af, tri, flis_tri, kjelder, framside, bakside, n_opt, tone, klynge, strekk):
        s.Pf, s.Nf, s.Af = Pf, Nf, Af
        s.prim = Nett(tri[0], tri[1], tri[2], flis_tri); s.prim.ark = s
        s.strekk = strekk
        s.kjelder = list(kjelder) if isinstance(kjelder, (list, tuple)) else [kjelder]
        no = Nf if n_opt is None else n_opt
        deler = []; s.lm_inn = 0.0
        for k in s.kjelder:
            inn = 0.0
            for pt in k.pts:
                d = Pf - pt; r2 = np.maximum((d * d).sum(1), 1e-8); dn = d / np.sqrt(r2)[:, None]
                c = -(dn * Nf).sum(1); fram = c > 0
                Fl = k.I(dn) * k.w * np.abs(c) / r2 * Af                  # lumen inn på kvar flis
                nl = np.where(fram[:, None], Nf, -Nf)
                nol = np.where(fram[:, None], no, -Nf)
                rr = dn - 2 * (dn * nol).sum(1)[:, None] * nol
                fin = lambda key: np.where(fram, framside[key], bakside[key])
                deler.append((Fl, nl, rr, fin('rd'), fin('rs'), np.radians(fin('sigma'))))
                inn += float(Fl.sum())
            k.lm_ut = max(k.lm - inn, 0.0); k.mater = True
            s.lm_inn += inn
        s.S = len(deler)
        s.Fl, s.nl, s.rr, s.rd, s.rs, s.sg = (np.stack([d[i] for d in deler]) for i in range(6))
        s.K = s.kjelder[0].K
        s.rgb = s.kjelder[0].rgb * (np.ones(3) if tone is None else np.asarray(tone, float))
        s.lm = s.lm_ut = float((s.Fl * (s.rd + s.rs)).sum() * (s.rgb @ LUM))
        s.klynger = []
        for kid in np.unique(klynge):
            ix = np.flatnonzero(klynge == kid)
            s.klynger.append((ix, Pf[ix].mean(0)))
    def E_mot(s, P, N, okkl):
        """Lux i punkta P frå arket (utan farge)."""
        E = np.zeros(len(P))
        for ix, c in s.klynger:
            m = np.flatnonzero(synleg(P, c, okkl, s.prim))
            if not len(m): continue
            steg = max(1, 300000 // (len(ix) * s.S))
            Pf = s.Pf[ix][None]
            for i0 in range(0, len(m), steg):
                mm = m[i0:i0 + steg]
                d = P[mm][:, None, :] - Pf
                r2 = np.maximum((d * d).sum(2), 1e-6); w = d / np.sqrt(r2)[..., None]
                cr = -(w * N[mm][:, None, :]).sum(2)
                e = 0.0
                for q in range(s.S):
                    co = (w * s.nl[q, ix][None]).sum(2)
                    x = 1 - np.clip((w * s.rr[q, ix][None]).sum(2), -1, 1)
                    sg = s.sg[q, ix][None]
                    g = np.exp(-(2 * x + x * x / 3) / (2 * sg * sg)) / (2 * PI * sg * sg)
                    e = e + np.where(co > 0, s.Fl[q, ix][None] * (s.rd[q, ix][None] * co / PI + s.rs[q, ix][None] * g), 0.0)
                E[mm] += np.where(cr > 0, e * cr / r2, 0.0).sum(1)
        return E
    def L_flis(s, fi, w):
        """cd/m² frå flis fi mot retninga w (einingsvektor frå flisa)."""
        L = np.zeros(len(fi))
        for q in range(s.S):
            co = (w * s.nl[q, fi]).sum(1)
            x = 1 - np.clip((w * s.rr[q, fi]).sum(1), -1, 1); sg = s.sg[q, fi]
            g = np.exp(-(2 * x + x * x / 3) / (2 * sg * sg)) / (2 * PI * sg * sg)
            L += np.where(co > 0, s.Fl[q, fi] / s.Af[fi] * (s.rd[q, fi] / PI + s.rs[q, fi] * g / np.maximum(co, 0.05)), 0.0)
        return L
    def L_mot(s, punkt, okkl):
        """Lysaste flis sett frå eit punkt (cd/m²)."""
        best = 0.0
        for ix, c in s.klynger:
            if synleg(punkt[None], c, okkl, s.prim)[0]:
                w = punkt - s.Pf[ix]; w = w / np.linalg.norm(w, axis=1)[:, None]
                best = max(best, float(s.L_flis(ix, w).max()))
        return best

def ark(kjelde, senter, normal, storleik=0.25, form=None, klipp=None, n=22, opp=None, rull=0.0,
        framside=MATT, bakside=MORK, fresnel=None, tone=None):
    """Reflektorark.
    kjelde: eitt eller fleire strøk som lyser på arket (ta dei med i lyslista òg, så blir spillet med).
    senter, normal: plass og retning for framsida av det flate arket. rull: dreiing i eige plan, grader.
    storleik: diameter (rund) eller (breidd langs u, høgd langs v).
    form(U, V) -> (X, Y, Z): bøying i arket sine eigne koordinatar, Z ut frå framsida. Sjå boy() og fald().
    klipp(u, v) -> bool: True der arket finst. framside/bakside: MATT, SATIN, BLANK, MORK eller eigen dict.
    fresnel: brennvidd i meter gjev eit flatt ark med fresnelspegel-normalar. tone: rgb-faktor, t.d. messing."""
    senter = np.asarray(senter, float); ez = nrm(normal); ex0, ey0 = ortho(ez, opp)
    cr, sr = math.cos(math.radians(rull)), math.sin(math.radians(rull))
    ex = cr * ex0 + sr * ey0; ey = np.cross(ez, ex)
    if np.ndim(storleik) == 0: w = h = float(storleik); rund = True
    else: w, h = storleik; rund = False
    nu = int(n); nv = max(2, int(round(n * h / w)))
    U, V = np.meshgrid(np.linspace(-w / 2, w / 2, nu + 1), np.linspace(-h / 2, h / 2, nv + 1), indexing='ij')
    X, Y, Z = (U, V, np.zeros_like(U)) if form is None else form(U, V)
    L3 = np.stack([X + 0 * U, Y + 0 * U, Z + 0 * U], -1)
    p00, p10, p01, p11 = L3[:-1, :-1], L3[1:, :-1], L3[:-1, 1:], L3[1:, 1:]
    cen = (p00 + p10 + p01 + p11) / 4
    nn = np.cross(p11 - p00, p01 - p10); ar = 0.5 * np.linalg.norm(nn, axis=-1); nn = nn / (2 * ar[..., None])
    uc = (U[:-1, :-1] + U[1:, 1:]) / 2; vc = (V[:-1, :-1] + V[1:, 1:]) / 2
    hald = np.ones(uc.shape, bool)
    if rund: hald &= uc ** 2 + vc ** 2 <= (w / 2) ** 2
    if klipp is not None: hald &= np.asarray(klipp(uc, vc), bool)
    strekk = 0.0                                   # kor mykje arket må tøyast: 0 for ei utfaldbar flate
    if form is not None and hald.any():
        e = 1e-5
        P3 = lambda a, c: np.stack([q + 0 * a for q in form(a, c)], -1)
        Xu = (P3(uc + e, vc) - P3(uc - e, vc)) / (2 * e); Xv = (P3(uc, vc + e) - P3(uc, vc - e)) / (2 * e)
        avvik = np.maximum(np.maximum(np.abs(np.linalg.norm(Xu, axis=-1) - 1), np.abs(np.linalg.norm(Xv, axis=-1) - 1)),
                           np.abs((Xu * Xv).sum(-1)))
        strekk = float(avvik[hald].max())
    verd = lambda L: senter + L[..., 0:1] * ex + L[..., 1:2] * ey + L[..., 2:3] * ez
    ret = lambda L: L[..., 0:1] * ex + L[..., 1:2] * ey + L[..., 2:3] * ez
    Pf = verd(cen)[hald]; Nf = ret(nn)[hald]; Af = ar[hald]
    n_opt = None
    if fresnel is not None:
        tilF = np.array([0.0, 0.0, fresnel]) - cen
        tilF = tilF / np.linalg.norm(tilF, axis=-1)[..., None]
        no = tilF + np.array([0.0, 0.0, 1.0]); no = no / np.linalg.norm(no, axis=-1)[..., None]
        n_opt = ret(no)[hald]
    w00, w10, w01, w11 = verd(p00)[hald], verd(p10)[hald], verd(p01)[hald], verd(p11)[hald]
    F = len(Pf); fi = np.arange(F)
    tri = (np.concatenate([w00, w00]), np.concatenate([w10, w11]), np.concatenate([w11, w01]))
    ii, jj = np.nonzero(hald)
    klynge = (ii * 3 // nu) * 3 + (jj * 3 // nv)
    return Ark(Pf, Nf, Af, tri, np.concatenate([fi, fi]), kjelde, framside, bakside, n_opt, tone, klynge, strekk)

def boy(kappa):
    """Sylindrisk bøy, altså ei utfaldbar flate: kappa er krumming i 1/m langs u (tal eller funksjon av u).
    Positiv krumming gjer framsida hol. Radius R svarar til kappa = 1/R."""
    def f(U, V):
        s = np.linspace(-0.5, 0.5, 4001); ds = s[1] - s[0]         # fast tabell, så same form gjev same flate
        k = kappa(s) if callable(kappa) else np.full_like(s, float(kappa))
        th = np.concatenate([[0.0], np.cumsum((k[1:] + k[:-1]) / 2 * ds)])
        i0 = int(np.argmin(np.abs(s))); th -= th[i0]
        x = np.concatenate([[0.0], np.cumsum((np.cos(th[1:]) + np.cos(th[:-1])) / 2 * ds)])
        z = np.concatenate([[0.0], np.cumsum((np.sin(th[1:]) + np.sin(th[:-1])) / 2 * ds)])
        return np.interp(U, s, x - x[i0]), V, np.interp(U, s, z - z[i0])
    return f

def fald(knekk):
    """Faldar parallelt med v: knekk = [(u-posisjon i meter, vinkel i grader), ...]. Positiv vinkel faldar mot framsida."""
    def kappa(s):
        k = np.zeros_like(s)
        for u0, a in knekk:
            k += math.radians(a) * np.exp(-0.5 * ((s - u0) / 0.0012) ** 2) / (0.0012 * math.sqrt(2 * PI))
        return k
    return boy(kappa)

def fresnelspegel(kjelde, senter, normal, f=0.1871, storleik=(0.285, 0.285), spreiing=2.5, n=30, **kw):
    """Fresnelspegelen frå overheadprojektoren: flat plate, brennvidd 187,1 mm, 285 x 285 mm.
    spreiing: sigma i grader. 2,5 er rein plate med lita kjelde, 8 til 14 er med diffusorark oppå."""
    return ark(kjelde, senter, normal, storleik=storleik, fresnel=f, n=n,
               framside=dict(rd=0.03, rs=0.85, sigma=spreiing), **kw)

def watt(t):
    """Budsjettet langs overgangen. t = 0 er stemning (1,25 W, 2200 K), t = 1 er arbeid (5 W, 3000 K).
    Gjev (W, K). Kjelde bak reflektor: lm = W * LMW_KJELDE. Strøk rett ut i rommet: lm = W * LMW."""
    t = {'s': 0.0, 'a': 1.0}.get(t, t)
    return 1.25 * 4.0 ** float(t), 2200 + 800 * float(t)

# ------------------------------------------------------------------ kamera og bilete

class Kamera:
    def __init__(s, C, T, fov):
        s.C = np.asarray(C, float); s.f = nrm(np.asarray(T, float) - s.C)
        s.r = nrm(np.cross(s.f, (0, 0, 1))); s.u = np.cross(s.r, s.f); s.h = math.tan(math.radians(fov / 2))
    def straaler(s, n):
        x = ((np.arange(n) + 0.5) / n * 2 - 1) * s.h
        X, Y = np.meshgrid(x, -x)
        D = s.f + X[..., None] * s.r + Y[..., None] * s.u
        D = D.reshape(-1, 3); D /= np.linalg.norm(D, axis=1)[:, None]
        return np.broadcast_to(s.C, D.shape).copy(), D

# Over høgre skulder: brukaren er ein mørk ryggfigur, rommet er motivet.
KAM = Kamera((0.98, -1.40, ZB + 0.80), (0.09, 0.42, ZB + 0.24), 43)

def luminans(lys, kropp, px=560, ss=2):
    """Luminansbilete i cd/m² (rgb), sett frå KAM."""
    R = rom()
    alle = list(lys) + [SKJERMLYS]
    prims = STATISK + list(kropp) + [l.prim for l in lys]
    Ed = E_direkte(R.P, R.N, lys, prims)
    Ei, B = R.radiositet(Ed)
    Ei = Ei + R.Ei_skjerm; B = B + R.B_skjerm
    n = px * ss
    O, D = KAM.straaler(n)
    tmin = np.full(len(O), np.inf); idx = np.full(len(O), -1)
    for k, p in enumerate(prims):
        t = p.t(O, D); m = t < tmin; tmin[m] = t[m]; idx[m] = k
    hdr = np.zeros((len(O), 3))
    for k, p in enumerate(prims):
        m = np.flatnonzero(idx == k)
        if not len(m): continue
        Dm = D[m]; P = O[m] + tmin[m, None] * Dm
        if p.lys is not None:
            hdr[m] = p.lys.L(-Dm)[:, None] * p.lys.rgb
            continue
        if isinstance(p, Nett):
            _, tr = p.t_idx(O[m], Dm)
            fi = np.where(tr >= 0, p.flis[np.maximum(tr, 0)], 0)
            hdr[m] = np.where(tr >= 0, p.ark.L_flis(fi, -Dm), 0.0)[:, None] * p.ark.rgb
            continue
        Nn = p.normal(P); snudd = (Nn * Dm).sum(1) > 0
        Nn = np.where(snudd[:, None], -Nn, Nn)
        E = E_direkte(P, Nn, alle, prims)
        if p.kart is not None:
            E += p.kart.oppslag(P, Ei[p.kart.sl].reshape(p.kart.nu, p.kart.nv, 3)) * (~snudd)[:, None]
        else:
            E += omgjevnad(p.senter, Nn, B)
        hdr[m] = p.rho * E / PI
    return hdr.reshape(n, n, 3)

L0 = 70.0     # låst eksponering: cd/m² som gjev 63 % av kvitt
def framkall(hdr, px, eksp=1.0):
    """Låst eksponering og slør frå sterke flater. Blending syner som utbrend flekk."""
    n = hdr.shape[0]; ss = n // px
    h = hdr.copy()
    for vekt, sigma in ((0.07, 0.010), (0.04, 0.035), (0.018, 0.10)):
        h += vekt * gaussian_filter(hdr, sigma=(sigma * n, sigma * n, 0))
    img = 1 - np.exp(-h * eksp / L0)
    img = img.reshape(px, ss, px, ss, 3).mean((1, 3))
    return (np.clip(img, 0, 1) ** (1 / 2.2) * 255 + 0.5).astype(np.uint8)

# ------------------------------------------------------------------ tal

LMW = 80.0          # lm/W ut av lampa (ramma)
CELLE = 15.1        # Wh brukbar i éi 21700-celle

def tal(lys, kropp):
    """Same tal på alle: berre lampa, skjermen er avslått i rekninga."""
    R = rom()
    okkl = STATISK + list(kropp) + [l.prim for l in lys]
    Ed = E_direkte(R.P, R.N, lys, okkl)
    Ei, B = R.radiositet(Ed)
    Y = (Ed + Ei) @ LUM
    kb, kv, kt = R.kart
    bord = Y[kb.sl].reshape(28, 14)
    felt = bord[8:20, 1:9]                                   # 0,6 x 0,4 m
    celler = felt.reshape(6, 2, 4, 2).mean((1, 3))           # rutenett 10 cm
    rest = (bord.sum() - felt.sum()) / (bord.size - felt.size)
    Pv = R.P[kv.sl]
    mv = (np.abs(Pv[:, 0]) < 0.7) & (Pv[:, 2] > ZB + 0.08) & (Pv[:, 2] < ZB + 0.78)
    flux = (Ed @ LUM) * R.A
    lm = sum(getattr(l, 'lm_ut', l.lm) for l in lys)
    W = sum(l.lm / (LMW_KJELDE if getattr(l, 'mater', False) else LMW) for l in lys if not isinstance(l, Ark))
    d = dict(lm=lm, W=W, strekk=max([l.strekk for l in lys if isinstance(l, Ark)] + [0.0]),
             E_felt=felt.mean(), U=celler.min() / max(celler.mean(), 1e-9),
             E_bord=rest, E_vegg=Y[kv.sl][mv].mean(),
             lm_bord=flux[kb.sl].sum(), lm_vegg=flux[kv.sl].sum(), lm_tak=flux[kt.sl].sum())
    d['nytte'] = d['E_felt'] * FELTAREAL / lm
    # ansikt: loddrett flate ved auget, vend mot skjermen
    okkl_a = [p for p in okkl if p not in PERSON]
    na = np.array([0.0, 1.0, 0.0])
    d['E_ansikt'] = float((E_direkte(AUGE[None], na[None], lys, okkl_a)[0] + samle(AUGE, na, B, [SKJERM])) @ LUM)
    # lys på skjermflata: loddrett lux på framsida, frå lampa åleine. Det blir gjenskin og et kontrasten.
    xs = np.linspace(-0.24, 0.24, 5); zs = ZB + np.linspace(0.14, 0.39, 3)
    Ps = np.array([[x, 0.447, z] for x in xs for z in zs]); Ns = np.tile([0.0, -1.0, 0.0], (len(Ps), 1))
    Es = E_direkte(Ps, Ns, lys, [p for p in okkl if p is not SKJERM]) @ LUM
    Es_ind = float(samle(np.array([0.0, 0.447, ZB + 0.265]), np.array([0.0, -1.0, 0.0]), B) @ LUM)
    d['E_skjerm'] = float(Es.mean()) + Es_ind
    d['E_skjerm_maks'] = float(Es.max()) + Es_ind
    # luminans mot auget: lampa sjølv, og lysaste romflate
    La = 0.0
    for l in lys:
        if isinstance(l, Ark):
            La = max(La, l.L_mot(AUGE, okkl_a)); continue
        for s in l.pts:
            if synleg(AUGE[None], s, okkl_a, l.prim)[0]:
                La = max(La, float(l.L(nrm(AUGE - s)[None])[0]))
    dv = R.P - AUGE
    framme = (dv[:, 1] / np.linalg.norm(dv, axis=1) > 0.2) & (np.arange(len(R.P)) < kv.sl.stop)
    d['L_lampe'] = La
    d['L_flate'] = float(((B @ LUM) / PI)[framme].max())
    # spegling i skjermen
    M = AUGE.copy(); M[1] = 2 * 0.45 - AUGE[1]
    Ls = 0.0
    okkl_s = [p for p in okkl if p is not SKJERM]
    for l in lys:
        if isinstance(l, Ark): continue          # spegling av arket i skjermen er ikkje rekna
        for s in l.pts:
            if s[1] >= 0.45: continue
            X = M + (s - M) * ((0.45 - M[1]) / (s[1] - M[1]))
            if abs(X[0]) < 0.27 and ZB + 0.11 < X[2] < ZB + 0.42 and synleg(X[None], s, okkl_s, l.prim)[0]:
                Ls = max(Ls, float(l.L(nrm(X - s)[None])[0]))
    d['L_spegl'] = Ls
    fb = flux[kb.sl].reshape(28, 14)
    soner = np.array([fb[8:20, 1:9].sum(), fb.sum() - fb[8:20, 1:9].sum(), flux[kv.sl][mv].sum(),
                      flux[kv.sl][~mv].sum(), flux[kt.sl].sum()])
    d['_fordeling'] = np.append(soner, max(lm - soner.sum(), 0.0)) / lm     # felt, bord, vegg nær, vegg elles, tak, rom
    return d

# ------------------------------------------------------------------ lysgrepa

SVART = None
def syl(a, c, r): return Syl(a, c, r)
def skive(c, n, r): return Skive(c, n, r)
def kule(c, r): return Kule(c, r)
def hovud(pos, n, r, l): return Syl(pos - l * n, pos - 0.004 * n, r)

A_LM, S_LM = 400.0, 100.0      # likt budsjett til alle: 5 W arbeid, 1,25 W stemning
A_K, S_K = 3000, 2200          # varmare når det blir dempa
def budsjett(m): return (A_LM, A_K) if m == 'a' else (S_LM, S_K)

def g_bordlykt(m):
    lm, K = budsjett(m)
    return [glod(b(0.47, 0.40, 0.25), 0.05, lm, K)], [syl(b(0.47, 0.40, 0), b(0.47, 0.40, 0.20), 0.016)]

def g_linsekule(m):
    lm, K = budsjett(m); c = b(0.47, 0.40, 0.30)
    ror = syl(b(0.47, 0.40, 0), b(0.47, 0.40, 0.268), 0.0125)
    if m == 's': return [glod(c, 0.035, lm, K)], [ror]
    n = nrm(FELT - c)
    return [straale(c + 0.037 * n, FELT, lm, K, spreiing=15, kutt=30, opning=0.033)], [ror, kule(c, 0.035)]

def g_plate(m):
    lm, K = budsjett(m)
    return ([flate(b(0.42, 0.41, 0.265), (-0.45, -0.89, 0.0), (0.20, 0.25), lm, K)],
            [syl(b(0.43, 0.43, 0), b(0.43, 0.43, 0.14), 0.006), syl(b(0.43, 0.43, 0), b(0.43, 0.43, 0.012), 0.05)])

def g_vend(m):
    lm, K = budsjett(m); c = b(0.47, 0.40, 0.41)
    kropp = [syl(b(0.47, 0.48, 0), b(0.47, 0.48, 0.05), 0.06), syl(b(0.47, 0.535, 0.05), b(0.47, 0.535, 0.42), 0.004)]
    if m == 's':
        n = nrm((-0.40, -0.55, -0.73)); l = flate(c, n, 0.25, lm, K)
    else:
        n = nrm(FELT - c); l = straale(c, FELT, lm, K, spreiing=12, opning=0.125, sprut=0.19)
    return [l], kropp + [skive(c - 0.004 * n, n, 0.127)]

def g_veggvask(m):
    lm, K = budsjett(m)
    mot = b(0, YV, 0.45) if m == 's' else b(0, YV, 0.95)
    l = straale(b(0, 0.60, 0.07), mot, lm, K, flat=(55, 24), kutt=80, opning=(0.30, 0.03))
    return [l], [syl(b(-0.17, 0.60, 0.03), b(0.17, 0.60, 0.03), 0.03)]

def g_skjermlist(m):
    lm, K = budsjett(m)
    kropp = [syl(b(-0.21, 0.455, 0.44), b(0.21, 0.455, 0.44), 0.015)]
    if m == 's':
        l = flate(b(0, 0.472, 0.44), (0, 1, 0), (0.40, 0.028), lm, K)
    else:
        l = straale(b(0, 0.438, 0.428), b(0, 0.20, 0), lm, K, flat=(42, 15), kutt=58, horisont=-20, opning=(0.40, 0.018))
    return [l], kropp

def g_snu(m):
    lm, K = budsjett(m); pos = b(0.40, 0.40, 0.40)
    mot = FELT if m == 'a' else b(0.75, YV, 0.75)
    n = nrm(mot - pos)
    l = straale(pos, mot, lm, K, spreiing=(26 if m == 'a' else 32), kutt=(48 if m == 'a' else 62), opning=0.045)
    return [l], [syl(b(0.40, 0.46, 0), b(0.40, 0.46, 0.40), 0.007), hovud(pos, n, 0.05, 0.07)]

def g_kryss(m):
    lm, K = budsjett(m)
    sokkel = syl(b(0.47, 0.42, 0), b(0.47, 0.42, 0.40), 0.028)
    opp = lambda f: straale(b(0.47, 0.42, 0.405), b(0.25, YV, 1.30), f, K, spreiing=36, kutt=70, opning=0.026)
    if m == 's': return [opp(lm)], [sokkel]
    ned = straale(b(0.435, 0.385, 0.37), FELT, 0.75 * lm, K, spreiing=28, kutt=48, opning=0.035)
    return [ned, opp(0.25 * lm)], [sokkel]

def g_lysoy(m):
    lm, K = budsjett(m); pos = b(0.40, 0.42, 0.13)
    if m == 'a': l = straale(pos, b(0.0, 0.25, 0), lm, K, flat=(40, 17), horisont=-6, opning=0.03)
    else: l = straale(pos, b(0.24, 0.35, 0), lm, K, spreiing=22, horisont=-6, opning=0.03)
    return [l], [kule(b(0.445, 0.445, 0.0), (0.06, 0.06, 0.15))]

def g_sidelys(m):
    lm, K = budsjett(m); pos = b(0.42, 0.32, 0.30)
    mot = b(-0.05, 0.25, 0) if m == 'a' else b(0.18, 0.30, 0)
    l = straale(pos, mot, lm, K, flat=(38, 14), horisont=-8, opning=(0.20, 0.025))
    return [l], [syl(b(0.445, 0.435, 0), b(0.445, 0.435, 0.315), 0.007), syl(b(0.44, 0.21, 0.315), b(0.44, 0.435, 0.315), 0.013)]

def g_retta(m):
    lm, K = budsjett(m)
    if m == 'a':
        pos = b(0.38, 0.38, 0.40)
        return ([straale(pos, FELT, lm, K, spreiing=24, kutt=45, opning=(0.20, 0.12), sprut=0.03)],
                [syl(b(0.42, 0.44, 0), b(0.42, 0.44, 0.40), 0.007)])
    return ([flate(b(0.38, 0.50, 0.36), (0, 1, 0), (0.20, 0.12), lm, K)],
            [syl(b(0.40, 0.485, 0), b(0.40, 0.485, 0.40), 0.007)])

def g_profil(m):
    lm, K = budsjett(m); pos = b(0.50, 0.40, 0.36)
    if m == 'a':
        mot = FELT; l = straale(pos, mot, lm, K, maske=maske_bord(-0.3, 0.3, 0.05, 0.45), opning=0.03)
    else:
        mot = b(0.0, YV, 0.33); l = straale(pos, mot, lm, K, maske=maske_vegg(0.0, ZB + 0.33, 0.30), opning=0.03)
    n = nrm(mot - pos)
    return [l], [syl(b(0.50, 0.46, 0), b(0.50, 0.46, 0.34), 0.008), hovud(pos, n, 0.035, 0.10)]

def g_arbeidslampe(m):
    lm, K = budsjett(m); pos = b(0.28, 0.38, 0.45); n = nrm(FELT - pos)
    l = straale(pos, FELT, lm, K, spreiing=27, kutt=50, opning=0.045)
    return [l], [syl(b(0.56, 0.60, 0), b(0.56, 0.60, 0.02), 0.07), syl(b(0.56, 0.60, 0.02), b(0.50, 0.56, 0.36), 0.006),
                 syl(b(0.50, 0.56, 0.36), pos - 0.07 * n, 0.006), hovud(pos, n, 0.055, 0.07)]

def g_zoom(m):
    lm, K = budsjett(m); pos = b(0.36, 0.41, 0.42)
    if m == 'a': mot = FELT; l = straale(pos, mot, lm, K, spreiing=30, kutt=50, opning=0.035)
    else: mot = b(0.36, 0.41, 0); l = straale(pos, mot, lm, K, spreiing=10, kutt=25, opning=0.035)
    n = nrm(mot - pos)
    return [l], [syl(b(0.52, 0.56, 0), b(0.52, 0.56, 0.45), 0.007), syl(b(0.52, 0.56, 0.45), b(0.38, 0.43, 0.46), 0.007),
                 hovud(pos, n, 0.04, 0.06)]

def g_hogd(m):
    lm, K = budsjett(m)
    if m == 's':
        l = straale(b(0.46, 0.40, 0.20), b(0.46, 0.40, 0), lm, K, spreiing=42, kutt=68, horisont=-10, opning=0.05)
        return [l], [syl(b(0.46, 0.49, 0), b(0.46, 0.49, 0.215), 0.012), skive(b(0.46, 0.42, 0.206), (0, 0, 1), 0.085)]
    l = straale(b(0.42, 0.40, 0.60), b(0.06, 0.25, 0), lm, K, spreiing=30, kutt=40, opning=0.05)
    return [l], [syl(b(0.46, 0.49, 0), b(0.46, 0.49, 0.615), 0.012), skive(b(0.43, 0.42, 0.606), (0, 0, 1), 0.085)]

def g_dokk(m):
    lm, K = budsjett(m); mast = syl(b(0.47, 0.46, 0), b(0.47, 0.46, 0.60), 0.008)
    if m == 's':
        l = straale(b(0.30, 0.10, 0.11), b(0.30, 0.10, 0), lm, K, spreiing=40, kutt=70, horisont=-12, opning=0.04)
        return [l], [mast, syl(b(0.30, 0.10, 0.114), b(0.30, 0.10, 0.135), 0.05), syl(b(0.30, 0.155, 0), b(0.30, 0.155, 0.114), 0.005)]
    pos = b(0.44, 0.40, 0.60); n = nrm(FELT - pos)
    return [straale(pos, FELT, lm, K, spreiing=24, kutt=42, opning=0.04)], [mast, hovud(pos, n, 0.05, 0.022)]

# rekkjefølgja er brettet, rad for rad
GREP = [
    ('bordlykt',     g_bordlykt,     'busett', 'glødande kule, dimma opp'),
    ('linsekule',    g_linsekule,    'S12',    'kula gløder, eller er linse mot feltet'),
    ('plate',        g_plate,        'S9',     'ståande lysande plate mot ansiktet'),
    ('vend',         g_vend,         'S2',     'skive med matt og retta side'),
    ('veggvask',     g_veggvask,     'S1',     'skjult list bak skjermen, veggen lyser'),
    ('skjermlist',   g_skjermlist,   'busett', 'list på skjermkanten, fram eller bak'),
    ('snu',          g_snu,          'S6',     'hovudet snur frå feltet til veggen'),
    ('kryss',        g_kryss,        'S10',    'to kammer, lyset flyttar opp og ned'),
    ('lysoy',        g_lysoy,        'S3',     'låg kropp, strøk langs bordet'),
    ('sidelys',      g_sidelys,      'S3',     'list under augehøgd, vifte over feltet'),
    ('retta',        g_retta,        'S8',     'flate med retning, vend mot veggen i stemning'),
    ('profil',       g_profil,       'S4',     'maske og linse: skarpt felt, sol bak skjermen'),
    ('arbeidslampe', g_arbeidslampe, 'busett', 'arm og avskjerma hovud, dimma ned'),
    ('zoom',         g_zoom,         'S5',     'lysmynt som opnar seg til felt'),
    ('hogd',         g_hogd,         'S11',    'lyspunktet går frå 20 til 60 cm'),
    ('dokk',         g_dokk,         'S7',     'laus lysøy som blir arbeidslys på masta'),
]

# ------------------------------------------------------------------ brett

def _arbeid(arg):
    i, m, px, ss = arg
    namn, f = GREP[i][0], GREP[i][1]
    lys, kropp = f(m)
    return i, m, framkall(luminans(lys, kropp, px, ss), px), tal(lys, kropp)

def _font(st):
    for p in (os.path.join(_HER, '..', '..', 'leveransar', '01_fase1_sider', 'fonts', 'EBGaramond12-Regular.otf'),):
        if os.path.exists(p): return ImageFont.truetype(p, st)
    return ImageFont.load_default()

def brett(bilete, px, merk=None, luft=16, kol=4):
    rader = -(-len(bilete) // kol)
    im = Image.new('RGB', (kol * px + (kol + 1) * luft, rader * px + (rader + 1) * luft), (0, 0, 0))
    dr = ImageDraw.Draw(im); fo = _font(max(12, px // 26))
    for k, a in enumerate(bilete):
        x = luft + (k % kol) * (px + luft); y = luft + (k // kol) * (px + luft)
        im.paste(Image.fromarray(a), (x, y))
        if merk:
            dr.text((x + px // 40, y + px - px // 9), merk[k], font=fo, fill=(168, 150, 128), spacing=2)
    return im

def likskap(a, c):
    return float(a @ c / (np.linalg.norm(a) * np.linalg.norm(c) + 1e-12))

def f0(x): return f'{x:.0f}'

def skriv_tal(T):
    """T[m][i] = tal. Skriv tal.csv og tal.md."""
    felt = ['lm', 'E_felt', 'U', 'nytte', 'E_bord', 'E_vegg', 'E_ansikt', 'L_lampe', 'L_flate', 'L_spegl', 'lm_bord', 'lm_vegg', 'lm_tak']
    with open(os.path.join(_HER, 'tal.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(['nr', 'namn', 'steg', 'tilstand'] + felt + ['lm_for_350lx', 'timar_per_celle', 'likskap_s_a'])
        for i, g in enumerate(GREP):
            lik = likskap(T['s'][i]['_fordeling'], T['a'][i]['_fordeling'])
            for m in 'sa':
                d = T[m][i]; need = d['lm'] * 350 / max(d['E_felt'], 1e-9)
                w.writerow([i + 1, g[0], g[2], {'s': 'stemning', 'a': 'arbeid'}[m]] + [f'{d[k]:.3g}' for k in felt]
                           + [f'{need:.0f}', f'{CELLE / (need / LMW):.1f}', f'{lik:.2f}'])
    L = []
    L.append('# Tal til lysbretta\n')
    L.append(f'Generert av `lysskisse.py`. Likt budsjett til alle: {A_LM:.0f} lm i arbeid ({A_LM/LMW:.1f} W) og {S_LM:.0f} lm i stemning. '
             'Tala gjeld lampa åleine i eit svart rom med éin vegg og tak. Modell, ikkje måling.\n')
    L.append('Rekkjefølgja er brettet, rad for rad.\n')
    L.append('| Nr. | Lysgrep | Steg | Felt, lx | Jamnheit | Lysnytte | lm for 350 lx | Timar per celle | Vegg, lx | Ansikt, lx | Mot auget, cd/m² | Mot auget ved 350 lx | Stemning: mot auget, cd/m² | Stemning: felt, lx | Likskap |')
    L.append('| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |')
    for i, g in enumerate(GREP):
        a, s = T['a'][i], T['s'][i]
        need = a['lm'] * 350 / max(a['E_felt'], 1e-9)
        lik = likskap(s['_fordeling'], a['_fordeling'])
        L.append(f"| {i+1} | {g[0]} | {g[2]} | {f0(a['E_felt'])} | {a['U']:.2f} | {a['nytte']*100:.0f} % | {f0(need)} | {CELLE/(need/LMW):.1f} | "
                 f"{f0(a['E_vegg'])} | {f0(a['E_ansikt'])} | {f0(max(a['L_lampe'], a['L_flate']))} | {f0(max(a['L_lampe'], a['L_flate']) * need / a['lm'])} | "
                 f"{f0(max(s['L_lampe'], s['L_flate']))} | {f0(s['E_felt'])} | {lik:.2f} |")
    L.append('')
    L.append('Lesenøkkel. Felt: snitt på 0,6 × 0,4 m. Jamnheit: lågaste rute delt på snittet, rutenett 10 cm. '
             'Lysnytte: lumen på feltet delt på lumen ut. Golvet er 84 lm (350 lx × 0,24 m²). '
             f'Timar per celle: {CELLE} Wh ved {LMW:.0f} lm/W. Vegg: sona rundt skjermen. Ansikt: loddrett ved auget, utan skjermen. '
             'Mot auget: lysaste av lampa og romflatene, sett frå 47 cm over bordet, først ved 400 lm, så skalert til 350 lx på feltet. '
             'Likskap: cosinus mellom lysfordelinga i stemning og arbeid. Over 0,9 er lampa ein dimmar, ikkje ein overgang.\n')
    sp = [(g[0], T[m][i]['L_spegl'], m) for i, g in enumerate(GREP) for m in 'sa' if T[m][i]['L_spegl'] > 1]
    L.append('Spegling i skjermen: ' + (', '.join(f"{n} ({'arbeid' if m=='a' else 'stemning'}, {v:.0f} cd/m²)" for n, v, m in sp) if sp else 'ingen kjelde ligg i spegelsona.') + '\n')
    open(os.path.join(_HER, 'tal.md'), 'w', encoding='utf-8').write('\n'.join(L))

def lag_brett(px=560, ss=2, prosessar=6):
    from multiprocessing import Pool
    jobbar = [(i, m, px, ss) for m in 'sa' for i in range(len(GREP))]
    with Pool(prosessar) as p:
        res = p.map(_arbeid, jobbar, chunksize=1)
    B = {'s': [None] * 16, 'a': [None] * 16}; T = {'s': [None] * 16, 'a': [None] * 16}
    for i, m, img, d in res:
        B[m][i] = img; T[m][i] = d
    for m, namn in (('a', 'arbeid'), ('s', 'stemning')):
        hale = '' if px >= 400 else '-prove'      # ei rask prøve skriv ikkje over fullversjonen
        brett(B[m], px).save(os.path.join(_HER, f'brett-{namn}{hale}.png'))
        merk = []
        for i, g in enumerate(GREP):
            d = T[m][i]
            merk.append(f"{i+1}  {g[0]}\nfelt {d['E_felt']:.0f} lx · vegg {d['E_vegg']:.0f} lx · auge {max(d['L_lampe'], d['L_flate']):.0f} cd/m²")
        brett(B[m], px, merk).save(os.path.join(_HER, f'brett-{namn}-merkt{hale}.png'))
    skriv_tal(T)
    return T

# ------------------------------------------------------------------ familiar og overgangar

def som_t(g):
    """Gjer eit gammalt lysgrep g('s'|'a') om til g(t), til bruk som referanse i ein familie."""
    return lambda t: g('a' if t >= 0.5 else 's')

def _rad(namn, s, a):
    Ea = max(a['E_felt'], 1e-9); La = max(a['L_lampe'], a['L_flate']); Ls = max(s['L_lampe'], s['L_flate'])
    W350 = a['W'] * 350 / Ea
    return dict(namn=namn, W=a['W'], lm=a['lm'], felt=a['E_felt'], jamnheit=a['U'], nytte=a['nytte'], W350=W350,
                timar=CELLE / W350, vegg=a['E_vegg'], ansikt=a['E_ansikt'], auge=La, auge350=La * 350 / Ea,
                s_auge=Ls, s_felt=s['E_felt'], s_vegg=s['E_vegg'], s_W=s['W'],
                skjerm=a['E_skjerm'], skjerm_del=a['E_skjerm'] / Ea, s_skjerm=s['E_skjerm'],
                likskap=likskap(s['_fordeling'], a['_fordeling']), strekk=max(a['strekk'], s['strekk']))

def familie(greps, mappe, px=200, ss=1):
    """greps: [(namn, g)] der g(t) -> (lys, kropp), t = 0 er stemning og t = 1 er arbeid.
    Skriv tal.md og tal.csv, og med px > 0 òg brett-stemning.png og brett-arbeid.png, i mappe.
    Gjev ei liste med éi rad (dict) per lysgrep."""
    os.makedirs(mappe, exist_ok=True)
    rader = []; B = {0.0: [], 1.0: []}; merk = {0.0: [], 1.0: []}
    for i, (namn, g) in enumerate(greps):
        T = {}
        for t in (0.0, 1.0):
            lys, kropp = g(t)
            T[t] = tal(lys, kropp)
            if px:
                B[t].append(framkall(luminans(lys, kropp, px, ss), px))
                merk[t].append(f"{i+1}  {namn}\nfelt {T[t]['E_felt']:.0f} lx · vegg {T[t]['E_vegg']:.0f} lx · auge {max(T[t]['L_lampe'], T[t]['L_flate']):.0f} cd/m²")
        rader.append(_rad(namn, T[0.0], T[1.0]))
    if px:
        for t, n in ((1.0, 'arbeid'), (0.0, 'stemning')):
            brett(B[t], px).save(os.path.join(mappe, f'brett-{n}.png'))
            brett(B[t], px, merk[t]).save(os.path.join(mappe, f'brett-{n}-merkt.png'))
    kol = ['namn', 'W', 'lm', 'felt', 'jamnheit', 'nytte', 'W350', 'timar', 'vegg', 'ansikt', 'auge', 'auge350',
           's_auge', 's_felt', 's_vegg', 's_W', 'likskap', 'strekk', 'skjerm', 'skjerm_del', 's_skjerm']
    with open(os.path.join(mappe, 'tal.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(kol)
        for r in rader: w.writerow([r[k] if k == 'namn' else f'{r[k]:.4g}' for k in kol])
    L = ['| Nr. | Lysgrep | W | lm ut | Felt, lx | Jamnheit | Lysnytte | W for 350 lx | Timar per celle | Vegg, lx | Ansikt, lx | Mot auget, cd/m² | Mot auget ved 350 lx | Stemning: mot auget | Stemning: felt, lx | Stemning: vegg, lx | Likskap | Strekk | Skjermflata, lx | Skjermflata / felt |',
         '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for i, r in enumerate(rader):
        L.append(f"| {i+1} | {r['namn']} | {r['W']:.2f} | {r['lm']:.0f} | {r['felt']:.0f} | {r['jamnheit']:.2f} | {r['nytte']*100:.0f} % | {r['W350']:.2f} | {r['timar']:.1f} | "
                 f"{r['vegg']:.0f} | {r['ansikt']:.0f} | {r['auge']:.0f} | {r['auge350']:.0f} | {r['s_auge']:.0f} | {r['s_felt']:.0f} | {r['s_vegg']:.0f} | {r['likskap']:.2f} | {r['strekk']*100:.2f} % | {r['skjerm']:.0f} | {r['skjerm_del']:.2f} |")
    open(os.path.join(mappe, 'tal.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    return rader

def overgang(g, n=7):
    """Gå overgangen i n steg frå stemning (t = 0) til arbeid (t = 1). Gjev (tal per steg, mål).
    topp: lysaste mellomsteg mot auget delt på lysaste endepunkt. Over 1 er blending undervegs.
    sprang: største endring i lysfordelinga mellom to nabosteg. 0 er glatt, 1 er at alt lyset byter adresse i eitt steg.
    jamn_auke: del av stega der lux på feltet aukar."""
    ts = np.linspace(0, 1, n); R = [tal(*g(float(t))) for t in ts]
    L = np.array([max(r['L_lampe'], r['L_flate']) for r in R])
    Ef = np.array([r['E_felt'] for r in R])
    spr = [1 - likskap(R[i]['_fordeling'], R[i + 1]['_fordeling']) for i in range(n - 1)]
    return R, dict(t=ts.tolist(), auge=L.tolist(), felt=Ef.tolist(), vegg=[r['E_vegg'] for r in R],
                   topp=float(L[1:-1].max() / max(L[0], L[-1], 1e-9)) if n > 2 else 1.0,
                   sprang=float(max(spr)), jamn_auke=float((np.diff(Ef) > 0).mean()))

def par(g, fil, px=420, ss=2, steg=(0.0, 1.0)):
    """Bilete av overgangen: eitt rom per t i steg, side om side. Til prøve: px=200, ss=1."""
    ruter = [framkall(luminans(*g(float(t)), px, ss), px) for t in steg]
    brett(ruter, px, kol=len(ruter)).save(fil)

# ------------------------------------------------------------------ kontroll

def sjekk():
    l = glod(b(0, 0.25, 0.5), 0.03, 1000)
    E = E_direkte(b(0, 0.25, 0)[None], np.array([[0, 0, 1.0]]), [l], [])[0] @ LUM
    print(f'1 avstandslova: {E:.1f} lx, analytisk {1000/(4*PI)/0.25:.1f}')
    l = flate((0, 0, 0), (0, 0, 1), 0.25, 154)
    E = E_direkte(np.array([[0, 0, 0.671]]), np.array([[0, 0, -1.0]]), [l], [])[0] @ LUM
    Lu = 154 / (PI * PI * 0.125 ** 2)
    print(f'2 lambertsk skive: {E:.1f} lx, analytisk {PI*Lu*0.125**2/(0.125**2+0.671**2):.1f} (L = {Lu:.0f} cd/m²)')
    l = glod((0, 0, 0), 0.035, 158)
    print(f'3 kule Ø 7 cm, 158 lm: {l.L(np.array([[1.0, 0, 0]]))[0]:.0f} cd/m², formromkartet seier 3270')
    for namn, l in (('stråle 20°', straale((0, 0, 1), (0, 0, 0), 400, spreiing=20, kutt=50)),
                    ('vifte med horisont', straale((0, 0, 1), (1, 0, 0.5), 400, flat=(40, 15), horisont=-6)),
                    ('maske', straale(b(0.52, 0.54, 0.36), FELT, 400, maske=maske_bord(-0.3, 0.3, 0.05, 0.45)))):
        print(f'4 lumen i {namn}: {4*PI*l.I(FIB).mean():.1f} av 400')
    l = straale(b(0.52, 0.54, 0.36), FELT, 400, maske=maske_bord(-0.3, 0.3, 0.05, 0.45), sprut=0.0)
    R = rom(); kb = R.kart[0]
    Ed = E_direkte(R.P[kb.sl], R.N[kb.sl], [l], []) @ LUM
    print(f'5 maska legg {float((Ed*R.A[kb.sl]).sum()):.0f} av 400 lm på bordet (ventar om lag 400)')
    print(f'6 formfaktor: største radsum {float(R.F.sum(1).max()):.2f} (skal vere under 1)')

# ------------------------------------------------------------------ mannekengen

def bruk_polge(**kw):
    """Byt ryggfiguren av kuler og sylindrar ut med pølge-mannekengen frå modell/polge.py.
    Må kallast før rom(). Set LYSSKISSE_POLGE=1 i miljøet for å slå han på overalt, òg i
    prosessane til lag_brett(). Tala for lampa åleine hoppar over figuren som før."""
    if _ROM is not None:
        raise RuntimeError('bruk_polge() må kallast før rom()')
    d = os.path.normpath(os.path.join(_HER, '..', '..', 'modell'))
    if d not in sys.path: sys.path.insert(0, d)
    import polge
    return polge.byt(sys.modules[__name__], **kw)

if os.environ.get('LYSSKISSE_POLGE') == '1':
    bruk_polge()

# ------------------------------------------------------------------ hovud

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    a = sys.argv[1:]
    px = int(a[a.index('--px') + 1]) if '--px' in a else 560
    ss = int(a[a.index('--ss') + 1]) if '--ss' in a else 2
    if '--sjekk' in a:
        sjekk()
    elif '--tal' in a:
        T = {m: [tal(*g[1](m)) for g in GREP] for m in 'sa'}
        skriv_tal(T)
        print(open(os.path.join(_HER, 'tal.md'), encoding='utf-8').read())
    elif '--eitt' in a:
        from multiprocessing import Pool
        namn = a[a.index('--eitt') + 1]
        i = [g[0] for g in GREP].index(namn)
        if '--px' not in a: px = 480
        with Pool(2) as pl:
            res = dict((m, (img, d)) for _, m, img, d in pl.map(_arbeid, [(i, 's', px, ss), (i, 'a', px, ss)]))
        for m in 'sa':
            print({'s': 'stemning', 'a': 'arbeid'}[m], {k: round(float(v), 2) for k, v in res[m][1].items() if not k.startswith('_')})
        print('likskap', round(likskap(res['s'][1]['_fordeling'], res['a'][1]['_fordeling']), 2))
        im = Image.new('RGB', (2 * px + 48, px + 32), (0, 0, 0))
        im.paste(Image.fromarray(res['s'][0]), (16, 16)); im.paste(Image.fromarray(res['a'][0]), (px + 32, 16))
        im.save(os.path.join(_HER, f'par-{namn}.png'))
    else:
        T = lag_brett(px, ss)
        print(open(os.path.join(_HER, 'tal.md'), encoding='utf-8').read())
