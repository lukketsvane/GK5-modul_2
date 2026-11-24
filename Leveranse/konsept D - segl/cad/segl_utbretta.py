# -*- coding: utf-8 -*-
"""
segl_utbretta.py  ·  utbretta plater for D01, D02, E01 og E02-BOTN

    python segl_utbretta.py

Skriv til ../produksjon/:
  <del>_utbretta.dxf   lag SKJER (kontur og hol), BOY (bøyelinjer), MERKE (sveisepunkt, gravert på baksida), TEKST
  boyetabell.csv      kvar bøy: del, nr, vinkel, retning, indre radius, bøyetillegg, lengd
  segl_mal_1til1.pdf  dei to segla 1:1 på A3 til ein papp-modell (skjer langs heil strek, bret langs stipla)

Bøyetillegget er rekna med K = 0,40 (ANTEKE). Den bretta STEP-fila er fasit; verkstaden reknar eiga utbretting.
"""
import os, sys, math, csv
import numpy as np
from shapely.geometry import Polygon, Point, LineString, box as sbox
from shapely.ops import unary_union
from shapely import affinity

HER = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HER)
import segl_geometri as G
from segl_geometri import T, RI, ZP, K, D01, D02, eining, V3
import segl_cad as C

UT = os.path.join(os.path.dirname(HER), 'produksjon')
BA = G.BA90
FL = G.FLENS - RI                     # flat flens etter tangenten


def P(pts):
    return Polygon([tuple(p) for p in pts]).buffer(0)


def lekk(pg, e=0.01):
    """Lukk hårfine sprekker der to delflater berre nesten møtest (flyttal), før relieff og avrunding."""
    return pg.buffer(e, join_style=2).buffer(-e, join_style=2)


def avrund_alt(pg, r=G.R_KANT):
    return pg.buffer(-r, join_style=1).buffer(r, join_style=1)


# ------------------------------------------------------------------ D01

def utbrett_d01():
    s = D01
    fasett = P(C.segl_omriss(s))
    S2 = s.til2d_v(s.S); A2 = s.til2d_v(s.A); B2 = s.til2d_h(s.B)
    # venstre bøy og flens (under Y = 0), frå hypotenusen sin forlenging
    dh = eining(A2 - S2)
    x_hb = S2[0] - BA * dh[0] / dh[1]
    boy_v = P([(x_hb, -BA), (0.0, -BA), (0.0, 0.0), tuple(S2)])
    tilflat_v = lambda x, v: (x - s.Q2[0], -BA - (v - RI))
    # venstre flens i plan (same som i 3D), gjæra
    uL = V3(1, 0, 0); uR = eining(V3(*(s.B2 - s.Q2), 0)); wL = V3(0, -1, 0); wR = V3(uR[1], -uR[0], 0)
    m = eining(wL + wR); glipe = G.FLENS_GLIPE / 2
    gjaer_x = lambda v: s.Q2[0] + m[0] / (-m[1]) * v
    vfl = [(0.0, G.FLENS), (gjaer_x(G.FLENS) - glipe, G.FLENS), (gjaer_x(RI) - glipe, RI), (0.0, RI)]
    flens_v = P([tilflat_v(x, v) for x, v in vfl])
    x0, v0, v1 = G.TUNGE_KLAMPE
    tunge = P([tilflat_v(x, v) for x, v in ((x0, v1), (0.5, v1), (0.5, v0), (x0, v0))])
    # høgre bøy og flens
    dr = eining(B2)
    nr = np.array([dr[1], -dr[0]])
    if nr.dot(A2) > 0:
        nr = -nr
    LR = np.linalg.norm(s.B2 - s.Q2)
    boy_h = P([(0, 0), tuple(B2), tuple(B2 + BA * nr), tuple(BA * nr)])
    s_gjaer = lambda v: m.dot(uR) / m.dot(wR) * v
    hfl = [(s_gjaer(RI) + glipe, RI), (LR, RI), (LR, G.FLENS), (s_gjaer(G.FLENS) + glipe, G.FLENS)]
    flens_h = P([tuple(a * dr + (BA + (v - RI)) * nr) for a, v in hfl])
    form = lekk(unary_union([fasett, boy_v, flens_v, tunge, boy_h, flens_h]))
    # relieff ved foten av falden: spalte 3,0 mm frå botnen av bøyen til 4 mm over, rund topp
    sp = unary_union([sbox(-1.5, -BA - 2.0, 1.5, 4.0 - 1.5), Point(0, 4.0 - 1.5).buffer(1.5, 32)])
    form = form.difference(sp)
    # glipa mellom flensane (frå bøyen og ut)
    form = avrund_alt(form)
    # hol: senka M2,5 i tunga
    hol = [Point(*tilflat_v(x, -y)).buffer(1.4, 32) for x, y in G.KLAMPE_SKRUE]
    for h in hol:
        form = form.difference(h)
    # bøyelinjer (midt i bøyesona)
    boy = [('B1', 'fotflens venstre', 90.0, 'ned (mot framsida)', LineString([(x_hb + 0.5, -BA / 2), (-1.5, -BA / 2)])),
           ('B2', 'fotflens høgre', 90.0, 'ned (mot framsida)', LineString([tuple(1.5 * dr + BA / 2 * nr), tuple(B2 + BA / 2 * nr)])),
           ('B3', 'falden', round(s.fald, 2), 'dal sett frå framsida', LineString([(0, 4.0), tuple(A2 - 6.0 * eining(A2))]))]
    merke = []
    for xb in G.BOLT_X:
        merke.append(np.array([xb - s.Q2[0], (G.BOLT_Z - ZP) / s.e2[2]]))
    return form, boy, merke, dict(lengd_flens=dict(venstre=float(s.Q2[0]), hogre=float(LR)))


