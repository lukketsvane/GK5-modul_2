# Ruta på fot, revisjon B: monteringsrettleiing M01

IKEA-stil, 17 sider, laga frå CAD-en (`../../northern.py`, delane i `../samla/`) med `verktoy/ikea/bygg.py` i formnerd og skillen `ikea-rettleiing`.

## Filer

| Fil | Innhald |
| --- | --- |
| `rettleiing.pdf` | rettleiinga i A4 |
| `sider/`, `kontaktark.png` | éin PNG per side, og alle på eitt ark |
| `rapport.json` | kontrollen frå byggjaren: beslag mot stykkliste, tomme figurar, overlappande tekst, strek i pt |
| `spesifikasjon.json` | sidene og figurane |
| `poser.py` | legg delane frå `../samla/` i 0°, 80° og 180° (berre rørsla bjelken har om røyret) |
| `ikea-reference-audit.md` | referansane og kva som er overført |

## Bygg på nytt

```bash
python3 poser.py
python3 <formnerd>/verktoy/ikea/bygg.py spesifikasjon.json .
```

Krev `bygg.py` frå greina `claude/ikea-manual-skill` i formnerd (stilnøklane, `line_pt`, `n: false` og `glas`).

## Digitalt kontrollert

- ID-ar og mengder følgjer stykklista i `../kontroll.json` (01–13 og E × 4). `rapport.json` har ingen åtvaringar.
- Stillingane er rørsla til bjelken om røyret. Ved 80° er lågaste punkt 59,4 mm, som i `kontroll.json`.
- Strek 0,5–1,0 pt, stegnummer 32 pt, mengder 18 pt, sidetal 9 pt.

## Portane (side 4 og 5)

- Leidninga gjennom foten, røyret og bjelken er ikkje i CAD-en.
- Stykklista manglar innpressmutrane i bjelken (4 × M3, 1 × M4), skruane til botnloket og settskruen M4 til røyret i foten. Hola finst i CAD-en.
- Korleis ballasten blir halden, er ikkje teikna.
- Prismesida kan ikkje teiknast: arket er ei flat plate i CAD-en, så steg 6 seier det med tre ord.

## Ikkje prøvd fysisk

Røyret i foten, bjelken på røyret, stoppskruen i sporet, friksjonen frå bremseskruen og lyset inn i plata. Ei vakker rettleiing er ikkje prov på at delane passar.

## Utgåver

M01: første for revisjon B. Revisjon A har monteringsarka i `../../ut/ruta-pa-fot-montering.pdf`.
