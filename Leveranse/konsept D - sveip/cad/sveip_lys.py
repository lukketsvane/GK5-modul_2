# -*- coding: utf-8 -*-
"""Lysmodulen (D03-D08): lysbrett, to LED-kort, ramme og to diffusorar.

Modulen blir senka ned gjennom den opne toppen og skrudd med fire M3 x 25
gjennom avstandsrøyr til toppflensen på chassiset. Éin 4-pols plugg (J1).
"""
from __future__ import annotations

import math

import cadquery as cq

from sveip_geometri import P0, boks, stadion, syl_z
from sveip_kropp import MODUL_HOL, chassis_senterline

# ------------------------------------------------------------ høgder (z)
TB = P0.tb
Z_BRETT = P0.brett_z                 # 186: underside lysbrett
Z_BRETT_O = Z_BRETT + TB             # 188
T_PCB = 1.6                          # nedkort MCPCB
T_OPP = 1.0                          # oppkort FR-4 1,0 mm
Z_OPP_KORT = Z_BRETT_O               # 187.5..188.5
Z_NED_KORT = Z_BRETT - T_PCB         # 184.4..186
LED = (3.0, 3.0, 0.65)               # 3030-hus
SPACER_H = 16.0
Z_DIFF_OPP = Z_BRETT_O + SPACER_H    # 204..206
T_DIFF = 2.0                         # nedre diffusor
T_DIFF_OPP = 1.5                     # øvre diffusor
PEM_H = (3.175, 1.1)                 # CLS-M3-1: hovud Ø6,35 x 1,1
Z_RAMME0 = 168.5                     # ramma sin underkant (1 mm over skjermkanten)
Z_DIFF_NED = Z_RAMME0 + 1.0          # 169.5..171.5

# ------------------------------------------------------------ posisjonar
XC = P0.S - P0.R                     # senter i høgre boge (247.5)
R_RAMME_Y = P0.R - P0.t - 0.5        # 50.5: ytterkant ramme
T_RAMME = 1.2
X_RAMME = 176.5                      # venstre vegg (lysvegg)
R_NED = 38.0                         # nedkortet: D-form
X_NED0 = 184.0
OPP_KORT = (30.0, 270.0, 18.0)       # x0, x1, halv breidd
OPP_LED = [(45.0 + 30 * k, sy * 8.0) for k in range(8) for sy in (-1, 1)]
NED_LED = [(190.0 + 16 * i, -24.0 + 16 * j) for i in range(6) for j in range(4)]
OPP_SKRUAR = [(33.0, -14.0), (33.0, 14.0), (125.0, -14.0), (125.0, 14.0),
              (220.0, -14.0), (220.0, 14.0)]
RAMME_SKRUAR = [(181.0, -44.0), (181.0, 44.0), (276.0, -34.0), (276.0, 34.0)]
LAAS_AVST = [(60.0, -42.0), (60.0, 42.0), (140.0, -42.0), (140.0, 42.0),
             (262.0, -44.0), (262.0, 44.0)]
H1 = (42.0, 28.0)                    # hovudleidning opp gjennom brettet
H2 = (181.0, 28.0)                   # leidning til nedkortet
J1 = (37.0, 0.0)
J2 = (185.0, 10.0)


def d_form(xl, R, z0, h, xc=XC):
    """D-form: rektangel frå xl til xc (|y| <= R) + halvsirkel R om (xc, 0)."""
    return (cq.Workplane("XY").workplane(offset=z0)
            .moveTo(xl, -R).lineTo(xc, -R).threePointArc((xc + R, 0), (xc, R))
            .lineTo(xl, R).close().extrude(h))


