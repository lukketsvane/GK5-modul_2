# -*- coding: utf-8 -*-
"""Faldemotor: parametrar inn, falda ark ut. Bygd på konsept/reflektor/_mal.py.

Eit ark får kreppar (rette linjer i det flate arket). Kvar krepp har plass, retning, vinkel og
radius. Radius 2 mm er ein skarp fald, 20 til 80 mm er ein mjuk fald. Alt er rein bøying,
så strekk skal vere 0. Motoren reknar i tillegg det lysmotoren ikkje reknar:

  rift    : arket heng ikkje saman (kreppar som kryssar utan klipp). Over 0,02 kan det ikkje lagast.
  sk_inn  : del av lyset inn som eigentleg er skugga av ein annan del av arket.
  sk_ut   : del av det spegla lyset som eigentleg treff arket ein gong til.

Arkkoordinatar med opp=(0,1,0) og arket over kjelda: +u peikar mot venstre (mot feltet),
+v mot veggen, framsida ned mot kjelda. Positiv vinkel faldar mot framsida (hol).
"""
import sys, os, math
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HER, '..', '..', 'lysskisse'))
from lysskisse import *

FOT = (0.47, 0.48)            # som i malen: foten står til høgre for skjermen
OPP = (0.0, 1.0, 0.0)         # fast referanse for arkramma, så ho ikkje hoppar når arket vippar
VEGGM = b(0.0, YV, 0.45)      # veggen bak og rundt skjermen
ADR = dict(felt=FELT, vegg=VEGGM, ansikt=AUGE)
SKARP = 0.002

# ------------------------------------------------------------------ geometri

def ramme(normal, rull=0.0):
    """Same ramme som ark() lagar med opp=OPP."""
    ez = nrm(normal); ex0, ey0 = ortho(ez, OPP)
    cr, sr = math.cos(math.radians(rull)), math.sin(math.radians(rull))
    ex = cr * ex0 + sr * ey0
    return ex, np.cross(ez, ex), ez

def _les(kreppar, anker=(0.0, 0.0)):
    """Gjer om kreppar til rekneform, sortert innanfrå og ut frå rotpanelet (det som inneheld ankeret)."""
    K = []; anker = np.array(anker, float)
    for i, k in enumerate(kreppar):
        p = np.array(k['p'], float); th = math.radians(k['ret'])
        d = np.array([math.cos(th), math.sin(th)]); n = np.array([-math.sin(th), math.cos(th)])
        if 'mot' in k:
            if (np.array(k['mot'], float) - p) @ n < 0: n = -n
        elif (p - anker) @ n < 0: n = -n
        a = math.radians(k['vinkel']); R = max(float(k.get('R', SKARP)), 1e-4)
        K.append(dict(i=i, p=p, d=d, n=n, a=a, R=R, w=R * abs(a), avst=float((p - anker) @ n)))
    K.sort(key=lambda x: x['avst'])
    return K

def faldeform(kreppar, anker=(0.0, 0.0)):
    """form(U, V) -> (X, Y, Z) for eit ark med rette kreppar. Rotpanelet (det som inneheld ankeret) ligg i ro.
    krepp = dict(p=(u, v), ret=grader i arkplanet (90 er parallell med v), vinkel=grader, R=radius i meter,
                 mot=(u, v) valfritt punkt på den sida som blir falda)."""
    K = _les(kreppar, anker)
    def f(U, V):
        U = np.asarray(U, float); V = np.asarray(V, float); sh = np.broadcast(U, V).shape
        u0 = np.broadcast_to(U, sh).reshape(-1).copy(); v0 = np.broadcast_to(V, sh).reshape(-1).copy()
        P = np.stack([u0, v0, np.zeros_like(u0)], 1)
        for k in K[::-1]:                                   # ytste krepp først
            if abs(k['a']) < 1e-9: continue
            p, d, n, a, R, w = k['p'], k['d'], k['n'], k['a'], k['R'], k['w']
            sf = (u0 - p[0]) * n[0] + (v0 - p[1]) * n[1]    # plass i det flate arket avgjer kva side
            m = sf > -w / 2
            if not m.any(): continue
            Q = P[m]; sg = 1.0 if a > 0 else -1.0; aa = abs(a)
            s = (Q[:, 0] - p[0]) * n[0] + (Q[:, 1] - p[1]) * n[1] + w / 2
            r = (Q[:, 0] - p[0]) * d[0] + (Q[:, 1] - p[1]) * d[1]
            z = Q[:, 2]
            sone = sf[m] < w / 2
            th = np.clip(s / R, 0, aa)
            s_b = (R - sg * z) * np.sin(th); z_b = sg * R - (R - sg * z) * sg * np.cos(th)
            s_r = R * math.sin(aa) + (s - w) * math.cos(aa) - z * sg * math.sin(aa)
            z_r = sg * R * (1 - math.cos(aa)) + (s - w) * sg * math.sin(aa) + z * math.cos(aa)
            sn = np.where(sone, s_b, s_r) - w / 2; zn = np.where(sone, z_b, z_r)
            P[m] = np.stack([p[0] + sn * n[0] + r * d[0], p[1] + sn * n[1] + r * d[1], zn], 1)
        return P[:, 0].reshape(sh), P[:, 1].reshape(sh), P[:, 2].reshape(sh)
    return f

