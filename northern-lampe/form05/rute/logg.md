# form05 «Lysrute»: logg

Dato: 13.11.2026. Lampa ER vindauget: ei rute som sjølv lyser, med lysleiarplate og prismefilm. Skilnaden på **målt**, **rekna** og **anslått** er merkt i kvar linje. Alt rekna er modell, ikkje måling.

## Utgangspunkt

- Konseptbileta «Telt» og «Klemme» er genererte (stiane står i `konsept.md`). Dei er retning, ikkje fysikk.
- Fotoa av filmen mot vindauget (stiane står i `konsept.md`) syner **(målt, observert)**: lyse ting blir smurde ut på tvers av rillene, og regnbogekanten kjem på kantane som står på tvers av smøret. Biletet blir dregne ut til striper, ikkje delt rein i to. Det stemmer med at prisma er avrunda eller har ein spreiar i tillegg (som `konsept/film/00-vindauge-utan-linse.md` seier).
- `konsept/vindauge/film/arket.md` fanst **ikkje** kl. 15.20. Filmen er difor førebels det ideelle 90°-prismet frå `film.py` (n_d 1,59, Abbe 30). Dette er ANTAKING. Sjå «Filmprofil» under for siste sjekk.
- **ANTAKING: lysleiarplata finst ikkje i byggjesettet.** Ho er rekna som ei klar PMMA-plate (sjå `konsept.md`, bolken «Lysmotoren»).

