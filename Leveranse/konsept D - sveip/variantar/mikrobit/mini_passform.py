# -*- coding: utf-8 -*-
"""mini_passform.py: kontrollerer at micro:bit V2 får plass i stamma på Sveip mini.

Mini er rev. B i skala K = 0,36 (108 x 108 x 37,8 mm), med 1,0 mm plate. Kortet står rotert 90°
med klokka bak framveggen på stamma: overkanten med USB peikar mot den opne enden av stamma,
kantkontakten mot nasen. Midtre LED står midt på stamma, både i breidda og i høgda. Skriptet
byggjer veggen og delane på kortet som lekamar og måler den minste avstanden mellom dei.
  python mini_passform.py
"""
import math

import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

from d15_lysrist import lysrist

K = 0.36
S, D, R = 300 * K, 105 * K, 52.5 * K          # 108 x 37,8, naseradius 18,9
X_ST, Z_SK = 178 * K, 167.5 * K               # stamma: 64,1 brei, 60,3 høg
T = 1.0                                       # plata (ikkje skalert)
MB = (X_ST / 2, Z_SK / 2)                     # midtre LED: midt på stamma (32,04; 30,15)
BOTN = 3.0                                    # minste høgd under kortet (golv og luft)
AVST = 5.1                                    # frå innsida av framveggen til framsida av kretskortet
YK = -D / 2 + T + AVST                        # framsida av kretskortet (y)


def stadion(lengd, djupn, z0, z1, x0=0.0):
    r = djupn / 2
    return (cq.Workplane("XY").workplane(offset=z0).center(x0 + lengd / 2, 0)
            .slot2D(lengd, djupn, 0).extrude(z1 - z0))


def boks(u0, u1, v0, v1, w0, w1):
    """Del på kortet. (u, v) er som på kortet sett framanfrå med kantkontakten ned, w er djupn
    framfor (+) og bak (-) framsida av kretskortet. Rotert 90° med klokka: x = v, z = -u."""
    x0, x1 = MB[0] + v0, MB[0] + v1
    z0, z1 = MB[1] - u1, MB[1] - u0
    y0, y1 = YK - w1, YK - w0                 # framover er mot -y
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


vegg = stadion(S, D, 0, S).cut(stadion(S - 2 * T, D - 2 * T, -1, S + 1, x0=T))
vegg = vegg.intersect(cq.Workplane("XY").box(X_ST + 5, D + 2, S, centered=False).translate((-1, -D / 2 - 1, 0)))

delar = {
    "kretskort": boks(-25.8, 25.8, -20.0, 22.0, -1.6, 0.0).edges("|Y").fillet(3.0),
    "knapp A": boks(-19.94 - 3.0, -19.94 + 3.0, 0.96 - 3.25, 0.96 + 3.25, 0.0, 4.55),
    "knapp B": boks(19.94 - 3.0, 19.94 + 3.0, 0.96 - 3.25, 0.96 + 3.25, 0.0, 4.55),
    # D15 er bygd i (u, v, w): snu han same veg som kortet og set han framfor kretskortet
    "lysrist D15": lysrist().rotate((0, 0, 0), (0, 0, 1), -90).rotate((0, 0, 0), (1, 0, 0), 90).translate((MB[0], YK, MB[1])),
    "JST": boks(-22.77, -14.87, 12.96, 21.56, -1.6 - 5.5, -1.6),
    "reset": boks(-9.53 - 3.25, -9.53 + 3.25, 18.86 - 3.0, 18.86 + 3.0, -1.6 - 4.55, -1.6),
    "hogtalar": boks(-4.0, 4.0, 1.75 - 4.0, 1.75 + 4.0, -1.6 - 3.0, -1.6),
    "USB": boks(-4.0, 4.0, 22.0 - 4.86, 22.0 + 1.4, -1.6 - 2.4, -1.6),
}


def avstand(a, b):
    d = BRepExtrema_DistShapeShape(a.val().wrapped, b.val().wrapped)
    d.Perform()
    return d.Value()


if __name__ == "__main__":
    print(f"Sveip mini, K = {K}: {S:.1f} x {S:.1f} x {D:.1f} mm, stamme {X_ST:.1f} x {Z_SK:.1f}, plate {T} mm")
    print(f"midtre LED i x = {MB[0]:.1f}, z = {MB[1]:.1f}. Flat framvegg frå x = {R:.1f} til {X_ST:.1f}")
    minst = 9e9
    for namn, d in delar.items():
        bb = d.val().BoundingBox()
        a = avstand(d, vegg)
        minst = min(minst, a)
        print(f"  {namn:11s} x {bb.xmin:5.1f}..{bb.xmax:5.1f}  z {bb.zmin:5.1f}..{bb.zmax:5.1f}  til veggen {a:5.2f} mm")
    kort = delar["kretskort"].val().BoundingBox()
    print(f"  kretskortet: {kort.xmin:.2f} frå nasespissen, {X_ST - kort.xmax:.2f} til enden av stamma, "
          f"{kort.zmin:.2f} over underkanten, {Z_SK - kort.zmax:.2f} under skjermsaumen")
    usb = delar["USB"].val().BoundingBox()
    print(f"  USB-kontakten sluttar {X_ST - usb.xmax:.2f} mm innanfor enden av stamma")
    bak = D / 2 - T - (YK + 1.6 + 5.5)
    print(f"  fri djupn bak det høgaste på kortet: {bak:.1f} mm (2 x AAA-haldar er om lag 14 mm)")
    assert minst >= 0.3 - 1e-6, "noko ligg nærare veggen enn 0,3 mm"
    assert kort.xmax <= X_ST - 3.0 and kort.zmin >= BOTN - 1e-9
    print(f"OK: minste avstand til veggen er {minst:.2f} mm (lysrista skal stå 0,3 mm frå veggen)")
