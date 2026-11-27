# -*- coding: utf-8 -*-
"""lag_delar.py: delane til monteringsrettleiinga for Sveip mini, som STL i éi monteringsramme (mm).

Ramma er lampa: x frå nasen mot utkraginga, y framover er minus, z opp. Printdelane kjem frå
../mini_print.py, micro:bit-en og beslaga er modellerte her. Beslag finst i to utgåver: ståande
(til beslagsida) og snudd som i lampa (til stega, med _y i namnet). posisjonar.json har stadene.
  python3 lag_delar.py
"""
import json
import math
import sys
from pathlib import Path

import cadquery as cq

HER = Path(__file__).resolve().parent
sys.path.insert(0, str(HER.parent))
import d15_lysrist as L15  # noqa: E402
import mini_print as MP  # noqa: E402
from mini_passform import MB, kortdelar  # noqa: E402

UT = HER / "delar"
UT.mkdir(exist_ok=True)
YK, MX, MZ = MP.YK, MB[0], MB[1]


def lampe(u, v, w):
    """Punkt i kortkoordinatar (u, v, w) til lampa. Kortet står rotert 90° med klokka sett framanfrå."""
    return [round(MX + v, 3), round(YK - w, 3), round(MZ - u, 3)]


def snu(form):
    """Same rotasjon som kortet får i lampa, utan flytting: w (ut frå kortet) blir -y."""
    return form.rotate((0, 0, 0), (0, 0, 1), -90).rotate((0, 0, 0), (1, 0, 0), 90)


def gjenger(form, r, z0, z1, steg=0.5):
    """Grunne ringspor langs skaftet, så skruen les som gjenga i strek."""
    z = z0 + steg
    while z < z1 - 0.2:
        form = form.cut(cq.Workplane("XY").workplane(offset=z).circle(r + 1).circle(r - 0.18).extrude(0.12))
        z += steg
    return form


def kryss(form, z_topp, d=2.6, djupn=0.9):
    for vinkel in (0, 90):
        spor = cq.Workplane("XY").box(d, 0.55, djupn * 2).translate((0, 0, z_topp)).rotate((0, 0, 0), (0, 0, 1), vinkel)
        form = form.cut(spor)
    return form


def skrue_a():
    """M3 x 8 senkskrue (DIN 965), hovudet øvst i z = 0, skaftet nedover."""
    hovud = cq.Workplane("XY").add(cq.Solid.makeCone(1.5, 2.8, 1.65, cq.Vector(0, 0, -1.65)))
    skaft = cq.Workplane("XY").workplane(offset=-8.0).circle(1.5).extrude(8.0 - 1.65)
    s = hovud.union(skaft)
    return kryss(gjenger(s, 1.5, -8.0, -1.65), 0.0)


def skrue_b():
    """M3 x 4 messingskrue med linsehovud (DIN 7985): anleggsflata i z = 0, hovudet over, skaftet under."""
    hovud = cq.Workplane("XY").circle(2.8).extrude(2.4).edges(">Z").fillet(1.0)
    skaft = cq.Workplane("XY").workplane(offset=-4.0).circle(1.5).extrude(4.0)
    s = hovud.union(skaft)
    return kryss(gjenger(s, 1.5, -4.0, 0.0), 2.4)


def fjor():
    """Fjør Ø 3,0 x 3,0, tråd 0,3: fem vindingar frå z = 0 og opp, flate i endane."""
    s = cq.Workplane("XY")
    for k, z in enumerate((0.15, 0.85, 1.5, 2.15, 2.85)):
        ring = cq.Solid.makeTorus(1.35, 0.15, pnt=cq.Vector(0, 0, 0), dir=cq.Vector(0, 0, 1))
        vipp = 0.0 if k in (0, 4) else 8.0
        s = s.union(cq.Workplane("XY").add(ring).rotate((0, 0, 0), (1, 0, 0), vipp).translate((0, 0, z)))
    return s


def leiar():
    """Lysleiar: 1,75 mm filament, 4,4 mm langt, frå z = 0 og opp."""
    return cq.Workplane("XY").circle(0.875).extrude(4.4)


