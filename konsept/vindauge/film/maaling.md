# Måling på fotoa av arket

Alt her er lese ut av fire foto (01, 05, 06, 07). Ingenting er målt på det fysiske arket.
Skript: `konsept/vindauge/film/maaling.py`. Figurar og `maaling_tal.json` ligg i `context/delar-foto/analyse/` (ikkje publisert).

Merking av tal: **F** = estimat frå foto, **R** = rekna, **K** = kjent frå kjelde, **A** = ANTAKING.

## Kort

- Arket bøyer synslinja 35–36° oppover og lagar samstundes eit andre bilete som er bøygd nedover. Det er ein lineær prismefilm med toppvinkel nær 90°, riller langs kortsida, og prismesida vende mot kamera på bileta. Sannsyn 87 % for denne familien (55 % «rein» 90°-film, 32 % variant).
- Dei lange loddrette stripene er ikkje diffusjon. Dei er eit bilete som er strekt loddrett (1,5–3 gonger) og farga ut (1–3° frå raudt til blått). Kvar bilet-kant er framleis skarp (0,5–1,2°).
- Brennvidda måtte reknast frå bygningane i biletet. Foto 01 og 07 har ulik zoom. Med feil brennvidd (26 mm for begge) hadde same måling gitt toppvinkel ca. 77°. Dette er den største feilkjelda.

## Metode

1. **Kamera.** EXIF er strippa (berre 1932 × 2576 px og ein Display P3-profil med Apple-signatur). Brennvidda er rekna frå forsvinningspunkt: helling på loddrette bygningskantar gir det loddrette forsvinningspunktet, vassrette fasadeliner gir horisonten, og f² = d_v · d_h. ANTAKING: hovudpunkt i biletsenteret, ikkje beskore bilete. Kontroll: horisonten kryssar same bygning (snøhylla til høgre) på same stad i begge foto.
2. **Pose.** Venstre og høgre kant av arket er spora rad for rad. Synleg breidd w(y) gir djupn (Z = f·W/w), og den deriverte gir lokal helling θs. ANTAKING: rektangulært ark med konstant breidd, krumma berre om ein vassrett akse. Kontroll: toppen av arket kjem ut loddrett (ligg mot glaset) i begge foto.
3. **Vinklar.** a = atan((y − 1288)/f), positiv nedover. φ = a + θs er vinkelen mellom kamerastråle og arknormal (positiv når strålen peikar meir nedover enn normalen). Avbøying D = a(gjennom arket) − a(direkte).
4. **Trekk.** Taklina (lys himmel over mørke bygg) er synleg både direkte og gjennom arket i foto 07. Kantposisjon = 50 %-kryssing i lineariserte RGB-profilar, kvar kanal for seg. I foto 01 ligg taklina over biletkanten; høgda over horisonten er henta frå 07.
5. **Modell til samanlikning.** To plane flater + plan bakside, Snells lov i 2D, med korreksjon for stråler på skrå langs rillene. Monte Carlo (4000 trekk) over brennvidd, helling, kantposisjon og brytingsindeks.

## Tal

### Kamera og geometri

| Storleik | Foto 01 | Foto 07 | Merke |
|---|---|---|---|
| Brennvidd | 2117 ± 72 px = 28,4 ± 1,0 mm ekv. | 2520 ± 56 px = 33,9 ± 0,8 mm ekv. | R frå F. Realistisk ± 100 px med systematikk |
| Synsfelt (b × h) | 49° × 63° | 42° × 54° | R |
| Vinkel per piksel i sentrum | 0,027° | 0,023° | R |
| Kamera vippa ned | 27,6 ± 0,8° | 18,9 ± 0,4° | R frå F |
| Rull | −2,5° | −3,0° | R frå F |
| Arkhelling θs i kameraramma, topp → botn | 30° → 10° | 22° → 8° | R frå F, ± 2–3° |
| φ midt i arket, topp → botn | 10,5° → 25,4° | −0,4° → 26,7° | R frå F |
| Toppen av arket mot lodd | −2,7° | −2,4° | R, ± 3°: loddrett |
| Nedre del lener bakover | ca. 17° | ca. 11° | R, ± 3° |

Brennviddene høver med 28 mm- og 35 mm-vala på nyare iPhone Pro (2085 og 2606 px) (K, frå minne). Nærbileta 05 og 06 har ingen bygg å kalibrere mot; vinklar derfrå er gitt som intervall for f = 2100–2600 px.

