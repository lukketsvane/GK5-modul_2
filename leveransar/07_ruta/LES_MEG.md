# Ruta, revisjon B: lysbilete, PDF, nettstad og 3D-fil

Dato: 14.11.2026, tredje utgåve. Alle bileta er no rendringar av CAD-modellen. Dei genererte bileta frå andre utgåve er tekne ut. Regelen er den same: lampa åleine på svart, eitt lys og éin biletstil, nesten ingen ord, og dei tekniske sidene som kvit strek. Alt blir bygd på nytt med `python lag.py`.

| Fil | Innhald |
| --- | --- |
| `Ruta-presentasjon.pdf` | tretten sider, 1127 × 797 px per side |
| `presentasjon.html` | same sider som lysbilete i nettlesaren. Piltastane blar, og sida fyller vindauget |
| `sider/side-NN.jpg` | kvar side som bilete, 2254 × 1594 |
| `../../ruta/index.html` | studioet: éin svart skjerm med modellen, tre modusar (lampe, mekanikk, lys), éin glidar og fargeval. Malen er `studio.html.mal` |
| `../../ruta/forteljing.html` | forteljinga: rendringane og streken nedover éi side |
| `../../ruta/3d/ruta-studio.glb` | modellen til studioet, med delane inni og to animasjonar (vipp og opne). 189 kB, pakka med Draco |
| `../../ruta/3d/ruta.usdz` | 3D-fila til AR på iPhone og iPad. Éi fil per farge |
| `../../ruta/3d/ruta.glb` | 3D-fila til nettlesaren |
| `bilete/` | rendringane som er brukte, som JPEG |
| `lag.py` | byggjer alt. Tala kjem frå `konsept/film/cad/ut-b/kontroll.json` og `lysmodell.json` |

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
| 10 | Tretten delar, fire skruar | delane trekte frå kvarandre, som rendring |
| 11 | Delane | sprengt vising som strek, med nummer og liste |
| 12 | Mål | framanfrå og frå sida som strek |
| 13 | Kontrollert, ikkje bygd | profilen, og det som er kontrollert og ikkje prøvd |

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

Strekteikningane (side 11 og 12) er kantane i CAD-modellen med skjulte liner fjerna, frå `teikning_b.py`. Dei er eksakte.

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
- **Nettlesaren:** studioet er prøvd i nettlesaren, sjå «Studioet» under.

Ikkje kontrollert: fila er ikkje opna på ein iPhone eller iPad. Materiala i 3D-fila er enkle og er ikkje dei same som i rendringane.

## Studioet

Studioet følgjer oppbygginga til Canon-sida på formnerd (`/canon50mm`): éin svart skjerm, objektet svevande, få modusar, éin glidar og éi line tekst berre der ho ber eit atterhald. Sida er skriven i three.js (versjon 0.170, henta frå jsDelivr) og teiknar berre når noko endrar seg.

| Modus | Glidaren | Det sida viser |
| --- | --- | --- |
| Lampe | helling, 0° til 80° | lampa i studiolys, ruta lyser |
| Mekanikk | samla til heilt opna | delane trekte frå kvarandre langs retningane dei blir sette saman i |
| Lys | effekt, 0,25 til 3 W | lampa som einaste lyskjelde, og lyset på bordet i lux med liner ved 50, 100, 200 og 400 lx |

### Lyset er rekna i fotometriske einingar

`konsept/film/cad/lysmodell.py` er fasiten, og sida reknar det same i nettlesaren. Kjeda er watt inn, lumen ut, candela per kvadratmeter på flatene og lux på bordet.

| Antaking | Verdi |
| --- | --- |
| Stripa | 100 lm per watt |
| Inn i plata | 60 % av lyset frå stripa |
| Ut av plata | 60 % ned gjennom undersida, 30 % opp gjennom arket, 10 % ned ved den frie kanten |
| Flatene | tre jamne, matte firkantar (Lambert) |

Ved 2 W gjev det 200 lm frå stripa og 120 lm ut av ruta: 447 cd/m² på undersida, 218 cd/m² på arket og 3183 cd/m² på kantstripa. Lux i eit punkt frå ein matt firkant har ei eksakt løysing (summen over dei fire kantane av vinkelen kanten spenner, gonga med kor mykje normalen til kantplanet peikar langs bordnormalen). Det er denne summen som blir rekna i kvar piksel på bordet, så biletet har inga støy og treng inga strålesporing.

| 2 W | Snitt over 40 × 40 cm under ruta | Høgst |
| --- | --- | --- |
| 0° | 191 lx | 305 lx |
| 20° | 210 lx | 392 lx |
| 35° | 203 lx | 456 lx |
| 60° | 167 lx | 519 lx |
| 80° | 137 lx | 458 lx |

Det modellen ikkje tek med: eit verkeleg prismeark samlar lyset og er ikkje matt, bjelken og foten skuggar ikkje bordet, og ingenting blir kasta vidare frå bordet. Verknadsgradane (100 lm/W og 60 % inn i plata) er anslag. Tala er ikkje målte.

I biletet svarar 300 cd/m² til kvitt før tonekurva (AgX). Lampa blir lyst opp av dei same tre flatene som lysflater med rett lysstyrke, og bordet kastar 45 % attende. I modusane Lampe og Mekanikk kjem det i tillegg eit svakt romlys, som er eit val for biletet.

### Kontrollert i nettlesaren

- **Lystala:** 15 prøvepunkt på bordet (tre hellingar, 2 W) er rekna i nettlesaren og i Python. Største avvik er 0,0005 lx. Sida viser 456 lx rett under ruta ved 2 W og 35°, 114 lx ved 0,5 W og 684 lx ved 3 W.
- **Hellinga:** animasjonen i fila går jamt, éin grad per bilete. Første utgåve hadde mjuk start og stopp, slik at 35° på glidaren var 32,5° i modellen. `eksporter_studio.py` måler no avviket og skriv det i `ruta-studio.kontroll.json` (0,0°).
- **Farten:** éi oppteikning tek 2,0 ms i Lampe, 2,2 ms i Lys og 1,4 ms i Mekanikk (median av 240, venta ut på skjermkortet), 1003 × 845 punkt, GTX 1070. Det er 56 588 trekantar i 16 teiknekall. Med alt i mellomlageret står modellen klar 0,2 sekund etter at sida opnar frå den lokale tenaren.
- **Storleiken:** modellen er 189 kB (var 1424 kB før Draco). three.js er 171 kB komprimert.

Ikkje kontrollert: sida er ikkje prøvd på telefon eller på ei maskin utan eige skjermkort. Fell farten under 25 bilete i sekundet, teiknar sida med færre punkt, men det er ikkje prøvd på ei maskin som treng det. Målinga er gjord med nettlesarruta i bakgrunnen, så sjølve flyten i rørsla er ikkje sett med auga av meg.

## Det sidene seier, og kvar det kjem frå

- Måla, massen, tyngdepunktet, veltekrafta og hellinga: `kontroll.json`, skriven av `konsept/film/cad/northern.py`.
- 203 lx og 456 lx på side 08: `konsept/film/cad/lysmodell.py` for revisjon B, 2 W og 35° helling. Snittet gjeld 40 × 40 cm av bordet under ruta. Det gamle overslaget for revisjon A (`lys_sjekk.py`) gav 190 og 436 lx. Tala er rekna, ikkje målte.
- Formspråket til Northern: `research/01-northern.md`.
- Det som ikkje er prøvd, står på side 13.
