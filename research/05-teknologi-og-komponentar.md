# 05 – Teknologi og systemkomponentar

Research til konseptgjennomgangen 18. november. Målet er å avgrense det tekniske moglegheitsrommet for ei kompakt, flyttbar og eventuelt oppladbar lampe, slik at dei tre konsepta blir truverdige.

Merking i teksten: **FAKTA** = påstand med kjelde rett etter. **TOLKING** = mi vurdering av fakta. **ANTAKING** = føresetnad utan kjelde, må kontrollerast. **Berekna** = eige reknestykke, føresetnadene står ved sida.

Avgrensing: Nettsøk-kvoten for økta tok slutt undervegs. Punkt som ikkje vart verifiserte mot kjelde, er merkte «ikkje verifisert» og samla under «Opne spørsmål». Northern si eiga produktside (northern.no) svara med HTTP 429 på alle forsøk; Snowball-tala er difor henta frå forhandlarar og eitt søkjetreff. Faktasjekken 12.11.2026 fekk opna northern.no; Snowball-tala er etter det kontrollerte mot Northern si produktside, produktark og brukarrettleiing (sjå punkt 1 og «Faktasjekk» nedst).

---

## Kort oppsummering

1. **Batteriet avgjer lysnivået, ikkje LED-en.** Samanliknbare designlamper gjev 100–240 lm i 8–10 timar frå 11–19 Wh. Skal lampa gje reelt arbeidslys på batteri, fell brukstida med éi til to celler til 2,8–8 timar ved 300 lm og 1,4–4 timar ved 600 lm (berekna, sjå tabell 2).
2. **Ein hybrid er det realistiske svaret på briefen:** stemningslys på batteri, fullt arbeidslys når USB-C-leidningen står i. 5 V/1,5 A gjev om lag 7,5 W og 5 V/3 A gjev 15 W utan Power Delivery, men berre når kjelda melder det nivået. Lampa må lese CC-pinnen og elles halde seg til standardstraum (0,5–0,9 A).
3. **Batteriet er komponenten som døyr først.** Celledatablad lovar 500 syklusar til 80 %, medan LED-modular er oppgjevne til 60 000 timar (L70). Frå 18. februar 2027 krev EU at sluttbrukaren skal kunne byte batteriet med vanleg verktøy.
4. **To-kanals LED (varm + nøytral) løyser «saumlaus overgang»**, men krev mikrokontrollar og to drivarkanalar. Ein-kanals dim-to-warm-COB er enklare, men dekkjer berre 1800–3000 K og koplar farge til lysstyrke.
5. **Flimmer i kamera er ein reell risiko ved PWM-dimming.** Ein studie fann uakseptabel striping ved 900–1500 Hz og 50 % dimming. Vel straumregulert (analog) dimming eller høg PWM-frekvens, og test med webkamera.
6. **Blending handlar om lysande areal.** 300 lm bak ein opal diffusor krev om lag 320 cm² lysande flate for å halde seg rundt 3000 cd/m² (berekna). Opale deksel slepper gjennom 30–90 % av lyset, avhengig av kvalitet.
7. **Varme er handterleg under 6–8 W.** Ein kompakt metallkropp på 200–300 cm² kan kvitte seg passivt med varmen frå 3–6 W. 10–15 W krev 400–750 cm² eller ein stor skjerm som kjøleflate (berekna).
8. **Reparerbar arkitektur finst alt i marknaden.** Louis Poulsen sel batteri-, LED- og kretskortsett til Panthella Portable, og batteriet er ei 18650-celle. Faktaarket er motstridande om kven som kan byte cella (sluttbrukar éin stad, «qualified person» ein annan), og typeskiltet krev «listed battery». Northern oppgjev sjølv at Snowball Portable har utskiftbart batteri og utskiftbar LED-modul med pluggkontakt.

---

## Funn

### 1. Referanselamper: kva gjer marknaden i dag?

