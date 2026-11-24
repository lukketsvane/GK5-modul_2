# -*- coding: utf-8 -*-
"""segl_mot_skisse.py · teiknar kantane i CAD-en over skissa gjennom kameraet som er passa til skissa.
Kameraet: f = 3400 px, passa på framseglet og klampa (sjå LES_MEG). Gjev kontroll/segl_mot_skisse.png og avvik i px."""
import os, sys, json, math
import numpy as np
import cadquery as cq
from PIL import Image, ImageDraw
HER = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HER)
import segl_cad as C
ROT = os.path.dirname(HER)
KAM = dict(f=3400.0, Cx=-379.4, Cy=-1093.13, Cz=212.16, theta=25.48, phi=3.48)   # frå passinga (kamera2.json)
W, H = 1536, 1024
def proj(P):
    th, ph = math.radians(KAM['theta']), math.radians(KAM['phi'])
    fwd = np.array([math.sin(th) * math.cos(ph), math.cos(th) * math.cos(ph), -math.sin(ph)])
    right = np.array([math.cos(th), -math.sin(th), 0.0]); up = np.cross(right, fwd)
    d = np.atleast_2d(P) - np.array([KAM['Cx'], KAM['Cy'], KAM['Cz']])
    z = d @ fwd
    return np.stack([W / 2 + KAM['f'] * (d @ right) / z, H / 2 - KAM['f'] * (d @ up) / z], 1)
if __name__ == '__main__':
    delar, _ = C.bygg()
    im = Image.open(os.path.join(ROT, 'referanse', 'skisse.png')).convert('RGB')
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
    farge = {'D01': (0, 255, 255, 230), 'D02': (255, 255, 0, 230), 'E02': (0, 255, 0, 230), 'E03': (255, 0, 255, 230)}
    for k, col in farge.items():
        for e in delar[k].Edges():
            n = max(2, int(e.Length() / 2))
            pts = np.array([[*e.positionAt(i / n)] for i in range(n + 1)])
            uv = proj(pts)
            dr.line([tuple(p) for p in uv], fill=col, width=1)
    out = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB')
    out.save(os.path.join(ROT, 'kontroll', 'segl_mot_skisse.png'))
    # avvik på nøkkelpunkt (px): toppane og den låge spissen
    import segl_geometri as G
    obs = {'topp D01': (1032, 325), 'topp D02': (681, 51), 'loddkant D01 nede': (1023.6, 873.3), 'låg spiss': (393.3, 924.1)}
    bb1 = delar['D01'].BoundingBox(); bb2 = delar['D02'].BoundingBox()
    top1 = max(delar['D01'].Vertices(), key=lambda v: v.Z); top2 = max(delar['D02'].Vertices(), key=lambda v: v.Z)
    cad = {'topp D01': (top1.X, top1.Y, top1.Z), 'topp D02': (top2.X, top2.Y, top2.Z),
           'loddkant D01 nede': (G.D01.B2[0], G.D01.B2[1], 0.0), 'låg spiss': (0.0, 0.0, 0.0)}
    av = {k: round(float(np.linalg.norm(proj(np.array(cad[k]))[0] - np.array(obs[k]))), 1) for k in obs}
    print(json.dumps(av, ensure_ascii=False))
    json.dump(dict(kamera=KAM, avvik_px=av, skala_mm_per_px_ved_spissen=round(1 / 2.95, 3)),
              open(os.path.join(ROT, 'kontroll', 'segl_mot_skisse.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
