# -*- coding: utf-8 -*-
"""
segl_geometri.py  ·  Konsept D «Segl»: alle mål, punkt og utbretta plater (2D)

To bretta segl i pulverlakkert stålplate (DC01 1,5 mm) og ei lita klampe med dreieknapp.
Framseglet (D01) står på ein fotflens som vender mot brukaren. Høgseglet (D02) står bak og har
golvet inne i V-en som fot; ein leppe på golvet er skrudd til framseglet på tre sveiseboltar.
LED-modulen (E01) ligg på golvet og lyser opp mot innsida av høgseglet. Klampa (E02) er skrudd
til ei tunge på framseglet sin fotflens.

Koordinatar: origo i den låge spissen til framseglet på bordflata. x langs framseglet mot høgre,
y bort frå brukaren (mot veggen), z opp. Alt i mm og grader.

Kvar tal har opphav i kommentaren:
  MÅLT    lese ut av skissa med kamerapassing (scratch maal/kamera*.py, kantar*.json)
  VALT    designval eg har teke og grunngjeve i LES_MEG
  DATABLAD frå produsent (sjå innkjøpsplanen)
  ANTEKE  ikkje stadfesta
"""
import math
import numpy as np

# ------------------------------------------------------------------ plate og bøying
T = 1.5            # DC01 platetjukkleik. VALT (forsking: 1,5 gjev 3,4 x stivleiken til 1,0; MÅLT kant ca 1,3-1,5)
RI = 1.65          # innvendig bøyeradius 90° i 1,5 mm stål, V10-dyse. DATABLAD 247TailorSteel
K = 0.40           # K-faktor. ANTEKE (sjå LES_MEG); fil til verkstaden er den bretta STEP-en
ZP = T + RI        # 3,15: høgda der den flate delen av seglet byrjar over bøyen
BA90 = math.pi / 2 * (RI + K * T)    # bøyetillegg 90°
FLENS = 12.5       # fotflensen, frå framsida av seglet til ytterkanten. MÅLT 12,3-12,9
R_SPISS = 3.0      # radius på dei frie spissane. VALT (regelverk: min R3 på spissar; 60598-1 4.25)
R_HJORNE = 2.0     # radius på flenshjørne. VALT
R_KANT = 0.5       # alle andre ytterhjørne i utbrettinga. VALT (laser rundar sjølv til R0,3)
FLENS_GLIPE = 1.6  # glipe mellom flensane ved falden. VALT (minste laserspalte 1,5 mm i stål; DATABLAD 247TailorSteel)
MIN_SPALTE = 1.6   # minste spalte mellom delar av same emne. VALT

# ------------------------------------------------------------------ framseglet D01
F_A = 123.0        # frå den låge spissen til foten av falden. MÅLT 122,5-125,3
F_B = 121.5        # frå falden til foten av den loddrette kanten. MÅLT 121,6-121,9
F_KNEKK = -5.0     # foten knekk mot brukaren ved falden. MÅLT -1 til -2 (skugge tyder på fleire); VALT -5
                   # slik at falden blir 5,8°, innanfor 175° som er grensa for kantpressa
F_H = 205.0        # toppen av den avrunda spissen over bordet. MÅLT (skalaankeret for heile lampa)

# ------------------------------------------------------------------ høgseglet D02
H_P1 = (-0.5, 6.5) # den låge spissen (bakre flate). MÅLT ca (-2,4; 4); VALT med 3,7 mm luft til D01 for leidningen
H_RETN = 26.0      # retninga til det smale feltet, grader frå x. VALT (biletet kan ikkje skilje; skuggen avgjer forteiknet)
H_A = 54.0         # frå spissen til foten av falden. MÅLT 52,9-54,8 ved denne retninga
H_KNEKK = -10.0    # foten knekk mot framseglet ved falden. VALT (stivar seglet; skugge: smalt felt mørkare)
H_B = 86.0         # frå falden til foten av den loddrette kanten. MÅLT 85,6-86,4
H_H = 305.0        # toppen av den avrunda spissen. MÅLT 304,9-305,7

