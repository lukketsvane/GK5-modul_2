import { chromium } from "playwright"
import { posen, spegl } from "/home/user/slicer.iverfinne.no/scripts/pose"
const K = "/tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/kule"
const ADR = "http://127.0.0.1:3230/nn"
const pause = (ms: number) => new Promise((r) => setTimeout(r, ms))
const filer = process.argv.slice(2)
void (async () => {
  for (let i = 0; i < 60; i++) { try { if ((await fetch(ADR)).ok) break } catch {} await pause(500) }
  const b = await chromium.launch()
  for (const f of filer) {
    const c = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 })
    const s = await c.newPage()
    const konsoll: string[] = []
    s.on("pageerror", (e) => konsoll.push(e.message))
    await spegl(s)
    await s.goto(ADR, { waitUntil: "load" })
    await s.waitForFunction(() => !!window.slicer, undefined, { timeout: 30000 })
    await s.locator('[aria-label="kontrollar"][aria-busy="false"]').waitFor({ timeout: 45000 })
    const fyrr = String(posen(s).kjelde)
    await s.locator("input[type=file]").first().setInputFiles(`${K}/prosjekt/${f}.zip`)
    for (let i = 0; i < 300 && String(posen(s).kjelde) === fyrr; i++) await pause(100)
    await s.locator('[aria-label="kontrollar"][aria-busy="false"]').waitFor({ timeout: 60000 })
    await pause(1500)
    await s.touchscreen.tap(60, 700)
    await pause(300)
    await s.screenshot({ path: `${K}/app/${f}.png` })
    const p = posen(s)
    console.log(f, "storleik", p.storleik, "tjukn", p.tjukn, "plan", String(p.plan).split(";").filter(Boolean).length, konsoll.length ? konsoll.join(" | ") : "konsoll rein")
    await c.close()
  }
  await b.close()
})()
