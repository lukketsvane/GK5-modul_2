# -*- coding: utf-8 -*-
"""
segl_teikning.py  ·  målteikning og monteringsrettleiing, strek frå CAD-en med skjulte liner fjerna

    python segl_teikning.py

Skriv ../montering/Segl_maalteikning_A3.pdf og ../montering/Segl_monteringsrettleiing.pdf (+ PNG per side).
Alle liner er projiserte kantar frå dei same lekamane som STEP-filene (HLR i OpenCascade), ortografisk.
"""
import os, sys, math
import numpy as np
import cadquery as cq
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HER = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HER)
import segl_geometri as G
import segl_cad as C

ROT = os.path.dirname(HER)
UT = os.path.join(ROT, 'montering')
FONT = 'Helvetica'
for kandidat in (r'C:\Windows\Fonts\arial.ttf',):
    if os.path.exists(kandidat):
        pdfmetrics.registerFont(TTFont('Arial', kandidat)); FONT = 'Arial'


def eining(v):
    v = np.asarray(v, float); return v / np.linalg.norm(v)


class Vis:
    """Ortografisk vising: N peikar mot den som ser, z blir opp i biletet."""
    def __init__(self, N, opp=(0, 0, 1)):
        self.N = eining(N)
        opp = np.asarray(opp, float)
        if abs(np.dot(eining(opp), self.N)) > 0.999:
            opp = np.array([0, 1.0, 0])
        self.X = eining(np.cross(opp, self.N))
        self.Y = np.cross(self.N, self.X)

    def p(self, P):
        P = np.asarray(P, float)
        return np.array([P @ self.X, P @ self.Y])

    def linjer(self, shapes):
        """Synlege skarpe kantar og omriss, som 2D-polyliner."""
        comp = cq.Compound.makeCompound(list(shapes))
        algo = HLRBRep_Algo()
        algo.Add(comp.wrapped)
        ax = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*self.N), gp_Dir(*self.X))
        algo.Projector(HLRAlgo_Projector(ax))
        algo.Update(); algo.Hide()
        h = HLRBRep_HLRToShape(algo)
        ut = []
        for comp2 in (h.VCompound(), h.OutLineVCompound()):
            if comp2 is None or comp2.IsNull():
                continue
            ex = TopExp_Explorer(comp2, TopAbs_EDGE)
            while ex.More():
                e = TopoDS.Edge_s(ex.Current())
                c = BRepAdaptor_Curve(e)
                u0, u1 = c.FirstParameter(), c.LastParameter()
                n = 2 if c.GetType() == 0 else max(4, int(abs(u1 - u0) * 8) if c.GetType() != 0 else 2)
                n = min(n, 120)
                pts = []
                for i in range(n + 1):
                    q = c.Value(u0 + (u1 - u0) * i / n)
                    pts.append((q.X(), q.Y()))
                ut.append(np.array(pts))
                ex.Next()
        return ut


