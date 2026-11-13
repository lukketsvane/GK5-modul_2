# -*- coding: utf-8 -*-
"""
lampe.py  ·  Ruta på fot: parametrisk CAD frå skissa 13.11 til samanstilling

Lampa: rund fot, éin arm av 5 mm aluminiumsplate, ein bjelke med LED-stripe som lyser inn i kanten på ei plate
(lysleiar), prismearket frå monitoren oppå plata, og ein knott som held hellinga med friksjon.
Alt er i mm. Origo er midt i foten på bordflata. x mot høgre, y bort frå brukaren, z opp.

  python lampe.py            byggjer alt, kontrollerer og eksporterer til ut/
  python lampe.py kontroll   berre kontrollane (kollisjon, masse, tyngdepunkt, velt, rørsle)

Måla merkte KONTROLLMÅL kjem frå foto og må målast med skyvelære før noko blir skore.
"""
import math, os, sys, json
import cadquery as cq

HER = os.path.dirname(os.path.abspath(__file__))
UT = os.path.join(HER, 'ut')

# ------------------------------------------------------------------ proporsjonar (namngjevne, så formsøket kan setje dei)
RUTE_B = 300.0        # breidd på ruta langs bjelken. KONTROLLMÅL: arket er anslått til om lag 250 × 440 mm, med rillene langs kortsida
RUTE_D = 190.0        # djupn på ruta frå innspent kant til fri kant. Går langs rillene, altså kortsida på arket (må vere under 250)
VINKEL = 35.0         # hellinga i teikninga, grader under vassrett (0 = ruta ligg flatt, peikar mot brukaren)
VINKEL_OMRAADE = (0.0, 80.0)
AKSE_H = 260.0        # høgda på bjelkeaksen over bordet
BJELKE_D = 32.0       # diameter på bjelken (og leddhuset)
FOT_D = 158.0         # 196 cm². Krav F9: høgst 200 cm²
FOT_H = 16.0
ARM_B = 40.0          # breidd på armen
ARM_T = 5.0           # platetjukn, EN AW-5754 H22 (kan bøyast kaldt)
ARM_UT = 70.0         # kor langt armen svingar ut mot høgre frå fot til topp. Flyttar ruta inn over foten
KNOTT_D = 44.0
KNOTT_L = 18.0

# ------------------------------------------------------------------ materiale og innkjøp
RUTE_T = 3.0          # lysleiarplata (PMMA). KONTROLLMÅL om plata frå monitoren blir brukt (2 til 3 mm)
FILM_T = 0.25         # prismearket. KONTROLLMÅL (anslått 0,2 ± 0,15)
LED_B = 8.0           # breidd på LED-stripa (COB 5 V). Lomma tek opp til 10 mm
ALU_B, ALU_T = 12.0, 2.0     # flatstong bak stripa: kjøleflate og avstiving
BALLAST_D = 120.0
BALLAST_T = 3.0       # stålplate. Vald slik at lampa held 1,2 kg (krav F8)

RHO = dict(petg=1.27e-3 * 0.55, pmma=1.19e-3, alu=2.70e-3, staal=7.85e-3, messing=8.5e-3, film=1.3e-3, gummi=1.1e-3)   # g/mm³. PETG: 55 % fylt i snitt

# ------------------------------------------------------------------ avleidde mål
R = BJELKE_D / 2
XF = 40.0                         # armen ved foten (midt i breidda)
YA = 44.0                         # armen: midtplanet i y
XT = XF + ARM_UT                  # armen i toppen
YB = YA - ARM_T / 2 - 1.0 - R     # bjelkeaksen i y
X_LH0, X_LH1 = XT - ARM_B / 2, XT + ARM_B / 2          # leddhuset
SKIVE_T = 1.0                     # friksjonsskive mellom bjelke og leddhus
X_BJ1 = X_LH0 - SKIVE_T           # høgre ende av bjelken
MASSIV = 18.0                     # massiv sone i høgre ende (boltehovudet)
X_RUTE1 = X_BJ1 - MASSIV - 2.0    # høgre kant av ruta
X_RUTE0 = X_RUTE1 - RUTE_B
X_BJ0 = X_RUTE0 - 5.0             # venstre ende av bjelken
X_KN0 = X_LH1 + 3.0               # knotten (3 mm til skiver)
BOLT_L = 70.0
X_BOLT0 = X_BJ1 - 12.0            # anleggsflata til boltehovudet
SPALTE = RUTE_T + FILM_T + 0.05   # det som blir klemt
U_KANT = 3.9                      # plata sin innspente kant, målt frå bjelkeaksen
U_SKRUE = 9.5                     # skruane gjennom lok og plate
SKRUAR_X = [X_RUTE0 + f * RUTE_B for f in (0.08, 0.36, 0.64, 0.92)]
TAB_L = 34.0
R_INN = 6.0                       # innvendig bøyeradius på fotfliken
Z_BOY = FOT_H + ARM_T + R_INN     # der bøyen går over i den rette armen
Y_BOY = YA - ARM_T / 2 - R_INN    # senter for bøyen
TAB_SKRUAR = [(XF - 10.0, Y_BOY - TAB_L / 2), (XF + 10.0, Y_BOY - TAB_L / 2)]
KABEL_XY = (XF, YA + ARM_T / 2 + 5.5)
TOPP_T = 2.4                      # toppflata på foten
VEGG = 6.0
BOSS_R = 66.0
BOSS_V = (20.0, 140.0, 260.0)

