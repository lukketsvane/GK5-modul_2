# Fotometri for (a) bru og (b) krok, og den felles lysmodellen · gransking 13.11.2026

Linse: fotometri for (a) og (b), og lysmodellen i `felles.py` (lys(), visible(), reflected(), sok(), stemningsmålet). Skeptisk og uavhengig: all kontrollrekning er eigen kode frå grunnformlane (Lamberts polygonformel, kvadratur dE = L·cosθe·cosθr·dA/r², Monte Carlo i røyret, spegling ved framover-strålegang). felles.py og motorane er berre importerte i del K i `fotometri_ab.py`, til samanlikning.

| skript | kva | utdata |
|---|---|---|
| `fotometri_ab.py` | Φ, U0, vegg på motorgitter og fint gitter; skjermlys og kontrast; ψ-sveip i 1°-steg; synlegheit for 8 augepunkt; spegling med spegla auge; første MC; stemningsmål for (a), (b), (c); kryssprøve mot felles.py | `fotometri_ab.json` |
| `fotometri_kontroll.py` | ny MC i røyret (LED i aksen / på bakveggen, 1,5 M strålar) med ψ-sveip; lambertsk opning trekt med same estimator som kontroll; spegling med tilt ved framover-strålegang; skjermlys i stemning; leppe langs opninga (lambertsk og MC) | `fotometri_kontroll.json`, `.log` |
| `fotometri_leppe.py` | kva leppene gjer med stemninga | `fotometri_leppe.json` |
| `kontroll_lys.py` | eldre kontroll (avbroten gransking), same tal som over | `kontroll_lys.json` |

Køyr med `PYTHONIOENCODING=utf-8 python <skript>`. `fotometri_kontroll.py` tek om lag 10 min.

## Samandrag
1. **Stadfesta på motorgitteret:** Φ, U0, Ē_vegg og R_stem i konsept.json er rette til 0,07 % for (a) og (b). felles.illum() avvik 0,03 % frå polygonformelen. visible() og reflected() er rette for det dei testar.
2. **Gitteret er grovt:** med arealsnitt er Φ 5 % lågare (1192 og 1246 lm). Veggsnittet i stemning er 23 og 29 % *høgare* enn 8×6-gitteret syner (75,7 og 89,3 lx), og feilen er ulik for (c).
3. **Skjermlyset 611 og 652 lx er rett** (eksakt). Det gjev 7,8 og 8,3 cd/m² slør på ein matt skjerm (ρ 0,04), og kontrasten fell frå 1000:1 til 26:1 og 25:1. Vrivinkelen kan ikkje rette det: skjermlyset fell berre når opninga vender mot auga. Ei svart leppe på 30 mm på veggsida tek det ned til 10–25 lx (a) og 54–86 lx (b), for 7–35 % meir fluks.
4. **«Skjerma» held berre for eitt augepunkt.** Søket legg ψ på kanten av synsgrensa: auga ligg 2,3° (a) og 4,2° (b) bak opningsplanet. 5 cm lågare eller 15 cm fram, og ei opning på 23–27 kcd/m² er synleg (8–257 lx ved auga). Med vanleg skjermtilt (14–18°) vert opninga spegla i skjermen (920–1070 cd/m² i ein blank skjerm).
5. **Lysmodellen held ikkje saman:** η-formelen føreset LED i aksen, men ein LED i aksen gjev ei vifte på ±25°, ikkje ei lambertsk opning (U0 0,15 i staden for 0,76). Med LED på røyrveggen (det konseptet seier: røyret kjøler) er η 0,56 og 0,54, og (b) treng 1627 lm (+24 %) og lyser 829 lx på skjermen.
6. **Stemningsmålet straffar verknadsgrad.** 25 %-regelen bind stemninga til arbeidsfluksen. Med fast veggluminans (10 cd/m²) treng (c) 1,0–1,3 W, (b) 1,5–1,8 W og (a) 1,7–1,8 W. Rangeringa snur.

## 1 · Φ, U0, veggdel og veggluminans (lambertsk opning, som motoren)

