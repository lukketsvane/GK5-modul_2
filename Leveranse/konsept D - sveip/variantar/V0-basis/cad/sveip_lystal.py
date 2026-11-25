# -*- coding: utf-8 -*-
"""Lystal for Sveip rev. B i lysmotoren til prosjektet (konsept/lysskisse/lysskisse.py),
same rom, same felt og same augepunkt som konsepta A til D vart rekna i.

Geometrien er henta frå CAD-en (sveip_lys.py): nedre diffusor er ei D-form på 0,0105 m2,
172,5 mm over bordet; øvre diffusor ligg 84 mm under toppkanten (rev. B).
Køyr frå cad/: python sveip_lystal.py   (om lag 20 s, éin prosess, lågaste prioritet)
Skriv kontroll/sveip_lys.json.
"""
import json
import math
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("LYSSKISSE_POLGE", "0")
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "2")
sys.dont_write_bytecode = True
from lagprio import lag_prioritet  # noqa: E402

lag_prioritet()
ROT = Path(__file__).resolve().parent.parent
REPO = next(p for p in ROT.parents if (p / 'konsept' / 'lysskisse').is_dir())
sys.path.insert(0, str(REPO / "konsept" / "lysskisse"))
import numpy as np  # noqa: E402
from lysskisse import LUM, STATISK, ZB, E_direkte, Rekt, b, flate, tal  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------------------------------------------------------------- geometri frå CAD (m)
S, D, R = 0.300, 0.105, 0.0525
FOT = 0.003
H_SKJ = 0.1675 + FOT                  # underkant skjerm over bordet
X_ST = 0.178
NED_A = 0.010504                      # areal nedre diffusor (D-form)
NED_XC = 0.2326                       # tyngdepunkt av D-forma (frå venstre silhuett)
NED_Z = 0.1695 + FOT                  # undersida av diffusoren over bordet
OPP_A = 0.026513                      # areal øvre diffusor
OPP_Z = 0.2155 + FOT                  # rev. B: 28 mm blandehøgd
TOPP_A = (S - D) * D + math.pi * R ** 2
ROMNING_OPP = 0.65                    # del av opplyset som kjem ut av toppen (overslag, sjå notat)


def sveip(x0, y0, lm_ned=400.0, lm_opp=200.0, K_ned=3000, K_opp=2700, spegla=False):
    sx = -1.0 if spegla else 1.0
    X = lambda u: x0 + sx * u  # noqa: E731
    yc = y0 + D / 2
    lys = []
    if lm_ned > 0:
        bx = NED_A / 0.0976
        lys.append(flate(b(X(NED_XC), yc, NED_Z), (0, 0, -1), (bx, 0.0976), lm_ned, K_ned))
    if lm_opp > 0:
        # opplyset modellert som den opne toppen med lyset som kjem ut (øvre grense for luminans)
        lys.append(flate(b(X(S / 2), yc, S + FOT), (0, 0, 1), (TOPP_A / D, D), lm_opp * ROMNING_OPP, K_opp))

    def plate(u0, u1, y, h0, h1):
        xa, xb = sorted((X(u0), X(u1)))
        return Rekt((xa, y, ZB + h0), (xb - xa, 0, 0), (0, 0, h1 - h0))

    def gavl(u, h0, h1):
        return Rekt((X(u), y0, ZB + h0), (0, D, 0), (0, 0, h1 - h0))
    kropp = [plate(R, X_ST, y0, FOT, H_SKJ), plate(R, X_ST, y0 + D, FOT, H_SKJ),
             plate(0, S, y0, H_SKJ, S + FOT), plate(0, S, y0 + D, H_SKJ, S + FOT),
             gavl(0, 0.061 + FOT, S + FOT), gavl(S, H_SKJ, S + FOT)]
    return lys, kropp


def lokalt(lys, kropp, cx, cy, halv=0.20, n=9):
    xs = np.linspace(cx - halv, cx + halv, n)
    ys = np.linspace(cy - halv, cy + halv, n)
    P = np.array([[x, y, ZB + 0.001] for x in xs for y in ys])
    N = np.tile([0, 0, 1.0], (len(P), 1))
    E = E_direkte(P, N, lys, list(STATISK) + list(kropp) + [l_.prim for l_ in lys]) @ LUM
    return E.reshape(n, n)


