# -*- coding: utf-8 -*-
"""Lagar kompakte use_figma-skript frå oppsett/*.json: éitt skript per gruppe av sider."""
import os, sys, json, re

UT = os.path.dirname(os.path.abspath(__file__))
SIDER = [('side-1-debrief', '1 Debrief'), ('side-2-bransjeresearch', '2 Bransjeresearch'), ('side-3-3b-analyse', '3 3B-analyse'),
         ('side-4-kravspesifikasjon', '4 Kravspesifikasjon'), ('side-5-berekraftshandling', '5 Berekraftshandling'),
         ('side-6-prosjektplan', '6 Prosjektplan'), ('side-7-bedriftsbesok', '7 Bedriftsbesøk')]
GRUPPER = [(0, 1, 2), (3, 4), (5, 6)]


def hexa(c):
    h = '%02x%02x%02x' % tuple(max(0, min(255, round(c[k] * 255))) for k in 'rgb')
    a = round(c.get('a', 1), 2)
    return h if a >= 0.995 else f'{h}/{a}'


def font(r):
    mono = bool(re.search(r'consolas|mono|courier', r['ff'], re.I))
    w = int(float(r['fw'] or 400)); it = r['fst'] == 'italic'
    k = ('M' if mono else 'G') + {400: '', 500: 'M', 600: 'S', 700: 'B'}.get(min((400, 500, 600, 700), key=lambda x: abs(x - w)), '')
    return k + ('I' if it else '')


def r1(x):
    return round(x * 2) / 2


# Consolas har 0,55 em per teikn, IBM Plex Mono 0,60 em. Med denne faktoren blir monoteksten like brei som i HTML-en,
# og versalhøgda blir nesten den same (0,64 mot 0,70 × 0,917).
K_MONO = 0.55 / 0.60


def tekst(t):
    runs = []
    for r in t['runs']:
        if 'ff' not in r:                       # mellomrom eller linjeskift
            if runs:
                runs[-1][0] += r['t']
            continue
        k = font(r)
        fs = r['fs'] * (K_MONO if k.startswith('M') else 1)
        st = (k, round(fs, 2), hexa(r['c']), round(r['ls'], 2))     # storleik og sperring nøyaktig, ikkje til halve piksel
        if runs and tuple(runs[-1][1:]) == st:
            runs[-1][0] += r['t']
        else:
            runs.append([r['t'], *st])
    if not runs:
        return None
    runs[0][0] = runs[0][0].lstrip(' '); runs[-1][0] = runs[-1][0].rstrip(' \n')
    for r in runs:
        r[0] = re.sub(r' *\n *', '\n', r[0])
    runs = [r for r in runs if r[0]]
    if not runs:
        return None
    lh = t['lh']; y = t['y']
    n = max(1, round(t['h'] / lh)) if lh else t['lines']
    if lh:
        ch = t['h'] - (n - 1) * lh
        y = t['y'] - (lh - ch) / 2
    fler = n > 1 and not t['nowrap']
    ta = {'center': 'C', 'right': 'R', 'end': 'R'}.get(t['ta'], 'L')
    x = r1(t['bx']) if fler else r1(t['x'])
    w = r1(t['bw'] + 4) if fler else 0
    if not fler and ta != 'L':
        x, w, ta = r1(t['x']), 0, 'L'               # éi line: plasser der ho står, utan justering
    return [x, r1(y), w, r1(lh) if lh else 0, ta, runs]


