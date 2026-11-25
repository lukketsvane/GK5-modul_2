# -*- coding: utf-8 -*-
"""V3 Felt: dei same nagla platene som V1, med ei mikrooverflate styrt av eit felt.

Feltet er avstanden til messingknappen. Eit sekskantnett av pressa gropar er registrert på
knappen: knappen står i ein node, og tangentlinene og underkanten av skjermen fell på heile
delingar. Gropene er størst ved knappen (Ø 5,2) og minkar lineært til Ø 2,6 der feltet
sluttar, 97,5 mm unna, i underkanten av skjermen. Berre heile gropar: ei grop som ikkje får
plass innanfor margen til saum og kant, er utelaten.
"""
import math

import numpy as np

from panel import panel
from sveip_hud import A, H0, NAGLE_R, P_, PKT_Z, S_KNAPP_B, S_KNAPP_F, Z_SKJERM

PS = P_ / 96                       # 7,4986 mm: knappen står i node 22 framme og 74 bak
QZ = PS * math.sqrt(3)
Z0 = PKT_Z - 5 * QZ                # ei rad går gjennom knappen
NIVAA = 0.73                       # nullnivået er løfta, så gropene kan gå 0,55 mm ned
R_MIN, R_MAKS, DJUPN = 1.3, 2.6, 0.55
REKKJEVIDD = (8.0, Z_SKJERM - PKT_Z)
MARG = A + NAGLE_R + 1.7           # frå gropkant til saum eller kant: 7,1 mm


def avst_knapp(s, z):
    d = lambda s0: np.abs(((s - s0 + P_ / 2) % P_) - P_ / 2)
    return np.minimum(np.hypot(d(S_KNAPP_F), z - PKT_Z), np.hypot(d(S_KNAPP_B), z - PKT_Z))


def felt(G):
    p = panel(G)
    h = p["h"] + (NIVAA - H0)
    grop = np.zeros_like(h)
    for fs, fz in ((0.0, 0.0), (0.5, 0.5)):   # to rektangelnett som saman er eit sekskantnett
        cs = (np.floor(G.S / PS - fs + 0.5) + fs) * PS
        cz = (np.floor((G.Z - Z0) / QZ - fz + 0.5) + fz) * QZ + Z0
        dk = avst_knapp(cs, cz)
        f = 1 - np.clip((dk - REKKJEVIDD[0]) / (REKKJEVIDD[1] - REKKJEVIDD[0]), 0, 1)
        r = R_MIN + (R_MAKS - R_MIN) * f
        djup = DJUPN * f ** 0.8
        heil = (djup >= 0.05) & (dk >= 12.0) & (G.sla_opp(p["d_plate"], cs, cz) >= MARG + r)
        d = np.hypot(G.S - cs, G.Z - cz)
        g = djup * np.clip(1 - (d / r) ** 2, 0, 1) ** 1.5       # mjuk rand, som ein pressradius
        grop = np.maximum(grop, np.where(heil, g, 0.0))
    tone = p["tone"] * (1 + 0.04 * grop / DJUPN)                # botnen er blankpressa
    rough = p["rough"] - 0.10 * grop / DJUPN
    return dict(h=h - grop, tone=tone, rough=rough, knapp_nivaa=NIVAA, mat=dict(sky=0.2, strok=0.5))
