"""Motprov av P3 (toppluminans i ansiktslyset til (c)).

Uavhengig av prisme.py: bakoversporing frå auga gjennom ei tynn plate (fasett τ(s) frå motoren på undersida,
flat overside 3 mm over), ingen stigeveggar, Snell og Fresnel på vektorform i 3D, renneopning ±8 mm ved z 5 mm.
Mattering som motoren: gauss σ på profilvinkelen ut av plata (kvadratur, ikkje Monte Carlo).
L(P) = T · L_LED · treff, L_LED = 1/(π w L) per LED-lumen.
Sjølvkonsistent Φ150: E_v ved midtauga = ∫ L cos dΩ over plata (same modell), Φ150 = 150 / E_v.
Køyr: PYTHONIOENCODING=utf-8 python stadfest_P3_1.py   (under 1 min)
"""
import os, sys, math, json, time
import numpy as np

ROOT = r'C:\Users\Iver\Documents\northern-lampe'
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form04'))
import felles as fe
import motor as mo

t0 = time.time()
B = mo.FINAL
O = mo.optikk(B)
n = mo.N_PMMA
d, tp, bp, L, ys, zs = B['d'], B['tp'], B['bp'], B['L'], B['ys'], B['zs']
ZB = d + tp
CW, ZC = 0.008, 0.005
phi_i = np.arcsin(np.sin(O['ph']) / n)
S_BOT = d * np.tan(O['ph']) + tp * np.tan(phi_i)          # rilla ligg der strålen går ut av botnen
TAU = O['tau']

S = mo.sok(B)
a_f = S['face']['s']
L150_motor, Phi150_motor, Le_motor = S['L150'], S['Phi150'], S['face']['Le']
print(f'motor: alfa_ansikt {math.degrees(a_f):.1f}°, Phi150 {Phi150_motor:.1f} lm, Le {Le_motor:.3f} cd/m² per lm, L150 {L150_motor:.1f}')


def refr(k, N, n1, n2):
    """k (…,3) innfall, N (…,3) normal mot innfallssida. Returnerer (t, T, ok)."""
    c1 = -(k * N).sum(-1)
    r = n1 / n2
    kk = 1 - r * r * (1 - c1 * c1)
    ok = kk > 0
    ct = np.sqrt(np.clip(kk, 0, None))
    t = r * k + (r * c1 - ct)[..., None] * N
    rs = ((n1 * c1 - n2 * ct) / (n1 * c1 + n2 * ct)) ** 2
    rp = ((n1 * ct - n2 * c1) / (n1 * ct + n2 * c1)) ** 2
    return t, np.where(ok, 1 - 0.5 * (rs + rp), 0.0), ok


fram = np.array([0, -math.cos(a_f), math.sin(a_f)]); ned = np.array([0, -math.sin(a_f), -math.cos(a_f)])
Oax = np.array([0, ys, zs])


def lok(e):
    v = e - Oax
    return np.array([e[0], v @ fram, v @ ned])


SG = np.arange(-bp / 2 + 5e-5, bp / 2, 1e-4)               # 0,1 mm
XG = np.linspace(-L / 2 + 0.005, L / 2 - 0.005, 60)          # 1 cm


