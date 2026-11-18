import json
import os
import urllib.request
req = urllib.request.Request("https://api.openai.com/v1/models", headers={"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]})
with urllib.request.urlopen(req, timeout=30) as res:
    models = json.load(res)
print("candidate_models=" + json.dumps([m["id"] for m in models.get("data", []) if "astra" in m["id"].lower() or "6.2" in m["id"]]))
