# -*- coding: utf-8 -*-
"""V12 Mini: Sveip i 36 % storleik, bygd rundt ein micro:bit V2 i stamma.

Lampa er 108 x 108 x 37,8 mm. Kortet står rotert 90° bak framveggen: det er 51,6 mm høgt i ei
stamme som er 60,3 mm høg, med 4,35 mm over og under, og USB-en peikar ut mot den opne enden
av stamma. Matrisa på 5 x 5 står midt på stamma, både i breidda og i høgda, og er det største
elementet på framsida. Til høgre for henne, der kortet har touch-logoen sin, står eit
messingpunkt (Ø 6). Dei to deler eitt forsenka felt på 32 x 23 mm, på same line som i rev. B,
og heile feltet ligg på den flate framveggen. Hakket for pluggen i nasen er borte. Skjermen
har banane frå V10 Baug. Stamma er glatt, så feltet er det einaste på henne.
"""
import numpy as np

import sveip_hud as H

K = 0.36                      # 108 / 300
MB = (89.0 * K, 83.75 * K)    # midtre LED på mini-lampa (mm): midt på stamma, (32,04; 30,15)
LOGO = 14.0                   # touch-logoen ligg 14,0 mm frå midtre LED
H.oppsett(skala=K, mikrobit=MB, knapp=(MB[0] + LOGO, MB[1], 3.0), knapp_bak=False, hakk=False,
          utan=("E01",), felt_ut=(9.0, 0.0))

from luftskip import ferdig   # etter oppsett(), så modulane les dei nye måla
from v10_baug import baug


def felt(G):
    sag, line, nr, dz, _ = baug(G)
    stamme = G.Z < H.Z_SKJERM                                  # glatt stamme: berre ringsaumen står att
    sag = np.where(stamme, 0.0, sag)
    line = np.where(stamme, np.exp(-(dz / 0.45) ** 2), line)
    nr = np.where(stamme, 1000, nr)
    return ferdig(G, sag, line, nr, mikrobit=True)
