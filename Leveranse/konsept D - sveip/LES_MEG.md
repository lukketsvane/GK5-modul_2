# Sveip · konsept D · rev. A

Éi aluminiumsplate, valsa til eit stadionrøyr på 300 × 300 × 105 mm. Øvst er ringen lukka og blir skjermen. Under er plata skoren bort til høgre, slik at skjermen kragar 122 mm ut over bordet. Stamma står på to botnflensar. Leidningen går ut gjennom eit hakk nede i venstre boge, som i skissa.

All innmat er éin modul som blir senka ned gjennom den opne toppen og skrudd fast med fire skruar nedanfrå. Det finst ingen synlege skruar. Eit messingpunkt ved kneet er berøringsbrytaren.

## Status

| | |
|---|---|
| Digital mekanisk kontroll | **bestått**: 0 kollisjonar i 780 par, klaringar og kontaktar som kravd, innsetjing av modulen, batteriskifte og plugg prøvde (diskret, steg på 10 og 5 mm) |
| Masse og velt | 1117 g (krav F8: høgst 1200 g); veltar først ved 15,3° mot utkraginga (EN 60598-2-4 krev 6°) |
| Slicar | 5 printplater slica i Bambu Studio for P1S, ingen utanfor plata. Verktøybanene er **ikkje** sette over i GUI |
| Fysisk prototype | **ikkje laga** |
| Elektronikk | arkitektur og kandidatdelar valde, **krinsskjema og kretskort er ikkje teikna** |

## Avvik frå skissa, og kvifor

1. **Messingpunkt Ø10** ved kneet (x 165, z 140), framme og bak. Det er brytaren og H5 i formføringa. Lampa er symmetrisk framme og bak, så punktet sit på begge sider.
2. **Føter 3 mm**: lampa står på fire TPE-føter i botnflensane. Kroppen svevar 3 mm over bordet.
3. **Saum**: plata blir sveisa saman med laser-buttsveis midt på den bakre flata i skjermen (x = 213 mm, 132,5 mm lang), slipt og lakkert over. Saumen syner ikkje framanfrå.
4. **Platetjukkleik 1,2 mm** (ikkje 1,5): med 1,5 mm vart lampa 1,23 kg, over F8.

Silhuetten er kontrollert mot skissa med same kamera (`render/sveip_samanlikn.png`): toppkant, venstre kant, indre hjørne, stammekant og hakk fell saman innanfor om lag 1 mm.

## Konstruksjon

| Del | Kva | Framstilling |
|---|---|---|
| D01 kropp | EN AW-5754 H22, 1,2 mm. Blank 716,1 × 307,7 mm. To 180°-bogar Ri 51,3, to botnflensar 90° innover | laserskjering, kantpresse for flensane, valsing/stegbøying av bogane, laser-buttsveis, sliping, matt pulverlakk |
| D02 chassis | 5754 H22, 1,5 mm, fire 90°-bøyar: tak over hakket (med USB-C), vegg, botn (på flensane), rygg (lukkar stamma mot utkraginga), toppflens som ber lysbrettet | laser, kantpresse, PEM-mutrar, lakk |
| D03 lysbrett | 5754 H22, 1,5 mm, flatt, 10 PEM CLS-M3-1 | laser, PEM |
| D04 LED opp | FR-4 1,0 mm, 16 × 3030 2700 K Ra ≥ 90 | kretskort |
| D05 LED ned | MCPCB 1,6 mm D-form, 24 × 3030 3000 K Ra ≥ 90 | kretskort |
| D06 ramme | lysvegg, styrer og klemmer nedkortet, ber nedre diffusor | PC kvit (sprøytestøypt); PETG i prototypen |
| D07, D08 diffusorar | PMMA opal 2,0 mm (ned), 1,5 mm (opp) | laser |
| D09 hovudkort | USB-C-lading med straumdeling, mikrokontroller med berøring, to boost-drivarar | kretskort |
| D10 luke | 5754 H22 1,5 mm, to myntskruar | laser, lakk |
| D11 USB-kort | loddrett USB-C i taket over hakket | kretskort |
| D12/D13 berøringspunkt | messingskive Ø10 pressa i POM-hylse med sneppehakar, smett inn utanfrå | stansa skive, sprøytestøypt hylse |
| D14 berøringskort | på ryggen, to fjørkontaktar mot baksida av messingskivene | kretskort |

