# -*- coding: utf-8 -*-
"""
vindauge.py  ·  varmt vindauge utan linse: diode, maske og film i same rom og med same tal som A, B og C

Hovudet står over hjørnet på skjermen (som C). Ei lita diode lyser gjennom ei maske og ein prismefilm.
Filmen deler strålen i to lober, om lag 31° til kvar side av aksen. Den eine lobe teiknar vindauget på veggen bak
skjermen, den andre legg lyset på feltet. Vinkelen mellom veggen og feltet, sett frå hovudet, er om lag 60°:
det er vinkelen filmen deler med.

Tre grep for overgangen:
  vipp     filmen vippar om rilleaksen. Det flyttar lyset mellom dei to lobene (frå om lag 4:1 til 1:4).
  spjeld   filmen står fast. Eit spjeld opnar for bordloben. Kvar lobe har si eiga opning (vindauge og felt).
  open     ingen film: berre maske. Hovudet vippar frå veggen ned på feltet (samanlikningsgrunnlag).

  python vindauge.py tal            tal for dei tre grepa, til tal.md
  python vindauge.py bilete [grep]  stemning og arbeid side om side
  python vindauge.py kart [grep]    lux-kart på vegg og bord (png og npy) til rendrar
"""
import os, sys, math, json
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
from kast import Kast, maske, rekt, vindauge, kartbilete, ls
from film import Film, prisme
b, YV, FELT, watt, nrm = ls.b, ls.YV, ls.FELT, ls.watt, ls.nrm

HOVUD = b(0.40, 0.42, 0.65)            # filmsenteret: over høgre skjermhjørne, 3 cm framfor skjermplanet
FOT = (0.40, 0.50)
VINDAUGE = dict(x0=-0.36, x1=0.20, h0=0.16, h1=0.74, kol=2, rad=3, sprosse=0.10)    # på veggen bak skjermen
FELTRUTE = (-0.30, 0.30, 0.05, 0.45)   # arbeidsfeltet på bordet
FILM = Film(prisme(90.0), n_d=1.59, abbe=30.0)      # ANTAKING til arket er målt: ideelt 90°-prisme

def rot(v, akse, vinkel):
    akse = nrm(akse); c, s = math.cos(vinkel), math.sin(vinkel)
    return v * c + np.cross(akse, v) * s + akse * (akse @ v) * (1 - c)

def retningar(pos=HOVUD, vegg=None, felt=None):
    """Aksen (halveringa mellom vegg og felt), rilleretninga og halve vinkelen mellom måla."""
    vegg = b(0.5 * (VINDAUGE['x0'] + VINDAUGE['x1']), YV, 0.5 * (VINDAUGE['h0'] + VINDAUGE['h1'])) if vegg is None else vegg
    felt = FELT if felt is None else felt
    dv = nrm(vegg - pos); df = nrm(felt - pos)
    return nrm(dv + df), nrm(np.cross(df, dv)), 0.5 * math.degrees(math.acos(float(dv @ df))), dv, df

def vindaugsruter(v=VINDAUGE):
    """Rutene i vindauget som firkantar på veggen (romkoordinatar)."""
    ut = []
    bx = (v['x1'] - v['x0']) / v['kol']; bh = (v['h1'] - v['h0']) / v['rad']
    sx = bx * v['sprosse'] / 2; sh = bh * v['sprosse'] / 2
    for i in range(v['kol']):
        for j in range(v['rad']):
            x0 = v['x0'] + i * bx + sx; x1 = v['x0'] + (i + 1) * bx - sx
            h0 = v['h0'] + j * bh + sh; h1 = v['h0'] + (j + 1) * bh - sh
            ut.append([b(x0, YV, h0), b(x1, YV, h0), b(x1, YV, h1), b(x0, YV, h1)])
    return ut

def feltfirkant(r=FELTRUTE):
    return [[b(r[0], r[2], 0), b(r[1], r[2], 0), b(r[1], r[3], 0), b(r[0], r[3], 0)]]

