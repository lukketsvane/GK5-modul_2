# -*- coding: utf-8 -*-
"""Lysbiletserie til konseptgjennomgangen med Northern 18.11.2026, i husstilen (svart, biletet først).

Byggjer på sidene 01 til 13: bileta frå leveransar/01_fase1_v2/bilete og leveransar/03_konsept/bilete,
tala frå konsept/tre/tal-*.json og silhuettane frå leveransar/02_formfoering/lys/bygg_formfoering.py.
Ligg det foto av skissemodellane i leveransar/03_konsept/foto/, blir dei brukte i staden for rendringane
(køyr leveransar/03_konsept/lys/bygg_konsept.py først, så blir dei beskorne).

  python lag_presentasjon.py      skriv presentasjon.html, presentasjon.pdf og png/lysbilete-NN.png
"""
import os, sys, json, subprocess, tempfile, importlib.util

HER = os.path.dirname(os.path.abspath(__file__))
LEV = os.path.normpath(os.path.join(HER, '..'))
TRE = os.path.normpath(os.path.join(HER, '..', '..', 'konsept', 'tre'))
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
NB = '&nbsp;'
W, H = 1280, 720


def _last(namn, fil):
    spec = importlib.util.spec_from_file_location(namn, fil)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


FF = _last('bygg_formfoering', os.path.join(LEV, '02_formfoering', 'lys', 'bygg_formfoering.py'))
KO = _last('bygg_konsept', os.path.join(LEV, '03_konsept', 'lys', 'bygg_konsept.py'))
T = {k: json.load(open(os.path.join(TRE, f'tal-{k}.json'), encoding='utf-8')) for k in 'ABC'}


def f0(x): return f'{x:,.0f}'.replace(',', NB)
def f1(x): return f'{x:.1f}'.replace('.', ',')
def f2(x): return f'{x:.2f}'.replace('.', ',')


def bilete(k, t):
    """Fotoet av skissemodellen om det finst, elles rendringa."""
    if KO.foto(k, t):
        return f'../03_konsept/bilete/{k}-{t}-foto.jpg', True
    return f'../03_konsept/bilete/{k}-{t}.png', False


def lysbilete(nr, tittel, innhald, kjelde=''):
    return f'''<section class="lb">
  <header class="topp"><span>GK5 · Northern · konseptgjennomgang 18.11.2026</span><span>{nr:02d}</span><span>Iver R. Finne</span></header>
  <h1 class="tittel">{tittel}</h1>
  <main>{innhald}</main>
  <footer class="botn"><span>{kjelde}</span></footer>
</section>'''


MODELL = 'Bileta er modell, ikkje måling: lysmotoren i konsept/lysskisse, same rom, mannekeng og budsjett.'


def l_tittel():
    return f'''<section class="lb tittelbilete">
  <img class="heil" src="../01_fase1_v2/bilete/rom-stemning.png" alt="">
  <div class="tekst">
    <p class="etikett">GK5 · Northern · konseptgjennomgang 18.11.2026</p>
    <h1>Ei stemningslampe som òg kan arbeide</h1>
    <p class="under">Tre konsept for heimearbeidsplassen</p>
    <p class="etikett namn">Iver R. Finne · AHO</p>
  </div>
</section>'''


def l_oppgaava():
    tre = ''.join(f'<figure><img src="../01_fase1_v2/bilete/{f}" alt=""><figcaption><b>{n}</b> · {u}</figcaption></figure>'
                  for f, n, u in (('rom-arbeid.png', 'Arbeid', f'350{NB}lx på feltet'), ('rom-paa-veg.png', 'Skiftet', f'éi rørsle, under 10{NB}s'),
                                  ('rom-stemning.png', 'Stemning', f'50 til 200{NB}lm, varmt')))
    inn = f'''<div class="to-tredel"><p class="stor">Ei lampe som gjer ein plass i heimen til arbeidsplass og til heim att, som gjev arbeidslys utan blending, og som eigaren kan reparere.</p>
    <p class="graa">Hybridarbeidaren, heime ein til to dagar i veka, i eit rom som òg er stove eller kjøken. 45,1{NB}% har heimekontor, berre 5,7{NB}% minst halve tida.</p></div>
    <div class="tre-bilete">{tre}</div>'''
    return lysbilete(2, 'Oppgåva slik eg les ho', inn, MODELL + ' Tal: SSB 2025.')


