import { gitter, type V3 } from "../gitter2"
const STL = new URL("./lampe.stl", import.meta.url).pathname
const E = (k: string, d: number) => +(process.env[k] ?? d)
const KULE: V3 = [0, -30, 136]
// stemning = kula i fanget vender mot deg. arbeid = ryggen mot deg, alt lyset går via veggen.
export const lampe = (modus: "stemning" | "arbeid") => gitter({
  namn: "kove-" + modus, stl: STL, snudd: modus === "arbeid", material: "bjork", tjukn: 4, farge: undefined as unknown as string,
  fam: [{ n: [1, 0, 0], avstand: 24, tal: 6, skift: E("S1", 0) }, { n: [0, 1, 0], avstand: 74, tal: 3, skift: E("S2", -2) }],
  vegg: 250, fjern: (process.env.FJERN ?? "").split(",").filter(Boolean).map(Number),
  utstyr: (P, D) => [
    { slag: "sokkel", senter: P([KULE[0], KULE[1], 57]), diameter: 40, lengd: 62, retning: D([0, 0, 1]) },
    { slag: "paere", senter: P(KULE), diameter: 95, lengd: 133, retning: D([0, 0, -1]) },
    { slag: "leidning", punkt: [P([0, 99, 34]), P([10, 135, 30]), P([70, 190, 29]), P([190, 230, 29])], diameter: 5 },
    { slag: "sylinder", senter: P([0, 66, 291]), diameter: 18, lengd: 8, retning: D([0, 0, 1]), farge: "#b8935a", metall: true },
  ],
})
