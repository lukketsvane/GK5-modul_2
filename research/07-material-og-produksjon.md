# 07 – Material og produksjonsmetodar

Research til konseptgjennomgangen 18. november. Rapporten gjev materialfagleg og produksjonsteknisk grunnlag for ei stemningsskapande og funksjonell lampe for Northern, i ein seriestorleik på nokre tusen einingar per år. Datainnsamling 12. november 2026.

Merking i teksten: **FAKTA** = påstand med kjelde rett etter. **TOLKING** = mi vurdering av fakta. **ANTAKING** = føresetnad utan kjelde, må kontrollerast. **Berekna** = eige reknestykke; føresetnadene står ved sida. «i.o.» = ikkje oppgjeve i kjelda.

Kjeldenøklar står i hakeparentes og er løyste opp under «Kjelder». Dei viktigaste: [F] = kursforelesinga i materialteknologi, [FS] og [FR] = dei to Flokk-forelesingane, [G] = GRIP-rettleiaren, [PolyCE] = EU-prosjektet sine retningsliner for resirkulering av EE-produkt, [N:namn] = produktsida `northern.no/products/namn`. Nøklar som startar med W er Wikipedia og er sekundærkjelder.

**Avgrensing.** Kvoten for nettsøk var brukt opp då denne økta starta. Alt nettinnhald er difor henta ved direkte oppslag på kjende adresser, ikkje ved søk. Følgjene er:

- Northern sine eigne produktsider er lesne direkte (33 lamper med spesifikasjonar) og er godt dekte.
- For metalltrykking, djuptrekking, pressstøyping, glasformer, tredreiing og keramikk fann eg inga leverandørkjelde med tal for toleransar og verktøykostnad. Der står rangering og «ukjent» i staden for tal.
- Transmisjonstal for opalglas, tekstil, papir og finer manglar.
- CO2-tal per kg er henta for aluminium, stål og rustfritt stål, ikkje for glas, PMMA, PC, tekstil og tre.
- Fleire nordiske leverandørar er ikkje verifiserte og er merkte slik.

Matrisa «material/prosess × del × berekraft × kostnad × Northern-preg» og dei tre materialpakkane står sist i kapittelet «Implikasjonar for designet».

---

## Kort oppsummering

1. **Northern sin palett er metall, munnblåse opalglas og messing.** Av 33 lampesider eg las, oppgjev 27 stål, 14 glas, 10 aluminium og minst 10 messing. Hardplast finst berre som akryl (4 lamper, i hovudsak som diffusor), i tillegg til silikon, polyresin og polyestertekstil. Konkurrentane i portabel-kategorien er i hovudsak sprøytestøypt PC, ABS og PP. Material er altså det tydelegaste skiljet Northern har.
2. **Ved nokre tusen einingar i året bør forma kunne lagast utan dyre verktøy.** Metalltrykking, platearbeid, røyr og profil, dreiing, glas blåse i form og PMMA frå plate har låg startkostnad. Sprøytestøyping er mogleg for éin til tre små delar med aluminiumsverktøy (3 000–5 000 USD per verktøy, 5 000–10 000 skot). Pressstøyping og djuptrekking krev herda stålverktøy og større volum.
3. **Diffusoren avgjer både lyset og merkevarekjensla.** Opalglas er Northern-signaturen, men er tungt, har ukjend transmisjon og varierer i tjukkleik. Opal PMMA er best dokumentert (72 % transmisjon ved 3 mm, garanti mot gulning i 30 år for klåre kvalitetar, opptil 90 % resirkulert råvare). PC toler mest varme, men gulnar i sollys og plasserer lampa i plastkategorien.
4. **Lågkarbon-metall er det største enkeltgrepet på materialsida.** Aluminium: 14,4 kg CO2e/kg i globalt snitt, 4,0 for Hydro REDUXA, 1,9 for Hydro CIRCAL. Stål: 2,34 kg CO2/kg via masomn, 0,69 via skrapbasert lysbogeomn. Rustfritt: 7 i globalt snitt, 1,6 hos Outokumpu, ned til 0,5 for Circle Green. I eit reknedøme med 0,25 kg aluminium og 0,83 kg stål fell materialutsleppet frå 5,5 til 1,0 kg CO2e.
5. **Overflata bør vere éi behandling per metall, og ingen på plast.** Pulverlakk, anodisering og PVD er dei aktuelle. Forkromming og annan galvanisk behandling bør unngåast, og lakkert plast øydelegg plastfraksjonen. Ubehandla messing og olja tre kan brukaren halde ved like sjølv.
6. **Samanføying: gjenger, bajonett og éin standard skrutype.** Lim, 2K-støyp, innstøypte metalldelar, nagling og pressa samband bør ut. Jern og ikkje-jern bør kunne falle frå kvarandre. Northern gjer alt noko av dette: Snowball Portable har gjenga glaskuppel, LED-modul med trykkontakt og utskiftbart batteri.
7. **Stabilitet kjem av fotradius delt på tyngdepunktshøgd, ikkje av vekt åleine.** Ei lykt på 1,07 kg med ei laus stålskive på 445 g i foten veltar først ved om lag 35° helling (berekna). Utan skiva veltar ho ved 23°. Stålskiva kostar 0,3–1,0 kg CO2 og hamnar i jernfraksjonen. Innstøypt ballast, sand og betong bør unngåast.
8. **Relevante leverandørmiljø finst i Noreg og Norden:** Hydro (pressverk på Magnor), Hadeland Glassverk (alle lamper i munnblåse glas frå eige verk), Plasto i Åndalsnes (sprøytestøyping, prosjekt med resirkulert plast), Innvik (Northern sin tekstilpartnar), Outokumpu og SSAB. New Comfort Products på Hemnesberget legg ned møbelproduksjonen hausten 2026. Det tyder på at norsk produksjon i resirkulert plast er sårbar (TOLKING, eitt døme).

---

## Funn

### 1. Ramma frå kurset: omgrep og tal

**FAKTA – stål mot aluminium** [F, slide 33]:

| Eigenskap | Stål | Aluminium |
|---|---|---|
| Tettleik | 7,8 kg/liter | 2,7 kg/liter |
| Stivleik (E) | 160–240 GPa | 69–71 GPa |
| Varmeleiing | 74 W/mK | 235 W/mK |
| Smeltetemperatur | ca. 1540 °C | ca. 660 °C |
| Korrosjon | korroderer lett | korroderer, men dannar vernande oksidlag |
| Resirkulering | over 85 % | over 60 %, berre 5 % av energien ved omsmelting |

**Berekna.** Aluminium leier varme 235 / 74 = 3,2 gonger betre enn stål og veg 2,7 / 7,8 = 35 % av stål per volum.

**TOLKING.** Tala gjev ei enkel arbeidsdeling i ei lampe: aluminium der varmen frå LED-en skal bort og vekta skal vere låg (skjerm, hovud), stål der lampa treng vekt og stivleik (fot, arm). Det er same deling Northern brukar i Birdy: skjerm i aluminium, kropp i stål [N:birdy-table-lamp].

**FAKTA – plast** [F]:
- Termoplast mjuknar ved varme, kan formast på mange måtar og kan i stor grad resirkulerast (slide 10). Herdeplast er «svært vrient å resirkulere» (slide 18).
- Resirkulering av plast er avhengig av at plasttypar ikkje blir blanda (slide 11). Forelesinga spør kva som skjer om det blir forbode å blande plasttypar i eitt produkt (slide 27).
- PP: 9–12 kr/kg, lett å resirkulere, toler UV dårleg, vanskeleg å lime (slide 13). ABS: 20–40 kr/kg, blank overflate og skarpe kantar, toler UV dårleg, skal ikkje i plastreturordninga (slide 15). PC: 42 kr/kg, 1,2 kg/liter, E = 2,6 GPa, svært slagfast, «blir gul i sollys» (slide 17). TPE bør resirkulerast for seg (slide 16).
- Bioplast er laga for kompostering, ikkje resirkulering, og er uheldig om han blir blanda med vanleg plast (slide 19).
- Sprøytestøyping: mest utbreidd, billeg i bruk, dyre verktøy og maskiner (slide 38). Verktøy har 6–16 vekers leveringstid (slide 39), blir laga i aluminium eller stål, og trykket er over 400 bar (slide 40). Prisen på verktøyet krev store seriar (slide 41). Tokomponentstøyp gjev fleire fargar eller plasttypar i same del (slide 43).
- Metallstøyping i modellskala: former i høgtemperatur-polyuretan eller silikon, med tinn (240 °C) eller vismut-tinn-legering (138–170 °C). Overgangar frå tjukt til tynt er problematiske, og underkutt er vanskelege (slide 45). Sandstøyping med eingongsformer gjev stor formfridom (slide 46).

**Berekna.** Ein PC-skjerm på 150 g kostar 0,15 kg × 42 kr/kg = 6,3 kr i råvare. Kiloprisen på plast betyr lite i ei lampe til 2 000–4 000 kr. Verktøy og overflate betyr meir (same konklusjon som i `research/05-teknologi-og-komponentar.md`, punkt 12).

**FAKTA – Flokk sine fem sirkulære designkriterium:** låg vekt, få komponentar, rett materialval, lang levetid, design for demontering [FS, s. 16–33]. Materialvalet er sortert slik [FS, s. 22]:
- «The Good»: resirkulert (post-consumer), fornybart, resirkulerbart.
- «The Bad», berre om det trengst: jomfruelege material, PUR-skum, komposittar og 2-komponent.
- «The Ugly», forbode: PVC, krom som overflatebehandling, lim (VOC), farlege kjemikaliar.

**FAKTA – GRIP-rettleiaren** [G]:
- For «aktive produkt», som brukar straum, er bruksfasen oftast mest miljøbelastande. Der produktet inneheld avgrensa ressursar som metall, er materialframstillinga ofte avgjerande: «Unngå derfor metaller i kortlivede produkter» (s. 12).
- Materialoptimering: lag produktet lett, bruk færre delar, bruk konstruksjonsteknikk for styrke og «festeanordninger i stedet for egenvekt for å gi stabilitet» (s. 35).
- Material bør ha om lag same levetid som produktet. Vurder overflatebehandling ut frå kor haldbart materialet er (s. 35).
- Energi til framstilling: rustfritt stål 50 MJ/kg jomfrueleg mot 10 MJ/kg attvunne; vanleg stål 30 mot 7 MJ/kg. «Økologisk ryggsekk»: stål 21, aluminium 85, resirkulert aluminium 3,5 kg råvare per kg (s. 39, med kjelde Dahlström mfl., IVF 2000).

**TOLKING.** Ei lampe i metall og glas er berre forsvarleg etter GRIP si tommelfingerregel dersom ho faktisk lever lenge. Det bind materialvalet til reparasjon: metallkroppen må overleve fleire batteri og minst éin LED-modul.

### 2. Kva Northern og samanliknbare merke brukar i dag

#### 2.1 Northern

**FAKTA.** Northern skriv om belysninga si at ho er «laget av solide materialer – skapt for generasjoner» [N1]. På «About»-sida står det at dei blandar «creativity with traditional craftsmanship, crafting things to last» [N7].

**FAKTA – utval av produktspesifikasjonar** (frå Northern sine eigne produktsider):

