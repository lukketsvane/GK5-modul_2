You are GPT-6.2 Astra at xhigh, a CADQuery and Blender senior engineer. User demands very close silhouette to a supplied product concept reference. REAL CAD/render ONLY, no ImageGen or fake geometry. Existing code v2 produced a functioning CAD/Blender render but two prominent visual discrepancies remain. We need smallest coherent v3 revision to build.py and render_blender.py, nothing else, on private Konsept E WIP branch.

Actual v2 render looked like a very FLAT long ivory wing, with silhouette left tip (x116,y160), crown (x500,y105), right tip (x895,y195), on 960x640 render. Target reference in 1536x1024: left tip (~150,320), high crown (~970,150), right tip (~1385,390). So at matching projected widths 778/1235=.63, required vertical crown above left tip ≈107px, not current≈55px, and right end should be much more rounded and deep. Upper shell should have stronger longitudinal camber and more dramatic asymmetric dome; do NOT make a thick cylinder, keep single thin-walled vacuum-formed canopy. Increase upper hood crown height from 40 to ~65-70mm and keep its interior cavity shell wall 1.5mm; keep X envelope ~440mm, Y~155mm, physical ceiling max300mm. Make attachment saddles actually reach the shell roof again; do NOT leave floating roof pads inside tall shell.

Actual v2 lower dish has the right silhouette, strong white front lower lip, one continuous smooth warm opal surface. KEEP that, keep all base/post/hinge/links locations and kinematics. However current upper shell interior appears dark almost black behind the wide gap, whereas original reference has strong soft warm cream luminous upper hood inner surface from x150..1150. Introduce physically credible emission/illumination from existing fixed COB onto interior of the hood and the fixed opal surface. Prefer stronger 3200K COB + translucent lens material and add one physically motivated soft area source at precise LED bar location and orientation in Blender stage lighting (illumination only; NO added product mesh/geometry), sufficient to light underside roof. Keep contrast realistic, no artificial glow painted onto opaque shell. No change to CAD electronics or power routing.

The studio backdrop v2 is far too dark, nearly black along top: increase neutral warm taupe world and stage material brightness about +30-40% to resemble original grey background. Maintain black variant. Product shell matte ivory and gentle metal details.

Change renderer FAST output to existing 960x640; full output 1536x1024 retained. Keep camera from v2 unless obvious objective improvement. User wants actual CAD rendered via Blender Cycles, no generated picture.

CRITICAL: Existing v2 patch has already modified build.py and render_blender.py, and reports 23 valid part types, 9 sampled poses, 210 OCC distance calls, swept box 440 x165.4578 x240mm. Revised dome height70 would raise box to270 < hard 300. Narrow styling target160mm depth is already exceeded, don't silently claim otherwise.

Return a SINGLE COMPLETE EXECUTABLE PYTHON 3 SCRIPT raw source named astra_v3_patch.py, using narrow anchored substitutions on the provided CURRENT files. Save current files as *_before_v3.py if not already backed up. Compile modified files, call build.validate() with explicit 9 pose and valid parts + hood height match 65..70, and rollback atomically if invalid. Do not run Blender in patch. Only change required geometry and lighting. No comments or docstrings. Under 160 lines preferred. Print JSON status.

===BUILD.PY===
{BUILD}
===END===
===RENDER_BLENDER.PY===
{RENDER}
===END===