def l_marknad():
    M = json.load(open(os.path.join(LEV, '01_fase1_v2', 'bilete', 'marknad.json'), encoding='utf-8'))
    def kol(f, n, u, d):
        auge = max(d['lampe_cd'], d['lysaste_flate_cd'])
        return (f'<figure><img src="../01_fase1_v2/bilete/{f}" alt=""><figcaption><b>{n}</b> · {u}</figcaption>'
                f'<div class="tre-tal"><div>{f0(d["felt_lx"])}{NB}lx<small>feltet</small></div><div>{f0(d["vegg_lx"])}{NB}lx<small>veggen</small></div>'
                f'<div>{f0(round(auge, -1) if auge >= 1000 else auge)}<small>cd/m² mot auget</small></div></div></figure>')
    inn = '<div class="fire-bilete">' + kol('marknad-snowball.png', 'Northern Snowball oppladbar', f'158{NB}lm', M['snowball']) + \
          kol('marknad-l1.png', 'Luxo L-1', f'529{NB}lm', M['l1']) + kol('marknad-litra.png', 'Logitech Litra Glow', f'250{NB}lm', M['litra']) + \
          (f'<figure><img src="../01_fase1_v2/bilete/rom-arbeid.png" alt=""><figcaption><b>Målet</b> · lyset ingen av dei gjev</figcaption>'
           f'<div class="tre-tal"><div>350{NB}lx<small>feltet</small></div><div>100–150{NB}lx<small>veggen</small></div><div>&lt; 1500<small>cd/m² mot auget</small></div></div></figure>') + '</div>'
    return lysbilete(3, 'Ingen av dei gjev både stemning og arbeidslys utan blending.', inn, 'Bileta er modell med lumental frå produsenten og forenkla form.')


def l_krav():
    inn = f'''<div class="to-kol"><figure class="stort"><img src="../01_fase1_v2/bilete/rom-krav.png" alt=""></figure>
    <section><p class="etikett">Prøvde før valet</p>
      <ul class="liste"><li><b>F1</b> låg blending: inga lyskjelde synleg frå 25 til 60{NB}cm</li><li><b>F2</b> éi handling mellom arbeid og stemning</li>
      <li><b>F3</b> 350{NB}lx jamt på feltet ved skjermen</li><li class="graa"><b>E2</b> speglar Northern</li><li class="graa"><b>M1</b> passar sortimentet</li>
      <li class="graa"><b>B1</b> eigaren byter slitedelane</li></ul>
      <p class="graa" style="margin-top:14px">Lyset (F1, F2, F3) er prøvd i modellen. Kroppen, sortimentet og reparasjonen (E2, M1, B1) står att, og dei vil eg avgjere saman med dykk.</p></section></div>'''
    return lysbilete(4, 'Lyset er prøvd i modellen. Kropp, sortiment og reparasjon står att.', inn, MODELL)


def l_northern():
    inn = f'''<figure class="silhuettar">{FF.silhuettrad()}</figure>
    <div class="fire-reglar"><div><b>R1</b> høgst tre primærformer</div><div><b>R2</b> det som ber, har konstant tverrsnitt</div>
    <div><b>R3</b> lyskjelda er aldri naken</div><div><b>R4</b> éin lakkfarge, kontrast berre i materialskifte</div></div>'''
    return lysbilete(5, 'Fire reglar ber attkjenninga. Silhuetten og handlinga er fri.', inn,
                     'Mål frå produktarka til Northern. Silhuettane er skjematiske. Regeltesten er gjord på 18 lamper i produktbilete.')


def l_tre():
    kol = ''.join(f'<figure><img src="{bilete(k, "arbeid")[0]}" alt=""><figcaption><b>{k} {K["namn"]}</b> · {K["gest"].lower().rstrip(".")}</figcaption>'
                  f'<p class="graa liten">{K["prinsipp"]}</p></figure>' for k, K in KO.KONSEPT.items())
    return lysbilete(6, 'Tre måtar å flytte lyset frå veggen til bordet.', f'<div class="tre-bilete hoge">{kol}</div>', MODELL)


def l_konsept(nr, k):
    K, r = KO.KONSEPT[k], T[k]
    auge = max(r['auge25'], r['auge47'], r['auge60'])
    bs, fs = bilete(k, 'stemning'); ba, fa = bilete(k, 'arbeid')
    ikkje = ''.join(f'<li>{x}</li>' for x in K['ikkje'][:3])
    inn = f'''<div class="konsept"><figure><img src="{bs}" alt=""><figcaption><b>Stemning</b>{' · foto' if fs else ''}</figcaption></figure>
    <figure><img src="{ba}" alt=""><figcaption><b>Arbeid</b>{' · foto' if fa else ''}</figcaption></figure>
    <section><p class="gest">{K["gest"]}</p>
      <div class="tal4"><div>{f2(r["W350"])}{NB}W<small>for 350{NB}lx på feltet</small></div><div>{f2(r["jamnheit"])}<small>jamnheit · ref. 0,6</small></div>
      <div>{f0(auge)}<small>cd/m² mot auget, høgst</small></div></div>
      <p class="etikett" style="margin-top:12px">Held ikkje enno</p><ul class="liste liten">{ikkje}</ul></section></div>'''
    return lysbilete(nr, KO.KONSEPT[k]['tittel'], inn, MODELL + ' Tala er skalerte til 350' + NB + 'lx på feltet.')