| Lampe | Skjerm / diffusor | Kropp / fot | Overflate og detaljar | Vekt | Kjelde |
|---|---|---|---|---|---|
| Snowball Portable bord (2025) | Munnblåse glas, opalkvit matt | Rustfritt stål | Gråbeige pulverlakk eller messingfarge med PVD; brytar i messing | 0,5 kg | [N:snowball-portable-table-lamp], [N3] |
| Snowball bord | Munnblåse opalglas | Stål og aluminium, eller messing | Stål, kvit, svart eller børsta messing | 0,9 kg | [N:snowball-table-lamp] |
| Birdy bord | Aluminium | Stål | Kvit, grå, svart; ledd i stål, messing eller svart | i.o. | [N:birdy-table-lamp] |
| Buddy bord | Stål | Stål | Fem fargar | 2,1 kg | [N:buddy-table-lamp] |
| Salto bord | Stål, diffusor i opal akryl | Stål | Svart eller beige; berøringsdimmar i messing | 2,5 kg | [N:salto-table-lamp], [N9] |
| Ombre bord | Stål | Stål | Matt svart eller beige pulverlakk | 1,8 kg | [N:ombre-table-lamp], [N9] |
| Archive bord | Stål | Rustfritt stål (børsta) eller lakkert stål | Matt svart eller blank mørkegrøn | 1,9 / 3,5 kg | [N:archive-table-lamp] |
| Tradition bord | Strikka polyestertekstil over stålramme | Stål | Gråbeige | i.o. | [N:tradition-table-lamp] |
| Kin bord | Glas, opalkvit matt | Dark Emperador-marmor, polert | – | 3,0 / 4,4 kg | [N:kin-table-lamp], [N9] |
| Balancer mini | Munnblåse glas (diffusor) | Stål | Svart, raud eller stål; dimmar i messing | 1,0 kg | [N:balancer-mini-lamp], [N9] |
| Hall vegg (merkt «New») | Glas, opalkvit matt | Aluminium, med «kompakt støpt arm» | Børsta aluminium eller svart | 0,8 kg | [N:hall-wall-lamp], [N9] |
| Acorn pendel | Aluminium med topp i bøk eller valnøtt | – | Måla kvit, grå eller svart | 2,3 kg | [N:acorn-pendant-lamp], [N9] |
| Oslo Wood golv | Farga tekstil («chain link fabric») | Stål | – | 3,5 kg | [N:oslo-wood] |
| Diva golv | Eikefiner på laminert kryssfiner (32 lamellar), indre skjerm i munnblåse glas | Stål | – | 7 kg | [N:diva-floor-lamp], [N9] |
| Me dim golv | Stål, diffusor i opal akryl | Stål og silikon | Pulverlakk; dimmar i messing | 11,3 kg | [N:me-dim-floor-lamp], [N9] |

**FAKTA – oppteljing.** Av dei 33 lampesidene med spesifikasjonar eg las, oppgjev 27 stål (inkludert rustfritt) i kropp eller skjerm, 14 glas i skjerm eller diffusor, 10 aluminium, minst 10 messing som material eller detalj, og 4 akryl. Éi lampe har marmorfot (Kin), éi har polyresin med glasfiber (Moo), og éi har tekstilskjerm over stålramme i tillegg til Oslo Wood (Tradition) [N:…, sjå lista under «Kjelder»].

**FAKTA – prosessord Northern sjølv brukar:** «munnblåst» glas, glas «etset» til matt overflate (Dahl), «pulverlakkert», «PVD-belagt», strikka polyester «strukket over en hvit metallramme» (Tradition), «laminert kryssfiner» (Diva), «polerte» marmor (Kin), «netting i rustfritt stål» (Heat), «perforert» metallskjerm (Glint), «støpt arm» (Hall) [N9]. Korleis metalldelane elles er forma (trykking, djuptrekking, støyping) står ikkje på sidene.

**FAKTA – reservedelar og reparasjon hos Northern.**
- Snowball Portable: «Utskiftbar LED-modul med trykkontakt» og «Utskiftbart batteri» [N:snowball-portable-table-lamp]. Produktarket listar reservedelane glasskjerm, LED-panel, diffusorlinse, ladekabel og deksel til USB-porten [N3]. Bruksrettleiinga omtalar «the threaded glass globe» og seier at glaset berre skal løysast når LED-en skal bytast [N4].
- Glasskjermar blir selde som reservedel: Snowball 420 kr, Over Me frå 1 200 kr, Dahl 2 590 kr [N:snowball-table-lamp], [N:over-me-ceiling-wall-lamp], [N:dahl-pendant-lamp-small]. Kin, Balancer og Hall oppgjev glas som tilgjengeleg reservedel, Hall også LED-modulen, Acorn tredelane [N:kin-table-lamp], [N:balancer-mini-lamp], [N:hall-wall-lamp], [N:acorn-floor-lamp].
- Oslo Wood har fot, skjerm, dimmar og sokkel som eigne varenummer [N:oslo-wood].
- Nyare produktsider har overskrifta «Replaceable electronics» (Snowball Portable, Tradition, Glint glass opal) [N:tradition-table-lamp], [N:glint-glass-opal-wall-lamp].

**FAKTA – vedlikehaldsrettleiinga** [N6]: munnblåse glas kan ha variasjon i tjukkleik, små bobler og virvlar, og dette er «characteristics», ikkje feil. Ubehandla messing og kopar får patina. Olja eik og finer får patina og skal oljast på nytt når overflata verkar tørr. Pulverlakk og lakk krev lite. Tekstil må haldast rein, fordi støv slit på fibrane og kan svekkje flammehemminga.

**FAKTA – tekstilpartnar.** Innvik i Innvikfjorden er «long-standing textile partner» for Northern sine møblar. Verksemda fargar, vev og etterbehandlar sjølv, har over 50 tilsette, har drive i over 130 år og arbeider mest med ull, lin og viskose [N8].

**TOLKING.** Northern-lampa er, materielt sett, ein metallkropp med eit lysande element i opalglas eller tekstil, og eitt berøringspunkt i messing. Plast er skjult eller sekundær. Vekta er ein del av kvalitetssignalet: bordlampene på nett veg 0,9–3,0 kg, medan Snowball Portable veg 0,5 kg. Northern har alt byrja å skrive reparasjon inn i produktsidene. Eit nytt produkt kan difor gå lenger på reparasjon utan å bryte med merkevara.

#### 2.2 Samanliknbare merke

**FAKTA** (primærkjelder lesne i denne økta; fleire produkt står i tabell A i `research/02-marknad.md`):

| Produkt | Material og prosess | Vekt | Reparasjon / demontering | Kjelde |
|---|---|---|---|---|
| Louis Poulsen PH 2/1 Portable | Skjermar i trelags munnblåse opalglas med sandblåsing på innsida; topp, kropp og fot i aluminium; messing-metallisert eller høgglans forkromma | 1,7 kg | «designed so that 100% of the product can be disassembled and reused»; utskiftbart batteri; 18 reservedelar | [L1] |
| Louis Poulsen PH 5 | Skjermar i trykt (spun) kopar, messing eller aluminium; nedste skjerm i trykt stål; avstandsstykke i valsa aluminium; diffusor i frosta glas; pulverlakk eller våtlakk | 8,6 kg | Same formulering om demontering; 23 reservedelar | [L2] |
| HAY PC Portable | Sprøytestøypt: topp, opak skjerm og fot i 95 % resirkulert ABS (post-consumer) + 5 % ABS; translusent skjerm og diffusor i 100 % resirkulert PP; batterihaldar i ABS, UL94-V0 | i.o. i arket | Utskiftbar LED-pære (G4) | [H1] |
| Fritz Hansen Clam Portable | Skjerm i polykarbonat, våtlakkert; kropp i stål med PC-deksel, våtlakkert; produsert i Kina | 0,8 kg | Utskiftbar LED og batteri (21700, 4800 mAh); «can be disassembled into parts» | [FH1] |
| Muuto Ease Portable | Kropp og skjerm i sprøytestøypt ABS, diffusor i opal akryl | 0,6 kg | i.o. | [MU1] |
| Marset FollowMe | Diffusor i blank opal PC, kropp i blank PC, hank i kryssfiner med eikefiner | 0,5 kg | i.o. | [M1] |
| &Tradition Flowerpot VP9 | Polykarbonat | i.o. | Batteri som reservedel | [AT1] |

**TOLKING.** Det finst to materialleirar. Den eine er sprøytestøypt polymer på 0,4–0,8 kg (HAY, Muuto, Marset, &Tradition, Fritz Hansen). Den andre er glas og metall (Northern Snowball Portable, Louis Poulsen PH 2/1). Northern står i den andre. HAY viser at resirkulert plast er mogleg i kategorien, men då i opake fargar og med CRI 75 og 85–155 lm ut av lampa [H1]. Fritz Hansen lakkerer polykarbonaten, noko retningslinene for resirkulering rår frå (punkt 6).

### 3. Prosessar ved nokre tusen einingar per år

**ANTAKING om volum.** «Nokre tusen per år» er her lese som om lag 3 000 lamper i året. Northern sitt reelle volum er ukjent og må spørjast om.

**FAKTA og vurdering per prosess.** Der eg ikkje fann tal, står «ukjent». Kolonnen «verktøy» er ei rangering (låg, middels, høg) når tal manglar. Rangeringa er mi tolking av kjeldene, ikkje eit tilbod.