# ------------------------------------------------------------------ D02

def utbrett_d02():
    s = D02
    u = eining(V3(*(s.B2 - s.Q2), 0)); w = eining(s.inn)
    Pa = s.Q + s.c * ((ZP + 0.5) / s.c[2]); Pb = s.Qh + 1.5 * u + V3(0, 0, 0.5); Pc = s.Qh + 1.5 * u
    S2, Q2 = s.til2d_v(s.S), np.zeros(2)
    B2 = s.til2d_h(s.B)
    bue, _ = s.bue_spiss()
    pts = [S2, Q2, s.til2d_h(Pa), s.til2d_h(Pb), s.til2d_h(Pc), B2] + bue[::-1]
    pts = C.avrund2d(pts, 0, G.R_SPISS)
    fasett = P(pts)
    # hovudbøyen: frå Pc til B i 2D, golvet under
    p0 = s.til2d_h(s.Qh); pB = B2
    d = eining(pB - p0)
    n = np.array([d[1], -d[0]])
    A2 = s.til2d_h(s.A)
    if n.dot(A2 - p0) > 0:
        n = -n
    Lh = np.linalg.norm(s.B2 - s.Q2)
    boy_g = P([tuple(p0 + 1.5 * d), tuple(pB), tuple(pB + BA * n), tuple(p0 + 1.5 * d + BA * n)])
    # golvet: plan -> flat er ei stiv rørsle. s langs u, w inn i V-en frå referanselinja
    def golv_flat(x, y):
        q = np.array([x, y]) - s.Q2
        a = q.dot(u[:2]); b = q.dot(w[:2])
        return tuple(p0 + a * d + (BA + (b - (RI + T))) * n)
    gp, y_fram, y_lepp = G.golv_punkt()
    golv = P([golv_flat(*p) for p in gp])
    # leppa: rulla ut vidare frå golvet sin framkant (mot lågare y i plan)
    alfa = math.degrees(math.atan2(-D01.nV[2], D01.nV[1]))       # leppa hallar som framseglet
    ba_l = math.radians(90.0 - abs(alfa)) * (RI + K * T)
    lh = (G.LEPP_H - ZP) / math.cos(math.radians(alfa))
    x0, x1 = G.LEPP_X
    yb0 = y_fram - ba_l                     # botnen av leppa i «utrulla plan»
    boy_l = P([golv_flat(x0, y_fram), golv_flat(x1, y_fram), golv_flat(x1, yb0), golv_flat(x0, yb0)])
    lp = [np.array([x0, yb0]), np.array([x1, yb0]), np.array([x1, yb0 - lh]), np.array([x0, yb0 - lh])]
    lp = C.avrund2d(C.avrund2d(lp, 3, G.R_HJORNE), 2, G.R_HJORNE)
    leppe = P([golv_flat(*p) for p in lp])
    form = lekk(unary_union([fasett, boy_g, golv, boy_l, leppe]))
    form = form.difference(Point(0.0, 0.0).buffer(G.MIN_SPALTE, 32))    # rundt relieff i foten av falden
    form = avrund_alt(form)
    for xb in G.BOLT_X:
        yv = yb0 - (G.BOLT_Z - ZP) / math.cos(math.radians(alfa))
        form = form.difference(Point(*golv_flat(xb, yv)).buffer(2.5, 48))
    boy = [('B1', 'golvet', 90.0, 'opp (inn i V-en)', LineString([tuple(p0 + 1.5 * d + BA / 2 * n), tuple(pB + BA / 2 * n)])),
           ('B2', 'leppa', round(90.0 - abs(alfa), 2), 'opp (mot framseglet)', LineString([golv_flat(x0, y_fram - ba_l / 2), golv_flat(x1, y_fram - ba_l / 2)])),
           ('B3', 'falden', round(s.fald, 2), 'dal sett frå innsida', LineString([tuple(s.til2d_h(Pa) + 2 * eining(A2)), tuple(A2 - 14.0 * eining(A2))]))]
    merke = [np.array(golv_flat(xb, yb)) for xb, yb in G.E01_BOLT]
    return form, boy, merke, dict(lengd_golvboy=float(Lh - 1.5))


