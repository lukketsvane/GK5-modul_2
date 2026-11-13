# -*- coding: utf-8 -*-
"""
lag.py  ·  presentasjonen av Ruta, revisjon B

Les tala frå CAD-kontrollen (konsept/film/cad/ut-b/kontroll.json), hentar rendringane derifrå, og skriv
presentasjon.html, Ruta-presentasjon.pdf og png/side-NN.png (2254 x 1594).

  python lag.py            alt
  python lag.py bilete     berre bileta på nytt

To slag bilete er med, og kvar side seier kva som er kva:
  rendring         geometrien frå CAD-en, rendra i Blender. Gløden er ei visualisering, ikkje ei lysrekning
  generert bilete  laga med ein biletmodell etter CAD-rendringa. Illustrasjon, ikkje simulering
"""
import os, sys, json, math, re, subprocess
from PIL import Image, ImageChops

HER = os.path.dirname(os.path.abspath(__file__))
ROT = os.path.normpath(os.path.join(HER, '..', '..'))
CAD = os.path.join(ROT, 'konsept', 'film', 'cad')
RUT = os.path.join(CAD, 'ut-b', 'render')
BIL = os.path.join(HER, 'bilete')
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
DATO = '13.11.2026'
B, H = 1127, 797

K = json.load(open(os.path.join(CAD, 'ut-b', 'kontroll.json'), encoding='utf-8'))
G = json.load(open(os.path.join(CAD, 'ut-b', 'geometri.json'), encoding='utf-8'))

def kom(x, n=1): return (('%%.%df' % n) % x).replace('.', ',')

# ------------------------------------------------------------------ bileta

GENERERTE = ['p0-framside', 'p1-miljo', 'p2-kveld', 'p3-pakke', 'p4-hand', 'p5-messing', 'p6-heim']
RENDRA = ['studio', 'detalj-messing', 'sprengt', 'kveld', 'rev-b-graabeige', 'rev-b-morkegron', 'rev-b-svart', 'rev-b-kirsebaer']

def bilete():
    """Gjer om til JPEG, så PDF-en og repoet held seg lette. Dei genererte bileta ligg som PNG i bilete/ til dei er gjorde om."""
    for n in GENERERTE:
        p = os.path.join(BIL, n + '.png')
        if os.path.exists(p):
            Image.open(p).convert('RGB').save(os.path.join(BIL, n + '.jpg'), quality=94, subsampling=0); os.remove(p)
    for n in RENDRA:
        p = os.path.join(RUT, n + '.png')
        if os.path.exists(p): Image.open(p).convert('RGB').save(os.path.join(BIL, n + '.jpg'), quality=93, subsampling=0)
    h = [os.path.join(RUT, 'helling-%02d.png' % v) for v in (0, 35, 70)]
    if all(os.path.exists(p) for p in h):
        im = [Image.open(p).convert('RGB') for p in h]
        ImageChops.lighter(ImageChops.lighter(im[0], im[1]), im[2]).save(os.path.join(BIL, 'helling.jpg'), quality=93, subsampling=0)
    print('bilete:', ' '.join(sorted(f for f in os.listdir(BIL) if f.endswith('.jpg'))))

def finst(n): return os.path.exists(os.path.join(BIL, n + '.jpg'))

# ------------------------------------------------------------------ projeksjon til merkelappane

def kamera(pos, maal, lens, bh):
    """Hòlkamera slik Blender set det opp i render_presentasjon.py. Gjev funksjonen frå rompunkt i mm til (u, v) i biletet."""
    f = [maal[i] - pos[i] for i in range(3)]; l = math.sqrt(sum(a * a for a in f)); f = [a / l for a in f]
    r = [f[1], -f[0], 0.0]; l = math.hypot(r[0], r[1]); r = [a / l for a in r]
    o = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    def p(q):
        d = [q[i] / 1000.0 - pos[i] for i in range(3)]
        x = sum(d[i] * r[i] for i in range(3)); y = sum(d[i] * o[i] for i in range(3)); z = sum(d[i] * f[i] for i in range(3))
        return 0.5 + x / z * lens / 36.0, 0.5 - y / z * lens / 36.0 * bh
    return p

