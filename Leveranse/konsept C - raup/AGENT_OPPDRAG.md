# RAUP · produksjonsklar lampe for Northern

## Mål
Ta designet i denne mappa frå skisse og referansemodell til ein faktisk produksjonsretta, fullstendig, parametrisk CAD-konstruksjon som kan byggjast som 1:1-prototyp og kontrollerast for vidare produksjon. Ikkje stopp ved nye illustrasjonar, rapportar eller planar: modeller, eksporter, sjekk og iterer.

## Kjeldeprioritet
1. `modell/modern_table_lamp_3d_model.fbx`: konkret 3D-geometri. Inspiser faktiske objekt, mål, transformasjonar, topologi og proporsjonar; ikkje anta at FBX er vass-/produksjonstett eller skalert rett.
2. `referanse/cad_visning_1.jpeg`, `cad_visning_2.jpeg`, `cad_visning_3.jpeg`: form og konstruksjon sett frå ulike vinklar. Kontroller silhuett og kontakt mellom dei to hovuddelane.
3. `render/01_hero.png` til `10_low_angle.png`: material- og lysintensjon, IKKE eksakt teknisk geometri. Nokre genererte bilete kan avvike mellom vinklar.
4. `../../context/2 Endelig designbrief Northern.md` og resten av relevant GK5-kontekst: funksjonelle og faglege krav.

## Produkt
RAUP er ein liten, skulpturell bordlampe. Behald den mjuke, asymmetriske, spiral-/halvmåneforma hovudkroppen og ei slank høg, forma diffusjonsflate som står i relasjon til kroppen. Hovudkroppen skal primært kunne støypast av resirkulert papirmasse i eigna støypeformer. Den optiske flata skal først og fremst undersøkjast med ei ombrukt, bøybar diffusjons-/prismeplate frå demontert monitor; måljast, formast og eventuelt laserskjerast etter faktisk materiale. Varmt, behageleg, indirekte lys, låg blending, dimming mellom arbeidslys og stemningslys. Kabel/LED, varme, festing, service, ballast og stabilitet er reelle konstruksjonsoppgåver.

## Gjennomfør
- Undersøk tilgjengelege CAD-verktøy (FreeCAD/CadQuery/Blender/OCCT osv.) og eksisterande arbeidsflyt. Hent berre relevante avhengnader; prioriter parametrisk B-rep/STEP, ikkje mesh som endeleg CAD.
- Dokumenter minimale antakingar der FBX, bilete og brief manglar mål. Mål/før opp ein dimensjonstabell i mm. Utled best mogleg skalering frå kjelder, og marker det som må målast på fysisk prototype.
- Modellér alle nødvendige einskilddelar med produksjonsvenlege veggar, radier, tilkomst, samanbinding og deling, utan unødig kompleksitet. Bruk reell montering, ikkje overlappande volum.
- Konstruer støypeform for papirmassen med delingslinjer, sleppvinklar, drenering, krymp/tykkleik og mogleg uttak. Vel justerbare parametrar når materiale er ukjent.
- Konstruer diffuserutforming og flatmønster/DXF frå ein faktisk bøybar plate, med festemetode som ikkje øydelegg prismefunksjonen eller overklemmer materialet. Skil mellom diffuser, reflektor og eventuelt polariseringslag; ikkje gå ut frå at alle monitorfoliar toler varme/bøying/laser.
- Konstruer LED-kjelde, varmestykkje, kabel, strekkavlasting, forsyning, dimming, service og tilkomst. Identifiser konkrete komponentstorleikar ut frå oppgitte dimensjonar og dokumenter eventuelle alternativ.
- Berekn massesentrum, veltetryggleik, kontakt, klaringar, bøyeradius, straum, varmefluks og lysoppgåva med transparente føresetnader; ikkje påstå verifiserte lux-/temperaturtal utan måling/simulering.
- Lever parametriske kjeldefiler, sjølvstendige STEP for delar og samanstilling, STL/3MF for printbare formar og eventuelle jigg-ar, DXF for laserkutting, enkel BOM og rekkjefølgje for montering/demontering.
- Lag faktiske kontrollar: B-rep-validitet, positive volum, ingen utilsikta kollisjonar, korrekte einingar/mål, at toleransane gir montering, og at eksporterte filer kan lesast inn att. Køyr og rett feil, ikkje berre skriv korleis ein kunne testa.
- Lag nokre nøytrale kontrollrendringar eller skjermbilete frå den FAKTISKE CAD-modellen som dokumenterer forma og komponentplassering. Ikkje erstatt eller «rett» konstruksjonen med nye AI-genererte illustrasjonar.

## Arbeidsgrense
Skriv, generer og endre berre i denne `konsept C - raup`-mappa. Les gjerne resten av repoet. Ikkje endre RUTA/FURU/zeppelin, ucommitta anna arbeid, globale oppsett eller API-innstillingar. Ikkje push, slett eller overskriv kjeldefiler utan særleg grunn. Ikkje eksponer API-nøklar. Samle den faktiske leveransen under `cad/`, `produksjon/` og `kontroll/` dersom det er naturleg. Hald dokumentasjonen konsis, på nynorsk.

## Stoppkriterium
Arbeid vidare til produksjonsmodellen, delgeometri, formar og eksportar er reelle og maskinelt validerte. Dersom noko er umogleg å avgjere frå kildene (materialprøvar, målt lys, CE/elektrisk tryggleik), marker presist kva som manglar, men gjer ferdig alt som kan byggjast og kontrollerast digitalt. Slutt med ei kort oppsummering av filer, utførte testar, manglande fysiske testar og korleis prototypen kan produserast.
