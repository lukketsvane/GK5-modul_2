# -*- coding: utf-8 -*-
"""
c_sok.py  ·  C Vindauge med linser som finst

Linsene:
  lupe 3x Ø 75 mm      vanleg handlupe (Maped, Levenhuk Zeno Handy ZH23, Verk). Brennvidda er ikkje oppgjeven.
                       3x gjev f = 250/(M-1) = 125 mm eller 250/M = 83 mm etter konvensjon. Rekna med 100 og 125 mm.
  vasskule Ø 70 mm     glaskule (julekule) fylt med vatn, n = 1,333: f = nD / (4(n-1)) = 70 mm frå midten.
Kondensoren er ei kredittkort-fresnel (85 x 55 mm, 3x) eller fresnelplata, rekna som TAU_K i familien.

Overgangen er den same som før: frontflatespegelen glir inn og legg delen q på bordet.
Søket: linse, q1 (delen til bordet i arbeid), kantbreidd og overfylling.

  python c_sok.py [delar]      delar = 0/1 for å dele søket på to prosessar
"""
import os, sys, json, itertools
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
import tre
from tre import ls, pro, b, YV, FELT, watt
import numpy as np

LINSER = {
    'lupe100': pro.optikk('lupe 3x Ø 75, f 100 mm', 'kort', 0.100, 0.075, c0=pro.C0_KORT),
    'lupe125': pro.optikk('lupe 3x Ø 75, f 125 mm', 'kort', 0.125, 0.075, c0=pro.C0_KORT),
    'vasskule': pro.optikk('vasskule Ø 70, f 70 mm', 'kule', 0.070, 0.070, p=0.035, c0=0.05),
}

def c_ny(o, q1=0.65, kant=0.06, marg=0.0, mot0=pro.VEGGSOL, grad=0.0, pos=None, fot=None):
    """Som p_dele i familien, men med vald linse, kant og overfylling."""
    def g(t):
        W, K = watt(t); P = pro.HODE if pos is None else np.asarray(pos, float)
        r = float(np.linalg.norm(FELT - P))
        u = pro.u_mjuk(o['f'], o['p'], r, kant)
        # Same oppsett som dele-vindauge i familien: maska er spegla, så strålen via spegelen legg feltet rett på bordet
        form = pro.dreidd(pro.feltmaske_m(u, marg, P), 0, True)
        q = q1 * t
        vb = pro.gradert(grad, u, pos=P) if grad else None                 # gråfilter i maskeplanet, same filter i begge strålane
        vv = pro.gradert(grad, u, pos=P, spegla=True) if grad else None
        lv = pro.stroek(P, mot0, W * (1 - q), K, form, o, u=u, bronn=45, vekt=vv)
        lys = [lv]
        if q > 1e-6:
            lys.append(pro.stroek(P, FELT, W * q, K, pro.dreidd(form, 0, True), o, u=u, spegel=1, bronn=45, vekt=vb))
        return lys, pro.lekam(P, ls.nrm(mot0 - P), lv.info, **({} if fot is None else {'fot': fot}))
    return g

def rad(namn, g):
    s = ls.tal(*g(0.0)); lys, kr = g(1.0); a = ls.tal(lys, kr)
    f = 350.0 / max(a['E_felt'], 1e-9); info = lys[0].info
    La = max(a['L_auge25'], a['L_lampe'], a['L_auge60'], a['L_flate'])
    return dict(namn=namn, W350=a['W'] * f, jamnheit=a['U'], bak350=a['E_bak'] * f, skjerm350=a['E_skjerm'] * f,
                auge350=La * f, s_bak=s['E_bak'], s_auge=max(s['L_auge25'], s['L_lampe'], s['L_auge60'], s['L_flate']),
                likskap=ls.likskap(s['_fordeling'], a['_fordeling']), lmw=info['lmw'], ledd=info['ledd'],
                hovud_mm=(round(info['breidd'] * 1000), round(info['lengd'] * 1000)), maske_mm=round(info['maske'] * 1000), u_mm=round(info['u'] * 1000))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    del_ = int(sys.argv[1]) if len(sys.argv) > 1 else None
    kombi = list(itertools.product(LINSER, (0.60, 0.65), (0.03, 0.06), (0.0, 0.03, 0.05)))
    if del_ is not None: kombi = kombi[del_::2]
    ut = os.path.join(HER, f'c_sok{"" if del_ is None else del_}.jsonl')
    ferdig = set()
    if os.path.exists(ut):
        ferdig = {json.loads(l)['namn'] for l in open(ut, encoding='utf-8')}
    for ln, q1, kant, marg in kombi:
        namn = f'{ln} q{q1:.2f} kant{kant:.2f} marg{marg:.2f}'
        if namn in ferdig: continue
        r = rad(namn, c_ny(LINSER[ln], q1, kant, marg))
        with open(ut, 'a', encoding='utf-8') as fh: fh.write(json.dumps(r, ensure_ascii=False) + '\n')
        print('%-36s W350 %.2f U %.2f bak %3.0f skjerm %3.0f auge %4.0f | stemning bak %3.0f auge %3.0f | lik %.2f | %.0f lm/W hovud %s maske %d u %d'
              % (namn, r['W350'], r['jamnheit'], r['bak350'], r['skjerm350'], r['auge350'], r['s_bak'], r['s_auge'], r['likskap'], r['lmw'], r['hovud_mm'], r['maske_mm'], r['u_mm']), flush=True)
