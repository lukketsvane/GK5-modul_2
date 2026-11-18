# plan.md — the plan language as a cookbook (everything was run unless marked "read")

Run 2026-11-17 against `/home/user/slicer.iverfinne.no` (read-only, `git status` empty). `P = /tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/kart/plan`
Run: `cd /home/user/slicer.iverfinne.no && npx tsx P/kokebok.ts` (5 s, every recipe R1–R14, ends `alle oppskriftene held`).
Builders: `P/oppskrift.ts` (import this one). Experiments: `P/radial.ts virvel.ts halv.ts orden.ts rutenett.ts ledd.ts skive.ts skive2.ts tapp.ts kasse.ts meir.ts boyg1-4.ts saum.ts fritak.ts reflektor.ts boymat.ts smaa.ts gods*.ts`.

Bodies (all 4 mm `bjork`, `storleik` 300 = 1:1, sheet 600 × 400 unless said): `opeSkal()` open shell of revolution, outer r = 150 − 70·(z/300)², wall 25, open both ends · `kuppel()` closed half-ellipsoid dome R 150 H 300, wall 25 · `massiv()` the same dome solid · `ror()` tube r 110..130, H 300 · `boks(b, d, h)`.
Result line = planes, parts, joints (of which tenons/fingers/through-mortises, rejected), loose, sheets, hard rules.
Hard rule ids: `grip delar orden klem gods plate snittspor`, plus `bog` and `bogledd` for bent planes and `lause` when `lause: 0`.

```ts
import { bag, kjor, opeSkal, kuppel, massiv, ror, boks, plan, mm, ringar, radial, tangent, halvribber, virvelhalv, utanfraa,
  sirkel, rundt, rektStrek, skjerm, renne, fot, skrivPlan } from "<P>/oppskrift"
const k = opeSkal()                                   // Registrert: kjelde, storleik, min, max, side
const l = utanfraa(ringar(k, 1, [60, 220]), halvribber(k, 10, 8, 5))   // Plan[]
const u = kjor("namn", bag(k, l, { tjukn: 4 }))       // prints the line; u.b = makeBygg result, u.harde = broken hard rule ids
// plan(k, id, [x, y, z] mm, n, extra)  ·  mm(k, [[u, v] mm …]) -> outline fractions  ·  skrivPlan(l) -> the string
```

## Recipes

**R1 Radial, full planes, ribs do not reach the axis** — `[...ringar(k,1,[60,220]), ...radial(k,10,N)]`, N planes through the axis, each plane = 2 rib pieces `10a 10b`.
`1@0.5,0.5,0.2/0,0,1;2@0.5,0.5,0.7333/0,0,1;10@0.5,0.5,0.5/1,0,0;11@0.5,0.5,0.5/0.9239,0.3827,0;…`

| body | N = 6 | 8 | 12 | 16 | 24 | hard rules |
|---|---|---|---|---|---|---|
| ope, 2 rings (parts/joints) | 14/24 | 18/32 | 26/48 | 34/64 | 50/96 | all ok |
| ope, 3 rings | 15/36 | 19/48 | 27/72 | 35/96 | 51/144 | all ok |
| kuppel + hub with ø40 axial hole, 2 rings, N 8 | | 18/32 | | | | all ok (3 rings, one through the hub: 19/48 ok) |
| kuppel (arches meet on the axis), 2 rings | 12/39 | 16/60 | 24/114 | 32/184 | 48/372 | **orden**: N−1 stuck (`11 mellom 1 og 10`) |
| massiv, 2 rings | 2/27, 30 loose | 2/44, 42 | 2/90, 66 | 2/152, 90 | 2/324, 115 | **orden**: N−1 stuck |

3 rings on kuppel/massiv: same break. List order does not matter here (ribs first, rings first, interleaved: all gave the same verdict; the engine found order `1,2,10,…`). Limit: one plane is one part, so on each ring half the slots open at the inner edge and half at the rim (`ring 1: 8 spor, 4 opnar i ytterkanten, 4 i innerkanten`).

