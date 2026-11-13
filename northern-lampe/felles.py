"""Northern-lampe · felles tal() for alle generasjonar (scene, lys, stabilitet, styrke, husstil på svart).

Ein motor (genNN/motor.py) gjev berre:
  opning(B, tilstand) -> (P (n,3), N (n,3), dA (n,))   luminøse flatebitar (lambertske) for éin gesttilstand
  eta (hulromsverknadsgrad), liste med gesttilstandar, geometri (V, F), delar [(masse, tyngdepunkt)], kontaktpolygon.
Alt anna vert rekna her, likt for alle. Premissane står i gen01/logg.md (+ skjerpa stemningsmål, sjå lys()).
"""
import math
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from scipy.spatial import ConvexHull
from skimage.morphology import convex_hull_image

G = 9.81
# ---------------- scene (m) ----------------
DESK = (-0.70, 0.70, 0.0, 0.75)
WALL_Y = 0.75
SCR = dict(x0=-0.275, x1=0.275, y=0.45, z0=0.10, z1=0.42)
EYES = np.array([[0.0, -0.30, 0.45], [-0.15, -0.30, 0.45], [0.15, -0.30, 0.45]])
_tx, _ty = np.meshgrid(np.linspace(-0.30, 0.30, 7), np.linspace(0.05, 0.40, 5))
TASK = np.c_[_tx.ravel(), _ty.ravel(), np.zeros(_tx.size)]
_wx, _wz = np.meshgrid(np.linspace(-0.70, 0.70, 8), np.linspace(0.05, 1.20, 6))
WALLG = np.c_[_wx.ravel(), np.full(_wx.size, WALL_Y - 1e-3), _wz.ravel()]
_dx, _dy = np.meshgrid(np.linspace(-0.68, 0.68, 8), np.linspace(0.02, 0.73, 5))
DESKG = np.c_[_dx.ravel(), _dy.ravel(), np.zeros(_dx.size)]
FORBID = (-0.30, 0.30, 0.0, 0.50, 0.0, 0.50)       # siktline + skjerm + hender
ANCHOR = {'side': (-0.50, 0.40), 'over': (0.0, 0.40), 'arm': (-0.60, 0.30)}
# ---------------- krav / lover ----------------
E_TASK, U0_MIN, L_MAX = 500.0, 0.40, 3000.0       # lx, -, cd/m2 (EN 12464-1)
E_FACE = 150.0                                     # lx vertikalt ved auga, videomøte (sekundært)
DIM_STEM, L_STEM_MAX, R_STEM_MIN = 0.25, 1000.0, 0.5   # stemning: 25 % fluks, synleg L <= 1000, veggdel E_v/(E_v+E_b) >= 0,5
RHO, LM_W = 0.85, 100.0
H_CONV, DT = 10.0, 30.0                            # A_kjøl >= P/(h·ΔT)
F_PUSH = 10.0
TIP_MIN, DELTA_MAX = 6.0, 2.0                      # grader (EN 60598-1, ikkje kontrollert), mm svikt under gestkraft
SIG, E_ST = 235e6 / 2, 200e9                       # stål S235, SF 2
BATT_WH = 21.6
FINER_LAG = 0.0006                                 # lagtjukn τ <= 0,03R


# ---------------- lys ----------------
def screen_block(P, Q):
    d = Q[None] - P[:, None]
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (SCR['y'] - P[:, None, 1]) / d[..., 1]
    X = P[:, None, 0] + t * d[..., 0]
    Z = P[:, None, 2] + t * d[..., 2]
    return (t > 1e-6) & (t < 1 - 1e-6) & (X > SCR['x0']) & (X < SCR['x1']) & (Z > SCR['z0']) & (Z < SCR['z1'])


def illum(P, N, dA, Q, qn):
    """Illuminans på mottakarar Q (normal qn) per eining luminans [lx per cd/m2]."""
    d = Q[None] - P[:, None]
    r2 = (d ** 2).sum(-1)
    r = np.sqrt(r2)
    ce = (d * N[:, None]).sum(-1) / r
    cr = -(d @ qn) / r
    ok = (ce > 0) & (cr > 0) & ~screen_block(P, Q)
    return (np.where(ok, ce * cr / r2, 0.0) * dA[:, None]).sum(0)


def visible(P, N):
    front = ((EYES[None] - P[:, None]) * N[:, None]).sum(-1) > 0
    return bool((front & ~screen_block(P, EYES)).any())


