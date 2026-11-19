import { gitter, type V3 } from "../gitter2"
// skulptur-09: to vinklar ber eit bøygd opalark frå tåa til toppen av ryggen. Kula står gøymd i tunnelen bak arket.
const STL = new URL("./lampe.stl", import.meta.url).pathname
const E = (k: string, d: number) => +(process.env[k] ?? d)
const R = 240, YC = -200, ZC = 285, F0 = (-64.5 * Math.PI) / 180, F1 = (2 * Math.PI) / 180, FM = (F0 + F1) / 2, a = (R * (F1 - F0)) / 2, B = 67.5, hj = 14
const rund = (): [number, number][] => {
  const p: [number, number][] = []
  const bue = (cx: number, cy: number, a0: number) => { for (let i = 0; i <= 8; i++) { const t = a0 + (i / 8) * (Math.PI / 2); p.push([cx + hj * Math.cos(t), cy + hj * Math.sin(t)]) } }
  bue(-a + hj, -B + hj, Math.PI); bue(a - hj, -B + hj, 1.5 * Math.PI); bue(a - hj, B - hj, 0); bue(-a + hj, B - hj, 0.5 * Math.PI)
  return p
}
const KULE: V3 = [0, -6, 118.5]
// kula stikk så vidt gjennom eit rundt hol i arket
const FG = Math.atan2(KULE[2] - ZC, KULE[1] - YC), HOLU = R * (FM - FG), HOLR = 17
const sirkel = (cu: number, r: number, n = 40): [number, number][] => Array.from({ length: n }, (_, i) => [cu + r * Math.cos((-2 * Math.PI * i) / n), r * Math.sin((-2 * Math.PI * i) / n)])
// stemning = arket mot deg, ei lysande bøygd flate. kveld = dreidd 180, du ser kula i tunnelen og veggen lyser.
export const lampe = (modus: "stemning" | "kveld") => gitter({
  namn: "le-" + modus, stl: STL, snudd: modus === "kveld", material: "bjork", tjukn: 4, farge: undefined as unknown as string,
  senter: [0, 0, 156],
  fam: [{ n: [1, 0, 0], avstand: E("A1", 80), tal: 2 }, { n: [0, 1, 0], avstand: 0, tal: 2, stader: [E("Y1", -78), E("Y2", 70)] }],
  vegg: 250, fjern: (process.env.FJERN ?? "").split(",").filter(Boolean).map(Number),
  scene: () => ({ kamera: { helt: { az: 32, el: 8 }, lys: { az: 28, el: 6 }, sprengt: { az: 32, el: 12 } } }),
  boygde: [{ namn: "ark", senter: [0, YC + R * Math.cos(FM), ZC + R * Math.sin(FM)], u: [0, Math.sin(FM), -Math.cos(FM)], v: [1, 0, 0], n: [0, -Math.cos(FM), -Math.sin(FM)], omriss: rund(), hol: [sirkel(HOLU, HOLR)], R, tjukn: 3, material: "akryl-opal" }],
  utstyr: (P, D) => [
    { slag: "sokkel", senter: P([0, -6, 57.5]), diameter: 28, lengd: 45, retning: D([0, 0, 1]) },
    { slag: "paere", senter: P(KULE), diameter: 45, lengd: 83, retning: D([0, 0, -1]) },
    { slag: "leidning", punkt: [P([0, 20, 40]), P([0, 99, 40]), P([8, 126, 29]), P([70, 190, 29]), P([190, 230, 29])], diameter: 5 },
    { slag: "sylinder", senter: P([0, -100, 46]), diameter: 14, lengd: 7, retning: D([0, -1, 0]), farge: "#b8935a", metall: true },
  ],
})
