import { rokkestein, klaring, VIPP_KVELD } from "../rokkestein"
import type { Kontekst } from "../../../verkty/typar"
const x = rokkestein(false)
export const namn = x.namn
export const kropp = x.kropp
export const bag = x.bag
export const plan = x.plan
export const utstyr = x.utstyr
export const krav = (k: Kontekst) => {
  const v = klaring(VIPP_KVELD)
  return [k.krav("stonga klarer den indre langplata ved 30° rokk", v >= 1, `22·tan30 + 3/cos30 = ${(22 * Math.tan(Math.PI / 6) + 3 / Math.cos(Math.PI / 6)).toFixed(1)} mm mot 17,5 mm: klaring ${v.toFixed(1)} mm`)]
}
