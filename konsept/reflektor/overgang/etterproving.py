# -*- coding: utf-8 -*-
"""Etterprøving av dei tre beste i OVERGANG (kryss-hog, skjer, drei-snigel). Køyr: python etterproving.py
Skriv etterproving.txt. Endrar ikkje familie.py eller motoren. AUGE og SATIN blir endra i minnet og sette tilbake."""
import sys, os, time
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
try:
    import psutil
    pr = psutil.Process(); pr.nice(psutil.IDLE_PRIORITY_CLASS)
    n = psutil.cpu_count(); pr.cpu_affinity(list(range(max(1, n - 2))))
except Exception:
    pass
from familie import *
import familie as F
import lysskisse

try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
TILLEGG = len(sys.argv) > 1 and sys.argv[1] == 'tillegg'
UT = open(os.path.join(HER, 'etterproving.txt'), 'a' if TILLEGG else 'w', encoding='utf-8')
def p(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); UT.write(s + '\n'); UT.flush()

A = F._ALLE
NAMN = ['kryss-hog', 'skjer', 'drei-snigel']
FUNN = {
    'kryss-hog':   dict(W350=4.46, felt=393, jamnheit=0.32, auge=555, vegg=126, ansikt=37, s_auge=148, s_vegg=6, likskap=0.28, topp=0.66, sprang=0.04, skjermmaks=66),
    'skjer':       dict(W350=2.25, felt=779, jamnheit=0.31, auge=1338, vegg=29, ansikt=55, s_auge=173, s_vegg=60, likskap=0.08, topp=0.79, sprang=0.15, skjermmaks=114),
    'drei-snigel': dict(W350=2.05, felt=852, jamnheit=0.24, auge=2311, vegg=55, ansikt=63, s_auge=279, s_vegg=54, likskap=0.20, topp=0.80, sprang=0.11, skjermmaks=132),
}

def spegl_ark(lys):
    """Lysaste del av eit ark sett i dataskjermen frå auget (spegelbiletet av auget), utan okklusjon."""
    M = AUGE.copy(); M[1] = 2 * 0.45 - AUGE[1]; best = 0.0
    for l in lys:
        if not isinstance(l, Ark): continue
        w = M - l.Pf; w = w / np.linalg.norm(w, axis=1)[:, None]
        tt = (0.45 - l.Pf[:, 1]) / (M[1] - l.Pf[:, 1]); X = l.Pf + (M - l.Pf) * tt[:, None]
        ok = (l.Pf[:, 1] < 0.45) & (np.abs(X[:, 0]) < 0.27) & (X[:, 2] > ZB + 0.11) & (X[:, 2] < ZB + 0.42)
        if ok.any(): best = max(best, float(l.L_flis(np.flatnonzero(ok), w[ok]).max()))
    return best

def geometri(lys):
    out = []
    for a in [l for l in lys if isinstance(l, Ark)]:
        P = np.concatenate([a.prim.V0, a.prim.V0 + a.prim.E1, a.prim.V0 + a.prim.E2])
        out.append(dict(strekk=a.strekk, lm_inn=a.lm_inn, ymin=P[:, 1].min(), ymax=P[:, 1].max(),
                        zmin=P[:, 2].min() - ZB, zmax=P[:, 2].max() - ZB, xmin=P[:, 0].min(), xmax=P[:, 0].max()))
    ks = [l for l in lys if not isinstance(l, Ark)]
    return out, [(np.round(np.mean(k.pts, 0) - [0, 0, ZB], 3).tolist(), round(k.lm, 1), round(getattr(k, 'lm_ut', k.lm), 1)) for k in ks]

