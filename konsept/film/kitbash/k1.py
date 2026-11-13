# -*- coding: utf-8 -*-
"""
k1.py  ·  K1 Ruta på armen: ferdig CAD av lampa bygd på armen og hengselet frå projektoren

Armen står midt i foten, og ruta ligg symmetrisk om han (T-form). Med armen i den eine enden, slik ruta på fot har han,
kjem tyngdepunktet 5 cm utanfor midten og lampa veltar på 1,3 N.

Delane frå settet er teikna som enkle lekamar etter måla i modell/byggjesett/maal.json. Dei måla er anslag frå foto.
Overgangane er difor klemmer som toler nokre millimeter avvik:
  - festeplata på hengselet blir klemd mot ein sokkel med ei list og to klør. Ingen hol i plata trengst
  - ein sal blir tredd ned over kappa på toppen av armen og klemd med éin skrue
  - bjelken ligg i ei vogge framfor kappa og dreier i ho. Ein bremseskrue med knott held hellinga

  python k1.py            kontroll og eksport til k1/
  python k1.py kontroll   berre kontrollen

Origo midt i foten på bordflata. x mot høgre, y bort frå brukaren, z opp. Alt i mm.
"""
import os, sys, math, json
import cadquery as cq

HER = os.path.dirname(os.path.abspath(__file__))
SETT = os.path.abspath(os.path.join(HER, '..', '..', '..', 'modell', 'byggjesett'))
sys.path.insert(0, os.path.join(HER, '..', 'cad'))
import lampe as L
UT = os.path.join(HER, 'k1')

# ------------------------------------------------------------------ KONTROLLMÅL: delane frå settet (anslag frå foto)
_M = json.load(open(os.path.join(SETT, 'maal.json'), encoding='utf-8'))
def m(pid, k): return float(_M[pid][k][0])
def pm(pid, k): return float(_M[pid][k][1])
TAPP_D, TAPP_L = m('P01', 'tapp_d'), m('P01', 'tapp_lengd')            # A, B
KAPPE_B, KAPPE_H, KAPPE_L = m('P01', 'kappe_breidd'), m('P01', 'kappe_hogd'), m('P01', 'kappe_lengd')     # C, D
PROFIL_B, PROFIL_T, PROFIL_L = m('P01', 'profil_breidd'), m('P01', 'profil_tjukk'), m('P01', 'profil_lengd')   # E, F
PLATE_B, PLATE_L, PLATE_T = m('P02', 'breidd'), m('P02', 'lengd'), 2.0  # G, H, I
PLATE_NED = 62.0                  # J: frå hengselbolten ned til nedste kant av festeplata
KANAL_B = 32.0                    # K: breidda på kanalen armen står i
BOLT_TIL_TAPP = 12.0 + PROFIL_L - 20.0 + KAPPE_L - KAPPE_H / 2          # L: frå hengselbolten til tappen (304,5)
ARM_MATERIALE = 'alu'             # M: vei armen og hengselet. Er røyret av stål, veg armen om lag 250 g meir

# ------------------------------------------------------------------ proporsjonar
RUTE_B, RUTE_D = L.RUTE_B, L.RUTE_D
VINKEL = 35.0
VINKEL_OMRAADE = (0.0, 80.0)
FOT_D, FOT_H = 158.0, 16.0
AKSE_Y = 35.0                     # armen står 35 mm bak midten av foten, så ruta kjem over midten
BALLAST_D, BALLAST_T = 120.0, 0.0  # sett over 0 når armen er vegen og det er masse å gå på

AX, AY, AZ = 0.0, AKSE_Y, FOT_H + PLATE_NED                  # hengselbolten
ZP = AZ + BOLT_TIL_TAPP                                      # tappen og knoken i toppen av armen
R = L.R
KLARING = 0.4
YB = AY - KAPPE_H / 2 - 6.0 - (R + 0.2)                      # bjelkeaksen: framfor kappa, i høgd med tappen
SAL_B = KAPPE_B + 9.0                                        # salen er 4,5 mm tjukk på kvar side av kappa
BREMS_V = 50.0                                               # bremseskruen: 50° over vassrett, framme
X0, X1 = -RUTE_B / 2 - 5.0, RUTE_B / 2 + 5.0                 # bjelken
SKRUAR_X = [f * RUTE_B for f in (-0.42, -0.14, 0.14, 0.42)]
TOPP_T, VEGG = 2.4, 6.0
BOSS_R, BOSS_V = FOT_D / 2 - VEGG - 7.0, (60.0, 180.0, 300.0)
SOKKEL_B, SOKKEL_T = 88.0, 22.0
KLO_X = PLATE_B / 2 + 6.0                                    # skruane til klemmene står utanfor kanten på plata

