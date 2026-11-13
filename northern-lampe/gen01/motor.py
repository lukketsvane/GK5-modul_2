"""Northern-lampe · parametrisk formsøk · gen 01 «Rull»  (2026-11-13)

Grep: lyset bur i ei hylse som roterer om éin akse. Vriding = overgangen arbeid <-> stemning.
Motor: sylinderhylse (K=0) med opning, på rett ryggrad, + støtte (portal, utkrag, T, vugge, lene).
Rekna fridomsgrad: vridvinkelen phi (eitt tal per modus). Resten er identitet.
Køyr: python motor.py  ->  brett.png, kontroll.png, tal.csv, tal.md, kroppar/*.png
"""
import os, math, csv
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from scipy.spatial import ConvexHull
from skimage.draw import polygon as skpoly
from skimage.morphology import convex_hull_image

HER = os.path.dirname(os.path.abspath(__file__))
G = 9.81

# ---------------- premissar (m, lm, W) — sjå logg.md ----------------
DESK = (-0.70, 0.70, 0.0, 0.75)                     # bordplate; vegg ved y = 0.75
WALL_Y = 0.75
SCR = dict(x0=-0.275, x1=0.275, y=0.45, z0=0.10, z1=0.42)
EYES = np.array([[0.0, -0.30, 0.45], [-0.15, -0.30, 0.45], [0.15, -0.30, 0.45]])
_tx, _ty = np.meshgrid(np.linspace(-0.30, 0.30, 7), np.linspace(0.05, 0.40, 5))
TASK = np.c_[_tx.ravel(), _ty.ravel(), np.zeros(_tx.size)]
FORBID = (-0.30, 0.30, 0.0, 0.50, 0.0, 0.50)         # siktline, skjerm, hender
ANCHOR = {'side': (-0.50, 0.40), 'over': (0.0, 0.40), 'arm': (-0.60, 0.30)}   # 'bak' (0,0.62) forkasta: skjermen skuggar alt
E_TASK, U0_MIN, L_MAX = 500.0, 0.40, 3000.0         # lx, -, cd/m2 (EN 12464-1)
E_FACE = 150.0                                      # lx vertikalt, videomøte
RHO, LM_W = 0.85, 100.0
H_CONV, DT = 10.0, 30.0
T_DET, F_PUSH = 0.08, 10.0                          # N·m vridstopp, N dytt
TIP_MIN, DELTA_MAX = 6.0, 2.0                       # grader, mm
SIG, E_ST = 235e6 / 2, 200e9                        # stål S235, SF 2
BATT_WH = 21.6
SPINE_A, SPINE_P = 8.7e-5, 0.064                    # alu 16x16x1.5: areal, omkrins
MAT = {'alu': dict(rho=2700, t=0.0010, metal=True, flat=False),
       'stal': dict(rho=7850, t=0.0008, metal=True, flat=False),
       'finer': dict(rho=680, t=0.0012, metal=False, flat=True, lag=0.0006),  # 2 x 0.6 ulimt, elastisk rulla
       'filt': dict(rho=250, t=0.0040, metal=False, flat=True)}
BASE_MAT = {'stal': (7850, 0.006), 'eik': (700, 0.030)}
SLOT = {'smal': (25, 25, 0.90), 'brei': (60, 60, 0.85), 'kile': (15, 65, 0.90),
        'vindauge': (75, 75, 0.50), 'umogleg': (100, 100, 0.90)}


def body(i, r, c, namn, stotte, plass, L, R, alfa, yaw, slot, mat, base, bmat, h=None, batt=False, base_r=None):
    b0, b1, k = SLOT[slot]
    return dict(id=i, rad=r, kol=c, namn=namn, stotte=stotte, plass=plass, L=L, R=R, alfa=alfa, yaw=yaw,
                slot=slot, b0=b0, b1=b1, k=k, mat=mat, base=base, bmat=bmat, h=h, batt=batt, base_r=base_r,
                nseg=2 if stotte == 'T' else 1)


