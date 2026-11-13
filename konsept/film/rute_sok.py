# -*- coding: utf-8 -*-
"""rute_sok.py  ·  dei to lampene frå bileta, og ruta over skjermen, med ulike arkoppsett og vippevinklar"""
import sys, json, os
import numpy as np
from rute import *
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass

FORD = {'matt': utfordeling(film=None), 'ut': utfordeling(innside='flat'), 'inn': utfordeling(innside='prisme'), 'kryss': utfordeling(innside='flat', lag2='kryss')}

def pult(v, ford, riller):      # biletet med fot: bjelke 27 cm oppe til høgre for skjermen, ruta 30 x 19 cm
    return lampe(b(0.47, 0.36, 0.27), (1, 0, 0), (0, 0, 1), 0.19, 0.30, ford, riller, v, fot=(0.47, 0.42))
def over(v, ford, riller):      # biletet med klemme: tak 32 x 16 cm, 33 cm oppe, festa i høgre ende
    return lampe(b(0.66, 0.40, 0.33), (0, 1, 0), (0, 0, -1), 0.32, 0.16, ford, riller, v, fot=(0.69, 0.40))
def skjerm(v, ford, riller, lengd=0.30, h=0.50, y=0.50):    # ruta over skjermkanten: heng bak skjermen i stemning, svingar fram i arbeid
    return lampe(b(0.0, y, h), (-1, 0, 0), (0, 0, 1), 0.19, lengd, ford, riller, v)

ut = {}
def kjor(namn, g):
    r = rekn(g, n=3); ut[namn] = r; print(linje(namn, r), flush=True)

if __name__ == '__main__':
    kva = sys.argv[1] if len(sys.argv) > 1 else 'a'
    if kva == 'a':
        for fk in ('matt', 'ut'):
            for ri in ('bjelke', 'tvers') if fk != 'matt' else ('bjelke',):
                kjor('pult teikna %s/%s' % (fk, ri), pult((35, 35), FORD[fk], ri))
                for v1 in (150, 180, 210):
                    kjor('pult 35->%d %s/%s' % (v1, fk, ri), pult((35, v1), FORD[fk], ri))
                kjor('over teikna %s/%s' % (fk, ri), over((0, 0), FORD[fk], ri))
                for v1 in (25, 45, 65):
                    kjor('over 0->%d %s/%s' % (v1, fk, ri), over((0, v1), FORD[fk], ri))
    else:
        for fk in ('matt', 'ut', 'kryss', 'inn'):
            for ri in ('bjelke', 'tvers') if fk in ('ut', 'inn') else ('bjelke',):
                for v1 in (190, 210, 230):
                    kjor('skjerm 90->%d %s/%s' % (v1, fk, ri), skjerm((90, v1), FORD[fk], ri))
    json.dump(ut, open(os.path.join(HER, 'rute-sok-%s.json' % kva), 'w', encoding='utf-8'), indent=1, default=float)
