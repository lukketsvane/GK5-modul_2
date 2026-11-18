import { nord } from "../globus"
const x = nord({ namn: "b1s", b: 100, ab: 100, af: 62, bor: 66, hr: 27, tjukn: 2, nett: [-126, -90, -54, -18, 18, 54, 90, 126], material: "akryl", klaring: 0.15, vri: 0, spegl: true, stativ: "globus", farge: "#b5ad9f", stilk: 175, fotBreidd: 158, fotH: 10, ryPluss: 7, messing: "krune", fot: 0, munn: { fram: false, elev: 40 } })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr()
export const krav = x.krav
