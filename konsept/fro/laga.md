# Laga: to konseptfrø

Dato: 12.11.2026. Linse: lampa er bygd i lag etter levetid. Kropp og skjerm er for tiår, lysmodul og kretskort kan bytast, og batteriet er forbruksdel. Batteri og lysmodul er synlege, gripbare einingar. Lampa lyser fullt ut utan batteri, og demonteringsrekkjefølgja kan lesast av forma.

Dei to frøa deler linsa og skil seg i struktur:

| | Frø 1: Rull | Frø 2: Vend |
| --- | --- | --- |
| Kva handa flyttar | Lysmodulen (laget som blir bytt) | Skiva (laget som varer) |
| Lyskjelde | Lineær lysstav øvst, 350 mm over bordet | Punktkjelde i foten, 70 mm over bordet, lyser opp |
| Optikk og skjerm | Asymmetrisk linserekkje i staven. Fast, kvit vegg i plata | Djup reflektor i kjerna. Vendbar skive, kvit og halvblank |
| Drivar | I lysstaven | I foten |
| Batteri | Éin eller to stavar i klips bak veggen | Éin stav skoven inn i sida av foten |
| Fot | Fotdelen av den knekte plata | Rund stålfot som òg er kjøleflate |
| Leidning i kroppen | Ingen. Stolpane leier straumen | Ingen over foten |
| Betjening | Rulle staven, vri messingknotten på staven | Vende skiva, dreie messinghjulet i foten |
| Prosess | Knekt plate og røyr | Trykt og dreidd rundt gods, bøygd røyr |

**Lesenøkkel.** Rapportane i `research/` står med nummer, formromkartet som `00`. (k) = sida er lesen 12.11.2026 (produsent eller museum). (s) = berre søkjetreff, ikkje stadfesta. ANTAKING = føresetnad som ikkje er kontrollert. «Modell» = tal frå eigne skript, sjå under. Ingen av frøa er bygde eller målte.

## Felles føresetnader og reknemåte

- **Geometri.** Arbeidsfeltet er 0,6 × 0,4 m. Lampa står til venstre for feltet, 0,45 m frå feltsentrum og 0,10 m bak det. Auget ligg 0,30 m framfor feltsentrum og 0,47 m over bordet (`03`). Det gjev 0,60 m frå lampe til auge, slik `00` føreset. Lampa står då 48° til sida for blikkretninga mot skjermen.
- **Formlar.** Matt flate: L = ρ · E / π. Lys frå eit flateelement: dE = L · cos θ₁ · cos θ₂ · dA / r² (`13` kap. 3.1). Kvit lakk ρ = 0,85 og halvblank aluminiumsspegel ρ = 0,85 (ANTAKING).
- **Luminans.** «Høgast» er 95-persentilen over flata. Måla er under 500 cd/m² i stemning og under 1500 cd/m² i møte.
- **Ansiktslys.** Oppgjeve to gonger: på ei flate vend mot lampa, og på ei loddrett flate vend mot kameraet (ansiktet ser mot skjermen). Det siste er lågast, fordi lampa står til sida.
- **Verknadsgrad og celle.** 80 lm/W frå batteri til lys ut av lysmodulen (`05`). Éi 21700-celle: 17,8 Wh, 85 % brukbart = 15,1 Wh (`05`). Brukstid t = 15,1 / (Φ / 80) timar.
- **Modell.** Rull: lysstaven er 31 punktkjelder, summert over vegg og bord i rutenett. Vend: 600 000 strålar frå kjerna, spegla eller spreidde på skiva. Handkontroll står i reknestykka.
- **Batteristaven** er felles for begge frøa: aluminiumsrøyr Ø 25 × 100 mm med éi verna 21700-celle og polar i endane. Ho er ein ferdig pakke, fordi laus Li-ion-celle ikkje er avklart for brukarbyte (`05`).
- **Skript.** Mellombelse filer i `C:/Users/Iver/AppData/Local/Temp/claude/8532dfb00720264d/2c1f63c0-844c-4780-bd7e-44e5353e679d/scratchpad/konsept/`: `laga_vals.py`, `laga_vals2.py`, `laga_vals3.py`, `laga_vals4.py` (Rull), `laga_vend.py`, `laga_vend2.py` (Vend), `laga_slutt.py` og `laga_slutt2.py` (tala som er siterte her).

## Frø 1: Rull

**Namn.** Rull.

**Éi setning.** Ei knekt plate med to tynne stolpar ber ein laus lysstav som handa rullar: mot lampa sin eigen kvite vegg gjev staven glød og ansiktslys, mot bordet gjev han arbeidslys, og same grepet lyfter han ut den dagen han skal bytast.

**Steget.** Næraste busette naboar er Northern Archive (knekt stålplate med fast, lineær LED på kabel, `01`) og Marset Theia M (sving om aksen gjev leselys eller indirekte lys, `00`). Regel: fast lysmodul bak skjerm, med leidning → laus lysstav i to fjørklips, med éin asymmetrisk optikk som kan rullast mellom to plan. Éin regelbruk gjev tre følgjer:

1. Det er lysmodulen sjølv som blir flytta, ikkje hovudet eller skjermen. Laget som blir bytt, er laget handa kjenner.
2. Flata staven lyser på i stemning og møte, er lampa sin eigen vegg: 780 cm² plate utan elektronikk.
3. Kvardagsgrepet og bytegrepet er det same. Staven og batteriet sit i like klips, og det går ingen leidning i kroppen.

**Konflikt.**

- K1, stemning mot arbeidslys, er hovudsaka. Lysfordelinga følgjer staven, ikkje dimmaren. Same 300 lm gjev anten 500 lx på feltet frå ei kjelde auget ikkje ser, eller ein vegg med 700 cd/m² som gjev 48 til 55 lx på ansiktet. Dimma til 60 til 120 lm er veggen ein glød under 500 cd/m². Prøva i `00` (500 lx og glød under 500 cd/m² frå same lampe, skifte i éi rørsle) er halden i modellen.
- K3, flyttbar mot vedvarande lys, blir flytta eit stykke. Lysnytte 0,36 til 0,39 mot 0,20 til 0,28 for ei lampe som lyser rundt seg, og plass til to stavar utan verktøy, gjev 7,4 til 7,9 timar med 500 lx. Kurva seier 2,8 til 4,0 celler for åtte timar. Her trengst 2,0 til 2,2.
- K2 blir ikkje flytta etter prøva i `00`. Luminansen i augeretninga er låg, men lekamen er 26 × 19 × 36 cm, fordi ansiktslyset krev areal (V2).

