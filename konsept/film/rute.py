# -*- coding: utf-8 -*-
"""
rute.py  ·  filmen som lysande rute: eit flatt, kvitt hus med dioder, og filmen som framside

Dette er lampa på dei to bileta frå 13.11: ei rute på ein arm (pult) og ei rute som tak over bordet (over).
Lyset i huset er diffust. Filmen slepper noko gjennom og kastar resten attende i huset, der det blir spreidd
på nytt (rho). Fordelinga ut av ruta kjem frå strålesporinga i film.py, ikkje frå ei antaking.

    ford = utfordeling(FILM, innside='flat')            # prisma ut mot rommet (slik arket sit i ein monitor)
    l = rute(senter, ut_normal, riller, (0.30, 0.19), W * 100, K, ford)

  python rute.py fordeling     kva dei ulike arkoppsetta gjer med lyset
  python rute.py tal           dei to lampene mot krava, til rute-tal.json
  python rute.py bilete        stemning og arbeid for dei beste
"""
import os, sys, math, json
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
sys.path.insert(0, os.path.join(HER, '..', 'lysskisse'))
import lysskisse as ls
from film import Film, prisme
b, YV, FELT, watt, nrm = ls.b, ls.YV, ls.FELT, ls.watt, ls.nrm

FILM = Film(prisme(90.0), n_d=1.59, abbe=30.0)      # ANTAKING til arket er målt
NLAT, NLON = 60, 120                                  # 3° ruter: pol langs rillene, lon = 0 er rett ut

def _lambert(n, forteikn, rng):
    u = rng.random(n); ph = 2 * math.pi * rng.random(n); r = np.sqrt(u)
    return np.stack([r * np.cos(ph), r * np.sin(ph), forteikn * np.sqrt(1 - u)], 1)

def utfordeling(film=FILM, innside='flat', rho=0.90, n=400000, runder=14, lag2=None, frø=3):
    """Fordelinga ut av ei rute med filmen som framside. innside: sida av filmen som vender inn mot huset.
    rho: del av det attendekasta lyset som huset sender ut att (kvit plast om lag 0,9). film=None: berre ein matt spreiar.
    lag2='kryss': eit ark til utanpå, med rillene på tvers (slik to ark ligg i ein monitor).
    Gjev dict(tab [NLAT, NLON] per steradian per lumen inn, verknad)."""
    rng = np.random.default_rng(frø)
    tab = np.zeros((NLAT, NLON))
    if film is None:
        D = _lambert(n, 1.0, rng); w = np.ones(n) * 0.90        # matt spreiar, ANTAKING 90 % gjennom
        _samle(tab, D, w)
        return dict(tab=tab / n / _romvinkel(), verknad=0.90, namn='spreiar')
    s = 1.0 if innside == 'flat' else -1.0                      # filmkoordinatar: flatsida er z = 0, lyset går mot +z
    w = np.ones(n)
    for _ in range(runder):
        D = _lambert(n, s, rng)
        U, st = film.spor(D, lam=550.0)
        gj = st == 1
        if lag2 == 'kryss' and gj.any():
            # ark nummer to: same film, rillene dreidde 90° (byt x og y)
            V = U[gj][:, [1, 0, 2]]
            U2, st2 = film.spor(V, lam=550.0)
            U2 = U2[:, [1, 0, 2]]
            ok = st2 == 1
            idx = np.flatnonzero(gj)
            _samle(tab, U2[ok] * [1, 1, s], w[idx[ok]])
            gj2 = np.zeros(n, bool); gj2[idx[ok]] = True
            w = np.where(gj2, 0.0, w * rho)                     # det som ikkje kom gjennom begge, går attende i huset
        else:
            _samle(tab, U[gj] * [1, 1, s], w[gj])
            w = np.where(gj, 0.0, w * rho)
        if w.sum() < 1e-3 * n: break
    tab = tab / n / _romvinkel()
    return dict(tab=tab, verknad=float((tab * _romvinkel()).sum()), namn='%s inn%s' % (innside, ' + kryss' if lag2 else ''))

def _romvinkel():
    lat = (np.arange(NLAT) + 0.5) / NLAT * math.pi - math.pi / 2
    return (np.cos(lat) * (math.pi / NLAT) * (math.pi / NLON))[:, None] * np.ones((1, NLON))

