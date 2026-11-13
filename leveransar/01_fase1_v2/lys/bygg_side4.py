# -*- coding: utf-8 -*-
"""Byggjer side-4-kravspesifikasjon.html: krava teikna inn i rommet, og matrisa ved sida.
Punkta i biletet kjem frå kameraet i lysmotoren (rom.proj)."""
import os, math
from rom import proj, b, FELT, AUGE, YV

HER = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.normpath(os.path.join(HER, '..'))
N = 500            # biletet på sida, px
X0, Y0 = 30, 46    # plassen til biletet i figuren
FW, FH = 560, 600  # heile figuren: band til merkelappar over og under biletet
NB = '&nbsp;'


def P(pt):
    x, y = proj(pt)
    return round(X0 + x * N, 1), round(Y0 + y * N, 1)


def poly(pts, kl):
    return f'<polygon points="{" ".join(f"{x},{y}" for x, y in pts)}" class="{kl}"/>'


def merke(x, y, liner):
    ut = []
    for i, t in enumerate(liner):
        kl = 'm1' if i == 0 else 'm2'
        ut.append(f'<text x="{x}" y="{y + i * 12.6:.1f}" class="{kl}">{t}</text>')
    return '\n      '.join(ut)


def leiar(x1, y1, x2, y2):
    """Tynn kvit strek med mørk kant under, så han syner både mot lys vegg og mørk kropp."""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="kant"/>'
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="leiar"/>'
            f'<circle cx="{x1}" cy="{y1}" r="2.6" class="kantprikk"/><circle cx="{x1}" cy="{y1}" r="1.8" class="prikk"/>')


felt = [P(b(-0.3, 0.05, 0)), P(b(0.3, 0.05, 0)), P(b(0.3, 0.45, 0)), P(b(-0.3, 0.45, 0))]
ff = P(b(0.0, 0.05, 0))                    # midt på framkanten av feltet
vh = P(b(0.55, YV, 0.55))
sk = P(b(0.0, 0.45, 0.40))
au = P(AUGE)
lpp = P(b(0.47, 0.40, 0.0))
fot = [P(b(0.47 + 0.08 * math.cos(a), 0.40 + 0.08 * math.sin(a), 0)) for a in [i * math.pi / 18 for i in range(36)]]

g = []
g.append(poly(felt, 'omrkant')); g.append(poly(felt, 'omr'))
g.append(poly(fot, 'omrkant')); g.append(poly(fot, 'omr'))
# over biletet
g.append(leiar(sk[0], sk[1], 196, 42))
g.append(merke(118, 12, ['F1◆ SKJERMEN', 'inga lyskjelde spegla i skjermen']))
g.append(leiar(vh[0], vh[1], 424, 42))
g.append(merke(360, 12, ['F6 VEGGEN VED SKJERMEN', f'100 til 150{NB}lx']))
# i den mørke kroppen
g.append(leiar(au[0], au[1], 112, 452))
g.append(merke(44, 468, ['F1◆ AUGET', 'inga lyskjelde synleg og', f'ingen flate over 3000{NB}cd/m²,', f'25 til 60{NB}cm over bordet', f'F5 under 1500{NB}cd/m²', f'F10 ansiktet 50 til 200{NB}lx']))
# under biletet
g.append(leiar(ff[0], ff[1], 232, 552))
g.append(merke(170, 568, ['F3◆ ARBEIDSFELTET', f'350{NB}lx frå lampa åleine,', f'500 med romlys, 0,6 × 0,4{NB}m']))
g.append(leiar(lpp[0], lpp[1], 424, 552))
g.append(merke(360, 568, ['HER STÅR LAMPA', f'F9 høgst 200{NB}cm² · F8 høgst 1,2{NB}kg', f'F2◆ éi handling, under 10{NB}s']))
SVG = '\n      '.join(g)

MATRISE = [
    ('Estetiske og semantiske',
     ['E1 heimleg, ikkje teknisk', 'E2◆ speglar Northern', 'E3 forklarar bruken'],
     ['E4 ny tolking'],
     ['E5 leiken handling']),
    ('Ergonomiske og funksjonelle',
     ['F1◆ låg blending', 'F2◆ saumlaus overgang', 'F3◆ jamt arbeidslys ved skjermen', 'F4 varmt lys', 'F8 flyttbar med éi hand'],
     ['F5 låg luminans', 'F6 dempa kontrast rundt skjermen', 'F7 trinnlaus demping', 'F9 liten bordplass', 'F10 mjukt ansiktslys', 'F11 varmare ved demping'],
     []),
    ('Tekniske',
     ['T1 flimrar ikkje', 'T2 veltar ikkje', f'T3 arbeidslys 8{NB}t på leidning', 'T4 naturlege fargar', 'T8 trygg å handtere'],
     ['T6 utan dyre verktøy', 'T7 stemningslys utan leidning'],
     ['T5 arbeidslys utan leidning']),
    ('Marknadsøkonomiske',
     ['M1◆ passar sortimentet', 'M2 reservedelar'],
     ['M3 prisnivået til Northern'],
     []),
    ('Berekraftsmessige',
     ['B1◆ eigaren byter slitedelar', 'B2 reine materialfraksjonar', 'B3 lyser utan batteri'],
     ['B4 materialmerkte delar', 'B5 lite straum avslått', 'B6 dokumentert klimaavtrykk', 'B7 ny lysmodul seinare'],
     []),
]


