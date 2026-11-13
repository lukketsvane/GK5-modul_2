# Gjennomgang av lysskissa

Dato: 13.11.2026. Uavhengig lesing av `konsept/lysskisse/` slik mappa stod kl. 01.33 (motoren, tala, funn 1 til 7, føreseiingane P1 til P4 og vala a, b og c). Laga av hovudøkta for lysskisseøkta.

**Status.** Tre av fem linser vart ferdige (Northern og leveranse, lysfag, bygging og optikk). Linsene fysikk og rom og brukar vart avbrotne, og steget der kvar innvending skulle prøvast av ein andre lesar, vart ikkje køyrt. Kvar innvending kjem altså frå éin lesar. «Rekna» tyder at lesaren rekna sjølv, ofte med ein kopi av motoren. «Lese» tyder at ho viser til fil og linje. «Tolka» er ei vurdering. Linjenummer gjeld kopien frå kl. 01.33.

Tre punkt er rekna av to lesarar uavhengig av kvarandre og av hovudøkta: arealregelen for eigen glød (637 cm² per 100 lm for 500 cd/m²), jamnheit 0,43 åleine som svarar til 0,6 med romlys, og at veggen bak skjermen er eit val i rommet og ikkje ein eigenskap ved lampa.


## Northern og leveranse

### Det som held

- REKNA: Tala i vala a, b og c let seg attskape med motoren i kopien. Profil: 1560 lx, jamnheit 0,30, lysnytte 94 %, stemning 225 cd/m². Retta: 773 lx, 0,39, 46 %, 193 cd/m² i arbeid og 145 i stemning. Vend: 949 lx, 0,27, 57 %, 494 og 648 cd/m². Bordlykt: 79 lx, 4053 og 1013 cd/m². Skript: C:/Users/Iver/AppData/Local/Temp/claude/9773ab2be0aca823/2c1f63c0-844c-4780-bd7e-44e5353e679d/scratchpad/kontroll/northern-og-leveranse/k1.py og k2.py.
- REKNA: Timar per celle stemmer med formelen: 15,1 Wh / (90 lm / 80 lm/W) = 13,4 t for profil, 6,7 t for retta og 8,2 t for vend. Vend i stemning: 100 lm / (pi x 0,0491 m2) = 648 cd/m², og grensa 77 lm for 500 cd/m² er same tal som i konsept/fro/reflektoren.md linje 37.
- REKNA: Profil toler mjuk kant. Med maskekant 13 cm (10 til 90 %) er lysnytta 81 % og 103 lm gjev 350 lx. Med 22 cm er ho 70 % og 120 lm. Profil er framleis øvst eller på nivå med linsekule (71 %).
- LESE: Brettet høver til konseptsteget i dømet til læraren (research/10 linje 447: mange alternative strukturar, så tre valde med namn). Dei umerkte bretta er 2320 x 2320 px, nok til ei heil leveranseside i 2x (2254 x 1594 px).
- LESE: Par-forma (stemning og arbeid, same kamera og eksponering) dekkjer felt 5 «Lys» i konseptsida (research/10 linje 457) og ordlyden «sømløs overgang» i briefen. 2200 K i stemning og 3000 K i arbeid (lysskisse.py linje 732) følgjer F4 og aksen Northern sjølv brukar (research/01 linje 384).
- LESE: Lånt eller reflektert stemning er ikkje framand for Northern. Ombre lyser opp i ein reflektor og på veggen (grunnlag/07 bilete B13), og Ink, Glint og Butterfly lyser indirekte (research/01 linje 247).
- LESE og TOLKA: Kroppen til profil i koden (hovud Ø 7 x 10 cm på røyr, linje 818) har same hovudmål som skjermen på Buddy bord (Ø 7, lengd 10 cm, grunnlag/07 linje 84). Silhuetten ligg i den slanke Northern-typen.
- LESE: Vend er best underbygd for Northern og leveranse av dei tre: 5 av 6 hypotesar, tre primærformer, slektning Ombre, skissemodell på under éin dag, batteri og lysmodul med mynt (konsept/fro/reflektoren.md linje 54 til 86).
- LESE: Grunnlaget for formføringsplansja finst alt i grunnlag/07-formfoering.md: DNA-malen frå merkevareforelesinga, tre verdiord med kva dei utelukkar, reglane R1 til R5 prøvde på 18 lamper, proporsjonar frå ti produktark, palett, ein skala på 7 poeng og biletlista S1 og B1 til B13. Det som manglar, er silhuett, proporsjonstal og poeng for kvart av dei tre konsepta.

### Innvendingar

**N1** (høg, rekna). Stemninga er berre prøvd ved arbeidsbordet, med vegg 25 cm bak skjermen og auget i éin posisjon. 3B seier at kveldsbruken er ein annan stad, på batteri: sofabord, skjenk, vindaugskarm eller hylle. Vala a og b har stemning berre via veggen.

- Prov: LESE: grunnlag/03-3b-analyse.md linje 22 og 52 (kveld, «der folk sit»), linje 48 («der veggen manglar»), grunnlag/00-ramme.md linje 19 (lampa må forsvare plassen som stemningslampe dei fleste dagane). REKNA (k1.py del 3 og 4): profil i stemning utan vegg gjev 156 til 196 cd frå ei opning på Ø 6 cm, altså 56 000 til 69 000 cd/m² innanfor 10° frå aksen. F1 er 3000. Retta-plata sett frå veggsida: 100 lm / (pi x 0,024 m2) = 1326 cd/m².
- Konsekvens: Lag ei kveldsscene (lågt bord utan nær vegg, utan skjerm, auge frå fleire retningar og høgder) og køyr dei 16 der. Funn 2 og vala må vente på ho. Skriv veggkravet inn som sviktrom for a og b.

**N2** (høg, rekna). Funn 2 («ein lekam som gløder, held ingen av luminanskrava. Stemninga må lånast») er for sterkt. Brotet gjeld bør-kravet F5 (500), ikkje skal-kravet F1 (3000). Og brettet prøver berre små lekamar. Northern sin hattetype er ikkje mellom dei 16.

- Prov: LESE: 00-lysskisse.md linje 71. Kravspesifikasjonen linje 9 (F1, 3000) og 26 (F5, bør). research/03 linje 490 merkjer 500 som TOLKING. Hattetypen: grunnlag/07 linje 100 (Kin Ø 20, Tradition Ø 29). REKNA med motoren (k1.py del 1): kule Ø 20 cm gjev 253 cd/m² ved 100 lm og 507 ved 200 lm. Ø 29 cm gjev 120 ved 100 lm og 482 ved 400 lm. Ø 10 cm gjev 507 ved 50 lm. Grensa for 500 cd/m² ved 100 lm er Ø 14 cm.
- Konsekvens: Skriv funn 2 om til: lekamar under om lag Ø 14 cm held ikkje 500 cd/m² ved 100 lm. Legg til eit grep med stor opal lekam (hatt) på brettet.

**N3** (høg, lese). Vala a og b er same konsept slik kurset skil konsept (struktur): kjelde og optikk i eit hovud på stamme, vend frå feltet til veggen bak skjermen. Snu (nr. 7) er same struktur. Northern har alt denne overgangen i Balancer vegg. Utvalet etter likskap under 0,1 plukkar berre grep der lyset flyttar til veggen, og likskap er ikkje eit krav.

- Prov: LESE: lysskisse.py linje 802 til 818 og 775 til 780 (hovud 36 til 40 cm over bordet, same plass ved skjermen). tal.md: stemning vegg 101 og 84 lx, 225 og 145 cd/m², likskap 0,00 og 0,04. research/10 linje 638 (konsepta skal skilje seg i struktur). research/01 linje 327 (Balancer vegg kan vendast mot vegg eller rettast mot skrivebord). F2 i kravspesifikasjonen linje 10 er éi handling under 10 s. research/01 linje 384: Northern forklarar overgangen som dimming og fargetemperatur.
- Konsekvens: Slå a og b saman til eitt konsept med to optikkvariantar, og hent det tredje frå eit anna hjørne (eigen glød). Kall likskap eit mål for fordeling, ikkje for F2.

**N4** (middels, rekna). Kroppane til a og b har ikkje plass til batteri, drivar eller fot. F8, F9, T2 og B1 kan difor ikkje vurderast for to av tre val, og dei tre står ikkje på likt nivå.

- Prov: REKNA frå lysskisse.py: stamme Ø 16 mm (profil, linje 818) og Ø 14 mm (retta, linje 807) mot 21700-cella på Ø 21 x 70 mm. Ingen fot i kroppslista. Vend har fot Ø 12 x 5 cm (linje 753). B1 er merkt for prøving før 18.11 (kravspesifikasjonen linje 21).
- Konsekvens: Gje kvar kropp fot, plass til celle og drivar, og eit punkt for betjening før valet. Oppgje høgd, fotavtrykk i cm² og masseoverslag for alle tre.