| | (a) konsept.json | (a) eige, 7×5 / 8×6 | (a) eige, fint | (b) konsept.json | (b) eige, 7×5 / 8×6 | (b) eige, fint |
|---|---|---|---|---|---|---|
| Φ for Ē 500 lx | 1255,2 lm | 1255,6 (+0,02 %) | **1191,6** (arealsnitt 5 mm, −5,1 %) | 1311,3 | 1311,4 (+0,01 %) | **1246,5** (−4,9 %) |
| U0 | 0,7573 | 0,7574 | 0,725 (5 mm), 0,867 (EN 5×3) | 0,6732 | 0,6733 | 0,647 (5 mm), 0,798 (EN 5×3) |
| Ē_vegg i stemning (25 %) | 61,6 lx | 61,6 (−0,06 %) | **75,7 lx** (2 cm, +23 %) | 69,2 | 69,2 | **89,3 lx** (+29 %) |
| R_stem | 0,899 | 0,899 | 0,902 | 0,938 | 0,938 | 0,943 |
| L̄_vegg (ρ 0,75), maks | | | 18,1 cd/m², maks 44,1 | | | 21,3 cd/m², maks 57,1 |
| maks/snitt på veggfeltet | | | 2,44 | | | 2,68 |
| LED-lm som når veggfeltet | | | 122 lm = 39 % | | | 144 lm = 44 % |

Metodar: polygonformelen (eksakt for eit fritt rektangel), kvadratur (Φ 7×5 lik til 0,001 %), og MC med lambertsk opning (Φ 1192 og 1245, same som arealsnittet). Motorgitteret tek med hjørne og kantar (lågaste E), så Φ er konservativ med 5 %. 8×6-gitteret på veggen har ingen punkt i x = 0 og hoppar over toppen ved z 0,6, så det underskattar veggsnittet. For (c) er same feil +7 % (fjernfelt) og +26 % (nærfelt), altså ulik mellom konsepta.

## 2 · Lys på skjermflata

**Stadfesta:** polygonformelen på 55×32 punkt: (a) 610,4 lx (min 259, maks 1133), (b) 651,5 lx (min 226, maks 1424) ved Φ i konsept.json. Kvadratur avvik 0,002 %. Ved Φ frå arealsnittet: 579 og 619 lx. Toppen ligg øvst på midten av skjermen, rett under lampa.

**Luminans og kontrast** (kvit 200 cd/m², svart 0,2 cd/m², altså 1000:1):

| | (a) | (b) | (c) motor / nærfelt |
|---|---|---|---|
| E på skjermen | 610 lx | 652 lx | 8,8 / 34 lx |
| matt, ρ_d 0,04: L_refl (maks) | 7,8 (14,4) cd/m² | 8,3 (18,1) cd/m² | 0,11 / 0,43 |
| kontrast 1000:1 vert | **26:1** | **25:1** | 640:1 / 316:1 |
| svartnivå | 0,2 → 8,0 cd/m² (40×) | 0,2 → 8,5 (42×) | 1,6× / 3,2× |
| matt, ρ_d 0,01 (meir typisk AG) | 1,9 cd/m², 94:1 | 2,1 cd/m², 89:1 | |
| blank, 0,5 % diffust slør | 0,97 cd/m², 172:1 | 1,04 cd/m², 163:1 | |
| blank, spegelbilete av opninga (ρ_s 0,04) | 920 cd/m² når ho vert spegla (sjå 3) | 1070 cd/m² | 0,4 cd/m² |

Svart tekst på kvitt held seg lesbar (Weber-kontrast 0,999 → 0,962). Tapet syner i mørke flater, mørk modus, bilete og video: svart vert 40 gonger lysare, og 20 %-grått mot kvitt fell frå 5,0 til 4,35. Merk: (c) er 8,8 lx i motoren sin fjernfeltmodell. Med plata si breidd (16 cm, 5 cm under lina) gjev min eigen nærfeltmodell 34 lx (maks 93). Det er framleis 18 gonger mindre enn (a) og (b), men 9 lx bør ikkje stå åleine i tabellen.

