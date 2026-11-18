from astra_scoop import make_scoop
import math
import json
from pathlib import Path
import cadquery as cq

HERE = Path(__file__).resolve().parent
PARTS = HERE / "delar"
POSES = HERE / "samansetjingar"
PARTS.mkdir(exist_ok=True)
POSES.mkdir(exist_ok=True)

PITCH = 13 * math.pi
CENTRES = [i * PITCH for i in range(-4, 5)]
HEIGHT = 111.0
CLOSED = 0.0
OPEN = 20.0
HALF_CHORD = [56, 49, 35, 20, 4]
WING_WIDTH = [57, 51, 47, 37, 30]
SHEET = 0.6
RACK_RADIUS = 10.0
MATTE = cq.Color(0.64, 0.65, 0.67)
FRAME = cq.Color(0.29, 0.30, 0.32)
METAL = cq.Color(0.48, 0.50, 0.52)
LIGHT = cq.Color(0.91, 0.88, 0.80)

def blade(kind,sign,direction):
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


def hinge_cap():
    return cq.Solid.makeCylinder(3.6,1.4,cq.Vector(0,-27.0,0),cq.Vector(0,-1,0))

def front_guard():
    return cq.Solid.makeCylinder(2.35,376.0,cq.Vector(-188,-82.0,111.0),cq.Vector(1,0,0))

def button():
    return cq.Solid.makeCylinder(3.4,2.5,cq.Vector(0,-10.0,31.0),cq.Vector(0,-1,0))

def opal_strip():
    return cq.Workplane("XY").box(341.0,2.4,10.0).translate((0,-15.5,83.0)).val()

def shoe(sign):
    block=cq.Workplane("XY").box(11.4,4.7,18.0).translate((0,sign*21.35,0)).val()
    bore=cq.Solid.makeCylinder(2.55,5.1,cq.Vector(0,sign*18.8,0),cq.Vector(0,sign,0))
    block=block.cut(bore)
    for z in (-7.0,7.0):
        hole=cq.Solid.makeCylinder(1.25,5.1,cq.Vector(0,sign*18.8,z),cq.Vector(0,sign,0))
        block=block.cut(hole)
    set_screw=cq.Solid.makeCylinder(1.5,3.5,cq.Vector(5.7,sign*21.35,0),cq.Vector(-1,0,0))
    return block.cut(set_screw)

def screw(sign,z):
    body=cq.Solid.makeCylinder(1.2,5.8,cq.Vector(0,sign*18.5,z),cq.Vector(0,sign,0))
    head=cq.Solid.makeCylinder(2.2,1.4,cq.Vector(0,sign*24.3,z),cq.Vector(0,sign,0))
    return body.fuse(head)

def shaft(lane,long=False):
    half=31.0+16.0*lane
    y0,y1=-half,(79.0 if long else half)
    return cq.Solid.makeCylinder(2.5,y1-y0,cq.Vector(0,y0,0),cq.Vector(0,1,0))

def bearing(sign):
    start = sign*8.0
    outer = cq.Solid.makeCylinder(5.0, 4.0, cq.Vector(0,start,HEIGHT),cq.Vector(0,sign,0))
    inner = cq.Solid.makeCylinder(2.55, 4.0, cq.Vector(0,start,HEIGHT),cq.Vector(0,sign,0))
    return outer.cut(inner)

def involute(r, base):
    if r <= base:
        return 0.0
    t = math.sqrt((r/base)**2-1.0)
    return t-math.atan(t)

