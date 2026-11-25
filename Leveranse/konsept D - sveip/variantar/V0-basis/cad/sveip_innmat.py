# -*- coding: utf-8 -*-
"""Elektronikk, batteri, luke, berøringspunkt, føter, skruar og leidning."""
from __future__ import annotations

import math

import cadquery as cq

from sveip_geometri import P0, boks, syl_x, syl_y, syl_z
from sveip_kropp import BK_Y, HK_HOL, LUKE_SKRUAR, MODUL_HOL, USB_YS, chassis_senterline
from sveip_lys import jst, skrue_ned, skrue_opp

CL = chassis_senterline()
Z_TAK_U = CL[0][1] - P0.tc / 2        # 61: underside taket over hakket
Z_TAK_O = Z_TAK_U + P0.tc             # 63
Z_BOTN_U = CL[2][1] - P0.tc / 2       # 1.5
Z_BOTN_O = Z_BOTN_U + P0.tc           # 3.5
Z_TOPP_U = CL[4][1] - P0.tc / 2       # 164

# ------------------------------------------------------------ hovudkort D09
HK_X = (70.0, 168.0)
HK_Y = 30.0
AVST_HK = 25.0
Z_HK = Z_BOTN_O + AVST_HK             # 27,7 underside
T_PCB = 1.6
CELLE = (21.25, 70.8)                 # Samsung INR21700-50E, maks mål
HALDAR = (82.2, 23.1, 21.6)           # Keystone 1121 (polarisert)
CELLE_Z = Z_HK - 12.2                 # celleaksen: 1,5 mm under kortet, 2,2 mm over botnen
CELLE_XC = 120.0


def hovudkort():
    k = boks(HK_X[0], HK_X[1], -HK_Y, HK_Y, Z_HK, Z_HK + T_PCB).edges("|Z").fillet(2.0)
    for x, y in HK_HOL:
        k = k.cut(syl_z(x, y, 1.7, Z_HK - 1, Z_HK + 3))
    return k


def hk_komponentar():
    z = Z_HK + T_PCB
    blokker = [
        (90.0, -18.0, 3.0, 3.0, 1.0),    # U1 ladar (BQ24074, QFN 3x3)
        (110.0, 0.0, 3.0, 3.0, 1.0),     # U2 MCU (ATtiny1616, QFN 3x3)
        (132.0, -18.0, 3.0, 3.0, 1.0),   # U3 boost arbeid (TPS61500-klasse)
        (132.0, 18.0, 3.0, 3.0, 1.0),    # U4 boost stemning
        (146.0, -18.0, 6.0, 6.0, 3.0),   # L1
        (146.0, 18.0, 6.0, 6.0, 3.0),    # L2
        (100.0, -18.0, 6.0, 6.0, 3.0),   # inngangskondensatorar
        (120.0, -12.0, 3.2, 1.6, 1.0),   # NTC (ved cella, botnsida i praksis)
    ]
    f = None
    for x, y, lx, ly, h in blokker:
        b = boks(x - lx / 2, x + lx / 2, y - ly / 2, y + ly / 2, z, z + h)
        f = b if f is None else f.union(b)
    f = f.union(jst(78.0, 12.0, 4, z))     # J3 til USB-kortet
    f = f.union(jst(78.0, -6.0, 4, z))     # J4 til lysmodulen
    f = f.union(jst(158.0, 0.0, 3, z))     # J5 berøringskortet
    return f


def hk_avstand():
    """M3 x 25 sekskant F-F, alu, 5,5 NV; skrue M3 x 6 nedanfrå i botnen."""
    f = None
    for x, y in HK_HOL:
        s = (cq.Workplane("XY").workplane(offset=Z_BOTN_O).center(x, y)
             .polygon(6, 5.5 / math.cos(math.pi / 6)).extrude(AVST_HK)
             .cut(syl_z(x, y, 1.5, Z_BOTN_O - 1, Z_HK + 1)))
        f = s if f is None else f.union(s)
    return f


