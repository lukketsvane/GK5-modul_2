# -*- coding: utf-8 -*-
"""
lag.py  ·  Ruta, revisjon B: lysbilete, PDF og nettstad frå same innhald

Objektet åleine på svart, eitt lys og éin biletstil gjennom alle sidene, og dei tekniske sidene som kvit strek.
Alle bileta er rendringar av CAD-modellen (konsept/film/cad/render_ekte.py). Ingen genererte bilete.

  python lag.py            alt
  python lag.py bilete     berre bileta på nytt

Skriv
  presentasjon.html        lysbileta. Piltastane blar, og sida fyller vindauget
  Ruta-presentasjon.pdf    same sider, 1127 x 797 px
  sider/side-NN.jpg        kvar side som bilete, 2254 x 1594
  ../../ruta/index.html    studioet: éin svart skjerm med modellen, tre modusar og éin glidar (malen er studio.html.mal)
  ../../ruta/forteljing.html   forteljinga: rendringane og streken nedover éi side

Tala kjem frå CAD-kontrollen (konsept/film/cad/ut-b/kontroll.json), streken frå teikning_b.py.
"""
import os, sys, json, math, re, shutil, subprocess
from PIL import Image, ImageChops

HER = os.path.dirname(os.path.abspath(__file__))
ROT = os.path.normpath(os.path.join(HER, '..', '..'))
CAD = os.path.join(ROT, 'konsept', 'film', 'cad')
EKTE = os.path.join(CAD, 'ut-b', 'ekte')
TEIK = os.path.join(CAD, 'ut-b', 'teikning')
TRED = os.path.join(CAD, 'ut-b', '3d')
BIL = os.path.join(HER, 'bilete')
NETT = os.path.join(ROT, 'ruta')
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
B, H = 1127, 797

K = json.load(open(os.path.join(CAD, 'ut-b', 'kontroll.json'), encoding='utf-8'))

def kom(x, n=1): return (('%%.%df' % n) % x).replace('.', ',')
def finst(n): return os.path.exists(os.path.join(BIL, n + '.jpg'))

FARGAR = [('graabeige', 'Grå-beige', (0.40, 0.350, 0.285)), ('morkegron', 'Mørkegrøn', (0.020, 0.050, 0.033)),
          ('svart', 'Svart', (0.011, 0.011, 0.012)), ('kirsebaer', 'Kirsebærraud', (0.20, 0.014, 0.020))]
RENDRA = 'Rendring av CAD-modellen'
STREK = 'Teikna frå CAD-modellen'

# ------------------------------------------------------------------ innhaldet, éin gong

INNHALD = [
    dict(id='helt', bilete='r-helt', h1='Ei rute som lyser.', tekst='Stemningsskapande lampe for heim og arbeid.', plass='left: 72px; top: 318px;'),
    dict(id='form', bilete='r-front', h1='Skive.<br>Røyr.<br>Blad.', tekst='Tre former møtest utan overgang. Røyret er stamme, aksel og kabelveg i eitt.',
         plass='left: 72px; top: 250px;', breidd=230, skyv=170),
    dict(id='vipp', bilete='r-vifte', h1='Vipp.', tekst='Éi handling, frå vassrett til 80°. Stoppen og friksjonen ligg skjult inni bjelken.',
         plass='left: 72px; top: 64px;', breidd=420, merke='Tre rendringar av CAD-modellen: 0°, 40° og 80°'),
    dict(id='messing', bilete='r-messing', h1='Eitt punkt i messing.', tekst='Der du tek. Trykk for av og på, hald for å dimme.', plass='left: 72px; bottom: 96px;'),
    dict(id='kant', bilete='r-kant', h1='Lyset kjem frå kanten.', tekst='Ei LED-stripe i bjelken lyser inn i ei klar plate. Eit prismeark frå ein gammal skjerm sender lyset ut.',
         plass='right: 72px; bottom: 96px; width: 470px; text-align: right;', breidd=470, merke=RENDRA + ' · rillene i arket er teikna grovare enn dei er'),
    dict(id='boge', bilete='r-boge', h1='Eitt røyr, éin boge.', tekst='Stål, 12&nbsp;mm. Éin boge på 120° med 45&nbsp;mm radius.', plass='left: 290px; bottom: 96px;'),
    dict(id='kveld', bilete='r-kveld', h1='Om kvelden.', tekst='190&nbsp;lx på bordet under ruta ved 2&nbsp;W. Eit stemningslys og sidelys, ikkje eit arbeidslys.',
         plass='left: 72px; top: 318px;', breidd=290, merke=RENDRA + ' · lystalet er eit overslag for revisjon A, same rute og høgd'),
    dict(id='opna', bilete='r-sprengt', h1='Tretten delar,<br>fire skruar.', tekst='Kjøpt: LED-stripa og dimmaren. Frå ein gammal skjerm: plata og arket. Ingen skruar syner ovanfrå.',
         plass='left: 72px; top: 290px;', breidd=250, merke=RENDRA + ', med delane trekte frå kvarandre'),
]
DELAR = [('01', 'Fot', 'trykt og lakkert'), ('02', 'Botnlok med pute', 'trykt'), ('03', 'Ballast', 'stålplate 5&nbsp;mm'),
         ('04', 'Røyr', 'stål Ø 12, éin boge'), ('05', 'Bjelke', 'trykt i to lengder'), ('06', 'Bjelkelok', 'trykt'),
         ('07', 'Lysleiar', 'plate 3&nbsp;mm frå skjermen'), ('08', 'Prismeark', 'frå skjermen'),
         ('09', 'Flatstong', 'aluminium 12 × 2'), ('10', 'LED-stripe', 'kjøpt'), ('11', 'Touch-dimmar', 'kjøpt'),
         ('12', 'Stoppskrue', 'M3 med tapp'), ('13', 'Bremseskrue', 'M4 med nylonspiss'), ('E', 'Fire skruar', 'M3 × 12')]
