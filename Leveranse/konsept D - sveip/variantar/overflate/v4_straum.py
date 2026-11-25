# -*- coding: utf-8 -*-
"""V4 Straum: fine ribber som følgjer eit felt rundt det indre hjørnet.

Feltet er avstanden til utskjeringa under skjermen. Nivålinene går vassrett langs skjermen,
i bogar rundt det indre hjørnet og loddrett ned stamma: det er sveipet i namnet.
Ribbeavstanden følgjer òg feltet: 2,2 mm inst ved hjørnet, 5,5 mm ytst.
Naglar berre langs dei frie kantane og i nasesaumen.
"""
import numpy as np

from sveip_hud import (H0, P_, R_INN, S_, S_STAMME_B, S_STAMME_F, X_STAMME, Z_SKJERM, glatt)

P0, P1 = 2.2, 5.5          # ribbeavstand inst og ytst
REKKJEVIDD = 150.0         # feltverdien der avstanden er heilt ute i P1
HOGD = 0.34


def felt(G):
    # avstand til utskjeringa (x > X_STAMME og z < Z_SKJERM), rekna i den utbretta plata, framme og bak
    def d_side(s_kant, retning):
        u = retning * (((G.S - s_kant + P_ / 2) % P_) - P_ / 2)   # > 0 inn over stamma
        v = G.Z - Z_SKJERM                                         # > 0 oppe i skjermen
        return np.where((u > 0) & (v > 0), np.hypot(u, v), np.where(u > 0, u, np.maximum(v, 0)))
    a = d_side(S_STAMME_F, 1.0)
    b = d_side(S_STAMME_B, -1.0)
    k = 22.0                                                       # mjuk overgang der felta møtest
    psi = -k * np.log(np.exp(-a / k) + np.exp(-b / k))
    psi = np.maximum(psi, 0.0)
    # fase: integralet av 1 / avstand(psi)
    tab = np.linspace(0, 420, 4201)
    avst = P0 + (P1 - P0) * glatt(tab, 0.0, REKKJEVIDD)
    fase_tab = np.concatenate([[0.0], np.cumsum(0.1 / avst[:-1])])
    fase = np.interp(psi, tab, fase_tab)
    bolgje = 0.5 + 0.5 * np.cos(2 * np.pi * fase)
    h = H0 + HOGD * bolgje ** 1.5
    # ribbene døyr ut mot dei frie kantane, der ei glatt list med naglar tek over
    list_ = glatt(G.kant, 6.5, 9.5)
    h = H0 + (h - H0) * list_
    n = G.naglar_langs_kant(3.6, 10.0, r=0.85, h=0.32)
    dn = G.avst_s(0.0)
    h = H0 + (h - H0) * glatt(dn, 6.5, 9.5)
    h = h - 0.2 * glatt(dn, 0.5, 0.15)
    for ds in (-3.6, 3.6):
        n = np.maximum(n, G.naglar_s(ds % P_, 10.0, r=0.85, h=0.32, fase=5.0, z_fra=Z_SKJERM, z_til=S_))
    return dict(h=h + n, tone=1 + 0.02 * G.stoy(60, 7), mat=dict(sky=0.2, rough=0.38))
