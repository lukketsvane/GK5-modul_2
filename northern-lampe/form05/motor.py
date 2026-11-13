# -*- coding: utf-8 -*-
"""
form05  ·  «Lysrute»: lampa ER vindauget

Ei lysleiarplate i PMMA, kantbelyst frå sylinderen (Telt) eller hovudet (Klemme), med prismefilm frå monitoren
utanpå. Filmen er strålespora per bølgjelengd med film.py (konsept/film). Rommet, mannekengen og tala er dei same
som for A Skiva, B Over og C Vindauge (konsept/tre/tre.py, lysskisse.py). Alt her er modell, ikkje måling.

  python -B motor.py film      fordelinga ut av ruta for kvar lysmotor (film_tabell.npz) og kontroll mot film.py-tala
  python -B motor.py sjekk     kopien av tre.rekn mot tal.md (konsept A)
  python -B motor.py sok       kandidatar for vinklar og motor, berre endepunkta (sok.json)
  python -B motor.py tal       dei valde: overgang, ekstra mål, tal.json, ies_*.ies, scene.json
  python -B motor.py stripe    stripene og regnbogebandet: kva auget ser i stemning (stripe.json, auga_stemning.png)
  python -B motor.py studie    lysstudie.png (og lysstudie_<andre>.png)

Køyr med NUMBA_CACHE_DIR peikande hit (.numba). Prosessen set seg sjølv på låg prioritet.
"""
import os, sys, math, json, time
HER = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('NUMBA_CACHE_DIR', os.path.join(HER, '.numba'))
os.environ.setdefault('NUMBA_NUM_THREADS', '4')
sys.dont_write_bytecode = True

def _skaansam():          # same som rendre_blender.py: lågaste prioritet, ikkje kjerne 0 og 1
    try:
        import ctypes
        k = ctypes.windll.kernel32; h = k.GetCurrentProcess()
        k.SetPriorityClass(h, 0x40); k.SetProcessAffinityMask(h, 0xFC)
    except Exception:
        pass
_skaansam()

