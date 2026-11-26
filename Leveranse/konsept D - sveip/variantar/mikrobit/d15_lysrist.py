# -*- coding: utf-8 -*-
"""d15_lysrist.py: lysrista D15, som sit mellom micro:bit V2 og framveggen.

Ei svart blokk med 25 kanalar, éin per LED, så kvar LED lyser opp berre sin eigen propp i veggen.
Foten under blokka blir skrudd til kortet med M3 i nylon gjennom ringane 0 til GND (senka hovud
framme, mutter og ringsko bak). Blokka er 4,8 mm tjukk: knapp A og B (4,55 mm) går klar av veggen,
og rista står 0,3 mm frå han. Måla er relative til midtre LED og er frå monteringsteikninga for V2.
  python d15_lysrist.py        skriv d15_lysrist.step og d15_lysrist.stl
"""
from pathlib import Path

import cadquery as cq

P = 4.0                      # LED-delinga
T = 4.8                      # tjukn, frå kretskortet og fram
KANAL = 2.4                  # kanal rundt kvar LED (0603 ståande: 0,8 x 1,6)
BLOKK = 23.0                 # blokka rundt matrisa, går klar av knapp A og B (innerkant ±16,9)
RINGAR = (-21.59, -11.43, 0.0, 11.43, 21.59)
RING_Z = -13.14
FOT = (51.6, 9.5)            # foten over ringane, like brei som kortet


def lysrist():
    d = cq.Workplane("XY").rect(BLOKK, BLOKK).extrude(T).edges("|Z").fillet(2.0)
    fot = cq.Workplane("XY").center(0, RING_Z).rect(*FOT).extrude(T).edges("|Z").fillet(2.0)
    d = d.union(fot)
    led = [((k - 2) * P, (2 - r) * P) for k in range(5) for r in range(5)]
    d = d.faces("<Z").workplane().pushPoints([(x, -z) for x, z in led]).hole(KANAL)
    # M3 med senka hovud frå framsida (flata mot veggen er z = T)
    d = d.faces(">Z").workplane().pushPoints([(x, RING_Z) for x in RINGAR]).cskHole(3.4, 6.0, 90)
    return d


if __name__ == "__main__":
    her = Path(__file__).resolve().parent
    d = lysrist()
    cq.exporters.export(d, str(her / "d15_lysrist.step"))
    cq.exporters.export(d, str(her / "d15_lysrist.stl"), tolerance=0.05, angularTolerance=0.2)
    bb = d.val().BoundingBox()
    print(f"D15: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, {d.val().Volume() / 1000:.2f} cm3")
    # kontroll mot kortet: kvar LED ligg fritt i sin kanal, og rista går klar av knappane
    for k in range(5):
        for r in range(5):
            l = cq.Workplane("XY").center((k - 2) * P, (2 - r) * P).rect(0.8 + 0.4, 1.6 + 0.4).extrude(0.5)
            assert d.intersect(l).val().Volume() < 1e-6, (k, r)
    for x in (-19.94, 19.94):
        kn = cq.Workplane("XY").center(x, 0.96).rect(6.0 + 0.6, 6.5 + 0.6).extrude(4.55)
        assert d.intersect(kn).val().Volume() < 1e-6, x
    kort = cq.Workplane("XY").center(0, 1.0).rect(51.6, 42.0).extrude(T)
    assert abs(d.intersect(kort).val().Volume() - d.val().Volume()) < 1e-3, "rista stikk utanfor kortet"
    print("kontroll: 25 LED-ar frie med 0,2 mm slark, knapp A og B frie med 0,3 mm, rista innanfor kortet")
