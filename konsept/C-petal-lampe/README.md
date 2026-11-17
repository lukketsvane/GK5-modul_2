# Konsept C: ribbelampe (R02)

R02 er ei parametrisk 1:1 CAD-utprøving frå biletet i ChatGPT-samtalen 17. november 2026. CAD er ikkje dokumentasjon på ei produksjonsgodkjend armatur.

## Avvik frå førre versjon

R01 hadde for brei kropp (158 mm), for stor sokkel (116 × 27 mm), sektorforma ribber og ei stor synleg opning på toppen. R02 er slankare (220 × 119 mm), har sokkel ca. Ø68 mm og åtte lange krumma ribber som rammar inn ein samanhengande frontspalte. Referansefotoet har om lag høgd/breidd 1,89, R02 har 1,85 (2,2 % avvik i proporsjonstalet). Mål er avleidde frå eit enkelt bilete, ikkje fysisk oppmåling.

## CAD

`build.py` byggjer STEP-samling og separate STEP/STL. `validate.py` testar lukkede volum, uventa kollisjonar, byggjevolum P1S og proporsjon. `render.py` lagar bilete av faktisk CAD-geometri. `C_PETAL_R02_EXPORTS.zip` inneheld eksportane, og `dimensions.json` + `validation.json` er maskinlesbar geometri.

Delar: 8 PETG-skalribber, låg PETG-sokkel med 8 skjulte rotspor, botnlokk, stålballast, opal PC-diffusorrøyr, toppføring/hette, 12 × 12 mm aluminiumskjerne og LED-plasshaldarar.

Førebels innfesting: 8 rotfeste frå underside, 0,27 mm modellert lateral klaring, opalrøyr i sokkelring, M3-sentralskrue inn i aluminiumsprofil, toppføring. Gjengrep, fasteners, toppføring og passform er ikkje fysisk prøvde.

## Monteringsrekkjefølgje

1. Prøveprint éi ribbe, ein kort prøvesokkel og toppføring.
2. Kontroller synleg form og passform; juster klaringar etter eigne printmålingar.
3. Fest aluminiumskjerne mekanisk i sentralsokkelen og sikra kabelavlasting.
4. Set inn opal diffusor, monter åtte ribber i sokkel og fest frå undersida.
5. Monter toppføring og diffusorhette; legg inn låg stålballast og lukk botnen.
6. Test styrke, statisk vipping, elektrisk tryggleik og lys ved begge bruksmodus.

## Ikkje verifisert

Elektrisk krets og to lysmodusar er ikkje implementerte. Det er ikkje testa LED-varme, blending, lys på skjerm/ansikt, temperatur i PETG/opal PC, kabelstrekk, 1:1 balanse, slagstyrke eller samsvar med armaturstandardar. Bruk berre ekstern kvalifisert 24 V SELV-forsyning etter val og prøving av faktisk elektronikk. Ikkje serieproduser direkte frå R02.
