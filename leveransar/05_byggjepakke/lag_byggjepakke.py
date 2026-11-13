# -*- coding: utf-8 -*-
"""Byggjepakke for dei tre skissemodellane til konseptgjennomgangen 18.11.

Lagar to PDF-ar i målestokk 1:1 (alle mål i SVG-einingar er millimeter):
  byggjepakke-A4.pdf   heile pakken: rekkjefølgje, målearket for lobebreidda, malar og mål for A, B og C
  malar-A3.pdf         malane som ikkje får plass på A4 i eitt stykke: målekortet til 28 cm og heile skiva til A
og ribbe_R1200_250mm.stl til 3D-printaren.

Måla kjem frå konsept/tre/00-tre-konsept.md, konsept/reflektor/*/funn.md og familiefilene (posisjonar i rommet).
Vinklane er rekna frå dei same posisjonane (sjå rekn_vinklar()).

  python lag_byggjepakke.py
"""
import os, sys, math, struct, subprocess, tempfile
import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
FONT = '../01_fase1_sider/fonts/EBGaramond12-Regular.otf'
NB = '\u00a0'

# ------------------------------------------------------------------ geometri frå modellen
R_SKIVE = 1200.0          # mm, kuv boge
D_SKIVE = 250.0
PIL = R_SKIVE - math.sqrt(R_SKIVE ** 2 - (D_SKIVE / 2) ** 2)      # 6,5 mm
T_RIBBE = 6.0             # mm, minste djupn på ribba (ved endane)
H_RIBBE = 6.0             # mm, tjukn (printhøgd)
ROER_D, ROER_L = 25.0, 100.0
OVERLAPP = 8.0
BRONN_H = (ROER_D / 2) / math.tan(math.radians(50))               # 10,5 mm gjev avskjerming ved 50°
V_FELT = 611.0            # mm, linsehovudet til feltmidten (C)
F_KULE = 70.0             # glaskule Ø 70 mm fylt med vatn: f = nD / 4(n-1) = 70 mm frå midten


def maske(f, v=V_FELT, felt=(600.0, 400.0)):
    u = f * v / (v - f)
    m = (v - f) / f
    return u, felt[0] / m, felt[1] / m


def rekn_vinklar():
    """Vinklane mellom stemning og arbeid, rekna frå posisjonane i modellen (meter, bordkoordinatar)."""
    def n(v): v = np.asarray(v, float); return v / np.linalg.norm(v)
    def flate(c, kjelde, maal):
        nn = n(n(np.subtract(kjelde, c)) + n(np.subtract(maal, c)))
        return nn, math.degrees(math.acos(min(1.0, -nn[2])))       # vinkel mot vassrett = vinkel mellom normal og -z
    ut = {}
    # A: skiva (0,47, 0,30, 0,41), lykta i foten (0,47, 0,38, 0,05). Stemning: veggen (0, 0,70, 0,45). Arbeid: SIKT (-0,10, 0,25, 0)
    c, k = (0.47, 0.30, 0.41), (0.47, 0.38, 0.05)
    ns, vs = flate(c, k, (0.0, 0.70, 0.45)); na, va = flate(c, k, (-0.10, 0.25, 0.0))
    ut['A'] = dict(stemning=vs, arbeid=va, dreiing=math.degrees(math.acos(float(ns @ na))))
    # B: plata OVER_C (0, 0,36, 0,62), lykta 12 cm langs OVER_A (0, 0,40, -0,90). Stemning: veggen (0, 0,70, 0,60). Arbeid: feltmidten
    c = np.array([0.0, 0.36, 0.62]); k = c + 0.12 * n((0.0, 0.40, -0.90))
    ns, vs = flate(c, k, (0.0, 0.70, 0.60)); na, va = flate(c, k, (0.0, 0.25, 0.0))
    ut['B'] = dict(stemning=vs, arbeid=va, dreiing=math.degrees(math.acos(float(ns @ na))), lykt=k)
    # C: linsehovudet (0,47, 0,40, 0,36). Veggen bak skjermmidten (0, 0,70, 0,42). Feltmidten (0, 0,25, 0)
    h = np.array([0.47, 0.40, 0.36])
    dw, df = np.array([0.0, 0.70, 0.42]) - h, np.array([0.0, 0.25, 0.0]) - h
    ut['C'] = dict(vegg=np.linalg.norm(dw) * 1000, felt=np.linalg.norm(df) * 1000,
                   avbøying=math.degrees(math.acos(float(n(dw) @ n(df)))))
    return ut


V = rekn_vinklar()


# ------------------------------------------------------------------ STL for ribba
def ribbe_profil(n=101):
    xs = np.linspace(-D_SKIVE / 2, D_SKIVE / 2, n)
    d = R_SKIVE - np.sqrt(R_SKIVE ** 2 - xs ** 2)
    front = T_RIBBE + (PIL - d)            # kuv boge: tjukkast på midten
    return xs, front


