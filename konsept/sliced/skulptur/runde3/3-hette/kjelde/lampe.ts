import { gitter, type V3 } from "../gitter2"
const STL = new URL("./lampe.stl", import.meta.url).pathname
const E = (k: string, d: number) => +(process.env[k] ?? d)
const KULE: V3 = [0, -30.5, 115]
// stemning = opninga mot deg, du ser kula i kvelven. arbeid = dreidd 180, skottet skjuler kula og lyset går via vegg og bord.
export const lampe = (modus: "stemning" | "arbeid") => gitter({
  namn: "hette-" + modus, stl: STL, snudd: modus === "arbeid", material: "bjork", tjukn: 4, farge: undefined as unknown as string,
  fam: [{ n: [0, 1, 0], avstand: E("A1", 26), tal: E("T1", 12), skift: E("S1", 3.5) }, { n: [1, 0, 0], avstand: E("A2", 68), tal: E("T2", 2), skift: E("S2", 0) }],
  vegg: 290, senter: [0, 0, 95], fjern: (process.env.FJERN ?? "12").split(",").filter(Boolean).map(Number),
  utstyr: (P, D) => [
    { slag: "sokkel", senter: P([0, 54, 115]), diameter: 40, lengd: 62, retning: D([0, 1, 0]) },
    { slag: "paere", senter: P(KULE), diameter: 95, lengd: 133, retning: D([0, 1, 0]) },
    { slag: "leidning", punkt: [P([0, 96, 36]), P([0, 144, 24]), P([12, 190, 5]), P([90, 250, 3]), P([220, 280, 3])], diameter: 5 },
    { slag: "sylinder", senter: P([0, 88, 115]), diameter: 46, lengd: 6, retning: D([0, 1, 0]), farge: "#b8935a", metall: true },
  ],
})
