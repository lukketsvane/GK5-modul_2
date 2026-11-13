# -*- coding: utf-8 -*-
"""Avgjerdssøk etter generasjon 3 (ikkje ein ny generasjon). Eitt ope spørsmål avgjer den tredje plassen:
kan veggstrøket i arbeid (knekt plate med flik mot veggen) kome utan å halvere feltet, om plata sit over skjermkanten
i staden for på stonga? Same fem steg langs overgangen og same tal som sok() i familie.py. Skriv avgjerd.csv og avgjerd.md.
Køyr: python avgjerd.py"""
from familie import *
import familie as _f

def knekk2(t, c, a, s, vegg, felt, spreiing=12, kjelde=SMAL, flytt=0.03, flik=0.10, fot=None, stong=None):
    """Same knekk som i familie.py, men for kva plass og kjelderetning som helst.
    Plata er delt langs ein diameter og knekt. Den store delen lyser på feltet, fliken på veggen. Heile plata vippar."""
    W, K = watt(t)
    c = np.asarray(c, float); a = nrm(a); kp = c + s * a
    nf = nrm(a + nrm(felt - c)); nw = nrm(a + nrm(vegg - c))
    r = nrm(np.cross(nf, nw)); phi = math.acos(float(np.clip(nf @ nw, -1, 1)))
    n1 = rot(nf, r, phi * (1 - t)); n2 = rot(nw, r, phi * (1 - t))
    e1 = np.cross(n1, r); e2 = np.cross(n2, r)
    sk, kutt, bronn = kjelde
    k = straale(kp, c + flytt * e1, W * LMW_KJELDE, K, spreiing=sk, kutt=kutt, opning=0.02, bronn=bronn)
    a1 = fresnelspegel(k, c, n1, spreiing=spreiing, n=_f.N, opp=e1, klipp=lambda u, v: v >= 0)
    a2 = fresnelspegel(k, c, n2, spreiing=spreiing, n=_f.N, opp=e2, klipp=lambda u, v: (v < 0) & (v > -flik))
    k.lm_ut = max(k.lm - a1.lm_inn - a2.lm_inn, 0.0)      # rettar motorfeil 2 (lm_ut blir skriven over)
    kropp = []
    if fot is not None: kropp.append(syl(b(fot[0], fot[1], 0), b(fot[0], fot[1], 0.04), 0.06))
    if stong is not None: kropp += STONG(stong)
    return [k, a1, a2], kropp

VEGG_OVER = b(0.0, YV, 0.60)

AVGJERD = [
    ('kryss-knekk',      'referanse frå generasjon 3: stong, kjelda i foten, flik 100 mm',
        lambda t: knekk(t)),
    ('kryss-knekk-ark10','same, ark 10 grader: meir på feltet?',
        lambda t: knekk(t, spreiing=10)),
    ('kryss-knekk-flik6','same, flik 60 mm: mindre til veggen',
        lambda t: knekk(t, flik=0.06)),
    # Første køyring hadde flytt=0,03 også over skjermen. Då siktar kjelda 14 grader skeivt, auget kjem innanfor brønnen
    # og ser den nakne dioden: 35 000 til 139 000 cd/m². Kjelda på skjermkanten har berre 7 grader å gå på. Difor flytt=0 her.
    ('over-knekk',       'plata over skjermkanten, kjelda på skjermkanten, knekt med flik 100 mm mot veggen over skjermen',
        lambda t: knekk2(t, OVER_C, OVER_A, 0.12, VEGG_OVER, FELT, kjelde=VID, flytt=0.0)),
    ('over-knekk-flik6', 'same, flik 60 mm',
        lambda t: knekk2(t, OVER_C, OVER_A, 0.12, VEGG_OVER, FELT, kjelde=VID, flik=0.06, flytt=0.0)),
    ('over-knekk-bak',   'same, fliken sender lyset ned bak skjermen (vegg 30 cm over bordet)',
        lambda t: knekk2(t, OVER_C, OVER_A, 0.12, b(0.0, YV, 0.30), FELT, kjelde=VID, flytt=0.0)),
]

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    sok(AVGJERD, 'avgjerd')