**Kan ein annan vrivinkel ta ned skjermlyset?** Nei. Polygonformelen i 1°-steg (`fotometri_ab.json`, psi_sok):

| | ψ | Φ | U0 | E skjerm | synleg for |
|---|---|---|---|---|---|
| (a) vald | −20 | 1256 | 0,76 | 610 | 3 av 8 augepunkt |
| (a) minst skjermlys, skjerma nominelt | −18 | 1242 (−1 %) | 0,77 | 595 (−2,5 %) | margin 0,7 cm |
| (a) skjerma for alle 8 augepunkt | −31 | 1367 (+9 %) | 0,70 | 701 (+15 %) | ingen |
| (a) 15° skjermvinkel | ≈ −33 | 1396 (+11 %) | 0,69 | 719 (+18 %) | ingen |
| (b) vald | −20 | 1311 | 0,67 | 652 | 2 av 8 |
| (b) minst skjermlys, skjerma nominelt | −16 | 1275 (−3 %) | 0,69 | 622 (−4,5 %) | margin 0,8 cm |
| (b) skjerma for alle 8 | −27 | 1399 (+7 %) | 0,64 | 707 (+8,5 %) | ingen |
| (b) 15° skjermvinkel | ≈ −31 | 1465 (+12 %) | 0,61 | 741 (+14 %) | ingen |

U0 ≥ 0,4 held i heile intervallet ψ −60…+10, så det er ikkje U0 som bind. Skjermlyset fell monotont når opninga vender mot brukaren (463 lx ved ψ 0 for (a)), men då er ho synleg. Grunnen er geometrien: røyret heng 20–27 cm framfor skjermplanet og 20 cm over skjermkanten, så skjermen ser opninga med cosinusfaktorar på 0,5–0,7 i heile det skjerma intervallet. I den fysiske røyrmodellen (del 4) er det verre: robust skjerming ved vriding kostar (a) over 2000 lm (+60 %) og over 1230 lx på skjermen, og (b) 2342 lm (+79 %) og 1616 lx.

**Det som verkar: leppe.** Ei svart, stiv forlenging av røyrprofilen frå opningskanten, loddrett ned i arbeid. Lepp på brukarsida skjermar auga, lepp på veggsida skjermar skjermen. ψ −20:

| leppe brukar / vegg | (a) lambertsk: Φ, U0, skjerm | (a) MC, LED på bakvegg | (b) lambertsk | (b) MC |
|---|---|---|---|---|
| 0 / 0 | 1256, 0,76, 610 lx (synleg for 3) | 1161, ≈0,41, 428 lx | 1311, 0,67, 652 (synleg for 2) | 1627, ≈0,47, 829 |
| 5 / 0 | 1275 (+1,5 %), 0,72, 619, skjerma for alle 8 | | 1355 (+3,4 %), 0,61, 671, skjerma | |
| 10 / 20 | 1486 (+18 %), 0,64, 155 | 1243 (−1 %), ≈0,37, 65 | 1513 (+15 %), 0,61, 273 | 1742 (+33 %), ≈0,40, 221 |
| **10 / 30** | **1614 (+29 %), 0,50, 25 lx** (maks 98) | **1342 (+7 %), ≈0,40, 10 lx** | **1579 (+20 %), 0,63, 86 lx** | **1774 (+35 %), ≈0,41, 54 lx** |

Begge modellane seier det same om skjermen: 10–25 lx for (a) og 54–86 lx for (b), skjerma for alle 8 augepunkt. Prisen er 7–29 % meir fluks for (a) og 20–35 % for (b), og U0 kjem ned mot 0,4 i den fysiske modellen. Leppene er stive og roterer med i stemning (`fotometri_leppe.py`): veggsnittet per LED-lm fell frå 0,242 til 0,128 lx (a) og frå 0,272 til 0,132 (b). 10 cd/m² på veggen krev då 3,3 og 3,2 W i staden for 1,7 og 1,5 W, og vrien vert 95–100°. Skjermlyset i stemning går til 0.

