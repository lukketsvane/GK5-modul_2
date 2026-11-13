# -*- coding: utf-8 -*-
"""sjekk.py  ·  kontroll av ei samling: kollisjon, masse, velt, varme, trykk, eksport

Alt er rekna, ikkje målt. Måla på delane frå settet er anslag frå foto, så massane er usikre til delane er vegne.

  kollisjonar(delar)            par av delar som overlappar, med volum (mm³)
  masse(delar)                  masse per del, total og tyngdepunkt
  kontakt(delar)                omrisset lampa står på (konveks hylster av det som rører bordet)
  velt(delar, punkt)            minste vassrette dytt i punktet som veltar lampa, og veltevinkelen
  tippkraft(delar, punkt, retning)   krafta i ei vald retning (til dømes rett ned på ein utkragar)
  varme(delar)                  kvar LED-en sit (metall eller print) og kor varm kjøleflata blir
  utskrift(delar)               trykte delar mot 256 x 256 x 256 mm, overheng og gram
  eksporter(delar, mappe, namn) STL per trykt del (mm, slik han ligg på plata) og heile samlinga som GLB
  rapport(byggjar, mappe, namn, stillingar, dytt)   alt over for fleire stillingar i gesten -> sjekk.json og sjekk.md

Tettleik (g/cm³): stål 7,85 · aluminium 2,70 · glas 2,5 · PMMA 1,19 · PET 1,38 · PLA 1,24 · PETG 1,27 (kjent frå kjelde).
ANTAKING: plasten i settet 1,05 (ABS), gummi 1,1, keramikk 2,4, «kopar» 8,96 (materialmerket er ein farge i delar.py).
"""
import os, sys, json, math
sys.dont_write_bytecode = True
HER = os.path.dirname(os.path.abspath(__file__))
if HER not in sys.path: sys.path.insert(0, HER)
import miljo                                         # høgst fire trådar og låg prioritet, før numpy
import numpy as np
import trimesh
from scipy.spatial import ConvexHull, cKDTree
import kit as K

G = 9.81
TETTLEIK = {'stål': 7.85, 'stål_svart': 7.85, 'aluminium': 2.70, 'glas': 2.5, 'fresnel': 1.19, 'opal': 1.19, 'film': 1.38,
            'PLA': 1.24, 'PETG': 1.27,
            'plast_grå': 1.05, 'plast_svart': 1.05, 'gummi_svart': 1.1, 'keramikk': 2.4, 'kopar': 8.96, 'kretskort': 1.85}
ANTEKEN = {'plast_grå', 'plast_svart', 'gummi_svart', 'keramikk', 'kopar', 'kretskort', 'fresnel'}      # tettleiken er ei antaking
# Underdelar som er teikna massive i delar.py, men er tynne skal i røynda. Massen blir flate x vegg x tettleik.
# Veggen i stål er godstjukna frå DIMS (P01 vegg). Plastveggen 2,5 mm er ANTAKING.
SKAL = {('P01', 'kappe'): 2.5, ('P07', 'fatning'): 2.5, ('P03', 'sokkel'): 'vegg'}
USIKKER = dict(sett=0.35, print=0.15, kjopt=0.10, vege=0.02)      # relativ usikkerheit i massen (ANTAKING)
PRINT_SKAL, PRINT_FYLL = 1.2, 0.15                                # trykk: tre vegger à 0,4 mm og 15 % fyll (ANTAKING)
METALL = {'aluminium', 'stål', 'stål_svart', 'kopar'}
H_KONV = 10.0                                                     # W/m²K, fri konveksjon og stråling (ANTAKING, som konsept/lysskisse/studie.py)
VARMEDEL = 0.70                                                   # delen av watten som blir varme i dioden (ANTAKING, same stad)
ROMTEMP = 25.0
MY = 0.4                                                          # friksjon fot mot bord (ANTAKING)

# ------------------------------------------------------------------ kollisjon

def _lekamar(mesh):
    """Tette lekamar i ein mesh (ein underdel kan vere fleire, t.d. vifteblad)."""
    if mesh.body_count <= 1:
        return [mesh]
    return [m for m in mesh.split(only_watertight=True)] or [mesh]