RHO = dict(L.RHO, plast=1.05e-3)

def boks(x0, x1, y0, y1, z0, z1): return L._boks(x0, x1, y0, y1, z0, z1)
def sylx(d, x0, x1, y, z): return L._syl_x(d, x0, x1, y, z)
def sylz(d, z0, z1, x, y): return L._syl_z(d, z0, z1, x, y)
def syly(d, y0, y1, x, z): return L._syl_y(d, y0, y1, x, z)
def lok(x0, x1, y0, y1, z0, z1):
    """Boks gjeven i armen sitt eige system (x langs armen, y langs bolten, z på tvers), lagd på plass i rommet."""
    return boks(AX + y0, AX + y1, AY + z0, AY + z1, AZ + x0, AZ + x1)
def radial(radius, r0, r1, vinkel, x=0.0):
    """Sylinder langs ei retning i yz-planet ut frå bjelkeaksen. vinkel: grader over vassrett, framover."""
    v = math.radians(vinkel); d = cq.Vector(0, -math.cos(v), math.sin(v))
    p = cq.Vector(x, YB, ZP) + d * r0
    return cq.Workplane('XY').newObject([cq.Solid.makeCylinder(radius, r1 - r0, p, d)])

# ------------------------------------------------------------------ delane frå settet, som enkle lekamar

def sett():
    vegg = 1.5
    profil = lok(12, 12 + PROFIL_L, -PROFIL_T / 2, PROFIL_T / 2, -PROFIL_B / 2, PROFIL_B / 2) \
        .cut(lok(11, 13 + PROFIL_L, -PROFIL_T / 2 + vegg, PROFIL_T / 2 - vegg, -PROFIL_B / 2 + vegg, PROFIL_B / 2 - vegg))
    xk = 12 + PROFIL_L - 20
    kappe = lok(xk, BOLT_TIL_TAPP, -KAPPE_B / 2, KAPPE_B / 2, -KAPPE_H / 2, KAPPE_H / 2) \
        .union(sylx(KAPPE_H, AX - KAPPE_B / 2, AX + KAPPE_B / 2, AY, ZP)).cut(lok(xk - 1, 12 + PROFIL_L, -PROFIL_T / 2, PROFIL_T / 2, -PROFIL_B / 2, PROFIL_B / 2))
    # kappa er hol plast: 2,5 mm vegg (ANTAKING), så massen ikkje blir rekna som massiv
    kappe = kappe.cut(lok(xk + 2.5, BOLT_TIL_TAPP, -KAPPE_B / 2 + 2.5, KAPPE_B / 2 - 2.5, -KAPPE_H / 2 + 2.5, KAPPE_H / 2 - 2.5)
                      .union(sylx(KAPPE_H - 5.0, AX - KAPPE_B / 2 + 2.5, AX + KAPPE_B / 2 - 2.5, AY, ZP)))
    tapp = sylx(TAPP_D, AX - KAPPE_B / 2 - TAPP_L, AX - KAPPE_B / 2 + 2, AY, ZP)
    plate = lok(-PLATE_NED, PLATE_L - PLATE_NED, -PLATE_B / 2, PLATE_B / 2, -27.5, -27.5 + PLATE_T)
    kanal = lok(-27, 19, -KANAL_B / 2, KANAL_B / 2, -27.5 + PLATE_T, 27.5).cut(lok(-28, 20, -KANAL_B / 2 + 2, KANAL_B / 2 - 2, -22, 29))
    bolt = sylx(6.0, AX - 24.8, AX + 24.8, AY, AZ)
    spak = lok(-40.6, 10.6, -17, 17, 28.6, 31.0)
    fjoer = lok(-54.5, -18.4, 24.7, 31.3, -25.4, -18.8)
    return [('S1', 'arm P01: røyr', profil, ARM_MATERIALE), ('S2', 'arm P01: kappe', kappe, 'plast'), ('S3', 'arm P01: tapp', tapp, 'staal'),
            ('S4', 'hengsel P02: festeplate', plate, 'staal'), ('S5', 'hengsel P02: kanal', kanal.union(bolt), 'staal'),
            ('S6', 'hengsel P02: spak og fjør', spak.union(fjoer), 'staal')]

