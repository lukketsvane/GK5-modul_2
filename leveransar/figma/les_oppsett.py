# -*- coding: utf-8 -*-
"""Les oppsettet av sidene i hovudlaus Chrome: tekstblokker (med løp), liner/flater, bilete og SVG-figurar.
Skriv oppsett/<side>.json, bilete/<side>-<n>.png (beskorne som på sida, 2x) og svg/<side>-<n>.png (2x, gjennomsiktig)."""
import os, sys, re, json, html, subprocess, tempfile, shutil
from PIL import Image

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
UT = os.path.dirname(os.path.abspath(__file__))
for d in ('oppsett', 'bilete', 'svg'):
    os.makedirs(os.path.join(UT, d), exist_ok=True)

JS = r"""
<script>
(function(){
function px(v){ return parseFloat(v) || 0; }
function rgb(c){ const m = (c||'').match(/rgba?\(([^)]+)\)/); if(!m) return null; const p = m[1].split(',').map(s=>parseFloat(s)); return {r:p[0]/255, g:p[1]/255, b:p[2]/255, a: p.length>3? p[3] : 1}; }
function run(){
 const root = document.querySelector('.side') || document.querySelector('.lb') || document.body;
 const R = root.getBoundingClientRect();
 const out = {w: R.width, h: R.height, bg: rgb(getComputedStyle(root).backgroundColor) || rgb(getComputedStyle(document.body).backgroundColor), texts: [], rects: [], imgs: [], svgs: []};
 const rel = r => ({x: r.left - R.left, y: r.top - R.top, w: r.width, h: r.height});
 const blockOf = el => { let e = el; while (e && e !== root) { const d = getComputedStyle(e).display; if (d !== 'inline' && d !== 'contents') return e; e = e.parentElement; } return root; };
 const blocks = new Map(); const order = [];
 const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
 let n;
 while ((n = walker.nextNode())) {
   if (n.nodeType === 1) {
     if (n.tagName === 'BR') { const b = blockOf(n.parentElement); if (!blocks.has(b)) { blocks.set(b, []); order.push(b); } blocks.get(b).push({t: '\n', br: 1}); }
     continue;
   }
   const pe = n.parentElement; if (!pe || pe.closest('svg') || pe.closest('pre#LAYOUT')) continue;
   const cs = getComputedStyle(pe);
   if (cs.visibility === 'hidden' || cs.display === 'none') continue;
   let t = n.nodeValue.replace(/[ \t\r\n]+/g, ' ');
   if (!t.replace(/ /g, '')) { const b = blockOf(pe); if (blocks.has(b)) blocks.get(b).push({t: ' ', sp: 1}); continue; }
   if (cs.textTransform === 'uppercase') t = t.toUpperCase();
   const b = blockOf(pe);
   if (!blocks.has(b)) { blocks.set(b, []); order.push(b); }
   blocks.get(b).push({t, ff: cs.fontFamily, fs: px(cs.fontSize), fw: cs.fontWeight, fst: cs.fontStyle, c: rgb(cs.color), ls: cs.letterSpacing === 'normal' ? 0 : px(cs.letterSpacing)});
 }
 for (const b of order) {
   const runs = blocks.get(b); if (!runs.some(r => r.ff)) continue;
   const cs = getComputedStyle(b);
   const rg = document.createRange(); rg.selectNodeContents(b);
   const rects = Array.from(rg.getClientRects()).filter(r => r.width > 0.5 && r.height > 0.5);
   const rr = rg.getBoundingClientRect(); const br = b.getBoundingClientRect();
   const lines = new Set(rects.map(r => Math.round(r.top))).size;
   const innW = br.width - px(cs.paddingLeft) - px(cs.paddingRight) - px(cs.borderLeftWidth) - px(cs.borderRightWidth);
   out.texts.push({x: rr.left - R.left, y: rr.top - R.top, w: rr.width, h: rr.height, bx: br.left - R.left + px(cs.paddingLeft) + px(cs.borderLeftWidth), bw: innW, lines, runs, lh: cs.lineHeight === 'normal' ? null : px(cs.lineHeight), ta: cs.textAlign, nowrap: cs.whiteSpace === 'nowrap'});
 }
 for (const el of root.querySelectorAll('*')) {
   if (el.closest('svg')) continue;
   const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
   const r = el.getBoundingClientRect(); if (r.width < 0.5 && r.height < 0.5) continue;
   const bg = rgb(cs.backgroundColor);
   if (bg && bg.a > 0.01 && el.tagName !== 'IMG') out.rects.push({...rel(r), c: bg});
   for (const s of ['Top','Right','Bottom','Left']) {
     const w = px(cs['border'+s+'Width']); const st = cs['border'+s+'Style']; const c = rgb(cs['border'+s+'Color']);
     if (w > 0 && st !== 'none' && c && c.a > 0.01) {
       let x = r.left - R.left, y = r.top - R.top, ww = r.width, hh = r.height;
       if (s === 'Top') hh = w; else if (s === 'Bottom') { y = y + r.height - w; hh = w; } else if (s === 'Left') ww = w; else { x = x + r.width - w; ww = w; }
       out.rects.push({x, y, w: ww, h: hh, c, dash: (st === 'dashed' || st === 'dotted') ? 1 : 0});
     }
   }
 }
 for (const im of root.querySelectorAll('img')) {
   const cs = getComputedStyle(im); const r = im.getBoundingClientRect();
   out.imgs.push({...rel(r), src: im.getAttribute('src'), nw: im.naturalWidth, nh: im.naturalHeight, fit: cs.objectFit, pos: cs.objectPosition});
 }
 for (const sv of root.querySelectorAll('svg')) {
   if (sv.parentElement && sv.parentElement.closest('svg')) continue;
   const r = sv.getBoundingClientRect(); if (r.width < 1) continue;
   const kl = sv.cloneNode(true);
   const src = [sv, ...sv.querySelectorAll('*')], dst = [kl, ...kl.querySelectorAll('*')];
   src.forEach((e, i) => {
     const cs = getComputedStyle(e); const d = dst[i];
     const props = ['fill','stroke','stroke-width','stroke-dasharray','opacity','font-family','font-size','font-weight','font-style','letter-spacing','text-anchor','dominant-baseline','fill-opacity','stroke-opacity','stroke-linecap','stroke-linejoin','font-variant-numeric','font-feature-settings'];
     let st = '';
     for (const p of props) { const v = cs.getPropertyValue(p); if (v) st += p + ':' + v + ';'; }
     d.setAttribute('style', st);
     if (e.tagName === 'text' && cs.textTransform === 'uppercase') d.textContent = e.textContent.toUpperCase();
   });
   kl.setAttribute('width', r.width); kl.setAttribute('height', r.height);
   out.svgs.push({...rel(r), svg: kl.outerHTML});
 }
 const pre = document.createElement('pre'); pre.id = 'LAYOUT'; pre.textContent = JSON.stringify(out); document.body.appendChild(pre);
}
document.fonts.ready.then(() => setTimeout(run, 80));
})();
</script>
"""


