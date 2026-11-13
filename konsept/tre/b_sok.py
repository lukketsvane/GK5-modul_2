# -*- coding: utf-8 -*-
"""
b_sok.py  ·  B Over: veggflik og jamnheit

Fresnelplata over skjermkanten er delt langs ein diameter og knekt (knekk2 i familien): den store delen lyser
på feltet, fliken på veggen bak skjermen. Kjelda står fast på skjermkanten i ein brønn på 50°.
Søket: høgda på plata, breidda på fliken, diffusorarket og kvar fliken siktar på veggen.

  python b_sok.py
"""
import os, sys, json, itertools
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
import tre
from tre import ls, fre, b, YV, FELT
import numpy as np

KP = fre.OVER_C + 0.12 * fre.OVER_A          # kjelda på skjermkanten, same stad som før
BRONN50 = (40, 50, 50)

def b_ny(zc=0.62, flik=0.10, spr=12, vegg=None):
    vegg = b(0.0, YV, 0.60) if vegg is None else vegg
    c = np.array([fre.OVER_C[0], fre.OVER_C[1], ls.ZB + zc])
    d = KP - c; s = float(np.linalg.norm(d)); a = d / s
    if flik <= 0:
        g = lambda t: fre.plate(t, c, a, s, fre.gli(vegg, FELT), spreiing=spr, kjelde=BRONN50)
    else:
        g = lambda t: fre.knekk2(t, c, a, s, vegg, FELT, spreiing=spr, kjelde=BRONN50, flytt=0.0, flik=flik)
    return tre._med_stolpe(g)

def rad(namn, g):
    s = ls.tal(*g(0.0)); a = ls.tal(*g(1.0))
    f = 350.0 / max(a['E_felt'], 1e-9)
    L = lambda d: max(d['L_auge25'], d['L_lampe'], d['L_auge60'], d['L_flate'])
    return dict(namn=namn, W350=a['W'] * f, jamnheit=a['U'], bak350=a['E_bak'] * f, skjerm350=a['E_skjerm'] * f,
                auge350=L(a) * f, s_bak=s['E_bak'], s_skjerm=s['E_skjerm'], s_auge=L(s), likskap=ls.likskap(s['_fordeling'], a['_fordeling']))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    ut = os.path.join(HER, 'b_sok.jsonl')
    ferdig = {json.loads(l)['namn'] for l in open(ut, encoding='utf-8')} if os.path.exists(ut) else set()
    for zc, flik, spr, vz in itertools.product((0.62, 0.70), (0.0, 0.06, 0.08, 0.10), (12, 14), (0.45, 0.60)):
        if flik == 0 and vz == 0.45: continue
        namn = f'z{zc:.2f} flik{flik:.2f} ark{spr} vegg{vz:.2f}'
        if namn in ferdig: continue
        r = rad(namn, b_ny(zc, flik, spr, b(0.0, YV, vz)))
        with open(ut, 'a', encoding='utf-8') as fh: fh.write(json.dumps(r, ensure_ascii=False) + '\n')
        print('%-30s W350 %.2f U %.2f bak %3.0f skjerm %3.0f auge %5.0f | stemning bak %3.0f skjerm %3.0f auge %4.0f | lik %.2f'
              % (namn, r['W350'], r['jamnheit'], r['bak350'], r['skjerm350'], r['auge350'], r['s_bak'], r['s_skjerm'], r['s_auge'], r['likskap']), flush=True)
