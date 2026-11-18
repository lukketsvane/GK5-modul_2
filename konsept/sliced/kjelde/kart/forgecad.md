# ForgeCAD for the lamps: what runs, what it gives, what it cannot

Everything below was run on 2026-11-17 in this container (Node 22, 4 CPUs). `L` is
`/tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe`.

**Verdict.** The CLI runs here, headless, including PNG renders (it finds `/usr/bin/google-chrome` itself).
`forgecad@0.13.0` is installed in `$L/forge` (`$L/forge/node_modules/.bin/forgecad`), OCP 8.0 (cadquery-ocp)
in `$L/forge/venv` for independent read-back. The fallback STEP writer (`tilstep.ts`) was not needed and not written.
The skill's `references/*.md` do not exist on disk; the same docs ship in
`$L/forge/node_modules/forgecad/dist-skill/docs/generated/*.md` (core, sketch, curves, sdf, viewport, lib ...).

**Licence, the owner must know.** `export step`, `export report`, `export cutting-layout` print
"Production output ... Free to run for personal non-commercial use. Pro covers human-operated commercial CAD work."
They run fully on the free tier. `capture gif|mp4` and `render hq` refuse: "requires a ForgeCAD Pro license".

## Recipe A: laser assembly JSON -> named, coloured STEP + diagnostics + PNG

```bash
cd /home/user/slicer.iverfinne.no
npx tsx $L/verkty/tilforge.ts <samling.json> <utmappe> [--sirklar] [--toleranse=0.02] [--utan-bilete] [--utan-step] [--feit] [--kant=off|thin|bold]
$L/forge/venv/bin/python -I $L/verkty/lesstep.py <utmappe>/<namn>.step <utmappe>/<namn>.venta.json [--overlapp] [--liste]
```

Input contract (mm). The flat frame is the engine's own: outline in XY, plate from z=0 to z=tjukn, and
`matrise` is exactly `MontDel.ferdig` (column-major: u, v, n, origin = o - t/2 n; `lib/montasje.ts:34-42`).

```json
{ "namn": "prove14", "delar": [ { "namn": "R01", "tjukn": 4, "omriss": [[x,y],...], "hol": [[[x,y],...]],
    "matrise": [16 numbers, column-major], "farge": "#c9a36b", "steg": 1, "sprengt": [dx,dy,dz] } ] }
```

`farge`, `steg` (1-based assembly step), `sprengt` (explode vector at Sprengt=1; default: away from the
assembly centre) and `hol` are optional. Names must be unique; the tool stops on a non-rigid or mirrored matrix.

It writes into `<utmappe>`: `<namn>.forge.js` (self-contained model), `<namn>.venta.json` (expected volume and
box per part, from polygon area x thickness), `<namn>.diag.txt` (`forgecad run --details --connectivity`),
`<namn>.step`, `<namn>_iso.png _front.png _top.png _sprengt.png` (1400 px, white, thin edges).

Tested on a made-up shade, 12 radial ribs + 2 slotted rings, half-lap slots, 246-point ribs with 3 holes
(`npx tsx $L/verkty/prove14.ts $L/ut/prove14/prove14.json`), exact polygons:

```
forge.js 158 kB · 14 delar · 5184 punkt
run 1.7 s · 14 objekt · volum 503704.4 mm3 · venta 503704.7 mm3 · avvik -0.25 · ingen overlapp
step 18.8 s + etterarbeid 1.5 s · 21633 kB -> 8326 kB · 14 MANIFOLD_SOLID_BREP · 14 namngjevne produkt · 14 fargar · 5212 flater (5212 plan, 0 sylinder)
bilete 12.7 s · prove14_iso.png prove14_front.png prove14_top.png prove14_sprengt.png      (whole run: 35 s)
```

Independent read-back with OCP (`STEPCAFControl_Reader`, XCAF names and colours, `BRepCheck`, exact volumes):

```
les 4.0 s · 14 delar · 14 solid · 5212 flater · 14 gyldige · 14 med farge
namn: R01 R02 R03 R04 R05 R06 R07 R08 R09 R10 R11 R12 G01 G02
volum 503704.654 mm3 · venta 503704.654 mm3 · avvik -0.000000
verste del: volum 0.000000 mm3 · boks 0.000000 mm · ukjende namn 0
overlapp 2.2 s · 28 par testa · 0 med volum · sum 0.000 mm3 · størst 0.000 mm3
```

