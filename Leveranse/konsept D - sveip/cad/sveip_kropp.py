# -*- coding: utf-8 -*-
"""Kroppen (D01) og chassiset (D02) for Sveip, med flatmønster."""
from __future__ import annotations

import math

import cadquery as cq

from sveip_geometri import P0, boks, bent_xz, stadion, syl_x, syl_y, syl_z, xz_profil

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

    # botnflensar framme og bak: bøygd profil i YZ, ekstrudert langs x
    x0, x1 = p.fl_x0, xs
    ro = p.fl_ri + t
    for sy in (-1, 1):
        # fjern den rette veggen der flensen skal bøyast
        yv0, yv1 = sorted((sy * R, sy * (R - t)))
        ring = ring.cut(boks(x0, x1 + 1, yv0 - 0.01, yv1 + 0.01, -1, 6))
        # avlastingsspor framfor flensen
        ring = ring.cut(boks(x0 - p.fl_avl, x0, min(yv0, yv1) - 0.5, max(yv0, yv1) + 0.5,
                             -1, p.fl_avl_h))
        ring = ring.union(flens(p, sy, x0, x1))

    if med_hol:
        # berøringspunkt framme og bak
        for sy in (-1, 1):
            ring = ring.cut(syl_y(p.pkt_x, p.pkt_z, p.pkt_hol / 2,
                                  sy * (R + 1) if sy < 0 else R - t - 1,
                                  -(R - t - 1) if sy < 0 else R + 1))
        # hol i flensane: M3 frihol (skrue nedanfrå) og push-in føter
        for sy in (-1, 1):
            for x in p.skrue_x:
                ring = ring.cut(syl_z(x, sy * p.fl_yc, 1.7, -1, t + 1))
            for x in p.fot_x:
                ring = ring.cut(syl_z(x, sy * p.fl_yc, 2.1, -1, t + 1))
    return ring


def flens(p, sy, x0, x1):
    """Botnflens: vegg ned, 90 graders bøy (ri), flens innover. sy = -1 framme."""
    R, t, ri = p.R, p.t, p.fl_ri
    ro = ri + t
    # profil i (u = |y|-retning innover, z); bygg for framsida og spegl
    yo = R              # ytterflate
    yi = R - t          # innerflate
    yc = R - ro         # bøyesenter (|y|)
    ye = R - p.fl_b     # flensen sluttar
    # bogane har senter i (-yc, ro); midtpunkta ligg på 45 grader
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


def chassis(p=P0, med_hol=True):
    pts = chassis_senterline(p)
    b = p.D / 2 - p.t - 2.5             # 0,5 mm fri av bøyeradien i flensen
    c = bent_xz(pts, p.tc, p.rc_i, -b, b)
    # klaringskonvolutt: innsida av kroppen minus 1 mm
    konv = stadion(p.S - 2 * (p.t + p.klaring), p.D - 2 * (p.t + p.klaring), -5, p.S + 10,
                   x0=p.t + p.klaring)
    c = c.intersect(konv)
    if not med_hol:
        return c
    z_tak = pts[0][1]
    z_botn = pts[2][1]
    z_topp = pts[4][1]
    # USB-C: opning i taket (8,94 x 3,26 munning + 0,3 klaring), langs y
    c = c.cut(rund_rekt(p.usb_x, 0.0, 3.9, 9.6, z_tak - 5, z_tak + 5, r=0.5))
    # 2 x PEM SO-M3-3 avstandsbolt for USB-kortet
    for y in (-USB_YS, USB_YS):
        c = c.cut(syl_z(p.usb_x, y, 2.11, z_tak - 5, z_tak + 5))
    # klaring for push-in-føtene sine soppehovud
    for sy in (-1, 1):
        for x in p.fot_x:
            c = c.cut(syl_z(x, sy * p.fl_yc, 3.5, z_botn - 5, z_botn + 5))
    # batteriluke i botnen
    lx0, lx1, lb = LUKE_OPNING
    c = c.cut(rund_rekt((lx0 + lx1) / 2, 0.0, lx1 - lx0, lb, z_botn - 5, z_botn + 5, r=3.0))
    # berøringskortet på venstre side av ryggen: 2 x PEM-mutter (hol 4,22)
    for y in BK_Y:
        c = c.cut(syl_x(y, p.pkt_z, 2.11, pts[3][0] - 5, pts[3][0] + 5))
    # PEM-mutrar M3 for kroppskruane (hol 4,22)
    for sy in (-1, 1):
        for x in p.skrue_x:
            c = c.cut(syl_z(x, sy * p.fl_yc, 2.11, z_botn - 5, z_botn + 5))
    # frihol for skruane som held avstandsbolten til hovudkortet (M3 nedanfrå)
    for x, y in HK_HOL:
        c = c.cut(syl_z(x, y, 1.7, z_botn - 5, z_botn + 5))
    # luka: PEM-mutrar for dei to myntskruane
    for x, y in LUKE_SKRUAR:
        c = c.cut(syl_z(x, y, 2.11, z_botn - 5, z_botn + 5))
    # toppflensen: 4 PEM-mutrar M3 for lysmodulen
    for x, y in MODUL_HOL:
        c = c.cut(syl_z(x, y, 2.11, z_topp - 5, z_topp + 5))
    return c


