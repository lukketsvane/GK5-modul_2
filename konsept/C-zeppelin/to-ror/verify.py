import math,json
from pathlib import Path
import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

root=Path(__file__).resolve().parent
scene=json.loads((root/"scene.json").read_text(encoding="utf-8"))
shells=[p for p in scene["parts"] if p["name"].startswith("shell_")]
assert len(shells)==12, len(shells)
assert len({p["name"].split("_")[1] for p in shells})==6
for shell_id in map(str,range(1,7)):
    assert {p["name"].split("_")[2] for p in shells if p["name"].split("_")[1]==shell_id}=={"upper","lower"}
print("SHELL_COUNT_CONFIRMED=6",flush=True)

files=root/"delar"
A=cq.importers.importStep(str(files/"shutter_upper.step")).val()
B=cq.importers.importStep(str(files/"shutter_lower.step")).val()
gA=cq.importers.importStep(str(files/"gear_upper.step")).val()
gB=cq.importers.importStep(str(files/"gear_lower.step")).val()

def pos(shape,which,deg,x=0):
    y=-10 if which=="upper" else 10
    turn=-deg if which=="upper" else deg
    return shape.moved(cq.Location(cq.Vector(x,y,136),cq.Vector(1,0,0),turn))
def dist(a,b):
    r=BRepExtrema_DistShapeShape(a.wrapped,b.wrapped)
    r.Perform()
    return float(r.Value()) if r.IsDone() else -1

test=[]
for deg in (0,8,16,24,32):
    a,b=pos(A,"upper",deg),pos(B,"lower",deg)
    ca,cb=pos(gA,"upper",deg,199),pos(gB,"lower",deg,199)
    gap=20-18.2*math.cos(math.radians(deg))+42*math.sin(math.radians(deg))
    line={"angle_deg":deg,"shutter_aperture_mm":round(gap,3),
          "shutter_min_clearance_mm":round(dist(a,b),4),
          "gear_intersection_mm3":round(ca.intersect(cb).Volume(),5),
          "gear_surface_gap_mm":round(dist(ca,cb),4)}
    test.append(line)
    print(line,flush=True)

assert test[0]["shutter_aperture_mm"]<2.1
assert test[-1]["shutter_aperture_mm"]>25
assert all(row["shutter_min_clearance_mm"]>=.5 for row in test)
report={"status":"GEOMETRIC TWO-AXIS PROOF OF CONCEPT; NOT PHYSICAL VALIDATION",
        "tube_axes":[[0,-10,136],[0,10,136]],
        "two_tubes_counterrotating":True,
        "station_count":9,
        "petal_count":18,
        "aperture_width_under_LED_mm":test,
        "led_face_width_mm":13,
        "remaining_checks":["actual involute tooth contact, backlash and loaded torque",
          "clamp-to-tube torque transfer and anti-slip fasteners",
          "all moving bracket-to-petal collision pairs and fatigue",
          "temperature, glare, ballast and electrical safety"]}
(root/"verification.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("VERIFICATION_PASSED_2_AXIS_APERTURE",flush=True)
