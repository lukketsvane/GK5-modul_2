# -*- coding: utf-8 -*-
"""
lag_spesifikasjon.py  ·  skriv spesifikasjon.json til verktoy/ikea/bygg.py (formnerd) for Sveip mini, M02

  python3 lag_delar.py
  python3 lag_spesifikasjon.py
  python3 <formnerd>/verktoy/ikea/bygg.py spesifikasjon.json ut
"""
import json
import os

HER = os.path.dirname(os.path.abspath(__file__))
POS = json.load(open(os.path.join(HER, 'delar', 'posisjonar.json'), encoding='utf-8'))
A, B, C, D = POS['A'], POS['B'], POS['C'], POS['D']
REV = 'M02'


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
def flytt(p, dx=0.0, dy=0.0, dz=0.0): return [round(p[0] + dx, 3), round(p[1] + dy, 3), round(p[2] + dz, 3)]


innmat = c('M2', 'MB', 'M3') + [ca('Ay', A), ca('Dy', D), ca('Cy', C)]
heil = c('M1') + innmat + [ca('By', B)]
alt = heil + c('M4')
logo, kant, felt, zp = POS['logo'], POS['kant'], POS['felt'], POS['z_plate']
lomme, hylse = POS['C_lomme'], POS['A_hylse']
matrise = [round(sum(p[i] for p in D) / len(D), 2) for i in range(3)]
skrue = A[2]
kropp = [42.0, 0.0, 42.0]                  # midt i M1
kortmidt = [round(logo[0] - 13.0, 2), logo[1], logo[2]]      # midt på kortet (v = 1)

# Fast utsnitt per sekvens (centre, span i mm): same skala gjennom sekvensen
BENK = dict(centre=flytt(kortmidt, dy=10.0), span=34)       # steg 1–2: rista og kortet på benken
STOLPE = dict(centre=matrise, span=38)      # steg 3–4
LAMPE = dict(centre=[42.0, 0.0, 50.0], span=62)   # steg 7, 8 og kontroll

PROV = dict(centre=flytt(kortmidt, dx=-6.0, dy=-6.0), span=28)      # porten: rista åleine
# ---------------------------------------------------------------- port: prøv før monteringa
prov_hylse = steg('Prøv', [
    {'view': 'benk', **PROV, 'scene': c('M3') + [ny('Dy', [0, -14, 0], at=[D[4]]), ny('Ay', [0, -14, 0], at=hylse)],
     'texts': [{'point': flytt(D[4], dy=-16.6), 'text': 'Ø 2,1', 'offset': [-40, -4], 'size': 9},
               {'point': flytt(logo, dy=-5), 'text': 'Ø 2,6', 'offset': [20, -16], 'size': 9}]},
    {'view': 'benk', **PROV, 'scene': c('M3') + [ca('Dy', [D[4]]), utan('Ay', [0, -14, 0], at=hylse, line='none')],
     'arrows': [[flytt(logo, dz=-6.0, dy=-6.0), flytt(logo, dz=-6.0, dy=-20.0)]]}],
    n=False, icons=['atvaring'], hardware=[], flow='right', note='D skal gli. A skal gå stramt inn, og ut att.')
prov_chassis = steg('Prøv', [
    {'view': 'under', 'scene': c('M1') + [ny('M2', [0, 0, -40], line='none', label_offset=[-46, 6])],
     'arrows': [[[30.0, 0.0, -14.0], [30.0, 0.0, -2.0]]]}],
    n=False, hardware=[], note='M2 skal gli inn med lett klem. Ta ut att.')

# ---------------------------------------------------------------- steg
fjor = steg('Fjør', [{'view': 'rygg', **BENK, 'scene': c('M3') + [utan('Cy', [0, 10, 0], at=lomme)],
                      'detail': {'centre': flytt(logo, dy=1.0), 'span': 6, 'pos': [0.84, 0.62], 'r': 75, 'qty': '1x', 'letter': 'C',
                                 'label': 'Ø 3 × 3', 'scene': c('M3') + [ny('Cy', [0, 3.5, 0], at=lomme)]}}])
kort = steg('Kort', [{'view': 'rygg', **BENK, 'scene': c('M3') + [ca('Cy', lomme), ny('MB', [0, 20, 0], line='none')],
                      'arrows': [[[9.0, 9.6, 6.0], [9.0, -5.9, 6.0]], [[9.0, 9.6, 51.6], [9.0, -5.9, 51.6]]]}])
stolpe = steg('Mot stolpen', [{'view': 'iso', **STOLPE,
                               'scene': c('M2') + [utan('MB', [0, -24, 0], line='none'), utan('M3', [0, -24, 0], line='none'),
                                                   utan('Cy', [0, -24, 0], at=C, line='none')],
                               'callouts': [{'part': 'MB', 'point': [44.0, -32.4, 50.0], 'offset': [34, 26]}],
                               'arrows': [[[9.0, -31.0, 58.0], [9.0, -7.3, 58.0]]],           # endar på framsida av stolpen
                               'detail': {'centre': flytt(kant, 1.0, 0.4, 1.5), 'span': 5.5, 'pos': [0.13, 0.3], 'r': 65,
                                          'scene': c('M2', 'MB')}}],
              hardware=[])
skruar = steg('Skruar', [{'view': 'iso', **STOLPE, 'scene': c('M2', 'MB', 'M3') + [ca('Cy', C), utan('Ay', [0, -10, 0], at=A)],
                          'detail': {'centre': skrue, 'span': 6, 'pos': [0.82, 0.8], 'r': 75, 'qty': '5x', 'letter': 'A',
                                     'scene': c('M2', 'MB', 'M3') + [ny('Ay', [0, -4, 0], at=[skrue])]}}])
