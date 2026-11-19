import { nikk } from "../nikk"
// møte og kveld: nikk 25° opp (hardt stopp) og lampa vridd 35° på foten mot brukaren
const x = nikk(-25, { sving: 35 })
export const namn = x.namn, kropp = x.kropp, bag = x.bag, plan = x.plan, utstyr = x.utstyr