**Struktur.**

- **Lyskjelde:** 8 diodar på eit aluminiumskort inne i lysstaven (Ø 25 × 250 mm), 350 mm over bordet, rett over knekken i plata. Dim-to-warm på éin kanal, 3000 til 1800 K, Ra minst 90 (ANTAKING: passiv to-strengs kopling, `05` punkt 3).
- **Optikk:** éi asymmetrisk linse per diode bak eit 12 mm breitt vindauge langs staven. Lyset blir kasta frå 5° til 58° til éi side for linseaksen.
- **Skjerm:** veggen, 300 × 260 mm, kvit, lent 30° bakover, 172 mm frå staven.
- **Drivar:** konstantstraumsdrivar og potensiometer med brytar inne i lysstaven. Staven er ei sjølvstendig lampe for 3 til 5 V med ein pol i kvar ende.
- **Straum:** stolpane (rustfritt stål Ø 6 × 350 mm) er leiarane, pluss i den eine og minus i den andre.
- **Batteri:** éin eller to batteristavar i fjørklips på foten bak veggen, synlege frå sida og bakfrå. USB-C-port og kort for lading og vern ligg under eit lite deksel same stad.
- **Fot:** fotdelen av plata, 260 × 190 mm. Ingen ballast.
- **Betjening:** handa rullar staven. Messingknotten i enden av staven er dimmar og brytar.

**Lys.** Tal frå modellen med to linsemodellar. Linsa er ei ANTAKING, sjå reknestykket.

| Modus | Lys frå staven | Kvar lyset går | Lysande flate og luminans | Lux på målet | Effekt og brukstid |
| --- | --- | --- | --- | --- | --- |
| Stemning | 60 til 120 lm, 1800 til 2200 K | 67 % på veggen, 33 % forbi veggen og ned på bordet ved sida av og bak lampa | 780 cm². Snitt 140 til 279, høgast 247 til 493 cd/m² | 18 til 37 lx ved auget | 0,75 til 1,5 W. 20 til 10 timar per stav |
| Arbeid | 306 til 329 lm, 3000 K | 36 til 39 % på feltet, 66 til 71 % på bordflata 1,2 × 0,7 m | Veggen er mørk. Vindauget vender ned og er ikkje synleg frå auget | 500 lx i snitt, lågast 207 til 242 lx, U0 0,41 til 0,49 | 3,8 til 4,1 W. 4,0 til 3,7 timar per stav, 7,9 til 7,4 timar på to |
| Møte | 300 til 365 lm | 67 % på veggen | Snitt 698 til 850, høgast 1234 til 1501 cd/m² | 48 til 67 lx mot kamera, 92 til 112 lx mot lampa | 3,75 til 4,6 W. 4,0 til 3,3 timar per stav |

- Utan batteri lyser lampa fullt ut på USB-C. 7,5 W dekkjer alle modusane. Staven er avgrensa til 6 W (480 lm) av varme.
- Auget ligg 11° over horisontalplanet gjennom staven. Alt lys frå vindauget går nedover, så dioderekkja er skjult for den som sit.
- Stemning ved 60 lm gjev 18 lx ved auget på 0,6 m, om lag 8 lx melanopisk EDI med DER 0,44 (`03` kap. 5, ANTAKING for 2700 K). Ved 120 lm må lampa stå 0,8 m unna for å halde 10 lx.

**Overgang.** Éin finger rullar staven 85° på om lag eitt sekund. Linseaksen går frå 70° bakover (veggen) til 15° framover (feltet). Mellom ytterstillingane ligg lyset som ei øy på bordet framfor lampa. Potensiometeret sit i staven og måler vinkelen mellom staven og messingknotten, som blir halden att av friksjon mot stolpen. Rullinga hevar difor nivået og fargetemperaturen medan lyset flyttar seg frå vegg til bord. Å vri knotten endrar nivået åleine, til dømes opp i veggstillinga før eit møte. Rullemomentet er sett til 0,02 Nm, altså 1,6 N med éin finger. Veltegrensa er 2,1 N.

**Form.** Tre primærformer: knekt plate, to stolpar, stavar.

- Plata er 260 mm brei og 490 mm utfalda. Fotdelen er 190 mm djup.
- Veggdelen er 300 mm lang og reiser seg frå framkanten av foten med spiss vinkel (60°), slik at han lener 30° bakover over foten. Veggtoppen ligg 265 mm over bordet.
- Dei to nedre hjørna av veggen (20 × 20 mm) er ikkje knekte opp. Dei står att som tunger i fotplanet, og der står stolpane, 250 mm frå kvarandre.
- Lysstaven ligg vassrett mellom stolpetoppane, 350 mm over bordet. Frå sitjande auge er han synleg om lag 55 mm over veggtoppen.
- Batteristavane ligg parallelt med lysstaven, bak veggen.
- Ytre mål 275 × 190 × 363 mm. Breidd til høgd om lag 3 : 4.

**Material.**

- **Plate:** aluminium 1,5 mm, laserskoren og knekt éin gong. Pulverlakkert i éin Northern-farge, kvit på veggflata. Ingen delspesifikke verktøy (`07` punkt 3).
- **Stolpar:** rustfritt stål Ø 6 mm, kappa, med gjenge i botnen. Lakkerte opp til dei øvste 15 mm. Isolerte frå plata med hylser i POM.
- **Lysstav:** aluminiumsrøyr Ø 25 × 1,5 mm med frest vindauge, LED-kort på aluminium, linserekkje i PMMA som blir klemd fast, endepolar og knott i dreidd, ubehandla messing.
- **Klips:** fjørbronse, seks like. To for lysstaven, fire for batteristavane.
- **Tal delar (overslag):** om lag 43 med skruar, 18 ulike. Lysstaven er 7 delar (røyr, LED-kort, linserekkje, drivarkort, potensiometer med knott, to endepolar), batteristaven 5.
- **Vekt per fraksjon (overslag):** aluminium 634 g, rustfritt stål 154 g, messing 30 g, fjørbronse 30 g, PMMA 12 g, POM 15 g, elektronikk 45 g, celle 70 g. Sum 0,99 kg, og 1,10 kg med to batteristavar.
- **Metallråvare:** 2,6 kg CO2e med valsa aluminium i REDUXA-klassen, røyr i CIRCAL-klassen og rustfritt stål på 1,6 kg CO2e per kg. Med globale snitt er talet 10,2 kg (faktorar frå `07` punkt 5).
- **Pris:** ikkje rekna. ANTAKING: Archive, med same plateprosess og fast LED, kostar 3 690 til 5 190 kr (`01`). Rull har i tillegg stolpar, laus stav og batteri og ligg truleg øvst i prisvindauget på 2 990 til 3 990 kr eller over.