def dekk(u, v, bh):
    """Frå (u, v) i eit bilete med breidd/høgd bh til pikslar på ei heildekt side."""
    w = H * bh
    return u * w - (w - B) / 2, v * H

def bjelkemidt(x):
    t = math.radians(180.0 + G['VINKEL'])
    return (x, G['YT'] + G['EKS'] * math.cos(t), G['AKSE_H'] + G['EKS'] * math.sin(t))

# ------------------------------------------------------------------ sidene

STIL = """
  html, body { background: #000; }
  .side { break-after: page; page-break-after: always; }
  .side.heil { padding: 0; display: block; }
  .side.heil img.bak { position: absolute; left: 0; top: 0; width: 1127px; height: 797px; object-fit: cover; display: block; }
  .side.heil svg.lag { position: absolute; left: 0; top: 0; }
  .side.heil .over { position: absolute; }
  .merk { font: 400 9.5px/1.4 var(--mono); letter-spacing: 0.08em; text-transform: uppercase; color: rgba(255,255,255,0.62); }
  .merk b { color: #fff; }
  .namn { font: 400 148px/0.86 var(--serif); color: #fff; letter-spacing: -0.025em; margin: 0; }
  .under { font: 400 23px/1.22 var(--serif); color: #F4F4F4; margin: 22px 0 0; max-width: 330px; }
  .linje { font: 400 34px/1.1 var(--serif); color: #fff; margin: 0; letter-spacing: -0.005em; }
  .skugge { text-shadow: 0 0 18px rgba(0,0,0,0.55); }
  .side.delt { padding: 0; display: grid; grid-template-columns: 531px minmax(0, 1fr); grid-template-rows: none; }
  .side.delt .bilete img { width: 531px; height: 797px; object-fit: cover; display: block; }
  .side.delt .kol { padding: 26px 44px 22px 40px; display: grid; grid-template-rows: auto minmax(0, 1fr) auto; min-height: 0; }
  .side.delt .kol .midt { align-self: center; }
  .side.delt .tittel { font-size: 44px; margin: 0 0 22px; }
  .side.delt p { font-size: 17px; line-height: 1.36; max-width: 440px; margin-bottom: 0.7em; }
  .side.delt p.stor { font-size: 25px; line-height: 1.2; margin-bottom: 0.8em; }
  figure.lag { position: relative; }
  figure.lag svg { position: absolute; left: 0; top: 0; }
  svg .l { stroke: #fff; stroke-width: 0.8; fill: none; }
  svg .ls { stroke: #000; stroke-opacity: 0.45; stroke-width: 2.4; fill: none; }
  svg .pr { fill: #fff; }
  svg text.m1 { fill: #fff; font-size: 10px; letter-spacing: 0.06em; }
  svg text.m2 { fill: #BDBDBD; font-size: 9.5px; letter-spacing: 0.04em; }
  svg text.nr { fill: #fff; font-size: 10.5px; letter-spacing: 0.04em; }
  .tekst p { font-size: 16px; line-height: 1.36; margin-bottom: 0.65em; }
  .tal3 { display: grid; row-gap: 14px; margin: 2px 0 18px; }
  .tal3 .stortal { font-size: 46px; }
  .tal3 .stortal span { font-size: 22px; color: var(--tekst); margin-left: 4px; }
  .tal5 { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); column-gap: 20px; border-top: 1px solid var(--linje); padding-top: 12px; }
  .tal5 .stortal { font-size: 34px; }
  .tal5 .stortal span { font-size: 17px; color: var(--tekst); margin-left: 3px; }
  .fargar { display: grid; grid-template-columns: 1fr 1fr; column-gap: 16px; row-gap: 12px; }
  .sidekol .tittel { margin: 0 0 18px; font-size: 34px; }
  .sidekol p { font-size: 15.5px; line-height: 1.36; }
  table.delar { font-size: 12.5px; line-height: 1.25; }
  table.delar td { padding: 4px 10px 4px 0; }
  table.delar td.id { width: 26px; color: var(--blekk); }
  table.delar td.k { color: var(--graa); }
  svg.maal { width: 100%; height: auto; }
  svg.maal .k { stroke: #fff; stroke-width: 1.15; fill: none; }
  svg.maal .s { stroke: #fff; stroke-width: 0.75; fill: none; }
  svg.maal .t { stroke: #BDBDBD; stroke-width: 0.5; fill: none; }
  svg.maal .m, svg.maal .h { stroke: #8E8E8E; stroke-width: 0.6; fill: none; }
  svg.maal .g { stroke: #5C5C5C; stroke-width: 0.6; fill: none; }
  svg.maal .st { stroke: #8E8E8E; stroke-width: 0.6; stroke-dasharray: 4 3; fill: none; }
  svg.maal .p { fill: #8E8E8E; }
  svg.maal text.mt { font-size: 10.5px; fill: #D9D9D9; }
  svg.maal text.et { font-size: 10px; fill: #8E8E8E; letter-spacing: 0.09em; }
"""

