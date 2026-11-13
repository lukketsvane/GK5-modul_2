# -*- coding: utf-8 -*-
"""Avgjerd 2: biletet viser dioden i over-vipp frå kameraet (80 cm over bordet, bak høgre skulder), sjølv om auget i 47 cm
ikkje ser han. Kor djup må brønnen vere før dioden er gøymd frå kameraet òg, og kva kostar det? Skriv avgjerd-bronn.txt."""
from familie import *
import familie as _f
_f.N = N_FIN
KAMPOS = np.array([0.98, -1.40, ZB + 0.80])
ut = []
for kj in (VID, (40, 50, 50), (30, 45, 45), (25, 40, 40)):
    for t in (0.0, 1.0):
        lys, kropp = plate(t, OVER_C, OVER_A, 0.12, gli(b(0.0, YV, 0.60), FELT), spreiing=12, kjelde=kj)
        d = tal(lys, kropp); k = lys[0]
        p = k.pts[0]; w = nrm(KAMPOS - p); vk = float(np.degrees(np.arccos(np.clip(w @ k.akse, -1, 1))))
        La = nrm(AUGE - p); va = float(np.degrees(np.arccos(np.clip(La @ k.akse, -1, 1))))
        Lk = float(k.L(w[None])[0])
        s = ('kjelde %s t=%.0f: felt %4.0f lx  U %.2f  vegg %3.0f  auge %4.0f  stemning/arbeid  | vinkel til auget %.0f grader, '
             'til kameraet %.0f grader, dioden mot kameraet %.0f cd/m2' % (kj, t, d['E_felt'], d['U'], d['E_vegg'],
             max(d['L_lampe'], d['L_flate']), va, vk, Lk))
        print(s, flush=True); ut.append(s)
open(os.path.join(HER, 'avgjerd-bronn.txt'), 'w', encoding='utf-8').write('\n'.join(ut) + '\n')
