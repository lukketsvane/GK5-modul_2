# Sveip mini · den minste lampa som rommar ein micro:bit V2

Sveip mini er rev. B i skala 0,28: **84 × 84 × 29,4 mm**. Stamma er 49,8 mm brei og 46,9 mm høg. Kortet (51,6 × 42,0 mm) står rotert 90° bak framveggen og fyller breidda på stamma. Det einaste som syner av kortet, er LED-matrisa på 5 × 5 gjennom 25 hol. Til høgre for matrisa står eit messingpunkt, der kortet har touch-logoen sin. Dei to deler eitt forsenka felt på 32 × 23 mm.

Varianten er V12 i `../overflate` (`v12_mini.py`). Rev. B er ikkje endra, og dei store variantane V9 til V11 har ikkje micro:bit.

## Kvifor 0,28 og rotert

- Rotert 90° med klokka er kortet 42 mm breitt. Det får plass i stamma med 0,6 mm til krumminga i nasen og 3,0 mm til enden av stamma.
- Mindre går ikkje: ved 82,5 mm (skala 0,275) treff kortet veggen i nasen.
- Kortet er 51,6 mm høgt, og stamma er 46,9 mm. Kortet går difor 7,7 mm opp bak skjermsaumen, på innsida av veggen. Det syner ikkje utanpå.
- Ståande kort krev skala 0,41 til 0,44 (122 til 130 mm).
- USB-en peikar ut mot den opne enden av stamma, så kortet kan programmerast utan å opne lampa.
- Logoen hamnar til høgre for matrisa, på same line som messingknappen i rev. B.

## Kva matrisa viser

Lampa sjølv, som ikon. Dei to øvste radene er skjermen og følgjer stemningslyset. Dei tre nedste radene, tre kolonnar breie, er stamma og følgjer arbeidslyset. Når du held fingeren på messingen, flyttar lyset seg mellom stamma og skjermen i ikonet, samtidig som det skjer i lampa.

## Oppbygging

Sjå `plassering.png`. Frå utsida og inn:

| Lag | Mål (mm) |
|---|---|
| Plata, med 25 hol Ø 2,0 på 4,0 mm deling | 1,0 |
| Klar, matta propp i kvart hol, i flukt med plata (UV-harpiks eller PMMA) | 1,0 |
| Luft mellom veggen og lysrista | 0,3 |
| Lysrista D15: svart blokk med 25 kanalar, skrudd til kortet | 4,8 |
| micro:bit V2 med framsida mot veggen | 1,6, og 5,5 bak |

Knapp A og B stikk 4,55 mm fram frå kortet, så LED-ane står om lag 5 mm bak plata. Utan rist og proppar syner dei berre rett framanfrå. Rista hindrar òg at éin LED lyser opp naboholet.

`mini_passform.py` byggjer veggen og kortet som lekamar og måler avstandane:

| Mål | mm |
|---|---|
| Kretskortet til krumminga i nasen | 0,6 |
| Knapp A og B til veggen | 0,55 |
| Lysrista til veggen | 0,3 |
| Kretskortet til enden av stamma | 3,0 |
| Kretskortet over underkanten | 3,0 |
| Kretskortet opp bak skjermsaumen | 7,7 |
| Fri djupn bak kortet | 15 |

Måla på kortet er frå den offisielle monteringsteikninga for V2 (Avnet, DWG 1.48, rev. 1, på tech.microbit.org).

## Kopling

| På kortet | Går til | Merknad |
|---|---|---|
| Ring 0 | arbeidslyset (ned), PWM | 10 kΩ til GND, så lyset er av medan kortet startar |
| Ring 1 | stemningslyset (opp), PWM | 10 kΩ til GND |
| Logoen | messingpunktet, via ein fjørpinne | messingen står i ei isolerande hylse |
| JST | 2 × AAA bak kortet | 3 V rett inn. Aldri ei litiumcelle direkte. Haldaren (14 mm) har 15 mm djupn å stå i, og stikk opp i skjermen |

Skruane gjennom ringane er dei fem M3-senkskruane (A). Kvar skrue rører berre sin eigen ring, og rista og stolpen er av plast, så stål går fint. Nylon formar ikkje gjenger i PLA. Ein utgang på kortet toler under 1 mA, så han styrer ein transistor eller ein drivar, aldri lysdiodane direkte.

