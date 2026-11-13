# -*- coding: utf-8 -*-
"""
northern.py  ·  Ruta på fot, revisjon B: forma tilpassa formspråket til Northern

Dei seks trekka frå research/01-northern.md (H1 til H6) er brukte som sjekkliste:
  H1  to–tre primærformer   skive (fot), eitt røyr, eitt blad (bjelke og rute)
  H2  tynn linje ber volumet  eitt røyr Ø 12 i éi rørsle: skrått opp frå foten, éin boge, vassrett gjennom bjelken
  H3  kjelda aldri naken    LED-stripa ligg inni bjelken og lyser inn i kanten på plata
  H4  éin matt farge        fot, røyr og bjelke i same pulverlakk
  H5  eitt messingpunkt     touch-dimmer i messing i den frie enden av bjelken, som på Salto
  H6  éi handling           vipp ruta: bjelken dreier på røyret

Mot revisjon A (lampe.py) er leddhuset, bolten, knotten, platearmen, fotfliken og kabeldekselet borte.
Røyret er både stamme, aksel og kabelveg. Skruane sit på undersida.

  python northern.py            kontroll og eksport til ut-b/
  python northern.py kontroll

Origo midt i foten på bordflata. x mot høgre, y bort frå brukaren, z opp. Alt i mm.
"""
import os, sys, math, json
import cadquery as cq
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
import lampe as L

UT = os.path.join(HER, 'ut-b')

# ------------------------------------------------------------------ proporsjonar
RUTE_B, RUTE_D, RUTE_T, FILM_T = L.RUTE_B, L.RUTE_D, L.RUTE_T, L.FILM_T
RUTE_HJORNE = 8.0        # avrunda frie hjørne på ruta
VINKEL = 35.0
VINKEL_OMRAADE = (0.0, 80.0)
AKSE_H = 260.0           # røyret sitt vassrette løp over bordet
FOT_D, FOT_H = 158.0, 16.0
ROYR_D, ROYR_T = 12.0, 1.5
ROYR_HELL = 30.0         # røyret hallar så mange grader ut mot høgre på veg opp. Flyttar ruta inn over foten
ROYR_BOGE = 45.0         # radius i den eine bogen
ROYR_FOT = (58.0, 22.0)  # der røyret går ned i foten (x, y)
BJELKE_D = 36.0
EKS = 9.5                # røyret ligg så langt bak midten av bjelken
DIMMER_D = 20.0          # messingpunktet
BALLAST_T = 5.0
BALLAST_X = 16.0         # ballasten ligg litt til høgre i foten og veg opp for ruta

R = BJELKE_D / 2
h = (RUTE_T + FILM_T + 0.05) / 2
U_KANT, U_SKRUE = L.U_KANT, L.U_SKRUE
YT = ROYR_FOT[1]                                             # planet røyret ligg i
_f = math.radians(ROYR_HELL)
Z0 = 3.0                                                     # røyret endar 3 mm over bordet, inne i foten
XC = ROYR_FOT[0] + (AKSE_H - FOT_H) * math.tan(_f)           # der skråbeinet ville møtt det vassrette løpet
_t = ROYR_BOGE * math.tan(math.radians(90.0 + ROYR_HELL) / 2)
T1 = (XC - _t * math.sin(_f), AKSE_H - _t * math.cos(_f))    # bogen startar
T2 = (XC - _t, AKSE_H)                                       # bogen sluttar, det vassrette løpet startar
X1 = T2[0] - 3.0                                             # høgre ende av bjelken, 3 mm før bogen startar
ENDE_V, ENDE_H = 14.0, 9.0                                   # endeveggene: venstre har rom til dimmaren, høgre til stoppsporet
X0 = X1 - RUTE_B - ENDE_V - ENDE_H                           # venstre ende
XR0, XR1 = X0 + ENDE_V, X1 - ENDE_H                          # ruta
STOPP_X = X1 - 4.5                                           # stoppskruen: står i røyret og går i eit spor inni høgre endevegg
STOPP_UT = 2.6                                               # så langt står han ut av røyret
BREMS_X = X1 - 40.0                                          # bremseskruen under bjelken
SKRUAR_X = [XR0 + f * RUTE_B for f in (0.08, 0.36, 0.64, 0.92)]
TOPP_T, VEGG = 2.4, 6.0
BOSS_R, BOSS_V = FOT_D / 2 - VEGG - 7.0, (95.0, 215.0, 335.0)
RHO = dict(L.RHO)

