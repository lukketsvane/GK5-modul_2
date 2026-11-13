# Arbeidsnotat: familien overgang

Journal undervegs. Rådata ligg i `journal-gen1.jsonl`, `journal-gen2.jsonl` og `journal-gen3.jsonl` (éi linje per mekanisme, sju steg kvar). Tala er modell, ikkje måling.

## Generasjon 1: mekanismen varierer, oppstillinga er malen

Oppstilling A: foten til høgre for skjermen, kjelda i foten lyser opp på eit ark 41 cm over bordet. `overgang(g, n=7)`.

| Mekanisme | topp | sprang | jamn auke | likskap | mot auget, steg for steg (cd/m²) | skjermlux maks undervegs |
| --- | --- | --- | --- | --- | --- | --- |
| dimmar (referanse) | 0,79 | 0,00 | 1,00 | 1,00 | 244 til 974 | 115 |
| vipp (éin hengsel) | 0,79 | 0,08 | 1,00 | 0,24 | 78, 78, 365, 471, 607, 772, 972 | 517 |
| vend-a (over toppen mot brukaren) | 6,11 | 0,50 | 0,50 | 0,80 | 1381, 37, 42, 36, 195, 8441, 975 | 114 |
| vend-b (andre vegen) | 0,98 | 0,56 | 0,67 | 0,80 | 1381, 1351, 696, 7, 16, 260, 975 | 114 |
| skyv-hol (kjelda langs stamma, hol satin) | 0,61 | 0,01 | 1,00 | 0,98 | 3232, 1978, 1456, 1198, 1061, 991, 965 | 150 |
| skyv-fresnel | 0,78 | 0,00 | 1,00 | 0,99 | 481 til 740 | 83 |
| skyv-bue (kjelda på skinne under boge) | 0,79 | 0,07 | 1,00 | 0,45 | 205 til 2646 | 1797 |
| boy-sym (kuv til hol) | 0,80 | 0,02 | 1,00 | 0,86 | 612, 534, 404, 489, 613, 769, 965 | 153 |
| boy-klemt-hol | 0,83 | 0,15 | 1,00 | 0,21 | 132 til 972 | 946 |
| boy-klemt-kuv | 0,76 | 0,05 | 1,00 | 0,43 | 175 til 972 | 374 |
| drei-to (matt og satinert halvdel) | 1,94 | 0,08 | 1,00 | 0,64 | 3704, 4720, 5981, 7203, 3900, 2111, 2615 | 181 |
| drei-hol (halve skiva klipt bort, lyset i taket) | 0,81 | 0,32 | 1,00 | 0,01 | 7, 55, 545, 1307, 1666, 2111, 2615 | 181 |
| hev (arket langs strålen) | 1,13 | 0,01 | 1,00 | 0,87 | 259, 205, 182, 1105, 1017, 980, 974 | 115 |
| drei-fot (heile lampa 50 grader) | 0,79 | 0,03 | 1,00 | 0,61 | 69 til 974 | 395 |
| flytt (75 grader og 14 cm) | 0,79 | 0,07 | 1,00 | 0,16 | 259, 204, 156, 110, 613, 774, 974 | 211 |
| kryss (to kjelder) | 0,66 | 0,04 | 1,00 | 0,23 | 199 til 974 | 115 |
| fald-ving | 0,79 | 0,03 | 1,00 | 0,74 | 243 til 972 | 453 |
| fresnel-vipp | 0,63 | 0,24 | 1,00 | 0,03 | 255, 257, 205, 113, 232, 466, 740 | 2350 |
| spegel-vipp (frontflatespegelen) | 0,74 | 0,37 | 1,00 | 0,03 | 368 til 824 | 2709 |
| VELT vipp-ansikt | 1,00 | 0,06 | 1,00 | 0,50 | 20771, 20722, 16434, 10016, 4207, 1009, 971 | 116 |
| UMOGLEG skål (strekk 6,5 %) | 0,78 | 0,04 | 1,00 | 0,63 | 6922 til 955 | 202 |

Lesing av settet:

- Det som berre endrar breidda på strålen (skyv, boy-sym, hev), er dimmarar: likskap 0,86 til 0,99.
- Alle verkelege overgangar flyttar lyset frå veggen til feltet. Seks av sju gjer det ved å sveipe strålen 36 grader (vipp, boy-klemt, flytt, fresnel-vipp, spegel-vipp). Settet har stivna rundt sveipet.
- Sveipet går over framsida av skjermen. Motoren måler ikkje det, så eg la til `skjermlux()`: 500 til 2700 lx på skjermflata midt i overgangen, mot 115 lx i arbeid.
- Smal stråle gjev høgt sprang (fresnel 0,24, spegel 0,37), brei stråle lågt (vipp 0,08). Spranget følgjer sveipevinkel per steg delt på strålebreidd.
- Vend er farleg éin veg (8441 cd/m² 30 grader før arbeid) og hakkete begge vegar (sprang 0,5), og mattsida gløder på 1381 cd/m² ved 1,25 W.
- Alle har om lag 32 lx på veggen i arbeid. F6 krev 100 til 150.

