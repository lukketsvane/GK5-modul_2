# -*- coding: utf-8 -*-
"""gransking/stadfest_M1_1.py · motprov av funn M1 (vridning i open U-søyle/arm, konsept c).
Uavhengig av granskarskripta: eigen FE-modell med 8-node heksaeder med inkompatible modar (Wilson/Taylor),
éin element gjennom veggtjukna, rektilineært gitter (alle plater er akseparallelle boksar).
Modellen tek med det handformlane ikkje kan: hjørnet søyle/arm (kopling mellom kvelving og vridning),
innfesting av foten (kvelving hindra), distorsjon av tverrsnittet og flikane som hovudet heng i.
Hovudet er stivt og fører lasta inn i flikane som RBE3 (mjuk fordeling, ingen ekstra stivleik).
Køyr: PYTHONIOENCODING=utf-8 python stadfest_M1_1.py [test|full]
"""
import sys, math, time, json, os
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

E, NU = 70e9, 0.33
G = E / (2 * (1 + NU))
lam = E * NU / ((1 + NU) * (1 - 2 * NU))
DM = np.zeros((6, 6))
DM[:3, :3] = lam
DM[[0, 1, 2], [0, 1, 2]] += 2 * G
DM[[3, 4, 5], [3, 4, 5]] = G
CORN = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]], float)
_ke = {}


def ke_box(a, b, c):
    key = (round(a, 7), round(b, 7), round(c, 7))
    if key in _ke:
        return _ke[key]
    g = 1 / math.sqrt(3)
    inv = np.array([2 / a, 2 / b, 2 / c])
    K = np.zeros((33, 33))
    for p in [(i, j, k) for i in (-g, g) for j in (-g, g) for k in (-g, g)]:
        p = np.array(p)
        dN = np.zeros((11, 3))
        for i, s in enumerate(CORN):
            q = 1 + s * p
            dN[i] = [s[0] * q[1] * q[2] / 8, s[1] * q[0] * q[2] / 8, s[2] * q[0] * q[1] / 8]
        dN[:8] *= inv
        for k in range(3):
            dN[8 + k, k] = -2 * p[k] * inv[k]
        B = np.zeros((6, 33))
        for i in range(11):
            dx, dy, dz = dN[i]
            B[0, 3 * i], B[1, 3 * i + 1], B[2, 3 * i + 2] = dx, dy, dz
            B[3, 3 * i], B[3, 3 * i + 1] = dy, dx
            B[4, 3 * i + 1], B[4, 3 * i + 2] = dz, dy
            B[5, 3 * i], B[5, 3 * i + 2] = dz, dx
        K += B.T @ DM @ B * (a * b * c / 8)
    Kc = K[:24, :24] - K[:24, 24:] @ np.linalg.solve(K[24:, 24:], K[24:, :24])
    _ke[key] = Kc
    return Kc


def akse(brot, h):
    pts = [brot[0]]
    for a, b in zip(brot[:-1], brot[1:]):
        n = max(1, int(round((b - a) / h)))
        pts += list(np.linspace(a, b, n + 1)[1:])
    return np.array(pts)


