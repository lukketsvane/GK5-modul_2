# -*- coding: utf-8 -*-
"""
lag_delar.py  ·  legg delane frå ../ut-c/samla/ i stillingane rettleiinga treng

Berre rørsle, ingen ny geometri. Bjelken dreier om røyret, slik han gjer i ruta_c.py. Samla-filene står i 35°.

  0     ruta vassrett: bjelken inn på røyret
  28    bremseskruen står loddrett: låsing og brems nedanfrå
  35    visingsstillinga
  80    største helling
  180   bjelken på benken med loket opp

Skriv òg éin skrue av kvart slag i origo, éin skivestabel, og posisjonane dei skal stå i (delar/posisjonar.json).
"""
import json, os, sys
import numpy as np
import trimesh
import cadquery as cq

HER = os.path.dirname(os.path.abspath(__file__))
UTC = os.path.join(HER, '..', 'ut-c')
G = json.load(open(os.path.join(UTC, 'geometri.json'), encoding='utf-8'))
UT = os.path.join(HER, 'delar')
VINKLAR = (0, 28, 35, 80, 180)


def last(i):
    return trimesh.load(os.path.join(UTC, 'samla', i + '.stl'), force='mesh')


def drei(m, v):
    m = m.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(v - G['VINKEL']), [1, 0, 0], [0, G['YT'], G['AKSE_H']]))
    return m


def skrue(lengd, hovud_opp=True):
    """M3 med sylinderhovud, spor og gjenger, til beslagsida og detaljboblene. Sentrert i origo som dei enkle skruane."""
    pkt = [(0.0, 0.0), (1.15, 0.0)]
    z = 0.3
    while z + 1.0 <= lengd - 0.6:                                   # gjenger som sagtenner, stigning 1 mm så dei syner i teikninga
        pkt += [(1.5, z + 0.5), (1.15, z + 1.0)]; z += 1.0
    pkt += [(1.5, lengd - 0.3), (1.5, lengd), (2.75, lengd), (2.75, lengd + 2.0), (0.0, lengd + 2.0)]
    f = cq.Workplane('XZ').polyline(pkt).close().revolve(360, (0, 0, 0), (0, 1, 0))
    f = f.cut(cq.Workplane('XY').box(6.0, 1.0, 1.0).translate((0, 0, lengd + 2.0 - 0.4)))
    f = f.translate((0, 0, -(lengd + 2.0) / 2))
    if not hovud_opp: f = f.rotate((0, 0, 0), (1, 0, 0), 180)
    v, t = f.val().tessellate(0.02, 0.15)
    return trimesh.Trimesh([[q.x, q.y, q.z] for q in v], t)


def i_origo(m):
    m = m.copy(); c = m.bounds.mean(axis=0); m.apply_translation(-c)
    return m, [round(float(x), 2) for x in c]


if __name__ == '__main__':
    os.makedirs(UT, exist_ok=True)
    pos = {}
    for i in G['FASTE']:
        last(i).export(os.path.join(UT, i + '.stl'))
    for v in VINKLAR:
        for i in G['ROERLEGE']:
            m = drei(last(i), v)
            if i == 'E':                                            # fem lokskruar og låseskruen lengst til høgre
                bitar = sorted(m.split(only_watertight=False), key=lambda s: s.bounds[0][0])
                trimesh.util.concatenate(bitar[:-1]).export(os.path.join(UT, 'Elok@%d.stl' % v))
                bitar[-1].export(os.path.join(UT, 'Elaas@%d.stl' % v))
                if v == 180:
                    skrue(20.0).export(os.path.join(UT, 'E.stl'))               # på benken står lokskruane med hovudet opp
                    pos['E_benk'] = [i_origo(b)[1] for b in bitar[:-1]]
            else:
                m.export(os.path.join(UT, '%s@%d.stl' % (i, v)))
    bitar = last('F').split(only_watertight=False)
    skrue(10.0, hovud_opp=False).export(os.path.join(UT, 'F.stl'))                  # botnskruane går inn nedanfrå
    pos['F'] = [i_origo(b)[1] for b in bitar]
    skrue(8.0).export(os.path.join(UT, 'G.stl'))                                    # G er ein F kappa til 8 mm
    sys.path.insert(0, os.path.join(HER, '..'))
    import ruta_c as C                                                              # styrepinnane i bjelkeskøyten, på benken
    pos['P'] = [[round(float(q), 2) for q in C.paa_plass(C.L._syl_x(1.75, C.X_DEL_K - 5.0, C.X_DEL_K + 5.0, u, w), 180.0).val().Center().toTuple()] for (u, w) in C.STYREPINNAR]
    bitar = last('03').split(only_watertight=False)
    ein, _ = i_origo(bitar[0]); ein.export(os.path.join(UT, 'S.stl'))
    pos['S'] = [i_origo(b)[1] for b in bitar]
    json.dump(pos, open(os.path.join(UT, 'posisjonar.json'), 'w'), indent=1)
    print('delar/: %d filer' % len(os.listdir(UT)), {k: len(v) for k, v in pos.items()})
