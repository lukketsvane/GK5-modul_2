import { dreiRing, type RZ } from "../../verkty/form"
import { plan as planVed, rundt } from "../../verkty/plan"
import { flatark } from "../../verkty/ekstra"
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
  stativ?: "bukk" | "globus"
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
  const fotplate = (grad: number, opp: boolean) => {
    bygg()
    const h = (grad * Math.PI) / 180
    const n: V3 = [-Math.sin(h), Math.cos(h), 0]
    const rho = v.b + 0.5
    const cz = v.munn.elev <= -89 ? v.af : v.b
    const golv = cz - v.b - v.fot
    const uf = (v.fotBreidd ?? 180) / 2
    const P = (grad2: number, r: number): [number, number] => [r * Math.sin((grad2 * Math.PI) / 180), cz - r * Math.cos((grad2 * Math.PI) / 180)]
    const t1 = 58
    const t2 = 30
    const z0 = cz - rho
    const apex = z0 - 14
    const zm = (z0 + apex) / 2
    const sp = ((v.tjukn ?? 3) + 0.1) / 2
    const sete: [number, number][] = []
    for (let g = -t1; g <= t1 + 0.01; g += 4) {
      const q = P(g, rho)
      if (Math.abs(q[0]) > sp + 0.5) sete.push(q)
      else if (opp && sete[sete.length - 1][0] < 0) sete.push([-sp, z0], [-sp, zm], [sp, zm], [sp, z0])
    }
    const hogre: [number, number][] = []
    for (let g = t1; g >= t2 - 0.01; g -= 4) hogre.push(P(g, rho + 5 + (9 * (t1 - g)) / (t1 - t2)))
    const p2 = hogre[hogre.length - 1]
    for (let i = 1; i <= 16; i++) {
      const t = i / 16
      hogre.push([p2[0] + (uf - p2[0]) * Math.pow(t, 1.6), p2[1] + (golv - p2[1]) * t])
    }
    hogre.push([uf - 12, golv])
    const boge: [number, number][] = []
    for (let i = 1; i < 24; i++) {
      const f = (i / 24) * (Math.PI / 2)
      boge.push([(uf - 12) * Math.pow(Math.cos(f), 0.75), golv + (apex - golv) * Math.pow(Math.sin(f), 0.75)])
    }
    const topp: [number, number][] = opp ? [[0, apex]] : [[sp, apex], [sp, zm], [-sp, zm], [-sp, apex]]
    const venstre = [...hogre, ...boge].map((q) => [-q[0], q[1]] as [number, number]).reverse()
    const omriss: [number, number][] = [...sete, ...hogre, ...boge, ...topp, ...venstre]
    return flatark({ namn: opp ? "bukk1" : "bukk2", punkt: [C[0], C[1], 0], n, omriss, tjukn: v.tjukn ?? 3, material: v.fotMat ?? "bjork" })
  }
  const utstyr = (): Utstyr => {
    bygg()
    const lk = 0.34 * v.b
    const kjerne = [
      { slag: "sylinder" as const, senter: paa((zs - 8 + H + 4) / 2), diameter: 2 * hr - 12 * k, lengd: H + 4 - (zs - 8), retning: akse, farge: "#26272a" },
      { slag: "paere" as const, senter: paa(zs - 10 - (lk + 12) / 2), diameter: lk, lengd: lk + 12, retning: akse },
    ]
    const delar: NonNullable<Utstyr["delar"]> = {}
    if (v.farge) for (let i = 0; i < d.length; i++) for (const id of [1 + i, 21 + i]) delar[String(id)] = v.spegl ? { material: "spegl", farge: v.farge, speglSide: d[i] < 0 ? 1 : -1 } : { material: "mdf", farge: v.farge }
    if (v.stativ !== "globus") return { utstyr: kjerne, ekstra: [fotplate(45, true), fotplate(135, false)], delar }
    const ry = v.b + (v.ryPluss ?? 10)
    const stilk = v.stilk ?? 130
    const fotH = v.fotH ?? 12
    const ro = v.roeyr ?? 8
    const zg = C[2] - ry - stilk - fotH
    const fg = v.farge ?? "#2b2b2b"
    const ms = { farge: "#b8935a", metall: 1, ru: 0.35 }
    const matt = { farge: fg, ru: 0.8 }
    const boge: V3[] = []
    for (let i = 0; i <= 28; i++) {
      const t = Math.PI + (Math.PI * i) / 28
      boge.push([C[0] + ry * Math.cos(t), C[1], C[2] + ry * Math.sin(t)])
    }
    const krune = v.messing === "krune"
    const ytst = ry + ro / 2
    const tapp = (side: number, dia: number, ut: number, mat: { farge: string; ru: number; metall?: number }) => ({ slag: "sylinder" as const, senter: [C[0] + (side * (kinn + ytst + ut)) / 2, C[1], C[2]] as V3, diameter: dia, lengd: ytst + ut - kinn, retning: [1, 0, 0] as V3, ...mat })
    const modul = [
      { slag: "sylinder" as const, senter: paa((zs - 8 + H) / 2), diameter: 2 * hr - 4 * k, lengd: H - (zs - 8), retning: akse, ...matt },
      krune
        ? { slag: "sylinder" as const, senter: paa(H + 5), diameter: 2 * hr - 4, lengd: 12, retning: akse, ...ms }
        : { slag: "sylinder" as const, senter: paa(H + 1), diameter: 2 * hr + 6 * k, lengd: 3, retning: akse, ...matt },
      kjerne[1],
    ]
    return {
      delar,
      utstyr: [
        ...modul,
        { slag: "sylinder", senter: [C[0], C[1], zg + fotH / 2], diameter: v.fotBreidd ?? 150, lengd: fotH, retning: [0, 0, 1], ...matt },
        { slag: "sylinder", senter: [C[0], C[1], zg + fotH + stilk / 2], diameter: ro, lengd: stilk, retning: [0, 0, 1], ...matt },
        { slag: "leidning", punkt: boge, diameter: ro, ...matt },
        ...(krune ? [tapp(-1, 12, 2, matt), tapp(1, 12, 2, matt)] : [tapp(-1, 12, 2, ms), tapp(1, 12, 1, ms), { slag: "sylinder" as const, senter: [C[0] + ytst + 7.5, C[1], C[2]] as V3, diameter: 22, lengd: 13, retning: [1, 0, 0] as V3, ...ms }]),
      ],
    }
  }
  const krav = (x: Kontekst) => {
    const ry = v.b + (v.ryPluss ?? 10)
    const fotD = v.fotBreidd ?? 150
    const krune = v.messing === "krune"
    const golv = C[2] - ry - (v.stilk ?? 130) - (v.fotH ?? 12)
    const topp = Math.max(C[2] + v.b, krune ? paa(H + 11)[2] + (hr - 2) * Math.hypot(akse[0], akse[1]) : paa(H + 2.5)[2])
    const ytst = ry + (v.roeyr ?? 8) / 2
    const maal = x.krav("mål med stativ", true, `høgd ${(topp - golv).toFixed(0)} mm · kulesenter ${(C[2] - golv).toFixed(0)} mm over bordet · fot ø${fotD} = ${((Math.PI * fotD * fotD) / 400).toFixed(0)} cm2 · breidd over tappane ${(krune ? 2 * (ytst + 2) : 2 * ytst + 2 + 14).toFixed(0)} mm · kinn ø${(2 * Math.sqrt(v.b * v.b - Math.max(...d) ** 2)).toFixed(0)}`)
    if (!tapphol) return [maal]
    return [maal, ...[1, d.length].flatMap((id, j) => {
      const h = x.hol(String(id))
      const pkt = [C[0] + n1[0] * d[j ? d.length - 1 : 0], C[1], C[2]]
      return [x.holKrav(String(id), tapphol, 0.6, 0.6), x.krav(`tapphol i del ${id} ligg på vippeaksen`, h.length === 1, `${h.length} hol · akse ${pkt.map((q) => q.toFixed(1)).join(", ")} · ${JSON.stringify(h[0] ?? null).slice(0, 160)}`)]
    })]
  }
  return { namn: v.namn, kropp: bygg, bag, plan, utstyr, krav }
}
