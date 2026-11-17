from pathlib import Path
import json
import cadquery as cq
from cadquery import exporters
import ezdxf
import ruta_c as R

OUT = Path(__file__).resolve().parent / 'ut-c' / 'kort-topp'
OUT.mkdir(parents=True, exist_ok=True)

CUT = R.X_DEL_K + 20.0
WIDTH = R.XR1 - CUT
DEPTH = R.RUTE_D
HOLES = [round(x - CUT, 3) for x in R.SKRUAR_X if CUT < x < R.XR1]
HOLE_Y = R.U_SKRUE - R.U_KANT
assert len(HOLES) == 3 and HOLES[0] >= 12.0 and WIDTH - HOLES[-1] >= 12.0
assert R.X1 - CUT == 177.0 and WIDTH == 163.0

def place(form, upright=False):
    if upright:
        form = form.rotate((0, 0, 0), (0, 1, 0), 90)
    bb = form.val().BoundingBox()
    return form.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))

B = R._bjelke_lokal()
parts = {
    '05_behald_bjelke_177mm_berre_ved_nyprint': place(R._del_x(B['kropp'], CUT, R.X1 + 1), True),
    '06_nytt_samanhengande_lok_164mm': place(R._del_x(B['lokk'], CUT, R.X1 + 1)),
    '11_endeplate_36mm': cq.Workplane('XY').circle(17.9).extrude(2.0),
}
for name, solid in parts.items():
    assert solid.val().isValid() and solid.val().Volume() > 0
    bb = solid.val().BoundingBox()
    assert max(bb.xlen, bb.ylen, bb.zlen) <= 250
    exporters.export(solid, str(OUT / (name + '.stl')), 'STL', tolerance=0.025, angularTolerance=0.1)
    print(name, tuple(round(v, 1) for v in (bb.xlen, bb.ylen, bb.zlen)))

def make_dxf(filename, depth):
    doc = ezdxf.new('R2010')
    doc.units = ezdxf.units.MM
    doc.layers.new('CUT')
    m = doc.modelspace()
    r = 8.0
    attr = {'layer': 'CUT'}
    for a, b in [
        ((0, 0), (WIDTH, 0)),
        ((WIDTH, 0), (WIDTH, depth-r)),
        ((WIDTH-r, depth), (r, depth)),
        ((0, depth-r), (0, 0)),
    ]:
        m.add_line(a, b, dxfattribs=attr)
    m.add_arc((WIDTH-r, depth-r), r, 0, 90, dxfattribs=attr)
    m.add_arc((r, depth-r), r, 90, 180, dxfattribs=attr)
    for x in HOLES:
        m.add_circle((x, HOLE_Y), 2.0, dxfattribs=attr)
    doc.saveas(OUT / filename)

def make_svg(filename, depth):
    w = WIDTH
    r = 8.0
    outline = f'M 0 0 L {w} 0 L {w} {depth-r} A {r} {r} 0 0 1 {w-r} {depth} L {r} {depth} A {r} {r} 0 0 1 0 {depth-r} Z'
    holes = ''.join(f'<circle cx="{x}" cy="{HOLE_Y}" r="2"/>' for x in HOLES)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{depth}mm" viewBox="0 0 {w} {depth}"><g fill="none" stroke="#000" stroke-width=".1">{chr(10)}<path d="{outline}"/>{holes}</g></svg>'
    (OUT / filename).write_text(svg, encoding='utf-8')

make_dxf('lysleiar_163x190_mm_PMMA_SJEKK_MATERIALE.dxf', DEPTH)
make_svg('lysleiar_163x190_mm.svg', DEPTH)
make_svg('prismefilm_163x184_mm_KLIPP_IKKJE_LASER.svg', DEPTH - 6.0)

data = {
    'original_topp_mm': R.X1 - R.X0,
    'fjern_heile_lause_forlenginga_mm': R.X_DEL_K - R.X0,
    'sag_fra_skjoyten_pa_behalden_del_mm': 20,
    'samla_fjerna_mm': CUT - R.X0,
    'topp_etter_kapping_mm': R.X1 - CUT,
    'lysskjerm_breidd_mm': WIDTH,
    'lysskjerm_djupn_mm': DEPTH,
    'prismefilm_djupn_mm': DEPTH - 6.0,
    'tre_skruehol_diameter_mm': 4.0,
    'skruehol_x_fra_ny_ende_mm': HOLES,
    'skruehol_y_fra_innspent_kant_mm': HOLE_Y,
    'min_avstand_skruesenter_til_ender_mm': min(HOLES[0], WIDTH-HOLES[-1]),
    'led_omtrent_maks_mm': WIDTH - 30,
}
(OUT / 'maal_og_kontroll.json').write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(data, ensure_ascii=False))
