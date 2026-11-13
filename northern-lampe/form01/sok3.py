import json, math, motor as M
from collections import Counter
res = []
for g in (0.0, 0.05, 0.10, 0.15, 0.20):
    for yp in (0.25, 0.30, 0.35, 0.40, 0.45):
        for hp in (0.62, 0.66, 0.70, 0.74):
            for pr in ((0,) if g == 0 else (15, 30, 45, 60)):
                B = dict(M.BASE, g=g, yp=yp, hp=hp, phir=float(pr)); S = M.sok(B); ok, Phi = M.score(S)
                W, Mo = S['work'], S['mood']
                res.append(dict(g=g, yp=yp, hp=hp, phir=pr, ok=ok, Phi=float(Phi), U0=float(W['U0']), Rst=float(Mo['R_stem']),
                                Ev=float(Mo['Ev_stem']), glare=bool(W['glare_ok']), kolli=bool(S['kolli_arb']), veg=S['veg'] is not None,
                                psi_w=math.degrees(W['s']), psi_m=math.degrees(Mo['s']), sving=(len(S['veg']) - 1) * 5 if S['veg'] else -1))
json.dump(res, open('sok3.json', 'w'), indent=1)
ok = [r for r in res if r['ok']]
print(len(res), 'køyrt', len(ok), 'ok')
for r in sorted(ok, key=lambda r: r['Phi'])[:10]: print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})
print('rett beste:', min([r for r in ok if r['g'] == 0], key=lambda r: r['Phi']))
for g in (0.05, 0.10, 0.15, 0.20):
    b = min([r for r in ok if r['g'] == g], key=lambda r: r['Phi']); print('g', g, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in b.items()})
print('fall:', Counter(('kolli ' if r['kolli'] else '') + ('glare ' if not r['glare'] else '') + ('veg ' if not r['veg'] else '') + ('U0' if r['U0'] < 0.4 else '') for r in res if not r['ok']))
