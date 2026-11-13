# -*- coding: utf-8 -*-
"""gransking/mekanikk_kontroll.py · uavhengig handkontroll av mekanikk_ut.py og motorane.
Ingen import frå mekanikk.py, mekanikk_ut.py, felles.py eller motorane: berre grunnformlar og parametrane skrivne inn.
Nytt her: kollisjon hovud/arm i (c) over vippebana, pendel og losriving i friksjonsleddet, motvekt bak i (a),
vidd i det opne røyret (a/b), varme med Morgan-korrelasjon og berøringsgrense.
Køyr: PYTHONIOENCODING=utf-8 python mekanikk_kontroll.py   (om lag 1 s)
"""
import math, json, os
import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
g, E, nu, rho, rho_st = 9.81, 70e9, 0.33, 2700.0, 7850.0
Gs = E / (2 * (1 + nu))
UT = {}


def p(*a):
    print(*a, flush=True)


def ror(D, t):
    d = D - 2 * t
    I = math.pi / 64 * (D ** 4 - d ** 4)
    return math.pi / 4 * (D ** 2 - d ** 2), I, 2 * I


# =============================== (a) BRU =========================================
p('== (a) bru')
L, D, t, beta, k, yp, hp, a, Dl, tl = 1.12, 0.044, 0.0012, 25.0, 0.536, 0.18, 0.62, 0.15, 0.020, 0.0015
A_r = ror(D, t)[0]
m_ror = rho * A_r * L * (1 - k * beta / 180)
m_hov = m_ror + 0.10 + 0.06 + 0.03
A_l = ror(Dl, tl)[0]
L_l = math.hypot(hp - Dl / 2, a)
m_bein = 4 * rho * A_l * L_l
m_a = m_hov + m_bein
z_a = (m_hov * hp + m_bein * (hp + Dl / 2) / 2) / m_a
yf, yb = yp - a, yp + a
M_fram = m_a * g * (yp - yf)
z_grep = hp + 0.026
p(f'masse {m_a:.3f} kg, tp z {z_a:.3f}, tipp fram {math.degrees(math.atan((yp - yf) / z_a)):.1f}°, M_rett {M_fram:.2f} N·m')
F_akse, F_grep = M_fram / hp, M_fram / z_grep
F_fing = 0.08 / 0.026
p(f'lyftar ved {F_akse:.2f} N i aksehøgd, {F_grep:.2f} N øvst på grepet; finger {F_fing:.2f} N der: λ {F_grep / F_fing:.2f}; 10 N: λ {F_grep / 10:.2f}')
p(f'kraftpar 0,08 N·m om x (rein vri): λ {M_fram / 0.08:.0f}')
# billegaste retting: meie langs foten (y 0,01 -> yb2) med stål, og evt. lodd bak
res_a = dict(masse=m_a, F_lyft_akse=F_akse, F_lyft_grep=F_grep, lam_finger=F_grep / F_fing)
kand = []
for lab, b_, h_, y0m, y1m, m_lodd, y_lodd in (
        ('stål i føtene (y 0,03–0,33, sentrum)', 0, 0, 0, 0, None, None),
        ('meie stål 25×5, y 0,01–0,70', 0.025, 0.005, 0.01, 0.70, 0.0, 0.0),
        ('meie alu 25×5, y 0,01–0,70 + lodd 2×0,35 kg bak (y 0,66)', 0.025, 0.005, 0.01, 0.70, 0.70, 0.66),
        ('meie stål 30×6, y 0,01–0,70', 0.030, 0.006, 0.01, 0.70, 0.0, 0.0)):
    if m_lodd is None:      # masse som trengst i sentrum for 10 N øvst på grepet
        m_need = 10 * z_grep / (g * (yp - yf))
        kand.append(dict(lab=lab, ekstra=m_need - m_a, F_fram=10.0, F_bak=10.0, masse=m_need))
        p(f'   {lab}: treng {m_need:.2f} kg totalt (+{m_need - m_a:.2f}) for 10 N øvst på grepet')
        continue
    rr = rho_st if 'stål' in lab.split('+')[0] else rho
    m_m = 2 * rr * b_ * h_ * (y1m - y0m)
    ms = [(m_a, yp), (m_m, (y0m + y1m) / 2), (m_lodd, y_lodd)]
    M = sum(x for x, _ in ms); yc = sum(x * y for x, y in ms) / M
    Ff = M * g * (yc - y0m) / z_grep
    Fb = M * g * (y1m - yc) / z_grep
    kand.append(dict(lab=lab, ekstra=M - m_a, F_fram=Ff, F_bak=Fb, masse=M))
    p(f'   {lab}: +{M - m_a:.2f} kg -> {M:.2f} kg, lyftar ved {Ff:.1f} N fram / {Fb:.1f} N bak øvst på grepet (finger λ {Ff / F_fing:.1f})')
