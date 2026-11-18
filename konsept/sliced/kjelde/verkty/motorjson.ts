import { readFileSync, writeFileSync } from "node:fs"
import { makeBygg } from "/home/user/slicer.iverfinne.no/lib/bygg"
import { parseMesh } from "/home/user/slicer.iverfinne.no/lib/io"
import { montasjen } from "/home/user/slicer.iverfinne.no/lib/montasje"
import { DEFAULT_PARAMS, type Params } from "/home/user/slicer.iverfinne.no/lib/params"
import { rutenett, skrivPlan } from "/home/user/slicer.iverfinne.no/lib/plan"
import { DETAIL } from "/home/user/slicer.iverfinne.no/lib/snitt"
import { put } from "/home/user/slicer.iverfinne.no/lib/sources"

const [ut, oppsett, detalj = "fil", nett] = process.argv.slice(2)
if (!ut) {
  console.error("bruk: motorjson.ts <ut.json> [oppsett.json|-] [lav|mid|hog|fil] [nett.stl|.glb|.obj]")
  process.exit(2)
}
const eige = oppsett && oppsett !== "-" ? JSON.parse(readFileSync(oppsett, "utf8")) : {}
if (eige.plan === undefined) eige.plan = skrivPlan(rutenett(4, 4))
if (nett) {
  const f = readFileSync(nett)
  put("fil", nett.split("/").pop() ?? "fil", parseMesh(nett, f.buffer.slice(f.byteOffset, f.byteOffset + f.byteLength) as ArrayBuffer))
  eige.kjelde = "fil"
}
const p = { ...DEFAULT_PARAMS, ...eige } as Params
const t0 = Date.now()
const b = makeBygg(p, DETAIL[detalj as keyof typeof DETAIL])
const m = montasjen(b.s, b.dl.delar, b.ns, p.tjukn, b.k.solid.min, b.k.solid.max)
const rammer = new Map(b.s.ribber.map((r) => [r.plan.id, r.r]))
const fargar = ["#c9a36b", "#6b8fc9", "#8fc96b", "#c96b8f", "#6bc9c0", "#b9a0d8"]
const delar = b.dl.delar.flatMap((d) => {
  const md = m.delar.find((x) => x.adr === d.adr)
  const r = rammer.get(d.plan)
  if (!md || !r) return []
  const t = p.tjukn
  const matrise = [...r.u, 0, ...r.v, 0, ...r.n, 0, r.o[0] - (t / 2) * r.n[0], r.o[1] - (t / 2) * r.n[1], r.o[2] - (t / 2) * r.n[2], 1]
  return [{ namn: d.adr, tjukn: t, omriss: d.outline, hol: d.holes, matrise, steg: md.steg + 1, farge: fargar[md.steg % fargar.length], boygd: !!md.boygd }]
})
writeFileSync(ut, JSON.stringify({ namn: String(p.kjelde), eining: "mm", delar }))
const punkt = delar.reduce((s, d) => s + d.omriss.length + d.hol.reduce((n, h) => n + h.length, 0), 0)
console.log(`kropp ${b.k.solid.min.map((x, i) => `${x.toFixed(1)}..${b.k.solid.max[i].toFixed(1)}`).join(" ")}`)
console.log(`${delar.length} delar · ${m.steg} steg · ${punkt} punkt · ${delar.filter((d) => d.boygd).length} bøygde · ${((Date.now() - t0) / 1000).toFixed(1)} s`)
