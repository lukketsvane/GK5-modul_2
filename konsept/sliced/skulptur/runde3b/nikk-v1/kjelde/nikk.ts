import { gitter } from "./gitter3"
import { flatark } from "../../verkty/ekstra"
type V3 = [number, number, number]
// Nikk (Northern, runde 3, skulptur-03 velta 90° fram): gråbeige nebb med fire finnar langs armen og seks opal tverrplater,
// på ei Ø8 line (330 mm) frå ein Ø120 batterifot. Messingknappen på leddet er både friksjonsakse og dimmar.
// LED-lista i spalta er tosidig: nedsida (arbeid, 3000 K) lyser gjennom cellene på arket, oppsida (møte/kveld, 2700→2200 K)
// lyser opalen og vaskar veggen. Nikket vel side: ned = nedsida dominerer, opp 35° = oppsida dominerer.
const STL = new URL("./nikk.stl", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")
const FARGE = "#c9bfae", MESSING = "#b8935a", OPAL = { material: "akryl-opal", farge: "#f6f4ef" }
const LINE = 330
const PIVOT: V3 = [0, 82, 22]
// spalta: x ±6, y -58..2, z 44..71 i kroppsramma. Lista (10 x 58 x 1,6) ligg midt i spalta, LED 4 mm under og over.
const LISTE_Z = 57.5
export const nikk = (opp: boolean) => {
  const ned = opp ? 0.3 : 2.0
  const upp = opp ? 1.2 : 0.25
  const farge = opp ? "#ffbd78" : "#ffd3a2"
  return gitter({
    namn: opp ? "nikk-mote" : "nikk-arbeid", stl: STL, H: 85.7, grep: "ingen", vipp: opp ? -35 : 0, vinkel: 0,
    avstand: 22, tal: 4, avstand2: 28, tal2: 6, farge: FARGE, mat2: OPAL, vegg: 215,
    // renderaren tek tre punkt: to på hovudsida (y -56 og -28, under nebbet og arket) og eitt på den andre (y -6)
    lys: [
      { punkt: [0, -56, LISTE_Z + (opp ? 4.5 : -4.5)] as V3, radius: 5, farge, styrke: opp ? upp : ned },
      { punkt: [0, -28, LISTE_Z + (opp ? 4.5 : -4.5)] as V3, radius: 5, farge, styrke: opp ? upp : ned },
      { punkt: [0, -6, LISTE_Z + (opp ? -4.5 : 4.5)] as V3, radius: 5, farge, styrke: opp ? ned : upp },
    ],
    scene: (P, D) => ({
      golv: P(PIVOT)[2] - LINE,
      ekstra: [
        flatark({ namn: "led-list", punkt: P([0, -28, LISTE_Z]), n: D([0, 0, 1]), omriss: [[-5, -29], [5, -29], [5, 29], [-5, 29]], tjukn: 1.6, material: "mdf", farge: FARGE }),
      ],
    }),
    utstyr: (P, D) => {
      const p = P(PIVOT), G = p[2] - LINE
      return [
        // fot Ø120 x 22 (batteri), line Ø8 opp til leddet, messingknapp på leddet
        { slag: "sylinder", senter: [p[0], p[1], G + 11], diameter: 120, lengd: 22, retning: [0, 0, 1], farge: FARGE },
        { slag: "sylinder", senter: [p[0], p[1], (G + 22 + p[2]) / 2], diameter: 8, lengd: p[2] - G - 22, retning: [0, 0, 1], farge: FARGE },
        { slag: "sylinder", senter: P([50.8, 82, 22]), diameter: 14, lengd: 8, retning: D([1, 0, 0]), farge: MESSING, metall: 1, ru: 0.3 },
        // skjerm med stativ, tastatur, A4-ark under armen
        { slag: "boks", senter: [370, 100, G + 70 + 160], storleik: [540, 26, 320], farge: "#151515" },
        { slag: "boks", senter: [370, 120, G + 35], storleik: [60, 30, 70], farge: "#1a1a1a" },
        { slag: "boks", senter: [340, -170, G + 8], storleik: [300, 110, 16], farge: "#2a2a2a" },
        { slag: "boks", senter: [0, -85, G + 1], storleik: [297, 210, 2], farge: "#efece4" },
      ]
    },
  })
}
