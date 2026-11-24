# -*- coding: utf-8 -*-
"""
lag_rettleiing.py  ·  monteringsrettleiing for Lut, teikna rett frå CAD-en (cad/lut.py)

  py -3 montering/lag_rettleiing.py         lagar montering/sider/*.png og montering/Lut-montering.pdf
  py -3 montering/lag_rettleiing.py 3 5     berre desse sidene

Strekteikningar med skjulte kantar fjerna (OCC HLR), svart på kvitt, ID-ane er dei same som i stykklista og
printfilene. Mutrane, skruane og magnetane er dei same formene som i kollisjonskontrollen.
"""
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
import lut as L                                                     # noqa: E402
from cadquery import Vector as V                                    # noqa: E402

SIDER = HER / 'sider'
DPI = 200
MM = DPI / 25.4
A4 = (int(210 * MM), int(297 * MM))                                 # ståande
REV = 'Lut · konsept D · rev. A · 24.11.2026'
FH = ((0.62, -1.0, 0.62), (1.0, 0.62, 0.0))                         # framme til høgre, litt ovanfrå
FV = ((-0.62, -1.0, 0.62), (1.0, -0.62, 0.0))                       # framme til venstre
UNDER = ((0.62, -1.0, -0.75), (1.0, 0.62, 0.0))                     # framme til høgre, nedanfrå
UNDER_BRATT = ((0.45, -0.75, -1.3), (1.0, 0.6, 0.0))                # bratt nedanfrå: ser opp i foten, forbi veggen
FRAMME = ((0.0, -1.0, 0.0), (1.0, 0.0, 0.0))
BAK = ((0.55, 1.0, 0.55), (-1.0, 0.55, 0.0))                        # bak til høgre


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
            dr.line([f(p) for p in pk], fill=(0, 0, 0), width=max(1, int(round(vekt * tjukk * DPI / 150))), joint='curve')
        s.k = k / MM
        s.f = f
        return lambda p3: f(s.punkt(p3))


def side(nr, tal=None, tekst=None):
    im = Image.new('RGB', A4, (255, 255, 255))
    dr = ImageDraw.Draw(im)
    m = int(10 * MM)
    if tal is not None:
        dr.text((m, m), str(tal), font=font(54, True), fill=(0, 0, 0))
    if tekst:
        f = font(13)
        x = m + (int(22 * MM) if tal is not None else 0)
        brei = A4[0] - m - x
        liner, linje = [], ''
        for o in tekst.split():
            if linje and dr.textlength(linje + ' ' + o, font=f) > brei:
                liner.append(linje)
                linje = o
            else:
                linje = (linje + ' ' + o).strip()
        liner.append(linje)
        for i, l_ in enumerate(liner):
            dr.text((x, m + int(7 * MM) + i * int(6.2 * MM)), l_, font=f, fill=(0, 0, 0))
    fn = font(7.5)
    t = f'{REV} · {nr}'
    dr.text((A4[0] - m - dr.textlength(t, font=fn), A4[1] - m + int(3 * MM)), t, font=fn, fill=(0, 0, 0))
    return im, dr


def ballong(dr, p, q, tekst, r=5.0):
    r = r * MM
    q = (min(max(q[0], 8 * MM + r), A4[0] - 8 * MM - r), min(max(q[1], 22 * MM + r), A4[1] - 14 * MM - r))
    dr.line([p, q], fill=(0, 0, 0), width=2)
    dr.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=(0, 0, 0))
    dr.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=(255, 255, 255), outline=(0, 0, 0), width=3)
    f = font(10, True)
    w = dr.textlength(tekst, font=f)
    dr.text((q[0] - w / 2, q[1] - 0.52 * f.size), tekst, font=f, fill=(0, 0, 0))


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
    dr.line([tuple(a), tuple(b - v * s * 0.8)], fill=(0, 0, 0), width=tjukk)
    tri = [tuple(b), tuple(b - v * s + n * s * 0.42), tuple(b - v * s - n * s * 0.42)]
    dr.polygon(tri, fill=(255, 255, 255) if hol else (0, 0, 0), outline=(0, 0, 0))


def stipla(dr, a, b, strek=2.2, luft=1.6, w=2):
    a, b = np.array(a, float), np.array(b, float)
    L_ = np.linalg.norm(b - a)
    if L_ < 1:
        return
    v = (b - a) / L_
    t = 0.0
    while t < L_:
        dr.line([tuple(a + v * t), tuple(a + v * min(t + strek * MM, L_))], fill=(0, 0, 0), width=w)
        t += (strek + luft) * MM


def etikett(dr, xy, tekst, f=None, pad=0.8):
    """Tekst med kvit botn, så strekar under ikkje går gjennom bokstavane."""
    f = f or font(9)
    x, y = xy
    w = dr.textlength(tekst, font=f)
    p = pad * MM
    dr.rectangle([x - p, y - p * 0.6, x + w + p, y + f.size * 1.15 + p * 0.6], fill=(255, 255, 255))
    dr.text((x, y), tekst, font=f, fill=(0, 0, 0))


def mengd(dr, p, tekst, storleik=12):
    etikett(dr, p, tekst, font(storleik, True))


def stipla_sirkel(dr, c, r, w=3, n=16):
    """Stipla sirkel for noko som ligg skjult bak ei flate."""
    for i in range(n):
        a0, a1 = 360 * i / n, 360 * (i + 0.55) / n
        dr.arc([c[0] - r, c[1] - r, c[0] + r, c[1] + r], a0, a1, fill=(0, 0, 0), width=w)


def boble(im, sentrum, r, kjelde_ramme, kjelde_im, peik_fra=None):
    """Rund forstørringsboble: klipp ut eit utsnitt av kjelde_im og legg det i ein sirkel."""
    x0, y0, x1, y1 = [int(c) for c in kjelde_ramme]
    ut = kjelde_im.crop((x0, y0, x1, y1)).resize((int(2 * r), int(2 * r)), Image.LANCZOS)
    maske = Image.new('L', ut.size, 0)
    ImageDraw.Draw(maske).ellipse([0, 0, ut.size[0] - 1, ut.size[1] - 1], fill=255)
    im.paste(ut, (int(sentrum[0] - r), int(sentrum[1] - r)), maske)
    dr = ImageDraw.Draw(im)
    dr.ellipse([sentrum[0] - r, sentrum[1] - r, sentrum[0] + r, sentrum[1] + r], outline=(0, 0, 0), width=4)
    if peik_fra is not None:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        dr.ellipse([x0, y0, x1, y1], outline=(0, 0, 0), width=2)
        v = np.array(sentrum, float) - np.array((cx, cy), float)
        v /= np.linalg.norm(v)
        dr.line([(cx + v[0] * (x1 - x0) / 2, cy + v[1] * (y1 - y0) / 2), (sentrum[0] - v[0] * r, sentrum[1] - v[1] * r)],
                fill=(0, 0, 0), width=2)


