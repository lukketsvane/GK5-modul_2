# gen_d · logg

Dato: 13.11.2026. Generasjonen gjeld kroppen Iver valde: Telt-kroppen frå det genererte biletet (`C:\Users\Iver\.claude\uploads\6910850b-7461-4c8f-b765-e2447a4a2bf7\50f3c975-image.png`) med lyset frå D Ruta (`konsept/film/02-D-ruta.md`). Motoren er `motor.py`, tala ligg i `tal.csv` og `tal.json`, og bileta i `brett.png` og `velt_umogleg.png`. Ingenting er målt. Lys og mekanikk er rekna, og materiale og mål frå byggjesettet er anslått frå foto. **Filmen er rekna som ideelt 90°-prisme. Det er ei ANTAKING i alle tal,** fordi `konsept/vindauge/film/arket.md` ikkje finst.

## Motoren

Lyset er motoren til ruta.py, importert og ikkje kopiert: `rute.rute`, `ruta.vindaugsdiode` og `ls.overgang`. Rillene, formatet og hellinga på ruta og høgda på bjelken er parametrar. Kroppen er bygd av faste tverrsnitt: armen er P01-profilen frå byggjesettet (43 × 26 × 1,5 mm alu, anslått), bjelken er eit alu-røyr på Ø24 × 1,5 mm, og foten er stål på 8 mm. Det som varierer, er identitet: kvar foten står, kvar armen møter bjelken, kvar knotten sit, rillene og høvet mellom fot, bjelke og arm.

### Kalibrering mot tal-D.json (rekna)

| | tal-D.json | ruta.py køyrd no | motoren, ruta.py-kroppen | motoren, D-kroppen |
| --- | --- | --- | --- | --- |
| W for 350 lx | 3,688 | 3,681 | 3,680 | 3,681 |
| Jamnheit | 0,617 | 0,63 | 0,63 | 0,63 |
| Mot auget 25 cm | 1040 | 1087 | 1087 | 1087 |
| Mot auget 47 cm | 136 | 149 | 142 | 142 |
| Veggen bak skjermen | 142 | 141 | 146 | 145 |
| Skjermflata | 188,4 | 187,8 | 187,7 | 187,8 |
| Stemning, veggen | 189 | 187 | 193 | 193 |
| Stemning, mot auget | 242 | 246 | 223 | 223 |
| Likskap | 0,42 | 0,42 | 0,43 | 0,42 |

Det som kjem frå ruta (watt, jamnheit og skjermflata), stemmer innan 0,5 %. Det som kjem frå vindaugsdioden, flyttar seg med fotona: ruta.py mot seg sjølv flyttar seg opptil 9 % (mot auget 47 cm), og motoren ligg innanfor det. Luminansen mot auget i 47 og 60 cm er den lysaste flata framfor auget, som er vindauget på veggen. Ho er fotonrekna og flytta seg 10 til 25 % mellom to køyringar (kropp 5: 1584 og 1205 cd/m²). **Utslag under om lag 10 % i lyset og 25 % i auge47 og auge60 les ikkje.** Bjelkerekninga er kontrollert mot ei utkraga stong: 0,0600 mm mot 0,0600 mm analytisk.

## Feila

1. **Kravet til dytt var dobbelt.** Første køyring (16.36) kravde at foten skulle tole to gonger fingerdytten (2 × 5 N). Då fanst det inga skive bak skjermen som heldt D (11,7 cm trengst, med 14,1 cm og 2 × 5 N mot 12 cm plass). Kravet er no éin dytt på 5 N (ANTAKING), og 6°-kravet står for seg (`r_krav_stat_cm`).
2. **Rekkjevidda var for kort.** Med 60 cm låg alle knottane utanfor. Ho er no 70 cm (ANTAKING, høgre skulder, lengste grep utan å reise seg), og alle knottane ligg framleis på 70 til 89 cm. Det er ein eigenskap ved heile familien, ikkje ved éin kropp: alt som sit i skjermplanet, er ein arm unna.
3. **Ein Blender-render stal maskina.** Andre tal-køyring (10 til 18) stoppa utan utskrift fordi ei anna økt starta Blender 16.42. Prosessen min låg på IDLE og fekk ingen tid. Rad 10 til 12 låg att frå første køyring utan dei nye kolonnane. No ventar kvar køyring til Blender er ferdig.
4. **Kollisjonen prøvde berre hjørna.** Kontrollkroppen «umogleg» har bjelken 40 cm over bordet, under skjermkanten på 42 cm. Han gjekk gjennom utan flagg, fordi meshen berre har punkt i endane av bjelken og hjørna av ruta. Bjelkeaksen og rutefronten blir no prøvde tett, og bjelken går 15 mm inn i skjermen. Alle 18 er rekna på nytt etter rettinga.
5. **Plata under skjermen skugga feltet.** Plata stod frå y 0,38, altså 7 cm inn i feltet. Det grove gitteret såg det ikkje (jamnheit 0,62). Det fine gitteret gav 0,03, fordi cellene under ei plate på 2 mm fekk null direkte lys. Plata står no bak feltet (y 0,45 til 0,68). Då fall W for kropp 9 frå 4,07 til 3,84, så den gamle plata stal lys i det grove gitteret òg. Rekna på nytt for kropp 9 til 12.
6. **Det grove gitteret er for snilt mot veggen.** I det fine gitteret (celler på 4 cm) får veggen bak skjermen 121 lx i arbeid og 143 lx i stemning for D, mot 139 og 190 lx i det grove. Det same gjeld tal-D.json (189 lx i stemning). F6 held framleis, men stemninga på veggen er om lag ein firedel svakare enn tal-D seier. Jamnheita fell frå 0,62 til 0,51 for D, og då er ho under referansen på 0,6.
7. **Når armen møter bjelken på midten, dekkjer han vindaugsdioden.** Dette er ikkje ein feil i motoren, men i grepet. Dioden sit midt bak bjelken, og armen kjem inn akkurat der (9 mm frå dioden). Stemninga på veggen blir 0 lx i kropp 2, 10, 12 og 15, og 85 lx i kropp 6. Den som vil ha armen bak midten, må flytte dioden.

