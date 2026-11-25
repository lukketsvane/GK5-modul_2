# Kran, endeleg arkitektur

Grunnlag: vinnaren TRUFAST (stålplate i tre lag med skjult kanal, dobbel fold i foten, friksjonsledd på holt M10×1-røyr). Inn frå dei andre: leddet roterer med armen (SERIE), øyret i laserskore aluminium (SERIE), knotten åleine som berøringsflate med MCU og CC-lesing (SERIE), fleire tallerkenfjører i serie (PROTOTYPE), potensiometer som reserve (PROTOTYPE), og eit rekneskript (PROTOTYPE). Alle reknefeila dommarane fann er retta, og alle tal under er rekna opp att med `design/rekning_endeleg.py`.

Koordinatar: x langs armen frå leddaksen (+ mot tuppen), y vinkelrett på plata (+ fram, sida armen sit på), z opp frå bordet. Mål i mm, masse i g.

## Skala og hovudmål

Kameratilpassinga i `referanse/maaling.json` (rms 2,5 px, stativplanet dreidd φ = 26,7°) er brukt i staden for dei rå pikselmåla i briefen. Ho rettar foreskortinga som forslaget let liggje.

| Mål | Verdi | Kjelde |
|---|---|---|
| Leddaksen over bordet | 330 | vald skala |
| Armen, leddaksen til tuppen | 480 (målt 481,4) | kamera |
| Botnkanten (foten langs armen) | 179,8, frå x −154,2 til +25,6 | kamera (Bx, Px) |
| Toppen av stativet | z 354,6, R 24,6 konsentrisk med leddet | kamera (Xv, Zv) |
| Høgrekanten | frå (25,6; 0) til (10,4; 314,1), går 9,6 frå leddaksen | kamera (Xh, Zh) |
| Spalta | midtlinje (−105,9; 50,3) til (−12,3; 313,1), 13,8 brei, 293 lang | kamera (S1, S2, Sb) |
| Armen | 20,3 høg, z 316,1–336,4 (midt 3,7 under leddaksen) | kamera (zt, zb) |
| Fotdjupn | 48,5: framflens 22 + plate 4,5 + bakflens 22 | vald etter velting |
| Plata | 3 × 1,5 S235 = 4,5 | vald |

Rettingar mot briefen og forslaget: spalta er 13,8 mm, ikkje 7,8 (kantane ligg om lag 38 px frå kvarandre vassrett i originalen, ikkje 22). Foten er 180 mm, ikkje 153. Høgrekanten går berre 9,6 mm frå leddaksen, fordi knotten sit framfor plata og blir forskoven mot venstre i biletet (Y · sin φ). Det gjev eit krav som styrer heile leddet: knottflata kan liggje høgst om lag 14 mm framfor midtplanet, elles kjem leddholet for nær kanten. Difor er øyret tynt (2 × 2 mm aluminium) og fjørpakka sit bak plata.

Toleranse: alt er rekna for skala 0,85, 1,00 og 1,15 (opprisset, flensdjupna og armlengda skalerte; platetjukkleik og profilsnitt faste). Laserordren og profillengda blir bestilte etter endeleg skala.

## Delar

Laserskore (éin DXF-ordre)

| Id | Del | Materiale og prosess | Mål | Masse |
|---|---|---|---|---|
| D01 | Framlag med framflens | S235 1,5, laser og éin 90°-bukk framover (Ri 1,5). Bogespor for stoppinnen R 12, 3,4 breitt, 75°–196°. Leddhol Ø 10,2 (rømt 10,0–10,1) | omriss 179,8 × 354,6, flens 22 × 179,8 | 426 |
| D02 | Midtlag med kanal og vridekammer | S235 1,5, laser. Kanal 3,4 brei frå vindauget (x −40, z 9) vassrett til x 17, opp 7 mm innanfor høgrekanten og inn i kammeret Ø 17 rundt leddaksen. Botnen heva 3 mm | same omriss | 358 |
| D03 | Baklag med bakflens | S235 1,5, laser og bukk bakover. Vindauge 20 × 10 (x −50…−30, z 4…14) for leidningane og jordkontakten. Leddhol Ø 10,2 | same omriss, flens 22 × 179,8 | 425 |
| D04 | Øyre, kjerneplate | Al 5754 2,0. D-hol 10,2 / flat 9,0, hol Ø 3 H7 for stoppinnen på R 12, kabelspalte 2,2 brei frå D-holet ut til tunga, tunge 45 × 16 med 2 hol Ø 3,3 for popnaglar | R 24,6 øvst, skrå overkant ned til armen ved x 28, z 336, underkant z 316, R 16 under leddet | 13 |
| D05 | Øyre, dekkplate | Al 5754 2,0, same omriss utan tunge, sluttar ved x 28. D-hol | som D04 | 11 |
| D06 | Låseskive | Rustfritt 1,0, D-hol | Ø 20 | 2 |