**N5** (middels, rekna). Retta er ikkje éi handling slik ho er koda. Mellom stemning og arbeid flyttar både plata og stamma seg. Same plate er dessutan lambertsk i stemning og retta i arbeid.

- Prov: REKNA frå linje 802 til 809 (k2.py): platesenteret flyttar 12,6 cm (12 cm bakover, 4 cm ned), stamma flyttar 4,9 cm, normalen dreier 103°. Profil: berre hovudet dreier, 54°. Stemning er `flate`, arbeid er `straale`.
- Konsekvens: Kod retta som g(t) rundt éi fast stamme og éin akse, og oppgje handlinga og tida for F2. Vel om plata har éi eller to optiske sider.

**N6** (middels, rekna). Timetala i vala (13,5, 6,7 og 8,2 t) gjeld feltstrøket åleine. Same notat seier at arbeidsmodusen uansett treng eit veggstrøk på om lag 210 lm. Då krympar forspranget til profil frå 2,0 til 1,3 gonger retta.

- Prov: LESE: 00-lysskisse.md linje 74 og 93 til 97. REKNA: 15,1 Wh / ((90 + 210) lm / 80 lm/W) = 4,0 t for profil, 3,1 t for retta og 3,4 t for vend. Arbeidslys på batteri er eit kan-krav (T5, 1,5 t). Ramma legg arbeidslyset på leidning.
- Konsekvens: Vis timar med og utan veggstrøk i tal.md og i vala. Ikkje ranger konsepta etter eit kan-krav.

**N7** (middels, rekna). F1 skal prøvast i tre augehøgder før 18.11, og berre 47 cm er rekna. Ved 25 cm endrar rekkjefølgja seg. «Lågast mot auget av alle» for retta gjeld berre frå 47 cm og opp.

- Prov: REKNA (k1.py del 5, auget flytta i motoren, skalert til 350 lx): ved 60 cm er alt som ved 47 cm. Ved 25 cm: profil 202 og vend 302 cd/m² held. Retta 2548 (5627 ved 400 lm). Snu 9372, hogd 17 141, kryss 19 256, dokk 21 533. ATTERHALD: tala heng på den idealiserte avskjeringa (kutt 40 til 50°) i `straale`.
- Konsekvens: Legg 25 og 60 cm inn som faste kolonnar i tal.md. Gje dei retta strøka brønn eller strammare kutt og køyr på nytt.

**N8** (middels, tolka). Verdiordet «mjuk» i formføringsgrunnlaget utelukkar skarp lyskant, og sløkt lysflate skal vere opalkvit og matt. Profil er definert ved skarp maske og klar linse, retta ved prismeark. Slik dei står, les lyset og fronten som teknisk utstyr, sjølv om silhuetten held.

- Prov: LESE: grunnlag/07-formfoering.md linje 34 (mjuk: «utan skarp lyskant») og linje 155 (sløkt flate opalkvit og matt). lysskisse.py linje 207: maskekant k = 0,012, altså 5 cm frå 10 til 90 %. REKNA: mjuk kant kostar 13 til 24 prosentpoeng lysnytte (81 % ved 13 cm, 70 % ved 22 cm). TOLKING: klar linse og prismeark er ikkje opalkvite når lampa er sløkt.
- Konsekvens: Gjer mjuk kant til hovudvarianten av profil. Sei kva fronten er når lampa er sløkt, for både profil og retta. Hovudøkta må avgjere om regelen om opalkvit flate kan brytast med vilje.

**NL1** (høg, lese). Lysskissene dekkjer eitt og eit halvt av ti felt i konseptsida: felt 5 (lys) og delar av felt 9 (F3, og F1 i éi augehøgd). Av dei seks krava som skal prøvast før valet, er E2, M1 og B1 ikkje rørte, og F2 er målt som likskap, ikkje som handling og tid.

- Prov: LESE: research/10 linje 449 til 462 (ti felt: namn, skisse, skissemodell, oppbygging, lys, betjening, Northern, berekraft, skal-krav, opne spørsmål). context/1 Prosjektbeskrivelse: tre konsept med skissemodellar på likt nivå 18.11, og bilete av tre konsept på Moodle 17.11 kl. 23.00. research/11 linje 97 til 99: skisser med lyskjelde, drivar og optikk i omtrentlege mål. Kravspesifikasjonen linje 43 (merkte krav).
- Konsekvens: Det andre økta må levere for kvart konsept, står i framlegg 4. Lysskissa må få kropp, oppbygging og handling ved sida av lyset.

**NL2** (middels, lese). Arbeidet går i djupna på eitt konsept. Reflektorfamilien (ark, bøy, fald, overgang g(t)) gjeld vend, medan a og b berre finst som to idealiserte tilstandar. Fem av seks grep i malen låner òg veggen. Kurset krev likt nivå.

- Prov: LESE: snapshot/reflektor/_mal.py (funksjonen `vipp` rettar speglinga mot veggen bak skjermen i stemning) og _mal/tal.md (stemning vegg 60 til 68 lx for flat, hol, kuv og fald). 00-lysskisse.md linje 107 («kva optikk som lagar dei, er neste spørsmål»). Prosjektbeskrivinga: «Konseptene skal være på likt nivå».
- Konsekvens: Før meir djupn i reflektoren: løft dei to andre konsepta til g(t) med `overgang()`, kropp med fot og same talsett. Elles blir alle tre avhengige av vegg, og nivået ulikt.

**NL3** (middels, rekna). Bileta kan ikkje brukast som konseptbilete slik dei er. Lampa er svart på svart, par-bileta er for små, og teksten i dei merkte bretta blir uleseleg på ei side.

- Prov: LESE og REKNA: par-profil.png er 888 x 452 px og par-retta.png 1008 x 512 px (ruter på 420 til 480 px). Leveransesidene er 1127 x 797 px, rendra til 2254 x 1594 px (leveransar/01_fase1_sider/LES_MEG.md). Merketeksten er 21 px på eit brett på 2320 px, altså om lag 7 px når brettet står på ei side. Regel 2 i 00-lysskisse.md linje 14: lampa er svart.
- Konsekvens: Lever ruter utan tekst i minst 1040 px, og eit eige bilete der kroppen syner. Sjå framlegg 4.

### Framlegg

- 1. Tre konsept som ligg langt frå kvarandre (TOLKING, med rekna tal). SNU: profil (S4) med mjuk kant i arbeid (103 til 120 lm for 350 lx), hovudet vridd 54° mot veggen i stemning. Kropp: kapsel Ø 7 x 10 cm, røyr Ø 25 mm, fot Ø 9 til 12 cm. Handling: vri hovudet. B1: batteristav ut av røyret, lysmodul bak gjenga front slik Snowball oppladbar har. Slektningar: Buddy bord, Blush, Balancer vegg. Retta flate (S8) er optikkvarianten om linsa ikkje let seg skaffe. Sviktrom: krev vegg.
- 2. VEND: skive med matt og retta side over kjelde i foten (S2), 147 lm for 350 lx, stemning under 77 lm for 500 cd/m². Kropp: låg sylinder Ø 12 x 5 cm, line Ø 8 mm, skive Ø 25 cm. Handling: vende skiva. B1: lyskjerne og batteri som to proppar i foten, ingenting elektrisk over foten (konsept/fro/laga.md, frø 2). Slektningar: Ombre og Glint. Reflektorfamilien høyrer heime her.
- 3. HATT (nytt grep, ikkje på brettet): stor opal lekam som gløder sjølv, med retta nedlys frå undersida i arbeid (S10 i hattekropp, gjerne med S11: hatten løfta frå 22 til 45 cm). REKNA med motoren (k2.py): Ø 20 cm gjev 253 cd/m² ved 100 lm, Ø 29 cm gjev 120. Arbeid med 80 % nedlys: 574 til 612 lx ved 400 lm, 229 til 244 lm for 350 lx, jamnheit 0,27 til 0,34, likskap 0,69 til 0,74. Kropp: opal kuppel og sylinder. Handling: løfte hatten. B1: hatten gjenga av over lysmodulen, batteri i sylinderen. Slektningar: Kin og Tradition bord. Sviktrom: 7100 til 8800 cd/m² ved auge 25 cm utan brønn, og nærast det busette.
- 4. Lever dette for kvart konsept, likt for alle tre: (a) stemning og arbeid som to åtskilde PNG utan tekst, kvadratiske, minst 1040 px, sRGB 8 bit, same kamera og eksponering. (b) Overgangsstripe t = 0, 0,5 og 1 i 520 px per rute, med `overgang()`-tala. (c) Eitt bilete der kroppen syner: same kamera, lampa sløkt, romlys på, kroppen i grå-beige. Klassane Syl, Skive, Kule og Rekt tek alt `rho=`, men hjelparane syl, skive og kule sender han ikkje vidare. (d) Sideriss og frontriss av kroppen som SVG i millimeter, til silhuettrekkja i formføringsplansja. (e) Éi CSV-rad per konsept og tilstand med krav-ID i kolonnenamnet: lm brukt (350 lx, ikkje 400), W, lux felt, jamnheit, cd/m² mot auget ved 25, 47 og 60 cm, vegg lx, ansikt lx, timar med og utan veggstrøk, høgd, største breidd, fotavtrykk i cm², masseoverslag, tal primærformer, handling og tid. (f) Éi line med atterhald: modell, svart rom, 2 % sprut.
- 5. Northern-prøve av dei andre kandidatane (TOLKING frå research/01 og grunnlag/07). Kan bli Northern-lampe: linsekule (Snowball-silhuetten, men 2068 cd/m² ved 100 lm og jamnheit 0,12), snu (Buddy og Blush, men overgangen finst alt i Balancer vegg), hogd (skive på røyr, ny høgdehandling, men 61,5 cm er over spennet 27 til 55 cm, og 21,5 til 61,5 cm krev tre teleskopledd). Blir utstyr: veggvask og skjermlist (lyslist utan lekam, grunnlag/07 linje 161), plate (møtelys, 2546 cd/m²), kryss som naken søyle. Dokk: masta står att åleine i stemning.
- 6. Skår konsepta med skalaen i grunnlag/07 del 6 (R1 til R5, palett og proporsjon, 0 til 7), ikkje med dei seks hypotesane i ramma. H6 er forkasta som regel og H2 retta der. Oppgje høgd, fotbreidd, fot av høgda og lyshovud mot fot for kvart konsept.
- 7. Legg til eit hatt-grep og ei kveldsscene i motoren før neste brett. Skriptet k2.py har ei ferdig `g_hatt(m, r, lav, hog, del_glod)` som kan kopierast: C:/Users/Iver/AppData/Local/Temp/claude/9773ab2be0aca823/2c1f63c0-844c-4780-bd7e-44e5353e679d/scratchpad/kontroll/northern-og-leveranse/k2.py.
- 8. Til 18.11 held det med volum-skissemodellar i 1:1 i same materiale for alle tre, pluss lysparet frå motoren. Kurset krev skissemodell, ikkje fungerande lys. Bordforsøka P1 til P4 er eit tillegg der dei let seg gjere, og bør då gjerast for alle tre eller merkjast som ekstra.

