# -*- coding: utf-8 -*-
"""
ruta_c.py  ·  Ruta på fot, revisjon C: produksjonsklar for 3D-print og butikkdelar

Forma er revisjon B (northern.py): skive, eitt røyr, eitt blad. Revisjon C endrar berre det som må til for at lampa
kan byggjast av trykte delar og delar frå hylla i ein jernvarebutikk, utan røyrbøyar, innpressmutrar eller boring i røyr:

  røyret       to rette koparrøyr Ø 12 (forkromma, Clas Ohlson) limte i eit trykt bogestykke (før: eitt bøygd stålrøyr)
  stopp        bogestykket har ein krage som går inn i enden av bjelken. Endane på kragen er stoppa 0° og 80°
  låsing       éin skrue nedanfrå ligg i eit spor i kragen og held bjelken på røyret (før: skrue gjenga i røyrveggen)
  friksjon     bremseskrue mot ein trykt sko, ikkje rett mot røyret
  gjenger      M3 formar gjenge i trykte hol Ø 2,5. Ingen innpressmutrar
  ballast      stålskiver M16 på tappar i foten (før: skoren stålplate)
  lys          COB-stripe 24 V med adapter og brytar på leidningen. Messingpunktet er eit trykt lok
  print        alle trykte delar går på 256 mm: bjelken og loket i to lengder med forskyvd skøyt

  python ruta_c.py            kontroll og eksport til ut-c/
  python ruta_c.py kontroll

Origo midt i foten på bordflata. x mot høgre, y bort frå brukaren, z opp. Alt i mm.
"""
import os, sys, math, json
import cadquery as cq
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
import lampe as L

UT = os.path.join(HER, 'ut-c')

# ------------------------------------------------------------------ innkjøpte delar: måla som styrer CAD-en
ROYR_D, ROYR_T = 12.0, 1.0        # koparrøyr, halvhardt og forkromma (Clas Ohlson 30-6571). KONTROLLMÅL: veggen er rekna frå vekta
SKRUE_FRI, SKRUE_PILOT = 3.4, 2.5  # M3: frigang, og holet M3 formar gjenge i
HOVUD_D, HOVUD_H = 5.5, 2.0       # sylinderhovud med spor, DIN 84 (Clas Ohlson 40-7042)
SENK_D = 6.6                      # forsenking til hovudet
E_L, F_L, G_L = 20.0, 10.0, 8.0   # lengder: lok og låsing, botnlok, brems. Settet har M3 × 10, 15 og 20: G er ein M3 × 10 kappa til 8
INNGREP = 8.0                     # gjengeinngrep i plast for skruane som held
LED_ROM, LED_DJUPN = 10.0, 2.8    # kanalen til LED-stripa: 8 × 2 mm COB (Clas Ohlson 36-8960)
SKIVE_D, SKIVE_HOL, SKIVE_T = 30.0, 17.0, 2.7   # skive M16 DIN 125 (Clas Ohlson 11-1203-16). KONTROLLMÅL: tjukna er rekna frå vekta
SKIVER_I_STABEL = 3
SKIVE_T_MAKS = 3.3                # tappar og klossar er laga for den tjukkaste skiva DIN 125 tillèt
PASS_LIM, PASS_GLID = 0.30, 0.40  # klaring på diameteren: der røyret blir limt, og der bjelken dreier
KNOTT_R, KNOTT_N = 75.0, 16       # antisklknottar Ø 8 under kanten av foten, over skøyten mot botnloket
UNDERLAG_R = (KNOTT_R + 4.0) * math.cos(math.pi / KNOTT_N)   # veltekanten: lina mellom to naboknottar

# ------------------------------------------------------------------ proporsjonar (som revisjon B)
RUTE_B, RUTE_D, RUTE_T, FILM_T = L.RUTE_B, L.RUTE_D, L.RUTE_T, L.FILM_T
RUTE_HJORNE = 8.0
VINKEL = 35.0
VINKEL_OMRAADE = (0.0, 80.0)
AKSE_H = 260.0
FOT_D, FOT_H = 158.0, 16.0
ROYR_HELL = 30.0
ROYR_FOT = (58.0, 22.0)
BJELKE_D = 36.0
EKS = 9.5
ENDELOK_D, ENDELOK_T = 20.0, 3.0

BOGE_R = 30.0                     # radius i senterlina på bogestykket
BOGE_D = ROYR_D + 6.0             # ytre diameter på bogestykket: 3 mm gods rundt røyret
MUFFE = 25.0                      # så langt går kvart røyr inn i bogestykket
KABEL_D = 7.0                     # kabelvegen gjennom bogen
SPALTE_E = 1.0                    # luft mellom bogestykket og enden av bjelken

R = BJELKE_D / 2
h = (RUTE_T + FILM_T + 0.05) / 2
U_KANT, U_SKRUE = L.U_KANT, L.U_SKRUE
YT = ROYR_FOT[1]
_f = math.radians(ROYR_HELL)
XC = ROYR_FOT[0] + (AKSE_H - FOT_H) * math.tan(_f)
_t = BOGE_R * math.tan(math.radians(90.0 + ROYR_HELL) / 2)
T1 = (XC - _t * math.sin(_f), AKSE_H - _t * math.cos(_f))    # bogen startar (i planet y = YT)
T2 = (XC - _t, AKSE_H)                                       # bogen sluttar, det vassrette løpet startar
XB = T2[0] - MUFFE                                           # venstre ende av bogestykket
X1 = XB - SPALTE_E                                           # høgre ende av bjelken
ENDE_V, ENDE_H = 14.0, 14.0                                  # endesonene: venstre har endeloket, høgre har kragerommet
X0 = X1 - RUTE_B - ENDE_V - ENDE_H
XR0, XR1 = X0 + ENDE_V, X1 - ENDE_H                          # ruta
BOR0 = X0 + 16.0                                             # botnen i boringa til røyret
ROYR_V = X0 + 46.0                                           # venstre ende av akselrøyret. Mellom her og botnen snur leidningen
SKRUAR_X = [XR0 + f * RUTE_B for f in (0.06, 0.28, 0.50, 0.72, 0.94)]
X_DEL_K = XR0 + 0.39 * RUTE_B                                # skøyten i bjelken: mellom skrue 2 og 3
STYREPINNAR = ((8.0, -9.0), (-2.0, 12.0))                    # (u, w) i skøytflata, Ø 2 × 6 mm i kvar halvdel, til filament 1,75
X_DEL_L = XR0 + 0.61 * RUTE_B                                # skøyten i loket: mellom skrue 3 og 4, så loket bind bjelkehalvdelane saman

