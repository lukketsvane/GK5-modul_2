"""form02 · val (a)/(b)/(c) med tal. Same lysrøyr og same felles tal(); ulik bering.
(a) Bru: røyr 1,12 m på A-bukkar (form01).
(b) Krok: røyr 0,64 m i eit nav, hengt frå éin flat alu-profil (6 mm, laserskoren) klemt på bakkanten.
    Breidda på profilen kjem frå momentlova w = √(6M/(tσ)) og vert skalert (ikkje klipt) til svikt ≤ 2 mm.
(c) Bru med synsfeltpremissen senka frå 15° til 10°.
"""
import os, sys, math, csv, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form01'))
import felles as fe
import motor as M1

E_ALU, RHO_ALU, SIG_ALU = 70e9, 2700, 250e6 / 2          # 6082-T6, SF 2
T_PL = 0.006
F_GEST = 3.0                                              # N, sidekraft ved grep (vurdering)
HUB = 0.015                                               # halv navbreidd


# ---------- (b) krok ----------
B_KROK = dict(M1.BASE, namn='krok', g=0.0, phir=0.0, yp=0.25, hp=0.62, L=0.64, k=0.94)


def opning_krok(B, psi, nt=3, n=None):
    P, N, dA = M1.opning(B, psi, nt, n)
    m = np.abs(P[:, 0]) > HUB
    return P[m], N[m], dA[m]


def eta_krok(B):
    return M1.eta(B)


def sok_krok(B):
    S = fe.sok(B, M1.PSIS, opning_krok, eta_krok(B))
    rows = S['rows']; n = len(rows)
    i0, i1 = rows.index(S['work']), rows.index(S['mood'])
    a = [(i0 + j) % n for j in range((i1 - i0) % n + 1)]
    b = [(i0 - j) % n for j in range((i0 - i1) % n + 1)]
    ok = [p for p in (a, b) if not any(rows[j]['vis'] and rows[j]['Lap'] > fe.L_MAX for j in p)]
    S['veg'] = min(ok, key=len) if ok else None
    return S


