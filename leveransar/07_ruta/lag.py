# -*- coding: utf-8 -*-
"""
lag.py  ·  presentasjonen av Ruta, revisjon B

Objektet åleine på svart, eitt lys og éin biletstil gjennom alle sidene, og dei tekniske sidene som kvit strek.
Skriv presentasjon.html, Ruta-presentasjon.pdf og sider/side-NN.jpg (2254 x 1594).

  python lag.py            alt
  python lag.py bilete     berre bileta på nytt

To slag bilete, og kvar side seier kva ho viser:
  generert bilete  CAD-rendringa fotografert om av ein biletmodell, med same utsnitt og geometri. Illustrasjon, ikkje simulering
  strek            kantane i CAD-modellen med skjulte liner fjerna (konsept/film/cad/teikning_b.py)
Tala kjem frå CAD-kontrollen (konsept/film/cad/ut-b/kontroll.json).
"""
import os, sys, json, math, re, subprocess
from PIL import Image

HER = os.path.dirname(os.path.abspath(__file__))
ROT = os.path.normpath(os.path.join(HER, '..', '..'))
CAD = os.path.join(ROT, 'konsept', 'film', 'cad')
TEIK = os.path.join(CAD, 'ut-b', 'teikning')
BIL = os.path.join(HER, 'bilete')
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
B, H = 1127, 797

K = json.load(open(os.path.join(CAD, 'ut-b', 'kontroll.json'), encoding='utf-8'))

def kom(x, n=1): return (('%%.%df' % n) % x).replace('.', ',')
def finst(n): return os.path.exists(os.path.join(BIL, n + '.jpg'))

# ------------------------------------------------------------------ bileta

FARGAR = [('graabeige', 'Grå-beige'), ('morkegron', 'Mørkegrøn'), ('svart', 'Svart'), ('kirsebaer', 'Kirsebærraud')]

