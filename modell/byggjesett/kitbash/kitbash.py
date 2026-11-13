# -*- coding: utf-8 -*-
"""kitbash.py · montasjemotor: lampekroppar sette saman av CAD-en som finst (generasjon 1, 13.11.2026)

Settet er delane frå overheadprojektoren (modell/byggjesett/delar.py, P01 til P08), ruta på fot
(konsept/film/cad/ut/samla/*.stl, lesne og ikkje endra) og nokre få nye smådelar (diode, klype, bøyel, røyr).
Basen P04 (nettspenning) og FSX-pæra P09 er ikkje med i nokon kropp.

Kvar kropp er støtte × lysorgan. Støtta seier kvar lampa bur (klype på skjermkanten, plate under skjermen,
konsoll på veggen, fot til høgre for skjermen). Lysorganet er eit grep som alt er rekna i lysmotoren
(fresnelplata som vippar, plata med flik, plata med vindaugsdiode, ruta, linsa, hovudet), pluss to nye (band og røyr).

Koordinatar: mm, origo på bordflata midt framfor skjermen ved bordkanten. x mot høgre, y frå brukaren mot veggen, z opp.
Same rom som lysmotoren (konsept/lysskisse/API.md): skjermen 54 × 31 cm med framsida i y = 450, veggen i y = 700.

  python kitbash.py mek      mekanikk for alle (masse, fotavtrykk, velt, rekkjevidd, kva som må skaffast) -> tal_mek.json
  python kitbash.py brett    brettet 4 × 4 i husstilen (same kamera og ramme, skjermen som skugge) -> brett.png, velt_umogleg.png
  python lys.py              lyset for kvart grep i lysmotoren -> tal_lys.json
  python samle.py            tal.csv, tal.md og brett-merkt.png

Ingenting er målt. Måla på delane er anslått frå foto (modell/byggjesett/LES_MEG.md), massane er rekna frå volum.
"""
import os, sys, math, json, time
import numpy as np
import trimesh
from shapely.geometry import MultiPoint, Point
from shapely.geometry.polygon import orient

HER = os.path.dirname(os.path.abspath(__file__))
BS = os.path.dirname(HER)
ROT = os.path.dirname(os.path.dirname(BS))
sys.path.insert(0, BS)
import delar as D

CAD = os.path.join(ROT, 'konsept', 'film', 'cad', 'ut')
G = 9.81

# ------------------------------------------------------------------ rommet (mm), same som lysmotoren
SKJ = dict(x=270.0, y0=450.0, y1=500.0, z0=110.0, z1=420.0)       # skjermen som boks, 5 cm djup (ANTAKING frå formsøket)
SKJ_FOT = dict(x=120.0, y0=400.0, y1=600.0, z1=25.0)              # skjermfoten 24 × 20 cm (ANTAKING frå formsøket)
SKJ_MASSE = 4000.0                                                # g, ANTAKING: skjermen står på plata i «under»-kroppane
FELT = np.array([0.0, 250.0, 0.0])                                # midt i arbeidsfeltet 0,6 × 0,4 m
SKULDER = np.array([200.0, -220.0, 320.0]); REKK = 700.0          # ANTAKING frå formsøket: høgre skulder, lengste grep utan å reise seg
F_FINGER = 5.0                                                    # N, ANTAKING frå formsøket: fingerdytt

# plata over skjermkanten: plass og kjelde frå fresnel-familien (konsept/reflektor/fresnel/familie.py, OVER_C og OVER_A)
C_OVER = np.array([0.0, 360.0, 620.0])
A_OVER = np.array([0.0, 0.40, -0.90]); A_OVER = A_OVER / np.linalg.norm(A_OVER)
KP_OVER = C_OVER + 120.0 * A_OVER                                 # dioden 9 cm over skjermkanten, 4 cm framfor skjermplanet
VEGG_OVER = np.array([0.0, 700.0, 600.0])                         # veggen over skjermen, der stemninga landar
FOT = np.array([440.0, 440.0, 0.0])                               # foten til høgre for skjermen
C_FOT = FOT + np.array([0.0, -80.0, 470.0])                       # plata på fot: senter
KP_FOT = FOT + np.array([0.0, -30.0, 50.0])                       # kjelda med linse på foten
VEGG_FOT = np.array([100.0, 700.0, 550.0])                        # veggen bak skjermen, sett frå foten til høgre


# ------------------------------------------------------------------ materiale: g/cm³ og fyllgrad
RHO = {'aluminium': 2.70, 'stål': 7.85, 'stål_svart': 7.85, 'plast_grå': 1.05, 'plast_svart': 1.05, 'kopar': 8.9,
       'kretskort': 1.85, 'gummi_svart': 1.1, 'keramikk': 2.4, 'fresnel': 1.19, 'glas': 2.5, 'film': 1.3,
       'print': 1.27 * 0.55, 'pmma': 1.19, 'messing': 8.5, 'led': 2.7}
FYLL = {'plast_grå': 0.35, 'kopar': 0.5}      # ANTAKING: kappa på armen er hol, lagerskiva er ikkje massiv kopar
FYLL_DEL = {'P03 hovud · sokkel': 0.15}       # ANTAKING: lampesokkelen er ein brakett, ikkje ein massiv stålkloss


# ------------------------------------------------------------------ hjelparar
def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def Tr(x, y, z):
    return trimesh.transformations.translation_matrix((x, y, z))


def Rot(akse, grader):
    return trimesh.transformations.rotation_matrix(math.radians(grader), akse)


def Mx(*steg):
    """Set saman transformasjonar. Første steg verkar først."""
    M = np.eye(4)
    for s in steg:
        M = s @ M
    return M


