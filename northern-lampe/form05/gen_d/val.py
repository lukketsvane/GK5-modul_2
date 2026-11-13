# -*- coding: utf-8 -*-
"""
gen_d/val.py  ·  valet etter generasjon D  (13.11.2026)

Hovudspørsmålet: kan CAD-kroppen (konsept/film/cad/lampe.py, «Ruta på fot») bli eit arbeidslys, altså 350 lx på feltet
framfor skjermen, utan å velte eller blende? Fridomsgradene er høgda på aksen, hellinga, kvar foten står i høve til feltet
og utsvinget på armen. Lyset er lysmotoren til lys_sjekk.py (rute.rute med lysleiar, 30 % opp gjennom arket, 60 % ned,
10 % ned ved den skrå kanten, 60 % av stripa inn i plata: alt ANTAKING derifrå). Massen er lampe.py sine delar, kalibrert
mot cad/ut/kontroll.json. Arket er arbeidsverdiane i konsept/vindauge/film/arket.md (H1), mot ideelt 90°-prisme.

Same tal() på alle: fint gitter (celler 4 cm, arealsnitt), augevolum, spegling i skjerm tilta 0 til 20°, tipp og svikt.
Grovt søk (berre direkte lys, utan sprett) først, full rekning (ls.tal med sprett + fint gitter) berre for avgjerda.

  python -B val.py ford            fordelingane ut av ruta: ideelt prisme og arket, mellomlagra i _ford_*.npz
  python -B val.py kalib           CAD-kroppen som teikna, mot lys_sjekk.py og kontroll.json
  python -B val.py sok             søket: høgd x helling x utsving x plassering, direkte lys -> sok.csv
  python -B val.py cad namn,..     full rekning for namngjevne variantar -> val_tal.json
  python -B val.py gen a,b,c       gen_d-framlegga (val_forslag.md) med arket og ideelt prisme, fint gitter -> val_tal.json
  python -B val.py studie a        lysstudie, studie_a.png
Éin prosess om gongen, låg prioritet (IDLE, via motor.py), kvar køyring under 6 min. Skriv berre i gen_d/.
"""
import os, sys, math, json, time, re, csv
HER = os.path.dirname(os.path.abspath(__file__))
F5 = os.path.dirname(HER); NL = os.path.dirname(F5); ROT = os.path.dirname(NL)
os.environ.setdefault('NUMBA_CACHE_DIR', os.path.join(F5, '.numba'))
sys.dont_write_bytecode = True
sys.path.insert(0, HER)
import numpy as np
import motor as M                                   # gen_d/motor.py: set IDLE, importerer ruta, rute, lysskisse, felles
ls, rutemod, ruta, fe = M.ls, M.rutemod, M.ruta, M.fe
from film import Film, prisme
b, ZB, YV, nrm = ls.b, ls.ZB, ls.YV, ls.nrm
G = 9.81
VALJSON = os.path.join(HER, 'val_tal.json')
LAMPE = os.path.join(ROT, 'konsept', 'film', 'cad', 'lampe.py')
KONTROLL = os.path.join(ROT, 'konsept', 'film', 'cad', 'ut', 'kontroll.json')

def lagre(nokkel, verdi):
    d = json.load(open(VALJSON, encoding='utf-8')) if os.path.exists(VALJSON) else {}
    if isinstance(verdi, dict) and isinstance(d.get(nokkel), dict): d[nokkel].update(verdi)
    else: d[nokkel] = verdi
    json.dump(d, open(VALJSON, 'w', encoding='utf-8'), indent=1, ensure_ascii=False, default=M._j)

def logg(tekst):
    with open(os.path.join(HER, 'logg.md'), 'a', encoding='utf-8') as f:
        f.write('- %s val %s\n' % (time.strftime('%H.%M'), tekst))

# ------------------------------------------------------------------ arket
ARKET = Film(prisme(90.0, avrunding=0.03), n_d=1.57, abbe=30.0, spreiing=0.3, spreiing_langs=0.3, haze=0.01)   # arket.md H1
FILMAR = {'ideell': rutemod.FILM, 'ark': ARKET}      # rute.FILM: prisme(90), n 1,59 (ANTAKING i alle tal før arket.md)
_FORD = {}
def ford(kva):
    """Fordelinga ut av ei rute med filmen ytst, flatsida inn (som ruta.ford('ut') og lys_sjekk F_OPP)."""
    if kva not in _FORD:
        fil = os.path.join(HER, '_ford_%s.npz' % kva)
        if os.path.exists(fil):
            z = np.load(fil); _FORD[kva] = dict(tab=z['tab'], verknad=float(z['verknad']), namn=kva)
        else:
            f = rutemod.utfordeling(film=FILMAR[kva], innside='flat')
            np.savez(fil, tab=f['tab'], verknad=f['verknad']); _FORD[kva] = f
    return _FORD[kva]