res_a['rettingar'] = kand
# ubalanse i røyret med spalte (2β ope) + LED-modul 18 mm frå aksen
Rm = (D - t) / 2
e_ring = Rm * math.sin(math.radians(beta)) / (math.pi - math.radians(beta))
m_spalt = rho * A_r * (k * L) * (1 - beta / 180)
T_ub = m_spalt * g * e_ring + 0.10 * g * 0.018
J_open = (2 * math.pi - 2 * math.radians(beta)) * Rm * t ** 3 / 3
GJo = Gs * J_open
p(f'ubalanse om røyraksen: spalte {e_ring * 1e3:.1f} mm ({m_spalt * g * e_ring:.4f} N·m) + LED 0,10 kg 18 mm ute = {T_ub:.3f} N·m mot friksjon 0,08 (faktor {0.08 / T_ub:.1f})')
p(f'ope røyr: GJ {GJo:.2f} N·m² (lukka {Gs * ror(D, t)[2]:.0f}); 0,04 N·m gjennom 0,60 m spalte vrir {math.degrees(0.04 * 0.60 / GJo):.2f}°')
res_a.update(T_ubalanse=T_ub, GJ_ope=GJo)
UT['a'] = res_a

# =============================== (b) KROK ========================================
p('\n== (b) krok, arm ut av planet: δ = ∫(Mb²/EI + T²/GJ)ds/F, eiga parametrisering')
hpB, RB = 0.62, 0.022
H = hpB + RB + 0.015
y0, y1, rf, z0 = 0.74, 0.25, 0.10, 0.012
yh = y0 - rf                                    # slutten av bogen


def arm_pkt(n=4000):
    """(punkt (y,z), tangent (y,z), ds) langs armen frå klemma til spissen (hjørnet over navet)."""
    out = []
    zs = np.linspace(z0, H - rf, n); ds = zs[1] - zs[0]
    out += [((y0, z), (0.0, 1.0), ds) for z in zs[:-1] + ds / 2]
    ph = np.linspace(0, math.pi / 2, n); dp = ph[1] - ph[0]
    out += [((yh + rf * math.cos(q), H - rf + rf * math.sin(q)), (-math.sin(q), math.cos(q)), rf * dp) for q in ph[:-1] + dp / 2]
    ys = np.linspace(yh, y1, n); dy = abs(ys[1] - ys[0])
    out += [((y, H), (-1.0, 0.0), dy) for y in ys[:-1] - dy / 2]
    return out


ARM = arm_pkt()


def delta(Dd, tt, A3, F3):
    """forskyving langs F i punktet A3 (x,y,z); armen ligg i x = 0."""
    _, I, J = ror(Dd, tt)
    F3 = np.asarray(F3, float); A3 = np.asarray(A3, float)
    s = 0.0
    for (y, z), (ty, tz), ds in ARM:
        r = A3 - np.array([0.0, y, z])
        M = np.cross(r, F3)
        T = M[1] * ty + M[2] * tz
        s += ((M @ M - T * T) / (E * I) + T * T / (Gs * J)) * ds
    return s / np.linalg.norm(F3)


