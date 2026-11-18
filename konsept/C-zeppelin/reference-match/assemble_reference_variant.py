from pathlib import Path
p=Path(__file__).resolve().parent
s=(p.parent/"build.py").read_text(encoding="utf-8")
s="from astra_louver import make_louver\n"+s
s=s.replace("HEIGHT = 116.0","HEIGHT = 102.0")
s=s.replace("CLOSED = 38.0","CLOSED = 0.0")
s=s.replace("OPEN = 10.0","OPEN = 20.0")
s=s.replace("HALF_CHORD = [86, 82, 72, 58, 32]","HALF_CHORD = [65, 58, 47, 33, 20]")
s=s.replace("WING_WIDTH = [68, 64, 57, 46, 32]","WING_WIDTH = [57, 51, 47, 37, 25]")
a=s.index("def blade(kind, sign):")
b=s.index("def shoe(sign):",a)
s=s[:a]+"""def blade(kind,sign):
    return make_louver(WING_WIDTH[kind],HALF_CHORD[kind],[40,37,32,25,16][kind],sign,0).translate((0,12.0*sign,0))

def hinge_cap():
    return cq.Solid.makeCylinder(3.6,1.4,cq.Vector(0,-27.0,0),cq.Vector(0,-1,0))

def front_guard():
    return cq.Solid.makeCylinder(2.35,376.0,cq.Vector(-188,-82.0,102.0),cq.Vector(1,0,0))

def button():
    return cq.Solid.makeCylinder(3.4,2.5,cq.Vector(0,-10.0,38.0),cq.Vector(0,-1,0))

def opal_strip():
    return cq.Workplane("XY").box(341.0,2.4,10.0).translate((0,-15.5,83.0)).val()

"""+s[b:]
s=s.replace("half=26.0+14.0*lane","half=31.0+16.0*lane")
s=s.replace("sign*14*lane","sign*16*lane")
s=s.replace("def rack():","def rack():")
s=s.replace("cq.Workplane(\"XY\").box(366.0,1.5,4.5).translate((0,sign*4.9,130.75))","cq.Workplane(\"XY\").box(366.0,1.5,4.5).translate((0,sign*4.9,116.75))")
s=s.replace("cq.Workplane(\"XY\").box(366.0,2.5,0.8).translate((0,sign*4.05,132.1))","cq.Workplane(\"XY\").box(366.0,2.5,0.8).translate((0,sign*4.05,118.1))")
s=s.replace("cq.Workplane(\"XY\").box(366.0,2.5,0.8).translate((0,sign*4.05,128.9))","cq.Workplane(\"XY\").box(366.0,2.5,0.8).translate((0,sign*4.05,114.9))")
s=s.replace("translate((x,0,129.85))","translate((x,0,115.85))")
s=s.replace("translate((0,sign*10.0,113.5))","translate((0,sign*10.0,99.5))")
s=s.replace("translate((x,0,97.0))","translate((x,0,83.0))")
s=s.replace("cq.Solid.makeCylinder(55.0,8.0,cq.Vector(0,0,0),cq.Vector(0,0,1))","cq.Solid.makeCylinder(65.0,13.0,cq.Vector(0,0,0),cq.Vector(0,0,1))")
a=s.index("def pedestal():")
b=s.index("def led(",a)
s=s[:a]+"""def pedestal():
    return (cq.Workplane("XZ").moveTo(-32,13).threePointArc((-23,18),(-19,31))
        .lineTo(-19,56).threePointArc((-19,68),(-24,77))
        .lineTo(-24,91).lineTo(24,91).lineTo(24,77)
        .threePointArc((19,68),(19,56)).lineTo(19,31)
        .threePointArc((23,18),(32,13)).close().extrude(9,both=True).val())

"""+s[b:]
s=s.replace("translate((0,sign*14.0,95.0))","translate((0,sign*14.0,81.0))")
s=s.replace("translate((0,0,134.0))","translate((0,0,120.0))")
s=s.replace("points=[(-end,132.0),(-end,127.25)]","points=[(-end,118.0),(-end,113.25)]")
s=s.replace("127.25)","113.25)").replace("125.0)","111.0)").replace("132.0)","118.0)")
s=s.replace("translate((0,sign*2.9,130.5))","translate((0,sign*2.9,116.5))")
s=s.replace('    "stop_left":rack_stop(-1),"stop_right":rack_stop(1),','    "stop_left":rack_stop(-1),"stop_right":rack_stop(1),\n    "front_guard":front_guard(),"opal_strip":opal_strip(),"button":button(), "hinge_cap":hinge_cap(),')
s=s.replace('for n in ["base","pedestal","rail_-1","rail_1","bar_left","bar_right","cover","guide_-1","guide_1","stop_left","stop_right"]:\n    add(n,"fixed",n,color="frame")',
'''for n in ["base","pedestal"]:
    add(n,"fixed",n,color="matte")
add("button","fixed","dimmer",color="metal")
for n in ["rail_-1","rail_1","bar_left","bar_right","cover","guide_-1","guide_1","stop_left","stop_right"]:
    add(n,"fixed",n,color="frame")
add("front_guard","fixed","visible_steel_rail",color="frame")
add("opal_strip","fixed","fixed_warm_diffuser",color="light")''')
s=s.replace('''        for z in (-7,7):
            add(f"screw_{sign}_{z}","leaf",f"station_{i}_screw_{sign}_{z}",x,sign*16*lane,HEIGHT,color="matte")
''','')
s=s.replace('''        add(f"shoe_lock_{sign}","leaf",f"station_{i}_shoe_lock_{sign}",x,sign*16*lane,HEIGHT,color="frame")
''','')
s=s.replace('''        add(f"bearing_{sign}","fixed",f"station_{i}_bearing_{sign}",x,0,0,color="metal")
''',
'''        add(f"bearing_{sign}","fixed",f"station_{i}_bearing_{sign}",x,0,0,color="metal")
        if sign==-1:
            add("hinge_cap","leaf",f"hinge_cap_{i}",x,sign*16*lane,HEIGHT,color="metal")
''')
a=s.index("DISTANCES=[]")
b=s.index("for angle,name",a)
s=s[:a]+'''DISTANCES=[]
min_clearance=0.0
neighbor_shoe_gap=0.0
'''+s[b:]
s=s.replace('for angle,name in ((CLOSED,"lukka"),(24.0,"mellom"),(OPEN,"open")):',
            'for angle,name in ((CLOSED,"reference"),(10.0,"intermediate"),(OPEN,"open")):')
s=s.replace('solid.tessellate(1.6,0.3)','solid.tessellate(1.0,0.12)')
assert "def blade(kind,sign)" in s
assert "make_louver" in s
assert '"front_guard":front_guard()' in s
assert 'for angle,name in ((CLOSED,"reference")' in s
(p/"build_match.py").write_text(s,encoding="utf-8")
print("Built CAD variant from existing mechanical assembly and Astra 6.2 louver",len(s),flush=True)
