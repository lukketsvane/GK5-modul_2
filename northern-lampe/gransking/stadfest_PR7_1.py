# -*- coding: utf-8 -*-
"""Motbevisar 1 for PR7 (miljøtiltaket i (c)). Eigen aritmetikk frå motorparametrane, ikkje frå premiss.json.
Køyr: PYTHONIOENCODING=utf-8 python stadfest_PR7_1.py  (under 1 s)"""
import math, json, os, csv
HER = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HER)
kj = json.load(open(os.path.join(ROOT, 'konsept.json'), encoding='utf-8'))
f4 = next(csv.DictReader(open(os.path.join(ROOT, 'form04', 'tal.csv'), encoding='utf-8')))
RHO = 2700
# (c): form04/motor.py tal_mek(): fot 0,24x0,30xt_fot, søyle+arm A_col=(COL_W+2COL_F)COL_T, za=zs+0,03, L_arm=COL_Y+COL_F-ys; stong hovud_masse()
t_fot = float(f4['t_fot_mm']) / 1000; zs, ys, L = float(f4['zs']), float(f4['ys']), float(f4['L'])
m_fot = RHO * 0.24 * 0.30 * t_fot
A_col = (0.10 + 2 * 0.03) * 0.002
m_col = RHO * A_col * ((zs + 0.03) + (0.512 + 0.03 - ys))
m_stong = RHO * (0.016 + 0.040) * 0.0015 * L
alu_c = m_fot + m_col + m_stong
pmma_c = float(f4['m_plate_kg'])
masse_c_sjekk = alu_c + pmma_c + 0.10 + 0.15
# (a): form01/motor.py tal(): røyr R 0,022, t 1,2 mm, L 1,12 (rett røyr, Larc = L), k 0,536, beta 25; bein Ø20x1,5; + 0,06 + 0,03 (grep, lokk)
m_ror = RHO * math.pi * 2 * 0.022 * 0.0012 * 1.12 * (1 - 0.536 * 25 / 180)
Aleg = math.pi / 4 * (0.020 ** 2 - 0.017 ** 2)
m_bein = RHO * Aleg * 4 * math.hypot(0.61, 0.15)
alu_a = m_ror + m_bein + 0.06 + 0.03
P = {k: kj[k]['P_W'] for k in 'ac'}
h = 920 * 10
kWh = {k: P[k] * h / 1000 for k in P}
d_kWh = kWh['a'] - kWh['c']
out = dict(alu_a=alu_a, alu_c=alu_c, m_fot=m_fot, pmma_c=pmma_c, masse_c_sjekk=masse_c_sjekk, masse_c_tabell=float(f4['masse_kg']),
           masse_a_tabell=kj['a']['masse_kg'], P=P, d_kWh=d_kWh)
rows = {}
for fs in (0.015, 0.152, 0.30):
    for fa in (2.0, 4.0, 7.0, 16.0):
        a = kWh['a'] * fs + alu_a * fa
        c = kWh['c'] * fs + alu_c * fa + pmma_c * 6.0
        rows[f'straum {fs} alu {fa}'] = dict(a=round(a, 1), c=round(c, 1), c_betre=c < a)
out['rader'] = rows
# break-even
out['alu_breakeven_ved_0152'] = (kWh['a'] * 0.152 - kWh['c'] * 0.152 - pmma_c * 6) / (alu_c - alu_a)
out['straum_breakeven_ved_alu16'] = (alu_c * 16 + pmma_c * 6 - alu_a * 16) / d_kWh
out['straum_breakeven_ved_alu2'] = (alu_c * 2 + pmma_c * 6 - alu_a * 2) / d_kWh
# rettferdig tilskriving: berre optikken (PMMA) mot straumsparinga, 10 og 20 år
out['berre_optikk'] = {f'{fs} kg/kWh, {yr} år': dict(sparing=round(d_kWh * yr / 10 * fs, 2), pmma=round(pmma_c * 6, 2)) for fs in (0.015, 0.152) for yr in (10, 20)}
# stålfot same masse (stabilitet), 1,5 til 2,3 kg CO2e/kg
alu_c_st = alu_c - m_fot
out['staalfot'] = {f'{fs}': dict(a_lag=round(kWh['a'] * fs + alu_a * 2, 1), c_lag=round(kWh['c'] * fs + alu_c_st * 2 + pmma_c * 6 + m_fot * 2.0, 1),
                                 a_hog=round(kWh['a'] * fs + alu_a * 16, 1), c_hog=round(kWh['c'] * fs + alu_c_st * 16 + pmma_c * 6 + m_fot * 2.3, 1)) for fs in (0.015, 0.152)}
print(json.dumps(out, ensure_ascii=False, indent=1, default=float))
