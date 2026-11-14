# Monteringsrettleiing for Ruta på fot, revisjon C (M02)

![Kontaktark](ut/kontaktark.png)

18 sider i IKEA-stil, laga med skillen `ikea-rettleiing` og `verktoy/ikea/bygg.py` i [formnerd](https://github.com/lukketsvane/formnerd). PDF-en ligg i `ut/rettleiing.pdf`, sidene i `ut/sider/`. Handleliste, printoppsett og lakk står i `../02-produksjonsklar.md`.

## Bygg på nytt

```bash
python ../ruta_c.py                                              # CAD, kontroll og ut-c/
python lag_delar.py                                              # delane i 0°, 28°, 35°, 80° og på benken
python lag_spesifikasjon.py                                      # spesifikasjon.json
python <formnerd>/verktoy/ikea/bygg.py spesifikasjon.json ut     # PDF, sider, kontaktark og rapport
```

## Rekkjefølgja

| Steg | Handling | Kvifor her |
| --- | --- | --- |
| | Kapp røyret i 242 og 308 mm | Alt anna ventar på røyra |
| 1 | Røyra (04, 09) limte i bogestykket (12) | Muffene styrer vinkelen |
| 2 | Stamma limt i foten (01), akselrøyret i vater | Vateret på akselrøyret er det einaste som må stillast |
| 3 | Bjelkehalvdelane (05) limte saman på restrøyret | Røyret held boringa rett medan limet set seg |
| | Lakk | Før lys og rute. Akselrøyr, boring og spalte er teipa |
| 4 | Bremsesko (13) og LED-stripe (10) | Skoen går inn frå LED-kanalen og må inn før stripa |
| 5 | Prismeark (08), så lysleiar (07) | Bjelken ligg med undersida opp |
| 6 | Lok (06) med 5 E, endelok (11) | Klemmer ruta. Loket bind skøyten i bjelken |
| 7 | Bjelken inn på akselrøyret | Leidningen går gjennom røyra til foten først |
| 8 | Låseskrue (E) og bremseskrue (F), ved 28° | Låseskruen går i sporet i kragen og held bjelken på røyret |
| 9 | 33 skiver på pinnane, lampa på ryggen | Skivene ligg laust til botnloket er på |
| 10 | Wago-klemmer (W), botnlok (02) med 3 F | Skøyten ligg i koplingsrommet, strips som strekkavlasting |
| 11 | 16 knottar (K) | Lampa står på knottane, 75 mm frå midten |
| | Kontroll ved 0° og 80° | Same rørsle som kollisjonskontrollen i `ruta_c.py` |

## Antakingar og det som manglar

- **Bremseskruen** er G i `ruta_c.py` og F i heftet. Det er same skrue som i botnloket (M3 × 10), så heftet tel han saman med dei.
- **Leidningen** er ikkje teikna i stega, berre nemnd i steg 7 og 10.
- **Digitalt kontrollert:** `ut/rapport.json` har ingen åtvaringar, og mengdene i stega stemmer med dellista (6 E, 4 F, 33 S, 2 W, 16 K).
- **Ikkje prøvd fysisk:** ingenting er trykt eller montert. Heftet er ikkje prov på at delane passar.

Referansane og grepa som er overførte, står i `ikea-reference-audit.md`.