## Køyringar (fortløpande)
- 15.34 kalib (196 s): film.py stemmer med 00-vindauge (prisme_0 {'T': 0.93, 'lober': [(-30.7, 0.47), (30.8, 0.47)]}, flat_0 {'T': 0.0, 'R': 1.0}, flat_30 {'T': 0.63, 'lober': [(-0.8, 0.61)]}, farge_450_650 [31.75, 30.25]). Motorane: E0 η 0.65, gain 1.05, halvvinkel y-z 90°; E1 η 0.53, gain 1.73, halvvinkel y-z 35°; E2 η 0.36, gain 2.47, halvvinkel y-z 21°
- 15.34 Flytta motor.py, logg.md og tal.json frå form05-rota til `form05/rute/` (hovudøkta: éin motor, i rute/). `film_tabell.npz` i rota er frå ein annan kopi og blir liggjande. Den første tretest-køyringa fall på stien til `konsept/film` etter flyttinga (retta).
- 15.34 **Funn (rekna) frå første kalib:** éin prismefilm har ein sidelobe på tvers av rillene: 0,03 av luminansen rett fram ved 40 til 50°, men 0,33 / 0,68 / 0,89 ved 60 / 70 / 80°. Langs rillene er det 0 frå 60°. Auget ser ruta frå sida, så rillene må peike mot auget (loddrett/kryss), ikkje ligge på tvers av synslina. Dette stemmer med `konsept/film/01-ruta.md` (0 frå 60° langs rillene, 160 cd per 1000 lm ved 70° på tvers).
- 15.36 Hovudøkta: `konsept/film/rute.py` (anna økt) har alt rekna ruta. Motoren her er **kalibrert mot rute.py** i staden for å finne opp rekninga på nytt: Rc 0,80 → 0,90 (rho i rute.py), kjelde «bak» = huset i rute.py (ingen ekstra tap), matt spreiar 0,90. Kjelde «kant» (lysleiarplata) har i tillegg ETA_KOPL · ETA_LEIAR = 0,72 (ANTAKING), og det er den einaste reelle skilnaden i lumen. Tabellane vart rekna om (kalib).
- 15.36 Motoren er gjort om til spesifikasjonar med identitetsparametrar (stotte, ruter, rille, kjelde, bak), så neste generasjon kan leggje til kroppar utan ny kode.
- 15.42 kalib (158 s) skreiv tab_ingen, tab_vassrett og tab_kryss
- 15.42 rutesjekk (7 s): fordelinga og lampa «over» mot rute.py: W350 10.73/10.71, jamnheit 0.03/0.03, bak350 112.82/112.37, skjerm350 57.88/54.65, auge25 6606.28/13539.98, auge47 653.25/662.95, s_auge25 769.71/1580.85, s_auge47 78.59/79.93, s_bak 13.41/13.39, s_felt 40.84/40.92
- 15.43 skann T kryss 90>0: W350 3.12 U 0.01 auge  338/  85/  85 bak  10 skjerm 117 | st: auge 261/973/995 bak   0 felt   0 skjerm 0.1 | lik 0.49
- 15.43 skann T kryss 110>0: W350 3.12 U 0.01 auge  338/  85/  85 bak  10 skjerm 117 | st: auge 322/306/940 bak   0 felt   1 skjerm 0.5 | lik 0.45
- 15.43 skann T loddrett 110>0: W350 3.65 U 0.01 auge  411/  70/  70 bak  13 skjerm 246 | st: auge 456/552/588 bak   1 felt   1 skjerm 0.9 | lik 0.65
- 15.43 skann T kryss-v 110>0: W350 3.11 U 0.01 auge  498/1949/  88 bak  20 skjerm 113 | st: auge  91/222/875 bak   0 felt   2 skjerm 0.7 | lik 0.41
- 15.43 skann T kryss 110>15: W350 3.68 U 0.01 auge  898/  88/  88 bak   5 skjerm  66 | st: auge 322/306/940 bak   0 felt   1 skjerm 0.5 | lik 0.59
- 15.43 skann T ingen 110>0: W350 6.68 U 0.02 auge 1884/1338/  64 bak  50 skjerm 487 | st: auge 317/321/315 bak   1 felt   2 skjerm 0.8 | lik 0.77
- 15.41 **Kalibrering mot rute.py held (rekna mot rekna):** éin film gjev same fordeling innanfor MC-støyen (rett fram 590 mot 589 cd per 1000 lm, verknad 0,89 mot 0,89). To filmar i kryss gjev same fordeling når ein byter om kva ark som ligg øvst (verknad 0,71 mot 0,68: her går lyset mellom dei to arka fleire gonger, i rute.py går det rett attende i huset). Lampa «over» frå rute-tal.json rekna med Rute-klassen her: 10,73 mot 10,71 W, jamnheit 0,03 mot 0,03, bak skjermen 113 mot 112 lx, auget 47 cm 653 mot 663 cd/m². Berre auget 25 cm skil (6 600 mot 13 500 cd/m² i arbeid): det ser ruta 80 til 88° frå normalen, der begge tabellane er grove. Begge er langt over F1, så konklusjonen står.
- 15.41 Det øvste arket avgjer kva veg sidelobane går. «kryss» er no det øvste arket loddrett (rillene mot auget, mørkt for auget frå 60°), «kryss-v» det øvste vassrett. Tabellen `motor` i tal.json vart rekna før dette skiljet: «kant-kryss» der er det som no heiter kryss-v.
- 15.43 skann K kryss 180>0: W350 2.91 U 0.56 auge  552/  82/  74 bak   8 skjerm  83 | st: auge   5/  5/ 49 bak   2 felt   4 skjerm 1.3 | lik 0.06
- 15.43 skann K loddrett 180>0: W350 3.43 U 0.68 auge  532/  65/  65 bak  11 skjerm 180 | st: auge   9/  9/ 64 bak   2 felt   5 skjerm 1.5 | lik 0.12
- 15.43 skann K kryss-v 180>0: W350 2.91 U 0.55 auge  365/1654/  77 bak  19 skjerm  93 | st: auge   9/  9/689 bak   7 felt   4 skjerm 1.3 | lik 0.04
- 15.43 skann K kryss -135>0: W350 2.91 U 0.56 auge  552/  82/  74 bak   8 skjerm  83 | st: auge  34/ 34/ 34 bak  13 felt   3 skjerm 1.8 | lik 0.07
- 15.43 skann K loddrett 180>10: W350 3.56 U 0.59 auge 1547/ 145/  66 bak   9 skjerm 114 | st: auge   9/  9/ 64 bak   2 felt   5 skjerm 1.5 | lik 0.13
- 15.44 skann T2 kryss 110>0: W350 2.88 U 0.47 auge  312/  78/  78 bak  10 skjerm 110 | st: auge 322/306/940 bak   0 felt   1 skjerm 0.5 | lik 0.37
- 15.44 skann T2 kryss 125>0: W350 2.88 U 0.47 auge  312/  78/  78 bak  10 skjerm 110 | st: auge  49/331/259 bak   1 felt   2 skjerm 1.1 | lik 0.23
- 15.44 skann T2 kryss 125>0 stripe0.2: W350 3.51 U 0.47 auge  304/  77/  77 bak  96 skjerm 129 | st: auge  39/265/207 bak  31 felt   5 skjerm 8.8 | lik 0.41
- 15.44 skann T2 kryss 125>0 bak0.3: W350 4.09 U 0.48 auge  310/  78/ 210 bak  14 skjerm 110 | st: auge  34/232/181 bak  26 felt   5 skjerm 2.1 | lik 0.53
- 15.44 skann K kryss -135>0 stripe0.2: W350 3.46 U 0.59 auge  524/  78/  73 bak  30 skjerm 169 | st: auge  30/ 30/ 30 bak  25 felt   3 skjerm 21.6 | lik 0.28
- 15.44 skann K kryss 180>0 stripe0.2: W350 3.46 U 0.59 auge  524/  78/  73 bak  30 skjerm 169 | st: auge   7/  7/ 39 bak  10 felt  10 skjerm 33.3 | lik 0.33
- 15.43 **Skann runde 1 (rekna), det som fall:**
  - Telt: jamnheit 0,01 i alle variantar. Årsaka var foten (Ø 240 mm), som stod inne i feltet og skugga rutene under seg. Foten er flytt til x = 0,44 (utanfor feltet), og armen går skrått opp. Det er ein formregel: den runde foten frå biletet kan ikkje stå på feltet.
  - Telt ståande (90°) i stemning: 973 til 995 cd/m² mot auget 47 og 60 cm (krav 500). Ruta lyser rett mot auget. Lent 20° bakover (110°) er det framleis 940 for auget 60 cm. Neste prøve er 125°.
  - Telt og Klemme med det øvste arket vassrett (kryss-v): 1949 og 1654 cd/m² mot auget 47 cm i arbeid. Det er sidelobane. Rillene i det øvste arket må peike mot brukaren.
  - Telt utan film (matt spreiar): 6,7 W og 1884 cd/m², same funn som rute.py (6,6 W og om lag 2000).
  - Begge: veggen bak skjermen 5 til 20 lx i arbeid (F6 100 til 150). Ruta lyser ikkje dit. Neste prøve er ei diodestripe mot veggen på hengslet (20 % av watten, som i rute.py).
  - Klemme snudd opp i stemning: 2 lx bak skjermen og 4 lx på feltet, så stemninga blir nesten borte (likskap 0,06). Snudd via veggen (−135°) gjev 13 lx bak skjermen og 34 cd/m² mot auget.
  - Det som held: Klemme i arbeid med kryss gjev 2,9 W, jamnheit 0,56 og 552 / 82 / 74 cd/m² mot auget. Telt i arbeid gjev om lag 3,1 W og 338 / 85 / 85 cd/m².