def _snittvolum(a, b):
    """Volumet der to tette lekamar overlappar (mm³). Manifold først, punktprøving som reserve."""
    try:
        import manifold3d as m3
        f = lambda m: m3.Manifold(m3.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32)))
        ma, mb = f(a), f(b)
        if ma.status() == m3.Error.NoError and mb.status() == m3.Error.NoError:
            return float((ma ^ mb).volume()), 'manifold'
    except Exception:
        pass
    lo = np.maximum(a.bounds[0], b.bounds[0]); hi = np.minimum(a.bounds[1], b.bounds[1])
    if np.any(hi <= lo): return 0.0, 'punkt'
    n = np.clip(np.ceil((hi - lo) / 1.5).astype(int), 2, 40)            # rutenett om lag 1,5 mm, høgst 40 per akse
    ax = [np.linspace(lo[i], hi[i], n[i] * 2 + 1)[1::2] for i in range(3)]
    P = np.stack(np.meshgrid(*ax, indexing='ij'), -1).reshape(-1, 3)
    try:
        inne = a.contains(P) & b.contains(P)
    except Exception:
        return float('nan'), 'ukjent'
    return float(inne.mean() * np.prod(hi - lo)), 'punkt'


def kollisjonar(delar, tillat=(), min_mm3=1.0):
    """Par av delar som overlappar. Underdelar i same del blir ikkje prøvde mot kvarandre.
    tillat: [('namn a', 'namn b'), ...] er par som skal overlappe (pressa tapp, film i spor) og berre blir noterte.
    min_mm3: mindre overlapp enn dette er berøring og blir ikkje meldt.
    Gjev [dict(a, b, volum_mm3, underdelar, tillate, metode)]."""
    lek = []
    for d in delar:
        L = []
        for u, m, mat in d.underdelar():
            for kropp in _lekamar(m):
                L.append((u, kropp))
        lek.append(L)
    tl = {frozenset(p) for p in tillat}
    ut = []
    for i in range(len(delar)):
        bi = delar[i].grenser()
        for j in range(i + 1, len(delar)):
            bj = delar[j].grenser()
            if np.any(np.minimum(bi[1], bj[1]) <= np.maximum(bi[0], bj[0])): continue
            vol = 0.0; kven = []; metode = set()
            for ua, a in lek[i]:
                for ub, b in lek[j]:
                    if np.any(np.minimum(a.bounds[1], b.bounds[1]) <= np.maximum(a.bounds[0], b.bounds[0])): continue
                    v, met = _snittvolum(a, b)
                    if v != v or v > 1e-6:
                        vol += 0.0 if v != v else v; kven.append('%s/%s' % (ua, ub)); metode.add(met)
            if vol >= min_mm3 or 'ukjent' in metode:
                ut.append(dict(a=delar[i].namn, b=delar[j].namn, volum_mm3=round(vol, 1), underdelar=sorted(set(kven)),
                               tillate=frozenset((delar[i].namn, delar[j].namn)) in tl, metode='+'.join(sorted(metode))))
    return ut


def avstand(a, b, n=4000):
    """Minste avstand (mm) mellom flatene til to delar, prøvd i punkt (hjørne og jamt spreidde flatepunkt).
    Til å sjå om ei klaring er slik du ville ha ho. 0 tyder at dei rører eller overlappar."""
    ma, mb = a.mesh(), b.mesh()
    pa = np.vstack([ma.vertices, ma.sample(n)]); pb = np.vstack([mb.vertices, mb.sample(n)])
    d1 = trimesh.proximity.closest_point(mb, pa)[1].min()
    d2 = trimesh.proximity.closest_point(ma, pb)[1].min()
    return float(min(d1, d2))

# ------------------------------------------------------------------ masse