def bruk_film(kva):
    """Same film i gen_d-motoren (ruta.ford('ut') -> motor.ford)."""
    ruta._FORD.clear(); M._FORD.clear()
    ruta._FORD['ut'] = ford(kva)
    M.FILMPROFIL = 'ideelt 90° (ANTAKING)' if kva == 'ideell' else 'arket.md H1: prisme(90, avrunding 0,03), n 1,57, Abbe 30, spreiing 0,3°, haze 0,01'

F_NED = None
def ford_ned():
    global F_NED
    if F_NED is None: F_NED = rutemod.utfordeling(film=None)
    return F_NED

# ------------------------------------------------------------------ CAD-kroppen: parametrane les vi frå lampe.py
NAMN = ('RUTE_B', 'RUTE_D', 'VINKEL', 'AKSE_H', 'BJELKE_D', 'FOT_D', 'FOT_H', 'ARM_B', 'ARM_T', 'ARM_UT', 'KNOTT_D', 'KNOTT_L',
        'RUTE_T', 'FILM_T', 'BALLAST_D', 'BALLAST_T')
def les_lampe():
    p = {}
    for line in open(LAMPE, encoding='utf-8'):
        m = re.match(r'^([A-Z_]+)\s*=\s*(-?[0-9.]+)', line)
        if m and m.group(1) in NAMN: p[m.group(1)] = float(m.group(2))
    return p
CAD0 = les_lampe()
PLASS0 = (0.47, 0.30, 0.0)          # lys_sjekk.py: midt i foten 47 cm til høgre og 30 cm inn på bordet, ikkje dreidd
INN, OPP, NED, KANT = 0.60, 0.30, 0.60, 0.10      # lys_sjekk.py (ANTAKING der)
LMW_STRIPE = 100.0                  # lys_sjekk.py: lm = W · 100 · INN
RHO = dict(petg=1.27e-3 * 0.55, pmma=1.19e-3, alu=2.70e-3, staal=7.85e-3, messing=8.5e-3, film=1.3e-3, gummi=1.1e-3)   # g/mm³, lampe.py

def mal(p):
    """Avleidde mål som i lampe.py (mm, lampa sitt eige system: origo midt i foten, x mot høgre, y bort frå brukaren)."""
    d = dict(p); R = p['BJELKE_D'] / 2; d['R'] = R
    d['XF'], d['YA'] = 40.0, 44.0
    d['XT'] = d['XF'] + p['ARM_UT']; d['YB'] = d['YA'] - p['ARM_T'] / 2 - 1.0 - R
    d['X_LH0'], d['X_LH1'] = d['XT'] - p['ARM_B'] / 2, d['XT'] + p['ARM_B'] / 2
    d['X_BJ1'] = d['X_LH0'] - 1.0; d['X_RUTE1'] = d['X_BJ1'] - 20.0; d['X_RUTE0'] = d['X_RUTE1'] - p['RUTE_B']
    d['X_BJ0'] = d['X_RUTE0'] - 5.0; d['X_KN0'] = d['X_LH1'] + 3.0; d['X_BOLT0'] = d['X_BJ1'] - 12.0
    d['U_KANT'] = 3.9; d['R_INN'] = 6.0; d['Z_BOY'] = p['FOT_H'] + p['ARM_T'] + 6.0
    return d

def midtline(d, z):
    t = min(max((z - 45.0) / (d['AKSE_H'] - 30.0 - 45.0), 0.0), 1.0)
    return d['XF'] + d['ARM_UT'] * (3 * t * t - 2 * t ** 3)

def retning(d):
    t = math.radians(d['VINKEL'])
    return np.array([0.0, -math.cos(t), -math.sin(t)]), np.array([0.0, -math.sin(t), math.cos(t)])   # s (ut i ruta), n (oppsida)

