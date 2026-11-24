# -*- coding: utf-8 -*-
"""
segl_lys.py  ·  siktliner (F1) og ei enkel lysrekning for Segl

    python segl_lys.py

1) Siktliner: frå 7 x 76 punkt på den lysande flata til LED-stripa til auge på ein kuppel med radius 700 mm
   rundt lampa (asimut kvar 5°, høgd 0-85° kvar 5°). Hindringar: begge segla (fire felt), beraren (sete,
   skjermleppe, endeflik) og klampa. Gjev eit polarkart og prosent synleg per sektor.
2) Lys: Monte Carlo med 400 000 strålar frå stripa (lambertsk). Første treff på segla gjev illuminans,
   L = rho * E / pi med rho = 0,30 (ANTEKE, terrakotta pulverlakk). Ingen fleire sprett.
   Straumen er LEDYI LY224-S2216DTW-W24: 1389 lm/m x 0,1875 m = 260 lm ved full styrke (DATABLAD).
Skriv kontroll/segl_lys.json og kontroll/segl_siktliner.png, kontroll/segl_luminans.png.
"""
import os, sys, json, math
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HER)
import segl_geometri as G
from segl_geometri import T, ZP, D01, D02, eining, V3
import segl_cad as C

ROT = os.path.dirname(HER)
RHO = 0.30
LM = 1389.0 * (G.LED_X[1] - G.LED_X[0]) / 1000.0


def trekantar():
    """Hindringar som trekantar (midtflata er nok for siktliner)."""
    tri = []
    def poly(pts):
        for i in range(1, len(pts) - 1):
            tri.append((pts[0], pts[i], pts[i + 1]))
    for s in (D01, D02):
        poly([s.S, s.Q, s.A]); poly([s.Qh, s.B, s.A])
        poly([s.S + 0 * s.nV, V3(s.S[0], s.S[1], 0), V3(s.Q[0], s.Q[1], 0), s.Q])     # bøyesona under felta
        poly([s.Qh, V3(s.Q2[0], s.Q2[1], 0), V3(s.B2[0], s.B2[1], 0), s.B])
    # beraren: setet, skjermleppa, endeflika (sjå lag_e01)
    s45 = math.sqrt(0.5); y0, y1 = G.E01_BASE_Y; x0, x1 = G.E01_X
    a = np.array([y0, T]); b = a + G.E01_SETE * np.array([-s45, s45])
    poly([V3(x0, a[0], a[1]), V3(x1, a[0], a[1]), V3(x1, b[0], b[1]), V3(x0, b[0], b[1])])
    zs = T + G.AL_T
    poly([V3(G.E01_SKJERM_X0, y1, zs), V3(x1, y1, zs), V3(x1, y1, zs + G.E01_SKJERM_H), V3(G.E01_SKJERM_X0, y1, zs + G.E01_SKJERM_H)])
    nset = np.array([s45, s45]); dset = np.array([-s45, s45])
    q0 = np.array([y0, T]) + G.AL_T * nset; q0 = q0 + ((T + G.AL_T - q0[1]) / dset[1]) * dset
    q1 = b + G.AL_T * nset
    poly([V3(x0, *q0), V3(x0, *q1), V3(x0, *(q1 + G.E01_ENDE_H * nset)), V3(x0, *(q0 + G.E01_ENDE_H * nset))])   # flik på setet, venstre
    xs = G.E01_SKJERM_X0; H_ = G.E01_SKJERM_H
    poly([V3(xs, y1, zs), V3(xs, G.E01_VENG_Y, zs), V3(xs, G.E01_VENG_Y, zs + H_), V3(xs, y1, zs + H_)])          # vengen
    poly([V3(x1, 6.0, zs), V3(x1, y1, zs), V3(x1, y1, zs + H_), V3(x1, 6.0, zs + H_)])                          # endeveggen
    # klampa
    kx0, kx1 = G.KL_X; ky0, ky1 = G.KL_Y; h = G.KL_H
    for p in ([V3(kx0, ky0, 0), V3(kx1, ky0, 0), V3(kx1, ky0, h), V3(kx0, ky0, h)], [V3(kx1, ky0, 0), V3(kx1, ky1, 0), V3(kx1, ky1, h), V3(kx1, ky0, h)],
              [V3(kx0, ky0, h), V3(kx1, ky0, h), V3(kx1, ky1, h), V3(kx0, ky1, h)]):
        poly(p)
    return [np.array(t) for t in tri]


def treff(o, d, tri, tmax=None):
    """Möller-Trumbore, vektorisert over strålar. Returnerer minste t (inf om ingen) og indeksen til trekanten."""
    n = len(o)
    best = np.full(n, np.inf); idx = np.full(n, -1)
    for k, (v0, v1, v2) in enumerate(tri):
        e1 = v1 - v0; e2 = v2 - v0
        p = np.cross(d, e2); det = p @ e1
        ok = np.abs(det) > 1e-12
        inv = np.where(ok, 1.0 / np.where(ok, det, 1), 0)
        s = o - v0
        u = (s * p).sum(1) * inv
        q = np.cross(s, e1)
        v = (d * q).sum(1) * inv
        t = (q @ e2) * inv
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-6)
        if tmax is not None:
            hit &= t < tmax
        better = hit & (t < best)
        best[better] = t[better]; idx[better] = k
    return best, idx


