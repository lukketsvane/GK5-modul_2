# Sidene inn i Figma med redigerbar tekst

To skript gjer HTML-sidene (til dømes `leveransar/01_fase1_v2/side-*.html`) om til Figma-rammer med redigerbar tekst, liner og bilete. Skripta legg rammene i den eigne Figma-fila (`h8W3hu6PLLjmj2Tra8FgOH`, teamet «personleg»), ikkje i klassefila. Iver flyttar dei sjølv over.

1. `les_oppsett.py side-*.html` køyrer kvar side i hovudlaus Chrome og les tekstblokkene (med skrift, storleik, farge og linehøgd), linene og flatene, bileta (beskorne som på sida) og SVG-figurane (rendra som gjennomsiktige PNG i 2×). Resultatet blir skrive til `oppsett/`, `bilete/` og `svg/` ved sida av skriptet.
2. `gen.py` lagar kompakte `use_figma`-skript (`bygg_0.js` og vidare). Skriftene er EB Garamond og IBM Plex Mono, som erstattar Consolas. Linehøgd og ombrekking følgjer nettlesaren.
3. Køyr skripta med `use_figma` mot fila. Last så opp bileta og figurane med `upload_assets` til rektangla skripta lagar. Rektangla heiter `bilete …` og `figur …`.

Bileta og figurane er innhaldsbilete. Teksten på sidene blir redigerbar. Lista over sider (`SIDER`) og gruppene (`GRUPPER`) i `gen.py` må endrast for nye innleveringar.