SIDER = []
def legg(html): SIDER.append(html)

def topp(nr, merke):
    return '<header class="topp"><span>GK5 modul 2 · Northern</span><span>%02d · %s</span><span>Iver R. Finne · %s</span></header>' % (nr, merke, DATO)

def botn(nr, kjelde):
    return '<footer class="botn"><span>%s</span><span>Ruta · revisjon B · {NR%d}</span></footer>' % (kjelde, nr)

def vanleg(nr, merke, tittel, innhald, kjelde, stil=''):
    legg('<section class="side">\n%s\n<h1 class="tittel">%s</h1>\n<main class="innhald"%s>\n%s\n</main>\n%s\n</section>' % (
        topp(nr, merke), tittel, (' style="%s"' % stil) if stil else '', innhald, botn(nr, kjelde)))

def peikar(p, q, t1, t2='', anker='start'):
    """Tynn line frå punktet p til q, med to tekstliner ved q."""
    dx = 5 if anker == 'start' else -5 if anker == 'end' else 0
    s = '<line class="ls" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/><line class="l" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (*p, *q, *p, *q)
    s += '<circle class="pr" cx="%.1f" cy="%.1f" r="1.8"/>' % p
    s += '<text class="m1" x="%.1f" y="%.1f" text-anchor="%s">%s</text>' % (q[0] + dx, q[1] + 3, anker, t1)
    if t2: s += '<text class="m2" x="%.1f" y="%.1f" text-anchor="%s">%s</text>' % (q[0] + dx, q[1] + 16, anker, t2)
    return s

def s01():
    bak = 'p0-framside' if finst('p0-framside') else 'p2-kveld'
    legg('''<section class="side heil">
<img class="bak" src="bilete/%s.jpg" alt="">
<div class="over" style="left: 56px; top: 44px;"><div class="merk">GK5 modul 2 · AHO · november 2026</div></div>
<div class="over skugge" style="left: 52px; top: 250px;">
  <h1 class="namn">Ruta</h1>
  <p class="under">Ei lysande rute på éin stilk. Stemningsskapande lampe for heim og arbeid.</p>
</div>
<div class="over" style="left: 56px; bottom: 30px;"><div class="merk">Iver R. Finne · revisjon B · %s</div></div>
<div class="over" style="right: 44px; bottom: 30px; text-align: right;"><div class="merk">Generert bilete etter CAD-modellen. Lyset i biletet er ikkje rekna.</div></div>
</section>''' % (bak, DATO))

def s02():
    legg('''<section class="side delt">
<div class="bilete"><img src="bilete/p1-miljo.jpg" alt=""></div>
<div class="kol">
%s
<div class="midt">
  <h1 class="tittel">Ei rute som lyser, på éin stilk.</h1>
  <p class="stor">Tre former: ei skive, eit røyr og eit blad.</p>
  <p>Bladet er ei klar plate som lyser frå kanten. Lyskjelda ligg skjult i bjelken og syner aldri.</p>
  <p>Lampa er teikna inn i formspråket til Northern: éin matt farge over heile lekamen, eitt røyr i éi rørsle, og eitt punkt i messing som òg er brytaren.</p>
  <p>Ho gjev eit lågt og varmt lys til pulten og veggen bak. Ho er eit stemningslys og sidelys, heime og ved skjermen.</p>
</div>
%s
</div>
</section>''' % (topp(2, 'Ideen'), botn(2, 'Generert bilete etter CAD-modellen. Grå-beige.')))

