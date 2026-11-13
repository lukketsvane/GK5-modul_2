# -*- coding: utf-8 -*-
"""Søkjehjelp for familien BØY: rutenettet på feltet, og raske enkeltmålingar. Ikkje ein del av leveransen."""
from familie import *

def ruter(lys, kropp):
    """Lux i dei 6 x 4 rutene på feltet (x frå -0,3 til 0,3 bortover, y frå 0,05 til 0,45 nedover i utskrifta)."""
    R = rom(); okkl = STATISK + list(kropp) + [l.prim for l in lys]
    Ed = E_direkte(R.P, R.N, lys, okkl); Ei, B = R.radiositet(Ed)
    Y = (Ed + Ei) @ LUM; kb = R.kart[0]
    return Y[kb.sl].reshape(28, 14)[8:20, 1:9].reshape(6, 2, 4, 2).mean((1, 3))

def vis(namn, g, t=1.0, rute=True):
    lys, kropp = g(t); d = tal(lys, kropp)
    print('%-16s t=%.1f felt %4.0f U %.2f W350 %5.2f vegg %3.0f ansikt %3.0f L_lampe %5.0f L_flate %4.0f lm %3.0f nytte %.2f strekk %.3f'
          % (namn, t, d['E_felt'], d['U'], d['W'] * 350 / d['E_felt'], d['E_vegg'], d['E_ansikt'], d['L_lampe'], d['L_flate'], d['lm'], d['nytte'], d['strekk']))
    if rute:
        c = ruter(lys, kropp)
        for j in range(3, -1, -1):
            print('      y=%.2f  ' % (0.10 + 0.1 * j) + ' '.join('%5.0f' % c[i, j] for i in range(6)))
    sys.stdout.flush()
    return d

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    vis('flat', lambda t: lampe(t))
    vis('hol-v', lambda t: lampe(t, form=boy(1 / 0.6), rull=90))
    vis('hol-v-stram', lambda t: lampe(t, form=boy(1 / 0.3), rull=90))
    vis('rull-v', lambda t: lampe(t, form=boy(kappa_rull(2.0, 0.05, -1)), rull=90))
    for h in (0.22, 0.30, 0.55, 0.70):
        vis('flat h=%.2f' % h, lambda t: lampe(t, c=(0.47, 0.40, h), spreiing=10 * 0.36 / (h - 0.05)), rute=(h in (0.22, 0.70)))
    for mx in (-0.10, -0.20):
        vis('flat mot x=%.2f' % mx, lambda t: lampe(t, mot=b(mx, 0.25, 0)))
    vis('flat stor 0.40 spr16', lambda t: lampe(t, storleik=0.40, spreiing=16))
    vis('flat liten 0.12 spr5', lambda t: lampe(t, storleik=0.12, spreiing=5))
