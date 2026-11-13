# Funn: familien KLIPP (omriss og opningar)

Dato 13.11.2026. Modell, ikkje måling. Tala står i `tal.md`, `tal.csv` og `klipp-tal.md` (produksjon, rørsle). Journal i `notat.md`. Same watt for alle: 1,25 W i stemning, 5 W i arbeid. Oppstilling «fram»: kjelda i foten (x 0,47, y 0,15, 5 cm over bordet) lyser bakover og opp på ei skive Ø 25 cm i satin med senter 33 cm over bordet ved y 0,40. Det som er klipt bort, slepper strålen vidare mot veggen bak skjermen.

## 1 Kva eg varierte, og kva som stivna

- **Generasjon 0, oppstillinga** (`gen0_*.py`). Med kjelda rett under arket (malen) går alt gjennom klippet til taket: ring med hol Ø 12 cm gav vegg 26 lx. Med kjelda 25 cm framfor arket gav same ring 89 til 187 lx på veggen. Kjelda er delt i tre punkt fordi eitt punkt gav støy (sjå 7).
- **Generasjon 1, identiteten til klippet** (`gen1/`). 15 klipp på same skive: ring, halvmåne, halv, blad, stripe, sektor, hol, gradert hol, slissar, bogar, spiral, frynser, tunge, lamellar. Stivna i overgangen: likskap 1,00 for alle. Klippet endrar kor mykje, ikkje kva. Byta grep til rørsla.
- **Generasjon 2, identiteten til rørsla** (siste, `familie.py`). 14 handlingar: dreie ei klipt skive, dreie to halve lag, skyve ei lita skive over eit hol, vippe (med og utan hol), skyve bladet langs stonga, opne ei luke, vri lamellar, skyve to holark, dreie to vifter, og fresnelplata med og utan papirmaske, og projeksjonslinsa bak holet. Stivna: alt som berre endrar opninga (dreie, skyve lag, vifte, maske) er framleis dimmar, likskap 0,88 til 1,00. Unntaket er halv-drei (0,81), som slepper nesten heile strålen til veggen (vegg/felt 1,15). Vipp, skyv langs stonga og flikar flyttar lyset (0,37 til 0,79).

## 2 Dei tre beste

| | ring-vipp | maane-drei | luke |
| --- | --- | --- | --- |
| Parametrar | hol Ø 10 cm midt i skiva, skiva vippar så speglinga går frå veggen (45 cm over bordet) til feltmidten | bit med radius 8,5 cm, sentrum 7,5 cm under midten, strålen siktar 4 cm ned, skiva dreier 110° | rund luke 11 × 11 cm, hengsle 5,5 cm under midten, opnar frå 80° til 25° mot kjelda |
| W for 350 lx | 4,44 | 4,60 | 4,24 |
| Felt ved 5 W, lx | 394 | 381 | 413 |
| Jamnheit | 0,42 | 0,21 | 0,38 |
| Vegg ved 5 W, lx (vegg/felt) | 117 (0,30) | 138 (0,36) | 59 (0,14) |
| Mot auget, cd/m² (ved 350 lx) | 779 (693) | 940 (864) | 1047 (887) |
| Stemning: auge, felt, vegg | 169, 11, 63 | 171, 58, 56 | 191, 89, 31 |
| Likskap | 0,78 | 0,90 | 0,74 |
| Overgang: topp, sprang | 0,72, 0,04 | 0,67, 0,02 | 0,52, 0,10 |
| Skjermflata, lx (del av felt) | 50 (0,13) | 44 (0,12) | 56 (0,13) |
| Open del, kant/omkrins, velt | 16 %, 1,4, 2,1 | 37 %, 1,2, 2,6 | 22 %, 1,5, 2,2 |