def paa_plass(lokal, vinkel):
    """Frå bjelken sitt eige system (x langs aksen, u ut i ruta, w mot undersida, origo midt i bjelken) til rommet.
    Bjelken dreier om røyret, som ligg EKS bak midten."""
    return lokal.translate((0, EKS, 0)).rotate((0, 0, 0), (1, 0, 0), 180.0 + vinkel).translate((0, YT, AKSE_H))

# ------------------------------------------------------------------ delane

def royr():
    """Eitt røyr i éi rørsle: skrått opp frå foten, éin boge, vassrett inn gjennom bjelken."""
    dl = (math.sin(_f), math.cos(_f))
    P0 = (ROYR_FOT[0] - (FOT_H - Z0) * math.tan(_f), Z0)
    O = (T2[0], AKSE_H - ROYR_BOGE)                                             # sentrum i bogen
    vm = math.atan2(XC - O[0], AKSE_H - O[1]) / 2                               # halvvegs mellom dei to tangentpunkta, sett frå sentrum
    a1 = math.atan2(T1[0] - O[0], T1[1] - O[1]); a2 = 0.0
    am = (a1 + a2) / 2
    M = (O[0] + ROYR_BOGE * math.sin(am), O[1] + ROYR_BOGE * math.cos(am))
    slutt = (X0 + 32.0, AKSE_H)
    veg = cq.Workplane('XZ', origin=(0, YT, 0)).moveTo(*P0).lineTo(*T1).threePointArc(M, T2).lineTo(*slutt)
    plan = cq.Plane(origin=(P0[0], YT, P0[1]), xDir=(0, 1, 0), normal=(dl[0], 0, dl[1]))
    r = cq.Workplane(plan).circle(ROYR_D / 2).circle(ROYR_D / 2 - ROYR_T).sweep(veg)
    return r.cut(paa_plass(L._syl_z(3.0, 2.0, ROYR_D / 2 + 1.0, STOPP_X, -EKS), 0.0))    # gjenga hol M3 på undersida, til stoppskruen

