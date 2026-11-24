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


def mengd(dr, p, tekst, storleik=12):
    dr.text(p, tekst, font=font(storleik, True), fill=(0, 0, 0))


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
        [('D08', 1), ('E01', 1), ('E02', 1), ('E03', 1), ('E04', 1)],
    ]
    y = int(28 * MM)
    hogder = [int(78 * MM), int(52 * MM), int(42 * MM)]
    for rad, h in zip(rader, hogder):
        b = (A4[0] - int(20 * MM)) / len(rad)
        for i, (pid, n) in enumerate(rad):
            x0 = int(10 * MM + i * b)
            ramme = (x0 + int(6 * MM), y + int(10 * MM), int(x0 + b - 6 * MM), y + h - int(8 * MM))
            Vising([D[pid]], FH).teikn(dr, ramme)
            dr.ellipse([x0 + int(2 * MM), y, x0 + int(12 * MM), y + int(10 * MM)], outline=(0, 0, 0), width=3)
            f = font(9.5, True)
            lab = pid
            dr.text((x0 + int(7 * MM) - dr.textlength(lab, font=f) / 2, y + int(2.6 * MM)), lab, font=f, fill=(0, 0, 0))
            dr.text((x0 + int(14 * MM), y + int(2.2 * MM)), f'×{n}', font=font(11, True), fill=(0, 0, 0))
        y += h
    # beslag
    dr.line([(int(10 * MM), y), (A4[0] - int(10 * MM), y)], fill=(0, 0, 0), width=2)
    y += int(4 * MM)
    beslag = [('M01', 'M4', 3, 'innpress'), ('M02', 'M3', 6, 'innpress'), ('M03', 'M4×16', 3, ''),
              ('M04', 'M3×10', 2, ''), ('M05', 'M3×8', 4, ''), ('M06', 'Ø6×3', 6, 'magnet'), ('M07', 'Ø10×2', 4, 'fot')]
    b = (A4[0] - int(20 * MM)) / len(beslag)
    for i, (pid, mal, n, kva) in enumerate(beslag):
        x0 = int(10 * MM + i * b)
        cx = x0 + b / 2
        dr.text((cx - dr.textlength(pid, font=font(10, True)) / 2, y), pid, font=font(10, True), fill=(0, 0, 0))
        # enkel teikning av beslaget
        yy = y + int(9 * MM)
        if pid in ('M01', 'M02'):
            w, h = (5.6, 8) if pid == 'M01' else (4.2, 5.7)
            dr.rectangle([cx - w * MM, yy, cx + w * MM, yy + h * 2 * MM], outline=(0, 0, 0), width=3)
            for k in range(1, 4):
                yk = yy + k * h * 2 * MM / 4
                dr.line([(cx - w * MM, yk), (cx + w * MM, yk)], fill=(0, 0, 0), width=2)
        elif pid in ('M03', 'M04', 'M05'):
            d_, l_ = {'M03': (4, 16), 'M04': (3, 10), 'M05': (3, 8)}[pid]
            hh = 1.65 if pid == 'M05' else d_
            s_ = 1.25
            dr.rectangle([cx - d_ * 0.85 * s_ * MM, yy, cx + d_ * 0.85 * s_ * MM, yy + hh * s_ * MM], outline=(0, 0, 0), width=3)
            dr.rectangle([cx - d_ / 2 * s_ * MM, yy + hh * s_ * MM, cx + d_ / 2 * s_ * MM, yy + (hh + l_) * s_ * MM], outline=(0, 0, 0), width=3)
            for k in range(int(l_)):
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
        dr.text((cx - dr.textlength(mal, font=font(8.5)) / 2, y + int(40 * MM)), mal, font=font(8.5), fill=(0, 0, 0))
        dr.text((cx - dr.textlength(f'×{n}', font=font(12, True)) / 2, y + int(46 * MM)), f'×{n}', font=font(12, True), fill=(0, 0, 0))
    y += int(58 * MM)
    dr.line([(int(10 * MM), y), (A4[0] - int(10 * MM), y)], fill=(0, 0, 0), width=2)
    verk = 'Loddebolt · unbrakonøkkel 2,0 · 2,5 · 3,0 mm · fastnøkkel 10 mm · tokomponent epoksy · E05 kabel 2 × 0,25 mm², 450 mm'
    dr.text((int(10 * MM), y + int(4 * MM)), verk, font=font(9), fill=(0, 0, 0))
    return im