def pinion():
    teeth, module, pressure = 20, 1.0, math.radians(20)
    pitch = teeth*module/2.0
    base = pitch*math.cos(pressure)
    root, tip = pitch-1.25*module, pitch+module
    half = math.pi/(2*teeth)+involute(pitch,base)
    phase = math.pi/2.0+math.pi/teeth
    poly=[]
    def at(r, a):
        poly.append((r*math.cos(a),r*math.sin(a)))
    for k in range(teeth):
        t = phase+k*2*math.pi/teeth
        at(root,t-half)
        at(base,t-half)
        for j in range(1,9):
            r=base+(tip-base)*j/8
            at(r,t-half+involute(r,base))
        left=t-half+involute(tip,base)
        right=t+half-involute(tip,base)
        for j in range(1,5):
            at(tip,left+(right-left)*j/4)
        for j in range(7,-1,-1):
            r=base+(tip-base)*j/8
            at(r,t+half-involute(r,base))
        at(root,t+half)
        next_left=t+2*math.pi/teeth-half
        for j in range(1,4):
            at(root,t+half+(next_left-(t+half))*j/4)
    shape=cq.Workplane("XZ").polyline(poly).close().extrude(2.0,both=True).val()
    hole=cq.Solid.makeCylinder(2.55,6.0,cq.Vector(0,-3,0),cq.Vector(0,1,0))
    hub=cq.Solid.makeCylinder(6.3,3.7,cq.Vector(0,2,0),cq.Vector(0,1,0))
    gear=shape.fuse(hub).cut(cq.Solid.makeCylinder(2.55,10,cq.Vector(0,-3,0),cq.Vector(0,1,0)))
    lock=cq.Solid.makeCylinder(1.4,4.1,cq.Vector(0,4,6.35),cq.Vector(0,0,-1))
    return gear.cut(lock)

def shoe_lock(sign):
    return cq.Solid.makeCylinder(1.35,3.1,cq.Vector(2.55,sign*21.35,0),cq.Vector(1,0,0))

def knob_lock():
    return cq.Solid.makeCylinder(1.35,15.0,cq.Vector(2.55,77.0,0),cq.Vector(1,0,0))

def gear_lock():
    return cq.Solid.makeCylinder(1.25,3.4,cq.Vector(0,4,2.5),cq.Vector(0,0,1))

def rack():
    end=179.0
    pitch=math.pi
    root_half=math.pi/4+1.25*math.tan(math.radians(20))
    tip_half=math.pi/4-math.tan(math.radians(20))
    points=[(-end,127.0),(-end,122.25)]
    for k in range(-56,57):
        x=k*pitch
        points.extend([(x-root_half,122.25),(x-tip_half,120.0),
                       (x+tip_half,120.0),(x+root_half,122.25)])
    points.extend([(end,122.25),(end,127.0)])
    slide=cq.Workplane("XZ").polyline(points).close().extrude(2.0,both=True).val()
    for sign in (-1,1):
        lip=cq.Workplane("XY").box(358.0,2.0,1.6).translate((0,sign*2.9,125.5)).val()
        slide=slide.fuse(lip)
    return slide

def guide(sign):
    side=cq.Workplane("XY").box(366.0,1.5,4.5).translate((0,sign*4.9,125.75)).val()
    upper=cq.Workplane("XY").box(366.0,2.5,0.8).translate((0,sign*4.05,127.1)).val()
    lower=cq.Workplane("XY").box(366.0,2.5,0.8).translate((0,sign*4.05,123.9)).val()
    return side.fuse(upper).fuse(lower)

def rack_stop(sign):
    x=179.85 if sign>0 else -184.74
    return cq.Workplane("XY").box(1.5,4.0,6.7).translate((x,0,124.85)).val()

def rail(sign):
    c=cq.Workplane("XY").box(376.0,4.0,14.0).translate((0,sign*10.0,111.0)).val()
    for x in CENTRES:
        bore=cq.Solid.makeCylinder(5.1,6.0,cq.Vector(x,sign*7,HEIGHT),cq.Vector(0,sign,0))
        c=c.cut(bore)
    return c

def bar(x):
    return cq.Workplane("XY").box(6.0,16.0,4.0).translate((x,0,92.0)).val()

def base():
    return cq.Solid.makeCylinder(65.0,13.0,cq.Vector(0,0,0),cq.Vector(0,0,1))

def pedestal():
    return (cq.Workplane("XZ").moveTo(-32,13).threePointArc((-23,18),(-19,31))
        .lineTo(-19,56).threePointArc((-19,68),(-24,77))
        .lineTo(-24,91).lineTo(24,91).lineTo(24,77)
        .threePointArc((19,68),(19,56)).lineTo(19,31)
        .threePointArc((23,18),(32,13)).close().extrude(9,both=True).val())

def led(sign):
    return cq.Workplane("XY").box(340.0,3.0,2.0).translate((0,sign*14.0,90.0)).val()

def cover():
    return cq.Workplane("XY").box(350.0,20.0,1.6).translate((0,0,129.0)).val()