BODIES = [
    body(1, 1, 1, 'overliggar', 'portal', 'over', 0.62, 0.022, 0, 0, 'smal', 'alu', 'foter', 'stal', h=0.60),
    body(2, 1, 2, 'bøyle', 'portal', 'side', 0.34, 0.038, 0, 0, 'brei', 'finer', 'rekt', 'eik', h=0.38),
    body(3, 1, 3, 'skråportal', 'portal', 'side', 0.26, 0.045, 30, -20, 'kile', 'filt', 'oval', 'stal', h=0.36),
    body(4, 1, 4, 'gaffel', 'portal', 'side', 0.14, 0.075, 0, 0, 'vindauge', 'stal', 'disk', 'eik', h=0.28),
    body(5, 2, 1, 'langarm', 'utkrag', 'arm', 0.56, 0.022, 0, 0, 'brei', 'filt', 'disk', 'stal', h=0.54),
    body(6, 2, 2, 'arm', 'utkrag', 'arm', 0.34, 0.038, 0, 0, 'smal', 'stal', 'oval', 'eik', h=0.54),
    body(7, 2, 3, 'stigarm', 'utkrag', 'arm', 0.26, 0.045, 30, 20, 'vindauge', 'alu', 'rekt', 'stal', h=0.50),
    body(8, 2, 4, 'trommearm', 'utkrag', 'arm', 0.14, 0.075, 0, 0, 'kile', 'finer', 'disk', 'eik', h=0.54),
    body(9, 3, 1, 'vektstong', 'T', 'side', 0.50, 0.022, 0, 90, 'kile', 'stal', 'rekt', 'stal', h=0.50),
    body(10, 3, 2, 'tvillingrør', 'T', 'side', 0.34, 0.038, 0, 0, 'vindauge', 'filt', 'disk', 'eik', h=0.40),
    body(11, 3, 3, 'skrå-T', 'T', 'side', 0.26, 0.045, 25, -30, 'smal', 'finer', 'oval', 'stal', h=0.40),
    body(12, 3, 4, 'tvillingtromme', 'T', 'side', 0.16, 0.075, 0, 0, 'brei', 'alu', 'rekt', 'eik', h=0.34, batt=True),
    body(13, 4, 1, 'vuggestav', 'vugge', 'side', 0.56, 0.022, 0, 90, 'vindauge', 'finer', 'ingen', 'eik', batt=True),
    body(14, 4, 2, 'vugge', 'vugge', 'side', 0.34, 0.038, 0, 0, 'kile', 'alu', 'rekt', 'eik', batt=True),
    body(15, 4, 3, 'lenerør', 'lene', 'side', 0.32, 0.045, 35, 0, 'brei', 'stal', 'disk', 'stal', batt=True),
    body(16, 4, 4, 'lenetromme', 'lene', 'side', 0.16, 0.075, 55, 0, 'smal', 'filt', 'disk', 'stal', batt=True),
]
CONTROLS = [
    body(17, 0, 1, 'veltar', 'lene', 'side', 0.45, 0.050, 40, 0, 'brei', 'alu', 'disk', 'eik', base_r=0.045),
    body(18, 0, 2, 'umogleg', 'portal', 'side', 0.12, 0.012, 0, 0, 'umogleg', 'finer', 'disk', 'eik', h=0.30),
]


# ---------------- ryggrad og opning ----------------
def frame(alfa, yaw):
    a, p = math.radians(alfa), math.radians(yaw)
    u = np.array([math.cos(a) * math.cos(p), math.cos(a) * math.sin(p), math.sin(a)])
    w = np.array([0.0, 0.0, -1.0]) + u[2] * u
    w /= np.linalg.norm(w)
    return u, w, np.cross(u, w)          # phi=0: opning ned; phi=+90: mot u x w


def segments(B):
    if B['nseg'] == 1:
        return [(0.0, B['L'])]
    Ls = (B['L'] - 0.03) / 2
    return [(0.0, Ls), (Ls + 0.03, Ls)]


def beta_at(B, x, Ls):
    a0, a1 = Ls * (1 - B['k']) / 2, Ls * (1 + B['k']) / 2
    if x < a0 or x > a1:
        return 0.0
    return math.radians(B['b0'] + (B['b1'] - B['b0']) * (x - a0) / (a1 - a0))


def place_spine(B):
    u, w, v = frame(B['alfa'], B['yaw'])
    ax, ay = ANCHOR[B['plass']]
    tb = BASE_MAT[B['bmat']][1] if B['base'] != 'ingen' else 0.0
    st, L, R = B['stotte'], B['L'], B['R']
    if st in ('portal', 'T'):
        c0 = np.array([ax, ay, B['h']]) - u * L / 2
    elif st == 'utkrag':
        c0 = np.array([ax, ay, B['h']]) + u * 0.025
    elif st == 'vugge':
        c0 = np.array([ax, ay, tb + R + 0.02]) - u * L / 2
    else:  # lene
        c0 = np.array([ax, ay, tb + 0.006 + R * math.cos(math.radians(B['alfa']))])
    B.update(u=u, w=w, v=v, c0=c0, tb=tb, seg=segments(B))
    return B


