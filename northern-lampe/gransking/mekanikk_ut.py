# -*- coding: utf-8 -*-
"""gransking/mekanikk_ut.py · utviding av mekanikk.py (som rekna det gamle (c) flak):
  1 (a) bru: dytt i grephøgd, fingergest, billegaste retting
  2 (b) krok: armen med vridning (einingslast-integral, uavhengig av rammeløysaren), Ø for 2 mm, klemme og bordplate
  3 (c) PRISME (form04): masse, tyngdepunkt, tipp, fottjukn, svikt i arm og søyle med vridning av open U, hovudet sjølv
  4 varme i røyr og renne: LED-temperatur og trygg effekt per meter
  5 gestar: vri 0,08 N·m (a/b), vipp 0,2–0,3 N·m (c)

Eigen kode frå grunnformlane. Frå mekanikk.py (eigen kode frå den avbrotne granskinga) vert berre hjelparar brukte:
Ramme (3D-bjelke med GJ), ror, u_profil, kasse, tyngd, tippvinklar, velt_faktor, h_sylinder, finne.
Ingen kall til felles.py, form01/motor.py, form02/val.py eller form04/motor.py. Parametrane er skrivne inn bokstavleg.
Køyr: PYTHONIOENCODING=utf-8 python mekanikk_ut.py   (under 10 s)
"""
import os, sys, math, json
import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
import mekanikk as MK
from mekanikk import Ramme, ror, u_profil, kasse, tyngd, tippvinklar, velt_faktor, h_sylinder, finne, G, E, GS, RHO

UT = {}
RHO_ST, RHO_PMMA, E_PMMA = 7850.0, 1190.0, 3.0e9


def p(*a):
    print(*a, flush=True)


def tittel(s):
    p('\n' + '=' * 100 + '\n' + s + '\n' + '=' * 100)


def rekt(x0, x1, y0, y1):
    return np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])


# ==============================================================================================
# 1. (a) BRU
# ==============================================================================================
PA = MK.PA                              # L 1,12 · R 0,022 · t 1,2 · β 25 · k 0,536 · yp 0,18 · hp 0,62 · a 0,15 · bein Ø20×1,5
T_VRI, R_GREP = 0.08, 0.026


def a_delar(ekstra=()):
    B = PA
    xe = B['L'] / 2 + 0.016
    rt, rl = ror(2 * B['R'], B['t']), ror(B['D_leg'], B['t_leg'])
    m_ror = RHO * rt['A'] * B['L'] * (1 - B['k'] * B['beta'] / 180)
    Lb = math.hypot(B['hp'] - B['D_leg'] / 2, B['a'])
    mb = RHO * rl['A'] * Lb
    d = [(m_ror, (0, B['yp'], B['hp'])), (0.10, (0, B['yp'], B['hp'])), (0.06, (B['L'] / 2 + 0.04, B['yp'], B['hp'])),
         (0.03, (-B['L'] / 2, B['yp'], B['hp']))]
    for sx in (-1, 1):
        for sy in (-1, 1):
            d.append((mb, (sx * xe, B['yp'] + sy * B['a'] / 2, (B['hp'] + B['D_leg'] / 2) / 2)))
    return d + list(ekstra), xe


def a_last(m, com, poly, xe):
    B = PA
    F1 = T_VRI / R_GREP
    gx = xe + 0.029
    fall = [('10 N mot brukar i aksehøgd', (0, B['yp'], B['hp']), (0, -10, 0)),
            ('10 N mot vegg i aksehøgd', (0, B['yp'], B['hp']), (0, 10, 0)),
            ('10 N mot brukar på grepet', (gx, B['yp'], B['hp'] + R_GREP), (0, -10, 0)),
            (f'finger øvst på grepet {F1:.2f} N mot brukar', (gx, B['yp'], B['hp'] + R_GREP), (0, -F1, 0)),
            (f'finger øvst på grepet {F1:.2f} N mot vegg', (gx, B['yp'], B['hp'] + R_GREP), (0, F1, 0)),
            (f'finger framme på grepet {F1:.2f} N ned', (gx, B['yp'] - R_GREP, B['hp']), (0, 0, -F1)),
            (f'finger framme på grepet {F1:.2f} N opp', (gx, B['yp'] - R_GREP, B['hp']), (0, 0, F1)),
            ('10 N sidevegs i aksehøgd', (0, B['yp'], B['hp']), (10, 0, 0))]
    out = {}
    for nm, pk, F in fall:
        lam = velt_faktor(m, com, poly, pk, F)
        out[nm] = dict(lam=lam, F_lyft=lam * np.linalg.norm(F))
    return out


