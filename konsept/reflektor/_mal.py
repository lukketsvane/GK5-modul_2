# -*- coding: utf-8 -*-
"""Mal for ein formfamilie. Kopier fila, gje ho nytt namn og byt ut GREP.

  python _mal.py            tal og prøvebrett i mappa _mal/

Eit lysgrep er ein funksjon g(t) -> (lys, kropp). t = 0 er stemning, t = 1 er arbeid,
og alt imellom er overgangen. Sjå konsept/lysskisse/API.md.
"""
import sys, os
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HER, '..', 'lysskisse'))
from lysskisse import *

FOT = (0.47, 0.48)      # foten står til høgre for skjermen. Lyspunkt og reflektor må liggje framfor skjermplanet (y under 0,45).

def reflektor(t, form=None, klipp=None, side=SATIN, storleik=0.25, hogd=0.41, mot=None, spreiing=10):
    """Kjelde i foten lyser opp på eit ark. Arket står slik at speglinga går mot punktet «mot»."""
    W, K = watt(t)
    mot = FELT if mot is None else mot
    c = b(0.47, 0.40, hogd); kp = b(FOT[0], FOT[1], 0.05)
    k = straale(kp, c, W * LMW_KJELDE, K, spreiing=spreiing, kutt=2 * spreiing, opning=0.02, bronn=40)
    n = nrm(nrm(kp - c) + nrm(mot - c))
    a = ark(k, c, n, storleik, form=form, klipp=klipp, framside=side)
    kropp = [syl(b(FOT[0], FOT[1], 0), b(FOT[0], FOT[1], 0.05), 0.06)]
    return [k, a], kropp

def vipp(t):
    """Overgang ved å vippe: speglinga flyttar seg frå veggen bak skjermen til arbeidsfeltet."""
    return b(0.0, YV, 0.45) * (1 - t) + FELT * t

GREP = [
    ('flat',     lambda t: reflektor(t, mot=vipp(t))),
    ('hol',      lambda t: reflektor(t, mot=vipp(t), form=boy(1 / 0.6))),
    ('kuv',      lambda t: reflektor(t, mot=vipp(t), form=boy(-1 / 0.6))),
    ('fald',     lambda t: reflektor(t, mot=vipp(t), form=fald([(0.0, 25)]))),
    ('slissa',   lambda t: reflektor(t, mot=vipp(t), klipp=lambda u, v: np.floor((u + 0.2) / 0.025) % 2 == 0)),
    ('vend',     lambda t: reflektor(t, side=(MATT if t < 0.5 else SATIN))),
]

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    ut = os.path.join(HER, '_mal')
    for r in familie(GREP, ut, px=220):
        print('%-8s felt %4.0f lx  jamnheit %.2f  W for 350 lx %.2f  vegg %3.0f lx  auge %5.0f  stemning: auge %5.0f, vegg %3.0f lx  likskap %.2f  strekk %.2f %%'
              % (r['namn'], r['felt'], r['jamnheit'], r['W350'], r['vegg'], r['auge'], r['s_auge'], r['s_vegg'], r['likskap'], r['strekk'] * 100))
    _, m = overgang(GREP[0][1], n=5)
    print('overgang flat: topp %.2f  sprang %.2f  jamn auke %.2f' % (m['topp'], m['sprang'], m['jamn_auke']))
    print('  mot auget langs overgangen:', [round(x) for x in m['auge']])
    par(GREP[1][1], os.path.join(ut, 'par-hol.png'), px=240, ss=1, steg=(0.0, 0.5, 1.0))