def skriv_stl(fil):
    xs, fr = ribbe_profil()
    tri = []
    def q(a, b, c, d):                     # firkant som to trekantar
        tri.append((a, b, c)); tri.append((a, c, d))
    for i in range(len(xs) - 1):
        x0, x1 = xs[i], xs[i + 1]
        for z in (0.0, H_RIBBE):
            a, b, c, d = (x0, 0, z), (x1, 0, z), (x1, fr[i + 1], z), (x0, fr[i], z)
            q(a, b, c, d) if z else q(a, d, c, b)
        q((x0, 0, 0), (x1, 0, 0), (x1, 0, H_RIBBE), (x0, 0, H_RIBBE))                       # baksida
        q((x0, fr[i], 0), (x0, fr[i], H_RIBBE), (x1, fr[i + 1], H_RIBBE), (x1, fr[i + 1], 0))   # bogen
    for x, f in ((xs[0], fr[0]), (xs[-1], fr[-1])):                                         # endane
        q((x, 0, 0), (x, 0, H_RIBBE), (x, f, H_RIBBE), (x, f, 0))
    with open(fil, 'wb') as fh:
        fh.write(b'ribbe R1200 boge 250 mm, GK5 skissemodell A'.ljust(80, b' '))
        fh.write(struct.pack('<I', len(tri)))
        for a, b, c in tri:
            a, b, c = map(np.asarray, (a, b, c))
            nv = np.cross(b - a, c - a); L = np.linalg.norm(nv); nv = nv / L if L else nv
            fh.write(struct.pack('<12fH', *nv, *a, *b, *c, 0))
    return len(tri)


# ------------------------------------------------------------------ SVG-hjelparar (mm)
def t(x, y, s, kl='', anker='start', storleik=None):
    st = f' font-size="{storleik}"' if storleik else ''
    return f'<text x="{x:.2f}" y="{y:.2f}" class="{kl}" text-anchor="{anker}"{st}>{s}</text>'


def tekstblokk(x, y, liner, kl='', lh=4.6, storleik=None):
    return ''.join(t(x, y + i * lh, s, kl, storleik=storleik) for i, s in enumerate(liner))


def ramme(W, H, tittel, nr, total):
    m = 12
    g = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>']
    g.append(t(m, m, 'GK5 · NORTHERN · BYGGJEPAKKE', 'mono'))
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
    for k in range(1, 10):
        g.append(f'<line x1="{x0 + 10 * k}" y1="{yb - 2.4}" x2="{x0 + 10 * k}" y2="{yb - 1.2}" stroke="#000" stroke-width="0.2"/>')
    g.append(t(W - m, yb, f'side {nr} av {total}', 'mono', 'end'))
    return ''.join(g)


def side_svg(W, H, innhald, tittel, nr, total):
    return (f'<section class="ark" style="width:{W}mm;height:{H}mm"><svg width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}" '
            f'xmlns="http://www.w3.org/2000/svg">{ramme(W, H, tittel, nr, total)}{innhald}</svg></section>')


def kutt(path_d):
    return f'<path d="{path_d}" class="kutt"/>'


def fald(x1, y1, x2, y2):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" class="fald"/>'


def rekt(x, y, w, h, kl='kutt'):
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" class="{kl}"/>'


