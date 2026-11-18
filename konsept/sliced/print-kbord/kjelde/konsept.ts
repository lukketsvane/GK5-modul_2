import { kule } from "../felles"
const x = kule({ namn: "kbord", R: 120, bor: 74, fot: 12, ligg: true, tjukn: 3, ark: [250, 250], hals: { r: 31, tjukk: 12, under: 8 }, a: [-108.33, -65, -21.67, 21.67, 65, 108.33], b: [-108.33, -65, -21.67, 21.67, 65, 108.33] })
export const namn = x.namn
export const kropp = x.kropp
export const bag = { ...x.bag, klaring: 0.25, snitt: 0, material: "graa" }
export const plan = x.plan
export const utstyr = x.utstyr
