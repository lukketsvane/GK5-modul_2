const { chromium } = require('playwright')
const fs = require('fs')
const K = '/tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/nord'
const tal = (v) => { const t = fs.readFileSync(`${K}/${v}s/ut/rapport.txt`, 'utf8'); const a = /(\d+) delar/.exec(t), l = /(\d+) ledd/.exec(t), k = /kutt\s+([\d.]+) m.*?(\d+) ark (\d+ x \d+).*?([\d.]+) kg/.exec(t); return `${a[1]} plater · ${l[1]} ledd · ${k[2]} ark ${k[3]} · ${k[1]} m kutt · ${k[4]} kg utan elektronikk` }
const V = [
  ['n1', '1 · Kule 220, bjørk', 'Kula ligg i ein bukk av to kryssa bogar. Ø 220, 3 mm bjørk, 6 × 6.', 'høgd 370 · føtene innanfor 127 × 127 mm (162 cm²)'],
  ['n2', '2 · Kule 220, opal', 'Same kule i opal akryl: heile gitteret lyser i stemning. Bukken i bjørk.', 'høgd 370 · 162 cm²'],
  ['n3', '3 · Kule 180, liten', 'Den kompakte: Ø 180 på låg bukk. Lettast å flytte med éi hand.', 'høgd 285 · føtene innanfor 106 × 106 mm (112 cm²)'],
  ['n4', '4 · Kule 240, tett', '8 × 8: tettare gitter gjev mjukare lys og skjermar kjelda betre.', 'høgd 405 · føtene innanfor 134 × 134 mm (180 cm²)'],
]
const css = `*{box-sizing:border-box}body{margin:0;background:#fff;color:#111;font:15px/1.4 -apple-system,Helvetica,Arial,sans-serif;width:1720px;padding:34px 36px}
h1{font-size:30px;font-weight:600;margin:0 0 6px}.under{color:#444;margin:0 0 6px;font-size:16px;max-width:1300px}.krav{color:#777;margin:0 0 22px;font-size:13px;max-width:1400px}
.rad{margin-bottom:22px}.fire{display:grid;grid-template-columns:repeat(4,1fr);gap:2px}img{width:100%;display:block}
.merke{display:grid;grid-template-columns:1fr 1fr;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:#777;margin-bottom:3px}
h2{font-size:18px;font-weight:600;margin:8px 0 0}p.t{margin:1px 0 0;font-size:14px;color:#333}p.n{margin:1px 0 0;font-size:12px;color:#888;font-variant-numeric:tabular-nums}
.fot{border-top:1px solid #ddd;padding-top:10px;color:#555;font-size:13px;max-width:1400px}`
const html = `<!doctype html><meta charset="utf-8"><style>${css}</style><body><h1>Northern · GK5 modul 2 — kula som svarar på briefen</h1>
<p class="under">Éi handling: <b>snu kula</b>. Holet opp og bak: stemning, veggen bak skjermen lyser. Holet ned: arbeid, lyset fell på bordet gjennom bukken og kjelda er ikkje synleg.</p>
<p class="krav">Mot krava dine: F2 éi handling · F1 inga synleg lyskjelde i arbeid · F6 lys på veggen i stemning · F8 under 1,2 kg · F9 under 200 cm² bordplass · E3 holet viser kvar lyset går · E5 leiken handling · B1 batteri og lysmodul i ein patron som vert dregen ut bak.</p>` +
  V.map(([v, n, t, m]) => `<div class="rad"><div class="merke"><span>stemning · holet opp og bak</span><span>arbeid · holet ned</span></div><div class="fire"><img src="file://${K}/tavle/${v}-s-helt.png"><img src="file://${K}/tavle/${v}-s-lys.png"><img src="file://${K}/tavle/${v}-a-helt.png"><img src="file://${K}/tavle/${v}-a-lys.png"></div><h2>${n}</h2><p class="t">${t}</p><p class="n">${tal(v)} · ${m}</p></div>`).join('') +
  `<p class="fot">Kula er skoren av motoren i slicerman og held alle harde reglar i begge stillingar. Bukken (to plater) og patronen er teikna ved sida av motoren. Bileta viser kvar lyset går, ikkje lux: 350 lx på feltet (F3), blending (F1) og velting (T2) er ikkje rekna eller målte.</p></body>`
;(async () => {
  fs.writeFileSync(`${K}/tavle/tavle.html`, html)
  const b = await chromium.launch(); const c = await b.newContext({ viewport: { width: 1720, height: 1000 }, deviceScaleFactor: 1.5 }); const s = await c.newPage()
  await s.goto(`file://${K}/tavle/tavle.html`); await s.waitForTimeout(500)
  await s.screenshot({ path: `${K}/tavle/northern-kula.png`, fullPage: true })
  console.log(await s.evaluate(() => [document.body.scrollHeight, [...document.images].filter((i) => !i.naturalWidth).length]))
  await b.close()
})()
