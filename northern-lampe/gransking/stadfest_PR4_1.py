# -*- coding: utf-8 -*-
"""Motprov av PR4 (open U 100×30×2 i (c) ikkje rekna for vridning; svikt-raden blandar lastfall).

Uavhengig av premiss.py og mekanikk*.py: eigen volummodell av U-ramma (søyle + arm) i hex8-element med
inkompatible modar (Wilson-Taylor), eitt element gjennom veggen (2 mm), om lag 5 mm i flata. Hjørnet er heilsveist
slik geometri() i form04/motor.py teiknar det (flensane er samanhengande L-plater, stega overlappar). Kvelving vert
då hindra der modellen seier, ikkje der ein handformel føreset.
Hovudet + hengjarane er stive og festa til flensane ved armenden (y 0,208–0,232) med RBE3-fordeling (ingen ekstra stivleik).
Kontroll: rett U-utkraging mot Vlasov (kvelving hindra i rota) og Euler-Bernoulli.
Køyr: PYTHONIOENCODING=utf-8 python stadfest_PR4_1.py   (om lag 1 min)
"""
import os, sys, json, math, time
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl

HER = os.path.dirname(os.path.abspath(__file__))
E, NU = 70e9, 0.33
G = E / (2 * (1 + NU))
lam = E * NU / ((1 + NU) * (1 - 2 * NU))
DM = np.zeros((6, 6)); DM[:3, :3] = lam; DM[[0, 1, 2], [0, 1, 2]] += 2 * G; DM[3, 3] = DM[4, 4] = DM[5, 5] = G
CORN = np.array([[i, j, k] for k in (0, 1) for j in (0, 1) for i in (0, 1)])
XI = 2 * CORN - 1


def Bmat(dN):
    n = dN.shape[0]; B = np.zeros((6, 3 * n))
    B[0, 0::3] = dN[:, 0]; B[1, 1::3] = dN[:, 1]; B[2, 2::3] = dN[:, 2]
    B[3, 0::3] = dN[:, 1]; B[3, 1::3] = dN[:, 0]
    B[4, 1::3] = dN[:, 2]; B[4, 2::3] = dN[:, 1]
    B[5, 0::3] = dN[:, 2]; B[5, 2::3] = dN[:, 0]
    return B


_kc = {}
def ke(a, b, c):
    key = (round(a * 1e7), round(b * 1e7), round(c * 1e7))
    if key in _kc: return _kc[key]
    s = np.array([2 / a, 2 / b, 2 / c]); detJ = a * b * c / 8; g = 1 / math.sqrt(3)
    K = np.zeros((33, 33))
    for q0 in (-g, g):
        for q1 in (-g, g):
            for q2 in (-g, g):
                q = np.array([q0, q1, q2]); f = 1 + XI * q
                dNn = np.stack([XI[:, 0] * f[:, 1] * f[:, 2], XI[:, 1] * f[:, 0] * f[:, 2], XI[:, 2] * f[:, 0] * f[:, 1]], 1) / 8
                B = np.hstack([Bmat(dNn * s), Bmat(np.diag(-2 * q * s))])
                K += B.T @ DM @ B * detJ
    Kr = K[:24, :24] - K[:24, 24:] @ np.linalg.solve(K[24:, 24:], K[24:, :24])
    _kc[key] = Kr
    return Kr


def lines(keys, h=0.005):
    out = [keys[0]]
    for a, b in zip(keys[:-1], keys[1:]):
        n = max(1, int(round((b - a) / h)))
        out += list(np.linspace(a, b, n + 1)[1:])
    return np.array(out)


# geometri frå form04/motor.py FINAL: ys 0,22, zs 0,70, za = zs + 0,03, COL_Y 0,512, COL_F 0,03, COL_T 0,002, COL_W 0,10
YS, ZS, D_, BP = 0.22, 0.70, 0.05, 0.16
ZA, CY, CF, CT = ZS + 0.03, 0.512, 0.03, 0.002
Y0, Y1 = YS - 0.012, CY + CF                     # arm y 0,208–0,542
ZB, ZT = 0.004, ZA + CF                          # søyle z 0,004–0,760