def del1_a():
    tittel('1. (a) BRU · dytt i grephøgd fram/bak, fingergest, retting')
    B = PA
    d, xe = a_delar()
    m, com = tyngd(d)
    y0, y1 = B['yp'] - B['a'], B['yp'] + B['a']
    poly = rekt(-xe, xe, y0, y1)
    tv = tippvinklar(m, com, poly)
    p(f"masse {m:.3f} kg, tyngdepunkt y {com[1]:.3f} z {com[2]:.3f} · føter y {y0:.2f}–{y1:.2f}, x ±{xe:.3f}")
    p(f"tipp fram {tv[0][1]:.1f}°, bak {tv[2][1]:.1f}°, side {tv[1][1]:.1f}° · rettande moment fram {m * G * tv[0][0]:.3f} N·m")
    L = a_last(m, com, poly, xe)
    for k, v in L.items():
        p(f"   {k:44s} tryggleik {v['lam']:6.2f}  (lyftar ved {v['F_lyft']:5.2f} N)" + ('  <- LYFTER' if v['lam'] < 1 else ('  (< 2)' if v['lam'] < 2 else '')))
    for mu in (0.3, 0.5, 0.8):
        p(f"   glid ved μ {mu}: {mu * m * G:.2f} N (lampa glir før ho tippar berre om μ < {L['10 N mot brukar i aksehøgd']['F_lyft'] / (m * G):.2f})")
    # kvar fell røyret: om framkanten (y0, z 0)
    r = math.hypot(B['yp'] - y0, B['hp'])
    p(f"   tippar fram: røyret (r {r:.3f} m om framføtene) landar ved y ≈ {y0 - r:+.2f} m, dvs. {abs(y0 - r):.2f} m utanfor bordkanten (y 0)")
    E_velt = m * G * (math.hypot(tv[0][0], com[2]) - com[2])
    p(f"   arbeid som veltar fram: {E_velt:.2f} J")
    res = dict(masse=m, com=list(com), tipp_fram=tv[0][1], M_res_fram=m * G * tv[0][0], last={k: v['lam'] for k, v in L.items()},
               F_lyft_10N_akse=L['10 N mot brukar i aksehøgd']['F_lyft'], E_velt_J=E_velt, landar_y=y0 - r)
    # ---- rettingar ----
    p('\n   Rettingar (kvar for seg):')
    F1 = T_VRI / R_GREP
    z_f = B['hp'] + R_GREP
    d_fram = com[1] - y0
    m_2f = 2 * F1 * z_f / (G * d_fram)
    m_10 = 10 * B['hp'] / (G * d_fram)
    p(f"   masse som trengst (tyngdepunkt uendra i y): λ ≥ 2 for fingeren {m_2f:.2f} kg (+{m_2f - m:.2f}); 10 N i aksehøgd {m_10:.2f} kg (+{m_10 - m:.2f})")
    rett = {}
    # (i) stålmeiar 40×8 mellom fram- og bakfot på kvar side: bind òg beina mot å spreie seg
    for bt in ((0.040, 0.008), (0.040, 0.010), (0.050, 0.012)):
        Lm = 2 * B['a'] + 0.04
        mm_ = RHO_ST * bt[0] * bt[1] * Lm
        dd, _ = a_delar([(mm_, (sx * xe, B['yp'], bt[1] / 2)) for sx in (-1, 1)])
        m2, c2 = tyngd(dd)
        L2 = a_last(m2, c2, poly, xe)
        tv2 = tippvinklar(m2, c2, poly)
        nm = f"stålmeie {bt[0] * 1000:.0f}×{bt[1] * 1000:.0f}×{Lm * 1000:.0f} per side"
        rett[nm] = dict(m_ekstra=2 * mm_, masse=m2, lam_finger=L2[f'finger øvst på grepet {F1:.2f} N mot brukar']['lam'],
                        F_lyft_akse=L2['10 N mot brukar i aksehøgd']['F_lyft'], tipp=tv2[0][1])
        p(f"   (i) {nm}: +{2 * mm_:.2f} kg -> {m2:.2f} kg, finger λ {rett[nm]['lam_finger']:.2f}, lyftar ved {rett[nm]['F_lyft_akse']:.1f} N i aksehøgd, tipp {tv2[0][1]:.1f}°")
    # (ii) føtene så langt fram som bordet tillet (y 0,01) og bakføtene til y 0,60 (utanfor skjermbreidda)
    poly2 = rekt(-xe, xe, 0.01, 0.60)
    L3 = a_last(m, com, poly2, xe)
    p(f"   (ii) føter y 0,01–0,60 (same masse): finger mot brukar λ {L3[f'finger øvst på grepet {F1:.2f} N mot brukar']['lam']:.2f}, mot vegg {L3[f'finger øvst på grepet {F1:.2f} N mot vegg']['lam']:.2f}, "
      f"10 N mot brukar lyftar ved {L3['10 N mot brukar i aksehøgd']['F_lyft']:.2f} N, mot vegg ved {L3['10 N mot vegg i aksehøgd']['F_lyft']:.2f} N")
    rett['føter 0,01–0,60'] = {k: v['lam'] for k, v in L3.items()}
    # (iii) tunge på grepet som peikar mot brukaren: gesten vert trykk ned/opp i staden for dytt fram/bak
    for rl in (0.026, 0.04):
        Ft = T_VRI / rl
        lam_n = velt_faktor(m, com, poly, (xe + 0.029, B['yp'] - rl, B['hp']), (0, 0, -Ft))
        lam_o = velt_faktor(m, com, poly, (xe + 0.029, B['yp'] - rl, B['hp']), (0, 0, Ft))
        p(f"   (iii) tunge r {rl * 1000:.0f} mm framme på grepet: {Ft:.2f} N ned λ {lam_n:.1f}, opp λ {lam_o:.2f}")
        rett[f'tunge r{rl * 1000:.0f}'] = dict(ned=lam_n, opp=lam_o)
    # beina spreier seg under eigenvekt utan meie
    h = B['hp'] - B['D_leg'] / 2
    H = (m * G / 4) * B['a'] / h
    p(f"   utan meie skyv kvart bein foten ut med {H:.2f} N; held berre om μ ≥ {H / (m * G / 4):.2f} eller toppen er momentstiv. Meia tek dette som strekk.")
    res['rettingar'] = rett
    res['m_krav_finger'] = m_2f
    res['m_krav_10N'] = m_10
    UT['a_dytt'] = res
    return m, com, poly, xe


# ==============================================================================================
# 2. (b) KROK
# ==============================================================================================
PB = MK.PB
F_GEST_B = 3.0


