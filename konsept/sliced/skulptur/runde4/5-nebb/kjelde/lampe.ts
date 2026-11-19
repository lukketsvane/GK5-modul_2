import { readFileSync } from "node:fs"
import { gitter, pose, rotZ, type V3 } from "../gitter2"
// skulptur-06: to sider med nebb held eitt bøygd opalblad. Messingfatninga står gjennom bladet, kula heng under.
const STL = new URL("./lampe.stl", import.meta.url).pathname
const B = JSON.parse(readFileSync(new URL("./blad.json", import.meta.url), "utf8"))
const E = (k: string, d: number) => +(process.env[k] ?? d)
const C: V3 = B.senter, N: V3 = B.nopp, W: V3 = B.v
// punkt langs bladlina: v framover frå nebbrota, h ut frå bladet
const L = (v: number, h = 0): V3 => [0, B.T0[0] + W[1] * v + N[1] * h, B.T0[1] + W[2] * v + N[2] * h]
// arbeid = bladet mot deg over bordet. stemning = lampa snudd, bladet mot veggen.
export const lampe = (modus: "arbeid" | "stemning") => gitter({
  namn: "nebb-" + modus, stl: STL, pose: pose(rotZ(180)), material: "bjork", tjukn: 4, farge: undefined as unknown as string,
  senter: [0, 0, 150],
  fam: [{ n: [1, 0, 0], avstand: 20, tal: 2 }, { n: [0, 1, 0], avstand: 0, tal: 2, stader: [-93, 78] }],
  vegg: 280, snudd: modus === "stemning",
  scene: () => ({ kamera: { helt: { az: E("AZ", 50), el: 8 }, lys: { az: E("AZ", 50) - 4, el: 6 }, sprengt: { az: E("AZ", 50), el: 12 } } }),
  boygde: [{ namn: "blad", senter: C, u: B.u, v: W, n: B.n, omriss: B.omriss, hol: [B.hol], R: B.R, tjukn: 3, material: "akryl-opal" }],
  utstyr: (P, D) => [
    { slag: "sylinder", senter: P(L(75, 11)), diameter: 30, lengd: 46, retning: D(N), farge: "#b8935a", metall: true },
    { slag: "paere", senter: P(L(75, -49.5)), diameter: 45, lengd: 83, retning: D(N) },
    { slag: "leidning", punkt: [L(75, 34), L(64, 46), L(42, 30), L(20, 18), L(-22, 6), [0, -45, 286], [0, -75, 246], [0, -108, 196], [0, -108, 24], [0, -126, 8], [0, -165, 3], [70, -240, 3]].map((q) => P(q as V3)), diameter: 4 },
  ],
})
