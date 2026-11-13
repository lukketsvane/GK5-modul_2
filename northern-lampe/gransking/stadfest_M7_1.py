# -*- coding: utf-8 -*-
"""stadfest_M7_1.py · motbevisar 1 for M7 (svikt-raden i konsept.md samanliknar ulike lastfall).
Eigen 3D-rammeløysar (12×12 bjelkeelement, St. Venant-vridning) i staden for einingslast-integralet til granskaren.
Kvelving i open U er lagd til med handformel (fri / hindra i rota / hindra i begge endar).
Frå motorane: berre val.arm_path og B_KROK (geometrien til armen i (b)); resten er skrive inn frå koden.
Køyr: PYTHONIOENCODING=utf-8 python stadfest_M7_1.py  (under 2 s)
"""
import os, sys, math, json
import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form01')); sys.path.insert(0, os.path.join(ROOT, 'form02'))
E, nu = 70e9, 0.33
G = E / (2 * (1 + nu))
UT = {}


def p(*a):
    print(*a, flush=True)


# ---------------- 3D-ramme ----------------
def kloc(A, Iy, Iz, J, L, Ee=E, Gg=G):
    k = np.zeros((12, 12))
    k[0, 0] = k[6, 6] = Ee * A / L; k[0, 6] = k[6, 0] = -Ee * A / L
    k[3, 3] = k[9, 9] = Gg * J / L; k[3, 9] = k[9, 3] = -Gg * J / L
    a, b, c, d = 12 * Ee * Iz / L ** 3, 6 * Ee * Iz / L ** 2, 4 * Ee * Iz / L, 2 * Ee * Iz / L
    for (i, j, v) in ((1, 1, a), (1, 5, b), (1, 7, -a), (1, 11, b), (5, 5, c), (5, 7, -b), (5, 11, d), (7, 7, a), (7, 11, -b), (11, 11, c)):
        k[i, j] = k[j, i] = v
    a, b, c, d = 12 * Ee * Iy / L ** 3, 6 * Ee * Iy / L ** 2, 4 * Ee * Iy / L, 2 * Ee * Iy / L
    for (i, j, v) in ((2, 2, a), (2, 4, -b), (2, 8, -a), (2, 10, -b), (4, 4, c), (4, 8, b), (4, 10, d), (8, 8, a), (8, 10, b), (10, 10, c)):
        k[i, j] = k[j, i] = v
    return k


def los(nodar, el, fast, laster, Gg=G):
    """nodar (n,3); el: (i, j, A, Iy, Iz, J, ref) der ref gjev lokal y; fast: nodeindeksar heilt fastlåste; laster: {node: (Fx,Fy,Fz)}."""
    n = len(nodar)
    K = np.zeros((6 * n, 6 * n))
    for (i, j, A, Iy, Iz, J, ref) in el:
        dx = nodar[j] - nodar[i]; L = np.linalg.norm(dx); ex = dx / L
        ez = np.cross(ex, ref); ez /= np.linalg.norm(ez); ey = np.cross(ez, ex)
        R = np.array([ex, ey, ez]); T = np.kron(np.eye(4), R)
        kg = T.T @ kloc(A, Iy, Iz, J, L, Gg=Gg) @ T
        idx = np.r_[6 * i:6 * i + 6, 6 * j:6 * j + 6]
        K[np.ix_(idx, idx)] += kg
    F = np.zeros(6 * n)
    for nd, f in laster.items():
        F[6 * nd:6 * nd + 3] += f
    fri = np.setdiff1d(np.arange(6 * n), np.concatenate([np.arange(6 * f, 6 * f + 6) for f in fast]))
    u = np.zeros(6 * n)
    u[fri] = np.linalg.solve(K[np.ix_(fri, fri)], F[fri])
    return u.reshape(n, 6)


STIV = (1e-2, 1e-4, 1e-4, 1e-4)          # A, Iy, Iz, J for stive lenkjer


def ror(D, t):
    d = D - 2 * t
    I = math.pi / 64 * (D ** 4 - d ** 4)
    return math.pi / 4 * (D ** 2 - d ** 2), I, I, 2 * I


