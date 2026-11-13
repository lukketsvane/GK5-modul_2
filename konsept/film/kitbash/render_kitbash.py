# -*- coding: utf-8 -*-
"""
render_kitbash.py  ·  rendrar lampene i scener.json med byggjesettet sitt eige Blender-oppsett

Brukar modell/byggjesett/rendre_blender.py uendra: same Cycles-innstillingar, same lys, same ortografiske delbank
(4 pikslar per mm, gjennomsiktig bakgrunn, asimut -35 og elevasjon 28). Det einaste som kjem til, er tre materiale.

  blender.exe -b -P render_kitbash.py -- [k1 k2 ...] [--prove]
"""
import bpy, json, os, sys
HER = os.path.dirname(os.path.abspath(__file__))
SETT = os.path.abspath(os.path.join(HER, '..', '..', '..', 'modell', 'byggjesett'))
sys.path.insert(0, SETT)
import rendre_blender as R

R.UT = os.path.join(HER, 'render')
_materiale = R.materiale
def materiale():
    M = _materiale()
    M['trykt'], _ = R._principled('trykt', (0.30, 0.035, 0.04), 0.0, 0.5)             # trykte delar: raudbrune, så dei skil seg frå settet
    m, p = R._principled('led', (1.0, 0.9, 0.7), 0.0, 0.5)
    p.inputs['Emission Color'].default_value = (1.0, 0.72, 0.38, 1.0); p.inputs['Emission Strength'].default_value = 6.0
    M['led'] = m
    return M
R.materiale = materiale

SCENER = json.load(open(os.path.join(HER, 'scener.json'), encoding='utf-8'))
ARG = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
for namn in ([a for a in ARG if not a.startswith('--')] or list(SCENER)):
    R.rendre(namn, SCENER[namn])
