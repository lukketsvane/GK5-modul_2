import json, math, motor as M
res = []
for g in (0.03, 0.05, 0.08):
    for yp in (0.20, 0.25, 0.30):
        for hp in (0.56, 0.58, 0.60):
            for pr in (30, 45, 60):
                B = dict(M.BASE, g=g, yp=yp, hp=hp, phir=float(pr)); S = M.sok(B); ok, Phi = M.score(S)
                W, Mo = S['work'], S['mood']
                res.append(dict(g=g, yp=yp, hp=hp, phir=pr, ok=ok, Phi=float(Phi), U0=float(W['U0']), Rst=float(Mo['R_stem']),
                                glare=bool(W['glare_ok']), kolli=bool(S['kolli_arb']), veg=S['veg'] is not None,
                                psi_w=math.degrees(W['s']), psi_m=math.degrees(Mo['s'])))
json.dump(res, open('sok2.json', 'w'), indent=1)
ok = [r for r in res if r['ok']]
print(len(res), 'køyrt', len(ok), 'ok')
for r in sorted(ok, key=lambda r: r['Phi'])[:8]: print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})
from collections import Counter
print('fall:', Counter(('kolli' if r['kolli'] else '') + ('glare' if not r['glare'] else '') + ('veg' if not r['veg'] else '') + ('U0' if r['U0'] < 0.4 else '') for r in res if not r['ok']))
