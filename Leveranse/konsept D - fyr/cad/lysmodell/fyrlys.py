"""FYR side light engine: 3D Monte-Carlo ray tracer (numpy, vectorised).
Units mm, lm. z = 0 table, axis = z, azimuth 0 = +X (window).
Surfaces: conical lamellae (top/bottom/inner edge/outer edge), roof cone closed to the mast, radial ribs,
side walls (clip corner -> r_out at +-33.75), mast + strip + clip boxes, floor, ceiling,
sleeve (inner/outer cylinder with port), mantel inner wall with 6 slots through 2 mm wall.
Forward MC -> exitance tallies (for luminance), escape records (for table and intensity).
Backward cast from eye positions through the slots -> luminance seen.
"""
import math, ctypes, os
import numpy as np

try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)  # IDLE
except Exception:
    pass

DEG = math.pi / 180.0
EPS = 1e-6
INF = np.inf

# surface type ids
LAMT, LAMB, LAMEI, LAMEO, RIB, SIDE, BOXS, STRIP, FLOOR, CEIL, SLIN, SLOUT, MANT, SLOTW, ESC, GAPZ, ROOFT, ROOFB = range(18)
NAMES = ["lam_top", "lam_bot", "lam_edge_in", "lam_edge_out", "rib", "side", "box", "strip", "floor", "ceil",
         "sleeve_in", "sleeve_out", "mantel", "slotwall", "escape", "gapz", "roof_top", "roof_bot"]


def default_geo(**kw):
    g = dict(
        r_in=8.0, r_out=22.0, beta=40.0, pitch=8.0, wall=0.8, lam_az=33.75, fill_to_side=False,
        strip_w=8.0, strip_x=2.6, strip_z0=92.0, strip_z1=252.0,
        mast=(-1.0, 1.0, -7.5, 7.5, 44.0, 254.0),
        rib_az=(0.0, 11.25, -11.25, 22.5, -22.5),
        side_J=(2.5, 9.1),
        r_si=40.25, r_so=41.85, port_half=32.0, rot=0.0, port_z=(92.0, 262.0), sleeve_z=(82.0, 299.0),
        r_mi=43.0, r_mo=45.0, slot_w=3.4, slot_z=(93.0, 260.0),
        slot_az=(-28.125, -16.875, -5.625, 5.625, 16.875, 28.125),
        z_floor=84.0, z_ceil=255.0,
        # materials: (Rd, Rs, T, blur_deg)
        mat=dict(lam_top=(0.8, 0.0, 0.0, 0), lam_bot=(0.8, 0.0, 0.0, 0), lam_edge=(0.8, 0.0, 0.0, 0),
                 rib=(0.8, 0.0, 0.0, 0), side=(0.8, 0.0, 0.0, 0), box=(0.5, 0.0, 0.0, 0), strip=(0.5, 0.0, 0.0, 0),
                 clip=(0.8, 0.0, 0.0, 0), floor=(0.05, 0.0, 0.0, 0), ceil=(0.5, 0.0, 0.0, 0),
                 sleeve_in=(0.4, 0.0, 0.0, 0), sleeve_out=(0.4, 0.0, 0.0, 0), mantel=(0.05, 0.0, 0.0, 0)),
        flux=112.0,  # lm, side strip (7 W/m x 0.16 m x 100 lm/W)
    )
    for k, v in kw.items():
        if k == "mat":
            g["mat"] = dict(g["mat"], **v)
        else:
            g[k] = v
    derive(g)
    return g


