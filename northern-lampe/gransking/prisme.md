# Gransking · prismeoptikken i (c)

**Kort.** Designlova i `form04/motor.py` `optikk()` er rett rekna, men ho er ei lov for ei tenkt plate: ei line utan breidd, ingen stigeveggar og berre strålar i snittet. Ein strålesporar med verkelege riller (deling 0,8 mm, aktiv fasett τ(s) og loddrett stigevegg) og 3D-retningar gjev same totale verknadsgrad (0,742 mot 0,739), men berre 0,630 av LED-fluksen hamnar i vifta. 16 til 21 % av lyset ned treffer ein stigevegg (premissen er 5 % tapt), og skeive strålar vert overbøygde. Det endrar tre tal mest: U0 fell frå 0,69 til 0,38 til 0,41, ansiktslyset har ein topp på 3 200 til 4 000 cd/m² (ikkje 659 i snitt), og luminansen mot auga i arbeid er 300 cd/m² i snitt med ein glans på 2 600 til 3 100 cd/m² (ikkje 11). Fluksen for 500 lx aukar berre 6 til 11 % (433 til 459 eller 482 lm). Slipp på stigeveggane (β opp til 25°) rettar mest.

Skript: `prisme.py` (om lag 2 min, éin tråd). Tal: `prisme.json`. Figur: `prisme.png`.

## Metode og kontroll av eigen kode

Eigen strålesporar (numba), ingen kall til `felles.py` eller `motor.py`. Geometri i snittet (s fram, z ned frå LED-aksen), retningar i 3D, så skeive strålar vert brotne etter Snell på vektorform. Kvar flate: upolarisert Fresnel, totalrefleksjon, Monte Carlo-val mellom refleksjon og transmisjon, opp til 60 sprett. Renne som i `geometri()`: veggar ±8 mm ned til 5 mm under lina, svarte (som motoren). Plate PMMA n 1,49, overside 50 mm under lina, botn 53 mm, 200 riller à 0,8 mm under botnen. Kinn i endane stoppar strålar som går ut forbi |x| 0,30.

| Kontroll | Resultat |
|---|---|
| Designlova attgjeven (τ, vifte, innfall, η) | τ −64,51° til +65,30°, vifte −16,70° til +15,95°, innfall maks 30,6°, η 0,7388. Likt `tal.csv`. |
| Min fjernfeltkode med designfordelinga | Φ 432,7 lm, U0 0,68, Ev 40,0 lx, R 1,00. Likt motoren (432,7; 0,688; 40,0; 1,0). |
| Flat plate, normalt innfall | T 0,9257 mot teori 0,9254 (fleire sprett). |
| Skeive strålar gjennom flat plate | ut parallell med inn, største avvik 1·10⁻⁶ °. |
| Reine to-flate-strålar mot lova | θ ut avvik median 0,12°, 95 % under 0,26°. |
| Deling 0,4 mot 0,8 mm (utan avrunding) | 0,631 mot 0,630 i vifta. Geometrisk optikk er skalafri, som venta. |

## 1 · η og vinkelfordelinga G(θ)

| Variant | samla | ut ned | i vifta | utanfor vifta | ned som trefte stigevegg | 95 % av fluksen ned |
|---|---|---|---|---|---|---|
| motoren (premiss) | 0,848 | 0,739 | 0,739 | 0 (+1 % strø) | 5 % tapt | −17° til +16° (+4° matt) |
| 2D, line, loddrett | 0,848 | 0,789 | 0,671 | 0,117 | 21,2 % | −57° til +56° |
| 3D, line, loddrett | 0,848 | 0,746 | 0,641 | 0,105 | 17,3 % | −53° til +52° |
| **3D, 5 mm, loddrett** | **0,839** | **0,742** | **0,630** | **0,112** | **16,0 %** | **−57° til +56°** |
| 3D, 10 mm, loddrett | 0,809 | 0,719 | 0,606 | 0,113 | 14,8 % | −60° til +59° |
| 2D, line, slipp | 0,848 | 0,790 | 0,778 | 0,012 | 2,2 % | −19° til +19° |
| 3D, 5 mm, slipp | 0,839 | 0,747 | 0,675 | 0,073 | 6,9 % | −36° til +35° |
| 3D, 10 mm, slipp | 0,810 | 0,725 | 0,646 | 0,079 | 6,6 % | −45° til +43° |

«i vifta»: θ innanfor −17,2° til +16,4° før mattering, i delar av LED-fluksen. Resten av fluksen går opp (5 % i 2D, 8 til 9 % i 3D: Fresnel frå oversida og totalrefleksjon av skeive strålar) eller tilbake i renna (1 %).