def retta(z_til, x_til=None):
    """Rotasjon som tek lokal +z til z_til og lokal +x så nær x_til som råd."""
    w = unit(z_til)
    x0 = np.array((1.0, 0.0, 0.0) if x_til is None else x_til, float)
    u = x0 - (x0 @ w) * w
    if np.linalg.norm(u) < 1e-6:
        u = np.array([0.0, 1.0, 0.0]) - w[1] * w
    u = unit(u); v = np.cross(w, u)
    M = np.eye(4); M[:3, 0], M[:3, 1], M[:3, 2] = u, v, w
    return M


def basis(u, v, w, p):
    M = np.eye(4); M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = u, v, w, p
    return M


def boks(p0, p1):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    m = trimesh.creation.box(np.abs(p1 - p0)); m.apply_translation((p0 + p1) / 2)
    return m


def stong(a, b, r, n=14):
    return trimesh.creation.cylinder(radius=r, segment=[list(map(float, a)), list(map(float, b))], sections=n)


def ror(a, b, ry, ri, n=24):
    a, b = np.array(a, float), np.array(b, float)
    m = trimesh.creation.annulus(r_min=ri, r_max=ry, height=float(np.linalg.norm(b - a)), sections=n)
    m.apply_transform(Mx(retta(unit(b - a)), Tr(*((a + b) / 2))))
    return m


def slaa(ms):
    return trimesh.util.concatenate(ms)


# ------------------------------------------------------------------ settet
_SETT = {}
def sett(pid, M, utan=(), berre=None):
    """Delar frå overheadprojektoren (delar.py), plasserte med M."""
    if pid not in _SETT:
        _SETT[pid] = D.DELAR[pid]()[0]
    ut = []
    for under, mesh, mat in _SETT[pid]:
        if under in utan or (berre and under not in berre):
            continue
        m = mesh.copy(); m.apply_transform(M)
        ut.append(dict(namn=f'{pid} {D.DIMS[pid]["namn"]} · {under}', mesh=m, mat=mat, kjelde='sett', pid=pid))
    return ut


_KTR = json.load(open(os.path.join(CAD, 'kontroll.json'), encoding='utf-8'))
CAD_MASSE = {d['id']: d['masse_g'] for d in _KTR['delar']}
CAD_NAMN = {d['id']: d['namn'] for d in _KTR['delar']}
CAD_MAT = {'01': 'print', '02': 'print', '03': 'stål', '04': 'aluminium', '05': 'print', '06': 'print', '07': 'print', '08': 'print',
           '09': 'pmma', '10': 'film', '11': 'aluminium', '12': 'led', '13': 'messing', '14': 'gummi_svart',
           'A': 'stål', 'B': 'stål', 'C': 'stål', 'D': 'stål', 'E': 'stål'}
CAD_ALLE = list(CAD_MAT)
_CAD = {}
def cad(ids, M):
    """Delar frå ruta på fot (konsept/film/cad), i samanstilt stilling, plasserte med M. Massen kjem frå kontroll.json."""
    ut = []
    for i in ids:
        if i not in _CAD:
            _CAD[i] = trimesh.load(os.path.join(CAD, 'samla', i + '.stl'), force='mesh')
        m = _CAD[i].copy(); m.apply_transform(M)
        ut.append(dict(namn=f'R{i} {CAD_NAMN[i]}', mesh=m, mat=CAD_MAT[i], kjelde='cad', pid='R' + i, masse_g=CAD_MASSE[i]))
    return ut


RUTA_AKSE = np.array([-73.5, 24.5, 260.0])                              # midt på bjelkeaksen i lampe.py (VINKEL 35, AKSE_H 260)
RUTA_D0 = np.array([0.0, -math.cos(math.radians(35)), -math.sin(math.radians(35))])   # retninga ruta peikar frå bjelken, og stripa lyser
def ruta_gruppe(ids, senter, langs, peik):
    """Bjelken (og ruta) frå ruta-CAD-en: bjelkeaksen langs «langs» gjennom «senter», ruta og stripa mot «peik»."""
    l = unit(langs); d = np.asarray(peik, float); d = unit(d - (d @ l) * l)
    A = np.stack([np.array([1.0, 0, 0]), RUTA_D0, np.cross([1.0, 0, 0], RUTA_D0)], 1)
    B = np.stack([l, d, np.cross(l, d)], 1)
    R = np.eye(4); R[:3, :3] = B @ A.T
    return cad(ids, Mx(Tr(*(-RUTA_AKSE)), R, Tr(*senter)))


def ny(namn, mesh, mat='print', merk=''):
    return dict(namn=namn, mesh=mesh, mat=mat, kjelde='ny', pid='N', merk=merk)


def diode(pos, mot, namn='diode i brønn'):
    M = Mx(retta(unit(np.asarray(mot, float) - np.asarray(pos, float))), Tr(*pos))
    puck = trimesh.creation.cylinder(radius=11, height=8, sections=20); puck.apply_translation((0, 0, -4)); puck.apply_transform(M)
    bronn = trimesh.creation.annulus(r_min=10.5, r_max=12, height=20, sections=20); bronn.apply_translation((0, 0, 10)); bronn.apply_transform(M)
    led = trimesh.creation.cylinder(radius=5, height=1, sections=16); led.apply_translation((0, 0, 0.6)); led.apply_transform(M)
    return [ny(namn, slaa([puck, bronn]), 'aluminium'), ny('lysdiode', led, 'led')]


