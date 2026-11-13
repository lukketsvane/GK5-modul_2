# -*- coding: utf-8 -*-
"""studie.py · lysstudie for kroppane i valet: stemning | arbeid, same kamera og eksponering (lysmotoren sin par())

  python studie.py over-band-vindauge-q30 fot-knekk     skriv studie-<grep>.png
"""
import os, sys, time
os.environ['LYSSKISSE_POLGE'] = '1'            # ryggfiguren skal vere med i rombileta
import lys

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    G = dict(lys.GREP)
    for namn in sys.argv[1:]:
        t0 = time.time()
        fil = os.path.join(lys.HER, 'studie-%s.png' % namn)
        lys.ls.par(G[namn], fil, px=420, ss=2, steg=(0.0, 1.0))
        print('studie', namn, '%.0f s' % (time.time() - t0), fil, flush=True)
