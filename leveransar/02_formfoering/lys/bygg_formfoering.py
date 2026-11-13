# -*- coding: utf-8 -*-
"""Byggjer formføringsplansja i to sider: Northern-forma lesen ut av sortimentet, og formføringa for den nye lampa.

Innhaldet kjem frå grunnlag/07-formfoering.md (måla frå produktarka, regeltesten på 18 lamper,
verdiorda og poengskalaen). Silhuettane er skjematiske: primitivane lampa er bygd av, i målestokk.

  python bygg_formfoering.py
"""
import os, sys, math

HER = os.path.dirname(os.path.abspath(__file__))
UT = os.path.normpath(os.path.join(HER, '..'))
NB = '&nbsp;'
KROPP = '#626262'
LYS = '#F4F4F4'


# ------------------------------------------------------------------ silhuettar (cm, x om aksen, y opp frå bordet)
def _r(x, y, w, h, k):
    return ('r', x, y, w, h, k)


def snowball():
    return dict(namn='Snowball oppladbar', aar='2025', h=33, x0=-4.5, x1=4.5, hovud=0.78, delar=[
        _r(-4.5, 0, 9, 2.2, 'k'), _r(-3.0, 2.2, 6, 1.3, 'k'), _r(-0.6, 3.5, 1.2, 22.6, 'k'),
        ('c', 0, 29.5, 3.5, 'l')])


def buddy():
    return dict(namn='Buddy', aar='2016', h=49, x0=-4.25, x1=16, hovud=0.82, delar=[
        _r(-4.25, 0, 8.5, 9, 'k'), ('ror', 1.4), ('kapsel', 6, 42, 10, 7), ('strek', 7.5, 42, 14.5, 42)])


def balancer():
    return dict(namn='Balancer mini', aar='2022', h=19, x0=-3, x1=11.5, hovud=1.5, delar=[
        _r(-3, 0, 6, 18, 'k'), ('halvkule', 7.0, 14.5, 4.5)])


def kin(hf, hg, df, namn):
    return dict(namn=namn, aar='2023', h=hf + hg, x0=-10, x1=10, hovud=round(20 / df, 2), delar=[
        _r(-df / 2, 0, df, hf, 'k'), ('kuppel', 0, hf, 10, hg, 'l')])


def tradition():
    return dict(namn='Tradition', aar='2025', h=39, x0=-14.5, x1=14.5, hovud=2.9, delar=[
        _r(-5, 0, 10, 18, 'k'), ('kuppel', 0, 18, 14.5, 21, 'l')])


LAMPER = [snowball(), buddy(), balancer(), kin(15, 18, 8, 'Kin H33'), kin(23, 17, 8.5, 'Kin H40'), tradition()]