def vindaugsmodul(pos, mot):
    """Dioden bak ei maske som teiknar vindauget på veggen (konsept/film/ruta.py, vindaugsdiode): 26 × 26 × 26 mm."""
    M = Mx(retta(unit(np.asarray(mot, float) - np.asarray(pos, float))), Tr(*pos))
    hus = boks((-13, -13, -14), (13, 13, 12)); hus.apply_transform(M)
    led = trimesh.creation.cylinder(radius=6, height=1, sections=16); led.apply_translation((0, 0, 12.6)); led.apply_transform(M)
    return [ny('vindaugsdiode med maske', hus, 'print'), ny('lysdiode', led, 'led')]


def boyel(K, c, r, halv=152.0):
    """Bøyel av Ø6 stong: tverrstong gjennom knoken på armen, to sidestenger fram til tappane midt på sidekantane av plata."""
    r = unit(r); a0, a1 = K - halv * r, K + halv * r; p0, p1 = c - halv * r, c + halv * r
    return slaa([stong(a0, a1, 3), stong(a0, p0, 3), stong(a1, p1, 3), stong(p0, p0 + 9 * r, 3), stong(p1 - 9 * r, p1, 3)])


def plate(c, n, r, flik=None, n_flik=None, skive=False):
    """Fresnelplata P05 med spegelsida mot n, vippeaksen langs r gjennom senteret c. flik: blank flik (mm) frå midtlina, med normal n_flik."""
    n = unit(n); r = np.asarray(r, float); r = unit(r - (r @ n) * n)
    if skive:      # plata maskert til skive Ø285: maska er svart og syner ikkje, massen er heile plata
        m = trimesh.creation.cylinder(radius=142.5, height=3.5, sections=48); m.apply_transform(Mx(retta(n, r), Tr(*c)))
        P = [dict(namn='P05 fresnelspegel · maskert til skive', mesh=m, mat='fresnel', kjelde='sett', pid='P05', masse_g=310.0)]
    else:
        P = sett('P05', Mx(Tr(0, 0, -1.75), retta(n, r), Tr(*c)))
    if flik:
        n2 = unit(n_flik); e2 = np.cross(n2, r)
        m = boks((-142.5, -flik, 0), (142.5, 0, 1.5)); m.apply_transform(basis(r, e2, n2, c + 2.5 * n))
        P.append(ny(f'blank flik 285 × {flik:g} mm', m, 'aluminium'))
    return P


def speglnormal(c, kjelde, maal):
    """Normalen som sender lyset frå kjelda via c til målet."""
    return unit(unit(np.asarray(kjelde, float) - c) + unit(np.asarray(maal, float) - c))


N_OVER = speglnormal(C_OVER, KP_OVER, FELT); NW_OVER = speglnormal(C_OVER, KP_OVER, VEGG_OVER)
N_FOT = speglnormal(C_FOT, KP_FOT, FELT); NW_FOT = speglnormal(C_FOT, KP_FOT, VEGG_FOT)
R_FOT = unit(np.cross(N_FOT, NW_FOT))                      # vippeaksen for plata på fot


# ------------------------------------------------------------------ støtter
def arm_paa(B, phi=180.0):
    """Hengselet P02 og armen P01 ståande i B (hengselaksen). Knokeaksen peikar langs (cos phi, sin phi). Gjev delane og knoken K."""
    a = phi - 90.0
    P = sett('P02', Mx(Rot((0, 0, 1), a), Tr(*B)))
    P += sett('P01', Mx(Rot((0, 1, 0), -90), Rot((0, 0, 1), a), Tr(*B)))
    return P, np.asarray(B, float) + np.array([0.0, 0.0, 304.5])


def bak_skjermen(stotte, knoke_z=620.0):
    """Armen står bak skjermen, midt på, med knoken i (0, 568, knoke_z). stotte: klype, under eller vegg."""
    B = np.array([0.0, 568.0, knoke_z - 304.5]); z1 = B[2] - 27.5; z0 = z1 - 6.0; P = []
    if stotte == 'klype':
        P.append(ny('skjermklype med hylle', slaa([boks((-35, 444, 420), (35, 506, 432)), boks((-35, 444, 395), (35, 450, 420)),
                                                   boks((-35, 500, z0), (35, 506, 420)), boks((-35, 506, z0), (35, 600, z1))])))
    elif stotte == 'under':
        P.append(ny('stålplate under skjermfoten, 300 × 230 × 2', boks((-150, 450, 0), (150, 680, 2)), 'stål'))
        P.append(ny(f'røyr Ø25 × 1,5, {z0 - 2:.0f} mm', ror((0, 640, 2), (0, 640, z0), 12.5, 11.0), 'aluminium'))
        P.append(ny('hylle med krage', slaa([boks((-35, 506, z0), (35, 660, z1)), boks((-18, 622, z0 - 20), (18, 658, z0))])))
    elif stotte == 'vegg':
        P.append(ny('veggplate 80 × 120 × 6', boks((-40, 694, z0 - 54), (40, 700, z0 + 66)), 'aluminium'))
        P.append(ny('konsoll frå veggen', slaa([boks((-35, 506, z0), (35, 694, z1)), stong((0, 692, z0 - 46), (0, 545, z0 + 1), 5)])))
    A, K = arm_paa(B, 180.0)
    return P + A, K


