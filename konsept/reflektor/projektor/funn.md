# Projektor: funn etter fire generasjonar

Familien: ei maske blir avbilda som ei form av lys. Motoren reknar ikkje linser, så strålegangen (tynn linse, uskarpskive, verknadsgrad ledd for ledd) står i `familie.py`. Same watt på alle: 1,25 W i stemning, 5 W i arbeid. Tala under er frå `tal.md` (G4) og `g4/overgang.md`.

## 1 Kva eg varierte, og kva som stivna

- **G1, staden** (11 grep, `g1/`): same sol og iris, linsa 285 på ni stader. Linsa verkar berre der kastet er over 4f = 1,14 m: tak (1,40 m), golv (1,45 m), vegg høgt. På bordet og bak skjermen (0,56 til 0,61 m) gjev ho uendeleg fokus eller ei maske på 0,53 m. Utan kondensor går 1 % av lyset gjennom (sin² av halvvinkelen: 0,0096), med fresnelplata som kondensor 55 til 62 lm/W.
- **G2, optikken** (13 grep, `g2/`): same stad, maske og vipp. Kort linse 41 til 60 mm, skuggemaske, glaskule, fresnelplata som avbildar, og trakt av spegelark som kondensor. Trakta løfte verknadsgraden frå 31 til 76 lm/W. Brennvidda åleine (41 mot 60 mm) endra ingenting: tala stivna, og eg bytte grep frå optikk til form og organ.
- **G3, forma og organet** (17 grep, `g3/`): sol, vindauge, horisont; vipp, iris, blad, delt spegel, fokus. Iris og blad vart dimmarar (likskap 1,00 og 0,99). Horisonten øydela feltet (jamnheit 0,01).
- **G4, avgjerda** (15 grep): fire opne spørsmål. (a) Kva kostar jamnheit under mjuk kant? (b) Kor stor del skal spegelen ta? (c) Kan linsa 285 vere éin av dei tre? (d) Sveipar vippen over skjermen? Eigen feil retta før køyringa: den graderte maska følgde siktet og ikkje maskeplanet (sjå 7).

## 2 Dei tre beste

| | dele-vindauge | golv-dele | zoom |
| --- | --- | --- | --- |
| Optikk | 60 mm linse, spegeltrakt, maske 63 mm | linsa 285, fresnelplata, maske 115 mm | 60 mm linse, spegeltrakt, sol Ø 40 mm |
| Parametrar | u 51 mm (16 mm innanfor fokus), spegel tek q = 0,75 | 1,45 m kast, u 241 mm (skarp ved 355), q = 0,75 | u frå 67 til 42 mm, fast sikte |
| Felt, lx / jamnheit | 981 / 0,24 | 382 / 0,58 | 956 / 0,36 |
| W for 350 lx | 1,78 | 4,58 | 1,83 |
| Vegg arbeid / stemning, lx | 106 / 91 | 43 / 37 | 18 / 5 |
| Mot auget arbeid / stemning, cd/m² | 358 / 265 | 169 / 62 | 324 / 167 |
| Likskap / sprang / topp | 0,35 / 0,06 / 0,93 | 0,37 / 0,07 / 0,53 | 0,94 / 0,01 / 0,87 |
| Skjermflata / felt | 0,10 | 0,08 | 0,18 |
| Kant arbeid, mm / hovud, mm | 73 / 121 x 75 | 63 / 600 x 285 | 123 / 137 x 53 |

- **dele-vindauge**: frontflatespegelen glid inn i strålen og deler han, så vindauget på veggen blir verande medan feltet veks fram på bordet, og det er den einaste som held F6 (100 til 150 lx på veggen) i arbeid.
- **golv-dele**: linsa 285 der ho verkar, på ei hylle 1,45 m unna bak høgre skulder, og den einaste med jamnheit nær 0,6 under mjuk kant, men ho er inga bordlampe.
- **zoom**: éin ring flyttar maska mot linsa, så ein skarp lysmynt på bordet (kant 13 mm) blir eit stort, mjukt felt (kant 123 mm), utan noko som rører seg i rommet.

Nest: vipp-vindauge (W350 1,22, best lysnytte), men vippen sveipar feltet over skjermen (36 lm på skjermen midt i overgangen, sprang 0,35) og veggen får 23 lx i arbeid.

## 3 Det som velta og det som ikkje kan lagast

