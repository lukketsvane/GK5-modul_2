import { lesNett } from "./verkty/form"
import { plan as planVed } from "./verkty/plan"
import type { Params, Registrert, Utstyr } from "./verkty/typar"
import { flatark } from "./verkty/ekstra"
import { akser } from "../slicer/lib/plan"

export type V3 = [number, number, number]
export type M3 = [V3, V3, V3]
const I: M3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
const mul = (a: M3, b: M3): M3 => a.map((r) => [0, 1, 2].map((j) => r[0] * b[0][j] + r[1] * b[1][j] + r[2] * b[2][j])) as M3
const app = (m: M3, p: V3): V3 => m.map((r) => r[0] * p[0] + r[1] * p[1] + r[2] * p[2]) as V3
const cs = (g: number) => [Math.cos((g * Math.PI) / 180), Math.sin((g * Math.PI) / 180)]
export const rotX = (g: number): M3 => { const [c, s] = cs(g); return [[1, 0, 0], [0, c, -s], [0, s, c]] }
export const rotY = (g: number): M3 => { const [c, s] = cs(g); return [[c, 0, s], [0, 1, 0], [-s, 0, c]] }
export const rotZ = (g: number): M3 => { const [c, s] = cs(g); return [[c, -s, 0], [s, c, 0], [0, 0, 1]] }
export const pose = (...ms: M3[]): M3 => ms.reduce((a, b) => mul(b, a), I)

export type Fam = { n: V3; avstand: number; tal: number; skift?: number; stader?: number[]; material?: string; farge?: string }
type Fn = (p: V3) => V3
export type Val = {
  namn: string
  stl: string
  pose?: M3
  fam: [Fam, Fam]
  farge: string
  material?: string
  tjukn?: number
  senter?: V3
  fjern?: number[]
  vegg?: number
  snudd?: boolean
  fri?: boolean
  flytt?: V3
  lys?: { punkt: V3; radius?: number; farge?: string; styrke?: number }[]
  utstyr?: (P: Fn, D: Fn) => Utstyr["utstyr"]
  scene?: (P: Fn, D: Fn) => Partial<Utstyr>
  ark?: [number, number]
  boygde?: { namn: string; senter: V3; u: V3; v: V3; n: V3; omriss: [number, number][]; hol?: [number, number][][]; R: number; tjukn?: number; material?: string; farge?: string }[]
  flater?: { namn: string; punkt: V3; n: V3; omriss: V3[]; hol?: V3[][]; tjukn?: number; material?: string; farge?: string }[]
}

