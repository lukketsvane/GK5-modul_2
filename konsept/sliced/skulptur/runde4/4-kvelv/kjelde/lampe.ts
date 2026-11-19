import { gitter, pose, rotZ, type V3 } from "../gitter2"
// skulptur-12: berre hovudet over foten er bjørk. Belgen er eitt bøygd opalark over ein opal lysstav.
const STL = new URL("./lampe.stl", import.meta.url).pathname
const E = (k: string, d: number) => +(process.env[k] ?? d)
const R = 84, ZS = 94, HALV = (64 * Math.PI) / 180, a = R * HALV, Y0 = -138, Y1 = 198, YM = (Y0 + Y1) / 2, h = (Y1 - Y0) / 2, hj = 58
const tunge = (): [number, number][] => {
  const p: [number, number][] = []
  const bue = (cx: number, cy: number, r: number, a0: number) => { for (let i = 0; i <= 10; i++) { const t = a0 + (i / 10) * (Math.PI / 2); p.push([cx + r * Math.cos(t), cy + r * Math.sin(t)]) } }
  bue(-a + 16, -h + 16, 16, Math.PI); bue(a - 16, -h + 16, 16, 1.5 * Math.PI); bue(a - hj, h - hj, hj, 0); bue(-a + hj, h - hj, hj, 0.5 * Math.PI)
  return p
}
const ZR = 142.5, RS = 15, YS0 = -60, YS1 = 176
// stemning = belgen langs veggen. arbeid = svinga 90 grader om foten, ut over bordet.
export const lampe = (modus: "stemning" | "arbeid") => gitter({
  namn: "kvelv-" + modus, stl: STL, pose: pose(rotZ(modus === "arbeid" ? 180 : -90)), material: "bjork", tjukn: 4, farge: undefined as unknown as string,
  senter: [0, 0, 87],
  fam: [{ n: [0, 1, 0], avstand: 0, tal: 3, stader: [E("Y1", -104), E("Y2", -78), E("Y3", -52)] }, { n: [1, 0, 0], avstand: E("A2", 28), tal: 2 }],
  vegg: 250, fjern: (process.env.FJERN ?? "").split(",").filter(Boolean).map(Number),
  scene: () => ({ kamera: { helt: { az: 32, el: 8 }, lys: { az: 28, el: 6 }, sprengt: { az: 32, el: 12 } } }),
  lys: [-10, 58, 126].map((y) => ({ punkt: [0, y, ZR] as V3, radius: 9, farge: "#ffcf9a", styrke: 0.8 })),
  boygde: [{ namn: "lysstav", senter: [0, (YS0 + YS1) / 2, ZR - RS], u: [1, 0, 0], v: [0, 1, 0], n: [0, 0, 1], omriss: [[-Math.PI * RS, -(YS1 - YS0) / 2], [Math.PI * RS, -(YS1 - YS0) / 2], [Math.PI * RS, (YS1 - YS0) / 2], [-Math.PI * RS, (YS1 - YS0) / 2]], R: RS, tjukn: 2, material: "akryl-opal" },
    { namn: "kvelv", senter: [0, YM, ZS + R + 1.5], u: [-1, 0, 0], v: [0, 1, 0], n: [0, 0, -1], omriss: tunge(), R, tjukn: 3, material: "akryl-opal" }],
  utstyr: (P, D) => [
    { slag: "sokkel", senter: P([0, -93, ZR]), diameter: 40, lengd: 62, retning: D([0, 1, 0]) },
    { slag: "leidning", punkt: [P([0, -98, 8]), P([-10, -135, 4]), P([-70, -190, 3]), P([-190, -230, 3])], diameter: 5 },
    { slag: "sylinder", senter: P([0, -141, ZR]), diameter: 20, lengd: 7, retning: D([0, -1, 0]), farge: "#b8935a", metall: true },
  ],
})
