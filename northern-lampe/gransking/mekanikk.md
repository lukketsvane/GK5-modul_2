# Mekanikk, varme og stabilitet · gransking · 2026-11-13

Linse: mekanikk, varme og stabilitet for (a) bru, (b) krok og (c) prisme. To skript, skrivne kvar for seg:
- `mekanikk_ut.py` (rammeløysar med GJ, einingslast for krum stong; frå den avbrotne granskinga, no køyrt ferdig, logg i `mekanikk_ut.log`, tal i `mekanikk_tal.json`).
- `mekanikk_kontroll.py` (ny, handformlar, ingen import frå mekanikk*.py, felles.py eller motorane; tal i `mekanikk_kontroll.json`, køyretid om lag 1 s).

Dei to gjev same tal innan 1–5 %. Der dei skil seg, står begge. Parametrane er lesne bokstavleg frå `form01/motor.py`, `form02/val.py` (tal_bru 15°, B_KROK, tube_arm) og `form04/motor.py` (FINAL, tal_mek).

## Kort
- **(a) veltar av sin eigen gest om han vert gjord som eit fingerdytt.** Lampa lyftar ved 2,81 N øvst på grepet. Eit fingerdytt som gjev 0,08 N·m på grepet (r 26 mm) er 3,08 N, λ 0,91. Som klyp (kraftpar) er λ 23. 10 N i grephøgd: λ 0,28.
- **(b) Ø23 er stadfest til 2,34 mm**, men det er for 3 N sidevegs i spissen. Sjølve fingergesten gjev 1,72 mm. Ø25×1,5 held 2 mm i alle lastfall. Klemma må halde 0,4–0,46 kN (SF 1), 0,8–0,9 kN med SF 2, og massiv spon eller MDF toler det med pute Ø40.
- **(c) Den opne U-profilen held ikkje.** Ein gest i enden av hovudet gjev 6–22 mm (krav 2 mm), og hovudet svingar om søyla med 1,9 Hz. Lukka 100×30×1,5 gjev under 0,05 mm og 40 Hz for +0,20 kg. Motoren sine 0,2 mm gjeld berre eit dytt midt på hovudet.
- **(c) Hovudet kan ikkje vippe til stemning slik det er teikna.** Plata går inn i armen ved α −51° (akse i LED-lina) eller −62° (akse i tyngdepunktet). Stemninga ligg på −105°.
- **(c) Vippeaksen er ikkje bestemt.** Mekanikken reknar med akse i tyngdepunktet til hovudet, geometri og lys med akse i LED-lina. Med LED-lina held ikkje friksjonen 0,20 pendelen (0,22 N·m). Med tyngdepunktet flyttar LED-lina seg 51 mm, og lyset er rekna for feil stad.
- **Varme er ikkje eit problem for nokon av dei.** LED-loddepunkt 35–53 °C i 25 °C rom. Kriteriet har rett form og rett h for eloksert eller lakka alu, men ΔT 30 K er for varmt for ei flate handa tek i.

## Tal mot konsept.md
| | konsept.md | kontroll | merknad |
|---|---|---|---|
| (a) masse | 1,25 kg | 1,23 kg | stadfest |
| (a) tipp | 18° | 17,6° | stadfest; lyftar likevel ved 2,8 N i grephøgd |
| (a) svikt under gesten | 0,8 mm | om lag 0 | 0,8 mm er 10 N sidevegs på toppen (form01 tal(), svikt_x); gesten går i A-planet, som er triangulert |
| (b) svikt | 2,0 mm | 2,34 (3 N sidevegs) · 1,72 (finger) | tube_arm() hadde berre bøying (dist²) |
| (b) klemme | 500 N, 1000 N med SF 2 | 395–456 N, 790–910 N | stadfest |
| (c) masse | 3,11 kg | 3,20 kg | tal_mek() manglar hengjarar, kinn og ledd (0,11 kg) |
| (c) tipp utan skjerm | 22° | 20,1° fram, 21,5° side | tyngdepunktet ligg 16 mm høgare når søyla går til overkant arm |
| (c) svikt | 0,2 mm | 0,16–0,22 midt · 6,3–22,5 i enden | vridning av open U er ikkje med i tal_mek() |
| (c) fot | 7 mm | 8 mm (T 0,20) · 14 mm (T 0,30) | rett kraftpunkt er plate-kanten i z 0,750, ikkje z 0,70 |