# ------------------------------------------------------------------ trykte delar

def fot():
    f = sylz(FOT_D, 0, FOT_H, 0, 0).faces('>Z').edges().fillet(2.0)
    f = f.cut(sylz(FOT_D - 2 * VEGG, -0.1, FOT_H - TOPP_T, 0, 0))
    for v in BOSS_V:
        x, y = BOSS_R * math.cos(math.radians(v)), BOSS_R * math.sin(math.radians(v))
        f = f.union(sylz(9.0, 2.0, FOT_H - TOPP_T + 0.1, x, y).union(
            boks(-4.5, 4.5, 0, FOT_D / 2 - VEGG - BOSS_R + 1.0, 2.0, FOT_H - TOPP_T + 0.1).translate((0, BOSS_R, 0)).rotate((0, 0, 0), (0, 0, 1), v - 90.0)))
        f = f.cut(sylz(4.0, 1.9, 8.5, x, y))
    # sokkelen: står framfor festeplata. Plata kviler på foten og blir klemd mot sokkelen bakfrå
    y1 = AY - 27.5; y0 = y1 - SOKKEL_T
    sokkel = boks(-SOKKEL_B / 2, SOKKEL_B / 2, y0, y1, FOT_H - 0.1, AZ + PLATE_L - PLATE_NED + 2.0).edges('|Z').fillet(3.0)
    fyll = boks(-SOKKEL_B / 2, SOKKEL_B / 2, y0, y1, 2.0, FOT_H - TOPP_T + 0.1)             # massivt under sokkelen
    f = f.union(sokkel).union(fyll)
    for sx in (-1, 1):
        for z in (AZ - PLATE_NED + 14.0, AZ + PLATE_L - PLATE_NED - 9.0):                   # innpressmutrar M4 til lista og klørne
            f = f.cut(syly(5.6, y1 - 9.0, y1 + 0.1, sx * KLO_X, z))
        f = f.cut(sylz(5.6, 1.9, 10.0, sx * 30.0, (y0 + y1) / 2))                           # M5 nedanfrå gjennom ballasten
    f = f.cut(sylz(6.0, FOT_H - TOPP_T - 1, FOT_H + 1, 0.0, AY + 27.5 + 8.0))               # kabelen ned bak armen
    f = f.cut(boks(-3.0, 3.0, FOT_D / 2 - VEGG - 1, FOT_D / 2 + 1, -0.1, 4.5))
    return f

def botnlok():
    l = sylz(FOT_D - 2 * VEGG - 0.6, 0, 2.0, 0, 0)
    for v in BOSS_V:
        x, y = BOSS_R * math.cos(math.radians(v)), BOSS_R * math.sin(math.radians(v))
        l = l.cut(sylz(3.4, -1, 3, x, y)).cut(sylz(6.4, -0.1, 1.0, x, y))
    y1 = AY - 27.5; y0 = y1 - SOKKEL_T
    l = l.cut(boks(-SOKKEL_B / 2 - 0.4, SOKKEL_B / 2 + 0.4, y0 - 0.4, y1 + 0.4, -0.1, 2.1))  # rundt fyllet under sokkelen
    return l.cut(boks(-3.0, 3.0, FOT_D / 2 - VEGG - 4, FOT_D / 2, -0.1, 2.1))

