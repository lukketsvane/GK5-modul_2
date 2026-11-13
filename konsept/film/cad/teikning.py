# -*- coding: utf-8 -*-
"""
teikning.py  ·  strekteikningar av lampa rett frå CAD-en: skjulte kantar fjerna, svart strek på kvitt

  python teikning.py         lagar sidene i ut/ark/ og samlar dei i ut/ruta-pa-fot-montering.pdf
"""
import os, sys, math, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cadquery as cq
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Pnt2d
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepLib import BRepLib
import lampe as L

HER = os.path.dirname(os.path.abspath(__file__))
ARK = os.path.join(L.UT, 'ark')
DPI = 200
A4 = (int(297 / 25.4 * DPI), int(210 / 25.4 * DPI))          # liggjande
MM = DPI / 25.4
ISO = ((-1.0, -1.35, 0.85), (1.0, -0.74, 0.0))                 # sett frå framme til venstre, litt ovanfrå (som skissa)
FRAMME = ((0.0, -1.0, 0.0), (1.0, 0.0, 0.0))
SIDE = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0))

def font(pt, feit=False):
    for f in (('arialbd.ttf' if feit else 'arial.ttf'), 'DejaVuSans.ttf'):
        try: return ImageFont.truetype(f, int(pt * DPI / 72))
        except Exception: pass
    return ImageFont.load_default()

class Vising:
    """Éi projeksjon av eit sett former. Gjev kantane som polylinjer i mm i teikneplanet."""
    def __init__(s, former, retning=ISO):
        syn, xr = retning
        s.proj = HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*syn), gp_Dir(*xr)))
        algo = HLRBRep_Algo()
        for f in former: algo.Add(f.val().wrapped if hasattr(f, 'val') else f)
        algo.Projector(s.proj); algo.Update(); algo.Hide()
        h = HLRBRep_HLRToShape(algo)
        s.liner = []          # (vekt, punkt)
        for vekt, comp in ((1.0, h.VCompound()), (1.6, h.OutLineVCompound()), (0.6, h.Rg1LineVCompound())):
            if comp is None or comp.IsNull(): continue
            BRepLib.BuildCurves3d_s(comp)
            exp = TopExp_Explorer(comp, TopAbs_EDGE)
            while exp.More():
                c = BRepAdaptor_Curve(TopoDS.Edge_s(exp.Current()))
                d = GCPnts_QuasiUniformDeflection(c, 0.05)
                if d.IsDone() and d.NbPoints() > 1:
                    s.liner.append((vekt, [(d.Value(i).X(), d.Value(i).Y()) for i in range(1, d.NbPoints() + 1)]))
                exp.Next()
        P = np.array([p for _, pk in s.liner for p in pk])
        s.min = P.min(0); s.max = P.max(0)
    def punkt(s, p):
        q = gp_Pnt2d(); s.proj.Project(gp_Pnt(*p), q); return (q.X(), q.Y())
    def teikn(s, dr, ramme, skala=None, tjukk=1.0):
        """Teiknar inn i ramma (x0, y0, x1, y1) i pikslar. Gjev funksjonen som flyttar mm i teikneplanet til pikslar."""
        x0, y0, x1, y1 = ramme
        b = s.max - s.min
        k = min((x1 - x0) / b[0], (y1 - y0) / b[1]) if skala is None else skala * MM
        ox = x0 + ((x1 - x0) - b[0] * k) / 2; oy = y0 + ((y1 - y0) - b[1] * k) / 2
        f = lambda p: (ox + (p[0] - s.min[0]) * k, oy + (s.max[1] - p[1]) * k)
        for vekt, pk in s.liner:
            dr.line([f(p) for p in pk], fill=(0, 0, 0), width=max(1, int(round(vekt * tjukk * DPI / 140))))
        s.k = k / MM
        return f

def flytt(form, v):
    return form.translate(tuple(v))

def side(tittel, nr, tal=None):
    im = Image.new('RGB', A4, (255, 255, 255)); dr = ImageDraw.Draw(im)
    m = int(8 * MM)
    dr.rectangle([m, m, A4[0] - m, A4[1] - m], outline=(0, 0, 0), width=2)
    if tal is not None:
        dr.text((m + int(6 * MM), m + int(4 * MM)), str(tal), font=font(40, True), fill=(0, 0, 0))
        dr.text((m + int(22 * MM), m + int(8.5 * MM)), tittel, font=font(15), fill=(0, 0, 0))
    else:
        dr.text((m + int(6 * MM), m + int(5 * MM)), tittel, font=font(15, True), fill=(0, 0, 0))
    dr.text((A4[0] - m - int(60 * MM), A4[1] - m - int(7 * MM)), 'Ruta på fot · rev. A · 13.11.2026 · side %d' % nr, font=font(8), fill=(0, 0, 0))
    return im, dr

def ballong(dr, p, q, tekst, r=None):
    """Nummer i sirkel ved q, med leiar frå p."""
    r = int(4.2 * MM) if r is None else r
    dr.line([p, q], fill=(0, 0, 0), width=2)
    dr.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=(0, 0, 0))
    dr.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
    f = font(11, True); w = dr.textlength(tekst, font=f)
    dr.text((q[0] - w / 2, q[1] - int(2.1 * MM)), tekst, font=f, fill=(0, 0, 0))

