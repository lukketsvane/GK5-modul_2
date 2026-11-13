# -*- coding: utf-8 -*-
"""
ruta.py  ·  Ruta: ei fast, lysande rute over skjermkanten, og ei diode som teiknar eit vindauge på veggen

Ein bjelke står over skjermkanten, 50 cm over bordet og 5 cm bak skjermplanet. Framover frå bjelken går ruta
(45 x 19 cm): eit flatt, kvitt hus med dioder og spreiar, og prismefilmen ytst med rillene mot brukaren.
På baksida av bjelken sit ei lita diode bak ei maske (og eventuelt eit stykke film). Ho kastar eit vindauge på veggen.

Ingenting svingar. Overgangen er ein knott: vindauget lyser heile vegen, og ruta kjem inn frå null.
(Framlegget med ei rute som svingar frå bak skjermen til tak, gjekk gjennom skjermkanten og er vraka.)

  python ruta.py vindauge     vindauget på veggen: open maske og med film, til vindauge-ruta.png
  python ruta.py tal          tala som for A, B og C, til tal-D.json
  python ruta.py ark [px]     konseptark til ark-D-ruta.png
"""
import os, sys, math, json
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
from kast import Kast, maske, kartbilete, ls
from film import Film, prisme
from rute import rute, utfordeling, FILM
from vindauge import attprojiser
b, YV, FELT, watt, nrm = ls.b, ls.YV, ls.FELT, ls.watt, ls.nrm

BJELKE = b(0.0, 0.50, 0.50)
VINDAUGE = dict(x0=-0.27, x1=0.27, h0=0.26, h1=0.86, kol=2, rad=3, sprosse=0.09)     # på veggen, mest over skjermen
_FORD = {}
def ford(k='ut'):
    if k not in _FORD:
        _FORD[k] = utfordeling(film=None) if k == 'matt' else utfordeling(innside='flat')
    return _FORD[k]

def ruter(v=VINDAUGE):
    ut = []
    bx = (v['x1'] - v['x0']) / v['kol']; bh = (v['h1'] - v['h0']) / v['rad']
    sx = bx * v['sprosse'] / 2; sh = bh * v['sprosse'] / 2
    for i in range(v['kol']):
        for j in range(v['rad']):
            x0 = v['x0'] + i * bx + sx; x1 = v['x0'] + (i + 1) * bx - sx
            h0 = v['h0'] + j * bh + sh; h1 = v['h0'] + (j + 1) * bh - sh
            ut.append([b(x0, YV, h0), b(x1, YV, h0), b(x1, YV, h1), b(x0, YV, h1)])
    return ut

def vindaugsdiode(W, K, film=None, riller=(1, 0, 0), N=2_000_000, opplaus=0.5, diode=0.001, a=0.012, mavst=0.010, v=VINDAUGE):
    """Dioden på baksida av bjelken: 12 mm bak ei ramme, maska 10 mm framfor dioden. Teiknar vindauget på veggen 18 cm unna."""
    led = BJELKE + np.array([0.0, 0.016, 0.0])
    mot = b(0.5 * (v['x0'] + v['x1']), YV, 0.5 * (v['h0'] + v['h1']))
    akse = nrm(mot - led); u, w = ls.ortho(akse)
    opn = attprojiser(ruter(v), led, led + mavst * akse, akse, u, w)
    return Kast(led, mot, W, K, film=film, riller=riller, side='flat', a=a, diode=diode, film_storleik=(0.07, 0.07),
                masker=[maske(mavst, opn)], N=N, opplaus=opplaus, namn='vindauge')

def kropp(c, ut, e, lengd, djupn):
    la = np.array([1.0, 0.0, 0.0])
    bak = ls.Rekt(c - ut * 0.012 - la * lengd / 2 - e * djupn / 2, la * lengd, e * djupn)
    return [bak, ls.syl(BJELKE - la * lengd / 2, BJELKE + la * lengd / 2, 0.012),
            ls.syl(b(0.31, 0.50, 0.0), b(0.31, 0.50, 0.50), 0.006), ls.skive(b(0.31, 0.50, 0.004), (0, 0, 1), 0.07)]

def g_ruta(v=190.0, lengd=0.45, djupn=0.19, q=0.2, W_s=1.25, fk='ut', film=None, riller=(1, 0, 0), N=2_000_000, opplaus=0.5):
    """v: vinkelen på ruta (180 er rett ned, 190 er 10° framover). q: del av watten til vindauget i arbeid.
    W_s: watt til vindauget i stemning. fk: 'ut' (filmen, prisma ut) eller 'matt'. film: film framfor vindaugsdioden, eller None."""
    vr = math.radians(v)
    ut = np.array([0.0, math.sin(vr), math.cos(vr)]); e = np.array([0.0, math.cos(vr), -math.sin(vr)])
    c = BJELKE + e * djupn / 2
    kr = kropp(c, ut, e, lengd, djupn)
    def g(t):
        W, K = watt(t)
        Wv = W_s * (q * 5.0 / W_s) ** float(t)            # vindauget: frå W_s i stemning til q · 5 W i arbeid
        Wv = min(Wv, W); Wp = W - Wv
        k = vindaugsdiode(Wv, K, film, riller, N, opplaus); g.siste = k
        lys = k.lys()
        if Wp > 0.02:
            lys.append(rute(c, ut, e, (lengd, djupn), Wp * ls.LMW_KJELDE, K, ford(fk)))
        return lys, kr
    return g

