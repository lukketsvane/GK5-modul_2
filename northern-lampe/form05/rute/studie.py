# -*- coding: utf-8 -*-
"""studie.py  ·  lysstudie.png for Lysrute: éin kropp stor på svart, med lyset på bordet og fargen i ruta.

Ein liten strålekastar utan skuggar: ruta lyser med luminansen frå motoren (per bølgjelengd, så cut-off-bandet får farge),
stripene frå stemningsrekkja ligg oppå, og bordet får lux frå ruta. Kroppen får lys frå ruta.
  python -B studie.py [T|K]
"""
import os, sys, math, json
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
import motor as m
ls = m.ls
FONT = r'C:\Windows\Fonts\georgiai.ttf'
FONT_R = r'C:\Windows\Fonts\georgia.ttf'

def kamera(pos, mot, fov, n):
    C = np.asarray(pos, float); f = m.nrm(np.asarray(mot, float) - C)
    r = m.nrm(np.cross(f, (0, 0, 1))); u = np.cross(r, f); h = math.tan(math.radians(fov / 2))
    x = ((np.arange(n) + 0.5) / n * 2 - 1) * h
    X, Y = np.meshgrid(x, -x)
    D = f + X[..., None] * r + Y[..., None] * u
    D = D.reshape(-1, 3); D /= np.linalg.norm(D, axis=1)[:, None]
    return C, D

def E_fraa(ruter, P, N, nu=14, nv=6):
    """Lux i punkta P med normal N frå rutene, utan skuggar."""
    E = np.zeros(len(P))
    for r in ruter:
        S = r.punkt(nu, nv); w = 1.0 / len(S)
        for s in S:
            d = P - s; r2_ = np.maximum((d * d).sum(1), 1e-6); dn = d / np.sqrt(r2_)[:, None]
            c = np.maximum(-(dn * N).sum(1), 0)
            E += r.I(dn) * w * c / r2_
    return E

def bilete(spec, t, W, n, stripe=None, Lref=30.0):
    ruter, kropp = m.bygg(spec, t, W=W)
    K = ruter[0].K
    kam = m.KAMERA[[k for k, v in m.KROPPAR.items() if v['namn'] == spec['namn']][0]]
    C, D = kamera(kam['pos'], kam['mot'], kam['fov_grader'], n)
    O = np.broadcast_to(C, D.shape).copy()
    bord = ls.Rekt((-0.7, 0, ls.ZB), (1.4, 0, 0), (0, 0.7, 0))
    prims = [bord] + list(kropp) + [ls.Rekt(r.o, r.ex * r.w, r.ey * r.h) for r in ruter]
    tmin = np.full(len(O), np.inf); idx = np.full(len(O), -1)
    for k, p in enumerate(prims):
        tt = p.t(O, D); s = tt < tmin; tmin[s] = tt[s]; idx[s] = k
    hdr = np.zeros((len(O), 3))
    farge = ls.farge(K)
    rgbw = np.clip(m._cmf(m.LAMS) @ m.XYZ_RGB.T, 0, None) * m.planck(m.LAMS, K)[:, None]
    nb = 1 + len(kropp)
    for k, p in enumerate(prims):
        s = np.flatnonzero(idx == k)
        if not len(s): continue
        P = O[s] + tmin[s, None] * D[s]; V = -D[s]
        if k >= nb:                                     # ruta
            r = ruter[k - nb]
            L = r.L(V)
            fram = (V @ r.ez) > 0
            u, v = V @ r.ex, V @ r.ey
            Ll = np.array([m.oppslag(r.motor['tab_l'][i], u, v) for i in range(len(m.LAMS))])
            rgb = Ll.T @ rgbw; rgb0 = rgbw.sum(0) * (m.vekter(K) @ Ll)[:, None] / m.vekter(K).sum()
            mod = np.where(fram[:, None], rgb / np.maximum(rgb0, 1e-12), 1.0)
            mod = mod / np.maximum(mod @ ls.LUM, 1e-9)[:, None]
            if stripe is not None:
                xs, ys, Ls = stripe
                a = (P - r.o) @ r.ex; bb = (P - r.o) @ r.ey
                ia = np.clip((a / r.w * (len(xs) - 1)).astype(int), 0, len(xs) - 1)
                ib = np.clip((bb / r.h * (len(ys) - 1)).astype(int), 0, len(ys) - 1)
                L = np.where(fram, L * Ls[ia, ib], L)
            hdr[s] = (L[:, None] * farge[None]) * mod
            kant = (np.minimum.reduce([((P - r.o) @ r.ex) / r.w, 1 - ((P - r.o) @ r.ex) / r.w,
                                       ((P - r.o) @ r.ey) / r.h, 1 - ((P - r.o) @ r.ey) / r.h]) < 0.008)
            hdr[s[kant]] *= 1.6                         # den lysande kanten på plata
            continue
        N = p.normal(P); N = np.where(((N * D[s]).sum(1) > 0)[:, None], -N, N)
        E = E_fraa(ruter, P, N)
        rho = np.array([0.42, 0.30, 0.20]) if k == 0 else p.rho
        hdr[s] = rho[None] * (E[:, None] * farge[None] / math.pi + 0.15)
        if k == 0:                                      # bordet fell mot svart utanfor lyset
            hdr[s] *= np.clip(1.2 - np.abs(P[:, 0]) / 0.7, 0, 1)[:, None] ** 0.5
    hdr = hdr.reshape(n, n, 3)
    h = hdr.copy()
    for vekt, sig in ((0.06, 0.008), (0.035, 0.03), (0.015, 0.09)):
        h += vekt * gaussian_filter(hdr, sigma=(sig * n, sig * n, 0))
    Y = h @ ls.LUM
    Yt = Y / (Y + Lref)
    img = h * (Yt / np.maximum(Y, 1e-9))[..., None] * 1.15
    return (np.clip(img, 0, 1) ** (1 / 2.2) * 255 + 0.5).astype(np.uint8), ruter