def _bjelke_lokal():
    """Snittet: røyret bak, LED-stripa i midten, plata i ei spalte framme. Loket sit på undersida, så oversida er heil."""
    syl = L._syl_x(BJELKE_D, X0, X1)
    x0, x1 = XR0 - 0.5, XR1 + 0.5
    hol = (L._boks(x0, x1, U_KANT - 0.3, R + 2, -h, h)
           .union(L._boks(x0, x1, 0.8, U_KANT - 0.3, -(L.LED_B + 2.4) / 2, (L.LED_B + 2.4) / 2))
           .union(L._boks(x0, x1, -1.3, 0.8, -(L.ALU_B + 0.4) / 2, (L.ALU_B + 0.4) / 2)))
    hol = hol.union(L._syl_x(ROYR_D + 0.4, X0 + 30.0, X1 + 1, -EKS, 0.0))            # boringa til røyret, open i høgre ende, botn i venstre
    hol = hol.union(L._boks(X0 + 34.0, X0 + 70.0, -EKS, -1.2, -2.0, 2.0))            # leidningen frå røyret inn til stripa
    hol = hol.union(L._syl_x(DIMMER_D + 1.0, X0 + 2.8, X0 + ENDE_V - 2.0, 0, 0))      # rom til dimmarkortet bak messingpunktet
    hol = hol.union(L._boks(X0 + ENDE_V - 2.5, XR0 + 1.0, 0.8, 3.0, -2.0, 2.0))       # leidningen frå dimmaren til stripa
    # stoppspor inni høgre endevegg. Stoppskruen står rett ned frå røyret og står i ro. Sett frå bjelken ligg han ved
    # vinkelen lik hellinga, målt frå undersida og inn mot ruta. Sporet er ein sektor med parallelle endar
    def _radial(d, r0, r1, beta):
        return L._syl_z(d, r0, r1, STOPP_X, -EKS).rotate((0, -EKS, 0), (1, -EKS, 0), -beta)
    b0, b1 = VINKEL_OMRAADE; r0, r1 = ROYR_D / 2 - 0.5, ROYR_D / 2 + STOPP_UT + 0.4
    pk = [(-EKS, 0.0)] + [(-EKS + r1 * math.sin(math.radians(a)), r1 * math.cos(math.radians(a))) for a in [b0 + (b1 - b0) * i / 20 for i in range(21)]]
    spor = cq.Workplane('YZ', origin=(STOPP_X - 1.75, 0, 0)).polyline(pk).close().extrude(3.5)
    spor = spor.union(_radial(3.5, r0, r1, b0)).union(_radial(3.5, r0, r1, b1))
    hol = hol.union(spor).union(L._syl_z(3.6, r1 - 0.5, R + 1, STOPP_X, -EKS))        # og eit hol nedanfrå til å setje skruen inn ved helling 0°
    lokkrom = L._boks(X0 + 3.0, X1 - 3.0, -1.3, R + 2, h, R + 2)                     # loket: undersida, mellom endeveggene
    kropp = syl.cut(lokkrom).cut(hol)
    lokk = syl.intersect(L._boks(X0 + 3.2, X1 - 3.2, -1.3 + 0.15, R + 2, h, R + 2)).cut(hol)
    skruar = None
    for x in SKRUAR_X:
        zt = math.sqrt(R * R - U_SKRUE ** 2)
        kropp = kropp.cut(L._syl_z(4.0, -h - 6.5, -h, x, U_SKRUE))                   # innpressmutter M3 i overkjeven
        lokk = lokk.cut(L._syl_z(3.4, h - 0.1, R + 1, x, U_SKRUE))
        lokk = lokk.cut(cq.Workplane('XY', origin=(x, U_SKRUE, zt - 2.2)).circle(3.2).extrude(2.6))
        sk = cq.Workplane('XY', origin=(x, U_SKRUE, zt - 2.0)).circle(2.8).extrude(1.7).union(L._syl_z(3.0, zt - 12.0, zt - 2.0, x, U_SKRUE))
        skruar = sk if skruar is None else skruar.union(sk)
    kropp = kropp.cut(L._syl_z(5.6, ROYR_D / 2 - 1.0, R + 1, BREMS_X, -EKS))             # bremseskrue M4 nedanfrå mot røyret (innpressmutter)
    kropp = kropp.cut(L._syl_x(DIMMER_D + 0.3, X0 - 0.1, X0 + 3.0, 0, 0))            # lomme til messingpunktet i venstre ende
    kropp = kropp.edges(cq.selectors.BoxSelector((X1 - 0.5, -R - 1, -R - 1), (X1 + 0.5, R + 1, R + 1))).fillet(1.5) if False else kropp
    plate = L._boks(XR0, XR1, U_KANT, U_KANT + RUTE_D, h - RUTE_T, h)
    form = (cq.Workplane('XY').center((XR0 + XR1) / 2, U_KANT + RUTE_D / 2 - 20.0).rect(RUTE_B, RUTE_D + 40.0).extrude(10).translate((0, 0, -5))
            .edges('|Z').fillet(RUTE_HJORNE))
    kile = (cq.Workplane('YZ', origin=(XR0 - 1, 0, 0))
            .polyline([(U_KANT + RUTE_D - RUTE_T, h - RUTE_T - 0.01), (U_KANT + RUTE_D + 0.01, h - RUTE_T - 0.01), (U_KANT + RUTE_D + 0.01, h + 0.01)])
            .close().extrude(RUTE_B + 2))
    plate = plate.intersect(form).cut(kile)
    film = L._boks(XR0, XR1, U_KANT, U_KANT + RUTE_D - 6.0, h - RUTE_T - FILM_T, h - RUTE_T).intersect(form.translate((0, -6.0, 0)))
    for x in SKRUAR_X:
        plate = plate.cut(L._syl_z(3.6, -5, 5, x, U_SKRUE)); film = film.cut(L._syl_z(3.6, -5, 5, x, U_SKRUE))
    led = L._boks(XR0 + 2, XR1 - 2, 0.8, 2.8, -L.LED_B / 2, L.LED_B / 2)
    alu = L._boks(XR0 + 2, XR1 - 2, -1.2, 0.8, -L.ALU_B / 2, L.ALU_B / 2)
    dimmer = L._syl_x(DIMMER_D, X0 - 1.0, X0 + 2.8, 0, 0).faces('<X').edges().chamfer(0.6)
    # stoppskruen: settskrue M3 med tapp, gjenga i røyrveggen. Held bjelken på røyret og stoppar hellinga i begge endar
    stopp = L._syl_z(2.9, ROYR_D / 2 - ROYR_T, ROYR_D / 2 + STOPP_UT, STOPP_X, -EKS)
    brems = L._syl_z(4.0, ROYR_D / 2 + 0.2, R - 1.0, BREMS_X, -EKS)                      # bremseskruen, med nylonspiss
    return dict(kropp=kropp, lokk=lokk, plate=plate, film=film, led=led, alu=alu, skruar=skruar, dimmer=dimmer, stopp=stopp, brems=brems)