| Prosess | Formfridom | Toleranse | Verktøy | Stykkpris | Designreglar | Overflate | Kjelde |
|---|---|---|---|---|---|---|---|
| Metalltrykking (spinning) | Rotasjonssymmetrisk. Innsnevring gjev underskorne former. | Ukjent | Låg. Trykkform i tre, plast eller metall, fordi kreftene er små. Faste kostnader lågare og variable høgare enn ved stansing, hydroforming og støyping. | Ukjent; arbeidskrevjande | Sluttdiameter alltid mindre enn emnet. Sprekk eller bulk gjev vrak. Aluminium, rustfritt, kopar, messing, kaldvalsa stål. | Spor etter rulla må slipast eller børstast (ANTAKING) | [W-spin] |
| Djuptrekking | Koppar og skåler. «Djup» når djupna er større enn diameteren. | Ukjent | Høg. Stempel og matrise i verktøystål, haldar mot rynker. | Låg ved store volum (ANTAKING) | Veggen blir tynnast ved stempelradien. Fleire trekk og gløding for djupe delar. Rustfritt krev om lag dobbel kraft av aluminium (166 mot 88 kN i kjelda sitt døme). | Glatt frå verktøy | [W-dd] |
| Pressstøyping av aluminium | Fri 3D-form med ribber, tappar og feste | 0,1 mm for dei første 2,5 cm, deretter 0,02 mm per cm | Høg. Herda verktøystål, «very high capital cost». Levetid om lag 100 000 skot for aluminium. | Låg ved volum. Kan løne seg frå 2 000 delar dersom støypinga fjernar mykje maskinering. | Minste gods 0,89 mm, slepp minst 1:100 (0,6°), tjukkaste parti under 13 mm, hòlkil i alle hjørne. Porer hindrar varmebehandling og sveising. | Ra 1–2,5 µm. Silisiumrike støypelegeringar gjer lyse fargar vanskelege ved anodisering. | [W-dc], [W-an] |
| Ekstrudering + maskinering | Konstant tverrsnitt med hòlrom, spor og skrukanalar; resten må fresast eller dreiast | I Hydro sin designmanual, kapittel 12 (krev innlogging, ikkje lese) | Låg til middels (ANTAKING). Hydro gjev berre pris per prosjekt. Hòle verktøy er dyrare enn massive. | Ukjent | Pressbolt ved 450–500 °C, profil ut i 5–50 m/min og 25–45 m lengd. Fleirhòlsverktøy med opptil 16 opningar for små profil. | Godt eigna for anodisering (ANTAKING, ikkje verifisert) | [HY-ex] |
| Platearbeid (laser + knekking) | Flate og bretta former, hòl og perforering | ±0,13 mm kant til kant (tynn plate), ±1° på knekk, 0,38 mm over to knekk | Ingen delspesifikke verktøy | Ukjent; fell lite med volum (ANTAKING) | Tjukkleik 0,6–6,35 mm, minste flens 4 × tjukkleik, hòl minst like store som tjukkleiken | Laserkant, må gradast; lakk eller anodisering etterpå | [P-sm] |
| Munnblåsing av glas i form | Hòle, lukka og mjuke former; rotasjonssymmetri vanlegast | Variasjon i tjukkleik er normalt; tal ukjent | Ukjent. Former i tre eller metall. | Høg (ANTAKING for delpris). Ferdige lamper i munnblåse glas frå Hadeland kostar 4 800–8 900 kr i utsal. | Arbeidstemperatur 870–1040 °C, avspenning ved 371–482 °C i timar til døgn | Blank frå form; matt ved etsing eller sandblåsing | [W-gb], [L1], [N6], [HG1] |
| Pressing av glas | Tjukkveggja, opne former med relieff (ANTAKING) | Ukjent | Ukjent; stålform, truleg høg (ANTAKING) | Ukjent | Ukjent | Ukjent | Inga kjelde funnen |
| Sprøytestøyping | Nær fri form, feste og ribber integrert | Typisk ±0,25 mm | Aluminium: 2 000–5 000 USD for om lag 1 000–10 000 skot. Stål: 5 000–100 000 USD for 10 000+ skot. Sidetrekk aukar prisen 15–30 %. | 1–5 USD per del ved 500–10 000 delar. Døme: 2,6 USD ved 5 000 delar, verktøy medrekna. | Slepp minst 2°, jamn vegg, ribbe 0,5 × vegg, innvendig radius 0,5 × vegg. Minste lønsame serie om lag 500 delar. Verktøyet er 50–70 % av totalkostnaden ved 1 000–10 000 delar. | SPI A (blank) til D (strukturert) rett frå verktøy | [P-im], [FL-im], [F, slide 38–41] |
| Termoforming | Skal- og kuppelformer frå plate; detaljar berre på éi side | Ukjent | Låg. Former i gips, tre, plast eller aluminium; billegare enn sprøytestøyping. | Ukjent | Tjukkplate er typisk for 250–3 000 delar i året. Ujamn veggtjukkleik er ei ulempe. Kant må fresast. PMMA, PC og ABS kan formast. | Som plata; satinert PMMA held på overflata etter forming | [W-tf], [FL-tf], [RO-led] |
| 3D-printing i småserie (MJF, PA12) | Fri form, underkutt utan kostnad | ±0,30 mm + 0,1 % av lengda | Ingen | 20–100 USD per prototypedel (allment tal for 3D-print) | Minste vegg 0,5 mm, tilrådd jamn vegg 3,2 mm, byggjevolum 284 × 380 × 380 mm | Kornete; berre svart hos denne leverandøren; dampglatting mogleg | [P-mjf], [P-im] |
| Dreiing i tre | Rotasjonssymmetrisk | Ukjent; tre rører seg med fukt (ANTAKING) | Låg (ANTAKING) | Ukjent | Northern brukar bøk og valnøtt (Acorn) og eikefiner (Diva) | Olje, voks eller lakk | [N:acorn-floor-lamp], [N:diva-floor-lamp] |
| Keramikk (slikkerstøyping) | Hòle former frå gipsform | Ukjent; krymp ved tørking og brenning er ikkje talfesta i kjelda | Låg; gipsformer har avgrensa levetid, tal ukjent | Ukjent | Støypetid 35–60 min for leirgods (earthenware), 10–15 min for 5–10 mm gods; trykkstøyping 2 min | Glasert eller rå | [W-sc] |

**Berekna – verktøy for sprøytestøyping fordelt på delar.** Eit aluminiumsverktøy til 3 000–5 000 USD som held 5 000–10 000 skot, gjev 0,3–1,0 USD per del i verktøykostnad [P-im]. Ei lampe med tre sprøytestøypte delar treng tre verktøy. Ved 3 000 lamper i året er aluminiumsverktøya utslitne etter om lag to til tre år (5 000–10 000 skot / 3 000 per år).

**FAKTA – resirkulert plast i sprøytestøyping** [FR]:
- Resirkulert PP har bøyemodul 900–1200 MPa mot om lag 1550 MPa for jomfrueleg, brotstyrke 21 MPa eller lågare mot 25, og brotforlenging 5–10 % mot 20–30 % (s. 5).
- Rekn med éi toleransegruppe dårlegare etter DIN 16742 (s. 8), 10–20 % tjukkare gods i berande delar (s. 11), ribber under 0,5 × veggtjukkleik for PP og 1/3 for synlege flater (s. 12).
- Grov tekstur skjuler småfeil (s. 10). Sneppfeste bør ha lang fjørlengd og låg tøying (s. 20).
- Resirkulert plast frå forbrukaravfall har tradisjonelt berre vore svart; lys kjelde gjev pastellar, reine sterke fargar er vanskelege (s. 6).

**TOLKING – kva som passar volumet.**
- *Passar godt:* platearbeid, metalltrykking, røyr og ekstrudert profil med maskinering, dreiing, glas blåse i form, PMMA skore frå plate eller termoforma, 3D-print av interne delar. Felles for dei er låg startkostnad og at forma blir rotasjonssymmetrisk, bretta eller har konstant tverrsnitt.
- *Mogleg:* sprøytestøyping av éin til tre små delar i aluminiumsverktøy, til dømes elektronikkberar og batterilok.
- *Krev større volum eller delt verktøy med andre produkt:* pressstøyping, djuptrekking og truleg pressa glas.
- Formspråket som følgjer av dei rimelege prosessane, ligg nær det Northern alt har: kule og sylinder (Snowball), trykt klokke (Dokka), bretta plate (Archive, som starta som papirmodellar [N9]).

### 4. Diffusor- og skjermmaterial

**FAKTA.**

| Material | Lystransmisjon og spreiing | Varme | Gulning og slitasje | Vekt | Resirkulering | Bruk i dag | Kjelder |
|---|---|---|---|---|---|---|---|
| Opalglas (munnblåse) | Tal ukjent. Opaliteten kjem av partiklar med annan brytingsindeks som spreier lyset. | Uproblematisk; glas blir forma ved 870–1040 °C | Uorganisk; ripefastare enn PMMA | Om lag 2,2–2,5 g/cm³ | Varmefast glas, blyglas og keramikk skal ikkje i emballasjeglas. Om opalglas kan gå dit, er ukjent. | Northern Snowball, Kin, Balancer, Hall; Louis Poulsen PH 2/1 (trelags) | [W-mg], [W-gb], [W-pmma], [W-gr], [L1] |
| PMMA (akryl), opal | Klår: opptil 92 % ved 3 mm. LED-opal (PLEXIGLAS LED 0M200 SC): 72 % ved 3 mm med sterk spreiing. Satinice kvit WH02: 44 %. | Glasovergang 105 °C (handelskvalitetar 85–165 °C); tenner ved 460 °C | Garanti mot gulning i 30 år for klåre PLEXIGLAS-kvalitetar. Ripast lettare enn glas. | 1,18 g/cm³, «half the weight of glass» | Produsenten oppgjev «100% recyclability». Kan depolymeriserast til monomer ved minst 400 °C. PLEXIGLAS proTerra har opptil 90 % resirkulert råvare. | Northern Salto, Blush, Me («opal akryl»); Muuto Ease | [W-pmma], [RO-led], [RO-prod], `research/05`, punkt 8 |
| PC (polykarbonat), opal | Tal ikkje henta | Glasovergang 147 °C; øvre brukstemperatur 115–130 °C | UV-motstand «fair»; standardkvalitetar toler ikkje langvarig UV utan stabilisator. «Blir gul i sollys.» Låg ripefastleik. | 1,20–1,22 g/cm³ | Resirkuleringskode 7 («andre»). Resirkulert PC frå industriavfall og PC/ABS frå EE-avfall er teke i bruk i nye produkt. | Panthella Portable, Flowerpot VP9, Clam, FollowMe | [W-pcarb], [F, slide 17], [PolyCE, s. 65], [FH1], [M1], [AT1] |
| Tekstil over ramme | Tal ukjent | Ukjent; kan innehalde flammehemmarar | Samlar støv; støv slit på fibrane og kan svekkje flammehemminga | Lågt | Ukjent; avheng av fiber og tilsetjingar | Northern Tradition (strikka polyester), Oslo Wood | [N:tradition-table-lamp], [N6], [G, s. 39] |
| Papir | Tal ukjent | Ukjent | Kort levetid samanlikna med metall | Lågt | Papir er vanleg å materialattvinne | Ingen hos Northern | [G, s. 35, s. 63] |
| Tynt tre (finer) | Tal ukjent | Ukjent | Får patina; skal ikkje stå i sterk sol eller fukt | Lågt | Trebasert; sertifisering (PEFC, FSC) tilrådd | Northern Diva (eikefiner på kryssfiner, som lamellar) | [N:diva-floor-lamp], [N6], [G, s. 37] |

**FAKTA – grenser for resirkulert plast nær varme og i optiske delar.** Resirkulert ABS kan svikte i kuletrykkprøva over 90 °C [PolyCE, s. 66]. Retningslinene rår til jomfrueleg plast i svært krevjande delar som transparente lysleiarar [PolyCE, s. 45, retningsline 26]. I 2021 var det ikkje mogleg å få resirkulert PMMA i god nok kvalitet til ei IR-linse [PolyCE, s. 55].

**FAKTA – areal.** 300 lm bak ein opal diffusor treng om lag 320 cm² lysande flate for å halde seg rundt 3000 cd/m² (`research/05-teknologi-og-komponentar.md`, punkt 8, berekna der).

**Berekna.** Ei skive med Ø 250 mm har 491 cm², ei med Ø 300 mm har 707 cm², og ei kule med Ø 120 mm har 452 cm² overflate.

**TOLKING.**
- Opalglas gjev mest Northern-preg og eldest best, men lystapet er ukjent og må målast på ein prøve. Glaset er tungt og sit høgt, så det styrer tyngdepunktet (punkt 8). Det bør behandlast som ein langlevd reservedel, ikkje som noko som blir resirkulert.
- Opal PMMA er det tryggaste valet for ei stor, flat eller svakt krumma lysflate: dokumentert transmisjon, låg vekt, kan skjerast frå plate utan verktøy, og Northern brukar det alt. Kjensla av kvalitet er svakare enn for glas, så PMMA bør liggje bak ein metallkant eller eit tekstil, ikkje vere det handa møter.
- PC er rett når diffusoren må tole slag eller varme, eller må sprøytestøypast med feste integrert. Elles talar gulning og plastkjensle mot.
- Tekstil, papir og finer gjev varme og heimleg karakter, men manglar tal for lys og brann. Dei bør vere lause, utskiftbare skjermar utanpå ein tett diffusor, slik at dei kan vaskast eller bytast.
- Med LED-effekt under 6–8 W og LED-kortet skrudd mot metall (`research/05`, punkt 7) blir diffusoren neppe varm nok til at PMMA er eit problem. Dette er ei ANTAKING som må kontrollerast med temperaturmåling på prototype.

### 5. Resirkulerte og lågkarbon-alternativ

**FAKTA – aluminium.**
- Globalt snitt for primæraluminium i 2024: 14,4 tonn CO2e per tonn, vogge til port. Elektrisiteten står for 8,5 av dette [IAI].
- Hydro REDUXA: karbonfotavtrykk 4,0 per kg aluminium, «about a quarter of the global average», laga med vass- og vindkraft, verifisert av DNV etter ISO 14067. Leverast som pressbolt, støypelegering, valseblokk og valsetråd [HY-r].
- Hydro CIRCAL: minst 75 % skrap frå brukte produkt (post-consumer), verifisert av DNV. Fotavtrykk 1,9 kg CO2e/kg i EU og 1,5 i USA, «product and market dependent». Leverast som pressbolt og støypelegering. CIRCAL 100R er laga heilt av brukt skrap og blir omtala som «near-zero»; sida gjev ikkje tal. 130 tonn vart produsert i Clervaux i Luxembourg i mai 2023 [HY-c].
- Omsmelting krev 5 % av energien til primærproduksjon. Prosesskrap frå fabrikk ber med seg fotavtrykket til primærmetallet; brukt skrap har svært lågt fotavtrykk [HY-rec]. Same 5 %-tal står i forelesinga [F, slide 33].

