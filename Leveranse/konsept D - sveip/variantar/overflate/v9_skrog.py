# -*- coding: utf-8 -*-
"""V9 Skrog: breie dukbanar mellom dragarar, langs sveipet i V4.

Banane følgjer same felt som V4 Straum: vassrett langs skjermen, i bogar rundt det indre
hjørnet og loddrett ned stamma. Dei er 14 mm breie ved hjørnet og 26 mm langt ute. Kvar bane
søkk 0,5 mm inn mellom dragarane, dragaren står som ei skarp line, og banane vekslar svakt i
tone. Matt, dopa sølv og ingen naglar.
"""
from luftskip import bane, ferdig
from straum import fase, sveip_felt

P0, P1 = 14.0, 26.0
REKKJEVIDD = 180.0


def felt(G):
    sag, line, nr = bane(fase(sveip_felt(G), P0, P1, REKKJEVIDD))
    return ferdig(G, sag, line, nr)
