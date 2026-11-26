# -*- coding: utf-8 -*-
"""V8 Labyrint: ein reaksjon-diffusjon-labyrint, som eit fingeravtrykk, med storleik styrt av sveipet i V4.

Mønsteret er rekna med Gray-Scott-likningane (F 0,037, k 0,06) på den utbretta plata, 0,5 mm
rutenett, frå tilfeldige frø. Diffusjonen følgjer feltet i V4, så mønsteret er
finast ved det indre hjørnet (om lag 5 mm mellom linene) og grovast langt ute (om lag 8,5 mm).
Felt der mønsteret døyr ut, blir sådde på nytt og rekna vidare.
Same kant og knappeland som V4. Mønsteret blir lagra i cache/ første gong.
"""
from pathlib import Path

import numpy as np
from scipy import ndimage

from straum import avslutt, sveip_felt
from sveip_hud import Gitter, glatt

CACHE = Path(__file__).resolve().parent / "cache" / "v8_labyrint.npy"
F, K, DU, DV = 0.037, 0.06, 0.16, 0.08
M0, M1 = 0.30, 0.80            # skalering av diffusjonen: finare ved hjørnet, grovare ute
STEG = 9000


def lap(a):
    return np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1) + np.roll(a, -1, 1) - 4 * a


def rekn():
    G = Gitter(0.5)
    psi = sveip_felt(G)
    m = M0 + (M1 - M0) * glatt(psi, 0.0, 200.0)
    # start: tette, tilfeldige frø over heile plata
    rng = np.random.default_rng(8)
    frø = rng.random(psi.shape) < 0.12
    V = np.where(frø, 0.25, 0.0) + 0.02 * rng.random(psi.shape)
    U = np.where(frø, 0.5, 1.0)
    def kjør(n):
        nonlocal U, V
        for _ in range(n):
            uvv = U * V * V
            U += m * DU * lap(U) - uvv + F * (1 - U)
            V += m * DV * lap(V) + uvv - (F + K) * V
    kjør(STEG)
    # så på nytt der mønsteret har døydd ut (felt utan liner, over om lag 10 mm), og rekn vidare
    for runde in range(3):
        daudt = ndimage.gaussian_filter(V, 8.0, mode="wrap") < 0.04
        if not daudt.any():
            break
        nye = daudt & (rng.random(psi.shape) < 0.12)
        V = np.where(nye, 0.25, V)
        U = np.where(nye, 0.5, U)
        kjør(4000)
    CACHE.parent.mkdir(exist_ok=True)
    np.save(CACHE, V.astype(np.float32))
    return V


def felt(G):
    V = np.load(CACHE) if CACHE.exists() else rekn()
    # frå 0,5 mm-rutenettet til G (rundt i s, kant i z)
    si = G.S / (719.87 / V.shape[0])
    zi = G.Z / (300.0 / (V.shape[1] - 1))
    v = ndimage.map_coordinates(np.concatenate([V, V[:3]], axis=0), [si, zi], order=3, mode="nearest")
    m = glatt(v, 0.10, 0.26)
    return avslutt(G, m)
