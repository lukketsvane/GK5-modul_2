"""Motor: seks konseptfrø som parametrar -> geometri, lyskjelder, massar.

Same oppstilling for alle (sjølvlagd premiss, sjå LESMEG):
bordkant y = 0, vegg y = 0.70, arbeidsfelt 0.6 x 0.4 m, auge 0.47 m over bordkanten,
lampefot i O, vend 27 grader inn mot brukaren (midt mellom feltsentrum og auge).
Lokale aksar: a = fram (F), b = side (S), c = opp (Z). Meter.
"""
import numpy as np

rad = np.radians
Z = np.array([0.0, 0.0, 1.0])
O = np.array([-0.45, 0.40, 0.0])
_f = rad(-27.0)
F = np.array([np.cos(_f), np.sin(_f), 0.0])
S = np.cross(Z, F)
FELT = (-0.30, 0.30, 0.10, 0.50)          # x0, x1, y0, y1
AUGE = np.array([0.0, 0.0, 0.47])
BORD = (-1.05, 0.85, 0.0, 0.70)           # x0, x1, y0, y1
VEGG_Y = 0.70
VEGG = (-1.45, 0.85, 0.0, 1.5)            # x0, x1, z0, z1


def W(a, b, c):
    return O + a * F + b * S + c * Z


def V(a, b, c):
    return a * F + b * S + c * Z


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def ortho1(n):
    n = unit(n)
    a = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1.0, 0])
    u = unit(np.cross(n, a))
    return u, np.cross(n, u)


# ---- delar ---------------------------------------------------------------
def cyl(p0, p1, r, mat, mat1=None, mat0=None):
    return dict(k='cyl', p0=np.array(p0, float), p1=np.array(p1, float), r=r, mat=mat,
                mat1=mat1 or mat, mat0=mat0 or mat, opt=None)


def skive(c, n, r, t, mf, mb, kant='kropp'):
    """Tynn skive. Framsida (mf) vender langs n. Optisk tosidig flate i c."""
    n = unit(n)
    u, v = ortho1(n)
    return dict(k='cyl', p0=c - n * t / 2, p1=c + n * t / 2, r=r, mat=kant, mat1=mf, mat0=mb,
                opt=dict(kind='disc', c=np.array(c, float), n=n, u=u, v=v, r=r, mf=mf, mb=mb))


def holspegel(c, n, r, R, t, mf, mb):
    """Sfærisk holspegel: toppunkt c, akse n mot den hole sida. Teikna som flat skive."""
    n = unit(n)
    u, v = ortho1(n)
    return dict(k='cyl', p0=c - n * t, p1=c, r=r, mat='kropp', mat1=mf, mat0=mb,
                opt=dict(kind='cap', c=np.array(c, float), n=n, u=u, v=v, r=r, R=R, cs=c + n * R,
                         cosa=np.sqrt(1 - (r / R) ** 2), mf=mf, mb=mb))


def plate(c, n, u, hu, hv, t, mf, mb, kant='kropp', optisk=True):
    n = unit(n)
    u = unit(u)
    v = np.cross(n, u)
    o = dict(kind='rect', c=np.array(c, float), n=n, u=u, v=v, hu=hu, hv=hv, mf=mf, mb=mb) if optisk else None
    return dict(k='box', c=np.array(c, float), ax=np.array([u, v, n]), h=np.array([hu, hv, t / 2]),
                mat=kant, mat1=mf, mat0=mb, opt=o)


def boks(c, ax, h, mat):
    return dict(k='box', c=np.array(c, float), ax=np.array([unit(a) for a in ax]), h=np.array(h, float),
                mat=mat, mat1=mat, mat0=mat, opt=None)


def boge(p0, pc, p1, r, mat, n=16):
    t = np.linspace(0, 1, n + 1)[:, None]
    P = (1 - t) ** 2 * p0 + 2 * t * (1 - t) * pc + t ** 2 * p1
    return [cyl(P[i], P[i + 1], r, mat) for i in range(n)]


# ---- lyskjelder (lm blir sett av kjor.py) -----------------------------------
def spot(p, d, half, r=0.0045):
    return dict(k='spot', p=np.array(p, float), d=unit(d), half=rad(half), r=r, lm=100.0)


def panel_skive(c, n, r, prisme=None):
    n = unit(n)
    u, v = ortho1(n)
    return dict(k='panel', shape='disc', c=np.array(c, float), n=n, u=u, v=v, r=r, A=np.pi * r * r,
                prisme=None if prisme is None else unit(prisme), lm=100.0)


def panel_rekt(c, n, u, hu, hv, prisme=None):
    n = unit(n)
    u = unit(u)
    return dict(k='panel', shape='rect', c=np.array(c, float), n=n, u=u, v=np.cross(n, u), hu=hu, hv=hv,
                A=4 * hu * hv, prisme=None if prisme is None else unit(prisme), lm=100.0)


