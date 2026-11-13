# -*- coding: utf-8 -*-
"""Generasjon 0: kvar hamnar lyset som går gjennom klippet? Prøve av oppstillinga før klippa blir varierte."""
import sys, os, time
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HER, '..', '..', 'lysskisse'))
from lysskisse import *

def lampe(kp, c, mot=FELT, klipp=None, storleik=0.25, n=22, t=1.0, spreiing=10):
    W, K = watt(t)
    k = straale(kp, c, W * LMW_KJELDE, K, spreiing=spreiing, kutt=2 * spreiing, opning=0.02, bronn=40)
    nn = nrm(nrm(kp - c) + nrm(mot - c))
    a = ark(k, c, nn, storleik, klipp=klipp, framside=SATIN, n=n)
    return [k, a], [syl(b(kp[0], kp[1], 0), b(kp[0], kp[1], 0.05), 0.05)]

ring = lambda r: (lambda u, v: u * u + v * v > r * r)
OPP = [
 ('opp-heil (mal)',   b(0.47, 0.48, 0.05), b(0.47, 0.40, 0.41), None),
 ('opp-ring',         b(0.47, 0.48, 0.05), b(0.47, 0.40, 0.41), ring(0.06)),
 ('fram25-ring',      b(0.47, 0.15, 0.05), b(0.47, 0.40, 0.41), ring(0.06)),
 ('fram30-ring',      b(0.47, 0.10, 0.05), b(0.47, 0.40, 0.41), ring(0.06)),
 ('fram25-h33-ring',  b(0.47, 0.15, 0.05), b(0.47, 0.40, 0.33), ring(0.06)),
 ('skra-ring',        b(0.60, 0.18, 0.05), b(0.45, 0.40, 0.41), ring(0.06)),
 ('skra2-ring',       b(0.66, 0.22, 0.05), b(0.44, 0.40, 0.38), ring(0.06)),
 ('skra2-heil',       b(0.66, 0.22, 0.05), b(0.44, 0.40, 0.38), None),
 ('side-ring',        b(0.68, 0.36, 0.05), b(0.42, 0.42, 0.38), ring(0.06)),
 ('nar-ring',         b(0.40, 0.20, 0.05), b(0.32, 0.40, 0.41), ring(0.06)),
]
if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for namn, kp, c, kl in OPP:
        t0 = time.time(); d = tal(*lampe(kp, c, klipp=kl))
        print('%-18s felt %4.0f U %.2f vegg %4.0f  forhold %.2f  auge %5.0f ansikt %3.0f lm_vegg %4.0f lm_tak %4.0f lm %4.0f  fordeling %s  %.1fs'
              % (namn, d['E_felt'], d['U'], d['E_vegg'], d['E_vegg'] / d['E_felt'], max(d['L_lampe'], d['L_flate']), d['E_ansikt'],
                 d['lm_vegg'], d['lm_tak'], d['lm'], np.round(d['_fordeling'], 2), time.time() - t0))