SPRENG = {
    'D02': (95, 0, 0), 'M06-1': (95, 0, 0), 'M06-2': (95, 0, 0), 'M06-3': (95, 0, 0),
    'D06': (95, 0, -85), 'M06-4': (95, 0, -85), 'M06-5': (95, 0, -85), 'M06-6': (95, 0, -85),
    'D07': (95, 0, -115), 'E01': (95, 0, -62), 'D08': (95, 0, -48),
    'M04-1': (150, 0, 0), 'M04-2': (150, 0, 0),
    'D05': (0, 0, 75), 'E02b': (0, 0, 48),
    'D03': (0, 0, -90), 'E02': (0, 0, -90), 'E03': (0, 0, -90), 'E04': (0, 0, -90),
    'M03-1': (0, 0, -140), 'M03-2': (0, 0, -140), 'M03-3': (0, 0, -140),
    'D04': (0, 0, -175), 'M05-1': (0, 0, -205), 'M05-2': (0, 0, -205), 'M05-3': (0, 0, -205), 'M05-4': (0, 0, -205),
    'M07-1': (0, 0, -192), 'M07-2': (0, 0, -192), 'M07-3': (0, 0, -192), 'M07-4': (0, 0, -192),
}


def s03_sprengt(nr):
    im, dr = side(nr, None, 'Oversikt')
    pids = [p for p in D if not p.startswith(('M04', 'M06')) and p != 'E04']     # vist i stega i staden
    S = sett(pids, SPRENG)
    v = Vising(list(S.values()), FH)
    P = v.teikn(dr, (int(14 * MM), int(26 * MM), A4[0] - int(30 * MM), A4[1] - int(16 * MM)))
    plass = {'D01': (-30, -22), 'D02': (18, -26), 'D06': (24, 6), 'D07': (24, 14), 'E01': (26, -6), 'D08': (30, -14),
             'D05': (-20, -18), 'E02b': (-24, -6), 'D03': (-34, 6), 'E02': (22, 22), 'E03': (30, 12),
             'D04': (-30, 10), 'M03-1': (-20, 10), 'M05-1': (-22, 12), 'M07-4': (24, 10)}
    for pid, (dx, dy) in plass.items():
        p = P(boks_senter(S[pid]))
        lab = pid.split('-')[0]
        ballong(dr, p, (p[0] + dx * MM, p[1] + dy * MM), lab, r=5.4)
    return im


def stegside(nr, tal, tekst, S, retning, ramme, ballongar=(), piler=(), stiplar=(), mengder=(), etter=None):
    im, dr = side(nr, tal, tekst)
    v = Vising(list(S.values()), retning)
    P = v.teikn(dr, ramme)
    for pid, p3, (dx, dy), lab in ballongar:
        p = P(p3 if p3 is not None else boks_senter(S[pid]))
        ballong(dr, p, (p[0] + dx * MM, p[1] + dy * MM), lab)
    for a, b, *val in piler:
        pil(dr, P(a), P(b), hol=bool(val and val[0]))
    for a, b in stiplar:
        stipla(dr, P(a), P(b))
    for p3, (dx, dy), t in mengder:
        p = P(p3)
        mengd(dr, (p[0] + dx * MM, p[1] + dy * MM), t)
    if etter:
        etter(im, dr, P, v)
    return im


def s04_mutrar(nr):
    """Innpressmutrar: 3 × M4 i rota av bladet, 2 × M3 i enden, 4 × M3 i tårna i foten."""
    blad_ned = sett(['D01'])
    xi = L.HOV_X - L.HOV_R
    im, dr = side(nr, 1, 'Varm inn mutrane med loddebolten, 230 °C. Plant med flata.')
    v1 = Vising(list(blad_ned.values()), UNDER)
    P = v1.teikn(dr, (int(12 * MM), int(32 * MM), int(118 * MM), int(150 * MM)))
    for x, y in L.BLAD_SKRUAR:
        a, b = (x, y, L.FOT_Z - 30), (x, y, L.FOT_Z - 1)
        pil(dr, P(a), P(b))
    mengd(dr, (P((60, 0, L.FOT_Z - 34))[0] - 18 * MM, P((60, 0, L.FOT_Z - 34))[1] + 4 * MM), 'M01 ×3')
    for zc in L.HOV_SKRUAR_Z:
        pil(dr, P((xi + 34, 0, zc)), P((xi + 1, 0, zc)))
    mengd(dr, (P((xi + 34, 0, 250))[0] + 2 * MM, P((xi + 34, 0, 250))[1] - 4 * MM), 'M02 ×2')
    # foten opp-ned
    fot = D['D03'].rotate(V(0, 0, 0), V(1, 0, 0), 180).translate(V(0, 0, 40))
    v2 = Vising([fot], FH)
    P2 = v2.teikn(dr, (int(92 * MM), int(150 * MM), A4[0] - int(12 * MM), A4[1] - int(22 * MM)))
    for x, y in L.PLATE_SKRUAR:
        z_tarn = 40 - (L.FOT_BOTN + L.PLATE_T)          # botnen av tårnet etter snuing
        pil(dr, P2((x, -y, z_tarn + 28)), P2((x, -y, z_tarn + 1)))
    pt = P2((40, 31, 70))
    mengd(dr, (pt[0] - 26 * MM, pt[1] - 10 * MM), 'M02 ×4')
    return im


