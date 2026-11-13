# Reflektoren: to konseptfrø

Dato: 12.11.2026. Linse: lampa ber sin eigen «vegg». Ei skjult kjelde lyser på ein reflektor som høyrer til lampa, og reflektoren er det einaste som lyser. Begge frøa byggjer på `grunnlag/00-ramme.md`, `konsept/00-formromkart.md` og `research/03`, `05`, `07` og `13`.

## Felles føresetnader og reknemodell

- **Oppstilling (ANTAKING):** auge 47 cm over bordet. Arbeidsfelt 0,6 × 0,4 m framfor brukaren. Lampa står ved sida av skjermen, 47 cm vassrett frå feltmidten og 67 cm frå auget, 39° til sida for kameraaksen (cos 39° = 0,78).
- **Kjelde (ANTAKING):** 100 lm/W for lys ut av kjeldeoptikken (LED 115 til 170 lm/W × drivar 0,9 × optikk 0,85 til 0,9, `05`). Når 78 % av kjeldelyset forlèt reflektoren, svarar det til om lag 80 lm/W «lys ut», som i ramma. Følsemd: 75 og 140 lm/W ved kjelda.
- **Celle:** 0,85 × 17,8 Wh = 15,1 Wh brukbar (`05`).
- **Matt flate:** ρ = 0,85, lambertsk. **Satinert flate (ANTAKING, ikkje målt):** 0,65 av lyset i ei lobe rundt spegelretninga med σ = 8 til 14°, og 0,15 diffust.
- **Modell:** punktkjelde med intensitet I(θ) gjev E = I · cos i / d² på kvart skiveelement. Luminansen frå elementet er L = E · (ρ_d / π + ρ_s · g(δ) / cos θ_ut), der g(δ) = exp(−δ² / 2σ²) / (2πσ²) og δ er vinkelen frå spegelretninga. Lux i eit punkt er Σ L · cos θ_ut · cos θ_inn · dA / r². Rekna med skript (mellombels: `C:/Users/Iver/AppData/Local/Temp/claude/8532dfb00720264d/2c1f63c0-844c-4780-bd7e-44e5353e679d/scratchpad/konsept/reflektor_modell.py`). Tal merkte (modell) kjem derifrå og er ikkje målte.

**Funn som styrer begge frøa.** Ei matt skive ved sida av feltet legg berre 13 % av lyset sitt på feltet (modell). 120 lm på feltet ville krevje om lag 920 lm ut, og V1 tillèt 231 lm frå 491 cm² ved 1500 cd/m². Arbeidslyset må difor kome frå ei retta flate, medan glød og ansiktslys treng ei matt flate eller ei flate som samlar lyset mot ansiktet. Dei to frøa løyser dette på kvar sin måte.

---

## Frø 1: Vend

**Éi setning.** Ei lykt i foten lyser opp på ei skive med ei matt og ei satinert side, og sida som vender ned, avgjer om lampa gløder, lyser på ansiktet eller legg 500 lx på arbeidsfeltet.

**Steget.** Regel: éin reflektor med éin karakter → éi skive med to karakterar (matt og retta) som blir vend framfor ei fast, samla kjelde i foten. Næraste busette nabo er Verpan Reflect: pære i røyrfoten og fast, kvit skråskive.

**Konflikt og kurve.**
- K2 for arbeidslyset: satinsida bryt føresetnaden i V1 om at flata lyser likt i alle retningar. 226 til 273 lm ut gjev 280 til 370 cd/m² mot auget (modell). Ei lambertsk flate på same areal ville hatt 1465 til 1770 cd/m².
- K3: lysnytta er 0,44 til 0,53 av lys ut (modell), mot 0,13 for mattsida og 0,20 til 0,28 for ei lampe som lyser rundt seg (kartet, K1). Det gjev 500 lx i 4,3 til 5,2 timar på éi celle (O1).
- K1: lysfordelinga skiftar med sida, ikkje berre nivået.
- Ikkje flytta: V2. Ansiktslyset følgjer arealet og vinkelen.