def reflected(P, N):
    m = P[:, 1] < SCR['y']
    if not m.any():
        return False
    Pm, Nm = P[m], N[m]
    for e in EYES:
        em = e.copy(); em[1] = 2 * SCR['y'] - e[1]
        t = (SCR['y'] - em[1]) / (Pm[:, 1] - em[1])
        Q = em + t[:, None] * (Pm - em)
        ok = (Q[:, 0] > SCR['x0']) & (Q[:, 0] < SCR['x1']) & (Q[:, 2] > SCR['z0']) & (Q[:, 2] < SCR['z1'])
        if (ok & (((Q - Pm) * Nm).sum(1) > 0)).any():
            return True
    return False


def lys(P, N, dA, eta):
    """Alle lystal for éin gesttilstand. Returnerer per-LED-lumen-verdiar og flagg."""
    A = dA.sum()
    k = eta / (math.pi * A)                        # luminans per LED-lm
    Et = illum(P, N, dA, TASK, np.array([0, 0, 1.0])) * k
    Ew = illum(P, N, dA, WALLG, np.array([0, -1.0, 0])) * k
    Ed = illum(P, N, dA, DESKG, np.array([0, 0, 1.0])) * k
    Fv = illum(P, N, dA, EYES[:1], np.array([0, 1.0, 0]))[0]
    Em = Et.mean()
    return dict(Em=Em, U0=Et.min() / max(Em, 1e-12), Phi=E_TASK / max(Em, 1e-12), k=k, A=A,
                vis=visible(P, N), refl=reflected(P, N), face=Fv,
                R_stem=Ew.mean() / max(Ew.mean() + Ed.mean(), 1e-12), Ew=Ew.mean(), Ed=Ed.mean())


def sok(B, states, opning, eta, ring=True):
    """Søk over gesttilstandar: beste arbeid, stemning, ansikt + sveip. states: liste av tilstandar (t.d. vinklar)."""
    rows = []
    for s in states:
        P, N, dA = opning(B, s)
        r = lys(P, N, dA, eta)
        r['s'] = s
        rows.append(r)
    for r in rows:
        r['Lap'] = r['k'] * r['Phi']                          # cd/m2 ved 500 lx
        r['glare_ok'] = (not r['vis'] or r['Lap'] <= L_MAX) and (not r['refl'] or r['Lap'] <= L_MAX)
    feas = [r for r in rows if r['glare_ok'] and r['U0'] >= U0_MIN]
    work = min(feas or rows, key=lambda r: r['Phi'] * (1 if feas else 1 + (not r['glare_ok']) + (r['U0'] < U0_MIN)))
    PhiW = work['Phi']
    for r in rows:   # stemning ved 25 % av arbeidsfluksen
        r['L_stem'] = r['k'] * PhiW * DIM_STEM
        r['stem_ok'] = ((not r['vis'] and not r['refl']) or r['L_stem'] <= L_STEM_MAX)
        r['Ev_stem'] = r['Ew'] * PhiW * DIM_STEM                 # lx snitt på veggen i stemning
    mf = [r for r in rows if r['stem_ok']]
    mood = max(mf or rows, key=lambda r: (r['R_stem'] >= R_STEM_MIN, r['Ev_stem']))
    face = max(rows, key=lambda r: r['face'])
    i0, i1, n = rows.index(work), rows.index(mood), len(rows)
    if ring:
        arcs = sorted([[(i0 + j) % n for j in range((i1 - i0) % n + 1)], [(i0 - j) % n for j in range((i0 - i1) % n + 1)]], key=len)
    else:
        lo, hi = sorted((i0, i1))
        arcs = [list(range(lo, hi + 1))] * 2
    bad = lambda j: rows[j]['vis'] and rows[j]['Lap'] > L_MAX
    sveip = 'fri' if not any(bad(j) for j in arcs[0]) else ('lang veg' if not any(bad(j) for j in arcs[1]) else 'blendar')
    return dict(rows=rows, work=work, mood=mood, face=face, sveip=sveip,
                L150=E_FACE / max(face['face'], 1e-12), steg=len(arcs[0]) - 1)


