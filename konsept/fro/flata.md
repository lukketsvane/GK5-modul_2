# Flata: to konseptfrø

Dato: 12.11.2026. Linse: lampa er eit plan, ikkje eit volum. Ei stor, tynn lysande flate med låg luminans kan vendast, lenast, leggjast ned eller hengjast, og stillinga til flata avgjer om ho gjev stemning, arbeidslys eller ansiktslys.

Dei to frøa deler linsa og skil seg i struktur:

| | Frø 1: Klaff | Frø 2: Tavle |
| --- | --- | --- |
| Lekam | Éin lekam med hengsel | To lekamar: laus tavle og passiv stolpe |
| Lyskjelde | LED-band i kanten av ei grunn skål | LED-list i ryggen på tavla |
| Optikk | Grunt holrom, opal front med lineære prisme | Kantbelyst lysleiar, opal front |
| Drivar og celle | I foten | I ryggen på tavla |
| Fot | Stamme og fot ber alt | Stolpen gjev berre høgd og leidning |
| Betjening | Hengselvinkelen er dimmaren | Festepunktet vel stilling og tak, hjulet set nivået |
| Overgang | Trinnlaus boge | Flytting mellom to hol |

**Lesenøkkel.** (k) = lese på produsentside, datablad eller forhandlarside 12.11.2026. (s) = berre søkjetreff, ikkje stadfesta. ANTAKING = føresetnad som ikkje er kontrollert. «Modell» = tal frå eige skript, sjå under. Rapportane i `research/` står med nummer, formromkartet som `00`.

## Felles føresetnader og reknemåte

- **Geometri.** Bordflata er z = 0. Brukaren sit ved bordkanten og ser innover bordet. Auget er 47 cm over bordet (`03`). Arbeidsfeltet er 0,6 × 0,4 m, frå 10 til 50 cm inn på bordet. Ansiktet blir rekna 45 cm over bordet.
- **Plassering A:** lampa står 30 cm til venstre for midtlinja og 45 cm inn på bordet, ved sida av ein laptop. **Plassering B:** lampa står midt bak laptopen, 62 cm inn på bordet.
- **Formlar.** Diffus flate: L = Φ / (π · A). Lys frå eit flateelement: dE = L · cos θ₁ · cos θ₂ · dA / r² (`13` kap. 3.1). Skive rett framfor ansiktet: E = π · L · a² / (a² + d²) (`03` kap. 6). Vegg: L = E · ρ / π med ρ = 0,7.
- **Modell.** Flata er delt i 28 × 28 punkt og summert numerisk over eit rutenett på 5 cm i feltet. Kontrollert mot to handrekna tilfelle: punktkjelde 35 cm over midten av feltet gjev 37,2 % på feltet i begge metodar, og skive Ø 250 mm med 150 lm gjev 127 lx på 0,6 m i begge.
- **Prismeark (ANTAKING).** Eitt prismeark smalnar lyset i planet på tvers av rillene. Modellen er ei gaussisk fordeling i dette planet med halvverdivinkel 40° og uendra fordeling langs rillene. Når lysstraumen er halden fast, gjev det forsterking 1,60 langs normalen. LG oppgjev 1,55 (`13` kap. 3.5). Vinklane og sidelobane er ikkje målte og er det forsøk 6 i `13` skal avgjere. Tap i arket er ikkje med.
- **Verknadsgrad (ANTAKING).** 80 lm/W frå celle til lys ut for holrommet (spenn 60–110, `00`). 65 lm/W for den kantbelyste lysleiaren, fordi verknadsgraden er ukjend (`05` punkt 8).
- **Celle.** Éi 21700: 4,9 Ah × 3,63 V = 17,8 Wh, 85 % brukbart = 15,1 Wh (`05` punkt 4).
- **Skript.** Mellombelse filer i `C:/Users/Iver/AppData/Local/Temp/claude/8532dfb00720264d/2c1f63c0-844c-4780-bd7e-44e5353e679d/scratchpad/konsept/`: `flata_rekn.py` (modell), `flata_fro1.py`, `flata_fro1b.py`, `flata_fro2.py`, `flata_skjerm.py`, `flata_forkasta.py` og `flata_slutt.py` (tala som er siterte her).

## Frø 1: Klaff

**Namn.** Klaff.

**Éi setning.** Ei flat, rund lysskive er hengsla i kanten til toppen av ei tynn stamme, og hengselvinkelen er dimmaren: hengande er ho glød mot veggen, ståande er ho ansiktslys, og lagd fram over bordet er ho arbeidslys som auget ikkje ser.

**Steget.** Næraste busette nabo er Nimbus Roxxane Fly (k): flatt hovud på 110 × 110 mm med 270° ledd rett på foten, om lag 400 lm, eigen gestedimmar. Regel: flatt hovud med ledd og eigen dimmar → flate på 491 cm² hengsla i kanten på toppen av ei stamme, der hengselet er dimmaren. Éin regelbruk gjev tre følgjer:

1. Lysstraum og fargetemperatur følgjer vinkelen gjennom eit potensiometer i leddet, utan mikrokontrollar.
2. Flata vender seg bort frå auget medan lysstraumen stig frå 34 til 600 lm.
3. Kantfestet gjev tre høgder for midten av flata: 265 mm (heng), 400 mm (ligg) og 535 mm (står). Det er låg glød, arbeidslys under augehøgd og ansiktslys over augehøgd.

**Konflikt.**

- Stemning mot arbeidslys (K1 i `00`). Kurva gjeld lamper med éi lysfordeling. Her endrar vinkelen retning, høgd, nivå og farge i same rørsle: 49–62 lm mot veggen bak, og 500 lx på feltet frå 372–498 lm.
- Kompakt mot blendfri (K2). 491 cm² ligg i ei skive på 22 mm (1,2 liter, mot 8,2 liter for ei kule med same tverrsnitt). I arbeidsstilling vender flata ned 40 cm over bordet, og auget ligg over planet: 0 cd/m². Med prismeark held modellen luminansen mot auget under 1500 cd/m² langs heile bogen. Det siste er ei føreseiing, ikkje eit resultat.
- Flyttbar mot vedvarande lys (K3) blir ikkje flytta. 372 lm i 3,25 timar er 1209 lm·t, altså på kurva. Arbeidslyset går på leidning, slik ramma seier.