**Struktur.**
- Lyskjelde: éin dim-to-warm-modul (3000 til 1800 K, Ra minst 90) i ein brønn framme i foten, 85 mm framfor stamma. Linsa ligg 36 mm under kanten av ein brønn på Ø 44 mm.
- Optikk: samlelinse som gjev ein stråle på ±14°, og skiva 365 mm over. Mattsida er lambertsk, satinsida retta.
- Drivar, ladekrets, 21700-celle, USB-C og ballast: i foten. Straumregulert dimming.
- Stamme og gaffel: massive, utan leidning. Ingen elektriske delar over foten.
- Betjening: skiva blir vend i gaffelen (to hakk), nivået blir stilt med ein messingknott på foten.

**Lys per modus (reknestykke).**
- Areal: π × 0,125² = 0,0491 m². V1: Φ_maks = π · A · L = 77 lm ved 500 cd/m², 154 lm ved 1000 og 231 lm ved 1500.
- Stemning, matt side: 70 lm frå kjelda × 0,98 treff × 0,85 = 58 lm ut. L = 58 / (π × 0,0491) = 376 cd/m² i snitt, 820 i den lysaste delen (modell). 16 lx ved auget (modell). 0,7 W, 15,1 / 0,7 = 21,6 timar.
- Stemning, satinside: 120 lm frå kjelda gjev 94 lm ut, ei lysøy med 190 lx i snitt på feltet og 116 cd/m² mot auget (modell). 1,2 W, 12,6 timar.
- Arbeid, satinside, 30° vipp: 250 lm frå kjelda gjev 195 lm ut og 87 til 105 lm på feltet (σ 12° til 8°, modell). 120 lm på feltet krev 120 / 0,53 = 226 til 120 / 0,44 = 273 lm ut, altså 290 til 350 lm frå kjelda og 2,9 til 3,5 W. Brukstid 15,1 / 2,9 = 5,2 til 15,1 / 3,5 = 4,3 timar. Ved 75 lm/W: 3,2 til 3,9 timar. Ved 140 lm/W: 6,0 til 7,3 timar.
- Luminans mot auget i arbeid: diffusdelen gjev L = ρ_d · E / π = 0,15 × (0,98 × 320 / 0,0491) / π = 305 cd/m². Modellen gjev 280 til 370 i snitt og 600 til 725 i den lysaste delen.
- Jamnheit på feltet: min/snitt 0,34 til 0,38 på rutenett med 10 cm, opp til 0,5 med lampa rett ved sida av feltet (modell). Referansen er 0,6.
- Møte, matt side, 55° vipp mot auget: Ω = A · cos 40° / d² = 0,0491 × 0,766 / 0,671² = 0,083 sr. E = L · Ω = 83 lx ved 1000 cd/m² og 125 lx ved 1500, vend mot lampa. Mot kameraet (× 0,78): 64 og 96 lx. Lys ut ved 1000 cd/m² er 154 lm, kjelda 154 / (0,90 × 0,85) = 201 lm, 2,0 W og 7,5 timar. På 60 cm blir tala 1,25 gonger høgare.
- Skiva er ujamt lys i møtestillinga: nedre kant er 2,2 gonger snittet (modell). Skal den lysaste delen halde 1500 cd/m², blir snittet 685 og ansiktet får 57 lx (44 lx mot kameraet).
- På leidning: tak 4,5 W, om lag 650 til 780 lx på feltet. USB-C på 7,5 W dekkjer lys og lading.
- Varme: foten har 196 cm² mantel og 98 cm² topp, i alt om lag 290 cm². 3,5 W treng 140 til 175 cm² og 4,5 W 180 til 225 cm² (V5).

**Overgang.**
- Stemning til arbeid med satinsida ned: éin vri på messingknotten. Lysøya går frå om lag 120 lm og 2000 K til 290 til 350 lm og 3000 K. Eitt grep, 1 til 2 sekund.
- Frå glød på mattsida til arbeid: vend skiva til hakket for arbeid og vri opp. To grep, føreseiing under 4 sekund.
- Arbeid til møte: vend skiva til hakket for møte, drei foten mot deg og vri litt ned.