### Spørsmål

- Kva er handlinga i retta flate: kva akse dreier plata om, og står stamma i ro? Koden flyttar stamma 4,9 cm.
- Kva lysstraum skal stemninga dømmast ved? Brettet brukar 100 lm, ramma seier 50 til 200 lm, og T7 seier 4 t ved 200 lm. Hattetypen og vend skiftar dom mellom 50, 100 og 200 lm.
- Er reflektorfamilien meint som utdjuping av konsept c åleine, eller skal han erstatte a og b? Kva er då dei tre konsepta 18.11?
- Kan motoren få ei kveldsscene (lågt bord, ingen nær vegg, ingen skjerm, fleire augepunkt) til 15.11, og kor lang tid tek eit nytt brett i 1040 px per rute?
- Kva er fronten på profil og retta når lampa er sløkt: klar linse, prismeark, eller eit opalt lag framfor? Kva kostar det opale laget i lysnytte?
- Kva linse skal skissemodellen av profil bruke når byggjesettet berre har projeksjonslinsa på 27 til 29 cm brennvidd, og V6 krev 41 til 64 mm?
- Held funn 2 òg for ein halvkuppel (Kin-forma) og ikkje berre for heil kule? Kontrollen her er gjord med `glod`, som er ei heil kule.
- Skal bileta til leveransesidene òg finnast i gråtone? Fase 1-sidene er berre svart, kvitt og grått, og stemningsbretta er sterkt gule.

## Lysfag

### Det som held

- REKNA: tal.md er reprodusert tal for tal (16 grep x 2 tilstandar) frå motoren i snapshot, auge 47 cm. Skript og utdata: C:/Users/Iver/AppData/Local/Temp/claude/9773ab2be0aca823/2c1f63c0-844c-4780-bd7e-44e5353e679d/scratchpad/kontroll/lysfag/k1.py, k2.py, k2.txt, k3.py.
- REKNA: Funn 2, tala for glød stemmer med L = Φ/(π·A) og kuleformelen i research/03 l.107: 100 lm gjev 2068 cd/m² (kule Ø 7 cm), 1013 (Ø 10 cm), 637 (plate 20 x 25 cm), 648 (skive Ø 25 cm). Vend held 500 cd/m² under 77 lm. Lånt stemning ligg på 51 til 225 cd/m² ved 100 lm og held 500 òg ved 200 lm (profil 450, retta 290).
- REKNA/LESE: Funn 3 held som geometri og samsvarer med Arbeidstilsynet (research/03 l.39: sterke lyskjelder aldri rett framfor eller bak skjermen). Ingen kjelde ligg i spegelsona ved 25, 35, 47 og 60 cm augehøgd (L_spegl = 0 for alle 16, loddrett skjerm).
- REKNA: Funn 4, ingen av dei 16 når 0,6 (høgst 0,49), og cos⁴-tala i V7 stemmer (25 % ved 30 cm, 64 % ved 60 cm, 30 cm ut).
- REKNA/LESE: Funn 5 held og er sterkare enn skrive. 45 lx kjem frå research/03 l.59-69: vegg ρ 0,7 og skjerm 100 cd/m² gjev 10 cd/m² = 1:10. Same golv kjem frå kvitt ark (ρ 0,82) ved 350 lx: 91 cd/m², 10:1 gjev 41 lx. Dimma til 350 lx på feltet gjev dei retta 3,7 til 9,6 lx på synleg vegg (kryss 34 lx), altså under golvet for alle.
- REKNA: Funn 6 held. Plata: 171 lx direkte + 13 lx indirekte = 184 lx (handrekna 174 direkte). Feltet ved 350 lx kastar 14 lx opp på ansiktet (handrekna 14,4). Via veggen bak skjermen kostar ansiktslys 0,13 lx per lm på veggen (veggvask: 217 lm på vegg gjev 28 lx), så 50 lx ville krevje om lag 710 lm.
- LESE/REKNA: Budsjetta er innanfor ramma. 100 lm ligg i 50 til 200 lm. 400 lm = 5,0 W ved 80 lm/W, under B3 (7,5 W = 600 lm) og under 1000 lm og 10 W. 15,1 Wh og 80 lm/W er tala i research/05 l.51 og l.131. 2200 og 3000 K held F4 og research/03 (stemning 1800-2400, arbeid 2700-3000).
- REKNA: 13 av 16 held 10 lx melanopisk EDI i stemning ved 100 lm, sjølv med DER 0,44 (høgst 18 lx fotopisk ved auget = 8,0 lx mEDI).

### Innvendingar

**F1** (høg, rekna). «Mot auget» er rekna frå eitt augepunkt (47 cm). F1 er eit skal-krav for 25 til 60 cm. Ved 25 cm står auget inne i strålen til sju av dei retta grepa, og val (b) bryt 3000 cd/m². Setninga «alle dei retta under 370» og «(b) lågast mot auget av alle» gjeld berre ved 47 og 60 cm.

- Prov: Eiga køyring av tal() med AUGE = b(0, -0.15, h), arbeid 400 lm, cd/m² ved 25 / 35 / 47 cm: retta 5627 / 694 / 193, snu 18517 / 3404 / 401, kryss 26448 / 7143 / 498, arbeidslampe 13796 / 468 / 400, zoom 35615 / 12912 / 663, hogd 26425 / 1106 / 324, dokk 35328 / 15287 / 513. Stabile: profil 901 (berre sprut), vend 820 / 532 / 494. Retta skalert til 350 lx ved 25 cm: 2546. Vinkel frå aksen til auget for retta: 60° ved 47 cm, 51° ved 35 cm, 44° ved 25 cm, og kutt er sett til 45°. Dokk: 49° ved 47 cm mot kutt 42°, altså 7° margin. Krav: grunnlag/04 F1.
- Konsekvens: tal() må gje høgste luminans over 25, 35, 47 og 60 cm, og tal.md må få den kolonnen. Funn 2 (arbeidsdelen) og val (b) må skrivast om: 193 cd/m² er ei følgje av kutt 45° og sprut 3 %, ikkje eit resultat. Retta strøk må få bronn eller kutt som held ved 25 cm.

**F2** (høg, rekna). Funn 2 «Stemninga må lånast» er ein artefakt av storleik og budsjett. Lekamane i brettet er Ø 7 og Ø 10 cm, 500 cm² og 491 cm², og budsjettet er 100 lm. Ein glødande lekam held 500 cd/m² når arealet er stort nok eller lysstraumen låg nok.