def _syl_x(d, x0, x1, y=0.0, z=0.0):
    return cq.Workplane('YZ', origin=(x0, 0, 0)).center(y, z).circle(d / 2).extrude(x1 - x0)
def _syl_z(d, z0, z1, x=0.0, y=0.0):
    return cq.Workplane('XY', origin=(0, 0, z0)).center(x, y).circle(d / 2).extrude(z1 - z0)
def _syl_y(d, y0, y1, x=0.0, z=0.0):
    return cq.Workplane('XZ', origin=(0, y1, 0)).center(x, z).circle(d / 2).extrude(y1 - y0)
def _boks(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
def _sekskant_x(nv, x0, x1, y=0.0, z=0.0):
    return cq.Workplane('YZ', origin=(x0, 0, 0)).center(y, z).polygon(6, nv / math.cos(math.radians(30))).extrude(x1 - x0)

def _paa_plass(lokal, vinkel):
    """Frå bjelken sitt eige system (x langs aksen, u ut i ruta, w mot undersida) til rommet."""
    return lokal.rotate((0, 0, 0), (1, 0, 0), 180.0 + vinkel).translate((0, YB, AKSE_H))

# ------------------------------------------------------------------ bjelken (lokalt system: y = u, z = w)

def _bjelke_lokal():
    syl = _syl_x(BJELKE_D, X_BJ0, X_BJ1)
    h = SPALTE / 2
    x0, x1 = X_RUTE0 - 0.5, X_RUTE1 + 0.5
    hol = (_boks(x0, x1, U_KANT - 0.3, R + 2, -h, h)                              # spalta til plata
           .union(_boks(x0, x1, 0.8, U_KANT - 0.3, -(LED_B + 2.4) / 2, (LED_B + 2.4) / 2))    # LED-stripa
           .union(_boks(x0, x1, -1.3, 0.8, -(ALU_B + 0.4) / 2, (ALU_B + 0.4) / 2)))           # flatstonga bak
    hol = hol.union(_sekskant_x(13.4, X_BOLT0 - 5.6, X_BOLT0)).union(_syl_x(8.4, X_BOLT0, X_BJ1 + 1))
    lokkrom = _boks(X_BJ0 - 1, X_BJ1 + 1, -1.3, R + 2, -R - 2, -h)
    kropp = syl.cut(lokkrom).cut(hol)
    lok = syl.intersect(_boks(X_BJ0 - 1, X_BJ1 + 1, -1.3 + 0.15, R + 2, -R - 2, -h)).cut(hol)
    for x in SKRUAR_X:
        kropp = kropp.cut(_syl_z(4.0, h, h + 6.5, x, U_SKRUE))                    # innpressmutter M3
        lok = lok.cut(_syl_z(3.4, -R - 1, -h + 0.1, x, U_SKRUE))
        lok = lok.cut(cq.Workplane('XY', origin=(x, U_SKRUE, -math.sqrt(R * R - U_SKRUE ** 2) - 0.2))
                      .circle(3.2).extrude(2.4))                                  # forsenking til skruehovudet
    kropp = kropp.cut(_syl_y(4.5, -R - 1, 0.9, X_RUTE1 - 8.0, 0.0))               # kabelen ut bak
    stopp = _syl_x(4.0, X_BJ1 - 0.1, X_BJ1 + SKIVE_T + 2.6, -11.0, 0.0)           # stoppinne i endeflata
    kropp = kropp.union(stopp)
    return kropp, lok

def _rute_lokal():
    h = SPALTE / 2
    plate = _boks(X_RUTE0, X_RUTE1, U_KANT, U_KANT + RUTE_D, h - RUTE_T, h)
    # fri kant skoren 45° mot undersida: lyset som når kanten, går ned på bordet og ikkje mot auget
    kile = (cq.Workplane('YZ', origin=(X_RUTE0 - 1, 0, 0))
            .polyline([(U_KANT + RUTE_D - RUTE_T, h - RUTE_T - 0.01), (U_KANT + RUTE_D + 0.01, h - RUTE_T - 0.01),
                       (U_KANT + RUTE_D + 0.01, h + 0.01)]).close().extrude(RUTE_B + 2))
    plate = plate.cut(kile)
    film = _boks(X_RUTE0, X_RUTE1, U_KANT, U_KANT + RUTE_D - 6.0, h - RUTE_T - FILM_T, h - RUTE_T)
    for x in SKRUAR_X:
        plate = plate.cut(_syl_z(3.6, -5, 5, x, U_SKRUE)); film = film.cut(_syl_z(3.6, -5, 5, x, U_SKRUE))
    led = _boks(X_RUTE0 + 2, X_RUTE1 - 2, 0.8, 2.8, -LED_B / 2, LED_B / 2)
    alu = _boks(X_RUTE0 + 2, X_RUTE1 - 2, -1.2, 0.8, -ALU_B / 2, ALU_B / 2)
    return plate, film, led, alu

def _skruar_lokal():
    ut = []
    for x in SKRUAR_X:
        z0 = -math.sqrt(R * R - U_SKRUE ** 2) - 0.2
        ut.append(cq.Workplane('XY', origin=(x, U_SKRUE, z0)).circle(2.8).extrude(1.7)
                  .union(_syl_z(3.0, z0 + 1.7, z0 + 1.7 + 12.0 - 1.7, x, U_SKRUE)))
    return ut

# ------------------------------------------------------------------ armen

def _midtline(z):
    t = min(max((z - 45.0) / (AKSE_H - 30.0 - 45.0), 0.0), 1.0)
    return XF + ARM_UT * (3 * t * t - 2 * t ** 3)

def _kantar(n, z0=None):
    """Høgre og venstre kant av armen: punkt 20 mm til kvar side av midtlina, målt vinkelrett på ho."""
    z0 = Z_BOY if z0 is None else z0
    zs = [z0 + (AKSE_H - z0) * i / n for i in range(n + 1)]
    v, h = [], []
    for z in zs:
        dz = 0.5
        dx = (_midtline(z + dz) - _midtline(z - dz)) / (2 * dz)
        l = math.hypot(dx, 1.0); nx, nz = 1.0 / l, -dx / l
        x = _midtline(z)
        h.append((x + nx * ARM_B / 2, z + nz * ARM_B / 2)); v.append((x - nx * ARM_B / 2, z - nz * ARM_B / 2))
    h[0] = (XF + ARM_B / 2, z0); v[0] = (XF - ARM_B / 2, z0)
    h[-1] = (XT + ARM_B / 2, AKSE_H); v[-1] = (XT - ARM_B / 2, AKSE_H)
    return h, v

def arm_omriss(n=90):
    """Omrisset av den rette delen av armen i xz-planet som polygon (til DXF): frå bøyen til toppen."""
    h, v = _kantar(n)
    boge = [(XT + ARM_B / 2 * math.cos(a), AKSE_H + ARM_B / 2 * math.sin(a)) for a in [math.pi * i / 24 for i in range(1, 24)]]
    return h + boge + v[::-1]

def arm():
    h, v = _kantar(14)
    blad = (cq.Workplane('XZ', origin=(0, YA + ARM_T / 2, 0)).moveTo(*h[0])
            .spline(h[1:], tangents=[(0, 1), (0, 1)], includeCurrent=True)
            .threePointArc((XT, AKSE_H + ARM_B / 2), v[-1])
            .spline(v[::-1][1:], tangents=[(0, -1), (0, -1)], includeCurrent=True)
            .close().extrude(ARM_T))
    # bøyen: kvartsirkel frå den loddrette armen fram til fliken som ligg på foten
    boy = (cq.Workplane('YZ', origin=(XF - ARM_B / 2, 0, 0))
           .moveTo(Y_BOY + R_INN, Z_BOY).lineTo(Y_BOY + R_INN + ARM_T, Z_BOY)
           .threePointArc((Y_BOY + (R_INN + ARM_T) * math.cos(math.radians(-45)), Z_BOY + (R_INN + ARM_T) * math.sin(math.radians(-45))),
                          (Y_BOY, Z_BOY - R_INN - ARM_T))
           .lineTo(Y_BOY, Z_BOY - R_INN)
           .threePointArc((Y_BOY + R_INN * math.cos(math.radians(-45)), Z_BOY + R_INN * math.sin(math.radians(-45))),
                          (Y_BOY + R_INN, Z_BOY)).close().extrude(ARM_B))
    flik = _boks(XF - ARM_B / 2, XF + ARM_B / 2, Y_BOY - TAB_L, Y_BOY, FOT_H, FOT_H + ARM_T)
    a = blad.union(boy).union(flik)
    for x, y in TAB_SKRUAR:
        a = a.cut(_syl_z(5.5, FOT_H - 1, FOT_H + ARM_T + 1, x, y))
        a = a.cut(cq.Workplane('XY', origin=(x, y, FOT_H + ARM_T - 2.6)).circle(5.2).extrude(2.7))
    for dx in (-12.0, 12.0):
        a = a.cut(_syl_y(4.5, YA - ARM_T / 2 - 1, YA + ARM_T / 2 + 1, XT + dx, AKSE_H))
        a = a.cut(_syl_y(8.4, YA + ARM_T / 2 - 2.2, YA + ARM_T / 2 + 0.1, XT + dx, AKSE_H))
    return a

def kabeldeksel():
    """Trykt list på baksida av armen. Kabelen ligg i sporet."""
    n = 14
    zs = [FOT_H + 2 + (AKSE_H - 22 - FOT_H - 2) * i / n for i in range(n + 1)]
    def band(halv, y0, t):
        hv = [(_midtline(max(z, Z_BOY)) + halv, z) for z in zs]; vv = [(_midtline(max(z, Z_BOY)) - halv, z) for z in zs]
        return (cq.Workplane('XZ', origin=(0, y0, 0)).moveTo(*hv[0]).spline(hv[1:], includeCurrent=True)
                .lineTo(*vv[-1]).spline(vv[::-1][1:], includeCurrent=True).close().extrude(t))
    return band(5.0, YA + ARM_T / 2 + 4.0, 4.0).cut(band(2.0, YA + ARM_T / 2 + 2.8, 2.9))

# ------------------------------------------------------------------ ledd og knott

def leddhus():
    k = _syl_x(BJELKE_D, X_LH0, X_LH1, YB, AKSE_H).union(_boks(X_LH0, X_LH1, YB, YA - ARM_T / 2, AKSE_H - 12, AKSE_H + 12))
    k = k.cut(_syl_x(8.4, X_LH0 - 1, X_LH1 + 1, YB, AKSE_H))
    for dx in (-12.0, 12.0):
        k = k.cut(_syl_y(5.6, YA - ARM_T / 2 - 8.0, YA - ARM_T / 2 + 0.1, XT + dx, AKSE_H))      # innpressmutter M4
    # spor for stoppinnen: pinnen står 11 mm frå aksen, på baksida av bjelken. Sporet dekkjer hellingsområdet
    a0, a1 = VINKEL_OMRAADE
    pk = []
    for i in range(25):
        a = math.radians(a0 - 3 + (a1 - a0 + 6) * i / 24)
        pk.append((YB + 11.0 * math.cos(a), AKSE_H + 11.0 * math.sin(a)))
    spor = None
    for (y, z) in pk:
        s = _syl_x(4.8, X_LH0 - 0.1, X_LH0 + 3.2, y, z)
        spor = s if spor is None else spor.union(s)
    return k.cut(spor)

def knott():
    k = _syl_x(KNOTT_D, X_KN0, X_KN0 + KNOTT_L, YB, AKSE_H).edges().chamfer(1.2)
    k = k.cut(_syl_x(18.0, X_KN0 - 0.1, X_KN0 + 0.6, YB, AKSE_H))                 # skive
    k = k.cut(_sekskant_x(13.2, X_KN0, X_KN0 + 8.6, YB, AKSE_H))                 # låsemutteren sit i knotten
    k = k.cut(_syl_x(8.6, X_KN0, X_KN0 + KNOTT_L - 3.0, YB, AKSE_H))
    # ringforma lomme på innsida: sparer 60 g messing, så lampa held 1,2 kg
    k = k.cut(_syl_x(36.0, X_KN0 - 0.1, X_KN0 + 10.0, YB, AKSE_H).cut(_syl_x(21.0, X_KN0 - 1, X_KN0 + 11, YB, AKSE_H)))
    return k

def bolt():
    return _sekskant_x(13.0, X_BOLT0 - 5.3, X_BOLT0, YB, AKSE_H).union(_syl_x(8.0, X_BOLT0, X_BOLT0 + BOLT_L, YB, AKSE_H))
def mutter():
    return _sekskant_x(13.0, X_KN0 + 0.4, X_KN0 + 8.4, YB, AKSE_H).cut(_syl_x(8.0, X_KN0, X_KN0 + 9, YB, AKSE_H))
def skive_ledd():      # friksjonsskive mellom bjelke og leddhus (kork eller gummi)
    return _syl_x(17.0, X_BJ1, X_LH0, YB, AKSE_H).cut(_syl_x(8.6, X_BJ1 - 1, X_LH0 + 1, YB, AKSE_H))
def skiver_knott():    # glideskive (nylon) og stålskive under knotten
    return _syl_x(17.0, X_LH1, X_KN0, YB, AKSE_H).cut(_syl_x(8.4, X_LH1 - 1, X_KN0 + 1, YB, AKSE_H))

# ------------------------------------------------------------------ foten

def fot():
    f = _syl_z(FOT_D, 0, FOT_H).faces('>Z').edges().fillet(2.0)
    f = f.cut(_syl_z(FOT_D - 2 * VEGG, -0.1, FOT_H - TOPP_T))
    for v in BOSS_V:
        x, y = BOSS_R * math.cos(math.radians(v)), BOSS_R * math.sin(math.radians(v))
        f = f.union(_syl_z(9.0, 2.0, FOT_H - TOPP_T + 0.1, x, y).union(
            _boks(-4.5, 4.5, 0, FOT_D / 2 - VEGG - BOSS_R + 1.0, 2.0, FOT_H - TOPP_T + 0.1)
            .translate((0, BOSS_R, 0)).rotate((0, 0, 0), (0, 0, 1), v - 90.0)))
        f = f.cut(_syl_z(4.0, 1.9, 8.5, x, y))
    for x, y in TAB_SKRUAR:
        f = f.cut(_syl_z(5.6, FOT_H - TOPP_T - 1, FOT_H + 1, x, y))
    f = f.cut(_syl_z(6.0, FOT_H - TOPP_T - 1, FOT_H + 1, *KABEL_XY))               # kabelen ned bak armen
    f = f.cut(_boks(-3.0, 3.0, FOT_D / 2 - VEGG - 1, FOT_D / 2 + 1, -0.1, 4.5))    # kabelen ut bak
    return f

def botnlok():
    l = _syl_z(FOT_D - 2 * VEGG - 0.6, 0, 2.0)
    for v in BOSS_V:
        x, y = BOSS_R * math.cos(math.radians(v)), BOSS_R * math.sin(math.radians(v))
        l = l.cut(_syl_z(3.4, -1, 3, x, y)).cut(_syl_z(6.4, -0.1, 1.0, x, y))
    return l.cut(_boks(-3.0, 3.0, FOT_D / 2 - VEGG - 4, FOT_D / 2, -0.1, 2.1))

def ballast():
    b = _syl_z(BALLAST_D, FOT_H - TOPP_T - BALLAST_T, FOT_H - TOPP_T)
    for x, y in TAB_SKRUAR:
        b = b.cut(_syl_z(4.2, 0, FOT_H, x, y))                                    # gjengast M5
    return b

def fotskruar():
    ut = []
    for x, y in TAB_SKRUAR:
        ut.append(cq.Workplane('XY', origin=(x, y, FOT_H + ARM_T - 2.6)).circle(4.8).extrude(2.6)
                  .union(_syl_z(5.0, FOT_H - TOPP_T - BALLAST_T, FOT_H + ARM_T - 2.6, x, y)))
    return ut

# ------------------------------------------------------------------ samanstilling

FARGE = dict(fot=(0.42, 0.10, 0.10), bjelke=(0.42, 0.10, 0.10), arm=(0.78, 0.78, 0.76), knott=(0.80, 0.66, 0.36),
             rute=(0.92, 0.96, 1.0), film=(1.0, 0.93, 0.80), staal=(0.45, 0.46, 0.48), led=(1.0, 0.85, 0.5),
             svart=(0.1, 0.1, 0.1), skive=(0.55, 0.42, 0.30))

def delar(vinkel=VINKEL):
    """Alle delane på plass. Gjev liste med (id, namn, form, materiale, farge, tal, prosess)."""
    kropp, lok = _bjelke_lokal()
    plate, film, led, alu = _rute_lokal()
    P = lambda s: _paa_plass(s, vinkel)
    skruar = [P(s) for s in _skruar_lokal()]
    D = [
        ('01', 'fot', fot(), 'petg', 'fot', 1, 'trykt (produksjon: trykkstøypt aluminium, pulverlakk)'),
        ('02', 'botnlok', botnlok(), 'petg', 'svart', 1, 'trykt'),
        ('03', 'ballast', ballast(), 'staal', 'staal', 1, 'stålplate %g mm, laserskoren, 2 × M5 gjenga' % BALLAST_T),
        ('04', 'arm', arm(), 'alu', 'arm', 1, 'aluminium 5 mm EN AW-5754, skoren og bøygd éin gong'),
        ('05', 'kabeldeksel', kabeldeksel(), 'petg', 'svart', 1, 'trykt, limt på baksida av armen'),
        ('06', 'leddhus', leddhus(), 'petg', 'bjelke', 1, 'trykt (produksjon: maskinert aluminium)'),
        ('07', 'bjelke', P(kropp), 'petg', 'bjelke', 1, 'trykt i to lengder (produksjon: ekstrudert aluminium)'),
        ('08', 'bjelkelok', P(lok), 'petg', 'bjelke', 1, 'trykt i to lengder'),
        ('09', 'lysleiar', P(plate), 'pmma', 'rute', 1, 'PMMA %g mm, frå monitoren eller akrylplate, kantane polerte' % RUTE_T),
        ('10', 'prismeark', P(film), 'film', 'film', 1, 'frå monitoren, prisma opp, rillene på tvers av bjelken (langs kortsida på arket)'),
        ('11', 'flatstong', P(alu), 'alu', 'arm', 1, 'aluminium 12 × 2 × %.0f' % (RUTE_B - 4)),
        ('12', 'led-stripe', P(led), 'gummi', 'led', 1, 'KJØP: COB 5 V, 2700 K, 8 mm, %.0f mm, med USB og dimmar' % (RUTE_B - 4)),
        ('13', 'knott', knott(), 'messing', 'knott', 1, 'dreia messing (prototyp: trykt)'),
        ('14', 'friksjonsskive', skive_ledd(), 'gummi', 'skive', 1, 'kork eller gummi 1 mm, Ø 17 med hol Ø 8,6'),
        ('A', 'bolt M8 × 70', bolt(), 'staal', 'staal', 1, 'sekskant, DIN 933'),
        ('B', 'låsemutter M8', mutter(), 'staal', 'staal', 1, 'DIN 985'),
        ('C', 'skiver M8', skiver_knott(), 'staal', 'staal', 2, 'éi nylon, éi stål'),
        ('D', 'skrue M5 × 12 senk', fotskruar()[0].union(fotskruar()[1]), 'staal', 'staal', 2, 'ISO 10642'),
        ('E', 'skrue M3 × 12 senk', skruar[0].union(skruar[1]).union(skruar[2]).union(skruar[3]), 'staal', 'staal', 4, 'ISO 10642, med innpressmutter M3'),
    ]
    return D

LAUSE = [('F', 'skrue M4 × 10 senk', 2, 'armen til leddhuset, med innpressmutter M4'),
         ('G', 'skrue M3 × 8 senk', 3, 'botnloket, med innpressmutter M3'),
         ('H', 'innpressmutter M3', 7, 'messing, varmepressa'), ('I', 'innpressmutter M4', 2, 'messing, varmepressa'),
         ('J', 'gummiføter Ø 10', 3, 'under botnloket')]

def vol(s): return s.val().Volume()
def tp(s):
    c = s.val().Center(); return (c.x, c.y, c.z)

def kontroll(vis=True):
    D = delar()
    rap = dict(delar=[], kollisjonar=[], rorsle=[])
    M = 0.0; mx = my = mz = 0.0
    for (i, namn, s, mat, _, n, _) in D:
        v = vol(s); m = v * RHO[mat]; c = tp(s)
        rap['delar'].append(dict(id=i, namn=namn, volum_cm3=round(v / 1000, 1), masse_g=round(m, 1), gyldig=bool(s.val().isValid())))
        M += m; mx += m * c[0]; my += m * c[1]; mz += m * c[2]
    ekstra = 25.0          # kabel, skruar som ikkje er modellerte, innpressmutrar
    M += ekstra
    T = (mx / M, my / M, mz / M)
    r = FOT_D / 2
    e = math.hypot(T[0], T[1])
    rap.update(masse_g=round(M), tyngdepunkt=[round(t, 1) for t in T], fotavtrykk_cm2=round(math.pi * r * r / 100, 1),
               veltevinkel=round(math.degrees(math.atan((r - e) / T[2])), 1))
    g = 9.81e-3
    # kraft som veltar lampa: trykk ned på ytste venstre hjørne av ruta, og på fremste kant
    xv = X_RUTE0; rap['velt_venstre_N'] = round(M * g * (r + T[0]) / max(-xv - r, 1e-6), 1)
    yf = YB - (U_KANT + RUTE_D); rap['velt_framme_N'] = round(M * g * (r + T[1]) / max(-yf - r, 1e-6), 1)
    rap['velt_dytt_topp_N'] = round(M * g * (r - e) / AKSE_H, 1)
    # kollisjonar: alle par, unnateke dei som skal gå i kvarandre (skruar i hol, bolt i hol)
    fri = {'A', 'B', 'C', 'D', 'E'}
    for a in range(len(D)):
        for b_ in range(a + 1, len(D)):
            if D[a][0] in fri or D[b_][0] in fri: continue
            try:
                v = vol(D[a][2].intersect(D[b_][2]))
            except Exception:
                v = 0.0
            if v > 0.5: rap['kollisjonar'].append((D[a][1], D[b_][1], round(v, 1)))
    # rørsle: ruta og bjelken i heile hellingsområdet mot dei faste delane og bordet
    faste = [d for d in D if d[0] in ('01', '04', '05', '06')]
    for vk in range(int(VINKEL_OMRAADE[0]), int(VINKEL_OMRAADE[1]) + 1, 10):
        Dv = delar(float(vk))
        rorl = [d for d in Dv if d[0] in ('07', '08', '09', '10')]
        verst = 0.0; kven = ''
        for a in rorl:
            for b_ in faste:
                try: v = vol(a[2].intersect(b_[2]))
                except Exception: v = 0.0
                if a[0] == '07' and b_[0] == '06': continue          # stoppinnen går i sporet
                if v > verst: verst, kven = v, a[1] + ' mot ' + b_[1]
        zmin = min(d[2].val().BoundingBox().zmin for d in rorl)
        rap['rorsle'].append(dict(vinkel=vk, kollisjon_mm3=round(verst, 1), kven=kven, laagaste_punkt=round(zmin, 1)))
    if vis:
        print('masse %d g (krav 1200)  ·  fotavtrykk %.1f cm² (krav 200)  ·  tyngdepunkt x %.1f y %.1f z %.1f' % (rap['masse_g'], rap['fotavtrykk_cm2'], *rap['tyngdepunkt']))
        print('veltevinkel %.1f°  ·  velt ved trykk på venstre hjørne %.1f N, fremste kant %.1f N, dytt i toppen %.1f N' % (rap['veltevinkel'], rap['velt_venstre_N'], rap['velt_framme_N'], rap['velt_dytt_topp_N']))
        for d in rap['delar']: print('  %-3s %-16s %7.1f cm³ %7.1f g %s' % (d['id'], d['namn'], d['volum_cm3'], d['masse_g'], '' if d['gyldig'] else 'UGYLDIG'))
        print('kollisjonar:', rap['kollisjonar'] or 'ingen')
        for r_ in rap['rorsle']: print('  helling %2d°: kollisjon %.1f mm³ %s · lågaste punkt %.0f mm over bordet' % (r_['vinkel'], r_['kollisjon_mm3'], r_['kven'], r_['laagaste_punkt']))
    return rap

# ------------------------------------------------------------------ eksport

def samanstilling(vinkel=VINKEL):
    a = cq.Assembly(name='ruta-pa-fot')
    for (i, namn, form, mat, farge, n, _) in delar(vinkel):
        a.add(form, name='%s_%s' % (i, namn.replace(' ', '_').replace('×', 'x')), color=cq.Color(*FARGE[farge]))
    return a

def utbreidd_arm():
    """Armen flat, før bøying. Gjev (omriss, hol [(x, z, d)], bøyeline z). K-faktor 0,4."""
    ba = math.pi / 2 * (R_INN + 0.4 * ARM_T)
    botn = Z_BOY - ba - TAB_L
    om = arm_omriss()
    om = [(XF + ARM_B / 2, botn)] + om + [(XF - ARM_B / 2, botn)]
    hol = [(x, Z_BOY - ba - (Y_BOY - y), 5.5) for x, y in TAB_SKRUAR] + [(XT - 12.0, AKSE_H, 4.5), (XT + 12.0, AKSE_H, 4.5)]
    return om, hol, Z_BOY - ba / 2, ba

def _dxf(fil, omriss=None, sirklar=(), liner=(), ytre_sirkel=None):
    import ezdxf
    d = ezdxf.new('R2010'); d.units = ezdxf.units.MM
    d.layers.add('SKJER', color=7); d.layers.add('BOY', color=1)
    m = d.modelspace()
    if omriss: m.add_lwpolyline(omriss, close=True, dxfattribs={'layer': 'SKJER'})
    if ytre_sirkel: m.add_circle((0, 0), ytre_sirkel, dxfattribs={'layer': 'SKJER'})
    for (x, y, dia) in sirklar: m.add_circle((x, y), dia / 2, dxfattribs={'layer': 'SKJER'})
    for (a, b_) in liner: m.add_line(a, b_, dxfattribs={'layer': 'BOY'})
    d.saveas(fil)

def eksporter():
    from cadquery import exporters
    for m in ('step', 'stl', 'dxf'): os.makedirs(os.path.join(UT, m), exist_ok=True)
    a = samanstilling()
    a.export(os.path.join(UT, 'ruta-pa-fot.step'))
    a.export(os.path.join(UT, 'ruta-pa-fot.glb'), tolerance=0.05, angularTolerance=0.2)
    D = delar()
    for (i, namn, form, mat, _, n, _) in D:
        exporters.export(form, os.path.join(UT, 'step', '%s_%s.step' % (i, namn.replace(' ', '_').replace('×', 'x'))))
    # printfiler i printstilling (z opp frå plata)
    d = {x[0]: x[2] for x in D}
    kropp, lok = _bjelke_lokal()
    xm = 0.5 * (X_RUTE0 + X_RUTE1)
    def del_x(form, x0, x1): return form.intersect(_boks(x0, x1, -40, 40, -40, 40))
    staaande = lambda f: f.rotate((0, 0, 0), (0, 1, 0), -90)                      # aksen opp
    P = [('01_fot', d['01'].rotate((0, 0, 0), (1, 0, 0), 180)),                   # toppflata mot plata
         ('02_botnlok', d['02']),
         ('05_kabeldeksel', d['05'].rotate((0, 0, 0), (1, 0, 0), 90)),
         ('06_leddhus', staaande(d['06'])),
         ('07_bjelke_venstre', staaande(del_x(kropp, X_BJ0 - 1, xm - 12))),
         ('07_bjelke_hogre', staaande(del_x(kropp, xm - 12, X_BJ1 + 5))),
         ('08_bjelkelok_venstre', staaande(del_x(lok, X_BJ0 - 1, xm + 12))),
         ('08_bjelkelok_hogre', staaande(del_x(lok, xm + 12, X_BJ1 + 5))),
         ('13_knott_prototyp', d['13'].rotate((0, 0, 0), (0, 1, 0), 90))]
    for namn, f in P:
        bb = f.val().BoundingBox()
        f = f.translate((-0.5 * (bb.xmin + bb.xmax), -0.5 * (bb.ymin + bb.ymax), -bb.zmin))
        exporters.export(f, os.path.join(UT, 'stl', namn + '.stl'), tolerance=0.02, angularTolerance=0.1)
        bb = f.val().BoundingBox()
        print('  stl %-24s %5.0f x %5.0f x %5.0f mm' % (namn, bb.xlen, bb.ylen, bb.zlen))
    # flate delar
    om, hol, zb, ba = utbreidd_arm()
    _dxf(os.path.join(UT, 'dxf', '04_arm_utbreidd.dxf'), om, hol, [((XF - ARM_B / 2, zb), (XF + ARM_B / 2, zb))])
    _dxf(os.path.join(UT, 'dxf', '03_ballast.dxf'), None, [(x, y, 4.2) for x, y in TAB_SKRUAR], ytre_sirkel=BALLAST_D / 2)
    hy = U_SKRUE - U_KANT
    ruta = [(0, 0), (RUTE_B, 0), (RUTE_B, RUTE_D), (0, RUTE_D)]
    _dxf(os.path.join(UT, 'dxf', '09_lysleiar.dxf'), ruta, [(x - X_RUTE0, RUTE_D - hy, 3.6) for x in SKRUAR_X])
    _dxf(os.path.join(UT, 'dxf', '10_prismeark.dxf'), [(0, 6.0), (RUTE_B, 6.0), (RUTE_B, RUTE_D), (0, RUTE_D)], [(x - X_RUTE0, RUTE_D - hy, 3.6) for x in SKRUAR_X])
    _dxf(os.path.join(UT, 'dxf', '14_friksjonsskive.dxf'), None, [(0, 0, 8.6)], ytre_sirkel=8.5)
    json.dump(dict(bolengd=ba, boyeline_z=zb, utbreidd_lengd=max(p[1] for p in om) - min(p[1] for p in om)),
              open(os.path.join(UT, 'dxf', 'arm.json'), 'w'), indent=1)
    print('  armen utbreidd: %.1f mm lang, bøyeline %.1f mm frå nedste kant' % (max(p[1] for p in om) - min(p[1] for p in om), zb - min(p[1] for p in om)))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    os.makedirs(UT, exist_ok=True)
    rap = kontroll()
    rap['lause'] = LAUSE
    rap['stykkliste'] = [dict(id=i, namn=n, tal=t, materiale=m, prosess=pr) for (i, n, _, m, _, t, pr) in delar()]
    json.dump(rap, open(os.path.join(UT, 'kontroll.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    if sys.argv[1:2] != ['kontroll']:
        eksporter()
