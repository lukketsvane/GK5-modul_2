"""Motbevisar 1 for M6: søkk PMMA-plata i (c) mellom kinna, og kva gjer det med lyset?
1) Eigen mekanikk: verkeleg rilletverrsnitt (deling 0,5 / 1 mm) gjev areal og I; fritt opplagd / innspent; kryp.
2) Optikk: rillene τ(s) er rekna for d = 50 mm. Plata midt heng lågare (d'). Snell framover per stråle, Fresnel, TIR,
   og lys som slepp forbi platekanten (renna klipper ved 58°, plata dekkjer berre atan(80/d')).
3) 3D med søkkprofilen langs x: kvart lineelement får lokal d(x). Em, U0, lm for 500 lx på oppgåvesona, mot flat plate.
"""
import os, sys, math, json
import numpy as np
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form04'))
import felles as fe
import motor as M

B = dict(M.FINAL)
O = M.optikk(B)
n = M.N_PMMA
g = 9.81
out = {}

# ---------------- 1) mekanikk ----------------
def snitt(pitch, tp=B['tp'], bp=B['bp']):
    """Tverrsnitt (y–z) med sagtann under 3 mm plate: areal per m og I om eige tyngdepunkt."""
    ny = int(round(bp / pitch))
    sub = 40
    ys = (np.arange(ny * sub) + 0.5) / (ny * sub) * bp - bp / 2
    dy = bp / (ny * sub)
    tau = np.interp(ys, O['s'], O['tau'])
    h = np.abs(np.tan(tau)) * pitch
    frac = ((ys + bp / 2) % pitch) / pitch
    hloc = np.where(tau > 0, h * (1 - frac), h * frac)      # rampe over kvar deling
    t = tp + hloc                                           # tjukn frå oversida (z = 0) og ned
    A = (t * dy).sum()
    zc = ((t * dy) * t / 2).sum() / A
    I = (dy * t ** 3 / 12 + t * dy * (t / 2 - zc) ** 2).sum()
    return A, I, float(h.max()), float((t - tp).mean())

E_s, E_k, NU = 3.0e9, 2.0e9, 0.37
L = B['L']
rows = []
for lab, pitch in (('flat 3 mm (granskar)', None), ('riller deling 1,0 mm', 0.001), ('riller deling 0,5 mm', 0.0005)):
    if pitch is None:
        A, I, hm, tm = B['bp'] * 0.003, B['bp'] * 0.003 ** 3 / 12, 0.0, 0.0
        q = M.RHO_PMMA * B['bp'] * 0.004 * g                 # granskaren: masse som 4 mm, stivleik som 3 mm
    else:
        A, I, hm, tm = snitt(pitch)
        q = M.RHO_PMMA * A * g
    for Elab, E in (('kort tid', E_s), ('kryp E 2 GPa', E_k)):
        EI = E * I
        ss = 5 * q * L ** 4 / (384 * EI)                    # fritt opplagd i kinna
        cl = q * L ** 4 / (384 * EI)                         # fast innspent i kinna
        ss_p = ss * (1 - NU ** 2)                            # øvre grense for platestivleik (sylindrisk bøying)
        hall = q * L ** 3 / (24 * EI)
        rows.append(dict(snitt=lab, E=Elab, q_N_m=q, I_mm4=I * 1e12, rille_maks_mm=hm * 1e3, rille_snitt_mm=tm * 1e3,
                         fritt_mm=ss * 1e3, fritt_plate_mm=ss_p * 1e3, innspent_mm=cl * 1e3, hall_deg=math.degrees(hall)))
print('1) Nedbøying midt, PMMA-plate 0,60 m mellom kinna (E 3,0 / 2,0 GPa)')
for r in rows:
    print(f"   {r['snitt']:24s} {r['E']:12s} q {r['q_N_m']:.2f} N/m  I {r['I_mm4']:6.0f} mm4  rille maks {r['rille_maks_mm']:.2f} snitt {r['rille_snitt_mm']:.2f} mm"
          f" | fritt {r['fritt_mm']:5.1f} (plate {r['fritt_plate_mm']:4.1f}) innspent {r['innspent_mm']:4.1f} mm, helling {r['hall_deg']:.1f}°")