spiss = (0.0, y1, H)
grep = (0.335, y1, hpB)
gtopp = (0.335, y1, hpB + 0.026)
res_b = {}
for Dd in (0.023, 0.024, 0.025, 0.026):
    dx = delta(Dd, 0.0015, spiss, (3, 0, 0)) * 1e3
    dfi = delta(Dd, 0.0015, gtopp, (0, -F_fing, 0)) * 1e3
    dgx = delta(Dd, 0.0015, grep, (3, 0, 0)) * 1e3
    res_b[f'{Dd * 1e3:.0f}x1.5'] = dict(spiss_x=dx, finger=dfi, grep_x=dgx)
    p(f'   Ø{Dd * 1e3:.0f}×1,5: 3 N sidevegs i spissen {dx:.2f} mm · i grepet {dgx:.2f} mm · fingergesten (3,08 N i y øvst på grepet) {dfi:.2f} mm')
# rett L, handformel (utan boge): P a³/3EI + P h³/3EI + P a² h/GJ
_, I, J = ror(0.023, 0.0015)
aL, hL = y0 - y1, H - z0
dL = 3 * (aL ** 3 / (3 * E * I) + hL ** 3 / (3 * E * I) + aL ** 2 * hL / (Gs * J)) * 1e3
p(f'   kontroll, rett L utan boge (a {aL:.2f}, h {hL:.3f}): {dL:.2f} mm (bogen kortar armane, så litt over)')
# klemme, dimensjonerande: 10 N langs røyret i navet -> Mz om skruelina, My om kjeftkanten
y_s = 0.72
Mz = 10 * (y_s - y1)
My = 10 * (hpB - 0.0)
m_heile = 1.00
V = m_heile * g
xx, yy = np.meshgrid(np.linspace(-0.025, 0.025, 51), np.linspace(-0.04, 0.04, 81))
r_top = float(np.hypot(xx, yy).mean())
for mu in (0.3, 0.6):
    P_vri = (Mz / mu - V * r_top) / (r_top + 2 / 3 * 0.020)
    P_rull = My / 0.025 - V
    p(f'   μ {mu}: vri krev {P_vri:.0f} N (Ø40-pute), rulling over 50 mm kjeft krev {P_rull:.0f} N -> SF 2: {2 * max(P_vri, P_rull):.0f} N')
    res_b[f'klem_mu{mu}'] = dict(P_vri=P_vri, P_rull=P_rull, P_SF2=2 * max(P_vri, P_rull))
P_d = res_b['klem_mu0.3']['P_SF2']
for lab, A in (('Ø25', math.pi * 0.0125 ** 2), ('Ø40', math.pi * 0.02 ** 2), ('60×60', 0.0036), ('100×80', 0.008)):
    p(f'   trykk {lab}: {P_d / A / 1e6:.2f} MPa ved {P_d:.0f} N')
res_b['trykk_Ø25_MPa'] = P_d / (math.pi * 0.0125 ** 2) / 1e6
res_b['T_M8_Nm'] = 0.2 * 0.008 * P_d
p(f'   M8, k 0,2: {0.2 * 0.008 * P_d:.2f} N·m; stjernegrep Ø50 -> {0.2 * 0.008 * P_d / 0.025:.0f} N i kanten')
UT['b'] = res_b

# =============================== (c) PRISME =======================================
p('\n== (c) prisme')
Lh, bp, dd, tp, ys, zs = 0.60, 0.16, 0.05, 0.003, 0.22, 0.70
cw, cf, ct, cy = 0.10, 0.03, 0.002, 0.512
fx, fy, tf = 0.24, 0.30, 0.007
za = zs + 0.03
yF1 = cy + cf + 0.04; yF0 = yF1 - fy
A_U = cw * ct + 2 * (cf - ct) * ct
cU = (cw * ct * ct / 2 + 2 * (cf - ct) * ct * (ct + (cf - ct) / 2)) / A_U       # frå ytterflata av steget
m_pl = 1190 * Lh * bp * (tp + 0.001)
m_rn = rho * (0.016 + 0.040) * 0.0015 * Lh + 0.10
m_kinn = 2 * rho * 0.0015 * (0.02 + bp) / 2 * (dd + tp)
z_pl, z_rn, z_kinn = zs - dd - 0.002, zs + 0.005, zs - dd / 2
m_hd = m_pl + m_rn + m_kinn
z_cg = (m_pl * z_pl + m_rn * z_rn + m_kinn * z_kinn) / m_hd


