# -*- coding: utf-8 -*-
"""V2 Gore: lange vassrette banar som på skroget til eit luftskip.

Fire banar i stamma og tre i skjermen. Ein saum fell nøyaktig i underkanten av skjermen, og
ingen saum ligg nærare knappen eller hakket enn 12 mm. Kvar bane ligg omlagt over den under,
med éi rekkje små naglar i omlegget. Tonen går i jamne steg, lysast øvst.
"""
import numpy as np

from sveip_hud import A, H0, P_, S_, Z_SKJERM, glatt

Z_SAUM = [Z_SKJERM * k / 4 for k in range(1, 5)] + [Z_SKJERM + (S_ - Z_SKJERM) * k / 3 for k in range(1, 3)]
OMLEGG = 0.42          # kor mykje nedkanten av ei bane står ut over bana under (mm)
DELING = P_ / 60       # 12,0 mm: går opp rundt omkrinsen
NAGLE_H = 0.24


def felt(G):
    kantar = np.array([0.0] + Z_SAUM + [S_])
    j = np.clip(np.searchsorted(kantar, G.Z, side="right") - 1, 0, len(kantar) - 2)
    z0, z1 = kantar[j], kantar[j + 1]
    t = (G.Z - z0) / (z1 - z0)                      # 0 i nedkanten av bana, 1 i overkanten
    h = H0 + OMLEGG * (1 - t) ** 1.6 * glatt(G.Z - z0, 0.0, 0.9)
    n = np.zeros_like(h)
    for zk in Z_SAUM:                               # éi naglerekkje i omlegget, 4 mm over saumen
        n = np.maximum(n, G.naglar_z(zk + 4.0, DELING, h=NAGLE_H))
    n = np.maximum(n, G.naglar_z(S_ - A, DELING, h=NAGLE_H))        # langs toppkanten
    # lukkesaum i nasen: ei fin fuge midt mellom to naglar
    h = h - 0.2 * glatt(G.avst_s(DELING / 2), 0.5, 0.15) * (G.Z > Z_SKJERM)
    fint, grovt = G.strok(90, 0.5, 2), G.strok(220, 3.0, 3)
    tone = (0.94 + 0.01 * j) * (1 + 0.07 * fint + 0.04 * grovt)
    rough = 0.46 + np.where(j % 2 == 0, -0.03, 0.03) + 0.05 * fint
    return dict(h=h + n, tone=tone, rough=rough, mat=dict(sky=0.15, strok=0.4))
