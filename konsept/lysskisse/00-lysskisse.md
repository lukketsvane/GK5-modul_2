# Lysskisse på svart

Dato: 13.11.2026. Ein måte å skissere på når det som skal formast, er lyset i rommet og ikkje berre lekamen som lagar det.

**Éi setning.** Teikn rommet slik lampa gjer det: svart er null lys, kvart strøk er lumen, og lampa er ein svart kropp som berre syner seg der ho skuggar eller lyser mot auget.

## Kvifor

Briefen ber om stemning, arbeidslys, låg blending og mjuk overgang. Alt dette er eigenskapar ved rommet. Ei skisse av lekamen på kvitt ark viser ingen av dei, og lekamen vinn over lyset kvar gong. På svart er det omvendt: det einaste som kan teiknast, er lys.

## Fem reglar

1. **Svart er null.** Arket er mørkret. Du kan berre leggje til lys. Viskelêret er ein skjerm.
2. **Lampa er svart.** Kroppen står svart på svart. Han syner seg på to måtar: som silhuett mot det han sjølv lyser opp, og som lysande flate. Ei lysande flate er luminans mot auget. Ei lampe som syner godt i skissa, er anten eit smykke eller ei blending, og talet under seier kva.
3. **Strøket er lumen.** Kvart strøk har fire tal: kvar frå, kvar til, kor breitt, kor mykje. Fire slag: glød, flate, stråle, maske.
4. **Skissa er eit par.** Stemning og arbeid, same rom, same kamera, same eksponering. Det som skal finnast, er overgangen, ikkje dei to endepunkta.
5. **Same tal under alle.** Lux på feltet, jamnheit, lumen for 350 lx, lux på veggen bak skjermen, lux på ansiktet, cd/m² mot auget.

Ryggfiguren høyrer til rommet: brukaren er ein mørk kropp som berre lyset teiknar. Arket på bordet er oppgåva. Skjermen er alltid på.

## Fire strøk

| Strøk | Kva det er | Tal du set |
| --- | --- | --- |
| `glod` | lekam som lyser likt alle vegar | plass, radius, lm |
| `flate` | matt lysande flate | plass, retning, storleik, lm |
| `straale` | retta lys frå ei opning | frå, mot, spreiing, avskjerming, opning, lm |
| `maske` | skarp form avbilda på bord eller vegg | frå, form, lm |

## Fire medium, same reglar

**Motoren (`lysskisse.py`).** Eit lysgrep er fem til ti linjer: strøka i stemning, strøka i arbeid, og ein svart kropp.

```python
def g_retta(m):                      # m er 's' (stemning) eller 'a' (arbeid)
    lm, K = budsjett(m)              # likt budsjett til alle: 100 lm og 400 lm
    if m == 'a':
        lys = [straale(b(0.38, 0.38, 0.40), FELT, lm, K, spreiing=24, kutt=45, opning=(0.20, 0.12))]
    else:
        lys = [flate(b(0.38, 0.50, 0.36), (0, 1, 0), (0.20, 0.12), lm, K)]   # same plate, vend mot veggen
    return lys, [syl(b(0.42, 0.44, 0), b(0.42, 0.44, 0.40), 0.007)]           # svart stamme
```

Legg grepet til i `GREP` og køyr:

- `python lysskisse.py --eitt retta` gjev paret og tala (om lag eitt minutt).
- `python lysskisse.py --px 240 --ss 1` gjev begge bretta som prøve (20 sekund).
- `python lysskisse.py` gjev bretta i full storleik (fleire minutt), `--tal` berre tala, `--sjekk` kontrollen.

Frå 13.11 kan motoren òg rekne ein verkeleg reflektor: eit ark som blir bøygd, falda og klipt (`ark`, `boy`, `fald`, `klipp`), og fresnelspegelen frå overheadprojektoren (`fresnelspegel`). Eit lysgrep er då `g(t)`, der t går frå stemning (0) til arbeid (1), og `overgang(g)` måler heile vegen: blending undervegs, sprang og jamn auke. Bruksrettleiinga står i `API.md`, og formfamiliane ligg i `konsept/reflektor/`.