def teikn(L, ax, by, s, glod=True):
    """SVG for éi lampe. ax: aksen i px, by: bordlina i px, s: px per cm."""
    X = lambda x: round(ax + x * s, 2)
    Y = lambda y: round(by - y * s, 2)
    ut = []
    for d in L['delar']:
        t = d[0]
        if t == 'r':
            _, x, y, w, h, k = d
            ut.append(f'<rect x="{X(x)}" y="{Y(y + h)}" width="{round(w * s, 2)}" height="{round(h * s, 2)}" fill="{KROPP if k == "k" else LYS}"/>')
        elif t == 'c':
            _, cx, cy, r, k = d
            if glod:
                ut.append(f'<circle cx="{X(cx)}" cy="{Y(cy)}" r="{round(r * s * 2.6, 2)}" fill="url(#glod)"/>')
            ut.append(f'<circle cx="{X(cx)}" cy="{Y(cy)}" r="{round(r * s, 2)}" fill="{LYS}"/>')
        elif t == 'kuppel':
            _, cx, yb, rx, ry, k = d
            if glod:
                ut.append(f'<ellipse cx="{X(cx)}" cy="{Y(yb + ry * 0.45)}" rx="{round(rx * s * 1.9, 2)}" ry="{round(ry * s * 1.5, 2)}" fill="url(#glod)"/>')
            ut.append(f'<path d="M{X(cx - rx)} {Y(yb)} A{round(rx * s, 2)} {round(ry * s, 2)} 0 0 1 {X(cx + rx)} {Y(yb)} Z" fill="{LYS}"/>')
        elif t == 'halvkule':
            _, cx, cy, r = d
            if glod:
                ut.append(f'<circle cx="{X(cx + r * 0.5)}" cy="{Y(cy)}" r="{round(r * s * 2.2, 2)}" fill="url(#glod)"/>')
            ut.append(f'<path d="M{X(cx)} {Y(cy + r)} A{round(r * s, 2)} {round(r * s, 2)} 0 0 1 {X(cx)} {Y(cy - r)} Z" fill="{LYS}"/>')
            ut.append(f'<path d="M{X(cx)} {Y(cy + r)} A{round(r * s, 2)} {round(r * s, 2)} 0 0 0 {X(cx)} {Y(cy - r)} Z" fill="{KROPP}"/>')
        elif t == 'ror':
            w = d[1]
            p = f'M{X(0)} {Y(9)} L{X(0)} {Y(39.5)} A{round(6 * s, 2)} {round(6 * s, 2)} 0 0 1 {X(6)} {Y(45.5)}'
            ut.append(f'<path d="{p}" fill="none" stroke="{KROPP}" stroke-width="{round(w * s, 2)}" stroke-linecap="butt"/>')
        elif t == 'kapsel':
            _, x, y, w, h = d
            ut.append(f'<rect x="{X(x)}" y="{Y(y + h)}" width="{round(w * s, 2)}" height="{round(h * s, 2)}" rx="{round(h * s / 2, 2)}" fill="{KROPP}"/>')
        elif t == 'strek':
            _, x1, y1, x2, y2 = d
            if glod:
                ut.append(f'<ellipse cx="{X((x1 + x2) / 2)}" cy="{Y(y1) + 2}" rx="{round((x2 - x1) * s * 0.9, 2)}" ry="{round(3 * s, 2)}" fill="url(#glod)"/>')
            ut.append(f'<line x1="{X(x1)}" y1="{Y(y1)}" x2="{X(x2)}" y2="{Y(y2)}" stroke="{LYS}" stroke-width="{round(max(1.2, 0.5 * s), 2)}"/>')
    return '\n        '.join(ut)


DEFS = '''<defs>
          <radialGradient id="glod"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.20"/><stop offset="0.45" stop-color="#FFFFFF" stop-opacity="0.07"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>
          <radialGradient id="mjuk"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.95"/><stop offset="0.55" stop-color="#FFFFFF" stop-opacity="0.45"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>
        </defs>'''


