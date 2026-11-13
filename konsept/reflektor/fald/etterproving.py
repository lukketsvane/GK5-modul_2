# -*- coding: utf-8 -*-
"""Etterprøving av dei tre beste i FALD (Z-spreidd, rund-bok, tak-vipp).

  python etterproving.py      skriv tala til etterproving.txt i denne mappa

Reknar tala på nytt med tal() og overgang(), og prøver dei mot fysikk og antakingar:
spill forbi arket, kvar arket står, andre augehøgder (25 og 60 cm over bordet), og SATIN
med sigma 6 og 14 og med rd 0,3. Endrar ikkje familie.py, faldmotor.py eller lysskisse.py.
"""
import sys, os, json, time
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
try: sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
except Exception: pass
from familie import *
import lysskisse

UT = []
def p(*a):
    s = ' '.join(str(x) for x in a); print(s); UT.append(s)

FUNN = {   # frå funn.md og tal.md
    'Z-spreidd': dict(W350=3.83, felt=457, U=0.34, auge=963, vegg=114, ansikt=48, s_auge=76, s_vegg=64, lik=0.68, W3=5.24, sprang=0.06, topp=0.70),
    'rund-bok':  dict(W350=4.05, felt=432, U=0.43, auge=941, vegg=118, ansikt=49, s_auge=222, s_vegg=46, lik=0.84, W3=5.15, sprang=0.02, topp=0.70),
    'tak-vipp':  dict(W350=3.33, felt=526, U=0.24, auge=974, vegg=96, ansikt=50, s_auge=53, s_vegg=48, lik=0.56, W3=5.23, sprang=0.07, topp=0.70),
}

def variant(namn, fl):
    if namn == 'Z-spreidd':
        return lambda t: lampe(t, saman(K1(FX(-0.15), 0.03, True, R=MJ), K1(FX(0.15), 0.03, False, R=MJ)), rot='vegg', flater=(fl,))
    if namn == 'rund-bok':
        return lambda t: lampe(t, K1('felt', 0.07, False, R=MJ, anker=(0.04, 0.07)), storleik=0.28, rot='vegg', anker=(0.04, 0.07), flater=(fl,))
    return lambda t: lampe(t, FAST_TAK_MJ, rot=vipp, flater=(fl,))

def rad(g):
    s = tal(*g(0.0)); a = tal(*g(1.0))
    La = max(a['L_lampe'], a['L_flate']); Ls = max(s['L_lampe'], s['L_flate'])
    krav = dict(felt=350 / a['E_felt'], vegg=100 / a['E_vegg'], ansikt=50 / a['E_ansikt'])
    bind = max(krav, key=krav.get)
    return dict(W350=a['W'] * 350 / a['E_felt'], felt=a['E_felt'], U=a['U'], auge=La, vegg=a['E_vegg'], ansikt=a['E_ansikt'],
                s_auge=Ls, s_vegg=s['E_vegg'], s_felt=s['E_felt'], lik=lysskisse.likskap(s['_fordeling'], a['_fordeling']),
                W3=a['W'] * krav[bind], bind=bind, auge3=La * krav[bind], skjerm=a['E_skjerm'] / a['E_felt'],
                strekk=max(a['strekk'], s['strekk']))

def fmt(r):
    return ('W350 %.2f felt %.0f U %.2f auge %.0f vegg %.0f ansikt %.0f | s_auge %.0f s_vegg %.0f s_felt %.0f | lik %.2f W3 %.2f (%s) auge3 %.0f skjerm/felt %.2f strekk %.4f'
            % (r['W350'], r['felt'], r['U'], r['auge'], r['vegg'], r['ansikt'], r['s_auge'], r['s_vegg'], r['s_felt'], r['lik'], r['W3'], r['bind'], r['auge3'], r['skjerm'], r['strekk']))

