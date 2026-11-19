import re, sys, zipfile, os

SRC = sys.argv[1]          # .../print-kbord/plater
OUT = sys.argv[2]          # output .3mf
S = 1 / 3                  # XY scale
T = 0.8                    # plate thickness in mm (original 3.0)
BED = 256.0
CELL = BED / 3

def read_objects(path):
    m = zipfile.ZipFile(path).read('3D/3dmodel.model').decode()
    objs = []
    for name, body in re.findall(r'<object id="\d+" type="model" name="([^"]*)">(.*?)</object>', m, re.S):
        V = [tuple(map(float, v)) for v in re.findall(r'<vertex x="([-\d.e]+)" y="([-\d.e]+)" z="([-\d.e]+)"', body)]
        Tr = re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', body)
        objs.append((name, V, Tr))
    return objs

files = [f'kbord-plate-{i}.3mf' for i in range(1, 9)] + ['kbord-plate-9-vogge.3mf']
# cell 0 (front-left, holds the bed exclusion zone 0..18 x 0..28) gets the round vogge
cells = [(c, r) for r in range(3) for c in range(3)]
order = [cells[i] for i in range(1, 9)] + [cells[0]]

out = []
for f, (c, r) in zip(files, order):
    objs = read_objects(os.path.join(SRC, f))
    zs = [v[2] for _, V, _ in objs for v in V]
    zmax = max(zs)
    sz = S if 'vogge' in f else T / zmax
    cx, cy = (c + 0.5) * CELL, (r + 0.5) * CELL
    for name, V, Tr in objs:
        NV = [((x - BED / 2) * S + cx, (y - BED / 2) * S + cy, z * sz) for x, y, z in V]
        out.append((name, NV, Tr))

xs = [v[0] for _, V, _ in out for v in V]; ys = [v[1] for _, V, _ in out for v in V]; zz = [v[2] for _, V, _ in out for v in V]
print(f'{len(out)} delar · x {min(xs):.1f}..{max(xs):.1f} · y {min(ys):.1f}..{max(ys):.1f} · z {min(zz):.2f}..{max(zz):.2f}')
for name, V, _ in out:
    x0 = min(v[0] for v in V); x1 = max(v[0] for v in V); y0 = min(v[1] for v in V); y1 = max(v[1] for v in V)
    if x0 < 18 and y0 < 28 and any(v[0] < 18 and v[1] < 28 for v in V):
        print('ADVARSEL: del', name, 'i ekskluderingssona')

res = []
items = []
for i, (name, V, Tr) in enumerate(out, 1):
    vs = ''.join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in V)
    ts = ''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in Tr)
    res.append(f'<object id="{i}" type="model" name="{name}"><mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh></object>')
    items.append(f'<item objectid="{i}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>')
model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
         'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
         '<metadata name="Title">kbord 1/3</metadata><resources>' + ''.join(res) + '</resources><build>' + ''.join(items) + '</build></model>')
src = zipfile.ZipFile(os.path.join(SRC, files[0]))
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', src.read('[Content_Types].xml'))
    z.writestr('_rels/.rels', src.read('_rels/.rels'))
    z.writestr('3D/3dmodel.model', model)
print('skreiv', OUT, os.path.getsize(OUT), 'byte')
