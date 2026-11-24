# SEGL · innkjøpsplan, prototyp og montering

Full liste med delenummer: `kontroll/segl_innkjopsliste.csv`. Prisane er anslag; ingen tilbod er henta inn.

## A · Plate og fres (produksjon)

| pos | kva | kjelde | merknad |
| --- | --- | --- | --- |
| D01, D02 | laserskjering og bøying i DC01 1,5 mm | `produksjon/*_utbretta.dxf` + `cad/D0*.step` | bøyetabell i `produksjon/boyetabell.csv` |
| E01, E02-BOTN | laserskjering og bøying i AlMg3 1,5 mm | same | |
| H01, H03 | 5 sveiseboltar ISO 13918 PT M3 × 8, CD-sveisa | merka på laget MERKE | prøveplate med lakk først |
| alle synlege | pulverlakk fin struktur matt, RAL 8023 | | samanlikn fysiske prøveplater med skissa |
| E02, E03 | klampe fresa, knapp dreia, EN AW-6082 | `cad/E02*.step`, `cad/E03*.step` | |

Anslag: 1600 til 3200 kr for eitt lakka sett plater; 120 til 220 kr per sett ved 50.

## B · Elektronikk

| pos | kva | delenummer |
| --- | --- | --- |
| E01-LED | LED-stripe 24 V, dim-to-warm 3000 til 1800 K, CRI 90, 10 mm, 2 steg = 125 mm | LEDYI LY224-S2216DTW-W24-IP20 |
| E04-ENK | enkoder med trykk, aksel 20 mm, D-flate | Bourns PEC12R-4220F-S0024 |
| E04-USB | USB-C, berre straum | GCT USB4125-GF-A-0190 |
| E04 | ATtiny412 (PWM 20 kHz, kurve ned til 2 %), AO3400A, boost 5 til 24 V, 2 × 5,1 kΩ på CC, PTC 2 A, TVS 5 V | forslag; kortet er ikkje lagt ut |
| H07 | JST PH 2-polar inline | PHR-2, SPH-002T-P0.5S, B2B-PH-K-S |

Kvifor 24 V og ikkje 5 V: det er berre 24 V-stripene som blir varmare når dei blir dempa (krav F11). Stripa trekkjer 2,25 W, så ein vanleg USB-lader på 5 V og 1 A er nok (krav B3).

## C · Festemiddel

| pos | tal | kva |
| --- | --- | --- |
| H02 | 3 | flensmutter M3 DIN 6923 A2 (pipenøkkel 5,5) |
| H04 | 2 | rifla mutter M3, for hand |
| H05 | 2 | senkskrue M2,5 × 6 DIN 965 A2, Torx T8 |
| | 6 | M2 × 4 og M2,5 × 5 til kort og botnplate |

## Prototyp med det du har

- **Pappmodell 1:1:** skriv ut `produksjon/segl_mal_1til1.pdf` på A3 i 100 %. Kontrollina skal vere 50 mm. Skjer langs heil strek og bret langs stipla. Det gjev forma i full storleik på om lag 20 minutt.
- **Segla i metall:** skjer DXF-ane i 1,0 til 1,5 mm aluminium eller stål på laseren på AHO, og bret på kantbenken. I staden for sveiseboltar kan du bruke M3-skruar gjennom hol på merka.
- **Klampe, knapp og berar:** `print/Segl_prototyp_P1S_PETG.3mf` i PETG. PLA mjuknar ved berarar som blir varme.
- **Lys:** det einaste du må kjøpe er ei 5 V COB-stripe på 2700 K (BTF-Lighting FCOB, om lag 90 kr meteren). Klipp henne til om lag 125 mm.
- **Styring:** Arduino Nano og ein logikknivå-MOSFET (AO3400A eller IRLZ44N). Kople stripe-minus til drain, source til GND, gate til D9 via 100 Ω, og 10 kΩ frå gate til GND. Stripe-pluss går til 5 V. Ein vanleg potmeter på A0 er nok til prøva.

```
// 20 kHz PWM på D9 (Timer1), kurve ned mot 2 %
void setup() {
  pinMode(9, OUTPUT);
  TCCR1A = _BV(COM1A1) | _BV(WGM11);
  TCCR1B = _BV(WGM13) | _BV(WGM12) | _BV(CS10);
  ICR1 = 799;                       // 16 MHz / 800 = 20 kHz
}
void loop() {
  float x = analogRead(A0) / 1023.0;
  float y = x * x * x;              // auget ser omtrent kubisk
  OCR1A = (int)(16 + y * (799 - 16));  // 16/800 = 2 % minste nivå
  delay(5);
}
```

Standard-PWM på Arduino (490 eller 980 Hz) flimrar på kamera. Bruk 20 kHz som over (krav T1).

## Montering

Rettleiinga står steg for steg i `montering/Segl_monteringsrettleiing.pdf`:

1. Før høgseglet inn mot framseglet slik at leppa går over dei tre boltane.
2. Skru på tre flensmutrar med pipenøkkel 5,5 mm.
3. Set lysmodulen på dei to boltane i golvet, stram dei rifla mutrane for hand og kople saman kontakten.
4. Set klampa på tunga og skru inn to skruar nedanfrå med Torx T8.
5. Trykk knappen ned på akselen. Den flate sida viser vegen.

**Byte lysmodulen:** trekk ut USB-kabelen og skru av dei to rifla mutrane for hand. Løys kontakten og løft modulen ut. Det krev ingen verktøy og tek under eitt minutt (krav B1).

**Materialfraksjonar (krav B2):** stål (D01, D02, boltar), aluminium (E01, E02, E03) og elektronikk (E04 og LED-stripa) kan skiljast utan lim. Tapen under stripa er ein del av lysmodulen, som blir bytt heil.
