# -*- coding: utf-8 -*-
"""Motbevis M5: gestkraft i (c). Brukar motoren sin eigen massemodell (tal_mek-delane) og
reknar momentet frå ei tangentiell handkraft T/r på plate-kantane om vippeaksen i tyngdepunktet til hovudet,
sveipt over α, mot fram- og bakkanten av foten. Køyr: PYTHONIOENCODING=utf-8 python stadfest_M5_1.py (< 5 s)."""
import os, sys, math
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form04'))
import felles as fe
import motor as mo

B = mo.FINAL
g = fe.G
mk = mo.tal_mek(B)
print(f"motor: t_fot {mk['t_fot']*1e3:.0f} mm, masse {mk['st_a']['masse_kg']:.3f} kg, F_tipp {mk['st_a']['F_tipp_N']:.2f} N, F_g {mk['F_g']:.2f} N")

za = B['zs'] + 0.03
m_plate, m_stong = mo.hovud_masse(B)
A_col = (mo.COL_W + 2 * mo.COL_F) * mo.COL_T
L_arm = mo.COL_Y + mo.COL_F - B['ys']
m_col, m_arm = mo.RHO_ALU * A_col * za, mo.RHO_ALU * A_col * L_arm
deler = [(m_plate, np.array([0, B['ys'], B['zs'] - B['d']])), (m_stong, np.array([0, B['ys'], B['zs']])),
         (m_arm, np.array([0, B['ys'] + L_arm / 2, za])), (m_col, np.array([0, mo.COL_Y + mo.COL_F / 2, za / 2]))]
fy0, fy1 = mo.fot_y()
h = mo.akse_under_led(B)
A = np.array([B['ys'], B['zs'] - h])
print(f"akse (tyngdepunkt hovud) z {A[1]:.4f}, {h*1e3:.1f} mm under LED-lina; fot y {fy0:.3f}–{fy1:.3f}")


def masse(t, ekstra=None):
    p = deler + [(mo.RHO_ALU * mo.FOT_XY[0] * mo.FOT_XY[1] * t + 0.15, np.array([0, (fy0 + fy1) / 2, t / 2]))]
    if ekstra: p = p + [ekstra]
    m = sum(x for x, _ in p); c = sum(x * q for x, q in p) / m
    return m, c


def verst(T, alfa_deg, w_list=(B['d'], B['d'] + B['tp'])):
    """største velte-moment framover og bakover over α og plate-kantane (begge flater), kraft tangentiell T/r."""
    Mf, Mb, kf = 0.0, 0.0, None
    for al in alfa_deg:
        a = math.radians(al)
        ned = np.array([-math.sin(a), -math.cos(a)]); fram = np.array([-math.cos(a), math.sin(a)])
        for s in (-B['bp'] / 2, B['bp'] / 2):
            for w in w_list:
                P = A + (w - h) * ned + s * fram
                r = P - A; rn = np.linalg.norm(r)
                tang = np.array([-r[1], r[0]]) / rn
                for sg in (1, -1):
                    F = sg * T / rn * tang
                    m_f = (P[0] - fy0) * F[1] - P[1] * F[0]
                    m_b = (P[0] - fy1) * F[1] - P[1] * F[0]
                    if m_f > Mf: Mf, kf = m_f, (al, P[1], rn)
                    Mb = min(Mb, m_b)
    return Mf, -Mb, kf


m7, c7 = masse(mk['t_fot'])
R7 = m7 * g * (c7[1] - fy0)
print(f"rettande moment om framkanten, 7 mm: {R7:.3f} N·m (m {m7:.3f} kg, y {c7[1]:.4f}); motorformel F_g·zs·2 = {2*mk['F_g']*B['zs']:.3f}")
for lab, rng in (('gestbana −105..+30', range(-105, 31, 1)), ('heile ALFA −130..+100', range(-130, 101, 1))):
    for T in (0.20, 0.24, 0.30):
        Mf, Mb, kf = verst(T, rng)
        lam = R7 / Mf
        Rb = m7 * g * (fy1 - c7[1])
        print(f"  {lab:22s} T {T:.2f}: M fram {Mf:.3f} N·m (α {kf[0]:+d}°, z {kf[1]:.3f}, r {kf[2]*1e3:.1f} mm), λ fram {lam:.2f}; "
              f"M bak {Mb:.3f}, λ bak {Rb/Mb:.2f}; motorens moment F_g·zs = {T/(B['bp']/2)*B['zs']:.3f} (forhold {Mf/(T/(B['bp']/2)*B['zs']):.3f})")

# fot for λ ≥ 2 med rett kraftpunkt
rng = range(-105, 31, 1)
for T in (0.20, 0.30):
    Mf, _, _ = verst(T, rng)
    for tm in range(3, 40):
        m, c = masse(tm / 1000)
        if m * g * (c[1] - fy0) >= 2 * Mf: break
    st = (2 * Mf - R7) / (g * (0.55 - fy0))
    print(f"T {T:.2f}: fot {tm} mm -> {m:.3f} kg (+{m - m7:.3f}); alternativ 7 mm + {st:.3f} kg bak i foten (y 0,55) -> {m7 + st:.3f} kg")
print(f"losriving som lyftar (λ = 1), 7 mm: {0.20 * R7 / verst(0.20, rng)[0]:.3f} N·m; 1,2–1,5 × 0,20 = 0,24–0,30")
