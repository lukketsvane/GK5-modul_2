"""form01 «Huske» — éin kropp i fokus, forma av Levin-prøvane (levin.md, utfall.md).

Grep: ein bøygd lysbøyle heng mellom to A-bukkar og svingar om lina mellom endane (bøttehank).
Gesten ψ flyttar sjølve kjelda: fram og ned over oppgåva (arbeid), opp og bak mot veggen (stemning).
Rekna fridomsgrad: ψ. Søkt éin gong: pilhøgd g, opningsvinkel φr i bøylen, aksehøgd og -djupn.
Lover: lys (felles), kjøling (bøylen er kjøleflata), A-bukk mot svikt, tipp i begge tilstandar.
"""
import os, sys, math, json
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
sys.path.insert(0, ROOT)
import felles as fe

E_ALU, RHO_ALU = 70e9, 2700
T_DET = 0.08
SYN_MIN = 15.0      # premiss (ny): bøylen over skjermbreidda minst 15° over augehøgd sett frå auga — «ro ved skjermen»
PSIS = list(np.radians(np.arange(-180, 180, 5)))
BASE = dict(id=1, rad=1, kol=1, namn='huske', L=0.62, R=0.022, beta=25.0, k=0.90, n=33,
            g=0.15, phir=0.0, yp=0.44, hp=0.72, a=0.20, t_bow=0.0012, D_leg=0.020, t_leg=0.0015)


def e_dir(psi):
    return np.array([0.0, -math.sin(psi), -math.cos(psi)])      # 0: ned, +90: mot brukaren, -90: mot veggen


def bow(B, psi, n=None):
    n = n or B['n']
    t = np.linspace(-1, 1, n)
    e = e_dir(psi)
    C = np.c_[t * B['L'] / 2, np.full_like(t, B['yp']), np.full_like(t, B['hp'])] + B['g'] * (1 - t ** 2)[:, None] * e
    U = np.gradient(C, axis=0); U /= np.linalg.norm(U, axis=1, keepdims=True)
    W = e[None] - (U @ e)[:, None] * U
    W /= np.linalg.norm(W, axis=1, keepdims=True)
    return t, C, U, W, np.cross(U, W)


def opning(B, psi, nt=3, n=None):
    t, C, U, W, V = bow(B, psi, n)
    tm = (t[:-1] + t[1:]) / 2
    Cm = (C[:-1] + C[1:]) / 2
    Um, Wm, Vm = [(X[:-1] + X[1:]) / 2 for X in (U, W, V)]
    ds = np.linalg.norm(np.diff(C, axis=0), axis=1)
    keep = np.abs(tm) <= B['k']
    pr = math.radians(B['phir'])
    nn = math.cos(pr) * Wm + math.sin(pr) * Vm
    nn /= np.linalg.norm(nn, axis=1, keepdims=True)
    td = np.cross(Um, nn)
    be = math.radians(B['beta'])
    half, off = B['R'] * math.sin(be), B['R'] * math.cos(be)
    P, N, dA = [], [], []
    for s in (np.arange(nt) + 0.5) / nt * 2 - 1:
        P.append((Cm + off * nn + s * half * td)[keep]); N.append(nn[keep]); dA.append((ds * 2 * half / nt)[keep])
    return np.vstack(P), np.vstack(N), np.concatenate(dA)


def arc_len(B):
    _, C, *_ = bow(B, 0.0)
    return float(np.linalg.norm(np.diff(C, axis=0), axis=1).sum())


def eta(B):
    A_ap = opning(B, 0.0)[2].sum()
    Lcav = arc_len(B) * B['k']          # endeskiver der opninga sluttar: hulrommet er berre så langt som opninga
    f = A_ap / (2 * math.pi * B['R'] * Lcav + 2 * math.pi * B['R'] ** 2)
    sb = math.sin(math.radians(B['beta']))
    return min(1.0, sb + (1 - sb) * fe.RHO * f / (1 - fe.RHO * (1 - f)))