LED_Y0 = 0.8                                                 # veggen LED-stripa er limt på. Loket startar her, så heile stripa ligg på bjelken
Z_SETE_E = E_L - INNGREP - h                                 # anlegget til hovudet på lokskruane

# kragen på bogestykket og rommet han går i. Vinklar i bjelken sitt snitt, målt om røyret frå u mot w. Kragen står i ro,
# og sett frå bjelken flyttar han seg mot lågare vinkel når hellinga aukar
KRAGE_INN = 10.0                                             # så langt inn i bjelken går kragen
KROM_A = 124.0                                               # rommet går frå −KROM_A til +KROM_A: bak der er godset for tynt
KRAGE_A = (-(KROM_A - 0.5) + VINKEL_OMRAADE[1], KROM_A - 0.5)    # kragen ved 0° helling
KROM_R = BOGE_D / 2 + 0.4
SPOR_R = BOGE_D / 2 - 1.4                                    # botnen i låsesporet
SPOR_B = SKRUE_FRI
PINNE_X = X1 - 5.6                                           # låseskruen: ligg tangentielt i sporet
PINNE_Y = -EKS + SPOR_R + 0.2 + 1.5
Z_SETE_P = 9.0

BREMS_X = X1 - 45.0
BREMS_V = 62.0                                               # retninga til bremseskruen, same vinkelmål som kragen. Her er godset tjukt nok til M3 × 8
SKO_R0 = ROYR_D / 2 + 0.05                                   # flata mot røyret
SKO_R1, SKO_R2 = 7.0, 8.6                                    # skuldra som held skoen i lomma, og flata skruen trykkjer på
SKO_LUFT = 0.65                                              # vengene på skoen står så høgt over skuldra i sporet: vandringa mot røyret er 0,75 mm, 0,25 trengst
RING_S = 24.0                                                # fotringen rekk så langt opp langs stammerøyret frå røyrenden
SKO_L = 10.0                                                 # lengda på skoen. Lomma er eit T-spor, dobbelt så langt: skoen går inn frå sida i den eine halvdelen

TOPP_T, VEGG, LOK_T = 3.0, 6.0, 2.0
TAK = FOT_H - TOPP_T
BOSS_R, BOSS_V, BOSS_Z = FOT_D / 2 - VEGG - 7.0, (95.0, 215.0, 335.0), 4.4
Z_HOVUD_F = 2.4                                              # anlegget til hovudet på botnskruane: 2 mm gods under, hovudet ligg forsenka
Z_STOPP = 5.8                                                # senteret i enden av stammerøyret nede i foten
def _akse_x(z): return ROYR_FOT[0] - (FOT_H - z) * math.tan(_f)
XS = _akse_x(8.0)
SOKKEL = (XS - 15.0, XS + 15.0, YT - 12.0, YT + 12.0)
BALLAST = [(-11.2, -32.8), (-36.3, -14.6), (-33.1, 16.2), (13.8, -51.1), (17.1, -20.2), (-8.0, -2.0), (-4.8, 28.8), (-29.8, 47.1),
           (42.2, -38.4), (45.4, -7.6), (20.3, 10.6)]        # stablane: tettpakka utanom sokkelen, skruetårna og koplingsrommet
KOPLING = (12.0, 40.0, 37.0, 57.0)                           # rom til to samanføyingsklemmer (Wago 221, 13 × 19 × 8 mm)
UT_X = 22.0                                                  # leidningen går ut bak, litt til høgre for midten

RHO = dict(L.RHO); RHO['petg_fast'] = 1.27e-3; RHO['kopar'] = 8.96e-3

def _syl(d, p, retning, lengd):
    return cq.Workplane('XY').newObject([cq.Solid.makeCylinder(d / 2.0, lengd, cq.Vector(*p), cq.Vector(*retning))])

def paa_plass(lokal, vinkel):
    """Frå bjelken sitt eige system (x langs aksen, u ut i ruta, w mot undersida, origo midt i bjelken) til rommet."""
    return lokal.translate((0, EKS, 0)).rotate((0, 0, 0), (1, 0, 0), 180.0 + vinkel).translate((0, YT, AKSE_H))

def _om_royret(lokal, grader):
    """Dreier ei form i bjelkesnittet om røyraksen."""
    return lokal.rotate((0, -EKS, 0), (1, -EKS, 0), grader)

