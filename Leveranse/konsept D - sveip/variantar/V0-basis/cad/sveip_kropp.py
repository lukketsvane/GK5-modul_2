# -*- coding: utf-8 -*-
"""Kroppen (D01) og chassiset (D02) for Sveip rev. B, med flatmønster."""
from __future__ import annotations

import math

import cadquery as cq

from sveip_geometri import P0, boks, bent_xz, stadion, syl_x, syl_y, syl_z, xz_profil

# posisjonar (x, y) som fleire delar deler
HK_HOL = [(74.0, -26.0), (74.0, 26.0), (164.0, -26.0), (164.0, 26.0)]   # hovudkort
MODUL_HOL = [(152.0, -35.0), (152.0, 35.0), (165.0, -35.0), (165.0, 35.0)]  # lysbrett på ryggflensen
LUKE_SKRUAR = [(72.0, 0.0), (167.0, 0.0)]
LUKE_OPNING = (78.0, 162.0, 30.0)                                        # x0, x1, breidd
USB_YS = 13.0                                                            # USB-kort, y = +-13
BK_Y = (-30.0, 30.0)                                                     # berøringskort, skruar
RYGG_FLENS = 8.0                                                         # sideflensar på ryggen
SPOR = (3.4, 5.0)                                                        # flenshol: spor (x, y)


def spor_z(x, y, bx, by, z0, z1):
    """Avlangt hol (spor) langs y."""
    r = bx / 2
    return (cq.Workplane("XY").workplane(offset=z0).center(x, y)
            .slot2D(by, bx, 90).extrude(z1 - z0))


# ---------------------------------------------------------------- D01 kropp


def kropp(p=P0, med_hol=True):
    S, D, t, R = p.S, p.D, p.t, p.R
    ring = stadion(S, D, 0, S).cut(stadion(S - 2 * t, D - 2 * t, -1, S + 2, x0=t))

    # utkraginga: alt til høgre for stamma under skjermen, R12 i det indre hjørnet
    xs, zs, r = p.x_stamme, p.z_skjerm, p.r_inn
    k = r * (1 - math.sqrt(0.5))
    tomrom = xz_profil([
        ("l", (xs, -20)), ("l", (S + 20, -20)), ("l", (S + 20, zs)),
        ("l", (xs + r, zs)),
        ("a", (xs + k, zs - k), (xs, zs - r)),
        ("l", (xs, -20))], -200, 200)
    ring = ring.cut(tomrom)

    # hakket for leidningen i venstre boge, R7 i hjørnet
    xh, zh, rh = p.x_hakk, p.z_hakk, p.r_hakk
    kh = rh * (1 - math.sqrt(0.5))
    hakk = xz_profil([
        ("l", (-20, -20)), ("l", (xh, -20)), ("l", (xh, zh - rh)),
        ("a", (xh - kh, zh - kh), (xh - rh, zh)),
        ("l", (-20, zh)), ("l", (-20, -20))], -200, 200)
    ring = ring.cut(hakk)

    # botnflensar framme og bak, frå fl_x0 til stammekanten
    x0, x1 = p.fl_x0, xs
    for sy in (-1, 1):
        yv0, yv1 = sorted((sy * R, sy * (R - t)))
        ring = ring.cut(boks(x0, x1 + 1, yv0 - 0.01, yv1 + 0.01, -1, 6))
        # avlasting: laserslisse 0,3 mm framfor flensen
        ring = ring.cut(boks(x0 - p.fl_avl, x0, min(yv0, yv1) - 0.5, max(yv0, yv1) + 0.5,
                             -1, p.fl_avl_h))
        ring = ring.union(flens(p, sy, x0, x1))

    if med_hol:
        for sy in (-1, 1):   # berøringspunkt framme og bak
            a, b = sorted((sy * (R + 1), sy * (R - t - 1)))
            ring = ring.cut(syl_y(p.pkt_x, p.pkt_z, p.pkt_hol / 2, a, b))
        for sy in (-1, 1):   # spor 3,4 x 6 for M3 i fotposisjonane
            for x in p.fot_x:
                ring = ring.cut(spor_z(x, sy * p.fl_yc, SPOR[0], SPOR[1], -1, t + 1))
    return ring


