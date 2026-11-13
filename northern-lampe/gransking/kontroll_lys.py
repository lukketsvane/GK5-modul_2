# -*- coding: utf-8 -*-
"""Gransking (premiss-linsa): uavhengig lysrekning for (a) bru, (b) krok, (c) flak.
Eigen kode. Scena og parametrane er skrivne av fraa felles.py / motorane som TAL, ingen funksjonskall dit.
Koeyr: PYTHONIOENCODING=utf-8 python kontroll_lys.py
"""
import math, json
import numpy as np

# ---- scene (tal fraa felles.py l.17-27) ----
SX0, SX1, SY, SZ0, SZ1 = -0.275, 0.275, 0.45, 0.10, 0.42
WALL = 0.75
EYE = np.array([0.0, -0.30, 0.45])
EYES = [EYE, np.array([-0.15, -0.30, 0.45]), np.array([0.15, -0.30, 0.45])]
R_TUBE, BETA = 0.022, math.radians(25.0)
RHO = 0.85


def hidden_by_screen(p, q):
    """True der strekninga p->q kryssar skjermrektangelet (plan y=SY). p (n,3), q (m,3) -> (n,m)."""
    dy = q[None, :, 1] - p[:, None, 1]
    with np.errstate(divide="ignore", invalid="ignore"):
        s = (SY - p[:, None, 1]) / dy
    x = p[:, None, 0] + s * (q[None, :, 0] - p[:, None, 0])
    z = p[:, None, 2] + s * (q[None, :, 2] - p[:, None, 2])
    return (s > 0) & (s < 1) & (x > SX0) & (x < SX1) & (z > SZ0) & (z < SZ1)


def E_unit(src, Q, qn, screen=True):
    """lx per (cd/m2) paa punkt Q med normal qn fraa lambertske flatebitar src=(P,N,dA)."""
    P, N, dA = src
    out = np.zeros(len(Q))
    for i0 in range(0, len(Q), 1500):
        q = Q[i0:i0 + 1500]
        v = q[None] - P[:, None]                       # fraa kjelde til mottakar
        d2 = np.einsum("ijk,ijk->ij", v, v)
        d = np.sqrt(d2)
        c_ut = np.einsum("ijk,ik->ij", v, N) / d
        c_inn = -(v @ qn) / d
        g = np.where((c_ut > 0) & (c_inn > 0), c_ut * c_inn / d2, 0.0)
        if screen:
            g = np.where(hidden_by_screen(P, q), 0.0, g)
        out[i0:i0 + 1500] = (g * dA[:, None]).sum(0)
    return out


def slot(yp, hp, psi_deg, xr, nx_per_m=300, nw=3):
    """Kordeopning i roeyr D44: plan i avstand R cos(beta) fraa aksen, breidd 2 R sin(beta). xr: liste av (x0,x1)."""
    ps = math.radians(psi_deg)
    n = np.array([0.0, -math.sin(ps), -math.cos(ps)])            # 0: ned, +: mot brukar, -: mot vegg
    t = np.array([0.0, math.cos(ps), -math.sin(ps)])
    c = np.array([0.0, yp, hp]) + R_TUBE * math.cos(BETA) * n
    hw = R_TUBE * math.sin(BETA)
    P, dA = [], []
    for x0, x1 in xr:
        k = max(2, int(round((x1 - x0) * nx_per_m)))
        xs = x0 + (np.arange(k) + 0.5) * (x1 - x0) / k
        for j in range(nw):
            w = (-1 + (2 * j + 1) / nw) * hw
            P.append(c[None] + np.c_[xs, np.zeros(k), np.zeros(k)] + w * t[None])
            dA.append(np.full(k, (x1 - x0) / k * 2 * hw / nw))
    P = np.vstack(P); dA = np.concatenate(dA)
    return P, np.tile(n, (len(P), 1)), dA


def panel(yp, zp, alpha_deg, L=0.60, b=0.25, nx=40, nb=16):
    a = math.radians(alpha_deg)
    f = np.array([0.0, -math.cos(a), math.sin(a)])               # framkant
    n = np.array([0.0, -math.sin(a), -math.cos(a)])              # lysnormal
    xs = (np.arange(nx) + 0.5) / nx * L - L / 2
    ss = ((np.arange(nb) + 0.5) / nb - 0.5) * b
    X, S = np.meshgrid(xs, ss)
    P = np.array([0.0, yp, zp])[None] + np.c_[X.ravel(), np.zeros(X.size), np.zeros(X.size)] + S.ravel()[:, None] * f[None]
    return P, np.tile(n, (len(P), 1)), np.full(len(P), L / nx * b / nb)


