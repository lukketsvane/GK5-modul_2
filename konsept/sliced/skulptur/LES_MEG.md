# skulptur: Northern-lamper frå skulpturformene i slicerman

19.11.2026. Utgangspunktet er dei tolv formene i «skulptur»-lista i slicerman (`skulptur-01-12.png`), skorne til 3 mm plater med motoren til slicer.iverfinne.no (origin/main 705b8ee, køyrd utan nettlesar). Platene står som eit gitter av lameller som gøymer lyskjelda, og éi handling skiftar mellom arbeid og kveld.

## Runde 3 (`runde3/`)

Fem lamper med synleg opal standardpære, bjørk 4 mm og éin messingdetalj: HATT (07), KOVE (09), HETTE (03), PILLE (12) og BLAD (10). Alle seks kroppane er ALT OK i full bygging. Sjå `runde3/LES_MEG.md`, `runde3/oversyn.png` og `runde3/profilar.png`.

Iver: berre BLAD i stemning (`runde3/5-blad/ark-stemning.png`) er rett retning estetisk. Tynt, bøygd opalark over ein liten kropp.

## Runde 3b (`runde3b/runde3b.png`)

Skulpturforma er konvolutten: ho blir kappa, av og til fylt eller skoren radialt, og gitteret av plater fyller ut det som er att. Kvar lampe har ei tynn line, ein rund fot med batteri, éin matt farge, éin messingdetalj og opal som einaste lysande flate.

| Design | Konvolutt | Handling | Modusar | Delar · ark · vekt | Motor |
| --- | --- | --- | --- | --- | --- |
| Nikk, `runde3b/nikk-01b/` | 01, flat linse | Rull linsa i messingnavet | Arbeid 0° (pøl på tastaturet), møte 100° (opalfelt bak gitter mot andletet), kveld 160° (mot taket); møte òg i gråbeige | 12 + 5 ekstra · 1 · 0,09 kg plater, om lag 1,4 kg heil | ALT OK, full bygging i alle tre (gråbeige `--rask`) |
| Nikk, `runde3b/nikk-forrige/` | 04, rund tromme | Trykk messingknappen ned | Arbeid −6° (pott ned), møte 85° (opal-andlet og veggvask), kveld 35° (opalmåne) | 14 + 3 ekstra · 1 · 0,11 kg plater, om lag 0,8 kg heil | ALT OK, arbeid full, møte og kveld `--rask` |
| Rokkestein, `runde3b/rokkestein/` | 05, flat stein | Løft framkanten, steinen rokkar | Arbeid 0° (nedre LED-rad, pøl), kveld og møte −30° (øvre rad, glorie på veggen) | 8 (alle opal) · 1 · om lag 1,0 kg heil | ALT OK, full bygging i begge |
| Hei, `runde3b/hei/` | 11, hatten utan stilk | Lett på hatten | Arbeid 0° (tre nedlys), møte og kveld −20° (varm vifte på veggen bak) | 11 + 6 opalskiver · 1 · 0,10 kg plater, om lag 0,85 kg heil | ALT OK, arbeid full, møte `--rask` |
| Nikk, `runde3b/nikk/` | 03, velta til eit nebb | Vipp hovudet om messingknappen | Arbeid 0° (LED-list, flekk på bordet), møte og kveld 25° og vridd 35° (opalnase mot andletet) | 10 (7 MDF + 3 opal) · 2 · 0,16 kg plater, om lag 0,7 kg heil | ALT OK, arbeid full og eiga opal-køyring, møte `--rask` |

Frå runde 2 til runde 3b har lampene gått frå skulpturar med lameller til Northern-lamper. Hovudet er no ei lita, roleg primærform på ei tynn line over ein rund fot, ikkje heile skulpturen. Kvar lampe har éin matt farge (svart, mørkegrøn eller gråbeige), og fargeveksling i gitteret er teken bort. Opal er einaste lysande flate, og LED-en ligg alltid bak opal eller djupt i ei celle. Handlinga er meir fysisk og leiken: tre av fem nikkar, éin rokkar og éin lettar på hatten, og ein vippesensor skal byte lysoppskrift i same rørsla. Briefen er teken meir på ordet: alle har tre lyslag (arbeid, møte, kveld) med dim-to-warm, og scena har tastatur, skjerm med fot, vegg og ofte eit andlet eller tak, så LYS-panela viser kvar lyset fell. Skjermen er mørk i alle modusar. Arbeidslyset fell likevel oftast på foten og venstre del av tastaturet, og ansiktslyset er vist, ikkje målt.

Merk mappene: Nikk/04 låg i `nikk/`, men vart skriven over av Nikk/03 og ligg no i `nikk-forrige/`. `nikk-v1/` er ein eldre versjon av Nikk/03. I `nikk-01b/skjerefiler/ekstra/` gjeld berre opal, saumring, bakskal og leppring1–2; `ekstra-leppe1–32` er gamle. Tavla er laga med `kjelde/tavle3.py (`runde3b/`)`. Motoren er køyrd med esbuild og sharp frå npx-cachen, fordi `node_modules` i slicer manglar plattformbinærane.

## Runde 2 (`runde2-hette-lykt-halo.png`)

| Design | Skulptur | Handling | Arbeid | Kveld og møte | Delar · ark · vekt |
| --- | --- | --- | --- | --- | --- |
| `hette/` | 03 | Drei hetta | Lys under skyggen på bordet | Veggen ved skjermen lyser: mjukt ansiktslys, låg kontrast | 15 · 3 · 0,52 kg |
| `lykt/` | 12 | Løft ut | I vogga ved skjermen: lang, lineær kjelde over tastaturet | Lykta løfta ut og boren til sofaen (tenkt oppladbar) | 17 · 2 · 0,40 kg |
| `halo/` | 07 | Vipp skiva | Vippa opp over skjermkanten: lys på tastaturet, skjermen skjermar auget | Bak skjermen: glorie på veggen rundt skjermen, roleg bakgrunn for kameraet | 12 · 1 · 0,20 kg |

Alle tre: ALT OK i motoren (harde reglar og alle krav, også i full bygging).

## Runde 1 (`slicerman-tre-forsok.png`)

`sopp/` (07, snu soppen), `skygge/` (03, drei skyggen) og `kapsel/` (12, sving kapselen). Dei held reglane, men svarar ikkje på heile briefen: ingen ansiktslys, Sopp er ikkje kompakt. Kapsel: dei fine skjerefilene gjev ikkje same delar som rapporten; sjekk før skjering.

## I kvar mappe

`ark-arbeid.png`, `ark-kveld.png` (runde 1: `ark-stemning.png`), `rapport.txt`, `prosjekt-arbeid.zip` (opne i appen: trykk på kroppsnamnet øvst, `fil`, vel zip-fila) og `skjerefiler/` (dei fine arka, `montering.txt`, `deler.csv`, `passprove.svg`).

## Kjelde

`kjelde/prep.py` (Blender: skalerer skulpturforma, kappar, hòlar ut lyskjelda, tettar nettet), `kjelde/gitter.ts` (to platefamiliar, snu, drei, vipp), eitt skript per design, og tavleskripta. Køyrd med verktykassa i `../kjelde/verkty/` (stiane retta til ein lokal kopi).

## Ikkje prøvd

Lux på arbeidsfeltet, blending målt, LED-modul og batteri. Bileta viser kvar lyset går, ikkje kor mykje. Vogga, skjermen, stanga og messingdetaljane er berre teikna. Ingenting er skore.

`astra/fire-design.md`: fire design med teikneprompts til Speculative Drawing (Astra 6.2 og gpt-image-2.6-sunburst), ventar på kreditt.
