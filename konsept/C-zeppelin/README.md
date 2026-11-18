# Konsept C: zeppelin

**Ny hovudvariant:** Sjå `to-ror/` for mekanismen med to langsgåande, parallelle og motroterande rør. Den eldre tannstongmodellen under er supersedert.

Mekanisk demonstrator for eit utfaldande, horisontalt bordlys inspirert av referanserendringen. Dette er eit proof of concept, ikkje produksjonsgodkjend CAD.

## Funksjon

Ni lamellstasjonar står på 40,84 mm senteravstand langs ein 376 mm lang rygg. Kvar stasjon har to plater på felles Ø5 mm stålaksel. Ein modul-1-pinjong med 20 tenner blir driven av éi lineært ført tannstong. Eit sidegrep roterer alle stasjonane frå 38° (samanlagt) til 10° (spreidd). Total lineær slaglengd er 4,887 mm.

Plater er modellerte som 0,6 mm laserskjerbare, sylindrisk bøygde flater, med 6,5 mm bøy ved ytterkantane, fire forskovne djupnelag og innsnevring kring akslingane. Hovudlyset er meint å vere fast montert under ryggen. Lamellane endrar sideopning og stemningslys. Flatene er ikkje dokumenterte å kunne regulere nedoverretta lys ved å rotere omkring y-aksen.

## Resultat

- `viewer.html`: lokal interaktiv 3D-vising med rotasjon, zoom, skyvekontroll og animasjon. Opne fila direkte, med `three.min.js` i same mappe.
- `renders/closed_3q.png`, `open_3q.png`, `closed_front.png`, `open_front.png`: ekte Blender 5.3-rendringar av CadQuery-modellen.
- `renders/Blender_kinematikk.gif`: 25 Blender-rendringar samla til ein animasjon.
- `C_zeppelin.blend`: redigerbar Blender-scene med den same CAD-geometrien og nøkkelrammer.
- `samansetjingar/lukka.step`, `mellom.step`, `open.step`: samansetjingar i tre stillingar.
- `delar/`: STEP for individuelle delar.
- `build.py`: parametrisk konstruksjon og eksport.
- `verify_final.py`, `verification_motion.json`: kollisjonskontroll for næraste lamell, nabofeste og naboaksel.
- `validation.json`: CAD-geometrisk oppsummering.
- `astra_6_2_xhigh_review.md`: teknisk vurdering frå `gpt-6.2-astra` via API med `reasoning.effort=xhigh`.

## Verifisert

CadQuery eksporterer tre STEP-samansetjingar og partmodellar, og alle genererte solids er gyldige. Ved 10°, 24° og 38° er minste målte avstand til naboplate 9,95 mm, til nabofeste 8,10 mm og til naboaksel 6,68 mm. Desse kontrollane gjeld utvalde geometripar, ikkje full toleransesjekk. Den analytiske grensa for avstand til næraste naboaksel er undersøkt frå 10° til 38° med steg 0,1°. Den digitale utsveipen vart kontrollert i 2° steg og held seg innanfor 384,82 × 152,59 × 201,13 mm. Stoppar på tannstonga ligg om lag 0,1 mm utanfor nominelle endeposisjonar.

## Gjenstår

Før fysisk konstruksjon: produser tre midtstasjonar, kontroller samankopling og tilspenning av settskruar, backlash, føringar, tannprofil, toleranseopphoping, vriding og platefjøring. Kontroller ballast og velt ved handkraft på knotten, varme frå LED, elektrisk tryggleik og klemfare. Ein rørsleanimasjon dokumenterer ikkje at dette er produksjonsklart.

## Regenerering

Frå denne mappa med Python 3.13 og CadQuery installert:

```powershell
py -3.13 build.py
py -3.13 verify_final.py
py -3.13 generate_viewer.py
py -3.13 render_motion.py
& 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe' --background --python render_blender.py
```