def _underdelmasse(d, u, mesh_lokal, mat):
    """(gram, merknad) for éin underdel."""
    if d.slag == 'print':
        V, A = abs(float(mesh_lokal.volume)) / 1000, float(mesh_lokal.area) / 100            # cm³, cm²
        skal = min(V, A * PRINT_SKAL / 10)
        g = TETTLEIK[d.plast] * (skal + PRINT_FYLL * (V - skal))
        return g, 'rekna: %s, vegg %s mm og %.0f %% fyll (ANTAKING), massiv %.0f g' % (d.plast, _nn(PRINT_SKAL, 1), PRINT_FYLL * 100, TETTLEIK[d.plast] * V)
    rho = TETTLEIK.get(mat)
    if rho is None:
        return 0.0, 'ukjent materiale %s: 0 g' % mat
    ant = ', tettleik ANTAKING' if mat in ANTEKEN else ''
    vegg = SKAL.get((d.pid, u))
    if vegg is not None:
        t = K.D.v('P01', 'vegg') if vegg == 'vegg' else float(vegg)
        V = min(abs(float(mesh_lokal.volume)), float(mesh_lokal.area) * t) / 1000
        return rho * V, 'rekna som skal, vegg %s mm (%s)%s' % (_nn(t, 1), 'DIMS P01 vegg' if vegg == 'vegg' else 'ANTAKING', ant)
    return rho * abs(float(mesh_lokal.volume)) / 1000, 'rekna frå volum, mål anslått frå foto%s' % ant


def masse(delar):
    """Masse og tyngdepunkt. Gjev dict(total_g, pm_g, tp_mm, rader=[dict(namn, slag, g, tp_mm, kjelde)])."""
    rader = []; M = 0.0; mom = np.zeros(3); var = 0.0
    for d in delar:
        if d.vekt_g is not None:
            g = float(d.vekt_g); c = d.mesh().center_mass if d.mesh().is_volume else d.mesh().centroid
            kjelde = 'oppgjeven' if d.slag == 'kjopt' else 'vegen'
            rel = USIKKER['kjopt'] if d.slag == 'kjopt' else USIKKER['vege']
        else:
            g = 0.0; cm = np.zeros(3); merk = []
            for (u, ml, mat), (_, mv, _) in zip(d.under, d.underdelar()):
                gi, tekst = _underdelmasse(d, u, ml, mat)
                ci = mv.center_mass if mv.is_volume else mv.centroid
                g += gi; cm += gi * np.asarray(ci); merk.append(tekst)
            c = cm / max(g, 1e-12); kjelde = '; '.join(sorted(set(merk))); rel = USIKKER[d.slag]
        rader.append(dict(namn=d.namn, slag=d.slag, pid=d.pid, g=round(g, 1), tp_mm=[round(float(x), 1) for x in c], kjelde=kjelde, pm_g=round(rel * g, 1)))
        M += g; mom += g * np.asarray(c); var += (rel * g) ** 2
    return dict(total_g=round(M, 1), pm_g=round(math.sqrt(var), 1), tp_mm=[round(float(x), 1) for x in mom / max(M, 1e-12)], rader=rader)

# ------------------------------------------------------------------ velt

def kontakt(delar, eps=0.5):
    """Det lampa står på: konveks hylster (xy, mm) av alle punkt som ligg innanfor eps mm frå det lågaste punktet.
    Gjev dict(hylster (n x 2, mot klokka), z0, areal_cm2)."""
    V = np.vstack([m.vertices for _, _, m, _ in K.alle_under(delar)])
    z0 = float(V[:, 2].min())
    P = V[V[:, 2] <= z0 + eps][:, :2]
    P = np.unique(np.round(P, 3), axis=0)
    if len(P) < 3:
        return dict(hylster=P, z0=z0, areal_cm2=0.0)
    try:
        h = ConvexHull(P)
    except Exception:
        return dict(hylster=P, z0=z0, areal_cm2=0.0)
    return dict(hylster=P[h.vertices], z0=z0, areal_cm2=float(h.volume) / 100)