class Modell:
    def __init__(self, boksar, h, fest):
        bx = sorted({round(v, 7) for b in boksar for v in b[0:2]})
        by = sorted({round(v, 7) for b in boksar for v in b[2:4]})
        bz = sorted({round(v, 7) for b in boksar for v in b[4:6]})
        X, Y, Z = akse(bx, h), akse(by, h), akse(bz, h)
        self.X, self.Y, self.Z = X, Y, Z
        cx, cy, cz = (X[1:] + X[:-1]) / 2, (Y[1:] + Y[:-1]) / 2, (Z[1:] + Z[:-1]) / 2
        I, J, K = np.meshgrid(np.arange(len(cx)), np.arange(len(cy)), np.arange(len(cz)), indexing='ij')
        inn = np.zeros(I.shape, bool)
        for (x0, x1, y0, y1, z0, z1) in boksar:
            inn |= ((cx[I] > x0) & (cx[I] < x1) & (cy[J] > y0) & (cy[J] < y1) & (cz[K] > z0) & (cz[K] < z1))
        I, J, K = I[inn], J[inn], K[inn]
        nx, ny = len(X), len(Y)
        nid = lambda i, j, k: i + nx * (j + ny * k)
        conn = np.stack([nid(I + (s[0] > 0), J + (s[1] > 0), K + (s[2] > 0)) for s in CORN], 1)
        used, inv = np.unique(conn, return_inverse=True)
        self.conn = inv.reshape(conn.shape)
        ui = used % nx; uj = (used // nx) % ny; uk = used // (nx * ny)
        self.P = np.c_[X[ui], Y[uj], Z[uk]]
        n = len(used)
        self.ndof = 3 * n
        rows, cols, vals = [], [], []
        for e in range(len(I)):
            a, b, c = X[I[e] + 1] - X[I[e]], Y[J[e] + 1] - Y[J[e]], Z[K[e] + 1] - Z[K[e]]
            ke = ke_box(a, b, c)
            d = (3 * self.conn[e][:, None] + np.arange(3)).ravel()
            rows.append(np.repeat(d, 24)); cols.append(np.tile(d, 24)); vals.append(ke.ravel())
        Kg = sp.coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(self.ndof, self.ndof)).tocsc()
        fast = np.where(fest(self.P))[0]
        fd = (3 * fast[:, None] + np.arange(3)).ravel()
        self.fri = np.setdiff1d(np.arange(self.ndof), fd)
        t0 = time.time()
        self.lu = spla.splu(Kg[self.fri][:, self.fri].tocsc(), permc_spec='COLAMD')
        self.nel, self.nnode, self.tf = len(I), n, time.time() - t0

    def los(self, f):
        u = np.zeros(self.ndof)
        u[self.fri] = self.lu.solve(f[self.fri])
        return u.reshape(-1, 3)


def rbe3(P, nodar, punkt, F, M=np.zeros(3)):
    """Kraft F i punkt (+ moment M) fordelt på nodane som ei stiv-kropp-likevekt utan stivleik."""
    r = P[nodar] - P[nodar].mean(0)
    c = P[nodar].mean(0)
    Mt = np.cross(punkt - c, F) + M
    In = sum(np.dot(q, q) * np.eye(3) - np.outer(q, q) for q in r)
    w = np.linalg.solve(In, Mt)
    return F / len(nodar) + np.cross(w, r)


def stivfit(P, nodar, u):
    """Minste kvadrat stiv rørsle (u0, θ) av nodane."""
    r = P[nodar] - P[nodar].mean(0)
    A = np.zeros((3 * len(nodar), 6))
    for i, q in enumerate(r):
        A[3 * i:3 * i + 3, :3] = np.eye(3)
        A[3 * i:3 * i + 3, 3:] = -np.array([[0, -q[2], q[1]], [q[2], 0, -q[0]], [-q[1], q[0], 0]])
    s = np.linalg.lstsq(A, u[nodar].ravel(), rcond=None)[0]
    return s[:3], s[3:]


def p(*a):
    print(*a, flush=True)


MODE = sys.argv[1] if len(sys.argv) > 1 else 'full'
UT = {}

