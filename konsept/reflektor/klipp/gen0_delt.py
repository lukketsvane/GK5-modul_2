# -*- coding: utf-8 -*-
"""Generasjon 0c: gjev delt kjelde same tal som punktkjelde for eit grovt klipp? (kontroll av eige grep)"""
import sys
from gen0_stoy import *
ring = lambda r: (lambda u, v: u * u + v * v > r * r)
sys.stdout.reconfigure(encoding='utf-8')
for namn, kl in (('heil', None), ('ring6', ring(0.06)), ('ingen ark', lambda u, v: u > 9)):
    for delt in (1, 3, 6):
        d = tal(*lampe(kl, delt=delt))
        print('%-10s delt %d: felt %4.0f vegg %4.0f lm %4.0f lm_vegg %4.0f lm_tak %3.0f fordeling %s' % (namn, delt, d['E_felt'], d['E_vegg'], d['lm'], d['lm_vegg'], d['lm_tak'], np.round(d['_fordeling'], 3)))
