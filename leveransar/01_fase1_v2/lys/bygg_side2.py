# -*- coding: utf-8 -*-
"""Byggjer side-2-bransjeresearch.html frå tala i bilete/marknad.json og bilete/rom-overgang.json."""
import json, os

HER = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.normpath(os.path.join(HER, '..'))
M = json.load(open(os.path.join(V2, 'bilete', 'marknad.json'), encoding='utf-8'))

NB = '&nbsp;'


def heil(x):
    return f'{x:.0f}'


def cd(x):
    """Luminans: rund av til næraste ti over 1000."""
    return f'{round(x, -1):.0f}' if x >= 1000 else f'{x:.0f}'


def auge(d):
    return max(d['lampe_cd'], d['lysaste_flate_cd'])


# ---------------------------------------------------------------- lysfluks-figuren
W, X0, X1 = 598, 150, 590
S = (X1 - X0) / 1200.0
P = 11.2


def x(lm):
    return round(X0 + lm * S, 1)


def sirkel(lm, y, open_):
    k = 'opn' if open_ else 'fyll'
    return f'<circle cx="{x(lm)}" cy="{y}" r="3.2" class="{k}"/>'


def firkant(lm, y):
    return f'<rect x="{x(lm) - 3.2:.1f}" y="{y - 3.2:.1f}" width="6.4" height="6.4" class="opn"/>'


def trekant(lm, y):
    c = x(lm)
    return f'<path d="M{c} {y - 4:.1f} L{c + 4:.1f} {y + 3.2:.1f} L{c - 4:.1f} {y + 3.2:.1f} Z" class="opn"/>'


rader = []      # (y, svg)
y = 22.0
g = []
g.append(f'<rect x="{x(400)}" y="14" width="{x(800) - x(400):.1f}" height="{P * 11:.1f}" class="lysflate"/>')
g.append(f'<text x="0" y="9" class="kv">BATTERI</text>')
g.append(f'<text x="{x(50) + 2}" y="9" class="graa">stemning</text>')
g.append(f'<text x="{x(400) + 3}" y="9" class="graa">arbeid, 400 til 800{NB}lm</text>')


def rad(nr, namn, kvit=False):
    kl = 'kv' if kvit else 'graa'
    return f'<text x="0" y="{y + 3:.1f}" class="{kl}">{nr} {namn}</text>'


def strek(a, c, yy, tjukk=1, stipla=False, kl='kvs'):
    d = ' stroke-dasharray="2 3"' if stipla else ''
    return f'<line x1="{x(a)}" y1="{yy}" x2="{x(c)}" y2="{yy}" class="{kl}" stroke-width="{tjukk}"{d}/>'


batteri = [
    (1, 'HAY PC Portable', False, lambda yy: strek(85, 155, yy, 3)),
    (2, 'Fritz Hansen Clam', False, lambda yy: sirkel(126, yy, False)),
    (3, 'Marset FollowMe', False, lambda yy: sirkel(135, yy, False)),
    (4, 'LP Panthella 160', False, lambda yy: sirkel(150, yy, False)),
    (5, 'Northern Snowball', True, lambda yy: sirkel(158, yy, True)),
    (6, 'Zafferano Poldina Pro', False, lambda yy: sirkel(188, yy, True)),
    (7, 'Muuto Ease', False, lambda yy: sirkel(230, yy, True)),
    (8, 'LP PH 2/1 Portable', False, lambda yy: sirkel(289, yy, True)),
    (9, 'Philips Hue Go', False, lambda yy: strek(370, 530, yy, 1, True) + sirkel(370, yy, True) + sirkel(530, yy, True)
        + f'<text x="{x(530) + 9}" y="{yy + 3:.1f}" class="graa">berre ved 4000{NB}K</text>'),
    (10, 'Nimbus Roxxane', False, lambda yy: strek(25, 400, yy, 1) + strek(400, 800, yy, 1, True) + firkant(25, yy) + firkant(800, yy)
        + f'<text x="{x(800) + 9}" y="{yy + 3:.1f}" class="graa">berre i boost</text>'),
]
for nr, namn, kvit, f in batteri:
    g.append(rad(nr, namn, kvit)); g.append(f(round(y, 1))); y += P
