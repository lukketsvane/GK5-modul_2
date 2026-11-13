# gen_d · val

Dato: 13.11.2026. Ingenting er målt. Lys og mekanikk er rekna med `val.py`, og tala ligg i `val_tal.json`, `sok.csv` og `sok2.csv`. Arket er rekna med arbeidsverdiane i `konsept/vindauge/film/arket.md` (H1, 55 %): prisme(90, avrunding 0,03), n_d 1,57, Abbe 30, spreiing 0,3°, haze 0,01. Dei er estimat frå foto, ikkje måling. Kroppen er CAD-en i `konsept/film/cad/lampe.py`, og lyset er lysmotoren i `lys_sjekk.py`. Derfrå kjem tre ANTAKINGAR: 60 % av stripa kjem inn i plata, 30 % går opp gjennom arket, 60 % går ned og 10 % går ut ved den skrå kanten. Merke: **(R)** rekna, **(A)** ANTAKING, **(F)** anslått frå foto. Designaren vel.

## Svar: nei

**Det finst ingen variant av den valde kroppen som får 350 lx inn på feltet utan å velte eller blende.** Grunnlaget er at lampa er rekna slik ho er teikna, i eit søk på 300 variantar og med full rekning for dei som kom nærast (R):

| | Som teikna | Står, nærast | Lyset held | Jamnast | Arket fullt ut |
| --- | --- | --- | --- | --- | --- |
| Aksen, helling, utsving (mm, °, mm) | 260, 35, 70 | 260, 20, 70 | 360, 20, −230 | 460, 0, −230 | 260, 20, 70, rute 440 × 244 |
| Foten (midt, frå midten av skjermen) | x 470, y 300 | x 380, y 300 (tangerer feltet) | x 380, y 300 | x 380, y 300 | x 380, y 300 |
| Feltet ved 2 W (lx) | **56** | 96 | 117 | 78 | 109 |
| W for 350 lx (tak 7,5) | **12,4** | 7,3 | 6,0 | 9,0 | 6,4 |
| U0 på fint gitter (ref. 0,6) | **0,08** | 0,09 | 0,44 | 0,60 | 0,13 |
| Mot auget ved 350 lx, høgaste (F5 1500) | 2171 | 1355 (augevolum 1608) | 1263 | 14 241 | 691 |
| Skjermflata ved 350 lx | 195 | 147 | 334 | 350 | 142 |
| Masse (F8 ≤ 1200 g) | 1182 | 1182 | **1276** | **1320** | **1457** |
| Tipp | 24,6° | 24,3° | **−21,7°, veltar utan dytt** | **−16,5°** | 12,4° |
| Trykk på venstre hjørne som veltar | 6,7 N | 6,7 N | **0** | **0** | **1,9 N** |
| Dytt i toppen som veltar | 3,1 N | 3,1 N | **0** | **0** | **2,0 N** |
| Fot som trengst (Ø, same ballast) | 155 | 157 | **544** | **535** | **283** |
| Ruta i siktlina | 0 % | 7 % | **99 %** | 0 % | 14 % |

- **Lyset og foten dreg kvar sin veg.** 350 lx med U0 over 0,4 krev at ruta heng ut over feltet. Med 1,2 kg på Ø 158 mm har tyngdepunktet 79 mm å gå på, og det er brukt opp. Med utsvinget −80 mm, altså ruta 15 cm lenger mot feltet, er tippvinkelen −0,6°, og lampa veltar utan dytt. Med −230 mm trengst ein fot på Ø 544 mm.
- **Ein høgare akse gjer det verre.** Dytten som veltar lampa, fell frå 3,1 N ved 260 mm til 2,2 N ved 360 mm og 1,7 N ved 460 mm. Massen stig samstundes til 1233 og 1286 g, over F8.
- **I søket held lyset (W ≤ 7,5, U0 ≥ 0,4 og auget ≤ 1500) for éin variant av 300.** Han veltar. Dei 10 som står, har U0 på 0,06 eller lågare.
- **Ei større rute hjelper ikkje.** Arket fullt ut (44 × 24,4 cm) gjev 6,4 W med U0 0,13, men 1457 g, og lampa veltar ved 1,5 N trykk på ruta.
- **Den teikna kroppen held heller ikkje over heile hellinga.** Ved 0 og 10° veltar eit trykk på 4,8 N på eit hjørne av ruta lampa. Ved 50 til 80° er dytten i toppen 2,7 N. Kontrollen i `kontroll.json` (6,7 N og 3,1 N) gjeld berre ved 35°.

