import os
import sys
import json
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parent
headers = {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "application/json"}
if sys.argv[1] == "submit":
    spec = (root/"astra_6_2_review.md").read_text(encoding="utf-8")
    src = (root/"build.py").read_text(encoding="utf-8")
    validation = (root/"validation.json").read_text(encoding="utf-8")
    task = "As gpt-6.2-astra acting as a senior mechanical engineer, critically audit this REAL complete CadQuery assembly for production feasibility and its specific reference render: continuous upper elliptical zeppelin-shaped canopy, separate concave lower glowing light dish, two vertical posts with visible 4-bar parallelogram lift and rear torque tube. Never produce fake images. Test correctness of 1-DOF mechanism, cross-end coupling, part-to-part interfaces, STEP validity, load path, unintended contacts, tolerance stack, actual moving clearances, shell assembly, LED thermal/electrical safety, stability, pinch and user interface. Report only evidenced problems and unverified assumptions with precise corrections, in rank order; propose precise minimal repairs where possible. Is a 476 x 165.46 x 200mm envelope acceptable under the chosen 485 x 175 x 300 design limits? Differ between geometric CAD passes and production ready. Build script and validation follow:"
    prompt = task + "\nMECHANISM SPEC\n" + spec + "\nSOURCE\n" + src + "\nVALIDATION\n" + validation
    body = {"model":"gpt-6.2-astra","reasoning":{"effort":"xhigh"},"background":True,"max_output_tokens":15000,"input":[{"role":"user","content":[{"type":"input_text","text":prompt}]}]}
    req = urllib.request.Request("https://api.openai.com/v1/responses",data=json.dumps(body).encode(),headers=headers,method="POST")
    with urllib.request.urlopen(req,timeout=60) as res:
        result=json.load(res)
    (root/"qa_response_id.txt").write_text(result["id"],encoding="utf-8")
else:
    ref=(root/"qa_response_id.txt").read_text(encoding="utf-8").strip()
    req=urllib.request.Request("https://api.openai.com/v1/responses/"+ref,headers=headers)
    with urllib.request.urlopen(req,timeout=60) as res:
        result=json.load(res)
out="\n".join(p.get("text","") for x in result.get("output",[]) for p in x.get("content",[]) if p.get("type")=="output_text")
if out:
    (root/"astra_qa_review.md").write_text(out,encoding="utf-8")
summary={"id":result.get("id"),"model":result.get("model"),"status":result.get("status"),"length":len(out),"usage":result.get("usage")}
(root/"qa_run.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
print(json.dumps(summary,ensure_ascii=True),flush=True)