def occ_arm(xc, yc, zc):
    fl = (np.abs(xc) > 0.049) & (yc > Y0) & (yc < Y1) & (zc > ZA) & (zc < ZT)
    web = (yc > Y0) & (yc < Y1) & (zc > ZT - CT) & (zc < ZT)
    return fl | web


def occ_col(xc, yc, zc):
    fl = (np.abs(xc) > 0.049) & (yc > CY) & (yc < Y1) & (zc > ZB) & (zc < ZT)
    web = (yc > Y1 - CT) & (yc < Y1) & (zc > ZB) & (zc < ZT)
    return fl | web


def bygg(occ, h=float(sys.argv[1]) if len(sys.argv) > 1 else 0.005):
    X = lines([-0.051, -0.049, 0.049, 0.051], h)
    Y = lines([Y0, YS + 0.012, CY, Y1 - CT, Y1], h)
    Z = lines([ZB, ZA, ZT - CT, ZT], h)
    xc, yc, zc = (X[:-1] + X[1:]) / 2, (Y[:-1] + Y[1:]) / 2, (Z[:-1] + Z[1:]) / 2
    I, J, K = np.meshgrid(np.arange(len(xc)), np.arange(len(yc)), np.arange(len(zc)), indexing='ij')
    I, J, K = I.ravel(), J.ravel(), K.ravel()
    m = occ(xc[I], yc[J], zc[K]); I, J, K = I[m], J[m], K[m]
    nx1, ny1 = len(X), len(Y)
    gid = lambda i, j, k: i + nx1 * (j + ny1 * k)
    en = np.stack([gid(I + c[0], J + c[1], K + c[2]) for c in CORN], 1)
    used, inv = np.unique(en, return_inverse=True); en = inv.reshape(en.shape)
    k_ = used // (nx1 * ny1); j_ = (used // nx1) % ny1; i_ = used % nx1
    P = np.stack([X[i_], Y[j_], Z[k_]], 1)
    dims = np.stack([X[I + 1] - X[I], Y[J + 1] - Y[J], Z[K + 1] - Z[K]], 1)
    cent = np.stack([xc[I], yc[J], zc[K]], 1)
    return P, en, dims, cent


def stivleik(P, en, dims):
    nd = 3 * len(P)
    dof = (3 * en[:, :, None] + np.arange(3)).reshape(len(en), 24)
    keys = np.round(dims * 1e7).astype(np.int64)
    uk, ui = np.unique(keys, axis=0, return_inverse=True)
    rows, cols, vals = [], [], []
    for u in range(len(uk)):
        sel = np.where(ui.ravel() == u)[0]
        Ke = ke(*(uk[u] / 1e7))
        d = dof[sel]
        rows.append(np.repeat(d, 24, axis=1).ravel()); cols.append(np.tile(d, (1, 24)).ravel()); vals.append(np.tile(Ke.ravel(), len(sel)))
    return sp.csc_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(nd, nd))


class Modell:
    def __init__(self, occ, fast, patch):
        t0 = time.time()
        self.P, self.en, dims, cent = bygg(occ)
        K = stivleik(self.P, self.en, dims)
        fx = np.where(fast(self.P))[0]
        fd = np.zeros(3 * len(self.P), bool); fd[(3 * fx[:, None] + np.arange(3)).ravel()] = True
        self.free = np.where(~fd)[0]
        self.lu = spl.splu(K[self.free][:, self.free].tocsc())
        pe = patch(cent)
        self.pn = np.unique(self.en[pe].ravel())
        self.c = self.P[self.pn].mean(0); self.r = self.P[self.pn] - self.c
        self.Jm = np.sum((self.r ** 2).sum(1)) * np.eye(3) - self.r.T @ self.r
        print(f'  modell: {len(self.en)} element, {len(self.P)} nodar, {len(self.free)} fridomsgrader, {len(self.pn)} nodar i festet, {time.time() - t0:.1f} s')

    def last(self, pkt, F, M_ekstra=np.zeros(3)):
        """kraft F i punktet pkt (stivt hovud) + eventuelt eit rent moment; gjev forskyving i pkt."""
        F = np.asarray(F, float); M = np.cross(np.asarray(pkt) - self.c, F) + M_ekstra
        w = np.linalg.solve(self.Jm, M)
        f = F / len(self.pn) + np.cross(w, self.r)
        b = np.zeros(3 * len(self.P)); b[(3 * self.pn[:, None] + np.arange(3)).ravel()] = f.ravel()
        u = np.zeros_like(b); u[self.free] = self.lu.solve(b[self.free])
        U = u.reshape(-1, 3)[self.pn]
        uc = U.mean(0); th = np.linalg.solve(self.Jm, np.cross(self.r, U).sum(0))
        return uc + np.cross(th, np.asarray(pkt) - self.c), th


