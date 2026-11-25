# -*- coding: utf-8 -*-
"""panel.py: den felles panelplanen for V1 Plate og V3 Felt.

Saumane ligg på lampa sine eigne liner, og kvar sekundærsaum endar i ein T:
  - tangentsaumar der dei flate sidene møter bogane (kvar boge er éi valsa plate)
  - ein ring i underkanten av skjermen, rundt stamma og venstre boge
  - stammekanten vidareført opp i skjermen
  - ein midtsaum på stamma, under skjermen
  - ein saum i overkanten av hakket, frå hakket til midtsaumen (ikkje under knappen)
  - ein kort gjæringssaum i det indre hjørnet, så tre plater møtest i eitt punkt
Naglane står per plate: 4,5 mm frå platekanten, med felles hjørnenagle og deling nær 10,5 mm.
"""
import numpy as np
from scipy import ndimage

from sveip_hud import (A, BUE, FLAT, H0, PKT_Z, S_, S_HAKK_F, S_KNAPP_F, S_STAMME_F, Z_HAKK, Z_SKJERM,
                       glatt, spegl)

S_MIDT = BUE + 132.25            # midt på den flate stamma (x = 115,25)
S_TANG_V = BUE + FLAT            # venstre tangentline (x = 52,5)
DELING = 10.5
BULING = 0.30                    # kor mykje plata bular mellom naglerekkjene (mm)
FUGE = 0.15                      # djupna på saumfuga


def saumar(G):
    m = G.linje_s(BUE, Z_SKJERM, S_) | G.linje_s(spegl(BUE), Z_SKJERM, S_)
    m |= G.linje_s(S_STAMME_F, Z_SKJERM, S_) | G.linje_s(spegl(S_STAMME_F), Z_SKJERM, S_)
    m |= G.linje_s(S_TANG_V, Z_HAKK, S_) | G.linje_s(spegl(S_TANG_V), Z_HAKK, S_)
    m |= G.linje_s(S_MIDT, 0.0, Z_SKJERM) | G.linje_s(spegl(S_MIDT), 0.0, Z_SKJERM)
    m |= G.linje_z(Z_SKJERM, S_STAMME_F, spegl(S_STAMME_F))
    # 8 mm forbi hakkanten, så avrundinga i hakket høyrer til fotplata
    m |= G.linje_z(Z_HAKK, S_MIDT, S_HAKK_F + 8.0) | G.linje_z(Z_HAKK, spegl(S_HAKK_F + 8.0), spegl(S_MIDT))
    t = 3.6                      # gjæring frå det teoretiske hjørnet ut til midten av avrundinga
    m |= G.linje((S_STAMME_F, Z_SKJERM), (S_STAMME_F - t, Z_SKJERM - t))
    m |= G.linje((spegl(S_STAMME_F), Z_SKJERM), (spegl(S_STAMME_F) + t, Z_SKJERM - t))
    return m & G.fast


def panel(G, tone_spreiing=0.16, fro=3):
    """Returnerer dict: h, tone, rough, d_plate (mm til næraste saum eller frie kant), ids, naglar."""
    saum = saumar(G)
    plate = G.fast & ~saum
    d_plate = G.avstand_til(plate)
    d_saum = G.avstand_til(~saum)
    ids, n = G.paneler(saum)
    # plata bular svakt mellom naglerekkjene; fuga er ei fin line med slak vegg
    bul = ndimage.gaussian_filter(glatt(d_plate, 3.0, 16.0), 2.0 / G.steg, mode=("wrap", "nearest"))
    h = H0 + BULING * bul - FUGE * glatt(d_saum, 0.60, 0.10)
    # naglar per plate, med symmetrisk opning i rekkja ved knappen
    tv = [(S_STAMME_F + A, PKT_Z - 10.9), (S_STAMME_F + A, PKT_Z + 10.9)]
    tv += [(spegl(s), z) for s, z in tv]
    pkt = G.utan_knapp(G.kontur_punkt(plate, A, DELING, tvang=tv), 9.5)
    h = h - G.stempel(pkt, 3.0, 0.05, form="grop") + G.stempel(pkt)
    nagle = G.stempel(pkt, 0.95, 1.0) > 0
    tone = G.tone_per_panel(ids, tone_spreiing, fro=fro)
    tone = tone * (1 + 0.03 * G.stoy(50, 5)) * (1 + 0.05 * G.strok(90, 0.6, 2) + 0.03 * G.strok(200, 3.0, 4))
    rough = 0.36 + 0.06 * (G.tone_per_panel(ids, 1.0, fro=fro + 5) - 1) + 0.08 * nagle
    return dict(h=h, tone=tone, rough=rough, d_plate=d_plate, ids=ids, naglar=pkt, n_panel=n)
