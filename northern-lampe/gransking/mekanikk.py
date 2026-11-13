# -*- coding: utf-8 -*-
"""gransking/mekanikk.py · uavhengig kontroll av mekanikk og varme for (a) bru, (b) krok, (c) flak.

Les berre parametrar (dict og konstantar) frå motorane. All rekning her er eigen kode:
handformlar + ein liten 3D-rammeløysar (Euler-Bernoulli, 12 fridomsgrader per bjelke, med vridning GJ).
Ingen kall til felles.stabilitet, motor.tal, val.tube_arm eller liknande.

Køyr:  PYTHONIOENCODING=utf-8 python mekanikk.py      -> skriv ut tal + mekanikk_tal.json
Einingar: SI (m, kg, N, Pa) om ikkje anna står.
"""
import os, sys, math, json
import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
G = 9.81
E, NU, RHO, K_ALU = 70e9, 0.33, 2700.0, 200.0
GS = E / (2 * (1 + NU))                    # 26,3 GPa
FY = 250e6                                 # 6082-T6
SIG_T = FY / 2                             # SF 2
UT = {}                                    # alt som skal i json


def p(*a):
    print(*a, flush=True)


def tittel(s):
    p('\n' + '=' * 100 + '\n' + s + '\n' + '=' * 100)


# ----------------------------------------------------------------------------------------------
# 0. Parametrar (bokstavleg her; kontrollert mot motorane ved import, berre lesing)
# ----------------------------------------------------------------------------------------------
PA = dict(L=1.12, R=0.022, t=0.0012, beta=25.0, k=0.536, yp=0.18, hp=0.62, a=0.15, D_leg=0.020, t_leg=0.0015)
PB = dict(L=0.64, R=0.022, t=0.0012, beta=25.0, k=0.94, yp=0.25, hp=0.62, D_arm=0.023, t_arm=0.0015,
          y0=0.74, rf=0.10, z0=0.012, m_klemme=0.25)
PC = dict(L=0.60, b=0.25, yp=0.26, zp=0.64, t_pl=0.0015, lip=0.020, col_w=0.10, col_f=0.03, col_t=0.002,
          col_y=0.512, fot=(0.24, 0.30, 0.004), m_skjerm=4.0, p_skjerm=(0.0, 0.50, 0.20))
T_VRI, R_GREP = 0.08, 0.026                # form01/motor.py:16, :181
T_VIPP = 0.30                              # form03/motor.py:21
F_PUSH, F_GEST_B = 10.0, 3.0               # felles.py:35, form02/val.py:18
H_CONV, DT_MAX, LM_W = 10.0, 30.0, 100.0   # felles.py:33-34


def les_motorar():
    """Kontroller at dei bokstavlege parametrane over er dei motorane faktisk brukar. Les òg påstandane."""
    pst = {}
    try:
        sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form01')); sys.path.insert(0, os.path.join(ROOT, 'form02'))
        import importlib.util
        import val as V2
        M1 = V2.M1
        spec = importlib.util.spec_from_file_location('motor3', os.path.join(ROOT, 'form03', 'motor.py'))
        M3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(M3)
        avvik = []
        for k in ('L', 'R', 'beta', 'k', 'hp', 'D_leg', 't_leg'):
            if abs(M1.FINAL[k] - PA[k]) > 1e-12: avvik.append(('a', k, M1.FINAL[k], PA[k]))
        if abs(M1.FINAL['t_bow'] - PA['t']) > 1e-12: avvik.append(('a', 't_bow'))
        for k in ('L', 'R', 'beta', 'k', 'hp', 'yp'):
            if abs(V2.B_KROK[k] - PB[k]) > 1e-12: avvik.append(('b', k, V2.B_KROK[k], PB[k]))
        for k in ('L', 'b', 'yp', 'zp'):
            if abs(M3.FINAL[k] - PC[k]) > 1e-12: avvik.append(('c', k, M3.FINAL[k], PC[k]))
        for nm, v in (('T_PL', PC['t_pl']), ('LIP', PC['lip']), ('COL_W', PC['col_w']), ('COL_F', PC['col_f']), ('COL_T', PC['col_t']),
                      ('COL_Y', PC['col_y']), ('M_SKJERM', PC['m_skjerm']), ('T_FRIK', T_VIPP)):
            if abs(getattr(M3, nm) - v) > 1e-12: avvik.append(('c', nm))
        if tuple(M3.FOT) != PC['fot']: avvik.append(('c', 'FOT'))
        if abs(M1.T_DET - T_VRI) > 1e-12 or abs(V2.F_GEST - F_GEST_B) > 1e-12: avvik.append(('gest',))
        p('Parametrar kontrollerte mot motorane:', 'ingen avvik' if not avvik else avvik)
    except Exception as ex:                                           # motorane treng PIL/skimage; rekninga her gjer det ikkje
        p('Kunne ikkje importere motorane (', ex, '). Brukar dei bokstavlege parametrane.')
    try:
        t2 = json.load(open(os.path.join(ROOT, 'form02', 'tal.json'), encoding='utf-8'))
        kj = json.load(open(os.path.join(ROOT, 'konsept.json'), encoding='utf-8'))
        import csv
        t3 = next(csv.DictReader(open(os.path.join(ROOT, 'form03', 'tal.csv'), encoding='utf-8')))
        pst = dict(t2=t2, kj=kj, t3={k: (float(v) if v.replace('.', '', 1).replace('-', '', 1).isdigit() else v) for k, v in t3.items()})
        # (a): yp, hp og fotbreidd a kjem frå søket i tal_bru(15.0); a = fot_cm2 / (2·(L+0,032))
        a_les = t2['a']['fot_cm2'] / 1e4 / (PA['L'] + 0.032) / 2
        assert abs(t2['a']['yp'] - PA['yp']) < 1e-9 and abs(t2['a']['hp'] - PA['hp']) < 1e-9 and abs(a_les - PA['a']) < 1e-6
        assert abs(t2['b']['arm_D_mm'] / 1000 - PB['D_arm']) < 1e-6
    except Exception as ex:
        p('Kunne ikkje lese påstandsfilene:', ex)
    return pst


# ----------------------------------------------------------------------------------------------
# Tverrsnitt
# ----------------------------------------------------------------------------------------------
def ror(D, t):
    d = D - 2 * t
    A = math.pi / 4 * (D ** 2 - d ** 2)
    I = math.pi / 64 * (D ** 4 - d ** 4)
    return dict(A=A, I=I, J=2 * I, W=I / (D / 2), D=D)


def ror_med_spalte(D, t, beta_deg, n=20000):
    """Tynnvegga røyr med langsgåande spalte ±beta om retninga 'ned'. Ope tverrsnitt."""
    Rm = (D - t) / 2
    b = math.radians(beta_deg)
    th = np.linspace(b, 2 * math.pi - b, n)                    # vinkel frå spalteretninga
    dth = th[1] - th[0]
    dA = Rm * t * dth * np.ones(n); dA[0] *= .5; dA[-1] *= .5
    u = Rm * np.cos(th)                                         # langs spalteretninga
    v = Rm * np.sin(th)
    A = dA.sum(); uc = (u * dA).sum() / A
    I_tvers = ((u - uc) ** 2 * dA).sum()                        # bøying der spalta ligg i ytste fiber
    I_langs = (v ** 2 * dA).sum()
    s = (2 * math.pi - 2 * b) * Rm
    return dict(A=A, I_tvers=I_tvers, I_langs=I_langs, J=s * t ** 3 / 3, uc=uc, s=s)


def u_profil(w, f, t):
    """U-profil, ytre breidd w (steg), flenshøgd f (ytre), tjukn t. Returnerer svak/sterk akse, J = Σ b t³/3, kvelving."""
    A_s, A_f = w * t, (f - t) * t
    A = A_s + 2 * A_f
    c = (A_s * t / 2 + 2 * A_f * (t + (f - t) / 2)) / A        # tyngdepunkt frå ytterside steg
    I_svak = w * t ** 3 / 12 + A_s * (c - t / 2) ** 2 + 2 * (t * (f - t) ** 3 / 12 + A_f * (t + (f - t) / 2 - c) ** 2)
    I_sterk = t * w ** 3 / 12 + 2 * ((f - t) * t ** 3 / 12 + A_f * ((w - t) / 2) ** 2)
    h, b = w - t, f - t / 2                                    # senterliner
    J = (h + 2 * b) * t ** 3 / 3
    e = 3 * b ** 2 / (6 * b + h)                               # skjersenter bak steget (senterline)
    Cw = t * b ** 3 * h ** 2 / 12 * (3 * b + 2 * h) / (6 * b + h)
    return dict(A=A, c=c, I_svak=I_svak, I_sterk=I_sterk, J=J, e=e, Cw=Cw, a_kv=math.sqrt(E * Cw / (GS * J)))


def kasse(w, f, t):
    """Lukka rektangelrøyr w × f × t (Bredt)."""
    h, b = w - t, f - t
    J = 4 * (h * b) ** 2 * t / (2 * (h + b))
    I_svak = (w * f ** 3 - (w - 2 * t) * (f - 2 * t) ** 3) / 12
    return dict(A=2 * (h + b) * t, J=J, I_svak=I_svak)