def delar(t_fot=tf, lukka=None):
    A = A_U if lukka is None else 2 * (cw + cf) * lukka - 4 * lukka ** 2
    c = cU if lukka is None else cf / 2
    ztop = za + cf
    Larm = cy - (ys - 0.012)
    Ls = ztop - t_fot
    d = [(m_pl, ys, z_pl), (m_rn, ys, z_rn), (m_kinn, ys, z_kinn), (0.05, ys, z_cg),
         (2 * rho * 0.002 * 0.024 * (ztop - (zs - 0.012)), ys, (ztop + zs - 0.012) / 2),
         (rho * A * Larm, (ys - 0.012 + cy) / 2, ztop - c), (rho * A * Ls, cy + cf - c, t_fot + Ls / 2),
         (rho * fx * fy * t_fot + 0.15, (yF0 + yF1) / 2, t_fot / 2)]
    return d


def tp_(d):
    m = sum(q[0] for q in d)
    return m, sum(q[0] * q[1] for q in d) / m, sum(q[0] * q[2] for q in d) / m


SKJ = (4.0, 0.50, 0.20)
res_c = {}
for lab, d in (('aleine', delar()), ('med skjerm', delar() + [SKJ])):
    m, yc, zc = tp_(d)
    tf_ = math.degrees(math.atan((yc - yF0) / zc)); tb_ = math.degrees(math.atan((yF1 - yc) / zc)); ts_ = math.degrees(math.atan(fx / 2 / zc))
    F10 = m * g * (yc - yF0) / z_cg
    res_c[lab] = dict(masse=m, y=yc, z=zc, tipp_fram=tf_, tipp_bak=tb_, tipp_side=ts_, F_lyft_akse=F10)
    p(f'   {lab:10s}: {m:.3f} kg, tp y {yc:.4f} z {zc:.4f}, tipp fram {tf_:.1f}° bak {tb_:.1f}° side {ts_:.1f}°, lyftar ved {F10:.2f} N mot brukar i aksen (z {z_cg:.3f})')
p(f'   hovud {m_hd:.3f} kg, tyngdepunkt z {z_cg:.4f} = {(zs - z_cg) * 1e3:.1f} mm under LED-lina')


def hovud_pkt(alfa, akse_z, s, w):
    """punkt på hovudet: s langs «fram» (−bp/2..bp/2), w langs «ned» frå LED-lina. Vippar om (ys, akse_z)."""
    a = math.radians(alfa)
    ned0, fram0 = np.array([0.0, -1.0]), np.array([-1.0, 0.0])          # α = 0, (y, z)
    p0 = np.array([0.0, zs - akse_z]) + w * ned0 + s * fram0              # relativt til aksen
    c, sn = math.cos(a), math.sin(a)
    # rotasjon om +x i (y,z): α < 0 = mot veggen (form04: ned = (−sin α, −cos α))
    R = np.array([[c, sn], [-sn, c]])
    q = R @ p0
    return np.array([ys, akse_z]) + q


# sjekk konvensjonen mot form04: ved α = −105 skal ned peike mot veggen
_n = hovud_pkt(-105, zs, 0, 1.0) - hovud_pkt(-105, zs, 0, 0.0)
assert _n[0] > 0.9, _n