def forsk(u, nd, f):
    f = np.asarray(f, float)
    return float(u[nd, :3] @ f / np.linalg.norm(f) * 1e3), float(np.linalg.norm(u[nd, :3]) * 1e3)


F_FING = 0.08 / 0.026                    # T_DET / grepradius, same tal som motoren brukar i stabilitet()

# ====================== (a) bru ======================
p('== (a) bru (tal_bru(15): hp 0,62, a 0,15, L 1,12)')
hp, a_, Dl, tl, L = 0.62, 0.15, 0.020, 0.0015, 1.12
Al, Il, _, Jl = ror(Dl, tl)
Lleg = math.hypot(hp, a_)
sv_motor = (10.0 / 4) * Lleg ** 3 / (3 * E * Il) * 1e3
p(f'motor tal(): (F_PUSH/4)·L³/(3EI) = {sv_motor:.3f} mm  (konsept.json 0,823) -> 10 N i x på apex, ut av A-planet')
xe = L / 2 + 0.016
yp = 0.18
nod = np.array([[xe, yp - a_, 0.0], [xe, yp + a_, 0.0], [xe, yp, hp], [xe + 0.029, yp, hp + 0.026], [xe + 0.029, yp - 0.026, hp]])
el = [(0, 2, Al, Il, Il, Jl, np.array([1.0, 0, 0])), (1, 2, Al, Il, Il, Jl, np.array([1.0, 0, 0])),
      (2, 3, *STIV, np.array([0, 0, 1.0])), (2, 4, *STIV, np.array([0, 0, 1.0]))]
res_a = {}
for lab, nd, f in (('10 N i x på apex (motoren sitt lastfall)', 2, (10.0, 0, 0)),
                   ('finger 3,08 N i y øvst på grepet (fram/bak)', 3, (0, F_FING, 0)),
                   ('finger 3,08 N i z framme på grepet (ned)', 4, (0, 0, -F_FING))):
    u = los(nod, el, [0, 1], {nd: f})
    dl, dt = forsk(u, nd, f)
    res_a[lab] = dl
    p(f'   ein A-bukk, føter fast (som motoren): {lab:44s}: {dl:.4f} mm langs krafta')
UT['a'] = res_a

# ====================== (b) krok ======================
p('\n== (b) krok, arm frå val.arm_path(B_KROK), røyr t 1,5')
import val as V2
B = V2.B_KROK
pts, H = V2.arm_path(B)
m_tube = V2.RHO_ALU * math.pi * 2 * B['R'] * B['t_bow'] * B['L'] * (1 - B['k'] * B['beta'] / 180)
TA = V2.tube_arm(B, m_tube + 0.20)
p(f"motor tube_arm(): D {TA['D'] * 1e3:.0f} mm, svikt i planet {TA['svikt']:.3f}, ut av planet {TA['svikt_x']:.3f} mm (berre EI, 3 N i x i spissen)")
xyz = np.c_[np.zeros(len(pts)), pts]
_, idx_u = np.unique(np.round(xyz, 9), axis=0, return_index=True)
xyz = xyz[np.sort(idx_u)]
i_spiss = int(np.argmin(np.linalg.norm(xyz - [0, B['yp'], H], axis=1)))
nav = len(xyz) - 1
ekstra = np.array([[0, B['yp'], B['hp']], [0.335, B['yp'], B['hp'] + 0.026], [0.335, B['yp'], B['hp']]])
nodb = np.r_[xyz, ekstra]
i_navs, i_gtopp, i_grep = nav + 1, nav + 2, nav + 3
res_b = {}
for D in (0.023, 0.025):
    A, I, _, J = ror(D, 0.0015)
    el = [(i, i + 1, A, I, I, J, np.array([1.0, 0, 0])) for i in range(nav)]
    el += [(nav, i_navs, *STIV, np.array([1.0, 0, 0])), (i_navs, i_gtopp, *STIV, np.array([0, 0, 1.0])), (i_navs, i_grep, *STIV, np.array([0, 0, 1.0]))]
    rad = {}
    for lab, nd, f, Gg in (('3 N i x i spissen, berre bøying (G stor)', i_spiss, (3.0, 0, 0), G * 1e6),
                           ('3 N i x i spissen, med vridning', i_spiss, (3.0, 0, 0), G),
                           ('3 N i x i grepet, med vridning', i_grep, (3.0, 0, 0), G),
                           ('finger 3,08 N i y øvst på grepet', i_gtopp, (0, -F_FING, 0), G),
                           ('finger 3,08 N i z på grepet', i_grep, (0, 0, -F_FING), G)):
        u = los(nodb, el, [0], {nd: f}, Gg=Gg)
        dl, dt = forsk(u, nd, f)
        rad[lab] = dl
        p(f'   Ø{D * 1e3:.0f}: {lab:42s}: {dl:.3f} mm')
    res_b[f'{D * 1e3:.0f}'] = rad
