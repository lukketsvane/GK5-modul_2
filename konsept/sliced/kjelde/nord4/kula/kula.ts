import { dreiRing, type RZ } from "../../verkty/form"
import { plan as planVed, rundt } from "../../verkty/plan"
import type { Kontekst, Params, Registrert, Utstyr } from "../../verkty/typar"

type V3 = [number, number, number]
export type Val = {
  namn: string
  b: number
  ab: number
  af: number
  aF?: number
  p?: number
  bor: number
  vegg?: number
  tjukn?: number
  munn: { fram: boolean; elev: number }
  fot: number
  fotBreidd?: number
  material?: string
  fotMat?: string
  nett?: number[]
  hr?: number
  stativ?: "globus" | "heng"
  farge?: string
  stilk?: number
  vri?: number
  spegl?: boolean
  klaring?: number
  fotH?: number
  messing?: "tappar" | "krune"
  tapphol?: number
  ryPluss?: number
  roeyr?: number
  kule?: number
  kuleS?: number
  knott?: number
  modul?: number
  snor?: number
}

export function nord(v: Val) {
  const p = v.p ?? 2
  const aF = v.aF ?? v.ab
  const k = v.b / 150
  const hr = (v.hr ?? 31) * k
  const ro = (s: number) => {
    const q = 1 - Math.pow(Math.abs(s) / (s < 0 ? aF : v.ab), p)
    return q <= 0 ? 0 : v.b * Math.pow(q, 1 / p)
  }
  const ai = v.ab - (v.vegg ?? 0.39 * v.b)
  const ri = (s: number) => (s <= 0 ? v.bor : v.bor * Math.sqrt(Math.max(0, 1 - (s / ai) ** 2)))
  const sS = ai * Math.sqrt(Math.max(0, 1 - ((hr + 0.05 * v.b) / v.bor) ** 2))
  const zs = sS + v.af
  const zt = zs + 10
  let lo = 0
  let hi = v.ab
  for (let i = 0; i < 50; i++) {
    const m = (lo + hi) / 2
    if (ro(m) > hr) lo = m
    else hi = m
  }
  const sW = lo
  const H = sW + v.af
  const ring: RZ[] = [[v.bor, 0], [ro(-v.af), 0]]
  const N = 90
  for (let i = 1; i <= N; i++) {
    const s = -v.af + ((sW + v.af) * i) / N
    ring.push([i === N ? hr : ro(s), s + v.af])
  }
  ring.push([hr, zt], [5, zt], [5, zs])
  for (let i = 0; i <= 48; i++) {
    const s = sS * (1 - i / 48)
    ring.push([ri(s), s + v.af])
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
      const q = rot([raa[i], raa[i + 1], raa[i + 2] - v.af])
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
    const q = rot([0, 0, z - v.af])
    return [C[0] + q[0], C[1] + q[1], C[2] + q[2]]
  }
  const akse = rot([0, 0, 1])
  const d = (v.nett ?? [-130, -78, -26, 26, 78, 130]).map((x) => x * k)
  const r2 = Math.SQRT1_2
  const vr = ((v.vri ?? 45) * Math.PI) / 180
  const n1 = rot([Math.cos(vr), Math.sin(vr), 0])
  const n2 = rot([-Math.sin(vr), Math.cos(vr), 0])
  const tj = v.tjukn ?? 3
  const kinn = Math.max(...d) + tj / 2
  const tapphol = v.vri === 0 ? (v.tapphol ?? 8) : 0
  const plan = (reg: Registrert) => {
    bygg()
    return [
      ...d.map((x, i) => planVed(reg, 1 + i, [C[0] + n1[0] * x, C[1] + n1[1] * x, C[2] + n1[2] * x], n1, tapphol && (i === 0 || i === d.length - 1) ? { strek: [rundt(reg, "hol", tapphol)] } : {})),
      ...d.map((x, i) => planVed(reg, 21 + i, [C[0] + n2[0] * x, C[1] + n2[1] * x, C[2] + n2[2] * x], n2)),
    ]
  }
  const bag: Partial<Params> = { tjukn: v.tjukn ?? 3, material: v.material ?? "bjork", klaring: v.klaring ?? 0.1, snitt: 0.2, arkB: 600, arkH: 400 }
  const ry = v.b + (v.ryPluss ?? 10)
  const ro2 = v.roeyr ?? 8
  const ytst = ry + ro2 / 2
  const kule = v.kule ?? 104
  const kS = v.kuleS ?? 0
  const heng = v.stativ === "heng"
  const utstyr = (): Utstyr => {
    bygg()
    const fg = v.farge ?? "#b5ad9f"
    const ms = { farge: "#b8935a", metall: 1, ru: 0.32 }
    const matt = { farge: fg, ru: 0.8 }
    const delar: NonNullable<Utstyr["delar"]> = {}
    for (let i = 0; i < d.length; i++) for (const id of [1 + i, 21 + i]) delar[String(id)] = v.spegl ? { material: "spegl", farge: fg, speglSide: d[i] < 0 ? 1 : -1 } : { material: "mdf", farge: fg }
    const modul = [
      { slag: "sylinder" as const, senter: paa((zs - 6 + H) / 2), diameter: v.modul ?? 20, lengd: H - (zs - 6), retning: akse, ...matt },
      { slag: "sylinder" as const, senter: paa(zs - 10 - (zs - 10 - (v.af + kS + kule / 2 - 6)) / 2), diameter: 14, lengd: zs - 10 - (v.af + kS + kule / 2 - 6), retning: akse, farge: "#e9e4da", ru: 0.6 },
      { slag: "paere" as const, senter: paa(v.af + kS), diameter: kule, lengd: kule + 6, retning: akse },
    ]
    const tapp = (side: number) => ({ slag: "sylinder" as const, senter: [C[0] + (side * (kinn + ytst + 2)) / 2, C[1], C[2]] as V3, diameter: 12, lengd: ytst + 2 - kinn, retning: [1, 0, 0] as V3, ...matt })
    const knott = { slag: "sylinder" as const, senter: [C[0] + ytst + 2 + 7, C[1], C[2]] as V3, diameter: v.knott ?? 24, lengd: 14, retning: [1, 0, 0] as V3, ...ms }
    const boge: V3[] = []
    const t0 = heng ? 0 : Math.PI
    for (let i = 0; i <= 32; i++) {
      const t = t0 + (Math.PI * i) / 32
      boge.push([C[0] + ry * Math.cos(t), C[1], C[2] + ry * Math.sin(t)])
    }
    const felles = [...modul, { slag: "leidning" as const, punkt: boge, diameter: ro2, ...matt }, tapp(-1), tapp(1), knott]
    if (heng) {
      const tak = C[2] + ry + (v.snor ?? 520)
      return {
        delar,
        heng: { tak, feste: [C[0], C[1], C[2] + ry + 13], leidning: 3, farge: "#2a2826" },
        utstyr: [...felles, { slag: "sylinder", senter: [C[0], C[1], C[2] + ry + 7], diameter: 12, lengd: 12, retning: [0, 0, 1], ...matt }, { slag: "sylinder", senter: [C[0], C[1], tak - 14], diameter: 110, lengd: 28, retning: [0, 0, 1], ...matt }],
      }
    }
    const stilk = v.stilk ?? 150
    const fotH = v.fotH ?? 14
    const zg = C[2] - ry - stilk - fotH
    const fd = v.fotBreidd ?? 150
    return {
      delar,
      utstyr: [
        ...felles,
        { slag: "sylinder", senter: [C[0], C[1], zg + fotH / 2 - 1], diameter: fd, lengd: fotH - 2, retning: [0, 0, 1], ...matt },
        { slag: "sylinder", senter: [C[0], C[1], zg + fotH - 1], diameter: fd - 4, lengd: 2, retning: [0, 0, 1], ...matt },
        { slag: "sylinder", senter: [C[0], C[1], zg + fotH + 4], diameter: 16, lengd: 8, retning: [0, 0, 1], ...matt },
        { slag: "sylinder", senter: [C[0], C[1], zg + fotH + stilk / 2], diameter: ro2, lengd: stilk, retning: [0, 0, 1], ...matt },
      ],
    }
  }
  const krav = (x: Kontekst) => {
    const golv = heng ? 0 : C[2] - ry - (v.stilk ?? 150) - (v.fotH ?? 14)
    const topp = heng ? C[2] + ry + 13 : C[2] + v.b
    const fotD = v.fotBreidd ?? 150
    const kc = paa(v.af + kS)
    const ka = paa(v.af + kS - 0.1)
    const kb = paa(v.af + kS + 0.1)
    const fri = x.fri(ka, kb)
    const L = (lm: number) => lm / (4 * Math.PI) / (Math.PI * (kule / 2000) ** 2)
    return [
      x.krav("mål med stativ", true, `${heng ? `kule + bøyle ${(topp - (C[2] - v.b)).toFixed(0)} mm · snor ${v.snor ?? 520} mm · takskål ø110` : `høgd ${(topp - golv).toFixed(0)} mm · kulesenter ${(C[2] - golv).toFixed(0)} · fot ø${fotD} = ${((Math.PI * fotD * fotD) / 400).toFixed(0)} cm2`} · bøyle r${ry} · breidd over knotten ${(2 * ytst + 4 + 14).toFixed(0)} · kinn ø${(2 * Math.sqrt(v.b * v.b - Math.max(...d) ** 2)).toFixed(0)}`),
      x.krav(`opal-kula ø${kule} går fri av alle plater (≥ 4 mm)`, fri.mm - kule / 2 >= 4, `${(fri.mm - kule / 2).toFixed(1)} mm luft · senter ${kc.map((q) => q.toFixed(1)).join(", ")} · nærast ${fri.del}`),
      x.krav(`lysmodulen ø${v.modul ?? 20} går fri mellom dei fire midtplatene`, x.fri(paa(zs - 6), paa(H)).mm >= (v.modul ?? 20) / 2 + 0.4, `${x.fri(paa(zs - 6), paa(H)).mm.toFixed(1)} mm frå aksen til næraste plate (${x.fri(paa(zs - 6), paa(H)).del})`),
      x.krav(`opal-kula ø${kule} går inn gjennom munnen ø${2 * v.bor}`, kule + 6 <= 2 * v.bor, ""),
      x.krav("luminans på opalen (lm / 4π / πr²)", true, `350 lm: ${L(350).toFixed(0)} cd/m2 · 60 lm: ${L(60).toFixed(0)} cd/m2`),
      ...[1, d.length].flatMap((id) => [x.holKrav(String(id), tapphol, 0.6, 0.6)]),
    ]
  }
  return { namn: v.namn, kropp: bygg, bag, plan, utstyr, krav }
}
