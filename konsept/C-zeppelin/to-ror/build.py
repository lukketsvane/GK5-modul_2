import math,json
from pathlib import Path
import cadquery as cq

ROOT=Path(__file__).resolve().parent
(ROOT/"samansetjingar").mkdir(exist_ok=True)
(ROOT/"delar").mkdir(exist_ok=True)
PITCH=60.0
STATIONS=list(range(6))
SHELL_KINDS=(4,2,0,0,2,4)
AXIS_Z=136.0
SHAFT_Y={"upper":-10.0,"lower":10.0}
HEIGHTS={"upper":[65,62,55,44,25],"lower":[38,36,32,26,15]}
OPEN_DEG=32.0
SHUTTER_CLOSED_DEG=0.0
SHUTTER_OPEN_DEG=32.0

def tube():
    outer=cq.Solid.makeCylinder(4.5,408,cq.Vector(-198,0,0),cq.Vector(1,0,0))
    inner=cq.Solid.makeCylinder(2.8,409,cq.Vector(-198.5,0,0),cq.Vector(1,0,0))
    return outer.cut(inner)

def leaf(kind,lane,which):
    side=1 if which=="upper" else -1
    ys=-1 if which=="upper" else 1
    reach=HEIGHTS[which][kind]
    span=[41,40,38,33,24][kind]
    wires=[]
    for j in range(35):
        u=j/34
        z=side*(7.8+(reach-7.8)*u)
        half=max(0.8,7.5*(1-u)+span*math.sin(math.pi*u)**0.85)
        centre=8.0+13*u
        y=ys*(18+13*lane+6*u*u)
        pts=[cq.Vector(centre-half,y-.35,z),cq.Vector(centre+half,y-.35,z),
             cq.Vector(centre+half,y+.35,z),cq.Vector(centre-half,y+.35,z)]
        wires.append(cq.Wire.makePolygon(pts+[pts[0]]))
    return cq.Solid.makeLoft(wires,ruled=True)

def mount(lane,which):
    zz=1 if which=="upper" else -1
    yy=-1 if which=="upper" else 1
    ring=cq.Solid.makeCylinder(6.5,7.0,cq.Vector(-3.5,0,0),cq.Vector(1,0,0))
    bore=cq.Solid.makeCylinder(4.55,7.2,cq.Vector(-3.6,0,0),cq.Vector(1,0,0))
    arm_len=18+13*lane+1
    arm=cq.Workplane("XY").box(7.0,arm_len,4).translate((0,yy*arm_len/2,zz*6.2)).val()
    hub=ring.cut(bore).fuse(arm)
    return hub

def shutter(which):
    yy=1 if which=="upper" else -1
    drop=20.0 if which=="upper" else 22.0
    dy=yy*9.1
    dz=-drop+6
    length=math.hypot(dy,dz)
    ny=-dz/length*.4
    nz=dy/length*.4
    points=[(-ny,-6-nz),(dy-ny,-drop-nz),(dy+ny,-drop+nz),(ny,-6+nz)]
    return cq.Workplane("YZ").polyline(points).close().extrude(175,both=True).val()

def bearing_block(x):
    b=cq.Workplane("XY").box(6.0,39.0,23.0).translate((x,0,132)).val()
    for y in (-10,10):
        bore=cq.Solid.makeCylinder(4.9,7,cq.Vector(x-3.5,y,AXIS_Z),cq.Vector(1,0,0))
        b=b.cut(bore)
    return b

def pedestal():
    wires=[]
    for z,w,h in ((12,54,30),(70,41,25),(122,26,22)):
        wires.append(cq.Workplane("XY",origin=(0,0,z)).rect(w,h).val())
    return cq.Solid.makeLoft(wires,ruled=True)

def gear(phase=0.0):
    teeth=20; module=1.0; pressure=math.radians(20)
    pitch=teeth*module/2
    base=pitch*math.cos(pressure)
    root=pitch-1.25*module; tip=pitch+module
    def inv(r):
        if r<=base:return 0.0
        t=math.sqrt((r/base)**2-1)
        return t-math.atan(t)
    half=math.pi/(2*teeth)+inv(pitch)
    coords=[]
    for n in range(teeth):
        mid=phase+n*2*math.pi/teeth
        def pt(r,a):coords.append((r*math.cos(a),r*math.sin(a)))
        pt(root,mid-half);pt(base,mid-half)
        for j in range(1,9):
            r=base+(tip-base)*j/8
            pt(r,mid-half+inv(r))
        lo=mid-half+inv(tip);hi=mid+half-inv(tip)
        for j in range(1,5):pt(tip,lo+(hi-lo)*j/4)
        for j in range(7,-1,-1):
            r=base+(tip-base)*j/8
            pt(r,mid+half-inv(r))
        pt(root,mid+half)
    solid=cq.Workplane("YZ").polyline(coords).close().extrude(2.5,both=True).val()
    bore=cq.Solid.makeCylinder(4.55,6,cq.Vector(-3,0,0),cq.Vector(1,0,0))
    return solid.cut(bore)

def knob():
    head=cq.Solid.makeCylinder(15,5,cq.Vector(0,0,0),cq.Vector(1,0,0))
    bore=cq.Solid.makeCylinder(4.55,5.2,cq.Vector(-.1,0,0),cq.Vector(1,0,0))
    return head.cut(bore)