## 1 (a) bru · dytt i grephøgd og retting
Masse 1,233 kg, tyngdepunkt y 0,180 z 0,474. Føter y 0,03–0,33, x ±0,576. Rettande moment om framkanten m·g·0,15 = 1,81 N·m.

| last | lyftar ved | λ |
|---|---|---|
| 10 N mot brukar eller vegg i aksehøgd 0,62 | 2,93 N | 0,29 |
| 10 N øvst på grepet (0,646) | 2,81 N | 0,28 |
| fingerdytt 3,08 N øvst på grepet, fram eller bak | 2,81 N | 0,91 |
| fingerdytt 3,08 N opp framme på grepet | 6,06 N | 1,97 |
| kraftpar 0,08 N·m om røyraksen (klyp) | 1,81 N·m | 23 |
| 10 N sidevegs i aksehøgd | 10,9 N | 1,09 |

Lampa tippar før ho glid så sant μ > 0,24, altså med gummiføter. Ho fell mot brukaren, og røyret slår ned om lag 0,6 m framfor bordkanten. Energien er 0,28 J, så det er ikkje farleg, men det strir mot «intuitiv bruk» og «ro». **Det er eit reelt problem**: gesten skjer på grepet, og eit sleivete vri med éin finger er nok til å lyfte lampa.

Tippkrafta er F = m·g·d/h. Ho avheng ikkje av kor høgt tyngdepunktet ligg, berre av masse, djupna d frå tyngdepunktet til kanten og høgda h på krafta. Framkanten kan ikkje flyttast fram (framfoten står alt på y 0,03, bordkanten er y 0). Fram må det difor masse til, og masse langt bak verkar 3–4 gonger meir enn masse midt, fordi armen om framkanten er lengre.

| retting (kvar for seg) | ekstra | total | lyftar ved, øvst på grepet (fram / bak) | finger λ |
|---|---|---|---|---|
| stål i føtene, same fotavtrykk | +3,16 kg | 4,39 kg | 10 / 10 N | 3,3 |
| meie flattstål 25×5, y 0,01–0,70 per side | +1,35 kg | 2,59 kg | 10,3 / 16,8 N | 3,3 |
| meie alu 25×5 + lodd 0,35 kg bak (y 0,66) per side | +1,17 kg | 2,40 kg | 12,5 / 12,6 N | 4,1 |
| meie flattstål 30×6, y 0,01–0,70 | +1,95 kg | 3,18 kg | 13,4 / 20,0 N | 4,4 |

**Billegaste retting: ei meie av flattstål 25×5 mm langs foten på kvar side, frå framfoten (y 0,01) til y 0,70.** Ho kostar nokre kroner i materiale og tek òg sidekrafta som spreier beina (0,74 N per fot utan meie, som berre held om μ ≥ 0,25). Meia ligg ved x ±0,576, utanfor skjermen og rett utanfor musesona (x 0,30–0,55). Grepet bør i tillegg formast for klyp (riflar rundt, ikkje ei tunge eller ein knapp øvst), sidan klyp gjev λ 23 og kostar ingenting.

Røyret er ope over 0,60 m (spalte 50°): GJ 1,76 N·m² mot 1946 for lukka røyr. 0,04 N·m friksjon i det fjerne navet vrir røyret 0,8°. Det kjennest som ei lita fjør i grepet, ikkje som eit problem.

## 2 (b) krok · arm, Ø, klemme, bordplate
Arm 1,104 m: loddrett frå klemma (y 0,74) til bogen, boge r 0,10, vassrett fram til y 0,25 i z 0,657, kort fall til navet. Utbøying langs krafta δ = ∫(M_b²/EI + T²/GJ) ds / F, med eiga parametrisering av bogen i `mekanikk_kontroll.py`.