def delar(d):
    """[(namn, masse g, tyngdepunkt mm)] for lampa. Massane er lampe.py sine (kontroll.json), skalerte med måla."""
    s, n = retning(d); A = np.array([0.0, d['YB'], d['AKSE_H']])
    ax = lambda x, u=0.0: A + np.array([x, 0, 0]) + s * u
    k = (d['FOT_D'] / 158.0) ** 2
    zs = np.linspace(d['Z_BOY'], d['AKSE_H'], 200); xs = np.array([midtline(d, z) for z in zs])
    ds = np.hypot(np.diff(xs), np.diff(zs)); Lb = ds.sum()
    cb = np.array([((xs[1:] + xs[:-1]) / 2 * ds).sum() / Lb, d['YA'], ((zs[1:] + zs[:-1]) / 2 * ds).sum() / Lb])
    gmm = d['ARM_B'] * d['ARM_T'] * RHO['alu']
    arm = [(gmm * Lb, cb), (gmm * 34.0, np.array([d['XF'], d['YA'] - d['ARM_T'] / 2 - 6 - 17.0, d['FOT_H'] + d['ARM_T'] / 2])),
           (math.pi / 4 * ((6 + d['ARM_T']) ** 2 - 36) * d['ARM_B'] * RHO['alu'], np.array([d['XF'], d['YA'] - 6, d['FOT_H'] + 9])),
           (math.pi / 8 * d['ARM_B'] ** 2 * d['ARM_T'] * RHO['alu'], np.array([d['XT'], d['YA'], d['AKSE_H'] + 2 * d['ARM_B'] / (3 * math.pi)]))]
    m_arm = sum(m for m, _ in arm); c_arm = sum(m * c for m, c in arm) / m_arm
    m_arm *= 165.5 / 171.06                                   # hol og avrunding: kalibrert mot kontroll.json (165,5 g)
    xm = (d['X_RUTE0'] + d['X_RUTE1']) / 2; lb = d['X_BJ1'] - d['X_BJ0']
    D = [('fot', 61.7 * k, np.array([0, 0, 11.0])), ('botnlok', 23.1 * k, np.array([0, 0, 1.0])),
         ('ballast', math.pi * (d['BALLAST_D'] / 2) ** 2 * d['BALLAST_T'] * RHO['staal'], np.array([0, 0, d['FOT_H'] - 2.4 - d['BALLAST_T'] / 2])),
         ('arm', m_arm, c_arm), ('kabeldeksel', 4.4 * d['AKSE_H'] / 260.0, c_arm),
         ('leddhus', 22.2, np.array([d['XT'], (d['YB'] + d['YA']) / 2, d['AKSE_H']])),
         ('bjelke og lok', 160.2 * lb / 325.0 * (d['BJELKE_D'] / 32.0) ** 2, ax((d['X_BJ0'] + d['X_BJ1']) / 2)),
         ('lysleiar', (d['RUTE_B'] * d['RUTE_D'] * d['RUTE_T'] - d['RUTE_B'] * d['RUTE_T'] ** 2 / 2) * RHO['pmma'], ax(xm, d['U_KANT'] + d['RUTE_D'] / 2)),
         ('prismeark', d['RUTE_B'] * (d['RUTE_D'] - 6) * 0.25 * RHO['film'], ax(xm, d['U_KANT'] + (d['RUTE_D'] - 6) / 2)),
         ('flatstong og stripe', (12 * 2 * RHO['alu'] + 8 * 2 * RHO['gummi']) * (d['RUTE_B'] - 4), ax(xm)),
         ('knott', 159.2 * (d['KNOTT_D'] / 44.0) ** 2, ax(d['X_KN0'] + d['KNOTT_L'] / 2)),
         ('bolt, mutter, skiver', 33.7 + 6.0 + 4.0 + 0.2, ax(d['X_BOLT0'] + 38.0)),
         ('skruar', 5.4 + 3.6, np.array([d['XF'], 18.0, 14.0])),
         ('ekstra', 25.0, np.zeros(3))]                       # lampe.py: 25 g i M, ikkje i momentet (kabel, mutrar)
    return D

def mek(d):
    """Masse, tyngdepunkt, tipp og kreftene som veltar, med same formlar som lampe.kontroll() og som motor.F_tipp."""
    D = delar(d)
    Mg = sum(m for _, m, _ in D)
    T = sum(m * c for nm, m, c in D if nm != 'ekstra') / Mg
    r = d['FOT_D'] / 2; e = math.hypot(T[0], T[1])
    g = 9.81e-3
    s, n = retning(d)
    ut = dict(masse_g=Mg, tyngdepunkt_mm=T.tolist(), fot_cm2=math.pi * r * r / 100, e_mm=e,
              veltevinkel=math.degrees(math.atan2(r - e, T[2])),
              velt_venstre_N=Mg * g * (r + T[0]) / max(-d['X_RUTE0'] - r, 1e-6),                       # lampe.kontroll
              velt_framme_N=Mg * g * (r + T[1]) / max(-(d['YB'] - (d['U_KANT'] + d['RUTE_D'])) - r, 1e-6),
              velt_dytt_topp_N=Mg * g * (r - e) / d['AKSE_H'])
    # same som motor.F_tipp: trykk ned på alle fire hjørne av ruta (der ruta faktisk står), dytt i 16 retningar på knotten
    parts = [(m / 1000, c / 1000) for nm, m, c in D if nm != 'ekstra'] + [(0.025, np.zeros(3))]
    th = np.arange(48) / 48 * 2 * math.pi; hull = np.c_[r / 1000 * np.cos(th), r / 1000 * np.sin(th)]
    A = np.array([0.0, d['YB'], d['AKSE_H']]) / 1000
    hj = [A + np.array([x, 0, 0]) / 1000 + s * u / 1000 for x in (d['X_RUTE0'], d['X_RUTE1']) for u in (d['U_KANT'], d['U_KANT'] + d['RUTE_D'])]
    ut['trykk_ruta_N'] = min(M.F_tipp(parts, hull, q, np.array([0, 0, -1.0])) for q in hj)
    K = A + np.array([d['X_KN0'] + d['KNOTT_L'] / 2, 0, 0]) / 1000
    ut['dytt_knott_N'] = min(M.F_tipp(parts, hull, K, dd) for dd in M.RETN[:-1])
    ut['stab_ok'] = bool(ut['veltevinkel'] >= M.TIP_MIN and ut['trykk_ruta_N'] >= M.F_DYTT and ut['dytt_knott_N'] >= 3.1)
    # foten som trengst (same plassering, same ballast): tipp 6°, trykk på ruta 5 N og dytt på knotten 3,1 N (som i dag)
    def ok(rr):
        hh = np.c_[rr * np.cos(th), rr * np.sin(th)]
        tip = math.degrees(math.atan2(rr - e / 1000, T[2] / 1000))
        return (tip >= M.TIP_MIN and min(M.F_tipp(parts, hh, q, np.array([0, 0, -1.0])) for q in hj) >= M.F_DYTT
                and min(M.F_tipp(parts, hh, K, dd) for dd in M.RETN[:-1]) >= 3.1)
    lo, hi = 0.02, 0.6
    if ok(hi):
        for _ in range(22):
            mid = (lo + hi) / 2
            if ok(mid): hi = mid
            else: lo = mid
        ut['fot_D_krav_mm'] = 2000 * hi
    else:
        ut['fot_D_krav_mm'] = float('inf')
    ut.update(svikt(d, D))
    return ut

