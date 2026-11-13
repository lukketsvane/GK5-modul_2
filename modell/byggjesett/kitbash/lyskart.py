# -*- coding: utf-8 -*-
"""lyskart.py · lyset på bordet sett ovanfrå, frå den uavhengige strålesporinga (etterproving.py)

To kart i same målestokk og same eksponering, begge skalerte til 350 lx i snitt på feltet:
LED-stripa 24 cm mot rein plate, og éi diode mot plata med diffusorark (12°). Berre direkte lys frå plata.
Brukaren sit nedst. Ramma er arbeidsfeltet 0,6 × 0,4 m, streken øvst er skjermen.

  python lyskart.py      skriv lyskart.png og lyskart.json
"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import etterproving as e

HER = os.path.dirname(os.path.abspath(__file__))
PXM = 560; OMR = (-0.46, 0.46, -0.06, 0.62); KVIT = 800.0        # pikslar per meter, utsnitt (m), lux som blir kvitt


def kart(halv, spreiing, N=9_000_000):
    c = np.array([0.0, 0.36, 0.62]); a = e.unit([0.0, 0.40, -0.90]); kp = c + 0.12 * a
    q, n = e.spor(c, kp, np.array([0.0, 0.25, 0.0]), halv, (1, 0, 0), spreiing=spreiing, N=N, treff=True)
    x0, x1, y0, y1 = OMR; nx = int(round((x1 - x0) * PXM)); ny = int(round((y1 - y0) * PXM))
    H, _, _ = np.histogram2d(q[:, 0], q[:, 1], bins=[nx, ny], range=[[x0, x1], [y0, y1]])
    E = H * 0.85 / n * PXM * PXM                                   # lux per lumen
    felt = (np.abs(np.linspace(x0, x1, nx, endpoint=False) + 0.5 / PXM) <= 0.30)[:, None] & \
           ((np.linspace(y0, y1, ny, endpoint=False) + 0.5 / PXM >= 0.05) & (np.linspace(y0, y1, ny, endpoint=False) + 0.5 / PXM <= 0.45))[None, :]
    lm = 350.0 / E[felt].mean()                                    # lumen frå kjelda som gjev 350 lx i snitt
    E = E * lm
    im = Image.fromarray(np.clip(E.T[::-1] / KVIT, 0, 1).astype(np.float32) * 255).convert('L').filter(ImageFilter.GaussianBlur(9))        # 1,6 cm: tek bort kornet i kanten av lyset
    v = (np.asarray(im).astype(float) / 255) ** (1 / 2.2)
    rgb = np.stack([v * 255, v * 222, v * 176], -1).astype(np.uint8)   # 3000 K mot kamera på 3900 K: varmt kvitt
    ut = Image.fromarray(rgb); dr = ImageDraw.Draw(ut)
    px = lambda x, y: ((x - x0) * PXM, (y1 - y) * PXM)
    dr.rectangle([px(-0.30, 0.45), px(0.30, 0.05)], outline=(120, 120, 120), width=1)
    dr.line([px(-0.27, 0.45), px(0.27, 0.45)], fill=(200, 200, 200), width=3)
    # jamnheit i ruter på 10 cm, same tal som i etterprøvinga
    H6, _, _ = np.histogram2d(q[:, 0], q[:, 1], bins=[6, 4], range=[[-0.30, 0.30], [0.05, 0.45]])
    return ut, dict(lm=float(lm), U_10cm=float(H6.min() / H6.mean()), felt_del=float(H6.sum() * 0.85 / n))


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    a, ta = kart(0.12, 2.5); b, tb = kart(0.001, 12.0)
    luft = 28
    im = Image.new('RGB', (a.width * 2 + luft, a.height), (0, 0, 0)); im.paste(a, (0, 0)); im.paste(b, (a.width + luft, 0))
    im.save(os.path.join(HER, 'lyskart.png'))
    json.dump(dict(stripe=ta, diode_ark=tb, utsnitt_m=OMR, px_per_m=PXM, lux_kvit=KVIT), open(os.path.join(HER, 'lyskart.json'), 'w', encoding='utf-8'), indent=1)
    print(im.size, ta, tb)
