import { lag } from "../auge"
const x = lag({ namn: "augestemning", vri: 180, retning: 210, farge: "#3e4a40", R1: 66, R2: 73, H: 260 })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr()
export const krav = x.krav
