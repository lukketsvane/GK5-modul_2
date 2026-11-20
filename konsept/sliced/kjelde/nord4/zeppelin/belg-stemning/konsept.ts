import { lag } from "../belg"
import { belg } from "../belg.val"
const x = lag({ ...belg, namn: "belgstemning", vri: 135 })
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr()
export const krav = x.krav