def derive(g):
    T = math.tan(g["beta"] * DEG)
    tv = g["wall"] / math.cos(g["beta"] * DEG)
    g["T"], g["tv"] = T, tv
    g["h"] = (g["r_out"] - g["r_in"]) * T
    # roof: underside at rho = strip_x passes 0.5 above strip top
    c_roof_bot = g["strip_z1"] + 0.5 + T * math.hypot(g["strip_x"], g["strip_w"] / 2)
    g["c_roof"] = c_roof_bot + tv  # top surface constant: z + T rho = c
    g["z_roof_tip"] = g["c_roof"] - T * g["r_out"]
    # lamellae k>=1: outer tip z_k = z_roof_tip - k p ; top surface c_k = z_k + T r_out
    zs = []
    k = 1
    while True:
        zk = g["z_roof_tip"] - k * g["pitch"]
        if zk + g["h"] < g["strip_z0"] - g["pitch"] or zk < g["z_floor"] + 0.5:
            break
        zs.append(zk)
        k += 1
    g["z_lam"] = np.array(zs)
    g["c_lam"] = g["z_lam"] + T * g["r_out"]
    Sx, Sy = g["r_out"] * math.cos(g.get("side_az", 33.75) * DEG), g["r_out"] * math.sin(g.get("side_az", 33.75) * DEG)
    g["side_S"] = (Sx, Sy)
    # boxes: (x0,x1,y0,y1,z0,z1, matname)
    m = tuple(g["mast"])
    zt = g["z_floor"], g["c_roof"]
    boxes = [m + ("box",),
             (g["mast"][1], g["strip_x"], -g["strip_w"] / 2, g["strip_w"] / 2, g["strip_z0"], g["strip_z1"], "strip"),
             (-3.2, 2.5, 7.65, 9.1) + zt + ("clip",), (-3.2, 2.5, -9.1, -7.65) + zt + ("clip",),
             (-3.2, -1.15, -9.1, 9.1) + zt + ("clip",),
             (1.15, 2.5, 4.6, 7.65) + zt + ("clip",), (1.15, 2.5, -7.65, -4.6) + zt + ("clip",)]
    g["boxes"] = boxes
    return g


# ----------------------------------------------------------------------------- helpers
def az_deg(x, y):
    return np.degrees(np.arctan2(y, x))


def in_lam_region(g, x, y, full=False):
    """Lamella plan region: inside the side walls, in front of the clip, |az| <= lam_az (or up to side walls)."""
    a = az_deg(x, y)
    ok = x >= 2.5
    if not (g["fill_to_side"] or full):
        ok &= np.abs(a) <= g["lam_az"]
    # inside side walls: for upper wall J->S, point must be on the -y side (cross < 0)
    Jx, Jy = g["side_J"]
    Sx, Sy = g["side_S"]
    for s in (1.0, -1.0):
        cr = (Sx - Jx) * (s * y - Jy) - (Sy - Jy) * (x - Jx)
        ok &= cr <= 0
    return ok


def in_slot(g, x, y, z):
    ok = np.zeros(x.shape, bool)
    w2 = g["slot_w"] / 2
    z0, z1 = g["slot_z"]
    for a in g["slot_az"]:
        ca, sa = math.cos(a * DEG), math.sin(a * DEG)
        perp = -x * sa + y * ca
        along = x * ca + y * sa
        zz = np.clip(z, z0 + w2, z1 - w2)
        ok |= (along > 0) & (perp ** 2 + (z - zz) ** 2 <= w2 * w2)
    return ok


def in_port(g, x, y, z):
    a = az_deg(x, y) + g["rot"]  # sleeve turned clockwise by rot -> port centre at -rot
    return (np.abs(a) <= g["port_half"]) & (z >= g["port_z"][0]) & (z <= g["port_z"][1])


def cyl_roots(P, D, R):
    A = D[:, 0] ** 2 + D[:, 1] ** 2
    B = P[:, 0] * D[:, 0] + P[:, 1] * D[:, 1]
    C = P[:, 0] ** 2 + P[:, 1] ** 2 - R * R
    disc = B * B - A * C
    with np.errstate(invalid="ignore", divide="ignore"):
        sq = np.sqrt(np.maximum(disc, 0))
        t1 = (-B - sq) / A
        t2 = (-B + sq) / A
    bad = (disc < 0) | (A < 1e-12)
    t1[bad] = INF
    t2[bad] = INF
    return t1, t2


class Hit:
    def __init__(self, n):
        self.t = np.full(n, INF)
        self.sid = np.full(n, -1, int)
        self.nrm = np.zeros((n, 3))
        self.k = np.full(n, -1, int)  # sub index (lamella k, rib index, ...)

    def offer(self, t, sid, nrm, k=None):
        b = t < self.t
        if not b.any():
            return
        self.t[b] = t[b]
        self.sid[b] = sid
        if nrm.ndim == 1:
            self.nrm[b] = nrm
        else:
            self.nrm[b] = nrm[b]
        if k is not None:
            self.k[b] = k if np.isscalar(k) else k[b]


