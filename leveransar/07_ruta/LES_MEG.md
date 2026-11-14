# Ruta, revisjon B: presentasjon

Dato: 14.11.2026, andre utgåve. Tolv sider om den endelege lampa. Første utgåve var ein rapport i husstilen med blanda biletspråk og vart vraka. Denne har éin regel: objektet åleine på svart, eitt lys og éin biletstil gjennom alle sidene, nesten ingen ord, og dei tekniske sidene som kvit strek. Alt blir bygd på nytt med `python lag.py`.

| Fil | Innhald |
| --- | --- |
| `Ruta-presentasjon.pdf` | presentasjonen, 1127 × 797 px per side |
| `sider/side-NN.jpg` | kvar side som bilete, 2254 × 1594 |
| `presentasjon.html` | kjelda til PDF-en |
| `bilete/` | bileta som er brukte |
| `lag.py` | byggjer bileta, HTML, PDF og sidene. Tala kjem frå `konsept/film/cad/ut-b/kontroll.json` |

## Sidene

| | Side | Bilete |
| --- | --- | --- |
| 01 | Ruta | enden av bjelken og ruta som éi line av lys |
| 02 | Ei rute som lyser | heile lampa, tre kvart |
| 03 | Skive. Røyr. Blad. | rett framanfrå |
| 04 | Vipp | ruta i tre stillingar: 0°, 40° og 80° |
| 05 | Eitt punkt i messing | enden av bjelken |
| 06 | Lyset kjem frå kanten | hjørnet og den frie kanten på ruta |
| 07 | Eitt røyr, éin boge | der røyret går inn i bjelken |
| 08 | Om kvelden | lampa på pulten, mørkegrøn |
| 09 | Éin matt farge | same utsnitt i fire fargar |
| 10 | Tretten delar, fire skruar | sprengt vising som strek |
| 11 | Mål | framanfrå og frå sida som strek |
| 12 | Kontrollert, ikkje bygd | profilen, og det som er kontrollert og ikkje prøvd |

## To slag bilete

Kvar side seier nedst kva ho viser.

- **Generert bilete etter CAD-modellen** (`f-*`, `p0-framside`): CAD-modellen er først rendra i Blender frå det utsnittet sida skal ha (`konsept/film/cad/render_presentasjon.py`, visingane `ref`, `refprofil` og `refkant`, filene `ut-b/render/ref-*.png`). Så har ein biletmodell (gpt-image-2.6-sunburst) fotografert rendringa om med same utsnitt og geometri, i eitt felles lys. Bileta er illustrasjonar. Materialkjensla, gløden og lyset i dei er ikkje rekna.
- **Teikna frå CAD-modellen** (side 10 og 11): kantane i CAD-modellen med skjulte liner fjerna, frå `konsept/film/cad/teikning_b.py`. Dei er eksakte.

To ting vart retta undervegs, fordi dei viste noko CAD-en ikkje har: profilen og vifta vart tekne om att frå eit førelegg sett rett frå sida (det første såg litt ovanfrå og gav bjelken ein kuleforma ende), og ei spegling under bjelken i messingbiletet vart teken bort.

## Det sidene seier, og kvar det kjem frå

- Måla, massen, tyngdepunktet, veltekrafta og hellinga: `kontroll.json`, skriven av `konsept/film/cad/northern.py`.
- 190 lx på side 08: overslaget i `konsept/film/cad/00-ruta-pa-fot.md` (`lys_sjekk.py`). Det gjeld revisjon A, som har same rute, høgd og helling, og er ikkje rekna på nytt.
- Formspråket til Northern: `research/01-northern.md`.
- Det som ikkje er prøvd, står på side 12.