def panelnr(kreppar, u, v, anker=(0.0, 0.0)):
    """Kva panel ei flis høyrer til: 0 er rota, i + 1 er panelet utanfor krepp i (ytste vinn)."""
    nr = np.zeros(np.shape(u), int)
    for k in _les(kreppar, anker):
        sf = (u - k['p'][0]) * k['n'][0] + (v - k['p'][1]) * k['n'][1]
        nr = np.where(sf > 0, k['i'] + 1, nr)
    return nr

def hjorneklipp(kreppar, anker=(0.0, 0.0)):
    """Klipp for flikar: ei flis som ligg utanfor meir enn éin krepp, er eit hjørne og blir skoren bort."""
    K = _les(kreppar, anker)
    def f(u, v):
        tal_ = np.zeros(np.shape(u), int)
        for k in K:
            tal_ = tal_ + (((u - k['p'][0]) * k['n'][0] + (v - k['p'][1]) * k['n'][1]) > -k['w'] / 2)
        return tal_ <= 1
    return f

def faldark(kjelde, senter, normal, storleik=(0.25, 0.25), kreppar=(), flater=(SATIN,), klipp=None,
            rull=0.0, n=22, bakside=MORK, eigaform=None, anker=(0.0, 0.0)):
    """ark() med faldar og éi overflate per panel. flater[0] er rota, flater[i + 1] panelet utanfor krepp i.
    Legg rift, sk_inn og sk_ut på arket."""
    kreppar = list(kreppar)
    form = eigaform if eigaform is not None else (faldeform(kreppar, anker) if kreppar else None)
    if np.ndim(storleik) == 0: w = h = float(storleik); rund = True
    else: w, h = storleik; rund = False
    nu = int(n); nv = max(2, int(round(n * h / w)))
    U, V = np.meshgrid(np.linspace(-w / 2, w / 2, nu + 1), np.linspace(-h / 2, h / 2, nv + 1), indexing='ij')
    uc = (U[:-1, :-1] + U[1:, 1:]) / 2; vc = (V[:-1, :-1] + V[1:, 1:]) / 2
    hald = np.ones(uc.shape, bool)
    if rund: hald &= uc ** 2 + vc ** 2 <= (w / 2) ** 2
    if klipp is not None: hald &= np.asarray(klipp(uc, vc), bool)
    fl = list(flater) + [flater[0]] * (len(kreppar) + 1 - len(flater))
    nr = panelnr(kreppar, uc, vc, anker)[hald] if kreppar else np.zeros(int(hald.sum()), int)
    side = {key: np.array([fl[j][key] for j in nr], float) for key in ('rd', 'rs', 'sigma')}
    a = ark(kjelde, senter, normal, storleik, form=form, klipp=klipp, n=n, opp=OPP, rull=rull,
            framside=side, bakside=bakside)
    assert len(a.Pf) == int(hald.sum()), 'flisteljinga stemmer ikkje med lysmotoren'
    # rift: arket skal vere samanhengande. To punkt 1 mm frå kvarandre i det flate arket kan ikkje
    # liggje lenger frå kvarandre i rommet. Gjer dei det, er arket rive (kreppar som kryssar utan klipp).
    a.rift = 0.0
    if form is not None:
        h_ = 0.001
        uu = np.arange(-w / 2 + h_ / 2, w / 2, h_); vv = np.arange(-h / 2 + h_ / 2, h / 2, h_)
        UU, VV = np.meshgrid(uu, vv, indexing='ij')
        inne = np.ones(UU.shape, bool)
        if rund: inne &= UU ** 2 + VV ** 2 <= (w / 2) ** 2
        if klipp is not None: inne &= np.asarray(klipp(UU, VV), bool)
        X, Y, Z = form(UU, VV); P = np.stack([X, Y, Z], -1)
        for ax in (0, 1):
            dP = np.linalg.norm(np.diff(P, axis=ax), axis=-1) / h_
            begge = (inne[1:, :] & inne[:-1, :]) if ax == 0 else (inne[:, 1:] & inne[:, :-1])
            if begge.any(): a.rift = max(a.rift, float(dP[begge].max()) - 1.0)
        a.rift = max(a.rift, 0.0) if a.rift > 1e-6 else 0.0
    # sjølvskugge inn og ut (lysmotoren reknar ikkje dette)
    kp = a.kjelder[0].pts[0]; Fl = a.Fl[0]; tot = max(float(Fl.sum()), 1e-12)
    D = a.Pf - kp
    t, _ = a.prim.t_idx(np.broadcast_to(kp, D.shape).copy(), D)
    a.sk_inn = float(Fl[t < 1 - 3e-3].sum() / tot)
    t2, _ = a.prim.t_idx(a.Pf + 2e-3 * a.rr[0], a.rr[0].copy())
    spegl = Fl * a.rs[0]
    a.sk_ut = float(spegl[np.isfinite(t2)].sum() / max(float(spegl.sum()), 1e-12))
    a.nr = nr
    # boydel: del av lyset inn som treff ei bøysone (mellom to panel)
    a.boydel = 0.0
    if kreppar:
        uu = uc[hald]; vv = vc[hald]; isone = np.zeros(len(uu), bool)
        for k in _les(kreppar, anker):
            sf = (uu - k['p'][0]) * k['n'][0] + (vv - k['p'][1]) * k['n'][1]
            isone |= np.abs(sf) < k['w'] / 2
        a.boydel = float(Fl[isone].sum() / tot)
    return a