## 3 · Synlegheit og spegling

`fotometri_ab.py` (siktliner, spegla auge) og `fotometri_kontroll.py` (framover-strålegang frå auga gjennom tilta skjerm) gjev same kritiske tilt til 0,25°.

| augepunkt | (a): synleg, E ved auga | (a): opninga spegla frå tilt | (b): synleg, E ved auga | (b): spegla frå tilt |
|---|---|---|---|---|
| nominelt (0, −0,30, 0,45) | nei, 2,3° bak planet | 15,75° | nei, 4,2° bak | 18,25° |
| x ±15 cm | nei | 15,75° | nei | 18,25° |
| lener 15 cm fram | **ja, 110 lx** | 16,0° | **ja, 8 lx** (0,4° framfor) | 18,5° |
| 5 cm lågare | **ja, 36 lx** | **14,0°** | nei, 0,1° bak | 16,5° |
| 5 cm høgare | nei | 17,25° | nei | 19,75° |
| fram 15 + lågare 5 | **ja, 257 lx** | **14,0°** | **ja, 122 lx** | 16,5° |
| fram 15 + høgare 5 | nei | 18,0° | nei | 20,5° |
| stemning (ψ −95), nominelt / lågare | aldri synleg | 17,25° / 15,5° | aldri synleg | 20,0° / 18,5° |

- Opninga har 23 kcd/m² (a) og 27 kcd/m² (b) i arbeid. Skjermvinkelen frå nominelt auge er 2,3° og 4,2°. EN 12464-1 krev minst 15° skjermvinkel for 20–50 kcd/m² (eg har ikkje standardteksten framfor meg). Opninga er altså ikkje skjerma i ein brukbar meining. Ho er skjult for tre punkt på same høgd, fordi søket i sok() vel minst Φ, og Φ fell når opninga vender mot brukaren. Optimum ligg difor alltid på synsgrensa.
- **reflected() er rett rekna** for det han testar: spegla auge i planet y = 0,45, skjermrektangelet, og kjelda vend mot skjermpunktet. 0 avvik mot mi spegling over 72 ψ-tilstandar. Men han føreset loddrett skjerm. Ein skjerm som står vinkelrett på siktlina i denne scena er tilta 14° (auga 19 cm over skjermmidten på 75 cm). Då vert opninga i (a) spegla for det lågare auget, og frå 15,75° for det nominelle. Ved 20° syner spegelbiletet på 2,4 % av skjermflata, øvst. Ein blank skjerm speglar 0,04 × 23 kcd/m² = 920 cd/m², 4,6 gonger skjermkvitt. I stemning er det 230 og 267 cd/m² i ein svart skjerm frå 17° og 20°.
- L_MAX = 3000 cd/m² i felles.py er grensa for skjermar over 200 cd/m². For ein skjerm på 200 cd/m² er grensa 1500 cd/m² (positiv polaritet) eller 1000 (EN 12464-1, tabellen for luminansgrenser for armaturar som kan speglast; ikkje kontrollert mot teksten). (a) og (b) bryt begge, (c) med 11 cd/m² bryt ingen.
- I stemning lyser (a) og (b) òg på skjermflata: 84 og 64 lx ved 25 % (maks 230 og 208), 46 og 30 lx ved 10 cd/m² på veggen. Det er ikkje rekna i tal().

## 4 · Lysmodellen: lambertsk opning mot røyret

felles.py reknar opninga som ei lambertsk kordeflate med jamn luminans L = ηΦ/(πA), og η frå motoren: η = sin β + (1 − sin β)·ρf/(1 − ρ(1 − f)). Den direkte delen sin β svarar til ein lambertsk LED-strimmel *i aksen*, vend mot opninga. Eigen MC i hulrommet (ρ 0,85 diffust, endeskiver, opninga i (b) delt av navet), 1,5 M LED-strålar per variant:

