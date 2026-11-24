# Sveip rev. B · elektrisk spesifikasjon

Kretskorta D09 (hovudkort), D11 (USB), D14 (berøring), D04 og D05 (LED) er **ikkje teikna**. Dette dokumentet er kravet dei skal teiknast etter. Delenummer er kandidatar og må stadfestast i datablad før tinging.

## 1. Blokkskjema

```
USB-C (D11) ── TVS + ESD på CC ── 5 V ─┐
  CC1/CC2 ──────────── ADC (MCU) ──────┤
                                       BQ24074 (lading + straumdeling, ILIM styrt)
21700 ── PTC 3 A ── vern (BQ2970 + 2 x N-FET) ── P-FET mot feil polaritet ── BAT
                                       │ OUT 3,0–4,4 V
                     ┌─────────────────┼─────────────────┐
              TPS61500 (ned, 3 x 8)  TPS61165 (opp, 2 x 8)  ATtiny1616 (PTC, PWM, ADC)
                     │                 │                     │
                  J4 → D03/D05      J4 → D04            J5 → D14 (S1, S2, GND)
```

## 2. Celle og vern (kritisk funn i gjennomgangen)

- Celle: Li-ion 21700 utan vernekrets (Samsung INR21700-50E, 4900 mAh, 3,6 V, 17,6 Wh). Haldar Keystone 1121, polarisert.
- Vernet sit på hovudkortet: vern-IC av BQ2970-klassen med dobbel N-FET. Grenser: overspenning 4,25 til 4,30 V, underspenning 2,8 V, overstraum 4 til 5 A, kortslutning ≥ 10 A.
- PTC eller smeltesikring om lag 3 A i serie med cella.
- Vern mot feil polaritet: P-FET i BAT-greina (R_DS(on) ≤ 20 mΩ, om lag 40 mW ved 1,4 A).
- NTC (10 k) på undersida av D09 rett over cella, med termopute. TS-nettverket i BQ24074 skal stoppe ladinga ved 0 °C og 45 °C. Stadfest V_HOT og V_COLD i databladet.
- Fastvara: ikkje lad når cellespenninga ved innsetjing er under 2,5 V eller over 4,25 V. Ladegrense 4,10 V for lengre levetid.
- Merking: lasermerk «+ →», «Li-ion 21700 3,6 V» og batterisymbol på luka D10 og ved haldaren.
- Sperresone på undersida av D09 over cella (x 87 til 153, y ±12): ingen kopar, vias eller THT-bein. I tillegg 0,1 mm polyimid (T4).
- Fraktmodus: vernekretsen eller ein FET som blir vekt av VBUS. Alternativt: cella blir send utanfor haldaren med ein papirlapp mellom pol og kontakt.

## 3. Straumbudsjett og fastvarereglar

| Kjelde (CC-lesing) | Inn | Tak for LED-skinna | Merknad |
|---|---|---|---|
| Default (0,2 til 0,66 V) | 2,5 W | 2,2 W | om lag 40 % arbeidslys, eller stemning |
| 1,5 A (0,66 til 1,23 V) | 7,5 W | 6,5 W | arbeid åleine fullt (5,45 W), lading med resten |
| 3 A (> 1,23 V) | 15 W | 6,5 W | BQ24074 gjev høgst 1,5 A uansett |

- EN1 og EN2 på BQ24074 står til USB500 ved oppstart. MCU les CC1 og CC2 med ADC og løftar inngangsgrensa først når kjelda har meldt 1,5 A.
- Sveipet er komplementært: summen av dei to kanalane går aldri over taket i tabellen.
- Utan celle (B3) går lampa rett frå USB gjennom straumdelinga. Fullt arbeidslys krev ei 1,5 A-kjelde og ein C-til-C-leidning (E01).
- Effektkjeda (sjå `kontroll/sveip_kontroll.json`, «effekt»): arbeid 400 lm ut gjev 4,80 W LED og 5,45 W frå skinna. Stemning 200 lm ut av toppen gjev 3,31 W LED og 3,76 W. Føresetnadene er 150/140 lm/W, opal 65/70 %, boost 88 %, og må målast.
- Driftstid på 21700 (15,9 Wh brukbart): arbeid 2,9 t (2,3 t aldra), stemning 4,2 t (3,4 t aldra).