# ------------------------------------------------------------------ golv og leppe på D02
LEPP_X = (45.0, 115.0)  # leppa ligg mot innsida av framseglet sitt venstre felt. VALT
LEPP_H = 26.0           # høgd på leppa. VALT: boltane må over setet til lysberaren
LEPP_LUFT = 0.15        # luft mellom leppa og framseglet (pulverlakk 2 x 70 µm). VALT
BOLT_X = (55.0, 82.0, 105.0)   # sveisebolt M3 på innsida av framseglet. VALT
BOLT_Z = 19.5           # høgd over bordet. VALT (over setet til E01, >10 mm frå bøyelinja)
TUNGE_X = 180.0         # golvet held fram som ei tunge langs framseglet til hit. VALT
TUNGE_Y = (3.0, 27.0)   # tunga sin framkant og bakkant. VALT
GOLV_X0 = 42.0          # venstre kant av golvet. VALT
E01_BOLT = ((70.0, 19.5), (152.0, 19.5))   # sveisebolt M3 opp frå golvet for lysmodulen. VALT

# ------------------------------------------------------------------ tunge under klampa (del av D01 sin flens)
TUNGE_KLAMPE = (-31.0, 2.2, 9.0)   # x0, v0, v1 (v = avstand frå framsida av seglet mot brukaren). VALT
KLAMPE_SKRUE = ((-24.0, -5.6), (-8.0, -5.6))   # to M3 senkskruar nedanfrå gjennom tunga. VALT

# ------------------------------------------------------------------ klampa E02 og knappen E03
KL_X = (-35.0, -1.0)    # MÅLT x0 = -34,3
KL_Y = (-9.5, 29.5)     # MÅLT djupn 38,9; framsida 3 mm bak flenskanten (skissa)
KL_H = 18.7             # MÅLT
KL_VEGG = 2.0           # VALT (fresa aluminium)
KNAPP_D = 22.0          # MÅLT
KNAPP_H = 7.6           # MÅLT
KNAPP_LUFT = 1.0        # luft mellom knappen og toppen av klampa. DATABLAD PEC12R (trykkvandring 0,7)
KNAPP_XY = (-17.6, 10.0)  # MÅLT (-17,6; 10,1)

# ------------------------------------------------------------------ lysmodulen E01
AL_T = 1.5              # EN AW-5754 H22. VALT
E01_X = (44.0, 172.5)   # berar med endeflik i begge endar. VALT
LED_X = (45.5, 170.5)   # LEDYI LY224-S2216DTW-W24, 2 steg à 62,5 mm = 125. DATABLAD. VALT: berre der høgseglet skjermar (sjå segl_lys)
LED_B = 10.0            # breidd. DATABLAD
LED_T = 1.2             # høgd. DATABLAD
E01_BASE_Y = (14.0, 26.0)   # botnen på beraren. VALT
E01_SETE = 15.0         # setet stig 45° mot framseglet. VALT
E01_SKJERM_X0 = 128.0   # skjermleppa bak stripa finst berre der høgseglet ikkje skjermar. VALT
E01_SKJERM_H = 45.0     # VALT (skjermar stripa bakfrå opp til ca 65°)
E01_ENDE_H = 14.0       # endeflikene. VALT (skjermar stripa langs V-en frå endane; 18 slo i høgseglet)
E01_VENG_Y = 50.0       # vengen på skjermleppa går bak til høgseglet og stengjer glipa mellom dei. VALT

V3 = lambda *a: np.array(a, dtype=float)
Z = V3(0, 0, 1)


def eining(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def rot2(v, grader):
    a = math.radians(grader)
    return np.array([v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a)])


# ------------------------------------------------------------------ eit bretta segl: to felt og ein fald