def chrome(args, timeout=120):
    tmp = tempfile.mkdtemp()
    try:
        return subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-first-run', f'--user-data-dir={tmp}', '--hide-scrollbars'] + args,
                              capture_output=True, timeout=timeout)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def les(htmlfil, namn, w=1127, h=797):
    mappe = os.path.dirname(htmlfil)
    s = open(htmlfil, encoding='utf-8').read()
    s = s.replace('</body>', JS + '</body>')
    tmpfil = os.path.join(mappe, f'_oppsett_{namn}.html')
    open(tmpfil, 'w', encoding='utf-8').write(s)
    try:
        r = chrome([f'--window-size={w},{h}', '--virtual-time-budget=8000', '--dump-dom', 'file:///' + tmpfil.replace('\\', '/')])
    finally:
        os.remove(tmpfil)
    dom = r.stdout.decode('utf-8', 'replace')
    m = re.search(r'<pre id="LAYOUT">(.*?)</pre>', dom, re.S)
    if not m:
        sys.exit(f'fann ikkje oppsettet for {namn}: {r.stderr.decode(errors="replace")[:500]}')
    d = json.loads(html.unescape(m.group(1)))
    # bilete: beskjer som på sida (object-fit cover og object-position), 2x
    for i, im in enumerate(d['imgs']):
        fil = os.path.normpath(os.path.join(mappe, im['src']))
        b = Image.open(fil).convert('RGB'); nw, nh = b.size
        W, H = im['w'], im['h']
        if im['fit'] == 'cover':
            s_ = max(W / nw, H / nh); cw, ch = W / s_, H / s_
            px_, py_ = [float(v.strip('%')) / 100 if v.endswith('%') else 0.5 for v in (im['pos'].split() + ['50%'])[:2]]
            x0 = (nw - cw) * px_; y0 = (nh - ch) * py_
            b = b.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch)))
        b = b.resize((max(1, round(W * 2)), max(1, round(H * 2))), Image.LANCZOS)
        ut = os.path.join(UT, 'bilete', f'{namn}-{i}.png'); b.save(ut)
        im['fil'] = ut
    # SVG-figurar: render kvar for seg, gjennomsiktig, 2x
    css = os.path.join(mappe, 'felles.css').replace('\\', '/')
    for i, sv in enumerate(d['svgs']):
        side = (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="file:///{css}">'
                '<style>html,body{margin:0;padding:0;background:transparent!important}svg{display:block}</style></head><body>' + sv['svg'] + '</body></html>')
        tmp = os.path.join(mappe, f'_svg_{namn}_{i}.html'); open(tmp, 'w', encoding='utf-8').write(side)
        ut = os.path.join(UT, 'svg', f'{namn}-{i}.png')
        try:
            chrome([f'--window-size={int(sv["w"] + 1)},{int(sv["h"] + 1)}', '--force-device-scale-factor=2', '--default-background-color=00000000',
                    '--virtual-time-budget=4000', f'--screenshot={ut}', 'file:///' + tmp.replace('\\', '/')])
        finally:
            os.remove(tmp)
        sv['fil'] = ut
        sv['svg'] = None
    json.dump(d, open(os.path.join(UT, 'oppsett', namn + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    return d


if __name__ == '__main__':
    for htmlfil in sys.argv[1:]:
        namn = os.path.splitext(os.path.basename(htmlfil))[0]
        d = les(os.path.abspath(htmlfil), namn)
        print(namn, f"tekst {len(d['texts'])} flater {len(d['rects'])} bilete {len(d['imgs'])} svg {len(d['svgs'])}", flush=True)