Printa (P1S, PETG HF)

| Id | Del | Prosess | Mål | Masse |
|---|---|---|---|---|
| D07 | Knott med elektrode | Framsida ned, «Concentric» topplag så ho ser dreidd ut. Frontvegg 1,0, koparfolie Ø 13 limt på innsida, 1,5 PETG mellom folien og mutteren, sekskantlomme for frammutteren | Ø 17 × 6 | 2 |
| D08 | Lomme bak (USB-C, MCU, MOSFET) | Print, limt med epoksy på bakflensen, innanfor omrisset sett framanfrå. USB-C-opning bakover | 60 × 20 × 24 utvendig | 12 |
| D09 | Bakhette | Limt på bakmutteren, roterer med armen | Ø 24 × 12 | 3 |
| D10 | Filt | Sjølvklebande møbelfilt 1 mm, éi list under kvar flens | 2 × 180 × 20 | 2 |

Kjøpt

| Id | Del | Spesifikasjon | Mål | Masse |
|---|---|---|---|---|
| K01 | LED-profil (armen) | Aluminium U om lag 16 × 20, innvendig ≥ 10, opninga ned (AliExpress «LED aluminium profile U 16x20», 1 m). Kappa, 2 hol Ø 3,3 og 1 hol Ø 4 i bakveggen | 16 × 20 × 451 (x 29–480) | 90 |
| K02 | Opal deksel | PC, følgjer K01 | 451 | 8 |
| K03 | COB-stripe | 5 V, 8 mm, 2700 K, CRI ≥ 90, om lag 8 W/m | 360 (x 110–470) | 6 |
| K04 | Endelokk | Følgjer profilen (eller PETG-print) | 16 × 20 × 3 | 2 |
| K05 | Kontrollar | Seeed XIAO SAMD21 (QTouch) | 21 × 17,5 | 3 |
| K06 | MOSFET | AO3400A (logisk nivå, Vgs(th) ≤ 1,45 V) på SOT-23-adapterkort, 100 Ω i gate, 100 kΩ ned | ca. 15 × 10 | 1 |
| K07 | USB-C-utbrytar | 6-pinnars (VBUS, GND, CC1, CC2, D+, D−) med CC1 og CC2 ute. 5,1 kΩ frå kvar CC til GND (på kortet eller lodda på) | ca. 13 × 15 | 2 |
| K08 | Leidning | PTFE, mangetråda: 2 × AWG28 (Ø 0,85, LED + og −) og 2 × AWG30 (Ø 0,6, berøring og jord) | 4 × 750 | 4 |
| K09 | Aksel | Holt gjengerøyr M10×1, boring ca. Ø 7, lampedel. Kappa 23, flat fila 9,0 over heile lengda, gjengetoppane slipte til Ø 9,9 i lagersona | M10×1 × 23 | 5 |
| K10 | Mutrar | 2 tynne lampemutrar M10×1 (ca. 3 mm) | | 6 |
| K11 | Friksjonsskiver | PA6 10,5 × 20 × 1 (Biltema nylonskiver) | 2 stk | 1 |
| K12 | Tallerkenfjører | DIN 2093 C 20 × 10,2 × 0,5, 4 stk i serie, motstilte ()() | | 3 |
| K13 | Stoppinne | ISO 2338 Ø 3 m6 × 4 | | 0,2 |
| K14 | Popnaglar | Aluminium 3,2 × 6, 2 stk | | 1 |
| K15 | Forbruk | Epoksy 2K, sparkel, primer, silkematt lakk (RAL 6021 som start), koparteip med leiande lim, middels gjengelås, krympestrømpe | | 14 |
| R1 | Reserve for dimminga | WH148 B10K med brytar og PWM-kort (same par som Lut E02/E03), i lomma med aksel bakover | | (10) |

