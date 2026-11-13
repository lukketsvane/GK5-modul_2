# Tre konsept, til Moodle 17.11

Fire sider i 1127 x 797 px, same stil som fase 1-sidene og formføringsplansja.

| Fil | Innhald |
| --- | --- |
| side-10-tre-konsept | Dei tre i arbeid side om side, og tala samanlikna |
| side-11-konsept-a-skiva | A Skiva: bøygd spegelskive som vippar frå veggen til feltet |
| side-12-konsept-b-over | B Over: fresnelplata over skjermkanten |
| side-13-konsept-c-vindauge | C Vindauge: linse og delt spegel, vindauget står og feltet kjem |

Konsepta, tala og konseptarka kjem frå lysskisseøkta i `konsept/tre/` (`00-tre-konsept.md`, `tal-*.json`, `ark-*.png`). Bileta på sidene er klipte ut av arka: stemning til venstre, arbeid til høgre. Tala er modell, ikkje måling.

Kjem det nye ark eller tal i `konsept/tre/`, lag sidene på nytt:

```
python lys/bygg_konsept.py
sh lag-png.sh side-10-tre-konsept
sh lag-png.sh side-11-konsept-a-skiva
sh lag-png.sh side-12-konsept-b-over
sh lag-png.sh side-13-konsept-c-vindauge
```

Tekstane om prinsipp, skissemodell og det som ikkje held enno står i `KONSEPT` øvst i `lys/bygg_konsept.py`.
