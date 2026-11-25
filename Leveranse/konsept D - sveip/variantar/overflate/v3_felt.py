# -*- coding: utf-8 -*-
"""V3 Felt: dei same nagla panela som V1, med ei mikrooverflate styrt av eit felt.

Feltet er avstanden til messingknappen. Eit sekskantnett av små gropar er pressa i plata.
Gropene er størst kring knappen (Ø 4,6 mm) og krympar jamt til dei er borte 190 mm unna.
Kvar grop får storleik etter feltverdien i sitt eige sentrum, så alle er runde.
"""
import math

import numpy as np

from sveip_hud import (BUE, FLAT, H0, P_, PKT_Z, R_, S_BAK, S_KNAPP_B, S_KNAPP_F, S_STAMME_B, S_STAMME_F,
                       S_VENSTRE, Z_HAKK, Z_SKJERM, glatt)

# same saumar og naglar som V1 Plate (kopiert hit, så varianten står åleine)
Z_SAUM = [Z_HAKK, Z_SKJERM]
S_SAUM = [0.0, BUE, S_STAMME_F, BUE + 132.5, BUE + FLAT, S_VENSTRE[0] + math.pi * R_ / 2,
          S_BAK[0], S_BAK[0] + 62.5, S_STAMME_B, S_BAK[1]]
A, NAGLEDELING = 4.5, 12.0


def panel(G):
    d_s, d_z = G.saum_s(*S_SAUM), G.saum_z(*Z_SAUM)
    d = np.minimum(d_s, d_z)
    h = H0 + 0.12 * glatt(d_s, 4.0, 22.0) * glatt(d_z, 4.0, 22.0)
    h = h - (H0 - 0.06) * glatt(d, 0.45, 0.12)
    n = G.naglar_langs_kant(A, NAGLEDELING)
    for z0 in Z_SAUM:
        for t in (-A, A):
            n = np.maximum(n, G.naglar_z(z0 + t, NAGLEDELING))
    for s0 in S_SAUM:
        for t in (-A, A):
            n = np.maximum(n, G.naglar_s((s0 + t) % P_, NAGLEDELING, fase=NAGLEDELING / 2))
    ids = G.panel_id(S_SAUM, Z_SAUM)
    tone = G.tone_per_panel(ids, 0.10, fro=3) * (1 + 0.04 * G.stoy(45, 5)) * (1 + 0.025 * G.stoy(9, 6))
    rough = 0.40 + 0.05 * (G.tone_per_panel(ids, 1.0, fro=8) - 1)
    return h + n, tone, rough, d

DELING = 6.0
NIVAA = 0.62       # nullnivået er løfta, så gropene kan gå 0,45 mm ned
R_MAKS, DJUPN = 2.3, 0.45
REKKJEVIDD = (12.0, 190.0)


def avst_knapp(s, z):
    d = lambda s0: np.abs(((s - s0 + P_ / 2) % P_) - P_ / 2)
    return np.minimum(np.hypot(d(S_KNAPP_F), z - PKT_Z), np.hypot(d(S_KNAPP_B), z - PKT_Z))


def felt(G):
    h, tone, rough, ds = panel(G)
    h = h + (NIVAA - H0)
    ps = P_ / round(P_ / DELING)          # delinga går opp i omkrinsen
    qz = ps * math.sqrt(3)
    grop = np.zeros_like(h)
    for fs, fz in ((0.0, 0.0), (0.5, 0.5)):   # to rektangelnett som saman er eit sekskantnett
        cs = (np.floor(G.S / ps - fs + 0.5) + fs) * ps
        cz = (np.floor(G.Z / qz - fz + 0.5) + fz) * qz
        f = 1 - glatt(avst_knapp(cs, cz), *REKKJEVIDD)      # feltet i sentrum av gropa: 1 ved knappen
        r = R_MAKS * f
        d = np.hypot(G.S - cs, G.Z - cz)
        g = DJUPN * f * np.clip(1 - (d / np.maximum(r, 1e-6)) ** 2, 0, 1)
        grop = np.maximum(grop, np.where(r > 0.35, g, 0.0))
    # reine marger: ingen gropar inntil saumar, naglar og frie kantar
    grop = grop * glatt(ds, 7.0, 10.5) * glatt(G.kant, 7.0, 10.5)
    return dict(h=h - grop, tone=tone, rough=rough, mat=dict(sky=0.3))
