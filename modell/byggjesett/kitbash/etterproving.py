# -*- coding: utf-8 -*-
"""etterproving.py · bandet rekna ein gong til med uavhengig kode (ikkje lysmotoren)

Strålesporing med numpy: ei lambertsk line (LED-stripa) under ein ideell fresnelspegel (flat plate med normalane til
ein paraboloide, f = 187,1 mm), speglinga landar på bordet. Ingen vegg, ingen skjerm, ikkje indirekte lys.
Spørsmålet er berre det eine: gjev stripa mot rein plate jamnheit over 0,6 på feltet, og kva skjer med kort stripe,
éi diode og stripa på fot?

  python etterproving.py
"""
import sys, math, json, os
import numpy as np

F = 0.1871; S = 0.285; FAS = 0.037
RNG = np.random.default_rng(7)


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def spor(c, kp, maal, halv, langs, kutt=50.0, spreiing=2.5, N=1_500_000, treff=False):
    """c: senter i plata. kp: midt på stripa. maal: punktet midtstrålen skal treffe. halv: halve stripelengda langs «langs».
    Gjev lux-kart på feltet (per lumen frå stripa), delen som treffer plata og delen som landar på feltet.
    treff=True gjev i staden punkta der lyset landar på bordet, og talet på strålar."""
    c, kp, maal = (np.asarray(x, float) for x in (c, kp, maal))
    a = unit(kp - c); til = unit(maal - c); nn = unit(a + til)
    u = unit(np.cross(nn, np.cross(a, til))) if np.linalg.norm(np.cross(a, til)) > 1e-9 else unit(np.cross(nn, [0, 1, 0]))
    v = np.cross(nn, u)
    l = unit(langs)
    s = kp + np.outer(RNG.uniform(-halv, halv, N), l)
    # lambertsk om aksen frå stripa mot plata, skoren ved «kutt»
    d0 = -a; e1 = unit(np.cross(d0, l)); e2 = np.cross(d0, e1)
    sm = math.sin(math.radians(kutt)); st = sm * np.sqrt(RNG.uniform(0, 1, N)); ct = np.sqrt(1 - st * st); ph = RNG.uniform(0, 2 * math.pi, N)
    d = ct[:, None] * d0 + (st * np.cos(ph))[:, None] * e1 + (st * np.sin(ph))[:, None] * e2
    t = ((c - s) @ nn) / (d @ nn); p = s + t[:, None] * d
    pu = (p - c) @ u; pv = (p - c) @ v
    paa = (t > 0) & (np.abs(pu) <= S / 2) & (np.abs(pv) <= S / 2) & ((S / 2 - np.abs(pu)) + (S / 2 - np.abs(pv)) >= FAS)
    p, d, pu, pv = p[paa], d[paa], pu[paa], pv[paa]
    n = unit(nn[None, :] - (pu / (2 * F))[:, None] * u - (pv / (2 * F))[:, None] * v)      # normalane til paraboloiden
    r = d - 2 * np.sum(d * n, 1)[:, None] * n
    if spreiing:                                                                           # litt spreiing i plata
        g = RNG.normal(0, math.radians(spreiing), (len(r), 2)); b1 = unit(np.cross(r, [1.0, 0.3, 0.2])); b2 = np.cross(r, b1)
        r = unit(r + g[:, :1] * b1 + g[:, 1:] * b2)
    ned = r[:, 2] < -1e-6
    tt = -p[ned, 2] / r[ned, 2]; q = p[ned] + tt[:, None] * r[ned]
    if treff:
        return q, N
    kart = {}
    for nx, ny in ((6, 4), (12, 8), (15, 10)):
        H, _, _ = np.histogram2d(q[:, 0], q[:, 1], bins=[nx, ny], range=[[-0.30, 0.30], [0.05, 0.45]])
        E = H * 0.85 / N / ((0.6 / nx) * (0.4 / ny))                # lux per lumen frå stripa, spegelen 0,85
        kart[(nx, ny)] = E
    inne = (np.abs(q[:, 0]) <= 0.30) & (q[:, 1] >= 0.05) & (q[:, 1] <= 0.45)
    return kart, float(paa.mean()), float(inne.sum() * 0.85 / N)


def linje(namn, kart, plate, felt):
    U = {k: float(E.min() / E.mean()) for k, E in kart.items()}
    E = kart[(6, 4)]
    print('%-34s jamnheit 6×4 %.2f · 12×8 %.2f · 15×10 %.2f · %.2f lx per lm · plata fangar %2.0f %% · feltet får %2.0f %%'
          % (namn, U[(6, 4)], U[(12, 8)], U[(15, 10)], E.mean(), plate * 100, felt * 100), flush=True)
    return dict(namn=namn, U_6x4=U[(6, 4)], U_12x8=U[(12, 8)], U_15x10=U[(15, 10)], lx_per_lm=float(E.mean()), plate=plate, felt=felt)


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    c = np.array([0.0, 0.36, 0.62]); a = unit([0.0, 0.40, -0.90]); kp = c + 0.12 * a; felt = np.array([0.0, 0.25, 0.0])
    ut = []
    ut.append(linje('stripe 24 cm, rein plate', *spor(c, kp, felt, 0.12, (1, 0, 0))))
    ut.append(linje('stripe 24 cm, utan spreiing', *spor(c, kp, felt, 0.12, (1, 0, 0), spreiing=0.0)))
    ut.append(linje('stripe 12 cm, rein plate', *spor(c, kp, felt, 0.06, (1, 0, 0))))
    ut.append(linje('éi diode, rein plate', *spor(c, kp, felt, 0.001, (1, 0, 0))))
    ut.append(linje('éi diode, ark 12°', *spor(c, kp, felt, 0.001, (1, 0, 0), spreiing=12.0)))
    ut.append(linje('stripe 30 cm, rein plate', *spor(c, kp, felt, 0.15, (1, 0, 0))))
    cf = np.array([0.44, 0.36, 0.47]); kf = np.array([0.44, 0.41, 0.05])
    rr = unit(np.cross(unit(kf - cf), unit(felt - cf)))
    ut.append(linje('på fot: stripe 20 cm, 42 cm under', *spor(cf, kf, felt, 0.10, rr, kutt=24.0)))
    json.dump(ut, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'etterproving.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
