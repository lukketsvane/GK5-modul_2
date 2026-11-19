import bpy, sys, json, math, zipfile, re, os
import numpy as np
from mathutils import Vector, Quaternion

argv = sys.argv[sys.argv.index('--') + 1:]
SRC, OUT = argv[0], argv[1]
os.makedirs(OUT, exist_ok=True)
R = 120.0
OFF = [-108.33, -65.0, -21.67, 21.67, 65.0, 108.33]
c45 = math.sqrt(0.5)
NA = np.array([c45, 0, c45]); NB = np.array([c45, 0, -c45]); YV = np.array([0, 1.0, 0])


def read(path):
    m = zipfile.ZipFile(path).read('3D/3dmodel.model').decode()
    out = []
    for name, body in re.findall(r'<object id="\d+" type="model" name="([^"]*)">(.*?)</object>', m, re.S):
        V = np.array(re.findall(r'<vertex x="([-\d.e]+)" y="([-\d.e]+)" z="([-\d.e]+)"', body), float)
        T = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', body), int)
        out.append((name, V, T))
    return out


def hull(P):
    P = np.unique(np.round(P, 4), axis=0)
    P = P[np.lexsort((P[:, 1], P[:, 0]))]
    def half(pts):
        h = []
        for p in pts:
            while len(h) >= 2:
                a, b = h[-1] - h[-2], p - h[-2]
                if a[0] * b[1] - a[1] * b[0] <= 0: h.pop()
                else: break
            h.append(p)
        return h
    lo, up = half(P), half(P[::-1])
    return np.array(lo[:-1] + up[:-1])


def fit(P, r):
    H = hull(P)
    c = np.array([(H[:, 0].min() + H[:, 0].max()) / 2, (H[:, 1].min() + H[:, 1].max()) / 2])
    pts = H
    for _ in range(3):
        for _ in range(80):
            d = pts - c; L = np.linalg.norm(d, axis=1)
            J = -d / L[:, None]; f = L - r
            delta = np.linalg.lstsq(J, -f, rcond=None)[0]
            c = c + delta
            if np.linalg.norm(delta) < 1e-7: break
        res = np.abs(np.linalg.norm(H - c, axis=1) - r)
        pts = H[res < 0.6]
    return c, float(np.median(np.abs(np.linalg.norm(pts - c, axis=1) - r))), len(pts), len(H)


parts = {}
for i in range(1, 9):
    for name, V, T in read(f'{SRC}/kbord-plate-{i}.3mf'):
        parts[int(name)] = (V, T)
vname, VV, VT = read(f'{SRC}/kbord-plate-9-vogge.3mf')[0]

info, lamp = {}, {}
for n, (V, T) in sorted(parts.items()):
    A = n <= 6
    d = OFF[n - 1] if A else OFF[n - 21]
    r = math.sqrt(R * R - d * d)
    c, med, k, nh = fit(V[:, :2], r)
    up, dn = V[:, 1].max() - c[1], c[1] - V[:, 1].min()
    s = 1 if up > dn + 1 else (-1 if dn > up + 1 else 0)
    info[n] = dict(set='A' if A else 'B', d=d, r=round(r, 2), cx=round(c[0], 3), cy=round(c[1], 3), med=round(med, 4), hullpts=f'{k}/{nh}', up=round(up, 1), dn=round(dn, 1), s=s)
for setn in 'AB':
    ss = [v['s'] for v in info.values() if v['set'] == setn and v['s'] != 0]
    sgn = 1 if sum(ss) >= 0 else -1
    for v in info.values():
        if v['set'] == setn and v['s'] == 0: v['s'] = sgn; v['s_from_set'] = True
for n, (V, T) in parts.items():
    v = info[n]; N, U = (NA, NB) if v['set'] == 'A' else (NB, -NA)  # keep both bases right-handed
    t = V[:, 2].max()
    L = v['d'] * N + np.outer(V[:, 0] - v['cx'], U) + np.outer(v['s'] * (V[:, 1] - v['cy']), YV) + np.outer(V[:, 2] - t / 2, N)
    lamp[n] = L