| Ø×1,5 | 3 N sidevegs i spissen | 3 N sidevegs i grepet | fingergest 3,08 N i grepet | arm |
|---|---|---|---|---|
| Ø23 | **2,34 mm** (bøy 0,91 + vri 1,42) | 2,24 | 1,72 | 0,30 kg |
| Ø24 | 2,04 | 1,96 | 1,50 | 0,32 kg |
| **Ø25** | **1,79** | 1,72 | 1,32 | 0,33 kg |
| Ø26 | 1,58 | 1,52 | 1,17 | 0,34 kg |

Kontroll med rett L utan boge (a 0,49, h 0,645): 2,44 mm, litt over sidan bogen kortar begge armane. **Stadfest: Ø23 svikter 2,34 mm, og Ø25×1,5 held 2 mm** (heile forskyvinga |u| i grepet 1,99 mm, så Ø26 om det skal vere margin). To presiseringar: 2,34 mm er for eit sidedytt langs røyret, ikkje for gesten, og gesten åleine held med Ø23 (1,72 mm). Eigenvekta gjev 2,25 mm nedbøying (Ø23), men det er ei fast forskyving som kan bøygjast inn, ikkje vagg. Sidesvinginga er 7,9 Hz (Ø23) og 8,9 Hz (Ø25).

**Klemme.** Dimensjonerande er 10 N langs røyret i navet: 4,7 N·m vri om skruelina og 6,2 N·m vipp over kanten av kjeften, som berre er 50 mm brei.

| | vri | vipp over 50 mm kjeft | SF 2 |
|---|---|---|---|
| μ 0,3 (metall mot melamin) | 395–456 N | 238 N | 0,8–0,9 kN |
| μ 0,6 (gummi) | 195 N | 238 N | 0,48 kN |

Det er ei vanleg skjermarmklemme: C-ramme stål 50×6 (σ 106 av 117 MPa) eller alu 6082 50×8 (σ 60 av 125 MPa) med kast 35 mm, M8 med 1,3–1,5 N·m. Med stjernegrep Ø50 er det 50–60 N i kanten, eit fast handtak; unbrako eller vengemutter er tryggare. Røyrfoten treng ei hylse minst 40 mm djup (12 mm gjev 7,8 MPa kanttrykk, 40 mm gjev 0,7 MPa). 0,25 kg for klemma i val.py held berre med alu; i stål vert ho om lag 0,45 kg.

**Bordplata.** Flatetrykk ved 0,8–0,9 kN: pute Ø25 1,6–1,9 MPa, Ø40 0,6–0,7 MPa, plate 60×60 0,22–0,25 MPa. Kanttrykk i toppkjeften 0,39 MPa. Bøying i plata frå 8,6 N·m over 0,2 m breidd: 0,4 MPa (25 mm) og 0,3 MPa (30 mm) mot bøyefastleik 11–14 MPa for spon P2. **Massiv spon eller MDF 25–30 mm er sterk nok.** Men ei lita pute kan merke melaminen, og spon kryp så klemma losnar over tid; bruk Ø40 med gummi eller ei stålplate 60×60 under. Ei hol bordplate med papirkjerne, vanleg i rimelege heimebord, er ikkje rekna og toler langt mindre; der må det lastfordelingsplate på begge sider. Klemma krev òg glipe mot veggen og ingen zarge langs bakkanten.

## 3 (c) prisme · masse, tipp, fot, svikt, vridning
**Masse og tyngdepunkt** (eige oppsett frå geometri(): U-areal 312 mm², søyle frå fot til overkant arm, hengjarar, kinn, ledd 0,05 kg):

| | masse | tyngdepunkt y / z | tipp fram / bak / side | lyftar ved, 10 N-retning, i aksen (z 0,668) |
|---|---|---|---|---|
| aleine | 3,20 kg (motor 3,11) | 0,394 / 0,305 | 20,1° / 31,7° / 21,5° | 5,26 N mot brukar |
| med skjerm 4 kg i (0, 0,50, 0,20) | 7,20 kg | 0,453 / 0,247 | 34,7° / 27,6° / 25,9° | 18,1 N |

