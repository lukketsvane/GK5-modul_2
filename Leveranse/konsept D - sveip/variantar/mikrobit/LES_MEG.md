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

`sveip_mikrobit.py` er MicroPython for V2. Opne python.microbit.org, lim inn fila og send ho til kortet.

- Kort trykk: av og på.
- Hald: lyset sveiper mellom arbeid og stemning på 8 s (F2 krev under 10 s). Neste hald går andre vegen.
- Berøring tel ikkje medan lampa blir lyfta (akselerometeret).
- Biletet blir snudd 90° i programmet, sidan kortet står rotert.

Logikken er køyrd mot ein stubb av `microbit`-modulen i åtte tilfelle. Ho er ikkje køyrd på eit kort.

## Print (Bambu Lab P1S)

`mini_print.py` byggjer fire printdelar, kontrollerer passforma mot micro:bit-en og skriv `print/`. Sjå `mini_sprengt.png`.

| Del | Plate | Farge | Mål (mm) | PLA |
|---|---|---|---|---|
| M1 kropp | A | lampefarge | 84 × 29,4 × 84 | om lag 21 g |
| M4 lysplate | A | same | 81 × 26 × 13 | 3 g |
| M2 chassis | B | svart | 47 × 27 × 60 | 8 g |
| M3 lysrist D15 | B | svart | 52 × 35 × 5 | 3 g |

Opne `print/Sveip_mini_A_kropp_PLA.3mf` og `print/Sveip_mini_B_innmat_PLA_svart.3mf` i Bambu Studio. Vel P1S med 0,4 mm dyse, PLA Matte og 0,20 mm lag. Bruk ingen støtte, og brim på 5 mm på plate A og 3 mm på plate B. Slice og print. Du kan òg køyre `python mini_print.py --slice` på maskina med Bambu Studio. Då blir platene slica same veg som rev. B.

- M1 blir printa opp ned, med toppkanten mot plata. Botnen under utkraginga blir då ei bru på 27 mm.
- Veggen er 1,2 mm (i aluminium 1,0). Det forsenka feltet er 0,3 mm djupt, så det syner i print.
- Endeplata på stamma og botnen under utkraginga er ein del av kroppen. Stamma er open nede, og der går chassiset inn.

### Det du treng i tillegg

- 5 × M3 × 8 senkskrue. Stål går fint, sidan kroppen er av plast.
- 1 × M3 × 4 messingskrue med linsehovud (DIN 7985). Dette er berøringspunktet.
- 1 fjør, Ø 3 til 3,5 mm og om lag 3 mm lang, til dømes klipt frå ei kulepennfjør
- om lag 15 cm naturfarga eller transparent 1,75 mm filament til lysleiarane
- micro-USB-kabel

### Montering

1. Legg fjøra i lomma bak hylsa på lysrista.
2. Legg lysrista på framsida av micro:bit-en, med hylsa over logoen og lommene over LED-ane. Set stolpen på chassiset mot baksida, og skru saman med dei fem senkskruane gjennom ringane.
3. Skuv filament inn i kvar kanal til det stoppar mot LED-en, og klipp i flukt med framsida av rista.
4. Skuv chassiset med kortet opp i stamma nedanfrå, med USB-kontakten mot endeplata.
5. Skru messingskruen inn gjennom holet i feltet til han tek i hylsa. Ikkje stram hardt. Skruen held chassiset på plass.
6. Legg lysplata ned i skjermen ovanfrå.
7. Kople USB gjennom holet i endeplata, og send fastvara til kortet.

Lampa har ingen lyskjelder enno. Matrisa viser sveipet, og utgangane P0 og P1 er klare for ein LED-drivar.

### Kontrollert

`mini_print.py` stoppar om ein av desse kontrollane feilar. Tala står i `print/print_rapport.json`.

| Kontroll | mm |
|---|---|
| Kroppen til kretskortet (krumminga i nasen) | 0,55 |
| Kroppen til knapp A og B | 0,55 |
| Kroppen til lysrista (0,1 framfor hylsa, som skruen trekkjer inntil) | 0,3 |
| Kroppen til chassiset | 0,2 |
| Tuppen på messingskruen til kretskortet (plass til fjøra) | 2,0 |
| USB-pluggen til kanten av holet | 1,0 |

- Ingen av dei printa delane går inn i kortet eller komponentane på det.
- Kvart LED-hol står på same akse som kanalen sin.
- Chassiset med kortet kjem opp i stamma utan å ta borti noko, og lysplata kjem ned i skjermen.
- Alle fire nett er lukka, manifolde og rett orienterte. 3MF-filene er kontrollerte med lib3mf.

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
| `sveip_mikrobit.py` | fastvara |
| `mini_print.py`, `print/` | printdelane: STL, 3MF per plate og kontrollrapport |
| `mini_sprengt.png`, `mini_sprengt.py` | sprengbilete av printdelane |
| `../overflate/bilete/v12_mini.png`, `v12_mini_naer.png` | rendringane |
