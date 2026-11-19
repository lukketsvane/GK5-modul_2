import sys, numpy as np, trimesh
from PIL import Image, ImageDraw
# snitt.py fil.stl ut.png "akse=verdi" ... : snitt med 20 mm rutenett; akse x|y|z
m = trimesh.load(sys.argv[1], force='mesh'); b = m.bounds; S = 420; pad = 20
spec = sys.argv[3:]; im = Image.new('RGB', (S * len(spec), S), 'white'); d = ImageDraw.Draw(im)
R = max(m.extents) / 2 + 15; c = (b[0] + b[1]) / 2; k = (S / 2 - pad) / R
for j, s in enumerate(spec):
    ak, val = s.split('='); val = float(val); i = 'xyz'.index(ak); n = [0, 0, 0]; n[i] = 1; o = c.copy(); o[i] = val
    ax = [a for a in range(3) if a != i]
    def px(u, v): return (j * S + S / 2 + (u - c[ax[0]]) * k, S / 2 - (v - c[ax[1]]) * k)
    for t in np.arange(-400, 401, 20):
        d.line([px(t, -400), px(t, 400)], fill=(225, 225, 225) if t % 100 else (170, 170, 170)); d.line([px(-400, t), px(400, t)], fill=(225, 225, 225) if t % 100 else (170, 170, 170))
    d.line([px(0, -400), px(0, 400)], fill=(255, 120, 120)); d.line([px(-400, 0), px(400, 0)], fill=(255, 120, 120))
    sec = m.section(plane_origin=o, plane_normal=n)
    if sec is not None:
        for e in sec.entities:
            p = sec.vertices[e.points][:, ax]; d.line([px(u, v) for u, v in p], fill=(0, 0, 0), width=2)
    d.text((j * S + 6, 4), f"{s}  ({'xyz'[ax[0]]} bortover, {'xyz'[ax[1]]} opp)", fill=(200, 0, 0)); d.rectangle([j * S, 0, j * S + S - 1, S - 1], outline=(120, 120, 120))
im.save(sys.argv[2])