# rista opp: leiarane går rett ned, og limet renn ikkje ut på framsida. Éi rad er vist, mengda står på bobla
leiarar = steg('Lysleiarar', [{'view': 'benk', 'centre': flytt(matrise, 4.2, 0.0, -5.6), 'span': 45,
                               'scene': c('M2', 'MB', 'M3') + [ca('Ay', A), ca('Cy', C), utan('Dy', [0, -12, 0], at=D[10:15])],
                               'detail': {'centre': flytt(D[12], dy=-5.1), 'span': 5, 'pos': [0.84, 0.74], 'r': 75, 'qty': '25x', 'letter': 'D',
                                          'scene': c('M2', 'MB', 'M3') + [ca('Dy', [D[k] for k in (6, 7, 8, 11, 13, 16, 17, 18)]),
                                                                          ny('Dy', [0, -3.5, 0], at=[D[12]])]}}],
               icons=['lim'], hardware=[['D', 25]], warning='Ingenting over framsida: klipp 0–0,2 mm under.')
inn = steg('Inn i stamma', [{'view': 'under', 'centre': [30.0, 0.0, 6.0], 'span': 80,
                             'scene': c('M1') + [ny('M2', [0, 0, -72], line='none', label_offset=[-46, 6])] +
                             [utan(n, [0, 0, -72], line='none') for n in ('MB', 'M3')] +
                             [utan(n, [0, 0, -72], at=p, line='none') for n, p in (('Ay', A), ('Dy', D), ('Cy', C))],
                             'arrows': [[[30.0, 0.0, -11.0], [30.0, 0.0, -1.5]]],
                             'detail': {'centre': [16.0, -6.0, 0.0], 'span': 13, 'pos': [0.84, 0.3], 'r': 75,
                                        'scene': c('M1') + [ny('M2', [0, 0, 0])]}}],         # sluttstilling: golvet i flukt med stamma
           hardware=[])
messing = steg('Messingskrue', [{'view': 'iso', **LAMPE, 'scene': c('M1') + innmat + [utan('By', [0, -22, 0], at=B)],
                                 'detail': {'centre': felt, 'span': 7, 'pos': [0.86, 0.74], 'r': 75, 'qty': '1x', 'letter': 'B',
                                            'label': 'M3 × 4', 'scene': c('M1') + innmat + [ny('By', [0, -5, 0], at=B)]}}],
               warning='Ikkje stram hardt.')
plate = steg('Lysplate', [{'view': 'iso', **LAMPE, 'scene': heil + [ny('M4', [0, 0, 40], line='none', label_offset=[-70, 0])],
                           'arrows': [[[74.0, -17.0, zp + 40.0], [74.0, -17.0, 86.5]]]}])
kabel = steg('USB', [{'view': 'bak', 'scene': alt + [ny('E', [26, 0, 0], label_offset=[-150, -38])]}],
             warning='Ikkje rør messingen når kabelen går i.', note='python.microbit.org · sveip_mikrobit.py')
kontroll = steg('Kontroll', [{'view': 'iso', **LAMPE, 'scene': alt + c('E'),
                              'arrows': [[flytt(B[0], dy=-30.0), flytt(B[0], dy=-3.5)]]}],
                n=False, icons=['ok'], note='Kort trykk på messingen: av og på. Hald: matrisa sveiper.')
bakside = steg('Bakside', [{'view': 'bak', 'centre': kropp, 'span': 120, 'scene': alt + c('E')}], n=False,
               note='Leveranse/konsept D - sveip/variantar/mikrobit')

pages = [
    {'type': 'cover', 'title': 'SVEIP MINI', 'view': 'iso', 'scene': alt, 'inset_pt': 40},
    {'type': 'inventory', 'cols': 2, 'parts': ['M1', 'M2', 'M3', 'M4', 'MB']},
    {'type': 'hardware', 'parts': ['A', 'B', 'C', 'D', 'E'], 'cols': 3, 'row_height': 250, 'centred': True},
    par(prov_hylse, prov_chassis, split=0.45),
    par(fjor, kort, split=0.5),
    par(stolpe, skruar, split=0.5),
    par(leiarar, inn, split=0.5),
    par(messing, plate, split=0.5),
    par(kabel, kontroll, split=0.5),
    bakside,
]

spec = {
    'meta': {'title': 'SVEIP MINI', 'footer': 'Sveip mini · micro:bit V2 · ' + REV, 'orientation': 'portrait'},
    'style': {'line_pt': 0.75, 'kontur': 1.6, 'svarting': 1.5, 'boble_pt': 1.1, 'sidetal_ytre': True, 'steg_pt': 32, 'mengd_pt': 18,
              'mengd_fyrst': True, 'tittel_pt': 80, 'tittel_feit': True, 'sidetal_pt': 9, 'del_pt': 7.5, 'lett_pt': 0.5,
              'ramme': False, 'beslagkolonne': False},
    'views': {'iso': {'dir': [-0.75, -1.0, 0.6], 'up': [0, 0, 1]},
              'under': {'dir': [-0.75, -1.0, -0.7], 'up': [0, 0, 1]},
              'hogre': {'dir': [0.9, -1.0, -0.3], 'up': [0, 0, 1]},
              'bak': {'dir': [0.7, 1.0, 0.55], 'up': [0, 0, 1]},
              'benk': {'dir': [-1.0, -0.65, -0.75], 'up': [0, -1, 0]},       # framsida av kortet opp
              'rygg': {'dir': [-1.0, 0.65, 0.75], 'up': [0, 1, 0]}},         # baksida opp: rista med lommene opp
    'parts': parts,
    'pages': pages,
}
json.dump(spec, open(os.path.join(HER, 'spesifikasjon.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('spesifikasjon.json: %d sider, %d delar' % (len(pages), len(parts)))
