# -*- coding: utf-8 -*-
"""
a_sok.py  ·  A Skiva: veggflik og blending med breiare lobe

1. Veggen bak skjermen i arbeid (F6). Ein andre diode i foten lyser på ein liten, fast flik på stamma.
   Fliken sender lyset forbi skjermkanten til veggen bak skjermen. Delen q av watten går dit, i begge modusar.
2. Blending om lobebreidda er feil. Skiva er rekna med blank folie (sigma 2,5°). Folie på papp ligg truleg på 4 til 6°.
   Prøv sigma 2,5, 4 og 6, og sjå kva auget 25, 47 og 60 cm over bordet ser.

  python a_sok.py flik     søk i fliken
  python a_sok.py lobe     lobebreidda
"""
import os, sys, json, itertools
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
import tre
from tre import ls, boy, b, YV, FELT, watt
import numpy as np

VEGGMAL = b(0.0, YV, 0.45)

def a_ny(q=0.35, fh=0.28, fw=0.14, fl=0.10, side2=None, spr2=8, sigma=2.5, flik=True):
    side = dict(rd=0.03, rs=0.85, sigma=sigma)
    side2 = ls.SATIN if side2 is None else side2
    def g(t):
        Wt, K = watt(t)
        Wm = Wt * (1 - q) if flik else Wt
        lys, kropp = boy.lampe(t, form=boy.boy(-1 / 1.2), side=side, n=30, fot=boy.F2, c=boy.CF,
                               mot=boy.vipp(t, til=boy.SIKT), ref=boy.SIKT, W=Wm)
        if flik:
            kp2 = b(boy.F2[0], boy.F2[1] + 0.02, 0.05)
            c2 = b(boy.F2[0], boy.F2[1] + 0.045, fh)          # fliken sit på stamma, bak strålen til skiva
            n2 = ls.nrm(ls.nrm(kp2 - c2) + ls.nrm(VEGGMAL - c2))
            k2 = ls.straale(kp2, c2, Wt * q * ls.LMW_KJELDE, K, spreiing=spr2, kutt=2 * spr2, opning=0.02, bronn=40)
            a2 = ls.ark(k2, c2, n2, (fw, fl), framside=side2, n=14, opp=np.array([0.0, 0.0, 1.0]))
            lys = lys + [k2, a2]
        return lys, kropp
    return tre._med_kantskive(g)

def rad(namn, g):
    s = ls.tal(*g(0.0)); a = ls.tal(*g(1.0))
    f = 350.0 / max(a['E_felt'], 1e-9)
    return dict(namn=namn, W350=a['W'] * f, jamnheit=a['U'], bak350=a['E_bak'] * f, skjerm350=a['E_skjerm'] * f,
                a25=max(a['L_auge25'], a['L_flate']) * f, a47=max(a['L_lampe'], a['L_flate']) * f, a60=max(a['L_auge60'], a['L_flate']) * f,
                s_bak=s['E_bak'], s_skjerm=s['E_skjerm'], s_auge=max(s['L_auge25'], s['L_lampe'], s['L_auge60'], s['L_flate']),
                likskap=ls.likskap(s['_fordeling'], a['_fordeling']))

def skriv(r, fil):
    with open(fil, 'a', encoding='utf-8') as fh: fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('%-36s W350 %.2f U %.2f bak %3.0f skjerm %3.0f auge 25/47/60 %5.0f %4.0f %4.0f | stemning bak %3.0f skjerm %3.0f auge %4.0f | lik %.2f'
          % (r['namn'], r['W350'], r['jamnheit'], r['bak350'], r['skjerm350'], r['a25'], r['a47'], r['a60'], r['s_bak'], r['s_skjerm'], r['s_auge'], r['likskap']), flush=True)

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    kva = sys.argv[1] if len(sys.argv) > 1 else 'flik'
    fil = os.path.join(HER, f'a_sok_{kva}.jsonl')
    ferdig = {json.loads(l)['namn'] for l in open(fil, encoding='utf-8')} if os.path.exists(fil) else set()
    if kva == 'lobe':
        for sigma in (2.5, 4.0, 6.0):
            namn = f'utan flik, sigma {sigma}'
            if namn not in ferdig: skriv(rad(namn, a_ny(sigma=sigma, flik=False)), fil)
    else:
        for q, fh, fw, s2 in itertools.product((0.30, 0.40), (0.22, 0.30), (0.12, 0.16), ('satin', 'matt')):
            namn = f'q{q:.2f} hogd{fh:.2f} breidd{fw:.2f} {s2}'
            if namn in ferdig: continue
            skriv(rad(namn, a_ny(q, fh, fw, fw * 0.7, ls.SATIN if s2 == 'satin' else ls.MATT)), fil)
