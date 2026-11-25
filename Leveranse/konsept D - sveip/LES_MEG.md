# Sveip · konsept D · rev. B

Éi aluminiumsplate, valsa til eit stadionrøyr på 300 × 300 × 105 mm. Øvst er ringen lukka og blir skjermen. Under er plata skoren bort til høgre, slik at skjermen kragar 122 mm ut over bordet. Stamma står på to botnflensar. Leidningen går ut gjennom eit hakk nede i venstre boge, som i skissa.

All innmat er éin modul som blir senka ned gjennom den opne toppen og skrudd fast med fire skruar nedanfrå. Skruane sit under føtene. Ein messingknapp nede på foten, framme og bak, er berøringsbrytaren. Lampa er lik framme og bak, så ho kan snuast slik at utkraginga ligg inn over arbeidsflata.

## Status

| | |
|---|---|
| Digital mekanisk kontroll | **bestått**: 0 kollisjonar i 861 par; klaringar og kontaktar som kravd; innsetjing av innmaten (steg på 0,5 mm dei siste 10 mm), batteriskifte og plugg prøvde diskret; hola i flatmønsteret kontrollerte mot 3D |
| Masse og velt | 1158 g (F8: høgst 1200 g). Veltar ved 12,7° mot utkraginga, rekna med effektiv fotkant (EN 60598-2-4 krev 6°). Eit trykk på knappen vippar lampa først ved 7,0 N; ho glir før (5,7 N ved μ 0,5) |
| Varme (overslag) | lysbrett 36 °C, LED-loddepunkt 39 °C, kropp 26 °C ved 25 °C rom |
| Slicar | 5 plater slica i Bambu Studio CLI for P1S, ingen utanfor plata. Verktøybanene er **ikkje** sette over i GUI |
| Fysisk prototype | **ikkje laga** |
| Elektronikk | spesifikasjon i `elektro/SPESIFIKASJON.md`; **kretskorta er ikkje teikna** |

## Revisjon B: kva den kritiske gjennomgangen fann

Fem uavhengige granskarar gjekk gjennom rev. A (68 funn, 11 kritiske). Dette er retta i CAD-en:

- **Flensane og valsinga:** flensane startar no 27,5 mm frå bogen (x = 80), så venstre boge kan valsast med flensane bøygde først. Flensen er 16 mm, hola er spor 3,4 × 5 med 5,1 mm til bøyen. K = 0,42 i flensbøyen.
- **PEM i chassiset:** mutrane sit 6,3 mm frå kanten (krav 4,8). Alle er CLS-M3-2 i 1,5 mm plate. Fotholet som skar gjennom bøyen er borte: føtene sneppar over skruehovuda.
- **Saumen** ligg i nasen på skjermen (x = 300) med påløps- og avløpsflikar. Lampa er dermed lik framme og bak.
- **Toleransar:** klaring til kroppen 2 til 3 mm, fire glideputer i POM som styrer innmaten, D = 105 ±0,3 kalibrert i sveisefikstur (merknad på teikninga). Ryggen i chassiset har fått sideflensar (U-profil).
- **Berøringspunktet:** messingknapp CuZn37 (blyfri, klarlakk) med krage Ø12,8 × 0,4 som stopp, pressa i ei POM-hylse med sneppehakar i eit Ø12,3-hol. Fjøra ligg mot baksida av skaftet med 0,8 mm forspenning og når ikkje kroppen når knappen er ute. Knappen er flytt ned på foten (z 70), så eit trykk ikkje vippar lampa.
- **Lysmodulen:** ramma blir skrudd ovanfrå i gjengeinnsatsar, så diffusoren og nedkortet kan leggjast i først. Øvre diffusor står 28 mm over LED-ane på nylonavstand (ingen sneppar i PMMA).
- **Cella** er no 21700 i polarisert haldar, 1,5 mm frå kortet, med trekkband og 30 mm opning. Luka har myntskruar med 2 mm hovud.
- **Kontrollen** reknar velt med effektiv fotkant og trykk på knappen. Han har eit termisk nettverk med leiing gjennom chassiset og éi felles effektkjede for lumen, watt og driftstid. Han kontrollerer òg hol i flatmønsteret mot 3D.
- **Elektro:** cellevern, sikring, vern mot feil polaritet, fastvarereglar for USB-C, LED-strengar, demping, ESD og jording, to berøringskanalar og regelverk står i `elektro/SPESIFIKASJON.md`.

