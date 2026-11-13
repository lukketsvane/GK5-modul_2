# -*- coding: utf-8 -*-
"""Hentar geometrien for runde 2 av dei tre konsepta frå modellkoden i konsept/tre, til byggjepakken.
Køyr han på nytt når konsepta endrar seg: python hent_geometri.py
Skriv leveransar/05_byggjepakke/runde2.json og maske_C.npz (maskepolygon og gråfilter i maskeplanet)."""
import os, sys, json, math
import numpy as np

REPO = 'C:/Users/Iver/Documents/github/GK5-modul_2'
sys.path.insert(0, REPO + '/konsept/tre')
os.chdir(REPO + '/konsept/tre')
import tre
import a_sok, b_sok, c_sok
from tre import ls, pro, b, YV, FELT

def nrm(v): v = np.asarray(v, float); return v / np.linalg.norm(v)
def tilt(n): return math.degrees(math.acos(min(1.0, abs(n[2]))))     # vinkel mellom flata og vassrett

ZB = ls.ZB
ut = {}

# ---------------- A: fliken (a_ny(q=0.40, fh=0.30, fw=0.12, fl=0.084, SATIN)), kjelda 2 og hovudlykta
F2 = tre.boy.F2
kp2 = b(F2[0], F2[1] + 0.02, 0.05); c2 = b(F2[0], F2[1] + 0.045, 0.30); VEGGMAL = b(0.0, YV, 0.45)
n2 = nrm(nrm(kp2 - c2) + nrm(VEGGMAL - c2))
ut['A'] = dict(flik_senter_cm=[round(float(c2[0]) * 100, 1), round(float(c2[1]) * 100, 1), round(float(c2[2] - ZB) * 100, 1)],
               flik_mm=[120, 84], flik_tilt_grader=round(tilt(n2), 1),
               flik_normal=[round(float(x), 3) for x in n2],
               lykt2_cm=[round(float(kp2[0]) * 100, 1), round(float(kp2[1]) * 100, 1), round(float(kp2[2] - ZB) * 100, 1)],
               lykt2_sigma=8, lykt2_kutt=16, lykt2_til_flik_cm=round(float(np.linalg.norm(c2 - kp2)) * 100, 1),
               lykt2_vinkel_fram_frå_loddrett=round(math.degrees(math.atan2(float(c2[1] - kp2[1]), float(c2[2] - kp2[2]))), 1),
               q=0.40)
kp1 = b(F2[0], F2[1], 0.05); c1 = b(*tre.boy.CF)
ut['A']['hovudlykt_vinkel_fram_frå_loddrett'] = round(math.degrees(math.atan2(float(kp1[1] - c1[1]), float(c1[2] - kp1[2]))), 1)
ut['A']['hovudlykt_til_skive_cm'] = round(float(np.linalg.norm(c1 - kp1)) * 100, 1)

# ---------------- B: b_ny(zc=0.62, flik=0.06, spr=14, vegg=b(0, YV, 0.60))
c = np.array([tre.fre.OVER_C[0], tre.fre.OVER_C[1], ZB + 0.62]); KP = b_sok.KP
d = KP - c; s = float(np.linalg.norm(d)); a = d / s
vegg = b(0.0, YV, 0.60)
nf = nrm(a + nrm(FELT - c)); nw = nrm(a + nrm(vegg - c)); phi = math.degrees(math.acos(float(np.clip(nf @ nw, -1, 1))))
r = nrm(np.cross(nf, nw))
e1_arbeid = np.cross(nf, r)
ut['B'] = dict(plate_senter_cm=[round(float(c[0]) * 100, 1), round(float(c[1]) * 100, 1), round(float(c[2] - ZB) * 100, 1)],
               lykt_cm=[round(float(KP[0]) * 100, 1), round(float(KP[1]) * 100, 1), round(float(KP[2] - ZB) * 100, 1)],
               lykt_avstand_cm=round(s * 100, 1),
               knekk_grader=round(phi, 1), dreieakse=[round(float(x), 3) for x in r],
               hovuddel_tilt_arbeid=round(tilt(nf), 1), flik_tilt_arbeid=round(tilt(nw), 1), heile_tilt_stemning=round(tilt(nw), 1),
               hovuddel_normal_arbeid=[round(float(x), 3) for x in nf], flik_normal=[round(float(x), 3) for x in nw],
               v_positiv_peikar=[round(float(x), 3) for x in e1_arbeid],
               flik_mm=60, maskert_mm=round(142.5 - 60, 1), diffusor_sigma=14)

# ---------------- C: c_ny(vasskule, 0.65, 0.06, 0.0, grad=1.5, pos=b(0.40, 0.42, 0.70), fot=(0.40, 0.50))
o = c_sok.LINSER['vasskule']; P = b(0.40, 0.42, 0.70)
rr = float(np.linalg.norm(FELT - P)); u = pro.u_mjuk(o['f'], o['p'], rr, 0.06)
hj = [b(-0.3, 0.05, 0), b(0.3, 0.05, 0), b(0.3, 0.45, 0), b(-0.3, 0.45, 0)]
poly = pro.tilbake(P, FELT, hj, u)                        # hjørna i maskeplanet: framkant v, framkant h, bakkant h, bakkant v
dw, df = pro.VEGGSOL - P, FELT - P
ut['C'] = dict(hovud_cm=[round(float(P[0]) * 100, 1), round(float(P[1]) * 100, 1), round(float(P[2] - ZB) * 100, 1)],
               fot_cm=[40.0, 50.0], f_mm=70, u_mm=round(u * 1000, 1), u_skarp_mm=round(pro.u_for(0.070, rr) * 1000, 1),
               til_felt_cm=round(rr * 100, 1), til_vegg_cm=round(float(np.linalg.norm(dw)) * 100, 1),
               avboying_grader=round(math.degrees(math.acos(float(nrm(dw) @ nrm(df)))), 1), q_bord=0.65, grad=1.5,
               maske_hjorne_mm=[[round(x * 1000, 2), round(y * 1000, 2)] for x, y in poly],
               hjorne_namn=['framkant venstre', 'framkant høgre', 'bakkant høgre', 'bakkant venstre'])
# gråfilteret i maskeplanet (same ramme som hjørna over, utan spegling)
v = pro.gradert(1.5, u, pos=P)
xs = np.array([p[0] for p in poly]); ys = np.array([p[1] for p in poly])
mx = 0.006
X, Y = np.meshgrid(np.linspace(xs.min() - mx, xs.max() + mx, 220), np.linspace(ys.min() - mx, ys.max() + mx, 160))
Wt = v(X, Y)
np.savez(REPO + '/leveransar/05_byggjepakke/maske_C.npz', X=X, Y=Y, W=Wt, poly=np.array(poly))
ut['C']['filter_min'] = round(float(Wt.min()), 3); ut['C']['filter_max'] = round(float(Wt.max()), 3)
json.dump(ut, open(REPO + '/leveransar/05_byggjepakke/runde2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(ut, ensure_ascii=False, indent=1))