UT['b'] = res_b

# ====================== (c) prisme ======================
p('\n== (c) prisme FINAL (ys 0,22, zs 0,70, L 0,60, bp 0,16, d 0,05), U 100×30×2')
ys, zs, Lh, bp, d = 0.22, 0.70, 0.60, 0.16, 0.05
CW, CF, CT, CY = 0.10, 0.03, 0.002, 0.512
za = zs + 0.03
L_arm = CY + CF - ys
A_col = (CW + 2 * CF) * CT
c = (2 * CF * CT * CF / 2 + CW * CT * CT / 2) / A_col
I_svak = 2 * (CT * CF ** 3 / 12 + CT * CF * (CF / 2 - c) ** 2) + CW * CT ** 3 / 12 + CW * CT * (c - CT / 2) ** 2
I_sterk = CT * CW ** 3 / 12 + 2 * (CF - CT) * CT * (CW / 2 - CT / 2) ** 2
J_U = ((CW - CT) + 2 * (CF - CT / 2)) * CT ** 3 / 3
h_, b_ = CW - CT, CF - CT / 2
Cw = CT * b_ ** 3 * h_ ** 2 / 12 * (3 * b_ + 2 * h_) / (6 * b_ + h_)
a_kv = math.sqrt(E * Cw / (G * J_U))
F_g = 0.20 / (bp / 2)
a2 = L_arm + bp / 2
sv_mot = (F_g * L_arm ** 3 / 3 + (F_g * a2) * za * a2) / (E * I_svak) * 1e3
p(f'I_svak {I_svak:.3e}, I_sterk {I_sterk:.3e}, J {J_U:.3e} (GJ {G * J_U:.2f} N·m²), Cw {Cw:.3e}, a {a_kv:.3f} m')
p(f'motor tal_mek(): F_g = T_FRIK/(bp/2) = {F_g:.2f} N i x 0, sv = {sv_mot:.3f} mm (konsept.json 0,194)')

# ramme: søylefot fast, søyletopp, armende, stiv lenkje til lastpunkt
yc, zt = CY + CF - c, za + CF - c
nodc0 = [[0, yc, 0.007], [0, yc, zt], [0, ys, zt], [0, ys, zs]]


def ramme_c(lastpkt, f, Jv=J_U, Gg=G, Iv=None, Is=None, Av=None):
    Iv, Is, Av = Iv or I_svak, Is or I_sterk, Av or A_col
    nod = np.array(nodc0 + [lastpkt], float)
    ref = np.array([1.0, 0, 0])
    el = [(0, 1, Av, Iv, Is, Jv, ref), (1, 2, Av, Iv, Is, Jv, ref),
          (2, 3, *STIV, np.array([0, 1.0, 0])), (3, 4, *STIV, np.array([0, 0, 1.0]) if abs(lastpkt[0]) > 1e-9 or True else ref)]
    u = los(nod, el, [0], {4: f}, Gg=Gg)
    return forsk(u, 4, f)


def kant(alfa, x, ovre):
    """plate-kant ved vinkel alfa (som geometri(): rotasjon om LED-lina), tangentiell kraftretning om tyngdepunktaksen."""
    a = math.radians(alfa)
    ned = np.array([0, -math.sin(a), -math.cos(a)]); fram = np.array([0, -math.cos(a), math.sin(a)])
    c0 = np.array([0, ys, zs]); top = c0 + d * ned
    k1, k2 = top - bp / 2 * fram, top + bp / 2 * fram
    if ovre:                                   # stemning: øvre kant
        k = k1 if k1[2] > k2[2] else k2
    else:                                      # arbeid: framkanten (minst y, mot brukaren)
        k = k1 if k1[1] < k2[1] else k2
    piv = c0 + 0.033 * ned
    r = k - piv; t = np.cross([1.0, 0, 0], r); t /= np.linalg.norm(t)
    return np.array([x, k[1], k[2]]), t, np.linalg.norm(r)