# ---------------- test: rett open U-søyle, kvelving hindra i botn, fri i toppen ----------------
if MODE in ('test', 'full'):
    t, L = 0.002, 0.747
    box = [(-0.05, 0.05, 0.028, 0.030, 0, L), (-0.05, -0.048, 0, 0.030, 0, L), (0.048, 0.05, 0, 0.030, 0, L)]
    t0 = time.time()
    m = Modell(box, 0.006, lambda P: P[:, 2] < 1e-9)
    topp = np.where(m.P[:, 2] > L - 1e-9)[0]
    f = np.zeros((m.nnode, 3))
    f[topp] = rbe3(m.P, topp, m.P[topp].mean(0), np.zeros(3), np.array([0, 0, 1.0]))
    u = m.los(f.ravel())
    th = stivfit(m.P, topp, u)[1][2]
    h_, b_ = 0.1 - t, 0.03 - t / 2
    J = (h_ + 2 * b_) * t ** 3 / 3
    Cw = t * b_ ** 3 * h_ ** 2 / 12 * (3 * b_ + 2 * h_) / (6 * b_ + h_)
    a = math.sqrt(E * Cw / (G * J))
    th_fri, th_kv = L / (G * J), (L - a * math.tanh(L / a)) / (G * J)
    # bøying om svak akse: 1 N i y i toppen
    f = np.zeros((m.nnode, 3)); f[topp] = rbe3(m.P, topp, m.P[topp].mean(0), np.array([0, 1.0, 0]))
    uy = stivfit(m.P, topp, m.los(f.ravel()))[0][1]
    A = 0.1 * t + 2 * 0.028 * t
    cU = (0.1 * t * (0.03 - t / 2) + 2 * 0.028 * t * 0.014) / A
    Isv = 0.1 * t ** 3 / 12 + 0.1 * t * (0.03 - t / 2 - cU) ** 2 + 2 * (t * 0.028 ** 3 / 12 + 0.028 * t * (0.014 - cU) ** 2)
    p(f'TEST rett U 100×30×2, L {L}: {m.nel} element, {m.nnode} nodar, {time.time() - t0:.1f} s')
    p(f'   vridning 1 N·m: FE {th:.4f} rad · Vlasov (kvelv. hindra i botn) {th_kv:.4f} · St.Venant fri {th_fri:.4f}  (FE/Vlasov {th / th_kv:.3f})')
    p(f'   bøying 1 N svak akse: FE {uy * 1e3:.4f} mm · Euler-Bernoulli {L ** 3 / (3 * E * Isv) * 1e3:.4f} mm')
    UT['test'] = dict(FE=th, vlasov=th_kv, fri=th_fri, a=a, bøy_FE=uy, bøy_EB=L ** 3 / (3 * E * Isv))

if MODE == 'test':
    sys.exit()

# ---------------- heile søyle + arm + flikar, konsept (c) FINAL ----------------
ys, zs, d, tp, bp, Lh = 0.22, 0.70, 0.05, 0.003, 0.16, 0.60
m_pl = 1190 * Lh * bp * (tp + 0.001)
m_st = 2700 * (0.016 + 2 * 0.020) * 0.0015 * Lh + 0.10
a_ul = m_pl * d / (m_pl + m_st)                 # vippeaksen under LED-lina (motor.akse_under_led)
Ax = np.array([ys, zs - a_ul])                  # vippeaksen i (y, z)
w_pl = d + tp / 2
z0, CY, CF, CW = 0.007, 0.512, 0.03, 0.10
za = zs + 0.03
yb = CY + CF                                     # bakkant søyle


def boksar(t, lukka, band=False):
    xa, xb = -CW / 2, CW / 2
    if band:                                                       # stivt hovud: massivt band mellom flikane i aksehøgd
        return boksar(t, lukka) + [(xa, xb, ys - 0.012, ys + 0.012, zs - 0.012, zs - 0.004)]
    B = [(xa, xb, yb - t, yb, z0, za + CF),                       # søyle, steg bak
         (xa, xa + t, CY, yb, z0, za + CF), (xb - t, xb, CY, yb, z0, za + CF),
         (xa, xb, ys - 0.012, yb, za + CF - t, za + CF),           # arm, steg oppe
         (xa, xa + t, ys - 0.012, yb, za, za + CF), (xb - t, xb, ys - 0.012, yb, za, za + CF),
         (xa, xa + t, ys - 0.012, ys + 0.012, zs - 0.012, za), (xb - t, xb, ys - 0.012, ys + 0.012, zs - 0.012, za)]  # flikar
    if lukka:
        B += [(xa, xb, CY, CY + t, z0, za + t),                       # lokk framme på søyla
              (xa, xb, ys - 0.012, CY + t, za, za + t)]               # lokk under armen
    return B


def hovudpunkt(alfa_deg, s, x):
    """punkt på plata (s: + = framkant ved α 0) og tangent for vipp om aksen."""
    al = math.radians(alfa_deg)
    rel = np.array([-s, -(w_pl - a_ul)])
    R = np.array([[math.cos(al), math.sin(al)], [-math.sin(al), math.cos(al)]])
    q = R @ rel
    tng = np.array([-q[1], q[0]]) / np.linalg.norm(q)
    return np.array([x, *(Ax + q)]), np.array([0, *tng]), np.linalg.norm(q)


I_z = None
VAR = (('open U 100×30×2', 0.002, False, 0.006, False), ('lukka 100×30×1,5', 0.0015, True, 0.006, False))
if MODE == 'variant':
    VAR = (('open U, gitter 4 mm', 0.002, False, 0.004, False), ('open U + stivt band mellom flikane', 0.002, False, 0.006, True))