def s03():
    bh = 1.5
    k = kamera((-0.52, -0.80, 0.27), (-0.01, 0.0, 0.132), 60.0, bh)
    P = lambda q: dekk(*k(q), bh)
    r = G['FOT_D'] / 2
    zr = 120.0; xr = G['ROYR_FOT'][0] + (zr - G['FOT_H']) * math.tan(math.radians(30.0))
    blad = bjelkemidt(G['XR0'] + 0.62 * G['RUTE_B']); blad = (blad[0], blad[1], blad[2] + G['R'])
    mess = bjelkemidt(G['X0'] - 1.0)
    skive = (r * 0.72, -r * 0.5, G['FOT_H'])
    a, b, c, d = P(blad), P((xr, G['YT'], zr)), P(skive), P(mess)
    lag = (peikar(a, (a[0] + 40, 58), 'BLAD', 'bjelke Ø 36 med rute 300 × 190') +
           peikar(b, (b[0] + 150, b[1] - 6), 'RØYR', 'stål Ø 12 i éi rørsle') +
           peikar(c, (c[0] + 130, c[1] + 44), 'SKIVE', 'fot Ø 158 med ballast') +
           peikar(d, (d[0] - 46, d[1] + 120), 'MESSINGPUNKT', 'touch-dimmar Ø 20', 'middle'))
    legg('''<section class="side heil">
<img class="bak" src="bilete/studio.jpg" alt="">
<svg class="lag" width="1127" height="797" viewBox="0 0 1127 797" xmlns="http://www.w3.org/2000/svg">%s</svg>
<div class="over" style="left: 56px; top: 30px; right: 44px;"><div class="merk" style="display: flex; justify-content: space-between;"><span>GK5 modul 2 · Northern</span><span><b>03 · Forma</b></span><span>Iver R. Finne · %s</span></div></div>
<div class="over" style="left: 56px; bottom: 64px; max-width: 420px;">
  <p class="linje">Tre former møtest utan overgangsform.</p>
  <p class="under" style="margin-top: 12px; font-size: 19px; max-width: 380px; color: #D9D9D9;">Skiva ber, røyret løftar, bladet lyser. Røyret er stamme, aksel og kabelveg i eitt.</p>
</div>
<div class="over" style="left: 56px; bottom: 30px;"><div class="merk">Rendring av CAD-modellen. Gløden er ei visualisering, ikkje ei lysrekning.</div></div>
<div class="over" style="right: 44px; bottom: 30px;"><div class="merk">Ruta · revisjon B · {NR3}</div></div>
</section>''' % (lag, DATO))

def s04():
    vanleg(4, 'Handlinga', 'Éi handling: vipp ruta.', '''
<figure class="k7"><img src="bilete/helling.jpg" alt=""><figcaption><b>0°, 35° og 70°</b> · tre rendringar av CAD-modellen, lagde oppå kvarandre</figcaption></figure>
<div class="k5">
  <figure><img src="bilete/p4-hand.jpg" alt=""><figcaption>Generert bilete etter CAD-modellen</figcaption></figure>
  <div class="tekst" style="margin-top: 18px;">
    <p>Bjelken dreier rett på røyret, frå vassrett til 80°. Vassrett lyser ruta ned på pulten. Bratt vender ho undersida mot veggen og står som eit varmt vindauge.</p>
    <p>Ein skrue inni bjelken stoppar rørsla i begge endar og held bjelken på røyret. Ein annan set friksjonen éin gong. Ingen av dei syner.</p>
  </div>
</div>''', 'Rørsla er kontrollert i CAD i steg på 10° frå 0° til 80°: ingen kollisjonar. Ho er ikkje bygd.')

