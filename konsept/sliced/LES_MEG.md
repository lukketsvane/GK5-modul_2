# sliced: konsept skorne med slicerman

Dato: 18.11.2026. Lampekroppar laga som plater med halvt-i-halvt-spor i motoren til slicerman (repoet `slicer.iverfinne.no`), køyrd utan nettlesar. Kvar kropp er ei prosjektfil appen opnar, og dei fire Northern-designa har skjerefiler.

| Mappe | Kva som ligg der |
| --- | --- |
| `northern/` | Fire design mot briefen. Éi handling: snu kula. Holet opp og bak er stemning, holet ned er arbeid |
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

I kvar mappe:

- `stemning-arbeid.png`: begge stillingar, i dagslys og i mørkt rom.
- `prosjekt-stemning.zip` (og `prosjekt-arbeid.zip` for nr. 1): opne i appen med trykk på kroppsnamnet i topplina, `fil`, vel zip-fila.
- `skjerefiler/`: ark som DXF, SVG og PNG. `fin/` er dei same arka med finare sporbotn, og det er dei som skal skjerast. `ekstra-bukk1` og `ekstra-bukk2` er bukken. `montering.txt`, `deler.csv`, `reglar.txt`, `passprove.svg` og `samla.glb` kjem frå motoren.

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
