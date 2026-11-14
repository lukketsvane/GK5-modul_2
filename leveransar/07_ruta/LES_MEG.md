# Ruta, revisjon B: presentasjon

Dato: 13.11.2026. Elleve sider om den endelege lampa: ei lysande rute på éin stilk, teikna inn i formspråket til Northern. Alt blir bygd på nytt med `python lag.py`.

| Fil | Innhald |
| --- | --- |
| `Ruta-presentasjon.pdf` | presentasjonen, 1127 × 797 px per side |
| `sider/side-NN.jpg` | kvar side som bilete, 2254 × 1594 |
| `presentasjon.html` | kjelda til PDF-en |
| `bilete/` | bileta som er brukte |
| `lag.py` | byggjer bileta, HTML, PDF og sidene. Tala kjem frå `konsept/film/cad/ut-b/kontroll.json` |

## To slag bilete

Kvar side seier kva slag bilete ho viser.

- **Rendring av CAD-modellen** (`studio`, `helling`, `detalj-messing`, `sprengt`, `kveld`, `rev-b-*`): geometrien frå `konsept/film/cad/northern.py`, rendra i Blender med `render_presentasjon.py`. Gløden i ruta er ei visualisering, ikkje ei lysrekning.
- **Generert bilete etter CAD-modellen** (`p0` til `p6`): laga med ein biletmodell (gpt-image-2.6-sunburst) med CAD-rendringa som førelegg. Dei er illustrasjonar. Røyret er litt tjukkare i nokre av dei enn i CAD-en, og lyset i dei er ikkje rekna.

| Bilete | Motiv | Førelegg |
| --- | --- | --- |
| `p0-framside` | pulten om kvelden, mørkegrøn, med plass til tittelen | `p2-kveld` |
| `p1-miljo` | pulten i dagslys, grå-beige | rendringa i grå-beige |
| `p2-kveld` | pulten om kvelden, mørkegrøn (ikkje brukt i presentasjonen) | rendringa i mørkegrøn |
| `p3-pakke` | lampa åleine mot lysegrå bakgrunn | rendringa i grå-beige |
| `p4-hand` | ei hand vippar ruta | `p1-miljo` |
| `p5-messing` | ein finger på messingpunktet | `p3-pakke` |
| `p6-heim` | skjenken heime om kvelden, svart | `p3-pakke` |

## Det sidene seier, og kvar det kjem frå

- Måla, massen, tyngdepunktet, veltekreftene og hellinga: `kontroll.json`, skriven av `northern.py`.
- Lystala på side 7: overslaget i `konsept/film/cad/00-ruta-pa-fot.md` (`lys_sjekk.py`). Det gjeld revisjon A, som har same rute, høgd og helling, og er ikkje rekna på nytt.
- Formspråket til Northern: `research/01-northern.md`.
- Det som ikkje er prøvd, står på side 11.
