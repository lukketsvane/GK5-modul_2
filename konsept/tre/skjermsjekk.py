# -*- coding: utf-8 -*-
"""
skjermsjekk.py  ·  augevolum, spegling i tilta skjerm og slør for A, B og C

1. Augevolum: lysaste del av lampa sett frå 18 auge (x ±15 cm, 15 cm nærare skjermen, høgd 37 til 57 cm),
   i stemning, midt i overgangen og i arbeid. Skalert til 350 lx på feltet i arbeid, slik tal.md gjer.
2. Spegling: skjermen tilta 0, 5, 10, 15 og 20° bakover om underkanten. Kva ser auget av lampa i skjermen?
   Luminansen i lampa langs speglingsretninga (før reflektansen) skal under 1500 cd/m² (EN 12464-1 for
   skjermar med høg luminans: 3000). Med blank skjerm (ρ 0,04) er det speglande biletet ρ · L.
3. Slør: L = ρ E / π med ρ 0,04. Kontrast (kvit 200 cd/m², svart 0,2) = (200 + L) / (0,2 + L).

  python skjermsjekk.py
"""
import os, sys, math, json
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
import tre
from tre import ls, b
import numpy as np

AUGE0 = ls.AUGE.copy()
AUGEVOLUM = [np.array([AUGE0[0] + dx, AUGE0[1] + dy, ls.ZB + h]) for dx in (-0.15, 0.0, 0.15) for dy in (0.0, 0.15) for h in (0.37, 0.47, 0.57)]

def okkl_av(lys, kropp):
    return [p for p in ls.STATISK + list(kropp) + [l.prim for l in lys] if p not in ls.PERSON]

def L_fraa(punkt, lys, okkl):
    best = 0.0
    for l in lys:
        if isinstance(l, ls.Ark):
            best = max(best, l.L_mot(punkt, okkl)); continue
        for s in l.pts:
            if ls.synleg(punkt[None], s, okkl, l.prim)[0]:
                best = max(best, float(l.L(ls.nrm(punkt - s)[None])[0]))
    return best

def L_langs(O, D, lys, kropp):
    """Luminansen i lampa langs strålane O + tD (det auget ser i spegelen). 0 der strålen ikkje treffer lampa."""
    prims = ls.STATISK + list(kropp) + [l.prim for l in lys]
    prims = [p for p in prims if p is not ls.SKJERM]
    tmin = np.full(len(O), np.inf); kva = np.full(len(O), -1)
    for i, p in enumerate(prims):
        t = p.t(O, D); m = t < tmin; tmin[m] = t[m]; kva[m] = i
    L = np.zeros(len(O))
    for i, p in enumerate(prims):
        m = np.flatnonzero(kva == i)
        if not len(m): continue
        if p.lys is not None:
            L[m] = p.lys.L(-D[m])
        elif isinstance(p, ls.Nett):
            _, tr = p.t_idx(O[m], D[m])
            fi = np.where(tr >= 0, p.flis[np.maximum(tr, 0)], 0)
            L[m] = np.where(tr >= 0, p.ark.L_flis(fi, -D[m]), 0.0)
    return L

def spegling(lys, kropp, tilt, auge):
    """Lysaste del av lampa auget ser i skjermen når han er tilta «tilt» grader bakover om underkanten."""
    z0, z1, x0, x1 = ls.ZB + 0.11, ls.ZB + 0.42, -0.27, 0.27
    a = math.radians(tilt)
    n = np.array([0.0, -math.cos(a), math.sin(a)])            # mot brukaren og litt opp
    opp = np.array([0.0, math.sin(a), math.cos(a)])           # langs skjermen, oppover og bakover
    o = np.array([0.0, 0.45, z0])
    us, vs = np.meshgrid(np.linspace(x0, x1, 28), np.linspace(0, z1 - z0, 16))
    P = o + us.ravel()[:, None] * np.array([1.0, 0, 0]) + vs.ravel()[:, None] * opp
    d_inn = P - auge; d_inn /= np.linalg.norm(d_inn, axis=1)[:, None]
    d_ut = d_inn - 2 * (d_inn @ n)[:, None] * n
    return float(L_langs(P + 1e-4 * d_ut, d_ut, lys, kropp).max())

def kontrast(E):
    L = 0.04 * E / math.pi
    return (200 + L) / (0.2 + L)

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    ut = {}
    for k in 'ABC':
        g = tre.KONSEPT[k]['g']; t_ = json.load(open(os.path.join(HER, f'tal-{k}.json'), encoding='utf-8'))
        a1 = ls.tal(*g(1.0)); f = 350.0 / a1['E_felt']        # same skalering som tal.md (watten i arbeid)
        r = dict()
        for namn, t in (('stemning', 0.0), ('midt', 0.5), ('arbeid', 1.0)):
            lys, kropp = g(t); okkl = okkl_av(lys, kropp)
            skal = f if t > 0 else 1.0                            # stemning står ved sin eigen watt (1,25 W)
            Ls = [L_fraa(p, lys, okkl) * skal for p in AUGEVOLUM]
            r[namn + '_auge_maks'] = max(Ls)
            r[namn + '_spegling'] = {tl: max(spegling(lys, kropp, tl, AUGE0), spegling(lys, kropp, tl, AUGE0 + np.array([0, 0, 0.10]))) * skal for tl in (0, 5, 10, 15, 20)}
        r['kontrast_arbeid'] = kontrast(t_['skjerm350'])
        r['kontrast_verst'] = kontrast(max(t_['veg_skjerm']) * f)
        ut[k] = r
        print(k, 'augevolum maks (stemning / midt / arbeid):', round(r['stemning_auge_maks']), round(r['midt_auge_maks']), round(r['arbeid_auge_maks']))
        for namn in ('stemning', 'midt', 'arbeid'):
            print('   spegling i skjermen,', namn, {tl: round(v) for tl, v in r[namn + '_spegling'].items()})
        print('   kontrast på skjermen: arbeid %.0f:1, verst langs overgangen %.0f:1' % (r['kontrast_arbeid'], r['kontrast_verst']), flush=True)
    json.dump(ut, open(os.path.join(HER, 'skjermsjekk.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
