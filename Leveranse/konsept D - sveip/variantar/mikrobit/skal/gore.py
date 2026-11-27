# -*- coding: utf-8 -*-
"""gore.py: Graf Zeppelin slik han ser ut på fotoa, utan noko ekstra.

Skjermen er skroget. Ni breie dukbanar (gores) følgjer omkrinsen, og sømma strålar ut frå eitt
punkt i spissen av nasen (s = 0, midt i høgda på skjermen). Langt frå nasen er banane vassrette
og parallelle, 4,12 mm breie, slik at ni banar fyller skjermen frå botnen til toppkanten. Frå
x = 28 mm og framover smalnar banane jamt (ned til 42 %) og endar mot ringen på nasekapselen.
Venstre boge er akterenden: banane smalnar òg der, men berre til 55 %.

Kvar bane er eit stramt, svakt kvelva felt (flatt inn mot sømmen, så saumflanken ikkje blir brattare). Mellom banane ligg ein smal V-saum (0,8 mm brei,
0,3 mm djup), og banane ligg i trinn av 0,25 mm som ei tønne: midtbana høgast, ytterbanane lågast,
slik at tonen i lerretet blir til lys og skugge. Trinnet kjem som ei rampe over saumen, så ingen
skarpe hyller vender opp i printen. Der banane blir smalare enn om lag 2,3 mm, bleikner saumen,
så nasen ikkje blir myldrande.

Nasekapselen: ein låg kuppel med ein ring rundt. Banane sluttar mot ringen.
Ringsaum der skjermen møter stamma: ei avrunda list i botnkanten av skjermen med ein V-saum under.
Stamma er gondolen: 18 felt med fine loddrette saumar (konstant i z, så dei blir skarpe i printen).
Saumane stoppar mjukt før feltet, som har ei smal ramme, ein vindaugsram, rundt seg.
"""
import numpy as np
from scipy import ndimage

from skal import BUE, P, R, S, S_VENSTRE, X_ST, Z_SK, glatt, i_felt

# ---------------------------------------------------------------- mål (mm)
ZC = (Z_SK + S) / 2                      # midten av skjermen i høgda, 65,45
NB = 9                                   # banar frå botn til topp i skjermen
W0 = (S - Z_SK) / NB                     # banebreidda langt frå nasen, 4,12
L_NASE = 58.0                            # banane er parallelle frå her og bakover
G_NASE = 0.42                            # relativ banebreidd ved kapselringen
L_AKTER = 36.0
G_AKTER = 0.55                           # akterenden smalnar berre til 55 %
S_AKTER = (S_VENSTRE[0] + S_VENSTRE[1]) / 2

L0 = 0.85                                # nivå på midtbana
STEG = 0.25                              # trinn mellom banane
KAMBER = 0.12                            # kvelving av ei bane på tvers
SAUM_B, SAUM_D = 0.4, 0.30               # V-saumen: halv breidd og djup
RAMPE = 1.0                              # trinnet kjem som ei rampe over saumen

R_RING = 8.0                             # nasekapselen
RING_H = 0.55

N_FELT = 18                              # felt rundt stamma
STAM_B, STAM_D = 0.35, 0.25
STAM_KAMBER = 0.08

RAMME_D, RAMME_B, RAMME_H = 2.2, 0.65, 0.5   # vindaugsramma: avstand frå feltkanten, halv breidd og høgd


def kos(u):
    """Mjuk topp: 1 ved u = 0, 0 for |u| >= 1."""
    return np.where(np.abs(u) < 1, np.cos(np.pi * u / 2) ** 2, 0.0)


def sid(H, s0):
    """Fortegna boglengd frå s0, rekna rundt."""
    return ((H.S - s0 + P / 2) % P) - P / 2


def avst_felt(H):
    """mm langs huda frå kanten av feltet. H.d_felt tel òg topp- og botnkanten som felt, så ei eiga
    utrekning her: der får z-kantane tilsvarande fyll (True) og ikkje nokon avstand."""
    felt = i_felt(H.X, H.Z) & H.framme
    pad = H.ns // 2
    m = np.concatenate([~felt[-pad:], ~felt, ~felt[:pad]], axis=0)
    m = np.pad(m, ((0, 0), (1, 1)), mode="edge")
    d = ndimage.distance_transform_edt(m, sampling=(H.ds, H.dz))
    return np.maximum(d[pad:-pad, 1:-1] - 0.5 * H.steg, 0.0)


def skrog_g(s):
    """Kor mykje banane er trekte saman (0 i nasen, 1 der dei er parallelle). Berre ein funksjon av s."""
    dn = np.abs(((s + P / 2) % P) - P / 2)
    x = np.clip((dn - R_RING) / (L_NASE - R_RING), 0.0, 1.0)
    gn = G_NASE + (1.0 - G_NASE) * x * x * (3.0 - 2.0 * x)         # jamn utvikling frå ringen og bakover
    gn = gn * np.minimum(1.0, np.sqrt(dn / R_RING))                # mot spissen under kapselen
    dt = np.abs(((s - S_AKTER + P / 2) % P) - P / 2)
    y = 1.0 - np.minimum(dt / L_AKTER, 1.0)
    gt = 1.0 - (1.0 - G_AKTER) * y * y                            # svakare mot akterenden
    return gn * gt


