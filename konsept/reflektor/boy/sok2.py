# -*- coding: utf-8 -*-
"""Søk 2: arket framfor skjermplanet. Kva gjer plass, sikte, bøy langs kastet og vifteforma stråle? Berre arbeid (t = 1)."""
from sok import *
F2 = (0.47, 0.38)            # foten flytta fram, så heile arket ligg framfor skjermplanet
def L(**kw):
    kw.setdefault('fot', F2); kw.setdefault('c', (0.47, 0.30, 0.41))
    return lambda t: lampe(t, **kw)
if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    print('--- plass'); 
    vis('mal-plass flat', lambda t: lampe(t), rute=False)
    vis('fram flat', L())
    vis('fram hol-kast', L(form=boy(1 / 0.6), rull=90))
    vis('fram hol-breidd', L(form=boy(1 / 0.6)))
    print('--- sikte og bøy langs kastet (k0, k1)')
    for mx in (0.0, -0.10, -0.20):
        for k0 in (-1.5, 0.0, 1.67):
            for k1 in (-3.0, 0.0, 3.0):
                kap = (lambda k0, k1: (lambda s: k0 + k1 * np.clip(s / 0.125, -1.2, 1.2)))(k0, k1)
                vis('mx%+.2f k0%+.1f k1%+.1f' % (mx, k0, k1), L(mot=b(mx, 0.25, 0), form=boy(kap), rull=90), rute=False)
    print('--- vifte')
    for fl in ((14, 8), (8, 14), (16, 6), (6, 16)):
        vis('flat vifte %s' % (fl,), L(flat=fl, mot=b(-0.10, 0.25, 0)), rute=False)
        vis('holkast vifte %s' % (fl,), L(flat=fl, mot=b(-0.10, 0.25, 0), form=boy(1 / 0.6), rull=90), rute=False)
    print('--- høgd')
    for h in (0.30, 0.55, 0.70):
        vis('h=%.2f flat' % h, L(c=(0.47, 0.30, h), spreiing=10 * 0.36 / (h - 0.05), mot=b(-0.10, 0.25, 0)), rute=False)
