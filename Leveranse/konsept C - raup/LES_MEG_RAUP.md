# RAUP · CAD-prototyp

Original FBX er geometrisk rekonstruert som parametrisk B-rep. Skala er sett frå ei antaking om 270 mm maksimal høgd.

`cad/*.step`: ytre kropp, bøygd filmplate, førebels kjerne, formhalvdelar, filmklips, LED-berar.

`produksjon/*.stl`: maskinlesbare prototypeksportar. `produksjon/raup_diffusor_1til1.dxf`: utbreidd film på mm-skala (ca 198 mm breidd).

**Ikkje enno produksjonsgodkjent:** Kjerne og ytre kropp er gyldige kvar for seg, men endeleg uthola BRep skal ikkje reknast som verifisert. Formfrigjering,  materialkrymp, papirvegg, lys, varme, stabilitet, elektrosikkerheit og filmens kjemiske samansetjing krev fysiske prøvar. Ikkje laserskjer ukjend monitorfolie. Klips og LED-berar er førebelse, ikkje montert eller lastprøvd.

Skriptet kan køyrast på ny med `py -3 cad/raup_produksjon.py` i `raup`-mappa. Endringar utanfor denne mappa er ikkje nødvendige.
