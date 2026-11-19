import { gitter, type Grep } from "./gitter"
const STL = new URL("./lykt.stl", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")
const MESSING = "#b8935a"
export const lykt = (grep: Grep) => {
  const ute = grep === "drei"
  return gitter({
    namn: ute ? "lykt-kveld" : "lykt-arbeid", stl: STL, H: 101.6, grep: "ingen", vinkel: 0, avstand: 27, tal: 13, tal2: 4, avstand2: 30, farge: "#e9e5dc", vegg: 300,
    lys: [-100, 0, 100].map((x) => ({ punkt: [x, 0, 51] as [number, number, number], radius: 9, farge: "#ffcf9a", styrke: ute ? 0.8 : 1.2 })),
    scene: ute ? {} : { golv: -42 },
    utstyr: () => ute ? [] : [
      { slag: "boks", senter: [0, 0, -21], storleik: [300, 70, 42], farge: "#2b2b2b" },
      { slag: "sylinder", senter: [-60, 0, -1], diameter: 10, lengd: 3, retning: [0, 0, 1], farge: MESSING, metall: 1, ru: 0.3 },
      { slag: "sylinder", senter: [60, 0, -1], diameter: 10, lengd: 3, retning: [0, 0, 1], farge: MESSING, metall: 1, ru: 0.3 },
      { slag: "leidning", punkt: [[140, 0, -30], [200, 30, -40], [260, 160, -41]], diameter: 5, farge: "#2a2a2a" },
      { slag: "boks", senter: [480, 160, 150], storleik: [540, 26, 320], farge: "#151515" },
    ],
  })
}
