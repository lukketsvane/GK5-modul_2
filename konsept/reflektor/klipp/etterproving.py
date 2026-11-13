# -*- coding: utf-8 -*-
"""Etterprøving av dei tre beste i familien KLIPP: ring-vipp, maane-drei, luke.

  python etterproving.py        skriv etterproving-logg.txt i mappa

Endrar ikkje familie.py, lysskisse.py eller funn.md. Prøver:
  1 tala på nytt med tal() og overgang() (n = 5), mot funn.md
  2 lyset på veggen rett bak og rundt skjermen, ikkje berre snittet over heile veggsona
  3 geometri: arket framfor skjermplanet, kor mykje av strålen arket fangar, spegling i skjermen
  4 augehøgd 25 og 60 cm over bordet (luminans langs heile overgangen)
  5 SATIN som antaking: sigma 6 og 14, og rd 0,3
"""
import sys, os, json, time
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
sys.path.insert(0, os.path.join(HER, '..', '..', 'lysskisse'))
from familie import *
import familie as F
import lysskisse

try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass

LOGG = open(os.path.join(HER, 'etterproving-logg.txt'), 'w', encoding='utf-8')
def p(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); LOGG.write(s + '\n'); LOGG.flush()

def kand(side=SATIN):
    lerp_ = lambda a, c, t: a + (c - a) * t
    return {
        'ring-vipp': lambda t: lampe(t, klipp=ring(0.05), mot=lerp_(b(0.0, YV, 0.45), FELT, t), n=N2, side=side),
        'maane-drei': lambda t: lampe(t, klipp=maane(0.085, dv=-0.075), sikt=(0, -0.04), rull=lerp_(0, 110, t), n=N2, side=side),
        'luke': lambda t: lampe(t, flikar=[dict(u=0.0, v=-0.055, b=0.11, l=0.11, vinkel=lerp_(80, 25, t), akse=0)], n=N2, side=side),
    }

FUNN = {  # frå funn.md / oppdraget
    'ring-vipp': dict(W350=4.44, felt=394, jamnheit=0.42, auge=779, vegg=117, ansikt=58, s_auge=169, s_vegg=63, s_felt=11, likskap=0.78, topp=0.72, sprang=0.04),
    'maane-drei': dict(W350=4.60, felt=381, jamnheit=0.21, auge=940, vegg=138, ansikt=55, s_auge=171, s_vegg=56, s_felt=58, likskap=0.90, topp=0.67, sprang=0.02),
    'luke': dict(W350=4.24, felt=413, jamnheit=0.38, auge=1047, vegg=59, ansikt=55, s_auge=191, s_vegg=31, s_felt=89, likskap=0.74, topp=0.52, sprang=0.10),
}

def veggflekk(lys, kropp):
    """Lux på veggen i tre soner: rett bak skjermen, ramma 20 cm rundt skjermen, og heile veggsona. Pluss toppunktet."""
    R = lysskisse.rom()
    okkl = lysskisse.STATISK + list(kropp) + [l.prim for l in lys]
    Ed = lysskisse.E_direkte(R.P, R.N, lys, okkl)
    Ei, B = R.radiositet(Ed)
    Y = (Ed + Ei) @ lysskisse.LUM
    kb, kv, kt = R.kart
    Pv = R.P[kv.sl]; Yv = Y[kv.sl]; x = Pv[:, 0]; z = Pv[:, 2] - ZB
    sona = (np.abs(x) < 0.7) & (z > 0.08) & (z < 0.78)
    bak = (np.abs(x) < 0.27) & (z > 0.11) & (z < 0.42)
    ramme_ = (np.abs(x) < 0.47) & (z > 0.0) & (z < 0.62) & ~bak
    venstre = sona & (x < 0); hogre = sona & (x > 0)
    i = int(np.argmax(np.where(sona, Yv, -1)))
    return dict(sona=float(Yv[sona].mean()), bak=float(Yv[bak].mean()), ramme=float(Yv[ramme_].mean()),
                venstre=float(Yv[venstre].mean()), hogre=float(Yv[hogre].mean()),
                topp_lx=float(Yv[i]), topp_x=float(x[i]), topp_z=float(z[i]))