# ------------------------------------------------------------------ E01 og E02-BOTN

def utbrett_e01():
    r, t = 1.5, G.AL_T
    ba90 = math.pi / 2 * (r + K * t); ba45 = math.pi / 4 * (r + K * t)
    sb45 = (r + t) * math.tan(math.radians(22.5)); sb90 = r + t
    y0, y1 = G.E01_BASE_Y
    base_u = (y1 - y0) - sb45                   # utan skjermleppe
    base_m = (y1 - y0) - sb45 - sb90            # med skjermleppe
    sete = G.E01_SETE - sb45
    skj = (G.E01_SKJERM_H + t) - sb90
    x0, x1 = G.E01_X
    xs = G.E01_SKJERM_X0
    # Y = 0 ved 45°-bøyen (midt), setet oppover, botnen nedover
    sete_p = sbox(x0, ba45 / 2, x1, ba45 / 2 + sete)
    b45 = sbox(x0, -ba45 / 2, x1, ba45 / 2)
    botn_u = sbox(x0, -ba45 / 2 - base_u, xs, -ba45 / 2)
    botn_m = sbox(xs, -ba45 / 2 - base_m, x1, -ba45 / 2)
    b90 = sbox(xs, -ba45 / 2 - base_m - ba90, x1, -ba45 / 2 - base_m)
    yl1 = -ba45 / 2 - base_m - ba90
    skjerm = sbox(xs, yl1 - skj, x1, yl1)
    # endeflikene: på endane av setet, bøygde 90° opp langs normalen til setet
    fl = G.E01_ENDE_H - sb90
    flik_v = sbox(x0 - ba90 - fl, ba45 / 2, x0, ba45 / 2 + sete)
    # vengen (venstre ende av skjermleppa, bak mot høgseglet) og endeveggen (høgre ende, fram)
    veng = sbox(xs - ba90 - (G.E01_VENG_Y - y1 - sb90 + t), yl1 - skj, xs, yl1)
    endev = sbox(x1, yl1 - skj, x1 + ba90 + (y1 - 6.0 - sb90), yl1)
    form = lekk(unary_union([sete_p, b45, botn_u, botn_m, b90, skjerm, flik_v, veng, endev]))
    form = avrund_alt(form)
    for xb, yb in G.E01_BOLT:
        yy = -ba45 / 2 - ((y1 - sb90 if xb > xs else y1) - yb) if False else -ba45 / 2 - (yb - (y0 + sb45))
        sp = unary_union([Point(xb - 1.5, yy).buffer(2.5, 32), Point(xb + 1.5, yy).buffer(2.5, 32), sbox(xb - 1.5, yy - 2.5, xb + 1.5, yy + 2.5)])
        form = form.difference(sp)
    boy = [('B1', 'setet', 45.0, 'opp', LineString([(x0, 0), (x1, 0)])),
           ('B2', 'skjermleppa', 90.0, 'opp', LineString([(xs, -ba45 / 2 - base_m - ba90 / 2), (x1, -ba45 / 2 - base_m - ba90 / 2)])),
           ('B3', 'endeflik venstre', 90.0, 'opp', LineString([(x0 - ba90 / 2, ba45 / 2), (x0 - ba90 / 2, ba45 / 2 + sete)])),
           ('B4', 'veng', 90.0, 'bak', LineString([(xs - ba90 / 2, yl1), (xs - ba90 / 2, yl1 - skj)])),
           ('B5', 'endevegg', 90.0, 'fram', LineString([(x1 + ba90 / 2, yl1), (x1 + ba90 / 2, yl1 - skj)]))]
    return form, boy, [], {}


