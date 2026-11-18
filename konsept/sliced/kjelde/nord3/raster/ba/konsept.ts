import { raster } from "../raster"
const x = raster({ namn: "ba", R: 94, hc: 46, he: 22, deling: 24, tal: 6, delingB: 26, talB: 4, skraa: 40, stativ: "blad", farge: "#b9b2a5", hogd: 380, fot: 150, lokk: 14, skjort: 5, speglA: "ned", speglB: "inn", lysPkt: [[0, 17.6], [-26, -6.4], [26, -6.4]], veggAvstand: 60, phi: 0, kamera: { helt: { az: 35, el: 6 }, lys: { vid: 2.1, el: 9 } } })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr()
