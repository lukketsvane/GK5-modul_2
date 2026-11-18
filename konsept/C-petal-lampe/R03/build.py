import cadquery as cq
import math,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
STEP=ROOT/'step'; STL=ROOT/'stl'; PRE=ROOT/'previews'
for p in (STEP,STL,PRE):p.mkdir(exist_ok=True)
P={'concept':'C','revision':'R03','height_mm':220,'petal_count':8,'petal_t_mm':2.6,'petal_z0_mm':8.0,'petal_z1_mm':220.0,'base_od_mm':60.0,'base_exposed_h_mm':7.7,'diffuser_od_mm':38.4,'supply_VDC':24,'prototype_only':True}

def vec(r,a,z):
 t=math.radians(a);return cq.Vector(r*math.cos(t),r*math.sin(t),z)
def box(x,y,z,l,w,h):return cq.Workplane('XY').box(l,w,h).translate((x,y,z)).val()
def turn(s,a):return s.rotate((0,0,0),(0,0,1),a)
def section(z):
 t=(z-8)/212;q=max(0,math.sin(math.pi*t));radius=25.5+32.5*q**.84-5.2*t**6
 a=5.+11.5*q**1.2
 if t>.982:a*=1-.53*((t-.982)/.018)**1.4
 twist=1.6*math.sin(2*math.pi*t)
 outer=[];inner=[]
 for i in range(23):
  v=-1+i/11;az=a*v+twist;r=radius+1.45*(1-v*v)-.6*v
  outer.append(vec(r,az,z));inner.append(vec(r-2.6,az,z))
 return cq.Wire.assembleEdges([cq.Edge.makeSpline(outer),cq.Edge.makeLine(outer[-1],inner[-1]),cq.Edge.makeSpline(inner[::-1]),cq.Edge.makeLine(inner[0],outer[0])])
def petal():
 body=cq.Solid.makeLoft([section(8+212*i/46) for i in range(47)],ruled=False)
 tongue=box(25.55,0,15.6,7.7,7.3,12.0)
 body=body.fuse(tongue)
 body=body.cut(cq.Solid.makeCylinder(2.03,6.6,cq.Vector(25.55,0,9.5)))
 return body.fuse(box(24.5,0,212.0,5.7,3.8,4.0))
def base():
 body=cq.Workplane('XY').circle(29.8).circle(26.4).extrude(5.5).translate((0,0,1.2))
 body=body.union(cq.Workplane('XY').circle(29.8).extrude(1.1).translate((0,0,6.6)))
 for k in range(8):
  a=22.5+45*k
  boss=cq.Workplane('XY').box(9.5,11.5,12.5,centered=(True,True,False)).translate((25,0,7.7)).rotate((0,0,0),(0,0,1),a)
  body=body.union(boss)
  pocket=cq.Workplane('XY').box(10.5,8.1,12.6,centered=(True,True,False)).translate((26.65,0,7.7)).rotate((0,0,0),(0,0,1),a)
  body=body.cut(pocket)
  body=body.cut(cq.Solid.makeCylinder(1.74,9,vec(25.55,a,1.0)))
  body=body.cut(cq.Solid.makeCylinder(2.85,2.3,vec(25.55,a,1.15)))
 for k in range(4):
  a=k*90;at=vec(20.5,a,0)
  body=body.union(cq.Workplane('XY').center(at.x,at.y).circle(3.7).extrude(5.4).translate((0,0,1.2)))
  body=body.cut(cq.Solid.makeCylinder(1.8,5.5,vec(20.5,a,1.15)))
 body=body.union(cq.Workplane('XY').circle(11).extrude(17.3).translate((0,0,7.7)))
 body=body.cut(cq.Workplane('XY').rect(12.6,12.6).extrude(18.2).translate((0,0,7.2)))
 body=body.cut(cq.Solid.makeCylinder(1.72,8,cq.Vector(0,0,5)))
 body=body.cut(cq.Workplane('XY').circle(19.5).circle(17.45).extrude(3.2).translate((0,0,7.1)))
 body=body.cut(cq.Solid.makeCylinder(2.25,11,cq.Vector(0,-31,4.2),cq.Vector(0,1,0)))
 return body.val()
def lid():
 p=cq.Workplane('XY').circle(29.8).extrude(1.2)
 for k in range(4):
  a=k*90;p=p.cut(cq.Solid.makeCylinder(1.4,1.3,vec(20.5,a,-.05)))
  p=p.cut(cq.Solid.makeCylinder(2.6,.92,vec(20.5,a,-.01)))
 return p.cut(cq.Workplane('XY').circle(1.7).extrude(1.3)).val()
