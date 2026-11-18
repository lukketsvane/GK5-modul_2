import { fri } from "../fri"
const x = fri({ namn: "ta", form: "kjegle", b: 90, rc: 32, hc: 140, vegg: 26, nett: [-52, -15.6, 15.6, 52], vri: 45, farge: "#2f3d35", spegl: true, ringR: 50, hogd: 265, munn: { fram: true, elev: -90 } })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr()
export const krav = x.krav
