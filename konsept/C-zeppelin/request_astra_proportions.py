import os,json,pathlib,urllib.request
p=pathlib.Path(__file__).resolve().parent
prompt="""Produce an exact minimal Python patch for build.py to correct the physically rendered CAD proportions. Source image was measured in pixels: silver zeppelin body x151..1377 width1226, y185..514 height329, horizontal black axle y399. Body width:height=3.73. Upper half above axle=214px; lower below=115px; upper:lower=1.86. Round foot diameter=420px =0.343 of hull width; pedestal visible y514..680 166px. Current CAD build.py has HALF_CHORD=[86,82,72,58,32] as symmetric top/bottom. Present Blender render is badly proportioned: body width~384 mm, height~173mm (ratio2.22); foot diameter110mm, ratio.286; pedestal barely visible. Target upper heights +63 mm, lower depths -34mm central, taper to ends, plus foot diameter132mm. Need asymmetric blade profiles and updated floating foot geometry if appropriate. The other Astra call is redesigning blade() at same time, so ideally output concise technical recommendations and exact modular patch script that creates constants UPPER_HEIGHTS=[63,59,52,42,26] and LOWER_DEPTHS=[34,32,27,21,11], changes base radius55 to66, base height8 to13 and pedestal from box46x21x87.5 center51.75 to physical convex profile; preserve z of hinge HEIGHT=116 and other attached geometry; do not change rail height without moving every component. If upper/lower cannot be done without modifying blade(), explain and show simplest required code change. Output a patch file Python code only, no code fences, no docstrings. Preserve functional CadQuery STEP assembly and collision checks.
Relevant named code:
HEIGHT = 116.0
HALF_CHORD = [86,82,72,58,32]
WING_WIDTH = [68,64,57,46,32]
SHEET=0.6
def base():
    return cq.Solid.makeCylinder(55.0,8.0,cq.Vector(0,0,0),cq.Vector(0,0,1))
def pedestal():
    return cq.Workplane("XY").box(46.0,21.0,87.5).edges("|Z").fillet(4.0).translate((0,0,51.75)).val()
"""
body={"model":"gpt-6.2-astra","reasoning":{"effort":"xhigh"},"max_output_tokens":4800,"input":[{"role":"user","content":[{"type":"input_text","text":prompt}]}]}
try:
 req=urllib.request.Request("https://api.openai.com/v1/responses",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+os.environ["OPENAI_API_KEY"],"Content-Type":"application/json"},method="POST")
 with urllib.request.urlopen(req,timeout=230) as r:data=json.load(r)
 output="\n".join(c.get("text","") for row in data.get("output",[]) for c in row.get("content",[]) if c.get("type")=="output_text")
 output=output.strip()
 if output.startswith(chr(96)*3):output=output.split("\n",1)[1].rsplit(chr(96)*3,1)[0]
 (p/"astra_proportions.py").write_text(output,encoding="utf-8")
 print("MODEL",data.get("model"),"STATUS",data.get("status"),"chars",len(output),"usage",data.get("usage",{}),flush=True)
except Exception as e:print("ERROR",type(e).__name__,str(e)[:700],flush=True)
