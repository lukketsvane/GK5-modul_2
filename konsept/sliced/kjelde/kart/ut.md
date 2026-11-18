# ut.md — everything that leaves the tool, headless, and proven to read back

All of it was run on 2026-11-17 against `/home/user/slicer.iverfinne.no` (read-only, `git status` still empty). Lines marked "read" come from code only.
`K = /tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/kart`
Run anything as `cd /home/user/slicer.iverfinne.no && npx tsx <absolute path>.ts`. Read `K/motor.md` first (body, frame, bag).
Files: `K/skriv.ts` (the two functions), `K/utprov/*.ts` (every experiment quoted here), `K/ut/lampeb/` and `K/ut/ror/` (written output).

## Recipe 1 — one call writes every production file

```ts
import { skrivAlt, delData } from "<K>/skriv"
const man = await skrivAlt(bag, [{ id: "lampeb", pos }], "/abs/folder", "lampe-b")   // bag: ParamBag, pos: Float32Array soup (mm, Z up)
```

- `nett[].id` must be `[a-z0-9]{1,40}` and equal `bag.kjelde` (it throws otherwise, see traps). Pass `[]` if the mesh is already registered WITH bytes.
- 4th argument names the project file, and that file name becomes the project's name on the phone.
- Returns the manifest (also written as `manifest.json`): `ok` (no hard rule broken), `tal`, `harde[]`, `mjuke[]`, `ark[]`, `delar[]`, `filer[]`.

Real output, sample dome from `K/minimal.ts` (`K/utprov/kjor.ts`, 2.4 s in all, 1.5 s of it the one 1200-cell build):

```
lampe-b: 7 plan · 11 delar (9 unike) · 24 ledd · 2 ark · utnytting 25 % · kutt 10.47 m · graver 573 mm · 8.7 min · 0.295 kg · 2454 ms
harde brot: 0 · mjuke: utnytting 25 %
ark 1: 1 2 4b 5a 3 · utnytting 27 % av brukt hogd, 26 % av heile arket · graver 205 mm · umerkte - · inni holet til ein annan: 3
ark 2: 6a 7a 5b 6b 7b 4a · utnytting 23 % av brukt hogd, 20 % av heile arket · graver 368 mm · umerkte - · inni holet til ein annan: -
  file             bytes    cells
  ark-1.dxf        43790    220   cut file, R12 ASCII, mm, layers KUTT + GRAVER, kerf taken      (ark-2.dxf 33446)
  ark-1.svg        12261    220   cut file 1:1, black = engrave, blue = cut, kerf taken          (ark-2.svg 10000)
  ark-1.png       178576    220   picture of the sheet, 2400 x 1600 px, not for the machine      (ark-2.png 136979)
  profilar.svg     22309    220   every profile side by side, 1:1
  samla.glb       272064   1200   assembled, metres, Y up, one node per part
  flat.glb        162832    220   parts flat as nested, one group per sheet
  deler.3mf       463949   1200   flat parts, one object per part, mm, Z up
  samla.stl       371884   1200   assembled, one triangle soup, mm, Z up
  samla.usdz      684525   1200   assembled, AR Quick Look
  passprove.svg    10763     -    fit-test coupon (bogprove.svg too, only when a plane is bent)
  alt.zip         357401    220   the ALT bundle exactly as the app downloads it
  montering.txt      775    220   assembly order, part by part, with direction      (taken out of alt.zip)
  deler.csv          467    220   cut list = kuttliste.csv from alt.zip
  reglar.txt         826    220   every rule, hard breaks with their why            (taken out of alt.zip)
  lampe-b.zip    1114594     -    the project file (LAGRE)
  delar.json       50166    220   per part: outline, holes, thickness, matrix; and the order (recipe 3)
```

## Recipe 2 — read it back (`K/utprov/les.ts [folder]`, exit 1 on any failure)