def veggdelar(lys, kropp):
    """Lux på veggsona delt i venstre (x < -0,27), over skjermen (|x| < 0,27, z > 42 cm), høgre (x > 0,27) og bak skjermen."""
    R = rom(); okkl = STATISK + list(kropp) + [l.prim for l in lys]
    Ed = E_direkte(R.P, R.N, lys, okkl); Ei, B = R.radiositet(Ed); Y = (Ed + Ei) @ LUM
    kb, kv, kt = R.kart; Pv = R.P[kv.sl]; Yv = Y[kv.sl]; z = Pv[:, 2] - ZB
    sone = (np.abs(Pv[:, 0]) < 0.7) & (z > 0.08) & (z < 0.78)
    d = {}
    for namn, m in (('venstre', sone & (Pv[:, 0] < -0.27)), ('over', sone & (np.abs(Pv[:, 0]) <= 0.27) & (z > 0.42)),
                    ('bak', sone & (np.abs(Pv[:, 0]) <= 0.27) & (z <= 0.42)), ('hogre', sone & (Pv[:, 0] > 0.27)),
                    ('sone', sone), ('over sona', (np.abs(Pv[:, 0]) < 0.7) & (z >= 0.78))):
        d[namn] = float(Yv[m].mean()) if m.any() else float('nan')
    return d

def avvik(a, b):
    return abs(a - b) / max(abs(b), 1e-9)

t0 = time.time()
S0 = dict(SATIN); z0 = float(lysskisse.AUGE[2])

def hovud():
    # ---------------------------------------------------------------- 2 tala på nytt
    p('## 2 Tala på nytt (overgang n=7 og _rad)')
    BASE = {}
    for nm in NAMN:
        g = A[nm]
        R, m = overgang(g, n=7)
        r = lysskisse._rad(nm, R[0], R[-1])
        sk = [F.skjermlux(*g(float(t)))[1] for t in m['t']]
        BASE[nm] = (R, m, r)
        ny = dict(W350=r['W350'], felt=r['felt'], jamnheit=r['jamnheit'], auge=r['auge'], vegg=r['vegg'], ansikt=r['ansikt'],
                  s_auge=r['s_auge'], s_vegg=r['s_vegg'], likskap=r['likskap'], topp=m['topp'], sprang=m['sprang'], skjermmaks=max(sk))
        p(nm)
        for k, v in FUNN[nm].items():
            dv = avvik(ny[k], v)
            p('  %-10s funn %8.2f  no %8.2f  avvik %5.1f %% %s' % (k, v, ny[k], dv * 100, 'FEIL' if dv > 0.05 else ''))
        p('  jamn auke %.2f  strekk %.4f' % (m['jamn_auke'], r['strekk']))
        p('  auge   ', [round(x) for x in m['auge']])
        p('  L_lampe', [round(x['L_lampe']) for x in R], ' L_flate', [round(x['L_flate']) for x in R])
        p('  felt   ', [round(x) for x in m['felt']])
        p('  vegg   ', [round(x) for x in m['vegg']])
        p('  ansikt ', [round(x['E_ansikt']) for x in R])
        p('  skjerm maks', [round(x) for x in sk], ' motor E_skjerm_maks', [round(x['E_skjerm_maks']) for x in R])
        p('  L_spegl (kjelder)', [round(x['L_spegl']) for x in R])
        p('  fordeling arbeid (felt, bord, vegg nær, vegg elles, tak, rom)', np.round(R[-1]['_fordeling'], 3).tolist())
        p('  fordeling stemning', np.round(R[0]['_fordeling'], 3).tolist())
        p('  (%.0f s)' % (time.time() - t0))

    # ---------------------------------------------------------------- 3 fysikk: geometri, spill, spegling, veggdelar
    p('\n## 3 Fysikk')
    for nm in NAMN:
        g = A[nm]
        p(nm)
        for t in (0.0, 0.5, 1.0):
            lys, kropp = g(t)
            ark_g, kj = geometri(lys)
            p('  t=%.1f kjelder (pos over bord, lm, lm forbi ark):' % t, kj)
            for a in ark_g:
                p('        ark: lm_inn %.1f  x %.2f..%.2f  y %.3f..%.3f  z %.2f..%.2f  strekk %.4f' % (a['lm_inn'], a['xmin'], a['xmax'], a['ymin'], a['ymax'], a['zmin'], a['zmax'], a['strekk']))
            p('        arket spegla i skjermen frå auget: %.0f cd/m²' % spegl_ark(lys))
        for t in (0.0, 1.0):
            d = veggdelar(*g(t))
            p('  vegg t=%.0f: ' % t + '  '.join('%s %.0f' % (k, v) for k, v in d.items()))
        p('  (%.0f s)' % (time.time() - t0))

    # ---------------------------------------------------------------- 3 augehøgder
    p('\n## 3 Augehøgder (L mot auget per steg, maks av lampe og romflate)')
    z0 = float(lysskisse.AUGE[2])
    for dz in (0.25, 0.60):
        lysskisse.AUGE[2] = ZB + dz
        for nm in NAMN:
            g = A[nm]
            L = []; Ll = []; Sp = []
            for t in np.linspace(0, 1, 7):
                lys, kropp = g(float(t)); d = tal(lys, kropp)
                L.append(max(d['L_lampe'], d['L_flate'])); Ll.append(d['L_lampe']); Sp.append(max(d['L_spegl'], spegl_ark(lys)))
            p('  auge %2.0f cm  %-12s L %s  (lampe %s)  spegla i skjerm maks %.0f' % (dz * 100, nm, [round(x) for x in L], [round(x) for x in Ll], max(Sp)))
    lysskisse.AUGE[2] = z0
    p('  AUGE sett tilbake til', round(float(lysskisse.AUGE[2]) - ZB, 3), '(%.0f s)' % (time.time() - t0))

    # ---------------------------------------------------------------- 3 SATIN-antakinga
    p('\n## 3 SATIN (alle tre brukar SATIN på arket)')
    S0 = dict(SATIN)
    for namn_v, v in (('sigma 6', dict(sigma=6.0)), ('sigma 14', dict(sigma=14.0)), ('rd 0.3', dict(rd=0.3)), ('rd 0.3 rs 0.5', dict(rd=0.3, rs=0.5))):
        SATIN.update(S0); SATIN.update(v)
        for nm in NAMN:
            R, m = overgang(A[nm], n=7)
            r = lysskisse._rad(nm, R[0], R[-1])
            p('  %-13s %-12s felt %4.0f  W350 %.2f  U %.2f  vegg %3.0f  auge %s  topp %.2f  sprang %.2f  likskap %.2f'
              % (namn_v, nm, r['felt'], r['W350'], r['jamnheit'], r['vegg'], [round(x) for x in m['auge']], m['topp'], m['sprang'], r['likskap']))
        p('  (%.0f s)' % (time.time() - t0))
    SATIN.clear(); SATIN.update(S0)
    p('SATIN sett tilbake:', SATIN)

