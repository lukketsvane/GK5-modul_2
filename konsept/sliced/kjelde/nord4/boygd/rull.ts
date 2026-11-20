import { boks } from "../../verkty/form"
import { plan as planVed, mm, sirkel, rundt } from "../../verkty/plan"
import type { Ekstra } from "../../verkty/ekstra"
import type { Kontekst, Params, Pt, Registrert, Utstyr } from "../../verkty/typar"

type V3 = [number, number, number]
export type Val = { namn: string; opning: number; midt?: number; synleg?: boolean; retning: number; farge: string; L?: number; R?: number; kant?: number; hogd?: number; fot?: number }

const rad = (g: number) => (g * Math.PI) / 180

const roeyrY = (namn: string, R: number, y0: number, y1: number, zA: number, tjukn: number): Ekstra => {
  const a = Math.PI * R
  const h = (y1 - y0) / 2
  const ym = (y0 + y1) / 2
  const o: V3 = [0, ym, zA + R]
  const n: V3 = [0, 0, -1]
  return { namn, tjukn, omriss: [[-a, -h], [a, -h], [a, h], [-a, h]], hol: [], matrise: [-1, 0, 0, 0, 0, 1, 0, 0, ...n, 0, o[0], o[1], o[2] + tjukn / 2, 1], krumming: 1 / R, material: "akryl-opal" }
}

export function lag(v: Val) {
  const t = 2
  const L = v.L ?? 300
  const R = v.R ?? 78
  const Rk = R + t / 2 + (v.kant ?? 7)
  const zA = Rk
  const hogd = v.hogd ?? 400
  const zT = zA - hogd
  const fot = v.fot ?? 150
  const oM = v.midt ?? v.opning
  const aV = (y: number) => ((360 - (v.opning + (oM - v.opning) * Math.cos((Math.PI * y) / L))) / 360) * Math.PI * R
  const NY = 10
  const ys = Array.from({ length: NY + 1 }, (_, i) => -L / 2 + (L * i) / NY)
  const opp = Math.abs(((v.retning % 360) + 360) % 360 - 180) < 90
  const kropp = () => boks(2 * Rk, L, 2 * Rk)
  const yk = L / 2 - t / 2
  const plan = (k: Registrert) => {
    const bog = Math.round((k.storleik / R) * 1e4) / 1e4
    const s = opp ? -rad(v.retning - 180) * R : rad(v.retning) * R
    const pts: Pt[] = [...ys.map((y) => [aV(y) + s, y] as Pt), ...ys.slice().reverse().map((y) => [-aV(y) + s, y] as Pt)]
    const runde = pts.map((_, i) => i).filter((i) => i % (NY + 1) !== 0 && i % (NY + 1) !== NY)
    const hette = opp
      ? planVed(k, 10, [0, 0, zA - R], [0, 0, 1], { bog, omriss: mm(k, pts), runde })
      : planVed(k, 10, [0, 0, zA + R], [0, 0, -1], { bog, omriss: mm(k, pts), runde })
    const kinn = (id: number, y: number) => planVed(k, id, [0, y, zA], [0, 1, 0], { ...sirkel(k, Rk, 24), strek: [rundt(k, "hol", 10), rundt(k, "hol", 6, 0, opp ? R : -R)] })
    return [kinn(1, -yk), kinn(2, yk), hette]
  }
  const bag: Partial<Params> = { tjukn: t, material: "papp", klaring: 0.05, snitt: 0.3, arkB: 600, arkH: 400 }
  const matt = { farge: v.farge, ru: 0.85 }
  const messing = { farge: "#b8935a", metall: 1, ru: 0.3 }
  const yB = L / 2 + 14
  const zY = zA - Rk - 30
  const utstyr = (): Utstyr => {
    const boyle: V3[] = [
      [0, -yB, zA], [0, -yB, zA - 40], [0, -yB, zY + 28], [0, -yB + 8.2, zY + 8.2], [0, -yB + 28, zY], [0, -yB + 70, zY], [0, 0, zY],
      [0, yB - 70, zY], [0, yB - 28, zY], [0, yB - 8.2, zY + 8.2], [0, yB, zY + 28], [0, yB, zA - 40], [0, yB, zA],
    ]
    const stamme = zY - (zT + 10)
    return {
      utstyr: [
        { slag: "sylinder", senter: [0, 0, zT + 5], diameter: fot, lengd: 10, retning: [0, 0, 1], ...matt },
        { slag: "sylinder", senter: [0, 0, zT + 10 + stamme / 2], diameter: 12, lengd: stamme, retning: [0, 0, 1], ...matt },
        { slag: "leidning", punkt: boyle, diameter: 10, ...matt },
        { slag: "sylinder", senter: [0, -(L / 2 + 6), zA], diameter: 18, lengd: 12, retning: [0, 1, 0], ...matt },
        { slag: "sylinder", senter: [0, L / 2 + 6, zA], diameter: 18, lengd: 12, retning: [0, 1, 0], ...matt },
        { slag: "sylinder", senter: [0, yB + 13, zA], diameter: 28, lengd: 16, retning: [0, 1, 0], ...messing },
        { slag: "leidning", punkt: [[fot / 2 - 10, 0, zT + 3], [fot / 2 + 30, 0, zT + 2], [fot / 2 + 200, 40, zT + 2]], diameter: 4, farge: v.farge },
      ],
      lys: [-0.3, 0, 0.3].map((f) => ({ punkt: [0, f * L, zA] as V3, radius: 10, farge: "#ffc98f", styrke: 1 })),
      delar: { "1": { material: "mdf", farge: v.farge }, "2": { material: "mdf", farge: v.farge }, "10": { material: "mdf", farge: v.farge } },
      ekstra: [roeyrY("opal", 16, -(L / 2 - t - 2), L / 2 - t - 2, zA, 1.5)],
    } as Utstyr
  }
  const o2 = Math.max(v.opning, oM) / 2
  const auge = [250, 600].map((h) => 90 + (Math.atan2(h - hogd, 600) * 180) / Math.PI)
  const th = ((v.retning % 360) + 360) % 360
  const inne = (f: number) => Math.abs(((f - th + 540) % 360) - 180) < o2
  const gøymd = !inne(auge[0]) && !inne(auge[1]) && !inne((auge[0] + auge[1]) / 2)
  const krav = (x: Kontekst) => [
    x.krav("tre delar", x.liste.length === 3, `${x.liste.length} delar`),
    x.krav("hetta sit med tappar i begge kinn", x.tappar >= 4, `${x.tappar} tappar`),
    x.krav("fot under 200 cm2", (Math.PI * fot * fot) / 400 <= 200, `ø${fot} = ${((Math.PI * fot * fot) / 400).toFixed(0)} cm2`),
    x.krav(v.synleg ? "opalen synleg med vilje (møtelys)" : "opalen gøymd for auge 250..600 mm over bordet, 600 mm unna", v.synleg ? true : gøymd, `opning ${v.opning}..${oM}° mot ${th}° · auga ser frå ${auge[0].toFixed(0)}..${auge[1].toFixed(0)}° · ${gøymd ? "gøymd" : "synleg"} · akse ${hogd} mm over bordet`),
  ]
  return { namn: v.namn, kropp, bag, plan, utstyr, krav }
}
