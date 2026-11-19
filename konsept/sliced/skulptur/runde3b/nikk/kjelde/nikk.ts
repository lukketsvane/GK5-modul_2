import { gitter } from "./gitter3"
import { flatark } from "../../verkty/ekstra"
import type { Params } from "../../verkty/typar"
type V3 = [number, number, number]
// Nikk (Northern, runde 3, skulptur-03 velta 90° fram), versjon 2 etter kritikk.
// Gråbeige nebb: dei ytre finnane (x ±40,5) er lukka kinn som ber heile nebbprofilen, dei indre (±13,5) dannar
// lyscella; seks opal tverrplater ligg som eit innfelt band mellom kinna. Ø8-line 380 mm frå ein Ø120 batterifot.
// Ledd: nav Ø16 på toppen av lina, aksel Ø6 gjennom alle fire finnane, messingknapp på −x (fri side, vekk frå skjermen).
// Hardt stopp: pinne Ø4 gjennom finnane går mot ein knast på navet når hovudet har nikka STOPP grader opp.
// LED-lista (aluminium, 10 × 58 × 1,6) ligg midt i hatten (z 75,9 av 54..95,7), i eit 10,4 mm spor i tverrplatene
// 22 og 23 med 1,2 mm skulder over eit 8 mm lysvindauge: om lag 21 mm celle både under og over lista.
const STL = new URL("./nikk6.stl", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")
const FARGE = "#c9bfae", MESSING = "#b8935a", STAAL = "#8f8d89", OPAL = { material: "akryl-opal", farge: "#f6f4ef" }
const H = 95.7
const LINE = 380
const PIVOT: V3 = [0, 81, 32]
const LISTE_Z = 75.9
// LED-punkta sit like over/under lista (0,8 + 0,4 mm), så lista skuggar den andre sida: punktlysa i renderaren er rundstrålande, ekte LED er ikkje
const LED = 1.2
// bordramme: foten står på (0, 40) i bordkoordinatar, 47 mm framfor skjermplanet (y 87) og fast i begge modusar: berre hovudet nikkar
const FOT_BORD: [number, number] = [0, 40]
// stopp: pinne Ø4 (hol Ø4,1 i alle fire finnane) 20° framom loddrett over aksen, r 11, 3 mm gods mot sporet for plate 26;
// knast på navet, r 8..12,5. Aksel Ø6 i hol Ø6,2. Begge hola er skorne i kroppen (nikk6.json), så finnane får dei.
const PINNE_VINKEL = -20, PINNE_R = 11, GAP = (Math.asin(3.5 / PINNE_R) * 180) / Math.PI
const rad = (g: number) => (g * Math.PI) / 180

export const nikk = (vipp: number, ekstraVal: { namn?: string; bag?: Partial<Params>; stopp?: number; sving?: number; fjern?: number[]; andlet?: boolean; kamera?: Record<string, { az?: number; el?: number; linse?: number; vid?: number }> } = {}) => {
  const opp = vipp !== 0
  const stopp = ekstraVal.stopp ?? (opp ? -vipp : 35)
  // dim-to-warm: arbeid 3000 K, møte/kveld 2200–2400 K
  const lys = opp
    ? [
        { punkt: [0, -30, LISTE_Z + LED] as V3, radius: 2, farge: "#ffa860", styrke: 0.8 },
        // nasefill: siste opp-LED like bak opalplate 21 (y −70), lyser plata frå innsida mot andletet
        { punkt: [0, -56, LISTE_Z + LED] as V3, radius: 2, farge: "#ffc080", styrke: 1.0 },
        { punkt: [0, -18, LISTE_Z - LED] as V3, radius: 2, farge: "#ffa860", styrke: 0.3 },
      ]
    : [
        { punkt: [0, -48, LISTE_Z - LED] as V3, radius: 2, farge: "#ffe0bc", styrke: 2.0 },
        { punkt: [0, -18, LISTE_Z - LED] as V3, radius: 2, farge: "#ffe0bc", styrke: 2.0 },
        { punkt: [0, -33, LISTE_Z + LED] as V3, radius: 2, farge: "#ffe0bc", styrke: 0.08 },
      ]
  return gitter({
    namn: ekstraVal.namn ?? (opp ? "nikk-mote" : "nikk-arbeid"), stl: STL, H, grep: "ingen", vipp, vinkel: 0,
    avstand: 27, tal: 4, avstand2: 28, tal2: 6, farge: FARGE, mat2: OPAL, bag: ekstraVal.bag, fjern: ekstraVal.fjern,
    // opal berre i nasebandet (21–23, over lista og mot andletet); 24–26 bak lista er matte gråbeige og stengjer for lys bakover
    delar: { "24": { material: "mdf", farge: FARGE }, "25": { material: "mdf", farge: FARGE }, "26": { material: "mdf", farge: FARGE } },
    lys,
    scene: (P, D) => {
      const p = P(PIVOT), G = p[2] - LINE
      // sving: lampa er vridd ψ grader på den runde foten mot brukaren; bordet roterer om foten i lampeframa
      const sv = rad(-(ekstraVal.sving ?? 0)), c = Math.cos(sv), s = Math.sin(sv)
      const B = (x: number, y: number, z: number): V3 => {
        const dx = x - FOT_BORD[0], dy = y - FOT_BORD[1]
        return [p[0] + c * dx - s * dy, p[1] + s * dx + c * dy, G + z]
      }
      return {
        golv: G,
        ...(ekstraVal.kamera ? { kamera: ekstraVal.kamera } : {}),
        vegg: { punkt: B(0, 215, 0), normal: [s, -c, 0] as V3 },
        ekstra: [
          flatark({ namn: "led-list", punkt: P([0, -28, LISTE_Z]), n: D([0, 0, 1]), omriss: [[-5, -29], [5, -29], [5, 29], [-5, 29]], tjukn: 1.6, material: "mdf", farge: "#5d6062" }),
        ],
      }
    },
    utstyr: (P, D) => {
      const p = P(PIVOT), G = p[2] - LINE
      // sving: lampa er vridd ψ grader på den runde foten mot brukaren; bordet roterer om foten i lampeframa
      const sv = rad(-(ekstraVal.sving ?? 0)), c = Math.cos(sv), s = Math.sin(sv)
      const B = (x: number, y: number, z: number): V3 => {
        const dx = x - FOT_BORD[0], dy = y - FOT_BORD[1]
        return [p[0] + c * dx - s * dy, p[1] + s * dx + c * dy, G + z]
      }
      const boks = (x: number, y: number, z: number, storleik: V3, farge: string) => ({ slag: "boks", storleik, farge, matrise: [c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, ...B(x, y, z), 1] })
      // knast på navet (følgjer lina, står fast i verda): vinkel frå loddrett mot +y
      const th = rad(stopp + PINNE_VINKEL + GAP)
      const kn: V3 = [p[0], p[1] + 10.25 * Math.sin(th), p[2] + 10.25 * Math.cos(th)]
      const pv = rad(PINNE_VINKEL)
      return [
        // fot Ø120 × 22 (batteri, USB-C), line Ø8 opp til navet
        { slag: "sylinder", senter: [p[0], p[1], G + 11], diameter: 120, lengd: 22, retning: [0, 0, 1], farge: FARGE },
        { slag: "sylinder", senter: [p[0], p[1], (G + 22 + p[2] - 8) / 2], diameter: 8, lengd: p[2] - 8 - G - 22, retning: [0, 0, 1], farge: FARGE },
        // ledd: nav Ø16 × 18 på lina, aksel Ø6 gjennom alle finnane, messingknapp (friksjon + dimmar) på −x
        { slag: "sylinder", senter: p, diameter: 16, lengd: 18, retning: D([1, 0, 0]), farge: FARGE },
        { slag: "sylinder", senter: p, diameter: 6, lengd: 84, retning: D([1, 0, 0]), farge: STAAL, metall: 1, ru: 0.35 },
        { slag: "sylinder", senter: P([-46, PIVOT[1], PIVOT[2]]), diameter: 14, lengd: 8, retning: D([-1, 0, 0]), farge: MESSING, metall: 1, ru: 0.3 },
        // hardt stopp: knast på navet + pinne mellom dei indre finnane
        { slag: "sylinder", senter: kn, diameter: 3, lengd: 4.5, retning: [0, Math.sin(th), Math.cos(th)], farge: FARGE },
        { slag: "sylinder", senter: P([0, PIVOT[1] + PINNE_R * Math.sin(pv), PIVOT[2] + PINNE_R * Math.cos(pv)]), diameter: 4, lengd: 84, retning: D([1, 0, 0]), farge: STAAL, metall: 1, ru: 0.35 },
        // skjerm med stativ og webkamera, tastatur, A4-ark framfor foten
        boks(370, 100, 230, [540, 26, 320], "#151515"),
        boks(370, 120, 35, [60, 30, 70], "#1a1a1a"),
        boks(370, 92, 397, [44, 18, 14], "#222222"),
        boks(320, -170, 8, [300, 110, 16], "#2a2a2a"),
        boks(0, FOT_BORD[1] - 170, 1, [297, 210, 2], "#efece4"),
        // andletsprobe (berre i kontrollbiletet): der brukaren sit, i augehøgd framfor skjermen
        ...(ekstraVal.andlet ? [{ slag: "kule", senter: B(370, -560, 440), diameter: 160, farge: "#cdc4b6" }] : []),
      ] as any
    },
  })
}