def klemlist():
    """Lista over nedste del av festeplata, og dei to klørne øvst. Skruane står utanfor plata."""
    yp = AY - 27.5 + PLATE_T                                   # baksida av plata
    z0 = AZ - PLATE_NED + 6.0
    lista = boks(-KLO_X - 7, KLO_X + 7, yp, yp + 12.0, z0, z0 + 16.0) \
        .cut(boks(22.0, 34.5, yp - 0.1, yp + 7.6, z0 - 0.1, z0 + 16.1))                    # lomme til fjøra: lista går bak ho
    lista = lista.union(boks(-KLO_X - 7, -PLATE_B / 2 - 0.6, yp - PLATE_T, yp, z0, z0 + 16.0)).union(boks(PLATE_B / 2 + 0.6, KLO_X + 7, yp - PLATE_T, yp, z0, z0 + 16.0))
    zt = AZ + PLATE_L - PLATE_NED - 16.0
    klor = None
    for sx in (-1, 1):
        k = boks(min(sx * (KANAL_B / 2 + 1.5), sx * (KLO_X + 7)), max(sx * (KANAL_B / 2 + 1.5), sx * (KLO_X + 7)), yp, yp + 7.0, zt, zt + 14.0)
        k = k.union(boks(min(sx * (PLATE_B / 2 + 0.6), sx * (KLO_X + 7)), max(sx * (PLATE_B / 2 + 0.6), sx * (KLO_X + 7)), yp - PLATE_T, yp, zt, zt + 14.0))
        klor = k if klor is None else klor.union(k)
    for sx in (-1, 1):
        lista = lista.cut(syly(4.5, yp - 3, yp + 13, sx * KLO_X, AZ - PLATE_NED + 14.0))
        klor = klor.cut(syly(4.5, yp - 3, yp + 8, sx * KLO_X, AZ + PLATE_L - PLATE_NED - 9.0))
    return lista, klor

def sal():
    """Salen: ei hylse ned over kappa, og ei vogge framfor ho som bjelken dreier i."""
    b = SAL_B / 2
    hylse = boks(-b, b, AY - KAPPE_H / 2 - 4.5, AY + KAPPE_H / 2 + 4.5, ZP - 40.0, ZP + KAPPE_H / 2 + 4.5).edges('|X').fillet(4.0)
    vogge = sylx(2 * (R + 0.2 + 6.0), -b, b, YB, ZP)
    steg = boks(-b, b, YB, AY - KAPPE_H / 2 - 4.0, ZP - (R + 6.2), ZP + (R + 6.2))
    brems = radial(8.0, R - 1.0, R + 14.0, BREMS_V)
    klemme = boks(-12, 12, AY + KAPPE_H / 2 + 4.0, AY + KAPPE_H / 2 + 14.5, ZP - 33.0, ZP - 17.0)
    s = hylse.union(vogge).union(steg).union(brems).union(klemme)
    # holrommet til kappa, opent nedover
    k = KLARING
    s = s.cut(boks(-KAPPE_B / 2 - k, KAPPE_B / 2 + k, AY - KAPPE_H / 2 - k, AY + KAPPE_H / 2 + k, ZP - 41.0, ZP)) \
        .cut(sylx(KAPPE_H + 2 * k, -KAPPE_B / 2 - k, KAPPE_B / 2 + k, AY, ZP))
    # spor til tappen, opent nedover
    s = s.cut(boks(-b - 0.1, -KAPPE_B / 2 - k + 0.1, AY - TAPP_D / 2 - 0.6, AY + TAPP_D / 2 + 0.6, ZP - 41.0, ZP)) \
        .cut(sylx(TAPP_D + 1.2, -b - 0.1, -KAPPE_B / 2 - k + 0.1, AY, ZP))
    # klemspalte bak, med skrue på tvers
    s = s.cut(boks(-1.0, 1.0, AY + KAPPE_H / 2 - 0.5, AY + KAPPE_H / 2 + 15.0, ZP - 41.0, ZP - 4.0))
    s = s.cut(sylx(4.5, -13, 13, AY + KAPPE_H / 2 + 9.5, ZP - 25.0))
    # vogga: boring til bjelken, og opning der ruta går ut og svingar
    s = s.cut(sylx(2 * (R + 0.2), -b - 1, b + 1, YB, ZP))
    a0, a1 = VINKEL_OMRAADE[0] - 10.0, VINKEL_OMRAADE[1] + 10.0
    pk = [(YB, ZP)] + [(YB - 60 * math.cos(math.radians(a)), ZP - 60 * math.sin(math.radians(a))) for a in [a0 + (a1 - a0) * i / 12 for i in range(13)]]
    s = s.cut(cq.Workplane('YZ', origin=(-b - 1, 0, 0)).polyline(pk).close().extrude(SAL_B + 2))
    s = s.cut(radial(2.8, R - 2.0, R + 15.0, BREMS_V))                                      # bremseskruen M5 (innpressmutter)
    return s