def kart(e_world, w, sig_deg, nq=41):
    """L-kart (len XG, len SG) per LED-lumen [cd/m2/lm] sett frå auget, og E_v-bidrag."""
    el = lok(e_world)
    if sig_deg > 0:
        dq = np.linspace(-3.5, 3.5, nq); gw = np.exp(-0.5 * dq ** 2); gw /= gw.sum(); dq = np.radians(dq * sig_deg)
    else:
        dq, gw = np.zeros(1), np.ones(1)
    tau = np.interp(SG, S_BOT, TAU)
    Nf = np.c_[np.zeros_like(tau), np.sin(tau), np.cos(tau)]       # fasettnormal mot lufta (ned)
    Lled = 1 / (math.pi * w * L)
    M = np.zeros((len(XG), len(SG))); Ev = 0.0
    for i, x in enumerate(XG):
        P = np.c_[np.full_like(SG, x), SG, np.full_like(SG, ZB)]
        b = P - el; r = np.linalg.norm(b, axis=1); b /= r[:, None]     # bakoverstråle, går opp (bz < 0)
        c, s_ = np.cos(dq)[:, None], np.sin(dq)[:, None]
        bb = np.stack([np.broadcast_to(b[:, 0], (len(dq), len(SG))), b[:, 1] * c + b[:, 2] * s_, -b[:, 1] * s_ + b[:, 2] * c], -1)
        t1, T1, ok1 = refr(bb, Nf[None], 1.0, n)
        lam = (d - ZB) / t1[..., 2]
        p1 = P[None] + lam[..., None] * t1
        ok = ok1 & (lam > 0) & (np.abs(p1[..., 1]) <= bp / 2)
        t2, T2, ok2 = refr(t1, np.array([0, 0, 1.0]), n, 1.0)
        ok &= ok2 & (t2[..., 2] < 0)
        lc = (ZC - d) / t2[..., 2]; sc = p1[..., 1] + lc * t2[..., 1]
        ok &= np.abs(sc) < CW
        l0 = (0 - d) / t2[..., 2]; u = p1[..., 1] + l0 * t2[..., 1]; xu = p1[..., 0] + l0 * t2[..., 0]
        ok &= (np.abs(u) <= w / 2) & (np.abs(xu) <= L / 2)
        M[i] = (gw[:, None] * np.where(ok, T1 * T2, 0.0)).sum(0) * Lled
        # E_v ved auget: dΩ = dA·|bz|/r², cos mot andletsnormalen (+y i verda)
        ce = np.clip(b[:, 1] * fram[1] + b[:, 2] * ned[1], 0, None)
        Ev += (M[i] * ce * np.abs(b[:, 2]) / r ** 2).sum() * 1e-4 * (XG[1] - XG[0])
    return M, Ev


def glid(v, k):
    return np.convolve(v, np.ones(k) / k, mode='same')


UT = {}
for w in (0.005, 0.010):
    for sig in (0.0, 4.0, 6.0, 8.0):
        rows = {}
        Ev_mid = None
        for ie, e in enumerate(fe.EYES):
            M, Ev = kart(e, w, sig)
            if ie == 0:
                Ev_mid = Ev
            rows[ie] = M
        Phi150 = 150 / Ev_mid
        res = dict(Phi150_eigen=Phi150, L_LED_eigen=Phi150 / (math.pi * w * L))
        for lab, ph in (('eigen', Phi150), ('motor', Phi150_motor)):
            t1 = max(max(glid(row, 10)[5:-5].max() for row in rows[ie]) for ie in rows) * ph
            t10 = max(max(glid(row, 100)[50:-50].max() for row in rows[ie]) for ie in rows) * ph
            mid = rows[0][np.argmin(np.abs(XG))]
            res[lab] = dict(topp_1mm=t1, topp_1cm=t10, topp_1mm_midtauga_x0=glid(mid, 10).max() * ph,
                            snitt_plata_midtauga=rows[0].mean() * ph,
                            s_topp_cm=float(SG[np.argmax(glid(mid, 10))] * 100))
        UT[f'w{int(w*1000)}_sig{int(sig)}'] = res
        e_, m_ = res['eigen'], res['motor']
        print(f'w {w*1000:.0f} mm σ {sig:.0f}°: Φ150 eigen {Phi150:.1f} lm (L_LED {res["L_LED_eigen"]:.0f}) | '
              f'topp 1 mm {e_["topp_1mm"]:.0f} (Φmotor {m_["topp_1mm"]:.0f}), 1 cm {e_["topp_1cm"]:.0f} ({m_["topp_1cm"]:.0f}), '
              f'snitt {e_["snitt_plata_midtauga"]:.0f} ({m_["snitt_plata_midtauga"]:.0f}), s_topp {e_["s_topp_cm"]:.2f} cm')

UT['motor'] = dict(alfa_ansikt=math.degrees(a_f), Phi150=Phi150_motor, Le_per_lm=Le_motor, L150=L150_motor)
print(f'{time.time() - t0:.0f} s')