def gest_lam(m, yc, alfa, akse_z, T, x_hand=0.0):
    best = (math.inf, None)
    for s in (-bp / 2, bp / 2):
        P = hovud_pkt(alfa, akse_z, s, dd + tp / 2)
        r = P - np.array([ys, akse_z]); rn = np.linalg.norm(r)
        tang = np.array([-r[1], r[0]]) / rn
        for sg in (1, -1):
            F = sg * T / rn * tang
            Mf = (P[0] - yF0) * F[1] - P[1] * F[0]            # om framkanten, + = veltar fram
            Mb = (P[0] - yF1) * F[1] - P[1] * F[0]
            if Mf > 0:
                lam = m * g * (yc - yF0) / Mf
                if lam < best[0]: best = (lam, (alfa, 'framkant' if s > 0 else 'bakkant', 'fram', P[1]))
            if Mb < 0:
                lam = m * g * (yF1 - yc) / (-Mb)
                if lam < best[0]: best = (lam, (alfa, 'framkant' if s > 0 else 'bakkant', 'bak', P[1]))
    return best


for akse_lab, akse_z in (('tyngdepunktet', z_cg), ('LED-lina', zs)):
    for T in (0.20, 0.30):
        for lab, d in (('aleine', delar()), ('med skjerm', delar() + [SKJ])):
            m, yc, zc = tp_(d)
            # om LED-lina må handa òg lyfte plata (pendel), om tyngdepunktet berre friksjon
            pend = lambda al: 0.0 if akse_z == z_cg else m_pl * g * (dd + tp / 2) * abs(math.sin(math.radians(al)))
            w = min(gest_lam(m, yc, al, akse_z, T + pend(al)) for al in range(-105, 71, 5))
            res_c[f'gest|{akse_lab}|T{T}|{lab}'] = w[0]
            p(f'   gest om {akse_lab:13s} T {T:.2f} {lab:10s}: λ {w[0]:.2f} ved α {w[1][0]:+d}°, {w[1][1]}, veltar {w[1][2]}, handa i z {w[1][3]:.3f}')
m0, yc0, _ = tp_(delar())
T_lyft = 0.20 * gest_lam(m0, yc0, -105, z_cg, 0.20)[0]
p(f'   utan skjerm lyftar lampa når leddet krev {T_lyft:.2f} N·m (losrivingsmoment), handa på øvre plate-kant ved α −105°')
res_c['T_losriving_lyft'] = T_lyft
# pendel om LED-lina
d_pl = dd + tp / 2
for al in (-105, -90, 70):
    Tp = m_pl * g * d_pl * abs(math.sin(math.radians(al)))
    p(f'   pendel om LED-lina ved α {al:+d}°: {Tp:.3f} N·m (friksjon 0,20 held {"ikkje" if Tp > 0.2 else "ja"})')
res_c['T_pendel_105'] = m_pl * g * d_pl * math.sin(math.radians(105))
# fottjukn: λ ≥ 2 med rett kraftpunkt, utan skjerm
for T in (0.20, 0.30):
    for tt in range(3, 40):
        m, yc, _ = tp_(delar(tt / 1000))
        if min(gest_lam(m, yc, al, z_cg, T)[0] for al in range(-105, 71, 5)) >= 2: break
    # motorformel: F_tipp = m g d / zs >= 2 T/(bp/2)
    for tm in range(3, 40):
        m2, yc2, _ = tp_(delar(tm / 1000))
        if m2 * g * (yc2 - yF0) / zs >= 2 * T / (bp / 2): break
    p(f'   fot for λ ≥ 2, T {T:.2f}: {tt} mm alu ({m:.2f} kg) · motorformelen: {tm} mm')
    res_c[f'fot_T{T}'] = dict(rett_mm=tt, motor_mm=tm, masse=m)
    # alternativ: stålinnlegg bak i foten (y 0,55)
    m, yc, _ = tp_(delar())
    lam0 = min(gest_lam(m, yc, al, z_cg, T)[0] for al in range(-105, 71, 5))
    Mtrong = (2 / lam0 - 1) * m * g * (yc - yF0)
    p(f'      alternativ: {Mtrong / (g * (0.55 - yF0)):.2f} kg stål bak i foten (y 0,55) gjev same')
# 10 N i aksehøgd utan skjerm
m, yc, _ = tp_(delar())
need = 10 * z_cg - m * g * (yc - yF0)
p(f'   10 N mot brukar i aksen utan skjerm: manglar {need:.2f} N·m -> {need / (g * (0.55 - yF0)):.2f} kg bak i foten eller {need / (g * (0.432 - yF0)):.2f} kg midt i foten')

