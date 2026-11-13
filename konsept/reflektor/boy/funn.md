# BØY: funn

Arket er berre bøygd (enkeltkrumt, strekk 0). Ei LED i foten lyser opp på arket. Tal frå `tal.md` (5 W i arbeid, 1,25 W i stemning), `ekstra.md` (auge i 25 og 60 cm) og `overgang.md`. Modell, ikkje måling.

## 1 Kva eg varierte, og kva som stivna
- **Gen 1 (16):** berre bøyen, satin Ø 250 mm på malplassen: hol og kuv, konstant og varierande krumming (S, trau, rull, bølgje, kjegle), aksen (rull 0 og 90). W for 350 lx gjekk frå 2,10 (hol) til 5,86 (kjegle-kuv), jamnheita frå 0,21 til 0,49. Stivna: bøyen bytte berre watt mot jamnheit. Veggen stod på 30 til 40 lx, og mot auget stod 949 til 973 cd/m² eller sprakk (kuv-kast 6289, rull-kast 20 694).
- **Gen 2 (17):** plass framfor skjermplanet og sikte 10 cm forbi feltmidten, storleik, overflate, høgd, kjelde i stamma, overgang ved å bøye, to adresser. Overflata flytta meir enn bøyen: blank kuv fekk jamnheit 0,60 og 194 cd/m². Kjegle-fram fekk 0,62, men 3865 cd/m². Flex gav 606 cd/m² i stemning. (To-radene i `gen2/tal.md` kom frå ein eldre `to()`.)
- **Gen 3 (16):** spegelkrumming R 0,6 til 2,0 m og flat, folie og krølla folie, storleik 0,20 til 0,32 m, to adresser på spegel med glid, to diodar og høgd, satin som referanse. Stivna: jamnheita står på 0,60 for all kuv spegel frå R 0,6 til 2,0. Bøyen styrer då berre watt (2,55 til 1,98) og om kjelda syner for eit lågt auge.

## 2 Dei tre beste
| | spegel-kuv-1.2 | to-spegel | to-spegel-kryss |
| --- | --- | --- | --- |
| W for 350 lx | 2,14 | 2,36 | 3,32 |
| W for 350 lx og 100 lx på veggen | 20,74 | 4,62 | 4,37 |
| Felt ved 5 W, jamnheit | 817 lx, 0,60 | 741 lx, 0,43 | 527 lx, 0,33 |
| Vegg i arbeid | 24 lx | 108 lx | 114 lx |
| Mot auget 25 / 47 / 60 cm | 194 / 194 / 194 | 193 / 205 / 193 | 1836 / 224 / 118 |
| Stemning: auge, felt, vegg | 83 cd/m², 9 lx, 68 lx | 94, 31, 56 | 139, 19, 50 |
| Skjermflata arbeid / stemning | 268 / 142 lx | 371 / 66 lx | 241 / 42 lx |
| Likskap, topp, sprang | 0,23, 0,70, 0,13 | 0,58, 1,01, 0,05 | 0,74, 0,97, 0,02 |

- **spegel-kuv-1.2.** Blank Ø 250 mm, kuv R 1,2 m (pil 6,5 mm), krumminga på tvers av kastet. Senter (0,47, 0,30) 41 cm over bordet, LED i foten (0,47, 0,38) 5 cm opp, 10° spreiing. Overgang: vipp frå veggen bak skjermen til 10 cm forbi feltmidten. *Den slakaste bøyen som spreier spegelbiletet over heile feltet: lågast watt med jamnheit 0,60, men veggen må få eit eige strøk i arbeid.*
- **to-spegel.** Blank 380 × 250 mm, to flate soner og ein mjuk bøy på 33,3° (sigma 20 mm) 40 mm frå midten. Sone A speglar mot feltet, sone B mot veggen. Overgang: arket glir 110 mm langs bøyeretninga medan strålen står i ro. *Ja, bøyen åleine gjev to adresser: 350 lx og 100 lx for 4,62 W, utan eige veggstrøk.*
- **to-spegel-kryss.** Same ark, fast. To diodar i foten siktar på kvar si sone, og watten blir flytta frå veggdioden til feltdioden (60 % i arbeid). *Ingen rørsle, mjukast overgang (sprang 0,02), men lys går forbi arkkanten mot taket, og det låge auget ser 1836 cd/m².*

## 3 Velt og umogleg
- **VELT-spegel-hol** (blank hol R 0,3): brennlinje på feltet. 1255 lx, men jamnheit 0,01. Bryt F3.
- Utilsikta velt: tett kuv (R 0,6) og stort ark (0,32 m) syner kjelda for auget 25 cm over bordet: 3475 og 19 194 cd/m². Bryt F1, men tal() ser det ikkje i 47 cm.
- **UMOGLEG-to-trau:** to-spegel med krumming på tvers attåt. Strekk 13,04 %. Kan ikkje bøyast av eitt ark, og jamnheita fell til 0,02.

