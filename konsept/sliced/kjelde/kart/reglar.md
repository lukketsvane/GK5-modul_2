# reglar.md — the rules and the material, to design against

Run on 2026-11-17 against `/home/user/slicer.iverfinne.no` (read-only, `git status` empty after). Every number marked "ran" is pasted from a script in
`G = /tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/kart/regel`; "code" means read, not run.
Run: `cd /home/user/slicer.iverfinne.no && npx tsx G/<name>.ts`. Body building and the headless path are in `kart/motor.md`.
Test lamp = the dome of `motor.md`: 300 mm, wall 25, hub with ø40 hole, 3 horizontal + 4 vertical planes.

## Recipe 1 — read the rules, never press the fixes

```ts
const m = MOTOR.measure(bag); const rs = MOTOR.rules(bag, m)       // Rule: id, label, hard, ok, value, why, fiks?{ord,set,riv}
const hard = rs.filter((r) => r.hard && !r.ok)                      // must be empty before a file is written
```

Do **not** call `MOTOR.fiksAlt` or apply `plate`'s fix on a 1:1 lamp: it rescales the body (ran, `reglar.ts`):
`fiksAlt paa ark 300 x 200 + klaring 0.4: fiksa [klaring, plate] · storleik 300 → 190 · att [ingen står i kvarandre]` — the E27 hole shrinks with it and a new hard break appears.

## Recipe 2 — four bags (ran, `posar.ts`; `MOTOR.clamp` leaves all four untouched)

| bag | material | tjukn | klaring | snitt | snittveg | fart | slot nominal / drawn | lamp result |
|---|---|---|---|---|---|---|---|---|
| 3 mm birch ply | `bjork` | 3 | 0.10 | 0.15 | 0 | 15 | 3.10 / 2.95 | 11 parts · 24 joints · gods 12.5 · 10.46 m · 11.6 min · 0.222 kg · 2 sheets |
| 4 mm poplar ply | `finer` | 4 | 0.10 | 0.20 | 0 | 15 | 4.10 / 3.90 | 11 · 24 · 12.5 · 10.47 m · 11.6 min · 0.299 kg · 2 |
| 3 mm acrylic | `akryl` | 3 | 0.15 | 0.20 | 0 | 10 | 3.15 / 2.95 | 11 · 24 · 12.5 · 10.46 m · 17.4 min · 0.395 kg · 2 |
| 2 mm cardboard | `papp` | 2 | 0.05 | 0.30 | 0 | 50 | 2.05 / 1.75 | 11 · 24 · 12.5 · 10.49 m · 3.5 min · 0.049 kg · 2 |

All four: no hard break, only soft `utnytting` 25–29 %. Reasons and what is mine are in section 6. `tjukn` is a placeholder: the tool wants the caliper reading.

## Recipe 3 — production cut files at a finer field (headless only; the app always writes 220 cells)

```ts
import { skrivKuttfiler } from "G/felles"       // makeBygg(p, celler) → sheetDxf / sheetSvg(ns, i, kerfOf(p)) per sheet
skrivKuttfiler(p, 1200, mappe, "lampe")          // lampe-c1200-ark-1av2.dxf + .svg …
```

Why: slot walls are exact, slot-bottom **corners are not** — the field leaves a chamfer one cell tall (cell = storleik / cells).
"sete" = how far before the slot bottom a rigid plate of `tjukn` stops against those chamfers, measured on the cut polygon (ran, `fin.ts`, 4 mm lamp):

```
motoren (220): 11 delar · 24 ledd · 10.47 m · 2 ark · harde brot 0
celler  220:    8 ms · 11 delar · 24 ledd · 10.47 m · 2 ark · sete 0.00..1.50 mm · DXF 14 kuttkonturar 1125 nodar
celler  440:  413 ms · 11 delar · 24 ledd · 10.51 m · 2 ark · sete 0.00..0.65 mm · 1421 nodar
celler 1200: 1410 ms · 11 delar · 24 ledd · 10.54 m · 2 ark · sete 0.00..0.16 mm · 1867 nodar
```

Same parts, joints and sheets; rules and numbers are still read at 220. Plywood crushes a 0.7 × 1.4 mm corner, acrylic does not.

## Recipe 4 — the two coupons

