import { readFileSync, writeFileSync } from "node:fs"
import { MOTOR } from "/home/user/slicer.iverfinne.no/lib/motor"
import { lesNett, registrer } from "../verkty/form"
const K = "/tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/kule"
const NAMN: Record<string, string> = { k5: "kule-A-5x5", k7: "kule-B-7x7", k9: "kule-C-9x9", k3: "kule-D-3x3", k4: "kule-E-4x4", k6hals: "kule-F-pendel", kskra: "kule-G-60", khell: "kule-H-45", kstor: "kule-I-golv", kbord: "kule-bord" }
for (const [v, namn] of Object.entries(NAMN)) {
  const r = JSON.parse(readFileSync(`${K}/${v}/ut/rapport.json`, "utf8"))
  registrer(r.pose.kjelde, lesNett(`${K}/${v}/ut/kropp.stl`))
  const ut = MOTOR.exportFile(r.pose, "prosjekt") as unknown as Record<string, unknown>
  const raa = (ut.bytes ?? ut.data ?? ut.innhald) as ArrayBuffer | Uint8Array
  const data = raa instanceof Uint8Array ? raa : new Uint8Array(raa)
  writeFileSync(`${K}/prosjekt/${namn}.zip`, data)
  console.log(namn, data.length, Object.keys(ut).join(","))
}