# ------------------------------------------------------------------ delane

print('Byggjer CAD-en', flush=True)
D = {pid: d['form'] for pid, d in L.bygg().items()}
FLYTT = {}


def flytta(pid, v):
    return D[pid].translate(V(*v)) if any(v) else D[pid]


def sett(pids, flytt=None):
    flytt = flytt or {}
    return {p: flytta(p, flytt.get(p, (0, 0, 0))) for p in pids}


def senter(form):
    return form.Center().toTuple()


def boks_senter(form):
    bb = form.BoundingBox()
    return ((bb.xmin + bb.xmax) / 2, (bb.ymin + bb.ymax) / 2, (bb.zmin + bb.zmax) / 2)


SYNLEGE = ['D01', 'D02', 'D03', 'D05', 'D04'] + [p for p in D if p.startswith('M07')]
SKRUAR_M03 = [p for p in D if p.startswith('M03')]
SKRUAR_M04 = [p for p in D if p.startswith('M04')]
SKRUAR_M05 = [p for p in D if p.startswith('M05')]
MAGNET_HOV = ['M06-1', 'M06-2', 'M06-3']
MAGNET_KOPP = ['M06-4', 'M06-5', 'M06-6']


# ------------------------------------------------------------------ sider

def s01_framside(nr):
    im, dr = side(nr)
    v = Vising([D[p] for p in SYNLEGE], FH)
    v.teikn(dr, (int(22 * MM), int(60 * MM), A4[0] - int(22 * MM), A4[1] - int(40 * MM)))
    dr.text((int(10 * MM), int(12 * MM)), 'LUT', font=font(64, True), fill=(0, 0, 0))
    dr.text((int(10 * MM), int(37 * MM)), 'Bordlampe med dimmar · 5 V USB-C', font=font(13), fill=(0, 0, 0))
    return im


def s02_delar(nr):
    im, dr = side(nr, None, 'Delar')
    rader = [
        [('D01', 1), ('D02', 1), ('D03', 1)],
        [('D04', 1), ('D05', 1), ('D06', 1), ('D07', 1)],
        [('D08', 1), ('E01', 1), ('E02', 1), ('E02b', 1), ('E03', 1), ('E04', 1)],
    ]
    y = int(26 * MM)
    hogder = [int(74 * MM), int(50 * MM), int(40 * MM)]
    for rad, h in zip(rader, hogder):
        b = (A4[0] - int(20 * MM)) / len(rad)
        for i, (pid, n) in enumerate(rad):
            x0 = int(10 * MM + i * b)
            ramme = (x0 + int(4 * MM), y + int(11 * MM), int(x0 + b - 4 * MM), y + h - int(7 * MM))
            Vising([D[pid]], FH).teikn(dr, ramme)
            f = font(9 if len(pid) > 3 else 9.5, True)
            dr.ellipse([x0 + int(2 * MM), y, x0 + int(13 * MM), y + int(11 * MM)], outline=(0, 0, 0), width=3)
            dr.text((x0 + int(7.5 * MM) - dr.textlength(pid, font=f) / 2, y + int(3.0 * MM)), pid, font=f, fill=(0, 0, 0))
            dr.text((x0 + int(15 * MM), y + int(2.6 * MM)), f'×{n}', font=font(11, True), fill=(0, 0, 0))
        y += h
    dr.line([(int(10 * MM), y), (A4[0] - int(10 * MM), y)], fill=(0, 0, 0), width=2)
    y += int(4 * MM)
    beslag = [('M01', 'M4', 3), ('M02', 'M3', 6), ('M03', 'M4×16', 3), ('M04', 'M3×10', 2), ('M05', 'M3×8', 4),
              ('M06', 'Ø6×3', 6), ('M07', 'Ø10×2', 4)]
    b = (A4[0] - int(20 * MM)) / len(beslag)
    for i, (pid, mal, n) in enumerate(beslag):
        cx = int(10 * MM + i * b) + b / 2
        dr.text((cx - dr.textlength(pid, font=font(10, True)) / 2, y), pid, font=font(10, True), fill=(0, 0, 0))
        yy = y + int(9 * MM)
        if pid in ('M01', 'M02'):
            w, h = (5.6, 8.1) if pid == 'M01' else (4.2, 5.7)
            dr.rectangle([cx - w * MM, yy, cx + w * MM, yy + h * 2 * MM], outline=(0, 0, 0), width=3)
            for k in range(1, 4):
                yk = yy + k * h * 2 * MM / 4
                dr.line([(cx - w * MM, yk), (cx + w * MM, yk)], fill=(0, 0, 0), width=2)
        elif pid in ('M03', 'M04', 'M05'):
            d_, l_ = {'M03': (4, 16), 'M04': (3, 10), 'M05': (3, 8)}[pid]
            s_ = 1.25
            if pid == 'M05':                                    # senkskrue: kjegleforma hovud, lengda inkluderer hovudet
                hh = 1.86
                dr.polygon([(cx - 3.36 * s_ * MM, yy), (cx + 3.36 * s_ * MM, yy), (cx + d_ / 2 * s_ * MM, yy + hh * s_ * MM),
                            (cx - d_ / 2 * s_ * MM, yy + hh * s_ * MM)], outline=(0, 0, 0), width=3)
                skaft = l_ - hh
            else:
                hh = d_
                dr.rectangle([cx - d_ * 0.85 * s_ * MM, yy, cx + d_ * 0.85 * s_ * MM, yy + hh * s_ * MM], outline=(0, 0, 0), width=3)
                skaft = l_
            dr.rectangle([cx - d_ / 2 * s_ * MM, yy + hh * s_ * MM, cx + d_ / 2 * s_ * MM, yy + (hh + skaft) * s_ * MM],
                         outline=(0, 0, 0), width=3)
            for k in range(int(skaft)):
                yk = yy + (hh + k + 0.5) * s_ * MM
                dr.line([(cx - d_ / 2 * s_ * MM, yk), (cx + d_ / 2 * s_ * MM, yk + 0.5 * s_ * MM)], fill=(0, 0, 0), width=1)
        elif pid == 'M06':
            dr.ellipse([cx - 6 * MM, yy, cx + 6 * MM, yy + 4 * MM], outline=(0, 0, 0), width=3)
            dr.rectangle([cx - 6 * MM, yy + 2 * MM, cx + 6 * MM, yy + 8 * MM], outline=(0, 0, 0), width=3)
            dr.rectangle([cx - 6 * MM + 3, yy + 2 * MM + 3, cx + 6 * MM - 3, yy + 8 * MM - 1], fill=(255, 255, 255))
            dr.ellipse([cx - 6 * MM, yy + 6 * MM, cx + 6 * MM, yy + 10 * MM], outline=(0, 0, 0), width=3)
        else:
            dr.ellipse([cx - 10 * MM, yy, cx + 10 * MM, yy + 6 * MM], outline=(0, 0, 0), width=3)
            dr.ellipse([cx - 10 * MM, yy + 3 * MM, cx + 10 * MM, yy + 9 * MM], outline=(0, 0, 0), width=3)
        dr.text((cx - dr.textlength(mal, font=font(8.5)) / 2, y + int(38 * MM)), mal, font=font(8.5), fill=(0, 0, 0))
        dr.text((cx - dr.textlength(f'×{n}', font=font(12, True)) / 2, y + int(44 * MM)), f'×{n}', font=font(12, True), fill=(0, 0, 0))
    y += int(56 * MM)
    dr.line([(int(10 * MM), y), (A4[0] - int(10 * MM), y)], fill=(0, 0, 0), width=2)
    g = font(9)
    liner = ['E05 kabel 2 × 0,25 mm², 650 mm · E06 leidning raud og svart, 2 × 120 mm',
             'M08 termisk teip Ø 50 × 2 · M09 kaptonteip 60 × 40 mm',
             'Loddebolt og loddetinn · unbrakonøkkel 2,0 · 2,5 · 3,0 mm, lang · fastnøkkel 10 mm · tusj',
             'Krympestrømpe · tokomponent epoksy, 24 t · avbitar · baufil og fil til akselen',
             'Saks til D07 · platesaks, bor 6 mm og fil til D08']
    for i, t in enumerate(liner):
        dr.text((int(10 * MM), y + int((4 + 5.2 * i) * MM)), t, font=g, fill=(0, 0, 0))
    return im