**FAKTA – stål** [WS]:
- Globalt snitt 2024: 1,92 tonn CO2 per tonn råstål (2,18 tonn CO2e med det utvida GHG-målet).
- Masomn og konverter (BF-BOF, om lag 10 % skrap): 2,34 tonn CO2 (2,66 tonn CO2e).
- Skrapbasert lysbogeomn (over 70 % skrap): 0,69 tonn CO2 (0,71 tonn CO2e).
- SSAB Zero er laga av resirkulert stål med fossilfri energi; sida gjev ikkje tal. For SSAB Fossil-free er målet under 0,05 kg CO2e/kg i scope 1, 2 og oppstraums jernmalm [SSAB].

**FAKTA – rustfritt stål** [OTK]: globalt snitt 2024 er 7 kg CO2e/kg. Outokumpu sitt snitt er 1,6 kg CO2e/kg (vogge til port, scope 1–3). Circle Green går ned til 0,5 kg CO2e/kg, har 100 % resirkulert innhald og blir levert som varm- og kaldvalsa band.

**FAKTA – plast.**
- Resirkulert PP har om lag halve CO2-utsleppet av jomfrueleg PP (2 kg per kg) [FR, s. 3]. Flokk brukte 1 070 tonn resirkulert plast i 2025 og oppgjev 1 390 tonn CO2 spart [FS, s. 26]. Berekna: 1 390 / 1 070 = 1,3 kg CO2 spart per kg plast.
- Typisk industriell PP er 50–100 % resirkulert, avhengig av kjeldekvalitet [FR, s. 2].
- PLEXIGLAS proTerra (Röhm, Tyskland): PMMA med opptil 90 % resirkulert råvare [RO-prod]. Om han finst i opal LED-kvalitet, er ikkje verifisert.
- Resirkulert PC og ABS: I Philips sin Senseo Eco-demonstrator leverte Sitraplas resirkulert PC i mellom anna «diffuse white» og røyktranslusent svart, og MGG Polymers leverte resirkulert ABS. Produktet fekk 75 % resirkulert innhald [PolyCE, s. 65].
- HAY brukar 95 % resirkulert ABS og 100 % resirkulert PP i ei lampe som er i sal [H1].

**FAKTA – glas.** Kvar 10 % auke i glasskår (cullet) sparar 2–3 % smelteenergi, og eitt tonn resirkulert glas sparar 315 kg CO2 [W-gr]. Artikkelen er merkt med kvalitetsmanglar; tala bør kontrollerast. Leverandør av lampeglas med resirkulert innhald er ikkje funnen.

**FAKTA – tre.** GRIP rår til trevirke frå skogbruk med PEFC, FSC eller «Levende skog»-merking, og til å unngå sjeldne og seintveksande treslag [G, s. 37]. CO2-tal og sertifiseringsdekning i Noreg vart ikkje henta (PEFC Norge si side var sperra for oppslag).

**FAKTA – åtvaringar frå kurset.**
- Flokk prøvde havplast (Plastix Oceanix PP) for fem år sidan. Han fall gjennom i tekniske testar fordi han var for sprø [FS, s. 41].
- GRIP: bruk resirkulert material i kjernen eller på delar som ikkje syner, eller bruk farge og tekstur i resirkulert material som designelement [G, s. 38]. Ver varsam med å bruke «resirkulerbar» som salsargument før produktet faktisk inngår i ei fungerande returordning [G, s. 63].

**Berekna – kva materialkjelda betyr for ei lampe.** Reknedøme med 248 g aluminium (trykt skjerm og røyr) og 827 g stål (fotplate Ø 150 × 6 mm), sjå pakke B i siste kapittel. Berre råmaterialet er med; forming, overflate, transport, glas, plast og elektronikk er ikkje med.

| Val | Aluminium 0,248 kg | Stål 0,827 kg | Sum |
|---|---|---|---|
| Globalt snitt primæraluminium + masomnstål | 0,248 × 14,4 = 3,57 | 0,827 × 2,34 = 1,94 | 5,5 kg |
| REDUXA + skrapbasert stål | 0,248 × 4,0 = 0,99 | 0,827 × 0,69 = 0,57 | 1,6 kg |
| CIRCAL + skrapbasert stål | 0,248 × 1,9 = 0,47 | 0,57 | 1,0 kg |

Til samanlikning: 588 g rustfritt stål (røyr og fotplate som i ei Snowball-liknande lykt) gjev 4,1 kg CO2e med globalt snitt, 0,94 kg med Outokumpu sitt snitt og 0,29 kg med Circle Green.

**TOLKING.** Val av metallkjelde endrar materialutsleppet med ein faktor på tre til fem i dømet (5,5 / 1,6 og 5,5 / 1,0). Stålballast i foten er billeg i CO2 så lenge stålet er skrapbasert. Aluminium og rustfritt er det som må spesifiserast. Tala er ulike mål (CO2 mot CO2e, råstål mot ferdig metall) og må ikkje summerast i ein presentasjon utan dette atterhaldet.

### 6. Overflatebehandling: resirkulering og reparasjon

**FAKTA.**

| Behandling | Kva det er | Miljø og resirkulering | Reparasjon og eldast | Northern i dag | Kjelder |
|---|---|---|---|---|---|
| Anodisering (aluminium) | Oksidsjikt på 1,8–25 µm (vanleg svovelsyreprosess). Sjiktet veks like mykje inn i som ut av overflata. Kan fargast og må då forseglast. | «One of the more environmentally friendly metal finishing processes»; biprodukta inneheld lite tungmetall og VOC. | Hardare enn rå aluminium. Kan sprekke over 80 °C, men flassar ikkje. Raudt og blått falmar lett; svart og gull er meir lysekte. Kvitt går ikkje. | «Børsta aluminium» på Hall, Glint og Butterfly; om dei er anodiserte, står ikkje | [W-an], [N:hall-wall-lamp] |
| Pulverlakk | Tørt pulver, herda ved 160–200 °C i om lag 10 min. Jamn film krev gjerne over 50 µm. | Ingen løysemiddel, lite eller ingen VOC. Overspray kan brukast om att. GRIP rår til pulverlakk framfor sprøytemåling. | Kan fjernast ved avbrenning (300–450 °C i om lag fire timar), kjemisk eller ved blåsing. Flekkreparasjon er ikkje omtala i kjelda. | Standard på stål og rustfritt («pulverlakkert») | [W-pc], [G, s. 41], [N6], [N:snowball-portable-table-lamp] |
| Våtlakk | Løysemiddel- eller vassbasert lakk | GRIP: bruk så lite organisk løysemiddel som mogleg, helst vassbasert | Kan flekkast (ANTAKING) | «Måla» på Acorn; Louis Poulsen brukar våtlakk på fargar | [G, s. 43], [L2], [N9] |
| PVD | Metall eller nitrid blir dampa på i vakuum som tynn film (under 4 µm på skjereverktøy). Gjev messing- og bronsefarge på rustfritt stål. | «Often more environmentally friendly than traditional coating processes» | «Sometimes harder and more corrosion-resistant» enn galvaniske sjikt. Kan ikkje flekkast (ANTAKING). | Messingversjonen av Snowball Portable er PVD på rustfritt stål | [W-pvd], [N:snowball-portable-table-lamp] |
| Forkromming, fornikling, forsinking | Galvanisk metallsjikt | Krom står på Flokk si forbodsliste. GRIP: unngå forkromma, fornikla og forsinka overflater. | – | Ikkje oppgjeve hos Northern. Louis Poulsen brukar «high-lustre chrome plated». | [FS, s. 22–23], [G, s. 43], [L1] |
| Ubehandla messing og kopar | Rått metall | Inga behandling | Får patina; skal berre tørkast med tørr klut | Messingdetaljar på mange lamper | [N6] |
| Olje og voks på tre | Trenger inn i veden | – | Brukaren oljar på nytt når overflata er tørr | Olja eik og finer | [N6] |
| Etsing og sandblåsing av glas | Matterer glaset | – | Varig | Dahl (etsa), PH 2/1 (sandblåsing på innsida) | [N9], [L1] |

**FAKTA – overflate på plast.**
- Unngå lakk og andre belegg på plast: belegget endrar tettleiken slik at delen hamnar i feil fraksjon, og det forureinar plasten. Trykk, lasergravering og tekstur i forma er greitt [PolyCE, s. 41, retningsline 6].
- Ikkje bruk plettering, galvanisering eller vakuummetallisering på plast [PolyCE, s. 41, retningsline 11].
- GRIP seier det same: unngå å male eller metallisere plastdelar, og bruk heller farga materiale enn overflatebehandling [G, s. 64].

**TOLKING.**
- Metall toler overflatebehandling betre enn plast i resirkuleringa. At lakk på metall brenn av ved omsmelting og at anodiseringssjiktet er aluminiumoksid, er fagleg allmennkunnskap som eg ikkje fekk verifisert mot kjelde her. Kjeldene viser i alle fall at pulverlakk kan brennast av ved 300–450 °C [W-pc].
- For reparasjon er skiljet dette: pulverlakk, anodisering og PVD kan ikkje flekkast av brukaren, så ein skadd del må bytast eller lakkerast om. Ubehandla messing, børsta rustfritt stål og olja tre kan pussast opp. Delar som blir tekne i kvar dag (dimmar, handtak, kant å løfte i) bør difor vere i material som toler slitasje utan belegg.
- PVD er eit truverdig alternativ til forkromming og metallisering når Northern vil ha messingfarge på ein stor del. Massiv messing bør avgrensast til små dreia detaljar.

### 7. Samanføying for demontering og materialseparasjon

**FAKTA – kva kjeldene krev.**
- Flokk: ingen lim, stiftar eller utilgjengelege skruar. Demontering med vanleg verktøy på få minutt [FS, s. 33]. 2-komponent samanbunden plast kan ikkje resirkulerast [FR, s. 7].
- GRIP: gjer delane lette å skilje med stiftar, skruar og mekaniske samband i staden for lim. Unngå tape og etikettar. Bruk få og like material. Merk alle delar med material [G, s. 62–64]. «Velg prosesser uten utslipp, f.eks. skruing fremfor sveising» [G, s. 44].
- PolyCE, retningsliner for EE-produkt som blir kverna:
  - Fest batteri med klikk eller snepp, ikkje lim, sveis eller innkapsling. Bruk harde celler, ikkje mjuke litiumceller (retningsline 1, s. 39).
  - Fest kretskort, kablar og motorar med metallskruar, klikkfingrar eller pluggar. Unngå 2K, dobbeltsidig tape, lim og sveising (retningsline 2, s. 39).
  - Gjer glas, keramikk, tekstil, tre og leidningar lette å ta av, fordi dei elles forureinar materialstraumane (retningsline 4, s. 40).
  - Minimer magnetar; dei hamnar i jernfraksjonen (retningsline 8, s. 41). Minimer termoplastiske elastomerar (retningsline 9, s. 41).
  - Unngå å støype ulike material saman (2K, overstøyping, in-mould-etikett) (retningsline 12, s. 42).
  - Unngå samband som kapslar eitt material varig inn i eit anna: innstøypte innsatsar, naglar, stiftar, pressa samband, boltar med mutter, lodding, sveising og clinching (retningsline 13, s. 42).
  - Bruk berre vanlege plasttypar: ABS, MABS, PE, PP, PA, PC, PC/ABS, HIPS (retningsline 19, s. 44). Unngå glasfiberfylt plast (20) og polymerblandingar utanom PC/ABS (22).
  - Unngå å feste jernmetall til ikkje-jernmetall, heller ikkje med festemiddel: ein stålskrue i ein aluminiumsdel følgjer anten aluminiumen eller dreg han med til jernfraksjonen (retningsline 30, s. 46). Ikkje fest stål, rustfritt stål eller kopar varig til aluminium, og ikkje rustfritt stål eller kopar varig til stål (retningsline 31, s. 46).
