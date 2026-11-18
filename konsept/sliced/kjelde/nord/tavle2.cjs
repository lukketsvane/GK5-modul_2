const { chromium } = require('playwright')
const fs = require('fs')
const K = '/tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/nord'
const tal = (v) => { const t = fs.readFileSync(`${K}/${v}s/ut/rapport.txt`, 'utf8'); const a = /(\d+) delar/.exec(t), l = /(\d+) ledd/.exec(t), k = /kutt\s+([\d.]+) m.*?(\d+) ark (\d+ x \d+).*?([\d.]+) kg/.exec(t); return `${a[1]} plater · ${l[1]} ledd · ${k[2]} ark ${k[3]} · ${k[1]} m kutt · kula ${k[4]} kg` }
const V = [
  ['n5', '5 · Globus 180, mørkegrøn', 'Kula heng i ein tynn bøyel på stilk og rund fot. Vipp henne om messingtappane.', 'høgd 345 · fot Ø 150 (177 cm²)'],
  ['n6', '6 · Globus 220, svart', 'Same oppbygging, større kule: meir lys ut, meir plass til lysmodulen.', 'høgd 385 · fot Ø 158 (196 cm²)'],
  ['n7', '7 · Globus 180, gråbeige', 'Den lyse varianten. Dei brende kantane teiknar kvar plate.', 'høgd 345 · fot Ø 150 (177 cm²)'],
]
const css = `*{box-sizing:border-box}body{margin:0;background:#fff;color:#111;font:15px/1.4 -apple-system,Helvetica,Arial,sans-serif;width:1720px;padding:34px 36px}
h1{font-size:30px;font-weight:600;margin:0 0 6px}.under{color:#444;margin:0 0 6px;font-size:16px;max-width:1300px}.krav{color:#777;margin:0 0 22px;font-size:13px;max-width:1400px}
.rad{margin-bottom:22px}.fire{display:grid;grid-template-columns:repeat(4,1fr);gap:2px}img{width:100%;display:block}
.merke{display:grid;grid-template-columns:1fr 1fr;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:#777;margin-bottom:3px}
h2{font-size:18px;font-weight:600;margin:8px 0 0}p.t{margin:1px 0 0;font-size:14px;color:#333}p.n{margin:1px 0 0;font-size:12px;color:#888;font-variant-numeric:tabular-nums}
.fot{border-top:1px solid #ddd;padding-top:10px;color:#555;font-size:13px;max-width:1400px}`
const html = `<!doctype html><meta charset="utf-8"><style>${css}</style><body><h1>Northern · GK5 modul 2 — Globus: kula i Northern-språket</h1>
<p class="under">Tre enkle former: kule, tynn line, rund fot. Éin matt farge, éin messingdetalj. Éi handling: <b>vipp kula</b>. Holet opp og bak er stemning, holet ned er arbeid.</p>
<p class="krav">Frå <code>grunnlag/00-ramme.md</code>, punkt 7: to til tre additive primærformer · ei tynn line som ber eit kompakt lyshovud · lyskjelda er aldri naken · éin matt farge · éin liten messingdetalj som aksent og betjening · ei leiken fysisk handling.</p>` +
  V.map(([v, n, t, m]) => `<div class="rad"><div class="merke"><span>stemning · holet opp og bak</span><span>arbeid · holet ned</span></div><div class="fire"><img src="file://${K}/tavle/${v}-s-helt.png"><img src="file://${K}/tavle/${v}-s-lys.png"><img src="file://${K}/tavle/${v}-a-helt.png"><img src="file://${K}/tavle/${v}-a-lys.png"></div><h2>${n}</h2><p class="t">${t}</p><p class="n">${tal(v)} · ${m}</p></div>`).join('') +
  `<p class="fot">Kula er skoren av motoren i slicerman og held alle harde reglar i begge stillingar. Bøyel, stilk, fot, messingtappar og patron er teikna ved sida av motoren, og festet mellom tapp og kule er ikkje løyst. Bileta viser kvar lyset går, ikkje lux: 350 lx på feltet (F3), blending (F1) og velting (T2) er ikkje rekna eller målte.</p></body>`
;(async () => {
  fs.writeFileSync(`${K}/tavle/tavle.html`, html)
  const b = await chromium.launch(); const c = await b.newContext({ viewport: { width: 1720, height: 1000 }, deviceScaleFactor: 1.5 }); const s = await c.newPage()
  await s.goto(`file://${K}/tavle/tavle.html`); await s.waitForTimeout(500)
  await s.screenshot({ path: `${K}/tavle/northern-globus.png`, fullPage: true })
  console.log(await s.evaluate(() => [document.body.scrollHeight, [...document.images].filter((i) => !i.naturalWidth).length]))
  await b.close()
})()
