import { lag } from "../rull"
const x = lag({ namn: "rullmote", opning: 120, midt: 150, retning: 65, synleg: true, farge: "#cfc6b8", L: 320, R: 80, kant: 3, hogd: 380 })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr()
export const krav = x.krav
