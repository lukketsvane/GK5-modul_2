# Konsept B: Tilta skive · Northern

Parametrisk CAD-samanstilling frå eitt perspektivbilete, revisjon A (17.11.2026).

**Prosjektplassering:** `GK5-modul_2/konsept/B-tilta-skive/`. Dette er det nye, biletrefererte **konsept B**, ikkje det eldre «B Over» i `konsept/tre/` med fresnelplate over skjermen. Den eldre undersøkinga skal ikkje skrivast over.

## Innhald

- `B_tilta_skive_revA_assembly.step`: full samanstilling, separate namngjevne delar.
- `parts/`: STEP per del, STL for utvalde prototypeflater. Skruar og elektronikkvolum er forenkla.
- `generate_cad.py`: parametrar og geometri, i mm. Køyr med Python 3.11+ og CadQuery 2.8.
- `validate_cad.py`, `validation.json`, `checks.json`: solidvalidering, kollisjonar, vippesveip, massar og velting.
- `BOM.csv`: material, prosess og funksjon for kvar del.
- `astra_6_2_max_review.md`: kritisk gjennomgang frå `gpt-6.2-astra`, `max`.
- `previews/`: visingar og eksplodert modell. Illustrasjonar av CAD, **ikkje lysmålingar**.
- Originalbiletet ligg i den separate ZIP-pakka frå samtalen, ikkje i Git-repoet. Ingen mål vart avlesne frå biletet.

## Foreløpige konstruksjonsmål

| Parameter | Verdi |
| --- | --- |
| Toppdiametrar, ellipse | 324 × 264 mm |
| Skivehelling | 33°, tillaten vippesone i modellen 15–37° |
| Skive-/vippemidte | (30, 0, 158) mm, (-77, 0, 207) mm |
| Sokkel | 196 × 118 × 27 mm |
| Minste avstand hovud til bord ved 33° | 62 mm |
| Skråstilt metalltopplokk | 1,1 mm aluminium |
| Hovud + oppheng, rekna | 0,71 kg |
| Total masse, rekna | 1,64 kg |
| Statisk hengselmoment frå eigevekt, rekna | 0,74 Nm |

### Konstruksjon

Det store synlege toppskalet er éin skjerma plate. Undersida inneheld separat metallramme, diffusor for arbeidslys, indirekte frontspalte og bakre halo. Ein dobbel yoke på M5-aksel koplar skiva til den hòle stolpen. Mekaniske stopp er skisserte for 15–37°; faktisk friksjon, moment og levetid må testast. Stolpen er skrudd frå innsida av sokkelen med to M4. Den avtakbare botnluka gjev tilkomst til batteri, drivkort, USB-C og ballast. Diffusorane er utskiftbare utan å øydeleggje metallskalet.

## Verifisering

- **Bestått i CAD:** Alle 31 namngjevne delar er éin gyldig solid kvar. Prøvesveip 15, 20, 25, 30, 33 og 37° utan kollisjon mellom hovud, stolpe eller sokkel ved nominelle mål. Også kontrollert til 45° for frie volum.
- **Ikkje bestått:** Maks 1,2 kg frå briefen. Berekningsmodellen gjev 1,64 kg, utan endeleg kabel, drivarkrets og produksjonstoleransar.
- **Ikkje bestått:** Motstand mot 10 N horisontalt dytt i hengselhøgda. Krevd moment 2,07 Nm, gjenopprettande moment frå den vesle foten om lag 0,92 Nm. Teoretisk velting rundt 4,5 N for verste retning. Om 10 N er obligatorisk, trengst ei dokumentert bordklemme eller vesentleg større/tungare sokkel.
- **Ikkje verifisert:** Lysfordeling, blending og skjermrefleksar, varmeveg, straumforsyning, lading/batterisikkerheit, boltforbelasting, kabel bøyeradius, toleransekjeder, 500+ syklusar i hengsel, produksjonskost, samsvar med produktstandardar.

## Før produksjonsfrigjeving

1. Vel faktiske LED-, batteri-, USB-C- og drivardelar med datablad. Utarbeid elektrisk skjema, vernekrets, varmegrensesnitt og kabelføring gjennom leddet.
2. Løys velt/vekt-konflikten. Verifiser direkte i prototype med kraftmålar og aktuell bordflate.
3. Bygg éi fungerande lysrigg. Mål luks på 600 × 400 mm, luminans i auga, skjermrefleksar, flimmer, lysspekter og overflatetemperatur ved full last.
4. Test hengseldreiemoment, eigenvekt, utilsikta rørsle, minimumsgap, leddkabelfatigue, toleransar og servicehandlingar.
5. Få mekanisk, elektrisk, optisk og regelverksmessig godkjenning før noko blir kalla produksjonsklart.

**Status:** produksjonsretta, parametrisk **revisjon A for prototype**, ikkje produksjonssertifisert CAD. Påstanden om 350 lx, CRI 90, låg blending, 4 timar batteri eller sikker elektrisk drift er ikkje dokumentert av desse filene.