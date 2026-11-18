import os, json, urllib.request
from pathlib import Path
folder = Path(__file__).resolve().parent
ref = (folder/"astra_response_id.txt").read_text(encoding="utf-8").strip()
req = urllib.request.Request("https://api.openai.com/v1/responses/"+ref,headers={"Authorization":"Bearer "+os.environ["OPENAI_API_KEY"]})
with urllib.request.urlopen(req,timeout=45) as r:
    result=json.load(r)
text="\n".join(p.get("text","") for o in result.get("output",[]) for p in o.get("content",[]) if p.get("type")=="output_text")
print("status="+result.get("status","")+" chars="+str(len(text))+" usage="+json.dumps(result.get("usage",{})),flush=True)
if text:
    (folder/"astra_6_2_review.md").write_text(text,encoding="utf-8")
    print(text[:14000],flush=True)
