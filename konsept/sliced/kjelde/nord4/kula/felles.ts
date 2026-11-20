import { nord, type Val } from "./kula"
export const grunn: Omit<Val, "namn" | "munn"> = { b: 100, ab: 100, af: 62, bor: 66, hr: 22, vegg: 32, tjukn: 2, nett: [-126, -90, -54, -18, 18, 54, 90, 126], material: "akryl", klaring: 0.15, vri: 0, spegl: true, farge: "#b5ad9f", fot: 0, ryPluss: 10, kule: 110, kuleS: 0 }
export const lag = (v: Partial<Val> & { namn: string; munn: Val["munn"] }) => {
  const x = nord({ ...grunn, ...v } as Val)
  return { namn: x.namn, kropp: x.kropp, bag: x.bag, plan: x.plan, utstyr: x.utstyr(), krav: x.krav }
}