## 4 Funn som gjeld meir enn bøy
1. Overflata avgjer før bøyen. Same plass og bøy: satin gjev 967 cd/m² mot auget, spegel 194 til 215. Ein satinlobe spreier alt, så bøyen får lite å gjere.
2. To adresser frå éi flate krev spegel. Satinlobane på 10° blandar dei to strålane: 4,91 til 5,55 W og 3944 til 3998 cd/m² for det låge auget, mot 4,62 W og 193 for spegel.
3. F1 må prøvast i tre augehøgder. I 47 cm gav alle spegel 194 cd/m²; i 25 cm gav dei 194 til 211 870.
4. Lampa lyser òg på skjermen: 0,11 til 0,52 av feltluxen i arbeid. I stemning gav einadresse-arka 98 til 153 lx på skjermflata fordi veggflekken ligg rett over skjermkanten. Sikte 62 cm over bordet tok spegel-kuv-1.2 frå 142 til 78 lx og veggen frå 68 til 64 (`sok11.txt`).
5. Stemning utan glød er lett når arket vender mot veggen: 50 til 196 cd/m² for alle gen 3 utanom umogleg (277). Krava blir brotne i arbeid og overgang, ikkje i stemning.

## 5 Føreseiingar til skissemodellen (sette 13.11 før måling)
- P1: Folie på papp med pil 6,5 mm over 250 mm gjev lågaste rute delt på snittet over 0,5, flat folie under 0,45 (modell 0,61, og 0,39 for flat spegel). Snittluxen fell høgst 25 % (modell 18 %).
- P2: Med pil 13 mm (R 0,6) ser du eit lyspunkt i arket frå 25 cm over bordet, med pil 6,5 mm ikkje (modell 3475 mot 194 cd/m²).
- P3: Knekk 33° 40 mm frå midten: veggen bak skjermen får minst 3 gonger så mykje som utan knekk (modell 4,4 gonger), og feltet mistar under 15 % (modell 10 %).
- P4: Bakepapir oppå folien (satin) gjev eit lyspunkt mot auget i 25 cm minst 5 gonger lysare enn flat folie (modell 3988 mot 194 for flat spegel).
- P5: Vippa mot veggen ser arket mørkt ut frå 47 cm, og veggflekken er det lysaste i synsfeltet (modell 0 cd/m² frå arket, `sok7.txt`).

## 6 Oppskrift: skissemodell på under éin dag
1. Ark: papp 380 × 250 mm og ein Ø 250 mm, glatt aluminiumsfolie limt på utan krøll (blank side ut). Bøyen: to 3D-printa ribber teipa bak, éin boge R 1,2 m (pil 6,5 mm) og éin med to rette strekk og ein 33° bøy med radius om lag 20 mm, 40 mm frå midten.
2. Kjelde: telefonlykta i ein svart papprull, Ø 25 × 100 mm, som avgrensar strålen til om lag ±12°. Lykta står i foten 5 cm over bordet og peikar opp mot arksenteret.
3. Stamme: stolpen med ledd frå overheadprojektoren held arket 41 cm over bordet, 15 cm framfor skjermplanet og 47 cm til høgre for feltmidten.
4. Sikt i arbeid: lysflekken midt 10 cm forbi feltmidten, bort frå lampa. Stemning: vipp (eller la arket gli) til flekken ligg på veggen over skjermkanten.
5. Mål i mørkt rom: lux i 6 × 4 ruter på 10 cm, tre punkt på veggen bak skjermen, foto over høgre skulder med låst eksponering, og sjå på arket frå 25, 47 og 60 cm. Lykta har ukjend lumen: prøv forhold, ikkje lux.

## 7 Usikkert, og det modellen ikkje reknar
- 194 cd/m² mot auget for spegel er diffusdelen (rd 0,03) i BLANK, ei antaking. Dis på folie er ikkje målt; FOLIE og KROLL er mine antakingar.
- Spegling av det blanke arket i dataskjermen er ikkje rekna. Ein spegel framfor skjermen kan synast der.
- Stripene i veggflekken for to-spegel kjem truleg av fasettane (n = 30, sigma 2,5°), ikkje av lyset.
- Minstestorleiken byggjer på tre punkt (0,18 og 0,20 m gav 0,05 og 0,15). Kvifor jamnheita fell så bratt, er ikkje forklart.
- Sjølvskugge i knekken er ikkje rekna. Skjermlux i `ekstra.md` er eitt punkt, `tal.md` er snittet.
- Motoren fekk nye skjermkolonnar kl. 10.33 midt i økta. Dei andre tala er uendra (spegel-kuv-0.6: 685 lx før og etter).
- Feil i motoren: `ortho()` byter opp-vektor når |n_z| passerer 0,9, så ramma til `ark()` (bøyeaksen og nullpunktet for `rull`) hoppar når arket blir vippa. Døme: n = (0,31, -0,31, 0,899) gjev u = (0,707, 0,707, 0), n_z = 0,901 gjev u = (0,947, 0, -0,322). Eit bøygd ark som blir vippa, er då ikkje éin stiv kropp. `lampe()` i `familie.py` sender difor eigen `opp`.
- `tal()` måler auget berre i 47 cm. F1 gjeld 25 til 60 cm, og det låge auget var det som skilde spegelarka (`auge_i()` i `familie.py`).
