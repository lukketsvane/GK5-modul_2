# syn.md — the renderer: plates in, studio pictures out

Everything here was run on 2026-11-17 (repo untouched, `git status` empty). Headless Chromium, three.js r185, software GL (SwiftShader).
`V = /tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/verkty`
`K = /tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/kart`
Files: `V/syn.ts` (CLI + `syn()`), `V/syn-side.js` (the page: scene, light, views), `V/syn-prov/` (test scenes and runs), `K/syn/*.png` (the sheets).
Run from the repo so `playwright` and `three` resolve: `cd /home/user/slicer.iverfinne.no && npx tsx <abs path>`.

## Recipe 1 — the contact sheet, straight from the engine's `delar.json` or GLB

```bash
npx tsx $V/syn.ts $K/ut/lampeb/delar.json --ut /abs/out --namn lampe-b            # default view: ark
npx tsx $V/syn.ts $K/ut/ror/samla.glb     --ut /abs/out --namn ror --material bjork
```

```
motor-json: 11 delar · 300 x 300 x 297 mm · 4468 trekantar · bygg 334 ms
  ark       12173 ms  …/kart/syn/motor-json-ark.png
motor-glb-boygd: 3 delar · 260 x 260 x 244 mm · 15192 trekantar · bygg 289 ms
  ark       18687 ms  …/kart/syn/motor-glb-boygd-ark.png
```

