import { dreiRing, sirkelRing, type RZ } from "../verkty/form"
import { flatark } from "../verkty/ekstra"
import { plan as planVed } from "../verkty/plan"
import type { Params, Registrert, Utstyr } from "../verkty/typar"

export type Val = {
  namn: string
  R: number
  bor: number
  fot?: number
  topphol?: number
  a: number[]
  b: number[]
  vinkel?: number
  hell?: number
  tjukn?: number
  heng?: boolean
  paere?: number
  ark?: [number, number]
  hals?: { r: number; tjukk: number; under: number; hol?: number }
  ligg?: boolean
}

export function kule(v: Val) {
  const { R, bor } = v
  const rb = bor + (v.fot ?? 22)
  const zc = Math.sqrt(R * R - rb * rb)
  const ct = v.topphol ?? 0
  const ring: RZ[] = [[bor, 0], [rb, 0]]
  const t0 = -Math.asin(zc / R)
  const t1 = ct > 0 ? Math.acos(ct / R) : Math.PI / 2
  const N = 96
  for (let i = 1; i <= N; i++) {
    const t = t0 + ((t1 - t0) * i) / N
    ring.push([R * Math.cos(t), zc + R * Math.sin(t)])
  }
  const tak = zc + bor
  const zs = v.hals ? tak - v.hals.under : 0
  const zt = v.hals ? zs + v.hals.tjukk : 0
  if (v.hals) {
    ring.length = 2
    const th = Math.acos(v.hals.r / R)
    for (let i = 1; i <= N; i++) {
      const t = t0 + ((th - t0) * i) / N
      ring.push([R * Math.cos(t), zc + R * Math.sin(t)])
    }
    const rh = v.hals.hol ?? 5
    ring.push([v.hals.r, zt], [rh, zt], [rh, zs])
  }
  const f1 = v.hals ? Math.asin((zs - zc) / bor) : ct > 0 ? Math.acos(ct / bor) : Math.PI / 2
  for (let i = 0; i <= 48; i++) {
    const f = f1 * (1 - i / 48)
    ring.push([bor * Math.cos(f), zc + bor * Math.sin(f)])
  }
  const ligg = !!v.ligg
  const zTopp = zc + Math.sqrt(R * R - (v.hals ? v.hals.r : ct) ** 2)
  const cy = -(zTopp - 2 * zc) / 2
  const Y = (z: number) => z - zc + cy
  const senter: [number, number, number] = ligg ? [0, cy, R] : [0, 0, zc]
  const legg = (pos: Float32Array) => {
    const ut = new Float32Array(pos.length)
    for (let i = 0; i < pos.length; i += 3) {
      ut[i] = pos[i]
      ut[i + 1] = Y(pos[i + 2])
      ut[i + 2] = R - pos[i + 1]
    }
    return ut
  }
  const kropp = () => (ligg ? legg(dreiRing(ring, 128)) : dreiRing(ring, 128))
  const bag: Partial<Params> = { tjukn: v.tjukn ?? 4, material: "bjork", klaring: 0.1, snitt: 0.2, arkB: v.ark?.[0] ?? 600, arkH: v.ark?.[1] ?? 400 }
  const vin = ((v.vinkel ?? 90) * Math.PI) / 180
  const hell = ((v.hell ?? (v.ligg ? 45 : 0)) * Math.PI) / 180
  const na: [number, number, number] = [Math.cos(hell), 0, Math.sin(hell)]
  const nb: [number, number, number] = hell ? [Math.cos(hell), 0, -Math.sin(hell)] : [Math.cos(vin), Math.sin(vin), 0]
  const plan = (k: Registrert) => [
    ...v.a.map((d, i) => planVed(k, 1 + i, [senter[0] + na[0] * d, senter[1] + na[1] * d, senter[2] + na[2] * d], na)),
    ...v.b.map((d, i) => planVed(k, 21 + i, [senter[0] + nb[0] * d, senter[1] + nb[1] * d, senter[2] + nb[2] * d], nb)),
  ]
  const H = zc + R
  const p = v.paere ?? 95
  const trinn = [0, 1, 2].map((i) => Math.sqrt(R * R - (R - 4 * (i + 1)) ** 2))
  const liggUtstyr: Utstyr = {
    utstyr: [
      { slag: "sokkel", senter: [0, Y(zt + 14), R], diameter: 40, lengd: 62, retning: [0, 1, 0] },
      { slag: "sylinder", senter: [0, Y(zt + 3.5), R], diameter: 57, lengd: 7, retning: [0, 1, 0], farge: "#1b1b1b" },
      { slag: "sylinder", senter: [0, Y(zs - 3.5), R], diameter: 57, lengd: 7, retning: [0, 1, 0], farge: "#1b1b1b" },
      { slag: "paere", senter: [0, Y(zs - 30 - (p + 38) / 2 + 19), R], diameter: p, lengd: p + 38, retning: [0, 1, 0] },
      { slag: "leidning", punkt: [[0, Y(zc + R) - 4, R], [0, Y(zc + R) + 50, R - 30], [30, Y(zc + R) + 110, 4], [150, Y(zc + R) + 190, 3]], diameter: 6 },
    ],
    ekstra: trinn.map((ri, i) => flatark({ namn: `vogge${i + 1}`, punkt: [0, cy, 4 * i + 2], n: [0, 0, 1], omriss: sirkelRing(80, 64), hol: [sirkelRing(ri, 64).reverse()], tjukn: 4, material: "bjork" })),
  }
  const utstyr: Utstyr = ligg ? liggUtstyr : v.heng
    ? { heng: { tak: H + 500, feste: [0, 0, H - 6] }, utstyr: [
        { slag: "sokkel", senter: [0, 0, v.hals ? zt + 14 : zc + p / 2 + 30], diameter: 40, lengd: v.hals ? 62 : 56 },
        ...(v.hals ? [{ slag: "sylinder" as const, senter: [0, 0, zt + 3.5] as [number, number, number], diameter: 57, lengd: 7, farge: "#1b1b1b" }, { slag: "sylinder" as const, senter: [0, 0, zs - 3.5] as [number, number, number], diameter: 57, lengd: 7, farge: "#1b1b1b" }] : []),
        { slag: "paere", senter: [0, 0, v.hals ? zs - 30 - (p + 38) / 2 + 19 : zc - 4], diameter: p, lengd: p + 38, retning: [0, 0, 1] } ] }
    : { utstyr: [
        { slag: "sokkel", senter: [0, 0, 30], diameter: 40, lengd: 60 },
        { slag: "paere", senter: [0, 0, zc + 4], diameter: p, lengd: p + 38, retning: [0, 0, -1] },
        { slag: "leidning", punkt: [[0, 0, 6], [rb + 40, 30, 4], [R + 160, 120, 3]], diameter: 6 } ] }
  return { namn: v.namn, kropp, bag, plan, utstyr }
}