def grid(x0, x1, nx, a0, a1, na, plane, const):
    gx, ga = np.meshgrid(np.linspace(x0, x1, nx), np.linspace(a0, a1, na))
    if plane == "bord":
        return np.c_[gx.ravel(), ga.ravel(), np.full(gx.size, const)]
    return np.c_[gx.ravel(), np.full(gx.size, const), ga.ravel()]


UP, TOEYE, TOROOM = np.array([0, 0, 1.0]), np.array([0, 1.0, 0]), np.array([0, -1.0, 0])
TASK35 = grid(-0.30, 0.30, 7, 0.05, 0.40, 5, "bord", 0.0)            # rutenettet i felles.py
TASKD = grid(-0.30, 0.30, 61, 0.05, 0.40, 36, "bord", 0.0)           # tett: 1 cm
WALL48 = grid(-0.70, 0.70, 8, 0.05, 1.20, 6, "vegg", WALL - 1e-3)
DESK40 = grid(-0.68, 0.68, 8, 0.02, 0.73, 5, "bord", 0.0)


def cell_grid(x0, x1, nx, a0, a1, na, plane, const):
    """cellesenter + celleareal, til fluksintegral."""
    xs = x0 + (np.arange(nx) + 0.5) * (x1 - x0) / nx
    as_ = a0 + (np.arange(na) + 0.5) * (a1 - a0) / na
    gx, ga = np.meshgrid(xs, as_)
    dA = (x1 - x0) / nx * (a1 - a0) / na
    if plane == "bord":
        return np.c_[gx.ravel(), ga.ravel(), np.full(gx.size, const)], dA
    return np.c_[gx.ravel(), np.full(gx.size, const), ga.ravel()], dA


def seen(src, eyes=EYES):
    P, N, _ = src
    for e in eyes:
        front = ((e[None] - P) * N).sum(1) > 0
        if (front & ~hidden_by_screen(P, e[None])[:, 0]).any():
            return True
    return False


def eta_cavity(A_ap, Lcav):
    """Same formel som form01/motor.py l.62-67, rekna paa nytt her."""
    f = A_ap / (2 * math.pi * R_TUBE * Lcav + 2 * math.pi * R_TUBE ** 2)
    sb = math.sin(BETA)
    return sb + (1 - sb) * RHO * f / (1 - RHO * (1 - f)), f


def row(src, eta, task=TASK35):
    A = src[2].sum()
    k = eta / (math.pi * A)                                        # cd/m2 per LED-lm
    Et = E_unit(src, task, UP) * k
    Ew = E_unit(src, WALL48, TOROOM) * k
    Ed = E_unit(src, DESK40, UP) * k
    face = E_unit(src, EYE[None], TOEYE)[0]
    return dict(k=k, A=A, Em=Et.mean(), Emin=Et.min(), U0=Et.min() / max(Et.mean(), 1e-12), Ew=Ew.mean(), Ed=Ed.mean(),
                R=Ew.mean() / max(Ew.mean() + Ed.mean(), 1e-12), face=face, vis=seen(src))


def flux_budget(srcM, LM):
    wq, wa = cell_grid(-0.70, 0.70, 112, 0.0, 1.20, 96, "vegg", WALL - 1e-3)
    dq, da = cell_grid(-0.70, 0.70, 112, 0.0, 0.75, 60, "bord", 0.0)
    wq2, wa2 = cell_grid(-3.0, 3.0, 240, 0.0, 1.65, 66, "vegg", WALL - 1e-3)     # heile veggen, tak 2,4 m over golv
    Ewall = E_unit(srcM, wq, TOROOM) * LM
    lm_w = Ewall.sum() * wa
    lm_d = (E_unit(srcM, dq, UP) * LM).sum() * da
    lm_w2 = (E_unit(srcM, wq2, TOROOM) * LM).sum() * wa2
    return lm_w, lm_d, lm_w2, float(Ewall.max()), float(Ewall.mean())


OUT = {}
SCRQ, _ = cell_grid(SX0, SX1, 22, SZ0, SZ1, 16, "vegg", SY - 1e-4)

