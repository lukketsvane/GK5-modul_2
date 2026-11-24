# -*- coding: utf-8 -*-
"""overlegg.py · legg opprisset av CAD-en (ortografisk, sett frå -Y) oppå skissa og reknar samsvaret.

  py -3 kontroll/overlegg.py      les referanse/skisse.png (berre lokalt) og produksjon/*.stl, skriv kontroll/overlegg.png
Avbildinga er den same som i referanse/maaling.json: x_px = 257,7 + 2 X, y_px = 899,5 - 2 Z (midt i djupna).
"""
import json, struct
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROT = Path(__file__).resolve().parent.parent
SYNLEG = ['D01_blad', 'D02_hovud', 'D03_fot', 'D05_knott', 'D07_spreiar']

def les_stl(sti):
    b = sti.read_bytes(); n = struct.unpack('<I', b[80:84])[0]
    a = np.frombuffer(b[84:84 + n * 50], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))
    return a['v']

ski = Image.open(ROT / 'referanse' / 'skisse.png').convert('L')
W, H = ski.size
maske_cad = Image.new('L', (W, H), 0)
d = ImageDraw.Draw(maske_cad)
for namn in SYNLEG:
    for tri in les_stl(ROT / 'produksjon' / f'{namn}.stl'):
        pts = [(257.7 + 2 * p[0], 899.5 - 2 * p[2]) for p in tri]
        d.polygon(pts, fill=255)
cad = np.asarray(maske_cad) > 127
skisse = np.asarray(ski).astype(float) > 45
iou = (cad & skisse).sum() / (cad | skisse).sum()
# berre over foten (perspektivet flyttar framkanten av foten ned i skissa)
ov = np.zeros_like(cad); ov[:830, :] = True
iou_ov = ((cad & skisse) & ov).sum() / ((cad | skisse) & ov).sum()
kant = np.asarray(maske_cad.filter(ImageFilter.FIND_EDGES)) > 0
bilete = np.stack([np.asarray(ski)] * 3, -1).astype(np.uint8).copy()
bilete[kant] = [255, 40, 30]
Image.fromarray(bilete).crop((200, 300, 800, 940)).resize((900, 960), Image.LANCZOS).save(ROT / 'kontroll' / 'overlegg.png')
json.dump(dict(samsvar_heile=round(float(iou), 4), samsvar_over_foten=round(float(iou_ov), 4),
               merknad='Ortografisk CAD mot skisse med svakt perspektiv: framkanten av foten ligg lågare i skissa.'),
          open(ROT / 'kontroll' / 'overlegg.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('IoU heile', round(float(iou), 4), 'over foten', round(float(iou_ov), 4))
