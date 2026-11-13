# -*- coding: utf-8 -*-
"""Søk 9: kontroll. Er jamnheita 0,60 for alle blanke kuve ark ein eigenskap ved lyset eller ved noko anna? Rutene på feltet."""
from sok import *
from sok7 import FOLIE
if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    for R in (0.6, 2.0):
        vis('blank-kuv R%.1f' % R, g2(form=boy(-1 / R), side=BLANK, n=30))
    vis('blank-flat', g2(side=BLANK, n=30))
    vis('to-gli blank', lambda t: to(t, 'gli', side=BLANK, n=30))
    vis('to-blank hog', lambda t: to(t, 'gli', side=BLANK, n=30, c=(0.47, 0.30, 0.55), spreiing=7.2))
    lys, kropp = g2(form=boy(-1 / 1.2), side=BLANK, n=30)(1.0)
    a = [l for l in lys if isinstance(l, Ark)][0]
    okkl = [p for p in STATISK + list(kropp) + [l.prim for l in lys] if p not in PERSON]
    print('L frå kjelda mot auget:', [round(float(l.L(nrm(AUGE - l.pts[0])[None])[0])) for l in lys if not isinstance(l, Ark)])
    print('L frå arket mot auget:', round(a.L_mot(AUGE, okkl)))
