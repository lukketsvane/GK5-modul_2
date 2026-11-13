# -*- coding: utf-8 -*-
import sys, time, math
import numpy as np
from PIL import Image
from kast import *
from film import Film, prisme
b = ls.b
t0 = time.time()
pos = b(0.40, 0.42, 0.65)
for namn, film, side in (('open', None, 'prisme'), ('prisme-inn', Film(prisme(90)), 'prisme'), ('flat-inn', Film(prisme(90)), 'flat')):
    k = Kast(pos, b(0.0, 0.70, 0.45) * 0.5 + b(0.0, 0.25, 0.0) * 0.5, W=5, K=3000, film=film, riller=(1, 0, 0), side=side,
             a=0.05, diode=0.002, film_storleik=(0.05, 0.05), masker=[maske(0.048, vindauge(0.036, 0.036, 2, 2, 0.12))], N=3_000_000, opplaus=0.5)
    r = k.rekneskap
    print(namn, 'tid %.1f s' % (time.time() - t0), {a: round(float(v), 3) for a, v in r.items()})
    d = ls.tal(k.lys(), [])
    print('   tal:', {a: round(float(d[a]), 1) for a in ('W', 'lm', 'E_felt', 'U', 'E_bak', 'E_vegg', 'E_skjerm', 'E_ansikt', 'L_lampe', 'L_auge25', 'L_auge60')})
    print('   kart vegg maks %.0f lx, bord maks %.0f lx' % (k.kart_vegg.sum(2).max() if False else (k.kart_vegg @ ls.LUM).max(), (k.kart_bord @ ls.LUM).max()))
    Image.fromarray(kartbilete(k.kart_vegg, 60)).save('prove-vegg-%s.png' % namn)
    Image.fromarray(kartbilete(k.kart_bord, 60)).save('prove-bord-%s.png' % namn)