**Form.**
- Tre primærformer: sylinder, linje og skive.
- Fot Ø 120 × 52 mm. Stamme Ø 8 mm, 50 mm bak fotsenteret. Gaffel i Ø 6 mm som held skiva i to akseltappar.
- Skive Ø 250 × 1,5 mm, senter 410 mm over bordet. Samla høgd 47 cm i arbeidsstilling og 52 cm i møtestilling.
- Masse om lag 1,15 kg: fot 850 g (skal 159, lok 124, ballast 357, celle 70, elektronikk og lysmodul 140), stamme og gaffel 81 g, skive 219 g. Tyngdepunkt 114 mm over bordet. Veltevinkel 22° bakover og 33° framover.

**Material og prosess.**
- Fot: aluminium, metalltrykt eller dreia skal, pulverlakkert. Botnlok og ballast: laserskoren stålplate.
- Stamme og gaffel: aluminiumsstong, bøygd og pulverlakkert.
- Skive: aluminiumsplate, laserskoren, perleblåst og anodisert på begge sider, den eine sida pulverlakkert matt.
- Lysmodul: LED-kort i dreia aluminiumskopp med hyllevarelinse og pluggkontakt.
- Dimmeknott: dreia messing, ubehandla. Elektronikkberar: éin plasttype, printa PA12 i første seriar.
- Einaste delspesifikke verktøy er ei trykkform til foten. Ingen lim.

**Reparasjon.**
- Batteri: botnlok med éin kvartvendingslås for mynt. Cella sit i haldar med fjørkontaktar. Eitt festemiddel, eitt verktøy, under eitt minutt.
- Lysmodul: gjengeringen rundt brønnen blir løyst med same mynt, modulen løfta ut og pluggen trekt. Éin ring, éin plugg, under to minutt.
- Drivarkort: to skruar av same type og tre pluggar.
- Lampa lyser fullt på USB-C utan celle (straumveg i ladekretsen, `05`).

**Northern.**
- Haldne: H1, H3, H4 (éin kontrast: satinsida), H5 (messingknott), H6 (vende).
- Broten: H2. Linja ber ei flate på Ø 250 mm, ikkje eit kompakt volum.
- Fem av seks. Nær attkjenning i primitiv, farge og messing. Endringa ligg på aksar utan variasjon i sortimentet: fargetemperatur, arbeidslys på batteri, lysformat og kamera. Slektningar: Ombre og Balancer mini.

**Naboar.**
- Verpan Reflect (Verner Panton): pære i sylinderfoten lyser opp på kvit, skrå skive. H 60 cm, skive Ø 30 cm, fot Ø 8 cm, 4,2 kg, E14 maks 10 W, kabel, ikkje dimbar (lese hos forhandlar 12.11.2026). Skilnad: skiva er fast og har éin karakter, ingen retta arbeidsstråle, ikkje portabel.
- Flos Taccia: kjelde i sokkelen og kvit reflektor på toppen, 16 W og om lag 1290 lm i liten utgåve (søkjetreff). Northern Ombre (`01`). Marset Ginger 20 M og Foscarini Chapeaux M (kartet).
- Ikkje funne: bordlampe med vendbar skive med matt og retta side. To søk, ikkje patentbasar.

**Skissemodell (under éin dag).**
- Volum: printa fot Ø 120 × 52 mm med stålballast, rundstokk Ø 8 mm, printa gaffel med friksjon, skive Ø 250 mm i papp med kvitt papir på den eine sida og aluminiumsfolie med den matte sida ut på den andre.
- Lys: telefonlykta i foten under ei pappblende med hol på Ø 30 mm 60 mm over lykta (±14°). Mål lysstraumen frå lykta først (`13` kap. 4).
- Alternativ satinflate: frontflatespegelen med eitt diffusorark frå LCD-en.

**Prøve.**
- Føreseiing 1: feltet får minst 2,9 gonger så mange lux med satinsida som med mattsida ved same lys og vipp (modell 3,4 til 4,0).
- Føreseiing 2: skiva er høgst 0,3 gonger så lys sett frå auget med satinsida (foto med låst eksponering, modell 0,19).
- Føreseiing 3: 1,4 til 1,7 lx i snitt på feltet per lumen frå kjelda, og 0,41 lx på ansiktet per lumen med mattsida i møtestilling på 67 cm.
- Føreseiing 4: min/snitt på feltet 0,35 til 0,5.
- Prøve: lux i 24 punkt på feltet, lux loddrett ved auget, foto frå stolen, tid og tal grep for ein som ikkje har sett lampa.
- Feller konseptet: forholdet i 1 under 2,9 (då held ikkje 500 lx i 4 timar på éi celle), eller forholdet i 2 over 0,5 (då flyttar ikkje satinsida K2).

