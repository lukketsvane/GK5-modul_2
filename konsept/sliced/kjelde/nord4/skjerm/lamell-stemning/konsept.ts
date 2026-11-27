import { lag } from "../lamell"
const x = lag({ namn: "lamellstemning", B: 96, D: 72, H: 280, vegg: 14, fins: 17, ribber: [0, 60, 120, 180], stilk: 130, fot: 120, vri: 180, farge: "#2f3d35" })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr()
export const krav = x.krav
