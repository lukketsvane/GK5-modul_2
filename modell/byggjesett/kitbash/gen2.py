# -*- coding: utf-8 -*-
"""gen2.py · kitbash generasjon 2: seks lamper med trykte delar, rendra med oppsettet til byggjesettet (13.11.2026)

Generasjon 1 (kitbash.py) var søket: 16 grove kroppar, målte likt. Her er dei som stod att, teikna med trykte delar
og rendra slik delbanken i byggjesettet er rendra: Cycles, same materiale og lys, ortografisk frå asimut −35 og
elevasjon 28, gjennomsiktig bakgrunn og 4 pikslar per mm. Raudt er trykt. Resten er delar frå settet, ruta-CAD-en eller kjøpt.

  1 Klype lett       bandlampa på skjermkanten med trykt klype, mast og ryggskjene. Ingen arm frå projektoren
  2 Klype med arm    same lyshovud på armen og hengselet frå projektoren, klemd på skjermkanten
  3 VESA             same, men boren av VESA-festet bak på skjermen
  4 Under            same, ståande på ei stålplate under skjermfoten
  5 Fot · knekk      plata på fot med flik, til høgre for skjermen (val c i generasjon 1)
  6 Projektoren snudd  hovudet er fot og lyshus, armen står opp ned, hengselet øvst vippar plata

  python gen2.py scener    skriv gen2/scener.json, gen2/stl/ og gen2/tal_mek.json
  blender.exe -b -P ../rendre_blender.py -- --scener=kitbash/gen2/scener.json --ut=kitbash/gen2/render   (frå modell/byggjesett)

Lysorganet i 1 til 4 har same plassar som grepet «over-band-vindauge-q30» i lys.py. Ingenting er målt.
"""
import os, sys, json, math
import numpy as np
import trimesh
from shapely.geometry import Polygon, box as sboks
import kitbash as kb
from kitbash import unit, Tr, Rot, Mx, retta, basis, boks, stong, ror, slaa, sett, cad, ny

HER = kb.HER
G2 = os.path.join(HER, 'gen2')
R = np.array([1.0, 0.0, 0.0]); N = kb.N_OVER; E1 = np.cross(N, R); OPP = -N
C = kb.C_OVER; KP = kb.KP_OVER
U_AX = unit(C - KP)                       # aksen LED-stripa lyser langs, opp mot plata
A_DIR = -np.cross(R, U_AX)                # på tvers av renna, mot veggen
PL = basis(R, -E1, OPP, C)                # platekoordinatar: x langs plata, y mot veggen, z opp frå oversida
REN = lambda L: basis(A_DIR, U_AX, R, KP - L / 2 * R)      # rennekoordinatar: a på tvers (mot veggen), b langs lysaksen, z langs stripa


def rb(p0, p1, r=4.0):
    """Boks med runda hjørne sett ovanfrå, slik ein trykt del ligg på byggjeplata."""
    p0, p1 = np.minimum(p0, p1).astype(float), np.maximum(p0, p1).astype(float)
    r = min(r, (p1[0] - p0[0]) / 2 - 0.01, (p1[1] - p0[1]) / 2 - 0.01)
    m = trimesh.creation.extrude_polygon(sboks(p0[0] + r, p0[1] + r, p1[0] - r, p1[1] - r).buffer(r, resolution=6), p1[2] - p0[2])
    m.apply_translation((0, 0, p0[2]))
    return m


def i(m, M):
    m.apply_transform(M)
    return m


