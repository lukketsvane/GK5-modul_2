# -*- coding: utf-8 -*-
"""Motbevisar 1 for PR14 (ansiktslys ved 150 lx). Les berre konsept.json; ingen import av felles/motor.
L = E / face (felles.py lys(): face = illum per cd/m2, uavhengig av fluks) -> luminansen er lineær i E.
Kamerasjekk: vinkel frå ein webkamera i overkant av skjermen til hovudet i (c) (form04/motor.py FINAL ys 0,22, zs 0,70)."""
import os, json, math
HER = os.path.dirname(os.path.abspath(__file__))
kj = json.load(open(os.path.join(HER, '..', 'konsept.json'), encoding='utf-8'))
L_MAX = 3000.0
out = {}
for k in 'abc':
    L150 = kj[k]['L_ansikt']
    out[k] = {f'{E} lx': round(L150 * E / 150) for E in (50, 100, 150, 200)}
    out[k]['E_maks_3000'] = round(L_MAX / L150 * 150, 1)
# topp for (c) frå prisme.md tabell 3 (4° matt, topp 1 mm, ansikt alfa +70°): 3130 til 3960 ved 150 lx
for lab, Lt in (('c_topp_lag', 3130.0), ('c_topp_hog', 3960.0), ('c_topp_sigma6', 2610.0)):
    out[lab] = {f'{E} lx': round(Lt * E / 150) for E in (50, 100)}
    out[lab]['E_maks_3000'] = round(L_MAX / Lt * 150, 1)
# webkamera i overkant av skjermen (x 0, y 0,45, z 0,42), siktar mot auga (0, -0,30, 0,45)
cam, eye, head = (0.45, 0.42), (-0.30, 0.45), (0.22, 0.70)
akse = math.degrees(math.atan2(eye[1] - cam[1], -(eye[0] - cam[0])))
hov = math.degrees(math.atan2(head[1] - cam[1], -(head[0] - cam[0])))
out['kamera'] = dict(akse_grad=round(akse, 1), hovud_c_grad=round(hov, 1), utanfor_akse_grad=round(hov - akse, 1))
print(json.dumps(out, ensure_ascii=False, indent=1))