# ----------------------------------------------------------------------------- intersection
def intersect(g, P, D):
    n = len(P)
    H = Hit(n)
    T = g["T"]
    A = D[:, 0] ** 2 + D[:, 1] ** 2
    B = P[:, 0] * D[:, 0] + P[:, 1] * D[:, 1]
    C = P[:, 0] ** 2 + P[:, 1] ** 2
    TT = T * T

    def cone(c, rmin, rmax, sid, k):
        u = c - P[:, 2]
        qa = D[:, 2] ** 2 - TT * A
        qb = -2.0 * (u * D[:, 2] + TT * B)
        qc = u * u - TT * C
        disc = qb * qb - 4 * qa * qc
        best = np.full(n, INF)
        with np.errstate(invalid="ignore", divide="ignore"):
            sq = np.sqrt(np.maximum(disc, 0))
            lin = np.abs(qa) < 1e-12
            ra = np.where(lin, INF, (-qb - sq) / (2 * qa))
            rb = np.where(lin, -qc / qb, (-qb + sq) / (2 * qa))
            for t in (ra, rb):
                t = np.where(disc < 0, INF, t)
                ok = (t > EPS) & np.isfinite(t)
                x = P[:, 0] + t * D[:, 0]
                y = P[:, 1] + t * D[:, 1]
                z = P[:, 2] + t * D[:, 2]
                rho = np.sqrt(x * x + y * y)
                ok &= (c - z) >= -1e-9
                ok &= (rho >= rmin) & (rho <= rmax)
                if rmin == 0:
                    ok &= in_lam_region(g, x, y, True) | (rho < 9.5)
                else:
                    ok &= in_lam_region(g, x, y)
                best = np.where(ok & (t < best), t, best)
        if np.isfinite(best).any():
            x = P[:, 0] + best * D[:, 0]
            y = P[:, 1] + best * D[:, 1]
            rho = np.maximum(np.sqrt(x * x + y * y), 1e-9)
            nr = np.stack([T * x / rho, T * y / rho, np.ones(n)], 1)
            nr /= np.linalg.norm(nr, axis=1)[:, None]
            H.offer(best, sid, nr, k)

    # roof (top and bottom surface), closed to the mast
    cone(g["c_roof"], 0.0, g["r_out"], ROOFT, 0)
    cone(g["c_roof"] - g["tv"], 0.0, g["r_out"], ROOFB, 0)
    for k, c in enumerate(g["c_lam"]):
        cone(c, g["r_in"], g["r_out"], LAMT, k + 1)
        cone(c - g["tv"], g["r_in"], g["r_out"], LAMB, k + 1)

    # lamella edges (cylinder bands)
    for R, sid in ((g["r_in"], LAMEI), (g["r_out"], LAMEO)):
        t1, t2 = cyl_roots(P, D, R)
        for t in (t1, t2):
            ok = (t > EPS) & np.isfinite(t)
            tt = np.where(ok, t, 0)
            x = P[:, 0] + tt * D[:, 0]
            y = P[:, 1] + tt * D[:, 1]
            z = P[:, 2] + tt * D[:, 2]
            ok &= in_lam_region(g, x, y)
            if sid == LAMEI:
                ztop = g["z_lam"] + g["h"]
            else:
                ztop = np.concatenate([[g["z_roof_tip"]], g["z_lam"]])
            inb = np.zeros(n, bool)
            for zt in ztop:
                inb |= (z <= zt) & (z >= zt - g["tv"])
            ok &= inb
            nr = np.stack([x / R, y / R, np.zeros(n)], 1)
            H.offer(np.where(ok, t, INF), sid, nr)

    # ribs (radial half planes) and side walls (segments)
    zlo, zhi = g["z_floor"], g["c_roof"]
    segs = []
    for i, a in enumerate(g["rib_az"]):
        ca, sa = math.cos(a * DEG), math.sin(a * DEG)
        r1 = g.get("rib_r1", g["r_out"])
        r0 = g.get("rib_r0", g["r_in"])
        segs.append(((r0 * ca, r0 * sa), (r1 * ca, r1 * sa), RIB, i))
    Jx, Jy = g["side_J"]
    Sx, Sy = g["side_S"]
    segs.append(((Jx, Jy), (Sx, Sy), SIDE, 0))
    segs.append(((Jx, -Jy), (Sx, -Sy), SIDE, 1))
    for (p0, p1, sid, i) in segs:
        ux, uy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(ux, uy)
        ux, uy = ux / L, uy / L
        nx, ny = -uy, ux
        dn = D[:, 0] * nx + D[:, 1] * ny
        with np.errstate(invalid="ignore", divide="ignore"):
            t = ((p0[0] - P[:, 0]) * nx + (p0[1] - P[:, 1]) * ny) / dn
        ok = (t > EPS) & np.isfinite(t)
        tt = np.where(ok, t, 0)
        x = P[:, 0] + tt * D[:, 0]
        y = P[:, 1] + tt * D[:, 1]
        z = P[:, 2] + tt * D[:, 2]
        s = (x - p0[0]) * ux + (y - p0[1]) * uy
        rho = np.sqrt(x * x + y * y)
        ztop = np.where(rho <= g["r_out"], g["c_roof"] - g["T"] * rho, g["z_roof_tip"])
        ok &= (s >= 0) & (s <= L) & (z >= zlo) & (z <= ztop)
        H.offer(np.where(ok, t, INF), sid, np.array([nx, ny, 0.0]), i)

    # boxes
    for bi, b in enumerate(g["boxes"]):
        lo = np.array([b[0], b[2], b[4]])
        hi = np.array([b[1], b[3], b[5]])
        with np.errstate(invalid="ignore", divide="ignore"):
            inv = 1.0 / D
            t0 = (lo - P) * inv
            t1 = (hi - P) * inv
        tmin = np.minimum(t0, t1)
        tmax = np.maximum(t0, t1)
        tmin = np.nan_to_num(tmin, nan=-INF)
        tmax = np.nan_to_num(tmax, nan=INF)
        te = tmin.max(1)
        tx = tmax.min(1)
        ok = (te <= tx) & (te > EPS)
        ax = tmin.argmax(1)
        nr = np.zeros((n, 3))
        nr[np.arange(n), ax] = -np.sign(D[np.arange(n), ax])
        sid = STRIP if b[6] == "strip" else BOXS
        H.offer(np.where(ok, te, INF), sid, nr, bi)

    # floor / ceiling (inside sleeve)
    for zp, sid in ((g["z_floor"], FLOOR), (g["z_ceil"], CEIL)):
        with np.errstate(invalid="ignore", divide="ignore"):
            t = (zp - P[:, 2]) / D[:, 2]
        ok = (t > EPS) & np.isfinite(t)
        tt = np.where(ok, t, 0)
        x = P[:, 0] + tt * D[:, 0]
        y = P[:, 1] + tt * D[:, 1]
        ok &= x * x + y * y <= g["r_si"] ** 2
        H.offer(np.where(ok, t, INF), sid, np.array([0, 0, 1.0]))
    # gap z limits (between sleeve and mantel)
    for zp in (g["sleeve_z"][0], 265.0):
        with np.errstate(invalid="ignore", divide="ignore"):
            t = (zp - P[:, 2]) / D[:, 2]
        ok = (t > EPS) & np.isfinite(t)
        tt = np.where(ok, t, 0)
        x = P[:, 0] + tt * D[:, 0]
        y = P[:, 1] + tt * D[:, 1]
        r2 = x * x + y * y
        ok &= (r2 > g["r_si"] ** 2) & (r2 <= g["r_mi"] ** 2)
        H.offer(np.where(ok, t, INF), GAPZ, np.array([0, 0, 1.0]))

    # sleeve inner / outer
    for R, sid in ((g["r_si"], SLIN), (g["r_so"], SLOUT)):
        t1, t2 = cyl_roots(P, D, R)
        for t in (t1, t2):
            ok = (t > EPS) & np.isfinite(t)
            tt = np.where(ok, t, 0)
            x = P[:, 0] + tt * D[:, 0]
            y = P[:, 1] + tt * D[:, 1]
            z = P[:, 2] + tt * D[:, 2]
            ok &= (z >= g["sleeve_z"][0]) & (z <= g["sleeve_z"][1]) & ~in_port(g, x, y, z)
            nr = np.stack([x / R, y / R, np.zeros(n)], 1)
            H.offer(np.where(ok, t, INF), sid, nr)

    # mantel inner wall with slots
    t1, t2 = cyl_roots(P, D, g["r_mi"])
    for t in (t1, t2):
        ok = (t > EPS) & np.isfinite(t)
        tt = np.where(ok, t, 0)
        x = P[:, 0] + tt * D[:, 0]
        y = P[:, 1] + tt * D[:, 1]
        z = P[:, 2] + tt * D[:, 2]
        sl = in_slot(g, x, y, z)
        nr = np.stack([x / g["r_mi"], y / g["r_mi"], np.zeros(n)], 1)
        H.offer(np.where(ok & ~sl, t, INF), MANT, nr)
        # through the slot: check outer radius
        u1, u2 = cyl_roots(P, D, g["r_mo"])
        to = np.where(u2 > EPS, u2, INF)
        to_ = np.where(np.isfinite(to), to, 0)
        xo = P[:, 0] + to_ * D[:, 0]
        yo = P[:, 1] + to_ * D[:, 1]
        zo = P[:, 2] + to_ * D[:, 2]
        esc = ok & sl & in_slot(g, xo, yo, zo) & np.isfinite(to)
        H.offer(np.where(esc, t, INF), ESC, nr)
        H.offer(np.where(ok & sl & ~esc, t, INF), SLOTW, nr)
    return H


