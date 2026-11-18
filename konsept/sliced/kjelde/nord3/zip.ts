import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs"
import { MOTOR } from "/home/user/slicer.iverfinne.no/lib/motor"
import { lesNett, registrer } from "../verkty/form"
const K = "/tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/nord3"
const r0 = JSON.parse(readFileSync(`${K}/resultat.json`, "utf8")) as { alle: { namn: string; stemning: string; arbeid: string }[] }
mkdirSync(`${K}/prosjekt`, { recursive: true })
for (const d of r0.alle) {
  const stutt = d.namn.split(" ")[0].toLowerCase().replace("å", "aa")
  for (const [pose, mappe] of [["stemning", d.stemning], ["arbeid", d.arbeid]] as const) {
    if (!existsSync(`${mappe}/ut/rapport.json`)) { console.log("MANGLAR", mappe); continue }
    const r = JSON.parse(readFileSync(`${mappe}/ut/rapport.json`, "utf8"))
    registrer(r.pose.kjelde, lesNett(`${mappe}/ut/kropp.stl`))
    const ut = MOTOR.exportFile(r.pose, "prosjekt") as unknown as { data: ArrayBuffer | Uint8Array }
    const data = ut.data instanceof Uint8Array ? ut.data : new Uint8Array(ut.data)
    writeFileSync(`${K}/prosjekt/${stutt}-${pose}.zip`, data)
    console.log(stutt, pose, data.length)
  }
}
