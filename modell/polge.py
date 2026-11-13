# -*- coding: utf-8 -*-
"""Pølge-mannekengen som ryggfigur i lysmotoren.

Byter ut figuren av kuler og sylindrar i konsept/lysskisse/lysskisse.py med eit trekantnett,
utan å endre motoren. Bruk, før første kall på rom():

    import lysskisse as L
    import polge
    polge.byt(L)

Modellen er glTF med Y opp. Han blir forenkla til nokre tusen trekantar, snudd til Z opp,
vend mot skjermen (+y) og skalert så hovudet får same høgd og plass som den gamle figuren.
Kamera, lys og målingar er urørte. Tala i tal() som gjeld lampa åleine, hoppar framleis over figuren.

  python polge.py            skriv ut mål på modellen og plasseringa
  python polge.py --prov     lite prøvebilete (bakfrå og framanfrå) i modell/prov-*.png
"""
import os, sys, json, struct
import numpy as np
from scipy.spatial import cKDTree

try:
    import numba
    _NUMBA = True
except Exception:                      # utan numba verkar alt, berre seinare
    _NUMBA = False

HER = os.path.dirname(os.path.abspath(__file__))
MODELL = os.path.join(HER, 'polge_1.glb')

# Plassen til den gamle figuren (meter, bordkoordinatar): hovudtopp 59,5 cm over bordet,
# hovudet midt framfor skjermen og 25 cm framfor bordkanten.
HOVUDTOPP = 0.595
HOVUD_Y = -0.25
HOVUDHOGD = 0.23          # frå isse til smalaste punkt på halsen