def _akser(hyl, n_kjegle=7):
    """Alle linjer lampa kan tippe om: gjennom kvart hjørne i hylsteret, med innovernormal mellom dei to nabokantane."""
    n = len(hyl); ut = []
    nrm_inn = []
    for i in range(n):
        a, b = hyl[i], hyl[(i + 1) % n]; e = b - a; L = np.linalg.norm(e)
        nrm_inn.append(np.array([-e[1], e[0]]) / max(L, 1e-12))            # mot klokka: innover er til venstre for kanten
    for i in range(n):
        n0, n1 = nrm_inn[i - 1], nrm_inn[i]
        a0, a1 = math.atan2(n0[1], n0[0]), math.atan2(n1[1], n1[0])
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        for k in range(n_kjegle):
            a = a0 + da * k / (n_kjegle - 1)
            ut.append((hyl[i], np.array([math.cos(a), math.sin(a)])))
    return ut


def _tipp(m_kg, tp, hyl, z0, punkt, retning):
    """Krafta (N) i retninga `retning` i `punkt` (mm) som akkurat tippar ein stiv kropp om kanten av hylsteret."""
    d = np.asarray(retning, float); d = d / np.linalg.norm(d)
    best = math.inf
    for v, ninn in _akser(hyl):
        v3 = np.array([v[0], v[1], z0]); n3 = np.array([ninn[0], ninn[1], 0.0])
        e = np.cross(n3, [0, 0, 1.0])                                      # tyngda gjev moment -m g a om denne aksen
        a = float((np.asarray(tp) - v3) @ n3)                              # arm for tyngda (mm), over 0 når tyngdepunktet er innanfor
        mf = float(np.cross(np.asarray(punkt, float) - v3, d) @ e)         # arm for krafta (mm)
        if a <= 0: return 0.0
        if mf > 1e-9: best = min(best, m_kg * G * a / mf)
    return best


def tippkraft(delar, punkt, retning, m=None, k=None):
    """Krafta (N) i ei vald retning (3 tal, t.d. (0, 0, -1) for trykk rett ned) i punktet (mm) som tippar lampa.
    inf tyder at krafta ikkje kan tippe henne."""
    m = m or masse(delar); k = k or kontakt(delar)
    if len(k['hylster']) < 3: return 0.0
    return _tipp(m['total_g'] / 1000, m['tp_mm'], k['hylster'], k['z0'], punkt, retning)


def velt(delar, punkt, krav_N=5.0, n_retn=72):
    """Minste vassrette dytt (N) i `punkt` (mm, lampa sitt system) som veltar lampa, over n_retn retningar,
    og veltevinkelen (kor mykje underlaget kan helle før tyngdepunktet går over kanten).
    Gjev dict(dytt_N, dytt_retning_grader (0 = +x, 90 = +y), krav_N, held, glid_N, veltevinkel, fot_cm2, masse_g, tp_mm ...)."""
    m = masse(delar); k = kontakt(delar)
    hyl = k['hylster']; tp = np.asarray(m['tp_mm']); mk = m['total_g'] / 1000
    if len(hyl) < 3:
        return dict(dytt_N=0.0, held=False, merknad='lampa står på færre enn tre punkt', masse_g=m['total_g'], tp_mm=m['tp_mm'], fot_cm2=0.0)
    F = []
    for i in range(n_retn):
        a = 2 * math.pi * i / n_retn
        F.append(_tipp(mk, tp, hyl, k['z0'], punkt, (math.cos(a), math.sin(a), 0.0)))
    i = int(np.argmin(F))
    inn = []                                                              # avstand frå tyngdepunktet inn til kvar kant
    for j in range(len(hyl)):
        a, b = hyl[j], hyl[(j + 1) % len(hyl)]; e = b - a
        inn.append(float(np.array([-e[1], e[0]]) @ (tp[:2] - a) / max(np.linalg.norm(e), 1e-12)))
    hmin = float(tp[2] - k['z0'])
    vinkel = math.degrees(math.atan2(min(inn), max(hmin, 1e-6)))
    pm = m['pm_g'] / max(m['total_g'], 1e-9)
    return dict(punkt_mm=[round(float(x), 1) for x in punkt], dytt_N=round(float(F[i]), 2), dytt_retning_grader=round(360.0 * i / n_retn, 1),
                dytt_N_lett=round(float(F[i]) * (1 - pm), 2), krav_N=krav_N, held=bool(F[i] >= krav_N),
                glid_N=round(MY * mk * G, 2), glir_forst=bool(MY * mk * G < F[i]), veltevinkel=round(vinkel, 1),
                tp_innanfor_mm=round(min(inn), 1), fot_cm2=round(k['areal_cm2'], 1), masse_g=m['total_g'], masse_pm_g=m['pm_g'],
                tp_mm=m['tp_mm'], z0_mm=round(k['z0'], 2),
                merknad='rekna: stiv kropp på stivt bord, friksjon %s (ANTAKING). dytt_N_lett er med massen i nedre kant av usikkerheita.' % _nn(MY, 1))

