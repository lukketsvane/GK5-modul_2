"""form03 «Lok» — motor: fald. Éi plate i tre faldar: fot under skjermen, søyle bak han, lysande lok over han.

Grep: lyset er ei flate, ikkje ei line. Undersida av loket lyser mjukt (<= 3000 cd/m2), så ho kan vere synleg.
Gest: opne loket som ein laptop (α om hengsla). Ned = arbeid, mot deg = ansikt, heilt bak = stemning mot veggen.
Rekna fridomsgrad: α. Søkt: hengslehøgd zh, hengsledjupn yh, lokdjupn b.
Lover: lys (felles), synsfelt >= 15° i arbeid, lepper mot svikt, søyle mot svikt, friksjonshengsle som held loket, tipp.
Forgjengar: bok_forkasta/ (ståande falda bok: 3,4–4,7 klm, stemninga hamna på bordet, paret stod i musesona).
"""
import os, sys, math, json
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
sys.path.insert(0, ROOT)
import felles as fe

E_ALU, RHO_ALU, K_ALU = 70e9, 2700, 200.0
ETA_OPT, PK = 0.70, 1.3        # PREMISS: optikk (linsevaska reflektor eller kantlyst leiar) gjev η 0,70 og topp/snitt 1,3. Ikkje løyst.
SYN_MIN = 15.0
ALFA = list(np.radians(np.arange(-30, 231, 5)))
T_PL, LIP = 0.0015, 0.020      # plate 1,5 mm, returfald 20 mm
COL_W, COL_F, COL_T = 0.10, 0.03, 0.002   # U-profil i søyla
FOT = (0.24, 0.30, 0.003)      # breidd x, djupn y, tjukn
M_SKJERM = 4.0                 # kg, skjermen står på foten (premiss)
BASE = dict(id=1, rad=1, kol=1, namn='lok', L=0.60, b=0.32, yh=0.50, zh=0.68)
FINAL = dict(BASE)


def vek(a):
    return np.array([0.0, -math.cos(a), math.sin(a)]), np.array([0.0, -math.sin(a), -math.cos(a)])   # lokretning, lysnormal


def opning(B, a, nt=None, n=None):
    f, nn = vek(a)
    H = np.array([0.0, B['yh'], B['zh']])
    ks, kb = (12, 5) if n is None else (36, 12)
    xs = (np.arange(ks) + .5) / ks * B['L'] - B['L'] / 2
    ss = (np.arange(kb) + .5) / kb * B['b']
    P = np.array([H + [x, 0, 0] + s * f for x in xs for s in ss])
    return P, np.tile(nn, (len(P), 1)), np.full(len(P), B['L'] / ks * B['b'] / kb)


def eta(B):
    return ETA_OPT


def kollisjon(B, a, arbeid):
    f, _ = vek(a)
    pts = np.array([[B['yh'], B['zh']] + s * B['b'] * f[1:] for s in np.linspace(0, 1, 9)])
    if (pts[:, 0] > 0.73).any() or ((pts[:, 0] < 0.50 - 1e-9) & (pts[:, 1] < 0.50)).any():
        return True
    if ((pts[:, 0] > 0.43) & (pts[:, 0] < 0.49) & (pts[:, 1] < 0.44)).any():
        return True
    if arbeid:
        e = fe.EYES[0]
        if (np.degrees(np.arctan2(pts[:, 1] - e[2], pts[:, 0] - e[1])) < SYN_MIN).any():
            return True
    return False


