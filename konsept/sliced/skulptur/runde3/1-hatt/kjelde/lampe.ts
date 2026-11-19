import { gitter, type V3 } from "../gitter2"
const E = (k: string, d: number) => +(process.env[k] ?? d)
const fil = (n: string) => new URL(`./${n}/lampe.stl`, import.meta.url).pathname
export const KULE: V3 = [0, 0, 113.5], LYFT = 53
const felles = { material: "bjork", tjukn: 4, farge: undefined as unknown as string, vegg: 300, fjern: (process.env.FJERN ?? "").split(",").filter(Boolean).map(Number) }
// foten ber sokkelen, kula står på foten, hatten kviler på kula og kan vippast om x-aksen
export const fot = () => gitter({
  ...felles, namn: "hatt-fot", stl: fil("fot"), senter: [0, 0, 28],
  fam: [{ n: [1, 0, 0], avstand: E("A1", 52), tal: 2 }, { n: [0, 1, 0], avstand: E("A2", 52), tal: 2 }],
  utstyr: (P, D) => [
    { slag: "sokkel", senter: P([0, 0, 31]), diameter: 40, lengd: 62, retning: D([0, 0, 1]) },
    { slag: "paere", senter: P(KULE), diameter: 95, lengd: 133, retning: D([0, 0, -1]) },
    { slag: "leidning", punkt: [P([0, 46, 8]), P([10, 80, 4]), P([70, 150, 3]), P([190, 200, 3])], diameter: 5 },
    { slag: "sylinder", senter: P([52, 0, 20]), diameter: 16, lengd: 8, retning: D([1, 0, 0]), farge: "#b8935a", metall: true },
  ],
})
export const topp = () => gitter({
  ...felles, namn: "hatt-topp", stl: fil("topp"), senter: [0, 0, 88],
  fam: [{ n: [0, 1, 0], avstand: E("B1", 26), tal: E("T1", 11), skift: E("S1", 0) }, { n: [1, 0, 0], avstand: 0, tal: 4, stader: [-E("R2", 85), -E("R1", 20), E("R1", 20), E("R2", 85)] }],
})
