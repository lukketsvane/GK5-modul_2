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
    rader = [('Watt for 350 lx på feltet', lambda r: r['W350'], f2, min), ('Timar arbeidslys per celle (15,1 Wh)', lambda r: r['timar'], f1, max),
             ('Jamnheit på feltet', lambda r: r['jamnheit'], f2, max), ('Mot auget frå 25 cm, cd/m²', lambda r: r['auge25'], f0, min),
             ('Veggen bak skjermen i arbeid, lx', lambda r: r['bak350'], f0, max), ('Skjermflata midt i overgangen, lx', lambda r: r['veg_skjerm'][2] * 350 / r['veg_felt'][-1], f0, min),
             ('Største sprang i overgangen', lambda r: r['sprang'], f2, min), ('Skjermflata i stemning, lx', lambda r: r['s_skjerm'], f0, min)]
    tr = ''
    for namn, fn, fmt, best in rader:
        v = {k: fn(T[k]) for k in 'ABC'}; bv = fmt(best(v.values()))      # like verdiar etter avrunding er like gode
        tr += f'<tr><td>{namn}</td>' + ''.join(f'<td class="tal{" best" if fmt(v[k]) == bv else ""}">{fmt(v[k])}</td>' for k in 'ABC') + '</tr>'
    inn = f'''<table class="sam"><tr><th></th><th class="tal">A Skiva</th><th class="tal">B Over</th><th class="tal">C Vindauge</th></tr>{tr}</table>
    <p class="stor" style="margin-top:20px">A brukar minst straum, men legg lys på skjermen. C legg minst lys på skjermen, men brukar mest straum. B ligg mellom og lyser ujamnast.</p>'''
    return lysbilete(10, 'Alle tre held veggen. Valet står mellom straum og lys på skjermen.', inn, MODELL + ' Kvit: best av dei tre.')


def kropp():
    """Masse, fotavtrykk og krafta som veltar lampa, med 0,5 kg ballast, frå konsept/tre/kropp.md (rekna av kropp.py)."""
    ut = {}
    for l in open(os.path.join(TRE, 'kropp.md'), encoding='utf-8'):
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        if len(c) >= 8 and c[0] and c[0] in 'ABC' and c[1] == '0.5':
            ut[c[0]] = dict(masse=float(c[2]), velt_N=float(c[5]), fot_cm2=float(c[6]))
    assert set(ut) == set('ABC'), 'kropp.md manglar rader med 0,5 kg ballast'
    return ut


def stykkliste():
    """Produksjonskost (lågt, høgt, €) og hovuddelar (T6) per konsept, og kostnadsmålet, frå konsept/tre/stykkliste.md."""
    import re
    s = open(os.path.join(TRE, 'stykkliste.md'), encoding='utf-8').read()
    ut = {}
    for k, namn in (('A', 'A Skiva'), ('B', 'B Over'), ('C', 'C Vindauge')):
        bolk = s.split(f'## {namn}', 1)[1].split('\n## ', 1)[0]
        lo, hi = re.search(r'\|\s*\*\*Sum\*\*.*?\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*', bolk).groups()
        delar = re.search(r'Hovuddelar \(T6\):[^\n]*?\*\*(\d+)', bolk).group(1)
        ut[k] = dict(lo=int(lo), hi=int(hi), delar=int(delar))
    maal = re.search(r'\*\*(\d+) til (\d+) €\*\*', s).groups()
    return ut, (int(maal[0]), int(maal[1]))


def f10():
    """Møtelyset (F10) frå konsept/tre/f10.json: A med kjelde 18° og C med alt lyset på veggen."""
    F = json.load(open(os.path.join(TRE, 'f10.json'), encoding='utf-8'))
    a18 = [r for r in F if r['namn'].startswith('A matt bakside mot auget') and r['namn'].endswith('18°')]
    bkv = [r for r in F if r['namn'].startswith('B kvit bakside på heile plata')]
    c = [r for r in F if r['namn'].startswith('C ')]
    assert len(a18) == 1 and len(bkv) == 1 and len(c) == 1, 'f10.json manglar A med kjelde 18°, B med kvit bakside eller C'
    return a18[0], bkv[0], c[0]