def banar(H):
    """Banane i skjermen: nivå, kvelving og V-saum. Gjeld for z >= Z_SK."""
    s1 = H.S[:, 0]
    g1 = skrog_g(s1)
    gd = np.gradient(g1, H.ds)
    g = np.maximum(g1, 0.04)[:, None]
    gd = gd[:, None]
    dz = H.Z - ZC
    nu = dz / (g * W0)                                            # banenummer med brøk, 0 midt i midtbana
    tall = nu + 0.5
    n = np.floor(tall)
    f = tall - n
    sp = g * W0 / np.sqrt(1.0 + (dz * gd / g) ** 2)               # mm mellom to sømmar, vinkelrett
    tl, tu = f * sp, (1.0 - f) * sp
    tyd = glatt(sp, 1.3, 2.3)                                     # saum og trinn bleiknar der banen er smal
    # nivået følgjer banens midtpunkt (n * g * W0) frå midtlinja, så trinnet blir mindre saman med
    # banen mot nasen, og toppkanten ligg lågt òg der banane er trekte saman
    lev = lambda k: np.maximum(L0 - STEG * g * np.abs(k), -0.2)   # noqa: E731
    tr = np.clip(0.3 * sp, 0.5, RAMPE)
    nivaa = lev(n - 1) + (lev(n) - lev(n - 1)) * glatt(tl, SAUM_B, SAUM_B + tr)
    kam = KAMBER * glatt(sp, 1.6, 4.0) * np.sin(np.pi * f) ** 2
    kant = glatt(H.Z - Z_SK, 0.25, 1.1) * glatt(S - H.Z, 0.25, 1.1)   # ingen saum i botn- og toppkanten
    t = np.minimum(tl, tu)
    saum = SAUM_D * tyd * kant * np.clip(1.0 - t / SAUM_B, 0.0, 1.0) ** 1.2
    return nivaa + kam - saum, sp


def kapsel(H, band):
    """Nasekapselen: låg kuppel og ein ring. Banane sluttar mot ringen."""
    d = np.hypot(sid(H, 0.0), H.Z - ZC)
    m = 1.0 - glatt(d, R_RING - 0.5, R_RING + 0.1)
    kuppel = 0.75 + 0.30 * np.clip(1.0 - (d / R_RING) ** 2, 0.0, 1.0)
    ring = RING_H * kos((d - R_RING) / 0.6)
    return m * kuppel + (1.0 - m) * band + ring


def stamme(H, d_felt):
    """Gondolen: 18 felt med fine loddrette saumar rundt stamma. Konstant i z."""
    s0 = H.s_av_x(X_ST)                                           # fremre hjørne av stamma
    s1 = H.s_av_x(X_ST, framme=False)                             # bakre hjørne
    pb = (s1 - s0) / N_FELT
    q = (H.S - s0) / pb
    k = np.round(q)
    f = q - np.floor(q)
    t = np.abs(q - k) * pb
    inne = (k >= 1) & (k <= N_FELT - 1)
    fade = (glatt(H.Z, 1.5, 3.5) * glatt(Z_SK - H.Z, 1.4, 3.0) * glatt(d_felt, 3.0, 3.9))
    saum = STAM_D * np.clip(1.0 - t / STAM_B, 0.0, 1.0) ** 1.2 * inne
    kam = STAM_KAMBER * 4.0 * f * (1.0 - f) * ((q >= 0) & (q <= N_FELT))
    return (kam - saum) * fade


def ringsaum(H):
    """Ei avrunda list i botnkanten av skjermen og ein V-saum under, der skjermen møter stamma."""
    list_ = 0.55 * kos((H.Z - (Z_SK + 1.0)) / 1.0)
    saum = 0.28 * np.clip(1.0 - np.abs(H.Z - (Z_SK - 0.35)) / 0.45, 0.0, 1.0) ** 1.2
    return list_ - saum


def vindaugsramme(H, d_felt):
    """Smal list rundt feltet (LED-matrisa er vindauga i gondolen)."""
    return RAMME_H * kos((d_felt - RAMME_D) / RAMME_B) * H.framme


def hud(H):
    d_felt = avst_felt(H)
    over = H.Z >= Z_SK
    band, sp = banar(H)
    band = kapsel(H, band)
    h_sk = band + ringsaum(H) * (H.Z >= Z_SK)
    h_st = stamme(H, d_felt) + ringsaum(H) * (H.Z < Z_SK)
    h = np.where(over, h_sk, h_st) + vindaugsramme(H, d_felt)
    return h
