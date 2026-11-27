# -*- coding: utf-8 -*-
"""
lag_spesifikasjon.py  ·  skriv spesifikasjon.json til verktoy/ikea/bygg.py (formnerd) for Sveip mini

  python3 lag_delar.py
  python3 lag_spesifikasjon.py
  python3 <formnerd>/verktoy/ikea/bygg.py spesifikasjon.json ut
"""
import json
import os

HER = os.path.dirname(os.path.abspath(__file__))
POS = json.load(open(os.path.join(HER, 'delar', 'posisjonar.json'), encoding='utf-8'))
A, B, C, D = POS['A'], POS['B'], POS['C'], POS['D']


def mesh(fil, ident, **k):
    return {'mesh': 'delar/%s.stl' % fil, 'id': ident, 'qty': 1, **k}


def beslag(bokstav, tal, fil, **k):
    return {'letter': bokstav, 'qty': tal, 'kind': 'hardware', 'mesh': 'delar/%s.stl' % fil, **k}


parts = {
    'M1': mesh('M1', 'M1', fill=False), 'M2': mesh('M2', 'M2'), 'M3': mesh('M3', 'M3'),
    'M4': mesh('M4', 'M4', fill=False), 'MB': mesh('MB', 'MB'),
    'A': beslag('A', 5, 'A'), 'Ay': beslag('A', 1, 'A_y', counts_as='A'),
    'B': beslag('B', 1, 'B'), 'By': beslag('B', 1, 'B_y', counts_as='B'),
    'C': beslag('C', 1, 'C'), 'Cy': beslag('C', 1, 'C_y', counts_as='C'),
    'D': beslag('D', 25, 'D'), 'Dy': beslag('D', 1, 'D_y', counts_as='D'),
    'E': beslag('E', 1, 'E', thumb_view='hogre'),
}


def c(*namn): return [{'part': n, 'role': 'context'} for n in namn]
def ca(n, at): return {'part': n, 'role': 'context', 'at': at}
def ny(n, ex, at=None, **k):
    e = {'part': n, 'role': 'new', 'explode': ex, **k}
    if at: e['at'] = at
    return e
def utan(n, ex, at=None, **k): return ny(n, ex, at, label=False, **k)
def steg(tittel, figurar, **k): return {'type': 'step', 'title': tittel, 'figures': figurar, **k}
def par(a, b, **k): return {'type': 'steps', 'steps': [a, b], **k}


innmat = c('M2', 'MB', 'M3') + [ca('Ay', A), ca('Dy', D), ca('Cy', C)]
heil = c('M1') + innmat + [ca('By', B)]
alt = heil + c('M4')
logo = POS['logo']
felt = POS['felt']
matrise = [round(sum(p[i] for p in D) / len(D), 2) for i in range(3)]
skrue = A[2]

prov = steg('Prøv', [{'view': 'benk', 'scene': c('M3') + [ny('Dy', [0, -14, 0], at=[D[12]]), ny('By', [0, -14, 0], at=[[logo[0], -13.4, logo[2]]])]}],
            n=False, icons=['atvaring'], hardware=[], note='Stramt? Kanal Ø 2,1 · hylse Ø 2,6')
fjor = steg('Fjør', [{'view': 'benk', 'scene': c('MB') + [utan('Cy', [0, -12, 0], at=C)],
                      'detail': {'centre': [logo[0], logo[1] - 2.0, logo[2]], 'span': 13, 'pos': [0.84, 0.62], 'r': 60, 'qty': '1x', 'letter': 'C',
                                 'scene': c('MB') + [ny('Cy', [0, -4, 0], at=C)]}}])
rist = steg('Lysrist', [{'view': 'benk', 'scene': c('MB') + [ca('Cy', C), ny('M3', [0, -24, 0])]}])
stolpe = steg('Mot stolpen', [{'view': 'iso', 'scene': c('M2') + [ny('MB', [0, -24, 0], line='none'), utan('M3', [0, -24, 0], line='none'),
                                                                 utan('Cy', [0, -24, 0], at=C, line='none')],
                               'arrows': [[[9.0, -31.0, 58.0], [9.0, -7.3, 58.0]]],           # endar på framsida av stolpen
                               'detail': {'centre': [POS['kant'][0] + 1.0, POS['kant'][1] + 0.4, POS['kant'][2] + 1.5], 'span': 11,
                                          'pos': [0.86, 0.3], 'r': 60, 'scene': c('M2', 'MB')}}],
              icons=['snu'], hardware=[])
