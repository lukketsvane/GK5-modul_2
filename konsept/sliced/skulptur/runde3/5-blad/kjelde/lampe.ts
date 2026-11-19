import { readFileSync } from "node:fs"
import { gitter, pose, rotZ, type V3 } from "../gitter2"
const STL = new URL("./lampe.stl", import.meta.url).pathname
const B = JSON.parse(readFileSync(new URL("./blad.json", import.meta.url), "utf8"))
const TOPP: V3 = [0, 0, B.topp]
const E = (k: string, d: number) => +(process.env[k] ?? d)
// vipp bladet om lengdeaksen (kroppen sin y) gjennom toppen av lykta
const vipp = (g: number) => (p: V3, punkt = true): V3 => {
  const c = Math.cos((g * Math.PI) / 180), s = Math.sin((g * Math.PI) / 180), q: V3 = punkt ? [p[0] - TOPP[0], p[1], p[2] - TOPP[2]] : p
  const r: V3 = [q[0] * c + q[2] * s, q[1], -q[0] * s + q[2] * c]
  return punkt ? [r[0] + TOPP[0], r[1], r[2] + TOPP[2]] : r
}
// stemning = bladet ligg som i forma. mote = kanten mot deg ned, oversida lyser mot ansiktet. arbeid = kanten mot deg opp.
const VINKEL = { stemning: 0, mote: 19, arbeid: -9 }
export const lampe = (modus: keyof typeof VINKEL) => {
  const V = vipp(VINKEL[modus])
  return gitter({
    namn: "blad-" + modus, stl: STL, pose: pose(rotZ(-90)), material: "bjork", tjukn: 4, farge: undefined as unknown as string,
    senter: [0, 0, 59],
    fam: [{ n: [1, 0, 0], avstand: E("A1", 28), tal: 2, skift: E("S1", 0) }, { n: [0, 1, 0], avstand: E("A2", 28), tal: 2, skift: E("S2", 0) }],
    vegg: 260, scene: () => ({ kamera: { helt: { az: 32, el: 7 }, lys: { az: 28, el: 5 }, sprengt: { az: 32, el: 12 } } }), fjern: (process.env.FJERN ?? "").split(",").filter(Boolean).map(Number),
    boygde: [{ namn: "blad", senter: V(B.senter), u: V(B.u, false), v: V(B.v, false), n: V(B.n, false), omriss: B.omriss, R: B.Rtvers, tjukn: 3, material: "akryl-opal" }],
    utstyr: (P, D) => [
      { slag: "sokkel", senter: P([0, 0, 22.5]), diameter: 28, lengd: 45, retning: D([0, 0, 1]) },
      { slag: "paere", senter: P([0, 0, 82.5]), diameter: 45, lengd: 83, retning: D([0, 0, -1]) },
      { slag: "leidning", punkt: [P([-38, 0, 6]), P([-70, 10, 3]), P([-130, 60, 3]), P([-170, 170, 3])], diameter: 5 },
      { slag: "sylinder", senter: P([0, 42, 18]), diameter: 14, lengd: 8, retning: D([0, 1, 0]), farge: "#b8935a", metall: true },
    ],
  })
}
