from pathlib import Path
import runpy, json, numpy as np
import cadquery as cq
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import PchipInterpolator, UnivariateSpline
from shapely.geometry import Polygon, LineString
import ezdxf

R = Path(__file__).resolve().parents[1]
CAD = R/'cad'; OUT = R/'produksjon'; TEST = R/'kontroll'
for p in (CAD,OUT,TEST):p.mkdir(parents=True,exist_ok=True)
ctx=runpy.run_path(str(CAD/'snitt_fbx.py'))
section,loops=ctx['section'],ctx['loops']
A=ctx['data']; SC=ctx['sc']; ZERO=ctx['zero']
N=60

def sample(s):
    contours=loops(section('c001',s+.0137))
    if not contours:raise ValueError('Ingen polygon ved z='+str(s))
    p=np.asarray(contours[0])
    if not np.allclose(p[0],p[-1]):p=np.vstack([p,p[0]])
    if not Polygon(p).exterior.is_ccw:p=p[::-1]
    dis=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
    points=np.linspace(0,dis[-1],N,endpoint=False)
    xy=np.array([np.interp(points,dis,p[:,i]) for i in range(2)]).T
    return gaussian_filter1d(xy,.4,axis=0,mode='wrap')

def spline_loft(profiles):
    wires=[]
    for z,pts in profiles:
        vectors=[cq.Vector(float(x),float(y),float(z)) for x,y in pts]
        wires.append(cq.Wire.assembleEdges([cq.Edge.makeSpline(vectors,periodic=True)]))
    solid=cq.Solid.makeLoft(wires,ruled=False)
    if not solid.isValid() or solid.Volume()<1:raise ValueError('Ikkje gyldig loft')
    return solid

def inward(xy,t=4):
    diff=np.roll(xy,-1,axis=0)-np.roll(xy,1,axis=0)
    n=np.stack([-diff[:,1],diff[:,0]],axis=1)/np.maximum(np.linalg.norm(diff,axis=1,keepdims=True),1e-9)
    return xy+t*n

zs=sorted(set([1]+list(range(5,196,5))+[196,196.2])); prof=[]
for z in zs:
    p=sample(z)
    if prof:
        old=prof[-1][1];p=np.roll(p,-int(np.argmin([np.sum((np.roll(p,-k,axis=0)-old)**2) for k in range(N)])),axis=0)
    else:p=np.roll(p,-np.argmax(p[:,0]),axis=0)
    prof.append((z,p))
body=spline_loft([(0,prof[0][1])]+prof)
print('Body',body.isValid(),round(body.Volume()),flush=True)
inner=[(-5,inward(prof[0][1]))]+[(z,inward(p)) for z,p in prof if z<=185]
core1=spline_loft([t for t in inner if t[0]<=130])
core2=spline_loft([t for t in inner if t[0]>=130])
print('Core parts',core1.isValid(),core2.isValid(),round(core1.Volume()),round(core2.Volume()),flush=True)

poly=Polygon(loops(section('c006',100.0137))[0]);xs=np.arange(-45,98,2);ys=[]
for x in xs:
    g=poly.intersection(LineString([(x,-150),(x,30)]))
    if g.geom_type=='LineString':q=np.array(g.coords)
    elif g.geom_type=='MultiLineString':q=np.array([a for seg in g.geoms for a in seg.coords])
    else:raise ValueError('Filmkrumming feila: x='+str(x))
    ys.append((q[:,1].min()+q[:,1].max())/2)
yfun=PchipInterpolator(xs,ys)
source=(A['c006']-ZERO)*SC
xref=np.arange(-45,99,4);tops=[];bots=[]
for x in xref:
    vertices=source[np.abs(source[:,0]-x)<3]
    tops.append(vertices[:,2].max());bots.append(vertices[:,2].min())
top=UnivariateSpline(xref,tops,k=3,s=35)
bottom=UnivariateSpline(xref,bots,k=3,s=12)
wires=[]
for x in np.linspace(-45,97,26):
    y=float(yfun(x));slope=float(yfun.derivative()(x))
    normal=np.array([-slope,1])/np.sqrt(1+slope*slope)
    p=np.array([x,y]);lo=p-.5*normal;hi=p+.5*normal
    verts=[cq.Vector(float(q[0]),float(q[1]),float(z)) for q,z in [(lo,float(bottom(x))),(hi,float(bottom(x))),(hi,float(top(x))),(lo,float(top(x)))]]
    wires.append(cq.Wire.makePolygon(verts,close=True))
panel=cq.Solid.makeLoft(wires,ruled=False)
if not panel.isValid():raise ValueError('Diffusjonsflate er ugyldig')
print('Panel',panel.isValid(),round(panel.Volume()),flush=True)

