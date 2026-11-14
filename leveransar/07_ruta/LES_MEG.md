# Ruta, revisjon B: lysbilete, PDF, nettstad og 3D-fil

Dato: 14.11.2026, tredje utgåve. Alle bileta er no rendringar av CAD-modellen. Dei genererte bileta frå andre utgåve er tekne ut. Regelen er den same: lampa åleine på svart, eitt lys og éin biletstil, nesten ingen ord, og dei tekniske sidene som kvit strek. Alt blir bygd på nytt med `python lag.py`.

| Fil | Innhald |
| --- | --- |
| `Ruta-presentasjon.pdf` | tolv sider, 1127 × 797 px per side |
| `presentasjon.html` | same sider som lysbilete i nettlesaren. Piltastane blar, og sida fyller vindauget |
| `sider/side-NN.jpg` | kvar side som bilete, 2254 × 1594 |
| `../../ruta/index.html` | nettstaden, med modellen som kan dreiast og vippast |
| `../../ruta/3d/ruta.usdz` | 3D-fila til AR på iPhone og iPad. Éi fil per farge |
| `../../ruta/3d/ruta.glb` | 3D-fila til nettlesaren |
| `bilete/` | rendringane som er brukte, som JPEG |
| `lag.py` | byggjer alt. Tala kjem frå `konsept/film/cad/ut-b/kontroll.json` |

## Sidene

| | Side | Bilete |
| --- | --- | --- |
| 01 | Ruta | enden av bjelken og ruta sett frå sida, vassrett |
| 02 | Ei rute som lyser | heile lampa, tre kvart |
| 03 | Skive. Røyr. Blad. | rett framanfrå |
| 04 | Vipp | tre rendringar ved sida av kvarandre: 0°, 40° og 80° |
| 05 | Eitt punkt i messing | enden av bjelken |
| 06 | Lyset kjem frå kanten | hjørnet og den frie kanten på ruta |
| 07 | Eitt røyr, éin boge | der røyret går inn i bjelken |
| 08 | Om kvelden | lampa som einaste lyskjelde, på ei mørk plate med eit ark under |
| 09 | Éin matt farge | same utsnitt i fire fargar |
| 10 | Tretten delar, fire skruar | sprengt vising som strek |
| 11 | Mål | framanfrå og frå sida som strek |
| 12 | Kontrollert, ikkje bygd | profilen, og det som er kontrollert og ikkje prøvd |

## Korleis rendringane er laga

`konsept/film/cad/render_ekte.py` rendrar i Cycles på skjermkortet, 2256 × 1600, om lag to minutt per bilete. Geometrien er delane frå `northern.py` med fin netting (`eksporter_fin.py`).

- **Kantar:** alle skarpe kantar får 0,3 mm radius i skyggjaren, slik lakkerte og dreidde delar har.
- **Lakk og messing:** matt pulverlakk med fin appelsinhud, og dreidd messing der glansen går i sirklar om midten.
- **Ruta:** plata er klar akryl som lyser nedover og ut av den frie kanten, og arket lyser oppover, mest ved bjelken. Det er dette lyset som lyser opp golvet i bileta.
- **Studio:** éi lang smal lysflate over og litt bak lampa, eit svakt kantlys, og svart rom.
- **Linsa:** lysspreiinga rundt dei lyse kantane er lagd på etterpå som ei folding av det lineære biletet.

Fire ting er val for biletet, ikkje fysikk, og bør vere kjende:

1. **Lysstyrkane i ruta er sette for auget.** Fordelinga mellom underside, kant og ark er ikkje rekna, og gløden er ikkje ei lysrekning.
2. **Studiolysa treff ikkje ruta og ikkje golvet.** Ei blank rute speglar lysflata over seg og mistar gløden. Ein fotograf ville skjerma lyset. Her er det gjort med lyslenking.
3. **Rillene i arket er teikna 0,5 mm breie i nærbileta.** Eit verkeleg prismeark har om lag 0,05 mm, og det syner ikkje i eit bilete.
4. **Vippinga er tre bilete ved sida av kvarandre**, ikkje éi eksponering. Bjelken svingar 9,5 mm om røyret når ruta vippar, så tre bilete oppå kvarandre gjev ein uklar ende på bjelken.

Sprengt vising og mål (side 10 og 11) er kantane i CAD-modellen med skjulte liner fjerna, frå `teikning_b.py`. Dei er eksakte.

## 3D-fila

`konsept/film/cad/eksporter_3d.py` skriv `ruta.usdz` og `ruta.glb` frå same delar, med middels netting.

| | |
| --- | --- |
| Trekantar | 54 816 |
| Storleik | USDZ 2,5 MB, GLB 1,4 MB |
| Eining og akse | meter, Y opp, foten på golvet i origo |
| Mål i fila | 378 × 273 × 454 mm (djupna tek med leidningen) |
| Animasjon | gruppa «Blad» dreier om røyret: 35° → 0° → 80° → 35°, tolv sekund |
| Material | lakk, messing, klar plate, lysande ark, pute, skrue og leidning |

Kontrollert:

- **ARKit-reglane:** Pixar sin kontrollør (`UsdUtils.ComplianceChecker` med ARKit-reglar) gjev ingen feil og ingen merknader for nokon av dei fire filene.
- **Lesen inn att:** `sjekk_3d.py` opnar USDZ-fila i ei tom scene og rendrar ho ved 35° og 80°. Geometri, material og animasjon er med.
- **Nettlesaren:** GLB-fila er prøvd i nettstaden: glidaren vippar ruta frå 0° til 80°, og fargeknappane byter lakk og AR-fil.

Ikkje kontrollert: fila er ikkje opna på ein iPhone eller iPad. Materiala i 3D-fila er enkle og er ikkje dei same som i rendringane.

## Det sidene seier, og kvar det kjem frå

- Måla, massen, tyngdepunktet, veltekrafta og hellinga: `kontroll.json`, skriven av `konsept/film/cad/northern.py`.
- 190 lx på side 08: overslaget i `konsept/film/cad/00-ruta-pa-fot.md` (`lys_sjekk.py`). Det gjeld revisjon A, som har same rute, høgd og helling, og er ikkje rekna på nytt.
- Formspråket til Northern: `research/01-northern.md`.
- Det som ikkje er prøvd, står på side 12.
