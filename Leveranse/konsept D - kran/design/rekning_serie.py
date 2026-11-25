# -*- coding: utf-8 -*-
"""
rekning_serie.py · konsept D «Kran», linse SERIE: masse, tyngdepunkt, velting og friksjonsledd.

Koordinatar: X vassrett i stativplanet langs armretninga, 0 i leddaksen (+X mot tuppen).
Y vinkelrett på stativplata, 0 i midtplanet, -Y framover (sida armen og knotten sit på).
Z opp frå bordet. Alle mål i mm, masse i g.

  py -3 design/rekning_serie.py          skriv tal til skjermen og design/rekning_serie.json
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

HER = Path(__file__).resolve().parent
G = 9.81
STAL, ALU, PA, PC, PLA = 7.85e-3, 2.70e-3, 1.14e-3, 1.20e-3, 1.24e-3   # g/mm3

# ---------------------------------------------------------------- skala (biletet, sjå forslag_serie.json)
import os, sys
SK = float(os.environ.get('SKALA', '1.0'))   # +-15 % prøve: heile opprisset skalert, platetjukkleik og profilsnitt faste
LEDD_Z = 330.0 * SK       # leddaksen over bordet
ARM_L = 480.0 * SK        # frå leddaksen til tuppen
FOT_X0, FOT_X1 = -135.0 * SK, 36.0 * SK   # botnkanten på stativet (171 mm): målt 177 mm, korta mot 150-anslaget
TOPP_R = 22.8             # avrundinga øvst, konsentrisk med leddet (målt 22,8): fast, ber leddet
SPALTE = ((-97.0 * SK, 43.0 * SK), (3.7, 330.0 * SK - 18.0), 8.0)   # midtlinje og breidd (målt)
T_STATIV = float(os.environ.get('T', '4.0'))            # S235
RI_BOY = T_STATIV         # indre bøyeradius = t
Y_TAN = T_STATIV / 2 + RI_BOY   # framkanten av bøyetangenten: flensen ligg flatt frå Y = -Y_TAN
FLENS_D = float(os.environ.get('FLENS', '115')) * SK    # flat flensdjupn framover, frå tangenten til bøyen
KASSETT = (-50.0, 20.0, 2.0 + 14.0)   # elektronikkassetten bak: X frå, X til, bakkant Y
FLENS_R = 15.0            # hjørneradius framme
FILT_INNSETT = 1.0

# ---------------------------------------------------------------- stativplata (X, Z)
def tangent(p, c, r, side):
    """Tangentpunkt frå p til sirkelen (c, r); side=+1 venstre, -1 høgre sett frå p mot c."""
    dx, dz = c[0] - p[0], c[1] - p[1]
    d = math.hypot(dx, dz)
    a = math.atan2(dz, dx) + side * math.asin(r / d)
    L = math.sqrt(d * d - r * r)
    return (p[0] + L * math.cos(a), p[1] + L * math.sin(a))

C = (0.0, LEDD_Z)
tl = tangent((FOT_X0, 0.0), C, TOPP_R, +1)
tr = tangent((FOT_X1, 0.0), C, TOPP_R, -1)
a0 = math.atan2(tr[1] - C[1], tr[0] - C[0])
a1 = math.atan2(tl[1] - C[1], tl[0] - C[0])
boge = [(C[0] + TOPP_R * math.cos(a0 + (a1 - a0) * i / 40), C[1] + TOPP_R * math.sin(a0 + (a1 - a0) * i / 40))
        for i in range(41)]
plate = Polygon([(FOT_X0, 0.0), (FOT_X1, 0.0)] + boge)
spalte = LineString([SPALTE[0], SPALTE[1]]).buffer(SPALTE[2] / 2, quad_segs=16)
ledd_hol = Point(C).buffer(6.0, quad_segs=32)                 # Ø 12 for glidelageret
stopp = LineString([(C[0] + 13 * math.cos(math.radians(a)), C[1] + 13 * math.sin(math.radians(a)))
                    for a in range(95, 186, 5)]).buffer(1.7)  # bogespalte R 13, 3,4 brei, for stoppepinnen
plate_netto = plate.difference(unary_union([spalte, ledd_hol, stopp]))

# vevane: minste materialbreidd mellom hol og kant
vev_spalte_ledd = spalte.distance(ledd_hol)
vev_spalte_kant = spalte.distance(plate.exterior)
vev_stopp_ledd = stopp.distance(ledd_hol)
vev_stopp_kant = stopp.distance(plate.exterior)
vev_stopp_spalte = stopp.distance(spalte)

# ---------------------------------------------------------------- massepunkt [namn, g, X, Y, Z, roterer]
delar = []
def legg(namn, m, x, y, z, rot=False):
    delar.append(dict(namn=namn, m=m, x=x, y=y, z=z, rot=rot))

A = plate_netto.area
legg('D01 stativplate (vertikal del)', A * T_STATIV * STAL, plate_netto.centroid.x, 0.0, plate_netto.centroid.y)
# bøyen: kvart sirkel, middelradius 6
boy_m = (math.pi / 2) * (RI_BOY + T_STATIV / 2) * T_STATIV * (FOT_X1 - FOT_X0) * STAL
legg('D01 bøyen', boy_m, (FOT_X0 + FOT_X1) / 2, -Y_TAN / 2, Y_TAN / 2)
flens = Polygon([(FOT_X0, -Y_TAN), (FOT_X1, -Y_TAN), (FOT_X1, -Y_TAN - FLENS_D), (FOT_X0, -Y_TAN - FLENS_D)])
flens = flens.buffer(-FLENS_R).buffer(FLENS_R, quad_segs=16).union(
    Polygon([(FOT_X0, -Y_TAN), (FOT_X1, -Y_TAN), (FOT_X1, -Y_TAN - FLENS_R), (FOT_X0, -Y_TAN - FLENS_R)]))
legg('D01 flens framover', flens.area * T_STATIV * STAL, flens.centroid.x, flens.centroid.y, 2.0)
legg('D09 filtpute 1,5 mm', flens.area * 1.5 * 0.35e-3, flens.centroid.x, flens.centroid.y, -0.7)

# armen (horisontal, theta = 0); Y-plassering etter leddstabelen
# stativ framflate Y -2, PA-skive -2..-3, kjerneplate -3..-5, dekkplate -5..-8, knott -8..-12
# profilen: bakflate Y -5 (tunga ligg mot bakflata), djupn 14 -> Y -5..-19, høgd 20,6, senter Z 327,5
PROF_X0, PROF_X1 = 30.0, ARM_L - 6.0
PROF_A = 96.0            # mm2, seriesnittet (sjå forslaget)
legg('D02 armprofil 6063', PROF_A * (PROF_X1 - PROF_X0) * ALU, (PROF_X0 + PROF_X1) / 2, -12.0, LEDD_Z - 2.5, True)
legg('D04 endekork (sink, serie)', 14.0, ARM_L - 4.0, -12.0, LEDD_Z - 2.5, True)
legg('D05 spreiar opal PC', 12.0 * 1.2 * 360 * SK * PC, PROF_X0 + 85 + 180 * SK, -12.0, LEDD_Z - 14.0, True)
legg('E01 COB-stripe 360 mm', 6.0 * SK, PROF_X0 + 85 + 180 * SK, -12.0, LEDD_Z - 12.0, True)
legg('E05 leidning i armen', 2.0, 90.0, -12.0, LEDD_Z, True)
ore_front = Point(C).buffer(23.0).union(Polygon([(0, LEDD_Z - 12.8), (36, LEDD_Z - 12.8), (36, LEDD_Z + 7.8), (0, LEDD_Z + 23.0)]))
ore_kjerne = ore_front.union(Polygon([(30, LEDD_Z - 10.5), (75, LEDD_Z - 10.5), (75, LEDD_Z + 5.5), (30, LEDD_Z + 5.5)]))   # med tunge
legg('D03a dekkplate 2 mm alu', ore_front.area * 2.0 * ALU, ore_front.centroid.x, -6.5, ore_front.centroid.y, True)
legg('D03b kjerneplate 2 mm alu', ore_kjerne.area * 2.0 * ALU, ore_kjerne.centroid.x, -4.0, ore_kjerne.centroid.y, True)
legg('M02 2 popnaglar 3,2', 1.0, 55.0, -8.0, LEDD_Z - 2.5, True)
legg('D06 leddtapp + knott', 7.0, 0.0, -5.0, LEDD_Z, True)
legg('M03-M06 skiver, fjører, mutter bak', 9.0, 0.0, 6.0, LEDD_Z, True)
legg('D08 kapsel bak leddet (PC/ABS)', 5.0, 0.0, 10.0, LEDD_Z)
legg('D07 kabeldeksel bak, alu U 10x8x1', (10 + 8 + 8) * 1.0 * (LEDD_Z - 50) * ALU, 10.0, 7.0, LEDD_Z / 2)
legg('D10 elektronikkassett bak (PC/ABS + PCB + USB-C)', 38.0, -15.0, 12.0, 24.0)
legg('E05 leidningar på baksida', 4.0, 5.0, 6.0, LEDD_Z / 2)

def rot(d, th):
    if not d['rot']:
        return d['x'], d['z']
    x, z = d['x'], d['z'] - LEDD_Z
    c, s = math.cos(th), math.sin(th)
    return x * c - z * s, LEDD_Z + x * s + z * c

def tp(th):
    M = sum(d['m'] for d in delar)
    xs = zs = ys = 0.0
    for d in delar:
        x, z = rot(d, th)
        xs += d['m'] * x; zs += d['m'] * z; ys += d['m'] * d['y']
    return M, xs / M, ys / M, zs / M

# støttefeltet: filtputa under flensen (bøyetangenten er bakkanten)
STOTTE = dict(mot_armen=FOT_X1 - FILT_INNSETT, fra_armen=FOT_X0 + FILT_INNSETT,
              framover=-Y_TAN - FLENS_D + FILT_INNSETT, bakover=-Y_TAN - FILT_INNSETT)

def vipp(th):
    M, x, y, z = tp(th)
    return dict(
        mot_armen=math.degrees(math.atan2(STOTTE['mot_armen'] - x, z)),
        fra_armen=math.degrees(math.atan2(x - STOTTE['fra_armen'], z)),
        framover=math.degrees(math.atan2(y - STOTTE['framover'], z)),
        bakover=math.degrees(math.atan2(STOTTE['bakover'] - y, z)))

from shapely.geometry import MultiPoint
filt = flens.buffer(-FILT_INNSETT)
kassett = Polygon([(KASSETT[0] + 3, T_STATIV / 2 + 2), (KASSETT[1] - 3, T_STATIV / 2 + 2),
                   (KASSETT[1] - 3, KASSETT[2] - 2), (KASSETT[0] + 3, KASSETT[2] - 2)])   # silikonpute under kassetten
SKROG = {'berre flensen': filt.convex_hull, 'flens + kassett': unary_union([filt, kassett]).convex_hull}

def vipp_skrog(th, skrog):
    M, x, y, z = tp(th)
    p = Point(x, y)
    if not skrog.contains(p):
        return -1.0
    return math.degrees(math.atan2(skrog.exterior.distance(p), z))

def vipp_retning(th, skrog):
    M, x, y, z = tp(th)
    b = skrog.bounds   # xmin, ymin, xmax, ymax ; retningane langs aksane gjennom tyngdepunktet
    def kant(dx, dy):
        L = 2000
        linje = LineString([(x, y), (x + dx * L, y + dy * L)])
        q = linje.intersection(skrog.exterior)
        q = min(q.geoms, key=lambda g: g.distance(Point(x, y))) if hasattr(q, 'geoms') else q
        return math.degrees(math.atan2(q.distance(Point(x, y)), z))
    return dict(mot_armen=kant(1, 0), fra_armen=kant(-1, 0), framover=kant(0, -1), bakover=kant(0, 1))

VINKLAR = [math.radians(a) for a in range(-20, 61, 5)]
verst = {k: min(vipp(t)[k] for t in VINKLAR) for k in ('mot_armen', 'fra_armen', 'framover', 'bakover')}

# ---------------------------------------------------------------- friksjonsleddet
arm = [d for d in delar if d['rot']]
m_arm = sum(d['m'] for d in arm)
x_arm = sum(d['m'] * d['x'] for d in arm) / m_arm
z_arm = sum(d['m'] * (d['z'] - LEDD_Z) for d in arm) / m_arm
r_arm = math.hypot(x_arm, z_arm)
T_g = m_arm / 1000 * G * r_arm / 1000            # Nm, største (når tyngdepunktet ligg vassrett ut frå aksen)

ri, ro = 10.5 / 2, 20.0 / 2                      # PA6-skiver 10,5 x 20 x 1
r_eff = (2 / 3) * (ro ** 3 - ri ** 3) / (ro ** 2 - ri ** 2)
N_FLATER = 2

def tallerken(s, De=20.0, Di=10.2, t=0.5, h0=0.65, E=206000.0, nu=0.3):
    """Almen-László, éi tallerkenfjør DIN 2093 C 20 x 10,2 x 0,5 (l0 1,15)."""
    d = De / Di
    K1 = (1 / math.pi) * ((d - 1) / d) ** 2 / ((d + 1) / (d - 1) - 2 / math.log(d))
    return 4 * E / (1 - nu ** 2) * t ** 4 / (K1 * De ** 2) * (s / t) * ((h0 / t - s / t) * (h0 / t - s / (2 * t)) + 1)

F_MAAL = 140.0
s1 = 0.0
while tallerken(s1) < F_MAAL:
    s1 += 0.001
S_PAKKE = 2 * s1                                  # to fjører i serie (rygg mot rygg)
dreie = S_PAKKE / 1.0 * 360                       # M10 x 1: 1 mm per omdreiing
T = {mu: N_FLATER * mu * F_MAAL * r_eff / 1000 for mu in (0.20, 0.25, 0.30)}
tupp_ned = (T[0.25] - T_g) / (ARM_L / 1000)       # N på tuppen for å senke armen
tupp_opp = (T[0.25] + T_g) / (ARM_L / 1000)
M_tot, Xc, Yc, Zc = tp(0.0)
# trykk ned på tuppen: veltemoment om kanten mot armen
M_rett = M_tot / 1000 * G * (STOTTE['mot_armen'] - Xc) / 1000
M_trykk = tupp_ned * (ARM_L - STOTTE['mot_armen']) / 1000
# største ned-kraft på tuppen før lampa vippar
F_tupp_maks = M_rett / ((ARM_L - STOTTE['mot_armen']) / 1000)

# bøying av flensen for hand: plastisk moment
M_pl = 235 * (FOT_X1 - FOT_X0) * T_STATIV ** 2 / 4 / 1000   # Nm

ut = dict(
    plate_areal_mm2=round(A), plate_tp_xz=[round(plate_netto.centroid.x, 1), round(plate_netto.centroid.y, 1)],
    vevar_mm=dict(spalte_ledd=round(vev_spalte_ledd, 1), spalte_kant=round(vev_spalte_kant, 1),
                  stopp_ledd=round(vev_stopp_ledd, 1), stopp_kant=round(vev_stopp_kant, 1),
                  stopp_spalte=round(vev_stopp_spalte, 1)),
    tangent_venstre=[round(v, 1) for v in tl], tangent_hogre=[round(v, 1) for v in tr],
    delar=[dict(namn=d['namn'], g=round(d['m'], 1), x=round(d['x'], 1), y=round(d['y'], 1), z=round(d['z'], 1))
           for d in delar],
    total_g=round(M_tot, 1), tp_mm=[round(Xc, 1), round(Yc, 1), round(Zc, 1)],
    stotte=STOTTE, vipp_arm_vassrett={k: round(v, 1) for k, v in vipp(0.0).items()},
)
ut['vipp_verst'] = {k: round(v, 1) for k, v in verst.items()}
ut['vipp_per_vinkel'] = {round(math.degrees(t)): {k: round(v, 1) for k, v in vipp(t).items()} for t in VINKLAR[::4]}
ut['tp_per_vinkel'] = {round(math.degrees(t)): [round(v, 1) for v in tp(t)[1:]] for t in VINKLAR[::4]}
ut['ledd'] = dict(m_arm_g=round(m_arm, 1), tp_arm_x=round(x_arm, 1), tp_arm_z=round(z_arm, 1),
                  T_g_Nm=round(T_g, 3), r_eff_mm=round(r_eff, 2), F_N=F_MAAL,
                  fjor_s_per_skive_mm=round(s1, 3), pakke_s_mm=round(S_PAKKE, 3), mutter_grader=round(dreie),
                  F_ved_s_075h0=round(tallerken(0.4875), 0),
                  T_mu020=round(T[0.20], 3), T_mu025=round(T[0.25], 3), T_mu030=round(T[0.30], 3),
                  tupp_ned_N=round(tupp_ned, 2), tupp_opp_N=round(tupp_opp, 2),
                  rettande_moment_Nm=round(M_rett, 3), trykk_moment_Nm=round(M_trykk, 3),
                  F_tupp_maks_N=round(F_tupp_maks, 2))
ut['vipp_alle_retningar_min'] = {k: round(min(vipp_skrog(t, v) for t in VINKLAR), 1) for k, v in SKROG.items()}
ut['vipp_retning_verst'] = {k: {r: round(min(vipp_retning(t, v)[r] for t in VINKLAR), 1)
                                for r in ('mot_armen', 'fra_armen', 'framover', 'bakover')} for k, v in SKROG.items()}
ut['kassett_klaring_vinkel_grad'] = round(math.degrees(math.atan2(0.3, KASSETT[2] - 2 + Y_TAN)), 2)
ut['flens_g'] = round(flens.area * T_STATIV * STAL, 1)
ut['boying_plastisk_moment_Nm'] = round(M_pl, 1)
if 'SKALA' not in os.environ and 'T' not in os.environ and 'FLENS' not in os.environ:
    (HER / 'rekning_serie.json').write_text(json.dumps(ut, ensure_ascii=False, indent=1), encoding='utf-8')
if os.environ.get('KORT'):
    print(SK, T_STATIV, FLENS_D, ut['total_g'], ut['tp_mm'], ut['vipp_alle_retningar_min'], ut['vipp_retning_verst'], ut['ledd']['T_g_Nm'], ut['ledd']['F_tupp_maks_N'], ut['ledd']['tupp_ned_N'])
else:
    print(json.dumps(ut, ensure_ascii=False, indent=1))