**Konseptarket (`studie.py`).** Eitt ark per konsept: stemning og arbeid med isolux på bord og vegg, lysfordelinga i snitt, tala mot kravspesifikasjonen, overgangen og kroppen (masse, velt, fot, kjøling, batteri). Dette er lampeverktøyet frå `Documents/northern-lampe` flytta over på grunnlaget til prosjektet: 350 lx og 7,5 W i staden for 500 lx etter kontornorma, og retta og reflektert lys i staden for berre lambertske opningar.

**Fotonsporaren (`../formsok`).** Ein uavhengig modell som gjev same tal innanfor 3 til 6 %, og som kan teikne strålen i lufta. Sjå `../formsok/LESMEG.md`.

**For hand.** Svart papir, kvit og oker fargeblyant. Rekkjefølgja er regelen: først kvar lyset landar (felt, vegg, ansikt), så kvar det kjem frå, og til slutt kroppen, som er det svarte som står att. Skriv dei fire tala attmed kvart strøk.

**Figma.** Svart ramme. Kvart strøk er ein radial gradient med blandingsmodus «Plus lighter», så strøka legg seg saman slik lys gjer. Kroppen er ei svart form øvst.

**På bordet.** Mørkt rom, eige skrivebord i 1:1, telefonlykt som kjelde, papp og dei optiske arka som strøk. Foto frå same punkt over høgre skulder med låst eksponering og kvitbalanse. Lux på feltet med telefonen. Dette er same skisse, og ho prøver modellen.

## Bretta

- `brett-arbeid.png` og `brett-stemning.png`: 16 rom kvar, same rekkjefølgje, utan tekst.
- `brett-arbeid-merkt.png` og `brett-stemning-merkt.png`: same, med namn og tre tal.
- `tal.md` og `tal.csv`: alle tala.

Radene er familiar etter kvar den lysande flata bur: (1) lekamen lyser, (2) rommet lyser, (3) bordet lyser frå under augehøgd, (4) bordet lyser frå høgd eller ved rørsle. Tre er busette referansar (bordlykt, skjermlist, arbeidslampe). Tretten er stega S1 til S12 frå formromkartet.

## Kva bretta viste

Tal ved likt budsjett, 400 lm i arbeid og 100 lm i stemning (modell).

1. **Lysnytta spenner frå 2 % til 94 % ved same watt.** Golvet er 84 lm (350 lx × 0,24 m²). Profilen treng 90 lm for 350 lx, bordlykta 1780 lm og veggvasken 3690 lm. Bordlykta ligg på 5 %.
2. **Ein lekam som gløder, held ingen av luminanskrava.** I stemning gjev 100 lm 637 til 2068 cd/m² mot auget (plate, vend, bordlykt, linsekule). Kravet er 500. Dei som låner veggen, ligg på 51 til 225, og dei som legg ein lysflekk på bordet, på 100 til 444. Ved 350 lx på feltet står bordlykta på om lag 18 000 cd/m², og alle dei retta under 370. Stemninga må lånast.
3. **Skjermen skuggar.** I første køyring stod sju lamper bak skjermplanet. Fem av dei fekk jamnheit under 0,10 fordi skjermen la skugge over delar av feltet. Lyspunktet må stå framfor skjermplanet eller over skjermkanten. Dette stod ikkje i kravspesifikasjonen.
4. **Ingen når jamnheit 0,6.** Best er 0,49 (lyspunkt 60 cm over bordet). Lysøya på 13 cm har 0,18. Høgd er det som hjelper, slik V7 seier.
5. **Veggen bak skjermen får nesten ingenting frå retta lys.** Dei retta gjev 15 til 47 lx, og kravet F6 er 100 til 150. Veggvasken gjev 191 lx av 400 lm, altså om lag 210 lm for 100 lx (V3 sa 220). Arbeidsmodusen treng difor to strøk: 90 til 180 lm på feltet og om lag 210 lm på veggen, i alt 300 til 390 lm og 3,8 til 4,9 W.
6. **Ansiktslys kjem ikkje gratis.** Berre plata lyser på ansiktet (184 lx ved 2546 cd/m²). Feltet kastar lys opp att, men 350 lx på feltet gjev berre 14 til 18 lx på ansiktet.
7. **Dimmar eller overgang.** Likskapen mellom lysfordelinga i stemning og arbeid er 1,00 for bordlykt, plate og arbeidslampe, og over 0,9 for veggvask, lysøy og sidelys. Dei er dimmarar. Under 0,1 ligg profil (0,00), skjermlist (0,03) og retta flate (0,04). Der flyttar lyset adresse.

