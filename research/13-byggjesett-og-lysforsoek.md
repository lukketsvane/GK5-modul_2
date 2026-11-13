# 13 Byggjesett og lysforsøk: projektoren, optiske ark og forsøk som kostar null

Dato: 12.11.2026. Område: kva du kan prøve fysisk før konseptgjennomgangen om seks dagar, med det du alt har.

**Slik les du rapporten**

- **FAKTA** = påstand med kjelde rett etter. «(søkjetreff)» tyder at kjelda berre er sett som søkjetreff eller samandrag, ikkje opna i fulltekst.
- **EIGA UTREKNING** = reknestykke eg har gjort. Formel og føresetnader står ved kvart stykke. Kvart stykke er rekna to gonger: for hand og med eit lite skript, og der det går, med to ulike metodar.
- **ANTAKING** = føresetnad som ikkje er kontrollert.
- **TOLKING** = mi vurdering, bygd på fakta.
- **UKJENT** = ikkje funne. Då står det korleis du finn det ut sjølv.
- Rapporten byggjer på rapport 03 (lys og syn) og 05 (teknologi). Tal derifrå blir viste til som «03 kap. x» og «05 punkt x», ikkje gjentekne.
- ANTAKING frå oppdraget: printaren er ein Bambu Lab P1S med byggjevolum 256 × 256 × 256 mm. Byggjevolumet for P1S er stadfesta i wikien til Bambu Lab ([FAQ](https://wiki.bambulab.com/en/p1/manual/faq), søkjetreff).
- ANTAKING: Arduinoen er ein Uno eller Nano med ATmega328P. Kodeskissene er ikkje testa på maskinvare.
- Norske prisar er berre tekne med når eg har sett dei på butikksida 12.11.2026. URL står ved prisen.

---

## Kort oppsummering

1. **Projektoren er truleg ein 3M 2000 («M2000»): berbar, samanleggbar og reflekterande.** Bruksrettleiing og deleliste er funne. Dei europeiske variantane har pære FSX, 230 V og 400 W, kopla rett på nettspenning utan transformator. Plata i botnen er ein fresnelspegel på 285 × 285 mm med brennvidd 187,1 mm. Projeksjonslinsa har om lag 27 til 29 cm brennvidd (eiga utrekning). Dokumenta nemner verken vifte eller termosikring.
2. **Set ikkje straum på projektoren att.** Halogenpæra må vere 250 til 800 °C for å fungere, medan PLA mjuknar ved om lag 55 °C og PETG ved om lag 68 °C. Den demonterte projektoren har open nettspenning. Fresnelplata fangar opptil 80 W sollys og samlar det i ein liten flekk.
3. **Det verdfulle er optikken:** fresnelplata, projeksjonslinsa, frontflatespegelen og stolpen med ledd. Saman med ei LED-kjelde på 1 til 5 W gjev dei same lærdom som halogenpæra, utan faren.
4. **Lys på veggen som ansiktslys er dyrt.** 100 lx på ansiktet krev 220 til 600 lm på veggen, alt etter avstand og feltstorleik. Eit lite felt blir opptil 4,5 gonger så lyst som ein skjerm på 100 cd/m². Eit stort felt (1 m breitt) hamnar på skjermnivå. Eit realistisk mål er 50 lx frå veggen.
5. **500 lx på 60 × 40 cm krev 120 lm på feltet.** Eit skarpt avgrensa felt frå ei kompakt lampe krev kort brennvidd (40 til 65 mm). Projeksjonslinsa er for lang til det, men høver til forsøk med 1 til 2 m kast.
6. **Kollimert lys er ikkje det ei bordlampe treng, men kjeldeposisjonen framfor fresnelplata er eit godt styringsgrep.** Kjelda 10 cm frå plata gjev eit felt på om lag 80 cm, målt 40 cm unna. Kjelda 19 cm frå plata gjev parallelt lys med breidd 28,5 cm.
7. **Printlinjene verkar som sylinderlinser og spreier lyset på tvers av linjene.** Klarast resultat i PETG: tynne lag, låg fart, vifta av, 100 % fyll i éi retning og litt over 100 % flyt.
8. **Arka frå LCD-skjermane er ein ferdig optikkpakke.** Ein skjermprodusent oppgjev at nedre prismeark aukar luminansen 1,55 gonger og øvre 1,33 gonger. Gevinsten føreset eit kvitt eller speglande holrom bak arka.
9. **Lyskjelder med kontrollert pris:** USB-lyslenke på 3 m til 159 kr og to LED-pærer på 806 lm til 89 kr (IKEA). Telefonlykta er gratis og er den beste punktkjelda du har.
10. **Standard-PWM gjev striper i kamera.** Arduino har 490 Hz som standard, men kan setjast til 3,9 eller 31 kHz. micro:bit når 3,9 kHz. Luxappar viste i ein laboratorietest i snitt om lag 60 % feil og opptil 113 %, så mål relativt og kalibrer mot ei pære med kjend lysfluks.

---

## 1. Projektoren: kva sit i ein 3M 2000

Kjeldene er to 3M-dokument for «3M 2000 Overhead Projector»:

- **BR** = bruksrettleiinga, 15 sider. Side 1, 2, 5, 6, 7, 9, 10, 11 og 12 er lesne som sidebilete. ([ManualsLib](https://www.manualslib.com/manual/872528/3m-2000.html))
- **DL** = delelista med sprengskisser («Illustrated Parts Breakdown»), 27 sider. ([ManualsOnline](https://music.manualsonline.com/manuals/mfg/3m/2000_1.html), same dokument hos [ManualsLib](https://www.manualslib.com/manual/655253/3m-2000.html) og [ManualsDump](https://manualsdump.com/en/manuals/3m-2000model/163128/26))

Eit servicehefte med koplingsskjema er ikkje funne fritt tilgjengeleg.

### 1.1 Kva dokumenta seier (FAKTA)

| Punkt | Funn | Kjelde |
|---|---|---|
| Type | Berbar overheadprojektor i koffert. Stolpen blir felt opp, projeksjonshovudet vippa opp, og loket blir snudd og lagt på med projeksjonsflata opp. Lampa sit i hovudet, bak ei luke som blir opna med ein mynt. | BR s. 1, 6, 7 og 11 |
| Variantar | 22 variantar med bokstavkode. Europa: AHST og AHSV, 230 V og 50 Hz. Storbritannia, Australia og Sør-Afrika: 240 V. USA: 120 eller 127 V. Japan: 100 V. | DL Appendix A |
| Pære | 230 V-variantane: FSX, 230 V, 400 W. 240 V-variantane: FSY, 240 V, 400 W. USA og Japan: EVW, 82 V (merkelappen i delelista seier 82 V og 250 W). Éin variant (BHQS) har EWF-pære. Éi pære er montert, og det finst ingen pærevekslar. | BR s. 11 og 12, DL seksjon 3, 4, 5, 12 og Appendix A |
| Data for FSX-pæra | Osram 93592: sokkel GY9.5, 400 W, 230 V, 3200 K, levetid 75 timar, diameter 20 mm, lengd 77 mm. | [Firstlight](https://en.firstlight.nl/lamps/entertainment-and-studio-lighting/halogen-lamps-110-240v/osram-93592-400w-230v-gy9-5-fsx-fsy/) |
| Straumforsyning | FSX og FSY: «Line», altså nettspenning rett til pæra. EVW: diode. Transformator finst berre i dei japanske variantane og i BHQS. Projektoren skal ha jorda kontakt. | DL Appendix A, seksjon 2 og 11, BR s. 2 |
| Brytar og sikring | Vippebrytar i sokkelen. Sikring 5 × 20 mm, treg. Delelista seier 5 A for alle utanom Japan. Spesifikasjonstabellen seier 2,5 for dei europeiske variantane og 3,0 for 2000 AG. Tala stemmer ikkje overeins. | DL seksjon 2 og Appendix A, BR s. 7 |
| Forrigling | Dei internasjonale variantane, mellom anna AHST og AHSV, har forriglingsbrytar med aktuator i fokusmekanismen. | DL seksjon 10 |
| Motstand | Eit motstandssett («resistor kit»), 1,2 Ω i fire USA-variantar. Funksjonen er ikkje forklart. | DL seksjon 13 |
| Fresnelplate | «Projection slate»: reflekterande fresnellinse med brennvidd 187,1 mm. A4-utgåva er 285 × 285 mm, den amerikanske 267 × 267 mm. Utgåve S høyrer til singlet-variantane og T til triplet-variantane, slik eg les tabellane. | DL seksjon 14, BR s. 12 |
| Projeksjonslinse | Singlet (éi linse) eller triplet (tre linser), i ope eller lukka hovud. Fokusratt på hovudet. Brennvidda står ikkje i dokumenta. | DL seksjon 8, 9, 10 og Appendix A, BR s. 7 |
| Spegel | Frontflatespegel i projeksjonshovudet. Han blir vippa opp ved bruk. | BR s. 7 og 9 |
| Kjøling | Slisser og opningar i sokkel og hovud gjev ventilasjon og må ikkje dekkjast til. Rista på hovudet og lampeluka blir varme. Inga vifte er nemnd, verken i bruksrettleiinga eller som del i delelista. | BR s. 2, DL seksjon 0 til 15 |
| Termosikring | Ikkje nemnd, verken i bruksrettleiinga eller som del i delelista. | BR s. 2, DL seksjon 0 til 15 |
| Biletstorleik | 102 × 102 cm på 101 cm avstand, 127 × 127 på 127 cm, 152 × 152 på 152 cm og 191 × 191 cm på 190 cm. | BR s. 5 |
| Lysstyrke og vekt | 1600 lumen for varianten 2000AG ([Aztek](https://www.aztekcomputers.com/2000ag-portable-overhead-projector-with-1600-lumens-3m/p)). Vekt 14 pund, om lag 6,4 kg, konveksjonskjøling og 11,5 tommar brennvidd på singlet-linsa ([B&H](https://www.bhphotovideo.com/c/product/1003-REG/3M_HK_4000_0038_4_2000AG_Portable_Overhead_Projector.html/overview), søkjetreff). | forhandlarar |
| Alder | Delelista har produksjonskodar for 1994 og 1995 og er utgjeven frå mars 1992 (utgjevingsdatoen er søkjetreff). | DL s. iii |

### 1.2 Optisk oppbygging

- FAKTA: Lampa sit i hovudet (BR s. 11). Plata i botnen er ei reflekterande fresnellinse (DL seksjon 14). Linsa og vippespegelen sit i hovudet (BR s. 7 og 9).
- FAKTA: I ein refleksjonsprojektor lyser ei lyskjelde i hovudet ned på ein fresnelspegel, og det reflekterte lyset går til projeksjonslinsa og ein spegel ([US 4,636,050](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4636050), søkjetreff). Oppgåva til fresnelen i ein overheadprojektor er å samle lyset i ei kjegle mot projeksjonslinsa ([Wikipedia, Overhead projector](https://en.wikipedia.org/wiki/Overhead_projector)).
- TOLKING: Lyset går altså lampe, plate, tilbake opp gjennom transparenten, linse, spegel, vegg. Plata gjer to jobbar: ho er projeksjonsflate, og ho avbildar glødetråden inn i linsa.
- EIGA UTREKNING, brennvidda til projeksjonslinsa. Tynn linse: 1/f = 1/u + 1/v, forstørring m = v/u ([OpenStax, Thin lenses](https://openstax.org/books/university-physics-volume-3/pages/2-4-thin-lenses)). Då er v = f(1 + m). Tabellen i BR s. 5 gjev biletbreidd W og avstand D. Med m = W/s, der s er platebreidda, veks D lineært med m, og stigningstalet er f.
  - A4-plata, s = 285 mm: (1900 - 1010) / (1910/285 - 1020/285) = 890 / (6,70 - 3,58) = 285 mm.
  - 10,5-tommarsplata, s = 267 mm: 267 mm.
  - Lineær regresjon over alle fire radene gjev 284,5 og 266,6 mm.
  - Kontroll: forhandlaren oppgjev 11,5 tommar, altså 292 mm, for singlet-linsa (søkjetreff).
  - Resultat: **om lag 27 til 29 cm**. Uvissa kjem av at tabellen er avrunda, og at eg ikkje veit om heile plata blir avbilda.
- EIGA UTREKNING, høgda på hovudet. Linsa står u = f(1 + 1/m) frå plata, målt langs lysvegen: 285 × (1 + 1/3,58) = 364 mm ved minste bilete og 285 × (1 + 1/6,70) = 327 mm ved største.
- EIGA UTREKNING, fresnelspegelen. Spegellikninga er 1/s + 1/s' = 1/f ([OpenStax, Spherical mirrors](https://openstax.org/books/university-physics-volume-3/pages/2-2-spherical-mirrors)). Med f = 187,1 mm blir ei kjelde 374 mm frå plata avbilda 374 mm frå plata (s = s' = 2f). Det stemmer med at lampe og linse sit side om side i hovudet, 33 til 40 cm over plata.

### 1.3 Det som er usikkert, og korleis du les det av sjølv

| Spørsmål | Status | Slik finn du det ut |
|---|---|---|
| Kva variant er det? | UKJENT. ANTAKING: AHSV eller AHST dersom projektoren er seld i Noreg. | Typeskiltet sit inne i projektoren og viser modell med bokstavkode, produksjonskode, lampedata og serienummer (DL s. iii). |
| Kva pære? | FSX, 230 V og 400 W dersom varianten er europeisk. | Les stemplinga på pæra og merkelappen ved lampeluka. Delelista har eigne merkelappar for EVW og for FSX/FSY (DL seksjon 6 og 7). Sokkelen GY9.5 har to pinnar. Talet i nemninga er pinneavstanden i millimeter (allmenn sokkelnemning, ikkje kontrollert mot kjelde her). |
| Vifte | Ikkje i dokumenta. Du har sett ei vifte i hovudet. | Les skiltet på vifta: spenning, AC eller DC, straum eller effekt. Sjekk òg at det står 2000 og ikkje 2100 på projektoren. 3M 2100 har motordriven vifte ved lampehuset, pære på 24 V og 275 W (FNT) og fresnellinse over lampa i sokkelen ([servicehefte 2100](https://auto.manualsonline.com/manuals/mfg/3m/2100.html?p=6)). Sit lampa di i sokkelen, er det ein annan modell enn denne rapporten skildrar. |
| Termosikring | Ikkje i dokumenta. | Sjå etter ein liten komponent med to leidningar, klemd mot lampehuset eller kopla i serie med pæra, merkt med ein temperatur i °C (TOLKING: slik ser termobrytarar vanlegvis ut). |
| Sikring | 2,5 A eller 5 A. Dokumenta er usamde. | Les på metallhetta på glasrøyrsikringa. |
| Brennvidd, linse | 27 til 29 cm (eiga utrekning), 292 mm (forhandlar, søkjetreff). | Mål sjølv, sjå 3.3. |
| Brennvidd, fresnelplate | 187,1 mm (deleliste). | Kontroller med måling, sjå 3.3. |
| Materialet i fresnelplata | UKJENT. ANTAKING: akryl med speglande belegg. | Ikkje test med løysemiddel. |
| Lysfluksen frå pæra | UKJENT. Ikkje funne i kjeldene. | Ikkje naudsynt. Pæra bør ikkje brukast. |

---

## 2. Trygg gjenbruk

### 2.1 Delar som er verde å ta vare på (TOLKING, bygd på kap. 1)

| Del | Kva han kan brukast til | Handsaming |
|---|---|---|
| Fresnelplata, 285 × 285 mm, f = 187 mm, reflekterande | Stor og lett samlespegel: kollimering, projisert felt, lysflate som berre lyser inne i strålen. | Lagre ho flatt, tildekt, med rillesida verna. Aldri i sollys (sjå 2.2). Rettleiinga seier mjuk, lofri bomullsklut og linsereinsemiddel, og den japanske teksten rår frå alkoholbaserte middel, slik eg les han (BR s. 10). |
| Projeksjonslinsa, singlet eller triplet | Avbildar ei maske eller ei lyskjelde på vegg og bord frå 1 til 2 m. For lang brennvidd til ei kompakt lampe (sjå 3.2). | Lat ho sitje i fatninga, så har du eit feste og ein fokusmekanisme. Støv av med mjuk pensel, deretter klut og linsereinsemiddel (BR s. 10). |
| Frontflatespegelen | Faldar strålegangen utan dobbeltbilete, fordi det speglande laget ligg på framsida. | Skal ikkje tørkast av. Støv blir fjerna med mjuk pensel (BR s. 9 og 10). Ta aldri på flata. |
| Stolpe, ledd og hovudlås | Ferdig, stiv arm med lås: rigg for lyskjelde, telefon eller prøveplater 30 til 40 cm over bordet. | Fjern nettleidningane som går gjennom stolpen (DL seksjon 15) før du brukar han til lågspenning. |
| Koffertsokkel, lok, platedelar og skruar | Stabil fot og mørk boks for lysforsøk. Platedelar og brakettar kan bli feste og skjermar i riggen. | Tøm sokkelen for nettdelar. Materialet i platedelane er UKJENT. |
| Vippebrytar, sikringshaldar og forriglingsbrytar | Av og på i ein 5 V-prototyp. Forriglingsbrytaren kan vise at ein del er flytta, slik 05 punkt 9 føreslår for mekanisk modusskifte. | Klipp bort alle nettleidningar og merk delane «berre lågspenning». |
| Vifta, om ho finst | Berre aktuell om ho er merkt for låg likespenning. | Les skiltet. Ei vifte for 230 V skal ikkje inn i ein prototyp. |
| Pære, lampehaldar, motstand og nettleidning | Ikkje gjenbruk. | Legg dei til side. Rettleiinga åtvarar mot støyt når pæra lyser (BR s. 12). |

### 2.2 Det som er farleg

**Varme**

- FAKTA: Ei halogenpære skal ha kolbetemperatur over 250 °C og under 800 °C, og innsmeltinga skal haldast under 350 °C. Produsenten åtvarar mot papir, tekstil og anna brennbart nær pæra, og mot å ta på ho medan ho er varm. ([Ushio](https://www.ushio.com/?p=1811))
- FAKTA: 3M åtvarar om brannskadar frå rista på hovudet og lampeluka, og krev at apparatet er heilt avkjølt før pærebyte. (BR s. 2 og 11)
- FAKTA: PETG har formstabilitetstemperatur (HDT) 68 °C ved 0,45 MPa ([Prusament PETG, datablad](https://cdn.shopify.com/s/files/1/1745/6181/files/PETG_TechSheet_ENG.pdf)). PLA har 55 °C ([Prusament PLA, datablad](https://cdn.shopify.com/s/files/1/1745/6181/files/PRUSA_PLA_TechSheet_ENG.pdf), søkjetreff). Glasovergangen er 55 til 60 °C for PLA og 80 til 85 °C for PETG ([All3DP](https://all3dp.com/2/pla-petg-glass-transition-temperature-3d-printing/), søkjetreff).
- FAKTA: Papir sjølvtenner ved 218 til 246 °C. Tala varierer mykje i litteraturen. ([Wikipedia, Autoignition temperature](https://en.wikipedia.org/wiki/Autoignition_temperature))
- EIGA UTREKNING: 400 W ved 230 V er 400 / 230 = 1,74 A.
- TOLKING: Kolben er minst 180 °C varmare enn det PETG toler, og kan vere varmare enn sjølvtenningstemperaturen til papir. Ingen prenta delar, papp eller ark frå LCD-skjermar skal nær pæra. Pensjoner henne. LED-kjeldene i kap. 4 gjev same optiske lærdom med 1 til 5 W.

**Open nettspenning**

- FAKTA: I dei europeiske variantane går nettspenninga rett til pæra, utan transformator (DL Appendix A). Rettleiinga krev at støpselet er ute før pærebyte og reingjering, og seier at apparatet ikkje skal demonterast av brukaren, på grunn av fare for støyt (BR s. 2 og 11).
- TOLKING: I den demonterte projektoren ligg brytar, sikringshaldar, forrigling, motstand og lampehaldar opne med 230 V dersom støpselet blir sett i. Forriglinga er truleg sett ut av spel. Set ikkje straum på han. Klipp av støpselet eller teip og merk det, så ingen andre gjer det.

**Fresnelplata i sol**

- FAKTA: Innstrålinga på ei flate vend mot sola er om lag 1000 W/m² ved havnivå på ein klar dag ([Wikipedia, Solar irradiance](https://en.wikipedia.org/wiki/Solar_irradiance)). Sola dekkjer om lag 0,53° på himmelen ([Wikipedia, Angular diameter](https://en.wikipedia.org/wiki/Angular_diameter), omrekna frå bogeminutt).
- FAKTA: Ein seljar av store fresnellinser åtvarar om svært høg temperatur i brennpunktet og om brannskadar, blending og brann ([Solar Brother](https://www.solarbrother.com/en/buy/xl-fresnel-lens/), søkjetreff). Eit patent på ein leselupe seier at ei linse i den storleiken raskt kan tenne brennbart materiale ([US 4,457,585](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4457585), søkjetreff).
- EIGA UTREKNING: Plata er 0,285 × 0,285 = 0,081 m² og fangar opptil 81 W sollys. Ideelt blir sola avbilda som ein flekk på 187 mm × 0,0092 rad = 1,7 mm, 187 mm framfor plata. Ei verkeleg fresnelplate gjev ein større flekk, men framleis titals watt på nokre få kvadratcentimeter.
- TOLKING: Plata er ein holspegel og samlar lyset *framfor* seg, òg når ho ligg i ein vindaugskarm eller blir boren ute. Lagre ho tildekt og aldri ved vindauge. Bruk aldri sola til å måle brennvidda.

---

## 3. Lysforsøk som kostar om lag null

**Slik gjer du kvart forsøk**

1. Skriv føreseiinga med tal og grunngjeving før du slår på lyset.
2. Mørkt rom, same stad, same telefon i same haldar.
3. Mål tre gonger og noter snittet. Ta eit bilete med låst eksponering (kap. 6).
4. Skriv avviket og kva som forklarer det.

Loggline: forsøk, føreseiing, målt, avvik, kva eg lærte, kva det tyder for konsepta.

### 3.1 Projisert lysfelt på vegg: ansiktslys og stemning

**Grunnlag**

- FAKTA: Luminansen til ei diffus flate er L = E · ρ / π. Belysningsstyrke er E = Φ / A. (03 kap. 1 og 9, etter Zumtobel)
- FAKTA: Kvit måling reflekterer 75 til 85 %, kvitt papir 70 til 80 % ([Engineering ToolBox](https://www.engineeringtoolbox.com/light-material-reflecting-factor-d_1842.html)).
- Frå 03 kap. 1 og 6: Ein skjerm har typisk 50 til 300 cd/m², og forsking tyder på at folk føretrekk omgjevnader som er like lyse som eller litt mørkare enn skjermen (fakta der). 03 vurderer 100 til 300 lx samla på ansiktet som realistisk heime, og reknar med at skjermen sjølv gjev om lag 60 lx ved 150 cd/m² (tolking og reknestykke der).

**EIGA UTREKNING**

Føresetnader: Veggfeltet er jamt opplyst og diffust. Reflektansen er ρ = 0,7 (ANTAKING, lys måla vegg). Ansiktet vender rett mot veggen, og feltet ligg midt framfor ansiktet. d er avstanden frå ansikt til vegg. Skjermen skuggar ikkje.

- Eit lite flateelement dA med luminans L gjev dE = L · cos θ₁ · cos θ₂ · dA / r². Når flatene er parallelle, er begge cosinusane d/r, så dE = L · d² · dA / r⁴.
- For eit felt som er lite i høve til avstanden: E_ansikt = L · A / d². Med L = ρ · E_vegg / π og Φ = E_vegg · A blir **Φ = π · E_ansikt · d² / ρ**. Feltstorleiken fell ut.
- Metode 1, punktformelen. 100 lx på 0,7 m: π × 100 × 0,49 / 0,7 = **220 lm**. På 1,0 m: π × 100 × 1,0 / 0,7 = **449 lm**.
- Metode 2, numerisk integrasjon over rektangelet (400 × 400 ruter). Tabellen viser lysfluks på veggen, belysningsstyrke på veggen og luminans, for 100 lx på ansiktet:

| Veggfelt | d = 0,7 m | d = 1,0 m |
|---|---|---|
| 0,6 × 0,4 m | 258 lm, 1076 lx, 240 cd/m² | 487 lm, 2031 lx, 453 cd/m² |
| 1,0 × 0,6 m | 318 lm, 529 lx, 118 cd/m² | 548 lm, 914 lx, 204 cd/m² |
| 1,2 × 0,8 m | 369 lm, 384 lx, 86 cd/m² | 600 lm, 625 lx, 139 cd/m² |

- Alt skalerer lineært. 50 lx krev halvparten, 200 lx det doble.
- Kontroll mot 03: Same metode gjev 258 cd/m², 1158 lx og 596 lm frå lampa for dømet i 03 kap. 9 (0,6 × 0,6 m, 0,9 m, 70 % treff). 03 oppgjev om lag 260 cd/m², 1150 lx og 600 lm.
- Felt utanfor aksen: Ligg midten av feltet 0,3 til 0,5 m over eller til sida for ansiktet, trengst 1,2 til 2,0 gonger så mykje lys på 0,7 m og 1,1 til 1,5 gonger på 1,0 m (same integrasjon).
- Annan vegg: ρ = 0,8 gjev 192 og 393 lm i punktformelen. ρ = 0,5 gjev 308 og 628 lm.
- Lampa må gje meir enn dette, fordi ikkje alt lyset treffer feltet (ANTAKING: 50 til 70 % treff).
- Luminans mot skjerm: Ved 100 lx på ansiktet er veggfeltet 0,9 til 4,5 gonger så lyst som ein skjerm på 100 cd/m², og 0,3 til 1,8 gonger så lyst som ein skjerm på 250 cd/m². Lite felt og lang avstand gjev høgast luminans.

**TOLKING**

- Indirekte ansiktslys kostar 220 til 600 lm på veggen for 100 lx, før tap i lampa. 03 kap. 9 kom til om lag 600 lm frå lampa for 100 lx i eitt døme, og om lag fem gonger så mykje lysfluks som direkte lys. Tabellen her viser spennet rundt det dømet.
- Eit lite, sterkt felt blir lysare enn skjermen. Eit felt på om lag 1 m breidd hamnar på skjermnivå.
- Eit realistisk mål er 50 lx frå veggen og resten frå skjerm og rom. Det krev 110 til 300 lm på veggen og gjev 45 til 225 cd/m².
- 03 minner om at veggen rett bak skjermen er skjult for ansiktet. Feltet må liggje over eller ved sida av skjermen, og då gjeld korreksjonen for felt utanfor aksen.

**Forsøk 1: veggfelt**

- **Oppsett:** Set deg som ved skjermen, 0,7 m og 1,0 m frå ein lys vegg. Lys på veggen med ei lampe med kjend pære (til dømes 806 lm) bak ein pappskjerm med rektangulært hol, eller med lommelykt. Teip opp felta 0,6 × 0,4 m og 1,0 × 0,6 m. Køyr med skjermen av, så på.
- **Måling:** Lux på veggen i fem punkt (telefonen flatt mot veggen). Lux ved ansiktet (telefonen loddrett, vend mot veggen). Webkamerabilete med låst eksponering og skjermbilete av sjølvvisinga.
- **Føreseiing:** E_ansikt ≈ 0,22 × Φ_vegg / d² for ρ = 0,7 og lite felt midt framfor ansiktet. Døme: 300 lm på veggen gjev 136 lx på 0,7 m og 67 lx på 1,0 m, og om lag 10 til 40 % mindre for felta i tabellen. Rekn sjølv ut Φ_vegg frå luxmålingane på veggen (snitt × areal) og skriv ned talet for ansiktet før du måler det.
- **Avgjer:** Kan eit konsept byggje på veggen som ansiktslys, eller berre som stemning og luminansbalanse? Kor stort må feltet vere? Må lampa ha kabel i denne modusen (sjå batteritabellen i 05 punkt 4)?

### 3.2 Skarpt avgrensa lysfelt på bordet: profilprinsippet

**Grunnlag**

- FAKTA: I ein profilkastar står glødetråden i det eine brennpunktet til ein ellipsoidereflektor, og porten med blendarblad står i det andre. Å skyve linserøyret inn eller ut gjer kanten hardare eller mjukare. Namnet kjem av at strålen kan formast etter profilen til eit objekt. ([Wikipedia, Ellipsoidal reflector spotlight](https://en.wikipedia.org/wiki/Ellipsoidal_reflector_spotlight))
- FAKTA: Referansen for arbeidsfeltet er 500 lx med jamnheit minst 0,6, og 300 lx i dei nære omgjevnadene. (03 kap. 1)

**EIGA UTREKNING**

- Lys på feltet: 500 lx × (0,6 × 0,4 m) = 500 × 0,24 = **120 lm**. Same tal som 03 kap. 9 og 05 punkt 8.
- Lys frå kjelda: 120 / η. Med η = 0,3 til 0,6 (ANTAKING for enkel optikk) blir det 200 til 400 lm.
- Optikk, tynn linse: u = f(1 + 1/m) og v = f(1 + m), der m = feltbreidd / portbreidd.
  - Projeksjonslinsa, f ≈ 285 mm: Port 100 mm gjev m = 6, u = 332 mm og v = 2,0 m. Port 170 mm gjev m = 3,5 og v = 1,3 m. Linsa høver for kast på 1 til 2 m, ikkje for ei bordlampe.
  - Kompakt lampe med 45 cm kast: m = 10 (port 60 × 40 mm) krev f = 41 mm. m = 6 (port 100 × 67 mm) krev f = 64 mm.
- Utan linse: Halvskuggen frå ein kant er w = s · b / a, der s er storleiken på lyskjelda, a avstanden frå kjelde til maske og b avstanden frå maske til flate. Kjelde 3 mm, a = 100 mm, b = 400 mm: 12 mm. Kjelde 10 mm: 40 mm.

**TOLKING**

- Eit skarpt felt krev anten ei lita lyskjelde (høg luminans, må skjermast heilt) eller avbildande optikk med kort brennvidd og stor opning.
- Ein skarp kant gjev brå overgang til mørk bordflate og bryt med 300 lx i dei nære omgjevnadene. Ein litt uskarp kant kan vere betre enn ein skarp.

**Forsøk 2: profil i tre trinn**

- **Oppsett a, skuggemaske:** Telefonlykta 40 cm over bordet, pappmaske med rektangulært hol 10 cm under lykta.
- **Oppsett b, projektoroptikken:** Fresnelplata med pappmaske (opning 170 × 115 mm), ei lommelykt der lampa sat, linsa og spegelen i hovudet. Felt 0,6 × 0,4 m på vegg eller bord 1,3 m unna. Juster skarpleiken med fokusrattet. Merk at plata berre fangar om lag 16 % av lyset frå ei naken LED i lampeposisjonen (eiga utrekning, flat LED 370 mm over plata), så bruk ei lykt som alt samlar lyset.
- **Oppsett c:** Ei lommelykt med fokus i smal stilling, om du har ei. TOLKING: ho avbildar då lysdioden og er ein profilkastar i miniatyr.
- **Måling:** Lux i rutenett på 10 cm (snitt og minste verdi delt på snitt). Breidda på overgangen frå lyst til mørkt. Lux på skjermflata og ved auget. Bilete frå sitjestilling av det som lyser.
- **Føreseiing:** E_snitt = Φ · η / A. Ei lykt på 200 lm gjev 250 til 500 lx dersom 30 til 60 % hamnar i feltet. Kantbreidda følgjer halvskuggeformelen.
- **Avgjer:** Er eit skarpt avgrensa arbeidsfelt verdt optikken? Kor høg og kor djup må lampa då vere? Kor mykje ser ein av lyskjelda frå stolen?

### 3.3 Kollimering med fresnelplata og projeksjonslinsa

**Grunnlag**

- FAKTA: Divergensen til ein kollimert stråle er om lag kjeldestorleiken delt på brennvidda. Lengre brennvidd gjev smalare stråle, men fangar mindre av lyset. ([Edmund Optics](https://www.edmundoptics.com/knowledge-center/application-notes/optics/considerations-in-collimation/), søkjetreff)
- FAKTA: Ein gjenstand som er mykje lenger unna enn brennvidda, blir avbilda nær brennplanet. ([OpenStax](https://openstax.org/books/university-physics-volume-3/pages/2-4-thin-lenses))
- FAKTA: Ingen lineær optikk kan gje høgare lysstyrke per flate og vinkel enn kjelda sjølv har. ([Wikipedia, Etendue](https://en.wikipedia.org/wiki/Etendue))
- FAKTA: Utanfor tilrådd avstand kan ein overheadprojektor gje blå eller brune kantar, fordi fresnelen er laga for éi linsestilling. ([Wikipedia, Overhead projector](https://en.wikipedia.org/wiki/Overhead_projector))

**Slik måler du brennvidda trygt**

- Projeksjonslinsa: Stå inst i rommet om dagen og avbild vindauget på eit kvitt ark, eller bruk ei lampe i andre enden av rommet. Mål avstanden frå linse til ark når biletet er skarpt, og rekn ut f frå 1/f = 1/u + 1/v. EIGA UTREKNING: For ein gjenstand 5 m unna og f = 285 mm blir avstanden 302 mm, altså 6 % meir enn f. Føreseiing: 27 til 29 cm.
- Fresnelplata: Mørkt rom, telefonlykta som kjelde. Hald lykta over midten av plata og flytt ho opp og ned til det skarpe biletet av lysdioden fell på eit kort du held rett attmed lykta. Då er avstanden 2f. Føreseiing: 374 mm. Kontroll: Med lykta 250 mm frå plata skal biletet liggje 744 mm frå plata.
- Aldri sola.

**EIGA UTREKNING: kva du kan vente**

| Kjelde, diameter | Divergens med fresnelplata (f = 187 mm) | Halvskugge 0,5 m bak ein kant |
|---|---|---|
| 1 mm | 0,3° | 3 mm |
| 3 mm | 0,9° | 8 mm |
| 10 mm | 3,1° | 27 mm |
| 60 mm (matt pære) | 18° | 160 mm |

- Fanga lys: Plata fangar om lag 42 % av lyset frå ei flat LED i brennpunktet. Ei linse på 70 mm diameter (ANTAKING) med 285 mm brennvidd fangar 1,5 %. Formel for sirkelopning: sin² av halvvinkelen.
- Kjeldeposisjonen styrer feltet (spegellikninga, plata er 285 mm brei):

| Kjelde framfor plata | Strålen | Feltbreidd 40 cm frå plata |
|---|---|---|
| 100 mm | spreier seg | 82 cm |
| 120 mm | spreier seg | 63 cm |
| 150 mm | spreier seg | 44 cm |
| 187 mm | parallell | 28,5 cm |
| 250 mm | samlar seg i eit punkt 74 cm framfor plata | 13 cm |

**Kva lyskvalitet parallelt lys gjev (TOLKING, bygd på formlane over)**

- Skuggane blir skarpe, som i sollys. Halvskuggen veks med kjeldestorleiken.
- Strålen er like brei som opninga. For å lyse opp 60 cm trengst ei opning på 60 cm eller ein stråle som spreier seg. Rein kollimering høver difor dårleg til ei kompakt bordlampe.
- Utanfor strålen ser plata mørk ut. Inne i strålen lyser heile plata med luminansen til lysdioden. Det er blendkontroll med geometri: ingen ser kjelda frå stolen, men ei blank bordflate kan spegle strålen rett i auga.
- Belysningsstyrken fell lite med avstanden så lenge strålen held seg samla.

**Forsøk 3: kollimering og kjeldeposisjon**

- **Oppsett:** Plata på høgkant, vippa 10 til 15° så strålen går forbi telefonen. Telefonlykta 100, 150, 187 og 250 mm framfor midten. Kvit vegg eller papp 40 cm og 1 m unna. Ein blyant som skuggekastar.
- **Måling:** Feltbreidd, lux i midten og ved kanten, breidda på halvskuggen bak blyanten. Bilete av plata sett frå strålen og 30° utanfor (ikkje sjå rett inn i strålen på kort hald).
- **Føreseiing:** Tabellane over. Skriv i tillegg ned kor stor du trur lysdioden er, og rekn ut divergensen.
- **Avgjer:** Kan ein reflektor som formar strålen erstatte ein diffusor i arbeidsmodus? Er «kjelda flyttar seg, feltet endrar seg» ei brukande handling for modusskifte? Kor stor må opninga vere?

### 3.4 Retningsbestemt spreiing med prenta klare plater

**Kvifor lyset blir spreidd på tvers av linjene**

- FAKTA: Ei sylinderlinse samlar eller spreier lyset berre på tvers av sylinderaksen og lèt det vere urørt langs aksen. ([Wikipedia, Cylindrical lens](https://en.wikipedia.org/wiki/Cylindrical_lens))
- FAKTA: Den krumme utsida på printlinjene verkar som stabla, klare røyr som bryt og spreier lyset ([Snapmaker](https://www.snapmaker.com/blog/how-to-3d-print-clear-filament/)). Lys blir brote i kvar overgang mellom luft og plast, og luftlommer og dårleg samansmelta grenseflater mellom linjene gjer printen mjølkete ([CNC Kitchen](https://www.cnckitchen.com/blog/transparent-fdm-3d-prints-are-clearly-stronger)).
- TOLKING: Kvar printlinje er ei lita sylinderlinse med aksen langs linja. Mange linjer side om side blir ei lentikulær plate. Lyset blir bøygd i planet på tvers av linjene og går rett fram langs dei. Ei punktkjelde sett gjennom plata blir difor ei stripe på tvers av linjene. Glansstripa du ser, er same sak i refleksjon.

**Printinnstillingar som gjev klarast resultat**

- FAKTA, PETG ([CNC Kitchen](https://www.cnckitchen.com/blog/transparent-fdm-3d-prints-are-clearly-stronger)): laghøgd 0,12 mm, ekstruderingsbreidd 0,5 mm, éin perimeter, flyt litt over 100 % (102 % i styrkeprøvene), dyse 220 til 230 °C for filamentet som vart brukt, fart 15 mm/s (5 og 10 mm/s gav mikrobobler), vifta av (30 % vifte heldt klarleiken og gav betre overheng), fyll «Aligned Rectilinear» i 0° og 100 %, ingen topp- og botnlag, nytørka filament. Metoden er treg og høver for enkle former.
- FAKTA, generelt ([MatterHackers](https://www.matterhackers.com/about/how-to-3d-print-clear-filament-for-better-transparency)): Klar PETG er det beste utgangspunktet. Klar PLA fungerer når delen berre skal sleppe lys gjennom. 0,1 mm lag og om lag 5 mm/s er klarast, 0,2 mm og om lag 50 mm/s er eit godt kompromiss. Juster temperaturen i steg på 5 °C og flyten i steg på om lag eitt prosentpoeng. Slå av «Detect narrow internal solid infill». I Bambu Studio ligg vifta under filamentinnstillingane.
- FAKTA, generelt ([Snapmaker](https://www.snapmaker.com/blog/how-to-3d-print-clear-filament/)): Prent øvst i temperaturområdet til filamentet, sakte (15 til 20 mm/s), med 100 % fyll i «Aligned Rectilinear», og auk flyten 1 til 5 % om det står att gliper. PETG gjev klarast resultat, PLA er lettare å prente og høver for gjennomskinlege delar.
- FAKTA: Prusament PETG har tilrådd dyse 250 ± 10 °C og plate 80 ± 10 °C som generelle verdiar ([datablad](https://cdn.shopify.com/s/files/1/1745/6181/files/PETG_TechSheet_ENG.pdf)).
- Kjeldene er usamde om laghøgda. CNC Kitchen brukar 0,12 mm og MatterHackers 0,1 mm for klarast resultat. Snapmaker tilrår tjukkare lag, 0,24 eller 0,28 mm, fordi færre lag gjev færre krumme flater. TOLKING: For forsøket ditt er laghøgda sjølve variabelen. Prent begge.
- UKJENT: Eigne tal for klar PLA er ikkje funne. CNC Kitchen skriv at overføring til andre materiale treng meir utprøving.

**Grenser (TOLKING, bygd på kjeldene over)**

- Du styrer ikkje linseprofilen, berre linjebreidd og laghøgd. Spreiingsvinkelen må målast, han kan ikkje bestillast.
- Luftlommer gjev dis som spreier lys i alle retningar og senkar verknadsgraden.
- Overflata mot byggjeplata blir flat eller matt, oversida får riller.
- Største plate er 256 mm. PLA mjuknar ved om lag 55 °C.

**Forsøk 4: tre plater**

- **Oppsett:** (A) flat plate, 1 mm, etter oppskrifta over, linjer i éi retning. (B) éin vegg i vasemodus, 0,2 mm lag, ståande, der laga er rillene. (C) to A-plater lagde i kryss. Telefonlykta 1 m bak plata, kvit vegg 0,5 m framfor.
- **Måling:** Retning og lengd på stripa på veggen, omrekna til vinkel: 2 × arctan(halv lengd / avstand). Lux rett bak plata med og utan plate. Bilete av lykta sett gjennom plata.
- **Føreseiing:** Stripa står på tvers av linjene. B spreier meir enn A (ANTAKING: djupare riller). C gjev ein firkanta eller rund flekk. Skriv ned vinkelen du trur du får.
- **Avgjer:** Kan lampa spreie lyset breitt langs bordet og smalt i høgda, slik at det ikkje treffer auga? Trengst det ein kjøpt optikk, eller held ein struktur som er ein del av forma?

**Produksjonsmateriale med same verknad**

- FAKTA: Lentikulære plater er lineære rekkjer av sylinderlinser, vanlegvis i PMMA eller polykarbonat ([Orafol LN 669 hos FindLight](https://www.findlight.net/optics/lenses/lenticulars/orafol-lenticular-ln-669), søkjetreff).
- FAKTA: Ekstruderte lineære linser for LED blir laga i diffus PMMA ([LEDiL LINDA](https://ledil.com/?p=12939), søkjetreff). Eitt datablad oppgjev oval fordeling på om lag 40° × 100° og verknadsgrad 80 til 88 %, alt etter lysdiode ([datablad hos Comet](https://store.comet.bg/download-file.php?id=24937), søkjetreff).
- FAKTA: Det finst diffusorfilm med elliptisk spreiing på den eine sida og prismestruktur på den andre, laga for lineære armatur ([LEDs Magazine om Luminit](https://www.ledsmagazine.com/leds-ssl-design/article/16679024/luminit-adds-lenticular-batwing-format-to-its-line-of-light-shaping-diffusers-for-ssl-design), søkjetreff).
- FAKTA: Rifla glas har parallelle riller som forvrengjer innsynet og slepper lyset gjennom ([Stake Glass](https://www.stakeglass.co.nz/products/reeded-glass), søkjetreff). At spreiinga går på tvers av rillene, er ikkje stadfesta i kjeldene, men følgjer av sylinderlinseprinsippet (TOLKING).
- FAKTA: Prismefilm (3M BEF) har parallelle 90°-prisme med 50 µm deling og samlar lyset i eitt plan per ark (patenttekstane [US 8,740,442](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8740442) og [US 7,898,520](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7898520), og [3M, bruksrettleiing for lysstyrkefilm](https://multimedia.3m.com/mws/media/1839627O/3m-brightness-film-app-guide-75050141318-pdf.pdf), alle søkjetreff). Sjå 3.5.

### 3.5 Optiske ark frå LCD-bakbelysning

**Kva arka er, bakfrå og fram**

| Ark | Kva det gjer | Tal | Kjelde |
|---|---|---|---|
| Reflektorark | Sender lys som lek ut på baksida av lysleiaren tilbake. Kvitt pigmentert eller metallisk. | 3M sin speglande film (ESR) reflekterer over 98 % og inneheld ikkje metall. | [LG, manual s. 11](https://www.manualslib.com/manual/559239/Lg-Le-15a10.html?page=11), [Wikipedia, Backlight](https://en.wikipedia.org/wiki/Backlight), [3M ESR](https://www.3m.co.uk/3M/en_GB/p/d/b5005047091/) (søkjetreff) |
| Lysleiarplate (LGP) | Leier lyset frå lysdiodar langs kanten og slepper det ut gjennom eit mønster av punkt. Punkta står tettare lenger frå lyskjelda. Akryl eller polykarbonat. | Kritisk vinkel om lag 42° for akryl. | [Wikipedia, Backlight](https://en.wikipedia.org/wiki/Backlight), [Hackaday](https://hackaday.com/2023/03/13/a-hackers-introduction-to-diy-light-guide-plates) |
| Nedre diffusor | Jamnar ut og samlar lyset frå lysleiaren. Aukar ikkje lysstyrken. | Ein leverandør oppgjev om lag 86 % transmisjon og 93 % dis for ein PET-diffusor (leverandørtal, søkjetreff, ikkje kontrollert). | [LG](https://www.manualslib.com/manual/559239/Lg-Le-15a10.html?page=11), [Riverdi](https://riverdi.com/blog/what-is-bef-and-how-does-it-work), [leverandør](https://china.org.ru/product/1600727505488) |
| Nedre prismeark | Samlar lyset mot synsaksen i eitt plan. Lys som kjem på skrå, blir brote framover. Lys rett på blir sendt tilbake og resirkulert. | Opptil 1,55 gonger luminansen frå lysleiaren (LG). 40 til 60 % auke (Riverdi). 1,6 gonger for eitt ark i ein patenttekst. Tjukkleik 60 til 120 µm (Riverdi). | [LG](https://www.manualslib.com/manual/559239/Lg-Le-15a10.html?page=11), [Riverdi](https://riverdi.com/blog/what-is-bef-and-how-does-it-work), patenttekstane [US 8,740,442](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8740442) og [US 7,898,520](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7898520) (søkjetreff) |
| Øvre prismeark, kryssa 90° | Same verknad i det andre planet. | Opptil 1,33 gonger det nedre prismearket (LG). 2,6 gonger for to kryssa ark i patentteksten. 108 til 111 % auke for to kryssa ark i databladet for 3M BEF III. | Same kjelder, og [3M BEF III hos Elcodis](https://elcodis.com/parts/151183/98044003659_dt658331_p3.html) (søkjetreff) |
| Øvre diffusor (vernefilm) | Same oppbygging som nedre diffusor. Vernar prismearket. | Ikkje oppgjeve. | [LG](https://www.manualslib.com/manual/559239/Lg-Le-15a10.html?page=11) |
| Reflekterande polarisator (DBEF), ikkje alltid med | Slepper gjennom éi polarisasjonsretning og sender den andre tilbake til resirkulering. Stabel av mange tynne polymerlag. | 3M oppgjev opptil 30 % betre utnytting (søkjetreff). | [Wikipedia, Backlight](https://en.wikipedia.org/wiki/Backlight), [3M DBEF](https://www.3m.com/3M/en_US/p/d/b5005047085/) (søkjetreff) |

- EIGA UTREKNING: 1,55 × 1,33 = 2,06. To kryssa prismeark doblar altså luminansen rett fram i LG-stabelen. Det stemmer med 3M-databladet (om lag 2,1 gonger). Patentteksten oppgjev 2,6.
- FAKTA: Prismearka skal liggje med prisma vende mot LCD-panelet, bort frå lyskjelda. Eitt ark smalnar lyskjegla i eitt plan, to kryssa ark i begge. ([3M, bruksrettleiing for lysstyrkefilm](https://multimedia.3m.com/mws/media/1839627O/3m-brightness-film-app-guide-75050141318-pdf.pdf), søkjetreff)
- UKJENT: Kor mange gradar lyskjegla blir smalna, står ikkje i den delen av kjeldene eg fekk lese. Mål det i forsøk 6.
- TOLKING: I ei lampe utan LCD-panel gjer den reflekterande polarisatoren berre at halve lyset må ta ein ekstra runde. Legg han til side.

**Slik kjenner du dei att (TOLKING, utleidd frå verkemåten, prøv sjølv)**

- Reflektorarket er ugjennomsiktig, kvitt eller speglande. Telefonlykta går ikkje gjennom.
- Lysleiarplata er stiv og klar, med eit punktmønster på éi side. Lys inn i kanten, og punkta lyser opp.
- Diffusorarka er mjølkete. Ei punktkjelde sett gjennom dei blir ein rund, mjuk flekk, same korleis du dreier arket.
- Prismearka ser klare og litt sølvaktige ut. Ei punktkjelde sett gjennom dei blir delt eller dregen ut i éi retning, og mønsteret følgjer med når du dreier arket. EIGA UTREKNING: Eit 90°-prisme med brytingsindeks 1,59 (ANTAKING) sender lys som kjem rett inn på prismesida ut om lag 30° til kvar side. Ein bloggar som demonterte ein LG-skjerm, fann fire ark og skildra dei to midtarka som fresnel-liknande, men ikkje i ringar ([New Screwdriver](https://roger-random.github.io/newscrewdriver/2021/06/05/lg-lcd-panel-backlight)). I skjermen ligg dei to prismearka 90° på kvarandre.
- Den reflekterande polarisatoren liknar ein svak spegel. Hald arket framfor ein lysande LCD-skjerm og drei det: i éi stilling slepper det lyset gjennom, 90° vidare blir det mørkt og speglande.

**Forsøk 5: stor, jamn lysflate med låg luminans**

- **Oppsett utan lysleiarplate:** Ei pappeske fôra med kvitt papir, 20 til 30 cm opning. Lyskjelda (USB-list eller telefonlykt) peikar bakover eller til sida i eska, ikkje rett mot opninga. Legg arka over opninga i denne rekkjefølgja: diffusor nærast lyset, prismeark med prisma ut mot deg, eventuelt eitt til i kryss, diffusor ytst.
- **Oppsett med lysleiarplate:** Reflektorark bak, plata, så arka i same rekkjefølgje som over. Lys inn i kanten med USB-lista. Den originale LED-stripa i ein skjerm blir driven av ein eigen drivarkrets på kortet (bloggaren bak [New Screwdriver](https://roger-random.github.io/newscrewdriver/2021/06/05/lg-lcd-panel-backlight) nemner TI TPS61187 i ein LG-skjerm). TOLKING: Ho kan ikkje koplast rett på 5 V.
- **Variasjonar:** Null, eitt og to diffusorark. Prismeark rett veg og feil veg. Eitt prismeark i 0° og i 90°. Avstand frå lyskjelde til første ark.
- **Måling:** Bilete med låst eksponering rett forfrå (kor jamn er flata, kor synleg er kjelda). Lux 30 cm framfor midten.
- **Føreseiing:** EIGA UTREKNING: Ei jamn, diffus flate har L = Φ / (π · A). 100 lm gjennom 20 × 20 cm gjev om lag 800 cd/m². Gjennom 30 × 30 cm: om lag 350 cd/m². 50 lm gjennom 30 × 30 cm: om lag 180 cd/m², altså skjermnivå. Kvart prismeark aukar luminansen rett fram med 1,3 til 1,6 gonger, men berre når eska er kvit innvendig. Kvart diffusorark tek 10 til 15 % (ANTAKING frå leverandørtalet over).
- **Avgjer:** Kor tynn kan ei stor lysflate bli? Er rettesnora i 05 på minst 160 cm² lysande flate per 150 lm (05 punkt 8) til å leve med i forma? Er dette ansiktslyset?

**Forsøk 6: prismeark som blendkontroll**

- **Oppsett:** Lysboksen frå forsøk 5. Fotografer flata frå 0°, 30°, 45°, 60° og 75°, først vassrett og så loddrett, med låst eksponering og same avstand. Gjer det med null, eitt og to prismeark.
- **Måling:** Lysstyrken midt på flata i kvart bilete, relativt til 0°. Vinkelen der flata er halvparten så lys.
- **Føreseiing:** Med eitt ark blir flata mørkare på skrå i éi retning og uendra i den andre. Med to kryssa ark i begge. Skriv ned halvverdivinkelen du trur du får. ANTAKING: Ved svært skrå vinklar kan det kome eit lysare band att. Sjå etter det.
- **Avgjer:** Kan ei lysflate i augehøgd vere lys nok mot bordet og ansiktet, og samstundes mørk nok frå sofaen og i spegling i skjermen? 03 set grensa for flater som kan speglast i skjermen til 1000 til 1500 cd/m².

**Forsøk 7: kantbelyst flate, med og utan lysleiarplate**

- FAKTA: Ei klar akrylplate leier lys frå den eine kanten til den andre ved totalrefleksjon. Lyset kjem først ut der flata er rita eller har punkt. Jamt fordelte punkt gav ei plate som var mørkast lengst frå lyskjelda, så mønsteret må bli tettare med avstanden. Blanke kantar er avgjerande for å få lyset inn. Lim mellom plate og reflektor eller diffusor trekkjer lys ut der limet er. ([Hackaday](https://hackaday.com/2023/03/13/a-hackers-introduction-to-diy-light-guide-plates), det siste frå kommentarfeltet)
- TOLKING, det som manglar utan dei originale delane: ei plate med uttaksmønster, ei lyskjelde som er like lang og smal som kanten, og ein reflektor bak. Arka åleine lagar ikkje ei flat lysflate.
- **Oppsett:** Ei klar akrylplate på 3 mm frå restekassa på verkstaden. Puss den eine kanten blank. Lag uttak på baksida med sandpapir eller ripenål, tynt ved lyskjelda og tettare lenger unna. USB-lista langs kanten, kvitt papir eller reflektorarket bak, diffusor framfor. Prøv i tillegg ei prenta klar plate som lysleiar.
- **Måling:** Bilete med låst eksponering. Lysstyrken nær kjelda delt på lysstyrken lengst unna.
- **Føreseiing:** Den urita plata lyser nesten berre i kantane. Den prenta plata lyser sterkt dei første centimeterane og døyr raskt ut, fordi luftlommene mellom linjene spreier lyset ut med ein gong (TOLKING frå CNC Kitchen). Skriv ned kor mange centimeter du trur.
- **Avgjer:** Er ei flat, kantbelyst lysflate realistisk for konseptet, og kan uttaksmønsteret vere ein del av uttrykket?

**Kva arka svarar til i ei ferdig lampe, og materialseparasjon**

- FAKTA: Lysleiarplater er akryl eller polykarbonat med punktmønster laga med laser eller i sprøytestøypeforma ([Hackaday](https://hackaday.com/2023/03/13/a-hackers-introduction-to-diy-light-guide-plates)). Prismefilm er ein polyesterfilm med prisme i modifisert akryl ([3M BEF III, datablad hos Elcodis](https://elcodis.com/parts/151183/98044003659_dt658331_p3.html), søkjetreff). Diffusorfilm er ofte PET med eit belegg av små kuler ([Information Display](https://archive.informationdisplay.org/id-archive/2012/january/making-displays-work-for-you-diffuser-films-and-o), søkjetreff). Den speglande reflektorfilmen og den reflekterande polarisatoren er fleirlags polymerfilm (3M, søkjetreff).
- FAKTA: Opal PMMA for LED slepper gjennom 72 % ved 3 mm, og opale deksel generelt 30 til 90 % (05 punkt 8).
- FAKTA: Kurset krev tilrettelegging for materialseparasjon, og Flokk sitt materiale seier at to-komponent-plast ikkje kan resirkulerast (rapport 06, funn frå prosjektskildringa og frå Flokk).
- TOLKING: I ei lampe svarar stabelen til opal plate (diffusor), mikroprismatisk plate (prismeark), kvitlakkert eller speglande reflektor og ei akrylplate med mønster (lysleiar). Stabelen frå ein skjerm er fire til seks tynne ark av minst tre ulike plasttypar, og fleire av arka er sjølve to materiale som ikkje kan skiljast. Arka ligg laust og kan plukkast frå kvarandre for hand, men dei er umerkte og vanskelege å sortere. Eitt tjukt, einsarta og merkt optisk element (til dømes ei PMMA-plate med struktur) er lettare å forsvare enn ein filmstabel. Om du brukar film, hald talet lågt, klem han fast i staden for å lime, og merk materialet.

---

## 4. Lyskjelder utan budsjett

| Kjelde | Data | Pris | Duger til | Merknad |
|---|---|---|---|---|
| Telefonlykta | Lita, sterk kjelde. Lysfluks og fargetemperatur UKJENT. | 0 kr | Kollimering, skuggar, profil, retningsspreiing, kjenne att ark. | Mål lysfluksen sjølv: lys på ein vegg, mål lux i rutenett, summer lux × areal. |
| LED-pære i ein lampehaldar du har | IKEA SOLHETTA E27: 806 lm, 2700 K og 5,0 W (søkjetreff frå norsk produktside). Ra 90 står på den svenske sida (søkjetreff). | 89 kr for to ([IKEA](https://www.ikea.com/no/no/p/solhetta-led-paere-e27-806-lumen-dimbar-globeformet-opalhvit-60583924/)) | Veggfelt, lysboks, kalibrering av luxapp (kap. 6). | Bruk pæra heil. |
| LED-modul frå utrangert pære | Diodane står i serie. Éi demontert pære hadde tre parallelle rekkjer med tolv diodar og trong 67 V ([CandlePowerForums](https://www.candlepowerforums.com/threads/hyperikon-teardown.434087/), søkjetreff). | 0 kr | Lite, sjå merknad. | Åtvaring under tabellen. |
| USB-driven LED-list | IKEA KABBLEKA: 3 m, dimbar, treng USB-A-forsyning på 5 V som blir seld separat. Lysfluks og fargetemperatur fann eg ikkje på sida. | 159 kr ([IKEA](https://www.ikea.com/no/no/p/kabbleka-led-lyslenke-med-usb-dimbar-70594601/)) | Lysboks, kantlys, veggfelt, PWM-forsøk. | Test den innebygde dimmaren mot kamera før du stolar på han. |
| Batteridriven LED-list | Clas Ohlson, 1 m: 2 W, 130 lm, 3100 K, Ra 80, 30 diodar, kan klippast kvar 3,5 cm, 4 × AAA, rørslesensor, ikkje dimbar. | 119,90 kr ([Clas Ohlson](https://www.clasohlson.com/no/Fleksibel-LED-lyslist-1-m/p/36-6704)) | Godt dokumentert referanse: du veit lumen, kelvin og Ra. | Sensoren slår av etter 30 til 40 sekund. Lista må koplast forbi sensoren for forsøk. |
| RGB-list med USB | Kjell, 1 m, 30 RGB-diodar, knappar på kabelen. | 99,90 kr. Sida viser òg 129 kr, og det er uklart kva som gjeld. ([Kjell](https://www.kjell.com/no/produkter/belysning-lamper/led-lister/rgb-led-lister/ledsavers-tv-led-list-med-usb-1-m-p57819)) | Fargeeffektar. | TOLKING: Ikkje kjøp denne for kvitt lys og hudtonar. |
| COB-list | Samanhengande lysline utan synlege punkt. | UKJENT. Ingen norsk butikkpris funnen for varmkvit COB på 5 V. | Kantlys og lysliner. | |
| Lommelykt med fokus | Clas Ohlson Asaklitt: 200 lm, 6500 K, to nivå, justerbar frå smal til brei stråle, 3 × AAA. | 149,90 kr ([Clas Ohlson](https://www.clasohlson.com/no/Batteridrevet-lommelykt-LED,-200-lumen,-Asaklitt/p/31-7326-2)) | Profil, kollimering, lyskjelde i projektoroptikken. | Ra er ikkje oppgjeven. Ein lykteprodusent oppgjev om lag 75 som vanleg for kvite lyktediodar ([Acebeam](https://www.acebeam.com/led-beam-color), søkjetreff). |
| Sykkellykt | Clas Ohlson Asaklitt: 60 og 30 lm, USB-lading, om lag 2 timar ved 60 lm. | 149,90 kr ([Clas Ohlson](https://www.clasohlson.com/no/Asaklitt-LED-sykkellykt-60-lm/p/31-1879)) | Lita oppladbar kjelde inne i ein modell. | Fargetemperatur ikkje oppgjeven. |

**LED-modular frå lyspærer: åtvaring**

- FAKTA: Ein ikkje-isolert LED-drivar manglar transformatoren som skil utgangen frå nettet. Ein drivarprodusent skriv at ein slik drivar ikkje er trygg i seg sjølv, og at det er armaturprodusenten som må sørgje for isolasjonen. Slike drivarar er vanlege i billege produkt med låg effekt. ([MEAN WELL](https://www.meanwell.com/es/newsInfo.aspx?c=5&i=819))
- TOLKING: I ei opna LED-pære kan heile LED-kortet ha nettpotensial. Bruk aldri kortet med originaldrivaren i ein open modell. Utan drivaren treng kortet titals volt og straumregulering, og det har du ikkje gratis. Bruk heller heile pærer i ein godkjend lampehaldar.

**Lysfluks, farge og kjøling i grove trekk**

- EIGA UTREKNING: Clas Ohlson-lista gjev 130 / 2 = 65 lm/W. SOLHETTA gjev 806 / 5 = 161 lm/W. Ein USB 2.0-port (5 V, 0,5 A, 2,5 W) gjev då om lag 160 lm frå ei slik list. 5 V og 1,5 A (7,5 W) gjev om lag 490 lm, og 2 A (10 W) om lag 650 lm.
- Frå 05 punkt 7: Tommelfingerregelen er om lag 65 cm² kjøleflate per watt (fakta der). 05 vurderer at opp til 3 W klarer seg i nesten kva kropp som helst (tolking der). TOLKING: Ei list på 2 W per meter treng inga kjøling. Ei tett list bør limast på metall.
- 03 set Ra minst 90 og 2700 K eller varmare som mål for den ferdige lampa (03 kap. 3). TOLKING: Lykter på 6500 K duger til optikk og skuggar, ikkje til å vurdere hudtonar og stemning.

---

## 5. Styring med Arduino og micro:bit

### 5.1 Kopling

Ein N-kanal MOSFET per kanal, kopla som brytar på minussida:

- Pluss på LED-lista går rett til +5 V frå USB-kjelda.
- Minus på LED-lista går til drain.
- Source går til GND på USB-kjelda.
- GND på mikrokontrollaren går til same GND. Felles jord er eit krav. ([Adafruit](https://learn.adafruit.com/rgb-led-strips/usage))
- PWM-pinnen går til gate. På ein TO-220 er beina gate, drain og source i den rekkjefølgja ([Adafruit](https://learn.adafruit.com/rgb-led-strips/usage)).
- TOLKING: Legg 100 til 220 Ω i serie med gate og 10 kΩ frå gate til GND, så lista er mørk medan kortet startar. Adafruit oppgjev ingen gatemotstand for MOSFET-koplinga.

Val av transistor:

- FAKTA: IRLB8721 fungerer med 3,3 V og 5 V logikk og toler 16 A ([Adafruit](https://learn.adafruit.com/rgb-led-strips/usage)).
- FAKTA: IRLZ44N er ein logikknivåtype med høgst 0,022 Ω, spesifisert ved 5 V på gate ([Infineon, datablad](https://www.infineon.com/assets/row/public/documents/24/49/infineon-irlz44npbf-datasheet-en.pdf), søkjetreff). TOLKING: Han høver til Arduino på 5 V, men er usikker på 3,3 V frå micro:bit.
- FAKTA: Ein Arduino Uno toler 20 mA per pinne ([Wevolver](https://www.wevolver.com/specs/arduino-uno-rev3), søkjetreff). Pinnane på micro:bit leverer 5 mA (V1) eller 1 til 4 mA i standard drift (V2), og 3 V-utgangen 90 mA (V1) eller 190 til 270 mA (V2) ([micro:bit, edge connector](https://tech.microbit.org/hardware/edgeconnector/), [micro:bit, power supply](https://tech.microbit.org/hardware/powersupply/)). LED-straumen skal difor aldri gå gjennom kortet.

### 5.2 PWM-frekvens og kamera

- FAKTA: analogWrite på Uno, Nano og Mini gjev 490 Hz på pinne 3, 9, 10 og 11 og 980 Hz på pinne 5 og 6, med verdiar frå 0 til 255. Uno R4 gjev 490 Hz. ([Arduino, analogWrite](https://raw.githubusercontent.com/arduino/reference-en/master/Language/Functions/Analog%20IO/analogWrite.adoc))
- FAKTA: Timer1 styrer pinne 9 og 10. Timer0 styrer pinne 5 og 6 og dessutan millis() og delay(), så Timer0 skal du ikkje røre. Fasekorrekt PWM har frekvensen 16 MHz / delar / 510, og Arduino set delaren til 64. Timer1 er 16-bits og gjev finare styring. ([Shirriff, Secrets of Arduino PWM](http://www.righto.com/2009/07/secrets-of-arduino-pwm.html))
- FAKTA: På micro:bit går write_analog frå 0 til 1023. Perioden blir sett i mikrosekund, og minste gyldige verdi er 256 µs ([MicroPython, pins](https://microbit-micropython.readthedocs.io/en/v2-docs/pin.html)). I MakeCode heiter funksjonen pins.analogSetPeriod, pinnen må først vere sett som analog, og dømet i dokumentasjonen brukar 20 000 µs ([MakeCode](https://makecode.microbit.org/reference/pins/analog-set-period)). Høgst tre pinnar kan ha PWM samstundes ([micro:bit, edge connector](https://tech.microbit.org/hardware/edgeconnector/)).
- FAKTA: Opptak var uakseptable ved 900 til 1500 Hz og 50 % dimming eller lågare, og utan striper ved om lag 10 kHz og fullt lys. Låge dimmenivå og kort eksponering er verst. (03 kap. 4 og 05 punkt 6)
- EIGA UTREKNING: Delar 8 gjev 16 000 000 / 8 / 510 = 3,9 kHz. Delar 1 gjev 31,4 kHz. 256 µs gjev 3,9 kHz. 20 000 µs gjev 50 Hz.
- EIGA UTREKNING, tommelfingerregel: Skilnaden mellom biletlinjene er høgst om lag 1/N, der N er talet på PWM-periodar i éi eksponering.

| PWM-frekvens | Eksponering 1/60 s | Eksponering 1/500 s |
|---|---|---|
| 490 Hz | N = 8, opptil 12 % | N = 1, opptil 100 % |
| 3,9 kHz | N = 65, opptil 1,5 % | N = 8, opptil 13 % |
| 31,4 kHz | N = 523, 0,2 % | N = 63, 1,6 % |

- TOLKING: Standardfrekvensen på Arduino vil gje striper. 3,9 kHz ligg over minstemålet i 03 (3 kHz), men kan framleis gje striper i lyse rom, der kameraet eksponerer kort. 31 kHz er tryggast, og berre Arduinoen når dit. 05 har dette som ope spørsmål. No kan du teste det.
- UKJENT: Standardperioden på micro:bit står ikkje på sidene eg las. Set han alltid sjølv.

**Forsøk 8: striper i webkameraet**

- **Oppsett:** Éi LED-list, éin MOSFET. Køyr 490 Hz, 3,9 kHz og 31,4 kHz ved 5, 20 og 50 % lys. Lys på ansiktet og på ein kvit vegg, i mørkt og i lyst rom.
- **Måling:** Skjermbilete frå webkameraet og sakte film med telefonen. Tel stripene.
- **Føreseiing:** Tabellen over. Skriv ned kva frekvens du trur er nok.
- **Avgjer:** Kan lampa dimmast med PWM, eller må kravet vere straumregulert dimming (03 kap. 4)?

Kodeskisse for Arduino (ikkje testa, kontroller registera mot databladet til ATmega328P):

```cpp
// Uno/Nano. Varm kanal på pinne 9, kald på pinne 10, dreiehjul på A0.
void setup() {
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  // Timer1: byt delar frå 64 til 8 -> 3,9 kHz. Bruk 0x01 for 31,4 kHz.
  TCCR1B = (TCCR1B & 0b11111000) | 0x02;
}

void loop() {
  float x = analogRead(A0) / 1023.0;               // 0 til 1
  float lys = x * x;                                // kvadratisk kurve
  float kald = constrain((x - 0.3) / 0.7, 0.0, 1.0); // kald kanal kjem inn over 30 %
  analogWrite(9, (int)(lys * 255));                 // varm
  analogWrite(10, (int)(lys * kald * 255));         // kald
  delay(10);
}
```

Finare steg nedst (fasekorrekt PWM med ICR1 som topp, 4 kHz og 2000 steg):

```cpp
TCCR1A = _BV(COM1A1) | _BV(COM1B1) | _BV(WGM11);
TCCR1B = _BV(WGM13) | _BV(CS10);
ICR1 = 2000;   // 16 MHz / (2 * 2000) = 4 kHz
OCR1A = 40;    // varm, 0 til 2000
OCR1B = 0;     // kald, 0 til 2000
```

### 5.3 To kanalar som etterliknar dim-to-warm

- Frå 05 punkt 3 og 6: Digital to-kanal-styring let ein mikrokontrollar PWM-styre ein varm og ein kald streng etter ein oppslagstabell, og kvar streng kan gå frå 0 til 100 % (fakta der). Opplevd lysstyrke følgjer om lag kvadratrota av målt lysmengd (kjelda vart ikkje stadfesta i faktasjekken i 05).
- TOLKING: Skissa over gjer det enklast moglege: den varme kanalen følgjer nivået, den kalde kjem inn frå 30 % og oppover. Under 30 % er lyset reint varmt. Kvadratet på nivået gjev jamnare opplevd dimming.
- TOLKING: Har du berre éin lysfarge, kan du prøve logikken med to like lister og eit ravgult filter over den eine. Det viser handlinga, ikkje fargekvaliteten.

### 5.4 Modusskifte ved å vippe eller snu lampa

- FAKTA: Akselerometeret i micro:bit gjev verdiar i milli-g og kjenner att rørslene up, down, left, right, face up, face down, freefall, 3g, 6g, 8g og shake ([MicroPython, accelerometer](https://microbit-micropython.readthedocs.io/en/v2-docs/accelerometer.html)). MakeCode har input.onGesture med mellom anna shake, logo up, logo down, screen up, screen down, tilt left og tilt right ([MakeCode](https://makecode.microbit.org/reference/input/on-gesture)).
- Frå 05 punkt 9: Søket der fann ingen etablert designlampe som dimmar ved vipping (fakta der). 05 vurderer at brukaren ikkje får fysisk tilbakemelding frå ein orienteringssensor utan ei god form (tolking der).

Kodeskisse for micro:bit i MicroPython (ikkje testa):

```python
from microbit import *

VARM, KALD = pin1, pin2
for p in (VARM, KALD):
    p.write_analog(0)                      # set pinnen i PWM-modus først
    p.set_analog_period_microseconds(256)  # om lag 3,9 kHz, minste gyldige verdi

# stilling -> nivå: liggjande = stemning, ståande = arbeid, på sida = møte, snudd = av
MODUS = {"face up": 0.15, "up": 1.0, "left": 0.5, "face down": 0.0}
niva = 0.15

while True:
    g = accelerometer.current_gesture()
    if g in MODUS:
        niva = MODUS[g]
    lys = niva * niva
    kald = max(0.0, min(1.0, (niva - 0.3) / 0.7))
    VARM.write_analog(int(lys * 1023))
    KALD.write_analog(int(lys * kald * 1023))
    sleep(100)
```

- TOLKING: Pinnane på micro:bit leverer berre nokre få milliampere, så ein kraftig MOSFET slår tregt av og på. Ved 3,9 kHz kan dei lågaste nivåa bli ujamne. Prøv òg 500 og 1000 µs.

**Forsøk 9: vipp og snu i pappmodell**

- **Oppsett:** Teip micro:bit inn i ein pappmodell av kvart konsept. Lat ein annan person bruke modellen utan forklaring.
- **Måling:** Kor mange forsøk før personen finn kvar modus. Kor mange utilsikta skifte når modellen blir flytta.
- **Føreseiing:** Skriv ned kva stillingar du trur er sjølvforklarande.
- **Avgjer:** Kan modusen lesast av forma, eller trengst ein fysisk brytar?

### 5.5 Straum frå USB og powerbank

- FAKTA: Standard USB gjev 500 eller 900 mA. USB-C utan Power Delivery gjev 1,5 A eller 3 A ved 5 V, altså 7,5 eller 15 W. (05 punkt 5)
- FAKTA: Mange powerbankar slår seg av når straumen fell under ein terskel, ofte rundt 50 til 200 mA. Nokre har ein eigen modus for låg straum, og éin slik slo seg likevel av etter eit par timar. ([0110.be](https://0110.be/posts/Powering_low_current_electronics_projects_with_power_banks))
- FAKTA: micro:bit-stiftinga rår frå å drive micro:bit frå USB-powerbank, fordi nokre gjev spenning utanfor området ved låg last eller når dei slår seg av ([micro:bit, power supply](https://tech.microbit.org/hardware/powersupply/)).
- TOLKING: Stemningsmodus på nokre få prosent kan trekkje mindre straum enn terskelen, og då sløkkjer powerbanken lampa. Det er eit reelt designproblem for ei oppladbar lampe, og verdt eit eige forsøk: mål kor lågt du kan dimme før banken slår seg av. Driv micro:bit frå eigen batteripakke eller frå PC-en, og LED-lista frå powerbanken, med felles jord.
- TOLKING: 5 V-lister mistar spenning langs lista. Hald dei korte, eller mat dei frå begge endar, om enden blir svakare eller varmare i fargen.

---

## 6. Måling med telefon

### 6.1 Kor nøyaktige er luxappar?

- FAKTA: Eit lyslaboratorium testa sju telefonar og seks appar mot eit kalibrert luxmeter i klasse A, ved 100, 500 og 1000 lx. Avvika gjekk frå 3 % til 113 %. Android- og Windows-telefonar viste i snitt om lag 60 % for mykje, iPhone om lag 60 % for lite. Feilen var ikkje ein fast prosent: éin app viste 180 % for mykje ved 10 lx og 50 % for lite ved 10 000 lx. Fire like telefonar med same app gav ulike tal. Årsaka er at telefonar manglar sensor tilpassa augekurva og korrekt måling av skrått lys. Kalibreringa i appane gjekk berre i grove steg. Konklusjonen er at seriøs måling krev eige instrument. ([DIAL](https://dial.de/en-GB/news/luxmeter-app-vs-measuring-device))

### 6.2 Slik blir målingane samanliknbare (TOLKING)

- Lån eit luxmeter frå skulen om det finst. Det er den eine målereiskapen som er verd å spørje om.
- Bruk éin telefon, éin app og éin sensor gjennom heile prosjektet. Finn sensoren ved å dekkje til delar av framsida medan appen går.
- Prent ein haldar som held telefonen i fast vinkel og høgd, så sensoren alltid står vinkelrett på lysretninga. Skrått lys blir målt feil.
- Mørkt rom. Mål bakgrunnen først og trekk han frå.
- Samanlikn berre kjelder med om lag same lysfarge. Varmt og kaldt lys blir vekta ulikt.
- Mål i om lag same område som du kalibrerte i. Feilen endrar seg med nivået.
- Oppgje tala som forhold («oppsett B gav 1,8 gonger A»), ikkje som absolutte lux, om du ikkje har kalibrert.

**Kalibrering mot ei pære med kjend lysfluks (EIGA UTREKNING)**

- Formel: Ei kjelde som lyser likt i alle retningar har lysstyrke I = Φ / 4π og gjev E = I / d².
- 806 lm gjev I = 64 cd. Det gjev 257 lx på 0,5 m, 64 lx på 1,0 m, 29 lx på 1,5 m og 16 lx på 2,0 m.
- ANTAKING: Pæra lyser likt i alle retningar. Det gjer ho ikkje heilt. Mål frå sida, vinkelrett på pæra sin akse, langt frå vegger, og rekn med 20 til 30 % uvisse. Det er likevel langt betre enn 60 til 113 %.
- Noter kva appen viser i dei fire avstandane og lag di eiga korreksjonskurve.
- FAKTA: micro:bit har lysmåling gjennom LED-matrisa ([micro:bit, edge connector](https://tech.microbit.org/hardware/edgeconnector/)). UKJENT kor nøyaktig ho er, men ho kan logge relative endringar på ein fast stad.

### 6.3 Ansiktslys med webkamera

- FAKTA: I OBS Studio kan ein opne innstillingane til kameradrivaren frå eigenskapane til videokjelda og slå av automatisk eksponering, kvitbalanse og fokus der drivaren tillèt det. Brukarar melder at eksponeringa ofte har grove steg, og at innstillingane ikkje alltid blir hugsa. ([Ceedo](https://www.ceedo.com/how-to-optimize-webcam-settings-in-obs/) og [OBS-forumet](https://obsproject.com/forum/threads/how-to-precisely-control-camera-exposure-in-obs.138203/), søkjetreff)
- UKJENT: Om det innebygde kameraet i PC-en din kan låsast. Test det først.

Protokoll (TOLKING):

1. Ta to bilete av kvart oppsett. Eitt med låst eksponering og kvitbalanse, for å samanlikne lysmengd. Eitt med automatikk i Teams eller Zoom, for å sjå det motparten ser.
2. Hald alt anna fast: stol, avstand (60 cm), utsnitt, klede, bakgrunn, skjerminnhald (same kvite dokument, og same mørke modus), lysstyrke på skjermen, mørkt ute eller gardiner for.
3. Ha ein referanse i kvart bilete: eit kvitt ark og eit grått kort ved sida av ansiktet. Kan ikkje kameraet låsast, er referansen det einaste som gjer bileta samanliknbare.
4. Mål lux loddrett ved auget og på veggen bak deg til kvart bilete. 03 kap. 6 gjev mål: 100 til 300 lx på ansiktet og bakgrunnen om lag halvparten så lys.
5. Gje filene namn etter oppsett, avstand og nivå, og legg dei i éi rute ved sida av kvarandre.
6. Vurder: skuggar i augehola, blenk i briller, hudtone, skilje mellom ansikt og bakgrunn, striper.

- TOLKING: Pikselverdiar i vanlege bilete er ikkje lineære. Bruk dei til å rangere oppsett, ikkje til å rekne ut forhold.

---

## 7. Modellar utan budsjett

### 7.1 Skissemodellar for lys

- FAKTA: Kvitt papir reflekterer 70 til 80 %, kvit måling 75 til 85 % og matt aluminium 55 til 75 % ([Engineering ToolBox](https://www.engineeringtoolbox.com/light-material-reflecting-factor-d_1842.html)).
- TOLKING: Kvitt papir er altså ein like god diffus reflektor som matt metall, og gratis. Bygg reflektorar i papir og papp, skjermar i svart papp, diffusorar i bakepapir, kalkerpapir eller diffusorarka frå skjermane. Transmisjonen i bakepapir er UKJENT. Mål han.
- TOLKING: Lat papp og skumplate vere volumet, og prent berre det som må vere presist: haldar for lyskjelda, ledd, feste for optiske plater og masker, haldar for telefon og micro:bit. Då rekk du tre modellar på seks dagar.
- TOLKING: Lag kvar skissemodell slik at lyskjelda kan flyttast. Dei fleste forsøka i kap. 3 handlar om avstand og vinkel.

### 7.2 Volummodell i 1:1 som er større enn byggjevolumet

- FAKTA: Bambu Studio har eit kutteverktøy som deler modellen med plane snitt og legg inn koplingar av typen plugg, dybel eller snepp, slik at delane kan setjast saman att. Delane kan kuttast vidare. ([Bambu Lab, Cut tool](https://wiki.bambulab.com/en/software/bambu-studio/cut-tool) og [3D print large files](https://wiki.bambulab.com/en/a1/troubleshooting/3d-print-large-files), søkjetreff)
- EIGA UTREKNING: Diagonalen i byggjeplata er 256 × √2 = 362 mm. Romdiagonalen er 256 × √3 = 443 mm. Ein slank del på opptil om lag 35 cm kan altså prentast i eitt stykke om han ligg diagonalt.
- 03 reknar med lampehøgder på 30 til 55 cm (03 kap. 6). Dei høgaste må altså delast.
- TOLKING, rekkjefølgje frå billegast til dyrast:
  1. Kjerne i papp eller skumplate med prenta endestykke og ledd.
  2. Tynne skal i vasemodus som volum, stiva av med papp inni.
  3. Heilprenta delar, kutta med dyblar. Legg snittet der produktet uansett har ei delelinje.

### 7.3 Billeg overflatebehandling

- FAKTA ([Hubs](https://www.hubs.com/knowledge-base/post-processing-fdm-printed-parts/)): Slip frå korn 150 (korn 100 ved synlege feil eller laghøgd frå 0,3 mm) via 220, 400 og 600, gjerne vått. Fyll gliper og skøytar før sliping. Sparkel for bil er slipbar og kan målast. Grunn i to strok frå 15 til 20 cm avstand etter sliping til korn 600. Grunning og måling endrar måla. Sliping er ikkje tilrådd for delar med to eller færre perimetrar.
- TOLKING: Til volummodellen held det med fyll i skøytane, grunning, lett sliping og eitt strok matt farge. Prent med minst tre perimetrar om modellen skal slipast. Prisar på sparkel og spray er ikkje kontrollerte.

---

## 8. Denne veka: prioritert liste

Rekkjefølgja er sett etter kor mykje kvart forsøk avgjer for dei tre konsepta.

| Nr. | Forsøk | Tid | Avgjer |
|---|---|---|---|
| 0 | Sikre projektoren (2.2), les av typeskilt, pære og vifte (1.3). Kalibrer luxappen mot ei pære (6.2). | 1 time | Grunnlaget for alt anna. |
| 1 | Forsøk 1, veggfelt (3.1). | 2 timar | Om indirekte lys via vegg kan vere ansiktslys, eller berre stemning. |
| 2 | Forsøk 5 og 6, lysflate og blendkontroll med LCD-arka (3.5). | 3 timar | Om ei stor, tynn lysflate er eit konsept, og kor mørk ho blir frå sida. |
| 3 | Forsøk 3, kollimering og kjeldeposisjon (3.3), med måling av brennviddene. | 2 timar | Om ein reflektor som formar strålen kan vere arbeidslyset. |
| 4 | Forsøk 4, prenta plater (3.4). Start prentinga første dag. | 1 time pluss prentetid | Om retningsbestemt spreiing kan byggjast inn i forma. |
| 5 | Forsøk 8, striper i webkameraet (5.2). | 2 timar | Om PWM held, eller om kravet må vere straumregulering. |
| 6 | Forsøk 2, profil (3.2). | 2 timar | Om eit skarpt arbeidsfelt er verdt optikken. |
| 7 | Forsøk 9, vipp og snu (5.4), og forsøk 7, kantlys (3.5), om tida held. | 2 timar | Om modus kan lesast av forma. Om kantbelyst flate er realistisk. |

TOLKING: Forsøk 1, 2 og 3 peikar mot tre ulike lysprinsipp: lys på veggen, stor lysande flate og forma stråle frå skjult kjelde. Dei kan bli utgangspunkt for kvar sitt konsept, men det valet er ditt.

---

## 9. Handleliste

### 0 kr

- Det du har: telefon, PC, printar, Arduino, micro:bit, fresnelplata, projeksjonslinsa, spegelen, stolpen, LCD-arka.
- Frå heimen: ei lampe med LED-pære der lysfluksen står på pæra, USB-ladar eller powerbank, papp, kvitt papir, svart papp, bakepapir, teip, linjal, blyant.
- Frå verkstaden på skulen (ANTAKING at det finst): luxmeter til låns, akrylrestar på 3 mm, sandpapir, to logikknivå-MOSFET-ar, motstandar, koplingsbrett og leidning, ein avklipt USB-kabel.
- Filament: klar PETG om du har, elles klar eller naturfarga PLA.

### Maks 300 kr

Framlegg A, 248 kr:

- IKEA KABBLEKA LED-lyslenke med USB, dimbar, 3 m: 159 kr ([IKEA](https://www.ikea.com/no/no/p/kabbleka-led-lyslenke-med-usb-dimbar-70594601/)). Lyskjelde til lysboks, kantlys, veggfelt og PWM-forsøk.
- IKEA SOLHETTA LED-pære E27, 806 lm, to stykk: 89 kr ([IKEA](https://www.ikea.com/no/no/p/solhetta-led-paere-e27-806-lumen-dimbar-globeformet-opalhvit-60583924/)). Kjend lysfluks til kalibrering og veggfelt.
- 52 kr att. MOSFET-ar og koplingsbrett bør lånast. Prisar på desse er ikkje kontrollerte.

Framlegg B, 269,80 kr, om du manglar ei lita, sterk lyskjelde og vil ha ei list med kjende data:

- Clas Ohlson Asaklitt lommelykt, 200 lm, justerbar stråle: 149,90 kr ([Clas Ohlson](https://www.clasohlson.com/no/Batteridrevet-lommelykt-LED,-200-lumen,-Asaklitt/p/31-7326-2)).
- Clas Ohlson fleksibel LED-lyslist 1 m, 130 lm, 3100 K, Ra 80: 119,90 kr ([Clas Ohlson](https://www.clasohlson.com/no/Fleksibel-LED-lyslist-1-m/p/36-6704)).

TOLKING: Vel A. Telefonlykta dekkjer behovet for punktkjelde.

---

## Opne spørsmål og det som ikkje vart stadfesta

1. **Vifte og termosikring i projektoren.** Ingen av dei finst i bruksrettleiinga eller delelista for 3M 2000. Anten er projektoren ein annan modell (til dømes 2100, som har vifte), eller så er vifta ikkje spesifisert som eigen del. Les av skilta.
2. **Kva variant av 3M 2000.** Typeskiltet avgjer. Tala for pære og sikring i denne rapporten gjeld dei europeiske 230 V-variantane.
3. **Brennvidda til projeksjonslinsa** er utrekna (27 til 29 cm) og oppgjeven av ein forhandlar (292 mm, søkjetreff), ikkje funnen i 3M-dokument. Mål ho.
4. **Sikringsverdien** er 2,5 A i éin tabell og 5 A i ein annan.
5. **Bruksrettleiinga s. 3, 4, 8 og 13 til 15** er ikkje lesne. Dei ser ut til å vere dei same avsnitta på andre språk.
6. **Materialet i fresnelplata, lysfluksen frå halogenpæra og funksjonen til motstandssettet** er ukjende.
7. **Kor mykje prismeark smalnar lyskjegla i gradar** er ikkje funne. 3M si bruksrettleiing for lysstyrkefilm og databladet for BEF kunne ikkje opnast. Tala i 3.5 er frå ein skjermprodusent, ein displayleverandør og søkjetreff på patenttekstar og eit 3M-datablad. Kva for ein av dei to patenttekstane tala 1,6 og 2,6 kjem frå, er ikkje kontrollert.
8. **Transmisjon for diffusorark** har berre eitt ukontrollert leverandørtal.
9. **KABBLEKA:** lysfluks, fargetemperatur, Ra og frekvensen til den innebygde dimmaren er ikkje funne.
10. **Biltema** sine sider kunne ikkje opnast, så ingen prisar derifrå er med. Prisar på MOSFET-ar, koplingsbrett, sparkel og spray er ikkje kontrollerte.
11. **Standardperioden for PWM på micro:bit** og kor fin oppløysinga er ved 256 µs, er ukjent.
12. **Om webkameraet i PC-en kan låsast** på eksponering og kvitbalanse, er ukjent.
13. **Eigne innstillingar for klar PLA** er ikkje funne. Oppskrifta i 3.4 er utvikla for PETG.
14. **Kodeskissene** er ikkje køyrde på maskinvare.
15. **Kjelder som berre er sette som søkjetreff** er merkte i teksten. Det gjeld mellom anna Edmund Optics, 3M sine produktsider, B&H og wikien til Bambu Lab, som alle avviste henting.

---

## Kjelder

**Lokale filer**

- research/03-lys-og-syn.md (kap. 1, 3, 4, 6 og 9)
- research/05-teknologi-og-komponentar.md (punkt 3 til 9)
- research/06-regelverk-og-berekraft.md (materialseparasjon og to-komponent-plast)

**Projektoren**

- 3M 2000, bruksrettleiing (sidebilete lesne): https://www.manualslib.com/manual/872528/3m-2000.html
- 3M 2000, deleliste med sprengskisser: https://music.manualsonline.com/manuals/mfg/3m/2000_1.html og https://manualsdump.com/en/manuals/3m-2000model/163128/26 og https://www.manualslib.com/manual/655253/3m-2000.html
- 3M 2100, servicehefte, verkemåte: https://auto.manualsonline.com/manuals/mfg/3m/2100.html?p=6
- Aztek, 3M 2000AG: https://www.aztekcomputers.com/2000ag-portable-overhead-projector-with-1600-lumens-3m/p
- B&H, 3M 2000AG (søkjetreff): https://www.bhphotovideo.com/c/product/1003-REG/3M_HK_4000_0038_4_2000AG_Portable_Overhead_Projector.html/overview
- Firstlight, Osram 93592 FSX/FSY: https://en.firstlight.nl/lamps/entertainment-and-studio-lighting/halogen-lamps-110-240v/osram-93592-400w-230v-gy9-5-fsx-fsy/
- Ushio, tryggleik for halogenpærer: https://www.ushio.com/?p=1811
- Wikipedia, Overhead projector: https://en.wikipedia.org/wiki/Overhead_projector
- US 4,636,050, Reflection type overhead projector (søkjetreff): https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4636050

**Varme, sol og materiale**

- Prusament PETG, datablad: https://cdn.shopify.com/s/files/1/1745/6181/files/PETG_TechSheet_ENG.pdf
- Prusament PLA, datablad (søkjetreff): https://cdn.shopify.com/s/files/1/1745/6181/files/PRUSA_PLA_TechSheet_ENG.pdf
- All3DP, glasovergang for PLA og PETG (søkjetreff): https://all3dp.com/2/pla-petg-glass-transition-temperature-3d-printing/
- Wikipedia, Autoignition temperature: https://en.wikipedia.org/wiki/Autoignition_temperature
- Wikipedia, Solar irradiance: https://en.wikipedia.org/wiki/Solar_irradiance
- Wikipedia, Angular diameter: https://en.wikipedia.org/wiki/Angular_diameter
- Solar Brother, XL Fresnel lens (søkjetreff): https://www.solarbrother.com/en/buy/xl-fresnel-lens/
- US 4,457,585, Magnifier reader (søkjetreff): https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4457585
- Engineering ToolBox, refleksjonsfaktorar: https://www.engineeringtoolbox.com/light-material-reflecting-factor-d_1842.html

**Optikk**

- OpenStax, Thin lenses: https://openstax.org/books/university-physics-volume-3/pages/2-4-thin-lenses
- OpenStax, Spherical mirrors: https://openstax.org/books/university-physics-volume-3/pages/2-2-spherical-mirrors
- Wikipedia, Ellipsoidal reflector spotlight: https://en.wikipedia.org/wiki/Ellipsoidal_reflector_spotlight
- Wikipedia, Etendue: https://en.wikipedia.org/wiki/Etendue
- Wikipedia, Cylindrical lens: https://en.wikipedia.org/wiki/Cylindrical_lens
- Edmund Optics, Considerations in Collimation (søkjetreff): https://www.edmundoptics.com/knowledge-center/application-notes/optics/considerations-in-collimation/

**Klare printar og retningsbestemt spreiing**

- CNC Kitchen, transparente FDM-printar: https://www.cnckitchen.com/blog/transparent-fdm-3d-prints-are-clearly-stronger
- MatterHackers, klar filament: https://www.matterhackers.com/about/how-to-3d-print-clear-filament-for-better-transparency
- Snapmaker, klar filament: https://www.snapmaker.com/blog/how-to-3d-print-clear-filament/
- Orafol LN 669 hos FindLight (søkjetreff): https://www.findlight.net/optics/lenses/lenticulars/orafol-lenticular-ln-669
- LEDiL LINDA (søkjetreff): https://ledil.com/?p=12939
- LINDA-O, datablad hos Comet (søkjetreff): https://store.comet.bg/download-file.php?id=24937
- LEDs Magazine om Luminit (søkjetreff): https://www.ledsmagazine.com/leds-ssl-design/article/16679024/luminit-adds-lenticular-batwing-format-to-its-line-of-light-shaping-diffusers-for-ssl-design
- Stake Glass, rifla glas (søkjetreff): https://www.stakeglass.co.nz/products/reeded-glass

**LCD-bakbelysning**

- LG LE-15A10, manual s. 11, Function of Back Light: https://www.manualslib.com/manual/559239/Lg-Le-15a10.html?page=11
- Riverdi, What is BEF: https://riverdi.com/blog/what-is-bef-and-how-does-it-work
- Wikipedia, Backlight: https://en.wikipedia.org/wiki/Backlight
- Hackaday, DIY light guide plates: https://hackaday.com/2023/03/13/a-hackers-introduction-to-diy-light-guide-plates
- New Screwdriver (blogg), LG LCD Panel Backlight Also Has Layers: https://roger-random.github.io/newscrewdriver/2021/06/05/lg-lcd-panel-backlight
- 3M, bruksrettleiing for lysstyrkefilm (søkjetreff): https://multimedia.3m.com/mws/media/1839627O/3m-brightness-film-app-guide-75050141318-pdf.pdf
- US 8,740,442, Backlight and display system (søkjetreff): https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8740442
- US 7,898,520, Method and apparatus for backlight simulation (søkjetreff): https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7898520
- 3M ESR (søkjetreff): https://www.3m.co.uk/3M/en_GB/p/d/b5005047091/
- 3M DBEF (søkjetreff): https://www.3m.com/3M/en_US/p/d/b5005047085/
- 3M BEF III, datablad hos Elcodis (søkjetreff): https://elcodis.com/parts/151183/98044003659_dt658331_p3.html
- Information Display, diffusorfilm (søkjetreff): https://archive.informationdisplay.org/id-archive/2012/january/making-displays-work-for-you-diffuser-films-and-o
- PET-diffusor, leverandørtal (søkjetreff): https://china.org.ru/product/1600727505488

**Lyskjelder og prisar (sette 12.11.2026)**

- IKEA KABBLEKA: https://www.ikea.com/no/no/p/kabbleka-led-lyslenke-med-usb-dimbar-70594601/
- IKEA SOLHETTA: https://www.ikea.com/no/no/p/solhetta-led-paere-e27-806-lumen-dimbar-globeformet-opalhvit-60583924/
- Clas Ohlson, fleksibel LED-lyslist 1 m: https://www.clasohlson.com/no/Fleksibel-LED-lyslist-1-m/p/36-6704
- Clas Ohlson, Asaklitt lommelykt 200 lm: https://www.clasohlson.com/no/Batteridrevet-lommelykt-LED,-200-lumen,-Asaklitt/p/31-7326-2
- Clas Ohlson, Asaklitt sykkellykt 60 lm: https://www.clasohlson.com/no/Asaklitt-LED-sykkellykt-60-lm/p/31-1879
- Kjell, Ledsavers TV LED-list med USB: https://www.kjell.com/no/produkter/belysning-lamper/led-lister/rgb-led-lister/ledsavers-tv-led-list-med-usb-1-m-p57819
- MEAN WELL, isolert og ikkje-isolert drivar: https://www.meanwell.com/es/newsInfo.aspx?c=5&i=819
- CandlePowerForums, demontering av LED-pære (søkjetreff): https://www.candlepowerforums.com/threads/hyperikon-teardown.434087/
- Acebeam, lysfarge og Ra (søkjetreff): https://www.acebeam.com/led-beam-color

**Styring**

- Arduino, analogWrite (kjeldefila til referansesida): https://raw.githubusercontent.com/arduino/reference-en/master/Language/Functions/Analog%20IO/analogWrite.adoc
- Ken Shirriff, Secrets of Arduino PWM: http://www.righto.com/2009/07/secrets-of-arduino-pwm.html
- micro:bit MicroPython, pins: https://microbit-micropython.readthedocs.io/en/v2-docs/pin.html
- micro:bit MicroPython, accelerometer: https://microbit-micropython.readthedocs.io/en/v2-docs/accelerometer.html
- MakeCode, analog set period: https://makecode.microbit.org/reference/pins/analog-set-period
- MakeCode, on gesture: https://makecode.microbit.org/reference/input/on-gesture
- micro:bit, power supply: https://tech.microbit.org/hardware/powersupply/
- micro:bit, edge connector: https://tech.microbit.org/hardware/edgeconnector/
- Adafruit, RGB LED strips, usage: https://learn.adafruit.com/rgb-led-strips/usage
- Infineon, IRLZ44N (søkjetreff): https://www.infineon.com/assets/row/public/documents/24/49/infineon-irlz44npbf-datasheet-en.pdf
- Wevolver, Arduino Uno Rev3 (søkjetreff): https://www.wevolver.com/specs/arduino-uno-rev3
- 0110.be, powerbankar og låg straum: https://0110.be/posts/Powering_low_current_electronics_projects_with_power_banks

**Måling**

- DIAL, luxapp mot måleinstrument: https://dial.de/en-GB/news/luxmeter-app-vs-measuring-device
- Ceedo, webkamerainnstillingar i OBS (søkjetreff): https://www.ceedo.com/how-to-optimize-webcam-settings-in-obs/
- OBS-forumet, eksponering (søkjetreff): https://obsproject.com/forum/threads/how-to-precisely-control-camera-exposure-in-obs.138203/

**Modellar**

- Bambu Lab, P1 FAQ (søkjetreff): https://wiki.bambulab.com/en/p1/manual/faq
- Bambu Lab, Cut tool (søkjetreff): https://wiki.bambulab.com/en/software/bambu-studio/cut-tool
- Bambu Lab, 3D print large files (søkjetreff): https://wiki.bambulab.com/en/a1/troubleshooting/3d-print-large-files
- Hubs, etterbehandling av FDM-delar: https://www.hubs.com/knowledge-base/post-processing-fdm-printed-parts/