### Arket

| Storleik | Verdi | Merke |
|---|---|---|
| Høgd / breidd (bogelengd, foto 07) | 1,745 ± 0,03 | F/R. 16:9 gir 1,778, 16:10 gir 1,6 |
| Breidd | 267 mm ± 15 % | F + A: målestokk frå lineavstanden i teksten på A4-arket (17 px), skrift 11–12 pt |
| Høgd | 465 mm ± 15 % | R |
| Passar med | 21,5" 16:9-skjerm (476 × 268 mm biletflate) | K: rekna frå diagonalen |
| Rilleretning | langs kortsida (vassrett på bileta) | F: all forskyving går langs langsida |

A4-arket er skore av biletkanten, så breidda (210 mm, K: ISO 216) kan ikkje lesast direkte. Difor er uvissa stor.

### (a) Forskyving

| Storleik | Verdi | Merke |
|---|---|---|
| Takline direkte, foto 07 | y = 100 ± 11 px, a = −25,2° | F |
| Same takline gjennom arket, foto 07 | y = 1711 (R), 1738 (G), 1844 (B) | F |
| **Avbøying D, foto 07** | **34,8° (R), 35,4° (G), 37,7° (B), ± 1,9°** | R frå F, ved φ = 18,0 ± 2,5° |
| Forteikn | Biletet ligg lågare enn motivet: gjennom arket ser ein det som ligg D *over* synslinja | F |
| Avbøying D, foto 01 | > 33,2° (sikker nedre grense), 35,9 ± 2,9° med takhøgd frå 07 | R frå F, ved φ = 24,1 ± 3,5° |
| Modell 90°, n = 1,585, prisme mot kamera | 36,3° (07), 38,9° (01) | R. Avvik −1,6 ± 1,9° og −3,0 ± 2,9° |
| Toppvinkel som gir målt D (n = 1,585 ± 0,03) | 92,9° (89–96) frå 07, 95,2° (90–100) frå 01, samla 93,6 ± 2,8° | R |
| Eller: toppvinkel 90° fast gir | n = 1,56 (07), 1,53 (01) | R |
| Sideforskyving | −40 px = −0,9°, lik rullen til arket i biletet | F: inga avbøying på tvers |

### Det andre biletet

| Storleik | Foto 01 | Foto 07 | Merke |
|---|---|---|---|
| Tynn lys line tvers over arket, y | 1685 | 1796 | F |
| Breidd (FWHM) | 0,69° | 0,74° | F |
| Farge | blå 8 px over raud (0,22°) | blå 6 px over raud (0,14°) | F: motsett rekkjefølgje av takline-frynsa |
| Lina ligg over overkanten på vindaugsramma (direkte) | 87 px = 24 mm | 106 px = 23 mm | F, mm ± 15 % |
| Skarp mørk kant ligg under same rammekant | 89 px = 25 mm | 122 px = 26 mm | F, mm ± 15 % |
| Plass på arket, frå toppen (line / kant) | 1,18 W / 1,38 W | 1,23 W / 1,42 W | R |
| φ ved lina | 25,4° | 19,6° | R |

Lina og kanten sit på same stad på arket i begge foto, men ved ulik synsvinkel. Dei følgjer altså vindaugsramma, ikkje ein optisk grensevinkel. Lesing: rammekanten, som ligg 2–4 cm bak arket (R, grovt), blir sett to gonger, éin gong forskuva opp og éin gong ned, omtrent like langt. Midt mellom, der kanten ligg direkte, finst ingenting: sprang inne i arket < 3,5 % (07) og < 0,4 % (01) av spranget utanfor (F).

### (b) Striper

| Storleik | Foto 01 | Foto 07 | Merke |
|---|---|---|---|
| Lengd på varm stripe (R/B > 1,2) | 14–15° | 10–11° | F |
| Kantskarpleik takline, 10–90 %, direkte | – | 0,68° (30 px) | F: kamera fokuserte på arket |
| Same kant gjennom arket (raud kanal) | 0,54° | 1,16° | F |
| Loddrett forstørring frå kantbreidda | – | 1,5–1,7 | R. Modell: 1,6–1,8 (prisme mot kamera), 0,6 (prisme mot vindauge) |
| Avstand takline → topp av høgt bygg, gjennom arket | 0,9–1,6° | 4,5–6,5° | F: 3–5 gonger meir strekk i 07 |

### (c) Frynser