- Slik EE-avfall blir handtert: innsamling, forbehandling der produktet blir knust opp og batteri og verdifulle komponentar plukka ut, kverning med sortering i jern, ikkje-jern og plast, og finsortering av plast [PolyCE, s. 12]. Småelektronikk blir kverna [PolyCE, s. 13]. Louis Poulsen skriv at lampene deira skal handterast som elektronisk avfall [L1].
- Verktøy: batteriforordninga krev at sluttbrukaren kan ta ut batteriet med verktøy som er i vanleg handel, utan spesialverktøy (med mindre det følgjer gratis med), proprietært verktøy, varme eller løysemiddel. EN 45554:2020 deler verktøy i fire grupper: grunnleggjande verktøy eller ingen, produktgruppespesifikke, vanleg tilgjengelege og proprietære [EU-bat, punkt 2.1]. Regelverket elles er dekt i `research/05-teknologi-og-komponentar.md`, punkt 4, 10 og 11.

**FAKTA – korleis andre løyser det.** Snowball Portable har gjenga glaskuppel og LED-modul med trykkontakt [N4], [N:snowball-portable-table-lamp]. I Kin «hviler» glasskjermen på marmorfoten ifølgje omtalen; om han er festa, står ikkje [N9]. Balancer Mini skiftar mellom vegg og bord med ei magnetisk metallplate [N9]. PolyCE sin demonstrator hadde hus som var skrudd saman «so it breaks up easily during the shredding step», og linsedeksel festa med snepp [PolyCE, s. 54–55].

**TOLKING – festemåtar vurderte.**

| Feste | Reparasjon | Separasjon ved kverning | Merknad |
|---|---|---|---|
| Gjenger i sjølve delane (glas mot metallkrage, lok mot kropp) | Svært god, utan verktøy | God når delane er i same metall; glas må takast av først | Northern-presedens i Snowball Portable. Krev pakning eller toleranseopptak mot glas. |
| Bajonett | Svært god, utan verktøy | God | Kvart-omdreiing gjev tydeleg «open/lukka». Krev presise spor, lettast i dreia eller støypt metall. |
| Standardskruar (éin type, t.d. Torx eller kryss) | God med grunnleggjande verktøy | Avheng av materialpar. Stålskrue i ståldel er uproblematisk. Stålskrue i aluminium er det PolyCE åtvarar mot. | Få, like og synlege frå undersida. Ikkje gøym dei under limte føter eller etikettar. |
| Snepp i plast | God om sneppet toler fleire syklusar | God; sneppa delar fell frå kvarandre | Lang fjørlengd og låg tøying, særleg i resirkulert plast [FR, s. 20] |
| Klemring, fjørring, låsering | God | God | Eignar seg til å halde ei diffusorskive eller ei ballastskive utan skruar |
| Tyngdekraft og styrekant | Svært god | God | Berre for delar som ikkje kan falle ut ved flytting |
| Magnet | Svært god | Dårleg; magneten forureinar jernfraksjonen | Berre om funksjonen krev det |
| Pressa samband, nagle, clinching | Dårleg | Dårleg | Unngå mellom ulike material |
| Lim, dobbeltsidig tape, sveis mellom ulike material | Dårleg | Dårleg | Unngå |
| Innstøypt metall i plast, 2K-støyp, in-mould-folie | Dårleg | Dårleg | Unngå. Skru heller i tapp i plasten (ytterdiameter 2 × skruen [P-im]). |

**TOLKING – motsetnaden mellom reparasjon og kverning.** Skruar er best for reparasjon, medan PolyCE vil ha færrast mogleg innkapsla og blanda metallsamband. Løysinga er å la dei store delane gripe i kvarandre med gjenger eller bajonett i same metall, bruke skruar berre der ein modul skal bytast, og sørgje for at ulike metall ligg laust mot kvarandre. Ei ballastskive i stål kan til dømes liggje laust i ein aluminiumsfot og bli halden av eit gjenga botnlok.

**TOLKING – monomaterialstrategiar som passar ei Northern-lampe.**
1. *Eitt metall i alt som er skrudd eller gjenga saman.* Heile kroppen i aluminium, eller heile i stål, slik Buddy, Ombre og Salto er i dag [N:buddy-table-lamp], [N:ombre-table-lamp], [N:salto-table-lamp].
2. *Éin laus diffusor.* Glas, PMMA eller tekstil som éin del brukaren kan ta av.
3. *Éin plasttype i dei få plastdelane,* ufarga eller gjennomfarga, ulakkert og merkt. GRIP viser til merking av plast med standardsymbol [G, s. 62].
4. *Farge i materialet framfor på materialet* der det er mogleg: børsta rustfritt stål, anodisert aluminium, gjennomfarga plast, opalt glas.

### 8. Stabilitet og vekt i ei flyttbar lampe

**FAKTA – kva Northern-lamper veg.** Snowball Portable 0,5 kg med rustfri stålkropp og fot på 9 × 9 cm [N3], `research/02-marknad.md` (tabell A). Balancer Mini 1,0 kg. Ombre 1,8 kg, Archive 1,9 kg, Buddy 2,1 kg og Salto 2,5 kg, alle i stål. Kin 3,0 kg med marmorfot [N:…]. Om Balancer golvlampe skriv Northern at «en tung base» forankrar konstruksjonen [N9].

**FAKTA.** GRIP rår til å bruke festeanordningar i staden for eigenvekt for å gje stabilitet [G, s. 35]. Stabilitetstesten i EN 60598-2-4 blir gjord på skråplan med lyskjelda montert (`research/05`, punkt 10). Vinklane er ikkje verifiserte; eg meiner å hugse 6° og 15°, og dette må kontrollerast i standarden.

**Berekna – veltevinkel.** Ei lampe på eit skråplan veltar når loddlina frå tyngdepunktet fell utanfor fotkanten: tan θ = r / h, der r er avstanden frå midten til fotkanten og h er tyngdepunktshøgda. For 6° må r / h vere over 0,105, for 15° over 0,268. Krafta som veltar lampa ved eit støyt i høgda H er F = m · g · r / H.

Reknedøme, lykt med glaskule Ø 120 mm (3 mm gods, 339 g) på aluminiumsrøyr Ø 40 × 150 mm (73 g), lok 60 g, elektronikk og batteri 150 g lågt i foten. Høgder og delvekter er ANTAKING for dømet:

| Variant | Totalvekt | Tyngdepunkt | Veltevinkel, fot Ø 110 | Veltevinkel, fot Ø 80 |
|---|---|---|---|---|
| Med laus stålskive Ø 110 × 6 mm (445 g) i foten | 1,07 kg | 78 mm | 35° | 27° |
| Utan stålskive | 0,62 kg | 131 mm | 23° | 17° |

Støytkraft: ei lampe på 0,5 kg med 45 mm frå midt til fotkant veltar ved 0,5 × 9,81 × 45 / 300 = 0,74 N i 300 mm høgd. Ei på 1,2 kg med 60 mm til kanten toler 2,35 N.

**Berekna – arbeidslampe med utkraga skjerm.** Hovud på 285 g (trykt aluminiumsskjerm 183 g, PMMA-skive 42 g, LED-modul 60 g) i avstand x frå midten av ei fotplate i stål, Ø 150 × 6 mm (827 g, pluss 80 g elektronikk). Veltemoment om fotkanten: 285 × (x − 75). Stabiliserande moment: 907 × 75 = 68 025 g·mm. Ved x = 200 mm er tryggleiksfaktoren 68 025 / 35 625 = 1,9. Ved x = 250 mm er han 1,4. Armen er ikkje med i reknestykket.

**TOLKING – ballast utan å blande material som ikkje kan skiljast.**

| Løysing | Separasjon | Vurdering |
|---|---|---|
| Laus eller skrudd stålskive, laserskoren | Jernfraksjon; fell ut når botnen blir opna | Best. Ingen verktøy, låg CO2 med skrapbasert stål (0,3 kg for 445 g). |
| Heile foten i stål, eller støypejern | Jernfraksjon | God. Støypejern krev støypeform. |
| Stein som fot (Kin: marmor) | Inert; blir ikkje resirkulert, men er lett å skilje om han ikkje er limt | Høgt Northern-preg, tung transport. Feste utan lim må løysast, t.d. gjennomgåande bolt. |
| Batteri og elektronikk lågast mogleg | Batteriet skal uansett ut | Gratis, men lita vekt: om lag 70 g per 21700-celle (`research/05`, punkt 4) |
| Brei fot og låg lampe | – | Det GRIP-rådet peikar mot: geometri i staden for eigenvekt |
| Sand, betong eller støypemasse i eit skal | Kan ikkje skiljast | Unngå |
| Metallklump innstøypt i plast | Kan ikkje skiljast | Unngå [PolyCE, retningsline 13] |

**TOLKING.** Fotradius og tyngdepunktshøgd verkar sterkare enn vekt. Ei glasflate høgt oppe er det som gjer ballast nødvendig. Lampa bør kjennast tung nok til å høyre heime hos Northern, men R02 peikar på om lag 1,2 kg som øvre grense for noko som skal flyttast (`research/02-marknad.md`, implikasjon 7). Til 1:1-modellen kan ballast støypast i lågtsmeltande legering i silikonform, slik forelesinga viser [F, slide 45], eller skjerast i stålplate.

### 9. Kopling mellom merkevare og material

**FAKTA.** Northern knyter sjølv merkevara til «solide materialer» og levetid «for generasjoner» [N1], til handverk [N7], og til at material endrar seg vakkert: patina på messing og tre, små variasjonar i munnblåse glas som «characteristics that make your glassware unique» [N6]. Om Unika skriv dei at ujamn tjukkleik i glaset gjev «en subtil ærlighet» [N9]. Om Kin: «kombinerer kvalitetsmaterialer og kontrasterende utførelser» [N9].

**TOLKING – kva material signaliserer nivået Northern ligg på.**

| Material | Signal | Grunnlag |
|---|---|---|
| Munnblåse opalglas, matt | Handverk, mjukt lys, arv frå Birger Dahl-klassikarane og Snowball | 14 av 33 lamper har glas [N:…] |
| Pulverlakkert stål i dempa fargar | Soliditet og vekt; fargepaletten er ein del av identiteten | Buddy, Dokka, Ombre, Salto |
| Børsta rustfritt stål og aluminium | Presisjon, «ærleg» metall | Archive, Hall, Glint |
| Messing som berøringspunkt | Varme og patina akkurat der handa møter lampa | Dimmarar på Snowball Portable, Salto, Balancer Mini, Me |
| Stein og tre som aksent | Natur og tyngd, kontrast til metall | Kin (marmor), Acorn (bøk, valnøtt), Diva (eik) |
| Tekstil | Heimleg, mjukt | Tradition, Oslo Wood; Innvik på møblane |
| Synleg plast | Ikkje ein del av uttrykket | Akryl berre som diffusor bak metall |

**TOLKING.**
- Nyfortolkinga briefen opnar for, kan liggje i korleis materiala blir sette saman, ikkje i å byte dei ut. Synlege gjenger, eit lok som kan opnast med ein mynt og ein diffusor som kan løftast av, kan lesast som den same «ærlegdomen» Northern alt skriv om.
- Sander si forelesing gjev eit språk for dette: i staden for å ekskludere eller skjule ufullkomne material kan ein «embrace» eller «highlight» dei (`context/Nicoline Sander Design with sustainability 26 aug 2026.pdf`, s. 48). Variasjon i resirkulert aluminium, i munnblåse glas eller i ei børsta overflate kan vere eit tilsikta trekk. Dette må avklarast med Northern, som i dag sel jamne, lakkerte flater.
- Ei rein plastlampe vil bryte med kvalitetsnivået og hamne i direkte priskonkurranse med HAY og Muuto.