class Side:
    def __init__(self, c, w, h):
        self.c, self.w, self.h = c, w, h

    def strek(self, linjer, ox, oy, skala, vekt=0.35):
        c = self.c
        c.setLineWidth(vekt); c.setLineCap(1); c.setLineJoin(1)
        for l in linjer:
            pa = c.beginPath(); pa.moveTo(ox + l[0, 0] * skala * mm, oy + l[0, 1] * skala * mm)
            for q in l[1:]:
                pa.lineTo(ox + q[0] * skala * mm, oy + q[1] * skala * mm)
            c.drawPath(pa, stroke=1, fill=0)

    def tekst(self, x, y, t, storleik=9, midt=False, hoeg=False):
        self.c.setFont(FONT, storleik)
        if midt:
            self.c.drawCentredString(x, y, t)
        elif hoeg:
            self.c.drawRightString(x, y, t)
        else:
            self.c.drawString(x, y, t)

    def nummer(self, x, y, n, r=None):
        c = self.c
        r = r or (4.4 * mm if len(str(n)) > 2 else 3.4 * mm)
        c.setLineWidth(0.6); c.setFillGray(1); c.circle(x, y, r, stroke=1, fill=1); c.setFillGray(0)
        c.setFont(FONT, 8 if len(str(n)) > 2 else 9); c.drawCentredString(x, y - 3.0, str(n))

    def pil(self, a, b, vekt=0.8, hovud=2.6 * mm):
        c = self.c
        c.setLineWidth(vekt)
        c.line(a[0], a[1], b[0], b[1])
        d = eining(np.array(b) - np.array(a)); n = np.array([-d[1], d[0]])
        p1 = np.array(b) - hovud * d + 0.45 * hovud * n; p2 = np.array(b) - hovud * d - 0.45 * hovud * n
        pa = c.beginPath(); pa.moveTo(*b); pa.lineTo(*p1); pa.lineTo(*p2); pa.close()
        c.setFillGray(0); c.drawPath(pa, stroke=0, fill=1)

    def maal(self, a, b, avstand, tekst, storleik=8):
        """Mål mellom a og b (sidekoordinatar), forskyvd vinkelrett med avstand."""
        c = self.c
        a = np.array(a, float); b = np.array(b, float)
        d = eining(b - a); n = np.array([-d[1], d[0]])
        a2, b2 = a + avstand * n, b + avstand * n
        c.setLineWidth(0.25)
        c.line(*(a + 1.0 * mm * np.sign(avstand) * n), *(a2 + 1.5 * mm * np.sign(avstand) * n))
        c.line(*(b + 1.0 * mm * np.sign(avstand) * n), *(b2 + 1.5 * mm * np.sign(avstand) * n))
        c.line(*a2, *b2)
        for p, s_ in ((a2, 1), (b2, -1)):
            h = 2.0 * mm
            q1 = p + s_ * h * d + 0.3 * h * n; q2 = p + s_ * h * d - 0.3 * h * n
            pa = c.beginPath(); pa.moveTo(*p); pa.lineTo(*q1); pa.lineTo(*q2); pa.close()
            c.setFillGray(0); c.drawPath(pa, stroke=0, fill=1)
        m = (a2 + b2) / 2 + 1.2 * mm * np.sign(avstand) * n
        c.saveState(); c.translate(*m)
        ang = math.degrees(math.atan2(d[1], d[0]))
        if ang > 90 or ang < -90:
            ang += 180
        c.rotate(ang); c.setFont(FONT, storleik); c.drawCentredString(0, 0 if avstand > 0 else -storleik * 0.8, tekst); c.restoreState()


def aktive(felles, eigne, tol=0.08):
    """Behald dei delane av `eigne` (HLR av dei aktive delane åleine) som òg finst i `felles` (HLR av alt)."""
    from scipy.spatial import cKDTree
    tett = []
    for l in felles:
        for i in range(len(l) - 1):
            a, b = l[i], l[i + 1]
            n = max(2, int(np.linalg.norm(b - a) / 0.05))
            tett.append(a + (b - a) * np.linspace(0, 1, n)[:, None])
    if not tett:
        return []
    tre = cKDTree(np.vstack(tett))
    ut = []
    for l in eigne:
        pts = []
        for i in range(len(l) - 1):
            a, b = l[i], l[i + 1]
            n = max(2, int(np.linalg.norm(b - a) / 0.2))
            pts.append(a + (b - a) * np.linspace(0, 1, n)[:, None])
        pts = np.vstack(pts)
        d, _ = tre.query(pts)
        ok = d < tol
        run = []
        for q, o in zip(pts, ok):
            if o:
                run.append(q)
            elif len(run) > 1:
                ut.append(np.array(run)); run = []
            else:
                run = []
        if len(run) > 1:
            ut.append(np.array(run))
    return ut


def plasser(vis, linjer, boks, skala=None, marg=0.0):
    """Finn skala og origo slik at linjene fyller boksen (x, y, b, h i pt)."""
    allp = np.vstack(linjer)
    lo, hi = allp.min(0), allp.max(0)
    x, y, b, h = boks
    if skala is None:
        skala = min((b - 2 * marg) / ((hi[0] - lo[0]) * mm), (h - 2 * marg) / ((hi[1] - lo[1]) * mm))
    ox = x + (b - (hi[0] - lo[0]) * skala * mm) / 2 - lo[0] * skala * mm
    oy = y + (h - (hi[1] - lo[1]) * skala * mm) / 2 - lo[1] * skala * mm
    til = lambda P: (ox + vis.p(P)[0] * skala * mm, oy + vis.p(P)[1] * skala * mm)
    return skala, ox, oy, til


# ------------------------------------------------------------------ delane

