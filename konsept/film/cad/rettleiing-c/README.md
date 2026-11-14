# Monteringsrettleiing for Ruta på fot, revisjon C (M03)

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
| | Kapp røyret i 242 og 308 mm, og éin M3 × 10 til 8 mm (G) | Alt anna ventar på røyra |
| 1 | 33 skiver på tappane i foten (01), limte | Foten ligg opp ned og er open. Limet held skivene til botnloket kjem på |
| 2 | Røyra (04, 09) limte i bogestykket (12) | Muffene styrer vinkelen |
| 3 | Stamma limt i foten, fotringen (14) flatt mot foten, akselrøyret i vater | Ringen set hellinga. Vateret er det einaste som må stillast. Trekkjesnora må inn før limet |
| 4 | Bjelkehalvdelane (05) limte saman på restrøyret, med to filamentpinnar | Røyret held boringa rett, pinnane held vinkelen |
| | Lakk | Før lys og rute. Akselrøyr, boring og spalte er teipa |
| 5 | Bremsesko (13) og LED-stripe (10) | Skoen går inn frå LED-kanalen og må inn før stripa |
| 6 | Prismeark (08), så lysleiar (07) | Bjelken ligg med undersida opp |
| 7 | Lok (06) med 5 E, endelok (11) | Klemmer ruta. Loket bind skøyten i bjelken |
| 8 | Bjelken inn på akselrøyret | Leidningen blir dregen gjennom røyra med snora. Røyret skuvar skoen på plass under skruen |
| 9 | Låseskrue (E) og bremseskrue (G), ved 28° | Låseskruen går i sporet i kragen og held bjelken på røyret |
| 10 | Wago-klemmer (W), botnlok (02) med 3 F, lampa på ryggen | Skøyten ligg i koplingsrommet, strips som strekkavlasting |
| 11 | 16 knottar (K) | Lampa står på knottane, 75 mm frå midten |
| | Kontroll ved 0° og 80° | Same rørsle som kollisjonskontrollen i `ruta_c.py` |

## Endra frå M02

Rekkjefølgja og delane følgjer rettingane etter den uavhengige kontrollen (sjå `../02-produksjonsklar.md`): fotringen (14) er ny, bremseskruen er eit eige beslag (G), skivene blir limte i steg 1, stripa er 27 cm, og notane nemner trekkjesnor, styrepinnar og etterstramming.

## Antakingar og det som manglar

- **Leidningen** og trekkjesnora er ikkje teikna i stega, berre nemnde i steg 3, 8 og 10.
- **Filamentpinnane** i steg 4 er ikkje teikna.
- **Digitalt kontrollert:** `ut/rapport.json` har ingen åtvaringar, og mengdene i stega stemmer med dellista (6 E, 3 F, 1 G, 33 S, 2 W, 16 K).
- **Ikkje prøvd fysisk:** ingenting er trykt eller montert. Heftet er ikkje prov på at delane passar.

Referansane og grepa som er overførte, står i `ikea-reference-audit.md`.
