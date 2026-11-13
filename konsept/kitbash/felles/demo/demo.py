# -*- coding: utf-8 -*-
"""demo.py  ·  prøvelampa som viser at verktøya i ../ heng saman. Ho er ikkje eit framlegg til lampe.

Armen frå projektoren (P01) står i ein trykt fot. På tappen som hovudet dreidde på, sit eit trykt nav med ei kjøpt
aluminiumsplate, og under plata ein kjøpt LED-modul. Gesten er å vippe plata om tappen: ned mot bordet er arbeid,
135° bakover mot veggen er stemning.

  python demo.py sjekk          kollisjon, masse, velt, varme, trykk, STL og GLB  -> sjekk.json, sjekk.md
  python demo.py prove          scener.json og små prøverendrar av samla, sprengt og delbank
  python demo.py full           samla i full storleik (tek nokre minutt, køyr i bakgrunnen)
  python demo.py studie [px]    lysstudien -> studie.png (px 560 er full, 300 er prøve)

Alle tal er rekna, ikkje målt. Måla på delane frå settet er anslag frå foto.
"""
import os, sys
sys.dont_write_bytecode = True
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HER, '..'))
import numpy as np
from kit import *            # sett, trykt, kjopt, plass, T, Rx, Ry, Rz, om, klaring, formene, led_skive ...
import kit as K

FOT_D, FOT_H = 180.0, 16.0                       # trykt fot (mm)
BALLAST_D, BALLAST_T = 140.0, 5.0                # kjøpt stålskive i ei utsparing under foten
BOTN = FOT_H                                     # enden av armprofilen står på skiva, inne i hylsa
PLATE = (70.0, 110.0, 2.0)                       # kjøpt aluminiumsplate: ber LED-en og leier varmen bort
VIPP = 135.0                                     # grader plata er vippa bakover i stemning
FOT_I_ROMMET = (0.40, 0.22)                      # midt i foten, meter i bordkoordinatar: rett til høgre for arbeidsfeltet

# Armen står loddrett i foten, med tappen mot venstre (-x, inn mot feltet) og breisida av profilen langs y.
M_ARM = T(0, 0, BOTN - 12.0) @ Rz(-90) @ Ry(-90)


def samling(t=1.0):
    """Lampa i stillinga t: 1 er arbeid (plata vassrett, LED-en ned), 0 er stemning (plata vippa 135° bakover)."""
    arm = sett('P01', M_ARM, spreng=(0, 0, 110))
    A = arm.punkt('hovudakse')                                   # aksen hovudet dreidde på: går langs x gjennom A
    # --- fot (trykt i to delar, så ingen av dei får overheng): skiva med utsparing til ballasten blir trykt opp ned,
    # hylsa som tek armprofilen blir trykt ståande og skrudd på skiva.
    # Opninga i hylsa er sett etter det største profilen kan vere (klaring): måla er anslag frå foto.
    bx = klaring('P01', 'profil_tjukk')['opning']; by = klaring('P01', 'profil_breidd')['opning']
    skive = minus(sylinder(FOT_D, FOT_H), sylinder(BALLAST_D + 2, BALLAST_T + 0.3, -0.01))
    hyl = pluss(hylse(bx, by, 45, vegg=4, z0=FOT_H), minus(boks(bx + 40, by + 40, 3, (0, 0, FOT_H + 1.5), r=6), boks(bx, by, 10, (0, 0, FOT_H))))
    delar = [trykt('fot', skive, plast='PETG', print_R=Rx(180), spreng=(0, 0, 0)),
             trykt('hylse', hyl, plast='PETG', spreng=(0, 0, 35)),
             kjopt('ballast', sylinder(BALLAST_D, BALLAST_T), 'stål', np.pi * (BALLAST_D / 20) ** 2 * BALLAST_T / 10 * 7.85,
                   spreng=(0, 0, -60), merknad='stålskive, masse rekna frå 7,85 g/cm³'),
             arm]
    # --- vippa: nav (trykt), kjøleplate og LED (kjøpte). Teikna rundt aksen (origo, x langs aksen), så dreidd og sett på A.
    Mv = T(*A) @ Rx(VIPP * (1.0 - t))
    hol = klaring('P01', 'tapp_d')['opning']
    langs_x = Ry(90)                                             # sylinder langs z -> langs x
    nav = pluss(flytta(sylinder(24, 15), T(-36, 0, 0) @ langs_x), boks(15, 40, 10, (-28.5, -20, -7)))
    nav = minus(nav, flytta(sylinder(hol, 40), T(-50, 0, 0) @ langs_x))
    bx_, by_, bt = PLATE
    delar += [trykt('nav', nav, Mv, plast='PETG', print_R=Ry(90), spreng=(-50, 0, 110)),
              kjopt('kjoleplate', boks(bx_, by_, bt, (-21 - bx_ / 2, -5 - by_ / 2, -12 - bt / 2)), 'aluminium', bx_ * by_ * bt / 1000 * 2.70, Mv,
                    spreng=(-50, 0, 75), merknad='aluminiumsplate 2 mm, masse rekna frå 2,70 g/cm³'),
              led_skive(40, 1.6, watt=5.0, M=Mv @ T(-21 - bx_ / 2, -5 - by_ / 2, -12 - bt) @ Rx(180), spreng=(-50, 0, 45))]
    return delar