def fot():
    f = L._syl_z(FOT_D, 0, FOT_H).faces('>Z').edges().fillet(3.0)
    f = f.cut(L._syl_z(FOT_D - 2 * VEGG, -0.1, FOT_H - TOPP_T))
    for v in BOSS_V:
        x, y = BOSS_R * math.cos(math.radians(v)), BOSS_R * math.sin(math.radians(v))
        f = f.union(L._syl_z(9.0, 2.0, FOT_H - TOPP_T + 0.1, x, y).union(
            L._boks(-4.5, 4.5, 0, FOT_D / 2 - VEGG - BOSS_R + 1.0, 2.0, FOT_H - TOPP_T + 0.1).translate((0, BOSS_R, 0)).rotate((0, 0, 0), (0, 0, 1), v - 90.0)))
        f = f.cut(L._syl_z(4.0, 1.9, 8.5, x, y))
    # hylse til røyret: skrå boring gjennom toppflata og ein kloss under, med settskrue nedanfrå
    xs = ROYR_FOT[0] - (FOT_H - 8.0) * math.tan(_f)
    f = f.union(L._boks(xs - 14, xs + 14, YT - 11, YT + 11, 2.0, FOT_H - TOPP_T + 0.1))
    d = cq.Vector(math.sin(_f), 0, math.cos(_f))
    p = cq.Vector(ROYR_FOT[0] - (FOT_H - Z0 + 1.0) * math.tan(_f), YT, Z0 - 1.0)
    f = f.cut(cq.Workplane('XY').newObject([cq.Solid.makeCylinder(ROYR_D / 2 + 0.15, 30.0, p, d)]))
    f = f.cut(L._syl_y(3.3, YT + 5, YT + 12, xs, 8.0))                                 # settskrue M4 mot røyret
    f = f.cut(L._boks(xs - 16, xs - 3, YT - 3, YT + 3, 1.9, 7.0))                        # leidningen frå røyret ut i holrommet
    f = f.cut(L._boks(-3.0, 3.0, FOT_D / 2 - VEGG - 1, FOT_D / 2 + 1, -0.1, 4.5))      # leidningen ut bak
    return f

