import math, json
from pathlib import Path
import cadquery as cq
import numpy as np
from scipy.interpolate import PchipInterpolator

ROOT=Path(__file__).resolve().parent
for sub in ('step','stl','previews'): (ROOT/sub).mkdir(exist_ok=True)
H=220.0
BASE_D=58.6
THICK=2.3
spec={
'front': [(8,24,26,25,7,0.7),(28,33,24,24,12,1.1),(60,44,21,21,16,1.7),(110,55,16,16,19.4,1.8),(160,54,16,16,19.4,1.8),(190,41,18,18,17,1.5),(207,31,18,18,12,1.1),(216,23.5,18,18,6,0.5),(220,23,18,18,2.1,0.2)],
'shoulder':[(11,23,43,40,5,0.5),(40,40,44,40,14,1.0),(90,52,40,37,25,1.7),(122,52,40,37,29,1.9),(160,50,41,38,27,1.8),(190,40,42,40,20,1.4),(207,30,42,40,11,0.8),(214,25,42,41,4,0.4),(216,24,42,41,1.3,0.1)],
'outer':[(12,24,83,57,4,0.5),(50,38,83,58,15,1.3),(90,50,84,60,23,1.8),(110,51.8,85,60,24,1.9),(165,52,85,60,24,1.9),(185,47,86,62,21,1.7),(200,35,86,62,13,1.0),(209,28,85,62,4,0.3),(211,25,85,62,1.2,0.1)],
'rear':[(16,24,125,130,5,0.4),(50,38,123,129,18,1.0),(90,49,123,130,26,1.7),(122,53,125,130,28,1.9),(160,51,126,130,27,1.8),(187,42,127,130,22,1.4),(199,30,127,130,12,0.8),(205,25,126,130,3,0.2),(207,24,126,130,1.0,0.1)]
}

def parameters(name,z):
    rows=np.asarray(spec[name],dtype=float)
    return [float(PchipInterpolator(rows[:,0],rows[:,j])(z)) for j in range(1,6)]

def point(z,sgn,r,phi,beta,w,c,u,depth=0):
    a=math.radians(phi); b=math.radians(beta)
    center=np.array([sgn*r*math.sin(a),-r*math.cos(a)])
    tangent=np.array([sgn*math.cos(b),math.sin(b)])
    normal=np.array([sgn*math.sin(b),-math.cos(b)])
    xy=center+tangent*(.5*w*u)+normal*(c*(1-u*u)-depth)
    return cq.Vector(float(xy[0]),float(xy[1]),float(z))

def section(name,side,z):
    r,phi,beta,w,c=parameters(name,z)
    front=[point(z,side,r,phi,beta,w,c,u) for u in np.linspace(-1,1,15)]
    back=[point(z,side,r,phi,beta,w,c,u,THICK) for u in np.linspace(1,-1,15)]
    es=[cq.Edge.makeSpline(front),cq.Edge.makeLine(front[-1],back[0]),cq.Edge.makeSpline(back),cq.Edge.makeLine(back[-1],front[0])]
    return cq.Wire.assembleEdges(es)

def rib(name,side):
    z0=spec[name][0][0]; z1=spec[name][-1][0]
    heights=np.linspace(z0,z1,29)
    heights=sorted(set([float(z) for z in heights]+[float(row[0]) for row in spec[name]]))
    shell=cq.Solid.makeLoft([section(name,side,z) for z in heights],ruled=False)
    r,phi,beta,_,_=parameters(name,z0)
    xy=point(z0,side,r,phi,beta,0,0,0)
    # Short keyed stalk below lower shell, a detachable prototype interface
    stalk=(cq.Workplane('XY').box(4.5,4.5,7,centered=(True,True,False)).translate((xy.x,xy.y,1.4)).val())
    return shell.fuse(stalk)

def base():
    radius=BASE_D/2
    body=cq.Workplane('XY').circle(radius).extrude(8.4)
    body=body.cut(cq.Workplane('XY').circle(25.3).extrude(3.8))
    body=body.cut(cq.Workplane('XY').circle(8).extrude(8.5))
    for name in spec:
      for side in (-1,1):
        z=spec[name][0][0]
        r,phi,beta,_,_=parameters(name,z)
        v=point(z,side,r,phi,beta,0,0,0)
        body=body.cut(cq.Workplane('XY').center(v.x,v.y).rect(5,5).extrude(5.8).translate((0,0,2)))
    body=body.cut(cq.Workplane('XY').center(0,-radius+1).rect(5,9).extrude(5))
    return body.val()

def diffuser():
    z=[8,15,30,55,85,115,145,170,185,200,210,215]
    r=[17.0,17.5,18.2,22,23.4,24,23.4,22,20,17.5,15.7,14.8]
    outer=cq.Solid.makeLoft([cq.Wire.makeCircle(rv,cq.Vector(0,0,zv),cq.Vector(0,0,1)) for zv,rv in zip(z,r)],ruled=False)
    inner=cq.Solid.makeLoft([cq.Wire.makeCircle(rv-1.5,cq.Vector(0,0,zv-.01),cq.Vector(0,0,1)) for zv,rv in zip(z,r)],ruled=False)
    # Keep vented open upper lip for concept level and avoid a forced hub
    return outer.cut(inner)

def core():
    return cq.Workplane('XY').rect(11.0,11.0).extrude(183).translate((0,0,10)).val()

def ballast():
    return cq.Workplane('XY').circle(24.8).circle(5).extrude(3).translate((0,0,.1)).val()

parts={}
for name in spec:
    for side in (-1,1):parts[f'RIB_{name.upper()}_{"R" if side>0 else "L"}']=rib(name,side)
parts['BASE']=base()
parts['DIFFUSER']=diffuser()
parts['AL_CORE']=core()
parts['BALLAST']=ballast()
assembly=cq.Assembly(name='NORTHERN_CONCEPT_C_R04')
for key,part in parts.items():
    if not part.isValid():raise RuntimeError('INVALID '+key)
    c=cq.Color(.62,.56,.48) if key.startswith('RIB') else cq.Color(.75,.72,.67) if key=='BASE' else cq.Color(1,.9,.69,.7) if key=='DIFFUSER' else cq.Color(.35,.35,.35)
    assembly.add(part,name=key,color=c)
    cq.exporters.export(part,str(ROOT/'step'/f'{key}.step'))
    if key!='AL_CORE':cq.exporters.export(part,str(ROOT/'stl'/f'{key}.stl'),tolerance=.075,angularTolerance=.14)
assembly.save(str(ROOT/'step'/'ASSEMBLY_R04.step'))
manifest={"revision":"R04","source":"one reference photograph; inferred dimensions","height_mm":220,"width_target_mm":115.3,"base_od_mm":BASE_D,"rib_count":8,"rib_groups":list(spec),"rib_wall_mm":THICK,"diffuser":'tapered opal hollow polycarbonate',"tests":"STEP solid validity only; photometry, mechanics, electricity are not certified"}
(ROOT/'dimensions.json').write_text(json.dumps(manifest,indent=2))
print('R04_BUILD_OK',len(parts))
for k,p in parts.items():
 bb=p.BoundingBox();print(k,round(p.Volume()),'BBOX',round(bb.xmin,1),round(bb.xmax,1),round(bb.zmin,1),round(bb.zmax,1))