def lysstav(p0, p1, akse, side, a0=5.0, a1=58.0):
    return dict(k='rod', p0=np.array(p0, float), p1=np.array(p1, float), akse=unit(akse), side=unit(side),
                a0=rad(a0), a1=rad(a1), lm=100.0)


def sirkel(a, b, r, n=32):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.c_[a + r * np.cos(t), b + r * np.sin(t)]


MODUSAR = ('stemning', 'arbeid', 'mote')


# ---- frø ---------------------------------------------------------------------
def rull(modus, **kw):
    """Knekt plate, to stolpar, laus lysstav som blir rulla mellom eigen vegg og bordet."""
    psi = rad(kw.get('psi', 15.0 if modus == 'arbeid' else -70.0))   # linseakse frå loddrett ned, + er fram
    D = [plate(W(-0.095, 0, 0.0015), Z, F, 0.095, 0.13, 0.003, 'kropp', 'kropp'),
         plate(W(-0.075, 0, 0.130), V(0.866, 0, 0.5), S, 0.13, 0.15, 0.003, 'kvit', 'kropp'),
         cyl(W(0, -0.125, 0), W(0, -0.125, 0.35), 0.003, 'staal'),
         cyl(W(0, 0.125, 0), W(0, 0.125, 0.35), 0.003, 'staal'),
         cyl(W(0, -0.125, 0.35), W(0, 0.125, 0.35), 0.0125, 'kropp'),
         cyl(W(0, 0.125, 0.35), W(0, 0.140, 0.35), 0.009, 'messing'),
         cyl(W(-0.165, -0.11, 0.0155), W(-0.165, -0.01, 0.0155), 0.0125, 'kropp'),
         cyl(W(-0.165, 0.01, 0.0155), W(-0.165, 0.11, 0.0155), 0.0125, 'kropp')]
    akse = V(np.sin(psi), 0, -np.cos(psi))
    side = V(np.cos(psi), 0, np.sin(psi))
    Lk = [lysstav(W(0, -0.115, 0.35) + 0.0125 * akse, W(0, 0.115, 0.35) + 0.0125 * akse, akse, side)]
    M = [(0.516, (-0.095, 0, 0.092)), (0.154, (0, 0, 0.175)), (0.140, (0, 0, 0.35)),
         (0.105, (-0.165, 0, 0.02)), (0.075, (-0.12, 0, 0.015))]
    base = np.array([[-0.19, -0.13], [0, -0.13], [0, 0.13], [-0.19, 0.13]])
    return dict(namn='Rull', linse='laga', delar=D, lys=Lk, masse=M, base=base, eta=80.0, vipp=None)


def vend_l(modus, **kw):
    """Laga-Vend: alt elektrisk i foten, bogestamme, skive med kvit og halvblank side."""
    arbeid = modus == 'arbeid'
    th = rad(kw.get('vipp', 21.0 if arbeid else 45.0))
    nd = V(np.sin(th), 0, -np.cos(th))                      # sida som vender ned
    Cd = W(0, 0, 0.46)
    D = [cyl(W(0, 0, 0), W(0, 0, 0.04), 0.075, 'kropp'),
         cyl(W(0, 0, 0.04), W(0, 0, 0.07), 0.025, 'kropp', mat1='svart'),
         cyl(W(0.068, 0, 0.02), W(0.081, 0, 0.02), 0.012, 'messing'),
         skive(Cd, nd, 0.14, 0.003, 'halvblank' if arbeid else 'kvit', 'kvit' if arbeid else 'halvblank'),
         cyl(W(0, 0.14, 0.46), W(0, 0.158, 0.46), 0.004, 'kropp')]
    D += boge(W(0, 0.072, 0.035), W(0, 0.26, 0.20), W(0, 0.155, 0.46), 0.005, 'kropp')
    Lk = [spot(W(0, 0, 0.07), Z, 18.0)]
    M = [(0.79, (0, 0, 0.025)), (0.148, (0, 0.19, 0.24)), (0.25, (0, 0, 0.46))]
    return dict(namn='Vend L', linse='laga', delar=D, lys=Lk, masse=M, base=sirkel(0, 0, 0.075), eta=80.0,
                vipp=np.degrees(th))