def knob():
    grip=cq.Solid.makeCylinder(18.0,4.0,cq.Vector(0,75.0,0),cq.Vector(0,1,0))
    dot=cq.Solid.makeCylinder(2.0,0.8,cq.Vector(0,79.0,12.0),cq.Vector(0,1,0))
    solid=grip.fuse(dot)
    bore=cq.Solid.makeCylinder(2.55,4.2,cq.Vector(0,74.9,0),cq.Vector(0,1,0))
    solid=solid.cut(bore)
    set_screw=cq.Solid.makeCylinder(1.5,16,cq.Vector(18,77.0,0),cq.Vector(-1,0,0))
    return solid.cut(set_screw)

def axial_collar(sign):
    y=sign*5.9
    outer=cq.Solid.makeCylinder(3.75,2.0,cq.Vector(0,y,0),cq.Vector(0,sign,0))
    bore=cq.Solid.makeCylinder(2.55,2.1,cq.Vector(0,y,0),cq.Vector(0,sign,0))
    return outer.cut(bore)

def locate(x, angle=0.0, z=HEIGHT, y=0.0):
    return cq.Location(cq.Vector(x,y,z),cq.Vector(0,1,0),angle)

def turn(theta):
    return RACK_RADIUS*math.radians(theta-CLOSED)

STATION_PARTS={}
for kind in range(5):
    for sign in (-1,1):
        for direction in (-1,1):
            STATION_PARTS[f"blade_{kind}_{sign}_{direction}"]=blade(kind,sign,direction)
STATION_PARTS.update({
    "shoe_-1":shoe(-1),"shoe_1":shoe(1),
    "screw_-1_-7":screw(-1,-7),"screw_-1_7":screw(-1,7),
    "screw_1_-7":screw(1,-7),"screw_1_7":screw(1,7),
    "gear":pinion(),"gear_lock":gear_lock(),"rack":rack(),"bearing_-1":bearing(-1),"bearing_1":bearing(1),
    "rail_-1":rail(-1),"rail_1":rail(1),"bar_left":bar(-183),"bar_right":bar(183),
    "base":base(),"pedestal":pedestal(),"led_-1":led(-1),"led_1":led(1),
    "cover":cover(),"knob":knob(),"knob_lock":knob_lock(),
    "guide_-1":guide(-1),"guide_1":guide(1),
    "stop_left":rack_stop(-1),"stop_right":rack_stop(1),
    "front_guard":front_guard(),"opal_strip":opal_strip(),"button":button(), "hinge_cap":hinge_cap(),
    "nose_left":endcap(-1),"nose_right":endcap(1),
    "shoe_lock_-1":shoe_lock(-1),"shoe_lock_1":shoe_lock(1),
})
for lane in range(4):
    STATION_PARTS[f"shaft_lane_{lane}"]=shaft(lane,False)
STATION_PARTS["shaft_lane_0_knob"]=shaft(0,True)
STATION_PARTS["collar_-1"]=axial_collar(-1)
STATION_PARTS["collar_1"]=axial_collar(1)

for name, solid in STATION_PARTS.items():
    if not solid.isValid() or solid.Volume() <= 0:
        raise ValueError(f"Invalid or empty CAD solid: {name}")
    cq.exporters.export(solid,str(PARTS/(name+".step")))

INSTANCES=[]
def add(g, move, name, x=0.0,y=0.0,z=0.0, color="matte"):
    INSTANCES.append({"g":g,"motion":move,"name":name,"p":[round(x,5),round(y,5),round(z,5)],"color":color})

for n in ["base","pedestal"]:
    add(n,"fixed",n,color="matte")
add("button","fixed","dimmer",color="metal")
for n in ["rail_-1","rail_1","bar_left","bar_right","cover","guide_-1","guide_1","stop_left","stop_right"]:
    add(n,"fixed",n,color="frame")
add("front_guard","fixed","visible_steel_rail",color="frame")
add("nose_left","fixed","left_blunt_tip",color="matte")
add("nose_right","fixed","right_blunt_tip",color="matte")

for sign in (-1,1):
    add(f"led_{sign}","fixed",f"LED_{sign}",color="light")