**Reparasjon.**

- **Batteri:** dra staven ut av to klips og trykk inn ein ny. 0 verktøy, 0 festemiddel, under 10 sekund. Måltalet i ramma er under eitt minutt.
- **Lysmodul:** lyft lysstaven ut av dei to klipsa på stolpane. 0 verktøy, 0 festemiddel, under 10 sekund. Måltalet er under fem minutt. Staven kan snuast, så knotten kan sitje til høgre eller venstre.
- **Inne i staven:** éin endepropp med gjenge, skrudd for hand, og éin pluggkontakt mellom LED-kort og drivarkort.
- **Kretskort i foten:** 2 skruar i dekselet og 2 i kortet, same type (Torx T10), 2 pluggkontaktar.
- **Resten:** 2 skruar under stolpane og 6 for klipsa. I alt 12 skruar av éin type, eitt verktøy, ingen lim.
- Lampa lyser fullt ut på USB-C med tomme batteriklips.
- **Rekkjefølgja kan lesast:** stavane ligg opne i klips, dekselet med to skruar ligg bak veggen, og plata og stolpane er det som står att.
- **Alternativ som bør vurderast:** tre AA NiMH i ein stav på 160 mm, slik Panthella V2 hadde (`05` punkt 4). Det gjev 7,2 Wh mot 17,8 Wh, men cella blir seld overalt.

**Northern.** Held H1 (plate, stolpar, stavar), H3 (lyset er alltid reflektert eller retta nedover), H4 (éin farge, med kvit veggflate som den eine kontrasten, slik Acorn, Me, Gear og Ink har kvit innside, `01`), H5 (messingknotten er einaste varme metallpunkt og er der handa skal) og H6 (namnet er handlinga). H2 er halden i ny form: to tynne stolpar ber eit lyshovud som er ein stav, ikkje eit volum. Brote: observasjonen i `01` om at elektronikk blir gøymd, sidan batteristavane er synlege bakfrå. Plass på aksen: nær attkjenning i form (slektning av Archive, same prosess og format), og endring på aksane der Northern ikkje har variasjon (lysformat, arbeid på batteri, ansiktslys, fargetemperatur som følgjer nivået).

**Naboar.**

- Northern Archive: knekt stålplate i 25 eller 50 cm breidd, fast LED på 900 eller 1100 lm, kabel, 3 690 til 5 190 kr (`01`). Skilnad: laus stav, eigen vegg, batteri.
- Marset Theia M: sving om aksen gjev leselys eller indirekte lys, 1066 lm, kabel (`00`). Skilnad: der blir hovudet vendt, her lysmodulen, og han kan takast ut.
- Flos Oblique: asymmetrisk linse, 7 W, kabel (`00`). Same optikkprinsipp for bordet, men éi stilling.
- Zafferano Pencil: laus, oppladbar LED-stav som blir sett i ulike feste, med batteriet inne i staven (s). Skilnad: her er batteriet ein eigen stav, og staven har retta optikk og ein vegg å lyse på.
- Davide Groppi TeTaTeT: batteristav Ø 25 × 330 mm (`00`). Der er staven stamma, her ein laus del i klips.
- Artemide Tizio: lågspent straum går gjennom metallkonstruksjonen, utan leidning (k).
- Airam Campus LED: bordlampe med utskiftbart LED-røyr i sokkel G23, 7,2 W, 670 lm, nettspenning (s). Zhaga Book 14: lineære LED-modular i sokkel, verktøyfritt byte (`05`, søkjetreff).
- LEDiL Florence-1R ZT25: asymmetrisk veggvaskarlinse på 19,5 × 286 mm for éi rekkje diodar, oppgjeven til 92 til 93 % verknadsgrad og til liming (s). Ho er lengre og breiare enn staven, så anten må ho kappast og klemmast, eller staven må bli Ø 28 × 300 mm. Ikkje avgjort.

**Skissemodell.**

- **Form i full storleik:** kapaplate 5 mm eller grå papp 2 mm, 260 × 490 mm, rissa og bretta til 60°, med kvitt papir på veggflata. To rundstenger Ø 6 × 350 mm (sveisetråd eller trepinne). Lysstav og batteristav prenta som røyr Ø 25 mm, lysstaven i to halvdelar på 125 mm. U-klips prenta. Mutrar som lodd til 0,99 kg. Om lag tre timar pluss printtid.
- **Lysmockup:** 25 cm USB-LED-list inne i det prenta røyret, 8 mm bak eit spor på 12 mm, som skjer lyset av ved om lag 50° til kvar side. Eit prismeark frå byggjesettet over sporet, med prisma på tvers av staven, smalnar lyset langs staven (`13` kap. 3.5). Telefonlykta i same høgd med ein skråskoren pappkrage viser retta lys mot bordet.
- **Målingar:** lux i ni punkt på veggen, lux ved ansiktet 0,6 m unna, lux i rutenett på 10 cm på feltet, og foto frå 47 cm høgd for kvar 30° av rullinga, med låst eksponering (`13` kap. 6).

**Prøve.** Føreseiingane er skrivne før modellen er bygd. Dei gjeld ei list på 33 lm (25 cm av ei list på 130 lm per meter, `13` kap. 4) i spor utan linse:

1. Veggen får 156 lx i snitt (42 cd/m²), og høgaste verdi er under 2,5 gonger snittet.
2. Ansiktet får 5,5 lx på 0,6 m, på ei flate vend mot lampa.
3. Feltet får 27 lx i snitt, lysnytte 0,20 og U0 0,23. Med prismearket stig lysnytta mot 0,26 til 0,28 dersom arket smalnar lyset til 30° til kvar side. Vinkelen er ikkje målt (`13`).
4. Dioderekkja er ikkje synleg frå 47 cm høgd i nokon stilling mellom vegg og bord.
5. Ein person som ikkje har sett lampa, går frå stemning til arbeid på under 3 sekund med éi hand, og tek staven ut og set han inn att på under 10 sekund.

