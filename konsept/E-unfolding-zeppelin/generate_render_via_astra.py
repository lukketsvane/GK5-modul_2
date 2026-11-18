import os
import sys
import json
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parent
headers = {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "application/json"}
mode = sys.argv[1]
if mode == "submit":
    prompt = (root / "render_prompt.md").read_text(encoding="utf-8")
    body = {"model": "gpt-6.2-astra", "reasoning": {"effort": "xhigh"}, "background": True, "max_output_tokens": 16000, "input": [{"role": "user", "content": [{"type": "input_text", "text": prompt}]}]}
    req = urllib.request.Request("https://api.openai.com/v1/responses", data=json.dumps(body).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=65) as response:
        result = json.load(response)
    (root / "render_response_id.txt").write_text(result["id"], encoding="utf-8")
elif mode == "poll":
    response_id = (root / "render_response_id.txt").read_text(encoding="utf-8").strip()
    req = urllib.request.Request("https://api.openai.com/v1/responses/" + response_id, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.load(response)
else:
    raise ValueError(mode)
summary = {"model": result.get("model"), "id": result.get("id"), "status": result.get("status"), "usage": result.get("usage")}
(root / "render_run.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
outputs = [part.get("text", "") for item in result.get("output", []) for part in item.get("content", []) if part.get("type") == "output_text"]
source = "\n".join(outputs).strip()
if source:
    if source.startswith("```python"):
        source = source[9:]
    if source.startswith("```"):
        source = source[3:]
    if source.endswith("```"):
        source = source[:-3]
    (root / "render.py").write_text(source.strip() + "\n", encoding="utf-8")
print(json.dumps({"model": summary["model"], "id": summary["id"], "status": summary["status"], "chars": len(source), "usage": summary["usage"]}, ensure_ascii=True), flush=True)

