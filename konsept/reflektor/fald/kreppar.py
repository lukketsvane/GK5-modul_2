# -*- coding: utf-8 -*-
"""Skriv ut kreppane (plass, retning, vinkel, radius) for dei tre beste ved t = 0, 0,5 og 1,
og normalen til rotpanelet. Til oppskrifta på skissemodellen. Rein geometri, ingen lysrekning."""
import sys, os, math
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
from familie import *

def rotnormal(rot, t, anker=(0.0, 0.0), pos=(0.47, 0.40), hogd=0.41):
    c = b(pos[0], pos[1], hogd)
    m = rot(t) if callable(rot) else rot
    m = ADR[m] if isinstance(m, str) else np.asarray(m, float)
    n = nrm(nrm(KP - c) + nrm(m - c))
    for _ in range(2):
        ex, ey, ez = ramme(n); pa = c + anker[0] * ex + anker[1] * ey
        n = nrm(nrm(KP - pa) + nrm(m - pa))
    return c, n

def vis_(namn, kr, rot, anker=(0.0, 0.0)):
    for t in (0.0, 0.5, 1.0):
        c, n = rotnormal(rot, t, anker)
        k = kr(t, c, n) if callable(kr) else [dict(x, vinkel=x['vinkel']) for x in kr]
        hell = math.degrees(math.acos(abs(n[2])))
        print(f"{namn} t={t}: rotnormal ({n[0]:+.2f}, {n[1]:+.2f}, {n[2]:+.2f}), {hell:.0f} grader frå loddrett")
        for x in k:
            print(f"   krepp p=({x['p'][0]*1000:+.0f}, {x['p'][1]*1000:+.0f}) mm  ret {x['ret']:.0f} grader  vinkel {x['vinkel']:+.0f} grader  R {x['R']*1000:.0f} mm")

vis_('Z-spreidd', saman(K1(FX(-0.15), 0.03, True, R=MJ), K1(FX(0.15), 0.03, False, R=MJ)), 'vegg')
vis_('rund-bok', K1('felt', 0.07, False, R=MJ, anker=(0.04, 0.07)), 'vegg', anker=(0.04, 0.07))
vis_('tak-vipp', FAST_TAK_MJ, vipp)
