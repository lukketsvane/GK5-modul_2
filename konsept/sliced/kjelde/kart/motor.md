# motor.md — a custom mesh through the engine, headless

Everything below was run on 2026-11-17 against `/home/user/slicer.iverfinne.no` (read-only); the few lines marked "read" come from the code only.
`K = /tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/kart`

Run anything as: `cd /home/user/slicer.iverfinne.no && npx tsx <absolute path>.ts` (tsx start 2–3 s).
Files: `K/form.ts` (helpers), `K/minimal.ts` (end to end), `K/prov/*.ts` (the experiments quoted here).

## Recipe 1 — mesh in code → body → slice → numbers

```ts
import { skal, sjekkNett, registrer, planVed } from "<K>/form"
import { MOTOR } from "/home/user/slicer.iverfinne.no/lib/motor"
import { DEFAULT_PARAMS, type Params } from "/home/user/slicer.iverfinne.no/lib/params"
import { skrivPlan } from "/home/user/slicer.iverfinne.no/lib/plan"
import type { ParamBag } from "/home/user/slicer.iverfinne.no/lib/core"

const nett = skal(profil, { vegg: 25, seg: 128, nav: { hogd: 30, hol: 40 } }) // Float32Array, 9 per triangle, mm, Z up
if (!sjekkNett(nett).ok) throw new Error("ikkje ein lukka kropp")
const k = registrer("lampe-b", nett)            // = put(id, label, makeSoup(pos), stlBytes) in lib/sources
const p: Params = { ...DEFAULT_PARAMS, kjelde: k.kjelde, scene: "", storleik: k.storleik, tjukn: 4,
  plan: skrivPlan([planVed(k, 1, [0, 0, 40], [0, 0, 1]), planVed(k, 4, [0, 0, 150], [1, 0, 0])]) }
const bag = p as unknown as ParamBag
const m = MOTOR.measure(bag)                    // Metrics
const reglar = MOTOR.rules(bag, m)              // Rule[]: id, label, hard, ok, value, why, fiks?
const liste = MOTOR.liste(bag)                  // Kutt[]: adr, id, plan, ark, w, h, area, cutLen, joints
```

`K/minimal.ts` is exactly this (dome 300 × 300 × 297 mm, wall 25, hub 30 with a ø40 through-hole,
3 horizontal + 4 vertical planes through the axis, 4 mm birch). Its real output:

```
nett   22272 trekantar · lukka true · samstemt true · utover true · 1 skal · 5227 cm3 · -150.0,-150.0,0.0 .. 150.0,150.0,297.3
plan   1@0.5,0.5,0.1345/0,0,1;2@0.5,0.5,0.5382/0,0,1;3@0.5,0.5,0.9418/0,0,1;4@0.5,0.5,0.5045/1,0,0;5@0.5,0.5,0.5045/0.7071,0.7071,0;6@0.5,0.5,0.5045/0,1,0;7@0.5,0.5,0.5045/-0.7071,0.7071,0
kropp  22272 av 22272 trekantar · 0 opne kantar · ytre 300.0 x 299.9 x 297.1 mm
tal    7 plan · 11 delar (9 unike) · 24 ledd (0 avviste) · 0 lause
kutt   10.47 m · 8.7 min ved 20 mm/s · 2 ark 600x400 · utnytting 25 % · 0.295 kg · spor 4.10 mm · minste gods 12.5 mm
tid    measure 470 ms · rules+liste 2 ms
delar  adr   form  plan  ark   b x h mm        areal mm2  kutt mm  ledd  hol (ø likt areal, med spor som munnar i holet)
       1     D01   1     1     297.1 x 297.1       21013     1900  8     ø247.4
       2     D02   2     1     253.6 x 253.7       18335     1630  8     ø201.6
       3     D03   3     1     107.5 x 107.5        7259      724  8     ø44.1
       4a    D04   4     2     129.9 x 297.1        7921      775  3     -
       ... 4b 5a 5b 6a 6b 7a 7b alike, 130.0 x 297.1 (7a = D06 = 5a, 7b = D07 = 5b)
reglar
  HARD ok   grip       plana grip               24 ledd
  HARD ok   delar      delar å skjere           11 stk
  HARD ok   orden      kan monterast            éin veg inn for kvar
  HARD ok   klem       ingen står i kvarandre   ingen klemmer
  HARD ok   gods       gods i leddet            12,5 mm
  HARD ok   plate      delane får plass         2 ark
  HARD ok   snittspor  snittet mot sporet       0,20 mm mot 4,10 mm
  mjuk ok   lause · klaring 0,10 · snitt 0,20 i fila · opning 116,0 mm · lukka · nett 22272 av 22272 · bog · bogledd · bogkurve
  mjuk BROT utnytting  utnytting                25 %
ingen harde brot
filer  <K>/ut/lampe-b.stl · lampe-b.glb · slicer-lampe-b-prosjekt.zip
```