Total masse: 1 404 g (skala 1,00). Kostnad: om lag 1 250 kr, der laserordren med to bukkar er om lag 450 kr.

## Ledd

Oppbygging framanfrå: knott D07 (limt på frammutteren) | frammutter M10×1 med gjengelås (fast hovud på akselen) | dekkplate D05 og kjerneplate D04, begge låste til flata på akselen, med stoppinnen bak | PA6-skive | stativet | PA6-skive | låseskive D06 (D-hol) | fire tallerkenfjører i serie | bakmutter M10×1 med gjengelås | bakhette D09.

Akselen roterer med armen og går i Ø 10,2-hola i fram- og baklaget. Alt anna enn stativet roterer med han, så det er inga rørsle i nokon gjenge og ingen mutter kan løyse seg. Øyret går ikkje på gjengene (det er låst til flata), og glidinga skjer berre i dei to PA6-skivene mot stativet. Midtlaget har eit kammer Ø 17 rundt akselen, og der vrir leidningane seg. Stoppinnen går i bogesporet i framlaget og avgrensar armen.

Mål i y: plata −2,25…+2,25, PA6 til 3,25, øyret 3,25–7,25, frammutteren 7,25–10,25, knotten 7,75–13,75 (om lag 6 mm framfor øyret). Bak: PA6, låseskive, fjører og mutter til y −11,5. Fjørpakka bak (Ø 20) ligg skjult bak øyret og armen frå biletvinkelen.

**Naudsynt moment: 0,275 Nm. Friksjonsmoment: 0,55 Nm (μ 0,25), 0,44–0,66 Nm (μ 0,20–0,30).**

Rekning:

- Armen om leddaksen, vassrett: øyret 24 g ved 12, profilen 90,2 g og dekselet 8,1 g ved 254,5 (x 29–480), COB 5,8 g ved 290 (midt i x 110–470), endelokket 2 g ved 481,5, popnaglar 1 g ved 40, leidning 0,5 g ved 65. Det gjev m = 131,6 g med tyngdepunkt 212,9 mm ut, og M = 0,1316 · 9,81 · 0,2129 = 0,275 Nm. Ved skala 0,85 er M 0,200 Nm, ved 1,15 er han 0,361 Nm.
- Friksjon: to sleteflater, PA6 mot stål. r_eff = 2/3 · (10³ − 5,25³)/(10² − 5,25²) = 7,87 mm. T = 2 · μ · F · r_eff. Med F = 140 N blir T = 0,44 / 0,55 / 0,66 Nm ved μ 0,20 / 0,25 / 0,30, altså 1,6–2,4 × M.
- Fjørene (Almen–László, K ≈ 206,6 N, t 0,5, h0/t 1,3): 140 N gjev s = 0,160 mm per skive, 0,64 mm for fire i serie, eller 230° på bakmutteren etter anlegg (stigning 1 mm). Stivleiken er 165 N/mm for pakka, så 0,05 mm innsliting i PA6 kostar 8 N (6 %), mot 25 % med to skiver i forslaget. Ved skala 1,15 trengst F ≈ 183 N for 2 × M: 0,94 mm, 339°.
- Flatetrykk på PA6: 140 / 227,6 mm² = 0,62 MPa.
- Handkraft ved tuppen, armen vassrett: ned (0,55 − 0,275)/0,48 = 0,58 N, opp (0,55 + 0,275)/0,48 = 1,72 N. Lampa vippar mot armen ved 1,404 · 9,81 · (24,6 + 17,5)/455,4 = 1,27 N ned på tuppen, altså 2,2 × krafta som skal til for å føre armen ned. Rettleiinga seier likevel at ein held i øyret når armen blir justert.
- Kontroll i bruk: armen vassrett skal halde 40 g ved tuppen (0,275 + 0,19 = 0,46 Nm) og gli med 80 g (0,65 Nm). Det fangar μ-spreiinga.