So: one solid per part, every part valid, names and colours read back (`#c9a36b` in, `#c9a36b` out), total
volume equal to sum(area x thickness) to 1e-6 mm3, every part's bounding box where the matrix says to 1e-6 mm.
Second reader, ForgeCAD itself: `forgecad run $L/ut/prove14/prove14.step --details` -> `bodies=14 vol=503526.4`
(on the `--sirklar` build, matches its venta), 16 s.

With `--sirklar --toleranse=0.02` on the same input: `5184 punkt -> 3852`, `step 10.8 s`, `8024 kB -> 3081 kB`,
`1998 flater (1960 plan, 38 sylinder)`, OCP `avvik -0.000000` against the adjusted expectation, whole run 24 s.

### What the STEP is, and what the tool does to it

- `forgecad export step` (OCCT backend) writes AP214 with exact planar B-rep: one `MANIFOLD_SOLID_BREP` per
  returned object, a root product plus one product and one `NEXT_ASSEMBLY_USAGE_OCCURRENCE` per part. A prism with
  n outline points has n+2 faces; it is not a triangle mesh.
- It carries **no names and no colours**: every product is `'Open CASCADE STEP translator 7.6 1.N'`. `tilforge.ts`
  rewrites the products and NAUOs to the part names (N-th product = N-th returned object, verified by the per-part
  box check) and appends one `STYLED_ITEM` + `COLOUR_RGB` chain per solid.
- OCCT writes two pcurves per edge: 3.9 kB per outline point. The tool's slimming pass points every `EDGE_CURVE`
  at its 3D line and drops what became unreferenced: 1.5 kB per point (21.6 -> 8.3 MB), still valid in OCP.
  `--feit` keeps the raw file.
- `--backend truck` is fast (2.9 s) but writes no product structure: OCCT finds `roots 0`, zero solids. Do not use.

### Matrix

`shape.transform(m)` takes the column-major 4x4 directly; the 12 ribs stand at 30 degree steps and land exactly.
A mirrored matrix (det -1) is refused by ForgeCAD ("received a non-rigid matrix"); the engine's frames are
right-handed (`u = v x n` in `lib/plan.ts:85`), so this does not arise. If `rotate` is ever needed instead:
`axis = [m6-m9, m8-m2, m1-m4]`, `angle = acos((m0+m5+m10-1)/2)` in degrees,
`shape.rotate(axis, angle).translate(m12, m13, m14)` gave the identical bounding box to 4 decimals
(not valid at exactly 180 degrees, where the axis vanishes).

### Hundreds of points, arcs

One plate, n outline points (export, raw -> slim size, OCP read time):

| n | export | STEP | OCP read |
|---|---|---|---|
| 100 | 5.6 s | 376 -> 142 kB | 0.1 s |
| 300 | 6.4 s | 1155 -> 437 kB | 0.2 s |
| 1000 | 8.9 s | 3902 -> 1475 kB | 1.9 s |
| 3000 | 24.2 s | 12027 -> 4564 kB | 56.5 s |

Size is linear, reading is not: keep a part under roughly 500 points. `--toleranse=<mm>` (Douglas-Peucker on
outline and holes, expectation recomputed from the simplified polygon) is the lever; on real engine outlines at
file detail it only removed 3 % at 0.02 mm (2219 -> 2143), they are already lean.

Arc fitting: **there is no working option.** `--sirklar` turns a hole whose points sit on one circle, evenly spaced
(>= 12 points, 1e-3 mm), into `circle2d` and that does export as a true `CYLINDRICAL_SURFACE` (also through
`difference2d`). For outlines, `path().exactArcTo()` is documented as exact but is not here: the shipped example
`examples/exact-arc-housing.forge.js` exports 262 faces with 1 cylinder (the bore), a notched ring built with it
came out as 3098 planar facets, 12.7 MB, 66 s to read, and a path with two semicircular arcs (chord = 2r) threw
"Invalid array length".
`arcTo` tessellates by design. Outlines stay polylines.

### From the real engine

