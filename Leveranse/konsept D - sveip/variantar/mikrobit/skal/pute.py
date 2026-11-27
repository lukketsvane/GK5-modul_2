# -*- coding: utf-8 -*-
"""pute.py: skalvariant «pute». Lerret stramma mellom spant og dragarar, som innsida av nasen på
eit luftskip.

Skjermen er skroget. Dragarane (0,9 mm breie ribber, +0,5 mm) løper langs skroget og trekkjer seg
saman mot nasen, der dei møtest i ei nasekapsel (ring og kuppel). Spanta er ringar på tvers med
jamn deling langs skroget. Mellom dragarane og spanta ligg lerretet som ei pute: botnen er −0,4 mm
og ho stig mjukt opp mot ribbene. Rutene blir difor lengre og smalare mot nasen, og putene grunnare.

Stamma er gondolen. Dragarane står loddrett og det er to spant vassrett. Feltet med LED-hola er
vindauga i gondolen: der ligg ei ramme (eit land som stig mjukt ut frå feltet), og putene stoppar
mot ho. Heile lampa har ei kantlist på 0,9 mm langs alle frie kantar (toppkanten, botnen, brua
under skjermen og sida av stamma), og saumen mellom stamme og skjerm er ein ring som går rundt
heile lampa i same høgd som kantlista under skjermen.

Korleis putene blir laga: alle ribber (dragarar, spant, kantlist, saum, ring, ramme) blir lagde i
éi maske, og avstanden frå masken gjev høgda. Det gjev ei pute med jamn skråning på alle sider,
òg i smale rutor og i hjørne, utan at kvar ribbetype treng sin eigen formel. Skråninga er under
40 grader, så ingen flater overheng meir enn print toler.
"""
import numpy as np
from scipy import ndimage

import skal as SK
from skal import BUE, P, R, S, X_ST, Z_SK, glatt

# ---- mål (mm i lampa)
BREIDD = 0.9                 # ribbene
RIBBE = 0.45                 # halv breidd
H_RIBBE = 0.6                # høgd på ribbene
DJUP = 1.0                   # frå ribbetopp ned til puteflata, så botnen blir −0,4
RAMPE = 3.2                  # så langt frå ribba botnen er nådd; smale rutor blir grunnare (skråning under 30 grader)
ZC = (Z_SK + S) / 2          # midten av skjermen, 65,45
Z_TOPP = S - RIBBE           # midten av kantlista øvst, 83,55
Z_SAUM = Z_SK + RIBBE        # midten av saumen mellom stamme og skjerm, 47,35
HALV = Z_TOPP - ZC           # 18,1
N_BANAR = 5                  # banar i full breidd
PITCH = 2 * HALV / N_BANAR   # 7,24: breidda på ei bane langt frå nasen
K_MAKS = 2.5                 # høgste dragar (halvt tal) frå aksen; dei ytste kjem inn frå kantlista
R_RING = 8.0                 # nasekapselen
L_NASE = 16.0                 # kor fort banane trekkjer seg saman (rasjonal kurve)
D_NASE_FULL = 90.0           # banane er i full breidd frå her
G_AKTER = 0.78               # banebreidda i akterenden, i høve til full


def sm(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def bane_skala(d):
    """Banebreidda i høve til full breidd, d mm frå nasen langs huda. 0 i nasen, 1 frå D_NASE_FULL."""
    g = d / (d + L_NASE) * (1 + L_NASE / D_NASE_FULL)
    return np.minimum(g, 1.0)


def hud(H):
    ds = ((H.S + P / 2) % P) - P / 2                 # boglengd frå nasen, med forteikn (framsida +)
    d = np.abs(ds)
    e = P / 2 - d                                    # frå akterenden (venstre tupp)
    skjerm = H.Z >= Z_SAUM
    r = np.hypot(ds, H.Z - ZC)

    # ---- banar i skjermen: dragarane er linjer med konstant (z − ZC) / (PITCH · G)
    g = np.maximum(bane_skala(d) * (G_AKTER + (1 - G_AKTER) * glatt(e, 0.0, 40.0)), 0.03)
    u = (H.Z - ZC) / (PITCH * g) - 0.5               # heile tal er dragarane
    du_dz = np.gradient(u, H.dz, axis=1)
    du_ds = (np.roll(u, -1, axis=0) - np.roll(u, 1, axis=0)) / (2 * H.ds)
    avst_bane = np.abs(u - np.round(u)) / np.maximum(np.hypot(du_dz, du_ds), 1e-6)
    k = np.round(u)
    bane = (avst_bane < RIBBE) & (k >= -K_MAKS - 0.5) & (k <= K_MAKS - 0.5) & skjerm & (r > R_RING)

    # ---- stamma: loddrette dragarar kvar PV frå midten av akterenden, kantlista er den ytste
    s_kant = BUE + (S - R - X_ST)                    # kanten av stamma (sida), framsida
    q = np.abs(H.S - P / 2)
    pv = (P / 2 - (s_kant + RIBBE)) / 4.5            # 12,84

    # ---- spant i skjermen: kvart andre loddrette dragar i stamma held fram oppover, og eitt til mot nasen
    d_spant = [P / 2 - pv * j for j in (0.5, 2.5, 4.5, 6.5)]
    spant = np.zeros(H.S.shape, dtype=bool)
    for d0 in d_spant:
        spant |= np.abs(d - d0) < RIBBE
    spant &= skjerm

    # ---- nasekapselen: ring (kuppelen kjem som tillegg til slutt)
    ring = np.abs(r - R_RING) < RIBBE

    # ---- stamma: loddrette dragarar og to vassrette spant
    avst_v = np.abs((q % pv) - pv / 2)
    loddrett = (avst_v < RIBBE) & (q <= 4.5 * pv + RIBBE) & ~skjerm
    z_sp = Z_SAUM - (Z_SAUM - RIBBE) * np.array([1 / 3, 2 / 3])
    vassrett = np.zeros(H.S.shape, dtype=bool)
    for z in z_sp:
        vassrett |= np.abs(H.Z - z) < RIBBE
    vassrett &= ~skjerm

    saum = np.abs(H.Z - Z_SAUM) < RIBBE
    kantlist = H.kant < BREIDD
    ramme = H.d_felt < 3.0                           # landet rundt feltet, stig mjukt ut frå feltet (tona i skal.py)

    ribber = bane | spant | ring | loddrett | vassrett | saum | kantlist | ramme | ~H.fast

    # lukk dei smale glippene (under 1,2 mm) mellom ribber, så det ikkje blir flisar
    px = max(1, int(round(0.6 / H.steg)))
    yy, xx = np.mgrid[-px:px + 1, -px:px + 1]
    skive = (yy ** 2 + xx ** 2) <= px ** 2 + 0.5
    pad = px + 2
    m = np.pad(ribber, ((pad, pad), (0, 0)), mode="wrap")
    m = np.pad(m, ((0, 0), (pad, pad)), mode="constant", constant_values=True)
    m = ndimage.binary_closing(m, structure=skive)
    ribber = m[pad:-pad, pad:-pad] | ribber

    # ---- puteflata: avstand frå næraste ribbe gjev høgda
    D = H.avstand_til(~ribber)
    h = H_RIBBE - DJUP * sm(D / RAMPE)

    # ---- kuppelen i nasekapselen
    ri = R_RING - RIBBE
    kuppel = 2.0 * np.clip(1 - (r / ri) ** 2, 0.0, None) ** 1.5
    h = h + kuppel
    return h
