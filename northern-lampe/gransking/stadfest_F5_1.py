# -*- coding: utf-8 -*-
"""Motprov F5 (stemningsmålet). Eigen rekning med motorane sine eigne kjeldemodellar (felles.illum, M3.E_punkt),
men eige cellegitter på veggen og eiga kollisjonssjekk mot armen i (c).
Køyr: PYTHONIOENCODING=utf-8 python stadfest_F5_1.py
"""
import os, sys, math, time, importlib.util
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HER)
sys.path[:0] = [ROOT, os.path.join(ROOT, 'form01'), os.path.join(ROOT, 'form02')]
import felles as fe
import motor as M1
import val as V2
spec = importlib.util.spec_from_file_location('motor3', os.path.join(ROOT, 'form04', 'motor.py'))
M3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(M3)
T0 = time.time()
RHO_V = 0.75
E10 = 10 * math.pi / RHO_V


def celler(x0, x1, z0, z1, h):
    nx, nz = int(round((x1 - x0) / h)), int(round((z1 - z0) / h))
    X, Z = np.meshgrid(x0 + (np.arange(nx) + .5) / nx * (x1 - x0), z0 + (np.arange(nz) + .5) / nz * (z1 - z0))
    return X.ravel(), Z.ravel()


def vegg(h):
    x, z = celler(-0.70, 0.70, 0.05, 1.20, h)
    return np.c_[x, np.full(x.size, fe.WALL_Y - 1e-3), z]


def bord(h):
    x, y = celler(-0.70, 0.70, 0.0, 0.75, h)
    return np.c_[x, y, np.zeros(x.size)]


NW, NB = np.array([0, -1.0, 0]), np.array([0, 0, 1.0])
GITTER = {'8x6': fe.WALLG, '4cm': vegg(0.04), '2cm': vegg(0.02)}
B4 = bord(0.04)


def lambert(B, opn, eta, psi, n=None, nt=3):
    P, N, dA = opn(B, psi, nt, n)
    k = eta / (math.pi * dA.sum())
    out = {g: fe.illum(P, N, dA, Q, NW) * k for g, Q in GITTER.items()}
    out['bord8x5'] = fe.illum(P, N, dA, fe.DESKG, NB) * k
    out['bord4cm'] = fe.illum(P, N, dA, B4, NB) * k
    return out


def prisme(B, a):
    out = {g: M3.E_punkt(B, a, Q, NW) for g, Q in GITTER.items()}
    out['bord8x5'] = M3.E_punkt(B, a, fe.DESKG, NB)
    out['bord4cm'] = M3.E_punkt(B, a, B4, NB)
    return out


def skriv(lab, r, Phi_w):
    s = f"{lab:28s}"
    for g in ('8x6', '4cm', '2cm'):
        s += f"  Ē/lm {g} {r[g].mean():.4f}"
    w = r['2cm'].mean()
    lm = E10 / w
    Rr = r['8x6'].mean() / (r['8x6'].mean() + r['bord8x5'].mean())
    fl_v = r['2cm'].mean() * 1.4 * 1.15
    fl_b = r['bord4cm'].mean() * 1.4 * 0.75
    s += (f"\n{'':28s}  25 %: {0.25*Phi_w:.0f} LED-lm -> Ē 8x6 {r['8x6'].mean()*0.25*Phi_w:.1f} lx, 2 cm {w*0.25*Phi_w:.1f} lx"
          f" | 10 cd/m²: {lm:.0f} lm = {lm/100:.2f} W | R_stem {Rr:.3f}, fluksdel vegg/(vegg+bord) {fl_v/(fl_v+fl_b):.3f}"
          f" | maks/snitt 2 cm {r['2cm'].max()/w:.2f}")
    print(s, flush=True)
    return dict(w=w, lm=lm, W=lm / 100)