def lyshovud(bak=167.0):
    """Lysorganet over skjermkanten: fresnelplata under ei ryggskjene, og renna med LED-stripa 12 cm under.
    Renna er usymmetrisk: veggen mot brukaren er høg og skjer ved framkanten av plata (41° frå aksen), så ein ikkje ser
    stripa ståande framfor bordet. Veggen mot veggen er låg og skjer ved bakkanten (61°)."""
    P = kb.plate(C, N, R)
    P.append(ny('ryggskjene, flatstong 20 × 5', i(boks((-10, -150, 1.75), (10, bak, 6.75)), PL), 'aluminium'))

    def klips(s):
        y0, y1 = (-153.5, -139.0) if s < 0 else (139.0, 153.5)
        kant = (-153.5, -149.5) if s < 0 else (149.5, 153.5); krok = (-153.5, -144.0) if s < 0 else (144.0, 153.5)
        return slaa([boks((-15, y0, 6.75), (15, y1, 11.0)), boks((-15, y0, 1.75), (-10.5, y1, 6.75)), boks((10.5, y0, 1.75), (15, y1, 6.75)),
                     boks((-15, kant[0], -5.5), (15, kant[1], 6.75)), boks((-15, krok[0], -5.5), (15, krok[1], -2.3))])
    P.append(ny('to klips som held plata under skjena', i(slaa([klips(-1), klips(1)]), PL)))
    L = 250.0
    prof = Polygon([(-11, -7), (11, -7), (11, 5), (8.5, 5), (8.5, 0), (-8.5, 0), (-8.5, 12), (-11, 12)])
    P.append(ny('renne for LED-stripa, 250 mm', i(trimesh.creation.extrude_polygon(prof, L), REN(L))))
    P.append(ny('LED-stripe, 24 cm', i(boks((-4, 0, 5), (4, 1.0, L - 5)), REN(L)), 'led'))
    P.append(ny('dreieknott for to kanalar', stong(KP + (L / 2) * R, KP + (L / 2 + 14) * R, 13, n=28), 'messing'))
    return P


KNOTT = dict(namn='knotten på renna', P=KP + 139.0 * R)


def klype_lett():
    P = lyshovud(167.0)
    P.append(ny('klype over skjermkanten', slaa([rb((-40, 438, 420), (40, 540, 432), 6), boks((-40, 438, 392), (40, 446, 421)),
                                                 boks((-40, 504, 352), (40, 512, 421))])))
    P.append(ny('klemskrue', stong((0, 512, 370), (0, 530, 370), 8, n=20), 'messing'))
    P.append(ny('mast, røyr Ø12 × 1, 210 mm', ror((0, 526, 432), (0, 526, 640), 6.0, 5.0), 'aluminium'))
    P.append(ny('skulder mellom mast og skjene', rb((-15, 513, 630), (15, 539, 652), 5)))
    P.append(ny('hals til renna', stong((0, 446, 430), KP - 7.0 * U_AX, 4.0, n=16)))
    P += kb.vindaugsmodul(np.array([0.0, 546.0, 575.0]), np.array([0.0, 700.0, 565.0]))
    return P, KNOTT


def med_arm(stotte):
    """Same lyshovud på armen P01 og hengselet P02. stotte: klype, vesa eller under."""
    if stotte == 'vesa':
        P = [ny('VESA-plate 120 × 120 × 3', boks((-60, 500, 205), (60, 503, 325)), 'stål'),
             ny('hylle på VESA-plata', slaa([boks((-35, 503, 282), (35, 600, 288)), boks((-3, 503, 215), (3, 590, 282))]))]
        A, K = kb.arm_paa(np.array([0.0, 568.0, 315.5]), 180.0); P += A
    else:
        P, K = kb.bak_skjermen(stotte)
    P += lyshovud(236.0)
    P.append(ny('sal over kappa på armen', rb((-23, 545, 641), (23, 592, 657), 5)))
    P.append(ny('hals til renna', stong((0, 545, 505), KP - 7.0 * U_AX, 4.0, n=16)))
    P += kb.vindaugsmodul(np.array([0.0, 607.0, 632.0]), np.array([0.0, 700.0, 600.0]))
    return P, KNOTT