## Mønster i tala

- **Rillene flyttar mest.** Med vassrette riller får ansiktet lys: 149 lx i kropp 5 og 142 lx i kropp 16, så F10 held. Men auget får 1877 og 2248 cd/m² i 47 cm, og F5 fell. Med loddrette riller får ansiktet 21 til 43 lx, og F10 fell i alle. Kryss treng to ark, mens byggjesettet har eitt (P08). Kryss gjev òg jamnheit 0,24 til 0,47.
- **Hellinga har eit smalt vindauge.** Ved 165 (15° ned mot brukaren) blir jamnheita 0,04 til 0,21, og skjermflata får 449 til 721 lx (kropp 4, 10 og 13). Ved 205 (25° opp mot brukaren) får auget 1976 til 2330 cd/m² i 25 cm (kropp 3, 6 og 11). Berre 180 til 190 held begge.
- **Foten avgjer stabiliteten, og plata under skjermen er einaste som er lett.** Kroppane på plata toler 4,6 til 9,8 N (kropp 12 fell så vidt), og dei veg 2,0 til 2,1 kg utan skjermen. Skiver med knotten i leddet tippar under 2,0 til 3,8 N (kropp 1, 3, 5 og 14). Kropp 15 toler 5,8 N, fordi leddet sit bak bjelken og nærare foten. D treng ei skive med radius 11,7 cm, og det er plass til 12 cm. Skiver på Ø180 (kropp 8, 13 og 16) veltar utan dytt.
- **Svikt er ikkje problemet.** Under 5 N gjev knotten etter 0 til 1,7 mm, og framkanten av ruta 0,4 til 1,6 mm (2,3 mm i kropp 18). Ruta heng 0,1 til 0,5 mm av eiga vekt (1,0 mm i kropp 18). Profilen frå byggjesettet er stiv nok. Problemet er at han er for kort.
- **Trykk på ruta veltar nesten alle.** 5 N ned på det ytste hjørnet av ruta veltar 13 av 18 kroppar. Berre dei fire på plata og kropp 15 toler det.

## Produksjon: «alt eg må kjøpe er LED-stripa»

Premisset held ikkje for nokon av dei 18 kroppane (rekna frå geometrien, med mål frå byggjesettet som er anslått frå foto).

- **Finst i byggjesettet:** P08-arket (30,6 × 53,5 cm) dekkjer ruta med loddrette riller i alle format utan skøyt. Vassrette riller gjev éi skøyt på tvers av ruta, og kryss treng to ark. P07-fatninga (Ø77 × 28) kan vere knotten. P01-profilen er 240 mm, men armane er 409 til 838 mm.
- **Må skaffast, utover LED-stripa:** 169 til 598 mm profil til armen, eit alu-røyr på Ø24 og 400 til 690 mm til bjelken, 1,6 til 3,3 kg stål til foten eller ei stålplate på 1,1 kg, og kvit plast med spreiar (0,2 m²). LED-stripa er 2,1 til 2,3 m (fem rader bak ruta, ANTAKING) pluss vindaugsdioden.
- **Elektronikken manglar i premisset.** Knotten skal flytte watten frå vindauget til ruta. Det krev to kanalar og ein driver eller ein mikrokontroller, og ei straumforsyning. Ingenting av dette finst i byggjesettet. Straumforsyninga i projektorbasen går på nettspenning og skal aldri brukast (`modell/byggjesett/LES_MEG.md`).

