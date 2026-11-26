# Sveip mini · lampa som så vidt rommar ein micro:bit V2

Sveip mini er rev. B i skala 0,32: **96 × 96 × 33,6 mm**. Stamma er 57,0 mm brei og 53,6 mm høg, og kortet (51,6 × 42,0 mm) står rotert 90° bak framveggen og fyller henne. Det einaste som syner av kortet, er LED-matrisa på 5 × 5 gjennom 25 hol. Til høgre for matrisa står eit messingpunkt, der kortet har touch-logoen sin. Dei to deler eitt forsenka felt på 32 × 23 mm.

Varianten er V12 i `../overflate` (`v12_mini.py`). Rev. B er ikkje endra, og dei store variantane V9 til V11 har ikkje micro:bit.

## Kvifor 0,32 og rotert

- Ståande kort krev skala 0,41 til 0,44 (122 til 130 mm): kortet er breiare enn den flate framveggen, og knapp A og lysrista treff krumminga i nasen.
- Rotert 90° med klokka er kortet 42 mm breitt og 51,6 mm høgt. Då styrer høgda: kortet er 51,6 mm i ei stamme på 53,6 mm.
- USB-en peikar ut mot den opne enden av stamma, så kortet kan programmerast utan å opne lampa.
- Logoen hamnar til høgre for matrisa, på same line som messingknappen i rev. B.
- Det går an å gå ned til 0,30 (90 mm). Då stikk kortet 4 mm opp bak skjermsaumen. Ved 0,28 treff foten på lysrista krumminga i nasen.

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
| Kretskortet til krumminga i nasen | 2,3 |
| Knapp A og B til veggen | 0,55 |
| Lysrista til veggen | 0,3 |
| Kretskortet til enden av stamma | 6,5 |
| Kretskortet over underkanten | 3,0 |
| Kretskortet over skjermsaumen (bak veggen) | 1,0 |
| Fri djupn bak kortet | 19 |

Måla på kortet er frå den offisielle monteringsteikninga for V2 (Avnet, DWG 1.48, rev. 1, på tech.microbit.org).

## Kopling

| På kortet | Går til | Merknad |
|---|---|---|
| Ring 0 | arbeidslyset (ned), PWM | 10 kΩ til GND, så lyset er av medan kortet startar |
| Ring 1 | stemningslyset (opp), PWM | 10 kΩ til GND |
| Logoen | messingpunktet, via ein fjørpinne | messingen står i ei isolerande hylse |
| JST | 2 × AAA bak kortet | 3 V rett inn. Aldri ei litiumcelle direkte |

Skruane gjennom ringane skal vere M3 i nylon. Ein utgang på kortet toler under 1 mA, så han styrer ein transistor eller ein drivar, aldri lysdiodane direkte.

## Fastvare

`sveip_mikrobit.py` er MicroPython for V2. Opne python.microbit.org, lim inn fila og send ho til kortet.

- Kort trykk: av og på.
- Hald: lyset sveiper mellom arbeid og stemning på 8 s (F2 krev under 10 s). Neste hald går andre vegen.
- Berøring tel ikkje medan lampa blir lyfta (akselerometeret).
- Biletet blir snudd 90° i programmet, sidan kortet står rotert.

Logikken er køyrd mot ein stubb av `microbit`-modulen i åtte tilfelle. Ho er ikkje køyrd på eit kort.

## Står att

1. **Storleiken.** Ei lampe på 96 mm gjev ikkje arbeidslys på eit skrivebord. Utkraginga er 39 mm, og kroppen kan kvitte seg med om lag 2 W. Mini er ei stemningslampe eller ein modell, ikkje ei erstatning for rev. B.
2. **Berøringa.** Fjørpinne frå messing til logoen gjennom ein jorda aluminiumsvegg er ikkje prøvd. Etter kjeldekoden kalibrerer kortet éin gong ved oppstart. Messingen treng seriemotstand og vern mot statisk utlading.
3. **Lyset.** Lyskjeldene, drivaren og kjølinga er ikkje teikna. Flimmer må målast: kortaste PWM-periode er 256 µs (3,9 kHz).
4. **Innmaten.** Chassis, endeplate med opning for USB, batterihaldar og ballast i foten er ikkje teikna. Botnflensane frå rev. B må teiknast om, for skalerte står dei i vegen for underkanten av kortet. Lampa veg truleg under 150 g og treng ballast.
5. **Toleransen** på LED-plasseringa er ikkje oppgjeven. Bor eit prøvestykke først.

## Filer

| Fil | Innhald |
|---|---|
| `plassering.png`, `plassering.py` | heile lampa framanfrå og snitt gjennom matrisa og messingpunktet |
| `mini_passform.py` | kontroll av at kortet får plass |
| `d15_lysrist.py`, `.step`, `.stl` | lysrista, kontrollert mot LED-ane, knappane og ringane |
| `sveip_mikrobit.py` | fastvara |
| `../overflate/bilete/v12_mini.png`, `v12_mini_naer.png` | rendringane |