- Prov: L = Φ/(π·A), einsidig matt flate, for 500 cd/m²: 50 lm 318 cm² (skive Ø 20 cm), 100 lm 637 cm² (Ø 28,5 cm), 200 lm 1273 cm² (Ø 40 cm). For 1500 cd/m²: 106, 212 og 424 cm² (Ø 11,6, 16,4 og 23,2 cm). Kule (L = Φ/(4π²r²)), 500 cd/m²: Ø 10,1 cm ved 50 lm, Ø 14,2 cm ved 100 lm, Ø 20,1 cm ved 200 lm. Kule Ø 16 cm (median bordlykt i formromkartet, fotavtrykk 201 cm² = F9) ber 126 lm ved 500 cd/m² og gjev 396 cd/m² ved 100 lm. Ved 50 lm (nedre ende i ramma) gjev plata 318 og vend 324 cd/m². 500 cd/m² er dessutan eit bør-krav (F5) og ei tolking i research/03 (ope spørsmål 4).
- Konsekvens: Skriv funn 2 som grense, ikkje forbod: eigen glød på 100 lm krev minst 637 cm² flat eller kule Ø 14 cm, under det må stemninga lånast eller dimmast til Φ = π·A·500. Legg til ei bordlykt på Ø 16 cm som referanse og ei kolonne «lm som held 500 cd/m²». Vis stemningstala for 50, 100 og 200 lm (T7 prøver 200 lm).

**F3** (høg, rekna). Lysnytte som mål løner lys berre på 0,24 m² og straffar lys rundt feltet. Research/03 krev lys på nære omgjevnader og har det med i lysbudsjettet. Profilen sine 94 % og 90 lm kjem av at bordet rundt feltet står mørkt.

- Prov: Eiga rekning frå E_bord i tal.csv, skalert til 350 lx på feltet: resten av bordet (0,74 m²) får profil 8 lx (45:1), linsekule 22 lx (16:1), vend 42 lx (8,3:1), arbeidslampe 42 lx, retta 60 lx (5,8:1), dokk 107 lx (3,3:1), hogd 131 lx (2,7:1). Research/03 l.49: nære omgjevnader 300 lx ved 500 (200 ved 300), Uo minst 0,40. L.55: 3:1 mellom arbeidsfelt og nære omgjevnader. L.260-262: budsjettet reknar 180 lm (åleine) eller 90 lm (med romlys) på resten av bordet. 3:1 ved 350 lx er 117 lx x 0,74 m² = 86 lm til. Med 150 lx romlys er alle innanfor (profil 500:158 = 3,2:1).
- Konsekvens: Ny kolonne «bord rundt feltet ved 350 lx» med forhold felt:rest. Funn 1 og val (a) må seie at 90 lm og 13,5 timar gjeld utan lys rundt feltet. Med 3:1 åleine treng profilen om lag 90 + 86 = 176 lm på bordet, same nivå som retta (181 lm).

**F4** (høg, rekna). Funn 5: (i) «V3 sa 220» samanliknar to ulike storleikar. (ii) 24 % av veggsona ligg skjult bak skjermen sett frå auget, og veggvasken legg det meste av lyset der. For veggen auget ser, kostar 100 lx om lag 444 lm med dette strøket, ikkje 210. (iii) Skjermen står på 40 cd/m² i motoren, medan golvet 45 lx føreset 100 cd/m².

- Prov: (i) konsept/00-formromkart.md V3: Φ = π·E·d²/ρ = π·100·0,7²/0,7 = 220 lm er lumen på veggen for 100 lx på ANSIKTET 0,7 m unna. Motoren sine 210 lm er 98 lm (100 lx x 0,98 m²) delt på treffdelen 47 %. (ii) Eiga rekning: veggruter der strålen frå AUGE kryssar SKJERM er tekne ut. Veggvask arbeid: heile sona 191 lx, synleg del 90 lx, lågaste synlege rute 5 lx, høgste 1434 lx. 400·100/90 = 444 lm for 100 lx, 200 lm for 45 lx. To strøk: 90-180 + 444 = 534-624 lm = 6,7-7,8 W mot B3 7,5 W. Stemning: profil 101 lx i sona, 54 lx synleg. Veggvask 62 og 24 lx. (iii) lysskisse.py l.281 SKJERM_CD = 40. Research/03 l.61-69 brukar 100 cd/m². Ved 40 cd/m² er 10:1 18 lx.
- Konsekvens: Stryk «(V3 sa 220)». Mål E_vegg på den synlege delen (snitt og lågaste rute), og gje òg cd/m². Oppgje kostnaden for golvet (45 lx) og målet (100-150 lx) kvar for seg. Set veggstrøket ved sida av eller over skjermen og rekn summen på nytt mot 600 lm. Vel éin skjermluminans (100 cd/m² som i research/03) eller grunngje 40.

**F5** (middels, rekna). Funn 1 «ved same watt» er same lumen ut. Motoren gjev alle 80 lm/W, medan optikken taper ulikt. Formromkartet set sjølv 30 til 60 % verknadsgrad for profilprinsippet. Timane i val (a) er difor for høge.

- Prov: lysskisse.py l.731-733 og l.664: alle grep får lm direkte, W = lm/80. konsept/00-formromkart.md S4: «Sviktrom: 30-60 % verknadsgrad (ANTAKING, 13)». Research/03 l.305: reflektor taper 20-40 %. Eiga rekning: 90 lm ut ved 100 lm/W kjelde (LMW_KJELDE) og optikk 0,3-0,6 er 1,5-3,0 W, altså 5,0-10,1 timar per celle (15,1 Wh), ikkje 13,5.
- Konsekvens: Skriv «ved same lumen ut». Gje kvart strøkslag ein verknadsgrad (ANTAKING med spenn til P1 er målt) og rekn W og timar frå han. Val (a): 5 til 10 timar, som overlappar retta (6,7) og vend (8,2).

**F6** (middels, rekna). Funn 4 måler mot 0,6, som er Uo for arbeidsfeltet i EN 12464-1 (takanlegg). F3 har ikkje noko tal for jamnheit. Og «høgd er det som hjelper» er ufullstendig: alle 16 siktar ei gausslobe mot midten av feltet frå høgre side. Sikte og plass over feltet hjelper like mykje, mot lågare lysnytte.

- Prov: Research/03 l.47 (Uo 0,60 arbeidsfelt), l.49 (0,40 nære omgjevnader), l.43 (standarden er referanse, ikkje noko lampa må oppfylle åleine). F3: 350 lx åleine, 500 med romlys. Eiga rekning: 0,60 med 150 lx jamt romlys krev (0,6·500-150)/350 = 0,43 åleine. Med romlys: dokk 0,64, hogd 0,62, skjermlist 0,59, arbeidslampe 0,59, retta 0,57, profil 0,51, vend 0,49. På 0,3 x 0,2 m der arket ligg: dokk 0,87, hogd 0,82, retta 0,78, profil 0,64, vend 0,46. Søk med straale() frå b(0.42, 0.40, h), direkte lys: beste U 0,54 (h 40 cm), 0,63 (50 cm), 0,71 (60 cm) med sikte forbi feltet (x -0,45, y 0,05, sigma 30°), lysnytte 0,16-0,21. Isotrop kjelde rett over feltmidten: U 0,73 ved 40 cm. U 0,6 frå sida kostar 84/0,18 = 467 lm for 350 lx.
- Konsekvens: Skriv kravet ut: framlegg minst 0,4 på 0,6 x 0,4 m åleine (gjev 0,6 med 150 lx romlys) og minst 0,6 der arket ligg. Legg til kolonnane «U med romlys» og «U på arket». Vis jamnheit mot lysnytte som éi avvegingskurve, for funn 1 og funn 4 dreg kvar sin veg, og val (a) ligg i den eine enden.

**F7** (middels, rekna). Kolonnen «Ansikt, lx» blandar retningar. 81 til 98 % av luxa kjem nedanfrå (gjenskin frå bordet, om lag 50° under vassrett) for 13 av 16 grep. Plata, det einaste grepet som «lyser på ansiktet», gjer det frå 16° under augehøgd. Research/03 seier frå augehøgd til 15° over, 20 til 45° til sida, ikkje nedanfrå.

- Prov: Eiga oppdeling av E_ansikt (arbeid 400 lm): profil 62 lx = 2 direkte + 55 via bord, vend 67 = 21 direkte (-4°) + 41 via bord, retta 43 = 4 + 36, plate 184 = 171 direkte (-15,6°) + 10 via bord. Berre hogd og dokk står over auget (+10,6°) og gjev 2,5 lx direkte. Research/03 l.504 (retning), l.209 (flatesenter 47-63 cm over bordet for 0-15° over auget på 60 cm), l.205 (lys nedanfrå som vanleg feil). Storleik, E = π·L·a²/(a²+d²), d 60 cm: 50 lx krev Ø 12 cm ved 1500 cd/m² og Ø 22 cm ved 500, 150 lx krev Ø 22 cm ved 1500, 200 lx Ø 25 cm. 50 lx frå plassen til plata (0,73 m) kostar 109 lm.
- Konsekvens: Del kolonnen i «frå augehøgd eller over» og «nedanfrå», og lat berre den første telje mot F10. Funn 6 bør seie geometrien: flate på minst Ø 12 til 22 cm med senter 47-63 cm over bordet og 20-45° til sida. For vala: (c) har ei flate som er stor nok (Ø 25 cm, 707 cd/m² for 50 lx) men står 6 cm under auget og vender mot feltet i arbeid, (b) si plate på 240 cm² gjev 1444 cd/m² for 50 lx, (a) har inga flate.