def s05_kabel_og_hovud(nr):
    xi = L.HOV_X - L.HOV_R
    S = sett(['D01', 'D02'], {'D02': (70, 0, 0)})
    _, k = L.kanal()

    def etter(im, dr, P, v):
        # kabelen gjennom kanalen, stipla
        pts = [(62, 0, 31), k['Ta'], (k['C'][0] + 15 * math.cos(math.radians(110)), 0, k['C'][1] + 15 * math.sin(math.radians(110))), k['Tb'], (xi + 40, 0, L.HOV_KABEL_Z)]
        pts = [(p[0], 0, p[1]) if len(p) == 2 else p for p in pts]
        for a, b in zip(pts, pts[1:]):
            stipla(dr, P(a), P(b), w=3)
        pil(dr, P((62, 0, -10)), P((62, 0, 25)))
        dr.text((P((62, 0, -10))[0] - 8 * MM, P((62, 0, -10))[1] + 2 * MM), 'E05', font=font(11, True), fill=(0, 0, 0))
        pil(dr, P((xi + 80, 0, 205)), P((xi + 8, 0, 205)), True)
        for zc in L.HOV_SKRUAR_Z:
            pil(dr, P((xi + 70 + 36, 0, zc)), P((xi + 70 + 8, 0, zc)))
        q = P((xi + 70 + 36, 0, 280))
        mengd(dr, (q[0] - 4 * MM, q[1] - 12 * MM), 'M04 ×2')
        dr.text((q[0] - 4 * MM, q[1] - 4 * MM), '2,5 mm', font=font(9), fill=(0, 0, 0))

    return stegside(nr, 2, 'Trekk kabelen gjennom bladet. Skyv hovudet på og skru frå innsida.', S, FRAMME,
                    (int(12 * MM), int(40 * MM), A4[0] - int(12 * MM), A4[1] - int(60 * MM)),
                    ballongar=[('D01', (60, 0, 120), (-22, 0), 'D01'), ('D02', (L.HOV_X + 70 + 20, 0, 262), (18, -12), 'D02')],
                    etter=etter)


def s06_fot_elektronikk(nr):
    """Foten sett nedanfrå: potensiometeret med kortet opp gjennom topplata, USB-C-kontakten ut i lomma bak.
    Boble: mutteren på toppen."""
    im, dr = side(nr, 3, 'Potensiometeret opp gjennom foten, mutteren på. USB-C-kontakten limast inn i lomma bak.')
    S = sett(['D03', 'E02', 'E03', 'E04'], {'E02': (0, 0, -60), 'E03': (0, 0, -60), 'E04': (0, -26, 0)})
    v = Vising(list(S.values()), UNDER)
    P = v.teikn(dr, (int(14 * MM), int(44 * MM), A4[0] - int(14 * MM), int(196 * MM)))
    pil(dr, P((L.KNOTT_X, 0, -34)), P((L.KNOTT_X, 0, 4)))
    pil(dr, P((L.USB_X, 2, L.USB_Z)), P((L.USB_X, 30, L.USB_Z)))
    for pid, p3, (dx, dy) in (('D03', (40, -40, 16), (-22, -16)), ('E02', None, (-26, 14)), ('E03', None, (26, 16)),
                              ('E04', None, (-30, -12))):
        q = P(p3 if p3 else boks_senter(S[pid]))
        ballong(dr, q, (q[0] + dx * MM, q[1] + dy * MM), pid)
    q = P(boks_senter(S['E04']))
    dr.text((q[0] - 52 * MM, q[1] - 2 * MM), 'epoksy', font=font(9), fill=(0, 0, 0))
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
    dr.text((A4[0] - 92 * MM, 238 * MM + 43 * MM), 'E02b · fastnøkkel 10 mm', font=font(9), fill=(0, 0, 0))
    return im