## Recipe 2 — STL / GLB bytes from disk

```ts
import { readFileSync } from "node:fs"
import { parseMesh } from "/home/user/slicer.iverfinne.no/lib/io"
import { put } from "/home/user/slicer.iverfinne.no/lib/sources"
const b = readFileSync(sti)
const soup = parseMesh("x.stl", b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength) as ArrayBuffer)
put("lampe", "lampe.stl", soup, new Uint8Array(b))   // id /^[a-z0-9_-]{1,40}$/i; 4th arg lets the project zip carry the file
// then { ...DEFAULT_PARAMS, kjelde: "lampe", scene: "", storleik: <longest side in mm> }
```

The three files `minimal.ts` wrote, read back from disk and sliced with the bag from the zip's `oppsett.json` (`K/prov/disk-prov.ts`):

```
fraa-stl  22272 tri · boks -150,-150,0 .. 150,150,297.309 · storleik 300 · 11 delar · 24 ledd · 10.47 m · harde brot 0   (fraa-zip: identical)
fraa-glb  22272 tri · boks -0.15,-0.15,0 .. 0.15,0.15,0.297 · storleik 300 · 11 delar · 24 ledd · 10.47 m · harde brot 0
```

GLB is metres and Y up; the parser turns it to Z up, and `storleik` sets the size anyway. Formats: `.glb .gltf .stl .obj .ply`, no Draco/meshopt.

In the app (read in `lib/worker.ts`, `components/studio.tsx`, not run in a browser): worker `import` → `parseMesh(name, buf)` →
`put(kjeldeId(bytes), label, soup, bytes)`, id = `"f" + hash of the bytes`; the main thread sets `kjelde` to that id.
`MOTOR` never sees bytes: `makeKropp(p)` reads `p.scene || "<kjelde>@0,0,0/1/0"` and looks each id up in the registry.
**An unknown id silently becomes the 150 mm cube** (ran: `ukjend kjelde: 12 trekantar`). Re-registering an id replaces its geometry.

## Frame and size (all run, `K/prov/ramme-prov.ts`)

- Engine frame: **Z up**, body centred on x = 0, y = 0, standing on z = 0. Box = `makeKropp(p).solid.min/max`.
  App view (read in `components/gizmo.tsx`, not run): Z up, +X right, "front" looks at the **−Y** face.
- STL/OBJ/PLY/code soups: used as given, **Z is up**. GLB/glTF: file Y → engine Z (x, y, z) → (x, −z, y).
- Order: `p' = Rz(rotZ)·Ry(rotY)·Rx(rotX)·p`, right-handed, fixed axes; then scaled by
  `storleik / longest side of the rotated box`; then centred in x, y and dropped to z = 0.
  Source box x 10..110, y 20..80, z 5..35 with a tower at the +x +y +z corner:
  ```
  {}            boks -50,-30,0 .. 50,30,50   tower top at  46.7, 23.3, 50.0
  {"rotX":90}   boks -50,-25,0 .. 50,25,60   tower top at  46.7,-25.0, 53.3   (source +Y is now up)
  {"rotY":90}   boks -25,-30,0 .. 25,30,100  tower top at  25.0, 23.3,  3.3   (source +Z is now +X)
  {"rotZ":90}   boks -30,-50,0 .. 30,50,50   tower top at -23.3, 46.7, 50.0   (source +X is now +Y)
  ```
- `storleik` is the longest side in mm and scales **everything** (storleik 600 on the 300 mm lamp gave a ø79.7 hole).
  For 1:1 set `storleik` = the mesh's longest side (`registrer(...).storleik`). Headless there is no clamp
  (700 ran fine); the app clamps to 40–600 on load (`MOTOR.clamp`: 700 → 600, 20 → 40; no step snapping).