SPRENG = {
    'D02': (95, 0, 0), 'M06-1': (95, 0, 0), 'M06-2': (95, 0, 0), 'M06-3': (95, 0, 0),
    'D06': (95, 0, -85), 'M06-4': (95, 0, -85), 'M06-5': (95, 0, -85), 'M06-6': (95, 0, -85),
    'D08': (95, 0, -125), 'E01': (95, 0, -145), 'D07': (95, 0, -170),
    'M04-1': (150, 0, 0), 'M04-2': (150, 0, 0),
    'D05': (0, 0, 75), 'E02b': (0, 0, 48),
    'D03': (0, 0, -90), 'E02': (0, 0, -90), 'E03': (0, 0, -90), 'E04': (0, 0, -90),
    'M03-1': (0, 0, -140), 'M03-2': (0, 0, -140), 'M03-3': (0, 0, -140),
    'D04': (0, 0, -175), 'M05-1': (0, 0, -205), 'M05-2': (0, 0, -205), 'M05-3': (0, 0, -205), 'M05-4': (0, 0, -205),
    'M07-1': (0, 0, -192), 'M07-2': (0, 0, -192), 'M07-3': (0, 0, -192), 'M07-4': (0, 0, -192),
}


def s03_sprengt(nr):
    im, dr = side(nr, None, 'Oversikt')
    pids = [p for p in D if not p.startswith(('M04', 'M06')) and p not in ('E03', 'E04')]   # vist i stega i staden
    S = sett(pids, SPRENG)
    v = Vising(list(S.values()), FH)
    P = v.teikn(dr, (int(14 * MM), int(26 * MM), A4[0] - int(30 * MM), A4[1] - int(16 * MM)))
    plass = {'D01': (-30, -22), 'D02': (18, -26), 'D06': (30, -16), 'D08': (34, 0), 'E01': (30, 10), 'D07': (26, 14),
             'D05': (-22, -16), 'E02b': (-26, -4), 'D03': (-34, -8), 'E02': (22, 20),
             'D04': (-30, 10), 'M03-1': (-30, 24), 'M05-1': (-24, 14), 'M07-4': (24, 12)}
    for pid, (dx, dy) in plass.items():
        p = P(boks_senter(S[pid]))
        ballong(dr, p, (p[0] + dx * MM, p[1] + dy * MM), pid.split('-')[0], r=5.4)
    return im


def stegside(nr, tal, tekst, S, retning, ramme, ballongar=(), etter=None):
    im, dr = side(nr, tal, tekst)
    v = Vising(list(S.values()), retning)
    P = v.teikn(dr, ramme)
    for pid, p3, (dx, dy), lab in ballongar:
        p = P(p3 if p3 is not None else boks_senter(S[pid]))
        ballong(dr, p, (p[0] + dx * MM, p[1] + dy * MM), lab)
    if etter:
        etter(im, dr, P, v)
    return im


def leiar(dr, p, q, tekst, f=None):
    """Tynn peikeline frå tekst (q) til punkt (p)."""
    f = f or font(9)
    dr.line([p, q], fill=(0, 0, 0), width=2)
    dr.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=(0, 0, 0))
    venstre = q[0] < p[0]
    tw = dr.textlength(tekst, font=f)
    x = q[0] - tw - 1.5 * MM if venstre else q[0] + 1.5 * MM
    x = min(max(x, 10 * MM), A4[0] - 10 * MM - tw)
    etikett(dr, (x, q[1] - 0.6 * f.size), tekst, f)


STEIL = ((0.45, -0.75, 1.3), (1.0, 0.6, 0.0))                     # framme til høgre, bratt ovanfrå


def snudd(form, akse, sentrum):
    """Forma snudd 180° om ein akse parallell med X eller Y gjennom sentrum."""
    a = V(*sentrum)
    return form.rotate(a, a + (V(1, 0, 0) if akse == 'x' else V(0, 1, 0)), 180)


def snu_pkt(p, akse, sentrum):
    x, y, z = p
    cx, cy, cz = sentrum
    return (x, 2 * cy - y, 2 * cz - z) if akse == 'x' else (2 * cx - x, y, 2 * cz - z)


def s04_mutrar(nr):
    """Steg 1. Innpressmutrar: 3 × M4 i rota av bladet, 2 × M3 i enden, 4 × M3 i tårna i foten."""
    xi = L.HOV_X - L.HOV_R
    im, dr = side(nr, 1, 'Varm inn mutrane med loddebolten, 230 °C, til dei ligg plant med flata. '
                          'M4 i rota av bladet, M3 i enden og i tårna i foten.')
    v1 = Vising([D['D01']], UNDER)
    P = v1.teikn(dr, (int(12 * MM), int(36 * MM), int(118 * MM), int(150 * MM)))
    for x, y in L.BLAD_SKRUAR:
        pil(dr, P((x, y, L.FOT_Z - 30)), P((x, y, L.FOT_Z - 1)))
    q = P((60, 0, L.FOT_Z - 34))
    mengd(dr, (q[0] - 18 * MM, q[1] + 4 * MM), 'M01 ×3')
    for zc in L.HOV_SKRUAR_Z:
        pil(dr, P((xi + 34, 0, zc)), P((xi + 1, 0, zc)))
    q = P((xi + 34, 0, 250))
    mengd(dr, (q[0] + 2 * MM, q[1] - 4 * MM), 'M02 ×2')
    fot = D['D03'].rotate(V(0, 0, 0), V(1, 0, 0), 180).translate(V(0, 0, 40))
    v2 = Vising([fot], FH)
    P2 = v2.teikn(dr, (int(92 * MM), int(150 * MM), A4[0] - int(12 * MM), A4[1] - int(22 * MM)))
    z_tarn = 40 - (L.FOT_BOTN + L.PLATE_T)
    for x, y in L.PLATE_SKRUAR:
        pil(dr, P2((x, -y, z_tarn + 28)), P2((x, -y, z_tarn + 1)))
    pt = P2((40, 31, 70))
    mengd(dr, (pt[0] - 26 * MM, pt[1] - 10 * MM), 'M02 ×4')
    return im


