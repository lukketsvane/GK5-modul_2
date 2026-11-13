# -*- coding: utf-8 -*-
"""lampe.py  ·  det minste dømet frå ../../LES_MEG.md, køyrt og prøvd. Kopier fila til konsept/kitbash/<lampa di>/.

Armen P01 står i ein trykt fot. På toppen ligg ei kjøpt aluminiumsplate med ein LED-modul under, som lyser ned.
Forma er den same i stemning og arbeid, berre watten endrar seg: dette er eit døme på verktøya, ikkje eit framlegg.

  python lampe.py           kontroll (sjekk.json, sjekk.md, stl/, minste.glb), tre små prøverendrar og lysstudien i prøvestorleik
"""
import os, sys
sys.dont_write_bytecode = True
HER = os.path.dirname(os.path.abspath(__file__))
FELLES = os.path.join(HER, '..', '..')                # frå konsept/kitbash/<lampa di>/ er det os.path.join(HER, '..', 'felles')
sys.path.insert(0, FELLES)
from kit import *
import kit as K, sjekk, rendre, bru, studie

FOT = (0.42, 0.25)                                    # midt i foten i rommet (m): rett til høgre for arbeidsfeltet


def samling(t=1.0):
    """Lampa i stillinga t: 0 er stemning, 1 er arbeid. Alt i mm, z = 0 er bordet."""
    arm = sett('P01', T(0, 0, 4) @ Ry(-90), spreng=(0, 0, 80))           # armen loddrett, profilenden 16 mm over bordet
    b = klaring('P01', 'profil_breidd')['opning']                        # 43 ± 6 mm: opninga tek den største profilen
    s = klaring('P01', 'profil_tjukk')['opning']
    fot = pluss(sylinder(180, 16), hylse(b, s, 40, vegg=4, z0=16))       # trykt fot med hylse rundt profilen
    topp = arm.grenser()[1][2]                                           # høgste punkt på armen
    plate = kjopt('plate', boks(60, 120, 2, (0, -40, topp + 1)), 'aluminium', 60 * 120 * 2 / 1000 * 2.70, spreng=(0, 0, 130))
    led = led_skive(40, watt=5.0, M=T(0, -70, topp) @ Rx(180), spreng=(0, 0, 100))    # under plata, lysflata ned
    return [trykt('fot', fot, plast='PETG'), arm, plate, led]


def grep(t):
    """Lysgrepet til lysmotoren: g(t) -> (lys, kropp)."""
    ls = bru.motor()
    delar = samling(t)
    pl = bru.i_rommet(delar, fot=FOT)                                    # origo i lampa -> b(0.42, 0.25, 0)
    W, Kelvin = ls.watt(t)                                               # 1,25 W og 2200 K i stemning, 5 W og 3000 K i arbeid
    led = K.finn(delar, 'led')
    n = led.retning((0, 0, 1))                                           # lysflata er +z på LED-skiva
    p = pkt(led.M, (0, 0, 1.6)) + 1.0 * n                                # 1 mm utanfor flata, elles skuggar kroppen ho
    return [ls.flate(pl.p(p), pl.r(n), 0.040, W * ls.LMW, Kelvin)], pl.kropp(delar)


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    r = sjekk.rapport(samling, HER, 'minste', dytt=lambda d: K.finn(d, 'arm').punkt('hovudakse'))    # sjekk.json, sjekk.md, stl/, minste.glb
    print('masse %.0f g · dytt %.1f N · varme: %s' % (r['masse']['lampe_g'], r['stillingar'][-1]['velt']['dytt_N'], r['varme'][0]['raad']))
    namn = rendre.scener(samling(1.0), HER, 'minste')                    # scener.json: minste-samla, minste-sprengt, minste-del
    rendre.koyr(HER, namn, prove=True)                                   # render/minste-samla-prove.png og dei to andre
    ut = studie.studie(grep, 'Minste døme · armen P01 på trykt fot, LED under ei aluminiumsplate', os.path.join(HER, 'studie.png'), px=200)
    print('350 lx krev %.1f W · jamnheit %.2f · krav %s' % (ut['W350'], ut['arbeid']['U'], ut['krav']))