def botnlok():
    l = L._syl_z(FOT_D - 2 * VEGG - 0.6, 0, 2.0)
    for v in BOSS_V:
        x, y = BOSS_R * math.cos(math.radians(v)), BOSS_R * math.sin(math.radians(v))
        l = l.cut(L._syl_z(3.4, -1, 3, x, y)).cut(L._syl_z(6.4, -0.1, 1.0, x, y))
    xs = ROYR_FOT[0] - (FOT_H - 8.0) * math.tan(_f)
    l = l.cut(L._boks(xs - 14.4, xs + 14.4, YT - 11.4, YT + 11.4, -0.1, 2.1))
    return l.cut(L._boks(-3.0, 3.0, FOT_D / 2 - VEGG - 4, FOT_D / 2, -0.1, 2.1))

def ballast():
    b = L._syl_z(106.0, FOT_H - TOPP_T - BALLAST_T, FOT_H - TOPP_T, BALLAST_X, 0.0)
    xs = ROYR_FOT[0] - (FOT_H - 8.0) * math.tan(_f)
    b = b.cut(L._boks(xs - 14.6, xs + 14.6, YT - 11.6, YT + 11.6, 0, FOT_H))
    for v in BOSS_V:
        x, y = BOSS_R * math.cos(math.radians(v)), BOSS_R * math.sin(math.radians(v))
        b = b.cut(L._syl_z(11.0, 0, FOT_H, x, y))
    return b

def leidning():
    """Stoffkledd leidning ut bak foten (berre til biletet)."""
    veg = cq.Workplane('XY', origin=(0, 0, 2.6)).moveTo(0, FOT_D / 2 - 2).spline([(10, FOT_D / 2 + 60), (60, FOT_D / 2 + 130), (40, FOT_D / 2 + 230)], includeCurrent=True)
    return cq.Workplane('XZ', origin=(0, FOT_D / 2 - 2, 2.6)).circle(2.4).sweep(veg)

def delar(vinkel=VINKEL):
    B = _bjelke_lokal(); P = lambda s: paa_plass(s, vinkel)
    D = [
        ('01', 'fot', fot(), 'petg', 'kropp', 1, 'prototyp: trykt og lakkert. Produksjon: trykkstøypt aluminium, matt pulverlakk'),
        ('02', 'botnlok med pute', botnlok(), 'petg', 'svart', 1, 'trykt, med svart mjuk pute under'),
        ('03', 'ballast', ballast(), 'staal', 'staal', 1, 'stålplate %g mm, skoren' % BALLAST_T),
        ('04', 'røyr', royr(), 'staal', 'kropp', 1, 'stålrøyr Ø %g × %g, éin boge med radius %g, same pulverlakk som foten' % (ROYR_D, ROYR_T, ROYR_BOGE)),
        ('05', 'bjelke', P(B['kropp']), 'petg', 'kropp', 1, 'prototyp: trykt i to lengder. Produksjon: ekstrudert aluminium, pulverlakk'),
        ('06', 'bjelkelok', P(B['lokk']), 'petg', 'kropp', 1, 'på undersida, fire skruar'),
        ('07', 'lysleiar', P(B['plate']), 'pmma', 'rute', 1, 'PMMA %g mm, frie hjørne R %g' % (RUTE_T, RUTE_HJORNE)),
        ('08', 'prismeark', P(B['film']), 'film', 'film', 1, 'prisma opp, rillene på tvers av bjelken'),
        ('09', 'flatstong', P(B['alu']), 'alu', 'staal', 1, 'aluminium 12 × 2'),
        ('10', 'led-stripe', P(B['led']), 'gummi', 'led', 1, 'KJØP: COB 5 V, 2700 K, 8 mm'),
        ('11', 'dimmer', P(B['dimmer']), 'messing', 'messing', 1, 'touch-dimmer i børsta messing, Ø %g' % DIMMER_D),
        ('12', 'stoppskrue', paa_plass(B['stopp'], 0.0), 'staal', 'staal', 1, 'settskrue M3 × 5 med tapp, gjenga i røyret nedanfrå. Stoppar hellinga ved %g° og %g° og held bjelken på røyret' % VINKEL_OMRAADE),
        ('13', 'bremseskrue', P(B['brems']), 'staal', 'staal', 1, 'M4 med nylonspiss, nedanfrå. Set friksjonen éin gong'),
        ('E', 'skrue M3 × 12 senk', P(B['skruar']), 'staal', 'staal', 4, 'nedanfrå, med innpressmutter'),
    ]
    return D