# ------------------------------------------------------------ D03 lysbrett
def lysbrett(p=P0):
    kl = p.t + 1.5
    b = stadion(p.S - 2 * kl, p.D - 2 * kl, Z_BRETT, TB, x0=kl)
    for x, y in MODUL_HOL:
        b = b.cut(syl_z(x, y, 1.7, Z_BRETT - 1, Z_BRETT_O + 1))
    for x, y in OPP_SKRUAR + RAMME_SKRUAR:          # PEM CLS-M3-1 (hol 4,22)
        b = b.cut(syl_z(x, y, 2.11, Z_BRETT - 1, Z_BRETT_O + 1))
    for x, y in LAAS_AVST:
        b = b.cut(syl_z(x, y, 2.0, Z_BRETT - 1, Z_BRETT_O + 1))
    b = b.cut(syl_z(*H1, 5.0, Z_BRETT - 1, Z_BRETT_O + 1))
    b = b.cut(syl_z(*H2, 3.0, Z_BRETT - 1, Z_BRETT_O + 1))
    return b


# ------------------------------------------------------------ D04 opp-kort
def opp_kort():
    x0, x1, hb = OPP_KORT
    k = boks(x0, x1, -hb, hb, Z_OPP_KORT, Z_OPP_KORT + T_OPP)
    k = k.edges("|Z").fillet(2.0)
    for x, y in OPP_SKRUAR:
        k = k.cut(syl_z(x, y, 1.7, Z_OPP_KORT - 1, Z_OPP_KORT + 3))
    return k


def opp_led():
    z = Z_OPP_KORT + T_OPP
    f = None
    for x, y in OPP_LED:
        b = boks(x - 1.5, x + 1.5, y - 1.5, y + 1.5, z, z + LED[2])
        f = b if f is None else f.union(b)
    return f


def jst(x, y, pol, z, opp=True):
    """JST PH, ståande hus: 2,0 mm deling. Hus (pol*2+1.9) x 4,5 x 6,0."""
    lx = pol * 2.0 + 1.9
    if opp:
        return boks(x - 2.25, x + 2.25, y - lx / 2, y + lx / 2, z, z + 6.0)
    return boks(x - 2.25, x + 2.25, y - lx / 2, y + lx / 2, z - 6.0, z)


# ------------------------------------------------------------ D05 ned-kort
def ned_kort():
    k = d_form(X_NED0, R_NED, Z_NED_KORT, T_PCB)
    for x, y in OPP_SKRUAR:                          # fri for skruespissane ovanfrå
        if x > X_NED0:
            k = k.cut(syl_z(x, y, 3.75, Z_NED_KORT - 1, Z_BRETT + 1))
    return k


def ned_led():
    z = Z_NED_KORT
    f = None
    for x, y in NED_LED:
        b = boks(x - 1.5, x + 1.5, y - 1.5, y + 1.5, z - LED[2], z)
        f = b if f is None else f.union(b)
    return f


# ------------------------------------------------------------ D06 ramme (PC kvit)
def ramme():
    zt = Z_BRETT
    h = zt - Z_RAMME0
    yt = R_RAMME_Y
    ytre = d_form(X_RAMME, yt, Z_RAMME0, h)
    indre = d_form(X_RAMME + T_RAMME, yt - T_RAMME, Z_RAMME0 - 1, h + 2)
    r = ytre.cut(indre)
    # nedre leppe: diffusoren kviler på ho (3 mm brei, 1 mm tjukk)
    lepp = d_form(X_RAMME, yt, Z_RAMME0, 1.0).cut(
        d_form(X_RAMME + T_RAMME + 3.0, yt - T_RAMME - 3.0, Z_RAMME0 - 1, 3))
    r = r.union(lepp)
    # øvre klemleppe under kanten av nedkortet (R36 -> vegg), 2 mm tjukk
    klem = d_form(X_RAMME, yt, Z_NED_KORT - 2.0, 2.0).cut(
        d_form(X_NED0 + 2.0, R_NED - 2.0, Z_NED_KORT - 3, 4))
    r = r.union(klem)
    # skrueknastar: M3 frå undersida opp i brettet
    for x, y in RAMME_SKRUAR:
        r = r.union(syl_z(x, y, 3.5, Z_NED_KORT - 2.0, zt))
        r = r.cut(syl_z(x, y, 1.7, Z_RAMME0 - 1, zt + 1))
    # leidningshol til nedkortet går ovanfor ramma; ingenting å skjere
    return r.intersect(d_form(X_RAMME, yt, Z_RAMME0, h))


