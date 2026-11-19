import zipfile, re, sys, json
import numpy as np
SRC, FIT = sys.argv[1], json.load(open(sys.argv[2]))
for f in [f'{SRC}/kbord-plate-{i}.3mf' for i in range(1, 9)]:
    m = zipfile.ZipFile(f).read('3D/3dmodel.model').decode()
    for name, body in re.findall(r'<object id="\d+" type="model" name="([^"]*)">(.*?)</object>', m, re.S):
        V = np.array(re.findall(r'<vertex x="([-\d.e]+)" y="([-\d.e]+)" z="([-\d.e]+)"', body), float)
        v = FIT[name]
        if abs(v['d']) < 100: continue
        P = V[:, :2] - [v['cx'], v['cy']]
        rr = np.linalg.norm(P, axis=1)
        mouth = P[(rr > v['r'] - 0.6) & (np.abs(np.abs(P[:, 0]) - 21.67) < 2.0)]
        print(name, v['set'], 'spormunning ved sirkelen, y =', sorted(set(np.round(mouth[:, 1], 1))))