```bash
npx tsx $L/verkty/motorjson.ts <ut.json> [oppsett.json|-] [lav|mid|hog|fil] [nett.stl]
```

`makeBygg(p, DETAIL.fil)` + `montasjen(...)`: part name = `adr`, outline/holes = `Del.outline/holes`, matrix from
the rib frame in doubles, `steg` = the engine's step + 1, colour by step. `oppsett.json` is a partial parameter bag
over `DEFAULT_PARAMS`; without `plan` it uses `rutenett(4, 4)`. Default cube -> `8 delar · 2 steg · 320 punkt`,
tilforge `ingen overlapp`, STEP 441 kB, OCP `avvik 0.000000`, 0 overlapping pairs; the render is the egg-crate.

## Recipe B: the body in ForgeCAD, cut by the slicer

`$L/ut/kropp/kropp.forge.js`: profile points in JS (X = radius, Y = height), `polygon(punkt).revolve(360, omlaup)`.
Parameters `Hogd 300, Vegg 25, Hol 40, Nav 30, Steg 96, Omlaup 192`; outer radius
`60 + 90 sin(pi (0.12 + 0.88 z/H))^0.8`, wall measured radially, hub = the top 30 mm solid from the bore out.

```bash
cd $L/forge
./node_modules/.bin/forgecad run $L/ut/kropp/kropp.forge.js --details
./node_modules/.bin/forgecad export stl $L/ut/kropp/kropp.forge.js --quality high --output $L/ut/kropp/kropp.stl
cd /home/user/slicer.iverfinne.no && npx tsx $L/verkty/stlsjekk.ts $L/ut/kropp/kropp.stl
```

```
Kropp: vol=5597697.0mm³  tris=75,264  bbox=[-150.0,-150.0,0.0] → [150.0,150.0,300.0]   ✓ Verifications: 1 pass
kropp.stl · 3675 kB · 75264 trekantar · 37632 hjørne · kantar med 1 trekant 0, med >2 0 · motoren: opne kantar 0, volum 5597697 mm3 · boks -150.0..150.0 -150.0..150.0 0.0..300.0
```

Binary STL, 1.1 s, closed by my own edge count and by the engine's `parseMesh` + `reparer` + `openEdges`.
`--quality high` changed nothing on any model tried (same triangle count as default); resolution is the script's:
`-p Omlaup=360 -p Steg=200` gave 290 880 triangles, still closed. `revolve(360)` without a count works out to 180 segments (3 600 triangles from a 10-point profile).

Into the engine: `motorjson.ts ... fil $L/ut/kropp/kropp.stl` first printed `kropp -75.0..75.0 ... 0.0..150.0`:
**the engine rescales the mesh to `storleik` (default 150)**. With `{"storleik":300,"tjukn":4}`:
`kropp -150.0..150.0 -150.0..150.0 0.0..300.0 · 8 delar · 2 steg · 2219 punkt`, STEP 3455 kB, OCP `avvik -0.000000`.

Open finding on that run: all 12 crossings overlap by slivers, `sum 1.017 mm3 · størst 0.130 mm3`. Pair 1 x 6
is two wedges over the full 4.00 x 4.00 mm crossing square, one at each end of the crossing column (where the
slot mouths are, on the slanted inner surface of the shell): `0.0507 mm3` at z 203.769..203.822 and `0.0796 mm3` at z 55.301..55.382,
so 0.05 to 0.08 mm tall. The cube has none. Cause in the engine not investigated. Consequence:
`forgecad run --connectivity` counts any positive overlap, so the tool prints
`OVERLAPP: 8 delar heng saman i 2 grupper (volum per par: lesstep.py --overlapp)`; read the volumes before
calling it a clash. A real clash looks different: one ring moved 1.5 mm gave 12 findings, 67.5 mm3 each, 810 mm3 in all.

### Organic tools, each run once (`$L/ut/organisk/*.forge.js`, STL closed = engine `opne kantar 0`)