def skraver(im, poly, steg=14, w=3):
    """Skraver ein polygon (epoksy) med 45°-liner."""
    from PIL import ImageChops
    maske = Image.new('L', im.size, 0)
    ImageDraw.Draw(maske).polygon(poly, fill=255)
    monster = Image.new('L', im.size, 0)
    dm = ImageDraw.Draw(monster)
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    for c in range(int(x0 - (y1 - y0)) - steg, int(x1) + steg, steg):
        dm.line([(c, y1), (c + (y1 - y0), y0)], fill=255, width=w)
    im.paste((0, 0, 0), (0, 0, im.width, im.height), ImageChops.multiply(maske, monster))
    ImageDraw.Draw(im).polygon(poly, outline=(0, 0, 0), width=3)


def forstorr(im, tmp, c, rk, sentrum, r):
    """Lim eit utsnitt av tmp (sentrum c, halvbreidd rk) inn som rund boble; gjev ein funksjon frå tmp- til sidekoordinatar."""
    boble(im, sentrum, r, (c[0] - rk, c[1] - rk, c[0] + rk, c[1] + rk), tmp)
    k = r / rk
    return lambda q: (sentrum[0] + (q[0] - c[0]) * k, sentrum[1] + (q[1] - c[1]) * k)


def stipla_ring(dr, pts, w=3):
    """Stipla lukka polylinje for ein kant som ligg skjult."""
    for i in range(0, len(pts), 2):
        dr.line([pts[i], pts[(i + 1) % len(pts)]], fill=(0, 0, 0), width=w)


