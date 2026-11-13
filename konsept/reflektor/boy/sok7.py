# -*- coding: utf-8 -*-
"""Søk 7 (økt 2, etter avbrotet): dei to opne spørsmåla før generasjon 3.
(a) Held den blanke kuve bøyen (beste i gen2) i alle augehøgder 25 til 60 cm, og kor stor og kor lita kan han vere?
(b) Kva gjev to-adresse-arket med den retta to() (sone A i referanseplanet)? Gen2-tala for to-* kom frå ein eldre to().
Skriv kvar linje til sok7.txt straks, så eit avbrot ikkje tek tala."""
from familie import *
UT = os.path.join(HER, 'sok7.txt')

def v(namn, g):
    r = []
    for t in (0.0, 1.0):
        lys, kropp = g(t); d = tal(lys, kropp)
        d['a25'] = auge_i(lys, kropp, 0.25); d['a60'] = auge_i(lys, kropp, 0.60); d['skj'] = skjermlux(lys, kropp)
        r.append(d)
    s, a = r
    Wb = a['W'] * max(350 / a['E_felt'], 100 / max(a['E_vegg'], 1e-9))
    lin = ('%-20s A: felt %4.0f U %.2f W350 %5.2f vegg %3.0f Wbegge %5.2f auge47 %5.0f a25 %5.0f a60 %5.0f flate %4.0f skj %3.0f'
           ' | S: felt %3.0f vegg %3.0f auge47 %4.0f a25 %4.0f a60 %4.0f | strekk %.2f %%'
           % (namn, a['E_felt'], a['U'], a['W'] * 350 / a['E_felt'], a['E_vegg'], Wb, a['L_lampe'], a['a25'], a['a60'], a['L_flate'], a['skj'],
              s['E_felt'], s['E_vegg'], s['L_lampe'], s['a25'], s['a60'], a['strekk'] * 100))
    print(lin); sys.stdout.flush()
    with open(UT, 'a', encoding='utf-8') as fh: fh.write(lin + '\n')

FOLIE = dict(rd=0.04, rs=0.82, sigma=3.0)      # glatt aluminiumsfolie (ANTAKING)
KROLL = dict(rd=0.10, rs=0.70, sigma=8.0)      # krølla og glatta folie (ANTAKING)

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    hva = sys.argv[1] if len(sys.argv) > 1 else 'a'
    if hva == 'a':
        v('blank-kuv R0.6', g2(form=boy(-1 / 0.6), side=BLANK, n=30))
        v('blank-kuv R0.3', g2(form=boy(-1 / 0.3), side=BLANK, n=30))
        v('blank-kuv R1.2', g2(form=boy(-1 / 1.2), side=BLANK, n=30))
        v('blank-flat', g2(side=BLANK, n=30))
        v('folie-kuv R0.6', g2(form=boy(-1 / 0.6), side=FOLIE, n=30))
        v('kroll-kuv R0.6', g2(form=boy(-1 / 0.6), side=KROLL, n=30))
        v('blank-kuvkast R0.6', g2(form=boy(-1 / 0.6), rull=90, side=BLANK, n=30))
        v('blank-kuv 0.15', g2(form=boy(-1 / 0.3), side=BLANK, n=30, storleik=0.15, spreiing=6))
        v('blank-kuv 0.35', g2(form=boy(-1 / 0.6), side=BLANK, n=30, storleik=0.35, spreiing=14))
    else:
        v('to-gli', lambda t: to(t, 'gli'))
        v('to-kryss', lambda t: to(t, 'kryss'))
        v('to-gli blank', lambda t: to(t, 'gli', side=BLANK, n=30))
        v('to-gli hog', lambda t: to(t, 'gli', c=(0.47, 0.30, 0.55), spreiing=7.2))
