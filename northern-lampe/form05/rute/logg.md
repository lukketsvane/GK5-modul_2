# form05 «Lysrute»: logg

Dato: 13.11.2026. Lampa ER vindauget: ei rute som sjølv lyser, med lysleiarplate og prismefilm. Skilnaden på **målt**, **rekna** og **anslått** er merkt i kvar linje. Alt rekna er modell, ikkje måling.

## Utgangspunkt

- Konseptbileta «Telt» og «Klemme» er genererte (stiane står i `konsept.md`). Dei er retning, ikkje fysikk.
- Fotoa av filmen mot vindauget (stiane står i `konsept.md`) syner **(målt, observert)**: lyse ting blir smurde ut på tvers av rillene, og regnbogekanten kjem på kantane som står på tvers av smøret. Biletet blir dregne ut til striper, ikkje delt rein i to. Det stemmer med at prisma er avrunda eller har ein spreiar i tillegg (som `konsept/film/00-vindauge-utan-linse.md` seier).
- `konsept/vindauge/film/arket.md` fanst **ikkje** kl. 15.20. Filmen er difor førebels det ideelle 90°-prismet frå `film.py` (n_d 1,59, Abbe 30). Dette er ANTAKING. Sjå «Filmprofil» under for siste sjekk.
- **ANTAKING: lysleiarplata finst ikkje i byggjesettet.** Ho er rekna som ei klar PMMA-plate (sjå `konsept.md`, bolken «Lysmotoren»).

## Køyringar (fortløpande)
- 15.34 kalib (196 s): film.py stemmer med 00-vindauge (prisme_0 {'T': 0.93, 'lober': [(-30.7, 0.47), (30.8, 0.47)]}, flat_0 {'T': 0.0, 'R': 1.0}, flat_30 {'T': 0.63, 'lober': [(-0.8, 0.61)]}, farge_450_650 [31.75, 30.25]). Motorane: E0 η 0.65, gain 1.05, halvvinkel y-z 90°; E1 η 0.53, gain 1.73, halvvinkel y-z 35°; E2 η 0.36, gain 2.47, halvvinkel y-z 21°
- 15.35 Flytta motor.py, logg.md og tal.json frå form05-rota til `form05/rute/` (hovudøkta: éin motor, i rute/). `film_tabell.npz` i rota er frå ein annan kopi og blir liggjande. Den første tretest-køyringa fall på stien til `konsept/film` etter flyttinga (retta).
- 15.36 **Funn (rekna) frå første kalib:** éin prismefilm har ein sidelobe på tvers av rillene: 0,03 av luminansen rett fram ved 40 til 50°, men 0,33 / 0,68 / 0,89 ved 60 / 70 / 80°. Langs rillene er det 0 frå 60°. Auget ser ruta frå sida, så rillene må peike mot auget (loddrett/kryss), ikkje ligge på tvers av synslina. Dette stemmer med `konsept/film/01-ruta.md` (0 frå 60° langs rillene, 160 cd per 1000 lm ved 70° på tvers).
- 15.37 Hovudøkta: `konsept/film/rute.py` (anna økt) har alt rekna ruta. Motoren her er **kalibrert mot rute.py** i staden for å finne opp rekninga på nytt: Rc 0,80 → 0,90 (rho i rute.py), kjelde «bak» = huset i rute.py (ingen ekstra tap), matt spreiar 0,90. Kjelde «kant» (lysleiarplata) har i tillegg ETA_KOPL · ETA_LEIAR = 0,72 (ANTAKING), og det er den einaste reelle skilnaden i lumen. Tabellane vart rekna om (kalib).
- 15.38 Motoren er gjort om til spesifikasjonar med identitetsparametrar (stotte, ruter, rille, kjelde, bak), så neste generasjon kan leggje til kroppar utan ny kode.
- 15.42 kalib (158 s) skreiv tab_ingen, tab_vassrett og tab_kryss