- **ring-vipp:** klippet er veggstrøket og vippen er overgangen, så éi skive gjev 350 lx på feltet og 104 lx på veggen ved 4,4 W og låner stemninga frå veggen (felt 11 lx, vegg 63 lx). Den einaste som held F3, F6 og overgang saman.
- **maane-drei:** halvmånen held F6 best (127 lx på veggen ved 350 lx), men dreiinga flyttar for lite lys til å vere meir enn ein dimmar (likskap 0,90), og jamnheita er 0,21.
- **luke:** klipp pluss bøy gjev den mjukaste overgangen (topp 0,52) og lyset flyttar seg (0,74), men flika skuggar sitt eige hol, så veggen får berre 50 lx ved 350 lx på feltet.

Alle tre har strekk 0, eitt stykke og minste bru over 12 mm. Ingen når jamnheit 0,6.

## 3 Det som velta og det som ikkje kan lagast

- **Velta, generasjon 2:** VELT-sveip vender skiva frå veggen til feltet om ansiktet. Endepunkta er gode (felt 665 lx, auge 923), men midt i overgangen er skiva 36 282 cd/m² mot auget (topp 39). Endepunkta seier ingenting om vegen.
- **Velta, generasjon 1:** VELT-auge, hol mot auget, 1,8 millionar cd/m².
- **Kan ikkje lagast:** UMOGL-kuppel, holark pressa til kuppel, strekk 31 % (grensa er 0,6 %). UMOGL-ringar i generasjon 1: konsentriske ringar utan bruer fell i 3 delar.

## 4 Funn som gjeld meir enn denne familien

1. **Oppstillinga avgjer adressa, ikkje klippet.** Same ring gav 26 lx på veggen med kjelda under arket og 89 til 187 lx med kjelda framfor. Eit klipp er eit veggstrøk berre når veggen ligg i forlenginga av strålen.
2. **Mønsteret er lysmessig nesten likegyldig.** Alle 13 klipp i generasjon 1 treng 4,1 til 5,0 W for 350 lx på feltet og 100 lx på veggen, heil skive 11,4 W. Då står formreglane fritt: éi rund opning (kant/omkrins 1,1 til 1,5, 0 til 1 hol) i staden for rist (3,0 til 4,4, 4 til 38 hol). Mjuk og enkel kostar ingen lux.
3. **Ei rørsle som endrar kor mykje, er ein dimmar. Ei rørsle som endrar kvar, er ein overgang.** Dreie og skyve lag: likskap 0,81 til 0,93. Vippe: 0,37 og 0,78. Klipp og vipp er to fridomsgrader: klippet set veggstrøket, vippen set overgangen.
4. **Ei flik som blir bøygd mot kjelda, stel sitt eige hol.** Tunge: vegg 43 lx mot 44 for heil skive. Luke: vegg/felt 0,14. Klipp pluss bøy flyttar lyset, men ikkje til veggen.
5. **Fresnelplata samlar for godt til arbeidslys.** Rein plate: jamnheit 0,01 og 1083 lx i ein flekk. Ho treng diffusorark eller ein annan avstand før ho kan vere eit felt.

## 5 Føreseiingar til skissemodellen (sette før måling)

Same telefonlykt i alle stillingar. Lux på feltet er snittet av fem punkt, lux på veggen snittet av ti punkt jamt over veggsona (1,4 × 0,7 m rundt skjermen, 8 til 78 cm over bordet), slik modellen reknar. Foto frå stolen med låst eksponering.

- **P1:** ring-vipp i arbeidsstilling gjev vegg/felt mellom 0,20 og 0,45 (modell 0,30). Same oppstilling med heil skive gjev under 0,12 (modell 0,06).
- **P2:** Vipp ring-vipp frå arbeid til stemning utan å endre lykta: feltet fell til under 0,2 av arbeidsnivået (modell 0,11), og veggen blir minst 1,5 gonger lysare (modell 2,2).
- **P3:** Dreiinga i maane-drei aukar feltet med minst 1,3 gonger ved same lykt (modell 1,6), og veggen fell med 20 til 50 % (modell 38 %).
- **P4:** luke i arbeidsstilling gjev vegg/felt under 0,2 (modell 0,14).

