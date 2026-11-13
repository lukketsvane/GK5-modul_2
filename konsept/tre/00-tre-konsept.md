# Tre konsept til 17. november

Dato: 13.11.2026. Dei tre konsepta kjem frå seks formfamiliar med 18 kandidatar, rekna i lysmotoren og etterprøvde av ein skeptikar per familie. Kvart konsept brukar éin del av byggjesettet: bøygd plate og folie, fresnelplata og ei linse med frontflatespegelen frå overheadprojektoren.

Dette er runde 2. Runde 1 fall på veggen bak skjermen i arbeid, på jamnheita for B og C og på ei linse som ikkje fanst. Arka og tala frå runde 1 ligg i `forste/`.

| | Grep | Byggjesett | Handling |
| --- | --- | --- | --- |
| **A Skiva** | Ei kjelde i foten lyser opp på ei bøygd spegelskive som vippar frå veggen ned på feltet. Ein fast flik på stamma held veggen bak skjermen lys. | folie på papp, bøygd over ein printa ribbe, ein flik med bakepapir | vipp skiva |
| **B Over** | Fresnelplata over skjermkanten er knekt. Den store delen vippar lyset frå veggen ned på bordet, fliken held veggen bak skjermen lys. | fresnelplata, diffusorark, stolpen | vipp plata |
| **C Vindauge** | Ei vasskule teiknar eit vindauge av lys på veggen. Ein spegel glir inn i strålen og legg feltet på bordet, medan vindauget blir. | julekule fylt med vatn, maske og gråfilter på overheadfilm, frontflatespegelen | skyv spegelen inn |

Arka: `ark-A-skiva.png`, `ark-B-over.png`, `ark-C-vindauge.png`. Tala: `tal.md`, rekna med `tre.py`. Søka: `a_sok.py`, `b_sok.py`, `c_sok.py` med resultat i `*.jsonl`.

## Tala

Same rom, same mannekeng, same watt: 1,25 W i stemning og 5 W i arbeid, skalert til 350 lx på feltet. Modell, ikkje måling.

| | A Skiva | B Over | C Vindauge |
| --- | --- | --- | --- |
| Watt for 350 lx på feltet (tak 7,5) | 2,99 | 3,56 | 5,78 |
| Timar per celle ved 350 lx | 5,1 | 4,2 | 2,6 |
| Jamnheit (referanse 0,6) | 0,62 | 0,41 | 0,62 |
| Mot auget ved 350 lx, auge 25 / 47 / 60 cm (F1 3000, F5 1500) | 1013 / 103 / 103 | 1124 / 196 / 196 | 155 / 122 / 122 |
| Veggen bak skjermen ved 350 lx (F6 100 til 150, snitt på 2 cm gitter) | 109 | 114 | 127 |
| Skjermflata ved 350 lx (del av feltet) | 115 (0,33) | 60 (0,17) | 39 (0,11) |
| Ansiktet ved 350 lx | 29 | 43 | 25 |
| Stemning: mot auget, verste augehøgd (krav 500) | 424 | 110 | 76 |
| Stemning: veggen bak skjermen | 131 | 108 | 72 |
| Stemning: skjermflata | 105 | 5 | 0 |
| Likskap stemning og arbeid (over 0,9 er dimmar) | 0,60 | 0,71 | 0,54 |
| Største sprang langs overgangen | 0,08 | 0,12 | 0,05 |
| Skjermflata langs overgangen, lx (skalert til 350 lx)¹ | 63 · 104 · 131 · 138 · 115 | 4 · 48 · 173 · 173 · 60 | 0 · 4 · 10 · 21 · 39 |

¹ Skalert til 350 lx på feltet i arbeid, som resten av tabellen. Uskalert, ved watten i kvart steg (1,25 til 5 W), var talet A 105 · 174 · 220 · 231 · 193, B 5 · 68 · 243 · 243 · 85 og C 0 · 3 · 9 · 18 · 34 lx.

Lyset på skjermflata blir samanlikna som del av feltet. Bru og krok frå formsøket i `northern-lampe/` ligg på om lag 1,2 til 1,3, prisma på 0,02.

## Kva som vart gjort i runde 2