| | η | direkte | ψ −20: Φ | U0 7×5 | U0 EN 5×3 | skjerm | minst Φ med U0 ≥ 0,4 og skjerma nominelt |
|---|---|---|---|---|---|---|---|
| (a) lambertsk opning (motoren) | 0,674 | | 1192 | 0,757 | 0,87 | 578 | ψ −18: 1178 lm, 563 lx |
| (a) LED i aksen (det η-formelen føreset) | 0,667 | 0,413 | 823 | **0,15** | 0,50 | 495 | ψ −40: **2521 lm, 2229 lx** |
| (a) LED på bakveggen (røyret kjøler) | **0,562** | 0,207 | 1161 | ≈0,41 | 0,43 | 428 | ψ −20…−23: 1161–1339 lm, 428–590 lx |
| (b) lambertsk opning | 0,667 | | 1245 | 0,673 | 0,78 | 617 | ψ −16: 1209 lm |
| (b) LED i aksen | 0,636 | 0,384 | 1077 | **0,15** | 0,22 | 855 | ψ −35: **2824 lm, 2310 lx** |
| (b) LED på bakveggen | **0,535** | 0,191 | **1627** | ≈0,47 | 0,52 | **829** | ψ −20: 1627 lm, 829 lx |

U0 7×5 i MC er rekna i celler på 4×4 cm rundt motorpunkta. Same estimator på den lambertske opninga gjev 0,69 og 0,62 mot eksakt 0,757 og 0,673, så MC-verdiane er retta med ×1,09 («≈»). EN-cellene er utan slik skeivskap.

- η-formelen er rett for LED i aksen (MC 0,667 mot 0,674). Men ein LED i aksen sender den direkte delen (41 %) ut i ei vifte på ±β = ±25° i snittet, ikkje lambertsk. Ved ψ −20 fell vifta frå y 0,13 til 0,79: framkanten av arbeidsflata får berre det diffuse lyset, og U0 vert 0,15. Modellen i felles.py er altså inkonsistent: η høyrer til ei kjelde som ikkje lagar den fordelinga lys() reknar med.
- Med LED-strimmel på røyrveggen beint mot opninga (det «røyret ber, kjøler og lyser» tyder) er den direkte delen sin(β/2) = 0,22, η 0,56 og 0,54, og den direkte strålen er ±12,5° brei. (a) kjem nesten likt ut (Φ −7,5 %, skjerm −30 %, U0 på grensa). (b) sit 7 cm lenger bak, og strålen ved ψ −20 treffer skjermfoten: Φ +24 %, skjermlys +27 %.
- Konklusjonen er at Φ for (a) og (b) har ei modelluvisse på −35 til +25 % og U0 ei uvisse frå 0,15 til 0,76, avhengig av eit val som ikkje er teke: kvar LED-en sit. Ein opal diffusor i opninga gjer den lambertske modellen gyldig, men overslaget mitt (τ 0,6–0,8, refleksjon tilbake i hulrommet) gjev η 0,39–0,48, altså 1,4–1,7 gonger Φ.
- Liten feil: i (a) er opninga 0,63 m lang (18 segment à 3,5 cm i opning()), medan η reknar hulrommet som k·L = 0,600 m. Opninga er lengre enn hulrommet. Verknad +0,2 % på Φ.

## 5 · Stemningsmålet

R_stem = Ē_vegg/(Ē_vegg + Ē_bord) er eit forhold mellom snitt over ulike flater (1,61 m² vegg mot 1,05 m² bord), ikkje ein fluksdel, og det skil ikkje: 0,90, 0,94 og 1,00 mot kravet 0,5. For (c) er 1,00 ein modellgjenstand (gaussvifte med σ 4°, ingen strølys mot bordet). 25 %-regelen set stemningsfluksen til 25 % av arbeidsfluksen, så stemninga vert sterkare jo dårlegare arbeidslyset er. Premissen i oppgåva om at (c) får ein tredjedel av stemninga, held ikkje: (c) legg 1,5–1,6 gonger meir av kvar lumen på veggen, så (c) får 0,58–0,65 av (a) og (b) på 8×6-gitteret og 0,48–0,58 på det fine.

