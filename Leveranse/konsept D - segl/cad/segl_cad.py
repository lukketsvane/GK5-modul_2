# -*- coding: utf-8 -*-
"""
segl_cad.py  ·  Konsept D «Segl»: 3D-delane, samanstillinga og kontrollen

    python segl_cad.py            byggjer alle delar, kontrollerer og eksporterer (STEP, STL, JSON)
    python segl_cad.py kontroll   berre kontroll, ingen eksport

Mål og opphav står i segl_geometri.py. Utbrettingane (DXF) lagar segl_utbretta.py.
"""
import os, sys, json, math
import numpy as np
import cadquery as cq
from shapely.geometry import Polygon, box as sbox
from shapely import affinity

HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
import segl_geometri as G
from segl_geometri import T, RI, ZP, D01, D02, eining, V3

ROT = os.path.dirname(HER)
UT_CAD = HER
UT_PROD = os.path.join(ROT, 'produksjon')
UT_KONTROLL = os.path.join(ROT, 'kontroll')


# ------------------------------------------------------------------ hjelparar

def V(p):
    return cq.Vector(float(p[0]), float(p[1]), float(p[2]))


def flate(poly3d, hol=()):
    yt = cq.Wire.makePolygon([V(p) for p in poly3d], close=True)
    inn = [cq.Wire.makePolygon([V(p) for p in h], close=True) for h in hol]
    return cq.Face.makeFromWires(yt, inn)


def prisme(poly3d, retning, tjukk, hol=()):
    f = flate(poly3d, hol)
    return cq.Solid.extrudeLinear(f, V(np.asarray(retning, float) * tjukk))


