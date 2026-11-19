import { gitter } from "./gitter4"
import { flatark, sylinderark, type Ekstra } from "../../verkty/ekstra"
const STL = new URL("./nikk.stl", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")
const MESSING = "#b8935a"
const GRON = "#3f4b42"
type V3 = [number, number, number]
type Modus = "arbeid" | "mote" | "kveld"
const sirkel = (r: number, n = 96) => Array.from({ length: n }, (_, i) => [r * Math.cos((2 * Math.PI * i) / n), r * Math.sin((2 * Math.PI * i) / n)] as [number, number])

// Nikk (Northern, runde 3, v2): trommehovud Ø184 x 38 frå skulptur-04 (radialt kappa på r 92), opal hatt Ø189 x 15 oppe (lokk + skjørt, 9 mm diffusorrom),
// loddrette celler nede. Hovudet sit på ei Ø9 stålsøyle (390 mm) ved sida; knappen ned = hovudet nikkar 85° mot deg (møte).
// Eitt tosidig LED-kort (32 punkt, eitt per celle) i staden for to punktlys: nedsida lyser gjennom cellene, oppsida lyser opalen.
const TAL = 7, AVSTAND = 26, SOYLE = 390, R = 92, ARM = 28
// LED-kortet har eitt punkt midt i kvar heile celle (celle 26 x 26, sentrum på ±13, ±39, ±65 innanfor r 80), aldri på eit plan.
// Same kort lyser ned (z 14) og opp mot opalen (z 29), så kvar celle gløder like mykje under lokket.
const C = [-65, -39, -13, 13, 39, 65]
const CELLER: [number, number][] = C.flatMap((a) => C.map((b) => [a, b] as [number, number])).filter(([a, b]) => Math.hypot(a, b) < 80)
const ring = (z: number, radius: number, styrke: number, farge: string) => CELLER.map(([a, b]) => ({ punkt: [a, b, z] as V3, radius, farge, styrke }))

// flyttar eit ekstra-ark frå hovudramma til lampeframa (vipp + forskyving)
const snu = (e: Ekstra, P: (p: V3) => V3, D: (d: V3) => V3): Ekstra => {
  const x = e.matrise
  const u = D([x[0], x[1], x[2]]), v = D([x[4], x[5], x[6]]), n = D([x[8], x[9], x[10]]), o = P([x[12], x[13], x[14]])
  return { ...e, matrise: [...u, 0, ...v, 0, ...n, 0, ...o, 1] }
}

export const nikk = (m: Modus) => {
  const vipp = m === "mote" ? 85 : m === "kveld" ? 35 : -6
  const ned = m === "arbeid" ? 3.2 : m === "mote" ? 0.5 : 0.12
  const opp = m === "arbeid" ? 0.2 : m === "mote" ? 1.0 : 0.8
  const farge = m === "kveld" ? "#ffad5c" : m === "mote" ? "#ffc68a" : "#ffd9b0"
  return gitter({
    namn: "nikk-" + m,
    stl: STL, H: 38, grep: "ingen", vipp, vinkel: 0, avstand: AVSTAND, tal: TAL, farge: GRON, vegg: 300,
    // Renderaren teiknar berre tre lyspunkt. Dei to ned-punkta står for heile ned-sida av kortet (eitt LED per celle): dei sit 14 mm under kortet
    // så lyskjegla får same breidd som 32 overlappande celle-kjegler (om lag 34° ut frå loddlinja). Opp-punktet sit i diffusorrommet under opalen.
    lys: [{ punkt: [13, -13, 24], radius: 5, farge, styrke: ned }, { punkt: [0, 0, 42], radius: 16, farge, styrke: opp }, { punkt: [-13, 13, 24], radius: 5, farge, styrke: ned }],
    scene: (P, D) => {
      const pv = P([-R, 0, 19])
      return {
        golv: pv[2] - SOYLE,
        ekstra: [
          // tosidig LED-kort (alu-kjerne, grønt lakkert) ligg på platetoppane og stengjer cellene oppe
          flatark({ namn: "led-kort", punkt: P([0, 0, 39.6]), n: D([0, 0, 1]), omriss: sirkel(R - 4), tjukn: 1.6, material: "mdf", farge: GRON }),
          // opal hatt: lokk Ø189 med 9 mm diffusorrom og ein skjørt-ring som dekkjer rommet frå sida
          flatark({ namn: "opal-lokk", punkt: P([0, 0, 50.5]), n: D([0, 0, 1]), omriss: sirkel(R + 2.5), tjukn: 3, material: "akryl-opal", farge: "#f4f1ea" }),
          snu(sylinderark({ namn: "opal-skjort", R: R + 1.5, grader: 360, z0: 34, z1: 49, tjukn: 2, material: "akryl-opal", farge: "#f4f1ea" }), P, D),
        ],
      }
    },
    utstyr: (P, D) => {
      const pv = P([-R, 0, 19])
      const G = pv[2] - SOYLE
      const x = pv[0] - ARM
      const nav = P([-R + 8, 0, 19])
      return [
        // søyle, vassrett stump inn til navet, kule i bøyen
        { slag: "sylinder", senter: [x, pv[1], (G + pv[2]) / 2], diameter: 9, lengd: pv[2] - G, retning: [0, 0, 1], farge: GRON },
        { slag: "sylinder", senter: [(x + pv[0] + 8) / 2, pv[1], pv[2]], diameter: 9, lengd: pv[0] + 8 - x, retning: [1, 0, 0], farge: GRON },
        { slag: "kule", senter: [x, pv[1], pv[2]], diameter: 9, farge: GRON },
        // friksjonsnav: går gjennom ytste plate (x -78)
        { slag: "sylinder", senter: nav, diameter: 20, lengd: 14, retning: D([1, 0, 0]), farge: GRON },
        // fot Ø160 med batteri, søyla står 8 mm innanfor kanten, hovudet 30 mm innanfor
        { slag: "sylinder", senter: [x + 72, pv[1], G + 11], diameter: 160, lengd: 22, retning: [0, 0, 1], farge: GRON },
        // messingknapp på framkanten, med hals inn til ytste plate (y -78)
        { slag: "sylinder", senter: P([0, -86, 19]), diameter: 6, lengd: 16, retning: D([0, 1, 0]), farge: MESSING, metall: true, ru: 0.3 },
        { slag: "sylinder", senter: P([0, -99, 19]), diameter: 18, lengd: 10, retning: D([0, 1, 0]), farge: MESSING, metall: true, ru: 0.3 },
        // fire fingerskruar held lokket (og kortet under) i krysspunkta mellom platene
        ...([[52, 52], [-52, 52], [52, -52], [-52, -52]] as const).map(([a, b]) => ({ slag: "sylinder" as const, senter: P([a, b, 53.5]), diameter: 8, lengd: 3, retning: D([0, 0, 1]), farge: GRON })),
        // scene: skjerm på fot, tastatur, brukarhovud
        { slag: "boks", senter: [430, 170, G + 105 + 165], storleik: [560, 25, 330], farge: "#121212" },
        { slag: "boks", senter: [430, 175, G + 55], storleik: [200, 160, 110], farge: "#2a2a2a" },
        { slag: "boks", senter: [140, -165, G + 10], storleik: [440, 140, 20], farge: "#9a9893" },
        { slag: "kule", senter: [190, -640, G + 465], diameter: 160, farge: "#d8c3b0" },
      ]
    },
  })
}