**Elektrisk (kandidatar, stadfest i datablad før tinging):** USB-C 5 V (CC-lesing: 1,5 A gjev 7,5 W), ladar med straumdeling TI BQ24074, boost-drivar TI TPS61500 (arbeid) og TI TPS61165 (stemning), mikrokontroller Microchip ATtiny1616 (PTC-berøring), celle Samsung INR18650-35E i Keystone 1043P, cellevern på hovudkortet. Effekt: arbeid 3,8 W, stemning 1,9 W.

**Betening:** kort trykk på messingpunktet slår på og av. Hald inne: lyset glid frå stemningslys (opp, 2700 K) til arbeidslys (ned, 3000 K) og attende (F2).

## Montering og service

1. Innmatsmodulen ned gjennom toppen. USB-C-kontakten i taket skal stå over hakket.
2. Fire ISO 7380 M3 × 6 nedanfrå gjennom botnflensane i PEM-mutrar i chassiset.
3. Berøringspunkta blir smett inn utanfrå til slutt, framme og bak.
4. Fire push-in-føter.
5. Celle og luke (to myntskruar).

Celle ut: to myntskruar, under 1 minutt (B1). Lysmodul: fire skruar nedanfrå, løft innmaten ut, ta av øvre diffusor, éin plugg og fire skruar. Om lag 5 minutt med éin 2,0 mm unbrakonøkkel (B1, ikkje teke tid på). Ingenting er limt (B2).

Rettleiinga ligg i `montering/sveip_montering.pdf`.

## Lys (lysmotoren i `konsept/lysskisse`, same rom som A til D)

| | Tal | Krav |
|---|---|---|
| Arbeidsfeltet 0,6 × 0,4 m, 400 lm ned, lampa snudd så utkraginga ligg inn over feltet | **309 lx i snitt, U = 0,07** | F3: 350 lx, jamt |
| Same, utkraginga vendt bort frå feltet | 32 lx | |
| Lyspol under opninga | 1249 lx snitt, 3911 lx rett under | |
| Kjelda synleg frå augehøgd 47 og 60 cm, 45 cm unna | nei (ein ser 38 og 67 mm ned, diffusoren ligg 95 mm under kanten) | F1 |
| Kjelda synleg når ein lenar seg over (60 cm høgd, 30 cm unna) eller står | ja | F1 |
| Bak skjermen / ansikt | 34 / 34 lx | F6 100 til 150 / F10 50 til 200 |
| Luminans nedre diffusor | 12 100 cd/m² (berre synleg nedanfrå) | F1: 3000 |
| Toppopninga, snitt ved 200 lm | om lag 1420 cd/m² (øvre grense, overslag) | F5: 500 i stemning |

Sveip når ikkje F3, F6 og F10 med denne forma. Lyset kjem ut 17 cm over bordet og blir ein pol, ikkje eit jamt felt (same funn som for Ruta på fot). Tre vegar vidare, ikkje valde: (a) prismearket frå skjermen (brukaren har fleire) under nedre diffusor deler lyset ±30° og jamnar ut polen, må prøvast med lykt; (b) større skala (S = 380 gjev lyset 21 cm over bordet); (c) kalle Sveip sidelys og stemningslys og la arbeidslyset vere ein pol.

## Krav (grunnlag/04-kravspesifikasjon.md)

