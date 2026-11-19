import json, math
from pathlib import Path
import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

root=Path(__file__).resolve().parent
data=json.loads((root/"scene.json").read_text(encoding="utf-8"))
shells=sorted([v for v in data["parts"] if v["name"].startswith("shell_")],key=lambda x:int(x["name"].split("_")[1]))
assert len(shells)==6,(len(shells),[s["name"] for s in shells])
assert [s["name"] for s in shells]==[f"shell_{n}" for n in range(1,7)]
assert [s["motion"] for s in shells]==["upper","lower"]*3
shapes=[]
for s in shells:
    step=root/"delar"/(s["g"]+".step")
    if not step.exists():
        raise AssertionError(f"Missing shell STEP {step.name}")
    shape=cq.importers.importStep(str(step)).val()
    bb=shape.BoundingBox()
    assert shape.isValid() and shape.Volume()>1.0 and len(shape.Solids())==1
    assert bb.zmin<-11 and bb.zmax>20,(s["name"],bb.zmin,bb.zmax)
    shapes.append(shape)

def location(shape,item,deg):
    x,y,z=item["p"]
    turn=-deg if item["motion"]=="upper" else deg
    return shape.moved(cq.Location(cq.Vector(x,y,z),cq.Vector(1,0,0),turn))

samples=[]
for deg in (0,8,16,24,32):
    moved=[location(s,item,deg) for s,item in zip(shapes,shells)]
    for i in range(5):
        a,b=moved[i:i+2]
        d=BRepExtrema_DistShapeShape(a.wrapped,b.wrapped)
        d.Perform()
        assert d.IsDone(),(deg,i)
        gap=float(d.Value())
        overlap=float(a.intersect(b).Volume())
        samples.append({"pose":deg,"pair":f"{i+1}-{i+2}","gap_mm":round(gap,3),"overlap_mm3":round(overlap,6)})
        assert overlap<.02 and gap>.2,(deg,i,gap,overlap)
report={"shell_count":6,"one_piece_per_shell":True,"rod_assignment":["upper","lower"]*3,
        "neighbor_shell_samples":samples,"checked_angles":[0,8,16,24,32],
        "limitations":["nonadjacent collision pairs not checked","hardware and shutter interference not checked","no load or light measurements"]}
(root/"verification_six_complete.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("SIX_WHOLE_SHELLS_PASS","min_neighbor_clearance_mm",min(s["gap_mm"] for s in samples),flush=True)
