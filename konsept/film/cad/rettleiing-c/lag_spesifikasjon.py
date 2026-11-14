# -*- coding: utf-8 -*-
"""
lag_spesifikasjon.py  ·  skriv spesifikasjon.json til verktoy/ikea/bygg.py (formnerd) frå geometrien i ../ut-c/

  python3 lag_delar.py
  python3 lag_spesifikasjon.py
  python3 <formnerd>/verktoy/ikea/bygg.py spesifikasjon.json ut
"""
import json, math, os

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
         'aksel': mesh('09', '09'), 'boge': mesh('12', '12')}
for i, n in ROERLEGE.items():
    for v in (0, 28, 35, 80, 180):
        parts['%s%d' % (n, v)] = mesh('%s@%d' % (i, v), ID.get(i, i))
for v in (0, 28, 35, 80, 180):
    parts['elok%d' % v] = mesh('Elok@%d' % v, 'E')
skruar = {x['id']: x['tal'] for x in K['stykkliste']}
parts.update({
    'E': beslag('E', skruar['E'], mesh='delar/E.stl'),
    'Elaas': beslag('E', 1, mesh='delar/Elaas@28.stl', counts_as='E'),
    'F': beslag('F', skruar['F'] + skruar['G'], mesh='delar/F.stl'),
    'Fbrems': beslag('F', 1, mesh='delar/G@28.stl', counts_as='F'),
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

stativ = ['fot', 'ballast', 'stamme', 'aksel', 'boge']
heil = lambda v: c('fot', 'botnlok', 'ballast', 'stamme', 'aksel', 'boge', *blad(v), 'elok%d' % v)
knottar = [[round(75.0 * math.cos(math.radians(22.5 * i)), 1), round(75.0 * math.sin(math.radians(22.5 * i)), 1), -1.25] for i in range(16)]
laas = [G['PINNE'][0], 18.0, 250.0]
kapp = K['kapp']

pages = [
    {'type': 'cover', 'title': 'RUTA', 'view': 'iso', 'scene': heil(35), 'glas': [[-60.0, -90.0, 215.0]]},
    {'type': 'inventory', 'parts': ['fot', 'botnlok', 'kv35', 'kh35', 'lv35', 'lh35', 'ende35', 'boge', 'sko35'], 'cols': 3},
    {'type': 'inventory', 'parts': ['stamme', 'aksel', 'rute35', 'ark35', 'led35'], 'cols': 3},
    {'type': 'hardware', 'parts': ['E', 'F', 'S', 'W', 'K']},
    {'type': 'step', 'n': False, 'title': 'Kapp', 'icons': ['atvaring'],
     'note': 'Kapp røyret i %.0f mm (04) og %.0f mm (09). Fil kantane. Slip av krommen der limet skal sitje.' % (kapp['stammeroyr_mm'], kapp['akselroyr_mm']),
     'figures': [{'view': 'iso', 'scene': c('stamme', 'aksel'), 'zoom': 1.0}]},
    {'type': 'step', 'title': 'Skiver', 'figures': [{'view': 'under', 'zoom': 1.25, 'multiplier': 'x3', 'scene': c('fot') + [ny('S', [0, 0, -45], at=POS['S'])]}]},
    {'type': 'step', 'title': 'Røyr i boge', 'icons': ['lim'], 'note': 'Skyv røyra heilt inn. La limet herde.',
     'figures': [{'view': 'iso', 'scene': c('boge') + [ny('stamme', [-70 * d[0], 0, -70 * d[2]]), ny('aksel', [-70, 0, 0])]}]},
    {'type': 'step', 'title': 'Stamme i fot', 'icons': ['lim'], 'note': 'Hald akselrøyret (09) vassrett til limet har herda.',
     'figures': [{'view': 'iso', 'scene': c('fot', 'ballast') + [ny('stamme', [70 * d[0], 0, 70 * d[2]]), ny('aksel', [70 * d[0], 0, 70 * d[2]], line='none'),
                                                                ny('boge', [70 * d[0], 0, 70 * d[2]], line='none')], 'labels': False}]},
    {'type': 'step', 'title': 'Bjelke', 'icons': ['lim'], 'note': 'Lim halvdelane saman på restrøyret. Dra røyret ut før limet herdar.',
     'figures': [{'view': 'bak', 'scene': c('kh180') + [ny('kv180', [-45, 0, 0])]}]},
    {'type': 'step', 'n': False, 'title': 'Lakk',
     'note': 'Slip lett, grunn og sprøyt. Teip akselrøyret (09), spalta og boringa. Endeloket (11) i messingfarge.',
     'figures': [{'view': 'iso', 'labels': False, 'scene': c(*stativ) + [{'part': n, 'role': 'exploded', 'explode': [-190, 0, 0]} for n in ('kv0', 'kh0', 'lv0', 'lh0', 'ende0')]}]},
    {'type': 'step', 'title': 'Sko og lys', 'note': 'Skoen (13) inn frå sida og til venstre under skruen. Så stripa (10), leidningen ut til høgre.',
     'figures': [{'view': 'bak', 'scene': c('kv180', 'kh180') + [ny('sko180', [0, 22, 26]), ny('led180', [0, 14, 44])]}]},
    {'type': 'step', 'title': 'Rute', 'note': 'Arket (08) først, prismesida ned. Rillene på tvers av bjelken.',
     'figures': [{'view': 'bak', 'scene': c('kv180', 'kh180', 'led180', 'sko180') + [ny('ark180', [0, 0, 45]), ny('rute180', [0, 0, 90])],
                  'glas': [[-60.0, 150.0, 350.0]]}]},
    {'type': 'step', 'title': 'Lok', 'figures': [{'view': 'bak', 'scene': c('kv180', 'kh180', 'led180', 'sko180', 'ark180', 'rute180') + [
        ny('lv180', [0, 0, 40]), ny('lh180', [0, 0, 40]), ny('E', [0, 0, 85], at=POS['E_benk']), ny('ende180', [-40, 0, 0])]}]},
    {'type': 'step', 'title': 'Bjelken på røyret', 'note': 'Leidningen ned gjennom røyret til foten først.',
     'figures': [{'view': 'iso', 'labels': False, 'scene': c(*stativ) + [ny('kh0', [-190, 0, 0])] + [ny(n, [-190, 0, 0], line='none') for n in blad(0, ('kh',)) + ['elok0']]}]},
    {'type': 'step', 'title': 'Lås og brems', 'note': 'Stram F til ruta står i alle stillingar, men kan flyttast med éi hand.',
     'figures': [{'view': 'under', 'scene': c(*stativ, *blad(28), 'elok28') + [ny('Elaas', [0, 16.4, -30.9]), ny('Fbrems', [0, 0, -35])],
                  'detail': {'centre': laas, 'span': 34, 'pos': 'left', 'r': 72}}]},
    {'type': 'step', 'title': 'Kopling', 'note': 'Skøyt leidningen i klemmene (W). Strips innanfor veggen som strekkavlasting.',
     'figures': [{'view': 'under', 'zoom': 1.2, 'scene': c('fot', 'ballast', 'stamme') + [ny('W', [0, 0, -30], at=[[19.0, 47.0, 7.0], [33.0, 47.0, 7.0]]),
                                                                              ny('botnlok', [0, 0, -60]), ny('F', [0, 0, -105], at=POS['F'])]}]},
    {'type': 'step', 'title': 'Knottar', 'figures': [{'view': 'under', 'zoom': 1.2, 'scene': c('fot', 'botnlok') + [ny('K', [0, 0, -30], at=knottar)]}]},
    {'type': 'step', 'n': False, 'title': 'Kontroll', 'flow': 'right', 'icons': ['ok'],
     'note': 'Ruta skal gå jamt frå 0° til 80° og stoppe i begge endar. Brytaren sit på leidningen.',
     'figures': [{'view': 'iso', 'scene': heil(0)}, {'view': 'iso', 'scene': heil(80)}]},
]

spec = {
    'meta': {'title': 'RUTA', 'footer': 'Ruta på fot · revisjon C · M02', 'orientation': 'portrait'},
    'style': {'line_pt': 0.75, 'steg_pt': 32, 'mengd_pt': 18, 'mengd_fyrst': True, 'tittel_pt': 96, 'tittel_feit': True, 'sidetal_pt': 9, 'del_pt': 7.5,
              'lett_pt': 0.5, 'ramme': False, 'beslagkolonne': False},
    'views': {'iso': {'dir': [0.75, -1.0, 0.6], 'up': [0, 0, 1]}, 'under': {'dir': [0.75, -1.0, -0.8], 'up': [0, 0, 1]},
              'bak': {'dir': [0.6, 1.0, 0.75], 'up': [0, 0, 1]}},
    'parts': parts,
    'pages': pages,
}
json.dump(spec, open(os.path.join(HER, 'spesifikasjon.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('spesifikasjon.json: %d sider, %d delar' % (len(pages), len(parts)))