# målet på batteri
g.append(f'<text x="0" y="{y + 3:.1f}" class="kv">MÅLET</text>')
g.append(strek(50, 200, round(y, 1), 3)); g.append(strek(200, 600, round(y, 1), 1.5, True))
g.append(f'<text x="{x(600) + 9}" y="{y + 3:.1f}" class="kv">arbeid i om lag to timar</text>')
y += P * 1.7
g.append(f'<line x1="62" y1="{y - 3:.1f}" x2="{X1}" y2="{y - 3:.1f}" class="haar"/>')
g.append(f'<text x="0" y="{y:.1f}" class="kv">LEIDNING</text>')
y += P * 1.25
g.append(f'<text x="0" y="{y + 3:.1f}" class="kv">MÅLET</text>')
g.append(strek(400, 800, round(y, 1), 3))
g.append(f'<text x="{x(800) + 9}" y="{y + 3:.1f}" class="kv">fullt arbeidslys</text>')
y += P
leidning = [
    (11, 'Logitech Litra Glow', False, lambda yy: trekant(250, yy)),
    (12, 'Luxo L-1', False, lambda yy: firkant(529, yy)),
    (13, 'Northern Salto', True, lambda yy: firkant(550, yy)),
    (14, 'Northern Archive', True, lambda yy: firkant(900, yy) + firkant(1100, yy)),
]
for nr, namn, kvit, f in leidning:
    g.append(rad(nr, namn, kvit)); g.append(f(round(y, 1))); y += P
ya = round(y + 2, 1)
g.append(f'<line x1="{X0}" y1="{ya}" x2="{X1}" y2="{ya}" class="strek"/>')
for lm in range(0, 1201, 200):
    g.append(f'<line x1="{x(lm)}" y1="{ya}" x2="{x(lm)}" y2="{ya + 4}" class="strek"/>')
    etik = f'{lm}{NB}lm' if lm == 1200 else str(lm)
    anker = 'end' if lm == 1200 else 'middle'
    g.append(f'<text x="{x(lm) + (6 if lm == 1200 else 0)}" y="{ya + 15}" class="graa" text-anchor="{anker}">{etik}</text>')
for lm in (400, 800):
    g.append(f'<line x1="{x(lm)}" y1="14" x2="{x(lm)}" y2="{ya}" class="haar"/>')
H = ya + 19
SVG = f'<svg width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}" xmlns="http://www.w3.org/2000/svg">\n        ' + '\n        '.join(g) + '\n      </svg>'


# ---------------------------------------------------------------- dei fire romma
def figur(fil, namn, under, d=None, maal=None):
    if d is not None:
        tre = (f'<div><span>{heil(d["felt_lx"])}{NB}lx</span><small>feltet</small></div>'
               f'<div><span>{heil(d["vegg_lx"])}{NB}lx</span><small>veggen</small></div>'
               f'<div><span>{cd(auge(d))}{NB}cd/m²</span><small>mot auget</small></div>')
    else:
        tre = maal
    return (f'<figure><img src="bilete/{fil}" alt="">'
            f'<figcaption><b>{namn}</b><br>{under}</figcaption>'
            f'<div class="tre">{tre}</div></figure>')


fig = [
    figur('marknad-snowball.png', 'Northern Snowball oppladbar', f'portabel designlampe · 158{NB}lm · batteri', M['snowball']),
    figur('marknad-l1.png', 'Luxo L-1', f'arbeidslampe · 529{NB}lm · leidning', M['l1']),
    figur('marknad-litra.png', 'Logitech Litra Glow', f'møtelys · 250{NB}lm · USB', M['litra']),
    figur('rom-arbeid.png', 'Målet', 'lyset ingen av dei gjev',
          maal=(f'<div><span>350{NB}lx</span><small>feltet</small></div>'
                f'<div><span>100–150{NB}lx</span><small>veggen</small></div>'
                f'<div><span>under 1500</span><small>cd/m² mot auget</small></div>')),
]

