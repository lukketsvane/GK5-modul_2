import os, json, urllib.request
from pathlib import Path
folder = Path(__file__).resolve().parent
prompt = (folder / "design_prompt.txt").read_text(encoding="utf-8")
body = {"model":"gpt-6.2-astra","reasoning":{"effort":"xhigh"},"max_output_tokens":16000,"background":True,"input":[{"role":"user","content":[{"type":"input_text","text":prompt}]}]}
req = urllib.request.Request("https://api.openai.com/v1/responses",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+os.environ["OPENAI_API_KEY"],"Content-Type":"application/json"},method="POST")
with urllib.request.urlopen(req,timeout=60) as r:
    result=json.load(r)
(folder/"astra_response_id.txt").write_text(result["id"],encoding="utf-8")
print("id="+result["id"]+" status="+result["status"]+" model="+result["model"],flush=True)