def vend_r(modus, **kw):
    """Reflektor-Vend: lykt i brønn framme i foten, gaffel, skive med matt og satinert side."""
    arbeid = modus == 'arbeid'
    th = rad(kw.get('vipp', 24.0 if arbeid else 55.0))
    nd = V(np.sin(th), 0, -np.cos(th))
    Cd = W(0, 0, 0.385)
    D = [cyl(W(-0.03, 0, 0), W(-0.03, 0, 0.056), 0.056, 'kropp'),
         cyl(W(0, 0, 0.0562), W(0, 0, 0.0566), 0.022, 'svart'),
         cyl(W(0.026, 0, 0.03), W(0.036, 0, 0.03), 0.010, 'messing'),
         cyl(W(-0.085, 0, 0.05), W(-0.085, 0, 0.25), 0.004, 'kropp'),
         cyl(W(-0.085, 0, 0.25), W(0, -0.135, 0.385), 0.003, 'kropp'),
         cyl(W(-0.085, 0, 0.25), W(0, 0.135, 0.385), 0.003, 'kropp'),
         cyl(W(0, -0.137, 0.385), W(0, -0.125, 0.385), 0.003, 'kropp'),
         cyl(W(0, 0.125, 0.385), W(0, 0.137, 0.385), 0.003, 'kropp'),
         skive(Cd, nd, 0.125, 0.003, 'satin' if arbeid else 'kvit', 'kvit' if arbeid else 'satin')]
    Lk = [spot(W(0, 0, 0.02), Z, 14.0)]
    M = [(0.85, (-0.03, 0, 0.028)), (0.081, (-0.06, 0, 0.22)), (0.219, (0, 0, 0.385))]
    return dict(namn='Vend R', linse='reflektoren', delar=D, lys=Lk, masse=M, base=sirkel(-0.03, 0, 0.056),
                eta=80.0, vipp=np.degrees(th))


def perle(modus, **kw):
    """Perle: lyskjelda glir på to skinner under ein satinert holspegel."""
    mote = modus == 'mote'
    th = rad(kw.get('vipp', 45.0 if mote else 24.0))
    under = kw.get('under', 0.38 if mote else 0.18)          # perla under spegelen
    cb = 0.435 - under
    nd = V(np.sin(th), 0, -np.cos(th))
    D = [cyl(W(0, 0, 0), W(0, 0, 0.035), 0.065, 'kropp'),
         cyl(W(0, 0, 0.035), W(0, 0, 0.041), 0.02, 'messing'),
         cyl(W(0, -0.008, 0.035), W(0, -0.008, 0.433), 0.0025, 'staal'),
         cyl(W(0, 0.008, 0.035), W(0, 0.008, 0.433), 0.0025, 'staal'),
         cyl(W(0, 0, cb - 0.021), W(0, 0, cb + 0.021), 0.028, 'kropp', mat1='svart'),
         holspegel(W(0, 0, 0.435), nd, 0.12, 0.52, 0.003, 'satin', 'kropp')]
    Lk = [spot(W(0, 0, cb + 0.021), Z, 30.0)]
    M = [(0.70, (0, 0, 0.018)), (0.123, (0, 0, 0.235)), (0.167, (0, 0, cb)), (0.188, (0, 0, 0.435))]
    return dict(namn='Perle', linse='reflektoren', delar=D, lys=Lk, masse=M, base=sirkel(0, 0, 0.065),
                eta=80.0, vipp=np.degrees(th))


def klaff(modus, **kw):
    """Klaff: flat lysskive hengsla i kanten på toppen av stamma. Vinkelen er dimmaren."""
    th = rad(kw.get('vinkel', dict(stemning=40.0, mote=180.0, arbeid=270.0)[modus]))
    d = V(-np.sin(th), 0, -np.cos(th))                       # hengsel -> skivesentrum
    nf = V(-np.cos(th), 0, np.sin(th))                       # lysande side
    H = W(0, 0, 0.40)
    Cd = H + 0.135 * d
    D = [cyl(W(0, 0, 0), W(0, 0, 0.03), 0.08, 'kropp'),
         cyl(W(0, 0, 0.03), W(0, 0, 0.40), 0.006, 'kropp'),
         cyl(W(0, -0.02, 0.40), W(0, 0.02, 0.40), 0.009, 'kropp'),
         cyl(W(0, 0.02, 0.40), W(0, 0.03, 0.40), 0.008, 'messing'),
         skive(Cd, nf, 0.125, 0.022, 'opalflate', 'kropp')]
    D[-1]['lys'] = 0
    Lk = [panel_skive(Cd + 0.0112 * nf, nf, 0.125, prisme=d)]
    la = 0.135 * np.array([-np.sin(th), 0, -np.cos(th)]) + np.array([0, 0, 0.40])
    M = [(0.60, (0, 0, 0.015)), (0.10, (0, 0, 0.215)), (0.35, tuple(la))]
    return dict(namn='Klaff', linse='flata', delar=D, lys=Lk, masse=M, base=sirkel(0, 0, 0.08), eta=80.0, vipp=None)


