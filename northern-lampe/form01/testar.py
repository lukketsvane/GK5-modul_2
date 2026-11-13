"""Prøvane av Levin-hypotesane i levin.md (festa 01:03). Køyr: python testar.py -> utfall.json + utskrift."""
import os, sys, math, json, copy
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
sys.path.insert(0, ROOT)
import felles as fe

E_ALU = 70e9
BASE = dict(id=1, rad=1, kol=1, namn='k01', L=0.62, h=0.60, y0=0.40, R=0.022, beta=25.0, k=0.90,
            g=0.0, phi2=0.0, n=33)
PHIS = list(np.radians(np.arange(-180, 180, 5)))


def spine(B):
    t = np.linspace(-1, 1, B['n'])
    C = np.c_[t * B['L'] / 2, B['y0'] - B['g'] * t ** 2, np.full_like(t, B['h'])]
    return t, C


def frames(C):
    U = np.gradient(C, axis=0); U /= np.linalg.norm(U, axis=1, keepdims=True)
    W = np.array([0, 0, -1.0]) + U[:, 2:3] * U
    W /= np.linalg.norm(W, axis=1, keepdims=True)
    return U, W, np.cross(U, W)


def opning(B, phi0, nt=3):
    t, C = spine(B)
    tm, Cm = (t[:-1] + t[1:]) / 2, (C[:-1] + C[1:]) / 2
    ds = np.linalg.norm(np.diff(C, axis=0), axis=1)
    U, W, V = frames(Cm)
    keep = np.abs(tm) <= B['k']
    phi = phi0 + math.radians(B['phi2']) * tm ** 2
    n = np.cos(phi)[:, None] * W + np.sin(phi)[:, None] * V
    td = np.cross(U, n)
    be = math.radians(B['beta'])
    half, off = B['R'] * math.sin(be), B['R'] * math.cos(be)
    P, N, dA = [], [], []
    for s in (np.arange(nt) + 0.5) / nt * 2 - 1:
        P.append((Cm + off * n + s * half * td)[keep]); N.append(n[keep]); dA.append((ds * 2 * half / nt)[keep])
    return np.vstack(P), np.vstack(N), np.concatenate(dA)


def eta(B):
    t, C = spine(B)
    Larc = np.linalg.norm(np.diff(C, axis=0), axis=1).sum()
    A_ap = opning(B, 0.0)[2].sum()
    f = A_ap / (2 * math.pi * B['R'] * Larc + 2 * math.pi * B['R'] ** 2)
    sb = math.sin(math.radians(B['beta']))
    return min(1.0, sb + (1 - sb) * fe.RHO * f / (1 - fe.RHO * (1 - f)))


def sok(B):
    return fe.sok(B, PHIS, opning, eta(B))


def best_ok(S):
    W = S['work']
    return W['glare_ok'] and W['U0'] >= fe.U0_MIN


