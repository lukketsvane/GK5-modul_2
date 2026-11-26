# Sveip · micro:bit V2 i stamma

Ein micro:bit V2 står bak framveggen på stamma. Det einaste som syner, er LED-matrisa på 5 × 5: 25 hol i plata, med ein klar, matta propp i kvart. Matrisa står på betjeningslina (z = 70), 47,2 mm til venstre for messingknappen. Ho står på den fjerde dragaren i huda, slik knappen står på den første.

Dette er ein variant. Rev. B (`../../cad`) er ikkje endra: hola er ikkje lagde inn i flatmønsteret, og festet i chassiset er ikkje teikna.

## Kva matrisa viser

Lampa sjølv, som ikon. Dei to øvste radene er skjermen og følgjer stemningslyset. Dei tre nedste radene, tre kolonnar breie, er stamma og følgjer arbeidslyset. Når du held fingeren på messingen, flyttar lyset seg mellom stamma og skjermen i ikonet, samtidig som det skjer i lampa.

## Oppbygging

Sjå `plassering.png`. Frå utsida og inn:

| Lag | Mål (mm) |
|---|---|
| Plata, med 25 hol Ø 2,0 på 4,0 mm deling i eit forsenka felt på 23 × 23 | 1,2 |
| Klar, matta propp i kvart hol, i flukt med plata (UV-harpiks eller PMMA) | 1,2 |
| Luft mellom veggen og lysrista | 0,3 |
| Lysrista D15: svart blokk med 25 kanalar, skrudd til kortet | 4,8 |
| micro:bit V2 med framsida mot veggen og logoen opp | 1,6, og 5,5 bak |

Knapp A og B stikk 4,55 mm fram frå kortet, så LED-ane blir ståande om lag 5 mm bak plata. Utan rist og proppar syner dei berre rett framanfrå. Rista hindrar òg at éin LED lyser opp naboholet.

Måla på kortet er frå den offisielle monteringsteikninga for V2 (Avnet, DWG 1.48, rev. 1, på tech.microbit.org): kortet er 51,60 × 42,00 mm, midtre LED sit midt på breidda og 20,00 mm over underkanten, og ringane sit 13,14 mm under midtre LED.

## Kopling

| Ring | Går til | Merknad |
|---|---|---|
| 0 | arbeidslyset (ned), PWM | 10 kΩ til GND, så lyset er av medan kortet startar |
| 1 | stemningslyset (opp), PWM | 10 kΩ til GND |
| 2 | messingknappen, kapasitiv berøring | ringen nærast knappen; kort leidning, vekk frå kroppen |
| 3V | regulert 3,3 V inn | 1,7 til 3,6 V. Aldri cella direkte |
| GND | felles jord med LED-drivarane | |

Skruane gjennom ringane skal vere M3 i nylon. Metallskruar gjennom 3V og GND kan kortslutte forsyninga mot kroppen. Ein utgang på kortet toler under 1 mA, så han styrer ein drivar eller ein transistor, aldri lysdiodane direkte.

## Fastvare

`sveip_mikrobit.py` er MicroPython for V2. Opne python.microbit.org, lim inn fila og send ho til kortet.

- Kort trykk: av og på.
- Hald: lyset sveiper mellom arbeid og stemning på 8 s (F2 krev under 10 s). Neste hald går andre vegen.
- Berøring tel ikkje medan lampa blir lyfta (akselerometeret).

Logikken er køyrd mot ein stubb av `microbit`-modulen i sju tilfelle. Ho er ikkje køyrd på eit kort.

## Står att

1. **Berøringa.** Kortet kalibrerer éin gong ved oppstart, og fingeren må auke utslaget med over 10 %. Leidning og messing nær ein jorda kropp er ikkje prøvd. Om knappen bak kan dele ring 2 med knappen framme, er heller ikkje prøvd.
2. **Demping.** Kortaste PWM-periode er 256 µs (3,9 kHz). `elektro/SPESIFIKASJON.md` punkt 4 krev minst 20 kHz under 10 %. PWM-en må difor filtrerast til ei styrespenning på drivarane, og flimmermålinga T1 må gjerast på nytt.
3. **Hovudkortet D09.** ATtiny1616 styrte berøring og PWM. Kven som les USB-C og styrer ladinga når micro:bit tek over, er ikkje avgjort.
4. **Festet.** Kortet og rista må følgje innmaten ned gjennom toppen. Braketten i chassiset D02 er ikkje teikna. Kontrollert: omhyllinga av kortet (52 × 13 × 43 mm bak veggen) kolliderer ikkje med nokon del i rev. B.
5. **Toleransen** på LED-plasseringa er ikkje oppgjeven. Bor eit prøvestykke først.

## Filer

| Fil | Innhald |
|---|---|
| `plassering.png`, `plassering.py` | stamma framanfrå og snitt gjennom matrisa og knappen |
| `d15_lysrist.py`, `.step`, `.stl` | lysrista, kontrollert mot LED-ane og knapp A og B |
| `sveip_mikrobit.py` | fastvara |
| `../overflate/bilete/` | V9, V10 og V11 med matrisa, og nærbilete |
