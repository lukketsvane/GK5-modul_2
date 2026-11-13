# Kitbash generasjon 1: søket

Seksten lampekroppar sette saman av CAD-en som finst: delane frå overheadprojektoren (`../delar.py`, P01 til P08), ruta på fot (`konsept/film/cad/ut/samla/*.stl`, lesne og ikkje endra) og nokre få nye smådelar. Kvar kropp er støtte × lysorgan. Alle blir målte likt: mekanikk frå geometrien og lys i lysmotoren, med same tal som A, B, C og D. Basen P04 (nettspenning) og FSX-pæra P09 er ikkje med i nokon kropp.

Dette er søket og valet. Dei fire lampene som blir bygde i djupna (printdelar, kollisjon, varme, rendrar, lysstudiar), ligg i `konsept/kitbash/` og høyrer til styringsøkta. Ingenting er målt.

## Filene

| Fil | Kva ho gjer |
| --- | --- |
| `kitbash.py` | Motoren: settet (`sett`, `cad`, `ny`), støttene (`bak_skjermen`, `paa_fot`), organa (`plate`, `boyel`, `diode`, `vindaugsmodul`, `ruta_gruppe`, `hovud`) og dei 18 kroppane i `KROPPAR` og `KONTROLL`. |
| `lys.py` | Lysgrepa `g(t) -> (lys, kropp)` for kvar kropp, rekna med `ruta.rekn` (same nøklar som `tre.rekn`). |
| `samle.py` | Set mekanikk og lys saman og prøver kvar kropp mot krava. |
| `etterproving.py` | Bandet rekna ein gong til med uavhengig kode (strålesporing i numpy), utan lysmotoren. |
| `lyskart.py` | Lyset på bordet sett ovanfrå, frå `etterproving.py`: stripa mot rein plate ved sida av éi diode med ark. |
| `ark.py` | Dei to arka i husstilen: `ark-brett` og `ark-val`. Dei ligg òg som rammer på sida «Kitbash · 13.11» i Figma-fila til Iver. |
| `studie.py` | Rombilete (stemning og arbeid) med lysmotoren sin `par()`. Verkar for enkle grep. Bandet er for tungt, sjå feil 9 i loggen. |
| `brett.png`, `velt_umogleg.png`, `flis/` | Brettet 4 × 4 i husstilen, dei to kontrollkroppane, og kvar flis for seg. |
| `brett-merkt.png` | Same brett med nummer, namn og tre tal per kropp. |
| `tal_mek.json`, `tal_lys.json`, `tal_brett.json` | Råtala. `tal.json`, `tal.csv` og `tal.md` er dei samla. |
| `logg.md` | Kva som vart gjort, med feila. |
| `val.md` | Valet (a)/(b)/(c) med tal. |

## Kommandoane

```
python kitbash.py mek      mekanikk for alle 18 (1 s)                     -> tal_mek.json
python kitbash.py brett    brettet (2 min)                                -> brett.png, velt_umogleg.png, flis/, tal_brett.json
python lys.py              alle lysgrep (om lag 15 min, bandet er tungt)  -> tal_lys.json
python lys.py over-vipp    eitt eller fleire grep ved namn
python samle.py            tabellane og det merkte brettet                -> tal.json, tal.csv, tal.md, brett-merkt.png
```

Køyr éin tung prosess om gongen. `lys.py` set seg sjølv til låg prioritet.

## Koordinatar

Kroppane er i **millimeter**, same rom som lysmotoren: origo på bordflata midt framfor skjermen ved bordkanten, x mot høgre, y frå brukaren mot veggen, z opp. Skjermen er 54 × 31 cm med framsida i y = 450, veggen står i y = 700. Lysgrepa i `lys.py` er i **meter** med `b(x, y, h)`. Plassane er dei same i begge filene: plata over skjermkanten har senter (0, 360, 620) og kjelda (0, 409, 510), plata på fot har senter (440, 360, 470) og kjelda (440, 410, 50).

## Slik brukar du ein kropp

```python
import kitbash as kb
sp = kb.SPEC[3]                 # kropp 4, Klype · band
delar, handtak = sp['bygg']()   # delar: liste med dict(namn, mesh (trimesh, mm), mat, kjelde ('sett', 'cad' eller 'ny'), pid)
rad = kb.mekanikk(sp, delar, handtak)

import lys
g = dict(lys.GREP)[sp['lys']]   # lysgrepet g(t) -> (lys, kropp), t = 0 stemning og t = 1 arbeid
tal = lys.ruta.rekn(g)          # W350, jamnheit, bak350, auge25/47/60, likskap, sprang ...
```

## Kva motoren går ut frå

- **Måla på delane** er dei i `../delar.py`, anslått frå foto. Massen er volum × tettleik. Kappa på armen er rekna 35 % fylt, lagerskiva 50 % og lampesokkelen i hovudet 15 % (ANTAKING). Delane frå ruta-CAD-en har massen frå `kontroll.json` der.
- **Velt.** Stiv kropp på det konvekse hylsteret av alt som rører bordet. `dytt_N` er vassrett kraft i handtaket i verste retning, `trykk_N` er kraft rett ned i handtaket. Måla er 3 N og 5 N, som i formsøket (`val_maal.json`). Kontroll: ruta på fot gjev 3,0 N og 24,0° her, mot 3,1 N og 24,5° i `konsept/film/cad/ut/kontroll.json`.
- **Under skjermen** står skjermen (4 kg, ANTAKING) på stålplata og held henne nede.
- **Rekkjevidd** er avstanden frå høgre skulder (200, −220, 320) til handtaket. Grensa er 70 cm (ANTAKING frå formsøket).
- **Lyset** har avgrensingane til lysmotoren (`konsept/lysskisse/API.md`). Vindaugsdioden er `ruta.vindaugsdiode` flytta til toppen av armen, med 600 000 foton. LED-stripa er fem punktkjelder langs 24 cm.
- **Brettet** brukar `northern-lampe/felles.py` (same lys og farge som formsøket). Kameraet står i asimut 300 og ikkje 240, fordi platene på fot elles ligg rett langs synslina. Skjermen er med som mørk skugge.

## Tryggleik

- Basen P04 går på nettspenning og er ikkje med. Ho skal aldri koplast til og aldri brukast i ein skissemodell.
- Fresnelspegelen og linsene må aldri stå i sol. Ei lampe med fresnelplata ved eit vindauge samlar sollyset 19 cm framfor plata. Det gjeld produktet òg, ikkje berre skissemodellen.