**Stigeveggane.** Ytst bøyer rilla 58° inn til 16° ut (42° avbøying). Utgangsstrålen går då mot neste stigevegg, som står 1,69 mm ned (h/p 2,1). I den ytste rilla går ein utgangsstråle i veggen om han går ut frå dei øvste 38 % av fasetten, og innanfrå får berre dei øvste 40 % lys. Treffdel per sone (3D, 5 mm): 4 % ved midten, 16 % ved ±2 til 4 cm, 33 % ved ±4 til 6 cm, 55 til 56 % ytst. Lyset vert ikkje borte: om lag tre firedelar går inn gjennom veggen (Fresnel ved om lag 74° innfall), inn i neste tann og ut i to lober ved ±50 til 60° (sjå `prisme.png`). Av LED-fluksen hamnar 3,8 % likevel i vifta og 8,1 % utanfor. Målt som det vifta mistar (2D med og utan slipp, 0,671 mot 0,778) er det 14 % av lyset ned, mot premissen 5 %. Premissen RISS 0,95 er altså feil i storleik og i art: det meste er strølys, ikkje tap.

**Skeive strålar.** Rillene er rekna i snittet. Ein stråle med x-del ser ein større effektiv indeks og vert overbøygd. Ved φ 40° (lova: θ 12,1°): dx 0,3 gjev 9,6°, dx 0,5 gjev 3,7°, dx 0,7 gjev −14,6°. Ved φ 55° og dx 0,7: totalrefleksjon. For ein lambertsk kjelde har 39 % av fluksen |dx| over 0,5. Lyset vert drege frå kantane av vifta inn mot midten. Motoren skil G(θ) og cos ξ, og ser ikkje dette.

**LED-breidd.** Rillene er rekna for ei line. Med 5 og 10 mm ser kvar rille lina under ein vinkel på 5,7° og 11,4° ved midten (1,6° og 3,2° ytst), og vifta vert like mykje uklar i kantane. Renna klipper meir (samla 0,848, 0,839, 0,809), og med 10 mm kan auget sjå lina forbi platekanten (del 3).

## 2 · Scene: illuminans, skjerm, stemning, ansikt

Nærfelt: strålane går ut der dei faktisk går ut av plata, mot bord, vegg, skjerm, søyle og ei augerute ±3 cm. Celler ±1,5 cm rundt dei 7 × 5 oppgåvepunkta, ±2,5 cm på veggen (8 × 6) og bordet (8 × 5). 4° mattering som motoren.

| | motoren | 3D line | **3D 5 mm** | 3D 10 mm | 3D 5 mm slipp | 3D 10 mm slipp |
|---|---|---|---|---|---|---|
| Φ for 500 lx (lm) | 433 | 456 | **459** | 482 | 432 | 455 |
| U0 (7 × 5) | 0,688 | 0,41 | **0,38** | 0,40 | 0,50 | 0,53 |
| E på skjermen, snitt (maks) lx | 8,8 (37,5) | 15,3 (33) | **13,9 (33)** | 13,4 (32) | 19,1 (52) | 19,0 (53) |
| R_stem | 1,00 | 0,975 | **0,978** | 0,979 | 0,981 | 0,980 |
| Ev stemning, 8 × 6 (lx) | 40,0 | 25,3 | **25,4** | 26,1 | 26,0 | 26,7 |
| Ev stemning, heile feltet (lx) | 41,7 (designlova, mi rekning) | 40,2 | **40,0** | 40,4 | 39,1 | 39,6 |
| L vegg, 8 × 6, ρ 0,75 (cd/m²) | 9,5 | 6,0 | **6,1** | 6,2 | 6,2 | 6,4 |
| Φ for 150 lx ved auga (lm) | 79,3 | 76,6 | **77,6** | 80,2 | 81,1 | 83,1 |

- **U0 er det største avviket.** Illuminansen er ikkje jamn i y: midtradene ligg på 1,3 til 1,5 gonger snittet, fremste og bakaste rad på 0,4 til 0,7, hjørna lågast (x ±0,30, y 0,40). Skeive strålar (2D gjev U0 0,58 i fjernfelt, 3D 0,34) og stigeveggane (designfordelinga 0,68, 2D med veggar 0,58) tek kvar sin del. Golvet er 0,40 i `felles.py`.
- **Φ** aukar 6 % (5 mm) og 11 % (10 mm). Kinna tek 5,4 % av LED-fluksen, oppgåvesona får 26 %.
- **Skjermen** får lys frå bakkanten av plata: frå y 0,30 går den bakre kanten av vifta (−16,7°) ned i skjermen under z 0,15. Motoren reknar vifta frå LED-aksen og ser det ikkje. Min fjernfeltkode gjev 7,3 lx med designfordelinga og 20,4 med den spora, nærfeltet 13,9. Tala er små mot (a) og (b) (611 og 652 lx).
- **Stemning.** På motoren sitt eige 8 × 6-gitter er veggen 37 % svakare (25 mot 40 lx), fordi vifta på veggen vert smalare og lysare i midten. Arealsnittet er nær uendra (40 lx). Om lag 4 % av fluksen går i søyla.
- **Ansiktslys:** Φ150 77 til 83 lm, nær motoren (79).

