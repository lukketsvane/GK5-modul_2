# -*- coding: utf-8 -*-
"""
gen_d/motor.py  ·  form05, generasjon D: familien rundt kroppen Iver valde  (13.11.2026)

Kroppen er «Telt» (uploads/.../50f3c975-image.png): rund raudbrun fot, arm i børsta aluminium, raudbrun bjelke
med knott i leddet, og ei rute som heng frå bjelken. Lyset er D Ruta (konsept/film/02-D-ruta.md, ruta.py, tal-D.json):
ruta har dioder bak ein spreiar og prismefilmen ytst, og ei diode bak bjelken teiknar eit vindauge på veggen.
Knotten flyttar watten frå vindauget til ruta. Ingenting anna rører seg.

Lysmotoren er ruta.py sin eigen (rute.rute, ruta.vindaugsdiode, ls.overgang), importert og ikkje kopiert, så
D-parametrane gjev tal-D.json (sjå `kalib`). Det som er ope, er parametrar:

  fot     'bak' (skive bak skjermen, mot veggen) · 'side' (skive til høgre for skjermen, utanfor feltet)
          · 'under' (stålplate under skjermfoten, skjermen er ballast)
  mote    kvar armen møter bjelken: 'ende' (høgre ende, som biletet) · 'midt' (bak midten) · 'skeiv' (bak, ein
          firedel inn frå midten)
  knott   'ledd' (i leddet arm/bjelke, som biletet) · 'fri' (fri ende av bjelken) · 'fot' (på foten) · 'arm' (på armen, 25 cm)
  rute    (lengd langs bjelken, djupn ut frå bjelken) i meter, v hellinga: 180 er rett ned, 190 er 10° mot brukaren (D)
  rille   'loddrett' (rillene peikar mot brukaren, D) · 'vassrett' (langs bjelken) · 'kryss' (to ark, øvste mot brukaren)
  H, r_fot, over   høgda på bjelken, radius på foten og kor langt bjelken går forbi ruta (høvet fot : bjelke : arm)

Tverrsnitta er faste (identitet, ikkje tjukn): armen er P01-profilen frå byggjesettet (43 × 26 × 1,5 alu, anslått frå
foto), bjelken alu-røyr Ø24 × 1,5, foten stål 8 mm.

  python -B motor.py kalib        motoren mot tal-D.json: ruta.py på nytt, motoren med kroppen til ruta.py, motoren med D-kroppen
  python -B motor.py tal [id,..]  same tal() på alle 18, grovt gitter (ls.tal) -> tal.csv, tal.json
  python -B motor.py fin id,..    fint gitter (arealsnitt, celler 4 cm) for avgjerda
  python -B motor.py brett        brett.png (4 × 4), velt_umogleg.png, nabo-IoU og pikselstatistikk
Éin prosess om gongen, låg prioritet (IDLE), kvar køyring under 6 min.
Filmen er rekna som ideelt 90°-prisme. Det er ei ANTAKING: konsept/vindauge/film/arket.md finst ikkje.
"""
import os, sys, math, json, csv, time
HER = os.path.dirname(os.path.abspath(__file__))
F5 = os.path.dirname(HER); NL = os.path.dirname(F5); ROT = os.path.dirname(NL)
os.environ.setdefault('NUMBA_CACHE_DIR', os.path.join(F5, '.numba'))
sys.dont_write_bytecode = True

def _skaansam():
    """Låg prioritet, som _skaansam i modell/byggjesett/rendre_blender.py."""
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetPriorityClass(k.GetCurrentProcess(), 0x40)          # IDLE_PRIORITY_CLASS
        k.SetProcessAffinityMask(k.GetCurrentProcess(), 0xFC)
    except Exception:
        pass
_skaansam()

FILMDIR = os.path.join(ROT, 'konsept', 'film')
for p in (NL, os.path.join(ROT, 'konsept', 'lysskisse'), FILMDIR):
    if p not in sys.path: sys.path.insert(0, p)
import numpy as np
import ruta                                   # konsept/film/ruta.py (lesast, ikkje skrivast)
import rute as rutemod                        # konsept/film/rute.py
import lysskisse as ls
import felles as fe
from PIL import Image

b, ZB, YV, nrm = ls.b, ls.ZB, ls.YV, ls.nrm
G = 9.81
LOGG = os.path.join(HER, 'logg.md')
TALJSON = os.path.join(HER, 'tal.json')
FILMPROFIL = 'ideelt 90° (ANTAKING)'

def logg(tekst):
    with open(LOGG, 'a', encoding='utf-8') as f:
        f.write('- ' + time.strftime('%H.%M') + ' ' + tekst + '\n')

def _j(o):
    if isinstance(o, np.ndarray): return o.tolist()
    if isinstance(o, (np.floating, np.integer)): return o.item()
    if isinstance(o, np.bool_): return bool(o)
    return str(o)

