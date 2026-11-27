# -*- coding: utf-8 -*-
"""luftskip.py: Graf Zeppelin i éin variant, alt på ein gong.

Skjermen er skroget og stamma er gondolen som heng under.

SKROGET (skjermen, z >= Z_SK)
  Sju breie dukbanar følgjer skroget: ei brei namneband i midten (10,8 mm) med tre smalare banar
  over og under (4,1 mm). Sømmane stråler ut frå ein punkt i spissen av nasen (s = 0), så banane
  løper saman mot nasen og breier seg ut mot toppkanten; mot akterenden (venstre boge) løper dei
  saman òg, men svakare. Kvar bane ligg eitt lite steg lågare enn nabobana mot kantane
  (0,34 mm, som ei tønne), slik at tonen i lerretet blir til lys og skugge. Mellom banane ligg
  ein smal V-saum (0,9 mm brei, 0,34 mm djup). Trinnet kjem som ei rampe, ikkje som ei hylle.
  NASEKAPSELEN er ei låg kuppel med ein ring rundt; banane sluttar mot ringen.
  SPANT: to tydelege ringsaumar på tvers (djupare V-saumar), ved nasekjegla og ved akterboga.
  NAMNET «SVEIP» står opphøgt (0,45 mm, 7 mm høge bokstavar) midt på framsida, rett langs
  skroget, i namnebanda, med 1,9 mm klaring til sømma.
  FINNA: ei lang, avrunda rygg (3 mm brei, 1,2 mm høg) går opp langs den venstre boga frå foten
  av stamma og inn i skjermen, og dør ut mjukt under toppkanten.
  RINGSAUM: ei avrunda list ligg der skjermen møter stamma, rundt heile omkrinsen.

GONDOLEN (stamma, z < Z_SK)
  Eit vindaugsband av åtte små avrunda rektangel, forsenka 0,3 mm, ligg i ei rad rett over
  feltet. Tre tynne, vassrette ringar går rundt stamma under feltet. Elles er stamma glatt.
  Feltet (LED-matrisa) er vindauga i gondolen: eit 2,5 mm breitt land rundt det er glatt.

Printa opp ned: ingen skråning på ei flate som vender opp over om lag 45 grader, alle
kantar og lister går mjukt, og relieff under 0,25 mm er unngått bortsett frå saumane.
"""
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

from skal import FELT, P, S, S_VENSTRE, X_ST, Z_SK, glatt

# ---------------------------------------------------------------- mål (mm)
COLLAR_B = 0.9                          # halv breidd på ringsaumen (lista) mellom skrog og gondol
COLLAR_H = 0.50
Z_COLLAR = Z_SK + COLLAR_B              # midten av lista
Z_BAND0 = Z_SK + 2 * COLLAR_B           # banane startar over lista
ZB = (Z_BAND0 + S) / 2                  # midten av skroget i høgda (nasepunktet og namnebanda)

A0 = 5.4                                # halv breidd på namnebanda
W = (S - ZB - A0) / 3.0                 # breidd på dei andre banane langt frå nasen
L0 = 0.80                               # nivå på namnebanda
K_NIVAA = 0.085                         # mm lågare per mm banemidten ligg frå midtlinja
L_MIN = -0.20
SAUM_B, SAUM_D = 0.45, 0.34             # V-saumen: halv breidd og djup
RAMPE = 1.2                             # breidda på trinnet mellom to banar
KAMBER = 0.10

G_NASE, R_NASE, L_NASE = 0.60, 8.0, 42.0     # banane smalnar til 60 % ved ringen, parallelle frå 42 mm
G_AKTER, L_AKTER = 0.78, 34.0                # og til 78 % mot akterenden
S_AKTER = (S_VENSTRE[0] + S_VENSTRE[1]) / 2

R_KUPPEL, H_KUPPEL = 5.0, 0.80          # nasekapselen
R_RING, B_RING, H_RING = 6.8, 1.3, 0.55
R_FLAT = 7.7                            # inni her er banane tona ut til eit flatt nivå

SPANT = (28.0, 85.0)                    # s for ringsaumane på tvers (speglar bak)
SPANT_B, SPANT_D = 0.65, 0.38

FINNE_B, FINNE_H = 1.5, 1.25            # halv breidd og høgd
FINNE_LAND = 0.25

TEKST = "SVEIP"
TEKST_CAP = 7.0                         # høgd på store bokstavar
TEKST_H = 0.45
TEKST_SKRAA = 0.50                      # breidd på skråkanten (helling 0,9)
TEKST_SPORING = 0.75                    # ekstra mellomrom mellom bokstavane
TEKST_X = 38.4                          # midten på framsida

VIN_N = 8                               # vindaugsbandet
VIN_B, VIN_H, VIN_R, VIN_DJ = 3.3, 3.0, 0.9, 0.30
VIN_GAP = 0.8
VIN_Z = 44.3
VIN_SKRAA = 0.5
RINGAR_Z = (4.0, 8.2, 12.4)             # ringane rundt stamma
RING_B, RING_H = 0.55, 0.28