def kollisjon(B, psi):
    """Bøylen mot forbode volum (siktline/hender) og skjermkassa."""
    _, C, *_ = bow(B, psi, 25)
    r = B['R']
    fx0, fx1, fy0, fy1, fz0, fz1 = fe.FORBID
    inn = (C[:, 0] > fx0) & (C[:, 0] < fx1) & (C[:, 1] > fy0 - r) & (C[:, 1] < fy1 + r) & (C[:, 2] < fz1 + r)
    scr = (np.abs(C[:, 0]) < fe.SCR['x1'] + r) & (C[:, 1] > fe.SCR['y'] - r) & (C[:, 1] < fe.SCR['y'] + 0.02 + r) & (C[:, 2] < fe.SCR['z1'] + r)
    e0 = fe.EYES[0]
    over = np.abs(C[:, 0]) < 0.35
    elev = np.degrees(np.arctan2(C[:, 2] - r - e0[2], C[:, 1] - e0[1]))
    syn = over & (elev < SYN_MIN)
    return bool(inn.any() or scr.any() or syn.any())


def sok(B):
    S = fe.sok(B, PSIS, opning, eta(B))
    rows = S['rows']; n = len(rows)
    i0, i1 = rows.index(S['work']), rows.index(S['mood'])
    a = [(i0 + j) % n for j in range((i1 - i0) % n + 1)]
    b = [(i0 - j) % n for j in range((i0 - i1) % n + 1)]
    ok_path = [p for p in (a, b) if not any(kollisjon(B, rows[j]['s']) for j in p)
               and not any(rows[j]['vis'] and rows[j]['Lap'] > fe.L_MAX for j in p)]
    S['veg'] = min(ok_path, key=len) if ok_path else None
    S['kolli_arb'] = kollisjon(B, S['work']['s'])
    return S


def score(S):
    W, M = S['work'], S['mood']
    ok = W['glare_ok'] and W['U0'] >= fe.U0_MIN and M['R_stem'] >= fe.R_STEM_MIN and M['stem_ok'] \
        and S['veg'] is not None and not S['kolli_arb']
    return bool(ok), W['Phi']


def search():
    res = []
    for g in (0.0, 0.05, 0.10, 0.15):
        for yp in (0.30, 0.35, 0.40):
            for hp in (0.58, 0.62, 0.66):
                for pr in ((0.0,) if g == 0 else (15, 30, 45, 60)):
                    B = dict(BASE, g=g, yp=yp, hp=hp, phir=float(pr))
                    S = sok(B)
                    ok, Phi = score(S)
                    W, M = S['work'], S['mood']
                    res.append(dict(g=g, yp=yp, hp=hp, phir=pr, ok=ok, Phi=float(W['Phi']), U0=float(W['U0']), Rst=float(M['R_stem']),
                                    Ev=float(M['Ev_stem']), psi_w=math.degrees(W['s']), psi_m=math.degrees(M['s']),
                                    steg=len(S['veg']) - 1 if S['veg'] else -1, glare=bool(W['glare_ok']), kolli=bool(S['kolli_arb'])))
                    print(f"g={g:.2f} yp={yp:.2f} hp={hp:.2f} phir={pr:+.0f} ok={ok} Phi={W['Phi']:.0f} U0={W['U0']:.2f} "
                          f"Rst={M['R_stem']:.2f} psi_w={math.degrees(W['s']):+.0f} psi_m={math.degrees(M['s']):+.0f} "
                          f"veg={'-' if not S['veg'] else len(S['veg'])-1}", flush=True)
    json.dump(res, open(os.path.join(HER, 'sok.json'), 'w'), indent=1)
    return res


