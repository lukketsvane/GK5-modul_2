# -*- coding: utf-8 -*-
"""Søk 11: stemninga til spegel-kuv-1.2 legg 142 lx på skjermflata. Hjelper det å sikte stemninga høgare på veggen?"""
from familie import *
if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    for h in (0.45, 0.55, 0.62, 0.70):
        fra = b(0.0, YV, h)
        g = lambda t: lampe(t, fot=F2, c=CF, mot=vipp(t, fra=fra, til=SIKT), ref=SIKT, form=boy(-1 / 1.2), side=BLANK, n=30)
        ls, ks = g(0.0); d = tal(ls, ks)
        lin = 'stemning sikte h %.2f: vegg %3.0f felt %3.0f skjerm %4.0f auge %4.0f a25 %4.0f' % (h, d['E_vegg'], d['E_felt'], d['E_skjerm'], max(d['L_lampe'], d['L_flate']), auge_i(ls, ks, 0.25))
        print(lin); open(os.path.join(HER, 'sok11.txt'), 'a', encoding='utf-8').write(lin + '\n')