def svikt(d, D):
    """Svikt under 5 N: knotten vassrett (armen, 40 x 5 alu, ut av planet) og framkanten av ruta ned (arm, bjelke, plate).
    Euler-Bernoulli og St-Venant, stive ledd og ingen glid i friksjonsleddet (ANTAKING). E PETG 2 GPa og 50 % av
    bjelkesnittet berande (ANTAKING), PMMA 3 GPa, plata ber med ei breidd lik djupna (45° spreiing, ANTAKING)."""
    E_al, G_al = 70e9, 26e9
    b_, t_ = d['ARM_B'] / 1000, d['ARM_T'] / 1000
    EIs, EIw, GJ = E_al * t_ * b_ ** 3 / 12, E_al * b_ * t_ ** 3 / 12, G_al * b_ * t_ ** 3 / 3
    R = d['BJELKE_D'] / 2000; Ib = 0.5 * math.pi * (2 * R) ** 4 / 64; EIb, GJb = 2e9 * Ib, 0.75e9 * 2 * Ib
    zs = np.linspace(d['Z_BOY'], d['AKSE_H'], 25)
    arm = [np.array([midtline(d, z), d['YA'], z]) / 1000 for z in zs]
    w = np.array([0.0, 1.0, 0.0])
    def forsk(kjede, P, F, Tp):
        u = np.zeros(3)
        for p0, p1, typ in kjede:
            L = np.linalg.norm(p1 - p0)
            if L < 1e-7: continue
            t = (p1 - p0) / L; n = 12; ds = L / n
            for i in range(n):
                x = p0 + t * (i + 0.5) * ds; Mo = np.cross(P - x, F)
                if typ == 'plate':
                    q = nrm(np.cross(t, w)); th = (w * (Mo @ w) / EIs + q * (Mo @ q) / EIw + t * (Mo @ t) / GJ) * ds
                else:
                    a = nrm(np.cross(t, [0, 0, 1.0])) if abs(t[2]) < 0.99 else np.array([1.0, 0, 0]); c = np.cross(t, a)
                    th = (a * (Mo @ a) / EIb + c * (Mo @ c) / EIb + t * (Mo @ t) / GJb) * ds
                u += np.cross(th, Tp - x)
        return u
    ch = [(p, q, 'plate') for p, q in zip(arm[:-1], arm[1:])]
    A = np.array([d['XT'], d['YB'], d['AKSE_H']]) / 1000
    K = np.array([d['X_KN0'] + d['KNOTT_L'] / 2, d['YB'], d['AKSE_H']]) / 1000
    sv_k = max(np.linalg.norm(forsk(ch, K, 5.0 * dd, K)) for dd in M.RETN[:-1])
    s, n = retning(d)
    xm = (d['X_RUTE0'] + d['X_RUTE1']) / 2000
    Pb = np.array([xm, d['YB'] / 1000, d['AKSE_H'] / 1000])
    fr = Pb + s * (d['U_KANT'] + d['RUTE_D']) / 1000
    F = np.array([0, 0, -5.0])
    u_kropp = forsk(ch + [(A, Pb, 'bjelke')], fr, F, fr)
    Ep, tp = 3e9, d['RUTE_T'] / 1000; L = d['RUTE_D'] / 1000
    u_plate = 5.0 * math.cos(math.radians(d['VINKEL'])) * L ** 3 / (3 * Ep * L * tp ** 3 / 12)
    # friksjonsleddet: momentet frå 5 N på framkanten om bolten
    Mledd = 5.0 * (d['U_KANT'] + d['RUTE_D']) / 1000 * math.cos(math.radians(d['VINKEL']))
    return dict(svikt_knott_mm=sv_k * 1000, svikt_framkant_mm=(np.linalg.norm(u_kropp) + u_plate) * 1000,
                svikt_framkant_kropp_mm=np.linalg.norm(u_kropp) * 1000, svikt_framkant_plate_mm=u_plate * 1000, moment_ledd_Nm=Mledd)