# ================= (a) bru og (b) krok =================
konf = {
    "a": dict(yp=0.18, hp=0.62, xr=[(-0.315, 0.315)], Lcav=1.12 * 0.536, A_eta=0.63 * 2 * R_TUBE * math.sin(BETA)),
    "b": dict(yp=0.25, hp=0.62, xr=[(-0.30, -0.02), (0.02, 0.30)], Lcav=0.64 * 0.94, A_eta=0.60 * 2 * R_TUBE * math.sin(BETA)),
}
for key, c in konf.items():
    eta, f = eta_cavity(c["A_eta"], c["Lcav"])
    rows = []
    for psi in range(-180, 180, 5):
        r = row(slot(c["yp"], c["hp"], psi, c["xr"]), eta)
        r["psi"] = psi
        rows.append(r)
    ok = [r for r in rows if not r["vis"] and r["U0"] >= 0.40]
    W = max(ok, key=lambda r: r["Em"])
    Phi = 500.0 / W["Em"]
    for r in rows:
        r["Ev_stem"] = r["Ew"] * Phi * 0.25
    hid = [r for r in rows if not r["vis"]]
    M = max(hid, key=lambda r: (r["R"] >= 0.5, r["Ev_stem"]))
    F = max(rows, key=lambda r: r["face"])
    srcW = slot(c["yp"], c["hp"], W["psi"], c["xr"])
    rd = row(srcW, eta, TASKD)
    Escr = E_unit(srcW, SCRQ, TOROOM, screen=False) * W["k"] * Phi
    srcM = slot(c["yp"], c["hp"], M["psi"], c["xr"])
    LM = M["k"] * Phi * 0.25
    lm_w, lm_d, lm_w2, Evmax, Evfin = flux_budget(srcM, LM)
    ut = eta * Phi * 0.25
    OUT[key] = dict(eta=eta, f=f, psi_arb=W["psi"], Phi=Phi, P_W=Phi / 100, U0=W["U0"], A_cm2=W["A"] * 1e4, L_arb=W["k"] * Phi,
                    Phi_tett=500.0 / rd["Em"], U0_tett=rd["U0"],
                    psi_stem=M["psi"], Ev_stem=M["Ev_stem"], R_stem=M["R"], L_stem=LM,
                    psi_ansikt=F["psi"], L150=150.0 / F["face"], Phi150=150.0 / F["face"] * math.pi * F["A"] / eta,
                    E_skjerm_snitt=float(Escr.mean()), E_skjerm_maks=float(Escr.max()),
                    stem_lm_LED=Phi * 0.25, stem_lm_ut=ut, stem_lm_vegg_rute=lm_w, stem_lm_bord=lm_d, stem_lm_heile_veggen=lm_w2,
                    del_vegg_av_ut=lm_w / ut, del_bord_av_ut=lm_d / ut, del_heile_veggen_av_ut=lm_w2 / ut, del_vegg_av_LED=lm_w / (Phi * 0.25),
                    Ev_maks_vegg=Evmax, Ev_snitt_fin=Evfin)
    OUT[key]["nabo"] = [dict(psi=r["psi"], Phi=(500.0 / r["Em"] if r["Em"] > 0 else None), U0=r["U0"], vis=r["vis"])
                        for r in rows if W["psi"] - 20 <= r["psi"] <= W["psi"] + 10]
    if key == "a":
        e60, _ = eta_cavity(0.60 * 2 * R_TUBE * math.sin(BETA), c["Lcav"])
        r60 = row(slot(c["yp"], c["hp"], W["psi"], [(-0.30, 0.30)]), e60)
        OUT[key]["Phi_60cm"] = 500.0 / r60["Em"]; OUT[key]["U0_60cm"] = r60["U0"]; OUT[key]["eta_60cm"] = e60

# ================= (c) flak =================
ETA_C, PK = 0.70, 1.3
yp, zp, b = 0.26, 0.64, 0.25
rows = []
for al in range(-120, 101, 5):
    src = panel(yp, zp, al, b=b)
    r = row(src, ETA_C); r["al"] = al
    a = math.radians(al)
    s = np.linspace(-0.5, 0.5, 9) * b
    py, pz = yp - s * math.cos(a), zp + s * math.sin(a)
    r["elev_min"] = float(np.degrees(np.arctan2(pz - EYE[2], py - EYE[1])).min())
    r["kolli"] = bool((py > 0.73).any() or ((py < 0.50) & (pz < 0.50)).any() or (py > 0.512 - 0.01).any())
    rows.append(r)
for r in rows:
    r["Phi"] = 500.0 / r["Em"] if r["Em"] > 0 else float("inf")
    r["Ltopp"] = r["k"] * r["Phi"] * PK
ok = [r for r in rows if r["U0"] >= 0.40 and not r["kolli"] and r["elev_min"] >= 15.0 and (not r["vis"] or r["Ltopp"] <= 3000)]
W = min(ok, key=lambda r: r["Phi"]); Phi = W["Phi"]
okh = [r for r in ok if not r["vis"]]
Wh = min(okh, key=lambda r: r["Phi"]) if okh else None
for r in rows:
    r["Ev_stem"] = r["Ew"] * Phi * 0.25
    r["Lstem"] = r["k"] * Phi * 0.25 * PK
