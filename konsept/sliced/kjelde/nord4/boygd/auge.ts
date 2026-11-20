import { sylinder } from "../../verkty/form"
import { plan as planVed, mm, sirkel, rundt } from "../../verkty/plan"
import { sylinderark } from "../../verkty/ekstra"
import type { Kontekst, Params, Pt, Registrert, Utstyr } from "../../verkty/typar"

type V3 = [number, number, number]
export type Val = { namn: string; vri: number; retning: number; farge: string; R1?: number; R2?: number; H?: number; auge?: number; omlegg?: number }

export function lag(v: Val) {
  const t = 2
  const R1 = v.R1 ?? 64
  const R2 = v.R2 ?? 72
  const H = v.H ?? 230
  const Rb = R2 + t / 2 + 3
  const Ri = R1 + t / 2 + 3
  const zi = H - 6
  const zl = H - 1
  const kropp = () => sylinder(Rb, 0, H, 96)
  const midtI = v.retning
  const midtY = v.retning + v.vri
  const c = v.auge ?? 16
  const e = v.omlegg ?? 4
  const NZ = 10
  const skjel = (k: Registrert, id: number, R: number, midt: number, z0: number, z1: number, rett: number, boge: (z: number) => number) => {
    const m = (midt * Math.PI) / 180
    const n: [number, number, number] = [-Math.cos(m), -Math.sin(m), 0]
    const zm = (z0 + z1) / 2
    const u = (g: number) => (-g * Math.PI * R) / 180
    const zs = Array.from({ length: NZ + 1 }, (_, i) => z0 + ((z1 - z0) * i) / NZ)
    const pts: Pt[] = [[u(rett), z0 - zm], ...zs.map((z) => [u(boge(z)), z - zm] as Pt), [u(rett), z1 - zm]]
    const runde = zs.map((_, i) => i + 1).filter((i) => i > 1 && i < NZ + 1)
    return planVed(k, id, [-R * n[0], -R * n[1], zm], n, { bog: Math.round((k.storleik / R) * 1e4) / 1e4, omriss: mm(k, pts), runde })
  }
  const kurve = (z0: number, z1: number, teikn: number, g0: number) => (z: number) => g0 + teikn * c * Math.sin((Math.PI * (z - z0)) / (z1 - z0))
  const plan = (k: Registrert) => {
    const skive = (id: number, z: number, r: number, hol: number, midt: number, R: number) => {
      const m = (midt * Math.PI) / 180
      return planVed(k, id, [0, 0, z], [0, 0, 1], { ...sirkel(k, r, 24), strek: [...(hol > 0 ? [rundt(k, "hol", hol)] : []), rundt(k, "hol", 6, -R * Math.cos(m), -R * Math.sin(m))] })
    }
    return [
      skive(1, t / 2, Rb, 0, midtI, R1),
      skive(2, zi, Ri, 8, midtI, R1),
      skive(3, zl, Rb, 8, midtY, R2),
      skjel(k, 10, R1, midtI, 0, zi + t / 2, -90 - e, kurve(0, zi + t / 2, -1, 90)),
      skjel(k, 11, R2, midtY, t + 3, H, 90 + e, kurve(t + 3, H, 1, -90)),
    ]
  }
  const bag: Partial<Params> = { tjukn: t, material: "papp", klaring: 0.05, snitt: 0.3, arkB: 600, arkH: 400 }
  const matt = { farge: v.farge, ru: 0.85 }
  const messing = { farge: "#b8935a", metall: 1, ru: 0.3 }
  const utstyr = (): Utstyr => ({
    utstyr: [
      { slag: "sylinder", senter: [0, 0, -8], diameter: 2 * Rb - 24, lengd: 16, retning: [0, 0, 1], ...matt },
      { slag: "sylinder", senter: [0, 0, H + 5], diameter: 24, lengd: 10, retning: [0, 0, 1], ...messing },
      { slag: "sylinder", senter: [0, 0, 14], diameter: 30, lengd: 24, retning: [0, 0, 1], ...matt },
      { slag: "sylinder", senter: [0, 0, zi - 10], diameter: 30, lengd: 16, retning: [0, 0, 1], ...matt },
    ],
    lys: [0.3, 0.55, 0.8].map((f) => ({ punkt: [0, 0, f * zi] as V3, radius: 8, farge: "#ffc98f", styrke: 1 })),
    delar: Object.fromEntries(["1", "2", "3", "10", "11"].map((d) => [d, { material: "mdf", farge: v.farge }])),
    ekstra: [sylinderark({ namn: "opal", R: 15, grader: 360, z0: 26, z1: zi - 18, tjukn: 1.5, material: "akryl-opal" })],
  }) as Utstyr
  const krav = (x: Kontekst) => [
    x.krav("fem delar", x.liste.length === 5, `${x.liste.length} delar`),
    x.krav("skjela sit med tappar", x.tappar >= 4, `${x.tappar} tappar`),
    x.krav("fot under 200 cm2", (Math.PI * Rb * Rb) / 100 <= 200, `ø${2 * Rb} = ${((Math.PI * Rb * Rb) / 100).toFixed(0)} cm2`),
    x.krav("opninga", true, v.vri === 180 ? `auge ${2 * c}° breitt midt på, lukka i endane, mot ${v.retning + 90}°` : `ytre skjel snudd ${v.vri}° · indre midt ${v.retning}°`),
  ]
  return { namn: v.namn, kropp, bag, plan, utstyr, krav }
}