# ---------------- geometri ----------------
def tube_along(C, U, W, V, R, n_th=40, cut=None):
    """Røyr langs kurve. cut(i, theta)->True fjernar flata (opning)."""
    th = np.arange(n_th) / n_th * 2 * np.pi
    ring = np.cos(th)[None, :, None] * W[:, None] + np.sin(th)[None, :, None] * V[:, None]
    Vt = (C[:, None] + R * ring).reshape(-1, 3)
    F = []
    for i in range(len(C) - 1):
        for j in range(n_th):
            if cut is not None and cut(i, th[j] + np.pi / n_th):
                continue
            a, b = i * n_th + j, i * n_th + (j + 1) % n_th
            F += [(a, b, b + n_th), (a, b + n_th, a + n_th)]
    # endelokk
    for i in (0, len(C) - 1):
        o = len(Vt)
        Vt = np.vstack([Vt, C[i][None], C[i] + R * ring[i]])
        F += [(o, o + 1 + j, o + 1 + (j + 1) % n_th) for j in range(n_th)]
    return Vt, F


def geometri(B, psi):
    t, C, U, W, V = bow(B, psi, 61)
    pr, be = math.radians(B['phir']), math.radians(B['beta'])
    tm = (t[:-1] + t[1:]) / 2
    cut = lambda i, th: abs(tm[i]) <= B['k'] and abs((th - pr + np.pi) % (2 * np.pi) - np.pi) < be
    meshes = [tube_along(C, U, W, V, B['R'], 48, cut)]
    nb = len(meshes[0][1])
    # lysande korde
    nn = math.cos(pr) * W + math.sin(pr) * V
    td = np.cross(U, nn)
    Va, Fa = [], []
    for i in range(len(C) - 1):
        if abs(tm[i]) > B['k']:
            continue
        q = []
        for j in (i, i + 1):
            c = C[j] + B['R'] * math.cos(be) * 0.97 * nn[j]
            q.append((c - B['R'] * math.sin(be) * td[j], c + B['R'] * math.sin(be) * td[j]))
        o = len(Va)
        Va += [q[0][0], q[1][0], q[1][1], q[0][1]]
        Fa += [(o, o + 1, o + 2), (o, o + 2, o + 3)]
    meshes.append((np.array(Va), Fa))
    ne = len(Fa)
    # A-bukkar, navar, grep
    xe = B['L'] / 2 + 0.016
    rl = B['D_leg'] / 2
    legs = []
    for sx in (-1, 1):
        apex = np.array([sx * xe, B['yp'], B['hp']])
        for sy in (-1, 1):
            foot = np.array([sx * xe, B['yp'] + sy * B['a'], rl])
            legs.append((apex, foot))
            meshes.append(fe.frustum(foot, apex, rl, rl, 16))
        meshes.append(fe.frustum(np.array([sx * (B['L'] / 2 - 0.005), B['yp'], B['hp']]), apex + np.array([sx * 0.012, 0, 0]),
                                 B['R'] * 0.55, B['R'] * 0.55, 24))
    gp = np.array([xe + 0.012, B['yp'], B['hp']])
    meshes.append(fe.frustum(gp, gp + np.array([0.034, 0, 0]), 0.026, 0.026, 32))        # vridegrep berre til høgre
    V_, F_ = fe.merge(meshes)
    emit = np.zeros(len(F_), bool)
    emit[nb:nb + ne] = True
    return V_, F_, emit, legs