def aperture(B, phi, ns=8, nt=3):
    n = math.cos(phi) * B['w'] + math.sin(phi) * B['v']
    td = np.cross(B['u'], n)
    P, dA = [], []
    for s0, Ls in B['seg']:
        a0, a1 = Ls * (1 - B['k']) / 2, Ls * (1 + B['k']) / 2
        for x in a0 + (np.arange(ns) + 0.5) / ns * (a1 - a0):
            be = beta_at(B, x, Ls)
            half, off = B['R'] * math.sin(be), B['R'] * math.cos(be)
            for t in (np.arange(nt) + 0.5) / nt * 2 - 1:
                P.append(B['c0'] + (s0 + x) * B['u'] + off * n + t * half * td)
                dA.append((a1 - a0) / ns * 2 * half / nt)
    return np.array(P), n, np.array(dA)


def cavity_eta(B):
    A_ap = sum(aperture(B, 0.0)[2])
    A_in = sum(2 * math.pi * B['R'] * Ls + 2 * math.pi * B['R'] ** 2 for _, Ls in B['seg'])
    f = A_ap / A_in
    sb = math.sin(math.radians((B['b0'] + B['b1']) / 2))
    return min(1.0, sb + (1 - sb) * RHO * f / (1 - RHO * (1 - f))), A_ap


def screen_block(P, Q):
    d = Q[None] - P[:, None]
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (SCR['y'] - P[:, None, 1]) / d[..., 1]
    X = P[:, None, 0] + t * d[..., 0]
    Z = P[:, None, 2] + t * d[..., 2]
    return (t > 0) & (t < 1) & (X > SCR['x0']) & (X < SCR['x1']) & (Z > SCR['z0']) & (Z < SCR['z1'])


def illum(P, n, dA, Q, qn):
    d = Q[None] - P[:, None]
    r2 = (d ** 2).sum(-1)
    r = np.sqrt(r2)
    ce, cr = (d @ n) / r, -(d @ qn) / r
    ok = (ce > 0) & (cr > 0) & ~screen_block(P, Q)
    return (np.where(ok, ce * cr / r2, 0.0) * dA[:, None]).sum(0)


def visible(P, n):
    front = ((EYES[None] - P[:, None]) @ n) > 0
    return bool((front & ~screen_block(P, EYES)).any())


def reflected(P, n):
    Em = EYES.copy()
    Em[:, 1] = 2 * SCR['y'] - Em[:, 1]
    for e in Em:
        m = P[:, 1] < SCR['y']
        if not m.any():
            continue
        Pm = P[m]
        t = (SCR['y'] - e[1]) / (Pm[:, 1] - e[1])
        Q = e + t[:, None] * (Pm - e)
        ok = (Q[:, 0] > SCR['x0']) & (Q[:, 0] < SCR['x1']) & (Q[:, 2] > SCR['z0']) & (Q[:, 2] < SCR['z1'])
        if (ok & (((Q - Pm) @ n) > 0)).any():
            return True
    return False


_rng = np.random.default_rng(7)
_U = _rng.random((300, 2))
_LOC = np.c_[np.sqrt(_U[:, 0]) * np.cos(2 * np.pi * _U[:, 1]),
             np.sqrt(_U[:, 0]) * np.sin(2 * np.pi * _U[:, 1]), np.sqrt(1 - _U[:, 0])]


def mood_split(P, n, u):
    t1 = np.cross(u, n)
    D = _LOC @ np.stack([t1, u, n])
    Pp = P[::3]
    with np.errstate(divide='ignore', invalid='ignore'):
        tw = np.where(D[None, :, 1] > 0, (WALL_Y - Pp[:, None, 1]) / D[None, :, 1], np.inf)
        td = np.where(D[None, :, 2] < 0, -Pp[:, None, 2] / D[None, :, 2], np.inf)
    zw = Pp[:, None, 2] + tw * D[None, :, 2]
    wall = (tw < td) & (zw < 2.4)
    down = ~wall & (D[None, :, 2] < 0)
    return float(wall.mean()), float(down.mean())


