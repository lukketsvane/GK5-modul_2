# -*- coding: utf-8 -*-
"""Byggjer konseptdelen av Moodle-innleveringa 17.11: eitt oversyn og éi side per konsept.

Bileta blir klipte ut av konseptarka i konsept/tre/ (stemning til venstre, arbeid til høgre),
og tala blir lesne frå tal-A.json, tal-B.json og tal-C.json same stad. Kjem det nye ark eller tal,
køyrer ein skriptet på nytt.

  python bygg_konsept.py
"""
import os, sys, json
from PIL import Image

HER = os.path.dirname(os.path.abspath(__file__))
UT = os.path.normpath(os.path.join(HER, '..'))
TRE = os.path.normpath(os.path.join(HER, '..', '..', '..', 'konsept', 'tre'))
NB = '&nbsp;'

KONSEPT = {
    'A': dict(namn='Skiva', fil='ark-A-skiva.png', nr='11',
              tittel='Skiva lyser jamnast av dei tre, men sveipar over skjermen på veg ned.',
              prinsipp='Ei kjelde i foten lyser opp på ei bøygd spegelskive. Skiva vippar lyset frå veggen bak skjermen ned på arbeidsfeltet.',
              northern='Fot, stong og skive: tre primærformer, som Northern.',
              nabo='Verner Panton Reflect, som har fast, kvit skive.',
              gest='Vipp skiva.',
              modell='Folie på papp, Ø 250' + NB + 'mm, på ein printa ribbe med boge R 1,2' + NB + 'm. Telefonlykta i ein svart papprull i foten. Stolpen frå projektoren held skiva 41' + NB + 'cm over bordet.',
              fore='Med bøyen er lågaste rute over 0,5 av snittet, flat under 0,45.',
              ikkje=['Midt i overgangen sveipar strålen over skjermen: 350' + NB + 'lx på skjermflata.',
                     'I stemning ligg 142' + NB + 'lx på skjermflata.',
                     'Veggen bak skjermen får 14' + NB + 'lx i arbeid. F6 krev 100 til 150.',
                     'F1 kviler på lobebreidda. Folie på papp kan gje 1600 til 9000' + NB + 'cd/m² frå 25' + NB + 'cm.']),
    'B': dict(namn='Over', fil='ark-B-over.png', nr='12',
              tittel='Plata brukar minst straum og flyttar lyset heilt, men skiftet hoppar.',
              prinsipp='Fresnelplata frå overheadprojektoren ligg over skjermkanten. Ho vippar lyset frå veggen bak skjermen ned på bordet.',
              northern='Kroppen er byggjesettet, ikkje forma enno.',
              nabo='BenQ ScreenBar Halo.',
              gest='Vipp plata.',
              modell='Fresnelplata i ei pappramme med teiphengsel langs bakkanten. Stolpen klemt bak skjermen. Telefonlykta på skjermkanten i ein brønn av svart papp, 12' + NB + 'cm under plata, og eitt eller to diffusorark på plata.',
              fore='Jamnheit 0,46 (0,35 til 0,55) med diffusorark, under 0,05 utan.',
              ikkje=['Overgangen hoppar: største sprang 0,36.',
                     'Veggen bak skjermen får 16' + NB + 'lx i arbeid. F6 krev 100 til 150.',
                     'Dioden har lite margin. Brønnen må vere 50°: med 64° ser auget dioden frå 60' + NB + 'cm, 140' + NB + '000' + NB + 'cd/m².',
                     'Kroppen er stolpen frå byggjesettet, ikkje ei Northern-form.']),
    'C': dict(namn='Vindauge', fil='ark-C-vindauge.png', nr='13',
              tittel='Spegelen deler strålen: vindauget står, feltet kjem, og skjermen blir ikkje treft.',
              prinsipp='Ei linse teiknar eit vindauge av lys på veggen. Ein spegel glir inn i strålen og legg feltet på bordet, medan vindauget blir ståande.',
              northern='Kroppen er ikkje forma enno.',
              nabo='ingen kjend lampe deler strålen slik.',
              gest='Skyv spegelen inn.',
              modell='Ei lupe eller ei vassfylt glaskule på Ø 70' + NB + 'mm som linse. Maska i papp, ei trakt av folie, og frontflatespegelen frå projektoren på eit papphengsel rett etter linsa.',
              fore='Vindauget står i ro medan feltet kjem fram. Skjermen får under 0,15 av feltet heile vegen.',
              ikkje=['Maska slepp gjennom 0,47 av lyset, så arbeidslyset krev 3,8' + NB + 'W.',
                     'Jamnheita er 0,24. Referansen er 0,6.',
                     'Linsa på om lag 60' + NB + 'mm finst ikkje i byggjesettet.',
                     'Vindauget har skarp kant, som verdiordet mjuk utelukkar (mi tolking).']),
}