def s05():
    vanleg(5, 'Messingpunktet', 'Eitt punkt i messing, der du tek.', '''
<figure class="k7"><img src="bilete/p5-messing.jpg" alt=""><figcaption>Generert bilete etter CAD-modellen</figcaption></figure>
<div class="k5">
  <figure><img src="bilete/detalj-messing.jpg" alt=""><figcaption>Rendring av CAD-modellen: enden slik han er teikna</figcaption></figure>
  <div class="tekst" style="margin-top: 18px;">
    <p>Dimmaren sit i den frie enden av bjelken: ei skive i børsta messing, 20&nbsp;mm brei, éin millimeter ut frå enden. Ho er den einaste blanke flata på lampa.</p>
    <p>Tenkt bruk: kort trykk slår av og på, langt trykk dimmar. Modulen er ikkje vald, og han må kjøpast saman med LED-stripa.</p>
  </div>
</div>''', 'Northern brukar same grepet: touch-dimmar i messing i enden av armen på Salto.')

def s06():
    legg('''<section class="side heil">
<img class="bak" src="bilete/p6-heim.jpg" alt="">
<div class="over" style="left: 56px; top: 30px; right: 44px;"><div class="merk" style="display: flex; justify-content: space-between;"><span>GK5 modul 2 · Northern</span><span><b>06 · Heime</b></span><span>Iver R. Finne · %s</span></div></div>
<div class="over skugge" style="right: 44px; top: 330px; width: 250px; text-align: right;">
  <p class="linje">Heime, om kvelden.</p>
</div>
<div class="over" style="left: 56px; bottom: 30px;"><div class="merk">Generert bilete etter CAD-modellen. Svart. Lyset i biletet er ikkje rekna.</div></div>
<div class="over" style="right: 44px; bottom: 30px;"><div class="merk">Ruta · revisjon B · {NR6}</div></div>
</section>''' % DATO)

def s07():
    vanleg(7, 'Lyset', 'Stemningslys og sidelys, ikkje arbeidslys.', '''
<figure class="k7"><img src="bilete/kveld.jpg" alt=""><figcaption>Rendring av CAD-modellen, mørkegrøn. Gløden er ei visualisering</figcaption></figure>
<div class="k5">
  <div class="tal3">
    <div class="stortal">190<span>lx</span><small>bordet under ruta, snitt, ved 2 W</small></div>
    <div class="stortal">57<span>lx</span><small>feltet framfor skjermen. Arbeidslys krev 350</small></div>
    <div class="stortal">372<span>cd/m²</span><small>høgst mot auget. Grensa for stemningslys er 500</small></div>
  </div>
  <div class="tekst">
    <p>LED-stripa lyser inn i kanten på ei 3&nbsp;mm plate. Oppå ligg prismearket frå ein gammal skjerm.</p>
    <p>Tala er eit overslag for revisjon A, som har same rute, høgd og helling. Dei kviler på ei antaking om kor mykje lys som kjem inn i plata. Lyset er ikkje rekna på nytt.</p>
  </div>
</div>''', 'Overslag: konsept/film/cad/lys_sjekk.py. At arket er ein prismefilm, er ikkje prøvd.')

def s08():
    f = lambda kode, namn: '<figure><img src="bilete/rev-b-%s.jpg" alt=""><figcaption><b>%s</b></figcaption></figure>' % (kode, namn)
    legg('''<section class="side">
%s
<main class="innhald" style="grid-row: 2 / 4; padding-top: 22px;">
<div class="k3 sidekol">
  <h1 class="tittel">Éin matt farge over heile lekamen.</h1>
  <p>Grå-beige er hovudfargen. Dei nyaste lampene til Northern kjem i han.</p>
  <p>Mørkegrøn og svart er dei andre trygge vala i paletten. Kirsebærraud er aksentfargen frå skissa.</p>
  <p class="graa">Foten, røyret og bjelken får same pulverlakk. Messingen er den einaste andre fargen.</p>
</div>
<div class="k9 fargar">%s%s%s%s</div>
</main>
%s
</section>''' % (topp(8, 'Fargane'), f('graabeige', 'Grå-beige'), f('morkegron', 'Mørkegrøn'), f('svart', 'Svart'), f('kirsebaer', 'Kirsebærraud'),
                 botn(8, 'Fire rendringar av CAD-modellen i dagslys frå sida. Gløden er ei visualisering.')))

