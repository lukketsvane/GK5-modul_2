import { dreiRing, type RZ } from "../../verkty/form"
import { plan as planVed } from "../../verkty/plan"
import { flatark, type Ekstra } from "../../verkty/ekstra"
import type { Params, Registrert, Utstyr } from "../../verkty/typar"

type V3 = [number, number, number]
export type Val = {
  namn: string
  R: number
  hc: number
  he?: number
  deling: number
  tal: number
  delingB?: number
  talB?: number
  skraa?: number
  vri?: number
  phi: number
  stativ: "flagg" | "blad"
  farge: string
  hogd: number
  fot?: number
  lokk?: number
  skjort?: number
  speglA?: "inn" | "ned" | "begge"
  speglB?: "inn" | "begge" | "matt"
  lysPkt: [number, number][]
  kamera?: Utstyr["kamera"]
  veggAvstand?: number
}

const rad = (g: number) => (g * Math.PI) / 180
const kryss = (a: V3, b: V3): V3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
const rekkje = (n: number, p: number) => Array.from({ length: n }, (_, i) => (i - (n - 1) / 2) * p)

export function raster(v: Val) {
  const he = v.he ?? v.hc
  const lokk = v.lokk ?? 24
  const skjort = v.skjort ?? 9
  const fot = v.fot ?? 140
  const Rk = v.R + 3
  const ring: RZ[] = [[0, 0]]
  const N = he === v.hc ? 1 : 40
  for (let i = 1; i <= N; i++) ring.push([(v.R * i) / N, (v.hc - he) * (i / N) ** 2])
  ring.push([v.R, v.hc], [0, v.hc])
  const c = Math.cos(rad(v.phi))
  const s = Math.sin(rad(v.phi))
  const rot = (q: V3): V3 => [q[0], q[1] * c - q[2] * s, q[1] * s + q[2] * c]
  let C: V3 = [0, 0, 0]
  let nett: Float32Array | null = null
  const bygg = () => {
    if (nett) return nett
    const raa = dreiRing(ring, 144)
    const ut = new Float32Array(raa.length)
    const mn: V3 = [Infinity, Infinity, Infinity]
    const mx: V3 = [-Infinity, -Infinity, -Infinity]
    for (let i = 0; i < raa.length; i += 3) {
      const q = rot([raa[i], raa[i + 1], raa[i + 2]])
      for (let a = 0; a < 3; a++) {
        ut[i + a] = q[a]
        if (q[a] < mn[a]) mn[a] = q[a]
        if (q[a] > mx[a]) mx[a] = q[a]
      }
    }
    C = [-(mn[0] + mx[0]) / 2, -(mn[1] + mx[1]) / 2, -mn[2]]
    for (let i = 0; i < ut.length; i += 3) for (let a = 0; a < 3; a++) ut[i + a] += C[a]
    nett = ut
    return ut
  }
  const paa = (q: V3): V3 => {
    const r = rot(q)
    return [C[0] + r[0], C[1] + r[1], C[2] + r[2]]
  }
  const akse = rot([0, 0, 1])
  const b = rad(v.skraa ?? 0)
  const w = rad(v.vri ?? 0)
  const omZ = (q: V3): V3 => [q[0] * Math.cos(w) - q[1] * Math.sin(w), q[0] * Math.sin(w) + q[1] * Math.cos(w), q[2]]
  const nA0 = omZ([0, Math.cos(b), -Math.sin(b)])
  const nB0 = omZ([1, 0, 0])
  const dA = rekkje(v.tal, v.deling * Math.cos(b))
  const dB = rekkje(v.talB ?? v.tal, v.delingB ?? v.deling)
  const plan = (reg: Registrert) => {
    bygg()
    const ved = (n0: V3, d: number, id: number) => planVed(reg, id, paa([n0[0] * d, n0[1] * d, v.hc / 2 + n0[2] * d]), rot(n0))
    return [...dA.map((d, i) => ved(nA0, d, 1 + i)), ...dB.map((d, i) => ved(nB0, d, 21 + i))]
  }
  const bag: Partial<Params> = { tjukn: 3, material: "akryl", klaring: 0.15, snitt: 0.2, arkB: 600, arkH: 400 }
  const band = (namn: string, Rb: number, s0: number, s1: number, tj: number): Ekstra => {
    const e1 = rot([0, 1, 0])
    const n: V3 = [-e1[0], -e1[1], -e1[2]]
    const u = kryss(akse, n)
    const o = paa([0, Rb, (s0 + s1) / 2])
    const a = Math.PI * Rb
    const h = (s1 - s0) / 2
    return { namn, tjukn: tj, omriss: [[-a, -h], [a, -h], [a, h], [-a, h]], hol: [], matrise: [...u, 0, ...akse, 0, ...n, 0, o[0] - (tj / 2) * n[0], o[1] - (tj / 2) * n[1], o[2] - (tj / 2) * n[2], 1], krumming: 1 / Rb, material: "mdf", farge: v.farge }
  }
  const sirkel = (r: number): [number, number][] => Array.from({ length: 72 }, (_, i) => [r * Math.cos((i * Math.PI) / 36), r * Math.sin((i * Math.PI) / 36)])
  const utstyr = (): Utstyr => {
    bygg()
    const matt = { farge: v.farge, ru: 0.85 }
    const messing = { farge: "#b8935a", metall: 1, ru: 0.35 }
    const delar: NonNullable<Utstyr["delar"]> = {}
    const side = (d: number, slag: string): 1 | -1 | 0 => (slag === "ned" ? 1 : slag === "begge" || Math.abs(d) < 1e-6 ? 0 : d < 0 ? 1 : -1)
    dA.forEach((d, i) => (delar[String(1 + i)] = { material: "spegl", farge: v.farge, speglSide: side(d, v.speglA ?? "inn") }))
    dB.forEach((d, i) => (delar[String(21 + i)] = v.speglB === "matt" ? { material: "mdf", farge: v.farge } : { material: "spegl", farge: v.farge, speglSide: side(d, v.speglB ?? "inn") }))
    const zl = v.hc + lokk
    const hovud = [
      { slag: "sylinder" as const, senter: paa([0, 0, zl + 3]), diameter: 2 * Rk, lengd: 6, retning: akse, ...matt },
    ]
    const ekstra: Ekstra[] = [
      band("skjort", Rk - 0.75, v.hc - skjort, zl, 1.5),
      flatark({ namn: "opal", punkt: paa([0, 0, v.hc + 1.5]), n: akse, omriss: sirkel(v.R), tjukn: 3, material: "akryl-opal" }),
    ]
    const lys = v.lysPkt.map(([x, y]) => ({ punkt: paa([x, y, v.hc - 2]), radius: 4, farge: "#ffcf9a", styrke: 1 }))
    const stativ: NonNullable<Utstyr["utstyr"]> = []
    if (v.stativ === "flagg") {
      const sp = zl / 2
      const P = paa([0, 0, sp])
      const xs = P[0] - Rk - 12
      const zt = P[2] - v.hogd - sp
      stativ.push(
        { slag: "sylinder", senter: [xs, P[1], zt + 5], diameter: fot, lengd: 10, retning: [0, 0, 1], ...matt },
        { slag: "sylinder", senter: [xs, P[1], (zt + 10 + P[2] + 10) / 2], diameter: 8, lengd: P[2] + 10 - zt - 10, retning: [0, 0, 1], ...matt },
        { slag: "sylinder", senter: [(xs + P[0] - Rk) / 2, P[1], P[2]], diameter: 12, lengd: 12, retning: [1, 0, 0], ...messing },
        { slag: "sylinder", senter: [xs - 9, P[1], P[2]], diameter: 24, lengd: 10, retning: [1, 0, 0], ...messing },
        { slag: "leidning", punkt: [[xs, P[1] + fot / 2 - 6, zt + 4], [xs, P[1] + fot / 2 + 40, zt + 2], [xs + 30, P[1] + fot / 2 + 150, zt + 2]], diameter: 4, farge: v.farge },
      )
    } else {
      const sh = (zl + 6) / 2
      const yh = Rk + 11
      const P = paa([0, yh, sh])
      const zt = P[2] - v.hogd - sh
      stativ.push(
        { slag: "sylinder", senter: [P[0], P[1], zt + 5], diameter: fot, lengd: 10, retning: [0, 0, 1], ...matt },
        { slag: "sylinder", senter: [P[0], P[1], (zt + 10 + P[2]) / 2], diameter: 8, lengd: P[2] - zt - 10, retning: [0, 0, 1], ...matt },
        { slag: "sylinder", senter: P, diameter: 14, lengd: 36, retning: [1, 0, 0], ...messing },
        { slag: "sylinder", senter: paa([0, Rk + 4, sh]), diameter: 8, lengd: 12, retning: rot([0, 1, 0]), ...matt },
        { slag: "leidning", punkt: [[P[0], P[1] + fot / 2 - 6, zt + 4], [P[0], P[1] + fot / 2 + 40, zt + 2], [P[0] + 30, P[1] + fot / 2 + 150, zt + 2]], diameter: 4, farge: v.farge },
      )
    }
    return { utstyr: [...hovud, ...stativ], ekstra, delar, lys, ...(v.kamera ? { kamera: v.kamera } : {}), ...(v.veggAvstand ? { veggAvstand: v.veggAvstand } : {}) } as Utstyr
  }
  return { namn: v.namn, kropp: bygg, bag, plan, utstyr }
}
