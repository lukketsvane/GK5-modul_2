# Ruta på fot, revisjon C: klar for print og butikk

Dato: 14.11.2026. Revisjon B var eit formstudium: eitt bøygd stålrøyr, innpressmutterar og ein brems som ikkje var teikna. Revisjon C er same lampe, teikna slik at ho kan lagast med ein 3D-printar, ei baufil og delar som står i hylla i Oslo sentrum. CAD-en er `ruta_c.py`, alt under `ut-c/` blir laga på nytt med `python ruta_c.py`. Monteringa står i heftet `rettleiing-c/ut/rettleiing.pdf`.

![Framsida på heftet](rettleiing-c/ut/sider/side-01.png)

## Kva som er endra frå B, og kvifor

| Revisjon B | Revisjon C | Grunn |
| --- | --- | --- |
| Eitt stålrøyr Ø 12 × 1,5 bøygd 120° | To rette koparrøyr Ø 12 i eit trykt bogestykke (12) med 25 mm muffer | Ingen røyrbøyar. Røyret kan kappast med baufil |
| Innpressmutterar M3 og M4 | Skruane formar gjenga sjølve i trykte hol Ø 2,5, med 8 mm inngrep | Ingen spesialdelar |
| Lokskruar M3 × 12, som ikkje nådde mutterane | M3 × 19 (E) | Feil i B, funnen då C vart teikna |
| Stoppskrue gjennom hol i røyret | Krage på bogestykket som går i ei C-forma lomme i bjelken, og ein låseskrue i eit spor | Ingen boring i røyret. Stoppen ved 0° og 80° sit i plasten |
| Bremsen ikkje teikna | Skrue (G, M3 × 12 kappa til 8 mm) som trykkjer ein trykt sko (13) mot akselrøyret | Friksjonen kan stillast, og skruen gneg ikkje på røyret |
| Rund stålplate Ø 106 × 5, skoren | 24 stålskiver M16 i åtte stablar på tappar i foten. Foten har elleve tappar | Skivene finst i pose. Plata måtte ha vore skoren hjå ein verkstad |
| Bjelke og lok i eitt stykke på 328 mm | Begge delte i to, med skøytane forskyvde 66 mm | Printaren tek 256 mm. Loket bind bjelkeskøyten, bjelken bind lokskøyten |
| USB-stripe med touch-dimmar | USB-stripe 5 V RGB, åtte diodar, kopla til fast kvitt | Budsjettet. Varm kvit USB-stripe fanst ikkje i sentrum |
| Settskrue mot røyret i foten | Røyret er limt i ein sokkel med blindboring, med ein trykt fotring (14) rundt | Epoksy tek moment betre enn éin skrue mot tynn røyrvegg. Ringen aukar innfestinga frå 8 til 24 mm og set hellinga på 30° |
| Bjelkehalvdelane møtest butt | To filamentbitar som styrepinnar i skøyten | Halvdelane kan ikkje vri seg mot kvarandre medan limet herdar |

Formtrekka H1 til H6 frå `01-northern-tilpassing.md` står. Bogestykket har same diameter heile vegen og les som ein del av lina. Skruane sit under og bak.

## Tala

| | Revisjon C | Krav |
| --- | --- | --- |
| Masse i CAD | 1014 g | høgst 1200 g |
| Fotavtrykk | 196 cm² | høgst 200 cm² |
| Tyngdepunkt frå midten av foten | 8 mm | |
| Kollisjonar, helling 0° til 80° | ingen | |
| Stopp ved 0° og 80°, låseskruen held | ja | |
| Leidning Ø 4 fri ut av foten | ja | |

Massen er rekna med 55 % fylt PETG i snitt og 24 skiver. Med printoppsettet under blir lampa om lag 1060 g.

Kor lite som skal til for å velte lampa, rekna over alle velteretningar:

| Helling på ruta | Trykk ned på venstre hjørne | Trykk ned midt på fremste kant | Dytt sidelengs i toppen | Veltevinkel |
| --- | --- | --- | --- | --- |
| 0° | 3,5 N | 6,0 N | 2,5 N | 23,6° |
| 35° | 4,3 N | 9,5 N | 2,7 N | 27,1° |
| 80° | 6,3 N | | 2,5 N | 27,9° |

3,5 N er om lag 360 gram på hjørnet av ruta. Det er lite, og det følgjer av krava: 1,2 kg og ein fot på 200 cm² under ei rute som stikk 19 cm ut. Med 33 skiver var talet 3,8 N. Dei tre tomme tappane står nærast venstre framkant; alt tungt som blir lagt på dei, hjelper. Tala i `01-northern-tilpassing.md` (7,7 og 12,0 N for revisjon B) er rekna med ein enklare formel som berre såg på éi retning, og er like mykje for høge.

