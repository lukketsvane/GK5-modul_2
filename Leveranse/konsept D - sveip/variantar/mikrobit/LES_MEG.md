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

Skruane gjennom ringane skal vere M3 i nylon. Ein utgang på kortet toler under 1 mA, så han styrer ein transistor eller ein drivar, aldri lysdiodane direkte.

## Fastvare

`sveip_mikrobit.py` er MicroPython for micro:bit V2. To måtar å få ho på kortet:

- Dra `sveip_mikrobit.hex` over på MICROBIT-disken. Fila er MicroPython 2.1.2 med programmet som `main.py`.
- Eller opne python.microbit.org, lim inn programmet (eller opne hex-fila der) og send det til kortet.

Programmet krev V2. V1 har ikkje touch-logoen.

| Handling | Kva lampa gjer |
|---|---|
| Kort trykk på messingen (under 0,4 s) | av eller på, med ei toning på 0,3 s |
| Hald | lyset sveiper mellom arbeid og stemning på 8 s (F2 krev under 10 s). Neste hald går andre vegen |
| Hald når lampa er av | slår på, og så sveiper ho |
| Lampa blir flytta medan fingeren ligg på | lyset går attende til der det var då fingeren kom |
| Straumen kjem | lampa slår seg på med blandinga frå førre sveip |

- **Matrisa er lampa sett framanfrå.** Dei to øvste radene er skjermen og følgjer stemningslyset. Dei tre nedste radene til venstre er stamma og følgjer arbeidslyset. Dei seks i hjørnet under skjermen er alltid mørke. Biletet blir snudd 90° i programmet, sidan kortet står rotert.
- **Lyset blir flytta, ikkje dempa.** Arbeid er cos² og stemning sin² av blandinga, så summen er alltid den same, som i rev. B (`../../elektro/SPESIFIKASJON.md`, del 3). Midt i sveipet er begge på 50 %, og endane går mjukt. P0 og P1 gjev det same som PWM på 3,9 kHz.
- **Matrisa viser same lysmengd som utgangane.** Nivåa 1 til 9 på kortet doblar lysstyrken for kvart steg (1, 2, 4 … 255 av 255), så programmet vel det nivået som ligg nærast i den skalaen.
- **Blandinga blir lagra** i `sveip.txt` på kortet etter kvart sveip. Trykk skriv ingenting, så flashminnet blir ikkje slite.
- **Flytting:** programmet følgjer tyngdevektoren, jamna ut over 0,2 s. Endrar han seg meir enn 0,4 g (om lag 23° vipping eller ei varig rørsle) medan fingeren ligg på, blir berøringa forkasta. Eit kort støyt frå sjølve trykket tel ikkje. Lampa er så lett (om lag 50 g) at eit fast trykk på messingen kan vippe henne. Hald gjerne ein finger bak, eller berre kom borti messingen.
- **Kalibrering:** kortet kalibrerer berøringa i 0,5 s når det startar, før programmet køyrer (CODAL, `TouchButton`). Ligg ein finger på messingen då, verkar ikkje berøringa. Trekk då ut kabelen og set han i att. MicroPython 2.1.2 kan ikkje kalibrere på nytt medan programmet køyrer.
- **Tida** blir rekna med `ticks_diff`. `running_time()` går over til negative tal etter 12,4 døgn, og då ville sveipet ha stoppa.

### Fastvara er kontrollert slik

| Kontroll | Resultat |
|---|---|
| `sveip_mikrobit_test.py`: 14 scenario mot eit simulert kort (trykk, hald, retning, hald når av, flytting, støyt, lagring, øydelagd fil, ticks som går rundt, treg runde, matrisa mot utgangane) | 14 av 14 |
| Typekontroll med dei offisielle stubbane til python.microbit.org (pyright) | 0 feil |
| Kompilert med `mpy-cross` 1.18 (MicroPython 2.1.2 byggjer på 1.18) | ok |
| Køyrt i MicroPython 1.29 (WebAssembly) med simulerte pinnar: fullt sveip, lagring og omstart | ok |
| Kvar funksjon programmet brukar, finst i MicroPython 2.1.2-fila som python.microbit.org legg på kortet | ok |
| Matrisa mot CAD-en: testen reknar biletet på lampa frå `til_lampa` i `mini_passform.py`, ikkje frå programmet | ok |
| `sveip_mikrobit.hex` lese attende: `main.py` er lik `sveip_mikrobit.py` | ok |

Ikkje prøvd på eit kort: om berøringa gjennom fjøra og messingskruen er sikker nok, om grensa for flytting passar til ei lampe på 50 g, og korleis toning og sveip ser ut gjennom lysleiarane.

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

Monteringsrettleiing i IKEA-stil: `rettleiing/ut/rettleiing.pdf` (sjå `rettleiing/README.md`). Kort fortalt:

1. Legg micro:bit-en med framsida opp. Set fjøra ståande midt på logoen.
2. Senk lysrista ned over kortet, med hylsa over fjøra og lommene over LED-ane.
3. Snu det heile og legg kortet mot stolpen på chassiset. Skuv kortet inn mot kanten på stolpen ved kantkontakten, og ned på hylla under kortet.
4. Skru saman med dei fem senkskruane gjennom lysrista, ringane og inn i stolpen.
5. Skuv filament inn i kvar kanal til det stoppar mot LED-en. Lim med ein drope CA-lim, og klipp i flukt med framsida av rista eller inntil 0,2 mm under. Ein leiar som stikk fram, sperrar når chassiset skal inn.
6. Skuv chassiset med kortet opp i stamma nedanfrå, med USB-kontakten mot endeplata. Dei fire ribbene på golvet klemmer.
7. Skru messingskruen inn gjennom holet i feltet til han tek i hylsa. Ikkje stram hardt. Mål gjerne med multimeter at det er kontakt mellom messingen og logoen.
8. Legg lysplata ned i skjermen ovanfrå.
9. Kople USB gjennom holet i endeplata, og send fastvara til kortet.

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
2. **Berøringa.** Fjørpinne frå messing til logoen gjennom ein jorda aluminiumsvegg er ikkje prøvd. Etter kjeldekoden kalibrerer kortet éin gong ved oppstart. Messingen treng seriemotstand og vern mot statisk utlading.
3. **Lyset.** Lyskjeldene, drivaren og kjølinga er ikkje teikna. Flimmer må målast: kortaste PWM-periode er 256 µs (3,9 kHz).
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
