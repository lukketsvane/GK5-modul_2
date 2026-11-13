# Kontroll: demo

Alt er rekna, ikkje målt. Måla på delane frå settet er anslag frå foto, og massane er usikre til delane er vegne.

## Masse

| Del | Slag | Gram | ± | Kjelde |
| --- | --- | --- | --- | --- |
| fot | print | 142 | 21 | rekna: PETG, vegg 1,2 mm og 15 % fyll (ANTAKING), massiv 410 g |
| hylse | print | 40 | 6 | rekna: PETG, vegg 1,2 mm og 15 % fyll (ANTAKING), massiv 54 g |
| ballast | kjopt | 604 | 60 | oppgjeven |
| arm | sett P01 | 184 | 64 | rekna frå volum, mål anslått frå foto; rekna som skal, vegg 2,5 mm (ANTAKING), tettleik ANTAKING |
| nav | print | 7 | 1 | rekna: PETG, vegg 1,2 mm og 15 % fyll (ANTAKING), massiv 14 g |
| kjoleplate | kjopt | 42 | 4 | oppgjeven |
| led | kjopt | 5 | 0 | oppgjeven |

Samla 1025 g ± 91 (rekna; ± er ANTAKING: 35 % på delar frå settet, 15 % på trykte, 10 % på kjøpte). Kravet F8 er høgst 1 200 g: held. Tyngdepunkt (-3, -3, 52) mm. Ytre mål 181 × 205 × 334 mm.

Armprofilen (P01) er merkt aluminium i `modell/byggjesett/delar.py`, medan oppdraget kallar han stål. Er han stål, veg lampa 1266 g ± 162 (F8: held ikkje), tyngdepunktet ligg i (-2, -2, 68) mm, og ho toler 3,2 N dytt i arbeidsstillinga. Prøv med ein magnet og vei armen: set `vekt_g=` i `sett()`.

## Kollisjon og velt langs gesten

| t | Kollisjonar | Dytt som veltar (N) | Retning | Held 5 N | Veltevinkel | Fot cm² |
| --- | --- | --- | --- | --- | --- | --- |
| 0,00 | ingen | 2,6 (lett 2,4) | 140° | nei | 59° | 254 |
| 0,25 | ingen | 2,6 (lett 2,4) | 160° | nei | 60° | 254 |
| 0,50 | ingen | 2,6 (lett 2,4) | 190° | nei | 60° | 254 |
| 0,75 | ingen | 2,6 (lett 2,4) | 215° | nei | 60° | 254 |
| 1,00 | ingen | 2,6 (lett 2,4) | 220° | nei | 59° | 254 |

Dyttepunkt i arbeidsstillinga: (0, -0, 334) mm. Lampa glir ved om lag 4,0 N (friksjon 0,4, ANTAKING). Kravet F9 er høgst 200 cm² fot: held ikkje.

Ekstra kraft: t 0,00: inf N; t 0,25: inf N; t 0,50: inf N; t 0,75: 57,5 N; t 1,00: 22,9 N.

## Varme

| LED | Watt | Ligg mot | Kjøleflate cm² | Temperatur °C | Råd |
| --- | --- | --- | --- | --- | --- |
| led | 5,00 | kjoleplate | 161 | 47 | Held: om lag 47 °C ved 5,0 W på 161 cm² metall (grense 78 °C for PETG). |

Rekna, ikkje målt. ANTAKING: 70 % av watten blir varme, flata gjev frå seg 10 W/m²K, rommet held 25 °C. Trykt PLA mjuknar ved 55 til 60 °C.

## Trykte delar (Bambu Lab P1S, 256 × 256 × 256 mm)

| Del | Plast | Mål på plata mm | Passar | Overheng cm² | Gram | Merknad |
| --- | --- | --- | --- | --- | --- | --- |
| fot | PETG | 180 × 180 × 16 | ja | 0 | 142 | ok |
| hylse | PETG | 69 × 89 × 45 | ja | 0 | 40 | ok |
| nav | PETG | 24 × 52 × 15 | ja | 0 | 7 | ok |

Gram er rekna med 1,2 mm vegg og 15 % fyll (ANTAKING).

## Tryggleik

- P04 (straumforsyninga, 230 V) og elektronikken hennar er ikkje med og skal aldri brukast.
- Fresnelspegelen og linsene må aldri stå i sol: dei samlar sollyset og kan tenne papir.
- LED-ar skal liggje på metall eller ha ein varmeveg. Trykt PLA mjuknar ved 55 til 60 °C.
