# -*- coding: utf-8 -*-
"""luftskip.py: det felles grunnlaget for dei tre luftskipsvariantane V9 Skrog, V10 Baug og V11 Spant.

Huda er dopa duk stramma mellom dragarar. Kvar bane søkk svakt inn mellom to dragarar, og
dragaren står som ei skarp line. Banane vekslar svakt i tone. Ingen naglar: lista langs
kantane er bindinga til duken.
  bane(fase)        profil, line og banenummer for ein fase der heile tal er dragarane
  nase_fase(G, ...) fasen til banar som løper saman mot nasen på skjermen og endar i ein kapsel
  ferdig(G, ...)    legg profilen på huda med kant, tone og ruheit som dopa sølv
"""
import numpy as np

from straum import avslutt
from sveip_hud import P_, S_, Z_SKJERM, glatt

ZC = (Z_SKJERM + S_) / 2          # midten av skjermen, der nasen sit (233,75)

# Det micro:bit-matrisa viser: lampa sjølv. Dei to øvste radene er skjermen (stemningslyset),
# dei tre nedste er stamma (arbeidslyset). Lysstyrken i kvar del følgjer lyset han står for.
# Standard er to tredelar av vegen frå arbeid til stemning, slik fastvara viser det.
def ikon(stemning=6, arbeid=3):
    return [[stemning] * 5, [stemning] * 5, [arbeid] * 3 + [0, 0], [arbeid] * 3 + [0, 0], [arbeid] * 3 + [0, 0]]
R_KAPSEL = 15.0                   # nasekapselen: banane endar i ei glatt skive


def bane(fase):
    """Profil 0..1 (1 på dragaren, 0 midt i bana), skarp line på dragaren, og banenummer."""
    u = fase % 1.0
    sag = 1 - 4 * u * (1 - u)                                 # søkk mellom dragarane
    line = np.exp(-(np.minimum(u, 1 - u) / 0.025) ** 2)      # dragaren som ei fin, hard line
    return sag, line, np.floor(fase).astype(int)


def nase_fase(G, avstand=18.0, lengd=90.0, minst=0.30):
    """Fase for banar i skjermen som løper saman mot nasen (s = 0, z = ZC). Langt frå nasen er
    banane vassrette med avstanden `avstand`; mot nasen trekkjer dei seg saman."""
    d = np.minimum(G.S, P_ - G.S)                             # boglengd frå nasen, lik framme og bak
    g = (d / (d + lengd)) ** 0.7 / (360.0 / (360.0 + lengd)) ** 0.7
    return (G.Z - ZC) / np.maximum(g, minst) / avstand + 0.5


def d_kapsel(G):
    return np.hypot(G.avst_s(0.0), G.Z - ZC)


def ferdig(G, profil, line, nummer, ekstra_tone=None, hogd=0.5):
    """Profil og line på huda, banevis tone, matt dopa sølv. Lista langs kantane utan naglar."""
    monster = np.clip(0.88 * profil + 0.12 * line, 0, 1)
    res = avslutt(G, monster, hogd=hogd, naglar=False, rampe=True)
    rng = np.random.default_rng(17)
    tab = rng.uniform(-1, 1, 4096)
    veksel = np.where(nummer % 2 == 0, 1.0, -1.0)
    tone = res["tone"] * (1 + 0.06 * veksel + 0.02 * tab[nummer % 4096])
    if ekstra_tone is not None:
        tone = tone * ekstra_tone
    res["tone"] = tone
    res["rough"] = res["rough"] + 0.06 - 0.05 * line
    res["mat"] = dict(farge=(0.74, 0.735, 0.72), sky=0.45, strok=0.08, metal=0.9, rough=0.44)
    res["mikrobit"] = ikon()
    return res