patch_fl = lambda c: (np.abs(c[:, 0]) > 0.049) & (c[:, 1] < YS + 0.012) & (c[:, 2] > ZA)
OUT = {}

# ---------------- 1 kontroll: rett U-utkraging (berre armen, fast ved y 0,542) ----------------
print('1 kontroll: rett U 100×30×2, fast i rota (kvelving hindra), last på flensane ved spissen')
mk = Modell(occ_arm, lambda P: P[:, 1] > Y1 - 1e-9, patch_fl)
h_, b_, t_ = 0.100, 0.029, CT
Jsv = (h_ + 2 * b_) * t_ ** 3 / 3
Cw = t_ * b_ ** 3 * h_ ** 2 / 12 * (3 * b_ + 2 * h_) / (6 * b_ + h_)
lamv = math.sqrt(E * Cw / (G * Jsv))
L = Y1 - mk.c[1]
_, th = mk.last(mk.c, np.zeros(3), np.array([0, 1.0, 0]))
th_fri = L / (G * Jsv); th_vl = (L - lamv * math.tanh(L / lamv)) / (G * Jsv)
print(f'  T 1 N·m om y, L {L:.3f}: FE {th[1]:.5f} rad · Vlasov hindra i rota {th_vl:.5f} · Saint-Venant fri {th_fri:.5f}  (J {Jsv:.3e}, Cw {Cw:.3e}, λ {lamv:.3f} m)')
# boying: 1 N loddrett i tyngdepunktet av festet
zc_ = (2 * (CF - CT) * CT * (ZA + (CF - CT) / 2) + 0.102 * CT * (ZT - CT / 2)) / (2 * (CF - CT) * CT + 0.102 * CT)
Iv = 2 * (CT * (CF - CT) ** 3 / 12 + CT * (CF - CT) * (ZA + (CF - CT) / 2 - zc_) ** 2) + 0.102 * CT ** 3 / 12 + 0.102 * CT * (ZT - CT / 2 - zc_) ** 2
u, _ = mk.last(mk.c, np.array([0, 0, 1.0]))
print(f'  F 1 N i z: FE {u[2] * 1e3:.4f} mm · Euler-Bernoulli {L ** 3 / (3 * E * Iv) * 1e3:.4f} mm (I {Iv:.3e})')
OUT['kontroll'] = dict(theta_FE=float(th[1]), theta_vlasov_rot=th_vl, theta_fri=th_fri, J=Jsv, Cw=Cw, lam=lamv,
                       boy_FE_mm_per_N=float(u[2] * 1e3), boy_EB_mm_per_N=L ** 3 / (3 * E * Iv) * 1e3)

# ---------------- 2 ramma i (c) ----------------
print('2 U-ramma i (c): søylefot fast (z 0,004), hjørnet heilsveist')
mf = Modell(lambda x, y, z: occ_arm(x, y, z) | occ_col(x, y, z), lambda P: P[:, 2] < ZB + 1e-9, patch_fl)
print('2b same, berre steget fast i foten (flensane fri til å kvelve)')
mw = Modell(lambda x, y, z: occ_arm(x, y, z) | occ_col(x, y, z), lambda P: (P[:, 2] < ZB + 1e-9) & (P[:, 1] > Y1 - CT - 1e-9), patch_fl)