SPRENGT_FLYTT = {}       # id -> (dx, dy, anker) for nummera på den sprengte visinga
DELAR = [('01', 'Fot', 'trykt og lakkert'), ('02', 'Botnlok med pute', 'trykt'), ('03', 'Ballast', 'stålplate 5&nbsp;mm'),
         ('04', 'Røyr', 'stål Ø 12 × 1,5, éin boge'), ('05', 'Bjelke', 'trykt i to lengder'), ('06', 'Bjelkelok', 'trykt, på undersida'),
         ('07', 'Lysleiar', 'plate 3&nbsp;mm frå skjermen, eller akryl'), ('08', 'Prismeark', 'frå skjermen'),
         ('09', 'Flatstong', 'aluminium 12 × 2'), ('10', 'LED-stripe', 'kjøpt · 5 V, 2700 K'), ('11', 'Touch-dimmar', 'kjøpt · børsta messing'),
         ('12', 'Stoppskrue', 'M3 med tapp, i røyret'), ('13', 'Bremseskrue', 'M4 med nylonspiss'), ('E', 'Fire skruar M3 × 12', 'nedanfrå i loket')]

def s09():
    w, h = 599.0, 599.0 * 1300 / 1500
    A = json.load(open(os.path.join(RUT, 'sprengt.json')))
    lag = ''
    for i, (u, v) in A.items():
        dx, dy, anker = SPRENGT_FLYTT.get(i, (0, -22, 'middle'))
        p = (u * w, v * h); q = (p[0] + dx, p[1] + dy)
        lag += '<line class="ls" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/><line class="l" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (*p, *q, *p, *q)
        lag += '<circle class="pr" cx="%.1f" cy="%.1f" r="1.6"/>' % p
        tx = q[0] + (4 if anker == 'start' else -4 if anker == 'end' else 0); ty = q[1] + (3.5 if anker != 'middle' else (-4 if dy < 0 else 11))
        lag += '<text class="nr" x="%.1f" y="%.1f" text-anchor="%s">%s</text>' % (tx, ty, anker, i)
    rader = ''.join('<tr><td class="id">%s</td><td>%s</td><td class="k">%s</td></tr>' % d for d in DELAR)
    vanleg(9, 'Oppbygginga', 'Tretten delar og fire skruar.', '''
<figure class="k7 lag"><img src="bilete/sprengt.jpg" alt=""><svg width="%d" height="%d" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">%s</svg></figure>
<div class="k5">
  <table class="delar"><tr><th></th><th>Del</th><th>Laga av</th></tr>%s</table>
  <p class="liten" style="margin-top: 12px;">Kjøpt: LED-stripa og touch-dimmaren. Frå skjermen: plata og prismearket. Trykt: fot, botnlok, bjelke og lok. Røyret og ballasten er stål som må skaffast.</p>
</div>''' % (w, h, w, h, lag, rader), 'Rendring av CAD-modellen med delane trekte frå kvarandre og ruta vassrett. Ingen skruar syner ovanfrå.')

def s10():
    svg = open(os.path.join(CAD, 'ut-b', 'teikning', 'maal.svg'), encoding='utf-8').read()
    T = K['tyngdepunkt']; e = math.hypot(T[0], T[1])
    tal = [('%d' % K['masse_g'], 'g', 'masse. Kravet er høgst 1200'), (kom(K['fotavtrykk_cm2'], 0), 'cm²', 'fotavtrykk. Kravet er høgst 200'),
           (kom(e, 0), 'mm', 'tyngdepunktet frå midten av foten'), (kom(K['velt_venstre_N']), 'N', 'trykk på hjørnet av ruta som veltar lampa'),
           ('0 til 80', '°', 'helling utan kollisjon')]
    rad = ''.join('<div class="stortal">%s<span>%s</span><small>%s</small></div>' % t for t in tal)
    vanleg(10, 'Mål og kontroll', 'Lampa held krava til vekt og fotavtrykk.', '''
<div class="k12">%s</div>
<div class="k12 tal5">%s</div>''' % (svg, rad), 'Mål i mm. Teikninga og tala kjem frå same CAD-modell: konsept/film/cad/northern.py.', stil='row-gap: 16px;')