# ------------------------------------------------------------------ CAD-kroppen i rommet
def rom(d, pl):
    """Frå lampa sitt system (mm) til rommet (m, ls.b): plassering (x, y, dreiing i grader om midt i foten)."""
    px, py, psi = pl; c, s_ = math.cos(math.radians(psi)), math.sin(math.radians(psi))
    Rz = np.array([[c, -s_, 0], [s_, c, 0], [0, 0, 1.0]])
    return lambda P: (np.asarray(P, float) / 1000) @ Rz.T + np.array([px, py, ZB]), Rz

def cad_lys(d, pl, W=1.0, film='ark', K=2700):
    """Lyset som lys_sjekk.lys(), med plassering og dreiing. Gjev (lys, kropp, c, n, s) i romkoordinatar."""
    T, Rz = rom(d, pl)
    s0, n0 = retning(d); s, n = Rz @ s0, Rz @ n0
    xm = 0.5 * (d['X_RUTE0'] + d['X_RUTE1'])
    c = T([xm, d['YB'], d['AKSE_H']]) + s * (d['U_KANT'] + d['RUTE_D'] / 2) / 1000
    lm = W * LMW_STRIPE * INN
    st = (d['RUTE_B'] / 1000, d['RUTE_D'] / 1000)
    Fo, Fn = ford(film), ford_ned()
    opp = rutemod.rute(c + n * 0.002, n, s, st, lm * OPP / Fo['verknad'], K, Fo, 'opp')
    ned = rutemod.rute(c - n * 0.002, -n, s, st, lm * NED / Fn['verknad'], K, Fn, 'ned')
    kc = T([xm, d['YB'], d['AKSE_H']]) + s * (d['U_KANT'] + d['RUTE_D']) / 1000
    kant = ls.flate(kc - n * 0.003, -n, (d['RUTE_B'] / 1000, 0.004), lm * KANT, K, opp=tuple(Rz @ np.array([1.0, 0, 0])))
    for l in (opp, ned): l.lm = 0.0
    kant.lm = W * LMW_STRIPE; kant.mater = True; kant.lm_ut = lm * KANT
    # kroppen som skuggar: bjelken, armen (fire stykke), knotten og foten
    kr = [ls.syl(T([d['X_BJ0'], d['YB'], d['AKSE_H']]), T([d['X_BJ1'], d['YB'], d['AKSE_H']]), d['R'] / 1000),
          ls.syl(T([d['X_LH1'], d['YB'], d['AKSE_H']]), T([d['X_KN0'] + d['KNOTT_L'], d['YB'], d['AKSE_H']]), d['KNOTT_D'] / 2000),
          ls.skive(T([0, 0, d['FOT_H']]), (0, 0, 1), d['FOT_D'] / 2000)]
    zs = np.linspace(d['Z_BOY'], d['AKSE_H'], 5)
    for z0, z1 in zip(zs[:-1], zs[1:]):
        kr.append(ls.syl(T([midtline(d, z0), d['YA'], z0]), T([midtline(d, z1), d['YA'], z1]), d['ARM_B'] / 2000))
    return [opp, ned, kant], kr, c, n, s

def pkt_ruta(d, pl, nu=12, nv=6):
    T, Rz = rom(d, pl); s, n = retning(d)
    return np.array([T(np.array([d['X_RUTE0'] + d['RUTE_B'] * (i + 0.5) / nu, d['YB'], d['AKSE_H']]) + 1000 * s * (d['U_KANT'] + d['RUTE_D'] * (j + 0.5) / nv) / 1000)
                     for i in range(nu) for j in range(nv)])