export function gitter(v: Val) {
  const M = v.pose ?? I
  const raa = lesNett(v.stl)
  const b0: V3 = [Infinity, Infinity, Infinity], b1: V3 = [-Infinity, -Infinity, -Infinity]
  const mn: V3 = [Infinity, Infinity, Infinity], mx: V3 = [-Infinity, -Infinity, -Infinity]
  const nett = new Float32Array(raa.length)
  for (let i = 0; i < raa.length; i += 3) {
    const q: V3 = [raa[i], raa[i + 1], raa[i + 2]]
    const r = app(M, q)
    for (let a = 0; a < 3; a++) { nett[i + a] = r[a]; mn[a] = Math.min(mn[a], r[a]); mx[a] = Math.max(mx[a], r[a]); b0[a] = Math.min(b0[a], q[a]); b1[a] = Math.max(b1[a], q[a]) }
  }
  const S: V3 = v.fri ? (v.flytt ?? [0, 0, 0]) : [-(mn[0] + mx[0]) / 2, -(mn[1] + mx[1]) / 2, -mn[2]]
  for (let i = 0; i < nett.length; i += 3) for (let a = 0; a < 3; a++) nett[i + a] += S[a]
  const P: Fn = (p) => { const r = app(M, p); return [r[0] + S[0], r[1] + S[1], r[2] + S[2]] }
  const D: Fn = (d) => app(M, d)
  const c = v.senter ?? [(b0[0] + b1[0]) / 2, (b0[1] + b1[1]) / 2, (b0[2] + b1[2]) / 2]
  const norm = (n: V3): V3 => { const l = Math.hypot(...n); return [n[0] / l, n[1] / l, n[2] / l] }
  const rekkje = (f: Fam, id0: number) => {
    const n = norm(f.n)
    return Array.from({ length: f.stader?.length ?? f.tal }, (_, i) => {
      const d = f.stader ? f.stader[i] : (i - (f.tal - 1) / 2) * f.avstand + (f.skift ?? 0)
      return { id: id0 + i, punkt: P([c[0] + n[0] * d, c[1] + n[1] * d, c[2] + n[2] * d]), normal: D(n) }
    })
  }
  const alle = [...rekkje(v.fam[0], 1), ...rekkje(v.fam[1], 21)].filter((q) => !(v.fjern ?? []).includes(q.id))
  const plan = (k: Registrert) => alle.map((q) => planVed(k, q.id, q.punkt, q.normal))
  if (process.env.FARGE) { v = { ...v, material: "mdf", farge: process.env.FARGE, fam: v.fam.map((f) => (f.material === "akryl-opal" ? f : { ...f, material: undefined, farge: undefined })) as [Fam, Fam] } }
  const bag: Partial<Params> = { tjukn: v.tjukn ?? 3, material: v.material ?? "mdf", klaring: 0.1, snitt: 0.2, arkB: v.ark?.[0] ?? 600, arkH: v.ark?.[1] ?? 400 }
  const delar: Record<string, { material?: string; farge?: string }> = {}
  v.fam.forEach((f, j) => { for (let i = 0; i < (f.stader?.length ?? f.tal); i++) for (const e of ["", "a", "b", "c", "d", "e", "f", "g", "h"]) delar[String((j ? 21 : 1) + i) + e] = { material: f.material ?? v.material ?? "mdf", farge: f.farge ?? v.farge } })
  const ekstra = (v.flater ?? []).map((f) => {
    const o = P(f.punkt), n = D(norm(f.n)), { u, v: w } = akser(n)
    const to = (q: V3): [number, number] => { const r = P(q); const d: V3 = [r[0] - o[0], r[1] - o[1], r[2] - o[2]]; return [d[0] * u[0] + d[1] * u[1] + d[2] * u[2], d[0] * w[0] + d[1] * w[1] + d[2] * w[2]] }
    return flatark({ namn: f.namn, punkt: o, n, omriss: f.omriss.map(to), hol: (f.hol ?? []).map((h) => h.map(to)), tjukn: f.tjukn ?? 3, material: f.material, farge: f.farge })
  })
  const utstyr: Utstyr = {
    delar,
    ...(ekstra.length || v.boygde?.length ? { ekstra: [...ekstra, ...(v.boygde ?? []).map((q) => { const t = q.tjukn ?? 3, o = P(q.senter), u = D(q.u), w = D(q.v), n = D(q.n); return { namn: q.namn, tjukn: t, omriss: q.omriss, hol: q.hol ?? [], matrise: [...u, 0, ...w, 0, ...n, 0, o[0] - (t / 2) * n[0], o[1] - (t / 2) * n[1], o[2] - (t / 2) * n[2], 1], krumming: 1 / q.R, material: q.material, farge: q.farge } })] } : {}),
    ...(v.vegg ? { vegg: { punkt: [0, v.snudd ? -v.vegg : v.vegg, 0] as V3, normal: [0, v.snudd ? 1 : -1, 0] as V3 } } : {}),
    ...(v.lys ? { lys: v.lys.map((l) => ({ ...l, punkt: P(l.punkt) })) } : {}),
    ...(v.scene ? v.scene(P, D) : {}),
    utstyr: v.utstyr ? v.utstyr(P, D) : [],
  }
  return { namn: v.namn, kropp: () => nett, bag, plan, utstyr }
}