# ------------------------------------------------------------------ glTF
def les_glb(fil):
    """Les posisjonar og trekantar frå ei glb-fil, med nodetransformasjonane lagde på."""
    d = open(fil, 'rb').read()
    magic, ver, lengd = struct.unpack_from('<4sII', d, 0)
    if magic != b'glTF':
        raise ValueError('ikkje ei glb-fil')
    p = 12; js = None; bin_ = None
    while p < lengd:
        n, typ = struct.unpack_from('<I4s', d, p); p += 8
        if typ == b'JSON': js = json.loads(d[p:p + n].decode('utf-8'))
        elif typ == b'BIN\x00' and bin_ is None: bin_ = d[p:p + n]
        p += n
    krev = js.get('extensionsRequired', [])
    if any(k in krev for k in ('KHR_draco_mesh_compression', 'EXT_meshopt_compression')):
        raise ValueError('modellen er komprimert (' + ', '.join(krev) + '); eksporter utan komprimering')
    TYP = {5120: 'i1', 5121: 'u1', 5122: '<i2', 5123: '<u2', 5125: '<u4', 5126: '<f4'}
    ANT = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}

    def acc(i):
        a = js['accessors'][i]; bv = js['bufferViews'][a['bufferView']]
        off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
        dt = np.dtype(TYP[a['componentType']]); nk = ANT[a['type']]; steg = bv.get('byteStride') or dt.itemsize * nk
        if steg == dt.itemsize * nk:
            arr = np.frombuffer(bin_, dtype=dt, count=a['count'] * nk, offset=off).reshape(a['count'], nk)
        else:
            arr = np.ndarray((a['count'], nk), dtype=dt, buffer=bin_, offset=off, strides=(steg, dt.itemsize))
        return np.array(arr, dtype=np.float64 if dt.kind == 'f' else np.int64)

    def mat(node):
        if 'matrix' in node:
            return np.array(node['matrix'], float).reshape(4, 4).T
        T = np.eye(4)
        x, y, z, w = node.get('rotation', [0, 0, 0, 1]); s = np.array(node.get('scale', [1, 1, 1]), float)
        R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                      [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                      [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        T[:3, :3] = R * s[None, :]; T[:3, 3] = node.get('translation', [0, 0, 0])
        return T

    V = []; F = []; n0 = [0]

    def gaa(i, M):
        node = js['nodes'][i]; M2 = M @ mat(node)
        if 'mesh' in node:
            for pr in js['meshes'][node['mesh']]['primitives']:
                if pr.get('mode', 4) != 4: continue
                pos = acc(pr['attributes']['POSITION'])
                pos = pos @ M2[:3, :3].T + M2[:3, 3]
                idx = acc(pr['indices']).reshape(-1, 3) if 'indices' in pr else np.arange(len(pos)).reshape(-1, 3)
                V.append(pos); F.append(idx + n0[0]); n0[0] += len(pos)
        for c in node.get('children', []):
            gaa(c, M2)

    for i in js['scenes'][js.get('scene', 0)]['nodes']:
        gaa(i, np.eye(4))
    return np.concatenate(V), np.concatenate(F)


# ------------------------------------------------------------------ nett
def forenkle(V, F, celle):
    """Slå saman hjørne i ruter på `celle` meter. Gjev hjørne, trekantar og glatte hjørnenormalar."""
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])          # flatevekta normalar
    q = np.floor((V - V.min(0)) / celle).astype(np.int64)
    _, inv = np.unique(q, axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    n = int(inv.max()) + 1
    Vn = np.zeros((n, 3)); np.add.at(Vn, inv, V); Vn /= np.bincount(inv, minlength=n)[:, None]
    Nn = np.zeros((n, 3))
    for k in range(3):
        np.add.at(Nn, inv[F[:, k]], fn)
    Nn /= np.maximum(np.linalg.norm(Nn, axis=1), 1e-12)[:, None]
    Fn = inv[F]
    Fn = Fn[(Fn[:, 0] != Fn[:, 1]) & (Fn[:, 1] != Fn[:, 2]) & (Fn[:, 0] != Fn[:, 2])]
    Fn = np.unique(np.sort(Fn, axis=1), axis=0)
    return Vn, Fn, Nn


def hals(V):
    """Høgda (z) der figuren er smalast i øvre halvdel: skiljet mellom hovud og kropp."""
    z0, z1 = V[:, 2].min(), V[:, 2].max()
    kantar = np.linspace(z0 + 0.5 * (z1 - z0), z1 - 0.03 * (z1 - z0), 60)
    breidd = []
    for a, c in zip(kantar[:-1], kantar[1:]):
        m = (V[:, 2] >= a) & (V[:, 2] < c)
        breidd.append(np.ptp(V[m, 0]) if m.sum() > 3 else np.inf)
    i = int(np.argmin(breidd))
    return 0.5 * (kantar[i] + kantar[i + 1])


def plasser(V, zb, snu=False, hovudhogd=HOVUDHOGD):
    """glTF (x høgre, y opp, z fram) -> motoren (x høgre, y mot skjermen, z opp), skalert og sett på plass."""
    P = np.stack([-V[:, 0], V[:, 2], V[:, 1]], 1)
    if snu:
        P[:, 0] *= -1; P[:, 1] *= -1
    zh = hals(P)
    s = hovudhogd / (P[:, 2].max() - zh)
    P = P * s
    zh = zh * s
    hovud = P[P[:, 2] > zh]
    P[:, 0] -= 0.5 * (hovud[:, 0].min() + hovud[:, 0].max())
    P[:, 1] += HOVUD_Y - 0.5 * (hovud[:, 1].min() + hovud[:, 1].max())
    dz = zb + HOVUDTOPP - P[:, 2].max()
    P[:, 2] += dz
    return P, s, zh + dz


def klynger(Vn, Fn, skive=0.05):
    """Del trekantane i små klynger (vassrette skiver gonger fire sektorar), kvar med si eiga kule.
    Gjev sorterte trekantar, startindeksar, klyngesenter og klyngeradiar."""
    c = Vn[Fn].mean(1)
    iz = np.floor((c[:, 2] - c[:, 2].min()) / skive).astype(np.int64)
    midt = np.array([c[:, 0].mean(), c[:, 1].mean()])
    ia = (np.floor((np.arctan2(c[:, 1] - midt[1], c[:, 0] - midt[0]) + np.pi) / (np.pi / 2)).astype(np.int64)) % 4
    kid = iz * 4 + ia
    orden = np.argsort(kid, kind='stable')
    Fs = Fn[orden]; kid = kid[orden]
    _, start = np.unique(kid, return_index=True)
    start = np.append(start, len(Fs)).astype(np.int64)
    cc = np.zeros((len(start) - 1, 3)); cr = np.zeros(len(start) - 1)
    for k in range(len(start) - 1):
        pk = Vn[Fs[start[k]:start[k + 1]]].reshape(-1, 3)
        cc[k] = 0.5 * (pk.min(0) + pk.max(0)); cr[k] = np.linalg.norm(pk - cc[k], axis=1).max() + 1e-5
    return Fs, start, cc, cr


if _NUMBA:
    @numba.njit(parallel=True, fastmath=True, cache=True)
    def _treff(O, D, c0, r0, cc, cr, start, V0, E1, E2, eps):
        n = O.shape[0]
        t = np.full(n, np.inf)
        for i in numba.prange(n):
            ox = O[i, 0]; oy = O[i, 1]; oz = O[i, 2]; dx = D[i, 0]; dy = D[i, 1]; dz = D[i, 2]
            a = dx * dx + dy * dy + dz * dz
            qx = ox - c0[0]; qy = oy - c0[1]; qz = oz - c0[2]
            b = qx * dx + qy * dy + qz * dz
            if b * b - a * (qx * qx + qy * qy + qz * qz - r0 * r0) < 0.0:
                continue
            best = np.inf
            for k in range(cr.shape[0]):
                qx = ox - cc[k, 0]; qy = oy - cc[k, 1]; qz = oz - cc[k, 2]
                b = qx * dx + qy * dy + qz * dz
                if b * b - a * (qx * qx + qy * qy + qz * qz - cr[k] * cr[k]) < 0.0:
                    continue
                for j in range(start[k], start[k + 1]):
                    e1x = E1[j, 0]; e1y = E1[j, 1]; e1z = E1[j, 2]; e2x = E2[j, 0]; e2y = E2[j, 1]; e2z = E2[j, 2]
                    px = dy * e2z - dz * e2y; py = dz * e2x - dx * e2z; pz = dx * e2y - dy * e2x
                    det = e1x * px + e1y * py + e1z * pz
                    if det > -1e-14 and det < 1e-14:
                        continue
                    inv = 1.0 / det
                    tx = ox - V0[j, 0]; ty = oy - V0[j, 1]; tz = oz - V0[j, 2]
                    u = (tx * px + ty * py + tz * pz) * inv
                    if u < 0.0 or u > 1.0:
                        continue
                    wx = ty * e1z - tz * e1y; wy = tz * e1x - tx * e1z; wz = tx * e1y - ty * e1x
                    v = (dx * wx + dy * wy + dz * wz) * inv
                    if v < 0.0 or u + v > 1.0:
                        continue
                    tt = (e2x * wx + e2y * wy + e2z * wz) * inv
                    if tt > eps and tt < best:
                        best = tt
            t[i] = best
        return t


def lag_klasse(L):
    class Kropp(L.Prim):
        """Trekantnett som svart kropp. Klynger med omslutta kuler, glatte normalar frå næraste hjørne."""
        def __init__(s, Vn, Fs, start, cc, cr, rho, tre, Nv):
            s.V0 = np.ascontiguousarray(Vn[Fs[:, 0]]); s.E1 = np.ascontiguousarray(Vn[Fs[:, 1]] - s.V0)
            s.E2 = np.ascontiguousarray(Vn[Fs[:, 2]] - s.V0)
            s.start = start; s.cc = np.ascontiguousarray(cc); s.cr = np.ascontiguousarray(cr)
            alle = Vn[Fs].reshape(-1, 3)
            s.c = 0.5 * (alle.min(0) + alle.max(0)); s.r = float(np.linalg.norm(alle - s.c, axis=1).max()) + 1e-4
            s.senter = s.c; s.rho = np.asarray(rho, float); s.tre = tre; s.Nv = Nv

        def t(s, O, D):
            O = np.ascontiguousarray(O, dtype=np.float64); D = np.ascontiguousarray(D, dtype=np.float64)
            if _NUMBA:
                return _treff(O, D, s.c, s.r, s.cc, s.cr, s.start, s.V0, s.E1, s.E2, L.EPS)
            n = len(O); t = np.full(n, np.inf)                      # rein numpy, sein
            with np.errstate(all='ignore'):
                oc = O - s.c; a = (D * D).sum(1); bq = (oc * D).sum(1); c = (oc * oc).sum(1) - s.r ** 2
                m = np.flatnonzero(bq * bq - a * c >= 0)
                steg = max(1, 400000 // len(s.V0))
                for i0 in range(0, len(m), steg):
                    mm = m[i0:i0 + steg]
                    Dm = D[mm][:, None, :]
                    Pv = np.cross(Dm, s.E2[None])
                    det = (s.E1[None] * Pv).sum(2); inv = 1.0 / det
                    Tv = O[mm][:, None, :] - s.V0[None]
                    u = (Tv * Pv).sum(2) * inv
                    Q = np.cross(Tv, s.E1[None])
                    v = (Dm * Q).sum(2) * inv
                    tt = (s.E2[None] * Q).sum(2) * inv
                    ok = (np.abs(det) > 1e-14) & (u >= 0) & (v >= 0) & (u + v <= 1) & (tt > L.EPS)
                    t[mm] = np.where(ok, tt, np.inf).min(1)
            return t

        def normal(s, P):
            d, i = s.tre.query(P, k=3)
            w = 1.0 / (d + 1e-4)
            nn = (s.Nv[i] * w[..., None]).sum(1)
            return nn / np.maximum(np.linalg.norm(nn, axis=1), 1e-12)[:, None]
    return Kropp


def figur(L, fil=MODELL, celle=0.008, snu=False, hovudhogd=HOVUDHOGD):
    """Gjev (liste med to kroppar: hovud og torso, opplysningar)."""
    V, F = les_glb(fil)
    P, s, zh = plasser(V, L.ZB, snu, hovudhogd)
    Vn, Fn, Nn = forenkle(P, F, celle)
    tre = cKDTree(Vn)
    Kropp = lag_klasse(L)
    zc = Vn[Fn].mean(1)[:, 2]
    delar = []
    for m, rho in ((zc > zh, L._HUD), (zc <= zh, L._TOY)):
        if not m.any(): continue
        Fs, start, cc, cr = klynger(Vn, Fn[m])
        delar.append(Kropp(Vn, Fs, start, cc, cr, rho, tre, Nn))
    info = dict(trekantar_inn=len(F), trekantar=len(Fn), hjorne=len(Vn), skala=round(float(s), 4),
                hogd=round(float(np.ptp(P[:, 2])), 3), breidd=round(float(np.ptp(P[:, 0])), 3), djupn=round(float(np.ptp(P[:, 1])), 3),
                hals_over_bordet=round(float(zh - L.ZB), 3), botn_over_golvet=round(float(P[:, 2].min()), 3),
                klynger=sum(len(d.cr) for d in delar), numba=_NUMBA,
                modellmaal=[round(float(x), 3) for x in np.ptp(V, axis=0)])
    return delar, info


def byt(L, fil=MODELL, **kw):
    """Byt ut ryggfiguren i motoren L med mannekengen. Må køyrast før L.rom() blir bygd."""
    if getattr(L, '_ROM', None) is not None:
        raise RuntimeError('rommet er alt bygd; kall polge.byt() rett etter import')
    delar, info = figur(L, fil, **kw)
    gamle = list(L.PERSON)
    L.STATISK[:] = [p for p in L.STATISK if not any(p is g for g in gamle)] + delar
    L.PERSON[:] = delar
    return info


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    import time
    sys.path.insert(0, os.path.normpath(os.path.join(HER, '..', 'konsept', 'lysskisse')))
    import lysskisse as L
    kw = {}
    if '--snu' in sys.argv: kw['snu'] = True
    if '--hovud' in sys.argv: kw['hovudhogd'] = float(sys.argv[sys.argv.index('--hovud') + 1])
    info = byt(L, **kw)
    print(info)
    if '--prov' in sys.argv:
        from PIL import Image
        px = 300
        lys = [L.straale(L.b(0.0, 0.25, 1.5), L.FELT, 88.0, 3000, maske=L.maske_bord(-0.3, 0.3, 0.05, 0.45, k=0.02), opning=0.03, sprut=0.0),
               L.straale(L.b(0.0, -0.2, 1.3), L.b(0.0, L.YV, 0.45), 244.0, 3000, maske=L.maske_vegg(0.0, L.ZB + 0.45, 0.75, k=0.18), opning=0.03, sprut=0.0)]
        t0 = time.time(); L.rom(); print('rom', round(time.time() - t0, 1), 's')
        t0 = time.time()
        Image.fromarray(L.framkall(L.luminans(lys, [], px, 1), px)).save(os.path.join(HER, 'prov-bak.png'))
        print('bilete bakfrå', px, 'px', round(time.time() - t0, 1), 's')
        # same figur sett framanfrå frå sida, med lys på han, for å sjå kvar han vender
        gammal = L.KAM
        L.KAM = L.Kamera((1.0, 0.35, L.ZB + 0.45), (0.0, -0.25, L.ZB + 0.25), 55)
        fram = [L.glod(L.b(0.8, 0.5, 0.9), 0.02, 1500.0, 3000)]
        Image.fromarray(L.framkall(L.luminans(fram, [], px, 1), px)).save(os.path.join(HER, 'prov-framme.png'))
        L.KAM = gammal
        print('prøvebilete skrivne')
