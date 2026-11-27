# -*- coding: utf-8 -*-
"""fasett.py: skalvariant «fasett». Eit luftskrog med mangekanta ramme: dragarane står i rette
liner og lerretet heng rett frå dragar til dragar.

Dei to runde endane, nasen og akterenden (venstre boge), blir mangekantar. Ytterflata er ein
omskriven sekskant: seks loddrette fasettar per halvsirkel, kvar 30 grader, og kantane mellom
dei er dragarane. Midt i kvar fasett tangerer flata sirkelen (h = 0), og i dragaren står ho ut
h = R / cos(15°) − R = 0,52 mm. Både nasen og akterenden har ein flat fasett i spissen, og den
siste halve fasetten fell saman med den flate sida, så mangekanten går reint over i framsida og
baksida utan steg. Alt står loddrett (konstant i z), så kantane blir skarpe i print. Dei er
stumpe (150 grader), ikkje spisse. Fasettane går heilt opp til toppkanten og stoppar der reint
(sjå komp() for kvifor), og dei går gjennom heile akterenden, stamme og skjerm i eitt.

Dei flate sidene får dragarlinene som held fram frå endane: låge, tydelege liner på 0,3 mm med
jamn deling.
  Skjermen er skroget. Fem breie banar (7 mm) mellom seks rette liner, og linene trekkjer seg
  jamt saman mot nasen (til 22 %) og svakare mot akterenden (til 62 %), rett som i eit skrog.
  Den nedste lina er kjølen, rett over stamma. Den øvste ligg langs toppkanten.
  Stamma er gondolen. Der står dei loddrette linene tettare (3,8 mm, halve fasettbreidda), som
  gondolplatene. På baksida går dei frå fot til kjøl. Framme er LED-feltet gondolens vindauge:
  ei ramme rundt det, og linene under stoppar mot botnlista. Akterkanten av rammen er den første
  dragaren i akterenden, så rammen har ikkje eigen stolpe der.
Spantet er ein loddrett ringsaum over skroget, i flukt med kanten av stamma (det indre hjørnet) og
der banane begynner å trekkje seg saman mot nasen. Nasekapselen er ein ring med ei låg skive i
spissen. Banane endar mot ho.

Alt relieff er 0,3 til 0,5 mm og står på ei flate med skråning under 35 grader, så det går an å
printe opp ned utan støtte. Ingen tilfeldig støy.
"""
import numpy as np
from scipy import ndimage

import skal as SK
from skal import BUE, P, R, S, S_VENSTRE, X_ST, Z_SK, glatt

# ---------------------------------------------------------------- mål (mm)
ZC = (Z_SK + S) / 2                       # midten av skjermen i høgda, 65,45; nasen sit her
S_AKTER = (S_VENSTRE[0] + S_VENSTRE[1]) / 2   # spissen av akterenden, 100,8

N_FASETT = 6                              # fasettar per halvsirkel
DELTA = np.pi / N_FASETT                  # 30 grader per fasett

H_LINE = 0.35                             # dragarlinene
H_SPANT = 0.30                            # spantet er litt lågare og smalare enn dragarane
HW_STAMME = 0.70                          # dei loddrette linene i stamma er finare
HW_LINE = 0.90                            # halv breidd ytst (heile lina er 1,8 mm)
RAMPE = 0.50                              # skråning på sidene av lina: 0,35 mm på 0,5 mm, 35 grader

N_BANAR = 5                               # banar i skjermen, frå kjøl til toppkant
Z_KJOL = Z_SK + 1.0                       # kjølen, nedste line: 1 mm over botnkanten av skjermen
Z_TOPP = S - 1.0                          # øvste line: 1 mm under toppkanten
PITCH = (Z_TOPP - Z_KJOL) / N_BANAR       # banebreidda langt frå nasen, 7,0

X_LINJE = SK.FELT[2] + 3.3                # dragaren langs kanten av stamma og spantet over han, x = 48,64
G_NASE = 0.22                             # banane er 22 % så breie i nasen
L_NASE = BUE + (S - R - X_LINJE)          # og parallelle frå spantet i det indre hjørnet, 43,75 mm frå nasen
G_AKTER, L_AKTER = 0.62, BUE              # akterenden: 62 %, og parallelle frå overgangen til den flate sida

R_KAPSEL = 7.0                            # nasekapselen: ring og låg skive
H_RING, H_SKIVE = 0.40, 0.20

PITCH_ST = (X_LINJE - R) / 9              # dei loddrette linene i stamma, 3,77 mm
D_RAMME = 3.3                             # midten av vindaugsramma frå feltkanten (utanfor tonen 2,5)
X_KREST = R - R * np.sin(DELTA / 2)       # første dragar i akterenden på framsida, x = 10,9


