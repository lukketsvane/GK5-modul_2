import { lesNett } from "../../verkty/form"
import { plan as planVed } from "../../verkty/plan"
import type { Params, Registrert, Utstyr } from "../../verkty/typar"

type V3 = [number, number, number]
export type Grep = "ingen" | "snu" | "drei"
type PF = (p: V3) => V3
export type Val = {
  namn: string; stl: string; H: number; grep: Grep
  dreiZ?: number; vipp?: number; vinkel?: number
  avstand: number; tal: number; tal2?: number; avstand2?: number; fjern?: number[]
  farge: string; material?: string; farge2?: string; material2?: string; tjukn?: number
  utstyr: (P: PF, D: PF) => Utstyr["utstyr"]
  vegg?: number; lys?: Utstyr["lys"]
  scene?: (P: PF, D: PF) => Partial<Utstyr>
}

export function gitter(v: Val) {
  const G = (p: V3): V3 => (v.grep === "snu" ? [p[0], -p[1], v.H - p[2]] : v.grep === "drei" ? [-p[0], -p[1], p[2]] : p)
  const GD = (d: V3): V3 => (v.grep === "snu" ? [d[0], -d[1], -d[2]] : v.grep === "drei" ? [-d[0], -d[1], d[2]] : d)
  const z = ((v.dreiZ ?? 0) * Math.PI) / 180
  const Z = (p: V3): V3 => [p[0] * Math.cos(z) - p[1] * Math.sin(z), p[0] * Math.sin(z) + p[1] * Math.cos(z), p[2]]
  const t = ((v.vipp ?? 0) * Math.PI) / 180
  const R = (p: V3): V3 => [p[0], p[1] * Math.cos(t) - p[2] * Math.sin(t), p[1] * Math.sin(t) + p[2] * Math.cos(t)]
  const raa = lesNett(v.stl)
  const mn: V3 = [Infinity, Infinity, Infinity], mx: V3 = [-Infinity, -Infinity, -Infinity]
  const nett = new Float32Array(raa.length)
  for (let i = 0; i < raa.length; i += 3) {
    const r = R(Z(G([raa[i], raa[i + 1], raa[i + 2]])))
    for (let a = 0; a < 3; a++) { nett[i + a] = r[a]; mn[a] = Math.min(mn[a], r[a]); mx[a] = Math.max(mx[a], r[a]) }
  }
  const S: V3 = [-(mn[0] + mx[0]) / 2, -(mn[1] + mx[1]) / 2, -mn[2]]
  for (let i = 0; i < nett.length; i += 3) for (let a = 0; a < 3; a++) nett[i + a] += S[a]
  const P = (p: V3): V3 => { const r = R(Z(G(p))); return [r[0] + S[0], r[1] + S[1], r[2] + S[2]] }
  const D = (d: V3): V3 => R(Z(GD(d)))
  const kropp = () => nett
  const a = ((v.vinkel ?? 45) * Math.PI) / 180
  const n1: V3 = D([Math.cos(a), Math.sin(a), 0])
  const n2: V3 = D([-Math.sin(a), Math.cos(a), 0])
  const o = P([0, 0, v.H / 2])
  const rad = (k: number, s: number) => Array.from({ length: k }, (_, i) => (i - (k - 1) / 2) * s)
  const off = rad(v.tal, v.avstand)
  const off2 = rad(v.tal2 ?? v.tal, v.avstand2 ?? v.avstand)
  const plan = (k: Registrert) => [
    ...off.map((d, i) => planVed(k, 1 + i, [o[0] + n1[0] * d, o[1] + n1[1] * d, o[2] + n1[2] * d], n1)),
    ...off2.map((d, i) => planVed(k, 21 + i, [o[0] + n2[0] * d, o[1] + n2[1] * d, o[2] + n2[2] * d], n2)),
  ].filter((q) => !(v.fjern ?? []).includes(q.id))
  const bag: Partial<Params> = { tjukn: v.tjukn ?? 3, material: "mdf", klaring: 0.1, snitt: 0.2, arkB: 600, arkH: 400 }
  const delar: Record<string, { material?: string; farge?: string }> = {}
  for (let i = 0; i < v.tal; i++) delar[String(1 + i)] = { material: v.material ?? "mdf", farge: v.farge }
  for (let i = 0; i < (v.tal2 ?? v.tal); i++) delar[String(21 + i)] = { material: v.material2 ?? v.material ?? "mdf", farge: v.farge2 ?? v.farge }
  const utstyr: Utstyr = {
    delar,
    ...(v.vegg ? { vegg: { punkt: [0, v.vegg, 0] as V3, normal: [0, -1, 0] as V3 } } : {}),
    ...(v.lys ? { lys: v.lys.map((l) => ({ ...l, punkt: P(l.punkt as V3) })) } : {}),
    ...(v.scene ? v.scene(P, D) : {}),
    utstyr: v.utstyr(P, D),
  }
  return { namn: v.namn, kropp, bag, plan, utstyr }
}