## 3 · Luminans mot auga: topp, ikkje snitt

Bakoversporing frå tre augepunkt (og midtauga skrått mot enden av plata), 400 strålar per 0,5 mm av plata, startpunkt rett under rillene slik at matteringa verkar ved plata. Toppen er glidande snitt over 1 mm (om lag éi rille) og over 1 cm. Kjelda er ei jamn lambertsk stripe, L_LED = Φ/(π w L). Tal i cd/m² med Φ frå same variant.

| Tilstand | Variant | L_LED | blank, topp 1 mm | 4° matt, topp 1 mm | 4° matt, topp 1 cm | snitt over plata | motoren |
|---|---|---|---|---|---|---|---|
| ansikt α +70° | 5 mm, loddrett | 8 230 | 7 550 | **3 680 til 3 960** | 3 370 | 568 | 659 (snitt) |
| ansikt α +70° | 10 mm, loddrett | 4 260 | 3 980 | **3 130 til 3 170** | 2 930 | 570 | 659 |
| ansikt α +70° | 5 mm, slipp | 8 600 | 8 070 | 4 040 til 4 290 | 3 650 | 555 | |
| ansikt α +70° | 10 mm, slipp | 4 410 | 4 170 | 3 330 til 3 380 | 3 130 | 562 | |
| arbeid α 0° | 5 mm, loddrett | 48 700 | 25 000 | **2 920 til 3 110** | 2 050 | 299 | 10,6 |
| arbeid α 0° | 10 mm, loddrett | 25 600 | 16 000 | 2 590 til 2 750 | 1 950 | 291 | 10,6 |
| arbeid α 0° | 5 mm, slipp | 45 800 | 1 030 | 690 til 740 | 195 | 15 | |
| arbeid α 0° | 10 mm, slipp | 24 100 | 690 | 420 til 480 | 220 | 19 | |

Spennet i topp 1 mm er to uavhengige frø.

- **Ansiktslyset er ikkje mjukt med 4° mattering.** Auget ser biletet av LED-stripa i ei stripe på plata 0,5 til 1,5 cm bak midten. Blankt er luminansen 0,92 til 0,95 av L_LED. 4° mattering tek toppen ned til om lag 49 % (5 mm) og 80 % (10 mm) av blank topp, ikkje meir. Toppen er 5 til 6 gonger snittet motoren rapporterer.
- **Arbeid:** stigeveggane sender ein glans mot auga frå s ≈ +5 cm (lober ved +50 til 60°). Snittet mot auga er 300 cd/m², ikkje 10,6 (motoren sitt tal er berre premissen 1 % strølys). Toppen ligg rett under 3 000 og over 1 500, som er grensa for ein skjerm på 200 cd/m² (sjå `fotometri.md`). Med slipp fell han til 420 til 740.
- **Innsyn forbi platekanten (arbeid, auga 64° frå loddrett).** Med 10 mm stripe ser auget 2,55 mm av lina direkte, over heile 60 cm, med full LED-luminans (25 600 cd/m² ved 482 lm). Med 5 mm er det 0,05 mm, med line ingenting. Det er geometrien til renna (veggane går berre 5 mm under lina) og gjeld begge stigeveggtypar.
- **Diskrete LED-ar.** Plata har ingen styrke langs x. Med LED-pakkar i staden for ei jamn stripe ser auget kvar pakke (4° mattering gjev 3,5 mm uklarleik 5 cm frå lina), og toppen er pakkeluminansen. Konseptet krev ei samanhengande COB-stripe.

**Kva mattering trengst?** (nærfelt og bakoversporing, same frø)

