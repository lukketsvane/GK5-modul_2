# -*- coding: utf-8 -*-
"""rute_tre.py  ·  dei to lampene frå bileta 13.11 og ruta over skjermkanten: tal (n=5) og bilete

  python rute_tre.py tal       til rute-tal.json
  python rute_tre.py bilete    til rute-tre.png
"""
import sys, json, os
from rute import *
from rute_sok import FORD, pult, over
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass

def ruta(ford=None, lengd=0.45, v1=190, q=0.2):
    """Ruta over skjermkanten: bjelken 50 cm over bordet, 5 cm bak skjermplanet. Heng bak skjermen i stemning (lyser på veggen),
    svingar opp og fram til eit tak over skjermkanten i arbeid. Rillene peikar mot brukaren."""
    return lampe(b(0.0, 0.50, 0.50), (-1, 0, 0), (0, 0, 1), 0.19, lengd, FORD['ut'] if ford is None else ford, 'tvers', (90, v1), bakstripe=q)

GREP = [
    ('pult', 'Biletet med fot, som teikna: ruta vender opp mot brukaren', lambda: pult((35, 35), FORD['ut'], 'bjelke')),
    ('over', 'Biletet med klemme, som teikna: ruta vender rett ned', lambda: over((0, 0), FORD['ut'], 'tvers')),
    ('over-vippa', 'Biletet med klemme, vippa 65° mot feltet i arbeid', lambda: over((0, 65), FORD['ut'], 'tvers')),
    ('ruta', 'Ruta over skjermkanten: bak skjermen i stemning, fram som tak i arbeid', lambda: ruta()),
    ('ruta-matt', 'Same rute med matt spreiar i staden for filmen', lambda: ruta(FORD['matt'])),
]

if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'tal':
        ut = {}
        for k, t, f in GREP:
            r = rekn(f(), n=5); r['tekst'] = t; ut[k] = r; print(linje(k, r), flush=True)
        json.dump(ut, open(os.path.join(HER, 'rute-tal.json'), 'w', encoding='utf-8'), indent=1, default=float, ensure_ascii=False)
    else:
        from PIL import Image, ImageDraw
        vis = [g for g in GREP if g[0] in ('pult', 'over-vippa', 'ruta')]
        px = 480; ims = []
        for k, t, f in vis:
            g = f()
            ims.append((t, ls.brett([ls.framkall(ls.luminans(*g(float(s)), px, 1), px) for s in (0.0, 1.0)], px, kol=2)))
            print(k, flush=True)
        W, H = ims[0][1].size
        ark = Image.new('RGB', (W, H * len(ims)), (0, 0, 0)); d = ImageDraw.Draw(ark); f1 = ls._font(17); f2 = ls._font(14)
        for i, (t, im) in enumerate(ims):
            ark.paste(im, (0, i * H))
            d.text((22, i * H + H - 30), t, fill=(190, 190, 190), font=f1)
            d.text((22, i * H + 20), 'stemning 1,25 W', fill=(150, 150, 150), font=f2)
            d.text((W // 2 + 14, i * H + 20), 'arbeid 5 W', fill=(150, 150, 150), font=f2)
        ark.save(os.path.join(HER, 'rute-tre.png')); print('rute-tre.png', ark.size)
