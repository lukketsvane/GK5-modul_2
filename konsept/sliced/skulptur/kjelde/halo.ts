import { gitter, type Grep } from "./gitter"
const STL = new URL("./halo.stl", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")
const MESSING = "#b8935a"
export const halo = (grep: Grep) => {
  const opp = grep === "drei"
  const G = opp ? -420 : -170
  return gitter({
    namn: opp ? "halo-arbeid" : "halo-kveld", stl: STL, H: 54.1, grep: "ingen", vipp: opp ? -45 : 90, avstand: 30, tal: 6, farge: "#1f2321", vegg: 230,
    lys: [{ punkt: [0, 0, 26], radius: 10, farge: "#ffcf9a", styrke: 1.5 }],
    scene: { golv: G },
    utstyr: (P) => {
      const c = P([0, 0, 26])
      return [
        { slag: "boks", senter: [0, opp ? -70 : -95, G + 70 + 165], storleik: [560, 30, 330], farge: "#121212" },
        { slag: "sylinder", senter: [0, 60, (G + c[2]) / 2], diameter: 8, lengd: c[2] - G, retning: [0, 0, 1], farge: "#1f2321" },
        { slag: "sylinder", senter: [0, 60, G + 6], diameter: 150, lengd: 12, retning: [0, 0, 1], farge: "#1f2321" },
        { slag: "sylinder", senter: [0, 48, c[2]], diameter: 18, lengd: 24, retning: [0, 1, 0], farge: MESSING, metall: 1, ru: 0.35 },
      ]
    },
  })
}