def maallinje(x1, y1, x2, y2, tekst, side=1):
    """Mållinje med ende-strekar og tekst midt på."""
    g = [f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" class="maal"/>']
    dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    for (x, y) in ((x1, y1), (x2, y2)):
        g.append(f'<line x1="{x - 1.6 * nx:.2f}" y1="{y - 1.6 * ny:.2f}" x2="{x + 1.6 * nx:.2f}" y2="{y + 1.6 * ny:.2f}" class="maal"/>')
    mx, my = (x1 + x2) / 2 + side * 3.2 * nx, (y1 + y2) / 2 + side * 3.2 * ny
    ang = math.degrees(math.atan2(dy, dx))
    if ang > 90 or ang < -90: ang += 180
    g.append(f'<text transform="translate({mx:.2f},{my + 1:.2f}) rotate({ang:.1f})" class="mono" text-anchor="middle">{tekst}</text>')
    return ''.join(g)


# ------------------------------------------------------------------ sidene
def s_oversikt(W, H):
    m = 12
    kol = [
        ('A SKIVA', 'vipp skiva',
         ['stolpen frå overheadprojektoren', 'telefonen (lykta)', 'reflektorfilm frå LCD-skjermen, om du har',
          'ribba (3D-print, STL i mappa)'],
         ['skive Ø 250 mm av papp med glatt aluminiumsfolie', 'arm 13,5 cm frå stolpen til skivemidten',
          'svart papprull Ø 25 × 100 mm', 'kloss 5 cm under lykta']),
        ('B OVER', 'vipp plata',
         ['fresnelplata 285 × 285 mm', 'stolpen frå overheadprojektoren', 'eitt og to diffusorark', 'telefonen (lykta)'],
         ['pappramme, fire strimlar 20 mm breie', 'teiphengsel langs bakkanten', 'brønn: svart krage Ø 25 × 10,5 mm',
          'kloss på skjermkanten, 8 til 9 cm']),
        ('C VINDAUGE', 'skyv spegelen inn',
         ['frontflatespegelen frå projektorhovudet', 'telefonen (lykta)', 'lupe, eller rund glaskule Ø 70 mm fylt med vatn'],
         ['maske i svart papp, opning etter brennvidda', 'trakt av papp med folie inni', 'pappflik som spegelen vippar inn på',
          'halding for linsa 36 cm over bordet']),
    ]
    g = [t(m, 30, 'Tre skissemodellar til konseptgjennomgangen 18.11', 'tittel')]
    g.append(t(m, 38, 'Kvar modell syner lyset i rommet, ikkje forma. Same telefonlykt i alle tre, så bileta kan samanliknast.', 'ingress'))
    bw = (W - 2 * m - 2 * 8) / 3
    for i, (namn, gest, kit, lag) in enumerate(kol):
        x = m + i * (bw + 8); y = 52
        g.append(t(x, y, namn, 'mono svart'))
        g.append(t(x, y + 6, gest + '.', 'kursiv'))
        g.append(t(x, y + 15, 'FRÅ BYGGJESETTET', 'mono'))
        g.append(tekstblokk(x, y + 20.5, ['· ' + s for s in kit], 'brod'))
        y2 = y + 22 + 4.6 * len(kit) + 3
        g.append(t(x, y2, 'LAG SJØLV', 'mono'))
        g.append(tekstblokk(x, y2 + 5.5, ['· ' + s for s in lag], 'brod'))
    y = 118
    g.append(f'<line x1="{m}" y1="{y - 6}" x2="{W - m}" y2="{y - 6}" class="haar"/>')
    g.append(t(m, y, 'REKKJEFØLGJE', 'mono'))
    rek = ['1  Start 3D-printen av ribba til A. Ho printar medan du gjer resten.',
           '2  Mål lobebreidda (side 2 og 3). Ho avgjer blendinga for A og B. Send tala før du byggjer vidare.',
           '3  Byggj B. Det går fortast: plata, ramma, stolpen og telefonen.',
           '4  Byggj A når ribba er ferdig.',
           '5  Mål brennvidda på lupa eller kula (side 8), skjer maska og byggj C.',
           '6  Fotografer etter fotolista, same kamera og eksponering for alle tre.']
    g.append(tekstblokk(m, y + 6, rek, 'brod'))
    x = m + (W - 2 * m) * 0.56
    g.append(t(x, y, 'TRYGGLEIK', 'mono'))
    tr = ['Overheadprojektoren skal ikkje koplast til straum. Fjern nettleidningane i stolpen.',
          'Fresnelplata, blanke hole former og ei vassfylt kule samlar sollys og kan tenne papp.',
          'Aldri i sol eller ved vindauge. Lagre dei tildekte.',
          'Frontflatespegelen: ikkje ta på flata, ikkje tørk av. Støv med mjuk pensel.',
          'Klipt folie og tynn plate har skarpe kantar.']
    g.append(tekstblokk(x, y + 6, tr, 'brod'))
    g.append(t(m, H - 26, 'Måla er frå lysmodellen (konsept/tre/tre.py og konsept/reflektor). Vinklane er rekna frå same posisjonar. Modellen er ikkje målt.', 'liten'))
    return ''.join(g)


def s_lobe_ark(W, H):
    m = 12
    g = [t(m, 30, 'Mål lobebreidda først', 'tittel')]
    g.append(t(m, 38, 'Ho avgjer om A og B held blendingskravet F1. Modellen reknar 2,5° for blank folie og 10° for satin.', 'ingress'))
    # diagram sett ovanfrå
    ox, oy = m + 8, 62
    g.append(t(ox - 8, 50, 'SETT OVANFRÅ, IKKJE I MÅLESTOKK', 'mono'))
    p = (ox + 60, oy + 48)                       # prøva
    lykt = (p[0] - 60 * math.cos(math.radians(45)) * 1.3, p[1] - 60 * math.sin(math.radians(45)) * 1.3)
    kort = (p[0] + 42 * math.cos(math.radians(45)), p[1] - 42 * math.sin(math.radians(45)))
    g.append(f'<line x1="{p[0] - 18}" y1="{p[1]}" x2="{p[0] + 18}" y2="{p[1]}" stroke="#000" stroke-width="1.2"/>')
    g.append(t(p[0], p[1] + 6, 'prøva', 'mono', 'middle'))
    g.append(f'<line x1="{lykt[0]:.1f}" y1="{lykt[1]:.1f}" x2="{p[0]}" y2="{p[1]}" class="straale"/>')
    g.append(f'<line x1="{p[0]}" y1="{p[1]}" x2="{kort[0]:.1f}" y2="{kort[1]:.1f}" class="straale"/>')
    g.append(f'<circle cx="{lykt[0]:.1f}" cy="{lykt[1]:.1f}" r="2" fill="#000"/>')
    g.append(t(lykt[0] - 3, lykt[1] - 3, 'telefonlykta', 'mono', 'end'))
    kx, ky = kort; dx, dy = math.cos(math.radians(45)), math.sin(math.radians(45))
    g.append(f'<line x1="{kx - 10 * dy:.1f}" y1="{ky - 10 * dx:.1f}" x2="{kx + 10 * dy:.1f}" y2="{ky + 10 * dx:.1f}" stroke="#000" stroke-width="1.2"/>')
    g.append(t(kx + 6, ky - 6, 'målekortet (side 3)', 'mono'))
    g.append(f'<line x1="{p[0]}" y1="{p[1]}" x2="{p[0]}" y2="{p[1] - 40}" class="hjelp"/>')
    g.append(t(p[0] - 14, p[1] - 14, '45°', 'mono', 'middle'))
    g.append(t(p[0] + 14, p[1] - 14, '45°', 'mono', 'middle'))
    g.append(t((lykt[0] + p[0]) / 2 - 8, (lykt[1] + p[1]) / 2 + 2, '1 m', 'mono', 'end'))
    g.append(t((kx + p[0]) / 2 + 6, (ky + p[1]) / 2 + 4, 'd = 50 cm', 'mono'))
    # framgang
    x = m + 150
    g.append(t(x, 50, 'SLIK GJER DU', 'mono'))
    steg = ['1  Mørkt rom. Telefonlykta 1 m frå prøva, lyset inn på 45°.',
            '2  Målekortet 50 cm frå prøva, vinkelrett på den speglande strålen.',
            '3  Sikt midten av flekken på krossen.',
            '4  Les av diameteren D der flekken er halvparten så lys som midten.',
            '     Ta eit foto rett framfrå med låst eksponering og kvitbalanse.',
            '5  Rekn σ = 0,48 · D, med D i cm og σ i grader (σ ≈ 24 · D / d).',
            '6  Send tabellen og bileta, så blir tala lagde inn i modellen.']
    g.append(tekstblokk(x, 56, steg, 'brod'))
    g.append(t(x, 92, 'Referansar: blank folie 2,5° gjev D ≈ 5 cm. Satin 10° gjev D ≈ 21 cm.', 'liten'))
    g.append(t(x, 97, 'Ligg folie på papp på 4 til 6°, ser auget frå 25 cm 1600 til 9000 cd/m² i spegelskivene.', 'liten'))
    # tabell til utfylling
    ty = 112
    kol = [('PRØVE', 0), ('D, CM', 92), ('σ = 0,48 · D', 122), ('FOTO NR.', 160), ('MERKNAD', 185)]
    for s, dx in kol:
        g.append(t(m + dx, ty, s, 'mono'))
    rader = ['1  folie på papp, blank side', '2  folie på papp, matt side', '3  reflektorfilm frå LCD-skjermen',
             '4  frontflatespegelen', '5  fresnelplata utan ark', '6  fresnelplata, eitt diffusorark',
             '7  fresnelplata, to diffusorark', '8  bakepapir oppå folie', '9  kvitt papir (referanse)']
    for i, r in enumerate(rader):
        y = ty + 3 + (i + 1) * 7.4
        g.append(f'<line x1="{m}" y1="{y}" x2="{W - m}" y2="{y}" class="haar"/>')
        g.append(t(m, y - 2.2, r, 'brod'))
    return ''.join(g)


def s_lobe_kort(W, H, maks_cm):
    m = 12
    cx, cy = W / 2, (H + 4) / 2
    g = [t(m, 26, 'Målekortet', 'tittel'), t(m, 33, 'Les av diameteren der flekken er halvparten så lys som midten. Linjene er tynne med vilje.', 'ingress')]
    for D in range(2, maks_cm + 1, 2):
        r = D * 10 / 2
        g.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#9a9a9a" stroke-width="0.15"/>')
        g.append(t(cx + r * 0.707 + 1, cy - r * 0.707 - 1, f'{D} cm · {0.48 * D:.1f}°'.replace('.', ','), 'mono grå'))
    g.append(f'<line x1="{cx - 6}" y1="{cy}" x2="{cx + 6}" y2="{cy}" stroke="#000" stroke-width="0.25"/>')
    g.append(f'<line x1="{cx}" y1="{cy - 6}" x2="{cx}" y2="{cy + 6}" stroke="#000" stroke-width="0.25"/>')
    g.append(t(m, H - 26, 'D i cm · σ i grader, for d = 50 cm. Ved anna avstand: σ ≈ 24 · D / d.', 'liten'))
    return ''.join(g)


def halvskive(ox, oy, flik):
    """Halv skive R 125 med rett kant oppe i (ox, oy). Flik på 12 mm langs den rette kanten om flik."""
    R = D_SKIVE / 2
    g = [kutt(f'M{ox - R} {oy} A{R} {R} 0 0 0 {ox + R} {oy}' + (f' L{ox + R - 6} {oy - 12} L{ox - R + 6} {oy - 12} Z' if flik else ' Z'))]
    if flik:
        g.append(fald(ox - R, oy, ox + R, oy))
        g.append(t(ox, oy - 4.5, 'LIMFLIK: lim den andre halvdelen her, kant mot kant på framsida', 'mono', 'middle'))
    g.append(f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy + R}" class="hjelp"/>')
    g.append(t(ox + 2, oy + R - 8, 'RIBBA her, på tvers av kastet', 'mono'))
    g.append(f'<circle cx="{ox}" cy="{oy}" r="1.2" fill="#000"/>')
    return ''.join(g)


def ribbemal(ox, oy):
    """Ribbeprofilen i 1:1 med bogen opp. ox, oy er midten av den rette baksida."""
    xs, fr = ribbe_profil()
    pts = [(ox + x, oy - f) for x, f in zip(xs, fr)]
    d = f'M{ox - D_SKIVE / 2} {oy} L{ox + D_SKIVE / 2} {oy} ' + ' '.join(f'L{x:.2f} {y:.2f}' for x, y in reversed(pts)) + ' Z'
    g = [kutt(d)]
    g.append(t(ox, oy + 5.5, f'RIBBE 1:1 · boge R 1200 mm, pil {PIL:.1f} mm · bogen mot baksida av skiva'.replace('.', ','), 'mono', 'middle'))
    g.append(t(ox, oy + 10, 'STL: ribbe_R1200_250mm.stl, 6 mm tjukk. Utan printar: tre lag bølgjepapp etter malen.', 'mono grå', 'middle'))
    return ''.join(g)


def roernett(ox, oy, L, tekst):
    w = math.pi * ROER_D + OVERLAPP
    g = [rekt(ox, oy, w, L)]
    g.append(fald(ox + w - OVERLAPP, oy, ox + w - OVERLAPP, oy + L))
    g.append(maallinje(ox, oy + L + 4, ox + w, oy + L + 4, f'{w:.1f} mm'.replace('.', ',')))
    g.append(maallinje(ox - 4, oy, ox - 4, oy + L, f'{L:.1f} mm'.replace('.', ','), side=-1))
    g.append(tekstblokk(ox, oy - 7.5, tekst, 'mono', lh=3.8))
    return ''.join(g)


def s_A_plassering(W, H):
    m = 12; a = V['A']
    g = [t(m, 30, 'A Skiva: plassering og bygging', 'tittel')]
    g.append(t(m, 38, 'Ei kjelde i foten lyser opp på ei bøygd spegelskive. Skiva vippar lyset frå veggen bak skjermen ned på arbeidsfeltet.', 'ingress'))
    x = m
    g.append(t(x, 50, 'MÅL FRÅ MODELLEN', 'mono'))
    maal = ['Foten: 47 cm til høgre for skjermmidten, 7 cm framfor skjermplanet.',
            'Lykta: 5 cm over bordet i papprullet, peikar opp mot midten av skiva.',
            'Stolpen: 1,5 cm framfor skjermplanet. Ein arm held skiva 13,5 cm framfor stolpen.',
            'Skiva: midten 41 cm over bordet og 15 cm framfor skjermplanet, rett over lykta.',
            'Spegelsida er kuv: ho bular ut mot lykta, 6,5 mm på 250 mm.',
            f'Stemning: sikt flekken midt på veggen bak skjermen, 45 cm over bordet. Skiva om lag {a["stemning"]:.0f}° mot vassrett.',
            f'Arbeid: sikt flekken 10 cm til venstre for feltmidten. Skiva om lag {a["arbeid"]:.0f}° mot vassrett.',
            f'Mellom dei dreier skiva om lag {a["dreiing"]:.0f}°. Sikt etter flekken, ikkje etter gradene.']
    g.append(tekstblokk(x, 56, maal, 'brod'))
    x2 = m + (W - 2 * m) * 0.56
    g.append(t(x2, 50, 'BYGGING', 'mono'))
    steg = ['1  Skjer skiva i papp etter malen (to halvdelar på A4, éin heil på A3).',
            '2  Lim glatt aluminiumsfolie på, blank side ut, utan krøll.',
            '     Har du reflektorfilm frå LCD-skjermen, bruk han i staden.',
            '3  Teip ribba bak, midt på og på tvers av kastet. Skiva tek bogen.',
            '4  Rull papprullet rundt eit Ø 25 mm skaft og lim. Svart side inn.',
            '5  Set telefonen på klossen med lykta opp i rullet.',
            '6  Fest armen på stolpen og skiva på armen, så ho kan vippast.',
            '7  Føreseiing: med bogen er lågaste rute over 0,5 av snittet,',
            '     flat skive under 0,45.']
    g.append(tekstblokk(x2, 56, steg, 'brod'))
    g.append(roernett(m + 18, 118, ROER_L, ['PAPPRULL Ø 25 × 100 MM, svart papp', 'stipla: fald, limflik på 8 mm']))
    return ''.join(g)


def s_A_malar_A4(W, H, nr):
    m = 12; R = D_SKIVE / 2
    if nr == 1:
        g = [t(m, 26, 'A Skiva: mal 1 av 2', 'tittel')]
        g.append(halvskive(W / 2, 46, flik=True))
        g.append(t(m, 190, 'Halv skive med limflik. Skjer to: den andre er på neste side.', 'liten'))
    else:
        g = [t(m, 26, 'A Skiva: mal 2 av 2 og ribba', 'tittel')]
        g.append(halvskive(W / 2 - 15, 36, flik=False))
        g.append(ribbemal(W / 2 - 15, 183))
    return ''.join(g)


def s_B(W, H):
    m = 12; b = V['B']
    g = [t(m, 30, 'B Over: plassering, bygging og mal', 'tittel')]
    g.append(t(m, 38, 'Fresnelplata ligg over skjermkanten og vippar lyset frå veggen bak skjermen ned på bordet.', 'ingress'))
    g.append(t(m, 50, 'MÅL FRÅ MODELLEN', 'mono'))
    lz = b['lykt'][2] * 100; ly = (0.45 - b['lykt'][1]) * 100
    maal = ['Plata: midten 62 cm over bordet, 20 cm over skjermkanten, midt framfor brukaren,',
            '     9 cm framfor skjermplanet. Hengsel langs bakkanten.',
            f'Lykta: 12 cm under plata, om lag {lz:.0f} cm over bordet og {ly:.0f} cm framfor skjermplanet.',
            '     Det er 8 til 9 cm over skjermkanten: set telefonen på ein kloss.',
            '     Lykta peikar opp mot midten av plata.',
            f'Stemning: sikt veggen bak skjermen, 60 cm over bordet. Plata om lag {b["stemning"]:.0f}° mot vassrett.',
            f'Arbeid: sikt feltmidten. Plata om lag {b["arbeid"]:.0f}°, nesten vassrett.',
            'Brønnen må skjerme ved 50°. Med 64° ser auget dioden frå 60 cm.']
    g.append(tekstblokk(m, 56, maal, 'brod'))
    x2 = m + (W - 2 * m) * 0.56
    g.append(t(x2, 50, 'BYGGING', 'mono'))
    steg = ['1  Skjer fire pappstrimlar, 20 mm breie: 2 × 315 mm og 2 × 275 mm.',
            '2  Teip dei på kanten av plata, 5 mm inn på plata. Rør ikkje rillene.',
            '3  Teip eit hengsel langs bakkanten til tverrstykket på stolpen.',
            '4  Klem stolpen bak skjermen.',
            '5  Rull brønnen (malen under) og set han rundt lykta.',
            '6  Prøv utan ark, med eitt og med to diffusorark på plata.',
            '7  Føreseiing: jamnheit 0,46 (0,35 til 0,55) med ark, under 0,05 utan.']
    g.append(tekstblokk(x2, 56, steg, 'brod'))
    g.append(roernett(m + 18, 128, BRONN_H, ['BRØNN · krage Ø 25 mm, ' + f'{BRONN_H:.1f}'.replace('.', ',') + ' mm høg, svart papp', 'gjev avskjerming ved 50° frå aksen']))
    g.append(t(m + 120, 132, 'RAMMA, SETT FRAMFRÅ (1:5)', 'mono'))
    s = 0.2; rx, ry = m + 120, 136
    g.append(rekt(rx, ry, 315 * s, 315 * s, 'tynn'))
    g.append(rekt(rx + 20 * s, ry + 20 * s, 275 * s, 275 * s, 'tynn'))
    g.append(f'<rect x="{rx + 15 * s:.2f}" y="{ry + 15 * s:.2f}" width="{285 * s:.2f}" height="{285 * s:.2f}" fill="none" stroke="#9a9a9a" stroke-dasharray="1 1" stroke-width="0.2"/>')
    g.append(t(rx + 315 * s + 4, ry + 8, 'ytre 315 × 315 mm', 'mono grå'))
    g.append(t(rx + 315 * s + 4, ry + 13, 'opning 275 × 275 mm', 'mono grå'))
    g.append(t(rx + 315 * s + 4, ry + 18, 'stipla: plata 285 × 285 mm', 'mono grå'))
    return ''.join(g)


def s_C(W, H):
    m = 12; c = V['C']
    g = [t(m, 30, 'C Vindauge: brennvidd, maske og plassering', 'tittel')]
    g.append(t(m, 38, 'Ei linse teiknar eit vindauge av lys på veggen. Ein spegel glir inn i strålen og legg feltet på bordet, medan vindauget blir.', 'ingress'))
    g.append(t(m, 50, 'MÅL BRENNVIDDA FØRST', 'mono'))
    br = ['Avbild eit vindauge eller ei lampe i andre enden av rommet på eit kvitt ark.',
          'Avstanden frå linsa til arket når biletet er skarpt, er om lag f.',
          'For glaskula: mål frå midten av kula. Ei vassfylt kule på Ø 70 mm har f om lag 70 mm.']
    g.append(tekstblokk(m, 56, br, 'brod'))
    g.append(t(m, 74, 'MASKA ETTER BRENNVIDDA · feltet 60 × 40 cm, 61 cm frå linsa', 'mono'))
    hy = 80
    for s_, dx in (('f, mm', 0), ('maske til linse, mm', 22), ('opning, mm', 64)):
        g.append(t(m + dx, hy, s_, 'mono grå'))
    for i, f in enumerate((50, 60, 70, 80, 100)):
        u, w, h = maske(f)
        y = hy + 5.5 * (i + 1)
        kl = 'brod svart' if f == 70 else 'brod'
        g.append(t(m, y, f'{f}', kl))
        g.append(t(m + 22, y, f'{u:.0f}', kl))
        g.append(t(m + 64, y, f'{w:.0f} × {h:.0f}', kl))
    g.append(t(m, hy + 39, 'Maska er eit rektangel her. Drei og trim ho til hjørna treffer feltet.', 'liten'))
    x2 = m + (W - 2 * m) * 0.56
    g.append(t(x2, 50, 'MÅL FRÅ MODELLEN', 'mono'))
    maal = ['Linsehovudet: 36 cm over bordet, 47 cm til høgre for skjermmidten,',
            '     5 cm framfor skjermplanet.',
            f'Utan spegel: sikt midt på veggen bak skjermen, 42 cm over bordet ({c["vegg"] / 10:.0f} cm unna).',
            f'Spegelen inne: om lag 3/4 av strålen går ned på feltmidten ({c["felt"] / 10:.0f} cm unna).',
            f'Strålen bøyer om lag {c["avbøying"]:.0f}° mellom vegg og felt.']
    g.append(tekstblokk(x2, 56, maal, 'brod'))
    g.append(t(x2, 86, 'BYGGING', 'mono'))
    steg = ['1  Skjer maska i svart papp (mal for f = 70 mm på neste side).',
            '2  Fald trakta, folie inni, og sett ho mellom lykta og maska.',
            '3  Set linsa i avstanden frå tabellen bak maska.',
            '4  Pappflik med frontflatespegelen rett etter linsa.',
            '     Flika vippar inn og dekkjer om lag 3/4 av strålen.',
            '5  Føreseiing: vindauget står i ro medan feltet kjem fram,',
            '     og skjermen får under 0,15 av feltet heile vegen.']
    g.append(tekstblokk(x2, 92, steg, 'brod'))
    return ''.join(g)


def trakt_nett(a1, b1, a2, b2, L):
    """Utfalda pyramidetrakt: smal ende a1 × b1, vid ende a2 × b2, lengd L. Gjev 2D-mangekantar (mm) og limflik."""
    N = [(-a1 / 2, -b1 / 2, 0), (a1 / 2, -b1 / 2, 0), (a1 / 2, b1 / 2, 0), (-a1 / 2, b1 / 2, 0)]
    Wd = [(-a2 / 2, -b2 / 2, L), (a2 / 2, -b2 / 2, L), (a2 / 2, b2 / 2, L), (-a2 / 2, b2 / 2, L)]
    N = [np.array(p, float) for p in N]; Wd = [np.array(p, float) for p in Wd]
    def plasser(A2, B2, dA, dB, ref):
        """Punkt med avstand dA til A2 og dB til B2, på motsett side av linja AB frå ref."""
        AB = B2 - A2; d = np.linalg.norm(AB); ex = AB / d; ey = np.array([-ex[1], ex[0]])
        x = (dA ** 2 - dB ** 2 + d ** 2) / (2 * d); y = math.sqrt(max(dA ** 2 - x ** 2, 0))
        P1 = A2 + x * ex + y * ey; P2 = A2 + x * ex - y * ey
        s = np.sign(np.cross(AB, ref - A2))
        return P1 if np.sign(np.cross(AB, P1 - A2)) != s else P2
    flater = []
    # første flata: N0 N1 W1 W0 i planet
    n0 = np.array([0.0, 0.0]); n1 = np.array([np.linalg.norm(N[1] - N[0]), 0.0])
    w1 = plasser(n0, n1, np.linalg.norm(Wd[1] - N[0]), np.linalg.norm(Wd[1] - N[1]), np.array([0.0, 1.0]))
    w0 = plasser(n1, w1, np.linalg.norm(Wd[0] - N[1]), np.linalg.norm(Wd[0] - Wd[1]), n0)
    # sørg for at w0 og w1 ligg på same side (positiv y)
    if w1[1] < 0: w1 = np.array([w1[0], -w1[1]]); w0 = np.array([w0[0], -w0[1]])
    flater.append([n0, n1, w1, w0])
    p = {('N', 0): n0, ('N', 1): n1, ('W', 1): w1, ('W', 0): w0}
    for k in (1, 2, 3):
        i, j = k, (k + 1) % 4
        A2, B2 = p[('N', i)], p[('W', i)]
        ref = flater[-1][0] if k > 1 else n0
        prev = flater[-1]
        refp = prev[0] if not np.allclose(prev[0], A2) else prev[3]
        nj = plasser(A2, B2, np.linalg.norm(N[j] - N[i]), np.linalg.norm(N[j] - Wd[i]), refp)
        wj = plasser(nj, B2, np.linalg.norm(Wd[j] - N[j]), np.linalg.norm(Wd[j] - Wd[i]), A2)
        flater.append([A2, nj, wj, B2])
        p[('N', j)] = nj; p[('W', j)] = wj
    # limflik på den siste frie kanten (N0-W0 på siste flata)
    A2, B2 = flater[-1][1], flater[-1][2]
    AB = B2 - A2; nrm = np.array([-AB[1], AB[0]]) / np.linalg.norm(AB)
    sentrum = np.mean(flater[-1], axis=0)
    if np.dot(nrm, sentrum - A2) > 0: nrm = -nrm
    flik = [A2, A2 + 8 * nrm + 0.12 * AB, B2 + 8 * nrm - 0.12 * AB, B2]
    return flater, flik


def s_C_malar(W, H):
    m = 12
    g = [t(m, 26, 'C Vindauge: maske og trakt for f = 70 mm', 'tittel')]
    u, w, h = maske(F_KULE)
    # maska
    ox, oy = m + 10, 44
    ytre_w, ytre_h = w + 40, h + 40
    g.append(rekt(ox, oy, ytre_w, ytre_h))
    g.append(rekt(ox + 20, oy + 20, w, h))
    g.append(maallinje(ox + 20, oy + 20 + h + 5, ox + 20 + w, oy + 20 + h + 5, f'{w:.0f} mm'))
    g.append(maallinje(ox + 20 + w + 5, oy + 20, ox + 20 + w + 5, oy + 20 + h, f'{h:.0f} mm'))
    g.append(tekstblokk(ox, oy + ytre_h + 8, ['MASKE · svart papp, skjer ut opninga',
                                              f'Maska {u:.0f} mm frå midten av glaskula (f 70 mm)'], 'mono', lh=4))
    # trakta
    flater, flik = trakt_nett(14.0, 10.0, w, h, 60.0)
    pts = np.concatenate([np.array(f) for f in flater] + [np.array(flik)])
    mn, mx = pts.min(0), pts.max(0)
    tx = ox + ytre_w + 30 - mn[0]; ty = 46 - mn[1]
    if mx[0] - mn[0] > W - (ox + ytre_w + 30) - m:
        s = 1.0
    for f in flater:
        d = 'M' + ' L'.join(f'{x + tx:.2f} {y + ty:.2f}' for x, y in f) + ' Z'
        g.append(f'<path d="{d}" class="fald-flate"/>')
    omriss = []
    # ytre omriss: kutt langs alle kantar som ikkje er delte
    for k, f in enumerate(flater):
        n_, nj, wj, w_ = f
        g.append(f'<line x1="{n_[0] + tx:.2f}" y1="{n_[1] + ty:.2f}" x2="{nj[0] + tx:.2f}" y2="{nj[1] + ty:.2f}" class="kuttlinje"/>')
        g.append(f'<line x1="{w_[0] + tx:.2f}" y1="{w_[1] + ty:.2f}" x2="{wj[0] + tx:.2f}" y2="{wj[1] + ty:.2f}" class="kuttlinje"/>')
        if k > 0:
            g.append(fald(n_[0] + tx, n_[1] + ty, w_[0] + tx, w_[1] + ty))
    f0 = flater[0]
    g.append(f'<line x1="{f0[0][0] + tx:.2f}" y1="{f0[0][1] + ty:.2f}" x2="{f0[3][0] + tx:.2f}" y2="{f0[3][1] + ty:.2f}" class="kuttlinje"/>')
    fl = flik
    g.append(f'<path d="M{fl[0][0] + tx:.2f} {fl[0][1] + ty:.2f} L{fl[1][0] + tx:.2f} {fl[1][1] + ty:.2f} L{fl[2][0] + tx:.2f} {fl[2][1] + ty:.2f} L{fl[3][0] + tx:.2f} {fl[3][1] + ty:.2f}" class="kutt"/>')
    g.append(fald(fl[0][0] + tx, fl[0][1] + ty, fl[3][0] + tx, fl[3][1] + ty))
    g.append(tekstblokk(tx + mn[0], ty + mx[1] + 8, ['TRAKT · papp med glatt folie på innsida',
                                                       f'smal ende 14 × 10 mm rundt lykta, vid ende {w:.0f} × {h:.0f} mm mot maska, 60 mm lang',
                                                       'heil strek: skjer · stipla: fald · limflik på 8 mm'], 'mono', lh=4))
    return ''.join(g)


def s_A3(W, H, nr, total):
    m = 12; R = D_SKIVE / 2
    g = [t(m, 26, 'A Skiva: heil skive, ribbe og papprull', 'tittel')]
    cx, cy = m + 20 + R, 40 + R
    g.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" class="kutt"/>')
    g.append(f'<line x1="{cx}" y1="{cy - R}" x2="{cx}" y2="{cy + R}" class="hjelp"/>')
    g.append(t(cx + 2, cy + R - 10, 'RIBBA her, på tvers av kastet', 'mono'))
    g.append(f'<circle cx="{cx}" cy="{cy}" r="1.2" fill="#000"/>')
    g.append(t(cx, cy - R - 3, f'SKIVE Ø {D_SKIVE:.0f} mm · papp med glatt aluminiumsfolie, blank side ut', 'mono', 'middle'))
    g.append(ribbemal(cx + R + 20 + 125 - 20, 70))
    g.append(roernett(cx + R + 40, 140, ROER_L, ['PAPPRULL Ø 25 × 100 MM, svart papp', 'stipla: fald, limflik på 8 mm']))
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
svg .ingress { font-size: 3.8px; fill: #333; }
svg .brod { font-size: 3.3px; }
svg .brod.svart { fill: #000; font-weight: 400; }
svg .kursiv { font-size: 4.2px; font-style: italic; }
svg .liten { font-size: 2.9px; fill: #555; }
svg .strek { stroke: #000; stroke-width: 0.25; }
svg .haar { stroke: #c8c8c8; stroke-width: 0.2; }
svg .kutt, svg .kuttlinje { fill: none; stroke: #000; stroke-width: 0.3; }
svg .tynn { fill: none; stroke: #000; stroke-width: 0.25; }
svg .fald { stroke: #000; stroke-width: 0.25; stroke-dasharray: 2 1.2; }
svg .fald-flate { fill: #f4f4f4; stroke: none; }
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
    print('vinklar', {k: {kk: (round(vv, 1) if isinstance(vv, float) else vv) for kk, vv in d.items() if kk != 'lykt'} for k, d in V.items()})
    print('pil', round(PIL, 2), 'brønn', round(BRONN_H, 2), 'maske f70', [round(x, 1) for x in maske(70)])
    n = skriv_stl(os.path.join(HER, 'ribbe_R1200_250mm.stl')); print('stl', n, 'trekantar')
    W, H = 297, 210
    lag = [lambda: s_oversikt(W, H), lambda: s_lobe_ark(W, H), lambda: s_lobe_kort(W, H, 18), lambda: s_A_plassering(W, H),
           lambda: s_A_malar_A4(W, H, 1), lambda: s_A_malar_A4(W, H, 2), lambda: s_B(W, H), lambda: s_C(W, H), lambda: s_C_malar(W, H)]
    tit = ['Oversikt', 'Lobebreidda', 'Målekortet', 'A Skiva', 'A Skiva, mal 1', 'A Skiva, mal 2', 'B Over', 'C Vindauge', 'C Vindauge, malar']
    sider = [side_svg(W, H, f(), tit[i], i + 1, len(lag)) for i, f in enumerate(lag)]
    hf = os.path.join(HER, 'byggjepakke-A4.html'); open(hf, 'w', encoding='utf-8').write(html(sider, W, H))
    skriv_pdf(hf, os.path.join(HER, 'byggjepakke-A4.pdf')); print('skrive byggjepakke-A4.pdf')
    W3, H3 = 420, 297
    sider3 = [side_svg(W3, H3, s_lobe_kort(W3, H3, 28), 'Målekortet', 1, 2), side_svg(W3, H3, s_A3(W3, H3, 2, 2), 'A Skiva, malar', 2, 2)]
    hf3 = os.path.join(HER, 'malar-A3.html'); open(hf3, 'w', encoding='utf-8').write(html(sider3, W3, H3))
    skriv_pdf(hf3, os.path.join(HER, 'malar-A3.pdf')); print('skrive malar-A3.pdf')
