# -*- coding: utf-8 -*-
"""Gransking, linse: prismeoptikken i (c). Uavhengig strålesporar for hovudet i form04 (FINAL).

Eigen kode frå grunnformlane: lambertsk utsending, Snell på vektorform, Fresnel (upolarisert) ved kvar flate,
totalrefleksjon, Monte Carlo-val mellom refleksjon og transmisjon (forventingsrett), fleire sprett.
Ingen import av felles.py eller form04/motor.py. Tal derifrå er skrivne av som konstantar (merkte).

Geometri i snittet (s, z): s = fram (mot brukaren ved α 0), z = ned frå LED-aksen. Retningar er 3D (dx, ds, dz),
flatene er 2D (lineær struktur, normalane har ingen x-del), så skeive strålar vert rett brotne (Bravais).
  LED: lambertsk stripe z = 0, |s| <= w/2.  Renne: veggar s = ±8 mm frå z = -15 til +5 mm (som geometri() i motor.py),
  svarte (motoren reknar lyset dei tek som tapt).  Plate: PMMA n 1,49, overside z = 50 mm (flat), botn z = 53 mm,
  riller under botnen med deling p. Kvar rille: aktiv fasett med vinkel τ frå designlova og ein stigevegg
  (loddrett, eller med slipp β), valfri avrunding r i alle hjørne (tupp og dal).
Designlova (attgjeven frå docstring/optikk() i motor.py, ikkje kalla): lambertsk vifte inn, kumulativ fluks lineær i
tan θ ut mellom kantane av oppgåvesona, normalen til fasetten frå Snell på vektorform.

Køyr: PYTHONIOENCODING=utf-8 python prisme.py   (om lag 2-4 min, éin prosess, éin tråd)
"""
import math, json, os, sys, time
import numpy as np
from numba import njit

HER = os.path.dirname(os.path.abspath(__file__))
T0 = time.time()

# ---------------- konstantar skrivne av ----------------
# felles.py l.17-33
SX0, SX1, SY, SZ0, SZ1 = -0.275, 0.275, 0.45, 0.10, 0.42
WALL = 0.75
EYES = np.array([[0.0, -0.30, 0.45], [-0.15, -0.30, 0.45], [0.15, -0.30, 0.45]])
TX, TY = np.linspace(-0.30, 0.30, 7), np.linspace(0.05, 0.40, 5)
WX, WZ = np.linspace(-0.70, 0.70, 8), np.linspace(0.05, 1.20, 6)
DX_, DY_ = np.linspace(-0.68, 0.68, 8), np.linspace(0.02, 0.73, 5)
E_TASK, E_FACE, L_MAX, DIM = 500.0, 150.0, 3000.0, 0.25
RHO_VEGG = 0.75                                     # som lysstudie.py / fotometri_ab.py
# form04/motor.py FINAL
n = 1.49
L, BP, D, TP, YS, ZS, Y1, Y2 = 0.60, 0.16, 0.05, 0.003, 0.22, 0.70, 0.02, 0.43
SIG = math.radians(4.0)                             # mattering (motoren: gauss 4° på θ)
CW, ZC, WT = 0.008, 0.005, 0.0015                   # renne: halvbreidd, underkant under LED, veggtjukn (geometri())
COL = ((-0.05, 0.512, 0.004), (0.05, 0.542, 0.76))   # søyle (COL_Y, COL_F, COL_W, za+COL_F)
ARM = ((-0.05, 0.208, 0.73), (0.05, 0.542, 0.76))    # arm over hovudet (ys-0,012 .. COL_Y+COL_F, za .. za+COL_F)
# påstandar i tal.csv / skjerm.json (til samanlikning)
MOTOR = dict(eta=0.7388, samla=0.848, T_fresnel=0.917, RISS=0.95, rille_min=-64.51, rille_maks=65.30, innfall_maks=30.61,
             vifte_fra=-16.70, vifte_til=15.95, Phi=432.737, U0=0.6878, E_skjerm=8.784, E_skjerm_maks=37.50, Ev_stem=39.99,
             R_stem=1.0, L_ansikt_snitt=658.6, Phi_ansikt=79.30, L_auga_arb=10.60)
TH1, TH2 = math.atan((YS - Y2) / ZS), math.atan((YS - Y1) / ZS)
ZB = D + TP


# ---------------- designlova (eigen kode) ----------------
def designlov(npts=8001):
    phm = math.atan(BP / 2 / D)
    ph = np.linspace(-phm, phm, npts)
    F = (np.sin(ph) + math.sin(phm)) / (2 * math.sin(phm))
    th = np.arctan(math.tan(TH1) + F * (math.tan(TH2) - math.tan(TH1)))
    pi_ = np.arcsin(np.sin(ph) / n)
    tau = np.arctan2(n * np.sin(pi_) - np.sin(th), n * np.cos(pi_) - np.cos(th))
    s_top = D * np.tan(ph)
    s_bot = s_top + TP * np.tan(pi_)
    return dict(ph=ph, th=th, pi=pi_, tau=tau, s_top=s_top, s_bot=s_bot, phm=phm)


DL = designlov()


def bue(V, u1, u2, r, nseg=6):
    """Avrunding av hjørnet V (inn-retning u1, ut-retning u2) med radius r. Returnerer punkt langs bogen."""
    c = float(np.clip(u1 @ u2, -1, 1))
    Dl = math.acos(c)                       # svingvinkel
    if Dl < 1e-6 or r <= 0:
        return [V]
    t = r * math.tan(Dl / 2)
    T1, T2 = V - u1 * t, V + u2 * t
    b = u2 - u1; b /= np.linalg.norm(b)
    C = V + b * r / math.cos(Dl / 2)
    a1 = math.atan2(*(T1 - C)[::-1]); a2 = math.atan2(*(T2 - C)[::-1])
    da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
    return [C + r * np.array([math.cos(a1 + da * k / nseg), math.sin(a1 + da * k / nseg)]) for k in range(nseg + 1)]