# --- tverrsnitt ---
h_, b_ = cw - ct, cf - ct / 2
J_U = (h_ + 2 * b_) * ct ** 3 / 3
Cw = ct * b_ ** 3 * h_ ** 2 / 12 * (3 * b_ + 2 * h_) / (6 * b_ + h_)
a_kv = math.sqrt(E * Cw / (Gs * J_U))
Am, pm = (cw - ct) * (cf - ct), 2 * ((cw - ct) + (cf - ct))
J_2 = 4 * Am ** 2 * ct / pm
J_15 = 4 * ((cw - 0.0015) * (cf - 0.0015)) ** 2 * 0.0015 / (2 * ((cw - 0.0015) + (cf - 0.0015)))
yU = cU                                                 # tyngdepunkt frå steget
I_sv = cw * ct ** 3 / 12 + cw * ct * (yU - ct / 2) ** 2 + 2 * (ct * (cf - ct) ** 3 / 12 + (cf - ct) * ct * (ct + (cf - ct) / 2 - yU) ** 2)
p(f'   U 100×30×2: A {A_U * 1e6:.0f} mm², J {J_U:.3e} m⁴ (GJ {Gs * J_U:.2f}), Cw {Cw:.3e} m⁶, a {a_kv:.3f} m, I_svak {I_sv:.3e}')
p(f'   lukka 100×30×2: J {J_2:.3e} ({J_2 / J_U:.0f}×), ×1,5: J {J_15:.3e} ({J_15 / J_U:.0f}×)')
Ls = za + cf - cU - tf
La = (cy + cf - cU) - ys
res_c.update(J_U=J_U, J_lukka2=J_2, J_lukka15=J_15, a_kv=a_kv, Ls=Ls, La=La)


def vri(Tq, Ll, GJ, kv=False):
    if kv:
        return Tq / GJ * (Ll - a_kv * math.tanh(Ll / a_kv))
    return Tq * Ll / GJ


for T in (0.20, 0.30):
    F = T / math.hypot(bp / 2, dd - (zs - z_cg))
    Tq = F * Lh / 2
    for lab, Ll in (('arbeid: framkant i enden ned -> armen vrir', La), ('stemning: øvre kant i enden mot brukar -> søyla vrir', Ls)):
        out = [vri(Tq, Ll, Gs * J_U) * Lh / 2 * 1e3, vri(Tq, Ll, Gs * J_U, True) * Lh / 2 * 1e3,
               vri(Tq, Ll, Gs * J_2) * Lh / 2 * 1e3, vri(Tq, Ll, Gs * J_15) * Lh / 2 * 1e3]
        res_c[f'vri|T{T}|{lab[:8]}'] = out
        p(f'   T {T:.2f} ({F:.2f} N, {Tq:.2f} N·m) {lab:52s}: U fri {out[0]:5.1f} · U kvelv. {out[1]:5.1f} · lukka 2 {out[2]:.3f} · lukka 1,5 {out[3]:.3f} mm i enden')
T10 = 10 * La
th10 = vri(T10, Ls, Gs * J_U)
p(f'   10 N sidevegs i hovudenden: søyla {T10:.2f} N·m -> {math.degrees(th10):.1f}°, {th10 * La * 1e3:.0f} mm; τ = T t/J {T10 * ct / J_U / 1e6:.0f} MPa')
I_z = m_hd * (Lh ** 2 / 12 + La ** 2) + rho * A_U * La ** 3 / 3
for lab, GJ in (('U fri', Gs * J_U), ('lukka 2', Gs * J_2), ('lukka 1,5', Gs * J_15)):
    kk = GJ / Ls
    p(f'   vridningssving om søyla, {lab:9s}: {math.sqrt(kk / I_z) / (2 * math.pi):5.1f} Hz (berre søyla; armbøying ikkje med)')
    res_c[f'f_Hz|{lab}'] = math.sqrt(kk / I_z) / (2 * math.pi)
