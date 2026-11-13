# -*- coding: utf-8 -*-
"""lag_ark.py · oversiktsarket for byggjesettet, i husstilen frå fase 1 (1127 × 797, svart, EB Garamond og Consolas)

Les storleiken på delbileta (render/del-*.json, rendra med fast tal pikslar per mm) og måla (maal.json), og set alle
delane på to hyller i same målestokk. Målestokken S (px på arket per mm) blir så stor som arket tillèt.

  python lag_ark.py          skriv ark/byggjesett.html og ark/byggjesett.png (2254 × 1594)
"""
import json, os, subprocess, tempfile, shutil

HER = os.path.dirname(os.path.abspath(__file__))
ROT = os.path.dirname(HER)
CSS = os.path.relpath(os.path.join(ROT, '..', '..', 'leveransar', '01_fase1_v2', 'felles.css'), HER).replace('\\', '/')
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
D = json.load(open(os.path.join(ROT, 'maal.json'), encoding='utf-8'))

B_HYLLE, H_HYLLE = 1039, 596          # plassen mellom tittelen og botnlina
GAP, MIN_CELLE, LINE = 26, 128, 13.5  # luft mellom delane, minste breidd for etiketten, linehøgd i etiketten (10 px × 1,35)
RADER = [['samla', 'P05', 'P04', 'P08'], ['P01', 'P03', 'P02', 'P07', 'P06', 'P09']]


def m(pid, k):
    return D[pid][k][0]


def pm(pid, *k):
    return max(D[pid][x][1] for x in k)


def tal(x):
    return f'{x:g}'.replace('.', ',')


def x3(pid, *k):
    return ' × '.join(tal(m(pid, x)) for x in k)


ETIKETT = {
    'samla': ['<b>Projektoren samla</b>', 'rekonstruksjon frå delane', 'ikkje målt'],
    'P01': ['<b>P01 arm</b>', x3('P01', 'profil_lengd', 'profil_breidd', 'profil_tjukk'),
            f"inntil ± {tal(pm('P01', 'profil_lengd', 'profil_breidd', 'profil_tjukk'))}"],
    'P02': ['<b>P02 hengsel</b>', x3('P02', 'lengd', 'breidd', 'hogd'), f"inntil ± {tal(pm('P02', 'lengd', 'breidd', 'hogd'))}"],
    'P03': ['<b>P03 hovud</b>', x3('P03', 'lengd', 'breidd', 'hogd'), f"inntil ± {tal(pm('P03', 'lengd', 'breidd', 'hogd'))}",
            f"vifte {tal(m('P03', 'vifte'))}, typeskilt"],
    'P04': ['<b>P04 base</b>', x3('P04', 'lengd', 'breidd', 'hogd'), f"inntil ± {tal(pm('P04', 'lengd', 'breidd', 'hogd'))}",
            '<b>230 V: skal aldri koplast til</b>'],
    'P05': ['<b>P05 fresnelspegel</b>', f"vindauge {tal(m('P05', 'vindauge'))} · f {tal(round(m('P05', 'brennvidd')))}", 'deleliste',
            '<b>aldri i sol</b>'],
    'P06': ['<b>P06 glaslinse</b>', f"Ø {x3('P06', 'd', 'hogd')}", f"inntil ± {tal(pm('P06', 'd', 'hogd'))}", '<b>aldri i sol</b>'],
    'P07': ['<b>P07 projeksjonslinse</b>', f"Ø {x3('P07', 'fatning_d', 'fatning_hogd')}", f"inntil ± {tal(pm('P07', 'fatning_d', 'fatning_hogd'))}",
            f"f ≈ {tal(m('P07', 'brennvidd'))}"],
    'P08': ['<b>P08 prismeark</b>', x3('P08', 'breidd', 'hogd', 'tjukk'), f"inntil ± {tal(pm('P08', 'breidd', 'hogd'))}",
            'frå monitoren, berre form'],
    'P09': ['<b>P09 FSX-pære</b>', f"Ø {x3('P09', 'd', 'lengd')}", 'deleliste'],
}


def mm(namn):
    j = json.load(open(os.path.join(ROT, 'render', f'del-{namn}.json'), encoding='utf-8'))
    return j['w'] / j['px_per_mm'], j['h'] / j['px_per_mm']


