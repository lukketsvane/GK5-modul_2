You are GPT-6.2 Astra xhigh, senior CADQuery mechanical engineer and Blender Cycles product-visualisation engineer. Work ONLY on a PRIVATE in-progress Git worktree for Konsept E. User insists on the same physical silhouette as their one supplied design reference, NOT an AI-generated invented design. The current render is NOT close enough. Need genuine corrected CAD, no image generation, fake mesh, or screenshot manipulation.

REFERENCE IMAGE exact visible landmarks from 1536×1024:
- Warm grey/taupe studio, cream matte product.
- Crown of ONE opaque smooth asymmetric zeppelin shell begins at LEFT tip (x~150,y~320), rises in a long sleek camber to (x~950,y~150), and curls into a much FULLER softly-rounded RIGHT tip (x~1385,y~385). At left end body tapers to a slim leading edge, right half is noticeably deeper. Horizontal upper shell tip-to-tip projects ~1230 px.
- LARGE white luminous fixed lower dish spans about x~345..1190 (only 69% of upper shell projected length, not 90%). The front lip starts near (x370,y440), hangs to (x760,y575) in a smooth suspended scallop, then rises to (x1170,y456). It is a broad, solid, glowing smooth surface, not a narrow strip, not ribbed.
- End posts are located INWARD from upper shell tips, with projected posts centered ~x375 and ~x1220, the front horizontal lower crosspiece runs x330..1260. They look predominantly VERTICAL, not outward-raking triangular struts. Both have rounded caps and appear as thick square ivory metal bars, right one bigger because camera angle.
- Short visible 2-bar articulating hinges on both sides near (x360,y390) and (x1150,y340): all axes on the actual inboard support posts, not mounted externally beyond the canopy nose.
- Upper canopy is suspended above glowing lower bowl through a visible uniform slot; only one shell, one lens, not ribs/panels/accordion.
- Lower base crossbar visibly closes front of U frame, is roughly 72–78% of hood projected width, not 95%.
- Soft white rather than yellowish lit diffuser, subtle champagne link finish; no long dark bar visible across front of luminous lower dish. Camera 3/4 nearly front on, slight perspective, soft product shadows. End attachment visible but not giant hardware.

CURRENT MODEL made in gpt-6.2-astra, current committed WIP worktree: build.py, render_blender.py, export_meshes.py, components.json, validation.json, STEP assemblies. Revision v1 solved broader 40mm droop and moved base front bar, but image is still wrong: base support width ~as large as canopy, post hinges at x +/-231 OUTSIDE shell +/-220, both posts lean heavily, 400mm diffuser seems almost as wide as 440mm shell, hood symmetric and too flat, exposed dark bar in front of luminous diffuser. We need ACTUAL GEOMETRY CHANGES, not rendering trick.

Build CAD v2 should visibly reproduce reference proportions while remaining physically plausible:
1. Put hinge columns INSIDE the hood projected endpoints. Hood length 440mm stays, keep its ends +/-220mm. Move four-bar hinge pivot axes from x +/-231 inward to approx x +/-160..180mm and make bridge supports correspondingly narrower. Keep exact 4-bar linkage lengths 45mm, pivot spacing 22mm, and the 28mm rise & parallel unpitched upper canopy if possible; adjust all part geometries and world transforms coherently. Do NOT place hinge parts at old x after relocation. Keep single DOF.
2. Horizontal base width should become ~350mm rather than 420mm, retain broad front joiner and rear stability arms + correct holes, and correct vertical posts to be near vertical, not raked. Extend post height if necessary (about 15-25mm) to make open lamp taller and more like reference while not exceeding max H 300mm; if you raise posts, maintain all pin heights, moving cheeks, hood and fixed dish relative. Prefer no raise if complex and risky.
3. Diffuser length around 330..350mm, narrower than top 440, attachment and heatsink scaled consistently; keep substantially arched lengthwise forward lip, maybe 45-55mm at midspan, but no self-intersection, hold physical fixed mounting points, rear rigid mounting rib. Hide fixed LED rail behind the leaf's front silhouette from camera side (+Y), use narrow diffused LED in no wired pivot.
4. Add asymmetry to upper shell loft (left thinner point, right fuller), without adding bulging inaccurate ribs, preserve constant-ish thickness and manufacturable PETG shell. Keep 155ish depth max and the 36ish mm dome height unless evidence requires slight increase. Reference is NOT fat cylindrical full capsule.
5. Only 1 continuous smooth upper shell and 1 continuous broad glowing lower dish. No extra visible structure across the light face. Thin brackets & satin warm hardware, not massive copper exposed arm ends. Keep material simple.

CHANGE BOUNDS/TESTS HONESTLY: existing validate() in build.py currently expects specific numeric targets (420, 400, etc). Update only those targets to revised intended sizes. Retain real OCP solid distances and 9 pose test, also assert no unintended overlaps; additional tests for correctly inward x support, base ratio, valid diffuser. Existing validation is not certified mechanical feasibility, never claim it. For any conflicting design requirement, prefer minimal coherent geometry rather than unsafe fakery.

Blender script render_blender.py: camera is x=.16,y=.75,z=.37, target z=.11, current orthographic makes shell top too flat. Revise to low-ish nearly frontal 3/4 x=.22,y=.78,z=.29 or similar, enough visible rear lip. Reference shell is higher arched than old render; adjust actual canopy cross section rather than primarily optics. Background warm neutral medium gray, no washed-out white. Bright opaque/opal light with highlight falloff, soft glow. No AI-generated product geometry.

You MUST return a SINGLE COMPLETE EXECUTABLE PYTHON3 SCRIPT as raw code (no markdown, comments, docstrings) named astra_v2_patch.py, which edits build.py and render_blender.py safely using exact anchor replacements, AST range replacement or assertions, no speculative changes. Save full original versions as *_before_v2.py before modifications. Make changes atomic: source compiles, fail loudly if anchor missing, do not accidentally clobber unrelated files, do not rewrite all project code. Include importable check post patch with model.catalogue() & validate() and exact geometry assertions. If implementation fails after patch, revert changed files but keep backups. Print concise JSON results. Test physics plausibility, not manufacturing certification. Keep explicit physical CAD dimensions and transform alignment, avoid superficial render-only tricks. Target full script under 350 lines if possible.

REFERENCE CURRENT SOURCES FOLLOW. Make your patch against exact names/values, not guesses.
===BUILD.PY===
{BUILD}
===END BUILD.PY===
===RENDER_BLENDER.PY===
{RENDER}
===END RENDER_BLENDER.PY===
===OLD VALIDATION===
{VALIDATION}
===END VALIDATION===