def hent_delar():
    delar, lys = C.bygg()
    return delar


def flytt(sol, d):
    return sol.translate(cq.Vector(*d))


# ------------------------------------------------------------------ målteikninga A3

def maalteikning(delar):
    os.makedirs(UT, exist_ok=True)
    W, H = 420 * mm, 297 * mm
    c = canvas.Canvas(os.path.join(UT, 'Segl_maalteikning_A3.pdf'), pagesize=(W, H))
    s = Side(c, W, H)
    synleg = [delar[k] for k in ('D01', 'D02', 'E02', 'E03', 'E01')]
    skala = 0.5
    # framvising (frå brukaren: ser mot +y)
    vf = Vis((0, -1, 0)); lf = vf.linjer(synleg)
    _, ox, oy, tf = plasser(vf, lf, (25 * mm, 95 * mm, 200 * mm, 180 * mm), skala)
    s.strek(lf, ox, oy, skala, 0.35)
    # ovanfrå (under framvisinga i europeisk projeksjon: ovanfrå teiknast under)
    vt = Vis((0, 0, 1), opp=(0, 1, 0)); lt = vt.linjer(synleg)
    _, ox2, oy2, tt = plasser(vt, lt, (25 * mm, 25 * mm, 200 * mm, 65 * mm), skala)
    # juster x slik at ovanfrå står rett under framvisinga
    dx = tf((0, 0, 0))[0] - tt((0, 0, 0))[0]
    ox2 += dx; tt2 = lambda P: (tt(P)[0] + dx, tt(P)[1])
    s.strek(lt, ox2, oy2, skala, 0.35)
    # frå høgre (sett frå +x mot -x), til venstre for framvisinga i europeisk projeksjon
    vs = Vis((1, 0, 0)); ls = vs.linjer(synleg)
    _, ox3, oy3, ts = plasser(vs, ls, (232 * mm, 95 * mm, 60 * mm, 180 * mm), skala)
    dy = tf((0, 0, 0))[1] - ts((0, 0, 0))[1]
    oy3 += dy; ts2 = lambda P: (ts(P)[0], ts(P)[1] + dy)
    s.strek(ls, ox3, oy3, skala, 0.35)
    # isometri
    vi = Vis((-1.0, -1.3, 0.9)); li = vi.linjer(synleg)
    _, ox4, oy4, ti = plasser(vi, li, (300 * mm, 120 * mm, 110 * mm, 150 * mm), None, 2 * mm)
    s.strek(li, ox4, oy4, _, 0.3)
    # mål i framvisinga
    d01, d02 = G.D01, G.D02
    s.maal(tf((G.KL_X[0], 0, 0)), tf((d01.B2[0], 0, 0)), -10 * mm, f'{d01.B2[0] - G.KL_X[0]:.1f}')
    s.maal(tf((d01.B2[0] + 3, 0, 0)), tf((d01.B2[0] + 3, 0, G.F_H)), -8 * mm, f'{G.F_H:.0f}')
    s.maal(tf((d02.B2[0], 0, 0)), tf((d02.B2[0], 0, G.H_H)), 10 * mm, f'{G.H_H:.0f}')
    s.maal(tf((G.KL_X[0], 0, 0)), tf((G.KL_X[0], 0, G.KL_H)), 6 * mm, f'{G.KL_H:.1f}')
    s.maal(tf((0, 0, 0)), tf((d01.Q2[0], 0, 0)), -4 * mm, f'{d01.Q2[0]:.0f}')
    # mål ovanfrå
    s.maal(tt2((d01.B2[0], -G.FLENS + d01.B2[1], 0)), tt2((d01.B2[0], d02.B2[1], 0)), -8 * mm, '')
    yspenn = d02.B2[1] - (d01.B2[1] - G.FLENS)
    p0 = tt2((d01.B2[0] + 12, d01.B2[1] - G.FLENS, 0)); p1 = tt2((d01.B2[0] + 12, d02.B2[1], 0))
    s.maal(p0, p1, 0.0001, f'{yspenn:.1f}')
    s.maal(tt2((G.KL_X[0], G.KL_Y[0], 0)), tt2((G.KL_X[0], G.KL_Y[1], 0)), 5 * mm, f'{G.KL_Y[1] - G.KL_Y[0]:.0f}')
    s.maal(tt2((G.KL_X[0], G.KL_Y[0], 0)), tt2((G.KL_X[1], G.KL_Y[0], 0)), -5 * mm, f'{G.KL_X[1] - G.KL_X[0]:.0f}')
    s.tekst(tt2((d02.Q2[0], d02.Q2[1], 0))[0] + 4 * mm, tt2((d02.Q2[0], d02.Q2[1], 0))[1] + 6 * mm, f'{G.H_RETN:.0f}° / {G.H_RETN + G.H_KNEKK:.0f}°', 7)
    s.tekst(tt2((d01.Q2[0], 0, 0))[0] + 2 * mm, tt2((d01.Q2[0], 0, 0))[1] - 9 * mm, f'knekk {abs(G.F_KNEKK):.0f}°', 7)
    s.tekst(tt2((G.KL_X[0], 0, 0))[0], tt2((G.KL_X[0], 0, 0))[1] - 18 * mm, f'flens {G.FLENS:.1f}  ·  knapp Ø{G.KNAPP_D:.0f} × {G.KNAPP_H:.1f}', 7)
    # visingsnamn
    s.tekst(25 * mm, 280 * mm, 'framfrå', 8); s.tekst(25 * mm, 88 * mm, 'ovanfrå', 8); s.tekst(235 * mm, 280 * mm, 'sett frå høgre ende', 8)
    # tittelfelt
    c.setLineWidth(0.5); c.rect(300 * mm, 10 * mm, 110 * mm, 100 * mm)
    rader = [('SEGL', 18), ('konsept D · samanstilling', 10), ('', 6),
             (f'målestokk 1:2 på A3 · mm · ISO 2768-m', 8), ('masse om lag 750 g (sjå kontroll/segl_CAD_verifisering.json)', 8),
             ('D01/D02: DC01 1,5 mm, pulverlakk fin struktur matt', 8), ('E01: EN AW-5754 1,5 mm · E02/E03: EN AW-6082', 8),
             ('farge: terrakotta, RAL 8023 (stadfest på prøveplate)', 8), ('', 6),
             ('kjelde: cad/segl_geometri.py, segl_cad.py', 7), ('teikna 24.11.2026 · ark 1 av 1', 7)]
    y = 100 * mm
    for t, st in rader:
        if st == 0:
            continue
        y -= (st + 4) * 1.0
        s.tekst(305 * mm, y, t, st)
    c.showPage(); c.save()


