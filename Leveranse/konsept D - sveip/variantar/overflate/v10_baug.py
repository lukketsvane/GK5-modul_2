# -*- coding: utf-8 -*-
"""V10 Baug: dukbanane i skjermen løper saman mot nasen, som i bauen på eit luftskip.

I skjermen er banane 18 mm breie og vassrette langt frå nasen. Mot nasen trekkjer dei seg
saman og endar i ein glatt nasekapsel (Ø 30 mm) med ein ring rundt. Ned stamma går banane
loddrett, som i V4. Der skjermen møter stamma, ligg ein ringsaum rundt heile forma, som eit
spant. Matt, dopa sølv og ingen naglar.
"""
import numpy as np

from luftskip import R_KAPSEL, bane, d_kapsel, ferdig, nase_fase
from straum import fase, sveip_felt
from sveip_hud import Z_SKJERM, glatt


def baug(G):
    psi = sveip_felt(G)
    over = G.Z >= Z_SKJERM
    f = np.where(over, nase_fase(G), fase(psi, 14.0, 26.0, 180.0) + 1000)
    sag, line, nr = bane(f)
    # ringsaum der skjermen møter stamma: glatt band på 8 mm med ei line i midten
    dz = np.abs(G.Z - Z_SKJERM)
    band = glatt(dz, 2.5, 4.5)
    ring = np.exp(-(dz / 0.45) ** 2)
    # nasekapselen
    dk = d_kapsel(G)
    kapsel = glatt(dk, R_KAPSEL, R_KAPSEL + 4.0)
    kring = np.exp(-((dk - R_KAPSEL) / 0.5) ** 2)
    sag = sag * band * kapsel
    line = np.maximum(line * band * kapsel, np.maximum(ring, kring))
    return sag, line, nr, dz, dk


def felt(G):
    sag, line, nr, _, _ = baug(G)
    return ferdig(G, sag, line, nr)