def s07_blad_paa_fot(nr):
    S = sett(['D01', 'D02', 'D03', 'E02', 'E03', 'E02b'] + SKRUAR_M03, {**{p: (0, 0, -70) for p in SKRUAR_M03}, 'D01': (0, 0, 60), 'D02': (0, 0, 60)})

    def etter(im, dr, P, v):
        for x, y in L.BLAD_SKRUAR:
            pil(dr, P((x, y, -48)), P((x, y, 16)))
        pil(dr, P((20, 0, 150)), P((20, 0, 105)), True)
        q = P((104, 11, -60))
        mengd(dr, (q[0] + 6 * MM, q[1] - 2 * MM), 'M03 ×3')
        dr.text((q[0] + 6 * MM, q[1] + 6 * MM), '3 mm', font=font(9), fill=(0, 0, 0))
        q = P((62, 0, 40))
        dr.text((q[0] - 36 * MM, q[1] - 2 * MM), 'kabelen ned først', font=font(9), fill=(0, 0, 0))

    return stegside(nr, 4, 'Set bladet på foten. Skru frå undersida.', S, UNDER,
                    (int(14 * MM), int(40 * MM), A4[0] - int(14 * MM), A4[1] - int(26 * MM)),
                    ballongar=[('D01', (70, -20, 160), (-26, -10), 'D01'), ('D03', (150, -40, 18), (16, 14), 'D03')],
                    etter=etter)


