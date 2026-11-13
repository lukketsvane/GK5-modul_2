# -*- coding: utf-8 -*-
"""
f10.py  ·  ansiktslys i møte (F10: 50 til 200 lx på ansiktet) utan å bryte blendingskrava

Ansiktslyset er E = L · Ω: luminansen i flata ansiktet ser, gonger romvinkelen ho dekkjer.
50 lx under 1500 cd/m² krev Ω over 0,033 sr, altså om lag 120 cm² sett frå 60 cm.
Kvart konsept får ein møtemodus med det det har:
  A  skiva vend med ei matt, kvit bakside mot ansiktet (Vend-frøet)
  B  plata vippa så speglinga går mot ansiktet, diffusorark 14° (fresnelfamilien: kryss-mote)
  C  ingen flate mot ansiktet: lyset kjem frå veggen. Rekna med alt lyset på veggen (q = 0)
For kvart: lux på ansiktet og lysaste flate mot auget (25, 47 og 60 cm) per watt. Begge er lineære i watten,
så forholdet avgjer om 50 lx går under 1500 cd/m² (F5) og 3000 cd/m² (F1).

  python f10.py
"""
import os, sys, json
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
import tre
from tre import ls, boy, fre, pro, b, YV, FELT, watt
import numpy as np

AUGE = ls.AUGE

def a_mote(t=1.0, W=1.0, side=ls.MATT, sikt=None, spreiing=10):
    sikt = AUGE if sikt is None else sikt
    lys, kropp = boy.lampe(t, form=boy.boy(-1 / 1.2), side=side, n=30, fot=boy.F2, c=boy.CF, mot=sikt, ref=boy.SIKT, W=W, spreiing=spreiing)
    return lys, kropp

def b_mote(t=1.0, W=1.0, spr=14, sikt=None):
    import b_sok
    sikt = AUGE if sikt is None else sikt
    c = np.array([fre.OVER_C[0], fre.OVER_C[1], ls.ZB + 0.62]); d = b_sok.KP - c; s = float(np.linalg.norm(d)); a = d / s
    lys, kropp = fre.plate(t, c, a, s, sikt, spreiing=spr, kjelde=b_sok.BRONN50, lmdel=W / watt(t)[0])
    return lys, kropp

def c_mote(t=1.0, W=1.0):
    import c_sok
    g = c_sok.c_ny(c_sok.LINSER['vasskule'], 0.0, 0.06, 0.0, grad=1.5, pos=b(0.40, 0.42, 0.70), fot=(0.40, 0.50))
    lys, kropp = g(t)                    # q = 0: alt lyset blir vindauge på veggen
    return lys, kropp

def maal(lys, kropp, W):
    d = ls.tal(lys, kropp)
    L = max(d['L_auge25'], d['L_lampe'], d['L_auge60'], d['L_flate'])
    return dict(E=d['E_ansikt'] / W, L=L / W, L25=d['L_auge25'] / W, L47=d['L_lampe'] / W, L60=d['L_auge60'] / W, skjerm=d['E_skjerm'] / W)

def rad(namn, m):
    W50 = 50.0 / max(m['E'], 1e-9)
    L50 = m['L'] * W50
    return dict(namn=namn, lx_per_W=m['E'], W_for_50=W50, L_ved_50=L50, L25=m['L25'] * W50, L47=m['L47'] * W50, L60=m['L60'] * W50,
                skjerm_ved_50=m['skjerm'] * W50, Omega=m['E'] / max(m['L'], 1e-9),
                held=bool(W50 <= 7.5 and L50 <= 1500), held_F1=bool(W50 <= 7.5 and L50 <= 3000))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    rader = []
    for namn, f in [('A matt bakside mot auget', lambda: a_mote(W=1.0)),
                    ('A matt bakside mot auget, kjelde 14°', lambda: a_mote(W=1.0, spreiing=14)),
                    ('A matt bakside mot auget, kjelde 18°', lambda: a_mote(W=1.0, spreiing=18)),
                    ('A matt, sikta 10 cm under auget', lambda: a_mote(W=1.0, sikt=AUGE - np.array([0, 0, 0.10]))),
                    ('A satin mot auget', lambda: a_mote(W=1.0, side=ls.SATIN)),
                    ('B plata mot auget, ark 14°', lambda: b_mote(W=1.0)),
                    ('B plata mot auget, ark 20°', lambda: b_mote(W=1.0, spr=20)),
                    ('B plata mot haka, ark 14°', lambda: b_mote(W=1.0, sikt=AUGE - np.array([0, 0, 0.12]))),
                    ('C alt lyset på veggen', lambda: c_mote(W=1.0))]:
        lys, kropp = f()
        W = 1.0 if not namn.startswith('C') else watt(1.0)[0]
        r = rad(namn, maal(lys, kropp, W)); rader.append(r)
        print('%-34s %5.1f lx/W  W for 50 lx %5.2f  lysaste flate %6.0f cd/m² (25/47/60: %6.0f %6.0f %6.0f)  skjerm %4.0f lx  Ω %.3f sr  F5 %s  F1 %s'
              % (namn, r['lx_per_W'], r['W_for_50'], r['L_ved_50'], r['L25'], r['L47'], r['L60'], r['skjerm_ved_50'], r['Omega'],
                 'held' if r['held'] else 'nei', 'held' if r['held_F1'] else 'nei'), flush=True)
    json.dump(rader, open(os.path.join(HER, 'f10.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
