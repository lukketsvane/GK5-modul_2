# Funn: familien overgang

Korleis éi lampe går frå stemning (1,25 W, 2200 K) til arbeid (5 W, 3000 K). Same rom, same watt og same tal for alle (`lysskisse.py`). Kroppen er enkel: flatt satinert ark, fald, klipt skive, fresnelplate og strøk. Mekanismen varierer. 47 mekanismar over tre generasjonar, kvar gått i sju steg med `overgang(g, n=7)`. Tala er modell, ikkje måling. Alle tal: `tal.md`, `tal.csv`, `overgang.csv`, `journal-gen*.jsonl`. Arbeidslogg: `notat.md`.

## 1 Kva eg varierte, og kva som stivna

- **Gen. 1 (21):** mekanismen i fast oppstilling (foten til høgre, kjelda lyser opp på eit ark 41 cm over bordet): vippe, vende, skyve kjelda, bøye, dreie, heve, dreie foten, flytte, kryssdimme, fald, fresnel og spegel. Det som berre gjer strålen breiare (skyv, boy-sym, hev), er dimmarar (likskap 0,86 til 0,99). Seks av sju verkelege overgangar sveipa strålen 36 grader frå veggen til feltet, over framsida av skjermen (500 til 2700 lx på skjermflata midt i overgangen). Stivna rundt sveipet.
- **Gen. 2 (14):** fordele i staden for å sveipe. Kjelda lyser mot veggen, arket blir skove, dreidd eller vridd inn i strålen. Saumlaust og utan skjermlys, men settet delte seg: likskap under 0,3 gav 26 til 55 lx på veggen i arbeid, og dei som heldt F6 (122 til 128 lx) fekk likskap 0,67 til 0,77. Stivna rundt adressa «veggen nær skjermen» i stemning.
- **Gen. 3 (12):** stemninga flyttar adresse (tak, høg vegg, bord), arbeidet er felt + veggstrøk. Svarte det opne spørsmålet: ja, med kryssdimming. Nei, med alle mekaniske sveip.

## 2 Dei tre beste

| | Parametrar | Topp | Sprang | Jamn auke | Likskap | W350 | Felt / vegg i arbeid, lx | Mot auget, stemning / arbeid, cd/m² | Skjermflata maks undervegs, lx |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **kryss-hog** | to strøk og eitt ark, éin knapp. Stemning: vifte frå toppen av lampa (57 cm) mot veggen 115 cm over bordet. Arbeid: 57 % av watten på arket mot feltet, 43 % på ein veggvaskar | 0,66 | 0,04 | 1,00 | 0,28 | 4,46 | 393 / 126 | 148 / 555 | 66 |
| **skjer** | oppstilling B: fot framme til høgre, strålen mot veggen ved skjermkanten. Satinert ark, 25 cm, blir skove 27 cm inn i strålen i sitt eige plan | 0,79 | 0,15 | 1,00 | 0,08 | 2,25 | 779 / 29 | 173 / 1338 | 114 |
| **drei-snigel** | oppstilling B. Skive 36 cm med spiralkant, dreidd 180 grader i sitt eige plan, 9 cm frå strålen | 0,80 | 0,11 | 1,00 | 0,20 | 2,05 | 852 / 55 | 279 / 2311 | 132 |

- **kryss-hog:** den einaste som er ein verkeleg overgang (likskap 0,28) og held 100 til 150 lx på veggen i arbeid, utan blending undervegs og utan å lyse på skjermen, men forma fortel ingenting om kva knappen gjer.
- **skjer:** den reinaste overgangen per watt (likskap 0,08, W350 2,25), og handlinga syner seg: ei plate som blir skoven inn i ein stråle, men arbeidet manglar veggstrøket.
- **drei-snigel:** spiralkanten gjer dreiinga mjuk (sprang 0,11 mot 0,30 for rett kant i drei-b) og er den mest effektive (W350 2,05), men satinflata står på 2311 cd/m² mot auget i arbeid, over F5 (1500).

## 3 Det som velta og det som ikkje kan lagast

- **VELT** vipp-ansikt (gen. 1): stemning som ansiktslys gjev 20 771 cd/m² mot auget. Skjer-matt (gen. 2): matt ark i staden for satin, 7583 cd/m² og W350 8,71. Glod-kryss (gen. 3): naken glødeperle i stemning, 17 590 cd/m², bryt R3. Topp er berre 1,06, fordi blendinga ligg i eit endepunkt.
- **UMOGLEG** skål (gen. 1, strekk 6,5 %), skjer-kuppel (gen. 2, 11,6 %) og fald-kuppel (gen. 3, 30,5 %). Arket må tøyast, så det kan ikkje bøyast fram. Fald-kuppel gjev dessutan 5604 cd/m² i arbeid.
- **Farlege mellomsteg (strålen i auget):** vend-a 8441 cd/m² ved t = 0,83 (topp 6,11), spjeld-tak 6690 ved t = 0,67 (topp 5,0), drei-to topp 1,94, hev 1,13, fresnel-skjer 1,10.

## 4 Funn som gjeld meir enn denne familien

