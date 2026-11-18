import os
import sys
import json
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parent
headers = {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type":"application/json"}
if sys.argv[1] == "submit":
    guide = (root / "blender_prompt.md").read_text(encoding="utf-8")
    existing = (root.parent / "B-tilta-skive" / "blender_revB.py")
    if not existing.exists():
        existing = root.parent.parent.parent / "GK5-modul_2_E_astra" / "konsept" / "B-tilta-skive" / "blender_revB.py"
    cad = (root/"build.py").read_text(encoding="utf-8")
    comps = json.loads((root/"components.json").read_text(encoding="utf-8"))
    excerpt = {"parts": dict(list(comps["parts"].items())[:3]), "instances": dict(list(comps["instances"].items())[:3]), "poses": {k: {"transforms": dict(list(v["transforms"].items())[:2])} for k,v in comps["poses"].items()}}
    prompt = guide + "\nE CAD BUILD SOURCE\n" + cad + "\nE COMPONENTS SAMPLE\n" + json.dumps(excerpt) + "\nB BLENDER REFERENCE SCRIPT\n" + existing.read_text(encoding="utf-8")
    body = {"model":"gpt-6.2-astra","reasoning":{"effort":"xhigh"},"max_output_tokens":30000,"background":True,"input":[{"role":"user","content":[{"type":"input_text","text":prompt}]}]}
    req = urllib.request.Request("https://api.openai.com/v1/responses", data=json.dumps(body).encode(),headers=headers,method="POST")
    with urllib.request.urlopen(req,timeout=65) as resp:
        result=json.load(resp)
    (root/"blender_response_id.txt").write_text(result["id"],encoding="utf-8")
else:
    id = (root/"blender_response_id.txt").read_text(encoding="utf-8").strip()
    req=urllib.request.Request("https://api.openai.com/v1/responses/"+id,headers=headers)
    with urllib.request.urlopen(req,timeout=65) as resp:
        result=json.load(resp)
txt="\n".join(p.get("text","") for item in result.get("output",[]) for p in item.get("content",[]) if p.get("type")=="output_text")
if txt:
    def section(a,b):
        if a not in txt or b not in txt:
            raise ValueError("Missing source delimiter "+a)
        src=txt.split(a,1)[1].split(b,1)[0].strip()
        return src.removeprefix("```python").removeprefix("```").removesuffix("```").strip()+"\n"
    (root/"export_meshes.py").write_text(section("===EXPORT_MESHES===","===END_EXPORT_MESHES==="),encoding="utf-8")
    (root/"render_blender.py").write_text(section("===RENDER_BLENDER===","===END_RENDER_BLENDER==="),encoding="utf-8")
summary={"id":result.get("id"),"model":result.get("model"),"status":result.get("status"),"chars":len(txt),"usage":result.get("usage")}
(root/"blender_run.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
print(json.dumps(summary,ensure_ascii=True),flush=True)