out['mekanikk'] = rows
# kontroll av granskartala
q4 = M.RHO_PMMA * 0.16 * 0.004 * g
EI3 = 3e9 * 0.16 * 0.003 ** 3 / 12
print(f"   granskar: 5qL4/384EI = {5 * q4 * L ** 4 / (384 * EI3) * 1e3:.2f} mm, kryp {5 * q4 * L ** 4 / (384 * EI3) * 1.5e3:.2f} mm, helling {math.degrees(q4 * L ** 3 / (24 * EI3)):.2f}°;"
      f" 6 mm: +{M.RHO_PMMA * 0.6 * 0.16 * 0.003:.3f} kg (ikkje 0,57)")
sig = q4 * L ** 2 / 8 * 0.0015 / (0.16 * 0.003 ** 3 / 12)
print(f"   bøyespenning midt {sig / 1e6:.2f} MPa (kryp ved < 5 MPa: E(1 år) ≈ 2–2,5 GPa er rimeleg)")

# ---------------- 2) optikk i snittet ----------------
PHR = math.atan(0.008 / 0.005)            # renna (veggar 5 mm under lina, ±8 mm) klipper her
SIG = M.SIGMA


def snitt_optikk(dp):
    """Fordeling G(θ) og η når plata heng i d' men rillene er rekna for d."""
    ph = np.linspace(-PHR, PHR, 4001)
    phm2 = math.atan(B['bp'] / 2 / dp)
    pa = np.abs(ph) <= phm2
    s = dp * np.tan(ph)
    tau = np.interp(s, O['s'], O['tau'])
    phi_i = np.arcsin(np.sin(ph) / n)
    ti2 = phi_i - tau
    arg = n * np.sin(ti2)
    tir = np.abs(arg) >= 1
    th = tau + np.arcsin(np.clip(arg, -1, 1))
    T1 = M.fresnel_T(np.abs(ph), np.abs(phi_i), 1.0, n)
    T2 = M.fresnel_T(np.abs(ti2), np.abs(np.arcsin(np.clip(arg, -1, 1))), n, 1.0)
    w_ref = np.where(pa & ~tir, np.cos(ph) * T1 * T2 * M.RISS, 0.0)
    w_lek = np.where(~pa, np.cos(ph), 0.0)
    dph = ph[1] - ph[0]
    tg = O['tg']
    def hist(theta, w, mat):
        h, _ = np.histogram(theta, bins=np.r_[tg - np.radians(0.125), tg[-1] + np.radians(0.125)], weights=w * dph)
        h = h / np.radians(0.25)
        if mat:
            k = np.exp(-0.5 * (np.degrees(tg - tg[len(tg) // 2]) / SIG) ** 2); k /= k.sum()
            h = np.convolve(h, k, mode='same')
        return h
    Gr = hist(th, w_ref, True); Gl = hist(ph, w_lek, False)
    Gt = Gr + Gl
    eta = np.trapezoid(Gt, tg) / 2                        # lambertsk total i snittet = ∫cos = 2
    eta_lek = np.trapezoid(Gl, tg) / 2
    # vifte: θ for 5/50/95 % av refraktert fluks
    Fc = np.cumsum(Gr); Fc /= Fc[-1]
    q5, q50, q95 = (math.degrees(np.interp(p, Fc, tg)) for p in (0.05, 0.5, 0.95))
    return dict(G=Gt / max(np.trapezoid(Gt, tg), 1e-12), eta=eta, eta_lek=eta_lek, q5=q5, q50=q50, q95=q95,
                phm2=math.degrees(phm2), tir=float(np.trapezoid(np.where(pa & tir, np.cos(ph), 0), ph) / 2))

print('\n2) Snittet midt på plata (rillene rekna for d = 50 mm)')
print(f"   motor: η {O['eta']:.3f}, vifte {math.degrees(O['th1']):+.1f}° … {math.degrees(O['th2']):+.1f}° (mål), renna klipper ved {math.degrees(PHR):.1f}°")
snittrad = {}
for dp in (0.050, 0.0575, 0.0617, 0.0675):
    r = snitt_optikk(dp)
    snittrad[f'{dp * 1e3:.1f}'] = {k: v for k, v in r.items() if k != 'G'}
    print(f"   d' {dp * 1e3:5.1f} mm: plata dekkjer ±{r['phm2']:.1f}°  η {r['eta']:.3f} (forbi kanten {r['eta_lek']:.3f}, TIR {r['tir']:.3f})"
          f"  refraktert vifte 5/50/95 % {r['q5']:+.1f}/{r['q50']:+.1f}/{r['q95']:+.1f}°")
out['snitt'] = snittrad

# ---------------- 3) 3D med søkkprofil ----------------
NX = 24
xs = (np.arange(NX) + .5) / NX * L - L / 2
S = np.c_[xs, np.full(NX, B['ys']), np.full(NX, B['zs'])]
u = xs / L + 0.5
form = 16 / 5 * (u - 2 * u ** 3 + u ** 4)                 # fritt opplagd, 1 midt


def E_task(dmax, Q=fe.TASK, qn=np.array([0, 0, 1.0]), a=0.0):
    tg = O['tg']
    d = Q[None] - S[:, None]
    r = np.linalg.norm(d, axis=-1)
    xi = np.arcsin(np.clip(d[..., 0] / r, -1, 1))
    th = np.arctan2(-d[..., 1], -d[..., 2])
    gam = (th - a + np.pi) % (2 * np.pi) - np.pi
    I = np.zeros_like(r)
    cache = {}
    for i in range(NX):
        dp = round(B['d'] + dmax * form[i], 4)
        if dp not in cache:
            cache[dp] = snitt_optikk(dp)
        R = cache[dp]
        I[i] = R['eta'] / NX * np.interp(gam[i], tg, R['G']) * (2 / np.pi) * np.cos(xi[i])
    ci = -(d @ qn) / r
    ok = (ci > 0) & ~fe.screen_block(S, Q)
    return (np.where(ok, I * ci / r ** 2, 0.0)).sum(0)

E_motor = M.E_punkt(B, 0.0, fe.TASK, np.array([0, 0, 1.0]))
print('\n3) Oppgåvesona (7×5), α 0, søkkprofil fritt opplagd langs x')
print(f"   motor (flat):       Em {E_motor.mean():.4f} lx/lm  U0 {E_motor.min() / E_motor.mean():.3f}  lm for 500 lx {500 / E_motor.mean():.0f}")
tre = {}
for lab, dm in (('flat (eigen kode)', 0.0), ('6 mm / innspent 2,5 mm', 0.0025), ('rilla 1 mm, kort 5,6 mm', 0.0056), ('rilla 0,5 mm, kort 7,1', 0.0071),
                ('rilla 1 mm, kryp 8,4 mm', 0.0084), ('rilla 0,5, kryp 10,7 mm', 0.0107), ('granskar 11,7 mm', 0.0117), ('granskar kryp 17,5 mm', 0.0175)):
    Et = E_task(dm)
    Ew = E_task(dm, fe.WALLG, np.array([0, -1.0, 0])).mean()
    Es = E_task(dm, np.c_[np.linspace(-0.25, 0.25, 5), np.full(5, fe.SCR['y'] - 1e-3), np.full(5, 0.30)], np.array([0, -1.0, 0])).mean()
    tre[lab] = dict(Em=float(Et.mean()), U0=float(Et.min() / Et.mean()), Phi=float(500 / Et.mean()), Ew=float(Ew), E_skjerm=float(Es),
                    rad=[float(v) for v in Et.reshape(5, 7).mean(1)])
    print(f"   {lab:24s} Em {Et.mean():.4f}  U0 {Et.min() / Et.mean():.3f}  lm for 500 lx {500 / Et.mean():.0f}  "
          f"rad y0,05→0,40 {np.round(Et.reshape(5, 7).mean(1) / E_motor.reshape(5, 7).mean(1), 3).tolist()}  vegg {Ew:.4f} skjerm(framside) {Es:.5f}")
out['tre_d'] = tre
# (skriv ikkje fil: oppgåva tillèt berre dette skriptet)
