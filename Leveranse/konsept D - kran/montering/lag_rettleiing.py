# -*- coding: utf-8 -*-
"""
lag_rettleiing.py  ·  monteringsrettleiing for Kran, teikna rett frå CAD-en (cad/kran.py)

  py -3 montering/lag_rettleiing.py         lagar montering/sider/*.png og montering/Kran-montering.pdf
  py -3 montering/lag_rettleiing.py 3 5     berre desse sidene

Strekteikningar med skjulte kantar fjerna (OCC HLR), svart på kvitt. ID-ane er dei same som i stykklista, DXF-filene
og printfilene, og beslaga er dei same formene som i kollisjonskontrollen. Tala for leddet (fjørkraft, vinkel på
bakmutteren, vektprøva) blir lesne frå kontroll/kran_kontroll.json, så rettleiinga følgjer CAD-en.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepLib import BRepLib
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Pnt2d

HER = Path(__file__).resolve().parent
ROT = HER.parent
sys.path.insert(0, str(ROT / 'cad'))
import kran as K                                                    # noqa: E402
from cadquery import Vector as V                                    # noqa: E402

SIDER = HER / 'sider'
DPI = 200
MM = DPI / 25.4
A4 = (int(210 * MM), int(297 * MM))                                 # ståande
REV = 'Kran · konsept D · rev. A · 25.11.2026'
KONTROLL = json.load(open(ROT / 'kontroll' / 'kran_kontroll.json', encoding='utf-8'))
LEDD = KONTROLL['ledd']

FH = ((0.62, -1.0, 0.62), (1.0, 0.62, 0.0))                         # framme til høgre, litt ovanfrå
FV = ((-0.62, -1.0, 0.55), (1.0, -0.62, 0.0))                       # framme til venstre
FRAMME = ((0.0, -1.0, 0.0), (1.0, 0.0, 0.0))
BAK = ((0.62, 1.0, 0.55), (-1.0, 0.62, 0.0))                        # bak til høgre
BV = ((-0.62, 1.0, 0.55), (-1.0, -0.62, 0.0))                       # bak til venstre
UNDER = ((0.55, -1.0, -0.75), (1.0, 0.55, 0.0))                     # framme til høgre, nedanfrå
SPV = ((-0.6, -0.72, 0.42), (0.72, -0.6, 0.0))                      # som sprengrendringa
FOTO = ((0.46, -0.887, 0.25), (0.887, 0.46, 0.0))                   # om lag som fotoet, litt ovanfrå
SVART = (0, 0, 0)


def font(pt, feit=False):
    for f in (('arialbd.ttf' if feit else 'arial.ttf'), 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(f, int(pt * DPI / 72))
        except OSError:
            pass
    return ImageFont.load_default()


class Vising:
    """Éi projeksjon av eit sett former; kantane blir polyliner i teikneplanet (mm)."""

    def __init__(s, former, retning=FH, glatte=False):
        syn, xr = retning
        s.proj = HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*syn), gp_Dir(*xr)))
        algo = HLRBRep_Algo()
        for f in former:
            algo.Add(f.wrapped)
        algo.Projector(s.proj)
        algo.Update()
        algo.Hide()
        h = HLRBRep_HLRToShape(algo)
        s.liner = []
        lag = [(1.0, h.VCompound()), (1.7, h.OutLineVCompound())] + ([(0.5, h.Rg1LineVCompound())] if glatte else [])
        for vekt, comp in lag:
            if comp is None or comp.IsNull():
                continue
            BRepLib.BuildCurves3d_s(comp)
            exp = TopExp_Explorer(comp, TopAbs_EDGE)
            while exp.More():
                c = BRepAdaptor_Curve(TopoDS.Edge_s(exp.Current()))
                d = GCPnts_QuasiUniformDeflection(c, 0.04)
                if d.IsDone() and d.NbPoints() > 1:
                    s.liner.append((vekt, [(d.Value(i).X(), d.Value(i).Y()) for i in range(1, d.NbPoints() + 1)]))
                exp.Next()
        P = np.array([p for _, pk in s.liner for p in pk])
        s.min, s.max = P.min(0), P.max(0)

    def punkt(s, p):
        q = gp_Pnt2d()
        s.proj.Project(gp_Pnt(*[float(c) for c in p]), q)
        return q.X(), q.Y()

    def teikn(s, dr, ramme, skala=None, tjukk=1.0):
        x0, y0, x1, y1 = ramme
        b = s.max - s.min
        k = min((x1 - x0) / b[0], (y1 - y0) / b[1]) if skala is None else skala * MM
        ox = x0 + ((x1 - x0) - b[0] * k) / 2
        oy = y0 + ((y1 - y0) - b[1] * k) / 2
        f = lambda p: (ox + (p[0] - s.min[0]) * k, oy + (s.max[1] - p[1]) * k)
        for vekt, pk in s.liner:
            dr.line([f(p) for p in pk], fill=SVART, width=max(1, int(round(vekt * tjukk * DPI / 150))), joint='curve')
        s.k = k / MM
        s.f = f
        return lambda p3: f(s.punkt(p3))


def bryt(dr, tekst, f, brei):
    liner, linje = [], ''
    for o in tekst.split():
        if linje and dr.textlength(linje + ' ' + o, font=f) > brei:
            liner.append(linje)
            linje = o
        else:
            linje = (linje + ' ' + o).strip()
    liner.append(linje)
    return liner


def side(nr, tal=None, tekst=None):
    im = Image.new('RGB', A4, (255, 255, 255))
    dr = ImageDraw.Draw(im)
    m = int(10 * MM)
    slutt = m + int(14 * MM)
    if tal is not None:
        dr.text((m, m), str(tal), font=font(54, True), fill=SVART)
        slutt = m + int(24 * MM)
    if tekst:
        f = font(13)
        x = m + (int(22 * MM) if tal is not None else 0)
        liner = bryt(dr, tekst, f, A4[0] - m - x)
        for i, l_ in enumerate(liner):
            dr.text((x, m + int(7 * MM) + i * int(6.2 * MM)), l_, font=f, fill=SVART)
        slutt = max(slutt, m + int(7 * MM) + len(liner) * int(6.2 * MM))
    fn = font(7.5)
    t = f'{REV} · {nr}'
    dr.text((A4[0] - m - dr.textlength(t, font=fn), A4[1] - m + int(3 * MM)), t, font=fn, fill=SVART)
    im.info['tekst_slutt'] = slutt
    return im, dr


def topp(im, luft=6):
    """Fyrste ledige y (pikslar) under teksten øvst på sida."""
    return im.info['tekst_slutt'] + int(luft * MM)


def ballong(dr, p, q, tekst, r=5.0):
    r = r * MM
    q = (min(max(q[0], 8 * MM + r), A4[0] - 8 * MM - r), min(max(q[1], 22 * MM + r), A4[1] - 14 * MM - r))
    dr.line([p, q], fill=SVART, width=2)
    dr.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=SVART)
    dr.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=(255, 255, 255), outline=SVART, width=3)
    f = font(10 if len(tekst) <= 3 else 8.5, True)
    w = dr.textlength(tekst, font=f)
    dr.text((q[0] - w / 2, q[1] - 0.52 * f.size), tekst, font=f, fill=SVART)


def ballongrad(dr, ankre, y, x0=None, x1=None, r=5.4, luft=2.2):
    """Ballongar på ei vassrett rad (y i pikslar), sorterte etter x for ankera og skyvne frå kvarandre."""
    x0 = 14 * MM if x0 is None else x0
    x1 = A4[0] - 14 * MM if x1 is None else x1
    ankre = sorted(ankre, key=lambda a: a[1][0])
    d = (2 * r + luft) * MM
    xs = [min(max(p[0], x0 + r * MM), x1 - r * MM) for _, p in ankre]
    for i in range(1, len(xs)):
        xs[i] = max(xs[i], xs[i - 1] + d)
    if xs and xs[-1] > x1 - r * MM:
        xs[-1] = x1 - r * MM
        for i in range(len(xs) - 2, -1, -1):
            xs[i] = min(xs[i], xs[i + 1] - d)
    for (tekst, p), x in zip(ankre, xs):
        ballong(dr, p, (x, y), tekst, r)


def pil(dr, a, b, tjukk=3, hol=False):
    """Rørslepil frå a til b (pikslar)."""
    a, b = np.array(a, float), np.array(b, float)
    v = b - a
    L_ = np.linalg.norm(v)
    if L_ < 1:
        return
    v /= L_
    n = np.array([-v[1], v[0]])
    s = 4.2 * MM
    dr.line([tuple(a), tuple(b - v * s * 0.8)], fill=SVART, width=tjukk)
    tri = [tuple(b), tuple(b - v * s + n * s * 0.42), tuple(b - v * s - n * s * 0.42)]
    dr.polygon(tri, fill=(255, 255, 255) if hol else SVART, outline=SVART)


def stipla(dr, a, b, strek=2.2, luft=1.6, w=2):
    a, b = np.array(a, float), np.array(b, float)
    L_ = np.linalg.norm(b - a)
    if L_ < 1:
        return
    v = (b - a) / L_
    t = 0.0
    while t < L_:
        dr.line([tuple(a + v * t), tuple(a + v * min(t + strek * MM, L_))], fill=SVART, width=w)
        t += (strek + luft) * MM


def stipla_line(dr, pts, w=3, strek=1.6, luft=1.2):
    for a, b in zip(pts, pts[1:]):
        stipla(dr, a, b, strek, luft, w)


def etikett(dr, xy, tekst, f=None, pad=0.8):
    """Tekst med kvit botn, så strekar under ikkje går gjennom bokstavane."""
    f = f or font(9)
    x, y = xy
    w = dr.textlength(tekst, font=f)
    p = pad * MM
    dr.rectangle([x - p, y - p * 0.6, x + w + p, y + f.size * 1.15 + p * 0.6], fill=(255, 255, 255))
    dr.text((x, y), tekst, font=f, fill=SVART)


def mengd(dr, p, tekst, storleik=12):
    etikett(dr, p, tekst, font(storleik, True))


def leiar(dr, p, q, tekst, f=None):
    """Tynn peikeline frå tekst (q) til punkt (p). Fleire liner med '\n'."""
    f = f or font(9)
    q = (min(max(q[0], 12 * MM), A4[0] - 12 * MM), min(max(q[1], 20 * MM), A4[1] - 16 * MM))
    dr.line([p, q], fill=SVART, width=2)
    dr.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=SVART)
    liner = tekst.split('\n')
    venstre = q[0] < p[0]
    tw = max(dr.textlength(l_, font=f) for l_ in liner)
    x = q[0] - tw - 1.5 * MM if venstre else q[0] + 1.5 * MM
    x = min(max(x, 10 * MM), A4[0] - 10 * MM - tw)
    for i, l_ in enumerate(liner):
        etikett(dr, (x, q[1] - 0.6 * f.size + i * f.size * 1.3), l_, f)


def skraver(im, poly, steg=14, w=3, omriss=True):
    """Skraver ein polygon (epoksy, maskering) med 45°-liner."""
    from PIL import ImageChops
    maske = Image.new('L', im.size, 0)
    ImageDraw.Draw(maske).polygon(poly, fill=255)
    monster = Image.new('L', im.size, 0)
    dm = ImageDraw.Draw(monster)
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    for c in range(int(x0 - (y1 - y0)) - steg, int(x1) + steg, steg):
        dm.line([(c, y1), (c + (y1 - y0), y0)], fill=255, width=w)
    im.paste(SVART, (0, 0, im.width, im.height), ImageChops.multiply(maske, monster))
    if omriss:
        ImageDraw.Draw(im).polygon(poly, outline=SVART, width=3)


def boble(im, sentrum, r, kjelde_ramme, kjelde_im, peik_fra=None):
    """Rund forstørringsboble: klipp ut eit utsnitt av kjelde_im og legg det i ein sirkel."""
    x0, y0, x1, y1 = [int(c) for c in kjelde_ramme]
    ut = kjelde_im.crop((x0, y0, x1, y1)).resize((int(2 * r), int(2 * r)), Image.LANCZOS)
    maske = Image.new('L', ut.size, 0)
    ImageDraw.Draw(maske).ellipse([0, 0, ut.size[0] - 1, ut.size[1] - 1], fill=255)
    im.paste(ut, (int(sentrum[0] - r), int(sentrum[1] - r)), maske)
    dr = ImageDraw.Draw(im)
    dr.ellipse([sentrum[0] - r, sentrum[1] - r, sentrum[0] + r, sentrum[1] + r], outline=SVART, width=4)


def sirkel3(P, c, r, akse='y', n=48):
    """Ein sirkel i 3D (normal langs akse) projisert til sida."""
    ut = []
    for t in np.linspace(0, 2 * math.pi, n, endpoint=False):
        if akse == 'y':
            p = (c[0] + r * math.cos(t), c[1], c[2] + r * math.sin(t))
        elif akse == 'z':
            p = (c[0] + r * math.cos(t), c[1] + r * math.sin(t), c[2])
        else:
            p = (c[0], c[1] + r * math.cos(t), c[2] + r * math.sin(t))
        ut.append(P(p))
    return ut


def tekstblokk(dr, x, y, brei, rader, ft=None, fs=None, innrykk=48):
    """Rader med (overskrift, tekst): overskrifta feit til venstre, teksten broten til høgre. Gjev y etter."""
    ft, fs = ft or font(10, True), fs or font(9)
    for t, s in rader:
        dr.text((x, y), t, font=ft, fill=SVART)
        liner = bryt(dr, s, fs, brei - innrykk * MM)
        for i, l_ in enumerate(liner):
            dr.text((x + innrykk * MM, y + i * int(4.6 * MM)), l_, font=fs, fill=SVART)
        y += max(1, len(liner)) * int(4.6 * MM) + int(3 * MM)
    return y


# ------------------------------------------------------------------ delane

print('Byggjer CAD-en', flush=True)
DELAR = K.bygg()
D = {pid: d['form'] for pid, d in DELAR.items()}
PROVE = K.leddprove()
LX, LZ = K.LEDD_X, K.LEDD_Z
SENTER_LEDD = (LX, 0.0, LZ)


def flytta(form, v):
    return form.translate(V(*v)) if any(v) else form


def sett(pids, flytt=None, kjelde=None):
    kjelde = kjelde or D
    flytt = flytt or {}
    return {p: flytta(kjelde[p], flytt.get(p, (0, 0, 0))) for p in pids}


def boks_senter(form):
    bb = form.BoundingBox()
    return ((bb.xmin + bb.xmax) / 2, (bb.ymin + bb.ymax) / 2, (bb.zmin + bb.zmax) / 2)


def utsnitt(form, x0=-1e3, x1=1e3, y0=-1e3, y1=1e3, z0=-1e3, z1=1e3):
    return form.intersect(K.boks(x0, x1, y0, y1, z0, z1)).clean()


SYNLEGE = ['D01', 'D02', 'D03', 'D04', 'D05', 'D06', 'D07', 'D08', 'D09', 'D10', 'D11', 'D12', 'D14',
           'M03-1', 'M03-2', 'D13-1', 'D13-2']
STATIV = ['D01', 'D02', 'D03']
FJOR = [f'M04-{i}' for i in range(1, 5)]
SPOR2 = (LX + 5.0 * math.cos(math.radians(-10)), sum(K.Y_DOBLAR) / 2, LZ + 5.0 * math.sin(math.radians(-10)))
SPOR1 = (LX + 5.0 * math.cos(math.radians(-60)), 0.0, LZ + 5.0 * math.sin(math.radians(-60)))
LED_START = K.LED_X0 + 2.0
LED_SLUTT = K.ARM_X1 - 9.0


# ------------------------------------------------------------------ sider

def s01_framside(nr):
    im, dr = side(nr)
    v = Vising([D[p] for p in SYNLEGE], FOTO)
    v.teikn(dr, (int(14 * MM), int(72 * MM), A4[0] - int(14 * MM), A4[1] - int(46 * MM)))
    dr.text((int(10 * MM), int(12 * MM)), 'KRAN', font=font(64, True), fill=SVART)
    dr.text((int(10 * MM), int(37 * MM)), 'Bordlampe med berøringsdimmar · 5 V USB-C', font=font(13), fill=SVART)
    dr.text((int(10 * MM), int(45 * MM)), 'Stativ i tre lag stål, arm i bøygd aluminium, lys under armen.',
            font=font(10), fill=SVART)
    return im


def celle(dr, ramme, form, pid, n, retning=FH):
    x0, y0, x1, y1 = [int(c) for c in ramme]
    Vising([form], retning).teikn(dr, (x0 + int(3 * MM), y0 + int(12 * MM), x1 - int(3 * MM), y1 - int(3 * MM)))
    f = font(9.5, True)
    dr.ellipse([x0 + int(1 * MM), y0, x0 + int(12 * MM), y0 + int(11 * MM)], outline=SVART, width=3)
    dr.text((x0 + int(6.5 * MM) - dr.textlength(pid, font=f) / 2, y0 + int(3.0 * MM)), pid, font=f, fill=SVART)
    dr.text((x0 + int(14 * MM), y0 + int(2.6 * MM)), f'×{n}', font=font(11, True), fill=SVART)


def rader_av_celler(dr, y, rader):
    """rader: liste av (overskrift, høgd mm, [(pid, tal, breiddevekt, form eller None, retning)])."""
    for tittel, h, celler in rader:
        dr.text((int(10 * MM), y), tittel, font=font(9.5, True), fill=SVART)
        y += int(6 * MM)
        sum_w = sum(c[2] for c in celler)
        x = 10 * MM
        brei = A4[0] - 20 * MM
        for pid, n, w, form, retn in celler:
            b = brei * w / sum_w
            celle(dr, (x, y, x + b - 2 * MM, y + h * MM), form if form is not None else D[pid], pid, n, retn)
            x += b
        y += int(h * MM) + int(3 * MM)
        dr.line([(int(10 * MM), y - int(1.5 * MM)), (A4[0] - int(10 * MM), y - int(1.5 * MM))], fill=SVART, width=1)
    return y


def s02_delar_1(nr):
    im, dr = side(nr, None, 'Delar 1/2: laserskore, printa og skore etter mal')
    y = topp(im, 2)
    rader_av_celler(dr, y, [
        ('Laserskore stål, S235 1,5 mm (D01 og D03 bøygde)', 66,
         [('D01', 1, 1, None, FH), ('D02', 1, 1, None, FH), ('D03', 1, 1, None, FH)]),
        ('Laserskore aluminium og rustfritt (same ordre)', 36,
         [('D04', 1, 3, None, FH), ('D05', 1, 1, None, FH), ('D06', 1, 0.8, None, FH)]),
        ('Printa i PETG, plate 1 (D11 og D14 svarte, resten lakka)', 38,
         [('D07', 1, 1, None, FH), ('D08', 1, 1, None, BAK), ('D09', 1, 1, None, FH), ('D10', 1, 1.6, None, UNDER),
          ('D11', 1, 1.5, None, BAK), ('D14', 1, 1.4, None, FH)]),
        ('Skore etter mal: opal PC 1,5 mm og møbelfilt 1 mm', 26,
         [('D12', 1, 3, None, FH), ('D13', 2, 1.2, D['D13-1'], FH)]),
    ])
    return im


def s03_delar_2(nr):
    im, dr = side(nr, None, 'Delar 2/2: elektronikk, beslag og verktøy')
    y = topp(im, 2)
    y = rader_av_celler(dr, y, [
        ('Elektronikk', 34, [('E01', 1, 2.6, None, FH), ('E02', 1, 1, None, FH), ('E03', 1, 1, None, FH),
                             ('E04', 1, 1, None, FH)]),
        ('Beslag', 36, [('M01', 1, 1, None, FH), ('M02', 2, 1, D['M02-1'], FH), ('M03', 2, 1, D['M03-1'], FH),
                        ('M04', 4, 1, D['M04-1'], FH), ('M05', 1, 1, None, FH)]),
    ])
    y += int(2 * MM)
    rader = [
        ('E01', 'COB-stripe 5 V, 8 mm, 2700 K, CRI ≥ 90, om lag 8 W/m, sjølvklebande. Kappa på merket næraste 343 mm.'),
        ('E02–E04', 'Seeed XIAO SAMD21 · AO3400A på SOT-23-kort med 100 Ω i gate og 100 kΩ frå gate til GND · '
                    'USB-C-kort, 6 pinnar, 5,1 kΩ frå CC1 og CC2 til GND.'),
        ('M01–M05', 'Holt gjengerøyr M10 × 1 i messing · 2 tynne lampemutrar M10 × 1, NV 13 · 2 nylonskiver '
                    '10,5 × 20 × 1 · 4 tallerkenfjører DIN 2093 C 20 × 10,2 × 0,5 · sylinderstift ISO 2338 Ø 3 m6 × 5.'),
        ('E05', 'Fire PTFE-leidningar, 750 mm kvar: AWG30 kvit (berøring) og svart (jord), AWG28 raud (LED +) '
                'og blå (LED −).'),
        ('M06–M09', 'Epoksy 2K (24 t) · koparteip med leiande lim og koparfolie · primer og silkematt lakk, '
                    'RAL 6021 som start · middels gjengelås · krympestrømpe · loddetinn · sparkel.'),
        ('Verktøy', 'Loddebolt · skyvelære · baufil og fil · Ø 9-bor eller -pinne · flattstang 13,8 mm · '
                    'tvinger og to rette plater · 2 fastnøklar 13 mm · tusj · maskeringstape · 40 g og 80 g lodd.'),
        ('Filer', 'Laser: produksjon/D01–D06_flat_*.dxf (1:1, bøyeliner på eige lag). Malar: D12_mal, D13_mal. '
                  'Print: print/KRAN_P1S_plate0 og plate1 (.gcode.3mf). Fastvare: fastvare/kran/kran.ino.'),
        ('Reserve', 'R01: viss berøringa ikkje blir stabil, potensiometer WH148 B10K med brytar og PWM-kort i lomma.'),
    ]
    tekstblokk(dr, int(10 * MM), y, A4[0] - int(20 * MM), rader, innrykk=26)
    return im


SPRENG = {
    'D04': (0, -95, 0), 'D05': (0, -73, 0), 'M05': (0, -51, 0), 'D09': (55, -95, 0), 'D10': (0, -95, -45),
    'E01': (0, -95, -45), 'D12': (0, -95, -80),
    'M02-1': (0, -150, 0), 'D07': (0, -185, 0), 'M01': (0, -235, 0), 'M03-1': (0, -42, 0),
    'D01': (0, -16, 0), 'D03': (0, 16, 0), 'D13-1': (0, -16, -30), 'D13-2': (0, 16, -30),
    'M03-2': (0, 40, 0), 'D06': (0, 58, 0), 'M04-1': (0, 77, 0), 'M04-2': (0, 84, 0), 'M04-3': (0, 91, 0),
    'M04-4': (0, 98, 0), 'M02-2': (0, 120, 0), 'D08': (0, 150, 0),
    'D11': (-175, 40, 0), 'E02': (-175, 40, 42), 'E03': (-175, 40, 42), 'E04': (-175, 40, 42), 'D14': (-175, 40, 80),
}


def s04_oversikt(nr):
    im, dr = side(nr, None, 'Oversikt')
    S = sett(list(D), SPRENG)
    v = Vising(list(S.values()), SPV)
    P = v.teikn(dr, (int(10 * MM), topp(im, 30), A4[0] - int(10 * MM), A4[1] - int(46 * MM)))
    lab = lambda p: p.split('-')[0] if p != 'E02' else 'E02–4'
    anker = lambda p: P(boks_senter(S[p]))
    bak = ['D08', 'M02-2', 'M04-2', 'D06', 'M03-2']
    ballongrad(dr, [(lab(p), anker(p)) for p in bak], topp(im, 14), x1=A4[0] * 0.45)
    fram = ['M03-1', 'D05', 'M05', 'D10', 'M02-1', 'D07', 'M01', 'E01', 'D12']
    yb = max(anker(p)[1] for p in fram) + 26 * MM
    ballongrad(dr, [(lab(p), anker(p)) for p in fram], yb, x0=A4[0] * 0.36)
    for pid, (dx, dy) in {'D01': (-22, 20), 'D02': (-28, -6), 'D03': (24, 30), 'D04': (14, -22), 'D09': (12, -14),
                          'D11': (-12, 16), 'D14': (-12, -12), 'D13-1': (-16, 14), 'E02': (-16, -4)}.items():
        p = anker(pid)
        ballong(dr, p, (p[0] + dx * MM, p[1] + dy * MM), lab(pid), r=5.4)
    return im


def s05_prove(nr):
    sp = {'M01': (0, -112, 0), 'M02-1': (0, -82, 0), 'P05': (0, -62, 0), 'P04': (0, -46, 0), 'M05': (0, -46, 0),
          'M03-1': (0, -28, 0), 'P01': (0, -12, 0), 'P02': (0, 0, 0), 'P03': (0, 12, 0), 'M03-2': (0, 27, 0),
          'P06': (0, 40, 0), 'M04-1': (0, 52, 0), 'M04-2': (0, 57, 0), 'M04-3': (0, 62, 0), 'M04-4': (0, 67, 0),
          'M02-2': (0, 86, 0)}
    kjelde = dict(D)
    kjelde.update(PROVE)
    S = sett(list(sp), sp, kjelde)
    im, dr = side(nr, 0, 'Før laserordren: print plate 0 (leddprøva) og set ho saman med dei kjøpte beslaga og dei fire '
                         'leidningane, som i steg 1, 2, 9 og 10. Rør armen 100 gonger mellom stoppane. Leidningane skal '
                         'gli fritt i kammeret, stoppinnen skal ta i begge endane av bogesporet, og D-hola skal sitje '
                         'utan slark på den flate sida. Mål beslaga og rett parametrane i cad/kran.py før du bestiller.')
    v = Vising(list(S.values()), FH)
    P = v.teikn(dr, (int(12 * MM), topp(im, 6), A4[0] - int(12 * MM), A4[1] - int(30 * MM)))
    plass = {'M01': (-10, -16), 'M02-1': (-8, -18), 'P05': (-22, -14), 'P04': (-16, 18), 'M05': (10, -18),
             'M03-1': (30, 34), 'P01': (-30, 8), 'P02': (24, 22), 'P03': (14, 22), 'M03-2': (12, -16),
             'P06': (10, 18), 'M04-2': (6, -18), 'M02-2': (14, 14)}
    for pid, (dx, dy) in plass.items():
        p = P(boks_senter(S[pid]))
        ballong(dr, p, (p[0] + dx * MM, p[1] + dy * MM), pid.split('-')[0], r=5.2)
    a, b = P((LX, -125, LZ)), P((LX, 100, LZ))
    stipla(dr, a, b, w=2)
    for i, l_ in enumerate(bryt(dr, 'P01–P06: print/KRAN_P1S_plate0_leddprove_PETG.gcode.3mf (0,16 mm lag, 41 min). '
                                'Laga er printa i same tjukkleik som stålet og aluminiumen.', font(9),
                                A4[0] - int(24 * MM))):
        dr.text((int(12 * MM), A4[1] - int(28 * MM) + i * int(4.6 * MM)), l_, font=font(9), fill=SVART)
    return im


def s06_aksel(nr):
    im, dr = side(nr, 1, 'Kapp akselen til 23,0 mm. Fil den flate sida til 9,0 mm over heile lengda, målt frå flata til '
                         'botnen av gjengene. Lag to tverrspor, 2 × 2 mm, gjennom veggen inn til boringa: det midtre '
                         '11,0 mm frå framenden, det fremre 6,25 mm frå framenden. Avgrad inni og fôr spora med '
                         'krympestrømpe.')
    a = D['M01']
    v = Vising([a], FH)
    y0 = topp(im, 8)
    P = v.teikn(dr, (int(16 * MM), y0, int(140 * MM), y0 + int(120 * MM)))
    yf, yb = K.Y_AKSEL
    leiar(dr, P((LX, yf, LZ + 4.5)), (P((LX, yf, LZ + 4.5))[0] - 10 * MM, P((LX, yf, LZ + 4.5))[1] - 12 * MM),
          'framenden')
    pf = P((LX, 4.0, LZ + 4.0))
    leiar(dr, pf, (pf[0] + 18 * MM, pf[1] - 16 * MM), 'flat: 9,0 mm\nfrå botnen av gjengene')
    p1 = P(SPOR1)
    leiar(dr, p1, (p1[0] + 30 * MM, p1[1] + 10 * MM), 'midtre spor 2 × 2, på undersida\n11,0 mm frå framenden')
    p2 = P(SPOR2)
    leiar(dr, p2, (p2[0] + 8 * MM, p2[1] + 30 * MM), 'fremre spor 2 × 2\n6,25 mm frå framenden')
    pl = P((LX - 3.0, (yf + yb) / 2, LZ + 4.0))
    leiar(dr, pl, (pl[0] - 34 * MM, pl[1] - 12 * MM), 'lengd 23,0 mm', font(10, True))
    # endevising framanfrå: flata kl. 12, spora mot armen (kl. 3) og ned
    ve = Vising([a], FRAMME)
    y1 = y0 + int(128 * MM)
    Pe = ve.teikn(dr, (int(30 * MM), y1, int(110 * MM), A4[1] - int(26 * MM)))
    c = Pe((LX, yf, LZ))
    for vinkel, tekst in ((-60.0, 'midtre spor, 60° ned'), (-10.0, 'fremre spor, 10° ned')):
        r = 7.2
        q = Pe((LX + r * math.cos(math.radians(vinkel)), yf, LZ + r * math.sin(math.radians(vinkel))))
        pil(dr, c, q, tjukk=3)
        etikett(dr, (q[0] + 2 * MM, q[1] - 2 * MM), tekst, font(9))
    etikett(dr, (Pe((LX - 5.5, yf, LZ + 5.5))[0], Pe((LX, yf, LZ + 5.5))[1] - 8 * MM), 'sett framanfrå', font(9, True))
    pil(dr, Pe((LX + 5.6, yf, LZ + 5.0)), Pe((LX + 7.6, yf, LZ + 5.0)), tjukk=3, hol=True)
    etikett(dr, (Pe((LX + 7.6, yf, LZ + 5.0))[0] + 2 * MM, Pe((LX + 7.6, yf, LZ + 5.0))[1] - 2.5 * MM), 'armen',
            font(9))
    return im


def s07_leidningar(nr):
    im, dr = side(nr, 2, 'Kapp dei fire leidningane til 750 mm. Legg dei utvinna i kanalen i midtlaget D02, frå vindauget '
                         'og opp til kammeret. La 120 mm stikke ut ved vindauget. Legg ei slakk sløyfe på om lag 15 mm '
                         'i kammeret, før dei inn i det midtre sporet og fram gjennom akselen: kvit og svart ut framenden, '
                         'raud og blå ut det fremre sporet.')
    v = Vising([D['D02'], D['M01']], FRAMME)
    y0 = topp(im, 4)
    P = v.teikn(dr, (int(10 * MM), y0, int(120 * MM), A4[1] - int(18 * MM)))
    _, (p0, p1, p2) = K.kanal_xz()
    bane = [P((p0[0], -1.0, p0[1])), P((p1[0], -1.0, p1[1])), P((p2[0], -1.0, p2[1]))]
    # sløyfa i kammeret
    slo = []
    for t in np.linspace(0, 1.75 * 2 * math.pi, 60):
        r = 7.0 - 1.4 * t / (2 * math.pi)
        a_ = math.radians(-73) + t
        slo.append(P((LX + r * math.cos(a_), -1.0, LZ + r * math.sin(a_))))
    dr.line(bane + slo, fill=SVART, width=9, joint='curve')
    dr.line(bane + slo, fill=(255, 255, 255), width=4, joint='curve')
    pv = P((p0[0], -1.0, p0[1]))
    leiar(dr, pv, (pv[0] - 6 * MM, pv[1] - 26 * MM), 'vindauget:\n120 mm ut bak')
    pk = P((LX, -1.0, LZ - 8.5))
    leiar(dr, pk, (pk[0] + 34 * MM, pk[1] + 20 * MM), 'sløyfe 15 mm i kammeret,\ninn i det midtre sporet')
    pm = P(((p1[0] + p2[0]) / 2, -1.0, (p1[1] + p2[1]) / 2))
    leiar(dr, pm, (pm[0] + 24 * MM, pm[1] - 40 * MM), 'kanalen, 3,4 brei')
    # snitt gjennom kanalen: rekkjefølgja
    x0, y_ = int(134 * MM), int(162 * MM)
    k = 9 * MM
    dr.rectangle([x0, y_, x0 + 3.4 * k, y_ + 1.5 * k], outline=SVART, width=3)
    namn = [('kvit', 'berøring'), ('svart', 'jord'), ('raud', 'LED +'), ('blå', 'LED −')]
    for i, (farge, kva) in enumerate(namn):
        cx = x0 + (0.42 + i * 0.85) * k
        dr.ellipse([cx - 0.36 * k, y_ + 0.39 * k, cx + 0.36 * k, y_ + 1.11 * k], outline=SVART, width=3,
                   fill=SVART if farge == 'svart' else (255, 255, 255))
        dr.line([(cx, y_ + 1.5 * k), (cx, y_ + 1.5 * k + (6 + 7 * i) * MM)], fill=SVART, width=2)
        etikett(dr, (cx + 1.2 * MM, y_ + 1.5 * k + (3.6 + 7 * i) * MM), f'{kva} ({farge})', font(9))
    dr.text((x0, y_ - int(7 * MM)), 'Snitt gjennom kanalen', font=font(9.5, True), fill=SVART)
    # akselen med leidningane
    va = Vising([D['M01']], FH)
    Pa = va.teikn(dr, (int(128 * MM), int(212 * MM), A4[0] - int(14 * MM), A4[1] - int(24 * MM)))
    yf = K.Y_AKSEL[0]
    inn = Pa(SPOR1)
    stipla_line(dr, [Pa((LX + 9 * math.cos(math.radians(-60)), 0, LZ + 9 * math.sin(math.radians(-60)))), inn,
                     Pa((LX, 0, LZ)), Pa((LX, yf, LZ))], w=4)
    dr.line([Pa((LX, yf, LZ)), Pa((LX - 1, yf - 9, LZ + 2))], fill=SVART, width=4)
    ut2 = Pa(SPOR2)
    dr.line([ut2, Pa((LX + 13, SPOR2[1], LZ - 2.5))], fill=SVART, width=4)
    etikett(dr, (Pa((LX - 1, yf - 9, LZ + 2))[0] - 30 * MM, Pa((LX - 1, yf - 9, LZ + 2))[1] - 6 * MM), 'kvit og svart', font(9))
    etikett(dr, (Pa((LX + 13, SPOR2[1], LZ - 2.5))[0] + 1 * MM, Pa((LX + 13, SPOR2[1], LZ - 2.5))[1] - 2 * MM),
            'raud og blå', font(9))
    return im


def s08_laminering(nr):
    sp = {'D01': (0, -55, 0), 'D02': (0, 0, 0), 'D03': (0, 55, 0)}
    S = sett(STATIV, sp)
    stang = K.prisme_y(K.stadion_xz(K.SPALTE_1, K.SPALTE_2, K.SPALTE_B / 2 - 0.1), -75, 75)
    im, dr = side(nr, 3, 'Smør eit tunt, jamt lag epoksy på begge sider av D02, men ikkje i kanalen og kammeret. Legg laga '
                         'saman på akselen og ei flattstang på 13,8 mm i spalta, så kantane ligg i flukt. Press mellom to '
                         'rette plater med tvinger, over bøyane, og la herde i 24 timar. Snu akselen nokre gonger den '
                         'første timen, så han ikkje limer seg fast.')
    v = Vising(list(S.values()) + [D['M01'], stang], FH)
    P = v.teikn(dr, (int(12 * MM), topp(im, 6), A4[0] - int(12 * MM), A4[1] - int(22 * MM)))
    for pid, (dx, dy) in {'D01': (-26, 10), 'D02': (-10, 30), 'D03': (24, 10)}.items():
        p = P(boks_senter(S[pid]))
        ballong(dr, p, (p[0] + dx * MM, p[1] + dy * MM), pid, r=5.6)
    for y_, retn in ((-55 - 40, 1), (55 + 40, -1)):
        a = P((95, y_, 160))
        b = P((95, y_ + retn * 34, 160))
        pil(dr, a, b, tjukk=6)
    q = P((95, -95, 160))
    etikett(dr, (q[0] - 30 * MM, q[1] + 3 * MM), 'tvinge', font(10, True))
    ps = P((K.SPALTE_1[0], 70, K.SPALTE_1[1]))
    leiar(dr, ps, (ps[0] + 26 * MM, ps[1] + 14 * MM), 'flattstang 13,8 mm i spalta')
    pa = P((LX, 40, LZ))
    leiar(dr, pa, (pa[0] + 18 * MM, pa[1] - 14 * MM), 'akselen med leidningane: snu han\nmedan epoksyen er open')
    pe = P((110, 0, 200))
    leiar(dr, pe, (pe[0] - 46 * MM, pe[1] - 34 * MM), 'epoksy på begge sider av D02,\nikkje i kanalen og kammeret')
    return im


def s09_forsterking(nr):
    im, dr = side(nr, 4, 'Press stoppinnen M05 inn i forsterkingsplata D05 frå framsida til han er i flukt; han stikk '
                         '2 mm ut bak. Smør tunt med epoksy på framsida av D05. Skyv plata inn bak øyret frå leddenden, '
                         'med tunga inn i profilen langs framflensen, og rett inn D-hola med eit Ø 9-bor. Klem og la '
                         'herde i 24 timar. Hald sporet for leidningane reint.')
    y0 = topp(im, 4)
    # 1: stoppinnen i forsterkingsplata
    pin = flytta(D['M05'], (0, -16, 0))
    v1 = Vising([D['D05'], pin], FH)
    P1 = v1.teikn(dr, (int(12 * MM), y0, int(98 * MM), y0 + int(76 * MM)))
    px, pz = K.stopp_pkt()
    pil(dr, P1((px, -30, pz)), P1((px, -21.5, pz)))
    q = P1((px, -16, pz))
    leiar(dr, q, (q[0] - 4 * MM, q[1] - 14 * MM), 'M05: press inn til flukt')
    ps = P1((K.ARM_X0 + 12, K.Y_DOBLAR[0], LZ - 3.5))
    leiar(dr, ps, (ps[0] + 6 * MM, ps[1] + 16 * MM), 'sporet for leidningane:\nhald det reint')
    p5 = P1(boks_senter(D['D05']))
    ballong(dr, p5, (p5[0] - 18 * MM, p5[1] + 18 * MM), 'D05')
    # 2: plata skyvd inn bak øyret, sett bakfrå
    arm = utsnitt(D['D04'], x1=262)
    d5 = flytta(D['D05'], (-42, 0, 0))
    v2 = Vising([arm, d5], BV)
    P2 = v2.teikn(dr, (int(30 * MM), y0 + int(84 * MM), A4[0] - int(12 * MM), A4[1] - int(22 * MM)))
    a = P2((K.ARM_X0 - 30, K.Y_DOBLAR[1] + 8, LZ - 2))
    b = P2((K.ARM_X0 + 6, K.Y_DOBLAR[1] + 8, LZ - 2))
    pil(dr, a, b, tjukk=5)
    p5 = P2(boks_senter(d5))
    ballong(dr, p5, (p5[0] - 16 * MM, p5[1] - 22 * MM), 'D05')
    p4 = P2((230, K.ARM_Y1, K.ARM_TOPP))
    ballong(dr, p4, (p4[0] + 4 * MM, p4[1] - 16 * MM), 'D04')
    pt = P2((K.ARM_X0 + 4, K.Y_DOBLAR[1], LZ - 2))
    leiar(dr, pt, (pt[0] + 6 * MM, pt[1] + 26 * MM), 'tunga går inn i profilen\nlangs innsida av framflensen')
    pd = P2((LX, K.Y_DOBLAR[1], LZ))
    leiar(dr, pd, (pd[0] - 20 * MM, pd[1] + 30 * MM), 'Ø 9-bor gjennom\nbegge D-hola')
    return im


def s10_lakk(nr):
    im, dr = side(nr, 5, 'Slip kantane flate, sparkle laminatlinjene og runde av med R 0,5. Maskér det skraverte: '
                         'ein ring Ø 28 framme rundt leddet med bogesporet, ein ring Ø 24 bak, vindauget bak (jord), '
                         'ein ring Ø 15 framme på øyret og innsida av D-hola. Pakk akselen og leidningane i tape. '
                         'Grunn og lakk to til tre strøk silkematt. Lakk stativet, armen, D07, D08, D09 og D10 i same '
                         'økt, frå same boks; prøv fargen mot fotoet først.')
    y0 = topp(im, 4)
    # 1: stativet framanfrå
    S = [D[p] for p in STATIV] + [D['M01']]
    v1 = Vising(S, FH)
    P1 = v1.teikn(dr, (int(10 * MM), y0, int(104 * MM), A4[1] - int(30 * MM)))
    skraver(im, sirkel3(P1, (LX, K.Y_PL0 - 0.01, LZ), 14.0), steg=10, w=2)
    ImageDraw.Draw(im).ellipse([P1((LX, K.Y_PL0, LZ))[0] - 3, P1((LX, K.Y_PL0, LZ))[1] - 3,
                                P1((LX, K.Y_PL0, LZ))[0] + 3, P1((LX, K.Y_PL0, LZ))[1] + 3], fill=SVART)
    q = P1((LX - 14, K.Y_PL0, LZ))
    leiar(dr, q, (q[0] - 4 * MM, q[1] + 22 * MM), 'Ø 28 framme,\nmed bogesporet')
    # 2: stativet bakfrå
    v2 = Vising([D[p] for p in STATIV], BAK)
    P2 = v2.teikn(dr, (int(112 * MM), y0, A4[0] - int(12 * MM), y0 + int(120 * MM)))
    skraver(im, sirkel3(P2, (LX, K.Y_PL1 + 0.01, LZ), 12.0), steg=10, w=2)
    vi = K.VINDAUGE
    skraver(im, [P2((vi[0], K.Y_PL1, vi[2])), P2((vi[1], K.Y_PL1, vi[2])), P2((vi[1], K.Y_PL1, vi[3])),
                 P2((vi[0], K.Y_PL1, vi[3]))], steg=8, w=2)
    q = P2((LX, K.Y_PL1, LZ - 12))
    leiar(dr, q, (q[0] + 8 * MM, q[1] + 16 * MM), 'Ø 24 bak')
    q = P2(((vi[0] + vi[1]) / 2, K.Y_PL1, vi[3]))
    leiar(dr, q, (q[0] + 10 * MM, q[1] - 18 * MM), 'vindauget: jord')
    # 3: øyret framanfrå
    arm = [utsnitt(D['D04'], x1=250), D['D05']]
    v3 = Vising(arm, FH)
    P3 = v3.teikn(dr, (int(116 * MM), y0 + int(128 * MM), A4[0] - int(12 * MM), A4[1] - int(30 * MM)))
    skraver(im, sirkel3(P3, (LX, K.ARM_Y0 - 0.01, LZ), 7.5), steg=8, w=2)
    q = P3((LX + 7.5, K.ARM_Y0, LZ - 2))
    leiar(dr, q, (q[0] + 12 * MM, q[1] + 20 * MM), 'Ø 15 på øyret og\ninnsida av D-hola')
    return im


def boks2d(dr, x, y, b, h, tittel, venstre=(), hogre=(), under=None):
    X = lambda v_: int(v_ * MM)
    dr.rectangle([X(x), X(y), X(x + b), X(y + h)], outline=SVART, width=4)
    dr.text((X(x + 2.5), X(y + 2)), tittel, font=font(10, True), fill=SVART)
    if under:
        liner = under.split('\n')
        for i, l_ in enumerate(liner):
            dr.text((X(x + 2.5), X(y + h - 2 - 4.2 * (len(liner) - i))), l_, font=font(8), fill=SVART)
    pins = {}
    f = font(9)
    for namn, dy in venstre:
        p = (X(x), X(y + dy))
        dr.ellipse([p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7], fill=SVART)
        dr.text((p[0] + 12, p[1] - 15), namn, font=f, fill=SVART)
        pins[namn] = p
    for namn, dy in hogre:
        p = (X(x + b), X(y + dy))
        dr.ellipse([p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7], fill=SVART)
        dr.text((p[0] - 12 - dr.textlength(namn, font=f), p[1] - 15), namn, font=f, fill=SVART)
        pins[namn] = p
    return pins


def leid(dr, pts, w=4, stipla_=False):
    q = [(int(a * MM), int(b * MM)) for a, b in pts]
    if stipla_:
        stipla_line(dr, q, w=w)
    else:
        dr.line(q, fill=SVART, width=w, joint='curve')


def mm(p):
    return (p[0] / MM, p[1] / MM)


def jordsymbol(dr, x, y, tekst=None):
    X = lambda v_: int(v_ * MM)
    dr.line([(X(x), X(y)), (X(x), X(y + 3))], fill=SVART, width=4)
    for i, b in enumerate((4.0, 2.6, 1.2)):
        yy = y + 3 + i * 1.3
        dr.line([(X(x - b), X(yy)), (X(x + b), X(yy))], fill=SVART, width=4)
    if tekst:
        dr.text((X(x + 5), X(y + 2.5)), tekst, font=font(8.5), fill=SVART)


def s11_kopling(nr):
    im, dr = side(nr, 6, 'Kopling. Lodd etter skjemaet. Dei fire leidningane frå vindauget går gjennom leddet: kvit til '
                         'knotten, svart til akselen, raud og blå til lyslista. XIAO-en får straum på 5V-pinnen: kople '
                         'aldri USB-en på XIAO-en til medan lampa står i straum.')
    y0 = topp(im, 2) / MM + 26
    usb = boks2d(dr, 10, y0, 32, 66, 'E04 USB-C', hogre=[('VBUS', 14), ('CC1', 26), ('CC2', 36), ('GND', 50)],
                 under='5,1 kΩ frå\nCC1 og CC2\ntil GND')
    xiao = boks2d(dr, 62, y0, 36, 62, 'E02 XIAO', venstre=[('5V', 14), ('A4', 26), ('A5', 36), ('GND', 50)],
                  hogre=[('A1', 20), ('A2', 44)], under='SAMD21')
    mos = boks2d(dr, 112, y0 + 30, 30, 36, 'E03', venstre=[('G', 14)], hogre=[('D', 8), ('S', 26)],
                 under='AO3400A')
    for a, b in (('VBUS', '5V'), ('CC1', 'A4'), ('CC2', 'A5'), ('GND', 'GND')):
        leid(dr, [mm(usb[a]), mm(xiao[b])])
    leid(dr, [mm(xiao['A2']), mm(mos['G'])])
    yj = y0 + 82
    leid(dr, [(52, y0 + 50), (52, yj)])
    s_ = mm(mos['S'])
    leid(dr, [s_, (148, s_[1]), (148, yj)])
    leid(dr, [(10, yj), (198, yj)], w=5)
    for x_ in (52, 148):
        dr.ellipse([int(x_ * MM) - 8, int(yj * MM) - 8, int(x_ * MM) + 8, int(yj * MM) + 8], fill=SVART)
    dr.text((int(12 * MM), int((yj - 6) * MM)), 'GND', font=font(9, True), fill=SVART)
    # lyslista øvst til høgre
    lx0, lx1, ly = 160, 196, y0 + 2
    dr.rectangle([int(lx0 * MM), int(ly * MM), int(lx1 * MM), int((ly + 8) * MM)], outline=SVART, width=4)
    for i in range(5):
        xx = lx0 + 6 + i * 5.6
        dr.rectangle([int(xx * MM), int((ly + 2.5) * MM), int((xx + 3) * MM), int((ly + 5.5) * MM)], fill=SVART)
    dr.text((int(lx0 * MM), int((ly - 7) * MM)), 'E01 lyslista', font=font(9.5, True), fill=SVART)
    dr.text((int((lx0 + 1) * MM), int((ly + 9) * MM)), '+', font=font(12, True), fill=SVART)
    dr.text((int((lx1 - 4) * MM), int((ly + 9) * MM)), '−', font=font(12, True), fill=SVART)
    leid(dr, [(52, y0 + 14), (52, y0 - 6), (163, y0 - 6), (163, ly)])
    dr.ellipse([int(52 * MM) - 8, int((y0 + 14) * MM) - 8, int(52 * MM) + 8, int((y0 + 14) * MM) + 8], fill=SVART)
    d_ = mm(mos['D'])
    leid(dr, [d_, (193, d_[1]), (193, ly + 8)])
    etikett(dr, (int(118 * MM), int((y0 - 10.5) * MM)), 'raud, LED +', font(8.5))
    etikett(dr, (int(194.5 * MM), int((y0 + 24) * MM)), 'blå', font(8.5))
    # knotten
    kx, ky = 178, y0 + 20
    leid(dr, [mm(xiao['A1']), (kx - 6, ky)])
    dr.ellipse([int((kx - 6) * MM), int((ky - 6) * MM), int((kx + 6) * MM), int((ky + 6) * MM)], outline=SVART, width=4)
    dr.text((int((kx - 14) * MM), int((ky + 7) * MM)), 'folie Ø 11\ni knotten', font=font(8.5), fill=SVART)
    etikett(dr, (int(126 * MM), int((ky - 5.5) * MM)), 'kvit, berøring', font(8.5))
    # jord
    leid(dr, [(30, yj), (30, yj + 10)])
    jordsymbol(dr, 30, yj + 10, 'koparteip på stålet i vindauget')
    leid(dr, [(170, yj), (170, yj + 10)])
    jordsymbol(dr, 170, yj + 10)
    dr.text((int(158 * MM), int((yj + 17) * MM)), 'svart: akselen,\nøyret og armen', font=font(8.5), fill=SVART)
    for x_ in (30, 170):
        dr.ellipse([int(x_ * MM) - 8, int(yj * MM) - 8, int(x_ * MM) + 8, int(yj * MM) + 8], fill=SVART)
    # grensa: det som går gjennom leddet
    xg = 154
    leid(dr, [(xg, y0 - 14), (xg, yj + 30)], w=2, stipla_=True)
    dr.text((int((xg - 22) * MM), int((yj + 26) * MM)), 'i lomma', font=font(8.5, True), fill=SVART)
    dr.text((int((xg + 2) * MM), int((yj + 26) * MM)), 'gjennom leddet', font=font(8.5, True), fill=SVART)
    yt = yj + 40
    rader = [('A1', 'berøring (QTouch): kvit leidning til folien i knotten'),
             ('A2', 'PWM 20 kHz til gate på MOSFET-kortet (100 Ω i serie, 100 kΩ til GND)'),
             ('A4, A5', 'CC1 og CC2: kor mykje straum ladaren lovar; standard USB gjev 75 % lys'),
             ('5V, GND', 'frå USB-C-kortet. Lyslista får VBUS direkte; minus går gjennom MOSFET-en (D), S til GND'),
             ('Fastvare', 'fastvare/kran/kran.ino: Arduino IDE, kortpakka Seeed SAMD (XIAO), biblioteka '
                          'Adafruit FreeTouch og FlashStorage. Ved oppstart blinkar lyset kort medan krysstalen blir målt.')]
    tekstblokk(dr, int(12 * MM), int(yt * MM), A4[0] - int(24 * MM), rader, innrykk=24)
    return im


def s12_lomma(nr):
    lx0, lx1, ly0, ly1, lz0, lz1 = K.lomme_y()
    sp = {'D11': (0, 70, 0), 'E02': (0, 70, 46), 'E03': (0, 70, 46), 'E04': (0, 70, 46), 'D14': (0, 70, 92)}
    S = sett(list(sp), sp)
    stativ = [utsnitt(D[p], z1=130) for p in STATIV]
    im, dr = side(nr, 7, 'Lim koparteip på det blanke stålet i vindauget og lodd ein svart leidning frå GND til teipen. '
                         'Lodd kortet etter skjemaet. Last opp fastvare/kran/kran.ino med USB-en på XIAO-en, utan straum '
                         'på USB-C-kortet. Prøv med ei kort LED-list på raud og blå ved leddet: lyset blinkar ved oppstart, '
                         'og den kvite leidningen slår av og på. Lim lomma på bakflensen med opninga mot vindauget. '
                         'Klikk på loket.')
    v = Vising(stativ + list(S.values()), BAK)
    P = v.teikn(dr, (int(12 * MM), topp(im, 4), A4[0] - int(12 * MM), A4[1] - int(20 * MM)))
    vi = K.VINDAUGE
    skraver(im, [P((vi[0] + 1, K.Y_PL1, vi[2] + 1)), P((vi[1] - 1, K.Y_PL1, vi[2] + 1)), P((vi[1] - 1, K.Y_PL1, vi[3] - 1)),
                 P((vi[0] + 1, K.Y_PL1, vi[3] - 1))], steg=7, w=2)
    q = P(((vi[0] + vi[1]) / 2, K.Y_PL1, vi[3]))
    leiar(dr, q, (q[0] - 40 * MM, q[1] - 30 * MM), 'koparteip i vindauget')
    a, b = P(((lx0 + lx1) / 2, ly1 + 70 + 14, lz0 + 10)), P(((lx0 + lx1) / 2, ly1 + 24, lz0 + 10))
    pil(dr, a, b, tjukk=5)
    a, b = P(((lx0 + lx1) / 2, ly0 + 80, lz1 + 88)), P(((lx0 + lx1) / 2, ly0 + 80, lz1 + 70))
    pil(dr, a, b, tjukk=4)
    for pid, (dx, dy) in {'D11': (18, 16), 'D14': (16, -14), 'E02': (-22, -14), 'E03': (-20, 12), 'E04': (22, 0)}.items():
        p = P(boks_senter(S[pid]))
        ballong(dr, p, (p[0] + dx * MM, p[1] + dy * MM), pid)
    q = P((134, ly1 + 70, 11))
    leiar(dr, q, (q[0] - 30 * MM, q[1] + 22 * MM), 'USB-C bakover')
    return im


def s13_arm(nr):
    d10 = flytta(D['D10'], (-118, 0, 0))
    e01 = flytta(D['E01'], (0, 0, -34))
    im, dr = side(nr, 8, f'Skyv endepluggen D10 inn frå rota av profilen, med botnen ned mellom leppene, til endeveggen '
                         f'er i flukt med enden. Lim med epoksy. Kapp lyslista E01 på merket næraste 343 mm, med '
                         f'loddeputene mot leddet, og lim ho midt under ryggen, {LED_START - K.ARM_X0:.0f} mm frå rota '
                         f'av profilen.')
    v = Vising([D['D04'], D['D05'], d10, e01], UNDER)
    P = v.teikn(dr, (int(10 * MM), topp(im, 10), A4[0] - int(10 * MM), A4[1] - int(60 * MM)))
    yc = (K.ARM_Y0 + K.ARM_Y1) / 2
    pil(dr, P((K.ARM_X0 - 70, yc, K.ARM_BOTN + 8)), P((K.ARM_X0 - 8, yc, K.ARM_BOTN + 8)), tjukk=5)
    p = P(boks_senter(d10))
    ballong(dr, p, (p[0] - 6 * MM, p[1] + 20 * MM), 'D10')
    for x_ in (LED_START + 60, LED_SLUTT - 60):
        pil(dr, P((x_, yc, K.ARM_BOTN - 30)), P((x_, yc, K.ARM_BOTN - 6)), tjukk=4)
    p = P(boks_senter(e01))
    ballong(dr, p, (p[0] + 10 * MM, p[1] + 22 * MM), 'E01')
    p = P((450, K.ARM_Y1, K.ARM_TOPP))
    ballong(dr, p, (p[0] + 8 * MM, p[1] - 14 * MM), 'D04')
    # mål frå rota til lyslista
    zm = K.ARM_BOTN - 50
    a, b = P((K.ARM_X0, K.ARM_Y0, zm)), P((LED_START, K.ARM_Y0, zm))
    dr.line([a, b], fill=SVART, width=2)
    for p_, x_ in ((a, K.ARM_X0), (b, LED_START)):
        stipla(dr, P((x_, K.ARM_Y0, K.ARM_BOTN)), p_, w=1)
    etikett(dr, ((a[0] + b[0]) / 2 - 8 * MM, (a[1] + b[1]) / 2 + 2 * MM), f'{LED_START - K.ARM_X0:.0f}', font(11, True))
    pp = P((LED_START + 2, yc, K.ARM_TOPP - 3 - 34))
    leiar(dr, pp, (pp[0] - 10 * MM, pp[1] + 34 * MM), 'loddeputene mot leddet')
    return im


def ledd_stativ(z0=262):
    return [utsnitt(D[p], z0=z0) for p in STATIV]


def s14_ledd_fram(nr):
    sp = {'M03-1': (0, -18, 0), 'D04': (0, -46, 0), 'D05': (0, -46, 0), 'M05': (0, -46, 0), 'M02-1': (0, -76, 0)}
    S = sett(list(sp), sp)
    S['D04'] = utsnitt(S['D04'], x1=232)
    im, dr = side(nr, 9, 'Træ PA6-skiva M03 på akselen framme. Legg raud og blå ut i sporet i forsterkingsplata og skyv '
                         'armen på den flate sida, med stoppinnen i bogesporet. Skru på frammutteren M02 med gjengelås. '
                         'Lodd den svarte leidningen til kanten av framenden på akselen, kort og lågt (under 1 mm). Den '
                         'kvite skal stikke fritt ut framme.')
    v = Vising(ledd_stativ() + [D['M01']] + list(S.values()), FV)
    y0 = topp(im, 8)
    P = v.teikn(dr, (int(12 * MM), y0, A4[0] - int(12 * MM), A4[1] - int(92 * MM)))
    stipla(dr, P((LX, 16, LZ)), P((LX, -98, LZ)), w=2)
    pil(dr, P((LX, -112, LZ)), P((LX, -92, LZ)), tjukk=4)
    anker = lambda p: P(boks_senter(S[p]))
    ballongrad(dr, [('M03', anker('M03-1')), ('D04', P((205, K.ARM_Y0 - 46, K.ARM_TOPP))), ('M02', anker('M02-1'))],
               y0 + 4 * MM, x0=A4[0] * 0.45)
    p = P((160, K.Y_PL0, 290))
    ballong(dr, p, (p[0] - 22 * MM, p[1] + 16 * MM), 'D01')
    bs = [P((LX + 12 * math.cos(math.radians(a_)), K.Y_PL0, LZ + 12 * math.sin(math.radians(a_))))
          for a_ in np.linspace(K.BOGE_FRA, K.BOGE_TIL, 30)]
    q = bs[len(bs) // 2]
    leiar(dr, q, (q[0] - 26 * MM, q[1] - 10 * MM), 'stoppinnen går\ni bogesporet')
    q = P((LX - 2, K.Y_AKSEL[0], LZ + 3.5))
    leiar(dr, q, (q[0] + 62 * MM, q[1] + 30 * MM), 'svart: lodda på framenden av akselen\nkvit: stikk fritt ut framme')
    # innfelt: forsterkingsplata bakfrå med leidningane i sporet
    v2 = Vising([D['D05'], D['M05']], BV)
    yb0 = A4[1] - int(86 * MM)
    P2 = v2.teikn(dr, (int(96 * MM), yb0, A4[0] - int(14 * MM), A4[1] - int(20 * MM)))
    bane = [P2((LX + 1.0, K.Y_DOBLAR[1], LZ - 0.6)), P2((LX + 3.5, K.Y_DOBLAR[1], LZ - 1.0)),
            P2((K.ARM_X0 + K.TUNGE_L + 2.0, K.Y_DOBLAR[1], LZ - 4.0)), P2((K.ARM_X0 + K.TUNGE_L + 14.0, K.Y_DOBLAR[1] + 3, LZ - 4.0))]
    dr.line(bane, fill=SVART, width=7, joint='curve')
    q = bane[2]
    leiar(dr, q, (q[0] - 30 * MM, q[1] + 16 * MM), 'raud og blå i sporet,\nut ved enden av tunga')
    p = P2(boks_senter(D['D05']))
    ballong(dr, p, (p[0] + 30 * MM, p[1] + 4 * MM), 'D05')
    pm = P2(boks_senter(D['M05']))
    ballong(dr, pm, (pm[0] - 18 * MM, pm[1] - 14 * MM), 'M05')
    dr.text((int(96 * MM), yb0 - int(7 * MM)), 'Forsterkingsplata sett bakfrå', font=font(9.5, True), fill=SVART)
    return im


def fjorpakke(dr, x, y, k=3.2 * MM):
    """Snitt gjennom dei fire tallerkenfjørene, motstilte ()(): fire kjegler langs akselen."""
    for i in range(4):
        x0 = x + i * 1.6 * k
        h = 2.6 * k
        if i % 2 == 0:
            pts = [(x0, y - h), (x0 + 1.2 * k, y - 0.6 * k)]
            pts2 = [(x0, y + h), (x0 + 1.2 * k, y + 0.6 * k)]
        else:
            pts = [(x0 + 1.2 * k, y - h), (x0, y - 0.6 * k)]
            pts2 = [(x0 + 1.2 * k, y + h), (x0, y + 0.6 * k)]
        dr.line(pts, fill=SVART, width=6)
        dr.line(pts2, fill=SVART, width=6)
    stipla(dr, (x - 1.5 * k, y), (x + 7.6 * k, y), w=2)


def s15_ledd_bak(nr):
    sp = {'M03-2': (0, 14, 0), 'D06': (0, 26, 0), 'M04-1': (0, 38, 0), 'M04-2': (0, 43, 0), 'M04-3': (0, 48, 0),
          'M04-4': (0, 53, 0), 'M02-2': (0, 72, 0)}
    S = sett(list(sp), sp)
    vinkel = LEDD['mutter_etter_anlegg_grad']
    im, dr = side(nr, 10, f'Bak: PA6-skiva, låseskiva D06 med D-holet på den flate sida og dei fire tallerkenfjørene '
                          f'motstilte ()(). Skru bakmutteren på til han ligg an. Merk mutteren og akselen med tusj, hald '
                          f'frammutteren med ein 13 mm fastnøkkel og skru bakmutteren {vinkel:.0f}° vidare. Det gjev om '
                          f'lag {LEDD["fjorkraft_N"]:.0f} N klemkraft. Gjengelås.')
    v = Vising(ledd_stativ() + [D['M01']] + list(S.values()), BAK)
    y0 = topp(im, 6)
    P = v.teikn(dr, (int(10 * MM), y0, int(150 * MM), A4[1] - int(24 * MM)))
    stipla(dr, P((LX, -4, LZ)), P((LX, 92, LZ)), w=2)
    pil(dr, P((LX, 112, LZ)), P((LX, 94, LZ)), tjukk=4)
    for pid, (dx, dy) in {'M03-2': (-14, 20), 'D06': (14, 22), 'M04-2': (-12, -20), 'M02-2': (-18, -12)}.items():
        p = P(boks_senter(S[pid]))
        ballong(dr, p, (p[0] + dx * MM, p[1] + dy * MM), pid.split('-')[0])
    q = P((LX, 4.25 + 26, LZ + 4))
    leiar(dr, q, (q[0] + 22 * MM, q[1] - 26 * MM), 'D-holet på\nden flate sida')
    # fjørene i snitt
    cx, cy = int(160 * MM), y0 + int(40 * MM)
    dr.text((cx - int(4 * MM), cy - int(30 * MM)), 'Fjørene, snitt', font=font(9.5, True), fill=SVART)
    fjorpakke(dr, cx, cy)
    etikett(dr, (cx - int(2 * MM), cy + int(14 * MM)), '( ) ( )  motstilte', font(9))
    # vinkelen
    cx2, cy2, r = int(172 * MM), y0 + int(100 * MM), int(15 * MM)
    dr.ellipse([cx2 - r, cy2 - r, cx2 + r, cy2 + r], outline=SVART, width=2)
    dr.arc([cx2 - r, cy2 - r, cx2 + r, cy2 + r], -90, -90 + vinkel, fill=SVART, width=8)
    a_ = math.radians(-90 + vinkel)
    pil(dr, (cx2 + r * math.cos(a_ - 0.25), cy2 + r * math.sin(a_ - 0.25)), (cx2 + r * math.cos(a_), cy2 + r * math.sin(a_)),
        tjukk=3)
    dr.line([(cx2, cy2 - r - 8), (cx2, cy2 - r + 14)], fill=SVART, width=4)
    t = f'{vinkel:.0f}°'
    dr.text((cx2 - dr.textlength(t, font=font(16, True)) / 2, cy2 - int(3.2 * MM)), t, font=font(16, True), fill=SVART)
    etikett(dr, (cx2 - int(18 * MM), cy2 + r + int(3 * MM)), 'etter anlegg, frå tusjmerket', font(9))
    return im


def s16_friksjon(nr):
    vekt = LEDD['vektprove_g']
    im, dr = side(nr, 11, f'Still armen vassrett. Heng {vekt[0]} g i tuppen: armen skal stå. Heng på {vekt[1]} g: armen '
                          f'skal gli ned. Søkk han med {vekt[0]} g, stram bakmutteren 30° og prøv att. Glir han ikkje med '
                          f'{vekt[1]} g, løys 30°. Lim så hetta D08 på bakmutteren med epoksy.')
    y0 = topp(im, 8)
    S = [D[p] for p in SYNLEGE if p != 'D08']
    for i, (g, tekst) in enumerate(((vekt[0], 'står'), (vekt[1], 'glir ned'))):
        v = Vising(S, FRAMME)
        x0 = int(10 * MM) + i * int(96 * MM)
        P = v.teikn(dr, (x0, y0, x0 + int(90 * MM), y0 + int(70 * MM)))
        tupp = P((K.ARM_X1 + 2.0, K.ARM_Y0, K.ARM_BOTN))
        lodd_y = tupp[1] + 18 * MM
        dr.line([tupp, (tupp[0], lodd_y)], fill=SVART, width=2)
        dr.rectangle([tupp[0] - 4 * MM, lodd_y, tupp[0] + 4 * MM, lodd_y + 7 * MM], outline=SVART, width=3,
                     fill=(255, 255, 255))
        t = f'{g} g'
        dr.text((tupp[0] - dr.textlength(t, font=font(9, True)) / 2, lodd_y + 1.6 * MM), t, font=font(9, True), fill=SVART)
        etikett(dr, (x0 + int(30 * MM), lodd_y + 12 * MM), tekst, font(12, True))
        if i == 1:
            pil(dr, (tupp[0] + 8 * MM, tupp[1] - 2 * MM), (tupp[0] + 8 * MM, tupp[1] + 12 * MM), tjukk=4)
    # hetta
    sp = {'D08': (0, 40, 0)}
    Sh = sett(['D08'], sp)
    v = Vising(ledd_stativ(250) + [utsnitt(D['D04'], x1=260), D['D05'], D['M01'], D['M02-2'], D['D06']] + FJOR_F()
               + list(Sh.values()), BAK)
    P = v.teikn(dr, (int(30 * MM), y0 + int(96 * MM), A4[0] - int(30 * MM), A4[1] - int(22 * MM)))
    pil(dr, P((LX, 70, LZ + 16)), P((LX, 36, LZ + 16)), tjukk=5)
    p = P(boks_senter(Sh['D08']))
    ballong(dr, p, (p[0] + 18 * MM, p[1] - 16 * MM), 'D08')
    q = P((LX, K.Y_MUTB[1], LZ - 6.5))
    leiar(dr, q, (q[0] - 30 * MM, q[1] + 22 * MM), 'epoksy på bakmutteren')
    return im


def FJOR_F():
    return [D[p] for p in FJOR]


def s17_lys(nr):
    d12 = flytta(D['D12'], (95, 0, 0))
    d09 = flytta(D['D09'], (150, 0, 0))
    im, dr = side(nr, 12, 'Før raud og blå ut av sporet ved enden av tunga og langs framflensen, framfor endepluggen, til '
                          'lyslista. Lodd raud til + og blå til −, og legg leidningane flatt inn mot ryggen. Skyv spreiaren '
                          'D12 inn frå tuppen, oppå leppene, til han ligg mot endepluggen. Lim endelokket D09 i tuppen; '
                          'tappen nedst held enden av spreiaren.')
    v = Vising([D['D04'], D['D05'], D['D10'], D['E01'], d12, d09], UNDER)
    P = v.teikn(dr, (int(10 * MM), topp(im, 10), A4[0] - int(10 * MM), A4[1] - int(70 * MM)))
    yv = K.Y_DOBLAR[0] + 1.6
    zt = LZ - 4.0
    bane = [P((K.ARM_X0 + K.TUNGE_L, yv, zt)), P((K.LED_X0 - 2, yv, zt)), P((K.LED_X0 + 1, 2.0, K.ARM_TOPP - 4)),
            P((LED_START + 1, (K.ARM_Y0 + K.ARM_Y1) / 2 - 2, K.ARM_TOPP - 3))]
    stipla_line(dr, bane, w=5)
    q = bane[1]
    leiar(dr, q, (q[0] - 20 * MM, q[1] + 34 * MM), 'raud og blå langs framflensen,\nframfor endepluggen D10')
    yc = (K.ARM_Y0 + K.ARM_Y1) / 2
    pil(dr, P((K.ARM_X1 + 82, yc, K.ARM_BOTN + 2)), P((K.ARM_X1 + 20, yc, K.ARM_BOTN + 2)), tjukk=5)
    pil(dr, P((K.ARM_X1 + 165, yc, K.ARM_TOPP - 8)), P((K.ARM_X1 + 120, yc, K.ARM_TOPP - 8)), tjukk=5)
    for pid, f_, (dx, dy) in (('D12', d12, (0, 22)), ('D09', d09, (10, -18))):
        p = P(boks_senter(f_))
        ballong(dr, p, (p[0] + dx * MM, p[1] + dy * MM), pid)
    p = P((LED_START + 1, yc - 2, K.ARM_TOPP - 3))
    leiar(dr, p, (p[0] + 10 * MM, p[1] - 22 * MM), 'raud til +, blå til −')
    return im


def s18_knott(nr):
    im, dr = side(nr, 13, 'Klipp koparfolien til Ø 11 og lim han i botnen av holrommet i knotten D07. Lodd den kvite '
                          'leidningen til kanten av folien, kort og flatt, minst 1,5 mm frå akselen. Lim knotten på '
                          'frammutteren med epoksy: sekskantlomma tek mutteren, og det skal vere 0,5 mm luft mot øyret.')
    y0 = topp(im, 6)
    # knotten bakfrå, med folien
    k7 = D['D07']
    v1 = Vising([k7], BAK)
    P1 = v1.teikn(dr, (int(14 * MM), y0, int(92 * MM), y0 + int(80 * MM)))
    yb = K.Y_KNOTT[0] + 1.0
    skraver(im, sirkel3(P1, (LX, yb + 0.02, LZ), 5.5), steg=8, w=2)
    q = P1((LX + 5.5, yb, LZ))
    leiar(dr, q, (q[0] + 16 * MM, q[1] + 26 * MM), 'koparfolie Ø 11')
    q = P1((LX - 5.5 * 0.7, yb, LZ + 5.5 * 0.7))
    dr.ellipse([q[0] - 9, q[1] - 9, q[0] + 9, q[1] + 9], fill=SVART)
    leiar(dr, q, (q[0] - 8 * MM, q[1] - 16 * MM), 'lodding, kvit')
    # knotten på mutteren
    sp = {'D07': (0, -26, 0)}
    S = sett(['D07'], sp)
    v2 = Vising(ledd_stativ() + [utsnitt(D['D04'], x1=232), D['D05'], D['M01'], D['M02-1'], D['M03-1']]
                + list(S.values()), FV)
    P2 = v2.teikn(dr, (int(70 * MM), y0 + int(70 * MM), A4[0] - int(12 * MM), A4[1] - int(22 * MM)))
    pil(dr, P2((LX, -52, LZ + 12)), P2((LX, -24, LZ + 12)), tjukk=5)
    p = P2(boks_senter(S['D07']))
    ballong(dr, p, (p[0] + 22 * MM, p[1] + 20 * MM), 'D07')
    stipla_line(dr, [P2((LX, K.Y_AKSEL[0], LZ)), P2((LX - 1, -20, LZ + 2)), P2((LX - 2, -27, LZ + 3))], w=4)
    q = P2((LX - 1, -20, LZ + 2))
    leiar(dr, q, (q[0] - 26 * MM, q[1] + 24 * MM), 'kvit leidning til folien')
    return im


def s19_filt(nr):
    sp = {'D13-1': (0, 0, -24), 'D13-2': (0, 0, -24)}
    S = sett(list(sp), sp)
    im, dr = side(nr, 14, 'Skjer to filtlister etter malen produksjon/D13_mal_1til1.dxf og lim éi under kvar flens, '
                          '1 mm inn frå kantane.')
    v = Vising([utsnitt(D[p], z1=90) for p in STATIV] + [utsnitt(D['D11'], z1=90)] + list(S.values()), UNDER)
    P = v.teikn(dr, (int(14 * MM), topp(im, 10), A4[0] - int(14 * MM), A4[1] - int(30 * MM)))
    for pid in sp:
        c = boks_senter(S[pid])
        pil(dr, P((c[0], c[1], c[2] - 22)), P((c[0], c[1], c[2] - 3)), tjukk=5)
        p = P(c)
        ballong(dr, p, (p[0] + 22 * MM, p[1] + 16 * MM), 'D13')
    return im


def s20_ferdig(nr):
    im, dr = side(nr, None, 'Ferdig')
    v = Vising([D[p] for p in SYNLEGE], FOTO)
    v.teikn(dr, (int(20 * MM), int(24 * MM), A4[0] - int(20 * MM), int(118 * MM)))
    y = int(126 * MM)
    dr.text((int(14 * MM), y), 'Prøv før bruk', font=font(12, True), fill=SVART)
    y += int(8 * MM)
    vk = KONTROLL['velting']['minste_grad']
    y = tekstblokk(dr, int(14 * MM), y, A4[0] - int(28 * MM), [
        ('Vipping', f'Set lampa på eit brett som hallar 6° (105 mm på 1 m), i fire retningar, med armen på −30°, 0° '
                    f'og +75°. Ho skal ikkje velte (CAD-en gjev minst {vk:.1f}°).'),
        ('Varme', 'Full styrke i 60 minutt: armen skal vere under 45 °C.'),
        ('Berøring', 'Hald handa på stativet og på øyret: lyset skal ikkje endre seg. Kort trykk på knotten slår av '
                     'og på; hald inne for å dimme.'),
    ], innrykk=30)
    y += int(4 * MM)
    dr.text((int(14 * MM), y), 'Feilsøking', font=font(12, True), fill=SVART)
    y += int(8 * MM)
    tekstblokk(dr, int(14 * MM), y, A4[0] - int(28 * MM), [
        ('Ikkje blink ved oppstart', 'Sjekk VBUS til 5V-pinnen og lyslista, at raud går til + og blå til −, og at '
                                     'minus går gjennom MOSFET-en (D til blå, S til GND).'),
        ('Knotten svarar ikkje', 'Ikkje rør knotten dei første sekunda: lampa måler då krysstalen. Sjekk at folien ikkje '
                                 'rører akselen. Slå på FEILSOK i fastvara og still TERSKEL etter utskrifta.'),
        ('Slår seg av og på sjølv', 'Den svarte leidningen må vere lodda til akselen, og koparteipen i vindauget må '
                                    'liggje på blankt stål.'),
        ('Svakare lys enn venta', 'Ladaren lovar berre standard USB, og fastvara avgrensar til 75 %. Bruk ein '
                                  'USB-C-ladar på 1,5 A eller meir.'),
        ('Armen søkk eller er tung', 'Gjer steg 11 om att og juster bakmutteren 30° om gongen. Etterstill etter ei veke.'),
        ('Armen skrapar', 'Stoppinnen skal stikke 2 mm ut bak forsterkingsplata, ikkje meir.'),
    ], innrykk=50)
    return im


SIDELISTE = [s01_framside, s02_delar_1, s03_delar_2, s04_oversikt, s05_prove, s06_aksel, s07_leidningar,
             s08_laminering, s09_forsterking, s10_lakk, s11_kopling, s12_lomma, s13_arm, s14_ledd_fram, s15_ledd_bak,
             s16_friksjon, s17_lys, s18_knott, s19_filt, s20_ferdig]


def main():
    SIDER.mkdir(parents=True, exist_ok=True)
    val = [int(a) for a in sys.argv[1:] if a.isdigit()]
    bilete = []
    for i, fn in enumerate(SIDELISTE, start=1):
        if val and i not in val:
            continue
        print('side', i, fn.__name__, flush=True)
        im = fn(i)
        im.save(SIDER / f'side-{i:02d}.png', optimize=True)
        bilete.append(im)
    if not val:
        bilete[0].save(HER / 'Kran-montering.pdf', save_all=True, append_images=bilete[1:], resolution=DPI)
        print('PDF skriven', flush=True)


if __name__ == '__main__':
    main()