def krav(liste):
    ut = []
    for k in liste:
        kid, _, tekst = k.partition(' ')
        kl = ' class="p"' if '◆' in kid else ''
        ut.append(f'<div{kl}><span class="kid">{kid}</span> {tekst}</div>')
    return ''.join(ut)


rader = []
for namn, skal, bor, kan in MATRISE:
    rader.append(f'<tr class="kat"><td colspan="3">{namn}</td></tr>')
    rader.append(f'<tr><td>{krav(skal)}</td><td>{krav(bor)}</td><td>{krav(kan)}</td></tr>')
TABELL = '\n        '.join(rader)

n_skal = sum(len(m[1]) for m in MATRISE); n_bor = sum(len(m[2]) for m in MATRISE); n_kan = sum(len(m[3]) for m in MATRISE)
n_p = sum(1 for m in MATRISE for l in m[1:] for k in l if '◆' in k)

HTML = f'''<!doctype html>
<html lang="nn">
<head>
<meta charset="utf-8">
<title>04 · Kravspesifikasjon</title>
<link rel="stylesheet" href="felles.css">
<style>
  .to {{ display: grid; grid-template-columns: {FW}px minmax(0, 1fr); column-gap: 30px; }}
  .rom {{ position: relative; width: {FW}px; height: {FH}px; }}
  .rom img {{ position: absolute; left: {X0}px; top: {Y0}px; width: {N}px; height: {N}px; display: block; }}
  .rom svg {{ position: absolute; left: 0; top: 0; }}
  .rom svg .omr {{ fill: none; stroke: #FFFFFF; stroke-width: 1; stroke-dasharray: 3 3; }}
  .rom svg .omrkant {{ fill: none; stroke: #000000; stroke-opacity: 0.45; stroke-width: 2.6; }}
  .rom svg .leiar {{ stroke: #FFFFFF; stroke-width: 0.9; }}
  .rom svg .kant {{ stroke: #000000; stroke-opacity: 0.5; stroke-width: 2.6; }}
  .rom svg .prikk {{ fill: #FFFFFF; }}
  .rom svg .kantprikk {{ fill: #000000; fill-opacity: 0.5; }}
  .rom svg text {{ letter-spacing: 0.04em; }}
  .rom svg .m1 {{ fill: #FFFFFF; font-size: 10px; }}
  .rom svg .m2 {{ fill: #BDBDBD; font-size: 9.5px; }}
  table.matrise {{ font-size: 12.5px; line-height: 1.3; table-layout: fixed; }}
  table.matrise th {{ padding-bottom: 5px; }}
  table.matrise td {{ padding: 2px 10px 7px 0; border-bottom: 1px solid var(--linje); }}
  table.matrise tr.kat td {{ font: 400 9.5px/1.2 var(--mono); letter-spacing: 0.08em; text-transform: uppercase; color: var(--graa); padding: 7px 0 2px; border-bottom: 0; }}
  table.matrise .kid {{ font: 400 10px/1 var(--mono); color: var(--graa); }}
  table.matrise .p, table.matrise .p .kid {{ color: var(--blekk); }}
  .sum {{ display: flex; gap: 28px; align-items: flex-end; margin: 0 0 12px; }}
  .sum div {{ font: 400 34px/1 var(--serif); color: var(--blekk); }}
  .sum div.graatal {{ color: var(--graa); }}
  .sum small {{ display: block; font: 400 9px/1.2 var(--mono); letter-spacing: 0.08em; text-transform: uppercase; color: var(--graa); margin-top: 5px; }}
</style>
</head>
<body>
<div class="side">
  <header class="topp">
    <span>GK5 · Northern · fase 1</span>
    <span>04 · Kravspesifikasjon</span>
    <span>Iver R. Finne · 13.11.2026</span>
  </header>

  <h1 class="tittel">Seks av krava blir prøvde på modell før konseptvalet.</h1>

  <main class="innhald" style="display: block;">
    <div class="to">
      <figure class="rom">
        <img src="bilete/rom-krav.png" alt="">
        <svg width="{FW}" height="{FH}" viewBox="0 0 {FW} {FH}" xmlns="http://www.w3.org/2000/svg">
      {SVG}
        </svg>
      </figure>

      <section>
        <div class="sum">
          <div>{n_p}<small>◆ prøvde før valet 18.11</small></div>
          <div class="graatal">{n_skal}<small>skal</small></div>
          <div class="graatal">{n_bor}<small>bør</small></div>
          <div class="graatal">{n_kan}<small>kan</small></div>
        </div>
        <table class="matrise">
        <colgroup><col style="width: 41%"><col style="width: 41%"><col style="width: 18%"></colgroup>
        <tr><th>Skal</th><th>Bør</th><th>Kan</th></tr>
        {TABELL}
        </table>
        <p class="liten graa" style="margin-top: 8px;">Krava er eigenskapar, ikkje løysingar. Måla står i biletet der dei gjeld.</p>
      </section>
    </div>
  </main>

  <footer class="botn">
    <span>Biletet er modell: lyset krava ber om, før lampa finst. Kjelder: designbriefen, prosjektbeskrivinga og eigne researchnotat.</span>
    <span>Måla er framlegg.</span>
  </footer>
</div>
</body>
</html>
'''
open(os.path.join(V2, 'side-4-kravspesifikasjon.html'), 'w', encoding='utf-8', newline='\n').write(HTML)
print('skrive. skal', n_skal, 'bor', n_bor, 'kan', n_kan, 'provde', n_p)
print('feltkant', ff, 'vegg', vh, 'skjerm', sk, 'auge', au, 'lampe', lpp)