def plass_sjekk(d, pl):
    """Grensa: foten på feltet, kollisjon med skjerm, skjermfot, vegg og bord, ruta i siktlina (motor.py sine boksar)."""
    T, Rz = rom(d, pl); SK, SF = M.SKJ, M.SKJ_FOT
    zs = np.linspace(d['Z_BOY'], d['AKSE_H'], 30)
    Q = [pkt_ruta(d, pl, 30, 12), np.array([T([x, d['YB'], d['AKSE_H']]) for x in np.linspace(d['X_BJ0'], d['X_KN0'] + d['KNOTT_L'], 40)]),
         np.array([T([midtline(d, z), d['YA'], z]) for z in zs])]
    Q = np.vstack(Q) - np.array([0, 0, ZB])
    def inni(P, bx):
        x0, x1, y0, y1, z0, z1 = bx
        m = (P[:, 0] > x0) & (P[:, 0] < x1) & (P[:, 1] > y0) & (P[:, 1] < y1) & (P[:, 2] > z0) & (P[:, 2] < z1)
        if not m.any(): return 0.0
        R = P[m]; return float(np.min(np.stack([R[:, 0] - x0, x1 - R[:, 0], R[:, 1] - y0, y1 - R[:, 1], R[:, 2] - z0, z1 - R[:, 2]]), 0).max())
    kol = max(inni(Q, (-SK['x'], SK['x'], SK['y0'], SK['y1'], SK['z0'], SK['z1'])), float(np.max(Q[:, 1] - YV, initial=0)),
              float(max(-Q[:, 2].min(), 0)))
    r = d['FOT_D'] / 2000; fx, fy = T([0, 0, 0])[:2]
    g = np.mgrid[-1:1:60j, -1:1:60j].reshape(2, -1).T; g = g[(g ** 2).sum(1) <= 1] * r + [fx, fy]
    FE = M.FELT
    fpf = float(((g[:, 0] > FE[0]) & (g[:, 0] < FE[1]) & (g[:, 1] > FE[2]) & (g[:, 1] < FE[3])).mean())
    paa_skjfot = float(((np.abs(g[:, 0]) < SF['x']) & (g[:, 1] > SF['y0']) & (g[:, 1] < SF['y1'])).mean())
    utanfor = float(((np.abs(g[:, 0]) > 0.70) | (g[:, 1] < 0.0) | (g[:, 1] > YV)).mean())
    return dict(kollisjon_mm=kol * 1000, fot_pa_felt=fpf, fot_pa_skjermfot=paa_skjfot, fot_utanfor_bordet=utanfor,
                i_sikt=M.i_sikt(pkt_ruta(d, pl) - np.array([0, 0, ZB])), fot_xy=[float(fx), float(fy)])

# ------------------------------------------------------------------ same tal() på alle
FELT4, SKJ4, BAK4 = M.FELT4, M.SKJ4, M.BAK4
def under_ruta(lys, okkl, c, s):
    """lys_sjekk.py: bordet under og framfor ruta, 40 x 40 cm, direkte lys (snitt, høgst). s gjev retninga ruta peikar."""
    h = np.array([s[0], s[1], 0.0]); h = h / max(np.linalg.norm(h), 1e-9) if np.linalg.norm(h) > 0.2 else np.array([0, -1.0, 0])
    q = np.array([-h[1], h[0], 0.0])
    P = np.array([[c[0], c[1], ZB + 0.001] + a * q + bb * h for a in np.linspace(-0.2, 0.2, 9) for bb in np.linspace(-0.15, 0.25, 9)])
    E = ls.E_direkte(P, np.tile([0, 0, 1.0], (len(P), 1)), lys, okkl) @ ls.LUM
    return float(E.mean()), float(E.max())

def tal_grov(d, pl, film='ark'):
    """Søket: berre direkte lys, ved 1 W, fint gitter på feltet, skjermflata, auget utan skugge, og mekanikken."""
    lys, kr, c, n, s = cad_lys(d, pl, 1.0, film)
    okkl = ls.STATISK + kr + [l.prim for l in lys]; okkl_s = [p for p in okkl if p is not ls.SKJERM]
    P, N, (nx, na) = FELT4
    cel = (ls.E_direkte(P, N, lys, okkl) @ ls.LUM).reshape(nx, na, 4).mean(-1)
    P3, N3, _ = SKJ4
    Es = float((ls.E_direkte(P3, N3, lys, okkl_s) @ ls.LUM).mean())
    av = max(M.augevolum(l, np.array(l.pts)) for l in lys[:2])
    ur = under_ruta(lys, okkl, c, s)
    Ef = float(cel.mean())
    return dict(E_felt_1W=Ef, U0=float(cel.min() / max(Ef, 1e-9)), W350_dir=350.0 / max(Ef, 1e-9), E_skjerm_1W=Es,
                augevolum_1W=av, under_ruta_1W=ur[0], under_ruta_maks_1W=ur[1])

def tal_full(lys, kr):
    """ls.tal (grovt gitter med sprett, som A, B, C og D) og det fine gitteret (motor.tal_fin), same rekning."""
    T = ls.tal(lys, kr)
    okkl = ls.STATISK + list(kr) + [l.prim for l in lys]; okkl_s = [p for p in okkl if p is not ls.SKJERM]
    (Pb, Nb), (Pw, Nw), (Ps, Ns) = M._ls_punkt()
    Ed = lambda P, N, o: ls.E_direkte(P, N, lys, o) @ ls.LUM
    ei_f = T['E_felt'] - Ed(Pb, Nb, okkl).mean(); ei_b = T['E_bak'] - Ed(Pw, Nw, okkl).mean(); ei_s = T['E_skjerm'] - Ed(Ps, Ns, okkl_s).mean()
    P, N, (nx, na) = FELT4; cel = Ed(P, N, okkl).reshape(nx, na, 4).mean(-1) + ei_f
    P2, N2, _ = BAK4; P3, N3, _ = SKJ4
    T.update(E_felt_fin=float(cel.mean()), U0_fin=float(cel.min() / max(cel.mean(), 1e-9)), E_bak_fin=float(Ed(P2, N2, okkl).mean() + ei_b),
             E_skjerm_fin=float(Ed(P3, N3, okkl_s).mean() + ei_s))
    T['L_auge_maks'] = max(T['L_auge25'], T['L_auge47'], T['L_auge60'])
    return T