# ----------------------------------------------------------------------------------------------
# 3D-rammeløysar
# ----------------------------------------------------------------------------------------------
class Ramme:
    def __init__(s):
        s.X, s.el = [], []

    def node(s, pt):
        s.X.append(np.array(pt, float)); return len(s.X) - 1

    def bjelke(s, i, j, EA, EIy, EIz, GJ, ref=(1.0, 0, 0)):
        """ref: retning for utbøyinga som EIy styrer (lokal z). EIz styrer utbøying normalt på ref."""
        s.el.append((i, j, EA, EIy, EIz, GJ, np.array(ref, float)))

    def stiv(s, i, j, ref=None):
        d = s.X[j] - s.X[i]
        if ref is None:
            ref = (1.0, 0, 0) if abs(d[0]) < 0.9 * np.linalg.norm(d) else (0, 1.0, 0)
        s.bjelke(i, j, 1e11, 1e8, 1e8, 1e8, ref)

    @staticmethod
    def _k(L, EA, EIy, EIz, GJ):
        k = np.zeros((12, 12))
        k[0, 0] = k[6, 6] = EA / L; k[0, 6] = -EA / L
        k[3, 3] = k[9, 9] = GJ / L; k[3, 9] = -GJ / L
        a, b, c, d = 12 * EIz / L ** 3, 6 * EIz / L ** 2, 4 * EIz / L, 2 * EIz / L          # v, θz
        k[1, 1] = a; k[1, 5] = b; k[1, 7] = -a; k[1, 11] = b
        k[5, 5] = c; k[5, 7] = -b; k[5, 11] = d
        k[7, 7] = a; k[7, 11] = -b; k[11, 11] = c
        a, b, c, d = 12 * EIy / L ** 3, 6 * EIy / L ** 2, 4 * EIy / L, 2 * EIy / L          # w, θy
        k[2, 2] = a; k[2, 4] = -b; k[2, 8] = -a; k[2, 10] = -b
        k[4, 4] = c; k[4, 8] = b; k[4, 10] = d
        k[8, 8] = a; k[8, 10] = b; k[10, 10] = c
        return k + np.triu(k, 1).T

    def _T(s, e):
        i, j, EA, EIy, EIz, GJ, ref = e
        d = s.X[j] - s.X[i]; L = np.linalg.norm(d); ex = d / L
        ey = np.cross(ref, ex); ey /= np.linalg.norm(ey); ez = np.cross(ex, ey)
        R = np.stack([ex, ey, ez])
        T = np.zeros((12, 12))
        for q in range(4):
            T[3 * q:3 * q + 3, 3 * q:3 * q + 3] = R
        return T, L

    def los(s, fast, last):
        """fast: {node: 'alle' | 'trans'}; last: {node: (Fx,Fy,Fz,Mx,My,Mz)}. Returnerer u (n,6), reaksjonar (n,6)."""
        n = len(s.X)
        K = np.zeros((6 * n, 6 * n))
        for e in s.el:
            T, L = s._T(e)
            kg = T.T @ s._k(L, *e[2:6]) @ T
            dof = np.r_[6 * e[0] + np.arange(6), 6 * e[1] + np.arange(6)]
            K[np.ix_(dof, dof)] += kg
        f = np.zeros(6 * n)
        for nd, v in last.items():
            f[6 * nd:6 * nd + 6] += np.array(v, float)
        lock = []
        for nd, hv in fast.items():
            lock += list(6 * nd + np.arange(6 if hv == 'alle' else 3))
        fri = np.setdiff1d(np.arange(6 * n), lock)
        u = np.zeros(6 * n)
        u[fri] = np.linalg.solve(K[np.ix_(fri, fri)], f[fri])
        r = K @ u - f
        return u.reshape(n, 6), r.reshape(n, 6)

    def snitt(s, u, idx):
        """Snittkrefter i lokal akse ved ende 1 på element idx: (N, Vy, Vz, T, My, Mz)."""
        e = s.el[idx]
        T, L = s._T(e)
        ug = np.r_[u[e[0]], u[e[1]]]
        return (s._k(L, *e[2:6]) @ (T @ ug))[:6]


def sjolvtest():
    """Tre kjende svar: utkragar, vridning, kvartsirkel lasta ut av planet (bøying + vridning kopla)."""
    EI, GJ, P, L = 400.0, 300.0, 3.0, 0.7
    r = Ramme(); n0 = r.node((0, 0, 0)); n1 = r.node((0, 0, L)); r.bjelke(n0, n1, 1e9, EI, EI, GJ)
    u, _ = r.los({n0: 'alle'}, {n1: (P, 0, 0, 0, 0, 2.0)})
    f1 = abs(u[n1, 0] / (P * L ** 3 / (3 * EI)) - 1); f2 = abs(u[n1, 5] / (2.0 * L / GJ) - 1)
    Rr = 0.5; r = Ramme(); ids = []
    for th in np.linspace(0, math.pi / 2, 201):
        ids.append(r.node((0, Rr * math.sin(th), Rr * (1 - math.cos(th)))))
    for i in range(200):
        r.bjelke(ids[i], ids[i + 1], 1e9, EI, EI, GJ)
    u, _ = r.los({ids[0]: 'alle'}, {ids[-1]: (P, 0, 0, 0, 0, 0)})
    fasit = P * Rr ** 3 / EI * math.pi / 4 + P * Rr ** 3 / GJ * (3 * math.pi / 4 - 2)
    f3 = abs(u[ids[-1], 0] / fasit - 1)
    p(f'Sjølvtest rammeløysar: utkragar {f1:.1e}, vridning {f2:.1e}, kvartsirkel ut av planet {f3:.1e} (relativ feil)')
    assert max(f1, f2) < 1e-9 and f3 < 1e-3


# ----------------------------------------------------------------------------------------------
# Stabilitet (eigen kode: moment om kvar kant i støttepolygonet)
# ----------------------------------------------------------------------------------------------
def tyngd(delar):
    m = sum(x for x, _ in delar)
    c = sum(x * np.array(q, float) for x, q in delar) / m
    return m, c


def kantar(poly):
    """poly (n,2) mot klokka. Gjev [(a3, e3, namn)]."""
    out = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        out.append((np.array([a[0], a[1], 0.0]), np.array([b[0] - a[0], b[1] - a[1], 0.0]) / np.linalg.norm(b - a)))
    return out


def tippvinklar(m, com, poly):
    res = []
    for a, e in kantar(poly):
        n_inn = np.array([-e[1], e[0], 0.0])                   # peikar inn for polygon mot klokka
        d = float(np.dot(com - a, n_inn))
        res.append((d, math.degrees(math.atan2(d, com[2]))))
    return res


def velt_faktor(m, com, poly, pkt, F):
    """Minste faktor λ slik at lasta λ·F i pkt lyftar lampa om ein kant. inf om lasta aldri veltar."""
    best = math.inf
    W = np.array([0, 0, -m * G])
    for a, e in kantar(poly):
        Mg = float(np.dot(np.cross(com - a, W), e))           # stabiliserande (forteikn definerer «inn»)
        Mf = float(np.dot(np.cross(np.array(pkt, float) - a, np.array(F, float)), e))
        if Mg * Mf < 0:
            best = min(best, -Mg / Mf)
    return best


