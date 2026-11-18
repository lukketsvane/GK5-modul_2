import { readFileSync, writeFileSync, mkdirSync } from "node:fs"
import { MOTOR } from "/home/user/slicer.iverfinne.no/lib/motor"
import { lesNett, registrer } from "../verkty/form"
const K = "/tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/nord"
mkdirSync(`${K}/prosjekt`, { recursive: true })
const NAMN: Record<string, string> = { n1s: "northern-1-kule220-stemning", n1a: "northern-1-kule220-arbeid", n2s: "northern-2-opal-stemning", n3s: "northern-3-kule180-stemning", n4s: "northern-4-tett-stemning" }
for (const [v, namn] of Object.entries(NAMN)) {
  const r = JSON.parse(readFileSync(`${K}/${v}/ut/rapport.json`, "utf8"))
  registrer(r.pose.kjelde, lesNett(`${K}/${v}/ut/kropp.stl`))
  const ut = MOTOR.exportFile(r.pose, "prosjekt") as unknown as { data: ArrayBuffer | Uint8Array }
  const data = ut.data instanceof Uint8Array ? ut.data : new Uint8Array(ut.data)
  writeFileSync(`${K}/prosjekt/${namn}.zip`, data)
  console.log(namn, data.length)
}