Ikkje retta: platetjukkleiken (granskaren tilrår 1,5 mm for stivleik og kjensle; det gjev om lag 1,28 kg og bryt F8), og spalta på 2 mm mellom innmaten og kroppen som ein ser inne i hakket. Funn 52 (prosessprofil for feil skrivar) var feil: «0.20mm Standard @BBL X1C» er oppgitt som kompatibel med P1S.

## Avvik frå skissa

1. Messingknapp Ø12,8 nede på foten (x 165, z 70), framme og bak. Formføringa (07) seier «eitt lite, rundt messingpunkt … på foten».
2. Føter på 3 mm: kroppen svevar 3 mm over bordet.
3. Saum i nasen på skjermen (132,5 mm, slipt og lakkert).
4. Platetjukkleik 1,2 mm.

Rendra med same kamera som skissa (`render/sveip_samanlikn.png`) fell proporsjonane saman med skissa innanfor om lag 1 %.

## Lys (lysmotoren i `konsept/lysskisse`, same rom som A til D)

| | Tal | Krav |
|---|---|---|
| Arbeidsfeltet 0,6 × 0,4 m, 400 lm ned, utkraginga inn over feltet | **309 lx i snitt, U = 0,07** | F3: 350 lx, jamt. **Ikkje oppfylt** |
| Same, utkraginga vendt bort | 32 lx | |
| Kjelda frå augehøgd 47 og 60 cm, 45 cm unna | skjult (ein ser 38 og 67 mm ned, diffusoren ligg 84 mm under kanten) | F1 |
| Kjelda når ein lenar seg over eller står | synleg | F1 held berre sitjande |
| Bak skjermen / ansikt | 34 / 34 lx | F6, F10: **ikkje oppfylt** |
| Øvre diffusor ved 200 lm / nedre ved 400 lm | 2400 / 12 100 cd/m² i snitt | F5: **ikkje oppfylt** når ein ser flata |

Lyset kjem ut 17 cm over bordet og blir ein pol (1249 lx snitt under opninga). Midten av polen ligg ved x = 0,39 m, utanfor den høgre kanten av feltet (0,30).

### Prismearket frå skjermen under nedre diffusor (`cad/sveip_prisme.py`)

Strålesporing med `konsept/film/film.py` (90°-prisme, n 1,57 etter domen i `konsept/vindauge/film/arket.md`). Opalen er lambertsk, og lys som arket kastar attende, går tilbake til opalen og det kvite kammeret og kjem ut att (resirkulering R). Lux er rekna direkte og skalert mot lysmotoren. Berre opal gav 303 lx direkte, mot 309 lx i lysmotoren.

| Variant, 400 lm frå opalen | R 0,5 | **R 0,7 (truleg)** | R 0,85 | U |
|---|---|---|---|---|
| Berre opal | 309 lx | 309 lx | 309 lx | 0,04 |
| Prismearket, prismesida opp mot opalen, riller langs y | 313 | **364** | 416 | 0,04 |
| Same, riller langs x | 126 | 147 | 169 | 0,00 |
| To ark i kryss | 107 | 145 | 194 | 0,00 |
| Prismesida ned, slik arket låg i skjermen | 131 | 153 | 174 | 0,11 |
| Sagtann 40/50 (eige ark), rett veg | | 397 | | 0,04 |

Dom: arket med prismesida opp og rillene på tvers av utkraginga flyttar den eine loben inn på feltet og løftar snittet med om lag 18 % (sagtann om lag 29 %). Med R 0,7 når snittet 350 lx (F3 sitt lux-tal), men jamnheita blir ikkje betre: U er 0,04 mot 0,6. Den andre loben går til spille utanfor feltet. Andre retningar gjer det verre. Eit ark kan ikkje jamne ut eit felt på 0,6 × 0,4 m når kjelda sit 17 cm over bordet ved sida av det. Det krev ei kjelde høgare og over feltet, altså ein annan lampetype. Arket er gratis (brukaren har fleire), 0,16 mm tjukt og passar på leppa i ramma under diffusoren. Det er ikkje med i CAD-en enno. Prøv først med lykteprøva P1 i `arket.md` og ein lux-app på telefonen. Tala ligg i `kontroll/sveip_prisme.json`, kartet i `render/sveip_prisme.png`.

## Krav (grunnlag/04-kravspesifikasjon.md)

