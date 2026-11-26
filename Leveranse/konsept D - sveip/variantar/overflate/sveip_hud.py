# -*- coding: utf-8 -*-
"""sveip_hud.py: overflatestudiar på Sveip som ekte geometri.

Ytterhuda på Sveip er éi utbrettbar plate. Her er ho bretta ut til eit rutenett (s, z):
s er boglengda rundt stadionforma (0 i nasen, framsida først), z er høgda. Ein variant er
ein funksjon felt(G) som gjev høgda h(s, z) i mm ut frå plata, pluss tone og ruheit.
Kjernen byggjer nettet, legg det utanpå CAD-kroppen (D01) og rendrar med fast kamera og
lys på heilt svart bakgrunn (#000). Forma er altså den same i alle variantar.

Køyr frå overflate/:
  python sveip_hud.py v1_plate            (full kvalitet, 1536 x 1536)
  python sveip_hud.py v1_plate --prove    (rask prøve, 640 x 640, grovare nett)
Les   ../V0-basis/render/geometri.json og STL-ane (lag dei med sveip_produksjon.py --rask i V0-basis/cad)
Skriv bilete/<variant>.png  (eller bilete/<variant>_prove.png)

Ein variant er ei fil <namn>.py i denne mappa med:
  def felt(G): return dict(h=..., tone=..., rough=..., mat={...}, knapp_nivaa=...)
    h      høgd i mm ut frå plata, same form som G.S. Nullnivået for huda er H0 (0,3 mm).
    tone   (valfri) lysleik, om lag 0,8 til 1,1
    rough  (valfri) ruheit 0 til 1
    mat    (valfri) dict: farge (r, g, b) sRGB, metal 0..1, rough, sky (skydekt variasjon 0..1),
           strok (slipestrok langs s, 0..1), vev (vev i duk, 0..1), floyel (sheen for duk, 0..1)
    knapp_nivaa (valfri) nivået huda har rundt messingknappen (standard H0)
    mikrobit (valfri) 5 x 5 lysstyrkar 0 til 9, øvste rad først: då får stamma eit forsenka felt
           med 25 hol der LED-matrisa på ein micro:bit V2 syner (--naer gjev nærbilete av betjeninga)

Nedskalert variant (V12 Mini): varianten kallar oppsett(skala, mikrobit, knapp, ...) før han
importerer mønstermodulane. Modellen held måla til rev. B, så biletet viser same form, medan
micro:bit, hol og messingpunkt blir større i høve til lampa.

Faste reglar for familien: naglar r 0,9 og h 0,28 mm, 4,5 mm frå saum og kant (A).
"""
from __future__ import annotations

import importlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

HER = Path(__file__).resolve().parent
BASIS = HER.parent / "V0-basis"

# ---------------------------------------------------------------- mål frå CAD (mm), rev. B
S_, D_, R_ = 300.0, 105.0, 52.5
Z_SKJERM, X_STAMME, R_INN = 167.5, 178.0, 12.0
X_HAKK, Z_HAKK, R_HAKK = 45.5, 61.0, 7.0
PKT_X, PKT_Z = 165.0, 70.0
R_KNAPP = 6.3                   # messingknappen, Ø 12,6
BUE = math.pi * R_ / 2          # kvartboge i nasen: 82,47
FLAT = S_ - 2 * R_              # flat side: 195
P_ = 2 * FLAT + 2 * math.pi * R_  # omkrins: 719,87
H0 = 0.3                        # nullnivå for huda over CAD-flata
A = 4.5                         # naglerekkja står 4,5 mm frå saum og kant
NAGLE_R, NAGLE_H = 0.9, 0.28
S_FRAMME = (BUE, BUE + FLAT)                      # s-området til den flate framsida
S_VENSTRE = (BUE + FLAT, BUE + FLAT + math.pi * R_)  # venstre halvsylinder
S_BAK = (BUE + FLAT + math.pi * R_, P_ - BUE)     # flat bakside
S_KNAPP_F = BUE + (S_ - R_ - PKT_X)               # knappen framme: s = 164,97
S_KNAPP_B = P_ - S_KNAPP_F                        # knappen bak
S_STAMME_F = BUE + (S_ - R_ - X_STAMME)           # høgre kant av stamma, framme: s = 151,97
S_STAMME_B = P_ - S_STAMME_F                      # same, bak
S_HAKK_F = S_VENSTRE[0] + R_ * math.asin((R_ - X_HAKK) / R_)   # der hakkanten skjer venstre boge, framme
S_HAKK_B = P_ - S_HAKK_F
S_TOPPUNKT = P_ / 2                               # toppunktet på venstre boge (x = 0)

# micro:bit V2 bak framveggen på stamma: berre LED-matrisa på 5 x 5 syner, gjennom 25 hol.
# Matrisa står i same høgd som messingknappen og midt på stamma, flytta 2,5 mm til den fjerde
# dragaren i sveipfeltet (x = 117,77), slik knappen står på den første.
MB_X, MB_Z = 117.77, PKT_Z                        # sentrum av matrisa (midtre LED)
MB_S = BUE + (S_ - R_ - MB_X)
MB_PX, MB_PZ = 4.0, 4.0                           # avstand mellom LED-ane, vassrett og loddrett
MB_HOL_R = 1.0                                    # hol Ø 2,0 i plata, med lysleiar bak
# Same grep som rundt messingknappen: ei grunn forsenking, og mønsteret viker med same luft.
# Avstandane er målte frå firkanten gjennom dei ytste LED-sentera (holkanten ligg på 1,0).
MB_FELT, MB_FELT_DJUPN = 3.5, 0.12                # forsenka felt 23 x 23 mm, hjørneradius 3,5
MB_FELT_UT = (0.0, 0.0)                           # feltet kan gå lenger mot høgre og opp, så det rommar messingpunktet
RAMPE = 0.15                                      # mønsteret stig høgst 0,15 mm per mm ut frå betjeninga,
MB_RAMPE_FRA = 5.5                                # frå 2 mm utanfor feltet (og 2 mm utanfor knappefeltet)
MB_LYS = 3.2                                      # utstråling midt i ein propp ved lysstyrke 9

# Nedskalerte variantar. Modellen held alltid måla til rev. B (300 mm). SKALA er storleiken på
# den verkelege lampa i høve til det, og alt som har fast storleik i røynda (micro:bit, hol,
# messingpunkt) blir rekna om til modelleiningar med mm().
SKALA = 1.0
HAKK = True                                       # hakket for pluggen nede i nasen
KNAPP_BAK = True                                  # messingknapp òg på baksida
UTAN = ()                                         # CAD-delar som ikkje skal med i biletet


