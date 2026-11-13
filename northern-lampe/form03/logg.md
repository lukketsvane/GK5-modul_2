# form03 «Flak» · 2026-11-13

**Grep.** Lyset er ei flate, ikkje ei line. Eit balansert, lysande brett (60 × 25 cm) vippar om midtlina si over skjermen.
**Éi setning.** Eit brett som lyser mjukt nok til å vere synleg, og som du vippar: ned mot arbeidet, bak mot veggen, fram mot andletet.
**Motor.** Fald: fot under skjermen, U-profilsøyle bak han, arm fram over han, brett med fire returfaldar.
**Rekna fridomsgrad.** Vippevinkelen α. Søkt: vippeaksen (yp, zp) og brettdjupna b. 40 av 60 punkt held alle krava (`sok.json`).
**Filer.** `motor.py` · `final.py` · `tal.csv` · `kropp.png` (arbeid · stemning · ansikt) · `studie.png` · `konsept.py` → `../konsept.png`

## Kroppen (yp 0,26 · zp 0,64 · b 0,25)
| Φ LED | W | E snitt | U0 | synleg flate | stemning (25 %) | ansikt 150 lx | vipp | masse | fot | tipp aleine | svikt | kjøl/krav |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1282 lm | 12,8 | 500 lx | 0,77 | 2475 cd/m² (< 3000) | 71 lx på veggen, 90 % | **573 cd/m²** med 297 lm, α +70° | 90° | 2,72 kg | 720 cm² under skjermen | 18,5° | 0,17 mm | 2264/427 cm² |

- Lovene som forma han: returfaldane kuttar svikten i brettkanten frå 0,13 til 0,003 mm. Foten vart 4 mm fordi 3 mm velta under dobbel gestkraft utan skjerm (4,64 mot 4,80 N). Brettet er balansert, så leddet treng berre 0,3 N·m friksjon.
- Dette er første kropp som gjev mjukt ansiktslys (kravet er under 3000 cd/m²).

## Forkasta på vegen (same dag)
1. **Bok** (`bok_forkasta/`): ei ståande falda plate ved sida av skjermen, med LED i leppene. Loddrette flater kastar lyset vassrett, ikkje ned. Ho trong 3,4–4,7 klm, og berre 23–58 % av LED-lyset trefte blada utan optikk. Éi bok gav U0 0,18–0,23. Eit par gav U0 0,5–0,6, men den høgre stod i musesona, og stemninga hamna på bordet (veggdel 0,29–0,39). Paret gav likevel det mjukaste ansiktslyset (650–850 cd/m²).
2. **Lok** (`lok_forkasta/`): brett hengsla i bakkant, som ein laptop. Det slo i veggen på veg bak til stemning (yh + b > 0,73 m), og hengsla måtte halde 1,4 N·m. Den balanserte vippa løyste begge.

## Premissar (nye, ikkje løyste)
- **Optikken er ein premiss.** η 0,70 og topp/snitt 1,3 føreset linsevaska reflektor eller kantlyst leiar. Bok-forsøket syner at ei naken LED-stripe ikkje klarar det. Dette er den største uvissa i (c).
- Skjermen (4 kg) står på foten. Utan skjerm held han akkurat (5,0 mot 4,8 N).
- I arbeid er lysflata synleg for auga med 2475 cd/m². Det er lov etter skjermgrensa (3000), men om det er «ro ved skjermen», må prøvast fysisk.
- I stemning heng brettet loddrett over skjermen, og du ser ryggen på det 10° over augehøgd. Synsfeltkravet (15°) er berre brukt i arbeid.

## Formkritikk
- Forma les som eit **skilt på ein stolpe**: ortogonalt, altså konstruksjon. Vippinga er einaste diagonal.
- Brettet er enden av gesten, ikkje eit lok. Søyla står bak skjermen og syner lite.
- Slektskapen med (b) er nær: det er arm og lysande del. Skilnaden er flate mot line, og at flata kan vere synleg.

## Feil i dokumentet
- Ingen ledd, kabel eller drivar er modellerte. Optikken er ikkje teikna.
- Søyla og armen er rekna for bøying fram/tilbake, ikkje for vridning om søyla når brettet vert dytta i éin ende.
- Tala er ikkje uavhengig kontrollerte enno.