def b_bane(n=600):
    """Armbana i y–z: loddrett frå klemma, kvartbøy r 0,10, vassrett fram, kort fall til navet. Eiga oppbygging."""
    hp, R = PB['hp'], PB['R']
    H = hp + R + 0.015
    y0, y1, rf, z0 = PB['y0'], PB['yp'], PB['rf'], PB['z0']
    s1 = np.c_[np.full(n, y0), np.linspace(z0, H - rf, n)]
    th = np.linspace(0, np.pi / 2, n // 2)
    s2 = np.c_[y0 - rf + rf * np.cos(th), H - rf + rf * np.sin(th)]
    s3 = np.c_[np.linspace(y0 - rf, y1, n), np.full(n, H)]
    s4 = np.c_[np.full(n // 10, y1), np.linspace(H, hp + 1.12 * R, n // 10)]
    pts = np.vstack([s1, s2[1:], s3[1:]])
    i_tip = len(pts) - 1
    pts = np.vstack([pts, s4[1:]])
    X = np.c_[np.zeros(len(pts)), pts]
    return X, i_tip, H


def b_integral(D, t, last, n_end=None, kun_ein=None):
    """Einingslast (Castigliano) for krum stong: δ i kraftretninga = ∫[(|M|²−T²)/EI + T²/GJ] ds / |F|.
    last: [(P (3,), F (3,))] reell last; kun_ein: retning for einingslasta i punktet P0 (standard: same som lasta)."""
    X, i_tip, H = b_bane()
    if n_end is not None:
        X = X[:n_end + 1]
    Xm = (X[1:] + X[:-1]) / 2
    dX = np.diff(X, axis=0)
    ds = np.linalg.norm(dX, axis=1)
    tv = dX / ds[:, None]
    tr = ror(D, t)
    EI, GJ = E * tr['I'], GS * tr['J']
    M = np.zeros_like(Xm)
    for P, F in last:
        M += np.cross(np.asarray(P, float)[None] - Xm, np.asarray(F, float)[None])
    P0, u = kun_ein if kun_ein is not None else (last[0][0], np.asarray(last[0][1], float) / np.linalg.norm(last[0][1]))
    m = np.cross(np.asarray(P0, float)[None] - Xm, np.asarray(u, float)[None])
    TM, Tm = (M * tv).sum(1), (m * tv).sum(1)
    bend = ((M * m).sum(1) - TM * Tm) / EI
    tors = TM * Tm / GJ
    return float(((bend + tors) * ds).sum()), float((bend * ds).sum()), float((tors * ds).sum()), tr


def del2_b():
    tittel('2. (b) KROK · arm med vridning (einingslast-integral), Ø for 2 mm, klemme og bordplate')
    X, i_tip, H = b_bane()
    tip = X[i_tip]
    hub = X[-1]
    sen = np.array([0, PB['yp'], PB['hp']])
    grep = np.array([PB['L'] / 2 + 0.015, PB['yp'], PB['hp']])
    grep_topp = grep + [0, 0, R_GREP]
    L_arm = float(np.linalg.norm(np.diff(X, axis=0), axis=1).sum())
    m_hovud = RHO * math.pi * 2 * PB['R'] * PB['t'] * PB['L'] * (1 - PB['k'] * PB['beta'] / 180) + 0.10 + 0.06 + 0.04
    p(f"armlengd {L_arm:.3f} m, spiss (hjørnet) y {tip[1]:.3f} z {tip[2]:.3f}, hovud {m_hovud:.3f} kg")
    res = {}
    p(f"\n   {'Ø×t':8s} {'spiss x':>8s} {'(bøy/vri)':>12s} {'spiss y':>8s} {'grep x':>7s} {'grep y':>7s} {'grep z':>7s} {'finger y':>9s} {'eigenvekt':>10s} {'arm kg':>7s}   [mm, 3 N]")
    for D, t in ((0.023, 0.0015), (0.024, 0.0015), (0.025, 0.0015), (0.026, 0.0015), (0.025, 0.002), (0.028, 0.0015), (0.030, 0.0015)):
        sx, bx, vx, tr = b_integral(D, t, [(tip, (F_GEST_B, 0, 0))], n_end=i_tip)
        sy, *_ = b_integral(D, t, [(tip, (0, F_GEST_B, 0))], n_end=i_tip)
        gx, *_ = b_integral(D, t, [(grep, (F_GEST_B, 0, 0))])
        gy, *_ = b_integral(D, t, [(grep, (0, F_GEST_B, 0))])
        gz, *_ = b_integral(D, t, [(grep, (0, 0, -F_GEST_B))])
        fy, *_ = b_integral(D, t, [(grep_topp, (0, -T_VRI / R_GREP, 0))])
        norm = {}
        for nmF, Fv in (('x', (F_GEST_B, 0, 0)), ('y', (0, F_GEST_B, 0)), ('z', (0, 0, -F_GEST_B))):
            uv = [b_integral(D, t, [(grep, Fv)], kun_ein=(grep, e_))[0] for e_ in np.eye(3)]
            norm[nmF] = float(np.linalg.norm(uv)) * 1e3
        # eigenvekt: hovud i senteret + armvekt jamt; einingslast 1 N ned i senteret
        Xm = (X[1:] + X[:-1]) / 2
        ds = np.linalg.norm(np.diff(X, axis=0), axis=1)
        w = RHO * tr['A'] * ds * G
        last = [(sen, (0, 0, -m_hovud * G))]
        # armvekt: punktlaster i midtpunkta, men berre for snitt «nedstraums»: handsama ved å summere med indeks
        EI = E * tr['I']
        Mw = np.zeros_like(Xm)
        for i in range(len(Xm)):
            Mw[:i] += np.cross(Xm[i][None] - Xm[:i], np.array([0, 0, -w[i]])[None])
        Mw += np.cross(sen[None] - Xm, np.array([0, 0, -m_hovud * G])[None])
        mu = np.cross(sen[None] - Xm, np.array([0, 0, -1.0])[None])
        ned = float(((Mw * mu).sum(1) / EI * ds).sum())
        m_arm = RHO * tr['A'] * L_arm
        k = f"{D * 1000:.0f}x{t * 1000:.1f}"
        res[k] = dict(spiss_x=sx * 1e3, spiss_x_boy=bx * 1e3, spiss_x_vri=vx * 1e3, spiss_y=sy * 1e3, grep_x=gx * 1e3, grep_y=gy * 1e3, grep_z=gz * 1e3,
                      finger_y=fy * 1e3, ned_eigenvekt=ned * 1e3, m_arm=m_arm, grep_norm=norm)
        p(f"   Ø{D * 1000:.0f}×{t * 1000:.1f} {sx * 1e3:8.2f} {bx * 1e3:5.2f}/{vx * 1e3:5.2f} {sy * 1e3:8.2f} {gx * 1e3:7.2f} {gy * 1e3:7.2f} {gz * 1e3:7.2f} {fy * 1e3:9.2f} {ned * 1e3:10.2f} {m_arm:7.3f}"
          f"   | |u| i grepet x/y/z {norm['x']:.2f}/{norm['y']:.2f}/{norm['z']:.2f}")
    gamal = json.load(open(os.path.join(HER, 'mekanikk_tal.json'), encoding='utf-8'))['b']
    p(f"   rammeløysaren (mekanikk_tal.json) Ø23: spiss x {gamal['D23']['ut_av_plan']:.2f}, grep x/y/z {gamal['D23']['grep']['x'] * 1e3:.2f}/{gamal['D23']['grep']['y'] * 1e3:.2f}/"
      f"{gamal['D23']['grep']['z'] * 1e3:.2f}, eigenvekt {gamal['D23']['ned_eigenvekt']:.2f}; motoren (berre bøying, dist²): 1,97 mm")
    ok_spiss = [k for k, v in res.items() if v['spiss_x'] <= 2.0 and v['spiss_y'] <= 2.0]
    ok_grep = [k for k, v in res.items() if max(v['grep_x'], v['grep_y'], v['grep_z']) <= 2.0]
    ok_norm = [k for k, v in res.items() if max(v['grep_norm'].values()) <= 2.0]
    p(f"   held 2 mm i spissen: {ok_spiss} · i grepet, komponent langs krafta: {ok_grep} · i grepet, heile forskyvinga |u|: {ok_norm}")
    # rein vri 0,08 N·m om x i grepet (to fingrar): bøying i planet
    tr = ror(0.023, 0.0015)
    th = T_VRI * L_arm / (E * tr['I'])
    p(f"   rein vri {T_VRI} N·m (kraftpar): armen roterer {math.degrees(th):.3f}°, grepet flyttar {th * R_GREP * 1e3:.3f} mm. Berre fingerdyttet gjev svikt.")
    # eigenfrekvens sidevegs
    for k in ('23x1.5', '25x1.5'):
        kx = F_GEST_B / (res[k]['spiss_x'] / 1e3)
        f = math.sqrt(kx / (m_hovud + 0.25 * res[k]['m_arm'])) / (2 * math.pi)
        res[k]['f_side_Hz'] = f
        p(f"   Ø{k}: sidesving ≈ {f:.1f} Hz")
    UT['b_arm'] = res

    # ---------------- klemme: statikk om skruelina (eigen modell) ----------------
    tr = ror(0.023, 0.0015)
    Xm = (X[1:] + X[:-1]) / 2
    ds = np.linalg.norm(np.diff(X, axis=0), axis=1)
    w = RHO * tr['A'] * ds * G
    y_f, y_b, y_s, bx, t_bord = 0.67, 0.75, 0.72, 0.025, 0.025
    Q = np.array([0, y_s, 0.0])
    eigen = [(sen, (0, 0, -m_hovud * G))] + [(Xm[i], (0, 0, -w[i])) for i in range(len(Xm))]
    m_kl = PB['m_klemme']
    eigen.append((np.array([0, 0.71, -0.01]), (0, 0, -m_kl * G)))
    fall = {'eigenvekt': [],
            '10 N mot brukar i røyret': [(sen, (0, -10, 0))],
            '10 N mot vegg i røyret': [(sen, (0, 10, 0))],
            '10 N langs røyret (x)': [(sen, (10, 0, 0))],
            '10 N ned i grepsenden': [(grep, (0, 0, -10))],
            '10 N langs røyret i grepsenden': [(grep, (10, 0, 0))],
            'finger 3,08 N mot brukar øvst på grepet': [(grep_topp, (0, -T_VRI / R_GREP, 0))]}
    r_top = None
    # midlare friksjonsradius for jamt trykk på 50×80 om midten, og skrueputa
    gx_, gy_ = np.meshgrid(np.linspace(-bx, bx, 101), np.linspace(-(y_b - y_f) / 2, (y_b - y_f) / 2, 161))
    r_top = float(np.hypot(gx_, gy_).mean())
    kl = {}
    p(f"\n   Klemme: toppkjeft 50 × 80 mm (y 0,67–0,75), skrue under ved y 0,72; friksjonsradius topp {r_top * 1e3:.1f} mm")
    p(f"   {'lastfall':42s} {'V':>6s} {'Mx':>7s} {'My':>7s} {'Mz':>7s} {'H':>6s} | P for vipp {'P vri μ0,3':>10s} {'μ0,6':>6s}  [N, N·m om skruelina]")
    for nm, ek in fall.items():
        L = eigen + ek
        F = sum(np.array(f, float) for _, f in L)
        M = sum(np.cross(np.asarray(q, float) - Q, np.array(f, float)) for q, f in L)
        V = -F[2]
        # resultanten av topptrykket må liggje i kjeften: y_R = y_s − Mx/R, x_R = My/R, R = P + V
        need_y = M[0] / (y_s - y_f) if M[0] > 0 else -M[0] / (y_b - y_s)
        need_x = abs(M[1]) / bx
        P_vipp = max(0.0, max(need_y, need_x) - V)
        out = {}
        for mu in (0.3, 0.6):
            for r_pad in (0.0125 * 2 / 3, 0.020 * 2 / 3):
                # μ(R r_top + P r_pad) ≥ |Mz|, R = P + V
                Pv = max(0.0, (abs(M[2]) / mu - V * r_top) / (r_top + r_pad))
                Ps = max(0.0, (math.hypot(F[0], F[1]) / mu - V) / 2)
                out[(mu, r_pad)] = max(Pv, Ps)
        kl[nm] = dict(V=V, Mx=M[0], My=M[1], Mz=M[2], H=math.hypot(F[0], F[1]), P_vipp=P_vipp, P_vri_03=out[(0.3, 0.0125 * 2 / 3)], P_vri_06=out[(0.6, 0.0125 * 2 / 3)],
                      P_vri_03_pad40=out[(0.3, 0.020 * 2 / 3)])
        p(f"   {nm:42s} {V:6.2f} {M[0]:+7.2f} {M[1]:+7.2f} {M[2]:+7.2f} {math.hypot(F[0], F[1]):6.2f} | {P_vipp:8.0f} {out[(0.3, 0.0125 * 2 / 3)]:10.0f} {out[(0.6, 0.0125 * 2 / 3)]:6.0f}")
    P1 = max(max(v['P_vipp'], v['P_vri_03']) for v in kl.values())
    P1_sv = max(v['P_vipp'] for v in kl.values())
    P1_gu = max(max(v['P_vipp'], v['P_vri_06']) for v in kl.values())
    p(f"   Naudsynt klemkraft SF 1: {P1:.0f} N (μ 0,3, metall mot melamin) · {P1_gu:.0f} N (μ 0,6, gummi) · berre vipp (svivel tek vriinga): {P1_sv:.0f} N")
    P_d = 2 * P1
    p(f"   Dimensjonerande (SF 2): {P_d:.0f} N. Skruemoment M8 (k 0,2): {0.2 * 0.008 * P_d:.2f} N·m · M6: {0.2 * 0.006 * P_d:.2f} N·m")
    trykk = {}
    for nm_, A in (('toppkjeft 50×80', 0.05 * 0.08), ('pute Ø25', math.pi * 0.0125 ** 2), ('pute Ø40', math.pi * 0.02 ** 2), ('stålplate 60×60 under', 0.06 * 0.06)):
        trykk[nm_] = P_d / A / 1e6
        p(f"   flatetrykk {nm_:22s} {P_d / A / 1e6:5.2f} MPa ved {P_d:.0f} N")
    # kanttrykk når resultanten går til framkanten: lineært trykk, null bak
    Mx_max = max(v['Mx'] for v in kl.values())
    R = P_d + kl['eigenvekt']['V']
    e = Mx_max / R
    a_k = y_b - y_f
    q_maks = R / (a_k * 2 * bx) * (1 + 6 * e / a_k) if e <= a_k / 6 else 2 * R / (3 * (a_k / 2 - e) * 2 * bx)
    p(f"   kanttrykk ved framkanten av kjeften (Mx {Mx_max:.2f} N·m, R {R:.0f} N, e {e * 1e3:.1f} mm): {q_maks / 1e6:.2f} MPa")
    # bøyespenning i bordplata ved kanten (M fordelt på 0,2 m breidd)
    for tb in (0.025, 0.030):
        sig = 6 * Mx_max / (0.20 * tb ** 2)
        p(f"   bordplate {tb * 1e3:.0f} mm: bøyespenning frå {Mx_max:.1f} N·m over 0,2 m breidd {sig / 1e6:.2f} MPa (spon P2 f_m ≈ 11–14 MPa)")
    # C-ramma
    for mat, s_till, t_ in (('alu 6082', 125e6, 0.008), ('stål S235', 117e6, 0.006)):
        Mr = P_d * 0.035
        Wr = 0.05 * t_ ** 2 / 6
        p(f"   C-ramme {mat} 50×{t_ * 1e3:.0f} mm, kast 35 mm: M {Mr:.0f} N·m, σ {Mr / Wr / 1e6:.0f} MPa (tillate {s_till / 1e6:.0f})")
    # røyrfot i hylse
    for dh in (0.012, 0.040):
        Fk = Mx_max / (2 / 3 * dh)
        p(f"   røyrfot Ø23 i {dh * 1e3:.0f} mm djup hylse: kraftpar {Fk:.0f} N, lineært trykk på veggen {Fk / (0.023 * dh / 2) / 1e6:.1f} MPa")
    UT['b_klemme'] = dict(fall=kl, P_SF1_mu03=P1, P_SF1_mu06=P1_gu, P_SF1_svivel=P1_sv, P_SF2=P_d, trykk_MPa=trykk, kanttrykk_MPa=q_maks / 1e6, r_top=r_top)


# ==============================================================================================
# 3. (c) PRISME (form04/motor.py FINAL) · parametrar bokstavleg
# ==============================================================================================
PC = dict(L=0.60, bp=0.16, d=0.05, tp=0.003, ys=0.22, zs=0.70, col_w=0.10, col_f=0.03, col_t=0.002, col_y=0.512,
          fot_x=0.24, fot_y=0.30, fot_bak=0.04, t_fot=0.007, m_el=0.15, m_skjerm=4.0, p_skjerm=(0.0, 0.50, 0.20), T=0.20,
          renne=(0.016, 0.020, 0.0015), m_led=0.10)


def c_hovud(tp_eff=0.004):
    C = PC
    m_plate = RHO_PMMA * C['L'] * C['bp'] * tp_eff
    w, h, t = C['renne']
    m_renne = RHO * (w + 2 * h) * t * C['L']
    return m_plate, m_renne + C['m_led']


def c_delar(t_fot, variant='motor', tverr='U'):
    """variant 'motor': same masseoppsett som motoren (for å kontrollere talet). 'geometri': eige oppsett frå geometrien
    (eksakt U-areal, søyle frå fot til overkant arm, arm til framkant søyle, hengjar, kinn, ledd)."""
    C = PC
    m_plate, m_stong = c_hovud()
    m_hov = m_plate + m_stong
    z_akse = C['zs'] - m_plate * C['d'] / m_hov
    y0f = C['col_y'] + C['col_f'] + C['fot_bak'] - C['fot_y']
    y1f = y0f + C['fot_y']
    m_fot = RHO * C['fot_x'] * C['fot_y'] * t_fot + C['m_el']
    if variant == 'motor':
        A = (C['col_w'] + 2 * C['col_f']) * C['col_t']
        za = C['zs'] + 0.03
        L_arm = C['col_y'] + C['col_f'] - C['ys']
        d = [(m_plate, (0, C['ys'], C['zs'] - C['d'])), (m_stong, (0, C['ys'], C['zs'])),
             (RHO * A * L_arm, (0, C['ys'] + L_arm / 2, za)), (RHO * A * za, (0, C['col_y'] + C['col_f'] / 2, za / 2)),
             (m_fot, (0, (y0f + y1f) / 2, t_fot / 2))]
        return d, (y0f, y1f), z_akse
    if tverr == 'U':
        U = u_profil(C['col_w'], C['col_f'], C['col_t'])
        A, c = U['A'], U['c']
    else:                                                       # lukka 100×30×t
        t = tverr
        A = 2 * (C['col_w'] + C['col_f']) * t - 4 * t * t
        c = C['col_f'] / 2
    z_top = C['zs'] + 0.03 + C['col_f']
    y_bak = C['col_y'] + C['col_f']
    L_s = z_top - t_fot
    L_a = C['col_y'] - (C['ys'] - 0.012)
    m_k = 2 * RHO * 0.0015 * ((0.02 + C['bp']) / 2 * (C['d'] + C['tp']))
    d = [(m_plate, (0, C['ys'], C['zs'] - C['d'] - C['tp'] / 2)), (m_stong, (0, C['ys'], C['zs'] - 0.005)),
         (m_k, (0, C['ys'], C['zs'] - C['d'] / 2)), (0.05, (0, C['ys'], z_akse)),
         (2 * RHO * 0.002 * 0.024 * (z_top - (C['zs'] - 0.012)), (0, C['ys'], (z_top + C['zs'] - 0.012) / 2)),
         (RHO * A * L_a, (0, (C['ys'] - 0.012 + C['col_y']) / 2, z_top - c)),
         (RHO * A * L_s, (0, y_bak - c, t_fot + L_s / 2)),
         (m_fot, (0, (y0f + y1f) / 2, t_fot / 2))]
    return d, (y0f, y1f), z_akse


def vek(a):
    """ned (lysnormal) og fram i y–z for vippevinkel a (0 = arbeid, − = mot veggen). Same konvensjon som form04."""
    return np.array([0.0, -math.sin(a), -math.cos(a)]), np.array([0.0, -math.cos(a), math.sin(a)])


def c_gestsveip(m, com, poly, z_akse, T, alfa=np.radians(np.arange(-110, 76, 5))):
    """Minste tryggleik mot lyft over vippebana: handa på plate-kanten (framkant/bakkant), midt eller i enden, tangentielt, begge veg."""
    C = PC
    P0 = np.array([0, C['ys'], z_akse])
    dpl = C['d'] - (C['zs'] - z_akse)                         # plata ligg så langt under aksen
    best = (math.inf, None)
    ex = np.array([1.0, 0, 0])
    for a in alfa:
        ned, fram = vek(a)
        for sg in (1, -1):
            rr = dpl * ned + sg * C['bp'] / 2 * fram
            r = np.linalg.norm(rr)
            tang = np.cross(ex, rr) / r
            F = T / r
            for x in (0.0, C['L'] / 2):
                pk = P0 + rr + [x, 0, 0]
                for ret in (1, -1):
                    lam = velt_faktor(m, com, poly, pk, ret * F * tang)
                    if lam < best[0]:
                        best = (lam, dict(alfa=math.degrees(a), kant='framkant' if sg > 0 else 'bakkant', x=x, F=F, z=pk[2], y=pk[1],
                                          Fy=float(ret * F * tang[1]), Fz=float(ret * F * tang[2])))
    return best


def c_ramme(t_fot, tverr, kv=False, pkt=()):
    """Søyle + arm + stiv hengjar ned til vippeaksen + stive lenker til lastpunkt. Fast innspent i fotplata (sjå tekst)."""
    C = PC
    _, _, z_akse = c_delar(t_fot)
    if tverr == 'U':
        U = u_profil(C['col_w'], C['col_f'], C['col_t'])
        EA, EIs, EIst, GJ, c = E * U['A'], E * U['I_svak'], E * U['I_sterk'], GS * U['J'], U['c']
        a_kv = U['a_kv']
    else:
        t = tverr
        ks = kasse(C['col_w'], C['col_f'], t)
        Ist = (C['col_f'] * C['col_w'] ** 3 - (C['col_f'] - 2 * t) * (C['col_w'] - 2 * t) ** 3) / 12
        EA, EIs, EIst, GJ, c = E * ks['A'], E * ks['I_svak'], E * Ist, GS * ks['J'], C['col_f'] / 2
        a_kv = None
    z_top = C['zs'] + 0.03 + C['col_f']
    yc, zc = C['col_y'] + C['col_f'] - c, z_top - c
    Ls, La = zc - t_fot, yc - C['ys']
    fs = fa = 1.0
    if kv and a_kv:
        fs = Ls / (Ls - a_kv * math.tanh(Ls / a_kv))
        fa = La / (La - a_kv * math.tanh(La / a_kv))
    r = Ramme()
    col = [r.node((0, yc, z)) for z in np.linspace(t_fot, zc, 21)]
    for i in range(20):
        r.bjelke(col[i], col[i + 1], EA, EIs, EIst, GJ * fs, ref=(0, 1, 0))
    arm = [col[-1]] + [r.node((0, y, zc)) for y in np.linspace(yc, C['ys'], 11)[1:]]
    for i in range(10):
        r.bjelke(arm[i], arm[i + 1], EA, EIs, EIst, GJ * fa, ref=(0, 0, 1))
    piv = r.node((0, C['ys'], z_akse))
    r.stiv(arm[-1], piv, ref=(1, 0, 0))
    nd = []
    for q in pkt:
        if np.linalg.norm(np.asarray(q, float) - np.array([0, C['ys'], z_akse])) < 1e-9:
            nd.append(piv); continue
        n_ = r.node(tuple(q)); r.stiv(piv, n_); nd.append(n_)
    return r, col, arm, piv, nd, dict(Ls=Ls, La=La, fs=fs, fa=fa, GJ=GJ, EIs=EIs, EIst=EIst)


def del3_c():
    tittel('3. (c) PRISME · masse, tyngdepunkt, tipp, fottjukn, svikt med vridning av open U, hovudet')
    C = PC
    # ---- masse og tipp ----
    res = {}
    m_plate, m_stong = c_hovud()
    p(f"hovud: plate {m_plate:.3f} kg (PMMA 60×16×4 mm, som motoren; 3,4 mm snitt med riller gjev {RHO_PMMA * 0.6 * 0.16 * 0.0034:.3f}), renne+LED {m_stong:.3f} kg")
    for var in ('motor', 'geometri'):
        d, (y0f, y1f), z_akse = c_delar(C['t_fot'], var)
        poly = rekt(-C['fot_x'] / 2, C['fot_x'] / 2, y0f, y1f)
        for lab, dl in (('aleine', d), ('med skjerm', d + [(C['m_skjerm'], C['p_skjerm'])])):
            m, com = tyngd(dl)
            tv = tippvinklar(m, com, poly)
            F10 = velt_faktor(m, com, poly, (0, C['ys'], z_akse), (0, -10, 0)) * 10
            F10b = velt_faktor(m, com, poly, (0, C['ys'], z_akse), (0, 10, 0)) * 10
            F10x = velt_faktor(m, com, poly, (C['L'] / 2, C['ys'], z_akse), (10, 0, 0)) * 10
            Fm_motor = m * G * min(x[0] for x in tv) / C['zs']
            p(f"   [{var:8s}] {lab:10s} masse {m:.3f} kg, tp y {com[1]:.4f} z {com[2]:.4f} · tipp fram {tv[0][1]:5.1f}°, side {tv[1][1]:5.1f}°, bak {tv[2][1]:5.1f}° · "
              f"lyftar ved {F10:.2f} N mot brukar / {F10b:.2f} N mot vegg / {F10x:.2f} N sidevegs (i aksen) · motorformel F_tipp {Fm_motor:.3f} N")
            res[f'{var}|{lab}'] = dict(masse=m, com=list(com), tipp_fram=tv[0][1], tipp_side=tv[1][1], tipp_bak=tv[2][1], F_lyft_fram=F10, F_lyft_bak=F10b,
                                       F_lyft_side=F10x, F_tipp_motorformel=Fm_motor)
    d, (y0f, y1f), z_akse = c_delar(C['t_fot'], 'motor')
    p(f"   fot y {y0f:.3f}–{y1f:.3f}, vippeakse z {z_akse:.4f} ({(C['zs'] - z_akse) * 1e3:.1f} mm under LED-lina), skjermen sitt tyngdepunkt y 0,50 er {(C['col_y'] - 0.50) * 1e3:.0f} mm framfor søyla")
    # ---- gest: rett kraftpunkt og -retning ----
    poly = rekt(-C['fot_x'] / 2, C['fot_x'] / 2, y0f, y1f)
    gest = {}
    for T in (0.20, 0.30):
        for lab, extra in (('aleine', []), ('med skjerm', [(C['m_skjerm'], C['p_skjerm'])])):
            m, com = tyngd(d + extra)
            lam, info = c_gestsveip(m, com, poly, z_akse, T)
            gest[f'T{T:.2f}|{lab}'] = dict(lam=lam, **info)
            p(f"   gest T {T:.2f} N·m, {lab:10s}: minste tryggleik {lam:5.2f} ved α {info['alfa']:+.0f}°, {info['kant']}, x {info['x']:.2f}, z {info['z']:.3f}, "
              f"F {info['F']:.2f} N (Fy {info['Fy']:+.2f}, Fz {info['Fz']:+.2f})")
    res['gest'] = gest
    # ---- fottjukn ----
    p('\n   Fottjukn (alu, 0,24 × 0,30 m):')
    fot = {}
    for T in (0.20, 0.30):
        F_g = T / (C['bp'] / 2)
        t_motor = t_rett = None
        for t_mm in range(2, 41):
            t = t_mm / 1000
            dd, (a0, a1), za_ = c_delar(t, 'motor')
            m, com = tyngd(dd)
            tv = tippvinklar(m, com, poly)
            Fm = m * G * min(x[0] for x in tv) / C['zs']
            if t_motor is None and Fm >= 2 * F_g and min(x[1] for x in tv) >= 6:
                t_motor = t_mm
            lam, _ = c_gestsveip(m, com, poly, za_, T)
            if t_rett is None and lam >= 2:
                t_rett = (t_mm, m)
            if t_motor and t_rett:
                break
        fot[f'T{T:.2f}'] = dict(t_motorformel_mm=t_motor, t_rett_mm=t_rett[0] if t_rett else None, masse_rett=t_rett[1] if t_rett else None)
        p(f"   T {T:.2f} N·m: motorformelen (F_g i z 0,70, næraste kant) gjev {t_motor} mm · rett kraftpunkt (plate-kanten, sveip) gjev "
          f"{t_rett[0] if t_rett else '> 40'} mm ({t_rett[1]:.2f} kg)" if t_rett else '')
    res['fot'] = fot
    # 10 N: kva fot trengst for F_lyft ≥ 10 N mot brukar (utan skjerm)?
    for t_mm in range(2, 81):
        dd, _, za_ = c_delar(t_mm / 1000, 'motor')
        m, com = tyngd(dd)
        if velt_faktor(m, com, poly, (0, C['ys'], za_), (0, -10, 0)) >= 1.0:
            break
    p(f"   10 N mot brukar i aksen utan skjerm krev alu-fot {t_mm} mm ({m:.2f} kg)")
    res['fot_10N_mm'] = t_mm

    # ---- svikt og vridning ----
    U = u_profil(C['col_w'], C['col_f'], C['col_t'])
    p(f"\n   U 100×30×2: A {U['A'] * 1e6:.0f} mm², I svak {U['I_svak'] * 1e8:.2f}e-8, I sterk {U['I_sterk'] * 1e7:.2f}e-7 m⁴, J = Σbt³/3 = {U['J'] * 1e10:.2f}e-10 m⁴ "
      f"(GJ {GS * U['J']:.1f} N·m²), Cw {U['Cw'] * 1e11:.2f}e-11 m⁶, a = √(ECw/GJ) {U['a_kv']:.3f} m, skjersenter {U['e'] * 1e3:.1f} mm bak steget")
    for t in (0.002, 0.0015):
        ks = kasse(C['col_w'], C['col_f'], t)
        p(f"   lukka 100×30×{t * 1e3:.1f}: A {ks['A'] * 1e6:.0f} mm², J {ks['J'] * 1e7:.2f}e-7 m⁴ = {ks['J'] / U['J']:.0f} × U, GJ {GS * ks['J']:.0f} N·m²")
    P0 = np.array([0, C['ys'], z_akse])
    dpl = C['d'] - (C['zs'] - z_akse)
    hb = C['bp'] / 2
    ex = np.array([1.0, 0, 0])

    def gestpunkt(a_deg, sg, x, T):
        ned, fram = vek(math.radians(a_deg))
        rr = dpl * ned + sg * hb * fram
        r = np.linalg.norm(rr)
        tang = np.cross(ex, rr) / r
        return P0 + rr + [x, 0, 0], tang * T / r
    svikt = {}
    for T in (0.20, 0.30):
        # arbeid: framkanten trykt ned; stemning: øvre kant (bakkant) dregen mot brukar
        pa, Fa = gestpunkt(0, 1, 0.0, T)
        Fa = Fa if Fa[2] < 0 else -Fa
        pa2, Fa2 = gestpunkt(0, 1, C['L'] / 2, T)
        Fa2 = Fa2 if Fa2[2] < 0 else -Fa2
        ps, Fs = gestpunkt(-105, -1, 0.0, T)
        Fs = Fs if Fs[1] < 0 else -Fs
        ps2, Fs2 = gestpunkt(-105, -1, C['L'] / 2, T)
        Fs2 = Fs2 if Fs2[1] < 0 else -Fs2
        fall = [(f'arbeid, framkant midt, {np.linalg.norm(Fa):.2f} N ned', pa, Fa), (f'arbeid, framkant i enden (x 0,30)', pa2, Fa2),
                (f'stemning, øvre kant midt, mot brukar', ps, Fs), (f'stemning, øvre kant i enden (x 0,30)', ps2, Fs2)]
        if T == 0.20:
            fall += [('10 N sidevegs (x) i hovudenden', P0 + [C['L'] / 2, 0, 0], np.array([10.0, 0, 0])),
                     ('10 N mot brukar i aksen', P0, np.array([0, -10.0, 0]))]
        p(f"\n   T {T:.2f} N·m · {'lastfall':42s} {'U fri':>8s} {'U kvelv.':>9s} {'lukka 2':>8s} {'lukka 1,5':>9s}   [mm i lastpunktet, i kraftretninga]  søyla vrir (U fri)")
        for nm, pk, F in fall:
            rad = []
            for tv_, kv in (('U', False), ('U', True), (0.002, False), (0.0015, False)):
                r, col, arm, piv, nd, info = c_ramme(C['t_fot'], tv_, kv, pkt=[pk])
                u, rr = r.los({col[0]: 'alle'}, {nd[0]: (*F, 0, 0, 0)})
                rad.append(float(np.dot(u[nd[0], :3], F / np.linalg.norm(F))) * 1e3)
                if tv_ == 'U' and not kv:
                    vr = math.degrees(u[col[-1], 5]); varm = math.degrees(u[arm[-1], 4])
            svikt[f'T{T:.2f}|{nm}'] = dict(U=rad[0], U_kv=rad[1], lukka2=rad[2], lukka15=rad[3], soyle_vri_deg=vr, arm_vri_deg=varm)
            p(f"   {'':12s} {nm:42s} {rad[0]:8.2f} {rad[1]:9.2f} {rad[2]:8.3f} {rad[3]:9.3f}   {vr:+.2f}° (arm {varm:+.2f}°)")
    res['svikt'] = svikt
    # handrekning: vridning
    r, col, arm, piv, nd, info = c_ramme(C['t_fot'], 'U')
    Ls, La = info['Ls'], info['La']
    for T in (0.20, 0.30):
        Tq = T / hb * C['L'] / 2
        th_s = Tq * Ls / info['GJ']
        th_a = Tq * La / info['GJ']
        p(f"   hand, T {T:.2f}: kraft {T / hb:.2f} N i enden gjev {Tq:.2f} N·m · søyla (L {Ls:.3f}) vrir {math.degrees(th_s):.2f}° -> {th_s * 0.30 * 1e3:.1f} mm i enden; "
          f"armen (L {La:.3f}) vrir {math.degrees(th_a):.2f}° -> {th_a * 0.30 * 1e3:.1f} mm")
    T10 = 10 * (La + U['e'])
    p(f"   hand, 10 N sidevegs: søyla får {T10:.2f} N·m -> {math.degrees(T10 * Ls / info['GJ']):.1f}° ({T10 * Ls / info['GJ'] * La * 1e3:.0f} mm i hovudet)")
    # skjerspenning frå vridning
    tau = (0.30 / hb * C['L'] / 2) * C['col_t'] / U['J']
    tau10 = T10 * C['col_t'] / U['J']
    p(f"   skjerspenning open U: {tau / 1e6:.1f} MPa (gest T 0,30 i enden, 1,1 N·m), {tau10 / 1e6:.0f} MPa (10 N sidevegs) mot tillate {125 / math.sqrt(3):.0f} MPa")
    # eigenfrekvens for vridningssvinging om søyla
    m_hov = m_plate + m_stong
    Iz = m_hov * (C['L'] ** 2 / 12 + La ** 2) + RHO * U['A'] * La * La ** 2 / 3
    frek = {}
    for lab, tv_, kv in (('U fri', 'U', False), ('U kvelv.', 'U', True), ('lukka 2', 0.002, False), ('lukka 1,5', 0.0015, False)):
        r, col, arm, piv, nd, info = c_ramme(C['t_fot'], tv_, kv)
        u, _ = r.los({col[0]: 'alle'}, {piv: (0, 0, 0, 0, 0, 1.0)})
        k = 1 / u[piv, 5]
        frek[lab] = math.sqrt(k / Iz) / (2 * math.pi)
        p(f"   vridningssving om søyla, {lab:9s}: k {k:8.1f} N·m/rad, I {Iz:.4f} kg·m² -> {frek[lab]:5.1f} Hz")
    res['f_vri_Hz'] = frek
    # statisk nedbøying frå hovudvekta (+ arm)
    r, col, arm, piv, nd, info = c_ramme(C['t_fot'], 'U')
    last = {piv: np.array([0, 0, -m_hov * G, 0, 0, 0.0])}
    w_arm = RHO * U['A'] * La * G
    for i in range(10):
        for n_ in (arm[i], arm[i + 1]):
            last[n_] = last.get(n_, np.zeros(6)) + np.array([0, 0, -w_arm / 20, 0, 0, 0])
    u, rr = r.los({col[0]: 'alle'}, last)
    ned = -u[piv, 2] * 1e3
    hand = m_hov * G * (La ** 3 / 3 + La ** 2 * Ls) / (E * U['I_svak']) * 1e3
    M0 = abs(rr[col[0], 3])
    p(f"   statisk: hovudet {m_hov:.3f} kg søkk {ned:.3f} mm (hand, berre hovud {hand:.3f}; motoren 0,355) og hallar {math.degrees(u[piv, 3]):+.3f}°; "
      f"moment i søylefoten {M0:.2f} N·m, σ {M0 * (C['col_f'] - U['c']) / U['I_svak'] / 1e6:.1f} MPa")
    res['ned_hovud_mm'] = ned
    res['M_fot_stat'] = M0
    # fotplata: statisk moment framover > gestmoment bakover -> plata ligg an, ingen lyft
    EIf = E * C['fot_x'] * C['t_fot'] ** 3 / 12
    wf = RHO * C['fot_x'] * C['t_fot'] * G
    for Tg in (0.20, 0.30):
        Mb = Tg / hb * (0.75 - C['t_fot'])
        net = Mb - M0
        if net <= 0:
            p(f"   fotplata, gest T {Tg:.2f} mot veggen øvst: {Mb:.2f} N·m bakover mot {M0:.2f} statisk framover -> plata ligg an, ingen svikt frå foten")
        else:
            l = math.sqrt(2 * net / wf)
            th = net * l / (3 * EIf)
            p(f"   fotplata, gest T {Tg:.2f} mot veggen øvst: netto {net:.2f} N·m bakover -> plata lyftar {l * 1e3:.0f} mm framfor søyla, søyla hallar {th * 1e3:.3f} mrad "
              f"({th * 0.75 * 1e3:.3f} mm øvst): ubetydeleg")
    # ---- hovudet sjølv ----
    w_, h_, t_ = C['renne']
    J_r = (w_ - t_ + 2 * (h_ - t_ / 2)) * t_ ** 3 / 3
    G_pm = E_PMMA / (2 * 1.37)
    J_p = C['bp'] * C['tp'] ** 3 / 3
    k1 = GS * J_r / (C['L'] / 2 - 0.05)
    k2 = 1 / (C['L'] / (G_pm * J_p) + (C['L'] / 2 - 0.05) / (GS * J_r))
    hov = {}
    for T in (0.20, 0.30):
        th = T / (k1 + k2)
        hov[f'T{T:.2f}'] = dict(grad=math.degrees(th), kant_mm=th * hb * 1e3)
        p(f"   hovudet vrir seg sjølv (open renne 16×20×1,5, GJ {GS * J_r:.2f} N·m², + plata via kinna): T {T:.2f} i enden -> {math.degrees(th):.2f}°, plate-kanten {th * hb * 1e3:.2f} mm")
    # plata: spenn mellom kinna i endane
    q = RHO_PMMA * C['bp'] * 0.004 * G
    sag = {}
    for lab, tp_, Ep, Lsp in (('3 mm, kinn i endane (0,60 m), kort tid', 0.003, E_PMMA, 0.60), ('3,5 mm snitt med riller, kort tid', 0.0035, E_PMMA, 0.60),
                              ('3 mm, kryp 1 år (E ≈ 2,0 GPa)', 0.003, 2.0e9, 0.60), ('3 mm, to hengjarar ved x ±0,10 (spenn 0,20 / utkrag 0,20)', 0.003, E_PMMA, None),
                              ('6 mm, kinn i endane', 0.006, E_PMMA, 0.60)):
        I = C['bp'] * tp_ ** 3 / 12
        qq = RHO_PMMA * C['bp'] * (tp_ + 0.001) * G if tp_ != 0.0035 else q
        if Lsp is None:
            s = 0.0069 * qq * 0.20 ** 4 / (Ep * I) * 1e3        # tre like spenn (kinn i endane + hengjarar ved ±0,10), største nedbøying
        else:
            s = 5 * qq * Lsp ** 4 / (384 * Ep * I) * 1e3
        sag[lab] = s
        p(f"   PMMA-plata, {lab:58s}: nedbøying {s:6.2f} mm")
    res['hovud_vri'] = hov
    res['plate_sag_mm'] = sag
    # pendel om aksen ligg i LED-lina (som geometrien teiknar hengjaren)
    T_pend = m_plate * G * C['d'] * math.sin(math.radians(105))
    p(f"   om vippeaksen ligg i LED-lina (hengjaren i geometri() endar i z {C['zs'] - 0.012:.3f}): plata gjev pendelmoment {T_pend:.3f} N·m ved α −105°; "
      f"friksjon 0,20 held ikkje, 0,30 held med faktor {0.30 / T_pend:.2f}")
    m, com = tyngd(d)
    for Tf in (0.45, 0.45 + T_pend):
        lam, info = c_gestsveip(m, com, poly, C['zs'], Tf)
        p(f"   med pendel (akse i LED-lina): handa må overvinne {Tf:.2f} N·m -> gesttryggleik utan skjerm {lam:.2f} ({info['alfa']:+.0f}°, {info['kant']}, z {info['z']:.3f})")
        res[f'gest_pendel_T{Tf:.2f}'] = lam
    res['T_pendel_LEDakse'] = T_pend
    # masse med lukka profil
    for tv_ in (0.002, 0.0015):
        dd, _, _ = c_delar(C['t_fot'], 'geometri', tv_)
        mU, _ = tyngd(c_delar(C['t_fot'], 'geometri', 'U')[0])
        mc, cc = tyngd(dd)
        p(f"   masse med lukka 100×30×{tv_ * 1e3:.1f} i staden for U: {mc:.3f} kg (U: {mU:.3f})")
        res[f'masse_lukka_{tv_ * 1e3:.1f}'] = mc
    UT['c_prisme'] = res


# ==============================================================================================
# 4. VARME
# ==============================================================================================
LYS_DEL = 0.33          # del av elektrisk effekt som går ut som lys ved 100 lm/W (≈ 300 lm per optisk watt, 2700 K Ra 90)


def h_renne(dT, eps, D_eq=0.056 / math.pi):
    return h_sylinder(D_eq, dT, eps)


def ror_T(P, Lz, Le, D, t, beta, eps, eta_kav, Rp):
    q_ror = P * (1 - LYS_DEL * eta_kav)                     # LED-varme + lys som vert absorbert i holrommet
    q_led = P * (1 - LYS_DEL)
    dT = 15.0
    bue = (math.pi - math.radians(beta)) * D / 2
    for _ in range(40):
        h = h_sylinder(D, dT, eps)[0]
        A = math.pi * D * Lz * (1 - beta / 180) * finne(h, t, bue) + 2 * math.pi * D * Le * finne(h, t, Le)
        dT = q_ror / (h * A)
    return dT, 25 + dT + q_led / Lz * Rp, h, A


def renne_T(P, L, eps, Rp, A_per_m=0.056, eta_kav=0.95):
    q_ror = P * (1 - LYS_DEL * eta_kav)
    q_led = P * (1 - LYS_DEL)
    dT = 10.0
    for _ in range(40):
        h = h_renne(dT, eps)[0]
        A = A_per_m * L
        dT = q_ror / (h * A)
    return dT, 25 + dT + q_led / L * Rp, h, A


def trygg_qm(fun, grense_Ts=60.0, grense_dT=30.0):
    """Største W/m med T_s ≤ grense og overflate-ΔT ≤ grense_dT (25 °C rom)."""
    lo, hi = 0.1, 200.0
    for _ in range(60):
        q = (lo + hi) / 2
        dT, Ts = fun(q)[:2]
        if Ts <= grense_Ts and dT <= grense_dT:
            lo = q
        else:
            hi = q
    return lo


def del4_varme():
    tittel('4. VARME · LED inne i røyr (a/b) og i renne (c)')
    kj = json.load(open(os.path.join(os.path.dirname(HER), 'konsept.json'), encoding='utf-8'))
    res = {}
    D, t, beta = 0.044, 0.0012, 25.0
    for key, Lz, Le, eta in (('a', 0.536 * 1.12, (1.12 - 0.536 * 1.12) / 2, 0.674), ('b', 0.94 * 0.64 - 0.03, 0.02, 0.674)):
        P = kj[key]['P_W']
        A_g = kj[key]['A_kjol_cm2']; A_k = kj[key]['A_krav_cm2']
        p(f"({key}) P {P:.2f} W over {Lz:.2f} m = {P / Lz:.1f} W/m · motoren: {A_g:.0f}/{A_k:.0f} cm² (h 10, ΔT 30)")
        for lab, eps in (('eloksert/lakka ε 0,85', 0.85), ('blank alu ε 0,10', 0.10)):
            for Rp in (0.1, 0.3):
                dT, Ts, h, A = ror_T(P, Lz, Le, D, t, beta, eps, eta, Rp)
                res[f'{key}|{lab}|R{Rp}'] = dict(dT=dT, T_s=Ts, h=h, A_eff_cm2=A * 1e4)
                p(f"    {lab:22s} R' {Rp:.1f} K·m/W: h {h:4.1f} W/m²K, A_eff {A * 1e4:5.0f} cm², røyret ΔT {dT:4.1f} K, LED-loddepunkt ≈ {Ts:4.1f} °C")
        res[f'{key}|qm'] = P / Lz
    P = kj['c']['P_W']
    p(f"(c) P {P:.2f} W over 0,60 m = {P / 0.6:.1f} W/m · motoren: {kj['c']['A_kjol_cm2']:.0f}/{kj['c']['A_krav_cm2']:.0f} cm² (tel begge sider av renna, 2 × 0,056 × 0,60)")
    for lab, eps in (('eloksert/lakka ε 0,85', 0.85), ('blank alu ε 0,10', 0.10)):
        for Rp in (0.1, 0.3):
            dT, Ts, h, A = renne_T(P, 0.60, eps, Rp)
            res[f'c|{lab}|R{Rp}'] = dict(dT=dT, T_s=Ts, h=h, A_cm2=A * 1e4)
            p(f"    {lab:22s} R' {Rp:.1f}: berre utsida (336 cm²), h {h:4.1f}, renna ΔT {dT:4.1f} K, LED ≈ {Ts:4.1f} °C")
    res['c|qm'] = P / 0.6
    # trygg effekt per meter
    p('\n   Trygg effekt per meter (25 °C rom; loddepunkt ≤ 60 °C og overflate ≤ 55 °C), langt røyr/renne utan endefinnar:')
    tr = {}
    for lab, eps in (('ε 0,85', 0.85), ('ε 0,10', 0.10)):
        for Rp in (0.1, 0.3):
            qr = trygg_qm(lambda q: ror_T(q, 1.0, 0.0, D, t, beta, eps, 0.674, Rp))
            qc = trygg_qm(lambda q: renne_T(q, 1.0, eps, Rp))
            qc2 = trygg_qm(lambda q: renne_T(q, 1.0, eps, Rp, A_per_m=0.056 + 0.5 * 0.054))
            tr[f'{lab}|R{Rp}'] = dict(ror44=qr, renne=qc, renne_inn=qc2)
            p(f"    {lab} R' {Rp:.1f}: røyr Ø44×1,2 {qr:5.1f} W/m · renne 16×20 utside {qc:5.1f} W/m (med halve innsida {qc2:5.1f})")
    res['trygg_W_per_m'] = tr
    # kriteriet: kva ΔT ville motoren sitt areal gje med rett h
    for key in 'abc':
        P = kj[key]['P_W']; A = kj[key]['A_kjol_cm2'] / 1e4
        p(f"   motorkriteriet ({key}): P/(h·A) med h 10 og motorareal = {P / (10 * A):.1f} K (krav ≤ 30)")
    UT['varme_inne'] = res


# ==============================================================================================
def main():
    MK.sjolvtest()
    del1_a()
    del2_b()
    del3_c()
    del4_varme()

    def rein(o):
        if isinstance(o, dict): return {str(k): rein(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)): return [rein(v) for v in o]
        if isinstance(o, (np.floating, float)): return None if not math.isfinite(float(o)) else round(float(o), 5)
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, np.ndarray): return rein(o.tolist())
        return o
    fn = os.path.join(HER, 'mekanikk_tal.json')
    gamal = json.load(open(fn, encoding='utf-8'))
    gamal['_merknad'] = ('c_stab, c_svikt, c_gest, vipp og varme["c|..."] er rekna for det GAMLE (c) flak (form03) i mekanikk.py. '
                         'Prisme (form04) står under c_prisme, rekna i mekanikk_ut.py. a_dytt, b_arm, b_klemme og varme_inne er òg frå mekanikk_ut.py.')
    gamal.update(rein(UT))
    json.dump(gamal, open(fn, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    p('\n-> mekanikk_tal.json (oppdatert)')


if __name__ == '__main__':
    main()
