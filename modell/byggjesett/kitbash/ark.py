# -*- coding: utf-8 -*-
"""ark.py · to ark i husstilen frå fase 1 (1127 × 797, svart): brettet med tal, og valet (a)/(b)/(c)

  python ark.py      skriv brett-ark.png, ark-brett.html/.png og ark-val.html/.png
"""
import os, sys, json, subprocess, tempfile, shutil
from PIL import Image

HER = os.path.dirname(os.path.abspath(__file__))
ROT = os.path.dirname(os.path.dirname(os.path.dirname(HER)))
CSS = os.path.relpath(os.path.join(ROT, 'leveransar', '01_fase1_v2', 'felles.css'), HER).replace('\\', '/')
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
T, G, S, SK = 512, 48, 120, 0.24          # flis, luft og tekststripe i biletet (px), og målestokken på arket
TOPP = '''  <header class="topp">
    <span>GK5 · Northern · kitbash</span>
    <span>%s</span>
    <span>Iver R. Finne · 13.11.2026</span>
  </header>'''


def k(x, d=1):
    return ('%.*f' % (d, x)).replace('.', ',')


def brettbilete():
    """Dei 16 flisene med luft mellom og plass til tekst under, utan tekst (teksten er redigerbar på arket)."""
    im = Image.new('RGB', (4 * T + 3 * G, 4 * (T + S)), (0, 0, 0))
    for i in range(16):
        im.paste(Image.open(os.path.join(HER, 'flis', '%02d.png' % (i + 1))), ((i % 4) * (T + G), (i // 4) * (T + S)))
    im.save(os.path.join(HER, 'brett-ark.png'))
    return im.size


def ark_brett(R, L):
    W, H = brettbilete(); w, h = W * SK, H * SK
    merke = []
    for r in R[:16]:
        i = r['id'] - 1; x = (i % 4) * (T + G) * SK; y = ((i // 4) * (T + S) + T) * SK + 3
        tal = ('%s W · U0 %s · %s lx' % (k(r['W350'], 1), k(r['U0'], 2), k(r['bak350'], 0))) if 'W350' in r else ''
        merke.append(f'      <div class="m" style="left:{x:.1f}px;top:{y:.1f}px"><b>{r["id"]} {r["namn"]}</b><br>{tal}</div>')
    r4 = R[3]; v = L['over-vipp']; d1 = L['over-vindauge-q30']
    return f'''<!doctype html>
<html lang="nn">
<head>
<meta charset="utf-8">
<title>Kitbash · brett</title>
<link rel="stylesheet" href="{CSS}">
<style>
  .to {{ display: grid; grid-template-columns: {w:.0f}px minmax(0, 1fr); column-gap: 36px; }}
  .brett {{ position: relative; width: {w:.0f}px; height: {h:.0f}px; }}
  .brett img {{ position: absolute; left: 0; top: 0; width: {w:.1f}px; height: {h:.1f}px; display: block; }}
  .brett .m {{ position: absolute; font: 400 8px/10.5px var(--mono); letter-spacing: 0.02em; color: var(--graa); white-space: nowrap; text-transform: uppercase; }}
  .brett .m b {{ color: var(--blekk); }}
  .tal4 {{ display: flex; gap: 24px; margin: 0 0 16px; }}
  .tal4 div {{ font: 400 34px/1 var(--serif); color: var(--blekk); white-space: nowrap; }}
  .tal4 small {{ display: block; font: 400 9px/1.2 var(--mono); letter-spacing: 0.08em; text-transform: uppercase; color: var(--graa); margin-top: 5px; }}
</style>
</head>
<body>
<div class="side">
{TOPP % 'Generasjon 1 · 16 kroppar'}

  <h1 class="tittel">Eitt grep held alle lyskrava: LED-stripa mot fresnelplata over skjermkanten.</h1>

  <main class="innhald" style="display: block;">
    <div class="to">
      <div class="brett">
        <img src="brett-ark.png" alt="">
{chr(10).join(merke)}
      </div>
      <section>
        <p class="etikett">Kropp 4 · Klype · band</p>
        <div class="tal4">
          <div>{k(r4['W350'], 1)} W<small>for 350 lx</small></div>
          <div>{k(r4['U0'], 2)}<small>jamnheit</small></div>
          <div>{k(r4['bak350'], 0)} lx<small>veggen bak</small></div>
          <div>{k(r4['auge'], 0)}<small>cd/m² mot auget</small></div>
        </div>
        <p class="etikett">Kva tala seier</p>
        <div class="punkt"><span class="nr">01</span><p>Over skjermkanten slår fot. Jamnheita er 0,41 til {k(r4['U0'], 2)} der, mot 0,29 til 0,39 for plata på fot.</p></div>
        <div class="punkt"><span class="nr">02</span><p>LED-stripa i staden for éi diode løftar jamnheita frå {k(d1['jamnheit'], 2)} til {k(r4['U0'], 2)}, utan diffusorark på plata.</p></div>
        <div class="punkt"><span class="nr">03</span><p>Vindaugsdioden held veggen lys utan at noko sveipar over skjermen: sprang {k(r4['sprang'], 2)}, mot {k(v['sprang'], 2)} når plata vippar.</p></div>
        <div class="punkt"><span class="nr">04</span><p>Ruta på fot treng {k(R[12]['W350'], 1)} W. Plata på fot held veggen med flik, men jamnheita blir {k(R[9]['U0'], 2)}, og ho veltar ved {k(R[9]['dytt_N'], 1)} N.</p></div>
        <div class="punkt"><span class="nr">05</span><p>Kropp 4 fell på éin ting: {k(r4['masse_g'], 0)} g på skjermen. Armen og hengselet frå projektoren er 421 g av det.</p></div>
        <p class="liten graa" style="margin-top: 10px;">A, B, C og D til samanlikning: {k(L['ref-A']['W350'], 1)}, {k(L['over-flik']['W350'], 1)}, {k(L['fot-linse']['W350'], 1)} og {k(L['ref-D']['W350'], 1)} W, jamnheit {k(L['ref-A']['jamnheit'], 2)}, {k(L['over-flik']['jamnheit'], 2)}, {k(L['fot-linse']['jamnheit'], 2)} og {k(L['ref-D']['jamnheit'], 2)}.</p>
      </section>
    </div>
  </main>

  <footer class="botn">
    <span>Under kvar kropp: watt for 350 lx på feltet, jamnheit og lux på veggen bak skjermen. Modell i lysmotoren, mekanikk frå CAD-en. Skjermen er skugge.</span>
    <span>Ingenting er bygt eller målt.</span>
  </footer>
</div>
</body>
</html>
'''


def ark_val(R, L, V):
    a, b_, c = V['a'], V['b'], V['c']
    def kol(bokstav, v):
        l = v['lys']
        return f'''      <div class="val">
        <figure><img src="{v['flis']}" alt=""></figure>
        <p class="stor" style="margin: 6px 0 4px;">({bokstav}) {v['namn']}</p>
        <p class="tal"><em>{k(l['W350'] * 100, 0)} lm · {k(l['W350'], 1)} W · 3000 K · 350 lx · U0 {k(l['jamnheit'], 2)}</em></p>
        <p class="liten">{v['tekst']}</p>
        <p class="m2">{v['mek']}</p>
      </div>'''
    return f'''<!doctype html>
<html lang="nn">
<head>
<meta charset="utf-8">
<title>Kitbash · val</title>
<link rel="stylesheet" href="{CSS}">
<style>
  .studie img {{ display: block; width: 1039px; height: auto; }}
  .studie figcaption {{ display: flex; justify-content: space-between; }}
  .tre {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); column-gap: 24px; margin-top: 12px; }}
  .val figure img {{ width: 120px; height: 120px; display: block; }}
  .val {{ display: grid; grid-template-columns: 120px minmax(0, 1fr); column-gap: 12px; align-items: start; }}
  .val figure {{ grid-row: span 4; }}
  .val .tal {{ font-size: 11.5px; color: var(--graa); margin: 0 0 4px; }}
  .val .liten {{ font-size: 12.5px; line-height: 1.3; margin: 0 0 4px; }}
  .val .m2 {{ font: 400 8.5px/1.35 var(--mono); letter-spacing: 0.04em; text-transform: uppercase; color: var(--graa); margin: 0; }}
</style>
</head>
<body>
<div class="side">
{TOPP % 'Valet (a), (b), (c)'}

  <h1 class="tittel">Lyset er funne. Valet er kven som ber plata: skjermen, bordet eller foten.</h1>

  <main class="innhald" style="display: block;">
    <figure class="studie">
      <img src="{V['studie']}" alt="">
      <figcaption><span><b>Stemning</b> · 1,25 W · 2200 K · vindauget på veggen {k(a['lys']['s_bak'], 0)} lx</span><span><b>Arbeid</b> · {k(a['lys']['W350'], 1)} W · 3000 K · feltet 350 lx · veggen bak {k(a['lys']['bak350'], 0)} lx</span></figcaption>
    </figure>
    <div class="tre">
{kol('a', a)}
{kol('b', b_)}
{kol('c', c)}
    </div>
  </main>

  <footer class="botn">
    <span>Bileta er lysmotoren sitt rom for (a) og (b), same kamera og eksponering. Tala er modell, skalerte til 350 lx på feltet.</span>
    <span>Designaren vel.</span>
  </footer>
</div>
</body>
</html>
'''


def png(namn):
    tmp = tempfile.mkdtemp()
    try:
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', f'--user-data-dir={tmp}',
                        '--force-device-scale-factor=2', '--window-size=1127,797', '--default-background-color=000000ff',
                        '--virtual-time-budget=6000', f'--screenshot={os.path.join(HER, namn + ".png")}',
                        'file:///' + os.path.join(HER, namn + '.html').replace('\\', '/')], capture_output=True, timeout=120)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    R = json.load(open(os.path.join(HER, 'tal.json'), encoding='utf-8'))
    L = json.load(open(os.path.join(HER, 'tal_lys.json'), encoding='utf-8'))
    open(os.path.join(HER, 'ark-brett.html'), 'w', encoding='utf-8').write(ark_brett(R, L)); png('ark-brett')
    vf = os.path.join(HER, 'val.json')
    if os.path.exists(vf):
        V = json.load(open(vf, encoding='utf-8'))
        open(os.path.join(HER, 'ark-val.html'), 'w', encoding='utf-8').write(ark_val(R, L, V)); png('ark-val')
    print('skrive ark')