def knott():
    """Bremseskruen: M5 med messingknott og ein sko av nylon mot bjelken."""
    return radial(15.0, R + 15.0, R + 27.0, BREMS_V).union(radial(2.5, R + 1.0, R + 16.0, BREMS_V))

def klips(z):
    """Kabelklips rundt armrøyret."""
    t = 2.0
    k = boks(-PROFIL_T / 2 - t, PROFIL_T / 2 + t, AY - PROFIL_B / 2 - t, AY + PROFIL_B / 2 + t + 5.0, z, z + 8.0) \
        .cut(boks(-PROFIL_T / 2 - 0.2, PROFIL_T / 2 + 0.2, AY - PROFIL_B / 2 - 0.2, AY + PROFIL_B / 2 + 0.2, z - 1, z + 9))
    k = k.cut(boks(-2.5, 2.5, AY + PROFIL_B / 2, AY + PROFIL_B / 2 + 5.0, z - 1, z + 9)).cut(boks(-8.0, 8.0, AY - PROFIL_B / 2 - t - 1, AY - PROFIL_B / 2 + 0.3, z - 1, z + 9))
    return k

# ------------------------------------------------------------------ bjelken og ruta (same snitt som ruta på fot, symmetrisk)

def _bjelke_lokal():
    syl = L._syl_x(L.BJELKE_D, X0, X1)
    h = L.SPALTE / 2
    x0, x1 = -RUTE_B / 2 - 0.5, RUTE_B / 2 + 0.5
    hol = (L._boks(x0, x1, L.U_KANT - 0.3, R + 2, -h, h)
           .union(L._boks(x0, x1, 0.8, L.U_KANT - 0.3, -(L.LED_B + 2.4) / 2, (L.LED_B + 2.4) / 2))
           .union(L._boks(x0, x1, -1.3, 0.8, -(L.ALU_B + 0.4) / 2, (L.ALU_B + 0.4) / 2)))
    lokkrom = L._boks(X0 - 1, X1 + 1, -1.3, R + 2, -R - 2, -h)
    kropp = syl.cut(lokkrom).cut(hol)
    lokk = syl.intersect(L._boks(X0 - 1, X1 + 1, -1.3 + 0.15, R + 2, -R - 2, -h)).cut(hol)
    for x in SKRUAR_X:
        kropp = kropp.cut(L._syl_z(4.0, h, h + 6.5, x, L.U_SKRUE))
        lokk = lokk.cut(L._syl_z(3.4, -R - 1, -h + 0.1, x, L.U_SKRUE))
        lokk = lokk.cut(cq.Workplane('XY', origin=(x, L.U_SKRUE, -math.sqrt(R * R - L.U_SKRUE ** 2) - 0.2)).circle(3.2).extrude(2.4))
    kropp = kropp.cut(L._syl_y(4.5, -R - 1, 0.9, SAL_B / 2 + 8.0, 0.0))                     # kabelen ut bak, rett ved salen
    plate = L._boks(-RUTE_B / 2, RUTE_B / 2, L.U_KANT, L.U_KANT + RUTE_D, h - L.RUTE_T, h)
    kile = (cq.Workplane('YZ', origin=(-RUTE_B / 2 - 1, 0, 0))
            .polyline([(L.U_KANT + RUTE_D - L.RUTE_T, h - L.RUTE_T - 0.01), (L.U_KANT + RUTE_D + 0.01, h - L.RUTE_T - 0.01), (L.U_KANT + RUTE_D + 0.01, h + 0.01)])
            .close().extrude(RUTE_B + 2))
    plate = plate.cut(kile)
    film = L._boks(-RUTE_B / 2, RUTE_B / 2, L.U_KANT, L.U_KANT + RUTE_D - 6.0, h - L.RUTE_T - L.FILM_T, h - L.RUTE_T)
    skruar = None
    for x in SKRUAR_X:
        plate = plate.cut(L._syl_z(3.6, -5, 5, x, L.U_SKRUE)); film = film.cut(L._syl_z(3.6, -5, 5, x, L.U_SKRUE))
        z0 = -math.sqrt(R * R - L.U_SKRUE ** 2) - 0.2
        sk = cq.Workplane('XY', origin=(x, L.U_SKRUE, z0)).circle(2.8).extrude(1.7).union(L._syl_z(3.0, z0 + 1.7, z0 + 12.0, x, L.U_SKRUE))
        skruar = sk if skruar is None else skruar.union(sk)
    led = L._boks(-RUTE_B / 2 + 2, RUTE_B / 2 - 2, 0.8, 2.8, -L.LED_B / 2, L.LED_B / 2)
    alu = L._boks(-RUTE_B / 2 + 2, RUTE_B / 2 - 2, -1.2, 0.8, -L.ALU_B / 2, L.ALU_B / 2)
    return dict(kropp=kropp, lokk=lokk, plate=plate, film=film, led=led, alu=alu, skruar=skruar)