def vol(s): return s.val().Volume()

def kontroll(vis=True):
    D = delar()
    rap = dict(delar=[], kollisjonar=[], rorsle=[])
    M = mx = my = mz = 0.0
    for (i, namn, s, mat, *_r) in D:
        v = vol(s); ma = v * RHO[mat]; c = s.val().Center()
        rap['delar'].append(dict(id=i, namn=namn, masse_g=round(ma, 1), gyldig=bool(s.val().isValid())))
        M += ma; mx += ma * c.x; my += ma * c.y; mz += ma * c.z
    M += 30.0
    T = (mx / M, my / M, mz / M); r = FOT_D / 2; e = math.hypot(T[0], T[1]); g = 9.81e-3
    t = math.radians(VINKEL)
    yf = YT - math.cos(t) * (U_KANT + RUTE_D + EKS)
    rap.update(masse_g=round(M), tyngdepunkt=[round(x, 1) for x in T], fotavtrykk_cm2=round(math.pi * r * r / 100, 1),
               veltevinkel=round(math.degrees(math.atan((r - e) / T[2])), 1),
               velt_venstre_N=round(M * g * (r + T[0]) / max(-XR0 - r, 1e-6), 1), velt_framme_N=round(M * g * (r + T[1]) / max(-yf - r, 1e-6), 1),
               velt_dytt_topp_N=round(M * g * (r - e) / AKSE_H, 1), delar_i_alt=len(D))
    fri = {'E', '13'}
    for a in range(len(D)):
        for b_ in range(a + 1, len(D)):
            if D[a][0] in fri or D[b_][0] in fri: continue
            try: v = vol(D[a][2].intersect(D[b_][2]))
            except Exception: v = 0.0
            if v > 0.5: rap['kollisjonar'].append((D[a][1], D[b_][1], round(v, 1)))
    faste = [d for d in D if d[0] in ('01', '04', '12')]
    for vk in range(int(VINKEL_OMRAADE[0]), int(VINKEL_OMRAADE[1]) + 1, 10):
        Dv = delar(float(vk)); rorl = [d for d in Dv if d[0] in ('05', '06', '07', '08')]
        verst = 0.0; kven = ''
        for a in rorl:
            for b_ in faste:
                try: v = vol(a[2].intersect(b_[2]))
                except Exception: v = 0.0
                if v > verst: verst, kven = v, a[1] + ' mot ' + b_[1]
        rap['rorsle'].append(dict(vinkel=vk, kollisjon_mm3=round(verst, 1), kven=kven, laagaste_punkt=round(min(d[2].val().BoundingBox().zmin for d in rorl), 1)))
    if vis:
        print('masse %d g (krav 1200)  ·  fotavtrykk %.1f cm² (krav 200)  ·  tyngdepunkt x %.1f y %.1f z %.1f  ·  %d delar' % (rap['masse_g'], rap['fotavtrykk_cm2'], *rap['tyngdepunkt'], len(D)))
        print('veltevinkel %.1f°  ·  velt ved trykk på venstre hjørne %.1f N, fremste kant %.1f N, dytt i toppen %.1f N' % (rap['veltevinkel'], rap['velt_venstre_N'], rap['velt_framme_N'], rap['velt_dytt_topp_N']))
        for d in rap['delar']: print('  %-3s %-18s %7.1f g %s' % (d['id'], d['namn'], d['masse_g'], '' if d['gyldig'] else 'UGYLDIG'))
        print('kollisjonar:', rap['kollisjonar'] or 'ingen')
        for r_ in rap['rorsle']: print('  helling %2d°: kollisjon %.1f mm³ %s · lågaste punkt %.0f mm' % (r_['vinkel'], r_['kollisjon_mm3'], r_['kven'], r_['laagaste_punkt']))
    return rap

