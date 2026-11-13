# -*- coding: utf-8 -*-
"""Søk 3: to adresser frå éi flate. Ei sone mot feltet, ei mjuk bøy, ei sone mot veggen. Strålen vandrar over bøyen."""
from sok import *
F2 = (0.47, 0.38)
def to(t, fot=F2, c=(0.47, 0.30, 0.41), u0=0.04, knekk=None, mjuk=0.02, kA=0.0, kB=0.0, hol=False, st=(0.34, 0.25), mx=-0.10, B=None, **kw):
    r, th = to_retning(c, fot, A=b(mx, 0.25, 0), B=B)
    th = th if knekk is None else knekk
    if hol: r += 180; form = boy(kappa_to(kA, kB, u0, mjuk, +th))
    else: form = boy(kappa_to(kA, kB, u0, mjuk, -th))
    return lampe(t, fot=fot, c=c, mot=b(mx, 0.25, 0), ref=b(mx, 0.25, 0), form=form, rull=r, storleik=st, **kw)
def v2(namn, g):
    lys, kropp = g(1.0); d = tal(lys, kropp)
    print('%-34s felt %4.0f U %.2f vegg %3.0f auge %5.0f flate %4.0f skjerm %4.0f lm %3.0f | Wbegge %.2f' % (namn, d['E_felt'], d['U'], d['E_vegg'], d['L_lampe'], d['L_flate'], skjermlux(lys, kropp), d['lm'],
          d['W'] * max(350 / d['E_felt'], 100 / max(d['E_vegg'], 1e-9)))); sys.stdout.flush()
if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    for c, fot in (((0.47, 0.30, 0.41), F2), ((0.47, 0.36, 0.41), (0.47, 0.44)), ((0.47, 0.30, 0.55), F2)):
        print('retning', c, to_retning(c, fot, A=b(-0.10, 0.25, 0)))
    print('--- kuv, strålen vandrar (du frå bøyen)')
    for du in (-0.10, -0.05, 0.0, 0.05, 0.10):
        v2('kuv du=%+.2f' % du, lambda t: to(t, treff=(0.04 + du, 0)))
    print('--- hol')
    for du in (-0.08, -0.03, 0.02):
        v2('hol du=%+.2f' % du, lambda t: to(t, hol=True, u0=-0.04, treff=(-0.04 - du, 0)))
    print('--- plass og høgd, kuv, du=-0.03')
    v2('bak y0.36', lambda t: to(t, c=(0.47, 0.36, 0.41), fot=(0.47, 0.44), treff=(0.01, 0)))
    v2('hog h0.55', lambda t: to(t, c=(0.47, 0.30, 0.55), treff=(0.01, 0), spreiing=7.2))
    v2('hog h0.55 bak', lambda t: to(t, c=(0.47, 0.36, 0.55), fot=(0.47, 0.44), treff=(0.01, 0), spreiing=7.2))
    print('--- veggmål høgare og mjukare bøy')
    v2('vegg h0.60', lambda t: to(t, treff=(0.01, 0), B=b(0, YV, 0.60)))
    v2('mjuk 0.04', lambda t: to(t, treff=(0.01, 0), mjuk=0.04))
    v2('kB kuv -3', lambda t: to(t, treff=(0.01, 0), kB=-3.0))
    v2('kA hol 1.2', lambda t: to(t, treff=(0.01, 0), kA=1.2))
