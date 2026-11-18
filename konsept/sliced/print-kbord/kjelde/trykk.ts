import { readFileSync, writeFileSync, mkdirSync } from "node:fs"
import { MOTOR } from "./motor/lib/motor"
import { DETAIL } from "./motor/lib/snitt"
import { makeBygg } from "./motor/lib/bygg"
import { flatDelar } from "./motor/lib/mesh"
import { delarTo3mf } from "./motor/lib/export-3mf"
import { lesNett, registrer, dreiRing, prisme, type Pt } from "./verkty/form"

const P = "/tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/print"
const UT = `${P}/ut`
mkdirSync(`${UT}/plater`, { recursive: true })
const r = JSON.parse(readFileSync(`${P}/kbord/ut/rapport.json`, "utf8"))
const bag = r.pose
registrer(bag.kjelde, lesNett(`${P}/kbord/ut/kropp.stl`))
const BED = 256
const { ns } = makeBygg(bag, DETAIL.fil)
const grupper = flatDelar(ns, bag.tjukn, true)
const oversyn: { plate: number; delar: string[]; min: number[]; max: number[] }[] = []
for (const [i, g] of grupper.entries()) {
  const mn = [Infinity, Infinity, Infinity], mx = [-Infinity, -Infinity, -Infinity]
  for (const d of g.delar) for (let k = 0; k < d.positions.length; k += 3) for (let a = 0; a < 3; a++) { mn[a] = Math.min(mn[a], d.positions[k + a]); mx[a] = Math.max(mx[a], d.positions[k + a]) }
  const dx = (BED - (mx[0] - mn[0])) / 2 - mn[0], dy = (BED - (mx[1] - mn[1])) / 2 - mn[1]
  const delar = g.delar.map((d) => {
    const p = new Float32Array(d.positions)
    for (let k = 0; k < p.length; k += 3) { p[k] += dx; p[k + 1] += dy }
    return { namn: d.adr, positions: p, tris: d.tris }
  })
  writeFileSync(`${UT}/plater/kbord-plate-${i + 1}.3mf`, delarTo3mf(delar, `kbord-plate-${i + 1}`))
  const ny = delar.flatMap((d) => [d])
  const mn2 = [Infinity, Infinity, Infinity], mx2 = [-Infinity, -Infinity, -Infinity]
  for (const d of ny) for (let k = 0; k < d.positions.length; k += 3) for (let a = 0; a < 3; a++) { mn2[a] = Math.min(mn2[a], d.positions[k + a]); mx2[a] = Math.max(mx2[a], d.positions[k + a]) }
  oversyn.push({ plate: i + 1, delar: g.delar.map((d) => d.adr), min: mn2.map((v) => +v.toFixed(2)), max: mx2.map((v) => +v.toFixed(2)) })
  writeFileSync(`${UT}/plater/plate-${i + 1}.json`, JSON.stringify(delar.map((d) => ({ namn: d.namn, pos: Array.from(d.positions) }))))
}
const R = 120
const ytre = 80
const steg = [1, 2, 3].map((n) => Math.sqrt(R * R - (R - 4 * n) ** 2))
const vogge: [number, number][] = [[steg[0], 0], [ytre, 0], [ytre, 12], [steg[2], 12], [steg[2], 8], [steg[1], 8], [steg[1], 4], [steg[0], 4]]
const vp = dreiRing(vogge, 192)
const vg = new Float32Array(vp)
for (let k = 0; k < vg.length; k += 3) { vg[k] += BED / 2; vg[k + 1] += BED / 2 }
writeFileSync(`${UT}/plater/kbord-plate-${grupper.length + 1}-vogge.3mf`, delarTo3mf([{ namn: "vogge", positions: vg, tris: vg.length / 9 }], "kbord-vogge"))
const t = bag.tjukn
const slissar = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
const L = 14 + slissar.length * 16, H = 34, djup = 16
const omr: Pt[] = [[0, 0], [L, 0], [L, H]]
for (let i = slissar.length - 1; i >= 0; i--) {
  const cx = 14 + i * 16, w = t + slissar[i]
  omr.push([cx + w / 2, H], [cx + w / 2, H - djup], [cx - w / 2, H - djup], [cx - w / 2, H])
}
omr.push([6, H], [0, H - 6])
const kam = prisme(omr, 0, t)
const tunge = prisme([[0, 0], [80, 0], [80, 22], [0, 22]], 0, t)
const flytt = (m: Float32Array, x: number, y: number) => { const o = new Float32Array(m); for (let k = 0; k < o.length; k += 3) { o[k] += x; o[k + 1] += y } return o }
const k1 = flytt(kam, 60, 90), k2 = flytt(tunge, 60, 150)
writeFileSync(`${UT}/kbord-passprove.3mf`, delarTo3mf([{ namn: "passprove-kam", positions: k1, tris: k1.length / 9 }, { namn: "passprove-tunge", positions: k2, tris: k2.length / 9 }], "kbord-passprove"))
writeFileSync(`${UT}/plater/oversyn.json`, JSON.stringify({ plater: oversyn, vogge: { ytre, steg: steg.map((v) => +v.toFixed(1)) }, slissar: slissar.map((s) => +(t + s).toFixed(2)) }, null, 1))
console.log(JSON.stringify(oversyn))
console.log("vogge steg", steg.map((v) => v.toFixed(1)).join(" "), "· passprøve slissar", slissar.map((s) => (t + s).toFixed(2)).join(" "))
const mo = MOTOR.exportFile(bag, "montering" as never) as unknown as { data?: ArrayBuffer }
console.log("montering", mo && mo.data ? "ja" : "nei")
