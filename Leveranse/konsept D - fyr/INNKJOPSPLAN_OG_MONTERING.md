# FYR · innkjøp og montering

Maskinlesbar liste: `kontroll/fyr_innkjopsliste.csv`. Monteringsrettleiing med teikningar: `montering/FYR_montering.pdf`.

## Prenta delar (prototype)

| Pos | Del | Komponent | Spesifikasjon | Tal | Leverandør | Pris 1 stk | Pris 100 stk |
|---|---|---|---|---|---|---|---|
| P1 | 01+04 | Fot og mantel (to halvdelar) | Bambu PLA Matte mørk raud (nærast oksebloddraud i Matte-serien); serie: RAL 3005 | 1 | Bambu Lab EU / 3DNet / Polyalkemi | ca 100 | - |
| P2 | 05+05b | Hylse med fotring | Bambu PLA Silk+ gull (messinglook) | 1 | Bambu Lab EU | ca 30 | - |
| P3 | 03+10+06d | Chassis, glidering og mastfot | Bambu PETG HF svart | 1 | Bambu Lab EU | ca 25 | - |
| P4 | 07 | Lysrist (ugjennomsiktig kvit) | Bambu PETG HF kvit; sjekk at 0,8 mm vegg ikkje lyser gjennom (T < 0,05), elles t 1,2 og deling 17 | 1 | Bambu Lab EU | ca 25 | - |

## Lys

| Pos | Del | Komponent | Spesifikasjon | Tal | Leverandør | Pris 1 stk | Pris 100 stk |
|---|---|---|---|---|---|---|---|
| E1 | 06b+06c | LED-stripe 5 V COB 8 mm RA90 | BTF-LIGHTING DC5V USB FCOB 8 mm 320 LED/m RA90, 2700 K (spesifisert; næraste lagervare hos BTF er 3000 K), 7 W/m; side 158 mm + topp 4 x 25 mm | 1 | btf-lighting.com / Amazon.de (B0B24LRXWD, 3000 K) | 45-100 | ca 10 |
| H6 | 08 | Lok (opal diffusor) | PLEXIGLAS Satinice WH02 3 mm, laserskoren Ø76,4 (prototype) / Ø78,6 (serie); prototype-alternativ: diffusorark frå monitor | 1 | laserteneste / plateleverandør | 30-60 (NV) | 10 (NV) |
| H7 | 06 | Lysstav | aluminium flatstål 15 x 2 x 1000 (kapp 193, ingen hol); baksida mattsvart (måling eller eloksering); limt i mastfoten og i klypa på rista (H11) | 1 | Hornbach / Bauhaus / Biltema | 30-60 | 8 (NV) |

## Elektro

