# -*- coding: utf-8 -*-
"""V4 Straum: fine ribber som følgjer eit felt rundt det indre hjørnet.

Feltet er avstanden til den avrunda utskjeringa under skjermen. Nivålinene går vassrett langs
skjermen, i bogar rundt det indre hjørnet og loddrett ned stamma: det er sveipet i namnet.
Nær hjørnet er nivålinene reine sirklar om avrundinga. Lenger ute er dei vinklar med fast
hjørneradius (75 mm), som følgjer toppkanten og venstre boge, så halvsylinderen berre har
loddrette ribber.
Ribbeavstanden følgjer òg feltet: 2,2 mm inst, 5,0 mm ytst. Knappen står på eit glatt land.
Naglar berre langs dei frie kantane, éin for kvar tredje ribbe ytst.
Feltet og kanten står i straum.py, som dei feltstyrte variantane etter V4 deler.
"""
import numpy as np

from straum import avslutt, fase, sveip_felt

P0, P1 = 2.2, 5.0          # ribbeavstand inst og ytst
REKKJEVIDD = 150.0         # feltverdien der avstanden er heilt ute i P1


def felt(G):
    bolgje = 0.5 + 0.5 * np.cos(2 * np.pi * fase(sveip_felt(G), P0, P1, REKKJEVIDD, maks=420.0))
    return avslutt(G, bolgje)
