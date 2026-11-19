# RAUP · Produksjonsklar CAD-samanstilling (1:1 mm)

Parametrisk Class-A B-rep (NURBS grad ≤ 3, utan voksling) i kompakt **1:1-skala** med **200,0 mm** total lampehøgd (bordplate → topp av diffusor).

## Hovudleveranse (prioritert ope-botn hovudskal)
- `cad/raup_skal.step` (**839 KB**, 11 Class-A-flater, `BRepCheck_Analyzer = True`, attlest STEP gyldig)
- `produksjon/raup_skal_P1S.stl` (**6,5 MB**, høg presisjon, 0 opne/ikkje-manifold kantar)
- `print/RAUP_P1S_H200_2.5mm_fuzzy.3mf` (**31,9 MB**, offisiell ferdig-slica Bambu Studio `02.08.04.57` P1S-prosjektfil med verifisert G-kode — klar til utskrift):
  - **Eksakt 1:1 mm skala**: `143,26 × 126,43 × 145,62 mm` (`transform = 1:1`, sentrert på `256 × 256 mm` P1S-plate ved `z = 0,000 mm`)
  - **Veggtjukkleik og print**: **2,5 mm** jamn vegg med open botn (`6` veggliner, `arachne`, `0 %` fylling, `0,16 mm` laghøgd, `Bambu PLA Matte`, `~218,9 g` inkl. tre-støtte frå plata, `7 t 29 m`)
  - **Overflatestruktur**: Bambu Studio **Fuzzy Skin (`external` / Contour)** på yttervegg (`thickness = 0,10 mm`, `point_distance = 0,25 mm`, `first_layer = off`) for matt papirmasse-/steinstruktur — stadfesta aktiv i slica G-kode

## Komplett samanstilling (`cad/raup_assembly.step`, 8 delar, 0 kollisjonar)
- `cad/raup_skal.step` — ope-botn hovudskal (2,5 mm vegg; papirmasse ~105 g / PLA ~200 g)
- `cad/raup_botn_chassis.step` — botnchassis med 0,40 mm registreringsflens, 1,40 mm boga diffusorspor, kabelutgang og 3× M3-hol
- `cad/raup_ballast.step` — 5 mm S235 stålballastplate (veltevinkel **51,9°** papir / **46,6°** PLA; krav EN 60598 ≥ 6°, Northern ≥ 15°)
- `cad/raup_batteri_21700.step` — brukarutskiftbar 18650 Li-ion-celle (Ø18,4 × 65,2 mm)
- `cad/raup_drivar_pcb.step` — drivar-/dimmar-/USB-C-modul (32 × 14 × 5 mm)
- `cad/raup_led_berar.step` — vertikal eloksert aluminiums LED-kjølesøyle
- `cad/raup_diffusor.step` + `produksjon/raup_diffusor_1til1.dxf` — avviklingsbar 1,0 mm optisk filmplate (`L = 139,5 mm`, `R_min = 37,2 mm`, ≥ 1,38 mm klaring til kropp)
- `cad/raup_filmklips.step` — boga styreklips med 1,60 mm ikkje-klemmande spor
- `cad/raup_stoypform_minus_Y.step` & `cad/raup_stoypform_pluss_Y.step` — todelt støypeform for papirmasse med styringspinnar

## Verifisering og køyring
Alle maskinelle kontrollar er logga i `kontroll/raup_CAD_verifisering.json`, `kontroll/raup_skal.json` og `kontroll/raup_BOM.csv`:
- Alle 11 STEP-delar + samanstilling bestod `BRepCheck_Analyzer` og STEP-attlesing.
- **0 kollisjonar** (`0,0000 mm³` overlapp på alle 28 par).
- **Fysisk test står att**: papirmasse-krymp/slepp i form, varmetoleranse på ombrukt monitorfolie, faktisk lux-/temperaturmåling og CE / EN 60598 / IEC 62133-tryggleik.

Køyr på ny (valfri vegg- og høgdeparameter i mm):
```bash
py -3 cad/raup_produksjon.py 2.5 200.0
py -3 cad/raup_skal.py 2.5 200.0
```
