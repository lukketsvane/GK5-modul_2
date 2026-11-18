from pathlib import Path
p=Path(__file__).resolve().parent/"build.py"
s=p.read_text(encoding="utf-8")
a='rise = z * z / (radius + math.sqrt(max(0.0, radius * radius - z * z)))\n        y = sign * (24.0 + rise)'
b='''rise = z * z / (radius + math.sqrt(max(0.0, radius * radius - z * z)))
        t = max(0.0, min(1.0, (abs(z)-8.0)/20.0))
        rise += 17.0*t*t*(3.0-2.0*t)
        y = sign * (24.0 + rise)'''
assert a in s
s=s.replace(a,b)
a='half=26.0+14.0*lane'
assert a in s
s=s.replace(a,'half=26.0+11.0*lane')
a='sign*14*lane'
assert s.count(a)==4
s=s.replace(a,'sign*11*lane')
assert 'HEIGHT,14.0)' in s
s=s.replace('HEIGHT,14.0)','HEIGHT,11.0)')
start=s.index("def rail(sign):")
end=s.index("def bar(x):",start)
rail='''def rail(sign):
    c=cq.Workplane("XY").box(376.0,4.0,4.0).translate((0,sign*10.0,HEIGHT)).val()
    tube=cq.Solid.makeCylinder(3.0,376.0,cq.Vector(-188.0,sign*14.0,HEIGHT),cq.Vector(1,0,0))
    c=c.fuse(tube)
    for x in CENTRES:
        boss=cq.Solid.makeCylinder(7.8,4.0,cq.Vector(x,sign*8.0,HEIGHT),cq.Vector(0,sign,0))
        c=c.fuse(boss)
    for x in CENTRES:
        bore=cq.Solid.makeCylinder(5.1,6.0,cq.Vector(x,sign*7,HEIGHT),cq.Vector(0,sign,0))
        c=c.cut(bore)
    return c

'''
s=s[:start]+rail+s[end:]
assert 'HEIGHT-5.5' in s
s=s.replace('HEIGHT-5.5','HEIGHT-2.0')
assert 'min_clearance=14.0-SHEET' in s
s=s.replace('min_clearance=14.0-SHEET','min_clearance=11.0-SHEET')
s=s.replace('neighbor_shoe_gap=14.0+19.0-24.0-SHEET/2-6.5','neighbor_shoe_gap=11.0+19.0-24.0-SHEET/2')
s=s.replace('assert min_clearance>12.0 and neighbor_shoe_gap>1.5','assert min_clearance>9.0 and neighbor_shoe_gap>1.5')
(p.parent/"build_before_spine_redesign.py").write_text(p.read_text(encoding="utf-8"),encoding="utf-8")
p.write_text(s,encoding="utf-8")
r=p.parent/"render_blender.py"
t=r.read_text(encoding="utf-8")
t=t.replace('0.46, 0.19, 1.25','0.46, 0.19, 3.5')
r.write_text(t,encoding="utf-8")
print("ASTRA-REVIEWED SPINE AND BENT-SKIN MODIFICATIONS",flush=True)