Kroppen er altså eit **stemnings- og sidelys**. Det er det (a), (b) og (c) under er: dei beste stemnings- og sidelysvariantane av kroppen Iver valde, ikkje arbeidslys. Arbeidslyset (F3) krev D-kroppen, som står lenger nede: bjelke over skjermkanten, 2 til 4 kg og ein fot som bryt F9.

## (a), (b), (c): stemnings- og sidelys

Alle tre har same kropp. Han er som teikna, med to endringar: aksen ligg 40 mm lågare (`AKSE_H` 220) og armen svingar 8 mm meir ut (`ARM_UT` 78). Då held kroppen over heile hellinga, frå 0 til 80° (R). Trykket på venstre hjørne som veltar lampa, er minst 7,3 N (i dag 6,7 N). Dytten i toppen er minst 3,04 N, mot 3,1 N i dag ved 35° og 2,7 N ved 80°. Trykket på eit hjørne av ruta er minst 5,06 N, og tippvinkelen minst 25,7°. Lampa veg 1164 g (F8 held) og har ein fot på 196 cm² (F9 held). Rutemålet 300 × 190 mm går inn i arket (25 × 44 cm). Vindauget for utsvinget er smalt: 77 til 79 mm. Utanfor det fell anten trykket ved 0° eller dytten ved 80° under kravet.

Handlinga er hellinga. Ruta ligg låg i sidelys og står nesten loddrett i stemning, med dimmaren på leidningen. Stripa er éin kanal på 2700 K, så fargetemperaturen er den same i begge tilstandane.

| | (a) Ved feltkanten | (b) Langs feltkanten | (c) Bak skjermen |
| --- | --- | --- | --- |
| Foten (midt, frå midten av skjermen) | x 380, y 300 mm, tangerer feltet | x 400, y 200 mm, dreidd −90°: bjelken langs feltkanten, ruta peikar inn | x 200, y 610 mm, mellom skjermen og veggen |
| Helling: sidelys / stemning | 20° / 80° | 0° / 80° | 60° / 80° |
| **Sidelys: lm · W · K · lx · U0** | *120 lm · 2,0 W · 2700 K · 103 lx · U0 0,07* | *120 lm · 2,0 W · 2700 K · 91 lx · U0 0,10* | *120 lm · 2,0 W · 2700 K · 14 lx · U0 0,68* |
| Lyspølen under ruta, snitt / høgst | 163 / 413 lx | 157 / 336 lx | 70 / 443 lx (bak skjermen) |
| Kva 350 lx på feltet ville kravd | 6,8 W, U0 0,07 | 7,7 W, U0 0,10 | 48 W |
| Skjermflata | 30 lx | 32 lx | 1 lx |
| Mot auget 25 / 47 / 60 cm | 167 / 343 / 367 cd/m² | 508 / 212 / 42 cd/m² | 408 / 0 / 0 cd/m² |
| Augevolumet, høgaste | 427 cd/m² | 508 cd/m² | 436 cd/m² |
| Spegling i blank skjerm, tilta 0 til 20° | **29 cd/m²** (skjermen 40) | **24 cd/m²** | 0 |
| Veggen bak skjermen | 8 lx | 9 lx | **87 lx** |
| Ansiktet (F10 50 til 200) | 18 lx | 11 lx | 3 lx |
| **Stemning: lm · W · K** | *75 lm · 1,25 W · 2700 K* | *75 lm · 1,25 W · 2700 K* | *75 lm · 1,25 W · 2700 K* |
| Stemning: veggen bak skjermen / feltet | 13 / 31 lx | 5 / 17 lx | **70** / 17 lx |
| Stemning: mot auget (krav 500) | 244 cd/m² | 101 cd/m² | 270 cd/m² |
| Likskap mellom stemning og sidelys (over 0,9 er ein dimmar) | 0,81 | 0,85 | **0,98** |
| Masse / fot | 1164 g / Ø 158, 196 cm² | same | same |
| Tipp, sidelys / stemning | 26,8° / 26,3° | 25,7° / 26,3° | 27,5° / 26,3° |
| Trykk på venstre hjørne som veltar (i dag 6,7 N) | 7,3 N | 7,3 N | 7,3 N |
| Dytt i toppen som veltar (i dag 3,1 N) | 3,4 / 3,0 N | 3,4 / 3,0 N | 3,3 / 3,0 N |
| Trykk ned på eit hjørne av ruta som veltar | 5,3 / 7,0 N | 5,1 / 7,0 N | 6,9 / 7,0 N |
| Svikt under 5 N: knotten / framkanten | 0,6 / 10,9 mm | 0,6 / 11,7 mm | 0,6 / 5,7 mm |
| Moment i friksjonsleddet frå 5 N på framkanten | 0,91 N·m | 0,97 N·m | 0,48 N·m |
| Ruta i siktlina | 3 % | 1 % | 0 |
| Arket | eitt stykke, 30 × 18,4 cm | same | same |
| Lysstudie | `studie_a.png` | `studie_b.png` | `studie_c.png` |

