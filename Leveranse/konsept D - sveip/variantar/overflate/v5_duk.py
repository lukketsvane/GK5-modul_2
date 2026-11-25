# -*- coding: utf-8 -*-
"""V5 Duk: ytterhuda til eit luftskip. Dopa lerret stramma over skjulte loddrette ribber.

18 ribber rundt forma (40 mm). Duken søkk svakt inn mellom ribbene og ligg flatt mot ramma
langs alle kantar. Over kvar ribbe og langs ringen i underkanten av skjermen ligg ei dopa
dekkremse på 9 mm med taggete kantar, som over snøringa på luftskipa. Ingen naglar.
"""
import numpy as np

from sveip_hud import H0, P_, Z_SKJERM, glatt

N_RIBBER = 18
SIG = 0.95         # kor djupt duken søkk midt mellom to ribber (mm)
TOPP = 1.25        # nivået over ribbene
REMSE_B, REMSE_H = 9.0, 0.11


def felt(G):
    felt_b = P_ / N_RIBBER
    u = (G.S % felt_b) / felt_b                         # 0..1 over eit felt, ribbe i 0 og 1
    d_ribbe = np.minimum(u, 1 - u) * felt_b             # avstand til næraste ribbe (mm)
    stramt = glatt(G.kant, 1.0, 34.0)                   # duken ligg flatt mot ramma langs kantane
    ring = glatt(np.abs(G.Z - Z_SKJERM), 0.0, 30.0)     # og mot ringen i underkanten av skjermen
    h = TOPP - SIG * np.sin(np.pi * u) ** 1.3 * stramt * ring
    # dekkremser med taggete kant (tagg 1,2 mm brei, 0,8 mm djup)
    def remse(d, langs):
        tagg = 0.8 * np.abs(((langs / 1.2) % 2.0) - 1.0)
        return REMSE_H * glatt(d, REMSE_B / 2 + tagg - 0.4, REMSE_B / 2 + tagg - 0.9)
    h = h + np.maximum(remse(d_ribbe, G.Z), remse(np.abs(G.Z - Z_SKJERM), G.S))
    felt_nr = (G.S // felt_b).astype(int)
    tone = (1 + 0.035 * np.where(felt_nr % 2 == 0, 1, -1) * stramt) * (1 + 0.04 * G.stoy(55, 11))
    return dict(h=h, tone=tone,
                mat=dict(farge=(0.80, 0.80, 0.80), metal=0.92, rough=0.5, sky=0.9, vev=1.0, floyel=0.1))
