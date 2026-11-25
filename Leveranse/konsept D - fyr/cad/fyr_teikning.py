# -*- coding: utf-8 -*-
"""FYR · produksjonsteikningar for seriegeometrien (FyrParams()).

Køyr frå kva mappe som helst:
    py -3 cad/fyr_teikning.py                 # alle ark + DXF + sjølvkontroll
    py -3 cad/fyr_teikning.py --berre T01,T05 # berre desse arka (PDF-en blir då ikkje sett saman)
    py -3 cad/fyr_teikning.py --ingen-buffer  # rekn HLR/snitt på nytt

Skriv:
    produksjon/teikningar/FYR_teikningar.pdf   alle ark, A3 liggjande
    produksjon/teikningar/FYR_<ark>.png        eitt PNG per ark, 200 dpi
    produksjon/fyr_05_hylse_flatmonster.dxf    flatmønster for laserskjering (0,8 CuZn37)
    produksjon/fyr_08_lok.dxf                  skive for laserskjering (PMMA opal 3), serie
    produksjon/fyr_08_lok_prototype.dxf        same skiva for prototypen (FyrParams.prototype())
    produksjon/fyr_04_mantel_utbretta.dxf      utbretta ytterflate (dokumentasjon)
    <buffer>/sjolvkontroll_*.json              kontroll av mål mot B-rep og av flatmønsteret

Teikneteknikk: ortogonal projeksjon med skjulte liner fjerna (OCP HLRBRep), diskretisert med
GCPnts_QuasiUniformDeflection, skrive som vektor-SVG i mm, cairosvg -> PDF/PNG, pypdf slår saman.
Snitt: lekamen blir kutta med eit halvrom, snittflatene blir skraverte (ISO 128-50) med shapely.
Utbretting: lekamen blir snitta med ein sylinderflate, og kantane blir lesne i (u, v) på flata.
Alle mål blir rekna frå FyrParams eller målte på B-rep; ingen tal er skrivne inn for hand.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import os
import pickle
import sys
import tempfile
import time
import traceback
from pathlib import Path

import numpy as np
import cadquery as cq
import cairosvg
import ezdxf
from PIL import ImageFont
from pypdf import PdfReader, PdfWriter
from shapely.geometry import LineString, MultiLineString, Point, Polygon, box as sbox
from shapely.ops import unary_union
from shapely.validation import make_valid

from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Curve2d, BRepAdaptor_Surface
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.BRepLib import BRepLib
from OCP.BRepTools import BRepTools_WireExplorer
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.GeomAbs import GeomAbs_Line
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.IntCurvesFace import IntCurvesFace_ShapeIntersector
from OCP.TopAbs import TopAbs_EDGE, TopAbs_IN, TopAbs_REVERSED
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Ax2, gp_Dir, gp_Lin, gp_Pnt

HER = Path(__file__).resolve().parent
ROT = HER.parent
sys.path.insert(0, str(HER))
import fyr_geometri as g  # noqa: E402

UT = ROT / "produksjon" / "teikningar"
PROD = ROT / "produksjon"
# mellomlager (HLR, snitt) og sjolvkontroll.json: utanfor repoet, kan setjast med FYR_TEIKNING_BUFFER
BUFFER = Path(os.environ.get("FYR_TEIKNING_BUFFER") or Path(tempfile.gettempdir()) / "fyr_teikning")

DATO = g.DATO
REV = g.REVISJON
DPI = 200
A3 = (420.0, 297.0)
DEG = math.pi / 180.0
ISO_FONT = "Arial"
SYM_FONT = "Segoe UI Symbol"
DIA = "\u2300"
INGEN_BUFFER = "--ingen-buffer" in sys.argv


# ============================================================================ tal og tekst
def tal(x: float, d: int = 2) -> str:
    s = f"{x:.{d}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    if s in ("-0", "−0"):
        s = "0"
    return s.replace(".", ",").replace("-", "\u2212")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


_FONTAR = {}


def _font(fil):
    if fil not in _FONTAR:
        try:
            _FONTAR[fil] = ImageFont.truetype(fil, 100)
        except Exception:  # noqa: BLE001
            _FONTAR[fil] = ImageFont.truetype("DejaVuSans.ttf", 100) if fil != "x" else None
    return _FONTAR[fil]


def fs(h: float) -> float:
    """ISO 3098: h = høgda på store bokstavar. Arial har versalhøgd 0,716 em."""
    return h / 0.716


def tekstbreidd(s: str, h: float, feit: bool = False) -> float:
    f = _font("arialbd.ttf" if feit else "arial.ttf")
    rein = s.replace(DIA, "")
    return (f.getlength(rein) / 100.0 * fs(h) if rein else 0.0) + s.count(DIA) * DIA_B * h


DIA_B = 1.0  # breidd av diameterteiknet i einingar av h (sirkel 0,72 h + luft)


# ============================================================================ B-rep-hjelparar
def form(wp) -> cq.Shape:
    vals = wp.vals() if hasattr(wp, "vals") else [wp]
    return vals[0] if len(vals) == 1 else cq.Compound.makeCompound(vals)


def fingeravtrykk(s: cq.Shape) -> str:
    bb = s.BoundingBox()
    try:
        v = s.Volume()
    except Exception:  # noqa: BLE001
        v = 0.0
    sv = np.zeros(3)
    for vt in s.Vertices():
        sv += (vt.X, vt.Y, vt.Z)
    return "%.5f|%.4f|%d|%d|%.4f,%.4f,%.4f,%.4f,%.4f,%.4f|%.4f,%.4f,%.4f" % (
        v, s.Area(), len(s.Faces()), len(s.Edges()), bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax, *sv)


def buffra(nokkel, fn):
    BUFFER.mkdir(parents=True, exist_ok=True)
    h = hashlib.md5(repr(nokkel).encode()).hexdigest()
    f = BUFFER / f"hlr_{h}.pkl"
    if f.exists() and not INGEN_BUFFER:
        try:
            return pickle.loads(f.read_bytes())
        except Exception:  # noqa: BLE001
            pass
    r = fn()
    f.write_bytes(pickle.dumps(r))
    return r


def ramme(n, x):
    n = np.array(n, float) / np.linalg.norm(n)
    x = np.array(x, float) / np.linalg.norm(x)
    return n, x, np.cross(n, x)


def _hlr_raa(shapes, n, x, defl):
    proj = HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*n), gp_Dir(*x)))
    algo = HLRBRep_Algo()
    for s in shapes:
        algo.Add(s.wrapped)
    algo.Projector(proj)
    algo.Update()
    algo.Hide()
    h = HLRBRep_HLRToShape(algo)
    ut = []
    for kl, comp in (("v", h.VCompound()), ("o", h.OutLineVCompound()), ("s", h.Rg1LineVCompound())):
        if comp is None or comp.IsNull():
            continue
        BRepLib.BuildCurves3d_s(comp)
        exp = TopExp_Explorer(comp, TopAbs_EDGE)
        while exp.More():
            c = BRepAdaptor_Curve(TopoDS.Edge_s(exp.Current()))
            d = GCPnts_QuasiUniformDeflection(c, defl)
            if d.IsDone() and d.NbPoints() > 1:
                ut.append((kl, np.array([(d.Value(i).X(), d.Value(i).Y()) for i in range(1, d.NbPoints() + 1)])))
            exp.Next()
    return ut


def hlr(shapes: list, n, x, defl: float = 0.03):
    n, x, _ = ramme(n, x)
    key = ("hlr", tuple(fingeravtrykk(s) for s in shapes), tuple(np.round(n, 6)), tuple(np.round(x, 6)), defl)
    return buffra(key, lambda: _hlr_raa(shapes, n, x, defl))


def wire_pts3(w: cq.Wire, defl: float = 0.01):
    ex = BRepTools_WireExplorer(w.wrapped)
    pts = []
    while ex.More():
        e = ex.Current()
        c = BRepAdaptor_Curve(e)
        d = GCPnts_QuasiUniformDeflection(c, defl)
        ps = [d.Value(i) for i in range(1, d.NbPoints() + 1)] if d.IsDone() else []
        if e.Orientation() == TopAbs_REVERSED:
            ps = ps[::-1]
        for q in ps:
            t = (q.X(), q.Y(), q.Z())
            if not pts or float(np.linalg.norm(np.subtract(t, pts[-1]))) > 1e-7:
                pts.append(t)
        ex.Next()
    return np.array(pts)


def halvrom(o, n, x):
    pl = cq.Plane(origin=tuple(o), xDir=tuple(x), normal=tuple(n))
    return cq.Workplane(pl).rect(4000, 4000).extrude(2000).val()


SNITT_FORSKYV = (0.0, -0.37, -0.74, 0.37, -1.11, 0.74)
SNITT_LOGG = []


def _hjorne(bb):
    return [np.array((X, Y, Z)) for X in (bb.xmin, bb.xmax) for Y in (bb.ymin, bb.ymax) for Z in (bb.zmin, bb.zmax)]


def _fram(s, o, n):
    """Kor langt framfor planet (mot auget) lekamen når: hjørne og midtpunkt på alle kantar."""
    pts = [np.array((v.X, v.Y, v.Z)) for v in s.Vertices()]
    for e in s.Edges():
        for t in (0.25, 0.5, 0.75):
            q = e.positionAt(t)
            pts.append(np.array((q.x, q.y, q.z)))
    return max(((q - o) @ n for q in pts), default=-1.0)


def _kutt(so, o, n, x):
    """Fjern halvrommet på augesida frå éin lekam. Boolske operasjonar kan feile utan feilmelding
    (resultatet er då uendra); difor blir resultatet kontrollert, og planet blir flytta litt
    (SNITT_FORSKYV, mm langs n) til kuttet held. Gjev (lekamar, origo som vart brukt) eller (None, None)."""
    bb0 = so.BoundingBox()
    if min((q - o) @ n for q in _hjorne(bb0)) > -1e-6:
        return [], o                       # heile lekamen ligg på augesida
    if max((q - o) @ n for q in _hjorne(bb0)) < 1e-6:
        return [so], o                     # heile lekamen ligg bak planet
    for d in SNITT_FORSKYV:
        o2 = o + n * d
        for metode in ("cut", "common"):
            try:
                r = so.cut(halvrom(o2, n, x)) if metode == "cut" else so.intersect(halvrom(o2, -n, x))
            except Exception:  # noqa: BLE001
                continue
            if not r.Solids():
                continue
            if _fram(r, o2, n) < 1e-3:
                if d:
                    SNITT_LOGG.append("snittplanet flytta %s mm for éin lekam" % tal(d))
                return r.Solids(), o2
    SNITT_LOGG.append("snitt feila for éin lekam")
    print("    snitt feila for ein lekam", flush=True)
    return None, None


def _snitt_raa(delar: dict, o, n, x, defl):
    n, x, y = ramme(n, x)
    o = np.array(o, float)
    kutta, polys = {}, {}
    for namn, s in delar.items():
        lek, pl = [], []
        for so in s.Solids():
            r, o2 = _kutt(so, o, n, x)
            if not r:
                continue
            lek += r
            for f in cq.Compound.makeCompound(r).Faces():
                if f.geomType() != "PLANE":
                    continue
                fn = f.normalAt()
                nn = np.array((fn.x, fn.y, fn.z))
                cc = f.Center()
                if abs(abs(nn @ n) - 1.0) > 1e-6 or abs((np.array((cc.x, cc.y, cc.z)) - o2) @ n) > 1e-4:
                    continue
                ringar = [wire_pts3(w) for w in [f.outerWire()] + f.innerWires()]
                ringar = [[(float(q @ x), float(q @ y)) for q in r_] for r_ in ringar if len(r_) > 2]
                if ringar:
                    pl.append(ringar)
        if lek:
            kutta[namn] = cq.Compound.makeCompound(lek)
        polys[namn] = pl
    liner = _hlr_raa(list(kutta.values()), n, x, defl) if kutta else []
    return {"liner": liner, "polys": polys, "logg": list(SNITT_LOGG)}


def snitt(delar: dict, o, n, x, defl: float = 0.03):
    n_, x_, _ = ramme(n, x)
    key = ("snitt-v4", tuple((k, fingeravtrykk(s)) for k, s in delar.items()), tuple(np.round(o, 6)),
           tuple(np.round(n_, 6)), tuple(np.round(x_, 6)), defl)
    return buffra(key, lambda: _snitt_raa(delar, o, n_, x_, defl))


def akse_snitt(phi: float, forskyv: float = 0.37):
    """Snittplan gjennom aksen langs asimut phi, forskyvd litt (unngå skøytar). Auget på -n-sida av
    halvrommet som blir fjerna; teikne-x = radielt utover langs phi."""
    c, s = math.cos(phi * DEG), math.sin(phi * DEG)
    n = (s, -c, 0.0)
    o = (-s * forskyv, c * forskyv, 0.0)
    return o, n, (c, s, 0.0)


def utbrett(shape: cq.Shape, r: float, saum: float, n_kurve: int = 64, r_skala: float | None = None):
    """Snittar lekamen med sylinderflata r (saum på asimut saum) og les kantane i (u, v).
    Gjev liste av ringar [(s, z)], første ring per flate er ytre. s = r * u (u frå saumen, mot klokka)."""
    zb = -500.0
    cyl = cq.Solid.makeCylinder(r, 1000.0, cq.Vector(0, 0, zb), cq.Vector(0, 0, 1)).rotate(
        cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), saum)
    lat = [f for f in cyl.Faces() if f.geomType() == "CYLINDER"][0]
    res = shape.intersect(lat)
    flater = []
    for f in res.Faces():
        ringar = []
        for w in [f.outerWire()] + f.innerWires():
            ex = BRepTools_WireExplorer(w.wrapped, f.wrapped)
            pts = []
            while ex.More():
                e = ex.Current()
                c2 = BRepAdaptor_Curve2d(e, f.wrapped)
                a, b = c2.FirstParameter(), c2.LastParameter()
                n = 1 if c2.GetType() == GeomAbs_Line else n_kurve
                ps = [c2.Value(a + (b - a) * i / n) for i in range(n + 1)]
                if e.Orientation() == TopAbs_REVERSED:
                    ps = ps[::-1]
                for q in ps:
                    t = ((r_skala or r) * q.X(), q.Y() + zb)
                    if not pts or math.hypot(t[0] - pts[-1][0], t[1] - pts[-1][1]) > 1e-6:
                        pts.append(t)
                ex.Next()
            if len(pts) > 1 and math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 1e-6:
                pts.pop()
            ringar.append(pts)
        flater.append(ringar)
    return flater


def region(flater) -> Polygon:
    ps = []
    for ringar in flater:
        try:
            ps.append(make_valid(Polygon(ringar[0], ringar[1:])).buffer(0))
        except Exception:  # noqa: BLE001
            pass
    return unary_union(ps)


def inni(shape: cq.Shape, pt) -> bool:
    c = BRepClass3d_SolidClassifier(shape.wrapped, gp_Pnt(*map(float, pt)), 1e-7)
    return c.State() == TopAbs_IN


def gjennom(shape: cq.Shape, a, b):
    """Materialintervall langs linja a -> b, i mm frå a (eksakte skjeringar med flatene)."""
    a = np.array(a, float)
    b = np.array(b, float)
    L = float(np.linalg.norm(b - a))
    d = (b - a) / L
    si = IntCurvesFace_ShapeIntersector()
    si.Load(shape.wrapped, 1e-7)
    si.Perform(gp_Lin(gp_Pnt(*a), gp_Dir(*d)), 0.0, L)
    ws = sorted([0.0, L] + [si.WParameter(i) for i in range(1, si.NbPnt() + 1)])
    w2 = [ws[0]]
    for w in ws[1:]:
        if w - w2[-1] > 1e-6:
            w2.append(w)
    iv = []
    for w0, w1 in zip(w2[:-1], w2[1:]):
        if inni(shape, a + d * (w0 + w1) / 2):
            if iv and abs(iv[-1][1] - w0) < 1e-6:
                iv[-1] = (iv[-1][0], w1)
            else:
                iv.append((w0, w1))
    return iv


def holrom(shape, a, b):
    """Tomrom langs a -> b mellom materialintervall (gjev (t0, t1) i mm frå a)."""
    iv = gjennom(shape, a, b)
    return [(iv[i][1], iv[i + 1][0]) for i in range(len(iv) - 1)]


def sylinderflater(s: cq.Shape):
    ut = []
    for f in s.Faces():
        if f.geomType() != "CYLINDER":
            continue
        cyl = BRepAdaptor_Surface(f.wrapped).Cylinder()
        ax = cyl.Axis()
        loc, di = ax.Location(), ax.Direction()
        bb = f.BoundingBox()
        ut.append(dict(r=cyl.Radius(), loc=np.array((loc.X(), loc.Y(), loc.Z())), dir=np.array((di.X(), di.Y(), di.Z())),
                       z=(bb.zmin, bb.zmax), bb=bb))
    return ut


# ============================================================================ SVG-ark
STIL = {
    "k": 'stroke="#000" stroke-width="0.5" fill="none" stroke-linecap="round" stroke-linejoin="round"',
    "t": 'stroke="#000" stroke-width="0.25" fill="none" stroke-linecap="round" stroke-linejoin="round"',
    "h": 'stroke="#000" stroke-width="0.25" fill="none"',
    "c": 'stroke="#000" stroke-width="0.25" fill="none" stroke-dasharray="10 1.5 1 1.5"',
    "d": 'stroke="#000" stroke-width="0.25" fill="none" stroke-dasharray="3 1.5"',
    "r": 'stroke="#000" stroke-width="0.7" fill="none" stroke-linecap="square"',
    "x": 'stroke="#000" stroke-width="0.7" fill="none" stroke-linecap="butt"',
    "m": 'stroke="#000" stroke-width="0.35" fill="none" stroke-linecap="square"',
    "f": 'stroke="#000" stroke-width="0.25" fill="none" stroke-dasharray="8 1.2 0.8 1.2 0.8 1.2"',  # nabodel (ISO 128-2, 05.1)
}
LINJEKLASSE = {"v": "k", "o": "k", "s": "t"}


def f2(v: float) -> str:
    return ("%.3f" % v).rstrip("0").rstrip(".")


class Ark:
    def __init__(self, kode, tittel, del_id="", materiale="", overflate="", skala="1:1", doktype="Detaljteikning"):
        self.kode, self.tittel, self.del_id = kode, tittel, del_id
        self.materiale, self.overflate, self.skala, self.doktype = materiale, overflate, skala, doktype
        self.el = []
        self.maallogg = []      # (tekst, verdi, målt på papiret / k)
        self.vis_bbox = {}

    # ---- primitive
    def pl(self, pts, kl="k", lukk=False):
        pts = [(float(a), float(b)) for a, b in pts]
        if len(pts) < 2:
            return
        d = " ".join("%s,%s" % (f2(a), f2(b)) for a, b in pts)
        tag = "polygon" if lukk else "polyline"
        self.el.append('<%s points="%s" %s/>' % (tag, d, STIL[kl]))

    def linje(self, a, b, kl="t"):
        self.el.append('<line x1="%s" y1="%s" x2="%s" y2="%s" %s/>' % (f2(a[0]), f2(a[1]), f2(b[0]), f2(b[1]), STIL[kl]))

    def sirkel(self, c, r, kl="t", fyll=None):
        st = STIL[kl] if fyll is None else 'fill="%s" stroke="#000" stroke-width="0.25"' % fyll
        self.el.append('<circle cx="%s" cy="%s" r="%s" %s/>' % (f2(c[0]), f2(c[1]), f2(r), st))

    def flate(self, ringar, fyll="#000"):
        d = ""
        for r in ringar:
            if len(r) < 3:
                continue
            d += "M" + " L".join("%s,%s" % (f2(a), f2(b)) for a, b in r) + " Z "
        if d:
            self.el.append('<path d="%s" fill="%s" fill-rule="evenodd" stroke="none"/>' % (d, fyll))

    def tekst(self, p, s, h=3.5, anker="middle", rot=0.0, feit=False, kursiv=False):
        if not s:
            return
        tr = ' transform="rotate(%s %s %s)"' % (f2(rot), f2(p[0]), f2(p[1])) if rot else ""
        w = ' font-weight="bold"' if feit else ""
        it = ' font-style="italic"' if kursiv else ""
        if DIA not in s:
            self.el.append('<text x="%s" y="%s" font-family="%s" font-size="%s" text-anchor="%s"%s%s%s fill="#000">%s</text>' % (
                f2(p[0]), f2(p[1]), ISO_FONT, f2(fs(h)), anker, w, it, tr, esc(s)))
            return
        # diameterteiknet (ISO 129) blir teikna som strek: sirkel + skråstrek, så det ikkje er avhengig av fonten
        bitar = s.split(DIA)
        bw = [tekstbreidd(b, h, feit) for b in bitar]
        W = tekstbreidd(s, h, feit)
        x = {"start": 0.0, "middle": -W / 2.0, "end": -W}[anker]
        g_ = ['<g transform="translate(%s %s)%s">' % (f2(p[0]), f2(p[1]), (" rotate(%s)" % f2(rot)) if rot else "")]
        for i, b in enumerate(bitar):
            if b:
                g_.append('<text x="%s" y="0" font-family="%s" font-size="%s" text-anchor="start"%s%s fill="#000">%s</text>' % (
                    f2(x), ISO_FONT, f2(fs(h)), w, it, esc(b)))
            x += bw[i]
            if i < len(bitar) - 1:
                cx, cy, r = x + DIA_B * h / 2.0, -h / 2.0, 0.36 * h
                d = 0.62 * h
                g_.append('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="#000" stroke-width="%s"/>' % (f2(cx), f2(cy), f2(r), f2(h / 10)))
                g_.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#000" stroke-width="%s"/>' % (
                    f2(cx - d * 0.47), f2(cy + d * 0.88), f2(cx + d * 0.47), f2(cy - d * 0.88), f2(h / 10)))
                x += DIA_B * h
        g_.append("</g>")
        self.el.append("".join(g_))

    def pil(self, spiss, retning, L=2.5, B=0.68):
        d = np.array(retning, float)
        d /= np.linalg.norm(d)
        nn = np.array((-d[1], d[0]))
        s = np.array(spiss, float)
        a = s - d * L + nn * B
        b = s - d * L - nn * B
        self.el.append('<polygon points="%s,%s %s,%s %s,%s" fill="#000" stroke="none"/>' % (
            f2(s[0]), f2(s[1]), f2(a[0]), f2(a[1]), f2(b[0]), f2(b[1])))

    def prikk(self, p, r=0.55):
        self.el.append('<circle cx="%s" cy="%s" r="%s" fill="#000" stroke="none"/>' % (f2(p[0]), f2(p[1]), f2(r)))

    # ---- mål (ISO 129-1): lukka fylte pilar, tal over mållinja, lese nedanfrå eller frå høgre
    def maal(self, a, b, orient, at, tekst, verdi=None, k=None, gap=1.0, over=1.5, tekst_ut=None, pos=0.5, avvik=None):
        """avvik = (øvre, nedre) grenseavvik (ISO 129-1 / ISO 14405-1), skrivne mindre etter måltalet."""
        a = np.array(a, float)
        b = np.array(b, float)
        if orient == "h":
            a2, b2 = np.array((a[0], at)), np.array((b[0], at))
            for p, q in ((a, a2), (b, b2)):
                sg = 1 if q[1] > p[1] else -1
                if abs(q[1] - p[1]) > gap:
                    self.linje((p[0], p[1] + sg * gap), (q[0], q[1] + sg * over))
        elif orient == "v":
            a2, b2 = np.array((at, a[1])), np.array((at, b[1]))
            for p, q in ((a, a2), (b, b2)):
                sg = 1 if q[0] > p[0] else -1
                if abs(q[0] - p[0]) > gap:
                    self.linje((p[0] + sg * gap, p[1]), (q[0] + sg * over, q[1]))
        else:  # justert: at = forskyving vinkelrett (papir-mm)
            v = (b - a) / np.linalg.norm(b - a)
            nn = np.array((v[1], -v[0]))
            a2, b2 = a + nn * at, b + nn * at
            if abs(at) > gap:
                for p, q in ((a, a2), (b, b2)):
                    self.linje(p + nn * gap * np.sign(at), q + nn * over * np.sign(at))
        L = float(np.linalg.norm(b2 - a2))
        v = (b2 - a2) / max(L, 1e-9)
        tw0 = tekstbreidd(tekst, 3.5)
        dw = (max(tekstbreidd(s, 2.0) for s in avvik) + 0.8) if avvik else 0.0
        tw = tw0 + dw
        inne = L >= 7.5
        if inne:
            self.linje(a2, b2)
            self.pil(a2, -v)
            self.pil(b2, v)
        else:
            self.linje(a2 - v * 5.0, b2 + v * 5.0)
            self.pil(a2, v)
            self.pil(b2, -v)
        mid = a2 + (b2 - a2) * pos
        vink = math.degrees(math.atan2(v[1], v[0]))
        if vink > 90.01 or vink <= -90.01:
            vink += 180.0
            vink = (vink + 180) % 360 - 180
        rv = np.array((math.cos(vink * DEG), math.sin(vink * DEG)))
        opp = np.array((rv[1], -rv[0]))
        if tekst_ut is None:
            tekst_ut = (tw + 1.5 > L - 5.0)
        if tekst_ut:
            # teksten utanfor, etter pila nærast høgre/nede
            ende = b2 if (b2 - a2) @ rv >= 0 else a2
            pos = ende + rv * (6.0 + tw / 2.0) + opp * 0.9
            self.linje(ende, ende + rv * (7.0 + tw))
        else:
            pos = mid + opp * 1.1
        if avvik:
            pos = pos - rv * dw / 2.0
            q = pos + rv * (tw0 / 2.0 + 0.8)
            self.tekst(q + opp * 2.3, avvik[0], 2.0, anker="start", rot=vink)
            self.tekst(q - opp * 0.3, avvik[1], 2.0, anker="start", rot=vink)
        self.tekst(pos, tekst, 3.5, rot=vink)
        if verdi is not None and k:
            self.maallogg.append((tekst, float(verdi), L / k if orient == "a" else
                              (abs(b[0] - a[0]) if orient == "h" else abs(b[1] - a[1])) / k))

    def ballong(self, anker, pos, nr, r=4.2):
        a = np.array(anker, float)
        p = np.array(pos, float)
        d = a - p
        L = np.linalg.norm(d)
        if L > r:
            self.linje(p + d / L * r, a)
        self.prikk(a, 0.6)
        self.sirkel(p, r, "t", fyll="#fff")
        self.tekst((p[0], p[1] + 1.25), nr, 3.5 if len(nr) <= 2 else 2.5, feit=True)

    def merknad(self, anker, pos, linjer, h=2.5, pil=True, side=None):
        a = np.array(anker, float)
        p = np.array(pos, float)
        if side is None:
            side = 1 if p[0] >= a[0] else -1
        bw = max(tekstbreidd(s, h) for s in linjer)
        self.linje(a, p)
        self.linje(p, p + (side * (bw + 1.0), 0))
        if pil:
            self.pil(a, a - p)
        else:
            self.prikk(a)
        x = p[0] + (0.5 if side > 0 else -0.5)
        for i, s in enumerate(linjer):
            self.tekst((x, p[1] - 0.9 + i * h * 1.6), s, h, anker="start" if side > 0 else "end")

    def tekstblokk(self, p, linjer, h=2.5, sprang=1.55, feit_forste=False):
        for i, s in enumerate(linjer):
            inn = 3.5 if s.startswith("    ") else 0.0
            self.tekst((p[0] + inn, p[1] + i * h * sprang), s.strip(), h, anker="start", feit=(feit_forste and i == 0))

    def tabell(self, x, y, kol, rader, h=2.5, rh=5.0, hovud=True):
        W = sum(kol)
        n = len(rader)
        self.linje((x, y), (x + W, y), "m")
        for i in range(n + 1):
            yy = y + i * rh
            self.linje((x, yy), (x + W, yy), "m" if (i == 0 or i == n or (hovud and i == 1)) else "t")
        xx = x
        for i in range(len(kol) + 1):
            self.linje((xx, y), (xx, y + n * rh), "m" if i in (0, len(kol)) else "t")
            if i < len(kol):
                xx += kol[i]
        for j, rad in enumerate(rader):
            xx = x
            for i, c in enumerate(rad):
                s = str(c)
                maxw = kol[i] - 1.6
                hh = h
                while tekstbreidd(s, hh, hovud and j == 0) > maxw and hh > 1.5:
                    hh -= 0.1
                self.tekst((xx + 0.8, y + j * rh + rh / 2 + hh / 2), s, hh, anker="start", feit=(hovud and j == 0))
                xx += kol[i]
        return y + n * rh

    def skravur(self, polys, vinkel=45.0, avstand=1.6, tynn=0.55):
        """polys: shapely-geometri i papir-mm. Tynne snitt (under 2 x tynn) blir fylte svarte (ISO 128-50)."""
        geoms = list(polys.geoms) if hasattr(polys, "geoms") else [polys]
        for pg in geoms:
            if pg.is_empty or pg.geom_type != "Polygon" or pg.area < 1e-4:
                continue
            if pg.buffer(-tynn).is_empty:
                self.flate([list(pg.exterior.coords)] + [list(i.coords) for i in pg.interiors])
                continue
            c = pg.centroid
            R = math.hypot(pg.bounds[2] - pg.bounds[0], pg.bounds[3] - pg.bounds[1]) / 2 + 1
            d = np.array((math.cos(vinkel * DEG), -math.sin(vinkel * DEG)))
            nn = np.array((-d[1], d[0]))
            k0 = -math.floor(R / avstand)
            liner = []
            for i in range(k0, -k0 + 1):
                o = np.array((c.x, c.y)) + nn * (i * avstand)
                liner.append(LineString([o - d * R, o + d * R]))
            sk = pg.intersection(MultiLineString(liner))
            for ln in (sk.geoms if hasattr(sk, "geoms") else [sk]):
                if ln.geom_type == "LineString" and ln.length > 0.05:
                    self.pl(list(ln.coords), "h")

    # ---- ramme og tittelfelt (ISO 5457, ISO 7200)
    def ramme(self, nr, tot):
        W, H = A3
        x0, y0, x1, y1 = 20.0, 10.0, W - 10.0, H - 10.0
        self.el.append('<rect x="%s" y="%s" width="%s" height="%s" %s/>' % (x0, y0, x1 - x0, y1 - y0, STIL["r"]))
        # midtmerke
        for (a, b) in (((W / 2 + 5, 0), (W / 2 + 5, y0 + 5)), ((W / 2 + 5, H), (W / 2 + 5, y1 - 5)),
                       ((5, H / 2), (x0 + 5, H / 2)), ((W, H / 2), (x1 - 5, H / 2))):
            self.linje(a, b, "r")
        # rutenett for referanse: 8 felt vassrett, 6 loddrett
        for i in range(9):
            xx = x0 + (x1 - x0) * i / 8
            self.linje((xx, y0), (xx, y0 - 5), "t")
            self.linje((xx, y1), (xx, y1 + 5), "t")
            if i < 8:
                xm = x0 + (x1 - x0) * (i + 0.5) / 8
                self.tekst((xm, y0 - 1.6), str(i + 1), 2.5)
                self.tekst((xm, y1 + 3.9), str(i + 1), 2.5)
        for j in range(7):
            yy = y0 + (y1 - y0) * j / 6
            self.linje((x0, yy), (x0 - 5, yy), "t")
            self.linje((x1, yy), (x1 + 5, yy), "t")
            if j < 6:
                ym = y0 + (y1 - y0) * (j + 0.5) / 6 + 1.25
                self.tekst((x0 - 2.5, ym), "ABCDEF"[j], 2.5)
                self.tekst((x1 + 2.5, ym), "ABCDEF"[j], 2.5)
        # tittelfelt 180 x 50 nede til høgre
        tx0, ty0 = x1 - 180.0, y1 - 50.0
        self.el.append('<rect x="%s" y="%s" width="180" height="50" fill="#fff" stroke="none"/>' % (f2(tx0), f2(ty0)))
        self.el.append('<rect x="%s" y="%s" width="180" height="50" %s/>' % (f2(tx0), f2(ty0), STIL["r"]))

        def celle(x, y, w, h, etikett, verdi, vh=2.5, feit=False):
            self.el.append('<rect x="%s" y="%s" width="%s" height="%s" %s/>' % (f2(x), f2(y), f2(w), f2(h), STIL["m"]))
            self.tekst((x + 0.8, y + 2.3), etikett, 1.8, anker="start")
            vv = vh
            while verdi and tekstbreidd(verdi, vv, feit) > w - 1.6 and vv > 1.4:
                vv -= 0.1
            self.tekst((x + 0.8, y + h - 1.2), verdi, vv, anker="start", feit=feit)

        y = ty0
        celle(tx0, y, 45, 8, "Teikna", "(namn)")
        celle(tx0 + 45, y, 45, 8, "Kontrollert", "(namn)")
        celle(tx0 + 90, y, 45, 8, "Godkjent", "(namn)")
        celle(tx0 + 135, y, 45, 8, "Dokumenttype", self.doktype)
        y += 8
        celle(tx0, y, 90, 8, "Materiale", self.materiale)
        celle(tx0 + 90, y, 90, 8, "Overflate", self.overflate)
        y += 8
        celle(tx0, y, 112, 18, "Tittel", "", 3.5)
        self.tekst((tx0 + 2, y + 9.5), "FYR", 5.0, anker="start", feit=True)
        tt = self.tittel
        hh = 3.5
        while tekstbreidd(tt, hh) > 112 - 18 and hh > 2.0:
            hh -= 0.1
        self.tekst((tx0 + 17, y + 9.5), tt, hh, anker="start")
        self.tekst((tx0 + 2, y + 15.8), "Lampe for bord, konsept D · seriegeometri", 2.0, anker="start")
        celle(tx0 + 112, y, 30, 18, "Projeksjon", "")
        self._fyrste_vinkel(tx0 + 127, y + 10.5)
        self.tekst((tx0 + 127, y + 16.8), "ISO 5456-2 (E)", 1.8)
        celle(tx0 + 142, y, 38, 9, "Skala", self.skala, 3.5)
        celle(tx0 + 142, y + 9, 38, 9, "Mål", "mm", 3.5)
        y += 18
        celle(tx0, y, 30, 8, "Del-ID", self.del_id, 3.5, feit=True)
        celle(tx0 + 30, y, 60, 8, "Generell toleranse", "ISO 2768-m", 2.5)
        celle(tx0 + 90, y, 20, 8, "Revisjon", REV, 2.5)
        celle(tx0 + 110, y, 35, 8, "Dato", DATO, 2.5)
        celle(tx0 + 145, y, 35, 8, "Status", "Til vurdering", 2.5)
        y += 8
        celle(tx0, y, 90, 8, "Teikningsnr.", "FYR-" + self.kode, 3.5, feit=True)
        celle(tx0 + 90, y, 30, 8, "Ark", "%d / %d" % (nr, tot), 2.5)
        celle(tx0 + 120, y, 25, 8, "Språk", "nn", 2.5)
        celle(tx0 + 145, y, 35, 8, "Format", "A3 (ISO 5457)", 2.5)

    def _fyrste_vinkel(self, cx, cy):
        # første vinkel: avkorta kjegle til venstre, sirklane til høgre
        x0 = cx - 11
        self.pl([(x0, cy - 2.2), (x0 + 9, cy - 3.6), (x0 + 9, cy + 3.6), (x0, cy + 2.2)], "m", lukk=True)
        self.sirkel((cx + 6, cy), 3.6, "m")
        self.sirkel((cx + 6, cy), 2.2, "m")
        self.linje((x0 - 1.5, cy), (x0 + 10.5, cy), "c")
        self.linje((cx + 1, cy), (cx + 11, cy), "c")
        self.linje((cx + 6, cy - 5), (cx + 6, cy + 5), "c")

    def svg(self, nr, tot):
        self.el_ramme = []
        el0 = self.el
        self.el = []
        self.ramme(nr, tot)
        ramme = self.el
        self.el = el0
        W, H = A3
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="%dmm" height="%dmm" viewBox="0 0 %d %d">\n'
                '<rect x="0" y="0" width="%d" height="%d" fill="#fff"/>\n%s\n%s\n</svg>\n') % (
            W, H, W, H, W, H, "\n".join(self.el), "\n".join(ramme))


class Vis:
    """Éi vising på eit ark. Projeksjonskoordinatar (X, Y) -> papir (mm, y nedover).
    n = retninga mot auget, x = teikne-x. k = papir-mm per modell-mm."""

    def __init__(self, ark: Ark, n, x, k, anker, papir, klipp=None, namn=""):
        self.ark, self.k, self.namn = ark, k, namn
        if n is not None:
            self.n, self.x, self.y = ramme(n, x)
        else:
            self.n = self.x = self.y = None
        self.X0, self.Y0 = self.pr(anker)
        self.px, self.py = papir
        self.klipp = klipp
        self.bbox = [1e9, 1e9, -1e9, -1e9]

    def pr(self, p):
        if len(p) == 2 or self.x is None:
            return float(p[0]), float(p[1])
        q = np.array(p, float)
        return float(q @ self.x), float(q @ self.y)

    def Q(self, X, Y):
        return (self.px + (X - self.X0) * self.k, self.py - (Y - self.Y0) * self.k)

    def P(self, p):
        return self.Q(*self.pr(p))

    def _utvid(self, pts):
        a = np.array(pts)
        self.bbox = [min(self.bbox[0], a[:, 0].min()), min(self.bbox[1], a[:, 1].min()),
                     max(self.bbox[2], a[:, 0].max()), max(self.bbox[3], a[:, 1].max())]

    def _bitar(self, arr):
        if self.klipp is None:
            return [arr]
        ln = LineString(arr)
        r = ln.intersection(self.klipp)
        ut = []
        for gg in (r.geoms if hasattr(r, "geoms") else [r]):
            if gg.geom_type == "LineString" and len(gg.coords) > 1:
                ut.append(np.array(gg.coords))
        return ut

    def liner(self, liner, glatt=True):
        for kl, arr in liner:
            if kl == "s" and not glatt:
                continue
            for b in self._bitar(arr):
                pp = [self.Q(*q) for q in b]
                self._utvid(pp)
                self.ark.pl(pp, LINJEKLASSE[kl])

    def ringar_til_poly(self, ringar):
        try:
            return make_valid(Polygon(ringar[0], ringar[1:])).buffer(0)
        except Exception:  # noqa: BLE001
            return Polygon()

    def skravur(self, polys_per_del: dict, stil: dict | None = None, avstand=None, tynn=0.55):
        stil = stil or {}
        for i, (namn, pl) in enumerate(polys_per_del.items()):
            if not pl:
                continue
            gm = unary_union([self.ringar_til_poly(r) for r in pl])
            if self.klipp is not None:
                gm = gm.intersection(self.klipp)
            if gm.is_empty:
                continue
            from shapely.affinity import affine_transform
            gp = affine_transform(gm, [self.k, 0, 0, -self.k, self.px - self.X0 * self.k, self.py + self.Y0 * self.k])
            vink, av = stil.get(namn, (45.0 if i % 2 == 0 else 135.0, None))
            self.ark.skravur(gp, vink, av or avstand or max(1.0, min(2.2, 1.6)), tynn=tynn)

    def senterlinje(self, a, b, ut=3.0):
        pa, pb = np.array(self.P(a)), np.array(self.P(b))
        v = (pb - pa) / np.linalg.norm(pb - pa)
        self.ark.linje(pa - v * ut, pb + v * ut, "c")

    def senterkryss(self, c, r=3.0):
        p = np.array(self.P(c))
        self.ark.linje(p - (r, 0), p + (r, 0), "c")
        self.ark.linje(p - (0, r), p + (0, r), "c")

    def merknad(self, *a, **kw):
        return self.ark.merknad(*a, **kw)

    def sirkel_c(self, c, R):
        self.ark.sirkel(self.P(c), R * self.k, "c")

    def maal(self, a, b, orient, at, tekst, verdi, **kw):
        pa, pb = self.P(a), self.P(b)
        if self.n is not None and orient in ("h", "a") and "pos" not in kw:
            c = self.P((0, 0, 0))
            mx = (pa[0] + pb[0]) / 2
            if abs(mx - c[0]) < 1.5:
                kw["pos"] = 0.3
        self.ark.maal(pa, pb, orient, at, tekst, verdi, self.k, **kw)

    def vinkelmaal(self, c3, r, a0, a1, z, tekst, verdi=None, r_ref=None, tekst_r=None):
        """Vinkelmål i ei toppvising: boge på radius r (modell) mellom asimut a0 og a1."""
        aa = np.linspace(a0, a1, 60)
        pts = [self.P((c3[0] + r * math.cos(t * DEG), c3[1] + r * math.sin(t * DEG), z)) for t in aa]
        self.ark.pl(pts, "t")
        for t in (a0, a1):
            if r_ref is not None:
                p0 = self.P((c3[0] + (r_ref + 1.0 / self.k) * math.cos(t * DEG), c3[1] + (r_ref + 1.0 / self.k) * math.sin(t * DEG), z))
                p1 = self.P((c3[0] + (r + 1.5 / self.k) * math.cos(t * DEG), c3[1] + (r + 1.5 / self.k) * math.sin(t * DEG), z))
                self.ark.linje(p0, p1)
        d0 = np.array(pts[0]) - np.array(pts[3])
        d1 = np.array(pts[-1]) - np.array(pts[-4])
        self.ark.pil(pts[0], d0)
        self.ark.pil(pts[-1], d1)
        tm = (a0 + a1) / 2
        rt = tekst_r if tekst_r is not None else r + 3.2 / self.k
        pt = self.P((c3[0] + rt * math.cos(tm * DEG), c3[1] + rt * math.sin(tm * DEG), z))
        self.ark.tekst((pt[0], pt[1] + 1.2), tekst, 3.5)
        if verdi is not None:
            self.ark.maallogg.append((tekst, float(verdi), abs(a1 - a0)))

    def tittel(self, tekst, under=None, dy=8.0):
        x = (self.bbox[0] + self.bbox[2]) / 2 if self.bbox[0] < 1e8 else self.px
        y = (self.bbox[3] if under is None else under) + dy
        self.ark.tekst((x, y), tekst, 3.5, feit=True)
        self.ark.vis_bbox[self.namn or tekst] = [round(v, 1) for v in self.bbox]


def detaljsirkel(vis: Vis, c, R, bokstav, vinkel=45.0, avstand=3.5):
    p = vis.P(c)
    vis.ark.sirkel(p, R * vis.k, "t")
    q = (p[0] + (R * vis.k + avstand) * math.cos(vinkel * DEG), p[1] - (R * vis.k + avstand) * math.sin(vinkel * DEG))
    vis.ark.tekst((q[0], q[1] + 2.5), bokstav, 5.0, feit=True)


def snittlinje(vis: Vis, a3, b3, bokstav, sjaa_mot):
    """Snittlinje (ISO 128-44): tynn strekpunkt, tjukke endar, pilar i sjåretninga (papirvektor)."""
    a, b = np.array(vis.P(a3)), np.array(vis.P(b3))
    v = (b - a) / np.linalg.norm(b - a)
    vis.ark.linje(a, b, "c")
    s = np.array(sjaa_mot, float)
    s /= np.linalg.norm(s)
    for p, sg in ((a, -1), (b, 1)):
        e = p + v * sg * 5.0
        vis.ark.linje(p, e, "x")
        m = p + v * sg * 3.5
        vis.ark.linje(m, m + s * 6.0, "t")
        vis.ark.pil(m + s * 6.0, s, 3.0, 0.9)
        t = m + s * 6.0 + v * sg * 3.0
        vis.ark.tekst((t[0], t[1] + 2.5), bokstav, 5.0, feit=True)


# ============================================================================ delar og data
from contextlib import contextmanager  # noqa: E402
import re  # noqa: E402
from shapely.affinity import affine_transform  # noqa: E402

HOPPA = []


@contextmanager
def valfri(namn):
    """Valfri blokk: geometrien er i endring, så eit mål som manglar ein parameter blir hoppa over og logga."""
    try:
        yield
    except Exception as e:  # noqa: BLE001
        HOPPA.append(f"{namn}: {type(e).__name__}: {e}")
        print(f"    hoppa over «{namn}»: {type(e).__name__}: {e}", flush=True)


def TUNGE(p):
    v = getattr(p, "tunge_vinkel", None)
    return v if v is not None else list(getattr(p, "tunge_vinklar"))[0]


def pv(p, namn, std=None):
    return getattr(p, namn, std)


def delar_tekst(namn: str) -> str:
    return g.DELAR[namn][1].split(" / ")[0].strip() if namn in g.DELAR else ""


NAMN = {
    "01_fot": "Fot", "03_chassis": "Chassis", "04_mantel": "Mantel", "05_hylse": "Hylse",
    "05b_hylsefot": "Hylsefot (fotring)", "05c_stoppskruar": "Stoppskrue", "06_lysstav": "Lysstav",
    "06b_led_side": "LED-stripe, side", "06c_led_topp": "LED, topp", "06d_kontakt": "Mastfot med TRS-plugg",
    "07_lysrist": "Lysrist", "08_lok": "Lok", "10_glidering": "Glidering", "11_oring": "O-ring",
    "12_brytarar": "Mikrobrytar", "13_jack": "TRS-kontakt 3,5 mm", "14_kretskort": "Kretskort",
}
# materiale, overflate, standard/teikning for delar der oppdraget fastset dei; resten kjem frå DELAR
SERIE = {
    "01_fot": ("EN AW-6082 T6", "Pulverlakk RAL 3005, fin struktur, matt", "FYR-T01"),
    "03_chassis": ("PA12, MJF/SLS", "Som bygd", "FYR-T03"),
    "04_mantel": ("EN AW-6060 T66, røyr 90 x 2", "Pulverlakk RAL 3005 inn og ut", "EN 755-8, FYR-T04"),
    "05_hylse": ("CuZn37, plate 0,8", "Børsta rundt + klarlakk", "FYR-T05"),
    "05b_hylsefot": ("POM-C", "Sprøytestøypt", "FYR-T05b"),
    "08_lok": ("PMMA opal 3", "Laserskoren", "FYR-T08"),
    "10_glidering": ("POM-C", "Delt ring", "FYR-T08"),
    "11_oring": ("Silikon 60 ShA", "-", "ISO 3601, 85 x 3"),
    "07_lysrist": (None, "-", "FYR-T07"),
    "06_lysstav": ("EN AW-6060, flat %s x %s, kappa %s" % (tal(g.FyrParams().stav_b), tal(g.FyrParams().stav_t),
                                                          tal(g.FyrParams().stav_z1 - g.FyrParams().stav_z0)),
                   "Baksida mattsvart", "FYR-T06 (H7)"),
    "06d_kontakt": ("Mastfot POM-C + TRS-plugg (E8)", "-", "FYR-T06 (E8)"),
}
INNKJOP = "kontroll/fyr_innkjopsliste.csv"
# Seriestift i foten (S01 i innkjøpslista). Stolpestiftet: lengd frå S01. Knaststiftet: lengste ISO 8734-lengd som
# ikkje stikk ut i lomma (sjå ark_T01); knastgeometrien (Ø = knasthøgda) kjem frå FyrParams.
STIFT_STOLPE_L = 12.0
ISO8734_L = (4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 24.0)


def knaststift(p):
    """Seriestift for bajonettknastane: (Ø, lengd, senter z, spiss r, innsenking frå lommeveggen)."""
    d = p.baj_knast_h
    zc = p.z_mantel_0 + p.baj_knast_z + p.baj_knast_h / 2.0
    r_a = p.r_mi - p.spor_klaring_inn
    spiss = r_a + p.baj_knast_ut + p.spor_klaring_inn
    L = max(l_ for l_ in ISO8734_L if l_ <= spiss - p.fot_lomme_r)
    return d, L, zc, spiss, spiss - L - p.fot_lomme_r


# Funksjonspassingar (ISO 14405-1, grenseavvik). Hol får + avvik, akslar − avvik, så minste klaring er klaringa
# i CAD (lager_klaring, hylsefoten r_hi − 0,05, mantel_styr_klaring, glide_klaring). Glideringen er delt og
# blir trykt saman i boret: fri ytterdiameter med overmål, vegg med smal toleranse.
MI = "−"
TOL = {
    "tapp": ("0", MI + "0,1"),          # 03 tapp Ø72 (aksel i boret på 05b)
    "bor": ("+0,1", "0"),               # 05b bor Ø72,4
    "fotring": ("0", MI + "0,1"),       # 05b ytterflate Ø82 (aksel i hylsa)
    "hylse": ("+0,1", "0"),             # 05 innerdiameter Ø82,1 og dermed ytterdiameter Ø83,7
    "toppdekk": ("0", MI + "0,2"),      # 03 toppdekk Ø85,7 (aksel i mantelen)
    "mantel": ("+0,1", MI + "0,1"),     # 04 innerdiameter Ø86 (øvst og ved toppdekket)
    "glide_ut": ("+0,3", "+0,15"),      # 10 fri ytterdiameter Ø86 (delt ring, presspassing)
    "glide_t": ("0", MI + "0,05"),      # 10 vegg 1
    "rist": ("+0,2", "0"),              # 07 bor i skjørtet Ø78,9
    "lok": ("0", MI + "0,2"),           # 08 lok Ø78,6
}


def tol(k):
    return "%s/%s" % TOL[k]


def tv(k):
    """Grenseavvika som tal (øvre, nedre)."""
    return tuple(float(s.replace(MI, "-").replace(",", ".")) for s in TOL[k])


def glide_montert_id(p):
    """Innerdiameter på den delte glideringen når han sit i mantelboret: boret minus to veggar."""
    lo = 2 * p.r_mi + tv("mantel")[1] - 2 * (p.glide_t + tv("glide_t")[0])
    hi = 2 * p.r_mi + tv("mantel")[0] - 2 * (p.glide_t + tv("glide_t")[1])
    return lo, hi


EKSTRA = [  # festemiddel og kjøpedelar som ikkje er modellerte; posisjonane er dei same som i kontroll/fyr_innkjopsliste.csv
    ("H1", "Gjengeinnsats M3 x 5,7", "3", "Messing", "Varmepressa", "Ruthex RX-M3x5.7"),
    ("H2", "Knappskrue M3 x 16", "3", "Stål A2 svart", "-", "ISO 7380"),
    ("H4", "Skrue M2 x 10 + mutter, brytar", "{n_sw2}", "Stål", "-", "ISO 7045, ISO 4032"),
    ("H11", "2K-epoksy, lysmodul", "1", "Epoksy, 5 min open tid", "-", "innkjøpsliste H11"),
    ("E9", "USB-kabel, fast", "1", "-", "-", "innkjøpsliste E9"),
    ("E12", "Leiarar AWG 28, lysmodul", "4", "Cu, silikon/PTFE", "3 fargar: raud, blå, 2 x svart", "innkjøpsliste E12"),
    ("S01a", "Sylinderstift " + DIA + "{ks_d} x {ks_l}, knast", "3", "Stål", "-", "ISO 8734 m6, FYR-T01"),
    ("S01b", "Sylinderstift " + DIA + "3 x {ss_l}, stolpe", "3", "Stål", "-", "ISO 8734 m6, FYR-T01"),
]


def stykk(namn: str):
    t = delar_tekst(namn)
    nn = NAMN.get(namn, namn.split("_", 1)[1].replace("_", " ").capitalize())
    if namn in SERIE:
        mat, ov, st = SERIE[namn]
        return nn, (mat or t), ov, st
    m = re.search(r"ISO\s*\d+\s*M\d+\s*x\s*\d+", t)
    if m:
        return nn, re.sub(r"^\d+\s*x\s*", "", t.replace(m.group(0), "")).strip(" ,") or "Stål", "-", m.group(0).replace("x", " x ")
    return nn, t, "-", "sjå innkjøpsliste"


def kort_id(namn: str) -> str:
    return namn.split("_")[0]


def bygg_data(p: g.FyrParams) -> dict:
    t0 = time.time()
    D = {}
    for namn, (fn, _m, _c, _r) in g.DELAR.items():
        t = time.time()
        D[namn] = form(fn(p))
        print(f"  bygd {namn:18s} {time.time() - t:5.1f} s", flush=True)
    print(f"  alle delar bygde på {time.time() - t0:.1f} s", flush=True)
    return D


def flat_teikn(A: Ark, V: Vis, fl):
    for ringar in fl:
        for r in ringar:
            pp = [V.Q(*q) for q in r] + [V.Q(*r[0])]
            V._utvid(pp)
            A.pl(pp, "k")


def flat_liner(fl):
    return [("v", np.array(list(r) + [r[0]])) for ringar in fl for r in ringar]


def detalj(A: Ark, foreldre: Vis, data, c3, R, bokstav, skala, pos, stil, tynn=0.5, lab_vinkel=30.0, tittel=None, glatt=True,
           lab_avstand=3.5):
    """Detaljvising (ISO 128): sirkel med bokstav på foreldrevisinga, forstørra utsnitt klipt til sirkelen."""
    detaljsirkel(foreldre, c3, R, bokstav, lab_vinkel, lab_avstand)
    X, Y = foreldre.pr(c3)
    Dv = Vis(A, (foreldre.n if foreldre.n is not None else None), (foreldre.x if foreldre.x is not None else None),
             skala, c3, pos, klipp=Point(X, Y).buffer(R, 128), namn=bokstav)
    if data.get("polys"):
        Dv.skravur(data["polys"], stil, tynn=tynn)
    Dv.liner(data["liner"], glatt=glatt)
    A.sirkel(pos, R * skala, "t")
    A.tekst((pos[0], pos[1] + R * skala + 9), tittel or "%s (%s)" % (bokstav, skala_tekst(skala)), 3.5, feit=True)
    return Dv


def skala_tekst(k):
    return ("%d:1" % round(k)) if k >= 1 else ("1:%d" % round(1 / k))


def vinkel_papir(A: Ark, apex, d0, d1, r, tekst):
    """Vinkelmål i papirplanet: boge med radius r mellom retningane d0 og d1 (einingsvektorar, papir)."""
    a0 = math.atan2(d0[1], d0[0])
    a1 = math.atan2(d1[1], d1[0])
    da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    ts = np.linspace(0, 1, 40)
    pts = [(apex[0] + r * math.cos(a0 + da * t), apex[1] + r * math.sin(a0 + da * t)) for t in ts]
    A.pl(pts, "t")
    for (q0, q1) in ((pts[0], pts[3]), (pts[-1], pts[-4])):
        A.pil(q0, np.subtract(q0, q1))
    for d in (d0, d1):
        A.linje(apex, (apex[0] + d[0] * (r + 2), apex[1] + d[1] * (r + 2)), "t")
    am = a0 + da / 2
    A.tekst((apex[0] + (r + 4.5) * math.cos(am), apex[1] + (r + 4.5) * math.sin(am) + 1.2), tekst, 3.5)


# ============================================================================ T00 samanstilling
SKRAVUR_T00 = {"01_fot": (45, 1.4), "03_chassis": (135, 1.4), "04_mantel": (45, 1.2), "05_hylse": (135, 1.2),
               "05b_hylsefot": (45, 1.0), "05c_stoppskruar": (135, 0.8), "06_lysstav": (45, 1.0),
               "06b_led_side": (135, 0.8), "06c_led_topp": (135, 0.8), "06d_kontakt": (45, 0.8),
               "07_lysrist": (135, 1.6), "08_lok": (45, 1.0), "10_glidering": (135, 1.0), "11_oring": (45, 0.8),
               "12_brytarar": (135, 1.0), "13_jack": (45, 0.8), "14_kretskort": (135, 0.8)}


def ark_T00(D, p, sjekk):
    A = Ark("T00", "Samanstilling", "FYR", "Sjå stykkliste", "Sjå stykkliste", "1:2 (detaljar 2:1)", "Samanstillingsteikning")
    k = 0.5
    bb = {kk: s.BoundingBox() for kk, s in D.items()}
    z_topp = max(b.zmax for b in bb.values())
    z_botn = min(b.zmin for b in bb.values())
    F = Vis(A, (1, 0, 0), (0, 1, 0), k, (0, 0, 0), (80, 212), namn="F")
    synlege = [s for kk, s in D.items() if not (bb[kk].zmax < p.z_spalte_0 and
               max(abs(bb[kk].xmin), abs(bb[kk].xmax), abs(bb[kk].ymin), abs(bb[kk].ymax)) < p.r_mi)]
    F.liner(hlr(synlege, (1, 0, 0), (0, 1, 0), 0.05))
    F.senterlinje((0, 0, 0), (0, 0, z_topp))
    o, n, x = akse_snitt(0.0)
    snittlinje(F, (0, 0.37, z_botn - 34), (0, 0.37, z_topp + 50), "A", (1, 0))
    S = Vis(A, n, x, k, (0, 0, 0), (165, 212), namn="S")
    sn = snitt(D, o, n, x, 0.03)
    S.skravur(sn["polys"], SKRAVUR_T00, tynn=0.6)
    S.liner(sn["liner"])
    S.senterlinje((0, 0, 0), (0, 0, z_topp))
    R = p.fot_d / 2
    ytopp = F.P((0, 0, z_topp))[1]
    xl = F.P((0, -R, 0))[0]
    xr = F.P((0, R, 0))[0]
    with valfri("T00 diametrar"):
        F.maal((0, -R, p.z_fot_0), (0, R, p.z_fot_0), "h", F.P((0, 0, 0))[1] + 9, DIA + tal(p.fot_d), p.fot_d)
        F.maal((0, -p.r_ho, p.z_hylse_1), (0, p.r_ho, p.z_hylse_1), "h", ytopp - 9, DIA + tal(2 * p.r_ho), 2 * p.r_ho)
        F.maal((0, -p.r_mo, p.z_mantel_1), (0, p.r_mo, p.z_mantel_1), "h", ytopp - 18, DIA + tal(p.mantel_d), p.mantel_d)
    with valfri("T00 høgder"):
        F.maal((0, -R, z_botn), (0, -R, z_topp), "v", xl - 22, tal(z_topp - z_botn), z_topp - z_botn)
        F.maal((0, -R, z_botn), (0, -p.r_mo, p.z_spalte_0), "v", xl - 11, tal(p.z_spalte_0 - z_botn), p.z_spalte_0 - z_botn)
        F.maal((0, -p.r_mo, p.z_spalte_0), (0, -p.r_mo, p.z_spalte_1), "v", xl - 11, tal(p.spalte_l), p.spalte_l)
        F.maal((0, -p.r_mo, p.z_mantel_1), (0, -p.r_ho, p.z_hylse_1), "v", xl - 11, tal(p.z_hylse_1 - p.z_mantel_1),
               p.z_hylse_1 - p.z_mantel_1)
        F.maal((0, R, p.z_fot_0), (0, R, p.z_fot_1), "v", xr + 8, tal(p.fot_h), p.fot_h)
        F.maal((0, p.r_mo, p.z_spalte_1), (0, p.r_mo, p.z_mantel_1), "v", xr + 8, tal(p.spalte_topp), p.spalte_topp)
    # titlane under snittpila A (pila endar under målet for Ø99)
    y_titt = F.P((0, 0, z_botn - 34))[1] + 17
    F.tittel("FRAMANFRÅ", under=y_titt, dy=0)
    S.tittel("SNITT A-A", under=y_titt, dy=0)
    # detaljar 2:1
    stil2 = {kk: (v[0], 1.4) for kk, v in SKRAVUR_T00.items()}
    with valfri("T00 detalj B"):
        detalj(A, S, sn, (p.bor_r + 1.5, 0.0, (p.toppdekk_z1 + pv(p, "z_fotring_1", p.toppdekk_z1 + 13)) / 2), 13.0, "B", 2.0,
               (240, 158), stil2, lab_vinkel=-45.0)
    with valfri("T00 detalj C"):
        detalj(A, S, sn, (p.r_mi - 2.0, 0.0, p.z_mantel_1 - 2.0), 14.0, "C", 2.0, (301, 158), stil2, lab_vinkel=110.0)
    with valfri("T00 detalj D"):
        detalj(A, S, sn, (p.r_mo - 3.0, 0.0, p.z_fot_0 + 8.0), 11.0, "D", 2.0, (361, 158), stil2, lab_vinkel=-90.0)
    # ballongar
    anker = {}
    for namn, pl in sn["polys"].items():
        if pl:
            gm = unary_union([S.ringar_til_poly(r) for r in pl])
            big = max(gm.geoms, key=lambda q: q.area) if hasattr(gm, "geoms") else gm
            if big.area > 0:
                rp = big.representative_point()
                anker[namn] = S.Q(rp.x, rp.y)
    for namn, s in D.items():
        if namn not in anker:
            for so in s.Solids():
                c = so.Center()
                if (np.array((c.x, c.y, c.z)) - np.array(o)) @ np.array(n) < 0:
                    anker[namn] = S.P((c.x, c.y, c.z))
                    break
    with valfri("T00 manuelle anker"):
        anker["11_oring"] = S.P((p.oring_id / 2 + p.oring_strekk_r + p.oring_snor / 2, 0, p.z_fot_0 + 0.6))
        anker["10_glidering"] = S.P((p.r_mi - p.glide_t / 2, 0, (p.z_glide_0 + p.z_glide_1) / 2))
        anker["05_hylse"] = S.P(((p.r_ho + p.r_hi) / 2, 0, 200.0))
        anker["04_mantel"] = S.P(((p.r_mo + p.r_mi) / 2, 0, 50.0))
        anker["08_lok"] = S.P((p.r_lok * 0.6, 0, p.z_lok_0 + p.lok_t / 2))
        anker["06_lysstav"] = S.P((0, 0, 200.0))
    ax = S.P((0, 0, 0))[0]
    venstre = sorted([kk for kk in anker if anker[kk][0] < ax], key=lambda kk: anker[kk][1])
    hogre = sorted([kk for kk in anker if anker[kk][0] >= ax], key=lambda kk: anker[kk][1])

    def fordel(liste, xb, y0, y1, dy=9.2):
        ut = []
        for kk in liste:
            yy = max(anker[kk][1], (ut[-1] + dy) if ut else y0)
            ut.append(yy)
        if ut and ut[-1] > y1:
            ut[-1] = y1
            for i in range(len(ut) - 2, -1, -1):
                ut[i] = min(ut[i], ut[i + 1] - dy)
        for kk, yy in zip(liste, ut):
            A.ballong(anker[kk], (xb, yy), kort_id(kk))

    fordel(venstre, S.P((-R, 0, 0))[0] - 12, 30, 218)
    fordel(hogre, S.P((R, 0, 0))[0] + 12, 30, 218)
    # stykkliste
    rader = [("Pos.", "Namn", "Tal", "Materiale", "Overflate", "Standard / teikning")]
    for namn in D:
        nn, mat, ov, st = stykk(namn)
        n_lek = len(D[namn].Solids())
        rader.append((kort_id(namn), nn, str(n_lek), mat, ov, st))
        sjekk["stykkliste_tal"][namn] = n_lek
    ks_d, ks_l, _zc, _sp, _inn = knaststift(p)
    for r in EKSTRA:
        rader.append(tuple(c.format(n_sw2=2 * len(p.sw), ks_d=tal(ks_d), ks_l=tal(ks_l), ss_l=tal(STIFT_STOLPE_L)) for c in r))
    yb = A.tabell(214, 14, [10, 34, 8, 58, 46, 38], rader, h=2.2, rh=4.0)
    A.tekst((214, yb + 3.6), "Stykkliste. Tal = lekamar i B-rep per del. H-, E- og S-radene er ikkje modellerte; posisjonane er "
            "dei same som i", 2.0, anker="start")
    A.tekst((214, yb + 6.8), INNKJOP + " (S01a/S01b er seriestifta i foten, del av S01).", 2.0, anker="start")
    sjekk["T00_stykkliste_botn_y"] = round(yb + 6.8, 2)
    A.tekstblokk((214, 207), [
        "Merknader",
        "1. Hylsa er vist i stilling 0° (open). Vandring %s°: %s stillingar (1-%d), %d steg à %s°." % (
            tal(p.vandring), {9: "ni"}.get(int(round(p.vandring / p.deling)) + 1, str(int(round(p.vandring / p.deling)) + 1)),
            int(round(p.vandring / p.deling)) + 1, int(round(p.vandring / p.deling)), tal(p.deling, 3)),
        "2. Snitt A-A i planet y = %s (utanfor skøytane). Tynne snitt er fylte svarte." % tal(0.37),
        "3. Asimut 0° = +X = vindauget (framme). Kabelen går ut bak (180°).",
        "4. Kopling: sjå FYR-E01. Mål for einskilde delar: sjå delteikningane.",
    ], h=2.2, feit_forste=True)
    # sjølvkontroll T00 mot B-rep
    rm = (p.r_mo + p.r_mi) / 2
    a0 = p.vindauge_vinklar[0] * DEG
    m_iv = holrom(D["04_mantel"], (rm * math.cos(a0), rm * math.sin(a0), p.z_mantel_0 + 0.5),
                  (rm * math.cos(a0), rm * math.sin(a0), p.z_mantel_1 - 0.5))
    slot = (p.z_mantel_0 + 0.5 + m_iv[0][0], p.z_mantel_0 + 0.5 + m_iv[0][1]) if m_iv else (float("nan"),) * 2
    zmin_all = min(b.zmin for b in bb.values())
    brep = {
        DIA + tal(p.fot_d): ("01_fot bbox x", bb["01_fot"].xlen),
        DIA + tal(2 * p.r_ho): ("05_hylse bbox y", bb["05_hylse"].ylen),
        DIA + tal(p.mantel_d): ("04_mantel bbox y", bb["04_mantel"].ylen),
        tal(z_topp - z_botn): ("alle delar bbox z", max(b.zmax for b in bb.values()) - zmin_all),
        tal(p.z_spalte_0 - z_botn): ("04_mantel spalte z0 (linjeprobe)", slot[0] - zmin_all),
        tal(p.spalte_l): ("04_mantel spaltelengd (linjeprobe)", slot[1] - slot[0]),
        tal(p.z_hylse_1 - p.z_mantel_1): ("05_hylse zmax - 04_mantel zmax", bb["05_hylse"].zmax - bb["04_mantel"].zmax),
        tal(p.fot_h): ("01_fot bbox z", bb["01_fot"].zlen),
        tal(p.spalte_topp): ("04_mantel zmax - spalte z1", bb["04_mantel"].zmax - slot[1]),
    }
    rad = []
    for tekst, verdi, papir in A.maallogg:
        kj, b = brep.get(tekst, (None, None))
        rad.append({"tekst": tekst, "verdi_frå_FyrParams": round(verdi, 4), "målt_på_papiret": round(papir, 3),
                    "brep_kjelde": kj, "brep": None if b is None else round(b, 4),
                    "ok": bool((abs(papir - verdi) < 0.05) and (b is None or abs(b - verdi) < 0.01))})
    sjekk["T00_maal_mot_brep"] = rad
    return A


# ============================================================================ T01 fot
def oringspor(s, p, sjekk):
    """O-ringsporet under foten, målt på B-rep langs +y (90°, vekk frå skruehol og kabelhol) 1 mm over underkanten.
    Gjev (r_inn, r_ut, djupn). Sjølvkontrollen samanliknar med FyrParams (oring_id/2 + oring_strekk_r)."""
    r0, z = 38.0, p.z_fot_0 + 0.5 * p.oring_spor_djup
    hr = [q for q in holrom(s, (0.0, r0, z), (0.0, p.fot_d / 2.0 - 0.5, z)) if q[1] - q[0] < 6.0]
    r_i, r_u = r0 + hr[0][0], r0 + hr[0][1]
    iv = gjennom(s, (0.0, (r_i + r_u) / 2, p.z_fot_0 - 1.0), (0.0, (r_i + r_u) / 2, p.z_fot_1 + 1.0))
    djup = p.z_fot_0 - 1.0 + iv[0][0] - p.z_fot_0
    r_par = p.oring_id / 2.0 + p.oring_strekk_r
    sjekk["T01_oringspor"] = {"r_inn_brep": round(r_i, 4), "r_ut_brep": round(r_u, 4), "djup_brep": round(djup, 4),
                              "r_inn_param": round(r_par, 4), "breidd_param": p.oring_spor_b,
                              "ok": bool(abs(r_i - r_par) < 0.01 and abs(r_u - r_i - p.oring_spor_b) < 0.01
                                         and abs(djup - p.oring_spor_djup) < 0.01)}
    return r_i, r_u, djup


def ark_T01(D, p, sjekk):
    mat, ov, _ = SERIE["01_fot"]
    A = Ark("T01", "Fot", "01", mat, ov, "1:1 (detaljar 3:1, 5:1)")
    s = D["01_fot"]
    o, n, x = akse_snitt(0.0)
    sn = snitt({"01_fot": s}, o, n, x, 0.02)
    st = {"01_fot": (45, 2.0)}
    S = Vis(A, n, x, 1.0, (0, 0, 0), (100, 58), namn="S")
    S.skravur(sn["polys"], st)
    S.liner(sn["liner"])
    S.senterlinje((0, 0, p.z_fot_0), (0, 0, p.z_fot_1))
    T = Vis(A, (0, 0, 1), (0, 1, 0), 1.0, (0, 0, 0), (100, 150), namn="T")
    T.liner(hlr([s], (0, 0, 1), (0, 1, 0), 0.02))
    T.senterkryss((0, 0, 0), p.fot_d / 2 + 4)
    T.sirkel_c((0, 0, p.z_fot_1), p.skrue_r)
    snittlinje(T, (-p.fot_d / 2 - 6, 0.37, p.z_fot_1), (p.fot_d / 2 + 6, 0.37, p.z_fot_1), "A", (1, 0))
    B = Vis(A, (0, 0, -1), (0, 1, 0), 1.0, (0, 0, 0), (232, 150), namn="B")
    B.liner(hlr([s], (0, 0, -1), (0, 1, 0), 0.02))
    B.senterkryss((0, 0, 0), p.fot_d / 2 + 4)
    B.sirkel_c((0, 0, p.z_fot_0), p.skrue_r)
    R = p.fot_d / 2
    yb = S.P((0, 0, p.z_fot_0))[1]
    yt = S.P((0, 0, p.z_fot_1))[1]
    r_a = p.r_mi - p.spor_klaring_inn
    r_b = p.r_mo + p.spor_klaring_ut
    S.maal((-R, 0, p.z_fot_0), (R, 0, p.z_fot_0), "h", yb + 9, DIA + tal(p.fot_d), p.fot_d, pos=0.7)
    S.maal((R, 0, p.z_fot_0), (R, 0, p.z_fot_1), "v", S.P((R, 0, 0))[0] + 8, tal(p.fot_h), p.fot_h)
    S.maal((-r_a, 0, p.z_fot_1), (r_a, 0, p.z_fot_1), "h", yt - 7, DIA + tal(2 * r_a), 2 * r_a)
    S.maal((-r_b, 0, p.z_fot_1), (r_b, 0, p.z_fot_1), "h", yt - 14, DIA + tal(2 * r_b), 2 * r_b)
    cyl = sylinderflater(s)
    r_l, z_l, z_g0 = 30.0, p.z_fot_0, p.z_fot_0
    with valfri("T01 lomme"):
        lom = [c for c in cyl if abs(c["dir"][2]) > 0.99 and np.hypot(*c["loc"][:2]) < 0.01 and c["r"] < r_a - 1]
        r_l = max(c["r"] for c in lom)
        # golvet i lomma målt på B-rep: loddrett linje gjennom lomma (x = +22, vekk frå stolpane)
        x_pr = 22.0
        iv_l = gjennom(s, (x_pr, 0.0, p.z_fot_1 + 1.0), (x_pr, 0.0, p.z_fot_0 - 1.0))
        z_l = p.z_fot_1 + 1.0 - iv_l[0][0]          # overkant golv
        z_g0 = p.z_fot_1 + 1.0 - iv_l[0][1]         # underkant
        S.maal((-r_l, 0, p.z_fot_1), (r_l, 0, p.z_fot_1), "h", yt - 21, DIA + tal(2 * r_l), 2 * r_l)
        # lommedjupn frå overflata (veggtoppen ved r_l + 1) ned til golvet, inne i lomma
        S.maal((x_pr, 0, z_l), (r_l + 1.0, 0, p.z_fot_1), "v", S.P((x_pr, 0, 0))[0], tal(p.z_fot_1 - z_l), p.z_fot_1 - z_l,
               tekst_ut=False)
        sjekk["T01_lomme"] = {"r": round(r_l, 4), "golv_z": round(z_l, 4), "golv_tjukn": round(z_l - z_g0, 4),
                              "djupn": round(p.z_fot_1 - z_l, 4), "fot_lomme_z_param": pv(p, "fot_lomme_z")}
    with valfri("T01 skruehol"):
        hol = [c for c in cyl if abs(c["dir"][2]) > 0.99 and abs(np.hypot(*c["loc"][:2]) - p.skrue_r) < 0.01]
        r_g = min(c["r"] for c in hol)
        r_s = max(c["r"] for c in hol)
        z_s = max(c["z"][1] for c in hol if abs(c["r"] - r_s) < 1e-6)
        S.merknad(S.P((p.skrue_r + r_s, 0, p.z_fot_0 + (z_s - p.z_fot_0) / 2)), (S.P((R, 0, 0))[0] + 20, yb + 18),
                  ["3 x %s%s gjennom, senk %s%s djup %s" % (DIA, tal(2 * r_g), DIA, tal(2 * r_s), tal(z_s - p.z_fot_0)),
                   "på %s%s ved %s° for ISO 7380 M3 x 16" % (DIA, tal(2 * p.skrue_r), "/".join(tal(a) for a in p.skrue_vinklar))])
    with valfri("T01 kabelhol"):
        kab = [c for c in cyl if abs(c["dir"][0]) > 0.99]
        r_k, z_k = kab[0]["r"], kab[0]["loc"][2]
        # fasen ytst: opninga målt på B-rep 0,02 inn frå ytterflata (45°-fas)
        d_e = 0.02
        iv_k = holrom(s, (-(R - d_e), 0.0, z_k - 4.0), (-(R - d_e), 0.0, z_k + 4.0))
        r_fas = max(q[1] - q[0] for q in iv_k) / 2.0 + d_e
        fas_k = r_fas - r_k
        sjekk["T01_kabelhol"] = {"d": round(2 * r_k, 4), "z_senter_over_underkant": round(z_k - p.z_fot_0, 4),
                                 "fas_målt": round(fas_k, 4)}
        S.merknad(S.P((-R + 0.3, 0, z_k)), (S.P((-R, 0, 0))[0] + 2, yb + 30),
                  ["Kabelhol %s%s radielt ved 180°," % (DIA, tal(2 * r_k)), "senter %s over underkant," % tal(z_k - p.z_fot_0),
                   "fas %s x 45° ytst" % tal(fas_k, 1)], side=1)
    S.tittel("SNITT A-A", under=yb + 9, dy=15)
    # lommer for silikonsnor i golvet av mantelsporet (snittet ved 0° går gjennom den eine), målt på B-rep
    snor = None
    with valfri("T01 snorlommer"):
        r_s = (p.r_mi + p.r_mo) / 2.0
        z_p = p.z_mantel_0 - 0.3
        bb_r = holrom(s, (r_a - 0.5, 0.0, z_p), (r_b + 0.5, 0.0, z_p))
        hr = [q for q in bb_r if q[1] - q[0] < 4.0]
        b_snor = hr[0][1] - hr[0][0]
        iv_s = gjennom(s, (r_s, 0.0, p.z_mantel_0 + 2.0), (r_s, 0.0, p.z_mantel_0 - 4.0))
        z_sb = p.z_mantel_0 + 2.0 - iv_s[0][0]
        d_snor = p.z_mantel_0 - z_sb

        def open_(a):
            return not inni(s, (r_s * math.cos(a * DEG), r_s * math.sin(a * DEG), z_p))
        kant = []
        for sg in (-1, 1):
            lo, hi = 0.0, sg * 30.0
            for _ in range(40):
                m = (lo + hi) / 2
                if open_(m):
                    lo = m
                else:
                    hi = m
            kant.append(lo)
        l_snor = r_s * abs(kant[1] - kant[0]) * DEG
        vinklar_s = [a for a in range(0, 360, 5) if open_(float(a))]
        snor = dict(breidd=b_snor, djup=d_snor, boge=l_snor, r=r_s)
        sjekk["T01_snorlommer"] = {"breidd": round(b_snor, 4), "djup": round(d_snor, 4), "bogelengd_r_midt": round(l_snor, 4),
                                   "r_midt": round(r_s, 4), "opne_vinklar_5grad": vinklar_s}
        S.merknad(S.P((r_s, 0, z_sb + 0.3)), (S.P((R, 0, 0))[0] + 10, 19.0),
                  ["3 lommer for silikonsnor %s%s x %s ved %s°" % (DIA, tal(p.snor_d), tal(p.snor_l),
                                                                 "/".join(tal(a) for a in p.snor_vinklar)),
                   "i golvet av sporet: breidd %s, boge %s på r = %s," % (tal(b_snor), tal(l_snor, 1), tal(r_s)),
                   "djup %s under sporgolvet" % tal(d_snor)], side=1)
    # detalj F (3:1) ved 180°: golvet i lomma, stolpane for strekkavlastning, kabelholet
    stolpar = sorted([c for c in cyl if abs(c["dir"][2]) > 0.99 and 10.0 < np.hypot(*c["loc"][:2]) < r_l - 1.0
                      and c["r"] < 2.0], key=lambda c: c["loc"][0])
    with valfri("T01 detalj F"):
        cF = (-22.0, 0.0, 8.0)
        Fd = detalj(A, S, sn, cF, 10.0, "F", 3.0, (345, 174), st, lab_vinkel=-60.0)
        xd = -21.0
        Fd.maal((xd, 0, z_g0), (xd, 0, z_l), "v", 345 + 30 + 7, tal(z_l - z_g0), z_l - z_g0, tekst_ut=False)
        s1 = stolpar[0]
        x1 = s1["loc"][0] + s1["r"]
        z1s = s1["z"][1]
        Fd.maal((x1, 0, z_l), (x1, 0, z1s), "v", Fd.P((xd, 0, 0))[0], tal(z1s - z_l), z1s - z_l, tekst_ut=False)
        for nr, c in enumerate(stolpar):
            if c["loc"][1] > 0:          # stolpane på augesida er kutta bort i snittet
                A.tekst(Fd.P((c["loc"][0], 0, (z_l + c["z"][1]) / 2 + 1.0)), "P%d" % (nr + 1), 2.2)
        A.tekst((345, 174 + 30 + 13.5), "P2 ligg framfor snittplanet. CAD-stolpe %s over golvet;" % tal(z1s - z_l), 2.0)
        A.tekst((345, 174 + 30 + 16.7), "serie: stift %s3 x %s flukt med botnen, topp %s over golvet" % (
            DIA, tal(STIFT_STOLPE_L), tal(STIFT_STOLPE_L - (z_l - z_g0))), 2.0)
    with valfri("T01 stolpetabell"):
        golv_t = z_l - z_g0
        rader = [("Pos.", "x", "y", "Ø", "Topp CAD", "Topp serie")]
        for nr, c in enumerate(stolpar):
            rader.append(("P%d" % (nr + 1), tal(c["loc"][0]), tal(c["loc"][1]), tal(2 * c["r"]), tal(c["z"][1] - z_l),
                          tal(STIFT_STOLPE_L - golv_t)))
        A.tekst((158, 237.5), "Stolpar (strekkavlastning)", 2.1, anker="start", feit=True)
        A.tekst((158, 240.8), "origo i aksen, x mot 0° (framme); topp over golvet i lomma", 1.8, anker="start")
        A.tabell(158, 242.5, [9, 12, 12, 7, 14, 14], rader, h=2.2, rh=4.3)
        sjekk["T01_stolpar"] = [{"x": round(c["loc"][0], 4), "y": round(c["loc"][1], 4), "d": round(2 * c["r"], 4),
                                 "z0": round(c["z"][0], 4), "z1": round(c["z"][1], 4),
                                 "topp_over_golv_cad": round(c["z"][1] - z_l, 4),
                                 "topp_over_golv_serie_stift": round(STIFT_STOLPE_L - golv_t, 4)} for c in stolpar]
    # detalj E (5:1) ved 180°: spor, knast og O-ringspor
    with valfri("T01 detalj E"):
        cE = (-(r_a + r_b) / 2 - 0.8, 0.0, p.z_fot_0 + 7.0)
        RE = 8.5
        E = detalj(A, S, sn, cE, RE, "E", 5.0, (345, 66), st, lab_vinkel=110.0)
        zk0 = p.z_mantel_0 + p.baj_knast_z
        # loddrette mål utanfor detaljsirkelen (ikkje oppå skraveringa)
        xE_v = 345 - RE * 5.0 - 6.0
        xE_h = 345 + RE * 5.0 + 6.0
        E.maal((-r_b, 0, p.z_fot_1), (-r_a, 0, p.z_fot_1), "h", E.P((0, 0, p.z_fot_1))[1] - 6, tal(r_b - r_a), r_b - r_a)
        E.maal((-r_a, 0, p.z_mantel_0), (-r_a, 0, p.z_fot_1), "v", xE_h, tal(p.spor_djup), p.spor_djup)
        xk = -(r_a + p.baj_knast_ut)
        # utstikket (1,25) står i merknaden ved sett ovanfrå: knastkanten ligg midt i sporet, så eit mål her ville
        # leggje talet over hjelpelina
        E.maal((xk, 0, zk0), (xk, 0, zk0 + p.baj_knast_h), "v", xE_v, tal(p.baj_knast_h), p.baj_knast_h, tekst_ut=False)
        E.maal((xk, 0, p.z_mantel_0), (xk, 0, zk0), "v", xE_v - 8, tal(p.baj_knast_z), p.baj_knast_z, tekst_ut=False)
        r_o_in = oringspor(s, p, sjekk)[0]
        E.maal((-r_o_in, 0, p.z_fot_0), (-(r_o_in + p.oring_spor_b), 0, p.z_fot_0), "h", E.P((0, 0, p.z_fot_0))[1] + 9,
               tal(p.oring_spor_b), p.oring_spor_b)
        E.maal((-(r_o_in + p.oring_spor_b), 0, p.z_fot_0), (-(r_o_in + p.oring_spor_b), 0, p.z_fot_0 + p.oring_spor_djup), "v",
               xE_v, tal(p.oring_spor_djup), p.oring_spor_djup, tekst_ut=False)
    with valfri("T01 toppvising"):
        T.maal((0, -p.skrue_r, p.z_fot_1), (0, p.skrue_r, p.z_fot_1), "a", 0.0, DIA + tal(2 * p.skrue_r), 2 * p.skrue_r)
        T.vinkelmaal((0, 0), p.skrue_r - 9, p.skrue_vinklar[0], p.baj_vinklar[0], p.z_fot_1, tal(p.baj_vinklar[0] - p.skrue_vinklar[0]) + "°",
                     p.baj_vinklar[0] - p.skrue_vinklar[0], tekst_r=p.skrue_r - 14)
        a = p.baj_vinklar[0] * DEG
        T.merknad(T.P(((r_a + 0.6) * math.cos(a), (r_a + 0.6) * math.sin(a), p.z_fot_1)), (T.P((0, 0, 0))[0] + 27, T.P((0, 0, 0))[1] + 68),
                  ["3 bajonettknastar ved %s°:" % "/".join(tal(a_) for a_ in p.baj_vinklar),
                   "radiell sylinderstift %s%s, utstikk %s frå sporveggen" % (DIA, tal(p.baj_knast_b),
                                                                          tal(p.baj_knast_ut + p.spor_klaring_inn)),
                   "Serie: stift %s%s x %s, sjå merknad 4" % (DIA, tal(knaststift(p)[0]), tal(knaststift(p)[1]))], side=1)
    with valfri("T01 stolpar ovanfrå"):
        s2 = stolpar[1]
        T.merknad(T.P((s2["loc"][0], s2["loc"][1] - s2["r"], p.z_fot_1)), (T.P((0, 0, 0))[0] - 30, T.P((0, 0, 0))[1] - 44),
                  ["Stolpar P1..P3, sjå F og tabell"], h=2.2, side=-1)
    # tittelen under den nedre snittpila A
    T.tittel("SETT OVANFRÅ", under=T.P((p.fot_d / 2 + 6, 0, 0))[1] + 9, dy=8)
    # asimutreferanse: 0° = +X (vindauget), positiv mot klokka sett ovanfrå
    yT = T.P((p.fot_d / 2 + 6, 0, 0))[1] + 9 + 8
    A.tekst((T.px, yT + 4.2), "0° = +X (framme) peikar nedover;", 2.2)
    A.tekst((T.px, yT + 7.6), "asimut positiv mot klokka sett ovanfrå", 2.2)
    for V_, ned in ((T, True), (B, False)):
        q0 = np.array(V_.P((p.fot_d / 2 + 0.5, 0, p.z_fot_1)))
        q1 = np.array(V_.P((p.fot_d / 2 + 4.5, 0, p.z_fot_1)))
        V_.ark.linje(q0, q1, "t")
        A.tekst((q1[0] - 1.5, q1[1] + (3.0 if ned else -1.0)), "0°", 2.5, anker="end")
    with valfri("T01 botn"):
        r_o_in = oringspor(s, p, sjekk)[0]
        B.maal((0, -(r_o_in + p.oring_spor_b), p.z_fot_0), (0, r_o_in + p.oring_spor_b, p.z_fot_0), "a", 0.0,
               DIA + tal(2 * (r_o_in + p.oring_spor_b)), 2 * (r_o_in + p.oring_spor_b))
        a = 120 * DEG
        B.merknad(B.P(((r_o_in + 1.4) * math.cos(a), (r_o_in + 1.4) * math.sin(a), p.z_fot_0)), (B.P((0, 0, 0))[0] + 30, B.P((0, 0, 0))[1] + 74),
                  ["O-ringspor %s%s / %s%s, djup %s," % (DIA, tal(2 * r_o_in), DIA, tal(2 * (r_o_in + p.oring_spor_b)), tal(p.oring_spor_djup)),
                   "for O-ring %s x %s silikon 60 ShA" % (tal(p.oring_id), tal(p.oring_snor))])
    B.tittel("SETT NEDANFRÅ")
    yB = B.bbox[3] + 8
    A.tekst((B.px, yB + 4.2), "0° = +X peikar oppover; sett nedanfrå", 2.2)
    A.tekst((B.px, yB + 7.6), "går asimut med klokka", 2.2)
    ks_d, ks_l, ks_zc, ks_sp, ks_inn = knaststift(p)
    r_a_ = p.r_mi - p.spor_klaring_inn
    golv_t = sjekk.get("T01_lomme", {}).get("golv_tjukn", p.fot_lomme_z - p.z_fot_0)
    sjekk["T01_seriestift"] = {"knast": {"d": ks_d, "L": ks_l, "z_senter": round(ks_zc, 4), "spiss_r": round(ks_sp, 4),
                                         "innsenking_frå_lommeveggen": round(ks_inn, 4)},
                               "stolpe": {"d": 3.0, "L": STIFT_STOLPE_L, "topp_z": round(p.z_fot_0 + STIFT_STOLPE_L, 4),
                                          "topp_over_golv": round(STIFT_STOLPE_L - golv_t, 4)}}
    A.tekstblokk((26, 234), [
        "Merknader",
        "1. Dreia og fresa av EN AW-6082 T6. Skarpe kantar brotne 0,2.",
        "2. Pulverlakk RAL 3005 fin struktur matt; spor for mantel og O-ring maskerte.",
        "3. Ytre fas %s x 45°." % tal(p.fot_fas),
        "4. Serie: knastane er 3 sylinderstift ISO 8734 %s%s x %s m6 i hol %s%s H7," % (
            DIA, tal(ks_d), tal(ks_l), DIA, tal(ks_d)),
        "    radielt ved %s°, senter %s over underkant (z %s), bora frå lomma" % (
            "/".join(tal(a) for a in p.baj_vinklar), tal(ks_zc - p.z_fot_0), tal(ks_zc)),
        "    (vinkelhovud) gjennom til sporet. Spissen på r = %s (%s ut frå sporveggen" % (tal(ks_sp), tal(ks_sp - r_a_)),
        "    r = %s); bakenden %s inne frå lommeveggen r = %s." % (tal(r_a_), tal(ks_inn), tal(p.fot_lomme_r)),
        "5. Strekkavlastning: 3 stolpar %s3 i lomma (F, tabell). Serie: hol %s3 H7" % (DIA, DIA),
        "    gjennom golvet, stift ISO 8734 %s3 x %s m6 pressa opp nedanfrå, flukt med" % (DIA, tal(STIFT_STOLPE_L)),
        "    botnen: toppen står %s over golvet (z %s), %s under chassisflensen." % (
            tal(STIFT_STOLPE_L - golv_t), tal(p.z_fot_0 + STIFT_STOLPE_L), tal(p.z_fot_1 - p.z_fot_0 - STIFT_STOLPE_L)),
        "    CAD-stolpen (%s over golvet) gjeld prentet." % (
            tal(sjekk.get("T01_stolpar", [{}])[0].get("topp_over_golv_cad", float("nan")))),
        "6. Snorlommene tek 3 bitar silikonsnor %s2 x 10 (forspenning av bajonetten)." % DIA,
    ], h=2.2, feit_forste=True)
    return A


# ============================================================================ T03 chassis
def ark_T03(D, p, sjekk):
    mat, ov, _ = SERIE["03_chassis"]
    A = Ark("T03", "Chassis", "03", mat, ov, "1:1 (detalj 5:1)")
    s = D["03_chassis"]
    zb = p.z_fot_1
    bbc = s.BoundingBox()
    st = {"03_chassis": (45, 2.0)}
    F = Vis(A, (1, 0, 0), (0, 1, 0), 1.0, (0, 0, zb), (70, 112), namn="F")
    F.liner(hlr([s], (1, 0, 0), (0, 1, 0), 0.03))
    F.senterlinje((0, 0, zb), (0, 0, bbc.zmax))
    o, n, x = akse_snitt(0.0)
    sn = snitt({"03_chassis": s}, o, n, x, 0.02)
    S = Vis(A, n, x, 1.0, (0, 0, zb), (172, 112), namn="S")
    S.skravur(sn["polys"], st)
    S.liner(sn["liner"])
    S.senterlinje((0, 0, zb), (0, 0, bbc.zmax))
    snittlinje(F, (0, 0.37, zb - 6), (0, 0.37, bbc.zmax + 6), "A", (1, 0))
    T = Vis(A, (0, 0, 1), (0, 1, 0), 1.0, (0, 0, 0), (70, 192), namn="T")
    T.liner(hlr([s], (0, 0, 1), (0, 1, 0), 0.03))
    T.senterkryss((0, 0, 0), p.chassis_r + 4)
    T.sirkel_c((0, 0, bbc.zmax), p.skrue_r)
    phiB = p.sw[0][0]
    oB, nB, xB = akse_snitt(phiB)
    snB = snitt({"03_chassis": s}, oB, nB, xB, 0.02)
    SB = Vis(A, nB, xB, 1.0, (0, 0, zb), (302, 112), namn="SB")
    SB.skravur(snB["polys"], {"03_chassis": (135, 2.0)})
    SB.liner(snB["liner"])
    SB.senterlinje((0, 0, zb), (0, 0, bbc.zmax))
    c, s_ = math.cos(phiB * DEG), math.sin(phiB * DEG)
    Rl = p.chassis_r + 6
    sjaa = np.array(T.P((s_, -c, 0))) - np.array(T.P((0, 0, 0)))
    snittlinje(T, (-c * Rl - s_ * 0.37, -s_ * Rl + c * 0.37, bbc.zmax), (c * Rl - s_ * 0.37, s_ * Rl + c * 0.37, bbc.zmax), "B", tuple(sjaa))
    R = p.chassis_r
    yb = S.P((0, 0, zb))[1]
    ytop = S.P((0, 0, bbc.zmax))[1]
    S.maal((-R, 0, zb), (R, 0, zb), "h", yb + 9, DIA + tal(2 * R), 2 * R, pos=0.72)
    with valfri("T03 diametrar"):
        S.maal((-p.toppdekk_r, 0, p.toppdekk_z1), (p.toppdekk_r, 0, p.toppdekk_z1), "h", ytop - 15,
               DIA + tal(2 * p.toppdekk_r), 2 * p.toppdekk_r, avvik=TOL["toppdekk"])
        S.maal((-p.tapp_ro, 0, p.tapp_topp), (p.tapp_ro, 0, p.tapp_topp), "h", ytop - 7, DIA + tal(2 * p.tapp_ro), 2 * p.tapp_ro,
               avvik=TOL["tapp"])
    with valfri("T03 høgder"):
        xr = S.P((R, 0, 0))[0]
        for i, z1 in enumerate((zb + p.chassis_flens_t, p.dekk_z, p.z_toppdekk_0, p.toppdekk_z1, p.tapp_topp)):
            S.maal((p.toppdekk_r if z1 >= p.z_toppdekk_0 else R, 0, zb), (p.toppdekk_r if z1 >= p.z_toppdekk_0 else R, 0, z1), "v",
                   xr + 6 + 6 * i, tal(z1 - zb), z1 - zb)
    cyl = sylinderflater(s)
    with valfri("T03 innsatsar"):
        ins = [cc for cc in cyl if abs(cc["dir"][2]) > 0.99 and abs(np.hypot(*cc["loc"][:2]) - p.skrue_r) < 0.01]
        r_i = min(cc["r"] for cc in ins)
        r_bo = max(cc["r"] for cc in ins)
        dj = gjennom(s, (p.skrue_r, 0, zb - 1), (p.skrue_r, 0, bbc.zmax + 1))
        d_ins = dj[0][0] - 1.0
        S.merknad(S.P((p.skrue_r, 0, zb + d_ins * 0.5)), (S.P((R, 0, 0))[0] + 4, yb + 31),
                  ["3 x %s%s djup %s for gjengeinnsats M3 x %s," % (DIA, tal(2 * r_i), tal(d_ins), tal(p.innsats_l)),
                   "nav %s%s, på %s%s ved %s°" % (DIA, tal(2 * r_bo), DIA, tal(2 * p.skrue_r), "/".join(tal(a) for a in p.skrue_vinklar))])
    with valfri("T03 kabelhol"):
        kab = [cc for cc in cyl if abs(cc["dir"][2]) > 0.99 and cc["loc"][0] < -5 and abs(cc["loc"][1]) < 0.01 and cc["r"] > 2.5]
        kk = max(kab, key=lambda q: q["r"])
        S.merknad(S.P((kk["loc"][0] - kk["r"] * 0.5, 0, zb + p.chassis_flens_t / 2)), (S.P((-R, 0, 0))[0] - 6, yb + 31),
                  ["Kabelhol %s%s, senter x = %s" % (DIA, tal(2 * kk["r"]), tal(kk["loc"][0]))], side=-1)
    S.tittel("SNITT A-A", under=yb + 9, dy=17)
    with valfri("T03 detalj Z"):
        a_st = p.stopp_vinklar[0]
        cZ = (p.tapp_ro - 1.0, 0.0, p.stopp_z)
        Z = detalj(A, S, sn, cZ, 5.0, "Z", 5.0, (383, 50), st, lab_vinkel=62.0)
        gv = gjennom(s, (p.tapp_ro - 0.3, 0.37, p.stopp_z - 5), (p.tapp_ro - 0.3, 0.37, p.stopp_z + 5))
        z_lo = p.stopp_z - 5 + gv[0][1]
        z_hi = p.stopp_z - 5 + gv[1][0]
        Z.maal((p.tapp_ro, 0, z_lo), (p.tapp_ro, 0, z_hi), "v", Z.P((p.tapp_ro, 0, 0))[0] + 8, tal(z_hi - z_lo), z_hi - z_lo)
        rr = gjennom(s, (p.tapp_ri - 0.5, 0.37, (z_lo + z_hi) / 2), (p.tapp_ro + 0.5, 0.37, (z_lo + z_hi) / 2))
        r_botn = (p.tapp_ri - 0.5) + rr[0][1]
        Z.maal((r_botn, 0, z_hi), (p.tapp_ro, 0, z_hi), "h", 50 - 5.0 * 5 - 3, tal(p.tapp_ro - r_botn), p.tapp_ro - r_botn)
        A.tekstblokk((343, 92), ["Spor for stoppskrue, 3 stk ved %s°" % "/".join(tal(a) for a in p.stopp_vinklar),
                                 "senter %s over underkant, sporbotn r = %s" % (tal(p.stopp_z - zb), tal(r_botn)),
                                 "spenn %s° + skrue, endestopp 0° og %s°" % (tal(p.vandring), tal(p.vandring))], h=2.2)
        sjekk["T03_stoppspor"] = {"breidd": round(z_hi - z_lo, 4), "sporbotn_r": round(r_botn, 4)}
    with valfri("T03 brytarspor"):
        T.merknad(T.P((p.sw_r * math.cos(p.sw[1][0] * DEG), p.sw_r * math.sin(p.sw[1][0] * DEG), bbc.zmax)),
                  (T.P((0, R, 0))[0] + 14, T.P((0, 0, 0))[1] - 30),
                  ["3 brytarslisser ved %s°, r = %s" % ("/".join(tal(a) for a, _ in p.sw), tal(p.sw_r))] + _spormaal_tekst(s, p), side=1)
    T.tittel("SETT OVANFRÅ")
    SB.tittel("SNITT B-B (%s°, SW1)" % tal(phiB), under=SB.P((0, 0, zb))[1] + 9, dy=8)
    F.tittel("FRAMANFRÅ", under=F.P((0, 0, zb))[1] + 9, dy=14)
    linjer = ["Merknader", "1. %s. Funksjonsflater: tapp %s%s (lager for fotringen), toppdekk %s%s." % (
        delar_tekst("03_chassis") or "PA12 MJF/SLS", DIA, tal(2 * p.tapp_ro), DIA, tal(2 * p.toppdekk_r)),
              "2. Gjengeinnsatsar M3 x %s varmepressa nedanfrå (3 stk)." % tal(p.innsats_l)]
    with valfri("T03 merknad tunge"):
        tv_ = list(pv(p, "tunge_vinklar", None) or [TUNGE(p)])
        linjer.append("3. Klikktunge%s ved %s°: lengd %s, tjukn %s, interferens %s mot boret i fotringen;" % (
            "r" if len(tv_) > 1 else "", "/".join(tal(a) for a in tv_), tal(p.tunge_l), tal(p.tunge_t), tal(p.tunge_kul)))
        linjer.append("    tungene står %s..%s over underkant (z %s..%s), tappen til %s." % (
            tal(p.klikk_z0 + 0.6 - zb), tal(p.tapp_topp - zb), tal(p.klikk_z0 + 0.6), tal(p.tapp_topp), tal(p.tapp_topp - zb)))

    with valfri("T03 merknad nøkkel"):
        linjer.append("4. Styrehol %s%s for nøkkeltappen på lysristen ved r = %s, asimut 0°." % (
            DIA, tal(p.nokkel_d + 0.5), tal(p.nokkel_r)))
    with valfri("T03 merknad TRS"):
        trs = [cc for cc in cyl if abs(cc["dir"][2]) > 0.99 and np.hypot(*cc["loc"][:2]) < 0.01 and cc["r"] < 5]
        linjer.append("5. Sokkel for mastfoten (06d); hol %s%s for TRS-kontakten (13), M6-bøssing." % (DIA, tal(2 * min(q["r"] for q in trs))))
    with valfri("T03 gjennomgang mastfot"):
        # gjennomgangen i navet på toppdekket, målt på B-rep under trakta (z_toppdekk_0 + 1)
        zg = p.z_toppdekk_0 + 1.0
        gx = [q for q in holrom(s, (-12.0, 0.0, zg), (12.0, 0.0, zg)) if q[0] < 12.0 < q[1]]
        gy = [q for q in holrom(s, (0.0, -14.0, zg), (0.0, 14.0, zg)) if q[0] < 14.0 < q[1]]
        bx_, ly_ = gx[0][1] - gx[0][0], gy[0][1] - gy[0][0]
        sjekk["T03_gjennomgang"] = {"x": round(bx_, 4), "y": round(ly_, 4),
                                    "ok": bool(abs(bx_ - p.mastfot_b - 0.6) < 0.01 and abs(ly_ - p.mastfot_l - 0.6) < 0.01)}
        linjer.append("    Gjennomgang %s x %s med trakt i navet for mastfoten (%s x %s, FYR-T06)." % (
            tal(bx_), tal(ly_), tal(p.mastfot_b), tal(p.mastfot_l)))
    with valfri("T03 sentreringstapp"):
        # bogetappen under flensen, målt på B-rep: radielt ved 0°, loddrett ved 0° og 180° (open for kabelen)
        zt_ = zb - 1.0
        iv = gjennom(s, (24.0, 0.0, zt_), (33.0, 0.0, zt_))
        r0_, r1_ = 24.0 + iv[0][0], 24.0 + iv[0][1]
        rm_ = (r0_ + r1_) / 2
        z_lo = zb - 5.0 + gjennom(s, (rm_, 0.0, zb - 5.0), (rm_, 0.0, zb + 1.0))[0][0]
        ved180 = gjennom(s, (-rm_, 0.0, zb - 5.0), (-rm_, 0.0, zb - 0.05))
        sjekk["T03_sentrering"] = {"r": [round(r0_, 4), round(r1_, 4)], "z_botn": round(z_lo, 4), "tapp_ved_180": bool(ved180)}
        linjer.append("6. Sentreringstapp under flensen: boge %s%s / %s%s (r = %s..%s), %s høg (z %s..%s), over 210..510°;" % (
            DIA, tal(2 * r0_), DIA, tal(2 * r1_), tal(r0_), tal(r1_), tal(zb - z_lo), tal(z_lo), tal(zb)))
        linjer.append("    open 150..210° for kabelen. Går i kabellomma %s%s i foten (01)." % (DIA, tal(2 * p.fot_lomme_r)))
    with valfri("T03 brytarbrakett"):
        a_sw = p.sw[0][0]

        def glob(lx, ly, z):
            c_, s_ = math.cos(a_sw * DEG), math.sin(a_sw * DEG)
            x0, y0 = g.polar(p.sw_r, a_sw)
            return (x0 + lx * c_ - ly * s_, y0 + lx * s_ + ly * c_, z)
        spor = []
        for y_h in (-6.85, -0.35):
            a_, b_ = glob(-3.8, y_h, p.sw_hol_z - 5.0), glob(-3.8, y_h, p.sw_hol_z + 5.0)
            hr = [q for q in holrom(s, a_, b_) if q[1] - q[0] < 8.0]
            h_ = hr[0][1] - hr[0][0]
            zc_ = p.sw_hol_z - 5.0 + (hr[0][0] + hr[0][1]) / 2
            hb = holrom(s, glob(-3.8, y_h - 3.0, p.sw_hol_z), glob(-3.8, y_h + 3.0, p.sw_hol_z))
            b_s = min((q[1] - q[0] for q in hb), default=float("nan"))
            spor.append((y_h, h_, b_s, zc_))
        tb = gjennom(s, glob(-8.0, -6.85 + 2.0, p.sw_hol_z), glob(0.0, -6.85 + 2.0, p.sw_hol_z))
        r_br = [p.sw_r - 8.0 + tb[0][0], p.sw_r - 8.0 + tb[0][1]] if tb else [float("nan")] * 2
        sjekk["T03_brytarspor"] = [{"y_lokal": y_, "høgd": round(h_, 4), "breidd": round(b_, 4), "z_senter": round(z_, 4)}
                                   for y_, h_, b_, z_ in spor] + [{"brakett_r": [round(v, 3) for v in r_br]}]
        h_, b_s, zc_ = spor[0][1], spor[0][2], spor[0][3]
        linjer.append("7. Brakett for kvar brytar (%s°): 2 loddrette spor %s x %s for M2 (H4) gjennom braketten (r = %s..%s)," % (
            "/".join(tal(a) for a, _ in p.sw), tal(b_s), tal(h_), tal(r_br[0]), tal(r_br[1])))
        linjer.append("    senter z %s (%s over underkant), justering ±%s; spora ligg %s og %s med klokka frå kontaktpunktet" % (
            tal(zc_), tal(zc_ - zb), tal(p.sw_just), tal(-spor[0][0]), tal(-spor[1][0])))
        linjer.append("    for armen (r = %s). Sjå snitt B-B." % tal(p.sw_r))
        a_br = glob(-3.8, -0.35, p.sw_hol_z)
        SB.merknad(SB.P(a_br), (331, 119), ["Brakett, 2 spor M2 (merknad 7)"], h=2.2, side=1)
    with valfri("T03 knusribber"):
        z_r = (p.z_toppdekk_0 + p.toppdekk_z1) / 2 - 0.5
        ut0 = 40.0 + gjennom(s, (40.0, 0.0, z_r), (46.0, 0.0, z_r))[-1][1]
        ut30 = 40.0 + gjennom(s, (40.0 * math.cos(30 * DEG), 40.0 * math.sin(30 * DEG), z_r),
                              (46.0 * math.cos(30 * DEG), 46.0 * math.sin(30 * DEG), z_r))[-1][1]
        rr = ut0 - 0.02
        zr = gjennom(s, (rr, 0.0, p.z_toppdekk_0 - 3.0), (rr, 0.0, p.toppdekk_z1 + 1.0))
        z_r0, z_r1 = p.z_toppdekk_0 - 3.0 + zr[-1][0], p.z_toppdekk_0 - 3.0 + zr[-1][1]
        sjekk["T03_knusribber"] = {"r_ut_ved_0": round(ut0, 4), "r_ut_ved_30": round(ut30, 4), "z_ved_r": [round(z_r0, 3), round(z_r1, 3)]}
        b_rib = 2 * p.r_mi * math.radians(math.degrees(0.75 / p.r_mi))
        linjer.append("8. %d knusribber ved %s°: %s breie, ut til %s%s (r = %s), full høgd z %s..%s (%s..%s over underkant)," % (
            p.knusribber_n, "/".join(tal(i * 360.0 / p.knusribber_n) for i in range(p.knusribber_n)), tal(b_rib),
            DIA, tal(2 * ut0), tal(ut0), tal(p.z_toppdekk_0), tal(p.toppdekk_z1 - 1.0),
            tal(p.z_toppdekk_0 - zb), tal(p.toppdekk_z1 - 1.0 - zb)))
        linjer.append("    fasa inn til %s%s øvst. Ribbene blir knuste mot boret i mantelen." % (DIA, tal(2 * p.toppdekk_r)))
    linjer.append("9. Funksjonspassingar: tapp %s%s %s mot boret %s%s %s i fotringen (05b); toppdekk %s%s %s" % (
        DIA, tal(2 * p.tapp_ro), tol("tapp"), DIA, tal(2 * p.bor_r), tol("bor"), DIA, tal(2 * p.toppdekk_r), tol("toppdekk")))
    linjer.append("    mot mantelen %s%s %s (04). Minste klaring = klaringa i CAD." % (DIA, tal(2 * p.r_mi), tol("mantel")))
    A.tekstblokk((190, 150), linjer, h=2.3, feit_forste=True)
    return A


def _spormaal_tekst(s, p):
    a = p.sw[0][0]
    c, si = math.cos(a * DEG), math.sin(a * DEG)
    z = p.toppdekk_z1 - 0.5
    cx, cy = p.sw_r * c, p.sw_r * si
    rad = holrom(s, (cx - c * 8, cy - si * 8, z), (cx + c * 8, cy + si * 8, z))
    tan = holrom(s, (cx + si * 10, cy - c * 10, z), (cx - si * 10, cy + c * 10, z))
    b = max((q[1] - q[0] for q in rad), default=float("nan"))
    l = max((q[1] - q[0] for q in tan), default=float("nan"))
    return ["gjennomgåande %s (radielt) x %s (målt)" % (tal(b), tal(l))]


# ============================================================================ T04 mantel
SAUM_MANTEL = 210.0


def ark_T04(D, p, sjekk):
    _mat, ov, _ = SERIE["04_mantel"]
    A = Ark("T04", "Mantel", "04", "Røyr EN AW-6060 T66, %s x %s (EN 755-8)" % (tal(p.mantel_d), tal(p.mantel_t)), ov,
            "1:2 (snitt 1:1, detaljar 5:1)")
    s = D["04_mantel"]
    k = 0.5
    F = Vis(A, (1, 0, 0), (0, 1, 0), k, (0, 0, p.z_mantel_0), (85, 168), namn="F")
    F.liner(hlr([s], (1, 0, 0), (0, 1, 0), 0.03))
    F.senterlinje((0, 0, p.z_mantel_0), (0, 0, p.z_mantel_1))
    L_tot = p.z_mantel_1 - p.z_mantel_0
    xl = F.P((0, -p.r_mo, 0))[0]
    F.maal((0, -p.r_mo, p.z_mantel_0), (0, -p.r_mo, p.z_mantel_1), "v", xl - 24, tal(L_tot), L_tot)
    F.maal((0, -p.r_mo, p.z_mantel_0), (0, -p.r_mo, p.z_spalte_0), "v", xl - 10, tal(p.z_spalte_0 - p.z_mantel_0), p.z_spalte_0 - p.z_mantel_0)
    F.maal((0, -p.r_mo, p.z_spalte_0), (0, -p.r_mo, p.z_spalte_1), "v", xl - 10, tal(p.spalte_l), p.spalte_l)
    F.maal((0, -p.r_mo, p.z_spalte_1), (0, -p.r_mo, p.z_mantel_1), "v", xl - 10, tal(p.spalte_topp), p.spalte_topp)
    F.maal((0, -p.r_mo, p.z_mantel_1), (0, p.r_mo, p.z_mantel_1), "h", F.P((0, 0, p.z_mantel_1))[1] - 8, DIA + tal(p.mantel_d), p.mantel_d)
    zc = p.z_spalte_0 + 0.3 * p.spalte_l
    snittlinje(F, (0, -p.r_mo - 3, zc), (0, p.r_mo + 3, zc), "B", (0, 1))
    F.tittel("FRAMANFRÅ", under=F.P((0, 0, p.z_mantel_0))[1], dy=9)
    fl = utbrett(s, p.r_mo - 0.02, SAUM_MANTEL, r_skala=p.r_mo)
    reg = region(fl)
    Lu = 2 * math.pi * p.r_mo
    U = Vis(A, None, None, k, (0.0, p.z_mantel_0), (128, 168), namn="U")
    flat_teikn(A, U, fl)
    rekt = sbox(0.0, p.z_mantel_0, Lu, p.z_mantel_1)
    utsp = rekt.difference(reg)
    utsp = [q for q in (utsp.geoms if hasattr(utsp, "geoms") else [utsp]) if q.area > 0.5]

    def az(sx):
        a = SAUM_MANTEL + math.degrees(sx / p.r_mo)
        return (a + 180.0) % 360.0 - 180.0
    spalter = sorted([q for q in utsp if q.bounds[3] - q.bounds[1] > 50], key=lambda q: q.centroid.x)
    baj = sorted([q for q in utsp if q.bounds[3] - q.bounds[1] <= 50], key=lambda q: q.centroid.x)
    ytop = U.Q(0, p.z_mantel_1)[1]
    for i, q in enumerate(spalter):
        cx = q.centroid.x
        U.senterlinje((cx, q.bounds[1]), (cx, q.bounds[3]), 2.0)
        pt = U.Q(cx, p.z_mantel_1)
        A.tekst((pt[0] + 0.8, ytop - 2), tal(az(cx), 3) + "°", 2.0, anker="start", rot=-90)
    sjekk["T04_spalter"] = [{"asimut": round(az(q.centroid.x), 4), "z0": round(q.bounds[1], 3), "z1": round(q.bounds[3], 3),
                             "breidd_utbretta": round(q.bounds[2] - q.bounds[0], 4)} for q in spalter]
    with valfri("T04 spaltedeling"):
        a0, a1 = spalter[2].centroid.x, spalter[3].centroid.x
        U.maal((a0, p.z_spalte_0), (a1, p.z_spalte_0), "h", U.Q(0, p.z_spalte_0)[1] + 9,
               tal(a1 - a0) + " (" + tal(math.degrees((a1 - a0) / p.r_mo), 3) + "°)", a1 - a0, tekst_ut=True)
    U.maal((0.0, p.z_mantel_0), (Lu, p.z_mantel_0), "h", U.Q(0, p.z_mantel_0)[1] + 11, tal(Lu) + " = π x " + tal(p.mantel_d), Lu)
    # L-spora er merkte med knastposisjonen i låst stilling (= baj_vinklar); sporet går frå knast − (vri + halv)
    # til knast + halv. halv = vinkelen frå knastsenteret til høgre sporkant, målt på flatmønsteret.
    halv_L = math.degrees(p.baj_knast_b / 2.0 / p.r_mi) + 0.5

    def knast_av(q):
        return min(p.baj_vinklar, key=lambda th: abs(((az(q.bounds[2]) - halv_L) - th + 180.0) % 360.0 - 180.0))
    for q in baj:
        pt = U.Q((q.bounds[0] + q.bounds[2]) / 2, q.bounds[3])
        A.tekst((pt[0], pt[1] - 4.5), "L-spor, knast %s°" % tal(knast_av(q)), 2.0)
    s0 = ((0.0 - SAUM_MANTEL) % 360.0) * DEG * p.r_mo
    pt = U.Q(s0, p.z_mantel_1)
    A.linje((pt[0], pt[1] - 14), (pt[0], pt[1] - 16.5), "t")
    A.tekst((pt[0], pt[1] - 18), "0° (framme)", 2.2)
    for sx, ank, dx in ((0.0, "start", 1.0), (Lu, "end", -1.0)):
        pt = U.Q(sx, p.z_mantel_0)
        A.tekst((pt[0] + dx, pt[1] + 4.5), "saum %s°" % tal(az(0.0)), 2.0, anker=ank)
    U.tittel("UTBRETTA YTTERFLATE (r = %s, sett utanfrå)" % tal(p.r_mo), under=U.Q(0, p.z_mantel_0)[1] + 11, dy=9)
    oB, nB, xB = (0, 0, zc), (0, 0, 1), (0, 1, 0)
    snB = snitt({"04_mantel": s}, oB, nB, xB, 0.02)
    SB = Vis(A, nB, xB, 1.0, (0, 0, zc), (348, 70), namn="SB")
    SB.skravur(snB["polys"], {"04_mantel": (45, 1.2)}, tynn=0.4)
    SB.liner(snB["liner"])
    SB.senterkryss((0, 0, zc), p.r_mo + 5)
    for a in p.vindauge_vinklar:
        SB.senterlinje(((p.r_mi - 6) * math.cos(a * DEG), (p.r_mi - 6) * math.sin(a * DEG), zc),
                       ((p.r_mo + 4) * math.cos(a * DEG), (p.r_mo + 4) * math.sin(a * DEG), zc), 0.0)
    va = p.vindauge_vinklar
    with valfri("T04 vinklar"):
        SB.vinkelmaal((0, 0), p.r_mo + 6, va[2], va[3], zc, tal(p.deling, 3) + "°", p.deling, r_ref=p.r_mo,
                      tekst_r=p.r_mo + 10.3)
        SB.vinkelmaal((0, 0), p.r_mo + 17, va[0], va[-1], zc, tal(va[-1] - va[0], 3) + "°", va[-1] - va[0], r_ref=p.r_mo,
                      tekst_r=p.r_mo + 21)
        pass
    SB.tittel("SNITT B-B (1:1)", under=SB.P((p.r_mo + 24, 0, zc))[1], dy=6)
    with valfri("T04 detalj G"):
        q = min(baj, key=lambda qq: abs(az(qq.bounds[0]) - p.baj_vinklar[0]))
        b0, b1 = q.bounds[0], q.bounds[2]
        cG = ((b0 + b1) / 2, p.z_mantel_0 + 3.0)
        G = Vis(A, None, None, 5.0, cG, (92, 224), klipp=sbox(b0 - 3, p.z_mantel_0 - 1.5, b1 + 3, p.z_mantel_0 + 8.5), namn="G")
        G.liner(flat_liner(fl))
        A.pl([G.Q(b0 - 3, p.z_mantel_0 - 1.5), G.Q(b1 + 3, p.z_mantel_0 - 1.5), G.Q(b1 + 3, p.z_mantel_0 + 8.5),
              G.Q(b0 - 3, p.z_mantel_0 + 8.5)], "t", lukk=True)
        ixs = list(q.exterior.coords)
        z_top = q.bounds[3]
        zz = sorted(set(round(c_[1], 4) for c_ in ixs if c_[1] > p.z_mantel_0 + 0.01))
        z_lo = zz[0]
        G.maal((b0, z_top), (b1, z_top), "h", G.Q(0, z_top)[1] - 8,
               tal(b1 - b0) + " (" + tal(math.degrees((b1 - b0) / p.r_mo), 2) + "°)", b1 - b0)
        G.maal((b1, p.z_mantel_0), (b1, z_top), "v", G.Q(b1 + 3, 0)[0] + 8, tal(z_top - p.z_mantel_0), z_top - p.z_mantel_0)
        botn = [c_[0] for c_ in ixs if abs(c_[1] - p.z_mantel_0) < 1e-3]
        G.maal((min(botn), p.z_mantel_0), (max(botn), p.z_mantel_0), "h", G.Q(0, p.z_mantel_0)[1] + 15,
               tal(max(botn) - min(botn)), max(botn) - min(botn))
        G.maal((b0, p.z_mantel_0), (b0, z_lo), "v", G.Q(b0 - 3, 0)[0] - 8, tal(z_lo - p.z_mantel_0), z_lo - p.z_mantel_0)
        # nabben på underkanten av den vassrette delen: hjørna på flatmønsteret like over z_lo
        z_nb = zz[1]
        nx = sorted(c_[0] for c_ in ixs if abs(c_[1] - z_nb) < 1e-3)
        n0, n1 = nx[0], nx[-1]
        y_in = G.Q(0, z_nb)[1]
        G.maal((n0, z_nb), (n1, z_nb), "h", y_in - 4.0,
               tal(n1 - n0) + " (" + tal(math.degrees((n1 - n0) / p.r_mo), 1) + "°)", n1 - n0, tekst_ut=True)
        G.maal((n1, z_nb), (b1, z_nb), "h", y_in - 10.0,
               tal(b1 - n1) + " (" + tal(math.degrees((b1 - n1) / p.r_mo), 2) + "°)", b1 - n1, tekst_ut=False)
        G.maal((n0, z_lo), (n0, z_nb), "v", G.Q(n0, 0)[0] - 5.0, tal(z_nb - z_lo), z_nb - z_lo)
        A.tekst((92, 268), "G (5:1)  L-spor for bajonett, %d stk, knast i låst stilling ved %s°" % (
            len(baj), "/".join(tal(a) for a in p.baj_vinklar)), 3.0, feit=True)
        A.tekst((92, 273), "Sporet går frå knast %s %s° til knast + %s°; nabben (%s høg) krev «trykk ned og vri»" % (
            MI, tal(p.baj_vri + halv_L, 2), tal(halv_L, 2), tal(z_nb - z_lo)), 2.2)
        sjekk["T04_nabb"] = {"breidd": round(n1 - n0, 4), "høgd": round(z_nb - z_lo, 4), "til_høgre_kant": round(b1 - n1, 4),
                             "z_lag_over_underkant": round(z_lo - p.z_mantel_0, 4)}
        uq = U.Q(*cG)
        A.pl([U.Q(b0 - 3, p.z_mantel_0 - 1.5), U.Q(b1 + 3, p.z_mantel_0 - 1.5), U.Q(b1 + 3, p.z_mantel_0 + 8.5),
              U.Q(b0 - 3, p.z_mantel_0 + 8.5)], "t", lukk=True)
        A.tekst((U.Q(b1 + 3, 0)[0] + 3, U.Q(0, p.z_mantel_0 + 8.5)[1] + 1), "G", 3.5, anker="start", feit=True)
        sjekk["T04_L_spor"] = [{"asimut_start": round(az(qq.bounds[0]), 3), "breidd": round(qq.bounds[2] - qq.bounds[0], 3),
                                "z_topp": round(qq.bounds[3] - p.z_mantel_0, 3)} for qq in baj]
    with valfri("T04 detalj H"):
        q = spalter[3]
        cH = (q.centroid.x, q.bounds[3] - 2.0)
        H = Vis(A, None, None, 5.0, cH, (362, 188), klipp=Point(*cH).buffer(4.5, 128), namn="H")
        H.liner(flat_liner(fl))
        A.sirkel((362, 188), 4.5 * 5, "t")
        bw = q.bounds[2] - q.bounds[0]
        H.maal((q.bounds[0], cH[1] - 1.5), (q.bounds[2], cH[1] - 1.5), "h", H.Q(0, cH[1])[1] + 15, tal(bw), bw)
        A.tekst((362, 188 + 22.5 + 8), "H (5:1)  spalteende", 3.0, feit=True)
        A.tekst((362, 188 + 22.5 + 13), "Skjeremål før pulverlakk; ferdig spalte 3,2", 2.2)
        uq = U.Q(*cH)
        A.sirkel(uq, 4.5 * k, "t")
        A.tekst((uq[0] + 4.5, uq[1] - 2), "H", 3.5, feit=True)
    A.tekstblokk((172, 202), [
        "Merknader",
        "1. Røyr EN AW-6060 T66 %s x %s etter EN 755-8, kappa til %s." % (tal(p.mantel_d), tal(p.mantel_t), tal(L_tot)),
        "2. Røyrlaser: berre radielle gjennomskjeringar. Leverandøren får",
        "    cad/fyr_04_mantel.step; utbretta vising og DXF er dokumentasjon.",
        "3. Skjeremål før pulverlakk; ferdig spalte 3,2.",
        "4. Pulverlakk RAL 3005 inn- og utvendig, fin struktur, matt.",
        "5. Spaltedeling %s° = éin klikk på hylsa. Asimut 0° = framme." % tal(p.deling, 3),
        "6. Funksjonsflate: innerdiameter %s%s %s i øvste %s mm (glideringen 10) og på %s..%s over" % (
            DIA, tal(2 * p.r_mi), tol("mantel"), tal(p.glide_h + p.glide_under_kant + 1.0),
            tal(p.z_toppdekk_0 - p.z_mantel_0), tal(p.toppdekk_z1 - p.z_mantel_0)),
        "    underkant (toppdekket på 03). Mål røyret; kalibrer innvendig om leveransen ikkje held dette.",
    ], h=2.3, feit_forste=True)
    dxf_mantel(reg, p, Lu)
    return A


# ============================================================================ T05 hylse
SAUM_HYLSE = float(getattr(g.FyrParams(), "hylse_saum", 180.0))   # stumpskøyten, asimut i hylsesystemet


def hylse_flat(D, p):
    s = D["05_hylse"]
    r_n = (p.r_ho + p.r_hi) / 2.0
    fl = utbrett(s, r_n, SAUM_HYLSE, n_kurve=72)
    reg = region(fl)
    L = 2 * math.pi * r_n
    rekt = sbox(0.0, p.z_hylse_0, L, p.z_hylse_1)
    utsp = rekt.difference(reg)
    utsp = sorted([q for q in (utsp.geoms if hasattr(utsp, "geoms") else [utsp]) if q.area > 0.05], key=lambda q: q.centroid.x)
    return s, r_n, fl, reg, L, utsp


def utsp_type(q):
    bw, hh = q.bounds[2] - q.bounds[0], q.bounds[3] - q.bounds[1]
    return "port" if bw > 20 else ("krone" if hh > 15 else "skruehol")


def ark_T05(D, p, sjekk):
    _mat, ov, _ = SERIE["05_hylse"]
    A = Ark("T05", "Hylse, flatmønster", "05", "CuZn37 (CW508L), plate %s" % tal(p.hylse_t), ov, "1:2 (detaljar 5:1)")
    s, r_n, fl, reg, L, utsp = hylse_flat(D, p)
    k = 0.5
    F = Vis(A, (1, 0, 0), (0, 1, 0), k, (0, 0, p.z_hylse_0), (60, 160), namn="F")
    F.liner(hlr([s], (1, 0, 0), (0, 1, 0), 0.03))
    F.senterlinje((0, 0, p.z_hylse_0), (0, 0, p.z_hylse_1))
    F.maal((0, -p.r_ho, p.z_hylse_1), (0, p.r_ho, p.z_hylse_1), "h", F.P((0, 0, p.z_hylse_1))[1] - 8, DIA + tal(2 * p.r_ho), 2 * p.r_ho,
           avvik=TOL["hylse"])
    F.maal((0, -p.r_ho, p.z_hylse_0), (0, -p.r_ho, p.z_hylse_1), "v", F.P((0, -p.r_ho, 0))[0] - 8,
           tal(p.z_hylse_1 - p.z_hylse_0), p.z_hylse_1 - p.z_hylse_0)
    F.tittel("VALSA, FRAMANFRÅ", under=F.P((0, 0, p.z_hylse_0))[1], dy=9)
    A.tekst((F.px, F.P((0, 0, p.z_hylse_0))[1] + 14), "vegg %s" % tal(p.hylse_t), 2.5)
    U = Vis(A, None, None, k, (0.0, p.z_hylse_0), (100, 160), namn="U")
    flat_teikn(A, U, fl)
    U.maal((0.0, p.z_hylse_0), (L, p.z_hylse_0), "h", U.Q(0, p.z_hylse_0)[1] + 9,
           tal(L) + " = π x (" + tal(2 * p.r_ho) + " − " + tal(p.hylse_t) + ")", L)
    U.maal((L, p.z_hylse_0), (L, p.z_hylse_1), "v", U.Q(L, 0)[0] + 8, tal(p.z_hylse_1 - p.z_hylse_0), p.z_hylse_1 - p.z_hylse_0)
    sx_front = (0.0 - SAUM_HYLSE) % 360.0 * DEG * r_n
    U.senterlinje((sx_front, p.z_hylse_0 - 3), (sx_front, p.z_hylse_1 + 3), 2.0)
    pt = U.Q(sx_front, p.z_hylse_1 + 3)
    A.tekst((pt[0], pt[1] - 6), "0° (framme)", 2.2)
    for sx, ank, dx in ((0.0, "start", 1.0), (L, "end", -1.0)):
        pt = U.Q(sx, p.z_hylse_0)
        A.tekst((pt[0] + dx, pt[1] + 4.2), "skøyt %s°" % tal(SAUM_HYLSE), 2.0, anker=ank)

    def az(sx):
        a = SAUM_HYLSE + math.degrees(sx / r_n)
        return (a + 180.0) % 360.0 - 180.0

    rader = [("Nr.", "Type", "Asimut °", "x senter", "Breidd", "z0", "z1")]
    for i, q in enumerate(utsp):
        bw = q.bounds[2] - q.bounds[0]
        cx = q.centroid.x
        rader.append(("U%d" % (i + 1), utsp_type(q), tal(az(cx), 3), tal(cx), tal(bw), tal(q.bounds[1] - p.z_hylse_0), tal(q.bounds[3] - p.z_hylse_0)))
        if utsp_type(q) == "krone":
            # kronespaltene står 6 under overkanten: nummera over kanten, i to rader
            pt = U.Q(cx, p.z_hylse_1)
            A.tekst((pt[0], pt[1] - 1.2 - (i % 2) * 2.4), "U%d" % (i + 1), 1.6)
        else:
            # hol og port: nummeret til høgre for utsparinga (klar av senterlinjene)
            pt = U.Q(q.bounds[2], q.bounds[3])
            A.tekst((pt[0] + 0.8, pt[1] + 1.6), "U%d" % (i + 1), 1.6, anker="start")
    A.tekst((272, 17.5), "Utsparingar på nøytralfiberen (x frå venstre kant, z frå underkant)", 2.1, anker="start")
    A.tabell(272, 19.5, [11, 17, 18, 18, 16, 14, 14], rader, h=2.0, rh=3.9)
    sjekk["T05_utsparingar"] = [r for r in rader[1:]]
    yA = U.Q(0, p.z_hylse_0)[1] + 25
    xa = U.Q(0, 0)[0]
    A.linje((xa, yA), (xa + 30, yA), "t")
    A.pil((xa + 30, yA), (1, 0), 3.0, 0.9)
    A.tekst((xa + 33, yA + 1.0), "Valseretning (rundvalsing om z) og børsteretning: langs x", 2.2, anker="start")
    A.tekst((xa, yA + 5.5), "Fiberretninga i plata (valseretning frå verket) langs x", 2.2, anker="start")
    U.tittel("FLATMØNSTER, sett frå utsida (børsta side)", under=yA + 5.5, dy=7)
    krone = sorted([q for q in utsp if utsp_type(q) == "krone"], key=lambda qq: qq.centroid.x)
    hol = [q for q in utsp if utsp_type(q) == "skruehol"]
    with valfri("T05 detalj K"):
        q, q2 = krone[0], krone[1]
        cK = ((q.centroid.x + q2.centroid.x) / 2, q.bounds[3] - 2.0)
        K = Vis(A, None, None, 5.0, cK, (298, 178), klipp=Point(*cK).buffer(6.5, 128), namn="K")
        K.liner(flat_liner(fl))
        A.sirkel((298, 178), 6.5 * 5, "t")
        bw = q.bounds[2] - q.bounds[0]
        K.maal((q.bounds[0], cK[1] - 2), (q.bounds[2], cK[1] - 2), "h", K.Q(0, cK[1])[1] + 24, tal(bw), bw)
        dx = q2.centroid.x - q.centroid.x
        K.maal((q.centroid.x, q.bounds[3]), (q2.centroid.x, q2.bounds[3]), "h", K.Q(0, q.bounds[3])[1] - 10,
               tal(dx) + " (" + tal(math.degrees(dx / r_n), 3) + "°)", dx, tekst_ut=False)
        A.tekst((298, 178 + 32.5 + 7), "K (5:1)  kronespalte, stadion R %s" % tal(bw / 2), 3.0, feit=True)
        uq = U.Q(*cK)
        A.sirkel(uq, 6.5 * k, "t")
        A.tekst((U.Q(0, 0)[0] - 1.5, uq[1] + 1.75), "K", 3.5, anker="end", feit=True)   # utanfor platekanten
    with valfri("T05 detalj S"):
        q = hol[0]
        cS = (q.centroid.x, q.centroid.y)
        SN = Vis(A, None, None, 5.0, cS, (370, 178), klipp=Point(*cS).buffer(5.0, 128), namn="SN")
        SN.liner(flat_liner(fl))
        A.sirkel((370, 178), 5.0 * 5, "t")
        bw = q.bounds[2] - q.bounds[0]
        hh = q.bounds[3] - q.bounds[1]
        SN.maal((q.bounds[0], q.centroid.y), (q.bounds[2], q.centroid.y), "h", SN.Q(0, q.bounds[1])[1] + 9, tal(bw), bw)
        SN.maal((q.bounds[2], q.bounds[1]), (q.bounds[2], q.bounds[3]), "v", SN.Q(q.bounds[2], 0)[0] + 8, tal(hh), hh)
        A.tekst((370, 178 + 25 + 7), "S (5:1)  hol for stoppskrue", 3.0, feit=True)
        A.tekst((370, 178 + 25 + 12), "rundt %s%s i flatmønsteret og etter valsing" % (DIA, tal(bw)), 2.0)
        sjekk["T05_stopphol"] = {"breidd": round(bw, 4), "høgd": round(hh, 4), "rundt": bool(abs(bw - hh) < 0.01)}
        uq = U.Q(*cS)
        A.sirkel(uq, 5.0 * k, "t")
        A.tekst((U.Q(0, 0)[0] - 1.5, uq[1] + 1.75), "S", 3.5, anker="end", feit=True)   # utanfor platekanten
    A.tekstblokk((26, 224), [
        "Merknader",
        "1. Laserskoren av CuZn37 %s mm, valsa til røyr, stumpskøyt på %s° (bak, mellom kronegruppene) på heil steg."
        % (tal(p.hylse_t), tal(SAUM_HYLSE)),
        "2. Flatlengd på nøytralfiberen: L = π x (YD − t) = π x (%s − %s) = %s (K = 0,5, r = %s)." % (
            tal(2 * p.r_ho), tal(p.hylse_t), tal(L), tal(r_n)),
        "3. Utsparingane er plasserte med x = asimut x r_nøytral; kantane blir radielle etter valsing.",
        "4. Børsta rundt (langs x) etter valsing, deretter klarlakk. DXF: produksjon/fyr_05_hylse_flatmonster.dxf.",
        "5. Funksjonsmål: innerdiameter %s%s %s etter valsing og lodding (kalibrert på dor), altså ytterdiameter" % (
            DIA, tal(2 * p.r_hi), tol("hylse")),
        "    %s%s %s. Fotringen %s%s %s går inn; glideringen (montert %s%s..%s) styrer utsida." % (
            DIA, tal(2 * p.r_ho), tol("hylse"), DIA, tal(2 * (p.r_hi - 0.05)), tol("fotring"),
            DIA, tal(glide_montert_id(p)[0]), tal(glide_montert_id(p)[1])),
    ], h=2.3, feit_forste=True)
    dxf_hylse(reg, p, r_n, L, utsp)
    return A


# ============================================================================ T05b hylsefot (fotring)
def ark_T05b(D, p, sjekk):
    _mat, ov, _ = SERIE["05b_hylsefot"]
    A = Ark("T05b", "Hylsefot (fotring)", "05b", "POM-C", ov, "1:1 (detaljar 5:1, 10:1)")
    s = D["05b_hylsefot"]
    bbf = s.BoundingBox()
    z0, z1 = bbf.zmin, bbf.zmax
    cyl = sylinderflater(s)
    ax_c = [c for c in cyl if abs(c["dir"][2]) > 0.99 and np.hypot(*c["loc"][:2]) < 0.01]
    r_ut = max(c["r"] for c in ax_c)
    r_bor = min(c["r"] for c in ax_c)
    st = {"05b_hylsefot": (45, 1.5)}
    o, n, x = akse_snitt(0.0)
    sn = snitt({"05b_hylsefot": s}, o, n, x, 0.01)
    S = Vis(A, n, x, 1.0, (0, 0, z0), (90, 50), namn="S")
    S.skravur(sn["polys"], st)
    S.liner(sn["liner"])
    S.senterlinje((0, 0, z0), (0, 0, z1))
    yb = S.P((0, 0, z0))[1]
    S.maal((-r_ut, 0, z0), (r_ut, 0, z0), "h", yb + 8, DIA + tal(2 * r_ut), 2 * r_ut, avvik=TOL["fotring"])
    S.maal((-r_bor, 0, z1), (r_bor, 0, z1), "h", S.P((0, 0, z1))[1] - 8, DIA + tal(2 * r_bor), 2 * r_bor, avvik=TOL["bor"])
    S.maal((-r_ut, 0, z0), (-r_ut, 0, z1), "v", S.P((-r_ut, 0, 0))[0] - 16, tal(z1 - z0), z1 - z0)
    S.tittel("SNITT A-A", under=yb + 8, dy=13)
    with valfri("T05b detalj X"):
        rad = [c for c in cyl if abs(c["dir"][2]) < 0.01 and abs(c["loc"][2] - p.stopp_z) < 0.01]
        r_sk = max(c["r"] for c in rad)
        r_m3 = min(c["r"] for c in rad)
        tr = gjennom(s, (r_bor - 1.0, 0.37 * 0, p.stopp_z + (r_m3 + r_sk) / 2), (r_ut + 1.0, 0.0, p.stopp_z + (r_m3 + r_sk) / 2))
        r_steg = (r_bor - 1.0) + tr[-1][1] if tr else float("nan")
        cX = ((r_bor + r_ut) / 2, 0.0, p.stopp_z)
        X5 = detalj(A, S, sn, cX, 4.5, "X", 5.0, (200, 52), st, lab_vinkel=-50.0)
        X5.maal((r_steg, 0, p.stopp_z + r_sk), (r_ut, 0, p.stopp_z + r_sk), "h", X5.P((0, 0, p.stopp_z + r_sk))[1] - 12,
                tal(r_ut - r_steg), r_ut - r_steg)
        X5.maal((r_ut, 0, z0), (r_ut, 0, p.stopp_z), "v", X5.P((r_ut, 0, 0))[0] + 8, tal(p.stopp_z - z0), p.stopp_z - z0)
        A.tekstblokk((232, 32), [
            "3 x M3 (kjernehol %s2,5) radielt ved %s°," % (DIA, "/".join(tal(a) for a in p.stopp_vinklar)),
            "senter %s over underkant, gjennom til boret." % tal(p.stopp_z - z0),
            "Forsenking %s%s for hovudet på stoppskrua" % (DIA, tal(2 * r_sk)),
            "(%s), botn på r = %s." % (stykk("05c_stoppskruar")[3], tal(r_steg)),
        ], h=2.2)
    B = Vis(A, (0, 0, -1), (0, 1, 0), 1.0, (0, 0, 0), (90, 148), namn="B")
    B.liner(hlr([s], (0, 0, -1), (0, 1, 0), 0.02))
    B.senterkryss((0, 0, 0), r_ut + 4)
    # snittlinje A-A (planet y = 0,37 gjennom aksen) og C-C (sylinderflata r = sw_r) i SETT NEDANFRÅ
    snittlinje(B, (-r_ut - 3, 0.37, z0), (r_ut + 3, 0.37, z0), "A", (1, 0))
    B.sirkel_c((0, 0, z0), p.sw_r)
    for a_c, sg in ((90.0, 1), (270.0, -1)):
        q_ = np.array(B.P((p.sw_r * math.cos(a_c * DEG), p.sw_r * math.sin(a_c * DEG), z0)))
        q2 = np.array(B.P(((p.sw_r + 12.0) * math.cos(a_c * DEG), (p.sw_r + 12.0) * math.sin(a_c * DEG), z0)))
        A.linje(q2, q_ + (q2 - q_) / np.linalg.norm(q2 - q_) * 3.0, "t")
        A.pil(q_ + (q2 - q_) / np.linalg.norm(q2 - q_) * 0.6, q_ - q2, 3.0, 0.9)
        A.tekst((q2[0] + sg * 3.0, q2[1] - 1.5), "C", 5.0, feit=True)
    with valfri("T05b kamspor"):
        for i, ((a0, a1), (a_sw, ter)) in enumerate(zip(g.kam_spor(p), p.sw)):
            am = (a0 + a1) / 2
            rm = (p.kam_r0 + p.kam_r1) / 2
            B.merknad(B.P((rm * math.cos(am * DEG), rm * math.sin(am * DEG), z0)),
                      B.P(((r_ut + 12) * math.cos(am * DEG), (r_ut + 12) * math.sin(am * DEG), z0)),
                      ["SW%d: %s°..%s°" % (i + 1, tal((a0 - p.kam_rampe) % 360, 1), tal((a1 + p.kam_rampe) % 360, 1))], h=2.2)
    B.tittel("SETT NEDANFRÅ (kamspor)", dy=18)
    with valfri("T05b snitt D-D"):
        zD = (p.klikk_z0 + z1) / 2
        oD, nD, xD = (0, 0, zD), (0, 0, 1), (0, 1, 0)
        snD = snitt({"05b_hylsefot": s}, oD, nD, xD, 0.01)
        SD = Vis(A, nD, xD, 1.0, (0, 0, zD), (210, 148), namn="SD")
        SD.skravur(snD["polys"], st, tynn=0.35)
        SD.liner(snD["liner"])
        SD.senterkryss((0, 0, zD), r_ut + 4)
        snittlinje(S, (-r_ut - 3, 0, zD), (r_ut + 3, 0, zD), "D", (0, 1))
        rv_ = r_bor + min(0.3, p.klikk_djup / 2)
        tom = [not inni(s, (rv_ * math.cos(t * DEG), rv_ * math.sin(t * DEG), zD)) for t in np.arange(0.0, 360.0, 0.25)]
        nk = sum(1 for i in range(len(tom)) if tom[i] and not tom[i - 1])
        # spora ligg på klikk_vinklar + k x deling (ikkje på tungevinkelen): finn senteret av kvart spor på B-rep
        sentra = []
        n_t = len(tom)
        for i in range(n_t):
            if tom[i] and not tom[i - 1]:
                j = i
                while tom[(j + 1) % n_t]:
                    j += 1
                sentra.append(((i + j) / 2.0 * 0.25) % 360.0)
        kv = list(p.klikk_vinklar)
        n_per = int(round(p.vandring / p.deling)) + 1
        venta = sorted((a + k * p.deling) % 360.0 for a in kv for k in range(n_per))
        avvik_s = [min(abs((c_ - v_ + 180.0) % 360.0 - 180.0) for c_ in sentra) for v_ in venta]
        sjekk["T05b_klikkspor"] = {"tal_brep": nk, "tal_param": len(venta), "første_i_gruppe": [round(a % 360.0, 3) for a in kv],
                                   "største_avvik_senter_grader": round(max(avvik_s), 3) if avvik_s else None,
                                   "ok": bool(nk == len(venta) and avvik_s and max(avvik_s) < 0.2)}
        a_k0 = kv[0]
        SD.vinkelmaal((0, 0), r_ut + 9, a_k0, a_k0 + p.deling, zD, tal(p.deling, 3) + "°", p.deling,
                      r_ref=r_bor, tekst_r=r_ut + 17)
        SD.tittel("SNITT D-D (z = %s)" % tal(zD - z0))
        a_v = a_k0 + p.deling * 4
        cV = (r_bor * math.cos(a_v * DEG), r_bor * math.sin(a_v * DEG), zD)
        detalj(A, SD, snD, cV, 1.6, "V", 10.0, (300, 148), st, lab_vinkel=180.0)
        A.tekstblokk((280, 185), [
            "%d V-spor 90° i boret (talde på B-rep), djup %s, deling %s°," % (nk, tal(p.klikk_djup), tal(p.deling, 3)),
            "%d grupper à %d; første spor i kvar gruppe ved %s°" % (len(kv), n_per, "/".join(tal(a % 360.0, 1) for a in kv)),
            "(tungene står ved %s°; kula sit %s° før tunga)." % ("/".join(tal(a) for a in p.tunge_vinklar),
                                                                tal(p.tunge_vinklar[0] - kv[0], 1)),
            "Frå z = %s over underkant og opp." % tal(p.klikk_z0 - z0),
        ], h=2.2)
    with valfri("T05b utbretta C-C"):
        rC = p.sw_r
        flC = utbrett(s, rC, 0.0)
        regC = region(flC)
        LC = 2 * math.pi * rC
        kC = 0.5                                  # ISO 5455: 1:2
        xC, yC = 60.0, 232.0
        C = Vis(A, None, None, kC, (0.0, z0), (xC, yC), namn="C")
        gp = affine_transform(regC, [kC, 0, 0, -kC, xC, yC + z0 * kC])
        A.skravur(gp, 45, 1.0, tynn=0.3)
        flat_teikn(A, C, flC)
        kam = []
        for i, (a0, a1) in enumerate(g.kam_spor(p)):
            rw = p.kam_rampe
            for a in (a0 - rw, a0, a1, a1 + rw):
                pt = C.Q((a % 360.0) * DEG * rC, z0)
                A.linje((pt[0], pt[1] + 1), (pt[0], pt[1] + 4), "t")
            pt = C.Q(((a0 - rw) % 360.0) * DEG * rC, z0)
            A.tekst((pt[0] - 0.5, pt[1] + 7.0), "SW%d %s°" % (i + 1, tal((a0 - rw) % 360.0, 1)), 2.0, anker="end")
            pt = C.Q(((a1 + rw) % 360.0) * DEG * rC, z0)
            A.tekst((pt[0] + 0.5, pt[1] + 7.0), tal((a1 + rw) % 360.0, 1) + "°", 2.0, anker="start")
            # mål på B-rep: kvar er utsparinga djupast (full djupn) langs bana, og kvar sluttar rampene
            zp = z0 + 0.5 * p.kam_djup

            def ope(a_):
                return not inni(s, (rC * math.cos(a_ * DEG), rC * math.sin(a_ * DEG), zp))
            ang = np.arange(a0 - rw - 3.0, a1 + rw + 3.0, 0.05)
            o_ = [a_ for a_ in ang if ope(a_)]
            kam.append({"SW": i + 1, "ope_på_halv_djupn": [round(o_[0] % 360.0, 2), round(o_[-1] % 360.0, 2)] if o_ else None,
                        "venta_halv_djupn": [round((a0 - rw / 2) % 360.0, 2), round((a1 + rw / 2) % 360.0, 2)]})
        sjekk["T05b_kamspor"] = kam
        C.maal((0.0, z1), (LC, z1), "h", C.Q(0, z1)[1] - 5, "360° = " + tal(LC), LC)
        A.tekst((xC, yC + 11), "UTBRETTA SNITT C-C (1:2), r = %s (brytarbana), sett utanfrå, 0° til venstre" % tal(rC), 3.0,
                anker="start", feit=True)
        A.tekst((xC, yC + 16), "Kamspor: djup %s, r = %s..%s; rampe %s° i båe endar (ned, full djupn, opp). Brytaren slepp i sporet." % (
            tal(p.kam_djup), tal(p.kam_r0), tal(p.kam_r1), tal(p.kam_rampe)), 2.2, anker="start")
        A.tekst((xC, yC + 20), "Vinklane: start på første rampe og slutt på siste. Strekane: rampestart, full djupn, "
                "slutt full djupn, rampeslutt.", 2.2, anker="start")
    A.tekstblokk((330, 62), [
        "Merknader",
        "1. POM-C, sprøytestøypt.",
        "2. Boret %s%s %s går på tappen" % (DIA, tal(2 * r_bor), tol("bor")),
        "    %s%s %s på chassiset (03)." % (DIA, tal(2 * p.tapp_ro), tol("tapp")),
        "3. Ytterflata %s%s %s inne i hylsa" % (DIA, tal(2 * r_ut), tol("fotring")),
        "    %s%s %s (05), låst med 3 stoppskruar." % (DIA, tal(2 * p.r_hi), tol("hylse")),
        "    Minste klaring = klaringa i CAD.",
        "4. I samanstillinga står ringen på",
        "    z %s..%s (stoppskruar på z %s)." % (tal(z0), tal(z1), tal(p.stopp_z)),
    ], h=2.2, feit_forste=True)
    return A


# ============================================================================ T06 lysstav og mastfot
def ark_T06(D, p, sjekk):
    A = Ark("T06", "Lysstav og mastfot", "06, 06d", "06: EN AW-6060; 06d: POM-C (prototype PETG HF)",
            "06: baksida mattsvart; 06d: som fresa", "1:1, 4:1, 2:1")
    stav = D["06_lysstav"]
    fot = form(g.mastfot(p))                       # mastfoten åleine (D har 06d = mastfot + plugg)
    pp = g.FyrParams.prototype()
    fot_p = form(g.mastfot(pp))
    plugg = form(g.trs_plugg(p))
    rader = []

    def mb(V, a, b, orient, at, tekst, verdi, kjelde, brep, tol_=0.01, **kw):
        """Mål på arket + prøve mot B-rep (same krav som T00: papir 0,05, B-rep 0,01)."""
        V.maal(a, b, orient, at, tekst, verdi, **kw)
        papir = A.maallogg[-1][2]
        rader.append({"tekst": tekst, "verdi_frå_FyrParams": round(verdi, 4), "målt_på_papiret": round(papir, 3),
                      "brep_kjelde": kjelde, "brep": None if brep is None else round(brep, 4),
                      "ok": bool(abs(papir - verdi) < 0.05 and brep is not None and abs(brep - verdi) < tol_)})

    # ------------------------------------------------------------------ B-rep: lysstaven
    bs = stav.BoundingBox()
    # staven har inkje hol (lysmodulen er limt): prøv at B-rep er eit reint prisme utan sylinderflater
    hol = sylinderflater(stav)
    L = p.stav_z1 - p.stav_z0
    # ------------------------------------------------------------------ B-rep: mastfoten
    z0f, z1f = p.mastfot_z0, p.mastfot_z1
    bx, ly = p.mastfot_b / 2.0, p.mastfot_l / 2.0
    bf = fot.BoundingBox()

    def lommer(s):
        return max(c["r"] for c in sylinderflater(s) if abs(c["dir"][2]) > 0.99 and np.hypot(*c["loc"][:2]) < 0.01)
    r_l, r_lp = lommer(fot), lommer(fot_p)
    y_pr = (p.stav_b / 2.0 + r_l) / 2.0                         # mellom lomma og sporveggen: golvet staven står på
    iv = gjennom(fot, (0.0, y_pr, z1f + 1.0), (0.0, y_pr, z0f - 1.0))
    z_golv = z1f + 1.0 - iv[0][0]
    x_l = (p.stav_t / 2 + 0.05 + r_l) / 2.0
    iv = gjennom(fot, (x_l, 0.0, z0f - 1.0), (x_l, 0.0, z1f + 1.0))   # framfor sporet, gjennom lomma
    z_lomme = z0f - 1.0 + iv[0][0]
    zm = (z_golv + z1f) / 2.0
    hy = [q for q in holrom(fot, (0.0, -ly - 1.0, zm), (0.0, ly + 1.0, zm))]
    y_s0, y_s1 = -ly - 1.0 + hy[0][0], -ly - 1.0 + hy[0][1]
    hx = [q for q in holrom(fot, (-bx - 1.0, y_pr, zm), (bx + 1.0, y_pr, zm))]
    x_s0, x_s1 = -bx - 1.0 + hx[0][0], -bx - 1.0 + hx[0][1]
    kanal_ned = not gjennom(fot, ((x_s0 + (-p.stav_t / 2 - 0.05)) / 2, 0.0, z0f - 1.0),
                            ((x_s0 + (-p.stav_t / 2 - 0.05)) / 2, 0.0, z1f + 1.0))
    gy = [q for q in holrom(fot, (0.0, -ly - 1.0, z_golv - 0.1), (0.0, ly + 1.0, z_golv - 0.1))]
    y_golv_inn = (gy[0][1] - gy[0][0]) / 2.0 if gy else float("nan")
    d_e = 0.01
    iv = gjennom(fot, (bx - d_e, -ly - 1.0, zm - 8.0), (bx - d_e, ly + 1.0, zm - 8.0))
    fas = (2 * ly - (iv[0][1] - iv[0][0])) / 2.0 + d_e
    pc = plugg.BoundingBox()
    sk = [c for c in sylinderflater(plugg) if abs(c["dir"][2]) > 0.99 and c["z"][1] <= z0f + 0.02]
    r_sk = sk[0]["r"]
    spor_b = p.stav_t + 0.1
    sjekk["T06_mastfot"] = {
        "bbox": [round(bf.xlen, 4), round(bf.ylen, 4), round(bf.zlen, 4)], "z": [round(bf.zmin, 4), round(bf.zmax, 4)],
        "fas": round(fas, 4), "lomme_d_serie": round(2 * r_l, 4), "lomme_d_prototype": round(2 * r_lp, 4),
        "lomme_topp_z": round(z_lomme, 4), "golv_z": round(z_golv, 4), "spor_djupn": round(z1f - z_golv, 4),
        "lomme_djupn_til_golvet": round(z_golv - bf.zmin, 4),
        "spor_y": [round(y_s0, 4), round(y_s1, 4)], "spor_x": [round(x_s0, 4), round(x_s1, 4)],
        "spor_breidd_param": round(spor_b, 4), "kanal_param": p.mastfot_kanal,
        "kanal_ned_i_lomma": bool(kanal_ned), "golv_y": [round(y_golv_inn, 4), round(y_s1, 4)],
        "plugg_under_foten": round(z0f - pc.zmin, 4), "plugg_skaft_d": round(2 * r_sk, 4),
        "ok": bool(abs(2 * r_l - (p.trs_kropp_d + p.mastfot_lomme_klaring)) < 0.01
                   and abs(2 * r_lp - (pp.trs_kropp_d + pp.mastfot_lomme_klaring)) < 0.01
                   and abs(z_golv - p.stav_z0) < 0.01 and z_lomme >= z_golv - 1e-6
                   and abs((x_s1 - x_s0) - (spor_b + p.mastfot_kanal)) < 0.01 and kanal_ned
                   and abs(y_golv_inn - r_l) < 0.01 and abs(fas - 0.5) < 0.01)}
    n_flater = len(stav.Faces())
    sjekk["T06_lysstav"] = {"bbox": [round(bs.xlen, 4), round(bs.ylen, 4), round(bs.zlen, 4)],
                            "z": [round(bs.zmin, 4), round(bs.zmax, 4)], "flater": n_flater,
                            "sylinderflater_(hol)": len(hol),
                            "ok": bool(not hol and n_flater == 6 and abs(bs.xlen - p.stav_t) < 0.01
                                       and abs(bs.ylen - p.stav_b) < 0.01 and abs(bs.zlen - L) < 0.01)}

    # ------------------------------------------------------------------ 06 lysstav, 1:1
    lin_f = hlr([stav], (1, 0, 0), (0, 1, 0), 0.01)
    Fv = Vis(A, (1, 0, 0), (0, 1, 0), 1.0, (0, 0, p.stav_z0), (50, 232), namn="06 framanfrå")
    Fv.liner(lin_f)
    Fv.senterlinje((0, 0, p.stav_z0), (0, 0, p.stav_z1))
    Sv = Vis(A, (0, -1, 0), (1, 0, 0), 1.0, (0, 0, p.stav_z0), (80, 232), namn="06 frå venstre")
    Sv.liner(hlr([stav], (0, -1, 0), (1, 0, 0), 0.01))
    ytop = Fv.P((0, 0, p.stav_z1))[1]
    mb(Fv, (0, -p.stav_b / 2, p.stav_z0), (0, -p.stav_b / 2, p.stav_z1), "v", Fv.P((0, -p.stav_b / 2, 0))[0] - 10,
       tal(L), L, "06 bbox z", bs.zlen)
    mb(Fv, (0, -p.stav_b / 2, p.stav_z1), (0, p.stav_b / 2, p.stav_z1), "h", ytop - 7, tal(p.stav_b), p.stav_b,
       "06 bbox y", bs.ylen)
    mb(Sv, (-p.stav_t / 2, 0, p.stav_z1), (p.stav_t / 2, 0, p.stav_z1), "h", ytop - 7, tal(p.stav_t), p.stav_t,
       "06 bbox x", bs.xlen)
    A.tekst((65, 242), "06 LYSSTAV (1:1)", 3.5, feit=True)
    A.tekst((65, 247), "framanfrå (+X) og frå venstre", 2.2)
    A.vis_bbox["06"] = [round(v, 1) for v in (Fv.bbox[0], Fv.bbox[1], Sv.bbox[2], Sv.bbox[3])]

    # ------------------------------------------------------------------ 06d mastfot, 4:1
    k4 = 4.0
    st = {"06d": (45, 2.0)}
    snA = snitt({"06d": fot}, (0, 0, 0), (1, 0, 0), (0, 1, 0), 0.01)
    SA = Vis(A, (1, 0, 0), (0, 1, 0), k4, (0, 0, z0f), (196, 128), namn="A-A")
    SA.skravur(snA["polys"], st)
    SA.liner(snA["liner"])
    SA.senterlinje((0, 0, z0f), (0, 0, z1f))
    oB = (0.0, 0.37, 0.0)
    snB = snitt({"06d": fot}, oB, (0, -1, 0), (1, 0, 0), 0.01)
    SB = Vis(A, (0, -1, 0), (1, 0, 0), k4, (0, 0, z0f), (296, 128), namn="B-B")
    SB.skravur(snB["polys"], st)
    SB.liner(snB["liner"])
    SB.senterlinje((0, 0, z0f), (0, 0, z1f))
    # nabodelar (strek-to-prikk): loddekroppen og skaftet til pluggen, staven i sporet
    rk = p.trs_kropp_d / 2.0
    for V_, langs_y in ((SA, True), (SB, False)):
        def q(a, z, V_=V_, langs_y=langs_y):
            return V_.P((0.0, a, z)) if langs_y else V_.P((a, 0.0, z))
        A.pl([q(-rk, z0f), q(-rk, z0f + p.trs_kropp_l), q(rk, z0f + p.trs_kropp_l), q(rk, z0f)], "f")
        for a in (-1.75, 1.75):
            A.linje(q(a, z0f), q(a, z0f - 3.0), "f")
    A.pl([SB.P((-p.stav_t / 2, 0, z1f)), SB.P((-p.stav_t / 2, 0, p.stav_z0)), SB.P((p.stav_t / 2, 0, p.stav_z0)),
          SB.P((p.stav_t / 2, 0, z1f))], "f")
    ytA = SA.P((0, 0, z1f))[1]
    yb = SA.P((0, 0, z0f))[1]
    mb(SA, (0, -ly, z1f), (0, ly, z1f), "h", ytA - 16, tal(p.mastfot_l), p.mastfot_l, "06d bbox y", bf.ylen)
    mb(SA, (0, -(p.stav_b / 2 + 0.05), z1f), (0, p.stav_b / 2 + 0.05, z1f), "h", ytA - 8, tal(p.stav_b + 0.1), p.stav_b + 0.1,
       "06d stavspor y (holrom langs y)", y_s1 - y_s0)
    mb(SA, (0, -ly, z0f), (0, -ly, z1f), "v", SA.P((0, -ly, 0))[0] - 14, tal(z1f - z0f), z1f - z0f, "06d bbox z", bf.zlen)
    d_l = p.trs_kropp_d + p.mastfot_lomme_klaring
    mb(SA, (0, -d_l / 2, z0f), (0, d_l / 2, z0f), "h", yb + 9, DIA + tal(d_l), d_l, "06d lomme (sylinderflate)", 2 * r_l)
    A.tekst((SA.px, yb + 15.5), "prototype %s%s" % (DIA, tal(pp.trs_kropp_d + pp.mastfot_lomme_klaring)), 2.5)
    xr = SA.P((0, ly, 0))[0] + 8
    mb(SA, (0, d_l / 2, z0f), (0, d_l / 2, p.stav_z0), "v", xr, tal(p.stav_z0 - z0f), p.stav_z0 - z0f,
       "06d golv i sporet - zmin (linjeprobe)", z_golv - bf.zmin)
    mb(SA, (0, p.stav_b / 2 + 0.05, p.stav_z0), (0, p.stav_b / 2 + 0.05, z1f), "v", xr, tal(z1f - p.stav_z0), z1f - p.stav_z0,
       "06d zmax - golv i sporet", bf.zmax - z_golv)
    SA.tittel("SNITT A-A (4:1)", under=yb + 25, dy=0)
    ytB = SB.P((0, 0, z1f))[1]
    xk0, xk1 = -p.stav_t / 2 - 0.05 - p.mastfot_kanal, p.stav_t / 2 + 0.05
    mb(SB, (-bx, 0, z1f), (bx, 0, z1f), "h", ytB - 16, tal(p.mastfot_b), p.mastfot_b, "06d bbox x", bf.xlen)
    mb(SB, (xk0, 0, z1f), (xk1, 0, z1f), "h", ytB - 8, tal(xk1 - xk0), xk1 - xk0, "06d spor + kanal x (holrom langs x)",
       x_s1 - x_s0, tekst_ut=False)
    mb(SB, (xk1, 0, z1f), (bx, 0, z1f), "h", ytB - 8, tal(bx - xk1), bx - xk1, "06d xmax - sporvegg +X", bf.xmax - x_s1,
       tekst_ut=True)
    xkm = (xk0 + (-p.stav_t / 2 - 0.05)) / 2
    SB.merknad(SB.P((xkm, 0, p.stav_z0 + 2.0)), (322.0, 52.0), ["Kanalen går ned i lomma"], h=2.2, side=1)
    SB.merknad(SB.P((0.3, 0, p.stav_z0 + 5.0)), (322.0, 40.0), ["Staven 06 (nabodel)"], h=2.2, side=1)
    SB.tittel("SNITT B-B (4:1)", under=yb + 25, dy=0)
    # sett ovanfrå: +X (framme) peikar nedover, som på dei andre arka
    T6 = Vis(A, (0, 0, 1), (0, 1, 0), k4, (0, 0, 0), (196, 190), namn="ovanfrå")
    T6.liner(hlr([fot], (0, 0, 1), (0, 1, 0), 0.01))
    A.pl([T6.P((-p.stav_t / 2, -p.stav_b / 2, z1f)), T6.P((-p.stav_t / 2, p.stav_b / 2, z1f)),
          T6.P((p.stav_t / 2, p.stav_b / 2, z1f)), T6.P((p.stav_t / 2, -p.stav_b / 2, z1f))], "f", lukk=True)
    T6.senterkryss((0, 0, z1f), ly + 2)
    snittlinje(T6, (0, -9.5, z1f), (0, 9.5, z1f), "A", (0, -1))
    snittlinje(T6, (-5.5, 0.37, z1f), (5.5, 0.37, z1f), "B", (1, 0))
    mb(T6, (-bx, -ly + 0.5, z1f), (bx, -ly + 0.5, z1f), "v", T6.P((0, -ly, 0))[0] - 22, tal(p.mastfot_b), p.mastfot_b,
       "06d bbox x", bf.xlen)
    T6.merknad(T6.P((-bx + 0.25, -ly + 0.25, z1f)), (150.0, 165.0), ["4 x fas %s x 45°" % tal(fas)], h=2.2, side=-1)
    T6.merknad(T6.P((xkm, 5.0, z1f)), (240.0, 162.0),
               ["Stavspor %s (staven %s + 0,1) og leidningskanal %s bak (%sX)" % (
                   tal(spor_b), tal(p.stav_t), tal(p.mastfot_kanal), MI)], h=2.2, side=1)
    T6.tittel("SETT OVANFRÅ (4:1)", under=232.0, dy=0)
    A.tekst((T6.px, 237.0), "+X (framme, LED-sida) peikar nedover", 2.2)

    # ------------------------------------------------------------------ 06d med pluggen, 2:1
    MK = Vis(A, (1, 0, 0), (0, 1, 0), 2.0, (0, 0, z0f), (372, 128), namn="06d med E8")
    MK.liner(hlr([D["06d_kontakt"]], (1, 0, 0), (0, 1, 0), 0.01))
    MK.senterlinje((0, 0, pc.zmin), (0, 0, z1f))
    mb(MK, (0, ly, pc.zmin), (0, ly, z0f), "v", MK.P((0, ly, 0))[0] + 8, tal(z0f - pc.zmin), z0f - pc.zmin,
       "E8 bbox: z0 mastfot - zmin plugg", z0f - pc.zmin)
    zs = (sk[0]["z"][0] + sk[0]["z"][1]) / 2
    mb(MK, (0, -r_sk, zs), (0, r_sk, zs), "h", MK.P((0, 0, pc.zmin))[1] + 8, DIA + tal(2 * r_sk), 2 * r_sk,
       "E8 skaft (sylinderflate)", 2 * r_sk)
    MK.tittel("06d MED TRS-PLUGG E8 (2:1)", dy=18)

    gg = sjekk.get("T03_gjennomgang", {})
    A.tekstblokk((262, 186), [
        "Merknader",
        "1. 06: flatstål EN AW-6060 %s x %s, kappa %s (H7). Kantar brotne." % (tal(p.stav_b), tal(p.stav_t), tal(bs.zlen)),
        "    Baksida (%sX) mattsvart, eloksert eller måla. Framsida (+X) ber LED-stripa 06b," % MI,
        "    %s..%s over underkanten." % (tal(p.stripe_z0 - p.stav_z0), tal(p.stripe_z1 - p.stav_z0)),
        "2. Inkje hol. Staven blir limt med 2K-epoksy (H11) i stavsporet i mastfoten 06d og til rista 07",
        "    (kil under golvet, bak og på sidene; FYR-T07). Lysmodulen er éi limt eining og blir bytt heil.",
        "3. 06d: POM-C fresa (serie) / PETG HF prenta (prototype). Fas %s x 45° på dei fire" % tal(fas),
        "    loddrette kantane. Prototypen skil seg berre i lomma.",
        "4. Lomme %s%s serie / %s%s prototype nedanfrå, %s djup (opp til golvet i sporet), for" % (
            DIA, tal(2 * r_l), DIA, tal(2 * r_lp), tal(z_golv - bf.zmin)),
        "    loddekroppen %s%s x %s til TRS-pluggen (E8), limt med epoksy (H11)." % (DIA, tal(p.trs_kropp_d), tal(p.trs_kropp_l)),
        "5. Stavspor %s x %s ovanfrå, %s djupt, med leidningskanal %s bak staven (%sX)" % (
            tal(spor_b), tal(y_s1 - y_s0), tal(z1f - z_golv), tal(p.mastfot_kanal), MI),
        "    ned i lomma: fire leiarar AWG 28 (E12: raud, blå, 2 x svart), tupp TOPP+, ring SIDE+,",
        "    hylse GND (FYR-E01).",
        "6. Staven blir limt i sporet (H11) og kviler på golvet utanfor lomma (|y| = %s..%s)." % (
            tal(y_golv_inn), tal(y_s1)),
        "7. Montert: mastfoten på z %s..%s, gjennom %s x %s i toppdekket (FYR-T03)." % (
            tal(bf.zmin), tal(bf.zmax), tal(gg.get("x", p.mastfot_b + 0.6)), tal(gg.get("y", p.mastfot_l + 0.6))),
    ], h=2.1, feit_forste=True)
    sjekk["T06_maal_mot_brep"] = rader
    return A


# ============================================================================ T07 lysrist
def ark_T07(D, p, sjekk):
    mat = delar_tekst("07_lysrist")
    A = Ark("T07", "Lysrist", "07", mat, "-", "1:1 (detaljar 2:1, 3:1)")
    s = D["07_lysrist"]
    bb = s.BoundingBox()
    z0 = bb.zmin
    st = {"07_lysrist": (45, 1.5)}
    F = Vis(A, (1, 0, 0), (0, 1, 0), 1.0, (0, 0, z0), (66, 256), namn="F")
    F.liner(hlr([s], (1, 0, 0), (0, 1, 0), 0.04), glatt=False)
    F.senterlinje((0, 0, z0), (0, 0, bb.zmax))
    o, n, x = akse_snitt(0.0)
    sn = snitt({"07_lysrist": s}, o, n, x, 0.02)
    S = Vis(A, n, x, 1.0, (0, 0, z0), (184, 256), namn="S")
    S.skravur(sn["polys"], st, tynn=0.6)
    S.liner(sn["liner"], glatt=False)
    S.senterlinje((0, 0, z0), (0, 0, bb.zmax))
    snittlinje(F, (0, 0.37, z0 - 2), (0, 0.37, bb.zmax + 5), "A", (1, 0))
    F.tittel("FRAMANFRÅ", under=F.P((0, 0, z0))[1], dy=19)
    S.tittel("SNITT A-A", under=S.P((0, 0, z0))[1], dy=19)
    Ry = bb.ylen / 2
    S.maal((-Ry, 0, bb.zmax), (Ry, 0, bb.zmax), "h", S.P((0, 0, bb.zmax))[1] - 8, DIA + tal(bb.ylen), bb.ylen)
    xl = S.P((-Ry, 0, 0))[0]
    S.maal((-Ry, 0, z0), (-Ry, 0, bb.zmax), "v", xl - 24, tal(bb.zlen), bb.zlen)
    with valfri("T07 høgder"):
        S.maal((-p.skjold_r, 0, z0), (-p.r_rand_ut, 0, p.skjort_z0), "v", xl - 8, tal(p.skjort_z0 - z0), p.skjort_z0 - z0)
        S.maal((-p.skjold_r, 0, z0), (-p.r_rand_ut, 0, p.z_lok_0), "v", xl - 16, tal(p.z_lok_0 - z0), p.z_lok_0 - z0)
    sete_tekst = []
    with valfri("T07 sete"):
        # boret i skjørtet (loket går i det) og innerdiameteren på setringen, målt på B-rep langs x
        z_b = p.z_lok_0 + 2.0
        g_b = [q for q in holrom(s, (-Ry - 2, 0.0, z_b), (Ry + 2, 0.0, z_b)) if q[1] - q[0] > 40]
        d_bor = g_b[0][1] - g_b[0][0]
        z_s = p.z_lok_0 - 0.6
        g_s = [q for q in holrom(s, (-Ry - 2, 0.0, z_s), (Ry + 2, 0.0, z_s)) if q[1] - q[0] > 40]
        d_set = g_s[0][1] - g_s[0][0]
        zs_iv = gjennom(s, (-(d_set / 2 + 0.5), 0.0, p.z_lok_0 - 5.0), (-(d_set / 2 + 0.5), 0.0, p.z_lok_0 + 0.5))
        z_set0, z_set1 = p.z_lok_0 - 5.0 + zs_iv[-1][0], p.z_lok_0 - 5.0 + zs_iv[-1][1]
        sjekk["T07_sete"] = {"bor_skjort": round(d_bor, 4), "setring_inn": round(d_set, 4),
                             "setring_z": [round(z_set0, 3), round(z_set1, 3)], "lok_param": round(2 * p.r_lok, 4)}
        S.maal((-d_bor / 2, 0, p.z_lok_1), (d_bor / 2, 0, p.z_lok_1), "h", S.P((0, 0, bb.zmax))[1] - 15,
               DIA + tal(d_bor), d_bor, avvik=TOL["rist"])
        S.maal((-d_set / 2, 0, z_set0), (d_set / 2, 0, z_set0), "h", S.P((0, 0, z_set0))[1] + 6,
               DIA + tal(d_set), d_set)
        sete_tekst = [
            "Sete for loket (08, %s%s %s): bor i skjørtet %s%s %s," % (DIA, tal(2 * p.r_lok), tol("lok"), DIA, tal(d_bor), tol("rist")),
            "setring innvendig %s%s, %s tjukk, %s..%s over underkant" % (
                DIA, tal(d_set), tal(z_set1 - z_set0), tal(z_set0 - z0), tal(z_set1 - z0)),
            "(%s under toppen)." % tal(bb.zmax - z_set1),
        ]
    lam = []
    with valfri("T07 lamellar"):
        rm = (p.rist_r_inn + p.rist_r_ut) / 2
        iv = gjennom(s, (rm, 0.9, z0 + 0.5), (rm, 0.9, bb.zmax - 0.5))
        lam = [(z0 + 0.5 + a, z0 + 0.5 + b) for a, b in iv if b - a < 4]
        i0 = len(lam) // 2
        deling = lam[i0 + 1][0] - lam[i0][0]
        tv = lam[i0][1] - lam[i0][0]
        # lekamane linja kryssar: golvet (nedst), lamellane, taket og bereren for toppemitteren (øvst)
        z_tak_r = p.tak_topp(rm)
        lam_berre = [q for q in lam if q[0] > p.rist_z0 + p.golv_t + 0.1 and q[1] < z_tak_r - p.rist_tv - 0.1]
        n_kryss = len(lam)
        sjekk["T07_lamell"] = {"lekamar_på_r_midt": n_kryss, "lamellar_målt": len(lam_berre),
                               "lamellar_param": len(p.lamell_tuppar), "ok": len(lam_berre) == len(p.lamell_tuppar),
                               "deling_målt": round(deling, 4), "loddrett_tjukn_målt": round(tv, 4),
                               "rist_tv_param": round(pv(p, "rist_tv", float("nan")), 4)}
        i0 = len(lam) // 2
        zc = (lam[i0][0] + lam[i0][1]) / 2
        cL = (rm, 0.0, zc + deling / 2)
        RL = 15.0
        Ld = detalj(A, S, sn, cL, RL, "L", 2.0, (340, 192), st, tynn=0.6, lab_vinkel=10.0, glatt=False)
        Ld.maal((rm, 0, lam[i0][0]), (rm, 0, lam[i0 + 1][0]), "v", Ld.P((p.rist_r_ut, 0, 0))[0] + 6, tal(deling), deling)
        # helling: apex i ytre tupp, referanse vassrett innover
        tb = math.tan(p.rist_helling * DEG)
        apex = Ld.P((p.rist_r_ut, 0, lam[i0 + 1][1] - (p.rist_r_ut - rm) * tb))
        d0 = (-1.0, 0.0)
        d1 = (-math.cos(p.rist_helling * DEG), -math.sin(p.rist_helling * DEG))
        vinkel_papir(A, apex, d0, d1, 9.0, tal(p.rist_helling) + "°")
        A.maallogg.append((tal(p.rist_helling) + "°", p.rist_helling, p.rist_helling))
    with valfri("T07 lamelltekst"):
        A.tekstblokk((229, 112), [
            "Lamellar: helling %s° under vassrett, ned og ut;" % tal(p.rist_helling),
            "deling %s, tjukn %s vinkelrett (%s loddrett)," % (tal(p.rist_deling), tal(p.rist_t), tal(p.rist_tv)),
            "r = %s..%s, i ein kile på ±%s° framme." % (tal(p.rist_r_inn), tal(p.rist_r_ut), tal(p.rist_vegg_vinkel)),
            "Inga direkte stråle frå stripa ut over",
            "%s° under vassrett." % tal(p.rist_avskjering, 1),
            "Golv %s, skjold bak r = %s x %s, skjørt %s." % (tal(p.golv_t), tal(p.skjold_r), tal(p.skjold_t), tal(p.skjort_t)),
            "Nøkkeltapp %s%s ved r = %s, asimut 0°." % (DIA, tal(p.nokkel_d), tal(p.nokkel_r)),
            "%d lamellar + tak (talde på B-rep på r = %s;" % (len(lam_berre), tal((p.rist_r_inn + p.rist_r_ut) / 2)),
            "snittet kryssar òg golv og berar).",
        ], h=2.2)
    hol_tekst = []
    with valfri("T07 stavspor"):
        # stavsporet i klypa (0,2 limfuge rundt staven) og toppen av sporet, der rista kviler på staven; målt på B-rep
        zm_k = (p.stripe_z0 + p.stripe_z1) / 2
        yb_k = (p.stripe_b / 2 + 0.6 + p.stav_b / 2) / 2          # bak vindauget for stripa, innanfor staven
        sx = [(-8.0 + a, -8.0 + b) for a, b in holrom(s, (-8.0, yb_k, zm_k), (8.0, yb_k, zm_k)) if -8.0 + a < 0.0 < -8.0 + b]
        sy = [(-12.0 + a, -12.0 + b) for a, b in holrom(s, (-0.5, -12.0, zm_k), (-0.5, 12.0, zm_k)) if -12.0 + a < 0.0 < -12.0 + b]
        mz = [(z0 - 1.0 + a, z0 - 1.0 + b) for a, b in gjennom(s, (-0.5, yb_k, z0 - 1.0), (-0.5, yb_k, bb.zmax + 1.0))]
        z_topp_spor = min(a for a, _b in mz if a > p.rist_z0 + p.golv_t + 1.0)
        spor_x, spor_y = sx[0][1] - sx[0][0], sy[0][1] - sy[0][0]
        stav = D["06_lysstav"]
        bs = stav.BoundingBox()
        sjekk["T07_stavspor"] = {"spor_x": [round(v, 4) for v in sx[0]], "spor_y": [round(v, 4) for v in sy[0]],
                                 "limfuge_x": round((spor_x - bs.xlen) / 2, 4), "limfuge_y": round((spor_y - bs.ylen) / 2, 4),
                                 "topp_spor_z": round(z_topp_spor, 4), "stav_zmax": round(bs.zmax, 4),
                                 "ok": bool(abs(z_topp_spor - bs.zmax) < 0.01 and abs((spor_x - bs.xlen) / 2 - 0.2) < 0.01
                                            and abs((spor_y - bs.ylen) / 2 - 0.2) < 0.01)}
        # teksten følgjer B-rep: kviler rista på staven (toppen av sporet = toppen av staven), eller står det luft over?
        kviler = abs(z_topp_spor - bs.zmax) < 0.01
        if not kviler:
            sjekk["T07_stavspor"]["merknad"] = ("toppen av stavsporet ligg %s over toppen av staven: rista kviler ikkje "
                                                "på staven i CAD" % tal(z_topp_spor - bs.zmax))
        S.merknad(S.P((0.0, 0, z_topp_spor)), (222.0, 88.0),
                  ["Rista kviler på toppen av", "staven (z %s), limt (H11)" % tal(bs.zmax)] if kviler else
                  ["Toppen av stavsporet, z %s" % tal(z_topp_spor),
                   "(%s over staven), limt (H11)" % tal(z_topp_spor - bs.zmax)], h=2.2, side=1)
        hol_tekst = [
            "3. Stavspor %s x %s gjennom golv og klype opp til z %s" % (tal(spor_x), tal(spor_y), tal(z_topp_spor)),
            ("    (staven 06, %s x %s, + limfuge 0,2). Rista kviler på toppen av staven" % (tal(bs.xlen), tal(bs.ylen))
             if kviler else
             "    (staven 06, %s x %s, + limfuge 0,2; %s luft over staven). Rista" % (
                 tal(bs.xlen), tal(bs.ylen), tal(z_topp_spor - bs.zmax))),
            "    og er limt med ein kil epoksy (H11) under golvet, bak og på sidene; sporet" if kviler else
            "    er limt med ein kil epoksy (H11) under golvet, bak og på sidene; sporet",
            "    hindrar vriing. Lysmodulen 06/06b/06c/06d/07 er éi limt eining.",
        ]
    with valfri("T07 leidningsgjennomgangar"):
        # leidningsgjennomgangane i golvet, målt på B-rep midt i golvet (z_g): framfor staven og bak klypa
        z_g = p.rist_z0 + p.golv_t / 2

        def tomrom_langs(a, b, inni_pt):
            L_ = float(np.linalg.norm(np.subtract(b, a)))
            d_ = np.subtract(b, a) / L_
            t_ = float(np.subtract(inni_pt, a) @ d_)
            q_ = [(u, v) for u, v in holrom(s, a, b) if u < t_ < v]
            return (float(np.add(a, d_ * q_[0][0]) @ d_), float(np.add(a, d_ * q_[0][1]) @ d_)) if q_ else (float("nan"),) * 2
        # framfor: tomrommet langs x på y = 0 er stavsporet + gjennomgangen; utanfor gjennomgangen (y = 5,5) berre sporet
        fx_med = tomrom_langs((-6.0, 0.0, z_g), (6.0, 0.0, z_g), (1.8, 0.0, z_g))
        fx_utan = tomrom_langs((-6.0, 5.5, z_g), (6.0, 5.5, z_g), (0.0, 5.5, z_g))
        fy = tomrom_langs((1.8, -12.0, z_g), (1.8, 12.0, z_g), (1.8, 0.0, z_g))
        bx = tomrom_langs((-8.0, 5.25, z_g), (0.0, 5.25, z_g), (-3.4, 5.25, z_g))
        by = tomrom_langs((-3.4, -2.0, z_g), (-3.4, 12.0, z_g), (-3.4, 5.25, z_g))
        # gjennom golvet: ingen materiale langs z frå under golvet til over det
        fz = gjennom(s, (1.8, 0.0, p.rist_z0 - 0.5), (1.8, 0.0, p.rist_z0 + p.golv_t + 0.5))
        bz = gjennom(s, (-3.4, 5.25, p.rist_z0 - 0.5), (-3.4, 5.25, p.rist_z0 + p.golv_t + 0.5))
        # golvet rundt (kontroll av at snittet går i golvet): materiale ved sida av gjennomgangane
        gz = gjennom(s, (-3.4, 0.0, p.rist_z0 - 0.5), (-3.4, 0.0, p.rist_z0 + p.golv_t + 0.5))
        f_x0, f_x1 = fx_utan[1], fx_med[1]
        lb = p.leidning_b

        # sidestripa 06b sit på staven når rista blir senka, så heile stripa går gjennom golvet: sveip tverrsnittet
        # av stripa (utan og med 0,2 klaring framfor og på sidene) frå under golvet til toppen av stripa og mål kor
        # mykje av rista sveipet skjer (B-rep). Gjennomgangen må vere minst så stor som stripa pluss klaring.
        def sveip_stripe(kl_):
            z_a = p.rist_z0 - 1.0
            b_ = cq.Solid.makeBox(p.stripe_t + kl_, p.stripe_b + 2 * kl_, p.stripe_z1 - z_a,
                                  cq.Vector(p.stav_t / 2, -p.stripe_b / 2 - kl_, z_a))
            try:
                return float(s.intersect(b_).Volume())
            except Exception:  # noqa: BLE001
                return float("nan")
        v_st, v_st_kl = sveip_stripe(0.0), sveip_stripe(0.2)
        stripe_fri = bool(v_st_kl < 1e-6)
        if not stripe_fri:
            print("  T07: sidestripa 06b skjer golvet i rista når rista blir senka (%.3f mm³, med 0,2 klaring %.3f mm³)"
                  % (v_st, v_st_kl), flush=True)
        sjekk["T07_leidningsgjennomgangar"] = {
            "golv_z": [round(p.rist_z0, 4), round(p.rist_z0 + p.golv_t, 4)],
            "golv_målt_ved_x-3,4_y0": [[round(p.rist_z0 - 0.5 + a, 4), round(p.rist_z0 - 0.5 + b, 4)] for a, b in gz],
            "framfor_staven": {"x": [round(f_x0, 4), round(f_x1, 4)], "y": [round(fy[0], 4), round(fy[1], 4)],
                               "breidd_x": round(f_x1 - f_x0, 4), "lengd_y": round(fy[1] - fy[0], 4),
                               "open_gjennom_golvet": not fz,
                               "stripa_06b_gjennom_golvet": {
                                   "sveip_skjer_rista_mm3": round(v_st, 4),
                                   "sveip_med_0,2_klaring_skjer_rista_mm3": round(v_st_kl, 4),
                                   "krav": "stripa %s x %s + 0,2 klaring framfor og på sidene, z %s..%s, skal ikkje skjere rista"
                                           % (tal(p.stripe_t), tal(p.stripe_b), tal(p.rist_z0 - 1.0), tal(p.stripe_z1)),
                                   "ok": stripe_fri}},
            "bak_klypa": {"x": [round(bx[0], 4), round(bx[1], 4)], "y": [round(by[0], 4), round(by[1], 4)],
                          "breidd_x": round(bx[1] - bx[0], 4), "lengd_y": round(by[1] - by[0], 4),
                          "open_gjennom_golvet": not bz},
            "leidning_b_param": lb,
            # framfor staven: minst leidning_b x stripebreidda (kor stor han må vere, avgjer sveipet over)
            "ok": bool(stripe_fri and not fz and not bz and gz and f_x1 - f_x0 > lb - 0.02 and fy[1] - fy[0] > p.stripe_b - 0.02
                       and abs(bx[0] - (-p.stav_t / 2 - 1.6 - lb - 0.4)) < 0.02 and abs(bx[1] - (-p.stav_t / 2 - 1.6)) < 0.02
                       and abs(by[0] - 3.0) < 0.02 and abs(by[1] - 7.5) < 0.02)}
        # snitt B-B gjennom golvet, sett ovanfrå (+X nedover som i SETT OVANFRÅ), 3:1, delvis snitt klipt til
        # eit rektangel (x -5..3,2, y -9,5..9,5) så måla kan stå utanfor skraveringa
        kB = 3.0
        cB = (-0.9, 0.0, z_g)
        pB = (258.0, 190.0)
        xr0, xr1, yr = -5.0, 3.2, 9.5
        lok_s = s.intersect(cq.Solid.makeCylinder(14.0, z_g - (z0 - 1.0), cq.Vector(0, 0, z0 - 1.0), cq.Vector(0, 0, 1)))
        snB = snitt({"07_lysrist": lok_s}, (0, 0, z_g), (0, 0, 1), (0, 1, 0), 0.005)
        V0 = Vis(A, (0, 0, 1), (0, 1, 0), kB, cB, pB)
        hjorne = [(xr0, -yr), (xr0, yr), (xr1, yr), (xr1, -yr)]
        B = Vis(A, (0, 0, 1), (0, 1, 0), kB, cB, pB, klipp=Polygon([V0.pr((x_, y_, z_g)) for x_, y_ in hjorne]), namn="B-B")
        B.skravur(snB["polys"], {"07_lysrist": (45, 1.2)}, tynn=0.4)
        B.liner(snB["liner"], glatt=False)
        A.pl([B.P((x_, y_, z_g)) for x_, y_ in hjorne], "t", lukk=True)
        # staven 06 i sporet (nabodel)
        A.pl([B.P((-p.stav_t / 2, -p.stav_b / 2, z_g)), B.P((-p.stav_t / 2, p.stav_b / 2, z_g)),
              B.P((p.stav_t / 2, p.stav_b / 2, z_g)), B.P((p.stav_t / 2, -p.stav_b / 2, z_g))], "f", lukk=True)
        B.senterlinje((xr0 + 0.5, 0.0, z_g), (xr1 - 0.5, 0.0, z_g), ut=0.0)
        ytopp_B, ybotn_B = B.P((xr0, 0, z_g))[1], B.P((xr1, 0, z_g))[1]
        xh_B = B.P((0, yr, z_g))[0]
        # framfor staven: lengd langs y (under), djupn langs x frå sporveggen (til høgre)
        B.maal((f_x1, fy[0], z_g), (f_x1, fy[1], z_g), "h", ybotn_B + 6.0, tal(fy[1] - fy[0], 1), fy[1] - fy[0])
        B.maal((f_x1, fy[1], z_g), (f_x0, fy[1], z_g), "v", xh_B + 11.0, tal(f_x1 - f_x0, 1), f_x1 - f_x0)
        # bak klypa: avstand frå senterlinja og lengd langs y (over), breidd langs x (til høgre)
        B.maal((bx[0], 0.0, z_g), (bx[0], by[0], z_g), "h", ytopp_B - 6.0, tal(by[0], 1), by[0], tekst_ut=False)
        B.maal((bx[0], by[0], z_g), (bx[0], by[1], z_g), "h", ytopp_B - 6.0, tal(by[1] - by[0], 1), by[1] - by[0])
        B.maal((bx[1], by[1], z_g), (bx[0], by[1], z_g), "v", xh_B + 5.0, tal(bx[1] - bx[0], 1), bx[1] - bx[0])
        A.tekst((pB[0], ybotn_B + 18.0), "SNITT B-B (3:1)", 3.5, feit=True)
        A.tekst((pB[0], ybotn_B + 22.5), "+X (framme) peikar nedover", 2.2)
        A.vis_bbox["B-B"] = [round(v, 1) for v in (B.P((0, -yr, 0))[0], ytopp_B, xh_B, ybotn_B)]
        # snittlinja B-B på snitt A-A: gjennom golvet, sett ned
        snittlinje(S, (-14.0, 0, z_g), (4.0, 0, z_g), "B", (0, 1))
        hol_tekst += [
            "4. Leidningsgjennomgangar gjennom golvet, z %s..%s (snitt B-B):" % (
                tal(p.rist_z0), tal(p.rist_z0 + p.golv_t)),
            ("    framfor staven %s x %s (x %s..%s, y %s..%s): stripa 06b og leiarane;" if stripe_fri else
             "    framfor staven %s x %s (x %s..%s, y %s..%s): sidestripa 06b;") % (
                tal(f_x1 - f_x0, 1), tal(fy[1] - fy[0], 1), tal(f_x0, 1), tal(f_x1, 1), tal(fy[0], 1), tal(fy[1], 1)),
            "    bak klypa %s x %s (x %s..%s, y %s..%s): toppstripene 06c." % (
                tal(bx[1] - bx[0], 1), tal(by[1] - by[0], 1), tal(bx[0], 1), tal(bx[1], 1), tal(by[0], 1), tal(by[1], 1)),
            "    Under golvet går leiarane (E12) rundt staven til kanalen i 06d (FYR-T06).",
        ]
    T = Vis(A, (0, 0, 1), (0, 1, 0), 1.0, (0, 0, 0), (300, 58), namn="T")
    T.liner(hlr([s], (0, 0, 1), (0, 1, 0), 0.04), glatt=False)
    T.senterkryss((0, 0, 0), Ry + 4)
    with valfri("T07 nabbar og fingergrep"):
        # nabbane over loket og fingergrepa i skjørtet, funne ved punktprøve rundt på B-rep
        r_sk_i = p.r_rand_ut - p.skjort_t

        def sektorar(r, z):
            fylt = [inni(s, (r * math.cos(t * DEG), r * math.sin(t * DEG), z)) for t in np.arange(0.0, 360.0, 0.25)]
            n_ = len(fylt)
            start = [i for i in range(n_) if fylt[i] and not fylt[i - 1]]
            def kant(inne_, ute_):          # halvering mellom ein fylt og ein tom vinkel
                for _ in range(30):
                    m_ = (inne_ + ute_) / 2
                    if inni(s, (r * math.cos(m_ * DEG), r * math.sin(m_ * DEG), z)):
                        inne_ = m_
                    else:
                        ute_ = m_
                return (inne_ + ute_) / 2
            ut = []
            for i0 in start:
                j = i0
                while fylt[(j + 1) % n_]:
                    j += 1
                a0_ = kant(i0 * 0.25, i0 * 0.25 - 0.25)
                a1_ = kant(j * 0.25, j * 0.25 + 0.25)
                ut.append(((a0_ + a1_) / 2 % 360.0, a1_ - a0_))
            return ut
        nabb = sektorar((p.r_lok + r_sk_i) / 2 - 0.1, p.z_lok_1 + 0.25)
        skj = sektorar((p.r_rand_ut + r_sk_i) / 2, p.z_lok_0 + 1.5)
        # fingergrepa er glippene mellom skjørtbitane
        grep = []
        sk = sorted(skj)
        for i_ in range(len(sk)):
            a_, b_ = sk[i_], sk[(i_ + 1) % len(sk)]
            e0 = (a_[0] + a_[1] / 2) % 360.0
            s1 = (b_[0] - b_[1] / 2) % 360.0
            w = (s1 - e0) % 360.0
            if 0.5 < w < 60:
                grep.append(((e0 + w / 2) % 360.0, w))
        sjekk["T07_nabbar"] = {"nabbar_asimut_breidd": [(round(a_, 2), round(w_, 2)) for a_, w_ in nabb],
                               "fingergrep_asimut_breidd": [(round(a_, 2), round(w_, 2)) for a_, w_ in grep]}
        an = sorted(round(a_) % 360 for a_, _ in nabb)
        ag = sorted(round(a_) % 360 for a_, _ in grep)
        a1n = an[1] if len(an) > 1 else an[0]
        rn = (p.r_lok + r_sk_i) / 2
        T.merknad(T.P((rn * math.cos(a1n * DEG), rn * math.sin(a1n * DEG), bb.zmax)), (348, 26),
                  ["%d nabbar ved %s° held loket," % (len(an), "/".join(str(a_) for a_ in an)),
                   "breidd %s° (målt)" % tal(nabb[0][1], 1)], h=2.2, side=1)
        rg = (p.r_rand_ut + r_sk_i) / 2
        T.merknad(T.P((rg * math.cos(ag[0] * DEG), rg * math.sin(ag[0] * DEG), bb.zmax)), (348, 74),
                  ["%d fingergrep ved %s°," % (len(ag), "/".join(str(a_) for a_ in ag)),
                   "breidd %s° (målt)" % tal(grep[0][1], 1)], h=2.2, side=1)
    T.tittel("SETT OVANFRÅ")
    A.tekstblokk((300, 112), [
        "Merknader",
        "1. %s; kvit, ugjennomsiktig, lysande flater utan riper." % (mat or "Sjå stykkliste"),
        "2. Éin del: golv, lamellar, tak, sideveggar, skjold, berar, skjørt, sete.",
    ] + hol_tekst + (["5. " + sete_tekst[0]] + ["    " + t_ for t_ in sete_tekst[1:]] if sete_tekst else []),
        h=2.2, feit_forste=True)
    return A


# ============================================================================ T08 lok + T10 glidering
def ark_T08(D, p, sjekk):
    A = Ark("T08", "Lok og glidering", "08, 10", "08: PMMA opal 3; 10: POM-C", "08: laserskoren; 10: delt ring", "1:1 (detalj 10:1)")
    lok = D["08_lok"]
    gl = D["10_glidering"]
    bl = lok.BoundingBox()
    r_l = bl.xlen / 2
    T = Vis(A, (0, 0, 1), (0, 1, 0), 1.0, (0, 0, 0), (90, 80), namn="T8")
    T.liner(hlr([lok], (0, 0, 1), (0, 1, 0), 0.02))
    T.senterkryss((0, 0, 0), r_l + 4)
    T.maal((0, -r_l, bl.zmax), (0, r_l, bl.zmax), "a", 0.0, DIA + tal(2 * r_l), bl.ylen, avvik=TOL["lok"])
    T.tittel("08 LOK, SETT OVANFRÅ")
    F = Vis(A, (1, 0, 0), (0, 1, 0), 1.0, (0, 0, bl.zmin), (90, 150), namn="F8")
    F.liner(hlr([lok], (1, 0, 0), (0, 1, 0), 0.02))
    F.maal((0, r_l, bl.zmin), (0, r_l, bl.zmax), "v", F.P((0, r_l, 0))[0] + 8, tal(bl.zlen), bl.zlen)
    F.tittel("FRAMANFRÅ", dy=8)
    A.tekstblokk((40, 178), [
        "08 Lok",
        "%s, laserskoren." % (delar_tekst("08_lok") or "PMMA opal 3 mm"),
        "Ligg i setet i lysristen og blir halde av tre nabbar.",
        "Går i boret %s%s %s i skjørtet på lysrista (FYR-T07)." % (DIA, tal(2 * (p.r_rand_ut - p.skjort_t)), tol("rist")),
        "DXF: produksjon/fyr_08_lok.dxf (lag SKJER).",
        "Prototype %s%s (H6): produksjon/fyr_08_lok_prototype.dxf." % (DIA, tal(2 * g.FyrParams.prototype().r_lok)),
    ], h=2.4, feit_forste=True)
    bg = gl.BoundingBox()
    ro = bg.xlen / 2
    TG = Vis(A, (0, 0, 1), (0, 1, 0), 1.0, (0, 0, 0), (245, 80), namn="TG")
    TG.liner(hlr([gl], (0, 0, 1), (0, 1, 0), 0.02))
    TG.senterkryss((0, 0, 0), ro + 4)
    TG.maal((0, -ro, bg.zmax), (0, ro, bg.zmax), "a", 0.0, DIA + tal(2 * ro), bg.ylen, avvik=TOL["glide_ut"])
    o, n, x = akse_snitt(0.0)
    snittlinje(TG, (-ro - 3, 0.37, bg.zmax), (ro + 3, 0.37, bg.zmax), "A", (1, 0))
    # kuttet: ikkje modellert i CAD; plassering ved montering bak (180°), vekk frå vindauget
    a_k = 180.0 + 12.0
    TG.merknad(TG.P((ro * math.cos(a_k * DEG), ro * math.sin(a_k * DEG), bg.zmax)),
               (TG.P((0, 0, 0))[0] - 30, TG.P((0, 0, 0))[1] - ro - 10),
               ["Kutt (sjå skisse): set ved 180° (bak)"], h=2.2, side=-1)
    TG.tittel("10 GLIDERING, SETT OVANFRÅ", dy=19)
    sn = snitt({"10_glidering": gl}, o, n, x, 0.005)
    SG = Vis(A, n, x, 1.0, (0, 0, bg.zmin), (245, 150), namn="SG")
    SG.skravur(sn["polys"], {"10_glidering": (45, 1.0)}, tynn=0.3)
    SG.liner(sn["liner"])
    SG.senterlinje((0, 0, bg.zmin), (0, 0, bg.zmax))
    SG.maal((ro, 0, bg.zmin), (ro, 0, bg.zmax), "v", SG.P((ro, 0, 0))[0] + 8, tal(bg.zlen), bg.zlen)
    SG.tittel("SNITT A-A", dy=8)
    ri = p.r_glide_i
    with valfri("T08 detalj G"):
        cG = (p.r_mi - p.glide_t / 2, 0.0, (bg.zmin + bg.zmax) / 2)
        G = detalj(A, SG, sn, cG, 4.0, "G", 10.0, (362, 128), {"10_glidering": (45, 1.5)}, lab_vinkel=-90.0)
        G.maal((ri, 0, bg.zmax), (p.r_mi, 0, bg.zmax), "h", G.P((0, 0, bg.zmax))[1] - 18, tal(p.r_mi - ri), p.r_mi - ri)
        fz = gjennom(gl, (ri + 0.1, 0.37, bg.zmin - 1), (ri + 0.1, 0.37, bg.zmax + 1))
        fas = fz[0][0] - 1.0 + 0.1
        G.merknad(G.P((ri + fas / 2, 0, bg.zmax - fas / 2)), (G.P((ri, 0, 0))[0] - 26, G.P((0, 0, bg.zmax))[1] - 16),
                  ["%s x 45° (2x)" % tal(fas, 1)], side=-1)
    lo_id, hi_id = glide_montert_id(p)
    A.tekstblokk((200, 178), [
        "10 Glidering",
        "POM-C, %s%s / %s%s x %s, innføringsfas oppe og nede inne." % (DIA, tal(2 * ro), DIA, tal(2 * ri), tal(bg.zlen)),
        "Fri ytterdiameter %s%s %s, vegg %s %s: presspassa i mantelboret" % (
            DIA, tal(2 * ro), tol("glide_ut"), tal(p.glide_t), tol("glide_t")),
        "%s%s %s (04); montert innerdiameter %s%s..%s mot hylsa %s%s %s (05)." % (
            DIA, tal(2 * p.r_mi), tol("mantel"), DIA, tal(lo_id), tal(hi_id), DIA, tal(2 * p.r_ho), tol("hylse")),
        "Delt ring: eitt skrått kutt, sjå skissa under (ikkje modellert i CAD).",
        "Sit %s under toppkanten av mantelen og styrer hylsa." % tal(p.glide_under_kant),
    ], h=2.4, feit_forste=True)
    # skisse av kuttet, sett radielt utanfrå (4:1): skrått 45° mot aksen, spalte målt langs omkrinsen
    KUTT_VINKEL, KUTT_SPALTE = 45.0, 2.0
    k4 = 4.0
    x0, y1 = 40.0, 232.0
    hh = p.glide_h * k4
    y0 = y1 - hh
    w = 60.0
    A.pl([(x0, y0), (x0 + w, y0), (x0 + w, y1), (x0, y1)], "k", lukk=True)
    xa = x0 + 14.0
    dx = hh / math.tan(KUTT_VINKEL * DEG)
    sp = KUTT_SPALTE * k4
    for xx in (xa, xa + sp):
        A.linje((xx, y1), (xx + dx, y0), "k")
    A.flate([[(xa, y1), (xa + sp, y1), (xa + sp + dx, y0), (xa + dx, y0)]], fyll="#fff")
    A.maal((xa, y1), (xa + sp, y1), "h", y1 + 7.0, tal(KUTT_SPALTE))
    vinkel_papir(A, (xa + sp, y1), (1.0, 0.0), (math.cos(KUTT_VINKEL * DEG), -math.sin(KUTT_VINKEL * DEG)), 9.0,
                 tal(KUTT_VINKEL) + "°")
    A.tekst((x0 + w + 4, y0 + 6), "Kutt i glideringen (4:1), sett utanfrå:", 2.2, anker="start", feit=True)
    A.tekst((x0 + w + 4, y0 + 10), "skrått %s° mot aksen gjennom heile veggen," % tal(KUTT_VINKEL), 2.2, anker="start")
    A.tekst((x0 + w + 4, y0 + 14), "spalte %s ± 0,2 langs omkrinsen i fri tilstand" % tal(KUTT_SPALTE), 2.2, anker="start")
    A.tekst((x0 + w + 4, y0 + 18), "(montert %s..%s). Set kuttet ved 180° (bak)." % (
        tal(KUTT_SPALTE - 0.2 - math.pi * (2 * ro + tv("glide_ut")[0] - (2 * p.r_mi + tv("mantel")[1])), 1),
        tal(KUTT_SPALTE + 0.2 - math.pi * (2 * ro + tv("glide_ut")[1] - (2 * p.r_mi + tv("mantel")[0])), 1)), 2.2, anker="start")
    d_serie = dxf_lok(lok, p)
    with valfri("T08 prototype-DXF"):
        d_prot = dxf_lok_prototype()
        sjekk["T08_lok_dxf"] = {"serie_d": round(d_serie, 4), "prototype_d": round(d_prot, 4),
                                "prototype_d_param": round(2 * g.FyrParams.prototype().r_lok, 4),
                                "ok": bool(abs(d_serie - 2 * p.r_lok) < 0.01 and
                                           abs(d_prot - 2 * g.FyrParams.prototype().r_lok) < 0.01)}
    return A


# ============================================================================ E01 koplingsskjema
# Koplinga slik fyr_geometri.py skildrar ho (kommentaren ved FyrParams.sw): tre parallelle høgsidevegar.
# (indeks i p.sw, motstand eller None, pol på X1, rolle). Endre her om koplinga blir endra.
KOPLING = [
    (0, "R1", "TOPP+", "glød"),
    (2, "R3", "TOPP+", "full"),
    (1, None, "SIDE+", "side"),
]


def brytar_tabell(D, p):
    hylse = D["05_hylse"]
    fot = D["05b_hylsefot"]
    rader = []
    for kk in range(int(round(p.vandring / p.deling)) + 1):
        th = kk * p.deling
        h = hylse.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -th) if th else hylse
        f = fot.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -th) if th else fot
        zm = (p.z_spalte_0 + p.z_spalte_1) / 2
        r = (p.r_ho + p.r_hi) / 2
        opne = 0
        for a in p.vindauge_vinklar:
            blokk = False
            for dy in (-1.4, 0.0, 1.4):
                da = math.degrees(dy / r)
                x, y = g.polar(r, a + da)
                for dz in (-50.0, 0.0, 50.0):
                    if inni(h, (x, y, zm + dz)):
                        blokk = True
            opne += 0 if blokk else 1
        sw = []
        for (a_sw, _t) in p.sw:
            x, y = g.polar(p.sw_r, a_sw)
            sw.append(bool(inni(f, (x, y, p.toppdekk_z1 + 0.3))))
        rader.append((th, opne, sw))
    return rader


def ark_E01(D, p, sjekk):
    A = Ark("E01", "Koplingsskjema", "E", "-", "-", "-", "Koplingsskjema")
    namn = list(pv(p, "sw_namn", ())) or ["SW%d" % (i + 1) for i in range(len(p.sw))]

    def leidning(pts):
        A.pl(pts, "k")

    def node(pt):
        A.prikk(pt, 0.9)

    def brytar(xa, y, nn, tekst):
        A.sirkel((xa, y), 0.9, "t")
        A.sirkel((xa + 12, y), 0.9, "t")
        A.linje((xa + 0.8, y - 0.4), (xa + 11.5, y - 4.8), "k")
        A.tekst((xa + 6, y - 7.5), nn, 3.0, feit=True)
        for j, t_ in enumerate([tekst] if isinstance(tekst, str) else tekst):
            A.tekst((xa - 1, y + 5.0 + 3.2 * j), t_, 2.0, anker="start")

    def motstand(xa, y, nn, tekst):
        A.pl([(xa, y - 1.6), (xa + 12, y - 1.6), (xa + 12, y + 1.6), (xa, y + 1.6)], "k", lukk=True)
        A.tekst((xa + 6, y - 3.5), nn, 3.0, feit=True)
        A.tekst((xa + 6, y + 5.5), tekst, 2.0)

    def led(xx, ya, nn, tekst, side=1):
        A.pl([(xx - 3, ya), (xx + 3, ya), (xx, ya + 5)], "k", lukk=True)
        A.linje((xx - 3, ya + 5), (xx + 3, ya + 5), "k")
        for dy in (1.0, 3.0):
            A.linje((xx + 3.5, ya + dy), (xx + 7, ya + dy - 2.5), "t")
            A.pil((xx + 7, ya + dy - 2.5), (1, -0.7), 1.4, 0.45)
        if side > 0:
            A.tekst((xx + 9, ya + 2.5), nn, 3.0, anker="start", feit=True)
            A.tekst((xx + 9, ya + 6.5), tekst, 2.0, anker="start")
        else:
            A.tekst((xx - 5, ya + 2.5), nn, 3.0, anker="end", feit=True)
            A.tekst((xx - 5, ya + 6.5), tekst, 2.0, anker="end")

    def jord(xx, y):
        A.linje((xx, y), (xx, y + 3), "k")
        A.linje((xx - 3, y + 3), (xx + 3, y + 3), "k")
        A.linje((xx - 2, y + 4.2), (xx + 2, y + 4.2), "k")
        A.linje((xx - 1, y + 5.4), (xx + 1, y + 5.4), "k")

    yg = 185.0
    ys = [60.0 + 40.0 * i for i in range(len(KOPLING))]
    # J1 og F1
    A.pl([(30, ys[0] - 8), (48, ys[0] - 8), (48, yg + 8), (30, yg + 8)], "k", lukk=True)
    A.tekst((39, (ys[0] + yg) / 2 - 4), "J1", 3.5, feit=True)
    A.tekst((39, (ys[0] + yg) / 2 + 1), "USB 5 V", 2.5)
    A.tekst((39, (ys[0] + yg) / 2 + 5), "E9 kabel", 1.8)
    A.tekst((39, (ys[0] + yg) / 2 + 8.2), "E10 JST PH", 1.8)
    A.tekst((50, ys[0] - 1.5), "VBUS", 2.0, anker="start")
    A.tekst((50, yg - 1.5), "GND", 2.0, anker="start")
    leidning([(48, ys[0]), (60, ys[0])])
    motstand(60, ys[0], "F1", "PTC")
    xb = 95.0
    leidning([(72, ys[0]), (xb, ys[0]), (xb, ys[-1])])
    A.tekst((xb - 2, ys[0] - 3), "+5V", 2.5, anker="end")
    x1 = 215.0
    pinnar = {"TOPP+": ys[0], "SIDE+": ys[-1], "GND": yg}
    topp_x = 196.0
    for i, (idx, mot, pol, rolle) in enumerate(KOPLING):
        y = ys[i]
        if i > 0:
            node((xb, y))
        leidning([(xb, y), (110, y)])
        a_sw, ter = p.sw[idx]
        # same ordlyd som FyrParams og dei andre dokumenta: lukka frå 0 til terskel - rampe/2 (halv djupn), avrunda
        brytar(110, y, "SW%d" % (idx + 1), [
            "%s, %s°, lukka 0..ca %d°" % (namn[idx].split(" ")[1] if len(namn[idx].split(" ")) > 1 else "",
                                          tal(a_sw), int(round(ter - p.kam_rampe / 2.0))),
            "(utsparing full djupn ved %s°)" % tal(ter)])
        if mot:
            leidning([(122, y), (168, y)])
            motstand(168, y, mot, "%s: sjå innkjøpsliste" % mot)
            x_ut = 180.0
        else:
            x_ut = 122.0
        if pol == "TOPP+":
            leidning([(x_ut, y), (topp_x, y), (topp_x, pinnar["TOPP+"])])
            if y != pinnar["TOPP+"]:
                node((topp_x, pinnar["TOPP+"]))
        else:
            leidning([(x_ut, y), (topp_x, y)])
            leidning([(topp_x, y), (x1, y)])
            pinnar[pol] = y
    leidning([(topp_x, pinnar["TOPP+"]), (x1, pinnar["TOPP+"])])
    leidning([(48, yg), (x1, yg)])
    jord(80, yg)
    A.pl([(x1, ys[0] - 8), (x1 + 10, ys[0] - 8), (x1 + 10, yg + 8), (x1, yg + 8)], "k", lukk=True)
    for pol, nr, t in (("TOPP+", "T", "tupp: TOPP+"), ("SIDE+", "R", "ring: SIDE+"), ("GND", "S", "hylse: GND")):
        y = pinnar[pol]
        A.tekst((x1 + 2.5, y + 1.0), nr, 2.2)
        A.tekst((x1 + 12, y - 1.5), t, 2.0, anker="start")
    A.tekst((x1 + 5, ys[0] - 11), "X1 = 13 + 06d", 2.8, feit=True)
    A.tekst((x1 + 5, yg + 13), "TRS 3,5 mm", 2.2)
    xt, xs = 318.0, 302.0
    # 06c er fire bitar på bereringen, i parallell: + og GND går som bøylar over skøytane mellom bitane
    # (monteringsrettleiinga, side M, steg 1)
    y_r0, y_r1, dx_c = 102.0, 117.0, 16.0
    xc = [xt + dx_c * i for i in range(4)]
    leidning([(x1 + 10, pinnar["TOPP+"]), (xt, pinnar["TOPP+"]), (xt, y_r0)])
    leidning([(xc[0], y_r0), (xc[-1], y_r0)])
    leidning([(xc[0], y_r1), (xc[-1], y_r1)])
    for i, xx in enumerate(xc):
        leidning([(xx, y_r0), (xx, y_r0 + 5)])
        led(xx, y_r0 + 5, "", "")
        leidning([(xx, y_r0 + 10), (xx, y_r1)])
        if 0 < i < 3:
            node((xx, y_r0))
            node((xx, y_r1))
    A.tekst((xt - 5, y_r0 + 7.5), "06c", 3.0, anker="end", feit=True)
    A.tekst((xt - 5, y_r0 + 11.0), "4 x 25 mm", 2.0, anker="end")
    A.tekst((xt + 2, y_r1 + 4.5), "LED topp, %s, i parallell:" % (delar_tekst("06c_led_topp") or "COB 5 V"), 2.0, anker="start")
    A.tekst((xt + 2, y_r1 + 7.7), "bøylar for + og GND over skøytane (montering, steg M1)", 2.0, anker="start")
    leidning([(xt, y_r1), (xt, yg)])
    leidning([(x1 + 10, pinnar["SIDE+"]), (xs, pinnar["SIDE+"]), (xs, pinnar["SIDE+"] + 10)])
    led(xs, pinnar["SIDE+"] + 10, "06b", "LED side, %s" % (delar_tekst("06b_led_side") or "COB 5 V"), side=-1)
    leidning([(xs, pinnar["SIDE+"] + 15), (xs, yg)])
    leidning([(x1 + 10, yg), (xt, yg)])
    node((xs, yg))
    # grensa mellom chassis og lysmodul går gjennom X1; ho blir broten der teksten til X1 står
    xg = x1 + 5
    A.pl([(xg, 28), (24, 28), (24, 206), (xg, 206)], "d")
    A.pl([(xg, 28), (406, 28), (406, 206), (xg, 206)], "d")
    A.linje((xg, 28), (xg, ys[0] - 16), "d")
    A.linje((xg, yg + 17), (xg, 206), "d")
    A.tekst((27, 34), "03 Chassis (fast): 12 brytarar, 14 kretskort (F1, R1, R3), 13 TRS-kontakt", 2.4, anker="start")
    A.tekst((x1 + 9, 34), "06 Lysmodul (utskiftbar)", 2.4, anker="start")
    # tilstandstabell (B-rep)
    rader = [tuple(["θ °", "Opne spalter"] + ["SW%d" % (i + 1) for i in range(len(p.sw))] + ["Lys"])]
    tab = brytar_tabell(D, p)
    for th, opne, swst in tab:
        roller = [rolle for (idx, _m, _pl, rolle) in KOPLING if swst[idx]]
        rader.append(tuple([tal(th, 3), str(opne)] + ["slutta" if v else "open" for v in swst] + [", ".join(roller) or "av"]))
    sjekk["E01_stillingar"] = [{"theta": th, "opne_spalter": o_, "SW": s_} for th, o_, s_ in tab]
    A.tekst((26, 216), "Stillingar for hylsa (målt på B-rep: punktprøve i fotringen over kvar brytar og i hylsa framfor kvar spalte)",
            2.4, anker="start", feit=True)
    A.tabell(26, 219, [16, 22] + [16] * len(p.sw) + [40], rader, h=2.0, rh=4.4)
    A.tekstblokk((232, 214), [
        "Merknader",
        "1. Brytarane er kopla COM-NO: trykt brytar = slutta krets.",
        "    Kamspora i fotringen (05b) slepp brytarane.",
        "2. Tre parallelle vegar frå +5V: %s." % "; ".join(
            "SW%d%s til %s (%s)" % (idx + 1, (" + " + m) if m else "", pl, r) for idx, m, pl, r in KOPLING),
        "3. Brytartypar: %s." % "; ".join(namn),
        "4. Komponentverdiar (F1, R1, R3) og leidningar: sjå %s." % INNKJOP,
        "5. 06c: fire bitar i parallell, + ytst; bøylar over skøytane (+ ved 0/90/180°, GND ved 0/180/270°).",
    ], h=2.1, feit_forste=True)
    return A


# ============================================================================ DXF
def _dxf_ny():
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    doc.header["$INSUNITS"] = 4
    doc.header["$MEASUREMENT"] = 1
    doc.layers.add("SKJER", color=1)
    doc.layers.add("MERKNAD", color=3)
    return doc


def _forenkle(pts, tol=1e-4):
    if len(pts) < 3:
        return pts
    ln = LineString(list(pts) + [pts[0]]).simplify(tol, preserve_topology=False)
    c = list(ln.coords)
    return c[:-1] if len(c) > 1 and c[0] == c[-1] else c


def _tekst(msp, s, pos, h=3.0):
    t = msp.add_text(s, dxfattribs={"layer": "MERKNAD", "height": h})
    t.set_placement(pos)


def _dxf_region(msp, reg, z0):
    for ext in (list(reg.geoms) if hasattr(reg, "geoms") else [reg]):
        msp.add_lwpolyline([(x_, y_ - z0) for x_, y_ in _forenkle(list(ext.exterior.coords)[:-1])], close=True, dxfattribs={"layer": "SKJER"})
        for it in ext.interiors:
            msp.add_lwpolyline([(x_, y_ - z0) for x_, y_ in _forenkle(list(it.coords)[:-1])], close=True, dxfattribs={"layer": "SKJER"})


def dxf_hylse(reg, p, r_n, L, utsp):
    doc = _dxf_ny()
    msp = doc.modelspace()
    z0 = p.z_hylse_0
    _dxf_region(msp, reg, z0)
    H = p.z_hylse_1 - z0
    for a, b in (((0, -12), (40, -12)), ((40, -12), (36, -10.5)), ((40, -12), (36, -13.5))):
        msp.add_line(a, b, dxfattribs={"layer": "MERKNAD"})
    _tekst(msp, "VALSERETNING OG BORSTERETNING LANGS X (rundvalsing om aksen parallell med Y)", (44, -13.2), 3.0)
    _tekst(msp, "FYR 05 HYLSE  CuZn37 %s mm  flatlengd %s = pi x (%s - %s), noytralfiber r %s, K 0,5" % (
        tal(p.hylse_t), tal(L), tal(2 * p.r_ho), tal(p.hylse_t), tal(r_n)), (0, -20), 3.0)
    _tekst(msp, "Stumpskoyt pa x = 0 og x = %s: asimut %s grader (bak, mellom kronegruppene). "
           "x = ((asimut - %s) mod 360) x r_noytral." % (tal(L), tal(SAUM_HYLSE), tal(SAUM_HYLSE)), (0, -26), 3.0)
    _tekst(msp, "Sett fra utsida (borsta side). Mal i mm. %s %s" % (REV, DATO), (0, -32), 3.0)
    s0 = ((0.0 - SAUM_HYLSE) % 360.0) * DEG * r_n          # asimut 0° (framme) på nøytralfiberen
    msp.add_line((s0, H + 3), (s0, H + 10), dxfattribs={"layer": "MERKNAD"})
    _tekst(msp, "0 grader (framme)", (s0 + 1, H + 7), 2.5)
    for i, q in enumerate(utsp):
        cx = (q.bounds[0] + q.bounds[2]) / 2
        _tekst(msp, "U%d" % (i + 1), (cx - 1.5, q.bounds[3] - z0 + 1.0), 1.8)
    doc.saveas(PROD / "fyr_05_hylse_flatmonster.dxf")


def dxf_mantel(reg, p, Lu):
    doc = _dxf_ny()
    msp = doc.modelspace()
    z0 = p.z_mantel_0
    _dxf_region(msp, reg, z0)
    _tekst(msp, "FYR 04 MANTEL  utbretta ytterflate r %s (dokumentasjon; royrlaseren far STEP)" % tal(p.r_mo), (0, -12), 3.0)
    _tekst(msp, "Saum pa x = 0 og x = %s: asimut %s grader. x = (asimut - %s) x r. Sett utanfra." % (
        tal(Lu), tal(SAUM_MANTEL), tal(SAUM_MANTEL)), (0, -18), 3.0)
    _tekst(msp, "Skjeremal for pulverlakk; ferdig spalte 3,2. %s %s" % (REV, DATO), (0, -24), 3.0)
    s0 = ((0.0 - SAUM_MANTEL) % 360.0) * DEG * p.r_mo
    H = p.z_mantel_1 - z0
    msp.add_line((s0, H + 3), (s0, H + 10), dxfattribs={"layer": "MERKNAD"})
    _tekst(msp, "0 grader (framme)", (s0 + 1, H + 7), 2.5)
    doc.saveas(PROD / "fyr_04_mantel_utbretta.dxf")


def dxf_lok(lok, p, fil="fyr_08_lok.dxf", variant="serie"):
    doc = _dxf_ny()
    msp = doc.modelspace()
    bb = lok.BoundingBox()
    r = bb.xlen / 2
    msp.add_lwpolyline([(r, 0, 0, 0, 1), (-r, 0, 0, 0, 1)], format="xyseb", close=True, dxfattribs={"layer": "SKJER"})
    _tekst(msp, "FYR 08 LOK (%s)  PMMA opal 3 mm  D %s  laserskoren. %s %s" % (variant, tal(2 * r), REV, DATO), (-r, -r - 8), 3.0)
    doc.saveas(PROD / fil)
    return 2 * r


def dxf_lok_prototype():
    """Loket for prototypen (FyrParams.prototype(): tjukkare hylse -> mindre lok), same skjeremal som serien."""
    pp = g.FyrParams.prototype()
    return dxf_lok(form(g.lok(pp)), pp, "fyr_08_lok_prototype.dxf", "prototype")


# ============================================================================ sjølvkontroll av flatmønsteret
def kontroll_flatmonster(D, p):
    """Les DXF-en tilbake, rullar kvar utsparing opp att (x -> asimut) og finn same utsparing på B-rep
    ved punktprøving langs bogen på r_nøytral. Krav: avvik under 0,05°."""
    s = D["05_hylse"]
    r_n = (p.r_ho + p.r_hi) / 2
    doc = ezdxf.readfile(PROD / "fyr_05_hylse_flatmonster.dxf")
    pl = [e for e in doc.modelspace() if e.dxftype() == "LWPOLYLINE" and e.dxf.layer == "SKJER"]
    polys = [Polygon([(v[0], v[1]) for v in e.get_points("xy")]) for e in pl]
    ytre = max(polys, key=lambda q: q.area)
    indre = [q for q in polys if q is not ytre]
    ut = {"r_noytral": r_n, "flatlengd_dxf": round(ytre.bounds[2] - ytre.bounds[0], 4),
          "flatlengd_pi_x_(OD_minus_t)": round(math.pi * (2 * p.r_ho - p.hylse_t), 4),
          "hogd_dxf": round(ytre.bounds[3] - ytre.bounds[1], 4), "hogd_param": round(p.z_hylse_1 - p.z_hylse_0, 4),
          "skoyt_asimut": SAUM_HYLSE, "utsparingar": []}
    for i, q in enumerate(sorted(indre, key=lambda qq: qq.centroid.x)):
        cx = q.centroid.x
        cz = q.centroid.y + p.z_hylse_0
        a_dxf = SAUM_HYLSE + math.degrees(cx / r_n)

        def mat(a):
            return inni(s, (r_n * math.cos(a * DEG), r_n * math.sin(a * DEG), cz))
        kant = []
        for sg in (-1, 1):
            lo = hi = a_dxf
            step = 0.05
            while not mat(hi) and abs(hi - a_dxf) < 60:
                lo = hi
                hi = hi + sg * step
                step *= 1.5
            for _ in range(40):
                m = (lo + hi) / 2
                if mat(m):
                    hi = m
                else:
                    lo = m
            kant.append((lo + hi) / 2)
        a_3d = (kant[0] + kant[1]) / 2
        d = (a_dxf - a_3d + 180) % 360 - 180
        bredd_dxf = 0.0
        # breidd i DXF på same høgd
        ln = LineString([(q.bounds[0] - 1, q.centroid.y), (q.bounds[2] + 1, q.centroid.y)]).intersection(q)
        bredd_dxf = ln.length / r_n / DEG
        ut["utsparingar"].append({"nr": "U%d" % (i + 1), "x_senter_dxf": round(cx, 4),
                                  "asimut_frå_dxf": round((a_dxf + 180) % 360 - 180, 4),
                                  "asimut_3d_brep": round((a_3d + 180) % 360 - 180, 4), "avvik_grader": round(d, 5),
                                  "breidd_dxf_grader": round(bredd_dxf, 4), "breidd_3d_grader": round(abs(kant[1] - kant[0]), 4),
                                  "ok": bool(abs(d) < 0.05 and abs(bredd_dxf - abs(kant[1] - kant[0])) < 0.05)})
    ut["alle_ok"] = bool(all(u["ok"] for u in ut["utsparingar"]) and
                         abs(ut["flatlengd_dxf"] - ut["flatlengd_pi_x_(OD_minus_t)"]) < 0.01)
    return ut


# ============================================================================ hovud
ARK = [("T00", ark_T00), ("T01", ark_T01), ("T03", ark_T03), ("T04", ark_T04), ("T05", ark_T05), ("T05b", ark_T05b),
       ("T06", ark_T06), ("T07", ark_T07), ("T08", ark_T08), ("E01", ark_E01)]


def passing_kontroll(p):
    """Minste og største diametral klaring for funksjonspassingane med grenseavvika i TOL (negativ = overmål)."""
    def par(hol_d, hol_k, aks_d, aks_k):
        return (round(hol_d + tv(hol_k)[1] - (aks_d + tv(aks_k)[0]), 4), round(hol_d + tv(hol_k)[0] - (aks_d + tv(aks_k)[1]), 4))
    lo_id, hi_id = glide_montert_id(p)
    ut = {
        "05b bor / 03 tapp": par(2 * p.bor_r, "bor", 2 * p.tapp_ro, "tapp"),
        "05 hylse ID / 05b fotring": par(2 * p.r_hi, "hylse", 2 * (p.r_hi - 0.05), "fotring"),
        "04 mantel ID / 03 toppdekk": par(2 * p.r_mi, "mantel", 2 * p.toppdekk_r, "toppdekk"),
        "07 skjørt / 08 lok": par(2 * (p.r_rand_ut - p.skjort_t), "rist", 2 * p.r_lok, "lok"),
        "10 glidering montert ID / 05 hylse OD": (round(lo_id - (2 * p.r_ho + tv("hylse")[0]), 4),
                                                  round(hi_id - (2 * p.r_ho + tv("hylse")[1]), 4)),
        "04 mantel ID / 10 glidering fri OD (presspassing)": par(2 * p.r_mi, "mantel", 2 * p.r_mi, "glide_ut"),
    }
    ok = all(v[0] > 0 for k, v in ut.items() if "presspassing" not in k) and \
        ut["04 mantel ID / 10 glidering fri OD (presspassing)"][1] < 0
    return {"klaring_min_max": ut, "ok": bool(ok)}


def feilark(kode, tekst):
    A = Ark(kode, "FEIL ved generering", kode, "-", "-", "-")
    for i, l in enumerate(tekst.splitlines()[-40:]):
        A.tekst((26, 20 + i * 4.5), l[:170], 2.2, anker="start")
    return A


def main():
    t0 = time.time()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    berre = None
    if "--berre" in sys.argv:
        berre = set(sys.argv[sys.argv.index("--berre") + 1].split(","))
    UT.mkdir(parents=True, exist_ok=True)
    BUFFER.mkdir(parents=True, exist_ok=True)
    p = g.FyrParams()
    print("FYR teikningar · serie · buffer:", BUFFER, flush=True)
    D = bygg_data(p)
    sjekk = {"stykkliste_tal": {}}
    tot = len(ARK)
    for i, (kode, fn) in enumerate(ARK):
        if berre and kode not in berre:
            continue
        t = time.time()
        try:
            A = fn(D, p, sjekk)
        except Exception:  # noqa: BLE001
            tb = traceback.format_exc()
            print(tb, flush=True)
            HOPPA.append(f"{kode}: HEILE ARKET FEILA")
            A = feilark(kode, tb)
        svg = A.svg(i + 1, tot)
        (BUFFER / f"FYR_{kode}.svg").write_text(svg, encoding="utf-8")
        pdf = cairosvg.svg2pdf(bytestring=svg.encode("utf-8"))
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(UT / f"FYR_{kode}.png"), dpi=DPI)
        (BUFFER / f"FYR_{kode}.pdf").write_bytes(pdf)
        feil = [m for m in A.maallogg if abs(m[1] - m[2]) > 0.05]
        # mål som òg er prøvde mot B-rep (T00, T06): eit mål som ikkje held mot B-rep tel som avvik
        feil += [(r["tekst"], r["verdi_frå_FyrParams"], r["brep"] if r["brep"] is not None else float("nan"))
                 for r in sjekk.get(f"{kode}_maal_mot_brep", []) if not r["ok"]]
        sjekk.setdefault("maal_mot_geometri", {})[kode] = {
            "tal_maal": len(A.maallogg), "avvik": [{"tekst": a, "verdi": b, "papir": round(c, 3)} for a, b, c in feil]}
        sjekk.setdefault("visingar", {})[kode] = A.vis_bbox
        print(f"  ark {kode:5s} {time.time() - t:6.1f} s  mål: {len(A.maallogg)}  avvik: {len(feil)}", flush=True)
    if not berre:
        w = PdfWriter()
        for kode, _ in ARK:
            for pg in PdfReader(str(BUFFER / f"FYR_{kode}.pdf")).pages:
                w.add_page(pg)
        w.add_metadata({"/Title": "FYR produksjonsteikningar %s" % REV, "/Subject": "Seriegeometri, FyrParams()"})
        with open(UT / "FYR_teikningar.pdf", "wb") as fh:
            w.write(fh)
    if not berre or "T05" in berre:
        with valfri("kontroll flatmønster"):
            sjekk["flatmonster"] = kontroll_flatmonster(D, p)
            print("  flatmønster re-rulla:", "OK" if sjekk["flatmonster"]["alle_ok"] else "AVVIK", flush=True)
    sjekk["passingar"] = passing_kontroll(p)
    sjekk["hoppa_over"] = HOPPA
    sjekk["snitt_logg"] = SNITT_LOGG
    tekst = json.dumps(sjekk, indent=1, ensure_ascii=False, default=str)
    (BUFFER / "sjolvkontroll.json").write_text(tekst, encoding="utf-8")
    if not berre:   # heil køyring: sjølvkontrollen er dokumentasjon og ligg i repoet ved sida av dei andre kontrollane
        (ROT / "kontroll" / "fyr_teikning_sjolvkontroll.json").write_text(tekst, encoding="utf-8")
    if HOPPA:
        print("  hoppa over:", len(HOPPA), flush=True)
    print(f"ferdig på {time.time() - t0:.1f} s · {UT}", flush=True)


if __name__ == "__main__":
    main()