def skjult_djupn(auge_h, avstand, breidd=0.102):
    """Kor djupt ein ser ned i toppopninga på tvers (m), for eit auge auge_h over bordet."""
    vinkel = math.atan2(auge_h - (S + FOT), avstand)
    return breidd * math.tan(max(vinkel, 0.0))


def main():
    t0 = time.time()
    ut = {"motor": "konsept/lysskisse/lysskisse.py (tal())",
          "rom": "bord 1,4 x 0,7 m, felt 0,6 x 0,4 m, auge 60 cm frå skjermen, augehøgder 25/47/60 cm",
          "foresetnader": ["lambertske opningar, ingen linse", "lampekroppen svart i motoren (skuggar berre)",
                           f"opplys: {int(ROMNING_OPP * 100)} % av lyset frå den øvre diffusoren kjem ut av toppen (overslag)",
                           "lysflux ut av armaturen, ikkje frå diodane"],
          "plasseringar": {}}
    for namn, kw in (("A_til_hogre_utkraging_ut", dict(x0=0.32, y0=0.25)),
                     ("B_til_hogre_snudd_utkraging_inn_over_feltet", dict(x0=0.62, y0=0.25, spegla=True))):
        rad = {}
        for modus, m in (("arbeid_400lm", dict(lm_opp=0)), ("stemning_200lm", dict(lm_ned=0)),
                         ("begge", {})):
            lys, kropp = sveip(**kw, **m)
            d = tal(lys, kropp)
            rad[modus] = {k: (round(float(v), 3) if isinstance(v, (int, float, np.floating)) else None)
                          for k, v in d.items() if not k.startswith("_")}
        lys, kropp = sveip(**kw, lm_opp=0)
        c = lys[0].prim.senter
        E = lokalt(lys, kropp, c[0], c[1])
        rad["pol_under_opninga"] = dict(snitt_lx=round(float(E.mean())), maks_lx=round(float(E.max())),
                                        rett_under_lx=round(float(E[4, 4])))
        ut["plasseringar"][namn] = rad
        print(namn, "felt", rad["arbeid_400lm"]["E_felt"], "U", rad["arbeid_400lm"]["U"])
    ut["kjelda_skjult"] = {
        f"auge_{int(h * 100)}cm_{int(a * 100)}cm_unna": dict(synleg_djupn_mm=round(1000 * skjult_djupn(h, a), 1),
                                                           diffusor_djupn_mm=95.0,
                                                           skjult=skjult_djupn(h, a) < 0.095)
        for h, a in ((0.47, 0.45), (0.60, 0.45), (0.60, 0.30), (1.70, 1.0))}
    for v in ut["kjelda_skjult"].values():
        v["diffusor_djupn_mm"] = round(1000 * (S + FOT - OPP_Z), 1)
        v["skjult"] = v["synleg_djupn_mm"] < v["diffusor_djupn_mm"]
    ut["luminans_cd_m2"] = dict(
        nedre_diffusor_400lm=round(400 / (math.pi * NED_A)),
        ovre_diffusor_200lm=round(200 / (math.pi * OPP_A)),
        toppopninga_snitt=round(200 * ROMNING_OPP / (math.pi * TOPP_A)))
    ut["tid_s"] = round(time.time() - t0, 1)
    (ROT / "kontroll" / "sveip_lys.json").write_text(json.dumps(ut, ensure_ascii=False, indent=1),
                                                     encoding="utf-8")
    print(json.dumps(ut["kjelda_skjult"], ensure_ascii=False))
    print(json.dumps(ut["luminans_cd_m2"]))
    for k, v in ut["plasseringar"].items():
        a = v["arbeid_400lm"]
        s_ = v["stemning_200lm"]
        print(k, "| arbeid: felt %.0f lx U %.2f bak %.0f ansikt %.0f auge25/47/60 %.0f/%.0f/%.0f spegl %.0f"
              % (a["E_felt"], a["U"], a["E_bak"], a["E_ansikt"], a["L_auge25"], a["L_auge47"], a["L_auge60"],
                 a["L_spegl"]),
              "| stemning: felt %.0f bak %.0f auge47 %.0f" % (s_["E_felt"], s_["E_bak"], s_["L_auge47"]),
              "| pol", v["pol_under_opninga"])


if __name__ == "__main__":
    main()