def rund_rekt(xc, yc, lx, ly, z0, z1, r=None):
    r = min(lx, ly) / 2 - 1e-3 if r is None else r
    return (cq.Workplane("XY").workplane(offset=z0).center(xc, yc)
            .rect(lx, ly).extrude(z1 - z0).edges("|Z").fillet(r))


# posisjonar (x, y) som fleire delar deler
HK_HOL = [(74.0, -26.0), (74.0, 26.0), (164.0, -26.0), (164.0, 26.0)]   # hovudkort
LUKE_OPNING = (81.0, 159.0, 25.0)                                        # x0, x1, breidd
BK_Y = (-30.0, 30.0)                                                     # berøringskort, skruar
MODUL_HOL = [(152.0, -35.0), (152.0, 35.0), (168.0, -35.0), (168.0, 35.0)]  # lysmodul
LUKE_SKRUAR = [(76.0, 0.0), (166.0, 0.0)]
USB_YS = 13.0                                                            # USB-kort, y = +-13


# ---------------------------------------------------------------- flatmønster


def kropp_flat(p=P0):
    """Flatmønster for kroppen (s langs nøytralfibra, z). K = 0,5.
    Returnerer dict med omriss (liste av segment), hol, bøyeliner og mål."""
    t, R = p.t, p.R
    rn = R - t / 2                      # nøytral radius
    flat = p.S - 2 * R                  # 195
    bog = math.pi * rn                  # 180 grader
    L = 2 * flat + 2 * bog
    # s = 0 i saumen (bakre flate, x = x_saum), s aukar mot +x på baksida
    xR = p.S - R
    xL = R
    s_bak_hogre = xR - p.x_saum                  # bakre flate x_saum -> xR
    s_boge_h0 = s_bak_hogre
    s_boge_h1 = s_boge_h0 + bog
    def s_framme(x):  # framre flate, x frå xR mot xL
        return s_boge_h1 + (xR - x)
    s_boge_v0 = s_framme(xL)
    s_boge_v1 = s_boge_v0 + bog
    def s_bak(x):     # bakre flate, x frå xL mot x_saum
        return s_boge_v1 + (x - xL)
    assert abs(s_bak(p.x_saum) - L) < 1e-6
    # stamma under skjermen: frå framre x_stamme til bakre x_stamme
    sa = s_framme(p.x_stamme)
    sb = s_bak(p.x_stamme)
    # hakket: vinkel der planet x = x_hakk kryssar nøytralflata
    phi = math.acos((R - p.x_hakk) / rn)
    s_mid = s_boge_v0 + bog / 2
    ha, hb = s_mid - rn * phi, s_mid + rn * phi
    # flensar: x frå fl_x0 til x_stamme, framme og bak
    BA = math.pi / 2 * (p.fl_ri + t / 2)
    fl_flat = p.fl_b - (p.fl_ri + t)
    z_v = p.fl_ri + t                    # rett vegg sluttar (ytterflate)
    z_fl1 = z_v - BA                     # flatt flensparti byrjar
    z_fl2 = z_fl1 - fl_flat              # flensen sluttar
    fa0, fa1 = s_framme(p.x_stamme), s_framme(p.fl_x0)
    fb0, fb1 = s_bak(p.fl_x0), s_bak(p.x_stamme)
    return dict(L=L, bog=bog, rn=rn, flat=flat, sa=sa, sb=sb, ha=ha, hb=hb, phi=phi,
                s_boge=[(s_boge_h0, s_boge_h1), (s_boge_v0, s_boge_v1)],
                flens=[(fa0, fa1), (fb0, fb1)], BA=BA, z_v=z_v, z_fl1=z_fl1, z_fl2=z_fl2,
                s_framme=s_framme, s_bak=s_bak)
