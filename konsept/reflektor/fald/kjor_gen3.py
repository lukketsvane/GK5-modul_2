# -*- coding: utf-8 -*-
"""Køyrer generasjon 3 (berre tal, px=0) med overgang for kandidatane, og serien skarp mot mjuk fald.
Skriv gen3/tal.md, gen3/tal.csv, gen3/ekstra.md og radius.md. Éin prosess, ingen multiprocessing."""
import sys, os, time
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
try: sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
except Exception: pass
from familie import *

t0 = time.time()
OVERG = ('bok', 'Z-samla', 'Z-spreidd', 'vifte', 'spel', 'bolgje', 'tak-vipp', 'Z-vipp', 'tak-sveip', 'rund-bok', 'liten-bok', 'fresnel-floy')
rader = kjor(GEN3, os.path.join(HER, 'gen3'), px=0, overg=OVERG)
vis(rader)
print('gen3 ferdig etter %.0f s' % (time.time() - t0))
if '--radius' in sys.argv:
    radiusserie(HER)
    print('radius ferdig etter %.0f s' % (time.time() - t0))
