# -*- coding: utf-8 -*-
"""bru.py  ·  frå lampa (mm) til rommet i lysmotoren (m)

Lampa er teikna i millimeter med Z opp: origo midt i foten på bordflata, x mot høgre, y bort frå brukaren.
Rommet til lysmotoren (konsept/lysskisse/lysskisse.py) er i meter: x mot høgre, y frå brukaren mot veggen, z opp,
og b(x, y, h) er eit punkt h meter over bordplata (bordet ligg i z = 0,72).

  pl = i_rommet(delar, fot=(0.42, 0.25), dreiing=0)   set origo i lampa i b(0.42, 0.25, 0), dreidd om loddlina
  pl.p(punkt_mm)        eit punkt i lampa -> punkt i rommet (m). Til lyskjeldene: flate(pl.p(...), pl.r(...), ...)
  pl.r(retning)         ei retning i lampa -> einingsvektor i rommet
  pl.kropp(delar)       samlinga som svarte kroppar i lysmotoren (trekantnett per materiale): skuggar og syner i biletet
  pl.nett(delar)        samlinga som trimesh i romkoordinatar (m)
  pl.sjekk(delar)       står foten på bordet, utanfor feltet, og går noko gjennom skjermen eller veggen

dreiing er i grader om loddlina, mot klokka sett ovanfrå. Med dreiing 0 peikar +y i lampa mot veggen.
"""
import os, sys, math
HER = os.path.dirname(os.path.abspath(__file__))
if HER not in sys.path: sys.path.insert(0, HER)
import miljo                                         # høgst fire trådar og låg prioritet, før numpy
import numpy as np
import trimesh
from scipy.spatial import cKDTree
import kit as K

LYSSKISSE = os.path.join(K.ROT, 'konsept', 'lysskisse')
_LS = None


def motor():
    """Lysmotoren, lasta éin gong (med mannekengen frå modell/polge.py, som er standard der)."""
    global _LS
    if _LS is None:
        if LYSSKISSE not in sys.path: sys.path.insert(0, LYSSKISSE)
        import lysskisse
        _LS = lysskisse
    return _LS


# Kor lys kvar overflate er i lysstudien (diffus refleksjon, rgb). Berre til biletet: tala bryr seg ikkje om fargen.
RHO = {'aluminium': (0.55, 0.55, 0.56), 'stål': (0.45, 0.45, 0.46), 'stål_svart': (0.035, 0.035, 0.04), 'plast_grå': (0.30, 0.31, 0.32),
       'plast_svart': (0.03, 0.03, 0.035), 'kopar': (0.60, 0.36, 0.26), 'gummi_svart': (0.03, 0.03, 0.03), 'keramikk': (0.70, 0.68, 0.64),
       'fresnel': (0.60, 0.60, 0.62), 'print': (0.30, 0.06, 0.055), 'opal': (0.70, 0.70, 0.68), 'led': (0.60, 0.55, 0.45),
       'glas': (0.10, 0.11, 0.11), 'film': (0.12, 0.12, 0.13)}
GJENNOMSIKTIG = ('glas', 'film')
_KLASSE = None


def _klasse():
    """Trekantnett som svart kropp i lysmotoren. Stråletreffet er det til mannekengen (modell/polge.py, importert);
    normalen er flatenormalen til næraste trekant, så skarpe kantar held seg skarpe."""
    global _KLASSE
    if _KLASSE is not None: return _KLASSE
    ls = motor()
    polge = sys.modules.get('polge') or K._last('polge', os.path.join(K.ROT, 'modell', 'polge.py'))
    Base = polge.lag_klasse(ls)

    class Lekam(Base):
        def __init__(s, V, F, rho):
            Fs, start, cc, cr, sstart, sc, sr = polge.klynger(V, F, skive=0.03, sektorar=6)
            Base.__init__(s, V, Fs, start, cc, cr, sstart, sc, sr, rho, None, None)
            tri = V[Fs]
            n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
            s.Nf = n / np.maximum(np.linalg.norm(n, axis=1), 1e-18)[:, None]
            s.P0 = tri[:, 0]; s.tre = cKDTree(tri.mean(1))

        def normal(s, P):
            k = min(12, len(s.P0))
            d, i = s.tre.query(P, k=k)
            d = d.reshape(len(P), -1); i = i.reshape(len(P), -1)
            plan = np.abs(((P[:, None, :] - s.P0[i]) * s.Nf[i]).sum(2)) + 1e-3 * d      # i planet til trekanten, nærast vinn
            return s.Nf[i[np.arange(len(P)), plan.argmin(1)]]
    _KLASSE = Lekam
    return Lekam


def lekam(mesh_m, rho=(0.045, 0.045, 0.045), maks_kant=0.02):
    """Ein trimesh i romkoordinatar (m) som kropp i lysmotoren."""
    v, f = trimesh.remesh.subdivide_to_size(np.asarray(mesh_m.vertices, float), np.asarray(mesh_m.faces), maks_kant)
    tri = v[f]
    areal = np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
    f = f[areal > 1e-12]
    return _klasse()(np.ascontiguousarray(v), np.ascontiguousarray(f), rho)


