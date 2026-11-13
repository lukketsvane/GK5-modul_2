# form02 · val (a)/(b)/(c) · 2026-11-13

Alle tre har same lysrøyr (alu Ø44 med opning 60 cm, 2700 K i arbeid og 2200 K i stemning, vri i endegrepet) og same felles tal(). Det som skil dei, er beringa. Designaren vel. Filer: `val.py`, `tal.json`, `val.png`, `kropp_a/b/c.png`.

| | (a) bru | (b) krok | (c) bru, 10° |
|---|---|---|---|
| bering | røyr 1,12 m på to A-bukkar | røyr 0,64 m i eit nav, bøygd alu-røyr Ø23 frå ei klemme på bakkanten | som (a), 6 cm lågare |
| plassering y / h | 0,18 / 0,62 m | 0,25 / 0,62 m | 0,18 / 0,56 m |
| Φ LED · W | 1255 lm · 12,6 W | 1311 lm · 13,1 W | **1054 lm · 10,5 W** |
| U0 | **0,76** | 0,67 | **0,76** |
| stemning (25 %) | 62 lx · 90 % på veggen | **69 lx · 94 %** | 51 lx · 88 % |
| vri arbeid → stemning | 75°, fri | 75°, fri | 80°, fri |
| masse | 1,25 kg | **1,00 kg** | 1,19 kg |
| på bordet | 3456 cm² | **40 cm²** (klemme) | 3456 cm² |
| tipp · grep/T | 18° · 23 | – (klemt) | 19° · 22 |
| svikt | 0,8 mm | 2,0 mm (dimensjonert) | 0,6 mm |
| kjøling (har/krav) | 1433/418 cm² | 769/437 cm² | 1433/351 cm² |
| ansiktslys 150 lx | 4,1 kcd/m² | 5,6 kcd/m² | **3,7 kcd/m²** |

Ansiktslyset krev under 3000 cd/m² for å vere mjukt, og det når ingen av dei.

## Pris per grep
- **(a) → (b):** lampa går frå halve bordet til 40 cm² og vert 0,25 kg lettare. Til gjengjeld trengst 4 % meir lys (sidan røyret sit 7 cm lenger bak), og det må vere ei glipe på 3 cm mellom bord og vegg for klemma. Armen stig bak midten av skjermen og syner 6° over augehøgd, ein Ø23-strek over skjermkanten. **Premissen min på 15° gjeld lyskroppen, ikkje armen. Det er eit val.**
- **(a) → (c):** 16 % mindre lys og 1,4 cm² mindre kjølekrav. Det kostar at røyret sit 6 cm lågare i synsfeltet (10° i staden for 15°). Forma er den same: utslaget er under 5 % av objektmålet og les ikkje. **(c) er ein premiss, ikkje eit konsept.**

## Funn i denne runden
- Ein flat laserskoren platearm (6 mm, breidd frå momentlova og skalert til svikt ≤ 2 mm i planet) vert 18 mm brei ved klemma og 1,7 mm ved spissen. **Han svikter 50 mm sidevegs under grepet.** Ei flat plate ber ikkje gesten, så ho vart bytt ut med eit røyr. Røyret er dimensjonert etter stivleik: Ø23 × 1,5. Spenninga er då 17 MPa, så stivleiken styrer, ikkje styrken.
- (a) fann eit betre punkt enn form01 (y 0,18 i staden for 0,25, med 1255 i staden for 1300 lm). Det kom fram fordi framføtene no er kravde å stå på bordet; i det gamle gitteret kunne dei hamne utanfor bordkanten.

## Feil i dokumentet
- Røyrarmen er dimensjonert berre for bøying. Vridning og ledd ved klemma er ikkje med.
- Klemma er ikkje rekna, og glipa mot veggen er ein premiss.
- (b) er ikkje søkt fram til y 0,18. Ein lengre arm vil krevje eit tjukkare røyr.

## Neste
Til 17.11 trengst tre konsept, og (c) er ikkje eitt. Det tredje må kome frå ein annan motor. Fysisk først: papprøyr Ø44 på 0,56 og 0,62 m ved skjermen (10° mot 15°), og ein Ø23-strek bak skjermkanten for å sjå om armen i (b) les som ro.