**Rørsleområde: −30° til +75° frå vassrett.** Stoppinnen Ø 3 sit på R 12 i kjerneplata. Han tek 2 · asin(1,5/12) ≈ 14° av bogesporet sjølv, så sporet er 121° langt (75°–196°, målt frå +x mot klokka med armen vassrett ved 112,5°). Det ligg øvst til venstre, med minst 5,0 mm stål mot spalteenden og 5,5 mm mot høgrekanten. Ved −30° står tuppen 90 mm over bordet. Leidningane vrir seg høgst 105° i kammeret.

## Kabelveg

USB-C går inn bak i lomma D08 på bakflensen. Fire PTFE-leidningar går gjennom vindauget i baklaget og inn i kanalen i midtlaget, side om side og utvinna (kanalen er 1,5 djup og 3,4 brei, leidningane til saman 2,9 breie). Rekkjefølgja er berøring | jord | LED + | LED −, så berøringsleidningen ligg lengst frå PWM-leidningen og har jord og 5 V imellom. Kanalen går vassrett til x 17, så opp 7 mm innanfor høgrekanten (minst 5 mm stål mot kanten og 13 mm mot spalta) og inn i kammeret Ø 17 i midtlaget. Der ligg ei slakk sløyfe på om lag 15 mm som tek opp ±105°. Leidningane går inn i akselen gjennom eit tverrspor (2 mm breitt, 4 mm djupt) midt i midtlaget og fram gjennom boringa. LED-paret går ut eit tverrspor på motsett side ved kjerneplata, langs kabelspalta i D04 ut på tunga og inn i profilen gjennom Ø 4-holet i bakveggen, der det er lodda til COB-stripa ved x 110. Jordleidningen endar i ein loddefane under frammutteren, så aksel, øyre og arm er jorda. Berøringsleidningen held fram gjennom framenden av akselen til koparfolien i knotten. Stativet er jorda med koparteip på blankt stål i vindauget. Ingen leidning syner frå nokon kant.

## Elektro og varme

**Straum.** 5 V frå USB-C, ingen nettspenning i lampa. 5,1 kΩ på CC1 og CC2 gjer at ladaren slår på 5 V, men kor mykje straum han lovar, avheng av Rp i ladaren. XIAO-en les begge CC-pinnane på ADC og brukar den høgaste (kabelen kan vere snudd): 0,25–0,61 V er standard USB, 0,70–1,16 V er 1,5 A og 1,31–2,04 V er 3 A. Lampa trekkjer om lag 0,60 A på full styrke. Ved standard USB blir PWM-en avgrensa til 75 %, så totalen held seg under 0,45 A. Spenningsfallet i 2 × 0,75 m AWG28 (0,21 Ω/m) er 0,6 · 0,32 = 0,19 V. Merk: XIAO-en blir forsynt på 5 V-pinnen. Ikkje kople til USB-en på XIAO-en og lampa samstundes.

**LED.** COB-stripe 5 V, 2700 K, CRI ≥ 90, 360 mm (x 110–470), limt i botnen av U-profilen bak opal PC. 8 W/m gjev 2,9 W og om lag 260 lm (90 lm/W).

**Effekt: 2,9 W** for LED-en, om lag 3,0 W med kontrollaren.

**Dimming.** Berøring på knotten åleine: kort trykk slår av og på, hald inne dimmar trinnlaust, og retninga byter kvar gong. QTouch på XIAO-en kjenner fingeren gjennom 1 mm PETG. Arm, aksel og stativ er jorda, så ein som held i øyret eller stativet, løyser ikkje ut berøringa. PWM på 20 kHz gjennom AO3400A som lågsidebrytar, logaritmisk kurve frå 1 til 100 %, og lampa hugsar siste nivå. Målinga blir teken i PWM-pausa for å unngå krysstale. Reserve om berøringa ikkje blir stabil: R1 (WH148 med brytar og PWM-kort frå Lut) i lomma, med akselen bakover.

