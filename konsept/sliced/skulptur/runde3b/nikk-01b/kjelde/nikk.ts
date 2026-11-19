import { gitter } from "./gitter2"
import { flatark } from "../../verkty/ekstra"
const STL = new URL("./nikk.stl", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")
type V3 = [number, number, number]
const MESSING = "#b8935a", SVART = "#1d1d1d", AKSEL = 330, H = 30
// v2: kroppen er kappa flatt på begge sider (kappBotn 50, kappTopp 80) -> rein skive, gitteret endar i éi flate.
// Lagdeling i prep-ramma (opalsida z=0, ut = -z): opal -3..0 (82x40), saumring -3..0 (85x43 / hol 82x40),
// LED-spalte -6..-3, bakskal -9..-6 (80x38, 3 mm), to leppringar -9..-3 (85x43 / hol 80x38, 2 x 3 mm) stengjer spalta.
// Spalta er 3 mm, så lyspunkta står klar av bakskalet (tynne flater tett inntil eit punktlys skuggar dårleg i motoren).
// Motoren lèt lys gå rett gjennom opal (ingen skugge), så den synlege opalkanten er modellert som ein tett ring
// i opalfarge. På den ekte lampa er det kanten av eitt opalark 170 x 86.
const ell = (a: number, b: number, n = 48): [number, number][] => Array.from({ length: n }, (_, i) => [a * Math.cos((i / n) * 2 * Math.PI), b * Math.sin((i / n) * 2 * Math.PI)])
const C: [number, number] = [0, 0]
// opalen ligg berre under dei fulldjupe cellene (kappflata 170 x 95); over dei grunne randcellene slapp ho flatt sidelys mot vegg og skjerm
const OPAL: [number, number] = [82, 40], SKAL: [number, number] = [80, 38], LEPPE: [number, number] = [85, 43]
const VIPP = { arbeid: 0, mote: -100, kveld: -160 } as const
const LYS = { arbeid: { farge: "#ffd9ad", styrke: 0.8 }, mote: { farge: "#ffc489", styrke: 0.6 }, kveld: { farge: "#ffb070", styrke: 0.9 } } as const
export const nikk = (modus: keyof typeof VIPP, farge: string = SVART) =>
  gitter({
    namn: "nikk-" + modus, stl: STL, H, grep: "snu", dreiZ: 180, vipp: VIPP[modus], vinkel: 0,
    tal: 9, avstand: 28, tal2: 5, avstand2: 25, fjern: [1, 9], farge, material: "mdf", vegg: 460,
    // motoren lagar berre punktlys av dei tre første lyskjeldene: tre punkt midt i kvar si celle (x -42, 14, 70; y 12,5), så ingen plate står rett framfor eit lys
    lys: [-42, 14, 70].map((x) => ({ punkt: [x, 12.5, -4.5] as V3, radius: 0.5, farge: LYS[modus].farge, styrke: LYS[modus].styrke })),
    scene: (P, D) => {
      const A = P([-130, 0, H / 2])
      const n = D([0, 0, 1])
      return {
        golv: A[2] - AKSEL,
        // atterskin 0: motoren sitt skuggelause fyll-lys i LED-punktet lyste opp utsida av bakskalet 3 mm unna
        atterskin: 0,
        // skjermen står til venstre for lampa, så biletkameraa ser frå venstre-framme og lampa dekkjer ikkje skjermen.
        // Møte: LYS-kameraet står på høgre sida av lampa, så ein ser sida av andletet som vender mot lampa.
        // Kveld: LYS-kameraet står lågt, under takplata, så ein ser lyset på undersida av taket.
        kamera: { helt: { az: modus === "mote" ? 15 : -35, el: 20 }, sprengt: { az: modus === "mote" ? 15 : -35, el: 22 }, lys: modus === "mote" ? { az: 82, el: 16, vid: 1.15 } : modus === "kveld" ? { az: -30, el: 2 } : { az: -30, el: 13 } },
        ekstra: [
          flatark({ namn: "opal", punkt: P([C[0], C[1], -1.5]), n, omriss: ell(OPAL[0], OPAL[1]), tjukn: 3, material: "akryl-opal" }),
          flatark({ namn: "saumring", punkt: P([C[0], C[1], -1.5]), n, omriss: ell(LEPPE[0], LEPPE[1]), hol: [ell(OPAL[0], OPAL[1]).reverse()], tjukn: 3, material: "mdf", farge: "#f3f0e8" }),
          flatark({ namn: "bakskal", punkt: P([C[0], C[1], -7.5]), n, omriss: ell(SKAL[0], SKAL[1]), tjukn: 3, material: "mdf", farge }),
          flatark({ namn: "leppring1", punkt: P([C[0], C[1], -7.5]), n, omriss: ell(LEPPE[0], LEPPE[1]), hol: [ell(SKAL[0], SKAL[1]).reverse()], tjukn: 3, material: "mdf", farge }),
          flatark({ namn: "leppring2", punkt: P([C[0], C[1], -4.5]), n, omriss: ell(LEPPE[0], LEPPE[1]), hol: [ell(SKAL[0], SKAL[1]).reverse()], tjukn: 3, material: "mdf", farge }),
        ],
      }
    },
    utstyr: (P) => {
      const A = P([-130, 0, H / 2]), g = A[2] - AKSEL, M = P([0, 0, H / 2])
      // dreiZ 180: navet sit på +x-enden, linsa strekkjer seg mot -x inn over tastaturet; skjermen står til venstre for lampa
      const sx = M[0] - 250, sy = A[1] + 420
      const u: any[] = [
        // messingnav Ø28 x 22: aksling, smekkstopp 0/100/160 og touch-dimmar
        { slag: "sylinder", senter: [A[0] + 11, A[1], A[2]], diameter: 28, lengd: 22, retning: [1, 0, 0], farge: MESSING, metall: 1, ru: 0.3 },
        // line Ø9
        { slag: "sylinder", senter: [A[0] + 26.5, A[1], (g + A[2] + 14) / 2], diameter: 9, lengd: A[2] + 14 - g, retning: [0, 0, 1], farge },
        // fot Ø170, sentrum 50 mm inn under linsa (stål + batteri ~0,9 kg)
        { slag: "sylinder", senter: [A[0] - 50, A[1], g + 7], diameter: 170, lengd: 14, retning: [0, 0, 1], farge },
        // skjerm med fot, bak og til høgre for lampa
        { slag: "boks", senter: [sx, sy, g + 70 + 160], storleik: [540, 26, 320], farge: "#151515" },
        { slag: "boks", senter: [sx, sy + 15, g + 39], storleik: [60, 20, 62], farge: "#202020" },
        { slag: "boks", senter: [sx, sy + 5, g + 4], storleik: [200, 180, 8], farge: "#202020" },
        // tastatur framfor skjermen
        { slag: "boks", senter: [M[0] - 70, A[1] + 160, g + 10], storleik: [440, 140, 20], farge: "#cfccc5" },
      ]
      if (modus === "mote") u.push({ slag: "kule", senter: [M[0] - 220, A[1] - 480, g + 440], diameter: 160, farge: "#d8c6b4" })
      if (modus === "kveld") u.push({ slag: "boks", senter: [M[0] - 120, A[1] - 150, g + 1000], storleik: [1100, 900, 10], farge: "#e8e4dc" })
      return u
    },
  })
