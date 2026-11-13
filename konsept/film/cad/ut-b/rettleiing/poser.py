# -*- coding: utf-8 -*-
"""
poser.py  ·  legg delane frå ../samla/ i stillingane rettleiinga treng

Berre rørsle, ingen ny geometri. Bjelken dreier om røyret, slik han gjer i northern.py:
aksen går langs x gjennom y = YT, z = AKSE_H (../geometri.json). Samla-filene står i VINKEL (35°).

  python3 poser.py        skriv delar/<id>@<vinkel>.stl

  0    ruta vassrett, til montering på røyret og stoppskruen
  80   største helling
  180  bjelken på benken med loket opp

E (fire like skruar i éi fil) blir òg skriven som éin skrue, E1@<vinkel>.stl, den lengst til venstre.
Spesifikasjonen set dei fire med «at», 84 mm frå kvarandre (SKRUAR_X i northern.py).
"""
import json, os
import numpy as np
import trimesh

HER = os.path.dirname(os.path.abspath(__file__))
SAMLA = os.path.join(HER, '..', 'samla')
G = json.load(open(os.path.join(HER, '..', 'geometri.json'), encoding='utf-8'))
UT = os.path.join(HER, 'delar')
DREIER = ('05', '06', '07', '08', '09', '10', '11', '13', 'E')      # delane som sit i bjelken
VINKLAR = (0, 80, 180)

if __name__ == '__main__':
    os.makedirs(UT, exist_ok=True)
    for v in VINKLAR:
        M = trimesh.transformations.rotation_matrix(np.radians(v - G['VINKEL']), [1, 0, 0], [0, G['YT'], G['AKSE_H']])
        for i in DREIER:
            m = trimesh.load(os.path.join(SAMLA, i + '.stl'), force='mesh')
            m.apply_transform(M)
            m.export(os.path.join(UT, '%s@%d.stl' % (i, v)))
            if i == 'E':
                min(m.split(only_watertight=False), key=lambda s: s.bounds[0][0]).export(os.path.join(UT, 'E1@%d.stl' % v))
    print('delar/: %d filer' % (len(os.listdir(UT))))