## Fastvare

`sveip_mikrobit.py` er MicroPython for micro:bit V2. To måtar å få ho på kortet:

- Dra `sveip_mikrobit.hex` over på MICROBIT-disken. Fila er MicroPython 2.1.2 med programmet som `main.py`.
- Eller opne python.microbit.org, lim inn programmet (eller opne hex-fila der) og send det til kortet.

Programmet krev V2. V1 har ikkje touch-logoen.

| Handling | Kva lampa gjer |
|---|---|
| Kort trykk på messingen (under 0,4 s) | av eller på, med ei toning på 0,3 s. Lampa svarar 0,12 s etter at fingeren er av |
| Hald | lyset sveiper mellom arbeid og stemning på 8 s (F2 krev under 10 s). Neste hald går andre vegen |
| Hald når lampa er av | ingenting. Ein grip om lampa for å flytte henne skal ikkje tenne henne. Trykk for å slå på |
| Lampa blir vippa meir enn om lag 23° medan fingeren ligg på | lyset går attende til der det var då fingeren kom, og glir dit på 0,3 s |
| Ein finger ligg på messingen når straumen kjem | blir sett bort frå til han er borte |
| Hald over 15 s | blir sett bort frå, med blandinga der ho står |
| Straumen kjem | lampa slår seg på med blandinga frå førre sveip |

- **Matrisa er lampa sett framanfrå.** Dei to øvste radene er skjermen og følgjer stemningslyset. Dei tre nedste radene til venstre er stamma og følgjer arbeidslyset. Dei seks i hjørnet under skjermen er alltid mørke. Biletet blir snudd 90° i programmet, sidan kortet står rotert.
- **Lyset blir flytta, ikkje dempa.** Arbeid er cos² og stemning sin² av blandinga, så summen er alltid den same, som i rev. B (`../../elektro/SPESIFIKASJON.md`, del 3). Midt i sveipet er begge på 50 %, og endane går mjukt. P0 og P1 gjev det same som PWM på 3,9 kHz.
- **Matrisa viser same lysmengd som utgangane.** Nivåa 1 til 9 på kortet doblar lysstyrken for kvart steg (1, 2, 4 … 255 av 255), så programmet vel det nivået som ligg nærast i den skalaen.
- **Blandinga blir lagra** i `sveip.txt` på kortet etter eit sveip som har flytta henne meir enn 2 %. Trykk og små rørsler skriv ingenting, så flashminnet blir ikkje slite. Er flashen full, verkar lampa likevel.
- **Berøringa blir filtrert i programmet.** MicroPython 2.1.2 gjev rå målingar av touch-logoen, éi kvar 2. ms, og filteret i CODAL blir ikkje brukt. Programmet krev difor tre runder (60 ms) på rad med kontakt før ei berøring tel, og 120 ms utan kontakt før ho er over. Ein støyspiss, eit utfall midt i eit hald og sprett ved slepp gjer då ingenting.
- **Dødt hald:** eit kort hald nær ein ende snur ikkje retninga. Innanfor 15 % frå ein ende går neste hald vekk frå enden.
- **Vipping:** programmet følgjer tyngdevektoren, jamna ut over 0,2 s. Endrar han seg meir enn 0,4 g medan fingeren ligg på, blir berøringa forkasta og lyset går attende. Det fangar vipping over om lag 23° og fall. Det fangar **ikkje** at lampa blir skoten bortover bordet, vridd eller lyft rett opp. Storleiken på akselerasjonen skil ikkje eit trykk frå eit skuv på ei lampe på 50 g. Ein vern mot skuv må kome frå ein annan kanal, slik rev. B har to berøringspunkt.
- **Terskelen for berøring er fast.** I MicroPython 2.1.2 (CODAL v0.2.43) får logoen ein fast terskel på 3500 tikk, om lag 219 µs ladetid. Kortet kalibrerer ikkje, og det finst ikkje noko kall for å lese råverdien eller kalibrere på nytt. Ekstra kapasitans frå fjør, messingskrue og vegg løftar grunnlinja, og ingenting rettar for det. Ligg grunnlinja over terskelen, er berøringa alltid sann. Då held lampa seg som ho var, og programmet verkar ikkje. Prøv difor på kortet med messingen montert, både på USB og på batteri, at lampa ikkje reagerer utan finger.
- **Feil:** eit uventa unntak startar kortet om, så lampa ikkje står på for alltid. Ctrl-C frå USB slår av lyset.
- **PWM-perioden** er 256 µs (3,9 kHz), og `PWM_US` øvst i programmet er den einaste staden han står. Han ligg der øyret er mest følsamt, så spoler og keramiske kondensatorar i ein drivar kan syngje. V2-kjelda har ingen nedre grense, og 40 µs (25 kHz) gjev 640 steg, men det er ikkje dokumentert og må prøvast på eit kort. Vel perioden saman med drivaren. Ein drivar som treng minst 5 µs på-tid, mistar alle verdiar under om lag 20 av 1023, og då er summen av kanalane ikkje lenger den same i endane av sveipet.
- **Tida** blir rekna med `ticks_diff`. `running_time()` går over til negative tal etter 12,4 døgn, og då ville sveipet ha stoppa.