BYGG = r"""
const F={G:['EB Garamond','Regular'],GI:['EB Garamond','Italic'],GM:['EB Garamond','Medium'],GMI:['EB Garamond','Medium Italic'],GS:['EB Garamond','SemiBold'],GSI:['EB Garamond','SemiBold Italic'],GB:['EB Garamond','Bold'],GBI:['EB Garamond','Bold Italic'],M:['IBM Plex Mono','Regular'],MI:['IBM Plex Mono','Italic'],MM:['IBM Plex Mono','Medium'],MMI:['IBM Plex Mono','Medium Italic'],MS:['IBM Plex Mono','SemiBold'],MSI:['IBM Plex Mono','SemiBold Italic'],MB:['IBM Plex Mono','Bold'],MBI:['IBM Plex Mono','Bold Italic']};
const fn=k=>({family:F[k][0],style:F[k][1]});
const brukt=new Set();for(const s of S)for(const t of s.t)for(const r of t[5])brukt.add(r[1]);
await Promise.all([...brukt].map(k=>figma.loadFontAsync(fn(k))));
const col=h=>{const[c,a]=h.split('/');return{p:{r:parseInt(c.slice(0,2),16)/255,g:parseInt(c.slice(2,4),16)/255,b:parseInt(c.slice(4,6),16)/255},a:a?+a:1}};
const paint=h=>{const c=col(h);return{type:'SOLID',color:c.p,opacity:c.a}};
const page=figma.root.children.find(p=>p.name==='Fase 1 · 13.11');
await figma.setCurrentPageAsync(page);
const ut=[];
for(const s of S){
 for(const n of page.children.filter(n=>n.name===s.namn))n.remove();
 const fr=figma.createFrame();page.appendChild(fr);fr.name=s.namn;fr.resize(s.w,s.h);fr.x=s.px;fr.y=0;fr.fills=[paint(s.bg)];fr.clipsContent=true;
 const ids={side:s.namn,frame:fr.id,bilete:[],svg:[]};
 for(const r of s.r){const n=figma.createRectangle();fr.appendChild(n);n.name='line';n.resize(Math.max(r[2],0.5),Math.max(r[3],0.5));n.x=r[0];n.y=r[1];n.fills=[paint(r[4])];}
 for(const b of s.b){const n=figma.createRectangle();fr.appendChild(n);n.name=b[4];n.resize(b[2],b[3]);n.x=b[0];n.y=b[1];n.fills=[{type:'SOLID',color:{r:.12,g:.12,b:.12}}];ids.bilete.push([n.id,b[4]]);}
 for(const b of s.v){const n=figma.createRectangle();fr.appendChild(n);n.name=b[4];n.resize(b[2],b[3]);n.x=b[0];n.y=b[1];n.fills=[];ids.svg.push([n.id,b[4]]);}
 for(const t of s.t){
  const n=figma.createText();fr.appendChild(n);n.fontName=fn(t[5][0][1]);
  n.characters=t[5].map(r=>r[0]).join('');
  let i=0;for(const r of t[5]){const j=i+r[0].length;if(j>i){n.setRangeFontName(i,j,fn(r[1]));n.setRangeFontSize(i,j,r[2]);n.setRangeFills(i,j,[paint(r[3])]);if(r[4])n.setRangeLetterSpacing(i,j,{unit:'PIXELS',value:r[4]});}i=j;}
  if(t[3])n.lineHeight={unit:'PIXELS',value:t[3]};
  n.textAlignHorizontal=t[4]==='C'?'CENTER':t[4]==='R'?'RIGHT':'LEFT';
  if(t[2]){n.textAutoResize='HEIGHT';n.resize(t[2],n.height);}else{n.textAutoResize='WIDTH_AND_HEIGHT';}
  n.x=t[0];n.y=t[1];n.name=n.characters.slice(0,40);
 }
 ut.push(ids);
}
return ut;
"""


def side_data(i):
    fil, namn = SIDER[i]
    d = json.load(open(os.path.join(UT, 'oppsett', fil + '.json'), encoding='utf-8'))
    t = [x for x in (tekst(t) for t in d['texts']) if x]
    r = [[r1(a['x']), r1(a['y']), r1(a['w']), r1(a['h']), hexa(a['c'])] for a in d['rects'] if not (a['w'] >= d['w'] - 1 and a['h'] >= d['h'] - 1)]
    b = [[r1(a['x']), r1(a['y']), r1(a['w']), r1(a['h']), 'bilete ' + os.path.basename(a['src'])] for a in d['imgs']]
    v = [[r1(a['x']), r1(a['y']), r1(a['w']), r1(a['h']), f'figur {k + 1}'] for k, a in enumerate(d['svgs'])]
    return dict(namn=f'Fase 1 · {namn}', w=round(d['w']), h=round(d['h']), px=i * (1127 + 120), bg=hexa(d['bg'] or {'r': 0, 'g': 0, 'b': 0}), t=t, r=r, b=b, v=v)


if __name__ == '__main__':
    for g, gr in enumerate(GRUPPER):
        S = [side_data(i) for i in gr]
        kode = 'const S=' + json.dumps(S, ensure_ascii=False, separators=(',', ':')) + ';' + BYGG.strip()
        open(os.path.join(UT, f'bygg_{g}.js'), 'w', encoding='utf-8').write(kode)
        print(f'bygg_{g}.js', len(kode), 'teikn', [s['namn'] for s in S])
