# -*- coding: utf-8 -*-
"""sveip_geometri.py: parametrisk geometri for lampa Sveip (konsept D), rev. B.

Koordinatar (mm): x mot høgre (utkraginga), y djupn (framside y < 0), z opp.
z = 0 er underkanten av kroppen. Bordet ligg i z = -P.fot_h (føtene).

Kroppen er éi aluminiumsplate (1,2 mm EN AW-5754 H22) valsa til eit stadionrøyr
300 x 105 mm: skjermen øvst er ein lukka ring, stamma under er ein U som står på
to botnflensar, utkraginga til høgre er skoren bort under skjermen.
Mål frå referansen: referanse/maaling.json (S = 300 mm, D = 0,35 S).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import cadquery as cq

# ---------------------------------------------------------------- parametrar


@dataclass
class P:
    # hovudform (yttermål på plata)
    S: float = 300.0          # breidd = høgd
    D: float = 105.0          # djupn
    t: float = 1.2            # platetjukkleik kropp (F8: masse under 1,2 kg)
    z_skjerm: float = 167.5   # underkant skjerm (0,558 S)
    x_stamme: float = 178.0   # høgre kant av stamma (0,593 S)
    r_inn: float = 12.0       # radius i det indre hjørnet stamme/skjerm
    x_hakk: float = 45.5      # hakket for leidningen: loddrett kant
    z_hakk: float = 61.0      # hakket: overkant
    r_hakk: float = 7.0
    # sveisesaum: loddrett i nasen på skjermen (x = S, y = 0), 132,5 mm, laser-buttsveis
    # med påløps- og avløpsflikar som blir skorne av; lampa er lik framme og bak

    # botnflensar (innover, berre på dei flate partia av stamma)
    fl_b: float = 16.0        # flensbreidd frå ytterflata: spor 3,4 x 5 med 3,5 mm til frikanten
    fl_ri: float = 2.0        # indre bøyeradius (5754 H22: min 1,5 t ved 90 grader)
    fl_x0: float = 80.0       # flensen startar 27,5 mm etter tangentlina (valsen går fri)
    fl_avl: float = 0.3       # avlasting: laserslisse 0,3 mm (lakken fyller han)
    fl_avl_h: float = 5.0
    K_flens: float = 0.42     # K-faktor for 90-gradarsbøyen (ri/t = 1,7)

    # fire skruar gjennom flensane, og TPE-føter som sneppar over skruehovuda
    fot_x: tuple = (86.0, 166.0)
    fot_h: float = 3.0
    fl_yc: float = 42.5       # 6,3 mm til kanten på chassisbotnen, 5,1 mm frå holkant til bøy

    # berøringspunkt (messing), framme og bak
    pkt_x: float = 165.0      # nede på foten, under kneet (R5: «på foten»)
    pkt_z: float = 70.0       # lågt: trykk på 7 N før lampa vippar
    pkt_hol: float = 12.3     # Ø12,1 hylse + lakk

    # innmat (éin modul, senka ned gjennom toppen)
    tc: float = 1.5           # chassis, 5754 H22
    rc_i: float = 1.5         # indre bøyeradius chassis
    klaring: float = 2.5      # mot kroppen (valsetoleranse, lakk)
    brett_z: float = 186.0    # underside lysbrett = topp av ryggflensen
    tb: float = 1.5           # lysbrett, 5754 H22
    usb_x: float = 23.0       # leidningen ut (frå skissa)

    @property
    def R(self):
        return self.D / 2.0

    @property
    def ri(self):  # indre radius i bogane
        return self.R - self.t

    @property
    def skrue_x(self):  # skruane sit i fotposisjonane
        return self.fot_x


P0 = P()

# ---------------------------------------------------------------- hjelparar


def stadion(L, W, z0, h, x0=0.0):
    """Stadionprisme: lengd L (x, ende til ende), breidd W (y), frå z0, høgd h."""
    r = W / 2.0
    s = (cq.Workplane("XY").workplane(offset=z0)
         .moveTo(x0 + r, -r).lineTo(x0 + L - r, -r)
         .threePointArc((x0 + L, 0), (x0 + L - r, r))
         .lineTo(x0 + r, r)
         .threePointArc((x0, 0), (x0 + r, -r)).close()
         .extrude(h))
    return s


def boks(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").add(cq.Solid.makeBox(
        x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0)))


def syl_y(x, z, r, y0, y1):
    """Sylinder langs y."""
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(
        r, y1 - y0, cq.Vector(x, y0, z), cq.Vector(0, 1, 0)))


def syl_z(x, y, r, z0, z1):
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(
        r, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0, 0, 1)))


def syl_x(y, z, r, x0, x1):
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(
        r, x1 - x0, cq.Vector(x0, y, z), cq.Vector(1, 0, 0)))


def bent_xz(pts, t, ri, y0, y1):
    """Bøygd plate: senterline pts (aksejusterte segment i XZ, 90-gradars bøyar),
    tjukkleik t, indre bøyeradius ri, ekstrudert frå y0 til y1."""
    rc = ri + t / 2.0
    n = len(pts)
    d = []
    for i in range(n - 1):
        ax, az = pts[i]
        bx, bz = pts[i + 1]
        L = math.hypot(bx - ax, bz - az)
        d.append(((bx - ax) / L, (bz - az) / L))
    # tangentpunkt
    start = [pts[0]]
    slutt = []
    bogar = []
    for i in range(1, n - 1):
        cx, cz = pts[i]
        d1, d2 = d[i - 1], d[i]
        T1 = (cx - rc * d1[0], cz - rc * d1[1])
        T2 = (cx + rc * d2[0], cz + rc * d2[1])
        C = (cx - rc * d1[0] + rc * d2[0], cz - rc * d1[1] + rc * d2[1])
        slutt.append(T1)
        start.append(T2)
        bogar.append((C, d1, d2))
    slutt.append(pts[-1])
    form = None
    for (a, b), (ux, uz) in zip(zip(start, slutt), d):
        # rett stykke: boks rundt senterlina
        nx, nz = -uz, ux
        xs = [a[0] + nx * t / 2, a[0] - nx * t / 2, b[0] + nx * t / 2, b[0] - nx * t / 2]
        zs = [a[1] + nz * t / 2, a[1] - nz * t / 2, b[1] + nz * t / 2, b[1] - nz * t / 2]
        if max(xs) - min(xs) < 1e-6 or max(zs) - min(zs) < 1e-6:
            continue
        stk = boks(min(xs), max(xs), y0, y1, min(zs), max(zs))
        form = stk if form is None else form.union(stk)
    for C, d1, d2 in bogar:
        ytre = syl_y(C[0], C[1], rc + t / 2, y0, y1)
        indre = syl_y(C[0], C[1], rc - t / 2, y0 - 1, y1 + 1)
        ring = ytre.cut(indre)
        # kvadranten mellom retning -d2 og d1 frå C
        e = rc + t
        px = [C[0], C[0] - d2[0] * e + d1[0] * e]
        pz = [C[1], C[1] - d2[1] * e + d1[1] * e]
        kv = boks(min(px), max(px), y0 - 1, y1 + 1, min(pz), max(pz))
        form = form.union(ring.intersect(kv))
    return form


def xz_profil(punkt_og_bogar, y0, y1):
    """Lukka profil i XZ-planet (liste av ('l', (x,z)) og ('a', (xm,zm), (x,z))),
    ekstrudert frå y0 til y1."""
    wp = cq.Workplane("XZ", origin=(0, 0, 0))
    first = punkt_og_bogar[0][1]
    wp = wp.moveTo(*first)
    for el in punkt_og_bogar[1:]:
        if el[0] == "l":
            wp = wp.lineTo(*el[1])
        else:
            wp = wp.threePointArc(el[1], el[2])
    wp = wp.close()
    # XZ-planet har normal -y: ekstruder begge vegar og skjer til [y0, y1]
    s = wp.extrude(1000, both=True)
    return s.intersect(boks(-2000, 2000, y0, y1, -2000, 2000))
