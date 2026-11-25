# -*- coding: utf-8 -*-
"""V2 Gore: lange vassrette banar som på skroget til eit luftskip.

Fire banar i skjermen og fem i stamma, så ein saum fell nøyaktig i underkanten av skjermen.
Kvar bane ligg omlagt over den under (overlappskøyt), med éi rekkje små naglar i omlegget.
Banane vekslar svakt mellom lysare og mørkare sølv. Éin loddrett lukkesaum i nasen.
"""
import numpy as np
from scipy import ndimage

from sveip_hud import H0, S_, Z_SKJERM, glatt

Z_SAUM = [Z_SKJERM * k / 5 for k in range(1, 6)] + [Z_SKJERM + (S_ - Z_SKJERM) * k / 4 for k in range(1, 4)]
OMLEGG = 0.42      # kor mykje nedkanten av ei bane står ut over bana under (mm)


def strok(G, lengd=140.0, breidd=2.0, fro=2):
    """Lange, vassrette strok som etter børsting langs bana."""
    rng = np.random.default_rng(fro)
    a = rng.standard_normal(G.S.shape)
    a = ndimage.gaussian_filter(a, (lengd / G.steg, breidd / G.steg), mode=("wrap", "nearest"))
    return a / np.abs(a).max()


def felt(G):
    kantar = np.array([0.0] + Z_SAUM + [S_])
    j = np.clip(np.searchsorted(kantar, G.Z, side="right") - 1, 0, len(kantar) - 2)
    z0, z1 = kantar[j], kantar[j + 1]
    t = (G.Z - z0) / (z1 - z0)                      # 0 i nedkanten av bana, 1 i overkanten
    # bana står ut i nedkanten og ligg inntil i overkanten, med mjuk avrunding heilt nedst
    h = H0 + OMLEGG * (1 - t) ** 1.6 * glatt(G.Z - z0, 0.0, 0.9)
    # éi naglerekkje i omlegget, 4 mm over nedkanten av kvar bane (ikkje i den nedste)
    n = np.zeros_like(h)
    for zk in Z_SAUM:
        n = np.maximum(n, G.naglar_z(zk + 4.0, 10.0, r=0.9, h=0.34))
    n = np.maximum(n, G.naglar_z(S_ - 4.0, 10.0, r=0.9, h=0.34))          # langs toppkanten
    # lukkesaum i nasen: fin fuge med naglar på begge sider
    dn = G.avst_s(0.0)
    h = h - 0.2 * glatt(dn, 0.5, 0.15)
    for ds in (-4.0, 4.0):
        n = np.maximum(n, G.naglar_s(ds % 719.87, 10.0, r=0.9, h=0.34, fase=5.0, z_fra=Z_SKJERM, z_til=S_))
    h = h + n
    veksel = np.where(j % 2 == 0, 1.045, 0.955)
    tone = veksel * (1 + 0.02 * G.tone_per_panel(j, 1.0, fro=4) - 0.02) * (1 + 0.035 * strok(G))
    rough = 0.43 + np.where(j % 2 == 0, -0.03, 0.03)
    return dict(h=h, tone=tone, rough=rough, mat=dict(sky=0.3))