# ==============================================================================================
def del1_masse_tipp(pst):
    tittel('1. MASSE, TYNGDEPUNKT, TIPP  (a) bru og (c) flak')
    # ---------- (a) ----------
    B = PA
    xe = B['L'] / 2 + 0.016
    rt = ror(2 * B['R'], B['t']); rl = ror(B['D_leg'], B['t_leg'])
    andel = 1 - B['k'] * B['beta'] / 180                      # spalta tek 2β av 360° over k·L
    m_ror_motor = RHO * math.pi * 2 * B['R'] * B['t'] * B['L'] * andel         # motoren brukar ytre omkrins
    m_ror = RHO * rt['A'] * B['L'] * andel                                      # eksakt ringareal
    L_bein = math.hypot(B['hp'] - B['D_leg'] / 2, B['a'])
    m_bein = RHO * rl['A'] * L_bein
    delar = [(m_ror, (0, B['yp'], B['hp'])), (0.10, (0, B['yp'], B['hp'])), (0.06, (B['L'] / 2 + 0.04, B['yp'], B['hp'])),
             (0.03, (-B['L'] / 2, B['yp'], B['hp']))]
    for sx in (-1, 1):
        for sy in (-1, 1):
            delar.append((m_bein, (sx * xe, B['yp'] + sy * B['a'] / 2, (B['hp'] + B['D_leg'] / 2) / 2)))
    m, com = tyngd(delar)
    poly = np.array([[-xe, B['yp'] - B['a']], [xe, B['yp'] - B['a']], [xe, B['yp'] + B['a']], [-xe, B['yp'] + B['a']]])
    tv = tippvinklar(m, com, poly)
    namn = ['fram (−y)', 'høgre (+x)', 'bak (+y)', 'venstre (−x)']
    p(f"(a) røyr {m_ror:.4f} kg (motor: {m_ror_motor:.4f}), 4 bein à {m_bein:.4f} kg (L {L_bein:.4f} m), LED 0,10 + grep 0,06 + nav 0,03")
    p(f"(a) masse {m:.4f} kg · tyngdepunkt x {com[0]:+.4f}, y {com[1]:.4f}, z {com[2]:.4f} m · del av massen i aksehøgd {100 * (m - 4 * m_bein) / m:.0f} %")
    for nm, (d, v) in zip(namn, tv):
        p(f"    kant {nm:13s} avstand {d * 1000:6.1f} mm  tippvinkel {v:5.2f}°")
    tipp_a = min(v for _, v in tv)
    Mres_y = m * G * min(tv[0][0], tv[2][0]); Mres_x = m * G * min(tv[1][0], tv[3][0])
    F_y_akse = Mres_y / B['hp']; F_x_akse = Mres_x / B['hp']
    p(f"(a) rettande moment om føtene: {Mres_y:.3f} N·m (fram/bak), {Mres_x:.3f} N·m (sidevegs)")
    p(f"(a) vassrett kraft i aksehøgd som lyftar føtene: {F_y_akse:.2f} N i y, {F_x_akse:.2f} N i x")
    for mu in (0.25, 0.4, 0.6):
        p(f"    glid ved μ {mu}: {mu * m * G:.2f} N")
    dh = math.hypot(tv[0][0], com[2]) - com[2]
    p(f"(a) arbeid for å velte framover (lyfte tyngdepunktet {dh * 1000:.1f} mm): {m * G * dh:.2f} J")
    if pst:
        c = pst['t2']['a']
        p(f"    PÅSTAND tal.json a: masse {c['masse_kg']:.4f}, tipp {c['tipp_deg']:.2f}°, F_tipp {c['F_tipp_N']:.3f} N, M_res {c['M_res_arb']:.3f} N·m")
    UT['a_stab'] = dict(masse=m, com=com.tolist(), tipp_deg=tipp_a, M_res_y=Mres_y, M_res_x=Mres_x, F_tipp_y=F_y_akse, F_tipp_x=F_x_akse,
                        E_velt_J=m * G * dh)
    A = dict(m=m, com=com, poly=poly, xe=xe, rt=rt, rl=rl, L_bein=L_bein, m_ror=m_ror)

    # ---------- (c) ----------
    C = PC
    U = u_profil(C['col_w'], C['col_f'], C['col_t'])
    za = C['zp'] + 0.02
    yb = C['col_y']; y_bak = yb + C['col_f']
    m_plate = RHO * C['t_pl'] * C['L'] * C['b']
    m_lepper = RHO * C['t_pl'] * C['lip'] * 2 * (C['L'] + C['b'])
    m_brett = m_plate + m_lepper + 0.15 + 0.08                # + LED/optikk 0,15 + nav 0,08 (motoren sine tillegg)
    L_soyle = za + C['col_f'] - C['fot'][2]                   # geometrien: frå foten til overkant arm
    L_arm = y_bak - C['col_f'] - (C['yp'] - 0.012)            # arm fram til søyla (utan overlapp)
    m_soyle, m_arm = RHO * U['A'] * L_soyle, RHO * U['A'] * L_arm
    m_fot = RHO * C['fot'][0] * C['fot'][1] * C['fot'][2] + 0.15
    Cp = np.array([0, C['yp'], C['zp']])
    delar = [(m_brett, Cp), (m_arm, (0, C['yp'] - 0.012 + L_arm / 2, za + C['col_f'] - U['c'])),
             (m_soyle, (0, y_bak - U['c'], C['fot'][2] + L_soyle / 2)), (m_fot, (0, y_bak - C['fot'][1] / 2, C['fot'][2] / 2))]
    m, com = tyngd(delar)
    poly = np.array([[-C['fot'][0] / 2, y_bak - C['fot'][1]], [C['fot'][0] / 2, y_bak - C['fot'][1]], [C['fot'][0] / 2, y_bak], [-C['fot'][0] / 2, y_bak]])
    p(f"\n(c) U-profil: A {U['A'] * 1e6:.0f} mm² (motor: {(C['col_w'] + 2 * C['col_f']) * C['col_t'] * 1e6:.0f}), brett {m_brett:.4f} kg (plate {m_plate:.3f}, lepper {m_lepper:.3f}), "
      f"søyle {m_soyle:.4f}, arm {m_arm:.4f}, fot {m_fot:.4f}")
    res_c = {}
    for lab, dl in (('aleine', delar), ('med skjerm 4 kg', delar + [(C['m_skjerm'], C['p_skjerm'])])):
        mm, cc = tyngd(dl)
        tv = tippvinklar(mm, cc, poly)
        p(f"(c) {lab}: masse {mm:.4f} kg · tyngdepunkt y {cc[1]:.4f}, z {cc[2]:.4f}")
        for nm, (d, v) in zip(namn, tv):
            p(f"    kant {nm:13s} avstand {d * 1000:6.1f} mm  tippvinkel {v:5.2f}°")
        res_c[lab] = dict(m=mm, com=cc, tv=tv)
    if pst:
        t3 = pst['t3']
        p(f"    PÅSTAND form03/tal.csv: masse {t3['masse_kg']}, tipp aleine {t3['tipp_aleine']}°, med skjerm {t3['tipp_deg']}°, "
          f"F_tipp aleine {t3['F_tipp_aleine']} N, med skjerm {t3['F_tipp_N']} N")
    UT['c_stab'] = {k: dict(masse=v['m'], com=v['com'].tolist(), tipp_deg=min(x[1] for x in v['tv']),
                            tipp_fram=v['tv'][0][1], tipp_side=v['tv'][1][1], tipp_bak=v['tv'][2][1]) for k, v in res_c.items()}
    # følsemd: optikk som lysleiarplate (PMMA 3 mm) i staden for 0,15 kg
    m_lgp = 1190 * C['L'] * C['b'] * 0.003
    dl2 = [(m_brett - 0.15 + m_lgp + 0.10, Cp)] + delar[1:]
    m2, c2 = tyngd(dl2); tv2 = tippvinklar(m2, c2, poly)
    p(f"(c) følsemd: PMMA-lysleiar 3 mm veg {m_lgp:.2f} kg (+0,10 LED/diffusor) mot 0,15 i motoren -> masse {m2:.2f} kg, tipp fram {tv2[0][1]:.1f}°, side {tv2[1][1]:.1f}°")
    UT['c_stab']['lgp'] = dict(m_lgp=m_lgp, masse=m2, tipp_fram=tv2[0][1], tipp_side=tv2[1][1])
    Cc = dict(m=m, com=com, poly=poly, U=U, za=za, y_bak=y_bak, L_arm=L_arm, L_soyle=L_soyle, m_brett=m_brett, m_arm=m_arm, m_soyle=m_soyle,
              m_fot=m_fot, delar=delar, Cp=Cp, res=res_c, m_brett_lgp=m_brett - 0.15 + m_lgp + 0.10, delar_lgp=dl2)
    return A, Cc


# ==============================================================================================
def del2a_bru(A, pst):
    tittel('2a. (a) BRU · A-bukkar under 10 N sidedytt og under vrimomentet')
    B = PA; xe = A['xe']; rt, rl = A['rt'], A['rl']
    sp = ror_med_spalte(2 * B['R'], B['t'], B['beta'])
    p(f"Bein Ø20×1,5: I {rl['I'] * 1e9:.3f}e-9 m⁴, EI {E * rl['I']:.1f} N·m² · røyr Ø44×1,2: I {rt['I'] * 1e8:.3f}e-8 m⁴")
    p(f"Røyr med spalte 2β = 50° (lyssona, {B['k'] * B['L']:.2f} m): I {sp['I_tvers'] * 1e8:.3f}e-8 (spalta i ytste fiber), "
      f"J ope {sp['J'] * 1e11:.2f}e-11 mot lukka {rt['J'] * 1e8:.2f}e-8 m⁴ (1/{rt['J'] / sp['J']:.0f})")
    # hand: motoren sin modell = bein som utkragar frå stivt nav; + bjelkeleddet (røyret er riegel i ei portalramme med ledda føter)
    h = B['hp'] - B['D_leg'] / 2
    d_bein_motor = (F_PUSH / 4) * math.hypot(B['hp'], B['a']) ** 3 / (3 * E * rl['I'])
    d_bein = (F_PUSH / 4) * A['L_bein'] ** 3 / (3 * E * rl['I'])
    d_riegel = F_PUSH * h ** 2 * (2 * xe) / (12 * E * rt['I'])
    p(f"Hand, 10 N i x: bein {d_bein * 1000:.3f} mm (motoren sin formel med L = hypot(hp, a): {d_bein_motor * 1000:.3f}) + riegel (røyret bøyer) {d_riegel * 1000:.3f} mm "
      f"= {(d_bein + d_riegel) * 1000:.3f} mm")

    def modell(spalte=True):
        r = Ramme(); ft = {}
        ap = {sx: r.node((sx * xe, B['yp'], B['hp'])) for sx in (-1, 1)}
        for sx in (-1, 1):
            for sy in (-1, 1):
                ft[(sx, sy)] = r.node((sx * xe, B['yp'] + sy * B['a'], B['D_leg'] / 2))
                r.bjelke(ft[(sx, sy)], ap[sx], E * rl['A'], E * rl['I'], E * rl['I'], GS * rl['J'], ref=(1, 0, 0))
        xs = [-xe, -B['k'] * B['L'] / 2, 0.0, B['k'] * B['L'] / 2, xe]
        ids = [ap[-1]] + [r.node((x, B['yp'], B['hp'])) for x in xs[1:-1]] + [ap[1]]
        for i in range(4):
            mid = spalte and i in (1, 2)
            EIv = E * (sp['I_tvers'] if mid else rt['I']); EIh = E * (sp['I_langs'] if mid else rt['I'])
            r.bjelke(ids[i], ids[i + 1], E * rt['A'], EIv, EIh, GS * (sp['J'] if mid else rt['J']), ref=(0, 0, 1))
        grep = r.node((xe + 0.029, B['yp'], B['hp'])); r.stiv(ap[1], grep)
        return r, ap, ft, ids, grep
    r, ap, ft, ids, grep = modell()
    fast = {n: 'trans' for n in ft.values()}
    u, _ = r.los(fast, {ap[1]: (F_PUSH, 0, 0, 0, 0, 0)})
    dx_fe = u[ap[1], 0]
    u2, _ = r.los(fast, {ids[2]: (F_PUSH, 0, 0, 0, 0, 0)})
    p(f"Ramme (ledda føter, stive nav): 10 N i x på høgre topp -> {dx_fe * 1000:.3f} mm · på midten av røyret -> {u2[ids[2], 0] * 1000:.3f} mm")
    if pst:
        p(f"    PÅSTAND svikt_mm (a): {pst['t2']['a']['svikt_mm']:.3f} mm ved 10 N")
    # spenning i bein og nav
    M_bein = F_PUSH / 4 * A['L_bein']; M_nav = F_PUSH * h / 2
    p(f"Spenning ved 10 N: bein M {M_bein:.2f} N·m -> {M_bein / rl['W'] / 1e6:.1f} MPa · navet må føre {M_nav:.2f} N·m (om y) kvar -> røyr {M_nav * B['R'] / sp['I_tvers'] / 1e6:.1f} MPa")
    # navslark: glidelager Ø24, lengd ~33 mm
    for kl in (0.05, 0.10):
        p(f"    slark i navet, diametral klaring {kl:.2f} mm over 33 mm lagerlengd: ±{kl / 33 * h * 1000:.1f} mm ved toppen (i tillegg til elastisk svikt)")
    # vrimoment om x på høgre nav
    u3, r3 = r.los(fast, {ap[1]: (0, 0, 0, T_VRI, 0, 0)})
    p(f"Vrimoment {T_VRI} N·m om x på høgre nav: rotasjon {math.degrees(u3[ap[1], 3]):.4f}°, størst utslag {np.abs(u3[:, :3]).max() * 1000:.4f} mm, "
      f"fotreaksjon ±{abs(r3[ft[(1, 1)], 2]):.3f} N (statisk fotlast ≈ {A['m'] * G / 4:.2f} N)")
    # vrimoment gjennom den opne lyssona (friksjon i venstre nav, grep til høgre)
    th = T_VRI / 2 * B['k'] * B['L'] / (GS * sp['J'])
    p(f"Vriding av det slissa røyret om halve momentet går til venstre nav: {math.degrees(th):.2f}° (lukka røyr: {math.degrees(T_VRI / 2 * B['k'] * B['L'] / (GS * rt['J'])):.4f}°)")
    # 10 N i y: fagverk, men lampa lyfter
    u4, r4 = r.los(fast, {ids[2]: (0, F_PUSH, 0, 0, 0, 0)})
    p(f"10 N i y midt på røyret (bukkane er fagverk i y–z): {abs(u4[ids[2], 1]) * 1000:.3f} mm. Men føtene lyfter ved {UT['a_stab']['F_tipp_y']:.2f} N: lastfallet finst ikkje.")
    # spreiing av beina under eigenvekt
    H = (A['m'] * G / 4) * B['a'] / h
    p(f"Eigenvekt: kvart bein skyv foten ut med {H:.2f} N; friksjon held berre om μ ≥ {H / (A['m'] * G / 4):.2f}. Toppen må vere momentstiv, elles sklir beina på glatt bord.")
    UT['a_svikt'] = dict(hand_bein=d_bein * 1000, hand_riegel=d_riegel * 1000, ramme_10N_x=dx_fe * 1000, motor=d_bein_motor * 1000,
                         M_nav=M_nav, sig_bein_MPa=M_bein / rl['W'] / 1e6, slark_005=0.05 / 33 * h * 1000, vriding_spalte_deg=math.degrees(th),
                         J_ope_over_lukka=sp['J'] / rt['J'])