def attprojiser(firkantar, kjelde, plan_c, plan_n, plan_u, plan_v, H=None, akse=None, vinkel=0.0):
    """Finn opningane i eit maskeplan som gjev desse firkantane i rommet, sett frå ei punktkjelde.
    Med film mellom maska og rommet: drei rompunkta attende om filmsenteret H (akse = rillene, vinkel = avbøyinga)."""
    ut = []
    for q in firkantar:
        pk = []
        for X in q:
            X = np.asarray(X, float)
            if H is not None and vinkel != 0.0: X = H + rot(X - H, akse, -vinkel)
            d = X - kjelde
            t = ((plan_c - kjelde) @ plan_n) / (d @ plan_n)
            P = kjelde + t * d - plan_c
            pk.append((float(P @ plan_u), float(P @ plan_v)))
        ut.append(pk)
    return ut

def kropp(pos, n, fot=FOT, r=0.035, l=0.11):
    """Det auget ser: hovudet som ein kort sylinder bak filmen, og ei stong ned til foten. Skuggar ikkje strålen."""
    h = ls.Syl(pos - l * n, pos - 0.004 * n, r); h.spoke = True
    return [h, ls.syl(b(fot[0], fot[1], 0.0), b(fot[0], fot[1], (pos - l * n)[2] - ls.ZB), 0.005),
            ls.skive(b(fot[0], fot[1], 0.004), (0, 0, 1), 0.06)]

def lobevinklar(film, vipp, lam=550.0):
    """Dei to sterkaste lobene når lyset kjem inn mot prismesida, vippa «vipp» grader. Gjev [(avbøying frå strålen i grader, del)]."""
    T, R, L = film.lober(abs(vipp), 0.0, lam, 'prisme', n=60000)
    s = 1.0 if vipp >= 0 else -1.0
    return T, [(s * (a - abs(vipp)), d) for a, d in L[:2]]

# ------------------------------------------------------------------ grepa

def g_vipp(film=FILM, vipp=(-28.0, 24.0), a=0.05, diode=0.002, led='lambert', N=2_000_000, opplaus=0.5, pos=HOVUD,
           maskeavstand=0.044, storleik=(0.07, 0.07), ruter=None):
    """Filmen vippar om rilleaksen frå vipp[0] (stemning: veggen sterkast) til vipp[1] (arbeid: feltet sterkast).
    Maska står mellom dioden og filmen og er teikna frå vindauget på veggen i stemning."""
    akse, riller, halv, dv, df = retningar(pos)
    led_pos = pos - a * akse
    u, v = ls.ortho(akse)
    # kva veg må filmen vippe for at veggloben skal bli sterkast? Prøv begge.
    def normal(vp):
        return rot(-akse, riller, math.radians(vp))
    def veggdel(vp):
        D, st = film.gjennom(np.tile(akse, (20000, 1)), normal(vp), riller)
        D = D[st == 1]
        return float(((D @ dv) > (D @ df)).mean()) if len(D) else 0.0
    forteikn = 1.0 if veggdel(abs(vipp[0])) > veggdel(-abs(vipp[0])) else -1.0
    v0 = forteikn * abs(vipp[0]); v1 = -forteikn * abs(vipp[1])
    # avbøyinga til veggloben i stemning, målt frå sporinga
    D, st = film.gjennom(np.tile(akse, (40000, 1)), normal(v0), riller)
    D = D[st == 1]; Dv = D[(D @ dv) > (D @ df)]
    mv = nrm(Dv.mean(0)); avb = math.atan2(float(np.cross(akse, mv) @ riller), float(akse @ mv))
    opn = attprojiser(vindaugsruter() if ruter is None else ruter, led_pos, led_pos + maskeavstand * akse, akse, u, v, pos, riller, avb)
    def g(t):
        W, K = watt(t)
        vp = v0 + (v1 - v0) * float(t)
        k = Kast(led_pos, pos, W, K, film=film, riller=riller, film_normal=normal(vp), a=a, diode=diode, led=led,
                 film_storleik=storleik, masker=[maske(maskeavstand, opn)], N=N, opplaus=opplaus, namn='vipp')
        g.siste = k
        return k.lys(), kropp(pos, akse)
    g.info = dict(grep='vipp', halvvinkel=halv, vipp=(v0, v1), avboying=math.degrees(avb), opningar=opn, maskeavstand=maskeavstand)
    return g

