import json, math, time, motor as M
from collections import Counter
t0 = time.time(); res = []
for par in (True, False):
    for w in (0.24, 0.32):
        for th in (80.0, 120.0):
            for lean in (0.0, 15.0, 25.0):
                for px in (-0.58, -0.46):
                    for py in ((0.25, 0.40) if par else (0.25,)):
                        B = dict(M.BASE, w=w, th=th, lean=lean, px=px, py=py, par=par)
                        S = M.sok(B); W, Mo = S['work'], S['mood']
                        st = M.stab(B, W['s'])[0]
                        res.append(dict(par=par, w=w, th=th, lean=lean, px=px, py=py, ok=bool(S['ok'] and st['tipp_deg'] >= 6), Phi=float(W['Phi']), U0=float(W['U0']),
                                        Ltopp=float(W['Lap']), pk=S['pk'], eta=M.eta(B), glare=bool(W['glare_ok']), Rst=float(Mo['R_stem']), Ev=float(Mo['Ev_stem']),
                                        L150=float(S['L150']), psi_w=math.degrees(W['s']), psi_m=math.degrees(Mo['s']), steg=S['steg'], tipp=st['tipp_deg']))
json.dump(res, open('sok_grovt.json', 'w'), indent=1)
print(f'{time.time()-t0:.0f} s')
f = lambda r: {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()}
for par in (True, False):
    rr = [r for r in res if r['par'] == par]; ok = [r for r in rr if r['ok']]
    print('PAR' if par else 'ÉI BOK', len(rr), 'køyrt', len(ok), 'ok')
    for r in sorted(ok, key=lambda r: r['Phi'])[:6]: print('  ', f(r))
    print('   fall:', Counter(('glare ' if not r['glare'] else '') + ('U0 ' if r['U0'] < 0.4 else '') + ('veg ' if r['steg'] < 0 else '') + ('Rst ' if r['Rst'] < 0.5 else '') + ('tipp' if r['tipp'] < 6 else '') for r in rr if not r['ok']))
    for r in sorted([r for r in rr if not r['ok']], key=lambda r: r['Phi'])[:3]: print('   lågast Phi utan ok:', f(r))
