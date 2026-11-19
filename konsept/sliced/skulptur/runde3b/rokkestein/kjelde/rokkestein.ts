import { gitter, type V3 } from "./gitter2"
const STL = new URL("./rokkestein.stl", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")
const MESSING = "#b8935a", GRON = "#3f4b42"
const NAV: V3 = [0, 0, 22] // midt på LED-ryggen = rokkeaksen
const STONG = 230, FOT = 22, STONG_D = 6
export const AVSTAND2 = 38 // to langplater i y = ±19: stonga klarer den indre plata ved 30°
export const VIPP_KVELD = -30
// klaring mellom stonga og den indre langplata ved vipp v (mm): (avstand2/2 - t/2) - (22·tan v + r/cos v)
export const klaring = (v: number) => {
  const a = (Math.abs(v) * Math.PI) / 180
  return AVSTAND2 / 2 - 1.5 - (NAV[2] * Math.tan(a) + STONG_D / 2 / Math.cos(a))
}

// Rokkestein v2: heile steinen opal, grønt berre på stong, nav og fot. Tosidig LED-rygg:
// eit ugjennomsiktig kretskort mellom ei nedre og ei øvre rad; tiltsensoren skiftar balansen mellom radene.
export const rokkestein = (kveld: boolean) => {
  const varm = kveld ? "#ffb877" : "#ffd9b0"
  const ned = kveld ? 0.15 : 0.9, opp = kveld ? 0.6 : 0.12
  // maks 3 lyskjelder i renderen: den sterke rada får to punkt (x = ±68), den svake eitt (x = 34, utanfor navet)
  const lys = kveld
    ? [{ punkt: [-68, 0, 26] as V3, styrke: opp }, { punkt: [68, 0, 26] as V3, styrke: opp }, { punkt: [34, 0, 18] as V3, styrke: ned }]
    : [{ punkt: [-68, 0, 18] as V3, styrke: ned }, { punkt: [68, 0, 18] as V3, styrke: ned }, { punkt: [34, 0, 26] as V3, styrke: opp }]
  return gitter({
    namn: kveld ? "rokkestein-kveld" : "rokkestein-arbeid", stl: STL, H: 44.4, vipp: kveld ? VIPP_KVELD : 0,
    vinkel: 0, avstand: 34, tal: 6, tal2: 2, avstand2: AVSTAND2,
    fam1: { material: "akryl-opal" }, fam2: { material: "akryl-opal" },
    lys: lys.map((l) => ({ ...l, radius: 1.5, farge: varm })),
    scene: (P) => {
      const c = P(NAV)
      return {
        golv: c[2] - STONG - FOT,
        vegg: { punkt: [0, c[1] + 190, 0], normal: [0, -1, 0] },
        lysstyrke: 1.8,
        kamera: { helt: { az: -32, el: 18 }, lys: { az: -38, el: 14 }, sprengt: { az: -32, el: 20 } },
      }
    },
    utstyr: (P, D) => {
      const c = P(NAV), G = c[2] - STONG - FOT
      const ex = D([1, 0, 0]), ey = D([0, 1, 0]), ez = D([0, 0, 1])
      const M = (p: V3) => [...ex, 0, ...ey, 0, ...ez, 0, ...P(p), 1] // roterer med steinen
      const kn = 35 // knausen: kula på stonga, under buken (klarer buken ved 30°)
      return [
        // fot med batteri, stong, nav og knaus i mørkegrøn
        { slag: "sylinder", senter: [c[0], c[1], G + FOT / 2], diameter: 130, lengd: FOT, retning: [0, 0, 1], farge: GRON, ru: 0.7 },
        { slag: "sylinder", senter: [c[0], c[1], (G + FOT + c[2] - 10) / 2], diameter: STONG_D, lengd: c[2] - 10 - G - FOT, retning: [0, 0, 1], farge: GRON, ru: 0.6 },
        { slag: "kule", senter: [c[0], c[1], c[2] - kn], diameter: 16, farge: GRON, ru: 0.6 },
        { slag: "sylinder", senter: c, diameter: 26, lengd: 20, retning: [1, 0, 0], farge: GRON, ru: 0.6 },
        // tosidig LED-rygg: H-profil i aluminium, kretskort i stegen, ei LED-rad i kvar kanal (flensane gjev ±48° avskjering)
        { slag: "boks", storleik: [256, 9, 1.5], matrise: M([0, 0, 22]), farge: "#1a1a1a", ru: 0.8 },
        { slag: "boks", storleik: [256, 1.2, 16], matrise: M([0, 4.5, 22]), farge: "#2b2b2b", ru: 0.6 },
        { slag: "boks", storleik: [256, 1.2, 16], matrise: M([0, -4.5, 22]), farge: "#2b2b2b", ru: 0.6 },
        // endehetter ø22 på begge tuppane (dekkjer kanalen ø18)
        { slag: "sylinder", senter: P([132, 0, 22]), diameter: 22, lengd: 4, retning: ex, farge: GRON, ru: 0.6 },
        { slag: "sylinder", senter: P([-132, 0, 22]), diameter: 22, lengd: 4, retning: ex, farge: GRON, ru: 0.6 },
        // dimmar: messingknapp på framkanten av foten, står stille og kan ikkje velte lampa
        { slag: "sylinder", senter: [c[0], c[1] - 65, G + 11], diameter: 15, lengd: 10, retning: [0, -1, 0], farge: MESSING, metall: 1, ru: 0.35 },
        // skjerm (kanten ved enden av hovudet), skjermfot, tastatur, A4 og andletsprobe
        { slag: "boks", senter: [c[0] + 330, c[1] + 90, G + 110 + 160], storleik: [520, 22, 320], farge: "#151515" },
        { slag: "boks", senter: [c[0] + 330, c[1] + 112, G + 55], storleik: [50, 20, 110], farge: "#202020" },
        { slag: "boks", senter: [c[0] + 330, c[1] - 150, G + 10], storleik: [440, 140, 20], farge: "#2a2a2a", ru: 0.8 },
        { slag: "boks", senter: [c[0] - 60, c[1] - 230, G + 1], storleik: [210, 297, 2], farge: "#f2f0ea", ru: 0.9 },
        { slag: "kule", senter: [c[0] + 330, c[1] + 90 - 600, G + 450], diameter: 180, farge: "#9a9894", ru: 0.95 },
      ]
    },
  })
}