| Storleik | Verdi | Merke |
|---|---|---|
| Rekkjefølgje ved takline (lys himmel over mørkt bygg) | raud kant øvst, så grøn, blå nedst i biletet | F, likt i 01, 05 og 07. Blått blir bøygd mest: vanleg brytingsspreiing |
| Raud → blå, foto 07 | 2,0° (lyst gavlbygg), 2,9° (takline, blå kant forstyrra av den tynne lina) | F |
| Raud → grøn, foto 07 | 0,6–0,9° | F |
| Raud → blå, foto 01 | 1,0° (raud → grøn 0,34°) | F |
| Raud → blå, foto 05 | 65 px = 1,4–1,8° | F, f ukjend |
| Modell, prisme mot kamera | 1,5–2,0° (07), 1,1–1,6° (01) | R, A: Δn(blå − raud) = 0,018–0,025 |

### (d) Frå topp til botn (gratis tilt-skann, foto 07)

| y (px) | φ | Lysstyrke (lin., himmel direkte = 0,85) | Det ein ser |
|---|---|---|---|
| 240–1200 | −0,4° → 9,3° | 0,52–0,64 | Jamt lyst: himmel (opp-biletet) + snø (ned-biletet) |
| 1320–1560 | 11° → 15° | 0,64–0,66 | Toppen av dei solgule bygga, strekt |
| 1680–1800 | 17,5° → 19,7° | 0,57 | Takline med frynser, så den tynne lina |
| 1920 | 22° | 0,41 | Bleike striper, ned-biletet ser no mørk ramme |
| 2040–2160 | 24° → 27° | 0,02–0,06 | Begge bileta ser mørk ramme og karm |

Lysfallet nedst kjem av det som står bak arket, ikkje av ein grensevinkel. D er berre målt ved éin φ per foto (18° og 24°); resten av skannet stadfestar forma, ikkje talet.

### (f) Transmisjon

| Storleik | Verdi | Merke |
|---|---|---|
| Himmel direkte (lin. RGB) | 0,72 / 0,94 / 0,90, 15 % av pikslane metta | F |
| Øvre del av arket | 0,40 / 0,58 / 0,67 | F |
| Forhold ark / himmel | 0,56 (R), 0,62 (G), 0,75 (B); 0,75–0,79 like over taklina | R |

Grenser: JPEG med lokal tonekartlegging, metta himmel, og arket viser to bilete oppå kvarandre (himmel + snø). Talet er difor ikkje transmittansen til filmen. Det seier berre at arket slepper gjennom det meste av lyset, og at ein rein 50 %-sperre (reflekterande polarisator) er lite truleg.

### (g) Finstruktur

- Ingen periodisk topp som går att mellom ruter i 05, 06 og 07 (FFT, toppar 2–3 gonger medianen, ingen overvekt for vassrette liner). F.
- For auga: fin sikksakk-ripling (2–3 px) berre på kontrastrike stripekantar, lagd i vassrette rader. Truleg aliasing mot pikselrasteret. Gir ingen rilleavstand.
- Oppløysing: 4,6 px/mm på arket i foto 07 (R). Periodar under ca. 0,45 mm kan ikkje sjåast. Vanleg rilleavstand er 0,024–0,05 mm (K: 3M BEF-datablad, frå minne), altså 10–20 gonger for fint.

## Kva tala tillèt og utelukkar

| Kandidat | Sannsyn | Grunn |
|---|---|---|
| (a) Lineær prismefilm ≈ 90°, plane flater | 55 % | D = 35–36° ved φ = 18–24° høver innanfor 1–1,3 σ. To skarpe bilete, eitt opp og eitt ned. Inga rett-gjennom-del. Rett fargerekkjefølgje |
| (b) Same familie med avvik: avrunda toppar, toppvinkel 85–100°, tilfeldig prismehøgd, matt bakside | 32 % | Målt toppvinkel 93,6 ± 2,8° (eller n ≈ 1,55). Avrunding opp til ca. 20 % av lyset (R, grovt) kan ikkje utelukkast frå foto. Strekket i 07 er større enn glatt modell gir |
| (f) Reflekterande polarisator: åleine eller på diffusor er utelukka; med prismeflate kan ikkje utelukkast | 4 % | Åleine gir han inga avbøying. Lysnivået (0,6–0,8 av himmel) talar svakt imot |
| (h) To ark i lag | 3 % | Kryssa prisme ville gitt bilete til sida; sideforskyvinga er 0 innanfor 0,9° |
| Anna, ikkje på lista | 2 % | |
| (c) Lentikulær (sylinderlinser) | 1 % | Ville spreidd lyset samanhengande rundt rett-gjennom. Her: < 3,5 % rett gjennom, to åtskilde bilete |
| (d) Einvegs diffusor | 1 % | Gir inga netto forskyving på 35° og ingen kant på 0,5° |
| (e) Vanleg diffusor | 1 % | Same, og sida ville vore uskarp |
| (g) Mikrolinsefilm | 1 % | Symmetrisk i to retningar; her er vassrett retning urørt |