W = (m_hd + 0.05) * g
ned = W * La ** 3 / (3 * E * I_sv) + W * La * Ls * La / (E * I_sv)
p(f'   nedbøying frå hovudvekta: {ned * 1e3:.3f} mm (arm + søylerotasjon, svak akse)')
res_c['ned_mm'] = ned * 1e3
# hovudet si eiga vridning: open renne 16×20×1,5 frå leddet (x 0,05) til enden
J_r = ((0.016 - 0.0015) + 2 * (0.020 - 0.00075)) * 0.0015 ** 3 / 3
for T in (0.20, 0.30):
    th = T * (Lh / 2 - 0.05) / (Gs * J_r)
    p(f'   renna åleine (GJ {Gs * J_r:.2f}): T {T:.2f} i enden -> {math.degrees(th):.2f}°, plate-kanten {th * bp / 2 * 1e3:.1f} mm')
# PMMA-plata
for lab, tt, EE, Lsp in (('3 mm, kinn i endane', 0.003, 3.0e9, 0.60), ('3 mm, kryp (E 2 GPa)', 0.003, 2.0e9, 0.60), ('6 mm, kinn i endane', 0.006, 3.0e9, 0.60)):
    q = 1190 * bp * (tt + 0.001) * g
    s = 5 * q * Lsp ** 4 / (384 * EE * bp * tt ** 3 / 12)
    hall = q * Lsp ** 3 / (24 * EE * bp * tt ** 3 / 12)
    p(f'   plate {lab:22s}: nedbøying {s * 1e3:5.1f} mm, d {dd * 1e3:.0f} -> {(dd + s) * 1e3:.0f} mm midt, helling ved kinnet {math.degrees(hall):.1f}°')
    res_c[f'plate|{lab}'] = s * 1e3

# --- kollisjon: hovudet mot armen over vippebana ---
y_arm0, z_arm = ys - 0.012, za
p(f'   arm: underkant z {z_arm:.3f} for y ≥ {y_arm0:.3f} (flensane ved x ±0,05; plata går gjennom heile x)')
kol = {}
for akse_lab, akse_z in (('LED-lina', zs), ('tyngdepunktet', z_cg)):
    first, zmax = None, -1
    for al in np.arange(0, -105.5, -0.5):
        for s in np.linspace(-bp / 2, bp / 2, 33):
            for w in (dd, dd + tp + 0.002):
                P = hovud_pkt(al, akse_z, s, w)
                if P[0] >= y_arm0:
                    zmax = max(zmax, P[1])
                    if P[1] >= z_arm and first is None: first = al
    P105 = max((hovud_pkt(-105, akse_z, s, dd) for s in (-bp / 2, bp / 2)), key=lambda q: q[1])
    kol[akse_lab] = dict(forste_treff=first, z_maks=zmax, inntrenging_mm=(zmax - z_arm) * 1e3, kant_105=list(P105))
    p(f'   vipp om {akse_lab:13s}: plata når armen ved α {first:+.1f}°; ved −105° står plate-kanten i y {P105[0]:.3f} z {P105[1]:.3f}; '
      f'høgaste punkt under armen {zmax:.3f} -> armen må {(zmax - z_arm) * 1e3:.0f} mm opp, eller hovudet ned')
res_c['kollisjon'] = kol
UT['c'] = res_c

# =============================== VARME ===========================================
p('\n== varme (Morgan: Nu = 0,48 Ra^¼ for Ra 1e4–1e7, 0,85 Ra^0,188 under; stråling 4εσT³)')
sig = 5.67e-8


def h_tot(Dh, dT, eps, Ta=298.15):
    Tf = Ta + dT / 2
    nu_a, al_a, k_a = 1.60e-5 * (Tf / 300) ** 1.75, 2.25e-5 * (Tf / 300) ** 1.75, 0.0263 * (Tf / 300) ** 0.85
    Ra = g / Tf * dT * Dh ** 3 / (nu_a * al_a)
    Nu = 0.48 * Ra ** 0.25 if Ra > 1e4 else 0.85 * Ra ** 0.188
    return Nu * k_a / Dh + eps * sig * ((Ta + dT) ** 2 + Ta ** 2) * (Ta + dT + Ta)