def geometri(lys, auge):
    """Største y i arka, kjeldeplass, kor mykje av strålen arka fangar, og om arket syner i skjermen sett frå auget."""
    ks = [l for l in lys if not isinstance(l, Ark) and getattr(l, 'mater', False)]
    arka = [l for l in lys if isinstance(l, Ark)]
    ymax = max(float(a.Pf[:, 1].max()) for a in arka)
    xmin = min(float(a.Pf[:, 0].min()) for a in arka)
    kjelde_lm = sum(k.lm for k in ks); inn = sum(a.lm_inn for a in arka)
    M = np.array(auge, float).copy(); M[1] = 2 * 0.45 - M[1]
    i_skjerm = 0
    for a in arka:
        P = a.Pf; f = (0.45 - M[1]) / (P[:, 1] - M[1])
        X = M + (P - M) * f[:, None]
        i_skjerm += int(((np.abs(X[:, 0]) < 0.27) & (X[:, 2] > ZB + 0.11) & (X[:, 2] < ZB + 0.42) & (P[:, 1] < 0.45)).sum())
    return dict(ymax=ymax, xmin=xmin, kp=[round(float(v), 3) for v in ks[0].pts[0]] if ks else None,
                fanga=inn / max(kjelde_lm, 1e-9), sum_inn_over_kjelde=inn > kjelde_lm * 1.0001, fliser_i_skjerm=i_skjerm)

def avvik(ny, gml):
    return abs(ny - gml) / max(abs(gml), 1e-9)

