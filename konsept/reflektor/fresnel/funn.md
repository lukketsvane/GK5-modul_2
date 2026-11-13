# Fresnel: funn

Familien er fresnelspegelen frå overheadprojektoren (285 × 285 mm, f = 187,1 mm) som stor, flat, retta reflektor. Alle tal er modell (lysskisse.py), 1,25 W i stemning og 5 W i arbeid. Hovudtabellen er `tal.md` (n = 26 fliser), vegen fem steg er nedst i same fil. Søket ligg i `gen1.md` til `gen3.md`, `skann-*.csv`, `avgjerd.md` og `avgjerd-bronn.txt` (n = 16, innanfor 1 % av n = 26).

## 1 Kva eg varierte, og kva som stivna

- **Gen 1 (16 kroppar):** kvar plata og kjelda bur (stav, lene, aksial som Perle, over skjermkanten), kva som rører seg (kjelda blir skoven, plata vippar, plata blir vend), omriss (skive 200 mm, stripe 285 × 100 mm), produktplate (pressa fresnel 150 mm, bøygd parabelrenne). Stivna: jamnheita låg på 0,01 til 0,03 for alle med rein plate. Plata avbildar kjelda, og feltet får ein flekk.
- **Gen 2 (16):** nytt grep, å fylle plata jamt: vid kjelde, kjelda i foten 50 cm under plata, plata som glir i høgda, diffusorark. Stivna: jamnheita kjem berre frå arket, og det same arket lyser opp plata mot auget.
- **Skann (skann.py):** éin parameter om gongen: ark, høgd, sikte, storleik 285 til 70 mm, ansikt.
- **Gen 3 (16):** det som stod att, bygd ut til ulike kroppar: knekt plate, vend, møteplate, høgd, zoom, hol, over skjermen, produktplatene og flatt satinark som samanlikning.
- **Avgjerd (6 + 4, ikkje ein ny generasjon):** tredjeplassen hang på om veggstrøket i arbeid kunne kome utan å halvere feltet. Knekt plate over skjermkanten slo knekt plate på stonga på alle tal, og står no i `tal.md` der kryss-knekk stod. Biletet synte så dioden i over-vipp frå kameraet. Djupare brønn (50 grader) gøymer han og gjev meir på feltet.

## 2 Dei tre beste (tal frå tal.md)

| | over-vipp | kryss-rund | over-knekk |
| --- | --- | --- | --- |
| Felt, lx / jamnheit / W for 350 lx | 867 / 0,46 / 2,02 | 642 / 0,41 / 2,73 | 452 / 0,35 / 3,87 |
| Vegg / ansikt, lx | 31 / 47 | 22 / 45 | 124 / 64 |
| Mot auget, arbeid / ved 350 lx / stemning, cd/m² | 183 / 74 / 165 | 630 / 344 / 90 | 391 / 302 / 106 |
| Stemning vegg, lx / likskap | 82 / 0,09 | 57 / 0,40 | 51 / 0,64 |
| Felt langs vegen, lx | 6 19 183 543 867 | 9 19 94 327 642 | 8 14 52 286 452 |
| Jamnheit langs vegen | 0,52 0,22 0,09 0,26 0,46 | 0,60 0,37 0,13 0,14 0,41 | 0,68 0,51 0,21 0,15 0,35 |
| Mot auget langs vegen, cd/m² | 165 168 82 139 183 | 90 64 38 139 630 | 106 98 75 183 391 |
| Topp / sprang | 0,92 / 0,32 | 0,22 / 0,13 | 0,47 / 0,17 |

- **over-vipp.** Plata heng over skjermkanten (senter 62 cm over bordet, y 0,36), kjelda sit på skjermkanten 120 mm under og lyser opp (vid diode, sigma 40, brønn 64), diffusorark 12 grader. Plata vippar frå veggen 60 cm oppe til feltmidten. Éi setning: den beste lampa i familien, ei plate over skjermen som vippar lyset frå veggen ned på bordet, med lågast luminans mot auget og høgast nytte. Med brønn 50 grader: 1019 lx, jamnheit 0,47, 221 cd/m², og dioden er gøymd frå kameraet òg.
- **kryss-rund.** Plata maskert til skive 285 mm på ei stong 55 cm oppe, kjelda med linse i foten 50 cm under (sigma 12, brønn 40), ark 12 grader. Vippar frå veggen bak skjermen til 4 cm forbi feltmidten. Éi setning: Northern i tre former (fot, stong, skive), med glattaste vegen (sprang 0,13) og ingen synleg kjelde, men 630 cd/m² mot auget.
- **over-knekk.** Same plass som over-vipp, plata delt langs ein diameter: halvdelen mot feltet, ein flik på 100 mm mot veggen 60 cm oppe. Heile plata vippar som éin kropp. Éi setning: den einaste som held F6 i arbeid (124 lx på veggen) utan eige veggstrøk, og betalar med nesten dobbel watt.

## 3 Det som velta, og det som ikkje kan lagast

- **Veltar: projektor.** Projektoren slik han står: 1567 lx, 1,12 W for 350 lx, men plata ligg flatt på bordet (812 cm² mot krav 200 cm²), og det er ikkje ei lampe. Tidlegare veltarar: koffert (22 lx på feltet) og hogd med rein plate (brennpunktet går gjennom bordet, 4255 cd/m² undervegs).
- **Kan ikkje lagast ved bøying: perleskaal.** Holspegel 240 mm, f 260 mm, strekk 2,54 % (grensa er 0,6 %). 917 lx, jamnheit 0,27, 846 cd/m². Ho er ikkje betre enn den flate plata med ark (kryss-ark10: 1171 lx, 0,32, 359 cd/m²).