```
ark-1.dxf: lag GRAVER,KUTT · $INSUNITS 4 · EXTMAX 600 x 400 · 776 entitetar · POLYLINE GRAVER 11, KUTT 8 · 5 ytre + 3 hol · 1 del(ar) ligg inni holet til ein annan · kutt 5812 mm · graver 205 mm · boks 2.6,2.6,592.1,380.1
ark-1.svg: 600.00 x 400.00 mm · viewBox 0 0 600.00 400.00 · 19 stiar: 11 svarte (graver), 8 blaa (kutt), 0 andre · fyll nei | ark-1.png: 2400 x 1600 px · 3 kanalar
ark-2.dxf: lag GRAVER,KUTT · $INSUNITS 4 · EXTMAX 600 x 400 · 592 entitetar · POLYLINE GRAVER 18, KUTT 6 · 6 ytre + 0 hol · kutt 4662 mm · graver 368 mm · boks 4.1,2.6,597.4,348.1
ark-2.svg: 600.00 x 400.00 mm · 24 stiar: 18 svarte (graver), 6 blaa (kutt), 0 andre · fyll nei | ark-2.png: 2400 x 1600 px
DXF samla: kutt 10473 mm (nominelt 10465) · graver 573 mm (manifest 573) · 11 av 11 omriss funne att fraa delar.json
DXF-omriss mot delar.json: arealet avvik hogst 0.98 % (snittet 0,2 mm ligg i fila)
samla.glb: 12 nodar = 11 delar + 1 gruppe (slicer-lampeb) · namn 1 2 3 4a 4b 5a 5b 6a 6b 7a 7b · matrise paa nodane: nei · 7436 trekantar
delar.json (220) gjennom matrisa mot boksane i samla.glb (1200), flate delar: verste avvik 0.134 mm
flat.glb: 11 delar i 2 grupper: ark-1 [1 2 4b 5a 3] · ark-2 [6a 7a 5b 6b 7b 4a]
deler.3mf: [Content_Types].xml, _rels/.rels, 3D/3dmodel.model · 11 objekt: 1 2 4b 5a 3 6a 7a 4a 5b 6b 7b · eining millimeter · 7400 trekantar
samla.stl: 7436 trekantar · boks -150.0,-150.0,0.0 .. 150.0,150.0,297.2
samla.usdz: slicerman.usda 684379 B
alt.zip: 11 filer: slicer-lampeb.stl 220684 · slicer-lampeb-4mm-bjork-k0p2-ark-1av2.dxf 43790 · …-ark-2av2.dxf 33446 · slicer-lampeb-profilar.svg 22309
         · …-ark-1av2.svg 12261 · …-ark-2av2.svg 10000 · passprove-4mm-bjork.svg 10763 · kuttliste.csv 467 · montering.txt 775 · reglar.txt 826 · oppsett.json 666
lampe-b.zip: oppsett.json 666 B, nett/lampeb__lampeb.stl 1113684 B · reiskap slicer.iverfinne, utgåve 2, kjelde lampeb.stl, 26 nyklar i p · nettet les som 22272 trekantar
alt les attende utan feil
```

GLB: the node count is parts + 1 (one group node that is the assembly); mesh nodes = parts, named by the engraved address.
DXF checks are the ones `scripts/rekkje.ts` makes: only POLYLINE/VERTEX/SEQEND, layers GRAVER and KUTT, engraving before any cut, inner cuts before outlines, everything inside `$EXTMAX`, one outline per part.

## Recipe 3 — per-part data for a CAD assembly and an exploded view

```ts
const d = delData(bag, [{ id: "lampeb", pos }])      // plain JSON; skrivAlt writes the same thing as delar.json
```

