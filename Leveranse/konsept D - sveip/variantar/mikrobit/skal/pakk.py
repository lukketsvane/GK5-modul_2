# -*- coding: utf-8 -*-
"""pakk.py: alle skalvariantane av M1 i éi 3MF-fil til Bambu Lab (eitt prosjekt, éi plate).

Kvar variant ligg som eit eige objekt, opp ned med toppkanten på plata, slik M1 skal printast.
Alle objekta har same farge, så Bambu Studio ikkje ber om filamentbyte. Fila følgjer kjerne-
spesifikasjonen til 3MF (som Sveip_mini_alle_delar.3mf), ikkje Bambus eigne prosjektfelt.

Les print/<namn>.3mf frå skal.py. Køyr frå skal/ etter at variantane er bygde (python3 skal.py <namn>):
    python3 pakk.py                      gore pute luftskip fasett
    python3 pakk.py gore luftskip        berre desse
    python3 pakk.py --med-glatt          legg den glatte kroppen først, som referanse
Skriv print/Sveip_mini_skal_alle_variantar.3mf, .png (plata ovanfrå) og .json (kontrollane).
Stoppar om eit nett ikkje er lukka, ein del ligg utanfor plata eller i sperresona, eller to
delar ligg nærare kvarandre enn 8 mm.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

HER = Path(__file__).resolve().parent
sys.path.insert(0, str(HER.parent))
sys.path.insert(0, str(HER))

import mini_print as MP                    # noqa: E402
import skal as SK                          # noqa: E402
import re                                  # noqa: E402
import zipfile                             # noqa: E402

PLATE = 256.0
SPERRE = (18.0, 28.0)                      # P1S: ingen plass framme til venstre (x < 18 og y < 28)
HOGD = 250.0
AVSTAND = 10.0                             # mellom delane (minst 8)
KOLONNAR = 2
STANDARD = ["gore", "pute", "luftskip", "fasett"]
UT = HER / "print" / "Sveip_mini_skal_alle_variantar"


def les_3mf(sti):
    """Nettet frå 3MF-fila til varianten (alt i printstilling, opp ned), med indeksane urørte.
    STL-fila går ikkje: ho lagrar kvart hjørne for seg, og å slå saman att gjev degenererte trekantar."""
    with zipfile.ZipFile(sti) as z:
        xml = z.read("3D/3dmodel.model").decode("utf-8")
    v = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', xml), dtype=np.float64)
    t = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', xml), dtype=np.int64)
    return v, t


def plasser(delar):
    """Rutenett med KOLONNAR kolonnar, midt på plata. Kolonnebreidda er den breiaste delen."""
    rader = math.ceil(len(delar) / KOLONNAR)
    bredde = [max((d["storleik"][0] for d in delar[k::KOLONNAR]), default=0) for k in range(KOLONNAR)]
    djupn = [max((d["storleik"][1] for d in delar[r * KOLONNAR:(r + 1) * KOLONNAR]), default=0) for r in range(rader)]
    tot_x = sum(bredde) + AVSTAND * (KOLONNAR - 1)
    tot_y = sum(djupn) + AVSTAND * (rader - 1)
    x0, y0 = PLATE / 2 - tot_x / 2, PLATE / 2 - tot_y / 2
    for i, d in enumerate(delar):
        r, k = divmod(i, KOLONNAR)
        cx = x0 + sum(bredde[:k]) + AVSTAND * k + bredde[k] / 2
        cy = y0 + sum(djupn[:r]) + AVSTAND * r + djupn[r] / 2
        d["senter"] = (cx, cy)
    return delar


def overheng_areal(v, t, plate=0.3):
    """Samla areal (mm²) av flater som vender nedover meir enn 45° og ikkje ligg på plata.
    mini_print.overheng slår saman etter høgd og droppar små grupper, så relieff blir ikkje talt."""
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    n = np.cross(b - a, c - a)
    ar = np.linalg.norm(n, axis=1) / 2
    nz = n[:, 2] / np.maximum(2 * ar, 1e-12)
    zmin = np.minimum(np.minimum(a[:, 2], b[:, 2]), c[:, 2])
    return float(ar[(nz < -math.sqrt(0.5)) & (zmin > plate)].sum())


def avstand_boksar(a, b):
    dx = max(a[0] - b[1], b[0] - a[1], 0.0)
    dy = max(a[2] - b[3], b[2] - a[3], 0.0)
    return math.hypot(dx, dy)


def main(namn):
    delar = []
    for n in namn:
        sti = HER / "print" / f"{n}.3mf"
        if not sti.exists():
            sys.exit(f"manglar {sti.relative_to(HER)}: køyr python3 skal.py {n}")
        v, t = les_3mf(sti)
        bb = (v[:, 0].min(), v[:, 0].max(), v[:, 1].min(), v[:, 1].max())
        delar.append(dict(namn=n, v=v, t=t, storleik=(bb[1] - bb[0], bb[3] - bb[2], float(v[:, 2].max() - v[:, 2].min()))))
    plasser(delar)

    objekt, rapport, boksar = [], [], []
    for d in delar:
        cx, cy = d["senter"]
        v = d["v"].copy()
        v[:, 0] += cx - (v[:, 0].min() + v[:, 0].max()) / 2
        v[:, 1] += cy - (v[:, 1].min() + v[:, 1].max()) / 2
        v[:, 2] -= v[:, 2].min()
        lukka, vol = MP.kontroll_nett(v, d["t"])
        assert lukka and vol > 0, f"{d['namn']}: nettet er ikkje lukka eller har feil retning"
        bb = (v[:, 0].min(), v[:, 0].max(), v[:, 1].min(), v[:, 1].max(), v[:, 2].max())
        assert 0 <= bb[0] and bb[1] <= PLATE and 0 <= bb[2] and bb[3] <= PLATE and bb[4] <= HOGD, f"{d['namn']} ligg utanfor plata"
        assert not (bb[0] < SPERRE[0] and bb[2] < SPERRE[1]), f"{d['namn']} ligg i sperresona"
        oh = overheng_areal(v, d["t"])
        boksar.append(bb[:4])
        objekt.append((f"M1_kropp_{d['namn']}", (v, d["t"])))
        rapport.append(dict(namn=d["namn"], trekantar=int(len(d["t"])), volum_mm3=round(vol, 0), masse_g_pla=round(vol / 1000 * 1.24, 1),
                            storleik_mm=[round(x, 1) for x in d["storleik"]], senter=[round(cx, 1), round(cy, 1)],
                            overheng_mm2=round(oh, 0)))
    minst = min((avstand_boksar(boksar[i], boksar[j]) for i in range(len(boksar)) for j in range(i + 1, len(boksar))), default=99.0)
    assert minst >= 8.0, f"delane ligg for tett ({minst:.1f} mm)"

    sti = UT.with_suffix(".3mf")
    MP.skriv_3mf(sti, objekt, "Sveip mini, skalvariantar av M1", ["lampefarge"] * len(objekt))
    ut = dict(fil=sti.name, delar=rapport, minste_avstand_mm=round(minst, 1),
              masse_g_pla=round(sum(r["masse_g_pla"] for r in rapport), 1), storleik_fil_mb=round(sti.stat().st_size / 1e6, 1))
    (UT.with_suffix(".json")).write_text(json.dumps(ut, indent=1, ensure_ascii=False), encoding="utf-8")
    teikn_plate(delar, UT.with_suffix(".png"))
    return ut


def teikn_plate(delar, sti):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(figsize=(7.2, 7.2), dpi=130)
    ax.add_patch(Rectangle((0, 0), PLATE, PLATE, fc="#f3f2ee", ec="#444", lw=1.2))
    ax.add_patch(Rectangle((0, 0), SPERRE[0], SPERRE[1], fc="#d9b3b0", ec="none", alpha=0.7))
    for d in delar:
        cx, cy = d["senter"]
        w, h, z = d["storleik"]
        ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, fc="#c9c7c1", ec="#222", lw=1.0))
        ax.text(cx, cy, d["namn"], ha="center", va="center", fontsize=11, weight="bold")
        ax.text(cx, cy - h / 2 - 3, f"{w:.0f} × {h:.0f} × {z:.0f} mm", ha="center", va="top", fontsize=7, color="#444")
    ax.set_xlim(-4, PLATE + 4)
    ax.set_ylim(-4, PLATE + 4)
    ax.set_aspect("equal")
    ax.set_title("Bambu Lab P1S · alle skalvariantar på éi plate, sett ovanfrå (framkant nede)", fontsize=9)
    ax.tick_params(labelsize=7)
    fig.tight_layout()
    fig.savefig(sti)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    namn = a or list(STANDARD)
    if "--med-glatt" in sys.argv:
        namn = ["glatt"] + [n for n in namn if n != "glatt"]
    print(json.dumps(main(namn), indent=1, ensure_ascii=False))