skruar = steg('Skruar', [{'view': 'iso', 'scene': c('M2', 'MB', 'M3') + [ca('Cy', C), utan('Ay', [0, -18, 0], at=A)],
                          'detail': {'centre': skrue, 'span': 12, 'pos': [0.82, 0.55], 'r': 58, 'qty': '5x', 'letter': 'A',
                                     'scene': c('M2', 'MB', 'M3') + [ny('Ay', [0, -5, 0], at=[skrue])]}}])
leiarar = steg('Lysleiarar', [{'view': 'iso', 'scene': c('MB', 'M3') + [ca('Ay', A), ny('Dy', [0, -14, 0], at=D)],
                               'detail': {'centre': matrise, 'span': 12, 'pos': [0.86, 0.3], 'r': 60,
                                          'scene': c('MB', 'M3') + [ca('Ay', A), ca('Dy', D)]}}],
               icons=['lim'], note='Klipp i flukt.')
inn = steg('Inn i stamma', [{'view': 'under', 'scene': c('M1') + [ny('M2', [0, 0, -72])] +
                             [utan(n, [0, 0, -72], line='none') for n in ('MB', 'M3')] +
                             [utan(n, [0, 0, -72], at=p, line='none') for n, p in (('Ay', A), ('Dy', D), ('Cy', C))]}],
           hardware=[])
messing = steg('Messingskrue', [{'view': 'iso', 'scene': c('M1') + innmat + [utan('By', [0, -22, 0], at=B)],
                                 'detail': {'centre': felt, 'span': 20, 'pos': 'right', 'r': 60, 'qty': '1x', 'letter': 'B',
                                            'scene': c('M1') + innmat + [ny('By', [0, -6, 0], at=B)]}}])
plate = steg('Lysplate', [{'view': 'iso', 'scene': heil + [ny('M4', [0, 0, 48])]}])
kabel = steg('USB', [{'view': 'hogre', 'scene': alt + [ny('E', [26, 0, 0])]}], note='python.microbit.org · sveip_mikrobit.py')
kontroll = steg('Kontroll', [{'view': 'iso', 'scene': alt}], n=False, icons=['ok'], note='Trykk på B: av og på. Hald: lyset sveiper.')
bakside = steg('Bakside', [{'view': 'bak', 'scene': alt}], n=False,
               note='Leveranse/konsept D - sveip/variantar/mikrobit · Sveip mini · M01')

pages = [
    {'type': 'cover', 'title': 'SVEIP MINI', 'view': 'iso', 'scene': alt, 'inset_pt': 40},
    {'type': 'inventory', 'cols': 2, 'parts': ['M1', 'M4', 'M2', 'M3', 'MB']},
    {'type': 'hardware', 'parts': ['A', 'B', 'C', 'D', 'E'], 'cols': 3, 'row_height': 170, 'centred': True},
    prov,
    par(fjor, rist, split=0.5),
    par(stolpe, skruar, split=0.5),
    par(leiarar, inn, split=0.45),
    par(messing, plate, split=0.5),
    par(kabel, kontroll, split=0.5),
    bakside,
]

spec = {
    'meta': {'title': 'SVEIP MINI', 'footer': 'Sveip mini · micro:bit V2 · M01', 'orientation': 'portrait'},
    'style': {'line_pt': 0.7, 'kontur': 1.6, 'svarting': 1.5, 'boble_pt': 1.1, 'sidetal_ytre': True, 'steg_pt': 32, 'mengd_pt': 15,
              'mengd_fyrst': True, 'tittel_pt': 64, 'tittel_feit': True, 'sidetal_pt': 9, 'del_pt': 8.5, 'lett_pt': 0.5,
              'ramme': False, 'beslagkolonne': False},
    'views': {'iso': {'dir': [-0.75, -1.0, 0.6], 'up': [0, 0, 1]},
              'under': {'dir': [-0.75, -1.0, -0.7], 'up': [0, 0, 1]},
              'hogre': {'dir': [0.9, -1.0, -0.3], 'up': [0, 0, 1]},
              'bak': {'dir': [0.7, 1.0, 0.55], 'up': [0, 0, 1]},
              'benk': {'dir': [-1.0, -0.65, -0.75], 'up': [0, -1, 0]}},
    'parts': parts,
    'pages': pages,
}
json.dump(spec, open(os.path.join(HER, 'spesifikasjon.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('spesifikasjon.json: %d sider, %d delar' % (len(pages), len(parts)))