```
d = { eining: "mm", detalj: 220, tjukn: 4, boks: { min, max }, delar: [...], orden: [...], lause: [] }
d.delar[3] = {"adr":"4a","form":"D04","plan":4,"ark":2,"tjukn":4,"omriss":[[-50.42,282.06],[-38.16,282.06],…],"hol":[],"rille":[],
  "areal":7921.2,"masseKg":0.0212,"kuttMm":775.3,"ledd":3,"matrise":[0,1,0,0, 0,0,1,0, 1,0,0,0, -2,0,0,1],"stabel":[16 numbers],
  "paaArk":[0,1,293.33,-1,0,198.08],"normal":[1,0,0],"krumming":0,"steg":2,"veg":"side","retning":[0,-1,0]}
d.orden[3] = {"nr":4,"plan":4,"delar":["4a","4b"],"steg":2,"veg":"side","retning":[0,-1,0],"mot":[1,2,3],"fast":false}
```

- `omriss` is counter-clockwise, every `hol` clockwise, mm, nominal (no kerf), slots and tenons already in it; `areal` is net of holes (ring 1: 69101 − 48088 = 21013). It is the cut profile at 220 cells — the same polygon the DXF carries, before the kerf offset.
- The 2D frame belongs to the PLANE, not the piece: `4a` and `4b` share one matrix (4a spans x −149.9..−20.0, y 0..297.1).
- `matrise`: 4×4, column-major (three.js `Matrix4.fromArray`, glTF `matrix`). `[x, y, z] = M·[u, v, w, 1]`, (u, v) from the outline, w from 0 to `tjukn`; result in the body frame: mm, Z up, centred, floor z = 0. The plate is centred on its plane (ring 1: origin z 37.99 for a plane at z 40). To glTF: `(x, z, −y) / 1000`.
- It is a pure rotation: I re-orthonormalise the engine's frame (a normal rounded to 4 decimals, e.g. 0.7071, left det 0.99998). Proof (`K/utprov/matrise.ts`):
  `11 delar · 13236 hjorne i motoren sitt eige nett (lagDelar, 220) · lengste veg til eit hjorne fraa delar.json gjennom matrisa: 1.44e-3 mm`
- `paaArk` `[a,b,c,d,e,f]`: sheet x = a·u + b·v + c, y = d·u + e·v + f (a quarter turn and a shift, never mirrored); sheet origin lower-left, y up. All 11 outlines were found again in the DXF this way. `ark` is 1-based; 0 = did not fit on any sheet.
- `stabel`: the montage's flat pose (sheets stacked under the body, 3 × tjukn apart) — for a plate-to-body animation.
- `orden` is the engine's own assembly order (`montering.orden`, the one `montering.txt` writes), one entry per PLANE. `retning` is the unit direction the part travels as it comes in, body frame; `null` = `veg: "ligg"` (it lies first, nothing to slide into). `mot` = planes already placed that it joins. `steg` = the montage step (parallel planes go in together). `fast: true` = stuck, hard rule `orden`. `lause` = parts in no joint.
- Exploded view: final pose = `matrise`; exploded pose = the same moved by `−retning × distance` (scale the distance by `nr` or `steg`); `ligg` parts stay.

```
  1  plan 1 [1] steg 1 · ligg · retning - · mot -              5  plan 5 [5a 5b] steg 3 · side · retning -0.707,0.707,0 · mot 1,2,3
  2  plan 2 [2] steg 1 · ligg · retning - · mot -              6  plan 6 [6a 6b] steg 4 · side · retning -1,0,0 · mot 1,2,3
  3  plan 3 [3] steg 1 · ligg · retning - · mot -              7  plan 7 [7a 7b] steg 5 · side · retning -0.707,-0.707,0 · mot 1,2,3
  4  plan 4 [4a 4b] steg 2 · side · retning 0,-1,0 · mot 1,2,3
montering.txt:   4  4 (2 stykke)  sidelengs, langs (0,00, -1,00, 0,00), mot 1, 2, 3
```

Triangles instead of polygons: `MOTOR.montasje(bag).delar[]` = `{ adr, steg, ark, veg, positions (soup in the same flat frame), ferdig, flat, boygd? }`.

