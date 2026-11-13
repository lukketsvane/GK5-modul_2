# -*- coding: utf-8 -*-
"""Gransking, premiss-linsa: påstandar, premissar, bilete og brief.
Eigen kode frå grunnformlane. Ingen import av felles.py, form01/02/04/motor.py eller val.py.
Konstantar er skrivne av frå kjeldefilene (linjetilvising i kommentar). Datafilene (json/csv) vert berre lesne.
Køyr: PYTHONIOENCODING=utf-8 python premiss.py   (om lag 20 s)
Del:
  P  talpåstandar i loggane mot datafilene
  L  lysmodell: lineær kjelde i fjernfelt, I = η·G(θ)·(2/π)·cos ξ per lm, med skjermskugge.
     Byte av optikk mellom posisjonane til (a) og (c): kor mykje av Φ-skilnaden er optikk, kor mykje er form?
     Same modell gjev skjermlys, veggen bak skjermen i arbeid (krav F6) og stemning med to reglar.
  S  synsfelt: vinkelkart frå auga, kor mykje av kvar lampe som ligg over skjermen og under 15°
  V  (c): hovudet sveipt om LED-aksen og om tyngdepunktet: synsfelt og kollisjon med armen
  M  (c): vridning av open U-profil når gesten tek i enden av plata
  K  krav i kravspesifikasjonen (GK5-modul_2/grunnlag/04) og ramma (00) mot dei tre
  C  masse, aluminium, straum og CO2e over ti år, med spenn i faktorane
"""
import os, json, math, csv
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
OUT = {}

# ---------------- scene (felles.py l.18-27) ----------------
SX0, SX1, SY, SZ0, SZ1 = -0.275, 0.275, 0.45, 0.10, 0.42
WALL = 0.75
EYE = np.array([0.0, -0.30, 0.45])
EYES = np.array([[0.0, -0.30, 0.45], [-0.15, -0.30, 0.45], [0.15, -0.30, 0.45]])
tx, ty = np.meshgrid(np.linspace(-0.30, 0.30, 7), np.linspace(0.05, 0.40, 5))
TASK = np.c_[tx.ravel(), ty.ravel(), np.zeros(tx.size)]
wx, wz = np.meshgrid(np.linspace(-0.70, 0.70, 8), np.linspace(0.05, 1.20, 6))
WALLG = np.c_[wx.ravel(), np.full(wx.size, WALL - 1e-3), wz.ravel()]
dx_, dy_ = np.meshgrid(np.linspace(-0.68, 0.68, 8), np.linspace(0.02, 0.73, 5))
DESKG = np.c_[dx_.ravel(), dy_.ravel(), np.zeros(dx_.size)]


def lese():
    kj = json.load(open(os.path.join(ROOT, 'konsept.json'), encoding='utf-8'))
    f2 = json.loads(open(os.path.join(ROOT, 'form02', 'tal.json'), encoding='utf-8').read().replace('NaN', 'null').replace('Infinity', 'null'))
    f4 = next(csv.DictReader(open(os.path.join(ROOT, 'form04', 'tal.csv'), encoding='utf-8')))
    f1 = next(csv.DictReader(open(os.path.join(ROOT, 'form01', 'tal.csv'), encoding='utf-8')))
    sk = json.load(open(os.path.join(ROOT, 'form04', 'skjerm.json'), encoding='utf-8'))
    mk = json.load(open(os.path.join(HER, 'mekanikk_tal.json'), encoding='utf-8'))
    kl = json.load(open(os.path.join(HER, 'kontroll_lys.json'), encoding='utf-8'))
    s4 = json.load(open(os.path.join(ROOT, 'form04', 'sok.json'), encoding='utf-8'))
    return kj, f2, {k: (float(v) if v.replace('.', '', 1).replace('-', '', 1).isdigit() else v) for k, v in f4.items()}, \
        {k: (float(v) if v.replace('.', '', 1).replace('-', '', 1).isdigit() else v) for k, v in f1.items()}, sk, mk, kl, s4