res_c = {}
for T in (0.20, 0.30):
    for lab, alfa, ovre in (('arbeid, framkant', 0.0, False), ('stemning, øvre kant', -105.0, True)):
        for x in (0.0, 0.30):
            P, t, r = kant(alfa, x, ovre)
            F = T / r
            dl, dt = ramme_c(P, F * t)
            # kvelving: skaler vridningsdelen. Vridningsdelen = rammeløysing minus same løysing med stor GJ.
            dl_stiv, _ = ramme_c(P, F * t, Gg=G * 1e6)
            dv = dl - dl_stiv
            Lv = (zt - 0.007) if alfa < -50 else (yc - ys)
            r_rot = Lv - a_kv * math.tanh(Lv / a_kv)
            r_beg = Lv - 2 * a_kv * math.tanh(Lv / (2 * a_kv))
            out = dict(F_N=F, fri=dl, kvelv_rot=dl_stiv + dv * r_rot / Lv, kvelv_begge=dl_stiv + dv * r_beg / Lv, berre_boying=dl_stiv)
            res_c[f'T{T}|{lab}|x{x}'] = out
            p(f'   T {T:.2f} {lab:20s} x {x:.2f} (F {F:.2f} N): fri {dl:6.2f} · kvelving hindra i rota {out["kvelv_rot"]:5.2f} · i begge endar {out["kvelv_begge"]:5.2f} · utan vridning {dl_stiv:.3f} mm')
# lukka 100×30×1,5 (Bredt)
Am = (CW - 0.0015) * (CF - 0.0015)
J15 = 4 * Am ** 2 * 0.0015 / (2 * ((CW - 0.0015) + (CF - 0.0015)))
for lab, alfa, ovre in (('arbeid, framkant', 0.0, False), ('stemning, øvre kant', -105.0, True)):
    P, t, r = kant(alfa, 0.30, ovre)
    dl, _ = ramme_c(P, 0.20 / r * t, Jv=J15)
    Ib_v = (CW * CF ** 3 - (CW - 0.003) * (CF - 0.003) ** 3) / 12
    Ib_s = (CF * CW ** 3 - (CF - 0.003) * (CW - 0.003) ** 3) / 12
    db, _ = ramme_c(P, 0.20 / r * t, Jv=J15, Iv=Ib_v, Is=Ib_s, Av=2 * (CW + CF) * 0.0015)
    dbt, _ = ramme_c(P, 0.20 / r * t, Jv=J15, Iv=Ib_v, Is=Ib_s, Av=2 * (CW + CF) * 0.0015, Gg=G * 1e6)
    res_c[f'lukka15|{lab}|x0.3'] = dict(I_som_U=dl, boks=db, boks_berre_vridning=db - dbt)
    p(f'   lukka 100×30×1,5 (J {J15:.2e}): {lab} x 0,30, T 0,20: I som U {dl:.3f} · rett boks-I ({Ib_v:.2e}) {db:.3f} mm, av det vridning {db - dbt:.3f} mm')
# renna i hovudet (open 16×20×1,5) frå leddet x 0,05 til enden, T 0,20
J_r = ((0.016 - 0.0015) + 2 * (0.020 - 0.00075)) * 0.0015 ** 3 / 3
th_r = 0.20 * (Lh / 2 - 0.05) / (G * J_r)
p(f'   renna (GJ {G * J_r:.2f}): T 0,20 frå x 0,05 til 0,30 vrir {math.degrees(th_r):.2f}°, plate-kanten {th_r * bp / 2 * 1e3:.1f} mm (kjem i tillegg)')
res_c['renne_mm'] = th_r * bp / 2 * 1e3
UT['c'] = res_c

p('\n' + json.dumps(UT, ensure_ascii=False, default=float)[:3000])     # berre utskrift; skriv ingen filer
