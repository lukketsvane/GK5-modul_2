# Arbeidsnotat, familien KLIPP

Journal undervegs. Det ferdige står i `funn.md`.

## Generasjon 0: kvar går lyset gjennom klippet? (`gen0_plassering.py`, `gen0_stoy.py`, `gen0_delt.py`)

- Med kjelda rett under arket (malen, «fot») går alt gjennom klippet til taket. Ring med hol Ø 12 cm: felt 302 lx, vegg 26 lx, 171 lm i taket.
- Med kjelda 25 til 30 cm framfor arket («fram») går det til veggen: same ring gjev vegg 89 til 187 lx. Lågt ark (33 cm) treffer veggsona best.
- Oppstillinga avgjer adressa. Klippet kan berre vere veggstrøk når veggen ligg i forlenginga av strålen.
- Støy: punktkjelde og éin stråle per veggrute gjev vegg 79 til 220 lx for same slissar (2,5 cm) med ulik fase. Kjelda er difor delt i tre punkt over opninga på Ø 4 cm (då 90 til 130 lx). For ring: 187 lx med eitt punkt, 154 med tre, 148 med seks.
- Ark der alt er klipt bort, krasjar motoren (tom Nett).
- Tid: tal() 5 til 13 s med tre kjeldepunkt, rendring px 200 om lag 80 s.

## Generasjon 1: identiteten til klippet (`gen1.py`, tal i `gen1/`)

Same oppstilling, same skive, same watt. Berre klippet skil.

- W for både 350 lx og 100 lx på veggen (det største av dei to): alle klipp ligg mellom 4,1 og 5,0 W. Heil skive: 11,4 W. Klippet verkar, men kva klipp er nesten likegyldig.
- Vegg/felt i målet (0,29 til 0,43): ring 0,36, halvmåne 0,41, halv 0,34.
- Jamnheita blir betre når midten er borte (ring 0,44, sektor 0,44, heil 0,35). Ei flik som lyser på den fjerne enden av feltet: 0,48.
- Flik bøygd lite mot kjelda skuggar sitt eige hol: tunge gjev vegg 43 lx, same som heil.
- Likskap 1,00 for alle: dimmarar. Settet har stivna i overgangen. Neste grep: rørsla.
- Velta: hol mot auget, 1,8 millionar cd/m². Kan ikkje lagast: konsentriske ringar utan bruer, 3 delar.

## Avbrot og framhald (13.11, føremiddag)

- Økta stoppa 02.28 før generasjon 2 gav tal. `gen2/` var tom. Generasjon 2 er skriven, men aldri køyrd.
- Røykprøve: `ring-linse` krasja fordi `from familie import *` ikkje tek med `_bokfor`. Retta i `gen2.py`. Dei andre femten byggjer geometri utan feil.
- Generasjon 2 er den siste. Ho svarar på det opne spørsmålet frå generasjon 1 (likskap 1,00 for alle): kva rørsle gjer klippet til ein overgang.
