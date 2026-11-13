# Kitbash generasjon 1 · logg

Dato: 13.11.2026, kl. 20.10 til 21.15. Motoren er montasje: kvar kropp er sett saman av delar som alt finst som CAD. Koden er `kitbash.py`, `lys.py` og `samle.py`. Tala ligg i `tal.json`, `tal.csv` og `tal.md`, bileta i `brett.png`, `brett-merkt.png` og `velt_umogleg.png`. Ingenting er målt. Måla på delane er anslått frå foto, massane er rekna frå volum, og lyset er modell.

## Kvifor ein ny motor

Formsøket rundt ruta på fot (`northern-lampe/form05/gen_d/`) enda med svaret nei: ingen variant av kroppen gjev 350 lx på feltet utan å velte eller blende. Kritikken der sa at settet var tre familiar med justeringar, ikkje seksten kroppar. Montasje byter identiteten i staden for måla: kva som lagar lyset, og kvar lampa bur.

## Settet

- **Frå overheadprojektoren** (`../delar.py`): armen P01, hengselet P02, hovudet P03, fresnelspegelen P05, glaslinsa P06, projeksjonslinsa P07 og prismearket P08. Basen P04 (nettspenning) og FSX-pæra P09 er ikkje med.
- **Frå ruta på fot** (`konsept/film/cad/ut/samla/`): foten med ballast (01, 02, 03), bjelken med LED-stripa (07, 08, 11, 12), ruta (09, 10) og heile lampa (kropp 13).
- **Nytt:** diode i brønn, vindaugsdiode med maske, skjermklype, bøyel av Ø6 stong, røyr, knott, blank flik.
- **Frontflatespegelen** i kropp 14 er ANTAKING. Han er ikkje fotografert og ikkje i `delar.py`.

## Brettet

Fire støtter × lysorgan. Rad 1 og 2 har armen ståande bak skjermen: klype på skjermkanten (1 til 5), stålplate under skjermfoten (6 og 7) og konsoll frå veggen (8). Rad 3 og 4 står på foten frå ruta-CAD-en, til høgre for skjermen. Kontrollane er projektoren slik han stod (17, bryt F9) og projeksjonslinsa i ei bordlampe (18, kan ikkje lagast: kastet er under 4f = 1,12 m, så biletet blir aldri skarpt).

## Feila

1. **Kameraet såg platene frå kanten.** Med asimut 240 frå husstilen låg platene på fot rett langs synslina og vart til strekar. Fem kroppar var dessutan klipte av ramma. Kameraet står no i asimut 300, og ingen av dei seksten er klipte.
2. **Delar bak skjermen skein gjennom.** Første brett fann lampepikslane ved å samanlikne fargar med lampa teikna åleine. Skjermen og armen har same farge der dei vender same veg, så armen bak skjermen kom fram som ein lys silhuett. No blir skjermen teikna lysande i eit eige pass for å finne pikslane hans.
3. **Ruta på fot gjekk inn i skjermen.** På plassen til dei andre føtene (440, 440) går bjelken 6 cm inn i skjermen. Kropp 13 står no der `lys_sjekk.py` har henne: 47 cm til høgre og 30 cm inn på bordet.
4. **Lampesokkelen var ein stålkloss.** I `delar.py` er sokkelen i hovudet ein massiv boks, og det gav 344 g. Han er rekna 15 % fylt (ANTAKING), og hovudet veg då om lag 0,6 kg.
5. **Bandet vart nesten skalert feil.** Første utgåve av band med vindauge endra lumen etter at strøka var laga. Intensiteten ligg i funksjonar som alt var bygde, så tala ville ha vorte feil. Koden vart skriven om før ho vart køyrd: bandet blir no laga med rett watt.
6. **Knotten var utanfor rekkjevidd.** På toppen av klypa var han 72 cm frå skuldra. På framsida av klypa er han 67 cm unna, og på enden av bjelken 65 cm.
7. **Veggen fekk for lite med 20 % til vindauget.** Band med vindauge gav 82 lx bak skjermen. Med 30 % blir det 132 lx, og watten går frå 2,6 til 2,9.
8. **To lysjobbar gjekk samstundes.** Første køyring av bandet tok 207 s medan brettet vart teikna. Jobben vart stoppa og køyrd om med dei raske grepa først.

## Kontroll

- **Mekanikken mot CAD-en:** ruta på fot gjev 3,0 N dytt, 24,0° veltevinkel, 1159 g og 196 cm² her. `konsept/film/cad/ut/kontroll.json` har 3,1 N, 24,5°, 1184 g og 196 cm².
- **Lyset mot tabellen for A, B, C og D:** B (over-flik) 3,6 W og jamnheit 0,41, C (fot-linse) 5,8 W og 0,62, A 3,0 W og 0,62, D 3,7 W og 0,62. Det er same tal som i `konsept/tre/00-tre-konsept.md` og `tal-D.json`.
- **Bandet med tre kjelder i staden for fem** gjev jamnheit 0,65 mot 0,69. Resultatet heng altså ikkje på kor mange punkt stripa er delt i.

