# Ramme for fase 1

Felles avgjerder og tal for alle fase 1-dokumenta, slik at debrief, 3B, kravspesifikasjon, prosjektplan, bransjeresearch og berekraftshandling seier det same. Vala under er framlegg frå research og må stadfestast av studenten. Tal er henta frå rapportane i `research/` og viser til dei.

## 1. Oppdraget i éi setning

Northern vil ha ei stemningsskapande, men funksjonell lampe for heim og arbeid: heimleg og varm, låg blending, støtte til skjermarbeid og digitale møte, saumlaus overgang mellom stemning og arbeid, gjerne kompakt, flyttbar og oppladbar.

## 2. Reformulering (framlegg)

> Ei lampe som gjer ein plass i heimen til arbeidsplass og attende til heim med éi rørsle, og som legg lyset på flatene rundt skjermen og på ansiktet i staden for i auga. Eigaren skal kunne halde ho i live i tiår.

Grunnlag: halvparten arbeider frå rom som òg er noko anna (`04`), refleksar og blending er hovudproblemet ved skjerm (`04`), og lys på ei flate ved skjermen tener stemning, luminansbalanse og blending samstundes (`03`).

## 3. Målgruppe (framlegg)

- **Primærbrukar:** hybridarbeidaren, om lag 30 til 55 år, som arbeider heime ein til to dagar i veka frå ein plass i eit fleirbruksrom (stove, kjøken, soverom). Ofte i hushald med fleire. Privat kjøp, ikkje arbeidsutstyr.
- **Sekundærbrukarar:** andre i hushaldet som flyttar og brukar lampa, den som reparerer ho (eigaren sjølv eller forhandlar), og den som til slutt skil materiala.
- **Kvifor denne gruppa:** 45,1 % av sysselsette har heimekontor, men berre 5,7 % halve tida eller meir (SSB, 4. kv. 2025). Lampa står ubrukt til arbeid dei fleste dagane og må forsvare plassen sin som stemningslampe. 50 % arbeidde frå fleirbruksrom i 2021 (AFI, sekundærkjelde). Arbeidsgjevar dekkjer sjeldan lys.

## 4. Konfliktane briefen sjølv inneheld

| Konflikt | Tal som viser han | Kjelde |
| --- | --- | --- |
| Stemning mot arbeidslys | 50–200 lm varmt og dempa mot 400–800 lm på arbeidsfeltet | `03` |
| Kompakt mot blendfri | L = Φ / (π · A). 300 lm bak opal treng om lag 320 cm² lysande flate for å halde 3000 cd/m². Målet er under 1000–1500 cd/m² i arbeid og under 500 i stemning, altså endå større flate | `03`, `05` |
| Flyttbar mot vedvarande lys | Éi 21700-celle (17,8 Wh) gjev om lag 12 t ved 100 lm, 4 t ved 300 lm og 2 t ved 600 lm | `05` |
| Attkjenning mot ny fortolking | Ingen av dei 56 Northern-lampene er ei portabel arbeidslampe, og ingen endrar fargetemperatur | `01` |

Kategorien løyser desse med kompromiss kvar for seg: portable designlamper gjev 58–313 lm, arbeidslamper 440–850 lm på kabel, møtelys 250–1000 lm med teknisk uttrykk. Kategoriane overlappar nesten ikkje (`02`).

## 5. Målverdiar (referansar, ikkje lovkrav heime)

| Storleik | Målverdi | Kjelde |
| --- | --- | --- |
| Arbeidsfelt | 500 lx i snitt på om lag 0,6 × 0,4 m, dimbart | `03` |
| Flate ved skjermen (vegg eller reflektor) | 100–150 lx, minst 45 lx | `03` |
| Synleg lysande flate | Under 500 cd/m² i stemning, under 1000–1500 cd/m² i arbeid | `03` |
| Lyskjelde | Ikkje synleg frå sitjande augehøgd (om lag 47 cm over bordet), ikkje spegla i skjermen | `03`, `04` |
| Ansikt i møte | 50–200 lx vertikalt frå lampa (100–300 lx samla), frå stor flate eller indirekte | `03` |
| Stemning | 50–200 lm, varm, avskjerma. Under 10 lx melanopisk EDI ved auget om kvelden. Ingen helsepåstand | `03` |
| Farge | Om lag 1800–3000 K der fargen følgjer dimminga, Ra minst 90 | `01`, `03`, `05` |
| Flimmer | Flimmerfritt i heile dimmeområdet, òg mot kamera (straumregulert eller PWM godt over 10 kHz) | `03`, `05` |
| Installert lys og effekt | Under om lag 1000 lm og 10 W | `03`, `05` |
| Drift | Stemning på batteri, arbeidslys på USB-C. Lampa skal lyse fullt ut på leidning utan batteri | `05`, `06` |
| Vekt og stabilitet | Om lag 0,9–1,2 kg, kontrollert veltevinkel | `07` |
| Pris og volum | 2 990–3 990 kr og nokre tusen i året (tolking, må stadfestast av Northern) | `02`, `07` |