Hovudet: plate 0,457 kg, renne og LED 0,236 kg, kinn 0,039 kg; tyngdepunktet ligg 32 mm under LED-lina (motoren: 33 mm).

**Gest og fot.** Handa tek i plate-kanten og skyv tangentielt. Sveip over α −105° til +70°, begge kantar, begge retningar:

| akse | T | aleine | med skjerm |
|---|---|---|---|
| tyngdepunktet (som tal_mek) | 0,20 N·m | **λ 1,92** (α −105°, øvre kant, z 0,750, veltar fram) | 4,48 |
| tyngdepunktet | 0,30 N·m | **λ 1,28** | 2,99 |
| LED-lina (som geometri og lys), friksjon + pendel | 0,20 N·m | λ 1,06 | 2,58 |
| LED-lina | 0,30 N·m | **λ 0,86, veltar** | 2,08 |

Motoren reknar F_tipp = m·g·d/z_s med krafta i z 0,70 og får 5,13 N ≥ 2·2,5 N med 7 mm fot. Rett kraftpunkt er 50 mm høgare. **Fot for λ ≥ 2 utan skjerm: 8 mm alu (3,40 kg) ved T 0,20, 14 mm (4,56 kg) ved T 0,30.** Billegare: stål bak i foten (y 0,55), 0,05 kg ved T 0,20 og 0,75 kg ved T 0,30. Lampa lyftar òg om losrivingsmomentet i leddet er over 0,38 N·m; friksjonsledd har ofte 20–50 % høgare losriving enn gangmoment, så eit ledd på 0,30 N·m ligg på grensa. 10 N i aksehøgd utan skjerm krev 1,20 kg ekstra bak i foten.

**U 100×30×2.** A 312 mm², I svak 2,35·10⁻⁸ m⁴, J = Σ b t³/3 = 4,16·10⁻¹⁰ m⁴ (GJ 10,9 N·m²), C_w 4,06·10⁻¹¹ m⁶, a = √(E C_w / G J) = 0,51 m. Lukka 100×30×2: J 2,39·10⁻⁷ (575×). Lukka 100×30×1,5: 1,86·10⁻⁷ (447×).

| gest i enden av hovudet (x 0,30) | U fri | U, kvelving hindra i rota | lukka ×2 | lukka ×1,5 |
|---|---|---|---|---|
| arbeid, framkant ned, T 0,20 (0,73 N·m om armen) | 6,3 mm | 0,7 | 0,011 | 0,014 |
| stemning, øvre kant mot brukar, T 0,20 (0,73 N·m om søyla) | **15,0 mm** | 5,8 | 0,026 | 0,033 |
| arbeid, T 0,30 | 9,5 | 1,1 | 0,017 | 0,021 |
| stemning, T 0,30 | **22,5** | 8,7 | 0,039 | 0,050 |
| 10 N sidevegs i hovudenden | 68 mm (12,3°) | | 0,14 | 0,18 |
| vridningssving om søyla | **1,9 Hz** | 3,1 Hz | 45 Hz | 40 Hz |

Rammeløysaren i `mekanikk_ut.py` gjev 6,9 / 15,2 / 10,3 / 22,8 mm for dei same fall (med bøying i tillegg). Midt på hovudet er svikta 0,16–0,22 mm i begge løysarar, som motoren (0,19). Nedbøying frå hovudvekta: 0,40 mm (motor 0,355). Skjerspenning i open U ved 10 N sidevegs: 15 MPa mot 72 tillate, så styrken held; det er stivleiken som sviktar. **U-profilen er ikkje god nok: ein gest som ikkje treffer midt på hovudet vrir søyla 3–8 gonger over kravet, og ein svingetid på 0,5 s gjer at hovudet dirrar synleg når bordet vert dunka i.** Kvelvingshindring hjelper berre om hjørnet er heilsveist, og held ikkje for stemningsgesten (5,8–8,7 mm). Lukka 100×30×1,5 (eller U-en lukka med ei 1,5 mm plate som er nagla tett) gjev 0,01–0,05 mm og 40 Hz for +0,20 kg.