def kos(u):
    """Mjuk topp: 1 ved u = 0, 0 for |u| >= 1."""
    u = np.asarray(u, dtype=np.float64)
    return np.where(np.abs(u) < 1, np.cos(np.pi * u / 2) ** 2, 0.0)


def rund(s, s0=0.0):
    """Fortegna boglengd frå s0, rekna rundt."""
    return ((s - s0 + P / 2) % P) - P / 2


# ---------------------------------------------------------------- banar
def skrog_g(s):
    """Kor mykje banane er trekte saman, som funksjon av s. 1 der dei er parallelle."""
    dn = np.abs(rund(s))
    gn = G_NASE + (1.0 - G_NASE) * glatt(dn, R_NASE, L_NASE)
    dt = np.abs(rund(s, S_AKTER))
    y = 1.0 - np.minimum(dt / L_AKTER, 1.0)
    ga = 1.0 - (1.0 - G_AKTER) * y * y
    return gn * ga


def banar(H):
    """Nivå, kvelving og V-saum for banane. Gjeld i skjermen. Returnerer h og saumen åleine."""
    g1 = skrog_g(H.S[:, 0])
    gd = np.gradient(g1, H.ds)
    g, gd = g1[:, None], gd[:, None]
    nu = (H.Z - ZB) / g                           # høgda i parallelt mål (mm der banane er parallelle)
    a = np.abs(nu)
    helling = nu * gd                              # dz/ds for sømmen gjennom punktet
    cosa = 1.0 / np.sqrt(1.0 + helling ** 2)
    sp = W * g * cosa                              # banebreidda vinkelrett på sømmen

    # nivå: L0 på namnebanda, lågare utover. Sømmane ligg ved A0 + W * j.
    nivaa = np.full(H.S.shape, L0)
    ny = lambda m: max(L_MIN, L0 - K_NIVAA * (0.0 if m == 0 else A0 + W * (m - 0.5)))   # noqa: E731
    for m in range(1, 16):
        sigma = A0 + W * (m - 1)
        td = (a - sigma) * g * cosa                # mm frå sømmen, positiv utanfor
        # trinnet ligg utanfor V-saumen, der flanken til saumen alt er støtta nedover i printen
        wr = np.clip(0.4 * sp, 0.8, RAMPE)
        nivaa = nivaa + (ny(m) - ny(m - 1)) * glatt(td, 0.15, 0.15 + wr)

    # V-saum
    j = np.maximum(np.round((a - A0) / W), 0.0)
    t = np.abs(a - (A0 + W * j)) * g * cosa
    tyd = glatt(sp, 1.3, 2.3)                      # saumen bleiknar der banen er smal
    kant_opp = glatt(S - H.Z, 0.2, 1.0)            # ingen saum heilt oppe i toppkanten
    kant_ned = glatt(H.Z - (Z_BAND0 + 0.2), 0.0, 1.0)   # og ikkje inn i lista nede
    saum = SAUM_D * tyd * kant_opp * kant_ned * np.clip(1.0 - t / SAUM_B, 0.0, 1.0)

    # kvelving av banen (ikkje namnebanda): flatt mot sømmen
    f = np.clip((a - A0) / W - np.floor((a - A0) / W), 0.0, 1.0)
    kam = KAMBER * glatt(sp, 1.6, 4.0) * np.sin(np.pi * f) ** 2 * (a > A0)
    return nivaa + kam, saum


def nasekapsel(H, band):
    """Banane sluttar mot ringen. Inni ringen er det eit flatt nivå med ei låg kuppel."""
    d = np.hypot(rund(H.S), H.Z - ZB)
    m = 1.0 - glatt(d, R_FLAT - 0.2, R_FLAT + 2.4)
    flat = L0 + 0.0 * d
    kuppel = H_KUPPEL * glatt(R_KUPPEL - d, 0.0, 2.6)
    ring = H_RING * kos((d - R_RING) / B_RING)
    return m * (flat + kuppel + ring) + (1.0 - m) * band, m


def ringsaum(H):
    """Avrunda list der skjermen møter stamma, rundt heile omkrinsen."""
    return COLLAR_H * kos((H.Z - Z_COLLAR) / COLLAR_B)


def spant(H):
    """To ringsaumar på tvers av skroget: djupare V-saumar enn mellom banane (loddrette, spegla bak).
    Dei er sømmar og ikkje lister, så dei ikkje rammar inn namnet som ei stropp."""
    d = np.minimum.reduce([np.abs(rund(H.S, s0)) for s0 in SPANT] + [np.abs(rund(H.S, -s0)) for s0 in SPANT])
    til_topp = glatt(S - H.Z, 0.3, 2.0)
    fra_list = glatt(H.Z - (Z_BAND0 + 0.3), 0.0, 2.0)
    return SPANT_D * np.clip(1.0 - d / SPANT_B, 0.0, 1.0) * til_topp * fra_list * (H.Z >= Z_SK)