def s05_lim(nr):
    """Steg 2. Éi limøkt: magnetane i hovudet og i koppen, og USB-C-kontakten i foten. Alt herdar i 24 timar.
    Hovudet og foten er snudde, slik ein faktisk held dei: lommene og spalta opnar seg oppover, og epoksyen renn inn."""
    im, dr = side(nr, 2, 'Lim alt i éi økt; epoksyen herdar i 24 timar. Stable dei seks magnetane og merk toppflata med tusj. '
                          'I hovudet: merket ned i lomma. I koppen: merket opp. Lodd E06 på USB-C-kontakten, snu foten, '
                          'senk kontakten ned bak ribba med leidningane gjennom sporet, skyv han ut i lomma og fyll spalta med epoksy.')
    m = int(12 * MM)
    midt = A4[0] // 2
    ya, yb_ = int(46 * MM), int(128 * MM)
    # 1  hovudet opp-ned: lommene i magnetringen opnar seg oppover; dei to som ligg bak veggen er stipla
    sh = (L.HOV_X, 0.0, (L.HOV_Z0 + L.HOV_Z1) / 2)
    v = Vising([snudd(D['D02'], 'x', sh)], STEIL)
    P = v.teikn(dr, (m + int(12 * MM), ya + int(12 * MM), midt - int(10 * MM), yb_))
    u = np.array(STEIL[0][:2]) / np.linalg.norm(STEIL[0][:2])          # vassrett, mot kameraet
    lommer = [snu_pkt(L.polar(L.MAGNET_R, a) + (L.RING_Z0,), 'x', sh) for a in L.MAGNET_VINKLAR]
    synleg = min(lommer, key=lambda o: (o[0] - L.HOV_X) * u[0] + o[1] * u[1])
    for o in lommer:
        if o is synleg:
            pil(dr, P((o[0], o[1], o[2] + 40)), P((o[0], o[1], o[2] + 1)))
        else:
            stipla_ring(dr, [P((o[0] + 3.1 * math.cos(t_), o[1] + 3.1 * math.sin(t_), o[2]))
                             for t_ in np.linspace(0, 2 * math.pi, 24, endpoint=False)])
    q = P((synleg[0], synleg[1], synleg[2] + 40))
    mengd(dr, (q[0] - 44 * MM, q[1] - 10 * MM), 'M06 ×3')
    etikett(dr, (q[0] - 44 * MM, q[1] - 1 * MM), 'merket ned i lomma')
    p = P((L.HOV_X + 40, 0, sh[2] - 20))
    ballong(dr, p, (p[0] + 8 * MM, p[1] + 12 * MM), 'D02')
    # 2  koppen rett veg: lommene på toppflata
    v = Vising([D['D06']], FH)
    P = v.teikn(dr, (midt + int(12 * MM), ya + int(30 * MM), A4[0] - m - int(4 * MM), yb_ - int(2 * MM)))
    for a in L.MAGNET_VINKLAR:
        x, y = L.polar(L.MAGNET_R, a)
        pil(dr, P((x, y, L.RING_Z0 + 26)), P((x, y, L.RING_Z0 + 1)))
    q = P((L.HOV_X + 40, 0, L.RING_Z0 + 32))
    tw = max(dr.textlength('M06 ×3', font=font(12, True)), dr.textlength('merket opp', font=font(9)))
    xl = min(q[0] - 2 * MM, A4[0] - 10 * MM - tw - 2 * MM)
    mengd(dr, (xl, q[1] - 14 * MM), 'M06 ×3')
    etikett(dr, (xl, q[1] - 5 * MM), 'merket opp')
    p = P((L.HOV_X - 30, -20, 200))
    ballong(dr, p, (p[0] - 12 * MM, p[1] + 10 * MM), 'D06')
    # 3  USB-C i den snudde foten: oversikt, så to forstørringar (kontakten på veg ned, og på plass med epoksy)
    sf = (L.USB_X, 0.0, (L.FOT_BOTN + L.FOT_Z) / 2)
    fot, usb = snudd(D['D03'], 'y', sf), snudd(D['E04'], 'y', sf)
    yb0 = L.FOT_B / 2 - L.VEGG + 1.0 - 8.8                     # baksida av kontakten (29,8)
    zf = snu_pkt((L.USB_X, 0, L.USB_Z), 'y', sf)[2]             # midt i kontakten i den snudde foten (20)
    yk = yb0 + 4.4                                              # midt i kontakten
    v = Vising([fot, usb], FH)
    P = v.teikn(dr, (int(58 * MM), int(134 * MM), int(152 * MM), int(170 * MM)))
    pf = P((L.USB_X, yk, zf))
    rr = 6 * MM
    dr.ellipse([pf[0] - rr, pf[1] - rr, pf[0] + rr, pf[1] + rr], outline=(0, 0, 0), width=2)
    p = P((L.USB_X + 40, -L.FOT_B / 2, sf[2]))
    ballong(dr, p, (p[0] + 16 * MM, p[1] - 2 * MM), 'D03')
    # A: kontakten 2,4 mm attende, ned bak ribba, så ut i lomma
    tmp = Image.new('RGB', (A4[0] * 2, A4[1] * 2), (255, 255, 255))
    dt = ImageDraw.Draw(tmp)
    PA = Vising([fot, usb.translate(V(0, -2.4, 24))], FH).teikn(dt, (0, 0, tmp.width, tmp.height), tjukk=2.2)
    xs_ = L.USB_X + 11.0                                        # rørsla ved sida av kontakten: ned, så ut
    pil(dt, PA((xs_, yk - 2.4, zf + 30)), PA((xs_, yk - 2.4, zf + 0.5)), tjukk=6)
    pil(dt, PA((xs_, yk - 2.4, zf)), PA((xs_, yk + 7, zf)), tjukk=6)
    leidning = []
    for dx in (-1.3, 1.3):                                      # E06, lodda på før kontakten går inn
        a0, a1, a2 = (np.array(t_, float) for t_ in ((L.USB_X + dx, yb0 - 2.4, zf + 24), (L.USB_X + dx, yb0 - 12, zf + 25),
                                                          (L.USB_X + dx * 2 - 7, yb0 - 15, zf + 12)))
        tr = [tuple((1 - s) ** 2 * a0 + 2 * (1 - s) * s * a1 + s ** 2 * a2) for s in np.linspace(0, 1, 16)]
        dt.line([PA(t_) for t_ in tr], fill=(0, 0, 0), width=5, joint='curve')
        leidning.append(tr)
    sA, rA = (int(58 * MM), int(216 * MM)), 38 * MM
    TA = forstorr(im, tmp, PA((L.USB_X, yk - 1.2, zf + 12)), 0.1 * tmp.width, sA, rA)
    dr = ImageDraw.Draw(im)
    vv = np.array(sA, float) - np.array(pf, float)
    vv /= np.linalg.norm(vv)
    dr.line([tuple(np.array(pf) + vv * rr), tuple(np.array(sA) - vv * rA)], fill=(0, 0, 0), width=2)
    p = TA(PA((L.USB_X + 3, yk - 2.4, zf + 26.5)))
    ballong(dr, p, (p[0] - 20 * MM, p[1] - 4 * MM), 'E04')
    p = TA(PA(leidning[0][10]))
    leiar(dr, p, (sA[0] - rA + 4 * MM, sA[1] - rA - 3 * MM), 'E06 lodda på først')
    # B: på plass, sett nesten rett ovanfrå; epoksy i spalta mellom ribba og kontakten
    tmp = Image.new('RGB', (A4[0] * 2, A4[1] * 2), (255, 255, 255))
    dt = ImageDraw.Draw(tmp)
    NESTEN = ((0.15, -0.35, 1.0), (1.0, 0.0, -0.15))
    PB = Vising([fot, usb], NESTEN).teikn(dt, (0, 0, tmp.width, tmp.height), tjukk=2.2)
    ztopp = snu_pkt((0, 0, L.USB_Z - 2.5), 'y', sf)[2]          # toppen av kontakten i den snudde foten (22,5)
    skraver(tmp, [PB((L.USB_X - 5.5, yb0 - L.USB_SPALTE, ztopp)), PB((L.USB_X + 5.5, yb0 - L.USB_SPALTE, ztopp)),
                  PB((L.USB_X + 5.5, yb0, ztopp)), PB((L.USB_X - 5.5, yb0, ztopp))])
    sB, rB = (int(154 * MM), int(216 * MM)), 38 * MM
    TB = forstorr(im, tmp, PB((L.USB_X, yb0 + 1.0, ztopp)), 0.065 * tmp.width, sB, rB)
    dr = ImageDraw.Draw(im)
    p = TB(PB((L.USB_X + 4.5, yb0 - 1.5, ztopp)))
    leiar(dr, p, (sB[0] + rB - 4 * MM, sB[1] + 22 * MM), 'epoksy')
    p = TB(PB((L.USB_X - 6, yb0 - L.USB_SPALTE - 2.0, 25.0)))
    leiar(dr, p, (sB[0] - rB + 6 * MM, sB[1] + 26 * MM), 'ribbe')
    pil(dr, (sA[0] + rA + 3 * MM, sA[1]), (sB[0] - rB - 3 * MM, sB[1]))
    # stabelen med tusjmerke, og herdetida
    x0, yy0 = int(14 * MM), int(270 * MM)
    for i in range(6):
        dr.rectangle([x0, yy0 + i * int(3.0 * MM), x0 + int(9 * MM), yy0 + i * int(3.0 * MM) + int(2.6 * MM)],
                     outline=(0, 0, 0), width=2)
    dr.ellipse([x0 + int(3.4 * MM), yy0 - int(3.0 * MM), x0 + int(5.6 * MM), yy0 - int(0.8 * MM)], fill=(0, 0, 0))
    etikett(dr, (x0 + int(13 * MM), yy0 - int(1 * MM)), 'tusjmerke på toppen av stabelen')
    etikett(dr, (x0 + int(13 * MM), yy0 + int(5 * MM)), 'ta av éin og éin frå toppen: merket er same pol på alle seks')
    dr.text((A4[0] - int(40 * MM), yy0), '24 t', font=font(26, True), fill=(0, 0, 0))
    return im


def s06_kabel_og_hovud(nr):
    """Steg 3. Kabelen gjennom bladet, hovudet på, to skruar frå innsida."""
    xi = L.HOV_X - L.HOV_R
    S = sett(['D01', 'D02'], {'D02': (70, 0, 0)})
    _, k = L.kanal()

    def etter(im, dr, P, v):
        pts = [(62, 0, 31), (k['Ta'][0], 0, k['Ta'][1]),
               (k['C'][0] + 15 * math.cos(math.radians(110)), 0, k['C'][1] + 15 * math.sin(math.radians(110))),
               (k['Tb'][0], 0, k['Tb'][1]), (xi + 40, 0, L.HOV_KABEL_Z)]
        for a, b in zip(pts, pts[1:]):
            stipla(dr, P(a), P(b), w=3)
        pil(dr, P((62, 0, -10)), P((62, 0, 25)))
        etikett(dr, (P((62, 0, -10))[0] - 30 * MM, P((62, 0, -10))[1] + 2 * MM), 'E05, 650 mm', font(11, True))
        pil(dr, P((xi + 80, 0, 205)), P((xi + 8, 0, 205)), True)
        for zc in L.HOV_SKRUAR_Z:
            pil(dr, P((xi + 70 + 36, 0, zc)), P((xi + 70 + 8, 0, zc)))
        q = P((xi + 70 + 36, 0, 284))
        mengd(dr, (q[0] - 4 * MM, q[1] - 14 * MM), 'M04 ×2')
        etikett(dr, (q[0] - 4 * MM, q[1] - 5 * MM), '2,5 mm, lange armen inn')

    return stegside(nr, 3, 'Trekk kabelen gjennom bladet. Skyv hovudet på, kabelen gjennom holet i veggen, '
                           'og skru frå innsida med lang unbrakonøkkel opp gjennom ringen.', S, FRAMME,
                    (int(12 * MM), int(46 * MM), A4[0] - int(12 * MM), A4[1] - int(60 * MM)),
                    ballongar=[('D01', (60, 0, 120), (-22, 0), 'D01'), ('D02', (L.HOV_X + 70 + 20, 0, 230), (20, 16), 'D02')],
                    etter=etter)


