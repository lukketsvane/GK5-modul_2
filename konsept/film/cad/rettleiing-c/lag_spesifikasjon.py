# -*- coding: utf-8 -*-
"""
lag_spesifikasjon.py  ·  skriv spesifikasjon.json til verktoy/ikea/bygg.py (formnerd) frå geometrien i ../ut-c/

  python3 lag_delar.py
  python3 lag_spesifikasjon.py
  python3 <formnerd>/verktoy/ikea/bygg.py spesifikasjon.json ut
"""
import json, math, os
import trimesh

HER = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HER, '..', 'ut-c', 'geometri.json'), encoding='utf-8'))
K = json.load(open(os.path.join(HER, '..', 'ut-c', 'kontroll.json'), encoding='utf-8'))
POS = json.load(open(os.path.join(HER, 'delar', 'posisjonar.json')))
ROERLEGE = {'05v': 'kv', '05h': 'kh', '06v': 'lv', '06h': 'lh', '07': 'rute', '08': 'ark', '10': 'led', '11': 'ende', '13': 'sko'}
ID = {'05v': '05V', '05h': '05H', '06v': '06V', '06h': '06H'}
f = math.radians(G['HELL']); d = (math.sin(f), 0.0, math.cos(f))


def mesh(fil, ident, **k):
    return {'mesh': 'delar/%s.stl' % fil, 'id': ident, 'qty': 1, **k}


def beslag(bokstav, tal, **k):
    return {'letter': bokstav, 'qty': tal, 'kind': 'hardware', **k}


parts = {'fot': mesh('01', '01'), 'botnlok': mesh('02', '02'), 'ballast': mesh('03', '03'), 'stamme': mesh('04', '04'),
         'aksel': mesh('09', '09'), 'boge': mesh('12', '12'), 'ring': mesh('14', '14')}
for i, n in ROERLEGE.items():
    for v in (0, 28, 35, 80, 180):
        parts['%s%d' % (n, v)] = mesh('%s@%d' % (i, v), ID.get(i, i))
for v in (0, 28, 35, 80, 180):
    parts['elok%d' % v] = mesh('Elok@%d' % v, 'E')
skruar = {x['id']: x['tal'] for x in K['stykkliste']}
parts.update({
    'E': beslag('E', skruar['E'], mesh='delar/E.stl'),
    'Elaas': beslag('E', 1, mesh='delar/Elaas@28.stl', counts_as='E'),
    'F': beslag('F', skruar['F'], mesh='delar/F.stl'),
    'G': beslag('G', skruar['G'], mesh='delar/G.stl'),
    'Gbrems': beslag('G', 1, mesh='delar/G@28.stl', counts_as='G'),
    'S': beslag('S', skruar['03'], mesh='delar/S.stl'),
    'W': beslag('W', 2, primitive={'box': [13.1, 18.6, 8.3]}),
    'K': beslag('K', 16, primitive={'cylinder': {'r': 4.0, 'h': 2.5}}),
})


def c(*namn): return [{'part': n, 'role': 'context'} for n in namn]
def ny(n, ex, at=None, **k):
    e = {'part': n, 'role': 'new', 'explode': ex, **k}
    if at: e['at'] = at
    return e
def blad(v, utan=()): return ['%s%d' % (n, v) for n in ROERLEGE.values() if n not in utan]

stativ = ['fot', 'stamme', 'aksel', 'boge', 'ring']
heil = lambda v: c('fot', 'botnlok', 'ballast', 'stamme', 'aksel', 'boge', 'ring', *blad(v), 'elok%d' % v)
knottar = [[round(75.0 * math.cos(math.radians(22.5 * i)), 1), round(75.0 * math.sin(math.radians(22.5 * i)), 1), -1.25] for i in range(16)]
laas = [G['PINNE'][0], 18.0, 250.0]
kapp = K['kapp']