def hk_skruar():
    f = None
    for x, y in HK_HOL:   # nedanfrå gjennom botnplata
        s = skrue_opp(x, y, Z_BOTN_U, 5.0, dk=5.7, k=1.65)
        s = s.union(skrue_ned(x, y, Z_HK + T_PCB, 5.0, dk=5.5, k=1.3))
        f = s if f is None else f.union(s)
    return f


def haldar():
    lx, ly, lz = HALDAR
    x0 = CELLE_XC - lx / 2
    h = boks(x0, x0 + lx, -ly / 2, ly / 2, Z_HK - lz, Z_HK)
    # celleleiet: open nedover
    h = h.cut(syl_x(0, CELLE_Z, 10.9, x0 + 4.0, x0 + lx - 4.0))
    h = h.cut(boks(x0 + 4.0, x0 + lx - 4.0, -9.0, 9.0, Z_HK - lz - 1, CELLE_Z))
    return h


def celle():
    d, L = CELLE
    return syl_x(0, CELLE_Z, d / 2, CELLE_XC - L / 2, CELLE_XC + L / 2)


# ------------------------------------------------------------ luke D10
LUKE_X = (66.0, 172.0)
LUKE_Y = 18.0
T_LUKE = 1.5


def luke():
    z1 = Z_BOTN_U
    l = boks(LUKE_X[0], LUKE_X[1], -LUKE_Y, LUKE_Y, z1 - T_LUKE, z1).edges("|Z").fillet(3.0)
    for x, y in LUKE_SKRUAR:
        l = l.cut(syl_z(x, y, 1.7, z1 - 2, z1 + 1))
    return l


def luke_skrue():
    """To myntskruar M3 x 6, spor 1,2 mm, fanga med låseskive (ISO 1580-klasse)."""
    f = None
    for x, y in LUKE_SKRUAR:
        s = skrue_opp(x, y, Z_BOTN_U - T_LUKE, 6.0, dk=8.0, k=2.0)
        f = s if f is None else f.union(s)
    return f


# ------------------------------------------------------------ USB-kort D11
USB_KORT = (14.0, 32.0, 17.0)       # x0, x1, halv breidd
Z_USB = Z_TAK_O + 3.0               # PEM SO-M3-3


def usb_kort():
    x0, x1, hb = USB_KORT
    k = boks(x0, x1, -hb, hb, Z_USB, Z_USB + T_PCB).edges("|Z").fillet(1.5)
    for y in (-USB_YS, USB_YS):
        k = k.cut(syl_z(P0.usb_x, y, 1.7, Z_USB - 1, Z_USB + 3))
    return k


def usb_kontakt():
    """USB-C hunn, loddrett montert: munning 8,94 x 3,26, flukt med takundersida."""
    x = P0.usb_x
    s = boks(x - 1.63, x + 1.63, -4.47, 4.47, Z_TAK_U, Z_USB)
    s = s.union(boks(x - 2.0, x + 2.0, -5.0, 5.0, Z_TAK_O + 0.3, Z_USB))   # hus over taket
    return s.cut(boks(x - 1.23, x + 1.23, -4.07, 4.07, Z_TAK_U - 1, Z_USB - 1.6))


def usb_avstand():
    f = None
    for y in (-USB_YS, USB_YS):
        s = syl_z(P0.usb_x, y, 2.6, Z_TAK_O, Z_USB).cut(syl_z(P0.usb_x, y, 1.5, Z_TAK_O - 1, Z_USB + 1))
        s = s.union(syl_z(P0.usb_x, y, 2.1, Z_TAK_U, Z_TAK_O))   # pressa skaft i taket
        f = s if f is None else f.union(s)
    return f


def usb_skruar():
    f = None
    for y in (-USB_YS, USB_YS):
        s = skrue_ned(P0.usb_x, y, Z_USB + T_PCB, 3.0, dk=5.5, k=1.3)
        f = s if f is None else f.union(s)
    return f


def jst_usb():
    return jst(26.0, 0.0, 4, Z_USB + T_PCB)