def s07_fot_elektronikk(nr):
    """Steg 4. Foten sett nedanfrå: potensiometeret opp gjennom topplata. Boble: mutteren på toppen."""
    im, dr = side(nr, 4, 'Kapp akselen til 15 mm frå monteringsflata, det vil seie 8 mm over halsen. Potensiometeret opp '
                          'gjennom foten med tappen i ei av dei fire lommene, så kortet peikar mot den runde enden. Mutteren på.')
    S = sett(['D03', 'E02', 'E03', 'E04'], {'E02': (0, 0, -60), 'E03': (0, 0, -60)})
    v = Vising(list(S.values()), UNDER_BRATT)
    P = v.teikn(dr, (int(14 * MM), int(50 * MM), A4[0] - int(14 * MM), int(190 * MM)))
    pil(dr, P((L.KNOTT_X, 0, -34)), P((L.KNOTT_X, 0, 22)))
    for pid, p3, (dx, dy) in (('D03', (40, -40, 16), (-22, -16)), ('E02', None, (20, -24)), ('E03', None, (26, 16))):
        q = P(p3 if p3 else boks_senter(S[pid]))
        ballong(dr, q, (q[0] + dx * MM, q[1] + dy * MM), pid)
    p = P((L.KNOTT_X + L.LUG_R, 0, L.FOT_Z - L.FOT_TAK))
    leiar(dr, p, (p[0] + 16 * MM, p[1] - 22 * MM), 'lomme for tappen ×4')
    tmp = Image.new('RGB', (A4[0] * 2, A4[1] * 2), (255, 255, 255))
    dt = ImageDraw.Draw(tmp)
    S2 = sett(['D03', 'E02', 'E02b'], {'E02b': (0, 0, 26)})
    v2 = Vising(list(S2.values()), FH)
    P2 = v2.teikn(dt, (0, 0, tmp.width, tmp.height), tjukk=2.2)
    pil(dt, P2((L.KNOTT_X, 0, 66)), P2((L.KNOTT_X, 0, 40)), tjukk=6)
    c = P2((L.KNOTT_X, 0, 50))
    rk = 0.085 * tmp.width
    boble(im, (A4[0] - 52 * MM, 238 * MM), 40 * MM, (c[0] - rk, c[1] - rk, c[0] + rk, c[1] + rk), tmp)
    dr = ImageDraw.Draw(im)
    etikett(dr, (A4[0] - 92 * MM, 238 * MM + 43 * MM), 'E02b · fastnøkkel 10 mm')
    etikett(dr, (int(14 * MM), int(204 * MM)), 'Passar ikkje tappen i lommene:')
    etikett(dr, (int(14 * MM), int(209 * MM)), 'knip han av og legg ei tannskive under mutteren.')
    return im


def s08_blad_paa_fot(nr):
    """Steg 5. Bladet på foten, tre M4 frå undersida."""
    S = sett(['D01', 'D02', 'D03', 'E02', 'E03', 'E02b', 'E04'] + SKRUAR_M03,
             {**{p: (0, 0, -70) for p in SKRUAR_M03}, 'D01': (0, 0, 60), 'D02': (0, 0, 60)})

    def etter(im, dr, P, v):
        for x, y in L.BLAD_SKRUAR:
            pil(dr, P((x, y, -48)), P((x, y, 16)))
        pil(dr, P((20, 0, 150)), P((20, 0, 105)), True)
        q = P((104, 11, -60))
        mengd(dr, (q[0] + 6 * MM, q[1] - 2 * MM), 'M03 ×3')
        etikett(dr, (q[0] + 6 * MM, q[1] + 7 * MM), '3 mm, handstramt')
        kx, ky = L.KABEL_FOT                                   # E05 ut av kanalen i bladet og ned gjennom holet i foten
        pil(dr, P((kx, ky, L.FOT_Z + 60)), P((kx, ky, L.FOT_Z - L.FOT_TAK - 1)), tjukk=4)
        p = P((kx, ky, L.FOT_Z + 30))
        etikett(dr, (p[0] + 3 * MM, p[1] - 2 * MM), 'E05', font(10, True))

    return stegside(nr, 5, 'Træ kabelen ned gjennom foten. Set bladet på og skru frå undersida, berre handstramt.', S, UNDER,
                    (int(14 * MM), int(44 * MM), A4[0] - int(14 * MM), A4[1] - int(26 * MM)),
                    ballongar=[('D01', (70, -20, 160), (-26, -10), 'D01'), ('D03', (150, -40, 18), (16, 14), 'D03')],
                    etter=etter)


