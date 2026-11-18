# Konsept C | fototru ribbelampe R07

Utgangspunkt er referansefotoet av ei vertikal sandfarga bordlampe med lange overlappande ribber kring ein varm diffusor. R07 er ein parametrisk CadQuery-modell og Blender-rendring, ikkje eit fotografisk eller produksjonsteknisk identisk objekt.

## Konstruksjon
- 8 separate krumma og lofta PETG-ribber, delte i fire spegla par
- Opal diffusor, separat aluminiumskjerne, låg sokkel og plass for ballast
- Omtrent 220 mm høgd, 117 mm breidd, sokkel ca. Ø58,6 mm
- Ribbene er laga med tett samplede, rette mellomseksjonar for å unngå loftartefaktar
- Separate STEP/STL-filer og montert STEP-samling i ZIP

## Visuell verifikasjon
- `renders/01_actual_CAD_reference_camera.png` er faktisk Blender/Cycles-render av CAD-geometrien i referansekamera, ikkje biletgenerering
- `renders/02_actual_CAD_threequarter.png` viser trekvart perspektiv av same geometri
- Kanten i front er samanlikna mot éitt originalfoto; medianavvik om lag 5 px i valde snitt etter normalisering
- Dette målet seier ikkje at ribbene, bakside, materialet eller fotometrien er identiske

## Mekaniske avgrensingar
Ribbene er lukka einpartssolider og STL passar innanfor Bambu P1S sitt byggevolum. Den faktiske passforma til stolpar og sokkelspor, skruar, tetting, stabilitet, LED-varme, elektrisk sikkerheit og blendingsnivå er ikkje fysisk verifiserte. Utfør prøvemontering og termisk/optisk test før funksjonell bruk.

## Reproduksjon
`python build.py` skriv STEP/STL, og `blender -b -P blender_render.py` skriv begge produktbileta. Renderkvaliteten er ikkje designgodkjenning.
