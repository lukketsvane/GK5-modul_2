# Tre konsept til 17. november

Dato: 13.11.2026. Dei tre konsepta kjem frå seks formfamiliar med 18 kandidatar, rekna i lysmotoren og etterprøvde av ein skeptikar per familie. Kvart konsept brukar éin del av byggjesettet: bøygd plate og folie, fresnelplata og linsa med frontflatespegelen frå overheadprojektoren.

| | Grep | Byggjesett | Handling |
| --- | --- | --- | --- |
| **A Skiva** | Ei kjelde i foten lyser opp på ei bøygd spegelskive som vippar frå veggen bak skjermen ned på arbeidsfeltet. | folie på papp, bøygd over ein printa ribbe | vipp skiva |
| **B Over** | Fresnelplata ligg over skjermkanten og vippar lyset frå veggen bak skjermen ned på bordet. | fresnelplata, diffusorark, stolpen | vipp plata |
| **C Vindauge** | Ei linse teiknar eit vindauge av lys på veggen. Ein spegel glir inn i strålen og legg feltet på bordet, medan vindauget blir. | linse, maske, frontflatespegelen | skyv spegelen inn |

Arka: `ark-A-skiva.png`, `ark-B-over.png`, `ark-C-vindauge.png`. Tala: `tal.md`, rekna med `tre.py`.

## Tala

Same rom, same mannekeng, same watt: 1,25 W i stemning og 5 W i arbeid, skalert til 350 lx på feltet. Modell, ikkje måling.

| | A Skiva | B Over | C Vindauge |
| --- | --- | --- | --- |
| Watt for 350 lx på feltet (tak 7,5) | 2,14 | 1,73 | 3,80 |
| Timar per celle ved 350 lx | 7,1 | 8,7 | 4,0 |
| Jamnheit (referanse 0,6) | 0,60 | 0,47 | 0,24 |
| Mot auget ved 350 lx, auge 25 / 47 / 60 cm (F1 3000, F5 1500) | 83 / 83 / 83 | 227 / 75 / 75 | 821 / 128 / 128 |
| Veggen bak skjermen ved 350 lx (F6 100 til 150) | 14 | 16 | 72 |
| Skjermflata ved 350 lx (del av feltet) | 115 (0,33) | 79 (0,23) | 34 (0,10) |
| Stemning: mot auget (krav 500) | 83 | 200 | 125 |
| Stemning: veggen bak skjermen | 142 | 184 | 85 |
| Stemning: skjermflata | 142 | 4 | 5 |
| Likskap stemning og arbeid (over 0,9 er dimmar) | 0,23 | 0,05 | 0,35 |
| Største sprang langs overgangen | 0,13 | 0,36 | 0,06 |
| Skjermflata langs overgangen, lx | 142 · 266 · 350 · 332 · 268 | 4 · 108 · 262 · 246 · 229 | 5 · 9 · 16 · 27 · 45 |

Lyset på skjermflata blir samanlikna som del av feltet. Bru og krok frå formsøket i `northern-lampe/` ligg på om lag 1,2 til 1,3, prisma på 0,02.

## Kvar dei står

**A Skiva** er den jamnaste og enklaste: fot, stong og skive, som Northern. Jamnheita 0,60 er den einaste i alle seks familiane som når referansen, og ho held for all kuv spegel frå R 0,6 til 2,0 m. Mot: skiva vippar strålen over skjermen på veg ned (350 lx på skjermflata midt i overgangen), stemninga legg 142 lx på skjermflata, og veggen bak skjermen er mørk i arbeid. Næraste nabo er Verner Panton Reflect, som har fast, kvit skive.

**B Over** er den mest effektive og den reinaste overgangen: likskap 0,05, så lyset byter adresse heilt. Plata ligg over skjermkanten, så stemninga går over skjermen og ikkje på han (4 lx). Mot: overgangen hoppar (sprang 0,36), veggen bak skjermen er mørk i arbeid, og dioden på skjermkanten har lite margin. Brønnen må vere 50°: med 64° ser auget dioden frå 60 cm (140 000 cd/m²). Næraste nabo er BenQ ScreenBar Halo.

