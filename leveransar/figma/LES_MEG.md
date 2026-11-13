# Sidene inn i Figma med redigerbar tekst

To skript gjer HTML-sidene (til dømes `leveransar/01_fase1_v2/side-*.html`) om til Figma-rammer med redigerbar tekst, liner og bilete. Skripta legg rammene i den eigne Figma-fila (`h8W3hu6PLLjmj2Tra8FgOH`, teamet «personleg»), ikkje i klassefila. Iver flyttar dei sjølv over.

1. `les_oppsett.py side-*.html` køyrer kvar side i hovudlaus Chrome og les tekstblokkene (med skrift, storleik, farge og linehøgd), linene og flatene, bileta (beskorne som på sida) og SVG-figurane (rendra som gjennomsiktige PNG i 2×). Resultatet blir skrive til `oppsett/`, `bilete/` og `svg/` ved sida av skriptet.
2. `gen.py` lagar kompakte `use_figma`-skript (`bygg_0.js` og vidare). Skriftene er EB Garamond og IBM Plex Mono, som erstattar Consolas. Plex Mono er 0,60 em per teikn mot 0,55 for Consolas, så monotekst blir sett med 0,917 av storleiken i HTML-en. Då blir han like brei, og versalhøgda blir nesten den same. Storleik og sperring blir overførte nøyaktig, ikkje runda til halve piksel, elles kolliderer fotnotane. Linehøgd og ombrekking følgjer nettlesaren.
3. Køyr skripta med `use_figma` mot fila. Last så opp bileta og figurane med `upload_assets` til rektangla skripta lagar. Rektangla heiter `bilete …` og `figur …`. Kvar opplasting legg òg biletet som ein laus node på den første sida i fila (`placedOnNodeId` i svaret). Set `imageHash` på rektangelet og slett den lause noden. Last opp éin og éin fil om Figma svarar 502.

Bileta og figurane er innhaldsbilete. Teksten på sidene blir redigerbar. Lista over sider (`SIDER`) og gruppene (`GRUPPER`) i `gen.py` må endrast for nye innleveringar.