def lagre(nokkel, verdi):
    d = json.load(open(TALJSON, encoding='utf-8')) if os.path.exists(TALJSON) else {}
    d[nokkel] = verdi
    json.dump(d, open(TALJSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=_j)

# ------------------------------------------------------------------ premissar (R rekna, A anslått, ANTAKING)
Y_BJ, R_BJ = 0.50, 0.012          # bjelken 5 cm bak skjermplanet, Ø24 (som ruta.py)
Q, W_S = 0.2, 1.25                # som ruta.py: vindauget får 1,25 W i stemning og 20 % av 5 W i arbeid
ARK = (0.306, 0.535)              # P08 prismeark (langs rillene, på tvers), A frå foto ±40/±70 mm (modell/byggjesett/LES_MEG.md)
ARK_I_KIT = 1                     # ANTAKING: byggjesettet har eitt ark. Rillene langs kortsida (ANTAKING frå gen/motor.py)
E_AL, G_AL, RHO_AL, RHO_ST = 70e9, 26e9, 2700.0, 7850.0

def _rekt_ror(B, Hh, t):
    """Rektangulært røyr, B djupn i bøyeplanet. Gjev (areal, I med B som djupn, I med Hh som djupn, J tynnvegga)."""
    A = B * Hh - (B - 2 * t) * (Hh - 2 * t)
    IB = (Hh * B ** 3 - (Hh - 2 * t) * (B - 2 * t) ** 3) / 12
    IH = (B * Hh ** 3 - (B - 2 * t) * (Hh - 2 * t) ** 3) / 12
    J = 4 * ((B - t) * (Hh - t)) ** 2 * t / (2 * ((B - t) + (Hh - t)))
    return A, IB, IH, J

_A, _IB, _IH, _J = _rekt_ror(0.043, 0.026, 0.0015)
ARM = dict(EIa=E_AL * _IB, EIb=E_AL * _IH, GJ=G_AL * _J, kgm=RHO_AL * _A, namn='P01 43 × 26 × 1,5')
P01_L = 0.240                                        # A: profillengda i byggjesettet
_Ib = math.pi / 64 * (0.024 ** 4 - 0.021 ** 4)
BJELKE = dict(EIa=E_AL * _Ib, EIb=E_AL * _Ib, GJ=G_AL * 2 * _Ib, kgm=RHO_AL * math.pi / 4 * (0.024 ** 2 - 0.021 ** 2), namn='Ø24 × 1,5')
T_FOT = 0.008                                        # stålskive 8 mm (fast, ikkje tjukn som fridomsgrad)
PLATE = dict(x=0.15, y0=0.45, y1=0.68, t=0.002)      # stålplate under skjermfoten, 30 × 23 cm × 2 mm, bak feltet (y0 0,38 skugga feltet, sjå logg.md)
M_SKJERM, C_SKJERM = 3.5, np.array([0.0, 0.47, 0.20])   # ANTAKING (som gen/motor.py): skjermen er ballast på plata
SKJ = dict(x=0.27, y0=0.45, y1=0.50, z0=0.10, z1=0.42)  # skjermen som boks (djupn 5 cm ANTAKING), h over bordet
SKJ_FOT = dict(x=0.12, y0=0.40, y1=0.60, z1=0.025)      # ANTAKING: skjermfoten 24 × 20 cm
KNOTT = dict(r=0.0385, l=0.028, m=0.08)              # P07 fatning Ø77 × 28 frå byggjesettet (A), masse A
F_DYTT = 5.0                                         # ANTAKING: fingerdytt på knotten, N
SKULDER = np.array([0.20, -0.22, 0.32]); REKK = 0.70 # ANTAKING: høgre skulder og lengste grep utan å reise seg, m
FELT = (-0.30, 0.30, 0.05, 0.45)
TIP_MIN, DELTA_MAX = fe.TIP_MIN, fe.DELTA_MAX         # 6° og 2 mm, som felles.py

def masse_rute(w, d, rille):
    """(A) kvit bakplate PS 1 mm, spreiar PMMA 2 mm, film 0,2 mm (to ark ved kryss), veggar 2 cm PS 1 mm, LED-rader."""
    A = w * d; nf = 2 if rille == 'kryss' else 1
    return A * (0.001 * 1050 + 0.002 * 1190 + nf * 0.0002 * 1380) + 2 * (w + d) * 0.020 * 0.001 * 1050 + led_rader(d) * w * 0.03

def led_rader(d): return max(2, math.ceil(d / 0.04))   # A: rader kvar 4 cm bak ein spreiar 2 cm framfor (2 × djupna)

# ------------------------------------------------------------------ geometri
def boks8(p0, p1, a, c, wa, wc):
    """Prisme langs p0 -> p1 med tverrsnitt wa × wc i retningane a og c. Gjev (V, F)."""
    V = []
    for p in (p0, p1):
        for sa, sc in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            V.append(p + a * sa * wa / 2 + c * sc * wc / 2)
    F = [(0, 1, 2), (0, 2, 3), (4, 6, 5), (4, 7, 6)]
    for i in range(4):
        j = (i + 1) % 4; F += [(i, j, 4 + j), (i, 4 + j, 4 + i)]
    return np.array(V), F

def akser(t):
    """Lokale aksar for eit stykke langs t: a ligg vassrett (sidevegs), c = t × a. Djupna 43 mm ligg langs c."""
    t = nrm(t)
    a = np.array([1.0, 0, 0]) if abs(t[2]) > 0.99 else nrm(np.cross(t, [0, 0, 1.0]))
    return a, nrm(np.cross(t, a))

class Kropp:
    def __init__(s, sp):
        s.sp = sp; s.w, s.d = sp['rute']; s.H = sp['H']; s.rille = sp['rille']
        vr = math.radians(sp['v'])
        s.ut = np.array([0.0, math.sin(vr), math.cos(vr)]); s.e = np.array([0.0, math.cos(vr), -math.sin(vr)])
        s.la = np.array([1.0, 0, 0])
        s.BJ = np.array([0.0, Y_BJ, s.H])                         # bordkoordinatar (h over bordet)
        s.xe = s.w / 2 + sp['over']
        mo = sp['mote']
        if mo == 'ende':
            s.M = np.array([s.xe + 0.013, Y_BJ, s.H]); s.xm = s.xe
        else:
            s.xm = 0.0 if mo == 'midt' else s.w / 4
            s.M = np.array([s.xm, Y_BJ + R_BJ + 0.013, s.H])
        # foten
        fo = sp['fot']; s.r = sp.get('r_fot', 0.11); s.tf = sp.get('t_fot', T_FOT)
        if 'fot_xy' in sp:
            s.xf, s.yf = sp['fot_xy']
        elif fo == 'bak':
            s.xf = max(s.M[0], SKJ_FOT['x'] + s.r + 0.005); s.yf = 0.69 - s.r
        elif fo == 'side':
            s.xf = 0.31 + s.r; s.yf = 0.47
        else:
            s.xf, s.yf = float(np.clip(s.M[0], -0.13, 0.13)), PLATE['y1'] - 0.02
        s.S0 = np.array([s.xf, s.yf, PLATE['t'] if fo == 'under' else s.tf])
        # armen: stigar og eitt skrått stykke til leddet
        hd = np.linalg.norm(s.M[:2] - s.S0[:2])
        kh = s.H - 0.14 if mo == 'ende' else s.H - 0.03
        s.arm = [s.S0, np.array([s.xf, s.yf, kh]), s.M] if hd > 0.03 else [s.S0, s.M]
        s.L_arm = sum(np.linalg.norm(q - p) for p, q in zip(s.arm[:-1], s.arm[1:]))
        # knotten
        kn = sp['knott']; l = KNOTT['l']
        if kn == 'ledd':
            s.K, s.Kax = ((np.array([s.xe + 0.026 + l / 2, Y_BJ, s.H]), s.la) if mo == 'ende'
                          else (np.array([s.xm, Y_BJ + R_BJ + 0.026 + l / 2, s.H]), np.array([0.0, 1.0, 0])))
        elif kn == 'fri':
            x = -s.xe - l / 2 if mo in ('ende', 'skeiv') else s.xe + l / 2
            s.K, s.Kax = np.array([x, Y_BJ, s.H]), s.la
        elif kn == 'fot':
            s.K, s.Kax = ((np.array([s.xf, s.yf - 0.6 * s.r, s.tf + l / 2]), np.array([0, 0, 1.0])) if fo != 'under'
                          else (np.array([0.11, PLATE['y0'] + 0.04, PLATE['t'] + l / 2]), np.array([0, 0, 1.0])))
        else:
            s.K, s.Kax = np.array([s.xf, s.yf - 0.013 - l / 2, 0.25]), np.array([0.0, -1.0, 0])

    # --- ruta
    def rute_c(s): return s.BJ + s.e * s.d / 2
    def rute_pkt(s, nu=24, nv=10):
        o = s.BJ - s.la * s.w / 2
        return np.array([o + s.la * s.w * (i + 0.5) / nu + s.e * s.d * (j + 0.5) / nv for i in range(nu) for j in range(nv)])

    # --- delar: (namn, mesh (V, F) bordkoordinatar, masse, tyngdepunkt, ls-prim)
    def delar(s):
        D = []; W = lambda p: np.asarray(p, float) + np.array([0, 0, ZB])
        c = s.rute_c(); o = c - s.la * s.w / 2 - s.e * s.d / 2
        V, F = boks8(o + s.la * s.w / 2 - s.ut * 0.0075, o + s.la * s.w / 2 + s.e * s.d - s.ut * 0.0075, s.la, s.ut, s.w, 0.015)
        pr = ls.Rekt(W(c - s.ut * 0.012 - s.la * s.w / 2 - s.e * s.d / 2), s.la * s.w, s.e * s.d)    # huset bak ruta, som ruta.py
        D.append(('rute', (V, F), masse_rute(s.w, s.d, s.rille), c - s.ut * 0.0075, pr))
        p0, p1 = np.array([-s.xe, Y_BJ, s.H]), np.array([s.xe, Y_BJ, s.H])
        D.append(('bjelke', fe.frustum(p0, p1, R_BJ, R_BJ, 24), BJELKE['kgm'] * 2 * s.xe + 0.02, (p0 + p1) / 2, ls.syl(W(p0), W(p1), R_BJ)))
        for i, (p, q) in enumerate(zip(s.arm[:-1], s.arm[1:])):
            a, cc = akser(q - p)
            D.append(('arm%d' % i, boks8(p, q, a, cc, 0.026, 0.043), ARM['kgm'] * np.linalg.norm(q - p), (p + q) / 2, ls.syl(W(p), W(q), 0.017)))
        k0, k1 = s.K - s.Kax * KNOTT['l'] / 2, s.K + s.Kax * KNOTT['l'] / 2
        D.append(('knott', fe.frustum(k0, k1, KNOTT['r'], KNOTT['r'], 32), KNOTT['m'], s.K, ls.syl(W(k0), W(k1), KNOTT['r'])))
        if s.sp['mote'] != 'ende' or s.sp['knott'] != 'ledd':      # endelokk på bjelken
            for x in (-s.xe, s.xe):
                D.append(('lokk', fe.frustum(np.array([x, Y_BJ, s.H]), np.array([x + np.sign(x) * 0.006, Y_BJ, s.H]), 0.016, 0.016, 24), 0.01, np.array([x, Y_BJ, s.H]), None))
        if s.sp['fot'] == 'under':
            o = np.array([-PLATE['x'], PLATE['y0'], 0.0])
            V, F = boks8(o + np.array([PLATE['x'], 0, PLATE['t'] / 2]), o + np.array([PLATE['x'], PLATE['y1'] - PLATE['y0'], PLATE['t'] / 2]),
                         s.la, np.array([0, 0, 1.0]), 2 * PLATE['x'], PLATE['t'])
            m = RHO_ST * 2 * PLATE['x'] * (PLATE['y1'] - PLATE['y0']) * PLATE['t']
            D.append(('plate', (V, F), m, np.array([0, (PLATE['y0'] + PLATE['y1']) / 2, PLATE['t'] / 2]),
                      ls.Rekt(W([-PLATE['x'], PLATE['y0'], PLATE['t']]), (2 * PLATE['x'], 0, 0), (0, PLATE['y1'] - PLATE['y0'], 0))))
        else:
            m = RHO_ST * math.pi * s.r ** 2 * s.tf
            D.append(('fot', fe.frustum(np.array([s.xf, s.yf, 0.0]), np.array([s.xf, s.yf, s.tf]), s.r, s.r, 64), m,
                      np.array([s.xf, s.yf, s.tf / 2]), ls.skive(W([s.xf, s.yf, 0.004]), (0, 0, 1), s.r)))
        return D

    def delar_c(s):
        if not hasattr(s, '_D'): s._D = s.delar()
        return s._D
    def prims(s): return [d[4] for d in s.delar_c() if d[4] is not None]
    def mesh(s): return fe.merge([d[1] for d in s.delar()])
    def kontakt(s):
        if s.sp['fot'] == 'under':
            return np.array([[-PLATE['x'], PLATE['y0']], [PLATE['x'], PLATE['y0']], [PLATE['x'], PLATE['y1']], [-PLATE['x'], PLATE['y1']]])
        th = np.arange(48) / 48 * 2 * math.pi
        return np.c_[s.xf + s.r * np.cos(th), s.yf + s.r * np.sin(th)]
    def masser(s, r=None):
        """(masse, tyngdepunkt) for alle delar, med skjermen som ballast når foten er plata. r: annan fotradius."""
        P = [(d[2], np.asarray(d[3], float)) for d in s.delar_c() if d[0] != 'fot']
        if s.sp['fot'] == 'under':
            P.append((M_SKJERM, C_SKJERM))
        else:
            rr = s.r if r is None else r
            P.append((RHO_ST * math.pi * rr ** 2 * s.tf, np.array([s.xf, s.yf, s.tf / 2])))
        return P

# ------------------------------------------------------------------ lyset: ruta.py sin motor
_KAST = {}
def kast_lys(H, t, Wv, K, N):
    """Vindaugsdioden bak bjelken (ruta.vindaugsdiode), mellomlagra per høgd og steg. Ho er lik for alle med same H."""
    k = (round(H, 4), round(float(t), 4), N)
    if k not in _KAST:
        gamal = ruta.BJELKE
        ruta.BJELKE = b(0.0, Y_BJ, H)
        try:
            _KAST[k] = ruta.vindaugsdiode(Wv, K, None, (1, 0, 0), N, 0.5)
        finally:
            ruta.BJELKE = gamal
    return _KAST[k].lys()

_FORD = {}
def ford(rille):
    if rille not in _FORD:
        _FORD[rille] = ruta.ford('ut') if rille != 'kryss' else rutemod.utfordeling(innside='flat', lag2='kryss')
    return _FORD[rille]

def rute_lys(kr, lm, K):
    c = kr.rute_c() + np.array([0, 0, ZB])
    if kr.rille == 'loddrett':
        return rutemod.rute(c, kr.ut, kr.e, (kr.w, kr.d), lm, K, ford('loddrett'))
    # vassrett: rillene langs bjelken. kryss: nedste ark langs bjelken, øvste (lag2) mot brukaren
    return rutemod.rute(c, kr.ut, kr.la, (kr.d, kr.w), lm, K, ford(kr.rille))

def g_lys(kr, N=2_000_000, prims=None):
    pr = kr.prims() if prims is None else prims
    def g(t):
        W, K = ls.watt(t)
        Wv = min(W_S * (Q * 5.0 / W_S) ** float(t), W); Wp = W - Wv
        lys = kast_lys(kr.H, t, Wv, K, N)
        if Wp > 0.02:
            lys.append(rute_lys(kr, Wp * ls.LMW_KJELDE, K))
        return lys, pr
    return g

def rekn_lys(g, n=5):
    """Same nøklar og same rekning som ruta.rekn (og tre.rekn)."""
    R, m = ls.overgang(g, n=n)
    s, a = R[0], R[-1]
    f = 350.0 / max(a['E_felt'], 1e-9)
    La = lambda d: max(d['L_lampe'], d['L_flate'])
    return dict(W350=a['W'] * f, jamnheit=a['U'], vegg350=a['E_vegg'] * f, bak350=a['E_bak'] * f, ansikt350=a['E_ansikt'] * f,
                skjerm350=a['E_skjerm'] * f, auge25=max(a['L_auge25'], a['L_flate']) * f, auge47=La(a) * f,
                auge60=max(a['L_auge60'], a['L_flate']) * f, s_W=s['W'], s_felt=s['E_felt'], s_bak=s['E_bak'], s_skjerm=s['E_skjerm'],
                s_auge25=max(s['L_auge25'], s['L_flate']), s_auge47=La(s), s_auge60=max(s['L_auge60'], s['L_flate']),
                likskap=ls.likskap(s['_fordeling'], a['_fordeling']), topp=m['topp'], sprang=m['sprang'], f=f)

AUGEVOLUM = [b(x, y, z) for x in (-0.15, 0.0, 0.15) for y in (-0.15, -0.075, 0.0) for z in (0.25, 0.37, 0.42, 0.47, 0.52, 0.60)]

def augevolum(l, P):
    """Høgaste luminans frå ruta mot auget i volumet ±15 cm sidevegs, 15 cm fram, 25 til 60 cm over bordet (som rute/motor.py)."""
    best = 0.0
    for E in AUGEVOLUM:
        d = E - P; d /= np.linalg.norm(d, axis=1)[:, None]
        best = max(best, float(np.max(l.L(d))))
    return best

def spegling(l, P, tiltar=(0, 5, 10, 15, 20)):
    """Luminansen av ruta slik auget ser henne spegla i skjermen, tilta 0 til 20° om underkanten (som rute/motor.py).
    Gjev luminansen før refleksjon; gang med 0,04 for blank skjerm."""
    ut = {}
    auge = [b(x, y, z) for x in (-0.15, 0.0, 0.15) for y in (-0.15, 0.0) for z in (0.37, 0.47, 0.57)]
    for tau in tiltar:
        t = math.radians(tau)
        P0 = b(-0.27, 0.45, 0.11); ex = np.array([1.0, 0, 0]); td = np.array([0.0, math.sin(t), math.cos(t)])
        n = np.array([0.0, -math.cos(t), math.sin(t)])
        best = 0.0
        for E in auge:
            if (E - P0) @ n <= 0: continue
            Em = E - 2 * ((E - P0) @ n) * n
            Sv = P[(P - P0) @ n > 0]
            if not len(Sv): continue
            dv = Em - Sv; tt = ((P0 - Sv) @ n) / (dv @ n); X = Sv + tt[:, None] * dv
            a = (X - P0) @ ex; bb = (X - P0) @ td
            ok = (tt > 0) & (tt < 1) & (a >= 0) & (a <= 0.54) & (bb >= 0) & (bb <= 0.31)
            if not ok.any(): continue
            d = X[ok] - Sv[ok]; d /= np.linalg.norm(d, axis=1)[:, None]
            best = max(best, float(np.max(l.L(d))))
        ut[tau] = best
    return ut

# --- fint gitter: arealsnitt med celler 4 cm (direkte i cellene, indirekte frå ls.tal)
def _rutenett(x0, x1, nx, a0, a1, na, plan, k):
    dx, da = (x1 - x0) / nx, (a1 - a0) / na; P = []
    for i in range(nx):
        for j in range(na):
            for si in (-0.25, 0.25):
                for sj in (-0.25, 0.25):
                    x = x0 + (i + 0.5 + si) * dx; a = a0 + (j + 0.5 + sj) * da
                    P.append([x, a, ZB + 1e-4] if plan == 'bord' else [x, k, ZB + a])
    P = np.array(P); N = np.tile([0.0, 0, 1] if plan == 'bord' else [0.0, -1, 0], (len(P), 1))
    return P, N, (nx, na)

FELT4 = _rutenett(-0.30, 0.30, 15, 0.05, 0.45, 10, 'bord', 0)
BAK4 = _rutenett(-0.35, 0.35, 18, 0.05, 0.65, 15, 'vegg', YV - 1e-4)
SKJ4 = _rutenett(-0.27, 0.27, 14, 0.11, 0.42, 8, 'skjerm', 0.447)

def _ls_punkt():
    R = ls.rom(); kb, kv = R.kart[0], R.kart[1]
    Pb = R.P[kb.sl].reshape(28, 14, 3)[8:20, 1:9].reshape(-1, 3); Nb = np.tile([0.0, 0, 1], (len(Pb), 1))
    Pv = R.P[kv.sl]; mb = (np.abs(Pv[:, 0]) < 0.35) & (Pv[:, 2] > ZB + 0.05) & (Pv[:, 2] < ZB + 0.65)
    Pw = Pv[mb]; Nw = np.tile([0.0, -1, 0], (len(Pw), 1))
    xs = np.linspace(-0.24, 0.24, 5); zs = ZB + np.linspace(0.14, 0.39, 3)
    Ps = np.array([[x, 0.447, z] for x in xs for z in zs]); Ns = np.tile([0.0, -1, 0], (len(Ps), 1))
    return (Pb, Nb), (Pw, Nw), (Ps, Ns)

def tal_fin(lys, prims):
    T = ls.tal(lys, prims)
    okkl = ls.STATISK + list(prims) + [l.prim for l in lys]; okkl_s = [p for p in okkl if p is not ls.SKJERM]
    (Pb, Nb), (Pw, Nw), (Ps, Ns) = _ls_punkt()
    Ed = lambda P, N, o: ls.E_direkte(P, N, lys, o) @ ls.LUM
    ei_f = T['E_felt'] - Ed(Pb, Nb, okkl).mean(); ei_b = T['E_bak'] - Ed(Pw, Nw, okkl).mean(); ei_s = T['E_skjerm'] - Ed(Ps, Ns, okkl_s).mean()
    P, N, (nx, na) = FELT4; c = Ed(P, N, okkl).reshape(nx, na, 4).mean(-1) + ei_f
    P2, N2, _ = BAK4; P3, N3, _ = SKJ4
    return dict(E_felt=float(c.mean()), U=float(c.min() / max(c.mean(), 1e-9)), E_bak=float(Ed(P2, N2, okkl).mean() + ei_b),
                E_skjerm=float(Ed(P3, N3, okkl_s).mean() + ei_s), W=T['W'])

# ------------------------------------------------------------------ mekanikk
def forskyving(kjede, P, F, T):
    """Forskyving i T (m) frå kraft F i P, der P og T heng stivt i enden av kjeda. Euler-Bernoulli og St-Venant-torsjon,
    stive ledd (ANTAKING). kjede: [(p0, p1, tverrsnitt)] frå foten og ut."""
    u = np.zeros(3)
    for p0, p1, sek in kjede:
        L = np.linalg.norm(p1 - p0)
        if L < 1e-6: continue
        t = (p1 - p0) / L; a, c = akser(t); n = 24; ds = L / n
        for i in range(n):
            x = p0 + t * (i + 0.5) * ds
            M = np.cross(P - x, F)
            th = (a * (M @ a) / sek['EIa'] + c * (M @ c) / sek['EIb'] + t * (M @ t) / sek['GJ']) * ds
            u += np.cross(th, T - x)
    return u

def kjede_til(kr, P):
    """Lastvegen frå foten til punktet P: armen, så bjelken frå leddet til x-en til P."""
    ch = [(p, q, ARM) for p, q in zip(kr.arm[:-1], kr.arm[1:])]
    x = float(np.clip(P[0], -kr.xe, kr.xe))
    if abs(x - kr.xm) > 1e-4:
        ch.append((np.array([kr.xm, Y_BJ, kr.H]), np.array([x, Y_BJ, kr.H]), BJELKE))
    return ch

def kontroll_utkraga():
    """Verifikasjon: loddrett P01-stong 0,5 m, 5 N vassrett i toppen, mot F L³ / (3 E I)."""
    p0, p1 = np.zeros(3), np.array([0, 0, 0.5])
    u = forskyving([(p0, p1, ARM)], p1, np.array([0, 5.0, 0]), p1)
    return dict(motor_mm=float(abs(u[1]) * 1000), analytisk_mm=5 * 0.5 ** 3 / (3 * ARM['EIa']) * 1000)

def F_tipp(parts, hull, P, retn):
    """Minste kraft (N) i retninga retn i punktet P som veltar kroppen om ein kant av hylsteret."""
    m = sum(x for x, _ in parts); C = sum(x * c for x, c in parts) / m
    best = float('inf')
    for i in range(len(hull)):
        a = np.r_[hull[i], 0.0]; q = np.r_[hull[(i + 1) % len(hull)], 0.0]
        u = nrm(q - a); n = np.array([u[1], -u[0], 0.0])                  # utover når hylsteret går mot klokka
        if (np.r_[hull.mean(0), 0] - a) @ n > 0: n = -n
        ax = np.cross([0, 0, 1.0], n)
        Mg = np.cross(C - a, [0, 0, -m * G]) @ ax
        Mf = np.cross(P - a, retn) @ ax
        if Mf > 1e-9: best = min(best, -Mg / Mf)
    return max(best, 0.0) if best < float('inf') else float('inf')

def hylster(kr):
    from scipy.spatial import ConvexHull
    pts = kr.kontakt(); return pts[ConvexHull(pts).vertices]

RETN = [np.array([math.cos(a), math.sin(a), 0.0]) for a in np.arange(16) / 16 * 2 * math.pi] + [np.array([0, 0, -1.0])]

def stab(kr, r=None):
    parts = kr.masser(r)
    if r is not None and kr.sp['fot'] != 'under':
        th = np.arange(48) / 48 * 2 * math.pi; hull = np.c_[kr.xf + r * np.cos(th), kr.yf + r * np.sin(th)]
    else:
        hull = hylster(kr)
    st = fe.stabilitet(parts, [hull], kr.K[2], F_DYTT)
    Fk = min(F_tipp(parts, hull, kr.K, d) for d in RETN)
    return st, Fk, parts, hull

def r_krav(kr, dytt=True):
    """Minste fotradius (same plassering, same tjukn) som gjev tipp ≥ 6°, og med dytt=True òg tol fingerdytten (5 N) på knotten."""
    if kr.sp['fot'] == 'under': return float('nan')
    def ok(r):
        st, Fk, _, _ = stab(kr, r)
        return st['tipp_deg'] >= TIP_MIN and (Fk >= F_DYTT or not dytt)
    lo, hi = 0.02, 0.40
    if not ok(hi): return float('inf')
    for _ in range(26):
        mid = (lo + hi) / 2
        if ok(mid): hi = mid
        else: lo = mid
    return hi

def r_maks(kr):
    fo = kr.sp['fot']
    if fo == 'bak': return 0.12              # mellom skjermplanet (0,45) og veggen (0,70) med 1 cm luft
    if fo == 'side': return (0.70 - 0.31) / 2
    return float('nan')

# ------------------------------------------------------------------ grense, sikt, produksjon
def i_sikt(P):
    """Del av punkta (bordkoordinatar) inne i synspyramiden frå auget (47 cm, 60 cm frå skjermen) til skjermflata."""
    E = ls.AUGE - np.array([0, 0, ZB]); s = (P[:, 1] - E[1]) / (SKJ['y0'] - E[1])
    with np.errstate(divide='ignore', invalid='ignore'):
        X = E + (P - E) / s[:, None]
    return float(((s > 0.05) & (s < 1) & (np.abs(X[:, 0]) < SKJ['x']) & (X[:, 2] > SKJ['z0']) & (X[:, 2] < SKJ['z1'])).mean())

def kollisjon(kr):
    """Djupaste punkt (mm) inne i skjermen, skjermfoten, veggen eller bordet. Armen er prøvd langs midtlina med 2 cm margin."""
    V, _ = kr.mesh()
    Q = [V]
    for p, q in zip(kr.arm[:-1], kr.arm[1:]):
        Q.append(p + (q - p) * np.linspace(0, 1, 60)[:, None])
    Q = np.vstack(Q)
    Pb = np.array([-kr.xe, Y_BJ, kr.H]) + np.linspace(0, 1, 80)[:, None] * np.array([2 * kr.xe, 0, 0])   # bjelkeaksen
    Pr = kr.rute_pkt(40, 16)                                                                          # rutefronten
    def inni(P, bx, m=0.0):
        x0, x1, y0, y1, z0, z1 = bx; x0 -= m; y0 -= m; z0 -= m; x1 += m; y1 += m; z1 += m
        m = (P[:, 0] > x0) & (P[:, 0] < x1) & (P[:, 1] > y0) & (P[:, 1] < y1) & (P[:, 2] > z0) & (P[:, 2] < z1)
        if not m.any(): return 0.0
        R = P[m]
        return float(np.min(np.stack([R[:, 0] - x0, x1 - R[:, 0], R[:, 1] - y0, y1 - R[:, 1], R[:, 2] - z0, z1 - R[:, 2]]), 0).max())
    sk = (-SKJ['x'], SKJ['x'], SKJ['y0'], SKJ['y1'], SKJ['z0'], SKJ['z1'])
    d = max(inni(Q, sk), inni(Pb, sk, R_BJ), inni(Pr, sk))
    if kr.sp['fot'] != 'under':
        d = max(d, inni(Q, (-SKJ_FOT['x'], SKJ_FOT['x'], SKJ_FOT['y0'], SKJ_FOT['y1'], -0.01, SKJ_FOT['z1'])))
    d = max(d, float(np.max(Q[:, 1] - YV, initial=0.0)), float(np.max(-Q[:, 2], initial=0.0) if Q[:, 2].min() < -1e-4 else 0.0))
    return d * 1000

def fot_pa_felt(kr):
    if kr.sp['fot'] == 'under': return 0.0
    g = np.mgrid[-1:1:60j, -1:1:60j].reshape(2, -1).T; g = g[(g ** 2).sum(1) <= 1] * kr.r + [kr.xf, kr.yf]
    return float(((g[:, 0] > FELT[0]) & (g[:, 0] < FELT[1]) & (g[:, 1] > FELT[2]) & (g[:, 1] < FELT[3])).mean())

def filmbitar(w, d, rille):
    """Bitane frå P08 (langs rillene ≤ 30,6, på tvers ≤ 53,5 cm). Gjev (ark, skøytar). Hyllepakking, éin rad per hylle."""
    bit = [(d, w)] if rille == 'loddrett' else ([(w, d)] if rille == 'vassrett' else [(d, w), (w, d)])
    skoyt = 0; pieces = []
    for L, T in bit:
        nl, nt = math.ceil(L / ARK[0] - 1e-9), math.ceil(T / ARK[1] - 1e-9)
        skoyt += nl * nt - 1
        pieces += [(L / nl, T / nt)] * (nl * nt)
    ark = []                                       # kvart ark: liste av hyller [høgd langs rillene, brukt på tvers]
    for L, T in sorted(pieces, key=lambda p: -p[0]):
        lagt = False
        for hyller in ark:
            for h in hyller:
                if L <= h[0] + 1e-9 and h[1] + T <= ARK[1] + 1e-9: h[1] += T; lagt = True; break
            if not lagt and sum(h[0] for h in hyller) + L <= ARK[0] + 1e-9: hyller.append([L, T]); lagt = True
            if lagt: break
        if not lagt: ark.append([[L, T]])
    return len(ark), skoyt

def produksjon(kr):
    """Kva som finst i byggjesettet, kva som må lagast, og kva som må kjøpast utover LED-stripa."""
    w, d, ri = kr.w, kr.d, kr.rille
    n_ark, skoyt = filmbitar(w, d, ri)
    kit, lag, skaff = [], [], []
    kit.append('P08 film' if n_ark <= ARK_I_KIT else 'P08 film (1 av %d ark)' % n_ark)
    if n_ark > ARK_I_KIT: skaff.append('%d prismeark til' % (n_ark - ARK_I_KIT))
    kit.append('P07 fatning som knott')
    if kr.L_arm <= P01_L: kit.append('P01 arm')
    else:
        kit.append('P01 (240 mm)'); skaff.append('alu-profil 43×26 %.0f mm' % ((kr.L_arm - P01_L) * 1000))
    knekk = len(kr.arm) - 2
    lag.append('arm %d stk%s' % (len(kr.arm) - 1, ', %d gjæring' % knekk if knekk else ''))
    lag.append('bjelke Ø24 %.0f mm' % (2 * kr.xe * 1000)); skaff.append('alu-røyr Ø24 %.0f mm' % (2 * kr.xe * 1000))
    if kr.sp['fot'] == 'under':
        lag.append('stålplate 300×230×2'); skaff.append('stålplate %.1f kg' % (RHO_ST * 0.30 * 0.23 * 0.002))
    else:
        mf = RHO_ST * math.pi * kr.r ** 2 * kr.tf
        lag.append('fot Ø%.0f×%.0f' % (2 * kr.r * 1000, kr.tf * 1000)); skaff.append('stål %.1f kg' % mf)
    lag.append('hus %.0f×%.0f×20 + spreiar' % (w * 1000, d * 1000)); skaff.append('kvit plast + spreiar %.2f m²' % (w * d * 2 + 2 * (w + d) * 0.02))
    led_m = led_rader(d) * w + 0.05
    return dict(n_ark=n_ark, skoyt=skoyt, arm_mm=kr.L_arm * 1000, arm_utover_P01_mm=max(0.0, kr.L_arm - P01_L) * 1000, knekk=knekk,
                bjelke_mm=2 * kr.xe * 1000, led_m=led_m, kit='; '.join(kit), lag='; '.join(lag), skaff='; '.join(skaff))

# ------------------------------------------------------------------ same tal() på alle
def tal(sp, n=5, N=2_000_000):
    t0 = time.time()
    kr = Kropp(sp)
    # --- lyset (grovt gitter: ls.tal, same som tal-D.json)
    g = g_lys(kr, N)
    L = rekn_lys(g, n=n); f = L['f']
    lys1, _ = g(1.0); rl = [l for l in lys1 if l.namn == 'rute'][0]
    P = kr.rute_pkt() + np.array([0, 0, ZB])
    av = augevolum(rl, P) * f; sp_ = spegling(rl, P); sp_maks = max(sp_.values()) * f * 0.04
    # --- form og mekanikk
    st, Fk, parts, hull = stab(kr)
    m = sum(x for x, _ in parts) - (M_SKJERM if sp['fot'] == 'under' else 0.0)
    rk = r_krav(kr); rk0 = r_krav(kr, dytt=False); rm = r_maks(kr)
    led = np.array([0.0, Y_BJ + 0.016, kr.H])
    d_led = min(np.linalg.norm(np.cross(led - p, nrm(q - p))) if 0 <= (led - p) @ nrm(q - p) <= np.linalg.norm(q - p) else min(np.linalg.norm(led - p), np.linalg.norm(led - q)) for p, q in zip(kr.arm[:-1], kr.arm[1:]))
    fr = kr.BJ + kr.e * kr.d                                         # framkanten, midt
    hj = [fr - kr.la * kr.w / 2, fr + kr.la * kr.w / 2]
    F_rute = min(F_tipp(parts, hull, q, np.array([0, 0, -1.0])) for q in hj)
    if sp['knott'] == 'fot': sv_k = 0.0
    elif sp['knott'] == 'arm':
        kh = np.array([kr.xf, kr.yf, 0.25])
        sv_k = max(np.linalg.norm(forskyving([(kr.S0, kh, ARM)], kr.K, F_DYTT * d, kr.K)) for d in RETN)
    else:
        ch = kjede_til(kr, kr.K)
        sv_k = max(np.linalg.norm(forskyving(ch, kr.K, F_DYTT * d, kr.K)) for d in RETN)
    sv_r = max(np.linalg.norm(forskyving(kjede_til(kr, q), q, np.array([0, 0, -F_DYTT]), q)) for q in hj)
    heng = [(d[2], np.asarray(d[3], float)) for d in kr.delar_c() if d[0] in ('rute', 'bjelke', 'knott', 'lokk') and d[3][2] > 0.1]
    mh = sum(x for x, _ in heng); ch_ = sum(x * c for x, c in heng) / mh
    heng_mm = abs(forskyving(kjede_til(kr, ch_), ch_, np.array([0, 0, -mh * G]), fr)[2]) * 1000
    rekk = float(np.linalg.norm(kr.K - SKULDER))
    bak_skj = bool(kr.K[1] > SKJ['y0'] and abs(kr.K[0]) < SKJ['x'] + 0.02 and kr.K[2] < SKJ['z1'] + 0.02)
    Pr = kr.rute_pkt(12, 6)
    isk = i_sikt(Pr); kol = kollisjon(kr); fpf = fot_pa_felt(kr)
    pd = produksjon(kr)
    V, _ = kr.mesh()
    rad = dict(id=sp['id'], rad=sp['rad'], kol=sp['kol'], namn=sp['namn'], fot=sp['fot'], mote=sp['mote'], knott=sp['knott'],
               rute_cm='%gx%g' % (kr.w * 100, kr.d * 100), v=sp['v'], rille=sp['rille'], H_cm=kr.H * 100,
               r_fot_cm=(kr.r * 100 if sp['fot'] != 'under' else float('nan')), over_cm=sp['over'] * 100, film=FILMPROFIL,
               # lys i arbeid ved 350 lx på feltet
               W350=L['W350'], U0=L['jamnheit'], auge25=L['auge25'], auge47=L['auge47'], auge60=L['auge60'], augevolum=av,
               spegling_blank=sp_maks, bak350=L['bak350'], skjerm350=L['skjerm350'], skjerm_del=L['skjerm350'] / 350.0,
               ansikt350=L['ansikt350'], ansikt_7_5W=L['ansikt350'] * 7.5 / L['W350'],
               # stemning og overgangen
               s_auge=max(L['s_auge25'], L['s_auge47'], L['s_auge60']), s_bak=L['s_bak'], s_skjerm=L['s_skjerm'],
               likskap=L['likskap'], sprang=L['sprang'], topp=L['topp'],
               # kropp
               masse_kg=m, hogd_cm=V[:, 2].max() * 100, breidd_cm=(V[:, 0].max() - V[:, 0].min()) * 100,
               tipp_deg=st['tipp_deg'], F_tipp_knott_N=Fk, F_tipp_rute_N=F_rute, r_krav_stat_cm=rk0 * 100, r_krav_cm=rk * 100, r_maks_cm=rm * 100,
               svikt_knott_mm=sv_k * 1000, svikt_rute_mm=sv_r * 1000, heng_mm=heng_mm,
               rekk_cm=rekk * 100, knott_bak_skjerm=bak_skj, arm_til_vindaugsdiode_mm=d_led * 1000, i_sikt=isk, kollisjon_mm=kol, fot_pa_felt=fpf)
    rad.update(pd)
    fl = []
    if rad['W350'] > 7.5: fl.append('over 7,5 W')
    if rad['U0'] < 0.4: fl.append('ujamt')
    am = max(rad['auge25'], rad['auge47'], rad['auge60'])
    if am > 3000: fl.append('F1')
    elif am > 1500: fl.append('F5')
    if rad['augevolum'] > 1500: fl.append('augevolum over F5')
    if rad['spegling_blank'] > 0.5 * ls.SKJERM_CD: fl.append('speglar seg')
    if rad['bak350'] < 100: fl.append('F6')
    if rad['ansikt350'] < 50: fl.append('F10')
    if rad['s_auge'] > 500: fl.append('stemning blendar')
    if rad['skjerm_del'] > 0.5: fl.append('lys på skjermen')
    if rad['likskap'] > 0.9: fl.append('dimmar')
    if rad['tipp_deg'] < TIP_MIN: fl.append('veltar')
    elif rad['F_tipp_knott_N'] < F_DYTT: fl.append('dytt veltar')
    if rad['F_tipp_rute_N'] < F_DYTT: fl.append('trykk på ruta veltar')
    if rad['svikt_knott_mm'] > DELTA_MAX: fl.append('knotten vaggar')
    if rad['svikt_rute_mm'] > 5: fl.append('ruta vaggar')
    if isk > 0.005: fl.append('i siktlina')
    if kol > 1: fl.append('kolliderer')
    if fpf > 0.005: fl.append('foten på feltet')
    if rk0 > rm: fl.append('ingen fot står')
    elif rk > rm: fl.append('ingen fot toler dytten')
    if d_led < 0.017 + 0.005: fl.append('armen dekkjer vindaugsdioden')
    if rekk > REKK: fl.append('knotten langt unna')
    if bak_skj: fl.append('knotten bak skjermen')
    if pd['skoyt']: fl.append('skøyt i filmen')
    if pd['n_ark'] > ARK_I_KIT: fl.append('treng %d ark' % pd['n_ark'])
    rad['kan_lagast'] = not (kol > 1 or rk0 > rm)
    rad['berre_kit_og_LED'] = False                       # sjå produksjon: bjelke, fot og hus finst ikkje i byggjesettet
    rad['flagg'] = '; '.join(fl) or '-'
    rad['sekund'] = time.time() - t0
    return rad, kr

# ------------------------------------------------------------------ dei 18 kroppane
def K_(i, rad, kol, namn, fot, mote, knott, rute, v, rille, H=0.50, r_fot=0.11, over=0.02, **kw):
    d = dict(id=i, rad=rad, kol=kol, namn=namn, fot=fot, mote=mote, knott=knott, rute=rute, v=v, rille=rille, H=H, r_fot=r_fot, over=over)
    d.update(kw); return d

R45, R36, R52 = (0.45, 0.19), (0.36, 0.24), (0.52, 0.16)
KROPPAR = [
    # rad 1: foten bak skjermen
    K_(1, 1, 1, 'D', 'bak', 'ende', 'ledd', R45, 190, 'loddrett', merk='D Ruta på Telt-kroppen: armen til høgre ende, knotten i leddet'),
    K_(2, 1, 2, 'bak-galge', 'bak', 'midt', 'fri', R36, 180, 'kryss', merk='armen går inn bak midten, knotten på høgre ende'),
    K_(3, 1, 3, 'bak-skeiv-høg', 'bak', 'skeiv', 'ledd', R52, 205, 'vassrett', H=0.56),
    K_(4, 1, 4, 'bak-tung', 'bak', 'ende', 'fot', R45, 165, 'loddrett', H=0.44, r_fot=0.12, over=0.12, merk='stor fot, lang bjelke, låg'),
    # rad 2: foten ved sida av skjermen
    K_(5, 2, 1, 'side-ende', 'side', 'ende', 'ledd', R36, 190, 'vassrett'),
    K_(6, 2, 2, 'side-T-låg', 'side', 'midt', 'arm', R45, 205, 'loddrett', H=0.44, over=0.12),
    K_(7, 2, 3, 'side-skeiv', 'side', 'skeiv', 'fri', R52, 180, 'loddrett', r_fot=0.13),
    K_(8, 2, 4, 'side-høg-kryss', 'side', 'ende', 'fot', R45, 190, 'kryss', H=0.56, r_fot=0.09),
    # rad 3: plate under skjermfoten
    K_(9, 3, 1, 'under-ende', 'under', 'ende', 'ledd', R52, 190, 'loddrett'),
    K_(10, 3, 2, 'under-galge', 'under', 'midt', 'fri', R45, 165, 'vassrett', over=0.12),
    K_(11, 3, 3, 'under-skeiv-låg', 'under', 'skeiv', 'arm', R36, 205, 'loddrett', H=0.44),
    K_(12, 3, 4, 'under-T-høg', 'under', 'midt', 'ledd', R45, 180, 'loddrett', H=0.56),
    # rad 4: høva drivne
    K_(13, 4, 1, 'bak-armknott', 'bak', 'ende', 'arm', R36, 165, 'loddrett', r_fot=0.09, over=0.12),
    K_(14, 4, 2, 'side-D', 'side', 'ende', 'ledd', R45, 190, 'loddrett', over=0.12, merk='D-lyset, foten ved sida'),
    K_(15, 4, 3, 'bak-galge-kryss', 'bak', 'midt', 'ledd', R52, 190, 'kryss', H=0.44, r_fot=0.12),
    K_(16, 4, 4, 'side-skeiv-fotknott', 'side', 'skeiv', 'fot', R36, 180, 'vassrett', H=0.56, r_fot=0.09),
]
KONTROLL = [
    K_(17, 0, 1, 'veltar', 'bak', 'ende', 'ledd', R45, 190, 'loddrett', r_fot=0.07, t_fot=0.004, fot_xy=(0.31, 0.50),
       merk='D med foten frå ruta.py: Ø140 × 4 mm ved x 0,31, y 0,50'),
    K_(18, 0, 2, 'umogleg', 'bak', 'ende', 'ledd', (0.60, 0.30), 190, 'kryss', H=0.40, r_fot=0.12,
       merk='bjelken under skjermkanten, 60 × 30 i kryss'),
]
ALLE = KROPPAR + KONTROLL
SPEC = {s['id']: s for s in ALLE}
KAM_D = 3.0

# ------------------------------------------------------------------ kommandoane
def k_kalib():
    t0 = time.time()
    ref = json.load(open(os.path.join(FILMDIR, 'tal-D.json'), encoding='utf-8'))
    nk = ['W350', 'jamnheit', 'auge25', 'auge47', 'auge60', 'bak350', 'skjerm350', 'ansikt350', 's_bak', 's_auge25', 's_skjerm', 'likskap', 'sprang']
    r_ruta = ruta.rekn(ruta.g_ruta(), n=5)
    kr = Kropp(SPEC[1])
    c = kr.rute_c() + np.array([0, 0, ZB])
    pr_ruta = ruta.kropp(c, kr.ut, kr.e, kr.w, kr.d)
    r_mot = rekn_lys(g_lys(kr, prims=pr_ruta), n=5)
    r_d = rekn_lys(g_lys(kr), n=5)
    ut = {}
    for k in nk:
        ut[k] = dict(tal_D=ref[k], ruta_no=r_ruta[k], motor_ruta_kropp=r_mot[k], motor_D_kropp=r_d[k],
                     avvik_motor=(r_mot[k] / ref[k] - 1) if ref[k] else 0.0, avvik_D=(r_d[k] / ref[k] - 1) if ref[k] else 0.0)
        print('%-10s tal-D %8.2f  ruta.py no %8.2f  motor (ruta-kropp) %8.2f  motor (D-kropp) %8.2f  avvik %+5.1f %% / %+5.1f %%' % (
            k, ref[k], r_ruta[k], r_mot[k], r_d[k], 100 * ut[k]['avvik_motor'], 100 * ut[k]['avvik_D']), flush=True)
    ut['_utkraga'] = kontroll_utkraga(); print(ut['_utkraga'])
    lagre('kalibrering', ut)
    logg('kalib (%.0f s): W350 %.3f / %.3f / %.3f mot %.3f; auge25 %.0f / %.0f / %.0f mot %.0f; utkraga %.3f mot %.3f mm' % (
        time.time() - t0, r_ruta['W350'], r_mot['W350'], r_d['W350'], ref['W350'], r_ruta['auge25'], r_mot['auge25'], r_d['auge25'], ref['auge25'],
        ut['_utkraga']['motor_mm'], ut['_utkraga']['analytisk_mm']))

def skriv_csv(rader):
    rows = [rader[k] for k in sorted(rader, key=int)]
    keys = list(rows[0].keys())
    with open(os.path.join(HER, 'tal.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, keys); w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})

def k_tal(kva=None):
    t0 = time.time(); rader = {}
    for sp in ALLE:
        if kva and str(sp['id']) not in kva.split(','): continue
        r, kr = tal(sp); rader[sp['id']] = r
        print('%2d %-20s W %4.2f U %.2f auge %4.0f/%3.0f/%3.0f vol %4.0f sp %4.1f bak %3.0f skj %3.0f ans %2.0f | st %3.0f/%3.0f lik %.2f | m %.2f tipp %5.1f Fk %5.1f rk %4.1f sv %4.2f/%4.2f | %s (%.0f s)' % (
            r['id'], r['namn'], r['W350'], r['U0'], r['auge25'], r['auge47'], r['auge60'], r['augevolum'], r['spegling_blank'], r['bak350'],
            r['skjerm350'], r['ansikt350'], r['s_auge'], r['s_bak'], r['likskap'], r['masse_kg'], r['tipp_deg'], r['F_tipp_knott_N'],
            r['r_krav_cm'], r['svikt_knott_mm'], r['svikt_rute_mm'], r['flagg'], r['sekund']), flush=True)
        if time.time() - t0 > 320: print('stoppar før 6 min'); break
    gamle = json.load(open(TALJSON, encoding='utf-8')).get('rader', {}) if os.path.exists(TALJSON) else {}
    gamle.update({str(k): v for k, v in rader.items()})
    lagre('rader', gamle); skriv_csv(gamle)
    logg('tal (%.0f s): %d kroppar rekna, tal.csv skriven' % (time.time() - t0, len(rader)))

def k_fin(kva):
    t0 = time.time(); ut = {}
    for i in [int(x) for x in kva.split(',')]:
        kr = Kropp(SPEC[i]); g = g_lys(kr)
        a = tal_fin(*g(1.0)); s = tal_fin(*g(0.0))
        f = 350.0 / a['E_felt']
        ut[str(i)] = dict(namn=SPEC[i]['namn'], W350_fin=a['W'] * f, U0_fin=a['U'], bak350_fin=a['E_bak'] * f, skjerm350_fin=a['E_skjerm'] * f,
                          s_bak_fin=s['E_bak'], s_felt_fin=s['E_felt'])
        print(i, {k: round(v, 3) if isinstance(v, float) else v for k, v in ut[str(i)].items()}, flush=True)
    d = json.load(open(TALJSON, encoding='utf-8')).get('fin', {}) if os.path.exists(TALJSON) else {}
    d.update(ut); lagre('fin', d)
    logg('fin (%.0f s): %s' % (time.time() - t0, ', '.join('%s W %.2f U0 %.2f bak %.0f' % (v['namn'], v['W350_fin'], v['U0_fin'], v['bak350_fin']) for v in ut.values())))

def pikselstat(path, n=None):
    im = np.asarray(Image.open(path).convert('RGB')).astype(float)
    H, W, _ = im.shape; n = n or (W // 512, H // 512); st = []
    for i in range(n[1]):
        for j in range(n[0]):
            tl = im[i * 512:(i + 1) * 512, j * 512:(j + 1) * 512]; m = tl.max(-1) > 12
            if not m.any(): continue
            Y = tl[m] @ np.array([0.2126, 0.7152, 0.0722])
            st.append(dict(dekning=m.mean(), rgb=tl[m].mean(0), Y50=np.percentile(Y, 50)))
    return dict(fliser=len(st), dekning=float(np.mean([s['dekning'] for s in st])),
                rgb=[round(float(x), 1) for x in np.mean([s['rgb'] for s in st], 0)], Y50=float(np.mean([s['Y50'] for s in st])))

def k_brett():
    t0 = time.time(); cam = fe.Cam(D=KAM_D)
    ims, masks, ramme = {}, {}, {}
    for sp in ALLE:
        kr = Kropp(sp); V, F = kr.mesh(); V = V.copy()
        c = (V[:, :2].min(0) + V[:, :2].max(0)) / 2; V[:, :2] -= c
        im, mk = fe.render(V, F, cam); ims[sp['id']], masks[sp['id']] = im, mk
        ys, xs = np.nonzero(mk); ramme[sp['id']] = (int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())) if len(xs) else None
    grid = {(s['rad'], s['kol']): s['id'] for s in KROPPAR}
    fe.brett(ims, grid, os.path.join(HER, 'brett.png')); fe.stripe([ims[17], ims[18]], os.path.join(HER, 'velt_umogleg.png'))
    fk = fe.formkritikk({k: masks[k] for k in grid.values()}, grid)
    par = []
    for (r, c), i in grid.items():
        for rr, cc in ((r, c + 1), (r + 1, c)):
            if (rr, cc) in grid:
                a_, b_ = masks[i], masks[grid[(rr, cc)]]; par.append((i, grid[(rr, cc)], float((a_ & b_).sum() / max((a_ | b_).sum(), 1))))
    ref = os.path.join(NL, 'gen01', 'brett.png')
    klipt = [i for i, r in ramme.items() if r and (r[0] <= 1 or r[2] <= 1 or r[1] >= 510 or r[3] >= 510)]
    ut = dict(iou_snitt=fk['iou_snitt'], iou_maks=fk['iou_maks'], iou_par=par, luft={str(k): v for k, v in fk['luft'].items()},
              pikselstat_gen01=pikselstat(ref) if os.path.exists(ref) else None, pikselstat=pikselstat(os.path.join(HER, 'brett.png')),
              klipt_av_ramma=klipt, ramme=ramme, kamera=dict(el=17, az=240, fov=19, D=KAM_D))
    lagre('brett', ut)
    print(json.dumps({k: v for k, v in ut.items() if k not in ('iou_par', 'ramme')}, ensure_ascii=False, default=_j), flush=True)
    logg('brett (%.0f s): nabo-IoU snitt %.2f, maks %.2f; klipt av ramma: %s' % (time.time() - t0, fk['iou_snitt'], fk['iou_maks'], klipt or 'ingen'))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit()
    {'kalib': k_kalib, 'tal': lambda: k_tal(a[1] if len(a) > 1 else None), 'fin': lambda: k_fin(a[1]), 'brett': k_brett}[a[0]]()
