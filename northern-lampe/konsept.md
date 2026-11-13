# Tre konsept · Northern, heim + arbeid · 2026-11-13

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

## Neste, fysisk
- Papprøyr Ø44 på 62 cm, 18–25 cm framfor skjermen (a/b).
- Ei bit Fresnel-linse eller prismeplate under ei LED-stripe, 5 cm unna. Sjå om stripene og vifta på bordet held seg.
