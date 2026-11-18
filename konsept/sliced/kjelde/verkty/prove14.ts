import { writeFileSync } from "node:fs"

type P2 = [number, number]

const T = 4
const HOGD = 300
const DJUPN = 25
const RIBBER = 12
const RINGAR = [60, 220]
const STEG = Number(process.argv[3] ?? 120)

const ytre = (z: number): number => 60 + 80 * Math.pow(Math.sin((Math.PI * (z + 20)) / 360), 0.8)
const indre = (z: number): number => ytre(z) - DJUPN
const midt = (zr: number): number => (indre(zr + T / 2) + ytre(zr + T / 2)) / 2

function sirkel(cx: number, cy: number, r: number, n: number): P2[] {
  const ut: P2[] = []
  for (let i = 0; i < n; i++) {
    const a = (2 * Math.PI * i) / n
    ut.push([cx + r * Math.cos(a), cy + r * Math.sin(a)])
  }
  return ut
}

function ribbe(): { omriss: P2[]; hol: P2[][] } {
  const omriss: P2[] = []
  for (let i = 0; i <= STEG; i++) {
    const z = (HOGD * i) / STEG
    omriss.push([ytre(z), z])
  }
  const brot = RINGAR.flatMap((zr) => [zr, zr + T])
  const zs = new Set<number>(brot)
  for (let i = 0; i <= STEG; i++) {
    const z = (HOGD * i) / STEG
    if (!RINGAR.some((zr) => z > zr && z < zr + T)) zs.add(z)
  }
  const ned = [...zs].sort((a, b) => b - a)
  for (const z of ned) {
    const topp = RINGAR.find((zr) => z === zr + T)
    const botn = RINGAR.find((zr) => z === zr)
    if (topp !== undefined) {
      omriss.push([indre(z), z], [midt(topp), z])
    } else if (botn !== undefined) {
      omriss.push([midt(botn), z], [indre(z), z])
    } else {
      omriss.push([indre(z), z])
    }
  }
  const hol = [110, 150, 190].map((z) => sirkel((indre(z) + ytre(z)) / 2, z, 6, 48))
  return { omriss, hol }
}

function ring(zr: number): { omriss: P2[]; hol: P2[][] } {
  const ro = Math.min(ytre(zr), ytre(zr + T)) - 6
  const ri = Math.min(indre(zr), indre(zr + T)) - 14
  const rm = midt(zr)
  const d = Math.asin(T / 2 / ro)
  const omriss: P2[] = []
  const per = Math.max(2, Math.round(STEG / RIBBER))
  for (let k = 0; k < RIBBER; k++) {
    const a = (2 * Math.PI * k) / RIBBER
    const c = Math.cos(a)
    const s = Math.sin(a)
    const xk = ro * Math.cos(d)
    const lokal = (x: number, y: number): P2 => [x * c - y * s, x * s + y * c]
    omriss.push(lokal(xk, -T / 2), lokal(rm, -T / 2), lokal(rm, T / 2), lokal(xk, T / 2))
    const fra = a + d
    const til = a + (2 * Math.PI) / RIBBER - d
    for (let i = 1; i < per; i++) {
      const b = fra + ((til - fra) * i) / per
      omriss.push([ro * Math.cos(b), ro * Math.sin(b)])
    }
  }
  return { omriss, hol: [sirkel(0, 0, ri, 96)] }
}

const delar: unknown[] = []
const r = ribbe()
for (let k = 0; k < RIBBER; k++) {
  const a = (2 * Math.PI * k) / RIBBER
  const u = [Math.cos(a), Math.sin(a), 0]
  const v = [0, 0, 1]
  const n = [Math.sin(a), -Math.cos(a), 0]
  const o = n.map((x) => (-T / 2) * x)
  delar.push({
    namn: `R${String(k + 1).padStart(2, "0")}`,
    tjukn: T,
    farge: "#c9a36b",
    omriss: r.omriss,
    hol: r.hol,
    matrise: [...u, 0, ...v, 0, ...n, 0, ...o, 1],
  })
}
RINGAR.forEach((zr, i) => {
  const g = ring(zr)
  delar.push({
    namn: `G${String(i + 1).padStart(2, "0")}`,
    tjukn: T,
    farge: "#6b8fc9",
    omriss: g.omriss,
    hol: g.hol,
    matrise: [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, zr, 1],
  })
})

const ut = process.argv[2]
writeFileSync(ut, JSON.stringify({ namn: "prove14", eining: "mm", delar }))
console.log(`${ut} · ${delar.length} delar · ribbe ${r.omriss.length} punkt + ${r.hol.length} hol`)
