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
import json, os
import numpy as np
import trimesh

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
                    ein, _ = i_origo(bitar[0]); ein.export(os.path.join(UT, 'E.stl'))
                    pos['E_benk'] = [i_origo(b)[1] for b in bitar[:-1]]
            else:
                m.export(os.path.join(UT, '%s@%d.stl' % (i, v)))
    bitar = last('F').split(only_watertight=False)
    ein, _ = i_origo(bitar[0]); ein.export(os.path.join(UT, 'F.stl'))
    pos['F'] = [i_origo(b)[1] for b in bitar]
    bitar = last('03').split(only_watertight=False)
    ein, _ = i_origo(bitar[0]); ein.export(os.path.join(UT, 'S.stl'))
    pos['S'] = [i_origo(b)[1] for b in bitar]
    json.dump(pos, open(os.path.join(UT, 'posisjonar.json'), 'w'), indent=1)
    print('delar/: %d filer' % len(os.listdir(UT)), {k: len(v) for k, v in pos.items()})