M = max([r for r in rows if not r["kolli"] and (not r["vis"] or r["Lstem"] <= 1000)], key=lambda r: (r["R"] >= 0.5, r["Ev_stem"]))
F = max([r for r in rows if not r["kolli"]], key=lambda r: r["face"])
srcW = panel(yp, zp, W["al"], b=b)
rd = row(srcW, ETA_C, TASKD)
Escr = E_unit(srcW, SCRQ, TOROOM, screen=False) * W["k"] * Phi
E_auge_arb = W["face"] * W["k"] * Phi
srcM = panel(yp, zp, M["al"], b=b)
LM = M["k"] * Phi * 0.25
lm_w, lm_d, lm_w2, Evmax, Evfin = flux_budget(srcM, LM)
ut = ETA_C * Phi * 0.25
OUT["c"] = dict(eta=ETA_C, alfa_arb=W["al"], Phi=Phi, P_W=Phi / 100, U0=W["U0"], A_cm2=W["A"] * 1e4, L_snitt=W["k"] * Phi, L_topp=W["Ltopp"],
                synleg_arb=W["vis"], elev_min_arb=W["elev_min"], Phi_tett=500.0 / rd["Em"], U0_tett=rd["U0"],
                alfa_stem=M["al"], Ev_stem=M["Ev_stem"], R_stem=M["R"], L_stem_topp=M["Lstem"], elev_min_stem=M["elev_min"],
                alfa_ansikt=F["al"], L150_topp=150.0 / F["face"] * PK, Phi150=150.0 / F["face"] / F["k"],
                E_skjerm_snitt=float(Escr.mean()), E_skjerm_maks=float(Escr.max()), E_auge_i_arbeid=E_auge_arb,
                stem_lm_LED=Phi * 0.25, stem_lm_ut=ut, stem_lm_vegg_rute=lm_w, stem_lm_bord=lm_d, stem_lm_heile_veggen=lm_w2,
                del_vegg_av_ut=lm_w / ut, del_bord_av_ut=lm_d / ut, del_heile_veggen_av_ut=lm_w2 / ut, del_vegg_av_LED=lm_w / (Phi * 0.25),
                Ev_maks_vegg=Evmax, Ev_snitt_fin=Evfin,
                skjult_variant=None if Wh is None else dict(alfa=Wh["al"], Phi=Wh["Phi"], U0=Wh["U0"], Ltopp=Wh["Ltopp"], elev_min=Wh["elev_min"]),
                sveip=[dict(al=r["al"], Phi=r["Phi"], U0=r["U0"], vis=r["vis"], Ltopp=r["Ltopp"], elev=r["elev_min"], kolli=r["kolli"])
                       for r in rows if -30 <= r["al"] <= 10])
OUT["c"]["Phi_ved_eta"] = {str(e): Phi * ETA_C / e for e in (0.55, 0.60, 0.674, 0.70, 0.80)}
# eta for (a)/(b) om LED sit paa roeyrveggen (direkte del sin(beta/2)) i staden for i aksen (sin beta)
for key in "ab":
    f = OUT[key]["f"]; cav = RHO * f / (1 - RHO * (1 - f))
    sb2 = math.sin(BETA / 2)
    e2 = sb2 + (1 - sb2) * cav
    OUT[key]["eta_LED_paa_vegg"] = e2
    OUT[key]["Phi_LED_paa_vegg"] = OUT[key]["Phi"] * OUT[key]["eta"] / e2
    OUT[key]["eta_berre_holrom"] = cav
    OUT[key]["Phi_berre_holrom"] = OUT[key]["Phi"] * OUT[key]["eta"] / cav
json.dump(OUT, open("kontroll_lys.json", "w"), indent=1, default=float)
for k in "abc":
    print("==", k)
    for q, v in OUT[k].items():
        if isinstance(v, list):
            print("  " + q + ":")
            for it in v:
                print("     ", {a: (round(float(x), 3) if isinstance(x, (float, np.floating)) else x) for a, x in it.items()})
        elif isinstance(v, dict):
            print("  " + q + ":", {a: (round(float(x), 3) if isinstance(x, (float, np.floating)) else x) for a, x in v.items()})
        elif isinstance(v, (float, np.floating)):
            print("  %-24s %.4f" % (q, v))
        else:
            print("  %-24s %s" % (q, v))
