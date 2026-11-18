import os,json,pathlib,urllib.request
p=pathlib.Path(__file__).resolve().parent
src=(p/"build.py").read_text(encoding="utf-8")
note="""The user DEMANDS actual CAD/Blender geometry look effectively identical to the source photo of this silver Zeppelin lamp against pure black. SIDE ELEVATION IMAGE SIZE 1536x864: shell spans pixel x150..1380 and y185..514; a black horizontal cylindrical spindle crosses the exact middle at image y398 with 9 circular silver pivot heads. The upper silhouette is formed from overlapping large rounded asymmetric HALF-ELLIPTICAL leaves, convex scalloped on top, gradually tapering toward both nose cones. The lower silhouette has correspondingly wide curved reflective scoops, warm ivory underside glow beneath central spindle. Each upper lobe rises from spindle, its broad face is visible in the XZ profile, smoothly bowed and not hourglass. Upper scales meet rail at z0 and lower start below, leaving the rod and evenly spaced pivot heads visible.
Existing build.py creates 9 stations x=i*40.84mm and y-offset depth layers, with some moving blades, central rail z116, 0.6mm thick material, 5mm shafts, hub, rack and pinions. Current Blender CAD result is aesthetically incorrect because ALL panels are full hourglass with massive waist notch. Need actual new sheet geometry, not render trick: every blade should have smooth separate upper and lower scalloped leaf with a narrow central gap (for black axle to show). At pivot roots structural tab must connect to hub; other sheets overlap by depth lanes 14mm; must avoid other shafts. Construct physically plausible 0.6mm laser-cut sheet, cylindrically bent in y (developable) with 5-8mm tip rise. Keep tool and geometry physically valid in CadQuery 2.8, STEP export and rotating in Blender.
Please output ONLY an executable complete Python patch script that reads existing build.py sibling, rewrites def blade(kind, sign), and if needed adjusts STATION_PARTS/INSTANCES to handle a Compound for two loose half sheets (or join via narrow bridge along z0 behind a spine cover). No comments/docstrings. Keep blade_{kind}_{sign} key if possible, successful positive shape validity, physically plausible torque-transmission via existing shoe. Need avoid a wide central XZ waist with unsightly notches: reference leaves from pivot to top with broad visible surface at z0, upper/lower lobes are independent and connected to same hub.
Use exact current source for replacement:
"""
note+=src[src.index("def blade(kind, sign):"):src.index("def shoe(sign):")]
note+="\nSTATIONS:\n"+src[src.index("STATION_PARTS={}"):src.index("COLORS=",src.index("STATION_PARTS={}"))]
req={"model":"gpt-6.2-astra","reasoning":{"effort":"xhigh"},"max_output_tokens":9300,"input":[{"role":"user","content":[{"type":"input_text","text":note}]}]}
try:
 request=urllib.request.Request("https://api.openai.com/v1/responses",data=json.dumps(req).encode(),headers={"Authorization":"Bearer "+os.environ["OPENAI_API_KEY"],"Content-Type":"application/json"},method="POST")
 with urllib.request.urlopen(request,timeout=240) as response:data=json.load(response)
 output="\n".join(c.get("text","") for row in data.get("output",[]) for c in row.get("content",[]) if c.get("type")=="output_text")
 output=output.strip()
 if output.startswith(chr(96)*3):output=output.split("\n",1)[1].rsplit(chr(96)*3,1)[0]
 (p/"edit_reference_form.py").write_text(output,encoding="utf-8")
 print("MODEL",data.get("model"),"STATUS",data.get("status"),"TOKENS",data.get("usage",{}),"CHARS",len(output),"HEAD",output[:380].encode("ascii","replace").decode(),flush=True)
except Exception as e:print("ERROR",type(e).__name__,str(e)[:800],flush=True)
