# spegl.md — mirror acrylic in the renderer

Everything here was run on 2026-11-18. Repo untouched. Read `kart/syn.md` first; this only adds to it.
`V = /tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/verkty`
`P = /tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/nord3/spegl-prov`

Changed: `V/syn-side.js` (material, reflection pass, ray pass), `V/syn.ts` (`speglSide` in the `Del` type, one `spegl:` line printed, `info.spegl`), `V/typar.ts` (one line: `speglSide` allowed in `Utstyr.delar`). `V/lag.ts` is untouched: it already spreads every key of `utstyr.delar[adr]` onto the part.
Backups of the files as they were: `V/syn.ts.for-spegl`, `V/syn-side.js.for-spegl`, and `P/kopi/{syn.ts,syn-side.js,typar.ts,lag.ts}`.

## Use

A part gets three keys. In a scene file:

```json
{ "adr": "4", "tjukn": 3, "omriss": [...], "matrise": [...], "material": "spegl", "farge": "#2f3d35", "speglSide": -1 }
```

In a `konsept.ts`, through `utstyr.delar` (keyed by the part's `adr`):

```ts
delar: { "4": { material: "spegl", farge: "#2f3d35", speglSide: -1 } }
```

- `material: "spegl"`: 3 mm mirror acrylic. `farge` is the matt colour of the face that is NOT mirrored (default `#8a8d8f`, the grey backing paint).
- `speglSide: 1`: the mirror is the face on the plate's +normal side. `-1`: the other face. `0` or missing: both faces mirrored.
- Cut edges are pale grey-green (`#c3d5cb`), roughness 0.2.

## The side convention (checked)

`+normal` is the normal of the plane as the plan gives it. In `delar.json` that is `delar[].normal`, and it is exactly the z axis of `matrise` (columns 8..10): checked on all 12 plates of `n5s` and `n5a`, dot product 1.000. The plate lies from w = 0 to w = `tjukn` with the plane in the middle, so `speglSide: 1` is the face at w = `tjukn`, `-1` the face at w = 0.

Mirror toward the inside of the sphere lattice (`d[i]` is plane i's signed offset along its normal from the sphere centre; the inside face is on the `-sign(d)` side):

```ts
const delar: NonNullable<Utstyr["delar"]> = {}
for (let i = 0; i < d.length; i++) for (const id of [1 + i, 21 + i])
  delar[String(id)] = { material: "spegl", farge: "#2f3d35", speglSide: d[i] < 0 ? 1 : -1 }
```

That is what `P/nord.ts` does with `spegl: true` (a copy of `nord/nord.ts`, one option added). Checked from `scene.json` in both poses: every mirror face's normal points at the sphere centre, 14 / 45 / 76 mm away:
`n5s spegl 12 … 1:1:77 2:1:45 3:1:14 4:-1:14 5:-1:45 6:-1:76 21:1:77 22:1:45 23:1:14 24:-1:14 25:-1:45 26:-1:76` (n5a the same).

## What the studio views do

- Each flat mirror plane gets a real planar reflection: the scene is drawn once more from the camera mirrored in that plane (clipped at the plane), and the mirror face shows that picture. Faces in the same plane share one pass (12 passes for the sphere lattice). Where the reflected ray meets nothing, the mirror shows the studio backdrop (lighter up, darker down). Reflectance 0.9.
- A mirror seen IN a mirror is not traced again: it is drawn as polished metal reflecting a painted grey studio (one softbox). So the second bounce is a stand-in, not the scene.
- The other face is matt `farge` (roughness 0.6), the edge pale grey-green and slightly glossy.

## What the lit view (`lys`) does — the proper version, with two honest gaps

Rays are traced: 240 000 from the bulbs (spread evenly over them, started inside the glass radius), each followed through up to 8 specular reflections off mirror faces, 0.87 of the light kept per reflection. What then lands on the floor, the back wall or the ceiling is added to the picture as light on that surface, on top of the direct light the renderer already draws. Flat plates are hit exactly (outline, holes, both faces); hardware (`utstyr`), bent parts and the cord are hit as triangles; `akryl-opal` and `pp` let rays through, as they do in the rest of `lys`.

Also changed: the renderer's random bounce lights (the ones that light inner faces) now follow a ray through up to 6 mirror reflections before they place their light, so matt surfaces lit by way of a mirror get some of it.

Gaps: (1) mirror-reflected light that lands on another plate, the stand or hardware is NOT added by the ray pass (only the bounce lights above reach it, and they are few and soft). (2) The mirror faces themselves show the planar reflection of the lit scene from ONE light sample and do not bloom; at sheet size the sphere still reads dark from outside, and the inward faces were not inspected up close in `lys`.

The tracer prints its counts (`syn.ts`, not `lag.ts`):

```
npx tsx $V/syn.ts $P/n5s-spegl/ut/scene.json --ut $P/bilete --namn n5s-spegl --syn lys
  spegl: 12 flater · 240000 strålar · ut av lampa direkte 19.1 % · via spegl 17.3 % (13.5 % landar på golv/vegg/tak) · fyrste treff spegl 64 % · 1864 ms
n5a: … ut av lampa direkte 16.7 % · via spegl 16.7 % (14 % landar på golv/vegg/tak) · fyrste treff spegl 64 % · 2035 ms
```

Read: of all rays from the bulb, 19.1 % leave the lamp touching nothing (the same for the matt lamp, same geometry), and another 17.3 % (already weighted 0.87 per bounce) leave after one or more mirror reflections. With matt plates those rays stop at the first plate. These are ray counts, not lux, and the matt plates' own diffuse bounce is not in them.

## The test

Four runs of `lag.ts --rask`, all hard rules green in both poses, sheets looked at:

```
n5s-matt  harde grip ok · delar ok · orden ok · klem ok · gods ok · plate ok · snittspor ok
n5a-matt  harde … all ok        n5s-spegl harde … all ok (20.7 s)        n5a-spegl harde … all ok (21.1 s)
```

- `P/bilete/n5s-par.png`, `P/bilete/n5a-par.png`: matt (top row) against mirror inside (bottom row): helt · lys · front · topp · under.
- `P/n5s-spegl/ut/ark.png`, `P/n5a-spegl/ut/ark.png`, `P/n5s-matt/ut/ark.png`, `P/n5a-matt/ut/ark.png`: the four contact sheets.
- `P/bilete/n5s-spegl-lys.png`, `n5a-spegl-lys.png`, `n5s-spegl-front.png`, `n5a-spegl-under.png` (900 px), `n5a-begge-helt.png` (`speglSide: 0` on every plate, through a scene file), `einskild.png` (those four side by side).
- Nothing else moved: `n5s-matt` and `n5a-matt` are pixel-identical to `nord/n5s/ut/ark.png` and `nord/n5a/ut/ark.png` above the footer (0 differing pixels). `V/syn-prov/pendel.json` still renders without an error.

What the pictures say: outside the sphere stays matt dark green with pale edges; the inward faces show in `front` and `topp` and reflect the bulb glass and the other plates. In `lys` the mirror version puts clearly more light on wall and floor: the sharp direct patches stay, and broad softer fields appear between them and above the lamp.

## Limits

- The engine knows nothing about this. `bag.material` is still what it cuts and weighs (the test says `mdf 3 mm · 0.257 kg`); acrylic is heavier and cuts differently. `spegl` is a renderer material only.
- Bent parts and GLB parts with `material: "spegl"`: both faces get the polished-metal stand-in, `speglSide` and `farge` are ignored, and in the ray pass they stop light like a matt part. Not rendered in any test.
- One true reflection per mirror, drawn once per view at no more than 900 px on the long side; a sheet tile is full size, a 1400 px single view is slightly soft in the mirror. Soft shadows inside a reflection come from one light sample.
- Ray pass: light map 256 × 256 over a square 8 × the lamp's size on each room plane (5.7 mm per texel for the 181 mm sphere), smoothed three times, so detail under about 10 mm is gone. A ray that enters a plate through its cut edge is absorbed. No diffuse light is traced, no colour from the matt faces.
- A mirror lining can show the bulb to the eye by reflection (F1). The studio views draw that first reflection (see `front`), but nothing measures it.
- Not tried: hanging lamps (the ceiling path), `opp: "y"`, more than one bulb, `--stor`, `sprengt` beyond the contact sheet. Time: the ray pass took 0.43 s for 60 000 rays alone and 1.9 to 2.0 s for 240 000 with three other renders running; a `--rask` run with mirrors took 20.7 and 21.1 s.