def pil(dr, a, b, w=3):
    dr.line([a, b], fill=(0, 0, 0), width=w)
    v = np.array(b, float) - np.array(a, float); l = np.linalg.norm(v)
    if l < 1: return
    v /= l; n = np.array([-v[1], v[0]]); s = 3.2 * MM
    dr.polygon([tuple(b), tuple(np.array(b) - v * s + n * s * 0.45), tuple(np.array(b) - v * s - n * s * 0.45)], fill=(0, 0, 0))

def maal(dr, a, b, tekst, forskyv=(0, 0)):
    """Mållinje mellom to pikselpunkt, med tekst midt på."""
    a = (a[0] + forskyv[0], a[1] + forskyv[1]); b = (b[0] + forskyv[0], b[1] + forskyv[1])
    dr.line([a, b], fill=(0, 0, 0), width=1)
    for p, q in ((a, b), (b, a)):
        v = np.array(q, float) - np.array(p, float); v /= max(np.linalg.norm(v), 1e-6); n = np.array([-v[1], v[0]]); s = 2.2 * MM
        dr.polygon([tuple(p), tuple(np.array(p) + v * s + n * s * 0.3), tuple(np.array(p) + v * s - n * s * 0.3)], fill=(0, 0, 0))
    f = font(9); w = dr.textlength(tekst, font=f)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dr.rectangle([mx - w / 2 - 4, my - 0.9 * MM * 2.2, mx + w / 2 + 4, my + 0.9 * MM * 2.2], fill=(255, 255, 255))
    dr.text((mx - w / 2, my - 1.7 * MM), tekst, font=f, fill=(0, 0, 0))

# ------------------------------------------------------------------ eksplodering