def g_spjeld(film=FILM, a=0.05, diode=0.002, led='lambert', N=2_000_000, opplaus=0.5, pos=HOVUD, plate=0.05,
             storleik=(0.036, 0.05), q1=1.0, ruter=None):
    """Filmen står fast, rett på strålen. Ei plate 5 cm etter filmen har to opningar: vindauget (veggloben) og
    feltet (bordloben). Eit spjeld opnar feltopninga frå 0 (stemning) til q1 (arbeid)."""
    akse, riller, halv, dv, df = retningar(pos)
    led_pos = pos - a * akse
    u, v = ls.ortho(akse)
    T, L = lobevinklar(film, 0.0)
    avb = math.radians(abs(L[0][0]))
    # kva forteikn går mot veggen?
    sv = 1.0 if (rot(akse, riller, avb) @ dv) > (rot(akse, riller, -avb) @ dv) else -1.0
    kv = pos + rot(led_pos - pos, riller, sv * avb)          # biletet av dioden for veggloben
    kf = pos + rot(led_pos - pos, riller, -sv * avb)         # og for bordloben
    pc = pos + plate * akse
    opn_v = attprojiser(vindaugsruter() if ruter is None else ruter, kv, pc, akse, u, v)
    opn_f = attprojiser(feltfirkant(), kf, pc, akse, u, v)[0]
    def g(t):
        W, K = watt(t)
        q = q1 * float(t)
        opn = list(opn_v)
        if q > 0.01:
            # spjeldet opnar frå den kanten som ligg lengst frå vindaugsopninga
            (p0, p1, p2, p3) = [np.array(p) for p in opn_f]
            opn.append([tuple(p0), tuple(p1), tuple(p1 + q * (p2 - p1)), tuple(p0 + q * (p3 - p0))])
        k = Kast(led_pos, pos, W, K, film=film, riller=riller, side='prisme', a=a, diode=diode, led=led,
                 film_storleik=storleik, masker=[maske(a + plate, opn, etter=True)], N=N, opplaus=opplaus, namn='spjeld')
        g.siste = k
        return k.lys(), kropp(pos, akse)
    g.info = dict(grep='spjeld', halvvinkel=halv, avboying=math.degrees(avb), opn_vindauge=opn_v, opn_felt=opn_f, plate=plate)
    return g

def g_open(a=0.05, diode=0.002, led='lambert', N=2_000_000, opplaus=0.5, pos=HOVUD, maskeavstand=0.044, storleik=(0.07, 0.07)):
    """Utan film: skuggemaske åleine. Hovudet vippar frå vindauget på veggen ned på feltet. Maska er teikna frå vindauget."""
    akse, riller, halv, dv, df = retningar(pos)
    led0 = pos - a * dv
    u0, v0 = ls.ortho(dv)
    opn = attprojiser(vindaugsruter(), led0, led0 + maskeavstand * dv, dv, u0, v0)
    def g(t):
        W, K = watt(t)
        n = nrm(rot(dv, riller, -math.radians(2 * halv) * float(t)))
        if (n @ df) < (dv @ df) and t > 0: n = nrm(rot(dv, riller, math.radians(2 * halv) * float(t)))
        k = Kast(pos - a * n, pos, W, K, film=None, riller=riller, a=a, diode=diode, led=led, film_storleik=storleik,
                 masker=[maske(maskeavstand, opn, opp=None)], N=N, opplaus=opplaus, namn='open')
        g.siste = k
        return k.lys(), kropp(pos, n)
    g.info = dict(grep='open', halvvinkel=halv, opningar=opn, maskeavstand=maskeavstand)
    return g

GREP = {'vipp': g_vipp, 'spjeld': g_spjeld, 'open': g_open}

