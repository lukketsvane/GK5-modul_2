# Runde 3: fem lamper med synleg opal kjelde

Dato: 19.11.2026. Laga i ei skyøkt, skorne i motoren til slicerman utan nettlesar. Iver: berre BLAD i stemning er rett retning estetisk. Runde 4 byggjer vidare på den. Alle seks kroppane: `ALT OK`, krav 12 av 12 i full bygging.

## Grepet

Same oppskrift som bordkula di: ei opal lyskjelde som er synleg, bjørk 4 mm rundt, éin messingdetalj. Skulpturforma er skjermen. Kvar lampe har éi handling som flyttar lyset, og stillinga kan lesast av forma.

- **Stemning:** du ser den opale kjelda.
- **Arbeid:** forma skjuler kjelda for deg, lyset går på bord og vegg.

Kjeldene er standardpærer eigaren byter utan verktøy: G95 E27 (HATT, KOVE, HETTE), opal rørpære Ø30 (PILLE), G45 E14 (BLAD).

## Dei fem

| Nr | Namn | Form | Handling | Plater | Ark 600 x 400 | Bjørk | Mål (mm) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | HATT | skulptur-07 | vipp hatten på kula | 15 i hatten + 4 i foten | 2 + 1 | 0,40 kg | Ø300 x 174 |
| 2 | KOVE | skulptur-09 | drei 180 | 6 ribber + 3 tverrplater | 2 | 0,46 kg | 135 x 194 x 260 |
| 3 | HETTE | skulptur-03 | drei 180 | 11 bogar + 2 ryggar | 2 | 0,32 kg | 205 x 303 x 190 |
| 4 | PILLE | skulptur-12 | sving belgen om foten | 11 bogar + 2 ryggar | 1 | 0,18 kg | 336 x 144 x 175 |
| 5 | BLAD | skulptur-10 | vipp bladet på lykta | 4 i lykta + opalblad | 1 | 0,06 kg | blad 252 x 341, høgd 137 |

1. **HATT.** Foten ber sokkelen, kula står på foten, hatten kviler på kula. Kula er leddet: hatten har eit kulesete (r 48,5) og vippar fram og attende. Flat er stemning og lesepøl, kanten ned mot deg skjuler kula (`ark-skjerm`), kanten opp gjev lys mot ansiktet (`ark-mote`).
2. **KOVE.** Kula sit i fanget på seks L-ribber. Ryggplata er reflektor når kova vender mot deg og skjerm når ryggen vender mot deg.
3. **HETTE.** Kula heng frå eit skott inne i ein ribbekvelv. Opninga mot deg viser kula. Dreidd skjuler skottet kula, og bogane kastar skuggar på veggen.
4. **PILLE.** Ein open belg av bogar med ein opal lysstav under ryggen. Belgen er open ned frå foten og ut til spissen.
5. **BLAD.** Ei lita lykt med fire rammer rundt ei kule, og eit bøygd opalblad (R 271) som kviler på toppen. Kanten mot deg ned gjev ei stor, mjuk flate mot ansiktet (652 cm²).

## Filer

- `oversyn.png`: éi rad per lampe. Stemning i dagslys og mørke, så den andre stillinga.
- `profilar.png`: dei fem i sideriss.
- `palett.png`: dei fem i Northern-fargar (mørkegrøn, svart, gråbeige, kvit, svart).
- I kvar mappe: `ark-<stilling>.png`, `prosjekt-<namn>.zip` (opne i appen: kroppsnamn, `fil`), `skjerefiler/fin/` (DXF og SVG som skal skjerast), `montering.txt`, `deler.csv`, `passprove.svg`, og `kjelde/`.
- HATT har to kroppar og difor to prosjektfiler og to sett skjerefiler. Arka for HATT er sette saman av dei to scenene.
- `ekstra-lysstav` (PILLE) og `ekstra-blad` (BLAD) er opalarka.

## Endra i formene

- **07:** delt i fot og hatt ved z = 56. Hatten er lyfta 53 mm og har fått kulesete.
- **09:** nettet tetta, sporet i foten fylt att, tappen under kappa, lomme til sokkelen.
- **03:** dreidd 17,7 grader så hovudaksen ligg rett. Foten er hola ut til 16 mm skal bak eit skott, open bak.
- **12:** belgen hola ut til 11 mm skal og opna under. Leidningen er fjerna.
- **10:** foten er det konvekse skalet av foten i forma, med kulerom. Bladet har éi krumming i staden for sadelflata.
- Alle kroppane er glatta (voksel 0,8 til 1,2 mm) før skjering.

## Ikkje prøvd

- Ingenting er skore. Snittbreidd 0,2 mm og klaring 0,1 mm er gjettingar til passprøva er skoren.
- Lux og blending er ikkje rekna. Lysbileta viser berre direkte lys.
- Pære, sokkel, leidning og messing er teikna, ikkje konstruerte. Feste for sokkel og opalark er ikkje løyst.
- **Velting, rekna frå platene pluss pære og sokkel:** HETTE har tyngdepunktet 28 mm framfor fremste støpunkt og treng om lag 0,4 kg ballast bak i foten. PILLE har tyngdepunktet 26 mm utanfor foten og treng om lag 0,7 kg ballast i foten eller ei fotplate. KOVE står. HATT og BLAD står i ro, men er topptunge.
- At hatten held seg vippa på kula er rekna grovt frå friksjon (μ over 0,22 held 22 grader), ikkje prøvd.
- E27 er 230 V. Det høver i mockupen. Eit Northern-produkt ville hatt LED-modul i opalglas.
- Prosjektfilene er ikkje opna i appen. Motoren sin eigen prøve «appen opnar posen uendra» gjekk gjennom.

## Kjelde

`kjelde/kropp.py` lagar glatte kroppar med holrom frå GLB. `gitter2.ts` er `gitter.ts` frå skillen med frie normalar, faste platestader, ekstraark og dreidd rom. `saman.py` set fleire skorne kroppar saman i éi scene. Stiane er frå maskina koden køyrde på. Kroppane (`lampe.stl`) ligg ikkje i repoet: lag dei med `python kropp.py <design>/kjelde/kropp.json`. Foten og bladet til BLAD kjem frå `5-blad/kjelde/fot.py`.