def oppsett(S):
    """Breidd og høgd for kvar hylle ved målestokk S, med etikettane under biletet."""
    rader = []
    for rad in RADER:
        celler = []
        for n in rad:
            w, h = (v * S for v in mm(n))
            celler.append(dict(n=n, w=w, h=h, cw=max(w, MIN_CELLE)))
        hb = max(c['h'] for c in celler)
        he = max(len(ETIKETT[c['n']]) for c in celler) * LINE + 7
        b = sum(c['cw'] for c in celler) + GAP * (len(celler) - 1)
        rader.append(dict(celler=celler, hb=hb, he=he, b=b))
    return rader


def finn_S():
    lo, hi = 0.2, 2.0
    for _ in range(40):
        S = (lo + hi) / 2
        r = oppsett(S)
        b = max(r[0]['b'], r[1]['b'] + GAP + 100 * S + 40)        # målestokklina står til høgre på nedste hylle
        h = sum(x['hb'] + x['he'] for x in r) + 22
        lo, hi = (S, hi) if (b <= B_HYLLE and h <= H_HYLLE) else (lo, S)
    return lo


def html(S):
    r = oppsett(S)
    del_html = []
    for i, rad in enumerate(r):
        fig = []
        for c in rad['celler']:
            fig.append(f'''      <figure class="del" style="width:{c['cw']:.1f}px">
        <div class="hylle" style="height:{rad['hb']:.1f}px"><img src="../render/del-{c['n']}.png" alt="" style="width:{c['w']:.1f}px;height:{c['h']:.1f}px"></div>
        <figcaption>{'<br>'.join(ETIKETT[c['n']])}</figcaption>
      </figure>''')
        if i == 1:
            fig.append(f'''      <figure class="del skala" style="width:{max(100 * S, 60):.1f}px">
        <div class="hylle" style="height:{rad['hb']:.1f}px"><div class="strek" style="width:{100 * S:.1f}px"></div></div>
        <figcaption><b>100 mm</b><br>alle delane i same<br>målestokk</figcaption>
      </figure>''')
        del_html.append(f'    <div class="rad" style="margin-top:{0 if i == 0 else 22}px">\n' + '\n'.join(fig) + '\n    </div>')
    return f'''<!doctype html>
<html lang="nn">
<head>
<meta charset="utf-8">
<title>Byggjesettet i 3D</title>
<link rel="stylesheet" href="{CSS}">
<style>
  .rad {{ display: flex; gap: {GAP}px; align-items: flex-start; }}
  .del .hylle {{ display: flex; align-items: flex-end; }}
  .del img {{ display: block; }}
  .del figcaption {{ margin-top: 7px; line-height: 1.35; }}
  .skala {{ margin-left: auto; }}
  .skala .strek {{ height: 6px; border: 1px solid #F4F4F4; border-top: 0; }}
</style>
</head>
<body>
<div class="side">
  <header class="topp">
    <span>GK5 · Northern · byggjesett</span>
    <span>Byggjesettet i 3D</span>
    <span>Iver R. Finne · 13.11.2026</span>
  </header>

  <h1 class="tittel">Ni delar i same målestokk, klare til skisser.</h1>

  <main class="innhald" style="display: block;">
{chr(10).join(del_html)}
  </main>

  <footer class="botn">
    <span>Mål i mm. Delelista til 3M 2000 og typeskiltet på vifta gjev dei sikre måla, resten er anslått frå foto 13.11.2026.</span>
    <span>Ingenting er målt med linjal enno.</span>
  </footer>
</div>
</body>
</html>
'''


if __name__ == '__main__':
    S = finn_S()
    fil = os.path.join(HER, 'byggjesett.html')
    open(fil, 'w', encoding='utf-8').write(html(S))
    print(f'målestokk {S:.3f} px/mm', [round(x['b']) for x in oppsett(S)], round(sum(x['hb'] + x['he'] for x in oppsett(S)) + 22))
    tmp = tempfile.mkdtemp()
    try:
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', f'--user-data-dir={tmp}',
                        '--force-device-scale-factor=2', '--window-size=1127,797', '--default-background-color=000000ff',
                        '--virtual-time-budget=6000', f'--screenshot={os.path.join(HER, "byggjesett.png")}',
                        'file:///' + fil.replace('\\', '/')], capture_output=True, timeout=120)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('skrive', fil, 'og byggjesett.png')