# ==============================================================================================
def arm_b():
    """(b) Armbane i y–z, eiga oppbygging: loddrett frå klemma, kvartbøy r 0,10, vassrett fram, ned til navet."""
    B = PB
    H = B['hp'] + B['R'] + 0.015
    pts = [(B['y0'], z) for z in np.linspace(B['z0'], H - B['rf'], 41)]
    pts += [(B['y0'] - B['rf'] + B['rf'] * math.cos(t), H - B['rf'] + B['rf'] * math.sin(t)) for t in np.linspace(0, math.pi / 2, 41)[1:]]
    pts += [(y, H) for y in np.linspace(B['y0'] - B['rf'], B['yp'], 41)[1:]]
    n_tip = len(pts) - 1
    pts += [(B['yp'], z) for z in np.linspace(H, B['hp'] + 1.12 * B['R'], 4)[1:]]
    return np.array(pts), H, n_tip


def modell_b(D, GJ_fak=1.0):
    B = PB
    ar = ror(D, B['t_arm'])
    pts, H, n_tip = arm_b()
    r = Ramme()
    ids = [r.node((0, y, z)) for y, z in pts]
    for i in range(len(ids) - 1):
        r.bjelke(ids[i], ids[i + 1], E * ar['A'], E * ar['I'], E * ar['I'], GS * ar['J'] * GJ_fak, ref=(1, 0, 0))
    sen = r.node((0, B['yp'], B['hp'])); r.stiv(ids[-1], sen, ref=(1, 0, 0))
    grep = r.node((B['L'] / 2 + 0.015, B['yp'], B['hp'])); r.stiv(sen, grep, ref=(0, 0, 1))
    return r, ids, n_tip, sen, grep, ar, pts


