# -*- coding: utf-8 -*-
"""d15_lysrist.py: lysrista D15 for Sveip mini, som sit mellom micro:bit V2 og framveggen.

Ei svart blokk med 25 kanalar, éin per LED, så kvar LED lyser opp berre sin eigen propp i veggen.
I kvar kanal står ein lysleiar av 1,75 mm naturfarga filament, frå LED-en til framsida av rista.
Nedst har kanalen ei lomme over LED-en. Blokka er 4,8 mm tjukk: knapp A og B (4,55 mm) går klar
av veggen, og rista står 0,3 mm frå han. Foten over ringane er 2,0 mm, for der krummar nasen på
lampa inn mot kortet. Rista blir skrudd gjennom ringane på kortet og inn i stolpen på chassiset
med fem M3 x 8 senkskruar. Over touch-logoen står ei hylse: messingskruen frå utsida skrur seg
inn i ho, og ei lita fjør i lomma under leier berøringa vidare til logoen. Måla er relative til
midtre LED, slik kortet ser ut framanfrå med kantkontakten ned, og er frå monteringsteikninga
for V2.
  python d15_lysrist.py        skriv d15_lysrist.step og d15_lysrist.stl
"""
from pathlib import Path

import cadquery as cq

P = 4.0                      # LED-delinga
T = 4.8                      # tjukn på blokka, frå kretskortet og fram
T_FOT = 2.0                  # tjukn på foten
KANAL = 1.9                  # kanal for lysleiaren (1,75 mm filament)
LOMME = (2.6, 1.1)           # lomme over LED-en: diameter og djupn (0603 ståande, opp til 1,0 høg)
LOGO = (0.0, 14.0)           # touch-logoen (u, v)
HYLSE = 6.5                  # ytre diameter på hylsa over logoen
STOPP = 0.2                  # ringen framme på hylsa går 0,2 nærare veggen enn rista
GJENGE = (2.6, 2.4)          # hol for M3-messingskruen (sjølvgjengande) og kvar det byrjar (w)
FJOR = 4.0                   # lomme for fjøra, frå kortet opp til GJENGE[1]
BLOKK_U = (-11.5, 11.5)      # blokka rundt matrisa, går klar av knapp A og B (innerkant ±16,9)
BLOKK_V = (-10.1, 10.3)      # kort mot logoen (v = 14) for hylsa til messingpunktet, og mot nasen
RINGAR = (-21.59, -11.43, 0.0, 11.43, 21.59)
RING_V = -13.14
FOT_U, FOT_V = (-25.8, 25.8), (-17.89, -8.39)


LED = [((k - 2) * P, (2 - r) * P) for k in range(5) for r in range(5)]


def lysrist():
    def plate(u, v, t):
        return (cq.Workplane("XY").center((u[0] + u[1]) / 2, (v[0] + v[1]) / 2)
                .rect(u[1] - u[0], v[1] - v[0]).extrude(t).edges("|Z").fillet(1.5))
    d = plate(BLOKK_U, BLOKK_V, T).union(plate(FOT_U, FOT_V, T_FOT))
    # hylsa over logoen, bunden til blokka med ein steg
    lu, lv = LOGO
    d = d.union(plate((lu - HYLSE / 2, lu + HYLSE / 2), (BLOKK_V[1] - 2.0, lv), T))
    d = d.union(cq.Workplane("XY").center(lu, lv).circle(HYLSE / 2).extrude(T + STOPP))
    d = d.cut(cq.Workplane("XY").pushPoints(LED).circle(KANAL / 2).extrude(T))
    d = d.cut(cq.Workplane("XY").pushPoints(LED).circle(LOMME[0] / 2).extrude(LOMME[1]))
    d = d.cut(cq.Workplane("XY").center(lu, lv).circle(GJENGE[0] / 2).extrude(T + STOPP))
    d = d.cut(cq.Workplane("XY").center(lu, lv).circle(FJOR / 2).extrude(GJENGE[1]))
    # M3 med senka hovud frå framsida av foten (flata mot veggen): hol Ø 3,4 og senking til Ø 5,4
    for u in RINGAR:
        d = d.cut(cq.Workplane("XY").center(u, RING_V).circle(1.7).extrude(T_FOT))
        d = d.cut(cq.Workplane("XY").add(cq.Solid.makeCone(1.7, 2.7, 1.0, cq.Vector(u, RING_V, T_FOT - 1.0))))
    return d


if __name__ == "__main__":
    her = Path(__file__).resolve().parent
    d = lysrist()
    cq.exporters.export(d, str(her / "d15_lysrist.step"))
    cq.exporters.export(d, str(her / "d15_lysrist.stl"), tolerance=0.05, angularTolerance=0.2)
    bb = d.val().BoundingBox()
    print(f"D15: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, {d.val().Volume() / 1000:.2f} cm3")
    # kontroll mot kortet: kvar LED (0603 ståande, med 0,2 slark og opp til 1,0 høg) ligg fritt i
    # lomma si, rista går klar av knappane og mikrofonen, og skruehola er opne
    for u, v in LED:
        l = cq.Workplane("XY").center(u, v).rect(0.8 + 0.4, 1.6 + 0.4).extrude(1.0)
        assert d.intersect(l).val().Volume() < 1e-6, (u, v)
    mik = cq.Workplane("XY").center(33.95 - 25.8, 31.82 - 20.0).circle(1.5).extrude(1.0)
    assert d.intersect(mik).val().Volume() < 1e-6, "rista dekkjer mikrofonen"
    for u in (-19.94, 19.94):
        kn = cq.Workplane("XY").center(u, 0.96).rect(6.0 + 0.6, 6.5 + 0.6).extrude(4.55)
        assert d.intersect(kn).val().Volume() < 1e-6, u
    for u in RINGAR:
        hol = cq.Workplane("XY").center(u, RING_V).circle(1.5).extrude(T)
        assert d.intersect(hol).val().Volume() < 1e-6, u
    kort = cq.Workplane("XY").center(0, 1.0).rect(51.6, 42.0).extrude(T + STOPP)
    assert abs(d.intersect(kort).val().Volume() - d.val().Volume()) < 1e-3, "rista stikk utanfor kortet"
    print("kontroll: 25 LED-ar frie med 0,2 mm slark, knapp A og B frie med 0,3 mm, mikrofonen fri, "
          "5 skruehol opne, rista innanfor kortet")