def flens(p, sy, x0, x1):
    """Botnflens: vegg ned, 90 graders bøy (ri), flens innover. sy = -1 framme."""
    R, t, ri = p.R, p.t, p.fl_ri
    ro = ri + t
    yo, yi, yc, ye = R, R - t, R - ro, R - p.fl_b
    mid_o = (-yc - ro * math.sqrt(0.5), ro - ro * math.sqrt(0.5))
    mid_i = (-yc - ri * math.sqrt(0.5), ro - ri * math.sqrt(0.5))
    wp = (cq.Workplane("YZ").moveTo(-yo, 6.0).lineTo(-yo, ro)
          .threePointArc(mid_o, (-yc, 0.0)).lineTo(-ye, 0.0).lineTo(-ye, t)
          .lineTo(-yc, t).threePointArc(mid_i, (-yi, ro)).lineTo(-yi, 6.0).close())
    s = wp.extrude(1000, both=True).intersect(boks(x0, x1, -500, 500, -500, 500))
    if sy > 0:
        s = s.mirror("XZ")
    return s


# ---------------------------------------------------------------- D02 chassis


def chassis_senterline(p=P0):
    tc = p.tc
    z_tak = p.z_hakk + tc / 2          # taket over hakket: underside flukt med hakket
    x_vegg = p.x_hakk + tc / 2         # veggen: ytterside flukt med hakkanten
    z_botn = p.t + tc / 2              # botnplata ligg oppå flensane
    x_rygg = p.x_stamme - 2.0 - tc / 2  # ryggen 2 mm inn frå stammekanten
    z_topp = p.brett_z - tc / 2         # toppflensen ber lysbrettet
    return [(0.0, z_tak), (x_vegg, z_tak), (x_vegg, z_botn), (x_rygg, z_botn),
            (x_rygg, z_topp), (x_rygg - 30.0, z_topp)]


def chassis_b(p=P0):
    return p.D / 2 - p.t - 2.5          # 48,8: 0,5 mm fri av bøyeradien i flensen


def chassis(p=P0, med_hol=True):
    pts = chassis_senterline(p)
    b = chassis_b(p)
    c = bent_xz(pts, p.tc, p.rc_i, -b, b)
    # sideflensar på ryggen (U-profil): bøygde 90 grader mot hakket, 8 mm djupe
    x_rv = pts[3][0] - p.tc / 2                      # venstre flate av ryggen
    z_a = pts[2][1] + p.tc / 2 + p.rc_i + 3.0        # fri av bøyane (avlasting)
    z_b = pts[4][1] - p.tc / 2 - p.rc_i - 3.0
    for sy in (-1, 1):
        y0, y1 = sorted((sy * b, sy * (b - p.tc)))
        c = c.union(boks(x_rv - RYGG_FLENS + p.tc, x_rv, y0, y1, z_a, z_b))
    # klaringskonvolutt: innsida av kroppen minus klaringa
    konv = stadion(p.S - 2 * (p.t + p.klaring), p.D - 2 * (p.t + p.klaring), -5, p.S + 10,
                   x0=p.t + p.klaring)
    konv = konv.union(boks(p.x_hakk, p.S, -b, b, -5, p.S + 10))   # botn og rygg går ut til b
    c = c.intersect(konv)
    if not med_hol:
        return c
    z_tak = pts[0][1]
    z_botn = pts[2][1]
    z_topp = pts[4][1]
    c = c.cut(rund_rekt(p.usb_x, 0.0, 3.9, 9.6, z_tak - 5, z_tak + 5, r=0.5))   # USB-C
    for y in (-USB_YS, USB_YS):                       # PEM SO-M3-3 for USB-kortet
        c = c.cut(syl_z(p.usb_x, y, 2.11, z_tak - 5, z_tak + 5))
    lx0, lx1, lb = LUKE_OPNING                        # batteriluke
    c = c.cut(rund_rekt((lx0 + lx1) / 2, 0.0, lx1 - lx0, lb, z_botn - 5, z_botn + 5, r=3.0))
    for sy in (-1, 1):                                # PEM CLS-M3-2 for kroppsskruane
        for x in p.fot_x:
            c = c.cut(syl_z(x, sy * p.fl_yc, 2.11, z_botn - 5, z_botn + 5))
    for x, y in HK_HOL:                               # frihol, avstandsbolt hovudkort
        c = c.cut(syl_z(x, y, 1.7, z_botn - 5, z_botn + 5))
    for x, y in LUKE_SKRUAR:                          # PEM for myntskruane
        c = c.cut(syl_z(x, y, 2.11, z_botn - 5, z_botn + 5))
    for x, y in MODUL_HOL:                            # PEM for lysbrettet
        c = c.cut(syl_z(x, y, 2.11, z_topp - 5, z_topp + 5))
    for y in BK_Y:                                    # PEM SO-M3-3 for berøringskortet
        c = c.cut(syl_x(y, p.pkt_z, 2.11, pts[3][0] - 5, pts[3][0] + 5))
    # jordpunkt: umaskert flekk under eitt kroppsskruehovud (merknad i teikninga)
    return c


