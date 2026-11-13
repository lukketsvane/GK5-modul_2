# Generasjon 2: kva optikk gjev eit felt på bordet

Strålegangen er rekna i `familie.py` (tynn linse), ikkje i motoren. u: maske til linse. v': der biletet er skarpt (negativ: virtuelt). r: linse til flata. Skala: r / u. Kant: 10 til 90 % av lyskanten. lm/W: lumen ut per watt inn. Kompakt: maske og lengd innanfor Ø 16 x 27,5 cm.

| Lysgrep | t | Optikk | u, mm | v', m | r, m | Skala | Maske Ø, mm | Kant, mm | lm/W | Lengd, mm | Breidd, mm | Kompakt | Ledd | Merknad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linse285 | 0 | linsa 285 + fresnelplata | 285 | uendeleg | 0.56 | 2.0 | 354 | 31 | 27.2 | 545 | 366 | nei | hale 0.90 x maske 0.44 x plate 0.85 x pupill 0.98 x linse 0.92 x étendue 1.00 x spegel 0.90 | kjelda 0.54 m over plata, maska er større enn plata |
| linse285 | 1 | linsa 285 + fresnelplata | 285 | uendeleg | 0.61 | 2.1 | 354 | 31 | 27.2 | 545 | 366 | nei | hale 0.90 x maske 0.44 x plate 0.85 x pupill 0.98 x linse 0.92 x étendue 1.00 x spegel 0.90 | kjelda 0.54 m over plata, maska er større enn plata |
| linse285-lupe | 0 | linsa 285 + fresnelplata | 150 | -0.32 | 0.56 | 3.7 | 187 | 133 | 21.6 | 600 | 285 | nei | hale 0.90 x maske 0.44 x plate 0.85 x pupill 0.70 x linse 0.92 x étendue 1.00 | kjelda 0.60 m over plata |
| linse285-lupe | 1 | linsa 285 + fresnelplata | 150 | -0.32 | 0.61 | 4.1 | 187 | 141 | 21.6 | 600 | 285 | nei | hale 0.90 x maske 0.44 x plate 0.85 x pupill 0.70 x linse 0.92 x étendue 1.00 | kjelda 0.60 m over plata |
| skugge-3 | 0 | skuggemaske, LED 3 mm | 100 | -0.10 | 0.56 | 5.6 | 124 | 14 | 15.7 | 120 | 136 | ja | maska slepper 0.14 |  |
| skugge-3 | 1 | skuggemaske, LED 3 mm | 100 | -0.10 | 0.61 | 6.1 | 124 | 15 | 15.7 | 120 | 136 | ja | maska slepper 0.14 |  |
| skugge-12 | 0 | skuggemaske, kjelde 12 mm | 100 | -0.10 | 0.56 | 5.6 | 124 | 54 | 15.7 | 120 | 136 | ja | maska slepper 0.14 |  |
| skugge-12 | 1 | skuggemaske, kjelde 12 mm | 100 | -0.10 | 0.61 | 6.1 | 124 | 59 | 15.7 | 120 | 136 | ja | maska slepper 0.14 |  |
| kort60 | 0 | produktlinse 60 mm | 67 | 0.61 | 0.56 | 8.4 | 83 | 13 | 30.8 | 112 | 95 | ja | hale 0.90 x maske 0.44 x kondensor 0.85 x linse 0.92 x étendue 1.00 |  |
| kort60 | 1 | produktlinse 60 mm | 67 | 0.61 | 0.61 | 9.2 | 83 | 13 | 30.8 | 112 | 95 | ja | hale 0.90 x maske 0.44 x kondensor 0.85 x linse 0.92 x étendue 1.00 |  |
| kort60-liten | 0 | produktlinse 60 mm, Ø 12 | 67 | 0.61 | 0.56 | 8.4 | 83 | 12 | 30.8 | 112 | 95 | ja | hale 0.90 x maske 0.44 x kondensor 0.85 x linse 0.92 x étendue 1.00 |  |
| kort60-liten | 1 | produktlinse 60 mm, Ø 12 | 67 | 0.61 | 0.61 | 9.2 | 83 | 13 | 30.8 | 112 | 95 | ja | hale 0.90 x maske 0.44 x kondensor 0.85 x linse 0.92 x étendue 1.00 |  |
| kort41 | 0 | produktlinse 41 mm | 44 | 0.61 | 0.56 | 12.8 | 55 | 13 | 30.8 | 89 | 67 | ja | hale 0.90 x maske 0.44 x kondensor 0.85 x linse 0.92 x étendue 1.00 |  |
| kort41 | 1 | produktlinse 41 mm | 44 | 0.61 | 0.61 | 13.9 | 55 | 13 | 30.8 | 89 | 67 | ja | hale 0.90 x maske 0.44 x kondensor 0.85 x linse 0.92 x étendue 1.00 |  |
| kort60-mjuk | 0 | produktlinse 60 mm | 51 | -0.32 | 0.56 | 11.1 | 63 | 68 | 30.8 | 96 | 75 | ja | hale 0.90 x maske 0.44 x kondensor 0.85 x linse 0.92 x étendue 1.00 |  |
| kort60-mjuk | 1 | produktlinse 60 mm | 51 | -0.32 | 0.61 | 12.1 | 63 | 73 | 30.8 | 96 | 75 | ja | hale 0.90 x maske 0.44 x kondensor 0.85 x linse 0.92 x étendue 1.00 |  |
| kort60-jamn | 0 | produktlinse 60 mm | 51 | -0.32 | 0.56 | 11.1 | 63 | 68 | 0.7 | 96 | 75 | ja | hale 0.90 x maske 0.44 x kondensor 0.85 x linse 0.92 x étendue 1.00 x gråfilter 0.02 |  |
| kort60-jamn | 1 | produktlinse 60 mm | 51 | -0.32 | 0.61 | 12.1 | 63 | 73 | 11.8 | 96 | 75 | ja | hale 0.90 x maske 0.44 x kondensor 0.85 x linse 0.92 x étendue 1.00 x gråfilter 0.38 |  |
| trakt60 | 0 | produktlinse 60 mm + trakt | 51 | -0.32 | 0.56 | 11.1 | 63 | 68 | 76.1 | 121 | 75 | ja | trakt og opning 0.85 x feltlinse 0.85 x linse 0.92 |  |
| trakt60 | 1 | produktlinse 60 mm + trakt | 51 | -0.32 | 0.61 | 12.1 | 63 | 73 | 76.1 | 121 | 75 | ja | trakt og opning 0.85 x feltlinse 0.85 x linse 0.92 |  |
| kule52 | 0 | glaskule Ø 70 | 57 | 0.61 | 0.56 | 9.9 | 71 | 21 | 30.8 | 137 | 83 | ja | hale 0.90 x maske 0.44 x kondensor 0.85 x linse 0.92 x étendue 1.00 |  |
| kule52 | 1 | glaskule Ø 70 | 57 | 0.61 | 0.61 | 10.7 | 71 | 21 | 30.8 | 137 | 83 | ja | hale 0.90 x maske 0.44 x kondensor 0.85 x linse 0.92 x étendue 1.00 |  |