# ------------------------------------------------------------------ varme

def _naer(ma, mb, grense, n=1500):
    """Sant om flatene til to meshar ligg nærare kvarandre enn grense (mm)."""
    if np.any(np.minimum(ma.bounds[1], mb.bounds[1]) + grense <= np.maximum(ma.bounds[0], mb.bounds[0])): return False
    pa = np.vstack([ma.vertices, ma.sample(n)]); pb = np.vstack([mb.vertices, mb.sample(n)])
    return bool(min(trimesh.proximity.closest_point(mb, pa)[1].min(), trimesh.proximity.closest_point(ma, pb)[1].min()) <= grense)


def varme(delar, grense=0.5):
    """For kvar kjøpt del med watt: kva han ligg mot, og kor varm kjøleflata blir.
    Reknestykket: 70 % av watten blir varme, flata gjev frå seg 10 W/m²K (ANTAKING, same som konsept/lysskisse/studie.py).
    Kjøleflata er den ytre flata (konvekst hylster) til metallunderdelane LED-en ligg mot (nærare enn `grense` mm),
    pluss metall som ligg mot dei att. Plast og print mellom LED og metall bryt varmevegen.
    Gjev [dict(namn, watt, ligg_mot, metall, print, kjoleflate_cm2, temp_C, ok, raad)]."""
    alle = K.alle_under(delar)
    ut = []
    for d in delar:
        if not d.watt: continue
        md = d.mesh()
        nabo = [(o, u, m, mat) for o, u, m, mat in alle if o is not d and _naer(md, m, grense)]
        met = [x for x in nabo if x[3] in METALL]
        ko = list(met)
        while ko:                                                        # metall mot metall leier varmen vidare
            _, _, m0, _ = ko.pop()
            for x in alle:
                if x[0] is not d and x[3] in METALL and not any(x[2] is y[2] for y in met) and _naer(m0, x[2], grense):
                    met.append(x); ko.append(x)
        A = 0.0
        for _, _, mv, _ in met:
            try: A += float(mv.convex_hull.area) / 100
            except Exception: A += float(mv.area) / 200
        pr = sorted({o.namn for o, _, _, _ in nabo if o.slag == 'print'})
        dT = VARMEDEL * d.watt / (H_KONV * A / 1e4) if A > 0 else float('inf')
        temp = ROMTEMP + dT
        grenseC = min([K.MJUKNAR[o.plast] for o in delar if o.slag == 'print'] or [K.MJUKNAR['PLA']])
        ok = bool(A > 0 and temp < grenseC - 5)
        if not met:
            raad = 'LED-en ligg ikkje mot metall. Trykt PLA mjuknar ved 55 til 60 °C: legg han på aluminium eller stål, eller gje han ei kjøleplate.'
        elif not ok:
            raad = 'For lita kjøleflate: %.0f cm² gjev om lag %.0f °C ved %s W. Større metallflate eller lågare watt.' % (A, temp, _nn(d.watt, 1))
        else:
            raad = 'Held: om lag %.0f °C ved %s W på %.0f cm² metall (grense %.0f °C for %s).' % (
                temp, _nn(d.watt, 1), A, grenseC, '/'.join(sorted({o.plast for o in delar if o.slag == 'print'})) or 'PLA')
        ut.append(dict(namn=d.namn, watt=d.watt, ligg_mot=sorted({'%s/%s' % (o.namn, u) if u != o.namn else o.namn for o, u, _, _ in nabo}),
                       metall=sorted({'%s/%s' % (o.namn, u) if u != o.namn else o.namn for o, u, _, _ in met}), print=pr,
                       kjoleflate_cm2=round(A, 1), temp_C=(round(temp, 1) if A > 0 else None), grense_C=grenseC, ok=ok, raad=raad,
                       merknad='rekna, ikkje målt. ANTAKING: %.0f %% varme, %.0f W/m²K, rom %.0f °C' % (VARMEDEL * 100, H_KONV, ROMTEMP)))
    return ut

