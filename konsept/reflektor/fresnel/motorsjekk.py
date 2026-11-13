# -*- coding: utf-8 -*-
"""Tre kontrollar av motoren (lysskisse.py), utan å endre han. Køyr: python motorsjekk.py"""
from familie import *
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass

# 1. Brønnen stoppar lys, men rekneskapen tel det som sendt ut.
k = straale((0, 0, 0), (0, 0, 1), 500, 3000, spreiing=35, kutt=70, opning=0.02, bronn=40)
ut = 4 * PI * k.I(FIB).mean()
print('1 brønn: kjelda er sett til 500 lm, fordelinga I(d) inneheld %.0f lm. Skilnaden blir rekna som lys ut i rommet (lm_ut).' % ut)

# 2. To ark på same kjelde: lm_ut blir skriven over av det siste arket.
c = b(0.47, 0.40, 0.55); kp = b(0.47, 0.40, 0.05)
k = straale(kp, c, 500, 3000, spreiing=12, kutt=24, opning=0.02, bronn=40)
nn = nrm(nrm(kp - c) + nrm(FELT - c))
a1 = fresnelspegel(k, c, nn, n=16, klipp=lambda u, v: v >= 0); etter1 = k.lm_ut
a2 = fresnelspegel(k, c, nn, n=16, klipp=lambda u, v: v < 0); etter2 = k.lm_ut
print('2 to ark: inn på ark 1 %.0f lm, inn på ark 2 %.0f lm. lm_ut etter ark 1: %.0f, etter ark 2: %.0f. Rett svar: %.0f.'
      % (a1.lm_inn, a2.lm_inn, etter1, etter2, 500 - a1.lm_inn - a2.lm_inn))

# 3. Fresnel og form saman: dei optiske normalane følgjer ikkje bøyen.
k = straale(kp, c, 500, 3000, spreiing=12, kutt=24, opning=0.02, bronn=40)
flat = fresnelspegel(k, c, nn, n=16)
boygd = fresnelspegel(k, c, nn, n=16, form=boy(2.0))          # radius 0,5 m: kanten er vridd 16 grader
i = int(np.argmax(flat.Pf @ ortho(nn)[0]))                    # ei flis ytst langs u
vinkel = lambda a_: float(np.degrees(np.arccos(np.clip(flat.rr[0, i] @ a_.rr[0, i], -1, 1))))
print('3 bøygd fresnel: kantflisa er vridd %.1f grader av bøyen, så speglinga skulle flytta seg om lag %.0f grader. Motoren flyttar ho %.1f grader.'
      % (np.degrees(2.0 * 0.1425), 2 * np.degrees(2.0 * 0.1425), vinkel(boygd)))
