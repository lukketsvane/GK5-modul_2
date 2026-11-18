from pathlib import Path
p=Path(__file__).resolve().parent
out=p/"contour"
out.mkdir(exist_ok=True)
s=(p/"build_match.py").read_text(encoding="utf-8").replace("from astra_scoop import make_scoop\n","")
a=s.index("def blade(kind,sign,direction):")
b=s.index("def hinge_cap():",a)
shape='''PROFILE=[
(150,395,395),(165,359,424),(215,314,456),(265,288,471),
(315,274,479),(365,249,491),(415,240,497),(465,218,501),
(515,206,506),(565,203,509),(615,188,512),(665,188,512),
(715,193,512),(765,200,512),(815,188,512),(865,185,508),
(915,198,505),(965,216,501),(1015,230,498),(1065,234,491),
(1115,253,483),(1165,267,477),(1215,284,467),(1265,311,457),
(1315,331,445),(1365,371,417),(1378,395,395)]
PX_MM=3.2
def read_hull(x):
    pixel_x=764.0+PX_MM*x
    for j in range(1,len(PROFILE)):
        if pixel_x<=PROFILE[j][0]:
            lo,hi=PROFILE[j-1],PROFILE[j]
            f=max(0.,min(1.,(pixel_x-lo[0])/(hi[0]-lo[0])))
            t=lo[1]+f*(hi[1]-lo[1])
            b=lo[2]+f*(hi[2]-lo[2])
            return (HEIGHT+(395-t)*0.258, HEIGHT-(b-395)*0.342)
    return HEIGHT,HEIGHT

def blade(i,sign):
    centre=i*PITCH
    halfwidth=[60,52,44,38,30][abs(i)]
    low=max(-191.,centre-halfwidth)
    high=min(191.,centre+halfwidth)
    skin=[]
    for j in range(85):
        x=low+(high-low)*(0.001+j*.998/84)
        top,bottom=read_hull(x)
        if top-bottom<1:
            top=HEIGHT+.5
            bottom=HEIGHT-.5
        u=(x-centre)/halfwidth
        fold=7.*(1-max(0.,min(1.,u*u)))
        yy=sign*(23.5+fold)
        ztop=top-HEIGHT
        zbottom=bottom-HEIGHT
        if sign>0:
            corners=[cq.Vector(x-centre,yy-.3,zbottom),cq.Vector(x-centre,yy-.3,ztop),
                     cq.Vector(x-centre,yy+.3,ztop),cq.Vector(x-centre,yy+.3,zbottom)]
        else:
            corners=[cq.Vector(x-centre,yy+.3,zbottom),cq.Vector(x-centre,yy+.3,ztop),
                     cq.Vector(x-centre,yy-.3,ztop),cq.Vector(x-centre,yy-.3,zbottom)]
        skin.append(cq.Wire.makePolygon(corners+[corners[0]]))
    shell=cq.Solid.makeLoft(skin,ruled=True)
    bore=cq.Solid.makeCylinder(2.7,100,cq.Vector(0,-50,0),cq.Vector(0,1,0))
    cut=shell.cut(bore)
    if cut.isValid() and cut.Volume()>0:
        return cut
    return shell

'''
s=s[:a]+shape+s[b:]
s=s.replace('''def hinge_cap():
    return cq.Solid.makeCylinder(3.6,1.4,cq.Vector(0,-27.0,0),cq.Vector(0,-1,0))''',
'''def hinge_cap():
    return cq.Solid.makeCylinder(3.6,1.4,cq.Vector(0,-36.0,0),cq.Vector(0,-1,0))''')
if "def endcap(" in s:
    aa=s.index("def endcap(")
    bb=s.index("def hinge_cap():",aa)
    s=s[:aa]+s[bb:]
s=s.replace('''for kind in range(5):
    for sign in (-1,1):
        for direction in (-1,1):
            STATION_PARTS[f"blade_{kind}_{sign}_{direction}"]=blade(kind,sign,direction)''',
'''for i in range(-4,5):
    for sign in (-1,1):
        STATION_PARTS[f"blade_{i}_{sign}"]=blade(i,sign)''')
s=s.replace('''    "nose_left":endcap(-1),"nose_right":endcap(1),''','')
s=s.replace('''add("nose_left","fixed","left_blunt_tip",color="matte")
add("nose_right","fixed","right_blunt_tip",color="matte")
''','')
s=s.replace('''        direction = (1 if i<0 else -1 if i>0 else 1 if sign==-1 else -1)
        add(f"blade_{kind}_{sign}_{direction}","leaf",f"station_{i}_blade_{sign}",x,sign*16*lane,HEIGHT)''',
'''        add(f"blade_{i}_{sign}","leaf",f"station_{i}_blade_{sign}",x,sign*16*lane,HEIGHT)''')
assert "PROFILE=[" in s
assert 'STATION_PARTS[f"blade_{i}_{sign}"]=blade(i,sign)' in s
assert "endcap(" not in s
(out/"build_contour.py").write_text(s,encoding="utf-8")
(out/"render_match.py").write_text((p/"render_match.py").read_text(encoding="utf-8"),encoding="utf-8")
(out/"compare_silhouette.py").write_text((p/"compare_silhouette.py").read_text(encoding="utf-8"),encoding="utf-8")
print("Prepared actual 9-piece CAD hull built from measurements of uploaded reference",flush=True)
