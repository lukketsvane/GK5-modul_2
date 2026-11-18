const { chromium } = require('playwright')
const fs = require('fs')
const K = '/tmp/claude-0/-home-user-slicer-iverfinne-no/0351339b-1ff7-580f-bca7-9071db1d2f3c/scratchpad/lampe/nord3'
const T = [
  ['globus/maane-par.png', '1 · Måne 200', 'Gråbeige kule av 8 + 8 tynne spegelskiver i ein halvbøyel på stilk. Skivene står vinkelrett på vippeaksen, så ytste skive på kvar side er eit flatt kinn som tappen går gjennom. Einaste messing er krona på lysmodulen.', '16 plater · 52 ledd · 2 ark 600 × 400 · kula 0,44 kg (2 mm spegelakryl)', 'Kritikaren, 7,5: den einaste som les som ei kule før ho les som plater. Neste grep: ein opal lekam rundt kjelda, så spegelen gjentek ei mjuk kule og ikkje eit punkt.'],
  ['fri/blunk-par.png', '2 · Blunk', 'Eit halvkuleskal som vrir seg som eit augelok rundt ei fast opal kule, bore av ei L-forma line. Skalet opp og bak: kula lyser mot veggen. Skalet over kula: lyset fell ned.', '12 plater · 24 ledd · 1 ark 600 × 400 · skalet 0,34 kg (3 mm) · høgd 350', 'Kritikaren, 7: den beste nye ideen og den mest heimlege silhuetten. Neste grep: tettare skal, 8 + 8 tynnare plater.'],
  ['raster/rist-par.png', '3 · Rist', 'Ein matt mørkegrøn trommel på ein tynn stilk. Spegelgitteret ligg skjult inni, under ein flat lysmodul, og er eit ekte blendingsraster. Vipp trommelen om messingtappen.', '10 plater · 21 ledd · 1 ark 600 × 400 · gitteret 0,16 kg (3 mm) · høgd 450', 'Kritikaren, 6,5: den som mest liknar eit ferdig Northern-produkt. Neste grep: hellande blad med spegel berre på sida som vender bort frå auget.'],
]
const R = [
  ['globus/perle-par.png', 'Perle 180', '5 — same idé som Måne, grovare. Dei lyse kuttkantane bryt den eine fargen.'],
  ['raster/blad-par.png', 'Blad', '3,5 — fin i arbeid, men blada står nakne i stemning, og lysbileta er for mørke til å lese.'],
  ['fri/trakt-par.png', 'Trakt', '2 — åtte plater vert ikkje ei kjegle. Handlinga er god, kroppen er det ikkje.'],
]
const css = `*{box-sizing:border-box}body{margin:0;background:#fff;color:#111;font:15px/1.4 -apple-system,Helvetica,Arial,sans-serif;width:1720px;padding:34px 36px}
h1{font-size:30px;font-weight:600;margin:0 0 6px}.under{color:#444;margin:0 0 20px;font-size:16px;max-width:1350px}
.rad{margin-bottom:24px}img{width:100%;display:block}.merke{display:grid;grid-template-columns:1fr 1fr;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:#777;margin-bottom:3px}
h2{font-size:19px;font-weight:600;margin:8px 0 0}p.t{margin:2px 0 0;font-size:14px;color:#222;max-width:1300px}p.n{margin:2px 0 0;font-size:12px;color:#888}p.k{margin:2px 0 0;font-size:13px;color:#555;max-width:1300px}
h3{font-size:15px;font-weight:600;margin:26px 0 8px;color:#555}.tre{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.tre h2{font-size:15px}.tre p.k{font-size:12px}
.fot{border-top:1px solid #ddd;margin-top:22px;padding-top:10px;color:#555;font-size:13px;max-width:1400px}`
const html = `<!doctype html><meta charset="utf-8"><style>${css}</style><body><h1>Northern · GK5 modul 2 — spegel mot innsida</h1>
<p class="under">Seks nye design. Platene er spegelakryl med spegelen inn og éin matt farge ut. Dei tre øvste er dei kritikaren sette fyrst mot Northern-formspråket og krava dine.</p>` +
  T.map(([f, n, t, tal, k]) => `<div class="rad"><div class="merke"><span>stemning</span><span>arbeid</span></div><img src="file://${K}/${f}"><h2>${n}</h2><p class="t">${t}</p><p class="n">${tal}</p><p class="k">${k}</p></div>`).join('') +
  `<h3>Dei tre andre</h3><div class="tre">` + R.map(([f, n, k]) => `<div><img src="file://${K}/${f}"><h2>${n}</h2><p class="k">${k}</p></div>`).join('') + `</div>` +
  `<p class="fot">Alle seks held dei harde reglane i motoren i begge stillingar. I lysbileta er 240 000 strålar følgde gjennom opptil åtte spegelrefleksar; dei viser kvar lyset går, ikkje lux. Bøyel, stilk, fot, tappar, opalkule og trommelhus er berre teikna. At spegelen ikkje kastar kjelda mot auget (F1) er ikkje prøvd. Vektene er den skorne kroppen åleine.</p></body>`
;(async () => {
  fs.writeFileSync(`${K}/tavle/tavle.html`, html)
  const b = await chromium.launch(); const c = await b.newContext({ viewport: { width: 1720, height: 1000 }, deviceScaleFactor: 1.5 }); const s = await c.newPage()
  await s.goto(`file://${K}/tavle/tavle.html`); await s.waitForTimeout(600)
  await s.screenshot({ path: `${K}/tavle/northern-spegl.png`, fullPage: true })
  console.log(await s.evaluate(() => [document.body.scrollHeight, [...document.images].filter((i) => !i.naturalWidth).length]))
  await b.close()
})()
