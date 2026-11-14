# Ruta på fot, revisjon C: klar for print og butikk

Dato: 14.11.2026. Revisjon B var eit formstudium: eitt bøygd stålrøyr, innpressmutterar og ein brems som ikkje var teikna. Revisjon C er same lampe, teikna slik at ho kan lagast med ein 3D-printar, ei baufil og delar som står i hylla i Oslo sentrum. CAD-en er `ruta_c.py`, alt under `ut-c/` blir laga på nytt med `python ruta_c.py`. Monteringa står i heftet `rettleiing-c/ut/rettleiing.pdf`.

![Framsida på heftet](rettleiing-c/ut/sider/side-01.png)

## Kva som er endra frå B, og kvifor

| Revisjon B | Revisjon C | Grunn |
| --- | --- | --- |
| Eitt stålrøyr Ø 12 × 1,5 bøygd 120° | To rette koparrøyr Ø 12 i eit trykt bogestykke (12) med 25 mm muffer | Ingen røyrbøyar. Røyret kan kappast med baufil |
| Innpressmutterar M3 og M4 | Skruane formar gjenga sjølve i trykte hol Ø 2,5, med 8 mm inngrep | Ingen loddebolt, ingen spesialdelar |
| Lokskruar M3 × 12, som ikkje nådde mutterane | M3 × 20 (E) | Feil i B, funnen då C vart teikna |
| Stoppskrue gjennom hol i røyret | Krage på bogestykket som går i ei C-forma lomme i bjelken, og ein låseskrue i eit spor | Ingen boring i røyret. Stoppen ved 0° og 80° sit i plasten |
| Bremsen ikkje teikna | Skrue (G) som trykkjer ein trykt sko (13) mot akselrøyret | Friksjonen kan stillast, og skruen gneg ikkje på røyret |
| Rund stålplate Ø 106 × 5, skoren | 33 stålskiver M16 i 11 stablar på pinnar i foten | Skivene finst i pose. Plata måtte ha vore skoren hjå ein verkstad |
| Bjelke og lok i eitt stykke på 328 mm | Begge delte i to, med skøytane forskyvde 66 mm | Printaren tek 256 mm. Loket bind bjelkeskøyten, bjelken bind lokskøyten |
| USB-stripe med touch-dimmar | COB-stripe 24 V med adapter og brytar på leidningen | Varm kvit USB-stripe og dimmar fanst ikkje i sentrum |
| Settskrue mot røyret i foten | Røyret er limt i ein sokkel med blindboring | Epoksy tek moment betre enn éin skrue mot tynn røyrvegg |

Formtrekka H1 til H6 frå `01-northern-tilpassing.md` står. Bogestykket har same diameter heile vegen og les som ein del av lina. Skruane sit under og bak.

## Tala

| | Revisjon B | Revisjon C | Krav |
| --- | --- | --- | --- |
| Masse | 1104 g | 1103 g | høgst 1200 g |
| Fotavtrykk | 196 cm² | 196 cm² | høgst 200 cm² |
| Tyngdepunkt frå midten av foten | 6 mm | 10 mm | |
| Trykk ned på venstre hjørne av ruta som veltar lampa | 7,7 N | 6,8 N | |
| Trykk ned på fremste kant | 12,0 N | 11,1 N | |
| Dytt sidelengs i toppen | 3,0 N | 2,8 N | |
| Veltevinkel | | 28,3° | |
| Kollisjonar, helling 0° til 80° | ingen | ingen | |

Veltetala er litt lågare enn i B fordi C reknar med at lampa står på knottane 75 mm frå midten, ikkje på ytterkanten av foten.

Styrke, rekna med den krafta som veltar lampa (3455 Nmm ved bogestykket):

| Del | Spenning | Grense | Tryggleik |
| --- | --- | --- | --- |
| Bogestykke, PETG | 6,2 MPa | 40 MPa | 6,5 |
| Koparrøyr Ø 12 × 1 | 39 MPa | 150 MPa | 3,8 |
| Flatetrykk i muffa | 2,1 MPa | 40 MPa | 19 |
| Stoppflata ved 1 Nm på ruta | 5,0 MPa | 40 MPa | 8 |
| Gjenga til bremseskruen | 120 N | 944 N | 7,8 |

Akselrøyret bøyer seg 0,34 mm under eigenvekta av ruta. Lampa veltar altså lenge før noko ryk.

## Trykte delar

PETG, dyse 0,4 mm, lag 0,2 mm, fire vegger, fem lag topp og botn, 25 % gyroid om ikkje anna står. Filene ligg i `ut-c/stl/` og er lagde i printstilling.

| Fil | Mål i mm | Stilling og oppsett |
| --- | --- | --- |
| `01_fot.stl` | 158 × 158 × 16 | Toppflata ned, utan støtte |
| `02_botnlok.stl` | 145 × 145 × 4 | Flatt |
| `05_bjelke_venstre.stl` | 36 × 36 × 131 | Ståande med skøyten ned, 5 mm brem |
| `05_bjelke_hogre.stl` | 36 × 36 × 197 | Ståande med skøyten ned, 5 mm brem |
| `06_lok_venstre.stl` | 194 × 17 × 16 | Klemflata ned |
| `06_lok_hogre.stl` | 118 × 17 × 16 | Klemflata ned |
| `11_endelok.stl` | 20 × 20 × 4 | Flatt |
| `12_bogestykke.stl` | 75 × 80 × 18 | Liggjande, 100 % fyll, støtte under |
| `13_bremsesko.stl` | 10 × 8 × 3 | 100 % fyll |