def utbrett_botn():
    x0, x1 = G.KL_X; y0, y1 = G.KL_Y; v = G.KL_VEGG
    form = sbox(x0 + v + 0.2, -1.9 + 0.2, x1 - v - 0.2, y1 - v - 0.2)
    form = form.difference(sbox(x1 - v - 4.4, 1.55, x1 - v - 4.4 + 4.6, 1.55 + 3.8))
    return avrund_alt(form, 0.3), [], [], {}


# ------------------------------------------------------------------ DXF, tabell og papirmal

def skriv_dxf(namn, form, boy, merke, tekst):
    import ezdxf
    doc = ezdxf.new('R2010', setup=True)
    doc.units = ezdxf.units.MM
    for lag, farge in (('SKJER', 1), ('BOY', 2), ('MERKE', 3), ('TEKST', 7)):
        doc.layers.add(lag, color=farge)
    doc.layers.get('BOY').dxf.linetype = 'DASHED'
    msp = doc.modelspace()
    geoms = form.geoms if hasattr(form, 'geoms') else [form]
    for g in geoms:
        msp.add_lwpolyline(list(g.exterior.coords), close=True, dxfattribs={'layer': 'SKJER'})
        for r in g.interiors:
            msp.add_lwpolyline(list(r.coords), close=True, dxfattribs={'layer': 'SKJER'})
    for nr, kva, vinkel, retn, ls in boy:
        c = list(ls.coords)
        msp.add_line(c[0], c[-1], dxfattribs={'layer': 'BOY'})
        mid = ls.interpolate(0.5, normalized=True)
        msp.add_text(f'{nr} {vinkel:g}° {retn}', height=2.0, dxfattribs={'layer': 'TEKST'}).set_placement((mid.x + 2, mid.y + 2))
    for p in merke:
        msp.add_circle(tuple(p), 0.5, dxfattribs={'layer': 'MERKE'})
        msp.add_line((p[0] - 1.5, p[1]), (p[0] + 1.5, p[1]), dxfattribs={'layer': 'MERKE'})
        msp.add_line((p[0], p[1] - 1.5), (p[0], p[1] + 1.5), dxfattribs={'layer': 'MERKE'})
    b = form.bounds
    for i, l in enumerate(tekst):
        msp.add_text(l, height=2.5, dxfattribs={'layer': 'TEKST'}).set_placement((b[0], b[1] - 8 - 4 * i))
    doc.saveas(os.path.join(UT, f'{namn}_utbretta.dxf'))