**R2 Radial half-ribs (the lamp recipe)** — one plane per rib, outline = a rectangle on one side of the axis, `n:1` binds it to the body. Works on hollow, closed and solid bodies, and `utanfraa` makes every ring slot open at the rim.
`halvribber(k, 10, N, r0)` = plane through the axis, `n = (sin t, −cos t, 0)` so 2D u is the radial direction; outline u r0..200, v ±200 mm.
`12@0.5,0.5,0.5/0.866,0.5,0/n:1/p:0.04,-0.6667,0.6667,-0.6667,0.6667,0.6667,0.04,0.6667;13@…;14@…;1@0.5,0.5,0.2/0,0,1;2@0.5,0.5,0.7333/0,0,1;10@0.5,0.5,0.5/0,-1,0/n:1/p:…;11@…;15@…`
```
kuppel 2 ringar + 6 halvribber r0=12, utanfraa  8 plan   8 delar  12 ledd (0 tapp, 0 avvist) 0 lause · 2 ark · alle harde ok
    ringar fyrst: ring 1: 6 spor, 3 opnar i ytterkanten, 3 i innerkanten  ||  utanfraa: ring 1: 6 spor, 6 opnar i ytterkanten, 0 i innerkanten
massiv 3 ringar + 24 halvribber r0=30, utanfraa 27 plan  27 delar  72 ledd (0 tapp, 0 avvist) 0 lause · 6 ark · alle harde ok
```
Ran N = 6, 8, 12, 16, 24 × 2 and 3 rings × ope (r0 5), kuppel (r0 12), massiv (r0 30): always N + R parts, N·R joints, all hard ok.
`utanfraa(rings, ribs)` = `[ribs whose radial direction has x < 0 (or x = 0, y < 0), ...rings, the other ribs]`. With rings first the rule still passes, but half the slots open inward, and on massiv that order dropped pieces (`6 lause` at N 8 with 2 rings, 33 at N 24 with 3).

**R3 Pinwheel half-ribs + rings** — `virvelhalv(k, 10, N, off)`: the same half-plane pushed `off` mm sideways (`o = off·n`). Forward half-lines of a pinwheel never cross each other.
`ope 12 virvel-halvribber, forskyving 40 + 2 ringar 14 plan  14 delar  24 ledd … alle harde ok` (also 8, 16, 24 at off 40 and 12 at off 70 on ope, kuppel, massiv, except kuppel 24).
Fails when neighbours come closer than a few thicknesses where both have material: `kuppel 24 … forskyving 40: 2 delar 120 ledd (72 tapp) HARDE BROT: orden[12 står fast]` — start the outline further out (massiv ran with u0 = 25).

**R4 Vortex alone (no rings)** — `tangent(k, 10, N, r)`: N full vertical planes r mm from the axis. All slot lines vertical.
`massiv: virvel åleine, 12 plan 40 mm frå aksen 12 plan 12 delar 48 ledd … alle harde ok` (massiv r 40: N 6/8/12/16 = 12/24/48/96 joints ok; r 80: 6/16/36 ok, N 16: `klem[16 par]`). Any ring added: `orden` breaks (ran on all three bodies, N 6–16).

**R5 Egg-crate** — `skrivPlan(rutenett(5, 5))` = `1@0.1,0.5,0.5/1,0,0/g:1;…;6@0.5,0.1,0.5/0,1,0/g:2;…`
`kuppel rutenett 5x5 10 plan 10 delar 21 ledd … alle harde ok` (soft: utnytting 23 %, 4 sheets); 4×4 8/12, 3×3 6/9 ok; massiv 5×5 10/21 ok.
On the open shell: `ope rutenett 5x5 … 18 ledd (2 avvist) HARDE BROT: klem[2–8, 4–8]`, 4×4 `klem` 4 pairs, 3×3 ok (8 parts 8 joints). A crossing line that grazes the wall has no shoulder beside the slot.

**R6 Families that share one slot direction** — any set of planes whose normals are all perpendicular to one direction assembles.
`kuppel: 3 ringar + 5 lameller n=Y 8 plan 8 delar 28 ledd … alle harde ok` (`1@0.5,0.5,0.1667/0,0,1;…;10@0.5,0.2,0.5/0,1,0;…`; ope: 11 parts 28 joints ok).
Fan about X (4 planes tilted ±20°, ±40° with n = (0, sin g, cos g) + 3 planes n = Y): kuppel 10 parts 36 joints ok, ope 11/36 ok.
Two oblique families n = (1,0,0.5) and (0,1,0.5), 3 + 3: `klem[30–42]` (one grazing crossing); + 1 ring: `orden[1 mellom 30 og 40]`.

