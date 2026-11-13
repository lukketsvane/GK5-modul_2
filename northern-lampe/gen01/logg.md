# Gen 01 «Rull» · 2026-11-13

**Grep.** Lyset sit i ei hylse som roterer om éin akse. Overgangen mellom arbeid og stemning er éin vridning.
**Motor.** Sylinderhylse (K = 0) med opning, på rett ryggrad, + støtte (portal · utkrag · T · vugge · lene).
**Rekna fridomsgrad.** Vridvinkelen φ per modus, funnen ved søk i steg på 5°. Alt anna er identitet: støttetopologi, proporsjon L/R, helling, opning (smal/brei/kile/vindauge), hylsemateriale og grunnplan.
**Filer.** `motor.py` (motor + tal() + brett) · `tal.csv` · `brett.png` (4×4) · `kontroll.png` (17 veltar, 18 umogleg) · `kroppar/k01–k18.png`

## Premissar (sjølvlagde, lista ved gen 1)
- Scene: bordplate 1,4 × 0,75 m med vegg bak. Skjerm 55 × 32 cm ved y = 0,45. Auge 45 cm over bordet, 30 cm framfor kanten. Lampa står til venstre for skjermen (side), over skjermkanten (over) eller på arm (arm).
- Arbeid: 500 lx i snitt over 60 × 35 cm og U0 ≥ 0,40 (EN 12464-1, lesing og skriving, lagt på heile sona). Kjelda kan vere synleg eller speglast i skjermen berre om L ≤ 3000 cd/m² (EN 12464-1, skjermgrense).
- Opninga er ei lambertsk kordeflate med jamn luminans (integrerande hulrom, ρ = 0,85). Ingen refleksar utanfor lampa, ingen skugge frå lampa sjølv. Skjermen er einaste hinder.
- Stemning: opninga vend vekk frå auga, mål = del av fluksen som ikkje treffer bordet. Ansikt: 150 lx vertikalt.
- 100 lm/W. Kjøling: A ≥ P/(h·ΔT), der h = 10 W/m²K og ΔT = 30 K. Batteri 21,6 Wh.
- Stenger i stål S235 med SF 2. Tverrsnittet kjem frå momentlova d(z) = (32M/πσ)^⅓, utan w_min. Dytt 10 N.
- Vrid: friksjonsmoment 0,08 N·m, eitt fingerdytt F = T/R ved toppen av hylsa. Tipp ≥ 6° (EN 60598-1, klausulen ikkje sjekka), og F_tipp ≥ 2·F_vrid.
- Finér: 2 × 0,6 mm, ulimt og elastisk rulla, med lagtjukn ≤ 0,03R. Det gjer at finérhylsa kan flatpakkast. Filt sig når L/R > 8. Ein C-klips held berre når opninga < 180°.