def profil(p=0.0008, slipp='loddrett', r=0.0, kart='botn'):
    """Underside som polyline (s, z) frå venstre til høgre, med type per segment (2 fasett, 3 stigevegg, 4 avrunding)."""
    K = int(round(BP / p)); p = BP / K
    e = -BP / 2 + np.arange(K + 1) * p
    m = (e[:-1] + e[1:]) / 2
    sk = DL['s_bot'] if kart == 'botn' else DL['s_top']
    tau = np.interp(m, sk, DL['tau']); th = np.interp(m, sk, DL['th']); pi_ = np.interp(m, sk, DL['pi'])
    if slipp == 'loddrett':
        beta = np.zeros(K)
    else:   # slipp mellom utgangsstrålen (når han går utover) og den indre strålen: ingen av dei treffer veggen
        beta = 0.5 * (np.maximum(th * np.sign(tau), 0) + np.abs(pi_))
    V = [np.array([e[0], ZB])]; typ = []
    for k in range(K):
        tk, bk = tau[k], beta[k]
        if abs(tk) < 1e-9:
            V.append(np.array([e[k + 1], ZB])); typ.append(2); continue
        mt = math.tan(abs(tk)); h = p * mt / (1 + mt * math.tan(bk))
        if tk > 0:      # djup ende til venstre: stigevegg, så fasett
            V.append(np.array([e[k] + h * math.tan(bk), ZB + h])); typ += [3, 2]
        else:           # fasett, så stigevegg
            V.append(np.array([e[k + 1] - h * math.tan(bk), ZB + h])); typ += [2, 3]
        V.append(np.array([e[k + 1], ZB]))
    # midten: celle med τ<0 følgd av τ>0 deler djup kant, fjern felles botnpunkt (to stigeveggar mot kvarandre)
    V2, T2 = [V[0]], []
    i = 1; j = 0
    Vs = V; ts = typ
    while i < len(Vs):
        if i + 1 < len(Vs) and j + 1 < len(ts) and ts[j] == 3 and ts[j + 1] == 3 and abs(Vs[i][1] - ZB) < 1e-12:
            T2.append(3); V2.append(Vs[i + 1]); i += 2; j += 2; continue
        V2.append(Vs[i]); T2.append(ts[j]); i += 1; j += 1
    V, typ = V2, T2
    if r > 0:
        V3, T3 = [V[0]], []
        for i in range(1, len(V) - 1):
            u1 = V[i] - V[i - 1]; u1 /= np.linalg.norm(u1)
            u2 = V[i + 1] - V[i]; u2 /= np.linalg.norm(u2)
            lim = 0.45 * min(np.linalg.norm(V[i] - V[i - 1]), np.linalg.norm(V[i + 1] - V[i]))
            Dl = math.acos(float(np.clip(u1 @ u2, -1, 1)))
            rr = min(r, lim / max(math.tan(Dl / 2), 1e-9)) if Dl > 1e-6 else 0.0
            pts = bue(V[i], u1, u2, rr)
            V3.append(pts[0]); T3.append(typ[i - 1])
            for q in pts[1:]:
                V3.append(q); T3.append(4)
        V3.append(V[-1]); T3.append(typ[-1])
        V, typ = V3, T3
    V = np.array(V)
    SA, SB = V[:-1].copy(), V[1:].copy()
    ok = np.linalg.norm(SB - SA, axis=1) > 1e-12
    SA, SB, typ = SA[ok], SB[ok], np.array(typ)[ok]
    # rutenett for oppslag: bingar med breidd p
    smin = np.minimum(SA[:, 0], SB[:, 0]); smax = np.maximum(SA[:, 0], SB[:, 0])
    i0 = np.clip(np.floor((smin + BP / 2) / p - 1e-6).astype(int), 0, K - 1)
    i1 = np.clip(np.floor((smax + BP / 2) / p + 1e-6).astype(int), 0, K - 1)
    lists = [[] for _ in range(K)]
    for g in range(len(SA)):
        for b in range(i0[g], i1[g] + 1):
            lists[b].append(g)
    B0 = np.zeros(K + 1, np.int64); B0[1:] = np.cumsum([len(l) for l in lists])
    BI = np.array([g for l in lists for g in l], np.int64)
    hmax = float(V[:, 1].max() - ZB)
    return dict(SA=np.ascontiguousarray(SA), SB=np.ascontiguousarray(SB), TYP=typ.astype(np.int64), B0=B0, BI=BI, p=p, K=K,
                hmax=hmax, tau=tau, beta=beta, e=e, V=V)


# ---------------- strålesporar (numba) ----------------
@njit(cache=True)
def naermaste(s, z, ds, dz, last, SA, SB, B0, BI, pg, nb, hmax):
    BIG = 1e30; eps = 1e-11
    tb = BIG; kind = -1; sid = -99; ns = 0.0; nz = 0.0
    hb = BP / 2
    if dz != 0.0 and last != -10:                        # overside
        t = (D - z) / dz
        if t > eps:
            sh = s + t * ds
            if abs(sh) <= hb:
                tb = t; kind = 0; sid = -10; ns = 0.0; nz = 1.0
    if ds != 0.0:                                        # endekantar s = ±bp/2, z frå D til ZB
        for k in range(2):
            sg = -hb if k == 0 else hb
            idk = -11 - k
            if idk == last:
                continue
            t = (sg - s) / ds
            if t > eps and t < tb:
                zh = z + t * dz
                if zh >= D and zh <= ZB:
                    tb = t; kind = 1; sid = idk; ns = 1.0; nz = 0.0
    if dz < 0.0 and z > ZC:                              # renneopning / veggunderkant (for strålar på veg opp)
        t = (ZC - z) / dz
        if t > eps and t < tb:
            sh = s + t * ds
            if abs(sh) < CW + WT:
                tb = t; kind = 5; sid = -20
    # underside: band ZB .. ZB+hmax
    zlo = ZB - 1e-9; zhi = ZB + hmax + 1e-9
    if dz > 0.0:
        ta = (zlo - z) / dz; tz = (zhi - z) / dz
    elif dz < 0.0:
        ta = (zhi - z) / dz; tz = (zlo - z) / dz
    else:
        if z >= zlo and z <= zhi:
            ta = 0.0; tz = BIG
        else:
            ta = 1.0; tz = 0.0
    if ta < 0.0:
        ta = 0.0
    if tz > ta and tz > eps and ta < tb:
        te = tz if tz < tb else tb
        sa = s + ta * ds; se = s + te * ds
        if ds >= 0.0:
            sf = max(sa, -hb); st = min(se, hb); okb = sf <= st
        else:
            sf = min(sa, hb); st = max(se, -hb); okb = sf >= st
        if okb:
            i = int((sf + hb) / pg); i1 = int((st + hb) / pg)
            i = min(max(i, 0), nb - 1); i1 = min(max(i1, 0), nb - 1)
            stp = 1 if ds >= 0.0 else -1
            while True:
                blo = -hb + i * pg; bhi = blo + pg
                tl = BIG; gl = -1
                for j in range(B0[i], B0[i + 1]):
                    g = BI[j]
                    if g == last:
                        continue
                    ax = SA[g, 0]; az = SA[g, 1]; ex = SB[g, 0] - ax; ez = SB[g, 1] - az
                    den = ds * ez - dz * ex
                    if abs(den) < 1e-300:
                        continue
                    wx = ax - s; wz = az - z
                    t = (wx * ez - wz * ex) / den
                    u = (wx * dz - wz * ds) / den
                    if t > eps and u >= -1e-12 and u <= 1.0 + 1e-12 and t < tl:
                        sh = s + t * ds
                        if sh >= blo - 1e-12 and sh <= bhi + 1e-12:
                            tl = t; gl = g
                if gl >= 0:
                    if tl < tb:
                        ex = SB[gl, 0] - SA[gl, 0]; ez = SB[gl, 1] - SA[gl, 1]
                        ll = math.sqrt(ex * ex + ez * ez)
                        tb = tl; kind = 2; sid = gl; ns = -ez / ll; nz = ex / ll
                    break
                if i == i1:
                    break
                i += stp
    return tb, kind, sid, ns, nz


