# -*- coding: utf-8 -*-
"""Monteringsrettleiing for Sveip i IKEA-stil: strekteikning frå CAD-en, éi handling per side.

Køyr frå cad/: python sveip_rettleiing.py
Skriv montering/sveip_montering.pdf og montering/side-NN.png (A4 liggjande).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import cadquery as cq  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

import sveip_samanstilling as SA  # noqa: E402
from sveip_geometri import P0  # noqa: E402
from sveip_teikning import MM, former, hlr, proj, tekst, teikn  # noqa: E402

ROT = Path(__file__).resolve().parent.parent
UT = ROT / "montering"
UT.mkdir(exist_ok=True)
A4 = (297.0, 210.0)
ISO = ((-1.0, -1.35, 0.85), (1.35, -1.0, 0.0))
UNDER = ((-1.0, -1.35, -1.0), (1.35, -1.0, 0.0))
MODUL = ["D02", "D03", "D04", "D04L", "D05", "D05L", "D06", "D07", "D08", "D09", "D09K", "D11",
         "D11K", "D11J", "D14", "K01", "K02", "K03", "K05", "K06", "K07", "K10", "K11", "K12",
         "K13", "K15", "K18", "K19", "K20", "K21"]
UTAN_CELLE = [i for i in MODUL if i != "K01"]


def side(nr, tittel=None):
    fig = plt.figure(figsize=(A4[0] / 25.4, A4[1] / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, A4[0]); ax.set_ylim(0, A4[1]); ax.set_aspect("equal"); ax.axis("off")
    if nr:
        tekst(ax, 14, A4[1] - 22, str(nr), 30)
    if tittel:
        tekst(ax, 30 if nr else 14, A4[1] - 18, tittel, 11, color="#333")
    return fig, ax


def plasser(ax, liner, cx, cy, s):
    us = [p[0] for pts, _ in liner for p in pts]
    vs = [p[1] for pts, _ in liner for p in pts]
    x0 = cx - s * (min(us) + max(us)) / 2
    y0 = cy - s * (min(vs) + max(vs)) / 2
    teikn(ax, liner, x0, y0, s)
    return x0, y0


def pil(ax, a, b, x0, y0, s, retn, lw=1.2):
    pa = proj(a, *retn)
    pb = proj(b, *retn)
    ax.annotate("", (x0 + pb[0] * s, y0 + pb[1] * s), (x0 + pa[0] * s, y0 + pa[1] * s),
                arrowprops=dict(arrowstyle="-|>", lw=lw * MM / 2, color="k", mutation_scale=14))


def ring(ax, x, y, r=16):
    ax.add_patch(plt.Circle((x, y), r, fill=False, lw=0.35 * MM))


def lagre(pdf, fig, nr):
    pdf.savefig(fig)
    fig.savefig(UT / f"side-{nr:02d}.png", dpi=130)
    plt.close(fig)


def main():
    with PdfPages(UT / "sveip_montering.pdf") as pdf:
        # 1 framside
        fig, ax = side(0)
        lin = hlr(former({"D01", "D12F", "D13F", "D12B", "D13B", "K08", "E01"}), *ISO)
        plasser(ax, lin, 150, 110, 0.42)
        tekst(ax, 14, 20, "Sveip", 28)
        tekst(ax, 14, 12, "Montering og service · rev. B", 9, color="#333")
        lagre(pdf, fig, 1)

        # 2 delar og verktøy
        fig, ax = side(0, "Delar og verktøy")
        grupper = [("Kropp", ["D01"], (60, 125), 0.22), ("Innmatsmodul", UTAN_CELLE, (152, 125), 0.22),
                   ("2 x berøringspunkt", ["D12F", "D13F"], (238, 140), 1.6),
                   ("Celle 21700", ["K01"], (238, 92), 0.9), ("Luke", ["D10"], (150, 52), 0.5),
                   ("4 x M3 x 6", ["K09"], (60, 45), 0.9), ("2 x myntskrue", ["K14"], (100, 45), 0.9),
                   ("4 x fot", ["K08"], (235, 45), 0.7)]
        for namn, ids, (cx, cy), s in grupper:
            f = former(set(ids))
            if ids in (["K09"], ["K14"], ["K08"]):
                f = [f[0].Solids()[0]]          # éin av fleire like
            lin = hlr(f, *ISO)
            plasser(ax, lin, cx, cy, s)
            vs = [p_[1] for pts, _ in lin for p_ in pts]
            tekst(ax, cx, cy - s * (max(vs) - min(vs)) / 2 - 7, namn, 8, ha="center")
        tekst(ax, 14, 14, "Verktøy: unbrakonøkkel 2,0 mm og ein mynt.", 9)
        lagre(pdf, fig, 2)

        # 3 modulen ned gjennom toppen
        fig, ax = side(1, "Senk innmatsmodulen ned gjennom toppen")
        f = former({"D01"}) + [s_.translate(cq.Vector(0, 0, 230)) for s_ in former(set(UTAN_CELLE))]
        s = 0.34
        x0, y0 = plasser(ax, hlr(f, *ISO), 150, 100, s)
        pil(ax, (150, 0, 430), (150, 0, 330), x0, y0, s, ISO)
        tekst(ax, 205, 30, "USB-C-kontakten i taket skal stå over hakket.", 8.5)
        lagre(pdf, fig, 3)

        # 4 fire skruar nedanfrå
        fig, ax = side(2, "Legg lampa på ryggen. Fire skruar gjennom botnflensane")
        f = former({"D01", "D02"}) + [s_.translate(cq.Vector(0, 0, -40)) for s_ in former({"K09"})]
        s = 0.40
        x0, y0 = plasser(ax, hlr(f, *UNDER), 140, 110, s)
        for x in P0.fot_x:
            for sy in (-1, 1):
                pil(ax, (x, sy * P0.fl_yc, -40), (x, sy * P0.fl_yc, -8), x0, y0, s, UNDER, lw=0.9)
        tekst(ax, 190, 36, "Mjukt underlag, hald innmaten inne med den andre handa.", 8.5)
        tekst(ax, 190, 29, "M3 x 6, 2,0 mm unbrako, høgst 0,6 Nm. Tannskiva under skruen framme til venstre.", 8.5)
        lagre(pdf, fig, 4)

        # 5 berøringspunkta
        fig, ax = side(3, "Smett berøringspunkta inn, framme og bak")
        flytt = {"D12F": (0, -45, 0), "D13F": (0, -45, 0), "D12B": (0, 45, 0), "D13B": (0, 45, 0)}
        f = former({"D01"}) + former({"D12F", "D13F", "D12B", "D13B"}, flytt)
        s = 0.42
        x0, y0 = plasser(ax, hlr(f, *ISO), 140, 105, s)
        pil(ax, (P0.pkt_x, -95, P0.pkt_z), (P0.pkt_x, -58, P0.pkt_z), x0, y0, s, ISO)
        tekst(ax, 190, 30, "Trykk til det klikkar. Kragen ligg an mot plata.", 8.5)
        lagre(pdf, fig, 5)

        # 6 føter, celle og luke
        fig, ax = side(4, "Føter, celle og luke")
        flytt = {"K08": (0, 0, -25), "K01": (0, 0, -60), "D10": (0, 0, -95), "K14": (0, 0, -120)}
        f = former({"D01", "D02"}) + former({"K08", "K01", "D10", "K14"}, flytt)
        s = 0.40
        x0, y0 = plasser(ax, hlr(f, *UNDER), 140, 112, s)
        pil(ax, (120, 0, -150), (120, 0, -105), x0, y0, s, UNDER, lw=0.9)
        tekst(ax, 190, 41, "Trykk føtene over skruehovuda.", 8.5)
        tekst(ax, 190, 34, "Pluss (+) mot hakket, trekkbandet under cella. Li-ion 21700, 3,6 V,", 8.5)
        tekst(ax, 190, 27, "til dømes Samsung INR21700-50E. Vernet sit på kortet.", 8.5)
        lagre(pdf, fig, 6)

        # 7 i bruk
        fig, ax = side(5, "Kople til og prøv")
        f = former({"D01", "D12F", "D13F", "K08", "E01"})
        s = 0.42
        x0, y0 = plasser(ax, hlr(f, *ISO), 120, 105, s)
        p = proj((P0.pkt_x, -P0.R, P0.pkt_z), *ISO)
        ring(ax, x0 + p[0] * s, y0 + p[1] * s, 9)
        tekst(ax, 200, 150, "Rør kort: på og av. Ein treng ikkje trykkje.", 9)
        tekst(ax, 200, 141, "Hald fingeren på: frå stemningslys (opp, varmt)", 9)
        tekst(ax, 200, 134, "til arbeidslys (ned, 3000 K) og attende.", 9)
        tekst(ax, 200, 122, "USB-C 5 V, minst 1,5 A og C-til-C-leidning for fullt lys.", 9)
        tekst(ax, 200, 115, "Snu lampa: utkraginga skal liggje inn", 9)
        tekst(ax, 200, 108, "over arbeidsflata.", 9)
        lagre(pdf, fig, 7)

        # 8 service
        fig, ax = side(0, "Service: celle og lysmodul")
        f = former({"D01"}) + [s_.translate(cq.Vector(0, 0, 200)) for s_ in former({"D03", "D04", "D05", "D06",
                                                                                      "D07", "D08", "K05", "K21"})]
        s = 0.30
        x0, y0 = plasser(ax, hlr(f, *ISO), 95, 100, s)
        tekst(ax, 175, 158, "Trekk alltid ut USB-C først.", 9)
        tekst(ax, 175, 150, "Celle: to myntskruar, under 1 minutt.", 9)
        tekst(ax, 175, 141, "Lysmodul: ta ut cella, lirk ut dei to messingknappane,", 9)
        tekst(ax, 175, 134, "fire skruar nedanfrå, løft innmaten ut, ta av øvre", 9)
        tekst(ax, 175, 127, "diffusor, éin plugg og fire skruar. Om lag 5 minutt.", 9)
        tekst(ax, 175, 115, "Ingenting er limt. Aluminium, PMMA, PC, POM og", 9)
        tekst(ax, 175, 108, "kretskort kan skiljast for gjenvinning.", 9)
        lagre(pdf, fig, 8)
    print("skreiv", UT / "sveip_montering.pdf")


if __name__ == "__main__":
    main()