**Struktur.**

- Lyskjelde: LED-band med 36 mid-power-diodar (Ra minst 90) på bøyeleg aluminiumskort, 760 × 10 mm, i spenn mot innsida av skålkanten. Dim-to-warm på éin kanal: to strengar (om lag 1800 K og 3000 K) med analog straumdeling på kortet. ANTAKING: kurva må veljast og målast.
- Optikk: holrom Ø 250 × 18 mm med kvitlakkert, svakt kvelva botn. Front: opal PMMA 2 mm med lineære prisme på innsida, rillene parallelle med hengselet. ANTAKING: plata finst som halvfabrikat (`13` kap. 3.4). I mockupen: diffusorark, eitt prismeark, diffusorark.
- Drivar: boost-drivar med analog (straumregulert) dimming, ladekrets med straumveg og ladegrense 4,05 V, og avlesing av USB-C-kjelda (`05` punkt 4 og 5). Alt på eitt kort i foten.
- Batteri: éi 21700-celle liggjande i foten, i haldar med fjørkontaktar.
- Fot og stamme: fot Ø 160 × 30 mm med laus stålskive som ballast. Stamme Ø 12 mm, 370 mm, med leidningane inni. USB-C i foten.
- Betjening: hengselet har 270° vandring og driv eit lineært potensiometer på 10 kΩ med 1 kΩ last. Kvilestillinga (0–10°) bryt straumen med ein mikrobrytar, altså ingen kvilestraum. Ein messingknott på enden av leddhuset er fintrim (30–100 %).

**Lys.** Lysande areal i alle modusar: Ø 250 mm, A = π × 0,125² = 0,0491 m² (491 cm²). Lambertsk: L = Φ / 0,154. Med prismeark: L₀ = 1,6 × Φ / 0,154 langs normalen. Dimmekurve: Φ = 600 lm × t / (1 + 10 · t · (1 − t)), der t = vinkel / 270°.

| Modus | Vinkel | Lysstraum, effekt | Kvar lyset går | Luminans mot auget | Lux på målet |
| --- | --- | --- | --- | --- | --- |
| Stemning | 30–90°, skiva heng eller ligg bakover | 34–62 lm, 0,4–0,8 W, 36–19 t per celle | Mot veggen bak og opp. 27–33 lm treffer ein vegg 15 cm bak | 0 cd/m² ved 30–75°, der flata vender 95–135° bort frå auget. Ved 90° ser auget flata i streifvinkel: 402 cd/m² lambertsk, 30–130 med prisme (modell) | Vegg: opptil 516–794 lx, altså 115–177 cd/m² |
| Møte | 180°, skiva står | 124 lm, 1,55 W, 9,7 t per celle | Rett fram mot ansiktet, 6–7° over augehøgd | 1288 cd/m² med prisme, 804 utan | Ansikt: 135–189 lx med prisme, 89–124 lx utan |
| Arbeid | 255–270°, skiva ligg fram | 372–600 lm, 4,7–7,5 W | Ned på feltet. 33–34 % treffer feltet med prisme, 24 % utan | 0 cd/m² ved 265–270°. Ved 255°: 230–760 cd/m² (modell utan og med 20 % sidelobar) | Felt: 510–521 lx ved 372 lm (prisme), 496–507 lx ved 498 lm (utan) |

- Kontroll av møtetalet med formelen i `03`: E = 0,131 × 1288 = 168 lx rett framfor på 0,6 m.
- Vender ein heile lampa mot seg i kvilestilling, gjev 34 lm ein glød på 220 cd/m² (lambertsk) eller 353 cd/m² (prisme langs normalen).
- På celle: 372 lm i 3,3 timar, 498 lm i 2,4 timar. På leidning: 600 lm ved 7,5 W, 604–804 lx.
- Mellomstilling 225°: 209 lm gjev 180–185 lx på feltet og 153–162 lx på ansiktet samstundes, med 1000–1050 cd/m² mot auget (modell).
- Melanopisk: 30 lm på veggen gjev 0,7 × 30 / π = 6,7 cd og 11 lx ved auget på 0,77 m, altså om lag 5 lx melanopisk EDI med DER 0,44 (ANTAKING for 2700 K, `03` kap. 5).

**Overgang.** Ta i kanten av skiva og før ho i ein boge. Frå kvile til ståande er 180°, om lag 2 sekund. Vidare 75–90° fram til liggjande er om lag 1 sekund. Éi hand. Nivå og farge følgjer vinkelen, og lyset blir aldri slått av undervegs. Stillinga er minnet: vinkelen viser nivået. Frå arbeid til møte er det eitt løft på 75–90°, og lysstraumen fell då frå 372–600 til 124 lm utan at brukaren rører noko anna.

**Form.** Tre primærformer og eit lite ledd.

- Skive Ø 264 × 22 mm (lysande Ø 250).
- Stamme Ø 12 mm, 370 mm, loddrett.
- Fot Ø 160 × 30 mm.
- Leddhus Ø 24 × 70 mm, vassrett på toppen av stamma, med messingknott Ø 22 × 12 mm i den eine enden. Hengselaksen ligg 400 mm over bordet, og skiva er festa i kanten, 135 mm frå aksen til midten.
- Høgd: 412 mm i kvile, 420 mm i arbeid, 667 mm i møte. Skiva kragar 190 mm ut frå fotkanten i arbeid.
- Proporsjonar: skive mot fot 1,65 : 1, stamme mot skive 1 : 22.
- Vekt om lag 1,16 kg: hovud 0,37 kg, stamme og ledd 0,21 kg, fot med ballast og celle 0,57 kg.

**Material.**