### Fastvara er kontrollert slik

| Kontroll | Resultat |
|---|---|
| `sveip_mikrobit_test.py`: 27 scenario mot eit simulert kort. Trykk, hald, retning, dødt hald ved ein ende, støyspiss, utfall og sprett i berøringa, finger på ved oppstart, fast kontakt, hald over 15 s, vipping med glidning, feil og Ctrl-C, full flash, ticks som går rundt, treg runde og matrisa mot utgangane. Dei nye scenarioa feilar på den førre versjonen av programmet | 27 av 27 |
| Typekontroll med dei offisielle stubbane til python.microbit.org (pyright) | 0 feil |
| Kompilert med `mpy-cross` 1.18 (MicroPython 2.1.2 byggjer på 1.18) | ok |
| Køyrt i MicroPython 1.29 (WebAssembly) med simulerte pinnar: fullt sveip, lagring og omstart | ok |
| Kvar funksjon programmet brukar, finst i MicroPython 2.1.2-fila som python.microbit.org legg på kortet | ok |
| Matrisa mot CAD-en: testen set LED-ane gjennom `til_lampa` i `mini_passform.py` (CadQuery) og samanliknar med eigen rotasjon, ikkje med programmet | ok |
| `sveip_mikrobit.hex` lese attende: `main.py` er lik `sveip_mikrobit.py` | ok |

Simulatoren gjev råe målingar av berøringa, slik MicroPython 2.1.2 gjer. Den ekte kapasitansen er ikkje modellert.

Ikkje prøvd på eit kort: kva grunnlinja og terskelen er med fjør og messingskrue, om berøringa er sikker nok, om grensa for vipping passar til ei lampe på 50 g, og korleis toning og sveip ser ut gjennom lysleiarane.

`lag_hex.cjs` byggjer hex-fila på nytt etter ei endring (sjå toppen av fila).

## Print (Bambu Lab P1S)

`mini_print.py` byggjer fire printdelar, kontrollerer passforma mot micro:bit-en og skriv `print/`. Sjå `mini_sprengt.png`.

| Del | Farge | Mål (mm) | PLA |
|---|---|---|---|
| M1 kropp | lampefarge | 84 × 29,4 × 84 | om lag 21 g |
| M2 chassis | kva som helst (syner ikkje) | 47 × 27 × 60 | 8 g |
| M3 lysrist D15 | svart | 52 × 35 × 5 | 3 g |
| M4 lysplate | kvit | 81 × 26 × 13 | 3 g |

**Alle delane er i éi fil:** `print/Sveip_mini_alle_delar.3mf`. Dei ligg ferdig plasserte på éi plate (sjå `print/Sveip_mini_alle_delar.png`). Kvar del har ein farge i fila: lampefarge, kvit eller svart.

1. Opne fila i Bambu Studio. Seier han at fila ikkje er frå Bambu Lab, vel du å laste geometrien.
2. Vel P1S med 0,4 mm dyse, PLA Matte og 0,20 mm lag.
3. Gje kvar del filament: M3 svart, M4 kvit, M1 og M2 lampefargen. Høgreklikk delen og vel filament.
4. Ingen støtte. Elefantfotkompensasjon 0,15 mm.
5. Brim berre på M1: 5 mm, berre ytre, med 0,1 mm avstand. Legg det til under innstillingane for objektet. Dei andre delane skal ikkje ha brim. Chassiset har berre 0,2 mm klaring i stamma, og ein brimrest kan sperre.
6. Slice og print. Skrap brimen pent av toppkanten på M1, for han syner.

