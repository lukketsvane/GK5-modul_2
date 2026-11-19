# skulptur-06 -> NEBB: sideprofilen til stilken (snitt x = 0) + tå, hovud med nebb, steg og fotbjelke. Bladet er eige ark.
import numpy as np, trimesh, json
from shapely.geometry import Polygon, LineString, Point, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
H = '/home/claude/arb2/'
stor = lambda g: g if g.geom_type == 'Polygon' else max(g.geoms, key=lambda q: q.area)
m = trimesh.load(H + 'stilk/heil.stl', force='mesh')
sec = m.section(plane_origin=[0, 0, 0], plane_normal=[1, 0, 0])
stem = stor(unary_union([Polygon(d[:, 1:3]).buffer(0) for d in sec.discrete if len(d) > 3]))
stem = stor(stor(stem.intersection(box(-200, -5, -14, 400))).buffer(-5).buffer(10).buffer(-5))
c, s = np.cos(np.radians(20)), np.sin(np.radians(20)); T0 = (-14.0, 318.0)
P = lambda v, h=0.0: (T0[0] + c * v + s * h, T0[1] - s * v + c * h)
hovud = LineString([P(-20), P(30)]).buffer(15)
taa = box(-118, 0, 88, 16).union(Point(88, 8).buffer(8))
prof = stor(unary_union([stem, taa, hovud]).buffer(10).buffer(-10).buffer(-3).buffer(3))
prof = stor(prof.intersection(box(-300, 0, 300, 500)))
prof = stor(prof.difference(LineString([P(0), P(90)]).buffer(1.7, cap_style=2)))
zt = LineString([(-93, -10), (-93, 500)]).intersection(prof).bounds[3]
steg = Polygon([(-46, 0), (46, 0), (22, zt), (-22, zt)]).buffer(-4).buffer(4)
bjelke = box(-48, 0, 48, 16).buffer(-6).buffer(6)
import shapely
p = 0.7; xs = np.arange(-50, 50.01, p); ys = np.arange(-125, 100.01, p); zs = np.arange(-1.05, 343, p)
inn = lambda poly, A, B: shapely.contains_xy(poly, *np.meshgrid(A, B, indexing='ij'))
g = (np.abs(xs) <= 22)[:, None, None] & inn(prof, ys, zs)[None]
g |= ((ys >= -98) & (ys <= -88))[None, :, None] & inn(steg, xs, zs)[:, None, :]
g |= ((ys >= 73) & (ys <= 83))[None, :, None] & inn(bjelke, xs, zs)[:, None, :]
np.savez(H + 'nebb/ra.npz', g=g, o=np.array([xs[0], ys[0], zs[0]]), p=p)
RB, VC = 113.5, 75.0
blad = Point(0, 0).buffer(RB, 48)
for x in (-10, 10): blad = blad.difference(box(x - 2.15, -130, x + 2.15, -VC))
blad = orient(stor(blad), 1.0)
C = P(VC); G = P(VC, -49.5)
json.dump({"senter": [0, C[0], C[1]], "u": [-1, 0, 0], "v": [0, c, -s], "n": [0, -s, -c], "nopp": [0, s, c], "T0": list(T0), "R": 200,
           "omriss": [[round(x, 2), round(y, 2)] for x, y in list(blad.exterior.coords)[:-1]],
           "hol": [[round(14.3 * np.cos(-t), 2), round(14.3 * np.sin(-t), 2)] for t in np.linspace(0, 2 * np.pi, 40, endpoint=False)]}, open(H + 'nebb/blad.json', 'w'))
# masse og tyngdepunkt (bjørk 0,68, akryl 1,19 g/cm3)
deler = [(2 * prof.area * 0.4 * 0.68 / 100, prof.centroid.x), (steg.area * 0.4 * 0.68 / 100, -93), (bjelke.area * 0.4 * 0.68 / 100, 78), (blad.area * 0.3 * 1.19 / 100, C[0]), (60, G[0])]
M = sum(q[0] for q in deler); print('profil', np.round(prof.bounds, 1), 'steg-topp', round(zt, 1), 'blad cm2', round(blad.area / 100), 'senter', np.round(C, 1), 'kule', np.round(G, 1))
print('masse g', [round(q[0]) for q in deler], 'sum', round(M), 'tyngdepunkt y', round(sum(q[0] * q[1] for q in deler) / M, 1), 'fot y -118..96')
json.dump({"npz": H + "nebb/ra.npz", "glatt": 0.8, "tris": 30000, "ut": H + "nebb/lampe.stl", "steg": []}, open(H + 'nebb/kropp.json', 'w'))