def f0(x): return f'{x:,.0f}'.replace(',', NB)
def f1(x): return f'{x:.1f}'.replace('.', ',')
def f2(x): return f'{x:.2f}'.replace('.', ',')


def last():
    T = {}
    for k in KONSEPT:
        T[k] = json.load(open(os.path.join(TRE, f'tal-{k}.json'), encoding='utf-8'))
        im = Image.open(os.path.join(TRE, KONSEPT[k]['fil'])).convert('RGB')
        for i, t in enumerate(('stemning', 'arbeid')):
            x0 = 70 + i * 1190
            im.crop((x0, 70, x0 + 1120, 1190)).resize((900, 900), Image.LANCZOS).save(os.path.join(UT, 'bilete', f'{k}-{t}.png'))
    return T


def side(fil, nr, namn, tittel, stil, innhald, kjelder, merknad):
    html = ('<!doctype html>\n<html lang="nn">\n<head>\n<meta charset="utf-8">\n<title>' + nr + ' · ' + namn + '</title>\n'
            '<link rel="stylesheet" href="../01_fase1_v2/felles.css">\n<style>\n' + stil + '\n</style>\n</head>\n<body>\n<div class="side">\n'
            '  <header class="topp">\n    <span>GK5 · Northern · fase 2</span>\n    <span>' + nr + ' · ' + namn + '</span>\n'
            '    <span>Iver R. Finne · 17.11.2026</span>\n  </header>\n\n'
            '  <h1 class="tittel">' + tittel + '</h1>\n\n  <main class="innhald">\n' + innhald + '\n  </main>\n\n'
            '  <footer class="botn">\n    <span>' + kjelder + '</span>\n    <span>' + merknad + '</span>\n  </footer>\n</div>\n</body>\n</html>\n')
    open(os.path.join(UT, fil), 'w', encoding='utf-8', newline='\n').write(html)
    print('skrive', fil)


KJELDE = 'Modell, ikkje måling: lysmotoren i konsept/lysskisse, same rom, mannekeng og budsjett (1,25' + NB + 'W i stemning, 5' + NB + 'W i arbeid).'