def paa_fot(ekstra=0.0, phi=None, fot=FOT, bak=38.0):
    """Foten frå ruta-CAD-en (01, 02, 03) med armen ståande bak på foten. ekstra: røyr mellom fot og hengsel (mm)."""
    fot = np.asarray(fot, float)
    P = cad(['01', '02', '03'], Tr(*fot))
    z0 = 16.0
    if ekstra:
        P.append(ny(f'røyr Ø25 × 1,5, {ekstra:g} mm', ror(fot + (0, bak, z0), fot + (0, bak, z0 + ekstra), 12.5, 11.0), 'aluminium'))
        P.append(ny('plattform for hengselet', boks(fot + (-34, bak - 64, z0 + ekstra), fot + (34, bak + 24, z0 + ekstra + 4))))
        z0 += ekstra + 4
    B = fot + np.array([0.0, bak, z0 + 27.5])
    if phi is None:
        phi = math.degrees(math.atan2(R_FOT[1], R_FOT[0]))
    A, K = arm_paa(B, phi)
    return P + A, K


def kjelde_paa_fot(c=C_FOT, kp=KP_FOT):
    """Dioden på foten med glaslinsa P06 over som samlelinse (kjelda «SMAL» i fresnel-familien)."""
    P = diode(np.array([kp[0], kp[1], 24.0]), c, 'diode på foten')
    P += sett('P06', Mx(retta(unit(c - kp)), Tr(kp[0], kp[1], kp[2] - 10.0)))
    P.append(ny('linsehaldar', ror((kp[0], kp[1], 16), (kp[0], kp[1], kp[2] - 8.0), 24.5, 21.5)))
    return P


def hovud(K, d, opp):
    """Hovudet P03 på knoken K, lengderetninga langs d og den opne flata mot «opp»."""
    u = unit(d); w = np.asarray(opp, float); w = unit(w - (w @ u) * u); v = np.cross(w, u)
    return sett('P03', basis(u, v, w, K + 28.0 * u)), u


# ------------------------------------------------------------------ kroppane
def over(stotte, organ):
    r = np.array([1.0, 0.0, 0.0]); h = dict(namn='framkanten av plata', P=C_OVER + 147.0 * np.cross(N_OVER, r))
    if organ == 'rute':        # D Ruta: bjelken og ruta frå CAD-en på knoken, 10° opp mot brukaren, den lysande sida ned
        P, K = bak_skjermen(stotte, 500.0)
        e = np.array([0.0, -math.cos(math.radians(10)), math.sin(math.radians(10))])
        P += ruta_gruppe(['07', '08', '09', '10', '11', '12'], (0.0, 526.0, 500.0), (1, 0, 0), e)
        P += vindaugsmodul(K + np.array([0.0, 7.0, 39.0]), K + np.array([0.0, 100.0, 20.0]))
        P.append(ny('dreieknott for to kanalar', stong((163, 526, 500), (189, 526, 500), 14), 'aluminium'))
        return P, dict(namn='knotten på bjelken', P=np.array([189.0, 526.0, 500.0]))
    P, K = bak_skjermen(stotte)
    P.append(ny('bøyel Ø6', boyel(K, C_OVER, r), 'aluminium'))
    if organ == 'flik':
        P += plate(C_OVER, N_OVER, r, flik=60.0, n_flik=NW_OVER)
    else:
        P += plate(C_OVER, N_OVER, r)
    if organ == 'band':        # bjelken med LED-stripa frå ruta-CAD-en på skjermkanten, stripa vend opp mot plata
        P += ruta_gruppe(['07', '08', '11', '12'], KP_OVER, (1, 0, 0), C_OVER - KP_OVER)
        P.append(ny('finger til bjelken', stong((0, 546, 503), KP_OVER + np.array([0, 16.0, -6.0]), 4), 'aluminium'))
    else:
        P += diode(KP_OVER, C_OVER)
        P.append(ny('finger til dioden', stong((0, 546, 503), KP_OVER + 9.0 * A_OVER, 3), 'aluminium'))
    if organ == 'vindauge':
        P += vindaugsmodul(K + np.array([0.0, 7.0, 39.0]), K + np.array([0.0, 100.0, 20.0]))
        P.append(ny('dreieknott for to kanalar', stong((36, 475, 426), (36, 475, 446), 14), 'aluminium'))
        h = dict(namn='knotten på skjermkanten' if stotte == 'klype' else 'knotten ved skjermkanten', P=np.array([36.0, 475.0, 446.0]))
    return P, h


def fot_plate(organ):
    hog = organ == 'skive'
    if hog:        # «Northern i tre former»: fot, tynn stong og skive. Ingen arm frå projektoren
        c = FOT + np.array([0.0, -80.0, 550.0]); n = speglnormal(c, KP_FOT, FELT); nw = speglnormal(c, KP_FOT, VEGG_FOT)
        r = unit(np.cross(n, nw))
        P = cad(['01', '02', '03'], Tr(*FOT))
        topp = c - 22.0 * n
        P.append(ny('stong Ø12 × 1, 560 mm', ror(FOT + (0, 38, 16), topp, 6.0, 5.0), 'aluminium'))
        P.append(ny('vippeledd', stong(topp - 14 * r, topp + 14 * r, 9)))
        P += plate(c, n, r, skive=True)
        P += kjelde_paa_fot(c)
        return P, dict(namn='kanten av skiva', P=c + 142.0 * np.cross(n, r))
    P, K = paa_fot()
    P.append(ny('bøyel Ø6', boyel(K, C_FOT, R_FOT), 'aluminium'))
    if organ == 'knekk':
        P += plate(C_FOT, N_FOT, R_FOT, flik=100.0, n_flik=NW_FOT)
    else:
        P += plate(C_FOT, N_FOT, R_FOT)
    P += kjelde_paa_fot()
    h = dict(namn='framkanten av plata', P=C_FOT + 147.0 * np.cross(N_FOT, R_FOT))
    if organ == 'vindauge':
        P += vindaugsmodul(K + np.array([0.0, 12.0, 39.0]), K + np.array([0.0, 200.0, 60.0]))
        P.append(ny('dreieknott for to kanalar', stong(FOT + (-40, -50, 16), FOT + (-40, -50, 34), 14), 'aluminium'))
        h = dict(namn='knotten på foten', P=FOT + np.array([-40.0, -50.0, 34.0]))
    return P, h