- Skål: aluminium 1,0 mm, metalltrykt (`07`: låg verktøykost), pulverlakkert utvendig i éin Northern-farge, kvit innvendig. 730 cm² ytre flate er kjøleflate.
- Front: PMMA 2 mm, skoren frå plate. Halden av ein fjørring i rustfritt stål.
- Leddhus: dreia aluminium. Friksjonsledd med svak torsjonsfjør og hakk i kvilestillinga. Knott: dreia messing, ubehandla.
- Stamme: stålrøyr, kappa og gjenga. Fotkappe: trykt eller dreia aluminium. Ballast: laserskoren stålskive Ø 130 × 3 mm (313 g), laus. Botnlok: aluminium med bajonett.
- Elektronikkberar: PA12, printa i første seriar.
- Ingen sprøytestøyping og ingen delspesifikke verktøy utanom trykkform og kretskort.
- Kostnadsmål rekna som i `05` punkt 12: 2 990–3 990 kr / 1,25 / 4–6 = 400–800 kr i produksjonskost. Ikkje kalkulert.

**Reparasjon.**

- Batteri: botnlok med kvart omdreiing og myntspor, 0 skruar. Cella ligg i haldar. Føreseiing: under 30 sekund. Verktøy: mynt.
- Lysmodul: fjørring ut, frontskive ut, 1 plugg, 2 skruar M3 Torx T10, LED-bandet ut. Føreseiing: under 5 minutt. Verktøy: T10.
- Heile lampa: 6 skruar av same type (2 i LED-bandet, 2 i leddhuset, 2 i elektronikkberaren), 1 fjørring og 1 bajonett. Stamma er gjenga inn i fot og leddhus. To verktøy: T10 og mynt.
- Ingen lim. Lampa lyser fullt på leidning utan celle (straumveg).
- Slitedelar som verkstaden byter: potensiometeret i leddet (1 mutter, 1 plugg) og leidninga gjennom leddet (plugg i begge endar).

**Northern.** Held H1 (skive, linje, låg sylinder), H3 (opal front, kjelda er aldri synleg), H4 (éin matt farge over skål, ledd, stamme og fot), H5 (messingknotten er einaste varme metallpunkt og er betjening) og H6 (klaffen blir slått opp og lagd fram, og namnet er handlinga). Bøyer H2: linja ber eit hovud på 26 cm, og leddet er synleg. 5 av 6. Forma ligg nær tyngdepunktet: Kin og Tradition har stor hatt, Salto har flat opal diffusor og messing, Balancer har skjerm som blir vippa. Det nye ligg på aksane der svermen ikkje har variasjon (K4): fargetemperatur som følgjer nivået, tre lysformat, kamera og arbeidslys med celle. Plassering: nær attkjenning i form, ny i optikk og betjening.

**Naboar.**

- Nimbus Roxxane Fly (k, datablad DE 05/16): flatt hovud 110 × 110 mm på 270° ledd, om lag 400 lm, 5,5 W, 2700 K, Ra over 90, 4–20 timar, 560 g, gestestyring, magnetar i foten. Brukaren kan ikkje byte batteriet. Skilnad: flata er 121 cm² mot 491 cm². 400 lm frå 121 cm² ville vore om lag 10 500 cd/m² frå ei diffus flate (eiga utrekning; Nimbus avblendar med kjeglesenkingar). Leddet sit rett på foten, og opna er lampa høgst 185 mm. Nivået er uavhengig av vinkelen, og fargen er fast.
- Lume Cube Edge Light 2.0 (s, `02`): hovud som kan vendast mot ansiktet, 700 lm, kabel, touch.
- Marset Theia M (k, `00`): sving om aksen gjev leselys eller indirekte lys, 1066 lm, kabel.
- Circa frå Haworth (k, forhandlarside): rund, flat LED-skive som kan vippast 45° og dreiast 360°, touch i tre steg. Lysstraum og batteri er ikkje oppgjevne.
- Northern Balancer mini (`01`): roterbar skjerm, to stillingar.
- Ingen av dei koplar nivå og farge til vinkelen. `05` fann ingen etablert designlampe som dimmar ved vipping. «Ikkje funnen» tyder ikkje «finst ikkje».

**Skissemodell.**

- Modell i full storleik, 4–5 timar: skive av to lag 5 mm kapa eller papp Ø 264 med 22 mm kant (printa kant i fire segment om printaren skal brukast, kvart under 256 mm). Stamme: røyr eller rundstokk Ø 12 × 370 mm. Fot: printa skål Ø 160 × 30 fylt med stålskiver til 0,57 kg. Ledd: M6-bolt gjennom printa leddhus med filtskive og vingemutter, stramma til skiva står i alle vinklar. Lodd i skiva til 0,37 kg, slik at løft og velt kan prøvast.
- Lysmockup, 2–3 timar: pappskål Ø 250 × 18 fôra med kvitt papir, USB-lyslenke langs innsida av kanten, og over opninga diffusorark, eitt prismeark med rillene parallelt med leddet, og diffusorark (forsøk 5 og 6 i `13`). Ein micro:bit teipa på skiva les vinkelen og styrer lyslenkja gjennom ein MOSFET etter kurva over (`13` kap. 5). I produktet er det eit potensiometer, ikkje ein sensor.
- Måling: lux i rutenett på 10 cm over 0,6 × 0,4 m ved 255° og 270°. Lux loddrett ved ansiktet ved 180°. Foto med låst eksponering frå augepunktet for kvar 15°, med og utan prismeark. Luxappen blir kalibrert mot ei pære på 806 lm (`13`).

**Prøve.** Føreseiingane er skrivne før modellen er bygd.