**Sviktrom.**
- Jamnheit 0,34 til 0,5 mot referansen 0,6.
- Kompakt: skive Ø 250 mm og høgd 47 til 52 cm ligg utanfor konvolutten til bordlykta (Ø 16 × 27,5 cm). Fotavtrykket er Ø 120 mm.
- Ansiktslys i nedre del av målet: 57 lx når den lysaste delen held 1500 cd/m², og lyset kjem 5° under augehøgd.
- Skiva dekkjer 0,08 sr og erstattar ikkje ein lys vegg bak skjermen.
- Risiko 1: spreiinga og diffusdelen til satinflata er antakingar.
- Risiko 2: open stråle mellom fot og skive. Hender og gjenstandar skuggar, og den som bøyer seg over foten, ser inn i optikken. Vurdering etter EN 62471 er ikkje gjord.
- Risiko 3: satinsida vippa over om lag 36° sender strålen mot auga, så hakket må stoppe ho. Ei blank bordflate speglar skiva (om lag 7000 cd/m² sett frå feltet, overslag).

---

## Frø 2: Perle

**Éi setning.** Lyskjelda er ei perle som blir skoven langs to skinner under ein satinert holspegel: nær spegelen spreier han lyset til arbeidsfeltet, nede ved foten samlar han det mot ansiktet.

**Steget.** Regel: fast kjelde under diffus skjerm → rørleg kjelde under éin satinert holspegel, der kjelda innanfor brennvidda gjev spreidd lys og utanfor brennvidda samla lys. Stamma er leiaren. Næraste busette naboar er Muuto Set (skjermhøgda over ei oppoverretta kjelde blir stilt på gjenger) og Verpan Reflect.

**Konflikt og kurve.**
- K3 for møtet: spegelen avbildar kjelda mot ansiktet, så heile skiva lyser jamt sett frå ansiktet og lite elles. 0,78 lm frå kjelda per lux på ansiktet, mot 2,45 lm per lux for mattsida i frø 1 (modell).
- K2 og K3 for arbeid: som frø 1, med lysnytte 0,44 til 0,56 av lys ut.
- K1: kjeldeposisjonen skiftar mellom felt og ansikt.
- Ikkje flytta: V2 (69 lx ved 1000 cd/m²). Zoomen på bordet er eit kompromiss, sjå sviktrom.

**Struktur.**
- Lyskjelde: LED-modul i ei aluminiumsperle på Ø 56 × 42 mm. Dioden ligg 22 mm nede i ein kopp på Ø 26 mm og lyser opp i ei kjegle på ±30°.
- Optikk: éin metalltrykt holspegel, Ø 240 mm, krummingsradius 520 mm (brennvidd 260 mm, pilhøgd 120² / (2 × 520) = 13,8 mm), satinert. Hengsla på toppen av skinnene, med hakk på 24° og 45°.
- Skinner: to stenger i rustfritt stål, Ø 5 mm, 16 mm mellom sentera, 400 mm lange. Dei fører konstantstraum til perla (høgst 17 V likespenning og 1,2 A). Perla har fjørkontaktar og friksjonsklemme.
- Drivar, ladekrets, 21700-celle, USB-C og ballast: i foten. Ein mekanisk brytar i foten senkar straumområdet til ein femtedel når perla står i botn.
- Betjening: skyve perla, vippe skiva, messingring ved foten for nivå.

