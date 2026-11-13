# Tre konsept · Northern, heim + arbeid · 2026-11-13

> **Granskinga vart pausa 13.11.2026 på grunn av vekegrensa.** Funna er rekna opp att med eigen kode, og dette er stadfesta: prisme P1–P7, fotometri F1–F5 og R-a2, mekanikk M1–M7 og premiss PR1–PR4, PR6, PR7 og PR14. P1, F2, M4 og M5 fall i storleik eller form. Det står att å stadfeste PR8, PR13 og PR15, og deretter å rette koden og skrive sluttkritikken. Granskinga kan takast opp att frå cache.

> **(a) bru, (b) krok og (c) prisme er no referansespor.** Konsepta til Moodle 17.11 er A Skiva, B Over og C Vindauge i `../konsept/tre/`. Det granskinga her fann som gjeld dei, står i «Til A Skiva, B Over og C Vindauge» nedst.

Alle tre er rekna i same scene med same tal() (`felles.py`): 500 lx i snitt på arbeidsflata med U0 ≥ 0,4, inga blending over 3000 cd/m², og stemning med 25 % lys der minst halvparten skal på veggen. Bilete: `konsept.png` og lysstudiane `form01/studie.png` og `form04/studie.png`. (c) er no **prisme** (form04); det førre (c), flak, ligg i form03. Designaren vel.

| | (a) bru | (b) krok | (c) prisme |
|---|---|---|---|
| éi setning | Eit alu-røyr som ber, kjøler og lyser, på to bukkar over arbeidsplassen. | Det same røyret, hengt frå éin arm som klemmer på bakkanten. | Ei klar plate der kvar rille er rekna frå lyslova, under ein stødig overhead-arm. |
| lysprinsipp | line, skjerma opning | line, skjerma opning | line, **retta** gjennom prismeplate |
| gest | vri endegrepet 75° | vri endegrepet 75° | vipp hovudet 105° |
| Φ LED · effekt | 1255 lm · 12,6 W | 1311 lm · 13,1 W | **433 lm · 4,3 W** |
| jamnleik U0 | 0,76 | 0,67 | 0,69 |
| luminans mot auga | skjerma | skjerma | 11 cd/m² |
| **lys på skjermen** | **611 lx** (maks 1118) | **652 lx** (maks 1392) | **9 lx** (maks 37) |
| stemning | 62 lx på veggen · 90 % | 69 lx · 94 % | 40 lx · 100 % |
| ansiktslys 150 lx | 4,1 kcd/m², for hardt | 5,6 kcd/m², for hardt | 0,66 kcd/m² i snitt, mjukt |
| batteri 21,6 Wh | 1,5 t | 1,5 t | **4,5 t** |
| masse | 1,25 kg | **1,00 kg** | 3,11 kg |
| på bordet | 3456 cm² | **40 cm²** | 720 cm², under skjermen |
| står | tipp 18° | klemt | tipp 22° utan skjerm |
| svikt under gesten | 0,8 mm | 2,0 mm (bør vere Ø25, sjå under) | 0,2 mm |

## Det som skil dei
- **(a)** rammar inn arbeidsplassen. Han er enklast å lage, men tek mest bord og lyser 600 lx på skjermen.
- **(b)** er lettast og tek minst plass. Armen syner over skjermkanten, og han lyser òg 650 lx på skjermen.
- **(c)** treng ein tredjedel av lyset, lyser nesten ikkje på skjermen og gjev mjukt ansiktslys. Han er tyngst, og optikken er rekna, men ikkje prøvd.

## Gransking (uavhengig, avbroten)
Granskinga stoppa på bruksgrensa før rapportane vart skrivne. Delresultata i `gransking/*.json`:
- **Stadfesta:** Φ og U0 for (a), (b) og det gamle (c) er rekna om med eigen kode, med avvik under 0,1 %. Med eit tettare gitter vert Φ om lag 5 % lågare og U0 0,72 i staden for 0,76 for (a). Gitteret er grovt, men konklusjonen held.
- **Nytt funn:** tal() målte ikkje lyset på skjermflata. (a) og (b) lyser 610–650 lx i snitt på skjermen, og det gjev slør og mindre kontrast. Det var difor eg rekna det for prisma (9 lx).
- **(b):** med vridning og eigenvekt svikter armen Ø23 2,3 mm ut av planet. Ø25 trengst (1,8 mm). Klemma må halde om lag 500 N, eller 1000 N med SF 2.
- (a) tippar ved 2,9 N fram/bak i grephøgd. Det er ikkje eit problem med vridegrepet, men ved eit dytt.

## Mot briefen
- **Stemning og arbeid i same produkt:** alle tre, med éin gest.
- **Låg blending og ro ved skjermen:** (c) er klart best (9 lx på skjermen). (a) og (b) skjermar kjelda, men lyser på skjermen.
- **Varm fargetemperatur:** 2700 K i arbeid og 2200 K i stemning er premiss for alle.
- **Reparasjon og materialseparasjon:** ikkje rekna. (c) har to materiale (alu og PMMA), som kan skiljast ved å skru.
- **Miljøtiltak:** (c) brukar ein tredjedel av energien og kan gå på batteri. (b) brukar minst aluminium.
- **Ansiktslys:** berre (c).