SPRENGT_FLYTT = {'08': (-22, -12, 'end'), '11': (-18, -12, 'end'), '05': (12, -20, 'start'), '10': (-22, -5, 'end'), '09': (-26, 8, 'end'),
                 '06': (-24, 12, 'end'), 'E': (-16, 16, 'end'), '07': (-24, 14, 'end'), '04': (16, -20, 'start'), '12': (18, -10, 'start'),
                 '13': (18, 8, 'start'), '01': (-30, -6, 'end'), '03': (-46, 6, 'end'), '02': (-32, 8, 'end')}

def kontrollert():
    T = K['tyngdepunkt']; e = math.hypot(T[0], T[1])
    return [('Masse', '%d g av høgst 1200' % K['masse_g']), ('Fotavtrykk', '%s cm² av høgst 200' % kom(K['fotavtrykk_cm2'], 0)),
            ('Tyngdepunktet frå midten av foten', '%s mm' % kom(e, 0)), ('Trykk på hjørnet av ruta som veltar lampa', '%s N' % kom(K['velt_venstre_N'])),
            ('Helling utan kollisjon', '0° til 80°')]

IKKJE_PROVD = ['Bøyen i røyret: 120° med 45&nbsp;mm radius krev røyrbøyar.', 'Friksjonen og stoppen er teikna, ikkje bygde.',
               'Touch-dimmaren er ikkje vald.', 'At arket er ein prismefilm, er ikkje prøvd.', 'Ingen slicer-kontroll og ingen fysisk modell.',
               'Lyset er eit overslag for revisjon A og er ikkje rekna på nytt.']

# ------------------------------------------------------------------ bileta