# ------------------------------------------------------------------ trykk

def _paa_plata(d):
    m = d.mesh(lokal=True); m.apply_transform(d.print_R)
    m.apply_translation((-(m.bounds[0][0] + m.bounds[1][0]) / 2, -(m.bounds[0][1] + m.bounds[1][1]) / 2, -m.bounds[0][2]))
    return m


def utskrift(delar, vinkel=45.0):
    """Trykte delar slik dei ligg på plata (print_R): mål mot 256 x 256 x 256 mm, overheng og gram.
    Overheng: flater som vender nedover brattare enn `vinkel` frå loddrett og ikkje ligg på plata (cm²): dei treng støtte.
    Gjev [dict(namn, plast, maal_mm, passar, overheng_cm2, overheng_del, g, g_massiv, tett, merknad)]."""
    ut = []
    for d in delar:
        if d.slag != 'print': continue
        m = _paa_plata(d)
        ext = m.extents
        nz = m.face_normals[:, 2]; cz = m.triangles_center[:, 2]
        ned = (nz < -math.cos(math.radians(vinkel))) & (cz > 0.3)
        A_ned = float(m.area_faces[ned].sum()) / 100
        V, A = abs(float(m.volume)) / 1000, float(m.area) / 100
        skal = min(V, A * PRINT_SKAL / 10)
        g = TETTLEIK[d.plast] * (skal + PRINT_FYLL * (V - skal))
        passar = bool(np.all(ext <= np.array(K.PRINTER) + 1e-6))
        merk = []
        if not passar: merk.append('for stor for plata: del han eller snu han')
        if A_ned > 1.0: merk.append('overheng %.0f cm²: støtte, eller snu delen' % A_ned)
        if not m.is_watertight: merk.append('meshen er ikkje tett')
        ut.append(dict(namn=d.namn, plast=d.plast, maal_mm=[round(float(x), 1) for x in ext], passar=passar,
                       overheng_cm2=round(A_ned, 1), overheng_del=round(A_ned / max(A, 1e-9), 3), g=round(g, 1),
                       g_massiv=round(TETTLEIK[d.plast] * V, 1), tett=bool(m.is_watertight), merknad='; '.join(merk) or 'ok'))
    return ut

# ------------------------------------------------------------------ eksport

FARGAR = dict(K.D.FARGAR)
FARGAR.update({'print': (124, 46, 48), 'led': (255, 214, 150), 'opal': (240, 238, 230)})


def eksporter(delar, mappe, namn='lampe'):
    """Skriv <mappe>/stl/<del>.stl for kvar trykt del (mm, slik han ligg på plata) og <mappe>/<namn>.glb for heile samlinga
    (meter, Y opp som glTF krev, farge per materiale). Gjev dict(stl=[...], glb=fil)."""
    os.makedirs(os.path.join(mappe, 'stl'), exist_ok=True)
    stl = []
    for d in delar:
        if d.slag != 'print': continue
        fil = os.path.join(mappe, 'stl', 'print_%s.stl' % d.namn)
        _paa_plata(d).export(fil); stl.append(fil)
    sc = trimesh.Scene()
    til_gltf = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1.0]]) @ np.diag([0.001, 0.001, 0.001, 1.0])
    for d, u, m, mat in K.alle_under(delar):
        m = m.copy(); m.apply_transform(til_gltf)
        m.visual.face_colors = (*FARGAR.get(mat, (180, 180, 180)), 255)
        sc.add_geometry(m, node_name='%s_%s_%s' % (d.slag, d.namn, u))
    glb = os.path.join(mappe, namn + '.glb')
    sc.export(glb)
    return dict(stl=stl, glb=glb)