def ballast():
 p=cq.Workplane('XY').circle(26.4).extrude(4.5).translate((0,0,1.5))
 p=p.cut(cq.Workplane('XY').circle(5.5).extrude(4.6).translate((0,0,1.45)))
 for k in range(8):p=p.cut(cq.Solid.makeCylinder(3.1,4.6,vec(25.55,22.5+45*k,1.45)))
 for k in range(4):p=p.cut(cq.Solid.makeCylinder(4,4.6,vec(20.5,90*k,1.45)))
 return p.cut(cq.Workplane('XY').box(5,29,4.8).translate((0,-14.5,3.75))).val()
def diffuser():return cq.Workplane('XY').circle(19.2).circle(17.7).extrude(197).translate((0,0,8.3)).val()
def cap_guide():
 cap=cq.Workplane('XY').circle(19.2).extrude(3).translate((0,0,205.3))
 cap=cap.union(cq.Workplane('XY').circle(17.7).circle(16.5).extrude(3).translate((0,0,202.3)))
 bridge=cq.Workplane('XY').circle(20.6).circle(16.5).extrude(1.7).translate((0,0,207.8))
 guide=cq.Workplane('XY').circle(20.6).circle(19.4).extrude(4.5).translate((0,0,209))
 for k in range(8):
  a=22.5+k*45
  arm=cq.Workplane('XY').box(9.5,11,4.5).translate((22,0,211.25)).rotate((0,0,0),(0,0,1),a)
  guide=guide.union(arm)
  pocket=cq.Workplane('XY').box(7.7,8.5,8).translate((24.5,0,212)).rotate((0,0,0),(0,0,1),a)
  guide=guide.cut(pocket)
 return cap.union(bridge).union(guide).val()
def core():
 p=cq.Workplane('XY').rect(12,12).extrude(191.5).translate((0,0,10))
 return p.cut(cq.Workplane('XY').circle(1.25).extrude(10).translate((0,0,9.9))).val()
def led():return box(6.22,0,109.5,.42,8,150)
def screw_m3():return cq.Solid.makeCylinder(1.47,13,cq.Vector(0,0,3.4)).fuse(cq.Solid.makeCylinder(2.75,2.2,cq.Vector(0,0,1.2)))
def screw_m25():return cq.Solid.makeCylinder(1.15,5,cq.Vector(0,0,.9)).fuse(cq.Solid.makeCylinder(2.4,.9,cq.Vector(0,0,0)))
parts={'C01_RIB_PETG':petal(),'C02_BASE_PETG':base(),'C03_BOTTOM_PETG':lid(),'C04_BALLAST_STEEL':ballast(),'C05_DIFFUSER_OPAL_PC':diffuser(),'C06_CAP_AND_GUIDE_OPAL_PC':cap_guide(),'C08_LED_CORE_ALUMINUM':core(),'C09_LED_STRIP_PLACEHOLDER':led(),'C10_RIB_SCREW_M3_PLACEHOLDER':screw_m3(),'C11_LID_SCREW_M25_PLACEHOLDER':screw_m25()}
ass=cq.Assembly(name='NORTHERN_C_PETAL_R03')
for name in ['C02_BASE_PETG','C03_BOTTOM_PETG','C04_BALLAST_STEEL','C05_DIFFUSER_OPAL_PC','C06_CAP_AND_GUIDE_OPAL_PC','C08_LED_CORE_ALUMINUM']:
 ass.add(parts[name],name=name)
for k in range(8):
 a=22.5+45*k
 ass.add(turn(parts['C01_RIB_PETG'],a),name=f'RIB_{k+1:02}')
 ass.add(parts['C10_RIB_SCREW_M3_PLACEHOLDER'].translate(vec(25.55,a,0)),name=f'M3_RIB_{k+1:02}')
for k in range(4):
 ass.add(turn(parts['C09_LED_STRIP_PLACEHOLDER'],90*k),name=f'LED_STRIP_{k+1:02}')
 ass.add(parts['C11_LID_SCREW_M25_PLACEHOLDER'].translate(vec(20.5,90*k,0)),name=f'LID_SCREW_{k+1:02}')
for name,solid in parts.items():
 assert solid.isValid(),name
 cq.exporters.export(solid,str(STEP/(name+'.step')))
 cq.exporters.export(solid,str(STL/(name+'.stl')),tolerance=.07,angularTolerance=.15)
ass.save(str(STEP/'C_PETAL_R03_ASSEMBLY.step'))
(ROOT/'dimensions.json').write_text(json.dumps(P,indent=2))
print('BUILD_SUCCESS',len(parts),'parts')
