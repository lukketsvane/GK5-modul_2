# Byggjesettet som 3D-delar

Delane frå den demonterte overheadprojektoren (truleg ein 3M 2000, sjå `research/13-byggjesett-og-lysforsoek.md`) og prismearket frå monitoren, modellerte med mål du kan endre. Biblioteket er laga for skisser og rendrar seinare. Optikken til arket er ikkje med. Han blir rekna i `konsept/vindauge/`.

## TRYGGLEIK

- **Straumforsyninga i basen går på nettspenning.** Det gjeld kortet, kondensatorane, trafoen og IEC-inntaket. Ho skal aldri koplast til straum att og aldri brukast i ein skissemodell. Kondensatorane kan halde på spenning lenge etter at straumen er borte. I modellen er desse underdelane med berre som form.
- **Fresnelspegelen og glaslinsene må aldri liggje i sol.** Dei samlar sollyset, og ein brennflekk kan tenne papir. Spegelen samlar lyset 187 mm framfor plata.

## Kva som ligg her

| Fil | Innhald |
| --- | --- |
| `delar.py` | Måla (`DIMS`, med verdi, usikkerheit og kjelde) og éin funksjon per del. Kvar funksjon gjev underdelar som `trimesh`-mesh i mm, med Z opp og materiale. Køyr `python delar.py` for å skrive alt under på nytt. |
| `stl/` | Éi STL-fil per underdel i mm, til dømes `P05_fresnelspegel_plate.stl`. Alle er tette. |
| `byggjesett.glb` | Alle delane lagde ut ved sida av kvarandre, med farge per materiale. Kan opnast i Blender, Fusion eller ein nettlesar. |
| `projektoren.glb` | Projektoren slik delane kan ha sete saman. Det er ein rekonstruksjon frå delane, ikkje målt. |
| `maal.json` | Same mål som `DIMS`, som JSON. |
| `scener.json`, `rendre_blender.py` | Fire studioscener, delbanken og rendraren for Blender (Cycles). |
| `render/` | Studiorendrane: projektoren samla, fresnelplata, linsene og arket. |
| `render/del-*.png` | Delbanken: kvar del for seg (P01 til P09) og projektoren samla, med gjennomsiktig bakgrunn. Ortografisk kamera frå same retning og 4 pikslar per mm, så bileta kan setjast saman i skisser utan å skalerast kvar for seg. `del-*.json` har storleiken. |
| `ark/` | Oversiktsarket (1127 × 797, husstilen frå fase 1): `lag_ark.py` legg alle delane i same målestokk og skriv `byggjesett.html` og `byggjesett.png`. |
| `kitbash/` | Søket: 16 lampekroppar sette saman av delane her og ruta på fot, med mekanikk og lys for alle, og valet (a)/(b)/(c). Sjå `kitbash/LES_MEG.md`. |

## Bruk

- **Fusion eller Blender:** importer STL-filene (mm) eller GLB-fila.
- **Python:** `from delar import del_, DIMS`, så gjev `del_('P05')` underdelane til fresnelspegelen. Endre eit mål i `DIMS` og køyr `python delar.py` på nytt.
- **Rendrar:** `blender.exe -b -P rendre_blender.py -- [scene ...]`. Blender 5.1.2 ligg i `Documents/verktoy/`. Skriptet køyrer på CPU med fire trådar og lågaste prioritet, så lyden ikkje hakkar. `--prove` gjev små, raske bilete. Scenene `del-P01` til `del-P09` og `del-samla` er delbanken.
- **Figma:** delbanken ligg på sida «Byggjesett · 13.11» i Figma-fila til Iver (ikkje klassefila), i 2 px per mm. Dra ein del inn i ei skisse og skaler alle delane like mykje, så held målestokken.
- **Arket (P08) i bileta:** filmen er vist som tynn, klar plast med glans og ein svak bøy, berre så han skal lesast som film. Prisma og optikken er ikkje med. Den første studiorendra hadde lys bak arket og vart heilt kvit. Det lyset er teke bort.

## Måla og kor sikre dei er

Dokumenterte mål kjem frå delelista til 3M 2000 og typeskiltet på vifta. Resten er anslått frå fotoa Iver tok 13.11.2026. Tre målarar målte fotoa kvar for seg med ulik målestokk: fresnelvindauget, A4-arka, og vifta saman med projektordata. Den eine fekk vindauget til 198 mm mot 285 mm i delelista, truleg fordi A4-arka låg i eit anna plan, og han er utelaten. Verdiane er snittet av dei to andre. Usikkerheita er minst halve skilnaden mellom dei. Ingenting er målt med linjal enno.

