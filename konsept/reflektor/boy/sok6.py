# -*- coding: utf-8 -*-
"""Søk 6: koordinatsøk for to-adresse-arket (arbeid, t = 1). Mål: høg jamnheit, felt 350 lx og vegg 100 lx under 5 W."""
from familie import *
import json
def maal(p, **fast):
    kw = dict(A=b(p['Ax'], p['Ay'], 0), B=b(p['Bx'], YV, p['Bh']), sb=(0.07, p['sbw']), mjuk=p['mjuk'], kA=p['kA'], kB=p['kB'], vinkel=p['vinkel'])
    kw.update(fast)
    lys, kropp = to(1.0, 'gli', **kw); d = tal(lys, kropp)
    Wb = d['W'] * max(350 / d['E_felt'], 100 / max(d['E_vegg'], 1e-9))
    sc = d['U'] - 0.08 * max(Wb - 4.5, 0) - (0.2 if d['L_lampe'] > 1500 else 0)
    return sc, dict(felt=round(d['E_felt']), U=round(d['U'], 2), vegg=round(d['E_vegg']), auge=round(d['L_lampe']), Wb=round(Wb, 2))
ALT = dict(Ax=(-0.05, -0.10, -0.15), Ay=(0.21, 0.25, 0.29), sbw=(-0.055, -0.04, -0.025), mjuk=(0.014, 0.02, 0.03),
           kA=(-0.8, 0.0, 0.8), kB=(0.0, -2.5), Bh=(0.45, 0.60), Bx=(0.0, 0.2), vinkel=(0.9, 1.0, 1.1))
def sok(namn, **fast):
    p = dict(Ax=-0.10, Ay=0.25, sbw=-0.04, mjuk=0.02, kA=0.0, kB=0.0, Bh=0.45, Bx=0.0, vinkel=1.0)
    best, info = maal(p, **fast); print(namn, 'start', round(best, 3), info); sys.stdout.flush()
    for runde in range(2):
        for k, alts in ALT.items():
            for a in alts:
                if a == p[k]: continue
                q = dict(p); q[k] = a
                sc, inf = maal(q, **fast)
                if sc > best + 0.004:
                    best, info, p = sc, inf, q; print('  ', k, '=', a, round(sc, 3), inf); sys.stdout.flush()
    print(namn, 'SLUTT', json.dumps(p), info); sys.stdout.flush()
    return p
if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    sok('h0.41')
    sok('h0.55', c=(0.47, 0.30, 0.55), spreiing=7.2)
