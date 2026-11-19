import zipfile, re, sys, json
import numpy as np
SRC, FIT = sys.argv[1], json.load(open(sys.argv[2]))
for f in [f'{SRC}/kbord-plate-{i}.3mf' for i in range(1, 9)]:
    m = zipfile.ZipFile(f).read('3D/3dmodel.model').decode()
    for name, body in re.findall(r'<object id="\d+" type="model" name="([^"]*)">(.*?)</object>', m, re.S):
        V = np.array(re.findall(r'<vertex x="([-\d.e]+)" y="([-\d.e]+)" z="([-\d.e]+)"', body), float)
        v = FIT[name]
        P = V[:, :2] - [v['cx'], v['cy']]
        rr = np.linalg.norm(P, axis=1)
        inner = P[(rr < v['r'] - 1.0)]
        # slot side walls sit at |u| = 21.67 +- ~1.6 (full-scale)
        w = inner[np.abs(np.abs(inner[:, 0]) - 21.67) < 2.2]
        if len(w):
            print(f"{name:>3} sett {v['set']}  spor ved u=+-21.67: y {w[:,1].min():7.1f} .. {w[:,1].max():7.1f}   (sirkel y -{v['dn']} .. +{v['up']})")