1. Blending langs bogen (K2). Føreseiing: lysstyrken i foto frå augepunktet, i høve til rett forfrå, er høgst 0,25 ved 240° og høgst 0,20 ved 255° med prismeark, og om lag 1,0 utan. Fell: over 0,54 ved 240° eller over 0,39 ved 255°. Då er flata over 1500 cd/m² medan ho er synleg (268 og 372 lm).
2. Arbeidslys (K1). Føreseiing: 33 % av lysstraumen treffer feltet ved 255° med prismeark og 24 % utan. Det gjev 500 lx frå om lag 370 lm, med lågaste verdi 0,25–0,40 av snittet. Fell: under 20 %. Då krev 500 lx meir enn dei 600 lm som 7,5 W gjev.
3. Møte. Føreseiing: 124 lm gjev 135–190 lx loddrett på ansiktet på 0,55–0,63 m, ved høgst 1300 cd/m². Fell: under 100 lx når flata held 1500 cd/m², eller hud som kameraet ikkje klarer å kvitbalansere.
4. Overgang. Føreseiing: frå kvile til arbeid med éi hand på under 3 sekund, utan at foten lettar. Fell: foten lettar eller lampa veltar. Rekna margin er minus 2 % med hovud på 0,38 kg og pluss 8 % med 0,30 kg, sjå reknestykket.
5. Reparasjon. Føreseiing: ein person som ikkje har sett lampa, tek ut cella på under 1 minutt og LED-bandet på under 5 minutt. Fell: meir enn to verktøy eller meir tid.

**Sviktrom.**

Aksar konseptet ikkje held:

- Jamnheit på feltet: lågaste verdi er 0,11–0,42 av snittet. Referansen er 0,6 (V7 i `00`).
- Lys på skjermen: 470–690 lx på ein laptopskjerm i feltet (tilta 20°) når feltet har om lag 500 lx. Rettesnora i `03` er under 215 lx. Flata held ikkje lyset unna skjermen.
- Breidd og høgd: 264 mm brei og 667 mm høg i møtestilling. Volumet er lite (1,9 liter mot 5,5 liter for bordlykta), utstrekninga er ikkje.
- Brukstid ved arbeid: 2,4–3,3 timar per celle. Region O1 i `00` (4 timar) blir ikkje nådd.
- 300 lx på resten av bordet er ikkje halde.
- Frå sofa, med auget lågare enn skiva, er undersida synleg: opptil 3900 cd/m² utan prismeark ved 600 lm, 400–1700 cd/m² med (modell).
- Veltevinkel 11° i arbeidsstilling og 19° i møtestilling (rekna). Kravet i standarden er ikkje verifisert (`07`).
- Fargetemperaturen i møtestilling er ukjend. Der går 21 % av full straum, og lyset kan bli for varmt for kameraet.

Dei tre største risikoane:

1. Prismearket. Sidelobar og tap er ikkje målte. Utan arket er flata 1740–2760 cd/m² mot auget mellom 240° og 262°, og då fell K2 i mellomstillingane.
2. Leddet. Det ber 0,3–0,4 kg på 135 mm arm, har potensiometer og leidning gjennom seg, og løft med éi hand er på grensa til å lette foten.
3. Lesinga. Ei skive på 26 cm på tynn stamme kan lesast som ringlys eller skjermutstyr, og ho dekkjer ein ekstern skjerm om ho blir lagd framfor han.

**Reknestykke.**

- Areal og luminans: π × 0,125² = 0,0491 m². π · A = 0,154. 100 lm gjev 648 cd/m² lambertsk og 1039 cd/m² langs normalen med prisme.
- Dimmekurve, lasta spenningsdelar: f = t / (1 + (R_pot / R_last) · t · (1 − t)).

| Vinkel | t | f | Lysstraum | Effekt ved 80 lm/W |
| --- | --- | --- | --- | --- |
| 30° | 0,111 | 0,056 | 34 lm | 0,42 W |
| 60° | 0,222 | 0,081 | 49 lm | 0,61 W |
| 90° | 0,333 | 0,103 | 62 lm | 0,78 W |
| 135° | 0,500 | 0,143 | 86 lm | 1,07 W |
| 180° | 0,667 | 0,207 | 124 lm | 1,55 W |
| 225° | 0,833 | 0,349 | 209 lm | 2,62 W |
| 240° | 0,889 | 0,447 | 268 lm | 3,35 W |
| 255° | 0,944 | 0,619 | 372 lm | 4,65 W |
| 265° | 0,981 | 0,831 | 498 lm | 6,23 W |
| 270° | 1,000 | 1,000 | 600 lm | 7,50 W |

- Luminans mot auget langs bogen, plassering A (modell). Vinkelen er mellom normalen til flata og retninga til auget.

| Vinkel | Lysstraum | Vinkel mot auget | Lambertsk | Prisme, utan sidelobar | Prisme, 20 % sidelobar |
| --- | --- | --- | --- | --- | --- |
| 90° | 62 lm | 84° | 402 | 32 | 127 |
| 150° | 96 lm | 43° | 623 | 587 | 578 |
| 180° | 124 lm | 31° | 805 | 1255 | 1236 |
| 195° | 144 lm | 32° | 935 | 1465 | 1442 |
| 210° | 171 lm | 40° | 1109 | 1403 | 1381 |
| 225° | 209 lm | 52° | 1357 | 1045 | 1029 |
| 240° | 268 lm | 67° | 1740 | 574 | 565 |
| 255° | 372 lm | 83° | 2410 | 227 | 760 |
| 265° | 498 lm | 94° | 0 | 0 | 0 |
| 270° | 600 lm | 99° | 0 | 0 | 0 |

  Alle tal i cd/m². Høgaste verdi med prisme er 1465 cd/m² ved 195°.

- Arbeidsfeltet (modell).

| Plassering, vinkel | Lysstraum | Optikk | Snitt | Lågast / snitt | På feltet |
| --- | --- | --- | --- | --- | --- |
| A, 255° | 372 lm | prisme | 510 lx | 0,25 | 122 lm, 33 % |
| A, 255° | 372 lm | lambertsk | 359 lx | 0,36 | 86 lm, 23 % |
| A, 265° | 498 lm | lambertsk | 507 lx | 0,30 | 122 lm, 24 % |
| A, 270° | 600 lm | prisme | 804 lx | 0,11 | 193 lm, 32 % |
| A, 270° | 600 lm | lambertsk | 619 lx | 0,27 | 149 lm, 25 % |
| B, 255° | 372 lm | prisme | 521 lx | 0,40 | 125 lm, 34 % |
| B, 265° | 498 lm | lambertsk | 496 lx | 0,42 | 119 lm, 24 % |
| B, 270° | 600 lm | lambertsk | 604 lx | 0,39 | 145 lm, 24 % |

  Kontroll med punktformelen for ei lita lambertsk flate 40 cm over bordet: 25,7 % (A) og 24,8 % (B) på feltet. Modellen gjev 25 og 24 %.