**Lys per modus (reknestykke).**
- Arbeid, perla 180 mm under skiva, 24° vipp: 250 lm frå perla gjev 93 % treff, 186 lm ut og 104, 93 eller 82 lm på feltet ved σ 10°, 12° og 14° (modell). 120 lm på feltet krev 288 til 366 lm frå perla, 2,9 til 3,7 W. Brukstid 15,1 / 2,9 = 5,2 til 15,1 / 3,7 = 4,1 timar.
- Luminans mot auget i arbeid: 285 til 470 cd/m² i snitt og 600 til 860 i den lysaste delen (modell).
- Jamnheit: min/snitt 0,34 til 0,40 (modell).
- Stemning: 80 lm frå perla gjev 59 lm ut, 124 lx i snitt på feltet og 83 cd/m² mot auget (modell). 0,8 W, 19 timar.
- Møte, perla 380 mm under skiva (ved foten), 45° vipp: Ω = 0,069 sr (modell). 60 lm frå perla gjev 28 % treff, 13 lm ut og 76 lx på ansiktet ved σ 12° (59 lx mot kameraet), med 1130 cd/m² i snitt og 1870 i den lysaste delen. Ved σ 14°: 58 lx, 870 og 1390 cd/m².
- Skalert til 1000 cd/m² i snitt: E = L · Ω = 1000 × 0,069 = 69 lx, med 53 til 69 lm frå perla. 0,5 til 0,7 W, 22 til 28 timar. Lyset som går forbi skiva (72 %), hamnar i taket.
- Hovudrørsle (modell): 80 % av lyset att 10 cm til sida, 41 til 49 % ved 20 cm.
- Varme: perla har 2 × π × 2,8² + π × 5,6 × 4,2 = 123 cm², som ber 2,5 til 3,1 W etter V5. 500 lx krev difor LED med minst 150 lm/W ved kjelda (2,1 til 2,7 W). Med 100 lm/W held perla 370 til 420 lx.

**Overgang.**
- Stemning til arbeid: éin vri på messingringen med perla i arbeidsposisjon. Eitt grep.
- Arbeid til møte: skyv perla ned til foten (brytaren senkar nivået) og vipp skiva til hakket på 45°. To grep, føreseiing under 5 sekund.
- Perla si høgd viser modusen: oppe er arbeid, nede er møte.

**Form.**
- Fire primærformer: sylinder, to linjer, perle og skive.
- Fot Ø 110 × 45 mm. Skinner frå fottoppen til hengsla 440 mm over bordet. Skive Ø 240 mm.
- Høgd 49 cm i arbeidsstilling og 53 cm i møtestilling.
- Masse om lag 1,2 kg: fot 700 g, skinner 123 g, perle 167 g, toppkloss og hengsle 40 g, skive 148 g. Tyngdepunkt om lag 146 mm. Veltevinkel om lag 21°.

**Material og prosess.**
- Fot: aluminium, metalltrykt eller dreia, pulverlakkert. Lok og ballast i laserskoren stålplate.
- Skinner: rustfrie stenger, kappa og gjenga i endane, ubehandla.
- Perle: dreia aluminium, anodisert, med isolerande hylse rundt den eine skinna.
- Skive: metalltrykt aluminium 1,2 mm, perleblåst og anodisert, utsida pulverlakkert.
- Toppkloss og hengsle: maskinert aluminium med isolerande hylser. Nivåring: dreia messing.
- Verktøy: trykkformer til skive og fot. Ingen lim.

**Reparasjon.**
- Batteri: som frø 1. Eitt festemiddel, mynt, under eitt minutt.
- Lysmodul: perla er modulen. Éin klemskrue blir løyst med mynt, og perla blir trekt av skinnene. Ingen plugg, glidekontaktane er kontakten. Under eitt minutt.
- Ingen leidning i stamma. Lampa lyser fullt på USB-C utan celle.

**Northern.**
- Haldne: H2 (tynne linjer ber hovudet), H3, H4 (kontrast: blanke skinner), H6 (skyve perla).
- Delvis: H5. Messing sit på nivåringen, men handa går òg til perla.
- Broten: H1, fire primærformer.
- Fire av seks. Lenger mot endring enn frø 1, og synleg leiar er nytt for Northern.

**Naboar.**
- Muuto Set (Jamie Wolfond): oppoverretta kjelde, aluminiumsskjerm som blir skrudd opp og ned på kroppen, 800 lm, 18 W, Ø 34 × 38 cm, kabel, LED ikkje utskiftbar (søkjetreff, ikkje stadfesta).
- Louis Poulsen Yuh: skjermen kan vippast, dreiast og skyvast på stamma (søkjetreff). Verpan Reflect (sjå frø 1). NOX (kartet).
- Frå minnet, ikkje stadfesta: Artemide Tizio leier straumen gjennom armane, og Flos Parentesi lèt lampa gli på ein wire.
- Ikkje funne: bordlampe der kjelda blir skoven under ein spegel som samlar lyset mot ansiktet.