Byte av grep til generasjon 2: fordel lyset i staden for å sveipe det. Strålen går til veggen av seg sjølv, og arket skjer ein del av han ned på feltet.

## Generasjon 2: fordele i staden for å sveipe

Oppstilling B: foten står framme til høgre (x 0,62, y 0,22). Kjelda lyser bakover og opp mot veggen 17 cm til høgre for skjermkanten. Arket står i strålen. Det arket fangar, går til feltet, resten held fram til veggen. `ring`, `VELT skjer-matt` og `UMOGLEG skjer-kuppel` vart køyrde ferdig etter avbrotet (13.11 om morgonen).

| Mekanisme | topp | sprang | jamn auke | likskap | W350 | U | vegg i arbeid, lx | mot auget i arbeid | skjermlux maks undervegs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| skjer (arket inn i strålen) | 0,79 | 0,15 | 1,00 | 0,08 | 2,25 | 0,31 | 29 | 1338 | 114 |
| skjer-57 (stoppar når 57 % er fanga) | 0,79 | 0,10 | 1,00 | 0,67 | 3,32 | 0,13 | 128 | 1337 | 51 |
| skjer-slissa (40 % ope) | 0,79 | 0,09 | 1,00 | 0,79 | 3,54 | 0,33 | 145 | 1338 | 78 |
| drei-b (halvskive dreidd i strålen) | 0,80 | 0,30 | 1,00 | 0,09 | 1,94 | 0,29 | 34 | 2319 | 148 |
| drei-snigel (spiralkant) | 0,80 | 0,11 | 1,00 | 0,20 | 2,05 | 0,24 | 55 | 2311 | 132 |
| spjeld (høgkant til arbeidsvinkel) | 0,72 | 0,13 | 1,00 | 0,08 | 2,28 | 0,27 | 28 | 1329 | 568 |
| vipp-b | 0,76 | 0,07 | 1,00 | 0,16 | 2,24 | 0,27 | 28 | 1331 | 595 |
| fresnel-skjer | 1,10 | 0,31 | 1,00 | 0,02 | 1,19 | 0,05 | 26 | 774 | 78 |
| kryss-b (slissa, fast, referanse) | 0,79 | 0,00 | 1,00 | 1,00 | 3,90 | 0,49 | 109 | 1242 | 104 |
| kryss-43 (A, 43 % til vaskaren) | 0,66 | 0,01 | 1,00 | 0,76 | 4,46 | 0,32 | 126 | 555 | 66 |
| fald-opp | 0,80 | 0,03 | 1,00 | 0,77 | 4,11 | 0,17 | 128 | 923 | 448 |
| ring | 0,79 | 0,04 | 1,00 | 0,67 | 3,28 | 0,18 | 122 | 974 | 680 |
| VELT skjer-matt | 0,79 | 0,14 | 1,00 | 0,13 | 8,71 | 0,26 | 34 | 7583 | 147 |
| UMOGLEG skjer-kuppel (strekk 11,6 %) | 0,90 | 0,20 | 1,00 | 0,05 | 2,02 | 0,32 | 23 | 1285 | 341 |

Lesing av settet:

- Å skjere strålen er saumlaust og flyttar ikkje lyset over skjermen: skjermlux held seg under 150 lx heile vegen (vipp-b og spjeld: 570 til 600).
- Settet deler seg i to leirar. Dei med likskap under 0,3 (skjer, drei, spjeld, vipp-b) har 26 til 55 lx på veggen i arbeid. Dei som held F6 (skjer-57, ring, kryss-43, fald-opp: 122 til 128 lx) har likskap 0,67 til 0,77.
- Rekninga bak: veggsona er om lag 1 m², feltet 0,24 m². 100 lx på veggen er om lag 100 lm, 350 lx på feltet om lag 84 lm. Når stemninga bur på veggen nær skjermen, må arbeidet ha minst like mykje lys der, og då blir cosinus 0,6 eller meir. Det er geometri, ikkje mekanisme.
- Open spørsmål som avgjer dei tre beste: kan stemninga bu ein annan stad (tak, høg vegg, bordet) slik at arbeidet kan ha både felt og veggstrøk og likevel likskap under 0,3?
- Settet har stivna rundt adressa «veggen nær skjermen» i stemning. Byte av grep til generasjon 3: flytt adressa til stemninga.

