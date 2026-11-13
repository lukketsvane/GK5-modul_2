"""Lyssporar: same foton gjev tala og biletet.

Framoversporing (Monte Carlo) frå lyskjeldene. Foton blir talde på bord, vegg og lampeflater (lux),
og veglengda deira blir samla i eit voxelgitter (lys i lufta). Kameraet les flatene og gitteret.
Einingar: lumen, lux, cd/m2. Ingen fysisk måling: alt er modell.
"""
import numpy as np
import motor as mo

EPS = 1e-6
MAT = {
    'kropp': dict(t='matte', rho=0.42, col=(0.46, 0.43, 0.38)),
    'kvit': dict(t='matte', rho=0.85, col=(0.87, 0.86, 0.83)),
    'opalflate': dict(t='matte', rho=0.50, col=(0.52, 0.51, 0.49)),
    'satin': dict(t='satin', rs=0.65, sig=np.radians(11.0), rd=0.15, col=(0.80, 0.80, 0.80)),
    'halvblank': dict(t='satin', rs=0.85, sig=np.radians(3.0), rd=0.0, col=(0.85, 0.85, 0.85)),
    'staal': dict(t='matte', rho=0.35, col=(0.36, 0.36, 0.38)),
    'messing': dict(t='matte', rho=0.45, col=(0.66, 0.47, 0.20)),
    'svart': dict(t='matte', rho=0.03, col=(0.03, 0.03, 0.03)),
    'laptop': dict(t='matte', rho=0.10, col=(0.10, 0.10, 0.11)),
    'skjerm': dict(t='matte', rho=0.03, col=(0.03, 0.03, 0.035)),
    'bord': dict(t='matte', rho=0.40, col=(0.45, 0.40, 0.34)),
    'vegg': dict(t='matte', rho=0.70, col=(0.72, 0.70, 0.67)),
}
PRISME_SIG = np.radians(40.0 / 1.1774)     # halvverdivinkel 40 grader (ANTAKING frå flata.md)
ROD_SIG = np.radians(20.0)                 # spreiing langs staven (ANTAKING)


def ortho(n):
    a = np.where(np.abs(n[:, :1]) < 0.9, np.array([[1.0, 0, 0]]), np.array([[0, 1.0, 0]]))
    t1 = np.cross(n, a)
    t1 /= np.linalg.norm(t1, axis=1)[:, None]
    return t1, np.cross(n, t1)


def cos_hemi(n, rng):
    k = len(n)
    u1, ph = rng.random(k), 2 * np.pi * rng.random(k)
    r = np.sqrt(u1)
    t1, t2 = ortho(n)
    return t1 * (r * np.cos(ph))[:, None] + t2 * (r * np.sin(ph))[:, None] + n * np.sqrt(1 - u1)[:, None]


# ---- kjelder -----------------------------------------------------------------
def emit(L, n, rng):
    if L['k'] == 'spot':
        ct = 1 - rng.random(n) * (1 - np.cos(L['half']))
        st, ph = np.sqrt(1 - ct * ct), 2 * np.pi * rng.random(n)
        t1, t2 = mo.ortho1(L['d'])
        d = L['d'] * ct[:, None] + t1 * (st * np.cos(ph))[:, None] + t2 * (st * np.sin(ph))[:, None]
        rr, pp = L['r'] * np.sqrt(rng.random(n)), 2 * np.pi * rng.random(n)
        p = L['p'] + t1 * (rr * np.cos(pp))[:, None] + t2 * (rr * np.sin(pp))[:, None]
        return p, d, np.full(n, L['lm'] / n)
    if L['k'] == 'panel':
        if L['shape'] == 'disc':
            rr, pp = L['r'] * np.sqrt(rng.random(n)), 2 * np.pi * rng.random(n)
            p = L['c'] + L['u'] * (rr * np.cos(pp))[:, None] + L['v'] * (rr * np.sin(pp))[:, None]
        else:
            p = L['c'] + L['u'] * ((2 * rng.random(n) - 1) * L['hu'])[:, None] + L['v'] * ((2 * rng.random(n) - 1) * L['hv'])[:, None]
        nn = np.broadcast_to(L['n'], (n, 3)).copy()
        d = cos_hemi(nn, rng)
        w = np.full(n, L['lm'] / n)
        if L['prisme'] is not None:
            g = np.exp(-np.arctan2(d @ L['prisme'], d @ L['n']) ** 2 / (2 * PRISME_SIG ** 2))
            w *= g / g.mean()
        return p, d, w
    if L['k'] == 'rod':
        p = L['p0'] + (L['p1'] - L['p0']) * rng.random(n)[:, None]
        s = (-1 + np.sqrt(1 + 8 * rng.random(n))) / 2          # intensitet aukar 1:3 mot langt kast
        phi = L['a0'] + (L['a1'] - L['a0']) * s
        ax = mo.unit(L['p1'] - L['p0'])
        psi = np.clip(rng.normal(size=n) * ROD_SIG, -0.9, 0.9)
        d = L['akse'] * np.cos(phi)[:, None] + L['side'] * np.sin(phi)[:, None] + ax * np.tan(psi)[:, None]
        d /= np.linalg.norm(d, axis=1)[:, None]
        return p, d, np.full(n, L['lm'] / n)
    raise ValueError(L['k'])


