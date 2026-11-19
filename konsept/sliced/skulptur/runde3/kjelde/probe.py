import sys, numpy as np, trimesh
# probe.py fil.stl "x,y,z" "dx,dy,dz" [fleire par] : kvar strålen går inn og ut av kroppen
m = trimesh.load(sys.argv[1], force='mesh')
for i in range(2, len(sys.argv), 2):
    o = np.array([float(t) for t in sys.argv[i].split(',')]); d = np.array([float(t) for t in sys.argv[i+1].split(',')]); d = d / np.linalg.norm(d)
    loc, _, _ = m.ray.intersects_location([o - d * 1000], [d])
    t = sorted(round(float((q - o) @ d), 1) for q in loc)
    print(sys.argv[i], '->', sys.argv[i+1], ':', ' '.join(f'[{t[j]},{t[j+1]}]' for j in range(0, len(t) - 1, 2)))
