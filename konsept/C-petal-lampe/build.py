import cadquery as cq
import math, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "step"
STL = HERE / "stl"
OUT.mkdir(exist_ok=True)
STL.mkdir(exist_ok=True)

P = {
    "concept": "C",
    "version": "R02",
    "source": "user reference image; proportions estimated, no measured source dimensions",
    "overall_height": 220.0,
    "diameter_target": 132.0,
    "base_diameter": 74.0,
    "base_height": 16.0,
    "rib_count": 8,
    "rib_thickness": 2.5,
    "petal_span_mid_deg": 35.0,
    "petal_span_end_deg": 21.0,
    "petal_z_start": 16.3,
    "petal_z_end": 220.0,
    "diffuser_od": 42.0,
    "diffuser_wall": 1.5,
    "diffuser_start": 13.3,
    "diffuser_end": 215.0,
    "center_led_bar_mm": 12.0,
    "led_strip_width_mm": 8.0,
    "led_strip_length_mm": 150.0,
    "petal_base_socket_clearance_mm": 0.30,
    "steel_ballast_diameter_mm": 66.0,
    "steel_ballast_thickness_mm": 3.0,
    "nominal_voltage_VDC": 24.0,
    "prototype_only": True,
    "xy_photo_scale": .915,
}

def polar(radius, angle, z):
    return cq.Vector(radius * math.cos(angle), radius * math.sin(angle), z)

def fin_profile(z, thick=P["rib_thickness"]):
    t = (z - P["petal_z_start"]) / (P["petal_z_end"] - P["petal_z_start"])
    q = math.sin(math.pi * t)
    radius = 28.5 + 36.0 * q ** .84 - 6.0 * t ** 6
    angle = math.radians(P["petal_span_end_deg"] + (P["petal_span_mid_deg"] - P["petal_span_end_deg"]) * q ** .32)
    twist = math.radians(1.4 * math.sin(2 * math.pi * t))
    outer = []
    inner = []
    for i in range(13):
        v = -1 + i / 6
        theta = (angle / 2) * v + twist
        r = radius + 1.8 * (1-v*v) - .8*v
        outer.append(polar(r, theta, z))
        inner.append(polar(r-thick, theta, z))
    edges = [cq.Edge.makeSpline(outer), cq.Edge.makeLine(outer[-1], inner[-1]),cq.Edge.makeSpline(inner[::-1]),cq.Edge.makeLine(inner[0],outer[0])]
    return cq.Wire.assembleEdges(edges)

def blade():
    zs=[P["petal_z_start"]+(P["petal_z_end"]-P["petal_z_start"])*k/28 for k in range(29)]
    body=cq.Solid.makeLoft([fin_profile(z) for z in zs],ruled=False)
    tongue = cq.Workplane("XY").box(8.0,8.8,14.5).translate((27.5,0,16.75)).val()
    body=body.fuse(tongue)
    body=body.cut(cq.Solid.makeCylinder(1.3,7.5,cq.Vector(27.5,0,9.48),cq.Vector(0,0,1)))
    return body

def base():
    body=cq.Workplane("XY").circle(37).extrude(11.8).translate((0,0,4.2))
    body=body.cut(cq.Workplane("XY").circle(1.85).extrude(7.5).translate((0,0,4.1)))
    body=body.cut(cq.Workplane("XY").rect(13.6,13.6).extrude(4.8).translate((0,0,11.4)))
    body=body.cut(cq.Workplane("XY").center(13,0).circle(2.4).extrude(12).translate((0,0,4.1)))
    body=body.cut(cq.Workplane("XY").circle(21.4).circle(18.9).extrude(3.1).translate((0,0,13)))
    clearance=P["petal_base_socket_clearance_mm"]
    for k in range(8):
        slot=cq.Workplane("XY").box(8+2*clearance,8.8+2*clearance,6.9,centered=(True,True,False)).translate((27.5,0,9.2)).rotate((0,0,0),(0,0,1),k*45+22.5)
        body=body.cut(slot)
        a=math.radians(k*45+22.5)
        body=body.cut(cq.Solid.makeCylinder(1.7,5.4,cq.Vector(27.5*math.cos(a),27.5*math.sin(a),4.1)))
    body=body.cut(cq.Solid.makeCylinder(2.4,10,cq.Vector(-37.5,0,9.3),cq.Vector(1,0,0)))
    return body.val()

def bottom():
    s=cq.Workplane("XY").circle(37).extrude(1.2)
    for k in range(8):
        a=math.radians(k*45+22.5)
        s=s.cut(cq.Workplane("XY").center(27.5*math.cos(a),27.5*math.sin(a)).circle(1.75).extrude(1.21))
    s=s.cut(cq.Workplane("XY").circle(10).extrude(1.3))
    return s.val()

def ballast():
    s=cq.Workplane("XY").circle(33).circle(10).extrude(3).translate((0,0,1.2))
    for k in range(8):
        a=math.radians(k*45+22.5)
        s=s.cut(cq.Workplane("XY").center(27.5*math.cos(a),27.5*math.sin(a)).circle(3.6).extrude(3.1).translate((0,0,1.15)))
    return s.val()