1. **Likskap og veggkrav kolliderer i geometrien, ikkje i mekanismen.** Veggsona er om lag 1 m², feltet 0,24 m². 100 lx på veggen er om lag like mange lumen som 350 lx på feltet. Bur stemninga på veggen nær skjermen, blir likskapen 0,6 eller meir for alle lamper som held F6. Ein verkeleg overgang med veggstrøk krev at stemninga flyttar seg dit arbeidet ikkje lyser: høgt på veggen eller i taket.
2. **Mellom to adresser ligg det som er farleg.** Ein stråle som blir flytt frå A til B, lyser på alt imellom. Frå veggen eller taket ned til feltet ligg skjermen (fald og vipp: 520 til 850 lx på skjermflata midt i overgangen, mot under 125 i endepunkta) eller auget (spjeld-tak: 6690 cd/m²). Saumlaus utan sveip får ein berre ved å dele strålen (skjer, drei, kryss), ikkje ved å flytte han.
3. **Sprang følgjer kor mykje av strålen eitt steg flyttar.** Rett kant over ein smal stråle gjev hopp (drei-b 0,30, fresnel-skjer 0,31, spegel-vipp 0,37). Spiralkant eller brei stråle gjev mjuk gang (drei-snigel 0,11, vipp 0,08). Mjukheita kan teiknast i klippekanten.
4. **Topp åleine er eit dårleg blendevarsel.** Det er relativt til endepunkta, så blending i stemning (glod-kryss) eller i arbeid gjer at topp ser trygg ut. Les auget steg for steg.
5. **Taket er ei usynleg stemning frå stolen.** 10 cd/m² mot auget og 3 lx på veggsona. Høg vegg gjev same arbeid og 148 cd/m², synleg over skjermen.

## 5 Føreseiingar til skissemodellen (sette 13.11, før måling)

Måla med lux-app på telefon. Tala er forhold, så lumen i lykta fell bort.

1. **skjer:** feltet aukar seint: ved halv slaglengd har feltet under 25 % av sluttverdien (modell 175 av 779 lx), og veggen stig først (60 til 92 lx ved t = 0,5) før han fell til under 35 % av toppen (29 lx) i arbeid.
2. **skjer:** lux på framsida av skjermen held seg under 15 % av feltet i arbeid i alle steg (modell 114 av 779).
3. **kryss-hog:** forholdet felt / vegg i arbeid blir mellom 2,5 og 4 (modell 3,1). I stemning les luxmåleren på veggsona under 10 % av det same punktet i arbeid (modell 6 av 126).
4. **drei-snigel:** arket er det lysaste i synsfeltet i arbeid, minst 4 gonger lysare enn lysaste romflate (modell 2311 mot 508 cd/m²). Ein diffusor oppå tek det under 1500 og senkar feltet med under 30 %.
5. **Alle tre:** overgangen tek under 3 s med éi hand, og ingen observatør seier «det blinka» undervegs.

## 6 Oppskrift: éin rigg som prøver alle tre, under éin dag

1. Bordrigg som i rommet: papp-skjerm 54 x 31 cm 45 cm frå veggen, kvit vegg bak, auge-merke 47 cm over bordet og 60 cm frå skjermen.
2. Fot (3D-print eller papp) framme til høgre (x 62, y 22 cm frå midten av bordkanten). Telefonlykt i eit pappør (brønn, 6 cm djupt) retta bakover og opp mot veggen 17 cm til høgre for skjermkanten, 80 cm over bordet.
3. **skjer:** tynn plate 25 x 25 cm med aluminiumsfolie, matt side ut (satin), og eitt prismeark eller diffusorark oppå om flata blendar. Plata går i eit pappspor 37 cm opp langs strålen og blir skoven 27 cm inn. Vinkelen held spegelbiletet mot feltet: still han med lykta på, med ein papplapp på feltet.
4. **drei-snigel:** klipp ei skive 36 cm av same plate med spiralkant (radius frå 1 til 17 cm over ein halv runde), nål i midten 9 cm frå strålen, dreiast 180 grader.
5. **kryss-hog:** to lykter til. Den eine på toppen av ein stolpe (stolpen med ledd frå overheadprojektoren, 57 cm) med folieskjerm som vifter mot veggen over skjermen. Den andre under eit fast satinark mot feltet, og ei vifte mot veggen bak skjermen. Ein papp-spjeld med kileforma opning framfor kvar lykt, kopla med tråd til éin spak: når den eine opnar, lukkar den andre. Ingen stråle flyttar seg, berre opninga.
6. Mål felt (midten), vegg (bak skjermen), skjermframside og luminans mot auget (foto frå auge-merket med låst eksponering) i fem steg: 0, 0,25, 0,5, 0,75 og 1. Fresnelplata skal ikkje i sola, og halogenpæra blir ikkje brukt.

## 7 Usikkert, og det modellen ikkje reknar

- SATIN (0,65 i ei lobe på 10 grader) og 2 % sprut er antakingar. Luminansen mot auget for skjer og drei står og fell med lobebreidda.
- Spegling av arket i dataskjermen er ikkje rekna. Skjermlux er rekna med eigen `skjermlux()`, ikkje målt.
- Rommet er svart utanom vegg og tak. Taket som stemning er truleg undervurdert: i eit verkeleg rom fyller det rommet. Kryss-hog og kryss-tak kan byte plass i eit kvitt rom.
- Kryss-hog brukar strøk rett ut (80 lm/W), så W350 4,46 er ein kostnad, ikkje ein feil. 5 W gjev 393 lx, nær kravet.
- To ark på éi kjelde: motoren trekkjer berre det siste arket frå kjelda (`k.lm_ut` blir overskriven i `Ark.__init__`). Eg rettar for hand i fald3, ring, drei-to og fald-kuppel. Lysfordelinga kan gå over 1 (tak 1,07 for fald-kuppel ved t = 0) når eit holt ark samlar lyset i ei flekk på det grove taknettet.
- Kryss og kryss-43 i gen. 1 og 2 manglar arket i stemningssteget. Retta i gen. 3, ikkje køyrt på nytt.
- Kva handling ein les av forma, er skjønn, ikkje rekna: skjer (plata inn i strålen) og vipp les seg sjølv. Drei-snigel les som ein knapp. Kryss-hog les som ein dimmar og fortel ikkje at lyset byter adresse.
