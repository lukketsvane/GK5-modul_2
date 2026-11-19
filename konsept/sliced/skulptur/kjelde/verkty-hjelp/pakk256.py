import zipfile, re, sys
SRC, OUT = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(SRC)
mf = [f for f in z.namelist() if f.endswith('.model')]
deler = []
for f in mf:
    m = z.read(f).decode()
    for n, b in re.findall(r'<object id="\d+"[^>]*?name="([^"]*)"[^>]*>(.*?)</object>', m, re.S):
        V = [list(map(float, v)) for v in re.findall(r'<vertex x="([-\d.e]+)" y="([-\d.e]+)" z="([-\d.e]+)"', b)]
        T = re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', b)
        if V:
            mn = [min(c) for c in zip(*V)]; mx = [max(c) for c in zip(*V)]
            deler.append((n, V, T, mn, mx))
deler.sort(key=lambda d: -(d[4][0] - d[3][0]))
B, GAP, X0 = 256, 2.0, 4.0
rader, ledig = [], list(deler)
while ledig:
    rad, x = [], X0
    for d in list(ledig):
        w = d[4][0] - d[3][0]
        if x + w <= B - 4:
            rad.append(d); ledig.remove(d); x += w + GAP
    rader.append(rad)
h = sum(max(d[4][1] - d[3][1] for d in r) for r in rader) + GAP * (len(rader) - 1)
y = (B - h) / 2
ut = []
for r in rader[::-1]:
    x = X0 if y > 30 else 22.0
    for n, V, T, mn, mx in r:
        dx, dy = x - mn[0], y - mn[1]
        ut.append((n, [(a + dx, b + dy, c - mn[2]) for a, b, c in V], T))
        x += mx[0] - mn[0] + GAP
    y += max(d[4][1] - d[3][1] for d in r) + GAP
print(f'{len(ut)} delar i {len(rader)} rader, høgd {h:.0f} mm')
res = ''.join(f'<object id="{i}" type="model" name="{n}"><mesh><vertices>' + ''.join(f'<vertex x="{a:.3f}" y="{b:.3f}" z="{c:.3f}"/>' for a, b, c in V) + '</vertices><triangles>' + ''.join(f'<triangle v1="{p}" v2="{q}" v3="{r}"/>' for p, q, r in T) + '</triangles></mesh></object>' for i, (n, V, T) in enumerate(ut, 1))
items = ''.join(f'<item objectid="{i}"/>' for i in range(1, len(ut) + 1))
model = f'<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>{res}</resources><build>{items}</build></model>'
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as o:
    o.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    o.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    o.writestr('3D/3dmodel.model', model)