res = {}
# (a) bru: B frå tal_bru (form02/tal.json: yp 0,18, hp 0,62), stemning ψ −95
Ba = dict(M1.FINAL, yp=0.18, hp=0.62)
ea = M1.eta(Ba)
ra = lambert(Ba, M1.opning, ea, math.radians(-95))
res['a'] = skriv('(a) ψ −95', ra, 1255.2431)
ra2 = lambert(Ba, M1.opning, ea, math.radians(-95), n=129, nt=6)
skriv('(a) ψ −95, fin kjelde', ra2, 1255.2431)
# (b) krok: stemningsstilling frå fe.sok
Bb = dict(V2.B_KROK)
Sb = V2.sok_krok(Bb)
pm = Sb['mood']['s']; pw = Sb['work']['s']
print(f"(b) sok: arbeid ψ {math.degrees(pw):.0f}, stemning ψ {math.degrees(pm):.0f}, Φ {Sb['work']['Phi']:.1f}, Ev_stem {Sb['mood']['Ev_stem']:.2f}, R {Sb['mood']['R_stem']:.4f}")
eb = V2.eta_krok(Bb)
rb = lambert(Bb, V2.opning_krok, eb, pm)
res['b'] = skriv(f'(b) ψ {math.degrees(pm):.0f}', rb, Sb['work']['Phi'])
print(f"   ({time.time()-T0:.0f} s)", flush=True)
# (c) prisme
Bc = dict(M3.FINAL)
Sc = M3.sok(Bc)
am = Sc['mood']['s']
print(f"(c) sok: arbeid α {math.degrees(Sc['work']['s']):.0f}, stemning α {math.degrees(am):.0f}, Φ {Sc['work']['Phi']:.1f}, Ev_stem {Sc['mood']['Ev_stem']:.2f}, R {Sc['mood']['R_stem']:.4f}")
PhiC = Sc['work']['Phi']
rc = prisme(Bc, am)
res['c105'] = skriv(f'(c) α {math.degrees(am):.0f}', rc, PhiC)


# armen: U-profil |x| <= 0,05, y frå ys−0,012 til COL_Y+COL_F, z frå za til za+COL_F. Plata (60 cm i x) kan ikkje gå forbi.
def plate_yz(B, a, n=41):
    ned = np.array([-math.sin(a), -math.cos(a)]); fram = np.array([-math.cos(a), math.sin(a)])
    c = np.array([B['ys'], B['zs']])
    pts = [c + v * fram + w * ned for v in np.linspace(-B['bp'] / 2, B['bp'] / 2, n) for w in (B['d'], B['d'] + B['tp'])]
    # kinna frå tverrstonga til plata
    pts += [c + v * fram + w * ned for w in np.linspace(0.02, B['d'], 8) for v in (-B['bp'] / 2 * (w - 0.02) / (B['d'] - 0.02),)]
    return np.array(pts)


za = Bc['zs'] + 0.03
y_lo, y_hi, z_lo, z_hi = Bc['ys'] - 0.012, M3.COL_Y + M3.COL_F, za, za + M3.COL_F
grense = None
for adeg in np.arange(0, -181, -1):
    p = plate_yz(Bc, math.radians(adeg))
    if ((p[:, 0] > y_lo) & (p[:, 0] < y_hi) & (p[:, 1] > z_lo) & (p[:, 1] < z_hi)).any():
        grense = adeg + 1
        break
print(f"(c) plata (om LED-aksen) treffer armen frå α {grense - 1}°: siste fri stilling {grense}°")
for adeg in (grense, -60, -70, -80, -90):
    r = prisme(Bc, math.radians(adeg))
    res[f'c{adeg}'] = skriv(f'(c) α {adeg}', r, PhiC)
print(f"\nSamandrag (2 cm, 10 cd/m², ρ 0,75): " + '  '.join(f"{k} {v['W']:.2f} W" for k, v in res.items()))
print(f"({time.time()-T0:.0f} s)")