def s11():
    P = [('Bøyen i røyret.', '120° med 45&nbsp;mm radius i stålrøyr Ø 12 × 1,5 krev røyrbøyar.'),
         ('Friksjonen.', 'Bremseskruen og stoppskruen er teikna og kontrollerte digitalt. Dei er ikkje bygde.'),
         ('Dimmaren.', 'Touch-modulen er ikkje vald. Alternativet er dimmar på leidningen, med messingpunktet som lok.'),
         ('Prismearket.', 'Lommelyktprøva og måla med skyvelære står att.'),
         ('Trykk og prototyp.', 'Ingen slicer-kontroll og ingen fysisk modell enno.'),
         ('Lyset.', 'Overslaget gjeld revisjon A og er ikkje rekna på nytt.')]
    pk = ''.join('<div class="punkt"><span class="nr">%02d</span><p><em>%s</em> %s</p></div>' % (i + 1, a, b) for i, (a, b) in enumerate(P))
    vanleg(11, 'Det som står att', 'Seks ting er ikkje prøvde enno.', '''
<figure class="k7"><img src="bilete/p3-pakke.jpg" alt=""><figcaption>Generert bilete etter CAD-modellen. Grå-beige</figcaption></figure>
<div class="k5">%s</div>''' % pk, 'CAD, STEP og printfiler: konsept/film/cad/ut-b/.')

def bygg():
    for f in (s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11): f()
    n = len(SIDER)
    kropp = '\n\n'.join(SIDER)
    kropp = re.sub(r'\{NR(\d+)\}', lambda m: '%s av %d' % (m.group(1), n), kropp)
    html = ('<!doctype html>\n<html lang="nn">\n<head>\n<meta charset="utf-8">\n<title>Ruta · revisjon B</title>\n'
            '<link rel="stylesheet" href="../01_fase1_v2/felles.css">\n<style>%s</style>\n</head>\n<body>\n%s\n</body>\n</html>\n' % (STIL, kropp))
    assert '—' not in html and '–' not in html
    hf = os.path.join(HER, 'presentasjon.html'); open(hf, 'w', encoding='utf-8').write(html)
    for i, s in enumerate(SIDER):
        ord_ = len(re.sub(r'<svg.*?</svg>', ' ', re.sub(r'<style.*?</style>', ' ', s, flags=re.S), flags=re.S).replace('&nbsp;', ' ').split()) if False else \
               len(re.sub(r'<[^>]+>', ' ', re.sub(r'<svg.*?</svg>', ' ', s, flags=re.S)).replace('&nbsp;', ' ').split())
        print('  side %2d: %3d ord' % (i + 1, ord_))
    return hf, n

def skriv(hf, n):
    import fitz, tempfile
    pdf = os.path.join(HER, 'Ruta-presentasjon.pdf')
    prof = tempfile.mkdtemp(prefix='chrome-ruta-')
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--user-data-dir=' + prof, '--no-pdf-header-footer',
                    '--virtual-time-budget=6000', '--print-to-pdf=' + pdf, 'file:///' + hf.replace('\\', '/')], check=True, capture_output=True, timeout=240)
    d = fitz.open(pdf); os.makedirs(os.path.join(HER, 'png'), exist_ok=True)
    for i, s in enumerate(d):
        s.get_pixmap(matrix=fitz.Matrix(2254 / s.rect.width, 1594 / s.rect.height)).save(os.path.join(HER, 'png', 'side-%02d.png' % (i + 1)))
    print('pdf: %d sider (venta %d), %.1f MB' % (len(d), n, os.path.getsize(pdf) / 1e6))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    bilete()
    if sys.argv[1:2] != ['bilete']:
        skriv(*bygg())
