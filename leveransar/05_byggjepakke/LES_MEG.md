# Byggjepakke for skissemodellane, runde 2

Til konseptgjennomgangen 18.11. Skriv ut i faktisk storleik (100 %). Kontrollstreken nedst på kvar side skal vere 100 mm.

| Fil | Innhald |
| --- | --- |
| `byggjepakke-A4.pdf` | 10 sider: delliste, rekkjefølgje og tryggleik, målearket for lobebreidda, målekortet til 16 cm, plassering og malar for A Skiva (skive, ribbe, røyr, flik, arm), B Over og C Vindauge (maske og gråfilter 1:1) |
| `malar-A3.pdf` | Målekortet til 24 cm og heile skiva til A med ribba |
| `fotoliste-A4.pdf` | Kameraplass, innstillingar, bileta per modell og måletabell |
| `ribbe_R1200_250mm.stl` | Ribba til A: boge R 1200 mm over 250 mm, pil 6,5 mm, 6 mm tjukk |

Pakken følgjer runde 2 av konsepta (`konsept/tre/00-tre-konsept.md`): veggflik og to lykter i A, knekt plate i B, julekule med kondensor, maske og gråfilter i C med hovudet 70 cm over bordet. Geometrien er henta frå modellkoden med `hent_geometri.py` (`runde2.json`, `maske_C.npz`). Første utgåva følgde runde 1 og vart kontrollert av to uavhengige lesarar; feila dei fann, er retta her.

Modellen er ikkje målt. Sikt etter lysflekken, ikkje etter gradene.

Lag pakken på nytt etter endringar i konsepta:

```
python hent_geometri.py
python lag_byggjepakke.py
python lag_fotoliste.py
```
