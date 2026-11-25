"""Part 6: top emitter cavity under the opal disc. 3D MC, numpy.
Cavity: white skirt cylinder r = Rw from floor z_f to disc underside z_d = 278; floor white; disc opal
(Lambertian diffuse transmission T, diffuse reflection R). Emitters: strip pieces 8 mm wide, Lambertian.
Output: disc exit luminance profile L(r) (cd/m2 per lm of emitter), efficiency, uniformity.
Run: py -3 topp.py
"""
import math, json, ctypes, sys
import numpy as np
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception:
    pass
from fyrlys import rng_cosine

INF = np.inf


def emitters(kind):
    """list of (cx, cy, half_len_along_u, half_w, ux, uy, nz) rectangles in plan; nz=+1 up, -1 down,
    or ('wall', z, az_center, half_len, n) for inward-facing pieces on the skirt."""
    E = []
    if kind == "2x25_centre":
        for y in (-4.0, 4.0):
            E.append((0.0, y, 12.5, 4.0, 1.0, 0.0, 1))
    elif kind == "4x25_ring22":
        for a in (0, 90, 180, 270):
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            E.append((22 * c, 22 * s, 12.5, 4.0, -s, c, 1))
    elif kind == "6x15_ring26":
        for a in range(0, 360, 60):
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            E.append((26 * c, 26 * s, 7.5, 4.0, -s, c, 1))
    elif kind == "2x25_ring22":
        for a in (90, 270):
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            E.append((22 * c, 22 * s, 12.5, 4.0, -s, c, 1))
    elif kind == "3x25_ring22":
        for a in (0, 120, 240):
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            E.append((22 * c, 22 * s, 12.5, 4.0, -s, c, 1))
    elif kind == "3x25_ring26":
        for a in (0, 120, 240):
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            E.append((26 * c, 26 * s, 12.5, 4.0, -s, c, 1))
    elif kind == "2x25_down_shield":
        for y in (-4.0, 4.0):
            E.append((0.0, y, 12.5, 4.0, 1.0, 0.0, -1))
    return E