# ------------------------------------------------------------------ alt på éin gong

def _j(o):
    if isinstance(o, (np.floating, np.integer)): return float(o)
    if isinstance(o, np.ndarray): return o.tolist()
    if isinstance(o, (set, frozenset)): return sorted(o)
    return str(o)


def _nn(v, d=0):
    return ('%.*f' % (d, v)).replace('.', ',')


def rapport(byggjar, mappe, namn='lampe', stillingar=(0.0, 0.25, 0.5, 0.75, 1.0), dytt=None, tillat=(), krav_N=5.0, trykk=None):
    """Køyr alle kontrollane og skriv <mappe>/sjekk.json og <mappe>/sjekk.md.
    byggjar: funksjon t -> liste med delar (t = 0 stemning, t = 1 arbeid), eller ei ferdig liste.
    dytt: funksjon delar -> punkt (mm) der handa dyttar (standard: det høgste punktet på lampa).
    trykk: funksjon delar -> (punkt, retning) for ei ekstra kraft, t.d. trykk rett ned på ein utkragar.
    Eksporten (STL og GLB) er frå arbeidsstillinga t = 1."""
    bygg = byggjar if callable(byggjar) else (lambda t: byggjar)
    ut = dict(namn=namn, merknad='rekna, ikkje målt. Mål på delane frå settet er anslag frå foto.', stillingar=[])
    for t in stillingar:
        delar = bygg(float(t))
        if dytt is None:
            lo, hi = K.grenser(delar); V = np.vstack([m.vertices for _, _, m, _ in K.alle_under(delar)])
            p = V[np.argmax(V[:, 2])]
        else:
            p = np.asarray(dytt(delar), float)
        s = dict(t=float(t), kollisjonar=kollisjonar(delar, tillat), velt=velt(delar, p, krav_N))
        if trykk is not None:
            pt, rt = trykk(delar)
            s['trykk'] = dict(punkt_mm=[round(float(x), 1) for x in pt], retning=[float(x) for x in rt], kraft_N=round(tippkraft(delar, pt, rt), 2))
        ut['stillingar'].append(s)
    delar = bygg(1.0)
    ut['masse'] = masse(delar); ut['varme'] = varme(delar); ut['utskrift'] = utskrift(delar)
    lo, hi = K.grenser(delar)
    ut['maal_mm'] = [round(float(x), 1) for x in hi - lo]
    ut['settdelar'] = sorted({d.pid for d in delar if d.pid})
    ut['eksport'] = {k: ([os.path.relpath(f, mappe).replace('\\', '/') for f in v] if isinstance(v, list) else os.path.relpath(v, mappe).replace('\\', '/'))
                     for k, v in eksporter(delar, mappe, namn).items()}
    os.makedirs(mappe, exist_ok=True)
    json.dump(ut, open(os.path.join(mappe, 'sjekk.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False, default=_j)
    # ---- sjekk.md
    L = ['# Kontroll: %s' % namn, '', 'Alt er rekna, ikkje målt. Måla på delane frå settet er anslag frå foto, og massane er usikre til delane er vegne.', '']
    m = ut['masse']
    L += ['## Masse', '', '| Del | Slag | Gram | ± | Kjelde |', '| --- | --- | --- | --- | --- |']
    L += ['| %s | %s | %s | %s | %s |' % (r['namn'], r['slag'] + (' ' + r['pid'] if r['pid'] else ''), _nn(r['g']), _nn(r['pm_g']), r['kjelde']) for r in m['rader']]
    L += ['', 'Samla %s g ± %s (rekna; ± er ANTAKING: 35 %% på delar frå settet, 15 %% på trykte, 10 %% på kjøpte). Kravet F8 er høgst 1 200 g: %s. Tyngdepunkt (%s) mm. Ytre mål %s mm.' % (
        _nn(m['total_g']), _nn(m['pm_g']), 'held' if m['total_g'] <= 1200 else 'held ikkje', ', '.join(_nn(x) for x in m['tp_mm']), ' × '.join(_nn(x) for x in ut['maal_mm'])), '']
    L += ['## Kollisjon og velt langs gesten', '', '| t | Kollisjonar | Dytt som veltar (N) | Retning | Held %s N | Veltevinkel | Fot cm² |' % _nn(krav_N), '| --- | --- | --- | --- | --- | --- | --- |']
    for s in ut['stillingar']:
        kol = '; '.join('%s mot %s %s mm³%s' % (c['a'], c['b'], _nn(c['volum_mm3']), ' (tillate)' if c['tillate'] else '') for c in s['kollisjonar']) or 'ingen'
        v = s['velt']
        L.append('| %s | %s | %s (lett %s) | %s° | %s | %s° | %s |' % (_nn(s['t'], 2), kol, _nn(v['dytt_N'], 1), _nn(v.get('dytt_N_lett', 0), 1), _nn(v.get('dytt_retning_grader', 0)),
                                                             'ja' if v['held'] else 'nei', _nn(v.get('veltevinkel', 0)), _nn(v.get('fot_cm2', 0))))
    v1 = ut['stillingar'][-1]['velt']
    L += ['', 'Dyttepunkt i arbeidsstillinga: (%s) mm. Lampa glir ved om lag %s N (friksjon %s, ANTAKING). Kravet F9 er høgst 200 cm² fot: %s.' % (
        ', '.join(_nn(x) for x in v1.get('punkt_mm', [])), _nn(v1.get('glid_N', 0), 1), _nn(MY, 1), 'held' if v1.get('fot_cm2', 0) <= 200 else 'held ikkje'), '']
    if trykk is not None:
        L += ['Ekstra kraft: ' + '; '.join('t %s: %s N' % (_nn(s['t'], 2), _nn(s['trykk']['kraft_N'], 1)) for s in ut['stillingar']) + '.', '']
    L += ['## Varme', '']
    if ut['varme']:
        L += ['| LED | Watt | Ligg mot | Kjøleflate cm² | Temperatur °C | Råd |', '| --- | --- | --- | --- | --- | --- |']
        L += ['| %s | %s | %s | %s | %s | %s |' % (h['namn'], _nn(h['watt'], 2), ', '.join(h['ligg_mot']) or 'ingenting', _nn(h['kjoleflate_cm2']),
                                               _nn(h['temp_C']) if h['temp_C'] is not None else 'ukjent', h['raad']) for h in ut['varme']]
        L += ['', 'Rekna, ikkje målt. ANTAKING: %.0f %% av watten blir varme, flata gjev frå seg %.0f W/m²K, rommet held %.0f °C. Trykt PLA mjuknar ved 55 til 60 °C.' % (VARMEDEL * 100, H_KONV, ROMTEMP), '']
    else:
        L += ['Ingen del har oppgjeven watt.', '']
    L += ['## Trykte delar (Bambu Lab P1S, 256 × 256 × 256 mm)', '', '| Del | Plast | Mål på plata mm | Passar | Overheng cm² | Gram | Merknad |', '| --- | --- | --- | --- | --- | --- | --- |']
    L += ['| %s | %s | %s | %s | %s | %s | %s |' % (p['namn'], p['plast'], ' × '.join(_nn(x) for x in p['maal_mm']), 'ja' if p['passar'] else 'nei', _nn(p['overheng_cm2']), _nn(p['g']), p['merknad'])
          for p in ut['utskrift']]
    L += ['', 'Gram er rekna med %s mm vegg og %.0f %% fyll (ANTAKING).' % (_nn(PRINT_SKAL, 1), PRINT_FYLL * 100), '',
          '## Tryggleik', '', '- P04 (straumforsyninga, 230 V) og elektronikken hennar er ikkje med og skal aldri brukast.',
          '- Fresnelspegelen og linsene må aldri stå i sol: dei samlar sollyset og kan tenne papir.',
          '- LED-ar skal liggje på metall eller ha ein varmeveg. Trykt PLA mjuknar ved 55 til 60 °C.', '']
    open(os.path.join(mappe, 'sjekk.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L))
    return ut