class Plass:
    """Lampa sett på bordet i rommet. M er 4x4 frå lampa (mm) til rommet (m)."""
    def __init__(s, fot=(0.42, 0.25), dreiing=0.0, h=0.0):
        ls = motor()
        c, si = math.cos(math.radians(dreiing)), math.sin(math.radians(dreiing))
        s.fot = (float(fot[0]), float(fot[1])); s.dreiing = float(dreiing); s.h = float(h)
        s.R = np.array([[c, -si, 0], [si, c, 0], [0, 0, 1.0]])
        s.o = np.array([fot[0], fot[1], ls.ZB + h])
        s.M = np.eye(4); s.M[:3, :3] = s.R * 0.001; s.M[:3, 3] = s.o

    def p(s, punkt_mm):
        """Punkt i lampa (mm) -> punkt i rommet (m)."""
        return s.R @ (np.asarray(punkt_mm, float) * 0.001) + s.o

    def r(s, retning):
        """Retning i lampa -> einingsvektor i rommet."""
        v = s.R @ np.asarray(retning, float)
        return v / np.linalg.norm(v)

    def nett(s, delar, utan=(), gjennomsiktig=False, lysande=False):
        """[(del, undernamn, trimesh i rommet (m), materiale)]. utan: namn på delar eller 'del/underdel' som skal ut."""
        ut = []
        for d, u, m, mat in K.alle_under(delar):
            if d.namn in utan or '%s/%s' % (d.namn, u) in utan: continue
            if mat in GJENNOMSIKTIG and not gjennomsiktig: continue
            if d.lyser and not lysande: continue
            m = m.copy(); m.apply_transform(s.M); ut.append((d, u, m, mat))
        return ut

    def kropp(s, delar, utan=(), rho=None, maks_kant=0.02):
        """Samlinga som kroppar i lysmotoren, éin per materiale. Dei skuggar og syner i biletet.
        Ute av kroppen som standard: glas og film (gjennomsiktige) og delar som lyser (lyskjelda står for dei).
        Ta òg ut det lysmotoren alt har som strøk, t.d. utan=('fresnelspegel/plate',) når fresnelspegel() står for plata.
        Lyskjelder må liggje minst 1 mm utanfor kroppen, elles skuggar kroppen dei."""
        per = {}
        for d, u, m, mat in s.nett(delar, utan):
            per.setdefault(mat, []).append(m)
        farge = dict(RHO); farge.update(rho or {})
        return [lekam(trimesh.util.concatenate(ms) if len(ms) > 1 else ms[0], farge.get(mat, (0.2, 0.2, 0.2)), maks_kant)
                for mat, ms in per.items()]

    def sjekk(s, delar):
        """Kvar lampa står i rommet: dict(fot_pa_felt, fot_utanfor_bordet, gjennom_skjerm, gjennom_vegg, under_bordet_mm,
        framfor_skjermplanet). Feltet er x -0,3 til 0,3 og y 0,05 til 0,45. Skjermen står i y = 0,45, 54 x 31 cm, 11 til 42 cm over bordet."""
        ls = motor()
        V = np.vstack([m.vertices for _, _, m, _ in s.nett(delar, gjennomsiktig=True, lysande=True)])
        hb = V[:, 2] - ls.ZB
        fot = V[hb < hb.min() + 0.0006][:, :2]
        inn_felt = (np.abs(fot[:, 0]) < 0.30) & (fot[:, 1] > 0.05) & (fot[:, 1] < 0.45)
        ute = (np.abs(fot[:, 0]) > 0.70) | (fot[:, 1] < 0.0) | (fot[:, 1] > ls.YV)
        skj = (np.abs(V[:, 0]) < 0.27) & (hb > 0.11) & (hb < 0.42) & (V[:, 1] > 0.45) & (V[:, 1] < 0.47)
        stativ = (np.hypot(V[:, 0], V[:, 1] - 0.47) < 0.018) & (hb < 0.20)
        return dict(fot_pa_felt=bool(inn_felt.any()), fot_utanfor_bordet=bool(ute.any()), gjennom_skjerm=bool(skj.any() or stativ.any()),
                    gjennom_vegg=bool((V[:, 1] > ls.YV).any()), under_bordet_mm=round(float(max(-hb.min(), 0.0)) * 1000, 2),
                    hogste_punkt_cm=round(float(hb.max()) * 100, 1),
                    framfor_skjermplanet=bool((V[:, 1] < 0.45).all()), over_skjermkanten=bool((hb > 0.42).any()))


def i_rommet(delar=None, fot=(0.42, 0.25), dreiing=0.0, h=0.0):
    """Set lampa i rommet: origo i lampa (midt i foten, på bordflata) hamnar i b(fot[0], fot[1], h), dreidd `dreiing`
    grader om loddlina. Gjev ein Plass. Med delar seier funksjonen frå om lampa ikkje står med z = 0 på bordet."""
    pl = Plass(fot, dreiing, h)
    if delar is not None:
        lo, hi = K.grenser(delar)
        if abs(lo[2]) > 0.5:
            print('  merk bru: lågaste punkt i lampa er z = %.1f mm, ikkje 0. Bordflata skal vere z = 0.' % lo[2])
    return pl