Det som feller konseptet:

- Diodar er synlege frå sitjande auge.
- Veggen er meir ujamn enn 2,5 gonger snittet i beste stilling, eller ansiktslyset er under 70 % av føreseiinga. Då når ikkje veggen 50 lx innanfor 1500 cd/m².
- Lysnytta i spor er under 0,15, altså tre firedelar av modellen. Då er modellen for optimistisk, og linseutgåva vil krevje over 400 lm og 5 W for 500 lx, under 3 timar per stav.
- Lampa veltar eller sklir når staven blir rulla med éin finger.

**Sviktrom.**

Aksar konseptet ikkje held:

- X8: fotavtrykket er 26 × 19 cm, mot Ø 16 cm i tyngdepunktet til bordlykta. K2-prøva i `00` er ikkje halden.
- Jamnheit: U0 0,41 til 0,49 når lampa vender mot feltet, og 0,23 til 0,28 når ho er dreidd 30° mot ansiktet. Referansen er 0,6.
- Flate ved skjermen i arbeidsmodus: veggen får ikkje direkte lys når staven lyser på bordet, så målet på 100 til 150 lx er ikkje halde. Ei mellomstilling gjev veggen 143 lx per 100 lm, men då er den fjerne delen av feltet mørk. Mogleg tiltak som ikkje er rekna: to sidelysande diodar i bakkant av kortet (ANTAKING, om lag 30 lm ekstra).
- X11 med éin stav: 3,7 til 4,0 timar med 500 lx. Den opne regionen O1 (minst 4 timar) er ikkje trygt nådd.
- Ansiktslys: 48 til 67 lx mot kamera frå sida. 100 lx mot kamera er ikkje mogleg innanfor 1500 cd/m².
- Den som har auga lågare enn 35 cm over bordet (barn, sofa), ser inn i linserekkja.

Dei tre største risikoane:

1. Linsa. Lysnytte 0,36 til 0,39 er ein modell av ei asymmetrisk linse per diode. Med berre list i spor er lysnytta 0,20, og 500 lx krev 600 lm og 7,5 W, over grensa på 6 W for staven. Handelsvara som er funnen, passar ikkje måla utan tilpassing.
2. Straum i stolpane og rullande kontaktar. Ein metallgjenstand mellom stolpane kortsluttar 5 V og krev elektronisk sikring. Kontaktane kan slitast og gje blink under rulling. Staven blir 37 til 47 °C ved 4 til 6 W i eit rom på 25 °C, og grensene for berøringstemperatur er ikkje verifiserte (`05`).
3. Retning og uttrykk. Sett frå lampa ligg feltet og ansiktet 29° frå kvarandre, så éi oppstilling tener ikkje begge fullt. Eit lysande, kvitt rektangel ved sida av skjermen kan bli lese som endå ein skjerm. Blank bordplate speglar linserekkja mot den som sit i kasteretninga.

**Reknestykke.**

1. **Geometri.** Veggen er 0,30 × 0,26 m = 780 cm², lent 30°. Staven ligg 350 mm over bordet, rett over knekken, 172 mm frå veggplanet. Auget ligg 0,12 m høgare enn staven og 0,60 m unna: arctan(0,12 / 0,60) = 11°.
2. **Linsemodell (ANTAKING).** Kvar diode har ei asymmetrisk linse. I planet på tvers av staven veks intensiteten som 1/cos² frå 5° til 58° frå linseaksen (modell «mild»), eller som 1/cos³ frå 12° til 62° (modell «skarp»). Langs staven er halvverdivinkelen 30°. Tala i lystabellen er spennet mellom dei to.
3. **Veggmodus.** Linseaksen 70° bakover frå loddlina. 67 % av lyset treffer veggen. Per 100 lm: E = 0,67 × 100 / 0,078 = 859 lx, og L = 0,85 × 859 / π = 232 cd/m² (modell 231 til 233). Høgast 396 til 411 cd/m², altså 1,7 til 1,8 gonger snittet.
4. **Stemning.** 60 lm: 0,6 × 233 = 140 og 0,6 × 411 = 247 cd/m². 120 lm: 279 og 493 cd/m². Ut av lampa: 0,85 × 0,67 = 57 % via veggen og 33 % forbi veggen, altså 54 til 108 lm. Effekt 60 / 80 = 0,75 W og 120 / 80 = 1,5 W. Brukstid 15,1 / 0,75 = 20 timar og 15,1 / 1,5 = 10 timar.
5. **Møte.** Per 100 lm får ansiktet 29 til 31 lx på ei flate vend mot lampa og 16,0 til 18,5 lx mot kamera (lågast når lampa vender mot feltet, høgast når ho vender mot ansiktet). 300 lm: 698 og 1234 cd/m², 48 til 55 lx mot kamera, 92 lx mot lampa. 365 lm: 850 og 1501 cd/m², 58 til 67 lx og 112 lx. Handkontroll for 300 lm: E ≈ L · A / r² = 698 × 0,078 / 0,75² = 97 lx før cosinusledd.
6. **Arbeid.** Lampa vender mot feltet, linseaksen 15° framover («mild») eller 5° («skarp»). Per 100 lm: 152 til 163 lx i snitt, lågast 63 til 79 lx, lysnytte 0,36 til 0,39, U0 0,41 til 0,49, og 66 til 71 % av lyset på bordflata. 500 lx krev 500 / 1,52 = 329 lm eller 500 / 1,63 = 306 lm. Handkontroll: 120 lm på feltet / 0,36 = 333 lm. Effekt 4,1 og 3,8 W. Brukstid 15,1 / 4,1 = 3,7 timar og 15,1 / 3,8 = 4,0 timar, det doble på to stavar. Åtte timar krev 8 × 306 til 329 = 2450 til 2630 lm·t, altså 2,0 til 2,2 celler à 1210 lm·t.
7. **Utan linse.** LED-list i spor med avskjering ved 50°: lysnytte 0,20, U0 0,23, 83 lx per 100 lm. 500 lx krev 600 lm = 7,5 W. Med prismeark som smalnar lyset langs staven til 30° til kvar side: lysnytte 0,26 til 0,28.
8. **Varme.** Stavflate π × 2,5 × 25 + 2 × π × 1,25² = 206 cm². ΔT = Q / (h · A) med h = 10 W/m²K og Q = 0,6 til 0,75 P (`05` punkt 7). 4,1 W: 12 til 15 K. 6 W: 17 til 22 K.
9. **Vekt.** Plate 1274 cm² × 0,15 cm × 2,7 g/cm³ = 516 g. Stolpar 2 × 77 g = 154 g. Lysstav 140 g. Batteristav 105 g. Kort, klips og skruar 75 g. Sum 0,99 kg.
10. **Velt.** Tyngdepunktet ligg 76 mm bak framkanten og 128 mm over bordet. Veltevinkel framover arctan(76 / 128) = 31°, bakover arctan(114 / 128) = 42°, sidelengs arctan(130 / 128) = 45°. Kraft som veltar lampa framover i stavhøgd: 0,99 × 9,81 × 0,076 / 0,35 = 2,1 N. Bakover 3,2 N. Rullemoment 0,02 Nm på radius 12,5 mm gjev 1,6 N.
11. **Metallråvare.** Valsa aluminium 0,532 kg × 4,0 = 2,13. Røyr 0,102 kg × 1,9 = 0,19. Rustfritt 0,154 kg × 1,6 = 0,25. Sum 2,6 kg CO2e. Globale snitt: 0,634 × 14,4 + 0,154 × 7 = 10,2 kg.