def _samle(tab, U, w):
    """U i rutekoordinatar: x på tvers av rillene, y langs, z ut."""
    U = U[U[:, 2] > 1e-9]; w = w[-len(U):] if len(w) != len(U) else w
    lat = np.arcsin(np.clip(U[:, 1], -1, 1)); lon = np.arctan2(U[:, 0], U[:, 2])
    ia = np.clip(((lat + math.pi / 2) / math.pi * NLAT).astype(int), 0, NLAT - 1)
    io = np.clip(((lon + math.pi / 2) / math.pi * NLON).astype(int), 0, NLON - 1)
    np.add.at(tab, (ia, io), w)

def tettleik(ford, x, y, z):
    """Lys per steradian per lumen inn, i retningar gjevne i rutekoordinatar (z ut)."""
    lat = np.arcsin(np.clip(y, -1, 1)); lon = np.arctan2(x, np.maximum(z, 1e-9))
    fa = (lat + math.pi / 2) / math.pi * NLAT - 0.5; fo = (lon + math.pi / 2) / math.pi * NLON - 0.5
    a0 = np.clip(np.floor(fa).astype(int), 0, NLAT - 2); o0 = np.clip(np.floor(fo).astype(int), 0, NLON - 2)
    ta = np.clip(fa - a0, 0, 1); to = np.clip(fo - o0, 0, 1)
    t = ford['tab']
    v = (1 - ta) * (1 - to) * t[a0, o0] + (1 - ta) * to * t[a0, o0 + 1] + ta * (1 - to) * t[a0 + 1, o0] + ta * to * t[a0 + 1, o0 + 1]
    return np.where(z > 0, v, 0.0)

def profil(ford, akse='tvers'):
    """Lysstyrke per lumen inn langs éin akse, kvar 10. grad frå 0 til 80. tvers: på tvers av rillene. langs: langs rillene."""
    v = np.radians(np.arange(0, 90, 10))
    if akse == 'tvers': return tettleik(ford, np.sin(v), 0 * v, np.cos(v))
    return tettleik(ford, 0 * v, np.sin(v), np.cos(v))

def rute(senter, ut, riller, storleik, lm_inn, K, ford, namn='rute'):
    """Ruta som strøk. ut: retninga den lysande sida peikar. riller: retninga rillene går.
    storleik: (på tvers av rillene, langs rillene) i meter. lm_inn: lumen frå diodene i huset."""
    c = np.asarray(senter, float); ez = nrm(ut); ey = np.asarray(riller, float); ey = nrm(ey - (ey @ ez) * ez); ex = np.cross(ey, ez)
    bx, by = storleik; A = bx * by
    prim = ls.Rekt(c - ex * bx / 2 - ey * by / 2, ex * bx, ey * by)
    pts = ls._prover_rekt(c, ex, ey, bx, by)
    I = lambda d: lm_inn * tettleik(ford, d @ ex, d @ ey, d @ ez)
    L = lambda d: I(d) / (A * np.maximum(d @ ez, 0.05))
    l = ls.Lys(lm_inn, K, prim, pts, I, L, namn)
    l.mater = True; l.lm_ut = lm_inn * ford['verknad']
    return l

# ------------------------------------------------------------------ dei to lampene

def _rot(v, akse, vinkel):
    akse = nrm(akse); c, s = math.cos(vinkel), math.sin(vinkel)
    return v * c + np.cross(akse, v) * s + akse * (akse @ v) * (1 - c)

