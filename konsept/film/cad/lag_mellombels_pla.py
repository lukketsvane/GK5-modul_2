from pathlib import Path
import sys
import cadquery as cq
from cadquery import exporters

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import ruta_c as R

OUT=ROOT/'ut-c'/'mellombels-pla'
OUT.mkdir(parents=True,exist_ok=True)

def shaft(length,socket):
    p=cq.Workplane('XY').circle(6).circle(2.5).extrude(length)
    if socket:
        recess=cq.Workplane('XY').circle(4.05).extrude(21).translate((0,0,length-21))
        p=p.cut(recess)
    else:
        peg=cq.Workplane('XY').circle(3.9).circle(2.5).extrude(20).translate((0,0,length))
        p=p.union(peg)
    return p

lower=R.STAMME_L/2
axle=R.AKSEL_L/2
shapes={
    '01_stamme_nedre':shaft(lower,True),
    '02_stamme_ovre':shaft(lower,False),
    '03_aksel_venstre':shaft(axle,True),
    '04_aksel_hogre':shaft(axle,False),
}
plane=R._bjelke_lokal()['plate']
split=R.X_DEL_L
minx,maxx=R.XR0,R.XR1
width=R.RUTE_D+3
zb=plane.val().BoundingBox()
cutleft=cq.Workplane('XY').box(split-0.15-(minx-2),width,zb.zlen+3).translate(((minx-2+split-0.15)/2,(4.3+194.3)/2,(zb.zmin+zb.zmax)/2))
cutright=cq.Workplane('XY').box(maxx+2-(split+0.15),width,zb.zlen+3).translate(((split+0.15+maxx+2)/2,(4.3+194.3)/2,(zb.zmin+zb.zmax)/2))
for name,box in [('05_ruta_venstre',cutleft),('06_ruta_hogre',cutright)]:
    shape=plane.intersect(box)
    bb=shape.val().BoundingBox()
    shapes[name]=shape.translate((-(bb.xmin+bb.xmax)/2,-(bb.ymin+bb.ymax)/2,-bb.zmin))

for name,shape in shapes.items():
    path=OUT/(name+'.stl')
    exporters.export(shape,str(path),'STL',tolerance=.055,angularTolerance=.085)
    b=shape.val().BoundingBox()
    print(name,'size_mm',tuple(round(v,2) for v in (b.xlen,b.ylen,b.zlen)),'solid_cm3',round(shape.val().Volume()/1000,2),'file',path.name)
print('exported',len(shapes),'to',OUT)