## Frø 2: Vend

**Namn.** Vend.

**Éi setning.** Alt elektrisk står som to proppar i foten og lyser opp på ei skive utan leidning: kvit side ned gjev glød og ansiktslys, halvblank side ned sender same strålen ned på arbeidsfeltet.

**Steget.** Næraste busette nabo er Northern Ombre (k): lyskjelda sit i foten og lyser opp på ein justerbar stålskjerm med kvit innside, 6 W, 550 lm, kabel, 1,8 kg, 3 990 kr. Regel: matt, justerbar reflektorskjerm over kjelda → flat skive med éi kvit og éi halvblank side som kan vendast, og alt elektrisk som lause einingar i foten. Éin regelbruk gjev tre følgjer:

1. Reflektoren får to optiske naturar. Den kvite sida spreier lyset og er ei stor, mjuk flate. Den halvblanke sida sender strålen samla vidare og er mørk frå auget.
2. Laget som varer lengst (stamme og skive, berre metall) ber modusskiftet. Laga som blir bytte (lyskjerne, batteri, kort) står samla i bordhøgd.
3. Spegelen gjev lang lysveg, 0,39 m opp og 0,62 m ned. Feltet blir lyst som frå ei kjelde ein meter unna, frå ei lampe der kjelda sit 7 cm over bordet.

**Konflikt.**

- K2, kompakt mot blendfri, er hovudsaka. Grensa L = Φ / (π · A) gjeld berre flater som lyser likt i alle retningar. Den kvite sida er ei slik flate og har arealet V2 krev: 616 cm², og 435 cm² sett frå brukaren. Den halvblanke sida er det ikkje. 274 lm gjev 500 lx på feltet utan at noko lysande areal er synleg frå auget. Atterhald: prøva i `00` krev lekam innanfor Ø 16 × 27,5 cm. Foten er Ø 15 cm, men skiva er Ø 28 cm i 46 cm høgd.
- K1 følgjer med. Skiva er lysfordelinga: same 270 lm er anten 500 lx på feltet eller ei flate på 860 cd/m² som gjev 56 til 65 lx på ansiktet.
- K3: lysnytte 0,44 (0,36 til 0,48 over tre strålemodellar) gjev 4,4 timar (3,6 til 4,8) med 500 lx på éi celle. Det ligg i den opne regionen O1 når strålen er god, og under når han er dårleg.

**Struktur.**

- **Lyskjelde:** éin dim-to-warm-COB med lysande flate Ø 9 mm, 3000 til 1800 K, Ra minst 90 (`05` punkt 2 og 3). Han sit i ei lyskjerne Ø 50 × 65 mm som står midt i foten og lyser rett opp. Lysopninga ligg 70 mm over bordet.
- **Optikk:** djup spegelreflektor i kjerna. Stråle 36° med flat topp og avskjerming ved 25° (ANTAKING at han finst som handelsvare).
- **Skjerm:** flat aluminiumsskive Ø 280 mm, 390 mm over kjerna. Kvit på den eine sida, halvblank med om lag 3° spreiing på den andre.
- **Drivar:** eitt kort i foten med USB-C, lading, vern og konstantstraumsdrivar som hevar spenninga til COB-en.
- **Batteri:** éin batteristav som blir skoven vassrett inn i sida av foten. Endeproppen stikk 8 mm ut.
- **Fot:** stål, Ø 150 × 40 mm, 540 g. Foten er kjøleflate for kjerna (365 cm²).
- **Stamme:** stålrøyr Ø 10 mm utan leidning, frå fotkanten i éin boge til skivekanten.
- **Betjening:** handa vender skiva. Eit dimmehjul i messing i fotkanten er dimmar og brytar.

**Lys.** Tal frå modellen med flat stråle på 36°. Spennet over tre strålemodellar står i parentes.

| Modus | Lys frå kjerna | Kvar lyset går | Lysande flate og luminans | Lux på målet | Effekt og brukstid |
| --- | --- | --- | --- | --- | --- |
| Stemning | 60 til 89 lm, 1800 til 2200 K | 75 % på den kvite sida, 25 % forbi skiva mot vegg og tak | 616 cm². Snitt 193 til 287, høgast 339 til 500 cd/m² | 20 til 33 lx ved auget | 0,75 til 1,1 W. 20 til 14 timar |
| Arbeid | 274 lm (252 til 335), 3000 K | 87 % treffer den halvblanke sida. 44 % av alt lyset landar på feltet, 73 % på bordflata | Skiva er mørk frå auget (ANTAKING: under 100 cd/m² frå strølys) | 500 lx i snitt, lågast 250 lx, U0 0,50 (0,40 til 0,52) | 3,4 W (3,2 til 4,2). 4,4 timar (3,6 til 4,8) |
| Møte | 266 lm (235 til 337) | 75 % på den kvite sida | Snitt 857, høgast 1500 cd/m² | 56 til 65 lx mot kamera, 98 lx mot lampa | 3,3 W. 4,5 timar |

