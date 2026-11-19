import sys, numpy as np, trimesh
for n in sys.argv[2:]:
    m = trimesh.load(f'{sys.argv[1]}/skulptur-{n}.glb', force='mesh')
    V = m.vertices.copy(); V = np.c_[V[:, 0], -V[:, 2], V[:, 1]]
    V -= [(V[:, 0].min() + V[:, 0].max()) / 2, (V[:, 1].min() + V[:, 1].max()) / 2, V[:, 2].min()]
    H = V[:, 2].max(); print(f'skulptur-{n}: H {H:.3f}  x {np.ptp(V[:,0]):.3f} y {np.ptp(V[:,1]):.3f}')
    for z0 in np.linspace(0, H, 13)[:-1]:
        s = V[(V[:, 2] >= z0) & (V[:, 2] < z0 + H / 12)]
        if len(s):
            print(f'  z {z0/H:4.2f}: x {s[:,0].min():+.3f}..{s[:,0].max():+.3f}  y {s[:,1].min():+.3f}..{s[:,1].max():+.3f}')