# ---------------- stenger, stabilitet ----------------
def stong(p0, p1, F, M0, n=16, m=10, stiv=False, F_gest=0.0):
    """Stong frå p0 (botn) til p1. Tverrsnitt frå momentlova (ingen w_min). stiv=True: konstant Ø frå svikt <= DELTA_MAX under F_gest.
    Returnerer (V, F, masse, tyngdepunkt, d_botn_mm, d_topp_mm, svikt_mm)."""
    hh = float(np.linalg.norm(p1 - p0))
    dfun = lambda t: (32 * (F * hh * (1 - t) + M0) / (math.pi * SIG)) ** (1 / 3)
    if stiv and F_gest > 0:
        I = F_gest * hh ** 3 / (3 * E_ST * DELTA_MAX / 1000)
        dst = (64 * I / math.pi) ** 0.25
        d0 = dfun
        dfun = lambda t: max(d0(t), dst)
    ts = np.linspace(0, 1, 60)
    d = np.array([dfun(t) for t in ts])
    I = math.pi * d ** 4 / 64
    delta = np.trapezoid(F_gest * (hh * (1 - ts)) ** 2 / (E_ST * I), ts * hh) * 1000 if F_gest > 0 else 0.0
    mass = 7850 * np.trapezoid(math.pi * d ** 2 / 4, ts * hh)
    Vs, Fs, o = [], [], 0
    tm = np.linspace(0, 1, m + 1)
    for i in range(m):
        V, Fc = frustum(p0 + tm[i] * (p1 - p0), p0 + tm[i + 1] * (p1 - p0), dfun(tm[i]) / 2, dfun(tm[i + 1]) / 2, n)
        Vs.append(V); Fs += [tuple(o + q for q in f) for f in Fc]; o += len(V)
    return np.vstack(Vs), Fs, mass, p0 + (p1 - p0) * 0.4, d[0] * 1000, d[-1] * 1000, delta


def stabilitet(parts, contacts, z_grip, F_gest):
    mass = sum(x for x, _ in parts)
    com = sum(x * np.asarray(c, float) for x, c in parts) / mass
    pts = np.vstack(contacts)
    hv = pts[ConvexHull(pts).vertices]
    dmin = min(np.dot(com[:2] - a, np.array([-(b - a)[1], (b - a)[0]]) / np.linalg.norm(b - a))
               for a, b in zip(hv, np.roll(hv, -1, 0)))
    tip = math.degrees(math.atan2(dmin, com[2]))
    F_tip = mass * G * dmin / max(z_grip, 0.02)
    return dict(masse_kg=mass, com=com, tipp_deg=tip, F_tipp_N=F_tip, F_gest_N=F_gest,
                fot_cm2=ConvexHull(pts).volume * 1e4)


def grense(V):
    x0, x1, y0, y1 = DESK
    fx0, fx1, fy0, fy1, fz0, fz1 = FORBID
    out = (V[:, 0] < x0) | (V[:, 0] > x1) | (V[:, 1] < y0) | (V[:, 1] > y1) | (V[:, 2] < -1e-3)
    inn = (V[:, 0] > fx0) & (V[:, 0] < fx1) & (V[:, 1] > fy0) & (V[:, 1] < fy1) & (V[:, 2] > fz0) & (V[:, 2] < fz1)
    return float(out.mean()), float(inn.mean())


def termisk(Phi, A_kjol):
    P = Phi / LM_W
    A_req = P / (H_CONV * DT)
    return dict(P_W=P, A_kjol_cm2=A_kjol * 1e4, A_krav_cm2=A_req * 1e4, termisk_ok=A_kjol >= A_req,
                batt_t=BATT_WH * 0.9 / P)


def standard_flagg(t):
    f = []
    if t['ut_bord'] > 0.005: f.append('utanfor bord')
    if t['i_sikt'] > 0.005: f.append('i siktlina')
    if t['tipp_deg'] < TIP_MIN: f.append('veltar')
    if t['F_tipp_N'] < 2 * t['F_gest_N']: f.append('gest veltar')
    if not t['glare_ok']: f.append('blendar i arbeid')
    if t['U0'] < U0_MIN: f.append('ujamt')
    if not t['stem_ok']: f.append('kjelde synleg i stemning')
    if t['R_stem'] < R_STEM_MIN: f.append('stemning ligg på bordet')
    if t['svikt_mm'] > DELTA_MAX: f.append('vaggar')
    if not t['termisk_ok']: f.append('for varm')
    return f


def tal_felles(B, S, st, V, svikt_mm, A_kjol):
    """Standardkolonnar, same rekkjefølgje i alle generasjonar."""
    W, M = S['work'], S['mood']
    ub, ik = grense(V)
    th = termisk(W['Phi'], A_kjol)
    t = dict(id=B['id'], rad=B['rad'], kol=B['kol'], namn=B['namn'],
             fot_cm2=st['fot_cm2'], hogd_cm=V[:, 2].max() * 100, ut_bord=ub, i_sikt=ik,
             masse_kg=st['masse_kg'], tipp_deg=st['tipp_deg'], F_tipp_N=st['F_tipp_N'], F_gest_N=st['F_gest_N'],
             A_opn_cm2=W['A'] * 1e4, Phi_lm=W['Phi'], U0=W['U0'], L_arb=W['Lap'], glare_ok=W['glare_ok'],
             gest_arb=W['s'], gest_stem=M['s'], R_stem=M['R_stem'], Ev_stem=M['Ev_stem'], L_stem=M['L_stem'], stem_ok=M['stem_ok'],
             sveip=S['sveip'], gest_steg=S['steg'], L_ansikt=S['L150'], svikt_mm=svikt_mm, **th)
    return t


