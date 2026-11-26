# Samla innsending 26.11

`GK5_modul2_Iver_R_Finne_innsending_26-11.pdf`: leveransane til og med formgjennomgangen 25.11 i éin PDF med bokmerke, 32 sider. Side 1 er ei oversikt som viser kva krav i prosjektbeskrivinga kvar del svarar på.

| Del | Sider | Innhald | Kjelde |
| --- | --- | --- | --- |
| Oversikt | 1 | Krav, frist og kvar i fila | `del0-oversikt.mal.html` |
| 1 | 2–3 | Erstatningsoppgåve for studieturen | `del1-erstatningsoppgave.html`, teksten frå `../00_erstatningsoppgaave/erstatningsoppgaave.md` |
| 2 | 4–16 | Moodle 17.11: fase 1, formføringsplansje og tre konsept | `../04_moodle/GK5_Northern_Moodle_17-11.pdf`, uendra |
| 3 | 17–28 | Lysbileta til konseptgjennomgangen 18.11 | `../06_konseptgjennomgang/presentasjon.pdf`, uendra |
| 4 | 29–30 | Formføring for Raup, side 14 og 15 | `del4-formfoering-raup.html` |
| 5 | 31–32 | Prosesslogg 12. til 26.11 | `del5-prosesslogg.html` |

Ikkje med: refleksjonsoppgåva om «Innovate with Intention», handskisser og foto av skissemodell.

## Kvar tala kjem frå

- **Del 1.** Dei tre svara, ordtala og kjeldene er tekne uendra frå utkastet. Atterhalda i utkastet er ikkje med på sidene. Kjelder som berre atterhalda viser til (A3, G7, G9, G10), er tekne ut.
- **Del 4.** Reglane R1 til R5 og poengskalaen er frå `grunnlag/07-formfoering.md`, del 3 og 6. Mål, material og status for Raup er frå `Leveranse/konsept C - raup/raup-svart/` (`HOVUDROLLE.md`, `delar/Verkstad.md`, `former/Materialinnkjop.csv`). Formrommet er frå README-fila og førehandsvala i kjeldekoden til raup.iverfinne.no. Bileta er kopierte til `bilete/`.
- **Del 5.** Tala er innsjekkingar per dato i dette repoet og i repoet til raup.iverfinne.no. 12. og 13.11 er daterte i dokumenta, ikkje i historikken.

## Lag PDF-en på nytt

```
python lag_innsending.py
```

Skriptet skriv ut dei nye sidene med hovudlaus Chrome, tek inn del 2 og del 3 som dei er, og skriv oversikta til slutt med rette sidetal (`del0-oversikt.html`). Sidene brukar `../01_fase1_v2/felles.css` og `innsending.css`. Consolas finst ikkje på Linux, der blir JetBrains Mono brukt.