# ---- optiske flater ------------------------------------------------------------
def isect(s, o, d):
    if s['kind'] == 'cap':
        oc = o - s['cs']
        b = (oc * d).sum(1)
        c = (oc * oc).sum(1) - s['R'] ** 2
        disc = b * b - c
        ok = disc > 0
        sq = np.sqrt(np.where(ok, disc, 0))
        best = np.full(len(o), np.inf)
        for t in (-b - sq, -b + sq):
            p = o + d * t[:, None]
            val = ok & (t > EPS) & (((s['cs'] - p) @ s['n']) >= s['cosa'] * s['R']) & (t < best)
            best = np.where(val, t, best)
        return best
    dn = d @ s['n']
    t = ((s['c'] - o) @ s['n']) / np.where(np.abs(dn) < 1e-12, 1e-12, dn)
    q = o + d * t[:, None] - s['c']
    if s['kind'] == 'disc':
        ok = (t > EPS) & ((q * q).sum(1) <= s['r'] ** 2)
    else:
        ok = (t > EPS) & (np.abs(q @ s['u']) <= s['hu']) & (np.abs(q @ s['v']) <= s['hv'])
    return np.where(ok, t, np.inf)


def normal(s, p):
    if s['kind'] == 'cap':
        return (s['cs'] - p) / s['R']
    return np.broadcast_to(s['n'], p.shape)


def halv(s):
    return (s['hu'], s['hv']) if s['kind'] == 'rect' else (s['r'], s['r'])


def scatter(mat, d, nn, w, rng):
    """Returnerer (ny retning, ny vekt, behald-maske)."""
    k = len(w)
    if mat['t'] == 'matte':
        return cos_hemi(nn, rng), w * mat['rho'], np.ones(k, bool)
    rs, rd = mat['rs'], mat['rd']
    spec = rng.random(k) < rs / (rs + rd)
    m = d - 2 * (d * nn).sum(1)[:, None] * nn
    t1, t2 = ortho(m)
    g = rng.normal(size=(k, 2)) * mat['sig']
    m2 = m + t1 * g[:, :1] + t2 * g[:, 1:]
    m2 /= np.linalg.norm(m2, axis=1)[:, None]
    keep = ~(spec & ((m2 * nn).sum(1) <= 0))
    nd = np.where(spec[:, None], m2, cos_hemi(nn, rng))
    return nd, w * (rs + rd), keep


class Gitter:
    """Voxelgitter for lys i lufta (fluens, lm/m2)."""

    def __init__(self, lo, hi, h):
        self.lo, self.h = np.array(lo, float), h
        self.shape = tuple(int(np.ceil((hi[i] - lo[i]) / h)) for i in range(3))
        self.acc = np.zeros(int(np.prod(self.shape)))

    def dep(self, pos, d, tend, w, rng, K=10):
        k = len(w)
        tt = (np.arange(K)[None, :] + rng.random((k, K))) / K * tend[:, None]
        idx = np.floor((pos[:, None, :] + d[:, None, :] * tt[:, :, None] - self.lo) / self.h).astype(np.int64)
        ok = np.all((idx >= 0) & (idx < np.array(self.shape)), axis=2)
        flat = (idx[..., 0] * self.shape[1] + idx[..., 1]) * self.shape[2] + idx[..., 2]
        wt = np.broadcast_to((w * tend / K)[:, None], (k, K))
        self.acc += np.bincount(flat[ok], weights=wt[ok], minlength=self.acc.size)

    def fluens(self):
        return (self.acc / self.h ** 3).reshape(self.shape).astype(np.float32)