## Formkritikk med tal

- **Nabo-IoU** er 0,19 i snitt og 0,43 på det høgste (9 mot 10, 6 mot 7). Konvolutten vandrar.
- **Luft i hylsteret** er 0,52 til 0,78. Alle er opne. Kropp 4 og 13 (låge, korte armar, 0,52 og 0,53) er tettast.
- **Ruta les som ein strek.** Lyset tillèt ruta 10° frå vassrett (D). Telt-biletet har henne på om lag 35° (anslått frå biletet). Frå kameraet (el 17) er ruta i D ei list, og gesten frå biletet, eit stort skrått vindauge, er borte. Tala over seier kvifor: 15° ned gjev jamnheit 0,15 og 721 lx på skjermen, og 25° opp blendar. **Telt-gesten ligg utanfor det lyset tillèt.** Identiteten må kome frå foten, armen og knotten, ikkje frå ruta.
- **Seksten kroppar, eller éin med seksten justeringar?** Topologien er lik i alle: skive eller plate, arm, bjelke og rute. Det som skil, er kvar foten står (tre grupper) og kvar armen møter bjelken. Rillene og hellinga flyttar tala mest, men dei syner ikkje i silhuetten. Svaret er tre familiar med justeringar, ikkje seksten kroppar.
- **Asymmetrien ber stabiliteten.** Armen til høgre ende er gesten i biletet, men han dreg tyngdepunktet frå midten av foten mot ruta. Difor treng D ei skive på Ø234 (11,7 cm i radius) for å tole dytten. Regelen i skillen er asymmetri frå delar som ikkje ber stabiliteten. Her ber armen stabiliteten, og det kostar 0,3 til 0,5 kg stål.

## Køyringar
- 16.30 kalib (10 s): W350 3.681 / 3.680 / 3.681 mot 3.688; auge25 1087 / 1087 / 1087 mot 1040; utkraga 0.060 mot 0.060 mm
- 16.36 tal (338 s): 16 kroppar rekna, tal.csv skriven  (stoppa før 6 min; 2 × dytt, rekkjevidd 60 cm: feil 1 og 2)
- 16.40 tal (213 s): 9 kroppar rekna, tal.csv skriven
- (16.43 tal 10 til 18: ingen utskrift, Blender frå anna økt; feil 3)
- 16.49 tal (84 s): 6 kroppar rekna, tal.csv skriven
- 16.49 brett (5 s): nabo-IoU snitt 0.19, maks 0.44; klipt av ramma: ingen
- 16.51 tal (79 s): 9 kroppar rekna, tal.csv skriven  (alle 18 på nytt etter feil 4)
- 16.52 tal (70 s): 9 kroppar rekna, tal.csv skriven
- 16.52 fin (7 s): D W 3.69 U0 0.51 bak 121, under-ende W 4.33 U0 0.03 bak 140, side-ende W 3.31 U0 0.58 bak 119, bak-skeiv-høg W 4.35 U0 0.44 bak 144  (U0 0.03: feil 5)
- 16.53 tal (16 s): 4 kroppar rekna, tal.csv skriven  (9 til 12 med plata bak feltet)
- 16.53 fin (5 s): under-ende W 3.94 U0 0.51 bak 127
- 16.53 brett (5 s): nabo-IoU snitt 0.19, maks 0.43; klipt av ramma: ingen
- 19.32 val ford (4 s): verknad ideelt 0.892, arket 0.903
- 19.32 val kalib (11 s): masse 1182 g mot 1184, tp [9.4, 4.1, 149.9] mot [9.2, 4.3, 150.8]; venstre 6.7 mot 6.7 N, dytt 3.1 mot 3.1 N; 2 W 35° ideelt: under 151 mot 190 lx, felt 56 mot 57 lx, auge 386 mot 372
- 19.37 val sok (313 s): 300 variantar, 0 utan flagg; lyset held i 1, av dei står 0
- 19.41 val sok2 (108 s): 150 variantar for stemning og sidelys, sok2.csv
- 19.48 val cad sporsmal (27 s): teikna W350 12.4 U0 0.08 auge 2171 tipp 25°; kant-står W350 7.3 U0 0.09 auge 1355 tipp 24°; lyset-held W350 6.0 U0 0.44 auge 1263 tipp -22°; jamnast W350 8.9 U0 0.60 auge 14241 tipp -16°; største-ark W350 6.4 U0 0.13 auge 691 tipp 12°
- 19.49 val cad abc (54 s): (a) felt 103 lx ved 2 W, stemning bak 13 lx, tipp 27°; (b) felt 91 lx ved 2 W, stemning bak 5 lx, tipp 26°; (c) felt 14 lx ved 2 W, stemning bak 70 lx, tipp 27°