def bilete():
    """Rendringane til JPEG. Vifta er tre rendringar lagde oppå kvarandre (det lysaste vinn). Fargesida er fire rendringar i rutenett."""
    os.makedirs(BIL, exist_ok=True)
    for f in sorted(os.listdir(BIL)):                                   # dei genererte bileta frå førre utgåve skal ikkje liggje att
        if f.startswith(('f-', 'p0-', 'p1-', 'p2-', 'p3-', 'p4-', 'p5-', 'p6-')) or f in ('fargar.jpg',): os.remove(os.path.join(BIL, f))
    if os.path.isdir(EKTE):
        for f in sorted(os.listdir(EKTE)):
            if f.startswith('r-') and f.endswith('.png') and 'prove' not in f and 'vifte-' not in f:
                Image.open(os.path.join(EKTE, f)).convert('RGB').save(os.path.join(BIL, f[:-4] + '.jpg'), quality=95, subsampling=0)
        v = [os.path.join(EKTE, 'r-vifte-%02d.png' % a) for a in (0, 40, 80)]
        if all(os.path.exists(p) for p in v):
            ark = Image.new('RGB', (2 * B, 2 * H), (0, 0, 0)); tw = 2 * B // 3
            for i, p in enumerate(v):
                im = Image.open(p).convert('RGB'); w, h = im.size
                u = im.crop((int(0.245 * w), int(0.06 * h), int(0.805 * w), h))               # lampa og heile ruta, same utsnitt i alle tre
                u = u.resize((tw, int(u.height * tw / u.width)), Image.LANCZOS)
                ton = Image.new('L', u.size, 255); px = ton.load()                             # mjuk overgang til svart i sidene, så leidningen ikkje blir kutta
                for x in range(u.width):
                    f = min(1.0, x / (0.10 * u.width), (u.width - 1 - x) / (0.05 * u.width))
                    if f < 1.0:
                        for y in range(u.height): px[x, y] = int(255 * f)
                ark.paste(u, (i * tw, 2 * H - u.height - 150), ton)
            ark.save(os.path.join(BIL, 'r-vifte.jpg'), quality=95, subsampling=0)
    kjelder = ['r-messing'] + ['r-messing-' + k for k, _, _ in FARGAR[1:]]
    if all(finst(n) for n in kjelder):
        tw, th = B - 1, H - 1
        ark = Image.new('RGB', (2 * B, 2 * H), (0, 0, 0))
        for i, n in enumerate(kjelder):
            ark.paste(Image.open(os.path.join(BIL, n + '.jpg')).convert('RGB').resize((tw, th), Image.LANCZOS), ((i % 2) * (tw + 2), (i // 2) * (th + 2)))
        ark.save(os.path.join(BIL, 'r-fargar.jpg'), quality=95, subsampling=0)
    if not finst('svart'): Image.new('RGB', (16, 16), (0, 0, 0)).save(os.path.join(BIL, 'svart.jpg'), quality=95)
    print('bilete:', ' '.join(sorted(f[:-4] for f in os.listdir(BIL) if f.endswith('.jpg'))))

# ------------------------------------------------------------------ strek

def sprengt_svg(hogd):
    svg = open(os.path.join(TEIK, 'sprengt.svg'), encoding='utf-8').read()
    J = json.load(open(os.path.join(TEIK, 'sprengt.json')))
    lag = ''
    for i, p in J['anker'].items():
        dx, dy, anker = SPRENGT_FLYTT.get(i, (16, -16, 'start'))
        q = (p[0] + dx, p[1] + dy)
        lag += '<line class="l" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/><circle class="p" cx="%.1f" cy="%.1f" r="1.4"/>' % (p[0], p[1], q[0], q[1], p[0], p[1])
        lag += '<text class="nr" x="%.1f" y="%.1f" text-anchor="%s">%s</text>' % (q[0] + (5 if anker == 'start' else -5), q[1] + 4, anker, i)
    if hogd: maal = 'width="%.0f" height="%.0f"' % (J['breidd'] * hogd / J['hogd'], hogd)
    else: maal = 'style="width: 100%; height: auto;"'
    return re.sub(r'<svg class="strek" width="\d+" height="\d+"', '<svg class="strek" ' + maal, svg).replace('</svg>', lag + '</svg>')

def maal_svg(flytande=False):
    svg = open(os.path.join(TEIK, 'maal.svg'), encoding='utf-8').read()
    if flytande: svg = re.sub(r'<svg class="maal" width="\d+" height="\d+"', '<svg class="maal" style="width: 100%; height: auto;"', svg)
    return svg

STREKSTIL = """
  svg { display: block; overflow: visible; }
  svg .k { stroke: #F4F1EB; stroke-width: 1.0; fill: none; }
  svg .s { stroke: #F4F1EB; stroke-width: 0.6; fill: none; }
  svg .t { stroke: #8A8781; stroke-width: 0.45; fill: none; }
  svg .st { stroke: #6C6964; stroke-width: 0.55; stroke-dasharray: 5 4; fill: none; }
  svg .m, svg .h { stroke: #6C6964; stroke-width: 0.55; fill: none; }
  svg .g { stroke: #3A3835; stroke-width: 0.55; fill: none; }
  svg .p { fill: #8A8781; }
  svg .l { stroke: #6C6964; stroke-width: 0.55; fill: none; }
  svg text { font-family: "EBG", serif; font-feature-settings: "lnum"; }
  svg text.nr { fill: #F4F1EB; font-size: 15px; }
  svg text.mt { fill: #C9C5BE; font-size: 12.5px; }
  svg text.et { fill: #6C6964; font-size: 9.5px; letter-spacing: 0.2em; }
"""

# ------------------------------------------------------------------ lysbileta og PDF-en

STIL = """
  @font-face { font-family: "EBG"; src: url("../01_fase1_sider/fonts/EBGaramond12-Regular.otf") format("opentype"); font-style: normal; }
  @font-face { font-family: "EBG"; src: url("../01_fase1_sider/fonts/EBGaramond12-Italic.otf") format("opentype"); font-style: italic; }
  @page { size: 1127px 797px; margin: 0; }
  html, body { margin: 0; padding: 0; background: #000; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  * { box-sizing: border-box; font-weight: 400; }
  .side { width: 1127px; height: 797px; position: relative; overflow: hidden; background: #000; color: #EFECE6;
          font-family: "EBG", Georgia, serif; font-feature-settings: "kern", "liga", "lnum"; break-after: page; page-break-after: always; }
  .side img.bak { position: absolute; left: 0; top: 0; width: 1127px; height: 797px; object-fit: cover; display: block; }
  .ord { position: absolute; }
  .ton { position: absolute; top: 0; width: 140px; height: 797px; background: linear-gradient(to right, #000, rgba(0,0,0,0)); }
  h1 { font: 400 54px/1.04 "EBG", serif; letter-spacing: -0.014em; margin: 0; color: #F4F1EB; }
  h1.namn { font-size: 132px; line-height: 0.9; letter-spacing: -0.03em; }
  p.t { font: 400 17.5px/1.44 "EBG", serif; color: #A6A29B; margin: 18px 0 0; }
  .sm { font: 400 9.5px/1.3 "EBG", serif; letter-spacing: 0.2em; text-transform: uppercase; color: #6C6964; }
  .folio { position: absolute; left: 72px; right: 72px; bottom: 38px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: baseline; }
  .folio span:last-child { text-align: right; }
  table.delar { border-collapse: collapse; font: 400 13.5px/1.25 "EBG", serif; width: 100%; }
  table.delar td { padding: 5.5px 0; border-bottom: 1px solid #1D1C1A; vertical-align: baseline; }
  table.delar td.id { width: 30px; color: #6C6964; }
  table.delar td.k { color: #8A8781; text-align: right; }
  .liste { font: 400 15px/1.35 "EBG", serif; }
  .liste div { display: grid; grid-template-columns: 1fr auto; column-gap: 18px; padding: 7px 0; border-bottom: 1px solid #1D1C1A; }
  .liste div span:last-child { color: #8A8781; text-align: right; }
  .liste.ein div { grid-template-columns: 1fr; color: #C9C5BE; }
  @media screen {
    html { scroll-snap-type: y mandatory; }
    body { display: flex; flex-direction: column; align-items: center; }
    .side { zoom: var(--k, 1); scroll-snap-align: start; flex: none; }
  }
""" + STREKSTIL

BLA = """<script>
(function () {
  var s = [].slice.call(document.querySelectorAll('.side')), i = 0;
  function maal() { document.documentElement.style.setProperty('--k', Math.min(innerWidth / 1127, innerHeight / 797)); }
  function vis(n) { i = Math.max(0, Math.min(s.length - 1, n)); s[i].scrollIntoView(); }
  addEventListener('resize', maal); maal();
  addEventListener('keydown', function (e) {
    if (['ArrowRight', 'ArrowDown', 'PageDown', ' '].indexOf(e.key) >= 0) { vis(i + 1); e.preventDefault(); }
    if (['ArrowLeft', 'ArrowUp', 'PageUp'].indexOf(e.key) >= 0) { vis(i - 1); e.preventDefault(); }
    if (e.key === 'Home') vis(0); if (e.key === 'End') vis(s.length - 1);
  });
  addEventListener('scroll', function () { i = Math.round(scrollY / (797 * Math.min(innerWidth / 1127, innerHeight / 797))); }, { passive: true });
})();
</script>"""

SIDER = []

def folio(merke):
    return '<div class="folio sm"><span>Ruta</span><span>%s</span><span>{NR}</span></div>' % merke

def biletside(bilete, h1, tekst, plass, merke=RENDRA, breidd=300, skyv=0, **_):
    if not finst(bilete): return
    t = '<p class="t" style="max-width: %dpx;">%s</p>' % (breidd, tekst) if tekst else ''
    b = '<img class="bak" src="bilete/%s.jpg" alt=""%s>' % (bilete, ' style="left: %dpx;"' % skyv if skyv else '')
    if skyv > 0: b += '<div class="ton" style="left: %dpx;"></div>' % (skyv - 1)
    if skyv < 0: b += '<div class="ton" style="left: %dpx; transform: scaleX(-1);"></div>' % (B + skyv - 139)
    SIDER.append('<section class="side">%s<div class="ord" style="%s"><h1>%s</h1>%s</div>%s</section>' % (b, plass, h1, t, folio(merke)))

def lysbilete():
    del SIDER[:]
    if finst('r-framside'):
        SIDER.append('''<section class="side"><img class="bak" src="bilete/r-framside.jpg" alt="">
<div class="ord" style="left: 300px; top: 468px;"><h1 class="namn">Ruta</h1><p class="t" style="margin-top: 28px; font-size: 20px; color: #C9C5BE;">Ei lysande rute på éin stilk.</p></div>
<div class="ord sm" style="left: 304px; right: 72px; bottom: 38px; display: flex; justify-content: space-between;"><span>Iver R. Finne · GK5 modul 2 · AHO · 2026</span><span>%s</span></div></section>''' % RENDRA)
    for x in INNHALD:
        if x['id'] != 'opna': biletside(**x)
    if finst('r-fargar'):
        x0, y0, w, h = 300, 106, 827, 585
        namn = ''.join('<div class="ord sm" style="left: %dpx; top: %dpx; color: #A6A29B;">%s</div>' % (x0 + 20 + (i % 2) * (w // 2 + 1), y0 + 18 + (i // 2) * (h // 2 + 1), n) for i, (_, n, _) in enumerate(FARGAR))
        SIDER.append('<section class="side"><img src="bilete/r-fargar.jpg" alt="" style="position: absolute; left: %dpx; top: %dpx; width: %dpx; height: %dpx; display: block;">%s'
                     '<div class="ord" style="left: 72px; top: 250px;"><h1>Éin<br>matt<br>farge.</h1><p class="t" style="max-width: 190px;">Foten, røyret og bjelken får same pulverlakk. '
                     'Messingen er den einaste andre fargen.</p></div>%s</section>' % (x0, y0, w, h, namn, folio('Fire rendringar av CAD-modellen')))
    for x in INNHALD:
        if x['id'] == 'opna': biletside(**x)
    rader = ''.join('<tr><td class="id">%s</td><td>%s</td><td class="k">%s</td></tr>' % d for d in DELAR)
    SIDER.append('''<section class="side">
<div class="ord" style="left: 64px; top: 46px;">%s</div>
<div class="ord" style="left: 770px; top: 64px; width: 285px;"><h1 style="font-size: 44px;">Delane.</h1>
<table class="delar" style="margin-top: 30px;">%s</table>
<p class="t" style="font-size: 14.5px; margin-top: 16px;">Ruta ligg vassrett i teikninga, og delane er trekte frå kvarandre langs aksane.</p></div>
%s</section>''' % (sprengt_svg(690.0), rader, folio(STREK)))
    SIDER.append('''<section class="side">
<div class="ord" style="left: 72px; top: 64px;"><h1>Mål.</h1></div>
<div class="ord" style="right: 72px; top: 86px; text-align: right;"><p class="t" style="margin: 0;">Breidd 378, djupn 223 og høgd 278&nbsp;mm.</p></div>
<div class="ord" style="left: 52px; top: 190px;">%s</div>
%s</section>''' % (maal_svg(), folio(STREK + ' · mål i mm')))
    if finst('r-profil'):
        a = ''.join('<div><span>%s</span><span>%s</span></div>' % x for x in kontrollert())
        n = ''.join('<div>%s</div>' % x for x in IKKJE_PROVD)
        SIDER.append('''<section class="side"><img class="bak" src="bilete/r-profil.jpg" alt="" style="left: -215px;"><div class="ton" style="left: 773px; transform: scaleX(-1);"></div>
<div class="ord" style="left: 640px; top: 64px; width: 415px;"><h1 style="font-size: 44px;">Kontrollert, ikkje bygd.</h1>
<div class="sm" style="margin-top: 34px;">Kontrollert i CAD</div><div class="liste" style="margin-top: 8px;">%s</div>
<div class="sm" style="margin-top: 30px;">Ikkje prøvd</div><div class="liste ein" style="margin-top: 8px;">%s</div></div>
%s</section>''' % (a, n, folio(RENDRA)))
    n = len(SIDER)
    svart = '<section class="side"><img class="bak" src="bilete/svart.jpg" alt="">'           # CSS-bakgrunnen åleine let ei lys hårline stå att nedst i PDF-en
    kropp = '\n\n'.join(x.replace('{NR}', '%02d' % (i + 1)).replace('<section class="side">', svart, 1) for i, x in enumerate(SIDER))
    html = ('<!doctype html>\n<html lang="nn">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>Ruta</title>\n'
            '<style>%s</style>\n</head>\n<body>\n%s\n%s\n</body>\n</html>\n' % (STIL, kropp, BLA))
    assert '—' not in html and '–' not in html
    hf = os.path.join(HER, 'presentasjon.html'); open(hf, 'w', encoding='utf-8').write(html)
    for i, s in enumerate(SIDER):
        print('  side %2d: %3d ord' % (i + 1, len(re.sub(r'<[^>]+>', ' ', re.sub(r'<svg.*?</svg>', ' ', s, flags=re.S)).replace('&nbsp;', ' ').split())))
    return hf, n

def pdf(hf, n):
    import fitz, tempfile
    ut = os.path.join(HER, 'Ruta-presentasjon.pdf')
    prof = tempfile.mkdtemp(prefix='chrome-ruta-')
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--user-data-dir=' + prof, '--no-pdf-header-footer',
                    '--virtual-time-budget=8000', '--print-to-pdf=' + ut, 'file:///' + hf.replace('\\', '/')], check=True, capture_output=True, timeout=300)
    d = fitz.open(ut); mappe = os.path.join(HER, 'sider')
    if os.path.isdir(mappe): shutil.rmtree(mappe)
    os.makedirs(mappe)
    for i, s in enumerate(d):
        px = s.get_pixmap(matrix=fitz.Matrix(2254 / s.rect.width, 1594 / s.rect.height), alpha=False)
        Image.frombytes('RGB', (px.width, px.height), px.samples).save(os.path.join(mappe, 'side-%02d.jpg' % (i + 1)), quality=94, subsampling=0)
    print('pdf: %d sider (venta %d), %.1f MB' % (len(d), n, os.path.getsize(ut) / 1e6))

# ------------------------------------------------------------------ nettstaden

NETTSTIL = """
  @font-face { font-family: "EBG"; src: url("../leveransar/01_fase1_sider/fonts/EBGaramond12-Regular.otf") format("opentype"); font-display: swap; }
  :root { --inn: clamp(24px, 6.4vw, 96px); --kvit: #F4F1EB; --graa: #A6A29B; --dim: #6C6964; --line: #1D1C1A; }
  * { box-sizing: border-box; font-weight: 400; }
  html { background: #000; scroll-behavior: smooth; }
  body { margin: 0; background: #000; color: #EFECE6; font-family: "EBG", Georgia, serif; font-feature-settings: "kern", "liga", "lnum"; -webkit-font-smoothing: antialiased; }
  a { color: inherit; text-underline-offset: 0.2em; text-decoration-color: var(--dim); }
  h1, h2 { font-size: clamp(2.3rem, 4.8vw, 3.9rem); line-height: 1.04; letter-spacing: -0.014em; margin: 0; color: var(--kvit); text-wrap: balance; }
  h1 { font-size: clamp(4.5rem, 12vw, 9.5rem); line-height: 0.9; letter-spacing: -0.03em; }
  p { font-size: clamp(1.05rem, 1.4vw, 1.22rem); line-height: 1.45; color: var(--graa); margin: 1.1rem 0 0; max-width: 23rem; }
  .sm { font-size: 0.66rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--dim); line-height: 1.5; }
  section { position: relative; }
  .b { min-height: 100svh; display: flex; align-items: center; overflow: hidden; }
  .b > img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: var(--pos, 78% 50%); display: block; }
  .b > .ord { position: relative; z-index: 1; padding: 0 var(--inn); }
  .b.nede { align-items: flex-end; } .b.nede > .ord { padding-bottom: clamp(3rem, 12vh, 7rem); }
  .b.hogre { justify-content: flex-end; text-align: right; } .b.hogre p { margin-left: auto; }
  .b.oppe { align-items: flex-start; } .b.oppe > .ord { padding-top: clamp(4rem, 13vh, 7.5rem); }
  .b.midt { justify-content: center; } .b.midt > .ord { padding-left: 12vw; }
  .b.forst > .ord { padding-left: 27vw; }
  .b > .merke { position: absolute; z-index: 1; left: var(--inn); right: var(--inn); bottom: 1.6rem; display: flex; justify-content: space-between; gap: 1rem; }
  .topp { position: absolute; z-index: 2; left: var(--inn); right: var(--inn); top: 1.6rem; display: flex; justify-content: space-between; gap: 1rem; }
  .tre { min-height: 100svh; display: grid; grid-template-columns: minmax(18rem, 30rem) minmax(0, 1fr); align-items: center; }
  .tre > .ord { padding: 0 0 0 var(--inn); position: relative; z-index: 1; }
  model-viewer { width: 100%; height: 100svh; background: #000; --poster-color: #000; --progress-bar-color: #6C6964; }
  .styr { margin-top: 2.2rem; max-width: 20rem; }
  .styr label { display: flex; justify-content: space-between; }
  input[type=range] { -webkit-appearance: none; appearance: none; width: 100%; height: 24px; background: transparent; margin: 0.3rem 0 0; cursor: pointer; }
  input[type=range]::-webkit-slider-runnable-track { height: 1px; background: #5A5753; }
  input[type=range]::-moz-range-track { height: 1px; background: #5A5753; }
  input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; width: 15px; height: 15px; border-radius: 50%; background: #C9A45C; margin-top: -7px; border: 0; }
  input[type=range]::-moz-range-thumb { width: 15px; height: 15px; border-radius: 50%; background: #C9A45C; border: 0; }
  .val { display: flex; gap: 0.9rem; margin-top: 1.7rem; align-items: center; }
  .val button { width: 26px; height: 26px; border-radius: 50%; border: 1px solid #3A3835; padding: 0; cursor: pointer; outline-offset: 4px; }
  .val button[aria-pressed=true] { outline: 1px solid var(--kvit); }
  .val span { margin-left: 0.4rem; }
  .ar { display: inline-block; margin-top: 1.9rem; border: 1px solid #5A5753; border-radius: 2rem; padding: 0.55rem 1.2rem; font: inherit; font-size: 0.95rem; color: var(--kvit); background: transparent; cursor: pointer; text-decoration: none; }
  .flate { padding: clamp(4rem, 12vh, 8rem) var(--inn); }
  .to { display: grid; grid-template-columns: minmax(0, 1.7fr) minmax(16rem, 1fr); gap: clamp(2rem, 5vw, 5rem); align-items: start; }
  .fargar { display: grid; grid-template-columns: 1fr 1fr; gap: 2px; }
  .fargar figure { margin: 0; position: relative; } .fargar img { width: 100%; display: block; } .fargar figcaption { position: absolute; left: 1rem; top: 0.9rem; }
  table { border-collapse: collapse; width: 100%; font-size: 0.95rem; margin-top: 1.8rem; }
  td { padding: 0.42rem 0; border-bottom: 1px solid var(--line); vertical-align: baseline; }
  td.id { width: 2.2rem; color: var(--dim); } td.k { color: #8A8781; text-align: right; }
  .liste { margin-top: 0.6rem; font-size: 1rem; }
  .liste div { display: grid; grid-template-columns: 1fr auto; gap: 1.2rem; padding: 0.5rem 0; border-bottom: 1px solid var(--line); }
  .liste div span:last-child { color: #8A8781; text-align: right; } .liste.ein div { grid-template-columns: 1fr; color: #C9C5BE; }
  footer { padding: 4rem var(--inn) 3rem; display: flex; flex-wrap: wrap; gap: 1rem 2.5rem; justify-content: space-between; border-top: 1px solid var(--line); }
  @media (max-aspect-ratio: 1/1), (max-width: 760px) {
    .b { display: block; min-height: 0; }
    .b > img { position: relative; inset: auto; height: auto; aspect-ratio: 2256 / 1600; object-position: 50% 50%; }
    .b > .ord, .b.nede > .ord { padding: 1.6rem var(--inn) 3.4rem; text-align: left; } .b.hogre p { margin-left: 0; }
    .b > .merke { position: static; padding: 0 var(--inn) 2rem; }
    .b.forst { display: flex; min-height: 100svh; align-items: flex-end; } .b.forst > img { position: absolute; inset: 0; height: 100%; aspect-ratio: auto; object-position: 25% 50%; }
    .b.forst > .ord, .b.nede.forst > .ord { padding-left: 24vw; }
    .tre { grid-template-columns: 1fr; min-height: 0; } .tre > .ord { padding: 3rem var(--inn) 0; } model-viewer { height: 72svh; }
    .to { grid-template-columns: 1fr; }
  }
""" + STREKSTIL

NETTSKRIPT = """<script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.0.0/model-viewer.min.js"></script>
<script>
(function () {
  var mv = document.getElementById('mv'), vipp = document.getElementById('helling'), grad = document.getElementById('grad');
  var FARGAR = __FARGAR__;
  // Animasjonen i fila går 35° → 0° → 80° → 35°. Stykket frå 0° til 80° ligg mellom bilete 108 og 180 (24 per sekund), med mjuk start og stopp.
  function tid(v) { var s = Math.min(1, Math.max(0, v / 80)); var t = 0.5 - Math.sin(Math.asin(1 - 2 * s) / 3); return (107 + 72 * t) / 24; }
  function set() { grad.textContent = vipp.value + '°'; if (mv.loaded) { mv.pause(); mv.currentTime = tid(+vipp.value); } }
  function lin(c) { return c; }
  function farge(kode) {
    var f = FARGAR[kode]; if (!f || !mv.model) return;
    mv.model.materials.forEach(function (m) { if (m.name === 'Lakk' || m.name === 'Leidning') m.pbrMetallicRoughness.setBaseColorFactor([f[0], f[1], f[2], 1]); });
    mv.setAttribute('ios-src', '3d/ruta' + (kode === 'graabeige' ? '' : '-' + kode) + '.usdz');
    [].forEach.call(document.querySelectorAll('.val button'), function (b) { b.setAttribute('aria-pressed', b.dataset.farge === kode); });
    document.getElementById('fargenamn').textContent = f[3];
  }
  mv.addEventListener('load', function () { if (mv.availableAnimations && mv.availableAnimations.length) mv.animationName = mv.availableAnimations[0]; set(); });
  vipp.addEventListener('input', set);
  [].forEach.call(document.querySelectorAll('.val button'), function (b) { b.addEventListener('click', function () { farge(b.dataset.farge); }); });
})();
</script>"""

def srgb(c):
    return '#%02x%02x%02x' % tuple(int(round(255 * (12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055))) for v in c)

def nettstad():
    os.makedirs(os.path.join(NETT, '3d'), exist_ok=True)
    if os.path.isdir(TRED):
        for f in os.listdir(TRED):
            if f.endswith(('.glb', '.usdz')): shutil.copyfile(os.path.join(TRED, f), os.path.join(NETT, '3d', f))
    bil = '../leveransar/07_ruta/bilete/'
    def b(x, klasse='', pos=None):
        if not finst(x['bilete']): return ''
        h = re.sub(r'<br>', ' ', x['h1'])
        return ('<section class="b %s" id="%s"%s><img src="%s%s.jpg" alt="" loading="lazy"><div class="ord"><h2>%s</h2><p>%s</p></div>'
                '<div class="merke sm"><span>%s</span></div></section>' % (klasse, x['id'], ' style="--pos: %s;"' % pos if pos else '', bil, x['bilete'], h, x['tekst'], x.get('merke', RENDRA)))
    I = {x['id']: x for x in INNHALD}
    del_ = []
    if finst('r-framside'):
        del_.append('<section class="b nede forst" style="--pos: 30%% 50%%;"><div class="topp sm"><span>GK5 modul 2 · AHO · 2026</span><span>Iver R. Finne</span></div>'
                    '<img src="%sr-framside.jpg" alt="Enden av bjelken med messingpunktet, og ruta sett frå sida som éi line av lys"><div class="ord"><h1>Ruta</h1><p style="color: #C9C5BE;">Ei lysande rute på éin stilk.</p></div>'
                    '<div class="merke sm"><span>%s</span><span><a href="./">Studio: snu, vipp og opne lampa</a></span></div></section>' % (bil, RENDRA))
    del_.append(b(I['helt']))
    knappar = ''.join('<button type="button" data-farge="%s" aria-label="%s" aria-pressed="%s" style="background: %s;"></button>' % (k, n, 'true' if i == 0 else 'false', srgb(c)) for i, (k, n, c) in enumerate(FARGAR))
    del_.append('''<section class="tre" id="modell"><div class="ord"><h2>Vipp.</h2><p>Éi handling, frå vassrett til 80°. Dra i modellen for å snu henne, og i lina under for å vippe ruta.</p>
<div class="styr"><label class="sm" for="helling"><span>Helling</span><span id="grad">35°</span></label><input type="range" id="helling" min="0" max="80" step="1" value="35"></div>
<div class="val">%s<span class="sm" id="fargenamn">Grå-beige</span></div>
<p class="sm" style="margin-top: 2.2rem; max-width: 20rem;">På iPhone og iPad kan du setje lampa på bordet ditt: trykk på knappen i modellen.</p></div>
<model-viewer id="mv" src="3d/ruta.glb" ios-src="3d/ruta.usdz" alt="Ruta som 3D-modell" ar ar-modes="webxr scene-viewer quick-look" ar-scale="fixed" camera-controls touch-action="pan-y"
 interaction-prompt="none" camera-orbit="-32deg 80deg 1.55m" camera-target="-0.03m 0.14m 0.05m" field-of-view="22deg" min-camera-orbit="auto 20deg 0.7m" max-camera-orbit="auto 100deg 2.6m"
 exposure="0.85" shadow-intensity="0" environment-image="neutral" loading="lazy" reveal="auto">
<button slot="ar-button" class="ar" style="position: absolute; right: var(--inn); bottom: 2rem;">Sjå henne på bordet ditt</button></model-viewer></section>''' % knappar)
    del_.append(b(I['form'], 'nede', '50% 50%')); del_.append(b(I['vipp'], 'oppe', '50% 50%'))
    del_.append(b(I['messing'], 'nede', '40% 50%')); del_.append(b(I['kant'], 'nede hogre', '30% 50%')); del_.append(b(I['boge'], 'nede midt', '50% 50%'))
    del_.append(b(I['kveld']))
    opna = b(I['opna'])
    if all(finst(n) for n in ['r-messing'] + ['r-messing-' + k for k, _, _ in FARGAR[1:]]):
        fig = ''.join('<figure><img src="%sr-messing%s.jpg" alt="%s" loading="lazy"><figcaption class="sm">%s</figcaption></figure>' % (bil, '' if i == 0 else '-' + k, n, n) for i, (k, n, _) in enumerate(FARGAR))
        del_.append('<section class="flate" id="farge"><div class="to" style="grid-template-columns: minmax(14rem, 0.6fr) minmax(0, 2fr); align-items: center;"><div><h2>Éin matt farge.</h2>'
                    '<p>Foten, røyret og bjelken får same pulverlakk. Messingen er den einaste andre fargen.</p></div><div class="fargar">%s</div></div></section>' % fig)
    rader = ''.join('<tr><td class="id">%s</td><td>%s</td><td class="k">%s</td></tr>' % d for d in DELAR)
    del_.append(opna)
    del_.append('<section class="flate" id="delar"><div class="to"><div>%s</div><div><h2>Delane.</h2><table>%s</table>'
                '<p>Ruta ligg vassrett i teikninga, og delane er trekte frå kvarandre langs aksane.</p><p class="sm" style="margin-top: 1.4rem;">%s</p></div></div></section>' % (sprengt_svg(0), rader, STREK))
    del_.append('<section class="flate" id="maal"><h2>Mål.</h2><p>Breidd 378, djupn 223 og høgd 278&nbsp;mm.</p><div style="margin-top: 3rem; max-width: 64rem;">%s</div>'
                '<p class="sm" style="margin-top: 1.4rem;">%s · mål i mm</p></section>' % (maal_svg(True), STREK))
    a = ''.join('<div><span>%s</span><span>%s</span></div>' % x for x in kontrollert()); n = ''.join('<div>%s</div>' % x for x in IKKJE_PROVD)
    del_.append('<section class="flate" id="status"><div class="to" style="grid-template-columns: 1fr 1fr;"><div><h2>Kontrollert, ikkje bygd.</h2>'
                '<p>Lampa finst som CAD-modell. Alt på denne sida er rendra eller teikna frå han.</p></div>'
                '<div><div class="sm">Kontrollert i CAD</div><div class="liste">%s</div><div class="sm" style="margin-top: 2.2rem;">Ikkje prøvd</div><div class="liste ein">%s</div></div></div></section>' % (a, n))
    del_.append('<footer class="sm"><span>Ruta · revisjon B · Iver R. Finne · GK5 modul 2 · AHO · 2026</span><span><a href="../leveransar/07_ruta/Ruta-presentasjon.pdf">PDF</a> &nbsp;·&nbsp; '
                '<a href="./">Studio</a> &nbsp;·&nbsp; <a href="../leveransar/07_ruta/presentasjon.html">Lysbilete</a> &nbsp;·&nbsp; <a href="3d/ruta.usdz">USDZ</a> &nbsp;·&nbsp; <a href="3d/ruta.glb">GLB</a> &nbsp;·&nbsp; '
                '<a href="../konsept/film/cad/ut-b/ruta-pa-fot-rev-b.step">STEP</a> &nbsp;·&nbsp; <a href="../">GK5 modul 2</a></span></footer>')
    skript = NETTSKRIPT.replace('__FARGAR__', json.dumps({k: [round(c[0], 4), round(c[1], 4), round(c[2], 4), n] for k, n, c in FARGAR}, ensure_ascii=False))
    html = ('<!doctype html>\n<html lang="nn">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>Ruta</title>\n'
            '<meta name="description" content="Ruta: ei lysande rute på éin stilk. Stemningsskapande lampe for heim og arbeid.">\n<style>%s</style>\n</head>\n<body>\n%s\n%s\n</body>\n</html>\n'
            % (NETTSTIL, '\n\n'.join(x for x in del_ if x), skript))
    assert '—' not in html and '–' not in html
    open(os.path.join(NETT, 'forteljing.html'), 'w', encoding='utf-8').write(html)
    # studioet: éin svart skjerm med modellen, tre modusar og éin glidar
    knapp = ''.join('<button type="button" data-farge="%s" aria-label="%s" aria-pressed="%s" style="background: %s;"></button>' % (k, n, 'true' if i == 0 else 'false', srgb(c)) for i, (k, n, c) in enumerate(FARGAR))
    mal = open(os.path.join(HER, 'studio.html.mal'), encoding='utf-8').read()
    st = mal.replace('__KNAPPAR__', knapp).replace('__FARGAR__', json.dumps({k: [round(c[0], 4), round(c[1], 4), round(c[2], 4), n] for k, n, c in FARGAR}, ensure_ascii=False))
    assert '—' not in st and '–' not in st
    open(os.path.join(NETT, 'index.html'), 'w', encoding='utf-8').write(st)
    print('nettstad: ruta/index.html (studio) og ruta/forteljing.html (%d bolkar), 3d: %s' % (len([x for x in del_ if x]), ' '.join(sorted(os.listdir(os.path.join(NETT, '3d'))))))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    bilete()
    if sys.argv[1:2] != ['bilete']:
        pdf(*lysbilete())
        nettstad()
