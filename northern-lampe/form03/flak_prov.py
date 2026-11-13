"""Rask prøve: flak (lysande lok) hengsla bak/over skjermen. α: 0 = ned, 90 = mot brukaren, 180+ = opp/bak."""
import sys, math, numpy as np
sys.path.insert(0, '..'); import felles as fe
ETA, PK, SYN = 0.70, 1.3, 15.0
ALFA = list(np.radians(np.arange(-30, 231, 5)))
def flak(B, a, n=None):
    f = np.array([0, -math.cos(a), math.sin(a)]); nn = np.array([0, -math.sin(a), -math.cos(a)])
    H = np.array([0, B['yh'], B['zh']])
    ks, kb = 12, 5
    xs = (np.arange(ks) + .5) / ks * B['L'] - B['L'] / 2
    ss = (np.arange(kb) + .5) / kb * B['b']
    P = np.array([H + [x, 0, 0] + s * f for x in xs for s in ss])
    return P, np.tile(nn, (len(P), 1)), np.full(len(P), B['L'] / ks * B['b'] / kb)
def kolli(B, a, work):
    f = np.array([-math.cos(a), math.sin(a)])
    pts = np.array([[B['yh'], B['zh']] + s * B['b'] * f for s in np.linspace(0, 1, 9)])
    if (pts[:, 0] > 0.73).any() or ((pts[:, 0] < 0.50) & (pts[:, 1] < 0.50)).any(): return True
    if ((pts[:, 0] > 0.43) & (pts[:, 0] < 0.49) & (pts[:, 1] < 0.44)).any(): return True
    if work:
        e = fe.EYES[0]; el = np.degrees(np.arctan2(pts[:, 1] - e[2], pts[:, 0] - e[1]))
        if (el < SYN).any(): return True
    return False
out = []
for yh in (0.50, 0.56):
    for zh in (0.56, 0.60, 0.64, 0.68):
        for b in (0.18, 0.25, 0.32):
            B = dict(L=0.60, b=b, yh=yh, zh=zh)
            S = fe.sok(B, ALFA, flak, ETA, ring=False); rows = S['rows']
            for r in rows:
                r['Lap'] = r['k'] * r['Phi'] * PK
                r['glare_ok'] = (not r['vis'] or r['Lap'] <= fe.L_MAX) and (not r['refl'] or r['Lap'] <= fe.L_MAX)
            fw = [r for r in rows if r['glare_ok'] and r['U0'] >= 0.4 and not kolli(B, r['s'], True)]
            if not fw: out.append((yh, zh, b, None)); continue
            W = min(fw, key=lambda r: r['Phi'])
            fm = [r for r in rows if not kolli(B, r['s'], False) and ((not r['vis'] and not r['refl']) or r['k'] * W['Phi'] * .25 * PK <= 1000)]
            M = max(fm, key=lambda r: (r['R_stem'] >= .5, r['Ew']))
            F = max([r for r in rows if not kolli(B, r['s'], False)], key=lambda r: r['face'])
            out.append((yh, zh, b, dict(Phi=W['Phi'], U0=W['U0'], Lw=W['Lap'], vis=W['vis'], aw=math.degrees(W['s']), am=math.degrees(M['s']), Rst=M['R_stem'],
                                        Ev=M['Ew'] * W['Phi'] * .25, af=math.degrees(F['s']), L150=150 / F['face'] * PK, Phi150=150 / F['face'] / F['k'])))
for yh, zh, b, r in out:
    print(yh, zh, b, '-' if r is None else {k: (round(float(v), 2) if not isinstance(v, (bool, np.bool_)) else bool(v)) for k, v in r.items()})