def _sektor(r0, r1, a0, a1, x0, x1, steg=3.0):
    """Ringsektor om røyret i bjelkesnittet. r0 = 0 gjev ein kakebit med spissen i røyraksen."""
    n = max(2, int(math.ceil((a1 - a0) / steg)))
    vink = [math.radians(a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    ytre = [(-EKS + r1 * math.cos(a), r1 * math.sin(a)) for a in vink]
    indre = [(-EKS + r0 * math.cos(a), r0 * math.sin(a)) for a in reversed(vink)] if r0 > 0 else [(-EKS, 0.0)]
    return cq.Workplane('YZ', origin=(x0, 0, 0)).polyline(ytre + indre).close().extrude(x1 - x0)

# ------------------------------------------------------------------ røyra og bogestykket

def _sveip(dia, a, b):
    """Sveip langs senterlina i bogestykket, frå a mm nedanfor bogen til b mm til venstre for han."""
    d = (math.sin(_f), math.cos(_f))
    A = (T1[0] - a * d[0], T1[1] - a * d[1])
    O = (T2[0], AKSE_H - BOGE_R)
    am = math.atan2(T1[0] - O[0], T1[1] - O[1]) / 2
    M = (O[0] + BOGE_R * math.sin(am), O[1] + BOGE_R * math.cos(am))
    veg = cq.Workplane('XZ', origin=(0, YT, 0)).moveTo(*A).lineTo(*T1).threePointArc(M, T2).lineTo(T2[0] - b, AKSE_H)
    plan = cq.Plane(origin=(A[0], YT, A[1]), xDir=(0, 1, 0), normal=(d[0], 0, d[1]))
    return cq.Workplane(plan).circle(dia / 2).sweep(veg)

P0 = (_akse_x(Z_STOPP), Z_STOPP)
STAMME_L = math.hypot(T1[0] - P0[0], T1[1] - P0[1])
AKSEL_L = T2[0] - ROYR_V

def royr_stamme():
    d = (math.sin(_f), 0, math.cos(_f)); p = (P0[0], YT, P0[1])
    return _syl(ROYR_D, p, d, STAMME_L).cut(_syl(ROYR_D - 2 * ROYR_T, p, d, STAMME_L))

def royr_aksel():
    return L._syl_x(ROYR_D, ROYR_V, T2[0], YT, AKSE_H).cut(L._syl_x(ROYR_D - 2 * ROYR_T, ROYR_V - 1, T2[0] + 1, YT, AKSE_H))

def _krage_lokal():
    k = _sektor(ROYR_D / 2 + PASS_LIM / 2, BOGE_D / 2, KRAGE_A[0], KRAGE_A[1], X1 - KRAGE_INN, XB + 0.01)
    return k.cut(_sektor(SPOR_R, BOGE_D / 2 + 1, KRAGE_A[0] - 1, KRAGE_A[1] + 1, PINNE_X - SPOR_B / 2, PINNE_X + SPOR_B / 2))

def bogestykke():
    d = (math.sin(_f), 0, math.cos(_f))
    b = _sveip(BOGE_D, MUFFE, MUFFE).cut(_sveip(KABEL_D, MUFFE + 1, MUFFE + 1))
    A = (T1[0] - (MUFFE + 0.5) * d[0], YT, T1[1] - (MUFFE + 0.5) * d[2])
    b = b.cut(_syl(ROYR_D + PASS_LIM, A, d, MUFFE + 0.5))                               # muffa til stammerøyret
    b = b.cut(L._syl_x(ROYR_D + PASS_LIM, XB - 0.5, T2[0], YT, AKSE_H))                 # muffa til akselrøyret
    return b.union(paa_plass(_krage_lokal(), 0.0))

# ------------------------------------------------------------------ bjelken (lokalt system)

def _bremseform(sko):
    """Skoen (sko=True) eller T-sporet han ligg i, bygd rett ned frå røyret og dreidd til BREMS_V.
    Sporet er to skolengder langt. I den høgre halvdelen er det ope mot LED-kanalen: der går skoen inn frå sida, før stripa
    kjem på. Så blir han skoven til venstre, under skruen, der sporet har skulder på begge sider."""
    hs = SKO_L / 2
    if sko:
        x0, x1 = BREMS_X - hs, BREMS_X + hs
        fot_ = L._boks(x0, x1, -EKS - 4.0, -EKS + 4.0, SKO_R1 + SKO_LUFT, SKO_R2)
        tapp = L._boks(x0, x1, -EKS - 2.5, -EKS + 2.5, 0.0, SKO_R1 + SKO_LUFT + 0.01).cut(L._syl_x(2 * SKO_R0, x0 - 1, x1 + 1, -EKS, 0.0))
        for xa, r_ in ((x0, 1), (x1, -1)):                                             # innløp i begge endar: røyret lyftar skoen når bjelken blir skoven inn
            tapp = tapp.cut(cq.Workplane('XY').newObject([cq.Solid.makeCone(SKO_R0 + 1.2, SKO_R0, 1.2, cq.Vector(xa, -EKS, 0), cq.Vector(r_, 0, 0))]))
        form = fot_.union(tapp).cut(L._syl_z(SKRUE_FRI, SKO_R2 - 0.5, SKO_R2 + 1, BREMS_X, -EKS))   # styrehol til skruespissen
    else:
        x0, x1, x2 = BREMS_X - hs - 0.2, BREMS_X + hs + 0.2, BREMS_X + 3 * hs + 0.4
        # i båsen (høgre halvdel) er taket 0,6 mm lågare: der stikk skoen inn i boringa, så røyret skuvar han til venstre og under
        # skruen når bjelken kjem på, og han kan ikkje gli attende etterpå
        fot_ = L._boks(x0, x1, -EKS - 4.2, -EKS + 4.2, SKO_R1 - 0.1, SKO_R2 + 0.3).union(L._boks(x1, x2, -EKS - 4.2, -EKS + 4.2, SKO_R1 - 0.1, SKO_R2 - 0.6))
        vindauge = L._boks(x0, x2, -EKS - 2.7, -EKS + 2.7, 0.0, SKO_R1)
        inn = L._boks(x1, x2, -EKS + 2.6, -EKS + 12.0, SKO_R0 - 1.4, SKO_R2 - 0.6)
        form = fot_.union(vindauge).union(inn)
    return _om_royret(form, BREMS_V - 90.0)

def _bremseskrue_hol():
    """Bremseskruen formar gjenge i plasten. Forsenkinga er djup nok til at hovudet aldri botnar før skoen ligg mot røyret."""
    spiss = SKO_R2 - 0.5 - 0.3                                                         # i styreholet, med 0,3 mm til slitasje
    golv = spiss + G_L - 0.8
    hol = L._syl_z(SKRUE_PILOT, SKO_R2, golv + 0.1, BREMS_X, -EKS).union(L._syl_z(SENK_D, golv, R + 6, BREMS_X, -EKS))
    return _om_royret(hol, BREMS_V - 90.0), spiss

def _lokform(c):
    """Rommet loket fyller: framfor veggen stripa sit på, frå klemflata og ned."""
    return L._boks(X0 + 3.0 + c, XR1 + 1.2 - c, LED_Y0 + c, R + 2, h, R + 2)

def _skrue(l, z_sete, x, y):
    return L._syl_z(HOVUD_D, z_sete, z_sete + HOVUD_H, x, y).union(L._syl_z(3.0, z_sete - l, z_sete, x, y))

def _bjelke_lokal():
    syl = L._syl_x(BJELKE_D, X0, X1)
    x0, x1 = XR0 - 0.5, XR1 + 0.5
    hol = (L._boks(x0, x1, U_KANT - 0.3, R + 2, -h, h)                                           # spalta til plata og arket
           .union(L._boks(x0, x1, LED_Y0, U_KANT - 0.3, -LED_ROM / 2, LED_ROM / 2)))             # kanalen til LED-stripa
    hol = hol.union(L._syl_x(ROYR_D + PASS_GLID, BOR0, X1 + 1, -EKS, 0.0))                       # boringa bjelken dreier på
    hol = hol.union(L._boks(BOR0 + 2.0, ROYR_V - 2.0, -EKS, LED_Y0 + 0.1, -2.5, 2.5))            # leidningen frå røyrenden til stripa
    hol = hol.union(L._syl_x(ENDELOK_D + 0.3, X0 - 0.1, X0 + ENDELOK_T, 0, 0))                   # lomma til endeloket
    hol = hol.union(_sektor(0.0, KROM_R, -KROM_A, KROM_A, X1 - KRAGE_INN - 0.6, X1 + 1))          # rommet kragen går i. Endane er stoppa
    # låseskruen: frigang nedanfrå og gjennom sporet, gjenge i godset over
    hol = hol.union(L._syl_z(SENK_D, Z_SETE_P, R + 1, PINNE_X, PINNE_Y)).union(L._syl_z(SKRUE_FRI, -5.3, Z_SETE_P + 0.1, PINNE_X, PINNE_Y))
    hol = hol.union(L._syl_z(SKRUE_PILOT, Z_SETE_P - E_L - 0.8, -5.2, PINNE_X, PINNE_Y))
    bhol, spiss = _bremseskrue_hol()
    hol = hol.union(_bremseform(False)).union(bhol)
    for (u, w) in STYREPINNAR:                                                                   # filamentbitar som held halvdelane rett mot kvarandre under liming
        hol = hol.union(L._syl_x(2.0, X_DEL_K - 6.0, X_DEL_K + 6.0, u, w))
    kropp = syl.cut(_lokform(0.0)).cut(hol)
    lokk = syl.intersect(_lokform(0.15)).cut(hol)
    # loket klemmer på plata. Utanfor plata er kroppen senka 0,8 mm, så loket klemmer plater ned til 2,25 mm og har flat underside til printen
    for xa, xb in ((X0 + 3.0, x0), (x1, XR1 + 1.2)):
        kropp = kropp.cut(L._boks(xa, xb, LED_Y0, R + 2, h - 0.8, h + 0.01))
    zt = math.sqrt(R * R - U_SKRUE ** 2)
    skruar = None
    for x in SKRUAR_X:
        kropp = kropp.cut(L._syl_z(SKRUE_PILOT, -h - INNGREP - 1.6, -h + 0.1, x, U_SKRUE))        # M3 formar gjenge i overkjeven
        lokk = lokk.cut(L._syl_z(SKRUE_FRI, h - 0.5, R + 1, x, U_SKRUE)).cut(L._syl_z(SENK_D, Z_SETE_E, R + 1, x, U_SKRUE))
        s = _skrue(E_L, Z_SETE_E, x, U_SKRUE)
        skruar = s if skruar is None else skruar.union(s)
    plate = L._boks(XR0, XR1, U_KANT, U_KANT + RUTE_D, h - RUTE_T, h)
    form = (cq.Workplane('XY').center((XR0 + XR1) / 2, U_KANT + RUTE_D / 2 - 20.0).rect(RUTE_B, RUTE_D + 40.0).extrude(10).translate((0, 0, -5))
            .edges('|Z').fillet(RUTE_HJORNE))
    kile = (cq.Workplane('YZ', origin=(XR0 - 1, 0, 0))
            .polyline([(U_KANT + RUTE_D - RUTE_T, h - RUTE_T - 0.01), (U_KANT + RUTE_D + 0.01, h - RUTE_T - 0.01), (U_KANT + RUTE_D + 0.01, h + 0.01)])
            .close().extrude(RUTE_B + 2))
    plate = plate.intersect(form).cut(kile)
    film = L._boks(XR0, XR1, U_KANT, U_KANT + RUTE_D - 6.0, h - RUTE_T - FILM_T, h - RUTE_T).intersect(form.translate((0, -6.0, 0)))
    for x in SKRUAR_X:
        plate = plate.cut(L._syl_z(4.0, -5, 5, x, U_SKRUE)); film = film.cut(L._syl_z(4.0, -5, 5, x, U_SKRUE))
    led = L._boks(XR0 + 15, XR1 - 15, LED_Y0, LED_Y0 + 1.6, -4.0, 4.0)            # 27 cm midt i kanalen: loddepunktet ligg over slissa
    endelok = L._syl_x(ENDELOK_D, X0 - 1.0, X0 + ENDELOK_T - 0.2, 0, 0).faces('<X').edges().chamfer(0.6)
    laas = _skrue(E_L, Z_SETE_P, PINNE_X, PINNE_Y)
    brems = _om_royret(_skrue(G_L, spiss + G_L, BREMS_X, -EKS), BREMS_V - 90.0)
    return dict(kropp=kropp, lokk=lokk, plate=plate, film=film, led=led, skruar=skruar, endelok=endelok, laas=laas, brems=brems,
                sko=_bremseform(True))

def _del_x(form, x0, x1): return form.intersect(L._boks(x0, x1, -40, 40, -40, 40))

# ------------------------------------------------------------------ foten

def _boss_xy(v): return BOSS_R * math.cos(math.radians(v)), BOSS_R * math.sin(math.radians(v))

def fot():
    f = L._syl_z(FOT_D, 0, FOT_H).faces('>Z').edges().fillet(3.0)
    f = f.cut(L._syl_z(FOT_D - 2 * VEGG, -0.1, TAK))
    inni = L._syl_z(FOT_D - 2 * VEGG + 1.0, 0, TAK + 0.1)
    for v in BOSS_V:
        x, y = _boss_xy(v)
        f = f.union(L._syl_z(9.0, BOSS_Z, TAK + 0.1, x, y).union(
            L._boks(-4.5, 4.5, 0, FOT_D / 2 - VEGG - BOSS_R + 1.0, BOSS_Z, TAK + 0.1).translate((0, BOSS_R, 0)).rotate((0, 0, 0), (0, 0, 1), v - 90.0)))
        f = f.cut(L._syl_z(SKRUE_PILOT, BOSS_Z - 0.1, Z_HOVUD_F + F_L + 0.8, x, y))
    # tappar til skivene. Dei stivar òg av toppflata
    for (x, y) in BALLAST:
        f = f.union(L._syl_z(SKIVE_HOL - 0.7, TAK - SKIVER_I_STABEL * SKIVE_T_MAKS - 0.5, TAK + 0.1, x, y))
    # sokkelen til røyret står på botnplanet og er bunden til ribbene
    x0, x1, y0, y1 = SOKKEL
    f = f.union(L._boks(x0, x1, y0, y1, 0.0, TAK + 0.1))
    f = f.union(L._boks(x1 - 2.0, x1, YT - 40.0, y0 + 0.1, LOK_T + 0.6, TAK + 0.1).intersect(inni))          # ribbe framover frå sokkelen
    f = f.union(L._boks(KOPLING[0] - 2.0, KOPLING[0], KOPLING[2], KOPLING[3] + 6.0, LOK_T + 0.6, TAK + 0.1).intersect(inni))   # vegg mot koplingsrommet
    d = cq.Vector(math.sin(_f), 0, math.cos(_f)); dn = (-d.x, 0, -d.z)
    p = (P0[0], YT, P0[1])
    f = f.cut(_syl(ROYR_D + PASS_LIM, p, (d.x, 0, d.z), 30.0))                           # hylsa: røyret står mot ein kant i botnen
    f = f.cut(_syl(6.0, (p[0] + 0.1 * d.x, YT, p[2] + 0.1 * d.z), dn, 4.1))              # kammeret under røyrenden, til leidningen
    kx = P0[0] - 2.0 * d.x
    f = f.cut(L._boks(kx - 3.0, kx + 3.0, YT, y1 + 1.0, 1.2, 6.5))                       # leidningen ut av sokkelen, bakover
    f = f.cut(L._boks(UT_X - 3.0, UT_X + 3.0, FOT_D / 2 - VEGG - 6, FOT_D / 2 + 1, -0.1, 4.5))   # og ut gjennom veggen
    return f

def botnlok():
    l = L._syl_z(FOT_D - 2 * VEGG - 0.6, 0, LOK_T)
    for v in BOSS_V:
        x, y = _boss_xy(v)
        l = l.union(L._syl_z(10.0, 0, BOSS_Z - 0.15, x, y))
        l = l.cut(L._syl_z(SKRUE_FRI, -1, BOSS_Z, x, y)).cut(L._syl_z(SENK_D, -0.1, Z_HOVUD_F, x, y))
    for (x, y) in BALLAST:                                                             # klossar under stablane. Skivene er limte til tappane
        l = l.union(L._syl_z(SKIVE_D - 4.0, 0, TAK - SKIVER_I_STABEL * SKIVE_T_MAKS - 0.3, x, y).cut(L._syl_z(SKIVE_HOL + 0.6, LOK_T, FOT_H, x, y)))
    x0, x1, y0, y1 = SOKKEL
    l = l.cut(L._boks(x0 - 0.4, FOT_D / 2, y0 - 0.4, y1 + 0.4, -0.1, FOT_H))
    return l.cut(L._boks(UT_X - 3.0, UT_X + 3.0, FOT_D / 2 - VEGG - 10, FOT_D / 2, -0.1, LOK_T + 0.1))

def fotring():
    """Ring rundt stammerøyret oppå foten, limt til begge. Han aukar innfestinga på den lasta sida frå 8 til 24 mm og set hellinga på røyret."""
    d = (math.sin(_f), 0, math.cos(_f)); p = (P0[0], YT, P0[1])
    return _syl(BOGE_D, p, d, RING_S).cut(_syl(ROYR_D + PASS_LIM, p, d, RING_S + 1)).intersect(L._boks(-200, 200, -200, 200, FOT_H + 0.05, 400))

def ballast():
    b = None
    for (x, y) in BALLAST:
        s = L._syl_z(SKIVE_D, TAK - SKIVER_I_STABEL * SKIVE_T, TAK, x, y).cut(L._syl_z(SKIVE_HOL, 0, FOT_H, x, y))
        b = s if b is None else b.union(s)
    return b

def botnskruar():
    s = None
    for v in BOSS_V:
        x, y = _boss_xy(v)
        k = L._syl_z(HOVUD_D, Z_HOVUD_F - HOVUD_H, Z_HOVUD_F, x, y).union(L._syl_z(3.0, Z_HOVUD_F, Z_HOVUD_F + F_L, x, y))
        s = k if s is None else s.union(k)
    return s

def leidning():
    """Stoffkledd leidning ut bak foten (berre til biletet)."""
    veg = cq.Workplane('XY', origin=(0, 0, 2.6)).moveTo(UT_X, FOT_D / 2 - 2).spline([(UT_X + 8, FOT_D / 2 + 60), (UT_X + 50, FOT_D / 2 + 130), (UT_X + 30, FOT_D / 2 + 230)], includeCurrent=True)
    return cq.Workplane('XZ', origin=(UT_X, FOT_D / 2 - 2, 2.6)).circle(2.0).sweep(veg)

# ------------------------------------------------------------------ samanstillinga

FASTE = ('01', '02', '03', '04', '09', '12', '14', 'F')
ROERLEGE = ('05v', '05h', '06v', '06h', '07', '08', '10', '11', '13', 'E', 'G')

def delar(vinkel=VINKEL):
    B = _bjelke_lokal(); P = lambda s: paa_plass(s, vinkel)
    D = [
        ('01', 'fot', fot(), 'petg', 'kropp', 1, 'TRYKT. PETG, toppflata ned, utan støtte, fem vegger'),
        ('02', 'botnlok', botnlok(), 'petg', 'svart', 1, 'TRYKT. %d antisklknottar limte under kanten av foten' % KNOTT_N),
        ('03', 'ballast', ballast(), 'staal', 'staal', len(BALLAST) * SKIVER_I_STABEL, 'KJØPT. Skive M16 DIN 125, Ø %g × %g. %d stablar à %d, limte til tappane' % (SKIVE_D, SKIVE_T, len(BALLAST), SKIVER_I_STABEL)),
        ('04', 'stammerøyr', royr_stamme(), 'kopar', 'kropp', 1, 'KJØPT. Koparrøyr Ø %g × %g, kappa i %.0f mm' % (ROYR_D, ROYR_T, STAMME_L)),
        ('05v', 'bjelke venstre', P(_del_x(B['kropp'], X0 - 1, X_DEL_K)), 'petg', 'kropp', 1, 'TRYKT. PETG, ståande med enden ned og skøyten opp. Støtte berre i endeloklomma'),
        ('05h', 'bjelke høgre', P(_del_x(B['kropp'], X_DEL_K, X1 + 1)), 'petg', 'kropp', 1, 'TRYKT. PETG, ståande med enden ned og skøyten opp. Støtte berre i kragerommet'),
        ('06v', 'lok venstre', P(_del_x(B['lokk'], X0 - 1, X_DEL_L)), 'petg', 'kropp', 1, 'TRYKT. PETG, klemflata ned, støtte frå plata under leppa'),
        ('06h', 'lok høgre', P(_del_x(B['lokk'], X_DEL_L, X1 + 1)), 'petg', 'kropp', 1, 'TRYKT. PETG, klemflata ned, støtte frå plata under leppa'),
        ('07', 'lysleiar', P(B['plate']), 'pmma', 'rute', 1, 'FRÅ SKJERMEN. PMMA %g mm, fem hol Ø 4' % RUTE_T),
        ('08', 'prismeark', P(B['film']), 'film', 'film', 1, 'FRÅ SKJERMEN. Prisma opp, rillene på tvers av bjelken'),
        ('09', 'akselrøyr', royr_aksel(), 'kopar', 'kropp', 1, 'KJØPT. Same røyr, kappa i %.0f mm' % AKSEL_L),
        ('10', 'LED-stripe', P(B['led']), 'gummi', 'led', 1, 'KJØPT. COB 24 V, 3000 K, 8 × 2 mm, klipt i 27 cm (9 × 3 cm). Adapter og brytar følgjer med'),
        ('11', 'endelok', P(B['endelok']), 'petg_fast', 'messing', 1, 'TRYKT. Messingpunktet: trykt i messingfarge eller sprøyta'),
        ('12', 'bogestykke', bogestykke(), 'petg_fast', 'kropp', 1, 'TRYKT. PETG, 100 % fyll, liggjande, støtte berre frå plata, 5 mm brem'),
        ('13', 'bremsesko', P(B['sko']), 'petg_fast', 'svart', 1, 'TRYKT. PETG, 100 % fyll'),
        ('14', 'fotring', fotring(), 'petg_fast', 'kropp', 1, 'TRYKT. PETG, 100 % fyll, ståande på den rette enden'),
        ('E', 'skrue M3 × %g' % E_L, P(B['skruar'].union(B['laas'])), 'staal', 'staal', len(SKRUAR_X) + 1, 'KJØPT. Fem i loket, éin som låser bjelken'),
        ('F', 'skrue M3 × %g' % F_L, botnskruar(), 'staal', 'staal', 3, 'KJØPT. Botnloket'),
        ('G', 'skrue M3 × %g' % G_L, P(B['brems']), 'staal', 'staal', 1, 'KJØPT. Bremseskruen: M3 × 10 kappa til %g mm, enden filt plan' % G_L),
    ]
    return D

def vol(s): return s.val().Volume()

def _snitt(a, b):
    try: return vol(a.intersect(b))
    except Exception: return 0.0

F_PROV = 8.0

def _massar(D):
    return [(i, vol(s) * RHO[mat], s.val().Center()) for (i, _n, s, mat, *_r) in D]

def _velt(W, T, P, r):
    """Minste kraft rett ned i P som veltar lampa, over alle velteretningar. W er tyngda, T tyngdepunktet og r radien lampa står på."""
    return min((W * (r - T[0] * math.cos(a) - T[1] * math.sin(a)) / (P[0] * math.cos(a) + P[1] * math.sin(a) - r)
                for a in (math.radians(k / 4) for k in range(1440)) if P[0] * math.cos(a) + P[1] * math.sin(a) > r + 1), default=None)

def styrke(M_blad, M_hald, M_fot):
    """Handrekning på dei fire stadene som ber. Lasta er det lampa toler før ho veltar, så meir kjem aldri på."""
    g = 9.81e-3
    x_blad = 0.5 * (X0 + X1)
    arm = T2[0] - MUFFE / 2 - x_blad                                                   # frå tyngdepunktet i bladet til bogen
    M_eigen = M_blad * g * arm                                                         # N·mm, eigenvekta
    F_velt = F_PROV                                                                    # N på venstre hjørne av ruta: om lag det doble av det som veltar lampa
    M_velt = M_eigen + F_velt * (T2[0] - XR0)
    Z_boge = math.pi * (BOGE_D ** 4 - KABEL_D ** 4) / (32 * BOGE_D)
    I_royr = math.pi * (ROYR_D ** 4 - (ROYR_D - 2 * ROYR_T) ** 4) / 64
    Z_royr = I_royr / (ROYR_D / 2)
    F_muffe = M_velt / (MUFFE * 2 / 3)
    r_stopp = 0.5 * (ROYR_D / 2 + BOGE_D / 2)
    A_stopp = (BOGE_D / 2 - ROYR_D / 2 - PASS_LIM / 2) * (KRAGE_INN - 0.6)
    M_stopp = 1000.0                                                                   # N·mm: meir enn dette og lampa lettar eller glir
    M_brems = 2.0 * M_hald                                                             # M_hald: momentet bladet gjev om røyret når ruta ligg flatt
    N_brems = M_brems / (2 * 0.25 * ROYR_D / 2)
    L_gjenge = G_L - 1.9                                                               # frå taket i T-sporet til golvet i forsenkinga
    F_gjenge = math.pi * 2.7 * L_gjenge * 0.5 * 25.0
    return dict(
        last=dict(blad_g=round(M_blad), moment_eigenvekt_Nmm=round(M_eigen), moment_ved_velt_Nmm=round(M_velt)),
        bogestykke=dict(spenning_eigenvekt_MPa=round(M_eigen / Z_boge, 1), spenning_ved_velt_MPa=round(M_velt / Z_boge, 1), grense_MPa=40,
                        tryggleik_ved_velt=round(40 / (M_velt / Z_boge), 1)),
        royr=dict(spenning_ved_velt_MPa=round(M_velt / Z_royr, 1), grense_MPa=150, tryggleik_ved_velt=round(150 / (M_velt / Z_royr), 1),
                  nedboying_eigenvekt_mm=round(M_eigen * (STAMME_L ** 2) / (2 * 120000 * I_royr), 2)),
        muffe=dict(kraft_N=round(F_muffe), flatetrykk_MPa=round(F_muffe / (ROYR_D * MUFFE / 3), 1), grense_MPa=40),
        stopp=dict(moment_Nmm=M_stopp, kraft_N=round(M_stopp / r_stopp), flate_mm2=round(A_stopp, 1),
                   flatetrykk_MPa=round(M_stopp / r_stopp / A_stopp, 1), grense_MPa=40),
        brems=dict(moment_fraa_ruta_Nmm=round(M_hald), bremsemoment_Nmm=round(M_brems), skruekraft_N=round(N_brems),
                   gjenge_mm=round(L_gjenge, 1), gjenga_toler_N=round(F_gjenge), tryggleik=round(F_gjenge / N_brems, 1),
                   vandring_sko_mm=round(SKO_LUFT + 0.1, 2), vandring_trengst_mm=round(0.05 + PASS_GLID / 2, 2)),
        fot=dict(moment_Nmm=round(M_fot), innfesting_mm=RING_S, kanttrykk_MPa=round(6 * M_fot / (ROYR_D * RING_S ** 2), 1), grense_MPa=40,
                 utan_ring_MPa=round(6 * M_fot / (ROYR_D * 8.3 ** 2), 1)))

def kontroll(vis=True):
    D = delar(); d = {x[0]: x for x in D}
    rap = dict(delar=[], kollisjonar=[], rorsle=[])
    M = mx = my = mz = 0.0; M_blad = 0.0
    for (i, namn, s, mat, *_r) in D:
        v = vol(s); ma = v * RHO[mat]; c = s.val().Center()
        rap['delar'].append(dict(id=i, namn=namn, masse_g=round(ma, 1), gyldig=bool(s.val().isValid())))
        M += ma; mx += ma * c.x; my += ma * c.y; mz += ma * c.z
        if i in ROERLEGE: M_blad += ma
    M += 30.0                                                                          # leidning, klemmer, lim og matte
    T = (mx / M, my / M, mz / M); r = UNDERLAG_R; e = math.hypot(T[0], T[1]); g = 9.81e-3
    # velt: minste kraft over alle velteretningar, ved tre hellingar. Hjørnet og fremste kant flyttar seg med hellinga
    velt = {}; D0 = None
    for vk in (0.0, VINKEL, VINKEL_OMRAADE[1]):
        Dv = D if vk == VINKEL else delar(vk)
        if vk == 0.0: D0 = Dv
        ms = _massar(Dv); Mv = sum(m for _i, m, _c in ms) + 30.0
        Tv = (sum(m * c.x for _i, m, c in ms) / Mv, sum(m * c.y for _i, m, c in ms) / Mv, sum(m * c.z for _i, m, c in ms) / Mv)
        yf = YT - math.cos(math.radians(vk)) * (U_KANT + RUTE_D + EKS); ev = math.hypot(Tv[0], Tv[1])
        rund = lambda x: None if x is None else round(x, 1)
        velt['%d' % vk] = dict(hjorne_N=rund(_velt(Mv * g, Tv, (XR0, yf), r)), framkant_N=rund(_velt(Mv * g, Tv, (0.5 * (XR0 + XR1), yf), r)),
                               dytt_topp_N=round(Mv * g * (r - ev) / AKSE_H, 1), veltevinkel=round(math.degrees(math.atan((r - ev) / Tv[2])), 1))
    minst = lambda k: min(x[k] for x in velt.values() if x[k] is not None)
    rap.update(masse_g=round(M), tyngdepunkt=[round(x, 1) for x in T], fotavtrykk_cm2=round(math.pi * (FOT_D / 2) ** 2 / 100, 1),
               veltevinkel=minst('veltevinkel'), velt_venstre_N=minst('hjorne_N'), velt_framme_N=minst('framkant_N'),
               velt_dytt_topp_N=minst('dytt_topp_N'), velt=velt, delar_i_alt=sum(x[5] for x in D), underlag_r=r)
    # moment ved 0°: bladet om akselrøyret (det bremsa må halde), og alt over foten om innfestinga av stamma, med prøvelasta på hjørnet
    ms0 = _massar(D0); xs = P0[0] + (FOT_H - P0[1]) * math.tan(_f)
    M_hald = g * abs(sum(m * (c.y - YT) for i, m, c in ms0 if i in ROERLEGE))
    over = [(m, c) for i, m, c in ms0 if i not in ('01', '02', '03', '14', 'F')]
    M_fot = math.hypot(g * sum(m * (c.x - xs) for m, c in over) + F_PROV * (XR0 - xs), g * sum(m * (c.y - YT) for m, c in over) + F_PROV * (-(U_KANT + RUTE_D + EKS)))
    sonde = L._syl_y(4.0, FOT_D / 2 - VEGG - 5.0, FOT_D / 2 + 1.0, UT_X, 2.3)                # leidningen Ø 4 frå koplingsrommet og ut gjennom veggen
    rap['leidning_ut_fri'] = bool(_snitt(sonde, d['01'][2]) < 0.05 and _snitt(sonde, d['02'][2]) < 0.05)
    skruar = {'E', 'F', 'G'}                                                           # skruar står i hol dei sjølve formar gjenge i
    for a in range(len(D)):
        for b_ in range(a + 1, len(D)):
            if D[a][0] in skruar or D[b_][0] in skruar: continue
            v = _snitt(D[a][2], D[b_][2])
            if v > 0.5: rap['kollisjonar'].append((D[a][1], D[b_][1], round(v, 1)))
    faste = [d[i] for i in ('01', '04', '09', '12', '14')]
    def verst(vk, flytt=0.0, kven=('05v', '05h', '06v', '06h', '07', '08', 'E')):
        Dv = {x[0]: x for x in delar(float(vk))}; ut = (0.0, '')
        for i in kven:
            form = Dv[i][2].translate((flytt, 0, 0)) if flytt else Dv[i][2]
            for b_ in faste:
                v = _snitt(form, b_[2])
                if v > ut[0]: ut = (v, Dv[i][1] + ' mot ' + b_[1])
        return ut, Dv
    for vk in range(int(VINKEL_OMRAADE[0]), int(VINKEL_OMRAADE[1]) + 1, 10):
        (v, kven), Dv = verst(vk)
        rap['rorsle'].append(dict(vinkel=vk, kollisjon_mm3=round(v, 1), kven=kven,
                                  laagaste_punkt=round(min(Dv[i][2].val().BoundingBox().zmin for i in ('05v', '05h', '06v', '06h', '07', '08')), 1)))
    # stoppa skal ta, og låseskruen skal halde: prøv litt forbi kvar ende og dra bjelken 3 mm av røyret
    (v0, k0), _ = verst(VINKEL_OMRAADE[0] - 3.0, kven=('05h',)); (v1, k1), _ = verst(VINKEL_OMRAADE[1] + 3.0, kven=('05h',))
    (v2, k2), _ = verst(40.0, flytt=-3.0, kven=('E',))
    rap['stopp'] = dict(nedre_tek=bool(v0 > 1.0), ovre_tek=bool(v1 > 1.0), laaseskruen_held=bool(v2 > 0.2),
                        snitt_mm3=[round(v0, 1), round(v1, 1), round(v2, 1)], mot=[k0, k1, k2])
    rap['styrke'] = styrke(M_blad, M_hald, M_fot)
    rap['kapp'] = dict(stammeroyr_mm=round(STAMME_L, 1), akselroyr_mm=round(AKSEL_L, 1), royr_i_alt_mm=round(STAMME_L + AKSEL_L, 1),
                       skiver=len(BALLAST) * SKIVER_I_STABEL)
    if vis:
        print('masse %d g (krav 1200)  ·  fotavtrykk %.1f cm² (krav 200)  ·  tyngdepunkt x %.1f y %.1f z %.1f  ·  %d delar' % (rap['masse_g'], rap['fotavtrykk_cm2'], *rap['tyngdepunkt'], rap['delar_i_alt']))
        print('veltevinkel %.1f°  ·  velt ved trykk på venstre hjørne %.1f N, fremste kant %.1f N, dytt i toppen %.1f N (minst over 0°, 35° og 80°)' % (rap['veltevinkel'], rap['velt_venstre_N'], rap['velt_framme_N'], rap['velt_dytt_topp_N']))
        for k, v in rap['velt'].items(): print('  helling %2s°: %s' % (k, v))
        print('leidningen fri ut av foten:', rap['leidning_ut_fri'])
        for x in rap['delar']: print('  %-3s %-18s %7.1f g %s' % (x['id'], x['namn'], x['masse_g'], '' if x['gyldig'] else 'UGYLDIG'))
        print('kollisjonar:', rap['kollisjonar'] or 'ingen')
        for r_ in rap['rorsle']: print('  helling %2d°: kollisjon %.1f mm³ %s · lågaste punkt %.0f mm' % (r_['vinkel'], r_['kollisjon_mm3'], r_['kven'], r_['laagaste_punkt']))
        print('stopp:', rap['stopp'])
        print('kapp:', rap['kapp'])
        for k, v in rap['styrke'].items(): print('  %-11s %s' % (k, v))
    return rap

FARGE = dict(kropp=(0.62, 0.59, 0.55), svart=(0.08, 0.08, 0.08), staal=(0.45, 0.46, 0.48), rute=(0.92, 0.96, 1.0), film=(1.0, 0.93, 0.80),
             led=(1.0, 0.85, 0.5), messing=(0.80, 0.66, 0.36))

def _namn(s): return s.replace(' ', '_').replace('×', 'x').replace('ø', 'o').replace('å', 'a').replace('æ', 'ae')

def printdelar():
    """Dei trykte delane i printstilling: (namn, form). Bjelkehalvdelane står på enden med skøyten opp, loka ligg på klemflata."""
    B = _bjelke_lokal()
    ned_x = lambda f: f.rotate((0, 0, 0), (0, 1, 0), 90)                # x-aksen opp, venstre ende øvst
    opp_x = lambda f: f.rotate((0, 0, 0), (0, 1, 0), -90)               # x-aksen opp, høgre ende øvst
    P = [('01_fot', fot().rotate((0, 0, 0), (1, 0, 0), 180)), ('02_botnlok', botnlok()),
         ('05_bjelke_venstre', opp_x(_del_x(B['kropp'], X0 - 1, X_DEL_K))), ('05_bjelke_hogre', ned_x(_del_x(B['kropp'], X_DEL_K, X1 + 1))),
         ('06_lok_venstre', _del_x(B['lokk'], X0 - 1, X_DEL_L)), ('06_lok_hogre', _del_x(B['lokk'], X_DEL_L, X1 + 1)),
         ('11_endelok', B['endelok'].rotate((0, 0, 0), (0, 1, 0), 90)),
         ('12_bogestykke', bogestykke().rotate((0, 0, 0), (1, 0, 0), 90)),
         ('13_bremsesko', _om_royret(B['sko'], 90.0 - BREMS_V).rotate((0, 0, 0), (1, 0, 0), 180)),
         ('prove_bjelkesnitt', opp_x(_del_x(B['kropp'], SKRUAR_X[3] - 9, SKRUAR_X[3] + 9))),
         ('prove_loksnitt', _del_x(B['lokk'], SKRUAR_X[3] - 9, SKRUAR_X[3] + 9)),
         ('14_fotring', fotring().rotate((0, 0, 0), (0, 1, 0), -ROYR_HELL).rotate((0, 0, 0), (1, 0, 0), 180)),
         ('prove_krageende', ned_x(_del_x(B['kropp'], X1 - 16, X1 + 1))),
         ('prove_krage', bogestykke().intersect(L._boks(X1 - 10, XB + 12, -400, 400, -400, 400)).rotate((0, 0, 0), (1, 0, 0), 90)),
         ('prove_brems', opp_x(_del_x(B['kropp'], BREMS_X - 9, BREMS_X + 19))),
         ('prove_muffe', _prove_muffe())]
    ut = []
    for namn, f in P:
        bb = f.val().BoundingBox()
        ut.append((namn, f.translate((-0.5 * (bb.xmin + bb.xmax), -0.5 * (bb.ymin + bb.ymax), -bb.zmin))))
    return ut

def _prove_muffe():
    """Tre hol til å finne rett passing før dei store delane blir trykte: lim (Ø +0,30), glid (Ø +0,40) og M3-gjenge (Ø 2,5)."""
    p = L._boks(0, 46, 0, 20, 0, 12)
    p = p.cut(L._syl_z(ROYR_D + PASS_LIM, -1, 13, 11, 10)).cut(L._syl_z(ROYR_D + PASS_GLID, -1, 13, 29, 10))
    return p.cut(L._syl_z(SKRUE_PILOT, -1, 13, 41, 5)).cut(L._syl_z(SKRUE_FRI, -1, 13, 41, 15))

def eksporter():
    from cadquery import exporters
    for m in ('step', 'stl', 'samla'): os.makedirs(os.path.join(UT, m), exist_ok=True)
    D = delar()
    a = cq.Assembly(name='ruta-pa-fot-rev-c')
    for (i, namn, form, mat, farge, n, _) in D:
        a.add(form, name='%s_%s' % (i, _namn(namn)), color=cq.Color(*FARGE[farge]))
        exporters.export(form, os.path.join(UT, 'samla', i + '.stl'), tolerance=0.03, angularTolerance=0.1)
        exporters.export(form, os.path.join(UT, 'step', '%s_%s.step' % (i, _namn(namn))))
    exporters.export(leidning(), os.path.join(UT, 'samla', 'leidning.stl'), tolerance=0.05, angularTolerance=0.15)
    a.export(os.path.join(UT, 'ruta-pa-fot-rev-c.step'))
    maal = []
    for namn, f in printdelar():
        exporters.export(f, os.path.join(UT, 'stl', namn + '.stl'), tolerance=0.02, angularTolerance=0.1)
        bb = f.val().BoundingBox(); maal.append(dict(fil=namn + '.stl', x=round(bb.xlen, 1), y=round(bb.ylen, 1), z=round(bb.zlen, 1)))
        print('  stl %-22s %5.0f x %5.0f x %5.0f mm' % (namn, bb.xlen, bb.ylen, bb.zlen))
    json.dump(dict(X0=X0, X1=X1, XR0=XR0, XR1=XR1, XB=XB, YT=YT, AKSE_H=AKSE_H, EKS=EKS, VINKEL=VINKEL, R=R, U_KANT=U_KANT, U_SKRUE=U_SKRUE,
                   RUTE_D=RUTE_D, SKRUAR_X=SKRUAR_X, X_DEL_K=X_DEL_K, X_DEL_L=X_DEL_L, PINNE=[PINNE_X, PINNE_Y], BREMS_X=BREMS_X, BREMS_V=BREMS_V,
                   BOSS=[_boss_xy(v) for v in BOSS_V], BALLAST=BALLAST, SOKKEL=SOKKEL, T1=T1, T2=T2, P0=P0, HELL=ROYR_HELL,
                   FASTE=FASTE, ROERLEGE=ROERLEGE),
              open(os.path.join(UT, 'geometri.json'), 'w', encoding='utf-8'), indent=1)
    return maal

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    os.makedirs(UT, exist_ok=True)
    rap = kontroll()
    rap['stykkliste'] = [dict(id=i, namn=n, tal=t, materiale=m_, framstilling=pr) for (i, n, _, m_, _, t, pr) in delar()]
    if sys.argv[1:2] != ['kontroll']:
        rap['print'] = eksporter()
        rap['print_passar_256'] = all(max(p['x'], p['y'], p['z']) <= 250.0 for p in rap['print'])
        print('alle trykte delar innanfor 250 mm:', rap['print_passar_256'])
    json.dump(rap, open(os.path.join(UT, 'kontroll.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
