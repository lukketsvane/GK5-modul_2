import { dreiRing, type RZ } from "../../verkty/form"
import { plan as planVed, rundt } from "../../verkty/plan"
import { sylinderark } from "../../verkty/ekstra"
import type { Kontekst, Params, Registrert, Utstyr } from "../../verkty/typar"

type V3 = [number, number, number]
export type Val = {
  namn: string
  form: "skaal" | "kjegle"
  munn: { fram: boolean; elev: number }
  b: number
  bor?: number
  af?: number
  rc?: number
  hc?: number
  vegg?: number
  hr?: number
  lomme?: number
  nett: number[]
  vri?: number
  tjukn?: number
  material?: string
  klaring?: number
  farge: string
  spegl?: boolean
  ringR?: number
  hogd: number
  fotD?: number
  fotH?: number
  kule?: number
  roeyr?: number
}

export function fri(v: Val) {
  const skaal = v.form === "skaal"
  const b = v.b
  const af = skaal ? (v.af ?? 14) : 0
  const bor = v.bor ?? 55
  const rc = v.rc ?? 34
  const hc = v.hc ?? 150
  const vegg = v.vegg ?? 26
  const hr = v.hr ?? 18.6
  const zt = hc - (v.lomme ?? 28)
  const zs = zt - 10
  const ro = (z: number) => b - ((b - rc) * z) / hc
  const zTopp = skaal ? af + Math.sqrt(b * b - 25) : hc
  const ring: RZ[] = []
  if (skaal) {
    ring.push([bor, 0], [Math.sqrt(b * b - af * af), 0])
    const t0 = Math.asin(-af / b)
    const t1 = Math.acos(5 / b)
    for (let i = 1; i <= 60; i++) {
      const t = t0 + ((t1 - t0) * i) / 60
      ring.push([i === 60 ? 5 : b * Math.cos(t), af + b * Math.sin(t)])
    }
    const u1 = Math.acos(5 / bor)
    for (let i = 0; i <= 40; i++) {
      const t = u1 * (1 - i / 40)
      ring.push([i === 0 ? 5 : bor * Math.cos(t), af + bor * Math.sin(t)])
    }
  } else {
    ring.push([b - vegg, 0])
    for (let i = 0; i <= 12; i++) ring.push([ro((hc * i) / 12), (hc * i) / 12])
    ring.push([hr, hc], [hr, zt], [5, zt], [5, zs])
    for (let i = 0; i < 10; i++) ring.push([ro(zs * (1 - i / 10)) - vegg, zs * (1 - i / 10)])
  }
  const al = (v.munn.elev * Math.PI) / 180
  const sg = v.munn.fram ? -Math.cos(al) : Math.cos(al)
  const cg = -Math.sin(al)
  const rot = (q: V3): V3 => [q[0], q[1] * cg - q[2] * sg, q[1] * sg + q[2] * cg]
  let C: V3 = [0, 0, 0]
  let nett: Float32Array | null = null
  const bygg = () => {
    if (nett) return nett
    const raa = dreiRing(ring, 112)
    const ut = new Float32Array(raa.length)
    const mn: V3 = [Infinity, Infinity, Infinity]
    const mx: V3 = [-Infinity, -Infinity, -Infinity]
    for (let i = 0; i < raa.length; i += 3) {
      const q = rot([raa[i], raa[i + 1], raa[i + 2] - af])
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
  const paa = (z: number): V3 => {
    const q = rot([0, 0, z - af])
    return [C[0] + q[0], C[1] + q[1], C[2] + q[2]]
  }
  const akse = rot([0, 0, 1])
  const d = v.nett
  const vr = ((v.vri ?? 0) * Math.PI) / 180
  const n1 = rot([Math.cos(vr), Math.sin(vr), 0])
  const n2 = rot([-Math.sin(vr), Math.cos(vr), 0])
  const tj = v.tjukn ?? 3
  const kinn = Math.max(...d) + tj / 2
  const tapphol = skaal ? 8 : 0
  const plan = (reg: Registrert) => {
    bygg()
    return [
      ...d.map((x, i) => planVed(reg, 1 + i, [C[0] + n1[0] * x, C[1] + n1[1] * x, C[2] + n1[2] * x], n1, tapphol && (i === 0 || i === d.length - 1) ? { strek: [rundt(reg, "hol", tapphol)] } : {})),
      ...d.map((x, i) => planVed(reg, 21 + i, [C[0] + n2[0] * x, C[1] + n2[1] * x, C[2] + n2[2] * x], n2)),
    ]
  }
  const bag: Partial<Params> = { tjukn: tj, material: v.material ?? "akryl", klaring: v.klaring ?? 0.15, snitt: 0.2, arkB: 600, arkH: 400 }
  const fotD = v.fotD ?? 150
  const fotH = v.fotH ?? 10
  const roeyr = v.roeyr ?? 8
  const ringR = v.ringR ?? 48
  const kule = v.kule ?? 80
  const opp = akse[2] < 0
  const sete = opp ? ((b - ringR + roeyr / 2) * hc) / (b - rc) : ((b - vegg - ringR - roeyr / 2) * hc) / (b - rc)
  const armX = -(b + 16)
  const maal = () => {
    bygg()
    const ringZ = paa(sete)[2]
    const golv = skaal ? C[2] - v.hogd : ringZ - v.hogd
    const topp = skaal ? C[2] + b : Math.max(paa(0)[2], paa(hc + 11)[2])
    const botn = skaal ? C[2] - b : Math.min(paa(0)[2], paa(hc + 11)[2])
    return { ringZ, golv, topp, botn }
  }
  const utstyr = (): Utstyr => {
    const { ringZ, golv } = maal()
    const ms = { farge: "#b8935a", metall: 1, ru: 0.35 }
    const matt = { farge: v.farge, ru: 0.8 }
    const delar: NonNullable<Utstyr["delar"]> = {}
    for (let i = 0; i < d.length; i++) for (const id of [1 + i, 21 + i]) delar[String(id)] = v.spegl ? { material: "spegl", farge: v.farge, speglSide: d[i] < 0 ? 1 : -1 } : { material: "mdf", farge: v.farge }
    const syl = (a: V3, e: V3, diameter: number, mat: object) => {
      const l = Math.hypot(e[0] - a[0], e[1] - a[1], e[2] - a[2])
      return { slag: "sylinder" as const, senter: [(a[0] + e[0]) / 2, (a[1] + e[1]) / 2, (a[2] + e[2]) / 2] as V3, diameter, lengd: l, retning: [(e[0] - a[0]) / l, (e[1] - a[1]) / l, (e[2] - a[2]) / l] as V3, ...mat }
    }
    if (skaal) {
      const x0 = C[0] + armX
      const fx = x0 + fotD / 2 - 20
      const rb = 22
      const line: V3[] = []
      for (let i = 0; i <= 8; i++) line.push([x0, C[1], golv + fotH + ((C[2] - rb - golv - fotH) * i) / 8])
      for (let i = 1; i <= 8; i++) line.push([x0 + rb - rb * Math.cos((i * Math.PI) / 16), C[1], C[2] - rb + rb * Math.sin((i * Math.PI) / 16)])
      for (let i = 1; i <= 4; i++) line.push([x0 + rb + ((C[0] - kule / 2 + 2 - x0 - rb) * i) / 4, C[1], C[2]])
      return {
        delar,
        utstyr: [
          { slag: "paere", senter: [C[0], C[1], C[2]], diameter: kule, lengd: kule + 4, retning: [-1, 0, 0] },
          { slag: "leidning", punkt: line, diameter: roeyr, ...matt },
          syl([C[0] + kule / 2 - 2, C[1], C[2]], [C[0] + kinn + 3, C[1], C[2]], roeyr, matt),
          syl([C[0] + kinn + 3, C[1], C[2]], [C[0] + kinn + 16, C[1], C[2]], 22, ms),
          syl([fx, C[1], golv], [fx, C[1], golv + fotH], fotD, matt),
          syl(paa(zTopp - 2), paa(zTopp + 0.6), 14, matt),
        ],
      }
    }
    const lk = 30
    const sirkel: V3[] = []
    for (let i = 0; i <= 36; i++) sirkel.push([C[0] + ringR * Math.cos((i * Math.PI) / 18 + Math.PI / 2), C[1] + ringR * Math.sin((i * Math.PI) / 18 + Math.PI / 2), ringZ])
    const za = paa(zs)[2]
    const zb = paa(zs - 56)[2]
    return {
      delar,
      ekstra: [sylinderark({ namn: "opal", R: 20, grader: 360, z0: Math.min(za, zb), z1: Math.max(za, zb), tjukn: 2, senter: [C[0], C[1]], material: "akryl-opal" })],
      utstyr: [
        syl(paa(zs - 8), paa(hc), 2 * hr - 2.4, matt),
        syl(paa(hc), paa(hc + 11), 2 * hr - 4, ms),
        { slag: "paere", senter: paa(zs - 10 - (lk + 12) / 2), diameter: lk, lengd: lk + 12, retning: akse },
        { slag: "leidning", punkt: sirkel, diameter: roeyr, ...matt },
        syl([C[0], C[1] + ringR + 1, golv + fotH], [C[0], C[1] + ringR + 1, ringZ], roeyr, matt),
        syl([C[0], C[1], golv], [C[0], C[1], golv + fotH], fotD, matt),
      ],
    }
  }
  const krav = (x: Kontekst) => {
    const { ringZ, golv, topp, botn } = maal()
    const fot = `fot ø${fotD} = ${((Math.PI * fotD * fotD) / 400).toFixed(0)} cm2`
    if (!skaal) return [x.krav("mål med stativ", botn > golv + fotH, `høgd ${(topp - golv).toFixed(0)} mm · ring ø${2 * ringR} ${(ringZ - golv).toFixed(0)} mm over bordet · hovud frå ${(botn - golv).toFixed(0)} til ${(topp - golv).toFixed(0)} mm · munn ø${2 * b} · sete ${sete.toFixed(0)} mm frå munnen · ${fot}`)]
    const m = x.krav("mål med stativ", true, `høgd ${(topp - golv).toFixed(0)} mm · kulesenter ${(C[2] - golv).toFixed(0)} mm over bordet · skål ø${2 * b} · opal kule ø${kule} · breidd arm til knott ${(kinn + 16 - armX + roeyr / 2).toFixed(0)} mm · ${fot}`)
    return [m, ...[1, d.length].flatMap((id) => {
      const h = x.hol(String(id))
      return [x.holKrav(String(id), tapphol, 0.6, 0.6), x.krav(`akselhol i del ${id}`, h.length === 1, `${h.length} hol · ${JSON.stringify(h[0] ?? null).slice(0, 140)}`)]
    })]
  }
  return { namn: v.namn, kropp: bygg, bag, plan, utstyr, krav }
}
