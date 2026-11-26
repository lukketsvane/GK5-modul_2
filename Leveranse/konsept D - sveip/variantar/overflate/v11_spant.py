# -*- coding: utf-8 -*-
"""V11 Spant: Baug (V10) med spant på tvers, som sidene på Graf Zeppelin.

Same banar som V10. I tillegg går spant på tvers av banane: loddrett i skjermen kvar 55 mm frå
nasen, og vassrett i stamma kvar 48,75 mm. Eitt spant går gjennom betjeningslina (z = 70), så
messingknappen og micro:bit-matrisa sit i kvart sitt knutepunkt mellom dragar og spant. Mellom
spanta ligg duken som puter: bana søkk mest midt mellom to spant og ligg flatt inn mot spantet.
Kvar rute får sin eigen svake tone, som lappane i dopa duk.
"""
import numpy as np

from luftskip import ferdig
from sveip_hud import P_, PKT_Z, Z_SKJERM, glatt
from v10_baug import baug

SPANT_S = 55.0            # avstand mellom spanta i skjermen, målt frå nasen
SPANT_Z = (Z_SKJERM - PKT_Z) / 2    # 48,75: spant i z = 21,25, 70 (betjeningslina) og 118,75


def felt(G):
    sag, line, nr, dz, dk = baug(G)
    over = G.Z >= Z_SKJERM
    d = np.minimum(G.S, P_ - G.S)
    a_s = np.abs(((d + SPANT_S / 2) % SPANT_S) - SPANT_S / 2)          # avstand til næraste spant i skjermen
    a_z = np.abs(((G.Z - PKT_Z + SPANT_Z / 2) % SPANT_Z) - SPANT_Z / 2)   # i stamma
    a = np.where(over, np.where(d < SPANT_S / 2, 99.0, a_s), a_z)
    pute = 0.35 + 0.65 * glatt(a, 0.0, 14.0)                           # duken ligg flatt inn mot spantet
    spant = np.exp(-(a / 0.4) ** 2)
    sag = sag * pute
    line = np.maximum(line * pute, spant * glatt(dz, 2.5, 4.5))
    rute = np.where(over, np.floor(d / SPANT_S), 50 + np.floor((G.Z - PKT_Z) / SPANT_Z)).astype(int)
    rng = np.random.default_rng(23)
    lapp = 1 + 0.025 * rng.uniform(-1, 1, 2000)[(rute * 37 + nr) % 2000]
    return ferdig(G, sag, line, nr, ekstra_tone=lapp)
