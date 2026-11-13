# -*- coding: utf-8 -*-
"""Generasjon 0b: kor mykje støy gjev eit fint klipp i tal()? Same slissar, ulik fase. Og: kva kostar ei rendring?"""
import sys, os, time
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HER, '..', '..', 'lysskisse'))
from lysskisse import *

def lampe(klipp, n=30, delt=1, t=1.0):
    W, K = watt(t)
    kp = b(0.47, 0.15, 0.05); c = b(0.47, 0.40, 0.33)
    if delt == 1:
        ks = [straale(kp, c, W * LMW_KJELDE, K, spreiing=10, kutt=20, opning=0.02, bronn=40)]
    else:
        ax = nrm(c - kp); u, v = ortho(ax)
        ks = [straale(kp + 0.013 * (math.cos(a) * u + math.sin(a) * v), c + 0.013 * (math.cos(a) * u + math.sin(a) * v),
                      W * LMW_KJELDE / delt, K, spreiing=10, kutt=20, opning=0.02 / math.sqrt(delt), bronn=40)
              for a in np.arange(delt) * 2 * PI / delt]
    nn = nrm(nrm(kp - c) + nrm(FELT - c))
    a = ark(ks, c, nn, 0.25, klipp=klipp, framside=SATIN, n=n)
    return ks + [a], [syl(b(0.47, 0.15, 0), b(0.47, 0.15, 0.05), 0.05)]

sliss = lambda per, fase: (lambda u, v: ((u + 0.5) / per + fase) % 1.0 < 0.6)
if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for per in (0.05, 0.025):
        for delt in (1, 3):
            for n in (30,):
                r = []
                for fase in (0.0, 0.25, 0.5, 0.75):
                    t0 = time.time(); d = tal(*lampe(sliss(per, fase), n=n, delt=delt)); dt = time.time() - t0
                    r.append((d['E_felt'], d['E_vegg'], d['lm']))
                r = np.array(r)
                print('periode %.3f delt %d n %d: felt %s  vegg %s  lm %s  (%.1f s)' % (per, delt, n, np.round(r[:, 0]), np.round(r[:, 1]), np.round(r[:, 2]), dt))
    for delt in (1, 3):
        t0 = time.time(); im = framkall(luminans(*lampe(sliss(0.05, 0), delt=delt), 200, 1), 200)
        print('rendring px 200, delt %d: %.0f s' % (delt, time.time() - t0))
        Image.fromarray(im).save(os.path.join(HER, '_prove-delt%d.png' % delt))
