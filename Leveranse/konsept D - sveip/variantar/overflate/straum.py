# -*- coding: utf-8 -*-
"""straum.py: det felles grunnlaget for V4 og dei feltstyrte variantane etter han.

  sveip_felt(G)  avstanden til den avrunda utskjeringa under skjermen (feltet i V4 Straum):
                 vassrett langs skjermen, sirklar rundt det indre hjørnet, loddrett ned stamma
  fase(d, ...)   fasen til ei ribbe med avstand som veks frå p0 til p1 langs feltet d
  avslutt(G, m)  legg mønsteret m (0 til 1, 1 er toppen av ribba) på huda med same kant som V4:
                 glatt list langs dei frie kantane, glatt land rundt knappen, naglar berre i lista
"""
import numpy as np

from sveip_hud import A, H0, P_, R_INN, R_KNAPP, RAMPE, S_STAMME_F, S_TOPPUNKT, Z_SKJERM, glatt, mjukmin

RHO = 75.0                 # største radius i bogane rundt hjørnet (mm)


def sveip_felt(G):
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
    return np.maximum(np.where((uu > 0) & (vv > 0), hj, np.where(uu > 0, u, v)), 0.0)


def fase(d, p0, p1, rekkjevidd, maks=900.0):
    """Fasen (tal på ribber) i avstanden d, når ribbeavstanden veks mjukt frå p0 til p1 over rekkjevidda."""
    tab = np.linspace(0, maks, int(maks * 10) + 1)
    avst = p0 + (p1 - p0) * glatt(tab, 0.0, rekkjevidd)
    return np.interp(d, tab, np.concatenate([[0.0], np.cumsum(0.1 / avst[:-1])]))


def avslutt(G, monster, hogd=0.34, sky=0.2, strok=0.25, naglar=True, rampe=False):
    """Same kant, knappeland, naglar, tone og ruheit som V4 Straum. naglar=False gjev berre lista.
    rampe=True: rundt knappen tonar ikkje mønsteret ut, det stig i ei slak rampe frå 2 mm utanfor
    knappefeltet, så kvar ribbe endar i ein spiss mot knappen."""
    kant = glatt(G.kant, 6.5, 9.5)
    list_ = kant * glatt(G.d_knapp, 11.5, 14.5)
    if rampe:
        h = H0 + mjukmin(hogd * monster ** 1.5 * kant, RAMPE * np.clip(G.d_knapp - (R_KNAPP + 4.2), 0, None))
    else:
        h = H0 + hogd * monster ** 1.5 * list_
    if naglar:
        pkt = G.utan_knapp(G.kontur_punkt(G.fast, A, 15.0), 10.0)
        h = h + G.stempel(pkt)
    tone = 0.95 + 0.045 * G.stoy(90, 7)
    rough = 0.38 * (1 - list_) + (0.44 - 0.14 * monster) * list_     # blankslitne toppar, matte dalar
    return dict(h=h, tone=tone, rough=rough, mat=dict(sky=sky, strok=strok))
