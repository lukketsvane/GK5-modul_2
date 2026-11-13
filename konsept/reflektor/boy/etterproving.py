# -*- coding: utf-8 -*-
"""Etterprøving av dei tre beste i BØY. Køyr: python etterproving.py  (skriv etterproving.txt)
Endrar ikkje familie.py eller motoren. Augehøgda blir flytta i AUGE og sett tilbake."""
import sys, os, tempfile
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
from familie import *
import familie as F
import lysskisse

UT = open(os.path.join(HER, 'etterproving.txt'), 'w', encoding='utf-8')
def p(*a):
    s = ' '.join(str(x) for x in a); print(s); UT.write(s + '\n'); UT.flush(); sys.stdout.flush()

G3 = dict(GEN3)
FUNN = {   # frå funn.md / agenten: W350, felt, U, auge, vegg, ansikt, s_auge, s_vegg, likskap, topp, sprang
    'spegel-kuv-1.2':  dict(W350=2.14, felt=817, jamnheit=0.60, auge=194, vegg=24, ansikt=45, s_auge=83, s_vegg=68, likskap=0.23, topp=0.70, sprang=0.13),
    'to-spegel':       dict(W350=2.36, felt=741, jamnheit=0.43, auge=205, vegg=108, ansikt=61, s_auge=94, s_vegg=56, likskap=0.58, topp=1.01, sprang=0.05),
    'to-spegel-kryss': dict(W350=3.32, felt=527, jamnheit=0.33, auge=224, vegg=114, ansikt=60, s_auge=139, s_vegg=50, likskap=0.74, topp=0.97, sprang=0.02),
}

def spegl_ark(lys):
    """Lysaste del av arket sett i dataskjermen (spegelbiletet av auget), utan reflektans i skjermen og utan okklusjon."""
    M = AUGE.copy(); M[1] = 2 * 0.45 - AUGE[1]; best = 0.0
    for l in lys:
        if not isinstance(l, Ark): continue
        w = M - l.Pf; w = w / np.linalg.norm(w, axis=1)[:, None]
        tt = (0.45 - l.Pf[:, 1]) / (M[1] - l.Pf[:, 1]); X = l.Pf + (M - l.Pf) * tt[:, None]
        ok = (l.Pf[:, 1] < 0.45) & (np.abs(X[:, 0]) < 0.27) & (X[:, 2] > ZB + 0.11) & (X[:, 2] < ZB + 0.42)
        if ok.any(): best = max(best, float(l.L_flis(np.flatnonzero(ok), w[ok]).max()))
    return best

def geometri(lys, kropp):
    a = [l for l in lys if isinstance(l, Ark)][0]
    ks = [l for l in lys if not isinstance(l, Ark) and getattr(l, 'mater', False)]
    lm = sum(k.lm for k in ks); spill = sum(k.lm_ut for k in ks)
    P = np.concatenate([a.prim.V0, a.prim.V0 + a.prim.E1, a.prim.V0 + a.prim.E2])
    return dict(strekk=a.strekk, spill=spill / max(lm, 1e-9), ymin=P[:, 1].min(), ymax=P[:, 1].max(),
                zmin=P[:, 2].min() - ZB, zmax=P[:, 2].max() - ZB, xmin=P[:, 0].min(), xmax=P[:, 0].max())