# ------------------------------------------------------------ D07/D08 diffusorar
def diffusor_ned():
    r = R_RAMME_Y - T_RAMME - 0.5
    return d_form(X_RAMME + T_RAMME + 0.5, r, Z_DIFF_NED, T_DIFF)


def diffusor_opp(p=P0):
    kl = p.t + 2.5
    d = stadion(p.S - 2 * kl, p.D - 2 * kl, Z_DIFF_OPP, T_DIFF_OPP, x0=kl)
    for x, y in LAAS_AVST:
        d = d.cut(syl_z(x, y, 2.0, Z_DIFF_OPP - 1, Z_DIFF_OPP + T_DIFF_OPP + 1))
    return d


# ------------------------------------------------------------ smådelar
def laas_avstand():
    """Låsande avstandsstykke 16 mm, nylon 6.6 (snepper i Ø4-hol begge endar)."""
    f = None
    for x, y in LAAS_AVST:
        s = syl_z(x, y, 2.75, Z_BRETT_O, Z_DIFF_OPP)
        s = s.union(syl_z(x, y, 1.95, Z_BRETT - 0.3, Z_BRETT_O))      # nedre tapp
        s = s.union(syl_z(x, y, 2.6, Z_BRETT - 1.4, Z_BRETT - 0.3))   # nedre sperre, kort
        s = s.union(syl_z(x, y, 1.95, Z_DIFF_OPP, Z_DIFF_OPP + T_DIFF_OPP))
        s = s.union(syl_z(x, y, 2.6, Z_DIFF_OPP + T_DIFF_OPP, Z_DIFF_OPP + T_DIFF_OPP + 1.5))
        f = s if f is None else f.union(s)
    return f


def skrue_ned(x, y, z_hovud, L, d=3.0, dk=5.7, k=1.65):
    """Skrue med knappehovud (ISO 7380), hovudet oppå z_hovud, skaft nedover."""
    h = syl_z(x, y, dk / 2, z_hovud, z_hovud + k)
    s = syl_z(x, y, d / 2 - 0.15, z_hovud - L, z_hovud)
    return h.union(s)


def skrue_opp(x, y, z_hovud, L, d=3.0, dk=5.7, k=1.65):
    """Skrue med hovudet under z_hovud, skaft oppover."""
    h = syl_z(x, y, dk / 2, z_hovud - k, z_hovud)
    s = syl_z(x, y, d / 2 - 0.15, z_hovud, z_hovud + L)
    return h.union(s)


def modul_skruar():
    """ISO 7380 M3 x 5 ovanfrå gjennom brettet i PEM-mutter under ryggflensen."""
    f = None
    for x, y in MODUL_HOL:
        s = skrue_ned(x, y, Z_BRETT_O, 5.0)
        f = s if f is None else f.union(s)
    return f


def opp_kort_skruar():
    f = None
    for x, y in OPP_SKRUAR:
        s = skrue_ned(x, y, Z_OPP_KORT + T_OPP, 4.0, dk=5.5, k=1.3)
        f = s if f is None else f.union(s)
    return f


def ramme_skruar():
    f = None
    for x, y in RAMME_SKRUAR:
        s = skrue_opp(x, y, Z_NED_KORT - 2.0, 6.0, dk=5.5, k=1.3)
        f = s if f is None else f.union(s)
    return f


def kontaktar_opp():
    z = Z_OPP_KORT + T_OPP
    return jst(*J1, 4, z).union(jst(*J2, 2, z))


def pem_brett():
    """PEM CLS-M3-1 i brettet: hovud under for oppkortet, oppå for ramma."""
    f = None
    for x, y in OPP_SKRUAR:
        s = syl_z(x, y, PEM_H[0], Z_BRETT - PEM_H[1], Z_BRETT).cut(
            syl_z(x, y, 1.5, Z_BRETT - 2, Z_BRETT + 1))
        f = s if f is None else f.union(s)
    for x, y in RAMME_SKRUAR:
        s = syl_z(x, y, PEM_H[0], Z_BRETT_O, Z_BRETT_O + PEM_H[1]).cut(
            syl_z(x, y, 1.5, Z_BRETT_O - 1, Z_BRETT_O + 2))
        f = f.union(s)
    return f