FARGE = dict(kropp=(0.62, 0.59, 0.55), svart=(0.08, 0.08, 0.08), staal=(0.45, 0.46, 0.48), rute=(0.92, 0.96, 1.0), film=(1.0, 0.93, 0.80),
             led=(1.0, 0.85, 0.5), messing=(0.80, 0.66, 0.36))

def eksporter():
    from cadquery import exporters
    for d in ('step', 'stl', 'samla'): os.makedirs(os.path.join(UT, d), exist_ok=True)
    D = delar()
    a = cq.Assembly(name='ruta-pa-fot-rev-b')
    for (i, namn, form, mat, farge, n, _) in D:
        a.add(form, name='%s_%s' % (i, namn.replace(' ', '_').replace('×', 'x')), color=cq.Color(*FARGE[farge]))
        exporters.export(form, os.path.join(UT, 'samla', i + '.stl'), tolerance=0.03, angularTolerance=0.1)
        exporters.export(form, os.path.join(UT, 'step', '%s_%s.step' % (i, namn.replace(' ', '_').replace('×', 'x'))))
    exporters.export(leidning(), os.path.join(UT, 'samla', 'leidning.stl'), tolerance=0.05, angularTolerance=0.15)
    a.export(os.path.join(UT, 'ruta-pa-fot-rev-b.step'))
    B = _bjelke_lokal(); xm = 0.5 * (XR0 + XR1)
    def del_x(form, x0, x1): return form.intersect(L._boks(x0, x1, -40, 40, -40, 40))
    staaande = lambda f: f.rotate((0, 0, 0), (0, 1, 0), -90)
    d = {x[0]: x[2] for x in D}
    P = [('01_fot', d['01'].rotate((0, 0, 0), (1, 0, 0), 180)), ('02_botnlok', d['02']),
         ('05_bjelke_venstre', staaande(del_x(B['kropp'], X0 - 1, xm - 12))), ('05_bjelke_hogre', staaande(del_x(B['kropp'], xm - 12, X1 + 1))),
         ('06_bjelkelok_venstre', staaande(del_x(B['lokk'], X0 - 1, xm + 12))), ('06_bjelkelok_hogre', staaande(del_x(B['lokk'], xm + 12, X1 + 1))),
         ('prove_bjelkesnitt', staaande(del_x(B['kropp'], SKRUAR_X[1] - 10, SKRUAR_X[1] + 10))),
         ('prove_loksnitt', staaande(del_x(B['lokk'], SKRUAR_X[1] - 10, SKRUAR_X[1] + 10)))]
    for namn, f in P:
        bb = f.val().BoundingBox()
        f = f.translate((-0.5 * (bb.xmin + bb.xmax), -0.5 * (bb.ymin + bb.ymax), -bb.zmin))
        exporters.export(f, os.path.join(UT, 'stl', namn + '.stl'), tolerance=0.02, angularTolerance=0.1)
        bb = f.val().BoundingBox(); print('  stl %-22s %5.0f x %5.0f x %5.0f mm' % (namn, bb.xlen, bb.ylen, bb.zlen))
    # røyret: rett lengd før bøying
    lengd = math.hypot(T1[0] - (ROYR_FOT[0] - (FOT_H - Z0) * math.tan(_f)), T1[1] - Z0) + ROYR_BOGE * math.radians(90.0 + ROYR_HELL) + (T2[0] - (X0 + 32.0))
    print('  røyret: %.0f mm langt før bøying, éin boge på %.0f° med radius %.0f mm i senterlina' % (lengd, 90.0 + ROYR_HELL, ROYR_BOGE))
    return lengd

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    os.makedirs(UT, exist_ok=True)
    rap = kontroll()
    rap['stykkliste'] = [dict(id=i, namn=n, tal=t, materiale=m_, framstilling=pr) for (i, n, _, m_, _, t, pr) in delar()]
    if sys.argv[1:2] != ['kontroll']:
        rap['royr_lengd'] = round(eksporter())
    json.dump(rap, open(os.path.join(UT, 'kontroll.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