# ------------------------------------------------------------------ tal (same som tre.rekn)

def rekn(g, n=5):
    R, m = ls.overgang(g, n=n)
    s, a = R[0], R[-1]
    f = 350.0 / max(a['E_felt'], 1e-9)
    La = lambda d: max(d['L_lampe'], d['L_flate'])
    return dict(W350=a['W'] * f, W_arbeid=a['W'], felt_5W=a['E_felt'], jamnheit=a['U'], lm_ut=a['lm'], verknad=a['lm'] / (a['W'] * 100),
                vegg350=a['E_vegg'] * f, bak350=a['E_bak'] * f, bak_5W=a['E_bak'], ansikt350=a['E_ansikt'] * f, skjerm350=a['E_skjerm'] * f,
                auge25=max(a['L_auge25'], a['L_flate']) * f, auge47=La(a) * f, auge60=max(a['L_auge60'], a['L_flate']) * f,
                s_W=s['W'], s_lm=s['lm'], s_felt=s['E_felt'], s_vegg=s['E_vegg'], s_bak=s['E_bak'], s_skjerm=s['E_skjerm'],
                s_auge25=max(s['L_auge25'], s['L_flate']), s_auge47=La(s), s_auge60=max(s['L_auge60'], s['L_flate']),
                likskap=ls.likskap(s['_fordeling'], a['_fordeling']), topp=m['topp'], sprang=m['sprang'], jamn_auke=m['jamn_auke'],
                veg_felt=[r['E_felt'] for r in R], veg_bak=[r['E_bak'] for r in R], veg_skjerm=[r['E_skjerm'] for r in R], veg_W=[r['W'] for r in R])

def linje(namn, r):
    return ('%-22s W350 %6.1f  verknad %.2f  felt(5W) %5.0f lx  U %.2f  bak350 %5.0f  skjerm350 %4.0f  auge350 %6.0f/%6.0f/%6.0f  '
            'stemning: bak %4.0f lx, felt %3.0f, auge %5.0f  likskap %.2f  sprang %.2f'
            % (namn, r['W350'], r['verknad'], r['felt_5W'], r['jamnheit'], r['bak350'], r['skjerm350'], r['auge25'], r['auge47'], r['auge60'],
               r['s_bak'], r['s_felt'], max(r['s_auge25'], r['s_auge47'], r['s_auge60']), r['likskap'], r['sprang']))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    a = sys.argv[1:]
    kven = a[1:] or list(GREP)
    if a and a[0] == 'tal':
        ut = {}
        for k in kven:
            g = GREP[k]()
            r = rekn(g); ut[k] = r
            print(linje(k, r), flush=True)
        json.dump(ut, open(os.path.join(HER, 'tal-grep.json'), 'w', encoding='utf-8'), indent=1, default=float)
    elif a and a[0] == 'bilete':
        for k in kven:
            g = GREP[k](N=30_000_000, opplaus=0.25)
            ls.par(g, os.path.join(HER, 'par-%s.png' % k), px=480, ss=1, steg=(0.0, 1.0))
            print('par-%s.png' % k, flush=True)
    elif a and a[0] == 'kart':
        from PIL import Image
        for k in kven:
            g = GREP[k](N=60_000_000, opplaus=0.25)
            for t, m in ((0.0, 'stemning'), (1.0, 'arbeid')):
                g(t); K = g.siste
                np.save(os.path.join(HER, 'kart-%s-%s-vegg.npy' % (k, m)), K.kart_vegg.astype(np.float32))
                np.save(os.path.join(HER, 'kart-%s-%s-bord.npy' % (k, m)), K.kart_bord.astype(np.float32))
                Image.fromarray(kartbilete(K.kart_vegg, 80)).save(os.path.join(HER, 'kart-%s-%s-vegg.png' % (k, m)))
                Image.fromarray(kartbilete(K.kart_bord, 200)).save(os.path.join(HER, 'kart-%s-%s-bord.png' % (k, m)))
                print(k, m, K.rekneskap, flush=True)