# ------------------------------------------------------------------ monteringsrettleiinga A4 liggjande

def rettleiing(delar):
    W, H = 297 * mm, 210 * mm
    c = canvas.Canvas(os.path.join(UT, 'Segl_monteringsrettleiing.pdf'), pagesize=(W, H))
    s = Side(c, W, H)
    vi = Vis((-1.0, -1.25, 0.95))
    sideno = [0]

    def botn(t=''):
        sideno[0] += 1
        s.tekst(W - 12 * mm, 9 * mm, f'{sideno[0]}', 9, hoeg=True)
        if t:
            s.tekst(12 * mm, 9 * mm, t, 9)

    # 1 framside
    alle = [delar[k] for k in ('D01', 'D02', 'E02', 'E03')]
    l = vi.linjer(alle)
    sk, ox, oy, _ = plasser(vi, l, (40 * mm, 35 * mm, 217 * mm, 150 * mm), None)
    s.strek(l, ox, oy, sk, 0.5)
    s.tekst(14 * mm, 188 * mm, 'SEGL', 26)
    botn()
    c.showPage()

    # 2 delar og verktøy
    s.tekst(14 * mm, 192 * mm, 'Delar', 14)
    rutar = [('D01', 1, 'D01'), ('D02', 1, 'D02'), ('E01', 1, 'E01'), ('E02', 1, 'E02'), ('E03', 1, 'E03')]
    bx = 14 * mm
    for i, (k, n, nr) in enumerate(rutar):
        li = vi.linjer([delar[k]] + ([delar['E01-LED']] if k == 'E01' else []))
        x0 = 14 * mm + (i % 5) * 56 * mm
        sk, ox, oy, _ = plasser(vi, li, (x0, 95 * mm, 52 * mm, 85 * mm), None, 2 * mm)
        s.strek(li, ox, oy, sk, 0.4)
        s.nummer(x0 + 6 * mm, 92 * mm, nr)
        s.tekst(x0 + 12 * mm, 89 * mm, f'{n}×', 10)
    smaa = [('H02', '3×', 'mutter M3 med flens'), ('H04', '2×', 'rifla mutter M3'), ('H05', '2×', 'senkskrue M2,5 × 6')]
    for i, (k, n, t) in enumerate(smaa):
        sol = delar[k]
        # vis éin av kvar
        one = sol.Solids()[0] if hasattr(sol, 'Solids') else sol
        li = Vis((-1.0, -1.25, 0.95)).linjer([one])
        x0 = 14 * mm + i * 56 * mm
        sk, ox, oy, _ = plasser(vi, li, (x0, 40 * mm, 30 * mm, 30 * mm), None, 2 * mm)
        s.strek(li, ox, oy, sk, 0.4)
        s.nummer(x0 + 6 * mm, 34 * mm, k)
        s.tekst(x0 + 12 * mm, 31 * mm, n, 10)
    s.tekst(190 * mm, 62 * mm, 'Verktøy', 12)
    s.tekst(190 * mm, 54 * mm, 'pipenøkkel 5,5 mm', 9)
    s.tekst(190 * mm, 47 * mm, 'skrutrekkjar Torx T8', 9)
    s.tekst(190 * mm, 40 * mm, 'ingen verktøy for lysmodulen', 9)
    botn()
    c.showPage()

    # steg: kvar har (synlege delar med forskyving, aktive delar, piler, nummer)
    n01 = G.D01.nV
    ovan = (-0.10, -0.12, 1.0)     # nesten rett ned i V-en: der arbeidet skjer
    steg = [
        dict(tittel='1', tekst='Før høgseglet inn mot framseglet. Leppa går over dei tre boltane.', vis=ovan,
             delar={'D01': (0, 0, 0), 'H01': (0, 0, 0), 'D02': tuple(45 * n01)}, aktiv=['D02'],
             piler=[((80, 45 * n01[1] + 14, 26), (80, 14, 26))], nummer=[('D02', (150, 110, 120), '1×')]),
        dict(tittel='2', tekst='Skru på dei tre mutrane. Pipenøkkel 5,5 mm.', vis=ovan,
             delar={'D01': (0, 0, 0), 'H01': (0, 0, 0), 'D02': (0, 0, 0), 'H02': tuple(22 * n01)}, aktiv=['H02'],
             piler=[((G.BOLT_X[1], 22 * n01[1] + 12, G.BOLT_Z + 12), (G.BOLT_X[1], 8, G.BOLT_Z + 2))], nummer=[('H02', (G.BOLT_X[1] + 20, 45, 45), '3×')]),
        dict(tittel='3', tekst='Set lysmodulen på dei to boltane i golvet, og stram dei rifla mutrane for hand. Kople saman kontakten.', vis=ovan,
             delar={'D01': (0, 0, 0), 'D02': (0, 0, 0), 'H02': (0, 0, 0), 'H03': (0, 0, 0), 'E01': (0, 0, 60), 'E01-LED': (0, 0, 60), 'H04': (0, 0, 100), 'H07': (0, 0, 0)},
             aktiv=['E01', 'E01-LED', 'H04'],
             piler=[((110, 20, 75), (110, 20, 20)), ((70, 19.5, 125), (70, 19.5, 85))], nummer=[('E01', (120, 40, 95), '1×'), ('H04', (60, 35, 135), '2×')]),
        dict(tittel='4', tekst='Set klampa på tunga ved den låge spissen. Skru inn dei to skruane nedanfrå. Torx T8.', vis=(-1.0, -1.15, -0.45),
             delar={'D01': (0, 0, 0), 'D02': (0, 0, 0), 'E02': (0, 0, 30), 'H05': (0, 0, -30)}, aktiv=['E02', 'H05'],
             piler=[((-18, 10, 70), (-18, 10, 32)), ((-16, -5, -40), (-16, -5, -6))], nummer=[('E02', (-18, 10, 85), '1×'), ('H05', (-16, -5, -50), '2×')]),
        dict(tittel='5', tekst='Trykk knappen ned på akselen. Den flate sida på akselen viser vegen.',
             delar={'D01': (0, 0, 0), 'D02': (0, 0, 0), 'E02': (0, 0, 0), 'E03': (0, 0, 40)}, aktiv=['E03'],
             piler=[((-17.6, 10, 82), (-17.6, 10, 42))], nummer=[('E03', (-17.6, 10, 100), '1×')]),
    ]
    for st in steg:
        v = Vis(st.get('vis', (-1.0, -1.25, 0.95)))
        alle_d = [flytt(delar[k], d) for k, d in st['delar'].items()]
        akt = [flytt(delar[k], st['delar'][k]) for k in st['aktiv']]
        la = v.linjer(alle_d)
        sk, ox, oy, til = plasser(v, la, (20 * mm, 22 * mm, 257 * mm, 160 * mm), None)
        s.strek(la, ox, oy, sk, 0.3)
        s.strek(aktive(la, v.linjer(akt)), ox, oy, sk, 0.8)
        for a, b in st['piler']:
            s.pil(til(a), til(b))
        for nr in st['nummer']:
            k, P = nr[0], nr[1]
            q = til(P); s.nummer(q[0], q[1], k)
            if len(nr) > 2:
                s.tekst(q[0] + 5.5 * mm, q[1] - 1.5 * mm, nr[2], 10)
        s.tekst(14 * mm, 192 * mm, st['tittel'], 26)
        s.tekst(30 * mm, 194 * mm, st['tekst'], 10)
        botn()
        c.showPage()

    # funksjon
    l = vi.linjer(alle)
    sk, ox, oy, til = plasser(vi, l, (20 * mm, 22 * mm, 257 * mm, 160 * mm), None)
    s.strek(l, ox, oy, sk, 0.4)
    kx, ky = G.KNAPP_XY
    k = til((kx, ky, G.KL_H + 12))
    c.setLineWidth(0.8); c.arc(k[0] - 9 * mm, k[1] - 5 * mm, k[0] + 9 * mm, k[1] + 5 * mm, 200, 140)
    s.pil((k[0] + 6 * mm, k[1] + 5.5 * mm), (k[0] + 9.5 * mm, k[1] + 2 * mm))
    c.setLineWidth(0.3); c.line(k[0] - 2 * mm, k[1] + 7 * mm, 40 * mm, 150 * mm)
    s.tekst(22 * mm, 160 * mm, 'vri: sterkare (2700 K) eller svakare og varmare (ned mot 1800 K)', 9)
    s.tekst(22 * mm, 154 * mm, 'trykk: på og av', 9)
    usb = til((G.KNAPP_XY[0], G.KL_Y[1], 8))
    c.line(usb[0], usb[1], 40 * mm, 60 * mm)
    s.tekst(22 * mm, 54 * mm, 'USB-C bak på klampa: 5 V, minst 1 A', 9)
    s.tekst(14 * mm, 192 * mm, 'Bruk', 14)
    botn()
    c.showPage()

    # service: byte lysmodulen
    vis = [delar[k] for k in ('D01', 'D02', 'E02', 'E03')]
    akt = [flytt(delar[k], (0, 0, 90)) for k in ('E01', 'E01-LED')] + [flytt(delar['H04'], (0, 0, 130))]
    la = vi.linjer(vis + akt)
    sk, ox, oy, til = plasser(vi, la, (20 * mm, 22 * mm, 257 * mm, 160 * mm), None)
    s.strek(vi.linjer(vis), ox, oy, sk, 0.3)
    s.strek(vi.linjer(akt), ox, oy, sk, 0.7)
    s.pil(til((110, 20, 40)), til((110, 20, 105)))
    s.tekst(14 * mm, 192 * mm, 'Byte lysmodulen', 14)
    s.tekst(14 * mm, 184 * mm, 'Trekk ut USB-kabelen. Skru av dei to rifla mutrane for hand, løys kontakten, løft modulen ut. Ingen verktøy.', 9)
    botn()
    c.showPage()
    c.save()


def til_png(pdf):
    import fitz
    d = fitz.open(pdf)
    ut = []
    for i, p in enumerate(d):
        f = pdf.replace('.pdf', f'_s{i + 1}.png')
        p.get_pixmap(dpi=110).save(f); ut.append(f)
    return ut


if __name__ == '__main__':
    delar = hent_delar()
    maalteikning(delar)
    rettleiing(delar)
    for f in ('Segl_maalteikning_A3.pdf', 'Segl_monteringsrettleiing.pdf'):
        print(til_png(os.path.join(UT, f)))