**FAKTA – Northern Snowball Portable.** Forhandlarar oppgjev 3 W LED, 2700 K, tre dimmesteg, IP44, USB-C-lading utan adapter, brukstid 8 timar, ladetid 4–5 timar, vekt 0,5 kg, skjerm i munnblåse opalglas og kropp i rustfritt stål, pris frå 189 € ([smow](https://www.smow.com/northern/snowball-portable-table-lamp.html)). Lysfluksen sprikjer mellom kjeldene: 240 lm ([smow](https://www.smow.com/northern/snowball-portable-table-lamp.html)), 200 lm med steg 60/120/200 lm ([David Village, produktark](https://www.davidvillagelighting.co.uk/productpdf/10002372)) og 158 lm med CRI > 90 ([northern.no](https://www.northern.no/en/products/snowball-portable-table-lamp), opna i faktasjekken 12.11.2026). Norsk utsalspris 1 790 kr, isolasjonsklasse III ([Kitchentime](https://www.kitchentime.com/brands/northern-lighting/snowball-portable-table-lamp-33-cm/)).

**FAKTA – Northern sine eigne kjelder (lagt til i faktasjekk).** Produktsida oppgjev «SMD chip, 3 W, 158 lm, 2700K, CRI >90», «Battery: 8 hours (at full power)», inngang 5,0 V – 3 A, tretrinns berøringsdimmar (10/50/100 %) med messingknott, 200 cm USB-C-kabel, IP44, pris 1 790 kr, kropp i rustfritt stål (pulverlakkert eller PVD-belagt), og under «Replaceable electronics»: «Replaceable LED module with push connector» og «Replaceable battery» ([northern.no](https://www.northern.no/en/products/snowball-portable-table-lamp)). Produktarket seier derimot 60/120/200 lm, brukstid 8–12 timar, ladetid 4–5 timar, 0,5 kg, høgd 33 cm, glaskule Ø 7 cm og fot 9 cm, klasse III og energiklasse F for lyskjelda. Reservedelslista der har glaskule, LED-panel, diffusorlinse, ladekabel og USB-deksel, men ikkje batteri ([Northern, produktark](https://www.northern.no/cdn/shop/files/Northern_product_sheet_-_Snowball_portable_table_lamp.pdf?v=11906401054735407144)). Brukarrettleiinga seier 158 lm, 3,7 V Li-ion-batteri utan oppgjeven kapasitet, 6–8 timar ladetid, «Only use the included battery», og at berre produsent, serviceagent eller tilsvarande kvalifisert person skal reparere og byte skadde delar ([Northern, brukarrettleiing](https://www.northern.no/cdn/shop/files/User_manual_-_Snowball_portable_table.pdf?v=10090650407803861463)). **TOLKING:** Northern sine eigne tal sprikjer (158 mot 200 lm, 10/50/100 % mot 60/120/200 lm, 4–5 mot 6–8 timar ladetid). Batteriet er utskiftbart ifølgje produktsida, men det er ikkje dokumentert at sluttbrukaren kan byte det sjølv, og batteriet står ikkje på reservedelslista.

**FAKTA – Louis Poulsen Panthella 160 Portable V3.** 2,5 W integrert LED, 2700 K. 150 lm ved 100 %, 50 lm ved 33 %, 15 lm ved 10 %. Brukstid 8,5 / 25,5 / 79 timar. Éi Li-ion 18650-celle på 3100 mAh (3,7 V på typeskiltet), «rechargeable and replaceable», finst som reservedel. Faktaarket er motstridande om kven som kan byte batteriet: produktinformasjonen seier «Battery replaceable by qualified person», tabellen seier «Battery change possible by end-consumer», og typeskiltet seier «Replaceable with listed battery only» (retta i faktasjekk). Batterilevetid 500 ladesyklusar til 70 % kapasitet. LED-levetid L70 = 60 000 timar; LED-sett og kretskort finst som reservedelar, bytast av elektrikar. Ladetid 5 timar via USB-C, adapter (min. 1,5 A) følgjer ikkje med. IP44, klasse III, 0,4 kg, 160 × 241 mm. Berøringsbrytar i toppmutteren. Skjerm og diffusor i sprøytestøypt polykarbonat ([Louis Poulsen faktaark V3](https://smow.fr/pdf/louis-poulsen-panthella-160-v3-factsheet.pdf)).

**FAKTA – same faktaark, versjonshistorikk.** V2 hadde USB-C og Qi-lading og 3 × AA NiMH-batteri. V3 har «USB-C charging – no QI charging», og brukstida ved 100 % auka frå 5 til 8,5 timar ([Louis Poulsen faktaark V3](https://smow.fr/pdf/louis-poulsen-panthella-160-v3-factsheet.pdf)).

**FAKTA – &Tradition Flowerpot VP9.** 104 lm (ikkje stadfesta: lysfluks står ikkje i &Tradition sine eigne dokument), 3 W LED-kort, CRI > 80 (retta frå > 90 etter &Tradition sitt faktaark), 2700 K, 5200 mAh Li-ion (ikkje stadfesta: kapasitet står ikkje i &Tradition sine eigne dokument), 10 timar brukstid, 8 timar ladetid, tre nivå (100/50/20 % i bruksrettleiinga, 100/70/40 % i faktaarket), lading 5 V/2 A via magnetisk ladekabel med USB-A (retta frå Micro-USB), batteri og LED-eining selde som reservedel, IP44, klasse III, 0,8 kg ([&Tradition, faktaark](https://www.assetslibrary.com/asset/586904ba-bd72-495c-bea8-38a9ae347f78/ATD_Product-Fact-Sheets_Flowerpot_VP9.pdf), [&Tradition, bruksrettleiing](https://www.assetslibrary.com/asset/c0a85983-134f-4603-9063-92a837a1b931/ATD_Instruction-Manuals_Flowerpot_VP9.pdf); lumen og mAh frå [Architonic](https://architonic.com/en/product/-tradition-flowerpot-vp9-grey-beige/20200625), [Connox](https://www.connox.com/categories/lighting/table-lamps/tradition-flowerpot-rechargeable-battery-table-lamp-vp9.html) via søkjetreff).

**FAKTA – Zafferano Poldina Pro.** 2,2 W, 188 lm, 3000 K, CRI > 80, 2 × 18650 à 2200 mAh «included – replaceable», ladetid 6 timar, kontakt-ladebase følgjer med, berøringsdimmar, passiv kjøling, «lamp life about 450 charges», batteripakke som tilbehør ([Zafferano spesifikasjonsark](https://cdn.shopify.com/s/files/1/0591/2484/2705/files/Specification_Sheet_Poldina_Pro.pdf)).

**FAKTA – videolys til skrivebord (ikkje stemningslamper).** Logitech Litra Glow: 250 lm, 2700–6500 K, CRI 93, USB-driven, 90,5 × 90,5 × 27,5 mm, 99 g ([Logitech](https://support.logi.com/hc/en-gb/articles/4418106727447-Specification-Litra-Glow)). Elgato Key Light Air: 1400 lm, 2900–7000 K, 80 LED-ar som lyser inn frå kanten (edge-lit), inntil 25 W, 205 × 205 × 35 mm, 550 g ([Elgato](https://help.elgato.com/hc/it/articles/360038093012-Key-Light-Air-Specifiche-Tecniche); via søkjetreff) (ikkje stadfesta: sida gav HTTP 403 i faktasjekken). BenQ ScreenBar: krev USB-forsyning på 5 V/1 A, asymmetrisk optikk som held lyset unna skjermen, CRI ≥ 95, 2700–6500 K ([BenQ](https://www.benq.com/en-us/lighting/monitor-light/screenbar.html); via søkjetreff).

**Berekna – systemutbytte i referanselampene** (lumen ut av lampa per watt frå batteriet; føreset at heile den nominelle kapasiteten blir brukt):

| Lampe | Energi (Wh) | Snitteffekt | Systemutbytte |
|---|---|---|---|
| Panthella V3 | 3,1 Ah × 3,7 V = 11,5 (typeskiltet seier 3,7 V; retta frå 3,6 V) | 11,5 / 8,5 h = 1,35 W | 150 / 1,35 = 111 lm/W |
| Flowerpot VP9 | 5,2 Ah × 3,7 V = 19,2 (ANTAKING: 3,7 V nominelt; mAh ikkje stadfesta) | 19,2 / 10 h = 1,92 W | 104 / 1,92 = 54 lm/W (lumen ikkje stadfesta) |
| Poldina Pro | oppgjeve 2,2 W | 2,2 W | 188 / 2,2 = 85 lm/W |
| Snowball Portable | ukjend kapasitet (3,7 V Li-ion) | oppgjeve 3 W | 158–200 / 3 = 53–67 lm/W med Northern sine eigne tal; 80 lm/W med 240 lm frå smow |

**TOLKING.** Reelle designlamper med opal skjerm ligg på om lag 55–110 lm/W på systemnivå. Eg brukar 80 lm/W som hovudføresetnad vidare, med 60 og 110 lm/W som yttergrenser. Ingen av dei stemningsskapande referansane kjem over 250 lm. Arbeidslys på batteri er altså eit område marknaden ikkje dekkjer, og det har ein fysisk grunn (sjå punkt 4).

### 2. Lyskjelder

**FAKTA frå emnet.** Teknikkarket skil mellom LED-pære (utskiftbar lyskjelde med sokkel), LED-modul (LED-ar på kretskort), COB (mange små brikker tett på éi flate) og LED-stripe (Teknisk forklaring.pdf, s. 1). Lysutbytte er lysfluks delt på tilført effekt, i lm/W (Lysteori.md, slide 5).

| Type | Lysutbytte (kjelde) | Levetid | Spenning | Merknad |
|---|---|---|---|---|
| Mid-power SMD på MCPCB (Samsung LM301B, 3,0 × 3,0 mm) | 220 lm/W ved 65 mA, 5000 K, CRI 80 ([Samsung](https://led.samsung.com/about-us/news-events/news/news-detail-37); via søkjetreff). CRI 90, 3000 K: 28–32 lm ved 65 mA ([Samsung](https://led.samsung.com/lighting/mid-power-leds/3030-leds/lm301b); via søkjetreff) (ikkje stadfesta: begge Samsung-lenkjene blir vidaresende til framsida per 12.11.2026) | Ikkje funne for CRI 90 | ca. 2,7 V per LED | Berekna: 38,8 lm / 220 lm/W = 0,176 W per LED, så CRI 90/3000 K gjev 28–32 / 0,176 ≈ 160–180 lm/W |
| COB (Bridgelux V-serien) | 171–182 lm/W ved 3000 K, CRI 90 ([datablad-kopi](https://static.chipdip.ru/lib/318/DOC042318248.pdf)); HD-variant 137 lm/W ([Bridgelux DS1360](https://www.bridgelux.com/sites/default/files/2024-09/ds1360_gen_8_v6_hd_array_data_sheet_202409_rev_b.pdf)); via søkjetreff | Ikkje henta | 17–36 V | Lita lysande flate, høg luminans, treng optikk eller skjerming |
| Dim-to-warm-COB (Bridgelux Vesta 9 mm) | 115 lm/W ved 3000 K (350 mA, 17,0 V, 6,0 W); 104 lm/W ved 1800 K (14 mA, 0,2 W); CRI ≥ 90 ([LED-Tech](https://www.led-tech.de/en/Bridgelux-Vesta-COB-Dim-To-Warm-6W-CRI90-1800K-3000K-LES-9mm)) | Ikkje henta | 11–17 V | 12 × 15 × 1,7 mm, 4,96 € netto per stk. i enkeltkjøp |
| Retrofit glaslampe E14 (Philips MASTER Value LEDcandle) | 138 lm/W: 470 lm, 3,4 W, 2700 K, CRI 90, energiklasse D ([Signify](https://www.signify.com/en-gb/prof/led-lamps-and-tubes/led-candles-and-lustres/philips-master-value-glass-led-candles-and-lustres/929003059502_EU/product)) | 15 000 timar (L70) | 220–240 V | 14 g, dimbar berre med visse dimmarar |
| Integrert modul i portabel lampe (Panthella V3) | systemnivå 111 lm/W (berekna over) | 60 000 timar (L70) ([Louis Poulsen](https://smow.fr/pdf/louis-poulsen-panthella-160-v3-factsheet.pdf)) | celle 3,7 V | LED-sett finst som reservedel |

**TOLKING – retrofit kontra integrert.** Ei sokkelpære kan bytast utan verktøy av kven som helst, og er slik det mest reparerbare alternativet. Men E14/E27/GU10 er nettspenning (220–240 V i databladet over), så dei passar ei kabla lampe, ikkje ei batterilampe på 3,6–5 V. Levetida er òg ein firedel av ein integrert modul (15 000 mot 60 000 timar). For ei batterilampe er ein eigen LED-modul med kontakt det realistiske valet. Om det finst gode lågvolts sokkellyskjelder (G4/GU5.3, 12 V) med CRI 90 er **ikkje undersøkt**.

**FAKTA – Zhaga.** Zhaga-konsortiet har 26 «Books» som standardiserer grensesnitt for LED-modular. Mellom anna: Book 3 og 11 (spotmodular 50 og 35 mm), Book 10 (modular for spotlys), Book 12 (COB-matriser og haldarar), Book 7 (lineære og kvadratiske modular), Book 14 (lineære modular med sokkel), Book 21 (lineære sokkelmodular for SELV) ([Zhaga](https://www.zhagastandard.org/books/overview/)). Book 14 har cap/holder for verktøyfritt byte og er teken opp som IEC 63356-1 ([Zhaga Book 14](https://www.zhagastandard.org/books/overview/socketable-linear-lles-14.html); via søkjetreff). Book 10 dekkjer runde modular som blir skrudde til kjøleflata i armaturen ([IEC PAS 63324](https://webstore.iec.ch/publication/67189); via søkjetreff).

**TOLKING.** Zhaga er laga for profesjonelle armaturar (spot, lineær, utandørs). Ingen av bøkene er tilpassa ei lita batterilampe. Det mest relevante er Book 12-prinsippet: ein standard COB i ein haldar med skruar og fjørkontaktar. Det gjev utskiftbar lyskjelde utan lodding, og haldaren er ein hyllevare.

**FAKTA – økodesign.** Forordning (EU) 2019/2020 artikkel 4 krev at lyskjelder og separate drivarar skal kunne bytast «with the use of common available tools and without permanent damage to the containing product», med mindre produsenten gjev ei teknisk grunngjeving. Om lyskjelda kan bytast eller ikkje, skal stå på emballasjen, minst som piktogram ([legislation.gov.uk, art. 4](https://www.legislation.gov.uk/eur/2019/2020/article/4/adopted)).

**FAKTA – unntak for batteridrivne produkt (lagt til i faktasjekk).** Forordninga gjeld ikkje «light sources and separate control gears in battery-operated products», med «desk lamps operating only on batteries» som eitt av døma (vedlegg III punkt 2 bokstav c). «Battery-operated» er definert som eit produkt som berre går på likestraum frå ei kjelde i produktet, «without being connected directly or indirectly to the mains electricity supply» (vedlegg I punkt 44). Forordninga gjeld dessutan berre lyskjelder med lysfluks mellom 60 og 82 000 lm (artikkel 2) ([EUR-Lex, konsolidert versjon 01.09.2021](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02019R2020-20210901)). **TOLKING:** Ei lampe som berre lyser på batteri, fell utanfor forordninga. Ei hybridlampe som òg skal lyse medan ho er kopla til ein USB-ladar, er indirekte kopla til nettet og fell etter ordlyden truleg innanfor, slik at artikkel 4 gjeld (ikkje stadfesta mot rettleiing frå Kommisjonen). Northern oppgjev energiklasse F for lyskjelda i Snowball Portable (punkt 1), noko som tyder på at Northern sjølv reknar lyskjelda som omfatta av lyskjelderegelverket.

### 3. Tunable white og dim-to-warm

**FAKTA.** Dim-to-warm tyder at lyset blir varmare når det blir dimma (Teknisk forklaring.pdf, s. 1). Tunable white blandar lys frå to LED-strengar med ulik fargetemperatur, slik at styrke og farge kan styrast uavhengig. Dim-to-warm har eitt handtak: styrke ([Acuity/eldoLED](https://insights.acuitybrands.com/eldoled-blog/article-interoperable-systems-for-dynamic-white-lighting); via søkjetreff).

**FAKTA – to måtar å byggje det på** ([Cree LED referansedesign CLD-AP291](https://downloads.cree-led.com/files/da/x/Tunable-White-COB-Dim-to-Warm.pdf)):
- *Passiv:* ein motstand i serie med den varme strengen og diodar i serie med den kalde. Få delar og låg kostnad, men lite kontroll over kurva; straumdelinga kunne berre varierast mellom 40 og 75 %.
- *Digital:* straummåling, operasjonsforsterkar, mikrokontrollar og to MOSFET-ar som PWM-styrer kvar streng etter ein oppslagstabell. Kvar streng kan gå frå 0 til 100 %, og kurva kan programmerast fritt. Døme-COB-en har 4000 K og 1800 K, begge CRI 90.

**FAKTA.** Ein ein-kanals dim-to-warm-COB (Bridgelux Vesta) går frå 3000 K ved 350 mA til 1800 K ved 14 mA på to tilkoplingar ([LED-Tech](https://www.led-tech.de/en/Bridgelux-Vesta-COB-Dim-To-Warm-6W-CRI90-1800K-3000K-LES-9mm)).

| Løysing | Kanalar | Styring | Fargeområde | Kompleksitet |
|---|---|---|---|---|
| Fast 2700 K + dimming | 1 | éin drivar | fast | lågast |
| Dim-to-warm-COB | 1 | éin drivar | 1800–3000 K, låst til styrke | låg |
| Passiv to-streng | 1 inn | motstand + diodar | avgrensa | låg, men unøyaktig |
| Digital to-kanal | 2 | MCU + 2 MOSFET eller 2 drivarar | t.d. 1800–4000 K, fritt | høgast: fastvare, kalibrering, fleire feilkjelder |

**TOLKING.** Briefen ber om «varm fargetemperatur» og «saumlaus overgang mellom stemningslys og arbeidslys». Ein digital to-kanal med t.d. 2200 K og 3500–4000 K kan gje både glødelampekurve i stemningsmodus og nøytralt lys i arbeids- og møtemodus. Prisen er ein mikrokontrollar og fastvare, som gjer reparasjon vanskelegare for andre enn leverandøren. Eit enklare alternativ er to fysisk skilde lyskjelder (éi varm, indirekte og éi nøytral, retta) med kvar sin brytar: då treng ein ingen fargeblanding, og modusen blir synleg i forma.

### 4. Batteri

**FAKTA – celletypar.**

| Kjemi | Nominell spenning | Spesifikk energi | Sykluslevetid | Termisk rømming | Kjelde |
|---|---|---|---|---|---|
| NMC | 3,6–3,7 V | 150–220 Wh/kg | 1000–2000 | ca. 210 °C | [Battery University BU-205](https://batteryuniversity.com/article/bu-205-types-of-lithium-ion) |
| LCO | 3,6 V | 150–200 Wh/kg | 500–1000 | ca. 150 °C | same |
| LFP (LiFePO4) | 3,2–3,3 V | 90–120 Wh/kg | 2000 og meir | ca. 270 °C | same |

**FAKTA – konkrete celler.**
- Samsung INR21700-50E: min. 4900 mAh, 3,63 V nominelt, ladespenning 4,2 V, standardlading 2450 mA i 4 timar, minst 80 % av merkekapasiteten etter 500 syklusar, maks 69,5 g, maks Ø 21,25 × 70,80 mm, lading berre mellom 0 og 45 °C ([Samsung SDI datablad](https://shop.aceongroup.com/cdn/shop/files/RLII-CSI-1618_Samsung_50E_DATASHEET.pdf)). Berekna: 4,9 Ah × 3,63 V = 17,8 Wh, 256 Wh/kg.
- Samsung INR18650-35E: 3500 mAh nominelt, 3350 mAh minimum, 3,6–3,7 V, spesifisert vekt 48 ± 1 g ([lygte-info](https://lygte-info.dk/review/batteries2012/Samsung%20INR18650-35E%203500mAh%20%28Pink%29%20UK.html); via søkjetreff). Berekna: ca. 12,2 Wh.
- Pouch-celler (Li-polymer): ikkje undersøkt med kjelde. **TOLKING:** dei har fritt format, men ingen standardmål og ingen stiv kappe. Det gjer brukarbyte og reservedelsforsyning vanskelegare enn med sylindriske standardceller.
- AA NiMH: Panthella V2 brukte 3 × AA NiMH som sluttbrukaren kunne byte ([Louis Poulsen](https://smow.fr/pdf/louis-poulsen-panthella-160-v3-factsheet.pdf)). Berekna: 3 × 2,0 Ah × 1,2 V ≈ 7,2 Wh (ANTAKING: 2000 mAh per celle).

**FAKTA – kva som slit batteriet** ([Battery University BU-808](https://batteryuniversity.com/article/bu-808-how-to-prolong-lithium-based-batteries)):
- Utladingsdjupn: NMC toler om lag 300 syklusar ved 100 % utlading, 600 ved 60 % og 1000 ved 40 % (til 70 % kapasitet).
- Ladespenning: 4,20 V gjev 300–500 syklusar og 100 % kapasitet; 4,06 V gjev 600–1000 syklusar og 81 % kapasitet; 4,00 V gjev 850–1500 syklusar og 73 %.
- Lagring fulladd: ved 25 °C er 80 % att etter eitt år på 100 % lading, mot 96 % ved 40 % lading. Ved 40 °C er tala 65 % og 85 %.

**TOLKING.** Ei arbeidslampe som står med leidningen i heile tida, held batteriet fulladd og lunkent. Det er den verste driftsforma for cella. Tre tiltak følgjer direkte av tala: (1) ladegrense rundt 4,05 V, som om lag doblar syklustalet mot 19 % mindre kapasitet, (2) straumveg som driv LED-en direkte frå USB når leidningen står i, og (3) plassere cella i foten, unna LED-varmen. Punkt 1 er ein konkret kandidat til berekraftshandlinga.

**Berekna – kor lenge varer batteriet i kalenderår?** 500 syklusar / 365 per år = 1,4 år ved full syklus kvar dag. 500 / (2 per veke × 52) = 4,8 år ved to syklusar i veka. LED-modulen varer 60 000 timar; ved 8 timar per dag er det 20 år. Batteriet må altså bytast fleire gonger i levetida til lampa.

**FAKTA – tryggleiksstandardar.** IEC 62133-2 set tryggleikskrav og testar for berbare, forsegla, oppladbare litiumceller og -batteri ved tiltenkt bruk og pårekneleg feilbruk; gjeldande utgåve er 2017 med tillegg A1:2021. UN 38.3 gjeld transport, IEC 62133-2 gjeld batteripakken som produkt ([batterydesign.net](https://www.batterydesign.net/legislation-rules-and-regulations/iec-62133-2/), [Dan Energy](https://www.danenergy.com/blog-posts/battery-pack-certification-europe); via søkjetreff). Innhaldet i UN 38.3-testane T1–T8 er **ikkje verifisert** mot primærkjelde.

**FAKTA – EUs batteriforordning (EU) 2023/1542, artikkel 11.** Gjeld frå 18. februar 2027. Berbare batteri (forsegla, 5 kg eller mindre, ikkje for industri) i produkt skal kunne takast ut og bytast av sluttbrukaren. Det skal gå med verktøy som er i vanleg handel; spesialverktøy er berre lov dersom det følgjer gratis med; varme og løysemiddel er ikkje lov. Batteriet skal vere tilgjengeleg som reservedel i minst fem år etter at siste eining av modellen er sett på marknaden. Programvare skal ikkje hindre byte. Produktet skal følgje med instruksjonar og tryggleiksinformasjon om bruk, uttak og byte av batteriet, og dei skal liggje permanent tilgjengeleg på nett. Kravet gjeld heile batteriet, ikkje enkeltceller. Ordlyden er stadfesta mot forordningsteksten, og artikkel 11 står uendra med verknad frå 18. februar 2027 i den konsoliderte versjonen av 13.08.2026 ([EUR-Lex, artikkel 3, 11 og 96](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02023R1542-20260813), [Compliance Gate](https://www.compliancegate.com/removable-and-replaceable-battery-requirements-european-union/), [Cooley om Kommisjonen si rettleiing](https://products.cooley.com/2025/02/13/european-commission-publishes-guidance-on-eu-batteries-regulation-removability-requirements/), [rettleiinga C/2025/214](https://eur-lex.europa.eu/eli/C/2025/214/oj/eng)). Unntaka gjeld mellom anna apparat som er spesifikt konstruerte for hovudsakleg bruk i vått miljø og er meinte å kunne vaskast eller skyljast (barbermaskiner, tannbørstar). Cooley les rettleiinga slik at IP-klasse åleine ikkje er nok grunngjeving ([Cooley](https://products.cooley.com/2025/02/13/european-commission-publishes-guidance-on-eu-batteries-regulation-removability-requirements/)) (ikkje stadfesta: den kunngjorde teksten i C/2025/214 seier bokstavleg at IP-klassen åleine «is considered as sufficient», truleg ein redaksjonsfeil sidan setninga framfor peikar motsett veg; bruk ikkje dette som sitat). Delegert forordning (EU) 2026/1770 av 14. juli 2026, kunngjord 22. oktober 2026, la til seks unntakskategoriar: visse kroppsborne einingar (t.d. smartklokker), elektriske leiker med oppladbart batteri (til 31. juli 2030), trådlause steiketermometer, utstyr for eksplosjonsfarlege område, kroppsborne system for medisindosering og telematikkeiningar på landbruks- og anleggsmaskiner. Lamper er ikkje med, og dei nye unntaka gjeld berre når dei trengst for tryggleiken til brukar og apparat ([EUR-Lex, 2026/1770](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32026R1770); stadfesta i faktasjekk) ([Lovguiden](https://www.lovguiden.dk/en/det-offentlige/eur-lex-eu-tidende/2026-10-22-seks-nye-undtagelser-fra-krav-om-udskiftelige-batterier-i-eu), [europalov.no](https://europalov.no/rettsakt/batteriforordningen-2023-utfyllende-bestemmelser-om-unntak-for-muligheten-til-fjerne-erstatte/id-34790); via søkjetreff).

**TOLKING.** Ei bordlampe til innebruk har ingen grunn til unntak. Eit konsept som blir lansert etter februar 2027, må ha batteri som brukaren sjølv kan byte. Plikta ligg på den som set produkt med berbare batteri på marknaden frå den datoen, så ho gjeld truleg òg nye einingar av eksisterande modellar som Snowball Portable (tolking lagt til i faktasjekk; ikkje stadfesta mot Kommisjonen si rettleiing om «placing on the market»). Standard sylindriske celler i ein haldar, bak eit lok med éin skrue eller myntspor, oppfyller kravet til uttak med vanleg verktøy med god margin. Påstanden om at løysinga òg gjer reservedelen uavhengig av leverandøren, er ikkje dekt av kjeldene (ikkje stadfesta): celledatabladet til Samsung føreset vernefunksjon i batteripakken, Kommisjonen si rettleiing krev at eit kompatibelt batteri ikkje skal utgjere nokon tryggleiksrisiko, og Louis Poulsen («listed battery only»), &Tradition og Northern («Only use the included battery») viser alle til sitt eige batteri. Kva celle brukaren trygt kan setje inn, må avklarast med rettleiar.

#### Tabell 2: lumen → effekt → batteri → brukstid

Reknestykke:
- Effekt: P = Φ / η, der η er systemutbytte frå batteri til lys ut av lampa. Hovudføresetnad η = 80 lm/W (ANTAKING, grunngjeve i punkt 1).
- Brukbar energi: E = 0,85 × nominell energi (ANTAKING: margin for utladingsgrense og aldring).
- Brukstid: t = E / P.
- Pakkar: 1 × 18650 = 3,4 Ah × 3,6 V = 12,2 Wh → 10,4 Wh brukbar. 2 × 18650 = 24,5 → 20,8 Wh. 1 × 21700 = 4,9 Ah × 3,63 V = 17,8 → 15,1 Wh. 2 × 21700 = 35,6 → 30,2 Wh. 4 × 21700 = 71,1 → 60,5 Wh.

| Lysfluks | Effekt ved 80 lm/W | 1 × 18650 (48 g) | 2 × 18650 (96 g) | 1 × 21700 (70 g) | 2 × 21700 (139 g) | 4 × 21700 (278 g) |
|---|---|---|---|---|---|---|
| 100 lm | 100/80 = 1,25 W | 8,3 t | 16,6 t | 12,1 t | 24,2 t | 48 t |
| 300 lm | 3,75 W | 2,8 t | 5,5 t | 4,0 t | 8,1 t | 16 t |
| 600 lm | 7,5 W | 1,4 t | 2,8 t | 2,0 t | 4,0 t | 8,1 t |
| 1000 lm | 12,5 W | 0,8 t | 1,7 t | 1,2 t | 2,4 t | 4,8 t |

Følsemd for systemutbytte (1 × 21700, 15,1 Wh brukbar):

| Lysfluks | 60 lm/W | 80 lm/W | 110 lm/W |
|---|---|---|---|
| 100 lm | 9,1 t | 12,1 t | 16,6 t |
| 300 lm | 3,0 t | 4,0 t | 5,5 t |
| 600 lm | 1,5 t | 2,0 t | 2,8 t |
| 1000 lm | 0,9 t | 1,2 t | 1,7 t |

Kontroll mot røynda: Panthella V3 gjev 150 lm i 8,5 timar frå 11,5 Wh ([Louis Poulsen](https://smow.fr/pdf/louis-poulsen-panthella-160-v3-factsheet.pdf)). Modellen gjev 150 lm → 1,36 W ved 110 lm/W → 7,1 timar med 85 % brukbar energi. Same storleiksorden; modellen er litt forsiktig.

**TOLKING.** Ein full arbeidsdag (8 timar) med 300 lm krev 2 × 21700. Ein arbeidsdag med 600 lm krev 4 × 21700 (278 g celler, 71 Wh). Ei kompakt lampe med éi celle klarer 100–150 lm ein heil dag, eller 300 lm i eit par møte.

### 5. Lading og drift med leidning

**FAKTA – USB-C utan Power Delivery.** Ei lampe (sink) melder seg med 5,1 kΩ nedtrekk på kvar CC-pinne. Kjelda fortel med opptrekksmotstanden kor mykje straum som er lov: standard USB (500/900 mA), 1,5 A eller 3 A ved 5 V, altså 7,5 W eller 15 W. Lampa må rette seg etter det kjelda tilbyr, og må difor måle spenninga på CC-pinnen: under om lag 0,66 V gjeld standardstraum, 0,66–1,23 V tillèt 1,5 A og over 1,23 V tillèt 3 A. Ei lampe med berre motstandar, utan CC-måling, har berre lov til å trekkje standardstraum; utan BC1.2-deteksjon er det 0,5 A frå ein USB 2.0-port (presisert i faktasjekk) ([Monolithic Power](https://media.monolithicpower.cn/mps_cms_document/u/s/usb-type-c-charging-connectors-design-optim-interop_r1.0.pdf), [Digi-Key forum](https://forum.digikey.com/t/simple-way-to-use-usb-type-c-to-get-5v-at-up-to-3a-15w/7016); via søkjetreff).

**FAKTA – USB Power Delivery.** Før revisjon 3.1 var grensa 100 W (20 V, 5 A). Revisjon 3.1 gjev inntil 240 W med faste spenningar på 28, 36 og 48 V ([USB-IF](https://www.usb.org/usb-charger-pd)).

**FAKTA – straumveg (power path).** Ladekretsar med dynamisk straumvegstyring, t.d. TI BQ24074, forsyner systemet og ladar batteriet samstundes og uavhengig av kvarandre. Kretsen har valbar inngangsgrense på 100 eller 500 mA for USB og ladestraum inntil 1,5 A ([Texas Instruments](https://www.ti.com/product/BQ24074)). Med slik styring får systemet straum straks kjelda er kopla til, sjølv om batteriet er tomt ([MPS](https://www.monolithicpower.com/en/power-path-management-in-charger-ics/); via søkjetreff).

**Berekna – ladetid** (energi / (ladeeffekt × 0,85), utan avsluttande konstantspenningsfase):

| Pakke | 5 V/0,5 A (2,5 W) | 5 V/1,5 A (7,5 W) | 5 V/3 A (15 W) |
|---|---|---|---|
| 1 × 18650 (12,2 Wh) | 5,8 t | 1,9 t | 1,0 t |
| 1 × 21700 (17,8 Wh) | 8,4 t | 2,8 t | 1,4 t (cella er spesifisert for 4 t standardlading) |
| 2 × 21700 (35,6 Wh) | 16,8 t | 5,6 t | 2,8 t |

Referanselampene ladar roleg: 5 timar for 11 Wh (Panthella), 6 timar for 16 Wh (Poldina), 8 timar for 19 Wh (Flowerpot); kjelder i punkt 1.

**Berekna – lys med leidningen i.** 5 V/1,5 A = 7,5 W → 600 lm ved 80 lm/W. 5 V/3 A = 15 W → inntil 1200 lm dersom alt går til lys, om lag 1000 lm med margin. **TOLKING:** lampa kan altså ha eit høgare toppnivå kabla enn på batteri. Dimensjoner for 7,5 W som normalnivå, sidan lampa ikkje kan krevje 3 A av ein vilkårleg ladar. Heller ikkje 1,5 A er garantert (retta i faktasjekk): ei kjelde som berre melder standardstraum, t.d. ein eldre USB-A-port med overgangskabel, gjev 0,5–0,9 A (2,5–4,5 W). Lampa må då dimme ned eller hente resten frå batteriet.

**FAKTA – trådlaus lading (Qi).** Baseline Power Profile gjev inntil 5 W, Extended Power Profile inntil 15 W, og Qi2 har ein magnetisk profil (MPP) på 15 W ([Granite River Labs](https://www.graniteriverlabs.com/en-us/technical-blog/2024-qi2-technical-compliance); via søkjetreff). Standarden har framandlekam-deteksjon for å hindre oppvarming av metall i feltet ([WPC, Qi FOD](https://www.wirelesspowerconsortium.com/media/klfjiwfh/qi-v13-fod.pdf); via søkjetreff). Ein laboratorietest frå 2016 målte om lag 63 % verknadsgrad trådlaust mot 81 % med leidning ([Allion](https://www.allion.com/?p=5581); via søkjetreff). Ein nyare forbrukartest oppgjev 60–80 % trådlaust mot 85–95 % med kabel, utan å namngje studiane ([Galaxus](https://www.galaxus.de/en/page/qi2-test-revelations-iphone-charges-faster-with-the-competition-40668); via søkjetreff). Louis Poulsen fjerna Qi frå Panthella Portable i V3 ([Louis Poulsen](https://smow.fr/pdf/louis-poulsen-panthella-160-v3-factsheet.pdf)).

**Berekna.** Å fylle 17,8 Wh krev om lag 19,8 Wh frå veggen ved 90 % verknadsgrad og 25,4 Wh ved 70 %. Trådlaus lading kostar altså rundt 30 % meir energi per lading i dette dømet.

**FAKTA – ladebase med kontaktpunkt.** Poldina Pro blir levert med kontakt-ladebase, og det finst ein base for seks lamper ([Zafferano](https://cdn.shopify.com/s/files/1/0591/2484/2705/files/Specification_Sheet_Poldina_Pro.pdf)).

**FAKTA – kommande krav til ladeutstyr.** Forordning (EU) 2025/2052 gjeld eksterne straumforsyningar, trådlause ladarar og ladeplater, og USB-C-kablar. Dei fleste krava gjeld frå 14. desember 2028. Straumforsyningar skal ha minst éin USB-C-port, og trådlause ladeplater får kviletak på 0,50 W ([EUR-Lex](https://eur-lex.europa.eu/eli/reg/2025/2052), [Nemko](https://www.nemko.com/blog/ecodesign-2025/2052-is-coming-what-makers-of-power-accessories-need-to-change-before-december-2028); via søkjetreff).

**TOLKING.** USB-C med to 5,1 kΩ-motstandar er den enklaste, billegaste og mest reparerbare ladeløysinga, og ho fungerer med ladarar brukaren alt har. Motstandane åleine held likevel berre til lading med standardstraum; skal lampa trekkje 1,5 A eller 3 A i arbeidsmodus, må ladekretsen i tillegg lese CC-nivået (retta i faktasjekk, sjå over). Ei ladebase med kontaktpunkt gjev «set ned og lad»-kvalitet utan tapet til Qi, og kan vere ein del av formkonseptet. Qi tilfører spole, elektronikk, tap og eit radiokrav, og eit referansemerke har alt valt det bort.

### 6. Drivar, dimming og flimmer

**FAKTA.** LED-ar skal drivast med konstantstraum, ikkje med motstand åleine ([LED-Tech om Bridgelux Vesta](https://www.led-tech.de/en/Bridgelux-Vesta-COB-Dim-To-Warm-6W-CRI90-1800K-3000K-LES-9mm)).

**TOLKING – spenningsnivå.** Ei Li-ion-celle gjev 2,5–4,2 V (datablad i punkt 4). Mid-power-LED-ar treng rundt 2,7 V kvar, COB-ar 11–36 V (punkt 2). Mid-power-LED-ar i parallell kan drivast frå éi celle med ein buck- eller buck-boost-drivar, medan COB krev boost. Det talar for mid-power på MCPCB i ei éincelle-lampe.

**FAKTA – flimmer for auget.** IEEE 1789-2015 tilrår for lågrisikonivået maks prosent flimmer = frekvens × 0,08 mellom 90 og 1250 Hz, og ingen avgrensing over 1250 Hz. For nivået «ingen observerbar effekt» er faktoren 0,0333 opp til 3000 Hz, og ingen avgrensing over 3000 Hz ([LightNOW, attgjeving av DOE sitt samandrag](https://www.lightnowblog.com/2015/08/brodrick-on-new-recommended-practice-for-led-flicker/)). Sjølve standarden er ikkje lesen. **TOLKING:** PWM slår lyset heilt av og på (100 % modulasjon), så PWM-frekvensen bør vere minst 1250 Hz og helst over 3000 Hz.

**FAKTA – EU-krav.** For LED-lyskjelder på nettspenning krev forordning 2019/2020 Pst LM ≤ 1,0 og SVM ≤ 0,4 ved full last (SVM ≤ 0,9 fram til september 2024), og kvileeffekt (standby) på høgst 0,5 W ([legislation.gov.uk, vedlegg II](https://legislation.gov.uk/eur/2019/2020/annex/II/2020-01-31), [gesetze.legal](https://gesetze.legal/eu/vo_eu_2019_2020/anhang_ii); via søkjetreff). Avklart i faktasjekk: krava til Pst LM og SVM gjeld berre LED- og OLED-lyskjelder som kan drivast direkte på nettspenning (MLS), ikkje ein 5 V-modul. Reint batteridrivne produkt er unnatekne heile forordninga (vedlegg III punkt 2 bokstav c), medan ei lampe som òg lyser med leidning truleg er omfatta; sjå punkt 2 og opne spørsmål 1 ([EUR-Lex, konsolidert versjon 01.09.2021](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02019R2020-20210901)).

**FAKTA – flimmer i kamera.** Striper i video kjem av samspelet mellom PWM-takta til lyset og avlesingstakta til kameraet ([Enttec](https://support.enttec.com/pixel/pixel-general-knowledge/why-do-leds-flicker-on-camera); via søkjetreff). I ein studie med Sony A7S II (24 bilete/s, lukkartid 1/125 s) gav om lag 10 000 Hz PWM ingen striper ved 100 % lys. Stripene kom når lyset vart dimma, og opptaka var uakseptable ved 900–1500 Hz og 50 % dimming eller lågare. Berre eitt kamera vart testa ([LEDs Magazine/Penn State](https://www.buildings.com/specialty-ssl/article/14299599/video-lighting-iso-settings-and-led-dimming-impact-video-quality)).

**TOLKING.** Ei lampe som skal brukast i digitale møte, blir dimma nettopp i den situasjonen. Vel anten straumregulert dimming (lyset blir aldri slått av, altså ingenting for kameraet å sample) eller PWM langt over 10 kHz. Kva frekvens som er «nok» for vanlege webkamera er **ukjent**; det må testast med ekte kamera på ein fungerande prototype.

**FAKTA – dimmeområde.** Opplevd lysstyrke følgjer om lag kvadratrota av målt lysmengd: 10 % målt lys blir opplevd som 32 %, og 1 % som 10 % ([Lutron/IESNA](https://www.lutron.com/asia/education-training/Documents/lce/lightsources/led/lutron_nemafeb2010.pdf); via søkjetreff) (ikkje stadfesta: lenkja blir no vidaresend til Lutron si framside; tala følgjer av kvadratrotregelen). **Berekna:** Panthella sine steg 10/33/100 % blir opplevde som om lag 32/57/100 %. **TOLKING:** «dempa atmosfære» krev dimming ned til 1–5 % målt lys, og stega bør følgje ei kvadratisk kurve.

### 7. Termikk

**FAKTA.** Diodeprodusentar tilrår å rekne forsiktig: heile den tilførte effekten blir rekna som varme, og delen som blir lys, blir sett bort frå (retta i faktasjekk: talet 85 % står ikkje i artikkelen som varmeandel) ([Digi-Key om Bridgelux AN10](https://www.digikey.co.uk/en/articles/effective-thermal-management-of-led-arrays)). Cree oppgjev at kvite LED-ar er over 40 % effektive og at 50–60 % blir varme ([Cree, via søkjetreff](https://www.mouser.lt/pdfDocs/XLampThermalManagement.pdf); dokumentet vart ikkje opna). Varmeovergangstalet for naturleg konveksjon i luft er 2–15 W/m²K, og ein tommelfingerregel er 10 kvadrattommar (ca. 65 cm²) kjøleflate per watt som skal bort ([Digi-Key](https://www.digikey.co.uk/en/articles/effective-thermal-management-of-led-arrays)).

**FAKTA frå emnet.** Aluminium leier varme med 235 W/mK, stål med 74 W/mK (materialteknologiforelesning Lampe Northern H2026.md, slide 33). Polykarbonat gulnar i sollys (same fil, slide 17).

**Berekna – nødvendig kjøleflate.** A = Q / (h × ΔT). ANTAKING: h = 10 W/m²K (konveksjon pluss stråling), 60–75 % av elektrisk effekt blir varme.

| Elektrisk effekt | Varme (60–75 %) | Flate ved ΔT = 15 K (overflate ca. 40 °C) | Flate ved ΔT = 25 K (ca. 50 °C) |
|---|---|---|---|
| 1,5 W | 0,9–1,1 W | 60–75 cm² | 36–45 cm² |
| 3 W | 1,8–2,3 W | 120–150 cm² | 72–90 cm² |
| 6 W | 3,6–4,5 W | 240–300 cm² | 144–180 cm² |
| 10 W | 6,0–7,5 W | 400–500 cm² | 240–300 cm² |
| 15 W | 9,0–11,3 W | 600–750 cm² | 360–450 cm² |

Til samanlikning (mantel + topp): sylinder Ø 60 × 100 mm = 217 cm², Ø 70 × 100 mm = 258 cm², Ø 80 × 150 mm = 427 cm², Ø 100 × 200 mm = 707 cm². Ei skive Ø 200 mm har 628 cm² på to sider.

**TOLKING.** Opp til 3 W klarer nesten kva kropp som helst seg, også i plast (Poldina Pro oppgjev passiv kjøling ved 2,2 W). Frå 6 W og opp må LED-kortet ha metallisk kontakt med ein kropp eller skjerm i aluminium, og forma må ha eksponert flate. 10–15 W i ei kompakt lampe føreset at skjermen eller reflektoren er kjøleflata. Batteriet toler lading berre opp til 45 °C (punkt 4) og må haldast termisk skilt frå LED-modulen. Grenser for berøringstemperatur i EN 60598-1 er **ikkje verifiserte**.

### 8. Optikk og blendkontroll

**FAKTA frå emnet.** Diffusor spreier lyset og gjer det jamnare, reflektor styrer lyset i ei retning, linse formar lysfordelinga, og skjerming hindrar direkte innsyn i lyskjelda (Teknisk forklaring.pdf, s. 1). Luminans er lystettleik i cd/m² (Lysteori.md, slide 5).

**FAKTA – transmisjon.**
- PLEXIGLAS LED 0M200 SC (opal PMMA for LED): 72 % ved 3 mm ([Zenit/Röhm datablad](https://www.zenit.cz/public/media/Plasty/Zenit_PLEXIGLAS_LED-0M200SC_EN.pdf); via søkjetreff).
- PLEXIGLAS Satinice: fargelaus 0F00 92 %, kvit WH02 44 % (tjukkleik ikkje oppgjeven) ([Zenit/Röhm](https://www.zenit.cz/public/media/Plasty/Zenit_Technicky_List_Plasty_Plexiglas_Satinice_AJ.pdf); via søkjetreff).
- Opale deksel har ofte under 50 % transmisjon ([Trilux](https://www.trilux.com/en/lighting-practice/lighting-equipment/luminaires/photometric-properties/covers); via søkjetreff) (ikkje stadfesta: lenkja gav 404 den 12.11.2026). Ein leverandør oppgjev 30–70 % for opale diffusorar, lågare med meir pigment ([Induflex](https://www.induflex.dk/uk/products/lighting/diffusers-for-lamps/); via søkjetreff) (ikkje stadfesta: lenkja gav 404 den 12.11.2026). Ein annan oppgjev ca. 30 % for klassisk opal og 60–90 % for optimaliserte LED-diffusorar ([Pyrasied](https://shop.pyrasied.com/en/materials/light-diffusers); via søkjetreff).
- Opalglas: Snowball brukar munnblåse opalglas ([smow](https://www.smow.com/northern/snowball-portable-table-lamp.html)). Transmisjonstal for opalglas er **ukjent** (ikkje funne).
- Lysleiarplater (edge-lit) og mikroprismatiske plater: verknadsgrad er **ukjent** (ingen primærkjelde funnen). **Berekna** peikepinn: Elgato Key Light Air gjev 1400 lm av inntil 25 W, altså om lag 56 lm/W på systemnivå med kantbelysning og fleire diffusjonslag.

**Berekna – luminans frå ein opal diffusor.** For ei jamt lysande, diffus flate er L = Φ / (π × A).

| Lysande flate | Areal | 150 lm | 300 lm | 600 lm |
|---|---|---|---|---|
| Kule Ø 70 mm (om lag som Snowball Portable) | 154 cm² | 3100 cd/m² | 6200 cd/m² | 12 400 cd/m² |
| Kule Ø 100 mm | 314 cm² | 1500 | 3000 | 6100 |
| Kule Ø 140 mm | 616 cm² | 780 | 1550 | 3100 |
| Skive Ø 200 mm, éi side | 314 cm² | 1500 | 3000 | 6100 |
| Panel 90 × 90 mm (om lag som Litra Glow) | 81 cm² | 5900 | 11 800 | 23 600 |

Omvendt: for å halde 3000 cd/m² treng 150 lm om lag 160 cm², 300 lm om lag 320 cm² og 600 lm om lag 640 cm² lysande flate. Delvis avklart i faktasjekk: for armaturar ved skjermarbeidsplassar krev EN 12464-1 ifølgje Zumtobel si lyshandbok at armaturluminansen er «below 3000 or 1500 cd/m² at an angle of 65°» ([Zumtobel, The Lighting Handbook, s. 14](https://resources.zumtobel.com/PDB/teaser/EN/lichthandbuch.pdf)). Grensa står under «Reflected glare» og er laga for armaturar som kan spegle seg i skjermen, ikkje for direkte innsyn i ei bordlampe i synsfeltet, så 3000 cd/m² er framleis berre ein reknereferanse, og 1500 cd/m² er det strengare alternativet. Standarden sjølv er ikkje lesen.

**TOLKING.** Ei lita opal kule kan ikkje gje arbeidslys utan å blende. Skal lampa vere kompakt og likevel gje 300–600 lm, må arbeidslyset anten (a) kome frå ei skjerma kjelde som lyser ned på bordet, (b) gå indirekte via ein skjerm, vegg eller reflektor med stort areal, eller (c) kome frå ei større flate som blir folda ut eller vend fram i arbeidsmodus. Dette er det sterkaste formdrivande funnet i rapporten.

**FAKTA – lysnivå.** EN 12464-1 krev 500 lx for ein vanleg kontorarbeidsplass. Retta i faktasjekk: Fagerhult sitt tal på om lag 300 lx gjeld tilrådd lys på tak og vegger (omgjevnadslys), der standarden normalt krev 30–100 lx på tak og 50–150 lx på vegger; det er ikkje eit argument for lågare lysnivå på arbeidsfeltet. I standarden sin kontortabell er 300 lx kravet til arkivering og kopiering, medan skriving, lesing og databehandling har 500 lx og UGR 19 ([Zumtobel, The Lighting Handbook, s. 36](https://resources.zumtobel.com/PDB/teaser/EN/lichthandbuch.pdf)). Sylindrisk belysningsstyrke, som avgjer kor godt ein les ansikt, er normalt sett til 50–150 lx ([Fagerhult](https://www.fagerhult.com/knowledge/light-planning/en-12464-1/lighting-of-indoor-workplaces/standard-en-12464-1-in-brief/)).

**Berekna – kor mange lumen trengst?**
- Arbeidsflate: 500 lx × (0,6 × 0,4 m) = 120 lm på flata. ANTAKING: 40–50 % av lyset treffer flata → 240–300 lm frå lampa. For 300 lx (lågare ambisjonsnivå enn standardkravet til lese- og skjermarbeid): 145–180 lm.
- Ansikt: frå ei lita diffus flate er E ≈ Φ / (π × d²) rett framfor. 100 lm gjev 127 lx på 0,5 m og 65 lx på 0,7 m. 250 lm gjev 318 lx og 162 lx.

**TOLKING.** 100–250 lm retta mot ansiktet frå 0,5–0,7 m dekkjer 50–150 lx. Ansiktslys er altså billeg i lumen og kan gå på batteri. Det som krev effekt, er bordflata. Asymmetrisk optikk, slik BenQ brukar for å halde lyset unna skjermen (punkt 1), er relevant for begge.

### 9. Betjening

**FAKTA – kva referansane gjer.** Panthella V3: berøringsflate i toppmutteren; kort trykk blar 0/10/33/100 %, mellomlangt trykk slår av, langt trykk låser. V3 har «no switch» ([Louis Poulsen](https://smow.fr/pdf/louis-poulsen-panthella-160-v3-factsheet.pdf)). Flowerpot VP9: tre nivå. Poldina Pro: berøringsdimmar. Snowball Portable: tre steg, omtala både som berøringsdimmar og som dimmeknott i messing ([David Village](https://www.davidvillagelighting.co.uk/productpdf/10002372)).

**FAKTA – rørsle og orientering.** Det finst patent på lamper som endrar lyset etter rørsle målt med gyroskop ([US 11,019,705](https://patentimages.storage.googleapis.com/7a/ec/a0/9a0d3ea0df215e/US11019705.pdf); via søkjetreff), og Occhio sel berøringsfri gestestyring ([Occhio](https://www.occhio.de/en/licht-gestensteuerung); via søkjetreff). Ein treaksa MEMS-akselerasjonsmålar som ST LIS2DH12 måler 2 × 2 mm, går på 1,71–3,6 V og brukar straum i mikroampere-området ([ST](https://www.st.com/en/mems-and-sensors/lis2dh12.html), [Digi-Key](https://www.digikey.com/en/products/detail/stmicroelectronics/LIS2DH12TR/4899838); via søkjetreff). Søket fann ingen etablert designlampe som dimmar ved vipping; døma var patent og hobbyprosjekt.

**TOLKING – robust og reparerbart, i rekkjefølgje:**

| Løysing | Fordel | Ulempe |
|---|---|---|
| Mekanisk dreiehjul (potensiometer) | Stillinga er minnet og er synleg. Trinnlaus. Ein standardkomponent som kan bytast. | Mekanisk slitasje, treng tetting og gjennomføring. |
| Mekanisk brytar eller trykknapp | Enkel, taktil, billeg å byte. | Berre steg, ikkje trinnlaus. |
| Modusskifte ved å flytte ein fysisk del (snu skjerm, løfte, vippe) som påverkar ein mekanisk brytar eller magnet/reed | Modusen kan lesast av forma. Ingen programvare. | Krev presis mekanikk og toleransar. |
| Dreiegivar (encoder) + MCU | Trinnlaus, kan styre to kanalar. | Treng fastvare og minne; stillinga viser ikkje nivået. |
| Kapasitiv berøring | Ingen rørlege delar, tett overflate. | Usynleg, fleire trykk for å nå eit nivå, treng MCU, vanskeleg å feilsøkje. |
| Orienteringssensor (akselerasjonsmålar) | Kan gje modus etter korleis lampa står. | Treng MCU og fastvare; brukaren får ingen fysisk tilbakemelding utan god form. |

Levetid for brytarar og givarar (tal på syklusar) er **ikkje henta** frå datablad.

### 10. Regulatoriske produktkrav

**FAKTA.**
- EN 60598-2-4:2018 gjeld flyttbare armaturar til allmenn bruk, inne og ute, opp til 250 V, og blir lesen saman med EN 60598-1. Stabilitetstesten på skråplan skal gjerast med lyskjelda montert, og flyttbare utandørsarmaturar skal ha minst IPX4 ([EVS](https://www.evs.ee/en/evs-en-60598-2-4-2018), [iTeh](https://iteh.es/catalog/standards/clc/bb5ec2e2-e267-4b38-a153-9c570a18d6c8/en-60598-2-4-2018); via søkjetreff).
- IEC 60598-1 kom i tiande utgåve i 2024 og erstatta 2020-utgåva; europeisk utgåve er EN IEC 60598-1:2024 ([Genorma](https://genorma.com/en/standards/en-iec-60598-1-2024/amp); [IEC-lenkja](https://webstore.iec.ch/publication/61414) viser den niande utgåva frå 2020, som vart trekt tilbake 6. november 2024).
- Lågspenningsdirektivet 2014/35/EU gjeld utstyr for 50–1000 V AC eller 75–1500 V DC. Batteridrive utstyr under grensene fell utanfor, men ein ladar eller straumforsyning på nettspenning fell innanfor ([Element](https://www.element.com/resources/articles/the-european-commissions-guide-to-the-low-voltage-directive), [IB-Lenhardt](https://ib-lenhardt.com/kb/faq/low-voltage-directive); via søkjetreff).
- Vanlege EMC- og tryggleiksstandardar for LED-armaturar: EN 55015 (utstråling), EN 61547 (immunitet), EN 61000-3-2 og -3-3 (nettforstyrringar), EN 62471 (fotobiologisk tryggleik) ([SIQ](https://siq.si/?p=25921), [Eurofins](https://www.eurofins.com/electrical-and-electronics/industries/electrical-consumer-products/lighting-luminaires/); via søkjetreff).
- Samanliknbare batterilamper er klasse III: Panthella V3 ([Louis Poulsen](https://smow.fr/pdf/louis-poulsen-panthella-160-v3-factsheet.pdf)), Flowerpot VP9 ([Architonic](https://architonic.com/en/product/-tradition-flowerpot-vp9-grey-beige/20200625)) og Snowball Portable ([Kitchentime](https://www.kitchentime.com/brands/northern-lighting/snowball-portable-table-lamp-33-cm/)).
- IP-klasse i marknaden: Panthella V1 IP23, V2 og V3 IP44; Flowerpot IP44; Snowball IP44 (kjelder i punkt 1).
- Felles ladar-direktivet (EU) 2022/2380 krev USB-C på bestemte kategoriar radioutstyr, mellom anna mobiltelefonar, nettbrett, kamera og hovudtelefonar ([Europakommisjonen](https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/radio-equipment-directive-red/one-common-charging-solution-all_en); via søkjetreff). Lamper står ikkje på lista i vedlegg Ia, som har 13 kategoriar (mobiltelefonar, nettbrett, digitalkamera, hovudtelefonar, hovudsett, handhaldne spelkonsollar, berbare høgtalarar, lesebrett, tastatur, mus, berbare navigasjonssystem, øyreproppar og berbare PC-ar), og direktivet gjeld uansett berre radioutstyr (stadfesta i faktasjekk mot [direktivteksten](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022L2380)).

**TOLKING.** Ei lampe som berre har 5 V inn via USB-C og batteri på 3,6 V, er ein klasse III-armatur på SELV-nivå. Det gjev stor formfridom: ingen krav til dobbel isolasjon mot nettspenning, og metall kan vere berørbart. Vel ein å leggje ved ein nettadapter, kjem han inn under lågspenningsdirektivet og økodesignkrava til straumforsyningar. Å ikkje leggje ved adapter er praksis hos referansane (punkt 1). IP44 i marknaden kjem av at lampene blir selde til terrassebruk; ei rein skrivebordslampe treng det ikkje (ANTAKING: IP20 held innandørs).

**ANTAKING, ikkje verifisert:** CE-merking krev i tillegg RoHS og WEEE-merking; produkt utan nettspenning blir vurderte etter den generelle produkttryggleiksforordninga (EU) 2023/988; trådlaus lading eller Bluetooth dreg inn radioutstyrsdirektivet. Definisjonen av SELV (spenningsgrenser) og detaljane i stabilitetstesten (vinklar) er heller ikkje verifiserte.

### 11. Arkitektur for reparasjon

**FAKTA – døme som gjer det godt.**
- Panthella 160 Portable V3: batteriet er ei 18650-celle som finst som reservedel (faktaarket er motstridande om det er sluttbrukar eller «qualified person» som skal byte, og typeskiltet krev «listed battery»; retta i faktasjekk), reservedelsnummer for batterisett og for «PCB & LED»-sett, skjermar og toppmutter kan kjøpast separat ([Louis Poulsen](https://smow.fr/pdf/louis-poulsen-panthella-160-v3-factsheet.pdf)).
- Tala Muse Portable: batteribyte med fire skruar i botnen, to skruar på batteripakken og éin pluggkontakt; nytt batteri blir selt av produsenten ([Tala](https://tala.co.uk/blogs/lighting-guide/how-to-replace-your-muse-portable-lamp-battery)).
- Zafferano Poldina Pro: batteripakke som tilbehør med eige varenummer ([Zafferano](https://cdn.shopify.com/s/files/1/0591/2484/2705/files/Specification_Sheet_Poldina_Pro.pdf)).
- Fermob: videorettleiingar for byte av batteri, LED-modul og diffusor ([Worm/Fermob](https://worm.co.uk/pages/fermob-lighting-sustainability); via søkjetreff).

**FAKTA.** Kommisjonen si rettleiing til batteriforordninga viser til EN 45554:2020 for kva som er vanleg og proprietært verktøy ([Cooley](https://products.cooley.com/2025/02/13/european-commission-publishes-guidance-on-eu-batteries-regulation-removability-requirements/)).

**TOLKING – tilrådd modulinndeling.**

| Modul | Feste | Tilkopling | Kven byter | Krav bak |
|---|---|---|---|---|
| Batteri: 1–2 standardceller i haldar, eller pakke | Lok med éin skrue eller myntspor | Fjørkontaktar eller polarisert plugg | Sluttbrukar | Batteriforordninga art. 11 |
| LED-modul: MCPCB eller COB i haldar | 2–3 like skruar mot kjøleflate | Plugg, ikkje lodding | Sluttbrukar eller verkstad | 2019/2020 art. 4 |
| Drivar- og ladekort | Skruar eller snepp i foten | Pluggar til batteri, LED, brytar, USB | Verkstad | 2019/2020 art. 4 (separat drivar) |
| USB-C-port på eige lite kort | Skruar | Plugg | Verkstad | Slitedel, bør ikkje sitje på hovudkortet |
| Brytar/dimmar | Mutter eller skruar | Plugg | Verkstad | Slitedel |
| Diffusor/skjerm | Gjenge, bajonett eller skruar; ikkje lim | – | Sluttbrukar | Knusbar del (glas) |

Merknad frå faktasjekk: 2019/2020 artikkel 4 gjeld ikkje reint batteridrivne produkt (vedlegg III punkt 2 bokstav c), men truleg ei lampe som òg lyser med leidning (sjå punkt 2). Kravet er uansett rett å designe etter. Om drivarkortet i ei 5 V-lampe er «separate control gear» i forordninga si meining, er ikkje avklart (ikkje stadfesta); definisjonen gjeld utstyr som tilpassar nettspenninga til lyskjelda, og eksterne straumforsyningar er haldne utanfor.

Prinsipp: éin skrutype (t.d. Torx eller kryss) gjennom heile produktet, ingen lim eller ultralydsveising, éin materialtype per del, og merking av plastdelar. Det tener både reparasjon og materialseparasjon.

### 12. Grov BOM og kostnadsbilete

**FAKTA – prisankre.**
- Utsalspris Snowball Portable: 1 790 kr ([Kitchentime](https://www.kitchentime.com/brands/northern-lighting/snowball-portable-table-lamp-33-cm/)), frå 189 € ([smow](https://www.smow.com/northern/snowball-portable-table-lamp.html)).
- Mid-power-LED CRI 90, 3000 K: om lag 0,17–0,25 USD per stk. ved 1000 stk. ([Zenode](https://zenode.ai/parts/u3rt25jzi2-samsung-semiconductor-inc-SPMWHD32AMVKXAV3SW), [element14](https://sg.element14.com/samsung/spmwhd32amd5xav3sk/led-hb-white-3000k-38lm-3030/dp/3003230); via søkjetreff, rettleiande prisar).
- Dim-to-warm-COB: 4,96 € netto per stk. i enkeltkjøp ([LED-Tech](https://www.led-tech.de/en/Bridgelux-Vesta-COB-Dim-To-Warm-6W-CRI90-1800K-3000K-LES-9mm)).
- 18650-celle (Samsung 35E): 6,10–8,50 € netto i småkjøp i Europa ([Ormix](https://ormix.lv/en/product/37351); via søkjetreff); 2,95 USD på tilbod hos amerikansk forhandlar ([18650 Battery Store](https://www.18650batterystore.com/collections/flat-top-18650-batteries); via søkjetreff).
- Sprøytestøypeverktøy: 1 000–5 000 USD for enkel einskavitets aluminiumsform, 3 000–25 000 USD for stål, ifølgje leverandørbloggar ([Hubs](https://hubs.com/knowledge-base/how-much-does-injection-molding-cost), [RapidDirect](https://www.rapiddirect.com/blog/injection-molding-quote-cost-breakdown/); via søkjetreff). Verktøy har 6–16 vekers leveringstid og krev store seriar (materialteknologiforelesning Lampe Northern H2026.md, slide 39 og 41).
- Tommelfingerregel: utsalspris er 4–6 gonger produksjonskostnaden når ein sel gjennom forhandlar ([Predictable Designs](https://predictabledesigns.com/how-to-price-your-product-for-various-distribution-channels/), [Inventors Digest](https://inventorsdigest.com/inventing-101-your-profit-formula); via søkjetreff, bloggkjelder).

**Berekna – kostnadsmål.** 1 790 kr / 1,25 (mva.) = 1 432 kr. Delt på 4–6 gjev 240–360 kr i produksjonskostnad. 189 € / 1,19 = 159 €; delt på 4–6 gjev 26–40 €.

**OVERSLAG (ANTAKING) – BOM for ei batterilampe på Snowball Portable-nivå, nokre tusen einingar per år.** Alle tal under er mine eigne grove overslag utan tilbod frå leverandør. Berre prisankra over har kjelde.

| Post | Lågt | Høgt | Merknad |
|---|---|---|---|
| LED-modul (MCPCB, 12–24 mid-power-LED, plugg) | 2 € | 5 € | To kanalar ligg i øvre del |
| Drivar-, lade- og vernekort, montert | 4 € | 9 € | MCU og to kanalar ligg i øvre del |
| Batteri (1–2 celler, haldar, vern) | 4 € | 10 € | |
| USB-C-kort og 2 m kabel, utan adapter | 1,5 € | 4 € | |
| Brytar/dimmar med knott | 1 € | 5 € | Dreidd metallknott ligg høgt |
| Diffusor/skjerm | 1 € | 15 € | Sprøytestøypt PMMA/PC lågt, munnblåse opalglas høgt |
| Kropp/fot i metall, overflatebehandla | 8 € | 25 € | Største usikre post |
| Skruar, pakningar, glidefot, ballast | 1 € | 3 € | |
| Emballasje og bruksrettleiing | 2 € | 5 € | |
| Montering og test | 4 € | 10 € | |
| **Sum** | **28,5 €** | **91 €** | |

**TOLKING.** Elektronikken (dei fire første postane) utgjer 11,5–28 € og er ikkje det som sprengjer rekneskapen. Det gjer dei mekaniske delane og finishen. Kostnadsmålet på 26–40 € blir berre nådd i nedre del av spennet: få delar, éin metallprosess, standardceller. Verktøy kjem i tillegg; tre former à 10 000 € fordelte på 3000 einingar i året over tre år er om lag 3,3 € per eining (ANTAKING). Ei arbeidslampe med større batteri og to kanalar vil liggje høgare og bør truleg prisast over Snowball Portable.

---

## Tal og fakta

| Storleik | Verdi | Kjelde |
|---|---|---|
| Lysfluks, portable designlamper | 104–240 lm ved 100 % | [LP](https://smow.fr/pdf/louis-poulsen-panthella-160-v3-factsheet.pdf), [Zafferano](https://cdn.shopify.com/s/files/1/0591/2484/2705/files/Specification_Sheet_Poldina_Pro.pdf), [smow](https://www.smow.com/northern/snowball-portable-table-lamp.html), [Architonic](https://architonic.com/en/product/-tradition-flowerpot-vp9-grey-beige/20200625) |
| Merkeeffekt, same lamper | 2,2–3 W | same |
| Brukstid ved 100 % | 8–10 timar | same |
| Ladetid | 4–8 timar | same |
| Vekt | 0,4–0,8 kg | same |
| Batteri i referansane | 1 × 18650 3100 mAh; 2 × 18650 2200 mAh; 5200 mAh | same |
| Batterilevetid oppgjeven | 500 syklusar til 70 % (LP); ca. 450 ladingar (Zafferano) | same |
| LED-levetid integrert modul | 60 000 timar L70 | [LP](https://smow.fr/pdf/louis-poulsen-panthella-160-v3-factsheet.pdf) |
| LED-levetid retrofit E14 | 15 000 timar L70 | [Signify](https://www.signify.com/en-gb/prof/led-lamps-and-tubes/led-candles-and-lustres/philips-master-value-glass-led-candles-and-lustres/929003059502_EU/product) |
| Lysutbytte mid-power CRI 80, 5000 K | 220 lm/W | [Samsung](https://led.samsung.com/about-us/news-events/news/news-detail-37) |
| Lysutbytte mid-power CRI 90, 3000 K | ca. 160–180 lm/W (berekna) | [Samsung](https://led.samsung.com/lighting/mid-power-leds/3030-leds/lm301b) |
| Lysutbytte dim-to-warm-COB | 115 lm/W (3000 K), 104 lm/W (1800 K) | [LED-Tech](https://www.led-tech.de/en/Bridgelux-Vesta-COB-Dim-To-Warm-6W-CRI90-1800K-3000K-LES-9mm) |
| Lysutbytte retrofit E14 CRI 90 | 138 lm/W | [Signify](https://www.signify.com/en-gb/prof/led-lamps-and-tubes/led-candles-and-lustres/philips-master-value-glass-led-candles-and-lustres/929003059502_EU/product) |
| Systemutbytte i referanselamper | 53–111 lm/W (berekna; retta i faktasjekk) | punkt 1 |
| 21700-celle | 4900 mAh, 3,63 V, 17,8 Wh, 69,5 g, Ø 21,25 × 70,8 mm | [Samsung SDI](https://shop.aceongroup.com/cdn/shop/files/RLII-CSI-1618_Samsung_50E_DATASHEET.pdf) |
| 18650-celle | 3500 mAh, 3,6 V, ca. 12 Wh, 48 g | [lygte-info](https://lygte-info.dk/review/batteries2012/Samsung%20INR18650-35E%203500mAh%20%28Pink%29%20UK.html) |
| Syklusar, 21700 | ≥ 80 % etter 500 | [Samsung SDI](https://shop.aceongroup.com/cdn/shop/files/RLII-CSI-1618_Samsung_50E_DATASHEET.pdf) |
| Ladetemperatur | 0–45 °C | same |
| LFP mot NMC | 90–120 mot 150–220 Wh/kg; ≥ 2000 mot 1000–2000 syklusar | [BU-205](https://batteryuniversity.com/article/bu-205-types-of-lithium-ion) |
| Ladegrense 4,06 V | 600–1000 syklusar, 81 % kapasitet | [BU-808](https://batteryuniversity.com/article/bu-808-how-to-prolong-lithium-based-batteries) |
| Lagring fulladd, 25 °C / 40 °C | 80 % / 65 % att etter eitt år | same |
| USB-C utan PD | 5 V, inntil 1,5 A (7,5 W) eller 3 A (15 W) | [MPS](https://media.monolithicpower.cn/mps_cms_document/u/s/usb-type-c-charging-connectors-design-optim-interop_r1.0.pdf) |
| Qi | BPP 5 W, EPP 15 W; målt 63 % mot 81 % kabla | [GRL](https://www.graniteriverlabs.com/en-us/technical-blog/2024-qi2-technical-compliance), [Allion](https://www.allion.com/?p=5581) |
| Flimmer, IEEE 1789 | ingen avgrensing over 1250 Hz (låg risiko) / 3000 Hz (ingen effekt) | [LightNOW/DOE](https://www.lightnowblog.com/2015/08/brodrick-on-new-recommended-practice-for-led-flicker/) |
| Flimmer, EU nettlyskjelder | Pst LM ≤ 1,0; SVM ≤ 0,4; standby ≤ 0,5 W | [2019/2020 vedlegg II](https://legislation.gov.uk/eur/2019/2020/annex/II/2020-01-31) |
| Kamerastriper | uakseptabelt ved 900–1500 Hz og ≤ 50 % dimming; ingen ved ca. 10 kHz og 100 % | [LEDs Magazine](https://www.buildings.com/specialty-ssl/article/14299599/video-lighting-iso-settings-and-led-dimming-impact-video-quality) |
| Opplevd mot målt lys | 10 % målt = 32 % opplevd; 1 % = 10 % (ikkje stadfesta: kjeldelenkja er død; tala følgjer av kvadratrotregelen) | [Lutron](https://www.lutron.com/asia/education-training/Documents/lce/lightsources/led/lutron_nemafeb2010.pdf) |
| Naturleg konveksjon | 2–15 W/m²K; ca. 65 cm² kjøleflate per watt | [Digi-Key](https://www.digikey.co.uk/en/articles/effective-thermal-management-of-led-arrays) |
| Varmeleiing | aluminium 235, stål 74 W/mK | materialteknologiforelesning Lampe Northern H2026.md, slide 33 |
| Opal PMMA for LED, 3 mm | 72 % transmisjon | [Röhm/Zenit](https://www.zenit.cz/public/media/Plasty/Zenit_PLEXIGLAS_LED-0M200SC_EN.pdf) |
| Opale deksel generelt | 30–70 %, ofte under 50 % (ikkje stadfesta: begge lenkjene gav 404 den 12.11.2026). Stadfesta: ca. 30 % for klassisk opal, 60–90 % for optimaliserte diffusorar | [Induflex](https://www.induflex.dk/uk/products/lighting/diffusers-for-lamps/), [Trilux](https://www.trilux.com/en/lighting-practice/lighting-equipment/luminaires/photometric-properties/covers), [Pyrasied](https://shop.pyrasied.com/en/materials/light-diffusers) |
| Arbeidsplass, EN 12464-1 | 500 lx; sylindrisk 50–150 lx | [Fagerhult](https://www.fagerhult.com/knowledge/light-planning/en-12464-1/lighting-of-indoor-workplaces/standard-en-12464-1-in-brief/) |
| Armaturluminans ved skjermarbeidsplass, EN 12464-1 | under 3000 eller 1500 cd/m² ved 65° (lagt til i faktasjekk) | [Zumtobel](https://resources.zumtobel.com/PDB/teaser/EN/lichthandbuch.pdf) |
| Batteri utskiftbart av sluttbrukar | krav frå 18.02.2027; reservedel i minst 5 år | [2023/1542 art. 11 og 96](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02023R1542-20260813), [Compliance Gate](https://www.compliancegate.com/removable-and-replaceable-battery-requirements-european-union/) |
| Lyskjelde og drivar utskiftbare | med vanleg verktøy, elles teknisk grunngjeving; gjeld ikkje reint batteridrivne produkt (vedlegg III punkt 2 c) | [2019/2020 art. 4](https://www.legislation.gov.uk/eur/2019/2020/article/4/adopted), [konsolidert tekst](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02019R2020-20210901) |
| Snowball Portable, Northern sine eigne tal | 158 lm (produktside, brukarrettleiing) eller 60/120/200 lm (produktark); 3 W; 2700 K; CRI > 90; 8 t ved full styrke; 33 cm høg, kule Ø 7 cm; 0,5 kg; IP44; klasse III (lagt til i faktasjekk) | [northern.no](https://www.northern.no/en/products/snowball-portable-table-lamp), [produktark](https://www.northern.no/cdn/shop/files/Northern_product_sheet_-_Snowball_portable_table_lamp.pdf?v=11906401054735407144) |
| Utsalspris Snowball Portable | 1 790 kr; frå 189 € | [Kitchentime](https://www.kitchentime.com/brands/northern-lighting/snowball-portable-table-lamp-33-cm/), [smow](https://www.smow.com/northern/snowball-portable-table-lamp.html) |

---

## Implikasjonar for designet

1. **Del lysoppgåva i to.** Stemningslys (15–150 lm, varm, diffus, låg luminans) er lett å løyse på batteri. Arbeidslys (300–600 lm på bordflata) krev anten leidning eller eit batteri på 35–70 Wh. Konsepta bør vise tydeleg kva modus som er batteridriven og kva som er kabla.
2. **La leidningen vere ein del av konseptet, ikkje ein nødvendig vond.** USB-C gjev 7,5–15 W når kjelda melder 1,5 A eller 3 A, nok til 600–1000 lm. Ei lampe som «landar» på ein base eller kabel i arbeidsmodus og blir teken med rundt i stemningsmodus, følgjer fysikken og svarar på «flyttbar og eventuelt oppladbar».
3. **Lysande areal er ein formparameter.** Rekn med minst 160 cm² lysande flate per 150 lm bak opal diffusor, eller skjerm kjelda heilt og lys indirekte. Ei lita opal kule er eit stemningslys, ikkje eit arbeidslys.
4. **Ansiktslys er billeg.** 100–250 lm frå ei mjuk flate i augehøgd på 0,5–0,7 m held. Det kan vere same diffuse flate som stemningslyset, vend mot brukaren.
5. **Vel dimmeteknikk med kameraet i tankane.** Straumregulert dimming eller PWM over 10 kHz, og test med webkamera. Dimming ned til 1–5 % målt lys for at «dempa» skal kjennast dempa.
6. **Batteriet skal ut med ein mynt.** Standard 18650 eller 21700 i haldar under eit lok i foten. Det oppfyller uttakskravet i batteriforordninga, gjev lågt tyngdepunkt og held cella unna LED-varmen. Kva celle brukaren trygt kan setje inn (verna celle eller pakke med vernekrets), må avklarast (sjå punkt 4). Lampa bør fungere med leidning også utan batteri, slik at eit dødt batteri ikkje gjer lampa til avfall.
7. **Lyskjelda på eigen modul med plugg og skruar.** Mid-power-LED på aluminiumskort passar spenninga til éi celle og spreier varmen. Kortet bør skruast mot ein metallkropp som er kjøleflate.
8. **Kandidatar til berekraftshandling med tal bak:** (a) ladegrense rundt 4,05 V, som om lag doblar syklustalet; (b) straumveg som let batteriet kvile når leidningen står i; (c) standardcelle som reservedel i staden for spesialpakke; (d) ingen adapter i esken; (e) ingen trådlaus lading, som sparer om lag 22 % ladeenergi (trådlaus lading krev rundt 30 % meir enn kabel; retta i faktasjekk) og ein spole; (f) éin skrutype og ingen lim.
9. **Fysisk dimmar framfor berøring** dersom konseptet toler det: stillinga er minnet, nivået er synleg, og komponenten kan bytast. Modusskifte ved å flytte ein del av lampa er mogleg utan elektronikk dersom rørsla påverkar ein mekanisk brytar.
10. **Kostnad:** elektronikken er ikkje problemet. Kvar ekstra metall- eller glasdel og kvar ekstra prosess er det. Tre konsept bør kunne forklarast med 6–10 hovuddelar.

### Mogleg konvolutt

Realistiske spenn for ei kompakt, flyttbar lampe i dette segmentet. Tala byggjer på referanselampene og reknestykka over; føresetnadene er merkte der.

| Parameter | Nedre | Typisk | Øvre | Grunnlag |
|---|---|---|---|---|
| Lysfluks på batteri | 15 lm (dempa) | 100–250 lm | 400 lm | Referanselamper; tabell 2 |
| Lysfluks med leidning | – | 400–600 lm (7,5 W) | ca. 1000 lm (15 W, 3 A-kjelde) | USB-C-nivå; 80 lm/W (ANTAKING) |
| Effekt på batteri | 0,15 W | 1,3–3 W | 5 W | Panthella berekna; merkeeffektar |
| Effekt med leidning | – | 5–7,5 W | 12–15 W | USB-C utan PD |
| Batteri | 11 Wh (1 × 18650) | 18 Wh (1 × 21700) | 36 Wh (2 × 21700); 71 Wh (4 ×) for arbeidsdag på 600 lm | Celledatablad |
| Cellevekt | 48 g | 70 g | 139–278 g | same |
| Brukstid | 2–4 t ved 300 lm | 8–12 t ved 100–150 lm | 25–80 t ved 15–50 lm | Tabell 2; Panthella |
| Ladetid | 2–3 t (7,5 W) | 4–6 t | 8 t | Berekna; referansar |
| Totalvekt | 0,4 kg | 0,5–0,8 kg | 1,2 kg | Referansar; ANTAKING for øvre |
| Fargetemperatur | 1800–2200 K (dempa) | 2700 K | 3500–4000 K (arbeid/møte, to kanalar) | Punkt 3 |
| Fargeattgjeving | CRI 80 | CRI 90 | CRI 95 | Referansar |
| Kjøleflate, passiv | 50 cm² (1,5 W) | 150–300 cm² (3–6 W) | 500–750 cm² (10–15 W) | Punkt 7 |
| Lysande flate ved 3000 cd/m² | 160 cm² (150 lm) | 320 cm² (300 lm) | 640 cm² (600 lm) | Punkt 8 |

**Minste byggjemål (overslag):**
- Batterirom for éi 21700-celle i haldar: om lag Ø 24 × 80 mm innvendig (cella er maks Ø 21,25 × 70,8 mm). To celler side om side: om lag 48 × 24 × 80 mm. For 18650 tilseier nemninga Ø 18 × 65 mm pluss haldar (ANTAKING for haldarmåla).
- LED-modul: COB 12 × 15 × 1,7 mm, eller eit MCPCB på 30–60 mm diameter med 12–24 LED-ar à 3 × 3 mm (ANTAKING for kortstorleik).
- Drivar- og ladekort: om lag 30 × 40 mm (ANTAKING).
- Minste fot som rommar éi liggjande 21700-celle, kort og USB-C-port: om lag Ø 85–90 mm × 30 mm, eller ein ståande sylinder på om lag Ø 35 × 90 mm (ANTAKING, må prøvast i mockup).
- Lågaste meiningsfulle totalvolum for ei stemningslampe med éi celle ligg rundt målet til Panthella Portable (Ø 160 × 241 mm) og Snowball Portable (Ø 70–90 × 330 mm); elektronikken tek lite av dette, optikken og stabiliteten tek resten.

---

## Opne spørsmål

1. **Gjeld økodesignforordninga 2019/2020 fullt ut for ei lampe som går på batteri, men òg kan drivast frå USB?** Eg meiner å hugse eit unntak for batteridrivne produkt i vedlegg III, men det er ikkje verifisert i denne økta. Avgjer om flimmerkrav og energimerking gjeld. *Faktasjekk:* Unntaket finst (vedlegg III punkt 2 bokstav c) og gjeld produkt som berre går på eiga straumkjelde utan direkte eller indirekte nettilkopling (vedlegg I punkt 44). Ei lampe som òg lyser med USB-leidning, fell truleg utanfor unntaket. Det som står att, er å få denne tolkinga stadfesta hos rettleiar, Northern eller eit testlaboratorium. Flimmerkrava (Pst LM, SVM) gjeld uansett berre lyskjelder for nettspenning.
2. **Kva står på Northern si eiga produktside for Snowball Portable** om lumen (158, 200 eller 240 lm), batterikapasitet og om batteri og LED-modul er utskiftbare? Sida kunne ikkje opnast. Bør spørjast direkte hos Northern, saman med kven som er leverandør av elektronikken. *Faktasjekk:* Sida vart opna 12.11.2026. Produktsida og brukarrettleiinga seier 158 lm, produktarket 60/120/200 lm. Produktsida seier «Replaceable battery» og «Replaceable LED module with push connector». Batterikapasiteten står ingen stad. Spør Northern om kapasitet, kva lumental som gjeld, og om sluttbrukaren sjølv kan byte batteriet.
3. **Ønskjer Northern ei arbeidslampe som er dyrare enn Snowball Portable?** Målpris og årsvolum styrer val mellom glas og polymer, ei eller to celler, ein eller to kanalar.
4. **Er to-kanals fargestyring ønskt, eller held dim-to-warm?** Bør avklarast med ekstern rettleiar, saman med realismen i 80 lm/W på systemnivå.
5. **Kva PWM-frekvens eller dimmemetode gjev stripefritt bilete i vanlege webkamera?** Ukjent; må testast.
6. **Kva luminansgrense gjeld for lamper i synsfeltet ved skjerm** (EN 12464-1)? 3000 cd/m² er brukt som reknereferanse utan verifisering. *Faktasjekk:* Zumtobel si lyshandbok attgjev kravet som under 3000 eller 1500 cd/m² ved 65° for armaturar ved skjermarbeidsplassar. Kva som gjeld for ei bordlampe i synsfeltet (direkte blending), er framleis ope.
7. **Grenser for berøringstemperatur og stabilitetstest i EN 60598-1 og -2-4** (vinklar, temperaturar) er ikkje verifiserte. Standardane må lesast, t.d. via biblioteket. *Faktasjekk:* Samandraget til IEC 60598-2-4:2017 stadfestar at stabilitetstesten på skråplan skal gjerast med lyskjelda montert, og at minstekravet utandørs er heva frå IPX3 til IPX4. Vinklar og temperaturgrenser er framleis ikkje verifiserte.
8. **Krav til batteri i armaturar i EN IEC 60598-1:2024** og kva dokumentasjon (IEC 62133-2, UN 38.3) celleleverandøren må levere: ikkje avklart.
9. **Transmisjon for opalglas og verknadsgrad for lysleiarplater og mikroprismer** vart ikkje funne. Bør målast på materialprøver med luxmeter.
10. **Blir artikkel 11 i batteriforordninga utsett?** Éi kjelde nemner eit utsetjingsforslag som ikkje er vedteke; status er ikkje undersøkt vidare. *Faktasjekk:* Ikkje utsett per konsolidert versjon 13.08.2026; artikkel 96 nr. 2 bokstav a seier framleis 18. februar 2027. Kommisjonsforslaget COM(2025) 981 endrar berre artikkel 11 nr. 5 om batteri til lette køyretøy. Seinare forslag er ikkje kontrollerte.
11. **Reparasjonsdirektivet (EU) 2024/1799:** om lamper står på produktlista vart ikkje verifisert her; høyrer til research om regelverk og berekraft. *Faktasjekk:* Lamper og lyskjelder står ikkje i vedlegg II til direktivet. Lista har ti produktgrupper: vaskemaskiner, oppvaskmaskiner, kjøleapparat, elektroniske skjermar, sveiseutstyr, støvsugarar, tenarar og datalagring, mobiltelefonar, trådlause telefonar og nettbrett, tørketromlar og varer med batteri til lette køyretøy ([direktivteksten](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024L1799)). Reparasjonsplikta i direktivet gjeld dermed ikkje lamper direkte. Dei bindande krava til reparerbarheit for dette produktet kjem frå batteriforordninga artikkel 11 og, for ei lampe som òg lyser med leidning, truleg 2019/2020 artikkel 4.
12. **Finst det lågvolts sokkellyskjelder (12 V) med CRI 90** som kunne gje brukarutskiftbar lyskjelde i ei batterilampe? Ikkje undersøkt.
13. **Kor mykje lys treng brukaren eigentleg?** Reknestykka for bordflate og ansikt bør kontrollerast med ein enkel mockup og luxmeter.
14. **BOM-overslaget** har ingen leverandørtilbod bak seg. Metallkropp, glas og montering er dei mest usikre postane.

---

## Kjelder

### Lokale filer
- `context/2 Endelig designbrief Northern.md` – designbrief.
- `context/Teknisk forklaring.pdf`, s. 1 – omgrep: lyskjelder, dim-to-warm, diffusor, reflektor, skjerming.
- `context/Lysteori.md`, slide 5 – lysfluks, lysutbytte, luminans.
- `context/materialteknologiforelesning Lampe Northern H2026.md`, slide 17 (polykarbonat), slide 33 (stål mot aluminium), slide 39 og 41 (sprøytestøypeverktøy).

### Referanseprodukt
- Louis Poulsen, Panthella 160 Portable V3, faktaark: https://smow.fr/pdf/louis-poulsen-panthella-160-v3-factsheet.pdf
- Northern Snowball Portable hos smow: https://www.smow.com/northern/snowball-portable-table-lamp.html
- Northern Snowball Portable, produktark hos David Village Lighting: https://www.davidvillagelighting.co.uk/productpdf/10002372
- Northern Snowball Portable hos Kitchentime: https://www.kitchentime.com/brands/northern-lighting/snowball-portable-table-lamp-33-cm/
- Northern, produktside (HTTP 429 i første økt; opna i faktasjekken 12.11.2026): https://www.northern.no/en/products/snowball-portable-table-lamp
- Northern, produktark Snowball portable table (lagt til i faktasjekk): https://www.northern.no/cdn/shop/files/Northern_product_sheet_-_Snowball_portable_table_lamp.pdf?v=11906401054735407144
- Northern, brukarrettleiing Snowball portable table (lagt til i faktasjekk): https://www.northern.no/cdn/shop/files/User_manual_-_Snowball_portable_table.pdf?v=10090650407803861463
- &Tradition, faktaark og bruksrettleiing Flowerpot VP9 (lagt til i faktasjekk): https://www.assetslibrary.com/asset/586904ba-bd72-495c-bea8-38a9ae347f78/ATD_Product-Fact-Sheets_Flowerpot_VP9.pdf og https://www.assetslibrary.com/asset/c0a85983-134f-4603-9063-92a837a1b931/ATD_Instruction-Manuals_Flowerpot_VP9.pdf
- &Tradition Flowerpot VP9 hos Architonic: https://architonic.com/en/product/-tradition-flowerpot-vp9-grey-beige/20200625
- &Tradition Flowerpot VP9 hos Connox: https://www.connox.com/categories/lighting/table-lamps/tradition-flowerpot-rechargeable-battery-table-lamp-vp9.html
- Zafferano Poldina Pro, spesifikasjonsark: https://cdn.shopify.com/s/files/1/0591/2484/2705/files/Specification_Sheet_Poldina_Pro.pdf
- Tala, batteribyte Muse Portable: https://tala.co.uk/blogs/lighting-guide/how-to-replace-your-muse-portable-lamp-battery
- Fermob hos Worm: https://worm.co.uk/pages/fermob-lighting-sustainability
- Logitech Litra Glow, spesifikasjon: https://support.logi.com/hc/en-gb/articles/4418106727447-Specification-Litra-Glow
- Elgato Key Light Air, spesifikasjon: https://help.elgato.com/hc/it/articles/360038093012-Key-Light-Air-Specifiche-Tecniche
- BenQ ScreenBar: https://www.benq.com/en-us/lighting/monitor-light/screenbar.html

### Lyskjelder og styring
- Samsung LM301B: https://led.samsung.com/lighting/mid-power-leds/3030-leds/lm301b og https://led.samsung.com/about-us/news-events/news/news-detail-37
- Bridgelux V6 HD Gen 8, datablad DS1360: https://www.bridgelux.com/sites/default/files/2024-09/ds1360_gen_8_v6_hd_array_data_sheet_202409_rev_b.pdf
- Bridgelux V-serien F90, datablad-kopi: https://static.chipdip.ru/lib/318/DOC042318248.pdf
- Bridgelux Vesta Dim-To-Warm hos LED-Tech: https://www.led-tech.de/en/Bridgelux-Vesta-COB-Dim-To-Warm-6W-CRI90-1800K-3000K-LES-9mm
- Signify, Philips MASTER Value LEDcandle E14: https://www.signify.com/en-gb/prof/led-lamps-and-tubes/led-candles-and-lustres/philips-master-value-glass-led-candles-and-lustres/929003059502_EU/product
- Zhaga, oversyn over Books: https://www.zhagastandard.org/books/overview/ og https://www.zhagastandard.org/books/overview/socketable-linear-lles-14.html
- IEC PAS 63324 (Zhaga Book 1 og 10): https://webstore.iec.ch/publication/67189
- Cree LED, referansedesign dim-to-warm CLD-AP291: https://downloads.cree-led.com/files/da/x/Tunable-White-COB-Dim-to-Warm.pdf
- Acuity/eldoLED om dynamisk kvitt lys: https://insights.acuitybrands.com/eldoled-blog/article-interoperable-systems-for-dynamic-white-lighting
- IEEE 1789-2015, samandrag: https://www.lightnowblog.com/2015/08/brodrick-on-new-recommended-practice-for-led-flicker/
- LEDs Magazine/Penn State, LED-dimming og video: https://www.buildings.com/specialty-ssl/article/14299599/video-lighting-iso-settings-and-led-dimming-impact-video-quality
- Enttec om LED-flimmer i kamera: https://support.enttec.com/pixel/pixel-general-knowledge/why-do-leds-flicker-on-camera
- Lutron, målt mot opplevd lys: https://www.lutron.com/asia/education-training/Documents/lce/lightsources/led/lutron_nemafeb2010.pdf

### Batteri og lading
- Samsung SDI INR21700-50E, datablad: https://shop.aceongroup.com/cdn/shop/files/RLII-CSI-1618_Samsung_50E_DATASHEET.pdf
- Samsung INR18650-35E, måling hos lygte-info: https://lygte-info.dk/review/batteries2012/Samsung%20INR18650-35E%203500mAh%20%28Pink%29%20UK.html
- Battery University BU-205: https://batteryuniversity.com/article/bu-205-types-of-lithium-ion
- Battery University BU-808: https://batteryuniversity.com/article/bu-808-how-to-prolong-lithium-based-batteries
- IEC 62133-2, omtale: https://www.batterydesign.net/legislation-rules-and-regulations/iec-62133-2/ og https://www.danenergy.com/blog-posts/battery-pack-certification-europe
- Monolithic Power, USB Type-C: https://media.monolithicpower.cn/mps_cms_document/u/s/usb-type-c-charging-connectors-design-optim-interop_r1.0.pdf
- Digi-Key forum, USB-C 5 V/3 A: https://forum.digikey.com/t/simple-way-to-use-usb-type-c-to-get-5v-at-up-to-3a-15w/7016
- USB-IF, USB Power Delivery: https://www.usb.org/usb-charger-pd
- Texas Instruments BQ24074: https://www.ti.com/product/BQ24074
- Monolithic Power, power path: https://www.monolithicpower.com/en/power-path-management-in-charger-ics/
- Granite River Labs, Qi2: https://www.graniteriverlabs.com/en-us/technical-blog/2024-qi2-technical-compliance
- Wireless Power Consortium, Qi FOD: https://www.wirelesspowerconsortium.com/media/klfjiwfh/qi-v13-fod.pdf
- Allion, måling av trådlaus lading: https://www.allion.com/?p=5581
- Galaxus, Qi2-test: https://www.galaxus.de/en/page/qi2-test-revelations-iphone-charges-faster-with-the-competition-40668

### Termikk og optikk
- Digi-Key, Effective Thermal Management of LED Arrays: https://www.digikey.co.uk/en/articles/effective-thermal-management-of-led-arrays
- Cree, XLamp Thermal Management (ikkje opna): https://www.mouser.lt/pdfDocs/XLampThermalManagement.pdf
- Röhm/Zenit, PLEXIGLAS LED 0M200 SC: https://www.zenit.cz/public/media/Plasty/Zenit_PLEXIGLAS_LED-0M200SC_EN.pdf
- Röhm/Zenit, PLEXIGLAS Satinice: https://www.zenit.cz/public/media/Plasty/Zenit_Technicky_List_Plasty_Plexiglas_Satinice_AJ.pdf
- Trilux, covers: https://www.trilux.com/en/lighting-practice/lighting-equipment/luminaires/photometric-properties/covers
- Induflex, diffusorar: https://www.induflex.dk/uk/products/lighting/diffusers-for-lamps/
- Pyrasied, light diffusers: https://shop.pyrasied.com/en/materials/light-diffusers
- Fagerhult, EN 12464-1 i korte trekk: https://www.fagerhult.com/knowledge/light-planning/en-12464-1/lighting-of-indoor-workplaces/standard-en-12464-1-in-brief/

### Betjening
- US 11,019,705 (lampe med rørslesensor): https://patentimages.storage.googleapis.com/7a/ec/a0/9a0d3ea0df215e/US11019705.pdf
- Occhio, gestestyring: https://www.occhio.de/en/licht-gestensteuerung
- ST LIS2DH12: https://www.st.com/en/mems-and-sensors/lis2dh12.html og https://www.digikey.com/en/products/detail/stmicroelectronics/LIS2DH12TR/4899838

### Regelverk og standardar
- Forordning (EU) 2019/2020, artikkel 4: https://www.legislation.gov.uk/eur/2019/2020/article/4/adopted
- Forordning (EU) 2019/2020, vedlegg II: https://legislation.gov.uk/eur/2019/2020/annex/II/2020-01-31 og https://gesetze.legal/eu/vo_eu_2019_2020/anhang_ii
- Batteriforordninga, artikkel 11 (omtale): https://www.compliancegate.com/removable-and-replaceable-battery-requirements-european-union/
- Cooley om Kommisjonen si rettleiing: https://products.cooley.com/2025/02/13/european-commission-publishes-guidance-on-eu-batteries-regulation-removability-requirements/
- Kommisjonen si rettleiing C/2025/214: https://eur-lex.europa.eu/eli/C/2025/214/oj/eng
- Delegert forordning 2026, nye unntak: https://www.lovguiden.dk/en/det-offentlige/eur-lex-eu-tidende/2026-10-22-seks-nye-undtagelser-fra-krav-om-udskiftelige-batterier-i-eu og https://europalov.no/rettsakt/batteriforordningen-2023-utfyllende-bestemmelser-om-unntak-for-muligheten-til-fjerne-erstatte/id-34790
- Forordning (EU) 2025/2052: https://eur-lex.europa.eu/eli/reg/2025/2052 og https://www.nemko.com/blog/ecodesign-2025/2052-is-coming-what-makers-of-power-accessories-need-to-change-before-december-2028
- Felles ladar, Europakommisjonen: https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/radio-equipment-directive-red/one-common-charging-solution-all_en
- EN 60598-2-4:2018: https://www.evs.ee/en/evs-en-60598-2-4-2018 og https://iteh.es/catalog/standards/clc/bb5ec2e2-e267-4b38-a153-9c570a18d6c8/en-60598-2-4-2018
- IEC 60598-1: https://webstore.iec.ch/publication/61414 og https://genorma.com/en/standards/en-iec-60598-1-2024/amp
- Lågspenningsdirektivet, omtale: https://www.element.com/resources/articles/the-european-commissions-guide-to-the-low-voltage-directive og https://ib-lenhardt.com/kb/faq/low-voltage-directive
- Testing av LED-armaturar: https://siq.si/?p=25921 og https://www.eurofins.com/electrical-and-electronics/industries/electrical-consumer-products/lighting-luminaires/
- Lagt til i faktasjekk, primærkjelder:
  - Forordning (EU) 2023/1542, konsolidert versjon 13.08.2026 (artikkel 3, 11 og 96): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02023R1542-20260813
  - Delegert forordning (EU) 2026/1770 (nye unntak i artikkel 11 nr. 2): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32026R1770
  - Forordning (EU) 2019/2020, konsolidert versjon 01.09.2021 (artikkel 2 og 4, vedlegg I, II og III): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02019R2020-20210901
  - Direktiv 2014/35/EU (artikkel 1): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014L0035
  - Direktiv (EU) 2022/2380 (vedlegg Ia): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022L2380
  - Direktiv (EU) 2024/1799 (vedlegg II): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024L1799
  - IEC 60598-2-4:2017, samandrag hos EVS: https://www.evs.ee/en/iec-60598-2-4-2017
  - Zumtobel, The Lighting Handbook (attgjeving av EN 12464-1, s. 14 og 36): https://resources.zumtobel.com/PDB/teaser/EN/lichthandbuch.pdf

### Kostnad
- Samsung LM301B, rettleiande prisar: https://zenode.ai/parts/u3rt25jzi2-samsung-semiconductor-inc-SPMWHD32AMVKXAV3SW og https://sg.element14.com/samsung/spmwhd32amd5xav3sk/led-hb-white-3000k-38lm-3030/dp/3003230
- 18650-prisar: https://ormix.lv/en/product/37351 og https://www.18650batterystore.com/collections/flat-top-18650-batteries
- Sprøytestøypeverktøy: https://hubs.com/knowledge-base/how-much-does-injection-molding-cost og https://www.rapiddirect.com/blog/injection-molding-quote-cost-breakdown/
- Prisstruktur: https://predictabledesigns.com/how-to-price-your-product-for-various-distribution-channels/ og https://inventorsdigest.com/inventing-101-your-profit-formula

---

## Faktasjekk

Gjennomført 12.11.2026 av ein uavhengig faktasjekkar. Påstandane under er dei designavgjerdene kviler mest på. Kvar påstand er kontrollert mot primærkjelde der det let seg gjere: lovtekst på EUR-Lex (opna direkte, inkludert konsoliderte versjonar), produsentane sine eigne dokument og datablad. Reknestykka er rekna på nytt. Nettsøk var ikkje tilgjengeleg i denne runden (søkjekvoten var brukt opp), så kontrollen byggjer på direkte oppslag i kjende kjelder. Standardar bak betalingsmur (EN 12464-1, EN 60598, IEEE 1789) er berre kontrollerte via samandrag og attgjevingar.

Dom: **stadfesta** = stemmer med kjelda. **retta** = feil eller manglar som er retta i teksten over. **ikkje stadfesta** = kunne ikkje kontrollerast, eller kjelda seier noko anna enn det ho er sitert for.

| Påstand | Dom | Kjelde | Merknad |
|---|---|---|---|
| Batteriforordninga (EU) 2023/1542 artikkel 11 gjeld frå 18. februar 2027: sluttbrukaren skal kunne ta ut og byte berbare batteri med verktøy i vanleg handel, kravet gjeld heile batteriet, batteriet skal finnast som reservedel i minst fem år, og programvare skal ikkje hindre byte | stadfesta | [EUR-Lex, artikkel 3 nr. 1 punkt 9, artikkel 11 og artikkel 96 nr. 2 bokstav a, konsolidert 13.08.2026](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02023R1542-20260813) | Ordlyden stemmer. Artikkel 11 er ikkje utsett per 13.08.2026. COM(2025) 981 foreslår berre endring i artikkel 11 nr. 5 (batteri til lette køyretøy). Lagt til i teksten: plikta til å leggje ved instruksjonar og tryggleiksinformasjon om batteribyte og halde dei tilgjengelege på nett. Innlemming i norsk rett er ikkje kontrollert. |
| Ei delegert forordning frå 14. juli 2026 la til seks unntakskategoriar; lamper er ikkje nemnde | stadfesta | [Delegert forordning (EU) 2026/1770](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32026R1770), kunngjord 22.10.2026 | Nummer og kategoriar er lagde inn i teksten. Dei nye unntaka (bokstav c–h) gjeld kroppsborne einingar, leiker, steiketermometer, Ex-utstyr, medisindosering og telematikk. Ei bordlampe har ingen heimel for unntak. |
| IP-klasse åleine er ikkje nok grunngjeving for vassunntaket (Cooley) | ikkje stadfesta | [C/2025/214](https://eur-lex.europa.eu/eli/C/2025/214/oj/eng), engelsk og dansk utgåve | Den kunngjorde teksten seier bokstavleg at IP-klassen åleine «is considered as sufficient», stikk i strid med setninga framfor og med Cooley si lesing. Truleg ein redaksjonsfeil. Ikkje siter dette punktet. Konklusjonen for lampa står likevel: unntaket krev eit apparat som er spesifikt konstruert for hovudsakleg bruk i vått miljø og er meint å kunne vaskast eller skyljast. Rettleiinga viser til EN 45554:2020 for verktøytypar (stadfesta). |
| Forordning (EU) 2019/2020 artikkel 4: lyskjelde og separat drivar skal kunne bytast med vanleg verktøy utan varig skade på produktet, elles teknisk grunngjeving; om lyskjelda kan bytast skal stå på emballasjen | stadfesta | [EUR-Lex, konsolidert 01.09.2021](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02019R2020-20210901) | Ordlyden stemmer. Artikkel 4 nr. 3 krev i tillegg at lyskjelde og drivar kan demonterast ved endt levetid, med rettleiing på ope nettsted. |
| Om 2019/2020 gjeld ei lampe som går på batteri (stod som «ikkje verifisert») | retta | Same, vedlegg III punkt 2 bokstav c og vedlegg I punkt 44 | Unntaket for «battery-operated products» finst, men er avgrensa til produkt som berre går på eiga straumkjelde utan direkte eller indirekte nettilkopling. Hybridlampa rapporten tilrår (lys med USB-leidning i) fell etter ordlyden truleg utanfor unntaket. Dette er ei tolking av lovteksten og er ikkje stadfesta mot rettleiing frå Kommisjonen. Northern oppgjev energiklasse F for lyskjelda i Snowball Portable. |
| EU-krav til flimmer: Pst LM ≤ 1,0 og SVM ≤ 0,4 ved full last (0,9 fram til 1.9.2024), standby høgst 0,5 W | stadfesta | Same, vedlegg II punkt 1 og tabell 4 | Flimmerkrava gjeld berre LED- og OLED-lyskjelder for nettspenning (MLS). Ein 5 V-modul er ikkje formelt omfatta av desse to krava. |
| Northern Snowball Portable: 3 W, 2700 K, tre dimmesteg, IP44, 8 timar, 0,5 kg, munnblåse opalglas, rustfritt stål, 1 790 kr, klasse III; lumen 158, 200 eller 240; utskiftbart batteri og LED-modul stod som «ikkje verifisert» | retta | [northern.no](https://www.northern.no/en/products/snowball-portable-table-lamp), [produktark](https://www.northern.no/cdn/shop/files/Northern_product_sheet_-_Snowball_portable_table_lamp.pdf?v=11906401054735407144), [brukarrettleiing](https://www.northern.no/cdn/shop/files/User_manual_-_Snowball_portable_table.pdf?v=10090650407803861463), [smow](https://www.smow.com/northern/snowball-portable-table-lamp.html) | Grunntala stemmer. Northern sine eigne kjelder sprikjer: 158 lm (produktside, brukarrettleiing) mot 60/120/200 lm (produktark); ladetid 4–5 timar (produktark) mot 6–8 timar (brukarrettleiing); dimmesteg 10/50/100 % (produktside). 240 lm finst berre hos smow. Produktsida stadfestar «Replaceable battery» og «Replaceable LED module with push connector», men batterikapasitet er ikkje oppgjeven, batteriet står ikkje på reservedelslista, og brukarrettleiinga seier «Only use the included battery». Mål: 33 cm høg, kule Ø 7 cm, fot 9 cm. |
| Louis Poulsen Panthella 160 Portable V3: 2,5 W, 150/50/15 lm, 8,5/25,5/79 timar, 18650 på 3100 mAh, 500 syklusar til 70 %, L70 60 000 timar, 5 timar lading, IP44, klasse III, 0,4 kg; batteriet kan bytast av sluttbrukar | retta | [Louis Poulsen, faktaark](https://smow.fr/pdf/louis-poulsen-panthella-160-v3-factsheet.pdf) | Alle tal stemmer. Retta: faktaarket er motstridande om kven som kan byte batteriet («qualified person» i produktinformasjonen, «end-consumer» i tabellen), og typeskiltet seier «Replaceable with listed battery only». Typeskiltet oppgjev 3,7 V, ikkje 3,6 V; systemutbyttet er difor retta frå 114 til 111 lm/W. |
| &Tradition Flowerpot VP9: 104 lm, CRI > 90, 5200 mAh, lading via Micro-USB, tre nivå 100/50/20 % | retta | [&Tradition, faktaark](https://www.assetslibrary.com/asset/586904ba-bd72-495c-bea8-38a9ae347f78/ATD_Product-Fact-Sheets_Flowerpot_VP9.pdf), [bruksrettleiing](https://www.assetslibrary.com/asset/c0a85983-134f-4603-9063-92a837a1b931/ATD_Instruction-Manuals_Flowerpot_VP9.pdf) | Retta: CRI > 80 og magnetisk ladekabel med USB-A. 3 W, 2700 K, 10 timar, 8 timar lading, 5 V/2 A, IP44, klasse III og 0,8 kg stemmer. Lumen og mAh står ikkje i &Tradition sine dokument og er merkte «ikkje stadfesta»; systemutbyttet på 54 lm/W kviler på desse to tala. Dimmenivåa sprikjer mellom faktaark (100/70/40 %) og bruksrettleiing (100/50/20 %). |
| Zafferano Poldina Pro: 2,2 W, 188 lm, 3000 K, CRI > 80, 2 × 18650 à 2200 mAh «replaceable», 6 timar lading, ladebase, om lag 450 ladingar | stadfesta | [Zafferano, spesifikasjonsark](https://cdn.shopify.com/s/files/1/0591/2484/2705/files/Specification_Sheet_Poldina_Pro.pdf) | Ingen avvik. |
| Samsung INR21700-50E: min. 4900 mAh, 3,63 V, 4,2 V ladespenning, standardlading 2450 mA i 4 timar, minst 80 % etter 500 syklusar, maks 69,5 g, maks Ø 21,25 × 70,80 mm, lading 0–45 °C; 17,8 Wh og 256 Wh/kg | stadfesta | [Samsung SDI, datablad](https://shop.aceongroup.com/cdn/shop/files/RLII-CSI-1618_Samsung_50E_DATASHEET.pdf) | 80 % er rekna av «rated capacity» (4753 mAh), altså minst 3802 mAh, målt ved 1C utlading. Databladet føreset vernefunksjon i batteripakken (note 1). |
| Battery University: syklustal mot utladingsdjupn og ladespenning (4,06 V gjev 600–1000 syklusar og 81 % kapasitet), lagringstap, og tabellen over NMC, LCO og LFP | stadfesta | [BU-808](https://batteryuniversity.com/article/bu-808-how-to-prolong-lithium-based-batteries), [BU-205](https://batteryuniversity.com/article/bu-205-types-of-lithium-ion) | Alle tal stemmer. Tala er estimat frå ei fagformidlingsside, ikkje fagfellevurdert forsking. |
| Reknestykka: tabell 2 med følsemd, ladetid, kjøleflate, luminans, lux på bord og ansikt, kostnadsmål og BOM-sum | stadfesta | Eiga kontrollrekning | Alle tal lét seg rekne på nytt med føresetnadene som står i teksten. Merk at hovudføresetnaden 80 lm/W er høgare enn det Northern sine oppgjevne tal for Snowball Portable tilseier (53–67 lm/W med 158–200 lm og 3 W). For konsept med opalglas er 60 lm/W-kolonnen det forsiktige valet. |
| USB-C utan Power Delivery: 5,1 kΩ på kvar CC-pinne, kjelda melder standardstraum, 1,5 A eller 3 A (7,5 W eller 15 W); «7,5 W som trygt nivå» og «to motstandar» som ladeløysing | retta | [Monolithic Power](https://media.monolithicpower.cn/mps_cms_document/u/s/usb-type-c-charging-connectors-design-optim-interop_r1.0.pdf), [Digi-Key forum](https://forum.digikey.com/t/simple-way-to-use-usb-type-c-to-get-5v-at-up-to-3a-15w/7016), [USB-IF](https://www.usb.org/usb-charger-pd) | Fakta stemmer, også 100 W og 240 W for Power Delivery. Retta tolking: 1,5 A er ikkje garantert frå ein vilkårleg ladar, og ei lampe med berre motstandar har berre lov til å trekkje standardstraum. For å trekkje 1,5 A eller 3 A må ladekretsen måle CC-spenninga. Northern oppgjev sjølv inngang 5 V – 3 A for Snowball Portable. |
| IEEE 1789-2015: ingen avgrensing over 1250 Hz (låg risiko) og over 3000 Hz (ingen observerbar effekt) | stadfesta | [LightNOW, attgjeving av DOE](https://www.lightnowblog.com/2015/08/brodrick-on-new-recommended-practice-for-led-flicker/) | Formlane stemmer (0,08 og 0,0333 gonger frekvensen). Sekundærkjelde; standarden sjølv er ikkje lesen. |
| Kamerastriper: uakseptabelt ved 900–1500 Hz PWM og 50 % dimming eller lågare; ingen striper ved om lag 10 kHz og 100 % | stadfesta | [LEDs Magazine/Penn State](https://www.buildings.com/specialty-ssl/article/14299599/video-lighting-iso-settings-and-led-dimming-impact-video-quality) | Eitt kamera (Sony A7S II, 24 bilete/s, 1/125 s). Kan ikkje overførast direkte til webkamera. |
| EN 12464-1 krev 500 lx på kontorarbeidsplass; «Fagerhult argumenterer for om lag 300 lx»; sylindrisk 50–150 lx | retta | [Fagerhult](https://www.fagerhult.com/knowledge/light-planning/en-12464-1/lighting-of-indoor-workplaces/standard-en-12464-1-in-brief/), [Zumtobel, The Lighting Handbook, s. 36](https://resources.zumtobel.com/PDB/teaser/EN/lichthandbuch.pdf) | 500 lx og 50–150 lx stemmer. Feillesing retta: Fagerhult sine 300 lx gjeld lys på takflata, ikkje arbeidsfeltet. I standarden er 300 lx kravet til arkivering og kopiering; skriving, lesing og databehandling har 500 lx. Standarden er skriven for arbeidsplassar innandørs; for eit heimekontor er han eit referansenivå, ikkje eit krav. |
| 3000 cd/m² som luminansreferanse (stod som «ikkje verifisert») | retta | [Zumtobel, The Lighting Handbook, s. 14](https://resources.zumtobel.com/PDB/teaser/EN/lichthandbuch.pdf) | Delvis stadfesta via sekundærkjelde: EN 12464-1 krev armaturluminans under 3000 eller 1500 cd/m² ved 65° ved skjermarbeidsplassar. Grensa står under «Reflected glare» og gjeld spegling i skjerm, ikkje direkte innsyn i ei bordlampe. Formelen L = Φ/(π·A) og tabellen er rette. |
| Termikk: all tilført effekt «eller 85 %» blir rekna som varme; naturleg konveksjon 2–15 W/m²K; 10 kvadrattommar kjøleflate per watt | retta | [Digi-Key](https://www.digikey.co.uk/en/articles/effective-thermal-management-of-led-arrays) | Konveksjonstalet og tommelfingerregelen stemmer. Talet 85 % står ikkje i artikkelen som varmeandel (det gjeld finneorientering) og er teke ut. Rapporten si eiga antaking om 60–75 % varme er merkt som antaking og står. |
| Lågspenningsdirektivet 2014/35/EU gjeld 50–1000 V AC og 75–1500 V DC | stadfesta | [EUR-Lex, artikkel 1](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014L0035) | Ei lampe med 5 V inn og 3,7 V batteri fell utanfor; ein medfølgjande nettadapter fell innanfor. |
| EN 60598-2-4:2018 (flyttbare armaturar opp til 250 V, stabilitetstest med lyskjelde, IPX4 utandørs); IEC 60598-1 i tiande utgåve 2024; IEC 62133-2:2017 med A1:2021 | stadfesta | [EVS, EN 60598-2-4](https://www.evs.ee/en/evs-en-60598-2-4-2018), [EVS, IEC 60598-2-4:2017](https://www.evs.ee/en/iec-60598-2-4-2017), [Genorma](https://genorma.com/en/standards/en-iec-60598-1-2024/amp), [batterydesign.net](https://www.batterydesign.net/legislation-rules-and-regulations/iec-62133-2/) | IEC-lenkja i rapporten viste den tilbaketrekte 2020-utgåva; presisert i teksten. iteh.es-lenkja er død. Vinklar og temperaturgrenser er framleis ikkje verifiserte. |
| Felles ladar-direktivet (EU) 2022/2380 omfattar ikkje lamper (lista stod som «ikkje verifisert») | stadfesta | [EUR-Lex, vedlegg Ia](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022L2380) | 13 kategoriar radioutstyr, ingen lamper. Presisert i teksten. |
| Forordning (EU) 2025/2052: gjeld frå 14. desember 2028, minst éin USB-C-port på straumforsyningar, 0,50 W kviletak for trådlause ladeplater | stadfesta | [EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32025R2052) | Omfattar òg batteriladarar for standardbatteri og USB-C-kablar (kabel med USB-C-plugg i begge endar, merkt 60 W eller 240 W). Ein USB-C-kabel som følgjer med lampa, er truleg omfatta frå same dato (tolking). |
| Trådlaus lading: 63 % mot 81 % verknadsgrad; «sparer rundt 30 % ladeenergi» | retta | [Allion](https://www.allion.com/?p=5581); eiga kontrollrekning | Måletala stemmer. Trådlaus lading krev rundt 30 % meir energi enn kabel, og det svarar til om lag 22 % spart ved å velje kabel. Formuleringa i implikasjon 8 er retta. |
| Transmisjon: PLEXIGLAS LED 0M200 SC 72 % ved 3 mm; klassisk opal ca. 30 %, optimaliserte diffusorar 60–90 % | stadfesta | [Röhm/Zenit](https://www.zenit.cz/public/media/Plasty/Zenit_PLEXIGLAS_LED-0M200SC_EN.pdf), [Pyrasied](https://shop.pyrasied.com/en/materials/light-diffusers) | Ingen avvik. |
| Opale deksel «ofte under 50 %» (Trilux) og «30–70 %» (Induflex) | ikkje stadfesta | Lenkjene i rapporten | Begge lenkjene gav 404 den 12.11.2026. Spennet 30–90 % i oppsummeringa er dekt av Pyrasied. |
| Reparasjonsdirektivet (EU) 2024/1799: står lamper på produktlista? (ope spørsmål 11) | retta | [EUR-Lex, vedlegg II](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024L1799) | Avklart: lamper og lyskjelder står ikkje blant dei ti produktgruppene. Reparasjonsplikta gjeld ikkje lamper direkte. Dei bindande krava kjem frå batteriforordninga artikkel 11 og truleg 2019/2020 artikkel 4. Viktig for korleis prosjektet viser til «Right to repair». |
| Standardcelle i haldar «oppfyller kravet med god margin og gjer reservedelen uavhengig av leverandøren» (tolking) | ikkje stadfesta | [C/2025/214](https://eur-lex.europa.eu/eli/C/2025/214/oj/eng), Samsung-databladet, produsentdokumenta over | Uttakskravet er oppfylt. At brukaren trygt kan setje inn ei vilkårleg laus Li-ion-celle, er ikkje dekt: rettleiinga krev at eit kompatibelt batteri ikkje utgjer tryggleiksrisiko, og alle tre referansemerka viser til sitt eige batteri. |
| Bridgelux Vesta (115 og 104 lm/W, 4,96 €), Cree-referansedesign (40–75 %, 4000 K og 1800 K), Philips E14 (470 lm, 3,4 W, 15 000 timar), Logitech Litra Glow, TI BQ24074, Tala Muse (fire og to skruar, éin plugg), Samsung 35E, Qi-effektnivåa (5 W og 15 W), Zhaga (26 bøker), forelesingstala (235 og 74 W/mK, 6–16 veker) | stadfesta | Lenkjene i rapporten; lokale filer i `context/` | Ingen avvik. Vekta på 48 g for Samsung 35E er spesifikasjon, ikkje måling. |
| Samsung LM301B (220 lm/W; 28–32 lm ved CRI 90), Lutron (10 % målt = 32 % opplevd), Elgato Key Light Air | ikkje stadfesta | Lenkjene i rapporten | Samsung- og Lutron-lenkjene blir vidaresende til framsider; Elgato gav HTTP 403. Tala er rimelege, men ikkje kontrollerte. Kvadratrotregelen er rekna rett. |

**Ikkje kontrollert i denne runden:** BenQ ScreenBar, prisankra i punkt 12 (LED, celler, verktøy, påslagsfaktor), framandlekam-deteksjon i Qi, Galaxus, Enttec, Acuity, Bridgelux V-serien, Fermob, Occhio, ST LIS2DH12 og patentet. Desse er merkte «via søkjetreff» i rapporten og bør ikkje siterast utan eigen kontroll.

**Tre ting som bør inn i kravspesifikasjonen etter faktasjekken:**
1. Batteriet skal kunne takast ut og bytast av sluttbrukaren med vanleg verktøy, med batteri som reservedel i minst fem år og instruksjonar på nett (artikkel 11, frå 18.02.2027). Merk at dette er eit lovkrav frå 2027, ikkje eit frivillig tiltak. I dokumenta som er kontrollerte her, er brukarbyte av batteriet ikkje dokumentert for Snowball Portable.
2. Ei lampe som òg lyser med leidning, bør utformast som om 2019/2020 artikkel 4 gjeld: lyskjelde og drivar skal kunne bytast med vanleg verktøy, og det skal stå på emballasjen om sluttbrukar eller fagperson kan byte dei.
3. Skal lampa dekkje standardnivået for lese- og skjermarbeid i EN 12464-1, er målet 500 lx på arbeidsfeltet, ikkje 300 lx. Romlyset kan dekkje ein del av dette.