- A plane is `{ id, o, n, bog: 0, strek: [] }`. `o` is a **fraction of the placed body's box** per axis, `n` the normal;
  both kept to 4 decimals (0.03 mm on 300 mm). With rot = 0: `x = (o.x − 0.5)·W`, `y = (o.y − 0.5)·D`, `z = o.z·H`.
  `planVed(k, id, [x, y, z] in the mesh's own mm, n)` does it (rot = 0 only); `lib/plan.ts` `broek(p, min, max)` is the same thing.
  `o` may lie outside the box (−4..5). Max 64 planes. The address of a part is the plane id (+ a, b… per piece).
- The plate is centred on the plane: plane z = 100, tjukn 4 → mesh z 98.01 .. 102.01. The profile is the section AT the plane.
- 2D frame of a plane: n = (0,0,1) → u = +X, v = +Y, origin on the axis; n = (1,0,0) → u = +Y, v = +Z (2D y = height).

## What the sections look like (shell: half-ellipse dome R 150, H 300, wall 25, `K/prov/snitt-prov.ts`)

| body | plane | result (220 cells) |
|---|---|---|
| a open shell | z = 100 | 1 outer r 141.32..141.39 (true 141.42) + 1 hole r 115.94..116.01, 20 503 mm² |
| a | z = 285 (above the inner dome) | 1 solid disc r 46.8, no hole |
| a | vertical through the axis | **1** arch piece, 17 075 mm² |
| a / b | vertical at x = 60 / x = 130 | 1 arch / 1 solid D-shaped piece of the wall |
| a / b | tilted 30° through the middle | 1 outer + 1 hole |
| b hub + ø40 hole | z = 282 (through the hub) | 1 outer r 51.13..51.16 + **1 round hole r 19.98..20.00**, 29 vertices |
| b | vertical through the axis | **2** pieces (the hole splits the arch): parts `4a`, `4b` |

- Roundness: every hole vertex lies on the true circle; the cut polygon is **inscribed** (29-gon, flats at r 19.88,
  area as ø39.82). Cut files and all numbers are built at 220 cells: polyline tolerance = `min(0.25, storleik/220/8)`
  = 0.17 mm at 300 mm. At 1200 cells (STL/GLB) the same hole has 62–64 vertices, r 19.99..20.00.
  Model the hole 0.3–0.5 mm over nominal if the fit matters. More mesh segments (256) changed nothing at 220 cells.
- **Slots can open into the hole.** A plane that gives two pieces (`4a`, `4b`) moves as ONE part in ONE direction, so on
  every ring it crosses one slot opens at the inner edge and the other at the outer edge. On the hub plate above:
  4 slots open into the ø40 hole (mouth r 20.0 → bottom r 36.9) and 4 at the rim (r 53.8 → 36.9); between the
  notches the hole is still r 19.98..20.00. Reordering the plan list flips which four, never all eight (`K/prov/spor-prov.ts`).
- **A closed internal cavity is filled** (`K/prov/hol-prov.ts`): repair orients every connected shell outward, rays
  sum them. Egg 6258 cm³ with a 2933 cm³ inner shell, either winding: engine volume 9191 cm³, sections solid,
  0 open edges, no warning. Same for "subtracting" with an inverted cylinder through a box: no hole.
  A cavity exists only if its surface is connected to the outside: the open shell works, and an 8 mm channel
  from cavity to outside gave `1 ytre, 1 hol, 13 645 mm²` (true 13 744).
- **Overlapping closed shells are a union** (box + overlapping cylinder, one source: correct sections). So: add by
  overlapping, never subtract; model every hole and cavity in one connected surface (`skal`, `loft`, `dreiRing` do).
- Pieces under 400 mm² net are dropped (z = 299.5 disc of 235 mm²: gone). Planes with no crossing: hard `grip` + `gods`.
- Wall ≥ about 2 × tjukn + margin: the half-lap leaves `ledd` × wall on the ring (25 mm wall → 12.5 mm "gods"; rule wants ≥ max(2, tjukn)).

Mesh parameters, on the hub plate (`K/prov/param-prov.ts`, hole should be r 20.00):

```
standard                kropp 22272 tri  boks z 297.31 | hol n=29 r 19.98..20.00 ø-ekv 39.82
hol 39                  hole kept          hol 40 / hol 41: hole GONE (filled)
forenkl 0.5             hol n=16 ø-ekv 39.42          forenkl 2: n=9 ø-ekv 37.49
glatt 2                 boks z 294.86 | hol r 20.27    glatt 8: z 293.49, r 20.93    glatt 24: z 292.00, r 21.43
66816-tri mesh, trekant 40 or 60:  kropp 20464 tri | hol r 19.73..20.34
22272-tri mesh, trekant 10:        kropp  9648 tri, z 292.86 | hol r 19.32..26.29     trekant 2: 48 open edges
```