| Krav | Status |
|---|---|
| E2 Northern | 6 av 7 på skalaen i 07 del 6: kjerne 5 (R1 éi form, R2 konstant tverrsnitt, R3 kjelda bak opal, R4 éin lakkfarge, R5 messing på foten), palett 1, proporsjon 0 (ny silhuettype). Endra med vilje: ny funksjon (to lys i eitt sveip), ny silhuett (valsa plate som kragar ut), ny handling (hald fingeren på) |
| F1 / F3 / F5 / F6 / F10 | sjå lys |
| F2 éi handling | ved konstruksjon, ikkje prøvd |
| F8 ≤ 1,2 kg | 1158 g (rekna med lakk, leidningar og tillegg) |
| F9 ≤ 200 cm² | stamma 175 cm²; heile lampa sett ovanfrå 291 cm² |
| T2 veltar ikkje | 12,7° (rekna) |
| T3 / B3 på leidning | fullt arbeidslys med USB-C-kjelde på 1,5 A og C-til-C-leidning; med standardstraum om lag 40 % |
| T5 / T7 batteri | arbeid 2,9 t, stemning 200 lm 4,2 t (aldra celle 3,4 t: T7 fell då) |
| T6 ≤ 10 hovuddelar | 9 mekaniske deltypar + 5 kretskort = 14: **ikkje oppfylt** |
| T8 | kroppen 26 °C (overslag); 5 V inn, høgst om lag 30 V internt (SELV) |
| B1, B2, B7 | celle ut under 1 min med mynt; lysmodul om lag 5 min med éin 2 mm unbrako (ikkje teke tid på); ingenting limt |
| M1, M3 pris | **ikkje rekna** |

## Filer

| Mappe | Innhald |
|---|---|
| `cad/` | `sveip_geometri.py` (parametrar), `sveip_kropp.py` (D01, D02, flatmønster), `sveip_lys.py` (lysmodulen), `sveip_innmat.py` (elektronikk, luke, knapp, føter), `sveip_samanstilling.py` (delregister), `sveip_produksjon.py` (eksport og kontroll), `sveip_flat.py` (DXF og 1:1-mal), `sveip_teikning.py`, `sveip_rettleiing.py`, `sveip_render.py`, `sveip_lystal.py`, `sveip_print.py` |
| `cad/sveip_samanstilling.step`, `.glb` | samanstillinga med namn og fargar |
| `cad/step/` | éin STEP per del |
| `produksjon/dxf/` | flatmønster 1:1 (lag SKJER, BOY, VALS, PEM, TEKST) |
| `produksjon/sveip_stykkliste.csv` | stykkliste per stykk, med kabelsett, termoputer og typeskilt |
| `produksjon/sveip_D01_kropp_mal_1til1_A3.pdf` | 1:1-mal av kroppen på fire A3-ark |
| `kontroll/sveip_kontroll.json`, `sveip_lys.json` | alle kontrolltal |
| `teikning/sveip_teikningar.pdf` | A3: generalarrangement, snitt, sprengd vising med stykkliste, flatmønster |
| `montering/sveip_montering.pdf` | montering og service, 8 sider |
| `elektro/SPESIFIKASJON.md` | krav til kretskorta |
| `print/` | slica 3MF for P1S (sjå `print_rapport.json`) |
| `render/` | samanlikning med skissa, svart, lys på, sprengd |

Køyr frå `cad/` (CadQuery 2.8):

```
python sveip_produksjon.py
python sveip_teikning.py
python sveip_rettleiing.py
python sveip_lystal.py
python sveip_print.py A
blender.exe -b -P sveip_render.py -- svart
```

## Opne punkt

1. **Opphavet til skissebiletet er ikkje avklara.** Biletet liknar eit produktfoto. Køyr eit omvendt biletsøk før forma blir vist offentleg eller til Northern. Biletet ligg berre lokalt.
2. Arbeidslyset (F3, F5, F6, F10).
3. Kretskorta etter `elektro/SPESIFIKASJON.md`.
4. Prøvestykke: berøringa med messingknapp i POM-hylse i 1,2 mm lakkert aluminium, sneppehakane, og laser-buttsveis i 1,2 mm 5754 i streiflys.
5. Leverandør: valsing av R51,3 med flensane bøygde, kalibreringsfikstur, tilbod (M3).
6. Fargeprøve for pulverlakken (grå frå Northern-paletten).
7. Sjå over verktøybanene i Bambu Studio. Print A (1:2) først.
