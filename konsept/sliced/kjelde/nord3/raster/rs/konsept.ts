import { raster } from "../raster"
const x = raster({ namn: "rs", R: 78, hc: 36, deling: 28, tal: 5, vri: 45, stativ: "flagg", farge: "#2f3d35", hogd: 390, lokk: 18, skjort: 38, speglA: "begge", speglB: "begge", lysPkt: [[19.8, 0], [-19.8, 0], [0, -19.8]], phi: 130, kamera: { helt: { az: 150, el: 22 } } })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr()
