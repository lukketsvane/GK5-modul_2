# BØY: etterprøving av dei tre beste

Tal frå `etterproving.py` (utskrift i `etterproving.txt`). Modell, ikkje måling. Målet var å felle kandidatane.

## Tala held
Alle tal i funn.md for dei tre kom att innanfor 1 % (W350, felt, jamnheit, auge, vegg, ansikt, stemning, likskap, topp). Einaste avvik over 5 % er sprang for to-spegel-kryss (0,022 mot 0,02), som er avrunding. Strekk er 0 for alle tre.

## Det som fell
1. **Alt kviler på at spegelloben er smalare enn 4°.** BLANK er ei antaking (rd 0,03, rs 0,85, sigma 2,5). Mot auget 25 cm over bordet i arbeid:

| sigma eller rd | spegel-kuv-1.2 | to-spegel | to-spegel-kryss |
| --- | --- | --- | --- |
| 2,5 (BLANK) | 194 | 193 | 1836 |
| 3 / 4 / 5 | 194 / 1600 / 5262 | 193 / 441 / 1090 | ikkje køyrt |
| 6 | 8936 | 2009 | 5910 |
| 14 | 10 673 (47 cm: 1960) | 6778 (47 cm: 1204) | 6559 |
| rd 0,3 | 1936 også i 47 cm | 1932 også i 47 cm | 1213 |

Folie limt på papp med fingerkrøll ligg truleg mellom 3 og 8°. Då bryt spegel-kuv-1.2 F5 ved 4° og F1 ved 5°. P2 i funn.md («inga lyspunkt frå 25 cm med pil 6,5 mm») står og fell med dette.

2. **Spill forbi arket:** spegel-kuv-1.2 18 % i stemning og 11 % i arbeid. to-spegel 30 % i stemning (33 % av lyset går til taket). to-spegel-kryss 48 % i stemning og 23 % i arbeid.
3. **Skjermplanet:** to-spegel og to-spegel-kryss går til y 0,49 i arbeid, altså 4 cm bak skjermframsida (ved sida av skjermen, x frå 0,35). to-spegel stikk i stemning fram til y -0,02, over bordkanten. spegel-kuv-1.2 held seg på y 0,17 til 0,43.
4. **Kjelda:** LED i foten er usynleg frå 47 cm (brønn 40°). Frå 60 cm ser auget dioden i to-spegel-kryss med 279 cd/m². `auge_i()` i familie.py tek berre med arket og gav difor 118 i ekstra.md. Feilen er i familie.py, ikkje i motoren.
5. **Sjølvskugge:** ingen. Alle tre er kuv (bøyen i to-spegel er ein kuv knekk). Ingen djupe holformer.
6. **Spegling av arket i skjermen** (eiga rekning, utan okklusjon): 20 til 21 cd/m² frå 25 cm for to-arka, 0 frå 47 og 60 cm. Ikkje avgjerande.

## Dom per kandidat
**spegel-kuv-1.2: held ikkje.** Tala stemmer, og med BLANK er alt under 200 cd/m². Men F1 ved 25 cm fell når loben blir 4 til 5°, og skissemodellen er nettopp folie. F6 i arbeid er 24 lx (krav 100 til 150), og å nå både 350 og 100 lx kostar 20,74 W, over B3 (7,5 W). Midt i vippen får skjermflata 364 lx: lysflekken går over skjermen. Ein blank spegeldisk Ø 250 ved skjermen bryt «mjuk» (blank stor flate) og verkar som eit optisk instrument, ikkje heimleg. R1: fot, stamme, arm og disk er fire element, for disken sit 13,5 cm framfor stamma.

**to-spegel: held ikkje.** Beste svaret på to adresser (350 og 100 lx for 4,62 W) står. Men jamnheita er 0,43 mot referansen 0,60 (F3 «jamt»), skjermflata får 371 lx eller 0,50 av feltet (det verste i første lysbrett var 0,49), arket stikk bak skjermplanet, og topp 1,01 er ein liten glødetopp midt i overgangen. Ved sigma 6 blir det låge auget 2009 cd/m² (F5). Glideskinna for 110 mm gjer mekanikk til hovudmotiv («enkel», «varm»), og ein spegel 380 × 250 mm ved skjermen verkar teknisk.

**to-spegel-kryss: held ikkje.** Bryt F5 alt med BLANK (1836 cd/m² frå 25 cm) og F1 med sigma 6 (5910). Jamnheit 0,33, 3,32 W for 350 lx, nær halve lyset går forbi arket i stemning. To kjelder krev to telefonlykter.

## Bygg
- spegel-kuv-1.2: kan byggjast på ein dag for om lag 0 kr (papp, folie, printa rib, lykt i papprull, stolpen). Manglar ein arm som held disken 13,5 cm framfor stolpen, og ei glatt spegelflate. Prøv bakre reflektorfilm frå LCD-panelet om han finst, elles blir folien den svake lekken.
- to-spegel: arket og ribba går, men glideskinna må printast og testast. Truleg to dagar.
- to-spegel-kryss: krev to lykter. Byggjesettet har éi. Arduino med lysdiodar er for svakt utan innkjøp.

## Northern
Ingen av dei held R3 sikkert: kjelda er gøymd, men om ho syner som punkt i spegelen avheng av loben. R2 held (stolpe). R4 held (aluminium er materialskifte). R5 er ikkje teikna. «Mjuk» blir broten av store blanke flater og, for to-arka, av knekken. «Enkel» blir broten av fjerde element (arm) og av skinna i to-spegel.

## Nabo
Verner Panton Reflect: foten kastar lyset opp mot ein skrå disk som sender det ut att, same prinsipp som spegel-kuv-1.2. https://www.danishdesignstore.com/collections/table-lamps/products/verner-panton-reflect-table-lamp-verpan
Oluce Siro har ein metallreflektor i midten, men lyset går mot ein lakkert skjerm. https://www.energybulldog.com/Oluce-Siro-LED-Table-Lamp-Dimmable-45-Cm-Gold-Lights-Co-Uk.html
Eg fann inga lampe med eitt bøygd ark som gjev to adresser (to-spegel).

## Feil
- Motoren: ingen nye feil funne. `ortho()` byter opp-vektor ved |n_z| 0,9, som agenten skreiv: stadfesta (n = (0,31, -0,31, 0,899) gjev u = (0,707, 0,707, 0)). Det er eit sprang i konvensjonen, ikkje feil tal, og familie.py omgår det.
- familie.py: `auge_i()` ser ikkje kjelda sjølv (279 mot 118 cd/m² frå 60 cm for to-spegel-kryss).
