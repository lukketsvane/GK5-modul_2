# prov.md — the toolkit used by a first user and checked by a sceptic

Ran 2026-11-17. Repo `/home/user/slicer.iverfinne.no` untouched (`git status --short`: 0 lines after everything). Nothing was cut on a machine.
`V = /tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/verkty` · `K = V/../kart/prov` · manual: `V/LES.md` (corrected here).

Verdict: the toolkit does what its report says, and its numbers survive an independent read-back. Following the manual alone I got a lamp that passed every hard rule and every check, and whose lampholder plate was cut almost in three. That hole is now closed by a check; four more things were fixed; section 5 lists what is still wrong.

## 1. Recipes (all ran; output pasted)

**A new concept, start to finish** (`V/prov/mi/konsept.ts`, table lamp `rist`: squircle `loft` with a lid, 4 rings, 4 slats, lampholder on a bridge in ring 1, pp sleeve as `ekstra`):

```bash
cd /home/user/slicer.iverfinne.no
npx tsx $V/lag.ts $V/prov/mi --rask; echo $?     # iterate
npx tsx $V/lag.ts $V/prov/mi --step              # everything
```
```
rist — 219 x 219 x 300 mm · bjork 4 mm · klaring 0.1 · snitt 0.2 · ALT OK
harde    grip ok · delar ok · orden ok · klem ok · gods ok · plate ok · snittspor ok
tal      8 delar · 22 ledd · 0 lause · 3 ark · 12.23 m · 0.474 kg · mjuke: utnytting 33 %
krav     18 av 18 ok
fin      produksjon/fin/: 1200 celler · 8 delar · 3 ark · 12.31 m · same tal på delar, ledd og ark som ved 220 · same delar på kvart ark
step     … 9 solid · 9 gyldige · overlapp 19 par testa · 14 med volum · sum 2.059 mm3 · størst 0.213 mm3
```

The three lines of it that matter for a designer:

```ts
...ringar(k, 1, [70], { strek: [rektStrek(k, "gods", 80, 180, 0, 0), rundt(k, "hol", 40.4, 0, 0)] }),   // bridge, not a full fill
...ringar(k, 2, [130, 190, 250]),
...lameller(k, 10, "x", [-95, -46, 46, 95]),      // planes x = …; the inner two are arches over the bulb
```

