# Konsept B – Furu

Bordlampe der seks samanhengande aluminiumsskal deler to parallelle røyr. Når bakre røyr blir løfta, vippar alle seks skala og slepper lyset ut. B02 og B03 er laga av GPT-6.2 Astra i to rundar, med bygging og kontroll i FreeCAD 1.0 og Blender 5.3 mellom rundane.

| Revisjon | Lukka (mm) | Open (mm) | Komplett masse | Lys |
| --- | --- | --- | --- | --- |
| Furu-B01, utgangspunkt | 487,0 × 230,6 × 233,2 | 473,5 × 230,6 × 243,8 ved 40° | 1113 g | 1,44 W stemningslys |
| Furu-B02, Astra runde 1 | 487,5 × 243,5 × 287,3 | 474,5 × 243,5 × 313,9 ved 40° | 1149 g | 6,1 W arbeidslys og vaskelys, dimming med løftet |
| Furu-B03, Astra runde 2 | 487,5 × 243,5 × 260,3 | 479,3 × 243,5 × 296,3 ved 30° | 1202,9 g, 2,9 g over grensa | som B02, med kortare lyssko i falden |

Måla er tesselerte nettmål utan lausleidning. Lystala er Astra sine prosjekteringsoverslag, ikkje måledata.

## Innhald i kvar revisjonsmappe

- `Kjelde/*.FCMacro`: geometrikjelda. Køyr med `freecadcmd` og set `FURU_DIR` til ei utmappe.
- `*.FCStd`, `*.step`, `Stykkliste.csv`, `Rullesjablonar/`: CAD, stykkliste og skjeremål.
- `analyse/`: stabilitet, massebudsjett, mekanisme, friksjon og service frå bygginga.
- `endringar.md`: Astra si grunngjeving. `Endringar-B0x.md`: tal frå den faktiske bygginga.
- `*.blend`: Blender-scene. Vel «Furu · styring» og endra «Opning» for å opne og lukke lampa.
- `render/`: studiobilete lukka og open.

## Verktøy

- `verktoy/bygg_cad.py`: byggjer makroen i FreeCAD 1.0, hentar riggen, lagar GLB og les mål.
- `verktoy/furu_bygg.py`, `furu_sjekk.py`, `furu_render.py`: Blender-scene, kollisjonssjekk og rendering.
- `verktoy/astra.py`: køyrer Astra-rundane mot OpenAI med nøkkelen i miljøvariabelen `OPENAI_API_KEY`.
- `astra/`: spørsmåla og svara frå Astra-rundane.
- `arkiv/astra-skisse/`: det første forsøket, der Astra modellerte lampa direkte i Blender.