def run(kind="2x25_centre", h=21.0, Rw=38.0, Tdisc=0.44, Rdisc=0.52, rho_w=0.80, rho_f=0.80, rho_e=0.5,
        shield=None, n=200000, seed=1, z_d=278.0, wall_spec=0.0):
    rng = np.random.default_rng(seed)
    z_e = z_d - h                     # emitting surface height (up-facing) or shield-mounted (down-facing)
    z_f = z_e - 1.6 if kind != "2x25_down_shield" else z_d - h
    E = emitters(kind)
    # sample emitters
    k = rng.integers(0, len(E), n)
    P = np.zeros((n, 3)); D = np.zeros((n, 3))
    for i, e in enumerate(E):
        m = k == i
        cx, cy, hl, hw, ux, uy, nz = e
        a = (rng.random(m.sum()) * 2 - 1) * hl
        b = (rng.random(m.sum()) * 2 - 1) * hw
        P[m, 0] = cx + a * ux - b * uy
        P[m, 1] = cy + a * uy + b * ux
        if nz > 0:
            P[m, 2] = z_e
            D[m] = rng_cosine(rng, np.tile([0, 0, 1.0], (m.sum(), 1)))
        else:
            P[m, 2] = shield[1] - 1.6 - 1e-4   # strip under the shield, facing down
            D[m] = rng_cosine(rng, np.tile([0, 0, -1.0], (m.sum(), 1)))
    W = np.full(n, 1.0 / n)
    rb = np.arange(0, Rw + 0.01, 2.0)
    out = np.zeros(len(rb) - 1)
    xb = np.arange(-36.0, 36.01, 4.0)
    map2 = np.zeros((len(xb) - 1, len(xb) - 1))
    absb = dict(floor=0.0, wall=0.0, disc=0.0, emit=0.0, shield=0.0)
    for bounce in range(40):
        if len(P) == 0:
            break
        nn = len(P)
        tbest = np.full(nn, INF); sid = np.full(nn, -1)
        # disc plane
        with np.errstate(divide="ignore", invalid="ignore"):
            t = (z_d - P[:, 2]) / D[:, 2]
            ok = (t > 1e-7)
            x = P[:, 0] + t * D[:, 0]; y = P[:, 1] + t * D[:, 1]
            ok &= x * x + y * y <= Rw * Rw
            b = ok & (t < tbest); tbest[b] = t[b]; sid[b] = 0
            t = (z_f - P[:, 2]) / D[:, 2]
            ok = (t > 1e-7)
            x = P[:, 0] + t * D[:, 0]; y = P[:, 1] + t * D[:, 1]
            ok &= x * x + y * y <= Rw * Rw
            b = ok & (t < tbest); tbest[b] = t[b]; sid[b] = 1
            if shield is not None:
                Rs, zs = shield
                for zz in (zs, zs - 1.6):
                    t = (zz - P[:, 2]) / D[:, 2]
                    ok = (t > 1e-7)
                    x = P[:, 0] + t * D[:, 0]; y = P[:, 1] + t * D[:, 1]
                    ok &= x * x + y * y <= Rs * Rs
                    b = ok & (t < tbest); tbest[b] = t[b]; sid[b] = 3
            # wall
            A = D[:, 0] ** 2 + D[:, 1] ** 2
            B = P[:, 0] * D[:, 0] + P[:, 1] * D[:, 1]
            C = P[:, 0] ** 2 + P[:, 1] ** 2 - Rw * Rw
            t = (-B + np.sqrt(np.maximum(B * B - A * C, 0))) / A
            ok = (t > 1e-7) & np.isfinite(t)
            b = ok & (t < tbest); tbest[b] = t[b]; sid[b] = 2
        H = P + np.where(np.isfinite(tbest), tbest, 0)[:, None] * D
        lost = sid < 0
        u = rng.random(nn)
        newD = np.zeros_like(D); keep = np.zeros(nn, bool)
        # disc
        m = sid == 0
        tr = m & (u < Tdisc)
        r = np.hypot(H[tr, 0], H[tr, 1])
        out += np.histogram(r, rb, weights=W[tr])[0]
        map2 += np.histogram2d(H[tr, 0], H[tr, 1], [xb, xb], weights=W[tr])[0]
        rf = m & (u >= Tdisc) & (u < Tdisc + Rdisc)
        absb["disc"] += W[m & (u >= Tdisc + Rdisc)].sum()
        newD[rf] = rng_cosine(rng, np.tile([0, 0, -1.0], (rf.sum(), 1)))
        keep |= rf
        # floor (emitter footprint reflectance rho_e)
        m = sid == 1
        onE = np.zeros(nn, bool)
        if kind != "2x25_down_shield":
            for e in E:
                cx, cy, hl, hw, ux, uy, nz = e
                dx, dy = H[:, 0] - cx, H[:, 1] - cy
                onE |= (np.abs(dx * ux + dy * uy) <= hl) & (np.abs(-dx * uy + dy * ux) <= hw)
        rr = np.where(onE, rho_e, rho_f)
        rf = m & (u < rr)
        absb["floor"] += W[m & ~onE & ~(u < rr)].sum(); absb["emit"] += W[m & onE & ~(u < rr)].sum()
        newD[rf] = rng_cosine(rng, np.tile([0, 0, 1.0], (rf.sum(), 1)))
        keep |= rf
        # wall
        m = sid == 2
        nrm = -np.stack([H[:, 0] / Rw, H[:, 1] / Rw, np.zeros(nn)], 1)
        rf = m & (u < rho_w)
        absb["wall"] += W[m & ~(u < rho_w)].sum()
        if rf.any():
            spec = rf & (rng.random(nn) < wall_spec)
            dif = rf & ~spec
            newD[dif] = rng_cosine(rng, nrm[dif])
            dd = D[spec]; nn_ = nrm[spec]
            newD[spec] = dd - 2 * (dd * nn_).sum(1)[:, None] * nn_
        keep |= rf
        # shield (white both sides; emitter on its underside reflects rho_e)
        m = sid == 3
        if m.any():
            rf = m & (u < rho_f)
            absb["shield"] += W[m & ~rf].sum()
            up = D[:, 2] < 0  # hit top surface coming down -> reflect up
            nz = np.where(up, 1.0, -1.0)
            newD[rf] = rng_cosine(rng, np.stack([np.zeros(rf.sum()), np.zeros(rf.sum()), nz[rf]], 1))
            keep |= rf
        newP = H + 1e-5 * newD
        P, D, W = newP[keep], newD[keep], W[keep]
    area = math.pi * (rb[1:] ** 2 - rb[:-1] ** 2)  # mm2
    L_per_lm = out / area * 1e6 / math.pi   # cd/m2 per lm of emitter
    eff = out.sum()
    rc = 0.5 * (rb[1:] + rb[:-1])
    xc = 0.5 * (xb[1:] + xb[:-1])
    inside = (xc[:, None] ** 2 + xc[None, :] ** 2) <= 33.0 ** 2
    L2 = map2 / 16.0 * 1e6 / math.pi
    sm = L2.copy()
    np.save(__file__.replace("topp.py", f"topp_map_{kind}_{Tdisc}.npy"), L2)
    hot = dict(max_over_mean_2d=round(float(L2[inside].max() / L2[inside].mean()), 2),
               max_min_2d=round(float(L2[inside].max() / max(L2[inside].min(), 1e-9)), 2))
    return dict(hot=hot, kind=kind, h=h, Tdisc=Tdisc, Rdisc=Rdisc, rho_w=rho_w, eff=round(float(eff), 3), rc=rc.tolist(),
                L_per_lm=[round(float(v), 1) for v in L_per_lm],
                centre_edge=round(float(L_per_lm[0] / L_per_lm[-2]), 2),
                max_min=round(float(L_per_lm[:-1].max() / L_per_lm[:-1].min()), 2),
                L_mean_per_lm=round(float(eff / (math.pi * Rw * Rw) * 1e6 / math.pi), 1),
                absorbed={k: round(v, 3) for k, v in absb.items()})


if __name__ == "__main__":
    res = []
    cases = [
        dict(kind="2x25_ring22", h=21),
        dict(kind="3x25_ring22", h=21),
        dict(kind="3x25_ring26", h=21),
        dict(kind="2x25_centre", h=21, rho_w=0.40),            # v1: no skirt, brass-PLA wall (diffuse 0.4)
        dict(kind="2x25_centre", h=21),                        # white skirt
        dict(kind="4x25_ring22", h=21),
        dict(kind="6x15_ring26", h=21),
        dict(kind="4x25_ring22", h=21, Tdisc=0.83, Rdisc=0.14),
        dict(kind="2x25_down_shield", h=21, shield=(14.0, 270.0)),
        dict(kind="2x25_down_shield", h=21, shield=(18.0, 272.0)),
        dict(kind="6x15_ring26", h=21, rho_w=0.6, wall_spec=1.0),  # series: brass reflector (specular 0.6)
    ]
    for c in cases:
        r = run(n=150000, **c)
        res.append(r)
        print(json.dumps({k: v for k, v in r.items() if k != "rc"}))
    json.dump(res, open(__file__.replace("topp.py", "topp_out.json"), "w"), indent=1)