def main():
    out = {}
    S0 = sok(BASE)
    W0 = S0['work']
    out['base'] = dict(Phi=W0['Phi'], U0=W0['U0'], phi=math.degrees(W0['s']))
    print(f"base Phi={W0['Phi']:.0f} U0={W0['U0']:.2f} (gen01: 1461 / 0.53)")

    # H1 settpunkt
    h1 = {}
    for key, dv in (('y0', -0.10), ('y0', 0.10), ('h', -0.10), ('h', 0.10)):
        B = dict(BASE); B[key] += dv
        W = sok(B)['work']
        h1[f'{key}{dv:+.2f}'] = dict(Phi=W['Phi'], dPhi=W['Phi'] / W0['Phi'] - 1, U0=W['U0'], ok=W['glare_ok'])
    out['H1'] = h1
    for k_, v in h1.items():
        print(f"H1 {k_}: Phi={v['Phi']:.0f} dPhi={v['dPhi']*100:+.1f}% U0={v['U0']:.2f} glare_ok={v['ok']}")

    # H5 lengd
    h5 = []
    for L in np.arange(0.30, 1.0001, 0.05):
        B = dict(BASE); B['L'] = float(L)
        W = sok(B)['work']
        h5.append(dict(L=float(L), Phi=W['Phi'], U0=W['U0'], ok=W['glare_ok']))
        print(f"H5 L={L:.2f} Phi={W['Phi']:.0f} U0={W['U0']:.2f} glare_ok={W['glare_ok']}")
    out['H5'] = h5

    # H8 + H2 bøyg i plan + vring
    h8 = []
    for g in np.arange(-0.10, 0.1501, 0.025):
        for p2 in range(-40, 41, 10):
            B = dict(BASE); B['g'] = float(g); B['phi2'] = float(p2)
            S = sok(B); W = S['work']
            h8.append(dict(g=float(g), phi2=p2, Phi=W['Phi'], U0=W['U0'], ok=bool(W['glare_ok'] and W['U0'] >= fe.U0_MIN),
                           phi0=math.degrees(W['s']), Rst=S['mood']['R_stem']))
    feas = [r for r in h8 if r['ok']]
    best = min(feas, key=lambda r: r['Phi'])
    straight = min([r for r in feas if abs(r['g']) < 1e-9 and r['phi2'] == 0], key=lambda r: r['Phi'])
    per_g = {}
    for r in feas:
        if r['g'] not in per_g or r['Phi'] < per_g[r['g']]['Phi']:
            per_g[round(r['g'], 3)] = r
    out['H8'] = dict(best=best, straight=straight, per_g=per_g, gain=1 - best['Phi'] / straight['Phi'])
    print(f"H8 best g={best['g']:.3f} phi2={best['phi2']} Phi={best['Phi']:.0f} U0={best['U0']:.2f} gain={out['H8']['gain']*100:.1f}%")
    for g, r in sorted(per_g.items()):
        print(f"   g={g:+.3f} best phi2={r['phi2']:+d} Phi={r['Phi']:.0f} U0={r['U0']:.2f}")

    # H7 kontinuum (base): sveip frå arbeid til stemning med lineær fluks 100 % -> 25 %
    rows = S0['rows']; n = len(rows)
    i0, i1 = rows.index(S0['work']), rows.index(S0['mood'])
    a = [(i0 + j) % n for j in range((i1 - i0) % n + 1)]
    b = [(i0 - j) % n for j in range((i0 - i1) % n + 1)]
    path = min(a, b, key=len)
    seq = []
    for j, i in enumerate(path):
        f = 1 - 0.75 * j / max(len(path) - 1, 1)
        r = rows[i]
        Lvis = r['k'] * W0['Phi'] * f if (r['vis'] or r['refl']) else 0.0
        seq.append(dict(phi=math.degrees(r['s']), f=f, E=r['Em'] * W0['Phi'] * f, Rst=r['R_stem'], Lvis=Lvis))
    monoE = all(seq[j + 1]['E'] <= seq[j]['E'] + 1e-9 for j in range(len(seq) - 1))
    monoR = all(seq[j + 1]['Rst'] >= seq[j]['Rst'] - 1e-9 for j in range(len(seq) - 1))
    out['H7'] = dict(seq=seq, monoE=monoE, monoR=monoR, Lmax=max(s['Lvis'] for s in seq))
    print(f"H7 steg={len(seq)-1} monoE={monoE} monoR={monoR} Lvis_maks={out['H7']['Lmax']:.0f}")
    for s in seq:
        print(f"   phi={s['phi']:+.0f} f={s['f']:.2f} E={s['E']:.0f} Rst={s['Rst']:.2f} Lvis={s['Lvis']:.0f}")

    # H3 endegrep (k01-geometri frå gen01)
    sys.path.insert(0, os.path.join(ROOT, 'gen01'))
    import motor as mo
    B1 = [b for b in mo.BODIES if b['id'] == 1][0]
    t1, geo = mo.tal(B1)
    zg = (B1['c0'] + B1['u'] * B1['L'] / 2)[2] + B1['R']
    M_res = t1['F_tipp_N'] * zg
    out['H3'] = dict(M_res=M_res, ratio_grep=M_res / fe_T_DET(), ratio_dytt=t1['F_tipp_N'] / t1['F_vrid_N'])
    print(f"H3 M_res={M_res:.2f} N·m  endegrep/T={out['H3']['ratio_grep']:.1f}  fingerdytt={out['H3']['ratio_dytt']:.2f}")

    # H4 stivleik-dimensjonert stong (portal: kvar stong F_gest/2)
    Fg = 0.08 / BASE['R']
    p0, p1 = np.array([0, 0, 0.006]), np.array([0, 0, 0.60])
    law = fe.stong(p0, p1, fe.F_PUSH / 2, 0.08, F_gest=Fg / 2)
    stiv = fe.stong(p0, p1, fe.F_PUSH / 2, 0.08, stiv=True, F_gest=Fg / 2)
    out['H4'] = dict(d_law=law[4], d_stiv=stiv[4], dm=2 * (stiv[2] - law[2]), svikt_law=law[6], svikt_stiv=stiv[6])
    print(f"H4 lov d={law[4]:.1f} mm svikt={law[6]:.1f} | stiv d={stiv[4]:.1f} mm svikt={stiv[6]:.2f} | masse +{out['H4']['dm']:.3f} kg")

    # H6 samanhengande alu-kjerne (bøyle): Ø25 x 1,5, legg 0,60 + topp 0,62
    D, tw = 0.025, 0.0015
    I = math.pi / 64 * (D ** 4 - (D - 2 * tw) ** 4)
    h = 0.60
    svikt = (Fg / 2) * h ** 3 / (3 * E_ALU * I) * 1000
    Ltot = BASE['L'] + 2 * h
    A_kj = math.pi * D * Ltot
    A_req = W0['Phi'] / fe.LM_W / (fe.H_CONV * fe.DT)
    m_tube = 2700 * math.pi / 4 * (D ** 2 - (D - 2 * tw) ** 2) * Ltot
    m_old = 2 * law[2] + fe_SPINE_mass(BASE['L'])
    out['H6'] = dict(svikt=svikt, A_kj=A_kj * 1e4, A_req=A_req * 1e4, ratio=A_kj / A_req, dm=m_tube - m_old)
    print(f"H6 svikt={svikt:.2f} mm A_kj={A_kj*1e4:.0f} cm2 krav={A_req*1e4:.0f} ({A_kj/A_req:.1f}x) masse +{m_tube - m_old:.3f} kg")

    json.dump(out, open(os.path.join(HER, 'utfall.json'), 'w'), indent=1, default=float)


def fe_T_DET():
    return 0.08


def fe_SPINE_mass(L):
    return 8.7e-5 * L * 2700


if __name__ == '__main__':
    main()