def del2b_krok(pst):
    tittel('2b. (b) KROK · arm Ø23×1,5 med vridning (GJ) og med vekta av røyret; klemme')
    B = PB
    andel = 1 - B['k'] * B['beta'] / 180
    m_ror = RHO * ror(2 * B['R'], B['t'])['A'] * B['L'] * andel
    m_ror_motor = RHO * math.pi * 2 * B['R'] * B['t'] * B['L'] * andel
    m_hovud = m_ror_motor + 0.10 + 0.06 + 0.04                 # motoren sitt hovud (bruker same tillegg)
    res = {}
    for D in (0.023, 0.024, 0.025, 0.026):
        r, ids, n_tip, sen, grep, ar, pts = modell_b(D)
        L_arm = float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())
        m_arm = RHO * ar['A'] * L_arm
        fast = {ids[0]: 'alle'}
        tip = ids[n_tip]
        ux = r.los(fast, {tip: (F_GEST_B, 0, 0, 0, 0, 0)})[0][tip, 0]
        uy = r.los(fast, {tip: (0, F_GEST_B, 0, 0, 0, 0)})[0][tip, 1]
        # same med GJ = EI (dvs. motoren sin forenkling: heile momentet som bøying)
        rm = modell_b(D, GJ_fak=(E * ar['I']) / (GS * ar['J']))
        ux_m = rm[0].los({rm[1][0]: 'alle'}, {rm[1][rm[2]]: (F_GEST_B, 0, 0, 0, 0, 0)})[0][rm[1][rm[2]], 0]
        # 3 N i grepet (røyrenden, x = L/2 + 15 mm), tre retningar; utslag i grepet
        g = {}
        for nm, F in (('x', (F_GEST_B, 0, 0)), ('y', (0, F_GEST_B, 0)), ('z', (0, 0, -F_GEST_B))):
            u = r.los(fast, {grep: (*F, 0, 0, 0)})[0]
            g[nm] = float(np.linalg.norm(u[grep, :3]))
        # eigenvekt: hovud i sentrum + arm som nodelaster
        last = {sen: np.array([0, 0, -m_hovud * G, 0, 0, 0.0])}
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        for i, s_ in enumerate(seg):
            for nd in (ids[i], ids[i + 1]):
                last[nd] = last.get(nd, np.zeros(6)) + np.array([0, 0, -RHO * ar['A'] * s_ * G / 2, 0, 0, 0])
        uw, rw = r.los(fast, last)
        res[D] = dict(ux=ux * 1000, uy=uy * 1000, ux_motor=ux_m * 1000, grep=g, ned=-uw[sen, 2] * 1000, fram=-uw[sen, 1] * 1000,
                      stup_deg=math.degrees(uw[sen, 3]), m_arm=m_arm, L_arm=L_arm, Mx_stat=rw[ids[0], 3], Fz_stat=rw[ids[0], 2], ar=ar)
        p(f"Ø{D * 1000:.0f}×1,5: 3 N i armspissen: ut av planet {ux * 1000:.2f} mm (utan vridningsskilnad, GJ=EI: {ux_m * 1000:.2f}), i planet {uy * 1000:.2f} mm · "
          f"3 N i grepet: x {g['x'] * 1000:.2f}, y {g['y'] * 1000:.2f}, z {g['z'] * 1000:.2f} mm · eigenvekt: ned {-uw[sen, 2] * 1000:.2f} mm, stup {math.degrees(uw[sen, 3]):+.2f}° · arm {m_arm:.3f} kg")
    if pst:
        p(f"    PÅSTAND (b): svikt {pst['t2']['b']['svikt_mm']:.3f} mm (maks av i/ut av planet, 3 N i spissen), arm Ø{pst['t2']['b']['arm_D_mm']:.0f}, "
          f"σ {pst['t2']['b']['arm_sig_MPa']:.2f} MPa, M_klemme {pst['t2']['b']['M_klemme']:.3f} N·m, masse {pst['t2']['b']['masse_kg']:.4f} kg")
    r23 = res[0.023]
    p(f"Masse (b): hovud {m_hovud:.4f} (røyr eksakt {m_ror:.4f}, motor {m_ror_motor:.4f}) + arm {r23['m_arm']:.4f} + klemme 0,25 = {m_hovud + r23['m_arm'] + 0.25:.4f} kg")
    # hand: vridningsdelen i loddrett stykke (arm 0,49 m), stykkevis
    ar = r23['ar']; EI = E * ar['I']; GJ = GS * ar['J']
    Lv = (B['hp'] + B['R'] + 0.015 - B['rf']) - B['z0']; ay = B['y0'] - B['yp']
    hand = F_GEST_B * ((0.645 ** 3 - 0.10 ** 3) / 3 / EI + ay ** 2 * Lv / GJ + (ay - B['rf']) ** 3 / 3 / EI)
    p(f"Hand (utan bøyen): bøying loddrett + vridning loddrett (T = F·{ay:.2f}) + bøying vassrett = {hand * 1000:.2f} mm; GJ/EI = {GJ / EI:.3f}")
    # eigenfrekvens sidevegs (grovt): k = F/δ, m = hovud + 1/4 arm
    k_x = F_GEST_B / (r23['ux'] / 1000); f_x = math.sqrt(k_x / (m_hovud + 0.25 * r23['m_arm'])) / (2 * math.pi)
    p(f"Sidesving Ø23: k {k_x:.0f} N/m, masse i spissen {m_hovud + 0.25 * r23['m_arm']:.2f} kg -> ≈ {f_x:.1f} Hz")

    # ---- spenning og klemme: reaksjonar i innfestinga for lastkombinasjonar (Ø23) ----
    r, ids, n_tip, sen, grep, ar, pts = modell_b(0.023)
    fast = {ids[0]: 'alle'}
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    vekt = {sen: np.array([0, 0, -m_hovud * G, 0, 0, 0.0])}
    for i, s_ in enumerate(seg):
        for nd in (ids[i], ids[i + 1]):
            vekt[nd] = vekt.get(nd, np.zeros(6)) + np.array([0, 0, -RHO * ar['A'] * s_ * G / 2, 0, 0, 0])
    komb = {'eigenvekt': {}, '+10 N mot brukar (−y) i røyret': {sen: (0, -F_PUSH, 0, 0, 0, 0)}, '+10 N mot vegg (+y) i røyret': {sen: (0, F_PUSH, 0, 0, 0, 0)},
            '+10 N langs røyret (x)': {sen: (F_PUSH, 0, 0, 0, 0, 0)}, '+10 N i y i grepet': {grep: (0, -F_PUSH, 0, 0, 0, 0)},
            '+10 N ned i grepet': {grep: (0, 0, -F_PUSH, 0, 0, 0)}, '+3 N i y i grepet (éin finger)': {grep: (0, -F_GEST_B, 0, 0, 0, 0)}}
    p('\nInnfesting (b), reaksjon i klemma [N, N·m] og spenning i røyrfoten (Ø23×1,5):')
    kl = {}
    for nm, ek in komb.items():
        last = {k: v.copy() for k, v in vekt.items()}
        for nd, v in ek.items():
            last[nd] = last.get(nd, np.zeros(6)) + np.array(v, float)
        u, rr = r.los(fast, last)
        R0 = rr[ids[0]]
        Mb = math.hypot(R0[3], R0[4]); T = abs(R0[5])
        sig = Mb / ar['W']; tau = T / (2 * ar['W'])
        vm = math.sqrt(sig ** 2 + 3 * tau ** 2)
        kl[nm] = dict(Fz=R0[2], Mx=R0[3], My=R0[4], Mz=R0[5], vm=vm / 1e6)
        p(f"  {nm:32s} Fz {R0[2]:6.2f}  Mx {R0[3]:+6.2f}  My {R0[4]:+6.2f}  Mz {R0[5]:+6.2f}   σ_vM {vm / 1e6:5.1f} MPa (tillate {SIG_T / 1e6:.0f})")
    # klemkraft: topplate 80 × 50 mm (y 0,67–0,75, x ±0,025), skrue under ved y ≈ 0,72, bordkant bak y 0,75. Arm ved y 0,74.
    y_fr, y_bk, y_skr, bx = 0.67, 0.75, 0.72, 0.025
    V = -kl['eigenvekt']['Fz'] if kl['eigenvekt']['Fz'] < 0 else kl['eigenvekt']['Fz']
    V = abs(kl['eigenvekt']['Fz']) + PB['m_klemme'] * G
    M_fram = max(abs(kl[k]['Mx']) for k in kl if 'mot brukar' in k or 'y i grepet' in k)
    M_bak = abs(kl['+10 N mot vegg (+y) i røyret']['Mx'])
    M_side = max(abs(kl[k]['My']) for k in kl)
    M_vri = max(abs(kl[k]['Mz']) for k in kl)
    P_fram = max(0.0, (M_fram - V * (B['y0'] - y_fr)) / (y_skr - y_fr))
    P_bak = max(0.0, (M_bak - V * (y_bk - B['y0'])) / (y_bk - y_skr)) if kl['+10 N mot vegg (+y) i røyret']['Mx'] * kl['eigenvekt']['Mx'] < 0 else 0.0
    P_side = max(0.0, (M_side - V * bx) / bx)
    r_frik = 0.0245 + 0.0083                                   # midlare friksjonsradius topplate 50×80 + skruetallerken Ø25
    P_vri = {mu: M_vri / (mu * r_frik) for mu in (0.3, 0.5)}
    p(f"Klemme (10 N-dytt, SF 1): moment fram {M_fram:.2f} N·m -> P ≥ {P_fram:.0f} N · bak {M_bak:.2f} -> {P_bak:.0f} N · sidevegs {M_side:.2f} N·m over 50 mm plate -> {P_side:.0f} N · "
          f"vridning om loddrett {M_vri:.2f} N·m -> {P_vri[0.3]:.0f} N (μ 0,3) / {P_vri[0.5]:.0f} N (μ 0,5)")
    P_dim = 2 * max(P_fram, P_bak, P_side, P_vri[0.3])
    p(f"Klemkraft med SF 2: ≈ {P_dim:.0f} N. Flatetrykk på 40 cm²: {P_dim / 40e-4 / 1e6:.2f} MPa. Ein M6–M8-skrue for hand gjev 1–3 kN.")
    # røyret i ei 12 mm djup hylse: kraftpar
    d_h = 0.012
    p(f"Røyrfot i {d_h * 1000:.0f} mm djup hylse (tjukna på toppkjeften): kraftpar {M_fram / (2 / 3 * d_h):.0f} N; 0,05 mm klaring gjev {0.05 / 12 * 645:.1f} mm slark i hovudet. "
      f"Vridning {M_vri:.1f} N·m må takast av kile eller klemring (friksjon på Ø23: {M_vri / (0.3 * 0.0115):.0f} N radialt).")
    UT['b'] = dict({f'D{int(D * 1000)}': dict(ut_av_plan=v['ux'], i_plan=v['uy'], ut_av_plan_GJ_lik_EI=v['ux_motor'], grep=v['grep'], ned_eigenvekt=v['ned'],
                                              stup_deg=v['stup_deg'], m_arm=v['m_arm']) for D, v in res.items()},
                   klemme=dict(M_fram=M_fram, M_bak=M_bak, M_side=M_side, M_vri=M_vri, P_fram=P_fram, P_bak=P_bak, P_side=P_side, P_vri_mu03=P_vri[0.3], P_SF2=P_dim, V=V),
                   reaksjonar=kl, f_side_Hz=f_x, masse=m_hovud + r23['m_arm'] + 0.25)


# ==============================================================================================
def vek(alfa):
    return np.array([0.0, -math.cos(alfa), math.sin(alfa)]), np.array([0.0, -math.sin(alfa), -math.cos(alfa)])


def modell_c(Cc, tverrsnitt='U', kv_soyle=1.0, kv_arm=1.0, pkt=()):
    """Søyle (akse z) + arm (akse y) + stiv lenk ned til vippeaksen + stive lenker til lastpunkt på brettet."""
    C = PC; U = Cc['U']
    if tverrsnitt == 'U':
        EA, EIs, EIst, GJ = E * U['A'], E * U['I_svak'], E * U['I_sterk'], GS * U['J']
    else:
        ks = kasse(C['col_w'], C['col_f'], C['col_t'])
        EA, EIs, EIst, GJ = E * ks['A'], E * ks['I_svak'], E * U['I_sterk'] * 1.3, GS * ks['J']
    yc = Cc['y_bak'] - U['c']; zc = Cc['za'] + C['col_f'] - U['c']
    r = Ramme()
    zs = np.linspace(C['fot'][2], zc, 21)
    col = [r.node((0, yc, z)) for z in zs]
    for i in range(20):
        r.bjelke(col[i], col[i + 1], EA, EIs, EIst, GJ * kv_soyle, ref=(0, 1, 0))       # EIy = svak akse: utbøying fram/bak (y)
    ys = np.linspace(yc, C['yp'], 11)
    arm = [col[-1]] + [r.node((0, y, zc)) for y in ys[1:]]
    for i in range(10):
        r.bjelke(arm[i], arm[i + 1], EA, EIs, EIst, GJ * kv_arm, ref=(0, 0, 1))         # EIy = svak akse: utbøying loddrett (z)
    piv = r.node(tuple(Cc['Cp'])); r.stiv(arm[-1], piv, ref=(1, 0, 0))
    nd = []
    for q in pkt:
        n_ = r.node(tuple(q)); r.stiv(piv, n_); nd.append(n_)
    return r, col, arm, piv, nd


