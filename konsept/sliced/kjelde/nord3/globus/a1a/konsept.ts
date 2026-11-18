import { nord } from "../globus"
const x = nord({ namn: "a1a", b: 90, ab: 90, af: 64, bor: 55.2, material: "akryl", klaring: 0.15, vri: 0, spegl: true, stativ: "globus", farge: "#2f3d35", stilk: 130, fotH: 10, ryPluss: 7, messing: "tappar", fot: 0, munn: { fram: true, elev: -75 } })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr()
export const krav = x.krav