| Pos | Del | Komponent | Spesifikasjon | Tal | Leverandør | Pris 1 stk | Pris 100 stk |
|---|---|---|---|---|---|---|---|
| E2 | 12 (SW1, SW3) | Mikrobrytar, gullkontakt (glødevegane) | Omron D2F-01L3 (simulert rullearm; 0,1 A maks / 1 mA min); -D3 = loddeterminal | 2 | Mouser 653-D2F-01L3 / DigiKey SW859-ND / TME | ca 20 per stk | ca 14 per stk |
| E3 | 12 (SW2) | Mikrobrytar, sølvkontakt (sidelys) | Omron D2F-L3 (2 A / min 100 mA ved 5 V) | 1 | Mouser / DigiKey / TME | ca 20 (NV) | ca 14 (NV) |
| E4 | 14 (R1) | Motstand, svak glød | 91 ohm 0,25 W metallfilm (prøv 82 / 91 / 100 på benken) | 1 | Elfa Distrelec / Kjell & Co | 2 | 0,5 |
| E5 | 14 (R3) | Motstand, full glød (parallelt med R1) | 33 ohm 0,25 W metallfilm (prøv 27 / 33 / 39) | 1 | Elfa Distrelec / Kjell & Co | 2 | 0,5 |
| E6 | 14 (F1) | Sjølvtilbakestillande sikring | PTC 0,5 A hald / 1 A løys, minst 6 V (t.d. Bourns MF-R050 eller Littelfuse RXEF050) | 1 | Elfa Distrelec / DigiKey | 5 (NV) | 2 (NV) |
| E7 | 13 | 3,5 mm TRS-kontakt, panel | 3-pol stereo panelkontakt med M6-bøssing og mutter, loddeterminal | 1 | Kjell & Co / Elfa Distrelec | 20 (NV) | 8 (NV) |
| E8 | 06d | 3,5 mm TRS-plugg | 3-pol stereo plugg, slank loddeutgåve utan skal: skaft Ø3,5 x 14, loddekropp innanfor Ø6 x 14 (lomma i mastfoten er Ø6,1 serie / Ø6,3 prototype); limt med epoksy | 1 | Kjell & Co / Elfa Distrelec | 15 (NV) | 5 (NV) |
| E9 | - | Kabel | 2 x 0,2 mm² (AWG 24) med USB-A-plugg, 2 m, tekstil svart, ytre Ø3,5-4,0; sløyfemotstand maks 0,4 ohm | 1 | prototype: kapp ein USB-A-kabel; serie: kabelleverandør (NV) | 0-60 | ca 25 (NV) |
| E10 | 14 (J1) | Kontakt kabel-kort | JST PH 2-pol: PHR-2 + B2B-PH-K-S + 2 x SPH-002T-P0.5S | 1 | Elfa Distrelec / DigiKey | 5 | 2 |
| E11 | 14 | Hullkort og leidning | hullkort 24 x 15; leidning 0,2 mm² raud/svart 0,5 m; krympestrømpe | 1 | Kjell & Co | 15 | 4 |
| E12 | 06b+06c+06d | Leiarar i lysmodulen | leiar AWG 28 (0,08 mm²) silikon eller PTFE: raud TOPP+ 0,4 m, blå SIDE+ 0,2 m, svart GND 2 x 0,4 m (éin frå kvar stripe) + ca 0,1 m til bøylane mellom dei fire toppbitane (06c i parallell); gjennom golvet i rista og kanalen bak staven til loddeøyra på pluggen | 1 | Elfa Distrelec / Kjell & Company | ca 50 (NV) | ca 3 (NV) |

## Festemiddel

| Pos | Del | Komponent | Spesifikasjon | Tal | Leverandør | Pris 1 stk | Pris 100 stk |
|---|---|---|---|---|---|---|---|
| H1 | 03 | Gjengeinnsats | Ruthex RX-M3x5.7 (hol Ø4,0 x 6,7) | 3 | Polyalkemi / 3DJake | 8 | serie: innpressa i SLS-delen |
| H2 | 01-03 | Knappskrue fot-chassis | ISO 7380 M3 x 16 A2 svart | 3 | Würth / Biltema / Clas Ohlson | 6 | 1 |
| H3 | 05c | Stoppskrue hylse | ISO 7380 M3 x 5 A2 svart; skjer gjengene sjølv i Ø2,5-holet (hovudet søkk i røyret, spissen i sporet i tappen) | 3 | Würth / RS | 5 | 1 |
| H4 | 12 | Brytarfeste | ISO 7045 M2 x 10 + ISO 4032 M2-mutter + skive | 6 | Würth / Biltema | 6 | 1 |
| H11 | 06+06d+07 | 2K-epoksy for lysmodulen | 2-komponent epoksy, 5 min open tid (t.d. Loctite EA 3430 eller UHU Plus Schnellfest): pluggkroppen i lomma, staven i mastfoten, rista på staven | 1 | Biltema / Clas Ohlson / Würth | ca 100 (NV) | ca 2 (NV) |

## Fot

