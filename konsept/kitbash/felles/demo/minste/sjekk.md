# Kontroll: minste

Alt er rekna, ikkje målt. Måla på delane frå settet er anslag frå foto, og massane er usikre til delane er vegne.

## Masse

| Del | Slag | Gram | ± | Kjelde |
| --- | --- | --- | --- | --- |
| fot | print | 178 | 27 | rekna: PETG, vegg 1,2 mm og 15 % fyll (ANTAKING), massiv 551 g |
| arm | sett P01 | 184 | 64 | rekna frå volum, mål anslått frå foto; rekna som skal, vegg 2,5 mm (ANTAKING), tettleik ANTAKING |
| plate | kjopt | 39 | 4 | oppgjeven |
| led | kjopt | 5 | 0 | oppgjeven |

Lampa veg 406 g (rekna; ± 70 er ANTAKING: 35 % på delar frå settet, 15 % på trykte, 10 % på kjøpte). Kravet F8 er høgst 1 200 g: held. Tyngdepunkt (-0, -5, 123) mm. Ytre mål 180 × 190 × 336 mm.

Armprofilen (P01) er merkt aluminium i `modell/byggjesett/delar.py`, medan oppdraget kallar han stål. Er han stål, veg lampa 647 g ± 151 (F8: held), tyngdepunktet ligg i (-0, -3, 128) mm, og ho toler 1,8 N dytt i arbeidsstillinga. Prøv med ein magnet og veg armen: set `vekt_g=` i `sett()`.

## Kollisjon og velt langs gesten

| t | Kollisjonar | Dytt som veltar (N) | Retning | Held 5 N | Veltevinkel | Fot cm² |
| --- | --- | --- | --- | --- | --- | --- |
| 0,00 | ingen | 1,1 (lett 0,9) | 265° | nei | 35° | 254 |
| 0,25 | ingen | 1,1 (lett 0,9) | 265° | nei | 35° | 254 |
| 0,50 | ingen | 1,1 (lett 0,9) | 265° | nei | 35° | 254 |
| 0,75 | ingen | 1,1 (lett 0,9) | 265° | nei | 35° | 254 |
| 1,00 | ingen | 1,1 (lett 0,9) | 265° | nei | 35° | 254 |

Dyttepunkt i arbeidsstillinga: (0, 0, 308) mm. Lampa glir ved om lag 1,6 N (friksjon 0,4, ANTAKING). Kravet F9 er høgst 200 cm² fot: held ikkje.

## Varme

| LED | Watt | Ligg mot | Kjøleflate cm² | Temperatur °C | Råd |
| --- | --- | --- | --- | --- | --- |
| led | 5,00 | plate | 151 | 48 | Held: om lag 48 °C ved 5,0 W på 151 cm² metall (grense 78 °C for PETG). |

Rekna, ikkje målt. ANTAKING: 70 % av watten blir varme, flata gjev frå seg 10 W/m²K, rommet held 25 °C. Trykt PLA mjuknar ved 55 til 60 °C.

## Trykte delar (Bambu Lab P1S, 256 × 256 × 256 mm)

| Del | Plast | Mål på plata mm | Passar | Overheng cm² | Gram | Merknad |
| --- | --- | --- | --- | --- | --- | --- |
| fot | PETG | 180 × 180 × 56 | ja | 0 | 178 | ok |

Gram er rekna med 1,2 mm vegg og 15 % fyll (ANTAKING).

## Tryggleik

- P04 (straumforsyninga, 230 V) og elektronikken hennar er ikkje med og skal aldri brukast.
- Fresnelspegelen og linsene må aldri stå i sol: dei samlar sollyset og kan tenne papir.
- LED-ar skal liggje på metall eller ha ein varmeveg. Trykt PLA mjuknar ved 55 til 60 °C.