def usb():
    """micro-USB-plugg med kabel, i lampa: metallet inn i kontakten, kabelen ut gjennom endeplata."""
    xk = MX + 22.0 + 1.4
    yu, zu = YK + 1.6 + 1.2, MZ - 0.13
    metall = MP.boks(xk - 5.0, xk + 1.0, yu - 0.9, yu + 0.9, zu - 3.425, zu + 3.425)
    hovud = MP.boks(xk + 1.0, xk + 16.0, yu - 3.5, yu + 3.5, zu - 5.3, zu + 5.3).edges("|X").fillet(1.5)
    kabel = cq.Workplane("YZ", origin=(xk + 16.0, yu, zu)).circle(1.75).extrude(26.0)
    hals = cq.Workplane("YZ", origin=(xk + 15.0, yu, zu)).circle(2.6).extrude(4.0)
    return metall.union(hovud).union(hals).union(kabel)


def mikrobit():
    """micro:bit V2 i kortkoordinatar: kort med ringhol, knappar, LED-ar, logo og komponentar bak."""
    def kboks(u0, u1, v0, v1, w0, w1):
        return cq.Workplane("XY").box(u1 - u0, v1 - v0, w1 - w0, centered=False).translate((u0, v0, w0))
    k = kboks(-25.8, 25.8, -20.0, 22.0, -1.6, 0.0).edges("|Z").fillet(3.0)
    k = k.cut(cq.Workplane("XY").workplane(offset=-2).pushPoints([(u, L15.RING_V) for u in L15.RINGAR]).circle(2.0).extrude(3))
    for u in (-19.94, 19.94):
        k = k.union(kboks(u - 3.0, u + 3.0, 0.96 - 3.25, 0.96 + 3.25, 0.0, 3.4))
        k = k.union(cq.Workplane("XY").workplane(offset=3.4).center(u, 0.96).circle(1.6).extrude(1.15))
    for u, v in L15.LED:
        k = k.union(kboks(u - 0.4, u + 0.4, v - 0.8, v + 0.8, 0.0, 0.4))
    logo = cq.Workplane("XY").center(*L15.LOGO).ellipse(4.35, 2.45).ellipse(3.85, 1.95).extrude(0.06)
    k = k.union(logo)
    k = k.union(kboks(-22.77, -14.87, 12.96, 21.56, -7.1, -1.6))          # JST
    k = k.union(kboks(-12.78, -6.28, 15.86, 21.86, -6.15, -1.6))          # reset
    k = k.union(kboks(-4.0, 4.0, -2.25, 5.75, -4.6, -1.6))                # høgtalar
    k = k.union(kboks(-4.0, 4.0, 17.14, 23.4, -4.0, -1.6))                # micro-USB
    return k


def skriv(namn, form):
    cq.exporters.export(form, str(UT / f"{namn}.stl"), tolerance=0.02, angularTolerance=0.12)
    print(f"  {namn}")


if __name__ == "__main__":
    kort = kortdelar(YK)
    skriv("M1", MP.kropp())
    skriv("M2", MP.chassis())
    skriv("M3", kort["lysrist D15"])
    skriv("M4", MP.lysplate())
    skriv("MB", snu(mikrobit()).translate((MX, YK, MZ)))
    a, b, c, d = skrue_a(), skrue_b(), fjor(), leiar()
    for namn, form in (("A", a), ("B", b), ("C", c), ("D", d)):
        # lysleiaren ligg på beslagsida, så han ikkje blir teikna høgare enn skruane
        skriv(namn, form.rotate((0, 0, 0), (0, 1, 0), 90) if namn == "D" else form)
        skriv(f"{namn}_y", snu(form))
    skriv("E", usb())
    pos = {
        "A": [lampe(u, L15.RING_V, L15.T_FOT) for u in L15.RINGAR],          # toppen av hovudet, i flukt med foten
        "B": [lampe(*L15.LOGO, MP.AVST + MP.T - MP.FELT_DJUPN)],            # anleggsflata, på framflata i feltet
        "C": [lampe(*L15.LOGO, 0.0)],                                       # står på logoen
        "D": [lampe(u, v, MP.LED_TOPP) for u, v in L15.LED],               # frå toppen av LED-en
        "logo": lampe(*L15.LOGO, 0.0),
        "kant": lampe(25.8, -20.0, 0.0),                                    # hjørnet ved kanten og hylla på stolpen
        "felt": [round(MX + 14.0, 3), round(-MP.D / 2, 3), round(MZ, 3)],
        "usb": [round(MP.X_ST, 3), round(YK + 2.8, 3), round(MZ, 3)],
        "z_plate": round(MP.Z_PLATE, 3),
    }
    (HER / "delar" / "posisjonar.json").write_text(json.dumps(pos, indent=1), encoding="utf-8")
    print("SKREIV", UT)
