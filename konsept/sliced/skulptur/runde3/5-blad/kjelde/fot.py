import sys, json, numpy as np, trimesh
from shapely.geometry import MultiPoint
# fot.py [K=340] : skil fot og blad i skulptur-10 (nettet er i bitar). Skriv fot.stl (konvekst skal) og blad.json (plan, omriss, krumming).
K = float(sys.argv[1]) if len(sys.argv) > 1 else 340
m = trimesh.load("/home/claude/slicer/public/form/skulptur-10.glb", force="mesh")
m.apply_transform(np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]))
b = m.bounds; k = K / m.extents.max(); c0 = np.array([(b[0][0] + b[1][0]) / 2, (b[0][1] + b[1][1]) / 2, b[0][2]])
V = (m.vertices - c0) * k; r = np.hypot(V[:, 0], V[:, 1]); s = K / 340
F = V[(r < 44 * s) & (V[:, 2] < 110 * s)]; top = 118 * s
F = np.vstack([F, [[0, 0, top]], [[8 * s * np.cos(a), 8 * s * np.sin(a), top - s] for a in np.linspace(0, 6.28, 24)], [[18 * s * np.cos(a), 18 * s * np.sin(a), top - 3.5 * s] for a in np.linspace(0, 6.28, 32)]])
trimesh.convex.convex_hull(F).export("fot.stl")
L = V[((r >= 44 * s) & (V[:, 2] > 84 * s)) | (V[:, 2] >= 118 * s)]
cen = np.array([np.mean([L[:, 0].min(), L[:, 0].max()]), np.mean([L[:, 1].min(), L[:, 1].max()]), 0])
A = np.c_[L[:, 0], L[:, 1], np.ones(len(L))]; (px, py, pz), *_ = np.linalg.lstsq(A, L[:, 2], rcond=None)
n = np.array([px, py, -1.0]); n /= np.linalg.norm(n); cen[2] = px * cen[0] + py * cen[1] + pz
v = np.array([0, -1, 0.0]); v = v - n * (v @ n); v /= np.linalg.norm(v); u = np.cross(v, n)
du, dv, dn = (L - cen) @ u, (L - cen) @ v, (L - cen) @ n
q, *_ = np.linalg.lstsq(np.c_[du ** 2, dv ** 2, du, dv, np.ones(len(du))], dn, rcond=None)
hull = MultiPoint(np.c_[du, dv]).convex_hull.buffer(-4).buffer(4).simplify(0.5)
json.dump({"senter": cen.round(2).tolist(), "u": u.round(5).tolist(), "v": v.round(5).tolist(), "n": n.round(5).tolist(), "omriss": np.round(np.array(hull.exterior.coords)[:-1], 2).tolist(), "Rtvers": float(1 / (2 * q[0])), "topp": float(top)}, open("blad.json", "w"))