- 15.44 **Skann runde 2 (rekna), foten utanfor feltet:** Telt kryss 125°→0° gjev 2,88 W, jamnheit 0,47, auget 312 / 78 / 78 cd/m² i arbeid og 49 / 331 / 259 i stemning (krav 500 held). Stripa mot veggen (20 %) løftar veggen bak skjermen frå 10 til 96 lx og kostar 3,51 W. Lys ut baksida (30 %) gav berre 14 lx og 4,09 W, og fall. For Klemme lyser same stripe på skjermflata (169 lx) fordi hovudet heng framfor skjermen, og veggen får berre 30 lx: stripa fall for Klemme.
- 15.44 **Val:** Telt = kryss, 125° → 0°, stripe 25 % (rekna fram til om lag 128 lx bak skjermen). Klemme = kryss, −135° → 0° (via veggen), utan stripe. Grunngjeving i konsept.md.
- 15.45 rekn T (5 s): W350 3.71 U 0.47 auge  301/  76/  76 bak 123 skjerm 135 | st: auge  37/248/194 bak  39 felt   5 skjerm 10.7 | lik 0.49. Stemning: augevolum 331.0 cd/m², spegling blank 0.0. Arbeid: 2.78 W, augevolum 870.0 cd/m², bak 2 cm 120.8 lx (tal() 123.5), spegling blank 28.2 cd/m².
- 15.45 rekn K (4 s): W350 2.91 U 0.56 auge  552/  82/  74 bak   8 skjerm  83 | st: auge  34/ 34/ 34 bak  13 felt   3 skjerm 1.8 | lik 0.07. Stemning: augevolum 0.0 cd/m², spegling blank 9.7. Arbeid: 2.91 W, augevolum 849.0 cd/m², bak 2 cm 8.4 lx (tal() 8.4), spegling blank 19.4 cd/m².
- 15.46 **Heile overgangen (rekna, tre.rekn med n = 5):** Telt held F1, F5 og F6 i arbeid (3,71 W, 301 / 76 / 76 cd/m², 123 lx bak skjermen), men **blendar undervegs**: når ruta passerer ståande, ser auget 47 cm 985 og 1445 cd/m² (topp 5,8). Ei rute som dreier om eitt hengsel frå vindauge til tak må passere anten auget (over hengslet) eller skjermen (under). Klemme snudd via veggen blendar ikkje undervegs (topp 0,66), men **sveipar over skjermen**: 53, 305 og 432 lx på skjermflata midt i overgangen (ved 1,8 til 3,5 W). Det er same funn som i `konsept/tre/00-tre-konsept.md` (flytte strålen sveipar over skjermen).
- 15.46 Augevolum (±15 cm, 15 cm fram, 25 til 60 cm): Telt 870 og Klemme 849 cd/m² i arbeid, begge for auget 25 cm over bordet, 15 cm til venstre og 15 cm fram. Under F5 (1500). Spegling i skjermen i arbeid: 0 ved loddrett skjerm, 325 / 706 cd/m² (Telt) og 238 / 485 (Klemme) ved 15 / 20° tilt før refleksjon, altså 28 og 19 cd/m² med blank skjerm (ρ 0,04) og 7 og 5 med matt (ρ 0,01).
- 15.46 striper (0 s): sjå tal.json["striper"]. Auget 47 cm i stemning: snitt 73.0 cd/m², stripetopp 926.0 (frå 30 mm 349.0).
- 15.46 ut: ies_*.ies og scene.json skrivne
- 15.47 ut: ies_*.ies og scene.json skrivne
- 15.49 **Stripene (rekna, 2D-modell av plata, ANTAKING):** arbeidsrekkja (60 LED, 8 mm) er jamn frå 30 mm (kontrast 0,05). Stemningsrekkja (kvar femte LED, 40 mm) med nakne LED-ar gjev vifter som berre syner dei første 30 mm (kontrast 0,23, så 0,14 ved 60 mm). Med smal innkopling (vifte 6° i plata) står stripene til om lag 100 mm (kontrast 0,96 ved 60 mm, 0,5 ved 100 mm) og løyser seg opp mot den frie kanten, som på biletet. Med 3° går dei over heile ruta. Auget 47 cm ser snittet 73 cd/m² og stripetoppen 926 cd/m² dei første 10 mm frå hengslet, 349 cd/m² frå 30 mm. Kravet 500 held difor berre om sylinderen dekkjer dei første 30 mm.
- 15.49 **Regnbogen (rekna):** auget 47 cm ser ruta 40 til 52° frå normalen i stemning, altså på skråninga til cut-off. Der skil bølgjelengdene lag (cut-off flyttar seg om lag 3 til 4° frå 430 til 670 nm), og om lag 60 mm av ruta får synleg farge (over 15 % endring i kromatisitet). Flyttar auget seg 15 cm fram, flyttar bandet seg til 97–166 mm frå hengslet. Bandet går med hovudet: det er eit grep, ikkje ein feil. Auget 25 cm ser ruta 61 til 68° frå normalen, der ho er mørk.
- 15.47 ut: ies_*.ies og scene.json skrivne
- 15.52 Skreiv `ies_telt_arbeid.ies`, `ies_telt_stemning.ies`, `ies_klemme_arbeid.ies`, `ies_klemme_stemning.ies` (LM-63-2002, type C, romkoordinatar, absolutte candela), `scene.json` (kroppar, emitterar med lumen, CCT og plass, stripa mot veggen som eige flatelys, materiale med filmprofil, pitch 50 µm (ANTAKING) og n(λ), kamera for begge bileta og augepunkt), `lysstudie.png` (Telt i stemning stor, arbeid som innfelt, polardiagram) og `konsept.md`.

