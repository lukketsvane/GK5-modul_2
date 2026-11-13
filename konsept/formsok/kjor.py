# -*- coding: utf-8 -*-
"""Køyrer dei seks frøa i motor.py gjennom fotonsporaren i lys.py.

  python kjor.py                  tal for alle frø og modusar, skrivne til tal.md
  python kjor.py bilete vend_r    stemning og arbeid med lys i lufta, til par-vend_r.png
  python kjor.py kryss            kryssjekk mot lysmotoren i ../lysskisse

Tala blir rekna utan laptopen, for han ligg oppå arbeidsfeltet og ville gjeve ruter med null lux.
Biletet blir laga med laptopen. Same laptop-objekt må gå til både spor() og bilete().
"""
import sys, os, math, time
import numpy as np
from PIL import Image

HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
import motor as mo, lys

WATT = dict(stemning=1.25, arbeid=5.0, mote=2.5)      # same budsjett som i ../lysskisse (møte er ANTAKING)
N_TAL, N_BILETE = 600_000, 800_000


def scene(namn, modus):
    sc = mo.FRO[namn](modus)
    lm = WATT[modus] * sc['eta']
    for L in sc['lys']:
        L['lm'] = lm / len(sc['lys'])
    return sc, lm


def alle_tal():
    L = ['# Tal frå fotonsporaren', '',
         'Generert av `kjor.py`. Same watt til alle: 1,25 W i stemning, 5 W i arbeid, 2,5 W i møte. Modell, ikkje måling. '
         'Rommet er bord og éin vegg, utan skjerm. Auget står ved bordkanten, 47 cm over bordet.', '',
         '| Frø | Modus | W | lm | Felt, lx | Jamnheit | På feltet | Bak skjermen, lx | Lysaste flate mot auget, cd/m² | Lysande flate, cm² | Ansikt frå lampa, lx | Ansikt frå rommet, lx | Kjelde synleg 25/47/60 cm |',
         '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    K = ['', '| Frø | Masse, kg | Veltevinkel | Høgd, cm | Breidd, cm | Fot, cm² |', '| --- | --- | --- | --- | --- | --- |']
    for namn in mo.FRO:
        for modus in mo.MODUSAR:
            sc, lm = scene(namn, modus)
            t = lys.tal(sc, lys.spor(sc, N_TAL))
            L.append(f"| {sc['namn']} | {modus} | {WATT[modus]:.2f} | {lm:.0f} | {t['felt_lx']:.0f} | {t['u0']:.2f} | {t['felt_lm'] / lm * 100:.0f} % | "
                     f"{t['bak_lx']:.0f} | {t['L95']:.0f} | {t['A_lys_cm2']:.0f} | {t['ans_lampe']:.0f} | {t['ans_rom']:.0f} | "
                     f"{'/'.join('ja' if v else 'nei' for v in t['kjelde'].values())} |")
            print(L[-1])
            if modus == 'arbeid':
                k = mo.kropp(sc)
                K.append(f"| {sc['namn']} | {k['masse']:.2f} | {k['velt']:.0f}° | {k['hogd'] * 100:.0f} | {k['breidd'] * 100:.0f} | {k['fot_cm2']:.0f} |")
    open(os.path.join(HER, 'tal.md'), 'w', encoding='utf-8').write('\n'.join(L + K) + '\n')


def bilete(namn, n=420, ss=2):
    ims = []
    for modus in ('stemning', 'arbeid'):
        sc, lm = scene(namn, modus)
        lap = mo.laptop()
        g = lys.Gitter((-1.1, -0.2, 0.0), (0.9, 0.75, 1.3), 0.025)
        res = lys.spor(sc, N_BILETE, gitter=g, ekstra=lap)
        ims.append(lys.bilete(sc, res, g, np.array([0.95, -1.35, 0.85]), np.array([-0.15, 0.40, 0.22]), fov=40.0, n=n, ss=ss, ekstra=lap))
    B = Image.new('RGB', (2 * n + 48, n + 32), (0, 0, 0))
    B.paste(Image.fromarray(ims[0]), (16, 16)); B.paste(Image.fromarray(ims[1]), (n + 32, 16))
    fil = os.path.join(HER, f'par-{namn}.png')
    B.save(fil)
    print(fil)


def kryss():
    """Vend R i begge modellane, same geometri. Lysmotoren har lampa på høgre side, så frøet blir spegla."""
    sys.path.insert(0, os.path.join(HER, '..', 'lysskisse'))
    import lysskisse as ls
    F = np.array([-math.cos(math.radians(27)), -math.sin(math.radians(27)), 0.0]); Z = np.array([0, 0, 1.0])
    O = ls.b(0.45, 0.35, 0.0)
    print('per 100 lm frå kjelda            felt, lx   jamnheit   lm på feltet   mot auget, cd/m²')
    for modus, vipp, side in (('arbeid', 24.0, dict(rd=0.15, rs=0.65, sigma=11.0)), ('stemning', 55.0, dict(rd=0.85, rs=0.0, sigma=10.0))):
        sc = mo.FRO['vend_r'](modus)
        t = lys.tal(sc, lys.spor(sc, N_TAL))
        th = math.radians(vipp)
        k = ls.straale(O + Z * 0.02, O + Z * 0.385, 100.0, 2700, spreiing=400, kutt=14, opning=0.0045, sprut=0.0)
        a = ls.ark(k, O + Z * 0.385, math.sin(th) * F - math.cos(th) * Z, 0.25, framside=side, n=30)
        d = ls.tal([k, a], [])
        print(f"Vend R {modus:8s} fotonsporar   {t['felt_lx']:7.1f}   {t['u0']:8.2f}   {t['felt_lm']:12.1f}   {t['L95']:10.0f}")
        print(f"Vend R {modus:8s} lysmotor      {d['E_felt']:7.1f}   {d['U']:8.2f}   {d['E_felt'] * 0.24:12.1f}   {d['L_lampe']:10.0f}")


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    a = sys.argv[1:]
    if a and a[0] == 'bilete': bilete(a[1] if len(a) > 1 else 'vend_r')
    elif a and a[0] == 'kryss': kryss()
    else: alle_tal()