def rekn(g, n=5):
    """Same nøklar som tre.rekn, så tala kan stå i same tabell som A, B og C."""
    R, m = ls.overgang(g, n=n)
    s, a = R[0], R[-1]
    f = 350.0 / max(a['E_felt'], 1e-9)
    La = lambda d: max(d['L_lampe'], d['L_flate'])
    return dict(konsept='D', namn='Ruta', W350=a['W'] * f, timar=ls.CELLE / (a['W'] * f), jamnheit=a['U'],
                vegg350=a['E_vegg'] * f, bak350=a['E_bak'] * f, ansikt350=a['E_ansikt'] * f, skjerm350=a['E_skjerm'] * f,
                auge25=max(a['L_auge25'], a['L_flate']) * f, auge47=La(a) * f, auge60=max(a['L_auge60'], a['L_flate']) * f,
                s_W=s['W'], s_felt=s['E_felt'], s_vegg=s['E_vegg'], s_bak=s['E_bak'], s_skjerm=s['E_skjerm'],
                s_auge25=max(s['L_auge25'], s['L_flate']), s_auge47=La(s), s_auge60=max(s['L_auge60'], s['L_flate']),
                likskap=ls.likskap(s['_fordeling'], a['_fordeling']), topp=m['topp'], sprang=m['sprang'], jamn_auke=m['jamn_auke'],
                veg_felt=[r['E_felt'] for r in R], veg_auge=[La(r) for r in R], veg_skjerm=[r['E_skjerm'] for r in R], strekk=0.0)

def linje(namn, r):
    return ('%-26s W350 %4.1f  U %.2f  bak350 %4.0f  skjerm350 %4.0f  ansikt350 %3.0f  auge350 %5.0f/%4.0f/%4.0f | '
            'stemning: bak %3.0f felt %2.0f auge %4.0f | likskap %.2f sprang %.2f topp %.2f'
            % (namn, r['W350'], r['jamnheit'], r['bak350'], r['skjerm350'], r['ansikt350'], r['auge25'], r['auge47'], r['auge60'],
               r['s_bak'], r['s_felt'], max(r['s_auge25'], r['s_auge47'], r['s_auge60']), r['likskap'], r['sprang'], r['topp']))

SETNING = 'Ei lysande rute over skjermkanten legg lyset på feltet. Prismefilmen frå ein monitor held ho mørk mot auget. Ei diode bak ei maske teiknar eit vindauge på veggen.'
HANDLING = 'Handlinga: vri knotten. Vindauget lyser heile vegen, ruta kjem inn.'

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    a = sys.argv[1:]
    if a and a[0] == 'vindauge':
        from PIL import Image
        ims = []
        for namn, f, ri in (('open', None, (1, 0, 0)), ('film-vassrett', FILM, (1, 0, 0)), ('film-loddrett', FILM, (0, 0, 1))):
            k = vindaugsdiode(1.25, 2200, f, ri, N=40_000_000, opplaus=0.25)
            print(namn, {x: round(float(y), 3) for x, y in k.rekneskap.items()}, 'maks %.0f lx' % (k.kart_vegg @ ls.LUM).max(), flush=True)
            # utsnitt av veggen: x -0,6..0,6, frå bordet til 1,0 m over
            kart = k.kart_vegg[25:275, 100:400]
            ims.append(Image.fromarray(kartbilete(kart, 120)))
        W, H = ims[0].size
        ark = Image.new('RGB', (W * 3 + 40, H), (0, 0, 0))
        for i, im in enumerate(ims): ark.paste(im, (i * (W + 20), 0))
        ark.save(os.path.join(HER, 'vindauge-ruta.png')); print(ark.size)
    elif a and a[0] == 'tal':
        ut = {}
        for namn, kw in (('ruta v190 q0.2', {}), ('ruta v185 q0.2', dict(v=185.0)), ('ruta v180 q0.2', dict(v=180.0)),
                         ('ruta v190 q0.15', dict(q=0.15)), ('ruta v190 matt', dict(fk='matt'))):
            r = rekn(g_ruta(**kw), n=5 if not kw else 3); ut[namn] = r; print(linje(namn, r), flush=True)
        json.dump(ut, open(os.path.join(HER, 'tal-ruta-sok.json'), 'w', encoding='utf-8'), indent=1, default=float)
    elif a and a[0] == 'ark':
        sys.path.insert(0, os.path.join(HER, '..', 'lysskisse'))
        import studie
        px = int(a[1]) if len(a) > 1 else 560
        kw = json.load(open(os.path.join(HER, 'val-D.json'), encoding='utf-8')) if os.path.exists(os.path.join(HER, 'val-D.json')) else {}
        g = g_ruta(N=30_000_000, opplaus=0.25, **kw)
        r = studie.konseptark('D  Ruta', SETNING, g, fil=os.path.join(HER, 'ark-D-ruta.png'), px=px, ss=1, handling=HANDLING)
        print('ferdig', {x: round(float(v), 2) for x, v in r.items() if isinstance(v, (int, float))})