**F8** (middels, lese). Funn 7: låg likskap er ikkje det same som god overgang. Likskapen måler kor ulike dei to endepunkta er. Briefen og notata definerer saumlaust som trinnlaust, éi handling, og lys på flata ved skjermen i alle modusar. Grensa «over 0,9 er dimmar, ikkje overgang» er økta si eiga og har ikkje dekning i kjeldene.

- Prov: context/2 Endelig designbrief Northern.md l.31 og «flere nivåer eller moduser». Research/03 l.363 (éin kontroll som aukar nivå og flyttar lyset frå flate til bord), l.501 (dimmeområde 2-100 % trinnlaust = saumlaus overgang), l.358 (lys på flate i synsfeltet bør vere med i alle modusar), l.235 (arbeid er focal glow skrudd opp, ikkje ei anna lampe). Research/01 l.384 (Northern forklarar overgangen som dimming og fargetemperatur). Research/02 l.321 (trinnlaus). F2: éi handling under 10 s. Motoren: dei 16 grepa finst berre som 's' og 'a' (som_t er eit sprang ved t = 0,5), så overgang() er ikkje køyrd på dei. Profil (likskap 0,00): synleg vegg 54 lx i stemning og 3,7 lx ved 350 lx-punktet i arbeid. Kryss (0,37) er det einaste retta grepet som held veggstrøket i arbeid (47 lx, 34 lx ved 350 lx).
- Konsekvens: Kall talet «flytting» og ikkje bruk det til å sile. Skriv a, b og c som g(t) og køyr overgang() med minst 7 steg: topp (ved 25 og 47 cm), sprang, jamn_auke og lågaste vegglux undervegs. Setninga «alle tre er verkelege overgangar» kan ikkje stå før det er gjort.

**F9** (middels, rekna). Melanopisk EDI om kvelden står i ramma, men ikkje i tala, endå motoren alt reknar lux loddrett ved auget i stemning. Plate og vend (val c) ligg over 10 lx mEDI ved 100 lm.

- Prov: tal.csv, E_ansikt i stemning: plate 46,1 lx, vend 33,1 lx, skjermlist 18,1, linsekule 16,9, bordlykt 16,4, retta 14,1, profil 13,4. Research/03 l.183: DER 0,44 ved 2700 K, 10 lx mEDI = 23 lx fotopisk. Det gjev plate 20,3 og vend 14,6 lx mEDI. Vend held 10 lx først under 69 lm. Ved 200 lm: retta 28 lx = 12,4 og profil 27 lx = 11,8 lx mEDI. DER ved 2200 K er lågare, men ukjend (research/03 ope spørsmål 6), så 0,44 er ei øvre grense.
- Konsekvens: Ny kolonne «stemning: lux ved auget» og mEDI = DER·E med DER oppgjeven. Val (c): legg til at stemninga må under om lag 69 lm for mEDI og 77 lm for luminans.

**F10** (middels, tolka). Lånt stemning og veggstrøket føreset ein kvit vegg (ρ 0,72) 25 cm bak skjermen. Det er eit val i rommet, ikkje ein eigenskap ved lampa, og halve målgruppa sit i fleirbruksrom.

- Prov: lysskisse.py l.262 og l.271 (YV = 0,70, VEGG ρ 0,74/0,72/0,68), skjerm i y = 0,45. Formromkartet S1: «Sviktrom: ingen lys vegg». Ramma kap. 3: 50 % arbeider frå fleirbruksrom. Research/04 l.267: scenario C er kjøkenbordet. Veggluminansen er L = ρ·E/π, så ρ 0,5 gjev 0,69 gonger tala i brettet (profil 225 til 156 cd/m²).
- Konsekvens: Køyr dei tre vala i to rom til: vegg ρ 0,5, og vegg 1 m unna eller ingen vegg. Oppgje kva av stemninga som står att. Eit val som berre har lånt stemning, må ha eit svar for bordet utan vegg.

**F11** (låg, rekna). Lys frå lampa på sjølve skjermflata er ikkje rekna. Regelen frå funn 3 (lyspunkt framfor skjermplanet) gjev streiflys over skjermen. Snittet held 200 lx for alle, men kanten nærast lampa går over hos ni grep, mellom dei val (b).

- Prov: Eiga rekning, 24 punkt på skjermflata, direkte + indirekte, skalert til 350 lx på feltet, snitt / høgste: retta 101 / 362 lx, sidelys 178 / 1419, zoom 143 / 1065, snu 126 / 752, arbeidslampe 154 / 628, kryss 134 / 570, hogd 117 / 515, dokk 109 / 445, profil 28 / 85, vend 47 / 94. Research/03 l.487: under 200 lx på skjermflata.
- Konsekvens: Legg E_skjerm (snitt og høgste) inn i tal(). Regelen i API.md bør seie «framfor skjermplanet og avskjerma mot skjermflata».

### Framlegg

- Lat tal() gå over augehøgdene 25, 35, 47 og 60 cm og gje høgste luminans (lampe og romflate) og spegling for kvar. Køyr dei 16 og reflektorfamilien på nytt. I reflektormalen blir L_mot(AUGE) for arket òg berre rekna frå 47 cm.
- Nye kolonnar i tal.md, alle ved 350 lx på feltet: bord rundt feltet (lx og forhold), synleg vegg (lx og cd/m², snitt og lågaste rute), U med 150 lx romlys, U på arket, lys på skjermflata (snitt og høgste). I stemning: lux ved auget, mEDI med oppgjeven DER, og lm som held 500 cd/m².
- Éi rad med luminansforhold per grep ved 350 lx: ark (ρ 0,82: 91 cd/m²), bord (ρ 0,41: 46 cd/m²), skjerm, synleg vegg. For a, b og c åleine er ark:vegg no om lag 107:1, 66:1 og 61:1 mot grensa 10:1. Med 45 lx på synleg vegg blir det 9:1.
- Skriv funn 2 om til arealtabellen (500 og 1500 cd/m² ved 50, 100 og 200 lm) og legg ei bordlykt på Ø 16 cm til som referanse.
- Byt «same watt» med W rekna frå verknadsgrad per strøkslag (opal, reflektor, maske og linse, prismeark), merkt ANTAKING til P1 og forsøka i research/13 er gjorde.
- Flytt veggstrøket ut frå bak skjermen og rekn på nytt: synleg veggring er 0,745 m², så 100 lx er 75 lm på veggen og 45 lx er 34 lm. Kontroller summen felt + vegg (+ ansikt 109 lm for 50 lx) mot 600 lm (7,5 W).
- Skriv dei tre vala som g(t) og køyr overgang() med minst 7 steg. Rapporter topp ved 25 og 47 cm, sprang, jamn_auke og lågaste vegglux undervegs.
- Del ansiktslyset i «frå augehøgd eller over» og «nedanfrå», og prøv for (b) og (c) ei tredje stilling der flata vender mot ansiktet med senter 47 til 63 cm over bordet.
- På bordet før 18.11: foto frå 25, 47 og 60 cm augehøgd (prøva F1 sjølv nemner), lux på veggen ved sida av skjermen og ikkje bak han, og prismearka fotografert i 45°, 60° og 75° (forsøk 6 i research/13), for det er vinklane auget ser (b) frå.
- Flimmer høyrer ikkje heime i motoren. Hald det som krav til drivar og kameraprøve (research/03 l.368). Fargetemperaturen treng berre stå per tilstand (2200 og 3000 K) og gå inn i DER.

### Spørsmål

- Kvifor står skjermen på 40 cd/m² når research/03 reknar veggolvet frå 100 cd/m² og ansiktslyset frå 150 til 250 cd/m²? Kva tal skal styre F6?
- Har sprut 2 % (3 % for retta, 19 % for vend) noko grunnlag? Profilen sine 901 cd/m² er berre sprut, og 7 % gjev 3150 cd/m². Kan P1-oppsettet òg måle dette før 18.11?
- Kutt 45° for retta er sett, ikkje målt. Kva er luminansen til prismestabelen ved 44°, 51° og 60° frå aksen, som er det auget ser frå 25, 35 og 47 cm?
- Skal F1-bandet 25 til 60 cm prøvast berre i y = -0,15, eller òg framoverlent og frå sida (ein annan i rommet, sofa)?
- Kva er lysnytta og jamnheita til profilen når maska blir gradert eller uskarp, slik at feltet ikkje får skarp kant? Research/03 l.484 seier «ingen skarp kant på lysfeltet» og l.232 «mjuke gradientar» i stemning.
- Kvar på veggen skal veggstrøket liggje når 24 % av sona er skjult bak skjermen, og kor mykje av profilen si «sol» (54 av 101 lx synleg) er meint å syne?
- Alle 16 grep står til høgre for feltet, og ryggfiguren har ikkje armar. Er skuggen frå skrivehanda på arket vurdert?
- Kva gjer dei tre vala i eit rom utan lys vegg 25 cm bak skjermen?

