import { gitter, type Grep } from "./gitter"
const STL = new URL("./skygge.stl", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")
const MESSING = "#b8935a"
export const skygge = (grep: Grep) =>
  gitter({
    namn: grep === "drei" ? "skygge-stemning" : "skygge-arbeid", stl: STL, H: 190.6, grep, avstand: 30, tal: 8, fjern: [1], farge: "#3f4b42", vegg: 260, lys: [{ punkt: [-10, -10, 166], radius: 9, farge: "#ffcf9a", styrke: 1.4 }],
    utstyr: (P, D) => [
      { slag: "sylinder", senter: P([-10, -10, 172]), diameter: 30, lengd: 6, retning: [0, 0, 1], farge: "#f4efe6" },
      { slag: "sylinder", senter: P([-10, -10, 192]), diameter: 22, lengd: 8, retning: [0, 0, 1], farge: MESSING, metall: 1, ru: 0.35 },
      { slag: "leidning", punkt: [P([-30, 95, 20]), P([-30, 95, 3]), P([-30, 170, 2]), P([40, 330, 2])], diameter: 5, farge: "#2a2a2a" },
    ],
  })
