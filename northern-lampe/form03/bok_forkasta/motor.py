"""form03 «Bok» — motor: fald. Ei plate, tre faldar (rygg + to lepper), står som ei open bok ved skjermen.

Grep: lyset er indirekte. LED-stripene ligg gøymde i leppene og lyser tvers over falden; dei to blada er den lysande flata.
Gest: snu boka om loddaksen (ψ). Open mot oppgåva = arbeid, mot brukaren = ansikt, mot veggen = stemning.
Rekna fridomsgrad: ψ. Søkt: bladbreidd w, faldvinkel θ, helling σ på ryggen (boka lener seg fram), plass (px, py), éi bok eller eit par.
Lover: lys (felles; synleg flate er lov når L_topp <= 3000 cd/m2), platetjukn frå svikt, grephøgd frå tipp, finne-verknadsgrad for kjøling.
v2 (etter grovt.py): v1 lyste eige blad i streif (toppfaktor 4,3) og stod loddrett (3,4 klm). No: visir mot eige blad, og helling.
"""
import os, sys, math, json
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
sys.path.insert(0, ROOT)
import felles as fe

E_ALU, RHO_ALU, K_ALU = 70e9, 2700, 200.0
MU = 0.20                      # filt mot bord
F_KANT = 2.0                   # N, fingertrykk på bladkanten (svikt)
PSIS = list(np.radians(np.arange(0, 360, 10)))
MUS = (0.30, 0.55, 0.0, 0.35)
BASE = dict(id=1, rad=1, kol=1, namn='bok', w=0.28, h=0.40, th=100.0, lean=0.0, px=-0.48, py=0.35, lip=0.020,
            rho=0.85, par=False, eige=False)


def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]])


def ramme(B, psi):
    """S3: ryggfot. e: botnkantretningar (3D, vassrette). r: ryggretning (lener seg σ mot opninga). n: innsidenormalar."""
    b = np.array([math.cos(psi), math.sin(psi)])
    th, sg = math.radians(B['th']) / 2, math.radians(B['lean'])
    es = [np.r_[rot(b, th), 0.0], np.r_[rot(b, -th), 0.0]]
    r = np.r_[math.sin(sg) * b, math.cos(sg)]
    c = (B['w'] / 2) * math.cos(th) + (B['h'] / 2) * math.sin(sg)        # tyngdepunkt langs b frå ryggfoten
    S3 = np.r_[np.array([B['px'], B['py']]) - c * b, 0.0]
    mid = [S3 + 0.5 * B['w'] * e + 0.5 * B['h'] * r for e in es]
    ns = []
    for i, e in enumerate(es):
        n = np.cross(e, r); n /= np.linalg.norm(n)
        if n @ (mid[1 - i] - mid[i]) < 0:
            n = -n
        ns.append(n)
    return b, S3, es, r, ns, mid


def blad(B, psi, ns_=8, nz=8):
    b, S3, es, r, ns, mid = ramme(B, psi)
    ss = (np.arange(ns_) + 0.5) / ns_ * B['w']
    us = (np.arange(nz) + 0.5) / nz * B['h']
    P, N, L = [], [], []
    for i, (e, n) in enumerate(zip(es, ns)):
        a = np.linalg.norm(np.cross(e, r)) * (B['w'] / ns_) * (B['h'] / nz)
        for s in ss:
            for u in us:
                P.append(S3 + s * e + u * r); N.append(n); L.append(i)
    return np.array(P), np.array(N), np.full(len(P), a), np.array(L)


_cache = {}


def fordeling(B, ns_=8, nz=8, nl=16):
    """Relativ luminans per flatebit, η, fanga del og toppfaktor frå to lambertske LED-liner i leppene (per LED-lumen)."""
    key = (B['w'], B['h'], B['th'], B['lean'], B['lip'], B['rho'], B['eige'], ns_, nz)
    if key in _cache:
        return _cache[key]
    b, S3, es, r, ns, mid = ramme(B, 0.0)
    P, N, dA, leaf = blad(B, 0.0, ns_, nz)
    E = np.zeros(len(P))
    ul = ((np.arange(nl) + 0.5) / nl * 0.9 + 0.05) * B['h']
    for i in (0, 1):
        m = mid[1 - i] - (S3 + B['w'] * es[i] + 0.5 * B['h'] * r)
        m /= np.linalg.norm(m)
        for u in ul:
            src = S3 + B['w'] * es[i] + u * r + 0.6 * B['lip'] * ns[i]
            d = P - src
            rr = np.linalg.norm(d, axis=1)
            cs = np.clip(d @ m / rr, 0, None)
            cp = np.clip(-(d * N).sum(1) / rr, 0, None)
            e_ = (0.5 / nl / math.pi) * cs * cp / rr ** 2
            if not B['eige']:
                e_[leaf == i] = 0.0                                      # visir: stripa ser ikkje eige blad
            E += e_
    fanga = float((E * dA).sum())
    eta = B['rho'] * fanga
    Lm = eta / (math.pi * dA.sum())
    rel = (B['rho'] * E / math.pi) / Lm
    _cache[key] = (rel, eta, fanga, float(rel.max()))
    return _cache[key]


