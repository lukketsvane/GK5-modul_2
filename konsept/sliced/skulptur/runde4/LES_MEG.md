# Runde 4: BLAD-retninga

Dato: 19.11.2026. Same motor og verkty som runde 3. Etter runde 3 sa Iver at berre BLAD i stemning er rett retning estetisk. Desse fem held seg til den oppskrifta. Alle fem: `ALT OK`, krav 12 av 12 i full bygging.

## Oppskrifta frå BLAD

- Eitt tynt opalark (3 mm), bøygd éin veg. Arket er skjermen og lysflata.
- Ein liten bjørkekropp (4 mm): fire eller fem delar, eitt ark 600 x 400.
- Ei lita opal kjelde, synleg frå éi side og skjult frå den andre.
- Éin messingdetalj og éi handling.

## Dei fem

| Nr | Namn | Form | Opalark (mm) | Handling | Bjørk | Mål (mm) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | SEGL | skulptur-10 | 181 x 234, R 44 | snu lampa | 4 delar, 3,02 m kutt, 0,060 kg | Ø91 x 252 |
| 2 | SKIVE | skulptur-07 | Ø300, R 420 | vipp skiva på kula | 4 delar, 1,57 m kutt, 0,048 kg | Ø300 x 162 |
| 3 | LE | skulptur-09 | 279 x 135, R 240 | snu lampa | 4 delar, 4,70 m kutt, 0,142 kg | 135 x 195 x 268 |
| 4 | KVELV | skulptur-12 | 188 x 336, R 84 | sving kvelven om foten | 5 delar, 4,92 m kutt, 0,110 kg | 151 x 336 x 181 |
| 5 | NEBB | skulptur-06 | Ø227, R 200 | snu lampa | 4 delar, 4,32 m kutt, 0,141 kg | 215 x 285 x 340 |

1. **SEGL.** Same lykt som BLAD, men bladet står: opalarket går 236 grader rundt lykta, og toppkanten stig frå 132 til 252 mm. Opninga mot deg viser kula (stemning). Snudd er arket ei lysande flate mot deg, og lyset klatrar opp kurva (arbeid).
2. **SKIVE.** Foten og G95-kula frå HATT, men hatten er éi opalskive med hol som kviler på kula. Kula er leddet: flat (stemning), 20 grader ned mot deg (`ark-skjerm`), 20 grader opp mot deg (`ark-mote`).
3. **LE.** To vinklar og to tverrplater. Opalarket går frå tåa til toppen av ryggen, og kula (G45) stikk så vidt gjennom eit rundt hol i arket. Snudd ser du kula gjennom rammene (`ark-kveld`). Messingknappen i tåa er dimmaren.
4. **KVELV.** Berre hovudet over foten er bjørk. Belgen er eitt opalark over ein opal lysstav (Ø30). Kvelven langs veggen er stemning. Svinga 90 grader om foten ligg han ut over bordet (arbeid).
5. **NEBB.** To sider med nebb held eit rundt opalblad i 20 grader: hakk i nebbet, spor i bladet. Messingfatninga står gjennom bladet og kula (G45) heng under. Leidningen går skjult mellom sidene. Bladet mot deg er arbeidslys med kula skjult bak bladkanten. Lampa snudd viser kula og vaskar veggen (stemning).

## Filer

- `oversyn.png`: BLAD frå runde 3 øvst, så dei fem. Dagslys, mørke, og den andre stillinga i mørke.
- I kvar mappe: `ark-<stilling>.png`, `prosjekt-<namn>.zip` (opne i appen: kroppsnamn, `fil`), `skjerefiler/fin/` (DXF og SVG som skal skjerast), `montering.txt`, `deler.csv`, `passprove.svg`, `rapport.txt` og `kjelde/`.
- `skjerefiler/ekstra-*.dxf` er opalarka, flate før bøying. `ekstra-lysstav` (KVELV) er røyret bretta ut; kjøp eit opalrør i staden.

## Endra i formene

- **10 (SEGL):** lykta er foten frå BLAD. Arket følgjer ikkje bladet i forma. Det er henta frå referansebiletet: eit opalark som sveiper opp rundt ein sylinder.
- **07 (SKIVE):** foten frå HATT (forma under z = 56). Skiva har omrisset til hatten sett ovanfrå.
- **09 (LE):** nettet tetta som i KOVE. Ryggen er hola ut til 13 mm skal, med sokkellomme og leidningskanal bak. Arket ligg der den hole framsida av kova var, som «Le» i `astra/fire-design.md`.
- **12 (KVELV):** kroppen frå PILLE, kappa 22 mm framfor foten. Resten av belgen er arket.
- **06 (NEBB):** sideprofilen er snittet x = 0 gjennom stilken i forma, glatta, med tå og hovud med nebb lagt til. Skåla er bytt mot eitt bøygd blad med same breidd og helling. Klokka under skåla er borte. Kroppen er bygd frå polygon (`form.py`), ikkje frå nettet.

## Ikkje prøvd

- Ingenting er skore eller bøygd. Snittbreidd 0,2 mm og klaring 0,1 mm er gjettingar til passprøva er skoren.
- Alle opalarka må varmebøyast over ein mal. Malane er ikkje laga. R 44 (SEGL) og R 84 (KVELV) er trange for 3 mm akryl.
- Feste for arket er berre løyst i NEBB (hakk 3,4 mm i nebbet, spor 4,3 mm i bladet) og SKIVE (hol Ø30 på kula). I SEGL, LE og KVELV ligg arket inntil kroppen utan teikna feste.
- Lux og blending er ikkje rekna. Lysbileta viser berre direkte lys.
- **Velting, rekna frå delane:** KVELV har tyngdepunktet framfor foten og treng om lag 0,5 kg ballast i foten eller ei fotplate. NEBB har tyngdepunktet 1 mm frå midten av ein 214 mm lang fot og står. SEGL (arket 21 mm frå aksen, fot ±39) og LE (fot 130 x 194) står.
- SKIVE: skiva (250 g) kviler på pæra. Ho held 20 grader vipp om friksjonen er over 0,32 (rekna grovt). Ein silikonring i holet er tryggast.
- NEBB: fatning med skjermringar gjennom eit hol Ø28,6 er standardvare, men fatning og pære (om lag 60 g) heng i eit 3 mm ark 75 mm frå nebbet. Nedbøying er ikkje rekna.
- Pære, sokkel, leidning og messing er teikna, ikkje konstruerte. E14 og E27 er 230 V, som i runde 3.
- Prosjektfilene er ikkje opna i appen.

## Kjelde

`kjelde/gitter2.ts` og `kjelde/kropp.py` er nyare enn i runde 3 (hol i bøygde ark, kropp frå vokselfil). SEGL les `../blad/lampe.stl` og SKIVE les `../hatt/fot/lampe.stl` frå runde 3. NEBB: `python kropp.py heil.json`, `python form.py`, `python kropp.py kropp.json`. Stiane er frå maskina koden køyrde på. Kroppane (`lampe.stl`) ligg ikkje i repoet.