def del2c_flak(Cc, pst):
    tittel('2c. (c) FLAK · søyle + arm U 100×30×2: bøying, VRIDNING om søyla, statisk nedbøying, fotplate')
    C = PC; U = Cc['U']
    ks = kasse(C['col_w'], C['col_f'], C['col_t'])
    F_g = T_VIPP / (C['b'] / 2)
    p(f"U 100×30×2: A {U['A'] * 1e6:.0f} mm², c {U['c'] * 1000:.2f} mm, I svak {U['I_svak'] * 1e8:.3f}e-8, I sterk {U['I_sterk'] * 1e7:.3f}e-7 m⁴, "
      f"J = Σbt³/3 = {U['J'] * 1e10:.3f}e-10 m⁴ -> GJ {GS * U['J']:.2f} N·m² (EI svak {E * U['I_svak']:.0f} N·m²)")
    p(f"   kvelving: Cw {U['Cw'] * 1e11:.2f}e-11 m⁶, a = √(ECw/GJ) = {U['a_kv']:.3f} m, skjersenter {U['e'] * 1000:.1f} mm bak steget")
    p(f"   lukka kasse 100×30×2: J {ks['J'] * 1e7:.2f}e-7 m⁴ = {ks['J'] / U['J']:.0f} × U-profilen")
    if pst:
        t3 = pst['t3']
        p(f"    PÅSTAND form03: svikt {t3['svikt_mm']} mm = brett {t3['svikt_brett_mm']} + arm {t3['svikt_arm_mm']} + søyle {t3['svikt_soyle_mm']}; nedbøying {t3['nedboying_mm']} mm; F_g {F_g:.1f} N")
    Cp = Cc['Cp']; hb = C['b'] / 2
    f0, _ = vek(0.0)                       # arbeid: brettet vassrett
    fs, _ = vek(math.radians(-90))         # stemning: framkanten ned, bakkanten opp
    pk = dict(arb_midt=Cp + hb * f0, arb_hjorne=Cp + hb * f0 + [C['L'] / 2, 0, 0],
              stem_topp_midt=Cp - hb * fs, stem_topp_hjorne=Cp - hb * fs + [C['L'] / 2, 0, 0],
              ende_akse=Cp + [C['L'] / 2, 0, 0])
    Lc = Cc['za'] + C['col_f'] - U['c'] - C['fot'][2]; La = Cc['y_bak'] - U['c'] - C['yp']
    a = U['a_kv']
    kv_s = Lc / (Lc - a * math.tanh(Lc / a))                   # søyle: kvelving hindra i foten, fri i toppen
    kv_a = La / (La - a * math.tanh(La / a))                   # arm: kvelving hindra ved søyla, fri ved navet
    p(f"   søylelengd {Lc:.3f} m, armlengd {La:.3f} m · stivleiksauke frå hindra kvelving i éin ende: søyle ×{kv_s:.2f}, arm ×{kv_a:.2f} (øvre grense for stivleik)")
    fall = [('arbeid, 2,4 N ned midt på framkanten (motoren sitt fall)', 'arb_midt', (0, 0, -F_g)),
            ('arbeid, 2,4 N ned i hjørnet (x = 0,30)', 'arb_hjorne', (0, 0, -F_g)),
            ('stemning, 2,4 N mot brukar øvst, midt', 'stem_topp_midt', (0, -F_g, 0)),
            ('stemning, 2,4 N mot brukar øvst i hjørnet', 'stem_topp_hjorne', (0, -F_g, 0)),
            ('10 N sidevegs (x) på brettenden i aksehøgd', 'ende_akse', (F_PUSH, 0, 0))]
    res = {}
    p(f"\n   {'lastfall':58s} {'U, fri kvelving':>16s} {'U, hindra kvelv.':>17s} {'lukka kasse':>12s}   [mm i lastpunktet]")
    for nm, key, F in fall:
        rad = []
        for tv, kvs, kva in (('U', 1.0, 1.0), ('U', kv_s, kv_a), ('kasse', 1.0, 1.0)):
            r, col, arm, piv, nd = modell_c(Cc, tv, kvs, kva, pkt=[pk[key]])
            u, rr = r.los({col[0]: 'alle'}, {nd[0]: (*F, 0, 0, 0)})
            rad.append(float(np.linalg.norm(u[nd[0], :3])) * 1000)
            if tv == 'U' and kvs == 1.0:
                tw = math.degrees(u[col[-1], 5]); R0 = rr[col[0]]
        res[key] = dict(U=rad[0], U_kv=rad[1], kasse=rad[2], vriding_soyle_deg=tw, Mz_fot=R0[5], Mx_fot=R0[3], My_fot=R0[4])
        p(f"   {nm:58s} {rad[0]:16.2f} {rad[1]:17.2f} {rad[2]:12.3f}   (søyla vrir {tw:+.2f}°, M i foten x/y/z {R0[3]:+.2f}/{R0[4]:+.2f}/{R0[5]:+.2f} N·m)")
    # hand: vridning av søyla i stemning, hjørne
    T = F_g * C['L'] / 2
    th = T * Lc / (GS * U['J'])
    p(f"   Hand: T = {F_g:.1f}·0,30 = {T:.2f} N·m, θ = T·L/GJ = {math.degrees(th):.2f}°, hjørnet flyttar θ·0,30 = {th * 300:.1f} mm; med hindra kvelving {th * 300 / kv_s:.1f} mm")
    Ta = F_g * C['L'] / 2; tha = Ta * La / (GS * U['J'])
    p(f"   Hand: vridning av armen i arbeid, hjørne: θ = {math.degrees(tha):.2f}°, hjørnet {tha * 300:.1f} mm; med hindra kvelving {tha * 300 / kv_a:.1f} mm")
    # skjerspenning frå vridning (ope tverrsnitt: τ = T·t/J)
    tau = T * C['col_t'] / U['J']; tau10 = F_PUSH * (Cc['y_bak'] - U['c'] + U['e'] - C['yp']) * C['col_t'] / U['J']
    p(f"   Skjerspenning frå vridning: {tau / 1e6:.1f} MPa (gest i hjørnet), {tau10 / 1e6:.1f} MPa (10 N sidevegs); tillate τ = {SIG_T / math.sqrt(3) / 1e6:.0f} MPa")
    # eigenfrekvens for vridningssvinginga (brett + arm om søyleaksen)
    arm_y = Cc['y_bak'] - U['c'] + U['e'] - C['yp']
    Iz = Cc['m_brett'] * ((C['L'] ** 2 + C['b'] ** 2) / 12 + arm_y ** 2) + Cc['m_arm'] * arm_y ** 2 / 3
    for lab, kth in (('fri kvelving', GS * U['J'] / Lc), ('hindra kvelving i foten', GS * U['J'] / Lc * kv_s), ('lukka kasse', GS * ks['J'] / Lc)):
        p(f"   Vridningssving om søyla ({lab}): k {kth:.1f} N·m/rad, I {Iz:.3f} kg·m² -> {math.sqrt(kth / Iz) / (2 * math.pi):.1f} Hz")
    res['f_vri_Hz'] = [math.sqrt(GS * U['J'] / Lc / Iz) / (2 * math.pi), math.sqrt(GS * U['J'] / Lc * kv_s / Iz) / (2 * math.pi)]

    # statisk nedbøying frå brettvekta (+ armvekta)
    r, col, arm, piv, nd = modell_c(Cc, 'U')
    u, rr = r.los({col[0]: 'alle'}, {piv: (0, 0, -Cc['m_brett'] * G, 0, 0, 0)})
    ned_b = -u[piv, 2] * 1000
    last = {piv: np.array([0, 0, -Cc['m_brett'] * G, 0, 0, 0.0])}
    for i in range(10):
        for n_ in (arm[i], arm[i + 1]):
            last[n_] = last.get(n_, np.zeros(6)) + np.array([0, 0, -Cc['m_arm'] * G / 20, 0, 0, 0])
    u, rr = r.los({col[0]: 'alle'}, last)
    ned_ba = -u[piv, 2] * 1000; M0 = abs(rr[col[0], 3])
    hand = Cc['m_brett'] * G * (La ** 3 / 3 + La ** 2 * Lc) / (E * U['I_svak']) * 1000
    p(f"\n   Statisk: brettvekt {Cc['m_brett'] * G:.2f} N i aksen -> ned {ned_b:.3f} mm (hand {hand:.3f}); med armvekta {ned_ba:.3f} mm, fram {-u[piv, 1] * 1000:.3f} mm, "
      f"helling {math.degrees(u[piv, 3]) :+.3f}°. Moment i søylefoten {M0:.2f} N·m -> {M0 * (C['col_f'] - U['c']) / U['I_svak'] / 1e6:.1f} MPa")
    if Cc.get('m_brett_lgp'):
        u2, _ = r.los({col[0]: 'alle'}, {piv: (0, 0, -Cc['m_brett_lgp'] * G, 0, 0, 0)})
        p(f"   med PMMA-lysleiar ({Cc['m_brett_lgp']:.2f} kg brett): ned {-u2[piv, 2] * 1000:.2f} mm")

    # fotplata 4 mm som fjør: plate på stivt bord, lyfter bak søyla. 1D-bjelke, full platebreidd (stivaste tolking).
    def fotplate(M0, N, S=0.0, s_av=0.05):
        EIp = E * C['fot'][0] * C['fot'][2] ** 3 / 12
        w = RHO * C['fot'][0] * C['fot'][2] * G
        # M(0)=0 i nedslagspunktet: M0 − N·l − S·(l − s_av) − w·l²/2 = 0
        aa, bb, cc = w / 2, N + S, -(M0 + S * s_av)
        l = (-bb + math.sqrt(bb ** 2 - 4 * aa * cc)) / (2 * aa)
        if l < s_av: S_, l = 0.0, (-N + math.sqrt(N ** 2 + 2 * w * M0)) / w
        else: S_ = S
        th = (M0 * l - N * l ** 2 / 2 - S_ * (l - s_av) ** 2 / 2 - w * l ** 3 / 6) / EIp
        return l, th, EIp
    N_opp = (Cc['m_brett'] + Cc['m_arm'] + Cc['m_soyle']) * G
    y_toe = C['col_y']
    mo, co = tyngd(Cc['delar'][:3])
    M_stat = mo * G * (y_toe - co[1])                           # moment om søyletåa frå alt over foten
    dM = F_g * (Cp[2] + hb)                                     # gest i stemning, vassrett øvst
    p(f"\n   Fotplate 4 mm: EI {E * C['fot'][0] * C['fot'][2] ** 3 / 12:.0f} N·m² (full breidd 0,24 m) mot søyla {E * U['I_svak']:.0f} N·m². Moment i søylerota: statisk {M_stat:.2f} N·m, gest +{dM:.2f} N·m")
    for lab, S in (('utan skjerm', 0.0), ('med skjerm 39 N, 5 cm framfor søyla', C['m_skjerm'] * G)):
        l0, th0, _ = fotplate(M_stat, N_opp, S)
        l1, th1, _ = fotplate(M_stat + dM, N_opp, S)
        p(f"   {lab}: lyft lengd {l0 * 1000:.0f} mm, søyla hallar {th0 * 1000:.2f} mrad statisk (navet {th0 * La * 1000:.2f} mm ned, {th0 * Cp[2] * 1000:.2f} mm fram); "
          f"under gesten +{(th1 - th0) * 1000:.2f} mrad -> {(th1 - th0) * (Cp[2] + hb) * 1000:.2f} mm i fingeren (lyft lengd {l1 * 1000:.0f} av {(y_toe - (Cc['y_bak'] - C['fot'][1])) * 1000:.0f} mm)")
        res['fotplate_' + ('utan' if S == 0 else 'med')] = dict(theta_stat_mrad=th0 * 1000, nav_ned_mm=th0 * La * 1000, gest_mm=(th1 - th0) * (Cp[2] + hb) * 1000)
    sig_pl = (M_stat + F_PUSH * (Cp[2] + hb)) / (C['col_w'] * C['fot'][2] ** 2 / 6)
    p(f"   Spenning i fotplata ved søyla (100 mm breidd), statisk + 10 N øvst: {sig_pl / 1e6:.0f} MPa")
    # brettet sjølv: ope trau (plate + lepper), vridning om x når éin tek i hjørnet
    J_trau = (C['b'] + 2 * C['lip']) * C['t_pl'] ** 3 / 3
    th_b = T_VIPP * (C['L'] / 2 - 0.06) / (GS * J_trau)
    p(f"   Brettet som ope trau: J {J_trau * 1e10:.2f}e-10 m⁴; grep i hjørnet (0,3 N·m over 0,24 m til navet): {math.degrees(th_b):.2f}° -> {th_b * hb * 1000:.2f} mm i hjørnet (om optikken ikkje lukkar trauet)")
    res['brett_vri_mm'] = th_b * hb * 1000
    res.update(ned_brett=ned_b, ned_brett_arm=ned_ba, M_fot_stat=M0, kv_s=kv_s, kv_a=kv_a, J_U=U['J'], J_kasse=ks['J'], F_g=F_g)
    UT['c_svikt'] = res