PARTS={"tube":tube(),"shutter_upper":shutter("upper"),"shutter_lower":shutter("lower"),
       "base":cq.Solid.makeCylinder(66,12,cq.Vector(0,0,0),cq.Vector(0,0,1)),
       "pedestal":pedestal(),"saddle":cq.Workplane("XY").box(374,13,3).translate((0,0,122)).val(),
       "led":cq.Workplane("XY").box(340,13,1.7).translate((0,0,127.2)).val(),
       "gear_upper":gear(),"gear_lower":gear(math.pi/20),"knob":knob(),
       "end_frame":bearing_block(0)}
for k in sorted(set(SHELL_KINDS)):
    for lane in range(4):
        for which in ("upper","lower"):
            PARTS[f"leaf_{which}_{k}_{lane}"]=leaf(k,lane,which)
for lane in range(4):
    for which in ("upper","lower"):
        PARTS[f"mount_{which}_{lane}"]=mount(lane,which)

for name,s in PARTS.items():
    if not s.isValid() or s.Volume()<=0:
        raise ValueError(f"Invalid CAD: {name} {s.Volume()}")
    if name in ("tube","shutter_upper","shutter_lower","gear_upper","gear_lower","knob") or name.startswith("leaf_"):
        cq.exporters.export(s,str(ROOT/"delar"/(name+".step")))

INST=[]
def add(g,name,motion="fixed",x=0,y=0,z=0,color="matte"):
    INST.append({"g":g,"name":name,"motion":motion,"p":[float(x),float(y),float(z)],"color":color})
for n in ("base","pedestal"):
    add(n,n,color="matte")
add("saddle","saddle",color="frame")
add("led","fixed_LED",color="light")
for x,kind in ((-185,"left"),(185,"right")):
    add("end_frame","bearing_frame_"+kind,x=x,color="frame")
for which in ("upper","lower"):
    yy=SHAFT_Y[which]
    add("tube","tube_"+which,which,y=yy,z=AXIS_Z,color="frame")
    add("shutter_"+which,"light_gate_"+which,which,y=yy,z=AXIS_Z,color="metal")
    add("gear_"+which,"synchronizing_gear_"+which,which,x=199,y=yy,z=AXIS_Z,color="metal")
    for i in STATIONS:
        lane=i%4
        x=(i-2.5)*PITCH
        kind=SHELL_KINDS[i]
        add(f"leaf_{which}_{kind}_{lane}",f"shell_{i+1}_{which}",which,x,yy,AXIS_Z)
        add(f"mount_{which}_{lane}",f"pipe_clamp_{which}_{i+1}",which,x,yy,AXIS_Z,color="metal")
add("knob","hand_control","upper",208,-10,AXIS_Z,color="metal")

def transform(item,opening):
    x,y,z=item["p"]
    if item["motion"]=="upper":
        return cq.Location(cq.Vector(x,y,z),cq.Vector(1,0,0),-opening)
    if item["motion"]=="lower":
        return cq.Location(cq.Vector(x,y,z),cq.Vector(1,0,0),opening)
    return cq.Location(cq.Vector(x,y,z))

def assembly(opening):
    a=cq.Assembly(name=f"two_tubes_open_{opening}")
    colors={"matte":cq.Color(.58,.60,.62),"frame":cq.Color(.15,.16,.17),
            "metal":cq.Color(.41,.43,.45),"light":cq.Color(.98,.74,.42)}
    for o in INST:
        a.add(PARTS[o["g"]],name=o["name"],loc=transform(o,opening),color=colors[o["color"]])
    return a

for deg,name in ((0,"lukka"),(16,"halvopen"),(32,"open")):
    a=assembly(deg)
    a.save(str(ROOT/"samansetjingar"/(name+".step")))
    print("STEP",name,flush=True)

models={}
for name,shape in PARTS.items():
    verts,faces=shape.tessellate(1.4,.15)
    models[name]={"v":[round(t,3) for p in verts for t in p.toTuple()],
                  "f":[i for triangle in faces for i in triangle]}
scene={"models":models,"parts":INST,"units":"mm","kinematics":{"open_deg":32,"closed_deg":0,
       "axes":[{"which":"upper","direction":[1,0,0],"origin":[0,-10,136]},
               {"which":"lower","direction":[1,0,0],"origin":[0,10,136]}],
       "drive":"20tooth module1 external spur gear pair (nominal only)",
       "source":"CadQuery solids; Blender receives exact tessellation"}}
(ROOT/"scene.json").write_text(json.dumps(scene,separators=(",",":")),encoding="utf-8")
(ROOT/"mechanism.json").write_text(json.dumps({"pivots":2,"moving_tubes":2,"shells":6,"half_shells":12,
    "axis_spacing_mm":20,"gear": "20T module1 paired external gears",
    "closed_angle":0,"open_angle":32,"shutter_inner_edge_closed_y_mm":[-.9,.9],
    "validation_status":"not yet production qualified"},indent=2),encoding="utf-8")
print("CAD_OK",len(PARTS),"parts",len(INST),"instances",flush=True)