## Uvisse og feil
- Lysmodellen har ingen refleksar i rommet og ingen skugge frå lampa sjølv.
- Optikken i (c) er rekna stråle for stråle, men med anslag for tap og strølys. Ansiktslyset er snitt, ikkje topp.
- Premissar som set forma og ikkje er prøvde: siktlinevolumet, synsfeltet (≥ 15°), musesona og stemning på 25 %.
- Standardgrensene er brukte utan standardteksten framfor meg.

## Til A Skiva, B Over og C Vindauge
Kvart funn er rekna opp att med eigen kode av minst éin motbevisar (`gransking/stadfest_*.py`). Det som gjeld for A, B og C:

**Prismeplata held lyset borte frå skjermen, men det er optikken som gjer det, ikkje forma.** Same vifte i (a) gjev 4 lx på skjermen (premiss.md). Plata sjølv gjev 9 lx i fjernfeltet og 14 lx (maks 33) i nærfeltet. For B, som har fresnelplata, betyr det fem ting:
1. **Rekn plata i 3D**, med Snell på vektorform. Skeive strålar møter ein høgare effektiv brytingsindeks og blir bøygde for mykje. Vifta smalnar ytst, og jamnheita fell frå 0,69 i snittet til 0,38–0,41 (P2, held hjå to motbevisarar). Er B rekna i snittet, kan 0,41 vere for høgt.
2. **Stigeveggane i rillene blendar.** Dei sender lys mot brukaren, med ein topp på 25 000 cd/m² over 1 mm når plata er blank og 2 000–2 400 med 4° mattering. Slipp på veggane tek toppen ned til 280–450 og kostar berre om lag 4 % av lyset (P1, P4). Ei ferdig fresnelplate har faste veggar, så snu rillesida bort frå auget og mål plata med lykta.
3. **Ansiktstoppen ligg langt over snittet**: 2 600–4 000 cd/m², mot eit snitt på 659. Under 3000 krev 6–8° mattering, ikkje 4° (P3). Det er same knapp som diffusorarket i B.
4. **Lysstripa syner gjennom renna** når auget står 3–5 cm lågare eller nærare enn modellauget, med 48 700 cd/m². Renneveggane må gå 6–7,5 mm under lina (P5).
5. **Sjekk sveipet når plata vippar.** Prismeplata gjekk inn i armen frå −51°, og stemninga fall frå 40 til 20 lx (P7). B vippar plata over skjermkanten og bør sjekke sveipesylinderen mot stolpen og skjermen.

**Gitter.** Veggsnittet på 8 × 6 punkt var 19–23 % for lågt for (a) og (b), men berre 7 % for (c), fordi smale lysband fell mellom radene (F5, P7). Feilen er ulik frå konsept til konsept, så rangeringa kan snu: (c) såg ut til å gje 65 % og så 40 % av stemningslyset til (a), men på arealsnitt er det 53–56 %. Veggen bør difor reknast som arealsnitt med celler på 4 cm eller mindre. 7 × 5 punkt på bordet er om lag 5 % konservativt og held.

**Skjermlys.**
- **Slør.** L = ρE/π. Med ρ 0,04 gjev 611 lx eit slør på 7,8 cd/m², og kontrasten fell til 26:1. Med ρ 0,01 er han 94:1 (F1). Med same rekning (kvit 200 og svart 0,2 cd/m²) gjev A sine 115 lx i arbeid om lag 120:1, og 131 lx midt i overgangen, skalert til 350 lx på feltet, gjev 108:1 (om lag 100:1). Svart blir då 8 og 9 gonger lysare.
- **Leppe.** Ei leppe på 30 mm på veggsida og 5 mm på brukarsida tok skjermlyset i (a) frå 611 til 10–24 lx, og i (b) frå 652 til 52–83 lx. Kostnaden var 7–26 % meir fluks, og kjelda vart skjult for alle 8 augepunkta (R-a2). For A, som legg 0,33 av feltet på skjermen, er ein kant på skjermsida av skiva same grep.
- **Spegling i skjermen.** reflected() rekna med loddrett skjerm. Når skjermen er tilta 15,5–18°, ser brukaren opninga i (a) og (b) spegla i skjermen med 920–1 070 cd/m² (F3). A, B og C har ikkje rekna spegling. B, med plata over skjermkanten, og A, med skiva bak skjermen, bør sveipast for tilt 0–20°.
- **Augevolum.** Tre augepunkt er for få. Funnet fall i storleik, for godset i opningskanten skjermar meir enn granskaren rekna med, men kravet om å sjekke eit volum står (F2). Bruk ±15 cm sidevegs, 15 cm fram og 10 cm i høgd.

**Stemning.** 25 %-regelen straffar konsept som brukar lite straum i arbeid (F5). Sett heller fast veggluminans, 10 cd/m². Då treng (a) 1,7–1,8 W, (b) 1,5–1,8 W og (c) 1,1–1,35 W. Den faste watten på 1,25 W i stemning for A, B og C ligg nær dette. Rapporter gjerne L̄_vegg.

**Ikkje stadfesta enno:** mekanikkfunna M1–M7, mellom anna at (a) lettar ved eit fingerdytt på 2,8 N. A og B bør sjekke tipp ved eit dytt i grephøgd.

## Neste, fysisk
- Papprøyr Ø44 på 62 cm, 18–25 cm framfor skjermen (a/b).
- Ei bit Fresnel-linse eller prismeplate under ei LED-stripe, 5 cm unna. Sjå om stripene og vifta på bordet held seg.
