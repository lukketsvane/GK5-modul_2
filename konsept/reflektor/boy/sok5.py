# -*- coding: utf-8 -*-
"""Søk 5: kvar ligg den mørkaste ruta for to-adresse-arket, og kva hjelper?"""
from sok import *
def v(namn, rute=False, **kw):
    g = lambda t: to(t, 'vandr', **kw)
    lys, kropp = g(1.0); d = tal(lys, kropp)
    print('%-30s felt %4.0f U %.2f vegg %3.0f auge %5.0f skjerm %3.0f Wbegge %5.2f lm %3.0f' % (namn, d['E_felt'], d['U'], d['E_vegg'], d['L_lampe'], skjermlux(lys, kropp),
          d['W'] * max(350 / d['E_felt'], 100 / max(d['E_vegg'], 1e-9)), d['lm']))
    if rute:
        c = ruter(lys, kropp)
        for j in range(3, -1, -1): print('      y=%.2f  ' % (0.10 + 0.1 * j) + ' '.join('%5.0f' % c[i, j] for i in range(6)))
    sys.stdout.flush()
if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    v('grunn', rute=True)
    v('hog', rute=True, c=(0.47, 0.30, 0.55), spreiing=7.2)
    v('u0=+0.04 du1=-0.03', u0=0.04, rute=True)
    v('u0=+0.04 st0.34', u0=0.04, st=(0.34, 0.25))
    v('u0=-0.04', u0=-0.04)
    v('c y=0.26', c=(0.47, 0.26, 0.41), fot=(0.47, 0.34))
    v('c y=0.34', c=(0.47, 0.34, 0.41), fot=(0.47, 0.42))
    v('A x=-0.05', A=b(-0.05, 0.25, 0))
    v('A x=-0.15', A=b(-0.15, 0.25, 0))
    v('A y=0.20', A=b(-0.10, 0.20, 0))
    v('A y=0.30', A=b(-0.10, 0.30, 0))
    v('mjuk 0.035', mjuk=0.035)
    v('mjuk 0.012', mjuk=0.012)
    v('spreiing 12', spreiing=12)
    v('vifte (12,8)', flat=(12, 8))
    v('vifte (8,12)', flat=(8, 12))
    v('B vegg h0.60', B=b(0, YV, 0.60))
    v('B vegg x+0.2', B=b(0.2, YV, 0.45))