# ------------------------------------------------------------------ projektoren snudd
SN_C = np.array([440.0, 425.0, 480.0])           # plata, over hovudet
SN_KP = np.array([440.0, 440.0, 75.0])           # linsa i hovudet
SN_N = kb.speglnormal(SN_C, SN_KP, kb.FELT); SN_NW = kb.speglnormal(SN_C, SN_KP, kb.VEGG_FOT)


def snudd():
    """Hovudet P03 ligg på bordet med opninga opp og er fot og lyshus. Armen P01 står opp ned frå lageret i hovudet,
    og hengselet P02 øvst er vippeleddet. Ein trykt bjelke klemmer høgrekanten av plata, slik bjelken i ruta på fot gjer."""
    fot = np.array([440.0, 440.0, 0.0])
    MH = Mx(Rot((0, 0, 1), 180), Tr(fot[0] + 70.0, fot[1], 40.0))                 # lengderetninga langs x, lageret til høgre
    P = sett('P03', MH, utan=('vifte', 'vifte_merke', 'sokkel'))
    P.append(ny('gummipute under hovudet', boks((fot[0] - 70, fot[1] - 39, -1.5), (fot[0] + 70, fot[1] + 39, 0)), 'gummi_svart'))
    akse = np.array([fot[0] + 94.0, fot[1], 344.5])                                # hengselaksen, langs x, øvst på armen
    P += sett('P01', basis((0, 0, -1), (1, 0, 0), (0, -1, 0), akse))               # armen opp ned: knoken nedst, tappen inn i lageret
    P += sett('P02', basis((0, 1, 0), (1, 0, 0), (0, 0, -1), akse))                # hengselet snudd: festeplata opp
    n = SN_N; rr = unit(R - (R @ n) * n); e = np.cross(n, rr)                      # platekoordinatar: rr langs plata mot høgre, e i plata
    PLs = basis(rr, e, n, SN_C)
    P += kb.plate(SN_C, n, rr, flik=100.0, n_flik=SN_NW)
    P.append(ny('bjelke som klemmer platekanten, 280 mm', i(slaa([boks((142, -140, 3), (164, 140, 11)), boks((142, -140, -11), (164, 140, -3)),
                                                                    boks((150, -140, -11), (164, 140, 11))]), PLs)))
    topp = SN_C + 157.0 * rr - 11.0 * n * 0 + 0.0
    P.append(ny('stolpe Ø10 frå hengselet til bjelken', stong(akse + np.array([0, -20.0, 29.0]), topp, 5.0, n=18), 'aluminium'))
    P.append(ny('sokkel på festeplata', rb(akse + np.array([-16, -44, 27.5]), akse + np.array([16, 4, 41.5]), 5)))
    P += kb.diode(np.array([fot[0], fot[1], 12.0]), SN_C, 'diode i hovudet')
    P += sett('P06', Mx(retta(unit(SN_C - SN_KP)), Tr(SN_KP[0], SN_KP[1], SN_KP[2] - 13.0)))
    P.append(ny('linsehaldar i hovudet', ror((fot[0], fot[1], 2.0), (fot[0], fot[1], SN_KP[2] - 11.0), 24.5, 21.5)))
    framme = e if e[1] < 0 else -e
    return P, dict(namn='framkanten av plata', P=SN_C + 147.0 * framme)


