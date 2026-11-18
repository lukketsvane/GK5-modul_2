from pathlib import Path
p=Path(__file__).resolve().parent
dst=p/"smooth-hull"
s=(p/"build_contour.py").read_text(encoding="utf-8")
first=s.index("def blade(i,sign):")
last=s.index("def moving_scoop(i):",first)
s=s[:first]+'''def smooth_hull():
    sections=[]
    for j in range(121):
        x=-190.0+j*380.0/120.0
        top,bottom=read_hull(x)
        bow=6.0*(1-(x/191.0)**2)
        yy=5.0+bow
        w=.6
        corners=[cq.Vector(x,yy-w/2,bottom),cq.Vector(x,yy-w/2,top),
                 cq.Vector(x,yy+w/2,top),cq.Vector(x,yy+w/2,bottom)]
        sections.append(cq.Wire.makePolygon(corners+[corners[0]]))
    return cq.Solid.makeLoft(sections,ruled=True)

'''+s[last:]
a='''for i in range(-4,5):
    for sign in (-1,1):
        STATION_PARTS[f"blade_{i}_{sign}"]=blade(i,sign)
    STATION_PARTS[f"scoop_{i}"]=moving_scoop(i)'''
b='''STATION_PARTS["smooth_hull"]=smooth_hull()
for i in range(-4,5):
    STATION_PARTS[f"scoop_{i}"]=moving_scoop(i)'''
assert a in s
s=s.replace(a,b)
a='''        add(f"blade_{i}_{sign}","fixed",f"station_{i}_blade_{sign}",x,sign*8*lane,HEIGHT)'''
assert a in s
s=s.replace(a,'')
s=s.replace('''add("front_guard","fixed","visible_steel_rail",color="frame")''','''add("front_guard","fixed","visible_steel_rail",color="frame")
add("smooth_hull","fixed","continuous_silver_body",color="matte")''')
s=s.replace("cq.Vector(-188,-82.0,111.0)","cq.Vector(-188,-104.0,111.0)")
s=s.replace('''        if sign==-1:
            add("hinge_cap","leaf",f"hinge_cap_{i}",x,sign*16*lane,HEIGHT,color="metal")''','''        if sign==-1:
            add("hinge_cap","fixed",f"hinge_cap_{i}",x,0,HEIGHT,color="metal")''')
s=s.replace('''return cq.Solid.makeCylinder(3.6,1.4,cq.Vector(0,-36.0,0),cq.Vector(0,-1,0))''','''return cq.Solid.makeCylinder(3.6,1.4,cq.Vector(0,-106.0,0),cq.Vector(0,-1,0))''')
s=s.replace("    \"kinematics\":{","    \"kinematics\":{")
(dst/"build_smooth.py").write_text(s,encoding="utf-8")
r=(p/"render_match.py").read_text(encoding="utf-8")
replacements={
'make_material("Satin silver aluminum", (0.39, 0.40, 0.41), 0.83, 0.30)':'make_material("Satin silver aluminum", (0.26, 0.28, 0.30), 0.82, 0.28)',
'0.90, 0.35, 8.0':'0.90, 0.35, 6.0',
'0.52, 0.25, 8.0':'0.52, 0.25, 10.0'
}
for a,b in replacements.items():
 if a in r:r=r.replace(a,b)
(dst/"render_smooth.py").write_text(r,encoding="utf-8")
(dst/"compare_silhouette.py").write_text((p/"compare_silhouette.py").read_text(encoding="utf-8"),encoding="utf-8")
(dst/"astra_scoop.py").write_text((p/"astra_scoop.py").read_text(encoding="utf-8"),encoding="utf-8")
print("new smooth hull with overlapping animated Astra scoops and continuous rod",len(s),flush=True)