Styrke, rekna med 8 N på hjørnet, det doble av det som veltar lampa:

| Del | Last | Grense | Tryggleik |
| --- | --- | --- | --- |
| Bogestykke, PETG, bøying | 6,2 MPa | 40 MPa | 6,5 |
| Koparrøyr Ø 12 × 1, bøying | 39 MPa | 150 MPa | 3,8 |
| Flatetrykk i muffene i bogestykket | 2,1 MPa | 40 MPa | 19 |
| Kanttrykk der stamma står i foten, med fotring | 2,7 MPa | 40 MPa | 15 |
| Stoppflata ved 1 Nm på ruta | 5,0 MPa | 40 MPa | 8 |
| Gjenga til bremseskruen | 169 N | 647 N | 3,8 |

Utan fotringen ville kanttrykket i foten vore 22 MPa. Bremsa må halde 252 Nmm når ruta ligg flatt, og er rekna for det doble. Skoen kan gå 0,9 mm mot røyret, og 0,25 mm trengst. Akselrøyret bøyer seg 0,34 mm under eigenvekta av ruta.

## Trykte delar

PETG, dyse 0,4 mm, lag 0,2 mm, fire vegger, fem lag topp og botn, 25 % gyroid om ikkje anna står. Filene ligg i `ut-c/stl/` og er lagde i printstilling.

| Fil | Mål i mm | Stilling og oppsett |
| --- | --- | --- |
| `01_fot.stl` | 158 × 158 × 16 | Toppflata ned, utan støtte, fem vegger |
| `02_botnlok.stl` | 145 × 145 × 4 | Den flate undersida ned. Støtte berre frå plata, eller reinsk dei tre forsenkingane med eit 6,5 mm bor |
| `05_bjelke_venstre.stl` | 36 × 36 × 131 | Ståande på enden med skøyten opp. Støtte berre i endeloklomma, 5 mm brem |
| `05_bjelke_hogre.stl` | 36 × 36 × 197 | Ståande på enden med skøyten opp. Støtte berre i kragerommet, 5 mm brem |
| `06_lok_venstre.stl` | 194 × 17 × 16 | Klemflata ned, støtte frå plata under leppa |
| `06_lok_hogre.stl` | 118 × 17 × 16 | Klemflata ned, støtte frå plata under leppa |
| `11_endelok.stl` | 20 × 20 × 4 | Flatt |
| `12_bogestykke.stl` | 75 × 80 × 18 | Liggjande, 100 % fyll, støtte berre frå plata, 5 mm brem |
| `13_bremsesko.stl` | 10 × 8 × 3 | 100 % fyll |
| `14_fotring.stl` | 18 × 18 × 17 | Ståande på den rette enden, 100 % fyll |

Alt får plass på 256 mm. Passingane er 0,30 mm der det skal limast og 0,40 mm der noko skal gli. Den avrunda toppkanten på foten ligg mot plata og blir litt ujamn i dei første laga. Slip han før lakk.

### Prøvebitar først

Seks små bitar fortel om passingane held på akkurat denne printaren og dette røyret. Print dei før dei store delane.

| Fil | Prøver |
| --- | --- |
| `prove_muffe.stl` | Røyret skal gå inn med handmakt i det eine holet og gli i det andre. M3 skal forme gjenge i det minste |
| `prove_krage.stl` | Limmuffa slik ho blir trykt i bogestykket, liggjande, med krage og låsespor |
| `prove_krageende.stl` | Kragen frå `prove_krage` skal dreie fritt i enden av bjelken |
| `prove_brems.stl` | Skoen (13) skal gå inn frå sida, og røyret skal skuve han på plass og gli under |
| `prove_bjelkesnitt.stl` og `prove_loksnitt.stl` | Rute og ark skal klemmast når skruen er stramma, utan at bossen sprekk |

Glepp noko, så endre `PASS_LIM`, `PASS_GLID` eller `ROYR_D` øvst i `ruta_c.py` og køyr på nytt.

## Handleliste

CAD-en er no sett opp for budsjettkurven på under 400 kr. Prisane er frå nettsidene 14.11.2026. Lagerstatus i kvar butikk er ikkje sjekka, og USB-stripa stod som utseld på nett.

| Vare | Butikk | Art.nr. | Pris | Bruk |
| --- | --- | --- | --- | --- |
| Koparrøyr Ø 12 mm × 2 m, forkroma | Clas Ohlson | 30-6571 | 199,90 | 04 (242 mm) og 09 (308 mm) |
| USB LED-list 1 m, RGB, 10 × 3 mm | Kjell & Company | 57819 | 99,90 | Åtte diodar, om lag 27 cm |
| Skruesortiment SK-180, M3 × 12, 19 og 25 | Kjell & Company | 89070 | 49,00 | 6 E (M3 × 19), 3 F (M3 × 12), og G som er ein M3 × 12 kappa til 8 mm |
| Skiver M16, Ø 30, 25 stk | Clas Ohlson | 11-1203-16 | 49,90 | 24 skiver som ballast |
| **Sum** | | | **398,70** | |

