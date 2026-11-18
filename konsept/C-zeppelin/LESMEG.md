# Konsept C: Zeppelin

Mekanisk proof of concept for ei bordlampe med ni synkroniserte, utfaldande lamellstasjonar. Formprinsippet kjem frå referansebiletet, men sjølve hengslings- og tannstongmekanismen er rekonstruert for å kunne modellerast og prøvast fysisk.

## Verkemåte

Kvar stasjon ber to spegelvende lamellar på ein felles 5 mm aksel. Akselen er lagra i to 5 × 10 × 4 mm lager. Eit modul 1-tannhjul med 20 tenner driv ei felles, ført tannstong. Knott på endestasjonen gir éin styrt fridomsgrad. Lamellane roterer samla frå 38° (lukka) til 10° (open), med 4,887 mm slaglengd i tannstonga.

Lamellane er 0,6 mm laserskjerbare plater med sylindrisk bøy og smal midje rundt gjennomgåande akslar. Fire ulike djupnelag lèt dei overlappe i sideriss utan å kollidere. Klemfeste, låseskruar, lager, tannhjul, føringar, fot og den faste lysføringa er eigne CAD-delar. LED og leidningar står i ro.

## Leveranse

- **viewer.html**: offline 3D-vising med frie kamerarørsler, animasjon og glidar. Opne i Chrome.
- **renders/**: fire ekte Blender-rendringar og ein 25-rammers GIF-animasjon.
- **C_zeppelin.blend**: redigerbar Blender 5.3-scene.
- **samansetjingar/**: fullstendige STEP-assemblyar i lukka, mellom- og open stilling.
- **delar/**: STEP-modellar for alle 43 unike delar.
- **build.py**: kjeldekode for parametrisk konstruksjon.
- **scene.json**, **viewer_template.html**, **generate_viewer.py** og **render_animation.py**: grunnlaget for den bevegelege visinga.
- **verification_final.json**: geometrisk validering og målingar.
- **astra_6_2_review.md** og **astra_6_2_visual_review.md**: tekniske vurderingar frå gpt-6.2-astra gjennom OpenAI-API.

## Verifisert digitalt

45 gyldige CAD-solidar, 151 komponentinstansar og tre eksporterte STEP-stillingar. Med den reviderte bøygde geometrien er dei undersøkte klaringane ved 10°, 24° og 38°: mellom lamellar minst **9,95 mm**, lamell mot nabofeste minst **8,10 mm** og lamell mot naboaksel minst **6,68 mm**. Eldre yttermål for flate lamellar er ikkje lenger gyldige. Eigen aksel har **0,22 mm** nominell radiell klaring i plateholet. Tanninngrep kontrollert i tre stillingar utan målt solid-overlapp, men utan full toleransemodell.

## Regenerering

Køyr frå denne mappa med Python 3.13, CadQuery, Pillow og lokal Chrome:

    py -3.13 build.py
    py -3.13 generate_viewer.py
    py -3.13 render_motion.py
    py -3.13 verify_fast.py

## Attståande

Dette er **ikkje** ein produksjonsgodkjend lampe. Fysiske testar må stadfeste skruelåsing og tannslark, toleransar, handkraft, tilstrekkeleg stivleik i 0,6 mm lamellmateriale, klemfare, veltetryggleik og varmeavleiing frå LED. Gjenbrukte monitorfilmar kan nyttast som lysdiffusorar, men er ikkje automatisk sterke nok til å bere lamellane.

Ingen endringar er gjorde i dei eksisterande Ruta- eller Northern-modellane.
