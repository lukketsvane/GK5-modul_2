# -*- coding: utf-8 -*-
"""
gen/motor.py  ·  form05 «Lysrute», generasjon 1: éin familiemotor for ruta som varmt vindauge  (13.11.2026)

Grep: ei rute som sjølv lyser (prismefilm framfor lysleiarplate eller dioder), og som er vindauge i stemning og tak i arbeid.
Motoren er rute/motor.py (luminanstabellane, Rute-klassen, watt og tal) utvida med identitet som parametrar:

  stotte   'klemme' (på høgre bordkant) · 'stolpe' (liten fot til venstre) · 'telt' (rund fot til høgre, bøygd arm)
           · 'fot' (plate under skjermfoten, stolpe bak skjermen, arm fram over skjermkanten)
  akse     'x' hengslet går langs skjermen · 'y' hengslet peikar mot brukaren (sidehengsel). Med akse y står normalen til
           ruta alltid vinkelrett på synslina, så den lysande sida kan aldri vende mot auget (rekna, sjå logg.md)
  mek      'dreie' eitt fast hengsel · 'to' to hengsel: hengslet til ruta sit på ein lenkearm som svingar om eit ledd
           (sirkelboge med pil 'bue') · 'glid' hengslet glir på ei skinne frå stemning til arbeid
  ruter    liste. Kvar rute: w (langs hengslet), h (ut frå hengslet), hengsel (x, y, h over bordet) i stemning,
           hengsel_a i arbeid (to/glid), vinkel (stemning, arbeid) i grader, fraa 'kant'|'midt', side (akse y: +1 hengsel
           til høgre). Vinkel 0 ligg og lyser ned. Akse x: 90 står og lyser mot brukaren, 180 lyser opp, −90 heng og lyser
           mot veggen. Akse y: 90 står og lyser inn over feltet. Kolonnen i brettet er stemningsstillinga:
           ståande · liggjande · skrå · delt (to ruter)
  rille    'vassrett' (langs hengslet) · 'loddrett' (ut frå hengslet) · 'kryss' (to ark, det øvste loddrett)
  kjelde   'kant' (kantlys i lysleiarplate, ANTAKING) · 'bak' (dioder bak arket i kvit boks, 25 mm)

  python -B motor.py kjede      kvifor ruta på fot gjev 128 W og Telt 3,71 W: éin endring om gongen
  python -B motor.py tal        same tal() på alle 18, grovt gitter (celler om lag 8 cm, arealsnitt) -> tal.csv, tal.json
  python -B motor.py brett      brett.png (4 × 4), velt_umogleg.png, formkritikk og pikselkalibrering mot gen01
Éin prosess om gongen, låg prioritet (rute/motor.py set IDLE ved import), kvar køyring under 6 min.
"""
import os, sys, math, json, csv, time, copy, importlib.util
HER = os.path.dirname(os.path.abspath(__file__))
F5 = os.path.dirname(HER)
NL = os.path.dirname(F5)
os.environ.setdefault('NUMBA_CACHE_DIR', os.path.join(F5, '.numba'))
sys.dont_write_bytecode = True

def _last(namn, fil):
    spec = importlib.util.spec_from_file_location(namn, fil)
    m = importlib.util.module_from_spec(spec); sys.modules[namn] = m; spec.loader.exec_module(m)
    return m

RM = _last('rutemotor', os.path.join(F5, 'rute', 'motor.py'))      # set låg prioritet, lastar film og tabellar
if NL not in sys.path: sys.path.insert(0, NL)
import felles as fe
import numpy as np
from PIL import Image

ls = RM.ls; b = RM.b; ZB = RM.ZB; YV = RM.YV; AUGE = RM.AUGE; nrm = RM.nrm
G = 9.81
LOGG = os.path.join(HER, 'logg.md')
TALJSON = os.path.join(HER, 'tal.json')

def logg(tekst):
    with open(LOGG, 'a', encoding='utf-8') as f:
        f.write('- ' + time.strftime('%H.%M') + ' ' + tekst + '\n')