def opning(B, psi, nt=None, n=None):
    k = 8 if n is None else 16
    rel = fordeling(B, k, k)[0]
    P, N, dA, _ = blad(B, psi, k, k)
    dA = dA * rel
    if B['par']:
        P2, N2 = P.copy(), N.copy()
        P2[:, 0] *= -1; N2[:, 0] *= -1
        P, N, dA = np.vstack([P, P2]), np.vstack([N, N2]), np.r_[dA, dA]
    return P, N, dA


def eta(B):
    return fordeling(B)[1]


def kollisjon(B, psi):
    b, S3, es, r, ns, mid = ramme(B, psi)
    pts = np.array([S3 + s * B['w'] * e + u * B['h'] * r for e in es for s in np.linspace(0, 1, 7) for u in (0.0, 0.5, 1.0)])
    if B['par']:
        q = pts.copy(); q[:, 0] *= -1
        pts = np.vstack([pts, q])
    x0, x1, y0, y1 = fe.DESK
    ute = (pts[:, 0] < x0) | (pts[:, 0] > x1) | (pts[:, 1] < y0) | (pts[:, 1] > y1 - 0.02)
    sikt = (np.abs(pts[:, 0]) < 0.30) & (pts[:, 1] < 0.50)
    low = pts[:, 2] < 0.10
    mus = low & (pts[:, 0] > MUS[0]) & (pts[:, 0] < MUS[1]) & (pts[:, 1] > MUS[2]) & (pts[:, 1] < MUS[3])
    return bool(ute.any() or sikt.any() or mus.any())


def sok(B):
    pk = fordeling(B)[3]
    S = fe.sok(B, PSIS, opning, eta(B))
    rows = S['rows']
    for r in rows:
        r['kolli'] = kollisjon(B, r['s'])
        r['Lap'] = r['k'] * r['Phi'] * pk                                   # toppluminans ved 500 lx
        r['glare_ok'] = (not r['vis'] or r['Lap'] <= fe.L_MAX) and (not r['refl'] or r['Lap'] <= fe.L_MAX)
    fri_r = [r for r in rows if not r['kolli']] or rows
    feas = [r for r in fri_r if r['glare_ok'] and r['U0'] >= fe.U0_MIN]
    W = min(feas or fri_r, key=lambda r: r['Phi'] * (1 if feas else 1 + (not r['glare_ok']) + (r['U0'] < fe.U0_MIN)))
    for r in rows:
        r['L_stem'] = r['k'] * W['Phi'] * fe.DIM_STEM * pk
        r['stem_ok'] = ((not r['vis'] and not r['refl']) or r['L_stem'] <= fe.L_STEM_MAX)
        r['Ev_stem'] = r['Ew'] * W['Phi'] * fe.DIM_STEM
    mf = [r for r in fri_r if r['stem_ok']]
    Mo = max(mf or fri_r, key=lambda r: (r['R_stem'] >= fe.R_STEM_MIN, r['Ev_stem']))
    Fa = max(fri_r, key=lambda r: r['face'])
    n = len(rows); i0, i1 = rows.index(W), rows.index(Mo)
    arcs = sorted([[(i0 + j) % n for j in range((i1 - i0) % n + 1)], [(i0 - j) % n for j in range((i0 - i1) % n + 1)]], key=len)
    # sveipet: fluksen fell lineært 100 % -> 25 % langs vegen; synleg topp skal halde seg under 3000
    def veg_ok(a):
        for j, i in enumerate(a):
            f = 1 - 0.75 * j / max(len(a) - 1, 1)
            if rows[i]['kolli'] or ((rows[i]['vis'] or rows[i]['refl']) and rows[i]['Lap'] * f > fe.L_MAX):
                return False
        return True
    fri = [a for a in arcs if veg_ok(a)]
    S.update(work=W, mood=Mo, face=Fa, veg=fri[0] if fri else None, sveip='fri' if fri else 'stengd',
             steg=(len(fri[0]) - 1) if fri else -1, L150=fe.E_FACE / max(Fa['face'], 1e-12) * pk, pk=pk,
             ok=bool(feas) and bool(fri) and Mo['R_stem'] >= fe.R_STEM_MIN and bool(Mo['stem_ok']))
    return S


