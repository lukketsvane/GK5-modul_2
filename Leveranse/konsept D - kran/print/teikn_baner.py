# -*- coding: utf-8 -*-
"""teikn_baner.py · teiknar verktøybanene i dei slica platene (G-koden i *.gcode.3mf) som eit 3D-bilete på svart.

  py -3 print/teikn_baner.py      skriv print/baner/<plate>.png og print/baner/baner.json (lag, høgd, støtte, banelengd)
Berre ekstruderingsrørsler blir teikna. Fargen går frå mørk grå nedst til kvit øvst. Den grå ramma er plata, 256 × 256 mm.
"""
import json
import math
import re
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

HER = Path(__file__).resolve().parent
UT = HER / 'baner'
TH, PH = math.radians(-32), math.radians(32)
B, H, K = 1600, 1066, 4.2          # biletstorleik og skala (piksel per mm)


def proj(x, y, z):
    xr = x * math.cos(TH) - y * math.sin(TH)
    yr = x * math.sin(TH) + y * math.cos(TH)
    return xr, z * math.cos(PH) + yr * math.sin(PH)


def main():
    UT.mkdir(exist_ok=True)
    info = {}
    for f in sorted(HER.glob('*.gcode.3mf')):
        namn = f.name.replace('.gcode.3mf', '')
        gk = zipfile.ZipFile(f).read('Metadata/plate_1.gcode').decode('utf-8', 'replace').splitlines()
        x = y = z = 0.0
        rel_e = True
        typ = ''
        seg, typar, lag = [], {}, set()
        for line in gk:
            if line.startswith('; FEATURE:') or line.startswith(';TYPE:'):
                typ = line.split(':', 1)[1].strip()          # Bambu skriv «; FEATURE: Outer wall» og så bortetter
                continue
            if line.startswith('M82'):
                rel_e = False
            elif line.startswith('M83'):
                rel_e = True
            if not (line.startswith('G1 ') or line.startswith('G0 ') or line.startswith('G2 ') or line.startswith('G3 ')):
                continue
            d = dict(re.findall(r'([XYZEF])(-?\d*\.?\d+)', line.split(';')[0]))
            nx, ny, nz = float(d.get('X', x)), float(d.get('Y', y)), float(d.get('Z', z))
            e = float(d.get('E', 0.0))
            if e > 0 and (nx != x or ny != y) and line[1] in '01' and nz < 300 and typ:
                seg.append((x, y, nx, ny, nz))
                typar[typ] = typar.get(typ, 0) + 1
                lag.add(round(nz, 3))
            x, y, z = nx, ny, nz
        zmax = max(s[4] for s in seg)
        hjorne = [proj(a, b, 0) for a, b in ((0, 0), (256, 0), (256, 256), (0, 256))]
        pts = [proj(s[0], s[1], s[4]) for s in seg] + hjorne + [proj(128, 128, zmax + 5)]
        umin, umax = min(p[0] for p in pts), max(p[0] for p in pts)
        vmin, vmax = min(p[1] for p in pts), max(p[1] for p in pts)
        k = min((B - 80) / (umax - umin), (H - 80) / (vmax - vmin))
        ou, ov = (B - (umax - umin) * k) / 2 - umin * k, (H - (vmax - vmin) * k) / 2 + vmax * k
        til = lambda p: (ou + p[0] * k, ov - p[1] * k)
        im = Image.new('RGB', (B, H), (0, 0, 0))
        dr = ImageDraw.Draw(im)
        dr.polygon([til(p) for p in hjorne], outline=(70, 70, 70), fill=(14, 14, 14))
        for s in seg:
            g = int(70 + 185 * (s[4] / zmax))
            dr.line([til(proj(s[0], s[1], s[4])), til(proj(s[2], s[3], s[4]))], fill=(g, g, g), width=1)
        im.save(UT / f'{namn}.png', optimize=True)
        stotte = sum(n for t, n in typar.items() if 'upport' in t)
        utypa = typar.get('', 0)
        info[namn] = dict(segment=len(seg), lag=len(lag), hogd_mm=round(zmax, 2), stotte_segment=stotte, utypa_segment=utypa,
                          typar={t: n for t, n in sorted(typar.items(), key=lambda kv: -kv[1])})
        print(namn, info[namn]['lag'], 'lag', info[namn]['hogd_mm'], 'mm, støttesegment', stotte, flush=True)
    (UT / 'baner.json').write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