# ----------------------------------------------------------------------------- sampling
def rng_cosine(rng, nrm):
    """cosine-weighted directions about normals nrm (N,3)."""
    n = len(nrm)
    u1, u2 = rng.random(n), rng.random(n)
    r = np.sqrt(u1)
    phi = 2 * np.pi * u2
    lx, ly, lz = r * np.cos(phi), r * np.sin(phi), np.sqrt(np.maximum(0, 1 - u1))
    a = np.where(np.abs(nrm[:, 0:1]) < 0.9, np.array([[1.0, 0, 0]]), np.array([[0, 1.0, 0]]))
    t1 = np.cross(nrm, a)
    t1 /= np.linalg.norm(t1, axis=1)[:, None]
    t2 = np.cross(nrm, t1)
    return lx[:, None] * t1 + ly[:, None] * t2 + lz[:, None] * nrm


def source(g, rng, n):
    y = (rng.random(n) - 0.5) * g["strip_w"]
    z = g["strip_z0"] + rng.random(n) * (g["strip_z1"] - g["strip_z0"])
    P = np.stack([np.full(n, g["strip_x"] + 1e-4), y, z], 1)
    D = rng_cosine(rng, np.tile([1.0, 0, 0], (n, 1)))
    return P, D


def mat_of(g, sid, k):
    m = g["mat"]
    key = {LAMT: "lam_top", LAMB: "lam_bot", LAMEI: "lam_edge", LAMEO: "lam_edge", RIB: "rib", SIDE: "side",
           STRIP: "strip", FLOOR: "floor", CEIL: "ceil", SLIN: "sleeve_in", SLOUT: "sleeve_out", MANT: "mantel",
           ROOFT: "lam_top", ROOFB: "lam_bot"}.get(sid)
    if sid == BOXS:
        key = "box" if k == 0 else "clip"
    return m[key] if key else (0.0, 0.0, 0.0, 0)