# ---------------------------------------------------------------- namnet
def tekst_sdf(px=25):
    """Fortegna avstand (mm, positiv inni) for teksten, på eit raster. Returnerer (sdf, x0, z_topp, px)."""
    import matplotlib
    sti = Path(matplotlib.__file__).parent / "mpl-data" / "fonts" / "ttf" / "DejaVuSans-Bold.ttf"
    str1 = ImageFont.truetype(str(sti), 200)
    e = str1.getbbox("E")
    em = 200.0 * TEKST_CAP * px / (e[3] - e[1])            # skriftstorleik som gjev rett versalhøgd
    fo = ImageFont.truetype(str(sti), int(round(em)))
    kap = fo.getbbox("E")
    kap_h = kap[3] - kap[1]
    sp = TEKST_SPORING * px
    brd = sum(fo.getlength(c) for c in TEKST) + sp * (len(TEKST) - 1)
    pad = 6 * px
    img = Image.new("L", (int(brd) + 2 * pad, kap_h + 2 * pad), 0)
    dr = ImageDraw.Draw(img)
    x = pad
    for c in TEKST:
        dr.text((x, pad - kap[1]), c, font=fo, fill=255)
        x += fo.getlength(c) + sp
    ink = np.array(img) > 127
    ys, xs = np.where(ink)
    # kutt til blekket, og sentrer
    ink = ink[ys.min() - pad // 2: ys.max() + pad // 2, xs.min() - pad // 2: xs.max() + pad // 2]
    inni = ndimage.distance_transform_edt(ink)
    ute = ndimage.distance_transform_edt(~ink)
    sdf = (inni - ute) / px                                 # positiv inni
    return sdf, ink.shape, px


def tekstfelt(H):
    """Høgd 0..TEKST_H for bokstavane, mjuk skråkant på kvar side."""
    sdf, (nr, nk), px = tekst_sdf()
    br, ho = nk / px, nr / px
    x0 = TEKST_X - br / 2
    z_topp = ZB + ho / 2
    kol = (H.X - x0) * px
    rad = (z_topp - H.Z) * px
    v = ndimage.map_coordinates(sdf, [rad, kol], order=1, mode="constant", cval=-5.0)
    v = np.where(H.flate == 1, v, -5.0)
    return TEKST_H * np.clip(v / TEKST_SKRAA, 0.0, 1.0), br


# ---------------------------------------------------------------- finna
def finne(H):
    """Lang, avrunda rygg opp langs den venstre boga. Returnerer høgda og landet ho står på."""
    ds = H.S - S_AKTER
    prof = kos(ds / FINNE_B)
    zp = FINNE_H * glatt(H.Z, 1.5, 9.0) * (1.0 - glatt(H.Z, 58.0, 77.0))
    ridge = zp * prof
    # banane og lista flatar seg ut rundt finna, så ho står på eit rolig land
    land_w = (1.0 - glatt(np.abs(ds), FINNE_B + 0.6, FINNE_B + 2.4)) * np.sqrt(np.clip(zp / FINNE_H, 0.0, 1.0))
    land_h = FINNE_LAND * glatt(H.Z, Z_SK, Z_SK + 4.0)
    return ridge, land_w, land_h


# ---------------------------------------------------------------- gondolen
def rundt_rektangel(x, z, cx, cz, hb, hh, r):
    """Fortegna avstand til avrunda rektangel (negativ inni)."""
    qx = np.abs(x - cx) - (hb - r)
    qz = np.abs(z - cz) - (hh - r)
    return np.hypot(np.maximum(qx, 0.0), np.maximum(qz, 0.0)) + np.minimum(np.maximum(qx, qz), 0.0) - r


def vindauge(H):
    """Åtte små avrunda rektangel i ei rad rett over feltet, forsenka VIN_DJ."""
    x0, _, x1, _ = FELT
    tot = VIN_N * VIN_B + (VIN_N - 1) * VIN_GAP
    start = (x0 + x1) / 2 - tot / 2 + VIN_B / 2
    sd = np.full(H.S.shape, 9.0)
    for i in range(VIN_N):
        sd = np.minimum(sd, rundt_rektangel(H.X, H.Z, start + i * (VIN_B + VIN_GAP), VIN_Z, VIN_B / 2, VIN_H / 2, VIN_R))
    return -VIN_DJ * np.clip(-sd / VIN_SKRAA, 0.0, 1.0) * H.framme * (H.flate == 1)


def ringar(H):
    """Tre tynne, vassrette ringar rundt stamma."""
    r = sum(RING_H * kos((H.Z - z0) / RING_B) for z0 in RINGAR_Z)
    return r * (H.Z < Z_SK)


# ---------------------------------------------------------------- samla
def hud(H):
    over = H.Z >= Z_SK
    band, saum = banar(H)
    band, m_kapsel = nasekapsel(H, band)
    saum = saum * (1.0 - m_kapsel)
    tekst, _ = tekstfelt(H)

    skrog = band - saum + ringsaum(H) - spant(H) * (1.0 - m_kapsel) + tekst
    stamme = vindauge(H) + ringar(H)
    h = np.where(over, skrog, stamme)

    ridge, land_w, land_h = finne(H)
    return h * (1.0 - land_w) + land_h * land_w + ridge