`delar.json` is read as it is: `delar[].adr/omriss/hol/matrise/tjukn/krumming/rille` and `orden` (the steps). A GLB gives one part per mesh node.
Flags: `--ut dir` (default: the scene's folder) · `--namn stem` · `--syn helt,front,side,topp,under,lys,sprengt,ark | alle` · `--storleik 1400x1400` · `--stor` (2×) · `--prover 40` · `--material bjork` · `--tjukn 3` · `--eining mm|m` and `--glbopp y|z` (GLB) · `--kropp surface.stl|glb`.
Files are `<ut>/<namn>-<syn>.png`. Exit 0 = ok (ran), 1 = crash (ran: `ukjent syn: skraa`), 2 = the page logged an error (written, never seen).
A ForgeCAD GLB is Z up and in mm: add `--glbopp z` (ran on `…/ut/prove14/prove14.glb`: `forge-glb: 14 delar · 280 x 280 x 300 mm`, upright; without the flag it lies on its side).

## Recipe 2 — a scene file with context and hardware

```json
{ "namn": "pendel", "opp": "z",
  "deler": [ { "namn": "A1", "tjukn": 4, "material": "bjork", "omriss": [[150,0],[149.9,5.75],…], "hol": [],
               "matrise": [1,0,0,0, 0,0,1,0, 0,-1,0,0, 0,2,0,1] } ],
  "steg": [ { "delar": ["R1"], "retning": null }, { "delar": ["A1"], "retning": [-1,0,0] } ],
  "heng": { "tak": 640, "feste": [0,0,222] },
  "utstyr": [ { "slag": "paere", "senter": [0,0,95], "diameter": 60, "lengd": 105, "retning": [0,0,1] },
              { "slag": "sokkel", "senter": [0,0,192], "diameter": 42, "lengd": 60 } ] }
```

`npx tsx $V/syn.ts $V/syn-prov/pendel.json --ut $K/syn --syn ark,helt,lys` →

```
pendel: 14 delar · 300 x 300 x 230 mm · 5840 trekantar · bygg 261 ms
  ark       10998 ms  …/kart/syn/pendel-ark.png
  helt       7824 ms  …/kart/syn/pendel-helt.png
  lys       20067 ms  …/kart/syn/pendel-lys.png
  ark-ruter: helt 1477 · lys 4018 · sprengt 1077 · front 1043 · side 1143 · topp 872 · under 1080 ms
```

Working scenes to copy from: `V/syn-prov/{pendel,rutenett,plate,vegglampe}.json`, built by `V/syn-prov/scener.ts`.

## Recipe 3 — from code, on engine data (`V/syn-prov/fraa-motor.ts`)

```ts
import { syn } from "<V>/syn"
const d = JSON.parse(readFileSync(`${K}/ut/lampeb/delar.json`, "utf8"))        // or delData(...) from K/skriv.ts
const r = await syn({ namn: "lampe-b hengande", delar: d.delar, orden: d.orden, material: "bjork",
    heng: { tak: d.boks.max[2] + 420, feste: [0, 0, d.boks.max[2] - 20] },
    utstyr: [{ slag: "paere", senter: [0, 0, 150], diameter: 60, lengd: 105, retning: [0, 0, 1] },
             { slag: "sokkel", senter: [0, 0, 245], diameter: 42, lengd: 62 }],
    kamera: { helt: { az: 25, el: -6 } } },
  { ut: `${K}/syn`, namn: "motor-heng", syn: ["ark"], stille: true })
```

`ark 11 delar [300,300,297] ark 9192 ms feil 0 ukjende []` → `K/syn/motor-heng-ark.png`
`syn(scene | path, { ut, namn, syn: [...] | "alle", storleik: [b, h], stor, prover, material, tjukn, eining, kropp, stille })` returns
`{ filer: { ark: "/abs.png", … }, ms: { bygg, helt, …, "ark.lys" }, ramme: { helt: [x0,x1,y0,y1] }, info: { delar, boks, mal, trekantar, lyskjelder, ukjende }, feil: [] }`.
`ramme` is where the fitted points landed in the picture, −1..1; beyond ±1 would be clipped and the CLI then prints `UTANFOR RAMMA` (never happened in any run). `info.ukjende` = step names that match no part (ran: `STEG NEMNER UKJENDE DELAR: finst-ikkje`).

## The scene format, exactly

Frame: mm, Z up (`"opp": "y"` turns a Y-up scene: checked, `helt` and `sprengt` come out pixel-identical). Front = the −y side (or `vegg.normal`, or `"fram": [x,y,z]`).

| key | meaning |
|---|---|
| `deler` (or `delar`) | the plates, see below |
| `glb` | path to a GLB instead of / beside `deler`; `eining` `"m"`/`"mm"` (default metres, but taken as mm if a coordinate is above 20); `glbOpp` `"y"` (default, glTF) / `"z"` |
| `material`, `tjukn` | defaults for parts that have none (`bjork`, 3) |
| `steg` (or `orden`) | `[{ "delar": ["A1"], "retning": [x,y,z] \| null, "steg"?: n }]`, in assembly order |
| `utstyr` | hardware stand-ins, see below |
| `heng` | `640` or `{ "tak": z, "feste": [x,y,z], "leidning": true \| false \| diameter, "farge": "#1c1c1d" }` — ceiling at z = tak, a rose, a cord from `feste` (default: top centre) |
| `vegg` | `true` or `{ "punkt": [x,y,z], "normal": [0,-1,0] }` — a wall behind the lamp (default: touching its back) |
| `golv` | z of the floor. Default: the lowest point for a standing lamp; none in studio views for `heng`/`vegg` (in `lys` they get one 1.1 × size below, or `golvAvstand` mm) |
| `kropp` | STL (mm, Z up) or GLB (m, Y up) of the design surface, drawn as a faint blue ghost in the studio views; `"kroppSyn": false` hides it |
| `lys` | extra light sources `{ "punkt": [x,y,z], "radius": 8, "farge": "#ffcf9a", "styrke": 1 }` or a list (LED boards). Each `paere` is already one. At most 3 are used; with none, the light sits in the middle of the box |
| `kamera` | per view: `{ "helt": { "az": 25, "el": -6, "linse": 37.8, "vid": 1 } }` (degrees; `vid` multiplies the distance) |
| tuning | `lysstyrke` 1 · `atterkast` 1 (bounce light, 0 = off) · `sprengAvstand` 1 · `golvAvstand`, `veggAvstand` (mm, room in `lys`) · `bakgrunn` `["#dedad4","#b7b2ab"]` |

A part: `{ "namn" | "adr", "tjukn", "omriss": [[u,v],…], "hol": [[[u,v],…],…], "matrise": [16], "material", "farge", "boygd", "rille" }`
- `omriss`/`hol`: any winding, a repeated closing point is dropped. Slots and tenons are whatever the polygon carries; nothing is added.
- `matrise`: column-major 4×4 (three.js `Matrix4.fromArray`), `[x,y,z] = M·[u,v,w,1]` with w from 0 to `tjukn` — exactly `delar.json`'s.
- `material`: `bjork` `poppel` `papp` `mdf` `akryl-opal` `pp`; `farge: "#rrggbb"` overrides the face (no grain). Faces are pale, every cut edge is charred brown; `akryl-opal`/`pp` are milky and let light through.
- `boygd: { "krumming": 1/R }` (or `krumming` on the part, as `delar.json` has it): the pattern is rolled about its v axis through u = 0, the mid-surface keeps its length: `a = k·u`, `u' = sin a / k − (w − t/2) sin a`, `w' = t/2 + (1 − cos a)/k + (w − t/2) cos a`. Same formula as `lib/plan.ts ut()`.
- `boygd: { "nett": [x,y,z, …] }`: a triangle soup already in the body frame (9 numbers per triangle, e.g. `MOTOR.montasje(bag).delar[i].boygd`); `matrise` is ignored. Faces and edges are told apart from the mesh.
- `rille`: `[[[u,v],[u,v]], …]` drawn as fine dark lines on both faces (the kerf-bend cuts).

`utstyr[]` (all take `farge`, `ru`, `metall`):
`{ "slag": "paere", "senter", "diameter": 60, "lengd": 105, "retning": [0,0,1] }` — `senter` is the centre of the glass ball, `retning` points from there to the screw base (so `[0,0,1]` hangs, `[0,0,-1]` stands) ·
`sokkel` / `sylinder`: `senter, diameter, lengd, retning` (axis; sokkel is black by default) · `leidning`: `punkt: [[x,y,z],…], diameter: 6` (smooth curve through the points) · `boks`: `senter, storleik: [x,y,z]` or `matrise` · `kule`: `senter, diameter`.

`steg[].retning` is the direction the part TRAVELS when it goes in (the same as `orden[].retning` in `delar.json`). `sprengt` moves it the other way by 0.55 × its own length along that line + 0.28 × the lamp's size; a later step with the same direction goes 55 % further; entries with the same `steg` number count as one step; `null` stays put. With no steps every part moves radially from the centre (never into the wall).

## The views

| name | camera | what it is for |
|---|---|---|
| `helt` | 35° to the right, 20° above (9° when hanging), 35 mm lens | the hero |
| `front` | on −y looking +y, level, long lens (24°) | silhouette; x right, z up |
| `side` | on +x looking −x | +y to the right |
| `topp` | straight down, +y up in the picture | plan |
| `under` | straight up from below (the floor and ceiling patch are hidden) | what you see looking into it |
| `lys` | 30° right, 13° above (5° hanging), 1.65 × back; dark room | the lamp lit |
| `sprengt` | 35° / 22° (14° hanging) | exploded, dashed lines back to each seat |
| `ark` | one 1800 × 1200 PNG: helt · lys · sprengt over front · side · topp · under, labels, box sizes, name, part count | what an agent reads |

Studio views: warm-grey seamless backdrop, soft key light from the camera's left, sky dome, floor that only shows the shadow (contact shadow included). `heng` adds a round ceiling patch, rose and cord; `vegg` a wall panel that takes the shadow. The camera fits the plates and hardware with a 10 % margin (7 % in `sprengt`); a cord only counts within 0.28 × size of the plates, so a long cord runs out of the frame.

`lys` is the honest one: a warm point light at every bulb, moved around inside the glass between samples, real cube-map shadows onto a floor, a back wall (0.75 × size behind the lamp, or `vegg`) and the ceiling (`heng`), plus two bounces of light that are shadowed too. A lamp that traps its light comes out dark: `K/syn/rutenett-lys.png` is an egg-crate that only shines up and down, and the picture says so. `K/syn/pendel-lys.png` and `plate-lys.png` show rib and hole patterns thrown on wall and table.

## Timings (seconds, 4 CPUs shared with another agent, ±20 % between runs; `V/syn-prov/kjor.ts`)

```
scene         helt   front    side    topp   under     lys sprengt     ark   (1400 x 1400, ark 1800 x 1200)
pendel         7.1     6.8     7.1     6.7     5.3    18.3     4.7     8.7
rutenett      23.9    18.4    13.6     9.6     6.6    31.8    13.5    17.4
plate         10.1     8.8     6.0     9.2     6.6    19.5    10.0    11.2
vegglampe     15.9    16.3     6.9     8.1     9.0    20.8    11.2    12.1
  ramme helt [-0.62,0.63,-0.8,0.8] … [-0.46,0.45,-0.8,0.8] · utanfor: ingen · feil: ingen   (all four scenes, all views)
```

Plus about 1.5 s to start Chromium and build the scene. `--stor` (pendel): `helt` 2800 × 2800 in 22.2 s, `ark` 3600 × 2400 in 23.6 s. A lamp that fills the frame and sits on a floor (rutenett) costs about twice a see-through one. Samples: 40 per view (`lys` 64), 24 per sheet tile (`lys` 38); `--prover n` sets the first and scales the rest.
PNG sizes: sheet 1.3–2.4 MB, single view 0.5–1.8 MB.

## What was tested

- `pendel` (12 ribs + 2 slotted rings, hanging, 300 mm), `rutenett` (5 × 5 egg-crate sphere with a bulb cavity, table), `plate` (one plate, 63 holes, bulb, socket, cord, base block), `vegglampe` (wall, bent opal acrylic, bent pp with slits, cardboard, birch). Sheets read by eye after every change: `K/syn/{pendel,rutenett,plate,vegglampe}-ark.png`.
- Engine output both ways (`V/syn-prov/boks.ts`): the bounding boxes agree, and so do the pictures.
  `lampeb json [-150,-149.9,0,150,150,297.1]` · `lampeb glb [-150,-150,0,150,150,297.2]`
  `ror json [-129.9,-129.9,28,129.9,129.9,272]` · `ror glb [-130,-130,28,130,130,272]`  (ror = bent plane from `krumming` + `matrise` vs the engine's own bent mesh)
- `kropp` from STL and from GLB over `lampeb` (`K/syn/motor-json-ark.png` has the ghost), a near ceiling (rose, patch, pattern on the ceiling), `opp: "y"`, a scene with no plates, an unknown view name, two calls side by side.
- Every other key once: `V/syn-prov/val.json` (`heng` as a number, `golv`, `fram`, `bakgrunn`, `farge`, `mdf`, `lys` as a list with no bulb, `boygd.nett`, `metall`, `sylinder`, `kule`, `lysstyrke`, `atterkast`, `sprengAvstand`, `veggAvstand`) and `V/syn-prov/glb-vegg.json` (`glb` in a scene, `vegg: true`, `golvAvstand`, `kroppSyn: false`, with `--material poppel --tjukn 4 --eining m`). Both rendered without an error and looked right.

## Limits

- Not a path tracer. Direct shadows from the bulb are real. Bounce light is two bounces with a clamped falloff: inner faces three or more bounces away stay darker than in life. The room is one wall, one floor and (hanging) one ceiling.
- `akryl-opal` and `pp` cast NO shadow in `lys` and do not dim or blur what passes: a pattern behind a diffuser is drawn as if the diffuser were clear. They glow by being lit from either side. In the studio views they are 90 % / 72 % opaque.
- `rille` are lines: no light comes through kerf-bend cuts. Engraving is not drawn.
- Exposure in `lys` is set from the room (bulb to wall distance), the same for every lamp of that size, so two lamps compare; it is not a lux value. `lysstyrke` scales it.
- `sprengt` with the engine's `orden`: ribs travel sideways in their own plane, so they cross the rings in the picture (`K/syn/motor-heng-ark.png`). For a cleaner picture give your own `steg`, or leave steps out and get the radial one (`K/syn/motor-glb-boygd-ark.png`). Without steps, nested parts with the same centre do not separate.
- GLB parts: flat plates are split into face/edge by normal, cylinders by a fitted axis (the engine's bent plane came out right). Any other curved mesh falls back to a guess from strip width (pass `--tjukn`); that path has not met a real file. A GLB with several plates in ONE node was not tried. One material for the whole GLB.
- Wood grain runs along each part's own u axis, not the sheet's. Colours are plausible, not measured. Every cut edge of wood, cardboard and MDF is dark; on `akryl-opal` and `pp` the edge is light.
- No collision or fit check of any kind: plates that pass through each other render happily. Thin bright hairlines can show where two plates meet (shadow bias, about 0.2 mm).
- A lone part named in `steg` but missing in `deler` is skipped silently except for `info.ukjende` / `STEG NEMNER UKJENDE DELAR`.
- One Chromium per call. Two calls ran side by side without trouble (a free port each), but they share the 4 CPUs.
