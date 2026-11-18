import os
import sys
import json
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parent
headers = {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "application/json"}
mode = sys.argv[1]
if mode == "submit":
    prompt = (root / "astra_reference_match_prompt.md").read_text(encoding="utf-8")
    for marker, filename in [("{BUILD_SOURCE}", "build.py"), ("{RENDER_SOURCE}", "render_blender.py"), ("{QA_SOURCE}", "astra_qa_review.md")]:
        prompt = prompt.replace(marker, (root / filename).read_text(encoding="utf-8-sig"))
    body = {"model": "gpt-6.2-astra", "reasoning": {"effort": "xhigh"}, "background": True, "max_output_tokens": 24000, "input": [{"role": "user", "content": [{"type": "input_text", "text": prompt}]}]}
    req = urllib.request.Request("https://api.openai.com/v1/responses", data=json.dumps(body).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=65) as response:
        result = json.load(response)
    (root / "astra_reference_match_response_id.txt").write_text(result["id"], encoding="utf-8")
elif mode == "poll":
    response_id = (root / "astra_reference_match_response_id.txt").read_text(encoding="utf-8").strip()
    req = urllib.request.Request("https://api.openai.com/v1/responses/" + response_id, headers=headers)
    with urllib.request.urlopen(req, timeout=65) as response:
        result = json.load(response)
else:
    raise ValueError(mode)
out = "\n".join(part.get("text", "") for item in result.get("output", []) for part in item.get("content", []) if part.get("type") == "output_text").strip()
if out and result["status"] == "completed":
    out = out.removeprefix("```python").removeprefix("```").removesuffix("```").strip() + "\n"
    (root / "astra_reference_patch.py").write_text(out, encoding="utf-8")
summary = {"id": result.get("id"), "model": result.get("model"), "status": result.get("status"), "chars": len(out), "usage": result.get("usage")}
(root / "astra_reference_match_run.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=True), flush=True)