@njit(cache=True)
def kjerne(s, z, dx, ds, dz, SA, SB, TYP, B0, BI, pg, nb, hmax, maxb):
    """Eitt strålespor. Kode: 0 ut i luft, 5 renne (s på z = ZC), 3 for mange sprett, 4 feil."""
    med = 0; last = -99; xs = 0.0; nris = 0; nfil = 0; nbb = 0; nfas = 0
    while nbb < maxb:
        t, kind, sid, ns, nz = naermaste(s, z, ds, dz, last, SA, SB, B0, BI, pg, nb, hmax)
        if kind == -1:
            return (0 if med == 0 else 4), s, z, dx, ds, dz, xs, nris, nfil, nfas, nbb
        s += t * ds; z += t * dz; xs += t * dx
        if kind == 5:
            return 5, s, z, dx, ds, dz, xs, nris, nfil, nfas, nbb
        if kind == 2:
            ty = TYP[sid]
            if ty == 3:
                nris += 1
            elif ty == 4:
                nfil += 1
            else:
                nfas += 1
        ci = -(ds * ns + dz * nz)
        if ci < 0.0:
            ns = -ns; nz = -nz; ci = -ci
        n1 = 1.0 if med == 0 else n
        n2 = n if med == 0 else 1.0
        r = n1 / n2
        k = 1.0 - r * r * (1.0 - ci * ci)
        if k < 0.0:
            R = 1.0
        else:
            ct = math.sqrt(k)
            rs = ((n1 * ci - n2 * ct) / (n1 * ci + n2 * ct)) ** 2
            rp = ((n1 * ct - n2 * ci) / (n1 * ct + n2 * ci)) ** 2
            R = 0.5 * (rs + rp)
        if np.random.random() < R:
            ds = ds + 2.0 * ci * ns; dz = dz + 2.0 * ci * nz
        else:
            ct = math.sqrt(k)
            dx = r * dx; ds = r * ds + (r * ci - ct) * ns; dz = r * dz + (r * ci - ct) * nz
            med = 1 - med
        q = math.sqrt(dx * dx + ds * ds + dz * dz)
        dx /= q; ds /= q; dz /= q
        last = sid
        nbb += 1
    return 3, s, z, dx, ds, dz, xs, nris, nfil, nfas, nbb


@njit(cache=True)
def framover(N, seed, w, tre_d, SA, SB, TYP, B0, BI, pg, nb, hmax, OUT, IOUT):
    """LED -> renne -> plate. OUT: s, z, dx, ds, dz, xs. IOUT: kode, nris, nfil, nfas, nsprett.
    Kode 6: teken av rennevegen ved utsending."""
    np.random.seed(seed)
    for i in range(N):
        s0 = (np.random.random() - 0.5) * w
        if tre_d:
            u1 = np.random.random(); u2 = np.random.random()
            st = math.sqrt(u1); dz = math.sqrt(1.0 - u1)
            dx = st * math.cos(2 * math.pi * u2); ds = st * math.sin(2 * math.pi * u2)
        else:
            sp = 2.0 * np.random.random() - 1.0
            ds = sp; dz = math.sqrt(1.0 - sp * sp); dx = 0.0
        if dz < 1e-9:
            IOUT[i, 0] = 6; continue
        t5 = ZC / dz; s5 = s0 + t5 * ds
        if abs(s5) >= CW:
            IOUT[i, 0] = 6; continue
        c, s, z, dx2, ds2, dz2, xs, nr, nf, nfa, nbb = kjerne(s5, ZC, dx, ds, dz, SA, SB, TYP, B0, BI, pg, nb, hmax, 60)
        OUT[i, 0] = s; OUT[i, 1] = z; OUT[i, 2] = dx2; OUT[i, 3] = ds2; OUT[i, 4] = dz2; OUT[i, 5] = xs + t5 * dx
        IOUT[i, 0] = c; IOUT[i, 1] = nr; IOUT[i, 2] = nf; IOUT[i, 3] = nfa; IOUT[i, 4] = nbb


@njit(cache=True)
def bakover(P, Dv, X0, w, seed, SA, SB, TYP, B0, BI, pg, nb, hmax, RES):
    """Strålar frå auga (lokal ramme). RES[i] = 1 om strålen endar på LED-stripa (|s| <= w/2, |x| <= L/2)."""
    np.random.seed(seed)
    for i in range(P.shape[0]):
        c, s, z, dx, ds, dz, xs, nr, nf, nfa, nbb = kjerne(P[i, 0], P[i, 1], Dv[i, 0], Dv[i, 1], Dv[i, 2], SA, SB, TYP, B0, BI, pg, nb, hmax, 60)
        RES[i] = 0.0
        if c == 5 and abs(s) < CW and dz < 0.0:
            t0 = -z / dz
            se = s + t0 * ds; xe = X0[i] + xs + t0 * dx
            if abs(se) <= w / 2 and abs(xe) <= L / 2:
                RES[i] = 1.0


# ---------------- køyring og utlesing ----------------
def spor(Pr, N, w, tre_d=True, seed=1):
    OUT = np.zeros((N, 6)); IOUT = np.zeros((N, 5), np.int64)
    framover(N, seed, w, tre_d, Pr['SA'], Pr['SB'], Pr['TYP'], Pr['B0'], Pr['BI'], Pr['p'], Pr['K'], Pr['hmax'], OUT, IOUT)
    return OUT, IOUT


def budsjett(OUT, IOUT, N, matt=True, seed=5):
    c = IOUT[:, 0]
    ut = c == 0
    th = np.arctan2(OUT[:, 3], OUT[:, 4])
    if matt:
        th = th + np.random.default_rng(seed).normal(0, SIG, len(th))
    ned = ut & (np.cos(th) > 0)
    tl, tr = TH1, TH2
    iv = ned & (th >= tl - math.radians(0.5)) & (th <= tr + math.radians(0.5))
    th0 = np.arctan2(OUT[:, 3], OUT[:, 4])
    iv0 = ned & (th0 >= tl - math.radians(0.5)) & (th0 <= tr + math.radians(0.5))
    ris = ut & (IOUT[:, 1] > 0)
    w = 1.0 / N
    thd = np.degrees(th[ned])
    q = np.percentile(thd, [0.5, 2.5, 50, 97.5, 99.5]) if ned.any() else [np.nan] * 5
    return dict(samla=float(1 - (c == 6).mean()), eta_ned=float(ned.sum() * w), eta_opp=float((ut & ~ned).sum() * w),
                renne_tilbake=float((c == 5).sum() * w), fanga=float((c == 3).sum() * w), feil=float((c == 4).sum() * w),
                i_vifta_umatt=float(iv0.sum() * w), utanfor_vifta_umatt=float((ned & ~iv0).sum() * w),
                del_ned_som_traff_stigevegg=float((ned & (IOUT[:, 1] > 0)).sum() / max(ned.sum(), 1)),
                del_utsendt_som_traff_stigevegg=float(((c != 6) & (IOUT[:, 1] > 0)).sum() * w),
                del_ned_avrunding=float((ned & (IOUT[:, 2] > 0)).sum() / max(ned.sum(), 1)),
                stigevegg_i_vifta=float((iv0 & (IOUT[:, 1] > 0)).sum() * w),
                stigevegg_utanfor=float((ned & ~iv0 & (IOUT[:, 1] > 0)).sum() * w),
                theta_kvantil_0_5_2_5_50_97_5_99_5=[float(v) for v in q],
                mot_skjermsida_lt_m35=float((ned & (th < math.radians(-35))).sum() * w),
                mot_brukaren_gt_35=float((ned & (th > math.radians(35))).sum() * w))


