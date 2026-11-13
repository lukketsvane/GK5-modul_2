# -*- coding: utf-8 -*-
"""Søk 8: finjustering før generasjon 3. Kor slak kan spegelbøyen vere, kor lite kan arket bli, og kva gjer høgd med to-adresse-spegelen?"""
from sok7 import *
UT2 = os.path.join(HER, 'sok8.txt')
import sok7; sok7.UT = UT2
if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    for R in (0.9, 2.0):
        v('blank-kuv R%.1f' % R, g2(form=boy(-1 / R), side=BLANK, n=30))
    v('folie-kuv R1.2', g2(form=boy(-1 / 1.2), side=FOLIE, n=30))
    for st, sp, R in ((0.18, 7, 0.6), (0.18, 7, 1.2), (0.20, 8, 0.9), (0.32, 13, 1.2)):
        v('blank-kuv %.2f R%.1f' % (st, R), g2(form=boy(-1 / R), side=BLANK, n=30, storleik=st, spreiing=sp))
    v('to-blank hog', lambda t: to(t, 'gli', side=BLANK, n=30, c=(0.47, 0.30, 0.55), spreiing=7.2))
    v('to-blank kryss', lambda t: to(t, 'kryss', side=BLANK, n=30))
    v('to-folie', lambda t: to(t, 'gli', side=FOLIE, n=30))
    v('to-blank kA-0.8', lambda t: to(t, 'gli', side=BLANK, n=30, kA=-0.8))
    v('to-blank vipp', lambda t: to(t, 'vipp', side=BLANK, n=30))
    v('blank-hol R0.3', g2(form=boy(1 / 0.3), side=BLANK, n=30))
