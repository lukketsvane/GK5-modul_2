# -*- coding: utf-8 -*-
"""demo.py  ·  prøvelampa som viser at verktøya i ../ heng saman. Ho er ikkje eit framlegg til lampe.

Armen frå projektoren (P01) står i ein trykt fot. På tappen som hovudet dreidde på, sit eit trykt nav med ei kjøpt
aluminiumsplate, og under plata ein kjøpt LED-modul. Gesten er å vippe plata om tappen: ned mot bordet er arbeid,
135° bakover mot veggen er stemning.

  python demo.py sjekk          kollisjon, masse, velt, varme, trykk, STL og GLB  -> sjekk.json, sjekk.md
  python demo.py prove          scener.json og små prøverendrar av samla, sprengt og delbank
  python demo.py full           samla i full storleik (tek nokre minutt, køyr i bakgrunnen)
  python demo.py studie [px]    lysstudien -> studie.png (px 560 er full, 300 er prøve)
  python demo.py sett           alle delane frå settet og eit filmstykke gjennom verktøya: massetabell og prøverendring
  python demo.py kryss          fresnelplata P05 gjennom kit og bru, mot talet til søkjebrettet (modell/byggjesett/kitbash)

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
    for b in rendre.koyr(HER, namn + ['demo-stemning-samla'], prove=True): print(b)


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


def settbenk():
    """Alle delane som kan brukast (P01, P02, P03, P05, P06, P07) og eit filmstykke klipt av P08, lagde ut på eit bord."""
    h = lambda pid, k: K.D.v(pid, k)
    return [sett('P05', T(0, 0, 0)),
            sett('P01', T(-120, 240, h('P01', 'kappe_hogd') / 2)),
            sett('P02', T(-250, 240, h('P02', 'hogd') / 2)),
            sett('P03', T(240, 240, h('P03', 'hogd') / 2)),
            sett('P06', T(215, 70, 0)),
            sett('P07', T(225, -40, 0)),
            film(200, 120, T(-235, 0, 60 * np.sin(np.radians(75))) @ Rz(90) @ Ry(75), namn='filmstykke'),
            trykt('trykt kloss 40', boks(40, 40, 40, (0, 0, 20)), T(225, -140, 0)),
            led_skive(40, watt=5.0, M=T(170, -140, 0))]


def k_sett():
    """Viser at kvar del i settet lastar, held materiala sine, får ein masse og kan rendrast. P04 og P09 er sperra."""
    import sjekk, rendre
    for pid in ('P04', 'P09'):
        try:
            sett(pid); print('FEIL: %s vart ikkje stoppa' % pid)
        except ValueError as e:
            print('  sperra:', e)
    delar = settbenk()
    m = sjekk.masse(delar)
    print('  masse per del (rekna frå anslåtte mål, usikker til delane er vegne):')
    for r in m['rader']:
        print('    %-18s %-6s %7.0f g ± %-4.0f %s' % (r['namn'], r['pid'] or r['slag'], r['g'], r['pm_g'], r['kjelde'][:90]))
    arm = K.finn(delar, 'arm')
    print('    armen om profilen er stål: %.0f g' % sjekk.masse(K.med_staalarm([arm]))['total_g'])
    kol = sjekk.kollisjonar(delar)
    print('  kollisjonar på benken:', [(c['a'], c['b'], c['volum_mm3']) for c in kol] or 'ingen')
    namn = rendre.scener(delar, HER, 'sett', elevasjon=32)
    for b in rendre.koyr(HER, ['sett-samla'], prove=True): print(b)


def k_kryss():
    """Fresnelplata P05 plassert med kit og sett i rommet med bru, mot «over-vipp» i modell/byggjesett/kitbash/tal_lys.json
    (plata over skjermkanten, diode i brønn 50 grader på skjermkanten, diffusorark 12 grader, plata vend mot feltet)."""
    import json, bru, studie
    ls = bru.motor()
    c = ls.b(0.0, 0.36, 0.62); a = ls.nrm((0.0, 0.40, -0.90)); kp = c + 0.12 * a           # som fre.OVER_C, OVER_A i reflektor/fresnel/familie.py
    pl = bru.i_rommet(fot=(0.0, 0.0))                                                      # lampa sitt system = bordet sitt, i mm
    mm = lambda P: (np.asarray(P) - ls.b(0, 0, 0)) * 1000.0
    def plate_i(mot):
        til = ls.nrm(mot - c); n = ls.nrm(a + til); y = ls.nrm(np.cross(a, til)); x = np.cross(y, n)
        R = np.stack([x, y, n], 1)                                                         # +z i delen (spegelsida) -> n
        t_sp = sett('P05').anker['spegelflate'][2]
        return sett('P05', plass(mm(c) - R @ np.array([0, 0, t_sp]), R))
    def grep(attekant, kropp_nett):
        def g(t):
            W, Kel = ls.watt(t)
            plate = plate_i(ls.b(0.0, ls.YV, 0.60) * (1 - t) + ls.FELT * t)
            k = ls.straale(pl.p(mm(kp)), pl.p(plate.punkt('spegelflate')), W * ls.LMW_KJELDE, Kel, spreiing=40, kutt=50, opning=0.02, bronn=50)
            lys = [k, pl.fresnel(plate, k, spreiing=12, n=16, attekant=attekant)]          # n = 16 fliser som i søket
            return lys, (pl.kropp([plate]) if kropp_nett else [])                          # søkjebrettet rekna «over-vipp» utan kropp
        return g
    brett = json.load(open(os.path.join(K.SETT, 'kitbash', 'tal_lys.json'), encoding='utf-8'))['over-vipp']
    print('  %-50s W350 %5.2f  U %.2f  bak350 %5.1f  skjerm350 %5.1f  ansikt350 %5.1f  auge %4.0f/%4.0f/%4.0f  s_bak %5.1f' % (
        'søkjebrettet (tal_lys.json, over-vipp)', brett['W350'], brett['jamnheit'], brett['bak350'], brett['skjerm350'], brett['ansikt350'],
        brett['auge25'], brett['auge47'], brett['auge60'], brett['s_bak']))
    ut = {}
    for namn, g in (('kit + bru, heil firkant, utan kropp', grep(False, False)), ('kit + bru, skorne hjørne, utan kropp', grep(True, False)),
                    ('kit + bru, skorne hjørne, plate og ramme som nett', grep(True, True))):
        R = studie.rekn(g); v = R['ved350']
        print('  %-50s W350 %5.2f  U %.2f  bak350 %5.1f  skjerm350 %5.1f  ansikt350 %5.1f  auge %4.0f/%4.0f/%4.0f  s_bak %5.1f' % (
            namn, R['W350'], R['arbeid']['U'], v['bak350'], v['skjerm350'], v['ansikt350'], v['auge25'], v['auge47'], v['auge60'], R['stemning']['E_bak']))
        ut[namn] = dict(W350=R['W350'], jamnheit=R['arbeid']['U'], **{k_: v[k_] for k_ in ('bak350', 'skjerm350', 'ansikt350', 'auge25', 'auge47', 'auge60')},
                        s_bak=R['stemning']['E_bak'])
    ut['søkjebrettet'] = {k_: brett[k_] for k_ in ('W350', 'jamnheit', 'bak350', 'skjerm350', 'ansikt350', 'auge25', 'auge47', 'auge60', 's_bak')}
    json.dump(ut, open(os.path.join(HER, 'kryss.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    a = sys.argv[1:] or ['sjekk']
    {'sjekk': k_sjekk, 'prove': k_prove, 'full': k_full, 'studie': k_studie, 'sett': k_sett, 'kryss': k_kryss}[a[0]](*a[1:])
