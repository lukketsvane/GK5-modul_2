import { gitter, type Grep } from "./gitter"
const STL = new URL("./sopp.stl", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")
const MESSING = "#b8935a"
export const sopp = (grep: Grep) => {
  const snudd = grep === "snu"
  return gitter({
    namn: snudd ? "sopp-stemning" : "sopp-arbeid", stl: STL, H: 132, grep, avstand: 30, tal: 8, farge: "#d8cfc0", vegg: 280,
    utstyr: (P, D) => [
      { slag: "paere", senter: P([0, 0, 90]), diameter: 56, lengd: 86, retning: D([0, 0, 1]) },
      { slag: "sylinder", senter: P([0, 0, 133]), diameter: 26, lengd: 6, retning: [0, 0, 1], farge: MESSING, metall: 1, ru: 0.35 },
      ...(snudd ? [] : [{ slag: "leidning" as const, punkt: [[0, 0, 30], [0, 0, 3], [0, -70, 2], [0, -190, 2], [90, -340, 2]] as [number, number, number][], diameter: 5, farge: "#2a2a2a" }]),
    ],
  })
}