Lysstudiane har same kamera og eksponering for arbeid og stemning (ls.KAM og ls.framkall, L0 70 cd/m²). Dei viser isolux på bord og vegg og lysfordelinga i snitt i cd/klm. Dei er rendra med lysmotoren og ikkje med Blender.

**(a) Ved feltkanten.** Dette er kroppen Iver valde, med foten flytt 9 cm inn til han tangerer feltet. Han gjev mest lys på feltet av dei tre (103 lx ved 2 W, mot 56 som teikna) og ein pøl på 163 lx i hjørnet til høgre for tastaturet. Auget får 367 cd/m², så han blendar ikkje. I stemning står ruta opp som eit lysande vindauge (`studie_a.png`, til høgre). Det er Telt-gesten, men på bordet: veggen bak skjermen får berre 13 lx. Svakheita er speglinga. Ruta lyser 29 cd/m² i ein blank skjerm, og skjermen sjølv er 40. På ein matt skjerm er det om lag ein tidel av dette (A).

**(b) Langs feltkanten.** Lampa er dreidd 90°. Bjelken går framover langs høgre kant av feltet, og ruta ligg flat inn over feltet. Ruta står nesten ikkje i siktlina (1 %), og ho speglar seg minst av (a) og (b). Lyset på feltet er 91 lx. Mot eit auge 25 cm over bordet lyser ruta 508 cd/m², fordi auget då ser rett inn i prismesida. I stemning er ho den mildaste (101 cd/m² mot auget), men ho lyser nesten ikkje opp veggen (5 lx).

**(c) Bak skjermen.** Foten står mellom skjermen og veggen, og ruta lyser på veggen bak og ved sida av skjermen. Ruta er skjult frå auget i 47 og 60 cm. Ho gjev 87 lx på veggen bak skjermen ved 2 W og 70 lx i stemning, og ingenting på skjermflata. Ved 2,5 W er det nok til F6 (100 til 150 lx) åleine. På feltet gjev ho nesten ingenting (14 lx), og likskapen er 0,98, så handlinga er berre ein dimmar. Ho er eit bakgrunns- og stemningslys, ikkje eit sidelys. Under 60° kolliderer ruta med skjermen. Ved 0 til 35° gjekk ho 18 til 25 mm inn i skjermen i sok2.csv (aksen 260).

## Mot A, B, C og D

A til D er frå `konsept/film/02-D-ruta.md` (grovt gitter, ideelt prisme). D-framlegga er rekna på fint gitter med arket. For (a), (b) og (c) er «ved 350 lx» skalert med watten, slik at kolonnane kan samanliknast. Ingen av dei er laga for 350 lx.