- `hol` (mm, default 0): a hole whose area is below a circle of that diameter is filled. **Leave at 0**; ≥ 40 kills an E27 hole.
- `forenkl` (mm, default 0): extra polyline tolerance; vertices stay on the curve, flats cut deeper. Leave at 0.
- `trekant` (thousands, default 40, max 60): a mesh at or under the budget is **untouched** (exact). Over it, vertex
  clustering replaces vertices by cell means (landed at ~20k, ±0.3 mm on the hole). Keep meshes ≤ 40 000 triangles.
- `glatt` (Taubin passes, default 0): any value moves a CAD mesh (hole +0.3 mm at 2 passes, body 2.4 mm shorter). Leave at 0.
- Repair also welds vertices closer than 1e-4 × box diagonal (0.05 mm at 300 mm) and drops zero-area and duplicate faces.

## The numbers: which call, which detail, what it costs

| want | call | detail |
|---|---|---|
| parts, unique, joints, rejected, loose, sheets, util, cutLen mm, cutTime s, mass kg, envelope, narrow, minGap, slotW, tris, openEdges | `MOTOR.measure(bag)` | mid (220) |
| every rule: `id, label, hard, ok, value, why, fiks` | `MOTOR.rules(bag, m)` | mid |
| per part: `adr` (engraved), `id` (shape, equal ids are identical), `plan`, `ark`, `w × h`, `area`, `cutLen`, `joints` | `MOTOR.liste(bag)` | mid |
| rings, holes, slots per part / per plane | `makeBygg(p, DETAIL.mid)` from `lib/bygg` → `.dl.delar[]` (`outline, holes, spor`), `.s.ribber[]` (`outlines, holes, raa, spor, area`), `.ns.sheets`, `.k.solid` | any |
| sheet i: placements + SVG | `MOTOR.arkSyn(bag, i)` | mid |
| assembly order text | `montering(p, makeBygg(p, DETAIL.mid).s)` from `lib/motor` | mid |
| files | `MOTOR.exportFile(bag, kind)`: `dxf svg ark alt flat prosjekt` at mid; `stl glb 3mf usdz` at fil (1200) | |

`cutTime = cutLen / fart`; `mass = area × tjukn × rho` (graa 700, bjork 670, finer 680, mdf 750, akryl 1190, papp 220 kg/m³).
Cost, 300 mm lamp, 14 planes (6 horizontal + 8 vertical), 22 parts, 96 joints, 22 272 triangles (`K/prov/tid-prov.ts`):

```
makeKropp 66 ms · buildSnitt lav 321 (first call, turns the body per plane direction) · mid 163 · hog 263 · fil 2576 ms
nest (makeBygg mid) 117 ms · measure/rules/liste once built 5/2/0 ms · montasje 47 ms
exportFile dxf 11 · ark 4 · svg 5 · alt 36 · stl 102 · glb 45 · flat 20 · 3mf 45 · prosjekt 4 ms (after the builds above)
cold MOTOR.measure after changing storleik: 319 ms
```

Results are cached per parameter bag (2 builds kept), so measure → rules → liste → exportFile is one build.

## Parameter bag (`lib/params.ts`; ranges are what `MOTOR.clamp` enforces, the engine itself takes anything)