class Segl:
    """To plane felt som møtest i ein fald. Referanseflata er den synlege yttersida; platetjukkleiken går inn i V-en.

    venstre felt: frå spissen (S) via foten av falden (Q) til toppen (A)
    høgre felt:   frå Q via foten av den loddrette kanten (B) til A. Høgre felt står loddrett.
    `fot_z`: høgda på botnlinja i referanseflata (ZP når feltet byrjar over ein bøy, 0 når kanten står på bordet).
    """

    def __init__(self, S, Q, B, topp, fot_z_v, fot_z_h, inn):
        self.S2, self.Q2, self.B2 = np.array(S, float), np.array(Q, float), np.array(B, float)
        self.inn = eining(V3(*inn, 0))           # vassrett retning inn i V-en (berre forteiknet tel)
        # toppen: teoretisk spiss rett over B, justert slik at den avrunda spissen når `topp`
        self.Hteori = topp
        for _ in range(30):
            self._bygg(fot_z_v, fot_z_h)
            fall = self.topp_avrunda() - topp
            if abs(fall) < 1e-6:
                break
            self.Hteori -= fall

    def _bygg(self, fz_v, fz_h):
        self.S = V3(self.S2[0], self.S2[1], fz_v)
        self.Q = V3(self.Q2[0], self.Q2[1], fz_v)
        self.Qh = V3(self.Q2[0], self.Q2[1], fz_h)
        self.B = V3(self.B2[0], self.B2[1], fz_h)
        self.A = V3(self.B2[0], self.B2[1], self.Hteori)
        # utbretta ramme: venstre felt sitt plan
        self.e1 = eining(self.Q - self.S)
        w = self.A - self.Q
        self.e2 = eining(w - w.dot(self.e1) * self.e1)
        self.nV = np.cross(self.e1, self.e2)
        if self.nV.dot(self.inn) < 0:
            self.nV = -self.nV                    # normal inn i V-en
        # høgre felt
        self.c = eining(self.A - self.Q)          # falden (frå Q til A)
        b = self.B - self.Qh
        self.pH = eining(b - b.dot(self.c) * self.c) if np.linalg.norm(b - b.dot(self.c) * self.c) > 1e-9 else None
        self.nH = eining(np.cross(eining(self.B - self.Qh), eining(self.A - self.Qh)))
        if self.nH.dot(self.inn) < 0:
            self.nH = -self.nH
        # 2D: Q i origo, e1 langs x
        self.c2 = np.array([self.c.dot(self.e1), self.c.dot(self.e2)])
        self.n_c2 = np.array([-self.c2[1], self.c2[0]])
        sV = np.sign(self.til2d_v(self.S).dot(self.n_c2))
        self.sH = -sV
        self.fald = math.degrees(math.acos(np.clip(abs(self.nV.dot(self.nH)), -1, 1)))

    # 3D -> 2D og attende for kvart felt
    def til2d_v(self, P):
        d = np.asarray(P, float) - self.Q
        return np.array([d.dot(self.e1), d.dot(self.e2)])

    def til3d_v(self, p):
        return self.Q + p[0] * self.e1 + p[1] * self.e2

    def til2d_h(self, P):
        d = np.asarray(P, float) - self.Q
        a = d.dot(self.c)
        b = d - a * self.c
        lb = b.dot(self.pH)
        return a * self.c2 + self.sH * lb * self.n_c2

    def til3d_h(self, p):
        a = p.dot(self.c2)
        b = p.dot(self.n_c2) * self.sH
        return self.Q + a * self.c + b * self.pH

    def side(self, p):
        """'v' eller 'h': kva felt eit 2D-punkt høyrer til (kva side av falden)."""
        return 'h' if p.dot(self.n_c2) * self.sH > 0 else 'v'

    def til3d(self, p):
        return self.til3d_h(p) if self.side(p) == 'h' else self.til3d_v(p)

    # spissen
    def bue_spiss(self, r=R_SPISS, n=14):
        """Bogen som rundar toppen, i 2D: (tangentpunkt hypotenus, punkt langs bogen..., tangentpunkt loddrett kant)."""
        A = self.til2d_v(self.A)
        dS = eining(self.til2d_v(self.S) - A)          # langs hypotenusen ned
        dB = eining(self.til2d_h(self.B) - A)          # langs den loddrette kanten ned
        th = math.acos(np.clip(dS.dot(dB), -1, 1))
        d = r / math.tan(th / 2)
        tS, tB = A + d * dS, A + d * dB
        C = A + r / math.sin(th / 2) * eining(dS + dB)
        a0 = math.atan2(*(tS - C)[::-1])
        a1 = math.atan2(*(tB - C)[::-1])
        # kortaste vegen rundt over toppen
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        return [C + r * np.array([math.cos(a0 + da * i / n), math.sin(a0 + da * i / n)]) for i in range(n + 1)], th

    def topp_avrunda(self):
        pts, _ = self.bue_spiss()
        return max(self.til3d(p)[2] for p in pts)

    def spissvinkel(self):
        return math.degrees(self.bue_spiss()[1])