# ==============================================================================================
def del5_gest(A, Cc):
    tittel('5. GESTKREFTER · velt med rett kraftretning')
    B = PA
    # (a) rein vri: kraftpar om x
    Mres = UT['a_stab']['M_res_y']
    p(f"(a) reint kraftpar {T_VRI} N·m om røyraksen: rettande moment {Mres:.3f} N·m -> faktor {Mres / T_VRI:.1f} (stemmer med grep_ratio)")
    F1 = T_VRI / R_GREP
    grep_x = B['L'] / 2 + 0.016 + 0.029
    for lab, pkt, F in ((f'éin finger øvst på grepet, {F1:.2f} N mot brukar', (grep_x, B['yp'], B['hp'] + R_GREP), (0, -F1, 0)),
                        (f'éin finger øvst på grepet, {F1:.2f} N mot vegg', (grep_x, B['yp'], B['hp'] + R_GREP), (0, F1, 0)),
                        (f'éin finger framme på grepet, {F1:.2f} N ned', (grep_x, B['yp'] - R_GREP, B['hp']), (0, 0, -F1)),
                        (f'éin finger framme på grepet, {F1:.2f} N opp', (grep_x, B['yp'] - R_GREP, B['hp']), (0, 0, F1)),
                        ('10 N dytt i y i aksehøgd', (0, B['yp'], B['hp']), (0, -10, 0)),
                        ('10 N dytt i x i aksehøgd', (0, B['yp'], B['hp']), (10, 0, 0))):
        lam = velt_faktor(A['m'], A['com'], A['poly'], pkt, F)
        p(f"    {lab:48s} tryggleik mot lyft {lam:6.2f}" + ('  <- LYFTER' if lam < 1 else ('  (< 2)' if lam < 2 else '')))
        UT.setdefault('a_gest', {})[lab] = lam
    # glid ved y-kraft i grepet: enden svingar om den andre bukken
    for mu in (0.3, 0.5, 0.8):
        N_h = A['m'] * G / 2 * (1 + 2 * A['com'][0] / (2 * A['xe']))
        p(f"    grepsenden glir (svingar om venstre bukk) ved μ {mu}: {mu * N_h * 2 * A['xe'] / (grep_x + A['xe']):.2f} N i y")
    # ubalanse i røyret mot haldemomentet 0,08
    m_led, r_led = 0.10, 0.018
    m_spalte = RHO * math.pi * 2 * B['R'] * B['t'] * B['L'] * B['k'] * B['beta'] / 180
    r_sp = B['R'] * math.sin(math.radians(B['beta'])) / math.radians(B['beta'])
    ub = (m_led * r_led + m_spalte * r_sp) * G
    p(f"(a)/(b) ubalanse om røyraksen: LED 0,10 kg på innerveggen (r 18 mm) + vekta som manglar i spalta ({m_spalte * 1000:.0f} g, r {r_sp * 1000:.0f} mm) = {ub:.3f} N·m "
      f"-> haldemoment {T_VRI} N·m gjev faktor {T_VRI / ub:.1f}. Fingerkraft i Ø52-grepet: {T_VRI / (2 * R_GREP):.1f} N per finger (to fingrar).")
    UT['vri'] = dict(ubalanse=ub, faktor=T_VRI / ub)

    # (c)
    C = PC; F_g = T_VIPP / (C['b'] / 2); Cp = Cc['Cp']; hb = C['b'] / 2
    p(f"\n(c) gestkraft F_g = {T_VIPP}/{hb} = {F_g:.1f} N, alltid normalt på brettet (i y–z-planet, aldri i x).")
    p(f"    Motoren: F_tipp = m·g·d_min/zp med d_min = 0,120 m (SIDEKANTEN, x) og arm zp = 0,64 m -> 4,997 N mot 2·F_g = 4,8 N.")
    rows = []
    for lab_m, dl in (('aleine', Cc['delar']), ('med skjerm', Cc['delar'] + [(C['m_skjerm'], C['p_skjerm'])]), ('aleine, PMMA-lysleiar', Cc['delar_lgp'])):
        mm, cc = tyngd(dl)
        verst = (math.inf, '')
        for al in np.radians(np.arange(-120, 101, 5)):
            f, nn = vek(al)
            for kant, sg in (('framkant', 1), ('bakkant', -1)):
                for x in (0.0, C['L'] / 2):
                    for ret in (1, -1):
                        lam = velt_faktor(mm, cc, Cc['poly'], Cp + sg * hb * f + [x, 0, 0], ret * F_g * nn)
                        if lam < verst[0]:
                            verst = (lam, f"α {math.degrees(al):+.0f}°, {kant}, x {x:.2f}, kraft {'med' if ret > 0 else 'mot'} lysnormalen")
        p(f"    {lab_m:24s} minste tryggleik mot lyft over heile vippebana: {verst[0]:.2f}  ({verst[1]})")
        rows.append((lab_m, verst[0], verst[1]))
        for lab, al, sg, ret in (('arbeid α 0°, framkant ned', 0, 1, 1), ('stemning α −90°, øvre kant mot brukar', -90, -1, -1),
                                 ('stemning α −90°, øvre kant mot vegg', -90, -1, 1), ('ansikt α +70°, framkant mot brukar', 70, 1, 1)):
            f, nn = vek(math.radians(al))
            pk = Cp + sg * hb * f
            lam = velt_faktor(mm, cc, Cc['poly'], pk, ret * F_g * nn)
            p(f"        {lab:40s} punkt y {pk[1]:.3f} z {pk[2]:.3f}  kraft ({(ret * F_g * nn)[1]:+.2f}, {(ret * F_g * nn)[2]:+.2f}) N  tryggleik {lam:6.2f}")
        lam10 = velt_faktor(mm, cc, Cc['poly'], Cp + [C['L'] / 2, 0, 0], (10, 0, 0))
        lam10y = velt_faktor(mm, cc, Cc['poly'], Cp, (0, -10, 0))
        p(f"        10 N dytt sidevegs i aksehøgd: {lam10:.2f} · 10 N mot brukar i aksehøgd: {lam10y:.2f}")
    UT['c_gest'] = {r_[0]: dict(tryggleik=r_[1], fall=r_[2]) for r_ in rows}
    # toleranse på friksjonsleddet
    mm, cc = tyngd(Cc['delar'])
    f, nn = vek(math.radians(-90))
    lam = velt_faktor(mm, cc, Cc['poly'], Cp - hb * f, -F_g * nn)
    p(f"    Friksjonsmoment som gjev tryggleik 2,0 utan skjerm: {T_VIPP * lam / 2:.3f} N·m (leddet er sett til {T_VIPP}; ±20 % toleranse -> {lam / 1.2:.2f})")
    # ubalanse i brettet: lepper og optikk ligg på lyssida av aksen
    m_pl = RHO * C['t_pl'] * C['L'] * C['b']; m_lp = RHO * C['t_pl'] * C['lip'] * 2 * (C['L'] + C['b'])
    e = (m_pl * (-C['t_pl'] / 2) + m_lp * C['lip'] / 2 + 0.15 * C['lip'] / 2) / (m_pl + m_lp + 0.15 + 0.08)
    ub = (m_pl + m_lp + 0.23) * G * e
    p(f"    Ubalanse i brettet (lepper + optikk 10 mm til lyssida): e {e * 1000:.1f} mm -> {ub:.3f} N·m i loddrett stilling; {T_VIPP} N·m held med faktor {T_VIPP / ub:.0f}")
    UT['vipp'] = dict(ubalanse=ub, T_SF2_utan_skjerm=T_VIPP * lam / 2)


