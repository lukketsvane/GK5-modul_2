# Konsept C, to parallelle rør

Denne varianten erstattar den feilaktige mekanismehypotesen med ni individuelle tverrakslar og tannstong. Den gamle modellen er ikkje endra.

## Prinsipp

To kontinuerlege, parallelle røyr langs X-aksen, med 20 mm avstand mellom senterlinjene, roterer motsatt veg. Eit nominelt 1:1-tannhjulpar (modul 1, 20 tenner) koplar røra. Det fremste røret ber seks øvre skjeldelar og ei langsgåande indre lysluke, det bakre seks nedre skjeldelar og den andre lysluka. Til saman dannar dei **seks skjel langs lampeskjermen**. Ein fast LED-kanal ligg mellom røra. Røra kan vridast 0–32 grader for å sleppe meir nedretta lys. Særskilde skjelflater er skorne som tynne, utviklingsbare (sylindrisk bøygde) plater.

Ved 0 grader møtest lyslukene med ei nominell lysopning på 1,8 mm. Ved 32 grader er lysopninga 26,82 mm. Dette er geometrisk fri opning, ikkje lysmålt lumen, lux eller blendingskontroll.

## Filer

- `build.py`: parametrisk CAD-geometri og samansetjing i CadQuery.
- `samansetjingar/lukka.step`, `halvopen.step`, `open.step`: tre CAD-stillingar.
- `delar/`: individuelle STEP-delar.
- `scene.json`: CAD-meshar og transformasjonar for Blender.
- `render_blender.py`: render fire faktiske CAD-visingar.
- `C_two_tubes.blend`: redigerbar Blender-scene med animerte rør.
- `renders/closed_front.png`, `open_front.png`, `closed_3q.png`, `open_3q.png`: Blender-rendringar på svart bakgrunn.
- `renders/Blender_kinematikk.gif`: 25 Blender-rendra animasjonsrammer.
- `verify.py` og `verification.json`: målt nominell avstand mellom lyslukene og geometritest av tannhjula i fem stillingar.
- `astra_two_rods_review.md`: vurdering frå gpt-6.2-astra via OpenAI API.

## Kva som er kontrollert

- 43 gyldige CAD-deltypar og 37 delinstansar, med seks skjel (tolv skjeldelar).
- To akslar og motrotasjon frå 0 til 32 grader.
- Oppmålte lyslukeklaringar ved fem stillingar; minste nominelle klaring mellom shutterflak 1,97 mm.
- Spurhjul har ingen solid-overlapp i dei fem kontrollerte stillingane. Nominell flateavstand i desse stillingane er om lag 0,0004–0,0021 mm.

## Kva som ikkje er stadfesta

Lysfluks og blending, plastisk forming, dreiemoment og slark, nødvendig toleranse/backlash i tannhjula, sikring av skjelflater og lysluker på akslane, varme og elektrisk tryggleik, stabilitet og kollisjonar mellom alle brakettar. Her trengst prototype av minst to akslar, to lysluker og tre naboskjelflater før produksjon. Skjelflatene i denne første varianten er heller ikkje geometrisk identiske med referansebiletet.

## Kjøring

```powershell
py -3.13 build.py
py -3.13 verify.py
& 'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe' --background --python render_blender.py
```