Framlegg: **fast veggluminans**. Mål effekten som trengst for L̄_vegg = 10 cd/m² over veggfeltet 1,4 × 1,15 m (ρ 0,75, celler på 2–4 cm), med krava fluksdel på veggen ≥ 0,5, opninga ikkje synleg eller spegla over 1000 cd/m², og rapportert maks/snitt. Som kontroll: fast 100 LED-lm.

| | (a) bru | (b) krok | (c) prisme (fjern / nær / nær med søyle og arm) |
|---|---|---|---|
| 25 %-regel: LED-lm i stemning | 314 | 328 | 108 |
| Ē_vegg 8×6 (konsept.json) | 61,6 lx | 69,2 lx | 40,0 lx |
| Ē_vegg 2 cm, 25 % | 75,7 lx | 89,3 lx | 42,8 / 43,9 / 35,1 lx |
| L̄_vegg ved 25 % | 18,1 cd/m² | 21,3 cd/m² | 10,2 / 10,5 / 8,4 |
| lx per LED-lm (lambertsk / MC bakvegg) | 0,241 / 0,229 | 0,272 / 0,239 | 0,396 / 0,406 / 0,324 |
| **L̄_vegg 10 cd/m²: LED-lm, W** | **174 lm, 1,74 W** (MC 1,83) | **154 lm, 1,54 W** (MC 1,75) | **106 / 103 / 129 lm, 1,03–1,29 W** |
| del av arbeidsfluksen | 14 % | 12 % | 24–30 % |
| batteri 21,6 Wh ved 10 cd/m² | 11 t | 13 t | 15–19 t |
| med leppe 10/30 mm (retting R-a2) | 3,3 W | 3,2 W | |
| 100 LED-lm gjev L̄_vegg | 5,8 cd/m² | 6,5 cd/m² | 9,4 / 9,7 / 7,7 |
| maks/snitt på veggen (lambertsk / MC) | 2,4 / 4,4 | 2,7 / 4,9 | 5,9 / 5,0 / 4,4 |

Med fast veggluminans snur rangeringa: (c) er mest effektiv i stemning òg, og (a) minst. (c) lagar ei smalare og skarpare stripe (maks/snitt 4,4–5,9). I den fysiske røyrmodellen er stripa frå (a) og (b) like skarp (4,4 og 4,9), så skilnaden i jamnleik er ein modellgjenstand frå den lambertske opninga.

## Funn og rettingar

