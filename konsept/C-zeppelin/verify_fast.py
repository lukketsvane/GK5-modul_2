import math,json
from pathlib import Path
import numpy as np
import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/"scene.json").read_text(encoding="utf-8"))
def sep(a,b):
    d=BRepExtrema_DistShapeShape(a.wrapped,b.wrapped)
    d.Perform()
    return round(float(d.Value()),4)
def shape(key): return cq.importers.importStep(str(ROOT/"delar"/(key+".step"))).val()
def move(shape,x=0,y=0,theta=0):
    return shape.moved(cq.Location(cq.Vector(x,y,116),cq.Vector(0,1,0),theta))
bounds={}
meshes={k:np.asarray(v["v"],dtype=float).reshape(-1,3) for k,v in DATA["models"].items()}
for angle in range(10,39,2):
    mins=np.array([1e6,1e6,1e6])
    maxs=-mins.copy()
    for obj in DATA["parts"]:
        v=meshes[obj["g"]]
        x,y,z=obj["p"]
        motion=obj["motion"]
        if motion=="leaf": ang=angle
        elif motion=="gear": ang=angle-38
        else:ang=0
        if motion=="rack":x+=10*math.radians(angle-38)
        if ang:
            c=math.cos(math.radians(ang))
            s=math.sin(math.radians(ang))
            xx=v[:,0]*c+v[:,2]*s+x
            zz=-v[:,0]*s+v[:,2]*c+z
        else:
            xx=v[:,0]+x
            zz=v[:,2]+z
        yy=v[:,1]+y
        mins=np.minimum(mins,[xx.min(),yy.min(),zz.min()])
        maxs=np.maximum(maxs,[xx.max(),yy.max(),zz.max()])
    dim=maxs-mins
    bounds[str(angle)]=[round(float(k),2) for k in dim]
    if dim[0]>400.6 or dim[1]>160 or dim[2]>300:
        raise AssertionError(f"Envelope outside target at {angle}: {dim}")
tests={}
for theta in (10,24,38):
    gear=move(shape("gear"),0,0,theta-38)
    rack=shape("rack").moved(cq.Location(cq.Vector(10*math.radians(theta-38),0,0)))
    dg=sep(gear,rack)
    tests[f"gear_rack_{theta}"]=dg
    if gear.intersect(rack).Volume()>0.02:
        raise AssertionError(f"gear intersects rack at {theta}")
    centre=move(shape("blade_0_1"),0,0,theta)
    own=move(shape("shaft_lane_0"),0,0,theta)
    adjacent=move(shape("shaft_lane_1"),13*math.pi,0,theta)
    same_layer=move(shape("blade_4_1"),4*13*math.pi,0,theta)
    for test,sol in (("own_bore",own),("adjacent_shaft",adjacent),("same_layer",same_layer)):
        v=sep(centre,sol)
        tests[f"{test}_{theta}"]=v
        if test=="own_bore" and v <.15: raise AssertionError("own shaft clashes with sheet hole")
        if test!="own_bore" and v <1.5: raise AssertionError(f"unexpected collision {test} at {theta}: {v}")
tests["min_analytic_sheet_other_depth_gap_mm"]=round(14-6.5-.6,3)
tests["min_analytic_neighbor_shaft_side_gap_mm"]=round((13*math.pi)*math.cos(math.radians(38))-23-2.5,3)
tests["minimum_gear_rack_distance_mm"]=min(tests[f"gear_rack_{t}"] for t in (10,24,38))
tests["maximum_gear_rack_distance_mm"]=max(tests[f"gear_rack_{t}"] for t in (10,24,38))
result={"passed":True,"poses":3,"unique_CAD_solids":len(DATA["models"]),"assembly_parts":len(DATA["parts"]),"swept_envelope_2deg_steps_mm":bounds,"measured_solid_distances_mm":tests,"caveats":["Physical stiffness, fatigue, thermal design, actual gear backlash and anti-tip performance require a bench prototype","Only three exact tooth-mesh samples, plus analytical clearance bounds, not a certified 0.1-degree industrial collision sweep"]}
(ROOT/"verification_final.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps({"passed":True,"samples":len(bounds),"envelope_max_mm":[max(v[i] for v in bounds.values()) for i in range(3)],"tests":tests},indent=2),flush=True)
