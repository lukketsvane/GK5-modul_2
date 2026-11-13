# Levin-lesing av overliggaren (gen01 k01)

**Festa 2026-11-13 kl 01:03, før nokon test er køyrd.** Utfalla står i `utfall.md`.

Dette er mi lesing av vår eiga modell (felles.py + gen01), gjort med Levin-grepa. Det er ikkje sitat frå Levin. Modellen er scena (bord, vegg, skjerm, auge), lysmodellen (lambertsk kordeopning), lovene (500 lx med U0 ≥ 0,4, ingen synleg kjelde over 3000 cd/m², stemning der veggdelen er ≥ 0,5) og konstruksjonen (vridd hylse på stong).

Utgangspunktet er k01: rett hylse med L 0,62 m, h 0,60 m, R 22 mm og smal opning (β 25°), på to hårtynne stålstenger. Ho treng 1461 lm og gjev U0 0,53. Ho svikter 13 mm under gesten, og fingerdyttet veltar ho (F_tipp/F_gest 0,34).

1. **Same mål med andre middel.** Settpunktet er lyspølen på oppgåva, ikkje lampa. Vridinga φ er middelet systemet nyttar for å finne attende til han.
   - Prøve: flytt k01 ±10 cm i djupn (y) og ±10 cm i høgd (z), og søk φ på nytt.
   - Føreseiing: etter at φ er søkt på nytt, endrar djupna Φ_krav med under 10 %. Høgda endrar Φ_krav med over 12 %, og U0 går motsett veg av Φ.
   - Utfallet som fell hypotesen: djupna kostar over 10 %, eller høgda under 12 %.
   - Følgje for forma: djupna er gratis og kan formast fritt. Høgda må festast av lova.

2. **Mønsterminnet ligg i mediet.** Kvar leppa skal sitje, er lagra i geometrien mellom auge, skjerm og oppgåve, ikkje i lampa. Ei rett hylse parallell med auglina har same avskjerming langs heile lengda (modellen gjev det eksakt). Når ryggraden vert bøygd, må opninga vri seg.
   - Prøve: bøy ryggraden og søk vringa φ(s) = φ0 + φ2·t².
   - Føreseiing: beste |φ2| ≥ 10°.
   - Utfallet som fell hypotesen: beste |φ2| < 5°.

3. **Minnet kan skrivast om.** Veltinga er ikkje ein eigenskap ved forma, men ved gesten (eitt fingerdytt). Eitt enkelt inngrep, å flytte gesten til eit vridegrep i éin ende (rein kraftpar), fjernar veltinga varig utan at forma elles endrar seg.
   - Føreseiing: med endegrep er tippmoment / gestmoment ≥ 5. Med fingerdytt er det 0,34.
   - Utfallet som fell hypotesen: under 2.
   - Følgje for forma: den eine enden vert grep og den andre ikkje. Asymmetrien kjem frå ein del som ikkje ber stabiliteten.

4. **Kreft er eit sjølv som har krympa.** Stengene i k01 optimerte berre sin eigen styrke og vart hårstrå. Kanalen til gesten var broten. Når stonga deler stresset (stivleik under gesten), vert ho ein del av lampa sitt sjølv.
   - Prøve: dimensjoner stonga etter svikt ≤ 2 mm under gesten.
   - Føreseiing: Ø ≥ 8 mm ved foten, og massen aukar med under 0,15 kg.
   - Utfallet som fell hypotesen: Ø < 6 mm (styrken var nok likevel), eller masseauke over 0,3 kg.

5. **Sjølvet sluttar der stresset sluttar å bli delt.** Grensa til lampa er lyspølen, ikkje kroppen. Lengda på hylsa er sett av breidda på oppgåva (0,60 m).
   - Prøve: varier L frå 0,30 til 1,00 m.
   - Føreseiing: U0 ≥ 0,40 krev L ≥ 0,45 m. Over 0,75 m stig Φ_krav med meir enn 10 % (lys utanfor oppgåva), medan U0 aukar med under 0,05.
   - Utfallet som fell hypotesen: U0 ≥ 0,40 allereie ved L ≤ 0,30, eller Φ flat over 0,75 m.

6. **Same stoff reknar fleire ting.** Om stengene og hylsekjernen vert eitt samanhengande alu-røyr (bøyle), reknar same stoff bering, stivleik, kjøling og leidningsføring.
   - Føreseiing: begge flagga «vaggar» og «for varm» forsvinn med same inngrep. Svikt ≤ 1 mm, A_kjøl ≥ 2 × krav og masseauke ≤ 0,35 kg.
   - Utfallet som fell hypotesen: eitt av flagga står att.

7. **Kontinuum, ikkje kategori.** Arbeid og stemning er ytterpunkt på éin akse, ikkje to modusar. Vridinga kan vere heile grensesnittet: fluksen fell lineært frå 100 % til 25 % langs vridinga.
   - Føreseiing: langs den korte vegen frå arbeid til stemning fell E_oppgåve monotont og veggdelen stig monotont. Synleg luminans er aldri over 3000 cd/m².
   - Utfallet som fell hypotesen: eitt steg som bryt monotonien, eller blending i sveipet.

8. **Nye former utan historie er ikkje tilfeldige.** Fri frå «skjerm på stong» bøyer lyslova ryggraden i plan, med endane fram mot brukaren (konkav mot auga), fordi hjørna på oppgåva ligg nærare auga enn midten.
   - Prøve: søk pilhøgd g frå −0,10 til +0,15 m (+ = endane fram) med vringa fri.
   - Føreseiing: beste g ≥ +0,04 m (≥ 5 % av L, så ho les) og Φ_krav minst 8 % lågare enn rett hylse, med U0 ≥ 0,40 og utan blending.
   - Utfallet som fell hypotesen: beste |g| < 0,03 m, eller vinst under 3 %.