def G_tab(OUT, IOUT, N, matt=True, seed=5, bin_deg=0.5):
    ut = IOUT[:, 0] == 0
    th = np.arctan2(OUT[:, 3], OUT[:, 4])[ut]
    if matt:
        th = th + np.random.default_rng(seed).normal(0, SIG, len(th))
    e = np.radians(np.arange(-180, 180.001, bin_deg))
    H, _ = np.histogram(th, e)
    c = (e[:-1] + e[1:]) / 2
    return c, H / N / (e[1] - e[0])           # LED-lm per radian av profilvinkelen (heile kula)


def G_design(matt=True):
    """Designfordelinga (motorens premiss, eigen kode): lambertsk inn med Fresnel per stråle, jamn E ut."""
    ph, th, pi_, tau = DL['ph'], DL['th'], DL['pi'], DL['tau']

    def fr(ci, ct, n1, n2):
        rs = ((n1 * ci - n2 * ct) / (n1 * ci + n2 * ct)) ** 2; rp = ((n1 * ct - n2 * ci) / (n1 * ct + n2 * ci)) ** 2
        return 1 - 0.5 * (rs + rp)
    T1 = fr(np.cos(ph), np.cos(pi_), 1.0, n)
    T2 = fr(np.cos(pi_ - tau), np.cos(th - tau), n, 1.0)
    wph = 0.5 * np.cos(ph) * T1 * T2 * MOTOR['RISS']          # LED-lm per radian av φ (profilmarginal av lambert = ½cos φ)
    e = np.radians(np.arange(-180, 180.001, 0.25)); c = (e[:-1] + e[1:]) / 2
    cum = np.concatenate([[0], np.cumsum(0.5 * (wph[1:] + wph[:-1]) * np.diff(ph))])
    Fe = np.interp(e, th, cum, left=0, right=cum[-1])
    G = np.diff(Fe) / np.diff(e)
    if matt:
        k = np.exp(-0.5 * (np.degrees(c - 0) / math.degrees(SIG)) ** 2); k /= k.sum()
        G = np.convolve(G, k, mode='same')
    return c, G, float(cum[-1])


# ---- fjernfelt (som motoren: linjekjelde langs x, I = G(θ)·(2/π)·cos ξ per eining lengd) ----
def E_fjern(c, G, Q, qn, alfa, nsrc=60):
    xs = (np.arange(nsrc) + .5) / nsrc * L - L / 2
    S = np.c_[xs, np.full(nsrc, YS), np.full(nsrc, ZS)]
    d = Q[None] - S[:, None]
    r = np.linalg.norm(d, axis=-1)
    xi = np.arcsin(np.clip(d[..., 0] / r, -1, 1))
    th = np.arctan2(-d[..., 1], -d[..., 2])
    gam = (th - alfa + np.pi) % (2 * np.pi) - np.pi
    I = np.interp(gam, c, G) * (2 / np.pi) * np.cos(xi) / nsrc
    ci = -(d @ qn) / r
    return np.where(ci > 0, I * ci / r ** 2, 0).sum(0)


def punkt(xg, yg, kind):
    X, Y = np.meshgrid(xg, yg)
    if kind == 'bord':
        return np.c_[X.ravel(), Y.ravel(), np.zeros(X.size)]
    return np.c_[X.ravel(), np.full(X.size, WALL - 1e-3), Y.ravel()]


TASKP, WALLP, DESKP = punkt(TX, TY, 'bord'), punkt(WX, WZ, 'vegg'), punkt(DX_, DY_, 'bord')
UP, MOTB = np.array([0, 0, 1.0]), np.array([0, -1.0, 0])


def fjern_tal(c, G):
    Et = E_fjern(c, G, TASKP, UP, 0.0)
    Phi = E_TASK / Et.mean()
    Ew = E_fjern(c, G, WALLP, MOTB, math.radians(-105)).mean(); Ed = E_fjern(c, G, DESKP, UP, math.radians(-105)).mean()
    Wf = punkt(np.linspace(-0.69, 0.69, 35), np.linspace(0.06, 1.19, 29), 'vegg')
    Ewf = E_fjern(c, G, Wf, MOTB, math.radians(-105)).mean()
    imin = np.argmin(Et)
    return dict(Phi=float(Phi), U0=float(Et.min() / Et.mean()), min_ved=(float(TASKP[imin, 0]), float(TASKP[imin, 1])),
                Ev_stem=float(Ew * Phi * DIM), Ev_stem_heile_feltet=float(Ewf * Phi * DIM), R_stem=float(Ew / (Ew + Ed)))


# ---- nærfelt: strålar ut i scena ----
def ramme(a):
    return np.array([0, -math.cos(a), math.sin(a)]), np.array([0, -math.sin(a), -math.cos(a)])


def boks_t(P, V, lo, hi):
    with np.errstate(divide='ignore', invalid='ignore'):
        t1 = (np.array(lo)[None] - P) / V; t2 = (np.array(hi)[None] - P) / V
    tmin = np.nanmax(np.minimum(t1, t2), axis=1); tmax = np.nanmin(np.maximum(t1, t2), axis=1)
    return np.where((tmax >= np.maximum(tmin, 0)) & (tmax > 0), np.maximum(tmin, 0), np.inf)


def scene(OUT, IOUT, N, alfa, matt=True, seed=11, hindringar=(COL,), sig=SIG):
    rng = np.random.default_rng(seed)
    ut = IOUT[:, 0] == 0
    o = OUT[ut]
    x0 = (rng.random(len(o)) - 0.5) * L
    xe = x0 + o[:, 5]
    kinn = np.abs(xe) > L / 2
    ds, dz = o[:, 3], o[:, 4]
    if matt:
        g = rng.normal(0, sig, len(o)); cg, sg = np.cos(g), np.sin(g)
        ds, dz = ds * cg + dz * sg, -ds * sg + dz * cg
    fr, ne = ramme(alfa)
    P = np.c_[xe, YS + o[:, 0] * fr[1] + o[:, 1] * ne[1], ZS + o[:, 0] * fr[2] + o[:, 1] * ne[2]]
    V = np.c_[o[:, 2], ds * fr[1] + dz * ne[1], ds * fr[2] + dz * ne[2]]
    V /= np.linalg.norm(V, axis=1, keepdims=True)
    w = np.full(len(o), 1.0 / N); w[kinn] = 0.0
    with np.errstate(divide='ignore', invalid='ignore'):
        td = np.where(V[:, 2] < 0, -P[:, 2] / V[:, 2], np.inf)
        tw = np.where(V[:, 1] > 0, (WALL - P[:, 1]) / V[:, 1], np.inf)
        ts = np.where(np.abs(V[:, 1]) > 1e-12, (SY - P[:, 1]) / V[:, 1], np.inf)
        te = np.where(V[:, 1] < 0, (EYES[0, 1] - P[:, 1]) / V[:, 1], np.inf)
    ts = np.where(ts > 1e-9, ts, np.inf)
    Ps = P + np.where(np.isfinite(ts), ts, 0)[:, None] * V
    on = np.isfinite(ts) & (Ps[:, 0] > SX0) & (Ps[:, 0] < SX1) & (Ps[:, 2] > SZ0) & (Ps[:, 2] < SZ1)
    ts = np.where(on, ts, np.inf)
    tb = np.full(len(o), np.inf)
    for lo, hi in hindringar:
        tb = np.minimum(tb, boks_t(P, V, lo, hi))
    t = np.minimum.reduce([td, tw, ts, tb])
    Q = P + np.where(np.isfinite(t), t, 0)[:, None] * V
    kind = np.select([t == ts, t == tb, t == td, t == tw], [1, 4, 2, 3], 0)
    kind[~np.isfinite(t)] = 0
    # auga: vindauge ±3 cm i planet y = -0,30 (andletet ser mot +y), berre om strålen ikkje er stoppa før
    Pe = P + np.where(np.isfinite(te), te, 0)[:, None] * V
    he = 0.03
    eye = np.isfinite(te) & (te < t) & (np.abs(Pe[:, 0] - EYES[0, 0]) < he) & (np.abs(Pe[:, 2] - EYES[0, 2]) < he)
    return dict(Q=Q, kind=kind, w=w, V=V, eye_E=float(w[eye].sum() / (2 * he) ** 2), kinn=float(kinn.mean() * ut.sum() / N))