### 10. Norske og nordiske leverandørar og industrimiljø

**FAKTA – verifisert i denne økta.**

| Aktør | Stad | Relevans | Kjelde |
|---|---|---|---|
| Hydro | Pressverk på Magnor; primærverk på Sunndal, Karmøy, Årdal og Høyanger; anlegg på Husnes | Ekstruderte profil, pressbolt i CIRCAL og REDUXA, eigen designmanual for profil | [HY-no], [HY-ex], [HY-c], [HY-r] |
| Hadeland Glassverk | Jevnaker | «All lamps are mouth-blown at Hadeland Glassverk»; 319 produkt i lampekategorien | [HG1] |
| Magnor Glassverk | Magnor | Glasverk sidan 1896, del av Home Brands, har lampekategori. Produksjonsmåte står ikkje på sida. | [MG1] |
| Plasto AS | Åndalsnes | Automatisert sprøytestøyping, ISO 9001 og 14001. Prosjektet HyPa utviklar produkt i resirkulert plast frå marin næring og forbrukaravfall. | [PLASTO] |
| New Comfort Products (NCP) | Hemnesberget | Sprøytestøyping med resirkulert plast. Avsluttar møbelproduksjonen; sel berre lager frå 18. september 2026. | [NCP] |
| Innvik | Innvikfjorden | Northern sin tekstilpartnar; ull, lin, viskose; fargar og vev sjølv | [N8] |
| Outokumpu | Finland (konsern) | Rustfritt stål med 1,6 kg CO2e/kg i snitt; Circle Green ned til 0,5 | [OTK] |
| SSAB | Sverige/Finland (konsern) | SSAB Zero og Fossil-free stål; tal for Zero står ikkje på sida | [SSAB] |
| Mjøs Metallvarefabrikk | Lonevåg, Osterøy | «Mekaniske komponenter og produkter»; prosessane står ikkje på framsida | [MJOS] |
| Vestre | Noreg/Sverige | Møbelprodusent som går over til «lower-carbon metals» og held reservedelar i heile levetida; leverandørar er ikkje namngjevne | [VESTRE] |
| Flokk | HÅG på Røros | Oppgjev at ein norsk avfallsfraksjon på 190 tonn i året går til dei i sin heilskap, og viser utrangerte brøytestikker som blir til granulat og stolskal | [FS, s. 27–29], [G, s. 13] |
| Glamox | Registrert adresse i Molde (`research/02-marknad.md`, punkt 9) | På lista over bedrifter for studieturen til Ålesund-regionen saman med Ekornes, Stokke og LK Hjelle | `context/Erstatningsoppgave for studietur Ålesund.md` |

**ANTAKING – kandidatar frå allmennkunnskap, ikkje verifiserte i denne økta.** Hydro sitt pressverk på Raufoss og industriklynga der. Speira i Holmestrand (valsa aluminium). Jotun (pulverlakk). Ulefos og Furnes (jernstøyperi). Lundhs i Larvik (larvikitt). Gudbrandsdalens Uldvarefabrik og Røros Tweed (ull). Kitron, Hapro og Norautron (elektronikkproduksjon). Louis Poulsen sin fabrikk i Vejen i Danmark. Eg fann ikkje namn på eit norsk metalltrykkjeri eller pressstøyperi for aluminium som eg kan stå inne for. Dette bør spørjast om hos Glamox og Northern.

**TOLKING.** Eit truverdig nordisk materialspor for Northern er aluminium frå Hydro, glas frå Hadeland og tekstil frå Innvik, saman med stål frå SSAB eller Outokumpu. Kvar Northern produserer i dag, er ukjent, og Fritz Hansen oppgjev Kina som opphavsland for Clam Portable [FH1]. Ein nordisk verdikjede vil truleg auke stykkprisen, og det må vegast mot prisbandet i `research/02-marknad.md`.

---

## Tal og fakta

| Storleik | Verdi | Kjelde |
|---|---|---|
| Tettleik stål / aluminium | 7,8 / 2,7 kg/liter | [F, slide 33] |
| Varmeleiing stål / aluminium | 74 / 235 W/mK | [F, slide 33] |
| Pris PP / ABS / PC | 9–12 / 20–40 / 42 kr/kg | [F, slide 13, 15, 17] |
| Leveringstid sprøytestøypeverktøy | 6–16 veker | [F, slide 39] |
| Northern-lamper med stål / glas / aluminium / messing / akryl | 27 / 14 / 10 / minst 10 / 4 av 33 | [N:…] |
| Vekt Northern bordlamper | 0,5 kg (Snowball Portable) til 3,0 kg (Kin H33) | [N3], [N:kin-table-lamp] |
| Reservedelspris glasskjerm | 420 kr (Snowball), frå 1 200 kr (Over Me), 2 590 kr (Dahl) | [N:snowball-table-lamp], [N:over-me-ceiling-wall-lamp], [N:dahl-pendant-lamp-small] |
| Primæraluminium, globalt snitt 2024 | 14,4 kg CO2e/kg | [IAI] |
| Hydro REDUXA | 4,0 kg CO2e/kg | [HY-r] |
| Hydro CIRCAL | 1,9 kg CO2e/kg (EU), minst 75 % brukt skrap | [HY-c] |
| Energi ved omsmelting av aluminium | 5 % av primærproduksjon | [HY-rec], [F, slide 33] |
| Stål, globalt snitt 2024 | 1,92 t CO2/t (2,18 t CO2e/t) | [WS] |
| Stål, masomn / skrapbasert lysbogeomn | 2,34 / 0,69 t CO2/t | [WS] |
| Rustfritt stål, globalt snitt / Outokumpu / Circle Green | 7 / 1,6 / 0,5 kg CO2e/kg | [OTK] |
| Resirkulert PP mot jomfrueleg | Om lag halve utsleppet (2 kg per kg) | [FR, s. 3] |
| Resirkulert PP, bøyemodul | 900–1200 MPa mot 1550 MPa | [FR, s. 5] |
| PLEXIGLAS proTerra | Opptil 90 % resirkulert råvare | [RO-prod] |
| Opal PMMA for LED, 3 mm | 72 % transmisjon | [RO-led] |
| Klår PMMA, 3 mm | Opptil 92 % | [W-pmma] |
| Glasovergang PMMA / PC | 105 °C / 147 °C | [W-pmma], [W-pcarb] |
| Øvre brukstemperatur PC | 115–130 °C | [W-pcarb] |
| Resirkulert ABS, kuletrykkprøve | Kan svikte over 90 °C | [PolyCE, s. 66] |
| Glasskår | 2–3 % energi spart per 10 % skår; 315 kg CO2 per tonn | [W-gr] |
| Pressstøyping, minste gods aluminium | 0,89 mm; slepp 0,6° | [W-dc] |
| Pressstøyping, toleranse | 0,1 mm på første 2,5 cm + 0,02 mm per cm | [W-dc] |
| Pressstøyping, verktøylevetid aluminium | Om lag 100 000 skot | [W-dc] |
| Sprøytestøyping, toleranse / slepp | ±0,25 mm / minst 2° | [P-im] |
| Sprøytestøypeverktøy, aluminium | 2 000–5 000 USD; 5 000–10 000 skot | [FL-im], [P-im] |
| Sprøytestøypeverktøy, stål | 5 000–100 000 USD | [FL-im] |
| Sprøytestøypt del ved 500–10 000 delar | 1–5 USD | [P-im] |
| Platearbeid, toleranse | ±0,13 mm kant til kant; ±1° knekk | [P-sm] |
| MJF-print, toleranse | ±0,30 mm + 0,1 % | [P-mjf] |
| Tjukkplate-termoforming, typisk volum | 250–3 000 delar per år | [W-tf] |
| Anodisering, sjikt | 1,8–25 µm | [W-an] |
| Pulverlakk, herding | 160–200 °C i om lag 10 min | [W-pc] |
| Pulverlakk, avbrenning | 300–450 °C i om lag 4 timar | [W-pc] |
| Hadeland, munnblåse lamper | Bordlampe 5 000 kr; taklamper 4 813–8 938 kr | [HG1] |
| Veltevinkel, lykt 1,07 kg med 445 g stålskive, fot Ø 110 | 35° (berekna) | Punkt 8 |
| Materialutslepp, 248 g aluminium + 827 g stål | 5,5 → 1,0 kg CO2e (berekna) | Punkt 5 |

---

## Implikasjonar for designet

1. **Bygg på paletten Northern eig.** Metallkropp, eitt lysande element i opalglas, akryl bak metall eller tekstil, og messing der handa møter lampa. Plast høyrer heime inni lampa eller som laus diffusor.
2. **La prosessane styre formspråket.** Rotasjonsformer (trykt, dreia, blåse), konstant tverrsnitt (røyr, profil) og bretta plate. Unngå former som berre let seg lage ved pressstøyping eller djuptrekking, med mindre Northern stadfestar volum som forsvarar verktøyet.
3. **Hald talet på sprøytestøypte delar til éin eller to.** Elektronikkberar og eventuelt batterilok, i éin plasttype, ulakkert, gjennomfarga og merkt. For dei første seriane kan dei printast i PA12.
4. **Lat metallet gjere tre jobbar:** bere, kjøle LED-en og gje vekt. Aluminium i hovud og skjerm, stål i foten.
5. **Diffusoren skal vere laus.** Gjenge, bajonett eller fjørring, aldri lim. For glas må grensesnittet ta opp variasjon i tjukkleik og diameter med pakning eller krage.
6. **Éi overflatebehandling per metall.** Pulverlakk i Northern-fargar, anodisering eller børsting. Ingen forkromming. Messing ubehandla, tre olja. Delar som blir slitne av hender, bør tole puss.
7. **Skil jern frå ikkje-jern med lause samband.** Ballast som laus stålskive, halden av eit gjenga lok. Stålskruar berre i ståldelar der det er mogleg.
8. **Éin skrutype, synleg frå undersida.** Batteriet ut med mynt eller vanleg skrutrekkar, LED-modulen ut med same verktøy.
9. **Spesifiser metallkjelda.** Aluminium med dokumentert fotavtrykk på høgst 4,0 kg CO2e/kg (REDUXA-klassen) eller 1,9 (CIRCAL-klassen), stål frå skrapbasert lysbogeomn, rustfritt i Outokumpu-klassen. Det reduserer materialutsleppet frå om lag 5,5 til 1,0–1,6 kg per lampe i reknedømet.
10. **Sikt mot 0,9–1,2 kg.** Tung nok til å høyre heime ved sida av Balancer Mini (1,0 kg), lett nok til å flyttast. Kontroller veltevinkel med r / h tidleg i skissefasen.
11. **Kandidatar til berekraftshandling på materialsida,** alle målbare:
    - «Ingen lim, ingen lakk på plast, éin skrutype» som konstruksjonsregel.
    - Alle metall frå resirkulert eller lågkarbon kjelde, med tal i materialspesifikasjonen.
    - Diffusor, batteri, LED-modul og dimmar som reservedelar med varenummer, slik Oslo Wood alt har for fot, skjerm, dimmar og sokkel.
    - Materialmerking av alle delar og ei demonteringsteikning i esken.
12. **I 1:1-modellen bør vekt og tyngdepunkt vere rette.** Legg inn ballast av stålplate eller støypt lågtsmeltande legering, og prøv velt og løft.

### Matrise: material og prosess × del × berekraft × kostnad × Northern-preg

Kostnad og volum gjeld om lag 3 000 lamper i året og er mi rangering (TOLKING) ut frå kjeldene i punkt 3. Northern-preg er vurdert mot punkt 2 og 9.