## 4 Funn som gjeld meir enn denne familien

1. **Å skuve kjelda er ein dimmar, å vippe er ein overgang.** Kjelda skoven 187 til 120 mm under plata (stav-zoom): feltet 163 235 330 453 633 lx, nøyaktig wattrampa (× 3,9 for × 4 W), jamnheit 0,19 til 0,27, mot auget 47 til 193 (gen 3), likskap 0,94. Med rein plate (gen 1, 250 til 120 mm) er likskapen 0,98. Vipp gjev likskap 0,03 til 0,13.
2. **Jamnheit og luminans mot auget er same knapp.** Arket på 8, 12 og 14 grader gjev jamnheit 0,20, 0,42 og 0,48 og 28, 312 og 854 cd/m² mot auget ved 350 lx (skann). 0,6 er ikkje nådd under 1500 cd/m² i denne geometrien. Best er 0,56 ved 1939 cd/m².
3. **Arbeidslys treng ikkje areal, ansiktslys gjer.** Med auget utanfor lobe er lampa berre den diffuse resten (3 %), og luminansen går som 1/areal: 85 cd/m² ved 285 mm til 937 ved 70 mm (5 W, ark 8). Grensa 1500 ligg ved om lag 55 mm ved 5 W og 35 mm ved 350 lx. Ligg auget i lobe (ark 14), er ho over 1500 alt ved 285 mm og 5 W (2004), og ved 350 lx mellom 100 mm (1201) og 70 mm (1688).
4. **50 lx på ansiktet under 1500 cd/m² krev heile plata.** 285 mm og ark 14: 1107 til 1224 cd/m² (kryss-mote 1230 ved 0,3 W). 200 mm: 2018, 150 mm: 3389, 100 mm: 7391. Golvet er L = E / (Ω cos) om lag 580 cd/m² for plata 73 cm frå auget, og modellen ligg om lag dobbelt over fordi plata har ein lys midte.
5. **Rillene er krumminga, men arket et fordelen.** Med ark 12 gjev fresnelplata 1,5 gonger flatt satinark (642 mot 433 lx), utan ark 2,9 gonger (1236) men jamnheit 0,02. Produktet treng ikkje skål: ei pressa flat fresnelplate gjer jobben, og ein ekte holspegel (strekk over 0) vinn ingenting.

## 5 Føreseiingar til skissemodellen (sette 13.11 før måling)

- Over-vipp med ark: lux i 6 × 4 ruter på feltet har min/snitt 0,46 (0,35 til 0,55). Utan ark under 0,05, med ein flekk under 15 cm.
- Zoom: lykta skoven 250 til 120 mm frå plata med same effekt endrar snittet på feltet under 10 %.
- Vipp: i arbeid har feltet minst 15 gonger lux på veggen bak skjermen (modell 28). I stemning har veggen minst 8 gonger lux på feltet (modell 14).
- Over-knekk: vegg delt på felt i arbeid 0,27 (0,2 til 0,35). Flik 60 mm i staden for 100: 0,20.
- Fresnelplata gjev 1,7 lx på feltet per lumen kjelde. Telefonlykta (30 til 60 lm, ANTAKING) gjev 50 til 100 lx midt på feltet.
- Plata mot ansiktet med ark: webkameraet ser ein lys midte, om lag dobbel luminans av snittet over plata.

## 6 Skissemodell på under éin dag (over-vipp og over-knekk)

1. Mål brennvidda: lykta over midten av plata, kort attmed lykta, skarpt bilete ved 374 mm (2f). Aldri sola.
2. Ramme av papp, 300 × 300 mm, plata med rillene opp. Hengsle av teip langs bakkanten.
3. Stolpen med ledd frå projektoren klemt bak skjermen, ramma 20 cm over skjermkanten, 9 cm framfor skjermplanet.
4. Telefonen på skjermkanten med lykta opp, i ein brønn av svart papp (rull 40 mm, 35 mm djup), 12 cm under plata.
5. Diffusorark frå LCD-en teipa på plata. Prøv eitt og to ark.
6. Knekk: ein flik av tynn plate med aluminiumsfolie (eller frontflatespegelen), 285 × 100 mm, hengsla i forkanten av ramma og vinkla mot veggen. Plata skal ikkje klippast.
7. Mål 6 × 4 ruter med luxapp, vegg 30 cm over bordet bak skjermen, og foto frå auget (47 cm) og frå 80 cm. Vipp med éi hand og film vegen.

## 7 Usikkert, og det modellen ikkje reknar

- Spegling av plata i skjermen er ikkje rekna. Over-vipp heng 9 cm framfor skjermkanten og kan synast i skjermen. Det er den største risikoen for dei to beste.
- Dioden på skjermkanten har 7 grader margin til auget. 3 cm skeivt sikte gav 139 000 cd/m² (avgjerd-flytt3.md). Frå 80 cm ser ein han med brønn 64 grader (biletet). Stolpen og plata ved webkameraet er ikkje sjekka mot kamerabiletet.
- Arket er modellert som gauss på 8 til 14 grader, og SATIN og 2 % sprut er antakingar. Fargekantar frå rillene, spreiing i rillekantane og skuggen plata kastar på seg sjølv er ikkje med.
- Motorfeil, meldte og ikkje retta i lysskisse.py: (1) lys som brønnen stoppar, blir rekna som lys ut (lm ut og lysnytte feil, lux rett); (2) to ark på same kjelde: lm_ut blir skriven over av det siste arket (retta for hand i knekk); (3) fresnel saman med form: dei optiske normalane følgjer ikkje bøyen (16 grader bøy flyttar speglinga 1,5 grader i staden for 33). Ei bøygd fresnelplate kan difor ikkje reknast. Sjå motorsjekk.py.