M1 blir printa opp ned, med toppkanten mot plata. Botnen under utkraginga blir då ei bru på 27 mm. Undersida held seg fin, men på innsida kan brua henge ned 0,5 til 1 mm.

AMS byter farge i dei første 5 mm, der M3 er svart. Er lampa kvit, kan M1, M2 og M4 dele same filament. Med grå lampe og kvit lysplate byter AMS farge i dei første 13 mm.

- Veggen er 1,2 mm (i aluminium 1,0). Det forsenka feltet er 0,3 mm djupt, så det syner i print.
- Endeplata på stamma og botnen under utkraginga er ein del av kroppen. Stamma er open nede, og der går chassiset inn.
- Hol som ligg ned i printen, blir trykte for små. Holet for messingskruen er difor 3,4 mm, og styreholet for M3 i stolpen 2,8 mm.

### Det du treng i tillegg

- 5 × M3 × 8 senkskrue. Stål går fint, sidan kroppen er av plast.
- 1 × M3 × 4 messingskrue med linsehovud (DIN 7985). Dette er berøringspunktet.
- 1 fjør, Ø 3,0 mm og om lag 3 mm lang, med indre Ø under 2,5 mm. Då kviler ho på tuppen av skruen og glir ikkje utanpå. Ei kulepennfjør klipt til passar.
- om lag 15 cm naturfarga eller transparent 1,75 mm filament til lysleiarane
- CA-lim (superlim)
- micro-USB-kabel

### Montering

Monteringsrettleiing i IKEA-stil: `rettleiing/ut/rettleiing.pdf` (M02, sjå `rettleiing/README.md`). Kort fortalt:

Før monteringa (porten): skuv eit stykke filament inn i ein kanal i lysrista. Det skal gli. Skru ein av senkskruane inn i hylsa over logoen, så han formar gjengene, og skru han ut att. Står han att, sperrar hovudet når chassiset skal inn. Skuv chassiset opp i den tomme stamma. Det skal gli inn med lett klem. Ta det ut att.

1. Legg lysrista med lommene opp. Slepp fjøra ned i lomma over hylsa.
2. Legg micro:bit-en med framsida ned over rista, med lommene over LED-ane og logoen over fjøra.
3. Hald kortet og rista saman, og legg kortet mot stolpen på chassiset. Skuv kortet inn mot kanten på stolpen ved kantkontakten, og ned på hylla under kortet.
4. Skru saman med dei fem senkskruane gjennom lysrista, ringane og inn i stolpen.
5. Legg chassiset på ryggen, så rista vender opp. Skuv filament inn i kvar kanal til det stoppar mot LED-en. Lim med ein drope CA-lim, og klipp i flukt med framsida av rista eller inntil 0,2 mm under. Ingenting, heller ikkje lim, må stå over framsida, for då sperrar det når chassiset skal inn.
6. Skuv chassiset med kortet opp i stamma nedanfrå, med USB-kontakten mot endeplata, til golvet er i flukt med underkanten av stamma. Ingenting stoppar det, berre dei fire ribbene på golvet klemmer.
7. Skru messingskruen (M3 × 4) inn gjennom holet i feltet til han tek i hylsa. Ikkje stram hardt, for gjengene i plasten er berre 2,6 mm lange. Mål gjerne med multimeter at det er kontakt mellom messingen og logoen.
8. Legg lysplata ned i skjermen ovanfrå.
9. Kople USB gjennom holet i endeplata, og send fastvara til kortet.

Kontroll: eit kort trykk på messingen slår lampa av og på. Held du, sveiper matrisa.

Lampa har ingen lyskjelder enno. Matrisa viser sveipet, og utgangane P0 og P1 er klare for ein LED-drivar.

### Kontrollert

`mini_print.py` stoppar om ein av desse kontrollane feilar. Tala står i `print/print_rapport.json`.

| Kontroll | mm |
|---|---|
| Kroppen til kretskortet (krumminga i nasen) | 0,55 |
| Kroppen til knapp A og B | 0,55 |
| Kroppen til lysrista (0,1 framfor hylsa, som skruen trekkjer inntil) | 0,3 |
| Kroppen til chassiset, utanom dei fire klemmeribbene | 0,2 |
| Kanten på stolpen til kortkanten | 0,1 |
| Tuppen på messingskruen til kretskortet (plass til fjøra) | 2,0 |
| USB-pluggen til kanten av holet | 1,0 |