def sok(B):
    S = fe.sok(B, ALFA, opning, eta(B), ring=False)
    rows = S['rows']
    for r in rows:
        r['Lap'] = r['k'] * r['Phi'] * PK
        r['glare_ok'] = (not r['vis'] or r['Lap'] <= fe.L_MAX) and (not r['refl'] or r['Lap'] <= fe.L_MAX)
        r['kolli'] = kollisjon(B, r['s'], False)
    fw = [r for r in rows if r['glare_ok'] and r['U0'] >= fe.U0_MIN and not kollisjon(B, r['s'], True)]
    W = min(fw or rows, key=lambda r: r['Phi'])
    for r in rows:
        r['L_stem'] = r['k'] * W['Phi'] * fe.DIM_STEM * PK
        r['stem_ok'] = (not r['vis'] and not r['refl']) or r['L_stem'] <= fe.L_STEM_MAX
        r['Ev_stem'] = r['Ew'] * W['Phi'] * fe.DIM_STEM
    fm = [r for r in rows if not r['kolli'] and r['stem_ok']]
    Mo = max(fm or rows, key=lambda r: (r['R_stem'] >= fe.R_STEM_MIN, r['Ev_stem']))
    Fa = max([r for r in rows if not r['kolli']], key=lambda r: r['face'])
    i0, i1 = sorted((rows.index(W), rows.index(Mo)))
    veg = list(range(i0, i1 + 1))
    if rows.index(W) > rows.index(Mo):
        veg = veg[::-1]
    def ok_steg(j, i):
        f = 1 - 0.75 * j / max(len(veg) - 1, 1)
        return not rows[i]['kolli'] and not ((rows[i]['vis'] or rows[i]['refl']) and rows[i]['Lap'] * f > fe.L_MAX)
    fri = all(ok_steg(j, i) for j, i in enumerate(veg))
    S.update(work=W, mood=Mo, face=Fa, veg=veg if fri else None, sveip='fri' if fri else 'stengd', steg=len(veg) - 1,
             L150=fe.E_FACE / max(Fa['face'], 1e-12) * PK, Phi150=fe.E_FACE / max(Fa['face'], 1e-12) / Fa['k'],
             ok=bool(fw) and fri and Mo['R_stem'] >= fe.R_STEM_MIN and bool(Mo['stem_ok']))
    return S


# ---------------- geometri ----------------
def rekt(x0, x1, y0, y1, z0, z1):
    return fe.prism(np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]]), z0, z1)


def geometri(B, a):
    f, nn = vek(a)
    H = np.array([0.0, B['yh'], B['zh']])
    meshes, emit = [], []
    nu, nv = 24, 12
    for off, em in ((0.0, True), (T_PL, False)):                      # lysande underside, rygg
        V = [H + [B['L'] * (i / nu - 0.5), 0, 0] + (B['b'] * j / nv) * f - off * nn for i in range(nu + 1) for j in range(nv + 1)]
        F = []
        for i in range(nu):
            for j in range(nv):
                q = i * (nv + 1) + j
                F += [(q, q + nv + 1, q + nv + 2), (q, q + nv + 2, q + 1)]
        meshes.append((np.array(V), F)); emit.append(np.full(len(F), em))
    def quad(p0, p1, p2, p3):
        meshes.append((np.array([p0, p1, p2, p3]), [(0, 1, 2), (0, 2, 3)])); emit.append(np.zeros(2, bool))
    for sx in (-1, 1):                                                 # sidelepper og frontleppe (returfald mot lyssida)
        o = H + [sx * B['L'] / 2, 0, 0]
        quad(o, o + B['b'] * f, o + B['b'] * f + LIP * nn, o + LIP * nn)
    o = H + B['b'] * f
    quad(o + [-B['L'] / 2, 0, 0], o + [B['L'] / 2, 0, 0], o + [B['L'] / 2, 0, 0] + LIP * nn, o + [-B['L'] / 2, 0, 0] + LIP * nn)
    meshes.append(fe.frustum(H - [B['L'] / 2, 0, 0], H + [B['L'] / 2, 0, 0], 0.008, 0.008, 16)); emit.append(np.zeros(len(meshes[-1][1]), bool))
    yb = B['yh'] + 0.012                                               # søyle: U-profil bak skjermen
    for m in (rekt(-COL_W / 2, COL_W / 2, yb + COL_F - COL_T, yb + COL_F, FOT[2], B['zh']),
              rekt(-COL_W / 2, -COL_W / 2 + COL_T, yb, yb + COL_F, FOT[2], B['zh']),
              rekt(COL_W / 2 - COL_T, COL_W / 2, yb, yb + COL_F, FOT[2], B['zh']),
              rekt(-FOT[0] / 2, FOT[0] / 2, yb + COL_F - FOT[1], yb + COL_F, 0.0, FOT[2])):
        meshes.append(m); emit.append(np.zeros(len(m[1]), bool))
    V, F = fe.merge(meshes)
    return V, F, np.concatenate(emit)


