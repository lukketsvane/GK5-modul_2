You are a senior industrial designer and a FreeCAD/OpenCascade CAD engineer. You are improving a table-lamp concept in a student project (AHO, GK5 module 2) for Northern, the Norwegian lighting brand. The concept is called FURU (concept B). Appended below: (1) Northern's final design brief, (2) the project's requirement specification (IDs E1–B7, "Skal" = must, "Bør" = should), (3) the complete FreeCAD 1.0 macro of the current revision, Furu-B01. Attached images: the original mood reference photo (black studio), then four Blender renders of B01 made from the exact CAD: front closed 0°, front open 40°, 3/4 closed, 3/4 open.

Keep the concept: six continuous rolled aluminium shells share two parallel tubes; raising the rear (regulating) tube tilts all six shells together and lets light out between them; closed, the body is a calm scaled spindle. The name is FURU. The words "Kongle"/"kongla" must not appear anywhere (code, labels, file names, documents).

Verified facts about B01:
- Closed 487.0 × 230.6 × 233.2 mm; open (40°) 473.5 × 230.6 × 243.8 mm, from the tessellated geometry. The 496.8 mm in B01's bounds.json is an artefact of OCC's loose BoundBox on BSpline faces; use mesh-based bounds.
- 97 parts, modelled mechanical mass 804.6 g; total budget incl. 205 g external power supply, cables, LED and reserve 1112.6 g (F8 limit 1200 g).
- No crossings between moving groups from 0° to 40° in 5° steps, apart from the two intended friction-spring contacts (F3F/B3F, F4F/B4F).
- Light: two 150 mm LED bands, 1.44 W in total, under an opal diffuser on the axis. The renders show only a faint glow between the shells.

My reading of the main gaps against the requirement spec. Verify and prioritise yourself:
1. F3, B3, F2: 1.44 W cannot give work light (350 lx evenly on 0.6 × 0.4 m from the lamp alone; 7.5 W on cord). The move between mood and work light must be one action under 10 s; ideally the same tilt that opens the shells should take the lamp from a soft glow to a downward work light.
2. F1, F5, F10: low glare. No light source visible or mirrored in a screen from 25–60 cm above the table; luminance under 1500 cd/m² (500 in mood mode); soft face light for video calls.
3. F4, F11, T4, F7: at most 3000 K, warmer when dimmed (2700 → 2000 K), Ra ≥ 90, stepless dimming to 2 %.
4. B1, B2, T6, M2, B7: the owner replaces the light module in under 5 min with at most two common tools; no glue between material fractions (B01 glues the ballast disc and the diffuser); at most 10 main parts; a documented module interface.
5. T2, F8, F9: must not tip (check the centre of mass in the open state on a tilted surface), at most 1.2 kg in total, footprint at most 200 cm².
6. E1, E2, E3, M1: homely, warm, simple, Northern's quality level; the form should explain its use. How one hand grips and raises the rear tube must be obvious and pleasant.
7. Form: in the reference photo the body reads as one calm, taut lens; B01 reads more like stacked cones. Refine proportions and shell outlines so the closed state is calmer and the open state clearly reads as opening scales.

Task: produce revision B02 as one complete FreeCAD 1.0 macro that makes concrete, measurable improvements on these points while keeping the concept recognisable and manufacturable.

Hard technical contract (my build and QA pipeline depends on it):
- Runs headless with `freecadcmd Furu-B02.FCMacro`. Output root from the environment variable FURU_DIR (default: a folder next to the macro). Writes packet/Furu-B02.FCStd, packet/Furu-B02.step (named AP214 assembly in mm, at 0°), packet/Stykkliste.csv (same columns as B01: ID;Del;Gruppe;Materiale;Volum_mm3;Tettleik_g_cm3;Masse_g;Prosess, ';'-separated, UTF-8 with BOM), packet/Rullesjablonar/S01–S06.dxf, work/mesh0.json and work/mesh<max>.json (same structure as B01) and work/bounds.json (mesh-based).
- Keep the structure: one root App::Part labelled "Furu B02"; the spreadsheet with A1 "Opning (0 til N grader)" and B1 aliased Opening; shell groups App::Part labelled "41 Skjell 1" … "46 Skjell 6" whose Placement expression is a pure rotation about the Y axis through the group origin (origin on the hinge axis), using the same sign convention as B01; exactly one translating drive group (the regulating tube) whose Placement follows p(a) = (0, 0, Z_axis) + R_y(s·a)·d for a constant offset vector d and the same sign s as the shells; every other group static. Clear part labels "ID Name"; every solid valid; every part in exactly one group.
- Explicit material strings as in B01 (e.g. "EN AW-5754 H22", "EN AW-6061 T6", "AISI 304", "POM-C", "Opal polykarbonat", "Silikon"); emitting parts must have a material string containing "LED" (purchased modules may be envelope solids); cables "kabel" or "leidning".
- No GUI modules (no FreeCADGui, no ImportGui): only FreeCAD, Part, Mesh, Import, Spreadsheet and the Python standard library.

Output format: first one ```python block with the complete macro (no ellipses or placeholders), then one ```markdown block in Nynorsk titled "Endringar B01 → B02" listing the changes by requirement ID with the new key numbers: dimensions closed and open, mass budget, LED power and luminous flux, estimated illuminance on the 0.6 × 0.4 m field at a stated height, part count and main-part count.

This is round 1 of 2. I will build your macro in FreeCAD 1.0, test the mechanism for crossings every 5°, render it in Blender and send back measurements and renders for round 2.