**R7 Lampholder plate with an exact round hole** — two ways, both gave the hole as an inscribed 29-gon, vertices r 19.99, flats 19.84, ø-equivalent 39.82 (same as a mesh hole):
- mesh ring + strokes, later stroke wins: `2@0.5,0.5,0.7333/0,0,1/+o:0,0,0.6333,0.6333,0/-o:0,0,0.1333,0.1333,0` (fill ø190, then cut ø40; reversed order: no hole)
- drawn disc: `3@0.5,0.5,0.7333/0,0,1/p:<24 points on r 100>/r:0,1,…,23/-o:0,0,0.1333,0.1333,0`
`ope: ring + teikna skive ø200 m/ hol ø40 + 8 halvribber 10 plan 10 delar 16 ledd … alle harde ok` (the disc must stand next to the ring in the list; listed after the ribs: `orden[3 mellom 10 og 11]`).
Drawn circle roundness at r 100: 4 arc points (`formPunkt("sirkel")`) r 88.3..99.9 — not a circle; 8: 99.1..99.9; 16: 99.5..100.0; 24 or 48: 99.88..99.98, flats 99.62.

**R8 Feet with tenons into a mesh ring** — a drawn vertical plate whose top edge stops at the ring. `fot(k, 30, 22.5, [[105,-80],[165,-80],[145,60],[105,60]])` = `30@0.5,0.5,0/0.3827,-0.9239,0/p:0.35,-0.2667,0.55,-0.2667,0.4833,0.2,0.35,0.2` (reaches 80 mm below the floor and 15 mm outside the body).
`ope: 2 ringar + 8 halvribber + 3 føter med tapp opp i ring 1 13 plan 13 delar 19 ledd (3 tapp, 0 avvist) … alle harde ok`
Edge on the ring's mid-plane, 2 mm below, or 8 mm above (showing tenon): all 3 tenons, ok. 40 mm past the ring: no tenons, 3 slots, ok. `tjukn 6, kilar 1`: 16 parts (wedges `k30-1-…`), ok.

**R9 Hanging bracket** — drawn plate over the top, crossing the top ring (2 slots), cord hole as a stroke:
`40@0.5,0.5,0.5/0.3827,-0.9239,0/p:-0.2833,0.3733,0.2833,0.3733,0.2833,0.5,0.0667,0.7,-0.0667,0.7,-0.2833,0.5/-o:0,0.65,0.0267,0.0267,0` → `11 plan 11 delar 18 ledd … alle harde ok`; drawn to stop on the ring instead: 2 tenons, ok.