# ---------------------------------------------------------------- tillegg: verste kombinasjon og kollisjon med skjermen
def tillegg():
    p('\n## Tillegg: auge 25 cm saman med SATIN-variantar, i arbeid (t = 1)')
    for namn_v, v in (('SATIN', {}), ('sigma 14', dict(sigma=14.0)), ('rd 0.3', dict(rd=0.3))):
        SATIN.clear(); SATIN.update(S0); SATIN.update(v)
        lysskisse.AUGE[2] = ZB + 0.25
        for nm in NAMN:
            d = tal(*A[nm](1.0))
            p('  %-9s %-12s L_lampe %5.0f  L_flate %4.0f' % (namn_v, nm, d['L_lampe'], d['L_flate']))
    lysskisse.AUGE[2] = z0; SATIN.clear(); SATIN.update(S0)
    p('\n## Tillegg: ark-flater bak skjermplanet innanfor skjermen (|x| < 0,27, 11 til 42 cm, y over 0,45)')
    for nm in NAMN:
        lys, _ = A[nm](1.0)
        for a in [l for l in lys if isinstance(l, Ark)]:
            P = a.Pf; z = P[:, 2] - ZB
            m = (np.abs(P[:, 0]) < 0.27) & (z > 0.11) & (z < 0.42) & (P[:, 1] > 0.45)
            p('  %-12s fliser bak skjermen: %d av %d (y maks %.3f)' % (nm, int(m.sum()), len(P), P[m, 1].max() if m.any() else 0))

if __name__ == '__main__':
    tillegg() if TILLEGG else hovud()
    UT.close()