def fot_rute():
    """Kroppen Iver valde: ruta på fot slik CAD-en står (konsept/film/cad/lampe.py). Plassen er den i lys_sjekk.py:
    midt i foten 47 cm til høgre og 30 cm inn på bordet. Ved foten til dei andre (y 440) går bjelken inn i skjermen."""
    f = np.array([470.0, 300.0, 0.0])
    P = cad(CAD_ALLE, Tr(*f))
    return P, dict(namn='knotten på leddet', P=f + np.array([136.0, 24.5, 260.0]))


def fot_linse():
    """C Vindauge av settet: hovudet P03 som projektor 70 cm oppe, glaslinsa P06 som linse, frontflatespegelen deler strålen."""
    fot = np.array([400.0, 500.0, 0.0])
    P, K = paa_fot(ekstra=350.0, phi=0.0, fot=fot, bak=0.0)
    d = unit(np.array([0.0, 700.0, 600.0]) - K); phi = math.degrees(math.atan2(d[0], -d[1]))
    P, K = paa_fot(ekstra=350.0, phi=phi, fot=fot, bak=0.0)
    H, u = hovud(K, d, (0, 0, 1)); P += H
    P += diode(K + 70.0 * u, K + 200.0 * u, 'diode med maske i hovudet')
    P += sett('P06', Mx(retta(u), Tr(*(K + 172.0 * u))))
    p = K + 235.0 * u; nm = unit(unit(FELT - p) - u)
    m = boks((-50, -35, 0), (50, 35, 3)); m.apply_transform(Mx(retta(nm, np.cross(u, nm)), Tr(*p)))
    P.append(dict(namn='frontflatespegelen frå projektoren, 100 × 70 (ANTAKING, ikkje fotografert)', mesh=m, mat='stål', kjelde='sett', pid='P10', masse_g=45.0))
    P.append(ny('skinne til spegelen', stong(K + 150.0 * u + (0, 0, -42), K + 260.0 * u + (0, 0, -42), 3), 'aluminium'))
    return P, dict(namn='spegelen', P=p)


def fot_hovud(linse280=False):
    """Projektoren som bordlampe: hovudet P03 på armen, opninga ned mot feltet. linse280: med projeksjonslinsa P07 (kan ikkje lagast)."""
    d = unit(np.array([FELT[0] - FOT[0], FELT[1] - (FOT[1] + 38.0), 0.0]))
    phi = math.degrees(math.atan2(d[0], -d[1]))
    P, K = paa_fot(phi=phi)
    if linse280:
        d = unit(np.array([0.0, 700.0, 600.0]) - K); phi = math.degrees(math.atan2(d[0], -d[1]))
        P, K = paa_fot(phi=phi)
        H, u = hovud(K, d, (0, 0, 1)); P += H
        P += sett('P07', Mx(retta(u), Tr(*(K + 170.0 * u))))
        P += diode(K + 40.0 * u, K + 200.0 * u, 'diode med maske i hovudet')
        return P, dict(namn='spaken på linsa', P=K + 180.0 * u)
    H, u = hovud(K, d, (0, 0, -1)); P += H
    P += diode(K + 98.0 * u + np.array([0, 0, 20.0]), K + 98.0 * u + np.array([0, 0, -200.0]), 'diode i hovudet')
    return P, dict(namn='hovudet', P=K + 168.0 * u)


def fot_royr():
    """Prismearket P08 rulla til eit røyr Ø97 × 535 på foten, med ei diode i botnen. Berre stemning."""
    P = cad(['01', '02', '03'], Tr(*FOT))
    m = trimesh.creation.annulus(r_min=48.2, r_max=48.7, height=535.0, sections=40); m.apply_translation(FOT + (0, 0, 16 + 267.5))
    P.append(dict(namn='P08 prismeark · rulla til røyr', mesh=m, mat='film', kjelde='sett', pid='P08', masse_g=306 * 535 * 0.2 / 1000 * 1.3))
    P += diode(FOT + np.array([0, 0, 24.0]), FOT + np.array([0, 0, 300.0]), 'diode i botnen')
    P.append(ny('ring og topplok', slaa([ror(FOT + (0, 0, 16), FOT + (0, 0, 30), 52, 49), ror(FOT + (0, 0, 545), FOT + (0, 0, 553), 52, 30)])))
    return P, dict(namn='dimmaren på leidningen', P=FOT + np.array([-79.0, -40.0, 10.0]))


def projektoren():
    """Projektoren slik delane kan ha sete (delar.scene_samla), utan basen P04. Plata ligg på bordet: bryt F9."""
    M0 = Mx(Rot((0, 0, 1), 180), Tr(440.0, 300.0, 0.0)); P = []
    for pid, M in D.scene_samla():
        if pid == 'P04':
            continue
        P += sett(pid, M0 @ np.asarray(M))
    P += diode(M0[:3, :3] @ np.array([0.0, -150.0, 330.0]) + M0[:3, 3], np.array([440.0, 300.0, 0.0]), 'diode i hovudet')
    return P, dict(namn='hovudet', P=np.array([440.0, 300.0, 400.0]))