- Lysnytte og brukstid: 120 lm på feltet krev 357–381 lm med prisme (4,5–4,8 W, 3,2–3,4 t per celle) og 484–526 lm utan (6,1–6,6 W, 2,3–2,5 t).
- Møte: skivemidt 535 mm over bordet, 0,55 m frå ansiktet i A og 0,63 m i B. 124 lm: L₀ = 1,6 × 124 / 0,154 = 1288 cd/m². V2 i `00`: 196 lx rett framfor ved 1500 cd/m² for Ø 250 på 0,6 m.
- Stemning, vegg 15 cm bak stamma: 34 lm ved 30° gjev opptil 516–543 lx (115–121 cd/m²). 49 lm ved 60° gjev opptil 590–794 lx (131–177 cd/m²).
- Tersklar i prøve 1: ved 255° er L₀ = 1,6 × 372 / 0,154 = 3856 cd/m², og 1500 / 3856 = 0,39. Ved 240° er L₀ = 2784 cd/m², og 1500 / 2784 = 0,54.
- Varme: 7,5 W gjev 4,5–5,6 W varme. Skåla har 547 + 182 = 730 cm². ΔT = Q / (h · A) = 6–8 K med h = 10 W/m²K. Kravet i V5 er 300–375 cm².
- Vekt: skål (547 + 182) cm² × 0,10 cm × 2,7 = 197 g. Front π × 12,5² × 0,2 × 1,18 = 116 g. LED-band, fjørring og hengselblad om lag 60 g. Stamme 144 g, ledd 70 g. Ballast π × 6,5² × 0,3 × 7,85 = 313 g, fotkappe 110 g, celle 70 g, kort og lok 80 g. Sum om lag 1,16 kg.
- Velt: tyngdepunktet ligg 44 mm ut frå stamma og 188 mm oppe når skiva ligg fram. tan θ = (80 − 44) / 188 gjev 10,8°. Ståande: 80 / 233 gjev 19°.
- Løft med éi hand: tyngdemomentet om leddet er 0,382 × 9,81 × 0,135 = 0,51 N·m. Friksjonen må vere større, til dømes 0,60 N·m. Løft frå vassrett krev då 1,11 N·m, altså 4,3 N i ytterkanten. Veltemoment om bakre fotkant: 1,11 × (1 + 0,08 / 0,26) = 1,45 N·m. Vekta held imot med 1,16 × 9,81 × 0,08 + 0,51 = 1,42 N·m. Foten lettar så vidt. Med hovud på 0,30 kg og friksjon 0,50 N·m: 1,17 mot 1,26 N·m. Med avlastingsfjør (friksjon 0,25 N·m): 0,85 mot 1,26 N·m.

## Frø 2: Tavle

**Namn.** Tavle.

**Éi setning.** Ei tynn, kantbelyst lystavle med celle, drivar og hjul i ryggen er heile lampa, og ein passiv stolpe med tapp gjev henne høgd og leidning: ståande på tappen er ho ansiktslys, liggjande på tappen er ho arbeidslys, og løfta av er ho ei glødande flate som kan stå, lenast, leggjast eller hengjast.

**Steget.** Næraste busette nabo er Nimbus Roxxane Leggera 52 CL (`02`): heile lampa er den flyttbare delen, og dokka berre ladar. Regel: éin lekam der dokka berre ladar → sjølvstendig lysflate og ein stolpe som gjev høgd og leidning, der festepunktet er modusen. Ryggen har to hol som passar på same tapp:

1. Holet i botnen av ryggen gjev ståande tavle (skilt), med tak på 200 lm.
2. Holet tvers gjennom ryggen gjev liggjande tavle med lysflata ned (hylle), med tak på 600 lm.
3. Utan tapp går tavla på cella, med tak på 70 lm.

Taket følgjer kor synleg flata er: under 500 cd/m² når ho er laus, under 1500 cd/m² når ho står mot ansiktet, og full styrke berre når auget ikkje ser ho.

**Konflikt.**

- Flyttbar mot vedvarande lys (K3). Kurva Φ · t per celle blir ikkje flytta fysisk, men konflikten blir lagd til to tilstandar (K3 b og c i `00`). På tappen driv leidninga arbeidslyset utan tidsgrense. Av tappen ber cella aldri meir enn 70 lm, altså 1,1 W i 14 timar. Cella blir bytt med ein mynt.
- Stemning mot arbeidslys (K1). Stillinga endrar fordelinga: laus og låg, ståande mot ansiktet, eller liggjande over feltet. Å løfte tavla av tappen gjer arbeidsplassen til heim att i éi rørsle, slik reformuleringa i ramma seier.
- Kompakt mot blendfri (K2). 450 cm² ligg i ei tavle på 8 mm (0,65 liter med rygg). Full styrke finst berre i stillinga der flata er skjult.

**Struktur.**

