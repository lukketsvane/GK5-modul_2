import { gitter, type V3 } from "./g11"
import { flatark } from "../../verkty/ekstra"
const STL = new URL("./hatt.stl", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")
const MESSING = "#b8935a", GRON = "#3f4b42", SVART = "#1d1d1d"
// Hei, runde 2: hatten frå skulptur-11 (k 205, 146 × 204 × 63 mm), heile rista matt mørkegrøn MDF.
// Opal berre som lukka linse: ei skive under og eit lokk over kvar av dei tre LED-cellene (ekstra, ikkje plan).
// Rista: 4 langplater (u ±13,5/±40,5) og 7 tverrplater (v -55..77, 22 mm), dreidde 9° om z. Brema peikar mot -y (brukaren).
// Krona (+y) er massiv 0–63 mm: LED i cellene (-27,22), (0,22), (0,44); hengselcella (0,66) bak dei.
const A = (9 * Math.PI) / 180
const g = (u: number, v: number, z: number): V3 => [u * Math.cos(A) - v * Math.sin(A), u * Math.sin(A) + v * Math.cos(A), z]
const U: V3 = [Math.cos(A), Math.sin(A), 0] // hengselaksen, langs u
const NAV: V3 = g(0, 66, 30) // hengselnav i cella mellom langplatene u ±13,5, bak LED-cellene
const FOT = 22, OVER = 243 + 30 // hattebotnen 243 mm over bordet i arbeid → lampa 306 mm
const LUT = (12 * Math.PI) / 180 // stonga lener 12° fram mot arbeidsfeltet (fram-høgre)
const LD: V3 = [0.35, -0.937, 0]
const CELLER: V3[] = [g(-27, 22, 0), g(0, 22, 0), g(0, 44, 0)]
const ring = (r: number): [number, number][] => Array.from({ length: 28 }, (_, i) => [r * Math.cos((i / 28) * 2 * Math.PI), r * Math.sin((i / 28) * 2 * Math.PI)])
const at = (p: V3, z: number): V3 => [p[0], p[1], z]

export const hei = (mote: boolean) =>
  gitter({
    namn: mote ? "hei-mote" : "hei-arbeid", stl: STL, H: 63.4, vipp: mote ? -20 : 0,
    vinkel: 9, avstand: 27, tal: 4, tal2: 8, avstand2: 22, fjern: [21],
    fam1: { material: "mdf", farge: GRON }, fam2: { material: "mdf", farge: GRON },
    // arbeid: tre nedlys like over linsa (z 12), kretskortet over skjermar opp → lyset går ned langs cellene
    // møte: to opplys over kortet (z 32) mot veggen bak, eitt mjukt nedlys mot bordet framfor deg, varmare
    lys: mote
      ? [
          { punkt: at(CELLER[0], 33), radius: 5, farge: "#ffb877", styrke: 1.1 },
          { punkt: at(CELLER[2], 33), radius: 5, farge: "#ffb877", styrke: 1.1 },
          { punkt: at(CELLER[1], 12), radius: 9, farge: "#ffc48a", styrke: 0.45 },
        ]
      : CELLER.map((p) => ({ punkt: at(p, 11), radius: 5, farge: "#ffd6a8", styrke: 1.3 })),
    scene: (P, D) => {
      const c = P(NAV), G = c[2] - OVER
      const n = D([0, 0, 1])
      return {
        golv: G,
        vegg: { punkt: [0, c[1] + 235, 0] as V3, normal: [0, -1, 0] as V3 },
        ekstra: CELLER.flatMap((p, i) => [
          flatark({ namn: `linse-${i + 1}`, punkt: P(at(p, 3)), n, omriss: ring(9), tjukn: 2, material: "akryl-opal" }),
          flatark({ namn: `lokk-${i + 1}`, punkt: P(at(p, 50)), n, omriss: ring(9), tjukn: 2, material: "akryl-opal" }),
        ]),
      } as never
    },
    utstyr: (P, D) => {
      const c = P(NAV), G = c[2] - OVER
      const L = (OVER - FOT - 6) / Math.cos(LUT), h = (OVER - FOT - 6) * Math.tan(LUT)
      const f: V3 = [c[0] - LD[0] * h, c[1] - LD[1] * h, G + FOT] // fotsentrum
      const s: V3 = [(c[0] + f[0]) / 2, (c[1] + f[1]) / 2, (c[2] - 6 + f[2]) / 2]
      const sd: V3 = [c[0] - f[0], c[1] - f[1], c[2] - 6 - f[2]]
      const u = D(U)
      return [
        { slag: "sylinder", senter: [f[0], f[1], G + FOT / 2], diameter: 130, lengd: FOT, retning: [0, 0, 1], farge: GRON, ru: 0.7 },
        { slag: "sylinder", senter: s, diameter: 8, lengd: L, retning: sd, farge: GRON, ru: 0.6 },
        { slag: "sylinder", senter: c, diameter: 12, lengd: 23, retning: u, farge: GRON, ru: 0.6 },
        { slag: "sylinder", senter: P(g(23.5, 66, 30)), diameter: 5, lengd: 47, retning: u, farge: GRON, ru: 0.6 },
        // messingknappen sit på hengselaksen, i spalta mellom to tverrribber på sida mot brukaren: drei = dim, trykk = av/på
        { slag: "sylinder", senter: P(g(53, 66, 30)), diameter: 18, lengd: 12, retning: u, farge: MESSING, metall: 1, ru: 0.3 },
        // LED-kort i kvar lyscelle (skjermar oppover i arbeid, ber opplysa i møte)
        ...CELLER.map((p) => ({ slag: "sylinder", senter: P(at(p, 22)), diameter: 16, lengd: 3, retning: D([0, 0, 1]), farge: SVART, ru: 0.8 })),
        // skjerm, skjermfot og tastatur
        { slag: "boks", senter: [c[0] + 360, c[1] + 80, G + 100 + 160], storleik: [540, 22, 320], farge: "#151515" },
        { slag: "boks", senter: [c[0] + 360, c[1] + 100, G + 50], storleik: [50, 20, 100], farge: "#202020" },
        { slag: "boks", senter: [c[0] + 330, c[1] - 170, G + 8], storleik: [430, 135, 16], farge: "#3a3a3a", ru: 0.8 },
      ] as never
    },
  })