def s09_led_i_koppen(nr):
    """Steg 6. Lyskoppen sett nedanfrå: kabelen gjennom spalta med knute over, kjøleplata med termisk teip i taket,
    kabelen lodda på framsida av LED-kortet, kortet med termisk teip på kjøleplata."""
    dz8, dz1 = -40, -84
    S = sett(['D06', 'D08', 'E01'] + MAGNET_KOPP, {'D08': (0, 0, dz8), 'E01': (0, 0, dz1)})
    a = math.radians(L.KABEL_SPOR_VINKEL)
    sx, sy = L.HOV_X + L.KABEL_SPOR_R * math.cos(a), L.KABEL_SPOR_R * math.sin(a)
    zk = L.RING_Z0 - 2.0                                       # undersida av taket i koppen (215)
    z8 = zk - L.KJOL_T + dz8                                   # undersida av kjøleplata, flytt ned
    z1 = zk - L.KJOL_T - L.LED_T + dz1                         # framsida av LED-kortet, flytt ned

    def etter(im, dr, P, v):
        stipla(dr, P((L.HOV_X, 0, z1 - 20)), P((L.HOV_X, 0, zk + 6)), 3.0, 1.2, 2)      # aksen gjennom Ø 6-hola
        pil(dr, P((L.HOV_X, 0, z1 - 46)), P((L.HOV_X, 0, z1 - 6)))
        stipla(dr, P((sx, sy, 238)), P((sx, sy, z1 - 0.4)), w=4)
        p = P((sx, sy, L.RING_Z0 + 3))
        stipla_sirkel(dr, p, 2.4 * MM)
        leiar(dr, p, (p[0] + 16 * MM, p[1] - 20 * MM), 'knute over spalta')
        p = P((L.HOV_X + L.LED_R, 0, z1 + 0.8))
        leiar(dr, p, (p[0] + 16 * MM, p[1] + 14 * MM), 'lodd på framsida ved kanten')
        p = P((L.HOV_X + 3, 0, z8))
        leiar(dr, p, (p[0] + 40 * MM, p[1] + 2 * MM), 'Ø 6: sentrer med eit 6 mm bor')
        p = P((L.HOV_X - 16, -10, z8))
        leiar(dr, p, (p[0] - 26 * MM, p[1] - 16 * MM), 'M08 termisk teip på begge sider')

    return stegside(nr, 6, 'Knyt ein knute på kabelen og træ han ned gjennom spalta, så knuten ligg over. Fest kjøleplata i '
                           'taket med termisk teip. Lodd kabelen på framsida av LED-kortet ved kanten, og fest kortet på '
                           'kjøleplata med termisk teip. La 80 mm kabel liggje laust i hovudet.',
                    S, UNDER, (int(54 * MM), int(50 * MM), A4[0] - int(54 * MM), A4[1] - int(62 * MM)),
                    ballongar=[('D06', (L.HOV_X - L.KOPP_RY, 0, 205), (-14, -12), 'D06'),
                               ('D08', (L.HOV_X - 24, -6, z8 + 0.75), (-16, 12), 'D08'),
                               ('E01', (L.HOV_X - 24, -6, z1 + 0.8), (-16, 12), 'E01')],
                    etter=etter)


def s10_kopling(nr):
    """Steg 7. Koplingsskjema og open lysprøve: koppen heng under hovudet, foten er open."""
    im, dr = side(nr, 7, 'Lodd som vist. Prøv lyset med koppen hengjande under hovudet og foten open: '
                          'vri akselen med fingrane.')
    f, g = font(10, True), font(8.5)
    y = int(52 * MM)
    w, h = int(32 * MM), int(24 * MM)
    boksar = [('E04', 'USB-C', 'VBUS · GND', 10), ('E02', 'brytar', 'i potensiometeret', 60),
              ('E03', 'PWM-dimmar', 'IN · OUT', 110), ('E01', 'LED', '+  −', 160)]
    pos = {}
    for pid, namn, pinnar, xmm in boksar:
        x = int(xmm * MM)
        dr.rectangle([x, y, x + w, y + h], outline=(0, 0, 0), width=3)
        dr.text((x + int(3 * MM), y + int(3 * MM)), pid, font=f, fill=(0, 0, 0))
        dr.text((x + int(3 * MM), y + int(10 * MM)), namn, font=font(10), fill=(0, 0, 0))
        dr.text((x + int(3 * MM), y + int(16.5 * MM)), pinnar, font=g, fill=(0, 0, 0))
        pos[pid] = x

    def tekst_midt(x0, x1, yy, s):
        dr.text(((x0 + x1) / 2 - dr.textlength(s, font=g) / 2, yy - int(5.5 * MM)), s, font=g, fill=(0, 0, 0))

    yl = y + int(7 * MM)
    for a_, b_, s in (('E04', 'E02', '+5 V, E06'), ('E02', 'E03', '+5 V, E06'), ('E03', 'E01', 'OUT+, E05')):
        dr.line([(pos[a_] + w, yl), (pos[b_], yl)], fill=(0, 0, 0), width=4)
        tekst_midt(pos[a_] + w, pos[b_], yl, s)
    yg = y + h + int(10 * MM)
    xa, xb = pos['E04'] + w // 2, pos['E03'] + w // 3
    dr.line([(xa, y + h), (xa, yg), (xb, yg), (xb, y + h)], fill=(0, 0, 0), width=4)
    tekst_midt(xa, xb, yg + int(7 * MM), 'GND, E06')
    yo = y + h + int(20 * MM)
    xc, xd = pos['E03'] + 2 * w // 3, pos['E01'] + w // 2
    dr.line([(xc, y + h), (xc, yo), (xd, yo), (xd, y + h)], fill=(0, 0, 0), width=4)
    tekst_midt(xc, xd, yo + int(7 * MM), 'OUT−, E05')
    S = sett(['D01', 'D02', 'D03', 'D06', 'D08', 'E01', 'E02', 'E03', 'E04'],
             {'D06': (0, 0, -70), 'D08': (0, 0, -70), 'E01': (0, 0, -70)})
    v = Vising(list(S.values()), FH)
    P = v.teikn(dr, (int(30 * MM), int(124 * MM), A4[0] - int(30 * MM), A4[1] - int(44 * MM)))
    a = math.radians(L.KABEL_SPOR_VINKEL)
    sx, sy = L.HOV_X + L.KABEL_SPOR_R * math.cos(a), L.KABEL_SPOR_R * math.sin(a)
    stipla(dr, P((sx, sy, L.HOV_Z0 + 2)), P((sx, sy, L.RING_Z0 - 70)), 1.6, 1.2, 3)
    for k in (-1, 0, 1):
        stipla(dr, P((L.HOV_X + 22 * k, 0, 120)), P((L.HOV_X + 36 * k, 0, 76)), 1.6, 1.2, 3)
    boge = [P((L.KNOTT_X + 12 * math.cos(math.radians(b)), 12 * math.sin(math.radians(b)), 50)) for b in range(200, 341, 5)]
    dr.line(boge, fill=(0, 0, 0), width=4)
    pil(dr, boge[-3], boge[-1], tjukk=4)
    q = boge[-1]
    etikett(dr, (q[0] + 2 * MM, q[1] + 7 * MM), 'av · på · dimme', g)
    liner = ['Prøv med C-til-C-kabel frå ein PD-ladar, begge vegar inn: lyset skal kome kvar gong.',
             'Lyset skal vere stødig på lågaste styrke, også sett gjennom sakte film på mobilen.']
    for i, t in enumerate(liner):
        dr.text((int(10 * MM), A4[1] - int((30 - 5.5 * i) * MM)), t, font=g, fill=(0, 0, 0))
    return im