def papirmal(former):
    """Dei to segla 1:1 på kvar si A3-side (PDF). Heil strek: skjer. Stipla: bret."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    A3 = (297 * mm, 420 * mm)
    c = canvas.Canvas(os.path.join(UT, 'segl_mal_1til1.pdf'), pagesize=A3)
    for namn, (form, boy, merke) in former.items():
        geoms = form.geoms if hasattr(form, 'geoms') else [form]
        b = form.bounds
        w, h = b[2] - b[0], b[3] - b[1]
        rot = w > 277 and h < 277
        sx = lambda x, y: ((y - b[1]) if rot else (x - b[0]), (-(x - b[0]) + w) if rot else (y - b[1]))
        ww, hh = (h, w) if rot else (w, h)
        ox, oy = (297 - ww) / 2, (420 - hh) / 2
        def tr(x, y):
            a, bb = sx(x, y)
            return (ox + a) * mm, (oy + bb) * mm
        c.setLineWidth(0.6)
        for g in geoms:
            for ring in [g.exterior] + list(g.interiors):
                pts = [tr(*p) for p in ring.coords]
                pa = c.beginPath(); pa.moveTo(*pts[0])
                for p in pts[1:]:
                    pa.lineTo(*p)
                pa.close(); c.drawPath(pa, stroke=1, fill=0)
        c.setDash(4, 3); c.setLineWidth(0.4)
        for nr, kva, vinkel, retn, ls in boy:
            (x0, y0), (x1, y1) = list(ls.coords)[0], list(ls.coords)[-1]
            c.line(*tr(x0, y0), *tr(x1, y1))
        c.setDash()
        c.setFont('Helvetica', 9)
        c.drawString(12 * mm, 12 * mm, f'{namn} 1:1  ·  heil strek: skjer  ·  stipla: bret  ·  skriv ut i faktisk storleik (100 %)')
        c.rect(12 * mm, 20 * mm, 50 * mm, 0.01 * mm)
        c.drawString(12 * mm, 22 * mm, 'kontroll: denne lina er 50 mm')
        c.showPage()
    c.save()


def main():
    os.makedirs(UT, exist_ok=True)
    rader = []
    former = {}
    for namn, fn, tekst in (
            ('D01_framsegl', utbrett_d01, ['D01 framsegl', 'DC01 1,5 mm, EN 10130', 'Ri 1,65 V10, K 0,40 (anteke)',
                                           'MERKE: sveisebolt ISO 13918 PT M3x8 på innsida (gravert på baksida)', 'senk 90° Ø4,9 for DIN 965 M2,5 frå undersida',
                                           'alle kantar avgrada, R0,3 til R0,5', 'pulverlakk fin struktur matt, RAL 8023 (prøveplate først)']),
            ('D02_hogsegl', utbrett_d02, ['D02 høgsegl med golv og leppe', 'DC01 1,5 mm, EN 10130', 'Ri 1,65 V10, K 0,40 (anteke)',
                                          'MERKE: sveisebolt ISO 13918 PT M3x8 opp frå golvet', 'ingen hol eller boltar i felta over golvet (lys med streifvinkel)',
                                          'pulverlakk fin struktur matt, RAL 8023']),
            ('E01_lysberar', utbrett_e01, ['E01 lysberar', 'EN AW-5754 H22 1,5 mm', 'Ri 1,5, K 0,40 (anteke)', 'naturleg eller klar anodisering']),
            ('E02_klampe_botnplate', utbrett_botn, ['E02 botnplate', 'EN AW-5754 H22 1,5 mm', 'senk for 2 x M2,5 DIN 965 etter boring']),
    ):
        form, boy, merke, info = fn()
        skriv_dxf(namn, form, boy, merke, tekst)
        b = form.bounds
        for nr, kva, vinkel, retn, ls in boy:
            rader.append(dict(del_=namn, nr=nr, kva=kva, vinkel_grader=vinkel, retning=retn,
                              indre_radius_mm=(1.5 if namn.startswith('E01') else RI), lengd_mm=round(ls.length, 1)))
        print(namn, 'flat', round(b[2] - b[0], 1), 'x', round(b[3] - b[1], 1), 'areal', round(form.area / 100, 1), 'cm2', 'gyldig', form.is_valid,
              'delar', len(form.geoms) if hasattr(form, 'geoms') else 1)
        if namn.startswith('D0'):
            former[namn] = (form, boy, merke)
    with open(os.path.join(UT, 'boyetabell.csv'), 'w', newline='', encoding='utf-8') as f:
        wr = csv.DictWriter(f, fieldnames=list(rader[0]))
        wr.writeheader(); wr.writerows(rader)
    papirmal(former)


if __name__ == '__main__':
    main()
