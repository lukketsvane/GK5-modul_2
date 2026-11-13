# -*- coding: utf-8 -*-
"""Gransking, premiss-linsa, tillegg (andre pass 13.11).
Eigen aritmetikk, ingen import av felles.py eller motorane. Datafilene vert berre lesne.
Køyr: PYTHONIOENCODING=utf-8 python premiss_tillegg.py   (under 1 s)
  F10  ansiktslys: konsept.md reknar luminansen ved 150 lx (felles.py l.31 E_FACE). Kravet F10 er 50 til 200 lx.
  GK5  effekt og batteritid med reknetala i GK5-modul_2 (60 til 80 lm/W, 17,8 Wh nominelt, 15,1 Wh brukbart)
  CO2  rett summering av tilfellet «høg straumfaktor, lågkarbon-aluminium» (premiss.md 2.6)
  H    høgd mot Northern-bordlampene (27 til 55 cm, formføringsplansja side 8)
"""
import os, json, csv

HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
kj = json.load(open(os.path.join(ROOT, 'konsept.json'), encoding='utf-8'))
f2 = json.loads(open(os.path.join(ROOT, 'form02', 'tal.json'), encoding='utf-8').read().replace('NaN', 'null').replace('Infinity', 'null'))
f4 = next(csv.DictReader(open(os.path.join(ROOT, 'form04', 'tal.csv'), encoding='utf-8')))
pr = json.load(open(os.path.join(HER, 'premiss.json'), encoding='utf-8'))
OUT = {}

# ---- F10: luminansen som trengst er lineær i ansiktslyset (L150 = Le·E_FACE/face i form04 sok(), same i felles) ----
E_F = 150.0
f10 = {}
for k in 'abc':
    L150 = kj[k]['L_ansikt']
    f10[k] = {f'{E:.0f} lx': round(L150 * E / E_F) for E in (50, 100, 150, 200)}
f10['c_topp_prisme_md'] = {f'{E:.0f} lx': [round(3200 * E / E_F), round(4000 * E / E_F)] for E in (50, 100, 150, 200)}
f10['grense'] = 'felles.py L_MAX 3000 cd/m²; ramma 00: under 1000 til 1500 i arbeid'
OUT['F10'] = f10

# ---- effekt og batteri under GK5-premissar ----
gk = {}
for k in 'abc':
    Phi = kj[k]['Phi_lm']
    r = {}
    for lmw in (100, 80, 60):
        for E, s in ((500, 1.0), (350, 0.7)):
            P = Phi * s / lmw
            r[f'{lmw} lm/W, {E} lx'] = dict(W=round(P, 2), t_19_4Wh=round(0.9 * 21.6 / P, 2), t_16_0Wh=round(0.9 * 17.8 / P, 2), t_15_1Wh=round(15.1 / P, 2))
    gk[k] = r
gk['krav'] = 'B3 skal: 7,5 W på leidning. Ramma: under 1000 lm og 10 W. T5 kan: arbeidslys på batteri minst 1,5 t'
OUT['GK5'] = gk

# ---- CO2: premiss.json C, rett sum ----
C = pr['C']['C'] if 'C' in pr.get('C', {}) else pr['C']
co2 = {}
for k in 'abc':
    c = C[k]
    hi_s_lo_a = c['straum_kgCO2e'][1] + c['alu_kgCO2e'][0] + c['pmma_kgCO2e']
    lo = c['straum_kgCO2e'][0] + c['alu_kgCO2e'][0] + c['pmma_kgCO2e']
    hi = c['straum_kgCO2e'][1] + c['alu_kgCO2e'][1] + c['pmma_kgCO2e']
    co2[k] = dict(hog_straum_lag_alu=round(hi_s_lo_a, 1), lag=round(lo, 1), hog=round(hi, 1))
co2['fot_c_alu_kg'] = round(2700 * 0.24 * 0.30 * 0.007, 3)
OUT['CO2'] = co2

# ---- høgd ----
R = 0.022                                   # form01/motor.py BASE R
H_b = 0.62 + R + 0.015 + 0.0115             # form02/val.py arm_path(): H = hp + R + 0,015, pluss halve Ø23
OUT['H_cm'] = dict(a=round(float(f2['a']['hogd_cm']), 1), b=round(H_b * 100, 1), c=round(float(f4['hogd_cm']), 1),
                   northern_bordlamper='27 til 55 cm (side-8-formfoering-sortiment)', breidd_a_m=1.12)

# ---- R: LED-lina i (c) sett frå auga i arbeid (alfa 0): skjermar rennekanten? form04/motor.py geometri():
#      renneveggar i y = ys ± 0,008 frå z = zs − 0,005 til zs + 0,015; plata (overside) i z = zs − d, y = ys ± bp/2 ----
ys, zs, d, bp = 0.22, 0.70, 0.05, 0.16
yw, zw = ys - 0.008, zs - 0.005
ren = {}
for ez in (0.25, 0.40, 0.45, 0.47, 0.60):
    ey = -0.30
    z_at_wall = ez + (zs - ez) * (yw - ey) / (ys - ey)
    t = (zs - d - ez) / (zs - ez)
    y_at_plate = ey + t * (ys - ey)
    ren[f'auge {ez:.2f} m'] = dict(margin_mm=round((z_at_wall - zw) * 1000, 1), skjerma=bool(z_at_wall >= zw),
                                  gjennom_plata=bool(ys - bp / 2 <= y_at_plate <= ys + bp / 2), y_ved_plata=round(y_at_plate, 3))
OUT['renne_c'] = ren

print(json.dumps(OUT, ensure_ascii=False, indent=1))
json.dump(OUT, open(os.path.join(HER, 'premiss_tillegg.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