def halvrom(p, n, L=3000.0):
    """Lekam som fyller {x : (x - p)·n >= 0} innanfor ein stor boks."""
    n = eining(n)
    a = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1.0, 0])
    u = eining(np.cross(n, a)); v = np.cross(n, u)
    p = np.asarray(p, float)
    hj = [p + L * (su * u + sv * v) for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return prisme(hj, n, L)


def kutt_halv(solid, p, n):
    """Behald den delen av solid der (x - p)·n >= 0."""
    return solid.intersect(halvrom(p, n))


def boy90(S, E, wdir, a, r=RI, t=T, ekstra=(0.0, 0.0), stubb=0.4):
    """Kvartring langs linja S-E på bordet. wdir: vassrett mot den liggjande plata.
    a: avstand langs wdir frå linja til flata på den ståande plata som vender bort frå den liggjande."""
    S = V3(S[0], S[1], 0); E = V3(E[0], E[1], 0)
    u = eining(E - S); w = eining(V3(wdir[0], wdir[1], 0)); z = V3(0, 0, 1)
    S0 = S - ekstra[0] * u
    L = np.linalg.norm(E - S) + ekstra[0] + ekstra[1]
    wc = a + r + t
    C = S0 + wc * w + (r + t) * z
    s2 = math.sqrt(0.5)
    y0 = C - (r + t) * w; ym = C - (r + t) * s2 * (w + z); y1 = C - (r + t) * z
    i0 = C - r * w; im = C - r * s2 * (w + z); i1 = C - r * z
    s0 = i0 + stubb * z; s1 = y0 + stubb * z     # stubb: den ståande plata held fram litt over bogen (overlapp)
    kantar = [cq.Edge.makeThreePointArc(V(y0), V(ym), V(y1)), cq.Edge.makeLine(V(y1), V(i1)),
              cq.Edge.makeThreePointArc(V(i1), V(im), V(i0)), cq.Edge.makeLine(V(i0), V(s0)),
              cq.Edge.makeLine(V(s0), V(s1)), cq.Edge.makeLine(V(s1), V(y0))]
    f = cq.Face.makeFromWires(cq.Wire.assembleEdges(kantar))
    return cq.Solid.extrudeLinear(f, V(u * L))


def avrund2d(pts, idx, r, n=10):
    """Byt hjørnet pts[idx] i ein 2D-polygon med ein boge med radius r."""
    pts = [np.asarray(p, float) for p in pts]
    P = pts[idx]; a = eining(pts[idx - 1] - P); b = eining(pts[(idx + 1) % len(pts)] - P)
    th = math.acos(np.clip(a.dot(b), -1, 1))
    d = r / math.tan(th / 2)
    ta, tb = P + d * a, P + d * b
    C = P + r / math.sin(th / 2) * eining(a + b)
    a0 = math.atan2(*(ta - C)[::-1]); a1 = math.atan2(*(tb - C)[::-1])
    da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    bue = [C + r * np.array([math.cos(a0 + da * i / n), math.sin(a0 + da * i / n)]) for i in range(n + 1)]
    return pts[:idx] + bue + pts[idx + 1:]


def poly_pts(pg):
    return [np.array(c) for c in list(pg.exterior.coords)[:-1]]


# ------------------------------------------------------------------ eit bretta segl som to prisme

def segl_omriss(s, tupp_rund=False):
    """2D-omrisset av dei to felta (utbretta, Q i origo), med avrunda topp og ev. avrunda låg spiss."""
    S, Q, A = s.til2d_v(s.S), np.zeros(2), s.til2d_v(s.A)
    B = s.til2d_h(s.B)
    bue, _ = s.bue_spiss()
    # bogen går frå hypotenusen (S-sida) til den loddrette kanten (B-sida)
    pts = [S, Q, B] + bue[::-1]
    if tupp_rund:
        pts = avrund2d(pts, 0, G.R_SPISS)
    return pts


def segl_lekam(s, omriss2d):
    """Lag to prisme frå 2D-omrisset, éitt per felt, gjæra langs falden."""
    pg = Polygon(omriss2d)
    n = s.n_c2 * s.sH            # peikar inn i høgre felt
    stor = 2000.0
    # halvplan med 1 mm overlapp forbi falden
    def halvplan(retn):
        t_ = np.array([-retn[1], retn[0]])
        p0 = -1.0 * retn
        return Polygon([p0 + stor * t_, p0 + stor * t_ + stor * retn, p0 - stor * t_ + stor * retn, p0 - stor * t_])
    del_h = pg.intersection(halvplan(n))
    del_v = pg.intersection(halvplan(-n))
    sol = []
    pV = eining((s.S - s.Q) - (s.S - s.Q).dot(s.c) * s.c)
    nb = eining(pV - s.pH)       # deler dei to felta langs halveringsplanet
    for d, til3d, norm, forteikn in ((del_v, s.til3d_v, s.nV, 1.0), (del_h, s.til3d_h, s.nH, -1.0)):
        p3 = [til3d(p) for p in poly_pts(d)]
        pr = prisme(p3, norm, T)
        pr = kutt_halv(pr, s.Q, forteikn * nb)
        sol.append(pr)
    return sol[0].fuse(sol[1]).clean()


# ------------------------------------------------------------------ D01 framseglet

def lag_d01():
    s = D01
    lek = segl_lekam(s, segl_omriss(s))
    uL = V3(1, 0, 0); uR = eining(V3(*(s.B2 - s.Q2), 0))
    wL = V3(0, -1, 0); wR = V3(uR[1], -uR[0], 0)          # mot brukaren (flensen)
    # bøyane
    bL = boy90((-2.0, 0.0), s.Q2, wL, -T, ekstra=(0, 3))
    bR = boy90(s.Q2, s.B2, wR, -T, ekstra=(3, 0))
    gjaer = eining(uL + uR)
    bL = kutt_halv(bL, s.Q, -gjaer)
    bR = kutt_halv(bR, s.Q, gjaer)
    # bøyen ved den låge spissen: berre under hypotenusen
    hyp = eining(s.A - s.S)
    n_hyp = eining(np.cross(hyp, s.nV))
    if n_hyp.dot(s.Q - s.S) < 0:
        n_hyp = -n_hyp
    bL = kutt_halv(bL, s.S, n_hyp)
    # flensane, gjæra med 1,2 mm glipe
    m = eining(wL + wR)                                   # gjæringslinja på bordet
    glipe = G.FLENS_GLIPE / 2
    # venstre flens i plan: x frå 0 til gjæringa, y frå -FLENS til -RI
    def gjaer_x(v):                                       # x på gjæringslinja i avstand v frå referanselinja
        return s.Q2[0] + m[0] / (-m[1]) * v
    vfl = [np.array([0.0, -G.FLENS]), np.array([gjaer_x(G.FLENS) - glipe, -G.FLENS]),
           np.array([gjaer_x(RI) - glipe, -RI]), np.array([0.0, -RI])]
    vfl = avrund2d(vfl, 0, G.R_HJORNE)
    # høgre flens: i sitt eige system (s langs, v ut)
    LR = np.linalg.norm(s.B2 - s.Q2)
    uR2, wR2 = uR[:2], wR[:2]
    s_gjaer = lambda v: m.dot(uR) / m.dot(wR) * v
    hfl_lok = [(s_gjaer(RI) + glipe, RI), (LR, RI), (LR, G.FLENS), (s_gjaer(G.FLENS) + glipe, G.FLENS)]
    hfl = [s.Q2 + a * uR2 + b * wR2 for a, b in hfl_lok]
    hfl = avrund2d(hfl, 2, G.R_HJORNE)
    # tunga under klampa
    x0, v0, v1 = G.TUNGE_KLAMPE
    tunge = [np.array([x0, -v1]), np.array([0.5, -v1]), np.array([0.5, -v0]), np.array([x0, -v0])]
    tunge = avrund2d(avrund2d(tunge, 3, 1.0), 0, 1.0)
    hol = [[(x + 1.45 * math.cos(a), y + 1.45 * math.sin(a), 0) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
           for x, y in G.KLAMPE_SKRUE]
    plan = lambda pts: [(p[0], p[1], 0.0) for p in pts]
    fl = prisme(plan(vfl), (0, 0, 1), T).fuse(prisme(plan(hfl), (0, 0, 1), T))
    tu = prisme(plan(tunge), (0, 0, 1), T, hol=hol)
    # senk for M2,5 DIN 965 nedanfrå
    for x, y in G.KLAMPE_SKRUE:
        kon = cq.Solid.makeCone(4.7 / 2 + 0.1, 0.0, 2.45, pnt=V((x, y, -0.05)), dir=V((0, 0, 1)))
        tu = tu.cut(kon)
    d = lek.fuse(bL).fuse(bR).fuse(fl).fuse(tu).clean()
    # relieff ved foten av falden: spalte 3 mm, 4 mm over bøyen, rund topp
    zt = ZP + 4.0 - 1.5
    sp = cq.Solid.makeBox(3.0, 8.0, zt + 1.0, pnt=V((s.Q2[0] - 1.5, -4.0, -1.0)))
    sp = sp.fuse(cq.Solid.makeCylinder(1.5, 8.0, pnt=V((s.Q2[0], -4.0, zt)), dir=V((0, 1, 0))))
    d = d.cut(sp)
    return d.clean()


# ------------------------------------------------------------------ D02 høgseglet med golv og leppe

def lag_d02():
    s = D02
    # omriss med relieff ved foten av falden på hovudfeltsida
    u = eining(V3(*(s.B2 - s.Q2), 0))
    Pa = s.Q + s.c * ((ZP + 0.5) / s.c[2])
    Pb = s.Qh + 1.5 * u + V3(0, 0, 0.5)
    Pc = s.Qh + 1.5 * u
    S, Q = s.til2d_v(s.S), np.zeros(2)
    B = s.til2d_h(s.B)
    bue, _ = s.bue_spiss()
    pts = [S, Q, s.til2d_h(Pa), s.til2d_h(Pb), s.til2d_h(Pc), B] + bue[::-1]
    pts = avrund2d(pts, 0, G.R_SPISS)
    lek = segl_lekam(s, pts)
    # golvbøyen langs hovudfeltet
    w = eining(s.inn)
    bg = boy90(s.Q2 + 1.5 * u[:2], s.B2, w[:2], 0.0)
    # golvet
    gp, y_fram, y_lepp = G.golv_punkt()
    gp = avrund2d(gp, 4, G.R_HJORNE)
    gp = avrund2d(gp, 3, G.R_HJORNE)
    hol = []
    golv = prisme([(p[0], p[1], 0) for p in gp], (0, 0, 1), T)
    # leppa: plan parallelt med innsida av D01 sitt venstre felt
    p0, n = G.leppe_plan()
    def paa_leppe(x, z):
        y = p0[1] - (z - p0[2]) * n[2] / n[1]
        return V3(x, y, z)
    x0, x1 = G.LEPP_X
    lp = [np.array([x0, ZP]), np.array([x1, ZP]), np.array([x1, G.LEPP_H]), np.array([x0, G.LEPP_H])]
    lp = avrund2d(avrund2d(lp, 3, G.R_HJORNE), 2, G.R_HJORNE)
    lhol = []
    for xb in G.BOLT_X:
        lhol.append([paa_leppe(xb + 2.5 * math.cos(a), G.BOLT_Z + 2.5 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 28, endpoint=False)])
    leppe = prisme([paa_leppe(p[0], p[1]) for p in lp], n, T, hol=lhol)
    bl = boy90((x0, 0.0), (x1, 0.0), (0, 1), y_lepp)
    d = lek.fuse(bg).fuse(golv).fuse(leppe).fuse(bl).clean()
    # rundt relieff i foten av falden (same som i utbrettinga)
    d = d.cut(cq.Solid.makeCylinder(G.MIN_SPALTE, 20.0, pnt=V(s.Q - 10.0 * s.nH), dir=V(s.nH)))
    return d.clean()


# ------------------------------------------------------------------ E01 lysmodulen

def lag_e01():
    t = G.AL_T
    y0, y1 = G.E01_BASE_Y
    zb = T                                       # botnen ligg på golvet
    s45 = math.sqrt(0.5)
    L = G.E01_SETE
    d_sete = np.array([-s45, s45]); n_sete = np.array([s45, s45])
    yt0 = np.array([y0, zb])                     # nedre ytre hjørne framme
    yt1 = yt0 + L * d_sete
    in0 = yt0 + t * n_sete
    # skjeringa mellom oversida av setet og toppen av botnen
    k = (zb + t - in0[1]) / d_sete[1]
    in_b = in0 + k * d_sete
    in1 = yt1 + t * n_sete
    prof = [yt0, np.array([y1, zb]), np.array([y1, zb + t]), in_b, in1, yt1]
    x0, x1 = G.E01_X
    p3 = [(x0, p[0], p[1]) for p in prof]
    berar = prisme(p3, (1, 0, 0), x1 - x0)
    # skjermleppa bak, berre der høgseglet ikkje skjermar
    sk = cq.Solid.makeBox(x1 - G.E01_SKJERM_X0, t, G.E01_SKJERM_H, pnt=V((G.E01_SKJERM_X0, y1 - t, zb + t)))
    # endeflikene: bretta 90° frå endane av setet, står opp langs normalen og dekkjer stripa sett langs V-en
    def flik(xp):
        q0 = in_b; q1 = in1
        pts = [q0, q1, q1 + G.E01_ENDE_H * n_sete, q0 + G.E01_ENDE_H * n_sete]
        return prisme([(xp, p[0], p[1]) for p in pts], (1, 0, 0), t)
    xs = G.E01_SKJERM_X0; zs = zb + t
    veng = cq.Solid.makeBox(t, G.E01_VENG_Y - y1, G.E01_SKJERM_H, pnt=V((xs, y1, zs)))          # bak mot høgseglet
    endevegg = cq.Solid.makeBox(t, y1 - t - 6.0, G.E01_SKJERM_H, pnt=V((x1 - t, 6.0, zs)))      # fram mot framseglet
    berar = berar.fuse(sk).fuse(flik(x0)).fuse(veng).fuse(endevegg)
    # spor for boltane
    for xb, yb in G.E01_BOLT:
        sp = cq.Solid.makeBox(8.0 - 5.0, 5.0, 10, pnt=V((xb - (8.0 - 5.0) / 2, yb - 2.5, 0)))
        sp = sp.fuse(cq.Solid.makeCylinder(2.5, 10, pnt=V((xb - (8.0 - 5.0) / 2, yb, 0))))
        sp = sp.fuse(cq.Solid.makeCylinder(2.5, 10, pnt=V((xb + (8.0 - 5.0) / 2, yb, 0))))
        berar = berar.cut(sp)
    berar = berar.clean()
    # LED-stripa på oversida av setet
    midt = in_b + 0.5 * (in1 - in_b)
    b2 = G.LED_B / 2
    sp0 = midt - b2 * d_sete; sp1 = midt + b2 * d_sete
    lx0, lx1 = G.LED_X
    strip = prisme([(lx0, sp0[0], sp0[1]), (lx0, sp1[0], sp1[1]), (lx1, sp1[0], sp1[1]), (lx1, sp0[0], sp0[1])],
                   (0, n_sete[0], n_sete[1]), G.LED_T)
    lys = dict(midt=(float((lx0 + lx1) / 2), float(midt[0] + n_sete[0] * G.LED_T), float(midt[1] + n_sete[1] * G.LED_T)),
               normal=(0.0, float(n_sete[0]), float(n_sete[1])), lengd=lx1 - lx0, breidd=G.LED_B,
               fremste_kant=(float(sp1[0]), float(sp1[1])), bakre_kant=(float(sp0[0]), float(sp0[1])))
    return berar, strip, lys


# ------------------------------------------------------------------ E02 klampa, E03 knappen, E04 kretskortet

KL_INNE_Y0 = -8.0                 # framveggen er 1,5 mm
PCB_TOPP = 6.2                    # sjå LES_MEG: knappen, aksellengd 20 og kragen avgjer
PCB_T = 1.6
PCB = (-32.5, -1.5, -3.5, 27.3)   # x0, y0, x1, y1


def lag_e02():
    x0, x1 = G.KL_X; y0, y1 = G.KL_Y; h = G.KL_H; v = G.KL_VEGG
    skal = cq.Solid.makeBox(x1 - x0, y1 - y0, h, pnt=V((x0, y0, 0)))
    hol = cq.Solid.makeBox(x1 - x0 - 2 * v, y1 - KL_INNE_Y0 - v, h - v + 1, pnt=V((x0 + v, KL_INNE_Y0, -1)))
    skal = skal.cut(hol)
    # ribbe over tunga med gjengar M2,5
    rib = cq.Solid.makeBox(x1 - x0 - 2 * v, -1.9 - KL_INNE_Y0, 6.0 - T, pnt=V((x0 + v, KL_INNE_Y0, T)))
    skal = skal.fuse(rib)
    # rom for tunga under ribba og under høgre vegg
    tx0, tv0, tv1 = G.TUNGE_KLAMPE
    skal = skal.cut(cq.Solid.makeBox(-tx0 + 0.5, tv1 - tv0 + 0.4, T + 0.1, pnt=V((tx0 - 0.2, -tv1 - 0.2, -0.1))))
    for x, y in G.KLAMPE_SKRUE:
        skal = skal.cut(cq.Solid.makeCylinder(1.05, 6.0, pnt=V((x, y, 0))))
    # bossar for kretskortet (M2 nedanfrå), frå toppen ned til kortet
    for bx, by in ((-30.5, 1.0), (-5.5, 1.0), (-30.5, 25.0), (-5.5, 25.0)):
        b = cq.Solid.makeCylinder(2.8, h - v - PCB_TOPP + 0.2, pnt=V((bx, by, PCB_TOPP)))   # 2,8: går 0,3 inn i veggen (ikkje tangent)
        b = b.cut(cq.Solid.makeCylinder(0.8, 6.0, pnt=V((bx, by, PCB_TOPP - 0.1))))
        skal = skal.fuse(b)
    # hol for akselkragen
    kx, ky = G.KNAPP_XY
    skal = skal.cut(cq.Solid.makeCylinder(3.7, 10, pnt=V((kx, ky, h - v - 1))))
    # USB-C i bakveggen: spalte 9,4 x 3,6 med runde endar, forsenka 13,0 x 7,0 x 1,2 utanfrå
    uz = PCB_TOPP + 1.58
    def avlang(bx, bz, djup, ypos):
        r = bz / 2
        k = cq.Solid.makeBox(bx - bz, djup, bz, pnt=V((kx - (bx - bz) / 2, ypos, uz - r)))
        k = k.fuse(cq.Solid.makeCylinder(r, djup, pnt=V((kx - (bx - bz) / 2, ypos, uz)), dir=V((0, 1, 0))))
        k = k.fuse(cq.Solid.makeCylinder(r, djup, pnt=V((kx + (bx - bz) / 2, ypos, uz)), dir=V((0, 1, 0))))
        return k
    skal = skal.cut(avlang(9.4, 3.6, 4.0, y1 - v - 1))
    skal = skal.cut(avlang(13.0, 7.0, 1.2 + 0.5, y1 - 1.2))
    # leidningen ut i høgre vegg, nede ved bordet
    skal = skal.cut(cq.Solid.makeBox(4.0, 3.4, 1.6, pnt=V((x1 - v - 1, 1.75, -0.1))))
    skal = skal.clean()
    # botnplata
    bp = cq.Solid.makeBox(x1 - x0 - 2 * v - 0.4, y1 - v - (-1.9) - 0.4, T, pnt=V((x0 + v + 0.2, -1.9 + 0.2, 0)))
    bp = bp.cut(cq.Solid.makeBox(4.6, 3.8, T + 1, pnt=V((x1 - v - 4.4, 1.55, -0.5))))
    return skal, bp


def lag_e03():
    kx, ky = G.KNAPP_XY
    z0 = G.KL_H + G.KNAPP_LUFT
    r = G.KNAPP_D / 2
    k = cq.Solid.makeCylinder(r, G.KNAPP_H, pnt=V((kx, ky, z0)))
    # rette riller: 48 V-spor, 0,35 djupe
    n = 48
    for i in range(n):
        a = 2 * math.pi * i / n
        c, s_ = math.cos(a), math.sin(a)
        tang = np.array([-s_, c])
        pr = np.array([kx + (r + 0.3) * c, ky + (r + 0.3) * s_])
        spiss = np.array([kx + (r - 0.35) * c, ky + (r - 0.35) * s_])
        w = 0.55
        tri = [(pr + w * tang), (pr - w * tang), spiss]
        k = k.cut(prisme([(p[0], p[1], z0 - 0.1) for p in tri], (0, 0, 1), G.KNAPP_H + 0.2))
    # fas på toppkanten
    k = cq.Workplane().add(k).faces('>Z').edges().chamfer(0.4).val()
    # D-hol for akselen nedanfrå: 6,05 med flate til 4,55, 6,5 djupt
    dh = cq.Solid.makeCylinder(3.025, 6.6, pnt=V((kx, ky, z0 - 0.01)))
    dh = dh.cut(cq.Solid.makeBox(10, 10, 10, pnt=V((kx - 5, ky + 4.55 - 3.025, z0 - 1))))
    k = k.cut(dh)
    return k.clean()


def lag_e04():
    """Kretskort med enkoder (Bourns PEC12R-4220F-S0024) og USB-C (GCT USB4125-GF-A). Forenkla."""
    x0, y0, x1, y1 = PCB
    kort = cq.Solid.makeBox(x1 - x0, y1 - y0, PCB_T, pnt=V((x0, y0, PCB_TOPP - PCB_T)))
    for bx, by in ((-30.5, 1.0), (-5.5, 1.0), (-30.5, 25.0), (-5.5, 25.0)):
        kort = kort.cut(cq.Solid.makeCylinder(1.1, 5, pnt=V((bx, by, PCB_TOPP - 3))))
    kx, ky = G.KNAPP_XY
    enk = cq.Solid.makeBox(12.4, 13.4, 6.1, pnt=V((kx - 6.2, ky - 6.7, PCB_TOPP)))
    krage = cq.Solid.makeCylinder(3.5, 5.0, pnt=V((kx, ky, PCB_TOPP + 6.1)))
    aksel = cq.Solid.makeCylinder(3.0, 20.0 - 11.1, pnt=V((kx, ky, PCB_TOPP + 11.1)))
    aksel = aksel.cut(cq.Solid.makeBox(10, 10, 8.0, pnt=V((kx - 5, ky + 4.5 - 3.0, PCB_TOPP + 20.0 - 7.0))))
    pinnar = cq.Solid.makeBox(10.0, 7.5 + 7.0, 1.9, pnt=V((kx - 5.0, ky - 7.5, PCB_TOPP - PCB_T - 1.9)))
    enk = enk.fuse(krage).fuse(aksel).fuse(pinnar)
    ub, uh, ud = 8.94, 3.16, 6.78
    uy0 = y1 + 0.58 - ud
    usb = cq.Solid.makeBox(ub - uh, ud, uh, pnt=V((kx - (ub - uh) / 2, uy0, PCB_TOPP)))
    for sx in (-1, 1):
        usb = usb.fuse(cq.Solid.makeCylinder(uh / 2, ud, pnt=V((kx + sx * (ub - uh) / 2, uy0, PCB_TOPP + uh / 2)), dir=V((0, 1, 0))))
    mcu = cq.Solid.makeBox(4.9, 3.9, 1.6, pnt=V((-30.0, 4.0, PCB_TOPP)))
    induktor = cq.Solid.makeBox(4.0, 4.0, 2.0, pnt=V((-10.5, 4.5, PCB_TOPP)))
    jst = cq.Solid.makeBox(4.5, 6.0, 4.0, pnt=V((-8.5, 15.0, PCB_TOPP)))
    return kort, enk, usb, mcu.fuse(induktor).fuse(jst)


# ------------------------------------------------------------------ innkjøpte smådelar

def bolt_cd(p, retn, lengd=8.0):
    """ISO 13918 PT M3: sveisebolt med flens Ø4,5 x 0,6."""
    retn = eining(retn)
    b = cq.Solid.makeCylinder(2.25, 0.6, pnt=V(p), dir=V(retn))
    return b.fuse(cq.Solid.makeCylinder(1.5, lengd, pnt=V(p), dir=V(retn)))


def mutter_m3(p, retn, h=3.7, nokkel=5.5, flens=(7.0, 0.8)):
    """DIN 6923 M3 flensmutter: sekskant 5,5 + flens Ø7,0."""
    retn = eining(retn)
    r = nokkel / math.sqrt(3)
    a = np.array([1.0, 0, 0]) if abs(retn[0]) < 0.9 else np.array([0, 1.0, 0])
    u = eining(np.cross(retn, a)); v = np.cross(retn, u)
    hex6 = [np.asarray(p) + r * (math.cos(k * math.pi / 3) * u + math.sin(k * math.pi / 3) * v) for k in range(6)]
    m = prisme(hex6, retn, h).fuse(cq.Solid.makeCylinder(flens[0] / 2, flens[1], pnt=V(p), dir=V(retn)))
    return m.cut(cq.Solid.makeCylinder(1.5, h + 2, pnt=V(np.asarray(p) - retn), dir=V(retn)))


def tommelmutter(p):
    m = cq.Solid.makeCylinder(4.0, 5.0, pnt=V(p))
    return m.cut(cq.Solid.makeCylinder(1.5, 7, pnt=V((p[0], p[1], p[2] - 1))))


def senkskrue(p, lengd, d=2.5, dk=4.7):
    """DIN 965, hovudet nedst (skrudd inn nedanfrå)."""
    k = cq.Solid.makeCone(dk / 2, d / 2, (dk - d) / 2, pnt=V(p), dir=V((0, 0, 1)))
    return k.fuse(cq.Solid.makeCylinder(d / 2, lengd, pnt=V(p), dir=V((0, 0, 1))))


def leidning():
    """Flat totrådsleidning 3,0 x 1,2 frå klampa inn i V-en og opp på golvet til starten av stripa."""
    w, h = 3.0, 1.2
    yc = 3.4
    a = cq.Solid.makeBox(36.0, w, h, pnt=V((-4.0, yc - w / 2, 0.0)))
    # skrått inn mot golvet, under setet
    p0 = np.array([32.0, yc]); p1 = np.array([40.5, 8.0])
    d = eining(p1 - p0); nn = np.array([-d[1], d[0]])
    sk = prisme([(*(p0 + w / 2 * nn), 0), (*(p1 + w / 2 * nn), 0), (*(p1 - w / 2 * nn), 0), (*(p0 - w / 2 * nn), 0)], (0, 0, 1), h)
    # opp på golvet og fram til kontakten
    c = cq.Solid.makeBox(3.0, w, h, pnt=V((40.0, 8.0 - w / 2, T)))
    kontakt = cq.Solid.makeBox(6.0, 4.5, 3.0, pnt=V((37.0, 8.0 - 2.25, T + h)))
    return a.fuse(sk).fuse(c), kontakt


# ------------------------------------------------------------------ samanstilling

MATERIAL = {
    'D01': ('DC01 1,5 mm, pulverlakk', 7.85), 'D02': ('DC01 1,5 mm, pulverlakk', 7.85),
    'E01': ('EN AW-5754 H22 1,5 mm', 2.66), 'E01-LED': ('LED-stripe (FPC + COB)', 2.2),
    'E02': ('EN AW-6082 fresa, pulverlakk', 2.70), 'E02-BOTN': ('EN AW-5754 1,5 mm', 2.66),
    'E03': ('EN AW-6082 dreia, pulverlakk', 2.70), 'E04': ('FR4 + komponentar', 2.2),
    'E04-ENK': ('Bourns PEC12R', 2.0), 'E04-USB': ('GCT USB4125', 4.0), 'E04-KOMP': ('komponentar', 2.5),
    'H01': ('sveisebolt M3x8 stål', 7.85), 'H02': ('flensmutter M3 DIN 6923 A2', 7.85), 'H03': ('sveisebolt M3x8 stål', 7.85),
    'H04': ('tommelmutter M3', 7.85), 'H05': ('senkskrue M2,5x6 DIN 965 A2', 7.9), 'H06': ('flat leidning 2x0,35 mm²', 3.0),
    'H07': ('JST PH 2-polar, inline', 1.4),
}

FARGE = {'D01': (0.62, 0.24, 0.16), 'D02': (0.62, 0.24, 0.16), 'E01': (0.75, 0.75, 0.77), 'E01-LED': (1.0, 0.92, 0.7),
         'E02': (0.62, 0.24, 0.16), 'E02-BOTN': (0.7, 0.7, 0.72), 'E03': (0.62, 0.24, 0.16), 'E04': (0.1, 0.35, 0.15),
         'E04-ENK': (0.2, 0.2, 0.2), 'E04-USB': (0.8, 0.8, 0.8), 'E04-KOMP': (0.15, 0.15, 0.15)}


def bygg():
    delar = {}
    delar['D01'] = lag_d01()
    delar['D02'] = lag_d02()
    berar, strip, lys = lag_e01()
    delar['E01'] = berar
    delar['E01-LED'] = strip
    skal, botn = lag_e02()
    delar['E02'] = skal
    delar['E02-BOTN'] = botn
    delar['E03'] = lag_e03()
    kort, enk, usb, komp = lag_e04()
    delar['E04'] = kort; delar['E04-ENK'] = enk; delar['E04-USB'] = usb; delar['E04-KOMP'] = komp
    # smådelar
    n01 = D01.nV
    bolt_d01 = None; mutt = None
    for xb in G.BOLT_X:
        # punkt på innsida av D01 sitt venstre felt i høgd BOLT_Z
        p = D01.Q + D01.nV * T
        e2 = D01.e2
        p = D01.til3d_v(np.array([xb - D01.Q[0], (G.BOLT_Z - ZP) / e2[2]])) + T * n01
        b = bolt_cd(p, n01)
        bolt_d01 = b if bolt_d01 is None else bolt_d01.fuse(b)
        mm = mutter_m3(p + n01 * (G.LEPP_LUFT + T), n01)
        mutt = mm if mutt is None else mutt.fuse(mm)
    delar['H01'] = bolt_d01
    delar['H02'] = mutt
    bolt_e01 = None; tm = None
    for xb, yb in G.E01_BOLT:
        b = bolt_cd((xb, yb, T), (0, 0, 1))
        bolt_e01 = b if bolt_e01 is None else bolt_e01.fuse(b)
        t_ = tommelmutter((xb, yb, T + G.AL_T))
        tm = t_ if tm is None else tm.fuse(t_)
    delar['H03'] = bolt_e01
    delar['H04'] = tm
    sk = None
    for x, y in G.KLAMPE_SKRUE:
        s_ = senkskrue((x, y, 0.0), 6.0)
        sk = s_ if sk is None else sk.fuse(s_)
    delar['H05'] = sk
    le, ko = leidning()
    delar['H06'] = le
    delar['H07'] = ko
    return delar, lys


# ------------------------------------------------------------------ kontroll

def kontroll(delar, lys):
    rap = {'eining': 'mm', 'delar': {}, 'kollisjonar': [], 'feil': []}
    masse = {}
    for k, sol in delar.items():
        ok = sol.isValid()
        vol = sol.Volume()
        bb = sol.BoundingBox()
        mat, rho = MATERIAL.get(k, ('?', 1.0))
        m = vol * rho / 1000.0
        masse[k] = m
        rap['delar'][k] = dict(gyldig=ok, volum_mm3=round(vol, 1), masse_g=round(m, 1), materiale=mat,
                               boks=[round(bb.xmin, 2), round(bb.ymin, 2), round(bb.zmin, 2), round(bb.xmax, 2), round(bb.ymax, 2), round(bb.zmax, 2)],
                               solids=len(sol.Solids()))
        if not ok or vol <= 0:
            rap['feil'].append(f'{k}: ugyldig eller tom lekam')
    # kollisjonar parvis (volum av snittet)
    namn = list(delar)
    tillate = {('E04-ENK', 'E04'), ('E04-USB', 'E04'), ('E04-KOMP', 'E04'), ('H01', 'D01'), ('H03', 'D02'),
               ('H01', 'H02'), ('H03', 'H04'), ('H05', 'E02'), ('E01-LED', 'E01')}
    for i in range(len(namn)):
        for j in range(i + 1, len(namn)):
            a, b = namn[i], namn[j]
            bba, bbb = delar[a].BoundingBox(), delar[b].BoundingBox()
            if (bba.xmax < bbb.xmin or bbb.xmax < bba.xmin or bba.ymax < bbb.ymin or bbb.ymax < bba.ymin
                    or bba.zmax < bbb.zmin or bbb.zmax < bba.zmin):
                continue
            try:
                v = delar[a].intersect(delar[b]).Volume()
            except Exception as e:
                v = -1
            if abs(v) > 1e-3:
                tl = (a, b) in tillate or (b, a) in tillate
                rap['kollisjonar'].append(dict(par=[a, b], volum_mm3=round(v, 4), tillate=tl))
    # tyngdepunkt og velting
    tot = 0.0; cg = np.zeros(3)
    for k, sol in delar.items():
        c = sol.Center()  # Center of mass for solids
        cm = cq.Shape.centerOfMass(sol)
        cg += masse[k] * np.array([cm.x, cm.y, cm.z]); tot += masse[k]
    cg /= tot
    rap['masse_g'] = round(tot, 1)
    rap['tyngdepunkt_mm'] = [round(v, 1) for v in cg]
    # støtteflata: alle punkt på bordet (z < 0,05) frå D01, D02, E02, E02-BOTN
    from shapely.geometry import MultiPoint
    pts = []
    for k in ('D01', 'D02', 'E02', 'E02-BOTN'):
        for v in delar[k].Vertices():
            if v.Z < 0.05:
                pts.append((v.X, v.Y))
    hull = MultiPoint(pts).convex_hull
    rap['fotavtrykk_cm2'] = round(hull.area / 100.0, 1)
    ring = list(hull.exterior.coords)
    from shapely.geometry import Point, LineString
    P = Point(cg[0], cg[1])
    kantar = []
    for i in range(len(ring) - 1):
        ls = LineString([ring[i], ring[i + 1]])
        if ls.length < 1.0:
            continue
        dist = ls.distance(P)
        kantar.append((dist, math.degrees(math.atan2(dist, cg[2])), ring[i], ring[i + 1]))
    kantar.sort()
    rap['velting'] = dict(innafor=hull.contains(P), minste_avstand_mm=round(kantar[0][0], 1),
                          minste_veltevinkel_grader=round(kantar[0][1], 1),
                          kant=[list(map(lambda v: round(v, 1), kantar[0][2])), list(map(lambda v: round(v, 1), kantar[0][3]))],
                          krav='15° (Northern-mål), 6° (EN 60598-2-4)')
    rap['hylster'] = [round(v, 1) for v in hull.exterior.coords[0]]
    rap['lys'] = lys
    return rap, hull


def eksporter(delar):
    os.makedirs(UT_PROD, exist_ok=True)
    os.makedirs(UT_KONTROLL, exist_ok=True)
    filnamn = {'D01': 'D01_framsegl', 'D02': 'D02_hogsegl', 'E01': 'E01_lysberar', 'E01-LED': 'E01_led_stripe',
               'E02': 'E02_klampe_skal', 'E02-BOTN': 'E02_klampe_botnplate', 'E03': 'E03_knapp', 'E04': 'E04_kretskort',
               'E04-ENK': 'E04_enkoder', 'E04-USB': 'E04_usb_c', 'E04-KOMP': 'E04_komponentar',
               'H01': 'H01_sveisebolt_D01', 'H02': 'H02_mutter', 'H03': 'H03_sveisebolt_golv', 'H04': 'H04_tommelmutter',
               'H05': 'H05_senkskrue', 'H06': 'H06_leidning', 'H07': 'H07_kontakt'}
    ass = cq.Assembly(name='segl')
    for k, sol in delar.items():
        cq.exporters.export(cq.Workplane().add(sol), os.path.join(UT_CAD, f'{filnamn[k]}.step'))
        if k in ('D01', 'D02', 'E01', 'E02', 'E02-BOTN', 'E03'):
            cq.exporters.export(cq.Workplane().add(sol), os.path.join(UT_PROD, f'{filnamn[k]}.stl'), tolerance=0.02, angularTolerance=0.1)
        f = FARGE.get(k, (0.6, 0.6, 0.6))
        ass.add(sol, name=filnamn[k], color=cq.Color(*f))
    ass.save(os.path.join(UT_CAD, 'segl_samanstilling.step'))
    return filnamn


if __name__ == '__main__':
    import time
    t0 = time.time()
    delar, lys = bygg()
    print('bygd', round(time.time() - t0, 1), 's')
    rap, hull = kontroll(delar, lys)
    rap['geometri'] = G.kontrolltal()
    print(json.dumps({k: rap[k] for k in ('masse_g', 'tyngdepunkt_mm', 'fotavtrykk_cm2', 'velting', 'kollisjonar', 'feil')}, indent=1, ensure_ascii=False))
    for k, v in rap['delar'].items():
        print(k, v['gyldig'], v['solids'], v['volum_mm3'], v['masse_g'], v['boks'])
    if 'kontroll' not in sys.argv:
        eksporter(delar)
        os.makedirs(UT_KONTROLL, exist_ok=True)
        json.dump(rap, open(os.path.join(UT_KONTROLL, 'segl_CAD_verifisering.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        print('eksportert', round(time.time() - t0, 1), 's')
