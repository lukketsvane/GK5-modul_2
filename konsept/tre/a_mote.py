# -*- coding: utf-8 -*-
"""
a_mote.py  ·  A Skiva med møtemodus: skiva blir vend, så den matte, kvite baksida lyser mot ansiktet

Tre tilstandar: stemning (spegel mot veggen), arbeid (spegel mot feltet), møte (matt bakside mot ansiktet).
Vendinga går frå arbeid til møte: skiva roterer om ein vassrett akse gjennom senteret. Undervegs kan spegelsida
sende strålen mot auget, så luminansen mot auget i 25, 47 og 60 cm blir rekna steg for steg.

  python a_mote.py tal      vendinga i 9 steg, til a_mote.md
  python a_mote.py bilete   stemning, arbeid og møte side om side, til ark-A-mote.png
"""
import os, sys, math, json
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
import tre
from tre import ls, boy, b, FELT, watt
import numpy as np

AUGE = ls.AUGE
KP = b(boy.F2[0], boy.F2[1], 0.05)
C = b(*boy.CF)
SPEGEL = dict(rd=0.03, rs=0.85, sigma=2.5)
W_MOTE = 3.9                      # 50 lx på ansiktet (f10.md)

def _rot(v, akse, vinkel):
    akse = ls.nrm(akse); c, s = math.cos(vinkel), math.sin(vinkel)
    return v * c + np.cross(akse, v) * s + akse * (akse @ v) * (1 - c)

def normalar():
    s = ls.nrm(KP - C)
    n_arbeid = ls.nrm(s + ls.nrm(boy.SIKT - C))           # spegelsida mot feltet
    n_mote = ls.nrm(s + ls.nrm(AUGE - C))                  # baksida mot auget: framsida peikar motsett veg
    return n_arbeid, -n_mote

def vend(u, andre_vegen=False):
    """u = 0 er arbeid, u = 1 er møte. Spegelsida roterer frå n_arbeid til -n_mote om ein akse gjennom senteret.
    andre_vegen: rotér den lange vegen rundt (360° minus vinkelen). Skiva blir bygd med boy.lampe, som A,
    så u = 0 er den same skiva som i arbeid. Når baksida vender mot kjelda, blir sidene bytte i modellen."""
    na, nm = normalar()
    akse = ls.nrm(np.cross(na, nm)); fi = math.acos(float(np.clip(na @ nm, -1, 1)))
    if andre_vegen: akse, fi = -akse, 2 * math.pi - fi
    n = _rot(na, akse, fi * u)
    W = 5.0 + (W_MOTE - 5.0) * u
    spr = 10 + 8 * u
    s = ls.nrm(KP - C)
    if n @ s >= 0:
        r = 2 * (n @ s) * n - s; form, side, bak = boy.boy(-1 / 1.2), SPEGEL, ls.MATT
    else:
        m = -n; r = 2 * (m @ s) * m - s; form, side, bak = boy.boy(1 / 1.2), ls.MATT, SPEGEL
    g = tre._med_kantskive(lambda t: boy.lampe(1.0, form=form, side=side, bak=bak, n=30, fot=boy.F2, c=boy.CF,
                                                 mot=C + r, ref=boy.SIKT, W=W, spreiing=spr))
    return g(1.0)

def tre_tilstandar(t):
    """t = 0 stemning, 0,5 arbeid, 1 møte (for bilete)."""
    if t < 0.75: return tre._A(min(t * 2, 1.0))
    return vend(1.0)

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    if sys.argv[1:2] == ['bilete']:
        ls.par(tre_tilstandar, os.path.join(HER, 'ark-A-mote.png'), px=480, ss=1, steg=(0.0, 0.5, 1.0))
        print('ark-A-mote.png')
    else:
        L = ['| Steg | Vending | W | Ansikt, lx | Mot auget 25 / 47 / 60 cm, cd/m² | Felt, lx | Skjermflata, lx |', '| --- | --- | --- | --- | --- | --- | --- |']
        rader = []
        veg = len(sys.argv) > 2 and sys.argv[2] == 'andre'
        for i, u in enumerate(np.linspace(0, 1, 9)):
            d = ls.tal(*vend(float(u), veg))
            na, nm = normalar(); fi = (360 - math.degrees(math.acos(float(np.clip(na @ nm, -1, 1)))) if veg else math.degrees(math.acos(float(np.clip(na @ nm, -1, 1))))) * u
            r = dict(u=float(u), vinkel=fi, W=5.0 + (W_MOTE - 5.0) * u, ansikt=d['E_ansikt'], L25=max(d['L_auge25'], d['L_flate']),
                     L47=max(d['L_lampe'], d['L_flate']), L60=max(d['L_auge60'], d['L_flate']), felt=d['E_felt'], skjerm=d['E_skjerm'])
            rader.append(r)
            L.append(f"| {i} | {r['vinkel']:.0f}° | {r['W']:.1f} | {r['ansikt']:.0f} | {r['L25']:.0f} / {r['L47']:.0f} / {r['L60']:.0f} | {r['felt']:.0f} | {r['skjerm']:.0f} |")
            print(L[-1], flush=True)
        namn = 'a_mote_andre' if veg else 'a_mote'
        open(os.path.join(HER, namn + '.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
        json.dump(rader, open(os.path.join(HER, namn + '.json'), 'w', encoding='utf-8'), indent=1)