**Veggen bak skjermen (F6).** 100 lx på om lag 0,84 m² vegg kostar like mange lumen som 350 lx på feltet. Difor må ein del av lyset gå til veggen òg i arbeid. Alle tre har no ein eigen veg dit:

- A: ein andre diode i foten (smal, 5°) lyser på ein fast flik 3,5 cm til venstre for stamma (12 × 8,4 cm, satinert, 30 cm over bordet). Fliken sender 30 % av watten forbi skjermkanten til veggen bak skjermen. Ein matt flik gav 32 til 52 lx og blenda med 2400 til 7000 cd/m², så fliken må vere satinert. Med fliken rett på stamma kasta stamma ein brei skugge på veggen, og ein vid diode (8°) lyste forbi fliken og opp i taket.
- B: plata er delt langs ein diameter og knekt. Ein flik på 60 mm siktar på veggen over skjermkanten. 80 mm gav 157 lx, over målet.
- C: spegelen tek 65 % til bordet i staden for 75 %. Resten blir verande vindauge på veggen.

**Ei linse som finst (C).** Den tenkte linsa på 60 mm er bytt ut med ei glaskule fylt med vatn, Ø 70 mm (ei julekule). Brennvidda er f = nD / (4(n − 1)) = 70 mm frå midten med n = 1,333. Ei vanleg lupe 3x Ø 75 mm gjev nesten same tal (f 100 mm: 6,4 W og jamnheit 0,60 med hovudet 60 cm over bordet). Kondensoren er rekna som ei sterk fresnellinse, til dømes ei kredittkort-fresnel.

**Jamnheita.**

- C: jamnheita kom av hovudhøgda, ikkje av linsa. Hovudet 36 cm over bordet gav 0,24, 48 cm gav 0,31 og 70 cm gav 0,39. Eit gråfilter i maska (svakare der strålen har kortast veg) løftar ho til 0,62 og kostar 1,6 W. Filteret kan skrivast ut som ein grå gradient på overheadfilm.
- B: jamnheita stoppar på om lag 0,45. Diffusorarket er same knapp som luminansen mot auget: ark 14° gjev 0,41 til 0,52 og om lag 1100 cd/m², ark 12° gjev 0,34 til 0,37 og om lag 420. Høgare plate (70 cm) gav 0,45 til 0,48 og 4,6 W. 0,6 er ikkje nådd under 1500 cd/m² i nokon variant. B held difor ikkje referansen, og det er eit funn om fresnelplata, ikkje ein feil i oppsettet.

**Blending om lobebreidda er feil (A).** Skiva er rekna med blank folie (lobe 2,5°). Med lobe 4° ser auget i 25 cm 700 cd/m², med 6° 4075. Grensa for F1 ligg om lag ved 5°. Krav til flata: lobe under 4,5°. Frontflatespegelen og blank, anodisert aluminium held det. Folie på papp må målast.

## Kvar dei står

**A Skiva** er den jamnaste og brukar minst straum (3,0 W). Svakheita er skjermflata: spegelskiva legg 0,33 av feltluxen på skjermen i arbeid og 131 lx midt i overgangen, og auget 25 cm over bordet ser fliken med 1013 cd/m². Næraste nabo er Verner Panton Reflect, som har fast, kvit skive og ingen flik.

**B Over** held stemninga av skjermen (5 lx), som C (0 lx). A legg 105 lx på skjermflata i stemning (ved 1,25 W). Svakheita er jamnheita (0,41) og at strålen sveipar over skjermen midt i vippen (173 lx). Det låge auget ser 1124 cd/m², under F5. Næraste nabo er BenQ ScreenBar Halo.

**C Vindauge** er den reinaste: lite lys på skjermen langs heile overgangen (høgst 39 lx), låg luminans mot auget i alle høgder, og vindauget på veggen står i ro. Svakheita er watten (5,8 W, 2,6 timar per celle) og hovudet 70 cm over bordet. Ingen kjend lampe deler strålen slik.

## Det etterprøvinga i runde 1 fann