def s11_koppen_inn(nr):
    """Steg 8. Spreiaren inn i koppen nedanfrå, koppen opp i hovudet."""
    S = sett(['D02', 'D06', 'D08', 'E01', 'D07'] + MAGNET_HOV + MAGNET_KOPP,
             {'D06': (0, 0, -55), 'D08': (0, 0, -55), 'E01': (0, 0, -55), **{p: (0, 0, -55) for p in MAGNET_KOPP},
              'D07': (0, 0, -100)})

    def etter(im, dr, P, v):
        pil(dr, P((L.HOV_X - 46, 0, 166)), P((L.HOV_X - 46, 0, 190)))
        pil(dr, P((L.HOV_X - 46, 0, 102)), P((L.HOV_X - 46, 0, 134)))
        p = P((L.HOV_X + 40, 0, 194))
        etikett(dr, (p[0] + 6 * MM, p[1] - 2 * MM), 'klikk', font(11, True))

    return stegside(nr, 8, 'Bøy spreiaren lett og smett han inn i koppen nedanfrå. Skyv koppen opp i hovudet til magnetane tek.',
                    S, UNDER, (int(30 * MM), int(44 * MM), A4[0] - int(30 * MM), A4[1] - int(26 * MM)),
                    ballongar=[('D02', None, (24, -18), 'D02'), ('D06', None, (28, 4), 'D06'), ('D07', None, (26, 10), 'D07')],
                    etter=etter)


KAPTON = (125.0, 185.0, -20.0, 20.0)                            # x0, x1, y0, y1: 60 × 40 under dimmarkortet, innanfor plata


def s12_botn_og_knott(nr):
    """Steg 9. Kaptonteip på oversida av botnplata, plata med fire senkskruar, føtene og knotten."""
    pids = ['D01', 'D02', 'D03', 'D04', 'D05', 'E02b'] + SKRUAR_M05 + [p for p in D if p.startswith('M07')]
    S = sett(pids, {'D04': (0, 0, -40), **{p: (0, 0, -70) for p in SKRUAR_M05}, **{p: (0, 0, -58) for p in D if p.startswith('M07')},
                    'D05': (0, 0, 40)})

    def etter(im, dr, P, v):
        for x, y in L.PLATE_SKRUAR:
            pil(dr, P((x, y, -64)), P((x, y, -42)))
        q = P((135, 31, -75))
        mengd(dr, (q[0] + 4 * MM, q[1]), 'M05 ×4')
        etikett(dr, (q[0] + 4 * MM, q[1] + 8 * MM), '2,0 mm')
        q = P((172, 26, -60))
        mengd(dr, (q[0] + 10 * MM, q[1] - 12 * MM), 'M07 ×4')
        pil(dr, P((L.KNOTT_X, 0, 115)), P((L.KNOTT_X, 0, 92)))
        p = P((L.KNOTT_X, 0, 120))
        etikett(dr, (p[0] + 4 * MM, p[1] - 4 * MM), 'ned til han stoppar')
        # boble: botnplata sett ovanfrå med kaptonteipen på oversida
        tmp = Image.new('RGB', (A4[0], A4[1]), (255, 255, 255))
        dt = ImageDraw.Draw(tmp)
        vp = Vising([D['D04']], FH)
        Pp = vp.teikn(dt, (int(10 * MM), int(10 * MM), A4[0] - int(10 * MM), A4[1] // 3), tjukk=1.6)
        zt = L.FOT_BOTN + L.PLATE_T
        x0_, x1_, y0_, y1_ = KAPTON
        hj = [Pp((x, y, zt)) for x, y in ((x0_, y0_), (x1_, y0_), (x1_, y1_), (x0_, y1_))]
        skraver(tmp, hj, steg=10, w=2)
        xs, ys = [h[0] for h in hj], [h[1] for h in hj]
        side_ = max(max(xs) - min(xs), max(ys) - min(ys)) + 80
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        sb, rb = (int(50 * MM), int(84 * MM)), 30 * MM
        boble(im, sb, rb, (cx - side_ / 2, cy - side_ / 2, cx + side_ / 2, cy + side_ / 2), tmp)
        dr2 = ImageDraw.Draw(im)
        etikett(dr2, (sb[0] - rb, sb[1] + rb + 3 * MM), 'M09 kaptonteip 60 × 40 på oversida av D04')

    return stegside(nr, 9, 'Kaptonteip på oversida av botnplata, under dimmarkortet. Skru plata fast med senkskruane, lim på '
                           'føtene, og press knotten ned til han stoppar.', S, UNDER,
                    (int(14 * MM), int(60 * MM), A4[0] - int(14 * MM), A4[1] - int(24 * MM)),
                    ballongar=[('D04', None, (-26, 12), 'D04'), ('D05', None, (22, -12), 'D05')],
                    etter=etter)


def s13_ferdig(nr):
    im, dr = side(nr, None, 'Ferdig')
    v = Vising([D[p] for p in SYNLEGE], FV)
    v.teikn(dr, (int(30 * MM), int(24 * MM), A4[0] - int(30 * MM), int(160 * MM)))
    f, g = font(10, True), font(9)
    y = int(170 * MM)
    rader = [('Lyset kjem ikkje', 'Snu knotten heilt mot venstre og tilbake: brytaren sit i potensiometeret. Verkar det '
                                  'berre med A-til-C-kabel, manglar E04 CC-motstandar. Byt kontakten.'),
             ('Lyset blinkar svakt', 'Dimmaren skal ha PWM på minst 3 kHz. Byt dimmarkortet, ikkje LED-en.'),
             ('Hovudet blir varmt', 'Mål etter 60 min på full styrke: LED-kortet høgst 60 °C og koppen under '
                                    'magnetringen høgst 45 °C. Over dette: svakare LED, eller hovudet i PETG (plate 5), '
                                    'som toler LED opp til 2 W.'),
             ('Koppen fell ut', 'Ein magnet står feil veg: i hovudet skal tusjmerket vere skjult, i koppen synleg.'),
             ('Lampa vippar', 'Med stålplata står ho til 22° og med PLA-plata til 15°; kravet er 6°. Sjekk at alle '
                              'fire føtene sit på.'),
             ('Plata går ikkje i', 'Mål falsen i foten før du bestiller stålplata: minst 192,0 × 77,0 mm.')]
    for t, s in rader:
        dr.text((int(14 * MM), y), t, font=f, fill=(0, 0, 0))
        ord_, linje_, yy = s.split(), '', y + int(5.5 * MM)
        for o in ord_:
            if dr.textlength(linje_ + ' ' + o, font=g) > A4[0] - int(80 * MM):
                dr.text((int(70 * MM), yy - int(5.5 * MM)), linje_.strip(), font=g, fill=(0, 0, 0))
                linje_, yy = o, yy + int(4.6 * MM)
            else:
                linje_ += ' ' + o
        dr.text((int(70 * MM), yy - int(5.5 * MM)), linje_.strip(), font=g, fill=(0, 0, 0))
        y = yy + int(4 * MM)
    return im


SIDELISTE = [s01_framside, s02_delar, s03_sprengt, s04_mutrar, s05_lim, s06_kabel_og_hovud, s07_fot_elektronikk,
             s08_blad_paa_fot, s09_led_i_koppen, s10_kopling, s11_koppen_inn, s12_botn_og_knott, s13_ferdig]


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
        bilete[0].save(HER / 'Lut-montering.pdf', save_all=True, append_images=bilete[1:], resolution=DPI)
        print('PDF skriven', flush=True)


if __name__ == '__main__':
    main()