## Bygging og optikk

### Det som held

- REKNA: Tala i tal.md blir attskapte eksakt når eg køyrer motoren frå kopien: profil 1560 lx, jamnheit 0,30, 94 %, 901 cd/m² mot auget; retta 773 lx, 46 %, 159 (lampe) og 193 (flate) cd/m²; vend 949 lx, 57 %, 494 cd/m²; bordlykt 79 lx, 5 %, 4053 cd/m². Utdata: C:/Users/Iver/AppData/Local/Temp/claude/9773ab2be0aca823/2c1f63c0-844c-4780-bd7e-44e5353e679d/scratchpad/kontroll/bygg-og-optikk/modell-ut.txt
- REKNA: «Linse på 40 til 65 mm finst ikkje i byggjesettet» held. Tynn linse, kast 450 mm: f = 40,9 mm (maske 60 mm, m = 10) og 64,3 mm (maske 100 mm, m = 6). Projeksjonslinsa (f = 285 mm) er ubrukeleg på bordet: ved 634 mm kast må maska stå 518 mm bak linsa og vere 490 mm brei, og under 570 mm kast (2f) blir biletet mindre enn maska.
- REKNA: Fresnel-tala i API.md og research/13 held med spegellikninga (f = 187,1 mm): kjelde 250 mm gjev bilete 744 mm framfor plata; feltbreidd 40 cm frå plata er 816, 626, 436, 285 og 132 mm for kjelde 100, 120, 150, 187 og 250 mm.
- REKNA: Bordlykta på 5 % er geometri: feltet dekkjer 0,487 sr frå kula, altså 3,9 % direkte (65 lx av 79 lx ved 400 lm, resten er refleksar). Modellforholdet i P1 er 1560/78,7 = 19,8. Kuleluminansen i P4 er rett: 100 lm frå Ø 10 cm gjev 1013 cd/m².
- REKNA: P2 held uavhengig av lyktestrålen. Naken lykt med sigma 20, 30 og 40° på dei to plassane i motoren gjev jamnheit 0,18, 0,17, 0,15 i 13 cm og 0,49, 0,49, 0,48 i 60 cm (motoren: 0,18 og 0,49). P3 held: profil ved y = 0,40 gjev 0,30, ved y = 0,50 gjev 0,01 (2 av 24 ruter i skugge).
- REKNA: Skuggemaske utan linse gjev like skarp kant som motoren sin «skarpe» maske. Motoren har 10–90 %-breidd 53 mm (k = 0,012 m, lysskisse.py l. 207). Ei kjelde på 3 mm med maske 65 mm framfor gjev halvskugge 26 mm vinkelrett på strålen midt i feltet (46 mm på bordet ved 55° innfall), med maske 100 mm framfor 16 mm (28 mm på bordet).
- REKNA: Ark-modellen bevarer energi (MATT: 112 lm inn, 95 ut frå arket pluss 13 lm forbi = 108; SATIN: 449 inn, 359 ut pluss 51 forbi = 410), og gausslobe-normaliseringa er rett for sigma opp til om lag 15°. Forholdet satin/matt på feltet i ark-modellen er 660/200 = 3,3, i samsvar med føreseiing 1 i konsept/fro/reflektoren.md (minst 2,9, modell 3,4 til 4,0).
- REKNA: Etendue hindrar ikkje profilen. Feltet dekkjer 0,385 sr projisert frå lyspunktet; opning Ø 60 mm gjev 1087 mm²·sr, medan ein COB med 9 mm lysflate treng 200 og 13 mid-power-diodar 368 mm²·sr. Hovudet på Ø 70 × 100 mm i g_profil er dimensjonert rimeleg for maske 60 mm og f om lag 58 mm.
- LESE: Byggjesettet dekkjer retta flate (lysboks, diffusor, to prismeark, reflektorark; research/13 kap. 3.5) og vend (papp, kvitt papir, aluminiumsfolie; reflektoren.md l. 84) til 0 kr. Åtvaringane om projektoren (ikkje straum, ikkje sol) står rett i research/13 kap. 2.2.

### Innvendingar

**B1** (høg, rekna). Val (a) profil er for sterkt. 94 % lysnytte, 90 lm for 350 lx og 13,5 timar er rekna utan tapet i avbildande optikk, og ved jamnheit 0,30. Formromkartet sjølv set S4 til 30–60 % verknadsgrad. Føremonen over retta og vend kan forsvinne.

- Prov: LESE: konsept/00-formromkart.md l. 118 («Sviktrom: 30–60 % verknadsgrad») og research/13 l. 199 (η 0,3–0,6). REKNA: 90 lm ut ved η 0,3 / 0,45 / 0,6 av kjeldelyset (100 lm/W) gjev 5,0 / 7,5 / 10,1 timar per celle, ikkje 13,5. Rutene i feltet går frå 461 til 3698 lx (8,0 gonger; hjørna 11,8 gonger etter h/r³, avstand 415 til 945 mm). Jamnar ein ut med gråtone i maska til jamnheit 0,4 / 0,5 / 0,6, er 74 / 59 / 49 % av lyset att, og lm for 350 lx blir 121 / 152 / 182. Retta treng 181 lm ved jamnheit 0,39.
- Konsekvens: Legg til ein kolonne «verknadsgrad i optikken» per lysgrep (profil 0,3–0,6, dei andre med sitt eige spenn), og rekn timar som spenn. Vis profilen òg ved same jamnheit som retta (om lag 120 lm ved 0,39). Skriv i val (a) at 13,5 timar er øvre grense utan optikktap.

**B2** (høg, rekna). Val (b): «lågast mot auget av alle (193 cd/m², 87 ved 350 lx)» kviler heilt på to innstillingar, ikkje på prismearka: sprut 3 % og hard avskjerming ved 45°. Auget står 60,1° frå plateaksen, så hovudloba gjev null der. Prismeark åleine gjev ikkje ei slik avskjerming.

- Prov: REKNA: L mot auget = sprut·Φ/(π·A) = 0,03·400/(π·0,024) = 159 cd/m² (lik L_lampe i tal.csv). Same plate utan kutt: sigma 24° gjev 856 cd/m² og lysnytte 41 % (203 lm for 350 lx); sigma 30° gjev 2033 cd/m² og 32 %; sigma 35° gjev 2964 cd/m². Sprut 10 % gjev 531, 20 % gjev 1061 cd/m². Luminans rett fram er 18 400 cd/m² ved 400 lm, så «lågast av alle» krev at flata ved 60° held under 1 % av det. LESE: research/13 l. 323 og 646 (vinklane til prismearka er ukjende) og l. 347 (ANTAKING om lysare band ved svært skrå vinklar).
- Konsekvens: Modeller retta med målt vinkelfordeling frå arka (forsøk R i framlegga). Ta avskjerminga inn som eigen del: svart raster, 10 mm celler og 10 mm djupn gjev 45°, open del 89 %, og 15 % av ei sigma 24°-lobe ligg utanfor 45° og går tapt, i alt om lag 0,76. «Kan byggjast i dag» gjeld lysboksen, ikkje avskjerminga. Oppgje luminansen mot auget som spenn 159 til 2000 cd/m² til arka er målte.

**B3** (høg, rekna). Val (c) vend bruker tala frå det idealiserte strøket, medan motoren sin eigen ark-versjon (malen, lysgrep «vend») er klart dårlegare. Stemningstalet 648 cd/m² er snittet av ei jamt lys skive; lysaste del er over det doble.

- Prov: LESE: snapshot/reflektor/_mal/tal.md rad 6 mot snapshot/lysskisse/tal.md rad 4. REKNA (attkøyrt): ark-versjonen gjev 660 lx, lysnytte 39 %, 2,65 W for 350 lx, 5,7 timar og 974 cd/m² mot auget (517 ved 350 lx). Det idealiserte gjev 949 lx, 57 %, 8,2 timar og 494 cd/m². Stemning med matt side ved 1,25 W: lysaste flis 1380 cd/m², snitt 619, topp/snitt 2,23 (reflektoren.md l. 38 har same forhold: 376 og 820). Lysaste flis held 500 cd/m² først under 45 lm frå kjelda (0,45 W), ikkje «under 77 lm». Ein topphatt på ±14° gjev same topp (1390).
- Konsekvens: Byt tala i val (c) til ark-versjonen, eller vis begge med forklaring. Rett «held 500 først under 77 lm» til om lag 45 lm frå kjelda for lysaste del. Skal mattsida bli jamn, må kjeldestrålen fylle heile skiva (±19° frå 365 mm), og då aukar spillet forbi skiva.