| Pos | Del | Komponent | Spesifikasjon | Tal | Leverandør | Pris 1 stk | Pris 100 stk |
|---|---|---|---|---|---|---|---|
| H10 | 11b | Silikonsnor for bajonetten | silikon O-ringsnor Ø2 mm, 3 bitar à 10 mm i lommene under mantelen (forspenning, trykk ned og vri) | 1 | Tameson / 123bearing / Biltema | 10 (NV) | 0,5 (NV) |
| H5 | 11 | O-ring | 85 x 3 silikon 60 ShA (alternativ NBR 70 ShA) | 1 | Tameson / 123bearing | 15 (NV) | 4 (NV) |

## Berre prototypen

| Pos | Del | Komponent | Spesifikasjon | Tal | Leverandør | Pris 1 stk | Pris 100 stk |
|---|---|---|---|---|---|---|---|
| H8 | 04 | Lim for falsen i mantelen | 2-komponent epoksy (eller CA), berre prototypen | 1 | Clas Ohlson / Biltema | 20 | - |
| H12 | 10 | CA-lim for gliderringen | cyanoakrylat (sekundlim), gliderringen i toppen av mantelen; berre prototypen (serien: presspassing) | 1 | Biltema / Clas Ohlson | ca 50 (NV) | - |

## Seriedelar

| Pos | Del | Komponent | Spesifikasjon | Tal | Leverandør | Pris 1 stk | Pris 100 stk |
|---|---|---|---|---|---|---|---|
| S01 | 01 | Fot | EN AW-6082 T6 dreia Ø99 x 14; 3 sylinderstift ISO 8734 Ø2,5 x 14 m6 som bajonettknastar (hol Ø2,5 H7 bora radielt frå lomma med vinkelhovud, utstikk 1,45); 3 stift ISO 8734 Ø3 x 12 m6 (hol H7) som stolpar for strekkavlastinga (pressa opp gjennom golvet i lomma, flukt med botnen); pulverlakk RAL 3005 fin struktur matt, sporet maskert | 1 | CNC-verkstad (NV) | - | NV |
| S04 | 04 | Mantel | røyr EN AW-6060 T66 90 x 2 (lager: Voss / lemu), kappa 263; 6 spalter med røyrlaser 3,4 (ferdig 3,2 etter lakk) + 3 L-spor; pulverlakk RAL 3005 inne og ute, øvste 8 mm maskert for gliderringen | 1 | røyrlaser + pulverlakk | - | NV |
| S05 | 05 | Hylse | CuZn37 0,8 mm plate, laserskoren flatmønster 260,4 x 222,7 (K 0,5), valsa til Ø83,7, buttskøyt på 225° (bak, mellom kronegruppene; laser- eller sølvlodda), børsta rundt + klarlakk | 1 | platelaser + valseverkstad (NV) | - | NV |
| S05b | 05b | Fotring | POM-C sprøytestøypt; radielle M3-hol med innsats eller gjenge | 1 | sprøytestøyping (NV), SLS PA12 under 500 stk | - | NV |
| S03 | 03 | Chassis | SLS PA12 svart | 1 | MJF/SLS-teneste | - | NV |
| S07 | 07 | Lysrist | SLS PA12 kvit (rista kan ikkje støypast i eitt drag) | 1 | SLS-teneste | - | NV |
| S10 | 10 | Glidering | POM-C delt ring Ø86 / Ø84 x 6 | 1 | dreiing eller støyping | - | NV |

## Koplingsskjema

```
USB-A 5 V --+-- F1 (PTC 0,5 A) --+--+--+                     X1 (3,5 mm TRS)
                                  |  |  |
                                  |  |  +-- SW1 (D2F-01L3, gull) -- R1 91 Ω --+-- TOPP+  (tupp)
                                  |  +----- SW3 (D2F-01L3, gull) -- R3 33 Ω --+
                                  +-------- SW2 (D2F-L3, sølv) ----------------- SIDE+  (ring)
GND -------------------------------------------------------------------------- GND    (hylse)
```

