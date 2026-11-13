# -*- coding: utf-8 -*-
"""maaling.py: tal ut av fotoa av arket (ikkje av arket sjolv).

Les:   context/delar-foto/01, 05, 06, 07 (JPEG, berre lokalt)
Skriv: context/delar-foto/analyse/  (figurar, utsnitt, maaling_tal.json)
Skriv ALDRI andre stader. Repoet er offentleg, fotoa er det ikkje.

Koyr:  python konsept/vindauge/film/maaling.py
Tid:   om lag eitt minutt, ein prosess, ingen trad-pool.

Alt her er estimat fraa foto. Ingenting er maalt paa det fysiske arket.
Piksel-vindauga nedanfor er valde for hand etter aa ha sett paa utsnitta;
dei er ein del av metoden og staar opne i koden.
"""
import os, json, glob
os.environ.setdefault("NUMBA_NUM_THREADS", "4")
os.environ.setdefault("OMP_NUM_THREADS", "4")
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, gaussian_filter1d, sobel, map_coordinates
from scipy.optimize import brentq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HER = os.path.dirname(os.path.abspath(__file__))
ROT = os.path.abspath(os.path.join(HER, "..", "..", ".."))
FOTO = os.path.join(ROT, "context", "delar-foto")
UT = os.path.join(FOTO, "analyse")
os.makedirs(UT, exist_ok=True)
RNG = np.random.default_rng(7)
N_MC = 4000
TAL = {}          # alt som blir skrive til maaling_tal.json


# ---------------------------------------------------------------- grunnverkty
def les(nr):
    f = glob.glob(os.path.join(FOTO, "%s-*.jpg" % nr))[0]
    return np.asarray(Image.open(f).convert("RGB"))


