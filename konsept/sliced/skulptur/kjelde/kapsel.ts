import { gitter, type Grep } from "./gitter"
const STL = new URL("./kapsel.stl", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")
const MESSING = "#b8935a"
export const kapsel = (grep: Grep) =>
  gitter({
    namn: grep === "drei" ? "kapsel-arbeid" : "kapsel-stemning", stl: STL, H: 191.6, grep, vinkel: 0, avstand: 30, tal: 4, tal2: 13, avstand2: 27, farge: "#e9e5dc", vegg: 300,
    lys: [-90, 10, 110].map((y) => ({ punkt: [0, y, 141] as [number, number, number], radius: 10, farge: "#ffcf9a", styrke: 1 })),
    utstyr: (P, D) => [
      { slag: "sylinder", senter: P([0, -106, 94]), diameter: 76, lengd: 6, retning: [0, 0, 1], farge: MESSING, metall: 1, ru: 0.35 },
      { slag: "leidning", punkt: [P([0, -106, 20]), P([0, -106, 3]), P([0, -180, 2]), P([-60, -330, 2])], diameter: 5, farge: "#2a2a2a" },
    ],
  })