| Krav | Status |
|---|---|
| E1 heimleg | matt, éin farge, ingen synlege skruar framanfrå (vurdering) |
| E2 Northern | H1 éi primærform, H3 kjelda bak opal, H4 éin matt farge, H5 messingpunkt, H6 «sveip» (hald inne, lyset sveipar frå opp til ned). H2 (tynn line) er broten |
| F1 blending | held frå sitjande augehøgd (rekna), ikkje når ein lenar seg over |
| F2 éi handling | ved konstruksjon, ikkje prøvd |
| F3 arbeidsfelt | **ikkje oppfylt** (309 lx, U 0,07) |
| F4 ≤ 3000 K | ja (2700/3000 K) |
| F8 ≤ 1,2 kg | ja, 1117 g (rekna med lakk og leidningar) |
| F9 ≤ 200 cm² | stamma 175 cm²; heile lampa sett ovanfrå 291 cm² |
| T2 veltar ikkje | ja, 15,3° (rekna) |
| T3 8 t på leidning | ja ved konstruksjon; lysbrettet om lag 39 °C, LED-loddepunkt om lag 43 °C (overslag) |
| T5 / T7 batteri | 18650 12,1 Wh: arbeid om lag 2,8 t, stemning 200 lm om lag 5,6 t (rekna) |
| T6 ≤ 10 hovuddelar | 8 mekaniske deltypar + 5 kretskort |
| T8 40 °C, låg spenning | 5 V; lysbrettet har 1,5 mm luft til kroppen |
| B1, B2, B3, B7 | ved konstruksjon (sjå service) |
| M1, M3 pris | **ikkje rekna** |

## Filer

| Mappe | Innhald |
|---|---|
| `cad/` | `sveip_geometri.py` (parametrar), `sveip_kropp.py` (D01, D02, flatmønster), `sveip_lys.py` (lysmodulen), `sveip_innmat.py` (elektronikk, luke, punkt), `sveip_samanstilling.py` (delregister), `sveip_produksjon.py` (eksport og kontroll), `sveip_flat.py` (DXF), `sveip_teikning.py`, `sveip_rettleiing.py`, `sveip_render.py` (Blender 5.1), `sveip_lystal.py`, `sveip_print.py` |
| `cad/sveip_samanstilling.step` | heile samanstillinga med namn og fargar (AP214); `.glb` for vising |
| `cad/step/` | éin STEP per del (40) |
| `produksjon/dxf/` | flatmønster 1:1: kropp (lag SKJER, BOY, VALS, TEKST), chassis, lysbrett, luke, diffusorar |
| `produksjon/stl/`, `produksjon/sveip_stykkliste.csv` | nett per del og stykkliste |
| `kontroll/sveip_kontroll.json`, `kontroll/sveip_lys.json` | alle kontrolltal |
| `teikning/sveip_teikningar.pdf` | A3: generalarrangement, snitt, sprengd vising med stykkliste, flatmønster |
| `montering/sveip_montering.pdf` | monteringsrettleiing, 8 sider |
| `print/` | slica 3MF for P1S: A skissemodell 1:2 (1,2 t, 78 g), B og C volummodell 1:1 (skjerm 3,0 t, stamme 2,1 t), D ramme og hylser i PETG, E skøyteband; `print_rapport.json` |
| `render/` | `sveip_samanlikn.png` (same kamera som skissa), `sveip_svart.png`, `sveip_lys.png`, `sveip_sprengt.png` |

Køyr frå `cad/` (CadQuery 2.8, `python` 3.11):

```
python sveip_produksjon.py
python sveip_teikning.py
python sveip_rettleiing.py
python sveip_lystal.py
python sveip_print.py A
blender.exe -b -P sveip_render.py -- svart
```

## Opne punkt

1. **Opphavet til skissebiletet er ikkje avklara.** Det liknar eit produktfoto. Køyr eit omvendt biletsøk før forma blir vist offentleg eller til Northern. Biletet ligg berre lokalt (`referanse/.gitignore`).
2. Arbeidslyset (F3, F6, F10): vel veg (a), (b) eller (c) over.
3. Krinsskjema og kretskort for D09, D11 og D14; stadfest delenummer.
4. Prøv berøringa på ein platebit: Ø10 messing i POM-hylse i 1,2 mm aluminium.
5. Spør leverandør om valsing og stegbøying av R51,3 i 1,2 mm 5754 med flensane bøygde først, og om laser-buttsveis i 1,2 mm.
6. Pris (M3) og fargeprøve for pulverlakken.
7. Sjå over verktøybanene i Bambu Studio før print; print A (1:2) først.