**Hovudet sjølv.** Renna 16×20×1,5 er open (GJ 1,57 N·m²). Med ledd ved x ±0,05 vrir T 0,20 i enden renna 1,8° (plate-kanten 2,5 mm), T 0,30 2,7° (3,8 mm). Plata bidreg litt via kinna (1,4° i `mekanikk_ut.py`). PMMA-plata 3 mm, berre boren av kinna i endane, søkk **11,7 mm** midt (17,5 mm etter kryp, E 2 GPa) og hallar 3,6° ved kinnet. Då er avstanden LED–plate 62–68 mm midt, ikkje dei 50 mm optikk() har rekna rillene for. 6 mm plate gjev 2,6 mm; to ekstra opphengspunkt ved x ±0,10 gjev 0,1 mm.

**Kollisjon mellom plate og arm.** Armen har underkant z 0,730 for y ≥ 0,208 (flensane ved x ±0,05; plata er heil i x). Kanten av plata ligg 94–96 mm frå LED-lina.

| akse | plata når armen ved | øvre plate-kant ved −105° | armen må opp |
|---|---|---|---|
| LED-lina (geometri(), hovudpunkt(), lyset) | α −51° | y 0,248 z 0,790 | 62 mm |
| tyngdepunktet (gestkraft(), logg.md) | α −62° | y 0,217 z 0,750 | 21 mm |

kollisjon() i form04/motor.py sjekkar vegg, skjerm, søyle og siktline, men ikkje armen. Hengjarane ved x ±0,05 går dessutan gjennom renna i geometri(); leddet må anten liggje i endane av hovudet (ei gaffel 62 cm brei) eller renna må delast ved hengjarane.

**Aksen.** tal_mek()/gestkraft() set pendelmomentet til null fordi aksen skal liggje i tyngdepunktet til hovudet. geometri() teiknar hengjarane ned til LED-lina, og lyset er rekna med vipp om LED-lina (logg.md nemner det som ein liten, ikkje rekna feil). Om LED-lina: plata gjev 0,22 N·m ved −105° og 0,23 N·m ved −90°, meir enn friksjonen 0,20, så hovudet fell tilbake frå stemning; og gesten veltar lampa utan skjerm ved T 0,30. Om tyngdepunktet: LED-lina går ein boge med radius 32 mm og flyttar seg 51 mm frå arbeid til stemning. Det er ikkje ein liten feil i lyset.

## 4 Varme
Eigen modell: Morgan (Nu = 0,48 Ra^¼) for vassrett sylinder, renna som sylinder med same omkrins (56 mm), stråling 4εσT³, 33 % av effekten går ut som lys (100 lm/W), lyset som vert att i hulrommet vert varme (η 0,674 for røyret, 15 % for renna), R′ 0,3 K·m/W frå LED til vegg. For (a) er dei mørke endane (0,26 m kvar side) rekna som finnar.

| | W/m | ε 0,85: h · flate · LED-lodd | ε 0,10 (blank): h · flate · LED-lodd |
|---|---|---|---|
| (a) | 20,9 | 10,0 · 34 °C · 38 °C | 5,9 · 40 °C · 44 °C |
| (b) | 23,0 | 10,7 · 39 °C · 44 °C | 6,5 · **48 °C** · 53 °C |
| (c) | 7,2 | 11,3 · 33 °C · 35 °C | 7,2 · 38 °C · 39 °C |

`mekanikk_ut.py` (Churchill–Chu, finneverknad rundt omkrinsen) gjev same innan 1 K.