| key | default | range | what |
|---|---|---|---|
| `kjelde` | `"kube"` | id | source id in the registry; also names the export files via its label |
| `scene` | `""` | string | `id@tx,ty,tz/s/rz` pieces, max 16; `""` = the one `kjelde` |
| `storleik` | 150 | 40–600 mm | longest side after scaling (README says 1200; the code says 600) |
| `rotX rotY rotZ` | 0 | ±180° | see frame |
| `glatt` · `forenkl` · `hol` | 0 · 0 · 0 | 0–24 · 0–10 mm · 0–80 mm | smoothing, profile tolerance, smallest hole — keep all three at 0 |
| `trekant` | 40 | 0.5–60 k | triangle budget — keep the mesh under it |
| `tjukn` | 3 | 1–25 mm | measured plate thickness |
| `klaring` | 0.1 | 0–0.6 mm | slot width = tjukn + klaring (soft rule wants 0.05–0.35) |
| `ledd` | 0.5 | 0.2–0.8 | where the half-lap splits (0.3 → ring keeps 7.9 of 26 mm, ran) |
| `deling` | `""` | string | one joint: `"1-2-0:0.25"` = planes 1–2, crossing 0 (ran) |
| `lause` | 1 | 0/1 | 1 drops pieces without a joint, 0 keeps them (then a hard rule if any) |
| `kilar` · `merk` | 0 · 0 | 0/1 | wedges on through tenons (drawn planes only) · address cut into the face in the 3D files |
| `snitt` | 0.2 | 0–6 mm | kerf; hard rule: must be < slot width |
| `snittveg` · `fart` | 0 · 20 | 0/1 · 1–200 mm/s | kerf taken in the file (0) or by the machine (1) · time estimate only |
| `arkB arkH` | 600 × 400 | 100–3000 × 100–2000 mm | sheet |
| `material` | `"graa"` | graa bjork finer mdf akryl papp | density + colour |
| `plan` | `""` | string | the planes, `skrivPlan(Plan[])` |
| `fest` · `snapp` | `""` · 3 | | pinned sheet positions · UI snapping only |

## `form.ts` (tested in `K/prov/form-prov.ts` and `kant-prov.ts`: every mesh 0 open edges, 1 shell, outward, volumes as computed by hand)

- `dreiRing(ring: [r, z][], seg = 96)` — revolve any closed section about Z. r = 0 points sit on the axis. Throws if the section crosses itself.
- `skal(ytre: [r, z][], { vegg, seg?, nav?: { hogd, hol? } })` — thick shell from an outer profile listed bottom rim first,
  wall measured normal to the profile, bottom open, rims horizontal where the profile end is steeper than 45°.
  Ends at r = 0 → closed top; ends at r > 0 → open top. `nav` makes the top `hogd` mm solid (never thinner than the wall),
  `hol` drills a ø through it. `skalRing(...)` returns the 2D section — print it before trusting a new profile.
- `loft(snitt: { z, ring: [x, y][] }[], { vegg, lok?, hol?, senter? })` — skin through closed sections (same point count,
  same start direction, rising z), wall measured **horizontally**, bottom open; `lok` = solid lid thickness at the top,
  `hol` = round through-hole in the lid (as many vertices as the rings — use ≥ 64 points). A lid without a hole is a fan
  from the centroid: sections must be star-shaped. Throws when the wall does not fit inside a section.
- `sjekkNett(pos)` → `{ tris, opne, mangfaldige, vrengde, utarta, skal: volumes per shell, volum, min, max, lukka, samstemt, utover, ok }`.
  `ok` demands ONE shell; for a deliberate union of overlapping shells check `lukka && samstemt` and that every `skal` volume is > 0.
- `saman(...nett)`, `flytt(nett, [x, y, z], vriZ°)`, `snu`, `utover`, `volum`, `innRing(ring, d)`, `ringKryssar(ring)`.
- `stlBytes / skrivStl(sti, pos)` (binary, mm, Z up) and `glbBytes / skrivGlb(sti, pos)` (the app's own `meshToGlb`: metres, Y up).
- `registrer(id, pos, etikett?)` → `{ kjelde, scene: "", storleik, min, max, side }`; `planVed(k, id, punktMm, n, meir?)` → `Plan`.

## Limits and traps

- No subtraction and no closed cavities (above), and no warning: at 1:1 compare `makeKropp(p).solid.volume()` with `sjekkNett(nett).volum`.
- `skal` offsets the profile by mitred normals: a wall thicker than a bulge radius of the profile self-intersects (ran: r 15 bulge, wall 25 → throws).
- Multi-piece `scene` works headless and is 1:1 when each piece's `s` = its longest side / 100, `t` in mm and `storleik` = the
  union's longest side (ran: foot ø120 × 20 + shade lifted 100 → box z 397.27, sections correct). But `s` is 0.05–5, `t` ≤ ±400, and on
  opening a project zip the app re-registers meshes under hash ids, so scene ids written here would fall back to the cube
  (read from code, not run). **Merge everything into one mesh with `saman` + `flytt` and keep `scene: ""`.**
- The app also clamps the bag on load: a body over 600 mm would be rescaled. Not tested in a browser.
- All section vertices are polylines; nothing here writes arcs. Tolerance 0.17 mm at 300 mm, 0.25 mm from 440 mm up.
- `utnytting` (soft) failed at 25 % on 600 × 400: rings waste the sheet. It is advice, not a break.