| Material og prosess | Eigna del av lampa | Berekraft | Kostnad ved lågt volum | Northern-preg |
|---|---|---|---|---|
| Stålplate, laserskoren og knekt, pulverlakkert | Fot, ballast, brakett, bretta skjerm | Skrapbasert stål 0,69 kg CO2/kg; jernfraksjon; pulverlakk utan løysemiddel | Låg; ingen verktøy | Høg (Archive, Buddy, Ombre) |
| Stålrøyr og rundstål, bøygd | Stamme, arm, ramme for tekstil | Som over | Låg | Høg (Birdy, Tradition) |
| Rustfritt stål, trykt eller dreia, børsta eller PVD | Kropp, fot, krage rundt glas | 7 → 1,6 → 0,5 kg CO2e/kg etter kjelde; treng ikkje belegg | Middels; hardt å forme | Høg (Snowball Portable, Archive) |
| Aluminium, metalltrykt, anodisert eller lakkert | Skjerm, reflektor, kjøleflate, lok | 14,4 → 4,0 → 1,9 kg CO2e/kg; lett | Låg til middels; rimelege trykkformer | Høg (Birdy-skjerm, Acorn) |
| Aluminium, ekstrudert eller røyr, maskinert | Stamme, ledd, ramme rundt lysflate, kjøleprofil | Som over; Hydro på Magnor | Låg til middels | Middels; meir teknisk uttrykk |
| Aluminium, pressstøypt, pulverlakkert | Kompleks fot eller ledd med integrerte feste | Støypelegering finst i CIRCAL; ikkje bland med smidd aluminium i faste samband | Høg startkostnad; krev volum | Middels (Hall har støypt arm) |
| Munnblåse opalglas | Kuppel, kule, sylinder som lysande element | Langlevd; resirkulering uviss; tung | Høg stykkpris, truleg låg formkostnad | Svært høg (signatur) |
| Pressa glas | Tjukk linse eller skive | Som over | Ukjent | Ukjent |
| Opal PMMA frå plate, skoren eller termoforma | Flat eller svakt krumma diffusor bak metallkant | Opptil 90 % resirkulert råvare tilgjengeleg; lett; må takast av før kverning | Låg; ingen eller rimeleg form | Middels; i bruk som skjult diffusor |
| PC, sprøytestøypt | Diffusor med integrerte feste, slagutsett del | Gulnar; resirkulert PC finst; verktøy krev volum | Middels til høg | Låg når han er synleg |
| Resirkulert ABS eller PP, sprøytestøypt | Interne delar: elektronikkberar, batterihaldar, lok | Om lag halvert utslepp mot jomfrueleg PP; éin plasttype | Middels; aluminiumsverktøy 2 000–5 000 USD | Nøytral når han er skjult |
| PA12, 3D-printa (MJF) | Interne delar i første seriar, prototypar | Ingen verktøy; PA er blant vanlege plasttypar | Høg stykkpris, null startkostnad | Nøytral når han er skjult |
| Tekstil over metallramme | Laus ytterskjerm, stor mjuk lysflate | Kan vaskast og bytast; brann og tilsetjingar må avklarast | Låg til middels | Høg (Tradition, Innvik) |
| Tre, dreia eller finer | Handtak, knott, topp, liten aksent | Fornybart; PEFC eller FSC; kan oljast om | Låg | Middels til høg som aksent |
| Stein, frest eller dreia | Fot og ballast | Inert, svært langlevd, tung å frakte; må festast utan lim | Middels | Høg som aksent (Kin) |
| Keramikk, slikkerstøypt | Fot eller kropp | Langlevd; kan ikkje resirkulerast som glas | Låg formkostnad | Middels; finst i tilbehør, ikkje i lamper |
| Messing, dreia | Dimmar, mutter, liten detalj | Lite volum; ubehandla | Låg i små delar | Svært høg som berøringspunkt |
| Papir | Laus, utskiftbar skjerm | Fornybart; kort levetid | Låg | Låg; ikkje i sortimentet |

### Tre materialpakkar for tre lampearketypar

Vekter og utslepp er **berekna** frå enkle geometriar og gjeld berre metallråvara. Dei er meinte for å samanlikne pakkane, ikkje som spesifikasjon.

#### Pakke A – «Lykta»: opal glaskuppel på metallfot, berbar

Stemningslys og ansiktslys først. Vidarefører Snowball Portable, men med større lysande flate og lågare tyngdepunkt.

| Del | Material | Prosess | Overflate | Feste |
|---|---|---|---|---|
| Kuppel | Opalglas, matt | Munnblåsing i form | Etsing eller sandblåsing | Gjenga krage eller bajonett med pakning |
| Kropp og fot | Aluminium (CIRCAL- eller REDUXA-klasse) | Trykt, eller røyr og dreia delar | Anodisert, eller pulverlakk i Northern-farge | Gjenger mellom kropp og botnlok |
| Ballast | Stålskive, skrapbasert | Laserskoren | Ubehandla eller fosfatert (ANTAKING) | Laus, klemd av botnloket |
| Dimmar | Messing | Dreia | Ubehandla | Mutter |
| Elektronikkberar | Éin plasttype (resirkulert ABS eller PA12) | Sprøytestøypt eller printa | Ingen | Snepp og to skruar |

- **Berekna:** om lag 1,07 kg med kule Ø 120 mm. Veltevinkel 35° med fot Ø 110 mm. Lysande flate 452 cm². Metallråvare: 133 g aluminium og 445 g stål gjev 3,0 kg CO2e med globale snitt og 0,56 kg med CIRCAL og skrapbasert stål.
- **Kvifor:** høgast Northern-preg, få delar, to metall som fell frå kvarandre, glas og batteri som reservedelar.
- **Risiko:** ukjend transmisjon og toleranse i glaset. Ei kule på 452 cm² gjev om lag 2 100 cd/m² ved 300 lm (berekna med formelen i `research/05`, punkt 8), så dette er ei stemnings- og møtelampe, ikkje eit arbeidslys.
- **Alternativ:** kropp i rustfritt stål som i Snowball Portable, då i Outokumpu-klassen.

#### Pakke B – «Skjermen»: retta arbeidslys frå metallskjerm, kabla

Arbeidslys først, stemning som indirekte lys når skjermen blir vend mot vegg. Vidarefører Birdy, Buddy og Salto.

| Del | Material | Prosess | Overflate | Feste |
|---|---|---|---|---|
| Skjerm og kjøleflate | Aluminium | Metalltrykt | Anodisert, eller pulverlakk; kvit innside | Skrudd til leddet |
| Diffusorskive | Opal PMMA 2–3 mm, eventuelt proTerra | Skoren frå plate | Satinert frå plata | Fjørring eller gjengering |
| Arm og stamme | Aluminiumsrøyr eller ekstrudert profil | Kappa, bora, eventuelt bøygd | Som skjermen | Dreia ledd med utskiftbar friksjonsskive |
| Fot | Stålplate 6 mm, skrapbasert | Laserskoren | Pulverlakk | Éin sentral skrue |
| Dimmar | Messing | Dreia | Ubehandla | Mutter |

- **Berekna:** om lag 1,2–1,3 kg. Tryggleiksfaktor mot velt 1,9 med hovudet 200 mm ut frå midten. Metallråvare: 248 g aluminium og 827 g stål gjev 5,5 kg CO2e med globale snitt og 1,0 kg med CIRCAL og skrapbasert stål.
- **Kvifor:** alle delar kan lagast utan dyre verktøy. Skjermen kjøler LED-en, så effekt over 6 W er mogleg (`research/05`, punkt 7). PMMA-skiva er billeg å byte.
- **Risiko:** uttrykket kan bli for likt det Northern alt har. Leddet er ein slitedel og må kunne strammast eller bytast. Stålskrue i aluminium bør avgrensast til punkt der delane uansett blir skilde ved reparasjon.

#### Pakke C – «Flata»: stor, mjuk lysflate som kan vendast

Éi lysande flate på 500–700 cm² som kan peike mot vegg (stemning), mot ansiktet (møte) eller ned mot bordet (arbeid). Dette er arketypen som svarar best på arealkravet i `research/05`.

| Del | Material | Prosess | Overflate | Feste |
|---|---|---|---|---|
| Bakskål, reflektor og kjøleflate | Aluminium | Metalltrykt grunn skål, eller laserskoren plate | Kvit innside, anodisert eller lakkert utside | Skrudd til vippeledd |
| Diffusor, variant 1 | Opal PMMA 3 mm | Skoren eller termoforma | Satinert | Fjørring i skålkanten |
| Diffusor, variant 2 | Strikka eller vove tekstil over tynn PMMA eller trådramme | Sydd strømpe | – | Trekt over kanten, kan takast av og vaskast |
| Stativ og fot | Stål: rundstål og plate | Bøygd og laserskoren | Pulverlakk | Skrudd |
| Handtak eller knott | Tre (PEFC eller FSC) eller messing | Dreia | Olja eller ubehandla | Skrudd, kan bytast |

- **Berekna:** om lag 1,2–1,3 kg med fotplate Ø 140 × 5 mm; lettare med mindre plate. Ei skive på Ø 250 mm gjev 491 cm² og om lag 1 950 cd/m² ved 300 lm. Metallråvare: 249 g aluminium og 738 g stål gjev 5,3 kg CO2e med globale snitt og 1,0 kg med CIRCAL og skrapbasert stål.
- **Kvifor:** låg luminans ved arbeidslysnivå, flatterande ansiktslys, og tekstilvarianten knyter seg til Tradition og Innvik. Modusen kan lesast av kva veg flata peikar.
- **Risiko:** størst volum av dei tre og mest krevjande å gjere kompakt. Tekstil nær LED må brann- og lystestast. PMMA er synleg i variant 1 og bør rammast inn av metall.

**TOLKING – samla.** Pakkane deler den same kjernen: aluminium som ber og kjøler, laus stålballast, messing som berøringspunkt og éin laus diffusor. Det gjer at berekraftshandlinga og reparasjonsarkitekturen kan vere felles for alle tre konsepta, medan diffusoren (glas, akryl eller tekstil) skil dei i uttrykk.

---

## Opne spørsmål

1. **Kvar og korleis blir Northern-lampene produserte i dag?** Land, leverandørar og metallprosessar står ikkje på produktsidene. Svaret avgjer kva som er truverdig i bedriftskontekst.
2. **Kva årsvolum og modell-levetid reknar Northern med?** Avgjer om sprøytestøyping og pressstøyping kan forsvarast.
3. **Transmisjon og spreiing i Northern sitt opalglas** er ukjent. Be om ein glasskjerm som prøve og mål med luxmeter. Same måling trengst for tekstil, papir og finer.
4. **Korleis er den gjenga glaskuppelen på Snowball Portable laga?** Gjenger i glaset eller ein pålimt metallring? Og kva toleransar held glasverket på diameter og tjukkleik?
5. **Verktøykostnad og toleransar for metalltrykking, djuptrekking, pressstøyping og glasformer** fann eg ikkje. Ekstern rettleiar frå Glamox/Luxo kan truleg gje storleiksorden.
6. **Kan CIRCAL og REDUXA kjøpast i formata ei lampe treng** (plate eller rondell til trykking, røyr, små profilseriar), og med kva minstekvantum? CIRCAL-sida nemner pressbolt og støypelegering, ikkje plate.
7. **Kva skjer med opalglas, PMMA og små lakkerte metalldelar i norsk EE-retur?** Avgjer om «resirkulerbar» kan brukast som argument, jf. åtvaringa i GRIP.
8. **Stabilitetskravet i EN 60598-2-4.** Eg meiner å hugse 6° og 15° skråplan; ikkje verifisert.
9. **Brannkrav til tekstil-, papir- og treskjermar nær LED** (glødetrådsprøve i EN 60598-1) er ikkje undersøkt.
10. **Finst PLEXIGLAS proTerra eller anna resirkulert PMMA i opal LED-kvalitet,** og med kva transmisjon? PolyCE fann i 2021 at resirkulert PMMA ikkje heldt til ei IR-linse.
11. **Resirkulert PC for diffusor** frå dei store råvareprodusentane er ikkje verifisert; Covestro si side var nede.
12. **CO2-tal per kg for glas, PMMA, PC, tekstil og tre** manglar. EPD-ar bør hentast før tala i punkt 5 blir brukte i ein samla klimarekneskap.
13. **Er forholdet mellom anodisert og pulverlakkert aluminium i omsmelting** slik eg har gått ut frå? Bør stadfestast av Hydro eller i faglitteratur.
14. **Norske eller nordiske metalltrykkjeri og pressstøyperi** er ikkje verifiserte.
15. **Vil Northern godta synlege gjenger, skruar og eit lok som kan opnast** som del av formspråket? Og vil dei godta synleg variasjon i resirkulert material?
16. **Avvik i Northern sine eigne data for Snowball Portable:** nettsida og bruksrettleiinga seier 158 lm, produktarket seier steg på 60, 120 og 200 lm. Ladetid er 4–5 timar i produktarket og 6–8 timar i bruksrettleiinga [N:snowball-portable-table-lamp], [N3], [N4].