def celle_E(Qa, Qb, w, ga, gb, h):
    """Illuminans i kvadratiske celler ±h rundt gitterpunkta (ga × gb)."""
    ia = np.rint((Qa - ga[0]) / (ga[1] - ga[0])).astype(int); ib = np.rint((Qb - gb[0]) / (gb[1] - gb[0])).astype(int)
    ok = (ia >= 0) & (ia < len(ga)) & (ib >= 0) & (ib < len(gb))
    ok[ok] &= (np.abs(Qa[ok] - ga[ia[ok]]) < h) & (np.abs(Qb[ok] - gb[ib[ok]]) < h)
    E = np.bincount(ib[ok] * len(ga) + ia[ok], weights=w[ok], minlength=len(ga) * len(gb))
    return E.reshape(len(gb), len(ga)) / (2 * h) ** 2


def naer_tal(OUT, IOUT, N, matt=True, sig=SIG):
    A = scene(OUT, IOUT, N, 0.0, matt, sig=sig)
    d = A['kind'] == 2
    Et = celle_E(A['Q'][d, 0], A['Q'][d, 1], A['w'][d], TX, TY, 0.015)
    rect = d & (np.abs(A['Q'][:, 0]) <= 0.30) & (A['Q'][:, 1] >= 0.05) & (A['Q'][:, 1] <= 0.40)
    Phi = E_TASK / Et.mean()
    sc = (A['kind'] == 1) & (A['V'][:, 1] > 0)
    Asc = (SX1 - SX0) * (SZ1 - SZ0)
    gx = SX0 + (np.arange(11) + .5) * 0.05; gz = SZ0 + (np.arange(8) + .5) * 0.04
    Esc = celle_E(A['Q'][sc, 0], A['Q'][sc, 2], A['w'][sc], gx, gz, 0.02)
    M = scene(OUT, IOUT, N, math.radians(-105), matt, sig=sig)
    wv = M['kind'] == 3; dd = M['kind'] == 2
    Ew = celle_E(M['Q'][wv, 0], M['Q'][wv, 2], M['w'][wv], WX, WZ, 0.025)
    Ed = celle_E(M['Q'][dd, 0], M['Q'][dd, 1], M['w'][dd], DX_, DY_, 0.025)
    felt = wv & (np.abs(M['Q'][:, 0]) <= 0.70) & (M['Q'][:, 2] >= 0.05) & (M['Q'][:, 2] <= 1.20)
    Ew_fin = M['w'][felt].sum() / (1.4 * 1.15)
    F = scene(OUT, IOUT, N, math.radians(70), matt, sig=sig)
    imin = np.unravel_index(np.argmin(Et), Et.shape)
    return dict(E_rel_rutenett=np.round(Et / Et.mean(), 2).tolist(), min_ved=(float(TX[imin[1]]), float(TY[imin[0]])),
                Phi=float(Phi), U0=float(Et.min() / Et.mean()), Phi_heile_sona=float(E_TASK / (A['w'][rect].sum() / 0.21)),
                E_skjerm_snitt=float(A['w'][sc].sum() / Asc * Phi), E_skjerm_maks_celle=float(Esc.max() * Phi),
                del_paa_skjerm=float(A['w'][sc].sum()), del_paa_oppgava=float(A['w'][rect].sum()), kinn=A['kinn'],
                R_stem=float(Ew.mean() / (Ew.mean() + Ed.mean())), Ev_stem=float(Ew.mean() * Phi * DIM),
                Lv_stem=float(RHO_VEGG * Ew.mean() * Phi * DIM / math.pi), Ev_stem_heile_feltet=float(Ew_fin * Phi * DIM),
                del_paa_veggfeltet_stem=float(M['w'][felt].sum()), del_soyle_stem=float(M['w'][M['kind'] == 4].sum()),
                E_ansikt_per_lm=F['eye_E'], Phi150=float(E_FACE / F['eye_E']) if F['eye_E'] > 0 else None)


# ---- luminans: bakoversporing frå auga ----
def luminans(Pr, w, alfa, eye, xt, ns=480, per=400, matt=True, seed=3, smax=0.12, sig=SIG):
    """Luminans av hovudet sett frå auga, som funksjon av sikta punkt s i planet rett under rillene (x = xt).
    Strålen startar i det planet (ikkje i auga), slik at matteringa (gauss σ 4° i profilvinkelen, motorens premiss)
    verkar ved plata. Utanfor plata (|s| > 8 cm) ingen mattering: der ser auget forbi kanten, inn mot renna.
    Eining: delen av LED-luminansen (radians av stripa)."""
    rng = np.random.default_rng(seed)
    fr, ne = ramme(alfa)
    O = np.array([0, YS, ZS])
    el = np.array([eye[0], (eye - O) @ fr, (eye - O) @ ne])
    zq = ZB + Pr['hmax'] + 0.0005
    sb = np.linspace(-smax, smax, ns + 1)
    st = rng.uniform(np.repeat(sb[:-1], per), np.repeat(sb[1:], per))
    Dl = np.c_[np.full(len(st), xt - el[0]), st - el[1], np.full(len(st), zq - el[2])]
    Dl /= np.linalg.norm(Dl, axis=1, keepdims=True)
    if matt:
        g = rng.normal(0, sig, len(Dl)) * (np.abs(st) <= BP / 2); cg, sg = np.cos(g), np.sin(g)
        Dl[:, 1], Dl[:, 2] = Dl[:, 1] * cg + Dl[:, 2] * sg, -Dl[:, 1] * sg + Dl[:, 2] * cg
    P = np.ascontiguousarray(np.c_[st, np.full(len(st), zq)])
    RES = np.zeros(len(Dl))
    bakover(P, np.ascontiguousarray(Dl), np.full(len(Dl), xt), w, seed, Pr['SA'], Pr['SB'], Pr['TYP'], Pr['B0'], Pr['BI'],
            Pr['p'], Pr['K'], Pr['hmax'], RES)
    prof = RES.reshape(ns, per).mean(1)
    return (sb[:-1] + sb[1:]) / 2, prof


