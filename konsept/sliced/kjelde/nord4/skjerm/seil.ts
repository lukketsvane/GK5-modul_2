import { prisme } from "../../verkty/form"
import { plan as planVed, mm } from "../../verkty/plan"
import type { Kontekst, Params, Pt, Registrert, Utstyr } from "../../verkty/typar"

type V3 = [number, number, number]
export type Val = {
  namn: string
  R: number
  grader: number
  H: number
  vri: number
  farge: string
  fot: number
  lepe?: number
  kant?: number
  kamera?: Utstyr["kamera"]
}

const rad = (g: number) => (g * Math.PI) / 180

export function lag(v: Val) {
  const t = 3
  const lepe = v.lepe ?? 10
  const Rc = v.R + (v.kant ?? 8)
  const h = rad(v.grader / 2)
  const yc = v.R * Math.cos(h) - lepe
  const xc = Math.sqrt(Rc * Rc - yc * yc)
  const a0 = Math.atan2(yc, xc)
  const N = 64
  const d: Pt[] = []
  for (let i = 0; i <= N; i++) {
    const a = a0 + ((Math.PI - 2 * a0) * i) / N
    d.push([Rc * Math.cos(a), Rc * Math.sin(a)])
  }
  const c = Math.cos(rad(v.vri))
  const s = Math.sin(rad(v.vri))
  const r2 = (p: Pt): Pt => [p[0] * c - p[1] * s, p[0] * s + p[1] * c]
  const dr = d.map(r2)
  const mn = [Math.min(...dr.map((p) => p[0])), Math.min(...dr.map((p) => p[1]))]
  const mx = [Math.max(...dr.map((p) => p[0])), Math.max(...dr.map((p) => p[1]))]
  const C: Pt = [-(mn[0] + mx[0]) / 2, -(mn[1] + mx[1]) / 2]
  const paa = (q: V3): V3 => {
    const r = r2([q[0], q[1]])
    return [r[0] + C[0], r[1] + C[1], q[2]]
  }
  const ret = (q: V3): V3 => {
    const r = r2([q[0], q[1]])
    return [r[0], r[1], q[2]]
  }
  const ring = dr.map((p) => [p[0] + C[0], p[1] + C[1]] as Pt)
  const kropp = () => prisme(ring, 0, v.H)
  const Z0 = t / 2
  const Z1 = v.H - t / 2
  const zm = (Z0 + Z1) / 2
  const bue = v.R * rad(v.grader) / 2
  const plan = (k: Registrert) => [
    planVed(k, 1, paa([0, 0, Z0]), [0, 0, 1]),
    planVed(k, 2, paa([0, 0, Z1]), [0, 0, 1]),
    planVed(k, 10, paa([0, v.R, zm]), ret([0, -1, 0]), { bog: Math.round((k.storleik / v.R) * 1e4) / 1e4, omriss: mm(k, [[-bue, Z0 - zm], [bue, Z0 - zm], [bue, Z1 - zm], [-bue, Z1 - zm]]) }),
  ]
  const bag: Partial<Params> = { tjukn: t, material: "bjork", klaring: 0.1, snitt: 0.15, arkB: 600, arkH: 450 }
  const yp = (yc + Rc) / 2
  const utstyr = (): Utstyr => {
    const matt = { farge: v.farge, ru: 0.8 }
    const messing = { farge: "#b8935a", metall: 1, ru: 0.32 }
    const P = paa([0, yp, 0])
    const sb = paa([0, yc + lepe + 2, zm])
    const hb = Z1 - Z0 - 2 * t
    return {
      utstyr: [
        { slag: "sylinder", senter: [P[0], P[1], -19], diameter: v.fot, lengd: 10, retning: [0, 0, 1], ...matt },
        { slag: "sylinder", senter: [P[0], P[1], -7], diameter: 30, lengd: 14, retning: [0, 0, 1], ...messing },
        { slag: "boks", senter: sb, storleik: [Math.abs(12 * c) + Math.abs(8 * s), Math.abs(12 * s) + Math.abs(8 * c), hb], ...matt },
        { slag: "leidning", punkt: [[P[0], P[1] + v.fot / 2 - 8, -20], [P[0], P[1] + v.fot / 2 + 30, -23], [P[0] + 40, P[1] + v.fot / 2 + 160, -23]], diameter: 4, farge: v.farge },
      ],
      lys: [0.25, 0.5, 0.75].map((f) => ({ punkt: paa([0, yc + lepe + 10, Z0 + f * (Z1 - Z0)]), radius: 5, farge: "#ffc98f", styrke: 1 })),
      delar: { "1": { material: "mdf", farge: v.farge }, "2": { material: "mdf", farge: v.farge }, "10": { material: "mdf", farge: v.farge } },
      ...(v.kamera ? { kamera: v.kamera } : {}),
    } as Utstyr
  }
  const krav = (x: Kontekst) => [
    x.krav("tre delar", x.liste.length === 3, `${x.liste.length} delar`),
    x.krav("botnen under 200 cm2", (Math.PI * v.fot * v.fot) / 4 / 100 <= 200, `fot ${((Math.PI * v.fot * v.fot) / 400).toFixed(0)} cm2`),
  ]
  return { namn: v.namn, kropp, bag, plan, utstyr, krav }
}