def lyspunkt(delar):
    """Midten av lysflata på LED-en (1 mm utanfor) og retninga ho lyser, i lampa sitt system (mm)."""
    led = K.finn(delar, 'led')
    n = led.retning((0, 0, 1))
    return pkt(led.M, (0, 0, 1.6)) + 1.0 * n, n


def grep(t):
    """Lysgrepet til lysmotoren: g(t) -> (lys, kropp). Same watt som alle andre: watt(t)."""
    import bru
    ls = bru.motor()
    delar = samling(t)
    pl = bru.i_rommet(delar, fot=FOT_I_ROMMET, dreiing=0.0)
    W, Kelvin = ls.watt(t)
    p, n = lyspunkt(delar)
    lys = [ls.flate(pl.p(p), pl.r(n), 0.040, W * ls.LMW, Kelvin)]
    return lys, pl.kropp(delar)


def k_sjekk():
    import sjekk
    dytt = lambda delar: K.finn(delar, 'arm').punkt('hovudakse') + np.array([0, 0, 25.0])       # handa tek i toppen av armen
    def trykk(delar):                                                                            # eller trykkjer plata ned ytst
        kp = K.finn(delar, 'kjoleplate'); b = kp.grenser()
        return np.array([(b[0][0] + b[1][0]) / 2, b[0][1], b[1][2]]), (0, 0, -1.0)
    r = sjekk.rapport(samling, HER, 'demo', stillingar=(0.0, 0.25, 0.5, 0.75, 1.0), dytt=dytt, trykk=trykk)
    print('masse %.0f g ± %.0f, tyngdepunkt %s' % (r['masse']['total_g'], r['masse']['pm_g'], r['masse']['tp_mm']))
    for s in r['stillingar']:
        print('  t %.2f: kollisjonar %s · dytt %.1f N (krav 5: %s) · veltevinkel %.0f° · trykk ned på plata %.1f N' % (
            s['t'], [(c['a'], c['b'], c['volum_mm3']) for c in s['kollisjonar']] or 'ingen', s['velt']['dytt_N'],
            'held' if s['velt']['held'] else 'held ikkje', s['velt']['veltevinkel'], s['trykk']['kraft_N']))
    for h in r['varme']: print('  varme:', h['raad'])
    for p in r['utskrift']: print('  trykk: %s %s mm, %s g, %s' % (p['namn'], p['maal_mm'], p['g'], p['merknad']))
    import bru
    print('  i rommet:', bru.i_rommet(samling(1.0), FOT_I_ROMMET).sjekk(samling(1.0)))
    return r


def k_prove():
    import rendre
    namn = rendre.scener(samling(1.0), HER, 'demo')
    rendre.scener(samling(0.0), HER, 'demo-stemning')
    for b in rendre.koyr(HER, namn, prove=True): print(b)


def k_full():
    import rendre
    rendre.scener(samling(1.0), HER, 'demo')
    for b in rendre.koyr(HER, ['demo-samla']): print(b)


def k_studie(px='560'):
    import studie, json
    ekstra_a, ekstra_s = [], []
    fil = os.path.join(HER, 'sjekk.json')
    if os.path.exists(fil):
        r = json.load(open(fil, encoding='utf-8')); v = r['stillingar'][-1]['velt']
        ekstra_s = ['%s g · fot Ø %.0f mm · veltar ved %s N dytt i toppen (krav 5)%s' % (
            studie._nn(r['masse']['total_g']), FOT_D, studie._nn(v['dytt_N'], 1), '' if v['held'] else ': held ikkje')]
    ut = studie.studie(grep, 'Demo · armen P01 på trykt fot, LED på aluminiumsplate som vippar om tappen', os.path.join(HER, 'studie.png'),
                       px=int(px), ekstra_arbeid=ekstra_a, ekstra_stemning=ekstra_s)
    print({k: round(v, 2) for k, v in ut['arbeid'].items()})
    print('W350 %.1f · likskap %.2f · krav %s' % (ut['W350'], ut['likskap'], ut['krav']))


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    a = sys.argv[1:] or ['sjekk']
    {'sjekk': k_sjekk, 'prove': k_prove, 'full': k_full, 'studie': k_studie}[a[0]](*a[1:])
