# -*- coding: utf-8 -*-
# kamera.py · Kameratilpassing for referansebiletet til Kran: vatrett kamera (loddrette liner er loddrette i biletet),
# stativplanet dreidd vinkelen phi om loddaksen. Skala: leddaksen Hp mm over bordet.
import json
from pathlib import Path
import math
import numpy as np
from scipy.optimize import least_squares

cx = 1128.0                       # midt i fotoet (ramme x 88-2168)
HP = 330.0                        # vald skala: leddaksen over bordet (mm)
Y_STATIV = -2.25                  # framsida av stativplata (tre lag à 1,5 mm, midtplanet på Y = 0)
Y_KNOTT = -13.75                  # framsida av knotten
Y_ARM = -7.25                     # framsida av armen og øyret, i same plan (sett av leddstabelen, sjå cad/kran.py)

# målte punkt (originale pikslar)
A = (339.0, 1288.0)               # nedre venstre hjørne
B = (762.0, 1315.0)               # nedre høgre hjørne
P = (681.0, 374.0)                # sentrum i knotten
venstre = [(621, 420), (595, 450 + 50), (562, 600), (530, 700), (497, 800), (462, 900), (429, 1000), (395, 1100)]
hogre = [(723, 420), (727, 500), (733, 600), (737, 700), (741, 800), (744, 900), (748, 1000), (751, 1100)]
spalte_v = [(626, 500), (596, 600), (566, 700), (536, 800), (505, 900), (476, 1000), (447, 1100)]
spalte_h = [(664, 500), (633, 600), (602, 700), (570, 800), (539, 900), (509, 1000), (479, 1100)]
spalte_ende = [(683, 408), (452, 1176)]          # øvre og nedre ende (ytterpunkt på bogen)
arm_topp = [(760, 352), (1050, 346), (1500, 336), (1900, 323)]
arm_botn = [(760, 410), (1000, 407), (1500, 399), (1900, 388)]
tupp_x_front, tupp_x_bak = 2000.0, 2042.0
knott_ratio = 36.0 / 42.0


def modell(q):
    f, phi, cy, uA, ZA = q
    return f, phi, cy, uA, ZA


def proj(q, X, Y, Z):
    """Punkt i lampekoordinatar (X langs armen i stativplanet, Y bakover frå planet, Z opp) til bilete."""
    f, phi, cy, uA, ZA, H = q
    lat = uA + X * math.cos(phi) + Y * math.sin(phi)
    djup = ZA - X * math.sin(phi) + Y * math.cos(phi)
    return cx + f * lat / djup, cy - f * (Z - H) / djup, djup


def los(geo):
    """geo: X-ar og Z-ar for formpunkta; returnerer residualar."""
    pass


# Ukjende: kamera f, phi, cy, uA, ZA, H og form: Bx, Px, Pz=HP (fast), XtopV, ZtopV (venstre kant øvst),
# XtopH, ZtopH (høgre kant øvst), spalte (X1,Z1,X2,Z2,breidd), arm (zt, zb, Xtupp, Yfront, Djup)
navn = ['f', 'phi', 'cy', 'uA', 'ZA', 'H', 'Bx', 'Px', 'Xv', 'Zv', 'Xh', 'Zh', 'S1x', 'S1z', 'S2x', 'S2z', 'Sb',
        'zt', 'zb', 'Xt', 'D']


def resid(v):
    p = dict(zip(navn, v))
    q = (p['f'], p['phi'], p['cy'], p['uA'], p['ZA'], p['H'])
    r = []
    w = 1.0

    def pt(X, Y, Z, obs, vekt=1.0):
        x, y, _ = proj(q, X, Y, Z)
        r.extend([(x - obs[0]) * vekt, (y - obs[1]) * vekt])

    def linje(P1, P2, obs_liste, vekt=1.0):
        a = np.array(proj(q, *P1)[:2]); b = np.array(proj(q, *P2)[:2])
        d = b - a; n = np.array([-d[1], d[0]]) / np.linalg.norm(d)
        for o in obs_liste:
            r.append(float(np.dot(np.array(o, float) - a, n)) * vekt)

    ys = Y_STATIV
    pt(0, ys, 0, A)
    pt(p['Bx'], ys, 0, B)
    pt(p['Px'], Y_KNOTT, HP, P)
    linje((0, ys, 0), (p['Xv'], ys, p['Zv']), venstre)
    linje((p['Bx'], ys, 0), (p['Xh'], ys, p['Zh']), hogre)
    # spalta: to kantar parallelle med aksen S1-S2, halv breidd Sb
    ax = np.array([p['S2x'] - p['S1x'], p['S2z'] - p['S1z']]); L = np.linalg.norm(ax); ax /= L
    nrm = np.array([-ax[1], ax[0]])
    for sgn, obs in ((1, spalte_v), (-1, spalte_h)):
        o1 = np.array([p['S1x'], p['S1z']]) + sgn * nrm * p['Sb']; o2 = np.array([p['S2x'], p['S2z']]) + sgn * nrm * p['Sb']
        linje((o1[0], ys, o1[1]), (o2[0], ys, o2[1]), obs)
    # spalteendane: ytterpunkt på bogen langs aksen
    e2 = np.array([p['S2x'], p['S2z']]) + ax * p['Sb']; e1 = np.array([p['S1x'], p['S1z']]) - ax * p['Sb']
    pt(e2[0], ys, e2[1], spalte_ende[0]); pt(e1[0], ys, e1[1], spalte_ende[1])
    # armen: vassrett, framflata på Y = Yf, topp zt, botn zb
    linje((p['Px'] + 30, Y_ARM, p['zt']), (p['Xt'], Y_ARM, p['zt']), arm_topp, 2.0)
    linje((p['Px'] + 30, Y_ARM, p['zb']), (p['Xt'], Y_ARM, p['zb']), arm_botn, 2.0)
    x_f = proj(q, p['Xt'], Y_ARM, (p['zt'] + p['zb']) / 2)[0]
    x_b = proj(q, p['Xt'], Y_ARM + p['D'], (p['zt'] + p['zb']) / 2)[0]
    r.extend([(x_f - tupp_x_front) * 2.0, (x_b - tupp_x_bak) * 2.0])
    # knotten er ein sirkel: breidd/høgd i biletet
    xs = [proj(q, p['Px'] + 10 * dx, Y_KNOTT, HP)[0] for dx in (-1, 1)]
    yy = [proj(q, p['Px'], Y_KNOTT, HP + 10 * dz)[1] for dz in (-1, 1)]
    r.append((abs(xs[1] - xs[0]) / abs(yy[1] - yy[0]) - knott_ratio) * 300.0)
    return np.array(r)


