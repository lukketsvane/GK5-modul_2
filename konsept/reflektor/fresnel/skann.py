# -*- coding: utf-8 -*-
"""Skann: finare søk mellom generasjon 2 og 3. Éin parameter om gongen rundt 'kryss' (kjelda i foten, plata høgt).
Skriv skann.csv. Køyr: python skann.py [del]   der del er jamn, storleik, ansikt eller alle."""
import sys, os, csv
from familie import *

def rad(merke, lys_kropp):
    d = tal(*lys_kropp)
    Ea = max(d['E_felt'], 1e-9)
    return dict(merke=merke, felt=d['E_felt'], U=d['U'], W350=d['W'] * 350 / Ea, nytte=d['nytte'], vegg=d['E_vegg'], ansikt=d['E_ansikt'],
                lampe=d['L_lampe'], flate=d['L_flate'], lampe350=d['L_lampe'] * 350 / Ea,
                lampe_ansikt50=d['L_lampe'] * 50 / max(d['E_ansikt'], 1e-9), W_ansikt50=d['W'] * 50 / max(d['E_ansikt'], 1e-9), lm=d['lm'])

def skriv(rader, fh, w):
    for r in rader:
        w.writerow([r[k] if k == 'merke' else '%.4g' % r[k] for k in KOL]); fh.flush()
        print('%-34s felt %5.0f  U %.2f  W350 %5.2f  vegg %3.0f  ansikt %4.0f  lampe %6.0f  flate %5.0f  lampe350 %5.0f  lampe@50lx-ansikt %6.0f  W@50lx %.2f'
              % (r['merke'], r['felt'], r['U'], r['W350'], r['vegg'], r['ansikt'], r['lampe'], r['flate'], r['lampe350'], r['lampe_ansikt50'], r['W_ansikt50']), flush=True)

KOL = ['merke', 'felt', 'U', 'W350', 'nytte', 'vegg', 'ansikt', 'lampe', 'flate', 'lampe350', 'lampe_ansikt50', 'W_ansikt50', 'lm']
FLAT = lambda s, d: (30, float(np.degrees(np.arctan(d / 2 / s))), 40)     # flat topp som akkurat fyller diameter d

def jamn():
    for H in (0.55, 0.65):
        for sp in (8, 14):
            for kn, kj in (('smal', SMAL), ('flat', FLAT(H - 0.05, 0.285))):
                for mn, mot in (('midt', FELT), ('forbi', b(-0.08, 0.25, 0))):
                    yield rad('kryss H%.2f ark%d %s %s' % (H, sp, kn, mot is FELT and 'midt' or 'forbi'),
                              plate(1.0, b(0.47, 0.40, H), NED, H - 0.05, mot, spreiing=sp, kjelde=kj, fot=(0.47, 0.40)))
    for s in (0.12, 0.16):
        yield rad('over vid s%.2f ark14' % s, plate(1.0, OVER_C, OVER_A, s, FELT, spreiing=14, kjelde=VID))
        yield rad('stav vid s%.2f ark14' % s, plate(1.0, STAV_C, NED, s, FELT, spreiing=14, kjelde=VID, fot=(0.47, 0.40)))

def storleik():
    for d in (0.285, 0.20, 0.15, 0.10, 0.07):
        for sp in (2.5, 8, 14):
            yield rad('arbeid rund %.0f mm ark%.1f' % (d * 1000, sp),
                      plate(1.0, KRYSS_C, NED, 0.50, FELT, spreiing=sp, storleik=d, kjelde=FLAT(0.50, d), fot=(0.47, 0.40)))

def ansikt():
    for d in (0.285, 0.20, 0.15, 0.10):
        for sp in (8, 14):
            yield rad('ansikt kryss rund %.0f mm ark%d' % (d * 1000, sp),
                      plate(1.0, KRYSS_C, NED, 0.50, AUGE, spreiing=sp, storleik=d, kjelde=FLAT(0.50, d), fot=(0.47, 0.40)))
    for sp in (8, 14):
        yield rad('ansikt kryss heil plate smal ark%d' % sp, plate(1.0, KRYSS_C, NED, 0.50, AUGE, spreiing=sp, kjelde=SMAL, fot=(0.47, 0.40)))
        yield rad('ansikt stav s250 flat ark%d' % sp, plate(1.0, STAV_C, NED, 0.25, AUGE, spreiing=sp, kjelde=FLAT(0.25, 0.285), fot=(0.47, 0.40)))

def fin():
    """Fint søk for avgjerda: kor sterkt ark, kor høgt, kvar speglinga siktar."""
    for H in (0.55, 0.60):
        for sp in (10, 12):
            for mn, mot in (('midt', FELT), ('litt forbi', b(-0.04, 0.25, 0)), ('forbi', b(-0.08, 0.25, 0))):
                yield rad('kryss H%.2f ark%d smal %s' % (H, sp, mn),
                          plate(1.0, b(0.47, 0.40, H), NED, H - 0.05, mot, spreiing=sp, kjelde=SMAL, fot=(0.47, 0.40)))
    for sp in (10, 12):
        yield rad('over vid s0.12 ark%d' % sp, plate(1.0, OVER_C, OVER_A, 0.12, FELT, spreiing=sp, kjelde=VID))
    yield rad('kryss matt bakside stemning', plate(0.0, KRYSS_C, NED, 0.50, FELT, snudd=True, bakside=MATT, kjelde=SMAL, fot=(0.47, 0.40)))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    kva = sys.argv[1] if len(sys.argv) > 1 else 'alle'
    deler = dict(jamn=jamn, storleik=storleik, ansikt=ansikt, fin=fin)
    for nm, f in deler.items():
        if kva not in (nm, 'alle'): continue
        with open(os.path.join(HER, 'skann-%s.csv' % nm), 'w', newline='', encoding='utf-8') as fh:
            w = csv.writer(fh); w.writerow(KOL); skriv(f(), fh, w)
