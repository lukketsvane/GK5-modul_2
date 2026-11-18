# sliced: konsept skorne med slicerman

Dato: 18.11.2026. Lampekroppar laga som plater med halvt-i-halvt-spor i motoren til slicerman (repoet `slicer.iverfinne.no`), køyrd utan nettlesar. Kvar kropp er ei prosjektfil appen opnar, og dei fire Northern-designa har skjerefiler.

| Mappe | Kva som ligg der |
| --- | --- |
| `northern/` | Fire design mot briefen. Éi handling: snu kula. Holet opp og bak er stemning, holet ned er arbeid |
| `spegl/` | Seks design med spegelakryl mot innsida og éin matt farge ut, kvart i stemning og arbeid |
| `kula-studie/` | Formstudien før: kule A til I, pendelen (F) og bordkula, som prosjektfiler og to oversynsark |
| `oversyn/` | Tavlene: dei fire Northern-designa, ni kulevariantar, kulene opna i appen, og prosessen fram til kula |
| `kjelde/` | Koden som laga alt: `nord/` (Northern-designa), `kule/` (studien), `verkty/` (verktykassa rundt motoren) og `kart/` (kva motoren kan skjere) |

## northern

| Nr | Design | Plater | Ledd | Ark 600 × 400 | Vekt utan elektronikk | Høgd | Føtene innanfor |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Kule 220, bjørk 3 mm, 6 × 6 | 12 | 24 | 2 | 0,35 kg | 370 mm | 127 × 127 mm |
| 2 | Kule 220, opal akryl 3 mm | 12 | 24 | 2 | 0,61 kg | 370 mm | 127 × 127 mm |
| 3 | Kule 180, bjørk 3 mm | 12 | 24 | 2 | 0,23 kg | 285 mm | 106 × 106 mm |
| 4 | Kule 240, bjørk 3 mm, 8 × 8 | 16 | 52 | 3 | 0,61 kg | 405 mm | 134 × 134 mm |

### Globus (5 og 6)

Same kule, sett inn i formspråket frå `grunnlag/00-ramme.md` punkt 7: kule, tynn line og rund fot, éin matt farge, éin messingdetalj. Kula heng i ein bøyel og vert vippa om to messingtappar.

| Nr | Design | Plater | Ark 600 × 400 | Kula åleine | Høgd | Fot |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | Globus 180, 3 mm MDF, mørkegrøn eller gråbeige | 12 | 2 | 0,26 kg | 345 mm | Ø 150 (177 cm²) |
| 6 | Globus 220, 3 mm MDF, svart | 12 | 2 | 0,39 kg | 385 mm | Ø 158 (196 cm²) |

Bøyel, stilk, fot og messingtappar er berre teikna i bileta. Festet mellom tapp og kule er ikkje løyst, og det finst ikkje skjerefiler for Globus enno.

I kvar mappe:

- `stemning-arbeid.png`: begge stillingar, i dagslys og i mørkt rom.
- `prosjekt-stemning.zip` (og `prosjekt-arbeid.zip` for nr. 1): opne i appen med trykk på kroppsnamnet i topplina, `fil`, vel zip-fila.
- `skjerefiler/`: ark som DXF, SVG og PNG. `fin/` er dei same arka med finare sporbotn, og det er dei som skal skjerast. `ekstra-bukk1` og `ekstra-bukk2` er bukken. `montering.txt`, `deler.csv`, `reglar.txt`, `passprove.svg` og `samla.glb` kjem frå motoren.

## spegl

Platene er 2 eller 3 mm spegelakryl med spegelen inn mot lyset og den matte fargen ut. Ein kritikar las bileta mot `grunnlag/00-ramme.md` punkt 7 og `grunnlag/04-kravspesifikasjon.md`.

| Design | Idé | Plater | Ledd | Ark 600 × 400 | Skoren kropp | Kritikaren |
| --- | --- | --- | --- | --- | --- | --- |
| Måne 200 | Gråbeige kule av 8 + 8 tynne skiver i halvbøyel. Ytste skive på kvar side er eit flatt kinn som tappen går gjennom | 16 | 52 | 2 | 0,44 kg | 7,5 |
| Blunk | Halvkuleskal som vrir seg som eit augelok rundt ei fast opal kule på ei L-forma line | 12 | 24 | 1 | 0,34 kg | 7 |
| Rist | Matt trommel på tynn stilk. Spegelgitteret ligg skjult inni som blendingsraster under ein flat lysmodul | 10 | 21 | 1 | 0,16 kg | 6,5 |
| Perle 180 | Som Måne, mørkegrøn, 6 + 6 skiver, messingtappar | 12 | 24 | 2 | 0,41 kg | 5 |
| Blad | Linse av hellande blad med spegel på éi side, snudd over eit hengsel | 10 | 24 | 1 | 0,24 kg | 3,5 |
| Trakt | Kjegle som ligg laus i ein ring og vert snudd | 8 | 16 | 1 | 0,20 kg | 2 |

Neste grep kritikaren peika på: Måne treng ein opal lekam rundt kjelda, Blunk eit tettare skal (8 + 8), Rist hellande blad med spegel berre på sida som vender bort frå auget.

I kvar mappe: `stemning-arbeid.png`, `prosjekt-stemning.zip`, `prosjekt-arbeid.zip` og rapportane frå motoren. Det finst ikkje skjerefiler for desse enno.

Ikkje prøvd for `spegl/`: at spegelen ikkje kastar kjelda mot auget (F1), lux (F3, F6), samla vekt (F8) og velting (T2). Bøyel, stilk, fot, tappar, opalkule og trommelhus er berre teikna. Lysbileta følgjer 240 000 strålar gjennom opptil åtte spegelrefleksar og viser kvar lyset går, ikkje kor mykje. Meir om spegelen i teiknaren: `kjelde/kart/spegl.md`.

## Kva prøvinga viste

- **Alle fire held dei harde reglane** i begge stillingar: plana grip, delar finst, kan monterast, ingen klemmer, gods i leddet, får plass på arket.
- **1 og 3 viser skiljet tydelegast.** Lys på veggen i stemning, ein lyspøl på bordet i arbeid.
- **2 lyser som ei heil kule i begge stillingar**, så skiljet mellom stemning og arbeid vert lite.
- **4 fangar for mykje lys.** Gitteret er for tett for holet.

## Ikkje prøvd

- Ingenting er skore på maskin. Snittbreidd (0,2 mm) og klaring (0,1 mm) er gjettingar til passprøva er skoren.
- Lux på feltet (F3), blending (F1) og velting (T2) er korkje rekna eller målte. Bileta viser kvar lyset går, ikkje kor mykje. Dei er ikkje køyrde gjennom lysmotoren i `konsept/lysskisse`.
- Bukken og patronen er teikna utanfor motoren. Bukken ligg i `skjerefiler/`, men er ikkje med i prosjektfilene.
- Koden i `kjelde/` har faste stiar frå maskina ho vart køyrd på og må rettast før ho køyrer ein annan stad.
