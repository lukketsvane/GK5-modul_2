# -*- coding: utf-8 -*-
"""Byggjepakke for dei tre skissemodellane til konseptgjennomgangen 18.11, runde 2 av konsepta.

Lagar to PDF-ar i målestokk 1:1 (alle mål i SVG-einingar er millimeter):
  byggjepakke-A4.pdf   heile pakken: rekkjefølgje, målearket for lobebreidda, malar og mål for A, B og C
  malar-A3.pdf         målekortet til 24 cm og heile skiva til A
og ribbe_R1200_250mm.stl til 3D-printaren.

Geometrien for runde 2 kjem frå modellkoden via hent_geometri.py (runde2.json, maske_C.npz).
Tekstane byggjer på konsept/tre/00-tre-konsept.md og på kontrollen av første utgåva av pakken.

  python hent_geometri.py      når konsepta endrar seg
  python lag_byggjepakke.py
"""
import os, sys, math, struct, subprocess, tempfile, json, base64, io
import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
FONT = '../01_fase1_sider/fonts/EBGaramond12-Regular.otf'
G = json.load(open(os.path.join(HER, 'runde2.json'), encoding='utf-8'))

# ------------------------------------------------------------------ mål
R_SKIVE = 1200.0          # mm, kuv boge (spegel-kuv-1.2)
D_SKIVE = 250.0
PIL = R_SKIVE - math.sqrt(R_SKIVE ** 2 - (D_SKIVE / 2) ** 2)      # 6,5 mm
T_RIBBE = 6.0
H_RIBBE = 6.0
ROER_D = 25.0
OVERLAPP = 8.0
ROER_A = (ROER_D / 2) / math.tan(math.radians(20))                # 34 mm: kutt ved 20° (sigma 10°)
ROER_FLIK = (ROER_D / 2) / math.tan(math.radians(G['A']['lykt2_kutt']))   # 71 mm: kutt ved 10° (sigma 5°)
ROER_FLIK_15 = 7.5 / math.tan(math.radians(G['A']['lykt2_kutt']))          # 43 mm: same kutt med ei lita lommelykt Ø 15
ROER_MOTE = (ROER_D / 2) / math.tan(math.radians(36))                       # 17 mm: møte, kjelde 18° (kutt 2 sigma), konsept/tre/f10.md
BRONN_H = (ROER_D / 2) / math.tan(math.radians(50))               # 10,5 mm: avskjerming ved 50°
ARM = 135.0


def k(x, d=1):
    return f'{x:.{d}f}'.replace('.', ',')


# ------------------------------------------------------------------ STL for ribba
def ribbe_profil(n=101):
    xs = np.linspace(-D_SKIVE / 2, D_SKIVE / 2, n)
    d = R_SKIVE - np.sqrt(R_SKIVE ** 2 - xs ** 2)
    return xs, T_RIBBE + (PIL - d)


def skriv_stl(fil):
    xs, fr = ribbe_profil()
    tri = []
    def q(a, b, c, d):
        tri.append((a, b, c)); tri.append((a, c, d))
    for i in range(len(xs) - 1):
        x0, x1 = xs[i], xs[i + 1]
        q((x0, 0, H_RIBBE), (x1, 0, H_RIBBE), (x1, fr[i + 1], H_RIBBE), (x0, fr[i], H_RIBBE))
        q((x0, 0, 0), (x0, fr[i], 0), (x1, fr[i + 1], 0), (x1, 0, 0))
        q((x0, 0, 0), (x1, 0, 0), (x1, 0, H_RIBBE), (x0, 0, H_RIBBE))
        q((x0, fr[i], 0), (x0, fr[i], H_RIBBE), (x1, fr[i + 1], H_RIBBE), (x1, fr[i + 1], 0))
    q((xs[0], 0, 0), (xs[0], 0, H_RIBBE), (xs[0], fr[0], H_RIBBE), (xs[0], fr[0], 0))
    q((xs[-1], 0, 0), (xs[-1], fr[-1], 0), (xs[-1], fr[-1], H_RIBBE), (xs[-1], 0, H_RIBBE))
    with open(fil, 'wb') as fh:
        fh.write(b'ribbe R1200 boge 250 mm, GK5 skissemodell A'.ljust(80, b' '))
        fh.write(struct.pack('<I', len(tri)))
        for a, b, c in tri:
            a, b, c = (np.asarray(v, float) for v in (a, b, c))
            nv = np.cross(b - a, c - a); L = np.linalg.norm(nv); nv = nv / L if L else nv
            fh.write(struct.pack('<12fH', *nv, *a, *b, *c, 0))
    return len(tri)


# ------------------------------------------------------------------ SVG-hjelparar (mm)
def t(x, y, s, kl='', anker='start'):
    return f'<text x="{x:.2f}" y="{y:.2f}" class="{kl}" text-anchor="{anker}">{s}</text>'


def tekstblokk(x, y, liner, kl='', lh=4.6):
    return ''.join(t(x, y + i * lh, s, kl) for i, s in enumerate(liner))