for lab, t, lukka, h, band in VAR:
    t0 = time.time()
    m = Modell(boksar(t, lukka, band), h, lambda P: P[:, 2] < z0 + 1e-9)
    flik = np.where((m.P[:, 1] <= ys + 0.012 + 1e-9) & (m.P[:, 2] <= zs + 1e-9))[0]
    p(f'\n== {lab}: {m.nel} element, {m.nnode} nodar, faktorisering {m.tf:.1f} s, totalt {time.time() - t0:.1f} s, foten fast innspent (kvelving hindra)')
    res = {}
    for T in (0.20, 0.30):
        for gest, alfa in (('arbeid', 0), ('stemning', -105)):
            for x in (0.0, 0.30):
                best = None
                for s in (bp / 2, -bp / 2):
                    P, tg, r = hovudpunkt(alfa, s, x)
                    F = T / r * tg
                    f = np.zeros((m.nnode, 3)); f[flik] = rbe3(m.P, flik, P, F)
                    u = m.los(f.ravel())
                    dl = float((f * u).sum() / np.linalg.norm(F))       # forskyving i kraftretninga
                    u0, th = stivfit(m.P, flik, u)
                    uP = u0 + np.cross(th, P - m.P[flik].mean(0))
                    o = dict(s=s, F=float(np.linalg.norm(F)), d_mm=dl * 1e3, uP_mm=float(np.linalg.norm(uP)) * 1e3, th_deg=list(np.degrees(th)))
                    if best is None or o['d_mm'] > best['d_mm']:
                        best = o
                res[f'T{T}|{gest}|x{x}'] = best
                p(f'   T {T:.2f} {gest:8s} α {alfa:+4d}° hand i x {x:.2f}: F {best["F"]:.2f} N -> {best["d_mm"]:6.3f} mm i kraftretninga '
                  f'(|u| {best["uP_mm"]:.3f}); flikrotasjon x/y/z {best["th_deg"][0]:+.3f} {best["th_deg"][1]:+.3f} {best["th_deg"][2]:+.3f}°')
    # 10 N sidevegs midt på hovudet (i vippeaksen)
    P = np.array([0, *Ax]); f = np.zeros((m.nnode, 3)); f[flik] = rbe3(m.P, flik, P, np.array([10.0, 0, 0]))
    u = m.los(f.ravel()); d10 = (f * u).sum() / 10
    p(f'   10 N sidevegs (x) midt på hovudet: {d10 * 1e3:.2f} mm')
    res['10N_side_mm'] = d10 * 1e3
    # vridningsstivleik om søyla (moment om z på hovudet) og svingetal
    f = np.zeros((m.nnode, 3)); f[flik] = rbe3(m.P, flik, np.array([0, *Ax]), np.zeros(3), np.array([0, 0, 1.0]))
    u = m.los(f.ravel()); thz = stivfit(m.P, flik, u)[1][2]
    kz = 1 / thz
    if I_z is None:
        m_hd = m_pl + m_st + 2 * 2700 * 0.0015 * (0.02 + bp) / 2 * (d + tp)
        La = yb - CF / 2 - ys
        I_z = m_hd * (Lh ** 2 / 12 + La ** 2) + 2700 * (0.1 * 0.002 + 2 * 0.028 * 0.002) * La ** 3 / 3
    fz = math.sqrt(kz / I_z) / (2 * math.pi)
    p(f'   moment om z på hovudet: k {kz:.1f} N·m/rad, I_z {I_z:.4f} kg·m² -> sving om søyla {fz:.1f} Hz (armbøying med, masse i arm/søyle utanom hovudet ikkje)')
    res.update(kz=kz, I_z=I_z, f_Hz=fz)
    # nedbøying frå hovudvekta
    Wt = (m_pl + m_st) * 9.81
    f = np.zeros((m.nnode, 3)); f[flik] = rbe3(m.P, flik, np.array([0, *Ax]), np.array([0, 0, -Wt]))
    u = m.los(f.ravel()); res['eigenvekt_mm'] = (f * u).sum() / Wt * 1e3
    p(f'   eigenvekta til hovudet {Wt:.2f} N: {res["eigenvekt_mm"]:.3f} mm ned')
    UT[lab] = res

# skriv berre til skjermen (motprovet skal ikkje leggje att filer)
