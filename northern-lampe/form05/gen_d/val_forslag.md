# gen_d · tre framlegg

Dato: 13.11.2026. Tala er frå `tal.csv` (grovt gitter, same som tal-D.json) og frå det fine gitteret i `tal.json` under «fin» (arealsnitt, celler på 4 cm). Lys og mekanikk er rekna, mål frå byggjesettet er anslått frå foto, og ingenting er målt. **Filmen er rekna som ideelt 90°-prisme (ANTAKING).** Fingerdytten er 5 N (ANTAKING). Designaren vel.

| | (a) D med Ø240 | (b) Plata under skjermen | (c) Vassrette riller |
| --- | --- | --- | --- |
| Kropp | 1, foten 12 cm i radius | 9 | 5, foten 13 cm i radius |
| Rute, helling, riller | 45 × 19, 10° mot brukaren, loddrett | 52 × 16, 10°, loddrett | 36 × 24, 10°, vassrett |
| W for 350 lx (grovt / fint) | 3,68 / 3,69 | 3,84 / 3,94 | 3,33 / 3,31 |
| Jamnheit (grovt / fint, referanse 0,6) | 0,62 / 0,51 | 0,61 / 0,51 | 0,69 / 0,58 |
| Mot auget 25 / 47 / 60 cm (F5 1500) | 1011 / 143 / 143 | 778 / 144 / 144 | 568 / **1877** / 1308 |
| Augevolum, høgaste (cd/m²) | 2140 | 2297 | 2433 |
| Spegling i blank skjerm, tilta 0 til 20° (cd/m²) | 18 | 17 | 69 |
| Veggen bak skjermen (grovt / fint, F6 100 til 150) | 139 / 121 | 146 / 127 | 136 / 119 |
| Skjermflata (grovt / fint) | 188 / 195 | 198 / 191 | 125 / 129 |
| Ansiktet, F10 (50 til 200) | 34 | 35 | **149** |
| Stemning: mot auget, veggen (grovt / fint) | 242, 190 / 143 | 233, 179 / 142 | 242, 190 / 143 |
| Likskap stemning og arbeid | 0,41 | 0,41 | 0,41 |
| Masse utan skjerm | 3,76 kg | 2,08 kg (+ skjermen 3,5 kg, ANTAKING) | 4,29 kg |
| Tipp, statisk | 34° | 12,7° | 33° |
| Dytt på knotten som veltar | 5,6 N | 5,0 N | 5,6 N |
| Trykk ned på hjørnet av ruta som veltar | 6,5 N | 23 N | 5,4 N |
| Svikt i knotten / framkanten under 5 N | 0,14 / 1,1 mm | 0,22 / 1,3 mm | 0,14 / 1,1 mm |
| Knotten frå skulderen | 75 cm | 75 cm | 74 cm |
| Film frå P08 | eitt stykke | eitt stykke | to stykke, éi skøyt |
| Må skaffast utover LED | 273 mm profil, røyr 490 mm, stål 2,8 kg | 386 mm profil, røyr 560 mm, plate 1,1 kg | 364 mm profil, røyr 400 mm, stål 3,3 kg |

Mekanikken i (a) og (c) er rekna på nytt med den større foten (`motor.Kropp` med `r_fot` 0,12 og 0,13). Lyset er rekna med foten i tal.csv. Foten står utanfor feltet og skuggar det ikkje.

## (a) D med Ø240

Dette er kroppen og lyset Iver valde. Den einaste endringa er at foten veks frå Ø220 til Ø240. Med Ø220 veltar ein dytt på 3,8 N lampa, fordi armen sit i den eine enden og dreg tyngdepunktet 4,5 cm frå midten av foten. Foten treng 11,7 cm i radius, og det er plass til 12 cm mellom skjermplanet og veggen. Det kostar 0,45 kg stål. Svakheitene er dei same som i D. Jamnheita er 0,51 på det fine gitteret, under referansen på 0,6. Skjermflata får 56 % av lyset på feltet. Ansiktet får 34 lx, så F10 fell. Ruta lyser 2140 cd/m² mot eit auge som bøyer seg ned til 25 cm over bordet.

## (b) Plata under skjermen

Foten er borte frå bordet. Ei stålplate på 30 × 23 cm og 2 mm ligg under skjermfoten, og skjermen er ballasten. Kroppen er den lettaste (2,1 kg), og eit trykk på ruta veltar henne ikkje (23 N). Dytten på knotten er derimot akkurat på grensa (5,0 N), fordi plata ligg bak feltet og hylsteret har kort veg mot brukaren. Lyset er som i D, med ei lengre og smalare rute (52 × 16), og kostar 4 til 7 % meir watt. Alt står og fell på to antakingar: at skjermfoten får plass på plata, og at skjermen veg 3,5 kg.

## (c) Vassrette riller

Dette er den einaste vegen til F10 (149 lx på ansiktet) som er rekna her. Han gjev òg lågast watt (3,3 W) og minst lys på skjermen av dei tre (36 % av feltet). Prisen er F5: 1877 cd/m² mot auget i 47 cm og 69 cd/m² spegla i skjermen. Kropp 3 (vassrette riller, 25° opp, 52 × 16) syner det same frå den andre sida: 56 lx på skjermen og ingen spegling, men 1976 cd/m² i 25 cm. Med vassrette riller kjem ruta inn i synsfeltet. Framlegget er med for at avveginga skal syne, ikkje fordi det held. Rillene må dessutan skøytast, fordi P08 berre er 30,6 cm langs rillene.

## Det same for alle tre

- Knotten ligg 74 til 75 cm frå skulderen, utanfor 70 cm. Det gjeld heile familien, fordi alt sit i skjermplanet. Ein knott nærare brukaren krev ein kabel eller ein knott på bordet, og det er ikkje rekna.
- «Berre LED-stripa» held ikkje. Profil, røyr, stål eller plate, kvit plast og spreiar må skaffast. I tillegg trengst elektronikk for to kanalar (vindauge og rute), ein driver og ei straumforsyning.
- Rillene må peike mot brukaren (loddrett) for å halde F5. Ruta må stå mellom 180 og 190, altså mellom vassrett og 10° mot brukaren.
