import { nord } from "../nord"
const x = nord({ namn: "n6a", b: 110, ab: 110, af: 78, bor: 67.5, material: "mdf", stativ: "globus", farge: "#1f2022", stilk: 130, fotBreidd: 158, munn: { fram: true, elev: -90 }, fot: 0 })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr()
