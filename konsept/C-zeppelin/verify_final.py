import json, math
from pathlib import Path
import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

root=Path(__file__).resolve().parent
p=root/"delar"
shapes={}
for n in ("blade_0_1","blade_1_1","shoe_1","shaft_lane_1"):
    shapes[n]=cq.importers.importStep(str(p/(n+".step"))).val()

P=13*math.pi
def located(name,x,theta,y=0):
    return shapes[name].moved(cq.Location(cq.Vector(x,y,116),cq.Vector(0,1,0),theta))

def separation(a,b):
    test=BRepExtrema_DistShapeShape(a.wrapped,b.wrapped)
    test.Perform()
    if not test.IsDone():
        raise RuntimeError("OCP distance not computed")
    return float(test.Value())

samples=[]
for theta in (10,24,38):
    centre=located("blade_0_1",0,theta)
    adjacent=located("blade_1_1",P,theta,14)
    hub=located("shoe_1",P,theta,14)
    neighbouring_axle=located("shaft_lane_1",P,theta)
    row={"angle":theta,
         "blade_blade_mm":round(separation(centre,adjacent),4),
         "blade_neighbour_hub_mm":round(separation(centre,hub),4),
         "blade_neighbour_shaft_mm":round(separation(centre,neighbouring_axle),4)}
    print(row,flush=True)
    samples.append(row)

continuous=[]
for k in range(281):
    deg=10+k/10
    minimum_x=P*math.cos(math.radians(deg))
    axle_gap=minimum_x-23.0-2.5
    continuous.append(axle_gap)
assert len(continuous)==281
assert min(continuous)>6.5
assert all(x["blade_blade_mm"]>6.0 for x in samples)
assert all(x["blade_neighbour_hub_mm"]>=1.6 for x in samples)
assert all(x["blade_neighbour_shaft_mm"]>4.0 for x in samples)
assert all((root/"samansetjingar"/(n+".step")).stat().st_size>1000000 for n in ("lukka","mellom","open"))
report={"status":"PASS FOR CHECKED RISK PAIRS, NOT FULL SAFETY CERTIFICATION",
        "cad_tool":"CadQuery 2.8 / OCP",
        "poses":samples,
        "numeric_grid_degrees":[10,38,0.1],
        "minimum_analytic_adjacent_shaft_gap_mm":round(min(continuous),4),
        "rack_travel_mm":round(10*math.radians(28),4),
        "gear": "20-tooth module-1, nominal rack pitch 13*pi, 20-degree pressure angle; actual sustained load/backlash unverified",
        "unverified":["all hardware contact pairs under worst-case manufacturing deviations","drive torque and clamp slip","lamp tipping under hand load","electrical design and thermal performance","sheet elastic stiffness","user pinch safety"]}
(root/"verification_motion.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("VALIDATION_PASS",flush=True)