- Lyskjelde: LED-list på 250 mm med 30 mid-power-diodar (Ra minst 90) på aluminiumskort i ryggen. Lista lyser inn i kanten på lysleiaren. Dim-to-warm på éin kanal som i frø 1 (ANTAKING).
- Optikk: lysleiarplate i PMMA, 2 mm, 250 × 190 mm, med laserprikka uttaksmønster. Bak: kvitlakkert innside av bakbrettet. Framfor: opal PMMA 1 mm. Ingen film i produktet. I mockupen: arka frå LCD-bakbelysninga.
- Drivar, ladekrets, celle og dreiehjul: i ryggen, eit firkantrøyr på 30 × 30 × 260 mm. Elektronikken sit på ein skuff som glir inn frå enden. Dreiehjulet i messing er potensiometer med brytar: nivå, og av ved klikk.
- Batteri: éi 21700-celle i den andre enden av ryggen, bak eit lok med myntspor.
- Fot: stolpe med stålrøyr Ø 10 mm på ei fotskive Ø 140 mm. Øvst ein tapp Ø 8 × 28 mm som er koaksial kontakt med tre polar: 5 V, jord og eitt signal som seier kva straum USB-C-kjelda tillèt. I foten: USB-C-kontakt, kjeldeavlesing og sikring. Elles har stolpen ingen elektronikk.
- Veggtapp: ein laus tapp Ø 8 mm utan straum følgjer med og blir skrudd i veggen. Holet på tvers gjer at tavla kan hengje der med lysflata ut eller inn mot veggen.
- Betjening: handa flyttar tavla mellom hola, og kvart hol har sitt kontaktpar og sitt tak. Hjulet set nivået under taket.

**Lys.** Lysande areal: 250 × 180 mm = 0,045 m² (450 cm²), lambertsk. L = Φ / (π · A) = Φ / 0,141. Tak: 70 lm = 495 cd/m², 200 lm = 1415 cd/m², 600 lm = 4244 cd/m² (skjult).

| Modus | Stilling | Lysstraum, effekt | Kvar lyset går | Luminans mot auget | Lux på målet |
| --- | --- | --- | --- | --- | --- |
| Stemning | Laus: står på ryggen, lena, lagd ned eller hengd | 30–70 lm, 0,5–1,1 W, 33–14 t per celle | Ut i rommet frå 13 cm høgd, eller mot ein vegg 10 cm bak | 212–495 cd/m². 0 når flata vender mot veggen | Vegg: 62 av 70 lm, synleg veggluminans opptil 100 cd/m². Ansikt på 0,6 m: 34–48 lx, nedanfrå |
| Møte | Står på tappen, leidning | 150–200 lm, 2,3–3,1 W | Rett fram frå augehøgd. Midt i flata 466 mm over bordet | 1061–1415 cd/m² | Ansikt: 113–155 lx ved 150 lm, 151–206 lx ved 200 lm |
| Arbeid | Ligg på tappen, lysflata ned 345 mm over bordet, leidning | 431–488 lm, 6,6–7,5 W | Ned på feltet. 26,5–27,8 % treffer feltet | 0 cd/m² når auget er meir enn 36 cm over bordet | Felt: 500 lx frå 431–453 lm. 538–565 lx ved 488 lm |

- Kontroll av møtetalet: E ≈ L · A / d² = 1061 × 0,045 / 0,58² = 142 lx.
- Arbeid ved lågare verknadsgrad: 60 lm/W gjev 450 lm og 496–522 lx. 55 lm/W gjev 412 lm og 455–478 lx.
- Jamnheit i arbeid: lågaste verdi er 0,19–0,31 av snittet.
- Melanopisk: 70 lm mot brukaren på 0,6 m gjev 34–48 lx ved auget, altså 15–21 lx melanopisk EDI med DER 0,44 (ANTAKING for 2700 K). Målet på 10 lx blir halde ved høgst om lag 35 lm mot brukaren, eller når flata vender mot veggen.

**Overgang.** Grip om ryggen, løft tavla av tappen, vend ho 90° og set det andre holet ned på tappen. Føreseiing: 3–4 sekund med éi hand. Hola har trakt, og ryggen er firkanta, så handa kjenner kva flate som vender ned. Frå arbeid til heim: løft tavla av og set ho frå deg på hylla. Då går ho over på cella, og taket fell til 70 lm og varm farge utan at hjulet blir rørt. Overgangen er ei flytting mellom to hol, ikkje ei trinnlaus rørsle.

**Form.**

- Tavle 260 × 200 × 8 mm, hjørneradius 30 mm på dei to frie hjørna. Lysande felt 250 × 180 mm.
- Rygg 30 × 30 × 260 mm langs den eine langsida. Tavla står i eit spor midt på den eine flata. Messinghjul Ø 26 × 14 mm i den eine enden, lok med myntspor i den andre.
- Laus står tavla på ryggen: 220 mm høg, midt i lysflata 132 mm over bordet.
- Stolpe: fotskive Ø 140 × 5 mm med ein boss Ø 30 × 12 mm, stamme Ø 10 mm, skulder 334 mm over bordet, tapp til 362 mm.
- Høgd på stolpen: 370 mm liggjande, 554 mm ståande. Liggjande kragar tavla 205 mm ut frå tappen og kan svingast rundt han.
- Vekt: tavle om lag 0,59 kg, stolpe om lag 0,60 kg, sum om lag 1,19 kg.

**Material.**

- Bakbrett: aluminium 0,8 mm, laserskore og knekt med tre flensar på 8 mm, pulverlakkert utvendig og kvit innvendig. Brettet er skrudd mot ryggen og er kjøleflate.
- Rygg: standard firkantrøyr i aluminium 30 × 30 × 1,5 mm, kappa og frest (spor og to hol), pulverlakkert i same farge.
- Lysleiar og front: PMMA frå plate, laserskore. Fronten er opal og ligg bak flensane på brettet.
- Hjul: dreia messing, ubehandla. Endelok: dreia aluminium.
- Skuff for elektronikk: PA12, printa i første seriar.
- Stolpe: stålrøyr og laserskoren fotskive i stål, pulverlakkert. Tapp: dreia rustfritt stål med isolerande hylser.
- Ingen delspesifikke verktøy utanom kretskort. Fargar som i frø 1.
- Kostnadsmål: 400–800 kr i produksjonskost, som i frø 1. Ikkje kalkulert.

**Reparasjon.**