def flate_dT(q_per_m, A_per_m, Dh, eps):
    dT = 10.0
    for _ in range(50):
        dT = q_per_m / (h_tot(Dh, dT, eps) * A_per_m)
    return dT


LYS = 0.33
kj = json.load(open(os.path.join(os.path.dirname(HER), 'konsept.json'), encoding='utf-8'))
var = {}
A_ror = math.pi * D * (1 - 2 * beta / 360)
A_rn = 0.056
for key, Lz, eta_k, Aper, Dh in (('a', 0.60, 0.674, A_ror, D), ('b', 0.57, 0.674, A_ror, D), ('c', 0.60, 0.15, A_rn, A_rn / math.pi)):
    P = kj[key]['P_W']
    qled = P / Lz * (1 - LYS)
    qflate = P / Lz * (1 - LYS * eta_k) if key != 'c' else P / Lz * (1 - LYS + LYS * 0.15)
    for eps in (0.85, 0.10):
        Aeff = Aper
        if key == 'a':          # endane utan LED (0,26 m kvar side) som finne
            mm = math.sqrt(h_tot(Dh, 10, eps) / (200 * t))
            Aeff = Aper * (Lz + 2 * math.tanh(mm * 0.26) / mm) / Lz
        dT = flate_dT(qflate, Aeff, Dh, eps)
        Ts = 25 + dT + qled * 0.3
        var[f'{key}|eps{eps}'] = dict(W_per_m=P / Lz, dT=dT, T_lodd=Ts, h=h_tot(Dh, dT, eps))
        p(f'   ({key}) {P / Lz:4.1f} W/m, ε {eps:.2f}: h {h_tot(Dh, dT, eps):4.1f}, flate ΔT {dT:4.1f} K ({25 + dT:.0f} °C), LED-lodd ≈ {Ts:.0f} °C (R′ 0,3)')
# trygg W/m: (i) lodd ≤ 60 °C og (ii) flate ≤ 45 °C (ΔT 20, grep og hovud vert tekne i)
for lab, Aper, Dh, frac in (('røyr Ø44×1,2 (spalte 50°)', A_ror, D, 1 - LYS * 0.674), ('renne 16×20, berre utsida', A_rn, A_rn / math.pi, 1 - LYS + LYS * 0.15)):
    for eps in (0.85, 0.10):
        q_touch = h_tot(Dh, 20, eps) * Aper * 20 / frac
        lo, hi = 0.1, 300
        for _ in range(60):
            q = (lo + hi) / 2
            if 25 + flate_dT(q * frac, Aper, Dh, eps) + q * (1 - LYS) * 0.3 <= 60: lo = q
            else: hi = q
        var[f'trygg|{lab}|eps{eps}'] = dict(beroering=q_touch, lodd60=lo)
        p(f'   trygg {lab:28s} ε {eps:.2f}: {q_touch:4.0f} W/m (flate 45 °C) · {lo:4.0f} W/m (lodd 60 °C)')
# motorkriteriet: arealet som trengst med rett h og ΔT 20
for key in 'abc':
    P = kj[key]['P_W']
    p(f'   ({key}) A ≥ P/(hΔT): h 10 ΔT 30 -> {P / 300 * 1e4:.0f} cm² · h 6 (blank) ΔT 20 -> {P / 120 * 1e4:.0f} cm² · motoren har {kj[key]["A_kjol_cm2"]:.0f}')
UT['varme'] = var


def rein(o):
    if isinstance(o, dict): return {str(kk): rein(v) for kk, v in o.items()}
    if isinstance(o, (list, tuple, np.ndarray)): return [rein(v) for v in o]
    if isinstance(o, (float, np.floating)): return None if not math.isfinite(float(o)) else round(float(o), 5)
    return o


json.dump(rein(UT), open(os.path.join(HER, 'mekanikk_kontroll.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
p('\n-> mekanikk_kontroll.json')