| | W for 350 lx | U0 | Mot auget ved 350 lx, høgaste | Veggen bak skjermen ved 350 lx | Skjermflata ved 350 lx | Ansiktet ved 350 lx | Stemning: veggen | Stemning: auget | Likskap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A Skiva | 2,99 | 0,62 | 1013 | 109 | 115 | 29 | 131 | 424 | 0,60 |
| B Over | 3,56 | 0,41 | 1124 | 114 | 60 | 43 | 108 | 110 | 0,71 |
| C Vindauge | 5,78 | 0,62 | 155 | 127 | 39 | 25 | 72 | 76 | 0,54 |
| D Ruta | 3,69 | 0,62 | 1040 | 142 | 188 | 35 | 189 | 242 | 0,42 |
| D-a, D med Ø240 (arket, fint) | 3,80 | 0,53 | 1169 (augevolum 2071) | 129 | 202 | 40 | 144 | 211 | 0,42 |
| D-b, plata under skjermen (arket, fint) | 4,05 | 0,54 | 792 (2269) | 136 | 195 | 39 | 143 | 244 | 0,43 |
| D-c, vassrette riller (arket, fint) | 3,45 | 0,60 | **1693** (2055) | 124 | 143 | **144** | 145 | 244 | 0,43 |
| (a) Ved feltkanten | **6,8** | **0,07** | 1248 (1452) | 26 | 101 | 60 | 13 | 244 | 0,81 |
| (b) Langs feltkanten | **7,7** | **0,10** | **1956** (1956) | 34 | 124 | 44 | 5 | 101 | 0,85 |
| (c) Bak skjermen | **48** | 0,68 | 9850 | 2100 | 34 | 75 | 70 | 270 | 0,98 |

Stemninga i A til D er 1,25 W med 2200 K. I (a), (b) og (c) er ho 1,25 W med 2700 K, fordi stripa har éin kanal.

## D-framlegga: arbeidslyset, med arket

Framlegga i `val_forslag.md` er arbeidslys med ein annan kropp enn den Iver valde. Bjelken står over skjermkanten, 50 cm over bordet. Dei er rekna om her med arket og på fint gitter, med celler på 4 cm, augevolum og spegling i ein skjerm tilta 0 til 20° (R).

| | D-a, D med Ø240 | D-b, plata under skjermen | D-c, vassrette riller |
| --- | --- | --- | --- |
| lm · W · K · lx · U0 (fint, arket) | *380 lm · 3,80 W · 3000 K · 350 lx · U0 0,53* | *405 lm · 4,05 W · 3000 K · 350 lx · U0 0,54* | *345 lm · 3,45 W · 3000 K · 350 lx · U0 0,60* |
| Same med ideelt prisme | 3,69 W · U0 0,51 | 3,94 W · U0 0,52 | 3,31 W · U0 0,58 |
| Mot auget 25 / 47 / 60 cm, arket (ideelt) | 1169 / 213 / 243 (1012 / 140 / 140) | 792 / 145 / 433 (877 / 141 / 141) | 563 / **1693** / 1407 (658 / 1822 / 1314) |
| Augevolumet, arket (ideelt) | **2071** (2067) | **2269** (2246) | **2055** (2158) |
| Spegling i blank skjerm, arket (ideelt) | **26** (19) cd/m² | **28** (20) | **70** (69) |
| Veggen bak skjermen, fint | 129 lx | 136 lx | 124 lx |
| Skjermflata, fint | 202 lx | 195 lx | 143 lx |
| Ansiktet (F10) | 40 lx | 39 lx | **144 lx** |
| Stemning: veggen, fint / auget | 144 lx / 211 cd/m² | 143 / 244 | 145 / 244 |
| Masse (F8 1,2 kg) | **3,76 kg** | **2,08 kg** + skjermen (A) | **4,29 kg** |
| Fot (F9 200 cm²) | **Ø 240, 452 cm²** | plate 30 × 23 cm under skjermfoten | **Ø 260, 531 cm²** |
| Tipp / dytt på knotten som veltar | 34° / 5,5 N | 12,7° / 5,0 N | 33° / 5,6 N |
| Svikt i knotten / framkanten under 5 N | 0,14 / 1,07 mm | 0,22 / 1,27 mm | 0,15 / 1,17 mm |
| Rute og ark | 45 × 19, rillene langs dei 19 cm: **treng eit større ark** (45 > 44 cm på tvers av rillene) | 52 × 16: **treng eit større ark** | 36 × 24, rillene langs dei 36 cm: **treng eit større ark** (36 > 25 cm langs rillene), eller ei skøyt |