| σ | profil | w | Φ (lm) | U0 | skjerm snitt (maks) lx | Φ150 | ansikt topp 1 mm | arbeid topp 1 mm |
|---|---|---|---|---|---|---|---|---|
| 4° | loddrett | 5 / 10 mm | 459 / 482 | 0,38 / 0,40 | 13,9 (33) / 13,4 (32) | 78 / 80 | 3 960 / 3 130 | 3 110 / 2 750 |
| 6° | loddrett | 5 / 10 mm | 479 / 498 | 0,45 / 0,47 | 24,2 (47) / 23,3 (50) | 82 / 85 | 2 950 / 2 610 | 1 970 / 1 820 |
| 8° | loddrett | 5 / 10 mm | 501 / 522 | 0,55 / 0,54 | 39,7 (68) / 39,1 (72) | 88 / 92 | 2 470 / 2 290 | 1 930 / 1 560 |
| 4° | slipp | 5 / 10 mm | 432 / 455 | 0,50 / 0,53 | 19,1 (52) / 19,0 (53) | 81 / 83 | 4 290 / 3 380 | 690 / 420 |
| 6° | slipp | 5 / 10 mm | 452 / 474 | 0,53 / 0,53 | 31,7 (72) / 31,2 (76) | 84 / 85 | 3 110 / 2 700 | 660 / 470 |

Grensa på 3 000 for ansiktet ligg mellom σ 6° og 8° for 5 mm og ved σ 6° for 10 mm. Sterkare mattering hjelper U0 òg, men kostar 4 til 9 % fluks og 10 til 25 lx meir på skjermen.

## 4 · Produserbarheit

- **Loddrette stigeveggar:** ytste tann 1,69 mm djup ved 0,8 mm deling (h/p 2,1), tuppvinkel 90° − 65,3° = 24,7°, null slipp på 200 veggar over 60 cm. Det er krevjande å fylle og å avforme, anten det er sprøytestøyping eller pressing, og eit diamantverktøy med 25° spiss er skjørt. Rillene går langs x og er like over heile lengda, så rullepreging ved ekstrudering eller pressing passar betre enn sprøytestøyping av 60 × 16 cm.
- **Med slipp** (β = ½(maks(θ·sgn τ, 0) + |φ_i|), opp til 25,4°): tanna er 0,85 mm (h/p 1,06), tuppvinkelen 50°, og veggane har 0° til 25° slipp. Same grep som rettar optikken gjer plata lettare å lage.
- **Avrunding 10 µm i alle tuppar og dalar:** 1,6 % (loddrett) og 1,9 % (slipp) av lyset ned rører ein avrunda kant. I vifta: 0,630 til 0,627 og 0,675 til 0,665. Φ +1,7 % og +1,6 % (467 og 439 lm). Tapet går som r/p: ved 0,4 mm deling om lag det dobbelte (ikkje køyrt). Dei lysande delane av fasettane ligg ved dalen (den grunne enden), så tuppavrundinga rører lite lys.
- Vinklane opp til ±65° og innfall opp til 31° gjev ingen totalrefleksjon i snittet. I ytre sone vert skeive strålar totalreflekterte frå |dx| mellom 0,5 og 0,7.
- Om rillene vert plasserte etter treffpunktet på oversida (som `geometri()`) eller på undersida: skilnaden er 0,2 prosentpoeng.

## Utanfor linsa, men det rører stemningstala

Plata går inn i armen frå α ≈ −55° (plateovekanten når z 0,73 ved y 0,31; armen ligg i x ±0,05, z 0,73 til 0,76). `kollisjon()` i `form04/motor.py` sjekkar ikkje armen. Stemningsstillinga −105° kan ikkje nåast med armen slik han er teikna. Hovudet sveipar ein radius på 9,6 cm om LED-aksen, armen ligg 3 cm over.

## Funn og rettingar