def tjukn(B):
    """Platetjukn frå lova: bladkanten gjev etter <= DELTA_MAX under F_KANT (utkraga stripe om ryggen). Avrunda opp til 0,5 mm."""
    t = (4 * F_KANT * B['w'] ** 3 / (E_ALU * B['h'] * fe.DELTA_MAX / 1000)) ** (1 / 3)
    return t, math.ceil(t * 2000 - 1e-9) / 2000


def geometri(B, psi):
    t = tjukn(B)[1]
    meshes, emit = [], []
    def book(mirror):
        b, S3, es, r, ns, mid = ramme(B, psi)
        mx = np.array([-1.0, 1, 1]) if mirror else np.ones(3)
        for e, n in zip(es, ns):
            nu = nv = 14
            for off, em in ((0.0, True), (-t, False)):
                V = [(S3 + (B['w'] * i / nu) * e + (B['h'] * j / nv) * r + off * n) * mx for i in range(nu + 1) for j in range(nv + 1)]
                F = []
                for i in range(nu):
                    for j in range(nv):
                        a = i * (nv + 1) + j
                        F += [(a, a + nv + 1, a + nv + 2), (a, a + nv + 2, a + 1)]
                meshes.append((np.array(V), F)); emit.append(np.full(len(F), em))
            o = S3 + B['w'] * e
            V = [o * mx, (o + B['lip'] * n) * mx, (o + B['lip'] * n + B['h'] * r) * mx, (o + B['h'] * r) * mx]
            meshes.append((np.array(V), [(0, 1, 2), (0, 2, 3)])); emit.append(np.zeros(2, bool))
        c = S3[:2] + 0.035 * b
        poly = np.array([(c + 0.02 * rot(b, a)) * mx[:2] for a in np.linspace(0, 2 * math.pi, 13)[:-1]])
        meshes.append(fe.prism(poly, 0.0, 0.07)); emit.append(np.zeros(len(meshes[-1][1]), bool))
    book(False)
    if B['par']:
        book(True)
    V, F = fe.merge(meshes)
    return V, F, np.concatenate(emit)


def stab(B, psi):
    t = tjukn(B)[1]
    b, S3, es, r, ns, mid = ramme(B, psi)
    a = np.linalg.norm(np.cross(es[0], r))
    parts = []
    for i, e in enumerate(es):
        parts.append((RHO_ALU * B['w'] * B['h'] * a * t, mid[i]))
        parts.append((RHO_ALU * B['lip'] * B['h'] * t + 0.03, S3 + B['w'] * e + 0.5 * B['h'] * r))
    parts.append((0.12, S3 + np.r_[0.035 * b, 0.035]))
    kont = np.array([S3[:2], (S3 + B['w'] * es[0])[:2], (S3 + B['w'] * es[1])[:2]])
    m1 = sum(x for x, _ in parts)
    st0 = fe.stabilitet(parts, [kont], 1.0, 0.0)
    d_min = math.tan(math.radians(st0['tipp_deg'])) * st0['com'][2]
    z_maks = max(d_min, 0.0) / (2 * MU)
    z_grep = max(min(B['h'] / 2, z_maks), 0.02)
    st = fe.stabilitet(parts, [kont], z_grep, MU * m1 * fe.G)
    return st, m1, z_maks, z_grep


def tal(B, S=None):
    S = S or sok(B)
    W, Mo = S['work'], S['mood']
    t_lov, t = tjukn(B)
    nbok = 2 if B['par'] else 1
    st, m1, z_maks, z_grep = stab(B, W['s'])
    V = geometri(B, W['s'])[0]
    mL = math.sqrt(2 * fe.H_CONV / (K_ALU * t)) * B['w']
    eta_f = math.tanh(mL) / mL
    A_kj = nbok * (2 * 2 * B['w'] * B['h'] * eta_f + 2 * 2 * B['lip'] * B['h'])
    svikt = 4 * F_KANT * B['w'] ** 3 / (E_ALU * B['h'] * t ** 3) * 1000
    tt = fe.tal_felles(B, S, st, V, svikt, A_kj)
    tt.update(masse_kg=m1 * nbok, fot_cm2=st['fot_cm2'] * nbok, toppfaktor=S['pk'], eta=eta(B), fanga=fordeling(B)[2],
              t_lov_mm=t_lov * 1000, t_mm=t * 1000, z_grep_maks_cm=z_maks * 100, z_grep_cm=z_grep * 100, eta_finne=eta_f,
              psi_arb=math.degrees(W['s']), psi_stem=math.degrees(Mo['s']), sving=S['steg'] * 10, n_bok=nbok,
              synleg_arb=bool(W['vis']), spegla_arb=bool(W['refl']), w=B['w'], h=B['h'], th=B['th'], lean=B['lean'], px=B['px'], py=B['py'])
    tt['flagg'] = '; '.join(fe.standard_flagg(tt)) or '-'
    return tt, S