def paa_plass(lokal, vinkel):
    return lokal.rotate((0, 0, 0), (1, 0, 0), 180.0 + vinkel).translate((0, YB, ZP))

def ballast():
    b = sylz(BALLAST_D, FOT_H - TOPP_T - BALLAST_T, FOT_H - TOPP_T, 0, 0)
    y1 = AY - 27.5; y0 = y1 - SOKKEL_T
    return b.cut(boks(-SOKKEL_B / 2 - 0.6, SOKKEL_B / 2 + 0.6, y0 - 0.6, y1 + 0.6, 0, FOT_H))

FARGE = dict(trykt=(0.42, 0.10, 0.10), sett=(0.72, 0.73, 0.74), plast=(0.45, 0.46, 0.47), rute=(0.92, 0.96, 1.0), film=(1.0, 0.93, 0.80),
             staal=(0.45, 0.46, 0.48), led=(1.0, 0.85, 0.5), knott=(0.80, 0.66, 0.36), svart=(0.1, 0.1, 0.1))

def delar(vinkel=VINKEL):
    """(id, namn, form, materiale, farge, tal, framstilling)"""
    B = _bjelke_lokal(); P = lambda s: paa_plass(s, vinkel)
    lista, klor = klemlist()
    D = [(i, n, f, mat, 'plast' if mat == 'plast' else 'sett', 1, 'frå settet') for (i, n, f, mat) in sett()]
    D += [
        ('01', 'fot med sokkel', fot(), 'petg', 'trykt', 1, 'trykt, toppflata mot plata'),
        ('02', 'botnlok', botnlok(), 'petg', 'svart', 1, 'trykt'),
        ('03', 'klemlist', lista, 'petg', 'trykt', 1, 'trykt'),
        ('04', 'klør', klor, 'petg', 'trykt', 2, 'trykt'),
        ('05', 'sal', sal(), 'petg', 'trykt', 1, 'trykt, liggjande på sida'),
        ('06', 'knott med bremseskrue', knott(), 'alu', 'knott', 1, 'dreia aluminium eller messing på M5-skrue (prototyp: trykt)'),
        ('07', 'bjelke', P(B['kropp']), 'petg', 'trykt', 1, 'trykt i to lengder, ståande'),
        ('08', 'bjelkelok', P(B['lokk']), 'petg', 'trykt', 1, 'trykt i to lengder'),
        ('09', 'lysleiar', P(B['plate']), 'pmma', 'rute', 1, 'PMMA %g mm, frå monitoren eller akryl' % L.RUTE_T),
        ('10', 'prismeark', P(B['film']), 'film', 'film', 1, 'frå monitoren, prisma opp, rillene på tvers av bjelken'),
        ('11', 'flatstong', P(B['alu']), 'alu', 'sett', 1, 'aluminium 12 × 2 × %.0f' % (RUTE_B - 4)),
        ('12', 'led-stripe', P(B['led']), 'gummi', 'led', 1, 'KJØP: COB 5 V, 2700 K, 8 mm'),
        ('13', 'kabelklips', klips(AZ + 60).union(klips(AZ + 150)).union(klips(AZ + 215)), 'petg', 'svart', 3, 'trykt'),
        ('E', 'skrue M3 × 12 senk', P(B['skruar']), 'staal', 'staal', 4, 'gjennom lok og plate, med innpressmutter'),
    ]
    if BALLAST_T > 0:
        D.append(('14', 'ballast', ballast(), 'staal', 'staal', 1, 'stålplate %g mm' % BALLAST_T))
    return D

