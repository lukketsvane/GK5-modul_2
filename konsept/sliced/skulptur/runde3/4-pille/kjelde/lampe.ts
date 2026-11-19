import { gitter, pose, rotZ, type V3 } from "../gitter2"
const STL = new URL("./lampe.stl", import.meta.url).pathname
const E = (k: string, d: number) => +(process.env[k] ?? d)
const ZR = 142.5, R = 15, Y0 = -60, Y1 = 176
// opal lysstav under ryggen, sokkelen over foten. Belgen er open ned frå foten og ut til spissen.
// stemning = belgen langs veggen. arbeid = svinga 90 grader om foten, ut over bordet mot deg.
export const lampe = (modus: "stemning" | "arbeid") => gitter({
  namn: "pille-" + modus, stl: STL, pose: pose(rotZ(modus === "arbeid" ? 180 : -90)), material: "bjork", tjukn: 4, farge: undefined as unknown as string,
  senter: [0, 0, 87],
  fam: [{ n: [0, 1, 0], avstand: E("A1", 26), tal: E("T1", 12), skift: E("S1", 39) }, { n: [1, 0, 0], avstand: E("A2", 28), tal: 2, skift: E("S2", 0) }],
  vegg: 290, fjern: (process.env.FJERN ?? "12").split(",").filter(Boolean).map(Number),
  boygde: [{ namn: "lysstav", senter: [0, (Y0 + Y1) / 2, ZR - R], u: [1, 0, 0], v: [0, 1, 0], n: [0, 0, 1], omriss: [[-Math.PI * R, -(Y1 - Y0) / 2], [Math.PI * R, -(Y1 - Y0) / 2], [Math.PI * R, (Y1 - Y0) / 2], [-Math.PI * R, (Y1 - Y0) / 2]], R, tjukn: 2, material: "akryl-opal" }],
  lys: [-10, 58, 126].map((y) => ({ punkt: [0, y, ZR] as V3, radius: 9, farge: "#ffcf9a", styrke: 0.8 })),
  utstyr: (P, D) => [
    { slag: "sokkel", senter: P([0, -93, ZR]), diameter: 40, lengd: 62, retning: D([0, 1, 0]) },
    { slag: "leidning", punkt: [P([0, -98, 10]), P([-10, -135, 4]), P([-70, -190, 3]), P([-190, -230, 3])], diameter: 5 },
    { slag: "sylinder", senter: P([0, -141, ZR]), diameter: 24, lengd: 8, retning: D([0, -1, 0]), farge: "#b8935a", metall: true },
  ],
})