**Bent planes** (`krumming` = 1/R ≠ 0; ran R11 from `K/plan.md`, `K/utprov/boygd.ts`): `omriss` is the unrolled pattern (u = arc length, 712 × 244 mm), `rille` holds the score cuts (625, open KUTT polylines in the DXF), and `matrise` only lays the flat pattern tangent to the cylinder — against the GLB it is off by up to 238 mm. For the curved shape take the GLB node, or `MOTOR.montasje(bag).delar[i].boygd` (soup already in the body frame). `bogprove.svg` is then written too.
`ror: ok true · 3 delar · 10 ledd · 1 ark · kutt 36.36 m` · `1 plan 1 · krumming R 120.0 · 712 x 244 mm · 625 riller · steg 1 ligg` · `2 [2] opp 0,0,1 mot 1` · `3 [3] ned 0,0,-1 mot 1`

## Recipe 4 — the project file, and proof that the app opens it

Format (what `MOTOR.exportFile(bag, "prosjekt")` writes; `skrivAlt` saves it as `<namn>.zip`):

```
<namn>.zip                     STORED zip, no compression — a deflated one is refused: `«oppsett.json» er komprimert, og det les ikkje denne` (ran lib/zip unzip)
  oppsett.json                 {"reiskap":"slicer.iverfinne","utgåve":2,"kjelde":"lampeb.stl","p":{ …the whole bag, 26 keys, plan included… }}
  nett/<id>__<label>           the mesh bytes exactly as given to put(id, label, soup, bytes) — here binary STL, mm, Z up
```

Headless: register the mesh WITH its bytes (`put(id, "x.stl", makeSoup(pos), stlBytes(pos))`, which `skrivAlt` and `form.ts registrer` do), then export. Without bytes (ran): `slicer-utanbytes-oppsett.zip · nettet er for stort til å leggjast ved: utanbytes.stl · inni: oppsett.json` — settings only, and the app would put them on the cube (read). `skrivAlt` throws before writing anything: `prosjektfila ville ikkje bere nettet «utanbytes»: registrer det med bytes`.

What the app does with it (read in `lib/worker.ts`, `components/studio.tsx`; then run): zip magic → `oppsett.json`.p becomes the bag → every `nett/*` is parsed by its extension and registered under a hash id `f…` → the first one becomes `kjelde` → `MOTOR.clamp` → a NEW project named after the zip file. On the phone: tap the body name in the top line → `fil` → pick the zip (same input as STL/GLB).

Proof (`K/utprov/opne.ts`; built app on :3210, Playwright 390×844 isMobile hasTouch, file given to the app's own `input[type=file]`, bag read back with `posen`, then the app's own DXF export downloaded and compared):

```
fyrr   prosjekt «prosjekt 1» · kjelde kube · plan «»
etter  prosjekt «lampe-b» · kjelde fi5vfplnvbo · storleik 300 · tjukn 4 · material bjork · scene «»
plan   likt det som vart skrive: «1@0.5,0.5,0.1345/0,0,1;2@0.5,0.5,0.5382/0,0,1;3@0.5,0.5,0.94…»
nyklar 26 skrivne · ulike etter opning: kjelde "lampeb" -> "fi5vfplnvbo"
appen  dxf -> slicer-lampeb-4mm-bjork-k0p2-dxf-2plater.zip (77574 B)
       …-ark-1av2.dxf 43790 B sha 8ffa764e0d34 · hovudlaus ark-1.dxf 43790 B sha 8ffa764e0d34 · LIKE
       …-ark-2av2.dxf 33446 B sha 658b7b227ada · hovudlaus ark-2.dxf 33446 B sha 658b7b227ada · LIKE
omlast prosjekt «lampe-b» · kjelde fi5vfplnvbo · plan likt          (survives a reload: it is in the browser's database)
konsoll ingen feil
```