def tal(B, S=None):
    S = S or sok(B)
    W, M = S['work'], S['mood']
    Larc = arc_len(B)
    rows = {}
    for lab, st in (('arbeid', W['s']), ('stemning', M['s'])):
        V_, F_, emit, legs = geometri(B, st)
        _, C, *_ = bow(B, st, 61)
        m_bow = RHO_ALU * math.pi * 2 * B['R'] * B['t_bow'] * Larc * (1 - B['k'] * B['beta'] / 180)
        Aleg = math.pi / 4 * (B['D_leg'] ** 2 - (B['D_leg'] - 2 * B['t_leg']) ** 2)
        parts = [(m_bow, C.mean(0)), (0.10, C[len(C) // 2]), (0.06, np.array([B['L'] / 2 + 0.04, B['yp'], B['hp']])),
                 (0.03, np.array([-B['L'] / 2, B['yp'], B['hp']]))]
        for ap, ft in legs:
            parts.append((RHO_ALU * Aleg * np.linalg.norm(ap - ft), (ap + ft) / 2))
        feet = np.array([[f[0], f[1]] for _, f in legs])
        st_ = fe.stabilitet(parts, [feet], B['hp'], T_DET / 0.026)
        st_['M_res'] = st_['F_tipp_N'] * B['hp']
        rows[lab] = (st_, V_)
    sa, Va = rows['arbeid']
    sm, _ = rows['stemning']
    # svikt: kraftpar om aksen går i planet til A-bukken (triangulert). Tilfeldig dytt 10 N i x på apex: 4 røyr ut av planet.
    I = math.pi / 64 * (B['D_leg'] ** 4 - (B['D_leg'] - 2 * B['t_leg']) ** 4)
    Lleg = math.hypot(B['hp'], B['a'])
    svikt_x = (fe.F_PUSH / 4) * Lleg ** 3 / (3 * E_ALU * I) * 1000
    A_kjol = math.pi * 2 * B['R'] * Larc * (1 - B['k'] * B['beta'] / 180)
    t = fe.tal_felles(B, S, sa, Va, svikt_x, A_kjol)
    t.update(tipp_stem=sm['tipp_deg'], M_res_arb=sa['M_res'], M_res_stem=sm['M_res'], grep_ratio=min(sa['M_res'], sm['M_res']) / T_DET,
             psi_arb=math.degrees(W['s']), psi_stem=math.degrees(M['s']), sving=len(S['veg']) * 5 - 5 if S['veg'] else -1,
             g=B['g'], phir=B['phir'], yp=B['yp'], hp=B['hp'], L_bue=Larc, eta=eta(B))
    return t, S


if __name__ == '__main__':
    search()


# ---------------- endeleg kropp (etter sok3: synsfelt 15°, rett røyr vann) ----------------
FINAL = dict(BASE, namn='bru', g=0.0, phir=0.0, yp=0.25, hp=0.62, L=1.12, k=0.536)
MUS = (0.30, 0.55, 0.0, 0.35)          # premiss (ny): musesona til høgre for tastaturet


def render_kropp(B, path):
    from PIL import Image
    S = sok(B)
    ims = []
    for st in (S['work']['s'], S['mood']['s']):
        V, F, emit, _ = geometri(B, st)
        V = V.copy(); V[:, 1] -= B['yp']
        cam = fe.Cam(S=3072, el=17, az=240, fov=19, D=4.4, target=(0, 0, 0.34))
        im, _ = fe.render(V, F, cam, emit=emit)
        ims.append(im)
    out = Image.new('RGB', (ims[0].width * 2, ims[0].height), 'black')
    for j, im in enumerate(ims):
        out.paste(im, (j * im.width, 0))
    out.save(path)
    return S


def final_tal():
    B = dict(FINAL)
    t, S = tal(B)
    V = geometri(B, S['work']['s'])[0]
    mx0, mx1, my0, my1 = MUS
    t['i_musesona'] = float(((V[:, 0] > mx0) & (V[:, 0] < mx1) & (V[:, 1] > my0) & (V[:, 1] < my1) & (V[:, 2] < 0.10)).mean())
    fl = [f for f in fe.standard_flagg(t) if f != 'gest veltar']       # gesten er eit kraftpar i endegrepet, ikkje eit dytt
    if t['grep_ratio'] < 5: fl.append('grep veltar')
    if t['i_musesona'] > 0.001: fl.append('i musesona')
    t['flagg'] = '; '.join(fl) or '-'
    return B, t, S