## Tal (utdrag frå tal.csv)
| # | kropp | Φ lm | U0 | φ arb | Δφ | sveip | tipp° | F_tipp/F_vrid | svikt mm | P W | kjøl/krav cm² | batt t | flagg |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | overliggar | 1461 | **0.53** | 15 | 165 | fri | 14.7 | 0.34 | 13.2 | 14.6 | 772/487 | – | vrid veltar, vaggar |
| 2 | bøyle | 1348 | 0.15 | −5 | 130 | fri | 50.6 | 1.5 | 3.0 | 13.5 | 218/449 | – | ujamt, for varm |
| 3 | skråportal | 1541 | 0.21 | 40 | 90 | fri | 62.5 | 2.3 | 3.6 | 15.4 | 166/514 | – | ujamt, for varm |
| 4 | gaffel | 1350 | 0.11 | −15 | 150 | fri | 44.6 | **9.5** | 0.8 | 13.5 | 351/450 | – | ujamt, for varm |
| 5 | langarm | **933** | 0.32 | 10 | 170 | fri | 33.1 | 0.52 | 6.7 | 9.3 | 358/311 | – | filt sig, vaggar |
| 6 | arm | 1637 | 0.24 | 10 | 170 | fri | 11.6 | 0.78 | 2.8 | 16.4 | 573/546 | – | ujamt, vaggar |
| 7 | stigarm | 1179 | 0.40 | −25 | 170 | blendar | 26.2 | 1.06 | 3.1 | 11.8 | 457/393 | – | blendar i arbeid |
| 8 | trommearm | 1738 | 0.21 | 10 | 170 | fri | 25.2 | 1.0 | 2.2 | 17.4 | 90/579 | – | for varm |
| 9 | vektstong | 2456 | 0.15 | 10 | 170 | fri | 19.9 | 0.67 | 7.9 | 24.6 | 561/819 | – | for varm |
| 10 | tvillingrør | 1337 | 0.16 | 0 | 125 | fri | 29.0 | 0.72 | 2.8 | 13.4 | 198/446 | – | for varm |
| 11 | skrå-T | 1578 | 0.22 | 5 | 125 | blendar | 42.1 | 1.25 | 2.6 | 15.8 | 147/526 | – | blendar |
| 12 | tvillingtromme | 1380 | 0.12 | −10 | 135 | fri | 18.4 | 2.1 | 1.0 | 13.8 | 303/460 | 1.4 | for varm |
| 13 | vuggestav | 2755 | 0.10 | −85 | 145 | blendar | 35.5 | 0.33 | 0 | 27.6 | 358/918 | 0.7 | blendar |
| 14 | vugge | 1972 | 0.01 | −25 | 175 | fri | 55.0 | 2.7 | 0 | 19.7 | 542/657 | 1.0 | for varm |
| 15 | lenerør | **459** | 0.07 | −25 | 175 | blendar | 71.5 | **11.5** | 0 | **4.6** | 529/153 | **4.2** | i siktlina |
| 16 | lenetromme | 915 | 0.06 | −20 | 170 | blendar | 75.0 | 6.5 | 0 | 9.1 | 102/305 | 2.1 | for varm |
| 17 | *veltar* | 472 | 0.14 | | | | **−25.4** | | | | | | veltar ✓ |
| 18 | *umogleg* | 1305 | | | | | | | | | 77/435 | | finér knekk, held ikkje, for varm ✓ |

Kontrollane slår ut som dei skal: 17 veltar og 18 kan ikkje lagast. Tal() fangar altså begge feilane.

## Veggane søket pressa mot (funn)
1. **Lova for lysfeltet peikar på ei lang, lineær kjelde over oppgåva.** 500 lx frå sida krev 1,3–2,8 klm (13–28 W). Berre overliggaren (1) når U0 ≥ 0,4 med lys i stemningsmodus utan blending. Han har ei 62 cm lang kjelde 60 cm over oppgåva, framfor skjermplanet.
2. **Kjølelova formar lengda.** A_krav = P/300 m². Under ≈ 0,5 m ryggrad held ikkje alu-profilen åleine, med mindre hylsa er av metall. 11 av 16 vert for varme. Kjølelova og lyslova trekkjer same veg: lang.
3. **Det er stivleiken som styrer, ikkje styrken.** Momentlova gjev stenger på 2–8 mm (hårstrå på brettet). Dei sviktar 3–13 mm når handa vrir. Under 2 mm svikt krev om lag Ø10 mm, eller triangulering.
4. **Gesten veltar lampa.** Fingerdyttet F = T/R aukar når R minkar. 9 av 16 tippar før hylsa snur. Låge og tunge kroppar (gaffel, vugge, lene) toler det. Talet vert betre med større R, lågare grep eller eit grep med to fingrar (rein vriding).
5. **Mjukt ansiktslys er utanfor rekkjevidd.** Beste kropp krev 4,6 kcd/m² for 150 lx. Under 3000 cd/m² krev om lag 200 cm² opning. Her er opningane 20–80 cm².
6. **Oppladbar og arbeidslys trekkjer kvar sin veg.** 21,6 Wh gjev 0,7–4,2 t i arbeidsmodus. Berre ei kjelde nær oppgåva (15) held ein halv arbeidsdag, og ho står i siktlina.
7. **Stemningsmålet skil ikkje mellom kroppane.** Den indirekte delen er 0,83–1,00 for alle. Målet må skjerpast, til dømes med veggluminans eller synleg glød ≤ 1000 cd/m².

