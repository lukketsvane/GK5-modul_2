# LES.md — the lamp toolkit: one `konsept.ts` in, cut files, pictures and a STEP assembly out

Everything here was run on 2026-11-17 against `/home/user/slicer.iverfinne.no` (read-only, `git status` empty). Nothing was cut on a machine.
`V = /tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/verkty` · depth: `V/../kart/{motor,plan,reglar,ut,syn,forgecad}.md`

```bash
cd /home/user/slicer.iverfinne.no
npx tsx $V/lag.ts <folder> --rask      # 15–28 s: engine, report, contact sheet. Iterate with this.
npx tsx $V/lag.ts <folder> --step      # 2.3–2.7 min: + every production file, 7 large views, STEP assembly (--stor: views at 2x)
npx tsx $V/lag.ts <folder>             # 2 min: no flag = production files and large views, no STEP
```

`<folder>` holds your `konsept.ts`; everything is written to `<folder>/ut/`. A new concept goes in its own folder anywhere under `V/..`; import the toolkit by absolute path.

Exit 0 = no hard rule broken and every `krav` holds, 1 = something fails (files are written anyway), 2 = crash. It prints five lines; read `<folder>/ut/rapport.txt`. Through a pipe the exit code is the pipe's: use `${PIPESTATUS[0]}` or read the first line (`ALT OK` / `IKKJE OK`).

## 1. A complete `konsept.ts` (this is `V/eksempel/ribber/konsept.ts`, minus the long import paths)

```ts
import { profil, skal } from "<V>/form"
import { halvribber, ringar, utanfraa } from "<V>/plan"
import type { Kontekst, Params, Registrert, Utstyr } from "<V>/typar"

export const namn = "ribber"                       // names the files; the source id is its letters and digits
const H = 250, NAV = 44, HOL = 40.4, Z_NAV = H - NAV / 2
const ytre = (z: number) => 58 + 102 * Math.pow(1 - Math.pow(z / H, 2.2), 1 / 2.2)

export const kropp = () => skal(profil(ytre, 0, H, 72), { vegg: 24, seg: 128, nav: { hogd: NAV, hol: HOL } })
export const bag: Partial<Params> = { tjukn: 4, material: "bjork", klaring: 0.1, snitt: 0.2, arkB: 600, arkH: 400 }
export const plan = (k: Registrert) => utanfraa(ringar(k, 1, [22, 125, Z_NAV]), halvribber(k, 10, 16, 34))
export const utstyr: Utstyr = {
  heng: { tak: H + 420, feste: [0, 0, Z_NAV + 12] },
  utstyr: [ { slag: "sokkel", senter: [0, 0, Z_NAV - 18], diameter: 42, lengd: 60 },
            { slag: "paere", senter: [0, 0, Z_NAV - 108], diameter: 60, lengd: 105, retning: [0, 0, 1] } ],
}
export const krav = (x: Kontekst) => [
  x.holKrav("3", HOL),                                                      // lampholder hole in part 3
  x.friKrav("fritt rundt pæra", [0, 0, Z_NAV - 140], [0, 0, Z_NAV - 70], 45, ["3"]),
  x.krav("ingen ribbe er vorten tapp", x.tappar === 0, `${x.tappar} tappar`),
  x.krav("største del får plass på 600 x 400", Math.max(...x.liste.map((d) => Math.max(d.w, d.h))) <= 393, "…"),
]
```

