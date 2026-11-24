# Lut · konsept D

Bordlampe. Eit skrått blad står på ein flat fot og ber eit sylindrisk hovud som lyser ned på foten og bordet. Knotten står i lyset under hovudet: av, på og dimming.

Mappa går frå skissa til ferdig CAD-samanstilling, slica printplater og monteringsrettleiing. Alt blir laga på nytt frå skripta.

![Lut frå framme til høgre](render/02_tre_kvart.png)

## Mål

| | mm | Grunnlag |
| --- | --- | --- |
| Heile lampa | 244,5 × 80 × 274 | |
| Fot | 195 × 80 × 32 (skal 30 + føter 2) | lengd og høgd målt, djupn vald |
| Blad | 40 tjukt; bakkant 29,4°, innerkant 8,7° frå loddrett | vinklane målt, tjukkleiken vald |
| Hovud | Ø 80 × 80, aksen 204,5 frå venstre ende | målt |
| Avrunding øvst | R 40, same som hovudradien | målt R 39,8 |
| Knott | Ø 20 × 17,2, i senter av den runde enden av foten | målt Ø 20,0 og 1,7 mm lenger til venstre |
| Masse | om lag 940 g med stålplate, 570 g med PLA-plate | rekna frå CAD og slicer |

Skissa har ingen målestokk. Eg valde 0,5 mm per pikselpunkt, slik at hovudet blir Ø 80 og knotten Ø 20. Då får kvar del plass på P1S-plata.

Opprisset er målt i skissa (`referanse/maaling.json`) og samsvarer 96 % med henne over foten (`kontroll/overlegg.png`). Under foten avvik det berre fordi skissa har perspektiv.

Djupna syner ikkje i skissa, så tre mål er valde etter ein regel. Foten er 80 djup, like djup som hovudet er breitt. Bladet er 40 tjukt, lik radien til hovudet. Venstre ende av foten er rett og nett så brei som bladet, med R 20 i hjørna. Skissa tillèt ein bladtjukkleik mellom 28 og 64 mm alt etter kva perspektivteikn ein les.

## Delar

| ID | Del | Tal | Materiale | Kjelde |
| --- | --- | --- | --- | --- |
| D01 | Blad med kabelkanal | 1 | PLA matt grå | print |
| D02 | Hovud med magnetring | 1 | PLA matt grå | print |
| D03 | Fot (skal) | 1 | PLA matt grå | print |
| D04 | Botnplate, ballast | 1 | stål S235 4 mm, laserskoren frå DXF (alternativ: PLA og stål limt inn) | laser / print |
| D05 | Knott | 1 | PLA matt grå | print |
| D06 | Lyskopp | 1 | PETG kvit | print |
| D07 | Spreiar Ø 71 | 1 | opal PC 1 mm eller eit LCD-diffusorark | skjer ut |
| D08 | Kjøleplate Ø 54 × 1,5 | 1 | aluminium (valfri) | skjer ut |
| E01 | LED-modul Ø 50, 5 V, ≤ 2 W, 2700 K, CRI ≥ 90 | 1 | | kjøp |
| E02 | Potensiometer med brytar, WH148 16 mm, M7-hals, riflet aksel Ø 6 | 1 | | kjøp |
| E03 | PWM-dimmarkort 5–24 V (potensiometeret lodda på) | 1 | | kjøp |
| E04 | USB-C-hokontakt, 5 V, med 5,1 kΩ CC-motstandar | 1 | | kjøp |
| E05 | Kabel 2 × 0,25 mm², 450 mm | 1 | | kjøp |
| M01–M07 | 3 + 6 innpressmutrar, 3 + 2 + 4 skruar, 6 magnetar Ø 6 × 3, 4 gummiføter | | | kjøp |

Heile lista med mengder og masse ligg i `kontroll/lut_stykkliste.csv`. Lampa går på 5 V frå ein vanleg USB-C-ladar. Det er ingen nettspenning inne i ho.

## Print

Bambu Lab P1S, 0,4 mm dyse, Textured PEI. Slica med Bambu Studio-CLI og systemprofilane (`print/slice_lut.py`, resultat i `print/slicing.json`). Ingen del treng støtte. Sliceren gav ingen åtvaringar.