# ======================= P: påstandar =======================
def del_P():
    kj, f2, f4, f1, sk, mk, kl, s4 = lese()
    rad = []

    def sjekk(fil, pastand, tekst, data, tol):
        ok = abs(tekst - data) <= tol
        rad.append(dict(fil=fil, pastand=pastand, tekst=tekst, data=round(float(data), 4), ok=bool(ok)))
    a, b, c = kj['a'], kj['b'], kj['c']
    sjekk('konsept.md', 'batteri (a) t = 0,9·21,6/P', 1.5, 0.9 * 21.6 / a['P_W'], 0.05)
    sjekk('konsept.md', 'batteri (b) t', 1.5, 0.9 * 21.6 / b['P_W'], 0.05)
    sjekk('konsept.md', 'batteri (c) t', 4.5, c['batt_t'], 0.05)
    sjekk('konsept.md', '(c) ein tredjedel av lyset: Φc/Φa', 1 / 3, c['Phi_lm'] / a['Phi_lm'], 0.02)
    sjekk('form04/logg.md', '«trefjerdedelar mindre lys»: 1 − Φc/Φa', 0.75, 1 - c['Phi_lm'] / a['Phi_lm'], 0.03)
    sjekk('form04/logg.md', '«trefjerdedelar mindre lys»: 1 − Φc/Φb', 0.75, 1 - c['Phi_lm'] / b['Phi_lm'], 0.03)
    sjekk('konsept.md', '(c) tipp utan skjerm', 22, f4['tipp_aleine'], 0.5)
    sjekk('konsept.md', '(c) tipp i tal.csv (med skjerm 4 kg)', 22, f4['tipp_deg'], 0.5)
    sjekk('konsept.md', '(a) tipp 2,9 N i grephøgd', 2.9, f2['a']['F_tipp_N'], 0.06)
    sjekk('konsept.md', 'tett gitter (a) Φ −5 %', -0.05, kl['a']['Phi_tett'] / kl['a']['Phi'] - 1, 0.006)
    sjekk('konsept.md', 'tett gitter (a) U0 0,72', 0.72, kl['a']['U0_tett'], 0.006)
    sjekk('konsept.md', '(a) skjerm 611 lx', 611, kl['a']['E_skjerm_snitt'], 1)
    sjekk('konsept.md', '(b) skjerm 652 lx', 652, kl['b']['E_skjerm_snitt'], 1)
    sjekk('konsept.md', '(c) skjerm 9 lx', 9, sk['E_skjerm_snitt'], 0.5)
    sjekk('konsept.md', '(b) Ø23 ut av planet 2,3 mm', 2.3, mk['b']['D23']['ut_av_plan'], 0.05)
    sjekk('konsept.md', '(b) Ø25 1,8 mm', 1.8, mk['b']['D25']['ut_av_plan'], 0.05)
    sjekk('konsept.md', '(b) klemme 500 N', 500, mk['b']['klemme']['P_vri_mu03'], 5)
    sjekk('konsept.md', '(b) klemme SF 2 1000 N', 1000, mk['b']['klemme']['P_SF2'], 10)
    sjekk('form02/val.md', '(a)→(b) 4 % meir lys', 0.04, b['Phi_lm'] / a['Phi_lm'] - 1, 0.004)
    sjekk('form02/val.md', '(a)→(b) 0,25 kg lettare', 0.25, a['masse_kg'] - b['masse_kg'], 0.01)
    sjekk('form02/val.md', '(a)→(c gamal) 16 % mindre lys', 0.16, 1 - f2['c']['Phi_lm'] / f2['a']['Phi_lm'], 0.005)
    sjekk('form02/val.md', '(a)→(c gamal) «1,4 cm² mindre kjølekrav»', 1.4, f2['a']['A_krav_cm2'] - f2['c']['A_krav_cm2'], 0.5)
    sjekk('form02/val.md', 'platearm 1,7 mm ved spissen', 1.7, f2['b']['plate_w_spiss_mm'], 0.1)
    sjekk('form02/val.md', 'platearm 18 mm ved klemma', 18, f2['b']['plate_w_klemme_mm'], 0.5)
    sjekk('form02/val.md', 'arm 6° over augehøgd (minste, utan stigaren)', 6, f2['b']['arm_elev_min'], 0.5)
    sjekk('form01/logg.md', 'kjøl/krav 492 cm²', 492, f1['A_krav_cm2'], 2)
    sjekk('form01/logg.md', 'krav ved 1476 lm (før endeskiver): 1476/100/300 m²', 492, 1476 / 100 / 300 * 1e4, 2)
    sjekk('form01/logg.md', 'fotavtrykk 0,46 m²', 0.46, f1['fot_cm2'] / 1e4, 0.005)
    sjekk('form04/logg.md', '6 av 20 punkt held', 6, sum(r['ok'] for r in s4), 0)
    sjekk('form04/logg.md', 'akse 33 mm under LED', 33, f4['akse_under_led_mm'], 0.5)
    sjekk('form04/logg.md', 'innfall aldri over 31°', 31, f4['innfall_maks_deg'], 0.5)
    sjekk('form04/logg.md', 'pendel 0,22 N·m = m_plate·g·d', 0.22, f4['m_plate_kg'] * 9.81 * 0.05, 0.005)
    sjekk('form04/logg.md', 'gestkraft første versjon 5,3 N = (0,20+0,22)/0,08', 5.3, (0.20 + f4['m_plate_kg'] * 9.81 * 0.05) / 0.08, 0.05)
    best_ok = min((r for r in s4 if r['ok']), key=lambda r: r['Phi'])
    rad.append(dict(fil='form04/motor.py FINAL', pastand='vald ys 0,22 zs 0,70 er minste Φ blant ok-punkta?', tekst=432.7,
                    data=round(best_ok['Phi'], 1), ok=False, merk=f"minst: ys {best_ok['ys']} zs {best_ok['zs']}"))
    OUT['P'] = rad
    return rad