## Generasjon 3: stemninga flyttar adresse

Arbeid er felt + veggstrøk. Stemninga bur i taket, høgt på veggen (over sona, 115 cm over bordet), eller på bordet framfor foten. Nye grep: kryss3 (kryssdimme tre adresser), fald3 (opne ein fald med to vengar, faldlinja parallell med vippeaksen), vipp3 (kontroll), spjeld3 (oppstilling B, dreie arket frå tvers i strålen til arbeidsvinkelen).

Feil undervegs: i første køyring av kryss-* og VELT glod-kryss fanst ikkje arket i stemningssteget (t = 0), berre frå t > 0. Då skugga arket ulikt i ulike steg, og glødeperla bak arket vart borte for auget frå steg 1 (17590 til 29 cd/m²). Retta: arket står der i alle steg, og stemningsstrøket sit på toppen av lampa (57 cm), over arket. Dei gamle linjene ligg i journal-gen3-feil.jsonl. Same feil finst i kryss og kryss-43 frå generasjon 1 og 2 (vaskaren står bak arket og er lite påverka); dei er ikkje køyrde på nytt.

| Mekanisme | topp | sprang | jamn auke | likskap | W350 | vegg i arbeid | stemning: mot auget / vegg | skjermlux maks undervegs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kryss-tak | 0,66 | 0,06 | 1,00 | 0,23 | 4,46 | 126 | 10 / 3 | 66 |
| kryss-tak-30 | 0,66 | 0,06 | 1,00 | 0,22 | 3,70 | 98 | 10 / 3 | 81 |
| kryss-hog | 0,66 | 0,04 | 1,00 | 0,28 | 4,46 | 126 | 148 / 6 | 66 |
| kryss-bord | 0,67 | 0,06 | 1,00 | 0,42 | 4,46 | 126 | 356 / 5 | 66 |
| fald-hog | 0,79 | 0,06 | 1,00 | 0,72 | 4,51 | 148 | 54 / 33 | 619 |
| fald-tak | 0,79 | 0,10 | 1,00 | 0,50 | 4,51 | 148 | 11 / 9 | 702 |
| fald-tak-veng | 0,83 | 0,10 | 1,00 | 0,50 | 6,90 | 186 | 11 / 9 | 573 |
| vipp-tak | 0,78 | 0,29 | 1,00 | 0,19 | 2,64 | 32 | 11 / 8 | 851 |
| spjeld-tak | 5,01 | 0,37 | 0,67 | 0,09 | 2,23 | 28 | 235 / 8 | 119 |
| spjeld-tak-sm | 5,02 | 0,37 | 0,67 | 0,19 | 2,32 | 53 | 235 / 18 | 115 |
| VELT glod-kryss | 1,06 | 0,01 | 1,00 | 0,74 | 4,46 | 126 | 17590 / 22 | 66 |
| UMOGLEG fald-kuppel (strekk 30,5 %) | 0,13 | 0,11 | 1,00 | 0,36 | 7,88 | 154 | 93 / 6 | 1432 |

Lesing av settet:

- Spørsmålet frå generasjon 2 er svart: når stemninga bur i taket eller høgt på veggen, går likskap under 0,3 og 100 lx på veggen i arbeid saman (kryss-tak 0,23 og 126 lx, kryss-hog 0,28 og 126 lx).
- Berre kryssdimminga gjer det utan å sveipe. Alle mekaniske grep som flyttar strålen frå taket eller den høge veggen ned til feltet, må gå gjennom romet imellom: der står skjermen (fald og vipp: 570 til 850 lx på skjermflata midt i overgangen) eller auget (spjeld-tak: 6690 cd/m² ved t = 0,67, topp 5,0).
- Taket som stemning er nesten usynleg frå stolen: 10 cd/m² mot auget og 3 lx på veggsona. Den høge veggen er synleg (148 cd/m²) og gjev same arbeid. Difor er kryss-hog betre stemning enn kryss-tak, med likskap 0,28 mot 0,23.
- Bordet som adresse deler sone med spillet frå arbeidet (bordet utanfor feltet får 14 % i arbeid), så likskapen blir 0,42.
- Kostnaden: W350 4,46 mot 2,25 for skjer. Vaskaren og stemningsstrøket er strøk rett ut (80 lm/W), og vaskaren brukar 43 % av watten på veggen.
- Glødeperla (VELT) syner at topp er relativ: blending i eit endepunkt gjev topp 1,06, ikkje eit varsel. Auget må lesast steg for steg.
