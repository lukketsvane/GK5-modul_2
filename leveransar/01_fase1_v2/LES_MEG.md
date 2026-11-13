# Fase 1-sider, utgåve 2

Sju sider i 1127 x 797 px, same storleik som rammene i klassefila i Figma. Biletet eller figuren først, på svart. Denne utgåva erstattar `leveransar/01_fase1_sider/`, som var tekst og tabellar på kvitt.

Ingenting her er lagt inn i klassefila. Du dreg sjølv bileta i `png/` inn i rammene dine.

| Fil | Innhald | Figur |
| --- | --- | --- |
| side-1-debrief | Debrief, åtte punkt | Same rom i arbeid, i skiftet og i stemning, utan lampe |
| side-2-bransjeresearch | Research i bransjen | Snowball, Luxo L-1 og Litra Glow i same rom, og målet |
| side-3-3b-analyse | Brukar, brukssituasjon, bruksmåte | Døgnlinja med tre rom og det kritiske steget |
| side-4-kravspesifikasjon | Fem kategoriar gonger skal, bør, kan | Krava teikna inn i rommet |
| side-5-berekraftshandling | Handling for berekraft | Lampa i tre lag etter levetid |
| side-6-prosjektplan | Tidsplan, førehandsprøver, risiko | Gantt 12.11 til 7.12 |
| side-7-bedriftsbesok | Bedriftsbesøk, skrivebordsresearch | Tidsline over produkt som er over femti år |

## Lysbileta er modell, ikkje måling

Bileta i `bilete/` kjem frå lysmotoren i `konsept/lysskisse/lysskisse.py`. Same rom, same kamera og same eksponering i alle. Tala under bileta er det modellen reknar.

- `rom-arbeid.png`, `rom-paa-veg.png`, `rom-stemning.png`, `rom-krav.png`: lyset briefen ber om, før lampa finst. Kjeldene står utanfor biletet eller bak skjermen.
- `marknad-*.png`: tre lamper som finst, med lumentalet til produsenten og forenkla form.

## Lage noko på nytt

```
python lys/rom.py overgang 700 2     # dei tre romma (tek fleire minutt)
python lys/rom.py marknad 500 2      # dei tre lampene
python lys/rom.py krav 1120 1        # det store biletet til kravsida
python lys/bygg_side2.py             # researchsida
python lys/bygg_side4.py             # kravsida
python lys/bygg_diagram.py 3 5 6 7   # 3B, berekraft, prosjektplan, bedriftsbesøk
sh lag-png.sh side-3-3b-analyse      # biletet av éi side, 2254 x 1594 px
```

`side-1-debrief.html` er skriven for hand. Rendringa køyrer på lågaste prioritet. Køyr éin om gongen.

Skrift: EB Garamond (i `../01_fase1_sider/fonts/`, OFL-lisens) og Consolas.
