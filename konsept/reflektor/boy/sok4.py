# -*- coding: utf-8 -*-
"""Søk 4: to adresser etter retting (sone A i referanseplanet). Berre arbeid, pluss stemning for nokre."""
from sok3 import v2
from familie import *
def v3(namn, g):
    r = []
    for t in (0.0, 1.0):
        lys, kropp = g(t); d = tal(lys, kropp); r.append((d, skjermlux(lys, kropp)))
    (s, ss), (a, sa) = r
    print('%-26s arbeid: felt %4.0f U %.2f vegg %3.0f auge %5.0f flate %4.0f skjerm %3.0f Wbegge %5.2f | stemning: felt %3.0f vegg %3.0f auge %4.0f flate %3.0f skjerm %3.0f' % (
        namn, a['E_felt'], a['U'], a['E_vegg'], a['L_lampe'], a['L_flate'], sa, a['W'] * max(350 / a['E_felt'], 100 / max(a['E_vegg'], 1e-9)),
        s['E_felt'], s['E_vegg'], s['L_lampe'], s['L_flate'], ss)); sys.stdout.flush()
if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    for d1 in (-0.06, -0.03, 0.0):
        v3('to-vandr du1=%+.2f' % d1, lambda t: to(t, 'vandr', du=(0.08, d1)))
    for dl in (0.5, 0.6, 0.7):
        v3('to-kryss deling=%.1f' % dl, lambda t: to(t, 'kryss', deling=dl))
    v3('to-vipp', lambda t: to(t, 'vipp'))
    v3('to-hog', lambda t: to(t, 'vandr', c=(0.47, 0.30, 0.55), spreiing=7.2))
    v3('to-hog kA=1.2', lambda t: to(t, 'vandr', c=(0.47, 0.30, 0.55), spreiing=7.2, kA=1.2))
    v3('to-hol', lambda t: to(t, 'vandr', hol=True))
    v3('over-skjerm', over_skjerm)
    v3('to-trau', lambda t: to(t, 'vandr', trau=0.5))
    v3('to-vandr kA=1.2', lambda t: to(t, 'vandr', kA=1.2))
    v3('to-vandr blank', lambda t: to(t, 'vandr', side=BLANK, n=30))
