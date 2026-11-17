# Konsept B · formrevisjon B i Blender

Biletet frå 17. november er visuell referanse. Dette er ei eiga formstudie og Blender-scene, ikkje ei ny produksjonsverifisert STEP-samanstilling.

- `B_tilta_skive_revB.blend`: redigerbar Blender 5.3-scene med namngjevne separate objekt, materiale, lys og kamera.
- `01_B_revB_hero.png`, `02_B_revB_front.png`: to separate Cycles-renderingar.
- `../blender_revB.py`: reproducerbar byggje- og renderkode.

Forma avvik frå RevA på fire punkt: mjukt forma skål under ei nesten rund, samanhengande toppflate; J-forma sokkel med samanhengande konkav overgang; smal lysåpning i staden for lys langs heile frontkanten; indirekte varmt baklys bak venstre kant.

**Grense:** Blender-scena er ei form- og materialstudie. Lysåpninga er ei separat visuell overflatemodell som følgjer fronten av underskåla, men er ikkje eit produksjonstilpassa utsnitt i STEP-skallet. STEP RevA er uendra. Før produksjon krevst oppdatert CAD, toleransar, mekanisk hengsel, stabilitetsløysing, kjøling, reelle LED/drivar/batteri og fotometri.

Køyr frå prosjektmappa på Windows:

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.3\blender.exe" --background --python blender_revB.py
```