## Det som fall, samla

| Prøve | Kvifor det fall |
| --- | --- |
| Foten til Telt på feltet, som på biletet | skuggar ruta under seg, jamnheit 0,01 |
| Telt ståande (90°) eller lent 20° (110°) i stemning | 940 til 995 cd/m² mot auget, krav 500 |
| Det øvste arket med vassrette riller (kryss-v) | sidelobane går i auget: 1650 til 1950 cd/m² i arbeid |
| Matt spreiar utan film | 6,7 W og 1884 cd/m² mot auget |
| Lys ut baksida av Telt (30 %) | 14 lx bak skjermen og 4,1 W, stripa gjev 123 lx for 3,7 W |
| Stripe mot veggen på Klemme | lyser på skjermflata (169 lx), berre 30 lx bak skjermen |
| Klemme snudd via brukaren (180°) | stemninga blir nesten borte (2 lx bak skjermen), og ruta vender mot auget midt i gesten |
| Gesten til Telt | blendar undervegs (985 og 1445 cd/m², topp 5,8) |
| Gesten til Klemme | sveipar over skjermen (305 og 432 lx midt i gesten) |
- 15.50 tretest: tre.rekn('A') gav W350 2.99 (tal.md 2.99), jamnheit 0.62 (tal.md 0.62), auge25 1013.4 (tal.md 1013), auge47 102.74 (tal.md 103), bak350 107.73 (tal.md 109), skjerm350 115.39 (tal.md 115), s_auge25 424.18 (tal.md 424), s_bak 130.85 (tal.md 131), likskap 0.6 (tal.md 0.6) på 23 s
- 15.55 Kontroll: tre.rekn('A') herfrå gav same tal som konsept/tre/tal.md (2,99 W, jamnheit 0,62, 1013 / 103 cd/m², 108 mot 109 lx bak skjermen, 115 lx skjermflata, likskap 0,60).
- 15.56 IES-filene integrerte til 142, 48, 149 og 64 lm, mot 144, 48, 150 og 65 lm ut av rutene (rekna). Stripa mot veggen er ikkje med i IES-fila til Telt, ho står som eige flatelys i scene.json.