Heimefrå: superlim eller epoksy, baufil og fil, loddebolt og litt krympestrømpe eller teip, USB-ladar, noko gummi til føter (16 små bitar), ei tynn snor, nokre centimeter 1,75 mm filament, skyvelære og vater.

Før du handlar og printar:

- **Sjå på skruane i pakken.** Hovudtypen står ikkje på nettsida. Forsenkingane er Ø 6,6 og tek sylinderhovud og panhovud. Senkhovud går òg, men ligg dårlegare an.
- **Mål stripa.** Kanalen er laga for 10 × 3 mm. Er ho annleis, rett `LED_B` og `LED_T` øvst i `ruta_c.py` før bjelken blir trykt.
- **Kopling av stripa.** Enklast er å klippe av kontrollboksen og lodde USB-leidningen rett på stripa: raud til «+5V», svart til R, G og B samla. Då lyser ho kvitt heile tida, og berre to leiarar går gjennom røyret. Det gjeld vanleg 4-pins RGB-stripe; sjekk at putene er merkte slik. Leidningen blir tredd frå foten og opp, sidan USB-pluggen ikkje går gjennom røyret.
- **Lyset** blir kaldt kvitt, og åtte diodar gjev synlege punkt langs kanten av ruta.

### Om det kjem meir pengar

Den fulle lista var 1199,20 kr, alt frå Clas Ohlson: COB-stripe 24 V 3000 K med adapter og brytar (36-8960, 349,90), skruesett med M3 × 10 og 20 (40-7042, 219,90), to pakkar skiver (99,80), Loctite Power Epoxy (34-8919, 149,90), Wago 221 (36-6520, 139,90) og antisklknottar (21-2865, 39,90), i tillegg til røyret. Stripa gjev varmt, jamt lys. Ho er 8 × 2 mm, så `LED_B`, `LED_T` må setjast til 8 og 2. Til lakk: Paintguide grunning 41-3362, matt svart 41-3355 eller Vintage Sand 41-3348, og gull metallic 41-3354 til endeloket.

## Lakk

Lakken er ikkje med i budsjettkurven. Har du boksar ståande, er dette framgangsmåten. Elles blir lampa trykt i den fargen ho skal ha.

Lampa blir sprøytt i éin matt farge. Det er det H4 krev, og det gøymer laglinene og skøytane.

1. Lim stativet (fot, fotring, stamme, bogestykke, akselrøyr) og bjelken først. Lakk før lys, rute og lok kjem i.
2. Slip plasten lett med korn 240. Slip krommen på stammerøyret matt, elles slepper lakken.
3. Teip det som skal passe: akselrøyret (09), boringa og kragelomma i bjelken, spalta til ruta og LED-kanalen. Lakken byggjer 0,05 til 0,1 mm og et opp klaringa på 0,40 mm.
4. To tynne strok grunning, så to til tre tynne strok farge. Loka (06) blir lakka for seg, med klemflata ned.
5. Endeloket (11) får messingfarge. Det er messingpunktet frå H5.
6. Lat lakken herde eit døgn før montering. Sprøyt ute eller med god lufting, og hald boksen over 15 °C.

Prøv grunning og lakk på ein av prøvebitane først. Heft på PETG er ikkje prøvd.

## Uavhengig kontroll

Tre kontrollørar gjekk gjennom første utkast kvar for seg: montering steg for steg, printbarheit lag for lag, og rekninga på nytt frå STL-volum. Kvart alvorleg funn vart etterprøvd av ein fjerde før det vart rekna som feil. Fire ting ville ha stoppa bygget:

| Funn | Retting |
| --- | --- |
| Leidningen kom ikkje ut av foten. Hakket i veggen var blindt, 2,4 mm gods stod att | Hakket startar 5 mm lenger inne. Kontrollen har fått ein Ø 4-sonde langs leidningsvegen |
| Bremsa klemde ikkje. Skoen tok i skuldra 0,10 mm før han nådde røyret | Vengene på skoen er flytta, så vandringa er 0,9 mm |
| Bjelkehalvdelane stod med skøyten ned og fekk tak i lufta 128 og 184 mm over plata | Dei står no på enden med skøyten opp |
| Botnloket låg opp ned i printfila | Retta |

