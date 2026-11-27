# Monteringsrettleiing for Sveip mini, M02

![Kontaktark](ut/kontaktark.png)

Rettleiinga har 10 sider i IKEA-stil. Ho er laga med skillen `ikea-rettleiing` og `verktoy/ikea/bygg.py` frå [formnerd](https://github.com/lukketsvane/formnerd), greina `claude/ikea-manual-skill`. PDF-en ligg i `ut/rettleiing.pdf`, og sidene ligg i `ut/sider/`. Printfiler, innkjøp og kontrollar står i `../LES_MEG.md`.

## Bygg på nytt

```bash
python3 lag_delar.py                                             # delane i lampa som STL, og posisjonar.json
python3 lag_spesifikasjon.py                                     # spesifikasjon.json
python3 <formnerd>/verktoy/ikea/bygg.py spesifikasjon.json ut    # PDF, sider, kontaktark og rapport
```

Det krev cadquery, trimesh og reportlab, og node med three (`npm install --prefix <formnerd>/verktoy`). Det krev òg Playwright med Chromium.

## Rekkjefølgja

| Steg | Handling | Kvifor her |
| --- | --- | --- |
| | Prøv eit stykke filament (D) i ein kanal. Skru ein stålskrue (A) inn i hylsa på lysrista (M3), og ut att | Små hol blir trykte for små. A formar gjengene, så den mjuke messingskruen slepp. Står A att, sperrar hovudet i steg 6 |
| | Skuv chassiset (M2) opp i den tomme stamma (M1), og ta det ut att | Klaringa er 0,2 mm, og ribbene klemmer. Ein elefantfot syner her, ikkje først i steg 6 |
| 1 | Rista med lommene opp. Fjøra (C) i lomma over hylsa | Lomma (Ø 3,4, 2,4 mm djup) sentrerer fjøra. Laus på logoen kunne ho bli klemd under kanten på lomma |
| 2 | Kortet (MB) med framsida ned over rista | Lommene går over LED-ane, og logoen kviler på fjøra |
| 3 | Kortet med rista mot stolpen på chassiset (M2), inn mot kanten og ned på hylla | Kanten og hylla set kortet, så spelet i ringane ikkje flyttar LED-ane |
| 4 | 5x A gjennom rista og ringane og inn i stolpen | Låser kort, rist og chassis til éin pakke |
| 5 | Pakka på ryggen, rista opp. 25x D i kanalane, limte og klipte 0–0,2 mm under framsida | Rista står 0,3 mm frå veggen. Ein leiar eller ein limdrope som stikk fram, sperrar i steg 6. Med rista opp renn ikkje limet ut |
| 6 | Chassiset opp i stamma nedanfrå, til golvet er i flukt med underkanten | Ingenting stoppar chassiset, berre ribbene held det. I flukt står hylsa bak holet og leiarane bak LED-hola |
| 7 | Messingskruen (B), M3 × 4, gjennom feltet og inn i hylsa. Ikkje stram hardt | Gjengene i PLA er 2,6 mm lange. M3 × 3 når ikkje fjøra, M3 × 5 klemmer ho flat |
| 8 | Lysplata (M4) ned i skjermen | Ligg på stolpen og to bein |
| 9 | USB-kabelen (E) gjennom endeplata, og fastvara | |
| | Kontroll med kabelen i: kort trykk på messingen, og hald | Trykk slår av og på. Held du, sveiper matrisa |

## Kva som er kontrollert

- **Delane** er dei same lekamane som i `../print/` og har same ID (M1–M4). micro:bit-en (MB) og beslaga er modellerte etter monteringsteikninga for V2 og innkjøpslista. I stega har skruane glisnare gjenger (steg 1,2 mm) og fjøra fire vindingar, så dei ikkje blir svarte i liten skala. Beslagsida har 0,5 mm.
- **Mengdene** i stega stemmer med dellista: A5, B1, C1, D25 og E1. Porten tel ikkje. `ut/rapport.json` har ingen åtvaringar.
- **Rekkjefølgja og innføringsretningane** følgjer passformkontrollen i `../mini_print.py`. Chassiset med kortet kjem opp i stamma nedanfrå utan å ta borti noko, og lysplata kjem ned i skjermen.
- **Mot CAD-en** (`../d15_lysrist.py`, `../mini_print.py`): lomma for fjøra er Ø 3,4 og 2,4 mm djup og opnar mot kortet, så fjøra (3,0 mm) står 0,6 mm opp og blir sentrert. Gjengene i hylsa er Ø 2,6 og 2,6 mm lange. Tuppen på B står 2,0 mm frå kortet. Chassiset kan skuvast 20 mm forbi sluttstillinga utan å ta borti M1.
- **Ikkje prøvd:** nokon fysisk montering, og kor store hola blir i print. Difor står portsida før steg 1.

## Avvik frå IKEA

- Skrifta er DejaVu Sans. Tittelen er 80 pt, for 90 pt går ut over sida.
- Det er ingen hender, og ingen par med rett og feil. Leiarane er rette liner, og «skru ut» og «trykk» er rette piler.
- Korte tekstar står berre der figuren ikkje kan seie det: kva som skal gli og vere stramt på portsida, holmål, kjøpemål for B og C, kor langt leiarane skal klippast, «Ikkje stram hardt», messingen ved oppstart, adressa til fastvara og kontrollen.
- I steg 5 er éi rad med leiarar vist. Mengda står på bobla.

## Endra frå M01

Etter ein uavhengig gjennomgang av stil og korrektheit, kontrollert mot CAD-en:

- **Porten** prøver hylsa med stålskruen A, som blir skrudd ut att, i staden for messingskruen B. Chassiset i den tomme stamma er nytt. Holmåla står ved kanalen og hylsa.
- **Fjøra** går i lomma på rista før kortet, og kortet kjem ned med framsida ned (steg 1–2, ny vinkel `rygg`).
- **Steg 5** viser pakka med chassiset, på ryggen med rista opp, og åtvarar mot alt som står over framsida.
- **Steg 6** har ei boble med sluttstillinga. **Steg 7** har «Ikkje stram hardt» og kjøpemålet M3 × 4.
- **Kontrollen** har kabelen med og ei pil mot messingen. «Trykk på B» er bytt ut, sidan B òg er ein knapp på kortet.
- **Skala:** fast utsnitt per sekvens (steg 1–2, 3–4, 7–8 og kontroll). Steg 9 er sett bakfrå, så lampa ikkje heng.
- **Boblene** forstørrar om lag 3–4 gonger og står i fri luft.
- **Pilene** endar ved grensesnittet og går ikkje gjennom delane. Snu-ikonet i steg 3 er borte, for pakka blir vippa, ikkje snudd.
- **Stilarket:** strek 0,75 pt, mengd 18 pt, delnummer 7,5 pt, tittel 80 pt. Dellista står i rekkjefølgja M1–M4, MB, og beslagsida er høgare.
- **Baksida** er mindre og har berre kjelda.
- **Steg 9:** åtvaringa «Ikkje rør messingen når kabelen går i», som kom inn i M02, er teken bort att. Ho bygde på at kortet kalibrerer berøringa ved oppstart. Det gjer det ikkje i MicroPython 2.1.2: terskelen er fast, og ein finger som ligg på ved oppstart blir sett bort frå av programmet.