def ramme(W, H, tittel, nr, total):
    m = 12
    g = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>']
    g.append(t(m, m, 'GK5 · NORTHERN · BYGGJEPAKKE · RUNDE 2', 'mono'))
    g.append(t(W / 2, m, tittel.upper(), 'mono svart', 'middle'))
    g.append(t(W - m, m, 'IVER R. FINNE · 13.11.2026', 'mono', 'end'))
    g.append(f'<line x1="{m}" y1="{m + 2.5}" x2="{W - m}" y2="{m + 2.5}" class="strek"/>')
    yb = H - m
    g.append(f'<line x1="{m}" y1="{yb - 6}" x2="{W - m}" y2="{yb - 6}" class="haar"/>')
    g.append(t(m, yb, 'Skriv ut i faktisk storleik (100 %), ikkje «tilpass til side». Kontrollstrek 100 mm:', 'mono'))
    x0 = m + 152
    g.append(f'<line x1="{x0}" y1="{yb - 1.2}" x2="{x0 + 100}" y2="{yb - 1.2}" stroke="#000" stroke-width="0.35"/>')
    for x in (x0, x0 + 100):
        g.append(f'<line x1="{x}" y1="{yb - 3.4}" x2="{x}" y2="{yb + 1}" stroke="#000" stroke-width="0.35"/>')
    for i in range(1, 10):
        g.append(f'<line x1="{x0 + 10 * i}" y1="{yb - 2.4}" x2="{x0 + 10 * i}" y2="{yb - 1.2}" stroke="#000" stroke-width="0.2"/>')
    g.append(t(W - m, yb, f'side {nr} av {total}', 'mono', 'end'))
    return ''.join(g)


def side_svg(W, H, innhald, tittel, nr, total):
    return (f'<section class="ark" style="width:{W}mm;height:{H}mm"><svg width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}" '
            f'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">{ramme(W, H, tittel, nr, total)}{innhald}</svg></section>')


def kutt(path_d):
    return f'<path d="{path_d}" class="kutt"/>'


def fald(x1, y1, x2, y2):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" class="fald"/>'


def rekt(x, y, w, h, kl='kutt'):
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" class="{kl}"/>'