json.dump(info, open(f'{OUT}/fit.json', 'w'), indent=1)
print(json.dumps(info))

allY = np.concatenate([L[:, 1] for L in lamp.values()])
YMIN, YMAX = float(allY.min()), float(allY.max())
VOG = np.c_[VV[:, 0] - 128, VV[:, 1] - 128, VV[:, 2]]  # world, lying pose

stand = lambda P: np.c_[P[:, 0], -P[:, 2], P[:, 1]]
lie = lambda P: np.c_[P[:, 0], P[:, 1], P[:, 2] + R]

GREY = (0.95, 0.95, 0.94); ACOL = (1.0, 0.80, 0.50); BCOL = (0.36, 0.66, 0.72); WOOD = (1.0, 0.91, 0.74); VCOL = (0.80, 0.66, 0.46)
GAP = 45.0

panels = [
    dict(key='s0', mode='flat', res=(2000, 860)),
    dict(key='s1', mode='stand', done=[], new=[3, 4], move=[23, 24]),
    dict(key='s2', mode='stand', done=[3, 4, 23, 24], new=[], move=[2, 5]),
    dict(key='s3', mode='stand', done=[2, 3, 4, 5, 23, 24], new=[], move=[22, 25]),
    dict(key='s4', mode='stand', done=[2, 3, 4, 5, 22, 23, 24, 25], new=[], move=[1, 6]),
    dict(key='s5', mode='stand', done=[1, 2, 3, 4, 5, 6, 22, 23, 24, 25], new=[], move=[21, 26]),
    dict(key='s6', mode='lie', cam=(-0.62, -1.0, 0.55)),
    dict(key='s7', mode='lie', cam=(0.0, -1.0, 0.0), novogge=True),
]
STANDCAM = (math.sin(math.radians(4)) * math.cos(math.radians(20)), -math.cos(math.radians(4)) * math.cos(math.radians(20)), math.sin(math.radians(20)))

sc = bpy.context.scene
for ob in list(bpy.data.objects): bpy.data.objects.remove(ob)
sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading
sh.light = os.environ.get('BK_MODE', 'STUDIO'); sh.color_type = 'OBJECT'
if os.environ.get('BK_LIGHT'):
    if sh.light == 'MATCAP': sh.studio_light = os.environ['BK_LIGHT']
    else: sh.studio_light = os.environ['BK_LIGHT']
print('lys', sh.light, sh.studio_light)
for attr, val in [('show_cavity', True), ('cavity_type', 'BOTH'), ('show_shadows', True), ('show_object_outline', True), ('object_outline_color', (0.12, 0.12, 0.12))]:
    try: setattr(sh, attr, val)
    except Exception as e: print('skip', attr, e)
try: sc.display.render_aa = '16'
except Exception as e: print('aa', e)
sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = 1000
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'Standard'
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
cd = bpy.data.cameras.new('cam'); cd.type = 'ORTHO'; cd.clip_end = 20000
cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam


def build(p):
    objs, ann = [], []
    if p['mode'] == 'stand':
        for n in p['done']: objs.append((n, stand(lamp[n]), parts[n][1], GREY))
        for n in p['new']:
            W = stand(lamp[n]); objs.append((n, W, parts[n][1], ACOL if n <= 6 else BCOL))
            top = W[:, 2].max(); ann.append(dict(n=n, label=[float(W[:, 0].mean()), float(W[:, 1].mean()), float(top - 30)]))
        for n in p['move']:
            L = lamp[n].copy(); A = n <= 6
            off = (YMIN - GAP) - L[:, 1].max() if A else (YMAX + GAP) - L[:, 1].min()
            L[:, 1] += off; W = stand(L)
            objs.append((n, W, parts[n][1], ACOL if A else BCOL))
            c = W.mean(0)
            end = [float(c[0]), float(c[1]), float(YMIN - 10 if A else YMAX + 10)]
            ann.append(dict(n=n, label=[float(c[0]), float(c[1]), float(c[2])], arrow=[[float(c[0]), float(c[1]), float(c[2])], end]))
    elif p['mode'] == 'flat':
        for row, (ns, yc) in enumerate([([1, 2, 3, 4, 5, 6], 150.0), ([21, 22, 23, 24, 25, 26], -150.0)]):
            x = 0.0
            for n in ns:
                V, T = parts[n]; v = info[n]
                w = V[:, 0].max() - V[:, 0].min()
                cxp = x + w / 2
                W = np.c_[V[:, 0] - v['cx'] + cxp, V[:, 1] - v['cy'] + yc, V[:, 2]]
                objs.append((n, W, T, ACOL if n <= 6 else BCOL))
                ann.append(dict(n=n, label=[float(cxp), float(W[:, 1].min() - 22), 0.0]))
                x += w + 28
        W = VOG.copy(); W[:, 0] += x + 90; objs.append(('vogge', W, VT, VCOL))
        ann.append(dict(n='vogge', label=[float(x + 90), -105.0, 0.0]))
    else:
        for n in parts: objs.append((n, lie(lamp[n]), parts[n][1], WOOD))
        if not p.get('novogge'): objs.append(('vogge', VOG, VT, VCOL))
    return objs, ann


def frame(D, pts):
    D = Vector(D).normalized()
    q = Quaternion() if D.z > 0.999 else (-D).to_track_quat('-Z', 'Y')
    M = q.to_matrix(); right = np.array(M @ Vector((1, 0, 0))); up = np.array(M @ Vector((0, 1, 0)))
    xs, ys = pts @ right, pts @ up
    return q, right, up, (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2, xs.max() - xs.min(), ys.max() - ys.min()


built = [build(p) for p in panels]
stand_scale = max(max(f[5], f[6]) for p, (objs, _) in zip(panels, built) if p['mode'] == 'stand'
                  for f in [frame(STANDCAM, np.concatenate([o[1] for o in objs]))]) * 1.06
meta = {}
ONLY = os.environ.get('BK_ONLY')
for p, (objs, ann) in zip(panels, built):
    if ONLY and p['key'] not in ONLY.split(','): continue
    for ob in [o for o in bpy.data.objects if o.type == 'MESH']: bpy.data.objects.remove(ob)
    for n, W, T, col in objs:
        me = bpy.data.meshes.new(str(n)); me.from_pydata(W.tolist(), [], T.tolist()); me.update()
        ob = bpy.data.objects.new(str(n), me); sc.collection.objects.link(ob); ob.color = (*col, 1.0)
    D = STANDCAM if p['mode'] == 'stand' else ((0, 0, 1) if p['mode'] == 'flat' else p['cam'])
    rx, ry = p.get('res', (1000, 1000))
    sc.render.resolution_x, sc.render.resolution_y = rx, ry
    q, right, up, cx, cy, w, h = frame(D, np.concatenate([o[1] for o in objs]))
    if p['mode'] == 'flat': cy -= 12; h += 60
    M = max(rx, ry)
    s = stand_scale if p['mode'] == 'stand' else max(w / rx, h / ry) * M * 1.08
    cam.rotation_euler = q.to_euler()
    cam.location = Vector(right * cx + up * cy) + Vector(D).normalized() * 5000
    cd.ortho_scale = s
    sc.render.filepath = f'{OUT}/{p["key"]}.png'
    bpy.ops.render.render(write_still=True)
    pix = s / M
    proj = lambda P, cx=cx, cy=cy, right=right, up=up, pix=pix, rx=rx, ry=ry: [rx / 2 + (np.dot(P, right) - cx) / pix, ry / 2 - (np.dot(P, up) - cy) / pix]
    meta[p['key']] = dict(res=[rx, ry], ann=[dict(n=a['n'], label=[float(v) for v in proj(np.array(a['label']))], arrow=[[float(v) for v in proj(np.array(x))] for x in a['arrow']] if 'arrow' in a else None) for a in ann])
json.dump(meta, open(f'{OUT}/ann.json', 'w'), indent=1)
print('ferdig', YMIN, YMAX)