def cad_full(d, pl, W, film='ark', K=2700):
    lys, kr, c, n, s = cad_lys(d, pl, W, film, K)
    T = tal_full(lys, kr)
    okkl = ls.STATISK + kr + [l.prim for l in lys]
    T['under_ruta'], T['under_ruta_maks'] = under_ruta(lys, okkl, c, s)
    T['augevolum'] = max(M.augevolum(l, np.array(l.pts)) for l in lys[:2])
    sp = {}
    for l in lys[:2]:
        for k_, v in M.spegling(l, np.array(l.pts)).items(): sp[k_] = max(sp.get(k_, 0.0), v)
    T['spegling_blank'] = max(sp.values()) * 0.04
    T['lm'] = W * LMW_STRIPE * INN; T['K'] = K
    return {k_: v for k_, v in T.items() if not k_.startswith('_')}

# ------------------------------------------------------------------ kommandoane
def k_ford():
    t0 = time.time()
    for k_ in ('ideell', 'ark'):
        f = ford(k_); print(k_, 'verknad %.3f' % f['verknad'], flush=True)
    logg('ford (%.0f s): verknad ideelt %.3f, arket %.3f' % (time.time() - t0, ford('ideell')['verknad'], ford('ark')['verknad']))

def k_kalib():
    t0 = time.time()
    d = mal(CAD0)
    kj = json.load(open(KONTROLL, encoding='utf-8'))
    m = mek(d)
    print('masse %.0f g (kontroll %s), tyngdepunkt %s (kontroll %s)' % (m['masse_g'], kj['masse_g'], np.round(m['tyngdepunkt_mm'], 1), kj['tyngdepunkt']))
    print('veltevinkel %.1f (%.1f) venstre %.1f N (%.1f) framme %.1f N (%.1f) dytt topp %.1f N (%.1f)' % (
        m['veltevinkel'], kj['veltevinkel'], m['velt_venstre_N'], kj['velt_venstre_N'], m['velt_framme_N'], kj['velt_framme_N'],
        m['velt_dytt_topp_N'], kj['velt_dytt_topp_N']))
    print('motor.F_tipp: trykk på ruta %.1f N, dytt på knotten %.1f N, fot som trengst Ø %.0f mm; svikt knott %.2f mm, framkant %.2f mm (plata %.2f)' % (
        m['trykk_ruta_N'], m['dytt_knott_N'], m['fot_D_krav_mm'], m['svikt_knott_mm'], m['svikt_framkant_mm'], m['svikt_framkant_plate_mm']), flush=True)
    ut = dict(mek=m, kontroll={k_: kj[k_] for k_ in ('masse_g', 'tyngdepunkt', 'veltevinkel', 'velt_venstre_N', 'velt_framme_N', 'velt_dytt_topp_N')})
    # lyset som lys_sjekk.py: 2 W, helling 35, ideelt prisme (som lys_sjekk) og arket
    for film in ('ideell', 'ark'):
        T = cad_full(d, PLASS0, 2.0, film)
        g = tal_grov(d, PLASS0, film)
        ut['lys_' + film] = dict(full=T, grov=g)
        print('%s: under ruta %.0f / %.0f lx, feltet %.0f lx (fint %.0f, U0 %.2f), auge %.0f/%.0f/%.0f, ansikt %.0f, skjerm %.0f | direkte: felt %.0f lx' % (
            film, T['under_ruta'], T['under_ruta_maks'], T['E_felt'], T['E_felt_fin'], T['U0_fin'], T['L_auge25'], T['L_auge47'], T['L_auge60'],
            T['E_ansikt'], T['E_skjerm'], g['E_felt_1W'] * 2), flush=True)
    ut['plass'] = plass_sjekk(d, PLASS0)
    ut['lys_sjekk_md'] = dict(under_snitt=190, under_hogst=436, felt=57, auge=372, ansikt=13)
    lagre('kalib', ut)
    logg('kalib (%.0f s): masse %.0f g mot %d, tp %s mot %s; venstre %.1f mot %.1f N, dytt %.1f mot %.1f N; 2 W 35° ideelt: under %.0f mot 190 lx, felt %.0f mot 57 lx, auge %.0f mot 372' % (
        time.time() - t0, m['masse_g'], kj['masse_g'], np.round(m['tyngdepunkt_mm'], 1).tolist(), kj['tyngdepunkt'], m['velt_venstre_N'], kj['velt_venstre_N'],
        m['velt_dytt_topp_N'], kj['velt_dytt_topp_N'], ut['lys_ideell']['full']['under_ruta'], ut['lys_ideell']['full']['E_felt'], ut['lys_ideell']['full']['L_auge_maks']))