## Føreseiingar å prøve på bordet

Sette før måling. Telefonlykt, same lykt i alle oppstillingar, lux midt på feltet og foto med låst eksponering.

- P1: Lykta med pappmaske og linse (profil) gjev minst 10 gonger så mange lux på feltet, i snitt over fem punkt, som same lykt i ei kule av kvitt papir (modell 20).
- P2: Jamnheita er under 0,3 med lykta 13 cm over bordet og over 0,4 med lykta 60 cm over (modell 0,18 og 0,49).
- P3: Flyttar du lykta frå 5 cm framfor til 5 cm bak skjermplanet, fell lågaste rute i feltet til under ein femdel (modell 0,30 til 0,00 for profilen).
- P4: Papirkula på Ø 10 cm er minst 3 gonger så lys i biletet som veggflekken frå same lykt (modell 1013 mot 225 cd/m²).

Fell P1 under 5, er sprut og tap i optikken større enn modellen trur, og profilen mistar føremonen sin.

## Val

Alle tre er verkelege overgangar eller nær. Tala er ved 400 lm.

- **(a) Profil** (S4): 94 % lysnytte, 90 lm for 350 lx, 13,5 timar per celle, sol bak skjermen på 225 cd/m², likskap 0,00. Mot: jamnheit 0,30, linse på 40 til 65 mm som ikkje finst i byggjesettet, og luminansen mot auget kviler på antakinga om sprut.
- **(b) Retta flate** (S8): 46 %, 181 lm, 6,7 timar, lågast mot auget av alle (193 cd/m², 87 ved 350 lx), stemning via veggen på 145 cd/m², likskap 0,04. Kan byggjast i dag med prismearka frå LCD-en. Mot: verknaden til arka er ikkje målt.
- **(c) Vend** (S2, frøet som finst): 57 %, 147 lm, 8,2 timar, 494 cd/m² i arbeid. Mot: stemninga er eigen glød på 648 cd/m² ved 100 lm (held 500 først under 77 lm), og likskapen er 0,59.

Uansett val: arbeidsmodusen treng eit veggstrøk attåt (funn 5), og lyspunktet må fram for skjermplanet (funn 3).

## Avgrensingar

- Modell, ikkje måling. Kontrollert mot avstandslova, ei lambertsk skive og kuleluminansen i formromkartet (`--sjekk`).
- Rommet er svart med éin vegg og tak. Romlyset er lågare enn i eit møblert rom.
- ANTAKING: 2 % av lyset lek diffust frå opninga til retta strøk. For små opningar er det dette som avgjer luminansen mot auget.
- ANTAKING: skjermen held 40 cd/m² i snitt. Han er med i bileta, ikkje i tala.
- Likt budsjett er eit val for å samanlikne fordeling. Kolonnen «lm for 350 lx» rettar opp for det.
- Auget står 47 cm over bordet. Kravet F1 gjeld 25 til 60 cm, og det er ikkje rekna.
- Strøka er idealiserte fordelingar. Kva optikk som lagar dei, er neste spørsmål, ikkje dette.
