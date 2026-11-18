import { nord } from "../nord"
const x = nord({ namn: "n4a", b: 120, ab: 120, af: 85, bor: 70, nett: [-131.25, -93.75, -56.25, -18.75, 18.75, 56.25, 93.75, 131.25], hr: 22, munn: { fram: true, elev: -90 }, fot: 165, fotBreidd: 190 })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr()