## 6. Berekraftshandling (framlegg)

**Levetid framfor lysutbyte.** Lampa er bygd i lag etter levetid: kropp og skjerm for tiår, lysmodul og kretskort som kan bytast, batteri som forbruksdel. Eigaren byter sjølv batteri og lysmodul med eitt vanleg verktøy, delane er til sals som reservedelar, og lampa lyser fullt ut på leidning utan batteri.

- **Aspektet som blir utfordra:** oppladbare lamper blir kasserte når batteriet eller elektronikken sviktar, år etter kjøpet. Batteriet held typisk 500 syklusar til 70–80 %, LED-modulen 60 000 timar (`05`).
- **Kvifor dette og ikkje lysutbyte:** med norsk straum ligg berre om lag 29 % av påverknaden til ei LED-lyskjelde i bruksfasen. 40 % lengre levetid gjev 21 % lågare påverknad, 40 % høgare lysutbyte gjev 11 % (`06`).
- **Lov og kurs:** reparasjonsdirektivet (EU) 2024/1799 gjeld ikkje lamper. Dei bindande krava er batteriforordninga artikkel 11 (brukarbytbart batteri frå 18.02.2027) og truleg økodesignforordninga 2019/2020 artikkel 4. Handlinga går lenger enn minstekravet (`06`).
- **Tilknyting til Northern:** Snowball oppladbar oppgjev alt utskiftbar LED-modul og batteri, men batteri og LED-modul er ikkje til sals i nettbutikken, og det finst inga rettleiing for byte (`01`, `06`). Handlinga fullfører det Northern har byrja på.
- **Støttetiltak:** éin skrutype og ingen lim, mekanisk brytar utan kvilestraum, metall med dokumentert låg CO2 (til dømes Hydro CIRCAL og skrapbasert stål), materialmerking av alle delar (`07`, `08`, `09`).
- **Måltal (framlegg):** batteri ut på under eitt minutt, lysmodul på under fem minutt, høgst to vanlege verktøy, null limfuger, og vekt per materialfraksjon oppgjeven.

## 7. Northern-formspråket (hypotesar frå `01`)

1. To til tre additive primærformer.
2. Ei tynn linje som ber eit kompakt lyshovud.
3. Lyskjelda er aldri naken.
4. Éin matt farge over heile lekamen.
5. Éin liten messingdetalj som både aksent og betjening.
6. Ei leiken fysisk handling som forklarar namnet.

Palett: pulverlakkert stål eller aluminium, munnblåse opalglas eller opal akryl, messing. Svart, kvit, grå-beige og mørkegrøn. Hardplast er aldri synleg hovudmateriale.

## 8. Det som ikkje er kjent

- Studenten var ikkje med på studieturen. Bedriftsdelen er skrivebordsresearch og skal merkjast som det.
- Det finst inga eiga primærresearch enno. Protokoll for intervju, fotoobservasjon og lampetest står i `04`, lysforsøk i `13`.
- Produksjonsland, årsvolum, målpris og sluttkunde hos Northern er ukjende og må spørjast om.
- Standardtala kviler på sekundærkjelder; NS-EN 12464-1 er ikkje lesen i original.
- Ikkje bruk: namnet «Northern Lighting» som historisk faktum, Pantone-koden 2579 C, eller tala for Dyson og Elgato. Dei er ikkje stadfesta.

## 9. Studenten sine eigne svar

- Læringsmål: lys og optikk, og konstruksjon i Fusion.
- Kapasitet: om lag 40 timar i veka, rundt 150 timar frå 12. november til 7. desember.
- Byggjeressursar: 3D-printar, Arduino, micro:bit, optikken frå ein overheadprojektor, optiske ark frå monitorar. Nesten ikkje budsjett.

## 10. Form på leveransane

- 3B-analysen er brukar, brukssituasjon og bruksmåte (frekvens og sekvens).
- Kravspesifikasjonen er fem kategoriar (estetiske og semantiske, ergonomiske og funksjonelle, tekniske, marknadsøkonomiske, berekraftsmessige) gonger skal, bør og kan. Krava er eigenskapar, ikkje løysingar.
- Debriefen er åtte setningar i eg-form.
- Formlæra blir brukt slik `research/12-formlaere-som-metode.md` viser, innanfor formata til faglæraren.
