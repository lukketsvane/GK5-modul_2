import { fri } from "../fri"
const x = fri({ namn: "bs", form: "skaal", b: 90, bor: 55, af: 24, nett: [-78, -46.8, -15.6, 15.6, 46.8, 78], farge: "#b7ad9c", spegl: true, hogd: 260, kule: 68, munn: { fram: false, elev: 40 } })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr()
export const krav = x.krav