def ein_rad(namn, g):
    mappe = tempfile.mkdtemp(prefix='etterp_')
    r = familie([(namn, g)], mappe, px=0)[0]
    R, m = overgang(g, n=5)
    f = FUNN[namn]
    nye = dict(W350=r['W350'], felt=r['felt'], jamnheit=r['jamnheit'], auge=r['auge'], vegg=r['vegg'], ansikt=r['ansikt'],
               s_auge=r['s_auge'], s_vegg=r['s_vegg'], likskap=r['likskap'], topp=m['topp'], sprang=m['sprang'])
    p('==', namn)
    for k, v in f.items():
        x = nye[k]; av = abs(x - v) / max(abs(v), 1e-9)
        p('  %-9s funn %8.2f  no %8.2f  avvik %5.1f %% %s' % (k, v, x, 100 * av, 'FEIL' if av > 0.05 and abs(x - v) > 0.006 else ''))
    p('  strekk %.4f  jamn_auke %.2f  skjerm %.0f lx  s_skjerm %.0f lx  s_felt %.0f' % (r['strekk'], m['jamn_auke'], r.get('skjerm', -1), r.get('s_skjerm', -1), r['s_felt']))
    p('  overgang auge', [round(x) for x in m['auge']], 'felt', [round(x) for x in m['felt']], 'vegg', [round(x) for x in m['vegg']])
    for t in (0.0, 1.0):
        lys, kr = g(t); d = tal(lys, kr); ge = geometri(lys, kr)
        fd = d['_fordeling']
        p('  t=%.0f geometri: strekk %.4f  spill forbi arket %.0f %%  ark x %.2f..%.2f  y %.2f..%.2f  h %.2f..%.2f' %
          (t, ge['strekk'], 100 * ge['spill'], ge['xmin'], ge['xmax'], ge['ymin'], ge['ymax'], ge['zmin'], ge['zmax']))
        p('       fordeling felt %.2f bord %.2f veggnær %.2f veggelles %.2f tak %.2f tapt %.2f | L_spegl(kjelde) %.0f  ark i skjermen %.0f cd/m2 | U %.2f' %
          (*fd, d['L_spegl'], spegl_ark(lys), d['U']))
        for k in lys:
            if isinstance(k, Ark): continue
            pos = np.asarray(k.pts).mean(0); w = nrm(AUGE - pos)
            p('       kjelde i (%.2f, %.2f, %.2f) mot auget 47: L %.0f cd/m2' % (pos[0], pos[1], pos[2] - ZB, float(k.L(w[None])[0])))
    # augehøgder
    for h in (0.25, 0.47, 0.60):
        lysskisse.AUGE[2] = ZB + h
        for t in (1.0, 0.5, 0.0):
            lys, kr = g(t); d = tal(lys, kr)
            p('  auge %.2f t=%.1f: L_lampe %6.0f  L_flate %5.0f  ark i skjermen %5.0f  ansikt %3.0f %s' %
              (h, t, d['L_lampe'], d['L_flate'], spegl_ark(lys), d['E_ansikt'],
               'OVER 1500' if t == 1.0 and d['L_lampe'] > 1500 else ('OVER 500' if t == 0.0 and d['L_lampe'] > 500 else '')))
    lysskisse.AUGE[2] = ZB + 0.47
    return r

def robust(namn, side):
    """Kviler resultatet på antakinga om overflata? BLANK er rd 0,03, rs 0,85, sigma 2,5 (ANTAKING)."""
    if namn == 'spegel-kuv-1.2':
        return lambda t: lampe(t, fot=F.F2, c=F.CF, mot=vipp(t, til=F.SIKT), ref=F.SIKT, form=boy(-1 / 1.2), side=side, n=30)
    if namn == 'to-spegel':
        return lambda t: F.to(t, 'gli', side=side, n=30)
    return lambda t: F.to(t, 'kryss', side=side, n=30)

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    for namn in TRE:
        ein_rad(namn, G3[namn])
    p('== robustheit for overflata (arbeid, auge 47 og 25)')
    VAR = [('BLANK', BLANK), ('sigma6', dict(rd=0.03, rs=0.85, sigma=6.0)), ('sigma14', dict(rd=0.03, rs=0.85, sigma=14.0)),
           ('rd0.3', dict(rd=0.30, rs=0.55, sigma=2.5)), ('folie', F.FOLIE)]
    for namn in TRE:
        for vn, side in VAR:
            g = robust(namn, side)
            la, ka = g(1.0); d = tal(la, ka); ls, ks = g(0.0); s = tal(ls, ks)
            p('  %-16s %-8s felt %4.0f U %.2f W350 %.2f vegg %3.0f auge47 %5.0f auge25 %6.0f | stemning auge %4.0f vegg %3.0f' %
              (namn, vn, d['E_felt'], d['U'], d['W'] * 350 / d['E_felt'], d['E_vegg'], d['L_lampe'], auge_i(la, ka, 0.25), s['L_lampe'], s['E_vegg']))
    UT.close()
