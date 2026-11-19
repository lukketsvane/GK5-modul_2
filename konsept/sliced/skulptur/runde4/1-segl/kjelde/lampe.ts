import { gitter, type V3 } from "../gitter2"
// same lykt som BLAD (skulptur-10), men bladet står: eit opalark bøygd rundt lykta, med opning på éi side
const STL = new URL("../blad/lampe.stl", import.meta.url).pathname
const E = (k: string, d: number) => +(process.env[k] ?? d)
const R = E("R", 44), GRAD = E("GRAD", 236), Z0 = E("Z0", 18), ZL = E("ZL", 132), ZH = E("ZH", 252)
const a = (R * GRAD * Math.PI) / 360
const glatt = (s: number) => s * s * (3 - 2 * s)
// omriss i arket sitt plan: u langs bogen, v opp. Rett botn, toppkant som stig frå låg til høg side, runda hjørne
const omriss = (zm: number): [number, number][] => {
  const p: [number, number][] = [], r = 16, N = 40
  const hj = (cx: number, cy: number, a0: number) => { for (let i = 0; i <= 8; i++) { const t = a0 + (i / 8) * (Math.PI / 2); p.push([cx + r * Math.cos(t), cy + r * Math.sin(t) - zm]) } }
  hj(-a + r, Z0 + r, Math.PI); hj(a - r, Z0 + r, 1.5 * Math.PI)
  hj(a - r, ZH - r, 0)
  for (let i = N - 1; i >= 1; i--) { const s = i / N, u = -a + r + s * (2 * a - 2 * r); p.push([u, ZL + (ZH - ZL) * glatt(s) - zm]) }
  hj(-a + r, ZL - r, 0.5 * Math.PI)
  return p
}
// stemning = opninga mot deg, du ser lykta. arbeid = opninga mot veggen, arket er ei lysande flate mot deg.
export const lampe = (modus: "stemning" | "arbeid") => {
  const t = ((modus === "stemning" ? 90 : -90) * Math.PI) / 180, zm = (Z0 + ZH) / 2
  return gitter({
    namn: "segl-" + modus, stl: STL, material: "bjork", tjukn: 4, farge: undefined as unknown as string,
    senter: [0, 0, 59],
    fam: [{ n: [1, 0, 0], avstand: 28, tal: 2 }, { n: [0, 1, 0], avstand: 28, tal: 2 }],
    vegg: 240, scene: () => ({ kamera: { helt: { az: 32, el: 8 }, lys: { az: 28, el: 6 }, sprengt: { az: 32, el: 12 } } }),
    boygde: [{ namn: "segl", senter: [R * Math.cos(t), R * Math.sin(t), zm], u: [Math.sin(t), -Math.cos(t), 0], v: [0, 0, 1], n: [-Math.cos(t), -Math.sin(t), 0], omriss: omriss(zm), R, tjukn: 3, material: "akryl-opal" }],
    utstyr: (P, D) => [
      { slag: "sokkel", senter: P([0, 0, 22.5]), diameter: 28, lengd: 45, retning: D([0, 0, 1]) },
      { slag: "paere", senter: P([0, 0, 82.5]), diameter: 45, lengd: 83, retning: D([0, 0, -1]) },
      { slag: "leidning", punkt: [P([0, 38, 6]), P([10, 70, 3]), P([60, 130, 3]), P([170, 170, 3])], diameter: 5 },
      { slag: "sylinder", senter: P([42, 0, 14]), diameter: 12, lengd: 7, retning: D([1, 0, 0]), farge: "#b8935a", metall: true },
    ],
  })
}