def overgangsfigur(r, ymaks=1100):
    """Feltet og skjermflata langs overgangen, fem steg frå stemning til arbeid."""
    W, H = 270, 128
    x0, x1, y0, y1 = 6, W - 64, 104, 10
    X = lambda i: round(x0 + i / 4 * (x1 - x0), 1)
    Y = lambda v: round(y0 - min(v, ymaks) / ymaks * (y0 - y1), 1)
    g = [f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" class="strek"/>']
    for v in (350, 1000):
        g.append(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" class="haar"/>')
        g.append(f'<text x="{x0}" y="{Y(v) - 3}" class="graa">{v}{NB}lx</text>')
    for key, kl, dash, namn in (('veg_felt', '#F4F4F4', '', 'feltet'), ('veg_skjerm', '#9A9A9A', ' stroke-dasharray="4 3"', 'skjermflata')):
        v = r[key]
        pts = ' '.join(f'{X(i)},{Y(x)}' for i, x in enumerate(v))
        g.append(f'<polyline points="{pts}" fill="none" stroke="{kl}" stroke-width="1.6"{dash}/>')
        for i, x in enumerate(v):
            g.append(f'<circle cx="{X(i)}" cy="{Y(x)}" r="2.2" fill="{kl}"/>')
        g.append(f'<text x="{X(4) + 7}" y="{Y(v[-1]) + 3}" fill="{kl}">{namn}</text>')
    g.append(f'<text x="{x0}" y="{y0 + 15}" class="graa">stemning</text>')
    g.append(f'<text x="{x1}" y="{y0 + 15}" class="graa" text-anchor="end">arbeid</text>')
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">' + ''.join(g) + '</svg>'


STIL_K = '''  .rad1 { display: grid; grid-template-columns: 362px 362px minmax(0, 1fr); column-gap: 14px; }
  .rad1 figcaption { margin-top: 6px; }
  .tal4 div { font: 400 30px/1 var(--serif); color: var(--blekk); padding: 6px 0 7px; border-top: 1px solid var(--linje); white-space: nowrap; }
  .tal4 div:first-child { border-top: 0; padding-top: 0; }
  .tal4 small { display: block; font: 400 9.5px/1.3 var(--mono); letter-spacing: 0.05em; text-transform: uppercase; color: var(--graa); margin-top: 4px; white-space: normal; }
  .gest { font: italic 400 24px/1.1 var(--serif); color: var(--blekk); margin: 0 0 10px; }
  .rad2 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); column-gap: 16px; margin-top: 12px; }
  .rad2 p:not(.etikett) { font-size: 13px; line-height: 1.33; }
  .rad2 .kvit { color: var(--blekk); }
  ul.ikkje { list-style: none; margin: 0; padding: 0; }
  ul.ikkje li { font-size: 13px; line-height: 1.3; color: var(--blekk); padding: 4px 0 5px; border-top: 1px solid var(--linje); }
  svg text { font-family: var(--mono); font-size: 9.5px; }
  svg .kv { fill: var(--blekk); }'''


def konseptside(k, r):
    K = KONSEPT[k]
    auge = max(r['auge25'], r['auge47'], r['auge60'])
    innhald = f'''    <div class="k12">
      <div class="rad1">
        <figure><img src="bilete/{k}-stemning.png" alt=""><figcaption><b>Stemning</b> · {f2(r['s_W'])}{NB}W · 2200{NB}K · veggen bak skjermen {f0(r['s_bak'])}{NB}lx</figcaption></figure>
        <figure><img src="bilete/{k}-arbeid.png" alt=""><figcaption><b>Arbeid</b> · 3000{NB}K · feltet {f0(r['veg_felt'][-1])}{NB}lx ved 5{NB}W</figcaption></figure>
        <section>
          <p class="etikett">Gesten</p>
          <p class="gest">{K['gest']}</p>
          <div class="tal4">
            <div>{f2(r['W350'])}{NB}W<small>for 350{NB}lx på feltet · tak 7,5</small></div>
            <div>{f2(r['jamnheit'])}<small>jamnheit · referanse 0,6</small></div>
            <div>{f0(auge)}{NB}cd/m²<small>høgst mot auget, 25 til 60{NB}cm · F1 3000</small></div>
            <div>{f1(r['timar'])}{NB}t<small>arbeidslys per 21700-celle</small></div>
          </div>
          <p class="etikett" style="margin-top: 10px;">Langs overgangen, lx</p>
          {overgangsfigur(r)}
        </section>
      </div>
      <div class="rad2">
        <section><p class="etikett">Prinsipp</p><p class="kvit">{K['prinsipp']}</p><p class="graa">{K['northern']} Næraste nabo: {K['nabo']}</p></section>
        <section><p class="etikett">Skissemodell til 18.11</p><p>{K['modell']}</p><p class="graa">Føreseiing: {K['fore']}</p></section>
        <section><p class="etikett">Held ikkje enno</p><ul class="ikkje">{''.join(f'<li>{x}</li>' for x in K['ikkje'])}</ul></section>
      </div>
    </div>'''
    side(f'side-{K["nr"]}-konsept-{k.lower()}-{K["namn"].lower()}.html', K['nr'], f'Konsept {k} · {K["namn"]}', K['tittel'], STIL_K, innhald,
         KJELDE, 'Tala er skalerte til 350' + NB + 'lx på feltet.')


def oversyn(T):
    rader = [
        ('Watt for 350 lx på feltet', 'tak 7,5 W', lambda r: r['W350'], f2, 'lag', lambda v: v <= 7.5),
        ('Timar arbeidslys per celle', '', lambda r: r['timar'], f1, 'hog', None),
        ('Jamnheit på feltet', 'referanse 0,6', lambda r: r['jamnheit'], f2, 'hog', None),
        ('Mot auget frå 25 cm, cd/m²', 'F1 under 3000', lambda r: r['auge25'], f0, 'lag', lambda v: v <= 3000),
        ('Veggen bak skjermen i arbeid, lx', 'F6 100 til 150', lambda r: r['bak350'], f0, 'hog', lambda v: v >= 100),
        ('Skjermflata midt i overgangen, lx', 'lys på skjermen', lambda r: r['veg_skjerm'][2], f0, 'lag', None),
        ('Største sprang i overgangen', '0 er glatt', lambda r: r['sprang'], f2, 'lag', None),
        ('Stemning: mot auget, cd/m²', 'F5 under 500', lambda r: r['s_auge25'], f0, 'lag', lambda v: v <= 500),
        ('Stemning: veggen bak skjermen, lx', '', lambda r: r['s_bak'], f0, 'hog', None),
    ]
    tr = []
    for namn, krav, fn, fmt, best, ok in rader:
        v = {k: fn(T[k]) for k in KONSEPT}
        bk = (min if best == 'lag' else max)(v, key=v.get)
        celler = []
        for k in KONSEPT:
            kl = 'best' if k == bk else ''
            feil = '' if ok is None or ok(v[k]) else '<span class="feil"> ikkje halde</span>'
            celler.append(f'<td class="tal {kl}">{fmt(v[k])}{feil}</td>')
        tr.append(f'<tr><td>{namn}<small>{krav}</small></td>{"".join(celler)}</tr>')
    tr.append('<tr><td>Ikkje prøvd enno<small>krava merkte ◆</small></td>' + ''.join('<td class="tal graa">E2, M1, B1</td>' for _ in KONSEPT) + '</tr>')
    kolonnar = ''.join(f'''      <figure><img src="bilete/{k}-arbeid.png" alt=""><figcaption><b>{k} {K['namn']}</b> · {K['gest'].lower().rstrip('.')}</figcaption></figure>
''' for k, K in KONSEPT.items())
    innhald = f'''    <div class="k12 tre">
{kolonnar}    </div>
    <section class="k12">
      <table class="samanlikning">
        <tr><th>Arbeidslys skalert til 350 lx på feltet</th>{''.join(f'<th class="tal">{k} {K["namn"]}</th>' for k, K in KONSEPT.items())}</tr>
        {''.join(tr)}
      </table>
      <p class="liten kvit" style="margin-top: 8px;">Ingen av dei 18 kandidatane held alle krava når augehøgda og antakingane blir varierte. F1 for A og B heng på lobebreidda til folien, og ho blir målt først.</p>
    </section>'''
    stil = '''  .tre { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); column-gap: 16px; }
  .tre img { aspect-ratio: 1.7 / 1; object-fit: cover; object-position: center 55%; }
  table.samanlikning { font-size: 13px; }
  table.samanlikning td { padding: 3px 10px 3px 0; }
  table.samanlikning td small { color: var(--graa); font: 400 9.5px/1 var(--mono); margin-left: 8px; letter-spacing: 0.03em; }
  table.samanlikning td.tal { width: 19%; color: var(--graa); font-size: 12px; }
  table.samanlikning td.best { color: var(--blekk); }
  table.samanlikning .feil { font-size: 9.5px; color: var(--graa); }
  table.samanlikning th.tal { width: 19%; }'''
    side('side-10-tre-konsept.html', '10', 'Tre konsept', 'B brukar minst straum, A lyser jamnast, og berre C held lyset borte frå skjermen.', stil, innhald,
         KJELDE, 'Kvit: best av dei tre.')


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    T = last()
    oversyn(T)
    for k in KONSEPT:
        konseptside(k, T[k])