def spor(sc, N, rute_bord=0.05, rute_flate=24, gitter=None, ekstra=(), seed=1, chunk=250_000):
    """Sporar N foton. Returnerer optiske flater med lumen per rute, bord- og veggruter."""
    rng = np.random.default_rng(seed)
    surfs = [d['opt'] for d in list(sc['delar']) + list(ekstra) if d.get('opt')]
    for s in surfs:
        hu, hv = halv(s)
        nb = rute_flate if rute_flate > 1 else max(4, int(round(2 * max(hu, hv) / rute_flate)))
        s['nb'] = nb
        s['E'] = np.zeros((2, nb, nb))
    bx0, bx1, by0, by1 = mo.BORD
    vx0, vx1, vz0, vz1 = mo.VEGG
    nbx, nby = int(round((bx1 - bx0) / rute_bord)), int(round((by1 - by0) / rute_bord))
    nvx, nvz = int(round((vx1 - vx0) / rute_bord)), int(round((vz1 - vz0) / rute_bord))
    bord, vegg = np.zeros(nbx * nby), np.zeros(nvx * nvz)
    ut = 0.0
    for L in sc['lys']:
        nL = max(1, int(N * L['lm'] / sum(x['lm'] for x in sc['lys'])))
        for c0 in range(0, nL, chunk):
            n = min(chunk, nL - c0)
            pos, d, w = emit(L, n, rng)
            w = w * (n / nL)
            for _ in range(6):
                k = len(w)
                if k == 0:
                    break
                tb, ib = np.full(k, np.inf), np.full(k, -1)
                for i, s in enumerate(surfs):
                    t = isect(s, pos, d)
                    m = t < tb
                    tb[m], ib[m] = t[m], i
                with np.errstate(divide='ignore', invalid='ignore'):
                    t = np.where(d[:, 2] < -1e-9, -pos[:, 2] / d[:, 2], np.inf)
                    px, py = pos[:, 0] + d[:, 0] * t, pos[:, 1] + d[:, 1] * t
                    m = (t > EPS) & (t < tb) & (px > bx0) & (px < bx1) & (py > by0) & (py < by1)
                    tb[m], ib[m] = t[m], -2
                    t = np.where(d[:, 1] > 1e-9, (mo.VEGG_Y - pos[:, 1]) / d[:, 1], np.inf)
                    px, pz = pos[:, 0] + d[:, 0] * t, pos[:, 2] + d[:, 2] * t
                    m = (t > EPS) & (t < tb) & (px > vx0) & (px < vx1) & (pz > vz0) & (pz < vz1)
                    tb[m], ib[m] = t[m], -3
                if gitter is not None:
                    gitter.dep(pos, d, np.minimum(tb, 3.0), w, rng)
                m = ib == -2
                if m.any():
                    p = pos[m] + d[m] * tb[m, None]
                    ix = np.clip(((p[:, 0] - bx0) / rute_bord).astype(int), 0, nbx - 1)
                    iy = np.clip(((p[:, 1] - by0) / rute_bord).astype(int), 0, nby - 1)
                    bord += np.bincount(ix * nby + iy, weights=w[m], minlength=bord.size)
                m = ib == -3
                if m.any():
                    p = pos[m] + d[m] * tb[m, None]
                    ix = np.clip(((p[:, 0] - vx0) / rute_bord).astype(int), 0, nvx - 1)
                    iz = np.clip(((p[:, 2] - vz0) / rute_bord).astype(int), 0, nvz - 1)
                    vegg += np.bincount(ix * nvz + iz, weights=w[m], minlength=vegg.size)
                ut += w[ib == -1].sum()
                P, Dn, Wn = [], [], []
                for i, s in enumerate(surfs):
                    m = ib == i
                    if not m.any():
                        continue
                    p, dd, ww = pos[m] + d[m] * tb[m, None], d[m], w[m]
                    nrm = normal(s, p)
                    front = (dd * nrm).sum(1) < 0
                    hu, hv = halv(s)
                    q = p - s['c']
                    iu = np.clip(((q @ s['u'] + hu) / (2 * hu) * s['nb']).astype(int), 0, s['nb'] - 1)
                    iv = np.clip(((q @ s['v'] + hv) / (2 * hv) * s['nb']).astype(int), 0, s['nb'] - 1)
                    for side, mn in ((0, s['mf']), (1, s['mb'])):
                        mm = front if side == 0 else ~front
                        if not mm.any():
                            continue
                        s['E'][side] += np.bincount(iu[mm] * s['nb'] + iv[mm], weights=ww[mm],
                                                    minlength=s['nb'] ** 2).reshape(s['nb'], s['nb'])
                        nn = nrm[mm] * (1.0 if side == 0 else -1.0)
                        nd, nw, keep = scatter(MAT[mn], dd[mm], nn, ww[mm], rng)
                        P.append((p[mm] + nn * 1e-5)[keep])
                        Dn.append(nd[keep])
                        Wn.append(nw[keep])
                if P:
                    pos, d, w = np.concatenate(P), np.concatenate(Dn), np.concatenate(Wn)
                else:
                    break
    return dict(surfs=surfs, bord=bord.reshape(nbx, nby), vegg=vegg.reshape(nvx, nvz), rute=rute_bord, ut=ut)


