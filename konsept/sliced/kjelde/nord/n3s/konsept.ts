import { nord } from "../nord"
const x = nord({ namn: "n3s", b: 90, ab: 90, af: 64, bor: 55.2, munn: { fram: false, elev: 40 }, fot: 105, fotBreidd: 150 })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr()