**Skilnaden mellom arket og ideelt prisme** (R, same køyring, same foton for vindaugsdioden): Watten stig 3 til 4 % (3,80 mot 3,69, 4,05 mot 3,94 og 3,45 mot 3,31). U0 stig 0,02. Speglinga stig 40 % i D-a og D-b (26 mot 19 og 28 mot 20 cd/m²), og dei går over grensa på 20 cd/m². Ruta lyser meir mot eit auge rett framfor: 1169 mot 1012 cd/m² i 25 cm (D-a) og 433 mot 141 i 60 cm (D-b). Avrundinga på prismetoppane og hazen slepper lys gjennom der det ideelle prismet stengjer. Augevolumet flyttar seg under 5 %. I CAD-kroppen flyttar arket nesten ingenting (feltet 103 mot 103 lx, auget 367 mot 384 cd/m²), fordi berre 30 % av lyset går gjennom arket og resten går ned gjennom plata utan film.

Ingen av D-framlegga held både F5 i augevolumet (2055 til 2269 cd/m², når auget bøyer seg ned og ser opp i ruta), F8 og F9. D-b er nærast, men berre om skjermen er ballast (A).

## Seksten kroppar, eller éin med seksten justeringar?

**Éin kropp.** Talet som avgjer, er ikkje nabo-IoU, men kor mange kroppar som står.

- **gen_d (brettet):** nabo-IoU er 0,19 i snitt og 0,43 på det høgste. Konvolutten vandrar, så silhuettane er ulike. Men topologien er lik i alle 16: fot eller plate, arm, bjelke og rute. Det som skil, er kvar foten står (tre grupper) og kvar armen møter bjelken. Rillene og hellinga, som flyttar lyset mest, syner ikkje i silhuetten. Det er tre familiar med justeringar.
- **CAD-kroppen:** av 300 variantar står 10, og alle har utsvinget 70 og aksen på 260. Vindauget som held over heile hellinga, er 77 til 79 mm i utsving ved aksen 220. Det er ±1 mm, 0,3 % av ruta. Silhuett-IoU (R, `val.py iou`) mellom den teikna og ARM_UT 78 er 0,92 framfrå og 1,00 frå sida. Det er over 0,9 og les ikkje. Aksen 40 mm lågare gjev 0,54 og 0,48. Det les, for det er 15 % av høgda.
- **(a), (b) og (c) er same kropp,** med like parametrar i lampe.py. Dei skil seg berre i plassering og helling. Handlinga sjølv, frå 20 til 80°, endrar silhuetten meir (IoU 0,50 framfrå) enn nokon parameter som held.

Settet har stivna. Etter skillen er det på tide å byte motor eller grep, ikkje å justere vidare. Arbeidslyset finst berre i ein annan topologi, der ruta heng over skjermkanten og noko anna enn ein fot på 1,2 kg ber henne, til dømes skjermen eller plata under han (D-b).

## Nøkkel til val_maal.json

`val_maal.json` brukar namna og einingane i `lampe.py`: RUTE_B, RUTE_D, VINKEL, AKSE_H, BJELKE_D, FOT_D, ARM_B, ARM_T, ARM_UT og KNOTT_D, i mm og grader. Kvart mål har ei kjelde: rekna (val.py), anslått (uendra frå lampe.py, der fleire er kontrollmål frå foto) eller D. Plasseringa og stemningshellinga er ikkje parametrar i lampe.py. Dei står for seg under `plassering` og `handling`.