Alt får plass på 256 mm. Passingane er 0,30 mm der det skal limast og 0,40 mm der noko skal gli.

### Prøvebitar først

Fire små bitar på til saman under ein time fortel om passingane held på akkurat denne printaren og dette røyret. Print dei før dei store delane.

| Fil | Prøver |
| --- | --- |
| `prove_muffe.stl` | Røyret skal gå inn med handmakt, utan slark |
| `prove_krageende.stl` | Røyret skal dreie lett i boringa |
| `prove_bjelkesnitt.stl` og `prove_loksnitt.stl` | Rute og ark skal klemmast når skruen er stramma. M3 skal forme gjenge utan at bossen sprekk |

Glepp noko, så endre `PASS_LIM`, `PASS_GLID` eller `ROYR_D` øvst i `ruta_c.py` og køyr på nytt.

## Handleliste

Alt er frå Clas Ohlson. Prisane er frå nettsida 14.11.2026. Lagerstatus i kvar butikk er ikkje sjekka.

| Vare | Art.nr. | Pris | Bruk |
| --- | --- | --- | --- |
| Koparrøyr Ø 12 mm × 2 m, forkroma | 30-6571 | 199,90 | 04 (242 mm) og 09 (308 mm) |
| Skruesett M3 med M3 × 10 og M3 × 20 | 40-7042 | 219,90 | 6 E, 3 F, 1 G |
| Skiver M16, Ø 30, 25 stk, to pakkar | 11-1203-16 | 99,80 | 33 skiver som ballast |
| COB LED-stripe 24 V, 3000 K, med adapter og brytar | 36-8960 | 349,90 | 30 cm klipt av, leidningen blir brukt |
| Loctite Power Epoxy 5 min, 25 ml | 34-8919 | 149,90 | Røyr i muffer og sokkel, bjelkeskøyten |
| Wago 221, to leiarar | 36-6520 | 139,90 | Skøyten i foten |
| Antisklknottar Ø 8, 28 stk | 21-2865 | 39,90 | 16 under foten |
| **Sum** | | **1199,20** | |

Til lakk kjem Paintguide grunning 41-3362, Paintguide matt svart 41-3355 eller Vintage Sand 41-3348, og gull metallic 41-3354 til endeloket. Lysleiaren (07) og prismearket (08) kjem frå den gamle skjermen. Akrylplate 300 × 200 × 3 (34-1360, 99,90) er reserve om lysleiaren ryk.

Verktøy om det manglar: baufil 40-8088, filsett 40-7692, sandpapir 41-3859 og 41-3860, stjernetrekkjar eller flat trekkjar til M3, vater.

## Lakk

Lampa blir trykt i den fargen som ligg i printaren, og sprøytt i éin matt farge. Det er det H4 krev, og det gøymer laglinene og skøytane.

1. Lim stativet (fot, stamme, bogestykke, akselrøyr) og bjelken først. Lakk før lys, rute og lok kjem i.
2. Slip plasten lett med korn 240. Slip krommen på stammerøyret matt, elles slepper lakken.
3. Teip det som skal passe: akselrøyret (09), boringa og kragelomma i bjelken, spalta til ruta og LED-kanalen. Lakken byggjer 0,05 til 0,1 mm og et opp klaringa på 0,40 mm.
4. To tynne strok grunning, så to til tre tynne strok farge. Loka (06) blir lakka for seg, med klemflata ned.
5. Endeloket (11) får messingfarge. Det er messingpunktet frå H5.
6. Lat lakken herde eit døgn før montering. Sprøyt ute eller med god lufting, og hald boksen over 15 °C.

Prøv grunning og lakk på ein av prøvebitane først. Heft på PETG er ikkje prøvd.

## Det som er uvisst eller ikkje gjort

- **Ingenting er trykt eller montert.** Kontrollen er digital: masse, velt, kollisjon, stopp og styrke i `ut-c/kontroll.json`.
- **Røyrveggen** er rekna til om lag 1,0 mm ut frå vekta på pakken. Mål ytterdiameteren med skyvelære før print.
- **Skivene** er rekna til 2,7 mm og 10 g ut frå vekta på pakken. DIN 125 seier 3 mm nominelt. Mål éin stabel på tre før foten blir trykt, og rett `SKIVE_T`.
- **Veggen bak kragelomma** i høgre ende av bjelken er 1,3 mm på det tynnaste. Han ber ikkje last, men kan bli synleg i printen.
- **Lyset** er ei 24 V-stripe med brytar, utan dimming. 30 cm gjev om lag 0,7 til 0,8 W etter databladet. Lysstyrken i ruta er ikkje rekna eller målt.
- **Slicing** er ikkje gjort. Printoppsettet over er eit framlegg.
- **Skjermdelane** (07 og 08) er føresette å vere 300 × 190 mm. Lysleiaren treng fem hol Ø 4 etter `ut-c/geometri.json`.

## Filene

| | |
| --- | --- |
| `ruta_c.py` | Parametrisk CAD, kontroll og eksport |
| `ut-c/stl/` | Printfiler og prøvebitar |
| `ut-c/ruta-pa-fot-rev-c.step`, `ut-c/step/` | Samanstilling og einskilddelar |
| `ut-c/kontroll.json`, `ut-c/geometri.json` | Tal og mål |
| `rettleiing-c/` | Monteringshefte i IKEA-stil, 18 sider |