KROPPAR = [
    # id, rad, kol, namn, støtte, organ, bygg, lysgrep, handling, éi setning
    (1, 0, 0, 'Klype · vipp', 'klype', 'plata vippar', lambda: over('klype', 'vipp'), 'over-vipp', 'vipp plata',
     'Fresnelplata heng som eit tak over skjermkanten og vippar lyset frå veggen ned på bordet.'),
    (2, 0, 1, 'Klype · flik', 'klype', 'plata med flik', lambda: over('klype', 'flik'), 'over-flik', 'vipp plata',
     'Same tak, med ein blank flik som held veggen bak skjermen lys i arbeid (B Over).'),
    (3, 0, 2, 'Klype · vindauge', 'klype', 'plata og vindaugsdiode', lambda: over('klype', 'vindauge'), 'over-vindauge', 'vri knotten',
     'Plata står fast mot feltet. Ei diode bak ei maske teiknar vindauget på veggen, og knotten flyttar watten.'),
    (4, 0, 3, 'Klype · band', 'klype', 'plata og LED-stripe', lambda: over('klype', 'band'), 'over-band', 'vipp plata',
     'Bjelken med LED-stripa ligg på skjermkanten og lyser opp i plata, som legg eit band av lys over feltet.'),
    (5, 1, 0, 'Klype · rute', 'klype', 'ruta og vindaugsdiode', lambda: over('klype', 'rute'), 'over-rute', 'vri knotten',
     'Ruta med prismefilmen over skjermkanten og vindaugsdioden bak (D Ruta), boren av armen frå projektoren.'),
    (6, 1, 1, 'Under · vipp', 'under', 'plata vippar', lambda: over('under', 'vipp'), 'over-vipp', 'vipp plata',
     'Same tak, men lampa står på ei stålplate under skjermfoten og lastar ikkje skjermen.'),
    (7, 1, 2, 'Under · vindauge', 'under', 'plata og vindaugsdiode', lambda: over('under', 'vindauge'), 'over-vindauge', 'vri knotten',
     'Plata fast mot feltet og vindauget på veggen, ståande på plata under skjermen.'),
    (8, 1, 3, 'Vegg · vipp', 'vegg', 'plata vippar', lambda: over('vegg', 'vipp'), 'over-vipp', 'vipp plata',
     'Same tak på ein konsoll frå veggen. Bordet er fritt, men lampa kan ikkje flyttast.'),
    (9, 2, 0, 'Fot · vipp', 'fot', 'plata vippar', lambda: fot_plate('vipp'), 'fot-vipp', 'vipp plata',
     'Plata står skrått på armen til høgre for skjermen, som ei rute på fot. Dioden med linse i foten lyser opp i henne.'),
    (10, 2, 1, 'Fot · knekk', 'fot', 'plata med flik', lambda: fot_plate('knekk'), 'fot-knekk', 'vipp plata',
     'Same, med ein flik på 100 mm som sender ein del av lyset til veggen bak skjermen.'),
    (11, 2, 2, 'Fot · vindauge', 'fot', 'plata og vindaugsdiode', lambda: fot_plate('vindauge'), 'fot-vindauge', 'vri knotten',
     'Plata fast mot feltet, vindaugsdioden på toppen av armen teiknar vindauget på veggen til høgre.'),
    (12, 2, 3, 'Fot · skive', 'fot', 'skiva vippar', lambda: fot_plate('skive'), 'fot-skive', 'vipp skiva',
     'Fot, tynn stong og plata maskert til ei skive 55 cm oppe: Northern i tre former.'),
    (13, 3, 0, 'Fot · rute', 'fot', 'ruta', fot_rute, 'fot-rute', 'vri knotten',
     'Kroppen Iver valde: ruta på fot slik CAD-en står.'),
    (14, 3, 1, 'Fot · linse', 'fot', 'linsa og spegelen', fot_linse, 'fot-linse', 'skyv spegelen inn',
     'Hovudet frå projektoren som projektor 70 cm oppe. Glaslinsa teiknar vindauget, spegelen deler strålen ned på feltet (C Vindauge).'),
    (15, 3, 2, 'Fot · hovud', 'fot', 'hovudet', fot_hovud, 'fot-hovud', 'drei hovudet',
     'Projektoren som bordlampe: hovudet på armen med opninga ned. Det busette: ei vanleg arbeidslampe.'),
    (16, 3, 3, 'Fot · røyr', 'fot', 'arket som røyr', fot_royr, 'fot-royr', 'dimmar',
     'Prismearket rulla til eit røyr på foten, med ei diode i botnen. Berre stemning.'),
]
KONTROLL = [
    (17, 4, 0, 'Veltar: projektoren', 'bord', 'som han stod', projektoren, 'projektor', 'ingen',
     'Projektoren slik delane sat, utan basen. Plata ligg på bordet og tek 870 cm².'),
    (18, 4, 1, 'Kan ikkje lagast: linsa 280', 'fot', 'projeksjonslinsa', lambda: fot_hovud(True), 'ingen', 'ingen',
     'Projeksjonslinsa P07 (f 280 mm) i ei bordlampe: kastet er under 4f = 1,12 m, så biletet blir aldri skarpt.'),
]
ALLE = KROPPAR + KONTROLL
NOKLAR = ('id', 'rad', 'kol', 'namn', 'stotte', 'organ', 'bygg', 'lys', 'handling', 'setning')
SPEC = [dict(zip(NOKLAR, k)) for k in ALLE]


# ------------------------------------------------------------------ mekanikk
def masse(p):
    if 'masse_g' in p:
        return float(p['masse_g'])
    return abs(float(p['mesh'].volume)) / 1000.0 * RHO[p['mat']] * FYLL_DEL.get(p['namn'], FYLL.get(p['mat'], 1.0))


