# formsok: fotonsporar og seks frø

Dato: 13.11.2026. Mappa hadde to filer som aldri var køyrde. Dei er no prøvde og har fått ei køyrefil.

| Fil | Kva ho gjer |
| --- | --- |
| `motor.py` | Seks konseptfrø (Rull, Vend L, Vend R, Perle, Klaff, Tavle) som delar, lyskjelder og massar, og `kropp()` med masse, tyngdepunkt, veltevinkel og fotavtrykk |
| `lys.py` | Fotonsporar: same foton gjev tala og biletet. Matt og satinert flate, holspegel, lys i lufta |
| `kjor.py` | Ny. Køyrer alle frøa, lagar par-bilete og kryssjekkar mot lysmotoren |

```
python kjor.py                  tal for alle frø og modusar, til tal.md
python kjor.py bilete vend_r    stemning og arbeid med lys i lufta
python kjor.py kryss            kryssjekk mot ../lysskisse
```

## Kva prøvinga viste

- **Begge filene køyrer.** Alle seks frøa går gjennom i alle tre modusane.
- **Sporaren og lysmotoren er samde.** Vend R, same geometri, per 100 lm frå kjelda:

| | Felt, lx | Jamnheit | lm på feltet | Mot auget, cd/m² |
| --- | --- | --- | --- | --- |
| Arbeid, fotonsporar | 154,5 | 0,17 | 37,1 | 208 |
| Arbeid, lysmotor | 149,3 | 0,18 | 35,8 | 203 |
| Stemning, fotonsporar | 40,6 | 0,34 | 9,8 | 1093 |
| Stemning, lysmotor | 42,9 | 0,37 | 10,3 | 1151 |

  To modellar skrivne uavhengig av kvarandre, den eine med tilfeldige foton og den andre med fliser og lober, ligg innanfor 3 til 6 %. Det er den sterkaste kontrollen prosjektet har på lystala så langt. Ingen av dei er målingar.

- **Feil 1, retta:** `bilete()` kræsja når laptopen ikkje var det same objektet som i `spor()`. Han toler det no, men bruk same objekt, elles blir laptopen svart.
- **Feil 2, i bruken:** med laptopen i sporinga får alle frøa jamnheit 0,00, fordi han ligg oppå arbeidsfeltet og tek fotona. `kjor.py` reknar tala utan laptop og biletet med.
- **Manglar:** Perle har same lys i stemning og arbeid (berre møte skil seg ut). Rull, Vend L og Vend R har same lys i stemning og møte.

## Kva som skil denne frå `../lysskisse`

| | `formsok` | `lysskisse` |
| --- | --- | --- |
| Metode | fotonsporing, tilfeldig | fliser og lober, eksakt |
| Fart | 5 til 10 s per tilstand | om lag 1 s per tilstand |
| Rom | bord, vegg, laptop | bord, vegg, tak, skjerm, brukar |
| Lampa lyser på seg sjølv | ja, seks sprett | nei |
| Lys i lufta | ja | nei |
| Bøygd og klipt ark | nei, berre skive og holspegel | ja |
| Bruk | kontroll og bilete av strålen | søk i formfamiliar |

Bruk lysmotoren til å søkje, og sporaren til å etterprøve det søket finn og til bilete der strålen skal synast.

## Det som ikkje er gjort

- Rommet er ikkje det same som i `../lysskisse` (laptop i staden for skjerm, lampa til venstre, auget ved bordkanten). Tal frå dei to kan berre samanliknast når geometrien er sett lik, slik `kjor.py kryss` gjer.
- Frøa er frå 12.11, før lysbrettet. Funna derifrå (stemninga må lånast, skjermen skuggar, arbeidsmodusen treng eit veggstrøk) er ikkje bygde inn i dei.
- Ingen av dei tre nye delane (bøygd ark, klipt ark, fresnelspegel) finst i sporaren.