# ---- luminans frå ei flaterute mot eit punkt -----------------------------------------
def rutesenter(s, side):
    nb = s['nb']
    hu, hv = halv(s)
    g = (np.arange(nb) + 0.5) / nb * 2 - 1
    U, Vv = np.meshgrid(g * hu, g * hv, indexing='ij')
    p = s['c'] + U[..., None] * s['u'] + Vv[..., None] * s['v']
    inne = np.ones((nb, nb), bool)
    if s['kind'] != 'rect':
        inne = U ** 2 + Vv ** 2 <= s['r'] ** 2
    if s['kind'] == 'cap':
        sag = s['R'] - np.sqrt(s['R'] ** 2 - np.minimum(U ** 2 + Vv ** 2, s['r'] ** 2))
        p = p + sag[..., None] * s['n']
        n = (s['cs'] - p) / s['R']
    else:
        n = np.broadcast_to(s['n'], p.shape)
    n = n * (1.0 if side == 0 else -1.0)
    dA = (2 * hu / nb) * (2 * hv / nb)
    return p, n, inne, dA


def lum_mot(s, side, punkt, spots):
    """Luminans (cd/m2) frå kvar rute på ei side mot eit punkt. Matt: rho E / pi. Satin: lobe rundt spegelretninga."""
    p, n, inne, dA = rutesenter(s, side)
    E = s['E'][side] / dA
    mat = MAT[s['mf'] if side == 0 else s['mb']]
    wo = punkt - p
    r = np.linalg.norm(wo, axis=-1)
    wo = wo / r[..., None]
    co = (wo * n).sum(-1)
    if mat['t'] == 'matte':
        Lm = mat['rho'] * E / np.pi
    else:
        Lm = mat['rd'] * E / np.pi
        if spots:
            sp = max(spots, key=lambda x: x['lm'])
            wi = p - sp['p']
            wi /= np.linalg.norm(wi, axis=-1)[..., None]
            mir = wi - 2 * (wi * n).sum(-1)[..., None] * n
            delta = np.arccos(np.clip((mir * wo).sum(-1), -1, 1))
            g = np.exp(-delta ** 2 / (2 * mat['sig'] ** 2)) / (2 * np.pi * mat['sig'] ** 2)
            Lm = Lm + mat['rs'] * E * g / np.maximum(co, 0.05)
    Lm = np.where(inne & (co > 0), Lm, 0.0)
    return Lm, p, n, co, r, dA, inne


def panel_lum(L, retning):
    """Luminans frå ei opal lysflate i ei retning (ut frå flata)."""
    L0 = L['lm'] / (np.pi * L['A'])
    if L['prisme'] is None:
        return np.full(retning.shape[:-1], L0)
    th = np.arctan2(retning @ L['prisme'], np.maximum(retning @ L['n'], 1e-6))
    k = np.linspace(-np.pi / 2, np.pi / 2, 721)
    norm = np.trapezoid(np.exp(-k ** 2 / (2 * PRISME_SIG ** 2)) * np.cos(k) ** 2, k) / (np.pi / 2)
    return L0 * np.exp(-th ** 2 / (2 * PRISME_SIG ** 2)) / norm


def panelruter(L, nb=14):
    g = (np.arange(nb) + 0.5) / nb * 2 - 1
    if L['shape'] == 'disc':
        U, Vv = np.meshgrid(g * L['r'], g * L['r'], indexing='ij')
        inne = U ** 2 + Vv ** 2 <= L['r'] ** 2
        dA = (2 * L['r'] / nb) ** 2
    else:
        U, Vv = np.meshgrid(g * L['hu'], g * L['hv'], indexing='ij')
        inne = np.ones_like(U, bool)
        dA = (2 * L['hu'] / nb) * (2 * L['hv'] / nb)
    p = L['c'] + U[..., None] * L['u'] + Vv[..., None] * L['v']
    return p[inne], dA