def s08_kopling(nr):
    """Koplingsskjema og open funksjonsprøve før botnplata går på."""
    im, dr = side(nr, 5, 'Kople som vist. Prøv lyset før foten blir lukka.')
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
    for a, b, s in (('E04', 'E02', '+5 V'), ('E02', 'E03', '+5 V'), ('E03', 'E01', 'OUT+ (E05)')):
        dr.line([(pos[a] + w, yl), (pos[b], yl)], fill=(0, 0, 0), width=4)
        tekst_midt(pos[a] + w, pos[b], yl, s)
    yg = y + h + int(10 * MM)
    xa, xb = pos['E04'] + w // 2, pos['E03'] + w // 3
    dr.line([(xa, y + h), (xa, yg), (xb, yg), (xb, y + h)], fill=(0, 0, 0), width=4)
    tekst_midt(xa, xb, yg + int(7 * MM), 'GND')
    yo = y + h + int(20 * MM)
    xc, xd = pos['E03'] + 2 * w // 3, pos['E01'] + w // 2
    dr.line([(xc, y + h), (xc, yo), (xd, yo), (xd, y + h)], fill=(0, 0, 0), width=4)
    tekst_midt(xc, xd, yo + int(7 * MM), 'OUT− (E05)')
    S = sett(['D01', 'D02', 'D03', 'D05', 'D06', 'D07', 'E02', 'E03', 'E04'])
    v = Vising(list(S.values()), FH)
    P = v.teikn(dr, (int(30 * MM), int(120 * MM), A4[0] - int(30 * MM), A4[1] - int(30 * MM)))
    for k in (-1, 0, 1):
        stipla(dr, P((L.HOV_X + 22 * k, 0, 186)), P((L.HOV_X + 36 * k, 0, 140)), 1.6, 1.2, 3)
    boge = [P((L.KNOTT_X + 17 * math.cos(math.radians(a)), 17 * math.sin(math.radians(a)), 56)) for a in range(200, 341, 5)]
    dr.line(boge, fill=(0, 0, 0), width=4)
    pil(dr, boge[-3], boge[-1], tjukk=4)
    q = boge[len(boge) // 2]
    dr.text((q[0] + 16 * MM, q[1] + 10 * MM), 'av · på · dimme', font=g, fill=(0, 0, 0))
    dr.text((int(10 * MM), A4[1] - int(22 * MM)), 'USB-C sit bak på foten: 5 V, minst 1 A.', font=g, fill=(0, 0, 0))
    return im


def s09_lyskopp(nr):
    """Sett nedanfrå: hovudet med magnetringen, koppen under, så kjøleplate, LED og spreiar som går opp i koppen."""
    S = sett(['D02', 'D06', 'D07', 'D08', 'E01'] + MAGNET_HOV + MAGNET_KOPP,
             {'D06': (0, 0, -60), **{p: (0, 0, -60) for p in MAGNET_KOPP}, 'D08': (0, 0, -92), 'E01': (0, 0, -112),
              'D07': (0, 0, -150)})

    def etter(im, dr, P, v):
        pil(dr, P((L.HOV_X - 50, 0, 130)), P((L.HOV_X - 50, 0, 170)))
        pil(dr, P((L.HOV_X - 50, 0, 60)), P((L.HOV_X - 50, 0, 92)))
        q = P((L.HOV_X + 44, 0, 214))
        dr.text((q[0] + 4 * MM, q[1] - 2 * MM), 'M06 ×3: S ned', font=font(9.5, True), fill=(0, 0, 0))
        q = P((L.HOV_X + 44, 0, 154))
        dr.text((q[0] + 4 * MM, q[1] - 2 * MM), 'M06 ×3: N opp', font=font(9.5, True), fill=(0, 0, 0))
        q = P((L.HOV_X - 44, 0, 110))
        dr.text((q[0] - 40 * MM, q[1]), 'termisk teip', font=font(9), fill=(0, 0, 0))
        q = P((L.HOV_X - 44, 0, 180))
        dr.text((q[0] - 40 * MM, q[1]), 'klikk', font=font(9), fill=(0, 0, 0))

    return stegside(nr, 6, 'Lim magnetane. Kjøleplate og LED inn i koppen, spreiaren inn nedanfrå. Koppen opp i hovudet.',
                    S, UNDER, (int(24 * MM), int(44 * MM), A4[0] - int(24 * MM), A4[1] - int(24 * MM)),
                    ballongar=[('D02', None, (24, -18), 'D02'), ('D06', None, (28, 2), 'D06'), ('D08', None, (-30, -6), 'D08'),
                               ('E01', None, (30, 6), 'E01'), ('D07', None, (26, 10), 'D07')],
                    etter=etter)


def s10_botn_og_knott(nr):
    pids = ['D01', 'D02', 'D03', 'D04', 'D05', 'E02b'] + SKRUAR_M05 + [p for p in D if p.startswith('M07')]
    S = sett(pids, {'D04': (0, 0, -40), **{p: (0, 0, -70) for p in SKRUAR_M05}, **{p: (0, 0, -58) for p in D if p.startswith('M07')},
                    'D05': (0, 0, 40)})

    def etter(im, dr, P, v):
        for x, y in L.PLATE_SKRUAR:
            pil(dr, P((x, y, -64)), P((x, y, -42)))
        q = P((135, 31, -75))
        mengd(dr, (q[0] + 4 * MM, q[1]), 'M05 ×4')
        dr.text((q[0] + 4 * MM, q[1] + 8 * MM), '2,0 mm', font=font(9), fill=(0, 0, 0))
        q = P((172, 26, -60))
        mengd(dr, (q[0] + 8 * MM, q[1] - 8 * MM), 'M07 ×4')
        pil(dr, P((L.KNOTT_X, 0, 115)), P((L.KNOTT_X, 0, 92)))

    return stegside(nr, 7, 'Skru botnplata fast og lim på føtene. Press knotten på akselen.', S, UNDER,
                    (int(14 * MM), int(36 * MM), A4[0] - int(14 * MM), A4[1] - int(24 * MM)),
                    ballongar=[('D04', None, (-26, 12), 'D04'), ('D05', None, (22, -12), 'D05')],
                    etter=etter)


def s11_ferdig(nr):
    im, dr = side(nr, None, 'Ferdig')
    v = Vising([D[p] for p in SYNLEGE], FV)
    v.teikn(dr, (int(30 * MM), int(24 * MM), A4[0] - int(30 * MM), int(170 * MM)))
    f, g = font(10, True), font(9)
    y = int(182 * MM)
    rader = [('Lyset kjem ikkje', 'Snu knotten heilt mot venstre og tilbake: brytaren sit i potensiometeret. Prøv ein annan USB-C-ladar (5 V, minst 1 A).'),
             ('Lyset blinkar ved låg styrke', 'Dimmaren må ha PWM over 1 kHz. Byt dimmarkortet, ikkje LED-en.'),
             ('Hovudet blir varmt', 'LED-en skal vere 2 W eller mindre og liggje på kjøleplata. Over 60 °C på kortet etter ein time: bruk ein svakare LED.'),
             ('Koppen fell ut', 'Ein magnet står feil veg. Alle tre i hovudet med S ned, alle tre i koppen med N opp.'),
             ('Lampa vippar', 'Botnplata skal vere av stål. Med botnplata i PLA må stål (skiver, flattstål) limast inn i foten.')]
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


SIDELISTE = [s01_framside, s02_delar, s03_sprengt, s04_mutrar, s05_kabel_og_hovud, s06_fot_elektronikk,
             s07_blad_paa_fot, s08_kopling, s09_lyskopp, s10_botn_og_knott, s11_ferdig]


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