- **Veltar, linse285-bord**: linsa 285 i bordlampa gjev 547 lx og jamnheit 0,28, men hovudet blir 545 x 366 mm og maska 354 mm, større enn plata (285). Bryt K2 (Ø 16 x 27,5 cm) og F9 (200 cm²).
- **Veltar etter (a), dele-fyll**: overfylling 5 cm og gradert maske gjev jamnheit 0,53, men W350 5,87: over budsjettet på 5 W (F3).
- **Kan ikkje lagast, onske-kort**: skarp sol på veggen frå eit hovud på 14 cm med linsa 285. u = 140 mm er innanfor f, biletet er virtuelt (v' = -0,28 m), og ingen skarp kant finst. Rekna med påtvinga kant 4 mm: felt 34 lx, vegg 315 lx. Fysikken forbyr det, ikkje motoren.

## 4 Funn som gjeld meir enn denne familien

1. **Brennvidda er kastet delt på (1 + m).** Ei bordlampe med 0,61 m kast og maske 60 mm (m = 10) treng f om lag 55 mm. Linsa 285 høyrer heime frå 1,1 m og ut: hylle, golv, tak.
2. **Kondensoren avgjer verknadsgraden, ikkje linsa.** Same linse: 1,0 lm/W utan kondensor, 59 med fresnelplata, 76 med spegeltrakt. Lysnytta på feltet spenner frå 2 til 98 % ved same watt.
3. **Jamnheit kjem av kastet, ikkje av maska.** Mjuk kant på 6 cm et hjørnerutene: 0,24 på 0,6 m kast. Gråfilter og overfylling gjev 0,53, men kostar 59 til 70 % av lyset. På 1,45 m gjev same kant 0,57 gratis (563 mot 571 lx for skarp).
4. **Ein overgang som deler, er saumlaus. Ein overgang som flyttar, sveipar.** Delt spegel: sprang 0,04 til 0,07 og 0 til 13 lm på skjermen. Vipp: sprang 0,35 til 0,57 og opp til 51 lm på skjermen midt i overgangen.
5. **Éi maske tener begge modusane, så arbeidsfeltet bestemmer forma.** Sol og vindauge gjev same vegg i stemning (90 og 91 lx). Horisonten gjev jamnheit 0,01 på bordet. Stemninga ligg i kanten og i adressa, ikkje i omrisset. Brettet viser det: maska er trapeskorrigert for bordet, så på veggen blir «vindauget» ein kile (dele-vindauge) eller ein rombe (golv-dele). Eit ekte vindauge på veggen krev ei eiga maske.

## 5 Føreseiingar til skissemodellen (sette før måling)

Modellen er golv-dele bygd av byggjesettet (sjå 6). Lux skal målast med same lykt og same rom før og etter.
- P1: skarpt bilete på bordet 1,45 m unna når linsa står 355 mm frå plata. Forstørring 4,1.
- P2: med linsa 241 mm frå plata blir biletet 6,0 gonger maska, og kanten blir 6 cm (10 til 90 %). Maska for feltet 0,6 x 0,4 m er eit skeivt trapes: framkant 91 mm, bakkant 82 mm, sider 53 og 60 mm.
- P3: jamnheit på feltet 0,58 i 10 cm ruter med mjuk kant, 0,64 med skarp. Lux i snitt fell berre 1 % frå skarp til mjuk.
- P4: utan fresnelplata, med lykta rett mot linsa, fell lyset på feltet til om lag 1/50.
- P5: spegelen inn i 3/4 av strålen: vegg delt på felt blir 0,11. Ingenting lys på skjermen under overgangen.

## 6 Oppskrift: skissemodell på under éin dag

1. Hylle eller krakk med toppen 0,95 m over bordplata, 0,75 m til høgre for og 0,8 m bak midten av arbeidsfeltet.
2. Fresnelplata på høgkant på hylla, vend mot bordet og vippa 10 til 15° så refleksen går til linsa. Telefonlykta i eit papprøyr ved sida av linsa, 0,60 m frå plata. Aldri halogenpæra, aldri plata i sola.
3. Maska: papp med trapesopninga frå P2 teipa rett på plata. Drei ho til hjørna treffer feltet. Bruk ikkje diffusorark: det øydelegg kondensoren.
4. Projeksjonslinsa på stolpen med ledd, 241 mm frå plata. Mål først skarpt ved 355 mm (P1), så mjukt ved 241 (P2).
5. Frontflatespegelen på eit papphengsel rett etter linsa. Utan spegel går strålen til veggen over skjermen. Spegelen inn: 3/4 går ned på feltet.
6. Mål lux i rutenett på 10 cm, kantbreidd med linjal, lux på veggen i fem punkt. Ta bilete frå stolen med låst eksponering.
Den kompakte dele-vindauge og zoom treng ei linse på om lag 60 mm som ikkje er i byggjesettet. Ei rund vassfylt glaskule på Ø 70 mm (f om lag 70 mm frå midten) eller ei lupe kan prøve prinsippet.

## 7 Usikkert, og det modellen ikkje reknar

- Diameteren 70 mm på linsa er ANTAKING. Det er òg 0,92 for linsa, 0,85 for kondensor og feltlinse, 0,90 for spegelen og 3 cm uskarpleik per meter for ei enkel linse på ±34°.
- Spegeltrakta er rekna med Monte Carlo og ei ideell feltlinse. LED-en må vere 5 mm og 5 W, altså om lag 1e7 cd/m². Det er ikkje prøvd.
- Kanten er ein logistisk modell av uskarpskiva. Fargekantar frå fresnelplata og linsa er ikkje rekna.
- Kjelda over plata er klipt til 0,60 m. Ideelt står ho 0,84 m unna for u = 241 mm. Hovudet i golv-dele blir stort.
- Spegling i dataskjermen og blank bordplate er ikkje rekna. Det er heller ikkje kor lenge auget ser inn i linsa (opninga lyser når ein ser langs strålen).
- Motoren reknar ikkje linser. All optikk er sett inn som lumen og maskefunksjon i `straale`. Eigen feil: G2 sin kort60-jamn har gråfilter som følgjer siktet. G4 brukar `gradert()`, som held filteret fast i maskeplanet.
- Eg fann ingen feil i `lysskisse.py`.