| Del | Mål | Verdi, mm | ± mm | Kjelde |
| --- | --- | --- | --- | --- |
| P01 arm | profil lengd | 240 | 12 | anslått frå foto |
|  | profil breidd | 43 | 6 | anslått frå foto |
|  | profil tjukk | 26 | 3 | anslått frå foto |
|  | vegg | 1,5 | 0,5 | antaking |
|  | kappe lengd | 98 | 10 | anslått frå foto |
|  | kappe breidd | 40 | 5 | anslått frå foto |
|  | kappe hogd | 51 | 8 | anslått frå foto |
|  | tapp d | 6 | 1,5 | anslått frå foto |
|  | tapp lengd | 15 | 3 | anslått frå foto |
|  | laas lengd | 12 | 4 | anslått frå foto |
| P02 hengsel | lengd | 84 | 12 | anslått frå foto |
|  | breidd | 66 | 12 | anslått frå foto |
|  | hogd | 55 | 15 | anslått frå foto |
|  | fjoer lengd | 35 | 8 | anslått frå foto |
|  | fjoer d | 5,5 | 2 | anslått frå foto |
| P03 hovud | lengd | 140 | 15 | anslått frå foto |
|  | breidd | 78 | 10 | anslått frå foto |
|  | hogd | 80 | 20 | anslått frå foto |
|  | fas | 18 | 5 | anslått frå foto |
|  | vifte | 60 | 1 | typeskilt Sunon GM1206PTV3-A |
|  | lager d | 70 | 10 | anslått frå foto |
| P04 base | lengd | 285 | 12 | anslått frå foto |
|  | breidd | 99 | 12 | anslått frå foto |
|  | hogd | 28 | 10 | anslått frå foto |
| P05 fresnelspegel | vindauge | 285 | – | deleliste |
|  | brennvidd | 187,1 | – | deleliste |
|  | ramme ytre | 295 | 4 | anslått frå foto |
|  | skraa | 37 | 5 | anslått frå foto |
|  | tjukk | 3,5 | 2 | anslått frå foto |
| P06 glaslinse | d | 41 | 4 | anslått frå foto |
|  | hogd | 14 | 6 | anslått frå foto |
| P07 projeksjonslinse | fatning d | 77 | 5 | anslått frå foto |
|  | fatning hogd | 28 | 10 | anslått frå foto |
|  | linse d | 40 | 4 | anslått frå foto |
|  | spak lengd | 17 | 5 | anslått frå foto |
|  | brennvidd | 280 | 10 | research/13, utrekna |
| P08 prismeark | breidd | 306 | 40 | anslått frå foto |
|  | hogd | 535 | 70 | anslått frå foto |
|  | tjukk | 0,2 | 0,15 | antaking |
|  | flik breidd | 10 | 3 | anslått frå foto |
|  | flik hogd | 1,6 | 1 | anslått frå foto |
|  | flik tal | 2 | – | anslått frå foto |
| P09 fsx_paere | d | 20 | – | deleliste |
|  | lengd | 77 | – | deleliste |

## Mål med skyvelære

Desse måla har størst usikkerheit og betyr mest for skisser og feste. Mål dei og set dei inn i `DIMS`:

1. **Hovudet (P03):** høgd, lengd og breidd. Høgda er 65 eller 95 mm frå dei to målarane, så ± 20 mm.
2. **Armprofilen (P01):** tverrsnittet. 43 × 26 mm er ± 6 og ± 3 mm.
3. **Avstanden frå hengselaksen til aksen hovudet dreier om.** Han avgjer kor høgt hovudet står.
4. **Basebrettet (P04):** høgd, ± 10 mm.
5. **Projeksjonslinsa (P07):** høgda på fatninga, ± 10 mm, og diameteren på flensen.
6. **Glaslinsa (P06):** diameter og høgd, og brennvidda (mål med telefonlykta, ikkje sola).
7. **Prismearket (P08):** breidd, høgd og tjukkleik, og kvar flikane sit. Målearket er side 11 i byggjepakken.
8. **Hengselet (P02):** lengd, breidd og høgd, ± 12 til 15 mm.
9. **Lagerskiva (P03):** diameter, ± 10 mm.

Fotoa ligg i `context/delar-foto/`. Mappa er ikkje i repoet, fordi repoet er offentleg og eitt av fotoa viser eit privat brev.