# ----------------------------------------------------------------------------- tallies
class Tally:
    """exitance tallies (lm) for luminance maps. Lamella maps averaged over 'middle' lamellae."""

    def __init__(self, g):
        self.g = g
        self.rb = np.arange(0.0, g["r_out"] + 0.51, 0.5)
        self.ab = np.arange(-60.0, 60.01, 11.25 / 8)
        self.top = np.zeros((len(self.rb) - 1, len(self.ab) - 1))
        self.bot = np.zeros_like(self.top)
        self.rtop = np.zeros_like(self.top)
        self.rbot = np.zeros_like(self.top)
        nl = len(g["z_lam"])
        self.kmid = (3, nl - 3)
        self.zb = np.arange(80.0, 300.1, 4.0)
        self.aw = np.arange(-180.0, 180.01, 2.8125)
        self.sl = np.zeros((len(self.aw) - 1, len(self.zb) - 1))
        self.mt = np.zeros_like(self.sl)
        self.sb = np.arange(0, 40.1, 1.0)
        self.rib = np.zeros((len(g["rib_az"]) + 2, 2, len(self.sb) - 1))  # [rib, side, s]
        self.ribz = (110.0, 230.0)
        self.misc = {}

    def add(self, sid, k, P, W, side):
        g = self.g
        if len(W) == 0:
            return
        x, y, z = P[:, 0], P[:, 1], P[:, 2]
        if sid in (LAMT, LAMB):
            r0 = k == 0
            if r0.any():
                h, _, _ = np.histogram2d(np.hypot(x[r0], y[r0]), az_deg(x[r0], y[r0]), [self.rb, self.ab], weights=W[r0])
                (self.rtop if sid == LAMT else self.rbot)[...] += h
            m = (k >= self.kmid[0]) & (k < self.kmid[1])
            if m.any():
                h, _, _ = np.histogram2d(np.hypot(x[m], y[m]), az_deg(x[m], y[m]), [self.rb, self.ab], weights=W[m])
                (self.top if sid == LAMT else self.bot)[...] += h
        elif sid in (SLIN, MANT):
            h, _, _ = np.histogram2d(az_deg(x, y), z, [self.aw, self.zb], weights=W)
            (self.sl if sid == SLIN else self.mt)[...] += h
        elif sid in (RIB, SIDE):
            m = (z > self.ribz[0]) & (z < self.ribz[1])
            if m.any():
                for i in np.unique(k[m]):
                    mm = m & (k == i)
                    idx = i if sid == RIB else len(g["rib_az"]) + i
                    s = np.hypot(x[mm], y[mm])
                    for sd in (0, 1):
                        q = mm[mm] & (side[mm] == sd)
                        h, _ = np.histogram(s[q], self.sb, weights=W[mm][q])
                        self.rib[idx, sd] += h
        else:
            self.misc[sid] = self.misc.get(sid, 0.0) + W.sum()

    def maps(self):
        """luminance maps cd/m2 (lm/mm2 -> lm/m2 x 1e6 / pi)."""
        g = self.g
        nl = self.kmid[1] - self.kmid[0]
        r0, r1 = self.rb[:-1], self.rb[1:]
        da = np.diff(self.ab) * DEG
        area = 0.5 * (r1 ** 2 - r0 ** 2)[:, None] * da[None, :] / math.cos(g["beta"] * DEG)  # mm2 per lamella
        Lt = self.top / (area * nl) * 1e6 / math.pi
        Lb = self.bot / (area * nl) * 1e6 / math.pi
        aw = np.diff(self.aw) * DEG
        dz = np.diff(self.zb)
        Lsl = self.sl / (g["r_si"] * aw[:, None] * dz[None, :]) * 1e6 / math.pi
        Lmt = self.mt / (g["r_mi"] * aw[:, None] * dz[None, :]) * 1e6 / math.pi
        Lrib = self.rib / (np.diff(self.sb)[None, None, :] * (self.ribz[1] - self.ribz[0])) * 1e6 / math.pi
        nlam = len(g["z_lam"]) + 1
        a_edge = nlam * g["r_out"] * (2 * g.get("side_az", 33.75) * DEG) * g["tv"]
        Le = self.misc.get(LAMEO, 0.0) / a_edge * 1e6 / math.pi
        Lrt = self.rtop / area * 1e6 / math.pi
        Lrb = self.rbot / area * 1e6 / math.pi
        return dict(top=Lt, bot=Lb, rtop=Lrt, rbot=Lrb, sl=Lsl, mt=Lmt, rib=Lrib, edge_out=Le)