SW1 er lukka 0 til ca 84°, SW3 0 til ca 73°, SW2 0 til ca 62° (kamsporet under fotringen). Gullkontaktane ber berre glødestraumen (under 40 mA), sølvkontakten ber sidestripa (ca 220 mA), innanfor kvar sitt område i Omron-databladet.

## Montering i kortform

Same steg og same rekkjefølgje som i `montering/FYR_montering.pdf`.

1. Smelt dei tre gjengeinnsatsane (H1) inn i chassisflensen nedanfrå med loddebolt, på temperaturen innsatsprodusenten tilrår for materialet.
2. TRS-kontakten (13) opp under navet på elektronikkdekket; M6-mutteren oppå navet blir trekt til med ein 8 mm fastnøkkel frå sida, mellom søylene.
3. Skru dei tre brytarane (12) til brakettane under toppdekket med M2 x 10 utanfrå og mutter innanfor (H4), armen opp gjennom slissa. Berre lett til.
4. Lodd kortet (14: R1, R3, F1, JST PH) og leidningane etter skjemaet; kortet ligg på armen bak.
5. Trer kabelen (E9) inn gjennom holet bak i foten og trykk han ned i ein S rundt dei tre stolpane i lomma (på motsett side av kvar stolpe). Skrell kappa rett etter siste stolpe, før leiarane opp gjennom holet i chassisflensen og forbi armen bak, og krymp JST-pluggen på.
6. Set chassiset på foten (bogetappen under flensen fell ned i lomma og sentrerer) og skru det fast nedanfrå med 3 x M3 x 16 (H2).
7. Strekk O-ringen (11) inn i sporet under foten.
8. Press gliderringen (10) inn i toppen av mantelen (prototype: lim med CA).
9. Set fotringen (05b) inn nedanfrå i messinghylsa (05), hol mot hol (prototypen: hylse og fotring er prenta i eitt).
10. Set hylsa med fotringen ned på tappen forbi dei tre klikktungene, med porten framme.
11. Vri kragen til 0° (porten framme) og skru dei tre stoppskruane M3 x 5 (05c) gjennom hola i messingen; første gong skjer dei gjengene sjølv i Ø2,5-holet.
12. Juster brytarane: med kragen på 0°, løys M2-skruane, skyv kvar brytar opp mot fotringen til han klikkar (multimeter på kontinuitet), deretter 0,6 mm lenger opp, og trekk til.
13. Set lysmodulen (06 + 06b + 06c + 07 + 06d, limt saman med 2K-epoksy, H11; sjå sida «Lysmodul: førmontering» i rettleiinga) ned gjennom kragen med rista mot spaltene; nøkkeltappen går i holet før pluggen når kontakten.
14. Funksjonsprøve: kople til straum og vri gjennom alle ni stillingane; sjekk tabellen i LES_MEG_FYR.
15. Legg dei tre bitane silikonsnor (11b) i lommene i golvet av mantelsporet i foten.
16. Senk mantelen (04) over kragen med L-spora over knastane (berre éin stilling passar: spaltene mot rista), trykk ned og vri ca 14° med klokka sett ovanfrå til nabben smett forbi og mantelen sprett 0,6 mm opp og låser.
17. Legg loket (08) i setet; det smett under dei tre nabbane.

**Service:** vri kragen til av (90°) før du tek ut lysmodulen. Løft loket ut i eitt av fingergrepa og trekk modulen rett opp. Ingen verktøy. For brytarar og kabel: ta ut lok og lysmodul først, trykk mantelen ned, vri han 14° mot klokka og løft han av. Brytarane er no tilgjengelege mellom søylene. For kabelen: snu lampa, skru ut dei tre M3 x 16 (H2, 2 mm unbrakonøkkel) og løft chassiset med hylsa på av foten; stoppskruane blir sitjande. Verktøy i alt: 2 mm unbrakonøkkel, 8 mm fastnøkkel og PH0-skrujarn; loddebolt og multimeter berre ved montering.