# ======================= L: lysmodell =======================
def gauss(G, tg, sig):
    k = np.exp(-0.5 * (np.degrees(tg - tg[len(tg) // 2]) / sig) ** 2)
    k /= k.sum()
    return np.convolve(G, k, mode='same')


TG = np.radians(np.arange(-180, 180.001, 0.25))


def G_lamb(thn):
    G = np.clip(np.cos(TG - thn), 0, None) / 2
    return G / np.trapezoid(G, TG)


def G_vifte(th1, th2, sig=4.0):
    """Ideell vifte: jamn E på bordet frå ei lang line: J ∝ 1/cos²θ mellom θ1 og θ2 (eigen utleiing, 2D)."""
    G = np.where((TG >= th1) & (TG <= th2), 1 / np.cos(TG) ** 2, 0.0)
    G = gauss(G, TG, sig)
    return G / np.trapezoid(G, TG)


def blokk(S, Q):
    """Strålen S→Q kryssar skjermrektangelet (y = SY) mellom endepunkta."""
    d = Q[None] - S[:, None]
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (SY - S[:, None, 1]) / d[..., 1]
    X = S[:, None, 0] + t * d[..., 0]
    Z = S[:, None, 2] + t * d[..., 2]
    return (t > 1e-6) & (t < 1 - 1e-6) & (X > SX0) & (X < SX1) & (Z > SZ0) & (Z < SZ1)


def E_per_lm(src, Q, qn):
    """src: dict(x0, x1, y, z, G, eta, hub). Illuminans per LED-lm på Q med normal qn."""
    n = 80
    xs = (np.arange(n) + .5) / n * (src['x1'] - src['x0']) + src['x0']
    if src.get('hub'):
        xs = xs[np.abs(xs) > src['hub']]
    S = np.c_[xs, np.full(len(xs), src['y']), np.full(len(xs), src['z'])]
    d = Q[None] - S[:, None]
    r = np.linalg.norm(d, axis=-1)
    xi = np.arcsin(np.clip(d[..., 0] / r, -1, 1))
    th = np.arctan2(-d[..., 1], -d[..., 2])
    I = src['eta'] / len(S) * np.interp(th, TG, src['G']) * (2 / np.pi) * np.cos(xi)
    ci = -(d @ qn) / r
    ok = (ci > 0) & ~blokk(S, Q)
    return (np.where(ok, I * ci / r ** 2, 0)).sum(0)


SCRQ = np.array([[x, SY - 1e-4, z] for z in (np.arange(16) + .5) / 16 * (SZ1 - SZ0) + SZ0
                 for x in (np.arange(22) + .5) / 22 * (SX1 - SX0) + SX0])
gwx, gwz = np.meshgrid(np.arange(-0.6875, 0.70, 0.025), np.arange(0.0625, 1.20, 0.025))
WALLF = np.c_[gwx.ravel(), np.full(gwx.size, WALL - 1e-3), gwz.ravel()]
bx, bz = np.meshgrid(np.arange(-0.39, 0.40, 0.02), np.arange(0.11, 0.70, 0.02))
BAK = np.c_[bx.ravel(), np.full(bx.size, WALL - 1e-3), bz.ravel()]           # flata bak og over skjermen, x ±0,40, z 0,10–0,70


def maal(src):
    Et = E_per_lm(src, TASK, np.array([0, 0, 1.0]))
    Phi = 500 / Et.mean()
    Es = E_per_lm(src, SCRQ, np.array([0, -1.0, 0])) * Phi
    Eb = E_per_lm(src, BAK, np.array([0, -1.0, 0])) * Phi
    return dict(Phi=float(Phi), U0=float(Et.min() / Et.mean()), E_skjerm=float(Es.mean()), E_skjerm_maks=float(Es.max()),
                E_bak_skjerm=float(Eb.mean()), E_bak_min=float(Eb.min()))


def stemning(src_m, Phi_arb):
    Ew = E_per_lm(src_m, WALLG, np.array([0, -1.0, 0])).mean()
    Ed = E_per_lm(src_m, DESKG, np.array([0, 0, 1.0])).mean()
    Ewf = E_per_lm(src_m, WALLF, np.array([0, -1.0, 0])).mean()
    E10 = 10 * math.pi / 0.75                                     # 10 cd/m² på ein vegg med ρ 0,75
    return dict(R=float(Ew / (Ew + Ed)), Ev25_8x6=float(Ew * Phi_arb * 0.25), Ev25_fin=float(Ewf * Phi_arb * 0.25),
                lm_25=float(0.25 * Phi_arb), lm_10cd=float(E10 / Ewf), W_10cd=float(E10 / Ewf / 100))


def synleg(c, n):
    """Lambertsk opning i (y,z) c med normal n (profil): synleg for auge i høgd z frå y −0,30 om (e − c)·n > 0."""
    zs = np.linspace(0.20, 0.65, 4501)
    v = (-0.30 - c[0]) * n[0] + (zs - c[1]) * n[1]
    return float(zs[v > 0].max()) if (v > 0).any() else None


def del_L():
    R, be = 0.022, math.radians(25)
    res = {}
    # (a): form02 tal_bru(15): yp 0,18 hp 0,62, ψ −20 (tal.json psi_arb), opning k·L = 0,536·1,12 = 0,600 m, η 0,674
    def tube(yp, hp, psi, L2, eta, hub=None):
        n = np.array([-math.sin(psi), -math.cos(psi)])
        c = np.array([yp, hp]) + R * math.cos(be) * n
        return dict(x0=-L2, x1=L2, y=c[0], z=c[1], G=G_lamb(psi), eta=eta, hub=hub), c, n
    psiA = math.radians(-20)
    sa, ca, na = tube(0.18, 0.62, psiA, 0.300, 0.674110050973263)
    sb, cb, nb = tube(0.25, 0.62, psiA, 0.3008, 0.6669177920830083, hub=0.015)
    # (c): line ys 0,22 zs 0,70, vifte mot y 0,02–0,43 (motor.py BASE y1, y2), η 0,739
    ETA_C = 0.7387707081611625
    th = lambda ys, zs: (math.atan((ys - 0.43) / zs), math.atan((ys - 0.02) / zs))
    sc = dict(x0=-0.30, x1=0.30, y=0.22, z=0.70, G=G_vifte(*th(0.22, 0.70)), eta=ETA_C)
    res['a_lamb'] = maal(sa); res['b_lamb'] = maal(sb); res['c_vifte'] = maal(sc)
    # byte: vifte på (a)-plassen (same η som (c), og η for hulrom × plate 0,674·0,85), lambertsk på (c)-plassen
    sa_v = dict(sa, y=0.18, z=0.62, G=G_vifte(*th(0.18, 0.62)), eta=ETA_C)
    res['a_vifte'] = maal(sa_v)
    res['a_vifte_eta_hulrom'] = maal(dict(sa_v, eta=0.674 * 0.85))
    sb_v = dict(sb, y=0.25, z=0.62, G=G_vifte(*th(0.25, 0.62)), eta=ETA_C)
    res['b_vifte'] = maal(sb_v)
    best = None
    for d in range(-60, 31):
        psi = math.radians(d)
        n = np.array([-math.sin(psi), -math.cos(psi)])
        if any((e[1] - 0.22) * n[0] + (e[2] - 0.70) * n[1] > 0 for e in EYES):
            continue                                              # same skjermingsregel som (a)/(b): opninga ikkje synleg
        m = maal(dict(sc, G=G_lamb(psi), eta=0.674))
        if m['U0'] >= 0.40 and (best is None or m['Phi'] < best[1]['Phi']):
            best = (d, m)
    res['c_lamb'] = dict(best[1], psi=best[0])
    # stemning, to reglar
    st = {}
    st['a'] = stemning(dict(sa, G=G_lamb(math.radians(-95))), res['a_lamb']['Phi'])
    st['b'] = stemning(dict(sb, G=G_lamb(math.radians(-95))), res['b_lamb']['Phi'])
    Gc = sc['G']
    sh = int(round(105 / 0.25))
    Gm = np.roll(Gc, -sh)                                         # vifta vipp 105° mot veggen (G(θ + 105°))
    st['c'] = stemning(dict(sc, G=Gm / np.trapezoid(Gm, TG)), res['c_vifte']['Phi'])
    res['stemning'] = st
    # (c) ved vippvinklar som er nåelege før plata går i armen (del V: −51° om LED-aksen, −63° om tyngdepunktet)
    res['stemning_c_alfa'] = {}
    for a_ in (-105, -60, -50):
        G_ = np.roll(Gc, -int(round(-a_ / 0.25)))
        res['stemning_c_alfa'][a_] = stemning(dict(sc, G=G_ / np.trapezoid(G_, TG)), res['c_vifte']['Phi'])
    # synlegheit av opninga for augehøgder 0,25–0,60 (krav F1), y −0,30
    res['synleg_under_z'] = dict(a=synleg(ca, na), b=synleg(cb, nb))
    OUT['L'] = res
    return res


# ======================= S: synsfelt =======================
def plate_pts(c, u, v, nu, nv):
    a = np.linspace(-.5, .5, nu)[:, None, None] * u
    b = np.linspace(-.5, .5, nv)[None, :, None] * v
    return (c + a + b).reshape(-1, 3)


def boks(x0, x1, y0, y1, z0, z1, h=0.0015):
    """Overflatepunkt på ein boks."""
    P = []
    nx, ny, nz = [max(2, int(abs(q) / h) + 1) for q in (x1 - x0, y1 - y0, z1 - z0)]
    X, Y, Z = np.linspace(x0, x1, nx), np.linspace(y0, y1, ny), np.linspace(z0, z1, nz)
    for xx in (x0, x1):
        g = np.meshgrid(Y, Z); P.append(np.c_[np.full(g[0].size, xx), g[0].ravel(), g[1].ravel()])
    for yy in (y0, y1):
        g = np.meshgrid(X, Z); P.append(np.c_[g[0].ravel(), np.full(g[0].size, yy), g[1].ravel()])
    for zz in (z0, z1):
        g = np.meshgrid(X, Y); P.append(np.c_[g[0].ravel(), g[1].ravel(), np.full(g[0].size, zz)])
    return np.vstack(P)


def roeyr(C, r, h=0.0015):
    """Røyr langs polylinje C (n,3): kuler med radius r langs lina (silhuett)."""
    C = np.asarray(C, float)
    seg = []
    for p, q in zip(C[:-1], C[1:]):
        n = max(2, int(np.linalg.norm(q - p) / h) + 1)
        seg.append(p + np.linspace(0, 1, n)[:, None] * (q - p))
    L = np.vstack(seg)
    k = int(r / h) + 1
    o = np.linspace(-r, r, 2 * k + 1)
    O = np.array([[a, b, cc] for a in o for b in o for cc in o if a * a + b * b + cc * cc <= r * r])
    O = O[np.abs(np.linalg.norm(O, axis=1) - r) < h * 1.2]       # berre skalet
    return (L[:, None] + O[None]).reshape(-1, 3)


def lampar():
    """Geometri skriven av frå form01/motor.py geometri(), form02/val.py geometri_krok()/arm_path(), form04/motor.py geometri()."""
    R = 0.022
    d = {}
    # (a) bru: røyr x ±0,56, y 0,18, z 0,62; A-bukkar Ø20 frå apex (±0,576, 0,18, 0,62) til føter (±0,576, 0,18 ± 0,15, 0,01)
    lys = roeyr([[-0.56, 0.18, 0.62], [0.56, 0.18, 0.62]], R)
    bein = [roeyr([[s * 0.576, 0.18, 0.62], [s * 0.576, 0.18 + t * 0.15, 0.01]], 0.010) for s in (-1, 1) for t in (-1, 1)]
    grep = roeyr([[0.588, 0.18, 0.62], [0.622, 0.18, 0.62]], 0.026)
    d['a'] = dict(lys=lys, bering=np.vstack(bein + [grep]))
    # (b) krok: røyr x ±0,32, y 0,25, z 0,62; arm Ø23: y 0,74 frå z 0,012 til 0,557, boge r 0,10, z 0,657 til y 0,25, ned til 0,6446
    lys = roeyr([[-0.32, 0.25, 0.62], [0.32, 0.25, 0.62]], R)
    H, rf = 0.62 + R + 0.015, 0.10
    t = np.linspace(0, math.pi / 2, 12)
    C = [[0, 0.74, 0.012], [0, 0.74, H - rf]] + [[0, 0.74 - rf + rf * math.cos(q), H - rf + rf * math.sin(q)] for q in t] + \
        [[0, 0.25, H], [0, 0.25, 0.62 + 1.12 * R]]
    arm = roeyr(C, 0.0115)
    grep = roeyr([[0.32, 0.25, 0.62], [0.35, 0.25, 0.62]], 0.026)
    nav = roeyr([[-0.015, 0.25, 0.62], [0.015, 0.25, 0.62]], R * 1.12)
    d['b'] = dict(lys=lys, bering=np.vstack([arm, grep, nav]))
    # (c) prisme (form04 FINAL): LED-renne 16×20 og plate 60×16 cm 5 cm under; heng x ±0,05; arm z 0,73–0,76; søyle U 100×30×2 ved y 0,512
    ys, zs, za, cy, cf = 0.22, 0.70, 0.73, 0.512, 0.03
    lys = np.vstack([boks(-0.30, 0.30, ys - 0.08, ys + 0.08, zs - 0.053, zs - 0.050), boks(-0.30, 0.30, ys - 0.008, ys + 0.008, zs - 0.005, zs + 0.015)])
    ber = [boks(s * 0.05 - 0.001, s * 0.05 + 0.001, ys - 0.012, ys + 0.012, zs - 0.012, za + cf) for s in (-1, 1)]
    ber += [boks(s * 0.05 - 0.001, s * 0.05 + 0.001, ys - 0.012, cy + cf, za, za + cf) for s in (-1, 1)]
    ber += [boks(s * 0.05 - 0.001, s * 0.05 + 0.001, cy, cy + cf, 0.004, za) for s in (-1, 1)]
    ber += [boks(-0.05, 0.05, ys - 0.012, cy + cf, za + cf - 0.002, za + cf), boks(-0.05, 0.05, cy + cf - 0.002, cy + cf, 0.004, za + cf)]
    d['c'] = dict(lys=lys, bering=np.vstack(ber))
    return d


def vinkel(P, e):
    v = P - e
    az = np.degrees(np.arctan2(v[:, 0], v[:, 1]))
    el = np.degrees(np.arctan2(v[:, 2], np.hypot(v[:, 0], v[:, 1])))
    t = (SY - e[1]) / (P[:, 1] - e[1])
    X, Z = e[0] + t * (P[:, 0] - e[0]), e[2] + t * (P[:, 2] - e[2])
    skjult = (P[:, 1] > SY) & (X > SX0) & (X < SX1) & (Z > SZ0) & (Z < SZ1)
    return az[~skjult], el[~skjult]


def kart(az, el, h=0.1):
    A = np.zeros((int(110 / h), int(110 / h)), bool)
    i = np.clip(((el + 40) / h).astype(int), 0, A.shape[0] - 1)
    j = np.clip(((az + 55) / h).astype(int), 0, A.shape[1] - 1)
    A[i, j] = True
    return A


def del_S():
    L = lampar()
    h = 0.1
    els = (np.arange(int(110 / h)) + .5) * h - 40
    azs = (np.arange(int(110 / h)) + .5) * h - 55
    EL, AZ = np.meshgrid(els, azs, indexing='ij')
    dA = h * h * np.cos(np.radians(EL))
    az_skj = math.degrees(math.atan(0.275 / 0.75))
    el_topp = math.degrees(math.atan((0.42 - 0.45) / 0.75))
    sone = (np.abs(AZ) <= az_skj) & (EL <= 15.0) & (EL >= el_topp - 0.5)
    skjerm_deg2 = float(((np.abs(AZ) <= az_skj) & (EL <= el_topp) & (EL >= math.degrees(math.atan(-0.35 / 0.75)))).sum() * h * h)
    res = {'skjerm_deg2': skjerm_deg2, 'sone': f'|az| ≤ {az_skj:.1f}°, el {el_topp:.1f}° til 15°'}
    kartar = {}
    for k in 'abc':
        r = {}
        for e_lab, e in (('midt', EYES[0]), ('venstre', EYES[1]), ('hogre', EYES[2])):
            m = {}
            for del_ in ('lys', 'bering'):
                az, el = vinkel(L[k][del_], e)
                A = kart(az, el, h)
                m[del_] = A
            Aall = m['lys'] | m['bering']
            r[e_lab] = dict(sone_lys_deg2=float((m['lys'] & sone).sum() * h * h), sone_bering_deg2=float((m['bering'] & sone).sum() * h * h),
                            sone_alt_deg2=float((Aall & sone).sum() * h * h), heile_deg2=float((Aall * dA).sum()),
                            lagaste_el_over_skjerm=float(EL[Aall & (np.abs(AZ) <= az_skj) & (EL >= el_topp - 0.5)].min()) if (Aall & (np.abs(AZ) <= az_skj) & (EL >= el_topp - 0.5)).any() else None,
                            lys_lagaste_el=float(EL[m['lys']].min()))
            if e_lab == 'midt':
                kartar[k] = m
        res[k] = r
    OUT['S'] = res
    # figur: auga sitt bilete, tre ramer, same skala
    W, Hh = 3 * 560, 620
    im = Image.new('RGB', (W, Hh), 'black'); dr = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype(r'C:\Windows\Fonts\georgiai.ttf', 22); fs = ImageFont.truetype(r'C:\Windows\Fonts\georgiai.ttf', 16)
    except OSError:
        f = fs = ImageFont.load_default()
    sc = 4.8                                                      # px per grad
    for j, k in enumerate('abc'):
        ox, oy = j * 560 + 280, 300                               # (az 0, el 0)
        def px(a, e_):
            return ox + a * sc, oy - e_ * sc
        # skjerm
        x0_, y0_ = px(-az_skj, el_topp); x1_, y1_ = px(az_skj, math.degrees(math.atan(-0.35 / 0.75)))
        dr.rectangle([x0_, y0_, x1_, min(y1_, Hh - 70)], fill=(28, 28, 30))
        # 15°-line
        xa, ya = px(-az_skj, 15); xb, _ = px(az_skj, 15)
        dr.line([xa, ya, xb, ya], fill=(120, 110, 95), width=1)
        dr.text((xb + 4, ya - 9), '15°', font=fs, fill=(150, 140, 125))
        for del_, col in (('bering', (200, 186, 160)), ('lys', (255, 220, 170))):
            A = kartar[k][del_]
            ii, jj = np.nonzero(A)
            for i_, j_ in zip(ii[::1], jj[::1]):
                x, y = px(azs[j_], els[i_])
                if j * 560 + 4 <= x < (j + 1) * 560 - 4 and 0 <= y < Hh - 70:
                    im.putpixel((int(x), int(y)), col)
        s = res[k]['midt']
        dr.text((j * 560 + 20, Hh - 62), {'a': '(a) bru', 'b': '(b) krok', 'c': '(c) prisme'}[k], font=f, fill=(240, 236, 228))
        dr.text((j * 560 + 20, Hh - 32), f"under 15° over skjermen: {s['sone_alt_deg2']:.0f} grad²".replace('.', ','), font=fs, fill=(170, 163, 152))
    im.save(os.path.join(HER, 'premiss.png'))
    return res


# ======================= V: sveip av hovudet i (c) =======================
def del_V():
    ys, zs, d, tp = 0.22, 0.70, 0.05, 0.003
    za, cf, cy = 0.73, 0.03, 0.512
    boksar = [(-0.051, -0.049, ys - 0.012, ys + 0.012, zs - 0.012, za + cf), (0.049, 0.051, ys - 0.012, ys + 0.012, zs - 0.012, za + cf),
              (-0.051, -0.049, ys - 0.012, cy + cf, za, za + cf), (0.049, 0.051, ys - 0.012, cy + cf, za, za + cf),
              (-0.05, 0.05, ys - 0.012, cy + cf, za + cf - 0.002, za + cf)]
    xs = np.linspace(-0.30, 0.30, 121); ss = np.linspace(-0.08, 0.08, 33)
    X, Sg = np.meshgrid(xs, ss)
    res = {}
    for lab, akse_ned in (('LED-aksen (teikna og rekna)', 0.0), ('tyngdepunktet 33 mm under (logg.md)', 0.0329)):
        rows = []
        for a_deg in range(-130, 101, 1):
            a = math.radians(a_deg)
            ned = np.array([-math.sin(a), -math.cos(a)]); fram = np.array([-math.cos(a), math.sin(a)])
            piv = np.array([ys, zs - akse_ned])                   # pivot i arbeid
            # punkt i hovudramma relativt til LED-aksen: w ned, s fram; roter om pivot
            pts = []
            for w in (d, d + tp):
                rel = np.c_[Sg.ravel(), np.full(Sg.size, w)]       # (s, w) frå LED-aksen
                rel_p = rel - np.array([0.0, akse_ned])            # frå pivot (pivot ligg akse_ned under LED i hovudramma)
                yz = piv + rel_p[:, :1] * fram + rel_p[:, 1:] * ned
                pts.append(np.c_[np.tile(X.ravel(), 1), yz])
            P = np.vstack(pts)
            kol = any(((P[:, 0] > b[0]) & (P[:, 0] < b[1]) & (P[:, 1] > b[2]) & (P[:, 1] < b[3]) & (P[:, 2] > b[4]) & (P[:, 2] < b[5])).any() for b in boksar)
            el = np.degrees(np.arctan2(P[:, 2] - EYE[2], P[:, 1] - EYE[1])).min()
            rows.append((a_deg, bool(kol), float(el)))
        kol_neg = [a for a, k, _ in rows if k and a < 0]
        kol_pos = [a for a, k, _ in rows if k and a > 0]
        res[lab] = dict(kollisjon_fra_bakover=max(kol_neg) if kol_neg else None, kollisjon_fra_fram=min(kol_pos) if kol_pos else None,
                        el_min_arbeid=next(e for a, k, e in rows if a == 0), el_min_stem=next(e for a, k, e in rows if a == -105),
                        el_min_ansikt=next(e for a, k, e in rows if a == 70), el_min_sveip=min(e for a, k, e in rows if -105 <= a <= 0))
    OUT['V'] = res
    return res


# ======================= M: vridning i open U =======================
def del_M():
    G_ALU, E_ALU = 26e9, 70e9
    t, w, f = 0.002, 0.10, 0.03
    J_open = (w + 2 * f) * t ** 3 / 3
    Am = (w - t) * (f - t / 2)
    J_box = 4 * Am ** 2 * t / (2 * (w - t) + 2 * (f - t / 2))      # Bredt, lukka 100 × 30 × 2
    F_g = 0.20 / 0.08                                               # motor: T_FRIK / (bp/2)
    L_arm, L_col, e = 0.512 + 0.03 - 0.22, 0.73, 0.30
    # kraft i framkanten av plata i arbeid: tangent til vippa om LED-aksen; radius (−0,08 fram, 0,05 ned) → retning
    r = np.array([-0.08, -0.05]); tng = np.array([r[1], -r[0]]) / np.linalg.norm(r)   # (y, z)
    Fy, Fz = F_g * abs(tng[0]), F_g * abs(tng[1])
    res = {}
    for lab, J in (('open U 100×30×2', J_open), ('lukka boks 100×30×2', J_box)):
        th_arm = Fz * e * L_arm / (G_ALU * J)                     # torsjon i armen om y frå loddrett del i enden
        th_col = Fy * e * L_col / (G_ALU * J)                     # torsjon i søyla om z frå y-delen i enden
        res[lab] = dict(J_m4=J, arm_mm=th_arm * e * 1000, soyle_mm=th_col * e * 1000, sum_mm=(th_arm + th_col) * e * 1000)
    res['F_g_N'] = F_g; res['Fy_N'] = Fy; res['Fz_N'] = Fz
    res['motor_svikt_mm'] = 0.194
    OUT['M'] = res
    return res


# ======================= K, C: krav, masse, CO2e =======================
def del_KC(L):
    kj, f2, f4, f1, sk, mk, kl, s4 = lese()
    a, b, c = kj['a'], kj['b'], kj['c']
    K = {}
    for k, o in (('a', a), ('b', b), ('c', c)):
        st = L['stemning'][k]
        K[k] = dict(Phi=o['Phi_lm'], W=o['P_W'], W_350lx=o['P_W'] * 350 / 500, masse=o['masse_kg'], bord_cm2=o['fot_cm2'],
                    stem_lm_25=0.25 * o['Phi_lm'], batt_arb_t=0.9 * 21.6 / o['P_W'], batt_arb_350_t=0.9 * 21.6 / (o['P_W'] * 0.7),
                    E_bak_skjerm=L[{'a': 'a_lamb', 'b': 'b_lamb', 'c': 'c_vifte'}[k]]['E_bak_skjerm'])
    OUT['K'] = K
    # C: masse og materiale (motorane sine delar), straum 10 år, faktorspenn
    R, tb = 0.022, 0.0012
    m_ror_a = 2700 * math.pi * 2 * R * tb * 1.12 * (1 - 0.536 * 25 / 180)
    Aleg = math.pi / 4 * (0.02 ** 2 - 0.017 ** 2)
    m_bein = 2700 * Aleg * 4 * math.hypot(0.62 - 0.01, 0.15)
    m_ror_b = 2700 * math.pi * 2 * R * tb * 0.64 * (1 - 0.94 * 25 / 180)
    m_arm_b = f2['b'].get('masse_arm', None)
    alu = dict(a=m_ror_a + m_bein + 0.06 + 0.03, b=m_ror_b + 0.302 + 0.25 + 0.06 + 0.04,
               c=2700 * 0.24 * 0.30 * 0.007 + 2700 * 3.2e-4 * (0.73 + 0.322) + 2700 * 0.056 * 0.0015 * 0.6)
    pmma = dict(a=0.0, b=0.0, c=f4['m_plate_kg'])
    timar = 920 * 10                                              # same bruk som 06-berekraftshandling: 920 t/år, 10 år
    C = {}
    for k, o in (('a', a), ('b', b), ('c', c)):
        kWh = o['P_W'] * timar / 1000
        C[k] = dict(alu_kg=alu[k], pmma_kg=pmma[k], kWh_10aar=kWh,
                    straum_kgCO2e=(kWh * 0.015, kWh * 0.152), alu_kgCO2e=(alu[k] * 2.0, alu[k] * 16.0), pmma_kgCO2e=pmma[k] * 6.0)
    OUT['C'] = dict(C=C, faktorar='straum 0,015 (norsk produksjon) til 0,152 kg/kWh (implisitt i 06-berekraftshandling: 7 kg for 5 W × 920 t × 10 år); '
                    'aluminium 2 (høg resirkulert del) til 16 kg CO2e/kg (primær, global snitt); PMMA 6 kg/kg. Alle er anslag utan kjelde framfor meg.')
    return K, OUT['C']


if __name__ == '__main__':
    P = del_P()
    print('P: påstandar'); [print(' ', 'OK ' if r['ok'] else 'AVVIK', r['fil'], '|', r['pastand'], '| tekst', r['tekst'], '| data', r['data'], r.get('merk', '')) for r in P]
    L = del_L()
    print('L:'); [print(' ', k, {q: (round(v, 3) if isinstance(v, float) else v) for q, v in m.items()}) for k, m in L.items() if k not in ('stemning', 'synleg_under_z')]
    print('  stemning', json.dumps({k: {q: round(v, 2) for q, v in m.items()} for k, m in L['stemning'].items()}, ensure_ascii=False))
    print('  opning synleg under augehøgd', L['synleg_under_z'])
    S = del_S()
    print('S:', json.dumps(S, ensure_ascii=False, indent=0)[:3000])
    V = del_V(); print('V:', json.dumps(V, ensure_ascii=False))
    M = del_M(); print('M:', json.dumps(M, ensure_ascii=False))
    K, C = del_KC(L)
    print('K:', json.dumps(K, ensure_ascii=False)); print('C:', json.dumps(C, ensure_ascii=False))
    json.dump(OUT, open(os.path.join(HER, 'premiss.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False, default=float)
