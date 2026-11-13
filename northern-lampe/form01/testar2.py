"""Tilleggsprøvar etter første utfall: kanten H8 pressa mot (g = 0,15 var gitterkanten) og djupna H1 opna."""
import math, json, numpy as np
import testar as T, felles as fe
out = {'g': [], 'y0': [], 'gy': []}
for g in np.arange(0.10, 0.4001, 0.05):
    for p2 in (-10, 0, 10):
        B = dict(T.BASE, g=float(g), phi2=float(p2)); S = T.sok(B); W = S['work']
        out['g'].append(dict(g=float(g), phi2=p2, Phi=W['Phi'], U0=W['U0'], ok=W['glare_ok'], Rst=S['mood']['R_stem']))
        print(f"g={g:.2f} phi2={p2:+d} Phi={W['Phi']:.0f} U0={W['U0']:.2f} ok={W['glare_ok']} Rst={S['mood']['R_stem']:.2f}")
for y0 in np.arange(0.40, 0.0999, -0.05):
    B = dict(T.BASE, y0=float(y0)); S = T.sok(B); W = S['work']
    out['y0'].append(dict(y0=float(y0), Phi=W['Phi'], U0=W['U0'], ok=W['glare_ok'], vis=W['vis'], Lap=W['Lap'], phi=math.degrees(W['s']), Rst=S['mood']['R_stem']))
    print(f"y0={y0:.2f} Phi={W['Phi']:.0f} U0={W['U0']:.2f} ok={W['glare_ok']} vis={W['vis']} L={W['Lap']:.0f} phi={math.degrees(W['s']):.0f} Rst={S['mood']['R_stem']:.2f}")
json.dump(out, open('utfall2.json', 'w'), indent=1, default=float)