def led_flate():
    _, _, lys = C.lag_e01()
    s45 = math.sqrt(0.5)
    n = np.array(lys['normal'])
    d = np.array([0.0, -s45, s45])
    mid = np.array(lys['midt'])
    return mid, d, n, lys


def siktliner():
    tri = trekantar()
    mid, dq, n, lys = led_flate()
    xs = np.linspace(G.LED_X[0] + 0.5, G.LED_X[1] - 0.5, 76)
    ws = np.linspace(-G.LED_B / 2 + 0.3, G.LED_B / 2 - 0.3, 7)
    L = np.array([[x, mid[1] + w * dq[1] + 0.05 * n[1], mid[2] + w * dq[2] + 0.05 * n[2]] for x in xs for w in ws])
    senter = np.array([120.0, 15.0, 0.0])
    R = 700.0
    asim = np.arange(0, 360, 5); hogd = np.arange(0, 90, 5)
    synleg = np.zeros((len(hogd), len(asim)))
    for i, el in enumerate(hogd):
        for j, az in enumerate(asim):
            a, e = math.radians(az), math.radians(el)
            E = senter + R * np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
            dvec = E - L
            dist = np.linalg.norm(dvec, axis=1)
            dirs = dvec / dist[:, None]
            framfor = dirs @ n > 0.02                 # stripa lyser berre ut av flata si
            t, _ = treff(L[framfor], dirs[framfor], tri, tmax=None)
            blokk = t < dist[framfor]
            synleg[i, j] = (~blokk).sum() / len(L)
    return asim, hogd, synleg


def lysrekning(nstr=400000, seed=1):
    rng = np.random.default_rng(seed)
    tri = trekantar()
    ntri_segl = 16                                    # dei 16 første trekantane er segla (4 per segl x 2 + bøysoner)
    mid, dq, n, lys = led_flate()
    x = rng.uniform(G.LED_X[0], G.LED_X[1], nstr)
    w = rng.uniform(-G.LED_B / 2, G.LED_B / 2, nstr)
    o = np.stack([x, mid[1] + w * dq[1] + 0.02 * n[1], mid[2] + w * dq[2] + 0.02 * n[2]], 1)
    # lambertsk retning rundt n
    r1, r2 = rng.random(nstr), rng.random(nstr)
    th = np.arcsin(np.sqrt(r1)); ph = 2 * math.pi * r2
    t1 = np.array([1.0, 0, 0]); t2 = np.cross(n, t1)
    d = (np.cos(th)[:, None] * n + (np.sin(th) * np.cos(ph))[:, None] * t1 + (np.sin(th) * np.sin(ph))[:, None] * t2)
    t, idx = treff(o, d, tri)
    lm_per = LM / nstr
    res = {'lm_kjelde': round(LM, 1)}
    # kva treffer kva
    # rekkjefølgja i trekantar(): per segl 1 venstre felt, 1 høgre felt, 2 + 2 i bøysonene
    namn = {}
    for b, s in ((0, 'D01'), (6, 'D02')):
        namn[b] = f'{s}_venstre'; namn[b + 1] = f'{s}_hogre'
        namn[b + 2] = namn[b + 3] = f'{s}_boy_v'; namn[b + 4] = namn[b + 5] = f'{s}_boy_h'
    del_lm = {}
    for i in np.unique(idx):
        key = namn.get(int(i), 'berar/klampe' if i >= 0 else 'ut_direkte')
        # trekantane er lagra som 2 per firkant/felt: grupper etter rekkjefølgje
        del_lm[key] = del_lm.get(key, 0) + float((idx == i).sum() * lm_per)
    res['lm_forste_treff'] = {k: round(v, 1) for k, v in del_lm.items()}
    # illuminans på innsida av høgseglet (hovudfeltet), rutenett 10 x 10 mm i feltet sitt plan
    hit = np.isfinite(t)
    P = o + d * np.where(hit, t, 0)[:, None]
    s = D02
    rut = {}
    for felt, (orig, e1, e2) in {'D02_hogre': (s.Qh, eining(s.B - s.Qh), V3(0, 0, 1)),
                                 'D02_venstre': (s.Q, s.e1, s.e2),
                                 'D01_venstre': (D01.Q, D01.e1, D01.e2),
                                 'D01_hogre': (D01.Qh, eining(D01.B - D01.Qh), V3(0, 0, 1))}.items():
        sel = np.zeros(nstr, bool)
        for i, nm in namn.items():
            if nm == felt:
                sel |= idx == i
        if not sel.any():
            continue
        q = P[sel] - orig
        a = q @ e1; b = q @ e2
        cell = 10.0
        H, xe, ye = np.histogram2d(a, b, bins=[np.arange(a.min() - cell, a.max() + cell, cell), np.arange(b.min() - cell, b.max() + cell, cell)])
        E = H * lm_per / (cell * cell * 1e-6)           # lux
        Lmax = RHO * E.max() / math.pi
        # p99 over celler med treff
        Ev = E[E > 0]
        rut[felt] = dict(lm=round(float(sel.sum() * lm_per), 1), E_maks_lx=round(float(E.max())), E_p99_lx=round(float(np.percentile(Ev, 99))),
                         L_maks_cd_m2=round(Lmax), L_p99_cd_m2=round(RHO * float(np.percentile(Ev, 99)) / math.pi),
                         L_snitt_cd_m2=round(RHO * float(Ev.mean()) / math.pi), _H=(H, xe, ye))
    res['felt'] = rut
    # stråler som går rett ut: kvar går dei (oppover, mot veggen, mot bordet)
    ut = ~hit
    du = d[ut]
    res['ut_direkte'] = dict(lm=round(float(ut.sum() * lm_per), 1), opp=round(float((du[:, 2] > 0.5).sum() * lm_per), 1),
                             mot_veggen=round(float(((du[:, 1] > 0.5) & (du[:, 2] <= 0.5)).sum() * lm_per), 1))
    # grovt: lys som forlet lampa etter eitt sprett (rho) + direkte
    sprett = sum(v['lm'] for v in rut.values()) * RHO
    res['lm_ut_eitt_sprett'] = round(res['ut_direkte']['lm'] + sprett, 1)
    return res