YT = G['YT']
midt = lambda fil: [round(float(v), 1) for v in trimesh.load(os.path.join(HER, 'delar', fil + '.stl'), force='mesh').bounds.mean(axis=0)]
steg = lambda tittel, figurar, **k: {'type': 'step', 'title': tittel, 'figures': figurar, **k}
par = lambda a, b, **k: {'type': 'steps', 'steps': [a, b], **k}
benk = c('kv180', 'kh180')
e5 = POS['E_benk'][4]

kapping = steg('Kapp', [{'view': 'iso', 'scene': c('stamme', 'aksel'), 'zoom': 1.0,
                         'texts': [{'point': [112.5, YT, 110.0], 'text': '%.0f mm' % kapp['stammeroyr_mm'], 'offset': [18, -10]},
                                   {'point': [-7.0, YT, 260.0], 'text': '%.0f mm' % kapp['akselroyr_mm'], 'offset': [-24, 16]}],
                         'callouts': [{'part': 'stamme', 'point': [150.0, YT, 175.0], 'offset': [34, 6]},
                                      {'part': 'aksel', 'point': [110.0, YT, 260.0], 'offset': [24, 26]}]}],
               n=False, icons=['atvaring'], note='G: kapp éin F til 8 mm.')
skiver = steg('Skiver', [{'view': 'under', 'zoom': 1.2, 'multiplier': 'x3', 'scene': c('fot') + [ny('S', [0, 0, -45], at=POS['S'])]}], icons=['lim'])
boge = steg('Røyr i boge', [{'view': 'iso', 'scene': c('boge') + [ny('stamme', [-70 * d[0], 0, -70 * d[2]]), ny('aksel', [-70, 0, 0])]}], icons=['lim'])
stamme = steg('Stamme i fot', [{'view': 'iso', 'scene': c('fot') + [ny('ring', [28 * d[0], 0, 28 * d[2]]), ny('stamme', [70 * d[0], 0, 70 * d[2]], label=False),
                                                                   ny('aksel', [70 * d[0], 0, 70 * d[2]], line='none', label=False),
                                                                   ny('boge', [70 * d[0], 0, 70 * d[2]], line='none', label=False)]}],
              icons=['lim', 'vater'], note='Snor gjennom røyra først.')
bjelke = steg('Bjelke', [{'view': 'bak', 'scene': c('kh180') + [ny('kv180', [-45, 0, 0])]}], icons=['lim'], note='To filamentpinnar i skøyten.')
lakk = steg('Lakk', [{'view': 'iso', 'labels': False, 'scene': c(*stativ) + [{'part': n, 'role': 'exploded', 'explode': [-190, 0, 0]} for n in ('kv0', 'kh0', 'lv0', 'lh0', 'ende0')]}],
            n=False, icons=['spray', 'klokke'], note='Teip 09, spalta og boringa.')
sko = steg('Sko og lys', [{'view': 'bak', 'scene': benk + [ny('sko180', [0, 22, 26]), ny('led180', [0, 14, 44])],
                           'detail': {'centre': midt('13@180'), 'span': 26, 'pos': 'right', 'r': 58,
                                      'scene': benk + [ny('sko180', [0, 9, 10])]}}])
rute = steg('Rute', [{'view': 'bak', 'scene': benk + c('led180', 'sko180') + [ny('ark180', [0, 0, 45]), ny('rute180', [0, 0, 90])], 'glas': [[-60.0, 150.0, 350.0]]}],
            note='08 først. Rillene på tvers.')
lok = steg('Lok', [{'view': 'bak', 'scene': benk + c('led180', 'sko180', 'ark180', 'rute180') + [
    ny('lv180', [0, 0, 40]), ny('lh180', [0, 0, 40]), ny('E', [0, 0, 85], at=POS['E_benk']), ny('ende180', [-40, 0, 0])],
    'detail': {'centre': [e5[0], e5[1], e5[2] + 4.0], 'span': 24, 'pos': 'right', 'r': 58,
               'scene': benk + c('led180', 'sko180', 'ark180', 'rute180', 'lv180', 'lh180') + [ny('E', [0, 0, 16], at=[e5])]}}])