def light(B):
    eta, A = cavity_eta(B)
    phis = np.radians(np.arange(-180, 180, 5))
    rows = []
    for ph in phis:
        P, n, dA = aperture(B, ph)
        Ev = illum(P, n, dA, TASK, np.array([0, 0, 1.0])) * eta / (math.pi * A)   # lx per LED-lm
        Fv = illum(P, n, dA, EYES[:1], np.array([0, 1.0, 0]))[0]                     # lx per cd/m2
        wall, down = mood_split(P, n, B['u'])
        rows.append(dict(phi=ph, Em=Ev.mean(), U0=Ev.min() / max(Ev.mean(), 1e-12),
                         vis=visible(P, n), refl=reflected(P, n), face=Fv, wall=wall, down=down))
    for r in rows:
        r['Phi'] = E_TASK / max(r['Em'], 1e-9)
        r['Lap'] = eta * r['Phi'] / (math.pi * A)
        r['glare_ok'] = (not r['vis'] or r['Lap'] <= L_MAX) and (not r['refl'] or r['Lap'] <= L_MAX)
    feas = [r for r in rows if r['glare_ok'] and r['U0'] >= U0_MIN]
    work = min(feas or rows, key=lambda r: r['Phi'] * (1 if feas else
                                                       (1 + (not r['glare_ok']) + (r['U0'] < U0_MIN))))
    mfeas = [r for r in rows if not r['vis'] and not r['refl']]
    mood = max(mfeas or rows, key=lambda r: 1 - r['down'])
    face = max(rows, key=lambda r: r['face'])
    # sveip: går vi frå arbeid til stemning utan å syne kjelda?
    i0, i1 = rows.index(work), rows.index(mood)
    n_ = len(rows)
    arcs = [[(i0 + j) % n_ for j in range((i1 - i0) % n_ + 1)], [(i0 - j) % n_ for j in range((i0 - i1) % n_ + 1)]]
    arcs.sort(key=len)
    sveip = 'fri' if not any(rows[j]['vis'] for j in arcs[0]) else (
        'lang veg' if not any(rows[j]['vis'] for j in arcs[1]) else 'blendar')
    dphi = abs((math.degrees(mood['phi'] - work['phi']) + 180) % 360 - 180)
    return dict(eta=eta, A_ap=A, work=work, mood=mood, face=face, dphi=dphi, sveip=sveip,
                L150=E_FACE / max(face['face'], 1e-12))


# ---------------- mesh ----------------
def sleeve_mesh(B, phi, ns=40, nt=96):
    V, F = [], []
    c0, u, w, v, R = B['c0'], B['u'], B['w'], B['v'], B['R']
    th = np.arange(nt) / nt * 2 * np.pi
    ring = np.cos(th)[:, None] * w + np.sin(th)[:, None] * v
    for s0, Ls in B['seg']:
        xs = np.linspace(0, Ls, ns + 1)
        base = len(V) if isinstance(V, list) else 0
        o = sum(len(x) for x in V)
        V.append((c0 + (s0 + xs)[:, None, None] * u + R * ring[None]).reshape(-1, 3))
        for i in range(ns):
            xm = (xs[i] + xs[i + 1]) / 2
            be = beta_at(B, xm, Ls)
            for j in range(nt):
                tm = th[j] + np.pi / nt
                if be > 0 and abs((tm - phi + np.pi) % (2 * np.pi) - np.pi) < be:
                    continue
                a, b = o + i * nt + j, o + i * nt + (j + 1) % nt
                F += [(a, b, b + nt), (a, b + nt, a + nt)]
        for x in (0.0, Ls):                                     # endelokk
            o = sum(len(q) for q in V)
            cen = c0 + (s0 + x) * u
            V.append(np.vstack([cen, cen + R * ring]))
            F += [(o, o + 1 + j, o + 1 + (j + 1) % nt) for j in range(nt)]
    return V, F


def frustum(p0, p1, r0, r1, n=16):
    ax = p1 - p0
    ax = ax / np.linalg.norm(ax)
    a = np.cross(ax, [1, 0, 0] if abs(ax[0]) < 0.9 else [0, 1, 0])
    a /= np.linalg.norm(a)
    b = np.cross(ax, a)
    th = np.arange(n) / n * 2 * np.pi
    ring = np.cos(th)[:, None] * a + np.sin(th)[:, None] * b
    V = np.vstack([p0 + r0 * ring, p1 + r1 * ring, [p1]])
    F = [(j, (j + 1) % n, n + (j + 1) % n) for j in range(n)] + [(j, n + (j + 1) % n, n + j) for j in range(n)]
    F += [(2 * n, n + j, n + (j + 1) % n) for j in range(n)]
    return V, F


def tapered_rod(p0, p1, d_of_t, n=16, m=10):
    Vs, Fs, o = [], [], 0
    ts = np.linspace(0, 1, m + 1)
    for i in range(m):
        V, F = frustum(p0 + ts[i] * (p1 - p0), p0 + ts[i + 1] * (p1 - p0), d_of_t(ts[i]) / 2, d_of_t(ts[i + 1]) / 2, n)
        Vs.append(V)
        Fs += [tuple(o + q for q in f) for f in F]
        o += len(V)
    return np.vstack(Vs), Fs


def prism(poly, z0, z1):
    n = len(poly)
    V = np.vstack([np.c_[poly, np.full(n, z0)], np.c_[poly, np.full(n, z1)]])
    c = len(V)
    V = np.vstack([V, [poly.mean(0)[0], poly.mean(0)[1], z1]])
    F = [(j, (j + 1) % n, n + (j + 1) % n) for j in range(n)] + [(j, n + (j + 1) % n, n + j) for j in range(n)]
    F += [(c, n + j, n + (j + 1) % n) for j in range(n)]
    return V, F