# ---------------------------------------------------------------- hjelparar
def rygg(d, hw=HW_LINE, ramp=RAMPE):
    """Profil 0..1 over ei line: flat topp, mjuke sider. d er avstanden frå midtlinja."""
    t = np.clip((hw - d) / ramp, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def sid(H, s0):
    """Fortegna boglengd frå s0, rekna rundt."""
    return ((H.S - s0 + P / 2) % P) - P / 2


def avst_felt(H):
    """mm langs huda frå kanten av feltet. H.d_felt tel òg topp- og botnkanten som felt, så ei eiga
    utrekning her: der får z-kantane tilsvarande fyll og ikkje nokon avstand."""
    felt = SK.i_felt(H.X, H.Z) & H.framme
    pad = H.ns // 2
    m = np.concatenate([~felt[-pad:], ~felt, ~felt[:pad]], axis=0)
    m = np.pad(m, ((0, 0), (1, 1)), mode="edge")
    d = ndimage.distance_transform_edt(m, sampling=(H.ds, H.dz))
    return np.maximum(d[pad:-pad, 1:-1] - 0.5 * H.steg, 0.0)


def mangekant(avst):
    """Omskriven mangekant rundt ei halv sirkel: h = R / cos(vinkel til midten av næraste fasett) − R.
    avst er boglengda frå spissen. Fasettsenter ligg i spissen og kvar DELTA, så det er eit senter òg
    der sirkelen går over i den flate sida (a = 90 grader). Utanfor boga er h = 0."""
    a = np.asarray(avst) / R
    d = a - np.round(a / DELTA) * DELTA
    return np.where(a <= np.pi / 2 + 1e-9, R * (1.0 / np.cos(d) - 1.0), 0.0)


def trekk_saman(H):
    """Kor tett banane ligg (1 = full breidd), som funksjon av s åleine. Lineært mot nasen og mot
    akterenden: rette liner."""
    s1 = H.S[:, 0]
    dn = np.abs(((s1 + P / 2) % P) - P / 2)
    dt = np.abs(((s1 - S_AKTER + P / 2) % P) - P / 2)
    gn = G_NASE + (1 - G_NASE) * np.clip(dn / L_NASE, 0.0, 1.0)
    gt = G_AKTER + (1 - G_AKTER) * np.clip(dt / L_AKTER, 0.0, 1.0)
    return gn * gt


def banelinene(H, g):
    """Dei seks dragarlinene langs skroget. Returnerer line-profilen og z for kjølen (som funksjon av s)."""
    gd = np.gradient(g, H.ds)
    prof = np.zeros(H.S.shape)
    for j in range(N_BANAR + 1):
        zj = ZC + (j - N_BANAR / 2) * PITCH * g
        dz = (j - N_BANAR / 2) * PITCH * gd
        d = np.abs(H.Z - zj[:, None]) / np.sqrt(1.0 + dz[:, None] ** 2)
        hw = np.clip(0.3 * PITCH * g, 0.5, HW_LINE)[:, None]        # linene blir smalare med banen
        prof = np.maximum(prof, rygg(d, hw, 0.55 * hw))
    kjol = ZC - (N_BANAR / 2) * PITCH * g
    return prof, kjol


def loddrette(H, kjol):
    """Dei loddrette linene i stamma, halve fasettbreidda frå kvarandre og i flukt med akterenden."""
    xk = np.linspace(R, X_LINJE, 10)
    d = np.min(np.abs(H.X[..., None] - xk), axis=-1)
    flat = (H.flate == 1) | (H.flate == 3)
    # baksida: frå fot til kjøl. Framme: berre under botnlista av rammen, og ikkje forbi kanten av feltet.
    bak = flat & ~H.framme & (H.Z <= kjol[:, None] + 0.1)
    fram = flat & H.framme & (H.X < X_ST - 3.0)
    return rygg(d, HW_STAMME, 0.42), bak, fram


def hud(H):
    d_f = avst_felt(H)
    g = trekk_saman(H)
    ds_nase = np.abs(sid(H, 0.0))
    ds_akter = np.abs(sid(H, S_AKTER))

    # ---- mangekanten i endane: gjennom heile høgda, fast kant mot toppkanten
    poly = mangekant(ds_nase) + mangekant(ds_akter)

    # ---- nasekapselen
    r = np.hypot(sid(H, 0.0), H.Z - ZC)
    kapsel = np.maximum(H_RING * rygg(np.abs(r - R_KAPSEL), 0.9, 0.5), H_SKIVE * glatt(R_KAPSEL + 0.6 - r, 0.0, 0.6)) * H.skjerm
    lin_h, kjol = banelinene(H, g)
    lin_h = H_LINE * lin_h * (r > R_KAPSEL + 0.1) * H.skjerm * (H.Z < S - 0.2)

    # ---- stamma
    lod, bak, fram = loddrette(H, kjol)
    lin_v = H_LINE * lod * (bak | (fram & (H.Z <= Z_RAMME_BOTN(H))))

    # ---- spantet: ein ringsaum over skroget i flukt med kanten av stamma (det indre hjørnet), der banane
    # begynner å trekkje seg saman. Loddrett, så han blir skarp i print.
    flat = (H.flate == 1) | (H.flate == 3)
    spant = H_SPANT * rygg(np.abs(H.X - X_LINJE), 0.75, 0.45) * flat * (H.Z >= Z_KJOL - 0.1) * (H.Z <= Z_TOPP + 0.1)

    # ---- vindaugsramma: ridge rundt feltet, utan akterstolpe (den første dragaren er stolpen)
    ramme = H_LINE * rygg(np.abs(d_f - D_RAMME)) * (d_f > 0) * H.framme * glatt(H.X, X_KREST, X_KREST + 1.1)
    ramme = ramme * (H.Z < Z_SK - 0.5)

    mål = poly + np.maximum.reduce([lin_h, lin_v, spant, ramme]) + kapsel
    return komp(mål, H)


def Z_RAMME_BOTN(H):
    """z for midten av botnlista i rammen."""
    return SK.FELT[1] - D_RAMME


def komp(mål, H):
    """skal.bygg() tonar h ned mot feltet og mot topp- og botnkanten (d_felt, 0,3 til 2,5 mm). Fasettane
    og linene skal gå reint inn i toppkanten, så h blir delt på same tonen. Er ikkje det mogleg (tonen er
    under mål / 2), blir resultatet den tona rampa 2·tone: på 1 mm frå kanten er ho full."""
    tone = glatt(H.d_felt, *SK.TONE_FELT)
    return np.minimum(mål / np.maximum(tone, 1e-3), SK.H_MAX)
