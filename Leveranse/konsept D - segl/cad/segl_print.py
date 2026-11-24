# -*- coding: utf-8 -*-
"""
segl_print.py  ·  prototypdelar for Bambu Lab P1S (256 x 256 mm), PETG

    python segl_print.py

Skriv ../print/Segl_prototyp_P1S_PETG.3mf (usliced, delane snudde og plasserte) og STL per del.
Delane: E02 klampa (snudd, toppen ned), E02 botnplata, E03 knappen (toppen ned), E01 lysberaren (botnen ned).
PETG fordi LED-beraren blir varm (forsking: PLA mjuknar ved om lag 53 °C på ein naken berar ved 3,3 W).
Ikkje slica her: opne fila i Bambu Studio, vel PETG, 0,20 mm lag, 3 veggar, 15 % gyroid, støtte berre der han ber om det.
"""
import os, sys
import numpy as np
import trimesh
import cadquery as cq
HER = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HER)
import segl_cad as C

UT = os.path.join(os.path.dirname(HER), 'print')


def mesh(sol):
    import tempfile
    f = os.path.join(tempfile.gettempdir(), 'segl_print_tmp.stl')
    cq.exporters.export(cq.Workplane().add(sol), f, tolerance=0.02, angularTolerance=0.1)
    m = trimesh.load(f, force='mesh')
    m.merge_vertices()
    return m


def legg_paa(m, rot=None, xy=(0, 0)):
    if rot is not None:
        m.apply_transform(rot)
    b = m.bounds
    m.apply_translation([xy[0] - b[0][0], xy[1] - b[0][1], -b[0][2]])
    return m


if __name__ == '__main__':
    os.makedirs(UT, exist_ok=True)
    delar, _ = C.bygg()
    R = trimesh.transformations.rotation_matrix
    plate = {
        'E02_klampe_skal': legg_paa(mesh(delar['E02']), R(np.pi, [1, 0, 0]), (20, 20)),
        'E02_klampe_botnplate': legg_paa(mesh(delar['E02-BOTN']), None, (75, 20)),
        'E03_knapp': legg_paa(mesh(delar['E03']), R(np.pi, [1, 0, 0]), (125, 20)),
        'E01_lysberar': legg_paa(mesh(delar['E01']), None, (20, 90)),      # botnen på plata, setet 45° utan støtte
    }
    sc = trimesh.Scene()
    for k, m in plate.items():
        b = m.bounds
        print(k, 'vasstett', m.is_watertight, 'storleik', np.round(b[1] - b[0], 1), 'inne på plata', bool((b[1][:2] <= 256).all()))
        m.export(os.path.join(UT, f'{k}_P1S.stl'))
        sc.add_geometry(m, node_name=k)
    sc.export(os.path.join(UT, 'Segl_prototyp_P1S_PETG.3mf'))
    print('skrive', os.listdir(UT))