I tillegg er dette endra etter kontrollen: fotringen, styrepinnane, stripa på 27 cm (leidningen kom ikkje ned i slissa med 30 cm), bremseskruen på 8 mm (hovudet stakk 1 mm ut), tappar og klossar som toler skiver opp til 3,3 mm, avlasting ved loket som klemmer plater ned til 2,25 mm, og velterekninga. Skoen blir no skoven på plass av røyret: i båsen der han går inn, er taket lågare, så røyret må flytte han inn under skruen for å kome forbi, og han kan ikkje gli attende.

Rettingane vart så etterprøvde av to nye kontrollørar, éin på bremsa og monteringa og éin på printfilene. Printfilene stod: alle er tette, ligg rett veg, og ingenting treng høg støtte. Bremsa hadde éin feil til: skoen kom ikkje inn i båsen, fordi tappen tok i overkjeven 0,6 mm før han var inne. No har tappen 45° fas på hjørna, og munninga held fram 2,9 mm inn i kjeven. Ein stegvis prøve viser at skoen går rett ned i ei sjakt og så sidelengs inn i båsen utan å ta i noko. Sjakta er om lag 0,6 mm vidare enn skoen, så `prove_brems.stl` bør prøvast før bjelken blir trykt. Vengene på skoen er 0,8 mm (fire lag) og har 0,3 mm klaring i båsen, og hakket i botnloket går heilt inn i koplingsrommet, så leidningen ligg rett heile vegen ut.

## Det heftet ikkje teiknar

- **Trekkjesnor.** Træ ei tynn snor gjennom akselrøyr, bogestykke og stamme, og vidare ned gjennom sokkelen og bak i foten, før stamma blir limt. Leidningen kan ikkje styrast rundt svingen i foten utan.
- **Grad.** Fil røyrendane innvendig, særleg venstre ende av akselrøyret der leidningen bøyer inn i slissa. Sjå etter grad på kanten mellom båsen til skoen og boringa.
- **Bjelken inn på røyret.** Hald ruta vassrett. Då ligg skoen mot den heile veggen i båsen, og røyret skuvar han rett inn under skruen.
- **Loket før G.** Forsenkinga til bremseskruen ligg over skøyten mellom bjelke og lok. Skal loket av att, må G ut først.
- **Stripa.** Lim enden av stripa godt der ho ligg over opninga til skoen.
- **G.** Fil den kappa enden plan, så han kviler flatt i styreholet i skoen.
- **Støtte i printen.** Foten skal ha støtte slått av, elles kjem det støtte inni hylsa til røyret. Dei andre delane som treng støtte, skal ha «berre frå plata».

## Det som er uvisst eller ikkje gjort

- **Ingenting er trykt eller montert.** Kontrollen er digital: masse, velt, kollisjon, stopp og styrke i `ut-c/kontroll.json`.
- **Røyrveggen** er rekna til om lag 1,0 mm ut frå vekta på pakken. Mål ytterdiameteren med skyvelære før print.
- **Skruane og stripa** i budsjettkurven er ikkje sette. Måla er frå nettsidene.
- **Varmen frå stripa.** Åtte RGB-diodar på fullt kvitt trekkjer om lag 0,5 A, 2,4 W. Det er tre gonger meir enn COB-stripa. PETG toler det. PLA gjer det truleg ikkje.
- **Skivene** er rekna til 2,7 mm og 10 g ut frå vekta på pakken. DIN 125 seier 3 mm nominelt. Foten tek skiver opp til 3,3 mm, og skivene blir limte til tappane, så tjukna treng ikkje treffe.
- **Lysleiaren** frå skjermen er føresett å vere 300 × 190 × 3 mm. Loket klemmer plater frå 2,25 til 3,2 mm. Mål plata og arket, og rett `RUTE_T` og `FILM_T` om dei vik av. Plata treng fem hol Ø 4 etter `ut-c/geometri.json`.
- **Bremsa** kviler på ein skruespiss mot 2 mm PETG. Plasten kan sige. Stram G etter eit døgn og etter ei veke.
- **Lyset** har ingen brytar eller dimming når kontrollboksen er klipt av: lampa blir slått på og av i USB-kontakten. 15 mm i kvar ende av kanten er utan stripe. Lysstyrken i ruta er ikkje rekna eller målt.
- **Slicing** er ikkje gjort. Printoppsettet over er eit framlegg.
- **Heft av lakk og lim** på PETG og på slipt krom er ikkje prøvd.

## Filene

| | |
| --- | --- |
| `ruta_c.py` | Parametrisk CAD, kontroll og eksport |
| `ut-c/stl/` | Printfiler og prøvebitar |
| `ut-c/ruta-pa-fot-rev-c.step`, `ut-c/step/` | Samanstilling og einskilddelar |
| `ut-c/kontroll.json`, `ut-c/geometri.json` | Tal og mål |
| `rettleiing-c/` | Monteringshefte i IKEA-stil, 10 sider (M06) |