**Varme.** 2,9 W på profilen, med overflate om lag 2 · (16 + 20) · 451 = 0,032 m² og h ≈ 9 W/m²K, gjev ΔT ≈ 10 K, altså om lag 35 °C ved 25 °C i rommet. COB-stripa toler 60 °C. Øyret er aluminium og står 80 mm frå næraste LED. Prøv: etter 60 min på full styrke skal profilen vere ≤ 45 °C.

## Stabilitet

**Total masse: 1 404 g.** Tyngdepunkt med armen vassrett, skala 1,00: **x −17,5, y +0,9, z 138,2.**

| Retning | Vassrett arm, skala 1,00 | Minste over skala 0,85–1,15 og arm −30°/0°/+75° |
|---|---|---|
| Mot armen | 16,9° | 15,0° (0,85, 0°) |
| Frå armen | 44,5° | 36,7° (0,85, +75°) |
| Framover | 9,2° | 7,7° (0,85, +75°) |
| Bakover | 9,9° | 8,5° (0,85, +75°) |

Rekning (`design/rekning_endeleg.py`, shapely):

- Stativplata: omrisset er det konvekse skroget av botnhjørna (−154,2; 0), (25,6; 0) og sirkelen R 24,6 rundt leddet, avskore av høgrekantlinja og lagt saman med R 16 rundt leddet. Brutto 36 425 mm². Spalta (3 999 mm²) er trekt frå, så netto er 32 426 mm². Dette rettar feilen dommarane fann: forslaget hadde ikkje trekt frå spalta. Framlaget (minus leddhol og bogespor) veg 379,7 g, baklaget (minus leddhol og vindauge) 378,5 g og midtlaget (minus kammer, kanal og 3 mm i botnen) 357,9 g. Til saman 1 116,1 g, med tyngdepunkt (−40,2; 0; 126,8).
- Flensane: 22 × 179,8 × 1,5 stål = 46,6 g kvar, ved y ±13,2 og z 1,8.
- Epoksy, sparkel og lakk: 13,5 g ved tyngdepunktet til plata. Lomma med elektronikk: 24 g ved (−40; −12,2; 14). Leidning 2 g, filt 2,4 g.
- Leddpakka (aksel, mutrar, skiver, fjører, knott): 21 g ved (0; 1; 330). Armen: 131,6 g som under Ledd, med profilen ved y 13,25 og z 326,3.
- Støttekantane ligg 1 mm inn frå flensane, der filten ber: x +24,6 og −153,2, y ±23,25. Vinkel = atan(avstand frå tyngdepunktet til kanten / z). Mot armen: atan((24,6 + 17,5)/138,2) = 16,9°. Frå armen: atan((153,2 − 17,5)/138,2) = 44,5°. Framover: atan((23,25 − 0,9)/138,2) = 9,2°. Bakover: atan((23,25 + 0,9)/138,2) = 9,9°.
- Alle ni tilfelle (tre skalaer, tre armvinklar) held 6° etter EN 60598-1 med minst 1,7° margin. Massen er 1 045 g ved skala 0,85 og 1 818 g ved 1,15.
- Plan B, to lag (3,0 mm) utan midtlag: 1 062 g, 13,2° / 45,3° / 8,5° / 9,4°, og minst 6,8° (framover, 0,85, +75°). Held kravet, men med mindre margin.
- Kontroll: same stativ i PLA hadde gjeve om lag 1° mot armen, så stålet er naudsynt. Stålet er 87 % av massa og ligg lågt.

## Avvik frå biletet

