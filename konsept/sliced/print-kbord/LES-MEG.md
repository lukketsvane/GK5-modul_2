# Bordkula på Bambu Lab P1S

Bordkula (kbord), skalert så kvar plate får plass på byggjeplata (256 × 256 mm): kula er 237 × 238 mm, 199 mm djup, med vogga under. Platene er 3 mm. Skoren av motoren i slicerman, med alle harde reglar haldne.

## Filene

| Fil | Kva |
| --- | --- |
| `00-passprove.3mf` | Skriv ut denne fyrst: ein kam med sju spor og ei tunge på 3 mm |
| `plater/kbord-plate-1.3mf` … `-8.3mf` | Dei tolv platene, éi byggjeplate per fil, alt plassert innanfor plata |
| `plater/kbord-plate-9-vogge.3mf` | Vogga kula ligg i, éin del, 12 mm høg |
| `montering.txt` | Rekkjefylgja frå motoren |
| `plater-oversyn.png` | Kva som ligg på kvar plate |
| `kbord-240.png` | Lampa i denne storleiken |

Adressa (1–6, 21–26) er gravert 1 mm ned i toppflata på kvar plate.

## 1. Passprøve fyrst

Spora i platene er laga for 0,25 mm klaring: 3,25 mm breie for 3 mm plate. Kva som sit godt, avheng av filamentet og printaren.

1. Skriv ut `00-passprove.3mf` i same filament og med same innstillingar som platene.
2. Skyv tunga ned i spora. Frå venstre er dei 3,10 · 3,15 · 3,20 · 3,25 · 3,30 · 3,35 · 3,40 mm (det smale sporet er ved det skrå hjørnet).
3. Det rette sporet tek tunga med fast tommeltrykk og held henne utan slark.
4. Er det 3,25: skriv ut. Er det eit anna: seg kva for eit, så lagar eg platene på nytt.

## 2. Innstillingar i Bambu Studio

- **Filament:** PETG (Bambu PETG HF eller Basic). PLA mjuknar ved om lag 60 °C, og platene ved lampehaldaren vert varme.
- **Profil:** 0,20 mm Standard, 0,4 mm dyse. 3 mm vert nøyaktig 15 lag.
- **Vegger og fyll:** 3 vegglinjer, 4 topplag og 4 botnlag, 25 % gyroid.
- **Støtte og brim:** ingen. Platene ligg flate og har inga overheng.
- **Plate:** Textured PEI. Bruk limstift på glatt PEI med PETG, så delane slepp.
- **Kompensasjon:** la «elephant foot» stå på standard (0,15) og «X-Y hole compensation» stå på 0. Klaringa ligg i fila.
- **Opning:** importer kvar fil på si eiga byggjeplate. Svar «nei» om Bambu Studio spør om å laste delane som eitt objekt. Delane står alt der dei skal.

Samla filament: om lag 0,7–0,8 kg PETG (heilt solid ville det vore 0,97 kg). Ha ei heil rull på 1 kg. Bambu Studio gjev eksakt tal og tid.

## 3. Det du må kjøpe

- E27-lampehaldar med **ytre gjenge Ø40 mm** og **to skjermringar** (om lag Ø57). Gjenga går gjennom den firkanta kanalen mellom dei fire midtplatene (3, 4, 23, 24), som er 40,3 mm brei. Ringane klemmer den 12 mm breie kragen frå kvar side.
- Tekstilleidning, 2 × 0,75 mm², med brytar og stikkontakt.
- LED-pære, opal, 2700 K, **høgst 8 W**:
  - A60 gjev om lag 40 mm luft til platene.
  - G95 (globe, som på biletet) gjev 25 mm luft, akkurat på grensa.

## 4. Montering

1. Følg `montering.txt`. Ståande plater fyrst: 1–6, med adressa same veg. Skyv så 21–26 inn éin og éin, langs lampeaksen, i den rekkjefylgja fila seier.
2. Lampehaldaren går inn bakfrå gjennom brønnen i toppen av kula (Ø62). Gjenga skal gjennom kanalen mellom 3, 4, 23 og 24. Skru den eine ringen på frå innsida gjennom framopninga, og stram den andre frå brønnen.
3. Leidningen går ut bak gjennom brønnen. Bruk strekkavlastinga i lampehaldaren.
4. Skru i pæra gjennom framopninga (Ø148) og legg kula i vogga. Kula kan dreiast i vogga, så lyset går dit du vil.

## Ikkje prøvd

- Ingenting er skrive ut. Passprøva er det einaste svaret på om 0,25 mm sit.
- Varmen rundt lampehaldaren er ikkje målt. PETG og høgst 8 W LED er det trygge valet.
- Kanalen for gjenga er 40,3 mm. Er gjenga på lampehaldaren din grovare enn Ø40, går ho ikkje inn. Mål før du kjøper.
- Om kula ligg stødig i vogga, er ikkje prøvd.