# ------------------------------------------------------------ berøringspunkt D12/D13
# Eininga (messingknapp pressa i POM-hylse) blir smett inn utanfrå etter at innmaten er
# skrudd fast. Krage Ø12,8 x 0,4 på utsida er stopp innover og dekkjer lakkanten; hakane på
# hylsa held utover. Fjøra på berøringskortet ligg mot baksida av skaftet med 0,8 mm forspenning.
D_KRAGE, H_KRAGE = 12.8, 0.4
D_SKAFT = 6.0
D_HYLSE = 12.1
L_HYLSE_INN = 1.5            # hylsa stikk 1,5 mm inn forbi innerflata


def _yspenn(sy, a, b):
    return sorted((sy * a, sy * b))


def punkt(sy):
    """Messingknapp CuZn37, klarlakkert: krage Ø12,8 x 0,4 utanpå plata og skaft Ø6."""
    R, t = P0.R, P0.t
    a, b = _yspenn(sy, R, R + H_KRAGE)
    krage = syl_y(P0.pkt_x, P0.pkt_z, D_KRAGE / 2, a, b)
    c, d = _yspenn(sy, R, R - t - L_HYLSE_INN)
    skaft = syl_y(P0.pkt_x, P0.pkt_z, D_SKAFT / 2, c, d)
    return krage.union(skaft)


def bossing(sy):
    """Hylse POM: røyr Ø12,1/Ø6 frå ytterflata til 1,5 mm innanfor, fire sneppehakar Ø13 bak veggen."""
    R, t = P0.R, P0.t
    x, z = P0.pkt_x, P0.pkt_z
    a, b = _yspenn(sy, R, R - t - L_HYLSE_INN)
    roeyr = syl_y(x, z, D_HYLSE / 2, a, b).cut(syl_y(x, z, D_SKAFT / 2, a - 1, b + 1))
    c, d = _yspenn(sy, R - t, R - t - 1.2)
    hake = syl_y(x, z, 6.5, c, d).cut(syl_y(x, z, D_HYLSE / 2, c - 1, d + 1))
    for k in range(4):   # fire hakar, slissa mellom
        v = math.radians(45 + 90 * k)
        hake = hake.cut(boks(x + 7 * math.cos(v) - 2.2, x + 7 * math.cos(v) + 2.2, c - 1, d + 1,
                             z + 7 * math.sin(v) - 2.2, z + 7 * math.sin(v) + 2.2))
    return roeyr.union(hake)


# ------------------------------------------------------------ berøringskort D14
X_RYGG_V = CL[3][0] - P0.tc / 2       # venstre flate av ryggen
BK_AVST = 3.0
BK = (X_RYGG_V - BK_AVST - 1.6, X_RYGG_V - BK_AVST, 36.0, P0.pkt_z - 12.0, P0.pkt_z + 12.0)


def beroringskort():
    x0, x1, hb, z0, z1 = BK
    k = boks(x0, x1, -hb, hb, z0, z1)
    for y in BK_Y:
        k = k.cut(syl_x(y, P0.pkt_z, 1.7, x0 - 1, x1 + 1))
    return k


def bk_avstand():
    """PEM SO-M3-3 pressa i ryggen; M3 x 5 held kortet."""
    x0, x1, hb, z0, z1 = BK
    f = None
    for y in BK_Y:
        s_ = syl_x(y, P0.pkt_z, 2.6, x1, X_RYGG_V).cut(syl_x(y, P0.pkt_z, 1.5, x1 - 1, X_RYGG_V + 1))
        s_ = s_.union(syl_x(y, P0.pkt_z, 2.1, X_RYGG_V, X_RYGG_V + P0.tc))
        s_ = s_.union(syl_x(y, P0.pkt_z, 2.75, x0 - 1.3, x0).union(syl_x(y, P0.pkt_z, 1.35, x0, x1)))
        f = s_ if f is None else f.union(s_)
    return f