## Mønster i tala

- **Over skjermkanten slår fot.** Plata over skjermkanten gjev jamnheit 0,41 til 0,70. Plata på fot gjev 0,29 til 0,39, fordi lyset kjem skrått inn frå sida.
- **Stripa er jamnheita.** Éi diode mot plata krev diffusorark (12°) og gjev 0,47. LED-stripa langs skjermkanten gjev 0,69 mot rein plate, og luminansen mot auget fell frå 227 til 70 cd/m², fordi arket er borte. Dette er første fresnelgrepet over referansen 0,6. Fresnel-familien stoppa på 0,56 og konkluderte med at jamnheit og luminans er same knapp. Stripa løyser dei frå kvarandre.
- **Å dele er betre enn å flytte.** Når plata vippar frå veggen til feltet, er spranget 0,37 til 0,42, og veggen bak skjermen får 14 til 16 lx i arbeid. Med plata fast og vindaugsdioden til veggen er spranget 0,07 til 0,11, og veggen får 106 til 132 lx.
- **Ruta på fot er stemning.** Kropp 13 treng 12,4 W for 350 lx og har jamnheit 0,07. Same svar som formsøket.
- **Ruta over skjermkanten (D) lyser på skjermen.** 163 lx på skjermflata, 0,47 av feltet.
- **Hovudet og røyret er det busette.** Hovudet som skjerm blendar det låge auget (5211 cd/m²) og er ein dimmar. Røyret av prismearket er ei rein stemningslampe.
- **Alt høgt på liten fot veltar.** Kroppane på Ø158-foten toler 0,6 til 1,9 N dytt i handtaket. Berre CAD-ruta når 3,0 N, og ho har ein messingknott på 159 g som motvekt.
- **Settet veg.** Armen og hengselet er 421 g, hovudet om lag 0,6 kg. Klypekroppane legg 0,9 til 1,1 kg på skjermen. Det er ein eigenskap ved delane, ikkje ved grepet.

## Formkritikk med tal

- **Nabo-IoU** er 0,45 i snitt og 0,97 på det høgste (6 mot 7). Para 1, 2 og 3 ligg på 0,94 til 0,96. Silhuetten skil ikkje kroppane som deler tak over skjermen.
- **Seksten kroppar, eller éin med seksten justeringar?** Åtte silhuettar: tak over skjermen (1 til 4 og 6 til 8), rute over skjermen (5), plate på fot (9 til 11), skive på stong (12), rute på fot (13), linse (14), hovud (15) og røyr (16). Det som skil dei sju taka, er kjelda og støtta, og ingen av dei syner godt frå framsida. Brettet spenner lysrommet betre enn formrommet.
- **Luft i hylsteret** er 0,19 (røyret) til 0,81 (under skjermen).
- **Taket er ein strek.** I arbeid ligg plata 7° frå vassrett, og frå stolen er ho ei list over skjermen. Gesten er vindauget på veggen og bandet på bordet, ikkje kroppen.

## Usikkert, og det modellen ikkje reknar

- LED-stripa er fem punktkjelder med brønn på 50°. Ei verkeleg stripe er ei line med lambertsk fordeling, og kanalen ho ligg i må skjere av lyset mot auget.
- Fresnelplata er ideell i modellen. Spreiing i rillekantane og dobbeltbilete er ikkje med, så luminansen mot auget blir truleg høgare enn 70 til 317 cd/m².
- Spegling av plata og stripa i skjermen er ikkje rekna.
- Vindaugsdioden står 12,5 cm frå veggen og får 45 % av lyset gjennom maska (59 % på 18 cm i D).
- Sollys i plata gjeld produktet òg: ho samlar lyset 19 cm framfor seg.
- Kor mykje skjermen toler på overkanten, er ikkje kjent.

## Køyringar

- 20.25 mek (1 s): 18 kroppar.
- 20.29 brett (54 s): feil 1 og 2.
- 20.33 brett (104 s): asimut 300, tre pass per kropp.
- 20.34 lys: over-vipp 4 s, over-flik 6 s, over-vindauge 2 s, over-band 207 s (feil 8).
- 20.40 lys: dei elleve raske grepa, 1 til 11 s kvar.
- 20.42 til 20.50 lys: over-band-vindauge 151 s, over-band-vindauge-q30 150 s, over-vindauge-q30 3 s, over-band-3 79 s.
- 20.47 brett (104 s): kropp 4 med vindaugsdiode og knott.