def lagre(nokkel, verdi):
    d = json.load(open(TALJSON, encoding='utf-8')) if os.path.exists(TALJSON) else {}
    d[nokkel] = verdi
    json.dump(d, open(TALJSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=RM._j)

# ------------------------------------------------------------------ premissar (merkte)
ARK_L, ARK_K = 0.61, 0.35     # (F) konsept/vindauge/film/bevis.md: arket er om lag 35 × 61 cm ±20 %, rillene parallelt med kortsida
RILLE_LAG = {'vassrett': ['x'], 'loddrett': ['y'], 'kryss': ['x', 'y'], 'kryss-v': ['x', 'y'], 'ingen': []}
LEIAR_MAKS = 0.30             # ANTAKING: lengste veg i lysleiarplata før uttaket blir ujamt (rute/motor.py har 200 mm)
T_HENGSEL = 1.5               # ANTAKING: friksjonshengsel som held 1,5 N·m
M_KLEMME = 4.0                # ANTAKING: handskrudd klemme på 18 til 25 mm bordplate held 4 N·m
M_SKJERM = 3.5                # ANTAKING: skjermen står på plata til «fot» og er ballast (kg), ikkje med i massen til lampa
SKJ = dict(x=0.27, y0=0.45, y1=0.50, z0=0.10, z1=0.42)    # skjermen som boks (djupn 5 cm ANTAKING), h over bordet
RAD = {'kant': 0.020, 'bak': 0.008}                       # huset langs hengslet: Ø40 alu med LED-ar, eller stong Ø16
TJUKN = {'kant': 0.008, 'bak': 0.025}                     # rute: plate + filmar + ramme, eller boks med dioder

def masse_rute(kj, w, h):
    """(anslått) kant: PMMA 4 mm, to filmar, reflektor og ramme. bak: spreiar 2 mm, filmar, alu-bakplate 0,8 mm og veggar."""
    A, P = w * h, 2 * (w + h)
    if kj == 'kant':
        return A * (0.004 * 1190 + 0.0004 * 1380 + 0.2) + P * 0.05
    return A * (0.002 * 1190 + 0.0004 * 1380 + 0.0008 * 2700) + P * 0.025 * 0.0008 * 2700 * 2 + 0.05

# ------------------------------------------------------------------ geometri: posen til ruta langs gesten
def lerp(a, c, t): return a + (c - a) * t

def akse_v(spec):
    return np.array([1.0, 0, 0]) if spec['akse'] == 'x' else np.array([0.0, 1.0, 0])

def boge(spec, r):
    """To hengsel: hengslet til ruta går på ein sirkelboge om eit ledd. Gjev (ledd, radius, u, n, θs, θa)."""
    Hs, Ha = b(*r['hengsel']), b(*r['hengsel_a'])
    a = akse_v(spec)
    d = Ha - Hs; c = np.linalg.norm(d) / 2; u = d / (2 * c)
    n = nrm(np.cross(a, u))
    if n[2] < 0: n = -n
    s = min(r.get('bue', 0.05), 0.999 * c)
    R = (c * c + s * s) / (2 * s); O = (Hs + Ha) / 2 - n * (R - s)
    return O, R, u, n, math.atan2(R - s, -c), math.atan2(R - s, c)

def hengsel_t(spec, r, t):
    Hs = b(*r['hengsel'])
    if 'hengsel_a' not in r or spec['mek'] == 'dreie': return Hs
    Ha = b(*r['hengsel_a'])
    if spec['mek'] == 'glid': return Hs + (Ha - Hs) * t
    O, R, u, n, ts, ta = boge(spec, r)
    th = ts + (ta - ts) * t
    return O + R * (math.cos(th) * u + math.sin(th) * n)

def pose(spec, r, t):
    """(o, ex, ey, H): o hjørnet, ex langs hengslet, ey ut frå hengslet, ez = ex × ey er den lysande sida."""
    phi = math.radians(lerp(*r['vinkel'], t)); c, s = math.cos(phi), math.sin(phi)
    H = hengsel_t(spec, r, t)
    if spec['akse'] == 'x':
        ex = np.array([1.0, 0, 0]); ey = np.array([0.0, -c, s])
    else:
        sd = r.get('side', 1)
        ex = np.array([0.0, -sd, 0]); ey = np.array([-sd * c, 0.0, s])
    off = (RAD[spec['kjelde']] + 0.002) if r.get('fraa', 'kant') == 'kant' else -r['h'] / 2
    return H + off * ey - ex * r['w'] / 2, ex, ey, H

def rute_pkt(spec, r, t, nu=8, nv=5):
    o, ex, ey, H = pose(spec, r, t)
    return np.array([o + ex * r['w'] * i / (nu - 1) + ey * r['h'] * j / (nv - 1) for i in range(nu) for j in range(nv)])

def boks(o, u, v, n, d):
    """Plate med hjørne o, kantar u og v, tjukn d bakover langs −n. Gjev (V, F)."""
    P = [o, o + u, o + u + v, o + v]
    V = np.array(P + [p - n * d for p in P])
    F = [(0, 1, 2), (0, 2, 3), (4, 6, 5), (4, 7, 6), (0, 4, 5), (0, 5, 1), (1, 5, 6), (1, 6, 2), (2, 6, 7), (2, 7, 3), (3, 7, 4), (3, 4, 0)]
    return V, F

def skive_mesh(c, r, t, n=40):
    return fe.frustum(np.asarray(c, float), np.asarray(c, float) + np.array([0, 0, t]), r, r, n)

def desk(P): return np.asarray(P, float) - np.array([0, 0, ZB])

# ------------------------------------------------------------------ kroppen: støtte, mekanikk, masse
class Kropp:
    """Ein kropp frå spesifikasjonen. Stengene får tverrsnitt frå stivleikslova (svikt ≤ 2 mm samla under gestkrafta,
    felles.stong med stiv=True), ikkje frå ein minstediameter."""
    def __init__(s, spec):
        s.spec = spec; s.kj = spec['kjelde']; s.R = spec['ruter']
        s.m_ruter = [masse_rute(s.kj, r['w'], r['h']) for r in s.R]
        s.fot = dict(spec.get('fot', {}))
        s._sett_feste(); s._mekanikk()

    # hengselendane og festepunktet S der støtta møter ruta
    def _hus(s, t):
        """Huset langs kvart hengsel ved t: liste av (p0, p1)."""
        ut = {}
        for r in s.R:
            o, ex, ey, H = pose(s.spec, r, t)
            k = tuple(np.round(H, 4))
            p0, p1 = H - ex * (r['w'] / 2 + 0.015), H + ex * (r['w'] / 2 + 0.015)
            if k in ut:
                q0, q1 = ut[k]; pts = np.array([q0, q1, p0, p1]); a = akse_v(s.spec)
                ut[k] = (pts[np.argmin(pts @ a)], pts[np.argmax(pts @ a)])
            else:
                ut[k] = (p0, p1) if (p1 - p0) @ akse_v(s.spec) > 0 else (p1, p0)
        return list(ut.values())

    def _sett_feste(s):
        sp = s.spec; st = sp['stotte']
        hus = s._hus(0.0)
        if sp['mek'] == 'to':
            O = boge(sp, s.R[0])[0]
            p0, p1 = hus[0]
            xe = (p1 if st in ('klemme', 'telt') else p0)[0] if sp['akse'] == 'x' else O[0]
            s.ledd = np.array([xe if st != 'fot' else 0.0, O[1], O[2]]) if sp['akse'] == 'x' else O
            S = s.ledd.copy()
        elif sp['akse'] == 'x':
            p0, p1 = hus[0]
            S = p1.copy() if st in ('klemme', 'telt') else (p0.copy() if st == 'stolpe' else (p0 + p1) / 2)
        else:
            ends = [p1 for p0, p1 in hus]                      # bakre ende av kvart sidehengsel
            S = np.mean(ends, axis=0)
        if sp['mek'] == 'glid':
            s.skinne = (S.copy(), S + (b(*s.R[0]['hengsel_a']) - b(*s.R[0]['hengsel'])))
        s.S = S
        xa = np.concatenate([rute_pkt(sp, r, 1.0)[:, 0] for r in s.R] + [rute_pkt(sp, r, 0.0)[:, 0] for r in s.R])
        if st == 'klemme': s.base = np.array([0.66, S[1]])
        elif st == 'stolpe': s.base = np.array([min(S[0], xa.min()) - 0.06, S[1]])
        elif st == 'telt': s.base = np.array([max(S[0] + 0.05, xa.max() + 0.05, 0.44), S[1]])
        else: s.base = np.array([0.0, 0.62])

    def _kjede(s):
        """Stengene i støtta frå golvet til S, i bordkoordinatar: liste av (p0, p1, kva)."""
        st = s.spec['stotte']; S = desk(s.S); bx, by = s.base
        if st == 'klemme':
            top = np.array([bx, by, S[2] + 0.015])
            ch = [(np.array([bx, by, -0.05]), top, 'stolpe'), (np.array([bx, by, S[2]]), S, 'arm')]
        elif st == 'stolpe':
            tf = s.fot.get('t', 0.010)
            ch = [(np.array([bx, by, tf]), np.array([bx, by, S[2] + 0.015]), 'stolpe'), (np.array([bx, by, S[2]]), S, 'arm')]
        elif st == 'telt':
            tf = s.fot.get('t', 0.012); kne = np.array([bx, by, S[2] - 0.03])
            ch = [(np.array([bx, by, tf]), kne, 'stolpe'), (kne, S, 'arm')]
        else:
            top = np.array([0.0, 0.62, S[2]])
            ch = [(np.array([0.0, 0.62, 0.004]), top, 'stolpe'), (top, np.array([S[0], S[1], S[2]]), 'arm')]
        if s.spec['akse'] == 'y' and len(s.R) > 1:                      # tverrbjelke til kvart sidehengsel
            for p0, p1 in s._hus(0.0):
                ch.append((S, desk(p1), 'tverr'))
        return [(p0, p1, k) for p0, p1, k in ch if np.linalg.norm(p1 - p0) > 0.01]

    def _hengande(s, t):
        """Masse og tyngdepunkt (bordkoordinatar) for alt som heng i S: ruter og hus."""
        parts = []
        for r, m in zip(s.R, s.m_ruter):
            o, ex, ey, H = pose(s.spec, r, t)
            parts.append((m, desk(o + ex * r['w'] / 2 + ey * r['h'] / 2)))
        for p0, p1 in s._hus(t):
            L = np.linalg.norm(p1 - p0)
            mh = (0.49 * L + 0.08) if s.kj == 'kant' else 0.40 * L
            parts.append((mh, desk((p0 + p1) / 2)))
        return parts

    def _mekanikk(s):
        # haldemoment i hengslet og gestkrafta ved den frie kanten
        Th = 0.0
        for r, m in zip(s.R, s.m_ruter):
            arm = 0.0 if r.get('fraa', 'kant') == 'midt' else r['h'] / 2 + RAD[s.kj]
            Th = max(Th, 1.3 * m * G * arm)
        s.T_hold = Th
        hmax = max(r['h'] for r in s.R)
        s.F_gest = max(Th / (hmax + RAD[s.kj]), 2.0)
        # last på stengene: verste av stemning og arbeid
        hang = [s._hengande(0.0), s._hengande(1.0)]
        mh = sum(m for m, _ in hang[0])
        def lever(p):
            return max(np.linalg.norm((sum(m * c for m, c in h) / mh)[:2] - p[:2]) for h in hang)
        ch = s._kjede()
        extra = []                                                 # lenkearm (to) og skinne (glid)
        if s.spec['mek'] == 'to':
            O, R, *_ = boge(s.spec, s.R[0])
            extra.append(('lenke', R))
        if s.spec['mek'] == 'glid':
            extra.append(('skinne', np.linalg.norm(s.skinne[1] - s.skinne[0])))
        n = len(ch) + len(extra)
        gamal = fe.DELTA_MAX; fe.DELTA_MAX = 2.0 / n
        s.stenger = []; s.svikt = 0.0; s.d_maks = 0.0
        for p0, p1, k in ch:
            M0 = mh * G * lever(p0) if k == 'stolpe' else mh * G * max(lever(p1), 0.0)
            F = s.F_gest if k == 'stolpe' else mh * G
            V, Fc, m, c, d0, d1, dl = fe.stong(p0, p1, F, M0, stiv=True, F_gest=s.F_gest)
            s.stenger.append(dict(p0=p0, p1=p1, kva=k, V=V, F=Fc, m=m, c=c, d0=d0, d1=d1, r=(d0 + d1) / 4000))
            s.svikt += dl; s.d_maks = max(s.d_maks, d0)
        s.ekstra = {}
        for k, L in extra:
            p0 = np.zeros(3); p1 = np.array([L, 0, 0])
            V, Fc, m, c, d0, d1, dl = fe.stong(p0, p1, mh * G, mh * G * 0.05, stiv=True, F_gest=s.F_gest)
            s.ekstra[k] = dict(m=m, r=(d0 + d1) / 4000, L=L); s.svikt += dl; s.d_maks = max(s.d_maks, d0)
        fe.DELTA_MAX = gamal
        s.mh = mh

    # delar ved t: prims til lysrekninga, mesh til brettet, masse til stabiliteten
    def delar(s, t):
        sp = s.spec; kj = s.kj; D = []                        # (mesh (V, F) i bordkoordinatar, prim, masse, tyngdepunkt, er_klemme)
        for r, m in zip(s.R, s.m_ruter):
            o, ex, ey, H = pose(sp, r, t); ez = nrm(np.cross(ex, ey))
            V, F = boks(desk(o), ex * r['w'], ey * r['h'], ez, TJUKN[kj])
            pr = ls.Rekt(o - TJUKN[kj] * ez, ex * r['w'], ey * r['h'], rho=RM.SVARTK) if kj == 'bak' else None
            D.append(((V, F), pr, m, desk(o + ex * r['w'] / 2 + ey * r['h'] / 2), False))
        for p0, p1 in s._hus(t):
            L = np.linalg.norm(p1 - p0); mh = (0.49 * L + 0.08) if kj == 'kant' else 0.40 * L
            D.append((fe.frustum(desk(p0), desk(p1), RAD[kj], RAD[kj], 24), ls.Syl(p0, p1, RAD[kj], rho=RM.GRA), mh, desk((p0 + p1) / 2), False))
        for st in s.stenger:
            D.append(((st['V'], st['F']), ls.Syl(st['p0'] + [0, 0, ZB], st['p1'] + [0, 0, ZB], max(st['r'], 0.003), rho=RM.ALU), st['m'], st['c'], False))
        if 'lenke' in s.ekstra:
            H = hengsel_t(sp, s.R[0], t); H = np.array([s.ledd[0], H[1], H[2]]) if sp['akse'] == 'x' else H
            e = s.ekstra['lenke']
            D.append((fe.frustum(desk(s.ledd), desk(H), e['r'], e['r'], 12), ls.Syl(s.ledd, H, e['r']), e['m'], desk((s.ledd + H) / 2), False))
            D.append((fe.frustum(desk(s.ledd) - akse_v(sp) * 0.012, desk(s.ledd) + akse_v(sp) * 0.012, 0.016, 0.016, 16), None, 0.05, desk(s.ledd), False))
        if 'skinne' in s.ekstra:
            p0, p1 = s.skinne; e = s.ekstra['skinne']
            D.append((fe.frustum(desk(p0), desk(p1), e['r'], e['r'], 12), ls.Syl(p0, p1, e['r']), e['m'], desk((p0 + p1) / 2), False))
        st = sp['stotte']; bx, by = s.base
        if st in ('telt', 'stolpe'):
            r_, t_ = (s.fot.get('r', 0.12), s.fot.get('t', 0.012)) if st == 'telt' else (s.fot.get('r', 0.09), s.fot.get('t', 0.010))
            m = 7850 * math.pi * r_ * r_ * t_
            D.append((skive_mesh((bx, by, 0.0), r_, t_), ls.Syl(b(bx, by, 0.0), b(bx, by, t_), r_, rho=RM.BURG if st == 'telt' else RM.GRA), m, np.array([bx, by, t_ / 2]), False))
        elif st == 'fot':
            o = np.array([-0.13, 0.43, 0.0]); u = np.array([0.26, 0, 0]); v = np.array([0, 0.20, 0])
            V, F = boks(o + [0, 0, 0.004], u, v, np.array([0, 0, 1.0]), 0.004)
            D.append(((V, F), None, 7850 * 0.26 * 0.20 * 0.004, np.array([0.0, 0.53, 0.002]), False))
        else:                                                  # klemme: kjeft over og under bordplata, C-boge utanfor kanten
            for z0, dz in ((0.0, 0.012), (-0.045, 0.010)):
                V, F = boks(np.array([0.62, by - 0.03, z0 + dz]), np.array([0.08, 0, 0]), np.array([0, 0.06, 0]), np.array([0, 0, 1.0]), dz)
                D.append(((V, F), None, 0.12, np.array([0.66, by, z0 + dz / 2]), True))
            V, F = boks(np.array([0.70, by - 0.03, 0.012]), np.array([0.012, 0, 0]), np.array([0, 0.06, 0]), np.array([0, 0, 1.0]), 0.057)
            D.append(((V, F), None, 0.11, np.array([0.706, by, -0.016]), True))
        return D

    def kontakt(s):
        st = s.spec['stotte']; bx, by = s.base
        if st in ('telt', 'stolpe'):
            r_ = s.fot.get('r', 0.12 if st == 'telt' else 0.09); th = np.arange(32) / 32 * 2 * math.pi
            return [np.c_[bx + r_ * np.cos(th), by + r_ * np.sin(th)]]
        if st == 'fot':
            return [np.array([[-0.13, 0.43], [0.13, 0.43], [0.13, 0.63], [-0.13, 0.63]])]
        return [np.array([[0.62, by - 0.03], [0.70, by - 0.03], [0.70, by + 0.03], [0.62, by + 0.03]])]

    def prims(s, t):
        return [p for _, p, _, _, _ in s.delar(t) if p is not None]

    def mesh(s, t):
        return fe.merge([d[0] for d in s.delar(t)])

# ------------------------------------------------------------------ lyset
_MOTOR = {}
def motor(kj, ri):
    if (kj, ri) not in _MOTOR: _MOTOR[(kj, ri)] = RM.last_motor(kj, ri)
    return _MOTOR[(kj, ri)]

def lys_t(spec, kr, t):
    W, K = RM.watt_k(t)
    M = motor(spec['kjelde'], spec['rille'])
    A = sum(r['w'] * r['h'] for r in spec['ruter'])
    stripe = []
    q = spec.get('bakstripe', 0.0)
    if q > 0:                                       # stripe dioder på huset, vend mot veggen bak skjermen (som rute.py)
        H = hengsel_t(spec, spec['ruter'][0], t); sn = nrm(np.array([0.0, 1.0, -0.3]))
        L = max(np.linalg.norm(p1 - p0) for p0, p1 in kr._hus(t)) - 0.03
        fl = ls.flate(H + sn * (RAD[spec['kjelde']] + 0.004), sn, (L, 0.02), q * W * ls.LMW_KJELDE * 0.9, K, opp=(0, 0, 1))
        fl.lm_ut = fl.lm; fl.lm = q * W * ls.LMW_KJELDE; fl.mater = True
        stripe = [fl]; W = W * (1 - q)
    ruter = []
    for r in spec['ruter']:
        o, ex, ey, H = pose(spec, r, t)
        ruter.append(RM.Rute(o, ex, ey, r['w'], r['h'], M, W * r['w'] * r['h'] / A, K, spec.get('bak', 0.0), spec['namn']))
    return sum([x.lys() for x in ruter], []) + stripe, kr.prims(t), ruter

def _rutenett(x0, x1, nx, a0, a1, na, plan, k):
    """Arealsnitt: nx × na celler, 2 × 2 prøvepunkt i kvar. plan 'bord' (x, y), 'vegg' (x, z) ved y = k, 'skjerm' (x, z) ved y = k."""
    dx, da = (x1 - x0) / nx, (a1 - a0) / na
    P = []
    for i in range(nx):
        for j in range(na):
            for si in (-0.25, 0.25):
                for sj in (-0.25, 0.25):
                    x = x0 + (i + 0.5 + si) * dx; a = a0 + (j + 0.5 + sj) * da
                    P.append([x, a, ZB + 1e-4] if plan == 'bord' else [x, k, ZB + a])
    P = np.array(P); N = np.tile([0.0, 0, 1] if plan == 'bord' else [0.0, -1, 0], (len(P), 1))
    return P, N, (nx, na)

FELT8 = _rutenett(-0.30, 0.30, 8, 0.05, 0.45, 5, 'bord', 0)              # celler 7,5 × 8 cm
BAK8 = _rutenett(-0.35, 0.35, 9, 0.05, 0.65, 8, 'vegg', YV - 1e-4)       # 7,8 × 7,5 cm
SKJ8 = _rutenett(-0.27, 0.27, 7, 0.11, 0.42, 4, 'skjerm', 0.447)          # 7,7 × 7,8 cm

def _ls_punkt():
    R = ls.rom(); kb, kv = R.kart[0], R.kart[1]
    Pb = R.P[kb.sl].reshape(28, 14, 3)[8:20, 1:9].reshape(-1, 3); Nb = np.tile([0.0, 0, 1], (len(Pb), 1))
    Pv = R.P[kv.sl]; mb = (np.abs(Pv[:, 0]) < 0.35) & (Pv[:, 2] > ZB + 0.05) & (Pv[:, 2] < ZB + 0.65)
    Pw = Pv[mb]; Nw = np.tile([0.0, -1, 0], (len(Pw), 1))
    xs = np.linspace(-0.24, 0.24, 5); zs = ZB + np.linspace(0.14, 0.39, 3)
    Ps = np.array([[x, 0.447, z] for x in xs for z in zs]); Ns = np.tile([0.0, -1, 0], (len(Ps), 1))
    return (Pb, Nb), (Pw, Nw), (Ps, Ns)

def tal8(lys, prims):
    """ls.tal (same rom, same tal som A, B og C) pluss feltet, veggen bak skjermen og skjermflata som arealsnitt på
    celler om lag 8 cm. Det direkte lyset er rekna i cellene, det indirekte er snittet frå ls.tal (glatt)."""
    T = ls.tal(lys, prims)
    okkl = ls.STATISK + list(prims) + [l.prim for l in lys]
    okkl_s = [p for p in okkl if p is not ls.SKJERM]
    (Pb, Nb), (Pw, Nw), (Ps, Ns) = _ls_punkt()
    Ed = lambda P, N, o: ls.E_direkte(P, N, lys, o) @ ls.LUM
    ei_f = T['E_felt'] - Ed(Pb, Nb, okkl).mean()
    ei_b = T['E_bak'] - Ed(Pw, Nw, okkl).mean()
    ei_s = T['E_skjerm'] - Ed(Ps, Ns, okkl_s).mean()
    (P, N, (nx, na)) = FELT8
    c = Ed(P, N, okkl).reshape(nx, na, 4).mean(-1) + ei_f
    T['E_felt8'] = float(c.mean()); T['U8'] = float(c.min() / max(c.mean(), 1e-9)); T['felt8'] = c
    P, N, _ = BAK8; T['E_bak8'] = float(Ed(P, N, okkl).mean() + ei_b)
    P, N, _ = SKJ8; e = Ed(P, N, okkl_s); T['E_skjerm8'] = float(e.mean() + ei_s); T['E_skjerm8_maks'] = float(e.max() + ei_s)
    return T

def L_auge(T): return max(T['L_auge25'], T['L_lampe'], T['L_auge60'], T['L_flate'])

# ------------------------------------------------------------------ same tal() på alle
SIKT_E = AUGE

def i_sikt(P):
    """Del av punkta (verd) inne i synspyramiden frå auget til skjermen, eller i handsona over feltet (15 cm)."""
    E = SIKT_E; s = (P[:, 1] - E[1]) / (0.45 - E[1])
    zlo = E[2] + s * (ZB + SKJ['z0'] - E[2]); zhi = E[2] + s * (ZB + SKJ['z1'] - E[2])
    pyr = (s > 0.05) & (s < 1) & (np.abs(P[:, 0]) < 0.27 * s + 0.0 * (1 - s)) & (P[:, 2] > zlo) & (P[:, 2] < zhi)
    hand = (np.abs(P[:, 0]) < 0.30) & (P[:, 1] > 0.05) & (P[:, 1] < 0.45) & (P[:, 2] < ZB + 0.15) & (P[:, 2] > ZB)
    return pyr | hand

def kollisjon(P):
    """Djupaste punkt (mm) inne i skjermboksen, under bordplata eller bak veggen."""
    h = P[:, 2] - ZB
    inn = (np.abs(P[:, 0]) < SKJ['x']) & (P[:, 1] > SKJ['y0']) & (P[:, 1] < SKJ['y1']) & (h > SKJ['z0']) & (h < SKJ['z1'])
    d = 0.0
    if inn.any():
        Q = P[inn]; hq = Q[:, 2] - ZB
        dd = np.min(np.stack([SKJ['x'] - np.abs(Q[:, 0]), Q[:, 1] - SKJ['y0'], SKJ['y1'] - Q[:, 1], hq - SKJ['z0'], SKJ['z1'] - hq]), 0)
        d = max(d, float(dd.max()))
    d = max(d, float(np.max(ZB - P[:, 2], initial=0.0)), float(np.max(P[:, 1] - YV, initial=0.0)))
    return d * 1000

def ark_bitar(spec):
    """Kor mange ark (61 × 35 cm, rillene langs kortsida, F ±20 %) filmbitane krev, og kor mange bitar som ikkje får plass (skøyt)."""
    bit = []
    for r in spec['ruter']:
        for retn in RILLE_LAG[spec['rille']]:
            bit.append((r['w'], r['h']) if retn == 'x' else (r['h'], r['w']))     # (langs rillene, på tvers)
    ok = [p for p in bit if p[0] <= ARK_K + 1e-9 and p[1] <= ARK_L + 1e-9]
    ark = []
    for Lr, La in sorted(ok, key=lambda p: -p[1]):
        for i in range(len(ark)):
            if La <= ark[i] + 1e-9: ark[i] -= La; break
        else: ark.append(ARK_L - La)
    return len(ark), len(bit) - len(ok)

def tal(spec, n_gest=5, n_geo=13):
    t0 = time.time()
    kr = Kropp(spec)
    # --- lyset langs gesten (ls.tal), med 8 cm-gitter i endepunkta
    ts = np.linspace(0, 1, n_gest); TT = []; RU = {}
    for t in ts:
        lys, pr, ruter = lys_t(spec, kr, float(t))
        TT.append(tal8(lys, pr) if t in (0.0, 1.0) else ls.tal(lys, pr)); RU[float(t)] = ruter
    s, a = TT[0], TT[-1]
    f8 = 350.0 / max(a['E_felt8'], 1e-9); fl = 350.0 / max(a['E_felt'], 1e-9)
    La = lambda d: max(d['L_lampe'], d['L_flate'])
    Lv = np.array([L_auge(T) for T in TT]); Sv = np.array([T['E_skjerm'] for T in TT])
    spr = [1 - ls.likskap(TT[i]['_fordeling'], TT[i + 1]['_fordeling']) for i in range(len(TT) - 1)]
    av, _ = RM.augevolum(RU[1.0]); sp = RM.spegling(RU[1.0])
    # --- geometri langs gesten
    ins, kol, ang = 0.0, 0.0, 180.0
    for t in np.linspace(0, 1, n_geo):
        for r in spec['ruter']:
            P = rute_pkt(spec, r, float(t))
            ins = max(ins, float(i_sikt(P).mean())); kol = max(kol, kollisjon(P))
            o, ex, ey, H = pose(spec, r, float(t)); ez = nrm(np.cross(ex, ey)); c = o + ex * r['w'] / 2 + ey * r['h'] / 2
            gøymd = c[1] > SKJ['y0'] and c[2] < ZB + SKJ['z1'] and abs(c[0]) < SKJ['x']
            if not gøymd: ang = min(ang, math.degrees(math.acos(np.clip(ez @ nrm(AUGE - c), -1, 1))))
    # --- form: grense, masse, stabilitet, styrke
    V0, _ = kr.mesh(0.0); V1, _ = kr.mesh(1.0)
    D0 = kr.delar(0.0)
    kl = np.concatenate([d[0][0] for d in D0 if d[4]]) if any(d[4] for d in D0) else np.zeros((0, 3))
    def utanfor(V):
        V = V + np.array([0, 0, ZB])
        o = (V[:, 0] < -0.70) | (V[:, 0] > 0.70) | (V[:, 1] < 0) | (V[:, 1] > YV) | (V[:, 2] < ZB - 1e-3)
        return o
    ut_b = max(float(utanfor(V).mean()) for V in (V0, V1)) if spec['stotte'] != 'klemme' else \
        max(float((utanfor(V) & ~((V[:, 0] > 0.61) & (V[:, 2] > -0.06))).mean()) for V in (V0, V1))
    ist = max(float(i_sikt(V + np.array([0, 0, ZB])).mean()) for V in (V0, V1))
    stab = []
    for t in (0.0, 1.0):
        D = kr.delar(t); parts = [(d[2], d[3]) for d in D]
        if spec['stotte'] == 'fot': parts.append((M_SKJERM, np.array([0.0, 0.50, 0.20])))
        zg = max(desk(hengsel_t(spec, r, t))[2] for r in spec['ruter'])
        stab.append(fe.stabilitet(parts, kr.kontakt(), zg, kr.F_gest))
    st = min(stab, key=lambda x: x['tipp_deg'])
    masse = sum(d[2] for d in D0)
    M_kl = 0.0
    if spec['stotte'] == 'klemme':
        for t in (0.0, 1.0):
            D = kr.delar(t)
            M_kl = max(M_kl, sum(d[2] * G * abs(d[3][0] - 0.66) for d in D if not d[4]) + kr.F_gest * desk(kr.S)[2])
    A_rute = sum(r['w'] * r['h'] for r in spec['ruter'])
    if spec['kjelde'] == 'kant':
        A_kj = sum(2 * math.pi * RAD['kant'] * np.linalg.norm(p1 - p0) for p0, p1 in kr._hus(1.0))
    else:
        A_kj = sum(r['w'] * r['h'] + 2 * (r['w'] + r['h']) * TJUKN['bak'] for r in spec['ruter'])
    n_ark, skoyt = ark_bitar(spec)
    W350 = a['W'] * f8
    leiar = spec['kjelde'] == 'kant' and max(r['h'] for r in spec['ruter']) > LEIAR_MAKS
    # --- kamera langs rillene (husstil): minste vinkel mellom synslina og rilleretningane i stemning
    cam = fe.Cam(D=KAM_D); fv = nrm(np.array(cam.M[2]))
    kam = 90.0
    for r in spec['ruter']:
        o, ex, ey, H = pose(spec, r, 0.0)
        for retn in RILLE_LAG[spec['rille']]:
            v = ex if retn == 'x' else ey
            kam = min(kam, math.degrees(math.acos(min(1.0, abs(float(fv @ v))))))
    rad = dict(id=spec['id'], rad=spec['rad'], kol=spec['kol'], namn=spec['namn'], stotte=spec['stotte'], rute=spec['rutetype'],
               akse=spec['akse'], mek=spec['mek'], rille=spec['rille'], kjelde=spec['kjelde'],
               vinkel='/'.join('%g>%g' % tuple(r['vinkel']) for r in spec['ruter']),
               # form
               fot_cm2=st['fot_cm2'], hogd_cm=(max(V0[:, 2].max(), V1[:, 2].max())) * 100, ut_bord=ut_b, i_sikt=ist,
               sveip_sikt=ins, kollisjon_mm=kol, masse_kg=masse, tipp_deg=st['tipp_deg'], F_tipp_N=st['F_tipp_N'],
               F_gest_N=kr.F_gest, M_klemme_Nm=M_kl, T_hengsel_Nm=kr.T_hold, d_stong_mm=kr.d_maks, svikt_mm=kr.svikt,
               A_rute_cm2=A_rute * 1e4, n_ark=n_ark, skoyt=skoyt, A_kjol_cm2=A_kj * 1e4, A_krav_cm2=W350 / (10 * 30) * 1e4,
               kamera_rille_deg=kam,
               # lys i arbeid (350 lx på feltet, 8 cm arealsnitt)
               W350=W350, U0=a['U8'], W350_ls=a['W'] * fl, U0_ls=a['U'], felt_5W=a['E_felt8'],
               bak350=a['E_bak8'] * f8, skjerm350=a['E_skjerm8'] * f8, skjerm_del=a['E_skjerm8'] * f8 / 350.0,
               ansikt350=a['E_ansikt'] * f8, auge25=max(a['L_auge25'], a['L_flate']) * f8, auge47=La(a) * f8,
               auge60=max(a['L_auge60'], a['L_flate']) * f8, augevolum=av * f8, spegling_blank=max(sp.values()) * f8 * 0.04,
               # stemning (1,25 W) og gesten
               s_auge25=max(s['L_auge25'], s['L_flate']), s_auge47=La(s), s_auge60=max(s['L_auge60'], s['L_flate']),
               s_bak=s['E_bak8'], s_vegg=s['E_vegg'], s_felt=s['E_felt8'], s_skjerm=s['E_skjerm8'], s_ansikt=s['E_ansikt'],
               likskap=ls.likskap(s['_fordeling'], a['_fordeling']),
               gest_L_maks=float(Lv[1:-1].max()), gest_skjerm_maks=float(Sv[1:-1].max()),
               topp=float(Lv[1:-1].max() / max(Lv[0], Lv[-1], 1e-9)), sprang=float(max(spr)), min_vinkel_auge=ang,
               veg_auge=[round(float(x)) for x in Lv], veg_skjerm=[round(float(x)) for x in Sv])
    fl_ = []
    if rad['ut_bord'] > 0.005: fl_.append('utanfor bordet')
    if rad['i_sikt'] > 0.005: fl_.append('i siktlina')
    if rad['sveip_sikt'] > 0.05: fl_.append('sveipar gjennom siktet')
    if rad['kollisjon_mm'] > 1: fl_.append('kolliderer')
    if spec['stotte'] != 'klemme':
        if rad['tipp_deg'] < fe.TIP_MIN: fl_.append('veltar')
        elif rad['F_tipp_N'] < 2 * rad['F_gest_N']: fl_.append('gest veltar')
    elif M_kl > M_KLEMME: fl_.append('klemma held ikkje')
    if kr.T_hold > T_HENGSEL: fl_.append('hengslet held ikkje')
    if A_kj < W350 / 300: fl_.append('for varm')
    if skoyt: fl_.append('skøyt i filmen')
    if leiar: fl_.append('lysleiar over 30 cm')
    if W350 > 7.5: fl_.append('over 7,5 W')
    if rad['U0'] < 0.4: fl_.append('ujamt')
    am = max(rad['auge25'], rad['auge47'], rad['auge60'])
    if am > 3000: fl_.append('F1')
    elif am > 1500: fl_.append('F5')
    if rad['augevolum'] > 1500: fl_.append('augevolum over F5')
    if rad['bak350'] < 100: fl_.append('F6')
    if max(rad['s_auge25'], rad['s_auge47'], rad['s_auge60']) > 500: fl_.append('stemning blendar')
    if rad['gest_L_maks'] > 1500: fl_.append('blendar undervegs')
    if rad['gest_skjerm_maks'] > 1.5 * max(Sv[0], Sv[-1]) and rad['gest_skjerm_maks'] > 100: fl_.append('sveipar over skjermen')
    if rad['likskap'] > 0.9: fl_.append('dimmar')
    if rad['skjerm_del'] > 0.5: fl_.append('lys på skjermen')
    if kam < 15: fl_.append('kamera langs rillene')
    rad['kan_lagast'] = not (rad['kollisjon_mm'] > 1 or kr.T_hold > T_HENGSEL or A_kj < W350 / 300)
    rad['av_arket'] = (skoyt == 0 and n_ark <= 1)
    rad['flagg'] = '; '.join(fl_) or '-'
    rad['sekund'] = time.time() - t0
    return rad, kr

# ------------------------------------------------------------------ dei 18 kroppane
def R_(w, h, hengsel, vinkel, **kw):
    d = dict(w=w, h=h, hengsel=hengsel, vinkel=vinkel); d.update(kw); return d

def K_(i, rad, kol, namn, stotte, rutetype, akse, mek, rille, kjelde, ruter, **kw):
    d = dict(id=i, rad=rad, kol=kol, namn=namn, stotte=stotte, rutetype=rutetype, akse=akse, mek=mek, rille=rille,
             kjelde=kjelde, ruter=ruter, bak=0.0); d.update(kw); return d

T_ = RM.KROPPAR['T']; K0 = RM.KROPPAR['K']
KROPPAR = [
    # rad 1: klemme på høgre bordkant
    K_(1, 1, 1, 'klemme-side', 'klemme', 'ståande', 'y', 'dreie', 'vassrett', 'bak',
       [R_(0.34, 0.52, (0.30, 0.22, 0.50), (90, 0), side=1)], merk='sidehengsel: står ved feltet og lyser inn, legg seg ned'),
    K_(2, 1, 2, 'klemme-glid', 'klemme', 'liggjande', 'x', 'glid', 'loddrett', 'bak',
       [R_(0.50, 0.22, (0.0, 0.68, 0.60), (0, 0), hengsel_a=(0.0, 0.42, 0.50))], merk='ligg bak skjermkanten, glir fram over feltet'),
    K_(3, 1, 3, 'Klemme', 'klemme', 'skrå', 'x', 'dreie', K0['rille'], K0['kjelde'],
       [dict(K0['ruter'][0])], merk='biletet «Klemme» som i rute/motor.py: snur via veggen'),
    K_(4, 1, 4, 'klemme-delt', 'klemme', 'delt', 'x', 'dreie', 'kryss', 'kant',
       [R_(0.48, 0.24, (0.0, 0.48, 0.64), (-40, 0)), R_(0.48, 0.12, (0.0, 0.48, 0.64), (-100, -100))],
       merk='fast flik mot veggen bak skjermen, rute som fell ned over feltet'),
    # rad 2: stolpe på liten fot til venstre
    K_(5, 2, 1, 'stolpe-to', 'stolpe', 'ståande', 'x', 'to', 'loddrett', 'kant',
       [R_(0.46, 0.20, (0.0, 0.58, 0.72), (-90, 0), hengsel_a=(0.0, 0.38, 0.50), bue=0.06)],
       merk='heng bak skjermen og lyser på veggen, lenkearmen fører ruta fram'),
    K_(6, 2, 2, 'stolpe-bok', 'stolpe', 'liggjande', 'y', 'dreie', 'vassrett', 'bak',
       [R_(0.34, 0.46, (-0.24, 0.22, 0.50), (160, 0), side=-1)], merk='sidehengsel: takvindauge utanfor feltet, blad som snur inn'),
    K_(7, 2, 3, 'stolpe-skrå', 'stolpe', 'skrå', 'x', 'dreie', 'loddrett', 'bak',
       [R_(0.48, 0.18, (0.0, 0.40, 0.62), (-120, 0))], merk='lent bakover mot veggen, fell fram'),
    K_(8, 2, 4, 'stolpe-bok-delt', 'stolpe', 'delt', 'y', 'dreie', 'vassrett', 'kant',
       [R_(0.34, 0.30, (0.0, 0.22, 0.52), (70, 0), side=1), R_(0.34, 0.30, (0.0, 0.22, 0.52), (70, 0), side=-1)],
       merk='opa bok: éin LED-rygg midt over feltet, to blad som står i V og legg seg flatt'),
    # rad 3: telt (rund fot til høgre, bøygd arm)
    K_(9, 3, 1, 'telt-vindauge', 'telt', 'ståande', 'x', 'to', 'kryss', 'kant',
       [R_(0.50, 0.24, (0.0, 0.58, 0.50), (90, 0), hengsel_a=(0.0, 0.40, 0.50), bue=0.08)],
       merk='står bak skjermen som eit vindauge mot brukaren, lenkearmen legg ho fram'),
    K_(10, 3, 2, 'telt-ligg', 'telt', 'liggjande', 'x', 'dreie', 'loddrett', 'kant',
       [R_(0.48, 0.20, (0.0, 0.30, 0.56), (180, 360), fraa='midt')], merk='dreier om midtlina frå tak-opp til tak-ned via veggen'),
    K_(11, 3, 3, 'Telt', 'telt', 'skrå', 'x', 'dreie', T_['rille'], T_['kjelde'],
       [dict(T_['ruter'][0])], bakstripe=T_['bakstripe'], merk='biletet «Telt» som i rute/motor.py'),
    K_(12, 3, 4, 'telt-møne', 'telt', 'delt', 'x', 'dreie', 'kryss', 'kant',
       [R_(0.48, 0.20, (0.0, 0.40, 0.60), (225, 180)), R_(0.48, 0.20, (0.0, 0.40, 0.60), (-45, 0))],
       merk='to ruter frå ein møne: bakre lyser opp og mot veggen, fremre fell ned'),
    # rad 4: fot under skjermen
    K_(13, 4, 1, 'fot-over', 'fot', 'ståande', 'x', 'dreie', 'loddrett', 'bak',
       [R_(0.45, 0.19, (0.0, 0.50, 0.50), (-90, 10))], bakstripe=0.20, merk='ruta over skjermkanten frå konsept/film/01-ruta.md'),
    K_(14, 4, 2, 'fot-ligg-to', 'fot', 'liggjande', 'x', 'to', 'kryss', 'bak',
       [R_(0.48, 0.20, (0.0, 0.48, 0.74), (180, 360), hengsel_a=(0.0, 0.40, 0.50), bue=0.10)],
       merk='takvindauge høgt over skjermen, lenkearmen vender det ned via veggen'),
    K_(15, 4, 3, 'fot-skrå-glid', 'fot', 'skrå', 'x', 'glid', 'loddrett', 'kant',
       [R_(0.48, 0.16, (0.0, 0.52, 0.74), (-150, 0), hengsel_a=(0.0, 0.40, 0.50))], merk='lent mot veggen høgt, glir ned og fram'),
    K_(16, 4, 4, 'fot-skodde', 'fot', 'delt', 'y', 'dreie', 'vassrett', 'kant',
       [R_(0.34, 0.30, (0.30, 0.22, 0.52), (90, 0), side=1), R_(0.34, 0.30, (-0.30, 0.22, 0.52), (90, 0), side=-1)],
       merk='to skodder på sidehengsel: står og lyser inn mot kvarandre, legg seg saman til eitt tak'),
]
KONTROLL = [
    K_(17, 0, 1, 'veltar', 'telt', 'skrå', 'x', 'dreie', 'kryss', 'kant', [dict(T_['ruter'][0])], bakstripe=0.25,
       fot=dict(r=0.06, t=0.006), merk='Telt med fot Ø120 × 6 mm i staden for Ø240 × 12'),
    K_(18, 0, 2, 'umogleg', 'fot', 'skrå', 'x', 'dreie', 'kryss', 'kant',
       [R_(0.62, 0.30, (0.0, 0.47, 0.50), (125, 360))],
       merk='eitt hengsel over skjermkanten, vindauge til tak via veggen: ruta går gjennom skjermen'),
]
ALLE = KROPPAR + KONTROLL
KAM_D = 3.6          # same kamera for alle: el 17, fov 19, avstand 3,6 m (gen01 hadde 3,0; rutene er breiare)

# ------------------------------------------------------------------ kjede: 128 W mot 3,71 W
def _g_fast(ruter_def, kj, ri, kropp, q=0.0):
    M = motor(kj, ri)
    def g(t):
        W, K = RM.watt_k(t); lys = []
        if q > 0:
            sn = nrm(np.array([0.0, 1.0, -0.3])); H = b(0.0, 0.40, 0.50)
            fl = ls.flate(H + sn * 0.024, sn, (0.48, 0.02), q * W * ls.LMW_KJELDE * 0.9, K, opp=(0, 0, 1))
            fl.lm_ut = fl.lm; fl.lm = q * W * ls.LMW_KJELDE; fl.mater = True; lys.append(fl); W *= 1 - q
        A = sum(w * h for _, _, _, w, h in ruter_def)
        for o, ex, ey, w, h in ruter_def:
            lys += RM.Rute(o, ex, ey, w, h, M, W * w * h / A, K, 0.0, 'kjede').lys()
        return lys, kropp
    return g

def k_kjede():
    t0 = time.time()
    def flat(c, w, h, ned=True):
        ex = np.array([1.0, 0, 0]); ey = np.array([0.0, -1.0, 0]) if ned else np.array([0.0, 1.0, 0])
        return (c - ex * w / 2 - ey * h / 2, ex, ey, w, h)
    # pult som teikna (konsept/film/rute_sok.py): bjelke b(0,47, 0,36, 0,27) langs x, ruta 30 × 19 cm vippa 35° opp mot brukaren
    bj = b(0.47, 0.36, 0.27); e = np.array([0.0, -math.cos(math.radians(35)), -math.sin(math.radians(35))])
    ex =np.array([-1.0, 0, 0]); c = bj + e * 0.095
    pult = (c - ex * 0.15 - e * 0.095, ex, e, 0.30, 0.19)
    kr_pult = [ls.Rekt(c - nrm(np.cross(ex, e)) * 0.012 - ex * 0.15 - e * 0.095, ex * 0.30, e * 0.19), ls.syl(bj - np.array([0.15, 0, 0]), bj + np.array([0.15, 0, 0]), 0.012),
               ls.syl(b(0.47, 0.42, 0.0), bj, 0.008), ls.skive(b(0.47, 0.42, 0.004), (0, 0, 1), 0.10)]
    cp = c.copy()
    steg = [('pult som teikna (30 × 19, vippa 35° opp mot brukaren, x 0,47, 27 cm)', [pult], 'bak', 'vassrett', kr_pult, 0.0),
            ('same stad, snudd ned (0°)', [flat(cp, 0.30, 0.19)], 'bak', 'vassrett', kr_pult[1:], 0.0),
            ('flytt over feltet: x 0, y 0,28, 50 cm', [flat(b(0.0, 0.278, 0.50), 0.30, 0.19)], 'bak', 'vassrett', [], 0.0),
            ('storleik 48 × 20', [flat(b(0.0, 0.278, 0.50), 0.48, 0.20)], 'bak', 'vassrett', [], 0.0),
            ('rillene mot brukaren (loddrett)', [flat(b(0.0, 0.278, 0.50), 0.48, 0.20)], 'bak', 'loddrett', [], 0.0),
            ('to ark i kryss', [flat(b(0.0, 0.278, 0.50), 0.48, 0.20)], 'bak', 'kryss', [], 0.0),
            ('kantlys i lysleiarplate (× 0,72, ANTAKING)', [flat(b(0.0, 0.278, 0.50), 0.48, 0.20)], 'kant', 'kryss', [], 0.0),
            ('+ stripe mot veggen 25 %', [flat(b(0.0, 0.278, 0.50), 0.48, 0.20)], 'kant', 'kryss', [], 0.25)]
    ut = []
    for namn, rd, kj, ri, kr_, q in steg:
        g = _g_fast(rd, kj, ri, kr_, q)
        T = tal8(*g(1.0))
        W = T['W'] * 350 / T['E_felt']; W8 = T['W'] * 350 / T['E_felt8']
        d = dict(steg=namn, W350=round(W, 2), W350_8cm=round(W8, 2), felt_5W=round(T['E_felt'], 1), U0=round(T['U'], 2),
                 U0_8cm=round(T['U8'], 2), nytte=round(T['nytte'], 3), lm_ut=round(T['lm'], 0))
        ut.append(d); print(d, flush=True)
    # Telt-kroppen sjølv (rute/motor.py) som kontroll
    T = tal8(*RM.grep(T_)(1.0)); d = dict(steg='Telt frå rute/motor.py (kontroll)', W350=round(T['W'] * 350 / T['E_felt'], 2),
                                          W350_8cm=round(T['W'] * 350 / T['E_felt8'], 2), felt_5W=round(T['E_felt'], 1), U0=round(T['U'], 2), U0_8cm=round(T['U8'], 2))
    ut.append(d); print(d, flush=True)
    for i in range(1, len(ut) - 1):
        ut[i]['faktor_mot_forre'] = round(ut[i - 1]['W350'] / ut[i]['W350'], 2)
    lagre('kjede', ut)
    logg('kjede (%.0f s): %s' % (time.time() - t0, ' → '.join('%s W' % x['W350'] for x in ut)))

# ------------------------------------------------------------------ tal og brett
def k_tal(kva=None):
    t0 = time.time()
    rader = {}
    for spec in ALLE:
        if kva and str(spec['id']) not in kva.split(','): continue
        r, kr = tal(spec)
        rader[spec['id']] = r
        print('%2d %-16s W %5.2f U0 %.2f auge %5.0f/%5.0f/%5.0f bak %4.0f skj %4.0f | st %4.0f/%4.0f/%4.0f bak %3.0f lik %.2f | gest %5.0f cd %4.0f lx | tipp %5.1f m %.2f d %4.1f | %s (%.0f s)' % (
            r['id'], r['namn'], r['W350'], r['U0'], r['auge25'], r['auge47'], r['auge60'], r['bak350'], r['skjerm350'],
            r['s_auge25'], r['s_auge47'], r['s_auge60'], r['s_bak'], r['likskap'], r['gest_L_maks'], r['gest_skjerm_maks'],
            r['tipp_deg'], r['masse_kg'], r['d_stong_mm'], r['flagg'], r['sekund']), flush=True)
        if time.time() - t0 > 320: print('stoppar før 6 min'); break
    gamle = json.load(open(TALJSON, encoding='utf-8')).get('rader', {}) if os.path.exists(TALJSON) else {}
    gamle.update({str(k): v for k, v in rader.items()})
    lagre('rader', gamle)
    rows = [gamle[k] for k in sorted(gamle, key=int)]
    keys = [k for k in rows[0] if k not in ('veg_auge', 'veg_skjerm')]
    with open(os.path.join(HER, 'tal.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, keys + ['veg_auge', 'veg_skjerm']); w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 3) if isinstance(v, float) else (' '.join(map(str, v)) if isinstance(v, list) else v)) for k, v in r.items()})
    logg('tal (%.0f s): %d kroppar rekna, tal.csv skriven' % (time.time() - t0, len(rader)))

def pikselstat(path, n=None):
    im = np.asarray(Image.open(path).convert('RGB')).astype(float)
    H, W, _ = im.shape; n = n or (W // 512, H // 512)
    st = []
    for i in range(n[1]):
        for j in range(n[0]):
            tl = im[i * 512:(i + 1) * 512, j * 512:(j + 1) * 512]
            m = tl.max(-1) > 12
            if not m.any(): continue
            Y = tl[m] @ np.array([0.2126, 0.7152, 0.0722])
            st.append(dict(dekning=m.mean(), rgb=tl[m].mean(0), Y10=np.percentile(Y, 10), Y50=np.percentile(Y, 50), Y90=np.percentile(Y, 90)))
    return dict(fliser=len(st), dekning=float(np.mean([s['dekning'] for s in st])), rgb=[round(float(x), 1) for x in np.mean([s['rgb'] for s in st], 0)],
                Y10=float(np.mean([s['Y10'] for s in st])), Y50=float(np.mean([s['Y50'] for s in st])), Y90=float(np.mean([s['Y90'] for s in st])),
                bakgrunn=float((im.max(-1) <= 12).mean()))

def k_brett():
    t0 = time.time()
    cam = fe.Cam(D=KAM_D)
    ims, masks, ramme = {}, {}, {}
    for spec in ALLE:
        kr = Kropp(spec)
        V, F = kr.mesh(0.0)                      # stemning: ruta som vindauge
        V = V.copy(); c = (V[:, :2].min(0) + V[:, :2].max(0)) / 2; V[:, :2] -= c
        im, mk = fe.render(V, F, cam)
        ims[spec['id']], masks[spec['id']] = im, mk
        ys, xs = np.nonzero(mk); ramme[spec['id']] = (int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())) if len(xs) else None
        print(spec['id'], spec['namn'], ramme[spec['id']], flush=True)
    grid = {(s['rad'], s['kol']): s['id'] for s in KROPPAR}
    fe.brett(ims, grid, os.path.join(HER, 'brett.png'))
    fe.stripe([ims[17], ims[18]], os.path.join(HER, 'velt_umogleg.png'))
    fk = fe.formkritikk({k: masks[k] for k in grid.values()}, grid)
    # nabo-IoU per par, til logg
    par = []
    for (r, c), i in grid.items():
        for rr, cc in ((r, c + 1), (r + 1, c)):
            if (rr, cc) in grid:
                a_, b_ = masks[i], masks[grid[(rr, cc)]]
                par.append((i, grid[(rr, cc)], float((a_ & b_).sum() / max((a_ | b_).sum(), 1))))
    ref = pikselstat(os.path.join(NL, 'gen01', 'brett.png')); mi = pikselstat(os.path.join(HER, 'brett.png'))
    klipt = [i for i, r in ramme.items() if r and (r[0] <= 1 or r[2] <= 1 or r[1] >= 510 or r[3] >= 510)]
    ut = dict(iou_snitt=fk['iou_snitt'], iou_maks=fk['iou_maks'], iou_par=par, luft={str(k): v for k, v in fk['luft'].items()},
              pikselstat_gen01=ref, pikselstat_gen=mi, klipt_av_ramma=klipt, kamera=dict(el=17, az=240, fov=19, D=KAM_D, tilstand='stemning (t = 0)'))
    lagre('brett', ut)
    print(json.dumps({k: v for k, v in ut.items() if k != 'iou_par'}, ensure_ascii=False, default=RM._j), flush=True)
    logg('brett (%.0f s): nabo-IoU snitt %.2f, maks %.2f; klipt av ramma: %s' % (time.time() - t0, fk['iou_snitt'], fk['iou_maks'], klipt or 'ingen'))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit()
    {'kjede': k_kjede, 'tal': lambda: k_tal(a[1] if len(a) > 1 else None), 'brett': k_brett}[a[0]]()
