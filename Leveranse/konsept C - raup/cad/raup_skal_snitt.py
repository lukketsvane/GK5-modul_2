# -*- coding: utf-8 -*-
"""raup_skal_snitt.py · hovudforma til Raup som tjukt skal for P1S, utan innvendig gitter (snittmetoden).

Kroppen i raup_produksjon.py er ein loft gjennom vassrette snitt av kjelda. Hòlrommet blir laga som ei ekte
3D-erosjon med ei kule på radius VEGG: eit punkt i høgd z ligg i hòlrommet berre om kula rundt det ligg heilt
inne i kroppen, altså om xy-punktet ligg i snittet ved z' krympa med sqrt(VEGG^2 - (z'-z)^2) for alle z' nær z.
Det gjev minst VEGG mm vegg også under den skrå toppflata, der vanleg 2D-forskyving gjev for tynn vegg og
gjennombrot (grunnen til at første uthòlinga i raup_produksjon.py feila). Snitt under z = 0 er ikkje med,
så botnen blir open. Hòlrommet er ein loft gjennom dei krympa snitta, og skalet er kroppen minus hòlrommet.

    py -3 cad/raup_skal_snitt.py [vegg_mm]

Skriv cad/raup_skal.step, produksjon/raup_skal_P1S.stl og kontroll/raup_skal.json.
"""
import sys, json, runpy, math
from pathlib import Path
import numpy as np
import cadquery as cq
from shapely.geometry import Polygon
from scipy.ndimage import gaussian_filter1d

VEGG = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0     # mm
MARGIN = 0.3                                                 # ekstra mm mot feil i loften mellom snitta
N = 60                                                       # punkt per snitt, som i raup_produksjon.py
P1S = 256.0

R = Path(__file__).resolve().parents[1]
CAD, UT, KONTROLL = R / 'cad', R / 'produksjon', R / 'kontroll'
ctx = runpy.run_path(str(CAD / 'snitt_fbx.py'))
section, loops = ctx['section'], ctx['loops']
TOPP = 196.2                                                 # toppen av loften i raup_produksjon.py


def ytre(z):
    """Snittet av kroppen i høgd z, som i raup_produksjon.sample (60 punkt, glatta)."""
    z = min(max(z, 1.0), TOPP)
    c = loops(section('c001', z + .0137))
    if not c:
        return None
    p = np.asarray(c[0])
    if not np.allclose(p[0], p[-1]):
        p = np.vstack([p, p[0]])
    if not Polygon(p).exterior.is_ccw:
        p = p[::-1]
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
    s = np.linspace(0, d[-1], N, endpoint=False)
    xy = np.array([np.interp(s, d, p[:, i]) for i in range(2)]).T
    xy = gaussian_filter1d(xy, .4, axis=0, mode='wrap')
    return Polygon(xy).buffer(0)


# ytre snitt kvar 0,5 mm
ZY = np.r_[np.arange(0.0, TOPP, 0.5), TOPP]
YTRE = {round(float(z), 2): ytre(z) for z in ZY}


def indre(z):
    """Hòlrommet i høgd z: snitta i [z - VEGG, z + VEGG] krympa med kuleradiusen i kvar høgd."""
    o = None
    for zz, poly in YTRE.items():
        dz = zz - z
        if abs(dz) > VEGG or zz < 0:
            continue
        if poly is None or poly.is_empty:
            return None
        r = math.sqrt(max(VEGG * VEGG - dz * dz, 0.0)) + MARGIN
        k = poly.buffer(-r, join_style=1)
        o = k if o is None else o.intersection(k)
        if o.is_empty:
            return None
    if z + VEGG > TOPP:                                       # over toppen finst ingen kropp
        return None
    if o is None or o.is_empty:
        return None
    if o.geom_type == 'MultiPolygon':
        o = max(o.geoms, key=lambda g: g.area)
    return o


def til_punkt(poly, forrige=None):
    p = np.asarray(poly.exterior.coords)[:-1]
    if not Polygon(p).exterior.is_ccw:
        p = p[::-1]
    p = np.vstack([p, p[:1]])
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
    s = np.linspace(0, d[-1], N, endpoint=False)
    xy = np.array([np.interp(s, d, p[:, i]) for i in range(2)]).T
    if forrige is None:
        return np.roll(xy, -int(np.argmax(xy[:, 0])), axis=0)
    k = int(np.argmin([np.sum((np.roll(xy, -j, axis=0) - forrige) ** 2) for j in range(N)]))
    return np.roll(xy, -k, axis=0)