paa = steg('Bjelken på røyret', [{'view': 'iso', 'labels': False, 'scene': c(*stativ) + [ny('kh0', [-190, 0, 0])] + [ny(n, [-190, 0, 0], line='none') for n in blad(0, ('kh',)) + ['elok0']]}])
laasing = steg('Lås og brems', [{'view': 'under', 'scene': c(*stativ, *blad(28), 'elok28') + [ny('Elaas', [0, 16.4, -30.9]), ny('Gbrems', [0, 0, -35])],
                                 'detail': {'centre': laas, 'span': 34, 'pos': 'left', 'r': 72}}],
               icons=['klokke'], note='Stram G til ruta står. Stram igjen etter eit døgn.')
kopling = steg('Kopling', [{'view': 'under', 'zoom': 1.2, 'scene': c('fot', 'ballast') + [ny('W', [0, 0, -30], at=[[19.0, 47.0, 7.0], [33.0, 47.0, 7.0]]),
                                                                                                    ny('botnlok', [0, 0, -60]), ny('F', [0, 0, -105], at=POS['F'])],
                            'detail': {'centre': [26.0, 47.0, 7.0], 'span': 26, 'pos': 'left', 'r': 58,
                                       'scene': c('fot', 'ballast') + [ny('W', [0, 0, -6], at=[[19.0, 47.0, 7.0], [33.0, 47.0, 7.0]])]}}])
knott = steg('Knottar', [{'view': 'under', 'zoom': 1.2, 'scene': c('fot', 'botnlok') + [ny('K', [0, 0, -30], at=knottar)]}])
ferdig = steg('Kontroll', [{'view': 'iso', 'scene': heil(0)}, {'view': 'iso', 'scene': heil(80)}], n=False, flow='right', icons=['ok'])

pages = [
    {'type': 'cover', 'title': 'RUTA', 'view': 'iso', 'scene': heil(35), 'glas': [[-60.0, -90.0, 215.0]]},
    {'type': 'inventory', 'cols': 3, 'parts': ['fot', 'botnlok', 'ring', 'stamme', 'aksel', 'boge', 'kv35', 'kh35', 'sko35', 'lv35', 'lh35', 'ende35', 'rute35', 'ark35', 'led35']},
    {'type': 'hardware', 'parts': ['E', 'F', 'G', 'S', 'W', 'K'], 'cols': 3, 'row_height': 320},
    par(kapping, skiver),
    par(boge, stamme, split=0.4),
    par(bjelke, lakk, split=0.45),
    par(sko, rute, split=0.45),
    par(lok, paa, split=0.45),
    par(laasing, kopling, split=0.55),
    par(knott, ferdig),
]

spec = {
    'meta': {'title': 'RUTA', 'footer': 'Ruta på fot · revisjon C · M04', 'orientation': 'portrait'},
    'style': {'line_pt': 0.7, 'kontur': 1.5, 'svarting': 1.5, 'steg_pt': 32, 'mengd_pt': 18, 'mengd_fyrst': True, 'tittel_pt': 96, 'tittel_feit': True, 'sidetal_pt': 9, 'del_pt': 7.5,
              'lett_pt': 0.5, 'ramme': False, 'beslagkolonne': False},
    'views': {'iso': {'dir': [0.75, -1.0, 0.6], 'up': [0, 0, 1]}, 'under': {'dir': [0.75, -1.0, -0.8], 'up': [0, 0, 1]},
              'bak': {'dir': [0.6, 1.0, 0.75], 'up': [0, 0, 1]}},
    'parts': parts,
    'pages': pages,
}
json.dump(spec, open(os.path.join(HER, 'spesifikasjon.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('spesifikasjon.json: %d sider, %d delar' % (len(pages), len(parts)))