HTML = f'''<!doctype html>
<html lang="nn">
<head>
<meta charset="utf-8">
<title>02 · Research i bransjen</title>
<link rel="stylesheet" href="felles.css">
<style>
  .fire {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); column-gap: 16px; }}
  .fire img {{ aspect-ratio: 248 / 220; object-fit: cover; object-position: center 62%; }}
  .fire figcaption {{ line-height: 1.45; }}
  .innhald {{ row-gap: 12px; }}
  .tre {{ display: flex; justify-content: space-between; align-items: flex-end; margin-top: 7px; border-top: 1px solid var(--linje); padding-top: 7px; }}
  .tre span {{ font: 400 20px/1 var(--serif); color: var(--blekk); white-space: nowrap; }}
  .tre small {{ display: block; font: 400 9px/1.2 var(--mono); letter-spacing: 0.08em; text-transform: uppercase; color: var(--graa); margin-top: 4px; }}
  svg .kv {{ fill: var(--blekk); }}
  svg .kvs {{ stroke: var(--blekk); fill: none; }}
  svg .opn {{ fill: #000; stroke: var(--blekk); stroke-width: 1; }}
  .nord {{ display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 12px; }}
  .nord div {{ font: 400 30px/1 var(--serif); color: var(--blekk); }}
  .nord small {{ display: block; font: 400 9px/1.2 var(--mono); letter-spacing: 0.08em; text-transform: uppercase; color: var(--graa); margin-top: 5px; }}
  .manglar {{ margin: 0; padding: 0; list-style: none; }}
  .manglar li {{ font-size: 13.5px; line-height: 1.33; padding: 5px 0 6px; border-top: 1px solid var(--linje); }}
</style>
</head>
<body>
<div class="side">
  <header class="topp">
    <span>GK5 · Northern · fase 1</span>
    <span>02 · Research i bransjen</span>
    <span>Iver R. Finne · 13.11.2026</span>
  </header>

  <h1 class="tittel">Feltet mellom stemningslampa og arbeidslampa står ope.</h1>

  <main class="innhald">
    <section class="k12 fire">
      {fig[0]}
      {fig[1]}
      {fig[2]}
      {fig[3]}
    </section>

    <figure class="k7">
      <p class="etikett">Lysfluks og drift for 14 lamper</p>
      {SVG}
      <figcaption style="text-transform: none; letter-spacing: 0.03em;">Sirkel: portabel. Firkant: arbeidslampe. Trekant: møtelys. Fylt: lys ut av lampa. Ope: produsenttal.</figcaption>
    </figure>

    <section class="k5">
      <p class="etikett">Northern</p>
      <div class="nord">
        <div>13<small>tilsette</small></div>
        <div>49,7<small>mill. kr i 2025</small></div>
        <div>56<small>lamper</small></div>
        <div>4{NB}490<small>kr, medianpris</small></div>
      </div>
      <p class="etikett">Det Northern ikkje har enno</p>
      <ul class="manglar">
        <li>Éi heimleg lampe med begge lysa: stemning på batteri, arbeidslys på leidning.</li>
        <li>Spreidd og retta lys i same flyttbare lampe, med éi handling mellom. Balancer skiftar slik, men på leidning.</li>
        <li>Mjukt ansiktslys frå stor flate, utan teknisk uttrykk.</li>
      </ul>
      <p class="liten graa" style="margin-top: 10px;">Systemkomponentar: lysmodul med Ra minst 90, optikk som held luminansen nede, drivar og mekanisk brytar, éi 21700-celle (17,8{NB}Wh) i foten, USB-C på 7,5{NB}W.</p>
    </section>
  </main>

  <footer class="botn">
    <span>Bileta er modell med lumental frå produsenten og forenkla form. Kjelder (12.11.2026): northern.no, Glamox, Logitech, Brønnøysundregistra, produktdatablad.</span>
    <span>Utvalet er 14 lamper.</span>
  </footer>
</div>
</body>
</html>
'''
open(os.path.join(V2, 'side-2-bransjeresearch.html'), 'w', encoding='utf-8', newline='\n').write(HTML)
print('skrive', 'svg-høgd', round(H))
for k, d in M.items():
    print(k, d, 'mot auget', cd(auge(d)))