def loft(profil):
    wires = [cq.Wire.assembleEdges([cq.Edge.makeSpline([cq.Vector(float(x), float(y), float(z)) for x, y in pts],
                                                        periodic=True)]) for z, pts in profil]
    s = cq.Solid.makeLoft(wires, ruled=False)
    if not s.isValid() or s.Volume() < 1:
        raise ValueError('ugyldig loft')
    return s


# Kroppen, nøyaktig som i raup_produksjon.py
zs = sorted(set([1] + list(range(5, 196, 5)) + [196, 196.2]))
prof = []
for z in zs:
    p = np.asarray(ytre(z).exterior.coords)[:-1]
    p = p if Polygon(p).exterior.is_ccw else p[::-1]
    prof.append((z, til_punkt(Polygon(p), prof[-1][1] if prof else None)))
kropp = loft([(0, prof[0][1])] + prof)
print('kropp', kropp.isValid(), round(kropp.Volume() / 1e3), 'cm3', flush=True)

# Hòlrommet: krympa snitt kvar 2 mm, tettare mot toppen, frå z = 0 til siste ikkje-tomme snitt
zi = list(np.arange(0.0, 150.0, 2.0)) + list(np.arange(150.0, TOPP, 1.0))
indre_prof, forrige_areal = [], None
for z in zi:
    poly = indre(z)
    if poly is None or poly.area < 40:
        break
    if forrige_areal and poly.area < 0.35 * forrige_areal:  # snittet sprang (delte seg): stopp før
        break
    indre_prof.append((float(z), til_punkt(poly, indre_prof[-1][1] if indre_prof else None)))
    forrige_areal = poly.area
z_tak = indre_prof[-1][0]
print(f'hòlrom: {len(indre_prof)} snitt, frå botnen til z = {z_tak:.1f} mm', flush=True)
hol = loft([(-5.0, indre_prof[0][1])] + indre_prof)          # stikk ut under botnen: open botn

skal = kropp.cut(hol)
if not skal.isValid():
    skal = skal.fix()
ok = skal.isValid() and skal.Volume() > 0 and len(skal.Solids()) == 1
sb = skal.BoundingBox()
passar = all(d <= P1S for d in (sb.xlen, sb.ylen, sb.zlen))
print('skal', ok, round(skal.Volume() / 1e3, 1), 'cm3', flush=True)

cq.exporters.export(skal, str(CAD / 'raup_skal.step'))
attlest = cq.importers.importStep(str(CAD / 'raup_skal.step')).val()
cq.exporters.export(skal, str(UT / 'raup_skal_P1S.stl'), tolerance=0.05, angularTolerance=0.1)

rapport = {
    'filer': ['cad/raup_skal.step', 'produksjon/raup_skal_P1S.stl'],
    'metode': '3D-erosjon av snitta med kule (raup_skal_snitt.py)',
    'veggtjukkleik_mm': VEGG, 'margin_mm': MARGIN,
    'botn': 'open', 'hòlrom_til_z_mm': z_tak,
    'gyldig_BRep': bool(ok), 'STEP_attlest_gyldig': bool(attlest.isValid()),
    'eitt_solid': len(skal.Solids()) == 1,
    'mal_mm': [round(sb.xlen, 1), round(sb.ylen, 1), round(sb.zlen, 1)],
    'passar_P1S_256': bool(passar),
    'volum_cm3': round(skal.Volume() / 1e3, 1),
    'masse_PLA_g': round(skal.Volume() / 1e3 * 1.24),
    'utskrift': 'Ståande på den opne botnen. Inga fylling: veggen er heile skalet. Set veggliner så dei fyller '
                'veggen (3 mm / 0,42 mm = 7), eller sparse infill 100 %. Taket i hòlrommet er flatt: brubygging, '
                'eller støtte inne om taket er breitt.',
}
(KONTROLL / 'raup_skal.json').write_text(json.dumps(rapport, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(rapport, indent=2, ensure_ascii=False), flush=True)
