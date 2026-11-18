import { nord } from "../nord"
const x = nord({ namn: "n1s", b: 110, ab: 110, af: 78, bor: 67.5, munn: { fram: false, elev: 40 }, fot: 150 })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr()
