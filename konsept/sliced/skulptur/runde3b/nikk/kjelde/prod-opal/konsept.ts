import { nikk } from "../nikk"
// produksjonskøyring 2: same gitter i 3 mm opal akryl (klaring 0.15). Bruk berre delane 21–23 frå denne køyringa;
// finnane 1–4 og tverrplatene 24–26 kjem frå MDF-køyringa i arbeid/. (Motoren godtek ikkje plater utan kryssledd, så alle må vere med.)
const x = nikk(0, { namn: "nikk-opal", bag: { material: "akryl", tjukn: 3, klaring: 0.15, snitt: 0.2 } })
export const namn = x.namn, kropp = x.kropp, bag = x.bag, plan = x.plan, utstyr = x.utstyr
