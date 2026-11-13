# Etterprøving av KLIPP: ring-vipp, maane-drei, luke

Dato 13.11.2026. Skript `etterproving.py`, logg `etterproving-logg.txt`, tal i `etterproving.json`. Modell, ikkje måling. Malen `_mal.py` er køyrd éin gong og verkar. Målet var å felle kandidatane. Alle tre fall.

## Tala på nytt

Alle tal i funn.md kjem att innanfor 5 prosent (største avvik: sprang for maane-drei 0,016 mot 0,02, avrunding). Strekk er 0 i alle steg. Rekninga er ikkje feil. Det som fell, er det tala ikkje spør om.

## Det tala skjuler

- **F6 bak skjermen.** Talet «vegg» er snittet over heile veggsona. Rett bak skjermen (54 × 31 cm) gjev arbeidsstillinga 31 lx (ring-vipp), 40 (maane-drei) og 56 (luke). Målet er 100 til 150. Lyset ligg i ein flekk til høgre: 2125 lx ved x 0,45 og 63 cm over bordet for ring-vipp, 1976 for maane-drei. Høgre halvdel av veggsona får 224 og 265 lx, venstre 11 og 12. Det er ikkje dempa kontrast rundt skjermen, det er ein ny lys flekk ved sida av han.
- **F1 ved låg augehøgd.** Med auget 25 cm over bordet ser ein satinloba frå framkanten av skiva: 5439 cd/m² i arbeid for ring-vipp og luke (grensa er 3000), og 1354 alt ved t 0,75 for ring-vipp. Luke ligg på 1360 i stemning (F5: 500). maane-drei held seg under 942. Ved 60 cm held alle tre.
- **SATIN.** ring-vipp med rd 0,3: 1559 cd/m² mot auget (F5 fell). Med sigma 14: 5,10 W for 350 lx, over 5 W, så F3 blir ikkje nådd innanfor budsjettet. maane-drei med sigma 6: jamnheit 0,08. Resultatet kviler på antakinga.
- **Strålen.** Skiva fangar 61 % av strålen i arbeid og 49 % i stemning for ring-vipp (maane-drei 52 og 32 %). Resten går gjennom klippet til veggflekken, nesten ingenting til taket (1 lm).
- **Geometri.** Kjelda står ved y 0,15, og ho syner ikkje frå stolen. Arket går til y 0,51 til 0,52, altså bak skjermplanet, men ved x over 0,36, utanfor skjermkanten (0,27). Inga flis speglar seg i skjermen frå nokon av dei tre augehøgdene. Flate skiver, inga djup holform.

## Dom per kandidat

**ring-vipp: held ikkje.** F3 held ved 47 cm (394 lx), F2 er éi handling med topp 0,72 og likskap 0,78. Men F6 bak skjermen er 31 lx, F1 fell ved auget 25 cm (5439 cd/m²), og F5 fell med rd 0,3. Jamnheit 0,42 mot 0,6. Veggstrøket er ein flekk ved sida av skjermen.

**maane-drei: held ikkje.** Likskap 0,90 er dimmar etter API.md, så F2 er ein dimmar og ikkje ein overgang. Bak skjermen 4 lx i stemning og 40 i arbeid. Jamnheit 0,21, og 0,08 med sigma 6. Ho er den einaste som held F1 ved alle augehøgder.

**luke: held ikkje.** F6 fell både i snitt (59 lx, vegg/felt 0,14) og bak skjermen (56). F1 fell ved 25 cm i alle stillingar (1360 til 5439 cd/m²), F5 fell i stemning ved same høgd.

## Briefen

«Utan å verke teknisk»: ei skive på projektorstolpen med synleg ledd og ein flekk på veggen les som riggutstyr, ikkje som heimleg lampe. Stemninga er lånt frå ein lys flekk (530 lx i stemning, ring-vipp), ikkje frå eit mjukt veggstrøk. Ansiktslys 55 til 58 lx held F10.

## Bygg

Skissemodellen kan lagast på éin dag for om lag null kroner: papp eller plate, folie, diffusorark, stolpen med ledd, telefonlykt i rør. Det som manglar: (1) telefonlykta er kald kvit, om lag 5000 til 6500 K, og eit varmt filter finst ikkje i byggjesettet, så F4 og stemninga kan ikkje prøvast. (2) ring-vipp kan ikkje festast i midten der holet er, og festet ved kanten endrar vippeaksen frå modellen. (3) Spreiinga til røyret (±14°) er ikkje målt, og modellen reknar 10°. (4) Satin av folie og diffusorark er ikkje målt. Mål lux rett bak skjermen, ikkje berre snittet, og fotografer frå 25 cm over bordet.

## Northern

R1: fot, stong og skive er tre primærformer, held. R2: stonga held. R3: ingen synleg kjelde, men holet kastar ein avgrensa lysflekk på veggen, og «mjuk» utelukkar skarp lyskant (halvskuggen er om lag 5 cm på ein flekk på 10 til 15 cm). R4 og R5 er opne. Den flate skiva har ein skarp kant i lyshovudet, medan «mjuk» krev krumma kontur. Luka er eit fjerde formelement og mekanikk i lyshovudet, så ho bryt «enkel».

## Nabo

Verner Panton Reflect (1980, Verpan): kjelda i foten lyser på ei vippbar skive som kastar lyset ned utan blending. Det er ring-vipp utan hol. https://hivemodern.com/pages/product13954/reflect-table-lamp-verner-panton-verpan . Òg 101 Copenhagen Reflect og Modo Luce Disk. Inga lampe med hol i skiva funne.

## Feil i motoren

Talet `E_vegg` er snittet over heile veggsona (1,4 × 0,7 m), medan F6 i API.md seier «bak skjermen». Ein flekk på 2000 lx ved sida av skjermen gjev same tal som jamt lys bak han. Ikkje endra, meld vidare.