def eksplodert(vinkel=L.VINKEL):
    """Flyttar delane frå kvarandre langs retninga dei blir sette inn. Gjev {id: (form, senter)}."""
    D = L.delar(vinkel)
    t = math.radians(vinkel)
    s = np.array([0.0, -math.cos(t), -math.sin(t)]); n = np.array([0.0, -math.sin(t), math.cos(t)])
    bj = np.array([-70.0, 0.0, 45.0])            # bjelkegruppa: ut til venstre og opp
    F = {'01': (0, 0, 0), '02': (0, 0, -55), '03': (0, 0, -28), '04': (0, 0, 45), '05': (0, 45, 45), 'D': (0, 0, 100),
         '06': (0, -30, 45), '14': (-28, -30, 45), 'C': (30, -30, 45), 'B': (48, -30, 45), '13': (75, -30, 45),
         '07': bj + (0, -30, 0), 'A': bj + (0, -30, 0), '11': bj + (0, -30, 0) + n * 26, '12': bj + (0, -30, 0) + n * 40,
         '08': bj + (0, -30, 0) + n * 62, 'E': bj + (0, -30, 0) + n * 95,
         '09': bj + (0, -30, 0) + s * 45, '10': bj + (0, -30, 0) + s * 45 + n * 24}
    ut = {}
    for (i, namn, form, *_r) in D:
        f = flytt(form, F[i])
        c = f.val().BoundingBox().center
        ut[i] = (f, (c.x, c.y, c.z), namn)
    return ut, D

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    import time
    os.makedirs(ARK, exist_ok=True)
    t0 = time.time()
    D = L.delar()
    former = [d[2] for d in D]
    sider = []

    # 1 framside
    im, dr = side('', 1)
    v = Vising(former, ISO)
    v.teikn(dr, (int(40 * MM), int(34 * MM), A4[0] - int(40 * MM), A4[1] - int(26 * MM)))
    dr.text((int(16 * MM), int(14 * MM)), 'RUTA PÅ FOT', font=font(30, True), fill=(0, 0, 0))
    dr.text((int(16 * MM), int(27 * MM)), 'Monteringsrettleiing · målestokk 1:%.1f' % (1 / v.k), font=font(10), fill=(0, 0, 0))
    im.save(os.path.join(ARK, 'side-1-framside.png')); sider.append(im); print('side 1 %.0f s' % (time.time() - t0), flush=True)

    # 2 eksplodert oversikt med delnummer
    E, _ = eksplodert()
    im, dr = side('Delane', 2)
    v = Vising([e[0] for e in E.values()], ISO)
    f = v.teikn(dr, (int(14 * MM), int(22 * MM), int(205 * MM), A4[1] - int(14 * MM)))
    # ballongane: (id, forskyving i mm på arket frå senteret til delen)
    PL = {'01': (-30, 12), '02': (-28, 10), '03': (-30, 8), '04': (34, 22), '05': (30, -6), 'D': (22, -10), '06': (8, -26), '14': (-6, -24),
          'C': (10, -22), 'B': (16, -18), '13': (22, -10), '07': (-34, 30), 'A': (-10, 28), '11': (-44, 10), '12': (-46, -2),
          '08': (-44, -12), 'E': (-30, -20), '09': (-40, 34), '10': (-52, 14)}
    for i, (form, c, namn) in E.items():
        p = f(v.punkt(c)); dx, dy = PL[i]
        ballong(dr, p, (p[0] + dx * MM, p[1] + dy * MM), i)
    # delliste
    x0 = int(212 * MM); y = int(24 * MM)
    dr.text((x0, y), 'Nr.  Del', font=font(9, True), fill=(0, 0, 0)); dr.text((A4[0] - int(20 * MM), y), 'Tal', font=font(9, True), fill=(0, 0, 0))
    y += int(6 * MM)
    for (i, namn, _f, mat, _c, n, pr) in D:
        dr.text((x0, y), '%-3s' % i, font=font(9, True), fill=(0, 0, 0)); dr.text((x0 + int(9 * MM), y), namn, font=font(9), fill=(0, 0, 0))
        dr.text((A4[0] - int(18 * MM), y), '× %d' % n, font=font(9), fill=(0, 0, 0)); y += int(5.6 * MM)
    dr.line([x0, y + 4, A4[0] - int(12 * MM), y + 4], fill=(0, 0, 0), width=1); y += int(4 * MM)
    for (i, namn, n, _m) in L.LAUSE:
        dr.text((x0, y), '%-3s' % i, font=font(9, True), fill=(0, 0, 0)); dr.text((x0 + int(9 * MM), y), namn, font=font(9), fill=(0, 0, 0))
        dr.text((A4[0] - int(18 * MM), y), '× %d' % n, font=font(9), fill=(0, 0, 0)); y += int(5.6 * MM)
    im.save(os.path.join(ARK, 'side-2-delane.png')); sider.append(im); print('side 2 %.0f s' % (time.time() - t0), flush=True)

    # 3 mål: framme og frå sida
    im, dr = side('Hovudmål i mm', 3)
    sk = 0.42
    v = Vising(former, FRAMME)
    f = v.teikn(dr, (int(14 * MM), int(26 * MM), int(175 * MM), A4[1] - int(30 * MM)), skala=sk)
    P = lambda x, y, z: f(v.punkt((x, y, z)))
    yb = int(8 * MM)
    maal(dr, P(-L.FOT_D / 2, 0, 0), P(L.FOT_D / 2, 0, 0), 'Ø %.0f' % L.FOT_D, (0, int(9 * MM)))
    maal(dr, P(L.X_RUTE0, 0, 0), P(L.X_RUTE1, 0, 0), '%.0f' % L.RUTE_B, (0, int(18 * MM)))
    maal(dr, P(L.X_BJ0, 0, L.AKSE_H + 30), P(L.X_KN0 + L.KNOTT_L, 0, L.AKSE_H + 30), '%.0f' % (L.X_KN0 + L.KNOTT_L - L.X_BJ0), (0, -int(6 * MM)))
    maal(dr, P(L.X_KN0 + L.KNOTT_L + 14, 0, 0), P(L.X_KN0 + L.KNOTT_L + 14, 0, L.AKSE_H), '%.0f' % L.AKSE_H, (int(4 * MM), 0))
    maal(dr, P(L.XF - 20, 0, 60), P(L.XF + 20, 0, 60), '%.0f' % L.ARM_B, (0, 0))
    v2 = Vising(former, SIDE)
    f2 = v2.teikn(dr, (int(185 * MM), int(26 * MM), A4[0] - int(20 * MM), A4[1] - int(30 * MM)), skala=sk)
    Q = lambda x, y, z: f2(v2.punkt((x, y, z)))
    t = math.radians(L.VINKEL)
    kant = (0, L.YB - math.cos(t) * (L.U_KANT + L.RUTE_D), L.AKSE_H - math.sin(t) * (L.U_KANT + L.RUTE_D))
    maal(dr, Q(0, L.YB, L.AKSE_H), Q(*kant), '%.0f' % L.RUTE_D, (-int(5 * MM), -int(7 * MM)))
    maal(dr, Q(0, kant[1], 0), Q(0, kant[1], kant[2]), '%.0f' % kant[2], (-int(6 * MM), 0))
    maal(dr, Q(0, -L.FOT_D / 2, 0), Q(0, L.FOT_D / 2, 0), 'Ø %.0f' % L.FOT_D, (0, int(9 * MM)))
    dr.text((int(190 * MM), A4[1] - int(26 * MM)), 'Hellinga på ruta: %.0f° til %.0f° under vassrett. Teikna ved %.0f°.' % (*L.VINKEL_OMRAADE, L.VINKEL), font=font(9), fill=(0, 0, 0))
    dr.text((int(16 * MM), A4[1] - int(26 * MM)), 'Framme · 1:%.2f' % (1 / sk), font=font(9), fill=(0, 0, 0))
    im.save(os.path.join(ARK, 'side-3-maal.png')); sider.append(im); print('side 3 %.0f s' % (time.time() - t0), flush=True)

    sider[0].save(os.path.join(L.UT, 'ruta-pa-fot-teikningar.pdf'), save_all=True, append_images=sider[1:], resolution=DPI)
    print('pdf ferdig')