- Batteri: endelok med kvart omdreiing og myntspor, 0 skruar. Cella glir ut. Føreseiing: under 30 sekund. Verktøy: mynt.
- Lysmodul: 2 skruar M3 Torx T10 i hjulenden, så glir heile skuffen ut. LED-lista sit i skuffen med 1 plugg. Føreseiing: under 5 minutt. Verktøy: T10.
- Tavla (bakbrett, lysleiar og front) kan bytast: 3 skruar gjennom ryggen.
- Heile lampa: 7 skruar av same type (2 i hjulenden, 3 gjennom ryggen, 2 under foten) og 1 bajonett. To verktøy: T10 og mynt.
- Ingen lim. Tavla lyser fullt på leidning utan celle når ho står på tappen.

**Northern.** Held H3 (opal front), H4 (éin matt farge over brett, rygg og stolpe), H5 (messinghjulet er einaste varme metallpunkt og er betjening) og H6 (tavla blir flytta: ho står, ligg og heng). Bøyer H1: kvar lekam har to primitiv, men silhuetten på stolpen har fire (tavle, rygg, linje, fotskive). Bøyer H2: linja ber ei flate, ikkje eit kompakt hovud. 4 av 6, altså under terskelen på 5 i K4. Rektangelet har presedens i Archive og i søyla på Balancer mini, men svermen er rund. Konseptet ligg lenger mot endring enn frø 1: det ville vore den første Northern-lampa der den lysande delen er laus frå foten. Balancer mini, som går frå vegg til bord, er næraste presedens.

**Naboar.**

- Nimbus Roxxane Leggera 52 CL (`02`): batteridriven arbeidslampe med flatt hovud, 25–800 lm, utskiftbar akkupakke i foten, magnetdokk som ladar, 1,15 kg, EUR 845. Skilnad: der er heile lampa den flyttbare delen. Her er flata heile lampa, og stolpen er berre høgd og leidning.
- Artemide Discovery (k, `00`): kantbelyst PMMA, 17 mm, pendel og vegg.
- Lume Cube Studio Panel og Edge Light Go (s, ikkje stadfesta: sidene gav 429 og 403 den 12.11.2026): kantbelyst panel med batteri for studio, og oppladbar skrivebordslampe.
- Lågprislamper med hovud som kan takast av og hengjast på vegg (s).
- Akrylplate i LED-sokkel, som skilt og nattlys: busett lågprisnabo (ikkje stadfesta, frå minnet).
- Logitech Litra Beam LX (s, `02`): nøkkellys mot brukaren og lys mot veggen bak, opptil 400 lm, kabel.
- NOX frå Studio Apure (sekundærkjelde, `00`): laust hovud med justerbar linse, 140 lm.
- Ingen er funnen der festepunktet vel både stilling og lysstraumtak. «Ikkje funnen» tyder ikkje «finst ikkje».

**Skissemodell.**

- Modell i full storleik, 2–3 timar: tavle av 5 mm kapa og 3 mm akryl, 260 × 200 mm. Rygg: trelist 30 × 30 × 260 mm med to hol på 8,5 mm, eitt i botnen og eitt tvers gjennom, og lodd til 0,30 kg. Stolpe: rundstål eller stokk Ø 10 mm med ein bolt Ø 8 mm som tapp, og fotskive med ballast til 0,60 kg.
- Lysmockup, 3–4 timar: lysleiarplata frå ein LCD-skjerm, kappa til 250 × 190 mm med blankpussa kant, reflektorarket bak og eitt diffusorark framfor. USB-lyslenke klemd mot kanten med ei aluminiumslist (forsøk 7 i `13`). Manglar plata: 3 mm klar akryl rubba med sandpapir, tettare lenger frå kanten. Straum frå powerbank når tavla er laus og frå USB-ladar når ho står på stolpen.
- Måling: verknadsgrad som lysstraum ut av flata delt på lysstraum frå naken list, begge målte som lux gonger areal på vegg. Lux i rutenett på bordet i hyllestilling. Lux ved ansiktet i skiltstilling. Jamnheit på flata frå foto. Tid og tal feilgrep når tre personar flyttar tavla frå skilt til hylle.

**Prøve.** Føreseiingane er skrivne før modellen er bygd.

1. Verknadsgrad. Føreseiing: minst 60 % av lysstraumen frå lista kjem ut av framsida. Med 108 lm/W inn frå LED og drivar (ANTAKING) er det 65 lm/W. Fell: under 51 %, altså 55 lm/W. Då gjev 7,5 W berre 412 lm og under 480 lx.
2. Arbeidslys. Føreseiing: 27–28 % av lysstraumen treffer feltet frå 345 mm høgd, og 488 lm gjev 538–565 lx. Lysflata er ikkje synleg frå augehøgd over 36 cm. Fell: under 25 % på feltet, for då gjev 488 lm under 500 lx.
3. Møte. Føreseiing: 150 lm gjev 113–155 lx loddrett på ansiktet ved 1061 cd/m². Fell: under 100 lx ved 1415 cd/m².
4. Overgang. Føreseiing: frå skilt til hylle på under 4 sekund med éi hand og høgst eitt feilgrep. Fell: over 6 sekund, eller at holet må finnast med to hender.
5. Kontakt. Føreseiing: ingen synlege blink når tavla blir dreidd på tappen, filma i sakte film. Fell: blink.
6. Reparasjon. Som i frø 1: celle på under 1 minutt, lysmodul på under 5 minutt.

**Sviktrom.**

Aksar konseptet ikkje held:

- Jamnheit på feltet: lågaste verdi er 0,19–0,31 av snittet. Referansen er 0,6.
- Lys på skjermen: 660–1040 lx på ein laptopskjerm når tavla ligg over laptopen. Rettesnora er under 215 lx.
- Overgangen er ei flytting på 3–4 sekund, ikkje trinnlaus.
- Arbeidslys og møtelys på celle finst ikkje. Taket laus er 70 lm, så region O2 i `00` blir ikkje nådd.
- Laus kjem ansiktslyset nedanfrå, 24–30° under auget.
- Vekt 1,19 kg, øvst i målet, med 0,59 kg øvst. Veltevinkel 12° liggjande og 18° ståande (rekna).
- Frå sofa er undersida synleg i arbeidsstilling: 3450–4240 cd/m².
- Formhypotesane: 4 av 6.

