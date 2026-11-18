import os
import sys
import json
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parent
headers = {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "application/json"}
mode = sys.argv[1]
if mode == "submit":
    prompt = (root / "astra_v2_prompt.md").read_text(encoding="utf-8")
    for token, fn in [("{BUILD}", "build.py"), ("{RENDER}", "render_blender.py"), ("{VALIDATION}", "validation.json")]:
        prompt = prompt.replace(token, (root / fn).read_text(encoding="utf-8-sig"))
    body = {"model": "gpt-6.2-astra", "reasoning": {"effort": "xhigh"}, "background": True, "max_output_tokens": 26000, "input": [{"role": "user", "content": [{"type": "input_text", "text": prompt}]}]}
    req = urllib.request.Request("https://api.openai.com/v1/responses", data=json.dumps(body).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=65) as resp:
        response = json.load(resp)
    (root / "astra_v2_response_id.txt").write_text(response["id"], encoding="utf-8")
else:
    rid = (root / "astra_v2_response_id.txt").read_text(encoding="utf-8").strip()
    req = urllib.request.Request("https://api.openai.com/v1/responses/" + rid, headers=headers)
    with urllib.request.urlopen(req, timeout=65) as resp:
        response = json.load(resp)
out = "\n".join(x.get("text","") for item in response.get("output",[]) for x in item.get("content",[]) if x.get("type")=="output_text").strip()
if out and response["status"] == "completed":
    out = out.removeprefix("```python").removeprefix("```").removesuffix("```").strip()+"\n"
    (root / "astra_v2_patch.py").write_text(out, encoding="utf-8")
result = {"id":response.get("id"),"model":response.get("model"),"status":response.get("status"),"chars":len(out),"usage":response.get("usage")}
(root / "astra_v2_run.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result), flush=True)