# ---------------- mesh-primitiv ----------------
def frustum(p0, p1, r0, r1, n=16):
    ax = p1 - p0
    ax = ax / np.linalg.norm(ax)
    a = np.cross(ax, [1, 0, 0] if abs(ax[0]) < 0.9 else [0, 1, 0]); a /= np.linalg.norm(a)
    b = np.cross(ax, a)
    th = np.arange(n) / n * 2 * np.pi
    ring = np.cos(th)[:, None] * a + np.sin(th)[:, None] * b
    V = np.vstack([p0 + r0 * ring, p1 + r1 * ring, [p1]])
    F = [(j, (j + 1) % n, n + (j + 1) % n) for j in range(n)] + [(j, n + (j + 1) % n, n + j) for j in range(n)]
    F += [(2 * n, n + j, n + (j + 1) % n) for j in range(n)]
    return V, F


def prism(poly, z0, z1):
    n = len(poly)
    V = np.vstack([np.c_[poly, np.full(n, z0)], np.c_[poly, np.full(n, z1)], [[*poly.mean(0), z1]]])
    c = 2 * n
    F = [(j, (j + 1) % n, n + (j + 1) % n) for j in range(n)] + [(j, n + (j + 1) % n, n + j) for j in range(n)]
    F += [(c, n + j, n + (j + 1) % n) for j in range(n)]
    return V, F


def merge(meshes):
    V = np.vstack([m[0] for m in meshes])
    F, o = [], 0
    for Vm, Fm in meshes:
        F += [tuple(o + q for q in f) for f in Fm]
        o += len(Vm)
    return V, np.array(F)


# ---------------- husstil: perspektiv el 17, fov 19, varm beige lambert, SVART bakgrunn ----------------
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
BG = np.zeros(3)          # svart. Skuggen fell bort: ein grå skugge på svart les som glød, ikkje skugge.


def render(V, F, cam=None, emit=None):
    """Z-buffer, flat lambert, tosidig. emit: valfri bool-maske per flate (lysande opning, varm kvit). Returnerer (PIL 512², maske)."""
    cam = cam or Cam()
    S = cam.S
    p = cam.proj(V)
    T = V[F]
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-15
    n *= np.sign(((cam.eye - T.mean(1)) * n).sum(1))[:, None]
    lam = np.clip(n @ KEY, 0, 1)
    col = np.clip(ALB[None] * (0.46 + 0.60 * lam[:, None] + 0.08 * np.clip(n[:, 2], 0, 1)[:, None]), 0, 1)
    if emit is not None:
        col[np.asarray(emit, bool)] = np.array([1.0, 0.86, 0.66])
    img = np.ones((S, S, 3)) * BG
    zb = np.zeros((S, S))
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
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((S // 2, S // 2), Image.LANCZOS)
    return im, np.array(Image.fromarray(obj.astype(np.uint8) * 255).resize((S // 2, S // 2))) > 127


def brett(ims, grid, path, n=4):
    """grid: {(rad, kol): id} 1-indeksert. Svart, ingen tekst."""
    B = Image.new('RGB', (512 * n, 512 * n), 'black')
    for (r, c), i in grid.items():
        B.paste(ims[i], ((c - 1) * 512, (r - 1) * 512))
    B.save(path)


def stripe(ims_list, path):
    B = Image.new('RGB', (512 * len(ims_list), 512), 'black')
    for j, im in enumerate(ims_list):
        B.paste(im, (j * 512, 0))
    B.save(path)


def formkritikk(masks, grid):
    ious = []
    for (r, c), i in grid.items():
        for rr, cc in ((r, c + 1), (r + 1, c)):
            if (rr, cc) in grid:
                a, b = masks[i], masks[grid[(rr, cc)]]
                ious.append((a & b).sum() / max((a | b).sum(), 1))
    luft = {i: 1 - m.sum() / max(convex_hull_image(m).sum(), 1) for i, m in masks.items() if m.any()}
    return dict(iou_snitt=float(np.mean(ious)), iou_maks=float(np.max(ious)), luft=luft)
