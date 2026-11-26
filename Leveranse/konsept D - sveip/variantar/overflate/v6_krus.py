# -*- coding: utf-8 -*-
"""V6 Krus: ringar som breier seg ut frå messingknappen, som krusningar i vatn.

Feltet er avstanden til knappen i den utbretta plata. Ringane er tette ved knappen (2,0 mm)
og glir ut til 6,0 mm. Ringane frå knappen framme og bak møtest i to liner: i nasen og i
toppunktet på venstre boge. Mønsteret er pressa i den flate plata før ho blir valsa, så ringane
held fram i skjermen over utkraginga. Same kant og knappeland som V4.
"""
import numpy as np

from straum import avslutt, fase

P0, P1 = 2.0, 6.0
REKKJEVIDD = 260.0
START = 14.5               # første ring like utanfor landet rundt knappen


def felt(G):
    d = np.clip(G.d_knapp - START, 0, None)
    bolgje = 0.5 + 0.5 * np.cos(2 * np.pi * fase(d, P0, P1, REKKJEVIDD))
    return avslutt(G, bolgje)