---

## Kjelder

Alle nettkjelder er henta 12. november 2026 ved direkte oppslag. Nettsøk vart ikkje brukt (kvoten var oppbrukt).

### Lokale filer

- [F] `context/materialteknologiforelesning Lampe Northern H2026.md` – kursforelesing i materialteknologi (slide 1–47).
- [FS] `context/Flokk - Sustainability and Environment - AHO 24 Aug 2026.pdf` – sidetal viser til PDF-sider.
- [FR] `context/Flokk Designing for recycled plastics.pdf` – sidetal viser til PDF-sider.
- [G] `context/GRIP veileder for designere.pdf` – «Økodesign – en veileder i miljøeffektiv produktutvikling». Lesne sider: 1–4, 10–15, 34–39, 41–46, 61–66.
- `context/Nicoline Sander Design with sustainability 26 aug 2026.pdf` – s. 48 (seks prinsipp for ufullkomne material).
- `context/2 Endelig designbrief Northern.md` og `context/1 Prosjektbeskrivelse Modul 2 Bedriftssamarbeid GK5 H26.md` – ramme for oppgåva.
- `context/Erstatningsoppgave for studietur Ålesund.md` – liste over bedrifter på studieturen.
- `research/02-marknad.md` og `research/05-teknologi-og-komponentar.md` – kryssreferansar.
- Ikkje lesne: `context/Jane Penty Product Design and Sustainability ch. 2 p. 33-81.pdf` (berre innhaldslista; skanna, høyrer til berekraftsrapporten). Artikkelen «Innovate with Intention» og refleksjonsoppgåva er ikkje opna.

### Northern

- [N1] Kolleksjonssida for belysning: https://www.northern.no/collections/lighting
- [N3] Produktark, Snowball portable table lamp (PDF): https://www.northern.no/cdn/shop/files/Northern_product_sheet_-_Snowball_portable_table_lamp.pdf
- [N4] Bruksrettleiing, Snowball portable table (PDF): https://www.northern.no/cdn/shop/files/User_manual_-_Snowball_portable_table.pdf
- [N6] Material Care and Maintenance Guide: https://www.northern.no/en/pages/material-care-and-maintenance-guide
- [N7] About: https://www.northern.no/en/pages/about
- [N8] «Deep in the Fjord: Crafting Northern's Textiles»: https://www.northern.no/en/blogs/news/deep-in-the-fjord-the-textile-mill-behind-northern-s-signature-textile
- [N9] Produktomtalar for alle 56 lamper (produktfeed): https://www.northern.no/collections/lighting/products.json?limit=250
- [N:namn] Produktsider med spesifikasjonar, `https://www.northern.no/products/` + namn. Lesne: snowball-portable-table-lamp, snowball-portable-floor-lamp, snowball-table-lamp, birdy-table-lamp, birdy-swing-table-lamp, buddy-table-lamp, kin-table-lamp, salto-table-lamp, ombre-table-lamp, archive-table-lamp, tradition-table-lamp, balancer-mini-lamp, oslo-wood, acorn-pendant-lamp, dokka-pendant-lamp, over-me-ceiling-wall-lamp, blush-wall-lamp, me-dim-floor-lamp, glint-wall-lamp, diva-floor-lamp, unika-pendant-lamp, reveal-pendant-lamp, hall-wall-lamp, dahl-pendant-lamp-small, butterfly-wall-lamp, circle-pendant-lamp, ink-wall-lamp, heat-steel-pendant-lamp, say-my-name-pendant-lamp, balancer-floor-lamp, acorn-floor-lamp, moo-wall-lamp, glint-glass-opal-wall-lamp. Sida for gear-table-lamp hadde tomt spesifikasjonsfelt.

### Samanliknbare merke

- [L1] Louis Poulsen, PH 2/1 Portable: https://www.louispoulsen.com/en/catalog/professional/decorative-lighting/table/ph-21-portable
- [L2] Louis Poulsen, PH 5: https://www.louispoulsen.com/en/catalog/private/pendants/ph-5
- [H1] HAY, PC Portable faktaark: https://smow.de/pdf/hay-pc-portable-recycled-factsheet.pdf
- [FH1] Fritz Hansen, Clam Portable faktaark: https://www.smow.de/pdf/fritz-hansen-clam-portable-factsheet-en.pdf
- [MU1] Muuto, Ease Portable Lamp: https://www.muuto.com/product/Ease-Portable-Lamp--p41401/p41401/
- [M1] Marset, FollowMe spesifikasjonsark: https://www.marset.com/wp-content/uploads/lamparas/portable-lamps-table-lamps/followme-table/MARSET_FOLLOWME_Spec-sheet.pdf
- [AT1] &Tradition Flowerpot VP9, spesifikasjonsark (Monologue London, 2023): https://cdn.shopify.com/s/files/1/1051/0202/files/MNLG_AndTradition_Flowerpot_VP9_Spec_Sheet.pdf
- [HG1] Hadeland Glassverk, lamper: https://www.hadeland.com/en/collections/lamper
- [MG1] Magnor Glassverk: https://magnor.no/

### Prosessar

- [W-spin] Wikipedia, «Metal spinning»: https://en.wikipedia.org/wiki/Metal_spinning
- [W-dd] Wikipedia, «Deep drawing»: https://en.wikipedia.org/wiki/Deep_drawing
- [W-dc] Wikipedia, «Die casting»: https://en.wikipedia.org/wiki/Die_casting
- [W-tf] Wikipedia, «Thermoforming»: https://en.wikipedia.org/wiki/Thermoforming
- [W-gb] Wikipedia, «Glassblowing»: https://en.wikipedia.org/wiki/Glassblowing
- [W-sc] Wikipedia, «Slip casting»: https://en.wikipedia.org/wiki/Slipcasting
- [P-im] Protolabs Network (Hubs), Injection molding guide: https://www.hubs.com/guides/injection-molding/
- [FL-im] Formlabs, «How to estimate injection molding cost»: https://formlabs.com/blog/injection-molding-cost/
- [FL-tf] Formlabs, guide til termoforming: https://formlabs.com/blog/thermoforming/
- [P-sm] Protolabs, Sheet metal design guidelines: https://www.protolabs.com/services/sheet-metal-fabrication/design-guidelines/
- [P-mjf] Protolabs, Multi Jet Fusion: https://www.protolabs.com/services/3d-printing/multi-jet-fusion/
- [HY-ex] Hydro, ekstruderte profil: https://www.hydro.com/en/global/aluminium/products/extruded-profiles/ ; verktøy: https://www.hydro.com/en/global/aluminium/products/extruded-profiles/services/custom-made-dies/ ; designmanual, kapittel 4 (open del): https://www.hydroaluminiumdesign.com/en/manual/chapter4/

### Material, overflate og lågkarbon

- [IAI] International Aluminium Institute, Primary Aluminium Greenhouse Gas Emissions Intensity (2024): https://international-aluminium.org/statistics/greenhouse-gas-emissions-intensity-primary-aluminium/
- [HY-c] Hydro CIRCAL: https://www.hydro.com/en/global/aluminium/products/low-carbon-and-recycled-aluminium/low-carbon-aluminium/hydro-circal/
- [HY-r] Hydro REDUXA: https://www.hydro.com/en/global/aluminium/products/low-carbon-and-recycled-aluminium/low-carbon-aluminium/hydro-reduxa/
- [HY-rec] Hydro, aluminium recycling: https://www.hydro.com/en/global/aluminium/about-aluminium/aluminium-recycling/
- [HY-no] Hydro i Noreg: https://www.hydro.com/en/global/about-hydro/hydro-worldwide/europe/norway/
- [WS] worldsteel, Sustainability Indicators Report 2025: https://worldsteel.org/wider-sustainability/sustainability-indicators/
- [SSAB] SSAB Zero: https://www.ssab.com/en/fossil-free-steel/ssab-zero
- [OTK] Outokumpu Circle Green: https://www.outokumpu.com/en/products/circle-green
- [RO-led] Röhm, Technical Information PLEXIGLAS LED 0M200 SC (ref. 232-22): https://www.zenit.cz/public/media/Plasty/Zenit_PLEXIGLAS_LED-0M200SC_EN.pdf
- [RO-prod] PLEXIGLAS produktoversikt (proTerra, Satinice, 30 års garanti): https://www.plexiglas.de/en/products/plexiglas-proterra
- [W-pmma] Wikipedia, «Poly(methyl methacrylate)»: https://en.wikipedia.org/wiki/Poly(methyl_methacrylate)
- [W-pcarb] Wikipedia, «Polycarbonate»: https://en.wikipedia.org/wiki/Polycarbonate
- [W-mg] Wikipedia, «Milk glass»: https://en.wikipedia.org/wiki/Milk_glass
- [W-gr] Wikipedia, «Glass recycling»: https://en.wikipedia.org/wiki/Glass_recycling
- [W-an] Wikipedia, «Anodizing»: https://en.wikipedia.org/wiki/Anodizing
- [W-pc] Wikipedia, «Powder coating»: https://en.wikipedia.org/wiki/Powder_coating
- [W-pvd] Wikipedia, «Physical vapor deposition»: https://en.wikipedia.org/wiki/Physical_vapor_deposition

### Demontering og resirkulering

- [PolyCE] PolyCE (mars 2021), «Design for Recycling – Design from Recycling. Practical guidelines for designers», retningsliner for elektrisk og elektronisk utstyr (PDF, 77 sider; sidetal viser til trykte sidetal): https://www.polyce-project.eu/wp-content/uploads/2021/04/PolyCE-E-book-Circular-Design-Guidelines-2.pdf
- [EU-bat] Europakommisjonen, rettleiing om uttakbare og utskiftbare batteri, C/2025/214, punkt 2.1: https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:C_202500214

### Leverandørar

- [PLASTO] Plasto AS: https://plasto.no/
- [NCP] New Comfort Products AS: https://ncp.no/
- [MJOS] Mjøs Metallvarefabrikk AS: https://www.mjosmetall.no/
- [VESTRE] Vestre, sustainability: https://vestre.com/sustainability

### Oppslag som ikkje gav innhald

CustomPartNet (krev innlogging), Covestro Makrolon (HTTP 503), PEFC Norge (HTTP 403), Zafferano Poldina Pro (arket oppgjev ikkje material), Hydro sin designmanual kapittel 12 (krev innlogging), JRC sin rapport om reparasjonsskår (berre samandrag tilgjengeleg), og tre adresser til metalltrykkjeri som ikkje fanst.