- Plata er tre lag stål på 1,5 mm (4,5 mm), ikkje éi plate. Etter sparkel, kantslip og lakk ser ho ut som éin del. Midtlaget gjev kanalen og vridekammeret utan fres.
- Foten har to foldar på 22 mm, fram og bak. Fotoet syner berre framfolden som ei stripe på 5–8 px. Med kamerahøgda (om lag 7° over bordet) blir stripa 1,5 + 22 · sin 7° ≈ 4,2 mm ≈ 12 px. Ein framflens på 15 mm hadde passa betre, men gjev under 7° framover ved skala 0,85. Bakflensen syner ikkje.
- Den grunne kanalen i framsida av armen fell bort. Armen er ein kjøpt LED-profil, 16 djup og 20 høg (fotoet 20,3).
- Øyret er to aluminiumsplater på 2 mm med ei fuge langs kanten. Fotoet ser ut som éin del.
- Knotten er printa med konsentrisk topplag, Ø 17 mot om lag Ø 15 i fotoet, fordi han må dekkje mutteren. Han står om lag 6 mm framfor øyret (fotoet 4–6 mm).
- Leddaksen er lagd etter kameratilpassinga med knottflata 12 mm framfor plata. Den verkelege knottflata ligg ved 13,75. Det flyttar høgrekanten i biletet under 1 mm.
- Fjørpakka og bakhetta (Ø 24 × 12) sit bak leddet. Lomma (60 × 20 × 24) sit bak plata ved foten. Begge syner berre bakfrå.
- Armen går frå −30° til +75° med stopp. Fotoet syner berre den vassrette stillinga.
- Filt på 1 mm under flensane.
- Fargen er sprøytelakk, silkematt RAL 6021 som utgangspunkt. Prøv han mot fotoet før heile lakkeringa.
- Toppen og botnen følgjer kameratilpassinga (fot 180, topp 354,6, spalte 13,8 brei), ikkje dei førebelse anslaga (150, 352, 7,8).

## Monteringsrekkjefølgje

0. Passprøve: print D07, D08 og D09. Mål profilen, mutrane, PA6-skivene, fjørene og USB-C-kortet med skyvelære og rett dei parametriske måla (tunga på D04, lomma, knottlomma) før laserordren. Prøv QTouch gjennom ein printa knott med folie på XIAO-en, med ein jorda stålbit bak.
1. Bestill frå DXF: D01, D02 og D03 i S235 1,5 med bukk på D01 (fram) og D03 (bak), 90° ± 0,5°, Ri 1,5. D04 og D05 i Al 5754 2,0 og D06 i rustfritt 1,0 på same ordre.
2. Aksel: kapp til 23 mm, fil flata til 9,0 over heile lengda og slip gjengetoppane til Ø 9,9 i lagersona (akselen i drill, fil og 240-papir). Sag eitt tverrspor midt i midtlaget og eitt ved kjerneplata, på kvar si side, 2 × 4 mm. Avgrad og fôr spora med krympestrømpe.
3. Leidning: legg dei fire PTFE-leidningane utvinna i kanalen i D02 i rekkjefølgja berøring, jord, LED +, LED −. Legg ei slakk sløyfe på om lag 15 mm i kammeret, før dei inn det bakre tverrsporet og fram gjennom akselen. Ut gjennom vindauget i D03 bak.
4. Laminering: tunt epoksylag på begge sider av D02, men ikkje i kanalen og kammeret. Rett inn med akselen i leddhola og ei 13,8 mm flattstang i spalta. Press mellom to plater med tvinger og herd i 24 timar. Snu akselen nokre gonger medan epoksyen er open, så han ikkje limer seg fast.
5. Overflate: slip kantane flate, sparkle laminatlinjene og avrund med R 0,5. Maskér leddhola, ein ring Ø 24 på begge sider rundt leddet (friksjonsflatene), bogesporet og kontaktflata i vindauget. Grunn og lakk to–tre strøk. Lakk D04 og D05 og utsida av profilen same dag.
6. Lomme: lodd USB-C-kortet, XIAO-en og MOSFET-en. Lim koparteip på blankt stål i vindauget og lodd jord til teipen. Last opp fastvara og prøv berøring og dimming med ei kort testlist før lomma blir limt på bakflensen.
7. Arm: kapp profilen til 451, bor 2 × Ø 3,3 og Ø 4 i bakveggen. Lim COB-stripa frå x 110 til 470.
8. Øyre: press stoppinnen inn i D04. Legg LED-paret ut det fremre tverrsporet, langs kabelspalta i D04 og inn Ø 4-holet i profilen. Nagle tunga til profilen med 2 popnaglar. Lodd LED-paret til stripa.
9. Ledd: PA6-skive framme, D04 og D05 på flata (stoppinnen i bogesporet), frammutter med gjengelås og jordfane. Bak: PA6-skive, D06, fire tallerkenfjører ()(), bakmutter. Skru bakmutteren til anlegg og så 230° vidare. Gjengelås.
10. Friksjon: armen vassrett skal halde 40 g ved tuppen og gli med 80 g. Juster bakmutteren ±30° om naudsynt. Lim bakhetta D09 på bakmutteren.
11. Knott: lodd berøringsleidningen til folien i D07 og lim knotten på frammutteren. Klikk inn dekselet og set på endelokket.
12. Filt under flensane.
13. Kontroll: vippeprøve på eit brett skråstilt 6° (105 mm stigning på 1 m) i fire retningar med armen på −30°, 0° og +75°. Varmeprøve 60 min på full styrke (profilen ≤ 45 °C). Prøv berøringa med handa på stativet og på øyret: lampa skal ikkje løyse ut.