PLASSAR = {'teikna': (0.47, 0.30, 0.0),          # lys_sjekk.py
           'kant': (0.38, 0.30, 0.0),            # foten tangerer feltet
           'skjermhjorne': (0.38, 0.52, 0.0),    # ved sida av skjermen, bak feltet
           'side-inn': (0.40, 0.25, -90.0),      # ved sida av feltet, dreidd: ruta peikar inn over feltet
           'bak-skjerm': (0.00, 0.60, 0.0)}      # bak skjermen, mot veggen
def variant(**kw):
    p = dict(CAD0); p.update({k_: float(v) for k_, v in kw.items()}); return mal(p)

def k_sok():
    t0 = time.time(); rader = []
    for H in (260.0, 360.0, 460.0):
        for V in (0.0, 20.0, 35.0, 60.0, 80.0):
            for U in (150.0, 70.0, -80.0, -230.0):
                d = variant(AKSE_H=H, VINKEL=V, ARM_UT=U)
                m = mek(d)
                for pn, pl in PLASSAR.items():
                    g = tal_grov(d, pl); ps = plass_sjekk(d, pl)
                    r = dict(AKSE_H=H, VINKEL=V, ARM_UT=U, plass=pn, **g, **{k_: m[k_] for k_ in ('masse_g', 'veltevinkel', 'velt_venstre_N', 'velt_dytt_topp_N',
                             'trykk_ruta_N', 'dytt_knott_N', 'stab_ok', 'fot_D_krav_mm', 'svikt_knott_mm', 'svikt_framkant_mm')},
                             **{k_: ps[k_] for k_ in ('kollisjon_mm', 'fot_pa_felt', 'fot_pa_skjermfot', 'fot_utanfor_bordet', 'i_sikt')})
                    r['auge350'] = r['augevolum_1W'] * r['W350_dir']
                    r['skjerm350'] = r['E_skjerm_1W'] * r['W350_dir']
                    fl = []
                    if r['W350_dir'] > 7.5: fl.append('over 7,5 W')
                    if r['U0'] < 0.4: fl.append('ujamt')
                    if r['auge350'] > 1500: fl.append('blendar')
                    if not r['stab_ok']: fl.append('veltar')
                    if r['kollisjon_mm'] > 1: fl.append('kolliderer')
                    if r['fot_pa_felt'] > 0.005: fl.append('foten på feltet')
                    if r['fot_pa_skjermfot'] > 0.005 or r['fot_utanfor_bordet'] > 0.005: fl.append('foten står ikkje')
                    if r['masse_g'] > 1200: fl.append('F8')
                    if r['i_sikt'] > 0.005: fl.append('i siktlina')
                    r['flagg'] = '; '.join(fl) or '-'
                    rader.append(r)
        print('H %.0f ferdig (%.0f s)' % (H, time.time() - t0), flush=True)
    keys = list(rader[0].keys())
    with open(os.path.join(HER, 'sok.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, keys); w.writeheader()
        for r in rader: w.writerow({k_: (round(v, 3) if isinstance(v, float) else v) for k_, v in r.items()})
    ok = [r for r in rader if r['flagg'] == '-']
    print('heilt fri for flagg: %d av %d' % (len(ok), len(rader)))
    for krav in ('over 7,5 W', 'ujamt', 'blendar', 'veltar', 'kolliderer', 'foten på feltet', 'foten står ikkje', 'F8', 'i siktlina'):
        print('  %-18s %3d' % (krav, sum(krav in r['flagg'] for r in rader)))
    lysok = [r for r in rader if r['W350_dir'] <= 7.5 and r['U0'] >= 0.4 and r['auge350'] <= 1500]
    print('lyset held (W, U0, auge): %d; av dei står %d, og %d står utan kollisjon og fot på feltet' % (
        len(lysok), sum(r['stab_ok'] for r in lysok), sum(r['stab_ok'] and r['kollisjon_mm'] <= 1 and r['fot_pa_felt'] <= 0.005 for r in lysok)))
    best = sorted(rader, key=lambda r: r['W350_dir'])[:12]
    for r in best:
        print('%4.0f %3.0f %5.0f %-13s W350 %5.1f U0 %.2f auge %6.0f skj %4.0f | m %4.0f tipp %5.1f venstre %5.1f dytt %4.1f fotkrav %4.0f | %s' % (
            r['AKSE_H'], r['VINKEL'], r['ARM_UT'], r['plass'], r['W350_dir'], r['U0'], r['auge350'], r['skjerm350'], r['masse_g'], r['veltevinkel'],
            r['velt_venstre_N'], r['dytt_knott_N'], r['fot_D_krav_mm'], r['flagg']))
    logg('sok (%.0f s): %d variantar, %d utan flagg; lyset held i %d, av dei står %d' % (time.time() - t0, len(rader), len(ok), len(lysok), sum(r['stab_ok'] for r in lysok)))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    a = sys.argv[1:]
    {'ford': k_ford, 'kalib': k_kalib, 'sok': k_sok}[a[0]](*a[1:])