| tool | what ran | result |
|---|---|---|
| revolve | 10-point profile, `revolve(360)` | 3 600 tris, closed, 1.8 s |
| loft | `loft([circle2d(95), ngon(6,150), circle2d(60)], [0,150,300])` minus an inner loft and a bore | 30 240 tris, closed, 2.8 s |
| sweep | `sweep(circle2d(12), [[0,0,0],[0,0,100],[60,0,200],[60,60,300]])` | 1 212 tris, closed, 1.8 s |
| SDF blend | `sdf.sphere(130).smoothUnion(sdf.cylinder(160,55).translate(0,0,150), 50).shell(25)` minus box and bore, `.toShape({ edgeLength: 3 })` | 128 732 tris, 15.9 s, engine says closed, but 8 edges carry more than 2 triangles |
| twist | `ngon(8,140).extrude(300, { twist: 120, divisions: 80, scaleTop: 0.5 })` minus inner twist and bore | 3 232 tris, closed, 2.0 s |

`shape.shell()` is documented for boxes, cylinders and straight extrudes only; hollowing above is done by
subtracting an inner body. SDF results are meshes only (no exact STEP).

## Pictures, camera, explode, report

- `forgecad render 3d <file> --output x.png --camera iso --camera front --size 1400 --edges thin --background "#ffffff"`
  writes `x_iso.png`, `x_front.png`; 4 to 13 s per call (Chrome start), whatever the number of cameras. The picture is a clean
  shaded viewport image, part colours as given, soft light, no ground or grid; `--edges thin` draws every facet edge,
  so polyline curves show as fine hatching on the cut faces. `--render-style studio` gives a glossier product look.
- Camera: presets (`iso front top front-right`), `az:el` (`--camera 35:-30` -> `x_az35_el-30.png`), or exact
  `--camera "proj=perspective;pos=420,-380,-160;target=0,0,150;up=0,0,1;fov=35"`. Exact and preset cameras cannot be
  mixed in one call ("Cannot mix exact --camera/--camera-json with camera presets").
- `explodeView()` only configures the Studio slider; the CLI has no explode flag. Use a parameter: the generated
  model has `Sprengt` (`-p Sprengt=0.6`) and `Steg` (`-p Steg=2` shows steps 1..2).
  `forgecad render variants <file> --vary Steg=1,2,3,4 --output <dir> --camera iso` rendered 4/4 in 6.7 s into
  `<dir>/0002-Steg_2/iso.png` etc. Each case is framed on what is visible: use an exact camera for a steady sequence.
- `forgecad render section <file> --output s.png --plane XZ --offset 0` works (3.7 s) but draws +Z downwards.
- `forgecad export report <file> --output r.pdf`: 5 pages for the 14 plates, 5.7 MB, 1.9 s: an assembly overview and
  one four-view page per unique part ("4 identical instances merged"), no dimensions unless the script declares them.
- `forgecad export cutting-layout` is a guillotine packer for rectangular `sheetStock()` panels (saw cut sequence).
  On a model without `sheetStock()` it answers "No sheetStock() declarations found". Not a nester for outlines.
- `forgecad export glb` gave a 1.7 MB GLB of the 14 plates in 1.4 s (content not inspected); `export 3mf` ran.
- `forgecad inspect fit interference <file> --output <dir>` writes `manifest.json` with
  `evidence.collisions.collisions[]` (names, `overlapVolume`, threshold 0.1 mm3) and a highlight PNG, 6 s.

## Does not work here

- `capture gif`, `capture mp4`, `render hq`: Pro licence. `render hq` would also need Blender (absent).
- `export step --backend truck`: unreadable assembly (no products).
- `exactArcTo`: not exact in STEP, unstable. No arc fitting for outlines.
- Bent parts (`MontDel.boygd`) are not handled: `motorjson.ts` flags them (`boygd: true`) and `tilforge.ts` would
  extrude them flat in the wrong shape. Not tested with a bent plane.
- `studio`, `dev`, `web`, hosted-project and login commands: not tried.
- Error line numbers from `forgecad run` are the script line + 3.

## Files

`$L/verkty/tilforge.ts` (JSON -> forge.js -> STEP/diag/PNG), `lesstep.py` (OCP read-back), `motorjson.ts` (engine ->
JSON), `stlsjekk.ts` (STL closedness with the engine), `prove14.ts` (test assembly). Outputs: `$L/ut/prove14/`,
`$L/ut/motor/`, `$L/ut/skjerm/`, `$L/ut/kropp/`, `$L/ut/organisk/`.
