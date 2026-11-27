import { lag } from "../felles"
const x = lag({ namn: "nikk-stemning", stativ: "globus", stilk: 130, fotBreidd: 156, fotH: 16, munn: { fram: false, elev: 40 } })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr
export const krav = x.krav