**B4** (middels, rekna). Reflektansmodellen (rd, rs, sigma) har rimeleg form, men standardverdiane er ikkje knytte til materiala han har, og resultata er følsame. SATIN (sum 0,80) ligg over spennet research/13 gjev for matt aluminium, og MATT 0,85 er lakk, ikkje papp.

- Prov: LESE: research/13 l. 571 (kvitt papir 70–80 %, matt aluminium 55–75 %), l. 313 (speglande reflektorfilm over 98 %), l. 89 (materialet i fresnelplata ukjent). REKNA, vend arbeid 5 W: sigma 5 / 10 / 15 / 20° gjev 781 / 660 / 521 / 406 lx, 6,7 / 5,7 / 4,5 / 3,5 timar, og mot auget 974 / 974 / 1715 / 4554 cd/m². rd 0,25 og rs 0,45 (sum 0,70) gjev 492 lx og 1624 cd/m². Papp med rd 0,75 i staden for 0,85 gjev 177 mot 200 lx og 1218 mot 1380 cd/m². BLANK (rs 0,85) er ei øvre grense for fresnelplata; riller og eventuelt akryllag er ikkje med.
- Konsekvens: Køyr reflektorfamilien med band, ikkje punkt: SATIN med sigma 5–15° og sum 0,55–0,80, MATT 0,75 for papp, reflektorfilm som eigen flate (rs 0,95–0,98, sigma etter kor flatt filmen ligg). Lås verdiane med flekkprøva i framlegga. Aluminiumsfolie har valseriller, så loba er truleg avlang; merk valseretninga på modellen (TOLKA).

**B5** (høg, rekna). P1 til P4 kan ikkje felle det i modellen som ber konseptvalet. P2 og P3 er geometri, P4 er ei fotometrisk lov, og P1 blandar to tap som ikkje er i modellen. Antakingane som avgjer (sprut 2–3 %, avskjerming, sigma for satin, tap i optikken) blir ikkje prøvde. Fellegrensa 5 i P1 er for slepphendt.

- Prov: REKNA: P1 målt forhold = 19,8 · η_optikk / τ_papir, altså 7,4 til 29,7 for η 0,3–0,6 og τ 0,4–0,8; ei tjukk papirkule får profilen til å stå. Profilen er jamgod med retta i energi alt ved η = 90/181 = 0,50 og med vend ved 90/147 = 0,61, medan fellegrensa 5 svarar til η/τ = 0,25. P2: same jamnheit for alle lyktestrålar (0,15–0,18 og 0,48–0,49). P3: skugge frå ein tett skjerm, 2 av 24 ruter. P4: L = Φ/(4π²r²) kan berre svikte gjennom transmisjonen i papiret; avstand og flekkstorleik på veggen er ikkje oppgjevne, og 225 cd/m² er toppen i ein skeiv flekk (snittet for 100 lm på Ø 60 cm er 81 cd/m²).
- Konsekvens: Behald P2 og P3 som kontroll av måleoppsettet og av skjermgeometrien hans, ikkje som modellprøver. Byt P1 og P4 mot forsøka i framlegga: lux per lumen frå same lykt for kvar rigg, vinkelfordelinga til arka, flekkbreidda til satinflata og luminansforholdet mellom lysande flate og kvitt ark.

**B6** (middels, rekna). Måleprotokollen held ikkje med telefonen slik han står. Kulearmen i P1 hamnar i botnen av måleområdet, jamnheit blir målt ved svært skrått lys, og P4 ber om eit forhold lese ut av eit bilete. Éin telefon kan heller ikkje vere lykt, luxmålar og kamera samstundes.

- Prov: REKNA: kula gjev 0,197 lx per lumen; ei lykt på 40–100 lm (ANTAKING, research/13 l. 372: ukjent) gjennom papir med τ 0,5 gjev 4–10 lx på feltet. LESE: research/13 l. 529: éin app viste 180 % for mykje ved 10 lx og 50 % for lite ved 10 000 lx. REKNA: det svarar til avlesing ∝ E^0,75, så eit sant forhold på 20 blir lese som 9,5 og 10 som 5,6. Innfallsvinklane i rutene er 49–80° med lykta i 13 cm og 18–51° i 60 cm; research/13 l. 535 krev sensoren vinkelrett på lyset. P4: research/13 l. 563 (pikselverdiar er ikkje lineære); med gamma 2,2 blir luminansforhold 3 til pikselforhold 1,65. Sprut 2 % gjev 0,35 lx ved auget frå ei lykt på 50 lm, under det telefonen løyser opp.
- Konsekvens: Skriv inn i «På bordet»: (1) linearitetsprøve først, (2) telefonen vend mot lykta i kvart punkt og lux gonga med cos (h/r), eller fotografer eit kvitt ark på feltet, (3) luminansforhold med lukkartid, ikkje pikselverdi, (4) ingen måling under 10 lx, bruk 806 lm-pæra der lykta er for svak, (5) referansemåling av lykta før og etter, fordi telefonlykter dimmar når dei blir varme (TOLKA), (6) to einingar: éi lykt og éin målar.

**B7** (middels, rekna). Profilen manglar meir enn ei linse, og linsa trengst for lysmengda, ikkje for skarpleiken. Utan kondensor fangar ei enkel linse lite, og utan optikk går berre ein åttedel av lyset inn i feltet. Brennvidda bør reknast frå kastet i motoren (634 mm), ikkje 45 cm.