**R10 Box with corner fingers** — four drawn walls 2 mm inside the faces, each 200 wide (to the neighbour's outside), lid and bottom flush:
`1@0.5,0.01,0.5/0,-1,0/p:-0.3333,-0.5,0.3333,-0.5,0.3333,0.5,-0.3333,0.5;2@0.99,0.5,0.5/1,0,0/p:…;3@0.5,0.99,0.5/0,1,0/p:…;4@0.01,0.5,0.5/-1,0,0/p:…;5@0.5,0.5,0.9933/0,0,1/p:-0.3333,-0.3333,0.3333,-0.3333,0.3333,0.3333,-0.3333,0.3333;6@0.5,0.5,0.0067/0,0,1/p:…/-o:0,0,0.1333,0.1333,0`
`kasse 200x200x300: 4 veggar + lok + botn m/ hol ø40, fingrar 6 plan 6 delar 124 ledd (124 tapp) … alle harde ok` (walls alone 52; shelf inside, 192 or 200 wide: +4 tenons, ok).

**R11 Cylinder shade R 120 between two rings, tenons along the arc** — `skjerm(k, 1, 120, 340, 30, 270)` + rings at z 30 and 270, each with a ø6 hole on the seam side:
`2@0.5,0.5,0.1/0,0,1/-o:0.4,0,0.02,0.02,0;3@0.5,0.5,0.9/0,0,1/-o:0.4,0,0.02,0.02,0;1@0.0385,0.5,0.5/1,0,0/b:2.5/p:-1.1868,-0.4,1.1868,-0.4,1.1868,0.4,-1.1868,0.4`
`røyr: skjerm R120 340° … 3 plan 3 delar 10 ledd (10 tapp, 0 avvist) 0 lause · 1 ark (1200x600) · alle harde ok` · `bog: 120,0 mm — rilla, 3,6 mm steg · bogledd: 1 bøygde, alle med ledd · 625 riller`
Flat pattern 712 × 244 mm, 5 tenons per ring. Without the ø6 holes: `HARDE BROT: gods[0,0 mm]` (false alarm, see below). Edge flush with the far face or 8 mm past: same 10 tenons. 356°, 360°, 380°: same line.

**R12 Seam rib** — a flat half-rib at the seam slots into both rings and breaks the circle, so no ø6 holes are needed: `5@0.5,0.5,0.5/0,-1,0/n:1/p:0.3333,-0.5,0.4667,-0.5,0.4667,0.5,0.3333,0.5` + sheet ≤ 360°: `skjerm 358° + saumribbe + 2 ringar 4 plan 4 delar 12 ledd (10 tapp) … alle harde ok`. The sheet does not join the rib.

**R13 Half-cylinder reflector between two end ribs** — `renne(k, 1, 120, 180, -130, 130, 150)`: n = (0,0,−1) at the top, axis along Y, curls downward; end ribs are mesh planes n = Y at y = ±130:
`2@0.5,0.0667,0.5/0,1,0;3@0.5,0.9333,0.5/0,1,0;1@0.5,0.5,0.9375/0,0,-1/b:2.5/p:-0.6283,-0.4333,0.6283,-0.4333,0.6283,0.4333,-0.6283,0.4333`
`boks 280x300x160: reflektor R120 180° mellom to gavlar 3 plan 3 delar 6 ledd (6 tapp) … alle harde ok` (150°: 4 tenons).

**R14 Bent sheet CROSSING flat planes (accepted, but look at what is cut)**
- floor across the axis: ONE half-lap along the whole common arc. `skjerm 340° + midtring som kryssar: 4 delar 11 ledd … alle harde ok`; on a 180° sheet through 3 floors: sheet slot `munn -188.5 botn 0.0` (a 188 mm slit per floor), floor slot `munn 188.5 botn 0.0 krumming -120` (a 188 mm arc slot, closed).
- flat rib along the axis: half-lap along the generator, half the common height each: `skjerm 340° + 4 radialplan: 9 delar 8 ledd … alle harde ok`, slots `munn 290 botn 150` in the 20 mm wide ribs; with 2 rings added: 26 joints but `16 lause` (the long slots cut the ribs to pieces).
Keep the crossing short (a hook or lug that meets the sheet over 20–30 mm) or use R11.

## Grammar (`lib/plan.ts`: `skrivPlan(Plan[])` writes, `lesPlan(string)` reads, `reinPlan` = both)

`plan := plane(;plane)*` (max 64) · `plane := id@ox,oy,oz/nx,ny,nz[/field]*` · all numbers kept to 4 decimals.

| field | `Plan` key | meaning |
|---|---|---|
| `id` | `id` | 1..99999, the name of the part. Duplicate ids, id 0, a zero normal, or `o` outside −4..5 drop the plane silently (ran: 7 planes in, 2 out). |
| `ox,oy,oz` | `o` | point as a fraction of the placed body's box (`plan(k, id, [x,y,z], n)` converts mm). |
| `nx,ny,nz` | `n` | normal, normalised on read. 2D frame (`akser`): v = Z projected into the plane (Y when n is vertical), u = v × n. n = (0,0,1): u = X, v = Y. n = (1,0,0): u = Y, v = Z. n = (sin t, −cos t, 0): u = radial direction at angle t. |
| `b:2.5` | `bog` | bend, −4..4. R = storleik / \|bog\| (`bogRadius`). Cylinder axis = v, through `n·(o·n) + R·n`: the tangent line is the foot of the perpendicular from the engine origin (centre of the footprint, z = 0), not `o`. Positive curls toward +n. For an axis on the body's axis: `o = −R·n`. |
| `p:u0,v0,u1,v1,…` | `omriss` | drawn outline, 3..48 points, fractions of `storleik` from the plane's point, \|coord\| ≤ 2. The body is then not read for this plane. On a bent plane u is arc length. |
| `r:0,2,5` | `runde` | which outline points are arcs (the curve passes through them; no control arms). |
| `n:1` | `nett` | only with `p:`: profile = outline ∩ body. |
| `f:1` | `firkant` | mesh profile replaced by its bounding box (ran: 300 × 300 plate, slots kept). |
| `m:0.01` | `mjuk` | rounds profile corners, ≤ 0.02 of storleik (not run here). |
| `g:3` · `c:2..29` | `gruppe` · `farge` | UI group, no geometry · DXF layer `C02`..`C29` instead of `KUTT`. |
| `+r: -r: +o: -o:` `x,y,w,h,a` | `strek[]` | rectangle / ellipse, `+` adds material, `-` cuts. Centre and full size as fractions of storleik from the plane's point, `a` degrees. Max 24, applied in order. |
| `+k: -k:` `x,y,w,h,a,px,py,…` | `strek[]` | contour in a unit box (points −0.5..0.5), ≥ 3 points. |

Constructors: `rutenett(nx, ny, fromId, fromGroup)`, `formPunkt("firkant"|"trekant"|"sekskant"|"sirkel", box)`, `nyId(list)`; read but not run: `lib/gruppe.ts rundt` (×N about the axis), `lib/vektor.ts delIto / kneik / spiler / leggStrek`.

## Bound by the mesh, or not

A plane with `p:` and no `n:1` is the outline and nothing else, so it may leave the body: the R8 foot stands 80 mm under the floor and 15 mm outside, the R9 bracket 60 mm over the top (points up to ±2 × storleik from the plane's point, `o` from −4 to 5 box fractions).
The same disc ø260 at z 220 of `ope`: free `3 D04 259.8 x 259.8 50773 mm2`, through-mortises for the ribs; with `n:1` `3 D04 224.5 x 224.5 16042 mm2` (cut to the body), slots.
A free plate joins only where it meets another plate: a disc ø170 inside the hollow reached nothing (`10 delar 8 ledd … 1 lause`, soft rule `lause` only: it stays in the cut list as a loose part).

## What decides a joint, and the order rule

Per pair of planes, along their meeting line (`lib/snitt.ts`, `lib/tapp.ts`):
1. **Tenon**: the plate has an outline and its material ends at the other plate, from half a thickness short to max(10, 2t) past the far face, over ≥ max(6, 3t) of line. One tenon per 150 mm. The mortise plate may be mesh-derived. A mesh plate never gets tenons.
2. **Through-mortise**: either plate drawn, one is narrow on the line and the other surrounds it by ≥ max(2t, 6) on all sides: closed hole, the narrow one slides through along the other's normal. Ran: free disc ø260 over the ribs: `16 ledd (8 tapp)`; the same disc with `n:1`: 8 slots.
3. **Corner fingers**: both drawn, both end flush at each other, straight line.
4. **Half-lap slot**: common material ≥ max(2, t) long. Bottom at `ledd` (0.5) of the overlap. No shoulder beside it: rejected, and the pair is a hard `klem`.
Nothing at all (read in the code and README, not run): an edge the mesh gave that merely touches another plate, two plates ending at each other when one has no outline or the line is an arc, a meeting shorter than max(6, 3t), planes under 5° apart.

`orden` ("kan monterast") passes when some order exists in which every part's joints to parts already placed are parallel and point the same way.
- A ring × a vertical rib meet in a horizontal line: ribs slide in sideways. Vertical × vertical: the later one in the list comes down.
- The list sets which way a slot opens. So every rib must have ALL the horizontals it meets on one side of it in the list (rings and discs contiguous).
- Ribs that meet a ring and also meet each other can never pass (R1 closed bodies, R4 + ring, grid + ring).
- `ledd` ≠ 0.5 is lopsided on a radial lamp (0.3: rib 10 slot 7.5 of 25.1 mm, rib 14 slot 17.6). One joint: `deling: "1-10-0:0.25"` (ids ascending, crossing index, 0.2–0.8) gave ring 18.8 / rib 6.3 mm and left the rest at 12.6.
- `gods` wants ≥ max(2, t) of material at every slot bottom and around every mortise.

## Bent planes

- R = storleik/\|bog\|, so R ≥ storleik/4 (75 mm at 300). Arc length ≤ 4 × storleik: a full tube needs R ≤ 0.63 × storleik.
- Without `p:` the profile is the body unrolled: fine through a solid (`massiv sylinder R140, R=300 + 2 golv: 3 delar 2 ledd ok`), but a tube coaxial with the bend gives nothing (`0 delar`, `grip delar gods bogledd`). Draw the sheet.
- Joints exist only with a flat plane whose normal is the cylinder axis (floor) or which contains the axis direction (rib), within 0.06°. A floor tilted 5°, a rib leaning on the axis, or bent × bent: `HARDE BROT: grip gods bogledd[1 plan utan ledd]` + soft `bogkurve`.
- `orden` skips a bent plane only when it has at least one slot and stands after that flat plane in the list: **list bent planes last**. Ran: end tenons + through-mortises in two axial ribs: `orden[1 mellom 2 og 3]`; add one crossing rib and put the sheet last: ok; sheet first: `orden[5, 6]`.
- Seam: nothing joins the two ends. 360° is a butt seam, 380° overlaps with no complaint. A 361° sheet gets 4 tenons into the seam rib and then `orden[1 mellom 2 og 3]`.
- One `tjukn` for every plate; a thin shade with thick ribs is two separate runs with unmatched slots.
- Export: the part is the flat unrolled pattern on the sheet (SVG `ark`, DXF). Below the minimum radius the pattern carries `rille`: rows of through-cuts across the bend on layer `KUTT` (DXF: `GRAVER 5, KUTT 642` polylines), row pitch min(√(2tR), c·t), each cut 12t long with t bridges, none within 3t of a slot or tenon. `MOTOR.exportFile(bag, "bogprove")` is the bend coupon (also in the ALT zip).

| at R 120 | min R = factor × t | result for the R11 sheet |
|---|---|---|
| bjork 4 / 3 / 1.5 | 150t = 600 / 450 / 225 | rilla, pitch 3.6 / 2.7 / 1.4 mm, 625 / 1244 / 5910 cuts, 31 / 46 / 107 m of cut |
| finer 3 · graa 3 | 100t = 300 | rilla 3.0 mm, 1123 cuts, 42 m |
| mdf 3 · akryl 3 | 200t = 600 · 230t = 690 | rilla 2.4 mm, 1401 cuts, 52 m |
| papp 2 / 6 | 10t = 20 / 60 | no scoring, 1.9 m |
| finer 1 / 1.2, bjork 0.8 | 100 / 120 / 120 | no scoring, but `gods` broke in this recipe at these thicknesses (not investigated) |

`bog` is soft while the row pitch is > 3 × `snitt`; hard otherwise (4 mm bjork: snitt 1.1 ok, 1.3 `HARD «120,0 mm av minst 600,0 mm»`).

## Names

Address = plane id, plus `a b c…` when the plane gives several pieces (`7`, `12a`, `12b`, `30`); wedges are `k<tenon plane>-<mortise plane>-<n>` with plan 0. It is engraved on layer `GRAVER`; `merk: 1` also cuts it into the 3D files. `Kutt.id` (`D01`…) is the shape: equal ids are identical parts. Ids are yours to choose in a plan string and are never renumbered; `nyId` = highest + 1.

## What does NOT work

- Full planes through one axis on a closed dome or solid: N−1 parts stuck (`orden`), and on a solid 2 parts + dozens loose. Use R2.
- Rings together with ribs that cross each other (vortex + ring, grid + ring, two oblique families + ring): `orden`, no list order fixes it.
- Mesh planes at the faces of a box (no outline): `klem[1–2, 1–4, 2–3, 3–4]`, 0 joints. Draw the walls (R10).
- Polygon prisms with drawn walls (5, 6, 8 sides): fingers are made (65 / 78 / 104) but `orden[6 mellom 1 og 5]` — the last wall cannot enter two non-parallel corners. Only 90° boxes pass.
- `gods[0,0 mm]` false alarm: arc mortises all round a closed ring. The wall check walks the circle and loses the run that wraps past the point opposite the sheet's tangent line. Anything that cuts the ring on that circle there (ø6 stroke hole, seam rib slot) removes it.
- A foot edge spanning the whole 25 mm ring wall: `gods[4,0 mm]` (3.96 < 4). Keep the meeting ≥ 2 mm inside the wall at each end (trapezoid foot: 4.18, ok).
- A drawn plate in the same plane as a rib (foot at the rib's angle): `gods[0,0 mm]`.
- Shelf drawn exactly max(10, 2t) proud (220 × 220 in the 200 box at 4 mm): `gods[0,0 mm]`, 1 piece dropped. At 6 mm with `kilar 1`: 9 parts, ok.
- Wedges need t ≥ 6 (4 mm, `kilar 1`: no wedges, same 3 parts).
- The order check does not sweep: the ø260 disc with through-mortises passed although the tapered ribs cannot physically slide through it.
- `lause: 1` (default) silently drops jointless pieces of a plane that has joints elsewhere; a plane with no joint at all stays in the cut list as a loose part. Both only show as `lause` in the line (soft rule). Check `m.loose === 0`.
- Sheet size: the 340° pattern is 712 mm long; on 600 × 400 it is `plate[1 utanfor]`.