def lappar(res, sc, mot=None):
    """Lambertske lappar (posisjon, normal, areal, luminans) for innsamling av indirekte lys."""
    P, Nn, A, Lm = [], [], [], []
    r = res['rute']
    for key, rho, nrm in (('bord', MAT['bord']['rho'], np.array([0, 0, 1.0])), ('vegg', MAT['vegg']['rho'], np.array([0, -1.0, 0]))):
        E = res[key] / r ** 2
        f = max(1, int(round(0.10 / r)))
        n0, n1 = (E.shape[0] // f) * f, (E.shape[1] // f) * f
        Ec = E[:n0, :n1].reshape(n0 // f, f, n1 // f, f).mean((1, 3))
        i, j = np.meshgrid(np.arange(Ec.shape[0]), np.arange(Ec.shape[1]), indexing='ij')
        if key == 'bord':
            p = np.stack([mo.BORD[0] + (i + 0.5) * f * r, mo.BORD[2] + (j + 0.5) * f * r, np.zeros_like(i, float)], -1)
        else:
            p = np.stack([mo.VEGG[0] + (i + 0.5) * f * r, np.full(i.shape, mo.VEGG_Y), mo.VEGG[2] + (j + 0.5) * f * r], -1)
        m = Ec > 0
        P.append(p[m]); Nn.append(np.broadcast_to(nrm, p[m].shape)); A.append(np.full(m.sum(), (f * r) ** 2)); Lm.append(rho * Ec[m] / np.pi)
    for s in res['surfs']:
        for side in (0, 1):
            p, n, inne, dA = rutesenter(s, side)
            mat = MAT[s['mf'] if side == 0 else s['mb']]
            rho = mat['rho'] if mat['t'] == 'matte' else mat['rd']
            L = rho * s['E'][side] / dA / np.pi
            m = inne & (L > 0)
            P.append(p[m]); Nn.append(n[m]); A.append(np.full(m.sum(), dA)); Lm.append(L[m])
    for L in sc['lys']:
        if L['k'] == 'panel':
            p, dA = panelruter(L)
            P.append(p); Nn.append(np.broadcast_to(L['n'], p.shape)); A.append(np.full(len(p), dA)); Lm.append(np.full(len(p), L['lm'] / (np.pi * L['A'])))
    return np.concatenate(P), np.concatenate(Nn), np.concatenate(A), np.concatenate(Lm)


def samle(pkt, nrm, lap, chunk=20000):
    """Lux i punkta frå lappane (utan skugge)."""
    P, Nn, A, Lm = lap
    ut = np.zeros(len(pkt))
    for i in range(0, len(pkt), chunk):
        w = P[None, :, :] - pkt[i:i + chunk, None, :]
        r2 = (w * w).sum(-1)
        r = np.sqrt(r2)
        c1 = np.maximum((w * nrm[i:i + chunk, None, :]).sum(-1), 0) / r
        c2 = np.maximum(-(w * Nn[None, :, :]).sum(-1), 0) / r
        ut[i:i + chunk] = (Lm * A * c1 * c2 / np.maximum(r2, 1e-4)).sum(1)
    return ut


# ---- tal ---------------------------------------------------------------------------
def synleg_kjelde(sc, res, auge):
    """Er sjølve kjelda (diode, linserekkje) synleg frå auget?"""
    for L in sc['lys']:
        if L['k'] == 'spot':
            v = auge - L['p']
            dist = np.linalg.norm(v)
            v = v / dist
            if v @ L['d'] > np.cos(L['half']):
                t = min(isect(s, L['p'][None], v[None])[0] for s in res['surfs']) if res['surfs'] else np.inf
                if t > dist:
                    return True
        if L['k'] == 'rod':
            mid = (L['p0'] + L['p1']) / 2
            v = mo.unit(auge - mid)
            phi = np.arctan2(v @ L['side'], v @ L['akse'])
            if L['a0'] - np.radians(3) < phi < L['a1'] + np.radians(3):
                return True
    return False


def tal(sc, res):
    """Alle mål per 100 lm frå kjelda (lineært i lysstraumen)."""
    r = res['rute']
    x0, x1, y0, y1 = mo.FELT
    E = res['bord'] / r ** 2
    ix0, ix1 = int(round((x0 - mo.BORD[0]) / r)), int(round((x1 - mo.BORD[0]) / r))
    iy0, iy1 = int(round((y0 - mo.BORD[2]) / r)), int(round((y1 - mo.BORD[2]) / r))
    felt = E[ix0:ix1, iy0:iy1]
    f = max(1, int(round(0.10 / r)))
    celler = felt.reshape(felt.shape[0] // f, f, felt.shape[1] // f, f).mean((1, 3))
    lm_src = sum(L['lm'] for L in sc['lys'])
    spots = [L for L in sc['lys'] if L['k'] == 'spot']
    # luminans mot auget
    Ls, As = [], []
    for s in res['surfs']:
        for side in (0, 1):
            Lm, p, n, co, rr, dA, inne = lum_mot(s, side, mo.AUGE, spots)
            m = inne & (co > 0)
            Ls.append(Lm[m]); As.append((dA * co)[m])
    for L in sc['lys']:
        if L['k'] == 'panel':
            p, dA = panelruter(L)
            v = mo.AUGE - p
            v /= np.linalg.norm(v, axis=1)[:, None]
            co = v @ L['n']
            m = co > 0
            Ls.append(panel_lum(L, v[m])); As.append(dA * co[m])
    Ls, As = np.concatenate(Ls), np.concatenate(As)
    lys = Ls >= 0.1 * Ls.max() if Ls.size and Ls.max() > 0 else np.zeros(0, bool)
    L95 = float(np.percentile(Ls[lys], 95)) if lys.any() else 0.0
    A_lys = float(As[lys].sum()) if lys.any() else 0.0
    # ansikt: loddrett flate mot skjermen (normal +y), frå lampeflatene åleine og med lånte flater
    ans = np.array([0.0, 0.0, 0.45])
    nf = np.array([0.0, 1.0, 0.0])
    e_lampe = 0.0
    for s in res['surfs']:
        for side in (0, 1):
            Lm, p, n, co, rr, dA, inne = lum_mot(s, side, ans, spots)
            w = (p - ans) / rr[..., None]
            e_lampe += float((Lm * dA * np.maximum(co, 0) * np.maximum(w @ nf, 0) / rr ** 2).sum())
    for L in sc['lys']:
        if L['k'] == 'panel':
            p, dA = panelruter(L)
            w = p - ans
            rr = np.linalg.norm(w, axis=1)
            w /= rr[:, None]
            co = -(w @ L['n'])
            m = co > 0
            e_lampe += float((panel_lum(L, -w[m]) * dA * co[m] * np.maximum(w[m] @ nf, 0) / rr[m] ** 2).sum())
    P, Nn, A, Lm = lappar(res, sc)
    lamp = np.zeros(len(P), bool)
    nrom = int((res['bord'] > 0).sum() + 0)  # berre for dokumentasjon
    rom = (np.abs(Nn[:, 2] - 1) < 1e-9) & (P[:, 2] == 0) | (np.abs(P[:, 1] - mo.VEGG_Y) < 1e-9)
    e_rom = float(samle(ans[None], nf[None], (P[rom], Nn[rom], A[rom], Lm[rom]))[0])
    # veggen bak skjermen
    Ev = res['vegg'] / r ** 2
    jx0, jx1 = int(round((x0 - mo.VEGG[0]) / r)), int(round((x1 - mo.VEGG[0]) / r))
    bak = Ev[jx0:jx1, 0:int(round(0.45 / r))]
    return dict(lm=lm_src, felt_lm=float(felt.sum() * r * r), felt_lx=float(felt.mean()),
                u0=float(celler.min() / max(celler.mean(), 1e-9)), bord_lm=float(res['bord'].sum()),
                vegg_lm=float(res['vegg'].sum()), ut_lm=float(res['ut']), L95=L95, A_lys_cm2=A_lys * 1e4,
                ans_lampe=e_lampe, ans_rom=e_rom, bak_lx=float(bak.mean()), vegg_Lmax=float(MAT['vegg']['rho'] * Ev.max() / np.pi),
                kjelde={h: synleg_kjelde(sc, res, np.array([0, 0, h])) for h in (0.25, 0.47, 0.60)})


# ---- kamera -------------------------------------------------------------------------
def stralar(C, T, fov, n):
    f = mo.unit(T - C)
    rt = mo.unit(np.cross(f, mo.Z))
    up = np.cross(rt, f)
    g = (np.arange(n) + 0.5) / n * 2 - 1
    X, Y = np.meshgrid(g, -g)
    tn = np.tan(np.radians(fov) / 2)
    D = f + X[..., None] * tn * rt + Y[..., None] * tn * up
    return (D / np.linalg.norm(D, axis=-1)[..., None]).reshape(-1, 3).astype(np.float64)


def treff_cyl(d, o, D):
    a = d['p1'] - d['p0']
    h = np.linalg.norm(a)
    a = a / h
    oc = o - d['p0']
    dpar, ocpar = D @ a, oc @ a
    dperp, ocperp = D - dpar[:, None] * a, oc - ocpar * a
    A = (dperp * dperp).sum(1)
    B = 2 * dperp @ ocperp
    Cc = ocperp @ ocperp - d['r'] ** 2
    disc = B * B - 4 * A * Cc
    ok = (disc > 0) & (A > 1e-12)
    t = np.where(ok, (-B - np.sqrt(np.where(ok, disc, 0))) / np.where(ok, 2 * A, 1), np.inf)
    s = ocpar + t * dpar
    t = np.where(ok & (t > EPS) & (s >= 0) & (s <= h), t, np.inf)
    with np.errstate(invalid='ignore'):
        nrm = (ocperp + t[:, None] * dperp) / d['r']
    nrm = np.where(np.isfinite(t)[:, None], nrm, 0.0)
    face = np.zeros(len(D), np.int8)
    with np.errstate(divide='ignore', invalid='ignore'):
        for sh, sign, fc in ((0.0, -1.0, 2), (h, 1.0, 1)):
            tc = (sh - ocpar) / dpar
            q = ocperp + tc[:, None] * dperp
            m = (tc > EPS) & (tc < t) & ((q * q).sum(1) <= d['r'] ** 2)
            t = np.where(m, tc, t)
            nrm[m] = sign * a
            face[m] = fc
    return t, nrm, face


def treff_box(d, o, D):
    ol, Dl = (o - d['c']) @ d['ax'].T, D @ d['ax'].T
    with np.errstate(divide='ignore', invalid='ignore'):
        t1, t2 = (-d['h'] - ol) / Dl, (d['h'] - ol) / Dl
    tn, tf = np.minimum(t1, t2), np.maximum(t1, t2)
    axn = np.argmax(tn, axis=1)
    tmin, tmax = tn.max(1), tf.min(1)
    ok = (tmax >= tmin) & (tmin > EPS)
    t = np.where(ok, tmin, np.inf)
    sg = -np.sign(Dl[np.arange(len(D)), axn])
    nrm = d['ax'][axn] * sg[:, None]
    face = np.where(axn == 2, np.where(sg > 0, 1, 2), 0).astype(np.int8)
    return t, nrm, face


def blur(a, sig):
    if sig <= 0:
        return a
    k = np.arange(-int(3 * sig) - 1, int(3 * sig) + 2)
    g = np.exp(-k ** 2 / (2 * sig ** 2))
    g /= g.sum()
    for ax in range(a.ndim):
        a = np.apply_along_axis(lambda v: np.convolve(v, g, mode='same'), ax, a)
    return a


def bilin(a, x, y):
    x, y = np.clip(x, 0, a.shape[0] - 1.001), np.clip(y, 0, a.shape[1] - 1.001)
    i, j = x.astype(int), y.astype(int)
    fx, fy = x - i, y - j
    return a[i, j] * (1 - fx) * (1 - fy) + a[i + 1, j] * fx * (1 - fy) + a[i, j + 1] * (1 - fx) * fy + a[i + 1, j + 1] * fx * fy


def bilete(sc, res, gitter, C, T, fov=36.0, n=720, ss=2, ekstra=(), sigma_luft=0.12, L_kvit=220.0, tint=(1.0, 0.84, 0.66)):
    """Kamerabilete i cd/m2, tonemappa. Returnerer uint8 (n, n, 3)."""
    M = n * ss
    D = stralar(C, T, fov, M)
    npx = len(D)
    tb = np.full(npx, np.inf)
    idb = np.full(npx, -1, np.int32)
    nb = np.zeros((npx, 3))
    fb = np.zeros(npx, np.int8)
    delar = list(sc['delar']) + list(ekstra)
    for i, d in enumerate(delar):
        t, nrm, face = (treff_cyl if d['k'] == 'cyl' else treff_box)(d, C, D)
        m = t < tb
        tb[m], idb[m], nb[m], fb[m] = t[m], i, nrm[m], face[m]
    bx0, bx1, by0, by1 = mo.BORD
    vx0, vx1, vz0, vz1 = mo.VEGG
    with np.errstate(divide='ignore', invalid='ignore'):
        t = np.where(D[:, 2] < -1e-9, -C[2] / D[:, 2], np.inf)
        px, py = C[0] + D[:, 0] * t, C[1] + D[:, 1] * t
        m = (t < tb) & (px > bx0) & (px < bx1) & (py > by0) & (py < by1)
        tb[m], idb[m] = t[m], -2
        t = np.where(D[:, 1] > 1e-9, (mo.VEGG_Y - C[1]) / D[:, 1], np.inf)
        px, pz = C[0] + D[:, 0] * t, C[2] + D[:, 2] * t
        m = (t < tb) & (px > vx0) & (px < vx1) & (pz > vz0) & (pz < vz1)
        tb[m], idb[m] = t[m], -3
    Pt = C + D * np.where(np.isfinite(tb), tb, 0.0)[:, None]
    rgb = np.zeros((npx, 3))
    r = res['rute']
    lap = lappar(res, sc)
    P, Nn, A, Lm = lap
    erbord = (P[:, 2] == 0) & (Nn[:, 2] > 0.99)
    ervegg = np.abs(P[:, 1] - mo.VEGG_Y) < 1e-9
    # bord og vegg: fotonruter + eitt sprett mellom bord og vegg
    for key, idv, mat, kilde in (('bord', -2, MAT['bord'], ~erbord), ('vegg', -3, MAT['vegg'], ~ervegg)):
        m = idb == idv
        if not m.any():
            continue
        E = blur(res[key] / r ** 2, 1.2)
        f = 5
        if key == 'bord':
            gx, gy = np.meshgrid(np.arange(bx0, bx1 + 1e-6, f * r), np.arange(by0, by1 + 1e-6, f * r), indexing='ij')
            pk = np.stack([gx, gy, np.zeros_like(gx)], -1).reshape(-1, 3)
            nk = np.broadcast_to(np.array([0, 0, 1.0]), pk.shape)
            u, v = (Pt[m, 0] - bx0) / r - 0.5, (Pt[m, 1] - by0) / r - 0.5
            ui, vi = (Pt[m, 0] - bx0) / (f * r), (Pt[m, 1] - by0) / (f * r)
        else:
            gx, gy = np.meshgrid(np.arange(vx0, vx1 + 1e-6, f * r), np.arange(vz0, vz1 + 1e-6, f * r), indexing='ij')
            pk = np.stack([gx, np.full_like(gx, mo.VEGG_Y), gy], -1).reshape(-1, 3)
            nk = np.broadcast_to(np.array([0, -1.0, 0]), pk.shape)
            u, v = (Pt[m, 0] - vx0) / r - 0.5, (Pt[m, 2] - vz0) / r - 0.5
            ui, vi = (Pt[m, 0] - vx0) / (f * r), (Pt[m, 2] - vz0) / (f * r)
        rom = erbord | ervegg
        Ei = samle(pk, nk, (P[rom & kilde], Nn[rom & kilde], A[rom & kilde], Lm[rom & kilde])).reshape(gx.shape)
        Et = bilin(E, u, v) + bilin(Ei, ui, vi)
        rgb[m] = (Et / np.pi)[:, None] * np.array(mat['col'])
    # lampe og laptop
    spots = [L for L in sc['lys'] if L['k'] == 'spot']
    lm_idx = np.where(idb >= 0)[0]
    if len(lm_idx):
        Eg = samle(Pt[lm_idx], nb[lm_idx], lap)
        for i, d in enumerate(delar):
            sel = idb[lm_idx] == i
            if not sel.any():
                continue
            for fc in (0, 1, 2):
                k = lm_idx[sel & (fb[lm_idx] == fc)]
                if not len(k):
                    continue
                mn = (d['mat'], d['mat1'], d['mat0'])[fc]
                mat = MAT[mn]
                Ed = np.zeros(len(k))
                s = d.get('opt')
                spec = np.zeros(len(k))
                if s is not None and fc > 0 and 'E' in s:      # 'E' manglar om delen ikkje var med i spor()
                    side = 0 if fc == 1 else 1
                    hu, hv = halv(s)
                    q = Pt[k] - s['c']
                    Eb = blur(s['E'][side], 0.8) / ((2 * hu / s['nb']) * (2 * hv / s['nb']))
                    Ed = bilin(Eb, (q @ s['u'] + hu) / (2 * hu) * s['nb'] - 0.5, (q @ s['v'] + hv) / (2 * hv) * s['nb'] - 0.5)
                    if mat['t'] == 'satin' and spots:
                        sp = max(spots, key=lambda x: x['lm'])
                        nn = (normal(s, Pt[k]) if s['kind'] == 'cap' else nb[k]) * 1.0
                        if s['kind'] == 'cap':
                            nn = nn * (1.0 if side == 0 else -1.0)
                        wi = Pt[k] - sp['p']
                        wi /= np.linalg.norm(wi, axis=1)[:, None]
                        mir = wi - 2 * (wi * nn).sum(1)[:, None] * nn
                        wo = -D[k]
                        delta = np.arccos(np.clip((mir * wo).sum(1), -1, 1))
                        g = np.exp(-delta ** 2 / (2 * mat['sig'] ** 2)) / (2 * np.pi * mat['sig'] ** 2)
                        spec = mat['rs'] * Ed * g / np.maximum((wo * nn).sum(1), 0.05)
                rho_col = np.array(mat['col']) * ((mat['rd'] / max(np.mean(mat['col']), 1e-6)) if mat['t'] == 'satin' else 1.0)
                Lpx = ((Ed + Eg[np.searchsorted(lm_idx, k)]) / np.pi)[:, None] * rho_col + spec[:, None]
                if d.get('lys') is not None and fc == 1:
                    Lpx = Lpx + panel_lum(sc['lys'][d['lys']], -D[k])[:, None]
                rgb[k] = Lpx
    # lys i lufta
    if gitter is not None and sigma_luft > 0:
        phi = gitter.fluens()
        phi = blur(phi, 0.8).astype(np.float32)
        Dh = stralar(C, T, fov, n)
        th = np.minimum(tb.reshape(M, M)[ss // 2::ss, ss // 2::ss].reshape(-1), 4.0)
        th = np.where(np.isfinite(th), th, 4.0)
        steg = gitter.h
        Lv = np.zeros(len(Dh), np.float32)
        sh = np.array(phi.shape)
        for k in range(int(4.0 / steg)):
            tt = (k + 0.5) * steg
            m = tt < th
            if not m.any():
                break
            idx = np.floor((C + Dh[m] * tt - gitter.lo) / steg).astype(np.int64)
            ok = np.all((idx >= 0) & (idx < sh), axis=1)
            val = np.zeros(m.sum(), np.float32)
            val[ok] = phi[idx[ok, 0], idx[ok, 1], idx[ok, 2]]
            Lv[m] += val * steg
        Lv = (Lv * sigma_luft / (4 * np.pi)).reshape(n, n)
        Lv = np.repeat(np.repeat(Lv, ss, 0), ss, 1).reshape(-1)
        rgb += Lv[:, None]
    rgb = rgb.reshape(n, ss, n, ss, 3).mean((1, 3)) * np.array(tint) / L_kvit
    x = np.maximum(rgb, 0)
    y = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)          # filmkurve (Narkowicz)
    return (np.clip(y, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8)