def outline(kind, cen, dirx, a, b):
    ex = np.array(dirx) / (np.linalg.norm(dirx) + 1e-12)
    ey = np.array([-ex[1], ex[0]])
    if kind == 'rekt':
        q = np.array([[-a, -b], [a, -b], [a, b], [-a, b]])
    else:
        t = np.arange(32) / 32 * 2 * np.pi
        q = np.c_[a * np.cos(t), b * np.sin(t)]
    return cen + q[:, :1] * ex + q[:, 1:] * ey


# ---------------- kropp: geometri, masse, styrke ----------------
def build(B, phi):
    m = MAT[B['mat']]
    L, R, u, c0, tb = B['L'], B['R'], B['u'], B['c0'], B['tb']
    meshes, parts, contacts, notes = [], [], [], []
    V, F = sleeve_mesh(B, phi)
    meshes.append((np.vstack(V), F))
    slot_area = sum(sum(2 * beta_at(B, x, Ls) * R * Ls / 200 for x in np.linspace(0, Ls, 200)) for _, Ls in B['seg'])
    sl_area = sum(2 * math.pi * R * Ls for _, Ls in B['seg']) - slot_area
    mid = c0 + u * L / 2
    capm = sum(2 * math.pi * R ** 2 * 0.003 * (m['rho'] if m['metal'] else 700) for _ in B['seg'])
    head = [(sl_area * m['t'] * m['rho'], mid), (capm, mid), (SPINE_A * L * 2700, mid), (0.05, mid)]
    if B['stotte'] == 'T':
        head.append((0.03, mid))
        meshes.append(frustum(mid - u * 0.015, mid + u * 0.015, 0.8 * R, 0.8 * R))
    m_head = sum(x for x, _ in head)
    parts += head
    ax, ay = ANCHOR[B['plass']]
    dxy = u[:2] if np.linalg.norm(u[:2]) > 1e-6 else np.array([1.0, 0])
    dxy = dxy / np.linalg.norm(dxy)
    st = B['stotte']
    posts = []                                      # (botn, topp, F, M0)
    if st == 'portal':
        for e in (c0 - u * 0.012, c0 + u * (L + 0.012)):
            posts.append((np.array([e[0], e[1], tb]), e - np.array([0, 0, 0]), F_PUSH / 2, T_DET))
        span = np.linalg.norm((posts[1][0] - posts[0][0])[:2])
        cen = (posts[0][0][:2] + posts[1][0][:2]) / 2
        if B['base'] == 'foter':
            for p in posts:
                pg = outline('rekt', p[0][:2], [-dxy[1], dxy[0]], 0.08, 0.0125)
                meshes.append(prism(pg, 0, tb)); contacts.append(pg)
                parts.append((BASE_MAT[B['bmat']][0] * 0.16 * 0.025 * tb, np.r_[p[0][:2], tb / 2]))
            bpoly = None
        else:
            a = span / 2 + 0.06
            bpoly = outline(B['base'], cen, dxy, a if B['base'] != 'disk' else a, 0.075 if B['base'] != 'disk' else a)
    elif st == 'utkrag':
        xarm = (0.025 + L / 2) * math.cos(math.radians(B['alfa']))
        posts.append((np.array([ax, ay, tb]), np.array([ax, ay, B['h']]), F_PUSH, m_head * G * xarm + T_DET))
        cen = np.array([ax, ay]) + 0.35 * xarm * dxy
        r = B['base_r'] or 0.09
        bpoly = outline(B['base'], cen, dxy, *(r, r) if B['base'] == 'disk' else (0.12, 0.08) if B['base'] == 'oval' else (0.11, 0.065))
    elif st == 'T':
        posts.append((np.array([ax, ay, tb]), mid - np.array([0, 0, 0.0]), F_PUSH, T_DET))
        r = B['base_r'] or 0.085
        bpoly = outline(B['base'], np.array([ax, ay]), dxy, *(r, r) if B['base'] == 'disk' else (0.11, 0.07) if B['base'] == 'oval' else (0.10, 0.065))
    elif st == 'vugge':
        bpoly = None
        if B['base'] == 'rekt':
            bpoly = outline('rekt', mid[:2], dxy, 0.4 * L, R + 0.02)
        for f in (0.2, 0.8):
            p = c0 + u * (f * L)
            pg = outline('rekt', p[:2], dxy, 0.018, R * 0.9)
            meshes.append(prism(pg, tb, p[2] - 0.45 * R))
            parts.append((700 * 0.036 * 1.8 * R * (p[2] - 0.45 * R - tb), np.r_[p[:2], (p[2] - 0.45 * R + tb) / 2]))
            if bpoly is None:
                contacts.append(pg)
    else:  # lene
        lever = (L / 2) * math.cos(math.radians(B['alfa']))
        r = B['base_r'] or max(0.09, 0.75 * lever + 0.03)
        cen = np.array([ax, ay]) + (0.5 * lever * dxy if B['base_r'] is None else 0)
        bpoly = outline('disk', cen, dxy, r, r)
        meshes.append(frustum(c0 - u * 0.006, c0 + u * 0.05, R + 0.008, R + 0.008, 32))
        parts.append((0.08, c0 + u * 0.02))
    if bpoly is not None:
        meshes.append(prism(bpoly, 0, tb)); contacts.append(bpoly)
        area = 0.5 * abs(np.dot(bpoly[:, 0], np.roll(bpoly[:, 1], 1)) - np.dot(bpoly[:, 1], np.roll(bpoly[:, 0], 1)))
        parts.append((BASE_MAT[B['bmat']][0] * area * tb, np.r_[bpoly.mean(0), tb / 2]))
    # stenger: tverrsnitt frå momentlova, ingen w_min
    dmax, dtop, delta = 0.0, 0.0, 0.0
    for p0, p1, Fp, M0 in posts:
        hh = p1[2] - p0[2]
        dfun = lambda t, hh=hh, Fp=Fp, M0=M0: (32 * (Fp * hh * (1 - t) + M0) / (math.pi * SIG)) ** (1 / 3)
        Vr, Fr = tapered_rod(p0, p1, dfun)
        meshes.append((Vr, Fr))
        ts = np.linspace(0, 1, 60)
        d = np.array([dfun(t) for t in ts])
        parts.append((7850 * np.trapezoid(math.pi * d ** 2 / 4, ts * hh), p0 + (p1 - p0) * 0.4))
        I = math.pi * d ** 4 / 64
        Fv = (T_DET / R) * (Fp / F_PUSH)
        delta = max(delta, np.trapezoid(Fv * (hh * (1 - ts)) ** 2 / (E_ST * I), ts * hh) * 1000)
        dmax, dtop = max(dmax, d[0] * 1000), d[-1] * 1000
    if B['batt']:
        bc = contacts[-1].mean(0) if contacts else mid[:2]
        parts.append((0.095, np.r_[bc, tb / 2]))
    Vall = np.vstack([x[0] for x in meshes])
    Fall, o = [], 0
    for Vm, Fm in meshes:
        Fall += [tuple(o + q for q in f) for f in Fm]
        o += len(Vm)
    return dict(V=Vall, F=np.array(Fall), parts=parts, contacts=contacts, m_head=m_head,
                d_bot=dmax, d_top=dtop, delta=delta, sl_area=sl_area)


