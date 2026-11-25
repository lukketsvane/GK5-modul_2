# -*- coding: utf-8 -*-
"""
overlegg.py  ·  samanlikn CAD-en for Kran med referansefotoet gjennom kameraet som er tilpassa i referanse/kamera.py

  py -3 kontroll/overlegg.py

Fotoet ligg berre lokalt (referanse/bilete.png, ikkje i git). Skriptet lagar ei maske av lampa i fotoet (oliven flate og
lysande spreiar), projiserer CAD-nettet med same kamera og reknar ut kor godt dei dekkjer kvarandre (IoU). Talet
blir skrive til kontroll/overlegg.json; overleggsbiletet kontroll/overlegg.png blir berre liggjande lokalt.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HER = Path(__file__).resolve().parent
ROT = HER.parent
sys.path.insert(0, str(ROT / 'cad'))
import kran as K                                                    # noqa: E402

M = json.loads((ROT / 'referanse' / 'maaling.json').read_text(encoding='utf-8'))
CX = 1128.0
RAMME = (270, 1330, 330, 2060)                                     # y0, y1, x0, x1: området rundt lampa


def proj(p):
    """Lampekoordinatar (mm) til pikslar i fotoet. Kameraet ser stativplanet dreidd phi om loddaksen.
    Kamerafit-koordinatane har origo i nedre venstre hjørne av stativet, same som CAD-en."""
    X, Y, Z = p
    f, phi, cy, uA, ZA, H = M['f'], M['phi'], M['cy'], M['uA'], M['ZA'], M['H']
    lat = uA + X * math.cos(phi) + Y * math.sin(phi)
    djup = ZA - X * math.sin(phi) + Y * math.cos(phi)
    return CX + f * lat / djup, cy - f * (Z - H) / djup


def maske_foto():
    im = np.asarray(Image.open(ROT / 'referanse' / 'bilete.png').convert('RGB')).astype(float)
    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    oliven = ((G - B) > 18) & (G > 100) & (R < G + 25) & (R > 0.75 * G)
    lys = (R > 200) & (G > 170) & (B > 110)
    y0, y1, x0, x1 = RAMME
    m = np.zeros(R.shape, bool)
    m[y0:y1, x0:x1] = oliven[y0:y1, x0:x1]
    band = np.zeros_like(m)
    band[290:430, 900:2060] = True
    m |= lys & band
    m = ndimage.binary_opening(ndimage.binary_closing(m, iterations=2), iterations=1)
    lab, n = ndimage.label(m)
    st = ndimage.sum(m, lab, range(1, n + 1))
    return np.isin(lab, 1 + np.where(st > 3000)[0])


def maske_cad(former, storleik):
    """Projiser trekantnettet til formene og fyll trekantane."""
    im = Image.new('L', storleik, 0)
    dr = ImageDraw.Draw(im)
    for f in former:
        v, t = f.tessellate(0.2, 0.3)
        P = [proj((p.x, p.y, p.z)) for p in v]
        for a, b, c in t:
            dr.polygon([P[a], P[b], P[c]], fill=255)
    return np.asarray(im) > 0


def main():
    delar = K.bygg()
    synlege = [d['form'] for pid, d in delar.items() if d.get('synleg_i_foto', True)]
    foto = maske_foto()
    cad = maske_cad(synlege, (foto.shape[1], foto.shape[0]))
    y0, y1, x0, x1 = RAMME
    a, b = foto[y0:y1, x0:x1], cad[y0:y1, x0:x1]
    iou = float((a & b).sum() / max(1, (a | b).sum()))
    ut = dict(iou=round(iou, 4), foto_pikslar=int(a.sum()), cad_pikslar=int(b.sum()),
              berre_foto=int((a & ~b).sum()), berre_cad=int((b & ~a).sum()),
              metode='IoU mellom maska av lampa i fotoet og CAD-nettet projisert med kameraet frå referanse/kamera.py')
    (HER / 'overlegg.json').write_text(json.dumps(ut, ensure_ascii=False, indent=1), encoding='utf-8')
    foto_im = Image.open(ROT / 'referanse' / 'bilete.png').convert('RGB')
    rgb = np.asarray(foto_im).copy()
    rgb[cad & ~foto] = (0.5 * rgb[cad & ~foto] + 0.5 * np.array([255, 40, 40])).astype(np.uint8)
    rgb[foto & ~cad] = (0.5 * rgb[foto & ~cad] + 0.5 * np.array([40, 120, 255])).astype(np.uint8)
    Image.fromarray(rgb).crop((x0 - 60, y0 - 40, x1 + 40, y1 + 20)).save(HER / 'overlegg.png')
    print(json.dumps(ut, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
