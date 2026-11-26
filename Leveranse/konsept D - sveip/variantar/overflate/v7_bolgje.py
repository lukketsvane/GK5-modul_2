# -*- coding: utf-8 -*-
"""V7 Bølgje: V4 Straum med ei mjuk bølgje i feltet, som sanddyner.

Same sveip som V4, men feltet er forskyvd av ei lågfrekvent bølgje (om lag 110 mm, opptil
13 mm utslag). Bølgja er spegla om nasen, så framside og bakside møtest reint, og ho er null ved det indre hjørnet og veks utover, så sveipet startar stramt i
hjørnet og løyser seg opp i bølgjer mot toppkanten og ned stamma. Same kant og knappeland som V4.
"""
import numpy as np

from straum import avslutt, fase, sveip_felt
from sveip_hud import S_TOPPUNKT, glatt

P0, P1 = 2.4, 5.0
REKKJEVIDD = 150.0
UTSLAG = 13.0


def felt(G):
    psi = sveip_felt(G)
    w = G.stoy(110, 21)
    w = np.where(np.arange(G.ns)[:, None] > G.ns // 2, w[(G.ns - np.arange(G.ns)) % G.ns], w)  # spegla om nasen
    # null i hjørnet, og dempa mot møtelinene i nasen og på venstre boge, så fram og bak møtest reint
    demp = glatt(psi, 8.0, 90.0) * glatt(G.avst_s(S_TOPPUNKT), 10.0, 70.0) * glatt(G.avst_s(0.0), 10.0, 70.0)
    bolgje_felt = w * UTSLAG * demp
    m = 0.5 + 0.5 * np.cos(2 * np.pi * fase(np.clip(psi + bolgje_felt, 0, None), P0, P1, REKKJEVIDD))
    return avslutt(G, m)