def mm(x):
    """Verkelege mm til modelleiningar."""
    return x / SKALA


def oppsett(skala, mikrobit, knapp, knapp_bak=True, hakk=True, utan=(), felt_ut=(0.0, 0.0)):
    """Set opp ein nedskalert variant. mikrobit = (x, z) for midtre LED og knapp = (x, z, radius),
    alt i verkelege mm på den nedskalerte lampa. felt_ut = kor mange mm det forsenka feltet går
    lenger mot høgre og opp enn matrisa. Skal kallast før Gitter blir laga og før mønstermodulane
    (straum, luftskip) blir importerte, sidan dei les måla ved import."""
    global SKALA, HAKK, KNAPP_BAK, UTAN, H0, PKT_X, PKT_Z, R_KNAPP, S_KNAPP_F, S_KNAPP_B
    global MB_X, MB_Z, MB_S, MB_PX, MB_PZ, MB_HOL_R, MB_FELT, MB_FELT_DJUPN, MB_RAMPE_FRA, MB_FELT_UT
    f = SKALA / skala                             # frå gamle til nye modelleiningar
    SKALA, HAKK, KNAPP_BAK, UTAN = skala, hakk, knapp_bak, tuple(utan)
    H0 *= f
    MB_PX, MB_PZ, MB_HOL_R = MB_PX * f, MB_PZ * f, MB_HOL_R * f
    MB_FELT, MB_FELT_DJUPN, MB_RAMPE_FRA = MB_FELT * f, MB_FELT_DJUPN * f, MB_RAMPE_FRA * f
    MB_FELT_UT = (mm(felt_ut[0]), mm(felt_ut[1]))
    MB_X, MB_Z = mm(mikrobit[0]), mm(mikrobit[1])
    MB_S = BUE + (S_ - R_ - MB_X)
    PKT_X, PKT_Z, R_KNAPP = mm(knapp[0]), mm(knapp[1]), mm(knapp[2])
    S_KNAPP_F = BUE + (S_ - R_ - PKT_X)
    S_KNAPP_B = P_ - S_KNAPP_F


def plan(s):
    """Punkt (x, y), normal (nx, ny) og flatenummer for boglengda s rundt stadionforma.
    Flater: 0 nase framme, 1 framside, 2 venstre boge, 3 bakside, 4 nase bak."""
    s = np.asarray(s, dtype=np.float64) % P_
    x = np.empty_like(s)
    y = np.empty_like(s)
    nx = np.empty_like(s)
    ny = np.empty_like(s)
    fl = np.empty(s.shape, dtype=np.int8)
    a = s < BUE
    th = -s[a] / R_
    x[a], y[a], nx[a], ny[a], fl[a] = S_ - R_ + R_ * np.cos(th), R_ * np.sin(th), np.cos(th), np.sin(th), 0
    b = (s >= BUE) & (s < BUE + FLAT)
    x[b], y[b], nx[b], ny[b], fl[b] = S_ - R_ - (s[b] - BUE), -R_, 0.0, -1.0, 1
    c = (s >= S_VENSTRE[0]) & (s < S_VENSTRE[1])
    th = -math.pi / 2 - (s[c] - S_VENSTRE[0]) / R_
    x[c], y[c], nx[c], ny[c], fl[c] = R_ + R_ * np.cos(th), R_ * np.sin(th), np.cos(th), np.sin(th), 2
    d = (s >= S_BAK[0]) & (s < S_BAK[1])
    x[d], y[d], nx[d], ny[d], fl[d] = R_ + (s[d] - S_BAK[0]), R_, 0.0, 1.0, 3
    e = s >= S_BAK[1]
    th = math.pi / 2 - (s[e] - S_BAK[1]) / R_
    x[e], y[e], nx[e], ny[e], fl[e] = S_ - R_ + R_ * np.cos(th), R_ * np.sin(th), np.cos(th), np.sin(th), 4
    return x, y, nx, ny, fl


def glatt(x, a, b):
    """Mjukt steg frå 0 (x <= a) til 1 (x >= b). a > b gjev fallande steg."""
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def kuppel(d, r, h):
    """Kulekalott med radius r og høgd h, som funksjon av avstanden d frå sentrum."""
    return h * np.sqrt(np.clip(1 - (d / r) ** 2, 0.0, 1.0))


def spegl(s):
    """Same punkt på baksida (spegla om nasen)."""
    return (P_ - s) % P_