def diffuser():
    outer=P['diffuser_od']/2
    return cq.Workplane('XY').circle(outer).circle(outer-P['diffuser_wall']).extrude(P['diffuser_end']-P['diffuser_start']).translate((0,0,P['diffuser_start'])).val()

def diffuser_cap():
    cap=cq.Workplane('XY').circle(17.6).extrude(2).translate((0,0,215))
    stem=cq.Workplane('XY').circle(19.35).circle(18).extrude(3).translate((0,0,212))
    return cap.union(stem).val()

def collar_slot(k):
    z=216.0
    t=(z-P['petal_z_start'])/(P['petal_z_end']-P['petal_z_start'])
    width=P['petal_span_end_deg'] + (P['petal_span_mid_deg']-P['petal_span_end_deg'])*math.sin(math.pi*t)**.32
    points=[]
    for r,angles in [(22.0,[i for i in range(-7,8)]),(29,[i for i in range(7,-8,-1)])]:
        for i in angles:
            a=math.radians(k*45+22.5 + i*(width/14 + .5))
            points.append((r*math.cos(a),r*math.sin(a)))
    return cq.Workplane('XY').polyline(points).close().extrude(4).translate((0,0,214.6))

def collar():
    s=cq.Workplane('XY').circle(28.6).circle(18.0).extrude(2.8).translate((0,0,215.2))
    for k in range(8): s=s.cut(collar_slot(k))
    return s.val()

def aluminum():
    body=cq.Workplane('XY').rect(12,12).extrude(180).translate((0,0,11.8))
    body=body.cut(cq.Workplane('XY').circle(1.25).extrude(9).translate((0,0,11.7)))
    return body.val()

def led_dummy():
    return cq.Workplane('XY').box(.4,8,150).translate((6.2,0,110)).val()

def rotate(s,angle):
    return s.rotate((0,0,0),(0,0,1),angle)

parts={
 'C01_RIB_PETG':blade(),
 'C02_BASE_PETG':base(),
 'C03_BOTTOM_PETG':bottom(),
 'C04_BALLAST_STEEL':ballast(),
 'C05_DIFFUSER_OPAL_PC':diffuser(),
 'C06_DIFFUSER_CAP':diffuser_cap(),
 'C07_UPPER_COLLAR':collar(),
 'C08_LED_CORE_ALUMINUM':aluminum(),
 'C09_LED_STRIP_PLACEHOLDER':led_dummy(),
}
def xy_scale(shape, factor):
    matrix=cq.Matrix([[factor,0,0,0],[0,factor,0,0],[0,0,1,0],[0,0,0,1]])
    return shape.transformGeometry(matrix)

for name in parts:
    if name not in ('C08_LED_CORE_ALUMINUM','C09_LED_STRIP_PLACEHOLDER'):
        parts[name]=xy_scale(parts[name],P['xy_photo_scale'])

assembly=cq.Assembly(name='CONCEPT_C_REFERENCE_MATCH_R02')
assembly.add(parts['C02_BASE_PETG'],name='BASE',color=cq.Color(.56,.51,.44))
assembly.add(parts['C03_BOTTOM_PETG'],name='BOTTOM',color=cq.Color(.55,.50,.44))
assembly.add(parts['C04_BALLAST_STEEL'],name='BALLAST',color=cq.Color(.30,.30,.30))
assembly.add(parts['C05_DIFFUSER_OPAL_PC'],name='DIFFUSER',color=cq.Color(.99,.85,.60,.60))
assembly.add(parts['C06_DIFFUSER_CAP'],name='TOP_CAP',color=cq.Color(.62,.55,.46))
assembly.add(parts['C07_UPPER_COLLAR'],name='RIB_GUIDE_TOP',color=cq.Color(.48,.44,.39))
assembly.add(parts['C08_LED_CORE_ALUMINUM'],name='LED_HEATSINK',color=cq.Color(.3,.32,.33))
for k in range(8):
    assembly.add(rotate(parts['C01_RIB_PETG'],k*45+22.5),name=f'RIB_{k+1:02}',color=cq.Color(.69,.66,.60))
for k in range(4):
    assembly.add(rotate(parts['C09_LED_STRIP_PLACEHOLDER'],k*90),name=f'LED_DUMMY_{k+1:02}',color=cq.Color(.97,.84,.58))
for name,part in parts.items():
    if not part.isValid(): raise ValueError(f'Invalid solid {name}')
    cq.exporters.export(part,str(OUT/(name+'.step')))
    if name not in ['C04_BALLAST_STEEL','C08_LED_CORE_ALUMINUM','C09_LED_STRIP_PLACEHOLDER']:
        cq.exporters.export(part,str(STL/(name+'.stl')),tolerance=.06,angularTolerance=.12)
assembly.save(str(OUT/'CONCEPT_C_ASSEMBLY_R02.step'))
(HERE/'dimensions.json').write_text(json.dumps(P,indent=2))
print('STEP AND STL OK')
for n,p in parts.items():
    bb=p.BoundingBox()
    print(f'{n}: valid={p.isValid()} V={p.Volume():.1f} mm3 W={bb.xlen:.1f} D={bb.ylen:.1f} H={bb.zlen:.1f}')