- Utan batteri lyser lampa fullt ut på USB-C. 7,5 W dekkjer alle modusane. Kjerna toler 6 W (480 lm) fordi foten kjøler.
- Auget ser kjerneopninga 56° frå aksen og ligg 55° frå aksen til den spegla strålen. Reflektoren skjermar frå 25°, så verken kjelda eller spegelbiletet er synleg frå stolen.
- Stemning ved 60 lm gjev 20 til 22 lx ved auget, om lag 9 lx melanopisk EDI med DER 0,44 (`03` kap. 5, ANTAKING for 2700 K).

**Overgang.** Handa tek i skivekanten og vender skiva 156° om akslingen, frå kvit side ned og fram (45°) til halvblank side ned (21°), eller omvendt. Det tek om lag eitt sekund. Leddet har to kvilestillingar og anslag, slik at den halvblanke sida aldri kan stå brattare enn 30° og sende strålen vassrett. Frå møte til arbeid er vendinga heile overgangen, fordi nivået er det same (266 mot 274 lm). Frå stemning til arbeid trengst i tillegg ein tommel på dimmehjulet: to grep med same hand, to til tre sekund. Overgangen har to stillingar og er ikkje trinnlaus. Vendemomentet må vere under 0,05 Nm, fordi lampa veltar ved 1,3 N i skivehøgd.

**Form.** Tre primærformer: låg sylinder, tynn boge, flat skive.

- Fot Ø 150 × 40 mm. Lyskjerna Ø 50 mm står i midten og stikk 30 mm opp.
- Stamma er festa 60 mm frå fotsenter og går i éin boge med radius om lag 1,1 m ut til 140 mm frå senteraksen i 460 mm høgd. Der er enden bøygd inn og ber skiva i kanten.
- Skiva er Ø 280 × 1 mm med falsa kant. Senteret ligg 460 mm over bordet, rett over kjerna. Akslingen går vassrett gjennom skivediameteren og er lagra i éin kant.
- Høgd 51 cm med den halvblanke sida ned og 56 cm med den kvite sida ned.
- Skiva er 1,9 gonger fotdiameteren (Kin: 2,4 til 2,5, `01`). Foten er 7 til 8 % av høgda.

**Material.**

- **Fot:** botnplate i stål 2 mm, laserskoren, og skal i stål 1 mm, metalltrykt (låg verktøykostnad, `07` punkt 3). Pulverlakkert. Skrapbasert stål.
- **Stamme:** stålrøyr Ø 10 × 1,5 mm, bøygd i éi rørsle, lakkert i same farge.
- **Skive:** reflektorplate i aluminium 1 mm, halvblank anodisert på den eine sida (ANTAKING: handelsvare for armatur, ρ om lag 0,85) og kvitlakkert på den andre. Laserskoren, kanten falsa.
- **Ledd:** friksjonsledd med éin skrue og to anslag. Friksjonsskivene er slitedel og reservedel (`07`, pakke B).
- **Lyskjerne:** dreidd aluminium, COB i haldar med skruar, spegelreflektor, vindauge i glas halde av ein gjengering.
- **Dimmehjul:** dreidd, ubehandla messing.
- **Tal delar (overslag):** om lag 37 med skruar, 23 ulike. Lyskjerna er 6 delar (hus, COB, haldar, reflektor, vindauge, gjengering), leddet 5, batteristaven 5.
- **Vekt per fraksjon (overslag):** stål 703 g, aluminium 275 g, messing 30 g, glas 5 g, POM 15 g, elektronikk 50 g, celle 70 g. Sum 1,15 kg.
- **Metallråvare:** 1,4 kg CO2e med skrapbasert stål og aluminium i REDUXA- og CIRCAL-klassen. Med globale snitt er talet 5,6 kg (faktorar frå `07` punkt 5).
- **Pris:** ikkje rekna. ANTAKING: Ombre, med same oppbygging i stål og 6 W LED på kabel, kostar 3 990 kr (k). Vend har i tillegg batteri og laus lyskjerne og ligg truleg øvst i prisvindauget på 2 990 til 3 990 kr eller over.

**Reparasjon.**

- **Batteri:** dra staven vassrett ut av foten. 0 verktøy, 0 festemiddel, under 10 sekund.
- **Lysmodul:** vri lyskjerna ein kvart omgang (bajonett) og lyft ho opp. 0 verktøy, 0 festemiddel, under 10 sekund. To fjørkontaktar i setet. COB-en i kjerna sit i haldar med 2 skruar.
- **Kretskort:** 3 skruar i botnplata og 2 i kortet, same type (Torx T10), og pluggkontaktar til batteri, kjerne og USB-C.
- **Stamme og skive:** 1 settskrue i foten og 1 skrue i leddet. I alt 9 skruar av éin type, eitt verktøy, ingen lim.
- Lampa lyser fullt ut på USB-C med tom batteribrønn.
- **Rekkjefølgja kan lesast:** to proppar i foten (opp og ut), tre skruar under foten, og over foten er det ikkje noko å opne.

**Northern.** Held H1 (skive, linje, låg sylinder), H2 (ei tynn linje i éi rørsle, silhuetten er mest luft), H3 (alt lys er reflektert, og kjerna er skjerma), H5 (dimmehjulet i messing er einaste varme metallpunkt) og H6 (namnet er handlinga). H4 er broten: lekamen har éin farge, men skiva har to kontrastflater, kvit og halvblank aluminium. Begge finst i sortimentet kvar for seg (kvit innside, børsta aluminium på Hall og Glint, `01`). Lyshovudet er heller ikkje kompakt: skiva er Ø 28 cm. Slektningar: Ombre (kjelde i foten, reflektorskjerm), Glint (skive), Trace (lyskjelda som laus aluminiumssylinder, `01`). Plass på aksen: byggjer på Ombre og ligg lenger mot endring enn Rull, fordi ei speglande flate og ein open stråle er nytt hos Northern.

**Naboar.**