def tal(B):
    """Same tal() på alle: grense, masse, stabilitet, funksjonsflate, styrke, produserbarheit."""
    place_spine(B)
    Lt = light(B)
    geo = build(B, Lt['work']['phi'])
    V = geo['V']
    m = MAT[B['mat']]
    mass = sum(x for x, _ in geo['parts'])
    com = sum(x * c for x, c in geo['parts']) / mass
    pts = np.vstack(geo['contacts'])
    hull = ConvexHull(pts)
    hv = pts[hull.vertices]
    dmin = min(np.dot(com[:2] - a, np.array([-(b - a)[1], (b - a)[0]]) / np.linalg.norm(b - a))
               for a, b in zip(hv, np.roll(hv, -1, 0)))
    ztop = V[:, 2].max()
    zgrip = max(V[:, 2].max() * 0 + (B['c0'] + B['u'] * B['L'] / 2)[2] + B['R'], 0.05)
    tip = math.degrees(math.atan2(dmin, com[2]))
    F_vrid = T_DET / B['R']
    F_tip = mass * G * dmin / zgrip
    x0, x1, y0, y1 = DESK
    fx0, fx1, fy0, fy1, fz0, fz1 = FORBID
    out = (V[:, 0] < x0) | (V[:, 0] > x1) | (V[:, 1] < y0) | (V[:, 1] > y1)
    inn = (V[:, 0] > fx0) & (V[:, 0] < fx1) & (V[:, 1] > fy0) & (V[:, 1] < fy1) & (V[:, 2] > fz0) & (V[:, 2] < fz1)
    W, Mo = Lt['work'], Lt['mood']
    P_W = W['Phi'] / LM_W
    A_req = P_W / (H_CONV * DT)
    A_kj = SPINE_P * sum(Ls for _, Ls in B['seg']) + (0.5 * geo['sl_area'] if m['metal'] else 0)
    finer_ok = B['mat'] != 'finer' or m['lag'] <= 0.03 * B['R']
    klips_ok = max(B['b0'], B['b1']) < 90
    filt_ok = B['mat'] != 'filt' or max(Ls for _, Ls in B['seg']) / B['R'] <= 8
    term_ok = A_kj >= A_req
    flat = m['flat'] and finer_ok
    sleeve_pack = sum(Ls * 2 * math.pi * B['R'] * (m['t'] + 0.003) if flat else Ls * (2 * B['R']) ** 2 for _, Ls in B['seg'])
    pack = 1.4 * (sleeve_pack + sum(np.prod(np.ptp(c, 0)) * 0.03 for c in geo['contacts'])
                  + B['L'] * 0.02 * 0.02 + 0.3 * 0.012 * 0.012 * len(geo['contacts'] or [1]))
    bbox = np.prod(np.ptp(V, 0))
    fot = ConvexHull(pts).volume * 1e4
    flags = []
    if out.mean() > 0.005: flags.append('utanfor bord')
    if inn.mean() > 0.005: flags.append('i siktlina')
    if tip < TIP_MIN: flags.append('veltar')
    if F_tip < 2 * F_vrid: flags.append('vrid veltar')
    if not W['glare_ok']: flags.append('blendar i arbeid')
    if W['U0'] < U0_MIN: flags.append('ujamt')
    if Mo['vis'] or Mo['refl']: flags.append('kjelde synleg i stemning')
    if geo['delta'] > DELTA_MAX: flags.append('vaggar')
    if not term_ok: flags.append('for varm')
    if not finer_ok: flags.append('finér knekk')
    if not klips_ok: flags.append('hylse held ikkje')
    if not filt_ok: flags.append('filt sig')
    return dict(id=B['id'], rad=B['rad'], kol=B['kol'], namn=B['namn'], stotte=B['stotte'], plass=B['plass'],
                L_cm=B['L'] * 100, R_mm=B['R'] * 1000, alfa=B['alfa'], yaw=B['yaw'], opning=B['slot'], hylse=B['mat'],
                fot_cm2=fot, hogd_cm=ztop * 100, ut_grense=float(out.mean() + inn.mean()),
                masse_kg=mass, tipp_deg=tip, F_tipp_N=F_tip, F_vrid_N=F_vrid,
                A_opn_cm2=Lt['A_ap'] * 1e4, eta=Lt['eta'], phi_arb=math.degrees(W['phi']), Phi_lm=W['Phi'],
                U0=W['U0'], L_arb=W['Lap'], synleg_arb=W['vis'], spegl_arb=W['refl'],
                phi_stem=math.degrees(Mo['phi']), indirekte=1 - Mo['down'], vegg=Mo['wall'],
                synleg_stem=Mo['vis'] or Mo['refl'], dphi=Lt['dphi'], sveip=Lt['sveip'], L_ansikt=Lt['L150'],
                d_bot_mm=geo['d_bot'], d_top_mm=geo['d_top'], svikt_mm=geo['delta'],
                P_W=P_W, A_kjol_cm2=A_kj * 1e4, A_krav_cm2=A_req * 1e4, batt_t=(BATT_WH * 0.9 / P_W) if B['batt'] else 0,
                pakke_l=pack * 1000, bbox_l=bbox * 1000, kan_lagast=finer_ok and klips_ok and filt_ok and term_ok,
                flagg='; '.join(flags) or '-'), geo


