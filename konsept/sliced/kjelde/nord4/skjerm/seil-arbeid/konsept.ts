import { lag } from "../seil"
const x = lag({ namn: "seilarbeid", R: 98, grader: 132, H: 380, lepe: 3, kant: 6, vri: 0, farge: "#d9d1c3", fot: 104 })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr()
export const krav = x.krav