# ==============================================================================================
def h_sylinder(D, dT, eps, Ta=298.0):
    """Fri konveksjon (Churchill–Chu, vassrett sylinder) + stråling."""
    Tf = Ta + dT / 2
    nu, al, k, Pr = 1.6e-5 * (Tf / 300) ** 1.7, 2.25e-5 * (Tf / 300) ** 1.7, 0.0263 * (Tf / 300) ** 0.8, 0.71
    Ra = G / Tf * dT * D ** 3 / (nu * al)
    Nu = (0.6 + 0.387 * Ra ** (1 / 6) / (1 + (0.559 / Pr) ** (9 / 16)) ** (8 / 27)) ** 2
    hr = eps * 5.67e-8 * ((Ta + dT) ** 2 + Ta ** 2) * (2 * Ta + dT)
    return Nu * k / D + hr, Nu * k / D, hr


def h_plate(Lk, dT, eps, opp=True, Ta=298.0):
    Tf = Ta + dT / 2
    nu, al, k = 1.6e-5 * (Tf / 300) ** 1.7, 2.25e-5 * (Tf / 300) ** 1.7, 0.0263 * (Tf / 300) ** 0.8
    Ra = G / Tf * dT * Lk ** 3 / (nu * al)
    Nu = (0.54 if opp else 0.27) * Ra ** 0.25
    hr = eps * 5.67e-8 * ((Ta + dT) ** 2 + Ta ** 2) * (2 * Ta + dT)
    return Nu * k / Lk + hr, Nu * k / Lk, hr


def finne(h, t, L, sider=1):
    m = math.sqrt(sider * h / (K_ALU * t))
    return math.tanh(m * L) / (m * L) if L > 0 else 1.0


def del4_varme(pst):
    tittel('4. VARME')
    kj = pst.get('kj', {}) if pst else {}
    R_STRIPE = 0.30                    # K·m/W frå LED-sperresjikt til alu-veggen (tape + kort + 120 LED/m à ~20 K/W): overslag
    ETA_STR = 0.31                     # 100 lm/W ÷ ~320 lm per optisk watt (2700 K, Ra 90): del av effekten som vert lys
    res = {}
    # ---- (a) og (b): røyr ----
    for key, B, eta_ut in (('a', PA, 0.674), ('b', PB, 0.674)):
        D = 2 * B['R']; Lz = B['k'] * B['L']; Le = (B['L'] - Lz) / 2
        Phi = kj[key]['Phi_lm'] if kj else (1255.0 if key == 'a' else 1311.0)
        P = Phi / LM_W
        A_motor = math.pi * D * B['L'] * (1 - B['k'] * B['beta'] / 180)
        A_krav = P / (H_CONV * DT_MAX)
        p(f"({key}) P {P:.2f} W · motor: A {A_motor * 1e4:.0f} cm², krav {A_krav * 1e4:.0f} cm² (h 10, ΔT 30) -> margin {A_motor / A_krav:.2f}"
          + (f"   [påstand {kj[key]['A_kjol_cm2']:.0f}/{kj[key]['A_krav_cm2']:.0f}]" if kj else ''))
        bue = (math.pi - math.radians(B['beta'])) * B['R']                   # frå LED-lina (motsett spalta) til spaltekanten
        for lab, eps in (('eloksert/lakka ε 0,85', 0.85), ('blank alu ε 0,10', 0.10)):
            for Pv, plab in ((P, 'all effekt som varme'), (P * (1 - ETA_STR * eta_ut), 'utan utstrålt lys')):
                dT = 15.0
                for _ in range(30):
                    h, hc, hr = h_sylinder(D, dT, eps)
                    A_eff = math.pi * D * Lz * (1 - B['beta'] / 180) * finne(h, B['t'], bue) + 2 * math.pi * D * Le * finne(h, B['t'], Le)
                    dT = Pv / (h * A_eff)
                Tj = 25 + dT + Pv / Lz * R_STRIPE
                p(f"    {lab:22s} {plab:22s}: h {h:.1f} (konv {hc:.1f} + strål {hr:.1f}) W/m²K · A_eff {A_eff * 1e4:.0f} cm² (endefinne η {finne(h, B['t'], Le):.2f}, "
                  f"rundt η {finne(h, B['t'], bue):.2f}) · ΔT røyr {dT:.1f} K · LED ≈ {Tj:.0f} °C ved 25 °C")
                res[f'{key}|{lab}|{plab}'] = dict(h=h, A_eff_cm2=A_eff * 1e4, dT=dT, T_led=Tj)
        h10 = H_CONV
        A_eff10 = math.pi * D * Lz * (1 - B['beta'] / 180) * finne(h10, B['t'], bue) + 2 * math.pi * D * Le * finne(h10, B['t'], Le)
        p(f"    med motoren sin h = 10: A_eff {A_eff10 * 1e4:.0f} cm² -> margin {A_eff10 / A_krav:.2f} (motor {A_motor / A_krav:.2f}); med h for blank alu (≈ 6): krav {P / (6.0 * DT_MAX) * 1e4:.0f} cm²")
        res[f'{key}|h10'] = dict(A_eff_cm2=A_eff10 * 1e4, margin=A_eff10 / A_krav, margin_motor=A_motor / A_krav)
    # ---- (c): brett ----
    C = PC
    Phi = kj['c']['Phi_lm'] if kj else 1281.6
    P = Phi / LM_W; A_krav = P / (H_CONV * DT_MAX)
    mL = math.sqrt(2 * H_CONV / (K_ALU * C['t_pl'])) * C['b'] / 2
    eta_m = math.tanh(mL) / mL
    p(f"\n(c) P {P:.2f} W · motoren: m·L = √(2h/kt)·b/2 = {mL:.4f}, η = tanh/mL = {eta_m:.4f}, A = 2·L·b·η = {2 * C['L'] * C['b'] * eta_m * 1e4:.0f} cm² (krav {A_krav * 1e4:.0f}) -> formelen er rett REKNA"
          + (f"   [påstand {kj['c']['A_kjol_cm2']:.0f}/{kj['c']['A_krav_cm2']:.0f}]" if kj else ''))
    p("    Føresetnader i formelen: (1) LED-ane ligg som éi line langs vippeaksen, (2) begge sider av plata er fri mot lufta. Lyssida er dekt av optikk, så (2) held ikkje.")
    eta1 = finne(H_CONV, C['t_pl'], C['b'] / 2, sider=1)
    A_rygg = C['L'] * C['b'] * eta1; A_lepp = 2 * (C['L'] + C['b']) * C['lip'] * 0.9
    p(f"    Berre ryggen kjøler (h 10): η {eta1:.3f} -> {A_rygg * 1e4:.0f} cm² + lepper utvendig ≈ {A_lepp * 1e4:.0f} cm² = {(A_rygg + A_lepp) * 1e4:.0f} cm² -> margin {(A_rygg + A_lepp) / A_krav:.1f} "
          f"(motor {2 * C['L'] * C['b'] * eta_m / A_krav:.1f}). LED jamt fordelt over plata (η ≈ 1): {(C['L'] * C['b'] + A_lepp) * 1e4:.0f} cm².")
    for lab, eps in (('eloksert/lakka ε 0,85', 0.85), ('blank alu ε 0,10', 0.10)):
        Pv = P * (1 - ETA_STR * 0.70)
        dT = 10.0
        for _ in range(30):
            h, hc, hr = h_plate(C['L'] * C['b'] / (2 * (C['L'] + C['b'])), dT, eps, opp=True)
            A_eff = C['L'] * C['b'] * finne(h, C['t_pl'], C['b'] / 2, 1) + A_lepp
            dT = Pv / (h * A_eff)
        Tj = 25 + dT + Pv / (2 * C['L']) * R_STRIPE
        p(f"    {lab:22s}: rygg opp, h {h:.1f} (konv {hc:.1f} + strål {hr:.1f}) · A_eff {A_eff * 1e4:.0f} cm² · ΔT plate {dT:.1f} K · LED ≈ {Tj:.0f} °C (kantlys, 2 × 0,6 m stripe)")
        res[f'c|{lab}'] = dict(h=h, A_eff_cm2=A_eff * 1e4, dT=dT, T_led=Tj)
    res['c|motor'] = dict(mL=mL, eta=eta_m, A_cm2=2 * C['L'] * C['b'] * eta_m * 1e4, A_rygg_cm2=(A_rygg + A_lepp) * 1e4, margin_rygg=(A_rygg + A_lepp) / A_krav)
    UT['varme'] = res


def main():
    pst = les_motorar()
    sjolvtest()
    A, Cc = del1_masse_tipp(pst)
    del2a_bru(A, pst)
    del2b_krok(pst)
    del2c_flak(Cc, pst)
    tittel('3. SPENNINGAR mot 125 MPa (6082-T6, SF 2): sjå linene «σ», «Spenning» og «σ_vM» over. Samandrag i mekanikk.md.')
    del4_varme(pst)
    del5_gest(A, Cc)

    def rein(o):
        if isinstance(o, dict): return {str(k): rein(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)): return [rein(v) for v in o]
        if isinstance(o, (np.floating, float)): return None if not math.isfinite(float(o)) else round(float(o), 5)
        if isinstance(o, np.ndarray): return rein(o.tolist())
        return o
    json.dump(rein(UT), open(os.path.join(HER, 'mekanikk_tal.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    p('\n-> mekanikk_tal.json')


if __name__ == '__main__':
    main()