## Formkritikk med tal
- Nabo-IoU er i snitt 0,25 og høgst 0,57. Silhuettane vandrar, og ingen par ligg over 0,9.
- **Svar på spørsmålet i skillen: rad 1–3 er éin kropp med tolv justeringar.** Alle er rør på hårstong på plate. Identiteten bur i støtta, ikkje i lampa. Rad 4 (vugge, lene) er dei einaste nye kroppane.
- Gesten syner ikkje. Opninga vender ned eller bort frå husstilkameraet, så brettet viser ikkje det lampa gjer.
- Luft i hylsteret (2D): 0,05 for vugge, 0,90 for overliggar.

## Feil i dokumentet
- Første køyring sette liggarane (1, 9) *bak* skjermen. Skjermen skugga heile oppgåva, og Φ_krav vart 153 klm. Det var min premissfeil og ikkje eit funn. Retta til «over» (y = 0,40, h = 0,60).
- Det finst ingen referanse å kalibrere husstilen mot med pikselstatistikk, så brettet er ukalibrert.
- Fingermodellen for vrid er konservativ. Eit tofingergrep veltar ikkje nokon av kroppane.
- Grensa på 6° i EN 60598-1 og kravet om 3000 cd/m² er brukte utan å ha standardteksten framfor meg.
- Kontroll 17: kragen (R + 8 mm) er større enn foten (r = 45 mm). Han er absurd med vilje, men geometrien er ikkje rein.

## Neste
Gen 02 byter motor, fordi settet har stivna i «rør på stong». Lovene peikar alle same veg: ei lang, lineær, høg kjelde framfor skjermplanet, ei stiv støtte og ei opning ≥ 200 cm². Kandidat: **band langs ryggrad**, der éi K = 0-strimle er bere, kjøleflate og skjerm i ein og same kurve. Vridinga vert då vridinga av bandet, (w/2·θ′)²/2 ≤ 0,6 %. Stemningsmålet må skjerpast før køyringa.

## Etterpå, same dag
- Husstilen er endra til **svart bakgrunn** utan golvskugge. `brett.png` og `kontroll.png` er på svart, og dei kvite er tekne vare på som `*_kvit.png`. Skillen er oppdatert.
- Målereiskapen er flytt til `../felles.py`, så gen 02 og seinare generasjonar brukar same tal(). Kryssjekk: Φ_krav frå felles.py er lik motor.py for alle 18 kroppane (`svart.py`).
- Stemningsmålet er skjerpa. Det er no veggdelen E_vegg/(E_vegg + E_bord) ≥ 0,5 ved 25 % fluks, med synleg L ≤ 1000 cd/m². For gen 01 ligg veggdelen på 0,53–1,00 og veggluminansen på 25–121 lx. Målet skil no mellom kroppane: dei låge (13–16) ligg nær grensa, og portalane og armane ligg på 0,77–0,91.

## Lysstudie k01 (overliggar)
`studie_k01.png` vert laga av `../lysstudie.py gen01 1`. Arket viser arbeid og stemning med same kamera og same eksponering. Lyset er rekna per punkt på bord, vegg og skjerm frå opninga, med ρ 0,45 for bordet og 0,75 for veggen. Arket har isolux, polar lysfordeling i snittet og nøkkeltal.
- Arbeid: 1461 lm frå LED, 954 lm ut (η 0,65), 14,6 W, 500 lx i snitt, U0 0,53, luminans i opninga 29 kcd/m². Opninga er skjerma frå auga og frå skjermen.
- Stemning (skjerpa mål): 365 lm, 92 lx i snitt på veggen, 88 % av lyset på veggen. Hylsa er vridd **75°**, ikkje 165°. Det nye målet vel den vinkelen som gjev mest lys på veggen, ikkje den som sender minst ned.
- Feil: omgjevnadslyset (2 % av snittet) er lagt inn berre for at biletet skal lesast og er ikkje med i tala. 2700 K og 2200 K er premissar. Ansiktslyset er ikkje vist; det krev 7,9 kcd/m² og er for hardt.
