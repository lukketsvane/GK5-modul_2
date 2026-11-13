# -*- coding: utf-8 -*-
"""
teikning.py  ·  strekteikningar av lampa rett frå CAD-en: skjulte kantar fjerna, svart strek på kvitt

  python teikning.py            lagar sidene i ut/ark/ og samlar dei i ut/ruta-pa-fot-montering.pdf
  python teikning.py 3 5        berre desse sidene (til prøving)
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
BAK = ((1.0, 1.35, 0.85), (-1.0, 0.74, 0.0))                   # sett bakfrå til høgre
FRAMH = ((1.0, -1.35, 0.85), (1.0, 0.74, 0.0))                  # sett frå framme til høgre
FRAMME = ((0.0, -1.0, 0.0), (1.0, 0.0, 0.0))
SIDE = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0))

def font(pt, feit=False):
    for f in (('arialbd.ttf' if feit else 'arial.ttf'), 'DejaVuSans.ttf'):
        try: return ImageFont.truetype(f, int(pt * DPI / 72))
        except Exception: pass
    return ImageFont.load_default()

class Vising:
    """Éi projeksjon av eit sett former. Kantane blir polylinjer i mm i teikneplanet."""
    def __init__(s, former, retning=ISO):
        syn, xr = retning
        s.proj = HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*syn), gp_Dir(*xr)))
        algo = HLRBRep_Algo()
        for f in former: algo.Add(f.val().wrapped if hasattr(f, 'val') else f)
        algo.Projector(s.proj); algo.Update(); algo.Hide()
        h = HLRBRep_HLRToShape(algo)
        s.liner = []
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
        """Teiknar inn i ramma (x0, y0, x1, y1) i pikslar. Gjev funksjonen frå mm i teikneplanet til pikslar."""
        x0, y0, x1, y1 = ramme
        b = s.max - s.min
        k = min((x1 - x0) / b[0], (y1 - y0) / b[1]) if skala is None else skala * MM
        ox = x0 + ((x1 - x0) - b[0] * k) / 2; oy = y0 + ((y1 - y0) - b[1] * k) / 2
        f = lambda p: (ox + (p[0] - s.min[0]) * k, oy + (s.max[1] - p[1]) * k)
        for vekt, pk in s.liner:
            dr.line([f(p) for p in pk], fill=(0, 0, 0), width=max(1, int(round(vekt * tjukk * DPI / 140))))
        s.k = k / MM
        return f

def side(tittel, nr, tal=None):
    im = Image.new('RGB', A4, (255, 255, 255)); dr = ImageDraw.Draw(im)
    m = int(8 * MM)
    dr.rectangle([m, m, A4[0] - m, A4[1] - m], outline=(0, 0, 0), width=2)
    if tal is not None:
        dr.text((m + int(6 * MM), m + int(4 * MM)), str(tal), font=font(40, True), fill=(0, 0, 0))
        dr.text((m + int(22 * MM), m + int(8.5 * MM)), tittel, font=font(15), fill=(0, 0, 0))
    elif tittel:
        dr.text((m + int(6 * MM), m + int(5 * MM)), tittel, font=font(15, True), fill=(0, 0, 0))
    dr.text((A4[0] - m - int(60 * MM), A4[1] - m - int(7 * MM)), 'Ruta på fot · rev. A · 13.11.2026 · side %d' % nr, font=font(8), fill=(0, 0, 0))
    return im, dr

def ballong(dr, p, q, tekst):
    r = int(4.2 * MM)
    dr.line([p, q], fill=(0, 0, 0), width=2)
    dr.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=(0, 0, 0))
    dr.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
    f = font(11, True); w = dr.textlength(tekst, font=f)
    dr.text((q[0] - w / 2, q[1] - int(2.1 * MM)), tekst, font=f, fill=(0, 0, 0))

def maal(dr, a, b, tekst, forskyv=(0, 0)):
    a = (a[0] + forskyv[0], a[1] + forskyv[1]); b = (b[0] + forskyv[0], b[1] + forskyv[1])
    dr.line([a, b], fill=(0, 0, 0), width=1)
    for p, q in ((a, b), (b, a)):
        v = np.array(q, float) - np.array(p, float); v /= max(np.linalg.norm(v), 1e-6); n = np.array([-v[1], v[0]]); s = 2.2 * MM
        dr.polygon([tuple(p), tuple(np.array(p) + v * s + n * s * 0.3), tuple(np.array(p) + v * s - n * s * 0.3)], fill=(0, 0, 0))
    f = font(9); w = dr.textlength(tekst, font=f)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dr.rectangle([mx - w / 2 - 4, my - 2.0 * MM, mx + w / 2 + 4, my + 2.0 * MM], fill=(255, 255, 255))
    dr.text((mx - w / 2, my - 1.7 * MM), tekst, font=f, fill=(0, 0, 0))

def retningar(vinkel=L.VINKEL):
    t = math.radians(vinkel)
    return np.array([0.0, -math.cos(t), -math.sin(t)]), np.array([0.0, -math.sin(t), math.cos(t)])

def gruppe(D, flytting):
    """Delane i flytting = {id: vektor}, flytte frå kvarandre langs retninga dei blir sette inn."""
    ut = {}
    for (i, namn, form, *_r) in D:
        if i not in flytting: continue
        f = form.translate(tuple(float(x) for x in flytting[i])); c = f.val().BoundingBox().center
        ut[i] = (f, (c.x, c.y, c.z))
    return ut

def stegside(nr, tal, tittel, G, plass, ramme, tekst, retning=ISO, anker=None):
    im, dr = side(tittel, nr, tal)
    v = Vising([g[0] for g in G.values()], retning)
    f = v.teikn(dr, ramme)
    for i, (form, c) in G.items():
        if i not in plass: continue
        p = f(v.punkt((anker or {}).get(i, c))); dx, dy = plass[i]
        ballong(dr, p, (p[0] + dx * MM, p[1] + dy * MM), i)
    y = A4[1] - int(14 * MM) - int(5.2 * MM) * len(tekst)
    for t in tekst:
        dr.text((int(16 * MM), y), t, font=font(9.5), fill=(0, 0, 0)); y += int(5.2 * MM)
    return im

STEG = {
    '3': dict(tal=1, tittel='Foten og armen', fil='side-3-fot-og-arm.png', retning=FRAMH,
              flytting={'02': (0, 0, -100), '03': (0, 0, -50), '01': (0, 0, 0), '04': (0, 0, 55), 'D': (0, 0, 115), '05': (0, 75, 55), '06': (0, -55, 55)},
              plass={'02': (-34, 8), '03': (-36, 2), '01': (-38, -4), '04': (-34, -4), 'D': (-22, -14), '05': (26, -10), '06': (-24, -16)},
              anker={'03': (-30, -45, 13.6 - 50), '02': (-30, -55, -99), '01': (-45, -50, 16)},
              ramme=(70, 24, 230, 176),
              tekst=['Press innpressmutrane H i foten (3) og I i leddhuset (2).',
                     'Legg ballasten 03 i foten. Skru armen 04 fast gjennom foten og inn i ballasten med D.',
                     'Skru leddhuset 06 til armen med F bakfrå. Lim kabeldekselet 05 på baksida av armen. Skru på botnloket 02 med G til slutt.']),
    '4': dict(tal=2, tittel='Bjelken og ruta', fil='side-4-bjelke-og-rute.png', retning=ISO,
              flytting='bjelke',
              plass={'07': (-30, 26), 'A': (22, 10), '11': (-52, 4), '12': (-50, -8), '09': (34, 30), '10': (-46, 26), '08': (-40, -16), 'E': (-26, -18)},
              ramme=(40, 22, 262, 172),
              tekst=['Legg bolten A i lomma i høgre ende av bjelken 07. Lim LED-stripa 12 på flatstonga 11 og legg ho i sporet. Før leidningen ut bak.',
                     'Legg lysleiaren 09 i spalta med den skrå kanten ned. Legg prismearket 10 oppå, med prisma opp og rillene på tvers av bjelken.',
                     'Legg på loket 08 og skru til med E gjennom plata. Stram til arket ligg flatt, ikkje hardare.']),
    '5': dict(tal=3, tittel='Leddet', fil='side-5-leddet.png', retning=ISO,
              flytting='ledd',
              plass={'14': (-4, -24), '06': (6, 24), 'C': (2, -22), 'B': (8, -20), '13': (16, -16), '07': (-20, -24)},
              ramme=(40, 22, 262, 172),
              tekst=['Tre friksjonsskiva 14 på bolten. Stikk bolten gjennom leddhuset 06 slik at stoppinnen på bjelken går i sporet.',
                     'Tre på skivene C (nylon inst) og låsemutteren B. Trykk knotten 13 over mutteren.',
                     'Stram med knotten til ruta står i ro, men kan vippast med éi hand. Prøv heile området frå flat til bratt.']),
}

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    import time
    os.makedirs(ARK, exist_ok=True)
    t0 = time.time()
    D = L.delar()
    former = [d[2] for d in D]
    s_, n_ = retningar()
    kva = sys.argv[1:] or ['1', '2', '3', '4', '5', '6']
    px = lambda r: tuple(int(x * MM) for x in r)

    if '1' in kva:
        im, dr = side('', 1)
        v = Vising(former, ISO)
        v.teikn(dr, px((40, 34, 257, 184)))
        dr.text(px((16, 14)), 'RUTA PÅ FOT', font=font(30, True), fill=(0, 0, 0))
        dr.text(px((16, 27)), 'Monteringsrettleiing · målestokk 1:%.1f' % (1 / v.k), font=font(10), fill=(0, 0, 0))
        im.save(os.path.join(ARK, 'side-1-framside.png')); print('side 1 %.0f s' % (time.time() - t0), flush=True)

    if '2' in kva:
        im, dr = side('Delane', 2)
        y = int(24 * MM); kol = px((16, 27, 78, 92))
        for x, t in zip(kol, ('Nr.', 'Del', 'Tal', 'Materiale og framstilling')): dr.text((x, y), t, font=font(9, True), fill=(0, 0, 0))
        y += int(6.5 * MM); dr.line([kol[0], y - 6, A4[0] - int(16 * MM), y - 6], fill=(0, 0, 0), width=1)
        for (i, namn, _f, mat, _c, n, pr) in D:
            dr.text((kol[0], y), i, font=font(9, True), fill=(0, 0, 0)); dr.text((kol[1], y), namn, font=font(9), fill=(0, 0, 0))
            dr.text((kol[2], y), '× %d' % n, font=font(9), fill=(0, 0, 0)); dr.text((kol[3], y), pr, font=font(9), fill=(0, 0, 0)); y += int(5.9 * MM)
        dr.line([kol[0], y + 2, A4[0] - int(16 * MM), y + 2], fill=(0, 0, 0), width=1); y += int(3 * MM)
        for (i, namn, n, m) in L.LAUSE:
            dr.text((kol[0], y), i, font=font(9, True), fill=(0, 0, 0)); dr.text((kol[1], y), namn, font=font(9), fill=(0, 0, 0))
            dr.text((kol[2], y), '× %d' % n, font=font(9), fill=(0, 0, 0)); dr.text((kol[3], y), m, font=font(9), fill=(0, 0, 0)); y += int(5.9 * MM)
        dr.text((kol[0], A4[1] - int(20 * MM)), 'Verktøy: sekskantnøklar 2, 2,5 og 3 mm · fastnøkkel 13 mm · loddebolt til innpressmutrane · sag, fil og skrustikke til armen',
                font=font(9), fill=(0, 0, 0))
        im.save(os.path.join(ARK, 'side-2-delane.png'))

    for k in ('3', '4', '5'):
        if k not in kva: continue
        S = STEG[k]
        if S['flytting'] == 'bjelke':
            fl = {'07': (0, 0, 0), 'A': (0, 0, 0), '11': n_ * 26, '12': n_ * 42, '09': s_ * 55, '10': s_ * 55 + n_ * 26, '08': n_ * 66, 'E': n_ * 100}
        elif S['flytting'] == 'ledd':
            fl = {i: (0, 0, 0) for i in ('01', '02', '03', '04', '05', '06', 'D')}
            fl.update({i: (-70, 0, 0) for i in ('07', '08', '09', '10', '11', '12', 'A', 'E')})
            fl.update({'14': (-34, 0, 0), 'C': (28, 0, 0), 'B': (46, 0, 0), '13': (74, 0, 0)})
        else:
            fl = S['flytting']
        im = stegside(int(k), S['tal'], S['tittel'], gruppe(D, fl), S['plass'], px(S['ramme']), S['tekst'], S['retning'], S.get('anker'))
        im.save(os.path.join(ARK, S['fil'])); print('side %s %.0f s' % (k, time.time() - t0), flush=True)

    if '6' in kva:
        im, dr = side('Hovudmål i mm', 6)
        sk = 0.42
        v = Vising(former, FRAMME)
        f = v.teikn(dr, px((14, 26, 175, 180)), skala=sk)
        P = lambda x, y, z: f(v.punkt((x, y, z)))
        maal(dr, P(-L.FOT_D / 2, 0, 0), P(L.FOT_D / 2, 0, 0), 'Ø %.0f' % L.FOT_D, (0, int(9 * MM)))
        maal(dr, P(L.X_RUTE0, 0, 0), P(L.X_RUTE1, 0, 0), '%.0f' % L.RUTE_B, (0, int(18 * MM)))
        maal(dr, P(L.X_BJ0, 0, L.AKSE_H + 30), P(L.X_KN0 + L.KNOTT_L, 0, L.AKSE_H + 30), '%.0f' % (L.X_KN0 + L.KNOTT_L - L.X_BJ0), (0, -int(6 * MM)))
        maal(dr, P(L.X_KN0 + L.KNOTT_L + 14, 0, 0), P(L.X_KN0 + L.KNOTT_L + 14, 0, L.AKSE_H), '%.0f' % L.AKSE_H, (int(4 * MM), 0))
        v2 = Vising(former, SIDE)
        f2 = v2.teikn(dr, px((185, 26, 277, 180)), skala=sk)
        Q = lambda x, y, z: f2(v2.punkt((x, y, z)))
        t = math.radians(L.VINKEL)
        kant = (0, L.YB - math.cos(t) * (L.U_KANT + L.RUTE_D), L.AKSE_H - math.sin(t) * (L.U_KANT + L.RUTE_D))
        maal(dr, Q(0, L.YB, L.AKSE_H), Q(*kant), '%.0f' % L.RUTE_D, (-int(5 * MM), -int(7 * MM)))
        maal(dr, Q(0, kant[1], 0), Q(0, kant[1], kant[2]), '%.0f' % kant[2], (-int(6 * MM), 0))
        maal(dr, Q(0, -L.FOT_D / 2, 0), Q(0, L.FOT_D / 2, 0), 'Ø %.0f' % L.FOT_D, (0, int(9 * MM)))
        dr.text(px((186, 186)), 'Frå høgre · hellinga %.0f° til %.0f°, teikna ved %.0f°' % (*L.VINKEL_OMRAADE, L.VINKEL), font=font(9), fill=(0, 0, 0))
        dr.text(px((16, 186)), 'Framme · 1:%.2f' % (1 / sk), font=font(9), fill=(0, 0, 0))
        im.save(os.path.join(ARK, 'side-6-maal.png')); print('side 6 %.0f s' % (time.time() - t0), flush=True)

    filer = ['side-1-framside.png', 'side-2-delane.png', 'side-3-fot-og-arm.png', 'side-4-bjelke-og-rute.png', 'side-5-leddet.png', 'side-6-maal.png']
    if all(os.path.exists(os.path.join(ARK, f)) for f in filer):
        ims = [Image.open(os.path.join(ARK, f)).convert('RGB') for f in filer]
        ims[0].save(os.path.join(L.UT, 'ruta-pa-fot-montering.pdf'), save_all=True, append_images=ims[1:], resolution=DPI)
        print('pdf ferdig')