def tyngdepunkt(p):
    m = p['mesh']
    try:
        if m.is_watertight:
            return np.asarray(m.center_mass, float)
    except Exception:
        pass
    return np.asarray(m.bounds, float).mean(0)


def mekanikk(sp, P, h):
    for p in P:
        p['m'] = masse(p); p['tp'] = tyngdepunkt(p)
    m = sum(p['m'] for p in P); tp = sum(p['m'] * p['tp'] for p in P) / m
    alle = np.vstack([p['mesh'].vertices for p in P])
    ut = dict(id=sp['id'], namn=sp['namn'], stotte=sp['stotte'], organ=sp['organ'], handling=sp['handling'], setning=sp['setning'], lys=sp['lys'],
              masse_g=round(m), tyngdepunkt=[round(float(x), 1) for x in tp], hogd_mm=round(float(alle[:, 2].max())),
              masse_sett_g=round(sum(p['m'] for p in P if p['kjelde'] == 'sett')), masse_cad_g=round(sum(p['m'] for p in P if p['kjelde'] == 'cad')),
              masse_ny_g=round(sum(p['m'] for p in P if p['kjelde'] == 'ny')),
              delar_sett=sorted({p['pid'] for p in P if p['kjelde'] == 'sett'}), delar_cad=sorted({p['pid'] for p in P if p['kjelde'] == 'cad'}),
              nye=sorted({p['namn'] for p in P if p['kjelde'] == 'ny' and p['namn'] != 'lysdiode'}),
              handtak=h['namn'], rekk_mm=round(float(np.linalg.norm(h['P'] - SKULDER))))
    flagg = []
    # skjermen: kjem noko inn i skjermboksen?
    inn = (np.abs(alle[:, 0]) < SKJ['x'] - 1) & (alle[:, 1] > SKJ['y0'] + 1) & (alle[:, 1] < SKJ['y1'] - 1) & (alle[:, 2] > SKJ['z0'] + 1) & (alle[:, 2] < SKJ['z1'] - 1)
    if inn.any():
        flagg.append('går inn i skjermen')
    kontakt = alle[alle[:, 2] < 1.0][:, :2]
    if sp['stotte'] in ('klype', 'vegg'):
        ut.update(fotavtrykk_cm2=0.0, tipp_grader=None, dytt_N=None, trykk_N=None)
        if sp['stotte'] == 'klype':
            arm_m = (tp[1] - (SKJ['y0'] + SKJ['y1']) / 2) / 1000.0
            ut.update(last_skjerm_g=round(m), moment_skjerm_Nm=round(m / 1000 * G * arm_m, 2),
                      trykk_moment_Nm=round(F_FINGER * (h['P'][1] - (SKJ['y0'] + SKJ['y1']) / 2) / 1000.0, 2))
            flagg.append('lastar skjermen (må prøvast)')
        else:
            flagg.append('skrudd i veggen: kan ikkje flyttast (F8)')
    else:
        deler = [(m, tp)]
        if sp['stotte'] == 'under':          # skjermen står på plata og held ho nede (ANTAKING 4 kg midt på skjermfoten)
            deler.append((SKJ_MASSE, np.array([0.0, 500.0, 200.0])))
        M = sum(a for a, _ in deler); TP = sum(a * b for a, b in deler) / M
        hull = orient(MultiPoint([tuple(k) for k in kontakt]).convex_hull, 1.0)
        inne = hull.contains(Point(TP[0], TP[1])); d = hull.exterior.distance(Point(TP[0], TP[1])) * (1 if inne else -1)
        ut['fotavtrykk_cm2'] = round(hull.area / 100.0, 1)
        ut['tipp_grader'] = round(math.degrees(math.atan2(d, TP[2])), 1)
        # dytt sidelengs i handtaket, verste retning; trykk rett ned i handtaket
        ut['dytt_N'] = round(max(M / 1000 * G * d / max(h['P'][2], 1.0), 0.0), 1)
        best = float('inf'); ko = list(hull.exterior.coords)
        for a, b in zip(ko[:-1], ko[1:]):
            a, b = np.array(a), np.array(b); t = unit(b - a); nu = np.array([t[1], -t[0]])
            sP = (h['P'][:2] - a) @ nu; sC = (TP[:2] - a) @ nu
            if sP > 0 and sC < 0:
                best = min(best, M / 1000 * G * (-sC) / sP)
        ut['trykk_N'] = None if best == float('inf') else round(best, 1)
        if not inne:
            flagg.append('veltar av seg sjølv')
        elif ut['dytt_N'] < F_FINGER or (ut['trykk_N'] is not None and ut['trykk_N'] < F_FINGER):
            flagg.append('veltar under fingerdytt')
        if ut['fotavtrykk_cm2'] > 200:
            flagg.append('bryt F9 (200 cm²)')
    if m > 1200:
        flagg.append('bryt F8 (1,2 kg)')
    if ut['rekk_mm'] > REKK:
        flagg.append('handtaket utanfor rekkjevidd')
    ut['flagg'] = flagg
    return ut