def maallinje(x1, y1, x2, y2, tekst, side=1, vassrett=False):
    g = [f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" class="maal"/>']
    dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    for (x, y) in ((x1, y1), (x2, y2)):
        g.append(f'<line x1="{x - 1.6 * nx:.2f}" y1="{y - 1.6 * ny:.2f}" x2="{x + 1.6 * nx:.2f}" y2="{y + 1.6 * ny:.2f}" class="maal"/>')
    mx, my = (x1 + x2) / 2 + side * 3.2 * nx, (y1 + y2) / 2 + side * 3.2 * ny
    if vassrett:
        g.append(t(mx + (2 if side > 0 else -2), my + 1, tekst, 'mono', 'start' if side > 0 else 'end'))
    else:
        ang = math.degrees(math.atan2(dy, dx))
        if ang > 90 or ang < -90: ang += 180
        g.append(f'<text transform="translate({mx:.2f},{my + 1:.2f}) rotate({ang:.1f})" class="mono" text-anchor="middle">{tekst}</text>')
    return ''.join(g)


def roernett(ox, oy, L, tekst):
    """Strimmel som blir rulla til eit røyr Ø 25 mm. Lengda L langs røyret (loddrett på arket)."""
    w = math.pi * ROER_D + OVERLAPP
    g = [rekt(ox, oy, w, L), fald(ox + w - OVERLAPP, oy, ox + w - OVERLAPP, oy + L)]
    g.append(maallinje(ox, oy + L + 4, ox + w, oy + L + 4, f'{k(w)} mm'))
    g.append(maallinje(ox - 4, oy, ox - 4, oy + L, '', side=-1, vassrett=True))
    g.append(t(ox - 6.5, oy + L / 2 + 1, f'{k(L)} mm', 'mono', 'end'))
    g.append(tekstblokk(ox, oy - 3.7 - 3.8 * (len(tekst) - 1), tekst, 'mono', lh=3.8))
    return ''.join(g)


# ------------------------------------------------------------------ sidene
def s_oversikt(W, H):
    m = 12
    kol = [
        ('A SKIVA', 'vipp skiva',
         ['stolpen frå overheadprojektoren', 'reflektorfilm frå LCD-skjermen, om du har', 'ribba (3D-print, STL i mappa)'],
         ['skive Ø 250 mm: glatt folie, kvit og matt bakside', 'veggflik 12 × 8,4 cm, folie og bakepapir',
          'papplist som held fliken ved sida av stolpen', 'arm 13,5 cm med ledd',
          f'to svarte papprull: {k(ROER_A, 0)} og {k(ROER_FLIK, 0)} mm lange', 'to lykter i foten']),
        ('B OVER', 'vipp plata',
         ['fresnelplata 285 × 285 mm', 'stolpen frå overheadprojektoren', 'to diffusorark'],
         ['pappramme, tappar midt på sidekantane', 'stag med merke for stemning og arbeid', 'flik 60 mm, blank folie på papp',
          'brønn: svart krage Ø 25 × 10,5 mm', 'kloss 9 cm på skjermkanten']),
        ('C VINDAUGE', 'skyv spegelen inn',
         ['frontflatespegelen frå projektorhovudet', 'stolpen frå overheadprojektoren'],
         ['julekule av glas Ø 70 mm, fylt med vatn (kjøp)', 'kredittkort-fresnel 85 × 55 mm (kjøp)', 'maske og gråfilter (side 10)',
          'pappflik for spegelen, 65 % av strålen', 'lekt eller kloss: hovudet 70 cm opp']),
    ]
    g = [t(m, 28, 'Tre skissemodellar til konseptgjennomgangen 18.11', 'tittel')]
    g.append(t(m, 35, 'Runde 2: alle tre held veggen bak skjermen lys i arbeid. Kvar modell syner lyset i rommet, ikkje forma.', 'ingress'))
    bw = (W - 2 * m - 2 * 8) / 3
    for i, (namn, gest, kit, lag) in enumerate(kol):
        x = m + i * (bw + 8); y = 46
        g.append(t(x, y, namn, 'mono svart'))
        g.append(t(x, y + 6, gest + '.', 'kursiv'))
        g.append(t(x, y + 14, 'FRÅ BYGGJESETTET', 'mono'))
        g.append(tekstblokk(x, y + 19.5, ['· ' + s for s in kit], 'brod', lh=4.4))
        y2 = y + 21 + 4.4 * len(kit) + 2
        g.append(t(x, y2, 'LAG ELLER SKAFF', 'mono'))
        g.append(tekstblokk(x, y2 + 5.5, ['· ' + s for s in lag], 'brod', lh=4.4))
    y = 128
    g.append(f'<line x1="{m}" y1="{y - 6}" x2="{W - m}" y2="{y - 6}" class="haar"/>')
    g.append(t(m, y, 'REKKJEFØLGJE', 'mono'))
    rek = ['1  Start 3D-printen av ribba til A. Ho printar medan du gjer resten.',
           '2  Mål lobebreidda (side 2 og 3). A krev under 4,5°. Send tala før du byggjer A.',
           '3  Byggj éin modell om gongen: det finst berre éin stolpe.',
           '     Han når 30 til 40 cm. B treng 62 cm og C 70 cm: set han på ein kloss eller ei lekt.',
           '4  B først, så A når ribba er ferdig, så C.',
           '5  Fotografer etter fotolista. Kameraet er ein annan telefon enn lykta.',
           '6  Vipp og skyv med to fingrar eller i leddet, ikkje med eit dytt. Eit dytt veltar',
           '     alle tre, og det same gjeld produktet: handlinga må vere eit kraftpar.']
    g.append(tekstblokk(m, y + 6, rek, 'brod', lh=4.4))
    x = m + (W - 2 * m) * 0.54
    g.append(t(x, y, 'TRYGGLEIK', 'mono'))
    tr = ['Projektoren: dra ut støpselet og klipp det av eller merk det før du fjernar leidningane.',
          'Fresnelplata, blanke hole former og vasskula samlar sollys og kan tenne papp.',
          '     Aldri i sol eller ved vindauge. Lagre dei tildekte.',
          'Julekula er tynt glas: fyll ho over ei skål med hanskar, tett opninga,',
          '     hald vatn borte frå telefonen og lykta.',
          'Frontflatespegelen: rør ikkje flata, teip berre på baksida og kantane.',
          '     Kantane kan vere uslipte. Teip dei.',
          'Skiva i A: vend ho alltid med spegelsida mot skjermen. Går spegelsida',
          '     forbi andletet ditt, kastar ho lyset frå lykta rett i auga.']
    g.append(tekstblokk(x, y + 6, tr, 'brod', lh=4.4))
    g.append(t(m, H - 23, 'Måla og vinklane er rekna frå lysmodellen i konsept/tre (runde 2). Modellen er ikkje målt: sikt etter lysflekken, ikkje etter gradene.', 'liten'))
    return ''.join(g)


def s_lobe_ark(W, H):
    m = 12
    g = [t(m, 28, 'Mål lobebreidda først', 'tittel')]
    g.append(t(m, 35, 'Ho avgjer om skiva i A held blendingskravet F1. A krev ei flate med lobe under 4,5°.', 'ingress'))
    g.append(t(m, 46, 'SETT OVANFRÅ, IKKJE I MÅLESTOKK', 'mono'))
    c45 = math.cos(math.radians(45))
    p = (m + 70, 92)
    lykt = (p[0] - 44 * c45, p[1] - 44 * c45)
    kort = (p[0] + 30 * c45, p[1] - 30 * c45)
    g.append(f'<line x1="{p[0] - 16}" y1="{p[1]}" x2="{p[0] + 16}" y2="{p[1]}" stroke="#000" stroke-width="1.2"/>')
    g.append(t(p[0], p[1] + 6, 'prøva, maskert til Ø 10 mm', 'mono', 'middle'))
    g.append(f'<line x1="{lykt[0]:.1f}" y1="{lykt[1]:.1f}" x2="{p[0]}" y2="{p[1]}" class="straale"/>')
    g.append(f'<line x1="{p[0]}" y1="{p[1]}" x2="{kort[0]:.1f}" y2="{kort[1]:.1f}" class="straale"/>')
    g.append(f'<circle cx="{lykt[0]:.1f}" cy="{lykt[1]:.1f}" r="2" fill="#000"/>')
    g.append(t(lykt[0] - 4, lykt[1] + 1, 'lykta', 'mono', 'end'))
    kx, ky = kort
    g.append(f'<line x1="{kx - 9 * c45:.1f}" y1="{ky - 9 * c45:.1f}" x2="{kx + 9 * c45:.1f}" y2="{ky + 9 * c45:.1f}" stroke="#000" stroke-width="1.2"/>')
    g.append(t(kx + 9, ky - 3, 'målekortet (side 3)', 'mono'))
    g.append(f'<line x1="{p[0]}" y1="{p[1]}" x2="{p[0]}" y2="{p[1] - 34}" class="hjelp"/>')
    g.append(t(p[0] - 8, p[1] - 12, '45°', 'mono', 'middle'))
    g.append(t(p[0] + 8, p[1] - 12, '45°', 'mono', 'middle'))
    g.append(t((lykt[0] + p[0]) / 2 - 4, (lykt[1] + p[1]) / 2 + 3, '1 m', 'mono', 'end'))
    g.append(t((kx + p[0]) / 2 + 5, (ky + p[1]) / 2 + 4, 'd = 50 cm', 'mono'))
    x = m + 150
    g.append(t(x, 46, 'SLIK GJER DU', 'mono'))
    steg = ['1  Mørkt rom. Lykta 1 m frå prøva, lyset inn på 45°.',
            '2  Dekk prøva med svart papp med eit hol på Ø 10 mm.',
            '     Utan maske måler du storleiken på prøva, ikkje loben.',
            '3  Målekortet 50 cm frå prøva, vinkelrett på den speglande strålen.',
            '4  Les av diameteren D der flekken er halvparten så lys som midten.',
            '     Foto med låst eksponering, teke med ein annan telefon enn lykta.',
            '5  Trekk frå holet: D_lobe ≈ √(D² − 1,5²), D i cm.',
            '6  σ ≈ 0,48 · D_lobe i grader (σ ≈ 24 · D_lobe / d).',
            '7  Send tabellen og bileta, så blir tala lagde inn i modellen.']
    g.append(tekstblokk(x, 52, steg, 'brod', lh=4.4))
    g.append(t(x, 96, 'A krev σ under 4,5°: D_lobe under 9 cm. Blank folie 2,5° gjev D_lobe ≈ 5 cm.', 'liten'))
    g.append(t(x, 101, 'Frå 25 cm ser auget om lag 700 cd/m² ved 4° og 4100 cd/m² ved 6°. Grensa for F1 ligg om lag ved 5°.', 'liten'))
    ty = 112
    for s_, dx in (('PRØVE', 0), ('D, CM', 84), ('D_LOBE', 108), ('σ, GRADER', 132), ('FOTO NR.', 160), ('MERKNAD', 185)):
        g.append(t(m + dx, ty, s_, 'mono'))
    rader = ['1  folie på papp, blank side', '2  folie på papp, matt side', '3  reflektorfilm frå LCD-skjermen',
             '4  frontflatespegelen', '5  fresnelplata utan ark', '6  fresnelplata, eitt diffusorark',
             '7  fresnelplata, to diffusorark', '8  bakepapir oppå folie', '9  kvitt papir (referanse)']
    for i, r in enumerate(rader):
        y = ty + 3 + (i + 1) * 7.2
        g.append(f'<line x1="{m}" y1="{y}" x2="{W - m}" y2="{y}" class="haar"/>')
        g.append(t(m, y - 2.2, r, 'brod'))
    return ''.join(g)


def s_lobe_kort(W, H, maks_cm):
    m = 12
    cx, cy = W / 2, (H / 2) + 2
    g = [t(m, 26, 'Målekortet', 'tittel')]
    g.append(tekstblokk(m, 34, ['Les av diameteren der flekken', 'er halvparten så lys som midten.', 'Linjene er tynne med vilje.'], 'liten', lh=4))
    for D in range(2, maks_cm + 1, 2):
        r = D * 10 / 2
        g.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#9a9a9a" stroke-width="0.15"/>')
        g.append(t(cx + r * 0.707 + 1, cy - r * 0.707 - 1, f'{D} cm', 'mono grå'))
    r9 = math.sqrt(9 ** 2 + 1.5 ** 2) * 10 / 2
    g.append(f'<circle cx="{cx}" cy="{cy}" r="{r9:.2f}" fill="none" stroke="#000" stroke-width="0.2" stroke-dasharray="1.5 1.5"/>')
    g.append(t(cx - r9 * 0.707 - 1, cy + r9 * 0.707 + 4, 'grensa for A', 'mono svart', 'end'))
    g.append(f'<line x1="{cx - 6}" y1="{cy}" x2="{cx + 6}" y2="{cy}" stroke="#000" stroke-width="0.25"/>')
    g.append(f'<line x1="{cx}" y1="{cy - 6}" x2="{cx}" y2="{cy + 6}" stroke="#000" stroke-width="0.25"/>')
    g.append(tekstblokk(m, H - 38, ['Ringane viser D i cm, før holet', 'er trekt frå. Stipla ring: D_lobe', '9 cm, grensa for A (σ 4,5°).'], 'liten', lh=4))
    return ''.join(g)


def halvskive(ox, oy, flik):
    R = D_SKIVE / 2
    g = [kutt(f'M{ox - R} {oy} A{R} {R} 0 0 0 {ox + R} {oy}' + (f' L{ox + R - 6} {oy - 12} L{ox - R + 6} {oy - 12} Z' if flik else ' Z'))]
    if flik:
        g.append(fald(ox - R, oy, ox + R, oy))
        g.append(t(ox, oy - 4.5, 'LIMFLIK: den andre halvdelen ligg kant mot kant oppå', 'mono', 'middle'))
    g.append(f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy + R}" class="hjelp"/>')
    g.append(t(ox + 2, oy + R - 24, 'RIBBA her, på tvers av kastet', 'mono'))
    g.append(f'<circle cx="{ox}" cy="{oy}" r="1.2" fill="#000"/>')
    return ''.join(g)


def ribbemal(ox, oy):
    xs, fr = ribbe_profil()
    pts = [(ox + x, oy - f) for x, f in zip(xs, fr)]
    d = f'M{ox - D_SKIVE / 2} {oy} L{ox + D_SKIVE / 2} {oy} ' + ' '.join(f'L{x:.2f} {y:.2f}' for x, y in reversed(pts)) + ' Z'
    g = [kutt(d)]
    g.append(t(ox, oy + 5, f'RIBBE 1:1 · boge R 1200 mm, pil {k(PIL)} mm · bogen mot baksida av skiva', 'mono', 'middle'))
    g.append(t(ox, oy + 9.5, 'STL: ribbe_R1200_250mm.stl, 6 mm tjukk. Utan printar: tre lag bølgjepapp etter malen.', 'mono grå', 'middle'))
    return ''.join(g)


def s_A_plassering(W, H):
    m = 12; A = G['A']
    g = [t(m, 28, 'A Skiva: plassering og bygging', 'tittel')]
    g.append(t(m, 35, 'Ei lykt i foten lyser på ei bøygd spegelskive som vippar frå veggen ned på feltet. Ein fast flik ved stolpen held veggen bak skjermen lys.', 'ingress'))
    g.append(t(m, 46, 'MÅL FRÅ MODELLEN', 'mono'))
    fl = A['flik_senter_cm']
    maal = ['Foten: 47 cm til høgre for skjermmidten, 7 cm framfor skjermplanet.',
            'Stolpen: 1,5 cm framfor skjermplanet. Armen held skiva 13,5 cm framfor stolpen.',
            'Skiva: midten 41 cm over bordet, 15 cm framfor skjermplanet, altså 8 cm',
            '     framfor lykta. Spegelsida er kuv: ho bular ut mot lykta, 6,5 mm på 250 mm.',
            f'Hovudlykta: 5 cm over bordet, vippa om lag {A["hovudlykt_vinkel_fram_frå_loddrett"]:.0f}° fram mot skivemidten ({k(A["hovudlykt_til_skive_cm"], 0)} cm unna).',
            f'Fliken: 12 × 8,4 cm, midten {fl[2]:.0f} cm over bordet, {k(-A["flik_dx_cm"])} cm til venstre for stolpen',
            f'     og {k(45 - fl[1])} cm framfor skjermplanet. Fest han på ein papplist: rett på stolpen',
            f'     kastar stolpen skugge på veggen. Fliken vender ned og mot venstre, om lag {A["flik_tilt_grader"]:.0f}°',
            '     mot vassrett, og siktar på veggen bak skjermmidten, 45 cm over bordet.',
            f'Fliklykta: {k(-A["flik_dx_cm"])} cm til venstre for og 2 cm bak hovudlykta, peikar nesten rett opp',
            f'     på fliken ({k(A["lykt2_til_flik_cm"], 0)} cm unna). Om lag {A["q"] * 100:.0f} % av lyset.',
            'Stemning: sikt skiveflekken midt på veggen bak skjermen. Arbeid: 10 cm til',
            '     venstre for feltmidten. Fliken står fast i begge.',
            'Møte (F10): sløkk fliklykta. Vend skiva så den kvite baksida ser ned mot lykta',
            '     og mot ansiktet. Vend den korte vegen (150°): spegelsida peikar mot skjermen',
            '     og veggen heile tida, aldri mot deg. Den lange vegen kastar lyset i auga.',
            f'     Lykta må spreie meir enn i arbeid (18° mot 10°): røyr på {k(ROER_MOTE, 0)} mm, halve hovudrøyret.']
    g.append(tekstblokk(m, 52, maal, 'brod', lh=4.4))
    x2 = m + (W - 2 * m) * 0.62
    g.append(t(x2, 46, 'BYGGING', 'mono'))
    steg = ['1  Skjer skiva i papp (side 5 og 6, eller A3).',
            '2  Lim glatt folie på, blank side ut, utan krøll.',
            '     Reflektorfilm frå LCD-skjermen er betre.',
            '     Kvitt, matt papir på baksida (møte).',
            '3  Teip ribba bak, på tvers av kastet.',
            '4  Skjer armen og fliken (side 7). Fliken: folie',
            '     med bakepapir oppå, matt flik blendar.',
            f'5  Rull røyra og set dei på lyktene: {k(ROER_A, 0)} mm på',
            f'     hovudlykta og {k(ROER_FLIK, 0)} mm på fliklykta. Er ho ei',
            f'     lita lommelykt: Ø 15 × {k(ROER_FLIK_15, 0)} mm.',
            '6  Fest armen på stolpen med ledd, så skiva',
            '     kan vippe og bli ståande.',
            f'7  Teip fliken på ein papplist, {k(-G["A"]["flik_dx_cm"])} cm til',
            '     venstre for stolpen.',
            '8  Føreseiing: lågaste rute over 0,5 av snittet',
            '     med bogen, under 0,45 flat. Veggen bak',
            '     skjermen om lag ein tredel av feltet i arbeid.']
    g.append(tekstblokk(x2, 52, steg, 'brod', lh=4.4))
    return ''.join(g)


def s_A_malar_A4(W, H, nr):
    m = 12
    if nr == 1:
        g = [t(m, 26, 'A Skiva: mal 1 av 3', 'tittel')]
        g.append(halvskive(W / 2, 46, flik=True))
        g.append(t(m, 186, 'Halv skive med limflik. Skjer to: den andre er på neste side.', 'liten'))
    else:
        g = [t(m, 26, 'A Skiva: mal 2 av 3 og ribba', 'tittel')]
        g.append(halvskive(W / 2 - 15, 34, flik=False))
        g.append(ribbemal(W / 2 - 15, 176))
    return ''.join(g)


def s_A_malar_3(W, H):
    m = 12
    g = [t(m, 26, 'A Skiva: mal 3 av 3, røyr, flik og arm', 'tittel')]
    g.append(roernett(m + 24, 46, ROER_A, ['HOVUDLYKTA · svart papp', f'{k(ROER_A, 0)} mm: kutt ved 20° frå aksen']))
    g.append(roernett(m + 24, 108, ROER_FLIK, ['FLIKLYKTA · svart papp', f'{k(ROER_FLIK, 0)} mm: kutt ved {G["A"]["lykt2_kutt"]}° frå aksen',
                                               f'lita lommelykt: rull Ø 15 × {k(ROER_FLIK_15, 0)} mm, same kutt']))
    fx, fy = m + 120, 44
    g.append(rekt(fx, fy, 120, 84))
    g.append(maallinje(fx, fy + 84 + 4, fx + 120, fy + 84 + 4, '120 mm'))
    g.append(maallinje(fx + 124, fy, fx + 124, fy + 84, '84 mm'))
    g.append(tekstblokk(fx + 4, fy + 8, ['FLIK · papp, glatt folie, bakepapir oppå',
                                         f'på ein papplist {k(-G["A"]["flik_dx_cm"])} cm til venstre for stolpen,',
                                         '30 cm over bordet'], 'mono', lh=3.8))
    ax, ay = m + 113, 152
    L = ARM + 20
    g.append(f'<rect x="{ax:.2f}" y="{ay:.2f}" width="{L:.2f}" height="20" rx="10" class="kutt"/>')
    for x in (ax + 10, ax + 10 + ARM):
        g.append(f'<circle cx="{x:.2f}" cy="{ay + 10:.2f}" r="2" class="kutt"/>')
    g.append(maallinje(ax + 10, ay + 26, ax + 10 + ARM, ay + 26, f'{ARM:.0f} mm mellom hola'))
    g.append(tekstblokk(ax, ay - 8, ['ARM · to lag papp limte, eller ein trelist', 'hol Ø 4: splittbinders eller skrue med vengemutter'], 'mono', lh=3.8))
    return ''.join(g)


def s_B(W, H):
    m = 12; B = G['B']
    g = [t(m, 28, 'B Over: plassering, bygging og mal', 'tittel')]
    g.append(t(m, 35, 'Fresnelplata over skjermkanten er knekt. Den store delen vippar lyset frå veggen ned på bordet, fliken held veggen bak skjermen lys.', 'ingress'))
    g.append(t(m, 46, 'MÅL FRÅ MODELLEN', 'mono'))
    maal = ['Plata: midten 62 cm over bordet, 20 cm over skjermkanten, midt framfor brukaren og',
            '     9 cm framfor skjermplanet. Ho vippar om ein vassrett akse gjennom midten.',
            '     Tappar midt på sidekantane, ikkje hengsel langs bakkanten.',
            f'Lykta: {k(B["lykt_avstand_cm"], 0)} cm under plata, 51 cm over bordet og 4 cm framfor skjermplanet:',
            '     ein kloss 9 cm over skjermkanten. Ho peikar opp mot midten av plata.',
            'Knekken går langs midtlina frå venstre til høgre. Den framre halvdelen er hovuddelen.',
            f'     Fliken er dei 60 mm bak midtlina, knekt {B["knekk_grader"]:.0f}° mot hovuddelen. Dei bakste 82,5 mm er dekte.',
            f'Arbeid: hovuddelen nesten vassrett (om lag {B["hovuddel_tilt_arbeid"]:.0f}°) og siktar på feltmidten,',
            f'     fliken om lag {B["flik_tilt_arbeid"]:.0f}° og siktar på veggen 60 cm over bordet.',
            f'Stemning: heile plata vippar {B["knekk_grader"]:.0f}°, så begge delar siktar på veggen.',
            'Brønnen skjermar ved 50°. Med 64° ser auget dioden frå 60 cm.']
    g.append(tekstblokk(m, 52, maal, 'brod', lh=4.4))
    x2 = m + (W - 2 * m) * 0.62
    g.append(t(x2, 46, 'BYGGING', 'mono'))
    steg = ['1  Ikkje skjer i fresnelplata. Plata er éi.',
            '     Dekk dei bakste 142,5 mm med svart papp,',
            '     og teip ein flik av blank folie på papp',
            f'     (60 × 285 mm) langs midtlina, {B["knekk_grader"]:.0f}° opp.',
            '     Folieflika gjev veggen like mykje lys som',
            '     ein fresnelstrimmel (135 mot 134 lx i modellen).',
            '2  Same side opp som i projektoren, mot lykta.',
            '3  Ramme med tappar midt på sidekantane,',
            '     og eit stag med merke for dei to stillingane.',
            '4  To diffusorark på hovuddelen.',
            '5  Føreseiing: jamnheit om lag 0,4, veggen',
            '     bak skjermen om lag ein tredel av feltet.']
    g.append(tekstblokk(x2, 52, steg, 'brod', lh=4.4))
    g.append(roernett(m + 18, 118, BRONN_H, ['BRØNN · krage Ø 25 mm, ' + k(BRONN_H) + ' mm høg, svart papp', 'gjev avskjerming ved 50° frå aksen']))
    s = 0.2; rx, ry = m + 130, 118
    g.append(t(rx, ry - 4, 'PLATA SETT OVANFRÅ (1:5)', 'mono'))
    g.append(rekt(rx, ry, 285 * s, 285 * s, 'tynn'))
    g.append(f'<line x1="{rx:.2f}" y1="{ry + 142.5 * s:.2f}" x2="{rx + 285 * s:.2f}" y2="{ry + 142.5 * s:.2f}" class="fald"/>')
    g.append(f'<rect x="{rx:.2f}" y="{ry:.2f}" width="{285 * s:.2f}" height="{82.5 * s:.2f}" fill="#d0d0d0" stroke="none"/>')
    g.append(f'<rect x="{rx:.2f}" y="{ry + 82.5 * s:.2f}" width="{285 * s:.2f}" height="{60 * s:.2f}" fill="none" stroke="#000" stroke-width="0.35"/>')
    for yy, tx in ((ry + 41 * s, 'dekt, 82,5 mm'), (ry + 112.5 * s, 'flik, 60 mm, 48° opp'), (ry + 213 * s, 'hovuddel, 142,5 mm')):
        g.append(t(rx + 285 * s + 4, yy + 1, tx, 'mono grå'))
    g.append(t(rx + 285 * s / 2, ry - 0.5 + 285 * s + 5, 'mot brukaren', 'mono grå', 'middle'))
    g.append(t(rx + 285 * s / 2, ry - 1.5, '', 'mono grå', 'middle'))
    g.append(t(rx + 285 * s + 4, ry - 1, 'mot veggen', 'mono grå'))
    return ''.join(g)


def s_C(W, H):
    m = 12; C = G['C']
    g = [t(m, 28, 'C Vindauge: plassering og bygging', 'tittel')]
    g.append(t(m, 35, 'Ei vasskule teiknar eit vindauge av lys på veggen. Ein spegel glir inn i strålen og legg feltet på bordet, medan vindauget blir.', 'ingress'))
    g.append(t(m, 46, 'MÅL FRÅ MODELLEN', 'mono'))
    maal = [f'Hovudet: {C["hovud_cm"][2]:.0f} cm over bordet, {C["hovud_cm"][0]:.0f} cm til høgre for skjermmidten, 3 cm framfor',
            '     skjermplanet. Foten 5 cm bak skjermplanet. Stolpen på ein kloss eller ei lekt.',
            f'Utan spegel: sikt midt på veggen bak skjermen, 42 cm over bordet ({C["til_vegg_cm"]:.0f} cm unna).',
            f'Spegelen inne: 65 % av strålen går ned på feltmidten ({C["til_felt_cm"]:.0f} cm unna).',
            f'     Strålen bøyer om lag {C["avboying_grader"]:.0f}° mellom vegg og felt. Resten blir verande vindauge.',
            f'Linsa: julekule av glas, Ø 70 mm, fylt med vatn. f om lag 70 mm frå midten av kula.',
            f'Maska: {k(C["u_mm"], 0)} mm frå midten av kula, innanfor fokus ({k(C["u_skarp_mm"], 0)} mm),',
            '     så kanten blir mjuk, om lag 6 cm på bordet.',
            'Kondensoren: kredittkort-fresnel 85 × 55 mm rett bak maska, mot lykta.',
            'Gråfilteret ligg i maska og dempar den delen av feltet som er nærast lampa.']
    g.append(tekstblokk(m, 52, maal, 'brod', lh=4.4))
    x2 = m + (W - 2 * m) * 0.62
    g.append(t(x2, 46, 'BYGGING', 'mono'))
    steg = ['1  Fyll kula over ei skål, med hanskar. Tett',
            '     opninga. Kula kviler i ein ring av papp.',
            '2  Skriv ut maska og gråfilteret (side 10):',
            '     maska på papir, filteret på overheadfilm.',
            '3  Lykt, kondensor, filter og maske i éin',
            '     svart pappboks. Maska vender mot kula.',
            '4  Frontflatespegelen på ei pappflik rett etter',
            '     kula. Inne dekkjer flika 65 % av strålen.',
            '5  Drei og snu maska til hjørna treffer feltet.',
            '6  Føreseiing: vindauget står i ro medan feltet',
            '     kjem fram, og skjermen får under 0,15 av',
            '     feltet heile vegen.']
    g.append(tekstblokk(x2, 52, steg, 'brod', lh=4.4))
    return ''.join(g)


def filterbilete(Wt):
    """Gråfilteret som PNG: kvitt slepp alt gjennom, mørkt dempar. Rad 0 er y minst."""
    from PIL import Image
    a = (np.clip(Wt, 0, 1) * 255).astype(np.uint8)[::-1]        # SVG y ned, maskekoordinat y opp
    im = Image.fromarray(a, 'L')
    buf = io.BytesIO(); im.save(buf, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def s_C_maske(W, H):
    m = 12; C = G['C']
    d = np.load(os.path.join(HER, 'maske_C.npz'))
    X, Y, Wt, poly = d['X'] * 1000, d['Y'] * 1000, d['W'], d['poly'] * 1000
    g = [t(m, 26, 'C Vindauge: maske og gråfilter 1:1', 'tittel')]
    # maska på papp: opninga er polygonet, i ei ramme 90 × 90 mm
    for i, (ox, tittel_, filter_) in enumerate(((m + 60, 'MASKE · svart papp, skjer ut opninga', False),
                                               (m + 185, 'GRÅFILTER · skriv ut på overheadfilm', True))):
        oy = 100
        P = [(ox + x, oy - y) for x, y in poly]
        if filter_:
            x0, x1 = X.min(), X.max(); y0, y1 = Y.min(), Y.max()
            g.append(f'<image x="{ox + x0:.2f}" y="{oy - y1:.2f}" width="{x1 - x0:.2f}" height="{y1 - y0:.2f}" preserveAspectRatio="none" href="{filterbilete(Wt)}"/>')
            g.append('<path d="M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in P) + ' Z" fill="none" stroke="#000" stroke-width="0.2" stroke-dasharray="1 1"/>')
        else:
            g.append(rekt(ox - 45, oy - 45, 90, 90))
            g.append('<path d="M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in P) + ' Z" class="kutt"/>')
        namn = C['hjorne_namn']
        for (x, y), nm in zip(P, namn):
            g.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="0.6" fill="#000"/>')
        g.append(f'<circle cx="{ox}" cy="{oy}" r="0.8" fill="#000"/>')
        g.append(tekstblokk(ox - 45, oy + 52, [tittel_], 'mono', lh=3.8))
    lab = ['Hjørna lagar desse hjørna i feltet:']
    for nm, (x, y) in zip(C['hjorne_namn'], poly):
        lab.append(f'· {nm}: x {k(x)} mm, y {k(y)} mm frå krossen')
    g.append(tekstblokk(m, 160, lab, 'liten', lh=4))
    g.append(tekstblokk(m + 140, 160, ['Maska og filteret ligg oppå kvarandre, krossen på krossen.',
                                       f'Filteret slepp gjennom {k(C["filter_min"] * 100, 0)} til 100 %: mørkast der feltet er nærast lampa.',
                                       'Linsa snur biletet. Ligg feltet feil, snu maska og filteret saman.',
                                       f'Maska {k(C["u_mm"], 0)} mm frå midten av kula. Kondensoren rett bak maska.'], 'liten', lh=4))
    return ''.join(g)


def s_A3(W, H):
    m = 12; R = D_SKIVE / 2
    g = [t(m, 26, 'A Skiva: heil skive og ribbe', 'tittel')]
    cx, cy = m + 20 + R, 152
    g.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" class="kutt"/>')
    g.append(f'<line x1="{cx}" y1="{cy - R}" x2="{cx}" y2="{cy + R}" class="hjelp"/>')
    g.append(t(cx + 2, cy + R - 24, 'RIBBA her, på tvers av kastet', 'mono'))
    g.append(f'<circle cx="{cx}" cy="{cy}" r="1.2" fill="#000"/>')
    g.append(t(cx, cy + 5, f'SKIVE Ø {D_SKIVE:.0f} mm · papp med glatt folie, blank side ut', 'mono', 'middle'))
    rx = cx + R + 20
    g.append(f'<g transform="rotate(-90 {rx} {cy})">{ribbemal(rx, cy)}</g>')
    return ''.join(g)


STIL = '''
@font-face { font-family: "EBG"; src: url("FONT") format("opentype"); }
@page { size: SIDE; margin: 0; }
html, body { margin: 0; padding: 0; background: #fff; }
.ark { break-after: page; overflow: hidden; }
.ark:last-child { break-after: auto; }
svg text { font-family: "EBG", Georgia, serif; fill: #000; }
svg .mono { font-family: Consolas, "Courier New", monospace; font-size: 2.6px; letter-spacing: 0.12px; fill: #555; }
svg .mono.svart { fill: #000; }
svg .mono.grå { fill: #888; }
svg .tittel { font-size: 8px; }
svg .ingress { font-size: 3.6px; fill: #333; }
svg .brod { font-size: 3.2px; }
svg .brod.svart { fill: #000; }
svg .kursiv { font-size: 4.2px; font-style: italic; }
svg .liten { font-size: 2.9px; fill: #555; }
svg .strek { stroke: #000; stroke-width: 0.25; }
svg .haar { stroke: #c8c8c8; stroke-width: 0.2; }
svg .kutt, svg .kuttlinje { fill: none; stroke: #000; stroke-width: 0.3; }
svg .tynn { fill: none; stroke: #000; stroke-width: 0.25; }
svg .fald { stroke: #000; stroke-width: 0.25; stroke-dasharray: 2 1.2; }
svg .maal { stroke: #777; stroke-width: 0.18; }
svg .hjelp { stroke: #999; stroke-width: 0.2; stroke-dasharray: 1 1; }
svg .straale { stroke: #000; stroke-width: 0.35; stroke-dasharray: 3 1.5; }
'''


def html(sider, W, H):
    s = STIL.replace('FONT', FONT).replace('SIDE', f'{W}mm {H}mm')
    return ('<!doctype html><html lang="nn"><head><meta charset="utf-8"><title>Byggjepakke</title><style>' + s +
            '</style></head><body>' + ''.join(sider) + '</body></html>')


def skriv_pdf(htmlfil, pdffil):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-first-run', f'--user-data-dir={tmp}',
                        '--no-pdf-header-footer', '--virtual-time-budget=4000', f'--print-to-pdf={pdffil}',
                        'file:///' + htmlfil.replace('\\', '/')], check=True, capture_output=True, timeout=180)


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    print('pil', round(PIL, 2), 'røyr A', round(ROER_A, 1), 'røyr flik', round(ROER_FLIK, 1), 'brønn', round(BRONN_H, 2))
    print('stl', skriv_stl(os.path.join(HER, 'ribbe_R1200_250mm.stl')), 'trekantar')
    W, H = 297, 210
    innhald = [s_oversikt(W, H), s_lobe_ark(W, H), s_lobe_kort(W, H, 16), s_A_plassering(W, H), s_A_malar_A4(W, H, 1),
               s_A_malar_A4(W, H, 2), s_A_malar_3(W, H), s_B(W, H), s_C(W, H), s_C_maske(W, H)]
    tit = ['Oversikt', 'Lobebreidda', 'Målekortet', 'A Skiva', 'A Skiva, mal 1', 'A Skiva, mal 2', 'A Skiva, mal 3', 'B Over',
           'C Vindauge', 'C Vindauge, maske']
    sider = [side_svg(W, H, s, tit[i], i + 1, len(innhald)) for i, s in enumerate(innhald)]
    hf = os.path.join(HER, 'byggjepakke-A4.html'); open(hf, 'w', encoding='utf-8').write(html(sider, W, H))
    skriv_pdf(hf, os.path.join(HER, 'byggjepakke-A4.pdf')); print('skrive byggjepakke-A4.pdf')
    W3, H3 = 420, 297
    sider3 = [side_svg(W3, H3, s_lobe_kort(W3, H3, 24), 'Målekortet', 1, 2), side_svg(W3, H3, s_A3(W3, H3), 'A Skiva, malar', 2, 2)]
    hf3 = os.path.join(HER, 'malar-A3.html'); open(hf3, 'w', encoding='utf-8').write(html(sider3, W3, H3))
    skriv_pdf(hf3, os.path.join(HER, 'malar-A3.pdf')); print('skrive malar-A3.pdf')