Fell P1 under 0,2, spreier lykta meir enn modellen (10°), og holet må bli større eller kjelda smalare.

## 6 Oppskrift på skissemodell (under éin dag)

1. Tre skiver Ø 25 cm i tynn plate eller papp med aluminiumsfolie (matt side ut) og eitt diffusorark frå LCD-en oppå som satin. Ring: hol Ø 10 cm i midten. Måne: klipp bort ein sirkel med radius 8,5 cm, sentrum 7,5 cm frå midten. Luke: skjer ein U på 11 × 11 cm med rund topp, hengsle 5,5 cm under midten, og bøy luka ut.
2. Stolpen med ledd frå overheadprojektoren held skiva 33 cm over bordet, til høgre for skjermen og 5 cm framfor skjermplanet. Dreietapp i midten av skiva (skrue med to skiver) for måne-dreiinga.
3. Kjelde: telefonlykta 5 cm over bordet, 25 cm framfor skiva, i eit printa eller rulla papprøyr på Ø 4 cm og om lag 8 cm lengd, så strålen blir om lag ±14°. Sikt på midten av skiva.
4. Merk to stillingar på leddet: arbeid (speglinga midt på feltet) og stemning (speglinga på veggen 45 cm over bordet). For luka: binders som stopp på 25° og 80°.
5. Mål med ein annan telefon: lux på feltet og veggen i begge stillingar, og foto frå stolen. Halogenpæra blir ikkje brukt, og fresnelplata står ikkje i sollys.

## 7 Usikkert, og det modellen ikkje reknar

- **Feil i motoren (meldt):** (a) Når fleire ark deler kjelde, skriv kvart ark over `lm_ut` på kjelda med sitt eige tap, så spillet blir talt fleire gonger. Omgått med `_bokfor` i `familie.py`. (b) Eit ark der alt er klipt bort, krasjar (tom `Nett`) i staden for å gje null. (c) Ei punktkjelde gjev striper bak klipte mønster: same slissar med ulik fase gav vegg 79 til 220 lx. Omgått med tre kjeldepunkt over Ø 4 cm (då 90 til 130 lx).
- Motoren blei endra kl. 10.33 (nytt tal for skjermflata). Generasjon 1 er rekna før, generasjon 2 og tal.md etter.
- **Biletet mot talet:** bretta viser at klippet lyser veggen til høgre for og over skjermen (strålen held fram til om lag x 0,47 og 67 cm over bordet), ikkje rundt skjermen. Talet «vegg» er snittet over heile veggsona (1,4 × 0,7 m) og skjuler at veggstrøket er ein flekk. Skal flekken bak skjermen, må kjelda stå lenger til høgre og strålen gå skrått mot venstre (oppstillinga «skra» frå generasjon 0, ikkje køyrd i generasjon 2).
- Flekkanten er hakkete i biletet fordi klippet blir rekna på fliser. Ei kjelde på Ø 4 cm, 37 cm frå skiva og 45 cm frå skiva til veggen, gjev om lag 5 cm halvskugge i røynda.
- Klippet blir rekna på fliser om lag 1,25 cm (n = 20). Hol under 2 cm og slissar blir grove i lyset, medan produksjonstala er rekna på 0,5 mm.
- Arket skuggar ikkje seg sjølv. Spegling av skiva i dataskjermen er ikkje rekna. SATIN og 2 % sprut er antakingar.
- Linsa bak holet (ring-linse) slepper 80 % (ANTAKING). Velt er ein enkel momentsum med fot 0,85 kg.
- Telefonlykta har breiare stråle og høgare luminans enn kjelda i modellen. Kva eit rør gjev, er ikkje målt.
- Kombinasjonen ring og luke (holet held veggen, luka gjev overgangen) er ikkje rekna. Det er neste steg.
