# -*- coding: utf-8 -*-
"""Etterprøving av dei tre beste i FRESNEL (over-vipp, kryss-rund, over-knekk). Endrar ikkje familie.py eller motoren.
Skriv etterproving.txt. Køyr: python etterproving.py"""
import sys, os
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
from familie import *
import familie as _f
import lysskisse
_f.N = N_FIN
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass

UT = []
def ut(s):
    print(s, flush=True); UT.append(s)
    open(os.path.join(HER, 'etterproving.txt'), 'w', encoding='utf-8').write('\n'.join(UT) + '\n')

AUGE0 = float(lysskisse.AUGE[2])

def over_vipp(t, s=0.12, kjelde=VID, spreiing=12):
    return plate(t, OVER_C, OVER_A, s, gli(b(0.0, YV, 0.60), FELT), spreiing=spreiing, kjelde=kjelde)
def kryss_rund(t, spreiing=12):
    return kryss(t, mot=gli(VEGGMAAL, FORBI), storleik=0.285, spreiing=spreiing, kjelde=SMAL)
def over_knekk(t, spreiing=12):
    return knekk2(t, OVER_C, OVER_A, 0.12, VEGG_OVER, FELT, spreiing=spreiing, kjelde=VID, flytt=0.0)

KAND = [('over-vipp', over_vipp), ('kryss-rund', kryss_rund), ('over-knekk', over_knekk)]

def spegl_ark(lys, R_skjerm=0.04):
    """Spegling av arket i skjermen, som motoren hoppar over. Lysaste flis sett i skjermen, gonger refleksjonen (ANTAKING 4 %)."""
    M = lysskisse.AUGE.copy(); M[1] = 2 * 0.45 - M[1]
    best = 0.0
    for l in lys:
        if not isinstance(l, lysskisse.Ark): continue
        P = l.Pf; ok = P[:, 1] < 0.449
        if not ok.any(): continue
        f = (0.45 - M[1]) / (P[:, 1] - M[1])
        X = M + (P - M) * f[:, None]
        inn = ok & (np.abs(X[:, 0]) < 0.27) & (X[:, 2] > ZB + 0.11) & (X[:, 2] < ZB + 0.42)
        fi = np.flatnonzero(inn)
        if len(fi):
            w = X[fi] - P[fi]; w /= np.linalg.norm(w, axis=1)[:, None]
            best = max(best, float(l.L_flis(fi, w).max()))
    return best * R_skjerm

def kort(d):
    return ('felt %5.0f lx  U %.2f  vegg %4.0f  ansikt %3.0f  lampe %6.0f  flate %5.0f  spegl(kjelde) %.0f'
            % (d['E_felt'], d['U'], d['E_vegg'], d['E_ansikt'], d['L_lampe'], d['L_flate'], d['L_spegl']))

# 1 Tala på nytt
ut('# 1 Tala på nytt (n = 26), t = 0 og 1, og overgang i fem steg')
for nm, g in KAND:
    R, m = overgang(g, n=5)
    a, s = R[-1], R[0]
    Ea = a['E_felt']
    ut('%s: felt %.0f  U %.2f  W350 %.2f  vegg %.0f  ansikt %.0f  auge %.0f | stemning auge %.0f vegg %.0f | likskap %.2f'
       % (nm, Ea, a['U'], a['W'] * 350 / Ea, a['E_vegg'], a['E_ansikt'], max(a['L_lampe'], a['L_flate']),
          max(s['L_lampe'], s['L_flate']), s['E_vegg'], likskap(s['_fordeling'], a['_fordeling'])))
    ut('   felt(t) %s | U(t) %s | auge(t) %s | topp %.2f sprang %.2f'
       % (' '.join('%.0f' % x for x in m['felt']), ' '.join('%.2f' % r['U'] for r in R),
          ' '.join('%.0f' % x for x in m['auge']), m['topp'], m['sprang']))
    lys, _ = g(1.0)
    k = lys[0]; inn = sum(l.lm_inn for l in lys if isinstance(l, lysskisse.Ark))
    ut('   arbeid: kjelde %.0f lm, på plata %.0f lm (%.0f %%), i taket %.0f lm, spegl(kjelde) %.0f cd/m2, spegl(ark) %.1f cd/m2'
       % (k.lm, inn, 100 * inn / k.lm, a['lm_tak'], a['L_spegl'], spegl_ark(lys)))

# 2 Augehøgder
ut('# 2 Augehøgder 25, 47 og 60 cm over bordet')
for nm, g in KAND + [('over-vipp brønn 50', lambda t: over_vipp(t, kjelde=(40, 50, 50)))]:
    for h in (0.25, 0.60):
        lysskisse.AUGE[2] = ZB + h
        for t in (0.0, 1.0):
            lys, kr = g(t); d = tal(lys, kr)
            k = lys[0]; v = float(np.degrees(np.arccos(np.clip(nrm(lysskisse.AUGE - k.pts[0]) @ k.akse, -1, 1))))
            ut('%s h %.2f t %.0f: %s  spegl(ark) %.1f  vinkel auge-kjeldeakse %.0f' % (nm, h, t, kort(d), spegl_ark(lys), v))
    lysskisse.AUGE[2] = AUGE0

# 3 Antakinga om arket
ut('# 3 Arket: sigma 6 og 14, og rd 0,3 (rs 0,58)')
for sp in (6, 14):
    for nm, g in KAND:
        a = tal(*g(1.0, spreiing=sp)) if nm != 'over-vipp' else tal(*over_vipp(1.0, spreiing=sp))
        s = tal(*(g(0.0, spreiing=sp) if nm != 'over-vipp' else over_vipp(0.0, spreiing=sp)))
        ut('sigma %d %s: arbeid %s | stemning auge %.0f' % (sp, nm, kort(a), max(s['L_lampe'], s['L_flate'])))
_fs = _f.fresnelspegel
def fs_rd(kjelde, senter, normal, f=0.1871, storleik=(0.285, 0.285), spreiing=2.5, n=30, **kw):
    return ark(kjelde, senter, normal, storleik=storleik, fresnel=f, n=n, framside=dict(rd=0.30, rs=0.58, sigma=spreiing), **kw)
_f.fresnelspegel = fs_rd
for nm, g in KAND:
    a = tal(*g(1.0)); s = tal(*g(0.0))
    ut('rd 0,3 %s: arbeid %s  W350 %.2f | stemning auge %.0f' % (nm, kort(a), a['W'] * 350 / a['E_felt'], max(s['L_lampe'], s['L_flate'])))
_f.fresnelspegel = _fs

# 4 Over-vipp med telefonen på sjølve skjermkanten (12 cm under plata er 9 cm over skjermkanten)
ut('# 4 Kjelda på sjølve skjermkanten, s = 0,219 m')
kp = OVER_C + 0.12 * OVER_A
ut('kjelda i over-vipp står i y %.3f, %.3f m over bordet (skjermkanten: y 0,45, 0,42 m)' % (kp[1], kp[2] - ZB))
for t in (0.0, 1.0):
    d = tal(*over_vipp(t, s=0.219))
    ut('over-vipp s 0,219 t %.0f: %s' % (t, kort(d)))