- Prov: REKNA: frå ei diffus maske fangar ei linse med f 50 mm og Ø 25 / 40 mm 5,0 / 12,0 %, og f 60 mm med Ø 60 mm 17,0 % (sin² av halvvinkelen). Ein lambertsk diode retta mot feltmidten sender 12,2 % inn i feltet (0,385 sr / π). Kast 634 mm gjev f = 57,6 mm (maske 60 mm) til 90,6 mm (maske 100 mm). Feltet ligg 55° skeivt; maska må vere eit trapes (vinkelhøgd 47° ved nær kant, 25° ved fjern) og tiltast 7–14° for full skarpleik. Ei maske 65 mm framfor ei kjelde på 3 mm gjev alt 26 mm halvskugge, mot 53 mm i motoren. SØKJETREFF, ikkje opna: Clas Ohlson lommelupe 3× og 6×, 99,90 kr, ikkje på lager (https://www.clasohlson.com/no/Forstorrelsesglass/p/34-7931); 6× svarar til f om lag 42–50 mm, diameter ukjend.
- Konsekvens: Skissemodellen til 18.11 bør vere skuggemaske utan linse: 0 kr, same bilete på bordet, og talet å måle er lux per lumen. Skriv i val (a) at produktet treng kondensor, maske og linse (f 58–91 mm, Ø minst 40 mm) og 100–150 mm djupn, og at verknadsgraden er ukjend. Lupa er ikkje verd kjøpet før kondensoren er løyst.

**B8** (låg, rekna). Retta er modellert med to ulike optikkar for «same plate»: retta stråle i arbeid og lambertsk flate i stemning. Vender han same prismeside mot veggen 20 cm unna, blir veggflekken om lag 2,7 gonger så lys som oppgjeve.

- Prov: LESE: lysskisse.py l. 802–809 (straale i 'a', flate i 's'). REKNA: same stråle (sigma 24°, sprut 3 %) mot veggen gjev 410 cd/m² med kutt 45 og 365 utan, mot 145 cd/m² lambertsk. Veggsona får 103 lx mot 84.
- Konsekvens: Avgjer kva side som lyser i stemning. Same side: skriv 365–410 cd/m² (held 500 med 18–27 % margin). To sider (prisme fram, diffus bak): ta bakveggen i lysboksen med i byggjelista. Rekkjefølgja i stemning blir då profil 225, retta 365–410, vend 648 snitt og 1380 topp.

**B9** (middels, rekna). Reflektorfamilien manglar tryggleiksreglar for det han no skal bøye og klippe. Eit blankt, hòlt ark samlar sollys på same måte som fresnelplata, folie leier straum, og klipte kantar i tynn plate er skarpe. Ingen av delane står i API.md eller malen.

- Prov: REKNA: ark 25 × 25 cm med radius 0,6 m (boy(1/0.6) i malen) har brennline 30 cm framfor seg. I full sol (1000 W/m²) treffer 53 W ei line på 1–3 cm: 7 til 21 soler (7–21 kW/m²). Same ark med satin (sigma 10°) spreier lina til om lag 12 cm: 1,3 soler. Ei blank, dobbeltkrum skål Ø 240 mm med f 260 mm ville gje om lag 66 soler. Fresnelplata: 81 W i ein flekk (research/13 l. 129). Varme: 65 cm² kjøleflate per watt (research/05 punkt 7) gjev 195 cm² for 3 W og 325 cm² for 5 W; PLA mjuknar ved 55 °C (research/13 l. 115). LESE: kravspesifikasjonen har T8 «trygg å handtere» som skal-krav.
- Konsekvens: Legg til i API.md og malen: (1) hol form med BLANK eller reflektorfilm skal ikkje stå eller lagrast i sol; satin med sigma frå om lag 5° er trygt, og dette er òg ein produktregel for Northern; (2) fresnelplata skal maskerast med svart papp, ikkje klippast; (3) folie og metall skal ikkje røre opne leiarar eller batteripolar, teip kantane; (4) klipte kantar i plate skal avgradast eller faldast, og slissa ark treng ei minste godstjukn; (5) ingen diode over om lag 3 W i prenta PLA utan metall; (6) ikkje sjå inn i biletpunktet til fresnelplata (74 cm framfor plata med lykta 25 cm unna).

**B10** (middels, rekna). Kjelda som ark-modellen føreset (sigma 10° frå Ø 40 mm, 100 lm/W) finst ikkje i byggjesettet med nok lys til å måle. Pappblenda frå reflektoren.md slepper gjennom for lite til at telefonen kan måle feltet.

- Prov: LESE: reflektoren.md l. 85 (hol Ø 30 mm 60 mm over lykta, ±14°). REKNA: ±14° er sin²14° = 5,9 % av ein lambertsk diode; ei lykt på 50 lm (ANTAKING) gjev då 3–10 lm på arket. Med 0,35 lm på feltet per lumen på arket (660 lx · 0,24 m² / 449 lm) blir det 4–15 lx med satin og under 5 lx med matt. Ei trakt med blank innside held etenduen: utgang Ø = 5 mm / sin 14° = 21 mm for ei kjelde på 5 mm, lengd om lag 51 mm. LESE: research/13 l. 379: lommelykt med fokus, 200 lm, 149,90 kr.
- Konsekvens: Gje reflektormodellane ei verkeleg kjelde: prent ei trakt (Ø 5 til Ø 21 mm, 51 mm lang) og fôr ho med reflektorfilm eller folie, eller kjøp fokuslykta til 149,90 kr. Gjer materialprøva (flekkbreidd) på kort hald, der lyset held. Oppgje i malen kva kjelde tala føreset.

### Framlegg

- Forsøk M, måleoppsettet (30 min, 0 kr), før alt anna. (1) Linearitet: lykta rett mot sensoren på 0,25, 0,5, 1,0 og 2,0 m i mørkt rom. Føreseiing: 16 : 4 : 1 : 0,25. Fellegrense: avvik over 20 % i området du skal måle i; lag då korreksjonskurve eller lån luxmeter. (2) 806 lm-pæra naken på plassen til bordlykta (25 cm over bordet, 47 cm til høgre for feltmidten). Føreseiing: 130 lx direkte, 159 lx med refleksane i modellrommet, snitt over feltet. Fellegrense: utanfor 100–200 lx etter kalibrering; då er oppstillinga eller målemåten feil, ikkje modellen. (3) Lykta i 60 cm: jamnheit 0,48–0,49 same kva lykt. Får du under 0,40, er det sensoren som les skrått lys feil.
- Forsøk R, retta flate (1–2 timar, 0 kr; 89 kr om du brukar 806 lm-pæra i boksen). Lysboks med opning 20 × 12 cm, diffusor og to kryssa prismeark. Mål lux 30 cm unna med telefonen alltid vend mot boksen, ved 0, 30, 45, 60 og 75° i to plan. Føreseiing frå motoren: 46 % ved 30°, om lag 9 % ved 45°, under 1 % ved 60°. Fellegrenser ved 60°: over 1,1 % av verdien rett fram, og retta er ikkje lenger lågast mot auget; over 9 %, og F5 (1500 cd/m²) ryk ved 350 lx. Gjer det om att med prenta svart raster (10 mm celler, 10 mm djupt). Føreseiing: under 1 % ved 60° og om lag 0,76 av lyset att rett fram. Med telefonlykta kan du berre prøve 9 %-grensa (28 av 307 lx); 1,1 % krev pæra i boksen (50 av 4950 lx).
- Forsøk S, satinflata (30 min, 0 kr). Folie med matt side ut, limt plant på papp, og kvitt papir ved sida av. Lykta 20–30 cm unna i 45°, kvit vegg 0,5 m unna i spegelretninga. Finn breidda der flekken er halvparten så lys (før telefonen over flekken). Føreseiing for sigma 10°: 206 mm (103 mm for 5°, 308 mm for 15°). Fellegrense: over 310 mm; då er lysnytta 30 % eller lågare, brukstida 4,5 timar eller kortare og luminansen mot auget over 1500 cd/m² ved 5 W. Mål same breidd for reflektorfilmen og legg tala inn som eigne flater i motoren.
- Forsøk L, lux per lumen for tre riggar med same lykt (2–3 timar, 0 kr). Mål først lumen frå lykta (research/13 kap. 4). Profil: skuggemaske 65 mm framfor lykta i 36 cm høgd, 50 cm til høgre. Retta: lysboksen 40 cm over bordet. Vend: skive Ø 250 mm med folie, kjelde gjennom prenta trakt. Føreseiing før optikktap: 3,9, 1,9 og 1,3 lx per kjeldelumen. Med venta tap (skuggemaske 12–35 %, arkstabel 50–70 %) hamnar alle tre truleg mellom 0,5 og 1,5. Fellegrense for påstanden om at profilen er best på energi: profilriggen gjev under 1,5 gonger retta-riggen. Mål i same omgang kantbreidda på profilen (føreseiing om lag 46 mm på bordet midt i feltet for ei kjelde på 3 mm) og største mot minste rute (føreseiing 8 gonger).
- Forsøk A, lysande flate mot kvitt ark, frå stolen (30 min, 0 kr). Kvitt ark i feltet. Fotografer med låst ISO og kvitbalanse og finn lukkartida som gjev same gråtone på arket og på den lysande flata; forholdet mellom tidene er luminansforholdet. Føreseiing (uavhengig av lumen): profilopninga 2,3 gonger arket, retta-plata 0,8 gonger (mørkare enn arket ho lyser på), vend-skiva 2,0 gonger. Fellegrenser: over 17 gonger bryt F5 ved 350 lx; retta over 2 gonger er ikkje lenger lågast. Dette er den einaste av prøvene som treffer sprutantakinga direkte.
- Byggjeliste per kandidat til 18.11. Profil: telefonlykt, prenta røyr med trapesmaske 65–100 mm framfor, svart innside; 0 kr; ingen linse. Retta: pappboks fôra med reflektorark, diffusor, to kryssa prismeark, prenta ramme, prenta raster og eit ledd som vender plata mot veggen; 0 kr, eller 89 kr for to 806 lm-pærer eller 159 kr for USB-lista. Vend og reflektor som form: papp med folie eller reflektorfilm, prenta ribber som held bøyen (radius 0,6 m gjev 13 mm pil over 250 mm), prenta trakt til kjelda; 0 kr, eller 149,90 kr for fokuslykta. Fresnelplata og projeksjonslinsa er gode til forsøk, ikkje til ein av dei tre modellane: plata er 285 mm og linsa krev maske på 490 mm.
- Endringar i motoren og tekstane: (1) kolonne for verknadsgrad i optikken og timar som spenn; (2) profilen òg ved jamnheit 0,4 og 0,6; (3) retta med målt vinkelfordeling og raster som eigen parameter, og same optikk i stemning; (4) val (c) med tala frå ark-versjonen og lysaste del i stemning; (5) SATIN og MATT som band til dei er målte; (6) tryggleiksreglane i B9 inn i API.md og malen; (7) «På bordet» i 00-lysskisse.md med målereglane i B6.

### Spørsmål

- Har brukaren to einingar (ein telefon som lykt og ein som målar), eller tilgang til luxmeter frå skulen? Protokollen i «På bordet» føreset det utan å seie det.
- Kva er reflektorarket frå LCD-skjermane: kvitt og matt, eller speglande film? Det avgjer om det skal inn som MATT (truleg rd over 0,9) eller som blank flate med rs opp mot 0,98.
- Skal same side av retta-plata lyse i arbeid og i stemning? Svaret avgjer om stemningstalet er 145 eller 365–410 cd/m², og om lysboksen treng ei diffus bakside.
- Kvifor har vend i brettet (idealisert strøk, sprut 19 %, sigma 12°) betre tal enn vend i malen (ark med SATIN)? Kva for ein meiner du gjeld for val (c)?
- Kva verknadsgrad reknar du for arkstabelen i retta (diffusor og to prismeark med resirkulering) og for opalen i bordlykta? 80 lm/W ut er brukt likt for alle.
- Er sprut 2 % for profilen meint for ei linse eller for ei rein maske? Ei fresnellinse eller ei ubehandla lupe spreier truleg meir (TOLKA), og 5 % gjev alt 2252 cd/m² ved 400 lm.
- Er avskjerminga ved 45° i g_retta meint som ein fysisk del (raster eller nedsenka plate)? Ho står ikkje i omtalen av val (b).
