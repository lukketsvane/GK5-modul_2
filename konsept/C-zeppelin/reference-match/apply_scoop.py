from pathlib import Path
p=Path(__file__).resolve().parent
a=p/"astra_scoop.py"
code=a.read_text(encoding="utf-8")
for before,after in [
 ("r = min(2.6, 0.08 * L, 0.25 * (up + down))","r = min(5.0, 0.09 * L, 0.25 * (up + down))"),
 ("y0 = side * 1.2 * layer","y0 = side * (12.0 + 1.2 * layer)"),
 ("0.46 * r","2.72")
]:
 assert before in code,before
 code=code.replace(before,after)
a.write_text(code,encoding="utf-8")
f=p/"build_match.py"
s=f.read_text(encoding="utf-8")
assert "from astra_louver import make_louver" in s
s=s.replace("from astra_louver import make_louver","from astra_scoop import make_scoop")
s=s.replace('def blade(kind,sign):\n    return make_louver(WING_WIDTH[kind],HALF_CHORD[kind],[40,35,28,16,5][kind],sign,0).translate((0,12.0*sign,0))',
'''def blade(kind,sign,direction):
    return make_scoop(WING_WIDTH[kind],HALF_CHORD[kind],[40,35,28,16,5][kind],sign,0,direction)

def endcap(side):
    wire_list=[]
    for j in range(13):
        t=.001+(j/12)*.998
        x=side*(193.0-30.0*t)
        rad_z=max(.4,13.0*math.sin(.5*math.pi*t))
        rad_y=max(.4,18.0*math.sin(.5*math.pi*t))
        pts=[cq.Vector(x,rad_y*math.cos(k*2*math.pi/16),HEIGHT+rad_z*math.sin(k*2*math.pi/16)) for k in range(16)]
        wire_list.append(cq.Wire.makePolygon(pts+[pts[0]]))
    return cq.Solid.makeLoft(wire_list,ruled=True)
''')
old='''for kind in range(5):
    for sign in (-1,1):
        STATION_PARTS[f"blade_{kind}_{sign}"]=blade(kind,sign)'''
new='''for kind in range(5):
    for sign in (-1,1):
        for direction in (-1,1):
            STATION_PARTS[f"blade_{kind}_{sign}_{direction}"]=blade(kind,sign,direction)'''
assert old in s
s=s.replace(old,new)
s=s.replace('    "front_guard":front_guard(),"opal_strip":opal_strip(),"button":button(), "hinge_cap":hinge_cap(),',
'''    "front_guard":front_guard(),"opal_strip":opal_strip(),"button":button(), "hinge_cap":hinge_cap(),
    "nose_left":endcap(-1),"nose_right":endcap(1),''')
assert 'add("front_guard","fixed","visible_steel_rail",color="frame")' in s
s=s.replace('add("front_guard","fixed","visible_steel_rail",color="frame")',
'''add("front_guard","fixed","visible_steel_rail",color="frame")
add("nose_left","fixed","left_blunt_tip",color="matte")
add("nose_right","fixed","right_blunt_tip",color="matte")''')
old='''        add(f"blade_{kind}_{sign}","leaf",f"station_{i}_blade_{sign}",x,sign*16*lane,HEIGHT)'''
new='''        direction = (1 if i<0 else -1 if i>0 else 1 if sign==-1 else -1)
        add(f"blade_{kind}_{sign}_{direction}","leaf",f"station_{i}_blade_{sign}",x,sign*16*lane,HEIGHT)'''
assert old in s
s=s.replace(old,new)
assert 'for angle,name in ((CLOSED,"reference")' in s
f.write_text(s,encoding="utf-8")
print("scoop symmetry broken by physically modeled asymmetrically anchored CAD metal sheets",flush=True)