def tavle(modus, **kw):
    """Tavle: laus, kantbelyst lystavle og ein passiv stolpe med tapp."""
    D = [cyl(W(0, 0, 0), W(0, 0, 0.008), 0.07, 'kropp'),
         cyl(W(0, 0, 0.008), W(0, 0, 0.345), 0.005, 'kropp'),
         cyl(W(0, 0, 0.345), W(0, 0, 0.373), 0.004, 'messing')]
    M = [(0.50, (0, 0, 0.004)), (0.10, (0, 0, 0.18))]
    if modus == 'arbeid':        # ligg på tappen, lysflata ned
        D += [boks(W(0, 0, 0.36), (F, S, Z), (0.015, 0.13, 0.015), 'kropp'),
              plate(W(0.110, 0, 0.349), -Z, S, 0.125, 0.095, 0.008, 'opalflate', 'kropp')]
        Lk = [panel_rekt(W(0.110, 0, 0.3448), -Z, S, 0.125, 0.095)]
        M += [(0.29, (0, 0, 0.36)), (0.30, (0.110, 0, 0.349))]
    elif modus == 'mote':        # står på tappen, lysflata fram
        D += [boks(W(0, 0, 0.36), (F, S, Z), (0.015, 0.13, 0.015), 'kropp'),
              plate(W(0, 0, 0.47), F, S, 0.125, 0.095, 0.008, 'opalflate', 'kropp')]
        Lk = [panel_rekt(W(0.0042, 0, 0.47), F, S, 0.125, 0.095)]
        M += [(0.29, (0, 0, 0.36)), (0.30, (0, 0, 0.47))]
    else:                        # laus: står på ryggen 10 cm frå veggen bak skjermen, lyser mot veggen
        P0 = np.array([-0.10, 0.60, 0.0])
        X, Y = np.array([1.0, 0, 0]), np.array([0, 1.0, 0])
        D += [boks(P0 + Z * 0.015, (Y, X, Z), (0.015, 0.13, 0.015), 'kropp'),
              plate(P0 + Z * 0.125, Y, X, 0.125, 0.095, 0.008, 'opalflate', 'kropp')]
        Lk = [panel_rekt(P0 + Z * 0.125 + Y * 0.0042, Y, X, 0.125, 0.095)]
    D[-1]['lys'] = 0
    return dict(namn='Tavle', linse='flata', delar=D, lys=Lk, masse=M, base=sirkel(0, 0, 0.07), eta=65.0,
                vipp=None, laus=modus == 'stemning')


FRO = dict(rull=rull, vend_l=vend_l, vend_r=vend_r, perle=perle, klaff=klaff, tavle=tavle)


def laptop():
    c15, s15 = np.cos(rad(15)), np.sin(rad(15))
    X = np.array([1.0, 0, 0])
    return [plate(np.array([0, 0.33, 0.0135]), Z, X, 0.16, 0.11, 0.003, 'laptop', 'laptop'),
            boks(np.array([0, 0.33, 0.006]), (X, np.array([0, 1.0, 0]), Z), (0.16, 0.11, 0.006), 'laptop'),
            plate(np.array([0, 0.44 + 0.105 * s15, 0.015 + 0.105 * c15]), np.array([0, -c15, s15]), X,
                  0.16, 0.105, 0.006, 'skjerm', 'laptop')]


def kropp(sc):
    """Masse, tyngdepunkt, veltevinkel (mot konvekst hylster av golvkontakten), utstrekning."""
    m = sum(x[0] for x in sc['masse'])
    g = sum(x[0] * np.array(x[1]) for x in sc['masse']) / m
    P = sc['base']
    c = P.mean(0)
    best = 1e9
    for i in range(len(P)):
        p, q = P[i], P[(i + 1) % len(P)]
        e = q - p
        nrm = np.array([e[1], -e[0]]) / np.linalg.norm(e)
        if nrm @ (c - p) > 0:
            nrm = -nrm
        best = min(best, -nrm @ (g[:2] - p))            # avstand innanfor kanten (negativ = utanfor)
    velt = np.degrees(np.arctan2(best, g[2]))
    pts = []
    for d in sc['delar']:
        if d['k'] == 'cyl':
            for p in (d['p0'], d['p1']):
                pts += [p + d['r'] * np.array(v) for v in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]
        else:
            for sx in (-1, 1):
                for sy in (-1, 1):
                    for sz in (-1, 1):
                        pts.append(d['c'] + (np.array([sx, sy, sz]) * d['h']) @ d['ax'])
    pts = np.array(pts)
    xy = pts[:, :2]
    dia = max(np.linalg.norm(xy[i] - xy, axis=1).max() for i in range(0, len(xy), 3))
    e = P - np.roll(P, 1, axis=0)
    areal = 0.5 * abs(np.sum(P[:, 0] * np.roll(P[:, 1], 1) - np.roll(P[:, 0], 1) * P[:, 1]))
    return dict(masse=m, tp_hogd=g[2], velt=velt, hogd=pts[:, 2].max(), breidd=dia, fot_cm2=areal * 1e4)