class Gitter:
    """Utbretta hud. Alle felt har form (ns, nz + 1): akse 0 er s (lukka, går rundt), akse 1 er z."""

    def __init__(self, steg=0.25):
        self.steg = steg
        self.ns = int(round(P_ / steg))
        self.nz = int(round(S_ / steg))
        self.ds = P_ / self.ns
        self.dz = S_ / self.nz
        self.s = np.arange(self.ns) * self.ds
        self.z = np.arange(self.nz + 1) * self.dz
        self.S, self.Z = np.meshgrid(self.s, self.z, indexing="ij")
        x, y, nx, ny, fl = plan(self.s)
        self.x1, self.y1, self.nx1, self.ny1 = x, y, nx, ny
        self.X = np.repeat(x[:, None], self.nz + 1, axis=1)       # verdskoordinat x for kvart punkt
        self.flate = np.repeat(fl[:, None], self.nz + 1, axis=1)
        self.krum = (self.flate != 1) & (self.flate != 3)          # sant på dei krumme partia
        self.fast = self._fast(self.X, self.Z)                     # sant der det er plate
        self.kant = self.avstand_til(self.fast)                    # mm til næraste frie kant
        self.d_knapp = np.hypot(self.avst_s(S_KNAPP_F), self.Z - PKT_Z)
        if KNAPP_BAK:
            self.d_knapp = np.minimum(self.d_knapp, np.hypot(self.avst_s(S_KNAPP_B), self.Z - PKT_Z))

    @staticmethod
    def _fast(X, Z):
        ut = (X > X_STAMME) & (Z < Z_SKJERM)
        hj = (X < X_STAMME + R_INN) & (Z > Z_SKJERM - R_INN) & \
             (np.hypot(X - (X_STAMME + R_INN), Z - (Z_SKJERM - R_INN)) > R_INN)
        ut &= ~hj
        hk = (X < X_HAKK) & (Z < Z_HAKK) & HAKK
        hh = (X > X_HAKK - R_HAKK) & (Z > Z_HAKK - R_HAKK) & \
             (np.hypot(X - (X_HAKK - R_HAKK), Z - (Z_HAKK - R_HAKK)) > R_HAKK)
        hk &= ~hh
        return ~(ut | hk)

    # ------------------------------------------------------------ avstandar
    def avst_s(self, s0):
        """Avstand langs s til s0, rekna rundt (mm)."""
        return np.abs(((self.S - s0 + P_ / 2) % P_) - P_ / 2)

    def avstand_til(self, maske, rekkjevidd=90.0):
        """Avstand (mm) frå kvart punkt i maska til næraste punkt utanfor, rekna rundt i s.
        Utanfor z-området tel som utanfor maska."""
        pad = int(rekkjevidd / self.steg)
        m = np.concatenate([maske[-pad:], maske, maske[:pad]], axis=0)
        m = np.pad(m, ((0, 0), (1, 1)), constant_values=False)
        d = ndimage.distance_transform_edt(m) * self.steg - 0.5 * self.steg
        return np.maximum(d[pad:-pad, 1:-1], 0.0)

    def sla_opp(self, felt, s, z):
        """Verdien av eit felt i vilkårlege punkt (s, z): næraste rutenettpunkt."""
        i = np.rint(np.asarray(s) / self.ds).astype(int) % self.ns
        j = np.clip(np.rint(np.asarray(z) / self.dz).astype(int), 0, self.nz)
        return felt[i, j]

    def mellom_s(self, s_fra, s_til):
        """Sant for s frå s_fra til s_til i aukande retning (går rundt om s_til < s_fra)."""
        return ((self.S - s_fra) % P_) <= ((s_til - s_fra) % P_)

    # ------------------------------------------------------------ saumar og panel
    def linje_z(self, z0, s_fra=None, s_til=None):
        """Vassrett saumline i høgda z0 (éi rad), valfritt berre frå s_fra til s_til."""
        m = np.zeros(self.S.shape, dtype=bool)
        m[:, int(round(z0 / self.dz))] = True
        if s_fra is not None:
            m &= self.mellom_s(s_fra, s_til)
        return m

    def linje_s(self, s0, z_fra=0.0, z_til=S_):
        """Loddrett saumline ved s0 (éi kolonne) frå z_fra til z_til."""
        m = np.zeros(self.S.shape, dtype=bool)
        m[int(round((s0 % P_) / self.ds)) % self.ns, :] = True
        return m & (self.Z >= z_fra - 1e-9) & (self.Z <= z_til + 1e-9)

    def linje(self, p0, p1):
        """Saumline mellom to punkt (s, z), rett line i den utbretta plata (ikkje over s = 0)."""
        (s0, z0), (s1, z1) = p0, p1
        L2 = (s1 - s0) ** 2 + (z1 - z0) ** 2
        t = np.clip(((self.S - s0) * (s1 - s0) + (self.Z - z0) * (z1 - z0)) / L2, 0, 1)
        return np.hypot(self.S - (s0 + t * (s1 - s0)), self.Z - (z0 + t * (z1 - z0))) < 0.71 * self.steg

    def paneler(self, saum):
        """Nummer per panel: samanhengande plate mellom saumliner og frie kantar. Saumpunkta
        får nummeret til næraste panel. Returnerer (nummer, tal på panel)."""
        fri = self.fast & ~saum
        lab, n = ndimage.label(fri)
        far = list(range(n + 1))

        def rot(a):
            while far[a] != a:
                far[a] = far[far[a]]
                a = far[a]
            return a
        for a, b in set(zip(lab[-1, :].tolist(), lab[0, :].tolist())):   # skøyt rundt s
            if a and b and rot(a) != rot(b):
                far[rot(a)] = rot(b)
        rotar = np.array([rot(a) for a in range(n + 1)])
        _, tett = np.unique(rotar, return_inverse=True)
        lab = tett[lab]
        null = tett[0]
        idx = ndimage.distance_transform_edt(lab == null, return_distances=False, return_indices=True)
        lab = lab[tuple(idx)]
        return lab, int(lab.max()) + 1

    def tone_per_panel(self, ids, spreiing=0.06, fro=1):
        """Ein tilfeldig lysleik per panel-id, 1 +- spreiing."""
        rng = np.random.default_rng(fro)
        tab = 1 + spreiing * rng.uniform(-1, 1, int(ids.max()) + 1)
        return tab[ids]

    # ------------------------------------------------------------ naglar
    def kontur_punkt(self, maske, a=A, deling=10.5, tvang=(), vinkel=38.0):
        """Naglepunkt i avstanden a innanfor randa på maska. Kvar lukka kontur blir delt i
        hjørna (og i tvangspunkta), og kvart stykke får jamn deling nærast `deling`.
        Hjørnenaglen er felles for dei to rekkjene som møtest. Returnerer (n, 2) med (s, z)."""
        import contourpy
        d = self.avstand_til(maske)
        d3 = np.concatenate([d, d, d], axis=0)
        s3 = np.arange(3 * self.ns) * self.ds
        liner = contourpy.contour_generator(x=s3, y=self.z, z=d3.T).lines(a)
        steg = 0.25
        ut = []
        for ln in liner:
            if len(ln) < 8:
                continue
            lukka = np.allclose(ln[0], ln[-1], atol=1e-6)
            if lukka:
                if not (P_ <= ln[:, 0].mean() < 2 * P_):
                    continue
                pts, skift = ln[:-1], 0.0
            else:   # går rundt heile forma: skjer ut éin periode
                i0 = int(np.argmax(ln[:, 0] >= P_)) if ln[0, 0] < ln[-1, 0] else int(np.argmax(ln[:, 0] <= 2 * P_))
                mål = ln[i0] + (P_ if ln[0, 0] < ln[-1, 0] else -P_) * np.array([1.0, 0.0])
                kand = np.where(np.hypot(*(ln[i0 + 10:] - mål).T) < 0.6)[0]
                if not len(kand):
                    continue
                i1 = i0 + 10 + int(kand[0])
                pts, skift = ln[i0:i1], float(mål[0] - ln[i0, 0])
            # jamn omsampling langs boglengda
            lukk = np.vstack([pts, pts[:1] + [skift, 0.0]])
            L = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(lukk, axis=0).T))])
            M = max(8, int(round(L[-1] / steg)))
            t = np.arange(M) * L[-1] / M
            q = np.stack([np.interp(t, L, lukk[:, 0]), np.interp(t, L, lukk[:, 1])], axis=1)
            ext = np.vstack([q - [skift, 0.0], q, q + [skift, 0.0]])
            w = max(2, int(round(1.5 / (L[-1] / M))))
            i = np.arange(M) + M
            t1 = ext[i] - ext[i - w]
            t2 = ext[i + w] - ext[i]
            sving = np.degrees(np.abs(np.arctan2(t1[:, 0] * t2[:, 1] - t1[:, 1] * t2[:, 0],
                                                 (t1 * t2).sum(1))))
            brot = set()
            kandidat = np.where(sving > vinkel)[0]
            for k in kandidat:   # lokalt maksimum innanfor +-3 mm
                nab = (np.arange(k - 2 * w, k + 2 * w + 1)) % M
                if sving[k] >= sving[nab].max() - 1e-9 and not any(((k - b) % M) < 2 * w or ((b - k) % M) < 2 * w
                                                                    for b in brot):
                    brot.add(int(k))
            for ts, tz in tvang:
                dd = np.hypot(((q[:, 0] - (ts % P_) - P_ + P_ / 2) % P_) - P_ / 2, q[:, 1] - tz)
                if dd.min() < 3.0:
                    brot.add(int(dd.argmin()))
            brot = sorted(brot)
            if not brot:
                n = max(1, int(round(L[-1] / deling)))
                idx = (np.arange(n) * M / n).astype(int)
            else:
                idx = []
                for b0, b1 in zip(brot, brot[1:] + [brot[0] + M]):
                    lengd = (b1 - b0) * L[-1] / M
                    n = max(1, int(round(lengd / deling)))
                    idx.extend(int(round(b0 + k * (b1 - b0) / n)) % M for k in range(n))
                idx = np.array(sorted(set(idx)))
            ut.append(q[idx])
        if not ut:
            return np.zeros((0, 2))
        pkt = np.vstack(ut)
        pkt[:, 0] %= P_
        return pkt

    def stempel(self, pkt, r=NAGLE_R, h=NAGLE_H, form="kuppel"):
        """Høgdefelt med éin nagle (kulekalott) i kvart punkt. form='grop' gjev ei mjuk skål."""
        ut = np.zeros_like(self.S)
        w = int(math.ceil(r / self.steg)) + 1
        for s0, z0 in pkt:
            i0 = int(round(s0 / self.ds))
            j0 = int(round(z0 / self.dz))
            ii = np.arange(i0 - w, i0 + w + 1) % self.ns
            jj = np.arange(max(0, j0 - w), min(self.nz, j0 + w) + 1)
            dss = ((self.s[ii] - s0 + P_ / 2) % P_) - P_ / 2
            d = np.hypot(dss[:, None], (self.z[jj] - z0)[None, :])
            blk = kuppel(d, r, h) if form == "kuppel" else h * np.clip(1 - (d / r) ** 2, 0, 1) ** 2
            ut[np.ix_(ii, jj)] = np.maximum(ut[np.ix_(ii, jj)], blk)
        return ut

    def utan_knapp(self, pkt, radius=11.5):
        """Fjern punkt nærare knappen enn radius."""
        d = np.minimum(np.hypot(((pkt[:, 0] - S_KNAPP_F + P_ / 2) % P_) - P_ / 2, pkt[:, 1] - PKT_Z),
                       np.hypot(((pkt[:, 0] - S_KNAPP_B + P_ / 2) % P_) - P_ / 2, pkt[:, 1] - PKT_Z))
        return pkt[d >= radius]

    def naglar_z(self, z0, deling=12.0, r=NAGLE_R, h=NAGLE_H, fase=0.0, s_fra=None, s_til=None):
        """Ei vassrett naglerekkje i høgda z0, jamn deling rundt heile forma (delinga blir retta
        så ho går opp i omkrinsen). s_fra/s_til avgrensar rekkja til eit s-område."""
        n = max(1, round(P_ / deling))
        d = P_ / n
        u = ((self.S - fase + d / 2) % d) - d / 2
        ut = kuppel(np.hypot(u, self.Z - z0), r, h)
        if s_fra is not None:
            ut = ut * self.mellom_s(s_fra, s_til)
        return ut

    # ------------------------------------------------------------ støy
    def stoy(self, skala=30.0, fro=1):
        """Mjuk støy med storleik om lag `skala` mm, verdiar om lag -1 til 1, saumlaus rundt s."""
        rng = np.random.default_rng(fro)
        f = max(1, int(round(skala / self.steg / 6)))
        a = rng.standard_normal((self.ns // f + 1, self.nz // f + 2))
        a = ndimage.gaussian_filter(a, 1.6, mode=("wrap", "nearest"))
        a = ndimage.zoom(a, (self.ns / a.shape[0], (self.nz + 1) / a.shape[1]), order=1, mode="grid-wrap")
        a = a[:self.ns, :self.nz + 1]
        return a / (np.abs(a).max() + 1e-9)

    def strok(self, lengd=120.0, breidd=1.0, fro=2):
        """Lange strok langs s (valse- og sliperetninga), standardavvik om lag 1/3."""
        rng = np.random.default_rng(fro)
        a = rng.standard_normal(self.S.shape)
        a = ndimage.gaussian_filter(a, (lengd / self.steg, breidd / self.steg), mode=("wrap", "nearest"))
        return a / (3 * a.std() + 1e-9)


# ---------------------------------------------------------------- nett


def mjukmin(a, b, e=0.04):
    """Den minste av a og b, med ein mjuk overgang på om lag e mm i staden for ein knekk."""
    return 0.5 * (a + b - np.sqrt((a - b) ** 2 + e * e))


def lag_nett(G, h, sirklar=()):
    """Punkt, firkantar og uv for huda, med kantstriper ned til CAD-flata langs alle frie kantar.
    sirklar = [(s0, z0, r), ...] gjev runde hol: rutene innanfor blir tekne ut, og punkta på
    randa blir flytte inn på sirkelen, så holet blir rundt og ikkje hakkete."""
    ns, nz = G.ns, G.nz
    h = np.where(G.fast, h, 0.0)
    hol = G.d_knapp < R_KNAPP + mm(0.25)
    dS = np.zeros(G.S.shape)
    dZ = np.zeros(G.S.shape)
    for s0, z0, r in sirklar:
        w = int(r / G.steg) + 3
        i0, j0 = int(round(s0 / G.ds)), int(round(z0 / G.dz))
        ii = np.arange(i0 - w, i0 + w + 1) % ns
        jj = np.arange(j0 - w, j0 + w + 1)
        us = (((G.s[ii] - s0 + P_ / 2) % P_) - P_ / 2)[:, None] * np.ones((1, jj.size))
        uz = np.ones((ii.size, 1)) * (G.z[jj] - z0)[None, :]
        d = np.hypot(us, uz)
        inne = d < r
        rand = ndimage.binary_dilation(inne, np.ones((3, 3), bool)) & ~inne
        f = np.where(rand, r / np.maximum(d, 1e-9) - 1.0, 0.0)
        ix = np.ix_(ii, jj)
        hol[ix] |= inne
        dS[ix] += us * f
        dZ[ix] += uz * f
    tx = (np.roll(G.x1, -1) - np.roll(G.x1, 1)) / (2 * G.ds)      # tangenten langs s
    ty = (np.roll(G.y1, -1) - np.roll(G.y1, 1)) / (2 * G.ds)
    px = G.x1[:, None] + G.nx1[:, None] * h + tx[:, None] * dS
    py = G.y1[:, None] + G.ny1[:, None] * h + ty[:, None] * dS
    pz = G.Z + dZ
    ok = G.fast & ~hol
    i1 = (np.arange(ns) + 1) % ns
    q = ok[:, :-1] & ok[i1][:, :-1] & ok[:, 1:] & ok[i1][:, 1:]
    idx = np.arange(ns * (nz + 1)).reshape(ns, nz + 1)
    a = idx[:, :-1][q]
    b = idx[i1][:, :-1][q]
    c = idx[i1][:, 1:][q]
    d = idx[:, 1:][q]
    quads = np.stack([a, d, c, b], axis=1)        # normalen peikar ut
    kanter = []
    qq = np.pad(q, ((0, 0), (1, 1)), constant_values=False)
    opp = q & ~qq[:, 2:]
    ned = q & ~qq[:, :-2]
    kanter.append((idx[:, 1:][opp], idx[i1][:, 1:][opp]))
    kanter.append((idx[i1][:, :-1][ned], idx[:, :-1][ned]))
    hog = q & ~np.roll(q, -1, axis=0)
    ven = q & ~np.roll(q, 1, axis=0)
    kanter.append((idx[i1][:, 1:][hog], idx[i1][:, :-1][hog]))
    kanter.append((idx[:, :-1][ven], idx[:, 1:][ven]))
    ka = np.concatenate([k[0] for k in kanter])
    kb = np.concatenate([k[1] for k in kanter])
    V = np.stack([px.ravel(), py.ravel(), pz.ravel()], axis=1)
    nxf = np.repeat(G.nx1[:, None], nz + 1, axis=1).ravel()
    nyf = np.repeat(G.ny1[:, None], nz + 1, axis=1).ravel()
    bx = (G.x1[:, None] + tx[:, None] * dS).ravel()
    by = (G.y1[:, None] + ty[:, None] * dS).ravel()
    inn = 0.05                                    # stripa går 0,05 mm inn i CAD-flata
    B = np.stack([bx - inn * nxf, by - inn * nyf, pz.ravel()], axis=1)
    brukt = np.unique(np.concatenate([quads.ravel(), ka, kb]))
    kart = -np.ones(V.shape[0], dtype=np.int64)
    kart[brukt] = np.arange(brukt.size)
    kb_ids = np.unique(np.concatenate([ka, kb]))
    kart_b = -np.ones(V.shape[0], dtype=np.int64)
    kart_b[kb_ids] = brukt.size + np.arange(kb_ids.size)
    verts = np.concatenate([V[brukt], B[kb_ids]])
    quads2 = kart[quads]
    striper = np.stack([kart[ka], kart[kb], kart_b[kb], kart_b[ka]], axis=1)
    uv = np.stack([(G.S + dS).ravel(), pz.ravel()], axis=1) / 1000.0
    uvv = np.concatenate([uv[brukt], uv[kb_ids]])
    return verts, quads2, striper, uvv, brukt, kb_ids


def knapp_nett(nivaa, side):
    """Dreia messingknapp: Ø 12,6, 0,45 mm fas og svak kuppel. side = -1 framme, +1 bak."""
    f = R_KNAPP / 6.3                             # same profil for alle storleikar
    prof = [(0.0, 1.05 * f), (2.5 * f, 1.02 * f), (4.5 * f, 0.93 * f), (R_KNAPP - 0.45 * f, 0.80 * f),
            (R_KNAPP, 0.35 * f), (R_KNAPP, -1.0)]
    n = 72
    v, f = [], []
    for r, t in prof:
        for k in range(n):
            a = 2 * math.pi * k / n
            v.append((PKT_X + r * math.cos(a), side * (R_ + nivaa + t), PKT_Z + r * math.sin(a)))
    for i in range(len(prof) - 1):
        for k in range(n):
            k1 = (k + 1) % n
            f.append((i * n + k, i * n + k1, (i + 1) * n + k1, (i + 1) * n + k))
    return np.array(v), np.array(f)


# ---------------------------------------------------------------- Blender


def render(namn, prove=False, ut=None, naer=False):
    import bpy
    from mathutils import Vector

    mod = importlib.import_module(namn)
    G = Gitter(0.5 if prove else 0.25)
    res = mod.felt(G)
    h = np.asarray(res["h"], dtype=np.float64)
    assert h.shape == G.S.shape, f"h har form {h.shape}, skal vere {G.S.shape}"
    assert np.isfinite(h).all(), "h har NaN eller inf"
    # rundt knappen er huda flat: ei grunn forsenking med 1 mm luft rundt messingen
    nivaa = float(res.get("knapp_nivaa", H0))
    k = glatt(G.d_knapp, R_KNAPP + mm(1.0), R_KNAPP + mm(2.2))
    h = (nivaa - mm(0.12)) + (h - (nivaa - mm(0.12))) * k
    # micro:bit: mønsteret viker for matrisa, som står i eit grunt, forsenka felt med 25 hol
    mb = res.get("mikrobit")
    hol_mb = []
    if mb is not None:
        mb = np.asarray(mb, dtype=float)
        assert mb.shape == (5, 5), "mikrobit skal vere 5 x 5 lysstyrkar (0 til 9), øvste rad først"
        ds_ = ((G.S - MB_S + P_ / 2) % P_) - P_ / 2
        dz_ = G.Z - MB_Z
        sidelengs = np.maximum(-ds_ - 2 * MB_PX - MB_FELT_UT[0], ds_ - 2 * MB_PX)      # mot høgre er minkande s
        loddrett = np.maximum(dz_ - 2 * MB_PZ - MB_FELT_UT[1], -dz_ - 2 * MB_PZ)
        q = np.hypot(np.clip(sidelengs, 0, None), np.clip(loddrett, 0, None))
        h = mjukmin(h, nivaa + RAMPE * np.clip(q - MB_RAMPE_FRA, 0, None))
        h = h - MB_FELT_DJUPN * (1 - glatt(q, MB_FELT - mm(0.6), MB_FELT))
        hol_mb = [(MB_S - (kol - 2) * MB_PX, MB_Z + (2 - rad) * MB_PZ, MB_HOL_R)
                  for kol in range(5) for rad in range(5)]
    h = np.clip(h, 0.03, 8.0)
    tone = np.asarray(res.get("tone", np.ones_like(h)), dtype=np.float64) * np.ones_like(h)
    rough = res.get("rough")
    m = dict(farge=(0.80, 0.785, 0.76), metal=1.0, rough=0.40, sky=0.2, strok=0.5, vev=0.0, floyel=0.0)
    m.update(res.get("mat", {}))
    rough = (np.full_like(h, m["rough"]) if rough is None else np.asarray(rough, dtype=np.float64) * np.ones_like(h))
    # med matrise er tone og ruheit jamne rundt betjeninga: skiftet mellom to banar og den blanke
    # lina på dragaren skal ikkje gå tvers gjennom knappen eller matrisa
    soner = []
    if mb is not None:
        rk0, rk1 = R_KNAPP + mm(2.2), R_KNAPP + mm(8.2)
        soner = [(G.d_knapp, rk0, rk1, G.S < P_ / 2), (G.d_knapp, rk0, rk1, G.S >= P_ / 2),
                 (q, MB_FELT, MB_RAMPE_FRA + mm(3.0), True)]
    for d_, r0, r1, side in soner:
        inne = (d_ < r1) & side & G.fast
        w = glatt(d_, r0, r1)
        tone = np.where(inne, tone[inne].mean() + (tone - tone[inne].mean()) * w, tone)
        rough = np.where(inne, rough[inne].mean() + (rough - rough[inne].mean()) * w, rough)
    verts, quads, striper, uv, brukt, kb_ids = lag_nett(G, h, hol_mb)
    tone_v = np.concatenate([tone.ravel()[brukt], tone.ravel()[kb_ids]])
    rough_v = np.concatenate([rough.ravel()[brukt], rough.ravel()[kb_ids]])
    print(f"nett: {verts.shape[0]} punkt, {quads.shape[0]} + {striper.shape[0]} flater, "
          f"h {h[G.fast].min():.2f} til {h[G.fast].max():.2f} mm")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.render.threads_mode = "FIXED"
    sc.render.threads = 4
    sc.cycles.use_denoising = True
    sc.cycles.adaptive_threshold = 0.012
    sc.cycles.samples = 64 if prove else 400
    sc.cycles.max_bounces = 8
    sc.render.resolution_x = sc.render.resolution_y = 1536
    sc.render.resolution_percentage = 42 if prove else 100
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass

    def lin(c):
        return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)

    def enkel(nm, farge, rough_=0.5, metal=0.0, aniso=0.0):
        mt = bpy.data.materials.new(nm)
        mt.use_nodes = True
        bs = mt.node_tree.nodes.get("Principled BSDF")
        bs.inputs["Base Color"].default_value = (*lin(farge), 1.0)
        bs.inputs["Roughness"].default_value = rough_
        bs.inputs["Metallic"].default_value = metal
        if aniso:
            bs.inputs["Anisotropic"].default_value = aniso
        return mt

    def nett_objekt(nm, v, f, glatt_=True):
        me = bpy.data.meshes.new(nm)
        nf = f.shape[0]
        me.vertices.add(v.shape[0])
        me.vertices.foreach_set("co", (v / 1000.0).astype(np.float32).ravel())
        me.loops.add(nf * 4)
        me.loops.foreach_set("vertex_index", f.astype(np.int32).ravel())
        me.polygons.add(nf)
        me.polygons.foreach_set("loop_start", np.arange(0, nf * 4, 4, dtype=np.int32))
        me.polygons.foreach_set("loop_total", np.full(nf, 4, dtype=np.int32))
        me.polygons.foreach_set("use_smooth", np.full(nf, glatt_, dtype=bool))
        me.update(calc_edges=True)
        ob = bpy.data.objects.new(nm, me)
        sc.collection.objects.link(ob)
        return ob, me

    # ---- huda
    alle = np.concatenate([quads, striper]).astype(np.int32)
    ob, me = nett_objekt("hud", verts, alle)
    uvl = me.uv_layers.new(name="UVMap")
    uvl.data.foreach_set("uv", uv[alle.ravel()].astype(np.float32).ravel())
    at = me.attributes.new("tone", "FLOAT", "POINT")
    at.data.foreach_set("value", tone_v.astype(np.float32))
    ar = me.attributes.new("ruheit", "FLOAT", "POINT")
    ar.data.foreach_set("value", rough_v.astype(np.float32))

    mt = bpy.data.materials.new("hud")
    mt.use_nodes = True
    nt = mt.node_tree
    bs = nt.nodes.get("Principled BSDF")
    bs.inputs["Metallic"].default_value = m["metal"]
    try:
        bs.inputs["Sheen Weight"].default_value = m["floyel"]
        bs.inputs["Sheen Roughness"].default_value = 0.5
    except Exception:
        pass
    a_t = nt.nodes.new("ShaderNodeAttribute")
    a_t.attribute_name = "tone"
    a_r = nt.nodes.new("ShaderNodeAttribute")
    a_r.attribute_name = "ruheit"
    uvn = nt.nodes.new("ShaderNodeUVMap")

    def stoy_node(skala_xy, detalj=4.0):
        kart_ = nt.nodes.new("ShaderNodeMapping")
        kart_.inputs["Scale"].default_value = (skala_xy[0], skala_xy[1], 1.0)
        nt.links.new(uvn.outputs["UV"], kart_.inputs["Vector"])
        st = nt.nodes.new("ShaderNodeTexNoise")
        st.inputs["Scale"].default_value = 1.0
        st.inputs["Detail"].default_value = detalj
        st.inputs["Roughness"].default_value = 0.6
        nt.links.new(kart_.outputs["Vector"], st.inputs["Vector"])
        return st

    def omfang(node, lo, hi):
        k_ = nt.nodes.new("ShaderNodeMapRange")
        k_.inputs["From Min"].default_value = 0.3
        k_.inputs["From Max"].default_value = 0.7
        k_.inputs["To Min"].default_value = lo
        k_.inputs["To Max"].default_value = hi
        nt.links.new(node.outputs["Fac"], k_.inputs["Value"])
        return k_

    def rekn(op, x, y):
        n_ = nt.nodes.new("ShaderNodeMath")
        n_.operation = op
        for inn_, v in zip(n_.inputs, (x, y)):
            if isinstance(v, (int, float)):
                inn_.default_value = v
            else:
                nt.links.new(v, inn_)
        return n_.outputs["Value"]

    sky = stoy_node((16.0, 16.0), 5.0)                 # mjuke felt, om lag 60 mm
    strok = stoy_node((9.0, 900.0), 3.0)               # slipestrok langs s: lange og 1 mm smale
    korn = stoy_node((2600.0, 2600.0), 2.0)            # fint korn, under 0,5 mm
    lys = rekn("MULTIPLY", a_t.outputs["Fac"], omfang(sky, 1 - 0.10 * m["sky"], 1 + 0.07 * m["sky"]).outputs["Result"])
    lys = rekn("MULTIPLY", lys, omfang(strok, 1 - 0.05 * m["strok"], 1 + 0.05 * m["strok"]).outputs["Result"])
    lys = rekn("MULTIPLY", lys, omfang(korn, 0.985, 1.015).outputs["Result"])
    farge = nt.nodes.new("ShaderNodeMixRGB")
    farge.blend_type = "MULTIPLY"
    farge.inputs["Fac"].default_value = 1.0
    farge.inputs["Color1"].default_value = (*lin(m["farge"]), 1.0)
    nt.links.new(lys, farge.inputs["Color2"])
    nt.links.new(farge.outputs["Color"], bs.inputs["Base Color"])
    ru = rekn("ADD", a_r.outputs["Fac"], omfang(sky, -0.05 * m["sky"], 0.05 * m["sky"]).outputs["Result"])
    ru = rekn("ADD", ru, omfang(strok, -0.07 * m["strok"], 0.07 * m["strok"]).outputs["Result"])
    ru = rekn("ADD", ru, omfang(korn, -0.02, 0.02).outputs["Result"])
    kl = nt.nodes.new("ShaderNodeClamp")
    nt.links.new(ru, kl.inputs["Value"])
    nt.links.new(kl.outputs["Result"], bs.inputs["Roughness"])
    if m["vev"] > 0:   # lerretsvev som svak bump: 0,35 mm trådavstand, viser seg først i nærbilete
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.3 * m["vev"]
        bump.inputs["Distance"].default_value = 0.00012
        w = []
        for retn in ("X", "Y"):
            wv = nt.nodes.new("ShaderNodeTexWave")
            wv.wave_type = "BANDS"
            wv.bands_direction = retn
            wv.inputs["Scale"].default_value = 0.31416 / 0.00035
            wv.inputs["Distortion"].default_value = 0.6
            wv.inputs["Detail"].default_value = 1.0
            nt.links.new(uvn.outputs["UV"], wv.inputs["Vector"])
            w.append(wv)
        nt.links.new(rekn("MAXIMUM", w[0].outputs["Fac"], w[1].outputs["Fac"]), bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    me.materials.append(mt)

    # ---- messingknappen (dreia, med fas), framme og bak
    messing = enkel("messing", (0.83, 0.67, 0.36), 0.26, 1.0, aniso=0.5)
    for side in ((-1, 1) if KNAPP_BAK else (-1,)):
        kv, kf = knapp_nett(nivaa, side)
        ko, kme = nett_objekt("knapp", kv, kf)
        kme.materials.append(messing)

    # ---- micro:bit: 25 lysleiarar i flukt med plata, raude der LED-en lyser
    if mb is not None:
        mb_mat = {}
        r_led = (MB_HOL_R + mm(0.03)) / 1000.0
        for kol in range(5):
            for rad in range(5):
                nivaa_led = int(round(mb[rad, kol]))
                if nivaa_led not in mb_mat:
                    lm = enkel(f"led{nivaa_led}", (0.05, 0.02, 0.02), 0.9)      # matta propp, mørk når han er av
                    if nivaa_led > 0:                                           # lyser sterkast i midten
                        nt = lm.node_tree
                        bsl = nt.nodes.get("Principled BSDF")
                        bsl.inputs["Emission Color"].default_value = (1.0, 0.005, 0.01, 1.0)
                        kjerne = MB_LYS * (nivaa_led / 9.0) ** 1.6
                        tc = nt.nodes.new("ShaderNodeTexCoord")
                        flat = nt.nodes.new("ShaderNodeVectorMath"); flat.operation = "MULTIPLY"
                        flat.inputs[1].default_value = (1.0, 1.0, 0.0)
                        lengd = nt.nodes.new("ShaderNodeVectorMath"); lengd.operation = "LENGTH"
                        kart = nt.nodes.new("ShaderNodeMapRange"); kart.interpolation_type = "SMOOTHSTEP"
                        for inn, verdi in (("From Min", 0.0), ("From Max", r_led), ("To Min", kjerne), ("To Max", 0.3 * kjerne)):
                            kart.inputs[inn].default_value = verdi
                        nt.links.new(tc.outputs["Object"], flat.inputs[0])
                        nt.links.new(flat.outputs["Vector"], lengd.inputs[0])
                        nt.links.new(lengd.outputs["Value"], kart.inputs["Value"])
                        nt.links.new(kart.outputs["Result"], bsl.inputs["Emission Strength"])
                    mb_mat[nivaa_led] = lm
                y_led = -(R_ + nivaa - MB_FELT_DJUPN - mm(0.10)) + 0.3
                bpy.ops.mesh.primitive_cylinder_add(
                    vertices=32, radius=r_led, depth=0.0006,
                    location=((MB_X + (kol - 2) * MB_PX) / 1000.0, y_led / 1000.0,
                              (MB_Z + (2 - rad) * MB_PZ) / 1000.0),
                    rotation=(math.pi / 2, 0.0, 0.0))
                bpy.context.active_object.data.materials.append(mb_mat[nivaa_led])

    # ---- resten av lampa frå CAD
    geo = json.loads((BASIS / "render" / "geometri.json").read_text(encoding="utf-8"))
    # innsida av plata: lys i skjermen, mørk i stamma, så ein ikkje ser lyse flater gjennom hakket
    inn = enkel("inn", (0.80, 0.78, 0.745), 0.62, 0.0)
    nti = inn.node_tree
    geo_n = nti.nodes.new("ShaderNodeNewGeometry")
    sep = nti.nodes.new("ShaderNodeSeparateXYZ")
    nti.links.new(geo_n.outputs["Position"], sep.inputs["Vector"])
    steg_n = nti.nodes.new("ShaderNodeMapRange")
    steg_n.inputs["From Min"].default_value = (Z_SKJERM - 2.0) / 1000.0
    steg_n.inputs["From Max"].default_value = (Z_SKJERM + 2.0) / 1000.0
    nti.links.new(sep.outputs["Z"], steg_n.inputs["Value"])
    bl = nti.nodes.new("ShaderNodeMixRGB")
    bl.inputs["Color1"].default_value = (*lin((0.07, 0.07, 0.07)), 1.0)
    bl.inputs["Color2"].default_value = (*lin((0.80, 0.78, 0.745)), 1.0)
    nti.links.new(steg_n.outputs["Result"], bl.inputs["Fac"])
    nti.links.new(bl.outputs["Color"], nti.nodes.get("Principled BSDF").inputs["Base Color"])
    mats = {
        "D01": inn,
        "D02": enkel("chassis", (0.10, 0.10, 0.10), 0.7, 0.0),
        "D10": enkel("luke", (0.10, 0.10, 0.10), 0.7, 0.0),
        "K08": enkel("fot", (0.10, 0.10, 0.10), 0.5),
        "E01": enkel("leidning", (0.035, 0.035, 0.035), 0.75),
        "D08": enkel("opal", (0.90, 0.89, 0.87), 0.5),
    }
    for d in geo["delar"]:
        if d["id"] not in mats or d["id"] in UTAN:
            continue
        bpy.ops.wm.stl_import(filepath=str(BASIS / d["stl"]), global_scale=0.001)
        o = bpy.context.selected_objects[0]
        o.name = d["id"]
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(28))
        except Exception:
            pass
        o.data.materials.append(mats[d["id"]])

    # ---- kamera og lys (fast for alle variantar)
    M = Vector((0.150, 0.0, 0.146))
    cam = bpy.data.cameras.new("kam")
    cam.lens = 165
    co = bpy.data.objects.new("kam", cam)
    sc.collection.objects.link(co)
    co.location = Vector((-0.27, -1.90, 0.64))
    co.rotation_euler = (M - co.location).to_track_quat("-Z", "Y").to_euler()
    if naer:   # nærbilete av betjeninga: matrisa og messingknappen
        cam.lens = 200 * SKALA ** 0.45              # vidare utsnitt når betjeninga er stor i høve til lampa
        co.location = Vector((0.035, -0.86, 0.33))
        sikt = Vector(((MB_X + PKT_X) / 2000.0, -R_ / 1000.0, ((MB_Z + PKT_Z) / 2 + 4.0) / 1000.0))
        co.rotation_euler = (sikt - co.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co

    def flate(nm, pos, storleik, energi, farge=(1, 1, 1), form=None, maal=None):
        l = bpy.data.lights.new(nm, "AREA")
        if form:
            l.shape = "RECTANGLE"
            l.size, l.size_y = form
        else:
            l.size = storleik
        l.energy = energi
        l.color = farge
        o = bpy.data.objects.new(nm, l)
        sc.collection.objects.link(o)
        o.location = Vector(pos)
        o.rotation_euler = ((Vector(maal) if maal else M) - o.location).to_track_quat("-Z", "Y").to_euler()

    flate("nokkel", (-1.30, -1.30, 1.05), 1.9, 88)                          # stor, mjuk, oppe til venstre
    flate("stripe", (-1.9, -0.25, 0.30), 0, 30, form=(0.35, 1.6))            # streiflys frå venstre: løftar relieff
    flate("front", (-0.15, -2.5, -0.15), 0, 15, form=(1.6, 1.2))             # låg flate framfor: framsida har noko å spegle
    flate("nase", (1.75, 0.10, -0.10), 0, 30, form=(0.45, 1.5))              # loddrett stripe til høgre: høglys på nasen
    flate("kant", (1.25, 0.95, 0.95), 0, 26, (0.90, 0.94, 1.0), form=(0.4, 1.4))  # kjølig kantlys bak til høgre
    flate("topp", (0.15, -0.2, 1.7), 1.2, 10)
    # svakt varmt lys nede i skjermen: innsida får eit fall, og tingen les som lampe
    flate("inni", (0.150, 0.0, 0.222), 0, 0.22, (1.0, 0.80, 0.58), form=(0.24, 0.07), maal=(0.150, 0.0, 0.5))
    w = bpy.data.worlds.new("verd")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes.get("Background").inputs["Color"].default_value = (0, 0, 0, 1)
    w.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.0

    utmappe = HER / "bilete"
    utmappe.mkdir(exist_ok=True)
    fil = Path(ut) if ut else utmappe / f"{namn}{'_naer' if naer else ''}{'_prove' if prove else ''}.png"
    sc.render.filepath = str(fil)
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    bpy.ops.render.render(write_still=True)
    # legg på heilt svart bakgrunn (#000)
    from PIL import Image
    im = Image.open(fil).convert("RGBA")
    bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
    bg.alpha_composite(im)
    bg.convert("RGB").save(fil)
    print("SKREIV", fil)
    return fil


if __name__ == "__main__":
    arg = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not arg:
        sys.exit("bruk: python sveip_hud.py <variant> [--prove]")
    sys.path.insert(0, str(HER))
    import sveip_hud                    # same modul som variantane importerer, så oppsett() gjeld
    sveip_hud.render(arg[0], prove="--prove" in sys.argv, naer="--naer" in sys.argv)
