import { nord } from "../nord"
const x = nord({ namn: "n5a", b: 90, ab: 90, af: 64, bor: 55.2, material: "mdf", stativ: "globus", farge: "#2f3d35", stilk: 120, munn: { fram: true, elev: -90 }, fot: 0 })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr()
