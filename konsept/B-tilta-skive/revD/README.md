# Northern · konsept B · referansetilpassa Rev D

Denne revisjonen gjeld den tilta skivelampa i referansebiletet, ikkje det eldre B Over. Den tidlegare STEP-samanstillinga Rev A og Blender Rev B/Rev C er urørte.

## Resultat

- `Concept_B_RevD.blend`: redigerbar scene i Blender 5.3 med eigne objekt, material, lys og kamera.
- `renders/B_REFERENCE_MATCH_REV_D.png`: 1536 × 1024, Cycles 64 sample, same kameravinkel som referansen.
- `renders/B_ALTERNATE_3_4_REV_D.png`: 1280 × 853, Cycles 42 sample, ein annan vinkel.
- `astra_review.md`: fullført formgjennomgang frå `gpt-6.2-astra` med `reasoning.effort=max`.
- `render_release.py`: renderar dei to bileta frå den lagra Blender-scena.

## Verifisert

- Krona, lyspanelet, reflektoren og sokkelen er Blender-meshar, ikkje biletegenererte motiv.
- Midten av topplata hadde feilvendt normal. Han er retta; nabonormalane har skalarprodukt om lag +1.
- Lysopninga ligg på evaluert underskålflate og er ein eigen oval diffusor med mørk fals.
- Bakgløden har gradert overflateintensitet, ikkje ein einsfarga oransje kile.
- Nedste fremre del av underskåla er løfta og trekt inn mot aksen for å minske den for djupe skålprofilen.

Mål for referanseutsnitt 1536 × 1024: stor skive frå kring x446, y134 til x1144, y645; lysvindauge kring x705–1067 og y631–667; bakglød langs venstre bakre boge; J-fot kring x463–847 og ned til y880. Tala er avlesne frå eitt bilete og er ikkje produkteigenskapar.

**Avgrensing:** Dette er ei formvisualisering. Éin perspektivreferanse kan ikkje fastsetje skjult geometri eller garantere pikselidentitet. Blending, faktisk lysmengde, termikk, elektrisk konstruksjon, toleransar og veltesikkerheit er ikkje validerte. Ingen påstand om produksjonsklare CAD-filer.
