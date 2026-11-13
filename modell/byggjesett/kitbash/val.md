# Kitbash generasjon 1: valet

Dato: 13.11.2026. Tala er modell (lysmotoren, skalert til 350 lx på feltet) og mekanikk frå CAD-en. Ingenting er bygt eller målt. Alle tala står i `tal.md`, feila i `logg.md`.

## Svaret frå søket

Lyset bur over skjermkanten. LED-stripa på skjermkanten lyser opp i den reine fresnelplata, som legg eit band av lys over feltet. Ei diode bak ei maske teiknar vindauget på veggen, og knotten flyttar watten mellom dei. Av seksten kroppar er dette den einaste som held alle lyskrava i lysmotoren. A, B, C og D gjer det heller ikkje.

Etterprøvinga med uavhengig kode (`etterproving.py`) held funnet, men ikkje talet: jamnheita er 0,59 i ruter på 10 cm, mot 0,70 i lysmotoren, og 0,30 i ruter på 5 cm, fordi dei fremste 5 cm av feltet er svake. Med plata sikta 3 cm nærare brukaren blir det 0,61 og 0,48. Les 0,70 som «på referansen», ikkje som trygt over.

Valet som står att, er kven som ber plata og stripa: skjermen, bordet eller foten.

## (a), (b) og (c)

| | (a) Klype · band | (b) Under · band | (c) Fot · knekk |
| --- | --- | --- | --- |
| Kropp | 4: på skjermkanten | 19: same lys, på ei stålplate under skjermfoten | 10: plata på fot med flik, til høgre for skjermen |
| Arbeid: lm · W · K · lx · U0 | 290 lm · 2,9 W · 3000 K · 350 lx · 0,70 | som (a) | 280 lm · 2,8 W · 3000 K · 350 lx · 0,29 |
| Veggen bak skjermen (F6: 100 til 150 lx) | 132 lx | 132 lx | 123 lx |
| Mot auget, verste augehøgd (F5: 1500 cd/m²) | 317 | 317 | 660 |
| Skjermflata, del av feltet | 0,18 | 0,18 | 0,22 |
| Stemning: veggen bak / mot auget (krav 500) | 143 lx / 334 | som (a) | 83 lx / 92 |
| Overgangen: likskap / sprang | 0,44 / 0,07 | som (a) | 0,74 / 0,16 |
| Timar per celle ved 350 lx | 5,2 | 5,2 | 5,3 |
| Masse (F8: 1200 g) | 1143 g, alt på skjermen | 2260 g | 1293 g |
| Bordflate (F9: 200 cm²) | 0 | 690 cm², under skjermen | 196 cm² |
| Dytt / trykk i handtaket (mål 3 og 5 N) | klemd på skjermen | 7,0 / 86,9 N | 1,9 / 6,2 N |
| Handtaket | knotten på bjelken, 65 cm | knotten på bjelken, 65 cm | framkanten av plata, 54 cm |
| Frå settet | plata, armen, hengselet, bjelken med stripa | som (a) | plata, armen, hengselet, glaslinsa, foten |
| Må skaffast | klype, bøyel, vindaugsdiode, knott, LED-stripe, to kanalar | som (a), pluss stålplate 300 × 230 × 2 og røyr | bøyel, blank flik, diode, linsehaldar |
| Fell på | lasta på skjermen | F8, og plata tek 690 cm² under skjermen | jamnheita, F8 med 93 g, dytt |

**(a) Klype · band.** Held alle lyskrava, og bordet er fritt. Kostnaden er 1143 g på overkanten av skjermen. Tyngdepunktet ligg 6 mm framfor midten av skjermkanten, så lampa balanserer, men om skjermen toler vekta, er ikkje kjent. Armen og hengselet frå projektoren er 421 g av dette. Ei trykt klype med to stenger gjev same lys med om lag 0,7 kg.

**(b) Under · band.** Same lys, og lampa står sjølv: ho toler 7 N dytt. Kostnaden er ei stålplate på 1,1 kg under skjermfoten og 2,3 kg i alt, så ho kan ikkje flyttast med éi hand (F8).

**(c) Fot · knekk.** Gesten frå den valde kroppen, ei skrå rute på fot, med fresnelplata som spegelrute og kjelda i foten. Ho held veggen (123 lx) og vekta nesten, men feltet blir ujamt (0,29) fordi lyset kjem inn frå sida, og ho veltar ved 1,9 N. LED-stripa hjelper ikkje her: 42 cm under plata blir stripa avbilda som ei line (jamnheit 0,02).

Vegg · band (kropp 20, same lys på ein konsoll frå veggen) er ikkje med i valet. Ho kan ikkje flyttast.

## Rådet mitt

(a), men med ei lettare klype enn armen frå projektoren. Lyset er det same i (a) og (b), så valet mellom dei er mekanisk og kan vente til skjermen er prøvd med vekt på kanten. (c) er verd å byggje berre om gesten på fot veg tyngre enn jamnheita.

Prøv bandet før noko blir bygt. Det er éin dag med papp, og det avgjer om (a) og (b) finst.

## Bandprøva: føreseiingar sette 13.11, før måling

Bygg B Over-modellen (plata i ei pappramme 20 cm over skjermkanten og 9 cm framfor skjermplanet, sjå `konsept/tre/00-tre-konsept.md`). Byt telefonlykta med ei LED-stripe i ei renne av svart papp på skjermkanten, 12 cm under plata. Ingen diffusorark. Stripa er den same som står på handlelista til ruta på fot (COB, 5 V). Mål lux i 6 × 4 ruter på feltet.

1. Stripa 24 cm, rein plate: lågaste rute delt på snittet mellom 0,55 og 0,70 i ruter på 10 cm (lysmotoren 0,69, uavhengig kode 0,59). Den svakaste ruta ligg i framkanten av feltet.
2. Same stripe dekt til 12 cm: under 0,4 (lysmotoren 0,34, uavhengig kode 0,15).
3. Stripa flytta til 42 cm under plata: ei lys line på bordet, under 0,1 (begge kodane 0,00 til 0,02).
4. Frå stolen, med auget 25 til 60 cm over bordet, er plata mørk: ingen lys flate i henne.
5. Snittet på feltet er 1,7 til 2,0 lx per lumen frå stripa.
6. Vippar du plata så midten av lyset flyttar seg 3 cm mot deg, blir framkanten jamnare (uavhengig kode: 0,61, og 0,48 i ruter på 5 cm).

Held ikkje 1 og 4, fell (a) og (b), og B Over med flik og diffusorark er att (3,6 W, jamnheit 0,41).

## Tryggleik

Fresnelplata samlar sollys 19 cm framfor seg. Ei lampe med plata over skjermen ved eit vindauge må tole det. Det gjeld produktet, ikkje berre skissemodellen. Basen P04 og pæra P09 er ikkje med i nokon kropp.