def fjorkontakt():
    """Fjørkontakt (CuSn6, forgylt, 0,3 mm), lodda på berøringskortet: arm langs x til
    punktaksen, så ei tunge med pute Ø4 mot baksida av messingskaftet. Teikna i arbeidsstilling;
    i fri stilling står puta 0,8 mm lenger ut (forspenning), og ho når ikkje kroppen."""
    x0 = BK[0]
    xp, zp = P0.pkt_x, P0.pkt_z
    f = None
    for sy in (-1, 1):
        y_ende = sy * (P0.R - P0.t - L_HYLSE_INN)    # baksida av messingskaftet
        y_arm = sy * 38.0
        arm = boks(xp - 1.0, x0, min(y_arm, y_arm + sy * 0.3), max(y_arm, y_arm + sy * 0.3),
                   zp - 2.0, zp + 2.0)
        a, b = sorted((y_arm, y_ende - sy * 0.3))
        tunge = boks(xp - 1.0, xp - 0.7, a, b, zp - 2.0, zp + 2.0)
        c, d = sorted((y_ende, y_ende - sy * 0.3))
        pute = syl_y(xp, zp, 2.0, c, d)
        s_ = arm.union(tunge).union(pute)
        f = s_ if f is None else f.union(s_)
    return f


# ------------------------------------------------------------ føter, skruar, PEM
def foter():
    """TPE-fot Ø12 x 3 med lomme som sneppar over knappehovudet på kroppsskruen."""
    f = None
    for sy in (-1, 1):
        for x in P0.fot_x:
            y = sy * P0.fl_yc
            s_ = syl_z(x, y, 6.0, -P0.fot_h, 0.0).cut(syl_z(x, y, 2.9, -1.75, 0.1))
            f = s_ if f is None else f.union(s_)
    return f


def kropp_skruar():
    """ISO 7380 M3 x 6 nedanfrå gjennom sporet i flensen, i PEM-mutter i chassisbotnen."""
    f = None
    for sy in (-1, 1):
        for x in P0.fot_x:
            s_ = skrue_opp(x, sy * P0.fl_yc, 0.0, 6.0)
            f = s_ if f is None else f.union(s_)
    return f


def pem_mutrar():
    """CLS-M3-2: hovud Ø6,35 x 1,5 på den sida som vender bort frå skruen."""
    f = []
    for sy in (-1, 1):
        for x in P0.fot_x:
            f.append(syl_z(x, sy * P0.fl_yc, 3.17, Z_BOTN_O, Z_BOTN_O + 1.5)
                     .cut(syl_z(x, sy * P0.fl_yc, 1.5, Z_BOTN_O - 1, Z_BOTN_O + 3)))
    for x, y in LUKE_SKRUAR:
        f.append(syl_z(x, y, 3.17, Z_BOTN_O, Z_BOTN_O + 1.5)
                 .cut(syl_z(x, y, 1.5, Z_BOTN_O - 1, Z_BOTN_O + 3)))
    for x, y in MODUL_HOL:
        f.append(syl_z(x, y, 3.17, Z_TOPP_U - 1.5, Z_TOPP_U)
                 .cut(syl_z(x, y, 1.5, Z_TOPP_U - 3, Z_TOPP_U + 1)))
    u = f[0]
    for s in f[1:]:
        u = u.union(s)
    return u


# ------------------------------------------------------------ leidning (følgjer med)
def plugg_og_leidning():
    x = P0.usb_x
    plugg = boks(x - 3.2, x + 3.2, -6.15, 6.15, Z_TAK_U - 15.0, Z_TAK_U - 0.3)
    plugg = plugg.edges("|Z").fillet(1.5)
    tapp = boks(x - 1.1, x + 1.1, -3.9, 3.9, Z_TAK_U - 0.3, Z_TAK_U + 2.6)
    zb = -P0.fot_h + 1.9
    bane = (cq.Workplane("XZ").moveTo(x, Z_TAK_U - 15.0)
            .spline([(x - 2.0, 18.0), (x - 14.0, 4.0), (x - 40.0, zb + 0.4), (x - 110.0, zb)],
                    tangents=[(0, -1), (-1, 0)], includeCurrent=True))
    snitt = cq.Workplane("XY").workplane(offset=Z_TAK_U - 15.0).center(x, 0).circle(1.9)
    leidning = snitt.sweep(bane)
    return plugg.union(tapp).union(leidning)
