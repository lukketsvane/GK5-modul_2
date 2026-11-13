# Status: varmt vindauge og samordning

Skrive 13.11.2026 kl. 20 av styringsøkta, som vart arkivert etterpå. Frå no melder kvar økt resultata sine rett til Iver.

## Kven eig kva

| Mappe | Eigar | Innhald |
| --- | --- | --- |
| `konsept/tre/` | New session | A Skiva, B Over, C Vindauge: ark, tal, valtabell til 18.11, stykkliste |
| `konsept/film/` | New session | `film.py` (optikken til arket), vindauge utan linse, D Ruta, CAD i `cad/` |
| `konsept/vindauge/film/` | styringsøkta (avslutta) | dommen om kva arket er: `arket.md`, `arket.json`, to analysar |
| `modell/byggjesett/` | Ypperleg design | delebiblioteket (overheadprojektoren, linsene, arket) og rendrar |
| `leveransar/` | Ypperleg design | Moodle-PDF, byggjepakke (side 11 er målearket for arket), presentasjon |
| `northern-lampe/` | Parametrisk formsøk | referansespor (bru, krok, prisme) og formsøket `form05/gen_d/` |

Skriv ikkje i ei mappe du ikkje eig. Commit berre eigne stiar, aldri `git add -A`.

## Ferdig

- Moodle-PDF til 17.11 (13 sider), byggjepakke og presentasjon til 18.11.
- A, B og C er rekna mot alle krava. D Ruta er rekna til same nivå og blir vist 18.11 som vidareføring av B.
- Dommen om arket: mest truleg prismefilm (55 % nær ideell, 31 % med avvik). Arbeidsverdi n 1,57, lobar ±29,4°. Ingenting er målt på arket.
- CAD av ruta på fot: `konsept/film/cad/lampe.py`, STEP, STL, DXF, monteringsark.
- Formgenerasjon rundt den valde kroppen: `northern-lampe/form05/gen_d/` (brett, tal, logg, framlegg til val).

## Ope

1. Iver gjer lykteprøvene P1–P3 (side 11 i byggjepakken, fasit i `konsept/vindauge/film/arket.md`) og måler arket med målband. Så reknar New session D om med målt n, éin gong.
2. Valet (a)/(b)/(c) frå formsøket, som mål i CAD-namna (`val_maal.json`). Iver vel.
3. Kroppen Iver valde (ruta på fot) gjev 57 lx på arbeidsfeltet mot kravet 350 lx. Formsøket ser etter variantar som held. Finst ingen, står valet mellom stemningslampe og D Ruta over skjermkanten.
4. Iver byggjer og fotograferer skissemodellane av A, B og C. Foto i `leveransar/03_konsept/foto/`, så byggjer Ypperleg design PDF-en og presentasjonen på nytt. Opplasting til Moodle innan 17.11 kl. 23.00.
5. Dei sju råfotoa av delane ligg i git-historikken (commit `1d554b5`, fjerna i `2a5e9f2`). Eitt viser eit brev. Ikkje skriv om historikken utan at Iver seier ja.
6. Etter nullstillinga tysdag: kropp, velt, kjøling og stykkliste for D; designteori-økta sine to stoppa arbeidsflytar; etterprøving av `film.py` med uavhengig kode.

## Reglar som gjeld vidare

- Vekegrensa stod på 82 % (alle modellar) og 84 % (Fable) kl. 19.40 og blir nullstilt tysdag 17.11 kl. 11.00. Ingen nye arbeidsflytar før det utan at Iver ber om det. Det som er att, skal rekke til å byggje Moodle-PDF-en på nytt.
- Høgst to til tre Python-prosessar om gongen, på låg prioritet. Lyden til Iver hakkar elles.
- Repoet er offentleg. Råfoto og utsnitt av dei ligg berre i `context/`.
- Det Iver skriv direkte i ei økt, går føre alt anna.