# ------------------------------------------------------------------ sikting

def sikt(c, n_rot, kp, maal, avstand, hol, rull=0.0, R=SKARP, anker=(0.0, 0.0)):
    """Krepp som gjer at panelet utanfor speglar lyset frå kp mot «maal».
    avstand: frå arksenteret til kreppen (m). hol=True faldar mot framsida, False gjev ei takform.
    Kreppretninga følgjer av adressa, ho er ikkje eit fritt val."""
    ex, ey, ez = ramme(n_rot, rull)
    g = None; aa = 0.0; an = np.array(anker, float); q = an[0] * ex + an[1] * ey
    for _ in range(3):
        pw = c + q
        n2 = nrm(nrm(kp - pw) + nrm(np.asarray(maal, float) - pw))
        ip = n2 - (n2 @ ez) * ez
        if np.linalg.norm(ip) < 1e-9: break
        ip = ip / np.linalg.norm(ip)
        g = np.array([ip @ ex, ip @ ey]); aa = math.degrees(math.acos(np.clip(n2 @ ez, -1, 1)))
        s = -1.0 if hol else 1.0
        qf = an + s * (avstand + 0.05) * g; q = qf[0] * ex + qf[1] * ey
    s = -1.0 if hol else 1.0
    p = an + s * avstand * g
    return dict(p=(float(p[0]), float(p[1])), ret=math.degrees(math.atan2(g[1], g[0])) + 90.0,
                vinkel=(aa if hol else -aa), R=R, mot=(float(p[0] + s * g[0]), float(p[1] + s * g[1])))

def treff(kp, c, n_rot, kreppar, uv, rull=0.0, anker=(0.0, 0.0)):
    """Kvar den spegla midtstrålen frå punktet uv i det flate arket hamnar: (retning, punkt på arket)."""
    ex, ey, ez = ramme(n_rot, rull); f = faldeform(kreppar, anker); e = 1e-4
    def P(u, v):
        X, Y, Z = f(np.array([u]), np.array([v])); return c + X[0] * ex + Y[0] * ey + Z[0] * ez
    p0 = P(*uv); nn = nrm(np.cross(P(uv[0] + e, uv[1]) - P(uv[0] - e, uv[1]), P(uv[0], uv[1] + e) - P(uv[0], uv[1] - e)))
    d = nrm(p0 - kp)
    if d @ nn > 0: nn = -nn
    return d - 2 * (d @ nn) * nn, p0

def still(kp, c, n_rot, kreppar, i, uv, maal, rull=0.0, omrade=(-85, 85), anker=(0.0, 0.0)):
    """Finn vinkelen på krepp i som sender midtstrålen frå uv nærast «maal». Rein geometri, ingen lysrekning."""
    best = (2.0, 0.0)
    for a in np.arange(omrade[0], omrade[1] + 0.5, 1.0):
        kk = [dict(k) for k in kreppar]; kk[i]['vinkel'] = float(a)
        r, p0 = treff(kp, c, n_rot, kk, uv, rull, anker)
        avvik = 1 - r @ nrm(np.asarray(maal, float) - p0)
        if avvik < best[0]: best = (avvik, float(a))
    return best[1]