So the phone cuts byte-identical DXF to the headless run. Screenshot: `K/ut/lampeb/opna-i-appen.png`.
Same file with `storleik: 700`, sheet 1200 × 800: `ulike etter opning: kjelde … · storleik 700 -> 600` — the app silently rescales a body over 600 mm; the big sheet is accepted.
To rerun: `cd /home/user/slicer.iverfinne.no && (npx next start -p 3210 > /dev/null 2>&1 &)`, run `opne.ts [folder] [file.zip]`, then `pkill -f next-server`.

## One call per output

`MOTOR.exportFile(bag, kind)` → `{ name, mime, text | data, merknad? }`. stem = `slicer-` + label without extension; plate = `4mm-bjork-k0p2` (`…-maskinsnitt` when `snittveg: 1`). Sizes for the sample (`K/utprov/uttak.ts`).

| kind | name | bytes | cells | what it is |
|---|---|---|---|---|
| `dxf` | 1 sheet: `stem-plate.dxf` (text); n sheets: `stem-plate-dxf-2plater.zip` of `stem-plate-ark-1av2.dxf` … | 77574 | 220 | per sheet directly: `sheetDxf(makeBygg(p, DETAIL.mid).ns, i, kerfOf(p))` |
| `ark` | `stem-plate-ark.svg`, or `stem-plate-ark-2plater.zip` | 22599 | 220 | per sheet: `sheetSvg(ns, i, kerfOf(p))`, or `MOTOR.arkSyn(bag, i).svg` |
| `svg` | `stem-profilar.svg` | 22309 | 220 | all profiles in rows, kerf taken |
| `png` | — | — | — | **not in the engine**: `exportFile(bag, "png")` returns the DXF. The app rasterises the sheet SVG on the main thread; `arkPng(svg, arkB, arkH)` in `skriv.ts` does the same with sharp: min(4, 2400 / longest side) px per mm, white ground |
| `glb` | `stem.glb` | 272064 | 1200 | assembled; 1 group + 1 node per part; geometry baked in metres, Y up — nodes carry no transform |
| `flat` | `stem-4mm-bjork-flat.glb` | 162832 | 220 | groups `ark-1`, `ark-2`; sheet 2 starts 1.1 × arkB along x (ran: x 2.7..592.0 and 664.2..1257.3 mm, up 0..4.00); nominal outline |
| `3mf` | `stem-4mm-delar.3mf` | 463949 | 1200 | one object per part, flat where the nester put it (ran: z 0.00..4.00, x 2.7..1247.9), mm, Z up |
| `stl` | `stem.stl` | 371884 | 1200 | assembled soup (the STL inside ALT is the 220 one, 220684 B) |
| `usdz` | `stem.usdz` | 684525 | 1200 | one `slicerman.usda` inside |
| `prove` | `passprove-4mm-bjork.svg` | 10763 | — | needs only tjukn, snitt, material |
| `bogprove` | `bogprove-4mm-bjork.svg` | 37268 | — | always answers; in ALT only when a plane has `bog` |
| `alt` | `stem-alt.zip` | 357401 | 220 | stl, dxf per sheet, profilar.svg, svg per sheet, passprove, (bogprove), `kuttliste.csv`, `montering.txt`, `reglar.txt`, `oppsett.json` — no GLB, no 3MF, no mesh |
| `prosjekt` | `stem-prosjekt.zip` | 1114594 | — | recipe 4 |

DXF: AC1009, `$INSUNITS 4`, `$EXTMIN/$EXTMAX` = the sheet (no burnable frame), origin lower-left, y up, polylines only (no arcs). Order in the file: engraved addresses → holes and score cuts → outlines. Kerf: outline +snitt/2, holes −snitt/2, so the DXF cut length is 10473 against the nominal 10465. SVG: mm, viewBox = sheet, `#000000` engrave, `#0000ff` cut, nothing filled. Planes with `farge` get their own layer `C02`… / colour (read).
Text only: `montering(p, makeBygg(p, DETAIL.mid).s)` (from `lib/motor`) and `kuttCsv(MOTOR.liste(bag))` (from `lib/core`); `reglar.txt` exists only inside ALT.