# ---------------- brett: husstil ----------------
class Cam:
    def __init__(s, S=1024, el=17, az=240, fov=19, D=3.0, target=(0, 0, 0.31)):
        s.S, t = S, np.array(target, float)
        e, a = math.radians(el), math.radians(az)
        s.eye = t + D * np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
        f = t - s.eye; f /= np.linalg.norm(f)
        r = np.cross(f, [0, 0, 1]); r /= np.linalg.norm(r)
        s.M = np.stack([r, np.cross(r, f), f])
        s.k = (S / 2) / math.tan(math.radians(fov) / 2)

    def proj(s, P):
        d = (P - s.eye) @ s.M.T
        return np.c_[s.S / 2 + s.k * d[:, 0] / d[:, 2], s.S / 2 - s.k * d[:, 1] / d[:, 2], d[:, 2]]


ALB = np.array([0.86, 0.77, 0.63])
KEY = np.array([-0.45, -0.55, 0.70]); KEY /= np.linalg.norm(KEY)
SHD = np.array([0.08, 0.12, 1.0]); SHD /= np.linalg.norm(SHD)


def render(V, F, cam):
    S = cam.S
    p = cam.proj(V)
    T = V[F]
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-15
    n *= np.sign(((cam.eye - T.mean(1)) * n).sum(1))[:, None]
    lam = np.clip(n @ KEY, 0, 1)
    col = np.clip(ALB[None] * (0.46 + 0.60 * lam[:, None] + 0.08 * np.clip(n[:, 2], 0, 1)[:, None]), 0, 1)
    img = np.ones((S, S, 3)); zb = np.zeros((S, S))
    for i, (a, b, c) in enumerate(F):
        P = p[[a, b, c]]
        x0, x1 = max(int(P[:, 0].min()), 0), min(int(P[:, 0].max()) + 1, S - 1)
        y0, y1 = max(int(P[:, 1].min()), 0), min(int(P[:, 1].max()) + 1, S - 1)
        if x1 < x0 or y1 < y0:
            continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        (xa, ya), (xb, yb), (xc, yc) = P[:, :2]
        den = (yb - yc) * (xa - xc) + (xc - xb) * (ya - yc)
        if abs(den) < 1e-9:
            continue
        l1 = ((yb - yc) * (xs - xc) + (xc - xb) * (ys - yc)) / den
        l2 = ((yc - ya) * (xs - xc) + (xa - xc) * (ys - yc)) / den
        l3 = 1 - l1 - l2
        iz = l1 / P[0, 2] + l2 / P[1, 2] + l3 / P[2, 2]
        sub = zb[y0:y1 + 1, x0:x1 + 1]
        msk = (l1 >= 0) & (l2 >= 0) & (l3 >= 0) & (iz > sub)
        sub[msk] = iz[msk]
        img[y0:y1 + 1, x0:x1 + 1][msk] = col[i]
    obj = zb > 0
    sh = np.zeros((S, S))
    for ldir, sig, k in ((SHD, 0.010, 0.30), (np.array([0, 0, 1.0]), 0.004, 0.22)):
        Gp = V - (V[:, 2:3] / ldir[2]) * ldir
        q = cam.proj(Gp)
        msk = np.zeros((S, S))
        for a, b, c in F:
            rr, cc = skpoly(q[[a, b, c], 1], q[[a, b, c], 0], (S, S))
            msk[rr, cc] = 1
        sh = np.maximum(sh, k * gaussian_filter(msk, sig * S))
    ground = (1 - sh)[..., None] * np.ones(3)
    out = np.where(obj[..., None], img, ground)
    im = Image.fromarray((out * 255).astype(np.uint8)).resize((S // 2, S // 2), Image.LANCZOS)
    return im, np.array(Image.fromarray(obj.astype(np.uint8) * 255).resize((S // 2, S // 2))) > 127


def main():
    os.makedirs(os.path.join(HER, 'kroppar'), exist_ok=True)
    cam = Cam()
    rows, masks, ims = [], {}, {}
    for B in BODIES + CONTROLS:
        t, geo = tal(B)
        V = geo['V'].copy()
        c = np.vstack(geo['contacts']).mean(0)
        V[:, :2] -= c
        im, mk = render(V, geo['F'], cam)
        im.save(os.path.join(HER, 'kroppar', f"k{B['id']:02d}.png"))
        ims[B['id']], masks[B['id']] = im, mk
        hull = convex_hull_image(mk)
        t['luft_2d'] = 1 - mk.sum() / max(hull.sum(), 1)
        rows.append(t)
        print(f"{B['id']:2d} {B['namn']:15s} Phi={t['Phi_lm']:6.0f} U0={t['U0']:.2f} ind={t['indirekte']:.2f} "
              f"tipp={t['tipp_deg']:5.1f} m={t['masse_kg']:.2f} {t['flagg']}")
    # nabo-IoU
    grid = {(r['rad'], r['kol']): r['id'] for r in rows if r['rad']}
    ious = []
    for (r, c), i in grid.items():
        for rr, cc in ((r, c + 1), (r + 1, c)):
            if (rr, cc) in grid:
                a, b = masks[i], masks[grid[(rr, cc)]]
                ious.append((a & b).sum() / (a | b).sum())
    board = Image.new('RGB', (2048, 2048), 'white')
    for (r, c), i in grid.items():
        board.paste(ims[i], ((c - 1) * 512, (r - 1) * 512))
    board.save(os.path.join(HER, 'brett.png'))
    ctrl = Image.new('RGB', (1024, 512), 'white')
    for j, B in enumerate(CONTROLS):
        ctrl.paste(ims[B['id']], (j * 512, 0))
    ctrl.save(os.path.join(HER, 'kontroll.png'))
    keys = list(rows[0].keys())
    with open(os.path.join(HER, 'tal.csv'), 'w', newline='', encoding='utf-8') as f:
        wr = csv.DictWriter(f, keys); wr.writeheader()
        for r in rows:
            wr.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
    print(f"nabo-IoU snitt {np.mean(ious):.2f} maks {np.max(ious):.2f}")
    return rows, ious


if __name__ == '__main__':
    main()