# ------------------------------------------------------------------ side 8: sortimentet
def silhuettrad():
    s = 4.6; by = 262; W = 1039
    g = [DEFS]
    # linjal: 0 til 55 cm
    lx = 18
    g.append(f'<line x1="{lx}" y1="{by}" x2="{lx}" y2="{by - 55 * s}" class="haar"/>')
    for cm in range(0, 56, 10):
        g.append(f'<line x1="{lx - 4}" y1="{by - cm * s}" x2="{lx}" y2="{by - cm * s}" class="strek"/>')
        g.append(f'<text x="{lx - 7}" y="{by - cm * s + 3}" class="graa" text-anchor="end">{cm}</text>')
    g.append(f'<line x1="{lx + 3}" y1="{by - 27 * s}" x2="{lx + 3}" y2="{by - 55 * s}" stroke="#F4F4F4" stroke-width="3"/>')
    g.append(f'<text transform="translate({lx + 15},{by - 41 * s}) rotate(-90)" class="graa" text-anchor="middle">27 til 55{NB}cm: bordlampene</text>')
    g.append(f'<text x="{lx - 7}" y="{by + 16}" class="graa" text-anchor="end">cm</text>')
    # bordline
    g.append(f'<line x1="{lx}" y1="{by}" x2="{W}" y2="{by}" stroke="#8E8E8E" stroke-width="1"/>')
    # plasser lampene
    total = sum((L['x1'] - L['x0']) * s for L in LAMPER)
    start, slutt = 130, W - 8
    gap = (slutt - start - total) / (len(LAMPER) - 1)
    x = start
    kantar = []
    for i, L in enumerate(LAMPER):
        ax = x - L['x0'] * s
        g.append(teikn(L, ax, by, s))
        midt = x + (L['x1'] - L['x0']) * s / 2
        kantar.append((x, x + (L['x1'] - L['x0']) * s))
        g.append(f'<text x="{midt:.1f}" y="{by + 18}" class="kv" text-anchor="middle">{L["namn"].upper()}</text>')
        g.append(f'<text x="{midt:.1f}" y="{by + 31}" class="graa" text-anchor="middle">{L["aar"]} · H {L["h"]}{NB}cm</text>')
        g.append(f'<text x="{midt:.1f}" y="{by + 44}" class="graa" text-anchor="middle">hovud/fot {str(L["hovud"]).replace(".", ",")}</text>')
        x += (L['x1'] - L['x0']) * s + gap
    for a_, b_, t in ((0, 1, 'SLANK TYPE · hovudet ein femdel av høgda'), (2, 2, 'IMELLOM'), (3, 5, 'HATTETYPEN · hovudet om lag halve høgda')):
        m = (kantar[a_][0] + kantar[b_][1]) / 2
        g.append(f'<text x="{m:.1f}" y="12" class="graa" text-anchor="middle">{t}</text>')
        g.append(f'<line x1="{kantar[a_][0]:.1f}" y1="18" x2="{kantar[b_][1]:.1f}" y2="18" class="haar"/>')
    return f'<svg width="{W}" height="{by + 50}" viewBox="0 0 {W} {by + 50}" xmlns="http://www.w3.org/2000/svg">\n        ' + '\n        '.join(g) + '\n      </svg>'