t0 = time.time()
UT = {}
K = kand()
for namn, g in K.items():
    p('=' * 70); p(namn)
    R, m = overgang(g, n=5)
    s, a = R[0], R[-1]
    La = max(a['L_lampe'], a['L_flate']); Ls = max(s['L_lampe'], s['L_flate'])
    ny = dict(W350=a['W'] * 350 / a['E_felt'], felt=a['E_felt'], jamnheit=a['U'], auge=La, vegg=a['E_vegg'], ansikt=a['E_ansikt'],
              s_auge=Ls, s_vegg=s['E_vegg'], s_felt=s['E_felt'], likskap=lysskisse.likskap(s['_fordeling'], a['_fordeling']),
              topp=m['topp'], sprang=m['sprang'])
    ut = dict(ny=ny, overgang=dict(auge=m['auge'], felt=m['felt'], vegg=m['vegg'], jamn=m['jamn_auke']),
              strekk=max(r['strekk'] for r in R), L_spegl=max(r['L_spegl'] for r in R), skjerm=a['E_skjerm'], skjerm_maks=a['E_skjerm_maks'],
              lm_tak=a['lm_tak'], lm_vegg=a['lm_vegg'], lm=a['lm'], s_lm_tak=s['lm_tak'])
    feil = []
    for k, v in FUNN[namn].items():
        d = avvik(ny[k], v)
        p('  %-9s funn %8.2f  ny %8.2f  avvik %5.1f %%%s' % (k, v, ny[k], d * 100, '  FEIL' if d > 0.05 and abs(ny[k] - v) > 0.015 else ''))
        if d > 0.05 and abs(ny[k] - v) > 0.015: feil.append(k)
    ut['avvik_over_5'] = feil
    p('  overgang auge', [round(x) for x in m['auge']], 'felt', [round(x) for x in m['felt']], 'vegg', [round(x) for x in m['vegg']])
    p('  strekk %.4f  L_spegl %.0f  skjermflata %.0f (maks %.0f)  lm ut %.0f  lm tak %.0f  lm vegg %.0f' % (ut['strekk'], ut['L_spegl'], ut['skjerm'], ut['skjerm_maks'], ut['lm'], ut['lm_tak'], ut['lm_vegg']))
    for t in (0.0, 1.0):
        lys, kropp = g(t)
        vf = veggflekk(lys, kropp); ge = geometri(lys, lysskisse.AUGE)
        ut['vegg_t%d' % t] = vf; ut['geo_t%d' % t] = ge
        p('  t=%d vegg: sona %.0f  bak skjermen %.0f  ramme rundt %.0f  venstre %.0f  hogre %.0f  topp %.0f lx ved x %.2f, %.0f cm over bordet'
          % (t, vf['sona'], vf['bak'], vf['ramme'], vf['venstre'], vf['hogre'], vf['topp_lx'], vf['topp_x'], vf['topp_z'] * 100))
        p('       geo: ark ymax %.3f  xmin %.3f  kjelde %s  fanga %.2f  over 100 %%: %s  fliser spegla i skjermen %d'
          % (ge['ymax'], ge['xmin'], ge['kp'], ge['fanga'], ge['sum_inn_over_kjelde'], ge['fliser_i_skjerm']))
    # augehøgder
    z0 = float(lysskisse.AUGE[2])
    for dz in (0.25, 0.60):
        lysskisse.AUGE[2] = ZB + dz
        Ra = [tal(*g(float(t))) for t in (0.0, 0.25, 0.5, 0.75, 1.0)]
        L = [max(r['L_lampe'], r['L_flate']) for r in Ra]
        geo = [geometri(g(float(t))[0], lysskisse.AUGE)['fliser_i_skjerm'] for t in (0.0, 0.5, 1.0)]
        ut['auge_%d' % int(dz * 100)] = dict(L=L, spegl=[r['L_spegl'] for r in Ra], i_skjerm=geo)
        p('  auge %d cm: mot auget %s  (maks %.0f, arbeid %.0f, stemning %.0f)  ark spegla i skjermen (t 0, 0,5, 1): %s'
          % (dz * 100, [round(x) for x in L], max(L), L[-1], L[0], geo))
        lysskisse.AUGE[2] = z0
    assert abs(float(lysskisse.AUGE[2]) - z0) < 1e-12
    UT[namn] = ut
    p('  tid %.0f s' % (time.time() - t0))

# SATIN som antaking
VAR = {'sigma6': dict(rd=0.15, rs=0.65, sigma=6.0), 'sigma14': dict(rd=0.15, rs=0.65, sigma=14.0), 'rd0.3': dict(rd=0.30, rs=0.65, sigma=10.0)}
p('=' * 70); p('SATIN som antaking (arbeid t 1 og stemning t 0)')
for vn, side in VAR.items():
    Kv = kand(side)
    for namn, g in Kv.items():
        s = tal(*g(0.0)); a = tal(*g(1.0))
        La = max(a['L_lampe'], a['L_flate']); Ls = max(s['L_lampe'], s['L_flate'])
        r = dict(W350=a['W'] * 350 / a['E_felt'], felt=a['E_felt'], jamnheit=a['U'], vegg=a['E_vegg'], vf=a['E_vegg'] / a['E_felt'],
                 auge=La, s_auge=Ls, s_vegg=s['E_vegg'], s_felt=s['E_felt'], likskap=lysskisse.likskap(s['_fordeling'], a['_fordeling']))
        UT[namn]['satin_' + vn] = r
        p('  %-8s %-11s W350 %.2f felt %4.0f U %.2f vegg %4.0f v/f %.2f auge %5.0f | stemn auge %4.0f felt %3.0f vegg %3.0f | lik %.2f'
          % (vn, namn, r['W350'], r['felt'], r['jamnheit'], r['vegg'], r['vf'], r['auge'], r['s_auge'], r['s_felt'], r['s_vegg'], r['likskap']))
p('tid totalt %.0f s' % (time.time() - t0))
json.dump(UT, open(os.path.join(HER, 'etterproving.json'), 'w', encoding='utf-8'), indent=1, default=float)