def rund_rekt(xc, yc, lx, ly, z0, z1, r=None):
    r = min(lx, ly) / 2 - 1e-3 if r is None else r
    return (cq.Workplane("XY").workplane(offset=z0).center(xc, yc)
            .rect(lx, ly).extrude(z1 - z0).edges("|Z").fillet(r))


# ---------------------------------------------------------------- flatmønster


def kropp_flat(p=P0):
    """Flatmønster for kroppen (s langs nøytralfibra, z). s = 0 i nasen (x = S, y = 0),
    s aukar langs framsida. K = 0,5 i bogane, p.K_flens i flensbøyen."""
    t, R = p.t, p.R
    rn = R - t / 2
    flat = p.S - 2 * R
    bog = math.pi * rn
    q = bog / 2
    L = 2 * flat + 2 * bog
    xR, xL = p.S - R, R

    def s_framme(x):   # framre flate, x frå xR mot xL
        return q + (xR - x)

    s_v0 = s_framme(xL)
    s_v1 = s_v0 + bog

    def s_bak(x):      # bakre flate, x frå xL mot xR
        return s_v1 + (x - xL)

    assert abs(s_bak(xR) + q - L) < 1e-6
    sa, sb = s_framme(p.x_stamme), s_bak(p.x_stamme)
    phi = math.acos((R - p.x_hakk) / rn)
    s_mid = s_v0 + bog / 2
    ha, hb = s_mid - rn * phi, s_mid + rn * phi
    BA = math.pi / 2 * (p.fl_ri + p.K_flens * t)
    fl_flat = p.fl_b - (p.fl_ri + t)
    z_v = p.fl_ri + t
    z_fl1 = z_v - BA
    z_fl2 = z_fl1 - fl_flat
    fa0, fa1 = s_framme(p.x_stamme), s_framme(p.fl_x0)
    fb0, fb1 = s_bak(p.fl_x0), s_bak(p.x_stamme)
    return dict(L=L, bog=bog, q=q, rn=rn, flat=flat, sa=sa, sb=sb, ha=ha, hb=hb, phi=phi,
                s_boge=[(0.0, q), (s_v0, s_v1), (L - q, L)],
                flens=[(fa0, fa1), (fb0, fb1)], BA=BA, z_v=z_v, z_fl1=z_fl1, z_fl2=z_fl2,
                s_framme=s_framme, s_bak=s_bak)