def arm_path(B, n=160):
    """Polylinje i y–z-planet: klemme (y 0,74, z 0) -> opp -> fram til navet. Hjørne med radius 0,10."""
    H = B['hp'] + B['R'] + 0.015
    y0, y1, rf = 0.74, B['yp'], 0.10
    seg1 = [(y0, z) for z in np.linspace(0.012, H - rf, n // 3)]
    th = np.linspace(0, math.pi / 2, n // 6)
    arc = [(y0 - rf + rf * math.cos(t), H - rf + rf * math.sin(t)) for t in th]
    seg2 = [(y, H) for y in np.linspace(y0 - rf, y1, n // 2)]
    drop = [(y1, z) for z in np.linspace(H, B['hp'] + 1.12 * B['R'], 6)]      # ned til navet
    pts = np.array(seg1 + arc[1:] + seg2[1:] + drop[1:])
    return pts, H


def arm_moment(pts, tip, P_v, F_y, T):
    """|M_x| i kvart punkt frå last i spissen: vekt P_v (ned), dytt ±F_y, kraftpar T."""
    dy, dz = tip[0] - pts[:, 0], tip[1] - pts[:, 1]
    Ms = [np.abs(dy * (-P_v) - dz * s * F_y) + T for s in (1, -1)]
    return np.maximum(*Ms)


def arm_design(B, m_head):
    pts, H = arm_path(B)
    tip = np.array([B['yp'], H])
    P_v = m_head * fe.G
    M = arm_moment(pts, tip, P_v, fe.F_PUSH, M1.T_DET)
    w_law = np.sqrt(6 * M / (T_PL * SIG_ALU))                    # momentlova, ingen w_min
    ds = np.r_[0, np.linalg.norm(np.diff(pts, axis=0), axis=1)]
    # svikt i y ved spissen under F_GEST (einingslast-metoden, bøying i planet)
    dz = tip[1] - pts[:, 1]
    def svikt(c):
        I = T_PL * (c * w_law) ** 3 / 12
        return float(np.sum((F_GEST * dz) * dz / (E_ALU * I) * ds) * 1000)
    c = max(1.0, (svikt(1.0) / fe.DELTA_MAX) ** (1 / 3))
    w = c * w_law
    area = float(np.sum(w * ds))
    # sidestivleik (ut av planet): 1 N i x i spissen, bøying med I = w t³/12 (vridning ikkje med: underskot)
    dist = np.linalg.norm(tip[None] - pts, axis=1)
    svikt_x = float(np.sum(1.0 * dist ** 2 / (E_ALU * (c * w_law) * T_PL ** 3 / 12) * ds) * 1000)
    return dict(pts=pts, w=w, w_law=w_law, c=c, svikt=svikt(c), svikt_law=svikt(1.0), H=H, tip=tip, svikt_x_per_N=svikt_x,
                masse=RHO_ALU * area * T_PL, M_klemme=float(M[0]), area=area)


def tube_arm(B, m_head, tw=0.0015):
    pts, H = arm_path(B)
    tip = np.array([B['yp'], H])
    ds = np.r_[0, np.linalg.norm(np.diff(pts, axis=0), axis=1)]
    dz = tip[1] - pts[:, 1]
    dist = np.linalg.norm(tip[None] - pts, axis=1)
    def sv(D):
        I = math.pi / 64 * (D ** 4 - (D - 2 * tw) ** 4)
        d_in = np.sum(F_GEST * dz * dz / (E_ALU * I) * ds) * 1000
        d_out = np.sum(F_GEST * dist ** 2 / (E_ALU * I) * ds) * 1000
        return d_in, d_out
    D = 0.008
    while max(sv(D)) > fe.DELTA_MAX:
        D += 0.001
    A = math.pi / 4 * (D ** 2 - (D - 2 * tw) ** 2)
    L = float(ds.sum())
    M = arm_moment(pts, tip, m_head * fe.G, fe.F_PUSH, M1.T_DET)
    sig = float(M.max() / (math.pi / 32 * (D ** 4 - (D - 2 * tw) ** 4) / D))
    return dict(pts=pts, D=D, svikt=sv(D)[0], svikt_x=sv(D)[1], masse=RHO_ALU * A * L, L=L, sig_MPa=sig / 1e6,
                area=math.pi * D * L, H=H)


def plate_mesh(pts, w, t):
    """Flat profil i y–z-planet, tjukn t i x. pts (n,2) = (y,z)."""
    d = np.gradient(pts, axis=0); d /= np.linalg.norm(d, axis=1, keepdims=True)
    nrm = np.c_[-d[:, 1], d[:, 0]]
    L, R = pts + nrm * w[:, None] / 2, pts - nrm * w[:, None] / 2
    n = len(pts)
    V = []
    for x in (-t / 2, t / 2):
        V += [[x, y, z] for y, z in L] + [[x, y, z] for y, z in R]
    V = np.array(V)
    F = []
    for i in range(n - 1):
        for off in (0, 2 * n):                                   # to flater
            a, b, c_, d_ = off + i, off + i + 1, off + n + i + 1, off + n + i
            F += [(a, b, c_), (a, c_, d_)]
        for s0 in (0, n):                                         # kantar
            a, b = s0 + i, s0 + i + 1
            F += [(a, b, 2 * n + b), (a, 2 * n + b, 2 * n + a)]
    for i in (0, n - 1):                                          # endar
        F += [(i, n + i, 3 * n + i), (i, 3 * n + i, 2 * n + i)]
    return V, F


def geometri_krok(B, psi):
    pr, be = math.radians(B['phir']), math.radians(B['beta'])
    t, C, U, W, V = M1.bow(B, psi, 65)
    tm = (t[:-1] + t[1:]) / 2
    xm = tm * B['L'] / 2
    cut = lambda i, th: abs(tm[i]) <= B['k'] and abs(xm[i]) > HUB and abs((th - pr + np.pi) % (2 * np.pi) - np.pi) < be
    meshes = [M1.tube_along(C, U, W, V, B['R'], 48, cut)]
    nb = len(meshes[0][1])
    nn = math.cos(pr) * W + math.sin(pr) * V
    td = np.cross(U, nn)
    Va, Fa = [], []
    for i in range(len(C) - 1):
        if abs(tm[i]) > B['k'] or abs(xm[i]) <= HUB:
            continue
        q = [(C[j] + B['R'] * math.cos(be) * 0.97 * nn[j] - B['R'] * math.sin(be) * td[j],
              C[j] + B['R'] * math.cos(be) * 0.97 * nn[j] + B['R'] * math.sin(be) * td[j]) for j in (i, i + 1)]
        o = len(Va); Va += [q[0][0], q[1][0], q[1][1], q[0][1]]; Fa += [(o, o + 1, o + 2), (o, o + 2, o + 3)]
    meshes.append((np.array(Va), Fa)); ne = len(Fa)
    c0 = np.array([0, B['yp'], B['hp']])
    meshes.append(fe.frustum(c0 - [HUB, 0, 0], c0 + [HUB, 0, 0], B['R'] * 1.12, B['R'] * 1.12, 40))      # nav
    gp = np.array([B['L'] / 2, B['yp'], B['hp']])
    meshes.append(fe.frustum(gp, gp + [0.03, 0, 0], 0.026, 0.026, 32))                                     # grep til høgre
    A = tube_arm(B, 0.5)
    C3 = np.c_[np.zeros(len(A['pts'])), A['pts']]
    U3 = np.gradient(C3, axis=0); U3 /= np.linalg.norm(U3, axis=1, keepdims=True)
    W3 = np.cross(U3, [1.0, 0, 0]); W3 /= np.linalg.norm(W3, axis=1, keepdims=True)
    meshes.append(M1.tube_along(C3, U3, W3, np.cross(U3, W3), A['D'] / 2, 20))
    for (y0, y1, z0, z1) in ((0.67, 0.75, 0.0, 0.012), (0.75, 0.762, -0.045, 0.012), (0.69, 0.762, -0.045, -0.035)):
        poly = np.array([[-0.025, y0], [0.025, y0], [0.025, y1], [-0.025, y1]])
        meshes.append(fe.prism(poly, z0, z1))                                                          # klemme
    Vv, Ff = fe.merge(meshes)
    emit = np.zeros(len(Ff), bool); emit[nb:nb + ne] = True
    return Vv, Ff, emit, A


def tal_krok(B):
    S = sok_krok(B)
    W, Mo = S['work'], S['mood']
    m_tube = RHO_ALU * math.pi * 2 * B['R'] * B['t_bow'] * B['L'] * (1 - B['k'] * B['beta'] / 180)
    m_head = m_tube + 0.10 + 0.06 + 0.04
    P_ = arm_design(B, m_head)                             # flat plate: berre for loggen
    A = tube_arm(B, m_head)
    mass = m_head + A['masse'] + 0.25                      # + klemme
    V = geometri_krok(B, W['s'])[0]
    above = V[:, 2] > 0.013
    ub, ik = fe.grense(V[above])
    e0 = fe.EYES[0]
    pts3 = np.c_[np.zeros(len(A['pts'])), A['pts']]
    over = (pts3[:, 1] < 0.74)
    elev = np.degrees(np.arctan2(pts3[over, 2] - e0[2], pts3[over, 1] - e0[1]))
    A_kj = math.pi * 2 * B['R'] * B['L'] * (1 - B['k'] * B['beta'] / 180)
    th = fe.termisk(W['Phi'], A_kj)
    t = dict(namn='krok', Phi_lm=W['Phi'], P_W=th['P_W'], U0=W['U0'], glare_ok=W['glare_ok'], R_stem=Mo['R_stem'],
             Ev_stem=Mo['Ev_stem'], stem_ok=Mo['stem_ok'], sving=(len(S['veg']) - 1) * 5 if S['veg'] else -1,
             L_ansikt=S['L150'], masse_kg=mass, fot_cm2=0.05 * 0.08 * 1e4, tipp_deg=float('nan'), grep_ratio=float('inf'),
             svikt_mm=max(A['svikt'], A['svikt_x']), arm_D_mm=A['D'] * 1000, arm_sig_MPa=A['sig_MPa'],
             plate_svikt_x_ved_grep_mm=P_['svikt_x_per_N'] * F_GEST, plate_w_klemme_mm=P_['w'][0] * 1000, plate_w_spiss_mm=P_['w'][-1] * 1000,
             M_klemme=P_['M_klemme'], A_kjol_cm2=th['A_kjol_cm2'], A_krav_cm2=th['A_krav_cm2'],
             termisk_ok=th['termisk_ok'], i_sikt=ik, arm_elev_min=float(elev.min()), L_m=B['L'])
    return t, S


# ---------- (a) og (c) ----------
def tal_bru(syn):
    M1.SYN_MIN = syn
    best = None
    for a_ in (0.15, 0.20):
        for yp in (0.18, 0.22, 0.25, 0.30):
            if yp - a_ < M1.BASE['D_leg'] / 2:                   # framføtene skal stå på bordet
                continue
            for hp in (0.54, 0.56, 0.58, 0.60, 0.62, 0.64):
                B = dict(M1.FINAL, yp=yp, hp=hp, a=a_)
                S = M1.sok(B)
                ok, Phi = M1.score(S)
                if ok and (best is None or Phi < best[1]):
                    t_, _ = M1.tal(B, S)
                    if t_['tipp_deg'] >= fe.TIP_MIN and t_['ut_bord'] < 0.005:
                        best = (B, Phi)
    B = best[0]
    t, S = M1.tal(B)
    t['namn'] = f'bru {syn:.0f}°'
    t['grep_ratio'] = t['grep_ratio']
    return B, t, S


def main():
    rows = {}
    Ba, ta, Sa = tal_bru(15.0)
    rows['a'] = (Ba, ta, Sa, lambda s: M1.geometri(Ba, s))
    Bc, tc, Sc = tal_bru(10.0)
    rows['c'] = (Bc, tc, Sc, lambda s: M1.geometri(Bc, s))
    M1.SYN_MIN = 15.0
    Bb = dict(B_KROK)
    tb, Sb = tal_krok(Bb)
    rows['b'] = (Bb, tb, Sb, lambda s: geometri_krok(Bb, s))
    for k in 'abc':
        B, t, S, _ = rows[k]
        print(k, {q: (round(v, 3) if isinstance(v, float) else v) for q, v in t.items()
                  if q in ('namn', 'Phi_lm', 'P_W', 'U0', 'R_stem', 'Ev_stem', 'sving', 'L_ansikt', 'masse_kg', 'fot_cm2', 'tipp_deg',
                           'svikt_mm', 'A_kjol_cm2', 'A_krav_cm2', 'i_sikt',
                           'arm_elev_min', 'yp', 'hp', 'glare_ok', 'stem_ok', 'grep_ratio', 'ut_bord', 'a', 'arm_D_mm', 'arm_sig_MPa', 'plate_svikt_x_ved_grep_mm', 'plate_w_klemme_mm', 'plate_w_spiss_mm')}, f"yp={B['yp']} hp={B['hp']}")
    json.dump({k: {q: (float(v) if isinstance(v, (float, np.floating)) else v) for q, v in rows[k][1].items()
                   if isinstance(v, (int, float, str, bool, np.floating, np.bool_))} for k in 'abc'},
              open(os.path.join(HER, 'tal.json'), 'w'), indent=1, default=str)
    # val-ark: tre store rammer, same kamera og skala, svart
    ims = []
    for k in 'abc':
        B, t, S, geo = rows[k]
        V, F, emit = geo(S['work']['s'])[:3]
        V = V.copy(); V[:, 1] -= 0.45
        cam = fe.Cam(S=2048, el=17, az=240, fov=19, D=4.6, target=(0, 0, 0.30))
        im, _ = fe.render(V, F, cam, emit=emit)
        im.save(os.path.join(HER, f'kropp_{k}.png'))
        ims.append(im)
    W_, H_ = 3 * 1024 + 4 * 60, 1024 + 120 + 430
    sh = Image.new('RGB', (W_, H_), 'black')
    dr = ImageDraw.Draw(sh)
    FONT = r'C:\Windows\Fonts\georgiai.ttf'
    fh, fb = ImageFont.truetype(FONT, 44), ImageFont.truetype(FONT, 28)
    nn_ = lambda v, d=0: f'{v:,.{d}f}'.replace(',', ' ').replace('.', ',')
    heads = {'a': '(a) bru', 'b': '(b) krok', 'c': '(c) bru, 10°'}
    for j, k in enumerate('abc'):
        x = 60 + j * (1024 + 60)
        sh.paste(ims[j], (x, 60))
        B, t, S, _ = rows[k]
        dr.text((x, 60 + 1024 + 40), heads[k], font=fh, fill=(240, 236, 228))
        dr.line([x, 60 + 1024 + 102, x + 260, 60 + 1024 + 100], fill=(240, 236, 228), width=2)
        st = '—' if k == 'b' else f"tipp {nn_(t['tipp_deg'])}°"
        lines = [f"{nn_(t['Phi_lm'])} lm · {nn_(t['P_W'], 1)} W · U0 {nn_(t['U0'], 2)}",
                 f"stemning {nn_(t['Ev_stem'])} lx på veggen · {t['R_stem'] * 100:.0f} %",
                 f"{nn_(t['masse_kg'], 2)} kg · {nn_(t['fot_cm2'])} cm² på bordet · {st}",
                 f"svikt {nn_(t['svikt_mm'], 1)} mm · vri {t['sving']:.0f}° · ansikt {nn_(t['L_ansikt'] / 1000, 1)} kcd/m²"]
        for i, s in enumerate(lines):
            dr.text((x, 60 + 1024 + 140 + i * 44), s, font=fb, fill=(240, 236, 228) if i < 2 else (170, 163, 152))
    sh.save(os.path.join(HER, 'val.png'))


if __name__ == '__main__':
    main()
