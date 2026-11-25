# -*- coding: utf-8 -*-
"""V4 Straum: fine ribber som følgjer eit felt rundt det indre hjørnet.

Feltet er avstanden til den avrunda utskjeringa under skjermen. Nivålinene går vassrett langs
skjermen, i bogar rundt det indre hjørnet og loddrett ned stamma: det er sveipet i namnet.
Nær hjørnet er nivålinene reine sirklar om avrundinga. Lenger ute er dei vinklar med fast
hjørneradius (75 mm), som følgjer toppkanten og venstre boge, så halvsylinderen berre har
loddrette ribber.
Ribbeavstanden følgjer òg feltet: 2,2 mm inst, 5,0 mm ytst. Knappen står på eit glatt land.
Naglar berre langs dei frie kantane, éin for kvar tredje ribbe ytst.
"""
import numpy as np

from sveip_hud import A, H0, P_, R_INN, S_STAMME_F, S_TOPPUNKT, Z_SKJERM, glatt

P0, P1 = 2.2, 5.0          # ribbeavstand inst og ytst
REKKJEVIDD = 150.0         # feltverdien der avstanden er heilt ute i P1
HOGD = 0.34
RHO = 75.0                 # største radius i bogane rundt hjørnet (mm)


def felt(G):
    x = ((G.S - S_TOPPUNKT + P_ / 2) % P_) - P_ / 2                  # 0 i toppunktet på venstre boge
    u = (S_TOPPUNKT - S_STAMME_F) - np.sqrt(x ** 2 + 2.5 ** 2)       # > 0 inn over stamma, framme og bak
    v = G.Z - Z_SKJERM                                              # > 0 oppe i skjermen
    uu, vv = u + R_INN, v + R_INN
    up, vp = np.clip(uu, 0, None), np.clip(vv, 0, None)
    # nivålinene er sirklar om avrundinga i hjørnet til radien når RHO; lenger ute er dei vinklar
    # med fast hjørneradius RHO (rett, boge, rett), utan knekk i overgangen
    sirkel = np.hypot(up, vp)
    senter = ((up + vp) - np.sqrt(np.clip(2 * RHO ** 2 - (up - vp) ** 2, 0, None))) / 2
    hj = np.where(sirkel <= RHO, sirkel,
                  np.where(np.minimum(up, vp) >= senter, senter + RHO, np.maximum(up, vp))) - R_INN
    psi = np.maximum(np.where((uu > 0) & (vv > 0), hj, np.where(uu > 0, u, v)), 0.0)
    # fase: integralet av 1 / avstand(psi)
    tab = np.linspace(0, 420, 4201)
    avst = P0 + (P1 - P0) * glatt(tab, 0.0, REKKJEVIDD)
    fase = np.interp(psi, tab, np.concatenate([[0.0], np.cumsum(0.1 / avst[:-1])]))
    bolgje = 0.5 + 0.5 * np.cos(2 * np.pi * fase)
    # ribbene døyr ut mot ei glatt list langs dei frie kantane og mot eit land rundt knappen
    list_ = glatt(G.kant, 6.5, 9.5) * glatt(G.d_knapp, 11.5, 14.5)
    h = H0 + HOGD * bolgje ** 1.5 * list_
    pkt = G.utan_knapp(G.kontur_punkt(G.fast, A, 15.0), 10.0)
    h = h + G.stempel(pkt)
    tone = 0.95 + 0.045 * G.stoy(90, 7)
    rough = 0.38 * (1 - list_) + (0.44 - 0.14 * bolgje) * list_     # blankslitne toppar, matte dalar
    return dict(h=h, tone=tone, rough=rough, mat=dict(sky=0.2, strok=0.25))