LAUSE = [('F', 'skrue M4 × 25', 2, 'lista, inn i sokkelen'), ('F2', 'skrue M4 × 20', 2, 'klørne, inn i sokkelen'), ('G', 'skrue M4 × 30', 1, 'klemmer salen om kappa'),
         ('H', 'skrue M3 × 8 senk', 3, 'botnloket'), ('I', 'innpressmutter M4', 5, ''), ('J', 'innpressmutter M3', 7, ''),
         ('K', 'innpressmutter M5', 1, 'bremseskruen i salen'), ('M', 'gummiføter Ø 10', 3, '')]

def vol(s): return s.val().Volume()

def kontroll(vis=True):
    D = delar()
    rap = dict(delar=[], kollisjonar=[], rorsle=[])
    M = mx = my = mz = 0.0
    for (i, namn, s, mat, *_r) in D:
        v = vol(s); ma = v * RHO[mat]; c = s.val().Center()
        rap['delar'].append(dict(id=i, namn=namn, masse_g=round(ma, 1), gyldig=bool(s.val().isValid())))
        M += ma; mx += ma * c.x; my += ma * c.y; mz += ma * c.z
    M += 30.0                                                # kabel, skruar og innpressmutrar
    T = (mx / M, my / M, mz / M); r = FOT_D / 2; e = math.hypot(T[0], T[1]); g = 9.81e-3
    t = math.radians(VINKEL)
    yf = YB - math.cos(t) * (L.U_KANT + RUTE_D)
    rap.update(masse_g=round(M), tyngdepunkt=[round(x, 1) for x in T], fotavtrykk_cm2=round(math.pi * r * r / 100, 1),
               veltevinkel=round(math.degrees(math.atan((r - e) / T[2])), 1),
               velt_hjorne_N=round(M * g * (r - abs(T[0])) / max(RUTE_B / 2 - r, 1e-6), 1),
               velt_framme_N=round(M * g * (r + T[1]) / max(-yf - r, 1e-6), 1), velt_dytt_topp_N=round(M * g * (r - e) / ZP, 1),
               hogd_akse=round(ZP, 1))
    # stålrøyr i staden for aluminium
    staal_ekstra = [d for d in D if d[0] == 'S1'][0]; rap['masse_staalroyr_g'] = round(M + vol(staal_ekstra[2]) * (RHO['staal'] - RHO['alu']))
    fri = {'E'}
    par_ok = {('S1', 'S2'), ('S2', 'S3'), ('S4', 'S5'), ('S1', 'S5'), ('S5', 'S6')}      # delar frå settet som heng saman
    for a in range(len(D)):
        for b_ in range(a + 1, len(D)):
            if D[a][0] in fri or D[b_][0] in fri or (D[a][0], D[b_][0]) in par_ok: continue
            try: v = vol(D[a][2].intersect(D[b_][2]))
            except Exception: v = 0.0
            if v > 0.5: rap['kollisjonar'].append((D[a][1], D[b_][1], round(v, 1)))
    faste = [d for d in D if d[0] in ('S1', 'S2', 'S4', 'S5', 'S6', '01', '03', '04', '05', '13')]
    for vk in range(int(VINKEL_OMRAADE[0]), int(VINKEL_OMRAADE[1]) + 1, 10):
        Dv = delar(float(vk)); rorl = [d for d in Dv if d[0] in ('07', '08', '09', '10')]
        verst = 0.0; kven = ''
        for a in rorl:
            for b_ in faste:
                try: v = vol(a[2].intersect(b_[2]))
                except Exception: v = 0.0
                if v > verst: verst, kven = v, a[1] + ' mot ' + b_[1]
        rap['rorsle'].append(dict(vinkel=vk, kollisjon_mm3=round(verst, 1), kven=kven, laagaste_punkt=round(min(d[2].val().BoundingBox().zmin for d in rorl), 1)))
    if vis:
        print('masse %d g (krav 1200; med stålrøyr %d g)  ·  fotavtrykk %.1f cm²  ·  tyngdepunkt x %.1f y %.1f z %.1f  ·  dreieaksen %.0f mm over bordet'
              % (rap['masse_g'], rap['masse_staalroyr_g'], rap['fotavtrykk_cm2'], *rap['tyngdepunkt'], ZP))
        print('veltevinkel %.1f°  ·  velt ved trykk på hjørnet av ruta %.1f N, fremste kant %.1f N, dytt i toppen %.1f N'
              % (rap['veltevinkel'], rap['velt_hjorne_N'], rap['velt_framme_N'], rap['velt_dytt_topp_N']))
        for d in rap['delar']: print('  %-3s %-26s %7.1f g %s' % (d['id'], d['namn'], d['masse_g'], '' if d['gyldig'] else 'UGYLDIG'))
        print('kollisjonar:', rap['kollisjonar'] or 'ingen')
        for r_ in rap['rorsle']: print('  helling %2d°: kollisjon %.1f mm³ %s · lågaste punkt %.0f mm' % (r_['vinkel'], r_['kollisjon_mm3'], r_['kven'], r_['laagaste_punkt']))
    return rap