def l_valet():
    """Kva valet står på, etter valtabellen i konsept/tre/val-18-11.md."""
    Kr = kropp()
    a18, bkv, cveg = f10()
    SL, _ = stykkliste()
    def kol(k, rolle, faar, pris):
        K, kr, sl = KO.KONSEPT[k], Kr[k], SL[k]
        velt = f'veltar ved {f1(kr["velt_N"])}{NB}N' if kr['velt_N'] > 0 else 'veltar av seg sjølv på fot'
        return (f'<figure><img src="{bilete(k, "arbeid")[0]}" alt=""><figcaption><b>{k} {K["namn"]}</b> · {rolle}</figcaption>'
                '<p class="etikett">Får de</p><ul class="liste liten">' + ''.join(f'<li>{x}</li>' for x in faar) + '</ul>'
                '<p class="etikett">Prisen</p><ul class="liste liten pris">' + ''.join(f'<li>{x}</li>' for x in pris) + '</ul>'
                f'<p class="kroppstal">{f2(kr["masse"])}{NB}kg · {f0(kr["fot_cm2"])}{NB}cm² · {velt}<br>'
                f'{sl["lo"]} til {sl["hi"]}{NB}€ i produksjon · {sl["delar"]} hovuddelar</p></figure>')
    A, B, C = T['A'], T['B'], T['C']
    inn = ('<div class="tre-val">' +
           kol('A', 'nærast Northern, enklast å byggje',
               [f'{f2(A["W350"])}{NB}W for 350{NB}lx, {f1(A["timar"])} timar per celle', f'jamt lys på feltet ({f2(A["jamnheit"])})',
                f'møtelys: vend skiva, 50{NB}lx på ansiktet ved {f1(a18["W_for_50"])}{NB}W', 'fot, stong og skive, nær Snowball og Ombre'],
               [f'skjermflata får {f2(A["skjerm350"] / 350)} av lyset på feltet', 'minst nytt: Verner Panton Reflect er nær nabo',
                'skiva må ha lobe under 4,5°']) +
           kol('B', 'den einaste over skjermen',
               ['bordet blir fritt med ei klemme bak skjermen', f'stemninga held seg av skjermen ({f0(B["s_skjerm"])}{NB}lx)', 'ein ny type for Northern'],
               [f'ujamt lys ({f2(B["jamnheit"])})', 'speglar seg i skjermen når han er tilta 20° (F1)',
                f'møtelyset går over F5: {f0(bkv["L_ved_50"])}{NB}cd/m² ved 50{NB}lx', 'treng klemme, og mekanikken kan verke teknisk']) +
           kol('C', 'det nyaste, lyser reinast',
               [f'høgst {f0(max(C["veg_skjerm"]) * 350 / C["veg_felt"][-1])}{NB}lx på skjermen gjennom skiftet', f'{f0(C["auge25"])}{NB}cd/m² mot auget, lågast av dei tre',
                'vindauget står i ro på veggen'],
               [f'{f1(C["W350"])}{NB}W og {f1(C["timar"])} timar per celle', f'møtelys berre via veggen: om lag {f0(cveg["lx_per_W"] * 7.5)}{NB}lx ved 7,5{NB}W',
                'hovudet 70' + NB + 'cm over bordet', 'optikk som må stå nøyaktig']) +
           '</div><p class="graa liten" style="margin-top:12px">Felles: eit dytt på 5' + NB +
           'N veltar alle tre. Vippen og skyvet må vere eit kraftpar, med ein knott i leddet eller ein spak ved foten.</p>')
    return lysbilete(11, 'A er det trygge kortet, C det nye, B lampa over skjermen.', inn,
                     'Kjelde: konsept/tre/val-18-11.md, tal-*.json, kropp.md (0,5 kg ballast), f10.md (møtelys) og stykkliste.md (overslag, ikkje tilbod). Modell, ikkje måling.')


def l_val():
    SL, (mlo, mhi) = stykkliste()
    lo, hi = min(r['lo'] for r in SL.values()), max(r['hi'] for r in SL.values())
    inn = f'''<div class="to-kol"><section><p class="etikett">Det eg vil spørje dykk om</p>
      <ol class="liste"><li>Kva vil de ha: det trygge kortet nær sortimentet (A), ei lampe over skjermen som lèt bordet vere fritt (B), eller ein ny type som held lyset av skjermen (C)?</li>
      <li>Kan ei lampe over skjermen (B) eller eit lyshovud på ei høg stong (C) stå i sortimentet ved sida av Snowball og Ombre?</li>
      <li>Vil de selje batteri, elektronikk og lysmodul som reservedelar?</li>
      <li>Pris og volum: overslaget gjev {lo} til {hi}{NB}€ i produksjon, og 2990 til 3990{NB}kr i butikk gjev rom for {mlo} til {mhi}{NB}€. Stemmer målprisen, og kva årsvolum reknar de med?</li></ol></section>
    <section><p class="etikett">Neste steg</p>
      <ul class="liste"><li>Mål lobebreidda på folien. Ho avgjer blendinga for A.</li>
      <li>Gjer handlinga til eit kraftpar, med knott eller spak, så lampa ikkje veltar.</li><li>Byggj skissemodellen av det valde konseptet om, med kropp.</li>
      <li>Formføring og handskisser til formgjennomgangen 25.11.</li><li>Konstruksjon i Fusion og 1:1-modell til 7.12.</li></ul></section></div>'''
    return lysbilete(12, 'Kva de vel, avgjer kva eg byggjer vidare.', inn, 'Konseptgjennomgangen er der valet blir teke saman med Northern (prosjektbeskrivinga).')


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
.tre-val { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); column-gap: 26px; }
.tre-val img { width: 100%; aspect-ratio: 2.5 / 1; object-fit: cover; object-position: center 62%; }
.tre-val .etikett { margin: 10px 0 2px; }
.tre-val .liste.liten li { font-size: 14.5px; padding: 4px 0 5px; }
.tre-val .liste.pris li { color: var(--graa); }
.kroppstal { font: 400 11px/1.3 var(--mono); letter-spacing: 0.04em; color: var(--graa); margin: 8px 0 0; border-top: 1px solid var(--linje); padding-top: 7px; }
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
          l_konsept(7, 'A'), l_konsept(8, 'B'), l_konsept(9, 'C'), l_samanlikning(), l_valet(), l_val()]
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