- **F1 (kritisk, a/b).** tal() målte ikkje skjermlyset (611/652 lx). Retting: `felles.py` lys(): legg til E_skjerm (55×32 punkt, normal −y, η/πA som no) og eit krav, til dømes E_skjerm ≤ 100 lx (slør ≤ 1,3 cd/m² ved ρ 0,04, kontrast ≥ 130:1). sok() skal velje arbeidstilstand under kravet. Då fell (a) og (b) utan leppe, og (c) held (9–34 lx).
- **R-a2 (retting for a/b).** Leppe 5–10 mm på brukarsida og 30 mm på veggsida i røyrprofilen (`form01/motor.py` geometri() og opning(), `form02/val.py` geometri_krok()). Venta tal: (a) 1340–1610 lm, U0 0,40–0,50, skjerm 10–25 lx; (b) 1580–1770 lm, U0 0,41–0,63, skjerm 54–86 lx; skjerma for alle 8 augepunkt. Stemninga kostar då 3,2–3,3 W.
- **F2 (kritisk, a/b).** visible() testar tre punkt på same høgd, og søket legg ψ på synsgrensa (2,3° og 4,2°). Retting: `felles.py` EYES til eit augevolum (x ±0,15, y −0,30…−0,15, z 0,40…0,50, 8 hjørne) og krav om skjermvinkel ≥ 15° når L > 20 kcd/m². Venta: (a) ψ ≈ −33, 1396 lm (+11 %), 719 lx på skjermen; (b) ψ ≈ −31, 1465 lm (+12 %), 741 lx; eller leppe 5 mm på brukarsida ved ψ −20 (+1,5 % og +3,4 %).
- **F3 (middels, a/b).** reflected() føreset loddrett skjerm. Retting: sløyfe over tilt 0–20° om underkanten og over augevolumet; L_MAX 1500 for skjerm på 200 cd/m². Venta: (a) og (b) får flagget «blendar i arbeid» frå tilt 14° (a) og 16,5° (b). (c) uendra.
- **F4 (kritisk, felles, a/b).** η og lambertsk opning er inkonsistente. Retting: lås LED-plasseringa i `form01/motor.py` eta()/opning() (bakvegg), og rekn utstrålinga med MC i hulrommet (som `fotometri_kontroll.py`) eller føreset opal diffusor og rekn η med han. Venta ved LED på bakveggen: (a) Φ ≈ 1160 lm, U0 ≈ 0,41, skjerm 428 lx; (b) Φ ≈ 1630 lm, U0 ≈ 0,47, skjerm 829 lx, 16,3 W.
- **F5 (middels, felles).** 25 %-regelen og R_stem. Retting: `felles.py` sok() og tal_felles(): byt Ev_stem ved DIM_STEM ut med P_stem for L̄_vegg = 10 cd/m² og maks/snitt; R_stem som fluksdel. Venta: (a) 1,7–1,8 W, (b) 1,5–1,8 W, (c) 1,0–1,3 W.
- **F6 (liten, felles).** Grove gitter. Retting: TASK til arealsnitt (cellesenter, ≤ 1 cm) i tillegg til 7×5 for U0, WALLG og DESKG til celler på ≤ 4 cm. Venta: Φ (a) 1192, (b) 1246 lm; Ē_vegg 75,7 og 89,3 lx ved 25 %.
- **F7 (liten, a/b).** Stemningslyset fell på skjermflata (84 og 64 lx ved 25 %) og opninga vert spegla i ein tilta svart skjerm frå 17° og 20° (230–267 cd/m²). Retting: E_skjerm og reflected() òg i stemningstilstanden.
- **F8 (liten, c).** «9 lx på skjermen» er fjernfelt. Med plata si breidd: 34 lx (maks 93). Retting: konsept.md skriv 9–34 lx. Endrar ikkje rangeringa.

## Kva det endrar i samanlikninga
- Tabellraden «luminans mot auga: skjerma» for (a) og (b) er for sterk. Skriv «skjerma berre for nominelt auge (2,3° og 4,2°); synleg ved 5 cm lågare eller 15 cm fram».
- Raden «lys på skjermen» er rett. Med leppe kan (a) kome ned på nivå med (c) (10–25 lx mot 9–34 lx), men då kostar (a) 1340–1610 lm og 3,3 W i stemning, mot 433 lm og 1,0–1,3 W for (c). Fordelen til (c) i energi aukar, han krympar ikkje.
- Φ for (b) er truleg 24 % for låg om LED-en sit på røyrveggen. (a) er robust for LED-plasseringa (−7 %), (b) er det ikkje.
- Stemningsraden snur når målet er fast veggluminans.
- Det som står seg for (a) og (b): U0 ≥ 0,4 i den lambertske modellen, og 500 lx med 1,2–1,3 klm.

## Uvisse
- Ingen inter-refleksar i rommet; ρ_vegg 0,75 er premiss. Skjermrefleksjon ρ_d 0,04 er det oppgåva bad om; matte AG-skjermar ligg ofte nærare 0,01 (då 1,9–2,1 cd/m² og 89–94:1).
- MC-variantane er modellar: ρ 0,85 diffust i røyret, LED-strimmel ±13° på bakveggen, ingen LED-optikk. Diffusoroverslaget er ein enkel rekneskapsformel, ikkje simulert.
- Augevolumet (±15 cm, +15 cm fram, ±5 cm) er mitt premiss. Kravet om 15° skjermvinkel og grensa 1500 cd/m² er sitert utan standardteksten framfor meg.
- (c)-tala her er mine eigne modellar av optikken, ikkje ei gransking av han.