| Plate | Innhald | Filament | Profil | Tid | Gram |
| --- | --- | --- | --- | --- | --- |
| 0 | Passprøve | PLA Matte | 0,20 Standard | 0 t 30 | 22 |
| 1 | D01 Blad, liggjande | PLA Matte | 0,20 Standard, 3 vegger, 15 % gyroid, stryking | 6 t 22 | 229 |
| 2 | D03 Fot, D02 Hovud, D05 Knott, alle opp-ned | PLA Matte | 0,16 Optimal, 6 vegger | 3 t 38 | 176 |
| 3 | D06 Lyskopp, opp-ned | PETG HF kvit | 0,16 Optimal | 0 t 36 | 19 |
| 4 | D04 i PLA, berre om du ikkje har stålplata | PLA Matte | 0,20, 100 % | 0 t 59 | 73 |

Print plate 0 først. Prøv dei kjøpte delane i ho:
- dei to innpressmutrane (M4 og M3) og magneten, som skal setjast inn utan å sprekke veggen;
- potensiometeret, som skal gå gjennom holet på Ø 7,3;
- knottstubben, som skal pressast fast på akselen;
- den smale ringen, som skal gli inn i den breie med litt luft.

Om noko er for trongt eller for laust, rett målet øvst i `cad/lut.py` og køyr skripta på nytt. Prøv deretter plate 1 til 3.

Framsida av bladet ligg mot plata og får teksturen frå henne. Baksida blir stroken toppflate. Vil du ha like flater, slip og lakker bladet.

## Montering

`montering/Lut-montering.pdf` har elleve sider med strekteikningar rett frå CAD-en, med same ID-ar som her. Stega er desse:
1. Smelt inn innpressmutrane.
2. Trekk kabelen gjennom bladet, og skru hovudet på frå innsida.
3. Set potensiometeret og USB-C-kontakten i foten.
4. Skru bladet fast frå undersida av foten.
5. Kople, og prøv lyset før foten blir lukka.
6. Set saman lyskoppen. Han klikkar på plass i hovudet med magnetar.
7. Skru botnplata på, lim på føtene og press på knotten.

## Status

| Kontroll | Resultat | Korleis |
| --- | --- | --- |
| Gyldige solidar | alle 32 delar, beslag og kjøpte delar | OCC `isValid` |
| Kollisjonar | 0 av alle par | boolsk snitt, terskel 0,01 mm³ |
| Monteringsvegar | fri for lyskopp, hovud på blad, knott og botnplate | diskret, steg på 1 mm |
| Velting | 23,8° framover og bakover, 42° mot hovudet (stål); 15,3° med PLA-plate | statisk, om ytterkanten av føtene; EN 60598-1 krev 6° |
| Print | alle delar passar P1S; 5 plater slica utan åtvaringar | Bambu Studio-CLI; verktøybanene er ikkje sette gjennom i programmet |
| Fysisk prøve | ikkje gjort | print plate 0 først |
| Varme | ikkje prøvd | mål LED-kortet etter 60 min på full styrke: over 60 °C krev svakare LED |
| Kjøpte delar | nominelle mål, ikkje målte | mål potensiometer, dimmar og USB-C med skyvelære før plate 2 |

## Serieproduksjon

Geometrien held òg for serie. Då blir blad og hovud éin pressstøypt aluminiumsdel utan skøyt, og foten blir støypt i sink, så stålplata fell bort. Knotten blir dreidd i aluminium, og alt blir pulverlakkert i same grå. Delinga i printutgåva (hovudet skrudd på bladet, botnplate i stål) er der for at P1S skal klare delane utan støtte.

## Filer

| Mappe | Innhald |
| --- | --- |
| `cad/` | `lut.py` (kjelda, alle mål som parametrar øvst), STEP per del og `lut_samanstilling.step` med fargar |
| `produksjon/` | STL per del i monteringsposisjon, `D04_botnplate_4mm_S235_1til1.dxf` for laser, `P00_passprove.stl` |
| `print/` | printplatene som 3MF (geometri) og `.gcode.3mf` (slica), `slice_lut.py`, `slicing.json` |
| `kontroll/` | `lut_kontroll.json`, `lut_stykkliste.csv`, `overlegg.py` og `overlegg.png` |
| `render/` | rendringar i Cycles frå CAD-nettet, `render_lut.py` |
| `montering/` | `Lut-montering.pdf`, sidene som PNG, `lag_rettleiing.py` |
| `referanse/` | `maaling.json`. Sjølve skissa ligg berre lokalt til opphavet er avklara, fordi repoet er offentleg. |

Køyr frå denne mappa:

```
py -3 cad/lut.py
py -3 print/slice_lut.py
py -3 kontroll/overlegg.py
blender -b -P render/render_lut.py -- oppriss tre_kvart venstre bak sprengt ovanfra
py -3 montering/lag_rettleiing.py
```
