# -*- coding: utf-8 -*-
"""V1 Plate: nagla aluminiumspanel der saumane følgjer geometrien til lampa.

Vassrette saumar i underkanten av skjermen og i overkanten av hakket. Loddrette saumar der
flatene møter bogane, i forlenginga av stammekanten, midt på stamma, i toppunktet på venstre
boge og i nasen. Éi naglerekkje på kvar side av kvar saum og langs alle frie kantar.
"""
import math

import numpy as np

from sveip_hud import (BUE, FLAT, H0, P_, R_, S_BAK, S_STAMME_B, S_STAMME_F, S_VENSTRE, Z_HAKK,
                       Z_SKJERM, glatt)

Z_SAUM = [Z_HAKK, Z_SKJERM]
S_SAUM = [0.0, BUE, S_STAMME_F, BUE + 132.5, BUE + FLAT, S_VENSTRE[0] + math.pi * R_ / 2,
          S_BAK[0], S_BAK[0] + 62.5, S_STAMME_B, S_BAK[1]]
A = 4.5        # naglerekkja står 4,5 mm frå saumen
DELING = 12.0


def felt(G):
    d_s, d_z = G.saum_s(*S_SAUM), G.saum_z(*Z_SAUM)
    d = np.minimum(d_s, d_z)
    # panelet bular svakt mellom naglerekkjene (produkt av to mjuke steg: ingen diagonale knekkar),
    # saumen er ei fin fuge
    h = H0 + 0.12 * glatt(d_s, 4.0, 22.0) * glatt(d_z, 4.0, 22.0)
    h = h - (H0 - 0.06) * glatt(d, 0.45, 0.12)
    n = G.naglar_langs_kant(A, DELING)
    for z0 in Z_SAUM:
        for t in (-A, A):
            n = np.maximum(n, G.naglar_z(z0 + t, DELING))
    for s0 in S_SAUM:
        for t in (-A, A):
            n = np.maximum(n, G.naglar_s((s0 + t) % P_, DELING, fase=DELING / 2))
    h = h + n
    ids = G.panel_id(S_SAUM, Z_SAUM)
    tone = G.tone_per_panel(ids, 0.10, fro=3) * (1 + 0.04 * G.stoy(45, 5)) * (1 + 0.025 * G.stoy(9, 6))
    rough = 0.40 + 0.05 * (G.tone_per_panel(ids, 1.0, fro=8) - 1)
    return dict(h=h, tone=tone, rough=rough, mat=dict(sky=0.6))