def bilete():
    """Gjer PNG om til JPEG, og set saman fargesida: same utsnitt i fire fargar, to gonger to."""
    for f in sorted(os.listdir(BIL)):
        if f.endswith('.png'):
            Image.open(os.path.join(BIL, f)).convert('RGB').save(os.path.join(BIL, f[:-4] + '.jpg'), quality=95, subsampling=0)
            os.remove(os.path.join(BIL, f))
    kjelder = ['f-messing'] + ['f-messing-' + k for k, _ in FARGAR[1:]]
    if all(finst(n) for n in kjelder):
        w, h = 2 * B, 2 * H; tw, th = B - 1, H - 1
        ark = Image.new('RGB', (w, h), (0, 0, 0))
        for i, n in enumerate(kjelder):
            b = Image.open(os.path.join(BIL, n + '.jpg')).convert('RGB').resize((tw, th), Image.LANCZOS)
            ark.paste(b, ((i % 2) * (tw + 2), (i // 2) * (th + 2)))
        ark.save(os.path.join(BIL, 'fargar.jpg'), quality=95, subsampling=0)
    print('bilete:', ' '.join(sorted(f[:-4] for f in os.listdir(BIL) if f.endswith('.jpg'))))

# ------------------------------------------------------------------ stil

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
  .sm b { color: #A6A29B; }
  .folio { position: absolute; left: 72px; right: 72px; bottom: 38px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: baseline; }
  .folio span:last-child { text-align: right; }
  .namnrad { position: absolute; left: 0; right: 0; bottom: 92px; display: grid; grid-template-columns: repeat(4, 1fr); }
  .namnrad span { text-align: center; }
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
  table.delar { border-collapse: collapse; font: 400 13.5px/1.25 "EBG", serif; width: 100%; }
  table.delar td { padding: 5.5px 0; border-bottom: 1px solid #1D1C1A; vertical-align: baseline; }
  table.delar td.id { width: 30px; color: #6C6964; }
  table.delar td.k { color: #8A8781; text-align: right; }
  .liste { font: 400 15px/1.35 "EBG", serif; }
  .liste div { display: grid; grid-template-columns: 1fr auto; column-gap: 18px; padding: 7px 0; border-bottom: 1px solid #1D1C1A; }
  .liste div span:last-child { color: #8A8781; text-align: right; }
  .liste.ein div { grid-template-columns: 1fr; color: #C9C5BE; }
"""

SIDER = []

def folio(merke):
    return '<div class="folio sm"><span>Ruta</span><span>%s</span><span>{NR}</span></div>' % merke

GEN = 'Generert bilete etter CAD-modellen'
STREK = 'Teikna frå CAD-modellen'

def biletside(bilete, h1, tekst, plass, merke=GEN, breidd=300, ekstra='', skyv=0):
    """Éi heildekt side: biletet, eitt utsegn og éi line tekst. plass er CSS for kvar orda står."""
    if not finst(bilete): return
    t = '<p class="t" style="max-width: %dpx;">%s</p>' % (breidd, tekst) if tekst else ''
    o = '<div class="ord" style="%s"><h1>%s</h1>%s</div>' % (plass, h1, t) if h1 else ''
    b = '<img class="bak" src="bilete/%s.jpg" alt=""%s>' % (bilete, ' style="left: %dpx;"' % skyv if skyv else '')
    if skyv > 0: b += '<div class="ton" style="left: %dpx;"></div>' % (skyv - 1)
    if skyv < 0: b += '<div class="ton" style="left: %dpx; transform: scaleX(-1);"></div>' % (B + skyv - 139)
    SIDER.append('<section class="side">%s%s%s%s</section>' % (b, o, ekstra, folio(merke)))

def s_framside():
    if not finst('f-framside'): return
    SIDER.append('''<section class="side"><img class="bak" src="bilete/f-framside.jpg" alt="">
<div class="ord" style="left: 300px; top: 468px;"><h1 class="namn">Ruta</h1><p class="t" style="margin-top: 28px; font-size: 20px; color: #C9C5BE;">Ei lysande rute på éin stilk.</p></div>
<div class="ord sm" style="left: 304px; right: 72px; bottom: 38px; display: flex; justify-content: space-between;"><span>Iver R. Finne · GK5 modul 2 · AHO · 2026</span><span>%s</span></div></section>''' % GEN)

def s_fargar():
    if not finst('fargar'): return
    x0, y0, w, h = 300, 106, 827, 585
    namn = ''.join('<div class="ord sm" style="left: %dpx; top: %dpx; color: #A6A29B;">%s</div>' % (x0 + 20 + (i % 2) * (w // 2 + 1), y0 + 18 + (i // 2) * (h // 2 + 1), n) for i, (_, n) in enumerate(FARGAR))
    bilete = '<img src="bilete/fargar.jpg" alt="" style="position: absolute; left: %dpx; top: %dpx; width: %dpx; height: %dpx; display: block;">' % (x0, y0, w, h)
    ord_ = ('<div class="ord" style="left: 72px; top: 250px;"><h1>Éin<br>matt<br>farge.</h1><p class="t" style="max-width: 190px;">Foten, røyret og bjelken får same pulverlakk. '
            'Messingen er den einaste andre fargen.</p></div>')
    SIDER.append('<section class="side">' + bilete + namn + ord_ + folio(GEN) + '</section>')

SPRENGT_FLYTT = {'08': (-22, -12, 'end'), '11': (-18, -12, 'end'), '05': (12, -20, 'start'), '10': (-22, -5, 'end'), '09': (-26, 8, 'end'),
                 '06': (-24, 12, 'end'), 'E': (-16, 16, 'end'), '07': (-24, 14, 'end'), '04': (16, -20, 'start'), '12': (18, -10, 'start'),
                 '13': (18, 8, 'start'), '01': (-30, -6, 'end'), '03': (-46, 6, 'end'), '02': (-32, 8, 'end')}
DELAR = [('01', 'Fot', 'trykt og lakkert'), ('02', 'Botnlok med pute', 'trykt'), ('03', 'Ballast', 'stålplate 5&nbsp;mm'),
         ('04', 'Røyr', 'stål Ø 12, éin boge'), ('05', 'Bjelke', 'trykt i to lengder'), ('06', 'Bjelkelok', 'trykt'),
         ('07', 'Lysleiar', 'plate 3&nbsp;mm frå skjermen'), ('08', 'Prismeark', 'frå skjermen'),
         ('09', 'Flatstong', 'aluminium 12 × 2'), ('10', 'LED-stripe', 'kjøpt'), ('11', 'Touch-dimmar', 'kjøpt'),
         ('12', 'Stoppskrue', 'M3 med tapp'), ('13', 'Bremseskrue', 'M4 med nylonspiss'), ('E', 'Fire skruar', 'M3 × 12')]

def s_sprengt():
    svg = open(os.path.join(TEIK, 'sprengt.svg'), encoding='utf-8').read()
    J = json.load(open(os.path.join(TEIK, 'sprengt.json')))
    lag = ''
    for i, p in J['anker'].items():
        dx, dy, anker = SPRENGT_FLYTT.get(i, (16, -16, 'start'))
        q = (p[0] + dx, p[1] + dy)
        lag += '<line class="l" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/><circle class="p" cx="%.1f" cy="%.1f" r="1.4"/>' % (p[0], p[1], q[0], q[1], p[0], p[1])
        lag += '<text class="nr" x="%.1f" y="%.1f" text-anchor="%s">%s</text>' % (q[0] + (5 if anker == 'start' else -5), q[1] + 4, anker, i)
    hogd = 690.0; f = hogd / J['hogd']
    svg = re.sub(r'<svg class="strek" width="\d+" height="\d+"', '<svg class="strek" width="%.0f" height="%.0f"' % (J['breidd'] * f, hogd), svg).replace('</svg>', lag + '</svg>')
    rader = ''.join('<tr><td class="id">%s</td><td>%s</td><td class="k">%s</td></tr>' % d for d in DELAR)
    SIDER.append('''<section class="side">
<div class="ord" style="left: 64px; top: 46px;">%s</div>
<div class="ord" style="left: 770px; top: 64px; width: 285px;"><h1 style="font-size: 44px;">Tretten delar, fire skruar.</h1>
<table class="delar" style="margin-top: 30px;">%s</table>
<p class="t" style="font-size: 14.5px; margin-top: 16px;">Kjøpt: LED-stripa og dimmaren. Frå ein gammal skjerm: plata og arket. Ingen skruar syner ovanfrå.</p></div>
%s</section>''' % (svg, rader, folio(STREK)))

def s_maal():
    svg = open(os.path.join(TEIK, 'maal.svg'), encoding='utf-8').read()
    SIDER.append('''<section class="side">
<div class="ord" style="left: 72px; top: 64px;"><h1>Mål.</h1></div>
<div class="ord" style="right: 72px; top: 86px; text-align: right;"><p class="t" style="margin: 0;">Breidd 378, djupn 223 og høgd 278&nbsp;mm.</p></div>
<div class="ord" style="left: 52px; top: 190px;">%s</div>
%s</section>''' % (svg, folio(STREK + ' · mål i mm')))

def s_fakta():
    if not finst('f-profil'): return
    T = K['tyngdepunkt']; e = math.hypot(T[0], T[1])
    A = [('Masse', '%d g av høgst 1200' % K['masse_g']), ('Fotavtrykk', '%s cm² av høgst 200' % kom(K['fotavtrykk_cm2'], 0)),
         ('Tyngdepunktet frå midten av foten', '%s mm' % kom(e, 0)), ('Trykk på hjørnet av ruta som veltar lampa', '%s N' % kom(K['velt_venstre_N'])),
         ('Helling utan kollisjon', '0° til 80°')]
    N = ['Bøyen i røyret: 120° med 45&nbsp;mm radius krev røyrbøyar.', 'Friksjonen og stoppen er teikna, ikkje bygde.',
         'Touch-dimmaren er ikkje vald.', 'At arket er ein prismefilm, er ikkje prøvd.', 'Ingen slicer-kontroll og ingen fysisk modell.',
         'Lyset er eit overslag for revisjon A og er ikkje rekna på nytt.']
    a = ''.join('<div><span>%s</span><span>%s</span></div>' % x for x in A)
    n = ''.join('<div>%s</div>' % x for x in N)
    SIDER.append('''<section class="side"><img class="bak" src="bilete/f-profil.jpg" alt="" style="left: -215px;"><div class="ton" style="left: 773px; transform: scaleX(-1);"></div>
<div class="ord" style="left: 640px; top: 64px; width: 415px;"><h1 style="font-size: 44px;">Kontrollert, ikkje bygd.</h1>
<div class="sm" style="margin-top: 34px;">Kontrollert i CAD</div><div class="liste" style="margin-top: 8px;">%s</div>
<div class="sm" style="margin-top: 30px;">Ikkje prøvd</div><div class="liste ein" style="margin-top: 8px;">%s</div></div>
%s</section>''' % (a, n, folio(GEN)))

def bygg():
    s_framside()
    biletside('f-helt', 'Ei rute som lyser.', 'Stemningsskapande lampe for heim og arbeid.', 'left: 72px; top: 318px;')
    biletside('f-front', 'Skive.<br>Røyr.<br>Blad.', 'Tre former møtest utan overgang. Røyret er stamme, aksel og kabelveg i eitt.', 'left: 72px; top: 250px;', breidd=230, skyv=170)
    biletside('f-vifte', 'Vipp.', 'Éi handling, frå vassrett til 80°. Stoppen og friksjonen ligg skjult inni bjelken.', 'left: 72px; top: 318px;', breidd=280)
    biletside('f-messing', 'Eitt punkt i messing.', 'Der du tek. Trykk for av og på, hald for å dimme.', 'left: 72px; bottom: 96px;')
    biletside('f-kant', 'Lyset kjem frå kanten.', 'Ei LED-stripe i bjelken lyser inn i ei klar plate. Eit prismeark frå ein gammal skjerm sender lyset ut.', 'right: 72px; bottom: 96px; width: 470px; text-align: right;', breidd=470)
    biletside('f-boge', 'Eitt røyr, éin boge.', 'Stål, 12&nbsp;mm. Éin boge på 120° med 45&nbsp;mm radius.', 'left: 290px; bottom: 96px;')
    biletside('p0-framside', 'Om kvelden.', '190&nbsp;lx på bordet under ruta ved 2&nbsp;W. Eit stemningslys og sidelys, ikkje eit arbeidslys.', 'left: 72px; top: 318px;', breidd=290,
              merke=GEN + ' · overslag for revisjon A, same rute og høgd')
    s_fargar()
    s_sprengt()
    s_maal()
    s_fakta()
    n = len(SIDER)
    svart = '<section class="side"><img class="bak" src="bilete/svart.jpg" alt="">'
    kropp = '\n\n'.join(x.replace('{NR}', '%02d' % (i + 1)).replace('<section class="side">', svart, 1) for i, x in enumerate(SIDER))
    html = ('<!doctype html>\n<html lang="nn">\n<head>\n<meta charset="utf-8">\n<title>Ruta</title>\n<style>%s</style>\n</head>\n<body>\n%s\n</body>\n</html>\n' % (STIL, kropp))
    assert '—' not in html and '–' not in html
    hf = os.path.join(HER, 'presentasjon.html'); open(hf, 'w', encoding='utf-8').write(html)
    for i, s in enumerate(SIDER):
        print('  side %2d: %3d ord' % (i + 1, len(re.sub(r'<[^>]+>', ' ', re.sub(r'<svg.*?</svg>', ' ', s, flags=re.S)).replace('&nbsp;', ' ').split())))
    return hf, n

def skriv(hf, n):
    import fitz, tempfile, shutil
    pdf = os.path.join(HER, 'Ruta-presentasjon.pdf')
    prof = tempfile.mkdtemp(prefix='chrome-ruta-')
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--user-data-dir=' + prof, '--no-pdf-header-footer',
                    '--virtual-time-budget=8000', '--print-to-pdf=' + pdf, 'file:///' + hf.replace('\\', '/')], check=True, capture_output=True, timeout=300)
    d = fitz.open(pdf); ut = os.path.join(HER, 'sider')
    if os.path.isdir(ut): shutil.rmtree(ut)
    os.makedirs(ut)
    for i, s in enumerate(d):
        px = s.get_pixmap(matrix=fitz.Matrix(2254 / s.rect.width, 1594 / s.rect.height), alpha=False)
        Image.frombytes('RGB', (px.width, px.height), px.samples).save(os.path.join(ut, 'side-%02d.jpg' % (i + 1)), quality=94, subsampling=0)
    print('pdf: %d sider (venta %d), %.1f MB' % (len(d), n, os.path.getsize(pdf) / 1e6))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    bilete()
    if sys.argv[1:2] != ['bilete']:
        skriv(*bygg())