import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates
REPO = os.path.normpath(os.path.join(HER, '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'konsept', 'film'))
sys.path.insert(0, os.path.join(REPO, 'konsept', 'lysskisse'))
from film import Film, prisme, analytisk_splitt
import lysskisse as ls
b, ZB, YV, nrm, LUM = ls.b, ls.ZB, ls.YV, ls.nrm, ls.LUM

# ================================================================== lysmotoren: plate, kavitet, film

FILM = Film(prisme(90.0), n_d=1.59, abbe=30.0)     # same ark som vindauge.py: ideelt 90°-prisme (ANTAKING til målt)
LAMDA = (450.0, 555.0, 650.0)
DU = 0.02; NB = 100                                # retningskosinus-ruter på ruta
ETA_INN = {'lgp': 0.80, 'led': 0.85}              # ANSLÅTT: innkopling 0,90 x plate 0,89 / kvit boks med diffusor
A_FRAMSIDE = 0.5                                   # ANTAKING: prikkane spreier like mykje mot begge sider av plata
R_REC = 0.85                                       # ANSLÅTT: refleksjon i kaviteten for lys filmen sender attende
T_BAK = 0.92                                       # Fresnel på to flater når lyset går attende gjennom klar plate
MOTORAR = {'LGP-0': ('lgp', 0), 'LGP-1': ('lgp', 1), 'LGP-2': ('lgp', 2), 'LED-0': ('led', 0), 'LED-1': ('led', 1)}

def _lambert(n, rng, opp=True):
    r = np.sqrt(rng.random(n)); f = 2 * math.pi * rng.random(n)
    z = np.sqrt(np.maximum(1 - r * r, 0))
    return np.c_[r * np.cos(f), r * np.sin(f), z if opp else -z]

def _til_f1(D): return np.c_[D[:, 1], -D[:, 0], D[:, 2]]      # film 1: riller langs u (sylinderen), x på tvers = v
def _fraa_f1(F): return np.c_[-F[:, 1], F[:, 0], F[:, 2]]

def _spor(D, filmnr, lam):
    """D i rutekoordinatar (u, v, n). Film 1 har riller langs u, film 2 langs v. Rifla side vender ut (+n)."""
    if filmnr == 1:
        U, st = FILM.spor(_til_f1(D), lam); return _fraa_f1(U), st
    return FILM.spor(D, lam)

def _hist(D, w):
    h, _, _ = np.histogram2d(D[:, 0], D[:, 1], bins=NB, range=[[-1, 1], [-1, 1]], weights=w)
    return h

def motor_mc(kjelde, filmar, tosidig, lam=555.0, N=400_000, seed=1):
    """Monte Carlo gjennom kavitet og film. Gjev (h_fram, h_bak, F_fram, F_bak) per eining fluks ut av plata/boksen.
    tosidig: klar plate utan reflektor. Lys som filmen kastar attende, går ut baksida (Telt).
    Elles: kvit reflektor bak. Attendekasta lys blir spreidd lambertsk på nytt med R_REC (Klemme)."""
    rng = np.random.default_rng(seed)
    hf = np.zeros((NB, NB)); hb = np.zeros((NB, NB))
    if tosidig:
        w0 = A_FRAMSIDE
        Db = _lambert(N, rng, opp=False); hb += _hist(Db, np.full(N, (1 - A_FRAMSIDE) / N))
    else:
        w0 = A_FRAMSIDE + (1 - A_FRAMSIDE) * R_REC if kjelde == 'lgp' else 1.0
    D = _lambert(N, rng); w = np.full(N, w0 / N); st = np.zeros(N, int)    # 0 opp mot film 1, 1 opp mot film 2, 2 ned mot film 1
    for _ in range(60):
        if not len(D): break
        nyD, nyw, nyst = [], [], []
        def vidare(Dx, wx, sx):
            nyD.append(Dx); nyw.append(wx); nyst.append(np.full(len(Dx), sx, int))
        def kavitet(Dx, wx):            # lys på veg ned i kaviteten
            if not len(Dx): return
            if tosidig:
                hb[:] += _hist(Dx, wx * T_BAK)
            else:
                vidare(_lambert(len(Dx), rng), wx * R_REC, 0)
        if filmar == 0:
            hf[:] += _hist(D, w); break
        for s in (0, 1, 2):
            m = st == s
            if not m.any(): continue
            Ds, ws = D[m], w[m]
            fnr = 2 if s == 1 else 1
            U, ut = _spor(Ds, fnr, lam)
            gj, at = ut == 1, ut == -1
            if s == 0:
                if filmar == 1: hf[:] += _hist(U[gj], ws[gj])
                else: vidare(U[gj], ws[gj], 1)
                kavitet(U[at], ws[at])
            elif s == 1:
                hf[:] += _hist(U[gj], ws[gj]); vidare(U[at], ws[at], 2)
            else:
                kavitet(U[gj], ws[gj]); vidare(U[at], ws[at], 1)
        if not nyD: break
        D = np.concatenate(nyD); w = np.concatenate(nyw); st = np.concatenate(nyst)
        keep = w > 1e-7 / N
        D, w, st = D[keep], w[keep], st[keep]
    return hf, hb, float(hf.sum()), float(hb.sum())

def lag_tabell():
    """Alle motorar, tre bølgjelengder. Lrel = luminans delt på lambertsk luminans for same fluks ut av plata."""
    ut = {}
    for namn, (kj, nf) in MOTORAR.items():
        for tos in ((True, False) if kj == 'lgp' else (False,)):
            for lam in LAMDA:
                hf, hb, Ff, Fb = motor_mc(kj, nf, tos, lam)
                k = f'{namn}|{"tosidig" if tos else "reflektor"}|{lam:.0f}'
                ut[k + '|fram'] = gaussian_filter(hf, 1.0) * math.pi / DU ** 2
                ut[k + '|bak'] = gaussian_filter(hb, 1.0) * math.pi / DU ** 2
                ut[k + '|F'] = np.array([Ff, Fb])
                print(k, 'F_fram %.3f F_bak %.3f  aksen %.2f' % (Ff, Fb, ut[k + '|fram'][NB // 2 - 1:NB // 2 + 1, NB // 2 - 1:NB // 2 + 1].mean()), flush=True)
    np.savez_compressed(os.path.join(HER, 'film_tabell.npz'), **ut)
    return ut

_TAB = None
def tabell():
    global _TAB
    if _TAB is None:
        f = os.path.join(HER, 'film_tabell.npz')
        _TAB = dict(np.load(f)) if os.path.exists(f) else lag_tabell()
    return _TAB

def Lrel(motor, tos, side, ux, uy, lam=555.0):
    T = tabell()[f'{motor}|{"tosidig" if tos else "reflektor"}|{lam:.0f}|{side}']
    c = np.stack([(np.asarray(ux) + 1) / DU - 0.5, (np.asarray(uy) + 1) / DU - 0.5])
    return np.maximum(map_coordinates(T, c.reshape(2, -1), order=1, mode='nearest').reshape(np.shape(ux)), 0.0)

def F(motor, tos, lam=555.0):
    return tabell()[f'{motor}|{"tosidig" if tos else "reflektor"}|{lam:.0f}|F']

def vinkelkurve(motor, tos, plan='tvers', side='fram', lam=555.0, vinklar=np.arange(-85, 86, 1.0)):
    """Lrel mot vinkel frå normalen. 'tvers': i planet på tvers av rillene til film 1 (v–n), 'langs': u–n."""
    s = np.sin(np.radians(vinklar))
    return (Lrel(motor, tos, side, 0 * s, s, lam) if plan == 'tvers' else Lrel(motor, tos, side, s, 0 * s, lam))

def kontroll_film():
    """Sporinga mot tala i konsept/film/00-vindauge-utan-linse.md."""
    T, R, L = FILM.lober(0, 0, 550, 'prisme')
    Tf, Rf, Lf = FILM.lober(0, 0, 550, 'flat')
    T30, R30, L30 = FILM.lober(30, 0, 550, 'flat')
    lb = abs(FILM.lober(0, 0, 450, 'prisme')[2][0][0]); lr = abs(FILM.lober(0, 0, 650, 'prisme')[2][0][0])
    D = np.tile([0, 0, -1.0], (5, 1)); U, st = FILM.spor(D, 550)        # forteikn: lys inn mot prismesida, ut på andre sida?
    return dict(lobe_550=abs(L[0][0]), lobe_del=[round(e[1], 3) for e in L[:2]], T_prisme=T, analytisk=analytisk_splitt(float(FILM.n(550))),
                T_flat_rett=Tf, flat30_lobe=L30[0][0] if L30 else None, flat30_T=T30, lobe_450=lb, lobe_650=lr,
                forteikn_ut_z=float(U[st == 1][:, 2].mean()) if (st == 1).any() else None,
                note='00-vindauge: ±30,8° (0,47 kvar, T 0,93), analytisk 30,69°, flatside rett på T 0, flatside 30°: lobe −0,8° T 0,63, 450/650 nm: 31,75/30,25°')

# ================================================================== ruta som strøk i lysmotoren

class Rute:
    """Lysande rute. H: midt på hengsellina. u: langs hengslet (sylinderen, rillene til film 1). e: frå hengslet mot fri kant.
    n: framsida (filmsida). bu x bv: storleik (m). motor: nøkkel i MOTORAR. tos: klar plate (lyser òg bak)."""
    def __init__(s, H, u, e, n, bu, bv, motor, tos, gap=0.022):
        s.u, s.e, s.n = nrm(u), nrm(e), nrm(n)
        s.v = s.e if (np.cross(s.u, s.e) @ s.n) > 0 else -s.e      # (u, v, n) høgrehendt
        s.bu, s.bv, s.motor, s.tos = bu, bv, motor, tos
        s.H0 = np.asarray(H, float) + gap * s.e
        s.C = s.H0 + 0.5 * bv * s.e
        s.A = bu * bv
        kj = MOTORAR[motor][0]
        s.eta_inn = ETA_INN[kj]
        s.Ff, s.Fb = F(motor, tos)
    def punkt(s, nu, nv):
        return [s.H0 + s.u * s.bu * ((i + 0.5) / nu - 0.5) + s.e * s.bv * (j + 0.5) / nv for i in range(nu) for j in range(nv)]
    def L_rel(s, d):
        d = np.atleast_2d(d); dn = d @ s.n; ux, uy = d @ s.u, d @ s.v
        return np.where(dn > 0, Lrel(s.motor, s.tos, 'fram', ux, uy), Lrel(s.motor, s.tos, 'bak', ux, uy) if (s.tos or s.Fb > 0) else 0.0)
    def lys(s, W, K, namn='rute'):
        lm = W * ls.LMW_KJELDE; Lref = lm * s.eta_inn / (math.pi * s.A)
        prim = ls.Rekt(s.H0 - 0.5 * s.bu * s.u, s.u * s.bu, s.e * s.bv)
        I = lambda d: s.A * Lref * s.L_rel(d) * np.abs(np.atleast_2d(d) @ s.n)
        L = lambda d: Lref * s.L_rel(d)
        l = ls.Lys(lm, K, prim, s.punkt(5, 3), I, L, namn)
        l.mater = True; l.lm_ut = lm * s.eta_inn * (s.Ff + s.Fb); l.rute = s; l.Lref = Lref
        return l

# ================================================================== dei to variantane

def rot_x(v, a):
    c, s_ = math.cos(a), math.sin(a)
    return np.array([v[0], v[1] * c - v[2] * s_, v[1] * s_ + v[2] * c])

TELT = dict(                         # mål i meter i romkoordinatane til lysskisse (x mot høgre, y mot veggen, z opp, ZB = bordplata)
    fot=(0.44, 0.52), fot_r=0.130, fot_t=0.010,          # Ø 260 x 10 stål: tippar ikkje (sjå tal.json, stabilitet)
    arm_x=0.32,                                          # flattstål 60 x 8 alu, 5 cm til høgre for skjermkanten (0,27)
    syl_y=0.42, syl_z=0.58, syl_r=0.020, syl_x=(-0.24, 0.32),   # Ø 40 x 560: LED-list, drivar, kodar i knotten
    bu=0.48, bv=0.26,                                    # ruta 480 x 260 x 4 PMMA: feltet er 600 x 400, og 0,125 m² held stemninga under 500 cd/m²
    motor='LGP-1', tos=True, beta_a=15.0, beta_s=90.0)   # beta: vinkelen til ruta over vassrett mot brukaren
KLEMME = dict(
    klemme=(0.70, 0.30), stong_r=0.0125, stong_h=0.62,  # klemt på høgre sidekant, Ø 25 stong
    lengd=0.60, breidd=0.22, x_ende=0.62,               # hovudet 600 x 220 mot venstre frå stonga
    motor='LGP-1', tos=False, rho_a=15.0, rho_s=-70.0)  # rho: rull om lengdeaksen, + mot brukaren

def telt_rute(P, beta):
    bt = math.radians(beta)
    e = np.array([0.0, -math.cos(bt), math.sin(bt)]); n = np.array([0.0, -math.sin(bt), -math.cos(bt)])
    H = b(0.5 * (P['syl_x'][0] + P['syl_x'][1]), P['syl_y'], P['syl_z'])
    return Rute(H, (1, 0, 0), e, n, P['bu'], P['bv'], P['motor'], P['tos'])

def telt_kropp(P):
    x0, x1 = P['syl_x']; y, z = P['syl_y'], P['syl_z']; fx, fy = P['fot']
    alu = (0.62, 0.62, 0.60); burg = (0.25, 0.06, 0.07)
    syl = ls.Syl(b(x0, y, z), b(x1, y, z), P['syl_r'], rho=burg)
    knott = ls.Syl(b(x1, y, z), b(x1 + 0.022, y, z), 0.028, rho=alu)
    kne = b(P['arm_x'] + 0.04, y + 0.04, 0.30)
    arm = [ls.Syl(b(fx, fy, P['fot_t']), kne, 0.010, rho=alu), ls.Syl(kne, b(x1 + 0.011, y, z - 0.03), 0.010, rho=alu)]
    fot = ls.Skive(b(fx, fy, P['fot_t']), (0, 0, 1), P['fot_r'], rho=burg)
    return [syl, knott, fot] + arm

def klemme_rute(P, rho):
    r = math.radians(rho)
    n = np.array([0.0, -math.sin(r), -math.cos(r)]); u = np.array([-1.0, 0, 0])
    e = np.array([0.0, math.cos(r), -math.sin(r)]) * -1          # breidda står vinkelrett på n og u
    kx, ky = P['klemme']
    H = b(P['x_ende'] - 0.5 * P['lengd'], ky, P['stong_h'] - 0.015) - 0.5 * P['breidd'] * e
    return Rute(H, u, e, n, P['lengd'], P['breidd'], P['motor'], P['tos'], gap=0.0)

def klemme_kropp(P, rute):
    kx, ky = P['klemme']; alu = (0.55, 0.53, 0.50)
    sx = kx - 0.04
    stong = ls.Syl(b(sx, ky, -0.03), b(sx, ky, P['stong_h']), P['stong_r'], rho=alu)
    ledd = ls.Syl(b(sx - 0.02, ky, P['stong_h']), b(P['x_ende'], ky, P['stong_h']), 0.016, rho=alu)
    skal = ls.Rekt(rute.H0 - 0.5 * rute.bu * rute.u - 0.014 * rute.n, rute.u * rute.bu, rute.e * rute.bv, rho=alu)
    return [stong, ledd, skal]

def g_telt(P=TELT, beta_a=None, beta_s=None, motor=None):
    P = dict(P);
    if motor: P['motor'] = motor
    ba = P['beta_a'] if beta_a is None else beta_a; bs = P['beta_s'] if beta_s is None else beta_s
    kropp = telt_kropp(P)
    def g(t):
        W = 1.25 * 4.0 ** float(t); K = 2200 + 500 * float(t)      # 2200 K i stemning, 2700 K i arbeid
        r = telt_rute(P, bs + (ba - bs) * float(t)); g.rute = r
        return [r.lys(W, K, 'telt')], kropp
    g.P = P; return g

def g_klemme(P=KLEMME, rho_a=None, rho_s=None, motor=None):
    P = dict(P)
    if motor: P['motor'] = motor
    ra = P['rho_a'] if rho_a is None else rho_a; rs = P['rho_s'] if rho_s is None else rho_s
    def g(t):
        W = 1.25 * 4.0 ** float(t); K = 2200 + 500 * float(t)
        r = klemme_rute(P, rs + (ra - rs) * float(t)); g.rute = r
        return [r.lys(W, K, 'klemme')], klemme_kropp(P, r)
    g.P = P; return g

# ================================================================== tal: kopi av tre.rekn, og dei tre måla frå granskinga

def rekn(g, n=5):
    """Kopi av tre.rekn (konsept/tre/tre.py), prøvd mot tal.md med 'sjekk'."""
    R, m = ls.overgang(g, n=n)
    s, a = R[0], R[-1]
    f = 350.0 / max(a['E_felt'], 1e-9)
    La = lambda d: max(d['L_lampe'], d['L_flate'])
    return dict(W350=a['W'] * f, timar=ls.CELLE / (a['W'] * f), jamnheit=a['U'], lm_ut=a['lm'], verknad=a['lm'] / (a['W'] * 100),
                vegg350=a['E_vegg'] * f, bak350=a['E_bak'] * f, ansikt350=a['E_ansikt'] * f, skjerm350=a['E_skjerm'] * f,
                auge25=max(a['L_auge25'], a['L_flate']) * f, auge47=La(a) * f, auge60=max(a['L_auge60'], a['L_flate']) * f,
                s_W=s['W'], s_lm=s['lm'], s_felt=s['E_felt'], s_vegg=s['E_vegg'], s_bak=s['E_bak'], s_skjerm=s['E_skjerm'],
                s_auge25=max(s['L_auge25'], s['L_flate']), s_auge47=La(s), s_auge60=max(s['L_auge60'], s['L_flate']),
                likskap=ls.likskap(s['_fordeling'], a['_fordeling']), topp=m['topp'], sprang=m['sprang'], jamn_auke=m['jamn_auke'],
                veg_felt=[r['E_felt'] for r in R], veg_skjerm=[r['E_skjerm'] for r in R], veg_auge=[La(r) for r in R], veg_W=[r['W'] for r in R])

AUGEVOLUM = [b(x, y, h) for x in (-0.15, 0.0, 0.15) for y in (-0.15, 0.0) for h in (0.42, 0.47, 0.52)]

def ekstra(lys, kropp):
    """F6 som arealsnitt på 4 cm, spegling i skjermen tilta 0–20°, og største luminans frå ruta i augevolumet."""
    R = ls.rom(); okkl = ls.STATISK + list(kropp) + [l.prim for l in lys]
    Ed = ls.E_direkte(R.P, R.N, lys, okkl); Ei, B = R.radiositet(Ed)
    kv = R.kart[1]; Eiv = Ei[kv.sl].reshape(kv.nu, kv.nv, 3)
    xs = np.arange(-0.33, 0.35, 0.04); zs = ZB + np.arange(0.07, 0.65, 0.04)
    P = np.array([[x, YV - 1e-4, z] for x in xs for z in zs]); N = np.tile([0, -1.0, 0], (len(P), 1))
    Ew = (ls.E_direkte(P, N, lys, okkl) + kv.oppslag(P, Eiv)) @ LUM
    r = lys[0].rute; pts = r.punkt(9, 5)
    okkl_a = [p for p in okkl if p not in ls.PERSON]
    Lmax = 0.0; EV = np.array(AUGEVOLUM)
    for S in pts:
        vis = ls.synleg(EV, S, okkl_a, lys[0].prim)
        if vis.any():
            d = EV[vis] - S; d /= np.linalg.norm(d, axis=1)[:, None]
            Lmax = max(Lmax, float(lys[0].L(d).max()))
    spegl = {}
    for tau in (0, 5, 10, 15, 20):
        ta = math.radians(tau)
        Q0 = b(0.0, 0.45, 0.11); ns = np.array([0, -math.cos(ta), math.sin(ta)]); opp = np.array([0, math.sin(ta), math.cos(ta)])
        best = 0.0
        for E in AUGEVOLUM:
            M = E - 2 * ((E - Q0) @ ns) * ns
            for S in pts:
                if (S - Q0) @ ns <= 0: continue
                t = ((Q0 - M) @ ns) / ((S - M) @ ns); X = M + t * (S - M)
                if 0 < t < 1 and abs(X[0]) < 0.27 and 0 < (X - Q0) @ opp < 0.31:
                    best = max(best, float(lys[0].L(nrm(X - S)[None])[0]))
        spegl[tau] = best
    return dict(bak_4cm=float(Ew.mean()), bak_4cm_min=float(Ew.min()), L_augevolum=Lmax, spegl=spegl, spegl_maks=max(spegl.values()))

def endepunkt(g, t):
    lys, kropp = g(t)
    d = ls.tal(lys, kropp); x = ekstra(lys, kropp)
    return d, x, lys

def kort(d, x, W350=None):
    f = 350.0 / max(d['E_felt'], 1e-9) if W350 else 1.0
    return dict(W=d['W'] * f, E_felt=d['E_felt'] * f, U=d['U'], bak=d['E_bak'] * f, bak4=x['bak_4cm'] * f, skjerm=d['E_skjerm'] * f,
                auge=max(d['L_auge25'], d['L_auge47'], d['L_auge60'], d['L_flate']) * f, augevol=x['L_augevolum'] * f,
                spegl=x['spegl_maks'] * f, lm=d['lm'] * f, ansikt=d['E_ansikt'] * f)

# ================================================================== modusar

def m_sok():
    ut = []
    def logg(namn, t, g):
        t0 = time.time(); d, x, lys = endepunkt(g, t)
        k = kort(d, x, W350=(t == 1))
        k.update(namn=namn, t=t, sek=round(time.time() - t0, 1)); ut.append(k)
        print(namn, {a: (round(v, 2) if isinstance(v, float) else v) for a, v in k.items()}, flush=True)
    for mo in ('LGP-0', 'LGP-1', 'LGP-2'):
        for ba in (-15.0, 0.0, 15.0, 30.0):
            logg(f'telt {mo} beta_a {ba:+.0f}', 1, g_telt(beta_a=ba, motor=mo))
    for bs in (90.0, 115.0):
        logg(f'telt LGP-1 beta_s {bs:.0f}', 0, g_telt(beta_s=bs))
    for mo in ('LGP-0', 'LGP-1', 'LGP-2', 'LED-0', 'LED-1'):
        for ra in (0.0, 15.0, 30.0):
            logg(f'klemme {mo} rho_a {ra:+.0f}', 1, g_klemme(rho_a=ra, motor=mo))
    for rs in (-70.0, 70.0):
        logg(f'klemme LGP-1 rho_s {rs:+.0f}', 0, g_klemme(rho_s=rs))
    json.dump(ut, open(os.path.join(HER, 'sok.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def m_sjekk():
    sys.path.insert(0, os.path.join(REPO, 'konsept', 'tre'))
    import tre
    t0 = time.time(); r = rekn(tre.KONSEPT['A']['g'])
    ref = json.load(open(os.path.join(REPO, 'konsept', 'tre', 'tal-A.json'), encoding='utf-8'))
    nk = ('W350', 'jamnheit', 'auge25', 'auge47', 'skjerm350', 'bak350', 's_auge25', 's_bak', 's_skjerm', 'likskap', 'sprang')
    av = {k: (round(float(r[k]), 3), round(float(ref.get('bak350_grovt' if k == 'bak350' else k)), 3)) for k in nk}
    print('kopien mot tal-A.json (bak350 mot bak350_grovt):', av, 'sek', round(time.time() - t0))
    json.dump(av, open(os.path.join(HER, 'sjekk.json'), 'w', encoding='utf-8'), indent=1)

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    a = sys.argv[1:]
    if a and a[0] == 'film':
        print(kontroll_film()); lag_tabell()
    elif a and a[0] == 'sjekk':
        m_sjekk()
    elif a and a[0] == 'sok':
        m_sok()
    elif a and a[0] in ('tal', 'stripe', 'studie'):
        import motor_ut
        getattr(motor_ut, 'm_' + a[0])()
