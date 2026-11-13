# Arbeidsnotat BØY (journal)

## Økt 1 (natt til 13.11, stoppa kl. 02.28)
- Generasjon 1 (`gen1/tal.md`): berre bøyen varierte. Fast fot, arkplass, Ø 250 mm, SATIN.
- Generasjon 2 (`gen2/tal.md`): arket framfor skjermplanet, sikte 10 cm forbi feltmidten, to adresser frå éi flate, overflate, storleik, høgd.
- Søk 1 til 6 (`sok*.py`). Søk 6 (koordinatsøk for to-adresse-arket) rakk ikkje å skrive tal.
- Merk: `gen2/tal.md` vart skriven før `to()` vart retta (sone A i referanseplanet, overgangen «gli»). Radene to-vandr, to-kryss, to-vipp og to-hog i gen2 kjem frå den eldre `to()` og kan ikkje lagast på nytt med `familie.py` slik han står no.

## Økt 2 (13.11, frå kl. 10.20)
- Malen køyrd éin gong: 5 min 21 s med brett, maskina travel (99 % last frå andre økter). Tala som venta.
- Søk 7 (`sok7.txt`): blank kuv R 0,6 syner kjelda for auget 25 cm over bordet (3475 cd/m²). R 1,2 og 2,0 gjer det ikkje (194). To-adresse-arket med retta `to()`: satin 5,55 W for felt og vegg, blank 4,62 W.
- Søk 8 (`sok8.txt`): jamnheita er 0,60 for blank kuv frå R 0,6 til 2,0. Ark under 0,22 m fell til 0,05 til 0,15.
- Søk 9: kontroll av rutene. 0,60 er ekte (lågaste rute er hjørnet ved lampa i begge), ikkje ein feil.
- Søk 10 (`sok10.txt`): koordinatsøk på to-adresse-spegelen. Inga enkeltendring betra han. Utgangspunktet er eit lokalt optimum.
- Generasjon 3: 16 kroppar, `tal.md`, `ekstra.md`, `overgang.md`, brett og par i denne mappa.
- Søk 11 (`sok11.txt`): sikte for stemninga 62 cm over bordet tek skjermflata frå 142 til 78 lx for spegel-kuv-1.2. Ikkje teke inn i generasjon 3.
- Kontroll av motoren: ortho() byter opp-vektor ved |n_z| = 0,9, så ramma til ark() hoppar (n = (0,31, -0,31, 0,899) gjev u = (0,707, 0,707, 0), n_z = 0,901 gjev u = (0,947, 0, -0,322)). `lampe()` sender difor eigen `opp`.
- Ferdig: tal.md, tal.csv, ekstra.md, overgang.md, brett med px = 200, tre par, funn.md.