- (a): `RUTA_AKSE_H=220 RUTA_ARM_UT=78 RUTA_VINKEL=20 RUTA_UT=ut-a`
- (b): `RUTA_AKSE_H=220 RUTA_ARM_UT=78 RUTA_VINKEL=0 RUTA_UT=ut-b`
- (c): `RUTA_AKSE_H=220 RUTA_ARM_UT=78 RUTA_VINKEL=60 RUTA_UT=ut-c`

Kroppen er den same i alle tre. Det einaste som skil filene, er hellinga i teikninga.

## Uvisse og det som ikkje er rekna

- **Ingenting er målt.** Arket er H1 i arket.md (55 %). H2 (toppvinkel 94°, avrunding 0,1) er ikkje rekna. Prøvene P1 og P2 avgjer det.
- **Lyset i CAD-kroppen kviler på antakingane i lys_sjekk.py:** 100 lm/W, 60 % inn i plata og fordelinga 30/60/10. Kalibreringa er rekna: utan kroppen sine eigne skuggar gjev val.py 190 / 436 lx under ruta, feltet 56 lx og auget 386 cd/m², mot 190 / 436, 57 og 372 i 00-ruta-pa-fot.md. Med skuggen frå foten, armen og bjelken er pølen 134 lx. Det er dette talet som gjeld i tabellane.
- **Massen er modellert frå delane i kontroll.json**, skalert med måla: 1182 mot 1184 g, og tyngdepunktet ligg innanfor 1 mm. Velteformlane gjev 6,7 / 10,7 / 3,1 N, det same som kontroll.json. `lampe.py kontroll` er ikkje køyrd for (a), (b) og (c), fordi han skriv i konsept/film/cad. New session bør køyre han.
- **Svikta i framkanten er dominert av plata** (8,4 av 10,9 mm i (a)). Det byggjer på tre ANTAKINGAR: PMMA 3 mm med E 3 GPa, ei berande breidd lik djupna, og ingen glid i leddet. Friksjonsleddet må halde 0,9 N·m. Det er ikkje rekna.
- **Søket rekna berre direkte lys.** Avgjerda er rekna med sprett, og watten flytta seg under 1 % mellom dei to.
- **I D-framlegga er auget i 47 og 60 cm fotonrekna** (vindauget på veggen) og flyttar seg 10 til 25 % mellom køyringar.
- **Plasseringane i (b) og (c) og stemningshellinga er ikkje parametrar i lampe.py.** Foten i (c) står 1 mm frå skjermfoten. Skjermfoten er ANTAKING (24 × 20 cm).
- **Speglinga er rekna for ein blank skjerm** (0,04).

## Feila i denne økta

1. **Rutenettet under ruta var spegla.** Første kalibrering gav 151 lx under ruta mot 190 i lys_sjekk, fordi nettet låg 40 cm feil veg langs y. Etter rettinga gav nettet 134 lx. Skilnaden mot 190 var skuggen frå kroppen, som lys_sjekk ikkje har med. Utan kroppen gjev val.py 190 / 436, nøyaktig som lys_sjekk. Kalibreringa er køyrd på nytt.
2. **Stabilitetskravet felte den teikna kroppen.** Kravet var dytt ≥ 3,1 N, og den teikna kroppen har 3,08. Difor vart alle 300 i sok.csv flagga «veltar». Kolonnane `stab_ok` og `flagg` i sok.csv har framleis 3,1 N. Tala i val.md er lesne med 3,0 N («ikkje svakare enn i dag»), og kravet i val.py er no 3,0 N.
3. **Kroppen held ikkje over heile hellinga.** Første (a), (b) og (c) var den teikna kroppen. Han feilar ved 0 og 10° (trykk 4,8 N) og ved 50 til 80° (dytt 2,7 N). Difor har (a), (b) og (c) aksen på 220 og utsvinget 78.
4. **Søket tok 313 s,** nær grensa på 6 minutt. Søket på stemning og sidelys (sok2) vart difor gjort mindre: 150 variantar.