def tal(B, S=None):
    S = S or sok(B)
    W, Mo = S['work'], S['mood']
    f, nn = vek(W['s'])
    H = np.array([0.0, B['yh'], B['zh']])
    m_lok = RHO_ALU * T_PL * (B['L'] * B['b'] + LIP * (2 * B['b'] + B['L'])) + 0.15
    A_col = (COL_W + 2 * COL_F) * COL_T
    yb = B['yh'] + 0.012
    m_col = RHO_ALU * A_col * B['zh']
    m_fot = RHO_ALU * FOT[0] * FOT[1] * FOT[2]
    parts = [(m_lok, H + B['b'] / 2 * f), (0.15, H), (m_col, np.array([0, yb + COL_F / 2, B['zh'] / 2])),
             (m_fot + 0.15, np.array([0, yb + COL_F - FOT[1] / 2, 0.002]))]
    kont = np.array([[-FOT[0] / 2, yb + COL_F - FOT[1]], [FOT[0] / 2, yb + COL_F - FOT[1]], [FOT[0] / 2, yb + COL_F], [-FOT[0] / 2, yb + COL_F]])
    # friksjonshengsla må halde loket vassrett: T >= m g b/2. Gestkrafta ved frontleppa: F = 1,3·T/b
    T_h = m_lok * fe.G * B['b'] / 2
    F_g = 1.3 * T_h / B['b']
    st_a = fe.stabilitet(parts, [kont], B['zh'], F_g)
    st_m = fe.stabilitet(parts + [(M_SKJERM, np.array([0, 0.50, 0.20]))], [kont], B['zh'], F_g)
    # svikt: frontleppa under F_g. Flat plate mot plate med sidelepper (returfalden ber)
    I_flat = B['L'] * T_PL ** 3 / 12
    I_lip = I_flat + 2 * T_PL * LIP ** 3 / 3
    sv_flat = F_g * B['b'] ** 3 / (3 * E_ALU * I_flat) * 1000
    sv_lok = F_g * B['b'] ** 3 / (3 * E_ALU * I_lip) * 1000
    # søyle: U-profil, bøying fram/tilbake (flensane i bøyeretninga), last F_g + moment T_h i toppen
    c = (2 * COL_F * COL_T * COL_F / 2 + COL_W * COL_T * COL_T / 2) / A_col
    I_col = 2 * (COL_T * COL_F ** 3 / 12 + COL_T * COL_F * (COL_F / 2 - c) ** 2) + COL_W * COL_T ** 3 / 12 + COL_W * COL_T * (c - COL_T / 2) ** 2
    sv_col = (F_g * B['zh'] ** 3 / 3 + 1.3 * T_h * B['zh'] ** 2 / 2) / (E_ALU * I_col) * 1000
    V = geometri(B, W['s'])[0]
    mL = math.sqrt(2 * fe.H_CONV / (K_ALU * T_PL)) * B['b']
    A_kj = 2 * B['L'] * B['b'] * math.tanh(mL) / mL
    t = fe.tal_felles(B, S, st_m, V[V[:, 2] > 0.01], sv_lok + sv_col, A_kj)
    t.update(L_arb_topp=W['Lap'], synleg_arb=bool(W['vis']), alfa_arb=math.degrees(W['s']), alfa_stem=math.degrees(Mo['s']),
             alfa_ansikt=math.degrees(S['face']['s']), sving=abs(math.degrees(Mo['s'] - W['s'])), Phi_ansikt=S['Phi150'],
             T_hengsle=T_h, tipp_aleine=st_a['tipp_deg'], F_tipp_aleine=st_a['F_tipp_N'], masse_kg=st_a['masse_kg'], fot_cm2=st_a['fot_cm2'],
             svikt_lok_flat_mm=sv_flat, svikt_lok_mm=sv_lok, svikt_soyle_mm=sv_col, eta=ETA_OPT, toppfaktor=PK,
             L=B['L'], b=B['b'], yh=B['yh'], zh=B['zh'])
    fl = fe.standard_flagg(t)
    if st_a['F_tipp_N'] < 2 * F_g: fl.append('gest veltar utan skjerm på foten')
    t['flagg'] = '; '.join(fl) or '-'
    return t, S


def search():
    res = []
    for yh in (0.50, 0.52):
        for zh in (0.64, 0.66, 0.68, 0.70, 0.74):
            for b in (0.24, 0.28, 0.32, 0.36):
                B = dict(BASE, yh=yh, zh=zh, b=b)
                S = sok(B); W, Mo = S['work'], S['mood']
                res.append(dict(yh=yh, zh=zh, b=b, ok=S['ok'], Phi=float(W['Phi']), U0=float(W['U0']), L=float(W['Lap']), Rst=float(Mo['R_stem']),
                                Ev=float(Mo['Ev_stem']), L150=float(S['L150']), aw=math.degrees(W['s']), am=math.degrees(Mo['s'])))
    json.dump(res, open(os.path.join(HER, 'sok.json'), 'w'), indent=1)
    return res


if __name__ == '__main__':
    res = search()
    ok = [r for r in res if r['ok']]
    print(len(res), 'køyrt', len(ok), 'ok')
    for r in sorted(ok, key=lambda r: r['Phi'])[:8]:
        print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})