**C Vindauge** er den einaste som held veggen lys i arbeid og den einaste som ikkje sveipar over skjermen: spegelen deler strålen i staden for å flytte han (sprang 0,06, høgst 45 lx på skjermflata). Mot: maska i trakta stengjer lyset utanfor opninga, så berre 0,47 kjem gjennom (0,62 med trakta tilpassa), og watten blir 3,8. Jamnheita er 0,24, og auget i 25 cm ser 821 cd/m². Linsa på om lag 60 mm finst ikkje i byggjesettet. Ingen kjend lampe deler strålen slik.

## Det etterprøvinga fann

Ingen av dei 18 kandidatane held alle krava når augehøgda og antakingane blir varierte. Det er det viktigaste funnet.

1. **Lobebreidda avgjer F1.** Tala kviler på at satin har ei lobe på 10° og blank folie 2,5°. Folie på papp ligg truleg på 4 til 6°. Då ser auget i 25 cm 1600 til 9000 cd/m² frå spegelskivene. Lobebreidda må målast før noko blir bygd vidare.
2. **Vippe og skjere er overgang. Skyve, dreie og dimme er dimmar** (likskap 0,8 til 0,99).
3. **Å flytte strålen frå vegg til felt sveipar over skjermen** (500 til 2700 lx på skjermflata midt i overgangen). Å dele strålen gjer det ikkje.
4. **F6 held ingen i arbeid.** Veggsona er om lag 1 m² og feltet 0,24 m², så 100 lx på veggen kostar like mange lumen som 350 lx på feltet. Lyset landar dessutan ved sida av skjermen, ikkje bak han.
5. **Mjuk fald er gratis.** Éin eller to faldar med radius 40 til 80 mm kostar 2 til 7 % watt. Northern sitt «mjuk» kostar ikkje lys.
6. **Linsa på 285 mm høyrer heime frå 1,1 m kast:** hylle, golv eller tak. Kondensoren, ikkje linsa, avgjer verknadsgraden: 1 lm/W utan, 59 med fresnelplata.

Etterprøvingane ligg i `../reflektor/*/etterproving.md`.

## Første forsøk: mål lobebreidda

Dette avgjer om A og B held F1, og kva overflate C treng.

1. Mørkt rom. Telefonlykta 1 m frå prøva, lyset inn på 45°.
2. Eit kvitt kort d = 50 cm frå prøva i speglingsretninga.
3. Mål diameteren D der flekken på kortet er halvparten så lys som midten. Foto med låst eksponering gjer det enklare.
4. Lobebreidda σ i grader er om lag 24 · D / d. Modellen brukar 2,5° for blank folie (D = 5 cm) og 10° for satin (D = 21 cm).
5. Prøv folie på papp, frontflatespegelen, fresnelplata med eitt og to diffusorark, og bakepapir oppå folie.

## Skissemodellar

**A Skiva:** Folie på papp Ø 250 mm, limt utan krøll. Ein 3D-printa ribbe med boge R 1,2 m (pil 6,5 mm) teipa bak. Telefonlykta i ein svart papprull Ø 25 × 100 mm i foten, 5 cm over bordet. Stolpen frå overheadprojektoren held skiva 41 cm over bordet, 15 cm framfor skjermplanet. Føreseiing: lågaste rute delt på snittet over 0,5 med bøyen, under 0,45 flat.

**B Over:** Fresnelplata i ei pappramme med teiphengsel langs bakkanten. Stolpen klemt bak skjermen, ramma 20 cm over skjermkanten og 9 cm framfor skjermplanet. Telefonen på skjermkanten med lykta opp i ein brønn av svart papp, 12 cm under plata. Eitt og to diffusorark teipa på plata. Føreseiing: jamnheit 0,46 (0,35 til 0,55) med ark, under 0,05 utan.

**C Vindauge:** Ei lupe eller ei vassfylt glaskule på Ø 70 mm (f om lag 70 mm) som linse. Maska i papp, trakt av folie, frontflatespegelen på eit papphengsel rett etter linsa. Føreseiing: vindauget står i ro på veggen medan feltet kjem fram, og lyset på skjermen er under 0,15 av feltet langs heile vegen.

## Avgrensingar

- Alle tal er modell. Kjelda er telefonlykta i modellane, ikkje produktet.
- Mannekengen frå `modell/polge.py` er ryggfigur. Han endrar ikkje tala for lampa.
- C er retta med faktor 0,47 for maska i trakta. Linsa er rekna som tynn linse.
- Spegling i skjermen og i blank bordflate er ikkje rekna for arka.