**Er kriteriet A ≥ P/(h·ΔT) rimeleg?** Forma er rett: det er energibalansen for ei overflate, og h 10 W/m²K stemmer for eloksert eller lakka alu (10,0–11,3). Tre veikskapar:
1. h 10 føreset ε ≥ 0,8. Blank alu gjev h 6–7, og arealkravet aukar 1,6 gonger.
2. ΔT 30 K gjev 55 °C på ei flate handa tek i under gesten. Det er om lag brannskadegrensa for blank metall ved 10 s (anslag frå EN ISO 13732-1, ikkje lese). Bruk ΔT 20 K (45 °C) for grep og hovud.
3. Kriteriet tel areal som ikkje får varmen (endane i (a), innsida av renna i (c)), og seier ingenting om vegen frå LED til vegg. Lufta i røyret leier nesten ikkje; LED-lina må limast til ein alu-profil som ligg an mot veggen.

Med h 6 og ΔT 20 krev (b) 1093 cm² og har 769. **(b) må difor vere eloksert eller lakka**; blank gjev 48 °C der handa tek. (a) og (c) held med margin i alle fall.

**Trygg effekt per meter** (25 °C rom, langt røyr eller lang renne utan endefinnar):

| | flate ≤ 45 °C | LED-lodd ≤ 60 °C |
|---|---|---|
| røyr Ø44×1,2, ε 0,85 | 35 W/m | 46 W/m |
| røyr Ø44×1,2, blank | 19 W/m | 30 W/m |
| renne 16×20 (berre utsida), ε 0,85 | 20 W/m | 31 W/m |
| renne 16×20, blank | 12 W/m | 21 W/m |

(a) og (b) brukar 21–23 W/m, (c) 7 W/m.

## 5 Gestar
**Vri 0,08 N·m i endegrepet (a/b).** Røyret med spalte har tyngdepunktet 3,3 mm ut frå aksen (R sin β / (π − β)); med LED-modulen 0,10 kg 18 mm ute er ubalansen 0,025 N·m. Friksjonen 0,08 held med faktor 3,2. Det er eit realistisk friksjonsledd (O-ring eller bølgjeskive mot ei bossing), og 0,08 N·m på eit grep Ø52 er eit lett vri. (a) veltar ikkje av eit klyp (λ 23), men lyftar av eit fingerdytt (λ 0,91). (b) kan ikkje velte; armen svikter 1,72 mm (Ø23) eller 1,32 mm (Ø25) under fingeren, og eit reint kraftpar roterer armen 0,012°.

**Vipp 0,20–0,30 N·m (c).** Eit friksjonsledd på 0,2–0,3 N·m er vanleg vare. Med akse i tyngdepunktet held det hovudet i alle vinklar. Gesten veltar ikkje lampa utan skjerm, men tryggleiken er 1,92 (T 0,20) og 1,28 (T 0,30), under kravet 2, og losriving over 0,38 N·m lyftar henne. Med skjermen på foten er λ 3,0–4,5. Med akse i LED-lina veltar ho utan skjerm ved T 0,30 (λ 0,86), og hovudet held ikkje stemningsvinkelen. Gesten krev at handa tek i plate-kanten; ei optisk flate med riller får fingermerke, så hovudet treng eit grep.

**Veltar nokon med éi hand?** (a) ja, om vriet vert eit dytt (2,8 N lyftar). (b) nei. (c) nei med skjerm på foten; utan skjerm på grensa (λ 1,3 ved 0,30 N·m) og ja om aksen ligg i LED-lina.

## Kva det endrar for samanlikninga
- **Masse etter naudsynte rettingar:** (a) 2,4–2,6 kg (meie), (b) 1,0–1,2 kg (Ø25, reell klemme), (c) 3,6 kg (lukka 1,5, fot 8 mm, T 0,20) til 4,2–4,8 kg (T 0,30). (b) er framleis lettast. (a) vert dobbelt så tung.
- **Stivleik:** (c) ser stivast ut i konsept.md (0,2 mm), men er den mjukaste med open U (6–22 mm, 1,9 Hz). Med lukka profil er han stivast att.
- **Stabilitet:** (a) er den einaste som kan velte av sin eigen gest. (b) kan ikkje velte, men krev klemme og glipe mot veggen. (c) står med skjerm på foten, men er under SF 2 utan.
- **(c) har to uløyste geometriske problem** (plata går inn i armen, aksen er ulik i mekanikk og lys) som (a) og (b) ikkje har. Inntil dei er løyste, er stemningstalet for (c) (40 lx på veggen, α −105°) ikkje oppnåeleg.
- **Varme skil dei ikkje.** (c) har størst margin, (b) minst og må ha eloksert eller lakka røyr.

