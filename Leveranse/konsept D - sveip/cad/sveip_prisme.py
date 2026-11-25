# -*- coding: utf-8 -*-
"""Prismearket frå skjermen under nedre diffusor: jamnar det ut arbeidslyset?

Strålesporing med konsept/film/film.py (90°-prisme, n 1,57 etter domen i
konsept/vindauge/film/arket.md). Opalen er ei lambertsk kjelde; lys som arket kastar
attende, går tilbake til opalen og kammeret og blir sendt ut att lambertsk med
refleksjonsgraden R_REK (resirkulering). Utgangsfordelinga gjev luminansen til
opninga, og lux på arbeidsfeltet blir rekna direkte (utan romlys og skuggar) og
skalert mot lysmotoren (309 lx for berre opal).

Køyr frå cad/: python sveip_prisme.py     Skriv kontroll/sveip_prisme.json og render/sveip_prisme.png
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
from lagprio import lag_prioritet  # noqa: E402

lag_prioritet()
import numpy as np  # noqa: E402

ROT = Path(__file__).resolve().parent.parent
REPO = ROT.parent.parent
sys.path.insert(0, str(REPO / "konsept" / "film"))
from film import Film, prisme  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

N_D = 1.57                  # arbeidsverdi frå arket.md
R_REK = float(next((a_.split("=")[1] for a_ in sys.argv[1:] if a_.startswith("R=")), 0.50))
# R_REK: refleksjon attende frå opal + kvitt kammer. 0,5 er lågt; opal (R 0,30, T 0,65) over eit
# kammer med R 0,8 gjev om lag 0,30 + 0,65 * 0,8 * 0,65 = 0,64 ved éin runde, nær 0,7 med fleire.
LM = 400.0                  # lumen ut av opalen utan ark
H = 0.1725                  # opninga over bordet (m), rev. B
SKALERING_LYSMOTOR = 309.0  # felt-lux i lysmotoren for berre opal (plassering B)

# plassering B i lysmotoren: lampa til høgre for skjermen, snudd så utkraginga ligg inn over feltet
X0, Y0 = 0.62, 0.25         # høgre silhuett og framplata (m)
R_OPN = 0.0451              # opninga: innsida av leppa på ramma
X_OPN0, X_C = 0.1807, 0.2475
FELT = (-0.30, 0.30, 0.05, 0.45)


def lambert_ned(n, rng):
    u1, u2 = rng.random(n), rng.random(n)
    st = np.sqrt(u1)
    ct = np.sqrt(1 - u1)
    f = 2 * math.pi * u2
    return np.stack([st * np.cos(f), st * np.sin(f), -ct], 1)


def stabel(lag, n=300_000, pass_maks=10, seed=1):
    """Spor lys gjennom ein stabel av ark under opalen.
    lag: liste av (film, normal, riller) ovanfrå og ned. Gjev (retningar ut, vekter, rekneskap)."""
    rng = np.random.default_rng(seed)
    D = lambert_ned(n, rng)
    W = np.ones(n)
    gap = np.zeros(n, int)          # mellomrom: 0 = under opalen, i = under ark i
    ut_D, ut_W = [], []
    rekn = dict(inn=float(n), ut=0.0, tapt=0.0, resirkulert=0.0)
    for _ in range(pass_maks * (len(lag) + 1)):
        if len(D) == 0:
            break
        ned = D[:, 2] < 0
        # stråler som går ned under nedste ark: samla
        ferdig = ned & (gap == len(lag))
        ut_D.append(D[ferdig]); ut_W.append(W[ferdig]); rekn["ut"] += W[ferdig].sum()
        # stråler som går opp mot opalen: resirkulert lambertsk
        mot_opal = (~ned) & (gap == 0)
        k = mot_opal.sum()
        nyD = lambert_ned(k, rng)
        rekn["resirkulert"] += (W[mot_opal] * R_REK).sum()
        rekn["tapt"] += (W[mot_opal] * (1 - R_REK)).sum()
        D[mot_opal] = nyD
        W[mot_opal] *= R_REK
        aktiv = ~ferdig
        D, W, gap = D[aktiv], W[aktiv], gap[aktiv]
        if len(D) == 0:
            break
        # kvar stråle treffer arket over eller under seg
        ned = D[:, 2] < 0
        idx = np.where(ned, gap, gap - 1)   # arket som blir treft
        nyD = D.copy()
        nygap = gap.copy()
        behald = np.ones(len(D), bool)
        for i, (f, nrm, ril) in enumerate(lag):
            m = idx == i
            if not m.any():
                continue
            U, st = f.gjennom(D[m], nrm, ril)
            ned_m = ned[m]
            nyD[m] = U
            g = gap[m]
            # gjennom: frå mellomrom i til i+1 (ned) eller i+1 til i (opp); attende: same mellomrom
            nygap[m] = np.where(st == 1, np.where(ned_m, g + 1, g - 1), g)
            tapt = st == 0
            bm = np.where(m)[0]
            behald[bm[tapt]] = False
            rekn["tapt"] += W[bm[tapt]].sum()
        D, W, gap = nyD[behald], W[behald], nygap[behald]
        W = np.where(W < 1e-4, 0.0, W)
        levande = W > 0
        D, W, gap = D[levande], W[levande], gap[levande]
    Dut = np.concatenate(ut_D) if ut_D else np.zeros((0, 3))
    Wut = np.concatenate(ut_W) if ut_W else np.zeros(0)
    return Dut, Wut / n, {k: v / n for k, v in rekn.items()}


def luminanstabell(D, W, nb=81, glatt=1.2):
    """Tettleik i (u, v) = (dx, dy) for strålene som går ned, normert så summen er T (gjennomslepp)."""
    u, v = D[:, 0], D[:, 1]
    kant = np.linspace(-1, 1, nb + 1)
    h, _, _ = np.histogram2d(u, v, [kant, kant], weights=W)
    if glatt:
        from scipy.ndimage import gaussian_filter
        h = gaussian_filter(h, glatt)
    du = kant[1] - kant[0]
    tett = h / (du * du)            # per projisert romvinkel
    return kant, tett


def lux_felt(tabell, T, n_kjelde=26, steg=0.01):
    """Lux på bordet frå opninga (D-form) med luminansfordelinga i tabellen. Gjev (xs, ys, E)."""
    kant, tett = tabell
    nb = len(kant) - 1
    # kjeldepunkt i D-forma (lampekoordinatar -> rom, spegla)
    xs_l = np.linspace(X_OPN0, X_C + R_OPN, n_kjelde)
    ys_l = np.linspace(-R_OPN, R_OPN, n_kjelde)
    Q = []
    for xl in xs_l:
        for yl in ys_l:
            if xl > X_C and (xl - X_C) ** 2 + yl ** 2 > R_OPN ** 2:
                continue
            Q.append((X0 - xl, Y0 + 0.0525 + yl))
    Q = np.array(Q)
    areal = (X_C - X_OPN0) * 2 * R_OPN + math.pi * R_OPN ** 2 / 2
    dA = areal / len(Q)
    xs = np.arange(-0.45, 0.62 + 1e-9, steg)
    ys = np.arange(-0.05, 0.62 + 1e-9, steg)
    PX, PY = np.meshgrid(xs, ys, indexing="ij")
    E = np.zeros_like(PX)
    # radians: L = LM * T * tett / (pi-normert) / areal; lambertsk tett = 1/pi
    for qx, qy in Q:
        dx, dy = PX - qx, PY - qy
        r2 = dx * dx + dy * dy + H * H
        r = np.sqrt(r2)
        u, v = dx / r, dy / r                     # retning frå kjelda (ned)
        iu = np.clip(((u + 1) / 2 * nb).astype(int), 0, nb - 1)
        iv = np.clip(((v + 1) / 2 * nb).astype(int), 0, nb - 1)
        L = LM * tett[iu, iv] / areal              # W per m2 per sr (lm)
        cos_q = H / r
        E += L * cos_q * cos_q * dA / r2
    return xs, ys, E


def maal(xs, ys, E):
    x0, x1, y0, y1 = FELT
    mx = (xs >= x0 - 1e-9) & (xs <= x1 + 1e-9)
    my = (ys >= y0 - 1e-9) & (ys <= y1 + 1e-9)
    F = E[np.ix_(mx, my)]
    snitt = float(F.mean())
    # jamnheit som i lysmotoren: lågaste 10 cm-rute mot snittet
    ruter = []
    for i in range(0, F.shape[0] - 9, 10):
        for j in range(0, F.shape[1] - 9, 10):
            ruter.append(F[i:i + 10, j:j + 10].mean())
    return dict(snitt=snitt, min=float(F.min()), maks=float(F.max()), U=float(min(ruter) / snitt),
                lm_paa_feltet=float(snitt * (x1 - x0) * (y1 - y0)))


def main():
    t0 = time.time()
    f = Film(prisme(toppvinkel=90), n_d=N_D)
    opp, ned_ = (0, 0, 1), (0, 0, -1)
    langs_y, langs_x = (0, 1, 0), (1, 0, 0)
    variantar = {
        "V0 berre opal": [],
        "V1 prisme opp, riller langs y (spreier mot feltet og bort)": [(f, opp, langs_y)],
        "V2 prisme opp, riller langs x (spreier framover og bakover)": [(f, opp, langs_x)],
        "V3 to ark i kryss, prisme opp": [(f, opp, langs_y), (f, opp, langs_x)],
        "V4 prisme ned (som i skjermen), riller langs y": [(f, ned_, langs_y)],
    }
    # sagtann (asymmetrisk prisme): fasettar 30 og 60 grader mot basen, begge vegar
    for vinkel in (20, 30, 40):
        h = 1 / (1 / math.tan(math.radians(vinkel)) + 1 / math.tan(math.radians(90 - vinkel)))
        a_ = h / math.tan(math.radians(vinkel))
        for teikn_, profil in (("+", [(0, 0), (a_, h), (1, 0)]), ("-", [(0, 0), (1 - a_, h), (1, 0)])):
            fs = Film(np.array(profil, float), n_d=N_D)
            variantar[f"V5 sagtann {vinkel}/{90 - vinkel} {teikn_}, prisme opp, riller langs y"] = [(fs, opp, langs_y)]
    ut = dict(metode=__doc__.strip().splitlines()[0], n_d=N_D, R_resirkulering=R_REK, lm_opal=LM,
              hogd_m=H, foresetnader=["90°-prisme, ideell (H1 i arket.md, 55 %)", "550 nm",
                                      "direkte lys, ingen romlys og ingen skugge frå lampa",
                                      "felt-lux skalert til lysmotoren (309 lx for berre opal)"],
              variantar={})
    kart = {}
    for namn, lag in variantar.items():
        if lag:
            D, W, rk = stabel(lag)
        else:
            rng = np.random.default_rng(1)
            D = lambert_ned(300_000, rng)
            W = np.full(len(D), 1 / len(D))
            rk = dict(inn=1.0, ut=1.0, tapt=0.0, resirkulert=0.0)
        T = float(W.sum())
        tab = luminanstabell(D, W)
        xs, ys, E = lux_felt(tab, T)
        m = maal(xs, ys, E)
        # vinkelfordeling: del av lyset innanfor 20° av loddlina
        ct = -D[:, 2]
        loddrett = float(W[ct > math.cos(math.radians(20))].sum() / max(T, 1e-9))
        ut["variantar"][namn] = dict(T_ut_av_arket=round(T, 3), rekneskap={k: round(v, 3) for k, v in rk.items()},
                                     del_innanfor_20gr=round(loddrett, 3),
                                     felt_direkte=dict((k, round(v, 3 if k == "U" else 1)) for k, v in m.items()))
        kart[namn] = (xs, ys, E)
        print(f"{namn:58s} T {T:.2f}  felt {m['snitt']:6.1f} lx  U {m['U']:.2f}  maks {m['maks']:6.0f}  "
              f"lm på feltet {m['lm_paa_feltet']:5.1f}  innanfor 20° {loddrett:.2f}  ({time.time() - t0:.0f} s)")
    base = ut["variantar"]["V0 berre opal"]["felt_direkte"]["snitt"]
    for namn, v in ut["variantar"].items():
        v["felt_skalert_lx"] = round(SKALERING_LYSMOTOR * v["felt_direkte"]["snitt"] / base, 1)
        v["lm_for_350lx"] = round(LM * 350.0 / v["felt_skalert_lx"], 0)
    sti = ROT / "kontroll" / "sveip_prisme.json"
    alle = json.loads(sti.read_text(encoding="utf-8")) if sti.exists() else {}
    if "variantar" in alle:          # gammalt format: éin køyring
        alle = {}
    alle[f"R_{R_REK:.2f}"] = ut
    sti.write_text(json.dumps(alle, ensure_ascii=False, indent=1), encoding="utf-8")
    if abs(R_REK - 0.70) < 1e-9:
        teikn(kart, ut)
    print(f"ferdig {time.time() - t0:.0f} s")


def teikn(kart, ut):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    namn = list(kart)
    vis = [namn[0], namn[1], namn[3]]
    fig, axs = plt.subplots(1, 3, figsize=(15, 5.2), facecolor="black")
    lmax = max(kart[n][2].max() for n in vis)
    for ax, n in zip(axs, vis):
        xs, ys, E = kart[n]
        ax.set_facecolor("black")
        ax.imshow(np.sqrt(E.T / lmax), origin="lower", extent=(xs[0], xs[-1], ys[0], ys[-1]), cmap="inferno",
                  vmin=0, vmax=1)
        cs = ax.contour(xs, ys, E.T, levels=[100, 200, 350, 500, 1000, 2000], colors="white", linewidths=0.5)
        ax.clabel(cs, fmt="%d", fontsize=7, colors="white")
        x0, x1, y0, y1 = FELT
        ax.plot([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0], color="#88ccff", lw=0.8)
        v = ut["variantar"][n]
        ax.set_title(f"{n.split(' (')[0]}\n{v['felt_skalert_lx']:.0f} lx på feltet, U {v['felt_direkte']['U']:.2f}",
                     color="white", fontsize=10)
        ax.set_xlim(-0.4, 0.6); ax.set_ylim(-0.05, 0.6)
        ax.tick_params(colors="#888"); ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(ROT / "render" / "sveip_prisme.png", dpi=130, facecolor="black")


if __name__ == "__main__":
    main()