def proporsjonsrom():
    W, H = 500, 268
    x0, x1, y0, y1 = 44, W - 8, 232, 22
    X = lambda v: round(x0 + v / 3.2 * (x1 - x0), 1)
    Y = lambda v: round(y0 - v / 60 * (y0 - y1), 1)
    g = []
    g.append(f'<rect x="{X(1.0)}" y="{y1}" width="{X(2.3) - X(1.0)}" height="{y0 - y1}" class="lysflate"/>')
    g.append(f'<text x="{X(1.65)}" y="{y1 + 14}" class="kv" text-anchor="middle">OPE</text>')
    g.append(f'<text x="{X(1.65)}" y="{y1 + 27}" class="graa" text-anchor="middle">berre Balancer mini</text>')
    g.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" class="strek"/>')
    g.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" class="strek"/>')
    for v in (0, 0.5, 1, 1.5, 2, 2.5, 3):
        g.append(f'<line x1="{X(v)}" y1="{y0}" x2="{X(v)}" y2="{y0 + 4}" class="strek"/>')
        g.append(f'<text x="{X(v)}" y="{y0 + 16}" class="graa" text-anchor="middle">{str(v).replace(".", ",").replace(",0", "")}</text>')
    for v in (0, 20, 40, 60):
        g.append(f'<line x1="{x0 - 4}" y1="{Y(v)}" x2="{x0}" y2="{Y(v)}" class="strek"/>')
        g.append(f'<text x="{x0 - 7}" y="{Y(v) + 3}" class="graa" text-anchor="end">{v}{NB}%</text>')
    g.append(f'<text x="{x1}" y="{y0 + 32}" class="graa" text-anchor="end">LYSHOVUDET GONGER FOTEN</text>')
    g.append(f'<text x="0" y="10" class="graa">LYSHOVUDET, DEL AV HØGDA</text>')
    pkt = [(0.78, 21, True), (0.82, 20, True), (0.70, 18, False), (0.75, 21, False), (1.5, 47, True), (2.35, 43, True), (2.5, 55, True), (2.9, 54, True)]
    for v, h, fylt in pkt:
        k = 'fyll' if fylt else 'opn'
        g.append(f'<circle cx="{X(v)}" cy="{Y(h)}" r="4" class="{k}"/>')
    g.append(f'<text x="{X(0.9) + 10}" y="{Y(22) - 4}" class="kv">Snowball oppladbar, Buddy,</text>')
    g.append(f'<text x="{X(0.9) + 10}" y="{Y(22) + 9}" class="kv">Snowball, Salto</text>')
    g.append(f'<text x="{X(0.9) + 10}" y="{Y(22) + 22}" class="graa">les som arbeidslampe</text>')
    g.append(f'<text x="{X(1.5) + 9}" y="{Y(47) + 3}" class="kv">Balancer mini</text>')
    g.append(f'<text x="{X(2.35) - 9}" y="{Y(43) + 3}" class="kv" text-anchor="end">Kin H40</text>')
    g.append(f'<text x="{X(2.5) - 9}" y="{Y(55) + 3}" class="kv" text-anchor="end">Kin H33</text>')
    g.append(f'<text x="{X(2.9)}" y="{Y(54) + 18}" class="kv" text-anchor="middle">Tradition</text>')
    g.append(f'<text x="{X(2.62)}" y="{Y(43) + 24}" class="graa" text-anchor="middle">les som stemningslampe</text>')
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">\n        ' + '\n        '.join(g) + '\n      </svg>'


# Regeltesten frå grunnlag/07, del 3. H: held, D: delvis, B: broten, -: gjeld ikkje. Sortert etter år.
TEST = [
    ('Birdy', 1952, 'DDDDBB'), ('Birdy swing', 1952, 'HDDDBH'), ('Dokka', 1954, 'H-DHDB'), ('Hall', 1955, 'H-HHBB'),
    ('Snowball', 2005, 'HHHHBB'), ('Oslo Wood', 2006, 'HHHDBB'), ('Buddy', 2016, 'HHDHBH'), ('Gear', 2018, 'DBDHBH'),
    ('Me dim', 2018, 'HHHHHD'), ('Blush', 2018, 'HHHHDH'), ('Ombre', 2019, 'DDHHBD'), ('Salto', 2022, 'HHHHHD'),
    ('Balancer mini', 2022, 'HBHHHH'), ('Archive', 2023, 'HBHBHB'), ('Kin', 2023, 'HBHDBB'), ('Snowball opp.', 2025, 'HHHHHB'),
    ('Tradition', 2025, 'HBHHHB'), ('Glint', 2025, 'H-HHDB'),
]
REGLAR = [('H1', 'høgst tre primærformer', 'R1 kjerne'), ('H2', 'tynn line ber hovudet', 'R2 retta'), ('H3', 'lyskjelda aldri naken', 'R3 kjerne'),
          ('H4', 'éin matt farge', 'R4 retta'), ('H5', 'messingpunkt betjener', 'R5 frå 2022'), ('H6', 'handlinga gjev namn', 'forkasta')]


