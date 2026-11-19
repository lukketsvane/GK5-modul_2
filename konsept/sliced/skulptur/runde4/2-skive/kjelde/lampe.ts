import { readFileSync } from "node:fs"
import { gitter, type V3 } from "../gitter2"
// foten frå skulptur-07 ber sokkelen, kula står på foten, og hatten er éi tynn opalskive som kviler på kula gjennom eit hol
const STL = new URL("../hatt/fot/lampe.stl", import.meta.url).pathname
const OM: [number, number][] = JSON.parse(readFileSync(new URL("./skive.json", import.meta.url), "utf8")).omriss
const E = (k: string, d: number) => +(process.env[k] ?? d)
const KULE: V3 = [0, 0, 113.5], RK = 47.5, HOL = E("HOL", 15), R = E("R", 420)
const SETE = Math.sqrt(RK * RK - HOL * HOL)
const sirkel = (r: number, n = 48): [number, number][] => Array.from({ length: n }, (_, i) => [r * Math.cos((-2 * Math.PI * i) / n), r * Math.sin((-2 * Math.PI * i) / n)])
// vipp skiva om x-aksen gjennom kulesenteret
const vipp = (g: number) => (p: V3, punkt = true): V3 => {
  const c = Math.cos((g * Math.PI) / 180), s = Math.sin((g * Math.PI) / 180), q: V3 = punkt ? [p[0], p[1] - KULE[1], p[2] - KULE[2]] : p
  const r: V3 = [q[0], q[1] * c - q[2] * s, q[1] * s + q[2] * c]
  return punkt ? [r[0], r[1] + KULE[1], r[2] + KULE[2]] : r
}
const VINKEL = { stemning: 0, skjerm: 20, mote: -20 }
export const lampe = (modus: keyof typeof VINKEL) => {
  const V = vipp(VINKEL[modus])
  return gitter({
    namn: "skive-" + modus, stl: STL, material: "bjork", tjukn: 4, farge: undefined as unknown as string,
    senter: [0, 0, 28],
    fam: [{ n: [1, 0, 0], avstand: 52, tal: 2 }, { n: [0, 1, 0], avstand: 52, tal: 2 }],
    vegg: 300, scene: () => ({ kamera: { helt: { az: 32, el: 8 }, lys: { az: 28, el: 6 }, sprengt: { az: 32, el: 12 } } }),
    // arket bøyer seg om x-aksen: kantane mot deg og mot veggen heng litt ned
    boygde: [{ namn: "skive", senter: V([0, 0, KULE[2] + SETE + 1.5]), u: V([0, 1, 0], false), v: V([1, 0, 0], false), n: V([0, 0, -1], false), omriss: OM.map(([x, y]) => [y, x] as [number, number]), hol: [sirkel(HOL)], R, tjukn: 3, material: "akryl-opal" }],
    utstyr: (P, D) => [
      { slag: "sokkel", senter: P([0, 0, 31]), diameter: 40, lengd: 62, retning: D([0, 0, 1]) },
      { slag: "paere", senter: P(KULE), diameter: 95, lengd: 133, retning: D([0, 0, -1]) },
      { slag: "leidning", punkt: [P([0, 46, 8]), P([10, 80, 4]), P([70, 150, 3]), P([190, 200, 3])], diameter: 5 },
      { slag: "sylinder", senter: P([52, 0, 20]), diameter: 14, lengd: 8, retning: D([1, 0, 0]), farge: "#b8935a", metall: true },
    ],
  })
}