xx=np.linspace(-45,97,401);xy=np.column_stack([xx,yfun(xx)])
u=np.r_[0,np.cumsum(np.linalg.norm(np.diff(xy,axis=0),axis=1))]
flatten=np.r_[np.column_stack([u,top(xx)]),np.column_stack([u[::-1],bottom(xx[::-1])])]
doc=ezdxf.new('R2010');doc.units=4;doc.layers.new('KUTT_1_1',dxfattribs={'color':7})
doc.modelspace().add_lwpolyline(flatten.tolist(),close=True,dxfattribs={'layer':'KUTT_1_1'})
doc.saveas(str(OUT/'raup_diffusor_1til1.dxf'))

clip=cq.Workplane('XY').box(22,13,12).val().cut(cq.Workplane('XY').box(24,1.35,11).translate((0,0,3.7)).val()).cut(cq.Solid.makeCylinder(1.65,13,cq.Vector(0,4.2,-6.5)))
carrier=cq.Workplane('XY').box(70,12,2).val()
for x in [-29,29]:carrier=carrier.cut(cq.Solid.makeCylinder(1.65,4,cq.Vector(x,0,-2)))
shapes={'raup_hovudkropp_ytre':body,'raup_kjerne_nedre':core1,'raup_kjerne_ovre':core2,'raup_diffusor':panel,'raup_filmklips':clip,'raup_led_berar':carrier}
for side,lo,hi in [('minus_Y',-100,0),('pluss_Y',0,110)]:
    mold=cq.Solid.makeBox(234,hi-lo,213,cq.Vector(-117,lo,-8)).cut(body)
    for x in [-110,110]:
        for z in [24,179]:
            p=cq.Vector(x,-8 if hi==0 else 0,z)
            mold=mold.cut(cq.Solid.makeCylinder(2.6,8,p,cq.Vector(0,1,0)))
    shapes['raup_stoypform_'+side]=mold

checks=[]
for name,shape in shapes.items():
    if not shape.isValid() or shape.Volume()<=0:raise ValueError('Ugyldig BRep '+name)
    step=CAD/(name+'.step');cq.exporters.export(shape,str(step))
    reread=cq.importers.importStep(str(step)).val()
    if not reread.isValid() or reread.Volume()<=0:raise ValueError('STEP reimport feila '+name)
    checks.append({'fil':step.name,'STEP_gyldig':True,'volum_mm3':round(reread.Volume())})
    cq.exporters.export(shape,str(OUT/(name+'.stl')),tolerance=.3,angularTolerance=.2)
    print('Export',name,flush=True)
report={'status':'Prototyp, ikkje ferdig produksjonsgodkjend','eining':'mm','FBX_antaking_panel_hogd_mm':270,'flate_veggtykkleik_mm':1,'inner_offset_mm':4,'flatmonster_breidd_mm':round(float(u[-1]),2),'kontrollar':checks,'alle_STEP_valid':True,'hollow_shell_validering':False,'manglar':['Eitt gyldig uthola slutt-BRep-skall','Mold demolding, underkutt og krymp','Lys, varme, elektro og veltetest','Faktisk material-ID for monitorfolien']}
(TEST/'raup_CAD_verifisering.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
(R/'LES_MEG_RAUP.md').write_text('# RAUP · CAD-prototyp\n\nOriginal FBX er geometrisk rekonstruert som parametrisk B-rep. Skala er sett frå ei antaking om 270 mm maksimal høgd.\n\n`cad/*.step`: ytre kropp, bøygd filmplate, førebels kjerne, formhalvdelar, filmklips, LED-berar.\n\n`produksjon/*.stl`: maskinlesbare prototypeksportar. `produksjon/raup_diffusor_1til1.dxf`: utbreidd film på mm-skala (ca 198 mm breidd).\n\n**Ikkje enno produksjonsgodkjent:** Kjerne og ytre kropp er gyldige kvar for seg, men endeleg uthola BRep skal ikkje reknast som verifisert. Formfrigjering,  materialkrymp, papirvegg, lys, varme, stabilitet, elektrosikkerheit og filmens kjemiske samansetjing krev fysiske prøvar. Ikkje laserskjer ukjend monitorfolie. Klips og LED-berar er førebelse, ikkje montert eller lastprøvd.\n\nSkriptet kan køyrast på ny med `py -3 cad/raup_produksjon.py` i `raup`-mappa. Endringar utanfor denne mappa er ikkje nødvendige.\n',encoding='utf-8')
print('RAUP COMPLETE',len(shapes),'STEP; DXF width',round(float(u[-1]),1),'mm',flush=True)
