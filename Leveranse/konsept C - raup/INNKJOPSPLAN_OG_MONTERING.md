# RAUP · Komplett Innkjøpsplan, Stykkliste (BOM) og Produksjons-/Monteringsmanual (1:1 · H = 200 mm)

Dette dokumentet spesifiserer **eksakt kva som må kjøpast inn** (med delenummer, dimensjonar, norske/europeiske leverandørar og prisar for både 1-stk prototyp og 50-stk pilotserie) og korleis de monterer den ferdige, salgs- og produksjonsklare **RAUP**-lampa.

---

## 1. Komplett Innkjøpsliste (Shopping List / COTS & Eigenproduksjon)

Maskinlesbar CSV-versjon ligg i [`kontroll/raup_innkjopsliste.csv`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/kontroll/raup_innkjopsliste.csv).

### A. Eigenproduserte strukturdelar (3D-print på Bambu Lab P1S / Støyp / Laserskoren DXF)

| Pos | Del / CAD-fil | Kva de må kjøpe / bestille | Leverandør (Noreg / EU) | Pris 1 stk (Prototyp) | Pris/stk ved 50 stk (Sal) |
| :--- | :--- | :--- | :--- | ---: | ---: |
| **01** | **Hovudskal (2,5 mm vegg)**<br>[`cad/raup_skal.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_skal.step)<br>[`print/RAUP_P1S_H200_2.5mm_fuzzy.3mf`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/print/RAUP_P1S_H200_2.5mm_fuzzy.3mf) | **P1S-prototyp:** 1 rull *Bambu PLA Matte Ivory White (#11100)* eller *Desert Tan (#11401)* (`220,5 g` per skal = 4 skal per 1 kg rull).<br>**Papirmasse-produksjon:** `116 g` tørr resirkulert cellulose-/bomullsfiber + `2 %` AKD våtstyrkelim + matt akrylforsegling, støypt i [`raup_stoypform_minus_Y.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_stoypform_minus_Y.step) / [`pluss_Y.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_stoypform_pluss_Y.step). | Polyalkemi.no / 3DNet.no / Bambu Lab EU | **65 kr** | **22 kr** |
| **02** | **Botnchassis med batterivugge, PCB-piedestall, LED-sokkel og 1,40 mm diffusorspor**<br>[`cad/raup_botn_chassis.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_botn_chassis.step)<br>[`print/RAUP_P1S_H200_chassis_og_klips.3mf`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/print/RAUP_P1S_H200_chassis_og_klips.3mf) | **P1S-prototyp:** *Bambu PETG HF Black/Gray* eller *PLA Matte Charcoal (#11101)* (`~53 g` per chassis).<br>**Sal / Serie:** CNC-frest eller presstøypt *EN AW-6061-T6* svart-/bronseeloksert aluminium etter `raup_botn_chassis.step`. | Polyalkemi.no (filament) / Xometry.eu (CNC alu) | **16 kr** | **115 kr** |
| **03** | **Stålballastplate (5,0 mm S235JR, ~140 g)**<br>[`cad/raup_ballast.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_ballast.step)<br>[`produksjon/raup_ballast_1til1.dxf`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/produksjon/raup_ballast_1til1.dxf) | **Laserskoren 5,0 mm S235JR stålplate** (`108,4 × 113,4 × 5,0 mm`, ferdig med 3× `Ø3,4 mm` M3-hol og nøkkelutsparingar rundt piedestallane). Last opp `raup_ballast_1til1.dxf` direkte. *(Prototyp-alternativ: fyll hulrommet rundt piedestallane med stålsand/blyhagl + epoksy til ~145 g).* | Xometry.eu / LaserTrykk / Lokal stålverkstad | **95 kr** | **28 kr** |
| **07** | **Avviklingsbar 1,0 mm optisk diffusorplate (`139,5 × 189,0 mm`)**<br>[`cad/raup_diffusor.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_diffusor.step)<br>[`produksjon/raup_diffusor_1til1.dxf`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/produksjon/raup_diffusor_1til1.dxf) | **Primær (Sirkulært ombruk):** Optisk diffusor-/prismefilm (`0,8–1,0 mm` opal PC/PMMA + BEF-folie) frå kassert 24"–32" LCD/LED-skjerm (1 skjerm gir nok film til 4–6 lampar).<br>**Kommersiell backup:** `1,0 mm` *Makrolon / Lexan Opal Diffuser PC-plate* + *Lee Filters 216 White Diffusion*, skoren etter `raup_diffusor_1til1.dxf`. | El-retur / IT-avdeling (0 kr) / Plastkompaniet / RS Components | **0 kr** | **24 kr** |
| **08** | **Skånsam boga styreklips (`1,60 mm` ikkje-klemmande spor)**<br>[`cad/raup_filmklips.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_filmklips.step) | Printast på samme P1S-plate som botnchassiset (`1,6 g` PETG/PLA Charcoal) + `20 mm` strimmel av `0,3 mm` silikon-/PTFE-glidetape inne i sporet. | Printast saman med pos 02 | **3 kr** | **2 kr** |

---

### B. Elektronikk, Lyskjelde og Batteri (Hyllevare / COTS)

| Pos | Del / CAD-fil | Eksakt spesifikasjon og delenummer å kjøpe | Antall | Leverandør | Pris 1 stk | Pris 50 stk |
| :--- | :--- | :--- | :---: | :--- | ---: | ---: |
| **04A** | **18650 Li-ion Battericelle**<br>[`cad/raup_batteri_21700.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_batteri_21700.step) | **Keeppower P1835J (3,6V / 3500 mAh / 12,6 Wh)** med innebygd Seiko PCM-vern (overlading, djup-utlading og kortslutningsvern, IEC 62133-2) eller **Samsung INR18650-35E** (`Ø18,4 × 65,2 mm`). Gir **~5,5–6 t på 100 % (2,2 W)** og **25–40 t på stemningslys (0,3–0,5 W)**. | 1 stk | Batterionline.no / Elfa Distrelec / Kjell & Co | **109 kr** | **58 kr** |
| **04B** | **Batterikontaktar til chassisvugga** | **Keystone Electronics 5209** (eller **Keystone 209**) fornikla fjørstål-bladkontaktar for 18650 (festast i endevegane av den integrerte batterivugga i `raup_botn_chassis`). *Alternativ:* **Keystone 1042P** 18650-holder (DigiKey `36-1042P-ND`). | 2 stk | DigiKey.no (`36-5209-ND`) / Mouser.no (`534-5209`) | **18 kr** | **9 kr** |
| **05** | **USB-C Lader + Trinnlaus Touch/Trykk PWM-Dimmar PCB**<br>[`cad/raup_drivar_pcb.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_drivar_pcb.step) | **Val A (Alt-i-eitt 32 × 14 mm):** *1S 3.7V Li-ion USB-C Touch/Push Stepless PWM LED Dimmer & TP4056/ETA9640 Charger PCB* (med minnefunksjon og > 4 kHz flimmerfri PWM).<br>**Val B (Modulært frå norsk lager):** *Adafruit BQ24074 USB-C Charger med Load-Sharing (#4755, DigiKey `1528-4755-ND`)* eller *Kjell & Co TP4056 USB-C (`87-194`)* + *TTP223 / SGL8022W kapasitiv touch-PWM-dimmar* (sensoren limast på innsida av den `2,5 mm` veggen så lampa dimmast ved berøring av skalet!). | 1 sett | DigiKey.no / Mouser.no / Kjell & Company | **69 kr** | **29 kr** |
| **06A** | **Vertikal LED-kjølesøyle**<br>[`cad/raup_led_berar.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_led_berar.step) | **Eloksert aluminiumsprofil EN AW-6063-T5, `12,0 × 5,5 mm`** (eller standard `12 × 6 mm` / `15 × 6 mm` flat-/U-profil frå byggevare), kappa til **`107,4 mm` lengd**. Stikk rett ned i den integrerte vertikale sokkelen i `raup_botn_chassis`. | 1 stk (`107,4 mm`) | Bauhaus / Maxbo / Sløyd-Detaljer / Biltema | **10 kr** | **6 kr** |
| **06B** | **High-CRI 95+ Varmkvit COB LED-stripe** | **8 mm brei 5V COB LED-stripe, 2700K Varmkvit, CRI (Ra) ≥ 95, 320 LED/m** (`100 mm` aktiv lengd = `~2,2 W` maks / `~220 lm`, 3M termisk teip på baksida som limast i det `8,2 × 0,9 mm` frontsporet på `06_raup_led_berar`). | 0,10 m (`100 mm`) | DigiKey.no / Elfa Distrelec / BTF-Lighting (`BTF-5V-320-8MM-2700K`) | **15 kr** | **9 kr** |
| **13** | **Kabling + USB-C Ladekabel** | `0,4 m` *22 AWG (`0,35 mm²`) silikonisolert fleksibel koblingstråd* (raud + svart) + Ø2 mm krympestrømpe + `1,5 m` *tekstiltrukken USB-C ladekabel* (varmgrå/lin). | 1 sett | Kjell & Company / DigiKey.no / Biltema | **39 kr** | **18 kr** |

---

### C. Festemateriell, Magnetlås og Møbelføter

| Pos | Komponent | Eksakt spesifikasjon | Antall | Leverandør | Pris 1 stk | Pris 50 stk |
| :--- | :--- | :--- | :---: | :--- | ---: | ---: |
| **09** | **Messing gjengeinnsatsar (Heat-Set Inserts)** | **Ruthex RX-M3x5.7** (`M3 × 5,7 mm`, for `Ø4,0 mm` hol — smeltast inn med loddebolt ved 210 °C for fastskruing av stålballast, LED-søyle og klips). | 5 stk | Polyalkemi.no / 3DNet.no / Amazon.de | **8 kr** | **4 kr** |
| **10** | **Maskinskruar (svarteloksert / A2 rustfri)** | **3× M3 × 10 mm forsenka unbrakoskruar (ISO 10642 / DIN 7991)** (frå undersida av botnchassiset gjennom stålballasten) + **2× M2,5 × 8 mm sylinderhovud (ISO 4762)** (låser LED-søyle og filmklips). | 5 stk | Biltema / Clas Ohlson / Würth / RS | **6 kr** | **2 kr** |
| **11** | **Skjult skall-låsing (Magnet / Friksjon)** | **6× Neodymmagnetar Ø6 × 2 mm (N42)** (3 par mellom registerflensen på `raup_botn_chassis` og innsida av `raup_skal`) *eller* **3× 1,5 mm silikon-friksjonsputer** på registerflensen (verktøyfri opning ved batteribyte!). | 1 sett | Kjell & Co / Supermagnete.de / Clas Ohlson | **15 kr** | **6 kr** |
| **12** | **Sklisikre møbelføter** | **4× 3M Bumpon SJ5312** (`Ø10,0 × 2,0 mm` sylindriske polyuretan-føter). Passer eksakt i dei 4× `Ø10,4 × 0,6 mm` lommene på undersida av `raup_botn_chassis` og gir **1,4 mm svevande skuggefuge** mot bordplata. | 4 stk | Elfa Distrelec (`300-59-140`) / Kjell & Co | **8 kr** | **3 kr** |
| **SUM** | **KOMPLETT RAUP-LAMPE (1:1)** | **Alle 8 CAD-delar + elektronikk + batteri + festemateriell** | **1 lampe** | **Total BOM-kostnad** | **476 kr** | **335 kr** |

---

## 2. Steg-for-steg Ferdigstilling og Montering

1. **3D-print / produser strukturdelane:**
   - **Plate 1 (Hovudskal):** Skriv ut [`print/RAUP_P1S_H200_2.5mm_fuzzy.3mf`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/print/RAUP_P1S_H200_2.5mm_fuzzy.3mf) på Bambu Lab P1S i *Bambu PLA Matte Ivory White / Desert Tan* (`2,5 mm` vegg, `6` veggløkker, `0 %` fylling, ekte 3D mikro-struktur + Contour Fuzzy Skin + skarp debossed skuggelinje ved `z = 37,78 mm`). Fjern tre-støtta under det bakre `37,78 mm` innspranget.
   - **Plate 2 (Botnchassis + Filmklips):** Skriv ut [`print/RAUP_P1S_H200_chassis_og_klips.3mf`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/print/RAUP_P1S_H200_chassis_og_klips.3mf) i *PETG HF* eller *PLA Matte Charcoal* (`0,16 mm` laghøgd, `4` veggløkker, `25 %` gyroid-fylling, **utan** fuzzy skin for eksakte mekaniske pasningar).
2. **Monter stålballast og føter i botnchassiset (`02` + `03`):**
   - Legg den laserskorne `5,0 mm` S235 stålballastplata ([`produksjon/raup_ballast_1til1.dxf`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/produksjon/raup_ballast_1til1.dxf)) ned over dei tre integrerte piedestallane (batterivugge, PCB-piedestall og LED-sokkel) i `02_raup_botn_chassis`.
   - Skru fast med **3× M3 × 10 mm forsenka skruar** frå undersida av botnchassiset, og lim inn **4× 3M Bumpon SJ5312 (`Ø10 × 2 mm`)** i dei fire forsenka fotlommene på undersida (`z = 0`).
3. **Monter elektronikk, batteri og LED-kjølesøyle (`04` + `05` + `06`):**
   - Lim den `100 mm` lange **8 mm CRI 95+ 2700K COB LED-stripa** inn i det `8,2 × 0,9 mm` frontsporet på den `107,4 mm` lange elokserte aluminiumsprofilen (`06_raup_led_berar`), og før tilførselskablar (`22 AWG`) ned gjennom bakrillene til sokkelen.
   - Stikk `06_raup_led_berar` ned i den vertikale sokkelhylsa i `02_raup_botn_chassis` (med COB-stripa vendt ut mot diffusorsporet) og lås med M2,5-skrue.
   - Fest **Keystone 5209** fjørkontaktar i batterivugga, lodde `B+ / B-` og `LED+ / LED-` til **USB-C / PWM-dimmar-PCB-et (`05_raup_drivar_pcb`)**, fest PCB-et på piedestallen og klikk inn **18650 Li-ion-cella (`04_raup_batteri_21700`)**.
4. **Sett på hovudskalet og den boga diffusorfilmen (`01` + `07` + `08`):**
   - Før hovudskalet (`01_raup_skal`) ned over den `8,15 mm` høge innvendige registerflensen på `02_raup_botn_chassis` til skalet kviler på den `0,8 mm` tilbaketrekte skuggefuge-hylla ved `z = 3,5 mm`.
   - Skjer ut diffusorplata etter [`produksjon/raup_diffusor_1til1.dxf`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/produksjon/raup_diffusor_1til1.dxf) (`139,5 × 189,0 mm` med `R = 16,3 mm` avrunda hjørne), sett filmklipsen (`08_raup_filmklips`) på brua ved spiralmunningen, og skyv den `1,0 mm` optiske diffusorfilmen ned i det `1,40 mm` boga sporet i diffusorfoten.
