# LES.md — miljo.py: one design folder in, four product photos out

`miljo.py` builds a lamp from the toolkit's output at real size in Blender 5.3 (bpy as a Python module) and renders it with Cycles on the CPU in two sets: a walnut sideboard against a lime-plaster wall (day, dusk, desk) and a dark-grey studio sweep (the mode shot).
`M = /tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/nord4/miljo`
`PY = /tmp/claude-0/-home-user/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/bl/venv/bin/python`

## Call

```bash
$PY $M/miljo.py -- <design folder> [--arbeid DIR] [--ut DIR] [--namn STEM] [--skot miljo-dag,miljo-kveld,miljo-arbeid,modus]
                                   [--rask] [--prover N] [--breidd PX] [--kraft F] [--blend]
L=/tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe
$PY $M/miljo.py -- $L/nord3/globus/b1s --ut $M/ut --namn maane          # all four, full size (b1a found as the work pose)
$PY $M/miljo.py -- $L/kule/kbord --rask --skot miljo-dag                # one 640 px preview, ~15 s on free CPUs
```

- `<design folder>`: the folder that holds `konsept.ts`, or its `ut/`. `ut/scene.json` is read first: its `delar` carry `material`, `farge` and `speglSide`, plus the extra parts that are not in `delar.json` (a cradle, for example), and its `utstyr` and `lys`. When there is no scene.json, the script falls back to `ut/delar.json`.
- `--arbeid DIR`: the work pose. Without it, the script looks for a sibling folder whose name has its last `s` replaced by `a` (`b1s` → `b1a`, `rs` → `ra`). Without a work pose, `miljo-arbeid` uses the main pose and `modus` shows one lamp.
- `--ut` (default: the design's `ut/`) · `--namn` (default: `namn` in scene.json) · `--skot` any subset, in any order.
- `--rask`: 640 px wide, 32 samples, noise threshold 0.06. `--prover N` sets the sample cap, and `--breidd PX` sets the width while keeping each shot's aspect ratio.
- `--kraft F` scales every lamp source (default 1). `--blend` also saves `<stem>-<shot>.blend` next to the picture.
- Exit codes: 0 ok · 3 = a lamp point falls outside the frame (`utanfor ramma`) · 1 = crash or unknown shot name.

Output files: `<ut>/<namn>-miljo-dag.png`, `-miljo-kveld.png` and `-miljo-arbeid.png` at 1600 × 1100, `-modus.png` at 1440 × 1000, and `<namn>-miljo.json` with the timings, CPU seconds, exposure, frame and every check below.

## What it prints, and what each check proves

```
maane: 16 delar · 8 utstyr · arbeid …/nord3/globus/b1a · 128 prøver
  miljo-dag      <wall s>  …/maane-miljo-dag.png  ramme [-0.209, 0.209, -0.44, 0.68]
  plater        plater 16 · hol 2 · flateavvik_pst 0.0 · utstyr 8
  miljo-dag     kontakt_mm 0.0 · vegg_mm 161.1 · fot_inne_mm 159.4 · under_topp 0
  miljo-arbeid  kontakt_mm 0.0 · vegg_mm 70.0 · fot_inne_mm 70.2 · under_topp 0 · props_i_lampa []
  cpu-s maane-miljo-dag.png 727.1 · …
  maane-miljo-dag.png: eksponering -0.11 EV · svart kant ingen · utbrent 0.01 %
```

- `flateavvik_pst`: the cap area of every extruded plate against `areal` in the toolkit, which is net of holes and slots. A value of 0.0 % means each plate is a solid with exactly the cut profile: outline, slots and holes. Both test designs and Rist read 0.0.
- `kontakt_mm`: the lowest point of the lamp (plates and hardware) minus the top surface. It is 0.0, so nothing floats. `under_topp`: lamp vertices below the top inside its footprint. It is 0, so nothing sinks in.
- `vegg_mm`: the gap from the lamp's backmost point to the wall. `fot_inne_mm`: how far the foot stays inside the top's edges. `props_i_lampa`: props whose box contains a lamp vertex below the prop's height.
- `ramme`: where the lamp's points land in the picture, from −1 to 1 (x, y). Anything beyond ±1 would be clipped, and the run would exit 3.
- `svart kant`: an edge strip (1 % of the width) that is under 60 % of the brightness just inside it. `utbrent`: the share of pixels at full white.

## The set

- Sideboard: top surface at 800 mm, a 45 mm walnut top, a 14 mm shadow reveal set back 18 mm, two 230 mm drawers with a 3 mm split, doors and a plinth below. Depth is max(480, lamp depth + 200) mm, or for the desk max(600, lamp depth + 360). The wall sits 20 mm behind it.
- The lamp stands at the centre of the top (in arbeid, pushed back to 70 mm from the wall). Its lowest point sits exactly on the top. A black power cord (a `leidning` with no colour or a near-black colour) is laid flat on the top, clamped to the back edge, and dropped behind the sideboard. A coloured `leidning` (Maane's yoke) is a structural tube and is left as drawn.
- Room: a lime-plaster wall (warm grey-beige, mottled, fine trowel bump) and a left side wall placed outside the frame. The side wall has a 1.35 × 1.43 m window with a mullion and a transom, and a sheer linen curtain hangs in front of it (folds, opacity rising toward grazing angles). The ceiling is shadow-only, there to stop the sun.
- Day: a sun at 5200 K, 3 W/m², 1.3° wide, aimed through the window at the wall behind the lamp, so the curtain folds and the window bars fall on the wall. The sky is a 6500 K area light inside the window, with a faint warm world fill. Lamp at 4 %.
- Dusk: sun off, the window light at 14000 K and tinted blue, the world dim blue, the lamp at 100 %.
- Desk: the dusk light plus a 24" monitor (545 × 322 mm, dark-mode document on screen, a 3000 K bias light on the wall behind it), an A5 notebook with a pencil, and a cup of coffee. The monitor goes on the side away from the cord's end. The camera looks across toward it.
- Mode: a dark-grey seamless sweep with key, fill and rim area lights scaled to the camera distance, a 55 mm lens at 32° from above, and the two poses side by side (main pose on the left). Lamp at 12 %.

Camera: 36 mm sensor and 50 mm lens. For dag and kveld it sits 16° to the right and 7° above, at f/5.6, focused on the lamp. Its distance and lens shift come from the lamp's own vertices, so any size works: the lamp spans at most 62 % of the frame width and 56 % of its height, with its foot at 28 % from the bottom. In arbeid the fit includes the cup and the notebook; the monitor may be cut by the frame edge.

Exposure is automatic. A 220 px pre-pass at 24 samples is rendered with the bulb glass hidden from the camera. For dag, the median goes to 0.2, capped so that p99 ≤ 5. For kveld and arbeid, a second, lamp-only pass sets the lamp's hottest 0.3 % to 2.4, capped so that the ambient-only median stays ≤ 0.035 (the room stays dusk). For the studio, the median goes to 0.07 (the dark sweep), with p99 ≤ 4. View transform: AgX, Medium High Contrast.

## Materials (matched to the toolkit's names)

| toolkit | here |
|---|---|
| `bjork` | pale birch face with grain and fibre along the part's own u axis, satin; every cut edge charred dark brown with faint ply bands |
| `poppel` | paler, less grain; charred edge |
| `mdf` | matt `#b89472` (or `farge`); dark brown-black edge |
| `papp` | matt cardboard, brown edge |
| any wood with `farge` | painted matt in that colour; charred edge |
| `akryl-opal` / `opal` / `akryl` | milky translucent (62 % translucent + a glossy diffuse layer); edges brighter |
| `pp` | more translucent, rougher |
| `spegl` | the `speglSide` face (+1 = w = t, −1 = w = 0, missing = both) is a silver mirror under a clear coat; the other face is matt `farge`; edges pale grey-green acrylic |
| `utstyr` with `metall` and a warm colour | satin brass |
| `utstyr` with `metall` and a grey colour, or a `sylinder` with no colour | brushed aluminium, anisotropic around the part's axis (spun look) |
| `leidning`, black or no colour | black textile cord with a braid bump and sheen |
| anything else with `farge` | powder coat in that colour, a fine orange-peel bump, roughness from `ru` |
| `sokkel` with no colour | black bakelite |
| `paere` | the frosted glass itself is the emitter: 2700 K blackbody, 9 W per bulb × shot factor × `--kraft`, spread over the glass area |
| `lys` (LED points) | a hidden 2700 K sphere light, 4 W × `styrke`, with the scene's `radius` |
| set | walnut (oiled, satin coat, pores), lime plaster, sheer linen, painted window frame, matt ceramic, bookcloth, aluminium |

Bent parts (`krumming`) are cut into 2–6 mm strips along u and rolled with the toolkit's own formula. `boygd.nett` is taken as given.

## Render settings

Cycles on the CPU with 4 fixed threads. 128 samples at most, with adaptive sampling (threshold 0.04) and OpenImageDenoise (albedo + normal, accurate prefilter). Bounces: 10 max, 3 diffuse, 5 glossy, 8 transmission, 24 transparent. Indirect clamp 6, filter glossy 0.6, reflective caustics on.
Measured at 400 px on Maane dag: path guiding cost 3× (turned off), the light tree cost 16 % (turned off), and the curtain cost 29 % until it was hidden from indirect rays and the sky light was moved inside it.

## Timings

Measured on the final runs, at 1600 × 1100 (modus 1440 × 1000), 128 samples at most. Another agent's headless Chromium held about 2 of the 4 CPUs the whole time (load average 6–8), so the wall times are pessimistic. CPU seconds count all four render threads, so CPU-s / 4 is the wall time on four free CPUs.

| shot | Maane wall | Maane CPU-s | kbord wall | kbord CPU-s |
|---|---|---|---|---|
| miljo-dag | 243 s | 716 | 500 s | 919 |
| miljo-kveld | 290 s | 654 | 255 s | 1001 |
| miljo-arbeid | 306 s | 833 | 260 s | 1020 |
| modus | 166 s | 368 | 137 s | 537 |
| all four | 16.8 min | | 19.2 min | |

- On four free CPUs that is about 2.7 / 2.7 / 3.5 / 1.5 min for Maane, which is inside the 4-minute aim. kbord is about 3.8 / 4.2 / 4.3 / 2.2 min: its bare bulb lights a dense lattice of birch from inside, so more pixels need all 128 samples. It sits at or just over the aim even alone. `--prover 96` takes about a quarter off.
- Under the shared load seen here, a full four-shot run took 17–19 minutes of render time.
- Each shot also renders one or two 220 px exposure pre-passes (1–3 s each), and a scene build takes about 1 s.
- `--rask` (640 × 440, 32 samples): 14–16 s per shot on free CPUs (about 57 CPU-s), and 35–60 s under the shared load.
- What the speed came from (Maane dag at 400 px, 128 samples, CPU-s): 94 as first built · 69 with the curtain hidden from indirect rays and the sky light moved inside it · 59 with the light tree off · 43 with the noise threshold at 0.05. Path guiding tripled the time at 640 px and is off.

## Test pictures

In `M/ut/` (final, full size), plus `M/ut/oversyn.png` (all eight, reduced):

- `maane-miljo-dag.png` · `maane-miljo-kveld.png` · `maane-miljo-arbeid.png` (b1a pose) · `maane-modus.png` (b1s left, b1a right)
- `kbord-miljo-dag.png` · `kbord-miljo-kveld.png` · `kbord-miljo-arbeid.png` · `kbord-modus.png` (one pose: kbord has no work-pose folder)
- `maane-miljo.json` and `kbord-miljo.json` hold the timings, CPU-s, exposure, frames and checks. The kbord JSON covers the second run (kveld and arbeid, rendered again after the dusk exposure rule changed). The first run's JSON is kept as `.kbord-miljo-fyrste.json`, and `kjoering.log` / `kjoering2.log` hold both console outputs.

`M/prov/` holds 640 px previews from development (not all made with the final code), including `rist-*` (nord3/raster/rs: opal disc, LED points, a bent MDF skirt, a coloured cord). That design is not one of the two asked for, but it is the one that exercises opal, `lys` and `krumming`.

Checks on the finals: every plate's cap area matched the toolkit's net area (0.0 %: Maane 16 plates with 2 holes, kbord 15 with 3, the cradle rings included). Contact is 0.0 mm and nothing sits below the top. The wall gap is 161 mm for Maane (70 mm in arbeid) and 134 mm for kbord (70 mm in arbeid). No prop touches the lamp. No frame is clipped. Burned-out pixels: 0.01 % for Maane, and 1–2 % for kbord, which is the bare globe bulb. kbord arbeid is flagged `svart kant botn`: the front edge of the desk falls off into the dark room, as intended.

## What still looks fake (honest list)

Looked at against the Kongle-miljo reference:

- **Curtain light (dag).** The sun comes through the window, the curtain and the window bars, but what reads on the wall is mostly one soft diagonal bar shadow, a soft gradient and the lamp's crisp shadow. The reference's distinct vertical fold streaks are weak here, and there are no branch shadows. A gobo texture would make them reliable, but it was not built.
- **Walnut.** Procedural. At picture size it reads as dark oiled walnut, but up close the figure is long straight streaks with no cathedral grain and no board joints, and the drawer fronts carry the same pattern as the top. The top's front edge is a 2 mm round.
- **Mirror light (Maane kveld).** Reflective caustics are on, but at 128 samples the denoiser turns the mirror-thrown pattern into one large soft glow with the shell's silhouette. A real mirror lattice would throw crisper bright bands onto the wall.
- **Bulbs.** The glass is a uniform 2700 K emitter. A bare globe in view (kbord) burns to a flat white disc in every shot: 1.5 % of the pixels in kveld, and still about 1.5 % in dag at 4 % power. That is how a photo of a bare bulb looks, but it flattens the bulb's shape.
- **Diffusers.** Opal and pp pass shadow rays straight through, tinted. Without that, no direct light reaches anything behind a diffuser. The cost is that light behind an opal disc casts point-source shadows instead of the soft spread a real diffuser gives.
- **Plates.** Laser edges are perfectly sharp and square: no kerf taper, no engraved addresses, and `rille` score lines are not drawn. Birch faces are clean, with no sanding marks or edge burn on the face.
- **Hardware and props.** Simple lathe and cylinder stand-ins, with no switch and no screws, and Maane has no power cord because its scene has none. The monitor shows a generic dark document. The cup, notebook and pencil are clean CG, with no wear and no paper texture. In kbord arbeid the monitor is cut by the top of the frame.
- **Room.** Only the back wall, a side wall out of frame, a floor and a shadow-only ceiling: the bounce light is plausible but not a measured room. The left edge of the dag frame falls off a little darker toward the window corner.
- **Exposure** is automatic per shot, so two lamps are not comparable in brightness. Lamp power is in Blender watts chosen by eye (9 W per bulb at 100 %), not lumens.
- **Not supported.** Pendant and wall lamps (`heng`, `vegg`) are still placed standing on the sideboard. Engraving and `rille` are ignored. A GLB-only design (no plates in JSON) is not read.