t0 = time.time()
G = dict(GEN3)
for namn in TRE:
    g = G[namn]
    p('\n=== %s ===' % namn)
    # 1 tala på nytt
    r = rad(g); p('nytt  ', fmt(r))
    f = FUNN[namn]; avvik = []
    for k_ in ('W350', 'felt', 'U', 'auge', 'vegg', 'ansikt', 's_auge', 's_vegg', 'lik', 'W3'):
        d_ = (r[k_] - f[k_]) / f[k_]
        if abs(d_) > 0.05: avvik.append('%s %.3g mot %.3g (%+.0f %%)' % (k_, r[k_], f[k_], d_ * 100))
    p('avvik over 5 %:', avvik if avvik else 'ingen')
    _, m = overgang(g, n=5)
    p('overgang n=5: topp %.2f sprang %.2f jamn_auke %.2f' % (m['topp'], m['sprang'], m['jamn_auke']))
    p('   auge', [round(x) for x in m['auge']], 'felt', [round(x) for x in m['felt']], 'vegg', [round(x) for x in m['vegg']])
    for fx, mx in (('sprang', m['sprang']), ('topp', m['topp'])):
        if abs(mx - f[fx]) / f[fx] > 0.05: p('   avvik', fx, '%.3f mot %.2f' % (mx, f[fx]))
    # 2 fysikk: geometri, spill, sjølvskugge
    for t in (0.0, 1.0):
        lys, kropp = g(t); k, a = lys[0], lys[1]
        Pf = a.Pf
        hell = math.degrees(math.acos(abs(nrm(a.Nf.mean(0))[2])))
        p('t=%.0f ark: y %.3f..%.3f  z over bord %.3f..%.3f  x %.3f..%.3f  snittnormal %.0f grader frå loddrett'
          % (t, Pf[:, 1].min(), Pf[:, 1].max(), Pf[:, 2].min() - ZB, Pf[:, 2].max() - ZB, Pf[:, 0].min(), Pf[:, 0].max(), hell))
        p('      kjelde lm %.0f, inn på arket %.0f (%.0f %%), spill %.0f %%; rift %.2f mm, sk_inn %.1f %%, sk_ut %.1f %%, boydel %.0f %%, strekk %.4f'
          % (k.lm, a.lm_inn, 100 * a.lm_inn / k.lm, 100 * (1 - a.lm_inn / k.lm), a.rift, a.sk_inn * 100, a.sk_ut * 100, a.boydel * 100, a.strekk))
        if t == 1.0:
            ds = tal([k], kropp + [a.prim])          # berre spillet, arket som skugge
            fo = ds['_fordeling']
            p('      spill åleine: felt %.0f lx, vegg %.0f lx, kjelda mot auget %.0f cd/m²; fordeling felt/bord/veggnær/vegg elles/tak/rom %s'
              % (ds['E_felt'], ds['E_vegg'], ds['L_lampe'], [round(x, 2) for x in fo]))
    p('kjelda KP', [round(float(x), 3) for x in KP], '(y = %.2f, skjermplanet y = 0,45; skjermen x frå -0,27 til 0,27)' % KP[1])
    # 3 augehøgder
    for h in (0.25, 0.60):
        lysskisse.AUGE[2] = ZB + h
        s = tal(*g(0.0)); a_ = tal(*g(1.0))
        p('auge %2.0f cm: arbeid lampe %.0f flate %.0f cd/m², ansikt %.0f lx | stemning lampe %.0f flate %.0f'
          % (h * 100, a_['L_lampe'], a_['L_flate'], a_['E_ansikt'], s['L_lampe'], s['L_flate']))
    lysskisse.AUGE[2] = ZB + 0.47
    # 4 SATIN-antakinga
    for lab, fl in (('sigma 6', dict(SATIN, sigma=6.0)), ('sigma 14', dict(SATIN, sigma=14.0)), ('rd 0,3', dict(SATIN, rd=0.30))):
        rv = rad(variant(namn, fl)); p('%-8s' % lab, fmt(rv))
    p('tid %.0f s' % (time.time() - t0))

open(os.path.join(HER, 'etterproving.txt'), 'w', encoding='utf-8').write('\n'.join(UT) + '\n')