- `kropp()` returns a triangle soup (mm, Z up, **centred on x = y = 0, standing on z = 0**, closed, ≤ 40 000 triangles) or a path to an STL/GLB. All coordinates you write (plan, hardware, krav) are in that frame, 1:1. `storleik` is set for you. For a standing lamp z = 0 is the table: the pictures put the floor at the lowest point.
- `bag` overrides `DEFAULT_PARAMS` (`kart/motor.md`, parameter table). Defaults here: `tjukn 4`, `bjork`. Never set `rotX/Y/Z`, `glatt`, `forenkl`, `hol`, `scene`.
- `plan` is `Plan[]`, a plan string, or a function of the registered body `k` (needed by every constructor: it turns mm into the fractions the engine stores).
- `utstyr` is the picture only: `heng` (ceiling z, cord from `feste`), `vegg`, or nothing (stands on a table); `utstyr[]` hardware (`paere sokkel leidning sylinder boks kule`, see `kart/syn.md`; `paere.senter` is the centre of the glass and `retning` points from there to the screw base: `[0,0,1]` hangs, `[0,0,-1]` stands; a table lamp's cord is `{ slag: "leidning", punkt: [[0,0,30],[0,-30,10],[0,-90,4],[20,-260,3]], diameter: 6 }`); `kamera`, `material`; `delar: { "3": { farge: "#333" } }` per-part look; `steg` your own exploded order; `ekstra` (section 7).
- `krav(x)` returns your own checks. `x`: `del(adr)`, `hol(adr)` (ø by area, r range, centre in the body, `iLuft` when the hole sits inside another hole of the part; `holKrav` fails on that), `fri(a, b, skip?)` (smallest distance from a segment to any plate), `tappar`, `liste`, `m` (Metrics), `data` (delar.json), and the builders `krav / holKrav / friKrav`.

Real output of that file (`--step`, 137 s):

```
ribber — 320 x 320 x 250 mm · bjork 4 mm · klaring 0.1 · snitt 0.2 · ALT OK
harde    grip ok · delar ok · orden ok · klem ok · gods ok · plate ok · snittspor ok
tal      19 delar · 48 ledd · 0 lause · 3 ark · 18.48 m · 0.531 kg · mjuke: utnytting 31 %
krav     17 av 17 ok
```

Working order that kept me out of trouble:

1. Body alone with two rings: run `--rask`, read the `nett` line and the built-in `krav`, look at `ark.png`.
2. Add one family of planes at a time. After each run read `tal` first (as many parts as planes? `0 tapp`? `0 lause`?), then the hard rules, then the picture.
3. Add hardware and your own `krav` (lampholder hole, air round the bulb). Run `--step` only when `--rask` says `ALT OK`.

Ids are the engraved addresses and are never renumbered: rings 1.., ribs 10.., feet 30.. reads well. The list order decides which way each slot opens; the assembly order in the report is the engine's own and may differ.
Hardware sizes I used for the stand-ins (typical parts, not measured here): E27 lampholder with threaded skirt ø40 and shade rings ø57, so keep 30 mm round the axis free on the plate; A60 bulb ø60 × 105; cord ø6.

## 2. What is written into `<folder>/ut/`

| path | what | cells |
|---|---|---|
| `rapport.txt`, `rapport.json` | the verdict (section 3); the JSON has every rule, metric, part and step | 220 |
| `ark.png` | contact sheet 1800 × 1200: helt · lys · sprengt / front · side · topp · under, built from the real cut parts | 220 |
| `delar.json`, `scene.json`, `kropp.stl` | per part: outline, holes, thickness, 4×4 matrix, step; the renderer's scene; the design surface | 220 |
| `produksjon/ark-N.dxf .svg .png` | cut sheets exactly as the phone app writes them (byte-identical, `kart/ut.md`) | 220 |
| `produksjon/fin/ark-N.dxf .svg`, `fin/delar.json` | **the files to cut**: same parts and joints, slot-bottom corners true to 0.16 mm instead of 1.5 mm (`kart/reglar.md`). Nested on their own: on `ribber` the parts lie on other sheets than the `ark` list in the report, and the `fin` line then lists them | 1200 |
| `produksjon/` rest | `samla.glb .stl .usdz`, `deler.3mf`, `flat.glb`, `profilar.svg`, `passprove.svg` (+ `bogprove.svg`), `montering.txt`, `deler.csv`, `reglar.txt`, `alt.zip`, `<id>.zip` (the project the app opens), `manifest.json`, `ekstra-<namn>.svg .dxf` | |
| `bilete/<id>-{helt,lys,sprengt,front,side,topp,under}.png` | 1400 × 1400 each; front, side, topp near-orthographic, no scale bar (the bar is only on `ark.png`) | |
| `step/<id>.step` + `_iso _front _top _sprengt.png`, `.forge.js` | named, coloured B-rep assembly from the 1200-cell parts, read back with OCP | 1200 |

Why two detail levels: the STEP built from 220-cell outlines overlapped 249 mm³ in the 48 joints of `ribber` (8.6 mm³ per slot bottom); from 1200 cells 5.6 mm³ (0.2 mm³ each). Cut `fin/`, build CAD from `fin/`; the rules and numbers are read at 220.

## 3. Reading `rapport.txt` and the contact sheet

```
tal      19 plan · 19 delar (5 unike) · 48 ledd (0 tapp, 0 avviste) · 0 lause
kutt     18.48 m · 15.4 min ved 20 mm/s · 3 ark 600 x 400 · utnytting 31 % · 0.531 kg · spor 4.10 mm · minste gods 12.0 mm
harde reglar
  ok   gods       gods i leddet            12,0 mm            (one line per hard rule; a BROT line is followed by the engine's own reason)
ark
  1  3 1 15 16 · 32 % av brukt hogd, 28 % av arket            (also: parts with no engraved address, parts nested inside another's hole)
delar    15..25 (8)     D01   126.0 x 250.0   3     1,2,3     (8 identical parts, first..last address · b x h · joints · sheets)
montering (motoren si eiga rekkjefylgje)
  1-3  ligg: 1 2 3
  4-11  side kvar langs sitt eige spor mot 1,2,3: 15 16 17 18 19 20 21 22       (a stuck part reads << STÅR FAST)
krav
  ok   hol ø40.4 i del 3: ø40.21 likt areal · r 20.03..20.20 · 29 punkt · senter -0.0, -0.0, 228.0
  ok   fritt rundt pæra: 59.0 mm til del 15, kravet er 45 mm
step     … 19 solid · 19 gyldige · avvik -0.000000 · overlapp 60 par testa · 48 med volum · sum 5.572 mm3
```

- `19 plan · 19 delar`: with half-ribs every plane is one part. Fewer parts than planes means planes vanished; the check `kvart plan gjev minst éin del` names them.
- **tapp** must be 0 unless you drew tenons on purpose; **avviste** and **lause** must be 0.
- **gods** is the material left at the weakest joint; the rule wants ≥ max(2, tjukn). **utnytting** under 35 % is only advice (rings waste sheet).
- The eleven built-in checks: mesh closed, ≤ triangle budget, centred, 1:1, engine volume = mesh volume (a filled cavity shows here), every plane read back, the app opens the bag unchanged (`storleik` ≤ 600!), nothing loose, everything on a sheet, every plane gives a part, no slot cut on through filled material past its mouth (section 7). A full run adds two: the 1200-cell files give the same parts, and the STEP was written and read back.
- The `ledd` column is the engine's slot count for that part, not its number of neighbours.
- `ark.png`: **helt** is the product picture; **lys** is the honest one (a lamp that traps light is dark); **sprengt** moves each part against its real assembly direction; **front / side / topp** are elevations through a 6° lens (near-orthographic: the front and back of a 220 mm deep lamp differ 6 % in size, 29 % before) with a 100 mm bar, so front and side can be compared and measured; **under** is what you see looking into it. A table cord is not counted when the elevations are framed. The footer counts engine parts and `ekstra` apart. Check: ribs complete, no plate through the bulb, hole centred on the socket, cord from the right point.

## 4. `form.ts` — bodies (every function returns a closed soup; `sjekkNett(n).ok` proves it)

- `skal(profile [r, z][] bottom rim first, { vegg, seg?, nav?: { hogd, hol? } })` thick shell of revolution; `nav` = solid top with a through-hole. `profil(z => r, z0, z1, n)` samples the profile. `skalRing` shows the 2D section.
- `loft(sections { z, ring }[], { vegg, lok?, hol? })` skin through closed sections (same point count), wall `vegg` mm thick, open at both ends; `lok` = mm of solid lid at the top, `hol` = diameter of a hole through that lid (ran: `lok: 36, hol: 56` on a 300 mm body gives r 28 from z 264 up). Rings from `sirkelRing(r, n)`, `superRing(a, b, e, n)` (half-axes; `e` 2 = ellipse, 4 = squircle), `bylgjeRing(r, amp, lobes, n)`, `vriRing(ring, deg)` (twist), `blandRing(a, b, t)`.
- `vri(mesh, z => deg)` twists any mesh about Z · `spegl(mesh, 0|1|2)` mirrors · `skaler` · `flytt(mesh, [x,y,z], rotZ)` · `sentrer(mesh)` · `saman(a, b…)` union by overlap.
- `dreiRing(section)`, `sylinder(r, z0, z1)`, `skive(rOuter, hole, z0, z1)`, `boks(b, d, h)`, `prisme(polygon, z0, z1, holes?)`.
- `forgeStl("x.forge.js", "x.stl", { Param: 96 })` runs ForgeCAD and returns the STL path (ran: 1.2 s, 19 200 triangles, closed); set segment counts in the script, `--quality` does nothing. `lesNett(path)`, `skrivStl`, `skrivGlb`.
- A hole or cavity must be part of ONE connected surface (`skal`, `loft`, `skive` are). Subtraction and closed inner shells are silently filled.

## 5. `plan.ts` — planes in mm (`k` = the registered body)

A plane has an id (1..99999 = the part's engraved address), a point, a normal. 2D frame: `n = (0,0,1)` → u = X, v = Y; a vertical plane → v = Z.

| constructor | gives |
|---|---|
| `ringar(k, id0, [z…], extra?)` | horizontal sections of the body; `extra` (strokes) goes on every ring of the call |
| `halvribber(k, id0, N, r0, { z0, z1, r1, fase })` | N radial half-planes from radius r0 outward, cut to the body (`p:` + `n:1`) |
| `utanfraa(horizontals, ribs)` | the list order that opens every ring slot at the rim |
| `radial(k, id0, N)` · `lameller(k, id0, "x"\|"y", [pos…])` · `rutenett(nx, ny)` | full planes through the axis · parallel slats, `"x"` = the planes x = pos · egg-crate (`rutenett` takes no `k`) |
| `radialplate(k, id, deg, [[r, z]…], extra?)` | a free drawn plate in a radial plane: feet, brackets, fins (no `nett: true` = may leave the body) |
| `golv(k, id, z, [[x, y]…], extra?)` · `vegg(k, id, n, dist, [[u, z]…], extra?)` · `rundskive(k, id, z, r, hole)` | drawn floors, walls, discs |
| `skjerm(k, id, R, deg, z0, z1, mid = 180)` · `renne(k, id, R, deg, y0, y1, zTop)` | bent sheet about Z (opening opposite `mid`) · trough about Y |
| `rundt(k, "hol"\|"gods", d, x, y)` · `rektStrek(k, slag, b, h, x, y, deg)` · `ellipse` | strokes for `extra.strek`: cut or add material, ≤ 24 per plane |
| `plan(k, id, [x,y,z], n, extra)` · `mm(k, pts)` · `sirkel(k, r)` | the general plane · outline fractions · a 24-point round outline |

## 6. Recipes that pass (`V/prov/kokebok.ts`, 4 s: 14 of 14, columns trimmed here; three are full examples)

```
K2 kuppel: 2 ringar + 16 halvribber r0 12, utanfraa    18 plan 18 delar 32 ledd (0 tapp)  harde ok     utanfraa(ringar(k,1,[60,200]), halvribber(k,10,16,12))
K3 kuppel: rutenett 5x5                                10 plan 10 delar 21 ledd           harde ok     rutenett(5, 5)
K4 kuppel: 3 ringar + 5 lameller langs y                8 plan  8 delar 28 ledd           harde ok
K5 ope: ring + rundskive r100 m/ hol 40 + 8 halvribber 10 plan 10 delar 16 ledd           harde ok     utanfraa([...ringar(k,1,[60]), rundskive(k,3,220,100,40)], ribs)
K6 … + 3 føter med tapp i ring 1                       13 plan 13 delar 19 ledd (3 tapp)  harde ok     radialplate(k,30,22.5,[[105,-80],[165,-80],[145,60],[105,60]])
K8 kasse 200x200x300: 4 veggar + lok + botn m/ hol      6 plan  6 delar 124 ledd (124 tapp) harde ok
K9 røyr: skjerm R120 340° mellom to ringar              3 plan  3 delar 10 ledd (10 tapp) harde ok     rings carry strek [rundt(k,"hol",6,120,0)]
K10 boks: reflektor R120 180° mellom to gavlar          3 plan  3 delar  6 ledd (6 tapp)  harde ok
```

- **`eksempel/ribber`** — rib pendant: shell with a 44 mm hub, 3 rings, 16 half-ribs. 19 parts, 48 joints, 3 sheets, 0.53 kg.
- **`eksempel/lykt`** — drawn plates only: 4 walls with 5 slits each (strokes), shelf with the ø40.4 hole, bottom, top frame. 7 parts, 104 finger and tenon joints, 2 sheets, 66 % utilisation, 0.60 kg. 16 of 16, 217 s.
- **`eksempel/skjerm`** — bent language: a 340° scored birch sheet R 120 with 10 tenons in arc mortises of two rings, top ring filled to a disc with `+o`/`-o` strokes. 3 parts, 515 score cuts, 30.9 m of cut, sheet 800 × 450.
- **`prov/mi`** — table lamp `rist` (written by the first user from this manual): `loft` of squircles with a lid, 4 rings, 4 slats `lameller(k,10,"x",[-95,-46,46,95])`, the two inner ones arches over the bulb; ring 1 carries the lampholder on a bridge `strek: [rektStrek(k,"gods",80,180), rundt(k,"hol",40.4)]`; a pp sleeve as `ekstra`. 8 parts, 22 joints, 3 sheets, 12.23 m, 0.47 kg, 18 of 18, 146 s.
- The lampholder plate: a ring through a `nav`, or a ring with `strek: [rundt(k,"gods",D), rundt(k,"hol",40.4)]`, or `rundskive`. Model ø40.4 for a 40 mm thread: the cut polygon is inscribed (r 20.03..20.20). The fill must reach into the ring's own material all round or along a bridge, and no slot of that ring may open towards it (section 7).

## 7. Traps (ran here, or in `kart/plan.md` and `kart/reglar.md`)

- **A drawn rib that stops near a plate becomes a tenon and is cut off there.** A plate with an outline (`halvribber`, `radialplate`, `vegg`, `golv`) needs its own material to continue ≥ t/2 + max(10, 2t) = 12 mm (t = 4) past the mid-plane of every plate it crosses, on both sides, along the whole meeting (stretches under max(6, 3t) do not count). Ran (`V/prov/tappgrense.ts`, `rib2.ts`): ring 14 mm from the rib's end fine, 12 mm half the ribs gone, 10 mm all gone; on `ribber` a hub 28 or 36 mm thick with the plate in its middle → **all 16 ribs gone, 3 parts, 64 joints, every hard rule green**; hub 44 → 19 parts. A surface that curves away within those 12 mm counts as an end (a ring 22 mm under the rim of the curved top lost the ribs; a straight 45° cone kept them). Keep rings ≥ 14 mm from where the rib's material stops, or use `radial` (mesh planes never get tenons). Checks: `kvart plan gjev minst éin del`, `x.tappar`.
- **A slot opens through whatever lies past its mouth.** A ring filled with a `gods` stroke and crossed by slats whose slots open inward (every arch does on one leg: `lameller` or `radial` through a hollow body) is slit from that slot to the far rim. Ran on `rist`: fill ø196, slats at x = ±46 → plate 1 cut by two 4.1 × 192 mm slits, the lampholder left on a 14 mm bridge, `ledd` 4 instead of 6, every hard rule green (`kart/prov/rist-spalte-ark-1.png`). The check `ingen spalte held fram gjennom gods forbi munnen` now fails on it (`del 1 spor 1-11-0: 177 mm`). Fix that ran: fill only a bridge between the slats, its edge 6 mm from the slot line (`rektStrek(k,"gods",80,180)` between slats at ±46). With `utanfraa` and half-ribs every ring slot opens at the rim and a fill is safe.
- **A `gods` stroke that does not reach the ring is an island: it is thrown away** (`1 lause · 1 kasta`) but its ø40.4 hole stays in the part and in the cut file. Ran: fill ø150 in a cavity 153 wide. `holKrav` now fails on it (`ligg i eit anna hol`).
- **An arch is not slid in sideways, whatever `montering.txt` says.** A slat crossing a ring on two legs has one slot opening outward and one inward. Worked out from the measured slots of `rist` (not simulated): pushed straight in along its line, the far leg hits the ring's near band; it has to be lowered over the rings with one leg inside them and one outside, at least 59 mm off its seat there, then slid home. So the arch must be open wider than the rings it passes, and nothing may fill those rings.
- A plane that runs within a few mm of a cavity wall where it meets a ring gives hard `klem` (ran: slats at x = ±76 where the cavity edge is at 76.2–76.6). Keep it 5 mm inside the cavity (ran: fine) or well inside the wall.
- Full planes through the axis of a closed dome or solid: `orden` (N − 1 stuck). Rings plus ribs that cross each other (grid + ring, vortex + ring): `orden` in every order. Use half-ribs.
- A full plane cut in two pieces (through a hub hole) opens half its ring slots into the hole. `holKrav` catches it (ran: `r 16.50..35.89 … utanfor ø39.5..ø41.0`).
- Bent planes join only floors across their axis or ribs along it; need a drawn outline; go last in the list; the seam is never joined; arc mortises all round a closed ring give a false `gods 0,0` unless the ring has a ø6 stroke hole on the mortise circle opposite the sheet's middle; 4 mm birch at R 120 is scored (515 cuts and 30.9 m on `skjerm`).
- One `tjukn` and one material per run. A thin diffuser is an `ekstra`, not a plane.
- Never `MOTOR.fiksAlt`: it rescales the body. A part larger than the sheet room (593 × 393 on 600 × 400) is in no cut file. Pieces under 400 mm² vanish.
- Crossings away from 90° are cut too narrow for square edges (derived in `kart/reglar.md`, not cut): keep plates perpendicular.
- Drawn boxes: each three-way corner carries a 0.01 × 4 mm whisker in the outline, sticking out into scrap. Stroke corners are chamfered 1.1 mm at 220 cells and 0.2 mm in `fin/` (measured on `lykt`).

`ekstra` — parts the engine does not know (diffusers, acrylic discs), drawn in every picture, written as `produksjon/ekstra-<namn>.svg/.dxf` (1:1, no kerf) and put in the STEP; no rules, no joints, not in `fri`:

```ts
import { flatark, sylinderark } from "<V>/ekstra"
ekstra: [ sylinderark({ namn: "diffusor", R: 70, grader: 360, z0: 40, z1: 200, tjukn: 0.5, material: "pp" }),
          flatark({ namn: "botnskive", punkt: [0, 0, 40], n: [0, 0, 1], omriss: sirkelRing(72, 48), tjukn: 3, material: "akryl-opal" }) ]
```

Picture materials: `bjork poppel papp mdf akryl-opal pp` (bag `finer`/`graa` → poppel, `akryl` → akryl-opal).

## 8. Numbers to design against (code and runs in `kart/reglar.md`)

| what | number |
|---|---|
| slot width | (tjukn + klaring) / sin θ nominal; the file is narrower by `snitt` (4.10 → 3.90 at t 4, k 0.10, s 0.20) |
| slot depth | half the common run (`ledd` 0.5); one joint: `deling: "1-10-0:0.25"` |
| a joint is cut when | common run ≥ max(2, t) and the plate is w + 4 mm wide across the slot (8.1 mm at t 4), else hard `klem` |
| gods | ≥ max(2, t) left at the slot bottom → shell wall ≥ 8 mm at t 4; 20–26 mm walls gave 10–12.6 mm |
| tenon | meeting ≥ max(6, 3t); one per 150 mm; wedges only at t ≥ 6 (`kilar: 1`) |
| smallest piece | 400 mm² net; smallest feature about storleik / 220 |
| sheet | 600 × 400 takes 593.3 × 393.3; 5.8–8.8 mm between parts; raise `arkB/arkH` yourself |
| body | longest side 40–600 mm in the app; ≤ 40 000 triangles; ≤ 64 planes; outline ≤ 48 points |
| bend | R ≥ storleik / 4; solid down to R = 150·t birch, 100·t `finer`, 200·t mdf, 230·t acrylic, 10·t cardboard; tighter is scored (cut length × 5–7) |
| STEP | keep parts under about 500 outline points; 1.5 kB per point |

## 9. Bags (`kart/reglar.md` section 6: klaring 0.10 and the densities are the tool's, kerf and speed are guesses until the fit coupon is cut)

| | material | tjukn | klaring | snitt | fart |
|---|---|---|---|---|---|
| 3 mm birch ply | `bjork` | 3 | 0.10 | 0.15 | 15 |
| 4 mm poplar ply | `finer` (mass reads a third high) | 4 | 0.10 | 0.20 | 15 |
| 3 mm acrylic | `akryl` | 3 | 0.15 | 0.20 | 10 |
| 2 mm cardboard | `papp` | 2 | 0.05 | 0.30 | 50 |

`tjukn` is the caliper reading. Cut `produksjon/passprove.svg` first and set `klaring` to the slot that holds.

## 10. What this toolkit cannot do, and what was not tested

- Bent parts in the STEP are a union of flat strips (sagitta 0.05 mm): volume −0.27 %, box within 0.04 mm on `skjerm`, no score cuts. Outlines are polylines everywhere; no arcs.
- The STEP reports sliver overlaps in every joint (5.6 mm³ over 48 joints on `ribber`, 1.1 mm³ on `lykt`); `forgecad --connectivity` therefore says parts hang together. Read `lesstep.py --overlapp` volumes in `rapport.txt`.
- ForgeCAD's `export step` is free for personal non-commercial use only; the owner decides whether production needs a licence.
- `fri` treats a bent part by its unrolled pattern; `ekstra` parts are not in it. No collision check between plates beyond the engine's own rules.
- A mixed-thickness lamp (thin shade in thick ribs) cannot get matching slots in one run.
- The `fin/` DXF were read back (same polyline counts as the 220 files, everything inside the sheet; a second reader in `kart/prov/dxfsjekk.py`: every KUTT outline closed, holes before their outline, GRAVER first, slots 3.90 mm wide) but never cut; the app itself can only write the 220 ones.
- Nothing checks that a part can travel to its seat: the engine reads joint directions only (the arch in section 7).
- A curved edge is as smooth as your mesh: on `rist` ring 2 the corners of the mesh's 96-sided section lie a median 0.03 mm from the `fin/` outline (0.14 mm at 220 cells), so its 7 mm facets are cut as facets. Give section rings more points for a smoother edge (not run).
- Not run: a real laser, a real iPhone (the project zip was opened in Chromium only, `kart/ut.md`), `--stor`, bodies over 600 mm. Run once each, in `V/prov/`: a ForgeCAD body (`forgekropp`), a GLB body (`glbkropp`: the same 11 parts, 24 joints, 10.47 m as `kart/motor.md`), a wall scene with own camera and steps (`vegg`), `ekstra` parts (`ekstra`), a deliberately broken concept (`brot`: exit 1, both hard breaks and five failed checks named).
