# Etterprøving: projektor, dei tre beste

Køyrt med `etterproving.py` (same motor, same watt, familie.py og funn.md urørte). Oppgåva var å prøve å felle kandidatane. Alle tre fell.

## Tala på nytt

Alle tal i funn.md blir att innanfor 2 %, òg topp, sprang og lm på skjermen. Einaste avvik over 5 %: zoom, vegg i stemning, 4,5 lx mot 5 i funn.md (avrunding, 0,5 lx).

## To feil i verknadsgraden i familie.py

1. **Maska i trakta er ikkje rekna.** For optikken «trakt» tel `lumen_per_watt` alt lys som kjem ut av trakta (66 x 48 mm) og går gjennom linsa, men maska stengjer lyset utanfor opninga. Monte Carlo med maska i utgangsplanet:
   - dele-vindauge: maska er 51 x 42 mm (1344 mm²). Berre 0,47 av lyset kjem gjennom med trakta slik ho er, 0,62 med trakta tilpassa maskeboksen.
   - zoom: sola er Ø 40 mm (1257 mm²). Faktoren er 0,45 med trakta som ho er, 0,76 med tilpassa trakt.
   - Konsekvens: dele-vindauge får W350 3,8 (2,9), vegg i arbeid 50 (66) lx og vegg i stemning 43 (56) lx. Zoom får W350 4,1 (2,4).
2. **Kjelda over fresnelplata når ikkje maska.** Golv-dele set «hale 0,90», altså at 90 % av kjeldelyset fell i sirkelen rundt maska. Lykta i modellen (G_LYKT: Ø 25 mm og ±20°) står 0,60 m over plata og lagar ein flekk på om lag 440 mm. Maska er Ø 115 mm, så berre 0,069 av lyset treffer ho. Étendue-taket er 0,034. Ein telefonlykt (±35°) gjev 0,019. W350 blir då om lag 60 til 120 W, ikkje 4,58. For at taket skal bli 1, må kjelda ha ei opning på om lag Ø 136 mm.

## Andre augehøgder (F1: 25 til 60 cm)

| Auge over bordet | dele-vindauge, arbeid | golv-dele, arbeid | zoom, arbeid / stemning |
| --- | --- | --- | --- |
| 0,25 m | 2301 cd/m² (over 1500, F5) | 3560 (auget står i strålen) | 3552 (over 3000, F1) / 852 (over 500) |
| 0,47 m | 358 | 169 | 324 / 167 |
| 0,60 m | 358 | 169 | 324 / 167 |

Luminansen på 0,25 m kjem frå spruten frå linseopninga (2 % ANTAKING) og fell bort berre fordi brønnen på 45° skjuler han for auget i 47 cm. Spruten veks lineært. Ved 5 % sprut blir dele-vindauge om lag 5700 cd/m² frå 25 cm, og då bryt ho F1. Golv-dele: på 25 cm ligg hovudet til brukaren i strålen frå hylla, og då skuggar hovudet feltet. SATIN er ikkje brukt i nokon av dei tre, så prøva med sigma og rd gjeld ikkje. Strekk er 0, fordi det ikkje finst noko ark. Lyspunkta står framfor skjermplanet (y 0,40 og -0,55), og ingen blir spegla i skjermen.

## Dom

**dele-vindauge: held ikkje.** Ho var «den einaste som held F6», men når maska blir rekna, fell veggen til 50 til 66 lx. Jamnheita er 0,24 (F3 «jamt», referansen er 0,6), og dele-fyll viser at det kostar meir enn 5 W å rette ho. Frå 25 cm er luminansen 2301 cd/m², som bryt F5. Overgangen er god (topp 0,93, sprang 0,06, 2 til 3 lm på skjermen), men vindauget blir ein kile på veggen, og ein frontflatespegel som glid inn framfor linsa, ser ut som ein projektor, altså teknisk. Bygg: krev ei linse på 60 mm, ein LED på 5 W med drivar og ei spegeltrakt. Ingen av delane er i byggjesettet, så berre prinsippet kan prøvast i golvriggen. Northern: spegelklaffen er eit fjerde formelement og synleg mekanikk (R1, «enkel»), og skyvet er ikkje eit messingpunkt (R5) utan motor. Den mjuke kanten held «mjuk».

**golv-dele: held ikkje.** Verknadsgraden er overvurdert 13 til 26 gonger (feil 2), så F3 fell med kjelda i modellen. Veggen får 43 lx (F6). Lampa er ei hylle på 600 x 285 mm, inga flyttbar lampe (F8, F9). På 25 cm står hovudet i strålen. Bygg: riggen kan setjast opp på éin dag for 0 kr (hylle, plate, telefonlykt, papp, linse på stolpen, spegel på papphengsel). P1 til P3 (fokus, skala, kant) kan prøvast, men telefonlykta gjev om lag 2 % av lyset funn.md reknar med, så lux-føreseiingane må lesast relativt, og rommet må vere mørkt. Northern: plate, linse, stolpe, kjelde og spegel er fem element (R1, «enkel»), og optikken er hovudmotivet («varm»).

**zoom: held ikkje.** Likskapen er 0,94, så etter definisjonen i motoren er ho ein dimmar, ikkje ein overgang mellom to lys (F2). Veggen får 5 til 18 lx (F6). Stemninga er ein lysmynt med skarp kant på 13 mm, og det bryt «mjuk». Frå 25 cm er luminansen 3552 cd/m², over 3000 (F1). Verknadsgraden er overvurdert med faktor 0,45 til 0,76 (feil 1). Bygg: same manglar som dele-vindauge, men prinsippet kan prøvast ved å skyve linsa i golvriggen. Northern: ein zoomring er ikkje eit messingpunkt (R5).

## Nabo (to søk)

- Framing-projektor med zoom: Times Square SoHo Mini, 7,5 W LED, zoom 25 til 40°, rammeskodder: https://www.filmandvideolighting.com/times-square-soho-mini-led-projector.html. Dedolight DP1 gjev mjuk eller skarp kant: https://www.bhphotovideo.com/c/product/125760-REG/Dedolight_DP1_Projection_Attachment_w_85mm_f_2_8.html. Dette er nærast zoom og golv-dele, men for galleri og ikkje heim.
- Bordlampe med kondensor og lysbilete: Hammacher «Slide Projection Table Lamp»: https://hammacher.com/product/slide-projection-table-lamp.
- Eg fann inga lampe som deler strålen med ein spegel mellom vegg og bord (dele-vindauge). Prinsippet ser ut til å vere nytt, men det er òg det einaste av dei tre som ikkje er prøvd fysisk.

## Det som står att

Funn 4 i funn.md held i tala: ein overgang som deler, er saumlaus. Det kan lånast av andre familiar utan linse. Feil 1 og 2 ligg i familie.py, ikkje i motoren. I lysskisse.py fann eg ingen feil. Ein avgrensing er verd å merke seg: `L_lampe` tek ikkje omsyn til kvar auget ser, så golv-dele bak brukaren blir rekna som synleg.
