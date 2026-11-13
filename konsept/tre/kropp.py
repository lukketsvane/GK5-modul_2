# -*- coding: utf-8 -*-
"""
kropp.py  ·  masse, velt, fotavtrykk og kjøling for A, B og C (T2, F8, F9)

Overslag for produktet, ikkje skissemodellen. Delane og materiala står i DELAR. Lysrekninga er ikkje med.
Velt: vinkelen lampa kan vippast før tyngdepunktet går over kanten av foten, og krafta i handlinga
(vipp eller skyv) som veltar ho. Kjøling: A = 0,7 P / (h ΔT) med h = 10 W/m²K og ΔT = 15 K.

  python kropp.py
"""
import os, sys, math, json
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HER, '..', 'lysskisse'))
os.environ.setdefault('LYSSKISSE_POLGE', '0')
import studie

ALU, STAAL, PMMA, GLAS = 2700.0, 7850.0, 1190.0, 2500.0
def stong(d, L, rho=ALU, vegg=None):
    A = math.pi * (d / 2) ** 2 if vegg is None else math.pi * ((d / 2) ** 2 - (d / 2 - vegg) ** 2)
    return A * L * rho
def skive(d, t, rho=ALU): return math.pi * (d / 2) ** 2 * t * rho
def plate(a, b, t, rho): return a * b * t * rho

TAL = json.load(open(os.path.join(HER, 'tal-A.json'), encoding='utf-8')), json.load(open(os.path.join(HER, 'tal-B.json'), encoding='utf-8')), json.load(open(os.path.join(HER, 'tal-C.json'), encoding='utf-8'))
W = {'A': TAL[0]['W350'], 'B': TAL[1]['W350'], 'C': TAL[2]['W350']}
FOTMASSE = (0.5, 0.8, 1.1)          # ballast å prøve i foten, kg

def A(ballast):
    fx, fy = 0.47, 0.38                                   # foten (F2 i familien)
    d = [(0.16 + 0.14 + 0.07, (fx, fy, 0.025)),          # skal, lok, celle, elektronikk og lysdiodar (Vend-frøet)
         (ballast, (fx, fy, 0.010)),
         (stong(0.008, 0.36), (fx, fy + 0.055, 0.23)),
         (skive(0.25, 0.0015), (0.471, 0.300, 0.411)),
         (plate(0.12, 0.084, 0.0015, ALU) + 0.010, (0.435, 0.425, 0.300))]
    return d, studie.sirkel(fx, fy, 0.060), 0.41, 'vipp skiva: 5 N på kanten av skiva'

def B(ballast):
    sx, sy = 0.31, 0.49                                   # stolpen bak skjermen ved høgre kant
    d = [(0.12 + 0.07, (sx, sy, 0.012)),                  # fot, celle og elektronikk
         (ballast, (sx, sy, 0.006)),
         (stong(0.012, 0.62, vegg=0.0015), (sx, sy, 0.31)),
         (stong(0.010, 0.31, vegg=0.0015), (0.155, 0.495, 0.62)),
         (plate(0.285, 0.2025, 0.002, PMMA) + 0.080, (0.0, 0.40, 0.62)),   # fresnelplata og ramma
         (0.030, (0.0, 0.409, 0.51))]                     # kjeldehuset på skjermkanten
    return d, studie.sirkel(sx, sy, 0.070), 0.62, 'vipp plata: 5 N på framkanten'

def C(ballast):
    fx, fy = 0.40, 0.50
    d = [(0.12 + 0.07, (fx, fy, 0.012)),
         (ballast, (fx, fy, 0.006)),
         (stong(0.010, 0.66), (fx, fy, 0.35)),
         (0.10 + 0.06 + 0.06 + 0.03, (0.40, 0.42, 0.70))]  # hovud: skal, linse (PMMA), lysmodul med kjøling, spegelslede
    return d, studie.sirkel(fx, fy, 0.075), 0.70, 'skyv spegelen: 5 N vassrett i hovudet'

def rad(k, f, ballast):
    d, kontakt, h, grep = f(ballast)
    r = studie.kroppstal(d, kontakt, W=W[k], grep=(h, 5.0))
    r['grep'] = grep; r['ballast'] = ballast
    return r

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    L = ['| Konsept | Ballast i foten, kg | Masse, kg | Tyngdepunkt, cm | Veltevinkel | Kraft som veltar, N (handlinga 5 N) | Fotavtrykk, cm² | Kjøleflate som trengst, cm² |',
         '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for k, f in (('A', A), ('B', B), ('C', C)):
        for bl in FOTMASSE:
            r = rad(k, f, bl)
            L.append(f"| {k} | {bl:.1f} | {r['masse']:.2f} | {r['tp_hogd'] * 100:.0f} | {r['velt']:.0f}° | {r['F_velt']:.1f} | {r['fot']:.0f} | {r['kjol_krav'] * W[k] / r['W']:.0f} |")
    tab = '\n'.join(L)
    print(tab)
    open(os.path.join(HER, 'kropp.md'), 'w', encoding='utf-8').write(tab + '\n')
