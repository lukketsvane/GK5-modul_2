# -*- coding: utf-8 -*-
"""Søk 10: koordinatsøk for to-adresse-spegelen (BLANK, arbeid). Mål: høg jamnheit med 350 lx på feltet og 100 lx på veggen
under 5 W, og under 1500 cd/m² mot auget i 25, 47 og 60 cm. Same søk som sok6, men på spegel og med alle augehøgder."""
from familie import *
import json
UT = os.path.join(HER, 'sok10.txt')
def logg(*a):
    s = ' '.join(str(x) for x in a); print(s); sys.stdout.flush()
    with open(UT, 'a', encoding='utf-8') as fh: fh.write(s + '\n')
def maal(p, **fast):
    kw = dict(A=b(p['Ax'], p['Ay'], 0), B=b(p['Bx'], YV, p['Bh']), sb=(0.07, p['sbw']), mjuk=p['mjuk'], kA=p['kA'], kB=p['kB'],
              vinkel=p['vinkel'], side=BLANK, n=30)
    kw.update(fast)
    lys, kropp = to(1.0, 'gli', **kw); d = tal(lys, kropp)
    au = max(d['L_lampe'], auge_i(lys, kropp, 0.25), auge_i(lys, kropp, 0.60))
    Wb = d['W'] * max(350 / d['E_felt'], 100 / max(d['E_vegg'], 1e-9))
    sc = d['U'] - 0.08 * max(Wb - 4.5, 0) - (0.3 if au > 1500 else 0)
    return sc, dict(felt=round(d['E_felt']), U=round(d['U'], 2), vegg=round(d['E_vegg']), auge=round(au), Wb=round(Wb, 2))
ALT = dict(Ax=(-0.05, -0.15), Ay=(0.21, 0.29), sbw=(-0.055, -0.025), mjuk=(0.014, 0.03),
           kA=(-0.8, 0.8), kB=(-2.5, 1.5), Bh=(0.30, 0.60), Bx=(-0.2, 0.2), vinkel=(0.9, 1.1))
if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    p = dict(Ax=-0.10, Ay=0.25, sbw=-0.04, mjuk=0.02, kA=0.0, kB=0.0, Bh=0.45, Bx=0.0, vinkel=1.0)
    best, info = maal(p); logg('start', round(best, 3), info)
    for runde in range(2):
        betre = False
        for k, alts in ALT.items():
            for a in alts:
                q = dict(p); q[k] = a
                if q == p: continue
                sc, inf = maal(q)
                if sc > best + 0.004:
                    best, info, p = sc, inf, q; betre = True; logg('  ', k, '=', a, round(sc, 3), inf)
        if not betre: break
    logg('SLUTT', json.dumps(p), info)
