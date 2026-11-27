import { lag } from "../belg"
import { skolm } from "../belg.val"
const x = lag({ ...skolm, namn: "skolmarbeid", vri: 0 })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr()
export const krav = x.krav