1. **Lobebreidda avgjer F1.** Sjå over.
2. **Vippe og skjere er overgang. Skyve, dreie og dimme er dimmar** (likskap 0,8 til 0,99).
3. **Å flytte strålen frå vegg til felt sveipar over skjermen** (500 til 2700 lx på skjermflata midt i overgangen, ved 5 W i overgangsfamilien). Å dele strålen gjer det ikkje. C deler, A og B flyttar.
4. **Veggen bak skjermen kostar like mykje lys som feltet.** Lyset landar dessutan lett ved sida av skjermen, ikkje bak han.
5. **Mjuk fald er gratis.** Éin eller to faldar med radius 40 til 80 mm kostar 2 til 7 % watt.
6. **Linsa på 285 mm høyrer heime frå 1,1 m kast.** Kondensoren, ikkje linsa, avgjer verknadsgraden.

Etterprøvingane ligg i `../reflektor/*/etterproving.md`.

## Første forsøk: mål lobebreidda

1. Mørkt rom. Telefonlykta 1 m frå prøva, lyset inn på 45°.
2. Eit kvitt kort d = 50 cm frå prøva i speglingsretninga.
3. Mål diameteren D der flekken er halvparten så lys som midten. Foto med låst eksponering gjer det enklare.
4. Lobebreidda σ i grader er om lag 24 · D / d. A krev σ under 4,5° (D under 9 cm). Satin er rekna med 10° (D 21 cm).
5. Prøv folie på papp, frontflatespegelen, fresnelplata med eitt og to diffusorark, og bakepapir oppå folie.

## Skissemodellar

**A Skiva:** Folie på papp Ø 250 mm, limt utan krøll, med ein 3D-printa ribbe med boge R 1,2 m (pil 6,5 mm) bak. Telefonlykta i foten, 5 cm over bordet, i ein svart papprull Ø 25 mm og 34 mm lang: då slepper rullen ut lys til 20° frå aksen, som i modellen. Stolpen frå overheadprojektoren held skiva 41 cm over bordet, 15 cm framfor skjermplanet. Fliken: papp 12 × 8,4 cm med folie og bakepapir, på ein kort arm 3,5 cm til venstre for stolpen og 30 cm over bordet. Han får lys frå ei lykt til med smal stråle (10° frå aksen: rull Ø 15 mm, 43 mm lang). Føreseiing: lågaste rute delt på snittet over 0,5 med bøyen, under 0,45 flat.

**B Over:** Fresnelplata i ei pappramme. Knekken går langs midtlina: den framre halvdelen (mot brukaren) lyser på feltet, fliken er dei 60 mm bak midtlina, og dei bakste 82,5 mm er dekte med svart papp. Plata skal ikkje klippast: ein flik av blank folie på papp, 285 × 60 mm, vinkla 48° frå hovuddelen, gjev same lys på veggen (135 mot 134 lx ved 350 lx på feltet). Plata vippar om ein akse gjennom midten, med tappar midt på sidekantane. Stolpen klemt bak skjermen, plata 20 cm over skjermkanten og 9 cm framfor skjermplanet. Telefonen 9 cm over skjermkanten og 4 cm framfor skjermplanet, med lykta opp i ein brønn av svart papp, 12 cm under plata. To diffusorark teipa på plata. Føreseiing: jamnheit om lag 0,4, veggen bak skjermen om lag ein tredel av feltet.

**C Vindauge:** Ei julekule av glas, Ø 70 mm, fylt med vatn. Maska i papp, gråfilteret skrive ut på overheadfilm, kredittkort-fresnel som kondensor, frontflatespegelen på eit papphengsel rett etter kula. Hovudet på stolpen 70 cm over bordet, til høgre for skjermen. Føreseiing: vindauget står i ro på veggen medan feltet kjem fram, og lyset på skjermen er under 0,15 av feltet langs heile vegen.

## Avgrensingar

- Alle tal er modell. Kjelda er telefonlykta i modellane, ikkje produktet.
- Mannekengen frå `modell/polge.py` er ryggfigur. Han endrar ikkje tala for lampa.
- Linsa i C er rekna som tynn linse med 5 cm uskarpleik per meter. Vasskula har stor sfærisk aberrasjon, så kanten blir mjukare enn rekna.
- Spegling i skjermen og i blank bordflate er ikkje rekna for arka.
- Kroppane er skisser: A har ei svart kantskive bak spegelen, B har stolpen bak skjermen. Dei endrar lysrekninga under 1 %.