def k_mek():
    t0 = time.time(); rader = []
    for sp in SPEC:
        P, h = sp['bygg'](); r = mekanikk(sp, P, h); rader.append(r)
        print('%2d %-28s %5d g (sett %4d, cad %4d, ny %4d)  fot %5.0f cm²  tipp %s  dytt %s N  trykk %s N  rekk %3d cm  %s' % (
            r['id'], r['namn'], r['masse_g'], r['masse_sett_g'], r['masse_cad_g'], r['masse_ny_g'], r['fotavtrykk_cm2'],
            r['tipp_grader'], r['dytt_N'], r['trykk_N'], r['rekk_mm'] / 10, '; '.join(r['flagg'])), flush=True)
    json.dump(rader, open(os.path.join(HER, 'tal_mek.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('mek %.0f s' % (time.time() - t0))


# ------------------------------------------------------------------ brett i husstilen (northern-lampe/felles.py: same kamera, lys og farge)
def k_brett():
    sys.path.insert(0, os.path.join(ROT, 'northern-lampe'))
    import felles as fe
    from PIL import Image
    t0 = time.time()
    # Husstilen har az 240. Her står kameraet i az 300 (framfor til høgre): frå 240 ligg platene på fot rett langs synslina.
    KAM = dict(el=17, az=300, fov=19, D=3.0, target=[0.16, 0.46, 0.36])
    cam = fe.Cam(S=1024, **{k: (tuple(v) if k == 'target' else v) for k, v in KAM.items()})
    E_FARGE = np.array([255, 219, 168])           # fargen fe.render gjev lysande flater
    sb = boks((-SKJ['x'], SKJ['y0'], SKJ['z0']), (SKJ['x'], SKJ['y1'], SKJ['z1']))
    sf = slaa([sb, boks((-SKJ_FOT['x'], SKJ_FOT['y0'], 0), (SKJ_FOT['x'], SKJ_FOT['y1'], SKJ_FOT['z1'])), boks((-30, 500, 0), (30, 540, 250))])
    Vs, Fs = np.asarray(sf.vertices) / 1000.0, np.asarray(sf.faces)
    ims, masks, klipt = {}, {}, []
    for sp in SPEC:
        P, _ = sp['bygg']()
        V = np.vstack([p['mesh'].vertices for p in P]) / 1000.0
        n = np.cumsum([0] + [len(p['mesh'].vertices) for p in P])
        F = np.vstack([np.asarray(p['mesh'].faces) + n[i] for i, p in enumerate(P)])
        emit = np.concatenate([np.full(len(p['mesh'].faces), p['mat'] == 'led') for p in P])
        iml, mkl = fe.render(V, F, cam, emit)
        if sp['id'] == 17:                    # projektoren står åleine: skjermen ville dekt han
            a = np.asarray(iml).astype(float); lampe = mkl
        else:
            # Skjermen er med som mørk skugge, med rett dekking. Første pass teiknar skjermen lysande for å finne pikslane hans.
            # (Første utgåve samanlikna fargar med lampa åleine. Då skein delar bak skjermen gjennom som lyse silhuettar.)
            VA, FA = np.vstack([V, Vs]), np.vstack([F, Fs + len(V)])
            im1, _ = fe.render(VA, FA, cam, np.r_[np.zeros(len(F), bool), np.ones(len(Fs), bool)])
            im2, _ = fe.render(VA, FA, cam, np.r_[emit, np.zeros(len(Fs), bool)])
            S = np.abs(np.asarray(im1).astype(int) - E_FARGE).max(-1) <= 8
            a = np.asarray(im2).astype(float); a[S] *= 0.26
            lampe = mkl & ~S
        ims[sp['id']] = Image.fromarray(a.astype(np.uint8)); masks[sp['id']] = lampe
        ys, xs = np.nonzero(mkl)
        if len(xs) and (xs.min() <= 1 or ys.min() <= 1 or xs.max() >= 510 or ys.max() >= 510):
            klipt.append(sp['id'])
        print('teikna', sp['id'], sp['namn'], len(F), 'flater', flush=True)
    brett = Image.new('RGB', (2048, 2048), (0, 0, 0))
    for sp in SPEC[:16]:
        brett.paste(ims[sp['id']], (sp['kol'] * 512, sp['rad'] * 512))
    brett.save(os.path.join(HER, 'brett.png'))
    stripe = Image.new('RGB', (1024, 512), (0, 0, 0))
    for i, k in enumerate((17, 18)):
        stripe.paste(ims[k], (i * 512, 0))
    stripe.save(os.path.join(HER, 'velt_umogleg.png'))
    for k, im in ims.items():
        im.save(os.path.join(HER, 'flis', f'{k:02d}.png'))
    # formkritikk: nabo-IoU og luft i hylsteret (maska mot det konvekse hylsteret sitt)
    grid = {(s['rad'], s['kol']): s['id'] for s in SPEC[:16]}; par = []
    for (r, c), i in grid.items():
        for rr, cc in ((r, c + 1), (r + 1, c)):
            if (rr, cc) in grid:
                A, B = masks[i], masks[grid[(rr, cc)]]
                par.append((i, grid[(rr, cc)], round(float((A & B).sum() / max((A | B).sum(), 1)), 2)))
    luft = {}
    for k, mk in masks.items():
        ys, xs = np.nonzero(mk)
        if len(xs) > 10:
            hull = MultiPoint(list(zip(xs[::7].tolist(), ys[::7].tolist()))).convex_hull
            luft[k] = round(1.0 - float(mk.sum()) / max(hull.area, 1.0), 2)
    ut = dict(iou_snitt=round(float(np.mean([p[2] for p in par])), 2), iou_maks=max(p[2] for p in par), iou_par=par, luft=luft,
              klipt_av_ramma=klipt, kamera=KAM)
    json.dump(ut, open(os.path.join(HER, 'tal_brett.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in ut.items() if k != 'iou_par'}, ensure_ascii=False), 'brett %.0f s' % (time.time() - t0))


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    os.makedirs(os.path.join(HER, 'flis'), exist_ok=True)
    a = sys.argv[1:] or ['mek']
    {'mek': k_mek, 'brett': k_brett}[a[0]]()