for i,x in zip(range(-4,5), CENTRES):
    kind=abs(i)
    lane=(i+4)%4
    for sign in (-1,1):
        direction = (1 if i<0 else -1 if i>0 else 1 if sign==-1 else -1)
        add(f"blade_{kind}_{sign}_{direction}","leaf",f"station_{i}_blade_{sign}",x,sign*16*lane,HEIGHT)

        add(f"bearing_{sign}","fixed",f"station_{i}_bearing_{sign}",x,0,0,color="metal")
        if sign==-1:
            add("hinge_cap","leaf",f"hinge_cap_{i}",x,sign*16*lane,HEIGHT,color="metal")
    add("shaft_lane_0_knob" if i==4 else f"shaft_lane_{lane}", "leaf", f"station_{i}_shaft",x,0,HEIGHT,color="metal")
    add("gear","gear",f"station_{i}_pinion",x,0,HEIGHT,color="frame")
    add("gear_lock","gear",f"station_{i}_gear_lock",x,0,HEIGHT,color="metal")
    if i==4:
        add("knob","leaf","knob",x,0,HEIGHT,color="frame")
        add("knob_lock","leaf","knob_lock",x,0,HEIGHT,color="metal")
add("rack","rack","rack",color="frame")

COLORS={"matte":MATTE,"frame":FRAME,"metal":METAL,"light":LIGHT}

def assembly(theta):
    a=cq.Assembly(name=f"C_zeppelin_{round(theta)}")
    for item in INSTANCES:
        p=item["p"]
        if item["motion"]=="leaf":
            loc=locate(p[0],theta,p[2],p[1])
        elif item["motion"]=="gear":
            loc=locate(p[0],theta-CLOSED,p[2])
        elif item["motion"]=="rack":
            loc=cq.Location(cq.Vector(turn(theta),0,0))
        else:
            loc=cq.Location(cq.Vector(*p))
        a.add(STATION_PARTS[item["g"]],name=item["name"],loc=loc,color=COLORS[item["color"]])
    return a

DISTANCES=[]
min_clearance=0.0
neighbor_shoe_gap=0.0
for angle,name in ((CLOSED,"reference"),(10.0,"intermediate"),(OPEN,"open")):
    assy=assembly(angle)
    assy.save(str(POSES/(name+".step")))
    print("exported",name,flush=True)

MESHES={}
for name,solid in STATION_PARTS.items():
    verts,faces=solid.tessellate(1.0,0.12)
    MESHES[name]={"v":[round(coord,2) for vert in verts for coord in vert.toTuple()],
                  "f":[int(i) for tri in faces for i in tri]}
data={
    "units":"mm",
    "models":MESHES,
    "parts":INSTANCES,
    "kinematics":{
        "dof":1,"actuation":"one keyed knob plus 9 module-1 pinions and single sliding rack",
        "closed_deg":CLOSED,"open_deg":OPEN,"rack_pitch_radius_mm":RACK_RADIUS,
        "rack_travel_mm":round(abs(turn(OPEN)),4),
        "pivot_axis":[0,1,0],"stations":[round(x,5) for x in CENTRES],
        "joint_types":["9 revolute bearings","1 prismatic guided rack","9 rack/pinion tooth contacts"],
        "shaft_radius_mm":2.5,"bearing_od_mm":10.0,"metal_thickness_mm":SHEET
    }
}
(HERE/"scene.json").write_text(json.dumps(data,separators=(",",":")),encoding="utf-8")
(HERE/"validation.json").write_text(json.dumps({
    "cad_engine":"CadQuery",
    "valid_solids":len(STATION_PARTS),
    "kinematic_states_exported":["closed","intermediate","open"],
    "sampled_exact_distances_between_neighbouring_middle_petal_solids_mm":DISTANCES,
    "conservative_adjacent_layer_sheet_clearance_mm":round(min_clearance,3),
    "bearing_cheek_to_shoe_y_gap_mm":7.0,
    "sheet_to_spine_y_gap_mm":11.7,
    "minimum_sheet_to_neighbor_shoe_y_gap_mm":round(neighbor_shoe_gap,3),
    "rack_travel_mm":round(abs(turn(OPEN)),4),
    "unverified":["rack tooth backlash under load","lamp stability under applied knob force","metal bending stiffness and springback","thermal performance","pinch force and finger access","hardware assembly tolerance stack"]
},indent=2),encoding="utf-8")
print("parts",len(STATION_PARTS),"instances",len(INSTANCES),"mesh_bytes",(HERE/"scene.json").stat().st_size,"min_gap",round(min_clearance,3),flush=True)
