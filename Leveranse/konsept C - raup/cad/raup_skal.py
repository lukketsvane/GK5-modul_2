# -*- coding: utf-8 -*-
"""raup_skal.py · hovudforma til Raup som tjukt skal for 3D-print (P1S), utan innvendig gitter.

Les den ytre kroppen (raup_hovudkropp_ytre.step, laga av raup_produksjon.py), held ytterflata urørt
og hòlar kroppen innanfrå med jamn veggtjukkleik VEGG. Botnen er open, så kabel og LED kan inn nedanfrå.
Skriv cad/raup_skal.step og produksjon/raup_skal_P1S.stl, og kontrollerer at skalet er gyldig, tett
og får plass i 256 x 256 x 256 mm.

    py -3 cad/raup_skal.py [vegg_mm]
"""
import sys, json
from pathlib import Path
import cadquery as cq

VEGG = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0     # mm
P1S = 256.0                                                  # byggjevolum, mm

R = Path(__file__).resolve().parents[1]
CAD, UT, KONTROLL = R / 'cad', R / 'produksjon', R / 'kontroll'

kropp = cq.importers.importStep(str(CAD / 'raup_hovudkropp_ytre.step')).val()
bb = kropp.BoundingBox()
print(f'ytre kropp: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, volum {kropp.Volume()/1e3:.0f} cm3')

# Fjern botnflata (den plane flata med lågast z) og tjukn inn resten med -VEGG.
skal = cq.Workplane('XY').add(kropp).faces('<Z').shell(-VEGG).val()
if not skal.isValid():
    skal = skal.fix()
ok = skal.isValid() and skal.Volume() > 0

sb = skal.BoundingBox()
passar = all(d <= P1S for d in (sb.xlen, sb.ylen, sb.zlen))
masse_pla = skal.Volume() / 1e3 * 1.24                      # g, PLA 1,24 g/cm3

cq.exporters.export(skal, str(CAD / 'raup_skal.step'))
cq.exporters.export(skal, str(UT / 'raup_skal_P1S.stl'), tolerance=0.05, angularTolerance=0.1)

rapport = {
    'fil': 'cad/raup_skal.step, produksjon/raup_skal_P1S.stl',
    'veggtjukkleik_mm': VEGG,
    'botn': 'open',
    'gyldig_BRep': bool(ok),
    'mal_mm': [round(sb.xlen, 1), round(sb.ylen, 1), round(sb.zlen, 1)],
    'passar_P1S_256': bool(passar),
    'volum_cm3': round(skal.Volume() / 1e3, 1),
    'masse_PLA_g': round(masse_pla),
    'utskrift': 'Ståande på den opne botnen. Inga fylling: veggen er heile skalet. '
                'Set talet på veggliner så dei fyller veggen (3 mm / 0,42 mm = 7 liner), eller sparse infill 100 %.',
}
(KONTROLL / 'raup_skal.json').write_text(json.dumps(rapport, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(rapport, indent=2, ensure_ascii=False))
