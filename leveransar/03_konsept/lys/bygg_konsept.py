# -*- coding: utf-8 -*-
"""Byggjer konseptdelen av Moodle-innleveringa 17.11: eitt oversyn og éi side per konsept.

Bileta blir klipte ut av konseptarka i konsept/tre/ (stemning til venstre, arbeid til høgre). Ligg det foto av
skissemodellane i foto/ (A-stemning.jpg, A-arbeid.jpg osv.), blir dei brukte i staden,
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

# Runde 2 av konsepta (konsept/tre/00-tre-konsept.md, 13.11.2026). Tala i tekstane blir lesne frå tal-*.json,
# og påstandane i titlane blir kontrollerte mot dei, så ei ny utrekning ikkje kan stå att med gamal tekst.
TAL = {k: json.load(open(os.path.join(TRE, f'tal-{k}.json'), encoding='utf-8')) for k in 'ABC'}
def _k(x, d=2): return f'{x:.{d}f}'.replace('.', ',')
def _n(x): return f'{x:,.0f}'.replace(',', NB)
_A, _B, _C = TAL['A'], TAL['B'], TAL['C']
_min = lambda f: min('ABC', key=lambda k: f(TAL[k]))
_max = lambda f: max('ABC', key=lambda k: f(TAL[k]))
assert all(100 <= TAL[k]['bak350'] <= 150 for k in 'ABC'), 'ikkje alle held veggen bak skjermen (F6)'
assert _min(lambda r: r['W350']) == 'A' and _max(lambda r: r['W350']) == 'C', 'A brukar ikkje minst / C ikkje mest straum'
assert _max(lambda r: r['skjerm350']) == 'A', 'A legg ikkje mest lys på skjermen'
assert _min(lambda r: r['skjerm350']) == 'C' and _min(lambda r: max(r['veg_skjerm'])) == 'C', 'C legg ikkje minst lys på skjermen'
assert _min(lambda r: r['jamnheit']) == 'B' and _B['s_skjerm'] < 10, 'B: jamnheit eller stemning på skjermen har endra seg'

KONSEPT = {
    'A': dict(namn='Skiva', fil='ark-A-skiva.png', nr='11',
              tittel='Skiva brukar minst straum, men legg lys på skjermen.',
              prinsipp='Ei lykt i foten lyser på ei bøygd spegelskive som vippar lyset frå veggen ned på feltet. Ein fast flik ved stolpen held veggen bak skjermen lys. I møte blir skiva vend, så den kvite baksida lyser på ansiktet.',
              northern='Fot, stong og skive som Northern. Fliken er eit fjerde element (mi tolking).',
              nabo='Verner Panton Reflect, som har fast, kvit skive og ingen flik.',
              gest='Vipp skiva.',
              modell='Folie på papp, Ø 250' + NB + 'mm, på ein printa ribbe med boge R 1,2' + NB + 'm. To lykter i foten: éi på skiva, éi på fliken (12 × 8,4' + NB + 'cm, folie og bakepapir), 30' + NB + 'cm over bordet og 3,5' + NB + 'cm til venstre for stolpen. Kvitt, matt papir på baksida av skiva (møte).',
              fore='Med bøyen er lågaste rute over 0,5 av snittet, flat under 0,45.',
              ikkje=[f'Spegelskiva legg {_k(_A["skjerm350"] / 350)} av feltluxen på skjermen i arbeid og {_n(_A["veg_skjerm"][2] * 350 / _A["veg_felt"][-1])}' + NB + 'lx midt i overgangen.',
                     'F1 krev ei skive med lobe under 4,5°. Folie på papp er ikkje målt.',
                     f'Frå 25' + NB + f'cm ser auget {_n(_A["s_auge25"])}' + NB + 'cd/m² i stemning. F5 tillèt 500.']),
    'B': dict(namn='Over', fil='ark-B-over.png', nr='12',
              tittel='Plata held stemninga heilt av skjermen, men lyser ujamnt.',
              prinsipp='Fresnelplata frå overheadprojektoren ligg over skjermkanten og er knekt. Den store delen vippar lyset frå veggen ned på bordet, fliken held veggen bak skjermen lys.',
              northern='Kroppen er stolpen frå byggjesettet, ikkje forma enno.',
              nabo='BenQ ScreenBar Halo.',
              gest='Vipp plata.',
              modell='Fresnelplata i pappramme som vippar om midten, med ein flik av blank folie 60' + NB + 'mm bak midtlina. Lykta i ein brønn av svart papp, 12' + NB + 'cm under plata. To diffusorark.',
              fore='Jamnheit om lag 0,4. Veggen bak skjermen om lag ein tredel av feltet.',
              ikkje=[f'Jamnheita stoppar under 0,5: {_k(_B["jamnheit"])} med ark. Referansen 0,6 er ikkje nådd under 1500' + NB + 'cd/m².',
                     f'Strålen sveipar over skjermen midt i vippen: {_n(_B["veg_skjerm"][2] * 350 / _B["veg_felt"][-1])}' + NB + 'lx.',
                     'Er skjermen tilta 20° bakover, speglar plata seg i han, og det bryt F1. Plata treng avskjerming på skjermsida, eller skjermtilten ei grense.']),
    'C': dict(namn='Vindauge', fil='ark-C-vindauge.png', nr='13',
              tittel='Spegelen deler strålen: skjermen får lite lys heile vegen, men det kostar straum.',
              prinsipp='Ei vasskule teiknar eit vindauge av lys på veggen. Ein spegel glir inn i strålen og legg feltet på bordet, medan vindauget blir ståande.',
              northern='Kroppen er ikkje forma enno. Spegelklaffen er synleg mekanikk.',
              nabo='ingen kjend lampe deler strålen slik.',
              gest='Skyv spegelen inn.',
              modell='Julekule av glas, Ø 70' + NB + 'mm, fylt med vatn. Maske i papp og gråfilter på overheadfilm, kredittkort-fresnel som kondensor, frontflatespegelen på ei pappflik. Hovudet 70' + NB + 'cm over bordet.',
              fore='Vindauget står i ro medan feltet kjem fram. Skjermen får under 0,15 av feltet heile vegen.',
              ikkje=[f'Arbeidslyset krev {_k(_C["W350"], 1)}' + NB + f'W og gjev {_k(_C["timar"], 1)} timar per celle.',
                     'Hovudet står 70' + NB + 'cm over bordet, høgare enn ei bordlampe.',
                     'Gråfilteret som gjev jamnheita, kostar 1,6' + NB + 'W.']),
}
assert _B['auge25'] == max(TAL[k]['auge25'] for k in 'ABC') and _B['auge25'] < 1500


def f0(x): return f'{x:,.0f}'.replace(',', NB)
def f1(x): return f'{x:.1f}'.replace('.', ',')
def f2(x): return f'{x:.2f}'.replace('.', ',')


FOTO = os.path.join(UT, 'foto')
BILETE = {}          # (konsept, tilstand) -> (fil relativt til sida, er foto)


def foto(k, t):
    """Fotoet av skissemodellen om det finst (foto/A-stemning.jpg osv.), beskore kvadratisk. Elles None."""
    for ending in ('jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG'):
        f = os.path.join(FOTO, f'{k}-{t}.{ending}')
        if os.path.exists(f):
            im = Image.open(f).convert('RGB'); w, h = im.size; s = min(w, h)
            im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((900, 900), Image.LANCZOS)
            ut = f'bilete/{k}-{t}-foto.jpg'; im.save(os.path.join(UT, ut), quality=90)
            return ut
    return None


def last():
    T = {}
    for k in KONSEPT:
        T[k] = json.load(open(os.path.join(TRE, f'tal-{k}.json'), encoding='utf-8'))
        im = Image.open(os.path.join(TRE, KONSEPT[k]['fil'])).convert('RGB')
        for i, t in enumerate(('stemning', 'arbeid')):
            x0 = 70 + i * 1190
            im.crop((x0, 70, x0 + 1120, 1190)).resize((900, 900), Image.LANCZOS).save(os.path.join(UT, 'bilete', f'{k}-{t}.png'))
            f = foto(k, t)
            BILETE[(k, t)] = (f, True) if f else (f'bilete/{k}-{t}.png', False)
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


def overgangsfigur(r, ymaks=400):
    """Feltet og skjermflata langs overgangen, fem steg frå stemning til arbeid."""
    W, H = 270, 128
    x0, x1, y0, y1 = 6, W - 64, 104, 10
    X = lambda i: round(x0 + i / 4 * (x1 - x0), 1)
    Y = lambda v: round(y0 - min(v, ymaks) / ymaks * (y0 - y1), 1)
    g = [f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" class="strek"/>']
    for v in (100, 350):
        g.append(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" class="haar"/>')
        g.append(f'<text x="{x0}" y="{Y(v) - 3}" class="graa">{v}{NB}lx</text>')
    for key, kl, dash, namn in (('veg_felt', '#F4F4F4', '', 'feltet'), ('veg_skjerm', '#9A9A9A', ' stroke-dasharray="4 3"', 'skjermflata')):
        v = [x * 350 / r['veg_felt'][-1] for x in r[key]]      # skalert til 350 lx på feltet, som tala
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
        <figure><img src="{BILETE[(k, 'stemning')][0]}" alt=""><figcaption><b>Stemning</b> · {'foto av skissemodellen' if BILETE[(k, 'stemning')][1] else f"{f2(r['s_W'])}{NB}W · 2200{NB}K · veggen bak skjermen {f0(r['s_bak'])}{NB}lx"}</figcaption></figure>
        <figure><img src="{BILETE[(k, 'arbeid')][0]}" alt=""><figcaption><b>Arbeid</b> · {'foto av skissemodellen' if BILETE[(k, 'arbeid')][1] else f"3000{NB}K · feltet {f0(r['veg_felt'][-1])}{NB}lx ved 5{NB}W"}</figcaption></figure>
        <section>
          <p class="etikett">Gesten</p>
          <p class="gest">{K['gest']}</p>
          <div class="tal4">
            <div>{f2(r['W350'])}{NB}W<small>for 350{NB}lx på feltet · tak 7,5</small></div>
            <div>{f2(r['jamnheit'])}<small>jamnheit · referanse 0,6</small></div>
            <div>{f0(auge)}{NB}cd/m²<small>høgst mot auget, 25 til 60{NB}cm · F1 3000</small></div>
            <div>{f1(r['timar'])}{NB}t<small>arbeidslys per 21700-celle, 15,1 Wh brukbart</small></div>
          </div>
          <p class="etikett" style="margin-top: 10px;">Langs overgangen, skalert, lx</p>
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
        ('Timar arbeidslys per celle', '15,1 Wh brukbart', lambda r: r['timar'], f1, 'hog', None),
        ('Jamnheit på feltet', 'referanse 0,6', lambda r: r['jamnheit'], f2, 'hog', None),
        ('Mot auget frå 25 cm, cd/m²', 'F1 under 3000', lambda r: r['auge25'], f0, 'lag', lambda v: v <= 3000),
        ('Veggen bak skjermen i arbeid, lx', 'F6 100 til 150', lambda r: r['bak350'], f0, 'hog', lambda v: v >= 100),
        ('Skjermflata midt i overgangen, lx', 'lys på skjermen', lambda r: r['veg_skjerm'][2] * 350 / r['veg_felt'][-1], f0, 'lag', None),
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
            kl = 'best' if fmt(v[k]) == fmt(v[bk]) else ''
            feil = '' if ok is None or ok(v[k]) else '<span class="feil"> ikkje halde</span>'
            celler.append(f'<td class="tal {kl}">{fmt(v[k])}{feil}</td>')
        tr.append(f'<tr><td>{namn}<small>{krav}</small></td>{"".join(celler)}</tr>')
    tr.append('<tr><td>Ikkje prøvd enno<small>krava merkte ◆</small></td>' + ''.join('<td class="tal graa">E2, M1, B1</td>' for _ in KONSEPT) + '</tr>')
    kolonnar = ''.join(f'''      <figure><img src="{BILETE[(k, 'arbeid')][0]}" alt=""><figcaption><b>{k} {K['namn']}</b> · {K['gest'].lower().rstrip('.')}</figcaption></figure>
''' for k, K in KONSEPT.items())
    innhald = f'''    <div class="k12 tre">
{kolonnar}    </div>
    <section class="k12">
      <table class="samanlikning">
        <tr><th>Arbeidslys skalert til 350 lx på feltet</th>{''.join(f'<th class="tal">{k} {K["namn"]}</th>' for k, K in KONSEPT.items())}</tr>
        {''.join(tr)}
      </table>
      <p class="liten kvit" style="margin-top: 8px;">Runde 2: alle tre har fått ein eigen veg til veggen bak skjermen. F1 for A heng på lobebreidda til folien, og ho blir målt først.</p>
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
    side('side-10-tre-konsept.html', '10', 'Tre konsept', 'Alle tre held veggen bak skjermen. A brukar minst straum, C legg minst lys på skjermen.', stil, innhald,
         KJELDE, 'Kvit: best av dei tre.')


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    T = last()
    oversyn(T)
    for k in KONSEPT:
        konseptside(k, T[k])
