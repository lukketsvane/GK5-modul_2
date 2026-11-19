import { utover } from "../../verkty/form"
import { plan as planVed, rundt } from "../../verkty/plan"
import type { Kontekst, Params, Registrert, Utstyr } from "../../verkty/typar"

type V3 = [number, number, number]
export type Val = {
  namn: string
  A: number
  R: number
  Ai: number
  Ri: number
  p?: number
  q?: number
  munn: number
  vri: number
  K: number
  steg: number
  xf: number
  tjukn?: number
  material?: string
  klaring?: number
  arkB?: number
  arkH?: number
  akse: number
  fotD: number
  farge: string
  ramme?: { material: string; farge?: string; speglSide?: 1 | -1 | 0 }
  kjolMat?: { material: string; farge?: string; speglSide?: 1 | -1 | 0 }
  vogge?: number
}

export function lag(v: Val) {
  const p = v.p ?? 2.6
  const q = v.q ?? 0.42
  const f = (t: number) => Math.pow(Math.max(0, 1 - Math.pow(Math.min(1, Math.abs(t)), p)), q)
  const ro = (x: number) => v.R * f(x / v.A)
  const ri = (x: number) => v.Ri * f(x / v.Ai)
  const M = (v.munn * Math.PI) / 180
  const th0 = -Math.PI / 2 + M
  const th1 = (3 * Math.PI) / 2 - M
  const fi = (v.vri * Math.PI) / 180
  const c = Math.cos(fi)
  const s = Math.sin(fi)
  const rot = (u: V3): V3 => [u[0], u[1] * c - u[2] * s, u[1] * s + u[2] * c]
  let C: V3 = [0, 0, 0]
  let nett: Float32Array | null = null
  const N = 110
  const J = 64
  const bygg = () => {
    if (nett) return nett
    const skal = (a: number, r: (x: number) => number): V3[][] =>
      Array.from({ length: N + 1 }, (_, i) => {
        const t = -1 + (2 * i) / N
        const x = a * Math.sign(t) * Math.pow(Math.abs(t), 0.85)
        return Array.from({ length: J + 1 }, (_, j) => {
          const th = th0 + ((th1 - th0) * j) / J
          const rr = r(x)
          return rot([x, rr * Math.cos(th), rr * Math.sin(th)])
        })
      })
    const O = skal(v.A, ro)
    const I = skal(v.Ai, ri)
    const ut: number[] = []
    const d = (a: V3, b: V3) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2])
    const tri = (a: V3, b: V3, e: V3) => {
      if (d(a, b) < 1e-9 || d(b, e) < 1e-9 || d(a, e) < 1e-9) return
      ut.push(...a, ...b, ...e)
    }
    for (let i = 0; i < N; i++)
      for (let j = 0; j < J; j++) {
        tri(O[i][j], O[i + 1][j], O[i + 1][j + 1])
        tri(O[i][j], O[i + 1][j + 1], O[i][j + 1])
        tri(I[i][j], I[i + 1][j + 1], I[i + 1][j])
        tri(I[i][j], I[i][j + 1], I[i + 1][j + 1])
      }
    for (let i = 0; i < N; i++)
      for (const j of [0, J]) {
        const [o0, o1, i0, i1] = [O[i][j], O[i + 1][j], I[i][j], I[i + 1][j]]
        if (j === 0) {
          tri(o0, i1, o1)
          tri(o0, i0, i1)
        } else {
          tri(o0, o1, i1)
          tri(o0, i1, i0)
        }
      }
    const raa = utover(new Float32Array(ut))
    const mn: V3 = [Infinity, Infinity, Infinity]
    const mx: V3 = [-Infinity, -Infinity, -Infinity]
    for (let i = 0; i < raa.length; i += 3)
      for (let a = 0; a < 3; a++) {
        if (raa[i + a] < mn[a]) mn[a] = raa[i + a]
        if (raa[i + a] > mx[a]) mx[a] = raa[i + a]
      }
    C = [-(mn[0] + mx[0]) / 2, -(mn[1] + mx[1]) / 2, -mn[2]]
    for (let i = 0; i < raa.length; i += 3) for (let a = 0; a < 3; a++) raa[i + a] += C[a]
    nett = raa
    return raa
  }
  const paa = (u: V3): V3 => {
    const r = rot(u)
    return [C[0] + r[0], C[1] + r[1], C[2] + r[2]]
  }
  const nF = Math.floor(v.xf / v.steg)
  const xs = Array.from({ length: 2 * nF + 1 }, (_, i) => (i - nF) * v.steg)
  const xp = v.A + 14
  const tapp = v.A - 12
  const plan = (reg: Registrert) => {
    bygg()
    const ny = rot([0, 1, 0])
    return [
      ...[-v.K, v.K].map((y, k) => planVed(reg, 1 + k, paa([0, y, 0]), ny, { strek: [rundt(reg, "hol", 4.2, -tapp, 0), rundt(reg, "hol", 4.2, tapp, 0)] })),
      ...xs.map((x, k) => planVed(reg, 10 + k, paa([x, 0, 0]), [1, 0, 0])),
    ]
  }
  const tj = v.tjukn ?? 3
  const bag: Partial<Params> = { tjukn: tj, material: v.material ?? "bjork", klaring: v.klaring ?? 0.1, snitt: 0.2, arkB: v.arkB ?? 600, arkH: v.arkH ?? 400 }
  const ry = v.R + (v.vogge ?? 12)
  const geom = () => {
    bygg()
    const a = paa([0, 0, 0])
    const zb = a[2] - ry
    const golv = a[2] - v.akse
    return { a, zb, golv }
  }
  const utstyr = (): Utstyr => {
    const { a, zb, golv } = geom()
    const matt = { farge: v.farge, ru: 0.8 }
    const ms = { farge: "#b8935a", metall: 1, ru: 0.35 }
    const alu = { farge: "#8d918f", metall: 0.6, ru: 0.45 }
    const lx = Math.min(v.xf + 6, v.Ai - 20)
    const nb = 7
    const paerer = Array.from({ length: nb }, (_, i) => {
      const x = -lx + 14 + ((2 * lx - 28) * i) / (nb - 1)
      return { slag: "paere" as const, senter: paa([x, 0, -10]), diameter: 9, lengd: 11, retning: rot([0, 0, 1]) }
    })
    const rb = Math.round(0.62 * ry)
    const boge: V3[] = []
    const ende = (sx: number) => {
      const pts: V3[] = []
      for (let i = 0; i <= 8; i++) {
        const g = (Math.PI / 2) * (i / 8)
        pts.push([sx * (xp - rb + rb * Math.sin(g)), a[1], zb + rb - rb * Math.cos(g)])
      }
      return pts
    }
    const vs = ende(-1).reverse()
    boge.push([-xp, a[1], a[2]], [-xp, a[1], (a[2] + zb + rb) / 2], ...vs)
    for (let i = 1; i < 8; i++) boge.push([-xp + rb + ((2 * (xp - rb)) * i) / 8, a[1], zb])
    boge.push(...ende(1), [xp, a[1], (a[2] + zb + rb) / 2], [xp, a[1], a[2]])
    const stilk: { slag: "sylinder"; senter: V3; diameter: number; lengd: number; retning: V3; farge: string; ru: number }[] = []
    const hS = zb - 5 - (golv + 9)
    const nS = 44
    for (let i = 0; i < nS; i++) {
      const t0 = i / nS
      const dia = 11 + 30 * Math.pow(1 - t0, 4.5)
      stilk.push({ slag: "sylinder", senter: [a[0], a[1], golv + 9 + hS * (t0 + 0.5 / nS)], diameter: dia, lengd: hS / nS + 0.2, retning: [0, 0, 1], ...matt })
    }
    const delar: NonNullable<Utstyr["delar"]> = {}
    if (v.ramme) for (let k = 0; k < xs.length; k++) delar[String(10 + k)] = { ...v.ramme, ...(v.ramme.material === "spegl" ? { speglSide: (xs[k] < 0 ? 1 : -1) as 1 | -1 } : {}) }
    else for (let k = 0; k < xs.length; k++) delar[String(10 + k)] = { material: "mdf", farge: v.farge }
    for (const id of ["1", "2"]) delar[id] = v.kjolMat ?? { material: "mdf", farge: v.farge }
    return {
      delar,
      utstyr: [
        { slag: "sylinder", senter: paa([0, 0, 0]), diameter: 12, lengd: 2 * lx, retning: rot([1, 0, 0]), ...alu },
        { slag: "boks", senter: paa([0, 0, -6.5]), storleik: [2 * lx - 8, 9, 1.5], ...{ farge: "#f4efe6", ru: 0.6 } },
        ...paerer,
        { slag: "sylinder", senter: [a[0] - (xp + v.A - 4) / 2, a[1], a[2]], diameter: 6, lengd: xp - v.A + 4 + 8, retning: [1, 0, 0], ...matt },
        { slag: "sylinder", senter: [a[0] + (xp + v.A - 4) / 2, a[1], a[2]], diameter: 6, lengd: xp - v.A + 4 + 8, retning: [1, 0, 0], ...matt },
        { slag: "leidning", punkt: boge, diameter: 8, ...matt },
        { slag: "sylinder", senter: [a[0] + xp + 9, a[1], a[2]], diameter: 22, lengd: 14, retning: [1, 0, 0], ...ms },
        { slag: "sylinder", senter: [a[0] - xp - 3, a[1], a[2]], diameter: 12, lengd: 4, retning: [1, 0, 0], ...matt },
        ...stilk,
        { slag: "sylinder", senter: [a[0], a[1], golv + 4.5], diameter: v.fotD, lengd: 9, retning: [0, 0, 1], ...matt },
        { slag: "leidning", punkt: [[a[0], a[1] + v.fotD * 0.3, golv + 4], [a[0], a[1] + v.fotD * 0.5 + 10, golv + 3], [a[0] + 30, a[1] + v.fotD * 0.5 + 120, golv + 3]], diameter: 4, farge: "#1f1f1f", ru: 0.7 },
      ],
    }
  }
  const krav = (x: Kontekst) => {
    const { a, zb, golv } = geom()
    const lx = Math.min(v.xf + 6, v.Ai - 20)
    const topp = a[2] + v.R
    const vekt = x.m && (x.m as any).massKg
    return [
      x.krav("mål med stativ", true, `lengd ${(2 * xp + 32).toFixed(0)} · høgd ${(topp - golv).toFixed(0)} · akse ${(a[2] - golv).toFixed(0)} over bordet · kropp ø${(2 * v.R).toFixed(0)} · fot ø${v.fotD} = ${((Math.PI * v.fotD * v.fotD) / 400).toFixed(0)} cm2 · ${xs.length} spant, steg ${v.steg} · ${vekt ?? ""}`),
      x.friKrav("vogga går fri under kroppen", [a[0] - xp + 30, a[1], zb], [a[0] + xp - 30, a[1], zb], ry - v.R - 6),
      x.friKrav("lysstaven går fri av spanta", paa([-lx, 0, 0]), paa([lx, 0, 0]), 9),
      x.friKrav("armane går fri av kjølen", [a[0] + xp, a[1], a[2] - 4], [a[0] + xp, a[1], zb + 26], 5),
      x.krav("stifthol i kjøl 1", x.hol("1").length === 2, JSON.stringify(x.hol("1").map((h) => [h.d.toFixed(2), h.iKroppen.map((q) => q.toFixed(0)).join(","), h.iLuft]))),
      x.krav("stifthol i kjøl 2", x.hol("2").length === 2, JSON.stringify(x.hol("2").map((h) => [h.d.toFixed(2), h.iKroppen.map((q) => q.toFixed(0)).join(","), h.iLuft]))),
    ]
  }
  return { namn: v.namn, kropp: bygg, bag, plan, utstyr: utstyr, krav }
}