# ----------------------------------------------------------------------------- forward trace
def trace(g, nrays=200000, batch=50000, seed=1, maxb=14, tally=None, keep_esc=True):
    rng = np.random.default_rng(seed)
    esc = []
    absorbed = {}
    wray = g["flux"] / nrays
    nb_done = 0
    while nb_done < nrays:
        n = min(batch, nrays - nb_done)
        nb_done += n
        P, D = source(g, rng, n)
        W = np.full(n, wray)
        NB = np.zeros(n, int)
        LAST = np.full(n, -1, int)
        for b in range(maxb + 1):
            if len(P) == 0:
                break
            H = intersect(g, P, D)
            miss = ~np.isfinite(H.t)
            if miss.any():  # should not happen: count as lost
                absorbed["lost"] = absorbed.get("lost", 0) + W[miss].sum()
            hp = P + np.where(np.isfinite(H.t), H.t, 0)[:, None] * D
            e = (H.sid == ESC) & ~miss
            if e.any():
                # move to outer radius
                u1, u2 = cyl_roots(hp[e], D[e], g["r_mo"])
                po = hp[e] + np.where(np.isfinite(u2), u2, 0)[:, None] * D[e]
                esc.append(np.column_stack([po, D[e], W[e], NB[e], LAST[e]]))
            cont = ~miss & ~e
            for sid in (SLOTW, GAPZ):
                m = cont & (H.sid == sid)
                absorbed[NAMES[sid]] = absorbed.get(NAMES[sid], 0) + W[m].sum()
                cont &= ~m
            if b == maxb:
                absorbed["maxb"] = absorbed.get("maxb", 0) + W[cont].sum()
                break
            idx = np.nonzero(cont)[0]
            if len(idx) == 0:
                break
            P2, D2, W2, nr, sid, kk = hp[idx], D[idx], W[idx], H.nrm[idx], H.sid[idx], H.k[idx]
            Rd = np.zeros(len(idx)); Rs = np.zeros(len(idx)); Tt = np.zeros(len(idx)); bl = np.zeros(len(idx))
            for s in np.unique(sid):
                for kq in np.unique(kk[sid == s]) if s == BOXS else [None]:
                    m = (sid == s) if kq is None else ((sid == s) & (kk == kq))
                    mt = mat_of(g, s, kq if kq is not None else 0)
                    Rd[m], Rs[m], Tt[m], bl[m] = mt
            tot = Rd + Rs + Tt
            # absorption bookkeeping
            for s in np.unique(sid):
                m = sid == s
                absorbed[NAMES[s]] = absorbed.get(NAMES[s], 0) + (W2[m] * (1 - tot[m])).sum()
            W2 = W2 * tot
            live = tot > 0
            # facing normal (toward incoming side)
            dn = (D2 * nr).sum(1)
            side = (dn < 0).astype(int)  # 1: came from +normal side
            nf = np.where((dn < 0)[:, None], nr, -nr)
            u = rng.random(len(idx)) * np.maximum(tot, 1e-12)
            isd = u < Rd
            iss = (u >= Rd) & (u < Rd + Rs)
            ist = u >= Rd + Rs
            newD = np.empty_like(D2)
            if isd.any():
                newD[isd] = rng_cosine(rng, nf[isd])
            if iss.any():
                r = D2[iss] - 2 * (D2[iss] * nf[iss]).sum(1)[:, None] * nf[iss]
                sg = bl[iss] * DEG
                r = r + rng.normal(size=r.shape) * sg[:, None]
                r /= np.linalg.norm(r, axis=1)[:, None]
                flip = (r * nf[iss]).sum(1) < 0
                r[flip] = r[flip] - 2 * (r[flip] * nf[iss][flip]).sum(1)[:, None] * nf[iss][flip]
                newD[iss] = r
            newP = P2 + nf * 1e-4
            if ist.any():
                newD[ist] = rng_cosine(rng, -nf[ist])
                thick = np.where(np.isin(sid[ist], (LAMT, LAMB, ROOFT, ROOFB)), g["wall"], 1e-3)
                newP[ist] = P2[ist] - nf[ist] * (thick[:, None] + 1e-4)
            # tally diffuse exitance: which surface/side does it leave from
            if tally is not None:
                dif = live & (isd | ist)
                for s in np.unique(sid[dif]):
                    m = dif & (sid == s)
                    # leaving side: for reflection the incident side; for transmission the opposite side
                    leave_plus = np.where(ist[m], side[m] == 0, side[m] == 1)  # True: leaves on +normal side
                    if s in (LAMT, LAMB, ROOFT, ROOFB):
                        # +normal = up-outward. leaving up -> top map; leaving down -> bottom map
                        up = leave_plus
                        tally.add(LAMT, kk[m][up], P2[m][up], W2[m][up], None)
                        tally.add(LAMB, kk[m][~up], P2[m][~up], W2[m][~up], None)
                    else:
                        tally.add(s, kk[m], P2[m], W2[m], leave_plus.astype(int))
            # roulette
            keep = live & (W2 > wray * 1e-3)
            P, D, W = newP[keep], newD[keep], W2[keep]
            NB = NB[idx][keep] + 1
            LAST = sid[keep]
    E = np.vstack(esc) if esc else np.zeros((0, 9))
    return E, absorbed