LAMPER = [
    # nøkkel, namn, støtte i mekanikken, bygg, lysgrep, handling, éi setning
    ('g2-1', 'Klype lett', 'klype', klype_lett, 'over-band-vindauge-q30', 'vri knotten',
     'Bandlampa utan armen frå projektoren: trykt klype, mast av røyr og ei ryggskjene som plata heng under.'),
    ('g2-2', 'Klype med arm', 'klype', lambda: med_arm('klype'), 'over-band-vindauge-q30', 'vri knotten',
     'Same lyshovud på armen og hengselet frå projektoren. Armen kan leggjast ned i hengselet.'),
    ('g2-3', 'VESA', 'klype', lambda: med_arm('vesa'), 'over-band-vindauge-q30', 'vri knotten',
     'Armen står på ei hylle på VESA-festet bak på skjermen. Overkanten av skjermen ber ingenting.'),
    ('g2-4', 'Under', 'under', lambda: med_arm('under'), 'over-band-vindauge-q30', 'vri knotten',
     'Armen står på eit røyr frå ei stålplate under skjermfoten. Lampa står sjølv.'),
    ('g2-5', 'Fot · knekk', 'fot', lambda: kb.fot_plate('knekk'), 'fot-knekk', 'vipp plata',
     'Plata på fot med flik, til høgre for skjermen. Dioden med glaslinsa står på foten.'),
    ('g2-6', 'Projektoren snudd', 'fot', snudd, 'snudd-knekk', 'vipp plata i hengselet',
     'Hovudet er fot og lyshus, armen står opp ned, og hengselet øvst vippar plata. Fem delar frå projektoren i ny rekkjefølgje.'),
]


def k_scener():
    os.makedirs(os.path.join(G2, 'stl'), exist_ok=True)
    scener, mek = {}, []
    for nr, (key, namn, stotte, bygg, lys, handling, setning) in enumerate(LAMPER, 1):
        P, h = bygg()
        objekt, alle = [], []
        for j, p in enumerate(P):
            if 'fil' in p:
                objekt.append(dict(fil=p['fil'], mat=p['mat'], M=np.asarray(p['M']).tolist(), del_=p['pid'] if p['pid'] != 'P08' else 'film', under=p['namn']))
            else:
                fil = f'kitbash/gen2/stl/{key}-{j:02d}.stl'
                p['mesh'].export(os.path.join(kb.BS, fil))
                objekt.append(dict(fil=fil, mat=p['mat'], M=np.eye(4).tolist(), del_='N', under=p['namn']))
            alle.append(np.asarray(p['mesh'].vertices))
        V = np.vstack(alle); lo, hi = V.min(0), V.max(0)
        scener[key] = dict(objekt=objekt, lo=lo.tolist(), hi=hi.tolist(), prover=32, storleik=[1600, 1000], baklys=False,
                           kamera=dict(mal=((lo + hi) / 2).tolist(), azimut=-35, elevasjon=28, lens=50, faktor=1.0), delbank=dict(px_per_mm=4))
        sp = dict(id=nr, namn=namn, stotte=stotte, organ='', handling=handling, setning=setning, lys=lys)
        r = kb.mekanikk(sp, P, h); r['key'] = key
        d = {}
        for p in P:
            if p['kjelde'] == 'ny' and p['namn'] != 'lysdiode':
                d[p['namn']] = d.get(p['namn'], 0) + p['m']
        r['nye_g'] = {k: round(v) for k, v in d.items()}
        r['trykt_g'] = round(sum(p['m'] for p in P if p['mat'] == 'print'))
        r['trykte'] = sorted({p['namn'] for p in P if p['mat'] == 'print'})
        r['kjopt'] = sorted({p['namn'] for p in P if p['kjelde'] == 'ny' and p['mat'] != 'print' and p['namn'] != 'lysdiode'})
        mek.append(r)
        print('%d %-18s %5d g (sett %4d, cad %4d, trykt %3d, anna nytt %4d)  fot %5.0f cm²  dytt %s N  trykk %s N  rekk %2.0f cm  %s' % (
            nr, namn, r['masse_g'], r['masse_sett_g'], r['masse_cad_g'], r['trykt_g'], r['masse_ny_g'] - r['trykt_g'], r['fotavtrykk_cm2'],
            r['dytt_N'], r['trykk_N'], r['rekk_mm'] / 10, '; '.join(r['flagg'])), flush=True)
    json.dump(scener, open(os.path.join(G2, 'scener.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(mek, open(os.path.join(G2, 'tal_mek.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    {'scener': k_scener}[(sys.argv[1:] or ['scener'])[0]]()