def eksporter():
    from cadquery import exporters
    for d in ('step', 'stl', 'samla'): os.makedirs(os.path.join(UT, d), exist_ok=True)
    D = delar()
    a = cq.Assembly(name='k1-ruta-pa-armen')
    for (i, namn, form, mat, farge, n, _) in D:
        a.add(form, name='%s_%s' % (i, namn.replace(' ', '_').replace(':', '').replace('×', 'x')), color=cq.Color(*FARGE[farge]))
        exporters.export(form, os.path.join(UT, 'samla', i + '.stl'), tolerance=0.03, angularTolerance=0.12)
    a.export(os.path.join(UT, 'k1-ruta-pa-armen.step'))
    d = {x[0]: x[2] for x in D}
    B = _bjelke_lokal()
    def del_x(form, x0, x1): return form.intersect(L._boks(x0, x1, -40, 40, -40, 40))
    staaande = lambda f: f.rotate((0, 0, 0), (0, 1, 0), -90)
    lista, klor = klemlist()
    P = [('01_fot_med_sokkel', d['01'].rotate((0, 0, 0), (1, 0, 0), 180)), ('02_botnlok', d['02']),
         ('03_klemlist', lista.rotate((0, 0, 0), (1, 0, 0), 90)), ('04_klor', klor.rotate((0, 0, 0), (1, 0, 0), 90)),
         ('05_sal', d['05'].rotate((0, 0, 0), (0, 1, 0), 90)),
         ('07_bjelke_venstre', staaande(del_x(B['kropp'], X0 - 1, -12))), ('07_bjelke_hogre', staaande(del_x(B['kropp'], -12, X1 + 1))),
         ('08_bjelkelok_venstre', staaande(del_x(B['lokk'], X0 - 1, 12))), ('08_bjelkelok_hogre', staaande(del_x(B['lokk'], 12, X1 + 1))),
         ('13_kabelklips', klips(0.0)),
         # prøvedelar: print desse først
         ('prove_sal_hylse', d['05'].intersect(boks(-40, 40, AY - 40, AY + 45, ZP - 41, ZP - 14)).rotate((0, 0, 0), (1, 0, 0), 180)),
         ('prove_vogge', d['05'].intersect(boks(-6, 6, YB - 40, AY - KAPPE_H / 2 - 4.4, ZP - 40, ZP + 45)).rotate((0, 0, 0), (0, 1, 0), 90)),
         ('prove_klor', klor.rotate((0, 0, 0), (1, 0, 0), 90))]
    for namn, f in P:
        bb = f.val().BoundingBox()
        f = f.translate((-0.5 * (bb.xmin + bb.xmax), -0.5 * (bb.ymin + bb.ymax), -bb.zmin))
        exporters.export(f, os.path.join(UT, 'stl', namn + '.stl'), tolerance=0.02, angularTolerance=0.1)
        bb = f.val().BoundingBox(); print('  stl %-24s %5.0f x %5.0f x %5.0f mm' % (namn, bb.xlen, bb.ylen, bb.zlen))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    os.makedirs(UT, exist_ok=True)
    rap = kontroll()
    rap['stykkliste'] = [dict(id=i, namn=n, tal=t, materiale=m_, framstilling=pr) for (i, n, _, m_, _, t, pr) in delar()]
    rap['lause'] = LAUSE
    json.dump(rap, open(os.path.join(UT, 'kontroll.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    if sys.argv[1:2] != ['kontroll']:
        eksporter()