**Read the outputs back without the toolkit** (`<ut>` = a concept's `ut/` folder after a `--step` run; from `K`):

```bash
python3 dxfsjekk.py <ut>      # both DXF sets: layers, closed outlines, parts per sheet against the list, order, inside the sheet
python3 glbsjekk.py <ut>      # samla.glb and flat.glb: nodes, names, triangles
python3 leddsjekk.py <ut>     # rigid matrices; every crossing pair: who has material where, slot widths in JSON and in the DXF, overlap
$V/../forge/venv/bin/python -I stepsjekk.py <ut>   # STEP: solids, validity, volume against outline area x thickness
```
```
produksjon/fin/ark-1.dxf lag {'GRAVER': 12, 'KUTT': 8} andre einingar [] · KUTT 8 (8 lukka, 0 opne = riller mot 0 i lista, minst 44 punkt) · ytre 4 mot 4 delar i lista True · hol 4 mot 4 · GRAVER 12 (0 lukka) · boks 2.57,2.57..596.10,394.77 i 600x400 True · graver fyrst True · hol før omriss True
samla.glb: glTF v2 197380 B · 9 nodar, 8 med nett, 8 nett · 8 delar i lista · namna er adressene True · 5392 trekantar
matriser: 8 delar · største avvik frå ortonormal/det +1/siste rad 0.00e+00
  2-11  vinkel 90.0 · møte 2 · gods i 2: [-108.6,-94.6] [80.6,94.5] · i 11: [-94.5,-80.6] [94.6,108.6] · begge 0.00 mm · spor i 2: [-94.5,-80.6] 4.10 [94.6,108.6] 4.10 · spor i 11: [-108.6,-94.6] 4.15 [80.6,94.5] 4.15 · overlapp 0.198 mm3
sum: 14 par · 22 møte (rapport 22 ledd) · midtliner i begge 0.00 mm · overlapp 1.975 mm3 · spor i delar.json 4.10..4.15 mm (ventar tjukn+klaring 4.10) · spor i DXF 3.90..3.90 mm (0 ikkje funne av 44; ventar 3.90)
STEP rist.step: 9 produkt med form · 9 solid · 9 gyldige · venta 9 delar
           1 solid 1 gyldig True volum   111828.6 mm3 · areal x tjukn 111828.6 · avvik -0.000 % · boks [-104.0, -104.0, 68.0, 104.0, 104.0, 72.0]
    diffusor solid 1 gyldig True volum    26279.7 mm3 · areal x tjukn 26263.7 · avvik +0.061 % (bøygd)
sum: flate delar verste volumavvik 0.0000 % · manglar [] · ukjende []
```

`leddsjekk.py` walks the line where two mid-planes meet in 0.1 mm steps and asks each plate's outline for material on it and 2.6 mm to each side. The 4.15 is its 0.05 mm step: the slot walls in slat 11 sit at z 127.94 and 132.04, 4.10 apart. Its overlap figure is an upper bound (section 2).

**The project file in the app** (built app, Chromium 390 × 844 touch; harness from the `ut` scout):

```bash
mkdir -p $K/opne && cp <ut>/produksjon/rist.zip <ut>/produksjon/ark-*.dxf $K/opne/
cd /home/user/slicer.iverfinne.no && (npx next start -p 3210 > /dev/null 2>&1 &) ; sleep 6
npx tsx $V/../kart/utprov/opne.ts $K/opne rist.zip
```
```
etter  prosjekt «rist» · kjelde f1ejrlo93wt0 · storleik 300 · tjukn 4 · material bjork · scene «»
plan   likt det som vart skrive: «1@0.5,0.5,0.2333/0,0,1/+r:0,0,0.2667,0.6,0/-o:0,0,0.1347,0.1…»
nyklar 26 skrivne · ulike etter opning: kjelde "rist" -> "f1ejrlo93wt0"
       slicer-rist-4mm-bjork-k0p2-ark-1av3.dxf 31568 B sha 85bd50c1b837 · hovudlaus ark-1.dxf 31568 B sha 85bd50c1b837 · LIKE   (also sheets 2 and 3)
omlast prosjekt «rist» · kjelde f1ejrlo93wt0 · plan likt
konsoll ingen feil
```

Stop the server by its own pid or port. `pkill -f next-server` kills every agent's server: another agent had one on :3230 here, started three minutes after I had used it.

**Timings** (seconds, lag.ts's own clock, 4 CPUs shared with another agent; wall time is 1 s more):

| | rist | ribber | lykt | skjerm |
|---|---|---|---|---|
| `--rask` | 17.1 · 14.8 · 25.6 · 25.4 | 21.9 | 28.2 | 16.0 |
| `--step` | 140.0 · 157.0 · 146.3 | 131.9 · 136.9 | 217.0 | 149.1 |
| no flag | 117.6 | | | |

`rist --step`, last run: ark 15.2 · produksjon 1.6 · bilete 97.4 · step 31.7. The large views are two thirds of a full run; `lykt` spent 168 s on them once.

## 2. What was checked, and what came out

| check (my own reader, not the toolkit's) | rist | ribber | lykt | skjerm |
|---|---|---|---|---|
| DXF 220 and `fin/`: only layers KUTT and GRAVER, only POLYLINE, units mm, extents = the bag's sheet | 600 × 400 | 600 × 400 | 600 × 400 | 800 × 450 |
| every KUTT outline closed; open ones are exactly the score cuts | 14 closed | 22 closed | 34 closed | 17 closed + 515 open = 515 `rille` |
| outer outlines per sheet = parts on that sheet in the part data; holes = holes in the part data | 4/2/2, 4/0/2 | 4/6/9, 2/1/0 | 4/3, 25/2 | 1/2, 0/14 |
| engraving before cuts, holes before their outline, everything inside the sheet | yes | yes | yes | yes |
| part matrices orthonormal, det +1 (worst deviation) | 0 | 3.3e-16 | 0 | 0 |
| crossing pairs · meetings found · joints in the report | 14 · 22 · 22 | 48 · 48 · 48 | fingers and tenons: see below | bent part: not covered |
| length where both plates have material on the meeting line | 0.00 mm | 0.00 mm | 0.80 mm | — |
| slot width in `fin/delar.json` (expect 4.10) | 4.10–4.15 | 4.05–4.15 | 4.10 | — |
| slot width in the `fin/` DXF (expect 4.10 − 0.20 = 3.90) | 3.90 | 3.85–3.95 | 3.90 | — |
| overlap volume, sampled · toolkit's exact boolean | 1.98 · 2.06 mm³ | 2.77 · 5.57 | 12.5 · 1.11 | — · 1.37 |
| `samla.glb`: mesh nodes = parts, named by address | 8 = 8 | 19 = 19 | 7 = 7 | 3 = 3 |
| STEP: solids = parts, all valid | 9 | 19 | 7 | 3 |
| STEP volume against outline area × thickness, flat parts | 0.0000 % | 0.0000 % | 0.0000 % | 0.0000 % |
| same, bent parts (strips) | +0.061 % | | | −0.266 % |
| project zip opens in the app, bag equal, DXF byte-identical, survives reload | yes | not run | not run | not run |

- Slot widths carry ±0.05 mm from the sampling step; on `ribber` the ribs lie at angles on the sheet.
- `lykt`: the 0.80 mm and my 12.5 mm³ are the 0.01 × 4 mm whiskers at the eight three-way corners, each counted 0.1 mm wide by a 0.1 mm step. The toolkit's 1.11 mm³ is the true figure. Its finger pairs are complementary on the line (`gods i 1: [25.6,50.8] … i 2: [4.0,25.4] [51.0,76.3] …`, 0.2 mm apart).
- `samla.glb` is in metres, Y up, one root node `slicer-<id>` plus one node per part.
- Not read back: `deler.3mf`, `samla.usdz`, `alt.zip`, `profilar.svg`, `passprove.svg`, the ForgeCAD pictures' content beyond looking at `rist_iso.png`.

## 3. The lamp that passed and was wrong

First version of the lampholder plate, exactly as the manual's recipe said: `strek: [rundt(k,"gods",196), rundt(k,"hol",40.4)]` on ring 1. Result: `ALT OK`, 15 of 15, every hard rule green, `gods 14,1 mm`. My joint reader said otherwise:

```
  1-11  … møte 1 · gods i 1: [-102.9,-88.9] · i 11: [-88.8,-74.9] [88.9,102.9] · spor i 1: [-88.8,-74.9] 4.10 [88.9,102.9] 4.10 · spor i 11: [-102.9,-88.9] 4.15
sum: 14 par · 20 møte (rapport 22 ledd)
```

Plate 1 has no material on the line x = −46 from y = −88.9 to the far rim: two slits 4.1 × 192 mm, the lampholder on a tongue held by a 14 mm bridge (`K/rist-spalte-ark-1.png`, concept `K/rist-spalte-konsept.ts`). Cause, read in `lib/snitt.ts` (`klar`): a slot is opened from its mouth through the whole stretch of material the mouth sits in. An arch crosses a ring on two legs, so one of its two slots opens inward; fill the ring and that slot runs to the other side. The engine's own slot record still says 14 mm (`1-11-0 munn -74.8 botn -88.9`), and the part's `ledd` drops from 6 to 4.

Fixed design: fill only a bridge between the slats (80 wide between slats at ±46). Fixed toolkit: section 4.

Two more things the same lamp showed:
- A fill that does not reach the ring (ø150 in a 153 mm cavity) is thrown away as loose, but its ø40.4 hole stays in part 1. `holKrav` reported `ok … senter 0, 0, 70` for a hole in thin air.
- `montering.txt` says of the arches `sidelengs, langs (0,00, -1,00, 0,00), mot 2, 1, 3, 4`. Worked out from the measured intervals above, not simulated: pushed straight in, the far leg's material [-94.5,-80.6] meets ring 2's near band [80.6,94.5] between 161 and 189 mm before its seat. The arch has to be lowered over the rings, one leg inside them and one outside, at least 59 mm off its seat (ring 2's outer edge 108.6 against the cavity radius 50 at the feet), then slid home. Nothing in the engine or the toolkit checks a travel path.

## 4. What I changed in `V` (originals in `K/*.for`)

| file | change | evidence |
|---|---|---|
| `lag.ts` | built-in check 11, `ingen spalte held fram gjennom gods forbi munnen`: for every engine slot record, walks on past the mouth and adds up the length where the line is cut but both sides (w/2 + 1.5 mm out) are material and no other slot record lies there; fails over 5 mm | broken `rist`: `BROT … del 1 spor 1-11-0: 177 mm · del 1 spor 1-12-0: 177 mm`, exit 1; fixed `rist`, `ribber`, `lykt`, `skjerm`: `ja` |
| `lag.ts`, `typar.ts` | `x.hol()` returns `iLuft`; `holKrav` fails when the hole lies inside another hole of the part | `BROT hol ø40.4 i del 1: ø40.24 ligg i eit anna hol i delen …` |
| `syn-side.js` | `front`, `side`, `topp` through a 6° lens instead of 24°: front and back of a 220 mm deep lamp differed 29 % in size, now 6 % | `rist`: slats evenly spaced, rings as lines |
| `syn-side.js` | a table cord no longer counts when `front side topp under` are framed | `lykt` side view is the size of its front view again; `rist` under view fills the tile |
| `syn-side.js` | 100 mm scale bar under the three elevations on `ark.png` | `rist` front, read off the picture: bar about 150 px, the 219 mm lamp about 330 px |
| `syn-side.js`, `lag.ts`, `syn.ts` | footer counts engine parts and `ekstra` apart | `8 delar + 1 ekstra` |
| `skriv.ts`, `lag.ts` | the `fin` line says whether the 1200-cell sheets hold the same parts as the report's `ark` list, and lists them when not | `ribber`: `DELANE LIGG PÅ ANDRE ARK ENN LISTA OVER: fin/ark-1: 3 1 16 18 · fin/ark-2: 2 20 22 10 12 14 · …` |

After the changes: all three examples and `rist` rerun with `--step`, exit 0 (17/17, 16/16, 16/16, 18/18); `lykt` and `skjerm` were last run before the `fin` line was reworded, so their reports carry the old wording. `V/prov/kokebok.ts` rerun: `alle oppskriftene held`, 4.3 s.

What the manual had wrong, missing or unclear, all corrected in `V/LES.md`:
- Wrong: the lampholder recipe (no condition on the fill); "ten built-in checks"; `--rask` 12–17 s (15–28 s here); `fin/` "same sheets"; `brot` names five failed checks, not six (rerun: exit 1, `krav 9 av 14 ok`).
- Missing: the run with no flag; exit code through a pipe; what `"x"` means in `lameller`; that `ringar`'s `extra` goes on every ring; `loft`'s `lok` and `hol` (a diameter: measured r 28 for `hol: 56`); `superRing`'s exponent; that `rutenett` takes no `k`; a standing bulb and a table cord (I had to open `kart/syn.md`); that z = 0 is the table.
- Unclear: the `ledd` column (the engine's slot count); a `front` view labelled in mm that was a 24° perspective.
- Added as traps: the slit, the island, the arch's travel, a plane grazing a cavity wall (`klem` on 4 pairs with slats at x = ±76 and the cavity edge at 76.2–76.6).
- `plan.ts` also exports `tangent(k, id0, N, r, fase)`; it is not in the manual and I did not run it.

## 5. The pictures

Read: `ark.png` of `rist`, `ribber`, `lykt`, `skjerm`, and the large `rist-helt`, `rist-lys`, `rist-sprengt`, `lykt-lys`, `ribber-front`.

- A designer can judge a form by them. Plates have thickness, burnt edges and grain; slots, fingers and score cuts are the real cut geometry; the diffuser sleeve and bulb read as what they are.
- `lys` is believable and honest: `skjerm` (4 mm scored birch) is a dark drum with light from the seam and below; `lykt` throws its slits on the table; `rist` shows the closed side slats as dark panels. Weak points: an `ekstra` diffuser burns out to flat white with a dotted edge, unlit outer faces go nearly black, and the lamp fills a third of the frame.
- `sprengt` is the engine's order, so slats travel in their own plane and stay threaded through the rings, and parts that "lie" (the rings) are not pulled apart. Give your own `steg` for a presentation picture.
- The large views carry no label and no scale; only `ark.png` does.

## 6. Still wrong, or not known

- The slit check is a heuristic on the 220-cell outline with fixed margins (1.5 mm to the side, 5 mm threshold). It was seen to fire once and to stay quiet on four lamps; nothing else.
- No check that a part can reach its seat. The arch above is the proof that `orden ok` is not enough.
- A slat running along a ring's band gets an honest half-lap that is long: `rist` rings carry 77–89 mm slits, 4.1 wide, in a 28 mm band. No rule or check speaks about it.
- `iLuft` only sees a hole inside another hole. Whether the island's hole also reaches the DXF was not looked at (that case was only run with `--rask`).
- `fin/` is nested on its own: on `ribber` 9 of 19 parts lie on another sheet than the report's `ark` list says. The report now prints it; `montering.txt`, `deler.csv` and the sheet PNGs still describe the 220 nesting.
- The elevations are still a perspective (6 % front to back on `rist`); the scale bar is true at the lamp's middle depth.
- A curved edge is cut as the mesh's facets: on `rist` ring 2 the corners of the 96-sided mesh section lie a median 0.03 mm from the `fin/` outline (0.14 mm at 220 cells). More ring points were not tried.
- The STEP is all planes (`1894 flater (1894 plan, 0 sylinder)` on `rist`): the ø40.4 hole is a 29-sided polygon, outlines are polylines.
- My own readers: `leddsjekk.py` covers flat plates crossing at slots; it does not judge tenons, mortises or bent parts, and its overlap is an upper bound.
- Not run by me: a laser, a phone, `--stor`, a body over 600 mm, the project zip of the three examples in the app.

## 7. Files

- `V/prov/mi/konsept.ts`, `V/prov/mi/ut/` — the final `rist`, full run.
- `K/dxfsjekk.py`, `glbsjekk.py`, `leddsjekk.py`, `stepsjekk.py`, `spor.ts` (prints the engine's slot records per part).
- `K/rist-sjekk.txt`, `ribber-sjekk.txt`, `ribber-ledd.txt`, `lykt-sjekk.txt`, `lykt-ledd.txt`, `skjerm-sjekk.txt` — the read-backs (the example `-sjekk` files hold the first, coarser overlap sampling; `-ledd` the final one).
- `K/rist-spalte-konsept.ts`, `rist-spalte-ark-1.png`, `rist-spalte-ledd.txt`, `rist-spalte-rapport-rask.txt` — the slit plate.
- `K/opne/opne.log`, `K/opne/opna-i-appen.png` — the project in the app.
- `K/*-ark-for.png`, `K/*-rapport-for.txt` — the examples before my changes; `K/*.for` — the toolkit files before my changes.
- `K/mi-full-*.log`, `ribber-full*.log`, `lykt-full.log`, `skjerm-full.log`, `utanflagg.log` — timed runs.