- **P1 (kritisk).** `form04/motor.py` `optikk()`, `RISS = 0.95`: stigeveggane tek 16 % (3D, 5 mm) til 21 % (2D) av lyset ned, og det går ut som strølys ved ±50 til 60°, ikkje som tap. I vifta 0,630, ikkje 0,739. *Retting:* gje stigeveggane slipp β(s) = ½(maks(θ·sgn τ, 0) + |φ_i|) i profilen, og byt `RISS` og den reint analytiske G(θ) i `optikk()` med tabellen frå `prisme.py` (`G_tab`, 3D, 5 mm, slipp). Venta: i vifta 0,675, utanfor 7,3 %, Φ 432 lm, U0 0,50.
- **P2 (kritisk).** `optikk()` og `I_mot()`: G(θ)·cos ξ føreset at skeive strålar vert brotne som strålar i snittet. Dei vert overbøygde, og U0 fell frå 0,688 til 0,38 til 0,41 (loddrett) og 0,50 til 0,53 (slipp), under eller nær golvet 0,40. *Retting:* rekn I(θ, ξ) med 3D-sporing i staden for G(θ)·cos ξ. For å nå U0 over 0,5 med margin: slipp og σ 6° (U0 0,53, Φ 452 til 474 lm). Ei 3D-designlov (fasettvinkel for fluksvege skeiv indeks) er ikkje prøvd.
- **P3 (kritisk for briefen).** `sok()` og `L_mot()`: ansiktslyset er rapportert som snitt (659 cd/m²). Toppen er 3 130 til 3 960 cd/m² med 4° mattering (blank 4 000 til 7 600). *Retting:* rekn toppen (bakoversporing som `luminans()`), og set σ ≥ 6° (10 mm stripe: 2 610 til 2 700) eller σ 8° (5 mm: 2 470). Kostnad: Φ +4 til 9 %, skjerm 23 til 40 lx.
- **P4 (middels).** `STRO = 0.01` og `L_mot()` i arbeid: 10,6 cd/m² er premissen. Spora: 300 cd/m² i snitt, glans 2 600 til 3 100 cd/m² frå s ≈ +5 cm (blank 16 000 til 25 000). *Retting:* slipp på stigeveggane (snitt 15 til 19, topp 420 til 740).
- **P5 (middels).** Renna i `geometri()` (veggar 5 mm under lina) med 10 mm stripe: auget ser 2,55 mm av lina forbi platekanten, 25 600 cd/m² over 60 cm. *Retting:* krev ei stripe på høgst 5 mm (innsyn 0,05 mm) eller rennevegger minst 7,6 mm under lina (analytisk, kostar fluks frå kanten av stripa). Med 10 mm stripe fell òg samla til 0,809.
- **P6 (middels).** `tal.csv` Φ 433 lm: spora 459 (5 mm) og 482 (10 mm), med slipp 432 og 455, med slipp og σ 6° 452 og 474. Batteritida går ned i same forhold (4,5 t til 4,0 til 4,2 t utan slipp). `kontroll_fluks()` syner berre at G(θ) er normert, ikkje at plata kan lage han.
- **P7 (middels).** Stemning i `sok()`: Ev_stem 40 lx på 8 × 6-gitteret vert 25 til 27 lx (arealsnitt 39 til 40), R_stem 0,975 til 0,98. Og stillinga −105° er ikkje nåeleg (plata i armen frå −55°). *Retting:* legg armboksen inn i `kollisjon()`, flytt hengslet til endane eller løft armen minst 10 cm over aksen, og rekn stemninga på arealsnitt.
- **P8 (liten).** `skjerm.json` 8,8 lx: nærfeltet gjev 13,4 til 15,3 lx (maks 33), med slipp 19 (maks 53), med slipp og σ 6° 31 (maks 76). Framleis 20 til 47 gonger under (a) og (b).
- **P9 (liten).** Produserbarheit: loddrette veggar gjev tenner på 1,69 mm, h/p 2,1, tupp 24,7°. Slipp gjev 0,85 mm, 1,06 og 50°. 10 µm avrunding kostar 0,3 til 1,0 prosentpoeng i vifta og 1,6 til 1,7 % i Φ ved 0,8 mm deling.
- **P10 (liten).** Lineær Fresnel blandar ikkje langs x: krev samanhengande COB-stripe, elles syner plata LED-prikkane med pakkeluminans.

## Kva det endrar i samanlikninga (a), (b), (c)

- **Energi:** (c) treng framleis om lag 63 % mindre fluks enn (a) og (b) (459 til 482 mot 1 256 og 1 311 lm). Fordelen står.
- **Jamnleik:** (c) gjekk frå 0,69 (mellom (a) 0,76 og (b) 0,67) til 0,38 til 0,41, altså lågast og under golvet. Med slipp 0,50 til 0,53, framleis lågast.
- **Ro ved skjermen:** står. 14 til 32 lx mot 611 og 652.
- **Blending i arbeid:** (c) er framleis klart betre enn (a) og (b), men ikkje 11 cd/m²: 300 i snitt og ein glans nær 3 000 utan slipp.
- **Ansiktslys:** (c) er ikkje «mjukt» under 3 000 cd/m² med 4° mattering. Det krev σ 6 til 8°.
- **Stemning:** (c) fell frå 65 % til om lag 40 % av (a) på 8 × 6-gitteret, og stillinga −105° må teiknast om.
- Konklusjonen «trefjerdedelar mindre lys fordi lyset går dit det trengst» held i energi, men «ingenting utanfor vifta» held ikkje: 11 % av LED-fluksen (7 % med slipp) går utanfor.