def lin(u8):
    """sRGB/P3-koda 8 bit -> lineaer (same kurve for Display P3)."""
    c = u8.astype(np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def graa(u8):
    return u8.astype(np.float64).mean(axis=2)


def ut(namn):
    p = os.path.join(UT, namn)
    assert os.path.abspath(p).startswith(os.path.abspath(UT))
    return p


# ---------------------------------------------------------------- 1 kamera
# EXIF er strippa (berre storleik + Display P3-profil med Apple-signatur).
# Brennvidda blir difor rekna fraa forsvinningspunkt i bygningane ute:
#   f^2 = d_v * d_h, d_v = avstand biletsenter -> loddrett forsvinningspunkt,
#   d_h = avstand biletsenter -> horisontlinja.  ANTAKING: hovudpunkt i
#   biletsenter, kvadratiske pikslar, ikkje beskore bilete.
VP_SPEK = {
    "01": {
        "v": {"L1": (5, 240, 95, 195), "L2": (40, 320, 270, 480), "M1": (300, 580, 130, 275),
              "M1b": (300, 560, 160, 270), "M2": (560, 960, 135, 280), "M2b": (600, 950, 170, 285),
              "M3": (1000, 1300, 150, 300), "R1": (1460, 1820, 180, 340), "R1b": (1560, 1800, 190, 335),
              "R2": (1480, 1930, 380, 600)},
        # vassrette linjer paa fasaden til den lange laage bygningen (ein familie)
        "h": {"fas_V": (310, 640, 125, 0.035), "fas_M": (640, 960, 140, 0.04), "fas_H": (1000, 1280, 155, 0.04),
              "glb_V": (330, 640, 272, 0.05), "glb_M": (640, 960, 293, 0.06), "glb_H": (1000, 1280, 313, 0.06),
              "band_V": (340, 640, 350, 0.07), "band_M": (560, 960, 377, 0.07)},
        "linjer": [("fas_V", "fas_M", "fas_H"), ("glb_V", "glb_M", "glb_H"), ("band_V", "band_M")],
    },
    "07": {
        "v": {"L_rib1": (5, 215, 430, 560), "L_rib2": (5, 215, 560, 680), "L_dor": (100, 330, 240, 400),
              "L_ror": (90, 170, 60, 220), "R_o1": (1640, 1930, 330, 490), "R_o2": (1700, 1930, 330, 490),
              "R_n1": (1620, 1930, 560, 790), "R_n2": (1700, 1930, 600, 790)},
        # vassrette linjer paa teglbygningen til venstre (fasaden gaar innover i biletet)
        "h": {"tak": (60, 300, 60, 0.45), "vindu": (80, 300, 95, 0.36), "band": (20, 330, 402, 0.0),
              "bakke": (20, 300, 655, -0.17)},
        "linjer": [("tak",), ("vindu",), ("band",), ("bakke",)],
    },
}


def _hlinje(gy, x0, x1, yc, m0, half=22, dm=0.12, nm=97):
    xs = np.arange(x0, x1)
    xc = (x0 + x1) / 2.0
    best = (0.0, 0.0, 0.0)
    y0s = np.arange(yc - half, yc + half + 1)
    for m in np.linspace(m0 - dm, m0 + dm, nm):
        Y = y0s[:, None] + m * (xs[None, :] - xc)
        X = np.broadcast_to(xs[None, :], Y.shape)
        v = map_coordinates(gy, [Y, X], order=1).mean(axis=1)
        i = int(np.argmax(v))
        if v[i] > best[2]:
            best = (m, float(y0s[i]), float(v[i]))
    return best[0], best[1], xc


def _vtilt(ev, win, bmax=0.35, nb=141):
    """Dominerande helling dx/dy for nesten loddrette kantar i eit vindauge."""
    x0, x1, y0, y1 = win
    sub = ev[y0:y1, x0:x1]
    H, W = sub.shape
    ys = np.arange(H) - H / 2.0
    m = int(bmax * H / 2) + 2
    bs = np.linspace(-bmax, bmax, nb)
    res = np.empty(nb)
    for k, b in enumerate(bs):
        acc = np.zeros(W)
        for i in range(H):
            acc += np.interp(np.arange(W) + b * ys[i], np.arange(W), sub[i], left=0, right=0)
        s = acc[m:-m]
        res[k] = np.var(s) / (np.mean(s) ** 2 + 1e-9)
    i = int(np.argmax(res))
    if 0 < i < nb - 1:
        a, b_, c = res[i - 1], res[i], res[i + 1]
        return bs[i] + 0.5 * (a - c) / (a - 2 * b_ + c) * (bs[1] - bs[0])
    return bs[i]


def _vp_fraa(vdata, linjer, cx, cy):
    """vdata: [(x, y, b)], linjer: [(y0, m)] med y = y0 + m*x.  Gir f, pitch, rull."""
    A = np.array([[1.0, -b] for (x, y, b) in vdata])        # x_v - b*y_v = x - b*y
    r = np.array([x - b * y for (x, y, b) in vdata])
    xv, yv = np.linalg.lstsq(A, r, rcond=None)[0]
    A = np.array([[-m, 1.0] for (y0, m) in linjer])          # -m*X + Y = y0
    r = np.array([y0 for (y0, m) in linjer])
    xh, yh = np.linalg.lstsq(A, r, rcond=None)[0]
    v = np.array([xv - cx, yv - cy])
    dv = np.hypot(*v)
    u = v / dv                                               # einingsvektor mot loddrett FP
    dh = -np.dot(np.array([xh - cx, yh - cy]), u)            # horisonten staar normalt paa u
    f = np.sqrt(max(dv * dh, 1.0))
    return dict(f=f, xv=xv, yv=yv, xh=xh, yh=yh, dv=dv, dh=dh,
                pitch=np.degrees(np.arctan2(dh, f)), rull=np.degrees(np.arctan2(v[0], v[1])))


def kamera(nr):
    im = les(nr)
    H, W = im.shape[:2]
    cx, cy = W / 2.0, H / 2.0
    g = gaussian_filter(graa(im), 1.2)
    gx = np.abs(sobel(g, axis=1))
    gy = np.abs(sobel(g, axis=0))
    ev = np.clip(gx - 1.5 * gy, 0, None)
    sp = VP_SPEK[nr]
    vdata = [((w[0] + w[1]) / 2.0, (w[2] + w[3]) / 2.0, _vtilt(ev, w)) for w in sp["v"].values()]
    hm = {k: _hlinje(gy, x0, x1, yc, m0) for k, (x0, x1, yc, m0) in sp["h"].items()}

    def linjer_av(hm_):
        out = []
        for grp in sp["linjer"]:
            if len(grp) == 1:
                m, y, xc = hm_[grp[0]]
                out.append((y - m * xc, m))
            else:                                   # fleire vindauge langs same linje: rett linje gjennom punkta
                xs = np.array([hm_[k][2] for k in grp])
                ys = np.array([hm_[k][1] for k in grp])
                m, y0 = np.polyfit(xs, ys, 1)
                out.append((y0, m))
        return out

    r0 = _vp_fraa(vdata, linjer_av(hm), cx, cy)
    # Monte Carlo: stoy paa helling (0.008), linjeposisjon (2 px), linjehelling (0.004), hovudpunkt (30 px)
    fs, ps = [], []
    for _ in range(1500):
        vd = [(x, y, b + RNG.normal(0, 0.008)) for (x, y, b) in vdata]
        hm_ = {k: (m + RNG.normal(0, 0.004), y + RNG.normal(0, 2.0), xc) for k, (m, y, xc) in hm.items()}
        r = _vp_fraa(vd, linjer_av(hm_), cx + RNG.normal(0, 30), cy + RNG.normal(0, 30))
        fs.append(r["f"]); ps.append(r["pitch"])
    r0["f_sd"] = float(np.std(fs)); r0["pitch_sd"] = float(np.std(ps))
    r0["f_ekv_mm"] = r0["f"] * 34.6 / H            # 4:3-bilete: langsida svarar til 34.6 mm i 35 mm-ekvivalent
    r0["f_ekv_sd"] = r0["f_sd"] * 34.6 / H
    r0["vdata"] = [[float(a) for a in t] for t in vdata]
    return {k: (float(v) if np.isscalar(v) else v) for k, v in r0.items()}


# ---------------------------------------------------------------- 2 arkkantar og pose
# Startlinjer (x ved to y) for venstre og hogre kant, valde for hand.
KANT = {
    "07": dict(L=(224, 150, 266, 2380), R=(1648, 215, 1470, 2290), ys=(240, 2300, 30), topp=165, botn=2392),
    "01": dict(L=(292, 470, 425, 1930), R=(1528, 500, 1368, 1960), ys=(520, 1950, 30), topp=470, botn=None),
}


def arkkantar(nr):
    im = les(nr)
    g = gaussian_filter(graa(im), 1.5)
    k = KANT[nr]
    ys = np.arange(*k["ys"])
    res = {}
    for side in ("L", "R"):
        xa, ya, xb, yb = k[side]
        xs, ws = [], []
        for y in ys:
            row = g[y - 3:y + 4].mean(axis=0)
            gxr = np.abs(np.gradient(row))
            x0 = xa + (xb - xa) * (y - ya) / (yb - ya)
            lo, hi = int(x0 - 22), int(x0 + 22)
            i = int(np.argmax(gxr[lo:hi]))
            xs.append(lo + i); ws.append(gxr[lo + i])
        xs = np.array(xs, float); ws = np.array(ws)
        ok = ws > 12.0                                # berre tydelege kantpunkt
        for _ in range(4):                            # robust kubisk tilpassing
            c = np.polyfit(ys[ok], xs[ok], 3)
            ok = (ws > 12.0) & (np.abs(xs - np.polyval(c, ys)) < 5.0)
        res[side] = dict(c=c, n=int(ok.sum()), rms=float(np.std(xs[ok] - np.polyval(c, ys[ok]))),
                         ys=ys[ok], xs=xs[ok])
    return res


def pose(nr, f, kant=None, cy=1288.0):
    """Lokal helling av arket i kameraramma, fraa synleg breidd w(y).
    ANTAKING: arket er eit rektangel med konstant breidd, krumma berre om ein vassrett akse.
    Djupn Z = f*W/w.  theta_s > 0 tyder at nedre del ligg lenger unna langs den optiske aksen."""
    kant = kant or arkkantar(nr)
    cL, cR = kant["L"]["c"], kant["R"]["c"]
    cw = np.polysub(cR, cL)
    dw = np.polyder(cw)

    def w(y): return np.polyval(cw, y)

    def theta(y):
        return np.degrees(np.arctan(-f * np.polyval(dw, y) / (w(y) - (y - cy) * np.polyval(dw, y))))

    def s_fraa_topp(y, y0):                            # bogelengd i einingar av arkbreidda W
        yy = np.linspace(y0, y, 400)
        Z = f / w(yy); Y = (yy - cy) / w(yy)
        return float(np.sum(np.hypot(np.diff(Z), np.diff(Y))))
    return w, theta, s_fraa_topp


# ---------------------------------------------------------------- 3 trekk i bileta
def profil(L, x0, x1, y0, y1, sigma=3.0):
    p = L[y0:y1, x0:x1].mean(axis=1)
    return np.arange(y0, y1), gaussian_filter1d(p, sigma, axis=0)


def kant50(ys, p, a, b, n=12):
    """y der profilen kryssar midtnivaaet mellom gjennomsnitt i [a,a+n] og [b-n,b]."""
    ia, ib = int(a - ys[0]), int(b - ys[0])
    v0, v1 = p[ia:ia + n].mean(), p[ib - n:ib].mean()
    mid = 0.5 * (v0 + v1)
    seg = p[ia:ib] - mid
    idx = np.where(np.sign(seg[:-1]) != np.sign(seg[1:]))[0]
    if len(idx) == 0:
        return float("nan"), v0, v1
    i = idx[0]
    return float(a + i + seg[i] / (seg[i] - seg[i + 1])), float(v0), float(v1)


def topp(ys, p, a, b):
    ia, ib = int(a - ys[0]), int(b - ys[0])
    i = int(np.argmax(p[ia:ib]))
    pk = p[ia + i]
    base = min(p[ia:ia + 8].mean(), p[ib - 8:ib].mean())
    half = base + 0.5 * (pk - base)
    j0 = i
    while j0 > 0 and p[ia + j0] > half: j0 -= 1
    j1 = i
    while j1 < ib - ia - 1 and p[ia + j1] > half: j1 += 1
    return float(a + i), float(j1 - j0), float(pk), float(base)


def vinkel(y, f, cy=1288.0):
    """Vinkel under den optiske aksen (grader), i loddplanet gjennom biletsenteret."""
    return np.degrees(np.arctan((np.asarray(y, float) - cy) / f))


# ---------------------------------------------------------------- 4 prismemodell (2D, to flater + plan bakside)
def D_fram(phi, alfa=45.0, n=1.59):
    """Prismeside MOT kamera.  phi: kamerastraalen sin vinkel fraa arknormalen, positiv naar
    straalen peikar meir nedover enn normalen.  Returnerer avboyinga oppover (grader) for biletet
    gjennom flatene som vender ned.  nan naar flata blir sett langs kanten."""
    phi = np.asarray(phi, float)
    i = np.radians(alfa + phi)
    with np.errstate(invalid="ignore"):
        t = np.arcsin(np.sin(i) / n)
        inn = np.radians(alfa) - t
        ut_ = np.arcsin(np.clip(n * np.sin(inn), -1, 1))
        d = phi + np.degrees(ut_)
    return np.where((alfa + phi < 90) & (alfa + phi > -90) & (np.abs(n * np.sin(inn)) <= 1), d, np.nan)


def D_bak(phi, alfa=45.0, n=1.59):
    """Prismeside mot VINDAUGET (plan side mot kamera).  Avboying oppover for det eine reine biletet."""
    phi = np.asarray(phi, float)
    with np.errstate(invalid="ignore"):
        beta = np.arcsin(np.sin(np.radians(phi)) / n)
        i = np.radians(alfa) - beta
        s = n * np.sin(i)
        e = np.arcsin(np.clip(s, -1, 1))
        d = phi - alfa + np.degrees(e)
    return np.where(np.abs(s) <= 1, d, np.nan)


def M_flat(fun, phi, **kw):
    """Loddrett vinkelforstorring for eit plant ark: d(kameravinkel)/d(scenevinkel)."""
    h = 0.05
    dD = (fun(phi + h, **kw) - fun(phi - h, **kw)) / (2 * h)
    return 1.0 / (1.0 - dD)


def dD_dn(fun, phi, alfa=45.0, n=1.59):
    return (fun(phi, alfa=alfa, n=n + 0.005) - fun(phi, alfa=alfa, n=n - 0.005)) / 0.01


def alfa_for(D_obs, phi, n, fun=D_fram, lo=20.0, hi=70.0):
    g = lambda a: float(fun(phi, alfa=a, n=n)) - D_obs
    aa = np.linspace(lo, hi, 101)
    vals = np.array([g(a) for a in aa])
    ok = np.isfinite(vals)
    for k in range(len(aa) - 1):
        if ok[k] and ok[k + 1] and vals[k] * vals[k + 1] <= 0:
            return brentq(g, aa[k], aa[k + 1])
    return float("nan")


# ================================================================= hovudlaup
def main():
    # ---- 1 kamera
    kam = {nr: kamera(nr) for nr in ("01", "07")}
    for nr in kam:
        print("kamera %s: f = %.0f +/- %.0f px (%.1f +/- %.1f mm ekv.), pitch %.1f +/- %.1f, rull %.1f" % (
            nr, kam[nr]["f"], kam[nr]["f_sd"], kam[nr]["f_ekv_mm"], kam[nr]["f_ekv_sd"],
            kam[nr]["pitch"], kam[nr]["pitch_sd"], kam[nr]["rull"]))
    TAL["kamera"] = kam
    f01, f07 = kam["01"]["f"], kam["07"]["f"]

    # ---- 2 kantar og pose
    kant = {nr: arkkantar(nr) for nr in ("01", "07")}
    pose_f = {}
    for nr, f in (("01", f01), ("07", f07)):
        w, th, s = pose(nr, f, kant[nr])
        pose_f[nr] = (w, th, s)
        ys = np.arange(KANT[nr]["ys"][0], KANT[nr]["ys"][1], 240)
        print("pose %s: " % nr + ", ".join("y=%d w=%.0f th=%.1f" % (y, w(y), th(y)) for y in ys))
        TAL["pose_" + nr] = dict(kantpunkt_L=kant[nr]["L"]["n"], kantpunkt_R=kant[nr]["R"]["n"],
                                 rms_L=kant[nr]["L"]["rms"], rms_R=kant[nr]["R"]["rms"],
                                 y=[int(y) for y in ys], w=[float(w(y)) for y in ys],
                                 theta_s=[float(th(y)) for y in ys])
    # hoegd/breidd for heile arket (07 viser baade topp og botn)
    w7, th7, s7 = pose_f["07"]
    HW = s7(KANT["07"]["botn"], KANT["07"]["topp"])
    TAL["ark_hoegd_over_breidd"] = HW
    print("ark H/W (bogelengd, 07): %.3f" % HW)
    # er toppen av arket loddrett (ligg mot glaset)?  lean = pitch - theta_s
    for nr in ("01", "07"):
        w, th, s = pose_f[nr]
        y0 = KANT[nr]["ys"][0] + 60
        TAL["helling_topp_" + nr] = float(kam[nr]["pitch"] - th(y0))
        print("helling fraa lodd, topp %s: %.1f grader" % (nr, kam[nr]["pitch"] - th(y0)))

    # ---- 3 trekk
    L01, L07 = lin(les("01")), lin(les("07"))
    trekk = {}

    # 07: direkte takline over toppen av arket (himmel -> morkt bygg), tre kolonneband
    dir07 = []
    for (x0, x1, a, b) in ((400, 500, 40, 130), (540, 630, 60, 140), (840, 880, 30, 110)):
        ys, p = profil(L07, x0, x1, 0, 200, 2.0)
        y, v0, v1 = kant50(ys, p[:, 2], a, b)          # blaakanalen: himmel lys, bygg mork
        dir07.append(y)
    trekk["07_takline_direkte_y"] = dir07

    # 07: same takline gjennom arket, per fargekanal (morke bygg, x 390-540)
    gj07 = {}
    for kan, c, (a, b) in (("R", 0, (1630, 1790)), ("G", 1, (1670, 1790)), ("B", 2, (1780, 1960))):
        vals = []
        for (x0, x1) in ((390, 450), (500, 540)):
            ys, p = profil(L07, x0, x1, 1300, 2100)
            vals.append(kant50(ys, p[:, c], a, b)[0])
        gj07[kan] = float(np.nanmean(vals))
    trekk["07_takline_gjennom_y"] = gj07
    # 07: lyst lite bygg (gavl), topp-posisjon per kanal
    ys, p = profil(L07, 730, 770, 1300, 2100)
    trekk["07_gavl_topp_y"] = dict(R=topp(ys, p[:, 0], 1700, 1800)[0], G=topp(ys, p[:, 1], 1760, 1840)[0],
                                   B=topp(ys, p[:, 2], 1810, 1900)[0])
    # 07: toppen av det hoge gule bygget gjennom arket (R stig)
    tt = []
    for (x0, x1, a, b) in ((870, 930, 1440, 1560), (960, 1010, 1380, 1560), (1060, 1100, 1350, 1460)):
        ys, p = profil(L07, x0, x1, 1300, 2100)
        tt.append(kant50(ys, p[:, 0], a, b)[0])
    trekk["07_hogt_bygg_topp_gjennom_y"] = tt

    # 01: takline gjennom arket (x 600-680) per kanal, og lyst lite bygg
    gj01 = {}
    ys, p = profil(L01, 600, 680, 1150, 1750)
    for kan, c, (a, b) in (("R", 0, (1330, 1400)), ("G", 1, (1340, 1420)), ("B", 2, (1360, 1440))):
        gj01[kan] = kant50(ys, p[:, c], a, b)[0]
    trekk["01_takline_gjennom_y"] = gj01
    ys, p = profil(L01, 780, 810, 1150, 1750)
    trekk["01_gavl_topp_y"] = dict(R=topp(ys, p[:, 0], 1330, 1420)[0], G=topp(ys, p[:, 1], 1330, 1420)[0])
    tt = []
    for (x0, x1, a, b) in ((930, 970, 1270, 1350), (1020, 1080, 1260, 1340), (1120, 1160, 1280, 1345)):
        ys, p = profil(L01, x0, x1, 1150, 1750)
        tt.append(kant50(ys, p[:, 0], a, b)[0])
    trekk["01_hogt_bygg_topp_gjennom_y"] = tt

    # tynn lys line og nedre kant av det lyse platået, begge foto; og vindaugsramma sett direkte
    def linje_og_kant(L, kol, vin_l, vin_k, yr):
        out = dict(line={}, line_fwhm={}, kant=[])
        for kan, c in (("R", 0), ("G", 1), ("B", 2)):
            pos, fw = [], []
            for (x0, x1) in kol:
                ys, p = profil(L, x0, x1, yr[0], yr[1], 2.0)
                t = topp(ys, p[:, c], *vin_l)
                pos.append(t[0]); fw.append(t[1])
            out["line"][kan] = float(np.mean(pos)); out["line_fwhm"][kan] = float(np.mean(fw))
        for (x0, x1) in kol:
            ys, p = profil(L, x0, x1, yr[0], yr[1], 2.0)
            out["kant"].append(kant50(ys, p.mean(axis=1), *vin_k)[0])
        return out
    trekk["07_line"] = linje_og_kant(L07, ((320, 420), (560, 640), (900, 960), (1380, 1440)), (1770, 1840), (1985, 2060), (1500, 2450))
    trekk["01_line"] = linje_og_kant(L01, ((470, 540), (640, 700), (860, 900), (1280, 1320)), (1640, 1720), (1830, 1915), (1250, 2000))
    ys, p = profil(L07, 1520, 1580, 1500, 2450, 2.0); pm = p.mean(axis=1)
    trekk["07_ramme_direkte"] = dict(overkant=kant50(ys, pm, 1870, 1925)[0], hylle_underkant=kant50(ys, pm, 2025, 2060)[0])
    ys, p = profil(L01, 1400, 1440, 1250, 2000, 2.0); pm = p.mean(axis=1)
    trekk["01_ramme_direkte"] = dict(overkant=kant50(ys, pm, 1745, 1790)[0], hylle_underkant=kant50(ys, pm, 1880, 1910)[0])
    TAL["trekk_piksel"] = trekk

    # ---- 4 vinklar, avboying, frynser
    res = {}
    a_dir07 = float(np.mean(vinkel(np.nanmean(dir07[:2]), f07)))          # taklina til dei morke bygga
    D07 = {k: float(vinkel(v, f07) - a_dir07) for k, v in gj07.items()}
    y_sky07 = gj07["R"]
    phi07 = float(vinkel(y_sky07, f07) + th7(y_sky07))
    res["07"] = dict(a_direkte=a_dir07, a_gjennom={k: float(vinkel(v, f07)) for k, v in gj07.items()},
                     D=D07, theta_s=float(th7(y_sky07)), phi=phi07)
    # 01: taklina ligg over biletkanten. Hogda over horisonten blir henta fraa 07
    # (ANTAKING: same kamerahoegd og fjernt bygg), og lagt paa pitch for 01.
    elev = -(a_dir07 + kam["07"]["pitch"])
    w1, th1, s1 = pose_f["01"]
    a_dir01 = -(elev + kam["01"]["pitch"])
    D01 = {k: float(vinkel(v, f01) - a_dir01) for k, v in gj01.items()}
    y_sky01 = gj01["R"]
    phi01 = float(vinkel(y_sky01, f01) + th1(y_sky01))
    res["01"] = dict(a_direkte_ekstrapolert=float(a_dir01), y_direkte_ekstrapolert=float(1288 + f01 * np.tan(np.radians(a_dir01))),
                     takline_elevasjon=float(elev), a_gjennom={k: float(vinkel(v, f01)) for k, v in gj01.items()},
                     D=D01, theta_s=float(th1(y_sky01)), phi=phi01)
    # nedre grense for 01 utan ekstrapolering: taklina er ikkje i biletet, altsaa over y = 0
    res["01"]["D_nedre_grense"] = float(vinkel(y_sky01, f01) - vinkel(0, f01))
    # frynser: avstand R -> B i grader
    fr = {}
    fr["07_takline_RB"] = float(vinkel(gj07["B"], f07) - vinkel(gj07["R"], f07))
    fr["07_takline_RG"] = float(vinkel(gj07["G"], f07) - vinkel(gj07["R"], f07))
    g7 = trekk["07_gavl_topp_y"]
    fr["07_gavl_RB"] = float(vinkel(g7["B"], f07) - vinkel(g7["R"], f07))
    fr["07_gavl_RG"] = float(vinkel(g7["G"], f07) - vinkel(g7["R"], f07))
    fr["01_takline_RB"] = float(vinkel(gj01["B"], f01) - vinkel(gj01["R"], f01))
    fr["01_takline_RG"] = float(vinkel(gj01["G"], f01) - vinkel(gj01["R"], f01))
    l7, l1 = trekk["07_line"], trekk["01_line"]
    fr["07_line_BR"] = float(vinkel(l7["line"]["R"], f07) - vinkel(l7["line"]["B"], f07))
    fr["01_line_BR"] = float(vinkel(l1["line"]["R"], f01) - vinkel(l1["line"]["B"], f01))
    fr["07_line_fwhm_grader"] = float(np.degrees(l7["line_fwhm"]["G"] / f07))
    fr["01_line_fwhm_grader"] = float(np.degrees(l1["line_fwhm"]["G"] / f01))
    res["frynser_grader"] = fr
    # loddrett strekk: avstand takline -> topp hogt bygg, gjennom arket (px og grader)
    for nr, f, gj, tp in (("07", f07, gj07, trekk["07_hogt_bygg_topp_gjennom_y"]), ("01", f01, gj01, trekk["01_hogt_bygg_topp_gjennom_y"])):
        d = gj["R"] - np.array(tp)
        res[nr]["takline_minus_hogt_bygg_px"] = [float(x) for x in d]
        res[nr]["takline_minus_hogt_bygg_grader"] = [float(vinkel(gj["R"], f) - vinkel(t, f)) for t in tp]
    # 07 direkte: det hoge bygget stikk minst fraa takryggen (y ~ 65) til biletkanten (y = 0)
    res["07"]["hogt_bygg_over_ryggen_direkte_min_grader"] = float(vinkel(65, f07) - vinkel(0, f07))
    # tilt-skann: posisjon paa arket (bogelengd fraa topp, i arkbreidder) for line og kant
    pos = {}
    pos["07_line_s"] = s7(l7["line"]["G"], KANT["07"]["topp"]); pos["07_kant_s"] = s7(np.nanmean(l7["kant"]), KANT["07"]["topp"])
    pos["01_line_s"] = s1(l1["line"]["G"], KANT["01"]["topp"]); pos["01_kant_s"] = s1(np.nanmean(l1["kant"]), KANT["01"]["topp"])
    pos["07_takline_s"] = s7(y_sky07, KANT["07"]["topp"]); pos["01_takline_s"] = s1(y_sky01, KANT["01"]["topp"])
    for nr, f, th, l in (("07", f07, th7, l7), ("01", f01, th1, l1)):
        pos[nr + "_line_phi"] = float(vinkel(l["line"]["G"], f) + th(l["line"]["G"]))
        pos[nr + "_kant_phi"] = float(vinkel(np.nanmean(l["kant"]), f) + th(np.nanmean(l["kant"])))
    res["posisjon_paa_arket"] = {k: float(v) for k, v in pos.items()}
    TAL["vinklar"] = res
    print("07: D(R,G,B) = %.1f %.1f %.1f ved phi = %.1f (theta_s %.1f)" % (D07["R"], D07["G"], D07["B"], phi07, th7(y_sky07)))
    print("01: D(R,G,B) = %.1f %.1f %.1f ved phi = %.1f (theta_s %.1f); nedre grense %.1f" % (
        D01["R"], D01["G"], D01["B"], phi01, th1(y_sky01), res["01"]["D_nedre_grense"]))
    print("frynser:", {k: round(v, 2) for k, v in fr.items()})
    print("posisjon:", {k: round(v, 2) for k, v in pos.items()})

    # ---- 5 modellsamanlikning + Monte Carlo
    mod = {}
    for nr, D, phi in (("07", D07["R"], phi07), ("01", D01["R"], phi01)):
        mod[nr] = dict(D_obs=D, phi=phi,
                       fram90=float(D_fram(phi)), bak90=float(D_bak(phi)),
                       M_fram90=float(M_flat(D_fram, phi)), M_bak90=float(M_flat(D_bak, phi)),
                       dDdn_fram90=float(dD_dn(D_fram, phi)), dDdn_bak90=float(dD_dn(D_bak, phi)))
    # MC: f (fraa FP-analysen), theta_s (2 gr), trekkposisjon (8 px gjennom, 5 px direkte), n_R (1.585 +/- 0.03),
    # for 01 i tillegg pitch-skilnaden (pitch_sd for begge foto)
    apex7, apex1, r_fram, r_bak = [], [], [], []
    for _ in range(N_MC):
        n = RNG.normal(1.585, 0.03)
        fa = RNG.normal(f07, kam["07"]["f_sd"]); sc = fa / f07
        ths = np.degrees(np.arctan(np.tan(np.radians(th7(y_sky07))) * sc)) + RNG.normal(0, 2.0)
        a_g = vinkel(y_sky07 + RNG.normal(0, 8), fa); a_d = vinkel(np.nanmean(dir07[:2]) + RNG.normal(0, 5), fa)
        D7, p7 = a_g - a_d, a_g + ths
        apex7.append(180 - 2 * alfa_for(D7, p7, n))
        fb = RNG.normal(f01, kam["01"]["f_sd"]); scb = fb / f01
        pit7 = np.degrees(np.arctan(np.tan(np.radians(kam["07"]["pitch"])) / sc)) + RNG.normal(0, 1.0)
        pit1 = np.degrees(np.arctan(np.tan(np.radians(kam["01"]["pitch"])) / scb)) + RNG.normal(0, 1.0)
        a_d1 = -(-(a_d + pit7) + pit1)
        ths1 = np.degrees(np.arctan(np.tan(np.radians(th1(y_sky01))) * scb)) + RNG.normal(0, 3.0)
        a_g1 = vinkel(y_sky01 + RNG.normal(0, 8), fb)
        D1, p1 = a_g1 - a_d1, a_g1 + ths1
        apex1.append(180 - 2 * alfa_for(D1, p1, n))
        r_fram.append((D7 - float(D_fram(p7, n=n)), D1 - float(D_fram(p1, n=n))))
        r_bak.append((D7 - float(D_bak(p7, n=n)), D1 - float(D_bak(p1, n=n))))
    apex7, apex1 = np.array(apex7), np.array(apex1)
    r_fram, r_bak = np.array(r_fram), np.array(r_bak)

    def stat(a):
        a = a[np.isfinite(a)]
        return dict(median=float(np.median(a)), p16=float(np.percentile(a, 16)), p84=float(np.percentile(a, 84)),
                    p2_5=float(np.percentile(a, 2.5)), p97_5=float(np.percentile(a, 97.5)))
    mod["toppvinkel_fram_07"] = stat(apex7)
    mod["toppvinkel_fram_01"] = stat(apex1)
    # vekta samanslaaing av dei to fotoa (sd fraa 16-84-intervallet)
    m7, s7_ = np.nanmedian(apex7), 0.5 * (np.nanpercentile(apex7, 84) - np.nanpercentile(apex7, 16))
    m1, s1_ = np.nanmedian(apex1), 0.5 * (np.nanpercentile(apex1, 84) - np.nanpercentile(apex1, 16))
    wsum = 1 / s7_ ** 2 + 1 / s1_ ** 2
    mod["toppvinkel_fram_samla"] = dict(verdi=float((m7 / s7_ ** 2 + m1 / s1_ ** 2) / wsum), sd=float(wsum ** -0.5))
    for namn, r in (("fram90", r_fram), ("bak90", r_bak)):
        r = r[np.all(np.isfinite(r), axis=1)]
        mod["rest_" + namn] = dict(snitt_07=float(r[:, 0].mean()), sd_07=float(r[:, 0].std()),
                                   snitt_01=float(r[:, 1].mean()), sd_01=float(r[:, 1].std()),
                                   z_07=float(r[:, 0].mean() / r[:, 0].std()), z_01=float(r[:, 1].mean() / r[:, 1].std()))
    # fargespreiing: forventa R->B for dn = 0.018..0.025 (ANTAKING, typisk akrylat/PET-harpiks) ganger flat forstorring
    for nr, phi in (("07", phi07), ("01", phi01)):
        for namn, fun in (("fram", D_fram), ("bak", D_bak)):
            dd = float(dD_dn(fun, phi)); M = float(M_flat(fun, phi))
            mod[nr]["frynse_%s90_flat" % namn] = [dd * 0.018 * M, dd * 0.025 * M]
    TAL["modell"] = mod
    print("toppvinkel (fram) 07:", {k: round(v, 1) for k, v in mod["toppvinkel_fram_07"].items()})
    print("toppvinkel (fram) 01:", {k: round(v, 1) for k, v in mod["toppvinkel_fram_01"].items()})
    print("samla:", mod["toppvinkel_fram_samla"])
    print("rest fram90:", {k: round(v, 2) for k, v in mod["rest_fram90"].items()})
    print("rest bak90:", {k: round(v, 2) for k, v in mod["rest_bak90"].items()})
    for nr in ("07", "01"):
        print(nr, {k: (np.round(v, 2).tolist() if isinstance(v, list) else round(v, 2)) for k, v in mod[nr].items()})

    # ---- 6 transmisjon (lineariserte verdiar; JPEG med tonekart, sjaa maaling.md)
    tr = {}
    him_dir = L07[8:45, 420:680].reshape(-1, 3).mean(axis=0)            # himmel sett direkte, like over taklina
    ark_ovre = L07[400:1100, 400:1300].reshape(-1, 3).mean(axis=0)      # ovre del av arket (to bilete oppaa kvarandre)
    ark_naer = L07[1560:1640, 390:540].reshape(-1, 3).mean(axis=0)      # like over taklina sett gjennom arket
    sno_dir = np.median(L07[1150:1750, 1700:1900].reshape(-1, 3), axis=0)  # sno i skugge, direkte
    tr["07_himmel_direkte_RGB"] = him_dir.tolist(); tr["07_ark_ovre_RGB"] = ark_ovre.tolist()
    tr["07_ark_like_over_takline_RGB"] = ark_naer.tolist(); tr["07_sno_direkte_RGB"] = sno_dir.tolist()
    tr["07_forhold_ovre_mot_himmel"] = (ark_ovre / him_dir).tolist()
    tr["07_forhold_naer_takline_mot_himmel"] = (ark_naer / him_dir).tolist()
    tr["07_del_metta_pikslar_himmel"] = float((les("07")[8:45, 420:680].max(axis=2) >= 250).mean())
    him1 = L01[1100:1250, 600:900].reshape(-1, 3).mean(axis=0)
    tr["01_ark_over_takline_RGB"] = him1.tolist()
    # dersom det nedovervende biletet ser sno og det oppovervende ser himmel: T ~ ark / (0.5*himmel + 0.5*sno)
    tr["07_T_grovt"] = float(ark_naer.mean() / (0.5 * him_dir.mean() + 0.5 * sno_dir.mean()))
    TAL["transmisjon"] = tr
    print("transmisjon:", {k: (np.round(v, 3).tolist() if isinstance(v, list) else round(v, 3)) for k, v in tr.items()})

    # ---- 7 finstruktur i naerbileta (FFT)
    fin = {}
    for nr, ruter in (("05", ((300, 700), (900, 900), (1100, 1500))), ("06", ((300, 600), (900, 700), (1000, 1300))),
                      ("07", ((500, 500), (900, 900), (700, 1300)))):
        g = graa(les(nr))
        ut_ = []
        for (x0, y0) in ruter:
            a = g[y0:y0 + 384, x0:x0 + 384]
            a = a - gaussian_filter(a, 6)
            wv = np.hanning(384)
            F = np.abs(np.fft.fftshift(np.fft.fft2(a * wv[:, None] * wv[None, :]))) ** 2
            c = 192
            yy, xx = np.indices(F.shape)
            r = np.hypot(yy - c, xx - c)
            ang = np.degrees(np.arctan2(yy - c, xx - c)) % 180            # retning paa frekvensvektoren
            m = (r > 20) & (r < 190)
            lodd = F[m & (np.abs(ang - 90) < 10)].mean()                  # frekvens langs y = vassrette liner
            vass = F[m & ((ang < 10) | (ang > 170))].mean()               # frekvens langs x = loddrette liner
            diag = F[m & (np.abs(ang - 45) < 10)].mean()
            # sterkaste topp utanom laagfrekvens, relativt til median i ringen
            Fm = np.where(m, F, 0)
            i = int(np.argmax(Fm)); py, px = divmod(i, F.shape[1])
            ring = F[(np.abs(r - r[py, px]) < 3)]
            ut_.append(dict(rute=[x0, y0], energi_vassrette_liner=float(lodd / diag), energi_loddrette_liner=float(vass / diag),
                            topp_periode_px=float(384.0 / r[py, px]), topp_retning_grader=float(ang[py, px]),
                            topp_over_ringmedian=float(F[py, px] / np.median(ring))))
        fin[nr] = ut_
    TAL["finstruktur"] = fin
    for nr in fin:
        print("fin", nr, [(d["rute"], round(d["energi_vassrette_liner"], 2), round(d["energi_loddrette_liner"], 2),
                           round(d["topp_periode_px"], 1), round(d["topp_retning_grader"]), round(d["topp_over_ringmedian"], 1)) for d in fin[nr]])

    # ---- 8 storleik fraa A4-arket i 07
    # Arket er skore av biletkanten, saa breidda kan ikkje lesast direkte. Maalestokken kjem fraa
    # lineavstanden i brodteksten (autokorrelasjon langs y, inga avskrift) og ANTAKING om 11-12 pt skrift.
    g7 = graa(les("07"))
    blokk = g7[2500:2576, 1720:1932]
    rad = blokk.mean(axis=1) - gaussian_filter1d(blokk.mean(axis=1), 12)
    ac = np.correlate(rad, rad, "full")[len(rad) - 1:]
    lag = int(np.argmax(ac[10:35])) + 10
    p7 = kam["07"]["pitch"]
    dep = p7 + float(vinkel(2538, f07))                       # sikt-vinkel ned mot bordflata der teksten ligg
    px_per_mm = []
    for leading_mm in (4.76, 5.12):                           # 11/13.5 pt og 12/14.5 pt (ANTAKING)
        px_per_mm.append((lag / np.sin(np.radians(dep))) / leading_mm)
    s_side = float(np.mean(px_per_mm))
    def skala(y):                                             # relativ maalestokk langs same vassrette flate
        return np.sin(np.radians(p7)) + np.cos(np.radians(p7)) * (y - 1288) / f07
    s_botn = s_side * skala(2388) / skala(2538)
    Wpx = float(w7(2300))                                     # breidd nedst (kantane er dekte heilt nedst)
    W_mm = Wpx / s_botn
    TAL["storleik"] = dict(lineavstand_px=lag, siktvinkel_ned=dep, px_per_mm_ved_teksten=px_per_mm,
                           px_per_mm_ved_arkfoten=float(s_botn), breidd_nedst_px=Wpx, breidd_mm=float(W_mm),
                           hoegd_mm=float(W_mm * HW), usikkerheit_relativ=0.15)
    print("storleik: lineavstand %d px, %.2f px/mm ved arkfoten, W = %.0f mm, H = %.0f mm" % (lag, s_botn, W_mm, W_mm * HW))

    # ---- figurar (berre til analyse/)
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ph = np.linspace(-25, 44, 300)
    for a_, st in ((45, "-"), (50, "--"), (40, ":")):
        ax[0].plot(ph, D_fram(ph, alfa=a_), "C0" + st, label="prisme mot kamera, topp %d" % (180 - 2 * a_))
        ax[0].plot(ph, D_bak(ph, alfa=a_), "C3" + st, label="prisme mot vindauge, topp %d" % (180 - 2 * a_))
    for nr, mk in (("07", "o"), ("01", "s")):
        r = r_fram  # berre for feilstolpar
        ax[0].errorbar(mod[nr]["phi"], mod[nr]["D_obs"], xerr=2.5, yerr=(1.3 if nr == "07" else 2.2), fmt="k" + mk, label="maalt, foto " + nr)
    ax[0].set_xlabel("phi: kamerastraale mot arknormal (grader)"); ax[0].set_ylabel("avboying D (grader)")
    ax[0].set_ylim(25, 60); ax[0].legend(fontsize=7); ax[0].grid(alpha=0.3)
    ax[0].set_title("Avboying: modell (n = 1.59) og maalte punkt")
    ax[1].hist(apex7[np.isfinite(apex7)], bins=60, alpha=0.6, label="foto 07")
    ax[1].hist(apex1[np.isfinite(apex1)], bins=60, alpha=0.6, label="foto 01")
    ax[1].axvline(90, color="k"); ax[1].set_xlabel("toppvinkel som gir maalt D (grader), prisme mot kamera")
    ax[1].legend(); ax[1].set_title("Monte Carlo over f, pose, trekk, n")
    fig.tight_layout(); fig.savefig(ut("maaling_avboying_modell.png"), dpi=90); plt.close(fig)

    # profilar med markerte trekk
    fig, ax = plt.subplots(2, 2, figsize=(15, 8))
    for j, (nr, L, kol, yr, gj, ln) in enumerate((("07", L07, ((390, 450), (730, 770)), (1300, 2100), gj07, l7),
                                                    ("01", L01, ((600, 680), (780, 810)), (1150, 1950), gj01, l1))):
        for i, (x0, x1) in enumerate(kol):
            ys, p = profil(L, x0, x1, yr[0], yr[1])
            for c, col in enumerate("rgb"):
                ax[i, j].plot(ys, p[:, c], col, lw=1)
            if i == 0:
                for kan, col in (("R", "r"), ("G", "g"), ("B", "b")):
                    ax[i, j].axvline(gj[kan], color=col, ls="--", lw=0.8)
            ax[i, j].axvline(ln["line"]["G"], color="k", ls=":", lw=0.8)
            ax[i, j].axvline(np.nanmean(ln["kant"]), color="k", ls="-.", lw=0.8)
            ax[i, j].set_title("foto %s, x %d-%d (lin. RGB); stipla: takline per kanal, prikka: tynn line, strekprikka: platåkant" % (nr, x0, x1), fontsize=8)
            ax[i, j].grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(ut("maaling_profilar.png"), dpi=80); plt.close(fig)

    # pose
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    for nr, f in (("07", f07), ("01", f01)):
        w, th, s = pose_f[nr]
        ys = np.arange(KANT[nr]["ys"][0], KANT[nr]["ys"][1], 10)
        ax[0].plot(ys, w(ys), label="foto " + nr)
        ax[0].plot(kant[nr]["R"]["ys"], np.interp(kant[nr]["R"]["ys"], ys, w(ys)), ".", ms=2, color="k")
        ax[1].plot(ys, th(ys), label="theta_s, foto " + nr)
        ax[1].plot(ys, vinkel(ys, f) + th(ys), "--", label="phi midt i arket, foto " + nr)
    ax[0].set_xlabel("y (px)"); ax[0].set_ylabel("synleg arkbreidd (px)"); ax[0].legend(); ax[0].grid(alpha=0.3)
    ax[1].set_xlabel("y (px)"); ax[1].set_ylabel("grader"); ax[1].legend(fontsize=7); ax[1].grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(ut("maaling_pose.png"), dpi=90); plt.close(fig)

    # oversyn med markerte trekk (foto -> berre i analyse/)
    for nr, f, gj, ln, dirs in (("07", f07, gj07, l7, dir07), ("01", f01, gj01, l1, None)):
        im = les(nr)
        fig, ax_ = plt.subplots(figsize=(7.2, 9.6))
        ax_.imshow(im)
        for kan, col in (("R", "red"), ("G", "lime"), ("B", "blue")):
            ax_.axhline(gj[kan], color=col, lw=0.6, ls="--")
        ax_.axhline(ln["line"]["G"], color="white", lw=0.6, ls=":")
        ax_.axhline(np.nanmean(ln["kant"]), color="white", lw=0.6, ls="-.")
        if dirs:
            ax_.axhline(np.nanmean(dirs[:2]), color="yellow", lw=0.6)
        k = kant[nr]
        yy = np.arange(KANT[nr]["ys"][0], KANT[nr]["ys"][1], 10)
        ax_.plot(np.polyval(k["L"]["c"], yy), yy, "c-", lw=0.6); ax_.plot(np.polyval(k["R"]["c"], yy), yy, "c-", lw=0.6)
        ax_.set_title("foto %s: takline gjennom arket (R/G/B stipla), tynn line (prikka), platåkant (strekprikka)" % nr, fontsize=7)
        fig.tight_layout(); fig.savefig(ut("maaling_oversyn_%s.jpg" % nr), dpi=110); plt.close(fig)

    def ren(o):
        if isinstance(o, dict): return {k: ren(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)): return [ren(v) for v in o]
        if isinstance(o, (np.floating, np.integer)): return float(o)
        if isinstance(o, np.ndarray): return o.tolist()
        return o
    with open(ut("maaling_tal.json"), "w", encoding="utf-8") as fh:
        json.dump(ren(TAL), fh, indent=1, ensure_ascii=False)
    print("skrive:", ut("maaling_tal.json"))


if __name__ == "__main__":
    main()
