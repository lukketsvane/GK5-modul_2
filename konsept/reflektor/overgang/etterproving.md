# OVERGANG: etterprøving av dei tre beste

Tal frå `etterproving.py` (utskrift i `etterproving.txt`, tillegget med `python etterproving.py tillegg`). Modell, ikkje måling. Målet var å felle kandidatane. Ingen av dei tre held.

## Tala held
Alle tal i funn.md for dei tre kom att innanfor 2 % (W350, felt, jamnheit, auge, vegg, ansikt, stemning, likskap, topp, skjermflata). Einaste avvik over 5 % er sprang for kryss-hog: 0,043 mot 0,04 i funn.md, som er avrunding. Strekk er 0 for alle tre, og alle ark er flate, så det er rett.

## Det som fell for alle tre
1. **Auget i 25 cm.** F1 gjeld 25 til 60 cm, motoren måler berre 47 cm. Mot auget i arbeid (cd/m²):

| | 47 cm | 60 cm | 25 cm | 25 cm, sigma 14 | 25 cm, rd 0,3 | 47 cm, rd 0,3 |
| --- | --- | --- | --- | --- | --- | --- |
| kryss-hog | 555 | 555 | 2581 | 3587 | 2700 | 1111 |
| skjer | 1338 | 1338 | 4111 | 7137 | 4442 | 2676 |
| drei-snigel | 2311 | 2311 | 2916 | 8253 | 4753 | 4622 |

Frå 47 cm og opp ser auget berre den diffuse delen av satinflata (1338 for skjer er rd åleine, han doblar seg med rd 0,3). I 25 cm treff loba auget. Skjer bryt F1 (over 3000) med SATIN som han står. Kryss-hog bryt F5 i 25 cm og F1 om loba er 14 grader. Drei-snigel bryt F5 i alle høgder og F1 med rd 0,3 eller sigma 14.
2. **SATIN avgjer òg feltet.** Sigma 6 gjev 15 til 21 % meir på feltet, sigma 14 gjev 15 til 21 % mindre (kryss-hog W350 5,33, over 5 W). Overgangstala (topp, sprang, likskap) flyttar seg høgst 0,03. Mekanismen held, luminansen gjer det ikkje.
3. **Veggen er skeiv.** Delt opp i arbeid (lx): kryss-hog venstre 27, over skjermen 106, høgre 131 (bak skjermen 301, gøymt). Skjer 13, 33, 31. Drei-snigel 12, 152, 23. Ingen gjev ein jamn krans rundt skjermen. Påstanden i funn.md om at vaskaren ikkje lyser bak skjermen, er feil: han lyser mest der, der ingen ser det.
4. **Skjermlux er lågt rekna.** `skjermlux()` i familie.py gjev 66, 114 og 132 lx. Motoren sin `E_skjerm_maks` (med indirekte lys) gjev 96, 181 og 177, det vil seie 23 til 24 % av feltet for skjer. Føreseiing 2 i funn.md (under 15 %) kviler på den lågaste målemåten.

## kryss-hog: held ikkje
- Fysikk: arket fangar 90 % av kjeldestrålen, spillet (10 %) går mot veggen. Kjelda og vaskaren står i y 0,48 og 0,53, bak skjermplanet, men til sides for skjermen, så skuggen fell ikkje på feltet. Ingen kjelde er synleg frå stolen (brønnen dekkjer). Modellen har tre kjelder (stemningsstrøk, kjelde under arket, vaskar), ikkje to slik meldinga seier.
- Krav: F3 393 lx held så vidt på 5 W og fell med sigma 14. F5 og F1 fell i 25 cm. F6 held i snitt (126), men skeivt. F2 er éi handling, men les som ein dimmar: E3 og «utan å verke teknisk» held ikkje.
- Bygg: tre lyskjelder, byggjesettet har éi telefonlykt. Spak, tråd og tre papp-spjeld går på ein dag om ein låner to telefonar til.
- Northern: R3 og R5 held. R1 og «enkel» brest: fot, stolpe, hovud med vifte, ark og vaskar er fem formelement.

## skjer: held ikkje
- Fysikk: arket fangar 94 % i arbeid, spillet går høgt på veggen (over sona 15 lx). Arket står i y 0,29 til 0,52, til høgre for skjermen. Kjelda ligg 63 grader frå auget, gøymd i brønnen.
- Krav: F1 fell i 25 cm (4111 cd/m²). F5 1338 i 47 cm er på grensa og går over med sigma 14 (1472) eller rd 0,3 (2676). F6 fell (29 lx). Stemninga er ein flekk over og til høgre for skjermen (114 og 109 lx), ikkje rundt han.
- Bygg: éi lykt, eitt foliekledd ark og eit pappspor. Går på ein dag for null kroner. Det som manglar, er ei måling av lobebreidda på folien.
- Northern: plate på fot, éi handling som syner. R1 og «enkel» held. Mjuk fell om lyskanten frå strålen som går forbi arket blir skarp på veggen.

## drei-snigel: held ikkje
- Fysikk: skiva på 36 cm går 13 fliser inn bak skjermflata (y til 0,56, x under 0,27, i høgda til skjermen). Ho kolliderer med ein verkeleg skjerm. Spill 12 %, mest som krans høgt på veggen.
- Krav: F5 fell i alle augehøgder (2311 til 2916). F1 fell med rd 0,3 eller sigma 14. F6 fell (55). Jamnheit 0,24 er lågast av dei tre.
- Bygg: enkelt (skive, nål, éi lykt), men riggen må flyttast for at skiva skal gå klar av skjermen, og då gjeld ikkje tala.
- Northern: rund skive i eit hovud er mjuk. Spiralkanten er ei sag på 1,6 cm i modellen.

## Næraste nabo
- kryss-hog: Occhio «up/down fading» (Gioia tavolo, Mito) kryssdimmar opp- og nedlys med éi handbevegelse: https://occhio.com/about-light/light-quality/light-up-down-fading. Prinsippet finst og er seld.
- skjer og drei-snigel: fann inga lampe med ei plate som blir skoven eller dreidd inn i ein stråle. Nærast er 101 Copenhagen Reflect, der ein vippar reflektoren: https://www.salonemilano.it/en/prodotti/101-copenhagen/reflect-table-lamp.

## Motoren
Ingen ny feil. `tal()` måler luminans frå éi augehøgd, så F1 må prøvast ved å flytte AUGE. Den kjende feilen står: `Ark.__init__` skriv over `k.lm_ut`, så to ark på éi kjelde må rettast for hand (gjeld ikkje dei tre her).

## Viktigaste innvending
Alle tre kviler på SATIN og på eitt auge i 47 cm. Med auget i 25 cm eller ei lobe på 14 grader går skjer og drei-snigel over 3000 cd/m², og kryss-hog over 1500. Mål lobebreidda på folien med telefonlykta før nokon av dei blir bygd vidare.