# ----------------------------------------------------------------------------- backward eye cast
def eye_view(g, maps, tally, eye, n=40000, seed=3, L_strip=None, maxspec=4):
    """Sample points on the open slot apertures (outer radius), look from eye; return luminances (cd/m2)
    and the slot-area-weighted mean. Surfaces looked up from forward-tally maps (diffuse)."""
    rng = np.random.default_rng(seed)
    E = np.array(eye, float)
    pts = []
    for a in g["slot_az"]:
        m = n // len(g["slot_az"])
        perp = (rng.random(m) - 0.5) * g["slot_w"]
        z = g["slot_z"][0] + rng.random(m) * (g["slot_z"][1] - g["slot_z"][0])
        ca, sa = math.cos(a * DEG), math.sin(a * DEG)
        along = np.sqrt(g["r_mo"] ** 2 - perp ** 2)
        x = along * ca - perp * sa
        y = along * sa + perp * ca
        p = np.stack([x, y, z], 1)
        p = p[in_slot(g, x, y, z)]
        pts.append(p)
    P = np.vstack(pts)
    D = P - E
    D /= np.linalg.norm(D, axis=1)[:, None]
    # front-facing check: ray must go inward
    inward = (P[:, :2] * D[:, :2]).sum(1) < 0
    P, D = P[inward], D[inward]
    L = np.zeros(len(P))
    gain = np.ones(len(P))
    surf = np.full(len(P), -1)
    # first: does the ray pass the 2 mm slot wall? check inner radius crossing in slot
    t1, t2 = cyl_roots(P, D, g["r_mi"])
    tt = np.where(t1 > EPS, t1, 0)
    q = P + tt[:, None] * D
    through = (t1 > EPS) & in_slot(g, q[:, 0], q[:, 1], q[:, 2])
    surf[~through] = SLOTW
    act = np.nonzero(through)[0]
    Pc, Dc = q[through] + D[through] * 1e-4, D[through]
    for it in range(maxspec + 1):
        if len(act) == 0:
            break
        H = intersect(g, Pc, Dc)
        hp = Pc + np.where(np.isfinite(H.t), H.t, 0)[:, None] * Dc
        nxt = np.zeros(len(act), bool)
        sid = H.sid
        for s in np.unique(sid):
            m = sid == s
            ids = act[m]
            surf[ids] = s
            x, y, z = hp[m, 0], hp[m, 1], hp[m, 2]
            if s == STRIP:
                L[ids] = gain[ids] * L_strip
            elif s in (LAMT, ROOFT, LAMB, ROOFB):
                # which side is the viewer on? viewer sees the side the ray comes from
                dn = (Dc[m] * H.nrm[m]).sum(1)
                mp = maps["top"] if True else None
                ri = np.clip(np.searchsorted(tally.rb, np.hypot(x, y)) - 1, 0, maps["top"].shape[0] - 1)
                ai = np.clip(np.searchsorted(tally.ab, az_deg(x, y)) - 1, 0, maps["top"].shape[1] - 1)
                if s in (ROOFT, ROOFB):
                    Lv = np.where(dn < 0, maps["rtop"][ri, ai], maps["rbot"][ri, ai])
                else:
                    Lv = np.where(dn < 0, maps["top"][ri, ai], maps["bot"][ri, ai])
                L[ids] = gain[ids] * Lv
            elif s in (SLIN,):
                mt = mat_of(g, s, 0)
                if mt[1] > 0:  # specular part: continue
                    nxt[m] = True
                ai = np.clip(np.searchsorted(tally.aw, az_deg(x, y)) - 1, 0, maps["sl"].shape[0] - 1)
                zi = np.clip(np.searchsorted(tally.zb, z) - 1, 0, maps["sl"].shape[1] - 1)
                L[ids] += gain[ids] * maps["sl"][ai, zi]
            elif s == MANT:
                ai = np.clip(np.searchsorted(tally.aw, az_deg(x, y)) - 1, 0, maps["mt"].shape[0] - 1)
                zi = np.clip(np.searchsorted(tally.zb, z) - 1, 0, maps["mt"].shape[1] - 1)
                L[ids] += gain[ids] * maps["mt"][ai, zi]
            elif s in (RIB, SIDE):
                kk = H.k[m]
                idx = np.where(s == RIB, kk, len(g["rib_az"]) + kk)
                dn = (Dc[m] * H.nrm[m]).sum(1)
                sd = (dn < 0).astype(int)
                si = np.clip(np.searchsorted(tally.sb, np.hypot(x, y)) - 1, 0, maps["rib"].shape[2] - 1)
                L[ids] = gain[ids] * maps["rib"][idx, sd, si]
            elif s == LAMEO:
                L[ids] = gain[ids] * maps.get("edge_out", 0.0)
            else:
                L[ids] = 0.0  # mast/clip/floor/ceil/edges: small areas, set 0 (reported separately)
        if not nxt.any():
            break
        # continue specular rays
        m = nxt
        mt = mat_of(g, SLIN, 0)
        nf = H.nrm[m] * np.sign(-(Dc[m] * H.nrm[m]).sum(1))[:, None]
        r = Dc[m] - 2 * (Dc[m] * nf).sum(1)[:, None] * nf
        gain[act[m]] *= mt[1]
        act = act[m]
        Pc, Dc = hp[m] + nf * 1e-4, r
    return P, L, surf
