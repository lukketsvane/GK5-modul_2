import { loft } from "../../verkty/form"
import { plan as planVed, radialplate, utanfraa } from "../../verkty/plan"
import { flatark, type Ekstra } from "../../verkty/ekstra"
import type { Kontekst, Params, Pt, Registrert, Utstyr } from "../../verkty/typar"

type V3 = [number, number, number]
export type Val = {
  namn: string
  B: number
  D: number
  H: number
  vegg: number
  fins: number
  ribber: number[]
  stilk: number
  fot: number
  vri: 0 | 180
  farge: string
  kamera?: Utstyr["kamera"]
}


export function lag(v: Val) {
  const t = 3
  const r = v.B / 2
  const ya = v.D / 2 - r
  const yf = -v.D / 2
  const s = v.vri === 180 ? -1 : 1
  const d: Pt[] = []
  const rc = 16
  const bue = (cx: number, cy: number, rr: number, a0: number, a1: number, n: number, med0: boolean) => {
    for (let i = med0 ? 0 : 1; i <= n; i++) {
      const a = a0 + ((a1 - a0) * i) / n
      d.push([cx + rr * Math.cos(a), cy + rr * Math.sin(a)])
    }
  }
  const linje = (a: Pt, b: Pt, n: number) => {
    for (let i = 1; i < n; i++) d.push([a[0] + ((b[0] - a[0]) * i) / n, a[1] + ((b[1] - a[1]) * i) / n])
  }
  bue(0, ya, r, 0, Math.PI, 56, true)
  linje([-r, ya], [-r, yf + rc], 4)
  bue(-r + rc, yf + rc, rc, Math.PI, 1.5 * Math.PI, 8, true)
  linje([-r + rc, yf], [r - rc, yf], 12)
  bue(r - rc, yf + rc, rc, 1.5 * Math.PI, 2 * Math.PI, 8, true)
  linje([r, yf + rc], [r, ya], 4)
  const ring = d.map(([x, y]) => [s * x, s * y] as Pt)
  const kropp = () => loft([{ z: 0, ring }, { z: v.H, ring }], { vegg: v.vegg })
  const z0 = 14
  const z1 = v.H - 14
  const zs = Array.from({ length: v.fins }, (_, i) => z0 + ((z1 - z0) * i) / (v.fins - 1))
  const plan = (k: Registrert) => {
    const fins = zs.map((z, i) => planVed(k, 1 + i, [0, 0, z], [0, 0, 1]))
    const rib = v.ribber.map((g, i) => radialplate(k, 40 + i, g + (s < 0 ? 180 : 0), [[12, -10], [200, -10], [200, v.H + 10], [12, v.H + 10]], { nett: true }))
    return utanfraa(fins, rib)
  }
  const bag: Partial<Params> = { tjukn: t, material: "bjork", klaring: 0.1, snitt: 0.15, arkB: 600, arkH: 400 }
  const utstyr = (): Utstyr => {
    const matt = { farge: v.farge, ru: 0.8 }
    const messing = { farge: "#b8935a", metall: 1, ru: 0.32 }
    const L = v.stilk
    const opalOmr: Pt[] = [[-r + 6, -v.H / 2 + 2], [r - 6, -v.H / 2 + 2], [r - 6, v.H / 2 - 2], [-r + 6, v.H / 2 - 2]]
    const lokk = (z: number): Ekstra => flatark({ namn: z > 0 ? "lokk" : "botn", punkt: [0, 0, z], n: [0, 0, 1], omriss: ring, tjukn: 2, material: "mdf", farge: v.farge })
    const ekstra: Ekstra[] = [
      flatark({ namn: "opal", punkt: [0, s * (yf - 2), v.H / 2], n: [0, -s, 0], omriss: opalOmr, tjukn: 3, material: "akryl-opal" }),
      lokk(v.H + 1),
      lokk(-1),
    ]
    const delar: NonNullable<Utstyr["delar"]> = {}
    zs.forEach((_, i) => (delar[String(1 + i)] = { material: "mdf", farge: v.farge }))
    v.ribber.forEach((_, i) => (delar[String(40 + i)] = { material: "mdf", farge: v.farge }))
    return {
      utstyr: [
        { slag: "sylinder", senter: [0, 0, -L - 6], diameter: v.fot, lengd: 12, retning: [0, 0, 1], ...matt },
        { slag: "sylinder", senter: [0, 0, -L / 2 - 4], diameter: 9, lengd: L - 8, retning: [0, 0, 1], ...matt },
        { slag: "sylinder", senter: [0, 0, -5], diameter: 22, lengd: 8, retning: [0, 0, 1], ...messing },
        { slag: "boks", senter: [0, s * (ya - 6), v.H / 2], storleik: [10, 12, v.H - 20], ...matt },
        { slag: "leidning", punkt: [[0, v.fot / 2 - 8, -L - 7], [0, v.fot / 2 + 30, -L - 10], [40, v.fot / 2 + 160, -L - 10]], diameter: 4, farge: v.farge },
      ],
      ekstra,
      delar,
      lys: [0.25, 0.5, 0.75].map((f) => ({ punkt: [0, s * (ya - 14), 10 + f * (v.H - 20)] as V3, radius: 5, farge: "#ffc98f", styrke: 1 })),
      ...(v.kamera ? { kamera: v.kamera } : {}),
    } as Utstyr
  }
  const krav = (x: Kontekst) => [
    x.krav("kvar finne og ribbe er ein del", x.liste.length === v.fins + v.ribber.length, `${x.liste.length} delar`),
    x.krav("ingen tapp", x.tappar === 0, `${x.tappar} tappar`),
    x.krav("foten under 200 cm2", (Math.PI * v.fot * v.fot) / 400 <= 200, `${((Math.PI * v.fot * v.fot) / 400).toFixed(0)} cm2`),
  ]
  return { namn: v.namn, kropp, bag, plan, utstyr, krav }
}