Sum 100 %.

**Kva side vende mot kamera?** Prismesida, ca. 90 % (gitt prismefilm):
- Øvre halvdel av arket i foto 07 (y = 240–1200) er sett ved φ = −0,4° til 9,3° og er lys (0,65 av himmelen) (F). Med plan side mot kamera ville ein 90°-film vore ugjennomsynleg for |φ| under 7,5–9,6° (n = 1,55–1,59): totalrefleksjon i begge flater (R).
- Det finst to reine bilete. Med plan side mot kamera finst berre eitt ved desse vinklane (R).
- Loddrett forstørring 1,5–1,7 i foto 07; omvendt film gir 0,6 (R).
- D åleine skil ikkje: begge kurvene kryssar ved φ ≈ 17°, D ≈ 35,5°.

**Kvifor lange striper når ein ideell film berre gir to kopiar?** Fordi kopien ikkje er i målestokk 1:1. Ved φ = 18–24° er opp-biletet strekt loddrett 1,8–2,2 gonger i ein plan film (R), og forstørringa er M = 1/(1 − D′·(1 + dθs/da)). Ei endring i arkhellinga på 3° over 4 cm er nok til å doble strekket. Så kjem fargespreiinga (1–3°) og kamera-uskarpleiken, som òg blir strekt. Sollyse fasadestriper blir til 10–15° lange band. Filmen sjølv smører kvart bilete mindre enn ca. 0,5° (frå kanten på 0,54° i foto 01).

## Ikkje forklart

- Strekket ved taklina er 3–5 gonger større i foto 07 enn i 01; glatt modell gir 1,3. Lokal krumming kan forklare det, men er ikkje målt.
- Svakt farga band ved y ≈ 1545 i foto 01 (raud/grøn 1545, blå 1595). Ukjent opphav.
- Målt D ligg 1,6–3,0° under ideell 90°/1,585 i begge foto. Innanfor uvissa, men same veg.
- Brennvidda kviler på forsvinningspunkt åleine. 10 % feil i f flyttar toppvinkelen om lag 7°.

## Målinga som fjernar mest uvisse

**Laserpeikar rett gjennom arket mot ein vegg, begge vegar.** Éi måling gir fire svar:

| Ein les av | Ein får |
|---|---|
| Vinkel mellom dei to flekkane | Toppvinkel/indeks: 61° for 90° og n = 1,59; 57° for 90° og n = 1,55; 52° for 100°; 70° for 80° (R) |
| Snu arket: kjem det lys rett gjennom? | Kva side som har prisme (ingen stråle gjennom frå den plane sida om filmen er 90°). Lys midt mellom flekkane måler avrunda toppar |
| Forma på flekkane | Diffusjon / matt bakside (rund sky) eller rein prismefilm (skarp flekk) |
| Avstand mellom diffraksjonsordenar | Rilleavstand: 13 mm per meter vegg for 0,05 mm og raud laser (R) |

Vippar ein arket om rilleaksen, sloknar den eine flekken ved ca. 35° (totalrefleksjon, avheng av både n og toppvinkel) og den andre ved 45° (halve toppvinkelen) for ein 90°-film (R). Dei to vinklane skil toppvinkel og indeks frå kvarandre. Linjal på arket (venta 267 × 465 mm) og eit blikk gjennom polariserte solbriller (vriding) tek resten.

## Filer

- `konsept/vindauge/film/maaling.py`: les `context/delar-foto/`, skriv berre til `context/delar-foto/analyse/`.
- `context/delar-foto/analyse/maaling_tal.json`: alle tal.
- `context/delar-foto/analyse/maaling_oversyn_01.jpg`, `maaling_oversyn_07.jpg`: foto med målte liner teikna inn.
- `context/delar-foto/analyse/maaling_profilar.png`, `maaling_pose.png`, `maaling_avboying_modell.png`.
