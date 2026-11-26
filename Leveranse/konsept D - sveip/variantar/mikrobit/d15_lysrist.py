# -*- coding: utf-8 -*-
"""d15_lysrist.py: lysrista D15 for Sveip mini, som sit mellom micro:bit V2 og framveggen.

Ei svart blokk med 25 kanalar, éin per LED, så kvar LED lyser opp berre sin eigen propp i veggen.
Blokka er 4,8 mm tjukk: knapp A og B (4,55 mm) går klar av veggen, og rista står 0,3 mm frå han.
Foten over ringane er 3,0 mm, for der krummar nasen på lampa inn mot kortet. Rista blir skrudd
til kortet med M3 i nylon gjennom ringane (senka hovud framme, mutter bak). Mot logoen er blokka
kort, så hylsa til messingpunktet får plass. Måla er relative til midtre LED, slik kortet ser ut
framanfrå med kantkontakten ned, og er frå monteringsteikninga for V2.
  python d15_lysrist.py        skriv d15_lysrist.step og d15_lysrist.stl
"""
from pathlib import Path

import cadquery as cq

P = 4.0                      # LED-delinga
T = 4.8                      # tjukn på blokka, frå kretskortet og fram
T_FOT = 3.0                  # tjukn på foten
KANAL = 2.4                  # kanal rundt kvar LED (0603: 0,8 x 1,6)
BLOKK_U = (-11.5, 11.5)      # blokka rundt matrisa, går klar av knapp A og B (innerkant ±16,9)
BLOKK_V = (-10.5, 10.3)      # kort mot logoen (v = 14), der hylsa til messingpunktet står
RINGAR = (-21.59, -11.43, 0.0, 11.43, 21.59)
RING_V = -13.14
FOT_U, FOT_V = (-25.8, 25.8), (-17.89, -8.39)


def lysrist():
    def plate(u, v, t):
        return (cq.Workplane("XY").center((u[0] + u[1]) / 2, (v[0] + v[1]) / 2)
                .rect(u[1] - u[0], v[1] - v[0]).extrude(t).edges("|Z").fillet(1.5))
    d = plate(BLOKK_U, BLOKK_V, T).union(plate(FOT_U, FOT_V, T_FOT))
    led = [((k - 2) * P, (2 - r) * P) for k in range(5) for r in range(5)]
    kanalar = cq.Workplane("XY").pushPoints(led).circle(KANAL / 2).extrude(T)
    d = d.cut(kanalar)
    # M3 med senka hovud frå framsida av foten (flata mot veggen): hol Ø 3,4 og senking til Ø 6,0
    for u in RINGAR:
        d = d.cut(cq.Workplane("XY").center(u, RING_V).circle(1.7).extrude(T_FOT))
        d = d.cut(cq.Workplane("XY").add(cq.Solid.makeCone(1.7, 3.0, 1.3, cq.Vector(u, RING_V, T_FOT - 1.3))))
    return d


if __name__ == "__main__":
    her = Path(__file__).resolve().parent
    d = lysrist()
    cq.exporters.export(d, str(her / "d15_lysrist.step"))
    cq.exporters.export(d, str(her / "d15_lysrist.stl"), tolerance=0.05, angularTolerance=0.2)
    bb = d.val().BoundingBox()
    print(f"D15: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, {d.val().Volume() / 1000:.2f} cm3")
    # kontroll mot kortet: kvar LED ligg fritt i sin kanal, rista går klar av knappane, og skruehola er opne
    for k in range(5):
        for r in range(5):
            l = cq.Workplane("XY").center((k - 2) * P, (2 - r) * P).rect(0.8 + 0.4, 1.6 + 0.4).extrude(0.5)
            assert d.intersect(l).val().Volume() < 1e-6, (k, r)
    for u in (-19.94, 19.94):
        kn = cq.Workplane("XY").center(u, 0.96).rect(6.0 + 0.6, 6.5 + 0.6).extrude(4.55)
        assert d.intersect(kn).val().Volume() < 1e-6, u
    for u in RINGAR:
        hol = cq.Workplane("XY").center(u, RING_V).circle(1.5).extrude(T)
        assert d.intersect(hol).val().Volume() < 1e-6, u
    kort = cq.Workplane("XY").center(0, 1.0).rect(51.6, 42.0).extrude(T)
    assert abs(d.intersect(kort).val().Volume() - d.val().Volume()) < 1e-3, "rista stikk utanfor kortet"
    print("kontroll: 25 LED-ar frie med 0,2 mm slark, knapp A og B frie med 0,3 mm, 5 skruehol opne, rista innanfor kortet")