def lampe(bjelke, langs, ut0, djupn=0.19, lengd=0.30, ford=None, riller='bjelke', vinkel=(0.0, 0.0), fot=None, bakstripe=0.0, stripe_n=(0.0, 1.0, -0.3)):
    """Ei rute som heng i ein bjelke og vippar om han. bjelke: midten av bjelken. langs: retninga bjelken går.
    ut0: retninga den lysande sida peikar når vinkelen er 0. vinkel: (stemning, arbeid) i grader om bjelken.
    riller: 'bjelke' (rillene langs bjelken) eller 'tvers'. bakstripe: del av watten til ei diodestripe på bjelken, vend mot veggen.
    Gjev lysgrep g(t)."""
    bj = np.asarray(bjelke, float); la = nrm(langs); ut0 = nrm(np.asarray(ut0, float) - (np.asarray(ut0, float) @ la) * la)
    e0 = np.cross(la, ut0)                                   # retninga ruta strekkjer seg frå bjelken
    def g(t):
        W, K = watt(t)
        v = math.radians(vinkel[0] + (vinkel[1] - vinkel[0]) * float(t))
        ut = _rot(ut0, la, v); e = _rot(e0, la, v)
        c = bj + e * djupn / 2
        r = la if riller == 'bjelke' else e
        st = (djupn, lengd) if riller == 'bjelke' else (lengd, djupn)
        l = rute(c, ut, r, st, (1 - bakstripe) * W * ls.LMW_KJELDE, K, ford)
        lys = [l]
        if bakstripe > 0:      # ei smal stripe dioder på bjelken, vend mot veggen: held veggen bak skjermen lys i arbeid
            sn = nrm(stripe_n)
            fl = ls.flate(bj + sn * 0.014, sn, (lengd, 0.02), bakstripe * W * ls.LMW_KJELDE * 0.9, K, opp=(0, 0, 1))
            fl.lm_ut = fl.lm; fl.lm = bakstripe * W * ls.LMW_KJELDE; fl.mater = True
            lys.append(fl)
        bak = ls.Rekt(c - ut * 0.012 - la * lengd / 2 - e * djupn / 2, la * lengd, e * djupn)       # huset: svart bakside
        kropp = [bak, ls.syl(bj - la * lengd / 2, bj + la * lengd / 2, 0.012)]
        if fot is not None:
            kropp += [ls.syl(b(fot[0], fot[1], 0.0), bj, 0.008), ls.skive(b(fot[0], fot[1], 0.004), (0, 0, 1), 0.10)]
        return lys, kropp
    return g

def rekn(g, n=5):
    R, m = ls.overgang(g, n=n)
    s, a = R[0], R[-1]
    f = 350.0 / max(a['E_felt'], 1e-9)
    La = lambda d: max(d['L_lampe'], d['L_flate'])
    return dict(W350=a['W'] * f, felt_5W=a['E_felt'], jamnheit=a['U'], verknad=a['lm'] / (a['W'] * 100),
                bak350=a['E_bak'] * f, vegg350=a['E_vegg'] * f, ansikt350=a['E_ansikt'] * f, skjerm350=a['E_skjerm'] * f,
                auge25=max(a['L_auge25'], a['L_flate']) * f, auge47=La(a) * f, auge60=max(a['L_auge60'], a['L_flate']) * f,
                spegl350=a['L_spegl'] * f,
                s_felt=s['E_felt'], s_bak=s['E_bak'], s_vegg=s['E_vegg'], s_ansikt=s['E_ansikt'], s_skjerm=s['E_skjerm'],
                s_auge25=max(s['L_auge25'], s['L_flate']), s_auge47=La(s), s_auge60=max(s['L_auge60'], s['L_flate']),
                likskap=ls.likskap(s['_fordeling'], a['_fordeling']), topp=m['topp'], sprang=m['sprang'],
                veg_auge=[La(r) for r in R], veg_skjerm=[r['E_skjerm'] for r in R], veg_felt=[r['E_felt'] for r in R])

def linje(namn, r):
    return ('%-34s W350 %5.1f  U %.2f  bak350 %4.0f  skjerm350 %4.0f  ansikt350 %4.0f  auge350 %5.0f/%5.0f/%5.0f  spegl %5.0f | '
            'stemning: bak %3.0f vegg %3.0f ansikt %3.0f auge %4.0f/%4.0f/%4.0f | likskap %.2f sprang %.2f topp %.2f'
            % (namn, r['W350'], r['jamnheit'], r['bak350'], r['skjerm350'], r['ansikt350'], r['auge25'], r['auge47'], r['auge60'], r['spegl350'],
               r['s_bak'], r['s_vegg'], r['s_ansikt'], r['s_auge25'], r['s_auge47'], r['s_auge60'], r['likskap'], r['sprang'], r['topp']))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    a = sys.argv[1:]
    if not a or a[0] == 'fordeling':
        print('Lysstyrke per 1000 lm inn (cd), kvar 10. grad frå rett ut til 80°. Matt flate med same lumen: %.0f cd rett ut.' % (1000 / math.pi))
        for namn, kw in (('matt spreiar', dict(film=None)), ('prisma ut', dict(innside='flat')), ('prisma inn', dict(innside='prisme')),
                         ('to ark i kryss, prisma ut', dict(innside='flat', lag2='kryss'))):
            f = utfordeling(**kw)
            print('\n%s: verknad %.2f' % (namn, f['verknad']))
            print('  på tvers av rillene: ' + ' '.join('%4.0f' % (1000 * x) for x in profil(f, 'tvers')))
            print('  langs rillene:       ' + ' '.join('%4.0f' % (1000 * x) for x in profil(f, 'langs')))
