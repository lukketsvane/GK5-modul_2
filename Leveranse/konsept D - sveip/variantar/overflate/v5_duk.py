# -*- coding: utf-8 -*-
"""V5 Duk: ytterhuda til eit luftskip. Dopa lerret stramma over skjulte loddrette ribber.

22 ribber, spegla om nasen og låste til knappen: knappen står midt på ei ribbe framme og bak,
og tangentlinene fell midt i eit felt. Duken er stram: han går rett frå ribbe til ribbe med
ein knekk over kvar ribbe og eit søkk på 0,95 mm midt i feltet. Over kvar ribbe ligg ei dopa
dekkremse på 9 mm. Skjermen er ramma av to ringremser, og knappen står på ein rund
forsterkingslapp, som rundt beslaga i luftskipsduken. Ingen naglar.
"""
import numpy as np

from sveip_hud import P_, S_, S_KNAPP_F, Z_SKJERM, glatt

FELT_1 = S_KNAPP_F / 5                         # 32,99 mm frå nasen til knappen
FELT_2 = (P_ / 2 - S_KNAPP_F) / 6              # 32,49 mm frå knappen til toppunktet på venstre boge
SIG = 0.95         # kor djupt duken søkk midt mellom to ribber (mm)
TOPP = 1.25        # nivået over ribbene
REMSE_B, REMSE_H = 9.0, 0.22
Z_RING = Z_SKJERM + REMSE_B / 2 + 2.0          # 174,0: heile remsa ligg på duken, 2 mm frå kanten
Z_TOPP = S_ - REMSE_B / 2 - 2.0                # 293,5
R_LAPP = 11.0


def felt(G):
    d = np.minimum(G.S, P_ - G.S)                                   # avstand frå nasen, lik framme og bak
    fb = np.where(d <= S_KNAPP_F, FELT_1, FELT_2)
    lokal = np.where(d <= S_KNAPP_F, d, d - S_KNAPP_F)
    u = (lokal % fb) / fb
    d_ribbe = np.minimum(u, 1 - u) * fb                             # avstand til næraste ribbe (mm)
    felt_nr = np.where(d <= S_KNAPP_F, lokal // fb, 5 + lokal // fb).astype(int)
    # stram duk: parabel mellom ribbene, med knekk 2 mm frå ribbesenteret
    halv = fb / 2 - 2.0
    profil = 1 - (1 - np.clip(d_ribbe - 2.0, 0, None) / halv) ** 2
    d_ring = np.minimum(np.abs(G.Z - Z_RING), np.abs(G.Z - Z_TOPP))
    stramt = glatt(G.kant, 1.0, 12.0) * glatt(d_ring, REMSE_B / 2, REMSE_B / 2 + 12.0)
    stramt = stramt * glatt(G.d_knapp, R_LAPP, R_LAPP + 6.0)
    h = TOPP - SIG * profil * stramt

    def remse(avst):
        return glatt(avst, REMSE_B / 2, REMSE_B / 2 - 0.5)
    lodd = np.maximum(remse(d_ribbe), glatt(G.d_knapp, R_LAPP, R_LAPP - 0.5))   # remser og knappelapp
    ring = remse(d_ring)
    h = h + REMSE_H * (lodd + ring)
    paa_remse = np.maximum(lodd, ring)
    rng = np.random.default_rng(4)
    tone = (1 + 0.015 * rng.uniform(-1, 1, 12)[felt_nr % 12]) * (1 + 0.012 * G.stoy(140, 11))
    tone = tone * (1 + 0.03 * paa_remse)
    rough = 0.40 - 0.08 * paa_remse                                 # fleire lag dope er glattare
    return dict(h=h, tone=tone, rough=rough, knapp_nivaa=TOPP + REMSE_H,
                mat=dict(farge=(0.78, 0.77, 0.74), metal=0.92, rough=0.40, sky=0.2, strok=0.15, vev=0.25,
                         floyel=0.2))