def teikn(asim, hogd, synleg, res):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(12, 5.4), facecolor='black')
    ax = fig.add_subplot(121, projection='polar', facecolor='black')
    A, Hh = np.meshgrid(np.radians(np.append(asim, 360)), 90 - np.append(hogd, 90))
    Z = np.c_[synleg, synleg[:, :1]]
    Z = np.r_[Z, Z[-1:]]
    ax.pcolormesh(A, Hh, Z, cmap='inferno', vmin=0, vmax=0.3, shading='auto')
    ax.set_theta_zero_location('E'); ax.set_ylim(0, 90)
    ax.set_yticks([30, 60, 90]); ax.set_yticklabels(['60°', '30°', '0°'], color='#888')
    ax.set_xticks(np.radians([0, 90, 180, 270])); ax.set_xticklabels(['høgre ende', 'bak (vegg)', 'venstre (klampe)', 'framme (brukar)'], color='#aaa')
    ax.set_title('kvar stripa kan sjåast frå (andel av stripa)', color='#ccc', fontsize=10)
    ax2 = fig.add_subplot(122, facecolor='black')
    H, xe, ye = res['felt']['D02_hogre']['_H']
    E = H * (LM / 400000) / (1e-4)
    L = RHO * E / math.pi
    im = ax2.imshow(L.T, origin='lower', extent=[xe[0], xe[-1], ye[0], ye[-1]], cmap='inferno', aspect='equal')
    ax2.set_title('luminans på innsida av høgseglet (cd/m², rho 0,30)', color='#ccc', fontsize=10)
    ax2.tick_params(colors='#888')
    cb = fig.colorbar(im, ax=ax2); cb.ax.tick_params(colors='#888')
    fig.tight_layout()
    fig.savefig(os.path.join(ROT, 'kontroll', 'segl_lys.png'), dpi=110, facecolor='black')


if __name__ == '__main__':
    asim, hogd, synleg = siktliner()
    sektor = {}
    for namn, (a0, a1) in {'framme (225-315°)': (225, 315), 'høgre ende (-45-45°)': (-45, 45), 'bak (45-135°)': (45, 135), 'venstre (135-225°)': (135, 225)}.items():
        sel = [(j) for j, a in enumerate(asim) if (a0 <= a <= a1) or (a0 < 0 and a >= 360 + a0)]
        lag = {}
        for el0, el1 in ((0, 30), (30, 60), (60, 85)):
            rows = [i for i, e in enumerate(hogd) if el0 <= e < el1 or (el1 == 85 and e == 85)]
            blokk = synleg[np.ix_(rows, sel)]
            lag[f'høgd {el0}-{el1}°'] = dict(retningar_med_synleg_stripe=f'{int((blokk > 0).sum())} av {blokk.size}', maks_andel=round(float(blokk.max()), 3))
        sektor[namn] = lag
    res = lysrekning()
    teikn(asim, hogd, synleg, res)
    for v in res['felt'].values():
        v.pop('_H', None)
    ut = dict(siktliner=sektor, lys=res, rho_anteke=RHO, merknad='Første treff og eitt sprett. Ingen inter-refleksjon, ingen rom.')
    json.dump(ut, open(os.path.join(ROT, 'kontroll', 'segl_lys.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(json.dumps(ut, indent=1, ensure_ascii=False))