## Rettingar
1. `form04/motor.py` tal_mek(): legg til vridning, θ = T·L/(G·J) med T = F·0,30 for søyle og arm; byt U 100×30×2 til lukka 100×30×1,5. Venta: svikt i enden 0,05 mm, 40 Hz, masse +0,20 kg.
2. `form04/motor.py` kollisjon(): sjekk hovudet mot armen (z ≥ z_s + 0,03 for y ≥ y_s − 0,012). Løys med å heve armen 25 mm (akse i tyngdepunktet) eller 65 mm (akse i LED-lina), eller senk hovudet like mykje. Venta: fri bane til −105°.
3. `form04/motor.py`: vel éin akse. Anten akse i tyngdepunktet og rekn lyset med LED-lina på ein boge med radius 32 mm (I_mot(), _src()), eller akse i LED-lina med motvekt 0,23 N·m over aksen (om lag 0,46 kg 50 mm over) og friksjon ≥ 0,30.
4. `form04/motor.py` fot_t(): kraftpunkt i plate-kanten og sveip over α, ikkje z_s. Venta: 8 mm (T 0,20) eller 14 mm (T 0,30), eller 0,05–0,75 kg stål bak i foten.
5. `form04/motor.py` geometri(): to ekstra opphengspunkt for plata ved x ±0,10, eller 6 mm plate. Venta: nedbøying 0,1 mm i staden for 11,7 mm.
6. `form01/motor.py` tal() og final_tal(): rekn fingerdyttet (3,08 N øvst på grepet) som eit lastfall i tillegg til kraftparet, og legg til meie flattstål 25×5, y 0,01–0,70. Venta: lyftar ved 10,3 N, finger λ 3,3, masse 2,59 kg. Rett svikt-raden i konsept.md: 0,8 mm er eit sidedytt, ikkje gesten.
7. `form02/val.py` tube_arm(): ta med vridning (einingslast med T²/GJ) og set D = 25 mm. Venta: 1,79 mm i spissen, 1,32 mm under fingeren, +0,03 kg. Klemme: 0,8–0,9 kN, M8, pute Ø40, hylse ≥ 40 mm.
8. `felles.py` termisk(): ΔT 20 K i staden for 30 for flater handa tek i, og h etter overflata (10 eloksert, 6 blank). Venta: alle held med eloksert eller lakka alu; (b) blank held ikkje.

## Premissar og uvisse
- 10 N i grephøgd er eit eige premiss (felles.F_PUSH). EN 60598-1 krev etter det eg hugsar berre at ei flyttbar lampe ikkje veltar på 6° skråplan, og det held alle tre. Standardteksten er ikkje lesen.
- Berøringsgrensa 45 °C, bøyefastleik for spon og friksjonstala 0,3 og 0,6 er anslag.
- «U, kvelving hindra» føreset full hindring i rota. Eit gjæra hjørne mellom to opne U gjev mindre, så det verkelege talet ligg mellom kolonnane.
- Skjermen på foten (4 kg i y 0,50) er eit premiss. Står skjermen på ein arm eller ved sida, gjeld kolonnen «aleine».
- Hol bordplate er ikkje rekna.
- Ingen fysiske prøvar. Det billegaste fysiske forsøket er ein 0,75 m lang bit U 100×30×2, festa i botnen slik foten er tenkt festa, med ei 0,3 m stong øvst og 250 g i enden (0,73 N·m). Venta utslag i enden av stonga: 15 mm om festet ikkje hindrar kvelving, 6 mm om det hindrar heilt. Forsøket syner difor òg kor mykje festet held.