- Northern Ombre: kjelde i foten, justerbar matt reflektorskjerm, 550 lm, kabel (k). Skilnad: éi matt flate og éin modus.
- Marset Ginger 20 M: portabel, reflektert lys frå skive, 290 lm, 3,5 W, 5 timar (`00`). Skilnad: berre stemning.
- Flos Taccia: indirekte og reflektert lys frå aluminiumsreflektor, 28 W, kabel (k). Sida seier ikkje kvar kjelda sit.
- Foscarini Chapeaux M: 920 lm, 8 W (`00`).
- Nemo Kuta: rund reflektorskive med éi kvit og éi svart side (s). Skilnad: sidene er uttrykk, ikkje to lysfordelingar.
- Artemide Eclisse: indre skal formørkar kjelda (`00`). Der blir lyset stengt, her får det ein annan natur.
- Sminkespegel med to sider i bøyel: same vendegrep, utan lys (allmenn type).
- Northern Trace: lommelykt i anodisert aluminium, 3 W (`01`).
- Ei bordlampe der same reflektor har ei spreiande og ei speglande side, er ikkje funnen i to søk. Det tyder ikkje at ho ikkje finst.

**Skissemodell.**

- **Form i full storleik:** fot av stabla pappskiver eller print, Ø 150 × 40 mm, med stålplate eller mutrar inni (0,5 kg). Stamme av røyr eller rundstong Ø 10 × 520 mm, bøygd for hand. Skive i kapaplate 3 mm, Ø 280 mm, med kvitt papir på den eine sida og aluminiumsfolie med den matte sida ut på den andre. Ledd: gjennomgåande skrue med fjørskive i eit prenta nav. Om lag tre timar.
- **Lysmockup:** telefonlykta i foten, lysande rett opp gjennom eit papprøyr Ø 40 × 60 mm som skjer strålen til om lag 18° til kvar side. Frontflatespegelen frå projektoren teipa midt på den halvblanke sida. Kvitt papir som kvit side.
- **Variant:** fresnelspegelen (285 × 285 mm, f = 187 mm) med lykta 150 mm under gjev eit felt på om lag 44 cm i 40 cm avstand (`13` kap. 3.3). Berre inne, og aldri ved vindauge (`13` kap. 2.2).
- **Målingar:** lysfluksen frå lykta etter røyret (lux i rutenett på ein vegg, summert, `13` kap. 4). Lux i rutenett på 10 cm på feltet. Lux på skiva og ved ansiktet 0,6 m unna. Foto frå 47 cm høgd, frå stolen til brukaren og frå plassen i kasteretninga, med og utan ei blank plate på bordet.

**Prøve.** Føreseiingane er skrivne før modellen er bygd. Dei gjeld per lumen frå lykta etter røyret:

1. Halvblank side: 1,8 lx i snitt på feltet per lumen (lysnytte 0,44, og 0,46 med frontflatespegel dersom ρ er 0,9). U0 om lag 0,5. 90 % av lyset landar 0,11 til 0,83 m frå foten.
2. Kvit side (papir, ρ 0,75): 12 lx på skiva og 0,30 lx ved ansiktet per lumen. Høgaste verdi på skiva er under 2 gonger snittet.
3. Frå 47 cm høgd og 0,5 til 0,9 m avstand er verken lykta eller spegelbiletet av henne synleg, same kva side som vender ned.
4. Vendinga tek under 2 sekund med éi hand, utan at foten flyttar seg.

Det som feller konseptet:

- Lysnytte under 0,35 eller U0 under 0,3. Då er spegelen ikkje betre enn ei låg lampe ved sida av feltet, og 500 lx kostar over 340 lm.
- Lykta eller spegelbiletet er synleg frå stolen til brukaren.
- Den kvite sida er meir ujamn enn 2,2 gonger snittet, eller ansiktslyset er under 70 % av føreseiinga.
- Foten flyttar seg eller veltar når skiva blir vend.

**Sviktrom.**

Aksar konseptet ikkje held:

- Jamnheit: U0 0,50 (0,40 til 0,52). Referansen er 0,6.
- X7 og X8: 51 til 56 cm høg og Ø 28 cm øvst, over spennet til bordlykta. K2-prøva i `00` er ikkje halden.
- Overgangen er to stillingar, ikkje trinnlaus.
- Flate ved skjermen i arbeidsmodus: berre dei 13 % som går forbi skiva (36 lm), hamnar på vegg og tak. Utan ein vegg nær lampa er målet på 100 til 150 lx ikkje halde.
- Ansiktslys: 56 til 65 lx mot kamera frå sida. 100 lx mot kamera er ikkje mogleg innanfor 1500 cd/m². Sett frå lampa ligg feltet og ansiktet 29° frå kvarandre, så lampa må dreiast for det høgaste talet.
- H4: to kontrastflater.

Dei tre største risikoane:

1. Open stråle opp frå bordhøgd. Den som lener seg over lampa eller står nærare enn om lag 0,4 m, kan sjå ned i kjerna. Gjenstandar, støv og søl hamnar på vindauget. Fotobiologisk klasse må kontrollerast (`05` punkt 10). Ein raster i staden for djup reflektor vil ta 15 til 25 % av lyset.
2. Spegla stråle. Med blank bordplate ser den som sit i kasteretninga spegelbiletet av skiva. Skuggane blir skarpe: kjelde Ø 40 mm og 1 m lysveg gjev om lag 4 mm halvskugge bak ei hand 7 cm over bordet (w = s · b / a = 40 × 0,094 / 0,92). Feil stilt skive kan sende strålen i augehøgd, så anslaga i leddet er naudsynte.
3. Topptung lekam og føresetnader. Lampa veltar ved 1,3 N i skivekanten. Reflektans 0,85 og flat stråle er ANTAKING. Med ein gaussisk stråle på ±15° fell lysnytta til 0,36, og 500 lx krev 335 lm og gjev 3,6 timar. Den halvblanke flata får riper og fingermerke.

**Reknestykke.**