## Risiko og opne spørsmål

- Skala: kameratilpassinga har fast brennvidd. Med brennvidd 2 500–9 000 px varierer foten mellom 179 og 188 mm og armen mellom 436 og 513 mm. Vippinga og momentet er kontrollerte for 0,85–1,15, men laserordren og profillengda må bestillast etter endeleg skala.
- Framover er margen minst: 7,7° (skala 0,85, armen på +75°). Ein stiv USB-kabel som dreg, kan tippe lampa. Bruk ein mjuk kabel som ligg flatt bakover.
- Laminering i stål: epoksyen må dekkje 32 000 mm² jamt, elles kan laga skilje seg eller laminatlinjene syne. Prøv på ein restbit først. Plan B er to lag (3,0 mm) utan midtlag, med leidningen i ein aluminium U 10 × 8 bak, innanfor omrisset (minst 6,8°). Då må vridesløyfa liggje i ei fast hette bak leddet, og den syner truleg frå biletvinkelen.
- Vridekammeret i midtlaget er berre 1,5 mm djupt. Leidningane kan setje seg fast i sløyfa. Det må prøvast i passprøva med ei laserskoren 1,5 mm-skive og 100 rørsler før laserordren for stativet.
- Lageret er stål mot slipte gjengetoppar i 2 × 1,5 mm plate. Klaringa (om lag 0,2 mm) gjev litt slark, men klemkrafta på 140 N ber armen. Opent: om lageret blir merkbart etter mange rørsler.
- μ for PA6 mot blankt stål er usikker (0,20–0,30). Ved μ 0,20 er margen 1,6 ved skala 1,00 og 1,2 ved 1,15. Bakmutteren er justerbar, og vektprøva avgjer. Etterstill etter ei veke. Den blanke ringen kan ruste. Lampa står inne, og ringen ligg dekt.
- Fjørkrafta er rekna med Almen–László, ikkje henta frå datablad. Vinkelen på 230° er eit startpunkt, og vektprøva er fasit.
- Berøring: elektroden sit 1,5 mm frå ein jorda mutter, så grunnkapasitansen er høg og følsemda låg. Terskelen må stillast i fastvara. Krysstale frå PWM-leidningen er dempa med rekkjefølgja i kanalen og måling i PWM-pausa. Reserven er R1.
- USB-C: ladarar som berre lovar standard USB gjev 75 % lys. Fastvara må lese begge CC-pinnane.
- XIAO-en blir forsynt på 5 V-pinnen. Kople aldri til USB-en på XIAO-en medan lampa står i straum.
- Kjøpte delar varierer (profil, USB-C-kort, mutrar). Mål før printing og laserordre. Alt er parametrisk.
- Bukk for hand kan gje ein vinkel som ikkje er 90°. Då vippar plata. Bukk hjå leverandøren.
- Lakken på stål og aluminium og PETG blir ikkje heilt lik. Lakk alt i same økt, frå same boks.
- Stålkantar etter laser er skarpe. Avgrad før lakk.