def l_samanlikning():
    rader = [('Watt for 350 lx på feltet', lambda r: r['W350'], f2, min), ('Timar arbeidslys per celle', lambda r: r['timar'], f1, max),
             ('Jamnheit på feltet', lambda r: r['jamnheit'], f2, max), ('Mot auget frå 25 cm, cd/m²', lambda r: r['auge25'], f0, min),
             ('Veggen bak skjermen i arbeid, lx', lambda r: r['bak350'], f0, max), ('Skjermflata midt i overgangen, lx', lambda r: r['veg_skjerm'][2], f0, min),
             ('Største sprang i overgangen', lambda r: r['sprang'], f2, min)]
    tr = ''
    for namn, fn, fmt, best in rader:
        v = {k: fn(T[k]) for k in 'ABC'}; bk = best(v, key=v.get)
        tr += f'<tr><td>{namn}</td>' + ''.join(f'<td class="tal{" best" if k == bk else ""}">{fmt(v[k])}</td>' for k in 'ABC') + '</tr>'
    inn = f'''<table class="sam"><tr><th></th><th class="tal">A Skiva</th><th class="tal">B Over</th><th class="tal">C Vindauge</th></tr>{tr}</table>
    <p class="stor" style="margin-top:22px">B brukar minst straum, A lyser jamnast, og berre C held lyset borte frå skjermen. Ingen held veggen bak skjermen lys i arbeid.</p>'''
    return lysbilete(10, 'Kvar dei står samanlikna', inn, MODELL + ' Kvit: best av dei tre.')


def l_val():
    inn = '''<div class="to-kol"><section><p class="etikett">Det eg vil spørje dykk om</p>
      <ol class="liste"><li>Kva skal lampa vere først: jamnt arbeidslys (A), minst straum og eit reint skifte (B), eller lys som aldri treffer skjermen (C)?</li>
      <li>Kva kropp passar i sortimentet: fot og stong (A), ei plate over skjermen (B), eller eit lyshovud (C)?</li>
      <li>Vil de selje batteri, elektronikk og lysmodul som reservedelar?</li>
      <li>Produksjon, årsvolum og målpris: kva ramme skal eg halde meg innanfor?</li></ol></section>
    <section><p class="etikett">Neste steg</p>
      <ul class="liste"><li>Mål lobebreidda på folien. Ho avgjer blendinga for A og B.</li><li>Byggj skissemodellen av det valde konseptet om, med kropp.</li>
      <li>Formføring og handskisser til formgjennomgangen 25.11.</li><li>Konstruksjon i Fusion og 1:1-modell til 7.12.</li></ul></section></div>'''
    return lysbilete(11, 'Kva de vel, avgjer kva eg byggjer vidare.', inn, 'Konseptgjennomgangen er der valet blir teke saman med Northern (prosjektbeskrivinga).')