## The cut list: where each number comes from

- Per part — `manifest.delar[]` = `MOTOR.liste(bag)`: `adr` (engraved), `id` (shape; equal ids are identical parts), `w × h` mm (box of the outline in its plane frame), `area` mm² (net of holes), `cutLen` mm (nominal, all rings), `joints`, `ark` (1-based), `plan`. Mass per part is `delar.json` `masseKg`.
- Per sheet — `manifest.ark[]`: `delar`, `utnytting` (what the app shows: part area / (used height × sheet width)), `avHeileArket` (part area / whole sheet), `gravMm`, `umerkte` (parts with no room for their address: nothing is engraved on them), `iHol` (parts nested inside another part's hole), and the three file names.
- Totals — `manifest.tal`: `kuttMm` (`Metrics.cutLen`), `tidS` = kuttMm / `fart` (20 mm/s default; engraving and travel are NOT in it), `masseKg` = area × tjukn × density, `ark`, `utnytting`, `ytre` (envelope), `sporMm`, `godsMm`. `gravMm` is not an engine metric: `skriv.ts` sums the same strokes the files engrave (573 mm, equal to the DXF GRAVER layer read back).
- `deler.csv`: `;` separated, decimal comma, no final newline: `adresse;form;breidd_mm;hogd_mm;flate_cm2;kutt_mm;ledd;plate` → `1;D01;297,14;297,14;210,13;1899,9;8;1`.

## Limits and traps

- **Source id**: letters and digits only. With `lampe-b` the app's worker does not strip the `id__` prefix: the body was called `lampe-b__lampe-b` and every export `slicer-lampe-b__lampe-b-…` (ran). `form.ts registrer` allows the hyphen; `skriv.ts` throws.
- **One mesh, `scene: ""`**: on opening only the first `nett/*` becomes `kjelde`; scene ids are not remapped (read).
- **Parts are nested inside other parts' holes** (ring 3 inside ring 1 here, `iHol`). The file order is engrave → all inner cuts → all outlines, so the offcut carrying part 3 is already loose when part 3 is cut. Pin it elsewhere with `fest: "adr:sheet(0-based),quarter-turns,x,y"`: `fest: "3:0,1,480,280"` gave `3@484,283` on sheet 1, outside the ring (`K/utprov/fest.ts`).
- **Two detail levels**: cut files, numbers, flat GLB and `delar.json` are 220 cells; STL, GLB, 3MF, USDZ are 1200. Boxes differ by up to 0.134 mm on this body. Build CAD from `delar.json` if it must equal what is cut.
- **A part that fits no sheet** is missing from the cut files (hard rule `plate`, `manifest.ok` false); `delar.json` still lists it with `ark: 0` (ran: 120 × 120 sheet → `plate 10 utanfor`, 11 parts in the JSON).
- **Files are written even when hard rules fail** — check `manifest.ok` and `harde[]`.
- **Narrow parts carry no address.** Same dome at `storleik: 70, tjukn: 2`: `10 delar · utan gravert adresse: 4a 4b 5a 5b 6a 6b 7a 7b · med: 1 2` (`K/utprov/smaatt.ts`). `montering.txt` still says every part is engraved; `manifest.ark[].umerkte` tells the truth.
- A plane cut in two pieces is ONE entry in `orden`: both pieces get the same direction.
- `sharp` is not a direct dependency: `skriv.ts` loads `/home/user/slicer.iverfinne.no/node_modules/.pnpm/sharp@0.34.5/node_modules/sharp`. The repo's own Playwright (1.62.1) has no browser installed; `createRequire("/tmp/x.js")("playwright")` gets the global one (1.63.0) that has.
- Not tested: opening on a real iPhone (only Chromium with a phone viewport), the share-sheet path, coloured layers, the USDZ in AR Quick Look, the 3MF in a slicer.
