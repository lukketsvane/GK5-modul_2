import sys, json, numpy as np, trimesh
from scipy import ndimage as ndi
from skimage import measure
# kropp.py spec.json : skulpturform -> glatt, tett kropp med holrom. Alle mål i mm, x og y sentrert, z = 0 i botn (før kapping).
a = json.load(open(sys.argv[1]))
RAA = "stl" in a
m = trimesh.load(a["stl"] if RAA else a["glb"], force="mesh")
if not RAA: m.apply_transform(np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1.0]]))
if a.get("dreiZ"):
    m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(a["dreiZ"]), [0, 0, 1]))
b = m.bounds
k = 1 if RAA else a["storst"] / m.extents.max() if "storst" in a else a["hogd"] / m.extents[2]
if not RAA: m.apply_translation(-np.array([(b[0][0] + b[1][0]) / 2, (b[0][1] + b[1][1]) / 2, b[0][2]])); m.apply_scale(k)
p = a.get("pitch", 1.2)
v = m.voxelized(p).fill(method="orthographic")
P = 10
g = np.pad(v.matrix, P); o = v.transform[:3, 3] - P * p
g = ndi.binary_closing(g, iterations=1)
X = (o[0] + p * np.arange(g.shape[0]))[:, None, None]; Y = (o[1] + p * np.arange(g.shape[1]))[None, :, None]; Z = (o[2] + p * np.arange(g.shape[2]))[None, None, :]

def prim(q):
    s = q["slag"]
    if s == "kule":
        c = q["senter"]; return (X - c[0]) ** 2 + (Y - c[1]) ** 2 + (Z - c[2]) ** 2 <= q["r"] ** 2
    if s == "sylinder":
        c = np.array(q["senter"], float); d = np.array(q.get("retning", [0, 0, 1]), float); d /= np.linalg.norm(d)
        t = (X - c[0]) * d[0] + (Y - c[1]) * d[1] + (Z - c[2]) * d[2]
        r2 = (X - c[0] - t * d[0]) ** 2 + (Y - c[1] - t * d[1]) ** 2 + (Z - c[2] - t * d[2]) ** 2
        return (r2 <= q["r"] ** 2) & (np.abs(t) <= q["lengd"] / 2)
    if s == "boks":
        c, h = q["senter"], np.array(q["storleik"]) / 2
        return (np.abs(X - c[0]) <= h[0]) & (np.abs(Y - c[1]) <= h[1]) & (np.abs(Z - c[2]) <= h[2])
    if s == "halvrom":   # alt der (punkt - senter) . retning > 0
        c = q["senter"]; d = q["retning"]; return (X - c[0]) * d[0] + (Y - c[1]) * d[1] + (Z - c[2]) * d[2] > 0
    raise SystemExit("ukjend form " + s)

for q in a.get("steg", []):
    op = q["op"]
    if op == "lukkZ":
        n = int(round(q["mm"] / p)); g = np.pad(g, ((0, 0), (0, 0), (n, n))); g = ndi.binary_closing(g, structure=np.ones((1, 1, n), bool))[:, :, n:-n]
    elif op == "minus": g = g & ~prim(q)
    elif op == "pluss": g = g | prim(q)
    elif op == "snitt": g = g & prim(q)
    elif op == "skal":  # hol ut: alt djupare enn t frå overflata vert luft, eventuelt berre innanfor ei form
        d = ndi.distance_transform_edt(g) * p; hol = d > q["t"]
        if "innanfor" in q: hol &= prim(q["innanfor"])
        g = g & ~hol
    elif op == "storste":
        l, n = ndi.label(g); g = l == (1 + np.argmax(ndi.sum(g, l, range(1, n + 1))))
    else: raise SystemExit("ukjend op " + op)
f = ndi.gaussian_filter(g.astype(np.float32), a.get("glatt", 1.3))
vs, fs, _, _ = measure.marching_cubes(f, 0.5)
ut = trimesh.Trimesh(vs * p + o, fs[:, ::-1], process=True)
ut = max(ut.split(only_watertight=False), key=lambda c: len(c.faces))
n = a.get("tris", 30000)
if len(ut.faces) > n: ut = ut.simplify_quadric_decimation(face_count=n)
ut = max(ut.split(only_watertight=False), key=lambda c: len(c.faces)); trimesh.repair.fix_normals(ut)
ut.export(a["ut"])
print("KROPP", a["ut"].split("/")[-2], "mm", np.round(ut.extents, 1).tolist(), "bb", np.round(ut.bounds, 0).tolist(), "tri", len(ut.faces), "tett", ut.is_watertight, "vol cm3", round(ut.volume / 1000), "k", round(k, 2))
