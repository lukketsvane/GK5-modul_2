# -*- coding: utf-8 -*-
"""skal.py: skalvariantar av M1 (kroppen på Sveip mini) for 3D-print.

Innsida er den same som i mini_print.py, så chassiset, lysrista, lysplata og micro:bit-en passar
i alle variantane. Berre ytterhuda er ny. Ho er stadionflata rundt lampa, bretta ut til eit
rutenett (s, z): s er boglengda rundt (0 i nasen, framsida først) og z er høgda.

Ein variant er ei fil <namn>.py i denne mappa med
    def hud(H): return h
der h er ein tabell med same form som H.S: høgda i mm ut frå den glatte flata (negativ er inn).
H har rutenettet, verdskoordinatane og ferdige avstandsfelt (sjå klassen Hud).

Korleis skalet blir bygt (manifold3d):
    kropp = M1 frå mini_print.kropp()                    (glatt)
    kjerne = kropp − det ytste laget, 0,55 mm             (innsida og endeplatene står att)
    skal = kjerne ∪ (ny ytterhud frå −0,6 til h, skoren som M1 under skjermen)
    skal = skal − feltet, dei 25 LED-hola og holet for messingskruen (same mål som i mini_print)
h blir klipt til [−0,5, +2,0]. Veggen er då minst 0,7 mm. h blir tona ned til 0 inn mot feltet.

Køyr frå skal/:
    python3 skal.py <namn> [--rask]     bygg, kontroller, skriv print/<namn>.3mf og rapport
    python3 skal.py glatt               kontrollerer at byggjaren gjev same lekam som mini_print
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
sys.path.insert(0, str(HER.parent))
sys.path.insert(0, str(HER))

import cadquery as cq                      # noqa: E402
import manifold3d as mf                    # noqa: E402

import mini_print as MP                    # noqa: E402
from mini_passform import D, S, X_ST, Z_SK, stadion   # noqa: E402

R = D / 2
BUE = math.pi * R / 2                      # kvartboge i nasen
FLAT = S - 2 * R                           # flat side, 54,6
P = 2 * FLAT + 2 * math.pi * R             # omkrinsen, 201,6
S_FRAMME = (BUE, BUE + FLAT)
S_VENSTRE = (BUE + FLAT, BUE + FLAT + math.pi * R)
S_BAK = (S_VENSTRE[1], S_VENSTRE[1] + FLAT)
T = MP.T                                   # veggen, 1,2
R_INN = MP.R_INN                           # hjørnet under skjermen, 3,36
INN = 0.6                                  # den nye ytterhuda går så langt inn i veggen
LAG = 0.55                                 # så mykje av den glatte veggen blir teke bort
H_MIN, H_MAX = -0.5, 2.0
MX, MZ = MP.MX, MP.MZ
LOGO = MP.LOGO                             # messingskruen (x, z)
FELT = (MX - 11.5, MZ - 11.5, LOGO[0] + 6.5, MZ + 11.5)   # x0, z0, x1, z1, hjørne r 3,5
FELT_R = 3.5
TONE_FELT = (0.3, 2.5)                     # h går frå 0 til fullt mellom desse avstandane frå feltet


def plan(s):
    """Punkt (x, y), normal (nx, ny) og flate for boglengda s.
    Flater: 0 nase framme, 1 framside, 2 venstre boge, 3 bakside, 4 nase bak."""
    s = np.asarray(s, dtype=np.float64) % P
    x, y, nx, ny = (np.empty_like(s) for _ in range(4))
    fl = np.empty(s.shape, dtype=np.int8)
    a = s < BUE
    th = -s[a] / R
    x[a], y[a], nx[a], ny[a], fl[a] = S - R + R * np.cos(th), R * np.sin(th), np.cos(th), np.sin(th), 0
    b = (s >= S_FRAMME[0]) & (s < S_FRAMME[1])
    x[b], y[b], nx[b], ny[b], fl[b] = S - R - (s[b] - BUE), -R, 0.0, -1.0, 1
    c = (s >= S_VENSTRE[0]) & (s < S_VENSTRE[1])
    th = -math.pi / 2 - (s[c] - S_VENSTRE[0]) / R
    x[c], y[c], nx[c], ny[c], fl[c] = R + R * np.cos(th), R * np.sin(th), np.cos(th), np.sin(th), 2
    d = (s >= S_BAK[0]) & (s < S_BAK[1])
    x[d], y[d], nx[d], ny[d], fl[d] = R + (s[d] - S_BAK[0]), R, 0.0, 1.0, 3
    e = s >= S_BAK[1]
    th = math.pi / 2 - (s[e] - S_BAK[1]) / R
    x[e], y[e], nx[e], ny[e], fl[e] = S - R + R * np.cos(th), R * np.sin(th), np.cos(th), np.sin(th), 4
    return x, y, nx, ny, fl


def glatt(x, a, b):
    """Mjukt steg frå 0 (x <= a) til 1 (x >= b). a > b gjev fallande steg."""
    t = np.clip((np.asarray(x, dtype=np.float64) - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def avst_tomrom(x, z):
    """mm i x-z frå punktet til utskjeringa under skjermen (tomrom() i mini_print: rektangel med
    hjørne r R_INN), negativ inne i ho."""
    cx, cz = X_ST + R_INN, Z_SK - R_INN
    dx, dz = cx - x, z - cz
    ute = np.hypot(np.maximum(dx, 0.0), np.maximum(dz, 0.0))
    inne = np.minimum(np.maximum(dx, dz), 0.0)
    return ute + inne - R_INN


def i_tomrom(x, z, vekst=0.0):
    """Sant der punktet (x, z) ligg i utskjeringa under skjermen, vaksen vekst mm."""
    return avst_tomrom(x, z) < vekst


def i_felt(x, z):
    """Sant inne i det forsenka feltet (avrunda rektangel i x-z, berre framme)."""
    x0, z0, x1, z1 = FELT
    dx = np.maximum(np.maximum(x0 + FELT_R - x, x - (x1 - FELT_R)), 0.0)
    dz = np.maximum(np.maximum(z0 + FELT_R - z, z - (z1 - FELT_R)), 0.0)
    return (x >= x0) & (x <= x1) & (z >= z0) & (z <= z1) & (np.hypot(dx, dz) <= FELT_R)


class Hud:
    """Den utbretta ytterhuda. Alle felt har form (ns, nz + 1): akse 0 er s (går rundt), akse 1 er z.

    S, Z       boglengd og høgd (mm)
    X, Y       verdskoordinatar på den glatte flata; NX, NY er normalen ut
    flate      0 nase framme, 1 framside, 2 venstre boge, 3 bakside, 4 nase bak
    framme     sant på framsida (y < 0), der feltet og messingen er
    fast       sant der huda finst (ikkje i utskjeringa under skjermen)
    skjerm     sant i skjermen (z >= Z_SK), elles stamma
    kant       mm langs huda til næraste frie kant (toppkanten, botnen av stamma, utskjeringa)
    d_felt     mm langs huda frå kanten av feltet (0 inne i feltet)
    d_logo     mm langs huda frå messingskruen
    d_tomrom   mm i x-z frå utskjeringa under skjermen (same framme og bak)
    """

    def __init__(self, steg=0.2):
        self.steg = steg
        self.ns = int(round(P / steg))
        self.nz = int(round(S / steg))
        self.ds, self.dz = P / self.ns, S / self.nz
        s = np.arange(self.ns) * self.ds
        z = np.arange(self.nz + 1) * self.dz
        self.S, self.Z = np.meshgrid(s, z, indexing="ij")
        x, y, nx, ny, fl = plan(s)
        rep = lambda a: np.repeat(a[:, None], self.nz + 1, axis=1)   # noqa: E731
        self.X, self.Y, self.NX, self.NY, self.flate = rep(x), rep(y), rep(nx), rep(ny), rep(fl)
        self.framme = self.Y < 0
        self.skjerm = self.Z >= Z_SK
        self.fast = ~i_tomrom(self.X, self.Z)
        self.kant = self.avstand_til(self.fast)
        felt = i_felt(self.X, self.Z) & self.framme
        self.d_felt = self.avstand_til(~felt)
        self.d_logo = np.hypot(self.avst_s(self.s_av_x(LOGO[0])), self.Z - LOGO[1])
        self.d_tomrom = np.maximum(avst_tomrom(self.X, self.Z), 0.0)

    # ------------------------------------------------------------ hjelparar
    @staticmethod
    def s_av_x(x, framme=True):
        """Boglengda for x på den flate framsida (eller baksida)."""
        return BUE + (S - R - x) if framme else S_BAK[0] + (x - R)

    def avst_s(self, s0):
        """Avstand langs s til s0, rekna rundt."""
        return np.abs(((self.S - s0 + P / 2) % P) - P / 2)

    def avstand_til(self, maske):
        """mm frå kvart punkt i maska til næraste punkt utanfor, rundt i s. Utanfor z tel som utanfor."""
        pad = self.ns // 2
        m = np.concatenate([maske[-pad:], maske, maske[:pad]], axis=0)
        m = np.pad(m, ((0, 0), (1, 1)), constant_values=False)
        d = ndimage.distance_transform_edt(m, sampling=(self.ds, self.dz))
        return np.maximum(d[pad:-pad, 1:-1] - 0.5 * self.steg, 0.0)


# ---------------------------------------------------------------- geometri

def til_manifold(arbeid, tol=0.01):
    v, t = MP.nett(arbeid, tol)
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(v, dtype=np.float32), tri_verts=np.asarray(t, dtype=np.uint32)))


def ny_hud(H, h):
    """Lukka rør frå INN under den glatte flata til h over, frå z = 0 til S."""
    ns, nz1 = H.S.shape
    ut_x, ut_y = H.X + H.NX * h, H.Y + H.NY * h
    inn_x, inn_y = H.X - H.NX * INN, H.Y - H.NY * INN
    v = np.concatenate([np.stack([ut_x, ut_y, H.Z], -1).reshape(-1, 3),
                        np.stack([inn_x, inn_y, H.Z], -1).reshape(-1, 3)])
    n = ns * nz1
    idx = np.arange(n).reshape(ns, nz1)
    i0, i1 = idx, np.roll(idx, -1, axis=0)
    a, b, c, d = i0[:, :-1], i1[:, :-1], i1[:, 1:], i0[:, 1:]
    # s går med klokka sett ovanfrå (framsida først), så (a, c, b) har normalen ut
    ut = np.concatenate([np.stack([a, c, b], -1), np.stack([a, d, c], -1)]).reshape(-1, 3)
    inn = ut[:, ::-1] + n
    lag = []
    for j, fl in ((0, True), (nz1 - 1, False)):        # lokk nede og oppe: ring mellom ytre og indre
        r0, r1 = idx[:, j], np.roll(idx[:, j], -1)
        q = np.concatenate([np.stack([r0, r1, r1 + n], -1), np.stack([r0, r1 + n, r0 + n], -1)])
        lag.append(q if fl else q[:, ::-1])
    t = np.concatenate([ut, inn] + lag)
    rr = mf.Manifold(mf.Mesh(vert_properties=v.astype(np.float32), tri_verts=t.astype(np.uint32)))
    if rr.is_empty() or rr.volume() <= 0:
        raise RuntimeError("ytterhuda er ikkje ein lukka lekam: %s" % rr.status())
    return rr


def kuttarar():
    """Felt, LED-hol og hol for messingskruen, same mål som i mini_print.kropp(). Feltet går ut
    gjennom ytterhuda, så relieff utanfor den glatte flata òg blir skore bort."""
    fx0, fz0, fx1, fz1 = FELT
    felt = (cq.Workplane("XY").box(fx1 - fx0, D / 2 + 4, fz1 - fz0).edges("|Y").fillet(FELT_R)
            .translate(((fx0 + fx1) / 2, -(D / 2 + 4) / 2, (fz0 + fz1) / 2)))
    hud = stadion(S + 8, D + 8, -1, S + 1, x0=-4).cut(
        stadion(S - 2 * MP.FELT_DJUPN, D - 2 * MP.FELT_DJUPN, -2, S + 2, x0=MP.FELT_DJUPN))
    k = felt.intersect(hud)
    hol = MP.fram(-D / 2 + T + 0.5).pushPoints(MP.led_lampa()).circle(MP.HOL_LED / 2).extrude(T + 4)
    skrue = MP.fram(-D / 2 + T + 0.5).center(*LOGO).circle(MP.HOL_SKRUE / 2).extrude(T + 4)
    return k.union(hol).union(skrue)


_FAST = {}


def faste_delar():
    if not _FAST:
        _FAST["kropp"] = til_manifold(MP.kropp())
        lag = stadion(S + 6, D + 6, -1, S + 1, x0=-3).cut(stadion(S - 2 * LAG, D - 2 * LAG, -2, S + 2, x0=LAG))
        _FAST["lag"] = til_manifold(lag)
        _FAST["tomrom"] = til_manifold(MP.tomrom())
        _FAST["kutt"] = til_manifold(kuttarar())
    return _FAST


def bygg(h, H):
    """Skalet som Manifold, og h slik det vart brukt (klipt og tona inn mot feltet)."""
    h = np.clip(np.asarray(h, dtype=np.float64), H_MIN, H_MAX)
    h = h * glatt(H.d_felt, *TONE_FELT)
    f = faste_delar()
    kjerne = f["kropp"] - f["lag"]
    hud = ny_hud(H, h) - f["tomrom"]
    return (kjerne + hud) - f["kutt"], h


# ---------------------------------------------------------------- kontroll og eksport

def til_numpy(m):
    g = m.to_mesh()
    return np.asarray(g.vert_properties[:, :3], dtype=np.float64), np.asarray(g.tri_verts, dtype=np.int64)


def kontroll(skal, h, H):
    """Tal som må halde for at skalet kan printast og passar til resten av byggjesettet."""
    f = faste_delar()
    v, t = til_numpy(skal)
    lukka, vol = MP.kontroll_nett(v, t)
    # innsida: alt i den glatte kroppen som ligg meir enn LAG inn frå ytterflata, er urørt
    indre = f["kropp"] - f["lag"] - f["kutt"]
    mangel = (indre - skal).volume()
    # ingenting nytt inne i lampa: skalet minus (glatt kropp + det ytste laget utanpå) skal vere tomt
    ute = stadion(S + 6, D + 6, -1, S + 1, x0=-3).cut(stadion(S, D, -2, S + 2))
    tillate = f["kropp"] + til_manifold(ute)
    inne_nytt = (skal - tillate).volume()
    # print opp ned: overheng på relieffet
    vp = v.copy()                                   # rotert 180° om x: toppkanten ned på plata
    vp[:, 1], vp[:, 2] = -vp[:, 1], S - vp[:, 2]
    oh = MP.overheng(vp, t)
    return {
        "lukka": bool(lukka) and skal.status() == mf.Error.NoError,
        "volum_mm3": round(vol, 1),
        "trekantar": int(len(t)),
        "genus": int(skal.genus()),
        "innsida_manglar_mm3": round(mangel, 3),
        "nytt_inne_i_lampa_mm3": round(inne_nytt, 3),
        "h_min": round(float(h[H.fast].min()), 3),
        "h_max": round(float(h[H.fast].max()), 3),
        "vegg_min_mm": round(T + float(min(0.0, h[H.fast].min())), 2),
        "overheng": oh,
        "masse_g_pla": round(vol / 1000 * 1.24, 1),
    }


def forenkla(v, t, feil=1e-6):
    """Slår saman trekantar der flata er plan. feil er kvadratfeilen i pyfqmr: 1e-6 flyttar
    ingenting meir enn om lag 0,001 mm (målt på eit bølgjeblikk)."""
    import pyfqmr
    s = pyfqmr.Simplify()
    s.setMesh(v, t)
    s.simplify_mesh_lossless(epsilon=feil, verbose=False)
    v2, t2, _ = s.getMesh()
    return np.asarray(v2, dtype=np.float64), np.asarray(t2, dtype=np.int64)


def i_printstilling(v, cx=128.0, cy=128.0):
    """Opp ned (toppkanten på plata), midt på plata."""
    v = v.copy()
    v[:, 1] = -v[:, 1]
    v[:, 2] = S - v[:, 2]
    v[:, 0] -= (v[:, 0].min() + v[:, 0].max()) / 2 - cx
    v[:, 1] -= (v[:, 1].min() + v[:, 1].max()) / 2 - cy
    v[:, 2] -= v[:, 2].min()
    return v


def skriv_stl(sti, v, t):
    import struct
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    n = np.cross(b - a, c - a)
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    data = np.zeros(len(t), dtype=[("n", "<f4", 3), ("a", "<f4", 3), ("b", "<f4", 3), ("c", "<f4", 3), ("x", "<u2")])
    data["n"], data["a"], data["b"], data["c"] = n, a, b, c
    with open(sti, "wb") as f:
        f.write(b"Sveip mini skal".ljust(80, b" "))
        f.write(struct.pack("<I", len(t)))
        f.write(data.tobytes())


def lag(namn, rask=False):
    """Byggjer varianten namn, kontrollerer og skriv print/<namn>.3mf, print/<namn>.stl og rapporten."""
    H = Hud(steg=0.4 if rask else 0.2)
    if namn == "glatt":
        h = np.zeros(H.S.shape)
    else:
        h = importlib.import_module(namn).hud(H)
    skal, h = bygg(h, H)
    k = kontroll(skal, h, H)
    v, t = til_numpy(skal)
    v, t = forenkla(v, t)
    k["trekantar_forenkla"] = int(len(t))
    lukka, vol = MP.kontroll_nett(v, t)
    k["lukka_forenkla"] = bool(lukka)
    k["volumendring_forenkla_mm3"] = round(vol - k["volum_mm3"], 3)
    ut = HER / "print"
    ut.mkdir(exist_ok=True)
    skriv_stl(ut / f"{namn}.stl", v, t)                   # i lampekoordinatar, for render og samanstilling
    MP.skriv_3mf(ut / f"{namn}.3mf", [(f"M1_kropp_{namn}", (i_printstilling(v), t))],
                 f"Sveip mini, M1 kropp: {namn}", ["lampefarge"])
    (ut / f"{namn}.json").write_text(json.dumps(k, indent=1, ensure_ascii=False), encoding="utf-8")
    return k


if __name__ == "__main__":
    namn = sys.argv[1]
    k = lag(namn, rask="--rask" in sys.argv)
    print(json.dumps(k, indent=1, ensure_ascii=False))
    feil = []
    if not (k["lukka"] and k["lukka_forenkla"]):
        feil.append("nettet er ikkje lukka")
    if k["innsida_manglar_mm3"] > 0.5:
        feil.append("innsida er endra")
    if k["nytt_inne_i_lampa_mm3"] > 0.5:
        feil.append("noko nytt stikk inn i lampa")
    if feil:
        sys.exit("FEIL: " + ", ".join(feil))