def lag_d01():
    Q = (F_A, 0.0)
    B = (F_A + F_B * math.cos(math.radians(F_KNEKK)), F_B * math.sin(math.radians(F_KNEKK)))
    # spissen på hypotenusen: der hypotenusen kryssar ZP; set teoretisk spiss på bordet i x = 0
    s = Segl(S=(0.0, 0.0), Q=Q, B=B, topp=F_H, fot_z_v=ZP, fot_z_h=ZP, inn=(0, 1))
    # flytt S langs linja y=0 slik at hypotenusen treffer bordet i x = 0
    for _ in range(20):
        A = s.A
        x_s = A[0] * ZP / A[2]
        s.S2 = np.array([x_s, 0.0])
        s._bygg(ZP, ZP)
        # hald toppen
        fall = s.topp_avrunda() - F_H
        s.Hteori -= fall
        s._bygg(ZP, ZP)
    return s


def lag_d02():
    P1 = np.array(H_P1)
    d1 = np.array([math.cos(math.radians(H_RETN)), math.sin(math.radians(H_RETN))])
    Q = P1 + H_A * d1
    d2 = rot2(d1, H_KNEKK)
    B = Q + H_B * d2
    # inn i V-en: framover (mot framseglet), vinkelrett på hovudfeltet
    inn = (d2[1], -d2[0])
    return Segl(S=P1, Q=Q, B=B, topp=H_H, fot_z_v=0.0, fot_z_h=ZP, inn=inn)


D01 = lag_d01()
D02 = lag_d02()

# leppa: parallell med innsida av framseglet sitt venstre felt
def leppe_plan():
    """Punkt og normal for yttersida av leppa (den som ligg mot framseglet)."""
    p0 = D01.Q + D01.nV * (T + LEPP_LUFT)       # innsida av framseglet + luft, i høgd ZP
    return p0, D01.nV


def golv_punkt():
    """Golvet til D02 i plan (z = 0..T). Returnerer liste med 2D-punkt mot klokka."""
    s = D02
    u = eining(s.B2 - s.Q2)                      # langs hovudfeltet
    w = eining(s.inn[:2])                        # inn i V-en
    tang = lambda t_: s.Q2 + t_ * u + (RI + T) * w   # tangenten der golvet byrjar
    Lh = np.linalg.norm(s.B2 - s.Q2)
    # leppa sin tangentlinje i golvet: y = y_lepp + RI + T (i høgd 0)
    p0, n = leppe_plan()
    y_lepp = p0[1] - (p0[2] - 0.0) * 0 if True else 0
    # framsida av leppa på bordet (plan med normal n gjennom p0): y på z = ZP. Leppa er nesten loddrett.
    y_lepp = p0[1]
    y_fram = y_lepp + RI + T
    pts = []
    pts.append(np.array([GOLV_X0, y_fram]))
    pts.append(np.array([LEPP_X[1], y_fram]))
    pts.append(np.array([LEPP_X[1], TUNGE_Y[0]]))
    pts.append(np.array([TUNGE_X, TUNGE_Y[0]]))
    pts.append(np.array([TUNGE_X, TUNGE_Y[1]]))
    # frå tunga skrått opp til bakhjørnet ved B (relieff 1 mm før enden av bøyen, 2 mm inn)
    b_ende = tang(Lh - 1.0)
    pts.append(np.array([b_ende[0] + 14.0, TUNGE_Y[1]]))
    pts.append(b_ende + 2.0 * w)
    pts.append(b_ende)
    # langs bøyen til starten (relieff 1,5 mm ved falden)
    pts.append(tang(1.5))
    # venstre kant: ned til leppelinja, med luft til det smale feltet
    s_v = tang(1.5) + 0.0 * w
    pts.append(np.array([GOLV_X0, s_v[1] - 6.0]))
    return pts, y_fram, y_lepp


def kontrolltal():
    d = {}
    for namn, s in (('D01', D01), ('D02', D02)):
        d[namn] = dict(
            fald_grader=round(s.fald, 2),
            spissvinkel_grader=round(s.spissvinkel(), 2),
            teoretisk_topp=round(s.Hteori, 2),
            avrunda_topp=round(s.topp_avrunda(), 2),
            S=s.S.round(2).tolist(), Q=s.Q.round(2).tolist(), B=s.B.round(2).tolist(), A=s.A.round(2).tolist(),
        )
    return d


if __name__ == '__main__':
    import json
    print(json.dumps(kontrolltal(), indent=1, ensure_ascii=False))
    print('golv', [p.round(1).tolist() for p in golv_punkt()[0]])