STIL = open(os.path.join(LEV, '01_fase1_v2', 'felles.css'), encoding='utf-8').read().replace('../01_fase1_sider/fonts/', '../01_fase1_sider/fonts/') + '''
@page { size: 1280px 720px; margin: 0; }
.lb { width: 1280px; height: 720px; padding: 26px 52px 22px; box-sizing: border-box; background: #000; color: var(--tekst); font-family: var(--serif);
      position: relative; overflow: hidden; display: grid; grid-template-rows: auto auto minmax(0, 1fr) auto; break-after: page; }
.lb:last-child { break-after: auto; }
.lb .topp { font: 400 11px/1 var(--mono); }
.lb .tittel { font-size: 40px; margin: 18px 0 16px; }
.lb main { min-height: 0; }
.lb .botn { font-size: 10.5px; }
.stor { font-size: 26px; line-height: 1.22; color: var(--blekk); }
.graa { color: var(--graa); } .liten { font-size: 15px; line-height: 1.32; }
.tre-bilete { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); column-gap: 18px; margin-top: 14px; }
.tre-bilete img { aspect-ratio: 1.8 / 1; object-fit: cover; object-position: center 58%; width: 100%; }
.tre-bilete.hoge img { aspect-ratio: 1 / 1; }
.to-tredel { display: grid; grid-template-columns: 2fr 1fr; column-gap: 30px; }
.to-tredel .graa { font-size: 17px; line-height: 1.35; }
.fire-bilete { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); column-gap: 16px; }
.fire-bilete img { aspect-ratio: 1 / 0.95; object-fit: cover; object-position: center 60%; width: 100%; }
.tre-tal { display: flex; justify-content: space-between; margin-top: 8px; border-top: 1px solid var(--linje); padding-top: 8px; }
.tre-tal div { font: 400 22px/1 var(--serif); color: var(--blekk); white-space: nowrap; }
.tre-tal small, .tal4 small { display: block; font: 400 10px/1.3 var(--mono); letter-spacing: 0.06em; text-transform: uppercase; color: var(--graa); margin-top: 4px; }
.to-kol { display: grid; grid-template-columns: 1fr 1fr; column-gap: 40px; align-items: start; }
.to-kol .stort img { width: 100%; aspect-ratio: 1.25 / 1; object-fit: cover; object-position: center 55%; }
ul.liste, ol.liste { margin: 0; padding: 0 0 0 0; list-style: none; counter-reset: n; }
.liste li { font-size: 19px; line-height: 1.3; padding: 8px 0 9px; border-top: 1px solid var(--linje); color: var(--blekk); }
ol.liste li { counter-increment: n; } ol.liste li::before { content: counter(n) "  "; font: 400 12px/1 var(--mono); color: var(--graa); }
.liste.liten li { font-size: 15px; padding: 5px 0 6px; }
.liste li.graa { color: var(--graa); }
.liste b { font: 400 13px/1 var(--mono); color: var(--graa); margin-right: 6px; }
.silhuettar svg { width: 100%; height: auto; }
.fire-reglar { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); column-gap: 18px; margin-top: 14px; }
.fire-reglar div { font-size: 19px; line-height: 1.25; color: var(--blekk); border-top: 1px solid var(--linje); padding-top: 8px; }
.fire-reglar b { display: block; font: 400 12px/1 var(--mono); color: var(--graa); margin-bottom: 6px; }
.konsept { display: grid; grid-template-columns: 430px 430px minmax(0, 1fr); column-gap: 18px; }
.konsept img { width: 100%; aspect-ratio: 1 / 1; object-fit: cover; }
.gest { font: italic 400 30px/1.1 var(--serif); color: var(--blekk); margin: 0 0 12px; }
.tal4 div { font: 400 30px/1 var(--serif); color: var(--blekk); padding: 7px 0 8px; border-top: 1px solid var(--linje); }
table.sam { width: 100%; border-collapse: collapse; font-size: 19px; }
table.sam th { font: 400 11px/1.2 var(--mono); letter-spacing: 0.08em; text-transform: uppercase; color: var(--graa); text-align: left; padding-bottom: 8px; border-bottom: 1px solid #5C5C5C; }
table.sam td { padding: 8px 10px 8px 0; border-bottom: 1px solid var(--linje); }
table.sam .tal { text-align: right; width: 16%; font-family: var(--mono); font-size: 17px; color: var(--graa); }
table.sam td.best { color: var(--blekk); }
.tittelbilete { padding: 0; display: block; }
.tittelbilete .heil { position: absolute; right: 0; top: 0; height: 720px; width: 720px; object-fit: cover; }
.tittelbilete .tekst { position: absolute; left: 52px; top: 0; bottom: 0; width: 500px; display: flex; flex-direction: column; justify-content: center; }
.tittelbilete h1 { font: 400 54px/1.05 var(--serif); color: var(--blekk); margin: 14px 0 14px; }
.tittelbilete .under { font-size: 24px; color: var(--tekst); }
.tittelbilete .namn { margin-top: 40px; }
'''


def skriv_pdf(hf, pdf):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-first-run', f'--user-data-dir={tmp}', '--no-pdf-header-footer',
                        '--virtual-time-budget=5000', f'--print-to-pdf={pdf}', 'file:///' + hf.replace('\\', '/')], check=True, capture_output=True, timeout=180)


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    KO.last()                                       # bileta (og eventuelle foto) frå konseptarka
    lb = [l_tittel(), l_oppgaava(), l_marknad(), l_krav(), l_northern(), l_tre(),
          l_konsept(7, 'A'), l_konsept(8, 'B'), l_konsept(9, 'C'), l_samanlikning(), l_val()]
    css = STIL.replace('url("../01_fase1_sider/fonts/', 'url("../01_fase1_sider/fonts/')
    html = ('<!doctype html><html lang="nn"><head><meta charset="utf-8"><title>Konseptgjennomgang 18.11</title><style>' + css +
            '</style></head><body style="margin:0;background:#000">' + ''.join(lb) + '</body></html>')
    hf = os.path.join(HER, 'presentasjon.html'); open(hf, 'w', encoding='utf-8').write(html)
    pdf = os.path.join(HER, 'presentasjon.pdf'); skriv_pdf(hf, pdf)
    import fitz
    d = fitz.open(pdf); os.makedirs(os.path.join(HER, 'png'), exist_ok=True)
    for n in range(len(d)):
        d[n].get_pixmap(dpi=96).save(os.path.join(HER, 'png', f'lysbilete-{n + 1:02d}.png'))
    print('skrive presentasjon.pdf,', len(d), 'lysbilete')