1. **Geometri.** Lysopninga ligg 70 mm over bordet og skivesenteret 460 mm, så kastet er 390 mm. Skiva er π × 0,14² = 616 cm². Stråle 36°: diameter ved skiva 2 × 390 × tan 18° = 253 mm.
2. **Halvblank side.** Skiva er vippa 21°, så midtstrålen går 42° frå loddlina og treffer bordet 0,46 × tan 42° = 0,42 m frå foten, i feltsentrum. Lysveg 0,39 + 0,46 / cos 42° = 1,01 m. Modell (flat stråle 36°, spreiing 3°, ρ 0,85): 87 % treffer skiva, lysnytte 0,44, 182 lx per 100 lm, lågast 91 lx, U0 0,50, 73 % på bordflata. Handkontroll: 0,87 × 0,85 × 0,59 (delen av den spegla strålen som landar i feltet) = 0,44. Gaussisk stråle ±12°: lysnytte 0,48, U0 0,40. Gaussisk ±15°: 0,36 og 0,45.
3. **Arbeid.** 500 / 1,82 = 274 lm (252 til 335). 274 / 80 = 3,4 W. 15,1 / 3,4 = 4,4 timar (3,6 til 4,8).
4. **Kvit side.** Vippa 45°. 75 % treffer skiva. Per 100 lm: E = 0,75 × 100 / 0,0616 = 1218 lx, og L = 0,85 × 1218 / π = 330 cd/m² (modell 322). Høgast 565 cd/m², altså 1,75 gonger snittet.
5. **Stemning.** 60 lm: 193 og 339 cd/m². 89 lm: 287 og 500 cd/m². Ut av lampa: 0,85 × 0,75 = 64 % via skiva og 25 % forbi skiva, altså 53 til 79 lm.
6. **Møte.** Høgaste luminans 1500 cd/m² ved 1500 / 5,65 = 266 lm. Snitt 3,22 × 266 = 857 cd/m². Per 100 lm får ansiktet 33 til 37 lx mot lampa og 21 til 24 lx mot kamera (lågast når lampa vender mot feltet, høgast når ho er dreidd 29° mot ansiktet). 266 lm: 56 til 65 lx mot kamera, 98 lx mot lampa. Handkontroll: E ≈ L · A · cos 45° / r² = 857 × 0,0616 × 0,71 / 0,60² = 104 lx.
7. **Blendgeometri.** Auget ligg 0,40 m over kjerneopninga og 0,60 m unna: arctan(0,60 / 0,40) = 56° frå aksen. Sett frå kjerna dekkjer skiva 20° til kvar side når ho ligg flatt (arctan(140 / 390)). Vippa 45° dekkjer ho 11° på den høge sida og 19° på den låge. Utanfor skiva og innanfor 25° er kjerna open for den som ser rett ned: i 0,8 m høgd over kjerna er det ei sone ut til 0,8 × tan 25° = 0,37 m frå aksen.
8. **Varme.** Fotflate π × 7,5² + π × 15 × 4 = 365 cm². 3,4 W: 6 til 7 K. 6 W: 10 til 12 K. Batteribrønnen ligg i same fot og held seg under 45 °C (`05`) ved romtemperatur opp til om lag 30 °C. ANTAKING: tørr kontakt mellom kjerne og fot leier varmen. Det må målast.
9. **Vekt.** Fot 540 g (botnplate 277 g, skal 263 g). Stamme 163 g. Skive 190 g. Kjerne 105 g. Batteristav 105 g. Kort, hjul og skruar 45 g. Sum 1,15 kg.
10. **Velt.** Tyngdepunktet ligg 128 mm over bordet og 10 mm til sida. Veltevinkel arctan(65 / 128) = 27°. Kraft som veltar lampa i skivekanten: 1,15 × 9,81 × 0,065 / 0,56 = 1,3 N. Vendemoment 0,05 Nm gjev 0,36 N i kanten, 0,14 m frå akslingen.
11. **Metallråvare.** Stål 0,703 kg × 0,69 = 0,49. Valsa aluminium 0,190 kg × 4,0 = 0,76. Dreidd og ekstrudert aluminium 0,085 kg × 1,9 = 0,16. Sum 1,4 kg CO2e. Globale snitt: 0,703 × 2,34 + 0,275 × 14,4 = 5,6 kg.

## Forkasta undervegs

- **Lysstav med lineær linse.** LED-list i spor gjev lysnytte 0,18 til 0,20 på feltet, og ei linse som berre formar lyset på tvers av staven, gjev 0,25 til 0,32 (modell). 500 lx krev då 375 til 670 lm. Erstatta med éi asymmetrisk linse per diode i Rull.
- **Opal glaskuppel som ansiktslys.** Ei halvkule på Ø 200 mm lyser i alle retningar. 1000 cd/m² gjev om lag 55 lx på ansiktet og krev 197 lm ut, altså 280 til 660 lm inne i kuppelen ved 30 til 70 % transmisjon (`05` punkt 8), 3,5 til 8 W. Erstatta med kvit flate vend mot brukaren.
- **Holspegel i Vend.** Høgare lysnytte, men ei skive på Ø 280 mm samlar opptil 60 W sollys i eit brennpunkt, same fare som fresnelplata i `13`. Erstatta med flat skive. Fresnelplata blir berre brukt som forsøk.
- **To blanke stenger som straumskinne med lause einingar i ulike høgder.** Mange lause delar, fare for kortslutning og teknisk uttrykk. Berre prinsippet med straum i stolpane er ført vidare i Rull.
- **Veggstilling i Rull med staven rulla 90° bakover.** Høgaste luminans blei 3,1 gonger snittet (modell), med eit lyst band øvst. Erstatta med 70°, som gjev 1,7 til 1,8 gonger snittet og 67 % av lyset på veggen.

## Kjelder for naboane

Kontrollerte 12.11.2026 (k):

- Northern Ombre bordlampe: https://www.northern.no/products/ombre-table-lamp
- Flos Taccia: https://professional.flos.com/en-US/us/product/taccia-f6602004/
- Artemide Tizio, omtale hos Museo Omero: https://museoomero.it/en/opere/tizio/

Berre søkjetreff (s), ikkje stadfesta:

- Zafferano Pencil (sida gav 429): https://www.zafferanoitalia.com/en-eu/products/pencil-led-module-big
- Nemo Kuta (databladet gav 403): https://www.nemolighting.com/usa/wp-content/uploads/sites/3/tech-sheets/en/kuta-table.pdf
- LEDiL Florence-1R: https://www.ledil.com/data/prod/Florence/Florence-1R-sfds.pdf
- Airam Campus LED: https://www.airam.fi/en/product/v18192/campus-led/campus-led/385/1

Dei andre naboane er henta frå `00`, `01` og `05`. Nabosøket er fire søk og seks sideoppslag. Det er ikkje søkt i patentbasar.