- Ingen av dei printa delane går inn i kortet eller komponentane på det.
- Stolpen ligg berre bak kantkontakten, under sona der baksida av kortet har komponentar.
- Kvart LED-hol står på same akse som kanalen sin.
- Chassiset med kortet kjem opp i stamma utan å ta borti noko, og lysplata kjem ned i skjermen.
- Delane ligg på plata, utanfor sperresona og minst 8 mm frå kvarandre.
- Alle fire nett er lukka, manifolde og rett orienterte, og 3MF-fila er kontrollert med lib3mf.
- Ein uavhengig gjennomgang av montering og print fann ingen kritiske feil. Dei viktige funna er retta: fjøra, lommene over LED-ane, kanalane, festet for kortet og chassiset, og fargen på lysplata.

Ikkje prøvd: kor mykje hola krympar i verkelegheita, og om Bambu Studio les fargane i fila. Print gjerne lysrista først. Ho er lita, og du ser då om filamentet går i kanalane.

## Står att

1. **Storleiken.** Ei lampe på 84 mm gjev ikkje arbeidslys på eit skrivebord. Utkraginga er 34 mm, og kroppen kan kvitte seg med 1 til 2 W. Mini er ei stemningslampe eller ein modell, ikkje ei erstatning for rev. B.
2. **Berøringa.** Fjørpinne frå messing til logoen gjennom ein jorda aluminiumsvegg er ikkje prøvd. Terskelen er fast (3500 tikk) og kortet kalibrerer ikkje, så grunnlinja med fjør og messingskrue må målast. Messingen treng seriemotstand og vern mot statisk utlading.
3. **Lyset.** Lyskjeldene, drivaren og kjølinga er ikkje teikna. Flimmer må målast. PWM-perioden er 256 µs (3,9 kHz) og kan setjast kortare, sjå Fastvare.
6. **Leidningar til ringane.** Foten på lysrista dekkjer alle fem ringane framme, og stolpen dekkjer dei bak, så det finst ingen veg for P0, P1 og GND når lampa er montert. Skruane fører ikkje signalet: dei har 0,5 mm spel i ringen, og kontakten er tilfeldig. Kortet står 0,55 mm frå nasen, så det er ikkje plass til kantkontakt eller klemmer. Det må teiknast ein veg, til dømes eit spor i stolpen bak ring 0, ring 1 og GND for lodda leidningar. Skriv òg kvar dei to motstandane på 10 kΩ skal sitje. Lampa har ingen lyskjelder enno, så det er ikkje kravd før drivaren er vald.
4. **Innmaten.** I aluminium er chassis, endeplate, batterihaldar og ballast i foten ikkje teikna. Marginane er små: 0,6 mm i nasen krev at plata blir valsa nøyaktig. Printversjonen har chassis og endeplate, men ikkje batteri eller ballast.
5. **Toleransen** på LED-plasseringa er ikkje oppgjeven. Bor eit prøvestykke først.

## Filer

| Fil | Innhald |
|---|---|
| `plassering.png`, `plassering.py` | heile lampa framanfrå og snitt gjennom matrisa og messingpunktet |
| `mini_passform.py` | kontroll av at kortet får plass |
| `d15_lysrist.py`, `.step`, `.stl` | lysrista, kontrollert mot LED-ane, knappane og ringane |
| `sveip_mikrobit.py`, `sveip_mikrobit.hex` | fastvara, og ho ferdig til å dra over på kortet |
| `sveip_mikrobit_test.py`, `lag_hex.cjs` | testane for fastvara, og byggjaren for hex-fila |
| `mini_print.py`, `print/` | printdelane: STL per del, 3MF med alle delane og kontrollrapport |
| `mini_plate.py`, `print/Sveip_mini_alle_delar.png` | plata med alle delane, sett ovanfrå |
| `rettleiing/` | monteringsrettleiinga: PDF, sider, spesifikasjon og kjelde |
| `mini_sprengt.png`, `mini_sprengt.py` | sprengbilete av printdelane |
| `../overflate/bilete/v12_mini.png`, `v12_mini_naer.png` | rendringane |