**Skissemodell (under éin dag).**
- Volum: printa fot og perle, to stålstenger eller grillspyd, printa toppkloss, skive i papp.
- Lys: fresnelplata (brennvidd 187 mm) maskert til Ø 240 mm med svart papp og med eitt diffusorark frå LCD-en oppå. Plata på projektorstolpen 44 cm over bordet. Telefonlykta med pappblende (±30°) på ein kloss som kan skyvast under plata.
- Brennvidda er 187 mm, ikkje 260. Posisjonane blir om lag 130 mm (arbeid) og 275 mm (møte), og må finnast ved prøving. Plata skal aldri stå i sollys (`13`).

**Prøve.**
- Føreseiing 1: med kjelda langt unna og plata på 45° er heile opninga jamt lys sett frå ansiktet på 65 cm (lysaste del høgst 2 gonger snittet i foto med låst eksponering).
- Føreseiing 2: ansiktet får minst 5 gonger så mange lux som frå ei kvit pappskive i same stilling (modell 10 til 17).
- Føreseiing 3: 80 % av lyset er att 10 cm til sida og 41 til 49 % ved 20 cm.
- Føreseiing 4: lysflekken på bordet endrar seg under 30 % i diameter når kjelda blir flytta, med diffusorark. Utan ark endrar han seg mykje (`13`: 82 til 28,5 cm).
- Feller konseptet: forholdet i 2 under 3, under halvparten av lyset att ved 10 cm, eller lysaste del over 3 gonger snittet.

**Sviktrom.**
- Glød: skiva er 83 til 170 cd/m² sett frå rommet i stemning. Stemninga er ei lysøy på bordet, ikkje ein lysande lekam.
- Ansiktslyset er bunde til plassen: halvert ved 20 cm sideflytting.
- Zoomen er liten: flata over halv maks går frå Ø 46 cm til Ø 35 cm når perla går frå 120 til 300 mm under skiva (modell). Spreiinga som gjer skiva mild å sjå på (σ 12° er ±14 cm på 65 cm), viskar ut samlinga.
- Jamnheit og kompaktheit: som frø 1.
- Risiko 1: varme i perla.
- Risiko 2: glidekontakt mot opne skinner (kontaktmotstand, flimmer, slitasje). Drivaren må tole kortslutning mellom skinnene (ANTAKING), og krava til opne leiarar i EN 60598 er ikkje kontrollerte.
- Risiko 3: arbeidsnivå retta mot ansiktet gjev 358 lx og om lag 5300 cd/m² (modell).

---

## Forkasta undervegs

- **Sonedelt skive** (satinert midtsone på Ø 110 mm, kvit ring, kjelde som blir skoven): kvar sone får for lite areal. Midtsona gav 1060 til 1130 cd/m² i snitt og 2700 til 3600 i den lysaste delen mot auget i arbeid, og opptil 39 000 cd/m² når skiva blei vippa mot ansiktet (modell). To sider gjev heile arealet til kvar karakter.
- **Satinert skål med kjelda på aksen** (lommelyktprinsippet): ikkje modellert. I spreidd stilling viser skåla eit lite, uskarpt bilete av dioden, og ei kvit skål gjev ingen zoom.
- **Ståande plate med lyslist i foten:** den matte sona blir liggjande 15 til 27° under augehøgd, eller lampa blir over 50 cm høg.

## Kjelder for naboane

- Verpan Reflect, forhandlarside (lese 12.11.2026): https://www.lampmasters.co.uk/p/reflect-table-lamp-matt-white-verpan-10026777.html
- Muuto Set, faktaark og forhandlarar (søkjetreff): https://fr.smow.ch/pdf/muuto-set-table-lamp-factsheet.pdf og https://www.architonic.com/en/p/muuto-set-table-lamp-20766747
- Flos Taccia (søkjetreff): https://www.lights.co.uk/p/flos-taccia-small-led-table-lamp-3510366x.html
- Louis Poulsen Yuh (søkjetreff): https://www.nordenliving.com/yuh-table-lamp.html