Dei tre største risikoane:

1. Lysleiaren. Verknadsgrad og jamnheit er ukjende. Under 55 lm/W held ikkje 500 lx på 7,5 W.
2. Tappen. 1,5 A går gjennom ein kontakt som blir dreidd og teken av og på dagleg. USB-C-kjelda må meldast vidare til tavla. Utan celle blinkar lyset om kontakten glepp.
3. To delar. Stolpen står att åleine og må forsvare plassen sin. Tavla er topptung, cella ligg i same profil som LED-lista, og framsida i akryl blir ripa når tavla står og ligg laus.

**Reknestykke.**

- Areal og luminans: 0,25 × 0,18 = 0,045 m². π · A = 0,141. Taket for 500 cd/m² er 71 lm, og for 1500 cd/m² 212 lm.
- Hylle, lysflata 345 mm over bordet (modell): 27,8 % på feltet i plassering A og 26,5 % i B. Punktformelen gjev 29,1 og 27,2 %. 120 lm på feltet krev 431 lm (A) og 453 lm (B).

| Verknadsgrad | Lysstraum ved 7,5 W | Snitt på feltet, A | Snitt på feltet, B |
| --- | --- | --- | --- |
| 55 lm/W | 412 lm | 478 lx | 455 lx |
| 60 lm/W | 450 lm | 522 lx | 496 lx |
| 65 lm/W | 488 lm | 565 lx | 538 lx |
| 80 lm/W | 600 lm | 696 lx | 662 lx |

- Høgare tapp gjev jamnare lys, men mindre på feltet: lysflata 395 mm over bordet gjev 23–24 % og krev 498–514 lm, altså 7,7–7,9 W ved 65 lm/W. Difor er tappen låg.
- Skilt, midt i flata 466 mm over bordet, 0,54 m frå ansiktet i A og 0,62 m i B (modell): 100 lm gjev 707 cd/m² og 75–103 lx. 150 lm gjev 1061 cd/m² og 113–155 lx. 200 lm gjev 1415 cd/m² og 151–206 lx.
- Laus mot vegg, 10 cm (modell): 70 lm gjev 62 lm på veggen, opptil 886 lx bak tavla og 450 lx (100 cd/m²) på den synlege delen av veggen.
- Brukstid ved 65 lm/W: 30 lm er 0,46 W og 32,7 t. 70 lm er 1,08 W og 14,0 t. 150 lm ville vore 2,31 W og 6,5 t.
- Varme: 7,5 W gjev 4,5–5,6 W varme. Rygg (312 cm²) og bakbrett (520 cm²) gjev 830 cm² og ΔT = 5–7 K. Ryggen åleine gjev 14–18 K, altså om lag 43 °C ved 25 °C i rommet, tett på ladegrensa til cella på 45 °C (`05`). Brettet må difor ha metallisk kontakt med ryggen.
- Vekt: lysleiar 25 × 19 × 0,2 × 1,18 = 112 g. Front 56 g. Bakbrett 26 × 20 × 0,08 × 2,7 = 112 g, flensar 10 g. Rygg (3² − 2,7²) × 26 × 2,7 = 120 g. Hjul og lok 40 g, celle 70 g, skuff og kort 50 g. Sum 570 g, med skruar og kontaktblokk om lag 0,59 kg. Stolpe: fotskive π × 7² × 0,4 × 7,85 = 483 g, stamme 71 g, boss og tapp 42 g.
- Velt: liggjande ligg tyngdepunktet 29 mm ut frå tappen og 189 mm oppe. tan θ = (70 − 29) / 189 gjev 12,4°. Ståande: 70 / 217 gjev 17,9°.

## Forkasta undervegs

Fire variantar innanfor linsa heldt ikkje då dei blei rekna.

1. **Frittståande flate utan stolpe** (kile, bok eller telt). Midten av flata ligg 13–20 cm over bordet, altså 24–30° under auget på 0,6 m, og flata kjem ikkje over feltet. Fell på møte og arbeid.
2. **Tosidig lysleiar** utan bakside. I liggjande stilling går halve lyset opp. 500 lm gjev 1768 cd/m² på oversida, som auget ser, og berre 250 lx på feltet. Fell på arbeid.
3. **Blad i fot som blir dreidd om loddrett akse**, med kanten mot brukaren i arbeid. Ei loddrett flate ved kanten av feltet legg 14 % av lyset på feltet einsidig og 7 % tosidig. 500 lx krev 1700 lm. Fell på arbeid.
4. **Bakteppe**: ei flate på 360 × 260 mm bak laptopen. Held ansiktslys ved stemningsluminans: 147 lm ved 500 cd/m² gjev 110 lx. Men ho er skjermutstyr på 36 × 26 cm og fungerer ikkje bak ein ekstern skjerm. Parkert, ikkje ført vidare.

## Kjelder for naboane

Kontrollerte 12.11.2026 (k):

- Nimbus Roxxane Fly, datablad DE 05/16: https://www.smow.de/pdf/nimbus-roxxane-fly-factsheet-de-en.pdf
- Circa (Haworth), forhandlarside: https://www.aristaint.com/en/product-technology/smart-lighting-circa?hsLang=en

Berre søkjetreff (s), ikkje stadfesta:

- Lume Cube Studio Panel (lumecube.com gav 429): https://lumecube.com/products/studio-panel
- Lume Cube Edge Light Go (adorama.com gav 403): https://www.adorama.com/lume-cube-edge-light-go-led-desk-lamp/p/lcedgegoslt
- Lågprislamper med avtakbart hovud: søkjetreff hos wayfair.co.uk og morningsave.com.

Marset Theia M, Artemide Discovery og NOX: sjå kjeldelista i `00`. Nimbus Roxxane Leggera 52 CL, Lume Cube Edge Light 2.0 og Logitech Litra Beam LX: sjå `02`. Northern: sjå `01`.