## 4. LED-strengar, demping og flimmer

- D05 (ned, 3000 K, Ra ≥ 90, R9 > 50): 24 × 3030 som 3 strengar à 8 i serie, om lag 23 V. Éin straumspegel eller seriemotstand per streng, slik at Vf-spreiing ikkje fordeler straumen ujamt.
- D04 (opp, 2700 K, Ra ≥ 90): 16 × 3030 som 2 strengar à 8.
- Kandidatar for diodar: Nichia 757-serien (R9050) eller Samsung LM301B (S90). Stadfest bin, Vf og lm/W ved 50 til 60 mA og 60 °C.
- Utgangsspenninga skal vere ≤ 30 V for margin (TPS61500: maks 38 V).
- Demping: analog (PWM filtrert til FB eller CTRL) ned til om lag 10 %, og PWM på ≥ 20 kHz under det, ned til 2 % (F7).
- Boost-drivarane skal ikkje gå i pulsutelating i bruksområdet. Mål Pst^LM og SVM ved 100, 50, 10 og 2 % (T1). Etter gjennomgangen er grensene i 2019/2020 skrivne for nettdrivne lyskjelder, så T1 er eit eige krav her, med målemetoden over.
- Open-LED-flagg: drivarane skal vere av når J4 manglar (vern når lysmodulen blir bytt).

## 5. Berøring, ESD og jording

- To kanalar: messingknappen framme og bak går til kvar sin PTC-kanal (J5: S1, S2, GND). Fastvara ser bort frå samtidig berøring på begge, sidan det tyder at nokon løftar lampa.
- QTouch «max on duration» skal vere lengre enn den lengste sveiptida (F2: under 10 s).
- D14: seriemotstand 1 til 4,7 kΩ og ESD-diode med låg kapasitans (< 1 pF) mot GND rett ved fjørkontakten.
- D11: TVS på VBUS (5 V-klasse) og ESD-diodar på CC1 og CC2.
- Jord: kroppen er éin flate i aluminium. Han blir kopla til GND gjennom chassiset: tannskive under éin K09-skrue på ein umaskert flekk i flensen, og W5 frå chassiset til GND på D09. Kontaktflatene mellom flensen og chassisbotnen blir maskerte under lakkinga.
- Prøv ±8 kV luft og ±4 kV kontakt (IEC 61000-4-2) på knapp, kropp og plugg før korta blir frosne.

## 6. Spenningar og tryggleik

- 5 V inn. Høgst om lag 30 V DC internt på LED-strengane (SELV, ES1). Klasse III.
- Kroppen og chassiset er tilgjengelege leiande delar på GND. Ingen uisolert leiar på kretskorta skal liggje nærare kroppen enn 3 mm. Hovudkortet ligg 21 mm frå kroppen og opp-kortet 23 mm.

## 7. Regelverk som må kartleggjast før sal

- EN IEC 60598-1:2024 med vedlegg W (batteridrivne armaturar) og EN 60598-2-4 (berbare bordlamper, velt 6°).
- EN 62031 (LED-modular), EN 62471 (fotobiologisk tryggleik), EN 55015 og EN 61547 (EMC), RoHS.
- (EU) 2019/2020 og 2019/2015: D04 og D05 er lyskjelder. Dei skal registrerast i EPREL, energiklassen skal stå i bruksrettleiinga, og lyskjeldene skal kunne takast ut (fire skruar).
- (EU) 2023/1542 art. 11 (brukaren byter cella, med vanleg verktøy) og art. 13 (merking) frå 18.02.2027, og produsentansvar for batteri.
- UN 38.3 / UN3481 for frakt med celle.

## 8. Service

1. Trekk ut USB-C.
2. Opne luka (to myntskruar) og ta ut cella med trekkbandet.
3. For lysmodulen: lirk ut dei to messingknappane (fingernegl under kragen), skru ut fire skruar nedanfrå og løft innmaten ut gjennom toppen.