`MOTOR.exportFile(bag, "prove")` → `passprove-3mm-bjork.svg`, `"bogprove"` → `bogprove-3mm-bjork.svg` (both use the bag's tjukn, snitt, snittveg, material). Ran, `stoff.ts` / `posar.ts`:

```
passprove-3mm-bjork.svg: 107.25 x 34.15 mm     spor 2.85 2.90 2.95 3.00 3.05 3.10 3.15 i fila   (snitt 0.15)
passprove-4mm-finer.svg: 142.30 x 38.20 mm     bogprove-4mm-finer.svg: 368.20 x 180.20 mm
passprove-2mm-papp.svg:   72.40 x 32.30 mm     bogprove-3mm-akryl.svg: 228.20 x 141.20 mm
```

- Fit coupon (code): seven slots, clearance 0 … 0.30 in 0.05 steps, engraved in 1/100 mm; depth max(10, 4·t), shoulder max(4, 2·t). Take the number of the slot that holds → `klaring`. If none holds, `snitt` is too low.
- Bend coupon (code): five scored fields at 0.5, 0.75, 1, 1.5, 2 × the table row step, the step engraved under each; bend each, keep the coarsest that survives. It is put in the ALT zip only when a plane is bent.

## 1. The rules (code `lib/rules.ts`; every break and fix ran in `reglar.ts`)

| id | panel label | English | kind | passes when | fix sets |
|---|---|---|---|---|---|
| `grip` | plana grip | planes grip | HARD | joints > 0 | none |
| `delar` | delar å skjere | parts exist | HARD | parts > 0 | none |
| `orden` | kan monterast | can be assembled | HARD | no flat part has joints to two already placed parts along lines more than 3° apart | `plan` reordered; else removes the stuck planes (riv) |
| `klem` | ingen står i kvarandre | nothing clamps | HARD | no two flat plates both keep > 1 mm of material on their crossing line | removes the plane in most pairs (riv) |
| `lause` | utan ledd · kasta / delar utan ledd | every part hangs in a joint | soft at `lause` 1, HARD at 0 | 0 parts without joint and 0 dropped | `lause: 1` |
| `gods` | gods i leddet | material left at the joint | HARD | `narrow` ≥ max(2, tjukn) | `ledd`: first of 0.5, 0.4, 0.6, 0.35, 0.65 … that passes |
| `plate` | delane får plass | parts fit the sheet | HARD | 0 parts outside, 0 pinned parts overlapping | mesh: `storleik` = ⌊storleik·worst·0.98 / 5⌋·5; drawn outline: `arkB/arkH` up in 50s; pins: `fest` |
| `klaring` | klaring | press fit | soft | 0.05 ≤ klaring ≤ 0.35 | `klaring: 0.1` |
| `snitt` | snittbreidd | kerf is set | soft | snitt > 0 | `snitt: 0.2` |
| `snittspor` | snittet mot sporet | slot survives the kerf | HARD | snitt < tjukn + klaring | `snitt` = ⌊slotW·0.5 / 0.05⌋·0.05 |
| `opning` | opning mellom plan | room between planes | soft | planes within 10° of parallel with overlapping profiles: distance − tjukn ≥ 3 | removes the close ones (riv) |
| `lukka` | lukka nett | mesh closed | soft | open edges = 0 | none |
| `nett` | nettoppløysing | resolution kept | soft | triangles ≥ 500, or none were removed | `trekant` up |
| `utnytting` | utnytting | utilisation | soft | part area / (used strip × arkB) ≥ 0.35, or 1 sheet | none |
| `bog` | bøyeradius | bend radius | HARD only if scoring cannot be laid | R ≥ BOG·tjukn, or row step > 3·snitt (then scored, soft, ok) | `plan`: bend relaxed to R = BOG·tjukn |
| `bogledd` | ledd på bøygde plan | bent ribs carry joints | HARD | every bent rib has a slot or a tenon | `plan`: those bends → 0 |
| `bogkurve` | møte på bøygde plan | meetings on bent planes | soft | no flat plane slanted to a bend axis | straighten (riv) |

`riv` fixes delete work and are skipped by `fiksAlt`; all others are applied by it, `plate` and `bogledd` included. Real lines (ran):

```
orden     «kan monterast» HARD BROT · 1 står fast: 3 mellom 1 og 2      (ring + rib + a chord rib crossing that rib)
klem      «ingen står i kvarandre» HARD BROT · 1 par klemmer: 2–3       (ring 3 mm under the hub top: no shoulder on the rib)
gods      «gods i leddet» HARD BROT · 5,0 mm → fiks «del i midten» set {ledd: 0.5} → ok · 12,5 mm      (6 mm plate, ledd 0.2, wall 25)
plate     «delane får plass» HARD BROT · 10 utanfor → fiks «prøv 190 mm» set {storleik: 190}             (sheet 300 × 200)
snittspor «snittet mot sporet» HARD BROT · 4,20 mm mot 4,10 mm → fiks «prøv 2,00 mm»
opning    «opning mellom plan» mjuk BROT · 2,0 mm                        (two rings 6 mm apart, 4 mm plate)
lause     «delar utan ledd» HARD BROT · 1 utan ledd → fiks «kast dei» set {lause: 1} → framleis mjuk · 1 utan ledd
bog       «bøyeradius» mjuk ok · 150,0 mm — rilla, 3,6 mm steg   |   snitt 1.5: HARD BROT · 150,0 mm av minst 600,0 mm → «rett ut til 600 mm»
```

- `orden` for a lamp: one family of parallel rings plus ribs that never meet each other in material goes together (rings first, each rib slides in along its own radial line). Two ribs that cross in material plus a ring is always hard.
- `lause` 1 drops a piece without a joint only when its plane has a joint elsewhere (ran, `kasta.ts`: `lause 1: 2 delar · «utan ledd · kasta» mjuk BROT · 1 kasta`, `lause 0: 3 delar (1a:0 ledd …) HARD`); a plane with no joint at all stays in the cut list (ran, above).

## 2. The slot (code `lib/snitt.ts` 488–840; ran `spor.ts`, `vegg.ts`, `vinkel.ts`, `skraa.ts`, `sete.ts`)

- **Width, nominal** = (tjukn + klaring) / sin θ, θ = angle between the two planes. Under 5° no joint is tried. Ran: 90° 3.10 · 60° 3.58 · 45° 4.38 · 30° 6.20 · 6° 29.67 · 4° 0 joints.
- **Width, in the file** = nominal − snitt (outline pushed out snitt/2, holes pulled in snitt/2). `snittveg` 1 or `snitt` 0 writes the nominal. Ran, 150 mm cube:
  ```
  t3 k0.10 s0.20 i fila      nominell 3.100 | i fila 2.900 · del 150.200 x 150.200
  t3 k0.10 s0.20 i maskina   nominell 3.100 | i fila 3.100 · del 150.000 x 150.000
  t4 k0.10 s0.15             nominell 4.100 | i fila 3.950      t2 k0.15 s0.30   nominell 2.150 | i fila 1.850
  ```
- **Depth**: the run [lo, hi] where both plates have material on the crossing line is split at lo + `ledd`·(hi − lo); one plate is slotted from hi, the other from lo. `deling: "1-2-0:0.7"` sets one joint (planes 1–2, crossing 0), range 0.2–0.8. Ran: `ledd` 0.3 → 104.2 / 44.2 of 150; `deling 1-2-0:0.7` → 44.2 / 104.2. Mouths flare about one cell.
- **A joint becomes a slot when** the run ≥ max(2, tjukn) **and** each plate has material across the slot at its mid-depth over ± (w/2 + min(6, max(2, tjukn/2))), i.e. a strip of w + 4 mm (t ≤ 4), w + tjukn (t 4–12), w + 12 above. Ran (rib 120 × H): t3 H 6.9 rejected, 7.3 cut (limit 7.1); t4 H 8 rejected, 8.9 cut (limit 8.1).
- **Too short a run** is skipped without being counted; **too little shoulder** counts as `avviste`. Either way, if both plates still share > 1 mm of material on the line, `klem` is hard. Ran: t3, wall 1.9 and 2.9 → `HARD klem=1 par klemmer: 1–2`.
- **gods** = material between the slot bottom and the far edge along the slot line, ≥ max(2, tjukn). At `ledd` 0.5 the overlap (a shell's wall) must be ≥ 2·max(2, tjukn). Ran: t3 wall 5.9 `HARD gods=2,9 mm`, 6.1 ok; t4 7.9 / 8.1; t1.5 3.9 / 4.1.
- **Smallest piece kept**: 400 mm² net of holes and slots (`MIN_AREA`); smaller pieces vanish with no rule (their joints can still be counted). Ran: t3, 4 × 100 mm rib → `1 delar · 2 ledd`.
- **Smallest feature seen**: about one cell (storleik / 220). Ran at 400 mm: a 1.2 mm wall gives `0 delar`, 1.9 mm survives.
- **Precision at 220 cells** (ran, ring + ribs at 0–90°, 300 mm): walls `breidd 3.10..3.10` at every in-plane angle, bottom centre within 0.15 mm, bottom corners chamfered: `plata stoppar foer botn: i ringen 0.01..1.05 mm` (t3), `0.02..1.40` (t4); at 1200 cells `0.00..0.17`. See recipe 3.
- **Oblique crossings are tight** — my derivation, not a rule: a square-cut plate crossing at θ needs t/sin θ + t/tan θ; the tool cuts (t + klaring)/sin θ. At 60°, 3 mm: needs 5.20, gets 3.58. Keep plate-to-plate crossings at 90° (± 3°) or plan to file.

## 3. Materials, mass, time (code `lib/core.ts`, `lib/rille.ts`; ran `stoff.ts`)

| key | panel name | kg/m³ | unscored bend R ≥ | score row step |
|---|---|---|---|---|
| `graa` | grå (default) | 700 | 100·t | 1.0·t |
| `bjork` | bjørk | 670 | 150·t | 0.9·t |
| `finer` | kryssfinér | 680 | 100·t | 1.0·t |
| `mdf` | mdf | 750 | 200·t | 0.8·t |
| `akryl` | akryl | 1190 | 230·t | 0.8·t |
| `papp` | papp | 220 | 10·t | 2.0·t |

- `material` changes exactly: density (mass), the two bend columns, the colour in GLB/USDZ, file names and the coupon label. It does **not** touch tjukn, klaring, snitt or fart. An unknown key weighs as `finer` and bends as 100·t (ran: `«eik»: masse 0.0908 kg · finer 0.0908 kg`).
- mass = Σ net part area × tjukn × ρ / 1e9 kg. Ran: `bjork … areal 44531 mm2 · masse 0.0895 kg (areal*t*rho/1e9 = 0.0895)`.
- time = cut length / `fart` (default 20 mm/s), nothing else: no travel, no engraving, no pierce, no material table. Cut length = nominal outlines + holes + score lines. Ran: `kutt 1497 mm · tid 74.9 s ved 20 mm/s`, `fart 8: tid 187.2 s`.

## 4. Bending (code `lib/rille.ts`, `lib/plan.ts`; ran `stoff.ts`, `posar.ts`)

- A plane's `bog` is size / radius: R = storleik / |bog|, |bog| ≤ 4 (ran: `bog 10 skrive og lese attende: 4 → ved storleik 300 er R = 75 mm`). So the tightest bend is storleik / 4.
- At R ≥ factor·tjukn the sheet is left solid; below, it is scored and the rule stays soft:

| | solid down to R | rows every | cut / bridge | hard when snitt ≥ |
|---|---|---|---|---|
| birch 3 | 450 | 2.7 | 36 / 3 | 0.90 |
| birch 4 | 600 | 3.6 | 48 / 4 | 1.20 |
| `finer` 3 / 4 | 300 / 400 | 3.0 / 4.0 | 36 / 3 · 48 / 4 | 1.00 / 1.33 |
| acrylic 3 | 690 | 2.4 | 36 / 3 | 0.80 |
| cardboard 2 | 20 | 4.0 | 24 / 2 | 1.33 |

- Layout (code + ran): open cut lines along the cylinder axis, length 12·t, bridge t, every other row shifted half a period, t kept clear at every edge, nothing within 3·t of a slot line (ran: nearest score 10.0 mm at t3, 12.7 at t4). Lines are written un-offset, before the outline.
- Cost (ran, 300 mm part, R 200): `bjork t3: 825 riller i 110 rader · steg 2.70 · kutt 32.17 m mot 4.79 m flatt`; `finer t4: 390 riller · 21.82 m`; `akryl t3: 937 riller · 35.88 m`; `papp t2: «200,0 mm av minst 20,0 mm» · 0 riller`.
- The coupon tests the one guessed number, the row step. Whether the bridges survive is not computed (README). The README text says plywood 100·t; the code says birch 150·t.

## 5. Sheets (code `lib/pack.ts`, `lib/bygg.ts`; ran `ark.ts`)

- Default 600 × 400 mm; range 100–3000 × 100–2000. Gap parameter = max(4, 2·snitt + 2) mm. Four rotations in 90° steps; grain is not considered.
- Largest part and edge strip (ran):
  ```
  ark 600 x 400 snitt 0.2: luke 4 · rom 593.3 x 393.3      ark 1220 x 610: rom 1208.0 x 596.0
  ark 800 x 450:           rom 793.3 x 442.7                ark 600 x 400 snitt 3: luke 8 · rom 586.7 x 386.7
  kube S paa 600 x 400:  S 393 ok · S 394 BROT · 2 utanfor · fiks «prøv 385 mm»
  ```
- Read back from the DXF (lamp, 600 × 400): first cut 2.6 mm from the sheet edge; smallest distance between two outer contours 5.95–7.17 mm (5.83 on 800 × 450, 8.80 on 1220 × 610).
- A part larger than the room: hard `plate` «N utanfor», the part stays in `MOTOR.liste` with `ark: 0` and is in **no** cut file. Ran: `lampe 300 x 200: 11 delar · 1 ark · utanfor 10` and `ark-nummer 1:0 2:0 3:1 4a:0 …`. Raise `arkB/arkH` yourself.
- Two or more sheets: `exportFile(bag, "dxf")` returns a zip; `skrivKuttfiler` writes one file per sheet.
- `utnytting` is measured against the used strip of each sheet, and shell rings waste it: 25–29 % on the lamp.

## 6. The bags: what is the tool's and what is mine

The tool's own numbers: defaults tjukn 3, klaring 0.10, snitt 0.20, snittveg 0, fart 20; the `klaring` window 0.05–0.35 with the rule's reason (under 0.05 needs a hammer and plywood splinters, over 0.35 does not hold); `tjukn` is the measured plate ("3 mm MDF measures 2.8–2.9"); "cut the fit-test coupon first: klaring and snitt are two guesses that multiply in every joint"; densities and bend factors.

| bag | tool's | my judgement |
|---|---|---|
| 3 mm birch | klaring 0.10 (default and the rule's own fix), `bjork` 670 kg/m³, solid bend ≥ 450 mm | snitt 0.15 for a focused CO2 beam in thin birch; fart 15 |
| 4 mm poplar | klaring 0.10, snitt 0.20 (default) | no poplar in the table: `finer` (680) reads the mass about a third high for poplar (≈ 450); fart 15 |
| 3 mm acrylic | snitt 0.20 (default), `akryl` 1190, solid bend ≥ 690 mm so keep every plane flat | klaring 0.15: acrylic does not crush and cracks at a forced slot, cast sheet varies ± 0.3 mm; write files at 1200 cells; fart 10 |
| 2 mm cardboard | `papp` 220, solid bend ≥ 20 mm, klaring 0.05 is the lowest the soft rule passes | klaring at that floor because board compresses; snitt 0.30 for a wide burn; fart 50 |

Design numbers that follow from the code for each bag (ran, `posar.ts`):

```
bjork3:  minste overlapp for spor 3.0 · vegg for gods ved ledd 0.5 >= 6.0 · gods tvers over sporet >= 7.10 · planavstand >= 6.0 · luke paa arket 4
poppel4: minste overlapp 4.0 · vegg >= 8.0 · tvers over sporet >= 8.10 · planavstand >= 7.0
akryl3:  minste overlapp 3.0 · vegg >= 6.0 · tvers over sporet >= 7.15 · planavstand >= 6.0
papp2:   minste overlapp 2.0 · vegg >= 4.0 · tvers over sporet >= 6.05 · planavstand >= 5.0
```

A 2 mm mock-up of a 3 mm design uses the same `plan` string; only the slots change. Read the rules again at the production thickness.

## Limits

- Nothing here was cut. Kerf, clearance and speed per material are guesses until the fit coupon is cut on the real machine and plate.
- "sete" is geometry on the polygon, not a measured fit; a laser's own corner radius and crushing reduce it in wood.
- Recipe 3 bypasses `MOTOR.exportFile`; pinned sheet positions (`fest`) and the rules were not tested at other cell counts beyond the lamp above.
- `klem` looks only at flat plates, and bent parts are exempt from `orden` (code); neither was run on a bent lamp part here.
- The plan-side recipes (bent planes, tenons, outlines) are another scout's; only their rule thresholds are covered here.
