# Raup svart · hovudrolle

Alle delane til Raup i pressa eggekartong, samla på éin stad. Geometrien er frå tupp-revisjonen ([Raup-tupp.step](delar/Raup-tupp.step)). Kjelda er Codex-økta «Raup A» (`Documents\Codex\2026-11-20\lag-ti-nye-design-for-northern-3\Raup-svart`).

## Status for print

| Del | Kva | Fil | Status |
|---|---|---|---|
| D02 | Matrise, formar utsida av skalet | [Raup-D02-A2-PLA.gcode.3mf](print/ferdig/Raup-D02-A2-PLA.gcode.3mf) | Ferdig printa |
| D01-R2 | Stempel med 6 mm fot langs Raup-kurva | [D01-R2-A2-PLA.gcode.3mf](print/ferdig/D01-R2-A2-PLA.gcode.3mf) · [STL](former/D01-R2/D01-R2.stl) | Ferdig printa |
| D03 + D04, B01, B02 ×2, B04 ×2, E04, M01 | Restdelane på éi plate | [Raup-svart-hovudprosjekt-A2-PLA.3mf](print/Raup-svart-hovudprosjekt-A2-PLA.3mf) | **Neste.** 2 t 37 min, 76 g kvit PLA (A2) |
| G02, G02b, G03 | Kabelfôring, kile og kabelauge | [03-Raup-TPU.3mf](delar/TPU/03-Raup-TPU.3mf) | TPU 95A, glatt plate. 15 min, 0,8 g |
| S02, E03 | Rotsko og lysberar | [S02](delar/SLS/S02.stl) · [E03](delar/SLS/E03_Lysberar.stl) | SLS PA12, bestillast |

Hovudprosjektet er skive med 0,20 mm Standard, Generic PLA, 4 veggar, 20 % gyroid og 4 mm brim. Berre M01 har støtte. Byggjeskriptet er [samle_hovudprosjekt.py](kjelde/samle_hovudprosjekt.py).

## Delane

| Del | Rolle | Fil |
|---|---|---|
| D01-R2 / D02 | Stempel og matrise for fiberskalet P01. Tre M6-stag | [former/](former/) |
| D03 | Formar den korte returveggen P02. Ryggen er halvert til 6 mm (22 cm³, var 44) sidan klossen ber lite. Pressflata er uendra | [D03-retur.stl](former/D03-retur.stl) · [d03_halv.py](kjelde/d03_halv.py) |
| D04 | Formar den smale randa (strimmel 76,6 × 6,1 mm) | [D04-rand.stl](former/D04-rand.stl) |
| B01 | Botnplate med lys, kabel og ballast | [B01-tupp.stl](delar/B01-tupp.stl) · [STEP](delar/B01_Botnplate-tupp.step) |
| B02 ×2 | Limføter med M3-mutter og Ø1,5 mm sikringspinne | [B02_1](delar/B02_1_Limfot.stl) · [B02_2](delar/B02_2_Limfot.stl) |
| B04 ×2 | Haldarar for ballastskivene | [B04_1](delar/B04_1_Skivehaldar.stl) · [B04_2](delar/B04_2_Skivehaldar.stl) |
| E04 | Kabelbru | [E04_Kabelbru.stl](delar/E04_Kabelbru.stl) |
| M01 | Boga nedre list for monitorfilmen | [M01-Nedrelist.stl](delar/M01-Nedrelist.stl) |
| P01, P02, P03 | Fiberdelane: skal, returvegg og hylle | Pressa i D01–D04. [Verkstad.md](delar/Verkstad.md) |

Innkjøp (M6-stag, M3/M2-skruar, stålskiver, spot, dimmar) står i [Materialinnkjop.csv](former/Materialinnkjop.csv). Rekkjefølgja i verkstaden står i [Verkstadkort.txt](former/Verkstadkort.txt). Skjeremalane i 1:1 er [Raup-skjeremalar-1til1.pdf](former/Raup-skjeremalar-1til1.pdf) og [Underkutt-verkstadmal-1til1.pdf](delar/Underkutt-verkstadmal-1til1.pdf).

## Står att

- Mål krympa på første pressing. D01 og D02 føreset 3 %.
- Lampedelane har tidlegare vore planlagde i PETG. PLA er greitt for prøvemontering. B01 ber spotten, så vurder PETG til den endelege lampa etter varmeprøva.