def kant(alfa, x, ovre, piv_cg=True):
    a = math.radians(alfa)
    ned = np.array([0, -math.sin(a), -math.cos(a)]); fram = np.array([0, -math.cos(a), math.sin(a)])
    c0 = np.array([0, YS, ZS]); top = c0 + D_ * ned
    k1, k2 = top - BP / 2 * fram, top + BP / 2 * fram
    k = (k1 if k1[2] > k2[2] else k2) if ovre else (k1 if k1[1] < k2[1] else k2)
    piv = c0 + (0.033 * ned if piv_cg else 0)
    r = k - piv; t = np.cross([1.0, 0, 0], r); t /= np.linalg.norm(t)
    return np.array([x, k[1], k[2]]), t, float(np.linalg.norm(r))


fall = []
# granskaren: 2,5 N, tangent om LED-lina, r (−0,08, −0,05)
r = np.array([-0.08, -0.05]); tg = np.array([r[1], -r[0]]) / np.linalg.norm(r)
fall.append(('granskar: 2,5 N tangent om LED-lina', 2.5 * np.array([0, tg[0], tg[1]]), np.array([0.0, YS - 0.08, ZS - 0.05])))
fall.append(('motor: 2,5 N loddrett, framkant', np.array([0, 0, 2.5]), np.array([0.0, YS - BP / 2, ZS - D_])))
for lab, alfa, ovre in (('arbeid α 0, framkant, T 0,20 om tyngdepunktet', 0.0, False), ('stemning α −105, øvre kant, T 0,20 om tyngdepunktet', -105.0, True),
                        ('stemning α −50, øvre kant, T 0,20 om tyngdepunktet', -50.0, True)):
    P0, t, rr = kant(alfa, 0.0, ovre)
    fall.append((lab, 0.20 / rr * t, P0))

res = []
for lab, F, P0 in fall:
    for x in (0.0, 0.30):
        P = P0.copy(); P[0] = x
        row = dict(fall=lab, x=x, F=F.tolist(), F_N=float(np.linalg.norm(F)))
        for nm, m in (('fot_fast', mf), ('berre_steg_fast', mw)):
            u, _ = m.last(P, F)
            row[nm] = dict(u_mm=(u * 1e3).tolist(), abs_mm=float(np.linalg.norm(u) * 1e3), langs_F_mm=float(u @ F / np.linalg.norm(F) * 1e3))
        res.append(row)
        print(f'  {lab:52s} x {x:.2f} F {row["F_N"]:.2f} N (y {F[1]:+.2f}, z {F[2]:+.2f}): |u| fot fast {row["fot_fast"]["abs_mm"]:6.3f} mm '
              f'(langs F {row["fot_fast"]["langs_F_mm"]:6.3f}; u y {row["fot_fast"]["u_mm"][1]:+.3f} z {row["fot_fast"]["u_mm"][2]:+.3f}) · berre steg fast {row["berre_steg_fast"]["abs_mm"]:6.3f} mm')
OUT['ramme'] = res

# granskaren sin handformel, attgjeven
Fy, Fz = 2.5 * abs(tg[0]), 2.5 * abs(tg[1])
GJ = 26e9 * (0.10 + 2 * 0.03) * 0.002 ** 3 / 3
arm = Fz * 0.30 * 0.322 / GJ * 0.30 * 1e3; col = Fy * 0.30 * 0.73 / GJ * 0.30 * 1e3
OUT['granskar_handformel'] = dict(arm_mm=arm, soyle_mm=col, sum_mm=arm + col, vektor_mm=math.hypot(arm, col), langs_F_mm=(Fz * arm + Fy * col) / 2.5)
print(f'  handformel (granskar): arm {arm:.2f} + søyle {col:.2f} = {arm + col:.2f} mm; som vektor {math.hypot(arm, col):.2f}, langs F {(Fz * arm + Fy * col) / 2.5:.2f}')
print(json.dumps(OUT['kontroll'], ensure_ascii=False))   # ingen fil: motprovet skriv berre til stdout
