# -*- coding: utf-8 -*-
"""
eksporter_fin.py  ·  delane frå northern.py med fin netting, til rendring og 3D-fil

ut-b/samla/ held nettinga som passar til kontroll og utskrift. Nærbilete og USDZ treng runde kantar utan fasettar,
så her blir kvar del netta med 0,01 mm avvik og 2,3° mellom flatene. Skriv ut-b/fin/<id>.stl.

  python eksporter_fin.py
"""
import os, sys
from cadquery import exporters
import northern as N

def main():
    ut = os.path.join(N.UT, 'fin'); os.makedirs(ut, exist_ok=True)
    for (i, namn, form, *_r) in N.delar():
        exporters.export(form, os.path.join(ut, i + '.stl'), tolerance=0.01, angularTolerance=0.04)
        print('  %-3s %-18s %6.1f kB' % (i, namn, os.path.getsize(os.path.join(ut, i + '.stl')) / 1e3))
    exporters.export(N.leidning(), os.path.join(ut, 'leidning.stl'), tolerance=0.02, angularTolerance=0.06)

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    main()