def L_tal(sc, prof):
    """Toppar (glidande snitt over 1 mm og 1 cm) på plata og utanfor kanten, og snitt over plata. Delar av L_LED."""
    h = sc[1] - sc[0]
    paa = np.abs(sc) <= BP / 2
    m1 = np.convolve(prof, np.ones(max(1, int(round(0.001 / h)))) / max(1, int(round(0.001 / h))), mode='same')
    m10 = np.convolve(prof, np.ones(int(round(0.01 / h))) / int(round(0.01 / h)), mode='same')
    pp = np.where(paa, prof, 0)
    lit = pp > 0.05 * pp.max() if pp.max() > 0 else pp > 1
    return dict(topp_1mm=float(m1[paa].max()), topp_1cm=float(m10[paa].max()), snitt_plata=float(prof[paa].mean()),
                kant_1mm=float(m1[~paa].max()), s_topp_cm=float(sc[paa][np.argmax(m1[paa])] * 100),
                breidd_lysande_cm=float(lit.sum() * h * 100))


# ---------------- køyring ----------------
if __name__ == '__main__':
    UT = {}
    def skriv(*a):
        print(*a, flush=True)

    # 0) designlova mot motoren
    UT['design'] = dict(tau_min=float(np.degrees(DL['tau'].min())), tau_maks=float(np.degrees(DL['tau'].max())),
                        phi_maks=float(np.degrees(DL['phm'])), vifte=(float(np.degrees(TH1)), float(np.degrees(TH2))),
                        avbøying_kant_deg=float(np.degrees(DL['ph'][-1] - DL['th'][-1])),
                        innfall_maks=float(np.degrees(np.abs(DL['pi'] - DL['tau']).max())))
    skriv('design', UT['design'])
    cD, GD, etaD = G_design(True)
    UT['design']['eta_design_inkl_RISS'] = etaD
    UT['fjern_design'] = fjern_tal(cD, GD)
    skriv('fjernfelt med designfordelinga (skal gje motoren):', UT['fjern_design'], 'η', etaD)

    # 1) prøvar: flat plate (τ = 0) og designkontroll (2D, w = 0, berre strålar med 2 brytingar)
    flat = dict(profil(0.0008))
    flat.update(SA=np.array([[-BP / 2, ZB]]), SB=np.array([[BP / 2, ZB]]), TYP=np.array([2], np.int64), hmax=0.0,
                B0=np.arange(flat['K'] + 1, dtype=np.int64), BI=np.zeros(flat['K'], np.int64))
    tr = []
    for sd in range(20000):
        c, s, z, dx, ds, dz, xs, nr, nf, nfa, nbb = kjerne(0.0, 0.0, 0.0, 0.0, 1.0, flat['SA'], flat['SB'], flat['TYP'], flat['B0'], flat['BI'],
                                                          flat['p'], flat['K'], flat['hmax'], 60)
        tr.append(c == 0 and dz > 0)
    R0 = ((n - 1) / (n + 1)) ** 2
    UT['prove_flat'] = dict(T_mc=float(np.mean(tr)), T_teori_fleire_sprett=float((1 - R0) / (1 + R0)), T_teori_to_flater=float((1 - R0) ** 2))
    skriv('prøve flat plate, normalt innfall:', UT['prove_flat'])
    rng = np.random.default_rng(1); avv = []
    for i in range(3000):
        u1, u2 = rng.random(), rng.random()
        st, dz0 = math.sqrt(u1) * 0.8, None
        dx0, ds0 = st * math.cos(2 * math.pi * u2), st * math.sin(2 * math.pi * u2); dz0 = math.sqrt(1 - dx0 ** 2 - ds0 ** 2)
        c, s, z, dx, ds, dz, xs, nr, nf, nfa, nbb = kjerne(0.0, 0.0, dx0, ds0, dz0, flat['SA'], flat['SB'], flat['TYP'], flat['B0'], flat['BI'],
                                                          flat['p'], flat['K'], flat['hmax'], 60)
        if c == 0 and dz > 0:
            avv.append(math.degrees(math.acos(min(1.0, dx * dx0 + ds * ds0 + dz * dz0))))
    UT['prove_flat']['skeiv_maks_avvik_deg'] = float(max(avv))
    skriv('skeive strålar gjennom flat plate, største avvik ut/inn (grader):', max(avv))

    # 2) strålesporaren, variantar
    N = 1_200_000
    VAR = [('2D_w0_loddrett', dict(), 0.0, False), ('3D_w0_loddrett', dict(), 0.0, True), ('3D_w5_loddrett', dict(), 0.005, True),
           ('3D_w10_loddrett', dict(), 0.010, True), ('2D_w0_slipp', dict(slipp='slipp'), 0.0, False), ('3D_w5_slipp', dict(slipp='slipp'), 0.005, True),
           ('3D_w10_slipp', dict(slipp='slipp'), 0.010, True), ('3D_w5_loddrett_r10', dict(r=10e-6), 0.005, True),
           ('3D_w5_slipp_r10', dict(slipp='slipp', r=10e-6), 0.005, True), ('3D_w5_loddrett_p04', dict(p=0.0004), 0.005, True),
           ('3D_w5_loddrett_topp', dict(kart='topp'), 0.005, True)]
    PROF = {}
    UT['spor'] = {}; GT = {}; LAGRA = {}
    for nm, kw, w, d3 in VAR:
        t1 = time.time()
        Pr = PROF.setdefault(json.dumps(kw, sort_keys=True), profil(**kw))
        OUT, IOUT = spor(Pr, N, w, d3, seed=7)
        b = budsjett(OUT, IOUT, N)
        b['hmax_mm'] = Pr['hmax'] * 1000; b['segment'] = int(len(Pr['SA']))
        c, G = G_tab(OUT, IOUT, N)
        GT[nm] = (c, G)
        b['fjern'] = fjern_tal(c, G)
        if d3 and nm in ('3D_w0_loddrett', '3D_w5_loddrett', '3D_w10_loddrett', '3D_w5_slipp', '3D_w10_slipp', '3D_w5_loddrett_r10', '3D_w5_slipp_r10'):
            b['naer'] = naer_tal(OUT, IOUT, N)
        UT['spor'][nm] = b
        b['beta_maks_deg'] = float(np.degrees(Pr['beta'].max()))
        if nm in ('3D_w5_loddrett', '3D_w10_loddrett', '3D_w5_slipp', '3D_w10_slipp'):
            LAGRA[nm] = (OUT, IOUT)
        skriv(f'{nm:24s} {time.time()-t1:5.1f}s', json.dumps(b, ensure_ascii=False))

    # designkontroll: 2D, w 0, strålar som gjekk gjennom nøyaktig to flater og ingen stigevegg: θ ut mot designlova
    Pr = PROF[json.dumps({}, sort_keys=True)]
    OUT, IOUT = spor(Pr, 200_000, 0.0, False, seed=9)
    ok = (IOUT[:, 0] == 0) & (IOUT[:, 4] == 2) & (IOUT[:, 1] == 0) & (OUT[:, 4] > 0)
    # inngangsvinkelen frå utgangspunktet er ikkje lagra; bruk monotoni: sorter etter utgangsstad s og samanlikn med θ(s) i lova
    th_ut = np.degrees(np.arctan2(OUT[ok, 3], OUT[ok, 4]))
    s_ut = OUT[ok, 0]
    th_lov = np.degrees(np.interp(s_ut, DL['s_bot'], DL['th']))
    UT['designkontroll'] = dict(n=int(ok.sum()), avvik_median_deg=float(np.median(np.abs(th_ut - th_lov))),
                                avvik_95_deg=float(np.percentile(np.abs(th_ut - th_lov), 95)))
    skriv('designkontroll (θ ut mot lova, reine to-flate-strålar):', UT['designkontroll'])

    # stigeveggtreff som funksjon av s (3D, w 5, loddrett): kor på plata tapet sit
    Pr = PROF[json.dumps({}, sort_keys=True)]
    OUT, IOUT = spor(Pr, N, 0.005, True, seed=13)
    ut = IOUT[:, 0] == 0
    th = np.arctan2(OUT[:, 3], OUT[:, 4]); ned = ut & (np.cos(th) > 0)
    iv = ned & (th >= TH1 - math.radians(.5)) & (th <= TH2 + math.radians(.5))
    sb = np.linspace(-BP / 2, BP / 2, 9)
    rad = []
    for a, b_ in zip(sb[:-1], sb[1:]):
        m = ned & (OUT[:, 0] >= a) & (OUT[:, 0] < b_)
        rad.append(dict(s_cm=f'{a*100:+.0f}..{b_*100:+.0f}', del_av_ned=float(m.sum() / ned.sum()), stigevegg=float((m & (IOUT[:, 1] > 0)).sum() / max(m.sum(), 1)),
                        i_vifta=float((m & iv).sum() / max(m.sum(), 1))))
    UT['stigevegg_per_sone'] = rad
    skriv('stigeveggtreff per sone (3D w5):', rad)

    # 3) luminans mot auga (bakover), α +70 (ansikt) og α 0 (arbeid). Fire syn: tre auge rett fram (x = auge-x) og
    #    midtauga skrått mot enden av plata (x = 0,25). Absolutte tal med Φ frå nærfeltet til same variant.
    UT['luminans'] = {}; PROFIL = {}
    SYN = [(EYES[0], 0.0), (EYES[1], -0.15), (EYES[2], 0.15), (EYES[0], 0.25)]
    for nm, kw in (('loddrett', {}), ('slipp', dict(slipp='slipp'))):
        Pr = PROF[json.dumps(kw, sort_keys=True)]
        for w in (0.005, 0.010):
            vn = f'3D_w{int(w*1000)}_{nm}'
            Phi_a, Phi_f = UT['spor'][vn]['naer']['Phi'], UT['spor'][vn]['naer']['Phi150']
            LL = 1 / (math.pi * w * L)                      # cd/m² per LED-lm for ei jamn lambertsk stripe
            for stl, a, Phi in (('ansikt_+70', 70.0, Phi_f), ('arbeid_0', 0.0, Phi_a)):
                for matt in (False, True):
                    best = None; kant = 0.0
                    for vi, (eye, xt) in enumerate(SYN):
                        sc, prof = luminans(Pr, w, math.radians(a), eye, xt, matt=matt, seed=3 + vi)
                        r = L_tal(sc, prof)
                        r['syn'] = vi; kant = max(kant, r['kant_1mm'])
                        if best is None or r['topp_1mm'] > best['topp_1mm']:
                            best = r; PROFIL[f'{nm}_w{int(w*1000)}_{stl}_{"matt" if matt else "blank"}'] = (sc, prof * LL * Phi)
                    best['kant_1mm'] = kant
                    for k in ('topp_1mm', 'topp_1cm', 'snitt_plata', 'kant_1mm'):
                        best[k + '_cdm2'] = best[k] * LL * Phi
                    best.update(Phi=Phi, L_LED_cdm2=LL * Phi)
                    key = f'{nm}_w{int(w*1000)}_{stl}_{"matt" if matt else "blank"}'
                    UT['luminans'][key] = best
                    skriv(key, {k: round(v, 3) if isinstance(v, float) else v for k, v in best.items()})
    # 3b) sterkare mattering: kva σ trengst for ansiktstoppen under 3000 cd/m², og kva kostar det i arbeid?
    UT['mattering'] = {}
    for pn, kw, sgd in (('loddrett', {}, 4.0), ('loddrett', {}, 6.0), ('loddrett', {}, 8.0), ('slipp', dict(slipp='slipp'), 4.0), ('slipp', dict(slipp='slipp'), 6.0)):
        Pr = PROF[json.dumps(kw, sort_keys=True)]
        sg_ = math.radians(sgd)
        rr = {}
        for w in (0.005, 0.010):
            vn = f'3D_w{int(w*1000)}_{pn}'
            OUTv, IOUTv = LAGRA[vn]
            q = naer_tal(OUTv, IOUTv, N, sig=sg_)
            LL = 1 / (math.pi * w * L)
            topp = 0.0
            for vi, (eye, xt) in enumerate(SYN):
                sc, prof = luminans(Pr, w, math.radians(70.0), eye, xt, matt=True, seed=30 + vi, sig=sg_)
                topp = max(topp, L_tal(sc, prof)['topp_1mm'])
            topp_a = 0.0
            for vi, (eye, xt) in enumerate(SYN):
                sc, prof = luminans(Pr, w, 0.0, eye, xt, matt=True, seed=40 + vi, sig=sg_)
                topp_a = max(topp_a, L_tal(sc, prof)['topp_1mm'])
            rr[f'w{int(w*1000)}'] = dict(Phi=q['Phi'], U0=q['U0'], E_skjerm=q['E_skjerm_snitt'], E_skjerm_maks=q['E_skjerm_maks_celle'],
                                        Phi150=q['Phi150'], L_ansikt_topp_1mm=topp * LL * q['Phi150'], L_arbeid_topp_1mm=topp_a * LL * q['Phi'],
                                        Ev_stem=q['Ev_stem'], R_stem=q['R_stem'])
        UT['mattering'][f'{pn}_sigma_{sgd:.0f}'] = rr
        skriv(f'mattering {pn} σ {sgd:.0f}°:', json.dumps(rr, ensure_ascii=False))
    # fjernfelt-skjerm (motorens metode) med design-G og spora G, for å skilje nærfelt frå fordeling
    SKP = np.array([[x, SY - 1e-4, z] for z in SZ0 + (np.arange(16) + .5) / 16 * (SZ1 - SZ0) for x in SX0 + (np.arange(22) + .5) / 22 * (SX1 - SX0)])
    UT['skjerm_fjern'] = {}
    for nm_, (c_, G_) in (('design', (cD, GD)), ('3D_w5_loddrett', GT['3D_w5_loddrett']), ('3D_w5_slipp', GT['3D_w5_slipp'])):
        Es = E_fjern(c_, G_, SKP, MOTB, 0.0)
        Phi_ = E_TASK / E_fjern(c_, G_, TASKP, UP, 0.0).mean()
        UT['skjerm_fjern'][nm_] = dict(E_snitt=float(Es.mean() * Phi_), E_maks=float(Es.max() * Phi_), Phi=float(Phi_))
    skriv('skjerm i fjernfelt:', UT['skjerm_fjern'])

    # direkte innsyn til LED-stripa forbi plata (arbeid): geometri utan plate i vegen, frå midtauga
    UT['innsyn_kant'] = {}
    for w in (0.0, 0.005, 0.010):
        fr, ne = ramme(0.0)
        e = EYES[0] - np.array([0, YS, ZS]); se, ze = e @ fr, e @ ne
        ss = np.linspace(-w / 2, w / 2, 2001) if w > 0 else np.array([0.0])
        synleg = []
        for s0 in ss:
            # line frå LED-punkt (s0, 0) til auga: renneopning ved z = ZC og forbi platekanten (z = D, |s| > BP/2)?
            k = (se - s0) / (ze - 0.0)
            s5 = s0 + k * ZC; sD = s0 + k * D; sB = s0 + k * (ZB + 0.002)
            synleg.append(abs(s5) < CW and (abs(sD) > BP / 2) and (abs(sB) > BP / 2))
        synleg = np.array(synleg)
        UT['innsyn_kant'][f'w{int(w*1000)}'] = dict(synleg_del_av_stripa=float(synleg.mean()), synleg_breidd_mm=float(synleg.mean() * w * 1000),
                                                     siktvinkel_deg=float(np.degrees(math.atan2(se, ze))))
    skriv('innsyn forbi platekanten:', UT['innsyn_kant'])

    # kollisjon i stemningsgesten (utanfor linsa, enkel kontroll): plateovekanten mot armen
    kol = []
    for a in range(0, -131, -5):
        fr, ne = ramme(math.radians(a))
        for sv in (-BP / 2, BP / 2):
            for zz in (D, ZB):
                P = np.array([0, YS, ZS]) + sv * fr + zz * ne
                if ARM[0][1] <= P[1] <= ARM[1][1] and ARM[0][2] <= P[2] <= ARM[1][2]:
                    kol.append(a)
    UT['kollisjon_arm_forste_alfa'] = max(kol) if kol else None
    skriv('plata i armen frå α =', UT['kollisjon_arm_forste_alfa'])

    # G(θ)-tabell til md / figur
    UT['G'] = {k: dict(theta_deg=[float(v) for v in np.degrees(c[::4])], G=[float(v) for v in G[::4]]) for k, (c, G) in GT.items()
               if k in ('2D_w0_loddrett', '3D_w5_loddrett', '3D_w10_loddrett', '3D_w5_slipp')}
    UT['G']['design'] = dict(theta_deg=[float(v) for v in np.degrees(cD[::8])], G=[float(v) for v in GD[::8]])
    UT['motor_pastand'] = MOTOR
    # figur: G(θ) og luminansprofil
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        plt.rcParams.update({'figure.facecolor': 'black', 'axes.facecolor': 'black', 'savefig.facecolor': 'black', 'text.color': '#ddd',
                             'axes.labelcolor': '#ddd', 'xtick.color': '#aaa', 'ytick.color': '#aaa', 'axes.edgecolor': '#555', 'font.size': 9})
        fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
        for k, col, lab in (('design', '#888', 'designlova (motoren)'), ('2D_w0_loddrett', '#6fa8dc', '2D, line, loddrett stigevegg'),
                            ('3D_w5_loddrett', '#e69138', '3D, 5 mm, loddrett'), ('3D_w5_slipp', '#93c47d', '3D, 5 mm, slipp')):
            if k == 'design':
                c_, G_ = cD, GD
            else:
                c_, G_ = GT[k]
            ax[0].semilogy(np.degrees(c_), np.maximum(G_ / G_.max(), 1e-4), color=col, lw=1.2, label=lab)
        for v in (TH1, TH2):
            ax[0].axvline(np.degrees(v), color='#444', lw=0.8)
        ax[0].axvspan(-39.4, -21.0, color='#3d1f1f', lw=0); ax[0].axvline(64.3, color='#a33', lw=0.8, ls=':')
        ax[0].set_xlim(-90, 90); ax[0].set_ylim(1e-4, 1.3); ax[0].set_xlabel('θ, profilvinkel frå loddrett (°), + mot brukaren'); ax[0].set_ylabel('G / G maks')
        ax[0].legend(frameon=False, fontsize=8, loc='lower center'); ax[0].set_title('vinkelfordeling ut av plata (raudt felt: skjermen, prikk: auga)', fontsize=9)
        for k, col, lab in (('loddrett_w5_ansikt_+70_blank', '#777', 'ansikt, blank'), ('loddrett_w5_ansikt_+70_matt', '#e69138', 'ansikt, 4° matt'),
                            ('loddrett_w10_ansikt_+70_matt', '#f6b26b', 'ansikt, 4° matt, 10 mm')):
            if k in PROFIL:
                sc_, pr_ = PROFIL[k]; ax[1].plot(sc_ * 100, pr_, color=col, lw=1, label=lab)
        ax[1].axhline(L_MAX, color='#a33', lw=0.8, ls=':'); ax[1].set_xlim(-12, 12); ax[1].set_xlabel('sikta punkt s på plata (cm)'); ax[1].set_ylabel('cd/m²')
        ax[1].legend(frameon=False, fontsize=8); ax[1].set_title('luminans mot auga, ansiktslys α +70°, Φ for 150 lx', fontsize=9)
        for k, col, lab in (('loddrett_w5_arbeid_0_matt', '#e69138', 'arbeid, 5 mm, loddrett'), ('loddrett_w10_arbeid_0_matt', '#f6b26b', 'arbeid, 10 mm, loddrett'),
                            ('slipp_w5_arbeid_0_matt', '#93c47d', 'arbeid, 5 mm, slipp')):
            if k in PROFIL:
                sc_, pr_ = PROFIL[k]; ax[2].semilogy(sc_ * 100, np.maximum(pr_, 1), color=col, lw=1, label=lab)
        ax[2].axhline(L_MAX, color='#a33', lw=0.8, ls=':'); ax[2].axvline(8, color='#444', lw=0.8); ax[2].axvline(-8, color='#444', lw=0.8)
        ax[2].set_xlim(-12, 12); ax[2].set_ylim(1, 1e5); ax[2].set_xlabel('sikta punkt s (cm), |s| > 8: forbi platekanten'); ax[2].set_ylabel('cd/m²')
        ax[2].legend(frameon=False, fontsize=8); ax[2].set_title('luminans mot auga i arbeid α 0°, 4° matt', fontsize=9)
        fig.tight_layout(); fig.savefig(os.path.join(HER, 'prisme.png'), dpi=130); plt.close(fig)
    except Exception as ex:
        skriv('figur feila:', repr(ex))
    UT['tid_s'] = time.time() - T0
    json.dump(UT, open(os.path.join(HER, 'prisme.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    skriv(f'skrive prisme.json ({time.time()-T0:.0f} s)')
