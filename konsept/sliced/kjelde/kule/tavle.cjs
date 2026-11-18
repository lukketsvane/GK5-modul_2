const { chromium } = require('playwright')
const fs = require('fs')
const K = '/tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/kule'
const tal = (v) => { const t = fs.readFileSync(`${K}/${v}/ut/rapport.txt`, 'utf8'); const a = /(\d+) delar/.exec(t), l = /(\d+) ledd/.exec(t), k = /kutt\s+([\d.]+) m · ([\d.]+) min.*?(\d+) ark (\d+ x \d+).*?([\d.]+) kg/.exec(t); const s = /— (\d+ x \d+ x \d+) mm/.exec(t); return `${s[1]} mm · ${a[1]} delar · ${l[1]} ledd · ${k[3]} ark ${k[4]} · ${k[1]} m kutt · ${k[5]} kg` }
const V = [
  ['k5', 'A · 5 × 5', '4 mm. Kula slik du såg ho, no med hol til pæra.'],
  ['k7', 'B · 7 × 7', '3 mm. Tettare, meir flate enn plate.'],
  ['k9', 'C · 9 × 9', '3 mm. Finaste rutenettet.'],
  ['k3', 'D · 3 × 3', '6 mm. Seks store skiver.'],
  ['k4', 'E · 4 × 4', '4 mm. Ingen plate i midten: open sjakt.'],
  ['k6h', 'F · 6 × 6 pendel', '4 mm. Heng i leidningen, lyser ned.'],
  ['kskra', 'G · 5 × 5 i 60°', '4 mm. Rombar i staden for ruter.'],
  ['khell', 'H · 5 × 5 helt 45°', '4 mm. Krossane ligg; ruter på høgkant.'],
  ['kstor', 'I · golvkule Ø 580', '6 mm, 7 × 7. Så stor appen tek.'],
]
const css = `*{box-sizing:border-box}body{margin:0;background:#fff;color:#111;font:15px/1.4 -apple-system,Helvetica,Arial,sans-serif;width:1680px;padding:34px 36px}
h1{font-size:30px;font-weight:600;margin:0 0 4px}.under{color:#666;margin:0 0 22px}
.rutenett{display:grid;grid-template-columns:repeat(3,1fr);gap:22px 20px}.par{display:grid;grid-template-columns:1fr 1fr;gap:2px}
img{width:100%;display:block}h2{font-size:18px;font-weight:600;margin:8px 0 0}p.t{margin:1px 0 0;font-size:13px;color:#444}p.n{margin:1px 0 0;font-size:12px;color:#888;font-variant-numeric:tabular-nums}`
const html = `<!doctype html><meta charset="utf-8"><style>${css}</style><body><h1>Kula — ni variantar, alle skorne av motoren</h1><p class="under">Same idé: ei kule av kryssande skiver med halvt-i-halvt-spor, hol i midten til pæra. Kvar held alle harde reglar. Venstre: i dagslys. Høgre: i mørkt rom, lyset kjem frå pæra.</p><div class="rutenett">` +
  V.map(([v, n, t]) => `<div><div class="par"><img src="file://${K}/studie/${v}-helt.png"><img src="file://${K}/studie/${v}-lys.png"></div><h2>${n}</h2><p class="t">${t}</p><p class="n">${tal(v)}</p></div>`).join('') + `</div></body>`
;(async () => {
  fs.writeFileSync(`${K}/studie/tavle.html`, html)
  const b = await chromium.launch(); const c = await b.newContext({ viewport: { width: 1680, height: 1000 }, deviceScaleFactor: 1.5 }); const s = await c.newPage()
  await s.goto(`file://${K}/studie/tavle.html`); await s.waitForTimeout(500)
  await s.screenshot({ path: `${K}/studie/kula-ni.png`, fullPage: true })
  console.log(await s.evaluate(() => [document.body.scrollHeight, [...document.images].filter((i) => !i.naturalWidth).length]))
  await b.close()
})()
