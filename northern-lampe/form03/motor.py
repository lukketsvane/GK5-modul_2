"""form03 «Flak» — motor: fald. Lyset er ei flate, ikkje ei line.

Kropp: fot under skjermen, falda U-søyle bak han, arm fram over han, og eit balansert lysande brett som vippar om midtlina si.
Gest: vipp brettet (α). 0 = lysflata ned (arbeid), framkanten ned = lysflata mot veggen (stemning), framkanten opp = mot deg (ansikt).
Rekna fridomsgrad: α. Søkt: vippeakse (yp, zp) og brettdjupn b.
Lover: lys (felles; synleg flate er lov når L_topp <= 3000 cd/m2), synsfelt >= 15° i arbeid, lepper og søyle mot svikt, tipp.
Forkasta på vegen (same dag, sjå logg.md):
  bok_forkasta/  ståande falda bok: 3,4–4,7 klm, stemninga hamna på bordet, paret stod i musesona.
  lok_forkasta/  lok hengsla i bakkant: slo i veggen på veg til stemning, og ubalansert (hengsla måtte halde 1,4 N·m).
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
T_FRIK = 0.30                  # N·m, friksjon i vippeleddet (brettet er balansert om aksen)
ALFA = list(np.radians(np.arange(-120, 101, 5)))
T_PL, LIP = 0.0015, 0.020      # plate 1,5 mm, returfald 20 mm
COL_W, COL_F, COL_T = 0.10, 0.03, 0.002   # U-profil i søyle og arm
COL_Y = 0.512                  # framsida av søyla (rett bak skjermen)
FOT = (0.24, 0.30, 0.004)      # breidd x, djupn y, tjukn (4 mm: 3 mm velta ved 2x gestkraft utan skjerm, 4,64 < 4,80 N)
M_SKJERM = 4.0                 # kg, skjermen står på foten (premiss)
BASE = dict(id=1, rad=1, kol=1, namn='flak', L=0.60, b=0.25, yp=0.30, zp=0.66)
FINAL = dict(BASE, yp=0.26, zp=0.64, b=0.25)      # frå sok.json: robust punkt, ikkje gitterkanten


def vek(a):
    return np.array([0.0, -math.cos(a), math.sin(a)]), np.array([0.0, -math.sin(a), -math.cos(a)])   # framkantretning, lysnormal


def opning(B, a, nt=None, n=None):
    f, nn = vek(a)
    C = np.array([0.0, B['yp'], B['zp']])
    ks, kb = (12, 5) if n is None else (36, 12)
    xs = (np.arange(ks) + .5) / ks * B['L'] - B['L'] / 2
    ss = ((np.arange(kb) + .5) / kb - 0.5) * B['b']
    P = np.array([C + [x, 0, 0] + s * f for x in xs for s in ss])
    return P, np.tile(nn, (len(P), 1)), np.full(len(P), B['L'] / ks * B['b'] / kb)


def eta(B):
    return ETA_OPT


def kollisjon(B, a, arbeid):
    f, _ = vek(a)
    pts = np.array([[B['yp'], B['zp']] + s * B['b'] * f[1:] for s in np.linspace(-0.5, 0.5, 9)])
    if (pts[:, 0] > 0.73).any() or ((pts[:, 0] < 0.50) & (pts[:, 1] < 0.50)).any():
        return True
    if ((pts[:, 0] > 0.43) & (pts[:, 0] < 0.49) & (pts[:, 1] < 0.44)).any():
        return True
    if (pts[:, 0] > COL_Y - 0.01).any():                              # brettet skal gå klar av søyla
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
    Fa = max([r for r in rows if not r['kolli']] or rows, key=lambda r: r['face'])
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
             ok=bool(bool(fw) and fri and Mo['R_stem'] >= fe.R_STEM_MIN and Mo['stem_ok']))
    return S


# ---------------- geometri ----------------
def rekt(x0, x1, y0, y1, z0, z1):
    return fe.prism(np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]]), z0, z1)


def geometri(B, a):
    f, nn = vek(a)
    C = np.array([0.0, B['yp'], B['zp']])
    meshes, emit = [], []
    nu, nv = 24, 12
    for off, em in ((0.0, True), (T_PL, False)):                      # lysande side, rygg
        V = [C + [B['L'] * (i / nu - 0.5), 0, 0] + (B['b'] * (j / nv - 0.5)) * f - off * nn for i in range(nu + 1) for j in range(nv + 1)]
        F = []
        for i in range(nu):
            for j in range(nv):
                q = i * (nv + 1) + j
                F += [(q, q + nv + 1, q + nv + 2), (q, q + nv + 2, q + 1)]
        meshes.append((np.array(V), F)); emit.append(np.full(len(F), em))

    def quad(p0, p1, p2, p3):
        meshes.append((np.array([p0, p1, p2, p3]), [(0, 1, 2), (0, 2, 3)])); emit.append(np.zeros(2, bool))
    hb = B['b'] / 2
    for sx in (-1, 1):                                                 # fire lepper (returfald mot lyssida)
        o = C + [sx * B['L'] / 2, 0, 0]
        quad(o - hb * f, o + hb * f, o + hb * f + LIP * nn, o - hb * f + LIP * nn)
    for sf in (-1, 1):
        o = C + sf * hb * f
        quad(o + [-B['L'] / 2, 0, 0], o + [B['L'] / 2, 0, 0], o + [B['L'] / 2, 0, 0] + LIP * nn, o + [-B['L'] / 2, 0, 0] + LIP * nn)

    def add(m):
        meshes.append(m); emit.append(np.zeros(len(m[1]), bool))
    za = B['zp'] + 0.02                                                # underkant arm; vippeaksen heng 2 cm under
    add(fe.frustum(C - [COL_W / 2 + 0.01, 0, 0], C + [COL_W / 2 + 0.01, 0, 0], 0.010, 0.010, 16))          # nav
    yb = COL_Y
    for sx in (-1, 1):                                                 # kinn ned til navet + flensar i arm og søyle
        add(rekt(sx * COL_W / 2 - 0.001, sx * COL_W / 2 + 0.001, B['yp'] - 0.012, B['yp'] + 0.012, B['zp'] - 0.012, za + COL_F))
        add(rekt(sx * COL_W / 2 - 0.001, sx * COL_W / 2 + 0.001, B['yp'] - 0.012, yb + COL_F, za, za + COL_F))
        add(rekt(sx * COL_W / 2 - 0.001, sx * COL_W / 2 + 0.001, yb, yb + COL_F, FOT[2], za))
    add(rekt(-COL_W / 2, COL_W / 2, B['yp'] - 0.012, yb + COL_F, za + COL_F - COL_T, za + COL_F))            # arm: U opp ned
    add(rekt(-COL_W / 2, COL_W / 2, yb + COL_F - COL_T, yb + COL_F, FOT[2], za + COL_F))                     # søyle: U
    add(rekt(-FOT[0] / 2, FOT[0] / 2, yb + COL_F - FOT[1], yb + COL_F, 0.0, FOT[2]))                          # fot under skjermen
    V, F = fe.merge(meshes)
    return V, F, np.concatenate(emit)


def tal(B, S=None):
    S = S or sok(B)
    W, Mo = S['work'], S['mood']
    C = np.array([0.0, B['yp'], B['zp']])
    za = B['zp'] + 0.02
    m_brett = RHO_ALU * T_PL * (B['L'] * B['b'] + LIP * 2 * (B['b'] + B['L'])) + 0.15
    A_col = (COL_W + 2 * COL_F) * COL_T
    L_arm = COL_Y + COL_F - B['yp']
    m_col, m_arm = RHO_ALU * A_col * za, RHO_ALU * A_col * L_arm
    m_fot = RHO_ALU * FOT[0] * FOT[1] * FOT[2]
    yb = COL_Y
    parts = [(m_brett + 0.08, C), (m_arm, np.array([0, B['yp'] + L_arm / 2, za])), (m_col, np.array([0, yb + COL_F / 2, za / 2])),
             (m_fot + 0.15, np.array([0, yb + COL_F - FOT[1] / 2, 0.002]))]
    kont = np.array([[-FOT[0] / 2, yb + COL_F - FOT[1]], [FOT[0] / 2, yb + COL_F - FOT[1]], [FOT[0] / 2, yb + COL_F], [-FOT[0] / 2, yb + COL_F]])
    F_g = T_FRIK / (B['b'] / 2)                                        # fingerkraft på brettkanten
    st_a = fe.stabilitet(parts, [kont], B['zp'], F_g)
    st_m = fe.stabilitet(parts + [(M_SKJERM, np.array([0, 0.50, 0.20]))], [kont], B['zp'], F_g)
    # svikt: brettkanten under F_g, utkraga b/2 frå aksen. Flat plate mot plate med lepper
    I_flat = B['L'] * T_PL ** 3 / 12
    I_lip = I_flat + 2 * T_PL * LIP ** 3 / 3
    sv_flat = F_g * (B['b'] / 2) ** 3 / (3 * E_ALU * I_flat) * 1000
    sv_brett = F_g * (B['b'] / 2) ** 3 / (3 * E_ALU * I_lip) * 1000
    # U-profil, bøying fram/tilbake: arm (L_arm) + rotasjon i søyletoppen frå momentet F_g·a
    c = (2 * COL_F * COL_T * COL_F / 2 + COL_W * COL_T * COL_T / 2) / A_col
    I_col = 2 * (COL_T * COL_F ** 3 / 12 + COL_T * COL_F * (COL_F / 2 - c) ** 2) + COL_W * COL_T ** 3 / 12 + COL_W * COL_T * (c - COL_T / 2) ** 2
    a_ = L_arm + B['b'] / 2
    sv_arm = F_g * L_arm ** 3 / (3 * E_ALU * I_col) * 1000
    sv_col = (F_g * a_) * za * a_ / (E_ALU * I_col) * 1000
    ned = (m_brett + 0.08) * fe.G * (L_arm ** 3 / 3 + L_arm ** 2 * za) / (E_ALU * I_col) * 1000     # statisk, frå vekta
    V = geometri(B, W['s'])[0]
    mL = math.sqrt(2 * fe.H_CONV / (K_ALU * T_PL)) * (B['b'] / 2)
    A_kj = 2 * B['L'] * B['b'] * math.tanh(mL) / mL
    t = fe.tal_felles(B, S, st_m, V[V[:, 2] > 0.01], sv_brett + sv_arm + sv_col, A_kj)
    t.update(L_arb_topp=W['Lap'], synleg_arb=bool(W['vis']), alfa_arb=math.degrees(W['s']), alfa_stem=math.degrees(Mo['s']),
             alfa_ansikt=math.degrees(S['face']['s']), sving=abs(math.degrees(Mo['s'] - W['s'])), Phi_ansikt=S['Phi150'],
             tipp_aleine=st_a['tipp_deg'], F_tipp_aleine=st_a['F_tipp_N'], masse_kg=st_a['masse_kg'], fot_cm2=st_a['fot_cm2'],
             svikt_brett_flat_mm=sv_flat, svikt_brett_mm=sv_brett, svikt_arm_mm=sv_arm, svikt_soyle_mm=sv_col, nedboying_mm=ned,
             eta=ETA_OPT, toppfaktor=PK, L=B['L'], b=B['b'], yp=B['yp'], zp=B['zp'], L_arm=L_arm)
    fl = fe.standard_flagg(t)
    if st_a['tipp_deg'] < fe.TIP_MIN or st_a['F_tipp_N'] < 2 * F_g:
        fl.append('veltar utan skjerm på foten')
    t['flagg'] = '; '.join(fl) or '-'
    return t, S


def search():
    res = []
    for yp in (0.22, 0.26, 0.30, 0.34, 0.38):
        for zp in (0.60, 0.64, 0.68, 0.72):
            for b in (0.20, 0.25, 0.30):
                B = dict(BASE, yp=yp, zp=zp, b=b)
                S = sok(B); W, Mo = S['work'], S['mood']
                res.append(dict(yp=yp, zp=zp, b=b, ok=S['ok'], Phi=float(W['Phi']), U0=float(W['U0']), L=float(W['Lap']), vis=bool(W['vis']),
                                Rst=float(Mo['R_stem']), Ev=float(Mo['Ev_stem']), L150=float(S['L150']), aw=math.degrees(W['s']),
                                am=math.degrees(Mo['s']), af=math.degrees(S['face']['s']), sveip=S['sveip']))
    json.dump(res, open(os.path.join(HER, 'sok.json'), 'w'), indent=1)
    return res


if __name__ == '__main__':
    res = search()
    ok = [r for r in res if r['ok']]
    print(len(res), 'køyrt', len(ok), 'ok')
    for r in sorted(ok, key=lambda r: r['Phi'])[:10]:
        print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})
    if not ok:
        for r in sorted(res, key=lambda r: r['Phi'])[:6]:
            print('ikkje ok:', {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})


GESTORD = 'vippa'


def render_kropp(B, path):
    from PIL import Image
    S = sok(B)
    ims = []
    for st in (S['work']['s'], S['mood']['s'], S['face']['s']):
        V, F, emit = geometri(B, st)
        V = V.copy(); V[:, 1] -= 0.45
        im, _ = fe.render(V, F, fe.Cam(S=2048, el=17, az=240, fov=19, D=4.6, target=(0, 0, 0.36)), emit=emit)
        ims.append(im)
    out = Image.new('RGB', (ims[0].width * 3, ims[0].height), 'black')
    for j, im in enumerate(ims):
        out.paste(im, (j * im.width, 0))
    out.save(path)
    return S