def polar(dr, ruter_a, ruter_s, x0, y0, R, f):
    """Lysstyrke i planet y-z gjennom ruta (sett frå sida): arbeid kvit, stemning rav. Kvar kurve er normert til sin topp."""
    th = np.radians(np.arange(0, 360, 2.0))
    d = np.stack([0 * th, -np.sin(th), -np.cos(th)], 1)      # 0 = rett ned, 90 = mot brukaren
    dr.ellipse([x0 - R, y0 - R, x0 + R, y0 + R], outline=(60, 60, 60))
    dr.line([x0 - R, y0, x0 + R, y0], fill=(45, 45, 45)); dr.line([x0, y0 - R, x0, y0 + R], fill=(45, 45, 45))
    for ruter, farge, namn in ((ruter_a, (235, 228, 215), 'arbeid'), (ruter_s, (230, 150, 70), 'stemning')):
        I = sum(r.I(d) for r in ruter); top = I.max()
        pts = [(x0 + R * I[i] / top * (-d[i, 1]) * -1, y0 + R * I[i] / top * (-d[i, 2])) for i in range(len(th))]
        pts = [(x0 - R * I[i] / top * d[i, 1], y0 - R * I[i] / top * d[i, 2]) for i in range(len(th))]
        dr.line(pts + [pts[0]], fill=farge, width=2)
    dr.text((x0 - R, y0 + R + 8), 'lysstyrke sett frå sida, normert', font=f, fill=(140, 140, 140))
    dr.text((x0 - R, y0 + R + 30), 'brukaren til venstre, veggen til høgre', font=f, fill=(110, 110, 110))

def lag(kv='T'):
    spec = m.KROPPAR[kv]
    ek = m.les('ekstra_' + kv, {})
    Wa = m.les('rekn_' + kv, {}).get('W350', 3.0)
    st = m.stripekart(spec['ruter'][0]['w'], spec['ruter'][0]['h'], m.STRIPER['pitch'], m.STRIPER['sigma'])
    n = 1000; na = 420
    imS, ruter_s = bilete(spec, 0.0, None, n, stripe=st)
    imA, ruter_a = bilete(spec, 1.0, Wa, na, Lref=60.0)
    ark = Image.new('RGB', (n + na + 60, n), (0, 0, 0))
    ark.paste(Image.fromarray(imS), (0, 0)); ark.paste(Image.fromarray(imA), (n + 30, 70))
    dr = ImageDraw.Draw(ark)
    f1 = ImageFont.truetype(FONT, 34); f2 = ImageFont.truetype(FONT, 19); f3 = ImageFont.truetype(FONT, 16)
    dr.text((40, 34), 'Lysrute · %s' % spec['namn'], font=f1, fill=(225, 220, 210))
    S = ek.get('stemning', {}); A = ek.get('arbeid', {})
    dr.text((40, 84), 'stemning · 2200 K · 1,25 W · %s lm ut av ruta' % f'{sum(r.phi_ut for r in ruter_s):.0f}',
            font=f2, fill=(220, 160, 95))
    dr.text((n + 30, 34), 'arbeid · 2700 K · %.1f W · %.0f lm ut' % (Wa, sum(r.phi_ut for r in ruter_a)), font=f2, fill=(225, 220, 210))
    polar(dr, ruter_a, ruter_s, n + 30 + na // 2, 70 + na + 150, 120, f3)
    y = 70 + na + 330
    rk = m.les('rekn_' + kv, {})
    linjer = []
    if rk:
        linjer += ['350 lx på feltet: %.1f W · jamnheit %.2f' % (rk['W350'], rk['jamnheit']),
                   'mot auget i arbeid: %.0f / %.0f / %.0f cd/m²' % (rk['auge25'], rk['auge47'], rk['auge60']),
                   'skjermflata %.0f lx · bak skjermen %.0f lx' % (rk['skjerm350'], rk['bak350']),
                   'stemning mot auget: %.0f cd/m²' % max(rk['s_auge25'], rk['s_auge47'], rk['s_auge60'])]
    linjer += ['%s, %s' % (m.KJELDE[spec['kjelde']]['namn'], spec['rille'] + ' riller'),
               'rekna, ikkje målt · prismet er ideelt (antaking)']
    for l in linjer:
        dr.text((n + 30, y), l, font=f3, fill=(170, 165, 158)); y += 24
    dr.text((40, n - 46), spec.get('gest', ''), font=f3, fill=(150, 145, 138))
    ark.save(os.path.join(HER, 'lysstudie.png'))
    print('lysstudie.png', ark.size)

if __name__ == '__main__':
    lag(*(sys.argv[1:] or ['T']))
