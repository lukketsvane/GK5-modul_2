# Arbeidsnotat FALD (journal, skriven undervegs)

## Oppsett
- Motor: `faldmotor.py`. Kreppar (plass, retning, vinkel, radius) inn, falda ark ut. Rein bøying, strekk 0.
- Eigne kontrollar: rift (kreppar som kryssar utan klipp), skugge inn og ut (lysmotoren reknar ikkje sjølvskugge).
- Kreppretninga følgjer av adressa: `sikt()` reknar normalen som speglar kjelda mot målet, og kreppen står vinkelrett på projeksjonen.
- Malen køyrd éin gong: 9 min 25 s på ei travel maskin. tal() tek 3 til 10 s.

## Generasjon 1: topologi (16 kroppar, skarpe faldar, SATIN, overgangen er «boka» frå flatt ark)
Tal i `gen1/tal.md` og `gen1/ekstra.md`.
- Éin fald mot veggen er nok til alle tre adressene: bok-hol 5,23 W, tak 5,22 W, rund 5,10 W, Z 4,78 W, trekkspel 4,88 W.
- Ansiktet er ikkje ei tredje flate. Felt og vegg kastar 48 til 54 lx attende på ansiktet. Ei eiga matt flik gjev 60 til 65 lx, men 2660 til 3450 cd/m² mot auget (flik, skeiv, band, matt-floy).
- Satin mot ansiktet (U-hol) gjev 15 500 cd/m². Velta.
- Vifta (tre kreppar frå eitt punkt, 15° kvar) samlar lyset på feltet (768 lx) og når ikkje veggen (31 lx).
- Trekkspelet har klart best jamnheit: 0,47 mot 0,18 til 0,38 for resten.
- To adresser attåt feltet gjev to kreppar som kryssar inne i arket (skeiv, rift 3,6 mm). Det må klippast (flik).
- valm: fire faldar utan klipp, rift 16 mm, men strekk frå lysmotoren er 0,00 %. `a.strekk` ser ikkje rifter.
- Stemninga er lik for nesten alle (flatt ark mot feltet): 244 cd/m² mot auget, 8 lx på veggen, likskap 0,7 til 0,95. Boka frå flatt ark mot feltet er ein dimmar.
- Settet har stivna: éin fald, tak, rund og bok-hol er same lys. Byt grep: overgangsprinsipp, radius og overflate.

## Generasjon 2: kva som rører seg, radius, overflate (15 kroppar)
Tal i `gen2/tal.md` og `gen2/ekstra.md`.
- Watt for alle tre adressene har stivna: 4,6 til 5,3 W for alt som er fornuftig. Talet skil ikkje lenger.
- Det som skil no: jamnheit (0,19 til 0,42), likskap (0,56 til 0,93), stemning mot auget (53 til 244) og stemning på veggen (8 til 64 lx).
- Boka verkar som overgang når rota er veggpanelet: Z-vegg likskap 0,69, stemning 64 lx på veggen og 76 cd/m² mot auget. Med rota mot feltet er boka ein dimmar (0,92).
- Vipp av heile arket (tak-vipp): likskap 0,56, 53 cd/m² i stemning. Sveip med kjelda (tak-sveip): likskap 0,56, men smalare stråle gjev 1492 cd/m² i arbeid.
- Mjuk fald kostar lite: tak R 40 mm 5,27 mot 5,22 W. Z med R 30 mm 5,00 mot 4,78 W. Seks mjuke faldar (bolgje) 5,65 mot 4,9 W. Heile arket som éin boge 6,09 W.
- Trekkspelet miste jamnheita si då kvart panel blei sikta mot feltmidten: 0,47 (gen 1, feilsikta) til 0,21. Jamnheit kjem av at panela siktar ULIKE stader, ikkje same stad.
- Matt flate mot veggen (tak-mattvegg): 7,70 W og 4462 cd/m². Matt rot (matt-rot): 10,75 W, velta. Kuppel: strekk 23 %, kan ikkje lagast.
- Byt grep til generasjon 3: fordelt sikt for jamnheit, mjuk radius som standard, rot mot veggen, og optikken frå overheadprojektoren.

## Generasjon 3: fordelt sikt, mjuk radius (R 25 mm), rot mot veggen, overheadoptikk (15 kroppar)
Køyrd etter avbrotet (13.11, `kjor_gen3.py`, 394 s på prioritet Idle). Tal i `gen3/tal.md` og `gen3/ekstra.md`. Radiusserien i `radius.md`.
- Watt for alle tre adressene står framleis på 4,8 til 5,3 W. Ansiktet bind nesten alle (48 til 50 lx).
- Faldevinkelen er overgangen når rota ser mot veggen: Z-spreidd og Z-samla likskap 0,68 og 0,69, sprang 0,06, topp 0,70 (ingen blending undervegs).
- Fordelt sikt løftar jamnheita: Z-spreidd 0,34 mot Z-samla 0,22, spel 0,35 mot 0,21 i gen 2. Bok og rund-bok 0,42 og 0,43, best i familien.
- Boka med éin mjuk fald har likskap 0,83 og 0,84: nær dimmar. Vipp av heile arket (tak-vipp) gjev 0,56 og 53 cd/m² i stemning.
- Liten bok (18 cm, 33 cm høgd): 1800 cd/m² mot auget, bryt F5. Storleiken på arket held luminansen nede.
- fresnel-floy: 356 cd/m² i arbeid, 893 lx på feltet, men jamnheit 0,13 (ein flekk) og sprang 0,21.
- blank-bok skulle velte på blending, men gjorde det ikkje: 205 cd/m², fordi auget ikkje står i spegelretninga. Ho veltar på jamnheit 0,14 og skarp lyskant. Den tydelege veltaren er flat-vipp: 15,71 W for alle tre (taket er 7,5).
- kryss (tre kreppar som kryssar): strekk 48 %, rift 20 mm. Kan ikkje lagast.
- Radius: éin fald R 80 mm kostar 2 % (5,34 mot 5,22 W). Z R 40 mm kostar 7 %. Seks faldar R 40 mm kostar 25 %. Kostnaden følgjer delen av lyset som treff bøyane, ikkje radiusen åleine.
- Ingen fleire generasjonar. Siste generasjon = gen 3. Tre beste: Z-spreidd, rund-bok, tak-vipp.

## Feil og veikskapar i lysmotoren (meldt, ikkje retta)
- `Ark.__init__` set `k.lm_ut = k.lm - inn` for kvart ark. Når to ark deler éi kjelde, skriv det andre over det første, og `lm ut` og lysnytte i `tal()` tel lyset to gonger. Luxtala blir ikkje råka. fresnel_floy rettar det for hand.
- `a.strekk` måler berre lokal tøying. Han ser ikkje rifter: valm har rift 16 mm og strekk 0,00 %. Kryss fekk 48 % berre fordi to mjuke bøysoner overlappar.
- `overgang()['topp']` blir 0,70 til 0,71 for alle med faldevinkel som overgang, fordi luminansen følgjer watt(t). Han fangar berre blending undervegs som er over 41 % sterkare enn watten.
- Rundt ark blir teikna med takka kant ved n = 22 (heile fliser utanfor sirkelen fell bort).