start = dict(f=4000, phi=math.radians(25), cy=570, uA=-290, ZA=1450, H=260, Bx=175, Px=150, Xv=150, Zv=330,
             Xh=170, Zh=320, S1x=45, S1z=40, S2x=150, S2z=310, Sb=6, zt=345, zb=322, Xt=640, D=25)
x0 = np.array([start[n] for n in navn], float)
lo = np.array([1500, math.radians(5), 300, -800, 300, 100, 80, 50, 50, 200, 80, 200, 0, 0, 50, 150, 2, 300, 280, 350, 8])
hi = np.array([12000, math.radians(60), 900, 0, 5000, 400, 300, 280, 260, 420, 300, 420, 150, 150, 260, 400, 15, 400, 380, 1000, 60])
res = least_squares(resid, x0, bounds=(lo, hi))
p = dict(zip(navn, res.x))
rms = float(np.sqrt(np.mean(res.fun ** 2)))
ut = {k: round(float(v), 2) for k, v in p.items()}
ut['phi_grad'] = round(math.degrees(p['phi']), 2)
ut['rms_px'] = round(rms, 2)
ut['arm_rekkjevidd_mm'] = round(p['Xt'] - p['Px'], 1)
ut['arm_hogd_mm'] = round(p['zt'] - p['zb'], 1)
print(json.dumps(ut, indent=1))
folsemd = {}
# føresetnaden om fast f: sjå korleis proporsjonane endrar seg med brennvidda
for ff in (2500, 3500, 5000, 7000, 9000):
    def r2(v):
        return resid(np.concatenate([[ff], v]))
    lo2, hi2 = lo[1:], hi[1:]
    x02 = np.clip(res.x[1:], lo2 + 1e-6, hi2 - 1e-6)
    s = least_squares(r2, x02, bounds=(lo2, hi2))
    q = dict(zip(navn[1:], s.x))
    folsemd[ff] = dict(rms_px=round(float(np.sqrt(np.mean(s.fun ** 2))), 2), phi_grad=round(math.degrees(q['phi']), 1), arm_mm=round(q['Xt'] - q['Px'], 1), fot_mm=round(q['Bx'], 1), arm_djupn_mm=round(q['D'], 1))
    print(ff, 'rms', round(float(np.sqrt(np.mean(s.fun ** 2))), 2), 'phi', round(math.degrees(q['phi']), 1),
          'Bx', round(q['Bx'], 1), 'Px', round(q['Px'], 1), 'arm', round(q['Xt'] - q['Px'], 1),
          'armhogd', round(q['zt'] - q['zb'], 1), 'armdjupn', round(q['D'], 1), 'H', round(q['H'], 1))

ut['folsemd_brennvidd'] = folsemd
ut['Yf'] = Y_ARM
ut['merknad'] = ('Flatene ligg der CAD-en har dei: framsida av stativet Y -2,25, knotten -13,75, armen og øyret -7,25. '
                 'Ei fri tilpassing gjev same rms (2,49 px) for alle Y på armen, så fotoet avgjer ikkje Y; øyret gjer det. '
                 'Vatrett kamera (loddrette liner er loddrette i fotoet), stativplanet dreidd phi om loddaksen. '
                 'Skala: leddaksen 330 mm over bordet (vald). Punkta er målte i originalbiletet, som ligg berre lokalt.')
(Path(__file__).resolve().parent / 'maaling.json').write_text(json.dumps(ut, ensure_ascii=False, indent=1), encoding='utf-8')