def regelrutenett():
    c, gap = 13, 3
    x0, y0 = 150, 22
    g = []
    for r, (kode, tekst, dom) in enumerate(REGLAR):
        y = y0 + r * (c + 7)
        kl = 'graa' if dom == 'forkasta' else 'kv'
        g.append(f'<text x="0" y="{y + 11}" class="{kl}">{kode} {tekst}</text>')
        for i, (_, _, v) in enumerate(TEST):
            x = x0 + i * (c + gap)
            t = v[r]
            if t == 'H':
                g.append(f'<rect x="{x}" y="{y}" width="{c}" height="{c}" fill="#F4F4F4"/>')
            elif t == 'D':
                g.append(f'<rect x="{x}" y="{y}" width="{c}" height="{c}" fill="#6A6A6A"/>')
            elif t == 'B':
                g.append(f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{c - 1}" height="{c - 1}" fill="none" stroke="#5A5A5A"/>')
            else:
                g.append(f'<circle cx="{x + c / 2}" cy="{y + c / 2}" r="1.3" fill="#5A5A5A"/>')
        xd = x0 + len(TEST) * (c + gap) + 6
        g.append(f'<text x="{xd}" y="{y + 11}" class="{kl}">{dom}</text>')
    yb = y0 + len(REGLAR) * (c + 7) + 2
    # skilje ved 2022
    i22 = next(i for i, t in enumerate(TEST) if t[1] >= 2022)
    xs = x0 + i22 * (c + gap) - gap / 2 - 0.5
    g.append(f'<line x1="{xs}" y1="{y0 - 6}" x2="{xs}" y2="{yb + 2}" stroke="#F4F4F4" stroke-width="1" stroke-dasharray="2 3"/>')
    g.append(f'<text x="{xs + 4}" y="{y0 - 8}" class="kv">frå 2022</text>')
    for i, (namn, aar, _) in enumerate(TEST):
        x = x0 + i * (c + gap) + c / 2 + 3
        g.append(f'<text transform="translate({x},{yb + 6}) rotate(-90)" class="graa" text-anchor="end">{namn}</text>')
    H = yb + 80
    W = xd + 76
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">\n        ' + '\n        '.join(g) + '\n      </svg>'


STIL = '''  svg .kv { fill: var(--blekk); }
  svg .stort { font-family: var(--serif); font-size: 40px; fill: var(--blekk); }
  svg .opn { fill: #000; stroke: var(--blekk); stroke-width: 1; }
  .forklaring { font: 400 10px/1.45 var(--mono); color: var(--graa); letter-spacing: 0.03em; margin-top: 6px; }
  .forklaring b { color: var(--blekk); font-weight: 400; }'''


def side(fil, nr, namn, tittel, stil, innhald, kjelder, merknad):
    html = ('<!doctype html>\n<html lang="nn">\n<head>\n<meta charset="utf-8">\n<title>' + nr + ' · ' + namn + '</title>\n'
            '<link rel="stylesheet" href="../01_fase1_v2/felles.css">\n<style>\n' + stil + '\n</style>\n</head>\n<body>\n<div class="side">\n'
            '  <header class="topp">\n    <span>GK5 · Northern · fase 2</span>\n    <span>' + nr + ' · ' + namn + '</span>\n'
            '    <span>Iver R. Finne · 17.11.2026</span>\n  </header>\n\n'
            '  <h1 class="tittel">' + tittel + '</h1>\n\n  <main class="innhald">\n' + innhald + '\n  </main>\n\n'
            '  <footer class="botn">\n    <span>' + kjelder + '</span>\n    <span>' + merknad + '</span>\n  </footer>\n</div>\n</body>\n</html>\n')
    open(os.path.join(UT, fil), 'w', encoding='utf-8', newline='\n').write(html)
    print('skrive', fil)


def side8():
    innhald = f'''    <figure class="k12">
      {silhuettrad()}
    </figure>

    <figure class="k6">
      {proporsjonsrom()}
      <p class="forklaring">Fylt: mål frå produktarket. Ope: målt i produktbilete. <b>Mi tolking:</b> ei lampe som skal vere både arbeidslampe og stemningslampe, kan bu i holet mellom dei to typane.</p>
    </figure>

    <figure class="k6">
      <p class="etikett">Seks hypotesar prøvde på 18 lamper</p>
      {regelrutenett()}
      <p class="forklaring">Kvit: held. Grå: delvis. Open: broten. Prikk: gjeld ikkje. Kjernen er R1 til R4. R2 er retta til at det som ber, har konstant tverrsnitt, og R4 til at kontrast berre kjem frå materialskifte.</p>
    </figure>'''
    stil = STIL + '''
  .innhald { row-gap: 8px; }'''
    side('side-8-formfoering-sortiment.html', '08', 'Formføringsplansje 1/2',
         'Fire reglar ber attkjenninga. Silhuetten og handlinga er fri.', stil, innhald,
         'Mål frå produktarka til Northern, lesne 12.11.2026. Regeltesten er gjord i produktbilete, ikkje på fysiske lamper.',
         'Silhuettane er skjematiske.')


# ------------------------------------------------------------------ side 9: den nye lampa
def skala():
    """Poenga til Northern sine eigne bordlamper som fire kolonnar (4 til 7), med sona 5 til 6 merkt."""
    W, H = 1039, 216
    s = 2.3
    by = 158
    bredd = [180, 180, 380, 281]
    x0 = [0]
    for w in bredd[:-1]:
        x0.append(x0[-1] + w + 6)
    lamp = {L['namn']: L for L in LAMPER}
    innhald = {4: [('tekst', 'Gear', 'R1, R5 og høgda trekkjer ned')],
               5: [('tekst', 'Archive', 'to fargar, platefot')],
               6: [('lampe', 'Balancer mini'), ('lampe', 'Kin H33'), ('lampe', 'Buddy'), ('tekst', 'Salto', '6 til 7, mål manglar')],
               7: [('lampe', 'Snowball oppladbar'), ('lampe', 'Tradition')]}
    g = [DEFS]
    g.append(f'<rect x="{x0[1]}" y="0" width="{x0[2] + bredd[2] - x0[1]}" height="{by + 34}" class="lysflate"/>')
    g.append(f'<text x="{x0[1] + 8}" y="16" class="kv">KJEND, MEN NY · sona briefen ber om (mi tolking)</text>')
    for k, p in enumerate((4, 5, 6, 7)):
        xa = x0[k]
        g.append(f'<text x="{xa + 8}" y="62" class="stort">{p}</text>')
        g.append(f'<line x1="{xa}" y1="{by}" x2="{xa + bredd[k]}" y2="{by}" class="strek"/>')
        slots = []
        for e in innhald[p]:
            if e[0] == 'lampe':
                L = lamp[e[1]]
                bw = (L['x1'] - L['x0']) * s
                slots.append((max(bw, len(e[1]) * 5.75) + 18, e, bw))
            else:
                slots.append((max(len(e[1]), len(e[2])) * 5.75 + 18, e, 0))
        x = xa + bredd[k] - sum(w for w, _, _ in slots) - 4
        for w, e, bw in slots:
            m = x + w / 2
            if e[0] == 'lampe':
                L = lamp[e[1]]
                ax = m - bw / 2 - L['x0'] * s
                g.append(teikn(L, ax, by, s))
                g.append(f'<text x="{m:.1f}" y="{by + 15}" class="kv" text-anchor="middle">{e[1]}</text>')
            else:
                g.append(f'<circle cx="{m:.1f}" cy="{by}" r="3.5" class="fyll"/>')
                g.append(f'<text x="{m:.1f}" y="{by + 15}" class="kv" text-anchor="middle">{e[1]}</text>')
                g.append(f'<text x="{m:.1f}" y="{by + 28}" class="graa" text-anchor="middle">{e[2]}</text>')
            x += w
    g.append(f'<text x="0" y="{H - 3}" class="graa">← ENDRING · poeng: reglane R1 til R5 (0 til 5), paletten (0 eller 1), proporsjonane (0 eller 1) · ATTKJENNING →</text>')
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">\n        ' + '\n        '.join(g) + '\n      </svg>'


KELVIN = {2200: '#FF932C', 2700: '#FFA757', 3000: '#FFB46B', 4000: '#FFD1A3'}


def piktogram(kva):
    W, H = 300, 92
    g = [DEFS]
    if kva == 'varm':
        g.append('<defs>' + ''.join(f'<radialGradient id="k{k}"><stop offset="0" stop-color="{c}" stop-opacity="0.9"/><stop offset="0.4" stop-color="{c}" stop-opacity="0.35"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>' for k, c in KELVIN.items()) + '</defs>')
        for i, k in enumerate((2200, 2700, 3000, 4000)):
            cx = 38 + i * 74
            op = '' if k < 4000 else ' opacity="0.45"'
            g.append(f'<circle cx="{cx}" cy="38" r="30" fill="url(#k{k})"{op}/>')
            g.append(f'<circle cx="{cx}" cy="38" r="7" fill="{KELVIN[k]}"{op}/>')
            g.append(f'<text x="{cx}" y="86" class="{"kv" if k < 4000 else "graa"}" text-anchor="middle">{k}{NB}K</text>')
        g.append(f'<line x1="{38 + 3 * 74 - 24}" y1="62" x2="{38 + 3 * 74 + 24}" y2="14" class="strek"/>')
    elif kva == 'mjuk':
        g.append('<line x1="0" y1="60" x2="300" y2="60" stroke="#5A5A5A"/>')
        g.append('<ellipse cx="78" cy="60" rx="70" ry="13" fill="url(#mjuk)"/>')
        g.append('<ellipse cx="226" cy="60" rx="46" ry="9" fill="#F4F4F4"/>')
        g.append('<line x1="186" y1="80" x2="266" y2="38" class="strek"/>')
        g.append('<text x="78" y="88" class="kv" text-anchor="middle">mjuk kant</text>')
        g.append('<text x="226" y="88" class="graa" text-anchor="middle">skarp kant</text>')
    elif kva == 'enkel':
        b = 72
        g.append(f'<line x1="0" y1="{b}" x2="300" y2="{b}" stroke="#5A5A5A"/>')
        g.append(f'<rect x="56" y="{b - 7}" width="40" height="7" fill="{KROPP}"/><rect x="74" y="{b - 52}" width="4" height="45" fill="{KROPP}"/><circle cx="76" cy="{b - 60}" r="11" fill="{LYS}"/>')
        g.append(f'<text x="76" y="{b + 16}" class="kv" text-anchor="middle">tre former</text>')
        g.append(f'<rect x="196" y="{b - 6}" width="34" height="6" fill="{KROPP}"/><line x1="213" y1="{b - 6}" x2="203" y2="{b - 36}" stroke="{KROPP}" stroke-width="3"/>'
                 f'<circle cx="203" cy="{b - 38}" r="4" fill="{KROPP}"/><line x1="203" y1="{b - 38}" x2="236" y2="{b - 58}" stroke="{KROPP}" stroke-width="3"/>'
                 f'<circle cx="236" cy="{b - 58}" r="4" fill="{KROPP}"/><path d="M230 {b - 60} L256 {b - 48} L248 {b - 34} Z" fill="{KROPP}"/><circle cx="222" cy="{b - 18}" r="3" fill="#8E8E8E"/>')
        g.append(f'<line x1="186" y1="{b + 2}" x2="266" y2="{b - 66}" class="strek"/>')
        g.append(f'<text x="226" y="{b + 16}" class="graa" text-anchor="middle">ledd og overgangar</text>')
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">\n          ' + '\n          '.join(g) + '\n        </svg>'


def side9():
    ord_ = [('varm', 'VARM', 'Lys frå 2200 til 3000' + NB + 'K som blir varmare når det blir dempa. Éin lakkfarge og eitt messingpunkt.',
             'Lys over 3000' + NB + 'K, blank kvit plast, mekanikk som motiv.'),
            ('mjuk', 'MJUK', 'Diffust eller reflektert lys utan skarp kant. Krumma kontur på lyshovudet.',
             'Fasettar, synleg lyskjelde, blank lakk på store flater.'),
            ('enkel', 'ENKEL', 'Høgst tre primærformer. Det som ber, har konstant tverrsnitt. Éi betjening.',
             'Eit fjerde formelement, ledd og overgangar, fleire knappar.')]
    kol = []
    for k, namn, tyder, utelukkar in ord_:
        kol.append(f'''      <section class="k4 ord">
        <p class="verdiord">{namn}</p>
        {piktogram(k)}
        <p class="tyder">{tyder}</p>
        <p class="ute"><span class="etikett">Utelukkar</span> {utelukkar}</p>
      </section>''')
    innhald = f'''    <figure class="k12">
      <p class="etikett">Endring og attkjenning: Northern sine eigne bordlamper</p>
      {skala()}
    </figure>

{chr(10).join(kol)}

    <section class="k3 liste"><p class="etikett">Må haldast</p>
      <ul class="rad"><li>Høgst tre primærformer, og eit bereelement med konstant tverrsnitt.</li><li>Inga lyskjelde synleg frå 47{NB}cm over bordet. Sløkt lysflate er opalkvit og matt.</li><li>Éin lakkfarge. Kontrast berre ved materialskifte.</li><li>Eitt lite, rundt messingpunkt der handa alt er.</li></ul></section>
    <section class="k3 liste"><p class="etikett">Kan vere nytt</p>
      <ul class="rad"><li>Silhuetten: lyshovud mellom 1 og 2,3 gonger foten.</li><li>Lyset: to modusar, og meir lys på batteri enn Snowball sine 158{NB}lm.</li><li>Handlinga som skiftar modus, og ei synleg opning for batteri og lysmodul.</li></ul></section>
    <section class="k3 liste"><p class="etikett">Aldri</p>
      <ul class="rad"><li>Synlege dioder, LED-ring eller lysstripe.</li><li>Hardplast som synleg hovudmateriale, eller ein andre lakkfarge.</li><li>Meir enn éi elektrisk betjening, eller ein skjerm.</li></ul></section>
    <section class="k3 liste"><p class="etikett">Til formlæraren</p>
      <ul class="rad graa"><li>Gjeld plansja alle tre konsepta før valet 18.11?</li><li>Skal ho ha tre verdiord?</li><li>Kan eit konsept bryte ein kjerneregel med vilje når brotet er grunngjeve?</li><li>Kva format og storleik?</li></ul></section>'''
    stil = STIL + '''
  .innhald { row-gap: 10px; }
  .ord svg { margin: 2px 0 4px; }
  .verdiord { font: 400 26px/1 var(--serif); color: var(--blekk); letter-spacing: 0.04em; margin: 0 0 4px; }
  .tyder { font-size: 13.5px; line-height: 1.32; color: var(--blekk); margin: 0 0 4px; }
  .ute { font-size: 13px; line-height: 1.32; color: var(--graa); }
  .ute .etikett { display: inline; margin-right: 4px; }
  ul.rad { list-style: none; margin: 0; padding: 0; }
  ul.rad li { font-size: 12.5px; line-height: 1.3; padding: 4px 0 5px; border-top: 1px solid var(--linje); }
  ul.rad.graa li { color: var(--graa); }'''
    side('side-9-formfoering-ny-lampe.html', '09', 'Formføringsplansje 2/2',
         'Den nye lampa held kjernen og er ny i silhuett, lys og handling.', stil, innhald,
         'Verdiorda er Northern sine eigne (varm i 28, mjuk i 22 av 56 lampetekstar). Poenga er rekna frå regeltesten og måla i produktarka.',
         'Formatet er ikkje fastsett i kursmaterialet.')


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    side8()
    side9()
